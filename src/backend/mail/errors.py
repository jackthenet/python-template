"""The mail error hierarchy (docs/specs/mail-service.md, D8, ADR-045).

Every error carries a short, secret-free ``reason`` string (error kind + short
reason only). The SMTP password, a token, and the email body are never part of
an error message (NFR-002).
"""

from __future__ import annotations


class MailError(Exception):
    """Base class for all mail domain errors."""


class MailConfigurationError(MailError):
    """The mail service is not correctly configured at send time.

    Raised when a required SMTP setting is missing or unusable (e.g., the SMTP
    host is empty). ``reason`` is a short, secret-free string (e.g.,
    ``"smtp_host_empty"``).
    """

    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(reason)


class MailTransportError(MailError):
    """The SMTP transport failed to deliver the email.

    Raised on connection failure, authentication failure, an SMTP protocol
    error, or a timeout. ``reason`` is a short, secret-free string (e.g.,
    ``"connection"``, ``"authentication"``, ``"smtp"``, ``"timeout"``). The
    SMTP password is never included.
    """

    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(reason)


class MailTemplateError(MailError):
    """The email could not be prepared from its template.

    Raised when the recipient is not a valid email address, a template variable
    is missing from the context, or the template is malformed (a ``{{`` without
    a closing ``}}``). ``reason`` is a short, secret-free string (e.g.,
    ``"invalid_recipient"``, ``"missing_variable:reset_url"``,
    ``"malformed_template"``).
    """

    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(reason)
