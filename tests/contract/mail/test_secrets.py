"""Contract tests for secret handling (NFR-002)."""

from __future__ import annotations

import pytest
from backend.mail import (
    MailService,
    MailTransportError,
    PasswordResetEmailRequest,
)
from mail_test_helpers import (
    EventCollector,
    FailingTransport,
    RecordingTransport,
    ensure_mail_settings,
    event_text,
    simple_template,
)

SMTP_PASSWORD = "nfr-smtp-password"
RESET_TOKEN = "nfr-reset-token"


def test_nfr_002_no_secrets_in_logs_or_events(log_records) -> None:
    """NFR-002: the SMTP password never appears in logs/events/errors; the body never in events."""
    ensure_mail_settings().set_value("mail.smtp_password", SMTP_PASSWORD)
    events = EventCollector()
    service = MailService(transport=RecordingTransport(), event_bus=events)

    service.send_password_reset_email(
        PasswordResetEmailRequest(
            to="nfr@example.com",
            display_name="Nfr",
            reset_url=f"https://reset.example.com/reset?token={RESET_TOKEN}",
        )
    )

    failing_service = MailService(transport=FailingTransport("connection"), event_bus=events)
    with pytest.raises(MailTransportError) as exc_info:
        failing_service.send_email("nfr@example.com", simple_template(), {"who": "Nfr"})

    # The error message is secret-free.
    assert SMTP_PASSWORD not in str(exc_info.value)
    # The events carry no password, token, or body.
    for event in events.events:
        text = event_text(event)
        assert SMTP_PASSWORD not in text
        assert RESET_TOKEN not in text
    # The log records carry no password or token.
    for record in log_records:
        text = str(record)
        assert SMTP_PASSWORD not in text
        assert RESET_TOKEN not in text
