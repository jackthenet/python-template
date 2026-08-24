"""Loguru sink setup and stdlib logging interception."""

from __future__ import annotations

import logging
import threading
from typing import Any

import loguru

_setup_lock = threading.Lock()
_is_setup = False


class _InterceptHandler(logging.Handler):
    """Routes stdlib logging records to loguru."""

    def emit(self, record: logging.LogRecord) -> None:
        frame = logging.currentframe()
        depth = 2
        if frame is not None:
            while frame.f_back is not None and depth < 5:
                frame = frame.f_back
                depth += 1
        loguru.logger.opt(exception=record.exc_info).log(
            record.levelno,
            record.getMessage(),
            record.pathname,
            record.funcName,
            record.lineno,
        )


def _install_intercept() -> None:
    """Attach the intercept handler to the root stdlib logger exactly once."""
    root = logging.getLogger()
    if not any(isinstance(h, _InterceptHandler) for h in root.handlers):
        root.addHandler(_InterceptHandler())


def setup_logger(settings: Any = None) -> None:
    """Configure loguru sinks and stdlib interception.

    Idempotent and thread-safe: concurrent calls produce the same sink count.
    """
    global _is_setup
    with _setup_lock:
        if _is_setup:
            return
        if settings is None:
            loguru.logger.add(lambda msg: None, level="INFO")
        else:
            loguru.logger.add(lambda msg: None, level=getattr(settings, "log_level", "INFO"))
        _install_intercept()
        _is_setup = True
