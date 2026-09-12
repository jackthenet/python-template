"""Acceptance tests for the high-level operations (AC-005, AC-006)."""

from __future__ import annotations

from backend.mail import (
    EmailSendResult,
    EmailVerificationEmailRequest,
    MailService,
    PasswordResetEmailRequest,
)
from mail_test_helpers import EventCollector, RecordingTransport, message_bodies

RESET_URL = "https://reset.example.com/reset?token=reset-token-123"
VERIFY_URL = "https://verify.example.com/verify?token=verify-token-456"


def test_ac_005_password_reset_email() -> None:
    """AC-005: send_password_reset_email uses the built-in PASSWORD_RESET_TEMPLATE."""
    transport = RecordingTransport()
    service = MailService(transport=transport, event_bus=EventCollector())

    result = service.send_password_reset_email(
        PasswordResetEmailRequest(to="alice@example.com", display_name="Alice", reset_url=RESET_URL)
    )

    assert isinstance(result, EmailSendResult)
    assert result.to == "alice@example.com"
    assert result.template == "password_reset"
    assert len(transport.messages) == 1
    text, html = message_bodies(transport.messages[0])
    assert "Alice" in text
    assert RESET_URL in text
    assert "Alice" in html
    assert RESET_URL in html


def test_ac_006_email_verification_email() -> None:
    """AC-006: send_email_verification_email uses the built-in EMAIL_VERIFICATION_TEMPLATE."""
    transport = RecordingTransport()
    service = MailService(transport=transport, event_bus=EventCollector())

    result = service.send_email_verification_email(
        EmailVerificationEmailRequest(to="bob@example.com", display_name="Bob", verification_url=VERIFY_URL)
    )

    assert result.to == "bob@example.com"
    assert result.template == "email_verification"
    assert len(transport.messages) == 1
    text, html = message_bodies(transport.messages[0])
    assert "Bob" in text
    assert VERIFY_URL in text
    assert "Bob" in html
    assert VERIFY_URL in html
