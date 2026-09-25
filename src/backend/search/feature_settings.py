"""Feature-owned settings registration for search (docs/specs/search.md).

``register_settings(registry)`` registers the search feature's
``SettingDefinition``s (``search.default_page_size``, ``search.max_page_size``,
``search.source_timeout``; category ``application``, group ``search``) with no
import side effects (REQ-013, D14). Each value is read live on each operation
by the service; unregistered keys fall back to the hardcoded defaults.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from backend.settings import SettingsRegistry


def register_settings(registry: SettingsRegistry) -> None:
    """Register the search feature's settings with ``registry`` (REQ-013)."""
    from backend.settings import SettingDefinition, SettingKind

    registry.register(
        SettingDefinition(
            key="search.default_page_size",
            kind=SettingKind.NUMBER,
            default=100,
            category="application",
            group="search",
        )
    )
    registry.register(
        SettingDefinition(
            key="search.max_page_size",
            kind=SettingKind.NUMBER,
            default=1000,
            category="application",
            group="search",
        )
    )
    registry.register(
        SettingDefinition(
            key="search.source_timeout",
            kind=SettingKind.NUMBER,
            default=5000,
            category="application",
            group="search",
        )
    )
