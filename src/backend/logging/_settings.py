"""Internal container for the logging feature's ``log_*`` values.

Replaces the removed stub ``Settings`` model (REQ-016). The values are read
from the shared settings registry, falling back to the original hardcoded
defaults when the registry does not exist or a key is unregistered.
"""

from __future__ import annotations

from dataclasses import dataclass

from backend.logging._decorator import logged


@dataclass
class Settings:
    """Plain container for the logging feature's ``log_*`` values."""

    log_level: str = "INFO"
    log_file: str = "logs/app.log"
    log_max_bytes: int = 10 * 1024 * 1024  # rotate at 10 MB
    log_backup_count: int = 5
    profiling_include_arguments: bool = False


def _settings_from_registry() -> Settings:
    """Read ``logging.*`` from the shared registry, falling back to defaults.

    REQ-014/AC-019: ``setup_logger`` reads the logging settings from the
    shared registry. When the registry does not exist or a key is
    unregistered, the original hardcoded default is used.
    """
    from backend.logging.feature_settings import _read_setting
    from backend.settings import get_settings_registry

    defaults = Settings()
    registry = get_settings_registry(required=False)
    if registry is None:
        return defaults
    values = {
        "log_level": _read_setting(registry, "logging.log_level", defaults.log_level),
        "log_file": _read_setting(registry, "logging.log_file", defaults.log_file),
        "log_max_bytes": _read_setting(registry, "logging.log_max_bytes", str(defaults.log_max_bytes)),
        "log_backup_count": _read_setting(registry, "logging.log_backup_count", str(defaults.log_backup_count)),
        "profiling_include_arguments": _read_setting(
            registry, "logging.profiling_include_arguments", str(defaults.profiling_include_arguments)
        ),
    }
    return Settings(
        log_level=values["log_level"],
        log_file=values["log_file"],
        log_max_bytes=int(values["log_max_bytes"]),
        log_backup_count=int(values["log_backup_count"]),
        profiling_include_arguments=values["profiling_include_arguments"] in ("True", "true"),
    )


@logged(slow_threshold_ms=5)
def get_settings() -> Settings:
    """Return the current ``log_*`` values (read from the registry, else defaults).

    Traced via the shared logging feature (``@logged``).
    """
    return _settings_from_registry()
