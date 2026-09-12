"""Email templates (docs/specs/mail-service.md, D2).

``EmailTemplate`` is a frozen Pydantic model: the "clear structure" of an email
template. ``subject``, ``body_html``, and ``body_text`` all support
``{{variable}}`` placeholders. The message is always ``multipart/alternative``
(text + HTML), so both ``body_html`` and ``body_text`` are required.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class EmailTemplate(BaseModel):
    """A named email template with ``{{variable}}`` placeholders."""

    model_config = ConfigDict(frozen=True)

    name: str = Field(min_length=1)
    subject: str
    body_html: str
    body_text: str


PASSWORD_RESET_TEMPLATE: EmailTemplate = EmailTemplate(
    name="password_reset",
    subject="Reset your password",
    body_html=(
        "<p>Hello {{display_name}},</p>"
        "<p>Click the link below to reset your password:</p>"
        '<p><a href="{{reset_url}}">Reset password</a></p>'
        "<p>If you did not request this, you can ignore this email.</p>"
    ),
    body_text=(
        "Hello {{display_name}},\n\n"
        "Reset your password by visiting the link below:\n"
        "{{reset_url}}\n\n"
        "If you did not request this, you can ignore this email.\n"
    ),
)

EMAIL_VERIFICATION_TEMPLATE: EmailTemplate = EmailTemplate(
    name="email_verification",
    subject="Verify your email address",
    body_html=(
        "<p>Hello {{display_name}},</p>"
        "<p>Click the link below to verify your email address:</p>"
        '<p><a href="{{verification_url}}">Verify email</a></p>'
    ),
    body_text=(
        "Hello {{display_name}},\n\n"
        "Verify your email address by visiting the link below:\n"
        "{{verification_url}}\n"
    ),
)
