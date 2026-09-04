"""Acceptance tests for the logging feature (docs/specs/logging.md).

These tests verify externally observable behavior only: what sinks exist,
what reaches the console and the log file, and what the repository layout
looks like.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from logging_test_helpers import captured_stderr, wait_for_file_content
from loguru import logger

from backend.logging import setup_logger

_EXPECTED_HANDLER_COUNT = 2  # one console sink + one file sink


def test_ac_001_setup_logger_adds_sinks(session_settings: object) -> None:
    """AC-001: setup_logger() configures a console sink on stderr and a rotating file sink."""
    setup_logger()  # idempotent: the session fixture already performed the real setup

    # Exactly one console sink and one file sink (loguru's default sink is removed).
    assert len(logger._core.handlers) == _EXPECTED_HANDLER_COUNT

    # Console sink: a log line reaches stderr (fd 2).
    with captured_stderr() as stderr_path:
        logger.info("ac_001 console line")
        content = stderr_path.read_text(encoding="utf-8")
    assert "ac_001 console line" in content

    # File sink: a log line reaches the configured log file (enqueued writer).
    log_file = Path(session_settings.log_file)  # type: ignore[attr-defined]
    logger.info("ac_001 file line")
    assert wait_for_file_content(log_file, lambda c: "ac_001 file line" in c, timeout=5)

    # Sink option contract (data-driven design): the named builders define the
    # sink properties the spec requires.
    from backend.logging._setup import _console_sink_options, _file_sink_options

    console_opts = _console_sink_options("INFO")
    assert console_opts["colorize"] is True
    assert console_opts["backtrace"] is True
    assert console_opts["diagnose"] is False

    file_opts = _file_sink_options(session_settings)  # type: ignore[arg-type]
    assert file_opts["encoding"] == "utf-8"
    assert file_opts["enqueue"] is True
    assert file_opts["backtrace"] is True
    assert file_opts["diagnose"] is False
    assert file_opts["rotation"] == session_settings.log_max_bytes  # type: ignore[attr-defined,union-attr]
    assert file_opts["retention"] == session_settings.log_backup_count  # type: ignore[attr-defined,union-attr]


def test_ac_002_setup_logger_idempotent() -> None:
    """AC-002: subsequent setup_logger() calls are no-ops and add no new sinks."""
    setup_logger()
    before = len(logger._core.handlers)
    setup_logger()
    setup_logger()
    after = len(logger._core.handlers)
    assert before == after


def test_ac_015_obsolete_module_deleted() -> None:
    """AC-015: the obsolete src/core/logging/ module is deleted."""
    repo_root = Path(__file__).resolve().parents[3]
    assert not (repo_root / "src" / "core" / "logging").exists()
    with pytest.raises(ImportError):
        import core.logging  # noqa: F401
