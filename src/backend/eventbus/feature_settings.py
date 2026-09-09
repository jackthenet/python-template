"""Feature-owned settings registration for the event bus (REQ-001)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from backend.logging._decorator import logged

if TYPE_CHECKING:
    from backend.settings import SettingsRegistry


@logged(slow_threshold_ms=5)
def register_settings(registry: "SettingsRegistry") -> None:
    """Register the event bus feature's settings with ``registry`` (REQ-001)."""
    from backend.settings import SettingDefinition, SettingKind

    registry.register(
        SettingDefinition(
            key="eventbus.max_queue_size",
            kind=SettingKind.NUMBER,
            default=1000,
            min_value=1,
            category="application",
            group="eventbus",
        )
    )
