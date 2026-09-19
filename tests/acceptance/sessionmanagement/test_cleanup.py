"""Acceptance tests for expired-row cleanup (docs/specs/session-management.md).

Covers AC-024, AC-025, EDGE-012 (REQ-012, REQ-018).
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sessionmanagement_test_helpers import make_session

from backend.settings import SettingDefinition, SettingKind, SettingsRegistry

# The spec's definition of sessionmanagement.cleanup_batch_size (REQ-019).
_CLEANUP_BATCH_SIZE_KEY = "sessionmanagement.cleanup_batch_size"


def _now() -> datetime:
    return datetime.now(UTC)


def _set_cleanup_batch_size(settings_registry: SettingsRegistry, value: int) -> None:
    """Register the spec's cleanup_batch_size definition and set the value live (REQ-019)."""
    settings_registry.register(
        SettingDefinition(
            key=_CLEANUP_BATCH_SIZE_KEY,
            kind=SettingKind.NUMBER,
            default=1000,
            min_value=1,
            category="sessionmanagement",
        )
    )
    settings_registry.set_value(_CLEANUP_BATCH_SIZE_KEY, value)


def _seed_expired(session_repository, user_id, count: int, base: datetime) -> None:
    """Seed ``count`` expired rows (created_at/expires_at in the past, all distinct)."""
    for i in range(count):
        make_session(
            session_repository,
            user_id,
            created_at=base - timedelta(days=2, minutes=i),
            expires_at=base - timedelta(days=1, minutes=i),
        )


def test_ac_024_cleanup_bounded_by_batch_size(
    session_service, session_repository, settings_registry, user_id
) -> None:
    """AC-024: 150 expired rows with cleanup_batch_size 100 → 100 deleted, 100 returned."""
    batch_size = 100
    expired_rows = 150
    _set_cleanup_batch_size(settings_registry, batch_size)
    base = _now()
    _seed_expired(session_repository, user_id, expired_rows, base)
    deleted = session_service.cleanup_expired()
    assert deleted == batch_size
    remaining_expired = [
        s for s in session_repository.list_for_user(user_id) if s.expires_at < base
    ]
    assert len(remaining_expired) == expired_rows - batch_size


def test_ac_025_cleanup_no_expired_returns_zero(
    session_service, session_repository, user_id
) -> None:
    """AC-025: no expired rows → cleanup_expired returns 0 (no error); valid rows untouched."""
    valid_rows = 2
    base = _now()
    for i in range(valid_rows):
        make_session(session_repository, user_id, created_at=base + timedelta(minutes=i))
    deleted = session_service.cleanup_expired()
    assert deleted == 0
    entries = session_service.list_sessions(user_id=user_id)
    assert len(entries) == valid_rows


def test_edge_012_cleanup_below_batch_size(
    session_service, session_repository, settings_registry, user_id
) -> None:
    """EDGE-012: fewer expired rows than cleanup_batch_size → all deleted, count returned."""
    batch_size = 100
    expired_rows = 3
    _set_cleanup_batch_size(settings_registry, batch_size)
    base = _now()
    _seed_expired(session_repository, user_id, expired_rows, base)
    deleted = session_service.cleanup_expired()
    assert deleted == expired_rows
    remaining_expired = [
        s for s in session_repository.list_for_user(user_id) if s.expires_at < base
    ]
    assert remaining_expired == []
