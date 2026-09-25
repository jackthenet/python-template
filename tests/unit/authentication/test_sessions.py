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


def test_list_all_returns_all_sessions_created_at_desc(tmp_path: Path) -> None:
    """T-004 / AC-036: the additive ``SessionRepository.list_all()`` returns all
    sessions (including revoked, no user filter), ``created_at`` descending."""
    fixture = build_auth_service(tmp_path)
    create_user(fixture.user_manager)
    tokens = []
    for _ in range(3):
        result = fixture.service.login(LoginRequest(**valid_login("alice")))
        tokens.append(result.token)
    # Revoke one session (so a revoked session is present).
    fixture.service.logout(tokens[0])
    sessions = fixture.session_repository.list_all()
    # All sessions are returned (no user filter, including the revoked one).
    assert len(sessions) == len(tokens)
    # created_at descending.
    created = [s.created_at for s in sessions]
    assert created == sorted(created, reverse=True)
