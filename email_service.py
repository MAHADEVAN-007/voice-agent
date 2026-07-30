import os, logging
import asyncio

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

try:
    import resend
    resend.api_key = os.environ.get("RESEND_API_KEY", "")
    _resend_available = bool(resend.api_key)
except:
    _resend_available = False
    logger.warning("Resend NOT Configured - Email Notifications DISABLED")


async def send_admin_notification(phone_number: str, request_id: str, base_url: str) -> bool:
    if not _resend_available:
        logger.info(f"[email] skipped (no Resend key): {phone_number} -> request {request_id}")
        return False

    admin_email = os.environ.get("ADMIN_EMAIL", "")
    if not admin_email:
        logger.warning("ADMIN Email not set - skipping email")
        return False

    admin_panel_url = f"{base_url}/admin?request_id={request_id}"

    html_content = f"""
    <h2>New Access Request</h2>
    <p><strong>Phone Number:</strong> {phone_number}</p>
    <p><strong>Request ID:</strong> {request_id}</p>
    <hr>
    <p>Approve or Reject via the admin panel:</p>
    <p><a href="{admin_panel_url}">Open Admin Panel</a></p>
    """

    try:
        params = {
            "from": os.environ.get("RESEND_FROM_EMAIL", "VocalKart <onboarding@resend.dev>"),
            "to": [admin_email],
            "subject": f"VocalKart: Access Request Form {phone_number}",
            "html": html_content,
        }
        await asyncio.to_thread(lambda: resend.Emails.send(params))
        logger.info(f"Email sent to {admin_email} for request {request_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False

