"""Stub Settings module for the logging feature (REQ-008).

This module is intentionally a self-contained stub: it exposes the settings
fields the approved spec's data structure defines, with no external
dependencies. The full settings module (environment-variable overrides,
validation, etc.) is out of scope for this feature; the stub is the
contract the rest of ``backend.logging`` and the test suite depend on.
"""

from __future__ import annotations

from pydantic import BaseModel


class Settings(BaseModel):
    """Logging settings (stub).

    Field semantics mirror the approved spec's data structure:
    ``log_level`` / ``log_file`` drive the sinks, ``log_max_bytes`` /
    ``log_backup_count`` drive rotation/retention, and
    ``profiling_include_arguments`` is the forward-looking profiling flag.
    """

    log_level: str = "INFO"
    log_file: str = "logs/app.log"
    log_max_bytes: int = 10 * 1024 * 1024  # rotate at 10 MB
    log_backup_count: int = 5
    profiling_include_arguments: bool = False


def get_settings() -> Settings:
    """Return the current Settings instance (defaults for the stub)."""
    return Settings()
