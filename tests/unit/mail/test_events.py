"""Unit tests for event-publisher edge cases (EDGE-009)."""

from __future__ import annotations

import pytest
from backend.mail import MailService, MailTemplateError
from mail_test_helpers import RecordingTransport, simple_template


def test_edge_009_none_event_bus() -> None:
    """EDGE-009: a None event bus publishes no events and raises no error."""
    service = MailService(transport=RecordingTransport(), event_bus=None)

    # Success: no error.
    result = service.send_email("a@example.com", simple_template(), {"who": "A"})
    assert result.to == "a@example.com"

    # Failure: the MailError is raised; no publisher error.
    with pytest.raises(MailTemplateError):
        service.send_email("not-an-email", simple_template(), {"who": "A"})
