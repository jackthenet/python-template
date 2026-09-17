"""Acceptance tests for feature-owned settings registration and live reads
(docs/specs/session-management.md).

Covers AC-039, AC-040 (REQ-019).
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sessionmanagement_test_helpers import make_session

from backend.settings import SettingDefinition, SettingKind, SettingsRegistry

# The spec's definition of sessionmanagement.max_listed_sessions (REQ-019).
_MAX_LISTED_SESSIONS_KEY = "sessionmanagement.max_listed_sessions"

# AC-039: the 3 keys register_settings must register, with their spec defaults.
_EXPECTED_DEFAULTS = {
    "sessionmanagement.max_listed_sessions": 100,
    "sessionmanagement.max_sessions_per_user": 5,
    "sessionmanagement.cleanup_batch_size": 1000,
}


def _now() -> datetime:
    return datetime.now(UTC)


def _set_max_listed_sessions(settings_registry: SettingsRegistry, value: int) -> None:
    """Register the spec's max_listed_sessions definition and set the value live (REQ-019)."""
    settings_registry.register(
        SettingDefinition(
            key=_MAX_LISTED_SESSIONS_KEY,
            kind=SettingKind.NUMBER,
            default=100,
            min_value=1,
            category="sessionmanagement",
        )
    )
    settings_registry.set_value(_MAX_LISTED_SESSIONS_KEY, value)


def test_ac_039_register_settings_defaults(settings_registry: SettingsRegistry) -> None:
    """AC-039: register_settings(registry) registers the 3 keys with defaults 100/5/1000 (all min_value 1)."""
    from backend.sessionmanagement import register_settings

    register_settings(settings_registry)

    # exactly the 3 spec keys are registered (REQ-019)
    registered = {view.key for view in settings_registry.views()}
    assert registered == set(_EXPECTED_DEFAULTS)
    for key, default in _EXPECTED_DEFAULTS.items():
        definition = settings_registry.get_definition(key)
        assert definition.kind is SettingKind.NUMBER
        assert definition.default == default
        assert definition.min_value == 1
        assert definition.category == "sessionmanagement"
        # the value is initialized to the default
        assert settings_registry.get_value(key) == default


def test_ac_040_live_read_max_listed_sessions(
    session_service, session_repository, settings_registry, user_id
) -> None:
    """AC-040: max_listed_sessions changed in the registry → list_sessions without an explicit limit uses the new value (live read)."""
    new_limit = 2
    _set_max_listed_sessions(settings_registry, new_limit)
    valid_rows = 5
    base = _now()
    for i in range(valid_rows):
        make_session(session_repository, user_id, created_at=base + timedelta(minutes=i))
    entries = session_service.list_sessions(user_id=user_id)
    assert len(entries) == new_limit
