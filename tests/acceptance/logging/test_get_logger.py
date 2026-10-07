"""AC-008: ``get_logger()`` is the feature's own way to emit through the pipeline
(docs/specs/structlog-logging.md REQ-005).

Observed from outside: one record in each managed sink, carrying the message and
the keyword fields.
"""

from __future__ import annotations

from pathlib import Path

from logging_test_helpers import bound_logger, captured_console, wait_for_record

import backend.logging as feature
from backend.logging import setup_logger

_ORDER_ID = 7
_ITEM = "widget"


def test_ac_008_get_logger_emits_to_sinks() -> None:
    """AC-008: a level method with a message and keyword fields reaches both sinks once."""
    setup_logger()

    log = bound_logger("ac_008_feature")
    token = "ac008 get_logger probe"

    with captured_console() as console_path:
        log.info(token, order_id=_ORDER_ID, item=_ITEM)

    console_text = console_path.read_text(encoding="utf-8")
    console_lines = [line for line in console_text.splitlines() if token in line]
    assert len(console_lines) == 1, f"AC-008: exactly one console record expected, got {console_lines!r}"
    assert "order_id" in console_text, "REQ-005: the console sink renders the same information as text"

    records = wait_for_record(Path(feature.get_settings().log_file), lambda r: r.get("event") == token)
    assert records is not None, "AC-008: the record must reach the file sink"
    assert records["logger"] == "ac_008_feature"
    assert records["order_id"] == _ORDER_ID
    assert records["item"] == _ITEM
