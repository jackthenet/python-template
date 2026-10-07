"""Property tests for the structlog record pipeline (docs/specs/structlog-logging.md).

This module holds the pipeline-core invariants: INV-001 (the feature logger owns
exactly one console handler and one file handler) and INV-004 (no other logger's
routing state changes). INV-002, INV-003 and INV-005 belong to the tracing
decorators and are added here by that task.

The strategies generate only in-domain values: the concurrency count is a
positive thread count, the reconfigure level is one of the ``logging.log_level``
SELECT options, and the renderer is one of the ``"text" | "json" | None`` values
§3 defines.
"""

from __future__ import annotations

import asyncio
import inspect
import logging
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from logging_test_helpers import (
    PIPELINE_COUNT_CODE,
    bound_logger,
    file_size,
    managed_sinks,
    pipeline_logger,
    record_mentions,
    records_since,
    run_python,
    session_log_path,
    wait_for_record_since,
)
from settings_test_helpers import set_value_settled

from backend.logging import logged, setup_logger
from backend.settings import get_settings_registry

_ROTATION_BYTES = 2048
_ROTATION_BACKUPS = 3
_WAIT_TIMEOUT_S = 10.0


def test_inv_001_concurrent_setup_owns_two_handlers(tmp_path: Path) -> None:
    """INV-001: for any number of concurrent setup_logger() calls, the feature logger owns exactly one console handler and one file handler.

    The subprocess shape is required: setup_logger() is idempotent per process,
    so a fresh interpreter is the only way to observe n competing setups. Beyond
    the pair count, the example pins the ownership consequences of D1 — a single
    owning logger, non-propagating, and the file handler rotating with the live
    ``logging.log_max_bytes`` / ``logging.log_backup_count`` values (REQ-002).
    """

    @settings(deadline=None, max_examples=8)  # each example costs a fresh interpreter
    @given(st.integers(min_value=1, max_value=16))
    def inner(n: int) -> None:
        log_file = tmp_path / f"inv_001_pipeline_{n}.log"
        code = f"""
import threading, tempfile
from backend.settings import SettingsRegistry, YamlValueRepository
from backend.settings import registry as _reg_mod
from backend.logging import register_settings as logging_register, setup_logger
reg = SettingsRegistry(value_repository=YamlValueRepository(tempfile.mkdtemp()))
_reg_mod._registry[0] = reg
logging_register(reg)
reg.set_value('logging.log_file', {str(log_file)!r})
reg.set_value('logging.log_level', 'INFO')
reg.set_value('logging.log_max_bytes', {_ROTATION_BYTES})
reg.set_value('logging.log_backup_count', {_ROTATION_BACKUPS})
errors = []

def worker():
    try:
        setup_logger()
    except BaseException as e:
        errors.append(e)

threads = [threading.Thread(target=worker) for _ in range({n})]
for t in threads:
    t.start()
for t in threads:
    t.join()
print("ERRORS", len(errors))
{PIPELINE_COUNT_CODE}
print("PROPAGATE", _owners[0].propagate if _owners else None)
print("MAXBYTES", _rotating[0].maxBytes if _rotating else 0)
print("BACKUPS", _rotating[0].backupCount if _rotating else 0)
"""
        result = run_python(code)
        assert result.returncode == 0, f"INV-001: the subprocess failed:\n{result.stderr}"
        out = result.stdout
        assert "ERRORS 0" in out, f"INV-001: {n} concurrent setups raised, output:\n{out}"
        assert "OWNERS 1" in out, f"INV-001: {n} concurrent setups, output:\n{out}"
        assert "CONSOLE 1" in out, f"INV-001: {n} concurrent setups, output:\n{out}"
        assert "FILE 1" in out, f"INV-001: {n} concurrent setups, output:\n{out}"
        assert "FEATURE_HANDLERS 2" in out, f"INV-001/D1: {n} concurrent setups, output:\n{out}"
        assert "PROPAGATE False" in out, f"REQ-003/D1: the feature logger must not propagate, output:\n{out}"
        assert f"MAXBYTES {_ROTATION_BYTES}" in out, (
            f"REQ-002: the file sink must rotate at the live value, output:\n{out}"
        )
        assert f"BACKUPS {_ROTATION_BACKUPS}" in out, f"REQ-002: retention must use the live value, output:\n{out}"

    inner()


def _routing_state() -> dict[str, tuple[tuple[logging.Handler, ...], int, bool]]:
    """The (handlers, level, disabled) triple of every named logger in the process.

    The root logger is not in ``loggerDict``, so it is deliberately absent here:
    INV-004's only exception is the single forwarding handler the feature
    installs on the root logger, which the test checks separately.
    """
    return {
        name: (tuple(lg.handlers), lg.level, lg.disabled)
        for name, lg in logging.Logger.manager.loggerDict.items()
        if isinstance(lg, logging.Logger)
    }


def test_inv_004_other_loggers_untouched() -> None:
    """INV-004: setup, live reconfigure and a renderer change leave every other logger's routing state unchanged.

    The foreign logger keeps its handler set, level and disabled state through
    every logging-feature operation; the root logger may gain at most the single
    forwarding handler (REQ-003) and never loses a handler it already had.
    """

    @settings(deadline=None, max_examples=20)
    @given(
        operation=st.sampled_from(("setup", "reconfigure", "renderer")),
        level=st.sampled_from(("DEBUG", "INFO", "WARNING", "ERROR")),
        renderer=st.sampled_from(("text", "json", None)),
    )
    def inner(operation: str, level: str, renderer: str | None) -> None:
        setup_logger()
        registry = get_settings_registry()
        original_level = registry.get_value("logging.log_level")
        foreign = logging.getLogger("inv_004_foreign")
        foreign.handlers.clear()
        foreign.addHandler(logging.NullHandler())
        foreign.setLevel(logging.WARNING)
        try:
            before = _routing_state()
            root_before = list(logging.getLogger().handlers)

            if operation == "setup":
                setup_logger()
            elif operation == "reconfigure":
                set_value_settled(registry, "logging.log_level", level)
            else:
                assert "renderer" in inspect.signature(setup_logger).parameters, (
                    "REQ-006: setup_logger() must accept a renderer parameter"
                )
                setup_logger(renderer=renderer)

            feature = pipeline_logger()
            after = _routing_state()
            changed = sorted(
                name for name, state in before.items() if after.get(name) != state and name != feature.name
            )
            assert not changed, f"INV-004: {operation} changed the routing state of {changed}"

            root_after = list(logging.getLogger().handlers)
            added = [handler for handler in root_after if handler not in root_before]
            assert len(added) <= 1, (
                f"INV-004/REQ-003: {operation} installed {len(added)} root handlers, at most one is allowed"
            )
            missing = [handler for handler in root_before if handler not in root_after]
            assert not missing, f"INV-004: {operation} removed {len(missing)} root handler(s) it does not own"
        finally:
            set_value_settled(registry, "logging.log_level", original_level)
            foreign.handlers.clear()
            foreign.setLevel(logging.NOTSET)

    inner()


# --------------------------------------------------------------------------
# INV-002 / INV-003 / INV-005: the invariants of the tracing decorators
#
# Every example emits through the session pipeline, waits for a record the file sink
# appended after its own byte offset, and then reads only that window — so examples
# never read each other's records and a leak is attributed to the call that caused
# it. The pipeline precondition is asserted once per test, before the Hypothesis
# loop: without the managed sinks there is no pipeline holding the invariant, and one
# fast failure is the honest RED signal instead of one timeout per example.
# --------------------------------------------------------------------------

# A secret is always non-empty and long enough that a coincidental substring match
# in an unrelated record is not a realistic failure mode.
_SECRET_ALPHABET = "abcdefghijklmnopqrstuvwxyz0123456789"
_SECRET_MIN_CHARS = 16
_SECRET_MAX_CHARS = 24
_REQUIRED_RECORD_FIELDS = frozenset({"level", "logger", "event", "timestamp", "file", "line"})


@logged
def inv_002_leaky_probe(secret: str) -> None:
    """A traced call that holds ``secret`` in a local of the frame that raises."""
    local_value = secret  # noqa: F841  the local's presence in the raising frame is the point
    raise RuntimeError("inv_002 leak probe")


@logged
def inv_003_sync_probe(steps: int) -> int:
    return sum(range(steps))


@logged
async def inv_003_async_probe(steps: int) -> int:
    return sum(range(steps))


@logged
def inv_005_sync_probe() -> None:
    return None


@logged
async def inv_005_async_probe() -> None:
    return None


@logged
def inv_005_raising_probe() -> None:
    raise RuntimeError("inv_005 raising probe")


def _record_for(token: str, field: str | None = None) -> Callable[[dict[str, Any]], bool]:
    """Predicate: a record naming ``token`` that carries ``field`` (when one is given)."""

    def _predicate(record: dict[str, Any]) -> bool:
        return record_mentions(record, token) and (field is None or field in record)

    return _predicate


def test_inv_002_no_local_value_ever_recorded() -> None:
    """INV-002 / NFR-003: for any traced call and any value held in a local, no emitted record contains that value."""
    setup_logger()
    managed_sinks()
    path = session_log_path()

    @settings(deadline=None, max_examples=10)
    @given(secret=st.text(alphabet=_SECRET_ALPHABET, min_size=_SECRET_MIN_CHARS, max_size=_SECRET_MAX_CHARS))
    def inner(secret: str) -> None:
        before = file_size(path)
        with pytest.raises(RuntimeError):
            inv_002_leaky_probe(secret)

        record = wait_for_record_since(
            path, before, _record_for("inv_002_leaky_probe", "exception"), timeout=_WAIT_TIMEOUT_S
        )
        assert record is not None, "INV-002: the raising traced call must emit an exception record to the file sink"
        assert "RuntimeError" in str(record["exception"]), (
            f"INV-002: the record must still carry the exception, got {record['exception']!r}"
        )

        emitted = records_since(path, before)
        assert emitted, "INV-002: the traced call must emit records through the pipeline"
        window = path.read_bytes()[before:].decode("utf-8", errors="replace")
        assert secret not in window, f"INV-002/NFR-003: the local value {secret!r} leaked into the emitted records"

    inner()


def test_inv_003_elapsed_non_negative() -> None:
    """INV-003: for any traced sync or async call, its exit record's elapsed_ms is a non-negative number."""
    setup_logger()
    managed_sinks()
    path = session_log_path()

    @settings(deadline=None, max_examples=12)
    @given(is_async=st.booleans(), steps=st.integers(min_value=0, max_value=2000))
    def inner(is_async: bool, steps: int) -> None:
        token = "inv_003_async_probe" if is_async else "inv_003_sync_probe"
        before = file_size(path)

        result = asyncio.run(inv_003_async_probe(steps)) if is_async else inv_003_sync_probe(steps)
        assert result == sum(range(steps)), "INV-003: tracing must not change what the traced call returns"

        record = wait_for_record_since(path, before, _record_for(token, "elapsed_ms"), timeout=_WAIT_TIMEOUT_S)
        assert record is not None, f"INV-003/REQ-011: {token} must emit an exit record carrying elapsed_ms"

        for exit_record in [entry for entry in records_since(path, before) if "elapsed_ms" in entry]:
            elapsed = exit_record["elapsed_ms"]
            assert isinstance(elapsed, int | float) and not isinstance(elapsed, bool), (
                f"INV-003/REQ-011: elapsed_ms must be a number, got {elapsed!r}"
            )
            assert elapsed >= 0, f"INV-003: elapsed_ms must be non-negative, got {elapsed!r}"

    inner()


def _emit_probe(kind: str, level: str) -> Callable[[dict[str, Any]], bool]:
    """Emit one INV-005 probe of the generated kind at the generated level.

    Returns the predicate selecting the record that probe must produce: the exception
    field for the raising probe, ``elapsed_ms`` for a traced one, the bare event otherwise.
    """
    if kind == "statement":
        token = "inv_005_statement_probe"
        getattr(bound_logger("inv_005_statement_logger"), level.lower())(token)
        return _record_for(token)
    if kind == "raising":
        token = "inv_005_raising_probe"
        with pytest.raises(RuntimeError):
            logged(level=level)(inv_005_raising_probe)()
        return _record_for(token, "exception")
    token = "inv_005_async_probe" if kind == "async" else "inv_005_sync_probe"
    traced = logged(level=level)(inv_005_async_probe if kind == "async" else inv_005_sync_probe)
    if kind == "async":
        asyncio.run(traced())
    else:
        traced()
    return _record_for(token, "elapsed_ms")


def test_inv_005_required_fields_present() -> None:
    """INV-005 / REQ-011: every record the pipeline emits carries level, logger, event, timestamp, file and line; a traced exit record additionally carries elapsed_ms."""
    setup_logger()
    managed_sinks()
    path = session_log_path()

    @settings(deadline=None, max_examples=12)
    @given(
        kind=st.sampled_from(("statement", "sync", "async", "raising")),
        level=st.sampled_from(("DEBUG", "INFO", "WARNING")),
    )
    def inner(kind: str, level: str) -> None:
        before = file_size(path)
        predicate = _emit_probe(kind, level)

        record = wait_for_record_since(path, before, predicate, timeout=_WAIT_TIMEOUT_S)
        assert record is not None, f"INV-005: the {kind} call emitted no record the test could wait for"

        emitted = records_since(path, before)
        assert emitted, f"INV-005: the {kind} call must emit records through the pipeline"
        for entry in emitted:
            missing = _REQUIRED_RECORD_FIELDS - entry.keys()
            assert not missing, f"INV-005/REQ-011: a {kind} record is missing {sorted(missing)}: {entry!r}"
        if kind in ("sync", "async"):
            assert any("elapsed_ms" in entry for entry in emitted), (
                f"INV-005/REQ-011: the traced {kind} exit record must additionally carry elapsed_ms"
            )

    inner()
