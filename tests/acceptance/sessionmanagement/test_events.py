"""Acceptance tests for typed events (docs/specs/session-management.md, AC-034, AC-035, AC-037)."""

from __future__ import annotations

import time
from datetime import UTC, datetime, timedelta

from sessionmanagement_test_helpers import build_session_service, make_session

from backend.authentication import LoginSucceeded
from backend.eventbus import get_event_bus, reset_event_bus
from backend.usermanagement import UserPasswordChanged


def test_ac_037_sessions_listed_event(session_service, session_repository, collector, user_id) -> None:
    """AC-037: a successful list_sessions publishes SessionsListed(user_id, count)."""
    from backend.sessionmanagement import SessionsListed

    base = datetime.now(UTC)
    count = 3
    for i in range(count):
        make_session(session_repository, user_id, created_at=base + timedelta(minutes=i))
    entries = session_service.list_sessions(user_id=user_id)
    listed = collector.of_type(SessionsListed)
    assert len(listed) == 1
    assert listed[0].user_id == user_id
    assert listed[0].count == len(entries) == count


def test_ac_034_session_revoked_event(session_service, session_repository, collector, user_id) -> None:
    """AC-034: a successful revoke_session publishes SessionRevoked(user_id, session_id)."""
    from backend.sessionmanagement import SessionRevoked

    row, _ = make_session(session_repository, user_id, created_at=datetime.now(UTC))
    session_service.revoke_session(row.id)
    revoked = collector.of_type(SessionRevoked)
    assert len(revoked) == 1
    assert revoked[0].user_id == user_id
    assert revoked[0].session_id == row.id


def test_ac_035_all_sessions_revoked_event(session_service, session_repository, collector, user_id) -> None:
    """AC-035: the revoke-all operations publish AllSessionsRevoked with the correct excluded id;
    an operation that revokes 0 sessions publishes no event."""
    from backend.sessionmanagement import AllSessionsRevoked

    base = datetime.now(UTC)
    expected = 0

    # logout_all_sessions: excluded id None
    rows = [make_session(session_repository, user_id, created_at=base + timedelta(minutes=i)) for i in range(3)]
    _, token = rows[1]
    session_service.logout_all_sessions(token)
    expected += 1
    events = collector.of_type(AllSessionsRevoked)
    assert len(events) == expected
    assert events[-1].user_id == user_id
    assert events[-1].excluded_session_id is None

    # logout_other_sessions: excluded id = the caller's session
    rows = [make_session(session_repository, user_id, created_at=base + timedelta(minutes=i)) for i in range(3, 6)]
    caller_row, token = rows[1]
    session_service.logout_other_sessions(token)
    expected += 1
    events = collector.of_type(AllSessionsRevoked)
    assert len(events) == expected
    assert events[-1].user_id == user_id
    assert events[-1].excluded_session_id == caller_row.id

    # revoke_all_sessions without exclusion: excluded id None
    for i in range(6, 9):
        make_session(session_repository, user_id, created_at=base + timedelta(minutes=i))
    session_service.revoke_all_sessions(user_id)
    expected += 1
    events = collector.of_type(AllSessionsRevoked)
    assert len(events) == expected
    assert events[-1].user_id == user_id
    assert events[-1].excluded_session_id is None

    # revoke_all_sessions with exclusion: excluded id = the excluded session
    rows = [make_session(session_repository, user_id, created_at=base + timedelta(minutes=i)) for i in range(9, 12)]
    keep_row, keep_token = rows[1]
    session_service.revoke_all_sessions(user_id, exclude_session_id=keep_row.id)
    expected += 1
    events = collector.of_type(AllSessionsRevoked)
    assert len(events) == expected
    assert events[-1].user_id == user_id
    assert events[-1].excluded_session_id == keep_row.id

    # 0 sessions revoked: no event (logout_other_sessions when the caller is the only session)
    session_service.logout_other_sessions(keep_token)
    events = collector.of_type(AllSessionsRevoked)
    assert len(events) == expected

    # the exclusion left one valid session: revoking it publishes (count > 0),
    # then re-running with 0 sessions revoked publishes no event
    session_service.revoke_all_sessions(user_id)
    expected += 1
    events = collector.of_type(AllSessionsRevoked)
    assert len(events) == expected
    session_service.revoke_all_sessions(user_id)
    events = collector.of_type(AllSessionsRevoked)
    assert len(events) == expected


def test_ac_036_expired_sessions_deleted_event(session_service, session_repository, collector, user_id) -> None:
    """AC-036: cleanup_expired publishes ExpiredSessionsDeleted(n) when n > 0;
    deleting 0 rows publishes no event."""
    from backend.sessionmanagement import ExpiredSessionsDeleted

    expired_rows = 3
    base = datetime.now(UTC)
    for i in range(expired_rows):
        make_session(
            session_repository,
            user_id,
            created_at=base - timedelta(days=2, minutes=i),
            expires_at=base - timedelta(days=1, minutes=i),
        )
    deleted = session_service.cleanup_expired()
    events = collector.of_type(ExpiredSessionsDeleted)
    assert len(events) == 1
    assert events[0].count == deleted == expired_rows

    # 0 rows deleted: no event
    session_service.cleanup_expired()
    events = collector.of_type(ExpiredSessionsDeleted)
    assert len(events) == 1


def test_ac_038_none_publisher_no_events_no_subscriptions(session_repository, settings_registry, user_id) -> None:
    """AC-038: a None publisher means no event is published, no error is
    raised, and no subscription to user-management or authentication events
    occurs."""
    service = build_session_service(session_repository, event_bus=None, settings_registry=settings_registry)
    base = datetime.now(UTC)
    rows = [make_session(session_repository, user_id, created_at=base + timedelta(minutes=i)) for i in range(3)]
    _, token = rows[1]
    # When: any operation runs — no error is raised with a None publisher.
    service.list_sessions(user_id=user_id)
    service.list_sessions(token=token)
    service.revoke_session(rows[0].id)
    service.logout_all_sessions(token)
    service.revoke_all_sessions(user_id)
    service.cleanup_expired()
    # Then: no subscription to user-management or authentication events occurs —
    # publishing them on the shared bus does not trigger the service.
    num_sessions = 3
    fresh_base = datetime.now(UTC)
    for i in range(num_sessions):
        make_session(session_repository, user_id, created_at=fresh_base + timedelta(minutes=i))
    reset_event_bus()
    try:
        bus = get_event_bus()
        bus.publish(UserPasswordChanged(user_id=user_id))
        bus.publish(LoginSucceeded(user_id=user_id, method="password"))
        time.sleep(1.0)  # grace period for async dispatch
        entries = service.list_sessions(user_id=user_id)
        assert len(entries) == num_sessions  # no revocation occurred
    finally:
        reset_event_bus()
