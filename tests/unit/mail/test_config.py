"""Unit tests for SMTP configuration edge cases (EDGE-004)."""

from __future__ import annotations

import pytest
from backend.mail import MailConfigurationError, MailService
from mail_test_helpers import RecordingTransport, ensure_mail_settings, simple_template


def test_edge_004_empty_smtp_host() -> None:
    """EDGE-004: an empty SMTP host raises MailConfigurationError (reason 'smtp_host_empty')."""
    ensure_mail_settings().set_value("mail.smtp_host", "")
    service = MailService(transport=RecordingTransport(), event_bus=None)

    with pytest.raises(MailConfigurationError) as exc_info:
        service.send_email("a@example.com", simple_template(), {"who": "A"})

    reason = getattr(exc_info.value, "reason", None)
    haystack = str(reason) if reason is not None else str(exc_info.value)
    assert "smtp_host_empty" in haystack
