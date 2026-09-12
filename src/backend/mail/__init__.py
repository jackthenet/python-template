"""Public API of the mail feature (module: backend.mail).

The public API is the NFR-003 backward-compatibility contract: the service, the
request/representation models, the error hierarchy, the transport ABC +
implementation, the events, the built-in templates, and the settings
registration/resolution.
"""

from __future__ import annotations

from backend.mail.errors import (
    MailConfigurationError,
    MailError,
    MailTemplateError,
    MailTransportError,
)
from backend.mail.events import EmailFailed, EmailSent, MailEvent
from backend.mail.feature_settings import MailConfig, register_settings, resolve_mail_config
from backend.mail.message import build_message, validate_recipient
from backend.mail.models import (
    EmailSendResult,
    EmailVerificationEmailRequest,
    EventPublisher,
    PasswordResetEmailRequest,
)
from backend.mail.render import RenderedTemplate, render_template
from backend.mail.service import MailService
from backend.mail.templates import EMAIL_VERIFICATION_TEMPLATE, PASSWORD_RESET_TEMPLATE, EmailTemplate
from backend.mail.transport import SmtpTransport, SmtpTransportImpl

__all__ = [
    "EMAIL_VERIFICATION_TEMPLATE",
    "PASSWORD_RESET_TEMPLATE",
    "EmailFailed",
    "EmailSendResult",
    "EmailSent",
    "EmailTemplate",
    "EmailVerificationEmailRequest",
    "EventPublisher",
    "MailConfig",
    "MailConfigurationError",
    "MailError",
    "MailEvent",
    "MailService",
    "MailTemplateError",
    "MailTransportError",
    "PasswordResetEmailRequest",
    "RenderedTemplate",
    "SmtpTransport",
    "SmtpTransportImpl",
    "build_message",
    "register_settings",
    "render_template",
    "resolve_mail_config",
    "validate_recipient",
]
