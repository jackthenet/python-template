"""Storage backends for the file-management feature (REQ-015, REQ-016).

The :class:`StorageBackend` ABC is the only seam service code references —
both concrete backends are swappable.

- :class:`LocalDiskStorageBackend` stores content on local disk in a flat
  layout (one file per key directly under the root; the key is the filename).
  Nothing can escape the storage root: key pattern + path containment +
  symlink rejection (defense in depth). ``put`` is atomic (temp file +
  ``os.replace``) and last-write-wins (replaces existing content).
- :class:`InMemoryStorageBackend` stores content in a dict of key → bytes.
  It is public for tests/DI; instances are isolated (no shared state between
  instances).
"""

from __future__ import annotations

import contextlib
import io
import os
import re
import shutil
import tempfile
from abc import ABC, abstractmethod
from datetime import UTC, datetime
from pathlib import Path
from typing import BinaryIO

from backend.filemanagement.errors import StorageError
from backend.filemanagement.models import KEY_PATTERN, StorageStat


class StorageBackend(ABC):
    """Seam for storage content (REQ-015).

    Service code references only this ABC — both backends are swappable.
    """

    @abstractmethod
    def put(self, key: str, data: bytes | BinaryIO) -> None:
        """Atomically write content to ``key``, replacing existing content (last-write-wins).

        Raises ``StorageError`` with reason ``'io'``, ``'symlink'``, or
        ``'path_escape'`` (local backend).
        """

    @abstractmethod
    def get(self, key: str) -> BinaryIO:
        """Return a file-like stream of the content at ``key``.

        Raises ``StorageError`` with reason ``'not_found'`` if the key is
        absent.
        """

    @abstractmethod
    def delete(self, key: str) -> None:
        """Delete the content at ``key`` (no-op if absent)."""

    @abstractmethod
    def exists(self, key: str) -> bool:
        """Whether content exists at ``key``."""

    @abstractmethod
    def stat(self, key: str) -> StorageStat | None:
        """Return the content's size/updated time at ``key``, or ``None`` if absent."""


class LocalDiskStorageBackend(StorageBackend):
    """Local-disk storage backend (REQ-015, REQ-016).

    Flat layout: one file per key directly under ``root`` (the key is the
    filename). Nothing can escape the storage root (defense in depth):

    1. the key must match ``KEY_PATTERN`` (no ``/``, no ``..``, no null
       bytes, no absolute paths) — a violating key raises
       ``StorageError(reason='path_escape')``;
    2. a symlink at the target path or any path component raises
       ``StorageError(reason='symlink')`` and is never followed;
    3. the resolved target path must stay inside the resolved root —
       otherwise ``StorageError(reason='path_escape')``.

    ``put`` writes to a temp file in ``root`` then ``os.replace`` (atomic
    rename) and is last-write-wins.
    """

    def __init__(self, root: Path) -> None:
        self._root = Path(root)

    def _target(self, key: str) -> Path:
        """Validate ``key`` and return its target path inside the root.

        Raises ``StorageError`` with reason ``'path_escape'`` (key pattern or
        containment) or ``'symlink'`` (a symlink at the target path or any
        path component, never followed).
        """
        if re.match(KEY_PATTERN, key) is None:
            raise StorageError(key, "path_escape")
        target = self._root / key
        for component in (self._root, target):
            if component.is_symlink():
                raise StorageError(key, "symlink")
        resolved_root = self._root.resolve()
        if not target.resolve().is_relative_to(resolved_root):
            raise StorageError(key, "path_escape")
        return target

    def put(self, key: str, data: bytes | BinaryIO) -> None:
        target = self._target(key)
        tmp: str | None = None
        try:
            self._root.mkdir(parents=True, exist_ok=True)
            fd, tmp = tempfile.mkstemp(dir=self._root, prefix=".tmp-")
            with os.fdopen(fd, "wb") as f:
                if isinstance(data, (bytes, bytearray, memoryview)):
                    f.write(bytes(data))
                else:
                    shutil.copyfileobj(data, f)
            os.replace(tmp, target)
            tmp = None
        except OSError as e:
            if tmp is not None:
                with contextlib.suppress(OSError):
                    os.unlink(tmp)
            raise StorageError(key, "io") from e

    def get(self, key: str) -> BinaryIO:
        target = self._target(key)
        if not target.is_file():
            raise StorageError(key, "not_found")
        try:
            return target.open("rb")
        except OSError as e:
            raise StorageError(key, "io") from e

    def delete(self, key: str) -> None:
        target = self._target(key)
        try:
            target.unlink(missing_ok=True)
        except OSError as e:
            raise StorageError(key, "io") from e

    def exists(self, key: str) -> bool:
        try:
            target = self._target(key)
        except StorageError:
            return False
        return target.is_file()

    def stat(self, key: str) -> StorageStat | None:
        try:
            target = self._target(key)
        except StorageError:
            return None
        if not target.is_file():
            return None
        st = target.stat()
        return StorageStat(size=st.st_size, updated_at=datetime.fromtimestamp(st.st_mtime, UTC))


class InMemoryStorageBackend(StorageBackend):
    """Public in-memory storage backend for tests/DI (REQ-015).

    Content is a dict of key → bytes. Instances are isolated: there is no
    shared state between instances.
    """

    def __init__(self) -> None:
        self._data: dict[str, bytes] = {}
        self._updated_at: dict[str, datetime] = {}

    def put(self, key: str, data: bytes | BinaryIO) -> None:
        content = bytes(data) if isinstance(data, (bytes, bytearray, memoryview)) else data.read()
        self._data[key] = content
        self._updated_at[key] = datetime.now(UTC)

    def get(self, key: str) -> BinaryIO:
        if key not in self._data:
            raise StorageError(key, "not_found")
        return io.BytesIO(self._data[key])

    def delete(self, key: str) -> None:
        self._data.pop(key, None)
        self._updated_at.pop(key, None)

    def exists(self, key: str) -> bool:
        return key in self._data

    def stat(self, key: str) -> StorageStat | None:
        if key not in self._data:
            return None
        return StorageStat(size=len(self._data[key]), updated_at=self._updated_at[key])
