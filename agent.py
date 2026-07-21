import os

# Workaround: On Windows, the default aiohttp DNS resolver (via aiodns/c-ares)
# fails with "Could not contact DNS servers". Force ThreadedResolver instead.
# This must run before any other imports that pull in aiohttp.
import aiohttp
import aiohttp.connector
import aiohttp.resolver as _r
if not hasattr(_r, '_patched'):
    _orig_init = aiohttp.connector.TCPConnector.__init__
    def _patched_init(self, **kwargs):
        if 'resolver' not in kwargs:
            kwargs['resolver'] = _r.ThreadedResolver()
        _orig_init(self, **kwargs)
    aiohttp.connector.TCPConnector.__init__ = _patched_init
    _r._patched = True

import logging
import time
import json, re

from dotenv import load_dotenv
from livekit import agents
from livekit.plugins import sarvam, silero
from livekit.agents import Agent, AgentServer, AgentSession, JobContext, room_io
from livekit.plugins import noise_cancellation, sarvam, silero
from livekit.agents import AgentStateChangedEvent, MetricsCollectedEvent, metrics, SessionUsageUpdatedEvent
from livekit.agents import function_tool, RunContext
from livekit.agents import inference

from database import session_scope, init_db
from crud import search_products, deduct_stock, create_product
from init_db import KIRANA_PRODUCTS

from sqlalchemy import text

from prompt import SYSTEM_PROMPT

load_dotenv()

logger = logging.getLogger(__name__)

try:
    from whatsapp import send_order_summary_via_twilio
except ImportError:
    send_order_summary_via_twilio = None
    logger.warning("whatsapp.py is not availabe - WhatsApp features disabled")


# Define your agent's behavior by extending the Agent class
class Assistant(Agent):
    def __init__(self, phone_number: str = " ") -> None:
        super().__init__(
            instructions=SYSTEM_PROMPT,
        )
        self.phone_number = phone_number

    @function_tool
    async def catalog_lookup(self, context: RunContext, query: str) -> str:
        """Search products in the store catalog. Returns JSON array.

Returns:
  [] — product not found (use Out-of-Stock fallback)
  [single item] — exact match found
  [multiple items] — ambiguous, ask ONE clarification

Each item: {"product": str, "mrp": float, "price_per_case": float, "schemes": list[str] | null}

Args:
    query: The product name to search for
"""
        try:
            async with session_scope() as db:
                items = await search_products(db, query)
                if not items:
                    return "[]"
                result = []
                for item in items:
                    schemes_list = item.schemes.split("; ") if item.schemes else None
                    product_name = re.sub(r'\b(\d+)g\b', r'\1 gram', item.product)
                    product_name = re.sub(r'\b(\d+)ml\b', r'\1 milliliter', product_name)
                    result.append({
                        "product": product_name,
                        "quantity": item.quantity,
                        "mrp": float(item.mrp),
                        "price_per_case": float(item.price_per_case),
                        "schemes": schemes_list,
                })
            return json.dumps(result, ensure_ascii=False)
        except Exception:
            logger.exception("catalog_lookup failed")
            return "[]"
        
    
        
    @function_tool
    async def send_order_summary_message(self, context: RunContext, customer_name: str, items_json: str, total_amount: int, phone_number: str = "") -> str:

        """
        *** IMPORTANT: You MUST call this tool after customer confirms the order. ***
        Do NOT tell the customer "WhatsApp bhej diya" until this tool returns success.
        Only call this when customer has confirmed their order.

        Args:
            customer_name: Customer's full name as collected during the conversation
            items_json: JSON array of ordered items. 
                Each item: {"product": str, "qty": int, "amount": float}
            total_amount: Total order amount as number
        """

        number = phone_number or self.phone_number
        if not number:
            return "Phone Number not available. Ask the customer for their WhatsApp Number and try again."

        try:
            items = json.loads(items_json)
        except json.JSONDecodeError:
            return f"Invalid items_json format. Please provide valid JSON"
        
        whatsapp_result = "WhatsApp sending failed"
        stock_result = "Stock deduction skipped"
        
        try:
            # Sending WhatsApp Message ->
            whatsapp_result = send_order_summary_via_twilio(
                to_phone=number,
                customer_name=customer_name,
                items=items,
                total_amount=total_amount
            )
        except Exception as e :
            logger.exception("send_order_summary_message failed")
            return f"Failed to send WhatsApp message. Error: {str(e)}"
        

        try:
            async with session_scope() as db:
                stock_result = await deduct_stock(db, items)
        except Exception as e:
            logger.exception("stock deduction failed")
            stock_result = {"success": False, "message": f"System Error: {str(e)}"}

        if "Failed" in whatsapp_result and not stock_result["success"]:
            return f"Both Failed. WhatsApp: {whatsapp_result}. Stock: {stock_result['message']}"
        
        if "Failed" in whatsapp_result:
            return f"WhatsApp: {whatsapp_result}, but Stock Deducted: {stock_result['message']}"
        
        if not stock_result['success']:
            return f"WhatsApp: {whatsapp_result}, but Stock Deduction Failed: {stock_result['message']}"
        
        return f"Both Successful. WhatsApp: {whatsapp_result}, and Stock: {stock_result['success']}"
        
  
server = AgentServer()

# The entrypoint function runs when a participant joins the room
@server.rtc_session(agent_name="agent")
async def entrypoint(ctx: JobContext):
    try:
        await init_db()
        async with session_scope() as db:
            existing = await db.execute(text("SELECT COUNT(*) FROM inventory"))
            result = existing.scalar()
            if result == 0:
                for product, qty, mrp, ppc, schemes in KIRANA_PRODUCTS:
                    await create_product(db, product, qty, mrp, ppc, schemes)
    except Exception:
        logger.exception("DB init failed — continuing without database")


    # Configure the voice `pipeline with STT, LLM, TTS, and VAD providers
    session = AgentSession(
        stt=sarvam.STT(
            language="hi-IN",
            model='saaras:v3',
            mode='transcribe',
            sample_rate=16000,
            high_vad_sensitivity=True,
            flush_signal=True,
        ),
        llm=inference.LLM(
            model="openai/gpt-4.1-nano",
            extra_kwargs={
                "prompt_cache_key": "voice-agent-v1",
                "service_tier": "priority"
            }
        ),
        tts=sarvam.TTS( 
            target_language_code='hi-IN',
            model='bulbul:v3',
            speaker='shubh',
            speech_sample_rate=22050,
            pace=1.25,
            output_audio_bitrate="128k",
            output_audio_codec='mp3',
            min_buffer_size=30,
            max_chunk_length=150,
            enable_preprocessing=True,
            send_completion_event=True,
            temperature=0.1,
        ),
        vad=silero.VAD.load(),
        turn_handling=agents.TurnHandlingOptions(
            # turn_detection=inference.TurnDetector(),
            turn_detection="stt",
            preemptive_generation={
                "enabled": True,
            },
        ),
    )

    # usage_collector = metrics.UsageCollector()
    # last_eou_metrics:  metrics.EOUMetrics | None = None

    # @session.on("metrics_collected")
    # def _on_metrics_collected(ev: MetricsCollectedEvent):
    #     nonlocal last_eou_metrics
    #     # Capture EOU metrics for TTFA calculation
    #     if ev.metrics.type == "eou_metrics":
    #         last_eou_metrics = ev.metrics

    #     # Log each metric as it arrives and add to usage collector
    #     metrics.log_metrics(ev.metrics)
    #     usage_collector.collect(ev.metrics)

    _usage = []

    @session.on("session_usage_updated")
    def _on_usage_updated(ev: SessionUsageUpdatedEvent):
        nonlocal _usage
        _usage = ev.usage.model_usage

    # async def log_usage():
    #     # Print per-session summary (tokens, audio duration, costs)
    #     summary = usage_collector.get_summary()
    #     logger.info("Usage summary: %s", summary)

    async def log_usage():
        for mu in _usage:
            logger.info("Usage: %s", mu)

    # Fire log_usage when worker shuts down
    ctx.add_shutdown_callback(log_usage)

    @session.on("agent_state_changed")
    def _on_agent_state_changed(ev: AgentStateChangedEvent):
        pass
        # if ev.new_state == "speaking":
        #     if last_eou_metrics:
        #     # Calculate time since user finished speaking
        #         elapsed = time.time() - last_eou_metrics.timestamp
        #         logger.info(f"Time to first audio: {elapsed:.3f}s")


    ## Try distpatch metadata first ()
    phone_number = ""
    try:
        if ctx.job.metadata:
            job_meta = json.loads(ctx.job.metadata)
            phone_number = job_meta.get("phone_number", "")
    except (AttributeError, json.JSONDecodeError):
        pass
    
    # Fallback: room metadata
    if not phone_number:
        room_meta = json.loads(ctx.room.metadata or "{}")
        phone_number = room_meta.get("phone_number", "")
    
    # Fallback: extract caller number from SIP participant identity
    if not phone_number:
        for p in ctx.room.remote_participants.values():
            match = re.search(r'\+?\d{7,15}', p.identity or "")
            if match:
                phone_number = match.group()
                break


    room_name = ctx.room.name
    try:
        await session.start(
            agent=Assistant(phone_number=phone_number),
            room=ctx.room,
            record=True,
            room_options=room_io.RoomOptions(
                audio_input=room_io.AudioInputOptions(),
                audio_output=room_io.AudioOutputOptions(),
            )
        )
    except Exception:
        logger.exception("Agent session failed - see traceback above")
        raise
    # finally:
    #     await log_usage()



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    agents.cli.run_app(server)



