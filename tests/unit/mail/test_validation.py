"""Unit tests for template validation edge cases (EDGE-001..EDGE-003)."""

from __future__ import annotations

import pytest
from backend.mail import MailService, MailTemplateError
from mail_test_helpers import RecordingTransport, simple_template


def _assert_reason(error: MailTemplateError, expected: str) -> None:
    reason = getattr(error, "reason", None)
    haystack = str(reason) if reason is not None else str(error)
    assert expected in haystack


def test_edge_001_invalid_recipient() -> None:
    """EDGE-001: an invalid recipient raises MailTemplateError (reason 'invalid_recipient')."""
    service = MailService(transport=RecordingTransport(), event_bus=None)

    with pytest.raises(MailTemplateError) as exc_info:
        service.send_email("not-an-email", simple_template(), {"who": "A"})

    _assert_reason(exc_info.value, "invalid_recipient")


def test_edge_002_missing_variable() -> None:
    """EDGE-002: a missing template variable raises MailTemplateError (reason 'missing_variable:<name>')."""
    service = MailService(transport=RecordingTransport(), event_bus=None)

    with pytest.raises(MailTemplateError) as exc_info:
        service.send_email("a@example.com", simple_template(), {})

    _assert_reason(exc_info.value, "missing_variable:who")


def test_edge_003_malformed_template() -> None:
    """EDGE-003: a malformed template raises MailTemplateError (reason 'malformed_template')."""
    service = MailService(transport=RecordingTransport(), event_bus=None)
    malformed = simple_template(
        name="malformed",
        subject="Broken {{who",
        body_html="<p>{{who</p>",
        body_text="{{who",
    )

    with pytest.raises(MailTemplateError) as exc_info:
        service.send_email("a@example.com", malformed, {"who": "A"})

    _assert_reason(exc_info.value, "malformed_template")
