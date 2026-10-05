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
)

from backend.logging import get_settings, setup_logger


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
