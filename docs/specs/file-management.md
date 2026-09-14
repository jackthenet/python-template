# Spec: File Management (Backend)

## Changelog
- v2 (2026-09-14): AC-035 amended — `replace_avatar` publishes NO `AvatarUploaded` (only `upload_avatar` does); `replace_avatar` publishes `FileUploaded` (new main+variants) + `FileDeleted` (old main+variants). Resolves the spec-wording vs. re-derived-test conflict (test wins per the Spec Drift rule).

## 1. Overview & Objectives
- **Feature Name:** File Management (Backend)
- **Target Component:** `src/backend/filemanagement/`
- **Goal:** Provide a backend service for storing user files — upload, download, delete, query — with size and type validation, atomic writes (no partial state), per-user avatars (variants + stable URL), content-hash metadata, and pluggable storage and metadata backends, so that application code and other features have a single, safe place to store user files.
- **Scope:** In-process Python service (no HTTP layer); flat opaque keys (object-store style); upload from an existing filesystem path, raw bytes, or a file-like binary stream; size validation (zero-byte files rejected; live-configurable max sizes — 10 MB general, 2 MB avatar defaults); magic-byte type detection (python-magic) as the source of truth, with conflicting declared/filename signals rejected; per-namespace allowed-type policy (live-configurable global default; avatars: images only); file metadata (id, key, original filename, declared + detected MIME, size, SHA-256 content hash, namespace, uploader reference, variant reference, created/updated timestamps) persisted in SQLite/SQLModel behind a `FileRepository` ABC; a `StorageBackend` ABC (local-disk default with root `./data/files`, public in-memory backend for tests/DI); atomic upload (temp file + atomic rename; metadata record and storage write rolled back against each other); last-write-wins for concurrent same-key uploads; per-user avatars (upload/replace/delete) with image/png, image/jpeg, image/webp types, max 4096×4096 dimensions verified by Pillow decode, a built-in default avatar, and 64px/256px PNG variants stored as separate files; avatar URL `https://<base>/files/<file_id>` with a live-configurable base URL (always `https`, satisfying user-management's `profile_picture_url` validation without a spec amendment); lookup by key + list by namespace prefix with limit/offset pagination; typed lifecycle events (`FileUploaded`, `FileDownloaded`, `FileDeleted`, `FileValidationFailed`, `AvatarUploaded`, `AvatarDeleted`) published to an injected event publisher (non-sensitive data only); a `FileManagementError` exception hierarchy with context attributes; live-configurable limits via the shared settings feature; observability via the shared logging feature.
- **Out of Scope:** HTTP/REST/GraphQL API layer; frontend UI; virus scanning; content deduplication; file versioning; retention/expiration (auto-cleanup); sharing/permission grants; S3 or other cloud storage backends (can be added later behind the `StorageBackend` interface); range/partial download; folders/directories (the store is flat); updating user-management user records (the caller's responsibility — this feature does not depend on user-management and does not subscribe to `UserDeleted`); avatar cleanup on user deletion (the caller's responsibility); centralizing other features' persistence (each feature keeps its own SQLite/YAML persistence — the common `./data/` root is a layout convention only, REQ-026); database migration/upgrade framework (bootstrap via `create_all` only); multi-tenancy.
- **Edge cases:** (folded into section 7) invalid keys (path traversal, null bytes, absolute paths); symlinks inside the storage root; zero-byte files; oversized files (path/bytes/stream, including mid-stream); type conflicts (declared MIME type or filename extension vs. detected type); types not in the allowed set; undecodable avatar images; oversized avatar dimensions; a missing source path; a directory as the source; a metadata record without storage content; a dangling avatar mapping; variant generation failure; concurrent same-key upload/download/delete; a publisher that raises.

## 2. Architecture & Design Decisions
- **Design Pattern:** Service + repository + storage backend. `FileService` (use cases, validation, domain rules) depends only on the `FileRepository` ABC (SQLite/SQLModel default) and the `StorageBackend` ABC (local-disk default, public in-memory backend for tests/DI). The service publishes typed lifecycle events to an injected `EventPublisher` (structural protocol; the real event bus is injected at wiring time). Limits, the storage root, and the avatar base URL are read live from the shared settings feature on each operation.
- **Dependencies:** `python-magic` (magic-byte type detection — NEW dependency; record in a Phase 2 ADR), `Pillow` (image decode validation + variant generation — NEW dependency; record in a Phase 2 ADR), `sqlmodel` (pulls in `sqlalchemy`; metadata persistence — existing project dependency), `pydantic` (request/representation models — existing project dependency); uses `backend.settings` (feature-owned `register_settings` + live-read pattern), `backend.logging` (`@logged`, `@logged_class`), and the structural `EventPublisher` protocol (the real event bus is injected at wiring time, consistent with user-management and authentication). No web framework. No import of `backend.usermanagement` (no cross-feature dependency — the caller owns the user record). No import of `backend.eventbus` (the event integration is a structural protocol, so this feature does not hard-depend on the event-bus feature's source).
- **Constraints:** In-process only (no HTTP/REST layer). File content never appears in log records, events, or error messages. The service code references only the `FileRepository` and `StorageBackend` ABCs (both must be swappable later). Keys and namespaces are validated against the key/namespace patterns (no path separators, no null bytes, no traversal). The local backend enforces path containment within the root and rejects symlinks (nothing escapes the storage root). This feature does NOT update user-management user records and does NOT subscribe to `UserDeleted` — the caller sets the avatar URL on the user record and cleans up the avatar on user deletion. The built-in default avatar image ships with the feature package.
- **Design Decisions (WHAT; WHY goes to ADRs in Phase 2):**
  - D1: Service + repository + backend — `FileService` depends on the `FileRepository` ABC (`SqliteFileRepository` default) and the `StorageBackend` ABC (`LocalDiskStorageBackend` default, `InMemoryStorageBackend` public for tests/DI); constructor injection.
  - D2: Flat opaque keys (object-store style) — no folders/directories in the public API; a "namespace" is a logical metadata field (e.g., `general`, `avatars`), not a real directory.
  - D3: Magic-byte type detection (python-magic) on the content is the source of truth for a file's type; conflicting signals (a declared MIME type, or an original-filename extension that implies a different MIME type) are rejected, not silently overwritten.
  - D4: Atomic upload — content is written to a temp file and atomically renamed at the storage level; the metadata record and the storage write are rolled back against each other (a failed upload leaves no partial state).
  - D5: Last-write-wins for concurrent same-key uploads — atomic replacement; exactly one winner, no error.
  - D6: Avatars are per-user files in the `avatars` namespace, tracked in a user → file mapping (`UserAvatar` table); the caller owns the user record (no user-management dependency, no `UserDeleted` subscription).
  - D7: Avatar URL format `https://<base>/files/<file_id>` — `<base>` from the live `filemanagement.avatar_base_url` setting; the `https` scheme is fixed, so the URL always satisfies user-management's `profile_picture_url` validation without a spec amendment.
  - D8: Image processing — avatars are validated by Pillow decode (≤ 4096×4096); 64px/256px PNG variants (longest side) are generated and stored as separate files with a `variant_of` reference; variants are deleted with the original. The "main file" of an avatar is the file the caller uploaded (as opposed to its variants).
  - D9: A built-in default avatar image ships with the feature package (an asset); `get_avatar` returns it (`is_default=True`, `file_id=None`) when the user has no avatar; the module function `get_default_avatar()` exposes the asset's bytes.
  - D10: Typed lifecycle events (`FileUploaded`, `FileDownloaded`, `FileDeleted`, `FileValidationFailed`, `AvatarUploaded`, `AvatarDeleted`) are published to the injected `EventPublisher` after each operation; a `None` publisher means no events; events carry non-sensitive data only.
  - D11: Error hierarchy — `FileManagementError` (root) + `FileManagementNotFoundError`, `FileTooLargeError`, `FileTypeNotAllowedError`, `FileValidationError`, `StorageError`, `AvatarError`, with context attributes. A "validation failure" is an upload rejected by size, type, key, namespace, source, or image validation; it publishes `FileValidationFailed` and raises the corresponding domain error.
  - D12: Settings — the feature-owned `register_settings(registry)` registers the feature's settings via `register_feature("filemanagement", [...])` (the settings key format forbids hyphens, so the registration name is `filemanagement`; the change/feature name remains `file-management`); all settings are read live on each operation; unregistered keys fall back to hardcoded defaults; repository/backend injection stays constructor args.
  - D13: Security — the key/namespace patterns reject path separators, null bytes, and traversal; the local backend verifies path containment within the root and rejects symlinks (nothing escapes the storage root).
  - D14: Layout convention — a common persistence root `./data/`: user files live under `./data/files/` (the default storage root) and each feature's own persistence lives in its own subdirectory; a normative layout convention, not a code dependency.

## 3. Data Structures & API Schemas

```python
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from io import BinaryIO
from pathlib import Path
from typing import Protocol, Sequence
from uuid import UUID, uuid4

from pydantic import BaseModel
from sqlmodel import SQLModel, Field as SField

# --- Table models (persistence) ---

class FileRecord(SQLModel, table=True):
    __tablename__ = "files"
    id: UUID = SField(default_factory=uuid4, primary_key=True)
    key: str = SField(index=True, unique=True)          # flat opaque key (D2)
    original_filename: str | None = None
    declared_mime_type: str | None = None
    detected_mime_type: str                             # magic-byte detection (D3)
    size: int                                           # bytes
    sha256: str                                         # 64 lowercase hex chars; required (REQ-012)
    namespace: str = SField(index=True)                 # logical (D2); e.g., "general", "avatars"
    uploader: str | None = None                         # opaque reference to who uploaded
    variant_of: UUID | None = None                      # for variant files: the id of the main file (D8)
    created_at: datetime                                # UTC
    updated_at: datetime                                # UTC

class UserAvatar(SQLModel, table=True):
    __tablename__ = "user_avatars"
    user_id: str = SField(primary_key=True)             # opaque user reference (D6)
    file_id: UUID = SField(foreign_key="files.id")      # the main file of the user's current avatar
    updated_at: datetime                                # UTC
```

```python
# --- Read-only representations (the only representations returned by the service) ---

class FileRead(BaseModel):
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
    user_id: str
    url: str                      # https://<base>/files/<file_id>, or the default avatar URL
    file_id: UUID | None          # None when the default avatar is returned
    is_default: bool
    updated_at: datetime | None   # None for the default avatar

# --- Fixed constants (NOT configurable) ---

AVATAR_VARIANT_SIZES: tuple[int, ...] = (64, 256)   # longest side, px (D8)
AVATAR_MAX_WIDTH: int = 4096
AVATAR_MAX_HEIGHT: int = 4096
AVATAR_ALLOWED_TYPES: frozenset[str] = frozenset({"image/png", "image/jpeg", "image/webp"})
DEFAULT_AVATAR_PATH: str = "default-avatar"          # path segment of the default avatar URL
KEY_PATTERN: str = r"^[A-Za-z0-9][A-Za-z0-9._-]{0,254}$"
NAMESPACE_PATTERN: str = r"^[a-z0-9][a-z0-9._-]{0,63}$"
```

```python
# --- Storage backend (D1, D13) ---

class StorageStat(BaseModel):
    size: int
    updated_at: datetime

class StorageBackend(ABC):
    @abstractmethod
    def put(self, key: str, data: bytes | BinaryIO) -> None: ...
    # Atomically write the content to key (replacing any existing content — last-write-wins, D5).
    # Raise StorageError on failure (reason: "io", "symlink", "path_escape").
    @abstractmethod
    def get(self, key: str) -> BinaryIO: ...
    # Return a file-like stream of the content at key.
    # Raise StorageError(reason="not_found") if the key is absent.
    @abstractmethod
    def delete(self, key: str) -> None: ...
    # Delete the content at key. No-op if the key is absent.
    @abstractmethod
    def exists(self, key: str) -> bool: ...
    @abstractmethod
    def stat(self, key: str) -> StorageStat | None: ...
    # Return the content's size/updated time, or None if the key is absent.

class LocalDiskStorageBackend(StorageBackend):
    def __init__(self, root: Path) -> None: ...
    # Flat layout: one file per key directly under root (the key is the filename).
    # Enforces the key pattern, path containment within root, and symlink rejection (D13):
    # a key violating KEY_PATTERN, a path that resolves outside root, or a symlink at the
    # target path or any path component → StorageError (reason: "path_escape" / "symlink").
    # put: write to a temp file in root, then os.replace (atomic rename, D4).

class InMemoryStorageBackend(StorageBackend):
    def __init__(self) -> None: ...
    # A dict of key → bytes; public for tests/DI; instances are isolated (no shared state).
```

```python
# --- Metadata repository (D1) ---

class FileRepository(ABC):
    @abstractmethod
    def add(self, record: FileRecord) -> FileRecord: ...
    # Insert the record. If a record with the same key exists, it is atomically replaced
    # (last-write-wins, D5); the replaced record is deleted.
    @abstractmethod
    def get_by_key(self, key: str) -> FileRecord | None: ...
    @abstractmethod
    def get_by_id(self, file_id: UUID) -> FileRecord | None: ...
    @abstractmethod
    def update(self, record: FileRecord) -> FileRecord: ...
    @abstractmethod
    def delete(self, file_id: UUID) -> None: ...
    @abstractmethod
    def list_by_namespace(
        self, namespace: str | None = None, limit: int = 100, offset: int = 0
    ) -> Sequence[FileRecord]: ...
    # Return records whose namespace starts with `namespace` (None → all),
    # ordered by created_at, with limit/offset pagination.
    # Avatar mapping (D6)
    @abstractmethod
    def set_user_avatar(self, user_id: str, file_id: UUID) -> None: ...
    @abstractmethod
    def get_user_avatar(self, user_id: str) -> UUID | None: ...
    @abstractmethod
    def clear_user_avatar(self, user_id: str) -> None: ...

class SqliteFileRepository(FileRepository):
    def __init__(self, database_url: str) -> None: ...
    # Creates the DB file's parent directory and all tables (no migration framework).
```

```python
# --- Service (D1) ---

class FileService:
    def __init__(
        self,
        repository: FileRepository,
        backend: StorageBackend | None = None,
        event_bus: EventPublisher | None = None,
        settings_registry: SettingsRegistry | None = None,
    ) -> None: ...
    # repository: the metadata repository (SqliteFileRepository is the default concrete implementation)
    # backend: None → a LocalDiskStorageBackend constructed from the live
    #   filemanagement.storage_root setting on each operation (default ./data/files, D14)
    # event_bus: the structural EventPublisher; None → no events, no error
    # settings_registry: None → the shared get_settings_registry();
    #   unregistered keys fall back to the hardcoded defaults (D12)
    # General files
    def upload(
        self,
        source: str | bytes | BinaryIO,
        *,
        key: str | None = None,
        namespace: str = "general",
        original_filename: str | None = None,
        declared_mime_type: str | None = None,
        uploader: str | None = None,
    ) -> FileRead: ...
    # source: an existing filesystem path (str), raw bytes, or a file-like binary stream
    # key: None → the service generates a canonical UUID key; a caller key must match KEY_PATTERN
    # namespace: must match NAMESPACE_PATTERN ("general" for general uploads)
    # original_filename: when source is a path and original_filename is not given,
    #   it defaults to the path's basename
    # Avatars (namespace "avatars")
    def upload_avatar(
        self, user_id: str, source: str | bytes | BinaryIO, *, declared_mime_type: str | None = None
    ) -> AvatarRead: ...
    def replace_avatar(
        self, user_id: str, source: str | bytes | BinaryIO, *, declared_mime_type: str | None = None
    ) -> AvatarRead: ...
    def delete_avatar(self, user_id: str) -> None: ...
    def get_avatar(self, user_id: str) -> AvatarRead: ...
    # Queries
    def download(self, key: str) -> bytes: ...
    def open(self, key: str) -> BinaryIO: ...
    def delete(self, key: str) -> None: ...
    def get_file(self, key: str) -> FileRead: ...
    def list_files(
        self, namespace: str | None = None, limit: int = 100, offset: int = 0
    ) -> list[FileRead]: ...
    # limit must be >= 1, offset must be >= 0 (otherwise ValueError)

def get_default_avatar() -> bytes: ...
# Return the bytes of the built-in default avatar image (D9); traced with @logged.
```

```python
# --- Lifecycle events (typed; D10) ---

class FileEvent(BaseModel):
    occurred_at: datetime                     # UTC

class FileUploaded(FileEvent):
    file_id: UUID
    key: str
    namespace: str
    size: int
    detected_mime_type: str
    variant_of: UUID | None = None

class FileDownloaded(FileEvent):
    file_id: UUID
    key: str
    size: int

class FileDeleted(FileEvent):
    file_id: UUID
    key: str
    namespace: str

class FileValidationFailed(FileEvent):
    key: str | None
    namespace: str | None
    reason: str        # "zero_byte_file" | "file_too_large" | "type_not_allowed"
                       # | "type_conflict" | "invalid_key" | "invalid_namespace"
                       # | "source_not_found" | "source_not_a_file"
                       # | "image_decode_failed" | "dimensions_exceeded"

class AvatarEvent(FileEvent):
    user_id: str

class AvatarUploaded(AvatarEvent):
    file_id: UUID
    url: str

class AvatarDeleted(AvatarEvent):
    file_id: UUID

# --- Publisher protocol (structural; the real EventBus satisfies it) ---

class EventPublisher(Protocol):
    def publish(self, event: object) -> None: ...
```

```python
# --- Errors (D11) ---

class FileManagementError(Exception): ...

class FileManagementNotFoundError(FileManagementError):
    key: str

class FileTooLargeError(FileManagementError):
    key: str | None
    size: int                      # actual size, bytes
    limit: int                     # effective max size, bytes

class FileTypeNotAllowedError(FileManagementError):
    key: str | None
    detected: str                  # the detected MIME type
    allowed: frozenset[str]        # the effective allowed set

class FileValidationError(FileManagementError):
    key: str | None
    reason: str                    # "zero_byte_file" | "type_conflict" | "invalid_key"
                                   # | "invalid_namespace" | "source_not_found"
                                   # | "source_not_a_file" | "image_decode_failed"
                                   # | "dimensions_exceeded"
    declared: str | None = None    # type_conflict: the declared MIME type
    detected: str | None = None    # type_conflict: the detected MIME type
    width: int | None = None       # dimensions_exceeded
    height: int | None = None      # dimensions_exceeded

class StorageError(FileManagementError):
    key: str | None
    reason: str                    # "not_found" | "io" | "symlink"
                                   # | "path_escape" | "variant_generation"

class AvatarError(FileManagementError):
    user_id: str
    operation: str                 # "upload" | "replace"
```

### 3.1 Feature settings (registered via `register_settings`)

The feature-owned `register_settings(registry)` (in `feature_settings.py`) registers the feature's settings with the settings registry via `registry.register_feature("filemanagement", [...])` (no import side effects, consistent with the other features; category `application`, group `filemanagement`). The registration name is `filemanagement` (no hyphen) because the settings key format `^[a-zA-Z_][a-zA-Z0-9_]*(\.[a-zA-Z_][a-zA-Z0-9_]*)*$` forbids hyphens (D12). Each setting is read live on each operation (REQ-024).

| Key | Kind | Default |
|-----|------|---------|
| `filemanagement.storage_root` | TEXT | `"./data/files"` |
| `filemanagement.max_file_size` | NUMBER | `10485760` (10 MB, bytes) |
| `filemanagement.avatar_max_size` | NUMBER | `2097152` (2 MB, bytes) |
| `filemanagement.allowed_types` | LIST | `["application/octet-stream", "application/pdf", "application/zip", "text/plain", "text/csv", "image/png", "image/jpeg", "image/gif", "image/webp"]` |
| `filemanagement.avatar_base_url` | TEXT | `"files.example.com"` |

The `avatar_base_url` value is the host only (no scheme); the avatar URL is constructed as `https://<avatar_base_url>/files/<file_id>` (D7), so the scheme is always `https`.

**Package layout:**

```text
src/backend/filemanagement/
├── __init__.py    # re-exports the public API
├── models.py      # FileRecord, UserAvatar, FileRead, AvatarRead, constants
├── events.py      # FileEvent + lifecycle events, EventPublisher
├── errors.py      # exception hierarchy
├── storage.py     # StorageBackend, LocalDiskStorageBackend, InMemoryStorageBackend
├── repository.py  # FileRepository, SqliteFileRepository
├── feature_settings.py  # register_settings
├── service.py     # FileService, get_default_avatar
└── assets/default_avatar.png  # the built-in default avatar (D9)
```

**Public API** (the NFR-003 backward-compatibility contract): `FileRecord`, `UserAvatar`, `FileRead`, `AvatarRead`, `StorageStat`, `StorageBackend`, `LocalDiskStorageBackend`, `InMemoryStorageBackend`, `FileRepository`, `SqliteFileRepository`, `FileService`, `FileEvent`, `FileUploaded`, `FileDownloaded`, `FileDeleted`, `FileValidationFailed`, `AvatarEvent`, `AvatarUploaded`, `AvatarDeleted`, `EventPublisher`, `FileManagementError`, `FileManagementNotFoundError`, `FileTooLargeError`, `FileTypeNotAllowedError`, `FileValidationError`, `StorageError`, `AvatarError`, `register_settings`, `get_default_avatar`, `AVATAR_VARIANT_SIZES`, `AVATAR_MAX_WIDTH`, `AVATAR_MAX_HEIGHT`, `AVATAR_ALLOWED_TYPES`, `DEFAULT_AVATAR_PATH`, `KEY_PATTERN`, `NAMESPACE_PATTERN`.

## 4. Requirements

Each normative requirement MUST have a stable ID. These IDs propagate through the lifecycle:
`REQ-001 → AC-001 → test → task → implementation`.

| ID | Requirement |
|----|-------------|
| REQ-001 | The feature provides an in-process file storage service for user files (no HTTP/REST layer), exposed via `FileService`; any in-process caller may use it (open in-process access, consistent with the existing features). |
| REQ-002 | `upload` accepts three input shapes: an existing filesystem path (`str`), raw bytes, and a file-like binary stream; when the source is a path and `original_filename` is not given, it defaults to the path's basename. |
| REQ-003 | Upload size validation: zero-byte content is rejected (`FileValidationError`, reason `zero_byte_file`); content larger than the effective max size is rejected with `FileTooLargeError` (actual size and limit as context). The effective max size is the `filemanagement.avatar_max_size` setting for the `avatars` namespace and the `filemanagement.max_file_size` setting for all other namespaces, read live on each operation. |
| REQ-004 | A file's type is determined by magic-byte detection (python-magic) on the content; the detected MIME type is the source of truth and is recorded in the metadata. |
| REQ-005 | Conflicting type signals are rejected (`FileValidationError`, reason `type_conflict`): a declared MIME type that differs from the detected type, or an original-filename extension that implies a different MIME type than the detected type. |
| REQ-006 | Allowed-type policy: the detected MIME type must be in the effective allowed set, else `FileTypeNotAllowedError` (detected type and allowed set as context). The effective allowed set is the fixed avatar set {image/png, image/jpeg, image/webp} for the `avatars` namespace and the `filemanagement.allowed_types` setting (live-configurable global default) for all other namespaces. |
| REQ-007 | Keys are flat and opaque (object-store style; no folders): a caller-specified key must match `KEY_PATTERN` (no path separators, no null bytes, no traversal), else `FileValidationError` (reason `invalid_key`); when no key is given, the service generates a canonical UUID key. Namespaces are logical (metadata field, not a directory) and must match `NAMESPACE_PATTERN`, else `FileValidationError` (reason `invalid_namespace`). |
| REQ-008 | Atomicity: a failed or interrupted upload leaves no partial state — content is written to a temp file and atomically renamed at the storage level; if the storage write fails, no metadata record is created, and if the metadata record cannot be created, the storage content is deleted (rollback against each other). |
| REQ-009 | Concurrent uploads to the same key are last-write-wins: atomic replacement, exactly one winner, no error; the final state is exactly one file record and one storage content for the key. |
| REQ-010 | Download: `download(key)` returns the file's bytes and `open(key)` returns a file-like stream; access is open to any in-process caller; a missing file raises `FileManagementNotFoundError`. |
| REQ-011 | Delete: `delete(key)` removes the storage content and the metadata record; a missing file raises `FileManagementNotFoundError`. |
| REQ-012 | File metadata carries the normative field set: id, key, original filename, declared MIME type, detected MIME type, size (bytes), SHA-256 content hash (required; 64 lowercase hex chars), namespace, uploader reference, variant reference, and created/updated timestamps (UTC). |
| REQ-013 | Metadata persistence: SQLite/SQLModel behind the `FileRepository` ABC (like user-management); the service depends only on the ABC, so the database can be changed later; `SqliteFileRepository` is the default concrete repository. |
| REQ-014 | Query API: `get_file(key)` returns the metadata for a key (`FileManagementNotFoundError` when missing); `list_files(namespace, limit, offset)` returns files whose namespace starts with the given prefix (None → all), with limit/offset pagination (`limit >= 1`, `offset >= 0`, else `ValueError`). |
| REQ-015 | Storage abstraction: the `StorageBackend` ABC (put/get/delete/exists/stat) with a local-disk implementation (`LocalDiskStorageBackend`, default root `./data/files` from the live `filemanagement.storage_root` setting) and a public in-memory implementation (`InMemoryStorageBackend`) for tests/DI; the backend is a constructor arg (None → local disk from the live setting). |
| REQ-016 | Security: nothing can escape the storage root — keys are rejected before they reach the storage (no `../`, no absolute paths, no null bytes, via `KEY_PATTERN`), and the local backend verifies path containment within the root and rejects symlinks (`StorageError`, reason `symlink`/`path_escape`). |
| REQ-017 | Avatar lifecycle: `upload_avatar(user_id, source)` creates the user's first avatar; `replace_avatar(user_id, source)` stores the new file, returns the new URL, and deletes the old file (and its variants); `delete_avatar(user_id)` deletes the file (and its variants) and clears the mapping — the caller clears the URL on the user record. `upload_avatar` on an existing avatar and `replace_avatar` on a missing avatar raise `AvatarError`; `delete_avatar` on a missing avatar is a no-op. |
| REQ-018 | Avatar URL: an avatar's URL is `https://<base>/files/<file_id>` with `<base>` from the live `filemanagement.avatar_base_url` setting; the `https` scheme is fixed, so the URL always satisfies user-management's `profile_picture_url` validation without a spec amendment. |
| REQ-019 | Avatar constraints: allowed types are image/png, image/jpeg, image/webp; content must be decodable as an image by Pillow (`FileValidationError`, reason `image_decode_failed` otherwise) and must be at most 4096×4096 dimensions (`FileValidationError`, reason `dimensions_exceeded` otherwise). |
| REQ-020 | Default avatar: the feature ships a built-in default avatar image (an asset of the feature package); `get_avatar(user_id)` returns it (`is_default=True`, `file_id=None`, URL `https://<base>/files/default-avatar`) when the user has no avatar; `get_default_avatar()` returns the asset's bytes. |
| REQ-021 | Image processing: a successful avatar upload/replace generates 64px and 256px variants (longest side, PNG) stored as separate files (separate keys, `variant_of` reference to the main file) with their own metadata records; variants are deleted with the main file. |
| REQ-022 | Events: the service publishes `FileUploaded` (per file record created), `FileDownloaded` (per successful download/open), `FileDeleted` (per file record deleted), `FileValidationFailed` (per validation failure, before the domain error is raised), `AvatarUploaded`, and `AvatarDeleted` to the injected event publisher; events carry non-sensitive data only; a `None` publisher means no events and no error; no other event is published on failure. |
| REQ-023 | Structured domain errors: an exception hierarchy rooted at `FileManagementError` (`FileManagementNotFoundError`, `FileTooLargeError`, `FileTypeNotAllowedError`, `FileValidationError`, `StorageError`, `AvatarError`) with documented context attributes (key; actual vs. limit/allowed; reason). |
| REQ-024 | Settings: the feature-owned `register_settings(registry)` registers the feature's settings (`filemanagement.storage_root`, `filemanagement.max_file_size`, `filemanagement.avatar_max_size`, `filemanagement.allowed_types`, `filemanagement.avatar_base_url`) via `register_feature("filemanagement", [...])`; all settings are read live on each operation; unregistered keys fall back to the hardcoded defaults; repository/backend injection stays constructor args. |
| REQ-025 | Observability: `FileService` is traced with `@logged_class` (sensible `slow_threshold_ms`), the module-level functions (`register_settings`, `get_default_avatar`) with `@logged`, `include_args=False` where arguments are sensitive (file content, paths); file content never appears in log records. |
| REQ-026 | Layout convention: a common persistence root `./data/` — user files live under `./data/files/` (the default storage root) and each feature's own persistence lives in its own subdirectory; this is a normative layout convention, not a code dependency (each feature keeps its own persistence). |

## 5. Acceptance Criteria

Each acceptance criterion MUST have a stable ID and MUST reference at least one requirement. Use Given/When/Then format.

| ID | References | Criterion |
|----|------------|-----------|
| AC-001 | REQ-001, REQ-002 | **Given** a `FileService` with working repository and backend and 1 KiB of valid content, **When** `upload(source)` is called, **Then** a `FileRead` is returned with `size == 1024`, the detected MIME type, a 64-character `sha256`, namespace `general`, and a generated key, **And** the file is retrievable via `get_file(key)`. |
| AC-002 | REQ-002 | **Given** an existing file on disk, **When** `upload(<path>)` is called, **Then** a `FileRead` is returned with `size` equal to the file's size on disk, **And** `original_filename` equals the path's basename. |
| AC-003 | REQ-002 | **Given** a file-like binary stream of N bytes, **When** `upload(stream)` is called, **Then** a `FileRead` is returned with `size == N`, **And** the stream is fully consumed. |
| AC-004 | REQ-003 | **Given** zero-byte content (any input shape), **When** `upload` is called, **Then** a `FileValidationError` is raised with reason `zero_byte_file`, **And** `FileValidationFailed` is published, **And** no file record and no storage content are created. |
| AC-005 | REQ-003 | **Given** content larger than the effective max size in a non-avatar namespace (default 10 MB), **When** `upload` is called, **Then** a `FileTooLargeError` is raised with `size` (actual) and `limit` (effective max size), **And** `FileValidationFailed` is published, **And** no partial state is left. |
| AC-006 | REQ-003 | **Given** content larger than the `filemanagement.avatar_max_size` setting (default 2 MB) in the `avatars` namespace, **When** `upload` is called, **Then** a `FileTooLargeError` is raised with `limit` equal to the avatar limit. |
| AC-007 | REQ-003 | **Given** a settings registry with `filemanagement.max_file_size` changed to a smaller value, **When** `upload` is called with content exceeding the new limit, **Then** the new limit is enforced (live read). |
| AC-008 | REQ-004 | **Given** JPEG content, **When** `upload` is called, **Then** `FileRead.detected_mime_type == "image/jpeg"` (magic-byte detection on the content). |
| AC-009 | REQ-005 | **Given** PNG content with `declared_mime_type="image/jpeg"`, **When** `upload` is called, **Then** a `FileValidationError` is raised with reason `type_conflict` (declared vs. detected), **And** `FileValidationFailed` is published. |
| AC-010 | REQ-005 | **Given** JPEG content with `original_filename="photo.png"`, **When** `upload` is called, **Then** a `FileValidationError` is raised with reason `type_conflict` (the filename extension implies `image/png`, differing from the detected `image/jpeg`), **And** `FileValidationFailed` is published. |
| AC-011 | REQ-006 | **Given** content whose detected MIME type is not in the effective allowed set, **When** `upload` is called in a non-avatar namespace, **Then** a `FileTypeNotAllowedError` is raised with `detected` and `allowed`, **And** `FileValidationFailed` is published. |
| AC-012 | REQ-006 | **Given** a settings registry with `filemanagement.allowed_types` changed, **When** `upload` is called with content whose detected type is in the new list, **Then** it succeeds (live read). |
| AC-013 | REQ-007 | **Given** `upload` without a key, **When** `upload` is called, **Then** `FileRead.key` is a canonical UUID string. |
| AC-014 | REQ-007 | **Given** a caller-specified key `report-2026.pdf`, **When** `upload` is called, **Then** the file is stored under that key. |
| AC-015 | REQ-007 | **Given** a caller-specified key containing a path separator (e.g., `a/b`), **When** `upload` is called, **Then** a `FileValidationError` is raised with reason `invalid_key`, **And** `FileValidationFailed` is published, **And** nothing is stored. |
| AC-016 | REQ-008 | **Given** a backend that fails on `put` (injected fault), **When** `upload` is called, **Then** a `StorageError` is raised, **And** no metadata record is created, **And** no storage content (or temp file) remains. |
| AC-017 | REQ-008 | **Given** a repository that fails on `add` (injected fault), **When** `upload` is called, **Then** a `StorageError` is raised (reason `io`), **And** the storage content written by the upload is deleted (rollback). |
| AC-018 | REQ-009 | **Given** two threads uploading different content to the same key concurrently, **When** both complete, **Then** no error is raised, **And** exactly one file record exists for the key, **And** its content equals one of the two uploads (last-write-wins). |
| AC-019 | REQ-010 | **Given** a stored file, **When** `download(key)` is called, **Then** the original bytes are returned, **And** `FileDownloaded` is published. |
| AC-020 | REQ-010 | **Given** a stored file, **When** `open(key)` is called, **Then** a file-like stream is returned whose content equals the stored bytes (usable as a context manager), **And** `FileDownloaded` is published. |
| AC-021 | REQ-010 | **Given** an unknown key, **When** `download(key)` or `open(key)` is called, **Then** a `FileManagementNotFoundError` is raised. |
| AC-022 | REQ-011 | **Given** a stored file, **When** `delete(key)` is called, **Then** the storage content and the metadata record are removed, **And** `FileDeleted` is published, **And** a subsequent `get_file(key)` raises `FileManagementNotFoundError`. |
| AC-023 | REQ-011 | **Given** an unknown key, **When** `delete(key)` is called, **Then** a `FileManagementNotFoundError` is raised. |
| AC-024 | REQ-012 | **Given** a successful upload, **When** the metadata record is read via the repository, **Then** all normative fields are present and correct: id, key, original filename, declared MIME type, detected MIME type, size, sha256 (64 lowercase hex chars), namespace, uploader, variant reference, created/updated timestamps (UTC). |
| AC-025 | REQ-013 | **Given** a file created via `SqliteFileRepository("sqlite:///<tmp>/files.db")`, **When** a new repository + service instance is constructed on the same file, **Then** the file is visible (persistence across instances). |
| AC-026 | REQ-013 | **Given** a service constructed with a non-SQLite `FileRepository` implementation (a test fake), **When** all operations are invoked, **Then** they work (the service depends only on the ABC). |
| AC-027 | REQ-014 | **Given** stored files in multiple namespaces, **When** `get_file(key)` is called, **Then** a `FileRead` is returned, **And** `list_files(namespace="avatars", limit=10, offset=0)` returns only files whose namespace starts with `avatars` (at most 10), **And** `list_files(namespace="avatars", limit=10, offset=5)` skips the first 5. |
| AC-028 | REQ-014 | **Given** `list_files` with `limit=0` or a negative `offset`, **When** it is called, **Then** a `ValueError` is raised. |
| AC-029 | REQ-015 | **Given** the default wiring (no backend), **When** operations are performed, **Then** a `LocalDiskStorageBackend` is used with the live `filemanagement.storage_root` setting (default `./data/files`). |
| AC-030 | REQ-015 | **Given** a service constructed with `InMemoryStorageBackend()`, **When** upload/download/delete are called, **Then** they work (the public in-memory backend). |
| AC-031 | REQ-016 | **Given** a local backend whose storage root contains a symlink at the target key path, **When** `put`/`get` is attempted, **Then** a `StorageError` is raised with reason `symlink`, **And** the symlink is not followed. |
| AC-032 | REQ-016 | **Given** a local backend, **When** a key would resolve outside the root (defense in depth), **Then** a `StorageError` is raised with reason `path_escape`, **And** nothing is written outside the root. |
| AC-033 | REQ-017 | **Given** a user without an avatar and valid avatar content, **When** `upload_avatar(user_id, source)` is called, **Then** an `AvatarRead` is returned with `is_default=False`, `file_id` set, and a URL matching the avatar URL format, **And** `get_avatar(user_id)` returns the same avatar, **And** `AvatarUploaded` is published. |
| AC-034 | REQ-017 | **Given** a user with an existing avatar, **When** `upload_avatar` is called, **Then** an `AvatarError` is raised with `operation == "upload"` (use `replace_avatar`). |
| AC-035 | REQ-017 | **Given** a user with an existing avatar, **When** `replace_avatar(user_id, new_source)` is called, **Then** an `AvatarRead` is returned with the new URL, **And** the old file (and its variants) are deleted, **And** `get_avatar` returns the new avatar, **And** `FileUploaded` events are published for the new main file and each variant, **And** `FileDeleted` events are published for the old main file and each variant, **And** no `AvatarUploaded` event is published (only `upload_avatar` publishes `AvatarUploaded`). |
| AC-036 | REQ-017 | **Given** a user without an avatar, **When** `replace_avatar` is called, **Then** an `AvatarError` is raised with `operation == "replace"` (use `upload_avatar`). |
| AC-037 | REQ-017 | **Given** a user with an avatar, **When** `delete_avatar(user_id)` is called, **Then** the file (and its variants) are deleted, **And** the mapping is cleared, **And** `AvatarDeleted` is published, **And** `get_avatar` returns the default avatar. |
| AC-038 | REQ-017 | **Given** a user without an avatar, **When** `delete_avatar` is called, **Then** it is a no-op (no event, no error). |
| AC-039 | REQ-018 | **Given** the default `filemanagement.avatar_base_url` (`files.example.com`), **When** an avatar is uploaded, **Then** the returned URL matches `https://files.example.com/files/<canonical UUID>` and starts with `https://` (satisfying user-management's `profile_picture_url` validation). |
| AC-040 | REQ-018 | **Given** a settings registry with `filemanagement.avatar_base_url` changed, **When** an avatar is uploaded, **Then** the new base is used in the URL (live read). |
| AC-041 | REQ-019 | **Given** avatar content that is not decodable as an image, **When** `upload_avatar` is called, **Then** a `FileValidationError` is raised with reason `image_decode_failed`, **And** `FileValidationFailed` is published. |
| AC-042 | REQ-019 | **Given** avatar content with dimensions 5000×5000, **When** `upload_avatar` is called, **Then** a `FileValidationError` is raised with reason `dimensions_exceeded` (width/height context), **And** `FileValidationFailed` is published. |
| AC-043 | REQ-019 | **Given** avatar content of type `image/gif`, **When** `upload_avatar` is called, **Then** a `FileTypeNotAllowedError` is raised (avatars allow only image/png, image/jpeg, image/webp). |
| AC-044 | REQ-020 | **Given** a user without an avatar, **When** `get_avatar(user_id)` is called, **Then** an `AvatarRead` is returned with `is_default=True`, `file_id=None`, and the default avatar URL (`https://<base>/files/default-avatar`). |
| AC-045 | REQ-021 | **Given** a successful `upload_avatar`, **When** the store is inspected, **Then** two variant files exist (`variant_of` equal to the main file's id), stored as PNG with longest side 64px and 256px, **And** each variant has a metadata record (sha256, detected type `image/png`, namespace `avatars`). |
| AC-046 | REQ-021 | **Given** a successful `replace_avatar`, **When** the store is inspected, **Then** the old main file and its variants are deleted, **And** the new main file and its two variants exist. |
| AC-047 | REQ-022 | **Given** a collector publisher, **When** a general upload succeeds, **Then** a `FileUploaded` event is published (file_id, key, namespace, size, detected_mime_type), **And** when an avatar upload succeeds, **Then** `FileUploaded` events are published for the main file and each variant, plus an `AvatarUploaded` event. |
| AC-048 | REQ-022 | **Given** a collector, **When** `download` succeeds, **Then** a `FileDownloaded` event is published, **And** when `delete` succeeds, **Then** a `FileDeleted` event is published. |
| AC-049 | REQ-022 | **Given** a collector, **When** an upload is rejected by validation, **Then** a `FileValidationFailed` event is published (key, namespace, reason) before the domain error is raised. |
| AC-050 | REQ-022 | **Given** a service without a publisher, **When** operations succeed, **Then** they work normally (no events, no errors). |
| AC-051 | REQ-023 | **Given** a domain error, **When** it is caught, **Then** it is a `FileManagementError` subclass carrying the documented context (`FileManagementNotFoundError.key`, `FileTooLargeError.size`/`.limit`, `FileTypeNotAllowedError.detected`/`.allowed`, `FileValidationError.reason`, `StorageError.key`/`.reason`, `AvatarError.user_id`/`.operation`). |
| AC-052 | REQ-024 | **Given** a settings registry, **When** `register_settings(registry)` is called, **Then** the feature's settings are registered: `filemanagement.storage_root`, `filemanagement.max_file_size`, `filemanagement.avatar_max_size`, `filemanagement.allowed_types`, `filemanagement.avatar_base_url`. |
| AC-053 | REQ-024 | **Given** a service whose settings registry has none of the feature's keys registered, **When** operations are performed, **Then** the hardcoded defaults are used (`./data/files`, 10 MB, 2 MB, the default allowed types, `files.example.com`). |
| AC-054 | REQ-025 | **Given** the shared logging feature configured at the default level, **When** service methods are invoked, **Then** entry/exit tracing occurs via `@logged_class`, **And** file content never appears in log records. |
| AC-055 | REQ-026 | **Given** the default settings, **When** the local backend is constructed, **Then** its root is `./data/files` (under the common persistence root `./data/`), **And** user files are stored there. |

## 6. Invariants

State invariants that hold over a large input space. These become Hypothesis property-based tests.

| ID | Invariant |
|----|-----------|
| INV-001 | For any upload (any input shape, any failure point — validation, storage, metadata): a failed or interrupted upload leaves no partial state — no temp file, no orphaned storage content, no orphaned metadata record. |
| INV-002 | For any concurrent uploads to the same key: after all complete, no error is raised, exactly one file record exists for the key, and its content equals one of the uploads (last-write-wins). |
| INV-003 | For any stored file: the metadata record's `size` equals the storage content's length, `sha256` equals the SHA-256 of the storage content, and `detected_mime_type` equals the magic-byte detection of the storage content. |
| INV-004 | For any user: at most one avatar file exists — the user → file mapping points to exactly one existing file (or the user has no avatar). |
| INV-005 | For any uploaded avatar: the returned URL matches `https://<host>/files/<canonical UUID>` and starts with `https://` (satisfying user-management's `profile_picture_url` validation). |
| INV-006 | For any operation: exactly the corresponding events are published — `FileUploaded` per file record created, `FileDeleted` per file record deleted, `FileDownloaded` per successful download/open, `AvatarUploaded`/`AvatarDeleted` per avatar operation; no event is published on failure except `FileValidationFailed` on a validation failure. |
| INV-007 | For any key (service-generated or caller-specified) and any storage operation: the resolved storage path is inside the storage root; no key can escape the root. |
| INV-008 | For any avatar file: exactly two variant files exist (`variant_of` equal to the avatar's id), stored as PNG with longest side 64px and 256px; when the avatar file is deleted, its variants are deleted. |

## 7. Edge Cases & Error Conditions

| ID | Condition | Expected Behavior |
|----|-----------|-------------------|
| EDGE-001 | `upload` with a `str` source that does not exist on disk | A `FileValidationError` is raised with reason `source_not_found`; `FileValidationFailed` is published; nothing is stored. |
| EDGE-002 | `upload` with a `str` source pointing to a directory | A `FileValidationError` is raised with reason `source_not_a_file`; `FileValidationFailed` is published; nothing is stored. |
| EDGE-003 | A file-like stream whose content exceeds the effective max size mid-stream | The stream is aborted, the temp file is deleted, and a `FileTooLargeError` is raised (no partial state). |
| EDGE-004 | A caller-specified key containing a null byte | A `FileValidationError` is raised with reason `invalid_key`; nothing is stored. |
| EDGE-005 | A caller-specified key that is an absolute path (e.g., `/etc/passwd`) | A `FileValidationError` is raised with reason `invalid_key` (the key pattern rejects it); nothing is stored. |
| EDGE-006 | A metadata record exists but the storage content is missing (inconsistent store) | `download`/`open` raises a `StorageError` with reason `not_found`; the record is not auto-deleted. |
| EDGE-007 | `delete` of a file whose storage content is already missing | The metadata record is still deleted (the storage delete is a no-op); `FileDeleted` is published. |
| EDGE-008 | `list_files` on an empty store | Returns `[]`. |
| EDGE-009 | `list_files` with an offset beyond the last item | Returns `[]`. |
| EDGE-010 | A sequential `upload` to an existing key | The file is replaced (a new record id, the new content, a fresh `updated_at`); no error. |
| EDGE-011 | The user → file mapping points to a deleted file (dangling mapping) | `get_avatar` returns the default avatar, **And** the dangling mapping is cleared. |
| EDGE-012 | Avatar content that magic bytes detect as `image/png` but that fails Pillow decode (truncated PNG) | A `FileValidationError` is raised with reason `image_decode_failed` (decode validation is stricter than magic bytes). |
| EDGE-013 | Variant generation failure (injected fault) | The entire upload is rolled back (no main file, no variants, no records), and a `StorageError` is raised with reason `variant_generation`. |
| EDGE-014 | A publisher that raises on `publish` | The exception propagates to the caller; the operation is already committed. |
| EDGE-015 | `SqliteFileRepository` with a `database_url` whose parent directory does not exist | The parent directory is auto-created; the repository works. |
| EDGE-016 | `InMemoryStorageBackend` isolation | Two instances are isolated (no shared state). |
| EDGE-017 | A `download` concurrent with a same-key upload completing | The download returns either the old or the new content — a complete file, never partial. |
| EDGE-018 | Avatar content with dimensions exactly 4096×4096 | Allowed (the boundary is inclusive). |
| EDGE-019 | A general upload of exactly the effective max size | Allowed (`size == limit` is OK; `size > limit` is rejected). |

## 8. Non-Functional Requirements

| ID | Category | Requirement |
|----|----------|-------------|
| NFR-001 | Performance | Upload of a 10 MB file completes in < 2 s (median); download of a 10 MB file completes in < 1 s (median); a metadata read (`get_file`) completes in < 5 ms (median); measured on local hardware with the shared logging feature configured at the default INFO level with a synchronous console sink; the budgets hold including the per-call `@logged` tracing overhead at that level. |
| NFR-002 | Security | Nothing escapes the storage root (the key/namespace patterns reject path separators, null bytes, and traversal; the local backend verifies path containment and rejects symlinks); file content never appears in log records, events, or error messages. |
| NFR-003 | Contract | The public API (`FileService`, `FileRepository`, `SqliteFileRepository`, `StorageBackend`, `LocalDiskStorageBackend`, `InMemoryStorageBackend`, schemas, events, errors) is backward-compatible; adding optional parameters must not break existing callers. The avatar URL contract: the URL always starts with `https://` (satisfying user-management's `profile_picture_url` validation without a spec amendment). |
| NFR-004 | Reliability | The SQLite repository is safe for concurrent use from multiple threads; a failed operation leaves no partial state (INV-001); the DB file's parent directory is auto-created. |
| NFR-005 | Observability | Service operations are traced via the shared logging feature (`@logged_class` on `FileService`, `@logged` on module functions); file content never appears in log records; validation failures are logged with the failure kind and key (no content). |

## 9. Observability & Logging

Every feature MUST be observable. Specify the logging behavior: which operations are logged, at what level, and with what context. Shared infrastructure features MUST log entry points, errors, and lifecycle events; verbose tracing belongs at DEBUG (off by default).

- `FileService` is decorated with `@logged_class(slow_threshold_ms=5000, include_args=False)` from the shared logging feature: every public method is traced with an entry line, an exit line (elapsed ms), and an exception line on error.
  - `include_args=False`: method arguments include file content (bytes/stream), paths, and user references — they are never logged (REQ-025).
  - `slow_threshold_ms=5000`: a 10 MB upload is budgeted at 2 s (NFR-001), so the slow-call threshold is set above the budget (consistent with the mail service).
- The module-level functions `register_settings` and `get_default_avatar` are traced with `@logged` (`register_settings` with `slow_threshold_ms=5`, consistent with the other features).
- Domain error messages carry no file content (only error kind, key, size, MIME type, dimensions), so exception lines are safe.

| Operation / Event | Level | Context |
|-------------------|-------|---------|
| Any service method call (entry/exit) | DEBUG | method qualname, elapsed ms |
| `upload` success | DEBUG | method qualname, elapsed ms (key/namespace via the return value, not the args) |
| Validation failure (`FileTooLargeError`, `FileTypeNotAllowedError`, `FileValidationError`) | DEBUG (exception line) | error type + message (kind, key, size/limit — no content) |
| Storage failure (`StorageError`) | DEBUG (exception line) | error type + message (key, reason — no content) |
| `FileUploaded` / `FileDownloaded` / `FileDeleted` / `AvatarUploaded` / `AvatarDeleted` | (event, not a log) | non-sensitive fields only (no content) |

- **Default level:** DEBUG tracing (off at INFO); domain errors are logged with type + message.
- **Error conditions:** domain errors are logged via `@logged` exception tracing; file content never appears in any log record (NFR-002).

## 10. Test Strategy

Map each requirement/AC to a test category. This drives the test file layout.

| ID | Test Category | Test File | Test Function |
|----|---------------|-----------|---------------|
| REQ-001 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_001_upload_bytes_round_trip` |
| REQ-002 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_001_upload_bytes_round_trip` |
| REQ-003 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_004_zero_byte_rejected` |
| REQ-004 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_008_magic_byte_detection` |
| REQ-005 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_009_declared_type_conflict` |
| REQ-006 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_011_type_not_allowed` |
| REQ-007 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_013_generated_uuid_key` |
| REQ-008 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_016_storage_failure_rollback` |
| REQ-009 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_018_concurrent_same_key_last_write_wins` |
| REQ-010 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_019_download_bytes` |
| REQ-011 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_022_delete` |
| REQ-012 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_024_metadata_fields` |
| REQ-013 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_025_persistence_across_instances` |
| REQ-014 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_027_get_file_and_list_pagination` |
| REQ-015 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_029_default_local_backend` |
| REQ-016 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_031_symlink_rejected` |
| REQ-017 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_033_upload_avatar` |
| REQ-018 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_039_avatar_url_format` |
| REQ-019 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_041_avatar_undecodable` |
| REQ-020 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_044_get_avatar_default` |
| REQ-021 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_045_avatar_variants_created` |
| REQ-022 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_047_event_uploaded` |
| REQ-023 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_051_error_hierarchy_context` |
| REQ-024 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_052_register_settings` |
| REQ-025 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_054_operations_traced` |
| REQ-026 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_055_layout_convention` |
| AC-001 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_001_upload_bytes_round_trip` |
| AC-002 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_002_upload_file_path` |
| AC-003 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_003_upload_file_like_stream` |
| AC-004 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_004_zero_byte_rejected` |
| AC-005 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_005_general_size_limit` |
| AC-006 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_006_avatar_size_limit` |
| AC-007 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_007_live_max_file_size` |
| AC-008 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_008_magic_byte_detection` |
| AC-009 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_009_declared_type_conflict` |
| AC-010 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_010_filename_type_conflict` |
| AC-011 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_011_type_not_allowed` |
| AC-012 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_012_live_allowed_types` |
| AC-013 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_013_generated_uuid_key` |
| AC-014 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_014_caller_key` |
| AC-015 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_015_traversal_key_rejected` |
| AC-016 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_016_storage_failure_rollback` |
| AC-017 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_017_metadata_failure_rollback` |
| AC-018 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_018_concurrent_same_key_last_write_wins` |
| AC-019 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_019_download_bytes` |
| AC-020 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_020_open_stream` |
| AC-021 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_021_download_missing` |
| AC-022 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_022_delete` |
| AC-023 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_023_delete_missing` |
| AC-024 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_024_metadata_fields` |
| AC-025 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_025_persistence_across_instances` |
| AC-026 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_026_service_with_fake_repository` |
| AC-027 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_027_get_file_and_list_pagination` |
| AC-028 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_028_list_invalid_pagination` |
| AC-029 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_029_default_local_backend` |
| AC-030 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_030_in_memory_backend` |
| AC-031 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_031_symlink_rejected` |
| AC-032 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_032_path_escape_rejected` |
| AC-033 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_033_upload_avatar` |
| AC-034 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_034_upload_avatar_existing` |
| AC-035 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_035_replace_avatar` |
| AC-036 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_036_replace_avatar_missing` |
| AC-037 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_037_delete_avatar` |
| AC-038 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_038_delete_avatar_noop` |
| AC-039 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_039_avatar_url_format` |
| AC-040 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_040_live_avatar_base_url` |
| AC-041 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_041_avatar_undecodable` |
| AC-042 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_042_avatar_dimensions_exceeded` |
| AC-043 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_043_avatar_type_not_allowed` |
| AC-044 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_044_get_avatar_default` |
| AC-045 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_045_avatar_variants_created` |
| AC-046 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_046_avatar_variants_replaced` |
| AC-047 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_047_event_uploaded` |
| AC-048 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_048_event_downloaded_deleted` |
| AC-049 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_049_event_validation_failed` |
| AC-050 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_050_no_publisher` |
| AC-051 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_051_error_hierarchy_context` |
| AC-052 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_052_register_settings` |
| AC-053 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_053_unregistered_settings_defaults` |
| AC-054 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_054_operations_traced` |
| AC-055 | acceptance | `tests/acceptance/filemanagement/test_filemanagement.py` | `test_ac_055_layout_convention` |
| INV-001 | property | `tests/property/filemanagement/test_filemanagement_properties.py` | `test_inv_001_no_partial_state_on_failure` |
| INV-002 | property | `tests/property/filemanagement/test_filemanagement_properties.py` | `test_inv_002_concurrent_same_key_last_write_wins` |
| INV-003 | property | `tests/property/filemanagement/test_filemanagement_properties.py` | `test_inv_003_metadata_matches_content` |
| INV-004 | property | `tests/property/filemanagement/test_filemanagement_properties.py` | `test_inv_004_at_most_one_avatar_per_user` |
| INV-005 | property | `tests/property/filemanagement/test_filemanagement_properties.py` | `test_inv_005_avatar_url_format` |
| INV-006 | property | `tests/property/filemanagement/test_filemanagement_properties.py` | `test_inv_006_event_correspondence` |
| INV-007 | property | `tests/property/filemanagement/test_filemanagement_properties.py` | `test_inv_007_key_containment` |
| INV-008 | property | `tests/property/filemanagement/test_filemanagement_properties.py` | `test_inv_008_variant_consistency` |
| EDGE-001 | unit | `tests/unit/filemanagement/test_filemanagement_edges.py` | `test_edge_001_source_not_found` |
| EDGE-002 | unit | `tests/unit/filemanagement/test_filemanagement_edges.py` | `test_edge_002_source_not_a_file` |
| EDGE-003 | unit | `tests/unit/filemanagement/test_filemanagement_edges.py` | `test_edge_003_stream_exceeds_limit_mid_stream` |
| EDGE-004 | unit | `tests/unit/filemanagement/test_filemanagement_edges.py` | `test_edge_004_key_null_byte` |
| EDGE-005 | unit | `tests/unit/filemanagement/test_filemanagement_edges.py` | `test_edge_005_key_absolute_path` |
| EDGE-006 | unit | `tests/unit/filemanagement/test_filemanagement_edges.py` | `test_edge_006_record_without_content` |
| EDGE-007 | unit | `tests/unit/filemanagement/test_filemanagement_edges.py` | `test_edge_007_delete_missing_content` |
| EDGE-008 | unit | `tests/unit/filemanagement/test_filemanagement_edges.py` | `test_edge_008_list_empty_store` |
| EDGE-009 | unit | `tests/unit/filemanagement/test_filemanagement_edges.py` | `test_edge_009_list_offset_beyond_end` |
| EDGE-010 | unit | `tests/unit/filemanagement/test_filemanagement_edges.py` | `test_edge_010_sequential_key_replacement` |
| EDGE-011 | unit | `tests/unit/filemanagement/test_filemanagement_edges.py` | `test_edge_011_dangling_avatar_mapping` |
| EDGE-012 | unit | `tests/unit/filemanagement/test_filemanagement_edges.py` | `test_edge_012_truncated_png_decode_failure` |
| EDGE-013 | unit | `tests/unit/filemanagement/test_filemanagement_edges.py` | `test_edge_013_variant_generation_failure_rollback` |
| EDGE-014 | unit | `tests/unit/filemanagement/test_filemanagement_edges.py` | `test_edge_014_publisher_raises` |
| EDGE-015 | unit | `tests/unit/filemanagement/test_filemanagement_edges.py` | `test_edge_015_repo_creates_parent_dir` |
| EDGE-016 | unit | `tests/unit/filemanagement/test_filemanagement_edges.py` | `test_edge_016_in_memory_isolation` |
| EDGE-017 | unit | `tests/unit/filemanagement/test_filemanagement_edges.py` | `test_edge_017_concurrent_download_upload` |
| EDGE-018 | unit | `tests/unit/filemanagement/test_filemanagement_edges.py` | `test_edge_018_dimensions_boundary_allowed` |
| EDGE-019 | unit | `tests/unit/filemanagement/test_filemanagement_edges.py` | `test_edge_019_size_boundary_allowed` |
| NFR-001 | contract | `tests/contract/filemanagement/test_filemanagement_contracts.py` | `test_nfr_001_performance_budgets` |
| NFR-002 | contract | `tests/contract/filemanagement/test_filemanagement_contracts.py` | `test_nfr_002_no_content_in_logs_events_errors` |
| NFR-003 | contract | `tests/contract/filemanagement/test_filemanagement_contracts.py` | `test_nfr_003_api_backward_compatible` |
| NFR-004 | contract | `tests/contract/filemanagement/test_filemanagement_contracts.py` | `test_nfr_004_concurrent_repository_safety` |
| NFR-005 | contract | `tests/contract/filemanagement/test_filemanagement_contracts.py` | `test_nfr_005_operations_logged` |
| — | integration | `tests/integration/filemanagement/test_filemanagement_integration.py` | `test_full_file_lifecycle` |
| — | integration | `tests/integration/filemanagement/test_filemanagement_integration.py` | `test_avatar_lifecycle_with_variants` |
| — | integration | `tests/integration/filemanagement/test_filemanagement_integration.py` | `test_concurrent_same_key_upload` |

## 11. Traceability Matrix

Maintain this matrix as tests are written and pass. Every normative requirement MUST have at least one executable test.

| Requirement | Acceptance Criterion | Test | Status |
|-------------|---------------------|------|--------|
| REQ-001 | AC-001 | `test_ac_001_upload_bytes_round_trip` | PENDING |
| REQ-002 | AC-001 | `test_ac_001_upload_bytes_round_trip` | PENDING |
| REQ-002 | AC-002 | `test_ac_002_upload_file_path` | PENDING |
| REQ-002 | AC-003 | `test_ac_003_upload_file_like_stream` | PENDING |
| REQ-003 | AC-004 | `test_ac_004_zero_byte_rejected` | PENDING |
| REQ-003 | AC-005 | `test_ac_005_general_size_limit` | PENDING |
| REQ-003 | AC-006 | `test_ac_006_avatar_size_limit` | PENDING |
| REQ-003 | AC-007 | `test_ac_007_live_max_file_size` | PENDING |
| REQ-004 | AC-008 | `test_ac_008_magic_byte_detection` | PENDING |
| REQ-005 | AC-009 | `test_ac_009_declared_type_conflict` | PENDING |
| REQ-005 | AC-010 | `test_ac_010_filename_type_conflict` | PENDING |
| REQ-006 | AC-011 | `test_ac_011_type_not_allowed` | PENDING |
| REQ-006 | AC-012 | `test_ac_012_live_allowed_types` | PENDING |
| REQ-007 | AC-013 | `test_ac_013_generated_uuid_key` | PENDING |
| REQ-007 | AC-014 | `test_ac_014_caller_key` | PENDING |
| REQ-007 | AC-015 | `test_ac_015_traversal_key_rejected` | PENDING |
| REQ-008 | AC-016 | `test_ac_016_storage_failure_rollback` | PENDING |
| REQ-008 | AC-017 | `test_ac_017_metadata_failure_rollback` | PENDING |
| REQ-009 | AC-018 | `test_ac_018_concurrent_same_key_last_write_wins` | PENDING |
| REQ-010 | AC-019 | `test_ac_019_download_bytes` | PENDING |
| REQ-010 | AC-020 | `test_ac_020_open_stream` | PENDING |
| REQ-010 | AC-021 | `test_ac_021_download_missing` | PENDING |
| REQ-011 | AC-022 | `test_ac_022_delete` | PENDING |
| REQ-011 | AC-023 | `test_ac_023_delete_missing` | PENDING |
| REQ-012 | AC-024 | `test_ac_024_metadata_fields` | PENDING |
| REQ-013 | AC-025 | `test_ac_025_persistence_across_instances` | PENDING |
| REQ-013 | AC-026 | `test_ac_026_service_with_fake_repository` | PENDING |
| REQ-014 | AC-027 | `test_ac_027_get_file_and_list_pagination` | PENDING |
| REQ-014 | AC-028 | `test_ac_028_list_invalid_pagination` | PENDING |
| REQ-015 | AC-029 | `test_ac_029_default_local_backend` | PENDING |
| REQ-015 | AC-030 | `test_ac_030_in_memory_backend` | PENDING |
| REQ-016 | AC-031 | `test_ac_031_symlink_rejected` | PENDING |
| REQ-016 | AC-032 | `test_ac_032_path_escape_rejected` | PENDING |
| REQ-017 | AC-033 | `test_ac_033_upload_avatar` | PENDING |
| REQ-017 | AC-034 | `test_ac_034_upload_avatar_existing` | PENDING |
| REQ-017 | AC-035 | `test_ac_035_replace_avatar` | PENDING |
| REQ-017 | AC-036 | `test_ac_036_replace_avatar_missing` | PENDING |
| REQ-017 | AC-037 | `test_ac_037_delete_avatar` | PENDING |
| REQ-017 | AC-038 | `test_ac_038_delete_avatar_noop` | PENDING |
| REQ-018 | AC-039 | `test_ac_039_avatar_url_format` | PENDING |
| REQ-018 | AC-040 | `test_ac_040_live_avatar_base_url` | PENDING |
| REQ-019 | AC-041 | `test_ac_041_avatar_undecodable` | PENDING |
| REQ-019 | AC-042 | `test_ac_042_avatar_dimensions_exceeded` | PENDING |
| REQ-019 | AC-043 | `test_ac_043_avatar_type_not_allowed` | PENDING |
| REQ-020 | AC-044 | `test_ac_044_get_avatar_default` | PENDING |
| REQ-021 | AC-045 | `test_ac_045_avatar_variants_created` | PENDING |
| REQ-021 | AC-046 | `test_ac_046_avatar_variants_replaced` | PENDING |
| REQ-022 | AC-047 | `test_ac_047_event_uploaded` | PENDING |
| REQ-022 | AC-048 | `test_ac_048_event_downloaded_deleted` | PENDING |
| REQ-022 | AC-049 | `test_ac_049_event_validation_failed` | PENDING |
| REQ-022 | AC-050 | `test_ac_050_no_publisher` | PENDING |
| REQ-023 | AC-051 | `test_ac_051_error_hierarchy_context` | PENDING |
| REQ-024 | AC-052 | `test_ac_052_register_settings` | PENDING |
| REQ-024 | AC-053 | `test_ac_053_unregistered_settings_defaults` | PENDING |
| REQ-025 | AC-054 | `test_ac_054_operations_traced` | PENDING |
| REQ-026 | AC-055 | `test_ac_055_layout_convention` | PENDING |
| INV-001 | — | `test_inv_001_no_partial_state_on_failure` | PENDING |
| INV-002 | — | `test_inv_002_concurrent_same_key_last_write_wins` | PENDING |
| INV-003 | — | `test_inv_003_metadata_matches_content` | PENDING |
| INV-004 | — | `test_inv_004_at_most_one_avatar_per_user` | PENDING |
| INV-005 | — | `test_inv_005_avatar_url_format` | PENDING |
| INV-006 | — | `test_inv_006_event_correspondence` | PENDING |
| INV-007 | — | `test_inv_007_key_containment` | PENDING |
| INV-008 | — | `test_inv_008_variant_consistency` | PENDING |
| NFR-001 | — | `test_nfr_001_performance_budgets` | PENDING |
| NFR-002 | — | `test_nfr_002_no_content_in_logs_events_errors` | PENDING |
| NFR-003 | — | `test_nfr_003_api_backward_compatible` | PENDING |
| NFR-004 | — | `test_nfr_004_concurrent_repository_safety` | PENDING |
| NFR-005 | — | `test_nfr_005_operations_logged` | PENDING |
