"""Unit tests for password reset edge cases (docs/specs/authentication.md, EDGE-007 .. EDGE-012)."""

from __future__ import annotations

import time
from datetime import timedelta
from pathlib import Path

import pydantic
import pytest
from authentication_test_helpers import build_auth_service, create_user

from backend.authentication import (
    InvalidResetTokenError,
    PasswordResetComplete,
    PasswordResetRequest,
)


def test_edge_007_reset_unknown_email_no_token(auth) -> None:
    token = auth.service.request_password_reset(PasswordResetRequest(email="ghost@example.com"))
    assert token is None


def test_edge_008_reset_expired_token(tmp_path: Path) -> None:
    fixture = build_auth_service(tmp_path, reset_token_ttl=timedelta(milliseconds=100))
    create_user(fixture.user_manager)
    token = fixture.service.request_password_reset(PasswordResetRequest(email="alice@example.com"))
    assert token is not None
    time.sleep(0.15)
    with pytest.raises(InvalidResetTokenError) as exc:
        fixture.service.complete_password_reset(
            PasswordResetComplete(token=token, new_password="new-pass-1")
        )
    assert exc.value.reason == "expired"


def test_edge_009_reset_used_token(auth) -> None:
    create_user(auth.user_manager)
    token = auth.service.request_password_reset(PasswordResetRequest(email="alice@example.com"))
    assert token is not None
    auth.service.complete_password_reset(PasswordResetComplete(token=token, new_password="new-pass-1"))
    with pytest.raises(InvalidResetTokenError) as exc:
        auth.service.complete_password_reset(PasswordResetComplete(token=token, new_password="new-pass-1"))
    assert exc.value.reason == "used"


def test_edge_010_reset_unknown_token(auth) -> None:
    with pytest.raises(InvalidResetTokenError) as exc:
        auth.service.complete_password_reset(
            PasswordResetComplete(token="no-such-token", new_password="new-pass-1")
        )
    assert exc.value.reason == "unknown"


def test_edge_011_new_request_supersedes(auth) -> None:
    create_user(auth.user_manager)
    first = auth.service.request_password_reset(PasswordResetRequest(email="alice@example.com"))
    assert first is not None
    second = auth.service.request_password_reset(PasswordResetRequest(email="alice@example.com"))
    assert second is not None
    with pytest.raises(InvalidResetTokenError):
        auth.service.complete_password_reset(PasswordResetComplete(token=first, new_password="new-pass-1"))


def test_edge_012_reset_weak_password() -> None:
    with pytest.raises(pydantic.ValidationError):
        PasswordResetComplete(token="some-token", new_password="short")
