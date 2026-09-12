"""Acceptance tests for template rendering (AC-008)."""

from __future__ import annotations

from backend.mail import MailService
from mail_test_helpers import RecordingTransport, message_bodies, simple_template


def test_ac_008_template_rendering() -> None:
    """AC-008: each {{variable}} is replaced with the context value, HTML-escaped."""
    transport = RecordingTransport()
    service = MailService(transport=transport, event_bus=None)

    xss_value = "<script>alert('x')</script>"
    template = simple_template(
        name="render",
        subject="Hello {{who}}",
        body_html="<p>Hello {{who}}</p>",
        body_text="Hello {{who}}",
    )

    service.send_email("carol@example.com", template, {"who": xss_value})

    text, html = message_bodies(transport.messages[0])
    # The value is HTML-escaped in the rendered output (no raw markup).
    assert "<script>" not in text
    assert "<script>" not in html
    assert "&lt;script&gt;" in text
    assert "&lt;script&gt;" in html
