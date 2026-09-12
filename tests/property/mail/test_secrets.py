"""Property tests for secret handling (INV-003, INV-004)."""

from __future__ import annotations

import pytest
from backend.mail import MailService, MailTransportError, PasswordResetEmailRequest
from hypothesis import given
from hypothesis import strategies as st
from mail_test_helpers import (
    EventCollector,
    FailingTransport,
    RecordingTransport,
    ensure_mail_settings,
    event_text,
    simple_template,
)


@given(password=st.text(min_size=1, max_size=64))
def test_inv_003_no_password_in_observable_output(password: str) -> None:
    """INV-003: the SMTP password never appears in the result, error message, or events."""
    ensure_mail_settings().set_value("mail.smtp_password", password)
    template = simple_template()

    # Success: the password is not in the result or the EmailSent event.
    events = EventCollector()
    service = MailService(transport=RecordingTransport(), event_bus=events)
    result = service.send_email("a@example.com", template, {"who": "A"})
    assert password not in repr(result)
    for event in events.events:
        assert password not in event_text(event)

    # Failure: the password is not in the error message or the EmailFailed event.
    events = EventCollector()
    service = MailService(transport=FailingTransport("connection"), event_bus=events)
    with pytest.raises(MailTransportError) as exc_info:
        service.send_email("a@example.com", template, {"who": "A"})
    assert password not in str(exc_info.value)
    for event in events.events:
        assert password not in event_text(event)


@given(token=st.text(min_size=1, max_size=64))
def test_inv_004_no_body_in_events(token: str) -> None:
    """INV-004: the email body (containing tokens) never appears in the published events."""
    reset_url = f"https://reset.example.com/reset?token={token}"
    request = PasswordResetEmailRequest(to="b@example.com", display_name="B", reset_url=reset_url)

    # Success: the body (with the token) is not in the EmailSent event.
    success_events = EventCollector()
    service = MailService(transport=RecordingTransport(), event_bus=success_events)
    service.send_password_reset_email(request)

    # Failure: the body (with the token) is not in the EmailFailed event.
    failure_events = EventCollector()
    service = MailService(transport=FailingTransport("connection"), event_bus=failure_events)
    with pytest.raises(MailTransportError):
        service.send_password_reset_email(request)

    for collector in (success_events, failure_events):
        for event in collector.events:
            text = event_text(event)
            assert token not in text
