"""Shared helpers for the file-management test suite.

The suite exercises the feature's public API (docs/specs/file-management.md).
The helpers import the feature's public API from ``backend.filemanagement``
at module level, so while the feature is unimplemented every file-management
test fails at collection with ``ModuleNotFoundError: backend.filemanagement``
— the expected RED state for a new FEATURE (see
``docs/verification/file-management.md``).
"""

from __future__ import annotations

import io
import tempfile
from collections.abc import Sequence
from pathlib import Path
from typing import BinaryIO
from uuid import UUID

from pydantic import BaseModel

from backend.filemanagement import (
    FileRecord,
    FileService,
    InMemoryStorageBackend,
    StorageBackend,
    StorageError,
    StorageStat,
    register_settings,
)
from backend.settings import SettingsRegistry, YamlValueRepository

# --- Deterministic magic-byte content factories --------------------------------


def text_bytes(n: int = 1024) -> bytes:
    """Plain ASCII content; magic-byte detection reports ``text/plain``."""
    return b"x" * n


def pdf_bytes() -> bytes:
    """Minimal PDF content; magic-byte detection reports ``application/pdf``."""
    return b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\ntrailer\n<< /Size 1 >>\n%%EOF\n"


def jpeg_bytes() -> bytes:
    """Minimal JFIF content (SOI + APP0 + EOI); detected as ``image/jpeg``."""
    app0 = b"\xff\xe0" + (16).to_bytes(2, "big") + b"JFIF\x00\x01\x01\x00\x00\x01\x00\x00\x01\x00"
    return b"\xff\xd8" + app0 + b"\xff\xd9"


def gif_bytes() -> bytes:
    """Minimal GIF89a content; magic-byte detection reports ``image/gif``."""
    return b"GIF89a" + (16).to_bytes(2, "little") + (16).to_bytes(2, "little") + b"\x00\x00\x00;"


def tiff_bytes() -> bytes:
    """Minimal little-endian TIFF header; detected as ``image/tiff``.

    ``image/tiff`` is not in the default allowed set (AC-011).
    """
    return b"II\x2a\x00" + (8).to_bytes(2, "little") + b"\x00" * 16


def png_bytes(width: int = 8, height: int = 8) -> bytes:
    """A real, decodable PNG via Pillow (avatar content and variants)."""
    from PIL import Image

    buf = io.BytesIO()
    Image.new("RGB", (width, height), (120, 90, 200)).save(buf, format="PNG")
    return buf.getvalue()


def webp_bytes(width: int = 8, height: int = 8) -> bytes:
    """A real, decodable WebP via Pillow."""
    from PIL import Image

    buf = io.BytesIO()
    Image.new("RGBA", (width, height), (120, 90, 200, 255)).save(buf, format="WEBP")
    return buf.getvalue()


def truncated_png() -> bytes:
    """PNG magic bytes plus a partial IHDR chunk.

    Magic-byte detection reports ``image/png``, but Pillow cannot decode the
    content (AC-041, EDGE-012).
    """
    return b"\x89PNG\r\n\x1a\n" + b"IHDR" + (13).to_bytes(4, "big") + b"\x00\x00"


# --- Wiring helpers -------------------------------------------------------------


class EventCollector:
    """A synchronous structural ``EventPublisher`` that records every event."""

    def __init__(self) -> None:
        self.events: list[BaseModel] = []

    def publish(self, event: object) -> None:
        self.events.append(event)

    def of_type(self, event_type: type) -> list[BaseModel]:
        """The recorded events that are instances of ``event_type``."""
        return [e for e in self.events if isinstance(e, event_type)]


def db_url(tmp_path: Path, name: str = "files.db") -> str:
    """A cross-platform absolute SQLite file URL under ``tmp_path``.

    POSIX absolute paths need four slashes (``sqlite:////abs``); Windows
    paths (``C:/...``) are already absolute and use three.
    """
    p = str(tmp_path / name).replace("\\", "/")
    prefix = "sqlite:////" if p.startswith("/") else "sqlite:///"
    return f"{prefix}{p}"


def isolated_registry() -> SettingsRegistry:
    """A fresh settings registry backed by a temp-dir value repository.

    No value is ever persisted to the shared ``settings/`` directory and
    nothing written by one test leaks into another (test isolation).
    """
    return SettingsRegistry(value_repository=YamlValueRepository(tempfile.mkdtemp()))


def make_service(
    repository: object,
    backend: StorageBackend | None = None,
    event_bus: object | None = None,
    registry: SettingsRegistry | None = None,
    register: bool = True,
) -> FileService:
    """Build a ``FileService`` with the given wiring.

    By default the feature's settings are registered on the registry and a
    public in-memory backend is used; pass ``register=False`` to exercise the
    hardcoded defaults (AC-053).
    """
    reg = registry if registry is not None else isolated_registry()
    if register:
        register_settings(reg)
    return FileService(
        repository,
        backend=backend if backend is not None else InMemoryStorageBackend(),
        event_bus=event_bus,
        settings_registry=reg,
    )


# --- Fault-injection doubles ------------------------------------------------------


class FailingPutBackend:
    """A ``StorageBackend`` whose ``put`` always fails (AC-016, INV-001)."""

    def __init__(self) -> None:
        self.put_attempts = 0
        self.put_keys: list[str] = []

    def put(self, key: str, data: bytes | BinaryIO) -> None:
        self.put_attempts += 1
        self.put_keys.append(key)
        raise StorageError(key=key, reason="io")

    def get(self, key: str) -> BinaryIO:
        raise StorageError(key=key, reason="not_found")

    def delete(self, key: str) -> None:
        return None

    def exists(self, key: str) -> bool:
        return False

    def stat(self, key: str) -> StorageStat | None:
        return None


class FailingAddRepository:
    """A ``FileRepository`` fake whose ``add`` always fails (AC-017, INV-001)."""

    def __init__(self) -> None:
        self.add_attempts = 0

    def add(self, record: FileRecord) -> FileRecord:
        self.add_attempts += 1
        raise RuntimeError("injected metadata failure")

    def get_by_key(self, key: str) -> FileRecord | None:
        return None

    def get_by_id(self, file_id: UUID) -> FileRecord | None:
        return None

    def update(self, record: FileRecord) -> FileRecord:
        return record

    def delete(self, file_id: UUID) -> None:
        return None

    def list_by_namespace(
        self, namespace: str | None = None, limit: int = 100, offset: int = 0
    ) -> Sequence[FileRecord]:
        return []

    def set_user_avatar(self, user_id: str, file_id: UUID) -> None:
        return None

    def get_user_avatar(self, user_id: str) -> UUID | None:
        return None

    def clear_user_avatar(self, user_id: str) -> None:
        return None


def _is_variant_png(content: bytes) -> bool:
    """True when ``content`` is a decodable PNG whose longest side is 64 or 256."""
    from PIL import Image

    try:
        with Image.open(io.BytesIO(content)) as img:
            return img.format == "PNG" and max(img.size) in (64, 256)
    except Exception:
        return False


class FailingVariantBackend:
    """A ``StorageBackend`` that fails only when writing avatar variants (EDGE-013).

    Delegates to an ``InMemoryStorageBackend``; ``put`` raises
    ``StorageError(reason="variant_generation")`` when the content decodes as
    a PNG whose longest side is one of the avatar variant sizes (64 or 256).
    """

    def __init__(self) -> None:
        self.inner = InMemoryStorageBackend()
        self.put_keys: list[str] = []

    def put(self, key: str, data: bytes | BinaryIO) -> None:
        self.put_keys.append(key)
        if isinstance(data, (bytes, bytearray, memoryview)) and _is_variant_png(bytes(data)):
            raise StorageError(key=key, reason="variant_generation")
        self.inner.put(key, data)

    def get(self, key: str) -> BinaryIO:
        return self.inner.get(key)

    def delete(self, key: str) -> None:
        self.inner.delete(key)

    def exists(self, key: str) -> bool:
        return self.inner.exists(key)

    def stat(self, key: str) -> StorageStat | None:
        return self.inner.stat(key)


class RaisingPublisher:
    """A structural ``EventPublisher`` that raises on ``publish`` (EDGE-014)."""

    def __init__(self) -> None:
        self.events: list[object] = []

    def publish(self, event: object) -> None:
        self.events.append(event)
        raise RuntimeError("injected publisher failure")


class DictFileRepository:
    """A plain in-memory ``FileRepository`` implementation (AC-026).

    The service depends only on the ``FileRepository`` ABC; this fake proves
    no SQLite/SQLModel detail leaks into the service.
    """

    def __init__(self) -> None:
        self._records: dict[str, FileRecord] = {}
        self._avatars: dict[str, UUID] = {}

    def add(self, record: FileRecord) -> FileRecord:
        self._records[record.key] = record
        return record

    def get_by_key(self, key: str) -> FileRecord | None:
        return self._records.get(key)

    def get_by_id(self, file_id: UUID) -> FileRecord | None:
        for r in self._records.values():
            if r.id == file_id:
                return r
        return None

    def update(self, record: FileRecord) -> FileRecord:
        self._records[record.key] = record
        return record

    def delete(self, file_id: UUID) -> None:
        for key, r in list(self._records.items()):
            if r.id == file_id:
                del self._records[key]

    def list_by_namespace(
        self, namespace: str | None = None, limit: int = 100, offset: int = 0
    ) -> Sequence[FileRecord]:
        rows = [
            r
            for r in sorted(self._records.values(), key=lambda r: r.created_at)
            if namespace is None or r.namespace.startswith(namespace)
        ]
        return rows[offset : offset + limit]

    def set_user_avatar(self, user_id: str, file_id: UUID) -> None:
        self._avatars[user_id] = file_id

    def get_user_avatar(self, user_id: str) -> UUID | None:
        return self._avatars.get(user_id)

    def clear_user_avatar(self, user_id: str) -> None:
        self._avatars.pop(user_id, None)
