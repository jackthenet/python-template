"""Acceptance tests for the standard-library logging pipeline (docs/specs/structlog-logging.md).

The managed sinks are ordinary standard-library handlers (REQ-002), so they are
observed through the public ``logging`` API rather than through a backend's
private handler table: which handlers the feature logger owns, where they write,
and how they are configured.
"""

from __future__ import annotations

import ast
import logging
import logging.handlers
from pathlib import Path

from logging_test_helpers import (
    STDERR_FD,
    bound_logger,
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


# --------------------------------------------------------------------------
# AC-001: no import of the removed backend anywhere, and the stdlib handler chain
#
# REQ-001 forbids a third-party logging *backend*; the one that is removed is loguru
# (REQ-013). structlog is not a backend in this spec's vocabulary — ADR-082 keeps it as
# the processor/renderer layer the feature itself owns — so the repo-wide search is for
# the removed backend, while the AC-009 witnesses keep forbidding a backend import
# (loguru *or* structlog) in the feature modules that must go through get_logger().
# --------------------------------------------------------------------------

_REPO_ROOT = Path(__file__).resolve().parents[3]

# AC-001: "searched for an import of the removed logging backend" — loguru (REQ-013).
_REMOVED_BACKEND_PACKAGES = frozenset({"loguru"})

# REQ-001 names both trees, so the search is not limited to the shipped package.
_SEARCHED_TREES = ("src", "tests")


def _backend_import_offenders() -> list[str]:
    """Every module under ``src/`` or ``tests/`` that imports the removed logging backend.

    Parsed, not grepped: REQ-001 forbids an *import*, and the repository keeps the removed
    backend's name in prose (docstrings, the superseded ADR's title), which a text search
    would report as a false match once the migration is complete.
    """
    offenders: list[str] = []
    for tree in _SEARCHED_TREES:
        for path in sorted((_REPO_ROOT / tree).rglob("*.py")):
            module = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(module):
                if isinstance(node, ast.Import):
                    names = [
                        alias.name for alias in node.names if alias.name.split(".")[0] in _REMOVED_BACKEND_PACKAGES
                    ]
                elif isinstance(node, ast.ImportFrom) and (node.module or "").split(".")[0] in (
                    _REMOVED_BACKEND_PACKAGES
                ):
                    names = [f"{node.module}.{alias.name}" for alias in node.names]
                else:
                    continue
                if names:
                    offenders.append(f"{path.relative_to(_REPO_ROOT).as_posix()} -> {sorted(names)}")
                    break
    return offenders


class _ObservingHandler(logging.Handler):
    """A plain standard-library handler that keeps what the feature logger's chain delivers."""

    def __init__(self) -> None:
        super().__init__()
        self.records: list[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(record)


def _observed_feature_record(token: str) -> logging.LogRecord | None:
    """Emit one feature statement and return the record a handler on the feature logger saw.

    AC-001's second clause is exactly this: the record must travel the standard-library
    handler chain, so a handler attached to the feature logger (the non-propagating logger
    owning the managed sinks, D1) observes it. ``get_logger()`` is the emitting entry point
    (REQ-005); the clause says nothing about the record's format, so nothing is asserted here
    beyond "it arrived, carrying the message".
    """
    feature_logger = pipeline_logger()
    observer = _ObservingHandler()
    feature_logger.addHandler(observer)
    try:
        bound_logger("ac_001").info(token)
    finally:
        feature_logger.removeHandler(observer)
    return observer.records[0] if observer.records else None


def test_ac_001_no_backend_import_and_stdlib_chain() -> None:
    """AC-001: no module under ``src/`` or ``tests/`` imports the removed backend, and a record
    emitted by the feature passes through the standard-library handler chain."""
    setup_logger()
    violations: list[str] = []

    if offenders := _backend_import_offenders():
        violations.append(f"{len(offenders)} module(s) import the removed logging backend: {offenders}")

    token = "ac_001_stdlib_handler_chain"
    try:
        record = _observed_feature_record(token)
    except AssertionError as exc:  # the pipeline / get_logger() this clause rides on is absent
        violations.append(f"stdlib handler chain: {exc}")
    else:
        if record is None:
            violations.append("stdlib handler chain: a handler on the feature logger observed no record")
        elif token not in record.getMessage():
            violations.append(f"stdlib handler chain: the observed record lost the message: {record.getMessage()!r}")

    assert not violations, "AC-001 / REQ-001: " + "; ".join(violations)
