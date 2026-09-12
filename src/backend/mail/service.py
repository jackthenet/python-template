"""The MailService use-case service (docs/specs/mail-service.md, D4-D6, D10, D13).

``MailService`` composes: validate recipient -> render template -> build a
``multipart/alternative`` ``EmailMessage`` (From from the settings) -> resolve
the SMTP configuration live -> send via the transport -> publish the lifecycle
event. It raises the ``MailError`` hierarchy on failure (and publishes
``EmailFailed``).

The service is traced with ``@logged_class`` (``include_args=False`` so the SMTP
password and tokens never appear in log records; ``slow_threshold_ms=5000``
because the SMTP send is network-dependent) (REQ-014, ADR-047).
"""

from __future__ import annotations

from backend.logging import logged_class

from backend.mail.errors import MailConfigurationError, MailTemplateError, MailTransportError
from backend.mail.events import EmailFailed, EmailSent, MailEvent
from backend.mail.feature_settings import MailConfig, resolve_mail_config
from backend.mail.message import build_message, validate_recipient
from backend.mail.models import (
    EmailSendResult,
    EmailVerificationEmailRequest,
    EventPublisher,
    PasswordResetEmailRequest,
)
from backend.mail.render import render_template
from backend.mail.templates import EMAIL_VERIFICATION_TEMPLATE, PASSWORD_RESET_TEMPLATE, EmailTemplate
from backend.mail.transport import SmtpTransport, SmtpTransportImpl


@logged_class(slow_threshold_ms=5000, include_args=False)
class MailService:
    """The reusable email-sending service other features consume."""

    def __init__(
        self,
        transport: SmtpTransport | None = None,
        event_bus: EventPublisher | None = None,
    ) -> None:
        self._transport = transport
        self._event_bus = event_bus

    def send_email(self, to: str, template: EmailTemplate, context: dict[str, str]) -> EmailSendResult:
        """The core send operation (REQ-003, REQ-006)."""
        try:
            validate_recipient(to)
            rendered = render_template(template, context)
            config = resolve_mail_config()
            if not config.host:
                raise MailConfigurationError("smtp_host_empty")
            message = build_message(to, rendered, config.from_name, config.from_address)
            transport = self._get_transport(config)
            transport.send(message)
            self._publish(EmailSent(to=to, template=template.name))
            return EmailSendResult(to=to, template=template.name)
        except MailTemplateError:
            self._publish(EmailFailed(to=to, template=template.name, reason="template"))
            raise
        except MailConfigurationError:
            self._publish(EmailFailed(to=to, template=template.name, reason="configuration"))
            raise
        except MailTransportError:
            self._publish(EmailFailed(to=to, template=template.name, reason="transport"))
            raise

    def send_password_reset_email(self, request: PasswordResetEmailRequest) -> EmailSendResult:
        """Send a password-reset email using the built-in template (REQ-004)."""
        context = {"display_name": request.display_name, "reset_url": request.reset_url}
        return self.send_email(request.to, PASSWORD_RESET_TEMPLATE, context)

    def send_email_verification_email(self, request: EmailVerificationEmailRequest) -> EmailSendResult:
        """Send an email-verification email using the built-in template (REQ-005)."""
        context = {"display_name": request.display_name, "verification_url": request.verification_url}
        return self.send_email(request.to, EMAIL_VERIFICATION_TEMPLATE, context)

    def _get_transport(self, config: MailConfig) -> SmtpTransport:
        """Return the injected transport, or build one from the live config (D1, D13)."""
        if self._transport is not None:
            return self._transport
        return SmtpTransportImpl(
            host=config.host,
            port=config.port,
            username=config.username,
            password=config.password,
            use_tls=config.use_tls,
            timeout=config.timeout,
        )

    def _publish(self, event: MailEvent) -> None:
        """Publish ``event`` to the injected publisher (a None publisher means no events)."""
        if self._event_bus is not None:
            self._event_bus.publish(event)
