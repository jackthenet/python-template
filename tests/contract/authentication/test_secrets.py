"""Contract tests for secrets (docs/specs/authentication.md, NFR-002)."""

from __future__ import annotations

from authentication_test_helpers import create_user, valid_login

from backend.authentication import LoginRequest, PasswordResetComplete, PasswordResetRequest


def test_nfr_002_no_secrets_in_logs_or_events(auth, log_records) -> None:
    create_user(auth.user_manager)
    password = "correct-horse-1"
    result = auth.service.login(LoginRequest(**valid_login("alice", password)))
    token = result.token
    reset_token = auth.service.request_password_reset(PasswordResetRequest(email="alice@example.com"))
    assert reset_token is not None
    auth.service.complete_password_reset(
        PasswordResetComplete(token=reset_token, new_password="new-pass-1")
    )
    auth.service.logout(token)
    # passwords, raw session tokens, and raw reset tokens never appear in
    # log records or events
    for record in log_records:
        text = str(record)
        assert password not in text
        assert token not in text
        assert reset_token not in text
    for event in auth.collector.events:
        data = event.model_dump_json()
        assert password not in data
        assert token not in data
        assert reset_token not in data
