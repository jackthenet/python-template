"""Acceptance tests for the built message (AC-019)."""

from __future__ import annotations

from backend.mail import MailService
from mail_test_helpers import RecordingTransport, ensure_mail_settings, message_bodies, simple_template


def test_ac_019_multipart_alternative() -> None:
    """AC-019: the built message is multipart/alternative (text + HTML); From from settings."""
    registry = ensure_mail_settings()
    registry.set_value("mail.from_name", "Test Sender")
    registry.set_value("mail.smtp_from", "sender@example.com")

    transport = RecordingTransport()
    service = MailService(transport=transport, event_bus=None)

    service.send_email("karen@example.com", simple_template(), {"who": "Karen"})

    message = transport.messages[0]
    assert message.get_content_type() == "multipart/alternative"
    from_header = str(message["From"])
    assert "Test Sender" in from_header
    assert "sender@example.com" in from_header
    text, html = message_bodies(message)
    assert "Karen" in text
    assert "Karen" in html
