"""Integration tests for device identification at login (docs/specs/session-management.md).

Covers REQ-016: AC-008, AC-032 — the login path stores the provided device
fields (``user_agent``/``ip``/``device_name``) and the login method
(``"password"`` | ``"passkey"``) on the issued session row of the reused
authentication store (multi-component interaction: authentication password
login / passkey login → shared ``sessions`` store → session service over the
reused store, REQ-017).
"""

from __future__ import annotations

from pathlib import Path

from authentication_test_helpers import build_auth_service, create_user, valid_login
from sessionmanagement_test_helpers import build_session_service

from backend.authentication import (
    LoginRequest,
    PasskeyLoginBegin,
    PasskeyLoginComplete,
    PasskeyRegistrationComplete,
)


def test_ac_008_login_stores_device_fields(tmp_path: Path) -> None:
    """AC-008: a login with device fields provided -> the list entry exposes them and login_method is "password"."""
    fixture = build_auth_service(tmp_path)
    create_user(fixture.user_manager)
    # Given: a login with user_agent/ip/device_name provided.
    result = fixture.service.login(
        LoginRequest(
            **valid_login(),
            user_agent="Mozilla/5.0 (X11; Linux x86_64) test-agent/1.0",
            ip="203.0.113.7",
            device_name="Test Laptop",
        )
    )
    # When: list_sessions is called for that session (over the reused store, REQ-017).
    service = build_session_service(fixture.session_repository)
    entries = service.list_sessions(token=result.token)
    # Then: the entry exposes the provided values and login_method is "password".
    assert len(entries) == 1
    entry = entries[0]
    assert entry.is_current is True
    assert entry.user_agent == "Mozilla/5.0 (X11; Linux x86_64) test-agent/1.0"
    assert entry.ip == "203.0.113.7"
    assert entry.device_name == "Test Laptop"
    assert entry.login_method == "password"


def test_ac_032_passkey_login_stores_method(tmp_path: Path) -> None:
    """AC-032: a passkey login (authentication REQ-015) -> the issued session row's login_method is "passkey"."""
    fixture = build_auth_service(tmp_path)  # FakeWebAuthnProvider by default
    user = create_user(fixture.user_manager)
    # Given: a passkey login (authentication REQ-015).
    fixture.service.complete_passkey_registration(
        PasskeyRegistrationComplete(user_id=user.id, response={})
    )
    fixture.service.begin_passkey_login(PasskeyLoginBegin(credential_id="fake-credential"))
    result = fixture.service.complete_passkey_login(
        PasskeyLoginComplete(credential_id="fake-credential", response={"id": "fake"})
    )
    # When: the issued session row is inspected (via the feature over the reused store).
    service = build_session_service(fixture.session_repository)
    entries = service.list_sessions(token=result.token)
    # Then: login_method is "passkey".
    assert len(entries) == 1
    entry = entries[0]
    assert entry.is_current is True
    assert entry.login_method == "passkey"
