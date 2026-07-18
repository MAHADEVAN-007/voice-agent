import os
import logging
from twilio.rest import Client

logger = logging.getLogger(__name__)

def format_order_message(customer_name: str, items: list[dict], total_amount: str) -> str:
    lines = [
        "*ORDER SUMMARY*",
        "  Company Inventory Store  ",
        "",
        f"*Customer Name:* {customer_name}",
        "",
        "*Items Ordered:*",
    ]
    for item in items:
        product = item["product"]
        qty = item['qty']
        amount = f"₹{int(item['amount']):,}"
        lines.append(f"• {product}  × {qty}  cases  — {amount}")
    lines.extend([
        "───────────────────",
        "",
        f"*Total: ₹{int(float(total_amount)):,}*",
        "",
        "━━━━━━━━━━━━━━━━━━━",
        "Thank you for your order!",
    ])
    return "\n".join(lines)

def send_order_summary_via_twilio(to_phone: str, customer_name: str, items: list[dict], total_amount: str) -> str :
    try:
        account_sid = os.environ['TWILIO_ACCOUNT_SID']
        auth_token = os.environ['TWILIO_AUTH_TOKEN']
        client = Client(account_sid, auth_token)

        message_body = format_order_message(customer_name, items, total_amount)

        message = client.messages.create(
            from_=os.environ['TWILIO_WHATSAPP_FROM'],
            to=f"whatsapp:{to_phone}",
            body=message_body
        )
        logger.info(f"WhatsApp Message sent to {to_phone}: SID {message.sid}")
        return f"Order Summary sent to {customer_name} on WhatsApp at {to_phone}."
    except Exception as e:
        logger.error(f"Failed to send WhatsApp message.")
        return f"Failed to send WhatsApp message. Error: {str(e)}"
    


