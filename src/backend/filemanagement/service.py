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
import io
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, BinaryIO, NoReturn
from uuid import UUID, uuid4

import filetype
from PIL import Image
from sqlalchemy.exc import IntegrityError

from backend.filemanagement.errors import (
    AvatarError,
    FileManagementError,
    FileManagementNotFoundError,
    FileTooLargeError,
    FileTypeNotAllowedError,
    FileValidationError,
    StorageError,
)
from backend.filemanagement.events import (
    AvatarDeleted,
    AvatarUploaded,
    EventPublisher,
    FileDeleted,
    FileDownloaded,
    FileUploaded,
    FileValidationFailed,
)
from backend.filemanagement.feature_settings import (
    DEFAULT_ALLOWED_TYPES,
    DEFAULT_AVATAR_BASE_URL,
    DEFAULT_AVATAR_MAX_SIZE,
    DEFAULT_MAX_FILE_SIZE,
    DEFAULT_STORAGE_ROOT,
)
from backend.filemanagement.models import (
    AVATAR_ALLOWED_TYPES,
    AVATAR_MAX_HEIGHT,
    AVATAR_MAX_WIDTH,
    AVATAR_VARIANT_SIZES,
    DEFAULT_AVATAR_PATH,
    KEY_PATTERN,
    NAMESPACE_PATTERN,
    AvatarRead,
    FileRead,
    FileRecord,
)
from backend.filemanagement.repository import FileRepository
from backend.filemanagement.storage import LocalDiskStorageBackend, StorageBackend
from backend.logging import logged, logged_class

if TYPE_CHECKING:
    from backend.settings import SettingsRegistry

# The built-in default avatar asset, shipped with the feature package (D9).
_DEFAULT_AVATAR_ASSET: Path = Path(__file__).resolve().parent / "assets" / "default_avatar.png"


@logged
def get_default_avatar() -> bytes:
    """The built-in default avatar asset's bytes (REQ-020, D9).

    The module function is traced via the shared logging feature (``@logged``).
    """
    return _DEFAULT_AVATAR_ASSET.read_bytes()


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
        event_bus: EventPublisher | None = None,
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
        *,
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
            key, namespace, content,
            limit=limit,
            registry=registry,
            original_filename=original_filename,
            declared_mime_type=declared_mime_type,
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

    # -- Avatar use cases -------------------------------------------------------

    def _validate_avatar_image(self, key: str, content: bytes) -> None:
        """Pillow decode + dimension validation (REQ-019, ADR-049).

        Decode validation is stricter than magic bytes: content detected as
        an image must fully decode, else
        ``FileValidationError(reason='image_decode_failed')`` (EDGE-012).
        Dimensions must be at most 4096x4096 (boundary inclusive, EDGE-018),
        else ``FileValidationError(reason='dimensions_exceeded', width, height)``.
        """
        try:
            with Image.open(io.BytesIO(content)) as img:
                img.load()
                width, height = img.size
        except Exception:
            self._validation_failure(
                key, "avatars", "image_decode_failed", FileValidationError(key, "image_decode_failed")
            )
        if width > AVATAR_MAX_WIDTH or height > AVATAR_MAX_HEIGHT:
            self._validation_failure(
                key,
                "avatars",
                "dimensions_exceeded",
                FileValidationError(key, "dimensions_exceeded", width=width, height=height),
            )

    def _generate_variants(self, key: str, content: bytes) -> list[bytes]:
        """Generate the 64px/256px PNG variants (longest side, REQ-021, D8).

        Returns the variant PNG bytes in ``AVATAR_VARIANT_SIZES`` order; a
        generation failure raises ``StorageError(reason='variant_generation')``
        (EDGE-013, INV-008).
        """
        try:
            variants: list[bytes] = []
            with Image.open(io.BytesIO(content)) as img:
                img.load()
                width, height = img.size
                longest = max(width, height)
                for size in AVATAR_VARIANT_SIZES:
                    new_size = (
                        max(1, round(width * size / longest)),
                        max(1, round(height * size / longest)),
                    )
                    resized = img.resize(new_size, Image.Resampling.LANCZOS)
                    buf = io.BytesIO()
                    resized.save(buf, format="PNG")
                    variants.append(buf.getvalue())
            return variants
        except Exception as e:
            raise StorageError(key, "variant_generation") from e

    def _store_avatar(
        self,
        source: str | bytes | BinaryIO,
        declared_mime_type: str | None,
    ) -> tuple[FileRecord, list[FileRecord]]:
        """Validate and persist a new avatar: the main file + its variants.

        Returns ``(main_record, variant_records)``. On a variant generation or
        persistence failure the entire write is rolled back (no main file, no
        variants, no records) (EDGE-013, INV-008).
        """
        registry = self._registry()
        key = str(uuid4())
        limit = self._effective_limit(registry, "avatars")
        content, original_filename = self._resolve_source(source, key, "avatars", limit, None)
        detected = self._validate_content(
            key, "avatars", content,
            limit=limit,
            registry=registry,
            original_filename=original_filename,
            declared_mime_type=declared_mime_type,
        )
        self._validate_avatar_image(key, content)

        backend = self._backend_for(registry)
        variant_contents = self._generate_variants(key, content)

        now = datetime.now(UTC)
        main_id = uuid4()
        main_record = FileRecord(
            id=main_id,
            key=key,
            original_filename=original_filename,
            declared_mime_type=declared_mime_type,
            detected_mime_type=detected,
            size=len(content),
            sha256=hashlib.sha256(content).hexdigest(),
            namespace="avatars",
            uploader=None,
            variant_of=None,
            created_at=now,
            updated_at=now,
        )
        variant_records = [
            FileRecord(
                id=uuid4(),
                key=str(uuid4()),
                original_filename=None,
                declared_mime_type=None,
                detected_mime_type="image/png",
                size=len(variant_bytes),
                sha256=hashlib.sha256(variant_bytes).hexdigest(),
                namespace="avatars",
                uploader=None,
                variant_of=main_id,
                created_at=now,
                updated_at=now,
            )
            for variant_bytes in variant_contents
        ]

        # Write content: the main file first, then the variants. A variant
        # write failure rolls back the entire write (EDGE-013).
        written: list[str] = []
        try:
            backend.put(key, content)
            written.append(key)
            for record, variant_bytes in zip(variant_records, variant_contents, strict=True):
                backend.put(record.key, variant_bytes)
                written.append(record.key)
        except StorageError as e:
            for written_key in written:
                with contextlib.suppress(Exception):
                    backend.delete(written_key)
            if key in written:
                # The main file was written: a variant write failed.
                raise StorageError(key, "variant_generation") from e
            raise  # the main write failed: propagate the backend's error

        # Persist the records with rollback of the entire write on failure.
        try:
            self._persist_record(backend, main_record)
            for record in variant_records:
                self._persist_record(backend, record)
        except StorageError:
            with contextlib.suppress(Exception):
                self._repository.delete(main_record.id)
            for record in [main_record, *variant_records]:
                with contextlib.suppress(Exception):
                    backend.delete(record.key)
            raise
        return main_record, variant_records

    def _avatar_url(self, registry: SettingsRegistry, file_id: UUID) -> str:
        """The avatar URL ``https://<base>/files/<file_id>`` (REQ-018, D7).

        ``<base>`` is the live ``filemanagement.avatar_base_url`` setting
        (host only); the ``https`` scheme is fixed.
        """
        base = str(self._read_setting(registry, "filemanagement.avatar_base_url", DEFAULT_AVATAR_BASE_URL))
        return f"https://{base}/files/{file_id}"

    def _default_avatar_read(self, user_id: str) -> AvatarRead:
        """The default avatar representation (REQ-020, D9)."""
        registry = self._registry()
        base = str(self._read_setting(registry, "filemanagement.avatar_base_url", DEFAULT_AVATAR_BASE_URL))
        return AvatarRead(
            user_id=user_id,
            url=f"https://{base}/files/{DEFAULT_AVATAR_PATH}",
            file_id=None,
            is_default=True,
            updated_at=None,
        )

    def _publish_uploaded(self, main_record: FileRecord, variant_records: list[FileRecord]) -> None:
        """``FileUploaded`` per file record created (REQ-022, AC-047)."""
        for record in [main_record, *variant_records]:
            self._publish(
                FileUploaded(
                    occurred_at=datetime.now(UTC),
                    file_id=record.id,
                    key=record.key,
                    namespace=record.namespace,
                    size=record.size,
                    detected_mime_type=record.detected_mime_type,
                    variant_of=record.variant_of,
                )
            )

    def _delete_avatar_files(self, file_id: UUID) -> None:
        """Delete the avatar file and its variants (content + records).

        Publishes ``FileDeleted`` per file record deleted (REQ-022).
        """
        backend = self._backend_for(self._registry())
        records = [
            record
            for record in self._repository.list_by_namespace("avatars")
            if file_id in (record.id, record.variant_of)
        ]
        for record in records:
            with contextlib.suppress(Exception):
                backend.delete(record.key)
            self._repository.delete(record.id)
            self._publish(
                FileDeleted(
                    occurred_at=datetime.now(UTC),
                    file_id=record.id,
                    key=record.key,
                    namespace=record.namespace,
                )
            )

    def upload_avatar(
        self,
        user_id: str,
        source: str | bytes | BinaryIO,
        *,
        declared_mime_type: str | None = None,
    ) -> AvatarRead:
        """Upload the user's first avatar (REQ-017).

        An existing avatar raises ``AvatarError(operation='upload')``.
        """
        if self._repository.get_user_avatar(user_id) is not None:
            raise AvatarError(user_id, "upload")
        main_record, variant_records = self._store_avatar(source, declared_mime_type)
        url = self._avatar_url(self._registry(), main_record.id)
        self._repository.set_user_avatar(user_id, main_record.id)
        self._publish_uploaded(main_record, variant_records)
        self._publish(AvatarUploaded(occurred_at=datetime.now(UTC), user_id=user_id, file_id=main_record.id, url=url))
        return AvatarRead(
            user_id=user_id,
            url=url,
            file_id=main_record.id,
            is_default=False,
            updated_at=main_record.updated_at,
        )

    def replace_avatar(
        self,
        user_id: str,
        source: str | bytes | BinaryIO,
        *,
        declared_mime_type: str | None = None,
    ) -> AvatarRead:
        """Replace the user's avatar (REQ-017).

        The new file is stored first; the old file and its variants are
        deleted afterwards. A missing avatar raises
        ``AvatarError(operation='replace')``.
        """
        old_file_id = self._repository.get_user_avatar(user_id)
        if old_file_id is None:
            raise AvatarError(user_id, "replace")
        main_record, variant_records = self._store_avatar(source, declared_mime_type)
        url = self._avatar_url(self._registry(), main_record.id)
        self._repository.set_user_avatar(user_id, main_record.id)
        self._publish_uploaded(main_record, variant_records)
        self._delete_avatar_files(old_file_id)
        return AvatarRead(
            user_id=user_id,
            url=url,
            file_id=main_record.id,
            is_default=False,
            updated_at=main_record.updated_at,
        )

    def delete_avatar(self, user_id: str) -> None:
        """Delete the user's avatar (REQ-017).

        The file and its variants are deleted and the user → file mapping is
        cleared; a missing avatar is a no-op (no event, no error).
        """
        file_id = self._repository.get_user_avatar(user_id)
        if file_id is None:
            return
        self._delete_avatar_files(file_id)
        self._repository.clear_user_avatar(user_id)
        self._publish(AvatarDeleted(occurred_at=datetime.now(UTC), user_id=user_id, file_id=file_id))

    def get_avatar(self, user_id: str) -> AvatarRead:
        """Return the user's avatar (REQ-017, REQ-020).

        A user without an avatar (or with a dangling mapping) gets the
        default avatar (``is_default=True``, ``file_id=None``); a dangling
        mapping is cleared (EDGE-011).
        """
        file_id = self._repository.get_user_avatar(user_id)
        record = self._repository.get_by_id(file_id) if file_id is not None else None
        if record is None:
            if file_id is not None:
                self._repository.clear_user_avatar(user_id)
            return self._default_avatar_read(user_id)
        return AvatarRead(
            user_id=user_id,
            url=self._avatar_url(self._registry(), record.id),
            file_id=record.id,
            is_default=False,
            updated_at=record.updated_at,
        )

    # -- Query use cases --------------------------------------------------------

    def download(self, key: str) -> bytes:
        """Return the stored file's bytes (REQ-010).

        A missing file (no metadata record) raises
        ``FileManagementNotFoundError``; a metadata record without storage
        content raises ``StorageError(reason='not_found')`` and the record is
        NOT auto-deleted (EDGE-006). A successful download publishes
        ``FileDownloaded`` (REQ-022). A download concurrent with a same-key
        upload returns a complete file, never partial (EDGE-017): the storage
        backends write atomically (local disk: temp file + ``os.replace``;
        in-memory: a single bytes assignment), so a concurrent read sees
        either the old or the new complete content.
        """
        record = self._repository.get_by_key(key)
        if record is None:
            raise FileManagementNotFoundError(key)
        backend = self._backend_for(self._registry())
        stream = backend.get(key)  # StorageError(reason='not_found') if content missing
        try:
            data = stream.read()
        finally:
            with contextlib.suppress(Exception):
                stream.close()
        self._publish(FileDownloaded(occurred_at=datetime.now(UTC), file_id=record.id, key=key, size=record.size))
        return data

    def open(self, key: str) -> BinaryIO:
        """Return a file-like stream of the stored file (REQ-010).

        The stream is usable as a context manager and its content equals the
        stored bytes. A missing file (no metadata record) raises
        ``FileManagementNotFoundError``; a metadata record without storage
        content raises ``StorageError(reason='not_found')`` (EDGE-006). A
        successful open publishes ``FileDownloaded`` (REQ-022).
        """
        record = self._repository.get_by_key(key)
        if record is None:
            raise FileManagementNotFoundError(key)
        backend = self._backend_for(self._registry())
        stream = backend.get(key)  # StorageError(reason='not_found') if content missing
        self._publish(FileDownloaded(occurred_at=datetime.now(UTC), file_id=record.id, key=key, size=record.size))
        return stream

    def delete(self, key: str) -> None:
        """Remove the storage content and the metadata record (REQ-011).

        A missing file (no metadata record) raises
        ``FileManagementNotFoundError``; a file whose storage content is
        already missing still has its metadata record deleted (the storage
        delete is a no-op) (EDGE-007). A successful delete publishes
        ``FileDeleted`` (REQ-022).
        """
        record = self._repository.get_by_key(key)
        if record is None:
            raise FileManagementNotFoundError(key)
        backend = self._backend_for(self._registry())
        backend.delete(key)  # no-op if the content is already missing (EDGE-007)
        self._repository.delete(record.id)
        self._publish(
            FileDeleted(
                occurred_at=datetime.now(UTC),
                file_id=record.id,
                key=key,
                namespace=record.namespace,
            )
        )

    def get_file(self, key: str) -> FileRead:
        """Return the metadata for a key (REQ-014).

        A missing file raises ``FileManagementNotFoundError``.
        """
        record = self._repository.get_by_key(key)
        if record is None:
            raise FileManagementNotFoundError(key)
        return _to_read(record)

    def list_files(
        self,
        namespace: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[FileRead]:
        """Return files whose namespace starts with the prefix (REQ-014).

        ``namespace=None`` returns all files. Results are ordered by
        created_at with limit/offset pagination. ``limit`` must be >= 1 and
        ``offset`` must be >= 0, otherwise ``ValueError``. An empty store
        returns ``[]``; an offset beyond the last item returns ``[]``
        (EDGE-008, EDGE-009).
        """
        if limit < 1:
            raise ValueError("limit must be >= 1")
        if offset < 0:
            raise ValueError("offset must be >= 0")
        records = self._repository.list_by_namespace(namespace, limit, offset)
        return [_to_read(record) for record in records]
