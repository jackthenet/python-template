"""Public API of the file-management feature (module: backend.filemanagement).

T-001 implements the foundation: the error hierarchy (``errors``), the typed
lifecycle events + structural publisher (``events``), and the domain models and
fixed constants (``models``).

``register_settings`` (T-002) is a real implementation in
``feature_settings``; the storage backends (T-003) are real implementations
in ``storage``; the metadata repository (T-004) is a real implementation in
``repository``; the upload service (T-005) is a real implementation in
``service``.
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
from backend.filemanagement.repository import FileRepository, SqliteFileRepository
from backend.filemanagement.service import FileService, get_default_avatar
from backend.filemanagement.storage import (
    InMemoryStorageBackend,
    LocalDiskStorageBackend,
    StorageBackend,
)

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
    "FileRepository",
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
    "get_default_avatar",
    "register_settings",
]
