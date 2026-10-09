"""Structured domain errors for the file-management feature (REQ-023, D11, ADR-059).

The exception hierarchy is rooted at :class:`FileManagementError`. Every
subclass carries the documented context attributes and a message free of file
content (error kind, key, size, MIME type, and dimensions only), so the
messages are safe to log (NFR-002).
"""

from __future__ import annotations


class FileManagementError(Exception):
    """Base class for all file-management domain errors."""


class FileManagementNotFoundError(FileManagementError):
    """No file exists for the requested key (REQ-010, REQ-011, REQ-014)."""

    def __init__(self, key: str) -> None:
        """``key`` is the looked-up key, echoed verbatim into the message.

        Every read and delete path raises this same error, so a caller cannot
        tell "never stored" from "already deleted" (REQ-023).
        """
        self.key = key
        super().__init__(f"file not found: {key}")


class FileTooLargeError(FileManagementError):
    """Content exceeds the effective max size (REQ-003).

    ``size`` is the actual size in bytes; ``limit`` is the effective max size
    in bytes.
    """

    def __init__(self, key: str | None, size: int, limit: int) -> None:
        """Both sizes are bytes; ``limit`` is the effective limit at check time.

        The limit is read live per namespace, so it need not match any
        configured default (REQ-003).
        """
        self.key = key
        self.size = size
        self.limit = limit
        super().__init__(f"file too large: {size} bytes exceeds the {limit} byte limit")


class FileTypeNotAllowedError(FileManagementError):
    """The detected MIME type is not in the effective allowed set (REQ-006).

    ``detected`` is the detected MIME type; ``allowed`` is the effective
    allowed set.
    """

    def __init__(self, key: str | None, detected: str, allowed: frozenset[str]) -> None:
        """``allowed`` is the effective set at check time, snapshotted into the error.

        For the ``avatars`` namespace that set is the fixed image set, so the
        ``filemanagement.allowed_types`` setting never appears in it (REQ-006).
        """
        self.key = key
        self.detected = detected
        self.allowed = allowed
        super().__init__(f"file type not allowed: detected {detected!r} is not in the allowed set")


class FileValidationError(FileManagementError):
    """An upload was rejected by validation (REQ-003..REQ-007, REQ-019).

    ``reason`` is a short, secret-free string (e.g. ``"zero_byte_file"``,
    ``"type_conflict"``, ``"invalid_key"``, ``"invalid_namespace"``,
    ``"source_not_found"``, ``"source_not_a_file"``, ``"image_decode_failed"``,
    ``"dimensions_exceeded"``). The optional ``declared``/``detected``
    (``type_conflict``) and ``width``/``height`` (``dimensions_exceeded``)
    carry the conflicting/exceeding context.
    """

    def __init__(
        self,
        key: str | None,
        reason: str,
        *,
        declared: str | None = None,
        detected: str | None = None,
        width: int | None = None,
        height: int | None = None,
    ) -> None:
        """Only the context matching ``reason`` is populated; the rest stays ``None``.

        For ``type_conflict`` a filename-extension conflict arrives as
        ``declared`` even though the caller declared nothing, so ``declared``
        means "the implied type", not "the caller's argument".
        """
        self.key = key
        self.reason = reason
        self.declared = declared
        self.detected = detected
        self.width = width
        self.height = height
        super().__init__(f"file validation failed: {reason}")


class StorageError(FileManagementError):
    """A storage operation failed (REQ-008, REQ-016).

    ``reason`` is a short, secret-free string (e.g. ``"not_found"``,
    ``"io"``, ``"symlink"``, ``"path_escape"``, ``"variant_generation"``).
    """

    def __init__(self, key: str | None, reason: str) -> None:
        """``reason`` is the stable classification callers branch on (REQ-023).

        For ``io`` and ``variant_generation`` the failing ``OSError`` is chained
        as ``__cause__``: the filesystem detail stays available to a debugger
        without reaching the message (NFR-002).
        """
        self.key = key
        self.reason = reason
        super().__init__(f"storage error: {reason}")


class AvatarError(FileManagementError):
    """An avatar lifecycle operation was invalid (REQ-017).

    ``operation`` is ``"upload"`` (an avatar already exists) or ``"replace"``
    (no avatar exists).
    """

    def __init__(self, user_id: str, operation: str) -> None:
        """One class covers both causes; the caller branches on ``operation``.

        ``"upload"`` means the user already has an avatar, ``"replace"`` means
        the user has none (REQ-017).
        """
        self.user_id = user_id
        self.operation = operation
        super().__init__(f"avatar error: {operation} for user {user_id!r}")
