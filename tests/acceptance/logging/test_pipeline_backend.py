"""Acceptance tests for the standard-library logging pipeline (docs/specs/structlog-logging.md).

The managed sinks are ordinary standard-library handlers (REQ-002), so they are
observed through the public ``logging`` API rather than through a backend's
private handler table: which handlers the feature logger owns, where they write,
and how they are configured.
"""

from __future__ import annotations

import logging.handlers

from logging_test_helpers import (
    STDERR_FD,
    managed_sinks,
    pipeline_logger,
    rotating_file_handlers,
    wait_for_traced_record,
)

from backend.logging import get_settings, logged, setup_logger


def test_ac_002_two_managed_handlers() -> None:
    """AC-002: ``setup_logger()`` gives the feature logger exactly two managed handlers.

    One writes human-readable text to standard error, the other is a rotating file
    handler carrying the configured rotation size, backup count and UTF-8 encoding.
    Colorizing the console record is the renderer's choice (D3 fixes the record
    fields, never the format), so the console assertion stops at "standard error".
    """
    setup_logger()

    console, file_sink = managed_sinks()
    assert console.stream.fileno() == STDERR_FD, "REQ-002: the console sink writes to standard error"
    assert pipeline_logger().propagate is False, "REQ-003/D1: the feature logger must not propagate"

    rotating = rotating_file_handlers()
    assert len(rotating) == 1, f"REQ-002: exactly one rotating file sink is expected, found {len(rotating)}"
    if isinstance(file_sink, logging.handlers.QueueHandler):
        # D4: the file handler is fed through the queue, so it is not itself on the logger.
        assert rotating[0] not in pipeline_logger().handlers

    settings = get_settings()
    assert rotating[0].maxBytes == settings.log_max_bytes
    assert rotating[0].backupCount == settings.log_backup_count
    assert rotating[0].encoding == "utf-8"


# --------------------------------------------------------------------------
# AC-003: the field set of a rendered record (REQ-002 + REQ-011)
#
# The traced exit record is the strictest AC-003 case: it must carry every §3 field
# including elapsed_ms, and must not leak the pipeline's own callsite names (D7 maps
# add_callsite's filename/lineno onto file/line) or the formatter's two bookkeeping
# keys (D3; verified against structlog 26.1.0, where ProcessorFormatter.format injects
# exactly ``_record`` and ``_from_structlog`` — ADR-082's smoke-test facts).
# --------------------------------------------------------------------------

_REQUIRED_RECORD_FIELDS = frozenset({"level", "logger", "event", "timestamp", "elapsed_ms", "file", "line"})
_PIPELINE_INTERNAL_KEYS = frozenset({"filename", "lineno", "_record", "_from_structlog"})


def test_ac_003_file_record_fields_as_json() -> None:
    """AC-003: a traced call's file record is a JSON object carrying the §3 field set — and nothing else."""
    setup_logger()

    @logged
    def ac_003_traced_probe() -> None:
        return None

    ac_003_traced_probe()

    record = wait_for_traced_record("ac_003_traced_probe", "exit")
    assert record is not None, "AC-003: the traced exit record must reach the file sink as a JSON object"

    missing = _REQUIRED_RECORD_FIELDS - record.keys()
    assert not missing, f"AC-003/REQ-011: the record is missing {sorted(missing)}: {record!r}"

    leaked = _PIPELINE_INTERNAL_KEYS & record.keys()
    assert not leaked, f"AC-003/D3/D7: a rendered record must not carry {sorted(leaked)}: {record!r}"
