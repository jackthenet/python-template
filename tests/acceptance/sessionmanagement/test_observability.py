"""Acceptance tests for observability and the secrets policy
(docs/specs/session-management.md).

Covers AC-044, AC-045, NFR-004.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from sessionmanagement_test_helpers import make_session

from backend.authentication import InvalidSessionError, hash_token


def test_ac_044_no_tokens_in_outputs(
    session_service, session_repository, collector, user_id, log_records
) -> None:
    """AC-044: no raw session token or token hash appears in any SessionEntry,
    log record, published event, or error message (only session ids)."""
    log_records.clear()
    base = datetime.now(UTC)
    rows = [
        make_session(session_repository, user_id, created_at=base + timedelta(minutes=i))
        for i in range(3)
    ]
    _, token = rows[1]
    outputs: list[str] = []
    # list entries (both paths)
    for entries in (
        session_service.list_sessions(user_id=user_id),
        session_service.list_sessions(token=token),
    ):
        for entry in entries:
            outputs.append(str(entry))
            outputs.append(repr(entry))
            outputs.append(entry.model_dump_json())
    # events
    session_service.revoke_session(rows[0][0].id)
    session_service.logout_other_sessions(token)
    session_service.revoke_all_sessions(user_id)
    session_service.cleanup_expired()
    for event in collector.events:
        outputs.append(str(event))
        outputs.append(repr(event))
        outputs.append(event.model_dump_json())
    # error message (the token is now revoked)
    with pytest.raises(InvalidSessionError) as excinfo:
        session_service.list_sessions(token=token)
    outputs.append(str(excinfo.value))
    outputs.append(repr(excinfo.value))
    # log records
    for record in log_records:
        outputs.append(str(record["record"]))
    # Then: no raw token or token hash (only session ids)
    for _row, tok in rows:
        for out in outputs:
            assert tok not in out
            assert hash_token(tok) not in out


def test_ac_045_traced_methods_no_tokens_in_logs(
    session_service, session_repository, user_id, log_records
) -> None:
    """AC-045: @logged_class produces entry/exit/exception records for the
    service's methods, and no log record contains a raw token or token hash."""
    log_records.clear()
    row, token = make_session(
        session_repository, user_id, created_at=datetime.now(UTC)
    )
    session_service.list_sessions(token=token)
    session_service.list_sessions(user_id=user_id)
    session_service.revoke_session(row.id)
    with pytest.raises(InvalidSessionError):
        session_service.list_sessions(token="bogus-token")
    joined = "\n".join(str(r) for r in log_records)
    # entry/exit/exception records are produced by @logged_class
    assert "SessionService.list_sessions called" in joined
    assert "SessionService.revoke_session called" in joined
    assert "returned in" in joined
    assert "raised InvalidSessionError" in joined
    # no log record contains a raw token or token hash
    for record in log_records:
        dumped = str(record["record"])
        assert token not in dumped
        assert hash_token(token) not in dumped
        assert "bogus-token" not in dumped
        assert hash_token("bogus-token") not in dumped
    assert token not in joined
    assert hash_token(token) not in joined
    assert "bogus-token" not in joined


def test_nfr_004_traced_service_publishes_events(
    session_service, session_repository, collector, user_id
) -> None:
    """NFR-004: lifecycle events are published to the injected publisher."""
    from backend.sessionmanagement import (
        AllSessionsRevoked,
        ExpiredSessionsDeleted,
        SessionRevoked,
        SessionsListed,
    )

    base = datetime.now(UTC)
    rows = [
        make_session(session_repository, user_id, created_at=base + timedelta(minutes=i))
        for i in range(3)
    ]
    _, token = rows[1]
    make_session(
        session_repository,
        user_id,
        created_at=base - timedelta(days=2),
        expires_at=base - timedelta(days=1),
    )
    session_service.list_sessions(user_id=user_id)
    session_service.revoke_session(rows[0][0].id)
    session_service.logout_other_sessions(token)
    session_service.cleanup_expired()
    for event_type in (SessionsListed, SessionRevoked, AllSessionsRevoked, ExpiredSessionsDeleted):
        assert len(collector.of_type(event_type)) >= 1, (
            f"{event_type.__name__} was not published to the injected publisher"
        )
