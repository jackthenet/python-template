"""Acceptance tests for password recovery (docs/specs/authentication.md, AC-015 .. AC-021)."""

from __future__ import annotations

import time
from datetime import timedelta
from pathlib import Path

import pytest
from authentication_test_helpers import build_auth_service, create_user, valid_login

from backend.authentication import (
    InvalidCredentialsError,
    InvalidResetTokenError,
    InvalidSessionError,
    LoginRequest,
    PasswordResetComplete,
    PasswordResetRequest,
)


def test_ac_015_reset_request_registered_email(auth) -> None:
    create_user(auth.user_manager)
    token = auth.service.request_password_reset(PasswordResetRequest(email="alice@example.com"))
    assert token is not None
    assert len(token) > 0


def test_ac_016_reset_request_unknown_email(auth) -> None:
    token = auth.service.request_password_reset(PasswordResetRequest(email="ghost@example.com"))
    assert token is None


def test_ac_017_reset_token_single_use(auth) -> None:
    create_user(auth.user_manager)
    token = auth.service.request_password_reset(PasswordResetRequest(email="alice@example.com"))
    assert token is not None
    auth.service.complete_password_reset(PasswordResetComplete(token=token, new_password="new-pass-1"))
    with pytest.raises(InvalidResetTokenError) as exc:
        auth.service.complete_password_reset(PasswordResetComplete(token=token, new_password="new-pass-1"))
    assert exc.value.reason == "used"


def test_ac_018_new_request_supersedes(auth) -> None:
    create_user(auth.user_manager)
    first = auth.service.request_password_reset(PasswordResetRequest(email="alice@example.com"))
    assert first is not None
    second = auth.service.request_password_reset(PasswordResetRequest(email="alice@example.com"))
    assert second is not None
    # the prior token is invalidated
    with pytest.raises(InvalidResetTokenError):
        auth.service.complete_password_reset(PasswordResetComplete(token=first, new_password="new-pass-1"))
    # the current token still works
    auth.service.complete_password_reset(PasswordResetComplete(token=second, new_password="new-pass-1"))


def test_ac_019_reset_completes_and_revokes_sessions(auth) -> None:
    user = create_user(auth.user_manager)
    result = auth.service.login(LoginRequest(**valid_login("alice")))
    token = auth.service.request_password_reset(PasswordResetRequest(email="alice@example.com"))
    assert token is not None
    auth.service.complete_password_reset(PasswordResetComplete(token=token, new_password="new-pass-1"))
    # the password is changed
    assert auth.service.login(LoginRequest(**valid_login("alice", "new-pass-1"))).user.id == user.id
    with pytest.raises(InvalidCredentialsError):
        auth.service.login(LoginRequest(**valid_login("alice", "correct-horse-1")))
    # all sessions for the user are revoked
    with pytest.raises(InvalidSessionError):
        auth.service.session_info(result.token)


def test_ac_020_reset_expired_token(tmp_path: Path) -> None:
    fixture = build_auth_service(tmp_path, reset_token_ttl=timedelta(milliseconds=100))
    create_user(fixture.user_manager)
    token = fixture.service.request_password_reset(PasswordResetRequest(email="alice@example.com"))
    assert token is not None
    time.sleep(0.15)
    with pytest.raises(InvalidResetTokenError) as exc:
        fixture.service.complete_password_reset(PasswordResetComplete(token=token, new_password="new-pass-1"))
    assert exc.value.reason == "expired"


def test_ac_021_reset_unknown_token(auth) -> None:
    with pytest.raises(InvalidResetTokenError) as exc:
        auth.service.complete_password_reset(PasswordResetComplete(token="no-such-token", new_password="new-pass-1"))
    assert exc.value.reason == "unknown"
