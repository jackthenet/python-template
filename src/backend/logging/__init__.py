"""Logging feature public API (docs/specs/logging.md).

Exposes the sink setup entrypoint and the function/class tracing decorators.
Importing this package does not require the rest of the application to be
wired up (REQ-001).
"""

from __future__ import annotations

from backend.logging._decorator import logged, logged_class
from backend.logging._setup import setup_logger
from backend.logging.feature_settings import _read_setting, register_settings
from backend.logging._settings import Settings, get_settings

__all__ = [
    "Settings",
    "_read_setting",
    "get_settings",
    "logged",
    "logged_class",
    "register_settings",
    "setup_logger",
]
