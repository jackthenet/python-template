"""Integration tests for the settings feature (docs/specs/settings.md).

Covers multi-feature reactive settings and the template capture/restore
workflow.
"""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from settings_test_helpers import wait_for

from backend.eventbus import EventBus
from backend.settings import (
    SettingChanged,
    SettingDefinition,
    SettingKind,
    SettingsRegistry,
)


@pytest.fixture
def registry() -> Iterator[SettingsRegistry]:
    bus = EventBus()
    r = SettingsRegistry(event_bus=bus)
    yield r
    bus.shutdown()


def test_multi_feature_reactive_settings() -> None:
    """Two features register settings; a reactive consumer tracks changes."""
    bus = EventBus()
    registry = SettingsRegistry(event_bus=bus)
    registry.register_feature("logging", [
        SettingDefinition(key="logging.level", kind=SettingKind.TEXT, default="INFO"),
    ])
    registry.register_feature("app", [
        SettingDefinition(key="app.name", kind=SettingKind.TEXT, default="orig"),
    ])
    latest: dict[str, object] = {}
    bus.subscribe(SettingChanged, lambda e: latest.__setitem__(e.key, e.value))
    registry.set_value("logging.level", "DEBUG")
    registry.set_value("app.name", "changed")
    assert wait_for(lambda: latest.get("logging.level") == "DEBUG"), "reactive consumer missed logging change"
    assert wait_for(lambda: latest.get("app.name") == "changed"), "reactive consumer missed app change"
    bus.shutdown()


def test_template_capture_restore_workflow(registry: SettingsRegistry) -> None:
    """Capture current values into a template, modify, then restore."""
    registry.register(SettingDefinition(
        key="app.a", kind=SettingKind.TEXT, default="a0", category="app",
    ))
    registry.register(SettingDefinition(
        key="app.b", kind=SettingKind.NUMBER, default=0, category="app",
    ))
    registry.set_value("app.a", "x")
    registry.set_value("app.b", 5)
    registry.create_template("snapshot", "app", None, None)
    assert registry.get_template("snapshot").values == {"app.a": "x", "app.b": 5}
    # Modify the settings away from the snapshot.
    registry.set_value("app.a", "y")
    registry.set_value("app.b", 9)
    # Restore from the template.
    registry.load_template("snapshot")
    assert registry.get_value("app.a") == "x"
    assert registry.get_value("app.b") == 5
