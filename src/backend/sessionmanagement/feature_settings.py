"""Feature-owned settings registration for session-management (REQ-019).

``register_settings(registry)`` registers the feature's three
``SettingDefinition``s — no import side effects: it is an explicit function
called at wiring time, not at import. All settings are read live on each
operation through the service's ``_read_setting`` helper, so a ``set_value``
affects a running service without re-construction; unregistered keys fall
back to the hardcoded defaults (the same defaults the service uses as
fallbacks). ``authentication.session_ttl`` is reused unchanged — no duplicate
TTL key (REQ-019).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from backend.logging import logged
from backend.sessionmanagement.service import (
    DEFAULT_CLEANUP_BATCH_SIZE,
    DEFAULT_MAX_LISTED_SESSIONS,
    DEFAULT_MAX_SESSIONS_PER_USER,
)

if TYPE_CHECKING:
    from backend.settings import SettingsRegistry


@logged(slow_threshold_ms=5)
def register_settings(registry: SettingsRegistry) -> None:
    """Register the session-management feature's settings with ``registry`` (REQ-019)."""
    from backend.settings import SettingDefinition, SettingKind

    registry.register_feature(
        "sessionmanagement",
        [
            SettingDefinition(
                key="sessionmanagement.max_listed_sessions",
                kind=SettingKind.NUMBER,
                default=DEFAULT_MAX_LISTED_SESSIONS,
                min_value=1,
                category="sessionmanagement",
            ),
            SettingDefinition(
                key="sessionmanagement.max_sessions_per_user",
                kind=SettingKind.NUMBER,
                default=DEFAULT_MAX_SESSIONS_PER_USER,
                min_value=1,
                category="sessionmanagement",
            ),
            SettingDefinition(
                key="sessionmanagement.cleanup_batch_size",
                kind=SettingKind.NUMBER,
                default=DEFAULT_CLEANUP_BATCH_SIZE,
                min_value=1,
                category="sessionmanagement",
            ),
        ],
    )
