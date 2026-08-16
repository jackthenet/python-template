"""Logger sink setup and stdlib interception."""

from __future__ import annotations

import inspect
import logging
import sys
import threading
from pathlib import Path

from loguru import logger

from core.settings import Settings

_setup_done = threading.Event()

_LOG_FORMAT = "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"


class _InterceptHandler(logging.Handler):
    """Route stdlib ``logging`` records into loguru.

    Attach to the stdlib root logger so third-party libraries (NiceGUI,
    pyresilience, etc.) that use stdlib logging are captured by loguru sinks.

    Extended to skip frozen importlib bootstrap frames, which appear in
    some stdlib call paths on Python 3.12+.
    """

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level: str | int = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = inspect.currentframe(), 0
        while frame:
            filename = frame.f_code.co_filename
            is_logging = filename == logging.__file__
            is_frozen = "importlib" in filename and "_bootstrap" in filename
            if depth > 0 and not (is_logging or is_frozen):
                break
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def setup_logger(*, settings: Settings) -> None:
    """Configure loguru sinks based on *settings*.

    Safe to call multiple times — subsequent calls are no-ops.
    Thread-safe: uses a ``threading.Event`` so concurrent startup calls are
    handled correctly.
    """
    if _setup_done.is_set():
        return

    logger.remove()

    log_level = settings.log_level.upper()

    logger.add(
        sys.stderr,
        format=_LOG_FORMAT,
        level=log_level,
        colorize=True,
        backtrace=True,
    )

    log_path = Path(settings.log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logger.add(
        str(log_path),
        format=_LOG_FORMAT,
        level=log_level,
        rotation=settings.log_max_bytes,
        retention=settings.log_backup_count,
        encoding="utf-8",
        enqueue=True,
        backtrace=True,
        diagnose=False,  # intentionally False — diagnose=True leaks local variable values
    )

    logging.basicConfig(handlers=[_InterceptHandler()], level=0, force=True)

    _setup_done.set()
