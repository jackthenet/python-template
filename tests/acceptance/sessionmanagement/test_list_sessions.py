"""Acceptance tests for session listing (docs/specs/session-management.md).

Covers AC-001, AC-002, AC-004, AC-005, AC-006, AC-007, AC-009, AC-010,
AC-011, AC-012, EDGE-006, EDGE-007.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from sessionmanagement_test_helpers import make_session

from backend.authentication import InvalidSessionError

# The spec's hardcoded default for sessionmanagement.max_listed_sessions (REQ-019).
_DEFAULT_MAX_LISTED = 100


def _now() -> datetime:
    return datetime.now(UTC)


def test_ac_001_list_token_returns_entries_with_current_flag(
    session_service, session_repository, user_id
) -> None:
    """AC-001: a valid token lists the user's sessions; the token's entry has is_current True."""
    base = _now()
    rows = [
        make_session(session_repository, user_id, created_at=base + timedelta(minutes=i))
        for i in range(3)
    ]
    current_row, current_token = rows[1]
    entries = session_service.list_sessions(token=current_token)
    assert len(entries) == len(rows)
    by_id = {e.session_id: e for e in entries}
    assert by_id[current_row.id].is_current is True
    for row, _ in rows:
        if row.id != current_row.id:
            assert by_id[row.id].is_current is False


def test_ac_002_list_user_id_admin_all_not_current(
    session_service, session_repository, user_id
) -> None:
    """AC-002: the admin (user_id) path lists all sessions with is_current False."""
    base = _now()
    rows = [
        make_session(session_repository, user_id, created_at=base + timedelta(minutes=i))
        for i in range(3)
    ]
    entries = session_service.list_sessions(user_id=user_id)
    assert len(entries) == len(rows)
    assert all(e.is_current is False for e in entries)
    assert {e.session_id for e in entries} == {row.id for row, _ in rows}


def test_ac_004_list_invalid_token_raises(session_service, session_repository, user_id) -> None:
    """AC-004: an unknown, revoked, or expired token raises InvalidSessionError."""
    base = _now()
    # unknown token
    with pytest.raises(InvalidSessionError):
        session_service.list_sessions(token="A" * 43)
    # revoked token
    _, revoked_token = make_session(session_repository, user_id, created_at=base, revoked=True)
    with pytest.raises(InvalidSessionError):
        session_service.list_sessions(token=revoked_token)
    # expired token
    _, expired_token = make_session(
        session_repository,
        user_id,
        created_at=base - timedelta(days=2),
        expires_at=base - timedelta(days=1),
    )
    with pytest.raises(InvalidSessionError):
        session_service.list_sessions(token=expired_token)


def test_ac_005_list_excludes_expired_rows(
    session_service, session_repository, user_id
) -> None:
    """AC-005: only the 2 valid sessions are returned (the expired one is not)."""
    base = _now()
    valid = [
        make_session(session_repository, user_id, created_at=base + timedelta(minutes=i))
        for i in range(2)
    ]
    make_session(
        session_repository,
        user_id,
        created_at=base - timedelta(days=2),
        expires_at=base - timedelta(days=1),
    )
    entries = session_service.list_sessions(user_id=user_id)
    assert {e.session_id for e in entries} == {row.id for row, _ in valid}


def test_ac_006_list_zero_sessions_empty(session_service, user_id) -> None:
    """AC-006: a user with zero valid sessions yields an empty list (no error)."""
    entries = session_service.list_sessions(user_id=user_id)
    assert entries == []


def test_ac_007_pre_feature_row_null_device_fields(
    session_service, session_repository, user_id
) -> None:
    """AC-007: a pre-feature row (device columns NULL) yields all-None device fields."""
    row, token = make_session(session_repository, user_id, created_at=_now())
    entries = session_service.list_sessions(token=token)
    assert len(entries) == 1
    entry = entries[0]
    assert entry.session_id == row.id
    assert entry.created_at == row.created_at
    assert entry.expires_at == row.expires_at
    assert entry.user_agent is None
    assert entry.ip is None
    assert entry.device_name is None
    assert entry.login_method is None
    assert entry.is_current is True


def test_ac_009_list_current_session_pinned_first(
    session_service, session_repository, user_id
) -> None:
    """AC-009: the current (oldest) session is pinned first; the rest are created_at descending."""
    base = _now()
    rows = [
        make_session(session_repository, user_id, created_at=base + timedelta(minutes=i * 10))
        for i in range(3)
    ]
    oldest_row, oldest_token = rows[0]
    entries = session_service.list_sessions(token=oldest_token)
    assert [e.session_id for e in entries] == [oldest_row.id, rows[2][0].id, rows[1][0].id]


def test_ac_010_list_ordered_created_at_desc(
    session_service, session_repository, user_id
) -> None:
    """AC-010: the admin path orders entries created_at descending (newest first)."""
    base = _now()
    rows = [
        make_session(session_repository, user_id, created_at=base + timedelta(minutes=i * 10))
        for i in range(3)
    ]
    entries = session_service.list_sessions(user_id=user_id)
    assert [e.session_id for e in entries] == [rows[2][0].id, rows[1][0].id, rows[0][0].id]


def test_ac_011_list_default_limit_100(session_service, session_repository, user_id) -> None:
    """AC-011: the default max_listed_sessions (100) bounds the list."""
    base = _now()
    for i in range(150):
        make_session(session_repository, user_id, created_at=base + timedelta(seconds=i))
    entries = session_service.list_sessions(user_id=user_id)
    assert len(entries) == _DEFAULT_MAX_LISTED


def test_ac_012_list_explicit_limit_truncates(
    session_service, session_repository, user_id
) -> None:
    """AC-012: an explicit limit truncates the list."""
    base = _now()
    for i in range(5):
        make_session(session_repository, user_id, created_at=base + timedelta(minutes=i))
    limit = 2
    entries = session_service.list_sessions(user_id=user_id, limit=limit)
    assert len(entries) == limit


def test_edge_006_pre_feature_null_fields(
    session_service, session_repository, user_id
) -> None:
    """EDGE-006: pre-existing rows (device fields NULL) list without error, all-None."""
    base = _now()
    count = 2
    for i in range(count):
        make_session(session_repository, user_id, created_at=base + timedelta(minutes=i))
    entries = session_service.list_sessions(user_id=user_id)
    assert len(entries) == count
    for e in entries:
        assert e.user_agent is None
        assert e.ip is None
        assert e.device_name is None
        assert e.login_method is None


def test_edge_007_expired_rows_excluded(
    session_service, session_repository, user_id
) -> None:
    """EDGE-007: expired-but-not-cleaned rows are excluded from the list (valid-only)."""
    base = _now()
    valid_row, _ = make_session(session_repository, user_id, created_at=base)
    expired_row, _ = make_session(
        session_repository,
        user_id,
        created_at=base - timedelta(days=2),
        expires_at=base - timedelta(days=1),
    )
    entries = session_service.list_sessions(user_id=user_id)
    ids = {e.session_id for e in entries}
    assert expired_row.id not in ids
    assert valid_row.id in ids
