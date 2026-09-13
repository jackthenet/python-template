"""Contract tests for the filemanagement feature (docs/specs/file-management.md).

NFR-001 .. NFR-005.
"""

from __future__ import annotations

import inspect
import statistics
import threading
import time
from pathlib import Path
from typing import Any

import pytest
from backend.filemanagement import (
    FileManagementNotFoundError,
    FileService,
    FileValidationError,
    InMemoryStorageBackend,
    SqliteFileRepository,
    register_settings,
)

from backend.settings import get_settings_registry
from tests.filemanagement_test_helpers import (
    EventCollector,
    db_url,
    isolated_registry,
    make_service,
    png_bytes,
    text_bytes,
)

_UPLOAD_BUDGET_S = 2.0
_DOWNLOAD_BUDGET_S = 1.0
_READ_BUDGET_MS = 5.0
_RUNS = 5

_PUBLIC_API = (
    "FileRecord",
    "UserAvatar",
    "FileRead",
    "AvatarRead",
    "StorageStat",
    "StorageBackend",
    "LocalDiskStorageBackend",
    "InMemoryStorageBackend",
    "FileRepository",
    "SqliteFileRepository",
    "FileService",
    "FileEvent",
    "FileUploaded",
    "FileDownloaded",
    "FileDeleted",
    "FileValidationFailed",
    "AvatarEvent",
    "AvatarUploaded",
    "AvatarDeleted",
    "EventPublisher",
    "FileManagementError",
    "FileManagementNotFoundError",
    "FileTooLargeError",
    "FileTypeNotAllowedError",
    "FileValidationError",
    "StorageError",
    "AvatarError",
    "register_settings",
    "get_default_avatar",
    "AVATAR_VARIANT_SIZES",
    "AVATAR_MAX_WIDTH",
    "AVATAR_MAX_HEIGHT",
    "AVATAR_ALLOWED_TYPES",
    "DEFAULT_AVATAR_PATH",
    "KEY_PATTERN",
    "NAMESPACE_PATTERN",
)


def test_nfr_001_performance_budgets(tmp_path: Path) -> None:
    # Measured with the shared logging feature at the default INFO level.
    shared = get_settings_registry()
    previous = shared.get_value("logging.log_level")
    shared.set_value("logging.log_level", "INFO")
    try:
        root = tmp_path / "files"
        root.mkdir()
        registry = isolated_registry()
        register_settings(registry)
        registry.set_value("filemanagement.storage_root", str(root))
        repo = SqliteFileRepository(db_url(tmp_path))
        svc = FileService(repo, backend=None, event_bus=None, settings_registry=registry)
        payload = text_bytes(10 * 1024 * 1024)

        upload_s: list[float] = []
        for i in range(_RUNS):
            t0 = time.perf_counter()
            svc.upload(payload, key=f"nfr001-{i}")
            upload_s.append(time.perf_counter() - t0)
        download_s: list[float] = []
        for _ in range(_RUNS):
            t0 = time.perf_counter()
            svc.download("nfr001-0")
            download_s.append(time.perf_counter() - t0)
        read_ms: list[float] = []
        for _ in range(_RUNS):
            t0 = time.perf_counter()
            svc.get_file("nfr001-0")
            read_ms.append((time.perf_counter() - t0) * 1000)
    finally:
        shared.set_value("logging.log_level", previous)
    assert statistics.median(upload_s) < _UPLOAD_BUDGET_S, (
        f"upload median {statistics.median(upload_s):.3f} s exceeds 2 s budget"
    )
    assert statistics.median(download_s) < _DOWNLOAD_BUDGET_S, (
        f"download median {statistics.median(download_s):.3f} s exceeds 1 s budget"
    )
    assert statistics.median(read_ms) < _READ_BUDGET_MS, (
        f"read median {statistics.median(read_ms):.3f} ms exceeds 5 ms budget"
    )


def test_nfr_002_no_content_in_logs_events_errors(tmp_path: Path, log_records: list[Any]) -> None:
    marker = b"SECRET-CONTENT-MARKER-" * 32
    events = EventCollector()
    svc = make_service(
        SqliteFileRepository(db_url(tmp_path)),
        backend=InMemoryStorageBackend(),
        event_bus=events,
        registry=isolated_registry(),
    )
    svc.upload(marker)
    with pytest.raises(FileValidationError):
        svc.upload(marker, key="bad\0key")  # failure path: error messages are secret-free
    text = [str(m) for m in log_records]
    assert "SECRET-CONTENT-MARKER" not in "\n".join(text)  # not in log records
    for e in events.events:
        assert "SECRET-CONTENT-MARKER" not in str(e)  # not in events


def test_nfr_003_api_backward_compatible(tmp_path: Path) -> None:
    import backend.filemanagement as fm

    for name in _PUBLIC_API:
        assert hasattr(fm, name), f"public API name {name!r} missing"
    # Adding optional parameters must not break existing callers: everything
    # after `repository` in FileService.__init__ is optional.
    sig = inspect.signature(FileService.__init__)
    for name, param in list(sig.parameters.items())[2:]:
        assert param.default is not inspect.Parameter.empty, f"parameter {name!r} is not optional"
    # The avatar URL contract: satisfies user-management's profile_picture_url
    # validation without a spec amendment.
    svc = make_service(
        SqliteFileRepository(db_url(tmp_path)),
        backend=InMemoryStorageBackend(),
        event_bus=None,
        registry=isolated_registry(),
    )
    r = svc.upload_avatar("alice", png_bytes(32, 32))
    assert r.url.startswith("https://")
    from backend.usermanagement import UserCreate

    user = UserCreate(
        username="alice",
        email="alice@example.com",
        password="correct-horse-battery-1",
        profile_picture_url=r.url,
    )
    assert user.profile_picture_url == r.url


def test_nfr_004_concurrent_repository_safety(tmp_path: Path) -> None:
    repo = SqliteFileRepository(db_url(tmp_path))
    svc = make_service(repo, backend=InMemoryStorageBackend(), event_bus=None, registry=isolated_registry())
    barrier = threading.Barrier(8)
    errors: list[Exception] = []

    def worker(i: int) -> None:
        try:
            barrier.wait(timeout=10)
            r = svc.upload(text_bytes(100 + i), key=f"nfr004-{i}")
            assert svc.get_file(r.key).key == r.key
            svc.delete(r.key)
        except Exception as e:  # collected and asserted
            errors.append(e)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=30)
    assert not errors
    assert svc.list_files() == []
    # The DB file's parent directory is auto-created.
    nested = tmp_path / "nfr004" / "db"
    p = str(nested / "files.db").replace("\\", "/")
    prefix = "sqlite:////" if p.startswith("/") else "sqlite:///"
    SqliteFileRepository(f"{prefix}{p}")
    assert (nested / "files.db").exists()


def test_nfr_005_operations_logged(tmp_path: Path, log_records: list[Any]) -> None:
    marker = b"SECRET-LOG-MARKER-" * 32
    svc = make_service(
        SqliteFileRepository(db_url(tmp_path)),
        backend=InMemoryStorageBackend(),
        event_bus=None,
        registry=isolated_registry(),
    )
    svc.upload(marker)
    with pytest.raises(FileValidationError):
        svc.upload(b"")
    with pytest.raises(FileManagementNotFoundError):
        svc.download("missing-key")
    text = [str(m) for m in log_records]
    assert any("upload" in t and ">>" in t for t in text), "no entry trace for upload"
    assert any("upload" in t and "<<" in t for t in text), "no exit trace for upload"
    # Validation failures are logged with the failure kind.
    assert any("zero_byte_file" in t or "FileValidationError" in t for t in text)
    # Domain errors are logged with their type.
    assert any("FileManagementNotFoundError" in t for t in text)
    # File content never appears in log records.
    assert "SECRET-LOG-MARKER" not in "\n".join(text)
