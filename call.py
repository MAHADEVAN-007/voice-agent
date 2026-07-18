import asyncio, sys, os, time, json

import socket, aiohttp
from aiohttp.resolver import AsyncResolver

from dotenv import load_dotenv
from livekit import api

load_dotenv()

async def call_number(phone_number: str):

    custom_resolver = AsyncResolver(nameservers=["8.8.8.8", "1.1.1.1"])
    connector = aiohttp.TCPConnector(resolver=custom_resolver)
    session = aiohttp.ClientSession(connector=connector)
    lk = api.LiveKitAPI(session=session)

    trunk_id = os.environ.get("LIVEKIT_OUTBOUND_TRUNK_ID")
    if not trunk_id:
        trunk = await lk.sip.create_outbound_trunk(
            api.CreateSIPOutboundTrunkRequest(
                trunk=api.SIPOutboundTrunkInfo(
                    name="vobiz-outbound",
                    address=os.environ["VOBIZ_SIP_DOMAIN"],
                    auth_username=os.environ["VOBIZ_USERNAME"],
                    auth_password=os.environ["VOBIZ_PASSWORD"],
                    numbers=[os.environ["VOBIZ_OUTBOUND_NUMBER"]],
                )
            )
        )
        trunk_id = trunk.sip_trunk_id
        print(f"Created outbound trunk: {trunk_id}")
        print(f"Save in .env: LIVEKIT_OUTBOUND_TRUNK_ID={trunk_id}")
    else:
        print(f"Using existing trunk: {trunk_id}")

    room_name = f"call-{int(time.time())}"
    print(f"Calling {phone_number} in room {room_name}...")

    participant = await lk.sip.create_sip_participant(
        api.CreateSIPParticipantRequest(
            sip_trunk_id=trunk_id,
            sip_call_to=phone_number,
            room_name=room_name,
        )
    )

    print(f"Phone ringing... Participant: {participant.participant_id}")


    dispatch = await lk.agent_dispatch.create_dispatch(
        api.CreateAgentDispatchRequest(
            agent_name="agent",
            metadata=json.dumps({
                "phone_number": phone_number,
            }),
            room=room_name,
        )
    )
    print(f"Agent dispatched! Waiting for call to connect...")

    
    await lk.aclose()
    await session.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: uv run call.py <phone_number>")
        print("Example: uv run call.py +91XXXXXXXXXX")
        sys.exit(1)
    number = sys.argv[1]
    if not number.startswith("+"):
        number = "+91" + number
    asyncio.run(call_number(number))





