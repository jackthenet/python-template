"""Property tests for the filemanagement feature (docs/specs/file-management.md).

Hypothesis-based tests for the invariants INV-001 .. INV-008.
"""

from __future__ import annotations

import hashlib
import io
import re
import threading
from pathlib import Path
from uuid import uuid4

import pytest
from filemanagement_test_helpers import (
    EventCollector,
    FailingAddRepository,
    FailingPutBackend,
    db_url,
    isolated_registry,
    make_service,
    png_bytes,
    text_bytes,
)
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from hypothesis.strategies import SearchStrategy

from backend.filemanagement import (
    AVATAR_VARIANT_SIZES,
    AvatarError,
    FileDeleted,
    FileDownloaded,
    FileUploaded,
    FileValidationError,
    FileValidationFailed,
    InMemoryStorageBackend,
    LocalDiskStorageBackend,
    SqliteFileRepository,
    StorageError,
)

_MAX_EXAMPLES = 20


def _content() -> SearchStrategy[bytes]:
    """Non-empty ASCII content of varying size (allowed by the default policy)."""
    return st.lists(st.sampled_from(b"abcdefghijklmnopqrstuvwxyz0123456789"), min_size=1, max_size=4096).map(bytes)


@settings(max_examples=_MAX_EXAMPLES, suppress_health_check=[HealthCheck.too_slow, HealthCheck.function_scoped_fixture])
@given(content=_content(), fault=st.sampled_from(["none", "storage", "metadata"]))
def test_inv_001_no_partial_state_on_failure(tmp_path: Path, content: bytes, fault: str) -> None:
    key = str(uuid4())
    repo = SqliteFileRepository(db_url(tmp_path, f"inv001-{uuid4()}.db"))
    mem = InMemoryStorageBackend()
    if fault == "storage":
        svc = make_service(repo, backend=FailingPutBackend(), event_bus=None, registry=isolated_registry())
        with pytest.raises(StorageError):
            svc.upload(content, key=key)
        assert list(repo.list_by_namespace(None)) == []  # no metadata record
    elif fault == "metadata":
        svc = make_service(FailingAddRepository(), backend=mem, event_bus=None, registry=isolated_registry())
        with pytest.raises(StorageError):
            svc.upload(content, key=key)
        assert not mem.exists(key)  # no orphaned storage content
        assert list(repo.list_by_namespace(None)) == []
    else:
        svc = make_service(repo, backend=mem, event_bus=None, registry=isolated_registry())
        r = svc.upload(content, key=key)
        assert r.size == len(content)
        assert mem.exists(key)


@settings(max_examples=_MAX_EXAMPLES, suppress_health_check=[HealthCheck.too_slow, HealthCheck.function_scoped_fixture])
@given(contents=st.lists(_content(), min_size=2, max_size=4))
def test_inv_002_concurrent_same_key_last_write_wins(tmp_path: Path, contents: list[bytes]) -> None:
    key = str(uuid4())
    repo = SqliteFileRepository(db_url(tmp_path, f"inv002-{uuid4()}.db"))
    backend = InMemoryStorageBackend()
    svc = make_service(repo, backend=backend, event_bus=None, registry=isolated_registry())
    barrier = threading.Barrier(len(contents))
    errors: list[Exception] = []

    def worker(data: bytes) -> None:
        try:
            barrier.wait(timeout=10)
            svc.upload(data, key=key)
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=worker, args=(c,)) for c in contents]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=30)
    assert not errors
    records = [r for r in repo.list_by_namespace(None) if r.key == key]
    assert len(records) == 1  # exactly one file record
    assert backend.get(key).read() in contents  # last-write-wins


@settings(max_examples=_MAX_EXAMPLES, suppress_health_check=[HealthCheck.too_slow, HealthCheck.function_scoped_fixture])
@given(content=_content())
def test_inv_003_metadata_matches_content(tmp_path: Path, content: bytes) -> None:
    key = str(uuid4())
    repo = SqliteFileRepository(db_url(tmp_path, f"inv003-{uuid4()}.db"))
    backend = InMemoryStorageBackend()
    svc = make_service(repo, backend=backend, event_bus=None, registry=isolated_registry())
    svc.upload(content, key=key)
    rec = repo.get_by_key(key)
    stored = backend.get(key).read()
    assert rec.size == len(stored)
    assert rec.sha256 == hashlib.sha256(stored).hexdigest()
    assert rec.detected_mime_type == "text/plain"


@settings(
    max_examples=_MAX_EXAMPLES,
    deadline=500,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.function_scoped_fixture],
)
@given(ops=st.lists(st.sampled_from(["upload", "replace", "delete"]), min_size=1, max_size=8))
def test_inv_004_at_most_one_avatar_per_user(tmp_path: Path, ops: list[str]) -> None:
    repo = SqliteFileRepository(db_url(tmp_path, f"inv004-{uuid4()}.db"))
    svc = make_service(repo, backend=InMemoryStorageBackend(), event_bus=None, registry=isolated_registry())
    for op in ops:
        try:
            if op == "upload":
                svc.upload_avatar("alice", png_bytes(32, 32))
            elif op == "replace":
                svc.replace_avatar("alice", png_bytes(48, 48))
            else:
                svc.delete_avatar("alice")
        except AvatarError:
            pass  # upload on existing / replace on missing: the state is unchanged
    file_id = repo.get_user_avatar("alice")
    if file_id is None:
        assert svc.get_avatar("alice").is_default is True
    else:
        assert repo.get_by_id(file_id) is not None  # the mapping points to an existing file


@settings(max_examples=_MAX_EXAMPLES, suppress_health_check=[HealthCheck.too_slow, HealthCheck.function_scoped_fixture])
@given(size=st.integers(min_value=8, max_value=256))
def test_inv_005_avatar_url_format(tmp_path: Path, size: int) -> None:
    repo = SqliteFileRepository(db_url(tmp_path, f"inv005-{uuid4()}.db"))
    svc = make_service(repo, backend=InMemoryStorageBackend(), event_bus=None, registry=isolated_registry())
    r = svc.upload_avatar("alice", png_bytes(size, size))
    assert r.url.startswith("https://")
    assert re.fullmatch(
        r"https://[a-z0-9.-]+/files/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
        r.url,
    )


@settings(max_examples=_MAX_EXAMPLES, suppress_health_check=[HealthCheck.too_slow, HealthCheck.function_scoped_fixture])
@given(n=st.integers(min_value=1, max_value=4))
def test_inv_006_event_correspondence(tmp_path: Path, n: int) -> None:
    events = EventCollector()
    repo = SqliteFileRepository(db_url(tmp_path, f"inv006-{uuid4()}.db"))
    svc = make_service(repo, backend=InMemoryStorageBackend(), event_bus=events, registry=isolated_registry())
    for i in range(n):
        svc.upload(text_bytes(100 + i), key=f"inv006-{uuid4()}")
    assert len(events.of_type(FileUploaded)) == n
    for rec in list(repo.list_by_namespace(None)):
        svc.download(rec.key)
    assert len(events.of_type(FileDownloaded)) == n
    for rec in list(repo.list_by_namespace(None)):
        svc.delete(rec.key)
    assert len(events.of_type(FileDeleted)) == n
    assert len(events.events) == n * 3  # no other events
    with pytest.raises(FileValidationError):
        svc.upload(b"")
    assert len(events.of_type(FileValidationFailed)) == 1
    assert len(events.events) == n * 3 + 1  # only FileValidationFailed on failure


@settings(max_examples=_MAX_EXAMPLES, suppress_health_check=[HealthCheck.too_slow, HealthCheck.function_scoped_fixture])
@given(key=st.from_regex(r"[A-Za-z0-9][A-Za-z0-9._-]{0,20}", fullmatch=True))
def test_inv_007_key_containment(tmp_path: Path, key: str) -> None:
    root = tmp_path / f"inv007-{uuid4()}"
    root.mkdir()
    backend = LocalDiskStorageBackend(root)
    backend.put(key, b"data")
    p = root / key
    assert p.resolve().is_relative_to(root.resolve())  # the resolved path is inside the root
    assert backend.exists(key)


@settings(max_examples=_MAX_EXAMPLES, suppress_health_check=[HealthCheck.too_slow, HealthCheck.function_scoped_fixture])
@given(size=st.sampled_from([32, 64, 128, 256]))
def test_inv_008_variant_consistency(tmp_path: Path, size: int) -> None:
    from PIL import Image

    repo = SqliteFileRepository(db_url(tmp_path, f"inv008-{uuid4()}.db"))
    backend = InMemoryStorageBackend()
    svc = make_service(repo, backend=backend, event_bus=None, registry=isolated_registry())
    r = svc.upload_avatar("alice", png_bytes(size, size))
    variants = [rec for rec in repo.list_by_namespace("avatars") if rec.variant_of == r.file_id]
    assert len(variants) == len(AVATAR_VARIANT_SIZES)
    sides: set[int] = set()
    for rec in variants:
        with Image.open(io.BytesIO(backend.get(rec.key).read())) as img:
            assert img.format == "PNG"
            sides.add(max(img.size))
    assert sides == {64, 256}
    svc.delete_avatar("alice")
    assert [rec for rec in repo.list_by_namespace("avatars") if rec.variant_of == r.file_id] == []
    assert not any(backend.exists(rec.key) for rec in variants)  # the variants are deleted
