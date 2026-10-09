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
    """The single clock source for event timestamps (tz-aware UTC)."""
    return datetime.now(UTC)


class UserEvent(BaseModel):
    """Base class for all user lifecycle events (``occurred_at`` is UTC)."""

    occurred_at: datetime = Field(default_factory=_utcnow)


class UserCreated(UserEvent):
    """Published once after a successful ``create_user`` (REQ-016, AC-030).

    Carries the stored username, the lowercased email, and the complete role
    list — never the password or its hash (REQ-017).
    """

    user_id: UUID
    username: str
    email: str
    roles: list[str]  # was: role: str


class UserUpdated(UserEvent):
    """Published after a non-empty update (AC-031).

    ``changed_fields`` lists exactly the fields that were written, so an
    update that changed nothing publishes no event (REQ-017).
    """

    user_id: UUID
    changed_fields: list[str]


class UserDeleted(UserEvent):
    """Published after the hard delete (AC-032).

    ``username`` is carried because the id is no longer resolvable once the
    row is gone.
    """

    user_id: UUID
    username: str


class UserPasswordChanged(UserEvent):
    """Published after a re-hash (AC-033).

    The id is the whole payload: no password, no hash (REQ-017).
    """

    user_id: UUID


class UserRoleChanged(UserEvent):
    """Published after a role assignment (user-roles-permissions AC-037).

    ``old_roles``/``new_roles`` are the complete role lists before and after,
    not a single role (user-roles-permissions REQ-026).
    """

    user_id: UUID
    old_roles: list[str]  # was: old_role: str
    new_roles: list[str]  # was: new_role: str


class UserActivated(UserEvent):
    """Published on an actual inactive-to-active transition (AC-035).

    Activating an already active user is a no-op and publishes nothing
    (REQ-017).
    """

    user_id: UUID


class UserDeactivated(UserEvent):
    """Published on an actual active-to-inactive transition (AC-036).

    Deactivating the last active admin raises before this event can be
    published (REQ-008).
    """

    user_id: UUID


class EventPublisher(Protocol):
    """Structural publisher protocol satisfied by the shared event bus."""

    def publish(self, event: object) -> None:
        """Accept one event from a producing feature.

        Nothing is caught here: a publisher that raises propagates to the
        caller after the mutation has already been committed (EDGE-020).
        """
        ...
