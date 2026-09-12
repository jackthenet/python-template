"""Contract tests for the public API backward-compatibility contract (NFR-003)."""

from __future__ import annotations

import pytest
from backend.mail import (
    EMAIL_VERIFICATION_TEMPLATE,
    PASSWORD_RESET_TEMPLATE,
    EmailFailed,
    EmailSendResult,
    EmailSent,
    EmailTemplate,
    EmailVerificationEmailRequest,
    MailConfigurationError,
    MailError,
    MailEvent,
    MailService,
    MailTemplateError,
    MailTransportError,
    PasswordResetEmailRequest,
    SmtpTransport,
    SmtpTransportImpl,
)
from pydantic import ValidationError


def test_nfr_003_public_api_stable() -> None:
    """NFR-003: the public API of backend.mail is a backward-compatibility contract."""
    # The service exposes the three operations.
    for op in ("send_email", "send_password_reset_email", "send_email_verification_email"):
        assert callable(getattr(MailService, op))

    # The error hierarchy is rooted at MailError (an Exception).
    assert issubclass(MailError, Exception)
    for error in (MailConfigurationError, MailTransportError, MailTemplateError):
        assert issubclass(error, MailError)

    # The transport ABC and the smtplib-backed implementation.
    assert "send" in SmtpTransport.__abstractmethods__
    assert issubclass(SmtpTransportImpl, SmtpTransport)

    # The events are frozen Pydantic models rooted at MailEvent.
    assert issubclass(EmailSent, MailEvent)
    assert issubclass(EmailFailed, MailEvent)
    assert EmailSent.model_config.get("frozen") is True
    assert EmailFailed.model_config.get("frozen") is True

    # The representation is frozen.
    assert EmailSendResult.model_config.get("frozen") is True

    # The request schemas validate their fields (schema-level validation).
    reset = PasswordResetEmailRequest(to="a@example.com", display_name="A", reset_url="https://r.example.com")
    assert reset.to == "a@example.com"
    verify = EmailVerificationEmailRequest(
        to="a@example.com", display_name="A", verification_url="https://v.example.com"
    )
    assert verify.to == "a@example.com"
    with pytest.raises(ValidationError):
        PasswordResetEmailRequest(to="not-an-email", display_name="A", reset_url="https://r.example.com")

    # The built-in templates are stable module constants.
    assert isinstance(PASSWORD_RESET_TEMPLATE, EmailTemplate)
    assert PASSWORD_RESET_TEMPLATE.name == "password_reset"
    assert "{{display_name}}" in PASSWORD_RESET_TEMPLATE.body_html
    assert "{{reset_url}}" in PASSWORD_RESET_TEMPLATE.body_html
    assert isinstance(EMAIL_VERIFICATION_TEMPLATE, EmailTemplate)
    assert EMAIL_VERIFICATION_TEMPLATE.name == "email_verification"
    assert "{{display_name}}" in EMAIL_VERIFICATION_TEMPLATE.body_html
    assert "{{verification_url}}" in EMAIL_VERIFICATION_TEMPLATE.body_html
