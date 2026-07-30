import os, json, uuid, uvicorn, logging, random, string, time, asyncio
from datetime import datetime, timedelta, timezone

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from pydantic import BaseModel

from livekit.api import LiveKitAPI, CreateAgentDispatchRequest, CreateSIPParticipantRequest, DeleteRoomRequest

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
ADMIN_SECRET = os.environ.get("ADMIN_SECRET", "vocalKart-admin-secret-2492")


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
    secret: str


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
    request_id = phone_request_index.get(body.phone_number)
    if not request_id or request_id not in access_requests:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access Denied. Please request approval first.")

    if access_requests[request_id]["status"] != "approved":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Approval Pending. Please wait for admin approval")

    del access_requests[request_id]
    del phone_request_index[body.phone_number]


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


access_requests: dict[str, dict] = {}
phone_request_index: dict[str, str] = {}

@app.post("/api/request-access")
async def request_access(body: RequestAccessBody, request: Request):
    if not body.phone_number:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Phone Number Required")

    existing_id = phone_request_index.get(body.phone_number)
    if existing_id and existing_id in access_requests:
        existing = access_requests[existing_id]

        if existing['status'] == "pending":
            return {"request_id": existing_id, "status":"pending"}
        if existing['status'] == "approved":
            return {"request_id": existing_id, "status": "approved"}

        del access_requests[existing_id]
        del phone_request_index[body.phone_number]

    request_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    record = {
        "id": request_id,
        "phone_number": body.phone_number,
        "status": "pending",
        "created_at": now.isoformat(),
        "responded_at": None,
    }

    access_requests[request_id] = record
    phone_request_index[body.phone_number] = request_id

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

        asyncio.create_task(send_admin_notification(body.phone_number, request_id, ADMIN_SECRET, base_url))
    except Exception as e:
        logger.exception(f"Failed to send admin notification for {body.phone_number}: {e}")

    return {"request_id": request_id, "status": "pending"}


@app.get("/api/request-status/{request_id}")
async def get_request_status(request_id: str):
    record = access_requests.get(request_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request NOT Found")
    else:
        return {
            "status": record['status'],
            "request_id": record['id'],
            "created_at": record['created_at'],
            "responded_at": record['responded_at'],
        }


@app.get("/api/admin/list-requests")
async def list_requests(secret: str = ""):
    if secret != ADMIN_SECRET:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid admin secret")
    return {"requests": list(access_requests.values())}

@app.post("/api/admin/respond-request")
async def admin_respond(body: AdminRespondBody):
    if body.secret != ADMIN_SECRET:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid admin secret")
    if body.action not in ("approved", "rejected"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Action must be 'approved' or 'rejected'")

    record = access_requests.get(body.request_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request NOT Found")
    if record['status'] != 'pending':
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Request already {record['status']}")

    record['status'] = body.action
    record['responded_at'] = datetime.now(timezone.utc).isoformat()

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







