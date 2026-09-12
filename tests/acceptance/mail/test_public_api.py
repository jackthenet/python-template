"""Acceptance tests for the public API (AC-017)."""

from __future__ import annotations

from backend.mail import (
    EMAIL_VERIFICATION_TEMPLATE,
    PASSWORD_RESET_TEMPLATE,
    EmailSendResult,
    EmailSent,
    EmailTemplate,
    EmailVerificationEmailRequest,
    MailConfigurationError,
    MailError,
    MailService,
    MailTemplateError,
    MailTransportError,
    PasswordResetEmailRequest,
    SmtpTransport,
)


def test_ac_017_public_api_stable() -> None:
    """AC-017: the public API (service, models, errors, transport ABC, events, templates) is present."""
    # Service.
    assert isinstance(MailService, type)
    # Request / representation models.
    for model in (PasswordResetEmailRequest, EmailVerificationEmailRequest, EmailSendResult):
        assert isinstance(model, type)
    # Error hierarchy rooted at MailError.
    assert issubclass(MailError, Exception)
    assert issubclass(MailConfigurationError, MailError)
    assert issubclass(MailTransportError, MailError)
    assert issubclass(MailTemplateError, MailError)
    # Transport ABC with the send operation.
    assert isinstance(SmtpTransport, type)
    assert "send" in SmtpTransport.__abstractmethods__
    # Events.
    assert isinstance(EmailSent, type)
    # Built-in templates.
    assert isinstance(PASSWORD_RESET_TEMPLATE, EmailTemplate)
    assert PASSWORD_RESET_TEMPLATE.name == "password_reset"
    assert isinstance(EMAIL_VERIFICATION_TEMPLATE, EmailTemplate)
    assert EMAIL_VERIFICATION_TEMPLATE.name == "email_verification"
