"""Logging feature public API (docs/specs/logging.md).

Exposes the pipeline setup entrypoint, the feature logger accessor, and the
function/class tracing decorators.  Importing this package does not require the
rest of the application to be wired up (REQ-001), and it never exposes a
backend logger object (AC-020).
"""

from __future__ import annotations

from backend.logging._decorator import logged, logged_class
from backend.logging._pipeline import get_logger, setup_logger
from backend.logging._settings import Settings, get_settings
from backend.logging.feature_settings import _read_setting, register_settings

__all__ = [
    "Settings",
    "_read_setting",
    "get_logger",
    "get_settings",
    "logged",
    "logged_class",
    "register_settings",
    "setup_logger",
]
