"""AC-013: a log sink failure MUST NOT interrupt the traced call; the call
completes normally (logging is best-effort and non-blocking).

REQ-013: a log sink failure MUST NOT interrupt the traced call.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from logging_coverage_test_helpers import (
    INVENTORY_CLASSES,
    entry_records,
    exit_records,
    for_qualname,
)
from logging_test_helpers import captured_console, managed_sinks, rotating_file_handlers
from loguru import logger

from backend.logging import setup_logger
from backend.usermanagement.repository import SqliteUserRepository


def test_sink_failure_does_not_interrupt(log_records: list[Any], tmp_path: Any) -> None:
    """AC-013: with a failing log sink, a traced call completes normally and still
    produces entry + exit records."""
    # The subject is a traced class.
    assert getattr(INVENTORY_CLASSES["SqliteUserRepository"], "__logged_class__", False) is True

    # A sink that always fails. loguru catches it (best-effort) and the call
    # continues.
    def failing_sink(message: Any) -> None:
        raise RuntimeError("sink failure")

    handler_id = logger.add(failing_sink, level="DEBUG", catch=True)
    try:
        repo = SqliteUserRepository(f"sqlite:///{tmp_path}/sink.db")
        result = repo.get_by_username("probe")  # must not raise
        assert result is None
    finally:
        logger.remove(handler_id)

    # The traced call still produced entry + exit records (via the working sink).
    entries = for_qualname(entry_records(log_records), "SqliteUserRepository.get_by_username")
    exits = for_qualname(exit_records(log_records), "SqliteUserRepository.get_by_username")
    assert len(entries) == 1, "traced call did not produce an entry record despite sink failure"
    assert len(exits) == 1, "traced call did not produce an exit record despite sink failure"


def test_ac_016_call_unaffected_by_failing_file_sink(tmp_path: Path) -> None:
    """AC-016 (structlog-logging): a broken managed file sink never reaches the caller.

    Both failure points are broken: the handler the emitting thread calls (the
    queue handler) and the handler the listener thread calls (the rotating file
    handler). Neither exception may escape into the emitting call, and the console
    sink keeps working. The traced call itself is the subject: it must return its
    normal result with the file sink down.
    """
    setup_logger()
    _console, queue_handler = managed_sinks()
    rotating = rotating_file_handlers()[0]

    def exploding_emit(record: logging.LogRecord) -> None:
        raise RuntimeError("managed file sink is down")

    queue_handler.emit = exploding_emit  # type: ignore[method-assign]
    rotating.emit = exploding_emit  # type: ignore[method-assign]
    token = "ac016 file sink down probe"
    try:
        repo = SqliteUserRepository(f"sqlite:///{tmp_path}/ac016.db")
        assert repo.get_by_username("probe") is None, "AC-016: the traced call must return its normal result"
        with captured_console() as console_path:
            logging.getLogger("ac_016_probe").warning(token)  # must not raise
    finally:
        del queue_handler.emit, rotating.emit

    assert token in console_path.read_text(encoding="utf-8"), "AC-016: the console sink must keep working"
