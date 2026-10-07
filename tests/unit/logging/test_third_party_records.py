"""AC-007: a forwarded third-party record names the emitting source location
(docs/specs/structlog-logging.md REQ-004, D7).

The callsite must be resolved where the record was emitted, not in the queue
listener thread — which is exactly what a wrong implementation produces.
"""

from __future__ import annotations

import inspect
import logging
from pathlib import Path

from logging_test_helpers import wait_for_record

import backend.logging as feature
from backend.logging import setup_logger


def _emit_and_line(logger: logging.Logger, message: str) -> int:
    """Emit ``message`` at the current line and return that line number."""
    logger.warning(message)
    return inspect.currentframe().f_lineno - 1


def test_ac_007_location_of_emitting_call() -> None:
    """AC-007: file and line name the emitting call, not the logging feature's own code."""
    setup_logger()

    third_party = logging.getLogger("ac_007_third_party")
    token = "ac007 source location probe"
    emitted_on = _emit_and_line(third_party, token)

    record = wait_for_record(Path(feature.get_settings().log_file), lambda r: r.get("event") == token)
    assert record is not None, "AC-007: the forwarded record must reach the file sink"
    assert Path(str(record["file"])).name == Path(__file__).name, (
        f"AC-007: file must name the emitting source file, got {record['file']!r}"
    )
    assert int(record["line"]) == emitted_on, (
        f"AC-007: line must be the emitting call (line {emitted_on}), got {record['line']!r}"
    )
