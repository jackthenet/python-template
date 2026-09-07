"""Typed lifecycle events and the publisher protocol (REQ-016, REQ-017).

Events carry non-sensitive data only (D11): no password, no hash. Each
successful mutation publishes exactly one event; failures and no-ops publish
none (D10).
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Protocol
from uuid import UUID

from pydantic import BaseModel, Field


def _utcnow() -> datetime:
    return datetime.now(UTC)


class UserEvent(BaseModel):
    """Base class for all user lifecycle events (``occurred_at`` is UTC)."""

    occurred_at: datetime = Field(default_factory=_utcnow)


class UserCreated(UserEvent):
    user_id: UUID
    username: str
    email: str
    role: str


class UserUpdated(UserEvent):
    user_id: UUID
    changed_fields: list[str]


class UserDeleted(UserEvent):
    user_id: UUID
    username: str


class UserPasswordChanged(UserEvent):
    user_id: UUID


class UserRoleChanged(UserEvent):
    user_id: UUID
    old_role: str
    new_role: str


class UserActivated(UserEvent):
    user_id: UUID


class UserDeactivated(UserEvent):
    user_id: UUID


class EventPublisher(Protocol):
    """Structural publisher protocol satisfied by the shared event bus."""

    def publish(self, event: object) -> None: ...
