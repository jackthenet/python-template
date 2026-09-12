"""Shared helpers for the mail test suite.

The helpers import the feature's public API from ``backend.mail`` at module
level: while the feature is unimplemented, every mail test fails with
``ModuleNotFoundError: backend.mail`` — the RED state for this feature.
"""

from __future__ import annotations

import contextlib
import socket
import threading
from email.message import EmailMessage
from typing import Any

from backend.mail import EmailTemplate, MailTransportError, SmtpTransport


def reset_registry() -> None:
    """Reset the settings-registry module singleton (cross-test isolation)."""
    from backend.settings import reset_settings_registry

    reset_settings_registry()


def setup_isolated_registry() -> None:
    """Install a fresh settings registry backed by a temp-dir value repository.

    Isolates the mail test suite's settings store so that no value is ever
    persisted to the shared ``settings/`` directory and nothing written by one
    mail test leaks into another (test isolation). The registry starts from
    the registered defaults; this changes no test assertion.
    """
    import tempfile

    from backend.settings import SettingsRegistry, YamlValueRepository
    from backend.settings import registry as _settings_registry_module

    _settings_registry_module.reset_settings_registry()
    isolated = SettingsRegistry(
        value_repository=YamlValueRepository(tempfile.mkdtemp())
    )
    _settings_registry_module._registry[0] = isolated


def ensure_mail_settings() -> Any:
    """Return the settings registry with the mail settings registered.

    Idempotent: registers the mail settings only when they are not registered
    yet (e.g., repeated Hypothesis examples within one test).
    """
    from backend.settings import get_settings_registry

    registry = get_settings_registry()
    try:
        registry.get_value("mail.smtp_host")
    except Exception:
        from backend.mail import register_settings

        register_settings(registry)
    return registry


def resolve_mail_config() -> Any:
    """The live SMTP config resolution (the read the service performs per send)."""
    try:
        from backend.mail import resolve_mail_config as _resolve
    except ImportError:
        from backend.mail.feature_settings import resolve_mail_config as _resolve
    return _resolve()


def event_text(event: object) -> str:
    """Serialize an event to a string for secret scanning."""
    dump_json = getattr(event, "model_dump_json", None)
    if callable(dump_json):
        return dump_json()
    dump = getattr(event, "model_dump", None)
    if callable(dump):
        return repr(dump())
    return repr(event)


def message_bodies(message: EmailMessage) -> tuple[str, str]:
    """Return the (text/plain, text/html) bodies of a multipart message."""
    text = ""
    html = ""
    for part in message.iter_parts():
        content_type = part.get_content_type()
        if content_type == "text/plain":
            text = part.get_content()
        elif content_type == "text/html":
            html = part.get_content()
    return text, html


def simple_template(
    name: str = "test",
    subject: str = "Test {{who}}",
    body_html: str = "<p>Test {{who}}</p>",
    body_text: str = "Test {{who}}",
) -> EmailTemplate:
    """Build an EmailTemplate for a test."""
    return EmailTemplate(name=name, subject=subject, body_html=body_html, body_text=body_text)


class EventCollector:
    """A synchronous event publisher for exact event observation.

    Structurally satisfies the ``EventPublisher`` protocol (a ``publish``
    method), so it can be injected into ``MailService``.
    """

    def __init__(self) -> None:
        self.events: list[object] = []

    def publish(self, event: object) -> None:
        self.events.append(event)

    def of_type(self, event_type: type) -> list[object]:
        return [event for event in self.events if isinstance(event, event_type)]


class RecordingTransport(SmtpTransport):
    """A transport that records messages instead of sending them."""

    def __init__(self) -> None:
        self.messages: list[EmailMessage] = []

    def send(self, message: EmailMessage) -> None:
        self.messages.append(message)


class FailingTransport(SmtpTransport):
    """A transport that always fails with a given secret-free reason."""

    def __init__(self, reason: str = "connection") -> None:
        self.reason = reason
        self.calls = 0

    def send(self, message: EmailMessage) -> None:
        self.calls += 1
        raise MailTransportError(self.reason)


class FlakyTransport(SmtpTransport):
    """A transport that fails its first ``fail_count`` sends, then records."""

    def __init__(self, fail_count: int = 1) -> None:
        self.fail_count = fail_count
        self.calls = 0
        self.messages: list[EmailMessage] = []

    def send(self, message: EmailMessage) -> None:
        self.calls += 1
        if self.calls <= self.fail_count:
            raise MailTransportError("connection")
        self.messages.append(message)


def closed_port() -> int:
    """Return a localhost port with no listener (a connect is refused)."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


class FakeSmtpServer:
    """A minimal raw-socket SMTP responder for transport tests.

    Handles a single connection. Modes:

    - ``"silent"``: accept the connection and never respond, so the client
      times out reading the greeting (``socket.timeout``).
    - ``"auth_fail"``: 220 greeting; EHLO -> 250; AUTH -> 535
      (``SMTPAuthenticationError``).
    - ``"protocol_fail"``: 220 greeting; EHLO -> 250; MAIL FROM -> 550
      (an ``SMTPException`` protocol error).
    """

    def __init__(self, mode: str = "silent") -> None:
        self.mode = mode
        self._conn: socket.socket | None = None
        self._server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_sock.bind(("127.0.0.1", 0))
        self._server_sock.listen(1)
        self.port = self._server_sock.getsockname()[1]
        self._thread = threading.Thread(target=self._serve, daemon=True)
        self._thread.start()

    def _serve(self) -> None:
        try:
            conn, _ = self._server_sock.accept()
        except OSError:
            return
        self._conn = conn
        try:
            if self.mode == "silent":
                self._hold(conn)
                return
            self._send(conn, "220 fake.smtp.local ready\r\n")
            self._dialogue(conn)
        except OSError:
            pass
        finally:
            with contextlib.suppress(OSError):
                conn.close()

    def _hold(self, conn: socket.socket) -> None:
        """Hold the connection open without responding until it closes."""
        while True:
            try:
                if not conn.recv(1):
                    return
            except OSError:
                return

    def _dialogue(self, conn: socket.socket) -> None:
        while True:
            line = self._readline(conn)
            if line is None:
                return
            cmd = line.decode("utf-8", "replace").strip().upper()
            if cmd.startswith("EHLO"):
                self._send(conn, "250 fake.smtp.local\r\n")
            elif cmd.startswith("AUTH"):
                if self.mode == "auth_fail":
                    self._send(conn, "535 authentication failed\r\n")
                    return
                self._send(conn, "235 authentication ok\r\n")
            elif cmd.startswith("MAIL FROM"):
                if self.mode == "protocol_fail":
                    self._send(conn, "550 protocol error\r\n")
                    return
                self._send(conn, "250 ok\r\n")
            elif cmd.startswith("RCPT TO"):
                self._send(conn, "250 ok\r\n")
            elif cmd.startswith("DATA"):
                self._send(conn, "354 go ahead\r\n")
                self._read_data(conn)
                self._send(conn, "250 queued\r\n")
            elif cmd.startswith("QUIT"):
                self._send(conn, "221 bye\r\n")
                return
            else:
                self._send(conn, "250 ok\r\n")

    def _readline(self, conn: socket.socket) -> bytes | None:
        chunk = conn.recv(1)
        if not chunk:
            return None
        line = bytearray(chunk)
        while not line.endswith(b"\r\n"):
            chunk = conn.recv(1)
            if not chunk:
                return bytes(line)
            line.extend(chunk)
        return bytes(line)

    def _read_data(self, conn: socket.socket) -> None:
        while True:
            line = self._readline(conn)
            if line is None or line.rstrip(b"\r\n") == b".":
                return

    @staticmethod
    def _send(conn: socket.socket, data: str) -> None:
        conn.sendall(data.encode("utf-8"))

    def close(self) -> None:
        with contextlib.suppress(OSError):
            self._server_sock.close()
        if self._conn is not None:
            with contextlib.suppress(OSError):
                self._conn.close()
        self._thread.join(timeout=5)
