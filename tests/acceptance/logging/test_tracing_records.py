"""Traced-record acceptance tests (docs/specs/structlog-logging.md AC-011, AC-012, AC-014).

A traced call is asserted on the record the pipeline renders, not on the decorator's
internals: an entry record, an exit record carrying ``elapsed_ms`` (REQ-011), and an
exception record carrying the ``exception`` field (REQ-009). The kinds are told apart
by those fields, so the assertions survive the wording of the event text while still
pinning what the specification requires.

AC-003 (the same record's field set) lives in ``test_pipeline_backend.py``; the
secret half of the exception record (AC-015) lives in ``test_secrets.py``.
"""

from __future__ import annotations

import asyncio
from typing import Any

import pytest
from logging_test_helpers import traced_records, wait_for_traced_record

from backend.logging import logged, logged_class, setup_logger

_AC012_MESSAGE = "ac_012 exception propagation probe"
_AC014_THRESHOLD_MS = 10_000.0
_AC014_PUBLIC_RESULT = 1
_AC014_PRIVATE_RESULT = 2


def _exit_record(token: str, requirement: str) -> dict[str, Any]:
    """The traced exit record for ``token`` (fails with a named AC if it never lands)."""
    record = wait_for_traced_record(token, "exit")
    assert record is not None, f"{requirement}: {token} must emit an exit record carrying elapsed_ms"
    return record


def _entry_record(token: str, requirement: str) -> dict[str, Any]:
    """The traced entry record for ``token`` (an exit record alone is not enough)."""
    record = wait_for_traced_record(token, "entry")
    assert record is not None, f"{requirement}: {token} must emit an entry record before its exit record"
    return record


def test_ac_011_sync_and_async_traced_records() -> None:
    """AC-011: a traced sync call and a traced async call each emit an entry record and
    an exit record carrying ``elapsed_ms``, at the configured level."""
    setup_logger()

    @logged(level="INFO")
    def ac_011_sync_target() -> str:
        return "sync"

    @logged(level="INFO")
    async def ac_011_async_target() -> str:
        return "async"

    assert ac_011_sync_target() == "sync", "AC-011: a traced sync call must return its own result"
    assert asyncio.run(ac_011_async_target()) == "async", (
        "AC-011/REQ-007: a traced async call must await and return its own result"
    )

    for token in ("ac_011_sync_target", "ac_011_async_target"):
        entry = _entry_record(token, "AC-011")
        exit_record = _exit_record(token, "AC-011")

        elapsed = exit_record["elapsed_ms"]
        assert isinstance(elapsed, int | float) and not isinstance(elapsed, bool), (
            f"REQ-011: {token}'s exit record must carry the elapsed milliseconds as a number, got {elapsed!r}"
        )
        assert elapsed >= 0, f"INV-003: {token}'s elapsed_ms must be non-negative, got {elapsed!r}"

        assert entry["level"] == "INFO" and exit_record["level"] == "INFO", (
            f"AC-011: both records must be emitted at the configured level, "
            f"got entry={entry.get('level')!r} exit={exit_record.get('level')!r}"
        )


def test_ac_012_exception_record_and_propagation() -> None:
    """AC-012: a raising traced call emits an exception record carrying the exception type
    and message, and the exception itself propagates unchanged."""
    setup_logger()

    @logged
    def ac_012_boom() -> None:
        raise ValueError(_AC012_MESSAGE)

    with pytest.raises(ValueError) as raised:
        ac_012_boom()

    assert type(raised.value) is ValueError, "AC-012: the exception type must propagate unchanged"
    assert raised.value.args == (_AC012_MESSAGE,), "AC-012: the exception arguments must propagate unchanged"

    record = wait_for_traced_record("ac_012_boom", "exception")
    assert record is not None, "AC-012: the exception record must reach the file sink"

    rendered = str(record["exception"])
    assert "ValueError" in rendered, f"AC-012: the exception type must be in the record, got {rendered!r}"
    assert _AC012_MESSAGE in rendered, f"AC-012: the exception message must be in the record, got {rendered!r}"

    # The call is still traced end to end: the raising call has an entry record too.
    assert _entry_record("ac_012_boom", "AC-012") is not None


def test_ac_014_logged_class_records() -> None:
    """AC-014: ``@logged_class`` traces public methods (entry + exit with ``elapsed_ms``),
    emits nothing for private methods, and marks the class traced with its resolved threshold."""
    setup_logger()

    @logged_class(slow_threshold_ms=_AC014_THRESHOLD_MS)
    class Ac014Service:
        def ac_014_public_call(self) -> int:
            return _AC014_PUBLIC_RESULT

        def _ac_014_private_call(self) -> int:
            return _AC014_PRIVATE_RESULT

    service = Ac014Service()

    assert service.ac_014_public_call() == _AC014_PUBLIC_RESULT, "AC-014: a traced method must return its own result"
    assert _entry_record("ac_014_public_call", "AC-014") is not None, (
        "AC-014: a public method must emit an entry record"
    )
    assert _exit_record("ac_014_public_call", "AC-014") is not None, (
        "AC-014: a public method must emit an exit record carrying elapsed_ms"
    )

    assert service._ac_014_private_call() == _AC014_PRIVATE_RESULT, (
        "REQ-008: skipping a private method's records must not change what the method returns"
    )
    quiet: list[dict[str, Any]] = traced_records("ac_014_private_call")
    assert not quiet, f"REQ-008/AC-014: a private method must emit no records, got {quiet}"

    assert getattr(Ac014Service, "__logged_class__", False) is True, (
        "REQ-008/AC-014: the decorated class must carry the traced marker __logged_class__"
    )
    resolved = getattr(Ac014Service, "slow_threshold_ms", None)
    assert isinstance(resolved, int | float) and float(resolved) == _AC014_THRESHOLD_MS, (
        f"AC-014: the class must expose the resolved slow-call threshold, got {resolved!r}"
    )
