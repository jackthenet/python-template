"""Handler ownership tests for the logging feature (docs/specs/structlog-logging.md).

REQ-003/INV-004: the feature owns its own handlers and the single forwarding
handler on the root logger, and nothing else. Everything here is observed through
the public ``logging`` API.
"""

from __future__ import annotations

import io
import logging
from pathlib import Path

from logging_test_helpers import bound_logger, captured_console, json_records, wait_for_record
from settings_test_helpers import set_value_settled

import backend.logging as feature
from backend.logging import setup_logger
from backend.settings import get_settings_registry


def test_ac_004_foreign_handlers_untouched() -> None:
    """AC-004: setup and a ``logging.*`` change leave foreign handlers attached and unmodified."""
    setup_logger()

    root = logging.getLogger()
    other_feature = logging.getLogger("ac_004_other_feature")
    foreign_on_root = logging.StreamHandler(io.StringIO())
    foreign_on_other = logging.StreamHandler(io.StringIO())
    for handler in (foreign_on_root, foreign_on_other):
        handler.setLevel(logging.ERROR)
        handler.setFormatter(logging.Formatter("%(message)s"))
    other_feature.setLevel(logging.DEBUG)
    root.addHandler(foreign_on_root)
    other_feature.addHandler(foreign_on_other)

    registry = get_settings_registry()
    original_level = str(registry.get_value("logging.log_level"))
    try:
        for level in ("DEBUG", "INFO"):
            setup_logger()  # idempotent re-run (REQ-002)
            set_value_settled(registry, "logging.log_level", level)  # REQ-012 reconfigure

            assert foreign_on_root in root.handlers, "AC-004: a root handler the feature does not own must survive"
            assert foreign_on_other in other_feature.handlers, "AC-004: another feature's logger must stay untouched"
            assert foreign_on_root.level == logging.ERROR and foreign_on_root.formatter is not None
            assert foreign_on_other.level == logging.ERROR and foreign_on_other.formatter is not None
            assert other_feature.level == logging.DEBUG, "AC-004: the feature must not re-level another logger"
            assert other_feature.propagate is True, "AC-004: the feature must not re-route another logger"
    finally:
        set_value_settled(registry, "logging.log_level", original_level)
        root.removeHandler(foreign_on_root)
        other_feature.removeHandler(foreign_on_other)
        other_feature.setLevel(logging.NOTSET)


def test_ac_005_no_duplicate_records() -> None:
    """AC-005: one record from the feature logger lands exactly once in each managed sink."""
    setup_logger()

    log = bound_logger("ac_005_feature")
    token = "ac005 single record probe"

    with captured_console() as console_path:
        log.warning(token)

    console_lines = [line for line in console_path.read_text(encoding="utf-8").splitlines() if token in line]
    assert len(console_lines) == 1, f"AC-005: exactly one console record expected, got {console_lines!r}"

    log_file = Path(feature.get_settings().log_file)
    assert wait_for_record(log_file, lambda record: record.get("event") == token) is not None
    file_records = [record for record in json_records(log_file) if record.get("event") == token]
    assert len(file_records) == 1, f"AC-005: exactly one file record expected, got {file_records!r}"
