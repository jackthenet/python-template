"""Logging feature: loguru sink setup, stdlib interception, and logging decorators."""

from __future__ import annotations

from features.logging._setup import setup_logger
from features.logging._decorator import logged, logged_class

__all__ = [
    "setup_logger",
    "logged",
    "logged_class",
]
