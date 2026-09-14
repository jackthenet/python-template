"""Domain models and fixed constants for the file-management feature.

``FileRecord`` and ``UserAvatar`` are the SQLModel table models (persistence,
REQ-012, REQ-013). ``FileRead`` and ``AvatarRead`` are the read-only
representations returned by the service (spec §3). ``StorageStat`` describes a
storage content's size and updated time. The constants are fixed (NOT
configurable) (REQ-012, REQ-019, REQ-020).
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel
from sqlmodel import Field as SField
from sqlmodel import SQLModel


class FileRecord(SQLModel, table=True):
    """A stored file's metadata (REQ-012).

    ``sha256`` is required and is 64 lowercase hex chars; all timestamps are
    UTC.
    """

    __tablename__ = "files"

    id: UUID = SField(default_factory=uuid4, primary_key=True)
    key: str = SField(index=True, unique=True)
    original_filename: str | None = None
    declared_mime_type: str | None = None
    detected_mime_type: str
    size: int
    sha256: str
    namespace: str = SField(index=True)
    uploader: str | None = None
    variant_of: UUID | None = None
    created_at: datetime
    updated_at: datetime


class UserAvatar(SQLModel, table=True):
    """The user → file mapping for a user's current avatar (D6)."""

    __tablename__ = "user_avatars"

    user_id: str = SField(primary_key=True)
    file_id: UUID = SField(foreign_key="files.id")
    updated_at: datetime


class FileRead(BaseModel):
    """Read-only representation of a file (the only representation returned by the service)."""

    id: UUID
    key: str
    original_filename: str | None
    declared_mime_type: str | None
    detected_mime_type: str
    size: int
    sha256: str
    namespace: str
    uploader: str | None
    variant_of: UUID | None
    created_at: datetime
    updated_at: datetime


class AvatarRead(BaseModel):
    """Read-only representation of a user's avatar (spec §3)."""

    user_id: str
    url: str
    file_id: UUID | None
    is_default: bool
    updated_at: datetime | None


class StorageStat(BaseModel):
    """A storage content's size and updated time (UTC)."""

    size: int
    updated_at: datetime


# --- Fixed constants (NOT configurable) ---

AVATAR_VARIANT_SIZES: tuple[int, ...] = (64, 256)
AVATAR_MAX_WIDTH: int = 4096
AVATAR_MAX_HEIGHT: int = 4096
AVATAR_ALLOWED_TYPES: frozenset[str] = frozenset({"image/png", "image/jpeg", "image/webp"})
DEFAULT_AVATAR_PATH: str = "default-avatar"
KEY_PATTERN: str = r"^[A-Za-z0-9][A-Za-z0-9._-]{0,254}$"
NAMESPACE_PATTERN: str = r"^[a-z0-9][a-z0-9._-]{0,63}$"
