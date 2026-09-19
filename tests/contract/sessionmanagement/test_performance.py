"""Contract tests for performance (docs/specs/session-management.md, NFR-001).

Budgets (NFR-001), measured on local hardware against a local SQLite database
with the shared logging feature active — the budgets hold including the
per-call logging overhead at that level:

- listing 100 sessions: <= 100 ms at p95
- revoking all sessions for a user with 1000 sessions: <= 500 ms at p95
- cleanup of 1000 expired rows: <= 500 ms at p95
"""

from __future__ import annotations

import statistics
import time
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from sessionmanagement_test_helpers import build_session_service, make_session

from backend.authentication.repository import SqliteSessionRepository

_LIST_BUDGET_SECONDS = 0.1  # 100 ms at p95
_REVOKE_BUDGET_SECONDS = 0.5  # 500 ms at p95
_CLEANUP_BUDGET_SECONDS = 0.5  # 500 ms at p95


def test_nfr_001_list_100_sessions_budget() -> None:
    """NFR-001: listing 100 sessions completes in <= 100 ms at p95."""
    _sample_list_100()  # warm up (module import, etc.)
    samples: list[float] = []
    for _ in range(15):
        samples.append(_sample_list_100())
    p95 = statistics.quantiles(samples, n=100, method="inclusive")[94]
    assert p95 <= _LIST_BUDGET_SECONDS


def test_nfr_001_revoke_1000_sessions_budget() -> None:
    """NFR-001: revoking all sessions for a user with 1000 sessions completes in
    <= 500 ms at p95."""
    _sample_revoke_1000()  # warm up (module import, etc.)
    samples: list[float] = []
    for _ in range(15):
        samples.append(_sample_revoke_1000())
    p95 = statistics.quantiles(samples, n=100, method="inclusive")[94]
    assert p95 <= _REVOKE_BUDGET_SECONDS


def test_nfr_001_cleanup_1000_rows_budget() -> None:
    """NFR-001: cleanup of 1000 expired rows completes in <= 500 ms at p95."""
    _sample_cleanup_1000()  # warm up (module import, etc.)
    samples: list[float] = []
    for _ in range(15):
        samples.append(_sample_cleanup_1000())
    p95 = statistics.quantiles(samples, n=100, method="inclusive")[94]
    assert p95 <= _CLEANUP_BUDGET_SECONDS


def _sample_list_100() -> float:
    """Time one list_sessions call over a fresh store with 100 valid sessions."""
    repo = SqliteSessionRepository("sqlite:///:memory:")
    service = build_session_service(repo)
    user_id = uuid4()
    now = datetime.now(UTC)
    for i in range(100):
        make_session(repo, user_id, created_at=now - timedelta(minutes=i))
    samples: list[float] = []
    start = time.monotonic()
    try:
        service.list_sessions(user_id=user_id)
    finally:
        samples.append(time.monotonic() - start)
    return samples[0]


def _sample_revoke_1000() -> float:
    """Time one revoke_all_sessions call over a fresh store with 1000 valid sessions."""
    repo = SqliteSessionRepository("sqlite:///:memory:")
    service = build_session_service(repo)
    user_id = uuid4()
    now = datetime.now(UTC)
    for i in range(1000):
        make_session(repo, user_id, created_at=now - timedelta(minutes=i))
    samples: list[float] = []
    start = time.monotonic()
    try:
        service.revoke_all_sessions(user_id)
    finally:
        samples.append(time.monotonic() - start)
    return samples[0]


def _sample_cleanup_1000() -> float:
    """Time one cleanup_expired call over a fresh store with 1000 expired rows."""
    repo = SqliteSessionRepository("sqlite:///:memory:")
    service = build_session_service(repo)
    user_id = uuid4()
    now = datetime.now(UTC)
    for i in range(1000):
        make_session(
            repo,
            user_id,
            created_at=now - timedelta(days=2, seconds=i),
            expires_at=now - timedelta(days=1, seconds=i),
        )
    samples: list[float] = []
    start = time.monotonic()
    try:
        service.cleanup_expired()
    finally:
        samples.append(time.monotonic() - start)
    return samples[0]
