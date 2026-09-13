"""Public API of the file-management feature (module: backend.filemanagement).

T-001 implements the foundation: the error hierarchy (``errors``), the typed
lifecycle events + structural publisher (``events``), and the domain models and
fixed constants (``models``).

The later-task public names (``FileService``, the repository, and the storage
backends) are present as **collection scaffolding** only: the derived test
suite imports them at module level, so the package must export them for the
tests to be collected. They raise ``NotImplementedError`` when used — they
carry no behavior. The real implementations land in T-003..T-008 and replace
these placeholders. ``register_settings`` (T-002) is a real implementation in
``feature_settings``.
"""

from __future__ import annotations

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
    AvatarEvent,
    AvatarUploaded,
    EventPublisher,
    FileDeleted,
    FileDownloaded,
    FileEvent,
    FileUploaded,
    FileValidationFailed,
)
from backend.filemanagement.feature_settings import register_settings
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
    StorageStat,
    UserAvatar,
)

# --- Collection scaffolding for later tasks (T-002..T-008) ------------------
# No behavior: each raises NotImplementedError when used. Replaced by the real
# implementations in the tasks noted below.


class StorageBackend:
    """Placeholder for the storage backend ABC (implemented in T-003)."""

    def __init__(self) -> None:
        raise NotImplementedError("StorageBackend is implemented in T-003")


class LocalDiskStorageBackend(StorageBackend):
    """Placeholder (implemented in T-003)."""

    def __init__(self, root) -> None:
        raise NotImplementedError("LocalDiskStorageBackend is implemented in T-003")


class InMemoryStorageBackend(StorageBackend):
    """Placeholder (implemented in T-003)."""

    def __init__(self) -> None:
        raise NotImplementedError("InMemoryStorageBackend is implemented in T-003")


class SqliteFileRepository:
    """Placeholder (implemented in T-004)."""

    def __init__(self, database_url: str) -> None:
        raise NotImplementedError("SqliteFileRepository is implemented in T-004")


class FileService:
    """Placeholder (implemented in T-005)."""

    def __init__(self, repository, backend=None, event_bus=None, settings_registry=None) -> None:
        raise NotImplementedError("FileService is implemented in T-005")


__all__ = [
    "AVATAR_ALLOWED_TYPES",
    "AVATAR_MAX_HEIGHT",
    "AVATAR_MAX_WIDTH",
    "AVATAR_VARIANT_SIZES",
    "DEFAULT_AVATAR_PATH",
    "KEY_PATTERN",
    "NAMESPACE_PATTERN",
    "AvatarDeleted",
    "AvatarError",
    "AvatarEvent",
    "AvatarRead",
    "AvatarUploaded",
    "EventPublisher",
    "FileDeleted",
    "FileDownloaded",
    "FileEvent",
    "FileManagementError",
    "FileManagementNotFoundError",
    "FileRead",
    "FileRecord",
    "FileService",
    "FileTooLargeError",
    "FileTypeNotAllowedError",
    "FileUploaded",
    "FileValidationError",
    "FileValidationFailed",
    "InMemoryStorageBackend",
    "LocalDiskStorageBackend",
    "SqliteFileRepository",
    "StorageBackend",
    "StorageError",
    "StorageStat",
    "UserAvatar",
    "register_settings",
]
