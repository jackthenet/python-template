"""Unit tests for send independence (EDGE-010)."""

from __future__ import annotations

import pytest
from backend.mail import EmailFailed, EmailSent, MailService, MailTransportError
from mail_test_helpers import EventCollector, FlakyTransport, simple_template


def test_edge_010_failure_then_success() -> None:
    """EDGE-010: a failed send followed by a successful send — no state carried over."""
    transport = FlakyTransport(fail_count=1)
    events = EventCollector()
    service = MailService(transport=transport, event_bus=events)
    template = simple_template()

    with pytest.raises(MailTransportError):
        service.send_email("first@example.com", template, {"who": "First"})

    result = service.send_email("second@example.com", template, {"who": "Second"})
    assert result.to == "second@example.com"
    assert len(transport.messages) == 1
    # The failed send published EmailFailed; the successful send published EmailSent.
    assert len(events.of_type(EmailFailed)) == 1
    assert len(events.of_type(EmailSent)) == 1
