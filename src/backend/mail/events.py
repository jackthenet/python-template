"""Typed lifecycle events (docs/specs/mail-service.md, D9).

``EmailSent``/``EmailFailed`` are frozen Pydantic models carrying non-sensitive
data only: no email body, no rendered subject, no token, and no SMTP password
(REQ-013, NFR-002).
"""

from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field


class MailEvent(BaseModel):
    """Base class for mail lifecycle events."""

    model_config = ConfigDict(frozen=True)

    occurred_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class EmailSent(MailEvent):
    """A successful send (non-sensitive data only)."""

    to: str
    template: str


class EmailFailed(MailEvent):
    """A failed send (non-sensitive data only).

    ``reason`` is the error kind: ``"template"``, ``"configuration"``, or
    ``"transport"``.
    """

    to: str
    template: str
    reason: str
