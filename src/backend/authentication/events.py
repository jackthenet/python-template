"""Typed lifecycle events for authentication (REQ-020).

Events carry non-sensitive data only (D13): no password, no raw token, no
hash. Each successful operation publishes exactly one event; failures and
no-ops publish none.
"""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from pydantic import BaseModel, Field


def _utcnow() -> datetime:
    """The single event timestamp source (timezone-aware UTC, read at construction)."""
    return datetime.now(UTC)


class AuthEvent(BaseModel):
    """Base class for all authentication lifecycle events (``occurred_at`` is UTC)."""

    occurred_at: datetime = Field(default_factory=_utcnow)


class LoginSucceeded(AuthEvent):
    """Published once per accepted login (REQ-020/AC-031), whichever method was used."""

    user_id: UUID
    method: str  # "password" | "passkey"


class LoginFailed(AuthEvent):
    """Published for every rejected password login (REQ-020/AC-032).

    The passkey login path publishes none of its failures, so a ``LoginFailed``
    record always has ``method="password"``.
    """

    identifier: str  # the identifier as attempted (username/email or credential id)
    method: str  # "password" | "passkey"


class Logout(AuthEvent):
    """Published when ``logout`` revokes a live session; the idempotent no-op path publishes nothing (AC-014)."""

    user_id: UUID


class PasswordResetRequested(AuthEvent):
    """Published for every reset request, registered email or not (EDGE-007).

    Carries the lower-cased address and never the token, so the event stream does
    not reveal whether the address exists (REQ-010).
    """

    email: str


class PasswordResetCompleted(AuthEvent):
    """Published after the password is changed and the user's sessions revoked (REQ-012)."""

    user_id: UUID


class PasskeyRegistered(AuthEvent):
    """Published once a credential row is stored (REQ-014); the public key is never carried."""

    user_id: UUID
    credential_id: str


class PasskeyDeleted(AuthEvent):
    """Published after a credential is deleted (REQ-017); a rejected deletion publishes nothing."""

    user_id: UUID
    credential_id: str
