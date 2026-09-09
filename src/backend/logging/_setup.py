"""Loguru sink configuration and stdlib logging interception (REQ-001..003).

This module is importable without application wiring: calling
``setup_logger()`` configures loguru's sinks and installs the stdlib
intercept handler. It is idempotent and thread-safe (REQ-002) and never
leaks local variable values (``diagnose=False``).
"""

from __future__ import annotations

import logging
import sys
import threading
import types
from pathlib import Path
from typing import Any

from loguru import logger

from backend.logging._decorator import logged
from backend.logging.settings import Settings, get_settings

# Standard stdlib level numbers -> loguru level names. Unknown level numbers
# are passed through numerically so loguru keeps the exact number (EDGE-005).
_LEVEL_NAMES: dict[int, str] = {
    10: "DEBUG",
    20: "INFO",
    30: "WARNING",
    40: "ERROR",
    50: "CRITICAL",
}

# Idempotency / thread-safety guard (REQ-002): a Lock serializes the first
# setup, and an Event records that setup is complete so later calls return
# without re-configuring the sinks.
_setup_lock = threading.Lock()
_setup_done = threading.Event()


class _InterceptHandler(logging.Handler):
    """Routes stdlib logging records to the loguru sinks (REQ-003).

    The handler re-attributes each record to the real caller by walking the
    stack above ``emit`` and skipping logging-module and frozen importlib
    bootstrap frames, so loguru's origin capture lands on the caller that
    actually emitted the record (AC-005).
    """

    def emit(self, record: logging.LogRecord) -> None:
        # Resolve the loguru level: standard name for standard levels,
        # numeric level number otherwise (EDGE-005).
        level: str | int = _LEVEL_NAMES.get(record.levelno, record.levelno)

        # Walk frames above emit, skipping logging-module and frozen
        # importlib bootstrap frames, counting how many to skip so loguru's
        # origin capture lands on the real caller.
        frame: types.FrameType | None = sys._getframe(1)  # frame above emit (Handler.handle)
        depth = 1
        while frame is not None:
            filename = frame.f_code.co_filename
            if filename == logging.__file__ or filename.startswith("<frozen"):
                frame = frame.f_back
                depth += 1
            else:
                break

        logger.opt(depth=depth).log(level, record.getMessage())


def _console_sink_options(level: str) -> dict[str, Any]:
    """Data-driven console sink options (standard error stream, colored)."""
    return {
        "level": level,
        "colorize": True,
        "backtrace": True,
        "diagnose": False,
    }


def _file_sink_options(settings: Settings) -> dict[str, Any]:
    """Data-driven rotating file sink options (UTF-8, enqueued, backtrace)."""
    return {
        "level": settings.log_level,
        "encoding": "utf-8",
        "enqueue": True,
        "backtrace": True,
        "diagnose": False,
        "rotation": settings.log_max_bytes,
        "retention": settings.log_backup_count,
    }


@logged(slow_threshold_ms=5)
def setup_logger(settings: Settings | None = None) -> None:
    """Configure loguru sinks and install the stdlib intercept handler.

    Idempotent and thread-safe (REQ-002): the first call configures a
    standard-stream console sink (stderr) and a rotating file sink; later
    calls return without re-configuring. The stdlib intercept handler is
    installed on the root stdlib logger exactly once (REQ-003).

    Traced via the shared logging feature (``@logged``).
    """
    if _setup_done.is_set():
        return
    with _setup_lock:
        if _setup_done.is_set():
            return
        _configure(settings)
        _setup_done.set()


def _configure(settings: Settings | None) -> None:
    settings = settings if settings is not None else get_settings()

    # Remove loguru's default sink so the handler set is exactly the two
    # configured sinks (REQ-001 / INV-001).
    logger.remove()

    # Console sink on the standard error stream (fd 2) so standard-stream
    # capture helpers observe it.
    logger.add(sys.stderr, **_console_sink_options(settings.log_level))

    # Create the log-file parent directory if it does not exist (EDGE-001).
    log_file = Path(settings.log_file)
    log_file.parent.mkdir(parents=True, exist_ok=True)

    # Rotating file sink.
    logger.add(str(log_file), **_file_sink_options(settings))

    # Match the stdlib root logger's level to the configured level so records
    # (e.g. INFO) are not dropped by the inherited WARNING default before
    # reaching the intercept handler (REQ-003 / AC-004).
    logging.getLogger().setLevel(settings.log_level)

    # Install the stdlib intercept handler on the root logger exactly once.
    _install_intercept_handler()


def _install_intercept_handler() -> None:
    root = logging.getLogger()
    if any(isinstance(h, _InterceptHandler) for h in root.handlers):
        return
    root.addHandler(_InterceptHandler())
