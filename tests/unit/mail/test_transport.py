"""Unit tests for the smtplib-backed transport (EDGE-005..EDGE-008)."""

from __future__ import annotations

from email.message import EmailMessage

import pytest
from backend.mail import MailTransportError, SmtpTransportImpl
from mail_test_helpers import FakeSmtpServer, closed_port


def _message() -> EmailMessage:
    message = EmailMessage()
    message["From"] = "from@example.com"
    message["To"] = "to@example.com"
    message["Subject"] = "test"
    message.set_content("hello")
    return message


def _assert_reason(error: MailTransportError, expected: str) -> None:
    reason = getattr(error, "reason", None)
    haystack = str(reason) if reason is not None else str(error)
    assert expected in haystack


def test_edge_005_connection_refused() -> None:
    """EDGE-005: a refused SMTP connection raises MailTransportError (reason 'connection')."""
    transport = SmtpTransportImpl(
        host="127.0.0.1", port=closed_port(), username="", password="", use_tls=False, timeout=5
    )
    with pytest.raises(MailTransportError) as exc_info:
        transport.send(_message())
    _assert_reason(exc_info.value, "connection")


def test_edge_006_auth_failure() -> None:
    """EDGE-006: a failed SMTP authentication raises MailTransportError (reason 'authentication')."""
    server = FakeSmtpServer("auth_fail")
    try:
        transport = SmtpTransportImpl(
            host="127.0.0.1", port=server.port, username="user", password="pass", use_tls=False, timeout=5
        )
        with pytest.raises(MailTransportError) as exc_info:
            transport.send(_message())
        _assert_reason(exc_info.value, "authentication")
    finally:
        server.close()


def test_edge_007_protocol_error() -> None:
    """EDGE-007: an SMTP protocol error raises MailTransportError (reason 'smtp')."""
    server = FakeSmtpServer("protocol_fail")
    try:
        transport = SmtpTransportImpl(
            host="127.0.0.1", port=server.port, username="", password="", use_tls=False, timeout=5
        )
        with pytest.raises(MailTransportError) as exc_info:
            transport.send(_message())
        _assert_reason(exc_info.value, "smtp")
    finally:
        server.close()


def test_edge_008_timeout() -> None:
    """EDGE-008: an SMTP timeout raises MailTransportError (reason 'timeout')."""
    server = FakeSmtpServer("silent")
    try:
        transport = SmtpTransportImpl(
            host="127.0.0.1", port=server.port, username="", password="", use_tls=False, timeout=0.5
        )
        with pytest.raises(MailTransportError) as exc_info:
            transport.send(_message())
        _assert_reason(exc_info.value, "timeout")
    finally:
        server.close()
