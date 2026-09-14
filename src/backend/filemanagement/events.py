"""Typed lifecycle events for the file-management feature (REQ-022, D10, ADR-058).

Events carry non-sensitive data only (NFR-002) — file content never appears in
an event. The service publishes them to the injected structural
:class:`EventPublisher` (the real event bus satisfies it and is injected at
wiring time; a ``None`` publisher means no events).
"""

from __future__ import annotations

from datetime import datetime
from typing import Protocol
from uuid import UUID

from pydantic import BaseModel


class FileEvent(BaseModel):
    """Base for file lifecycle events; ``occurred_at`` is UTC."""

    occurred_at: datetime


class FileUploaded(FileEvent):
    """Published per file record created (REQ-022)."""

    file_id: UUID
    key: str
    namespace: str
    size: int
    detected_mime_type: str
    variant_of: UUID | None = None


class FileDownloaded(FileEvent):
    """Published per successful download/open (REQ-022)."""

    file_id: UUID
    key: str
    size: int


class FileDeleted(FileEvent):
    """Published per file record deleted (REQ-022)."""

    file_id: UUID
    key: str
    namespace: str


class FileValidationFailed(FileEvent):
    """Published per validation failure, before the domain error is raised (REQ-022).

    ``reason`` is a short, secret-free string (e.g. ``"zero_byte_file"``,
    ``"file_too_large"``, ``"type_not_allowed"``, ``"type_conflict"``,
    ``"invalid_key"``, ``"invalid_namespace"``, ``"source_not_found"``,
    ``"source_not_a_file"``, ``"image_decode_failed"``, ``"dimensions_exceeded"``).
    """

    key: str | None
    namespace: str | None
    reason: str


class AvatarEvent(FileEvent):
    """Base for avatar lifecycle events."""

    user_id: str


class AvatarUploaded(AvatarEvent):
    """Published when a user uploads a new avatar via `upload_avatar` (not on `replace_avatar`) (REQ-022)."""

    file_id: UUID
    url: str


class AvatarDeleted(AvatarEvent):
    """Published when a user's avatar is deleted (REQ-022)."""

    file_id: UUID


class EventPublisher(Protocol):
    """Structural publisher protocol (ADR-058); the real event bus satisfies it."""

    def publish(self, event: object) -> None: ...
