"""Property tests for session-management invariants (docs/specs/session-management.md).

Covers INV-001, INV-002, INV-003, INV-004, INV-005.
"""

from __future__ import annotations

import tempfile
import threading
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from eventbus_test_helpers import isolated_event_bus
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from sessionmanagement_test_helpers import EventCollector, build_session_service, make_session

from backend.authentication import LoginSucceeded
from backend.authentication.repository import SqliteSessionRepository
from backend.eventbus import get_event_bus, reset_event_bus
from backend.settings import SettingDefinition, SettingKind, SettingsRegistry, YamlValueRepository

_MAX_EXAMPLES = 10

_session_spec = st.fixed_dictionaries(
    {
        "revoked": st.booleans(),
        "age_minutes": st.integers(min_value=0, max_value=1000),
        "ttl_days": st.integers(min_value=1, max_value=30),
    }
)


def _build(specs: list[dict]) -> tuple[object, list[tuple[object, str]], UUID]:
    """Build an in-memory store + service with the given random session specs.

    Returns ``(service, created, user_id)`` where ``created`` is a list of
    ``(row, raw_token)`` pairs in spec order.
    """
    user_id = uuid4()
    repo = SqliteSessionRepository("sqlite:///:memory:")
    registry = SettingsRegistry(value_repository=YamlValueRepository(tempfile.mkdtemp()))
    service = build_session_service(repo, event_bus=None, settings_registry=registry)
    base = datetime.now(UTC)
    created: list[tuple[object, str]] = []
    for i, spec in enumerate(specs):
        created_at = base - timedelta(minutes=spec["age_minutes"], seconds=i)
        expires_at = created_at + timedelta(days=spec["ttl_days"])
        row, token = make_session(
            repo,
            user_id,
            created_at=created_at,
            expires_at=expires_at,
            revoked=spec["revoked"],
        )
        created.append((row, token))
    return service, created, user_id


@settings(max_examples=_MAX_EXAMPLES, deadline=None, suppress_health_check=[HealthCheck.too_slow])
@given(specs=st.lists(_session_spec, max_size=20))
def test_inv_002_valid_only_listing(specs: list[dict]) -> None:
    """INV-002: every listed entry is valid (unrevoked and unexpired)."""
    service, created, user_id = _build(specs)
    entries = service.list_sessions(user_id=user_id)
    now = datetime.now(UTC)
    valid_ids = {row.id for row, _ in created if not row.revoked and row.expires_at > now}
    returned_ids = {e.session_id for e in entries}
    assert returned_ids <= valid_ids


@settings(max_examples=_MAX_EXAMPLES, deadline=None, suppress_health_check=[HealthCheck.too_slow])
@given(existing=st.integers(min_value=0, max_value=12), cap=st.integers(min_value=1, max_value=10))
def test_inv_003_cap_held_after_login(existing: int, cap: int) -> None:
    """INV-003: after LoginSucceeded handling, the user's valid session count is at most the cap."""
    with isolated_event_bus():
        reset_event_bus()
        try:
            user_id = uuid4()
            repo = SqliteSessionRepository("sqlite:///:memory:")
            registry = SettingsRegistry(value_repository=YamlValueRepository(tempfile.mkdtemp()))
            registry.register(
                SettingDefinition(
                    key="sessionmanagement.max_sessions_per_user",
                    kind=SettingKind.NUMBER,
                    default=cap,
                    min_value=1,
                    category="sessionmanagement",
                )
            )
            service = build_session_service(repo, event_bus=EventCollector(), settings_registry=registry)
            base = datetime.now(UTC)
            for i in range(existing):
                make_session(repo, user_id, created_at=base - timedelta(minutes=existing - i))
            # the login issues a new session, then LoginSucceeded is dispatched
            make_session(repo, user_id, created_at=base)
            dispatched = threading.Event()
            bus = get_event_bus()
            bus.subscribe(LoginSucceeded, lambda event: dispatched.set())
            bus.publish(LoginSucceeded(user_id=user_id, method="password"))
            assert dispatched.wait(timeout=5.0), "LoginSucceeded was not dispatched"
            entries = service.list_sessions(user_id=user_id)
            assert len(entries) <= cap
        finally:
            reset_event_bus()


@settings(max_examples=_MAX_EXAMPLES, deadline=None, suppress_health_check=[HealthCheck.too_slow])
@given(specs=st.lists(_session_spec, min_size=1, max_size=20))
def test_inv_005_current_session_first(specs: list[dict]) -> None:
    """INV-005: the first entry of list_sessions(token) is the token's session."""
    service, created, _user_id = _build(specs)
    now = datetime.now(UTC)
    valid = [(row, token) for row, token in created if not row.revoked and row.expires_at > now]
    if not valid:
        return  # no valid token to resolve; pinning is vacuously true
    target_row, target_token = valid[0]
    entries = service.list_sessions(token=target_token)
    assert entries[0].session_id == target_row.id


def _build_collected(
    specs: list[dict],
) -> tuple[object, SqliteSessionRepository, list[tuple[object, str]], UUID, EventCollector]:
    """Build an in-memory store + service with an event collector.

    Returns ``(service, repo, created, user_id, collector)`` where ``created``
    is a list of ``(row, raw_token)`` pairs in spec order.
    """
    user_id = uuid4()
    repo = SqliteSessionRepository("sqlite:///:memory:")
    registry = SettingsRegistry(value_repository=YamlValueRepository(tempfile.mkdtemp()))
    collector = EventCollector()
    service = build_session_service(repo, event_bus=collector, settings_registry=registry)
    base = datetime.now(UTC)
    created: list[tuple[object, str]] = []
    for i, spec in enumerate(specs):
        created_at = base - timedelta(minutes=spec["age_minutes"], seconds=i)
        expires_at = created_at + timedelta(days=spec["ttl_days"])
        row, token = make_session(
            repo,
            user_id,
            created_at=created_at,
            expires_at=expires_at,
            revoked=spec["revoked"],
        )
        created.append((row, token))
    return service, repo, created, user_id, collector


def _revoked_state(repo: SqliteSessionRepository, created: list[tuple[object, str]]) -> dict[UUID, bool]:
    """Snapshot of the current revoked flag of every created row, by id."""
    state: dict[UUID, bool] = {}
    for row, _token in created:
        current = repo.get_by_token_hash(row.token_hash)
        assert current is not None, "created row disappeared from the store"
        state[current.id] = current.revoked
    return state


@settings(max_examples=_MAX_EXAMPLES, deadline=None, suppress_health_check=[HealthCheck.too_slow])
@given(specs=st.lists(_session_spec, max_size=20))
def test_inv_001_revocation_idempotent(specs: list[dict]) -> None:
    """INV-001: re-running a revocation operation after it has succeeded is a
    no-op — no error, no state change, no duplicate event."""
    service, repo, created, user_id, collector = _build_collected(specs)
    # logout_other_sessions (needs a valid caller token)
    now = datetime.now(UTC)
    valid = [token for row, token in created if not row.revoked and row.expires_at > now]
    if valid:
        caller = valid[0]
        service.logout_other_sessions(caller)  # first run: succeeds
        state = _revoked_state(repo, created)
        collector.events.clear()
        service.logout_other_sessions(caller)  # re-run: no-op
        assert _revoked_state(repo, created) == state
        assert not collector.events, "re-run published a duplicate event"
    # revoke_session (idempotent for unknown and already-revoked ids)
    target = created[0][0].id if created else uuid4()
    service.revoke_session(target)  # first run: succeeds
    state = _revoked_state(repo, created)
    collector.events.clear()
    service.revoke_session(target)  # re-run: no-op
    assert _revoked_state(repo, created) == state
    assert not collector.events, "re-run published a duplicate event"
    # revoke_all_sessions (a re-run revokes 0 sessions and publishes no event)
    service.revoke_all_sessions(user_id)  # first run: succeeds
    state = _revoked_state(repo, created)
    collector.events.clear()
    service.revoke_all_sessions(user_id)  # re-run: 0 revoked
    assert _revoked_state(repo, created) == state
    assert not collector.events, "re-run published a duplicate event"


@settings(max_examples=_MAX_EXAMPLES, deadline=None, suppress_health_check=[HealthCheck.too_slow])
@given(specs=st.lists(_session_spec, min_size=1, max_size=20))
def test_inv_004_no_tokens_in_outputs(specs: list[dict]) -> None:
    """INV-004: the raw session token and its SHA-256 hash never appear in any
    operation output — returned entries, published events, raised error messages."""
    service, _repo, created, user_id, collector = _build_collected(specs)
    outputs: list[str] = []
    now = datetime.now(UTC)
    valid = [token for row, token in created if not row.revoked and row.expires_at > now]
    # returned entries (both listing paths)
    listings = [service.list_sessions(user_id=user_id)]
    if valid:
        listings.append(service.list_sessions(token=valid[0]))
    for entries in listings:
        for entry in entries:
            outputs.append(str(entry))
            outputs.append(repr(entry))
            outputs.append(entry.model_dump_json())
    # operations that produce events
    service.revoke_session(created[0][0].id)
    service.revoke_all_sessions(user_id)
    service.cleanup_expired()
    for event in collector.events:
        outputs.append(str(event))
        outputs.append(repr(event))
        outputs.append(event.model_dump_json())
    # raised error messages (every session is revoked now, so any token is dead)
    try:
        service.list_sessions(token=created[0][1])
    except Exception as exc:
        outputs.append(str(exc))
        outputs.append(repr(exc))
    # Then: no raw token or token hash in any output
    for row, token in created:
        for out in outputs:
            assert token not in out
            assert row.token_hash not in out
