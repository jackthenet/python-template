"""Unit tests for login edge cases (docs/specs/authentication.md, EDGE-001, EDGE-002, EDGE-018)."""

from __future__ import annotations

import pydantic
import pytest
from authentication_test_helpers import create_user, valid_login

from backend.authentication import InvalidCredentialsError, LoginRequest


def test_edge_001_login_neither_username_nor_email(auth_service, user_manager) -> None:
    # an identifier that matches neither a username nor an email
    create_user(user_manager)
    with pytest.raises(InvalidCredentialsError):
        auth_service.login(LoginRequest(**valid_login("not-a-user-or-email", "correct-horse-1")))


def test_edge_002_login_inactive_user(auth_service, user_manager) -> None:
    user = create_user(user_manager)
    user_manager.deactivate_user(user.id)
    with pytest.raises(InvalidCredentialsError):
        auth_service.login(LoginRequest(**valid_login("alice")))


def test_edge_018_empty_identifier() -> None:
    with pytest.raises(pydantic.ValidationError):
        LoginRequest(identifier="", password="correct-horse-1")
