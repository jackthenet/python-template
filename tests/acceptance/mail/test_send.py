"""Acceptance tests for the core send operation (AC-004, AC-007)."""

from __future__ import annotations

from backend.mail import EmailSendResult, MailService
from mail_test_helpers import EventCollector, RecordingTransport, message_bodies, simple_template


def test_ac_004_core_send_success() -> None:
    """AC-004: send_email sends via the transport and returns an EmailSendResult."""
    transport = RecordingTransport()
    service = MailService(transport=transport, event_bus=EventCollector())

    result = service.send_email("alice@example.com", simple_template(), {"who": "Alice"})

    assert isinstance(result, EmailSendResult)
    assert result.to == "alice@example.com"
    assert result.template == "test"
    assert len(transport.messages) == 1
    text, html = message_bodies(transport.messages[0])
    assert "Alice" in text
    assert "Alice" in html


def test_ac_007_feature_specific_template() -> None:
    """AC-007: a feature-provided EmailTemplate is sent via the core send."""
    transport = RecordingTransport()
    service = MailService(transport=transport, event_bus=None)

    template = simple_template(
        name="welcome",
        subject="Welcome {{user}}",
        body_html="<p>Welcome, {{user}}!</p>",
        body_text="Welcome, {{user}}!",
    )

    result = service.send_email("bob@example.com", template, {"user": "Bob"})

    assert result.to == "bob@example.com"
    assert result.template == "welcome"
    assert len(transport.messages) == 1
    text, html = message_bodies(transport.messages[0])
    assert "Bob" in text
    assert "Bob" in html
