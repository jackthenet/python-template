"""Feature-owned settings registration for authentication (REQ-001)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from backend.logging._decorator import logged

if TYPE_CHECKING:
    from backend.settings import SettingsRegistry


@logged(slow_threshold_ms=5)
def register_settings(registry: "SettingsRegistry") -> None:
    """Register the authentication feature's settings with ``registry`` (REQ-001)."""
    from backend.settings import SettingDefinition, SettingKind

    registry.register(
        SettingDefinition(
            key="authentication.session_ttl",
            kind=SettingKind.NUMBER,
            default=604800,
            min_value=1,
            category="security",
            group="authentication",
        )
    )
    registry.register(
        SettingDefinition(
            key="authentication.reset_token_ttl",
            kind=SettingKind.NUMBER,
            default=900,
            min_value=1,
            category="security",
            group="authentication",
        )
    )
    registry.register(
        SettingDefinition(
            key="authentication.max_failed_attempts",
            kind=SettingKind.NUMBER,
            default=5,
            min_value=1,
            category="security",
            group="authentication",
        )
    )
    registry.register(
        SettingDefinition(
            key="authentication.lockout_duration",
            kind=SettingKind.NUMBER,
            default=900,
            min_value=1,
            category="security",
            group="authentication",
        )
    )
    registry.register(
        SettingDefinition(
            key="authentication.rp_id",
            kind=SettingKind.TEXT,
            default="localhost",
            category="security",
            group="authentication",
        )
    )
    registry.register(
        SettingDefinition(
            key="authentication.rp_name",
            kind=SettingKind.TEXT,
            default="Python Template",
            category="security",
            group="authentication",
        )
    )
    registry.register(
        SettingDefinition(
            key="authentication.origin",
            kind=SettingKind.TEXT,
            default="http://localhost:3000",
            category="security",
            group="authentication",
        )
    )
