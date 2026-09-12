"""Acceptance tests for service-level validation (AC-009, AC-010)."""

from __future__ import annotations

import pytest
from backend.mail import MailService, MailTemplateError
from mail_test_helpers import RecordingTransport, simple_template


def test_ac_009_invalid_recipient() -> None:
    """AC-009: an invalid recipient raises MailTemplateError."""
    service = MailService(transport=RecordingTransport(), event_bus=None)

    with pytest.raises(MailTemplateError):
        service.send_email("not-an-email", simple_template(), {"who": "Alice"})


def test_ac_010_missing_variable() -> None:
    """AC-010: a template variable missing from the context raises MailTemplateError."""
    service = MailService(transport=RecordingTransport(), event_bus=None)

    with pytest.raises(MailTemplateError):
        service.send_email("dave@example.com", simple_template(), {})
