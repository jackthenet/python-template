"""Property tests for send independence (INV-005)."""

from __future__ import annotations

import pytest
from backend.mail import MailService, MailTransportError
from hypothesis import given
from hypothesis import strategies as st
from mail_test_helpers import EventCollector, FlakyTransport, simple_template


@given(
    failures=st.integers(min_value=0, max_value=3),
    successes=st.integers(min_value=1, max_value=5),
)
def test_inv_005_failure_independence(failures: int, successes: int) -> None:
    """INV-005: a send failure does not affect subsequent sends."""
    transport = FlakyTransport(fail_count=failures)
    events = EventCollector()
    service = MailService(transport=transport, event_bus=events)
    template = simple_template()

    for i in range(failures):
        with pytest.raises(MailTransportError):
            service.send_email(f"fail{i}@example.com", template, {"who": "F"})

    for i in range(successes):
        result = service.send_email(f"ok{i}@example.com", template, {"who": "O"})
        assert result.to == f"ok{i}@example.com"

    assert len(transport.messages) == successes
