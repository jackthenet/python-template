"""Edge case tests for the logging feature (docs/specs/logging.md).

Covers the spec's edge cases: log file parent directory creation, @logged
with no arguments, slow_threshold_setting referencing a non-existent field,
@logged_class with no public methods, and stdlib records with unknown levels.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from logging_test_helpers import run_python

from backend.logging import logged, logged_class, setup_logger


def test_edge_001_log_file_parent_created(tmp_path: Path) -> None:
    """EDGE-001: a log_file path whose parent directory does not exist is created automatically.

    Runs in a subprocess because setup_logger() is idempotent per process and
    the in-process session setup already chose its log file.
    """
    nested = tmp_path / "a" / "b" / "c" / "app.log"
    code = f"""
from backend.logging import setup_logger
from backend.logging.settings import Settings

setup_logger(Settings(log_file={str(nested)!r}, log_level="INFO"))
"""
    result = run_python(code)
    assert result.returncode == 0, result.stderr
    assert nested.parent.exists()
    assert nested.exists()


def test_edge_002_logged_no_args(log_records: list[Any]) -> None:
    """EDGE-002: @logged on a no-argument function emits an entry line without argument repr."""

    @logged
    def edge_002_fn() -> str:
        return "ok"

    assert edge_002_fn() == "ok"

    entries = [m for m in log_records if ">>" in str(m) and "edge_002_fn" in str(m)]
    assert entries


def test_edge_003_logged_nonexistent_setting(log_records: list[Any]) -> None:
    """EDGE-003: slow_threshold_setting referencing a non-existent field means no escalation."""

    @logged(slow_threshold_setting="does_not_exist")
    def edge_003_fn() -> None:
        time.sleep(0.05)

    edge_003_fn()

    # No escalation: no WARNING end-of-call line for this function.
    warnings = [m for m in log_records if "<<" in str(m) and "edge_003_fn" in str(m) and m["level"].name == "WARNING"]
    assert not warnings


def test_edge_004_logged_class_no_public_methods() -> None:
    """EDGE-004: @logged_class on a class with no public methods returns the class unchanged."""

    @logged_class
    class Edge004Service:
        def __init__(self) -> None:
            self.x = 1

    assert Edge004Service().x == 1


def test_edge_005_intercept_unknown_level(log_records: list[Any]) -> None:
    """EDGE-005: a stdlib record with a level name loguru does not recognize is routed numerically."""
    import logging

    setup_logger()

    unknown_level_no = 25

    class UnknownLevelFilter(logging.Filter):
        def filter(self, record: logging.LogRecord) -> bool:
            record.levelname = "NOT_A_LEVEL"
            return True

    stdlib_logger = logging.getLogger("edge_005")
    stdlib_logger.setLevel(unknown_level_no)
    stdlib_logger.addFilter(UnknownLevelFilter())
    stdlib_logger.log(unknown_level_no, "unknown level message")

    routed = [m for m in log_records if "unknown level message" in str(m)]
    assert routed
    assert routed[0]["level"].no == unknown_level_no
