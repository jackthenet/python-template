"""Unit tests for the filemanagement feature (docs/specs/file-management.md).

One test function per edge case EDGE-001 .. EDGE-019.
"""

from __future__ import annotations

import io
import threading
from pathlib import Path

import pytest
from backend.filemanagement import (
    FileDeleted,
    FileService,
    FileTooLargeError,
    FileValidationError,
    FileValidationFailed,
    InMemoryStorageBackend,
    SqliteFileRepository,
    StorageError,
)

from backend.settings import SettingsRegistry
from tests.filemanagement_test_helpers import (
    EventCollector,
    FailingVariantBackend,
    RaisingPublisher,
    isolated_registry,
    make_service,
    png_bytes,
    text_bytes,
    truncated_png,
)


def test_edge_001_source_not_found(tmp_path: Path, service: FileService, events: EventCollector) -> None:
    with pytest.raises(FileValidationError) as exc:
        service.upload(str(tmp_path / "missing.txt"))
    assert exc.value.reason == "source_not_found"
    assert len(events.of_type(FileValidationFailed)) == 1


def test_edge_002_source_not_a_file(tmp_path: Path, service: FileService, events: EventCollector) -> None:
    d = tmp_path / "adir"
    d.mkdir()
    with pytest.raises(FileValidationError) as exc:
        service.upload(str(d))
    assert exc.value.reason == "source_not_a_file"
    assert len(events.of_type(FileValidationFailed)) == 1


def test_edge_003_stream_exceeds_limit_mid_stream(
    tmp_path: Path,
    service: FileService,
    repo: SqliteFileRepository,
    registry: SettingsRegistry,
) -> None:
    registry.set_value("filemanagement.max_file_size", 4096)
    stream = io.BytesIO(text_bytes(100_000))
    with pytest.raises(FileTooLargeError):
        service.upload(stream)
    assert list(repo.list_by_namespace(None)) == []  # no partial state


def test_edge_004_key_null_byte(service: FileService) -> None:
    with pytest.raises(FileValidationError) as exc:
        service.upload(text_bytes(), key="bad\0key")
    assert exc.value.reason == "invalid_key"


def test_edge_005_key_absolute_path(service: FileService) -> None:
    with pytest.raises(FileValidationError) as exc:
        service.upload(text_bytes(), key="/etc/passwd")
    assert exc.value.reason == "invalid_key"


def test_edge_006_record_without_content(
    tmp_path: Path,
    repo: SqliteFileRepository,
    backend: InMemoryStorageBackend,
) -> None:
    svc = make_service(repo, backend=backend, event_bus=None, registry=isolated_registry())
    r = svc.upload(text_bytes())
    backend.delete(r.key)  # simulate an inconsistent store: the content is gone
    with pytest.raises(StorageError) as exc:
        svc.download(r.key)
    assert exc.value.reason == "not_found"
    assert repo.get_by_key(r.key) is not None  # the record is not auto-deleted


def test_edge_007_delete_missing_content(
    tmp_path: Path,
    repo: SqliteFileRepository,
    backend: InMemoryStorageBackend,
    events: EventCollector,
) -> None:
    svc = make_service(repo, backend=backend, event_bus=events, registry=isolated_registry())
    r = svc.upload(text_bytes())
    backend.delete(r.key)  # the storage content is already missing
    svc.delete(r.key)  # the storage delete is a no-op; the record is still deleted
    assert repo.get_by_key(r.key) is None
    assert len(events.of_type(FileDeleted)) == 1


def test_edge_008_list_empty_store(service: FileService) -> None:
    assert service.list_files() == []


def test_edge_009_list_offset_beyond_end(service: FileService) -> None:
    [service.upload(text_bytes(100), key=f"e009-{i}") for i in range(3)]
    assert service.list_files(limit=10, offset=100) == []


def test_edge_010_sequential_key_replacement(service: FileService, repo: SqliteFileRepository) -> None:
    r1 = service.upload(text_bytes(100), key="e010")
    data = text_bytes(200)
    r2 = service.upload(data, key="e010")
    assert r2.id != r1.id  # a new record id
    assert r2.size == len(data)
    assert len([r for r in repo.list_by_namespace(None) if r.key == "e010"]) == 1
    assert service.download("e010") == data


def test_edge_011_dangling_avatar_mapping(
    tmp_path: Path,
    repo: SqliteFileRepository,
    backend: InMemoryStorageBackend,
) -> None:
    svc = make_service(repo, backend=backend, event_bus=None, registry=isolated_registry())
    r = svc.upload_avatar("alice", png_bytes(32, 32))
    # Simulate a dangling mapping: the file (and its variants) are deleted out of band.
    for rec in [rec for rec in repo.list_by_namespace("avatars") if r.file_id in (rec.id, rec.variant_of)]:
        repo.delete(rec.id)
    avatar = svc.get_avatar("alice")
    assert avatar.is_default is True  # the default avatar is returned
    assert repo.get_user_avatar("alice") is None  # the dangling mapping is cleared


def test_edge_012_truncated_png_decode_failure(service: FileService) -> None:
    with pytest.raises(FileValidationError) as exc:
        service.upload_avatar("alice", truncated_png())
    assert exc.value.reason == "image_decode_failed"


def test_edge_013_variant_generation_failure_rollback(
    tmp_path: Path,
    repo: SqliteFileRepository,
) -> None:
    failing = FailingVariantBackend()
    svc = make_service(repo, backend=failing, event_bus=None, registry=isolated_registry())
    with pytest.raises(StorageError) as exc:
        svc.upload_avatar("alice", png_bytes(128, 128))  # the 64/256 variants fail
    assert exc.value.reason == "variant_generation"
    assert list(repo.list_by_namespace(None)) == []  # no main file, no variants, no records
    assert not any(failing.inner.exists(k) for k in failing.put_keys)  # no content remains


def test_edge_014_publisher_raises(
    tmp_path: Path,
    repo: SqliteFileRepository,
    backend: InMemoryStorageBackend,
) -> None:
    publisher = RaisingPublisher()
    svc = make_service(repo, backend=backend, event_bus=publisher, registry=isolated_registry())
    with pytest.raises(RuntimeError):
        svc.upload(text_bytes())
    assert list(repo.list_by_namespace(None)) != []  # the operation is already committed


def test_edge_015_repo_creates_parent_dir(tmp_path: Path) -> None:
    nested = tmp_path / "a" / "b"  # the parent directory does not exist
    p = str(nested / "files.db").replace("\\", "/")
    prefix = "sqlite:////" if p.startswith("/") else "sqlite:///"
    SqliteFileRepository(f"{prefix}{p}")
    assert (nested / "files.db").exists()  # the parent directory is auto-created


def test_edge_016_in_memory_isolation() -> None:
    a = InMemoryStorageBackend()
    b = InMemoryStorageBackend()
    a.put("k", b"data")
    assert a.exists("k")
    assert not b.exists("k")  # two instances are isolated


def test_edge_017_concurrent_download_upload(
    tmp_path: Path,
    repo: SqliteFileRepository,
    backend: InMemoryStorageBackend,
) -> None:
    svc = make_service(repo, backend=backend, event_bus=None, registry=isolated_registry())
    key = "e017"
    old = text_bytes(1024)
    new = text_bytes(2048)
    svc.upload(old, key=key)
    barrier = threading.Barrier(2)
    errors: list[Exception] = []
    results: list[bytes] = []

    def uploader() -> None:
        try:
            barrier.wait(timeout=10)
            svc.upload(new, key=key)
        except Exception as e:
            errors.append(e)

    def downloader() -> None:
        try:
            barrier.wait(timeout=10)
            results.append(svc.download(key))
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=uploader), threading.Thread(target=downloader)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=30)
    assert not errors
    assert results[0] in (old, new)  # a complete file, never partial


def test_edge_018_dimensions_boundary_allowed(service: FileService) -> None:
    r = service.upload_avatar("alice", png_bytes(4096, 4096))
    assert r.file_id is not None  # the boundary is inclusive


def test_edge_019_size_boundary_allowed(service: FileService, registry: SettingsRegistry) -> None:
    limit = 2048
    registry.set_value("filemanagement.max_file_size", limit)
    r = service.upload(text_bytes(limit))  # size == limit is OK
    assert r.size == limit
