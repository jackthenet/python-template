"""Acceptance tests for passkey/WebAuthn (docs/specs/authentication.md, AC-022 .. AC-029)."""

from __future__ import annotations

import pytest

from authentication_test_helpers import create_user, valid_login

from backend.authentication import (
    LoginRequest,
    PasskeyHijackError,
    PasskeyLoginBegin,
    PasskeyLoginComplete,
    PasskeyRegistrationBegin,
    PasskeyRegistrationComplete,
)


def test_ac_022_begin_registration_options(auth) -> None:
    user = create_user(auth.user_manager)
    options = auth.service.begin_passkey_registration(
        PasskeyRegistrationBegin(user_id=user.id, username="alice")
    )
    assert isinstance(options, dict)
    assert options  # non-empty WebAuthn registration options


def test_ac_023_complete_registration_stores(auth) -> None:
    user = create_user(auth.user_manager)
    auth.service.begin_passkey_registration(PasskeyRegistrationBegin(user_id=user.id, username="alice"))
    read = auth.service.complete_passkey_registration(
        PasskeyRegistrationComplete(user_id=user.id, response={"id": "fake", "rawId": "fake"})
    )
    assert read.credential_id == "fake-credential"
    assert read.transports == ["internal"]
    # the credential is stored
    stored = auth.webauthn_repository.get_by_credential_id("fake-credential")
    assert stored is not None
    assert stored.user_id == user.id


def test_ac_024_begin_login_options(auth) -> None:
    user = create_user(auth.user_manager)
    auth.service.complete_passkey_registration(
        PasskeyRegistrationComplete(user_id=user.id, response={})
    )
    options = auth.service.begin_passkey_login(PasskeyLoginBegin(credential_id="fake-credential"))
    assert isinstance(options, dict)
    assert options  # non-empty WebAuthn authentication options


def test_ac_025_complete_login_issues_session(auth) -> None:
    user = create_user(auth.user_manager)
    auth.service.complete_passkey_registration(PasskeyRegistrationComplete(user_id=user.id, response={}))
    auth.service.begin_passkey_login(PasskeyLoginBegin(credential_id="fake-credential"))
    result = auth.service.complete_passkey_login(
        PasskeyLoginComplete(credential_id="fake-credential", response={"id": "fake"})
    )
    assert result.user.id == user.id
    # a session token is issued
    info = auth.service.session_info(result.token)
    assert info.user_id == user.id
    # the stored sign count is updated to the response's sign count
    stored = auth.webauthn_repository.get_by_credential_id("fake-credential")
    assert stored.sign_count == 1  # the fake provider's assertion sign count


def test_ac_026_hijack_detected(auth) -> None:
    user = create_user(auth.user_manager)
    provider = auth.webauthn_provider
    auth.service.complete_passkey_registration(PasskeyRegistrationComplete(user_id=user.id, response={}))
    auth.service.begin_passkey_login(PasskeyLoginBegin(credential_id="fake-credential"))
    auth.service.complete_passkey_login(PasskeyLoginComplete(credential_id="fake-credential", response={}))
    # the stored sign count is now 1; a response sign count of 0 is a regression
    provider.sign_count = 0
    with pytest.raises(PasskeyHijackError):
        auth.service.complete_passkey_login(PasskeyLoginComplete(credential_id="fake-credential", response={}))
    # no session is issued and the sign count is not updated to the hijacked value
    stored = auth.webauthn_repository.get_by_credential_id("fake-credential")
    assert stored.sign_count == 1


def test_ac_027_list_passkeys(auth) -> None:
    user = create_user(auth.user_manager)
    auth.service.complete_passkey_registration(PasskeyRegistrationComplete(user_id=user.id, response={}))
    listed = auth.service.list_passkeys(user.id)
    assert len(listed) == 1
    assert listed[0].credential_id == "fake-credential"


def test_ac_028_delete_passkey(auth) -> None:
    user = create_user(auth.user_manager)
    auth.service.complete_passkey_registration(PasskeyRegistrationComplete(user_id=user.id, response={}))
    auth.service.delete_passkey(user.id, "fake-credential")
    assert auth.webauthn_repository.get_by_credential_id("fake-credential") is None
    assert auth.service.list_passkeys(user.id) == []


def test_ac_029_password_and_passkey_coexist(auth) -> None:
    user = create_user(auth.user_manager)
    auth.service.complete_passkey_registration(PasskeyRegistrationComplete(user_id=user.id, response={}))
    # password login works
    assert auth.service.login(LoginRequest(**valid_login("alice"))).user.id == user.id
    # passkey login works
    result = auth.service.complete_passkey_login(
        PasskeyLoginComplete(credential_id="fake-credential", response={})
    )
    assert result.user.id == user.id
    # and the password still works after passkey use
    assert auth.service.login(LoginRequest(**valid_login("alice"))).user.id == user.id
