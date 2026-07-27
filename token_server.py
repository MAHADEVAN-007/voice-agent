import os, json, uuid, uvicorn, logging
from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from pydantic import BaseModel

from livekit.api import LiveKitAPI, CreateAgentDispatchRequest, CreateSIPParticipantRequest, DeleteRoomRequest

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

import aiohttp
from aiohttp.resolver import AsyncResolver

app = FastAPI(title="VocalKart")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

LIVEKIT_URL = os.environ['LIVEKIT_URL']
LIVEKIT_API_KEY = os.environ['LIVEKIT_API_KEY']
LIVEKIT_API_SECRET = os.environ['LIVEKIT_API_SECRET']
LIVEKIT_OUTBOUND_TRUNK_ID = os.environ['LIVEKIT_OUTBOUND_TRUNK_ID']
TURNSTILE_SECRET_KEY = os.environ.get("TURNSTILE_SECRET_KEY")

# Rate limiting — in-memory call log (resets on restart)
call_log: dict[str, list[datetime]] = {}

class CreateSessionBody(BaseModel):
    phone_number: str
    turnstile_token: str


@app.post("/api/create-session")
async def create_session(body: CreateSessionBody, request: Request):
    if not body.phone_number:
        raise HTTPException(status_code=400, detail="Phone number is required")

    if not await verify_turnstile(body.turnstile_token):
        raise HTTPException(status_code=403, detail="Verification failed. Please refresh and try again.")

    client_ip = get_client_ip(request)
    if is_rate_limited(body.phone_number, client_ip):
        raise HTTPException(status_code=429, detail="Too many requests. Please wait before trying again.")

    room_name = f"web-{uuid.uuid4().hex[:12]}"

    resolver = AsyncResolver(nameservers=["1.1.1.1", "8.8.8.8"])
    connector = aiohttp.TCPConnector(resolver=resolver)
    session = aiohttp.ClientSession(connector=connector)

    try:
        async with LiveKitAPI(session=session) as lk:
            await lk.sip.create_sip_participant(
                CreateSIPParticipantRequest(
                    sip_trunk_id=LIVEKIT_OUTBOUND_TRUNK_ID,
                    sip_call_to=body.phone_number,
                    room_name=room_name,
                )
            )

            await lk.agent_dispatch.create_dispatch(
                CreateAgentDispatchRequest(
                    agent_name="agent",
                    metadata=json.dumps({"source": "web", "phone_number": body.phone_number}),
                    room=room_name,
                )
            )
    except Exception:
        try:
            async with LiveKitAPI(session=session) as lk:
                await lk.room.delete_room(DeleteRoomRequest(room=room_name))
        except Exception:
            pass
        raise HTTPException(status_code=503, detail="Service unavailable. Too many active calls — please wait and try again.")
    finally:
        await session.close()

    return {
        "status": "calling",
    }


@app.get("/api/health")
async def health():
    return {"status": "OK"}


FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "frontend", 'dist')
if os.path.isdir(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name='frontend')


def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host

def is_rate_limited(phone: str, ip: str) -> bool:
    now = datetime.utcnow()
    for key in list(call_log.keys()):
        if key.startswith("phone:"):
            call_log[key] = [t for t in call_log[key] if now - t < timedelta(hours=24)]
        elif key.startswith("ip:"):
            call_log[key] = [t for t in call_log[key] if now - t < timedelta(hours=1)]
        if not call_log[key]:
            del call_log[key]
    phone_key = f"phone:{phone}"
    if len(call_log.get(phone_key, [])) >= 2:
        return True
    ip_key = f"ip:{ip}"
    if len(call_log.get(ip_key, [])) >= 5:
        return True
    call_log.setdefault(phone_key, []).append(now)
    call_log.setdefault(ip_key, []).append(now)
    return False

async def verify_turnstile(token: str) -> bool:
    if not TURNSTILE_SECRET_KEY:
        return True
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://challenges.cloudflare.com/turnstile/v0/siteverify",
            data={"secret": TURNSTILE_SECRET_KEY, "response": token},
        ) as resp:
            result = await resp.json()
            return result.get("success", False)



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)







