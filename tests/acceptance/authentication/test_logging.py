"""Acceptance tests for logging (docs/specs/authentication.md, AC-035)."""

from __future__ import annotations

import pytest

from authentication_test_helpers import create_user, valid_login

from backend.authentication import InvalidCredentialsError, LoginRequest


def test_ac_035_no_secrets_in_log_records(auth, log_records) -> None:
    create_user(auth.user_manager)
    password = "correct-horse-1"
    result = auth.service.login(LoginRequest(**valid_login("alice", password)))
    token = result.token
    auth.service.session_info(token)
    auth.service.logout(token)
    # a failed login too
    with pytest.raises(InvalidCredentialsError):
        auth.service.login(LoginRequest(**valid_login("alice", "wrong-pass-1")))
    for record in log_records:
        text = str(record)
        assert password not in text
        assert token not in text
