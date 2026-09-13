"""Acceptance tests for the filemanagement feature (docs/specs/file-management.md).

One test function per acceptance criterion AC-001 .. AC-055.
"""

from __future__ import annotations

import io
import os
import re
import threading
from pathlib import Path
from typing import Any
from uuid import UUID

import pytest
from backend.filemanagement import (
    AVATAR_VARIANT_SIZES,
    AvatarDeleted,
    AvatarError,
    AvatarUploaded,
    FileDeleted,
    FileDownloaded,
    FileManagementError,
    FileManagementNotFoundError,
    FileService,
    FileTooLargeError,
    FileTypeNotAllowedError,
    FileUploaded,
    FileValidationError,
    FileValidationFailed,
    InMemoryStorageBackend,
    LocalDiskStorageBackend,
    SqliteFileRepository,
    StorageError,
    register_settings,
)
from logging_test_helpers import run_python

from backend.settings import SettingsRegistry
from tests.filemanagement_test_helpers import (
    DictFileRepository,
    FailingAddRepository,
    FailingPutBackend,
    db_url,
    gif_bytes,
    isolated_registry,
    jpeg_bytes,
    make_service,
    png_bytes,
    text_bytes,
    tiff_bytes,
    truncated_png,
)

DEFAULT_MAX_FILE_SIZE = 10485760  # 10 MB
DEFAULT_AVATAR_MAX_SIZE = 2097152  # 2 MB


def test_ac_001_upload_bytes_round_trip(service: FileService) -> None:
    payload = text_bytes(1024)
    r = service.upload(payload)
    assert r.size == len(payload)
    assert r.detected_mime_type == "text/plain"
    assert re.fullmatch(r"[0-9a-f]{64}", r.sha256)
    assert r.namespace == "general"
    UUID(r.key)
    assert service.get_file(r.key).key == r.key


def test_ac_002_upload_file_path(tmp_path: Path, service: FileService) -> None:
    p = tmp_path / "report.txt"
    data = text_bytes(2048)
    p.write_bytes(data)
    r = service.upload(str(p))
    assert r.size == len(data)
    assert r.original_filename == "report.txt"


def test_ac_003_upload_file_like_stream(service: FileService) -> None:
    size = 4096
    stream = io.BytesIO(text_bytes(size))
    r = service.upload(stream)
    assert r.size == size
    assert stream.read() == b""  # the stream is fully consumed


@pytest.mark.parametrize("shape", ["bytes", "stream", "path"])
def test_ac_004_zero_byte_rejected(tmp_path: Path, service: FileService, repo: SqliteFileRepository, events: Any, shape: str) -> None:
    if shape == "bytes":
        source: str | bytes | io.BytesIO = b""
    elif shape == "stream":
        source = io.BytesIO(b"")
    else:
        empty = tmp_path / "empty.txt"
        empty.write_bytes(b"")
        source = str(empty)
    with pytest.raises(FileValidationError) as exc:
        service.upload(source)
    assert exc.value.reason == "zero_byte_file"
    assert len(events.of_type(FileValidationFailed)) == 1
    assert list(repo.list_by_namespace(None)) == []


def test_ac_005_general_size_limit(service: FileService, repo: SqliteFileRepository) -> None:
    payload = text_bytes(10 * 1024 * 1024 + 1)
    with pytest.raises(FileTooLargeError) as exc:
        service.upload(payload)
    assert exc.value.size == len(payload)
    assert exc.value.limit == DEFAULT_MAX_FILE_SIZE
    assert list(repo.list_by_namespace(None)) == []


def test_ac_006_avatar_size_limit(service: FileService) -> None:
    with pytest.raises(FileTooLargeError) as exc:
        service.upload(text_bytes(2 * 1024 * 1024 + 1), namespace="avatars")
    assert exc.value.limit == DEFAULT_AVATAR_MAX_SIZE


def test_ac_007_live_max_file_size(service: FileService, registry: SettingsRegistry) -> None:
    limit = 4096
    registry.set_value("filemanagement.max_file_size", limit)
    with pytest.raises(FileTooLargeError) as exc:
        service.upload(text_bytes(5000))
    assert exc.value.limit == limit


def test_ac_008_magic_byte_detection(service: FileService) -> None:
    r = service.upload(jpeg_bytes())
    assert r.detected_mime_type == "image/jpeg"


def test_ac_009_declared_type_conflict(service: FileService, events: Any) -> None:
    with pytest.raises(FileValidationError) as exc:
        service.upload(png_bytes(), declared_mime_type="image/jpeg")
    assert exc.value.reason == "type_conflict"
    assert len(events.of_type(FileValidationFailed)) == 1


def test_ac_010_filename_type_conflict(service: FileService, events: Any) -> None:
    with pytest.raises(FileValidationError) as exc:
        service.upload(jpeg_bytes(), original_filename="photo.png")
    assert exc.value.reason == "type_conflict"
    assert len(events.of_type(FileValidationFailed)) == 1


def test_ac_011_type_not_allowed(service: FileService, events: Any) -> None:
    with pytest.raises(FileTypeNotAllowedError) as exc:
        service.upload(tiff_bytes())
    assert exc.value.detected == "image/tiff"
    assert "text/plain" in exc.value.allowed
    assert len(events.of_type(FileValidationFailed)) == 1


def test_ac_012_live_allowed_types(service: FileService, registry: SettingsRegistry) -> None:
    registry.set_value("filemanagement.allowed_types", ["image/tiff"])
    r = service.upload(tiff_bytes())
    assert r.detected_mime_type == "image/tiff"


def test_ac_013_generated_uuid_key(service: FileService) -> None:
    r = service.upload(text_bytes())
    UUID(r.key)  # a canonical UUID string


def test_ac_014_caller_key(service: FileService) -> None:
    r = service.upload(text_bytes(), key="report-2026.pdf")
    assert r.key == "report-2026.pdf"
    assert service.get_file("report-2026.pdf").key == "report-2026.pdf"


def test_ac_015_traversal_key_rejected(service: FileService, repo: SqliteFileRepository, events: Any) -> None:
    with pytest.raises(FileValidationError) as exc:
        service.upload(text_bytes(), key="a/b")
    assert exc.value.reason == "invalid_key"
    assert len(events.of_type(FileValidationFailed)) == 1
    assert list(repo.list_by_namespace(None)) == []


def test_ac_016_storage_failure_rollback(tmp_path: Path) -> None:
    failing = FailingPutBackend()
    repo = SqliteFileRepository(db_url(tmp_path))
    svc = make_service(repo, backend=failing, event_bus=None, registry=isolated_registry())
    with pytest.raises(StorageError):
        svc.upload(text_bytes())
    assert failing.put_attempts >= 1
    assert list(repo.list_by_namespace(None)) == []  # no metadata record


def test_ac_017_metadata_failure_rollback(tmp_path: Path, backend: InMemoryStorageBackend) -> None:
    failing = FailingAddRepository()
    svc = make_service(failing, backend=backend, event_bus=None, registry=isolated_registry())
    with pytest.raises(StorageError) as exc:
        svc.upload(text_bytes(), key="k1")
    assert exc.value.reason == "io"
    assert failing.add_attempts == 1
    assert not backend.exists("k1")  # the written content is rolled back


def test_ac_018_concurrent_same_key_last_write_wins(
    tmp_path: Path, repo: SqliteFileRepository, backend: InMemoryStorageBackend
) -> None:
    svc = make_service(repo, backend=backend, event_bus=None, registry=isolated_registry())
    key = "concurrent-key"
    a = text_bytes(1024)
    b = text_bytes(2048)
    barrier = threading.Barrier(2)
    errors: list[Exception] = []

    def worker(data: bytes) -> None:
        try:
            barrier.wait(timeout=10)
            svc.upload(data, key=key)
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=worker, args=(a,)), threading.Thread(target=worker, args=(b,))]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=30)
    assert not errors
    records = list(repo.list_by_namespace(None))
    assert len(records) == 1  # exactly one file record
    content = backend.get(key).read()
    assert content in (a, b)  # last-write-wins


def test_ac_019_download_bytes(service: FileService, events: Any) -> None:
    r = service.upload(text_bytes(3072))
    assert service.download(r.key) == text_bytes(3072)
    assert len(events.of_type(FileDownloaded)) == 1


def test_ac_020_open_stream(service: FileService, events: Any) -> None:
    r = service.upload(text_bytes(2048))
    with service.open(r.key) as stream:
        data = stream.read()
    assert data == text_bytes(2048)
    assert len(events.of_type(FileDownloaded)) == 1


def test_ac_021_download_missing(service: FileService) -> None:
    with pytest.raises(FileManagementNotFoundError):
        service.download("nope")
    with pytest.raises(FileManagementNotFoundError):
        service.open("nope")


def test_ac_022_delete(service: FileService, repo: SqliteFileRepository, backend: InMemoryStorageBackend, events: Any) -> None:
    r = service.upload(text_bytes())
    service.delete(r.key)
    assert repo.get_by_key(r.key) is None
    assert not backend.exists(r.key)
    assert len(events.of_type(FileDeleted)) == 1
    with pytest.raises(FileManagementNotFoundError):
        service.get_file(r.key)


def test_ac_023_delete_missing(service: FileService) -> None:
    with pytest.raises(FileManagementNotFoundError):
        service.delete("nope")


def test_ac_024_metadata_fields(service: FileService, repo: SqliteFileRepository) -> None:
    payload = text_bytes(1024)
    r = service.upload(payload, original_filename="a.txt", uploader="u1")
    rec = repo.get_by_key(r.key)
    assert rec is not None
    assert rec.id == r.id
    assert rec.key == r.key
    assert rec.original_filename == "a.txt"
    assert rec.detected_mime_type == "text/plain"
    assert rec.size == len(payload)
    assert re.fullmatch(r"[0-9a-f]{64}", rec.sha256)
    assert rec.namespace == "general"
    assert rec.uploader == "u1"
    assert rec.variant_of is None
    assert rec.created_at.tzinfo is not None  # UTC
    assert rec.updated_at.tzinfo is not None


def test_ac_025_persistence_across_instances(tmp_path: Path) -> None:
    db = db_url(tmp_path)
    svc1 = make_service(SqliteFileRepository(db), backend=InMemoryStorageBackend(), event_bus=None, registry=isolated_registry())
    r = svc1.upload(text_bytes())
    svc2 = make_service(SqliteFileRepository(db), backend=InMemoryStorageBackend(), event_bus=None, registry=isolated_registry())
    assert svc2.get_file(r.key).key == r.key


def test_ac_026_service_with_fake_repository(tmp_path: Path) -> None:
    fake = DictFileRepository()
    svc = make_service(fake, backend=InMemoryStorageBackend(), event_bus=None, registry=isolated_registry())
    r = svc.upload(text_bytes())
    assert svc.get_file(r.key).key == r.key
    assert svc.download(r.key) == text_bytes()
    assert len(svc.list_files()) == 1
    svc.delete(r.key)
    assert svc.list_files() == []


def test_ac_027_get_file_and_list_pagination(service: FileService) -> None:
    n_docs = 12
    limit = 10
    offset = 5
    doc_keys = [service.upload(text_bytes(100), key=f"doc-{i}", namespace="docs").key for i in range(n_docs)]
    [service.upload(text_bytes(100), key=f"oth-{i}", namespace="other") for i in range(3)]
    assert service.get_file(doc_keys[0]).key == doc_keys[0]
    page = service.list_files(namespace="docs", limit=limit, offset=0)
    assert len(page) == limit
    assert all(f.namespace.startswith("docs") for f in page)
    rest = service.list_files(namespace="docs", limit=limit, offset=offset)
    assert len(rest) == n_docs - offset  # skips the first 5


def test_ac_028_list_invalid_pagination(service: FileService) -> None:
    with pytest.raises(ValueError):
        service.list_files(limit=0)
    with pytest.raises(ValueError):
        service.list_files(offset=-1)


def test_ac_029_default_local_backend(tmp_path: Path) -> None:
    registry = isolated_registry()
    register_settings(registry)
    registry.set_value("filemanagement.storage_root", str(tmp_path / "files"))
    svc = FileService(
        SqliteFileRepository(db_url(tmp_path)),
        backend=None,  # default wiring: local disk from the live setting
        event_bus=None,
        settings_registry=registry,
    )
    r = svc.upload(text_bytes())
    assert (tmp_path / "files" / r.key).is_file()


def test_ac_030_in_memory_backend(tmp_path: Path) -> None:
    backend = InMemoryStorageBackend()
    svc = make_service(SqliteFileRepository(db_url(tmp_path)), backend=backend, event_bus=None, registry=isolated_registry())
    r = svc.upload(text_bytes())
    assert svc.download(r.key) == text_bytes()
    svc.delete(r.key)
    assert not backend.exists(r.key)


def test_ac_031_symlink_rejected(tmp_path: Path) -> None:
    root = tmp_path / "files"
    root.mkdir()
    outside = tmp_path / "outside.txt"
    outside.write_text("outside")
    try:
        os.symlink(outside, root / "mykey")
    except OSError:
        pytest.skip("symlinks not available on this host")
    backend = LocalDiskStorageBackend(root)
    with pytest.raises(StorageError) as exc:
        backend.put("mykey", b"data")
    assert exc.value.reason == "symlink"


def test_ac_032_path_escape_rejected(tmp_path: Path) -> None:
    root = tmp_path / "files"
    root.mkdir()
    backend = LocalDiskStorageBackend(root)
    with pytest.raises(StorageError) as exc:
        backend.put("../evil", b"data")
    assert exc.value.reason == "path_escape"
    assert not (tmp_path / "evil").exists()  # nothing written outside the root


def test_ac_033_upload_avatar(service: FileService, events: Any) -> None:
    r = service.upload_avatar("alice", png_bytes(64, 64))
    assert r.is_default is False
    assert r.file_id is not None
    assert re.fullmatch(r"https://files\.example\.com/files/[0-9a-f-]{36}", r.url)
    assert service.get_avatar("alice").url == r.url
    assert len(events.of_type(AvatarUploaded)) == 1


def test_ac_034_upload_avatar_existing(service: FileService) -> None:
    service.upload_avatar("alice", png_bytes(32, 32))
    with pytest.raises(AvatarError) as exc:
        service.upload_avatar("alice", png_bytes(32, 32))
    assert exc.value.operation == "upload"


def test_ac_035_replace_avatar(service: FileService, repo: SqliteFileRepository, events: Any) -> None:
    old = service.upload_avatar("alice", png_bytes(32, 32))
    new = service.replace_avatar("alice", png_bytes(48, 48))
    assert new.file_id != old.file_id
    assert repo.get_by_id(old.file_id) is None  # the old file is deleted
    assert service.get_avatar("alice").url == new.url
    assert len(events.of_type(AvatarUploaded)) == 1


def test_ac_036_replace_avatar_missing(service: FileService) -> None:
    with pytest.raises(AvatarError) as exc:
        service.replace_avatar("bob", png_bytes(32, 32))
    assert exc.value.operation == "replace"


def test_ac_037_delete_avatar(service: FileService, repo: SqliteFileRepository, events: Any) -> None:
    r = service.upload_avatar("alice", png_bytes(32, 32))
    service.delete_avatar("alice")
    assert repo.get_by_id(r.file_id) is None  # the file is deleted
    assert repo.get_user_avatar("alice") is None  # the mapping is cleared
    assert len(events.of_type(AvatarDeleted)) == 1
    assert service.get_avatar("alice").is_default is True


def test_ac_038_delete_avatar_noop(service: FileService, events: Any) -> None:
    service.delete_avatar("bob")  # no error
    assert events.events == []  # no event


def test_ac_039_avatar_url_format(service: FileService) -> None:
    r = service.upload_avatar("alice", png_bytes(32, 32))
    assert re.fullmatch(
        r"https://files\.example\.com/files/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
        r.url,
    )


def test_ac_040_live_avatar_base_url(service: FileService, registry: SettingsRegistry) -> None:
    registry.set_value("filemanagement.avatar_base_url", "cdn.example.org")
    r = service.upload_avatar("alice", png_bytes(32, 32))
    assert r.url.startswith("https://cdn.example.org/files/")


def test_ac_041_avatar_undecodable(service: FileService, events: Any) -> None:
    with pytest.raises(FileValidationError) as exc:
        service.upload_avatar("alice", truncated_png())
    assert exc.value.reason == "image_decode_failed"
    assert len(events.of_type(FileValidationFailed)) == 1


def test_ac_042_avatar_dimensions_exceeded(service: FileService, events: Any) -> None:
    with pytest.raises(FileValidationError) as exc:
        service.upload_avatar("alice", png_bytes(5000, 5000))
    assert exc.value.reason == "dimensions_exceeded"
    assert (exc.value.width, exc.value.height) == (5000, 5000)
    assert len(events.of_type(FileValidationFailed)) == 1


def test_ac_043_avatar_type_not_allowed(service: FileService) -> None:
    with pytest.raises(FileTypeNotAllowedError):
        service.upload_avatar("alice", gif_bytes())


def test_ac_044_get_avatar_default(service: FileService) -> None:
    r = service.get_avatar("bob")
    assert r.is_default is True
    assert r.file_id is None
    assert r.url == "https://files.example.com/files/default-avatar"


def test_ac_045_avatar_variants_created(service: FileService, repo: SqliteFileRepository, backend: InMemoryStorageBackend) -> None:
    from PIL import Image

    r = service.upload_avatar("alice", png_bytes(128, 128))
    records = list(repo.list_by_namespace("avatars"))
    variants = [rec for rec in records if rec.variant_of == r.file_id]
    assert len(variants) == len(AVATAR_VARIANT_SIZES)
    sides: set[int] = set()
    for rec in variants:
        content = backend.get(rec.key).read()
        with Image.open(io.BytesIO(content)) as img:
            assert img.format == "PNG"
            sides.add(max(img.size))
        assert rec.detected_mime_type == "image/png"
        assert rec.namespace == "avatars"
        assert re.fullmatch(r"[0-9a-f]{64}", rec.sha256)
    assert sides == {64, 256}


def test_ac_046_avatar_variants_replaced(service: FileService, repo: SqliteFileRepository) -> None:
    old = service.upload_avatar("alice", png_bytes(128, 128))
    new = service.replace_avatar("alice", png_bytes(64, 64))
    assert new.file_id != old.file_id
    assert repo.get_by_id(old.file_id) is None  # the old main file is deleted
    assert [rec for rec in repo.list_by_namespace("avatars") if rec.variant_of == old.file_id] == []
    new_records = [
        rec for rec in repo.list_by_namespace("avatars") if new.file_id in (rec.id, rec.variant_of)
    ]
    assert len(new_records) == len(AVATAR_VARIANT_SIZES) + 1  # the new main file and its variants


def test_ac_047_event_uploaded(service: FileService, events: Any) -> None:
    r = service.upload(text_bytes())
    uploaded = events.of_type(FileUploaded)
    assert len(uploaded) == 1
    assert uploaded[0].file_id == r.id
    assert uploaded[0].key == r.key
    assert uploaded[0].namespace == "general"
    assert uploaded[0].size == r.size

    service.upload_avatar("alice", png_bytes(32, 32))
    assert len(events.of_type(FileUploaded)) == 2 + len(AVATAR_VARIANT_SIZES)  # + main avatar and its variants
    assert len(events.of_type(AvatarUploaded)) == 1


def test_ac_048_event_downloaded_deleted(service: FileService, events: Any) -> None:
    r = service.upload(text_bytes())
    service.download(r.key)
    assert len(events.of_type(FileDownloaded)) == 1
    service.delete(r.key)
    assert len(events.of_type(FileDeleted)) == 1


def test_ac_049_event_validation_failed(service: FileService, events: Any) -> None:
    with pytest.raises(FileValidationError):
        service.upload(b"")
    failed = events.of_type(FileValidationFailed)
    assert len(failed) == 1
    assert failed[0].reason == "zero_byte_file"


def test_ac_050_no_publisher(tmp_path: Path) -> None:
    svc = make_service(
        SqliteFileRepository(db_url(tmp_path)), backend=InMemoryStorageBackend(), event_bus=None, registry=isolated_registry()
    )
    r = svc.upload(text_bytes())  # works normally without a publisher
    assert svc.download(r.key) == text_bytes()
    svc.delete(r.key)


def test_ac_051_error_hierarchy_context() -> None:
    assert issubclass(FileManagementNotFoundError, FileManagementError)
    assert issubclass(FileTooLargeError, FileManagementError)
    assert issubclass(FileTypeNotAllowedError, FileManagementError)
    assert issubclass(FileValidationError, FileManagementError)
    assert issubclass(StorageError, FileManagementError)
    assert issubclass(AvatarError, FileManagementError)

    not_found = FileManagementNotFoundError(key="k1")
    assert not_found.key == "k1"
    size, limit = 2000, 1000
    too_large = FileTooLargeError(key="k2", size=size, limit=limit)
    assert too_large.size == size and too_large.limit == limit
    not_allowed = FileTypeNotAllowedError(key=None, detected="image/tiff", allowed=frozenset({"text/plain"}))
    assert not_allowed.detected == "image/tiff" and not_allowed.allowed == frozenset({"text/plain"})
    validation = FileValidationError(key="k3", reason="zero_byte_file")
    assert validation.reason == "zero_byte_file"
    storage = StorageError(key="k4", reason="io")
    assert storage.key == "k4" and storage.reason == "io"
    avatar = AvatarError(user_id="alice", operation="upload")
    assert avatar.user_id == "alice" and avatar.operation == "upload"


def test_ac_052_register_settings() -> None:
    registry = isolated_registry()
    register_settings(registry)
    assert registry.has("filemanagement.storage_root")
    assert registry.has("filemanagement.max_file_size")
    assert registry.has("filemanagement.avatar_max_size")
    assert registry.has("filemanagement.allowed_types")
    assert registry.has("filemanagement.avatar_base_url")
    assert registry.get_value("filemanagement.storage_root") == "./data/files"
    assert registry.get_value("filemanagement.max_file_size") == DEFAULT_MAX_FILE_SIZE
    assert registry.get_value("filemanagement.avatar_max_size") == DEFAULT_AVATAR_MAX_SIZE
    assert registry.get_value("filemanagement.allowed_types") == [
        "application/octet-stream",
        "application/pdf",
        "application/zip",
        "text/plain",
        "text/csv",
        "image/png",
        "image/jpeg",
        "image/gif",
        "image/webp",
    ]
    assert registry.get_value("filemanagement.avatar_base_url") == "files.example.com"


def test_ac_053_unregistered_settings_defaults(tmp_path: Path) -> None:
    # No feature settings registered: the hardcoded defaults apply.
    svc = make_service(
        SqliteFileRepository(db_url(tmp_path)),
        backend=InMemoryStorageBackend(),
        event_bus=None,
        registry=isolated_registry(),
        register=False,
    )
    with pytest.raises(FileTooLargeError) as exc:
        svc.upload(text_bytes(10 * 1024 * 1024 + 1))
    assert exc.value.limit == DEFAULT_MAX_FILE_SIZE  # 10 MB default
    with pytest.raises(FileTypeNotAllowedError):
        svc.upload(tiff_bytes())  # default allowed types
    r = svc.upload_avatar("alice", png_bytes(32, 32))
    assert r.url.startswith("https://files.example.com/files/")  # default base URL


def test_ac_054_operations_traced(service: FileService, log_records: list[Any]) -> None:
    marker = b"SECRET-MARKER-" * 64
    service.upload(marker)
    text = [str(m) for m in log_records]
    assert any("upload" in t and ">>" in t for t in text), "no entry trace for upload"
    assert any("upload" in t and "<<" in t for t in text), "no exit trace for upload"
    assert "SECRET-MARKER" not in "\n".join(text)  # file content never logged


def test_ac_055_layout_convention() -> None:
    code = (
        "import os, tempfile\n"
        "from pathlib import Path\n"
        "os.chdir(tempfile.mkdtemp())\n"
        "from backend.filemanagement import FileService, SqliteFileRepository\n"
        "db = os.path.join(tempfile.mkdtemp(), 'files.db')\n"
        "svc = FileService(SqliteFileRepository('sqlite:///' + db.replace(os.sep, '/')))\n"
        "r = svc.upload(b'x' * 1024)\n"
        "assert (Path('data/files') / r.key).is_file(), 'file not stored under ./data/files'\n"
    )
    result = run_python(code)
    assert result.returncode == 0, result.stderr
