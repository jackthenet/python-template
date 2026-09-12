"""Acceptance tests for transport failures (AC-012)."""

from __future__ import annotations

import pytest
from backend.mail import MailService, MailTransportError
from mail_test_helpers import FailingTransport, simple_template


def test_ac_012_transport_failure() -> None:
    """AC-012: a transport failure raises MailTransportError."""
    failing = FailingTransport(reason="connection")
    service = MailService(transport=failing, event_bus=None)

    with pytest.raises(MailTransportError):
        service.send_email("frank@example.com", simple_template(), {"who": "Frank"})

    assert failing.calls == 1
