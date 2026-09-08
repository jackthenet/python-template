"""Acceptance tests for lifecycle events (docs/specs/authentication.md, AC-031 .. AC-033)."""

from __future__ import annotations

from pathlib import Path

import pytest
from authentication_test_helpers import build_auth_service, create_user, valid_login

from backend.authentication import (
    InvalidCredentialsError,
    LoginFailed,
    LoginRequest,
    LoginSucceeded,
    Logout,
    PasskeyDeleted,
    PasskeyRegistered,
    PasskeyRegistrationComplete,
    PasswordResetComplete,
    PasswordResetCompleted,
    PasswordResetRequest,
    PasswordResetRequested,
)


def test_ac_031_login_success_event(auth) -> None:
    create_user(auth.user_manager)
    auth.service.login(LoginRequest(**valid_login("alice")))
    events = auth.collector.of_type(LoginSucceeded)
    assert len(events) == 1
    assert events[0].method == "password"


def test_ac_032_login_failed_event(auth) -> None:
    create_user(auth.user_manager)
    with pytest.raises(InvalidCredentialsError):
        auth.service.login(LoginRequest(**valid_login("alice", "wrong-pass-1")))
    events = auth.collector.of_type(LoginFailed)
    assert len(events) == 1
    assert events[0].method == "password"


def test_ac_033_lifecycle_events_and_none_publisher(auth, tmp_path: Path) -> None:
    user = create_user(auth.user_manager)
    # logout
    result = auth.service.login(LoginRequest(**valid_login("alice")))
    auth.service.logout(result.token)
    # reset request + completion
    token = auth.service.request_password_reset(PasswordResetRequest(email="alice@example.com"))
    assert token is not None
    auth.service.complete_password_reset(PasswordResetComplete(token=token, new_password="new-pass-1"))
    # passkey registration + deletion
    read = auth.service.complete_passkey_registration(
        PasskeyRegistrationComplete(user_id=user.id, response={})
    )
    auth.service.delete_passkey(user.id, read.credential_id)

    assert len(auth.collector.of_type(Logout)) == 1
    assert len(auth.collector.of_type(PasswordResetRequested)) == 1
    assert len(auth.collector.of_type(PasswordResetCompleted)) == 1
    assert len(auth.collector.of_type(PasskeyRegistered)) == 1
    assert len(auth.collector.of_type(PasskeyDeleted)) == 1

    # a None publisher: no event is published and no error is raised
    # (separate store: the auth fixture already owns tmp_path)
    fixture = build_auth_service(tmp_path / "none-publisher")
    create_user(fixture.user_manager)
    fixture.service.login(LoginRequest(**valid_login("alice")))
