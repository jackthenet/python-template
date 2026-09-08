"""Integration tests for the SQLite repositories (docs/specs/authentication.md)."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import uuid4

import pytest
from authentication_test_helpers import build_auth_service, create_user, valid_login

from backend.authentication import (
    InvalidSessionError,
    LoginRequest,
    PasswordReset,
    PasswordResetComplete,
    PasswordResetRequest,
    Session,
    WebAuthnCredential,
)

_NEW_SIGN_COUNT = 5


def test_session_repository_roundtrip(tmp_path: Path) -> None:
    fixture = build_auth_service(tmp_path)
    user_id = uuid4()
    session = Session(
        id=uuid4(),
        user_id=user_id,
        token_hash="ab" * 32,
        created_at=datetime.now(UTC),
        expires_at=datetime.now(UTC) + timedelta(days=7),
    )
    fixture.session_repository.add(session)
    stored = fixture.session_repository.get_by_token_hash(session.token_hash)
    assert stored is not None
    assert stored.id == session.id
    assert stored.user_id == user_id
    # revoke
    fixture.session_repository.revoke(session.id)
    assert fixture.session_repository.get_by_token_hash(session.token_hash).revoked is True
    # revoke_all_for_user
    other = Session(
        id=uuid4(),
        user_id=user_id,
        token_hash="cd" * 32,
        created_at=datetime.now(UTC),
        expires_at=datetime.now(UTC) + timedelta(days=7),
    )
    fixture.session_repository.add(other)
    fixture.session_repository.revoke_all_for_user(user_id)
    assert fixture.session_repository.get_by_token_hash(other.token_hash).revoked is True
    # delete_expired
    expired = Session(
        id=uuid4(),
        user_id=uuid4(),
        token_hash="ef" * 32,
        created_at=datetime.now(UTC) - timedelta(days=1),
        expires_at=datetime.now(UTC) - timedelta(seconds=1),
    )
    fixture.session_repository.add(expired)
    count = fixture.session_repository.delete_expired()
    assert count >= 1
    assert fixture.session_repository.get_by_token_hash(expired.token_hash) is None


def test_reset_repository_roundtrip(tmp_path: Path) -> None:
    fixture = build_auth_service(tmp_path)
    reset = PasswordReset(
        id=uuid4(),
        user_id=uuid4(),
        email="alice@example.com",
        token_hash="12" * 32,
        created_at=datetime.now(UTC),
        expires_at=datetime.now(UTC) + timedelta(minutes=15),
    )
    fixture.reset_repository.add(reset)
    stored = fixture.reset_repository.get_by_token_hash(reset.token_hash)
    assert stored is not None
    assert stored.email == "alice@example.com"
    # invalidate_all_for_user
    fixture.reset_repository.invalidate_all_for_user(reset.user_id)
    assert fixture.reset_repository.get_by_token_hash(reset.token_hash).used is True
    # mark_used
    other = PasswordReset(
        id=uuid4(),
        user_id=uuid4(),
        email="bob@example.com",
        token_hash="34" * 32,
        created_at=datetime.now(UTC),
        expires_at=datetime.now(UTC) + timedelta(minutes=15),
    )
    fixture.reset_repository.add(other)
    fixture.reset_repository.mark_used(other.id)
    assert fixture.reset_repository.get_by_token_hash(other.token_hash).used is True


def test_webauthn_repository_roundtrip(tmp_path: Path) -> None:
    fixture = build_auth_service(tmp_path)
    user_id = uuid4()
    credential = WebAuthnCredential(
        id=uuid4(),
        user_id=user_id,
        credential_id="cred-1",
        public_key="pk",
        transports='["internal"]',
        sign_count=0,
        created_at=datetime.now(UTC),
    )
    fixture.webauthn_repository.add(credential)
    stored = fixture.webauthn_repository.get_by_credential_id("cred-1")
    assert stored is not None
    assert stored.public_key == "pk"
    # list_for_user
    second = WebAuthnCredential(
        id=uuid4(),
        user_id=user_id,
        credential_id="cred-2",
        public_key="pk2",
        transports="[]",
        sign_count=0,
        created_at=datetime.now(UTC),
    )
    fixture.webauthn_repository.add(second)
    listed = fixture.webauthn_repository.list_for_user(user_id)
    assert {c.credential_id for c in listed} == {"cred-1", "cred-2"}
    # update_sign_count
    fixture.webauthn_repository.update_sign_count("cred-1", _NEW_SIGN_COUNT)
    assert fixture.webauthn_repository.get_by_credential_id("cred-1").sign_count == _NEW_SIGN_COUNT
    # delete
    fixture.webauthn_repository.delete("cred-2")
    assert fixture.webauthn_repository.get_by_credential_id("cred-2") is None


def test_full_flow_login_reset_logout(tmp_path: Path) -> None:
    fixture = build_auth_service(tmp_path)
    user = create_user(fixture.user_manager)
    # login
    result = fixture.service.login(LoginRequest(**valid_login("alice")))
    assert fixture.service.session_info(result.token).user_id == user.id
    # request password reset
    token = fixture.service.request_password_reset(PasswordResetRequest(email="alice@example.com"))
    assert token is not None
    # complete reset
    fixture.service.complete_password_reset(PasswordResetComplete(token=token, new_password="new-pass-1"))
    # old sessions are revoked
    with pytest.raises(InvalidSessionError):
        fixture.service.session_info(result.token)
    # login with the new password
    new_result = fixture.service.login(LoginRequest(**valid_login("alice", "new-pass-1")))
    assert new_result.user.id == user.id
    # logout
    fixture.service.logout(new_result.token)
    with pytest.raises(InvalidSessionError):
        fixture.service.session_info(new_result.token)
