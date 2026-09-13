"""Integration tests for the filemanagement feature (docs/specs/file-management.md).

Multi-component interactions: service + repository + storage backend + events.
"""

from __future__ import annotations

import threading
from pathlib import Path

from filemanagement_test_helpers import (
    EventCollector,
    db_url,
    isolated_registry,
    make_service,
    png_bytes,
    text_bytes,
)

from backend.filemanagement import AVATAR_VARIANT_SIZES, InMemoryStorageBackend, SqliteFileRepository


def test_full_file_lifecycle(tmp_path: Path) -> None:
    """Upload → query → download → delete across service, repository, and storage."""
    events = EventCollector()
    repo = SqliteFileRepository(db_url(tmp_path))
    backend = InMemoryStorageBackend()
    svc = make_service(repo, backend=backend, event_bus=events, registry=isolated_registry())

    r = svc.upload(text_bytes(2048), original_filename="notes.txt")
    assert svc.get_file(r.key).key == r.key
    assert len(svc.list_files()) == 1
    assert svc.download(r.key) == text_bytes(2048)
    svc.delete(r.key)
    assert svc.list_files() == []
    assert repo.get_by_key(r.key) is None
    assert not backend.exists(r.key)


def test_avatar_lifecycle_with_variants(tmp_path: Path) -> None:
    """Avatar upload → variants → replace → delete across all components."""
    events = EventCollector()
    repo = SqliteFileRepository(db_url(tmp_path))
    backend = InMemoryStorageBackend()
    svc = make_service(repo, backend=backend, event_bus=events, registry=isolated_registry())

    r = svc.upload_avatar("alice", png_bytes(128, 128))
    variants = [rec for rec in repo.list_by_namespace("avatars") if rec.variant_of == r.file_id]
    assert len(variants) == len(AVATAR_VARIANT_SIZES)
    new = svc.replace_avatar("alice", png_bytes(64, 64))
    assert new.file_id != r.file_id
    assert repo.get_by_id(r.file_id) is None  # the old main file is deleted
    assert not any(backend.exists(rec.key) for rec in variants)  # the old variants are gone
    svc.delete_avatar("alice")
    assert repo.get_user_avatar("alice") is None
    assert svc.get_avatar("alice").is_default is True


def test_concurrent_same_key_upload(tmp_path: Path) -> None:
    """Concurrent same-key uploads across threads, repository, and storage."""
    repo = SqliteFileRepository(db_url(tmp_path))
    backend = InMemoryStorageBackend()
    svc = make_service(repo, backend=backend, event_bus=None, registry=isolated_registry())
    key = "integration-concurrent"
    a = text_bytes(1024)
    b = text_bytes(2048)
    barrier = threading.Barrier(2)
    errors: list[Exception] = []

    def worker(data: bytes) -> None:
        try:
            barrier.wait(timeout=10)
            svc.upload(data, key=key)
        except Exception as e:  # collected and asserted
            errors.append(e)

    threads = [threading.Thread(target=worker, args=(a,)), threading.Thread(target=worker, args=(b,))]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=30)
    assert not errors
    assert len([r for r in repo.list_by_namespace(None) if r.key == key]) == 1
    assert backend.get(key).read() in (a, b)  # last-write-wins
