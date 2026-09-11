"""Feature-owned settings registration and live-read helper for logging.

REQ-001: the logging feature exposes ``register_settings(registry)`` which
registers the feature's ``SettingDefinition``s (no import side effects).
REQ-005: live reads via ``_read_setting`` (the feature reads its settings on
each use, falling back to a hardcoded default when the key is unregistered,
EDGE-002). REQ-020: a live read is traced only when the observed value
differs from the feature's previously observed value for that key.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from loguru import logger

from backend.logging._decorator import logged

if TYPE_CHECKING:
    from backend.settings import SettingsRegistry

# Track the previously observed value per key so a live read is traced only
# when the value changes (REQ-020).
_previously_observed: dict[str, str] = {}


@logged(slow_threshold_ms=5)
def _read_setting(registry: SettingsRegistry, key: str, fallback: str) -> str:
    """Read a setting live from ``registry`` (REQ-005).

    If ``key`` is registered, return the current value (traced when it
    changes, REQ-020). If ``key`` is unregistered, return ``fallback`` and
    log a warning (EDGE-002).
    """
    if not registry.has(key):
        logger.warning("setting '{}' is not registered; using fallback '{}'", key, fallback)
        return fallback
    value = registry.get_value(key)
    previous = _previously_observed.get(key)
    if previous is not None and previous != value:
        logger.debug("setting '{}' changed: '{}' -> '{}'", key, previous, value)
    _previously_observed[key] = value
    return value


@logged(slow_threshold_ms=5)
def register_settings(registry: SettingsRegistry) -> None:
    """Register the logging feature's settings with ``registry`` (REQ-001).

    The backend.settings import is deferred to the call site: importing it at
    module level here would create a circular import (the settings registry
    imports backend.logging for its tracing decorators).
    """
    from backend.settings import SelectOption, SelectSpec, SettingDefinition, SettingKind

    registry.register(
        SettingDefinition(
            key="logging.log_level",
            kind=SettingKind.SELECT,
            default="INFO",
            select=SelectSpec(
                options=[
                    SelectOption(value="DEBUG"),
                    SelectOption(value="INFO"),
                    SelectOption(value="WARNING"),
                    SelectOption(value="ERROR"),
                    SelectOption(value="CRITICAL"),
                ]
            ),
            category="application",
            group="logging",
        )
    )
    registry.register(
        SettingDefinition(
            key="logging.log_file",
            kind=SettingKind.TEXT,
            default="logs/app.log",
            category="application",
            group="logging",
        )
    )
    registry.register(
        SettingDefinition(
            key="logging.log_max_bytes",
            kind=SettingKind.NUMBER,
            default=10485760,
            min_value=1,
            category="application",
            group="logging",
        )
    )
    registry.register(
        SettingDefinition(
            key="logging.log_backup_count",
            kind=SettingKind.NUMBER,
            default=5,
            min_value=0,
            category="application",
            group="logging",
        )
    )
    registry.register(
        SettingDefinition(
            key="logging.profiling_include_arguments",
            kind=SettingKind.BOOLEAN,
            default=False,
            category="application",
            group="logging",
        )
    )
