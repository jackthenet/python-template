"""Acceptance tests for session revocation (docs/specs/session-management.md).

Covers AC-014, AC-015, AC-016, AC-017, AC-018, AC-019, AC-020, AC-021,
AC-022, AC-023, EDGE-001, EDGE-002, EDGE-003, EDGE-004, EDGE-005.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from sessionmanagement_test_helpers import make_session

from backend.authentication import InvalidSessionError


def _now() -> datetime:
    return datetime.now(UTC)


def test_ac_014_revoke_session_revokes(session_service, session_repository, user_id) -> None:
    """AC-014: revoke_session revokes the session; it no longer appears in list_sessions."""
    base = _now()
    rows = [
        make_session(session_repository, user_id, created_at=base + timedelta(minutes=i))
        for i in range(2)
    ]
    target_row, _ = rows[0]
    other_row, _ = rows[1]
    session_service.revoke_session(target_row.id)
    entries = session_service.list_sessions(user_id=user_id)
    ids = {e.session_id for e in entries}
    assert target_row.id not in ids
    assert other_row.id in ids


def test_ac_015_revoke_unknown_id_noop(session_service) -> None:
    """AC-015: revoke_session with a session id that does not exist raises no error (no-op)."""
    session_service.revoke_session(uuid4())


def test_ac_016_revoke_already_revoked_noop(
    session_service, session_repository, user_id
) -> None:
    """AC-016: revoke_session with an already-revoked session id raises no error (no-op)."""
    row, _ = make_session(session_repository, user_id, created_at=_now(), revoked=True)
    session_service.revoke_session(row.id)


def test_ac_017_logout_all_revokes_including_caller(
    session_service, session_repository, user_id
) -> None:
    """AC-017: logout_all_sessions revokes all 3 sessions; the token is immediately unusable."""
    base = _now()
    rows = [
        make_session(session_repository, user_id, created_at=base + timedelta(minutes=i))
        for i in range(3)
    ]
    _, caller_token = rows[1]
    session_service.logout_all_sessions(caller_token)
    assert session_service.list_sessions(user_id=user_id) == []
    # the token is immediately unusable
    with pytest.raises(InvalidSessionError):
        session_service.list_sessions(token=caller_token)


def test_ac_018_logout_all_invalid_token_raises(
    session_service, session_repository, user_id
) -> None:
    """AC-018: logout_all_sessions with an unknown, revoked, or expired token raises."""
    base = _now()
    # unknown token
    with pytest.raises(InvalidSessionError):
        session_service.logout_all_sessions("A" * 43)
    # revoked token
    _, revoked_token = make_session(session_repository, user_id, created_at=base, revoked=True)
    with pytest.raises(InvalidSessionError):
        session_service.logout_all_sessions(revoked_token)
    # expired token
    _, expired_token = make_session(
        session_repository,
        user_id,
        created_at=base - timedelta(days=2),
        expires_at=base - timedelta(days=1),
    )
    with pytest.raises(InvalidSessionError):
        session_service.logout_all_sessions(expired_token)


def test_ac_019_logout_other_keeps_caller(
    session_service, session_repository, user_id
) -> None:
    """AC-019: logout_other_sessions revokes the other 2; the token's session remains valid."""
    base = _now()
    rows = [
        make_session(session_repository, user_id, created_at=base + timedelta(minutes=i))
        for i in range(3)
    ]
    caller_row, caller_token = rows[1]
    session_service.logout_other_sessions(caller_token)
    entries = session_service.list_sessions(user_id=user_id)
    assert [e.session_id for e in entries] == [caller_row.id]
    # the caller's session is still valid through the token path
    token_entries = session_service.list_sessions(token=caller_token)
    assert [e.session_id for e in token_entries] == [caller_row.id]


def test_ac_020_logout_other_only_caller_noop(
    session_service, session_repository, user_id
) -> None:
    """AC-020: logout_other_sessions with only the caller's session leaves it valid."""
    row, token = make_session(session_repository, user_id, created_at=_now())
    session_service.logout_other_sessions(token)
    entries = session_service.list_sessions(token=token)
    assert [e.session_id for e in entries] == [row.id]


def test_ac_021_revoke_all_returns_count(
    session_service, session_repository, user_id
) -> None:
    """AC-021: revoke_all_sessions revokes all 3 sessions and returns 3."""
    base = _now()
    count = 3
    for i in range(count):
        make_session(session_repository, user_id, created_at=base + timedelta(minutes=i))
    revoked = session_service.revoke_all_sessions(user_id)
    assert revoked == count
    assert session_service.list_sessions(user_id=user_id) == []


def test_ac_022_revoke_all_excludes_session(
    session_service, session_repository, user_id
) -> None:
    """AC-022: revoke_all_sessions with an exclusion revokes the other 2; X remains valid."""
    base = _now()
    count = 3
    rows = [
        make_session(session_repository, user_id, created_at=base + timedelta(minutes=i))
        for i in range(count)
    ]
    keep_row, _ = rows[1]
    revoked = session_service.revoke_all_sessions(user_id, exclude_session_id=keep_row.id)
    assert revoked == count - 1
    entries = session_service.list_sessions(user_id=user_id)
    assert [e.session_id for e in entries] == [keep_row.id]


def test_ac_023_revoke_all_zero_sessions(session_service, user_id) -> None:
    """AC-023: revoke_all_sessions for a user with zero valid sessions returns 0 (no error)."""
    revoked = session_service.revoke_all_sessions(user_id)
    assert revoked == 0


def test_edge_001_zero_sessions_empty_and_noop(session_service, user_id) -> None:
    """EDGE-001: zero valid sessions — list is empty, revoke-all returns 0, token ops raise."""
    assert session_service.list_sessions(user_id=user_id) == []
    assert session_service.revoke_all_sessions(user_id) == 0
    # a valid token implies a valid session (authentication INV-002), so no valid token
    # exists in this state — any token is invalid for the token-based operations
    with pytest.raises(InvalidSessionError):
        session_service.logout_all_sessions("A" * 43)
    with pytest.raises(InvalidSessionError):
        session_service.logout_other_sessions("A" * 43)


def test_edge_002_revoke_unknown_id_noop(session_service, collector) -> None:
    """EDGE-002: revoke_session with an unknown session id is a no-op (no error, no event)."""
    from backend.sessionmanagement import SessionRevoked

    session_service.revoke_session(uuid4())
    assert collector.of_type(SessionRevoked) == []


def test_edge_003_revoke_already_revoked_noop(
    session_service, session_repository, collector, user_id
) -> None:
    """EDGE-003: revoke_session with an already-revoked session id is a no-op (no error, no event)."""
    from backend.sessionmanagement import SessionRevoked

    row, _ = make_session(session_repository, user_id, created_at=_now(), revoked=True)
    session_service.revoke_session(row.id)
    assert collector.of_type(SessionRevoked) == []


def test_edge_004_logout_all_self_lockout(
    session_service, session_repository, user_id
) -> None:
    """EDGE-004: logout_all_sessions revokes the caller's own session; the token becomes unusable."""
    _, token = make_session(session_repository, user_id, created_at=_now())
    session_service.logout_all_sessions(token)
    with pytest.raises(InvalidSessionError):
        session_service.list_sessions(token=token)
    assert session_service.list_sessions(user_id=user_id) == []


def test_edge_005_logout_other_only_caller(
    session_service, session_repository, user_id
) -> None:
    """EDGE-005: logout_other_sessions with only the caller's session revokes nothing."""
    row, token = make_session(session_repository, user_id, created_at=_now())
    session_service.logout_other_sessions(token)
    entries = session_service.list_sessions(token=token)
    assert [e.session_id for e in entries] == [row.id]
