"""Message building and recipient validation (docs/specs/mail-service.md).

``build_message`` builds a ``multipart/alternative`` (text + HTML)
``EmailMessage`` with the From header set from the settings (REQ-017).
``validate_recipient`` validates the recipient using ``email-validator`` and
raises ``MailTemplateError`` (reason ``"invalid_recipient"``) for an invalid
recipient (REQ-008).
"""

from __future__ import annotations

from email.message import EmailMessage

import email_validator

from backend.mail.errors import MailTemplateError
from backend.mail.render import RenderedTemplate


def build_message(to: str, rendered: RenderedTemplate, from_name: str, from_address: str) -> EmailMessage:
    """Build a ``multipart/alternative`` (text + HTML) ``EmailMessage``."""
    message = EmailMessage()
    message["From"] = f"{from_name} <{from_address}>"
    message["To"] = to
    message["Subject"] = rendered.subject
    message.set_content(rendered.body_text)
    message.add_alternative(rendered.body_html, subtype="html")
    return message


def validate_recipient(to: str) -> None:
    """Validate ``to`` is a valid email address (format-only, no DNS).

    Raises ``MailTemplateError`` (reason ``"invalid_recipient"``) otherwise.
    """
    try:
        email_validator.validate_email(to, check_deliverability=False)
    except email_validator.EmailNotValidError:
        raise MailTemplateError("invalid_recipient") from None
