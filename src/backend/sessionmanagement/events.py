"""Typed events for the session-management feature (docs/specs/session-management.md).

Events carry non-sensitive data only — user ids, session ids, and counts.
Raw session tokens and token hashes never appear (REQ-021, NFR-002).
"""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class _FrozenEvent(BaseModel):
    """Base for session-management events (frozen, non-sensitive)."""

    model_config = ConfigDict(frozen=True)


class SessionRevoked(_FrozenEvent):
    """Published when a single session is revoked (REQ-018)."""

    user_id: UUID
    session_id: UUID


class AllSessionsRevoked(_FrozenEvent):
    """Published when all of a user's sessions are revoked (REQ-018).

    ``excluded_session_id`` is ``None`` when nothing was excluded (all
    sessions revoked, including the caller's).
    """

    user_id: UUID
    excluded_session_id: UUID | None = None


class ExpiredSessionsDeleted(_FrozenEvent):
    """Published when expired session rows are deleted (REQ-018)."""

    count: int


class SessionsListed(_FrozenEvent):
    """Published when a session listing succeeds (REQ-018, AC-037)."""

    user_id: UUID
    count: int


class EventPublisher(Protocol):
    """Structural publisher protocol; the real event bus satisfies it."""

    def publish(self, event: object) -> None: ...
