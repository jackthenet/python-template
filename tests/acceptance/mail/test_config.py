"""Acceptance tests for SMTP configuration validation (AC-011)."""

from __future__ import annotations

import pytest
from backend.mail import MailConfigurationError, MailService
from mail_test_helpers import RecordingTransport, ensure_mail_settings, simple_template


def test_ac_011_empty_smtp_host() -> None:
    """AC-011: an empty SMTP host raises MailConfigurationError at send time."""
    ensure_mail_settings().set_value("mail.smtp_host", "")

    service = MailService(transport=RecordingTransport(), event_bus=None)

    with pytest.raises(MailConfigurationError):
        service.send_email("erin@example.com", simple_template(), {"who": "Erin"})
