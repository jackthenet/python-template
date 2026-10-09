"""Structured domain errors for the user-management feature (REQ-014).

The exception hierarchy is rooted at :class:`UserManagerError`. Every subclass
carries the documented context attributes and a message free of secrets
(error kind, field names, and role names only), so the messages are safe to
log (NFR-002).
"""

from __future__ import annotations

from collections.abc import Sequence


class UserManagerError(Exception):
    """Base class for all user-management domain errors."""


class UserAlreadyExistsError(UserManagerError):
    """A user with the same username or email already exists.

    ``field`` is ``"username"`` or ``"email"``.
    """

    def __init__(self, field: str) -> None:
        """``field`` names the unique column that collided.

        It is the only value interpolated into the message — the colliding
        username/email value itself never reaches the message (NFR-002).
        """
        self.field = field
        super().__init__(f"a user with {field} already exists")


class UserNotFoundError(UserManagerError):
    """No user exists for the requested id or username."""

    def __init__(self, message: str | None = None) -> None:
        """An explicit ``message`` names the identifier the raising site looked up.

        Without one, the generic "user not found" wording is used.
        """
        super().__init__(message or "user not found")


class InvalidRoleError(UserManagerError):
    """The requested role is not in the role store's role set."""

    def __init__(self, role: str, allowed: Sequence[str]) -> None:
        """``allowed`` is the whole role set the store accepts.

        It is sorted into the message so the caller can see what would have
        been valid.
        """
        self.role = role
        self.allowed = allowed
        super().__init__(f"role {role!r} is not in the allowed role set {sorted(allowed)}")


class LastAdminError(UserManagerError):
    """The operation would leave zero active admins (last-admin protection)."""

    def __init__(self, message: str | None = None) -> None:
        """Every guard site raises it bare, so the default wording is what a caller sees (REQ-008)."""
        super().__init__(message or "operation would leave no active admin")
