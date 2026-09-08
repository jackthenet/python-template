"""AC-013: a log sink failure MUST NOT interrupt the traced call; the call
completes normally (logging is best-effort and non-blocking).

REQ-013: a log sink failure MUST NOT interrupt the traced call.
"""

from __future__ import annotations

from typing import Any

from loguru import logger

from logging_coverage_test_helpers import (
    INVENTORY_CLASSES,
    entry_records,
    exit_records,
    for_qualname,
)
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
