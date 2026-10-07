"""Acceptance tests for the logging feature (docs/specs/logging.md).

These tests verify externally observable behavior only: what sinks exist,
what reaches the console and the log file, and what the repository layout
looks like.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from logging_test_helpers import captured_console, managed_handlers, managed_sinks, pipeline_logger, wait_for_record

from backend.logging import setup_logger


def test_ac_001_setup_logger_adds_sinks(session_settings: object) -> None:
    """AC-001 (logging.md v3, restated by structlog-logging): one setup_logger() call installs a
    colorized text console sink on stderr and a rotating JSON file sink.

    Re-derived from the amended AC-001 wording. The loguru handler-count and
    ``_console_sink_options`` / ``_file_sink_options`` assertions measured the
    implementation this change replaces, so they are replaced by assertions on
    the observable sinks and the records they write.
    """
    setup_logger()  # idempotent: the session fixture already performed the real setup

    console, _file_sink = managed_sinks()
    assert console.stream is not None, "AC-001: the console sink must write to a stream"

    token = "ac_001 pipeline line"
    with captured_console() as console_path:
        pipeline_logger().warning(f"{token} console")
        assert f"{token} console" in console_path.read_text(encoding="utf-8"), (
            "AC-001: the console sink must render the record as text on stderr"
        )

    log_file = Path(session_settings.log_file)  # type: ignore[attr-defined]
    record = wait_for_record(log_file, lambda record: record.get("event") == f"{token} console")
    assert record is not None, "AC-001: the file sink must write the record as JSON"
    assert record["level"] == "WARNING", "AC-001: the record must carry its level"


def test_ac_002_setup_logger_idempotent() -> None:
    """AC-002: subsequent setup_logger() calls are no-ops and add no new sinks."""
    setup_logger()
    before = managed_handlers(pipeline_logger())
    setup_logger()
    setup_logger()
    after = managed_handlers(pipeline_logger())
    assert before == after


def test_ac_015_obsolete_module_deleted() -> None:
    """AC-015: the obsolete src/core/logging/ module is deleted."""
    repo_root = Path(__file__).resolve().parents[3]
    assert not (repo_root / "src" / "core" / "logging").exists()
    with pytest.raises(ImportError):
        import core.logging  # noqa: F401
