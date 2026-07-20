import os, json, uuid, uvicorn, logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from pydantic import BaseModel

from livekit.api import AccessToken, VideoGrants, LiveKitAPI, CreateAgentDispatchRequest, CreateSIPParticipantRequest, DeleteRoomRequest

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

class CreateSessionBody(BaseModel):
    phone_number: str

@app.post("/api/create-session")
async def create_session(body: CreateSessionBody):
    if not body.phone_number:
        raise HTTPException(status_code=400, detail="Phone number is required")

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

    token = AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)\
        .with_identity(f"web-user-{uuid.uuid4().hex[:8]}")\
        .with_grants(VideoGrants(
            room_join=True,
            room=room_name,
            can_publish=True,
            can_subscribe=True,
        )).to_jwt()

    return {
        "token": token,
        "room_name": room_name,
        "ws_url": LIVEKIT_URL,
    }


@app.get("/api/health")
async def health():
    return {"status": "OK"}


FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "frontend", 'dist')
if os.path.isdir(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name='frontend')


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)






