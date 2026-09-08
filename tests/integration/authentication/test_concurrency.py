"""Integration tests for concurrency (docs/specs/authentication.md, NFR-005)."""

from __future__ import annotations

import threading
from pathlib import Path

from authentication_test_helpers import build_auth_service, create_user, valid_login

from backend.authentication import LoginRequest

_THREAD_COUNT = 8


def test_nfr_005_concurrent_login_thread_safety(tmp_path: Path) -> None:
    fixture = build_auth_service(tmp_path)
    create_user(fixture.user_manager)
    errors: list[BaseException] = []
    results: list = []

    def worker() -> None:
        try:
            results.append(fixture.service.login(LoginRequest(**valid_login("alice"))))
        except BaseException as exc:
            errors.append(exc)

    threads = [threading.Thread(target=worker) for _ in range(_THREAD_COUNT)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert not errors
    assert len(results) == _THREAD_COUNT
    # all sessions are valid and distinct
    tokens = [r.token for r in results]
    assert len(set(tokens)) == _THREAD_COUNT
    for r in results:
        fixture.service.session_info(r.token)
