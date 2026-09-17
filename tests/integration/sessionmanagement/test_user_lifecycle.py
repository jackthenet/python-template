"""Integration tests for revocation on user lifecycle (docs/specs/session-management.md).

Covers REQ-015: AC-029, AC-030, AC-031 — the feature subscribes to
user-management's ``UserPasswordChanged``, ``UserDeactivated``, and
``UserDeleted`` events and revokes all sessions for the affected user on each
(multi-component interaction: user-management → shared event bus → session
service over the reused authentication store).
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from eventbus_test_helpers import wait_for
from sessionmanagement_test_helpers import build_session_service, db_url, make_session
from usermanagement_test_helpers import valid_create

from backend.authentication import InvalidSessionError
from backend.authentication.repository import SqliteSessionRepository
from backend.eventbus import EventBus
from backend.usermanagement import SqliteUserRepository, UserCreate, UserManager


def _now() -> datetime:
    return datetime.now(UTC)


def test_ac_029_password_change_revokes_all(tmp_path: Path) -> None:
    """AC-029: a successful change_password (UserPasswordChanged) revokes all of the user's sessions."""
    bus = EventBus()
    try:
        manager = UserManager(SqliteUserRepository(db_url(tmp_path, "users.db")), event_bus=bus)
        session_repository = SqliteSessionRepository(db_url(tmp_path, "sessions.db"))
        service = build_session_service(session_repository, event_bus=bus)
        # Given: a user with valid sessions.
        user = manager.create_user(UserCreate(**valid_create()))
        base = _now()
        session_count = 3
        rows = [
            make_session(session_repository, user.id, created_at=base + timedelta(minutes=i))
            for i in range(session_count)
        ]
        assert len(service.list_sessions(user_id=user.id)) == session_count
        # When: change_password succeeds (publishes UserPasswordChanged).
        manager.change_password(user.id, "new-password-1")
        # Then: all sessions for the user are revoked (async subscription delivery).
        assert wait_for(lambda: service.list_sessions(user_id=user.id) == []), (
            "UserPasswordChanged did not revoke all sessions"
        )
        for _, token in rows:
            with pytest.raises(InvalidSessionError):
                service.list_sessions(token=token)
    finally:
        bus.shutdown()


def test_ac_030_deactivation_revokes_all(tmp_path: Path) -> None:
    """AC-030: deactivating the user (UserDeactivated) revokes all of the user's sessions."""
    bus = EventBus()
    try:
        manager = UserManager(SqliteUserRepository(db_url(tmp_path, "users.db")), event_bus=bus)
        session_repository = SqliteSessionRepository(db_url(tmp_path, "sessions.db"))
        service = build_session_service(session_repository, event_bus=bus)
        # Given: a user with valid sessions.
        user = manager.create_user(UserCreate(**valid_create()))
        base = _now()
        session_count = 3
        rows = [
            make_session(session_repository, user.id, created_at=base + timedelta(minutes=i))
            for i in range(session_count)
        ]
        assert len(service.list_sessions(user_id=user.id)) == session_count
        # When: the user is deactivated (publishes UserDeactivated).
        manager.deactivate_user(user.id)
        # Then: all sessions for the user are revoked (async subscription delivery).
        assert wait_for(lambda: service.list_sessions(user_id=user.id) == []), (
            "UserDeactivated did not revoke all sessions"
        )
        for _, token in rows:
            with pytest.raises(InvalidSessionError):
                service.list_sessions(token=token)
    finally:
        bus.shutdown()


def test_ac_031_deletion_revokes_all(tmp_path: Path) -> None:
    """AC-031: deleting the user (UserDeleted) revokes all of the user's sessions."""
    bus = EventBus()
    try:
        manager = UserManager(SqliteUserRepository(db_url(tmp_path, "users.db")), event_bus=bus)
        session_repository = SqliteSessionRepository(db_url(tmp_path, "sessions.db"))
        service = build_session_service(session_repository, event_bus=bus)
        # Given: a user with valid sessions.
        user = manager.create_user(UserCreate(**valid_create()))
        base = _now()
        session_count = 3
        rows = [
            make_session(session_repository, user.id, created_at=base + timedelta(minutes=i))
            for i in range(session_count)
        ]
        assert len(service.list_sessions(user_id=user.id)) == session_count
        # When: the user is deleted (publishes UserDeleted).
        manager.delete_user(user.id)
        # Then: all sessions for the user are revoked (async subscription delivery).
        assert wait_for(lambda: service.list_sessions(user_id=user.id) == []), (
            "UserDeleted did not revoke all sessions"
        )
        for _, token in rows:
            with pytest.raises(InvalidSessionError):
                service.list_sessions(token=token)
    finally:
        bus.shutdown()
