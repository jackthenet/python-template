"""Feature-owned settings registration for permissions (REQ-019, D16)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from backend.logging import logged

if TYPE_CHECKING:
    from backend.settings import SettingsRegistry


@logged(slow_threshold_ms=5)
def register_settings(registry: SettingsRegistry) -> None:
    """Register the permissions feature's settings with ``registry`` (REQ-019).

    ``permissions.system_principal`` (LIST, default = the bootstrap system
    set) is the live-configurable alias for the system-principal permission
    set: a registry write updates the table (via the ``SettingChanged``
    subscription) and the check reads the table (source of truth, D16).
    """
    from backend.permissions.models import BOOTSTRAP_SYSTEM_PERMISSIONS
    from backend.settings import ListSpec, SettingDefinition, SettingKind

    registry.register(
        SettingDefinition(
            key="permissions.system_principal",
            kind=SettingKind.LIST,
            default=list(BOOTSTRAP_SYSTEM_PERMISSIONS),
            list_spec=ListSpec(item_pattern=r"^[a-z0-9_-]+\.[a-z0-9_-]+$"),
            category="permissions",
            group="permissions",
        )
    )
