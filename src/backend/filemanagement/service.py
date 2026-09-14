"""File management service (REQ-001..REQ-009, REQ-012, REQ-015, REQ-022).

``FileService`` implements the upload use case: input shapes (filesystem
path, raw bytes, or file-like binary stream), key/namespace validation, the
live size-limit and allowed-type policy, magic-byte content-type detection,
an atomic write with mutual rollback between the storage content and the
metadata record, and the upload lifecycle events.

The service references only the ``FileRepository`` and ``StorageBackend``
ABCs (D1, REQ-013, REQ-015) — both are swappable.
"""

from __future__ import annotations

import contextlib
import hashlib
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, BinaryIO, NoReturn
from uuid import uuid4

import filetype
from sqlalchemy.exc import IntegrityError

from backend.filemanagement.errors import (
    FileManagementError,
    FileTooLargeError,
    FileTypeNotAllowedError,
    FileValidationError,
    StorageError,
)
from backend.filemanagement.events import FileUploaded, FileValidationFailed
from backend.filemanagement.feature_settings import (
    DEFAULT_ALLOWED_TYPES,
    DEFAULT_AVATAR_MAX_SIZE,
    DEFAULT_MAX_FILE_SIZE,
    DEFAULT_STORAGE_ROOT,
)
from backend.filemanagement.models import (
    AVATAR_ALLOWED_TYPES,
    KEY_PATTERN,
    NAMESPACE_PATTERN,
    FileRead,
    FileRecord,
)
from backend.filemanagement.repository import FileRepository
from backend.filemanagement.storage import LocalDiskStorageBackend, StorageBackend
from backend.logging import logged_class

if TYPE_CHECKING:
    from backend.settings import SettingsRegistry

_CHUNK_SIZE: int = 65536

# Bounded attempts for the metadata record add: a concurrent same-key
# replacement can race the repository's atomic replacement (unique-key
# IntegrityError); retrying keeps last-write-wins error-free (ADR-054).
_ADD_ATTEMPTS: int = 5

# Filename extension → MIME type for the filename-signal conflict check
# (REQ-005). Only extensions with an unambiguous mapping are listed; an
# unknown extension implies no signal.
_EXTENSION_MIME: dict[str, str] = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".webp": "image/webp",
    ".txt": "text/plain",
    ".csv": "text/csv",
    ".pdf": "application/pdf",
    ".zip": "application/zip",
    ".tif": "image/tiff",
    ".tiff": "image/tiff",
}


def _detect_mime_type(data: bytes) -> str:
    """Magic-byte detection (source of truth). filetype detects binary types;
    text fallback: text content -> text/plain, unidentified binary ->
    application/octet-stream. Preserves the spec's behavior."""
    mime = filetype.guess_mime(data)
    if mime is not None:
        return mime
    if b"\x00" not in data[:8192]:
        return "text/plain"
    return "application/octet-stream"


def _mime_from_filename(filename: str | None) -> str | None:
    """The MIME type implied by ``filename``'s extension, or ``None``."""
    if filename is None:
        return None
    dot = filename.rfind(".")
    if dot <= 0:
        return None
    return _EXTENSION_MIME.get(filename[dot:].lower())


def _to_read(record: FileRecord) -> FileRead:
    """The read-only representation of ``record``."""
    return FileRead(
        id=record.id,
        key=record.key,
        original_filename=record.original_filename,
        declared_mime_type=record.declared_mime_type,
        detected_mime_type=record.detected_mime_type,
        size=record.size,
        sha256=record.sha256,
        namespace=record.namespace,
        uploader=record.uploader,
        variant_of=record.variant_of,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


@logged_class(slow_threshold_ms=5000, include_args=False)
class FileService:
    """Use-case service for file uploads (REQ-001..REQ-009, REQ-012, REQ-022).

    The class is traced via the shared logging feature (``@logged_class``
    with ``include_args=False`` so file content never appears in log
    records, REQ-025, NFR-002).
    """

    def __init__(
        self,
        repository: FileRepository,
        backend: StorageBackend | None = None,
        event_bus: object | None = None,
        settings_registry: SettingsRegistry | None = None,
    ) -> None:
        self._repository = repository
        self._backend = backend
        self._event_bus = event_bus
        self._settings_registry = settings_registry

    # -- Wiring helpers -------------------------------------------------------

    def _registry(self) -> SettingsRegistry:
        """The settings registry: the injected one, or the shared singleton."""
        if self._settings_registry is not None:
            return self._settings_registry
        from backend.settings import get_settings_registry

        return get_settings_registry()

    def _read_setting(self, registry: SettingsRegistry, key: str, fallback: Any) -> Any:
        """The live value of ``key``, or ``fallback`` when unregistered."""
        if registry.has(key):
            return registry.get_value(key)
        return fallback

    def _effective_limit(self, registry: SettingsRegistry, namespace: str) -> int:
        """The effective max size for ``namespace``, read live (REQ-003)."""
        if namespace == "avatars":
            return int(self._read_setting(registry, "filemanagement.avatar_max_size", DEFAULT_AVATAR_MAX_SIZE))
        return int(self._read_setting(registry, "filemanagement.max_file_size", DEFAULT_MAX_FILE_SIZE))

    def _allowed_types(self, registry: SettingsRegistry, namespace: str) -> frozenset[str]:
        """The effective allowed-type set for ``namespace`` (REQ-006)."""
        if namespace == "avatars":
            return AVATAR_ALLOWED_TYPES
        return frozenset(self._read_setting(registry, "filemanagement.allowed_types", DEFAULT_ALLOWED_TYPES))

    def _backend_for(self, registry: SettingsRegistry) -> StorageBackend:
        """The storage backend: the injected one, or local disk from the live
        ``filemanagement.storage_root`` setting (constructed per operation)."""
        if self._backend is not None:
            return self._backend
        root = self._read_setting(registry, "filemanagement.storage_root", DEFAULT_STORAGE_ROOT)
        return LocalDiskStorageBackend(Path(root))

    def _publish(self, event: object) -> None:
        """Publish ``event``; a ``None`` publisher means no events and no error."""
        if self._event_bus is not None:
            self._event_bus.publish(event)

    def _validation_failure(self, key: str, namespace: str, reason: str, error: FileManagementError) -> NoReturn:
        """Publish ``FileValidationFailed`` and raise ``error`` (REQ-022)."""
        self._publish(FileValidationFailed(occurred_at=datetime.now(UTC), key=key, namespace=namespace, reason=reason))
        raise error

    def _read_stream(self, source: BinaryIO, key: str, namespace: str, limit: int) -> bytes:
        """Fully consume ``source``; abort mid-stream once the limit is exceeded."""
        chunks: list[bytes] = []
        total = 0
        while True:
            chunk = source.read(_CHUNK_SIZE)
            if not chunk:
                break
            total += len(chunk)
            if total > limit:
                self._validation_failure(key, namespace, "file_too_large", FileTooLargeError(key, total, limit))
            chunks.append(chunk)
        return b"".join(chunks)

    def _persist_record(self, backend: StorageBackend, record: FileRecord) -> None:
        """Persist ``record`` with the mutual-rollback guarantee (REQ-008).

        A concurrent same-key replacement can race the repository's atomic
        replacement (unique-key ``IntegrityError``); the add is retried so the
        upload still commits — last-write-wins, no error (ADR-054). When the
        record cannot be persisted, the written content is rolled back.
        """
        for attempt in range(_ADD_ATTEMPTS):
            try:
                self._repository.add(record)
                return
            except IntegrityError:
                if attempt + 1 >= _ADD_ATTEMPTS:
                    break
            except Exception as e:
                with contextlib.suppress(Exception):
                    backend.delete(record.key)
                raise StorageError(record.key, "io") from e
        with contextlib.suppress(Exception):
            backend.delete(record.key)
        raise StorageError(record.key, "io")

    def _resolve_source(
        self,
        source: str | bytes | BinaryIO,
        key: str,
        namespace: str,
        limit: int,
        original_filename: str | None,
    ) -> tuple[bytes, str | None]:
        """Read ``source``'s content (input shapes, REQ-002).

        Returns ``(content, original_filename)``; a path source defaults
        ``original_filename`` to the path's basename.
        """
        if isinstance(source, str):
            path = Path(source)
            if not path.exists():
                self._validation_failure(
                    key, namespace, "source_not_found", FileValidationError(key, "source_not_found")
                )
            if not path.is_file():
                self._validation_failure(
                    key, namespace, "source_not_a_file", FileValidationError(key, "source_not_a_file")
                )
            if original_filename is None:
                original_filename = path.name
            return path.read_bytes(), original_filename
        if isinstance(source, (bytes, bytearray, memoryview)):
            return bytes(source), original_filename
        return self._read_stream(source, key, namespace, limit), original_filename

    def _validate_content(
        self,
        key: str,
        namespace: str,
        content: bytes,
        limit: int,
        registry: SettingsRegistry,
        original_filename: str | None,
        declared_mime_type: str | None,
    ) -> str:
        """Size and type validation (REQ-003..REQ-006); returns the detected type.

        The effective limit is enforced (size == limit is allowed, EDGE-019);
        magic-byte detection is the source of truth and conflicting signals
        (declared MIME, filename extension) are rejected, not overwritten.
        """
        if len(content) == 0:
            self._validation_failure(key, namespace, "zero_byte_file", FileValidationError(key, "zero_byte_file"))
        if len(content) > limit:
            self._validation_failure(key, namespace, "file_too_large", FileTooLargeError(key, len(content), limit))
        detected = _detect_mime_type(content)
        if declared_mime_type is not None and declared_mime_type != detected:
            self._validation_failure(
                key,
                namespace,
                "type_conflict",
                FileValidationError(key, "type_conflict", declared=declared_mime_type, detected=detected),
            )
        filename_mime = _mime_from_filename(original_filename)
        if filename_mime is not None and filename_mime != detected:
            self._validation_failure(
                key,
                namespace,
                "type_conflict",
                FileValidationError(key, "type_conflict", declared=filename_mime, detected=detected),
            )
        allowed = self._allowed_types(registry, namespace)
        if detected not in allowed:
            self._validation_failure(
                key, namespace, "type_not_allowed", FileTypeNotAllowedError(key, detected, allowed)
            )
        return detected

    # -- Use case ---------------------------------------------------------------

    def upload(
        self,
        source: str | bytes | BinaryIO,
        *,
        key: str | None = None,
        namespace: str = "general",
        original_filename: str | None = None,
        declared_mime_type: str | None = None,
        uploader: str | None = None,
    ) -> FileRead:
        """Upload ``source`` (a filesystem path, raw bytes, or a file-like
        binary stream) and return the stored file's ``FileRead``.

        Validation: key/namespace patterns, zero-byte, the live size limit,
        magic-byte type detection, declared/filename type conflicts, and the
        live allowed-type set. The write is atomic with mutual rollback
        between the storage content and the metadata record (REQ-008).
        """
        registry = self._registry()

        # Key (REQ-007): generated when not given; must match KEY_PATTERN.
        if key is None:
            key = str(uuid4())
        if re.match(KEY_PATTERN, key) is None:
            self._validation_failure(key, namespace, "invalid_key", FileValidationError(key, "invalid_key"))

        # Namespace: must match NAMESPACE_PATTERN.
        if re.match(NAMESPACE_PATTERN, namespace) is None:
            self._validation_failure(key, namespace, "invalid_namespace", FileValidationError(key, "invalid_namespace"))

        limit = self._effective_limit(registry, namespace)
        content, original_filename = self._resolve_source(source, key, namespace, limit, original_filename)
        detected = self._validate_content(
            key, namespace, content, limit, registry, original_filename, declared_mime_type
        )

        # Atomic write with mutual rollback (REQ-008, ADR-053).
        backend = self._backend_for(registry)
        backend.put(key, content)
        now = datetime.now(UTC)
        record = FileRecord(
            id=uuid4(),
            key=key,
            original_filename=original_filename,
            declared_mime_type=declared_mime_type,
            detected_mime_type=detected,
            size=len(content),
            sha256=hashlib.sha256(content).hexdigest(),
            namespace=namespace,
            uploader=uploader,
            variant_of=None,
            created_at=now,
            updated_at=now,
        )
        self._persist_record(backend, record)

        # Success event (REQ-022); a raising publisher propagates after the
        # operation is committed (EDGE-014).
        self._publish(
            FileUploaded(
                occurred_at=datetime.now(UTC),
                file_id=record.id,
                key=key,
                namespace=namespace,
                size=len(content),
                detected_mime_type=detected,
                variant_of=None,
            )
        )
        return _to_read(record)
