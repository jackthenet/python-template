"""The SMTP transport ABC and the smtplib-backed implementation (D1, ADR-043/046).

``SmtpTransport`` is the seam for testability (a single ``send(message)``
operation). ``SmtpTransportImpl`` is the smtplib-backed default: it connects per
send (no long-lived connection), authenticates when a username is present, sends
the message, and closes. Failures are wrapped in ``MailTransportError`` with a
secret-free ``reason``; the SMTP password is never included in the error, in any
log, or in any event (NFR-002).
"""

from __future__ import annotations

import contextlib
import socket
import smtplib
from abc import ABC, abstractmethod
from email.message import EmailMessage

from backend.mail.errors import MailTransportError


class SmtpTransport(ABC):
    """The physical SMTP send (the seam for testability)."""

    @abstractmethod
    def send(self, message: EmailMessage) -> None:
        """Send ``message``; raise ``MailTransportError`` on failure."""


class SmtpTransportImpl(SmtpTransport):
    """The smtplib-backed default transport (connects per send)."""

    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        use_tls: bool,
        timeout: float,
    ) -> None:
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._use_tls = use_tls
        self._timeout = timeout

    def send(self, message: EmailMessage) -> None:
        """Connect, authenticate when credentials are present, send, close."""
        server: smtplib.SMTP | None = None
        try:
            server = smtplib.SMTP(self._host, self._port, timeout=self._timeout)
            server.ehlo()
            if self._use_tls:
                server.starttls()
                server.ehlo()
            if self._username:
                # Force the AUTH extension so login() sends the AUTH command
                # even when the server's EHLO response does not advertise it.
                server.esmtp_features["auth"] = "PLAIN"
                server.login(self._username, self._password)
            server.send_message(message)
        except smtplib.SMTPAuthenticationError:
            raise MailTransportError("authentication") from None
        except socket.timeout:
            raise MailTransportError("timeout") from None
        except smtplib.SMTPServerDisconnected as exc:
            # A greeting-read timeout is wrapped into SMTPServerDisconnected;
            # distinguish it from a plain disconnection by the timeout message.
            detail = str(exc).lower()
            if "timed out" in detail or "timeout" in detail:
                raise MailTransportError("timeout") from None
            raise MailTransportError("smtp") from None
        except smtplib.SMTPException:
            raise MailTransportError("smtp") from None
        except (ConnectionRefusedError, socket.gaierror, OSError):
            raise MailTransportError("connection") from None
        finally:
            if server is not None:
                with contextlib.suppress(Exception):
                    server.quit()
