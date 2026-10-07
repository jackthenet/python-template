"""AC-006: records emitted by third-party loggers reach the two managed sinks
(docs/specs/structlog-logging.md REQ-004).

The third-party logger is a plain standard-library logger with no handlers of its
own — exactly the situation the root forwarding handler exists for.
"""

from __future__ import annotations

import logging
from pathlib import Path

from logging_test_helpers import captured_console, wait_for_record

from backend.logging import get_settings, setup_logger


def test_ac_006_third_party_reaches_both_sinks() -> None:
    """AC-006: a foreign record reaches both managed sinks with its level and message."""
    setup_logger()

    third_party = logging.getLogger("ac_006_third_party")
    assert not third_party.handlers, "the spec's given: a third-party logger with no handlers of its own"
    token = "ac006 third-party probe"

    with captured_console() as console_path:
        third_party.warning(token)

    console_text = console_path.read_text(encoding="utf-8")
    assert token in console_text, "REQ-004: the forwarded record must reach the console sink"
    assert "ac_006_third_party" in console_text, "REQ-004: the logger name must survive forwarding"
    assert "WARNING" in console_text, "REQ-004: the level must survive forwarding"

    record = wait_for_record(Path(get_settings().log_file), lambda r: r.get("event") == token)
    assert record is not None, "REQ-004: the forwarded record must reach the file sink"
    assert record["level"] == "WARNING"
    assert record["logger"] == "ac_006_third_party"
