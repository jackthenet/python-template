"""Typed lifecycle events for the permissions feature (docs/specs/user-roles-permissions.md, D17).

Events carry non-sensitive data only: no session token, no user account data
(REQ-020, NFR-002). The publisher is optional (``None`` -> no events, no
errors, AC-025).
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Protocol
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PermissionEvent(BaseModel):
    """Base class for permissions lifecycle events (``occurred_at`` is UTC)."""

    model_config = ConfigDict(frozen=True)

    occurred_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class PermissionDenied(PermissionEvent):
    """A permission check was denied (``reason`` is the closed set, D12)."""

    user_id: UUID | None
    permission: str
    reason: str


class RoleCreated(PermissionEvent):
    """A role was created."""

    role: str


class RoleDeleted(PermissionEvent):
    """A role was deleted."""

    role: str


class RolePermissionsChanged(PermissionEvent):
    """A role's explicit grants changed (grant/revoke)."""

    role: str
    added: list[str]
    removed: list[str]


class EventPublisher(Protocol):
    """Structural publisher protocol satisfied by the shared event bus."""

    def publish(self, event: object) -> None: ...
