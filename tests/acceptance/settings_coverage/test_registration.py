"""AC-001: register_settings(registry) registers the feature's definitions."""

from __future__ import annotations

from collections.abc import Iterator

import pytest

from backend.settings import SettingDefinition, SettingKind, SettingsRegistry
from settings_test_helpers import make_registry


@pytest.fixture(autouse=True)
def _reset_registry() -> Iterator[None]:
    from backend.settings import reset_settings_registry

    reset_settings_registry()
    yield
    reset_settings_registry()


def test_register_settings_registers() -> None:
    """AC-001: calling register_settings(registry) registers the feature's SettingDefinitions."""
    reg, _bus = make_registry()

    from backend.logging import register_settings as logging_register

    logging_register(reg)
    assert reg.has("logging.log_level")
    assert reg.has("logging.log_file")
    assert reg.has("logging.log_max_bytes")
    assert reg.has("logging.log_backup_count")
    assert reg.has("logging.profiling_include_arguments")

    from backend.authentication import register_settings as auth_register

    auth_register(reg)
    assert reg.has("authentication.session_ttl")
    assert reg.has("authentication.reset_token_ttl")
    assert reg.has("authentication.max_failed_attempts")
    assert reg.has("authentication.lockout_duration")
    assert reg.has("authentication.rp_id")
    assert reg.has("authentication.rp_name")
    assert reg.has("authentication.origin")

    from backend.usermanagement import register_settings as um_register

    um_register(reg)
    assert reg.has("usermanagement.roles")

    from backend.eventbus import register_settings as bus_register

    bus_register(reg)
    assert reg.has("eventbus.max_queue_size")
