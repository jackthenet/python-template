"""Unit tests for session edge cases (docs/specs/authentication.md, EDGE-004 .. EDGE-006, EDGE-017)."""

from __future__ import annotations

import time
from datetime import timedelta
from pathlib import Path

import pytest
from authentication_test_helpers import build_auth_service, create_user, valid_login

from backend.authentication import InvalidSessionError, LoginRequest


def test_edge_004_session_info_expired(tmp_path: Path) -> None:
    fixture = build_auth_service(tmp_path, session_ttl=timedelta(milliseconds=100))
    create_user(fixture.user_manager)
    result = fixture.service.login(LoginRequest(**valid_login("alice")))
    time.sleep(0.15)
    with pytest.raises(InvalidSessionError):
        fixture.service.session_info(result.token)


def test_edge_005_session_info_revoked(auth) -> None:
    create_user(auth.user_manager)
    result = auth.service.login(LoginRequest(**valid_login("alice")))
    auth.service.logout(result.token)
    with pytest.raises(InvalidSessionError):
        auth.service.session_info(result.token)


def test_edge_006_logout_twice_noop(auth) -> None:
    create_user(auth.user_manager)
    result = auth.service.login(LoginRequest(**valid_login("alice")))
    auth.service.logout(result.token)
    auth.service.logout(result.token)  # idempotent no-op


def test_edge_017_session_info_no_token(auth) -> None:
    create_user(auth.user_manager)
    result = auth.service.login(LoginRequest(**valid_login("alice")))
    info = auth.service.session_info(result.token)
    fields = set(info.model_dump().keys())
    assert "token" not in fields
