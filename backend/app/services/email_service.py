import logging
import re

from app.config import settings

logger = logging.getLogger(__name__)


def _replace_placeholders(template: str, context: dict[str, str]) -> str:
    result = template
    for key, value in context.items():
        result = result.replace(f"[{key}]", value)
    return result


def send_email(to_email: str, subject: str, body_text: str, body_html: str | None = None) -> bool:
    if not settings.SENDGRID_API_KEY:
        logger.info(
            "Email (dev mode) to=%s subject=%s body=%s",
            to_email,
            subject,
            body_text[:200],
        )
        return True

    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail

    message = Mail(
        from_email=settings.FROM_EMAIL,
        to_emails=to_email,
        subject=subject,
        plain_text_content=body_text,
        html_content=body_html or _text_to_html(body_text),
    )
    SendGridAPIClient(settings.SENDGRID_API_KEY).send(message)
    return True


def _text_to_html(text: str) -> str:
    paragraphs = text.strip().split("\n\n")
    html_parts = []
    for p in paragraphs:
        lines = p.replace("\n", "<br>")
        if re.match(r"^https?://", p.strip()):
            html_parts.append(f'<p><a href="{p.strip()}">{p.strip()}</a></p>')
        else:
            html_parts.append(f"<p>{lines}</p>")
    return "".join(html_parts)


def send_order_confirmation(
    to_email: str,
    customer_name: str | None,
    order_id: str,
    campaign_title: str,
    total: str,
    items_summary: str,
) -> bool:
    name = customer_name or "there"
    subject = f"Order confirmed — {campaign_title}"
    body = (
        f"Hi {name},\n\n"
        f"Thank you for your order! We've received your payment.\n\n"
        f"Order #{order_id[:8]}\n"
        f"Campaign: {campaign_title}\n\n"
        f"{items_summary}\n\n"
        f"Total: ${total}\n\n"
        f"We'll notify you when your order ships.\n"
    )
    return send_email(to_email, subject, body)


def send_abandoned_checkout_email(
    to_email: str,
    store_name: str,
    campaign_title: str,
    recovery_url: str,
    subject_template: str | None,
    body_template: str | None,
    cart_summary: str,
) -> bool:
    subject = subject_template or "You left something in your cart!"
    body = body_template or (
        "Hi there,\n\n"
        "You started checkout but didn't finish your order. "
        "Your items are still waiting — complete your purchase before they're gone!\n\n"
        "[Checkout Link]\n"
    )

    context = {
        "Checkout Link": recovery_url,
        "Store Name": store_name,
        "Campaign Title": campaign_title,
        "Cart Summary": cart_summary,
        "Customer Email": to_email,
    }
    subject = _replace_placeholders(subject, context)
    body = _replace_placeholders(body, context)

    if "[Checkout Link]" in body:
        body = body.replace("[Checkout Link]", recovery_url)

    return send_email(to_email, subject, body)
