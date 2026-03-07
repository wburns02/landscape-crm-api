import asyncio
import logging
import os

import httpx

logger = logging.getLogger(__name__)

RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")
RESEND_FROM = os.environ.get("RESEND_FROM_EMAIL", "Maas Verde <noreply@maasverde.ecbtx.com>")
UNSUBSCRIBE_URL = os.environ.get("UNSUBSCRIBE_BASE_URL", "https://maasverde.ecbtx.com/unsubscribe")

# Rate limiter: max 10 emails/second
_send_semaphore = asyncio.Semaphore(10)


def _add_unsubscribe_link(html: str, prospect_id: str) -> str:
    link = f'{UNSUBSCRIBE_URL}?id={prospect_id}'
    footer = (
        f'<div style="text-align:center;margin-top:40px;padding:20px;border-top:1px solid #e5e7eb;'
        f'font-size:12px;color:#9ca3af;">'
        f'<p>You received this email because you are a homeowner in the Austin, TX metro area.</p>'
        f'<p><a href="{link}" style="color:#6b7280;">Unsubscribe</a></p>'
        f'</div>'
    )
    if '</body>' in html:
        return html.replace('</body>', f'{footer}</body>')
    return html + footer


async def send_email(
    to: str,
    subject: str,
    html: str,
    text: str | None = None,
    prospect_id: str | None = None,
) -> dict:
    if not RESEND_API_KEY:
        logger.warning("RESEND_API_KEY not set — email not sent")
        return {"id": None, "error": "RESEND_API_KEY not configured"}

    if prospect_id:
        html = _add_unsubscribe_link(html, prospect_id)

    payload = {
        "from": RESEND_FROM,
        "to": [to],
        "subject": subject,
        "html": html,
    }
    if text:
        payload["text"] = text

    async with _send_semaphore:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://api.resend.com/emails",
                json=payload,
                headers={"Authorization": f"Bearer {RESEND_API_KEY}"},
                timeout=10.0,
            )
            if resp.status_code in (200, 201):
                data = resp.json()
                return {"id": data.get("id"), "error": None}
            else:
                logger.error("Resend API error: %s %s", resp.status_code, resp.text)
                return {"id": None, "error": f"Resend API error: {resp.status_code}"}


def render_template(html: str, variables: dict) -> str:
    result = html
    for key, value in variables.items():
        result = result.replace("{{" + key + "}}", str(value or ""))
    return result
