"""AC-006 / AC-015: secret/credential handlers never log argument values, and no
raw tokens, passwords, or hashes appear in any log record.

REQ-006: every traced class or function that handles secrets/credentials uses
``include_args=False`` so arguments never appear in log records.
REQ-015 / NFR-002: no raw tokens, passwords, or hashes appear in any log record.
"""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from logging_coverage_test_helpers import (
    entry_records,
    messages,
)
from backend.authentication.repository import (
    SqlitePasswordResetRepository,
    SqliteSessionRepository,
)
from backend.authentication.tokens import hash_token, new_token
from backend.authentication.tracker import InMemoryAttemptTracker
from backend.usermanagement.models import UserCreate
from backend.usermanagement.repository import SqliteUserRepository
from backend.usermanagement.service import UserManager


def test_secret_handler_args_not_logged(log_records: list[Any], tmp_path: Any) -> None:
    """AC-006: calling a secret/credential handler with arguments does not log the
    argument values."""
    sentinel = "sentinel-secret-abc123"
    db = f"sqlite:///{tmp_path}/secret.db"

    # Exercise each secret/credential handler with the sentinel as an argument.
    # (PyWebAuthnProvider is excluded: its methods require py-webauthn, which is
    # not installed in the test environment — the auth suite uses a fake provider.)
    SqlitePasswordResetRepository(db).get_by_token_hash(sentinel)
    SqliteSessionRepository(db).get_by_token_hash(sentinel)
    InMemoryAttemptTracker(3, timedelta(minutes=5)).record_failure(sentinel)
    hash_token(sentinel)
    new_token()

    # No log record includes the sentinel argument value.
    for msg in messages(log_records):
        assert sentinel not in msg, f"secret argument leaked into log record: {msg}"

    # Tracing is active on these handlers (records were produced).
    assert any("SqlitePasswordResetRepository.get_by_token_hash" in str(r) for r in entry_records(log_records))
    assert any("InMemoryAttemptTracker.record_failure" in str(r) for r in entry_records(log_records))
    assert any(str(r).startswith(">> hash_token called") for r in entry_records(log_records))


def test_no_raw_secrets_in_any_log_record(log_records: list[Any], tmp_path: Any) -> None:
    """AC-015 / NFR-002: no raw tokens, passwords, or hashes appear in any log record."""
    password = "sentinel-password-xyz789"
    db = f"sqlite:///{tmp_path}/users.db"

    # A password handler (UserManager) is exercised with an identifiable password.
    manager = UserManager(SqliteUserRepository(db))
    user = manager.create_user(
        UserCreate(username="alice", email="alice@example.com", password=password, role="member")
    )
    manager.verify_password(user.id, password)

    # A raw token is produced and hashed; neither the token nor the password may leak.
    token = new_token()
    hash_token(token)

    for msg in messages(log_records):
        assert password not in msg, f"raw password leaked into log record: {msg}"
        assert token not in msg, f"raw token leaked into log record: {msg}"

    # Tracing is active on the secret handlers (records were produced).
    assert any("UserManager.create_user" in str(r) for r in entry_records(log_records))
    assert any(str(r).startswith(">> new_token called") for r in entry_records(log_records))
    assert any(str(r).startswith(">> hash_token called") for r in entry_records(log_records))
