"""Acceptance tests for timing equalization (docs/specs/authentication.md, AC-009)."""

from __future__ import annotations

import statistics
import time

import pytest
from authentication_test_helpers import create_user

from backend.authentication import AuthService, InvalidCredentialsError, LoginRequest
from backend.usermanagement import UserManager


def _login_seconds(service: AuthService, identifier: str, password: str) -> float:
    start = time.monotonic()
    with pytest.raises(InvalidCredentialsError):
        service.login(LoginRequest(identifier=identifier, password=password))
    return time.monotonic() - start


def test_ac_009_dummy_verify_on_unknown_user(auth_service: AuthService, user_manager: UserManager) -> None:
    create_user(user_manager)
    # an unknown identifier still performs one Argon2id (dummy) verification,
    # so its dominant cost term is equalized with a known user's failed login
    unknown = statistics.median([_login_seconds(auth_service, "ghost-user", "correct-horse-1") for _ in range(5)])
    known = statistics.median([_login_seconds(auth_service, "alice", "wrong-pass-1") for _ in range(5)])
    assert unknown >= 0.25 * known
