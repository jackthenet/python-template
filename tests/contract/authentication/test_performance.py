"""Contract tests for performance (docs/specs/authentication.md, NFR-001)."""

from __future__ import annotations

import contextlib
import statistics
import time
from pathlib import Path

from authentication_test_helpers import build_auth_service, create_user, valid_login

from backend.authentication import InvalidCredentialsError, LoginRequest

_BUDGET_SECONDS = 0.25  # 250 ms at p95


def test_nfr_001_login_performance_budget(tmp_path: Path) -> None:
    fixture = build_auth_service(tmp_path)
    create_user(fixture.user_manager)
    # warm up (SQLite page cache, etc.)
    with contextlib.suppress(InvalidCredentialsError):
        fixture.service.login(LoginRequest(**valid_login("alice", "warmup-1")))
    samples: list[float] = []
    for _ in range(15):
        start = time.monotonic()
        try:
            fixture.service.login(LoginRequest(**valid_login("alice")))
        finally:
            samples.append(time.monotonic() - start)
    p95 = statistics.quantiles(samples, n=100, method="inclusive")[94]
    assert p95 <= _BUDGET_SECONDS
