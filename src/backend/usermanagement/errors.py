"""Structured domain errors for the user-management feature (REQ-014).

The exception hierarchy is rooted at :class:`UserManagerError`. Every subclass
carries the documented context attributes and a message free of secrets
(error kind, field names, and role names only), so the messages are safe to
log (NFR-002).
"""

from __future__ import annotations


class UserManagerError(Exception):
    """Base class for all user-management domain errors."""


class UserAlreadyExistsError(UserManagerError):
    """A user with the same username or email already exists.

    ``field`` is ``"username"`` or ``"email"``.
    """

    def __init__(self, field: str) -> None:
        self.field = field
        super().__init__(f"a user with {field} already exists")


class UserNotFoundError(UserManagerError):
    """No user exists for the requested id or username."""

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or "user not found")


class InvalidRoleError(UserManagerError):
    """The requested role is not in the configured role set."""

    def __init__(self, role: str, allowed: frozenset[str]) -> None:
        self.role = role
        self.allowed = allowed
        super().__init__(f"role {role!r} is not in the allowed role set {sorted(allowed)}")


class LastAdminError(UserManagerError):
    """The operation would leave zero active admins (last-admin protection)."""

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or "operation would leave no active admin")
