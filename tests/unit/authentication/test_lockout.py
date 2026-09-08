"""Unit tests for lockout edge cases (docs/specs/authentication.md, EDGE-003)."""

from __future__ import annotations

from pathlib import Path

import pytest
from authentication_test_helpers import build_auth_service, create_user, valid_login

from backend.authentication import InvalidCredentialsError, LoginRequest


def test_edge_003_login_while_locked(tmp_path: Path) -> None:
    fixture = build_auth_service(tmp_path)
    create_user(fixture.user_manager)
    for _ in range(5):  # max_failed_attempts
        with pytest.raises(InvalidCredentialsError):
            fixture.service.login(LoginRequest(**valid_login("alice", "wrong-pass-1")))
    with pytest.raises(InvalidCredentialsError):
        fixture.service.login(LoginRequest(**valid_login("alice")))
