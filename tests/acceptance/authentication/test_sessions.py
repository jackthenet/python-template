"""Acceptance tests for sessions (docs/specs/authentication.md, AC-010 .. AC-014)."""

from __future__ import annotations

import hashlib
import re
import time
from datetime import timedelta
from pathlib import Path

import pytest

from authentication_test_helpers import build_auth_service, create_user, valid_login

from backend.authentication import InvalidSessionError, LoginRequest


def test_ac_010_token_format_and_hashed_at_rest(auth) -> None:
    create_user(auth.user_manager)
    result = auth.service.login(LoginRequest(**valid_login("alice")))
    token = result.token
    # 256-bit URL-safe: token_urlsafe(32) -> 43 chars
    assert re.fullmatch(r"[A-Za-z0-9_-]{43}", token) is not None
    # the store is keyed by the SHA-256 hash, not the raw token
    digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
    stored = auth.session_repository.get_by_token_hash(digest)
    assert stored is not None
    assert stored.user_id == result.session.user_id
    assert auth.session_repository.get_by_token_hash(token) is None


def test_ac_011_session_expiry(tmp_path: Path) -> None:
    fixture = build_auth_service(tmp_path, session_ttl=timedelta(milliseconds=100))
    create_user(fixture.user_manager)
    result = fixture.service.login(LoginRequest(**valid_login("alice")))
    time.sleep(0.15)
    with pytest.raises(InvalidSessionError):
        fixture.service.session_info(result.token)


def test_ac_012_session_info_valid(auth) -> None:
    user = create_user(auth.user_manager)
    result = auth.service.login(LoginRequest(**valid_login("alice")))
    info = auth.service.session_info(result.token)
    assert info.user_id == user.id
    assert info.created_at is not None
    assert info.expires_at > info.created_at


def test_ac_013_logout_revokes(auth) -> None:
    create_user(auth.user_manager)
    result = auth.service.login(LoginRequest(**valid_login("alice")))
    auth.service.logout(result.token)
    with pytest.raises(InvalidSessionError):
        auth.service.session_info(result.token)


def test_ac_014_logout_invalid_noop(auth, tmp_path: Path) -> None:
    # unknown token
    auth.service.logout("A" * 43)
    # revoked token
    create_user(auth.user_manager)
    result = auth.service.login(LoginRequest(**valid_login("alice")))
    auth.service.logout(result.token)
    auth.service.logout(result.token)
    # expired token
    fixture = build_auth_service(tmp_path, session_ttl=timedelta(milliseconds=100))
    create_user(fixture.user_manager)
    expired = fixture.service.login(LoginRequest(**valid_login("alice")))
    time.sleep(0.15)
    fixture.service.logout(expired.token)
