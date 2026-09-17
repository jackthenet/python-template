"""Integration tests for concurrent use (docs/specs/session-management.md).

Covers EDGE-010 and NFR-005: the service and the reused SQLite repository are
safe for concurrent use from multiple threads (each operation opens its own
session; SQLite busy-timeout serializes concurrent writers).
"""

from __future__ import annotations

import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import UUID, uuid4

from sessionmanagement_test_helpers import build_session_service, db_url, make_session

from backend.authentication.repository import SqliteSessionRepository


def test_edge_010_concurrent_revocation_and_listing(tmp_path: Path) -> None:
    """EDGE-010: one thread revokes while another lists — no crash; the list
    reflects a consistent revocation state (a row is either present or absent,
    never partial)."""
    session_repository = SqliteSessionRepository(db_url(tmp_path))
    service = build_session_service(session_repository, event_bus=None)
    user_id = uuid4()
    base = datetime.now(UTC)
    rows = [make_session(session_repository, user_id, created_at=base + timedelta(minutes=i)) for i in range(20)]
    created_ids = {row.id for row, _ in rows}
    errors: list[BaseException] = []
    stop = threading.Event()

    def revoker() -> None:
        try:
            for row, _token in rows:
                service.revoke_session(row.id)
        except BaseException as exc:
            errors.append(exc)

    def lister() -> None:
        try:
            while not stop.is_set():
                entries = service.list_sessions(user_id=user_id)
                for entry in entries:
                    # a row is either present or absent, never partial
                    assert entry.session_id in created_ids
                    assert entry.session_id is not None
                    assert entry.created_at is not None
                    assert entry.expires_at is not None
                    assert entry.is_current is not None
        except BaseException as exc:
            errors.append(exc)

    with ThreadPoolExecutor(max_workers=2) as pool:
        revoke_future = pool.submit(revoker)
        list_future = pool.submit(lister)
        revoke_future.result()
        stop.set()
        list_future.result()
    assert not errors, errors
    # final state: everything revoked
    assert service.list_sessions(user_id=user_id) == []


def test_nfr_005_concurrent_threads_safe(tmp_path: Path) -> None:
    """NFR-005: the service and the SQLite repositories are safe for
    concurrent use from multiple threads."""
    session_repository = SqliteSessionRepository(db_url(tmp_path))
    service = build_session_service(session_repository, event_bus=None)
    user_ids = [uuid4() for _ in range(4)]
    base = datetime.now(UTC)
    rows_by_user: dict[UUID, list[tuple[object, str]]] = {
        uid: [make_session(session_repository, uid, created_at=base + timedelta(minutes=i)) for i in range(10)]
        for uid in user_ids
    }
    all_ids = {row.id for rows in rows_by_user.values() for row, _token in rows}
    errors: list[BaseException] = []

    def worker(uid: UUID) -> None:
        try:
            rows = rows_by_user[uid]
            for row, _token in rows:
                service.revoke_session(row.id)
            for _ in range(5):
                entries = service.list_sessions(user_id=uid)
                for entry in entries:
                    assert entry.session_id in all_ids
            service.revoke_all_sessions(uid)
            service.cleanup_expired()
        except BaseException as exc:
            errors.append(exc)

    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = [pool.submit(worker, uid) for uid in user_ids]
        for future in futures:
            future.result()
    assert not errors, errors
    for uid in user_ids:
        assert service.list_sessions(user_id=uid) == []
