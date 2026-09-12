"""Acceptance tests for observability (AC-016)."""

from __future__ import annotations

import pytest
from backend.mail import (
    MailService,
    MailTemplateError,
    PasswordResetEmailRequest,
)
from mail_test_helpers import (
    EventCollector,
    RecordingTransport,
    ensure_mail_settings,
    simple_template,
)

SMTP_PASSWORD = "smtp-log-secret"
RESET_TOKEN = "log-reset-token-999"


def test_ac_016_no_secrets_in_log_records(log_records) -> None:
    """AC-016: no log record contains the SMTP password or a token."""
    ensure_mail_settings().set_value("mail.smtp_password", SMTP_PASSWORD)
    service = MailService(transport=RecordingTransport(), event_bus=EventCollector())

    service.send_password_reset_email(
        PasswordResetEmailRequest(
            to="judy@example.com",
            display_name="Judy",
            reset_url=f"https://reset.example.com/reset?token={RESET_TOKEN}",
        )
    )
    with pytest.raises(MailTemplateError):
        service.send_email("not-an-email", simple_template(), {"who": "Judy"})

    for record in log_records:
        text = str(record)
        assert SMTP_PASSWORD not in text
        assert RESET_TOKEN not in text
