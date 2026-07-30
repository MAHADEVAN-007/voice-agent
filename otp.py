import os, logging
from twilio.rest import Client

logger = logging.getLogger(__name__)

def send_otp_sms(phone_number: str, otp_code: str) -> bool:
    try:
        client = Client(os.environ['TWILIO_ACCOUNT_SID'], os.environ['TWILIO_AUTH_TOKEN'])
        client.http_client.timeout = 15  # secondss
        client.messages.create(
            from_=os.environ['TWILIO_MOBILE_NUMBER'],
            to=phone_number,
            body=f"VocalKart OTP : {otp_code}. Valid for 1 minute. Do NOT Share."
        )
        logger.info(f"OTP sent to {phone_number}")
        return True
    except Exception as e:
        logger.error(f"Failed to send OTP to {phone_number}: {e}")
        return False

    

