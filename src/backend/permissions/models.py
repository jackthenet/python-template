"""Domain models for the permissions feature (docs/specs/user-roles-permissions.md, D15).

Table models (``Role``, ``RolePermission``, ``SystemPrincipalPermission``) are
the SQLModel/SQLite persistence behind the repository ABCs (REQ-022). Read
models (``RoleRead``, ``PermissionRead``) are the service's representations.
``SessionRecord``/``SessionLookup`` are the structural session-validation
seam (D9; the real implementation is authentication's session repository,
which stores SHA-256 token hashes).
"""

from __future__ import annotations

from datetime import datetime
from typing import Protocol
from uuid import UUID

from pydantic import BaseModel
from sqlmodel import Field as SField
from sqlmodel import SQLModel


class Role(SQLModel, table=True):
    """A runtime-managed role (the single source of truth for role names, D4)."""

    __tablename__ = "roles"

    role: str = SField(primary_key=True)  # ^[a-z0-9_-]{1,32}$
    description: str | None = None
    is_builtin: bool = False  # True for the seeded admin / user roles
    created_at: datetime  # UTC


class RolePermission(SQLModel, table=True):
    """A dynamic role->permission grant (a catalog action key or a feature
    wildcard ``<feature>.*``)."""

    __tablename__ = "role_permissions"

    role: str = SField(foreign_key="roles.role", primary_key=True)
    permission: str = SField(primary_key=True)
    granted_at: datetime  # UTC


class SystemPrincipalPermission(SQLModel, table=True):
    """A permission granted to the system principal (``user_id=None``, D10)."""

    __tablename__ = "system_principal_permissions"

    permission: str = SField(primary_key=True)
    granted_at: datetime  # UTC


class RoleRead(BaseModel):
    """The read-only role representation."""

    role: str
    description: str | None
    is_builtin: bool
    created_at: datetime


class PermissionRead(BaseModel):
    """A catalog permission (the action key ``feature.action``, D2)."""

    permission: str
    feature: str
    description: str | None


class SessionRecord(Protocol):
    """A session record as seen by the check (D9)."""

    user_id: UUID
    expires_at: datetime
    revoked: bool


class SessionLookup(Protocol):
    """Structural session-validation seam (D9)."""

    def get_by_token_hash(self, token_hash: str) -> SessionRecord | None: ...


# The built-in role names (seeded by the migration, REQ-007). These are always
# valid / "known" roles even before a row exists in the ``roles`` table (the
# grant path must accept them without a role-repository row).
BUILTIN_ROLES: frozenset[str] = frozenset({"admin", "user"})


BOOTSTRAP_SYSTEM_PERMISSIONS: frozenset[str] = frozenset({
    "usermanagement.get_user",
    "usermanagement.verify_password",
    "usermanagement.change_password",
    "settings.register",
    "settings.register_feature",
    "mail.send_email",
    "mail.send_password_reset_email",
    "mail.send_email_verification_email",
    "sessionmanagement.cleanup_expired",
})
