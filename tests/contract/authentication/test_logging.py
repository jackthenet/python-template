"""Contract tests for logging (docs/specs/authentication.md, NFR-004)."""

from __future__ import annotations

import pytest
from authentication_test_helpers import create_user, valid_login

from backend.authentication import InvalidCredentialsError, LoginRequest


def test_nfr_004_service_traced(auth, log_records) -> None:
    create_user(auth.user_manager)
    log_records.clear()
    result = auth.service.login(LoginRequest(**valid_login("alice")))
    auth.service.session_info(result.token)
    # a failed login too
    with pytest.raises(InvalidCredentialsError):
        auth.service.login(LoginRequest(**valid_login("alice", "wrong-pass-1")))
    # @logged_class traces entry/exit/exception per public method
    joined = "\n".join(str(r) for r in log_records)
    assert "AuthService.login called" in joined
    assert "returned in" in joined
    assert "AuthService.session_info called" in joined
    assert "raised InvalidCredentialsError" in joined
