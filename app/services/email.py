import httpx
from typing import List, Optional
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

RESEND_BASE = "https://api.resend.com"

async def send_resend_email(subject: str, html: str, to: Optional[List[str]] = None, from_email: Optional[str] = None) -> bool:
    """Send an email via Resend API.
    Returns True on success, False on failure.
    """
    api_key = settings.RESEND_API_KEY
    if not api_key:
        logger.warning("RESEND_API_KEY not set; skipping email send")
        return False

    if to is not None:
        recipients = to
    else:
        # settings.NOTIFY_RECIPIENTS may be a comma-separated string
        if isinstance(settings.NOTIFY_RECIPIENTS, str):
            recipients = [s.strip() for s in settings.NOTIFY_RECIPIENTS.split(',') if s.strip()]
        else:
            recipients = list(settings.NOTIFY_RECIPIENTS)
    payload = {
        "from": from_email or settings.EMAIL_FROM,
        "to": recipients,
        "subject": subject,
        "html": html,
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(f"{RESEND_BASE}/emails", json=payload, headers=headers)
            if resp.status_code in (200, 202):
                logger.info("Resend email queued: %s", resp.text)
                return True
            logger.error("Resend send failed [%s]: %s", resp.status_code, resp.text)
            return False
    except Exception as e:
        logger.exception("Resend send exception: %s", e)
        return False


def render_contact_email(name: str, email: str, message: str) -> str:
    return f"""
    <div style='font-family: Arial, sans-serif;'>
      <h2>New Contact Message</h2>
      <p><strong>Name:</strong> {name}</p>
      <p><strong>Email:</strong> {email}</p>
      <p><strong>Message:</strong></p>
      <div style='white-space: pre-wrap; border:1px solid #eee; padding:12px; border-radius:8px;'>
        {message}
      </div>
    </div>
    """
