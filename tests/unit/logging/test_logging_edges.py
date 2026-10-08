"""Edge case tests for the logging feature (docs/specs/logging.md).

Covers the spec's edge cases: log file parent directory creation, @logged
with no arguments, slow_threshold_setting referencing a non-existent field,
and @logged_class with no public methods. (logging.md EDGE-005 is deleted by
docs/specs/structlog-logging.md; the unknown-level case survives as that
spec's EDGE-004 in tests/unit/logging/test_pipeline_edges.py.)
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from logging_test_helpers import run_python, subprocess_setup_code

from backend.logging import logged, logged_class


def test_edge_001_log_file_parent_created(tmp_path: Path) -> None:
    """EDGE-001: a log_file path whose parent directory does not exist is created automatically.

    Runs in a subprocess because setup_logger() is idempotent per process and
    the in-process session setup already chose its log file.
    """
    nested = tmp_path / "a" / "b" / "c" / "app.log"
    code = (
        subprocess_setup_code(str(nested), {"logging.log_level": "INFO"})
        + """
from backend.logging import setup_logger

setup_logger()
"""
    )
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
