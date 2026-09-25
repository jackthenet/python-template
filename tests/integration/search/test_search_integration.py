"""Integration tests for the search feature (docs/specs/search.md).

Covers the cross-cutting integration criteria: the resilient global fan-out
failure marker (AC-025), concurrent register/search (EDGE-019), the
thread-safe registry (NFR-005), and the startup wiring that registers all
three feature sources so a global search fans out to them (REQ-023).

The ``backend.search`` and ``build_*_source`` imports are deferred into the
test bodies so the module collects cleanly before the feature is implemented
(RED).
"""

from __future__ import annotations

import threading
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from search_test_helpers import (
    EventCollector,
    db_url,
    demo_source,
    failing_source,
    fresh_registry,
    search_query,
    service,
)

_BASE = datetime(2024, 1, 1, tzinfo=UTC)


def test_ac_025_global_fanout_source_failure_partial() -> None:
    """AC-025: a global fan-out where one source raises during its query
    returns a ``SearchResult`` with the other sources' items, a failure marker
    for the failing source (feature, reason ``query_failed``, error kind), and
    publishes a ``SourceQueryFailed`` event."""
    from backend.search import SourceQueryFailed

    collector = EventCollector()
    svc = service(event_bus=collector)
    n_ok = 3
    svc.register_source(demo_source("ok", n=n_ok))
    svc.register_source(failing_source("failing"))
    result = svc.search(search_query())  # no feature = global fan-out
    # The other sources' items are returned.
    assert result.total == n_ok
    assert [it.feature for it in result.items] == ["ok"] * n_ok
    # A failure marker for the failing source (feature, reason, error kind).
    assert len(result.failures) == 1
    failure = result.failures[0]
    assert failure.feature == "failing"
    assert failure.reason == "query_failed"
    assert failure.error  # error kind (no sensitive data)
    # A SourceQueryFailed event is published.
    assert len(collector.of_type(SourceQueryFailed)) == 1


def test_edge_019_concurrent_register_search() -> None:
    """EDGE-019: concurrent register/replace + search: no exception, no partial
    state; a query sees either the old or the new source (never a partial
    state)."""
    svc = service()
    svc.register_source(demo_source("demo", n=3))
    errors: list[BaseException] = []
    barrier = threading.Barrier(2)

    def registrar() -> None:
        barrier.wait()
        try:
            for i in range(30):
                svc.register_source(demo_source("demo", n=(i % 5) + 1))  # replace
        except BaseException as exc:
            errors.append(exc)

    def searcher() -> None:
        barrier.wait()
        try:
            for _ in range(30):
                result = svc.search(search_query(feature="demo"))
                # A query sees either the old or the new source: a valid total,
                # no partial state (the replace cycle is n in 1..5).
                max_items = 5
                assert 1 <= result.total <= max_items
                assert len(result.items) <= result.total
        except BaseException as exc:
            errors.append(exc)

    threads = [threading.Thread(target=registrar), threading.Thread(target=searcher)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert not errors, f"unexpected exceptions: {errors}"


def test_nfr_005_thread_safe_registry() -> None:
    """NFR-005: the registry and the query path are thread-safe (concurrent
    register/query, no partial state); a failed operation leaves the registry
    unchanged."""
    svc = service()
    errors: list[BaseException] = []
    barrier = threading.Barrier(3)

    def registrar(prefix: str) -> None:
        barrier.wait()
        try:
            for i in range(20):
                svc.register_source(demo_source(f"{prefix}-{i % 3}"))
        except BaseException as exc:
            errors.append(exc)

    def searcher() -> None:
        barrier.wait()
        try:
            for _ in range(50):
                svc.search(search_query())  # global fan-out
        except BaseException as exc:
            errors.append(exc)

    threads = [
        threading.Thread(target=registrar, args=("a",)),
        threading.Thread(target=registrar, args=("b",)),
        threading.Thread(target=searcher),
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # No exception from any thread.
    assert not errors, f"unexpected exceptions: {errors}"
    # No partial state: the final registry is a function of the last operation
    # per name (each thread's three names end up registered).
    assert set(svc.list_sources()) == {"a-0", "a-1", "a-2", "b-0", "b-1", "b-2"}

    # A failed operation leaves the registry unchanged.
    svc.register_source(failing_source("failing"))
    result = svc.search(search_query())  # global fan-out; "failing" raises
    assert any(f.feature == "failing" for f in result.failures)
    assert "failing" in svc.list_sources()  # the registry is unchanged


def test_startup_wiring_all_sources(tmp_path: Path) -> None:
    """REQ-023: after the startup wiring (``register_settings``,
    ``register_actions``, the three feature sources), a global search fans out
    to all three feature sources."""
    from backend.search import register_actions, register_settings

    from backend.authentication import hash_token, new_token
    from backend.authentication.models import Session
    from backend.authentication.repository import SqliteSessionRepository
    from backend.filemanagement import FileRecord, SqliteFileRepository, build_file_source
    from backend.permissions.catalog import PermissionCatalog
    from backend.sessionmanagement import build_session_source
    from backend.usermanagement import SqliteUserRepository, User, build_user_source

    # Startup wiring: feature settings + actions, then the three feature sources.
    reg = fresh_registry()
    register_settings(reg)
    catalog = PermissionCatalog()
    register_actions(catalog)
    assert catalog.has("search.search")

    # The three feature repositories with valid rows.
    user_repo = SqliteUserRepository(db_url(tmp_path, "users.db"))
    user_repo.add(
        User(
            username="alice",
            email="alice@example.com",
            display_name="Alice",
            roles=["user"],
            password_hash="argon2id:fake-alice",
            profile_picture_url=None,
            is_active=True,
            created_at=_BASE,
            updated_at=_BASE,
        )
    )
    file_repo = SqliteFileRepository(db_url(tmp_path, "files.db"))
    file_repo.add(
        FileRecord(
            key="rep-1",
            original_filename="report.txt",
            declared_mime_type="text/plain",
            detected_mime_type="text/plain",
            size=1024,
            sha256="a" * 64,
            namespace="general",
            uploader=None,
            created_at=_BASE,
            updated_at=_BASE,
        )
    )
    session_repo = SqliteSessionRepository(db_url(tmp_path, "sessions.db"))
    session_repo.add(
        Session(
            user_id=uuid4(),
            token_hash=hash_token(new_token()),
            created_at=_BASE,
            expires_at=_BASE,
            revoked=False,
            login_method="password",
        )
    )

    svc = service(settings_registry=reg)
    svc.register_source(build_user_source(user_repo))
    svc.register_source(build_file_source(file_repo))
    svc.register_source(build_session_source(session_repo))

    # The global search fans out to all three feature sources (registration order).
    n_sources = 3
    result = svc.search(search_query())
    assert result.total == n_sources
    assert [it.feature for it in result.items] == [
        "usermanagement",
        "filemanagement",
        "sessionmanagement",
    ]
