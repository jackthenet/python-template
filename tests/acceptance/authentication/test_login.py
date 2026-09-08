"""Acceptance tests for login (docs/specs/authentication.md, AC-001 .. AC-005)."""

from __future__ import annotations

import pytest
from authentication_test_helpers import create_user, valid_login

from backend.authentication import InvalidCredentialsError, LoginRequest


def test_ac_001_login_by_username_success(auth_service, user_manager) -> None:
    user = create_user(user_manager)
    result = auth_service.login(LoginRequest(**valid_login("alice")))
    assert result.user.username == "alice"
    assert result.session.user_id == user.id
    info = auth_service.session_info(result.token)
    assert info.user_id == user.id


def test_ac_002_login_by_email_success(auth_service, user_manager) -> None:
    create_user(user_manager)
    result = auth_service.login(LoginRequest(**valid_login("alice@example.com")))
    assert result.user.username == "alice"


def test_ac_003_login_wrong_password_rejected(auth_service, user_manager) -> None:
    create_user(user_manager)
    with pytest.raises(InvalidCredentialsError):
        auth_service.login(LoginRequest(**valid_login("alice", "wrong-pass-1")))


def test_ac_004_login_unknown_user_rejected(auth_service, user_manager) -> None:
    with pytest.raises(InvalidCredentialsError):
        auth_service.login(LoginRequest(**valid_login("ghost", "correct-horse-1")))


def test_ac_005_login_inactive_user_rejected(auth_service, user_manager) -> None:
    user = create_user(user_manager)
    user_manager.deactivate_user(user.id)
    with pytest.raises(InvalidCredentialsError):
        auth_service.login(LoginRequest(**valid_login("alice")))
