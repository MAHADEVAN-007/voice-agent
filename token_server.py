import os, json, uuid, uvicorn, logging, random, string, time, asyncio
from datetime import datetime, timedelta, timezone

from fastapi import FastAPI, HTTPException, Request, status, Header, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from pydantic import BaseModel

from contextlib import asynccontextmanager

from livekit.api import LiveKitAPI, CreateAgentDispatchRequest, CreateSIPParticipantRequest, DeleteRoomRequest

from database import init_db, session_scope

from crud import (
    get_access_request,
    get_latest_request_by_phone,
    create_access_request,
    set_request_status,
    consume_approved_request,
    list_access_requests,
    access_request_to_dict,
)

from dotenv import load_dotenv
load_dotenv()

from email_service import send_admin_notification
from admin import router as admin_router

try:
    from otp import send_otp_sms
except ImportError:
    send_otp_sms = None

logger = logging.getLogger(__name__)

import aiohttp
from aiohttp.resolver import AsyncResolver



@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await init_db()
    except Exception as e:
        logger.exception(f"init_db failed at startup: {e}")
    yield

app = FastAPI(title="VocalKart", lifespan=lifespan)


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
ADMIN_SECRET = os.environ.get("ADMIN_SECRET", "")


class CreateSessionBody(BaseModel):
    phone_number: str
    turnstile_token: str | None = ""

class SendOTPBody(BaseModel):
    phone_number: str
    turnstile_token: str | None = ""

class VerifyOTPBody(BaseModel):
    phone_number: str
    otp: str

class RequestAccessBody(BaseModel):
    phone_number: str

class AdminRespondBody(BaseModel):
    request_id: str
    action: str
    secret: str = ""


def generate_otp() -> str:
    chars = string.ascii_letters + string.digits + "@#$%&*"
    return "".join(random.choices(chars, k=6))


# OTP ->
otp_store: dict[str, dict] = {}
verified_numbers: set[str] = set()

# Send OTP ->
@app.post("/api/send-otp")
async def send_otp(body: SendOTPBody):

    if not body.phone_number:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Phone number is required")
    
    if not await verify_turnstile(body.turnstile_token):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Verification failed. Please refresh and try again.")

    otp_code = generate_otp()
    otp_store[body.phone_number] = {"otp_code":otp_code, "expires":time.time()+60}

    if not callable(send_otp_sms):
        raise HTTPException(status_code=503, detail="SMS service unavailable")
    sent = await asyncio.to_thread(send_otp_sms, body.phone_number, otp_code)
    if not sent:
        raise HTTPException(status_code=503, detail="Failed to send OTP. Try again.")

    return {"success": True}


# Verify OTP ->
@app.post("/api/verify-otp")
async def verify_otp(body: VerifyOTPBody):
    entry = otp_store.get(body.phone_number)

    # No OTP requested ->
    if not entry:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No OTP requested. Click Send OTP first.")

    # If time exceeds then 1 min, OTP expires ->
    if time.time() > entry["expires"]:
        del otp_store[body.phone_number]
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="OTP Expired. Request a new OTP.")

    # If entered_otp != otp ->
    if entry['otp_code'] != body.otp:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid OTP. Try Again.")


    del otp_store[body.phone_number]
    verified_numbers.add(body.phone_number)
    return {"verified": True}


@app.post("/api/create-session")
async def create_session(body: CreateSessionBody, request: Request):
    if not body.phone_number:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Phone number is required")

    if body.phone_number not in verified_numbers:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Please verify your phone number first with OTP.")

    if not await verify_turnstile(body.turnstile_token):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Verification failed. Please refresh and try again.")

    # ____ Approval Guard ______
    async with session_scope() as db:
        approval_request = await get_latest_request_by_phone(db, body.phone_number)

        if not approval_request:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail = "Access Denied. Please request approval first")

        if approval_request.status != 'approved':
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Approval Pending. Please wait for admin aprroval.')

        consumed = await consume_approved_request(db, approval_request.id)

        if not consumed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Approval already used. Please request a new approval.')


    client_ip = get_client_ip(request)
    if is_rate_limited(body.phone_number, client_ip):
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many requests. Please wait before trying again.")

    verified_numbers.discard(body.phone_number)

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


@app.post("/api/request-access")
async def request_access(body: RequestAccessBody, request: Request):
    if not body.phone_number:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Phone Number Required")

    async with session_scope() as db:
        existing = await get_latest_request_by_phone(db, body.phone_number)
        if existing and existing.status == 'pending':
            request_id = existing.id
        else:
            new_record = await create_access_request(db, body.phone_number)
            request_id = new_record.id

    try:
        public_url = os.environ.get("PUBLIC_URL", "").rstrip("/")
        if public_url:
            base_url = public_url
        else:
            scheme = request.headers.get("X-Forwarded-Proto", request.url.scheme)
            host = request.headers.get("X-Forwarded-Host", request.url.hostname)
            if request.url.port and request.url.port not in (80, 443) and ":" not in host:
                host = f"{host}:{request.url.port}"
            base_url = f"{scheme}://{host}"

        asyncio.create_task(send_admin_notification(body.phone_number, request_id, base_url))
    except Exception as e:
        logger.exception(f"Failed to send admin notification for {body.phone_number}: {e}")

    return {"request_id": request_id, "status": "pending"}


@app.get("/api/request-status/{request_id}")
async def get_request_status(request_id: str):
    async with session_scope() as db:
        record = await get_access_request(db, request_id)

    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Request NOT Found')

    return{
        "status": record.status,
        "request_id": record.id,
        "phone_number": record.phone_number,
        "created_at": record.created_at.isoformat() if record.created_at else None,
        "responded_at": record.responded_at.isoformat() if record.responded_at else None,
    }


@app.get("/api/admin/list-requests")
async def list_requests(secret: str = Header(default="", alias="X-Admin-Secret"), secret_query: str = Query(default="")):

    secret = secret or secret_query

    if not ADMIN_SECRET:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Admin Secret NOT Configured.')

    if secret != ADMIN_SECRET:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Invalid or Expired Request')

    async with session_scope() as db:
        records = await list_access_requests(db)

    return {
        "requests": [access_request_to_dict(r) for r in records]
    }
    

@app.post("/api/admin/respond-request")
async def admin_respond(body: AdminRespondBody):

    if body.secret:
        if not ADMIN_SECRET:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Admin secret not configured")

        if body.secret != ADMIN_SECRET:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Invalid or Expired Request')

    if body.action not in ('approved', 'rejected'):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Action must be 'approved' or 'rejected'.")

    async with session_scope() as db:
        record = await get_access_request(db, body.request_id)

        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Request NOT Found.')

        if record.status != 'pending':
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Request already {record.status}")

        await set_request_status(db, body.request_id, body.action, responded_at=datetime.now(timezone.utc))

    return {
        "status": body.action,
        "request_id": body.request_id,
    }



@app.get("/api/health")
async def health():
    return {"status": "OK"}


app.include_router(admin_router)

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "frontend", 'dist')
if os.path.isdir(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name='frontend')

# Get IP Address of the User ->
def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host


# Rate limiting — in-memory call log (resets on restart)
call_log: dict[str, list[datetime]] = {}

# Rate Limiting Implementation ->
def is_rate_limited(phone: str, ip: str) -> bool:
    now = datetime.utcnow()
    for key in list(call_log.keys()):
        if key.startswith("phone:"):
            call_log[key] = [t for t in call_log[key] if now - t < timedelta(hours=24)]
        elif key.startswith("ip:"):
            call_log[key] = [t for t in call_log[key] if now - t < timedelta(hours=1)]
        if not call_log[key]:
            del call_log[key]

    # Checks phone limit ->
    phone_key = f"phone:{phone}"
    if len(call_log.get(phone_key, [])) >= 2:
        return True # User has hit the max rate limit. Denied to call the agent!!

    # Check IP limit ->
    ip_key = f"ip:{ip}"
    if len(call_log.get(ip_key, [])) >= 5:
        return True # User has hit the max rate limit. Denied to call the agent!!
    
    call_log.setdefault(phone_key, []).append(now)
    call_log.setdefault(ip_key, []).append(now)

    return False # User has not hit the max rate limit. Allowed to call the agent!!

async def verify_turnstile(token: str | None) -> bool:
    if not TURNSTILE_SECRET_KEY or not token:
        return True
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://challenges.cloudflare.com/turnstile/v0/siteverify",
            data={"secret": TURNSTILE_SECRET_KEY, "response": token},
            timeout=aiohttp.ClientTimeout(total=10),
        ) as resp:
            result = await resp.json()
            return result.get("success", False)




if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)







