"""Acceptance tests for brute-force lockout (docs/specs/authentication.md, AC-006 .. AC-008)."""

from __future__ import annotations

import time
from datetime import timedelta
from pathlib import Path

import pytest

from authentication_test_helpers import build_auth_service, create_user, valid_login

from backend.authentication import InvalidCredentialsError, LoginRequest


def test_ac_006_below_max_failures_not_locked(tmp_path: Path) -> None:
    fixture = build_auth_service(tmp_path)
    create_user(fixture.user_manager)
    for _ in range(4):  # max_failed_attempts - 1
        with pytest.raises(InvalidCredentialsError):
            fixture.service.login(LoginRequest(**valid_login("alice", "wrong-pass-1")))
    # not yet locked: the next attempt is evaluated normally
    result = fixture.service.login(LoginRequest(**valid_login("alice")))
    assert result.user.username == "alice"


def test_ac_007_locked_identifier_rejected_even_correct_password(tmp_path: Path) -> None:
    fixture = build_auth_service(tmp_path)
    create_user(fixture.user_manager)
    for _ in range(5):  # max_failed_attempts
        with pytest.raises(InvalidCredentialsError):
            fixture.service.login(LoginRequest(**valid_login("alice", "wrong-pass-1")))
    with pytest.raises(InvalidCredentialsError):
        fixture.service.login(LoginRequest(**valid_login("alice")))


def test_ac_008_lockout_expires_and_success_clears(tmp_path: Path) -> None:
    fixture = build_auth_service(tmp_path, lockout_duration=timedelta(milliseconds=100))
    create_user(fixture.user_manager)
    for _ in range(5):
        with pytest.raises(InvalidCredentialsError):
            fixture.service.login(LoginRequest(**valid_login("alice", "wrong-pass-1")))
    time.sleep(0.15)
    # the lockout window has elapsed: login succeeds and the state is cleared
    result = fixture.service.login(LoginRequest(**valid_login("alice")))
    assert result.user.username == "alice"
    # a fresh failure sequence starts from zero
    for _ in range(4):
        with pytest.raises(InvalidCredentialsError):
            fixture.service.login(LoginRequest(**valid_login("alice", "wrong-pass-1")))
    assert fixture.service.login(LoginRequest(**valid_login("alice"))).user.username == "alice"
