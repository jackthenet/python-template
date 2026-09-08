"""Structured domain errors for the authentication feature (REQ-019).

The exception hierarchy is rooted at :class:`AuthenticationError`. Every
subclass carries a message free of secrets (error kind only), so the messages
are safe to log (NFR-002). ``InvalidResetTokenError`` additionally carries the
documented ``reason`` (``"unknown"``, ``"expired"``, or ``"used"``).
"""

from __future__ import annotations


class AuthenticationError(Exception):
    """Base class for all authentication domain errors."""


class InvalidCredentialsError(AuthenticationError):
    """Unified login failure.

    Unknown user, wrong password, inactive user, and locked identifiers all
    raise this single error kind (D4): no user enumeration, no lock-state
    signal.
    """


class InvalidSessionError(AuthenticationError):
    """The session token is unknown, revoked, or expired."""


class InvalidResetTokenError(AuthenticationError):
    """The reset token is invalid.

    ``reason`` is ``"unknown"``, ``"expired"``, or ``"used"``.
    """

    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(f"reset token is {reason}")


class PasskeyCredentialNotFoundError(AuthenticationError):
    """No stored WebAuthn credential for the requested credential id."""


class InvalidPasskeyResponseError(AuthenticationError):
    """The WebAuthn response failed verification (registration or authentication)."""


class PasskeyHijackError(AuthenticationError):
    """The assertion sign count is lower than the stored sign count (hijack signal)."""
