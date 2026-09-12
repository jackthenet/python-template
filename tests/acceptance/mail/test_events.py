"""Acceptance tests for lifecycle events (AC-013, AC-014, AC-015)."""

from __future__ import annotations

import pytest
from backend.mail import (
    EmailFailed,
    EmailSent,
    MailService,
    MailTemplateError,
    PasswordResetEmailRequest,
)
from mail_test_helpers import (
    EventCollector,
    RecordingTransport,
    ensure_mail_settings,
    event_text,
    simple_template,
)

SMTP_PASSWORD = "smtp-secret-password"
RESET_TOKEN = "reset-token-abc-123"


def test_ac_013_email_sent_event() -> None:
    """AC-013: a successful send publishes EmailSent."""
    events = EventCollector()
    service = MailService(transport=RecordingTransport(), event_bus=events)

    service.send_email("grace@example.com", simple_template(), {"who": "Grace"})

    sent = events.of_type(EmailSent)
    assert len(sent) == 1
    assert sent[0].to == "grace@example.com"
    assert sent[0].template == "test"


def test_ac_014_email_failed_event() -> None:
    """AC-014: a failed send publishes EmailFailed (with the error kind) and re-raises."""
    events = EventCollector()
    service = MailService(transport=RecordingTransport(), event_bus=events)

    with pytest.raises(MailTemplateError):
        service.send_email("not-an-email", simple_template(), {"who": "Heidi"})

    failed = events.of_type(EmailFailed)
    assert len(failed) == 1
    assert failed[0].to == "not-an-email"
    assert failed[0].template == "test"
    assert failed[0].reason == "template"


def test_ac_015_non_sensitive_events() -> None:
    """AC-015: events carry no email body, rendered subject, token, or SMTP password."""
    ensure_mail_settings().set_value("mail.smtp_password", SMTP_PASSWORD)
    events = EventCollector()
    service = MailService(transport=RecordingTransport(), event_bus=events)

    service.send_password_reset_email(
        PasswordResetEmailRequest(
            to="ivan@example.com",
            display_name="Ivan",
            reset_url=f"https://reset.example.com/reset?token={RESET_TOKEN}",
        )
    )
    with pytest.raises(MailTemplateError):
        service.send_email("not-an-email", simple_template(), {"who": "Ivan"})

    for event in events.events:
        text = event_text(event)
        assert SMTP_PASSWORD not in text
        assert RESET_TOKEN not in text
        # The email body and the rendered subject are not part of the payload.
        assert "Hello" not in text
        assert "Reset your password" not in text
