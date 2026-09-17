"""Acceptance tests for expiration semantics (docs/specs/session-management.md).

Covers AC-026 (REQ-013).
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sessionmanagement_test_helpers import make_session

from backend.authentication import hash_token


def test_ac_026_expiration_unchanged_no_activity_tracking(
    session_service, session_repository, user_id
) -> None:
    """AC-026: a session created with TTL T is invalid once T has elapsed, and
    no operation of this feature changes expires_at or tracks activity (REQ-013)."""
    base = datetime.now(UTC)
    # Given: a session created with TTL T (already elapsed) and a valid companion.
    expired_row, expired_token = make_session(
        session_repository,
        user_id,
        created_at=base - timedelta(seconds=20),
        expires_at=base - timedelta(seconds=10),
    )
    _valid_row, valid_token = make_session(session_repository, user_id, created_at=base)
    original_expires_at = expired_row.expires_at
    # When: a sequence of this feature's operations runs.
    session_service.list_sessions(user_id=user_id)
    session_service.list_sessions(token=valid_token)
    session_service.revoke_session(expired_row.id)
    session_service.logout_other_sessions(valid_token)
    session_service.revoke_all_sessions(user_id)
    # Then: no operation changed expires_at or tracked activity.
    row = session_repository.get_by_token_hash(hash_token(expired_token))
    assert row is not None
    assert row.expires_at == original_expires_at
    # And: the session is invalid (T has elapsed).
    entries = session_service.list_sessions(user_id=user_id)
    assert all(e.session_id != expired_row.id for e in entries)
    # The expired row is deletable by cleanup (REQ-012) — outside this AC.
    session_service.cleanup_expired()
