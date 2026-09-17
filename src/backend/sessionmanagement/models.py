"""Representations for the session-management feature (docs/specs/session-management.md)."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SessionEntry(BaseModel):
    """A listed session (read-only; no tokens or token hashes, REQ-021, NFR-002).

    ``is_current`` is ``True`` for exactly the session resolved from the
    provided token (token path); on the admin (user_id) path all entries
    have ``is_current`` ``False`` (REQ-005). The device fields and
    ``login_method`` are ``None`` for rows created before the
    session-management feature (REQ-004, EDGE-006).
    """

    model_config = ConfigDict(frozen=True)

    session_id: UUID
    created_at: datetime  # UTC
    expires_at: datetime  # UTC
    is_current: bool
    user_agent: str | None = None
    ip: str | None = None
    device_name: str | None = None
    login_method: str | None = None  # "password" | "passkey" | None
