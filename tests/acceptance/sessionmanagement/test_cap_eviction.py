"""Acceptance tests for the per-user session cap (docs/specs/session-management.md).

Covers AC-027, AC-028, EDGE-011 (REQ-014).

The cap is enforced event-driven on authentication's ``LoginSucceeded``
(REQ-014, ADR-063): the service subscribes its eviction handler to the shared
event bus at construction, so the shared bus is reset around each test
(autouse ordering puts this before the ``session_service`` fixture) and the
test publishes ``LoginSucceeded`` to that same shared bus. Bus dispatch is
asynchronous and in subscription order, so a marker handler subscribed after
the service proves the eviction handler has already run when it fires.
"""

from __future__ import annotations

import threading
from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest
from sessionmanagement_test_helpers import make_session

from backend.authentication import InvalidSessionError, LoginSucceeded
from backend.eventbus import get_event_bus, reset_event_bus
from backend.settings import SettingDefinition, SettingKind, SettingsRegistry

_MAX_SESSIONS_PER_USER_KEY = "sessionmanagement.max_sessions_per_user"


@pytest.fixture(autouse=True)
def fresh_shared_bus():
    """Reset the shared event bus around each test (REQ-014, ADR-063).

    The service subscribes its ``LoginSucceeded`` eviction handler to the
    shared bus at construction; autouse fixtures run before the
    ``session_service`` fixture, so the service always subscribes to a fresh
    bus. The post-test reset removes this file's handlers from the singleton.
    """
    reset_event_bus()
    yield
    reset_event_bus()


def _now() -> datetime:
    return datetime.now(UTC)


def _set_max_sessions_per_user(settings_registry: SettingsRegistry, value: int) -> None:
    """Register the spec's max_sessions_per_user definition and set the value live (REQ-019)."""
    settings_registry.register(
        SettingDefinition(
            key=_MAX_SESSIONS_PER_USER_KEY,
            kind=SettingKind.NUMBER,
            default=5,
            min_value=1,
            category="sessionmanagement",
        )
    )
    settings_registry.set_value(_MAX_SESSIONS_PER_USER_KEY, value)


def _login(user_id: UUID) -> None:
    """Publish a login's ``LoginSucceeded`` to the shared bus and wait for dispatch.

    The marker handler is subscribed after the service's eviction handler, and
    the bus dispatches in subscription order, so when the marker fires the
    eviction handler has already run (deterministic for no-eviction asserts).
    """
    dispatched = threading.Event()
    bus = get_event_bus()
    bus.subscribe(LoginSucceeded, lambda event: dispatched.set())
    bus.publish(LoginSucceeded(user_id=user_id, method="password"))
    assert dispatched.wait(timeout=5.0), "LoginSucceeded was not dispatched"


def test_ac_027_cap_evicts_oldest_at_sixth_login(
    session_service, session_repository, settings_registry, user_id
) -> None:
    """AC-027: cap 5 with 5 valid sessions — the 6th login revokes the oldest; the user has 5 valid sessions."""
    cap = 5
    _set_max_sessions_per_user(settings_registry, cap)
    base = _now()
    rows = [
        make_session(session_repository, user_id, created_at=base + timedelta(minutes=i))
        for i in range(cap)
    ]
    oldest_row, oldest_token = rows[0]
    # the 6th login issues a new session, then LoginSucceeded is dispatched
    new_row, _ = make_session(session_repository, user_id, created_at=base + timedelta(minutes=cap))
    _login(user_id)
    entries = session_service.list_sessions(user_id=user_id)
    ids = {e.session_id for e in entries}
    assert oldest_row.id not in ids
    assert ids == {r[0].id for r in rows[1:]} | {new_row.id}
    assert len(entries) == cap
    # the oldest session's token is immediately unusable
    with pytest.raises(InvalidSessionError):
        session_service.list_sessions(token=oldest_token)


def test_ac_028_no_eviction_below_cap(
    session_service, session_repository, settings_registry, user_id
) -> None:
    """AC-028: cap 5 with 3 valid sessions — a login revokes nothing; the user has 4 valid sessions."""
    cap = 5
    existing = 3
    _set_max_sessions_per_user(settings_registry, cap)
    base = _now()
    rows = [
        make_session(session_repository, user_id, created_at=base + timedelta(minutes=i))
        for i in range(existing)
    ]
    new_row, _ = make_session(session_repository, user_id, created_at=base + timedelta(minutes=existing))
    _login(user_id)
    entries = session_service.list_sessions(user_id=user_id)
    assert len(entries) == existing + 1
    assert {e.session_id for e in entries} == {r[0].id for r in rows} | {new_row.id}


def test_edge_011_cap_eviction_at_exact_cap(
    session_service, session_repository, settings_registry, user_id
) -> None:
    """EDGE-011: user already at exactly the cap — the login evicts exactly the oldest session and keeps the new one."""
    cap = 5
    _set_max_sessions_per_user(settings_registry, cap)
    base = _now()
    rows = [
        make_session(session_repository, user_id, created_at=base + timedelta(minutes=i))
        for i in range(cap)
    ]
    oldest_row, _ = rows[0]
    second_oldest_row, _ = rows[1]
    new_row, new_token = make_session(session_repository, user_id, created_at=base + timedelta(minutes=cap))
    _login(user_id)
    entries = session_service.list_sessions(user_id=user_id)
    ids = {e.session_id for e in entries}
    # exactly one eviction: the oldest (no under-eviction, no over-eviction)
    assert oldest_row.id not in ids
    assert second_oldest_row.id in ids
    assert len(entries) == cap
    # the new session is kept and valid through the token path
    token_entries = session_service.list_sessions(token=new_token)
    # the new session is pinned first (REQ-006, INV-005) and the token path
    # returns the full valid list — exactly the cap after eviction (INV-003)
    assert token_entries[0].session_id == new_row.id
    assert len(token_entries) == cap
