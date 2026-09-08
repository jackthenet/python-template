"""Acceptance tests for representations (docs/specs/authentication.md, AC-034)."""

from __future__ import annotations

from authentication_test_helpers import create_user, valid_login

from backend.authentication import LoginRequest, PasskeyRegistrationComplete


def test_ac_034_no_hash_in_representations(auth) -> None:
    user = create_user(auth.user_manager)
    result = auth.service.login(LoginRequest(**valid_login("alice")))
    credential = auth.service.complete_passkey_registration(
        PasskeyRegistrationComplete(user_id=user.id, response={})
    )
    reps = [
        ("LoginResult", result),
        ("UserRead", result.user),
        ("SessionInfo", result.session),
        ("WebAuthnCredentialRead", credential),
        ("SessionInfo (session_info)", auth.service.session_info(result.token)),
    ]
    for name, rep in reps:
        fields = set(rep.model_dump().keys())
        assert "password_hash" not in fields, name
    # no raw session token except the initial LoginResult.token
    assert "token" not in set(result.session.model_dump().keys())
    assert "token" not in set(credential.model_dump().keys())
