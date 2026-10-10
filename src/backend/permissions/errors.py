"""Structured authorization error hierarchy (docs/specs/user-roles-permissions.md, D18).

The hierarchy is rooted at ``AuthorizationError`` — a distinct class that is
not a subclass of the built-in ``PermissionError`` — so ``except
PermissionError`` never catches it (REQ-021). Errors carry non-sensitive
context only: never the session token (NFR-002).
"""

from __future__ import annotations

from uuid import UUID


class AuthorizationError(Exception):
    """Root of the permissions error hierarchy (REQ-021)."""


class PermissionDeniedError(AuthorizationError):
    """A permission check was denied (fail-closed, D12).

    ``reason`` is the closed set (D12): ``"unauthorized"``,
    ``"unknown_user"``, ``"inactive_user"``, ``"unknown_permission"``,
    ``"malformed_permission"``, ``"invalid_session"``,
    ``"session_principal_mismatch"``, ``"storage_error"``.
    """

    def __init__(self, user_id: UUID | None, permission: str, reason: str) -> None:
        """Build the message from the check context and keep the context as attributes.

        ``user_id=None`` is worded as the system principal rather than as
        ``None`` (AC-026); the message never carries a session token (NFR-002).
        """
        self.user_id = user_id
        self.permission = permission
        self.reason = reason
        if user_id is None:
            message = f"permission {permission!r} denied for the system principal ({reason})"
        else:
            message = f"permission {permission!r} denied for user {user_id} ({reason})"
        super().__init__(message)


class RoleNotFoundError(AuthorizationError):
    """The referenced role does not exist."""

    def __init__(self, role: str) -> None:
        """Carry the rejected role name so the caller never parses the message (AC-026)."""
        self.role = role
        super().__init__(f"role {role!r} not found")


class RoleAlreadyExistsError(AuthorizationError):
    """A role with the same name already exists."""

    def __init__(self, role: str) -> None:
        """Raised by the role repositories on a duplicate insert; ``create_role`` lets it propagate (REQ-006)."""
        self.role = role
        super().__init__(f"role {role!r} already exists")


class RoleInUseError(AuthorizationError):
    """The role is assigned to one or more users and cannot be deleted."""

    def __init__(self, role: str) -> None:
        """The deletion guard for a still-assigned role (REQ-007); the role is left in place."""
        self.role = role
        super().__init__(f"role {role!r} is assigned to one or more users")


class RoleProtectedError(AuthorizationError):
    """A built-in role (admin, user) is protected from deletion."""

    def __init__(self, role: str) -> None:
        """The guard on the seeded ``admin`` / ``user`` roles (REQ-007); no row is ever deleted."""
        self.role = role
        super().__init__(f"built-in role {role!r} cannot be deleted")


class UnknownPermissionError(AuthorizationError):
    """The referenced permission is not in the catalog (D18)."""

    def __init__(self, permission: str) -> None:
        """Raised by the grant/revoke and system-set paths for a key outside the closed catalog (REQ-008, EDGE-020)."""
        self.permission = permission
        super().__init__(f"permission {permission!r} is not in the catalog")
