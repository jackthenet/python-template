"""Feature-owned settings registration for user-management (REQ-001)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from backend.logging._decorator import logged

if TYPE_CHECKING:
    from backend.settings import SettingsRegistry


@logged(slow_threshold_ms=5)
def register_settings(registry: "SettingsRegistry") -> None:
    """Register the user-management feature's settings with ``registry`` (REQ-001)."""
    from backend.settings import ListSpec, SettingDefinition, SettingKind

    registry.register(
        SettingDefinition(
            key="usermanagement.roles",
            kind=SettingKind.LIST,
            default=["admin", "member"],
            list_spec=ListSpec(item_pattern=r"^[a-z0-9_-]{1,32}$", min_items=1),
            category="security",
            group="usermanagement",
        )
    )
