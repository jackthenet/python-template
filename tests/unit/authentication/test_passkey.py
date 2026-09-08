"""Unit tests for passkey edge cases (docs/specs/authentication.md, EDGE-013 .. EDGE-016)."""

from __future__ import annotations

import pytest
from authentication_test_helpers import create_user

from backend.authentication import (
    InvalidPasskeyResponseError,
    PasskeyCredentialNotFoundError,
    PasskeyHijackError,
    PasskeyLoginBegin,
    PasskeyLoginComplete,
    PasskeyRegistrationComplete,
)


def test_edge_013_registration_invalid_response(auth) -> None:
    user = create_user(auth.user_manager)
    auth.webauthn_provider.fail_registration = True
    with pytest.raises(InvalidPasskeyResponseError):
        auth.service.complete_passkey_registration(
            PasskeyRegistrationComplete(user_id=user.id, response={})
        )
    # nothing is stored
    assert auth.webauthn_repository.get_by_credential_id("fake-credential") is None


def test_edge_014_begin_login_unregistered_credential(auth) -> None:
    with pytest.raises(PasskeyCredentialNotFoundError):
        auth.service.begin_passkey_login(PasskeyLoginBegin(credential_id="no-such-credential"))


def test_edge_015_hijack_detected(auth) -> None:
    user = create_user(auth.user_manager)
    provider = auth.webauthn_provider
    auth.service.complete_passkey_registration(PasskeyRegistrationComplete(user_id=user.id, response={}))
    auth.service.begin_passkey_login(PasskeyLoginBegin(credential_id="fake-credential"))
    auth.service.complete_passkey_login(PasskeyLoginComplete(credential_id="fake-credential", response={}))
    # a response sign count lower than the stored 1 is a regression
    provider.sign_count = 0
    with pytest.raises(PasskeyHijackError):
        auth.service.complete_passkey_login(PasskeyLoginComplete(credential_id="fake-credential", response={}))


def test_edge_016_login_failed_assertion(auth) -> None:
    user = create_user(auth.user_manager)
    auth.webauthn_provider.fail_assertion = True
    auth.service.complete_passkey_registration(PasskeyRegistrationComplete(user_id=user.id, response={}))
    auth.service.begin_passkey_login(PasskeyLoginBegin(credential_id="fake-credential"))
    with pytest.raises(InvalidPasskeyResponseError):
        auth.service.complete_passkey_login(PasskeyLoginComplete(credential_id="fake-credential", response={}))
