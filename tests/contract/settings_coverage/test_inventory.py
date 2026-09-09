"""Contract tests for the settings inventory (AC-022..AC-024, NFR-002, NFR-003)."""

from __future__ import annotations

from collections.abc import Iterator

import pytest

from backend.settings import SettingsRegistry
from settings_test_helpers import make_registry

# The complete inventory from spec section 3.5:
# key -> (kind, default, category, group)
INVENTORY: dict[str, tuple[str, object, str, str]] = {
    "logging.log_level": ("SELECT", "INFO", "application", "logging"),
    "logging.log_file": ("TEXT", "logs/app.log", "application", "logging"),
    "logging.log_max_bytes": ("NUMBER", 10485760, "application", "logging"),
    "logging.log_backup_count": ("NUMBER", 5, "application", "logging"),
    "logging.profiling_include_arguments": ("BOOLEAN", False, "application", "logging"),
    "authentication.session_ttl": ("NUMBER", 604800, "security", "authentication"),
    "authentication.reset_token_ttl": ("NUMBER", 900, "security", "authentication"),
    "authentication.max_failed_attempts": ("NUMBER", 5, "security", "authentication"),
    "authentication.lockout_duration": ("NUMBER", 900, "security", "authentication"),
    "authentication.rp_id": ("TEXT", "localhost", "security", "authentication"),
    "authentication.rp_name": ("TEXT", "Python Template", "security", "authentication"),
    "authentication.origin": ("TEXT", "http://localhost:3000", "security", "authentication"),
    "usermanagement.roles": ("LIST", ["admin", "member"], "security", "usermanagement"),
    "eventbus.max_queue_size": ("NUMBER", 1000, "application", "eventbus"),
}


@pytest.fixture(autouse=True)
def _reset_registry() -> Iterator[None]:
    from backend.settings import reset_settings_registry

    reset_settings_registry()
    yield
    reset_settings_registry()


def _registry_with_all_features() -> SettingsRegistry:
    reg, _bus = make_registry()
    from backend.authentication import register_settings as auth_register
    from backend.eventbus import register_settings as bus_register
    from backend.logging import register_settings as logging_register
    from backend.usermanagement import register_settings as um_register

    logging_register(reg)
    auth_register(reg)
    um_register(reg)
    bus_register(reg)
    return reg


def test_key_prefix() -> None:
    """AC-022: keys use the full feature name as the prefix."""
    reg = _registry_with_all_features()
    for key in INVENTORY:
        assert reg.has(key), f"missing inventory key {key}"
        feature = key.split(".", 1)[0]
        assert key.startswith(f"{feature}.")


def test_category_group() -> None:
    """AC-023: category = domain, group = feature name."""
    reg = _registry_with_all_features()
    for key, (_kind, _default, category, group) in INVENTORY.items():
        d = reg.get_definition(key)
        assert d.category == category, f"{key}: category {d.category!r} != {category!r}"
        assert d.group == group, f"{key}: group {d.group!r} != {group!r}"


def test_inventory_matches() -> None:
    """AC-024: keys, kinds, and defaults match the inventory."""
    reg = _registry_with_all_features()
    for key, (kind, default, _category, _group) in INVENTORY.items():
        d = reg.get_definition(key)
        assert d.kind.value == kind, f"{key}: kind {d.kind!r} != {kind!r}"
        assert d.default == default, f"{key}: default {d.default!r} != {default!r}"
        assert reg.get_value(key) == default, f"{key}: value {reg.get_value(key)!r} != {default!r}"


def test_no_secret_settings() -> None:
    """NFR-002: settings contain no passwords or tokens."""
    reg = _registry_with_all_features()
    for key in INVENTORY:
        lowered = key.lower()
        assert "password" not in lowered
        assert "secret" not in lowered
        assert "credential" not in lowered
        value = reg.get_value(key)
        if isinstance(value, str):
            assert value and "://" not in value[:4]


def test_inventory_backward_compatible() -> None:
    """NFR-003: the inventory is a superset of the spec table (adding a setting is non-breaking)."""
    reg = _registry_with_all_features()
    for key in INVENTORY:
        assert reg.has(key), f"inventory key {key} missing"
