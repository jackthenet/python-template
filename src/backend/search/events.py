"""Typed lifecycle/failure events for the search feature (D15, REQ-014).

Events carry non-sensitive data only (source names, reasons) — never query
text, result content, or source data (NFR-002). There is NO per-query event.
"""

from __future__ import annotations

from typing import Protocol

from pydantic import BaseModel


class SourceRegistered(BaseModel):
    """A source was registered or replaced (D15)."""

    source: str


class SourceUnregistered(BaseModel):
    """A source was removed (D15)."""

    source: str


class SourceQueryFailed(BaseModel):
    """A source query failed (``query_failed``/``timeout``) (D15)."""

    source: str
    reason: str


class EventPublisher(Protocol):
    """Structural publisher protocol (the real event bus satisfies it; a
    ``None`` publisher means no events and no error, REQ-014)."""

    def publish(self, event: object) -> None: ...
