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
    return datetime.now(UTC)


class AuthEvent(BaseModel):
    """Base class for all authentication lifecycle events (``occurred_at`` is UTC)."""

    occurred_at: datetime = Field(default_factory=_utcnow)


class LoginSucceeded(AuthEvent):
    user_id: UUID
    method: str  # "password" | "passkey"


class LoginFailed(AuthEvent):
    identifier: str  # the identifier as attempted (username/email or credential id)
    method: str  # "password" | "passkey"


class Logout(AuthEvent):
    user_id: UUID


class PasswordResetRequested(AuthEvent):
    email: str


class PasswordResetCompleted(AuthEvent):
    user_id: UUID


class PasskeyRegistered(AuthEvent):
    user_id: UUID
    credential_id: str


class PasskeyDeleted(AuthEvent):
    user_id: UUID
    credential_id: str
