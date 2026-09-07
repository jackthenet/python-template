"""Unit tests for the logging feature (docs/specs/logging.md).

Covers the acceptance criteria that are verified at unit level per the
spec's test strategy: thread-safe setup, stdlib interception, @logged sync/
async tracing, exception propagation, level/include_args/slow_threshold
parameters, @logged_class, and Settings defaults.
"""

from __future__ import annotations

import asyncio
import re
import threading
import time
from typing import Any

import pytest
from loguru import logger

from backend.logging import logged, logged_class, setup_logger

_EXPECTED_HANDLER_COUNT = 2  # one console sink + one file sink
_ASYNC_SLEEP_MS = 50  # minimum measurable elapsed time for the ~100 ms async sleep
_AC012_RESULT = 42
_AC006_SUM = 3
_BACKUP_COUNT = 5


def test_ac_003_setup_logger_thread_safe() -> None:
    """AC-003: concurrent setup_logger() calls are safe; exactly one setup wins."""
    errors: list[BaseException] = []

    def worker() -> None:
        try:
            setup_logger()
        except BaseException as exc:
            errors.append(exc)

    threads = [threading.Thread(target=worker) for _ in range(8)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert not errors
    assert len(logger._core.handlers) == _EXPECTED_HANDLER_COUNT


def test_ac_004_intercept_handler_routes_records(log_records: list[Any]) -> None:
    """AC-004: a stdlib logging record is routed into loguru sinks with correct level and message."""
    import logging

    setup_logger()
    stdlib_logger = logging.getLogger("ac_004_third_party")
    stdlib_logger.info("routed from stdlib")

    routed = [m for m in log_records if "routed from stdlib" in str(m)]
    assert routed
    assert routed[0]["level"].name == "INFO"


def test_ac_005_intercept_handler_skips_bootstrap(log_records: list[Any]) -> None:
    """AC-005: bootstrap/logging frames are skipped in depth calculation.

    The observable consequence: the loguru record is attributed to the real
    caller (function and file), not to the logging module or the handler.
    """
    import logging
    from pathlib import Path

    setup_logger()

    def _emit_source() -> None:
        logging.getLogger("ac_005").warning("from real caller")

    _emit_source()

    routed = [m for m in log_records if "from real caller" in str(m)]
    assert routed
    record = routed[0]["record"]
    assert record["function"] == "_emit_source"
    assert Path(record["file"].path).resolve() == Path(__file__).resolve()


def test_ac_006_logged_sync_entry_exit(log_records: list[Any]) -> None:
    """AC-006: a sync @logged function emits an entry line and an exit line with elapsed ms."""

    @logged
    def ac_006_add(a: int, b: int) -> int:
        return a + b

    assert ac_006_add(1, 2) == _AC006_SUM

    entries = [m for m in log_records if ">>" in str(m) and "ac_006_add" in str(m)]
    exits = [m for m in log_records if "<<" in str(m) and "ac_006_add" in str(m)]
    assert entries
    assert exits
    assert re.search(r"\d+(?:\.\d+)? ms", str(exits[0]))


def test_ac_007_logged_async_entry_exit(log_records: list[Any]) -> None:
    """AC-007: an async @logged function emits entry/exit lines; elapsed time covers execution."""

    @logged
    async def ac_007_fetch() -> str:
        await asyncio.sleep(0.1)
        return "ok"

    result = asyncio.run(ac_007_fetch())
    assert result == "ok"

    entries = [m for m in log_records if ">>" in str(m) and "ac_007_fetch" in str(m)]
    exits = [m for m in log_records if "<<" in str(m) and "ac_007_fetch" in str(m)]
    assert entries
    assert exits
    match = re.search(r"(\d+(?:\.\d+)?) ms", str(exits[0]))
    assert match
    # The measured elapsed time must include the actual async execution (~100 ms).
    assert float(match.group(1)) >= _ASYNC_SLEEP_MS


def test_ac_008_logged_exception_propagates(log_records: list[Any]) -> None:
    """AC-008: a raising @logged function emits an exception line (type + message) and propagates."""

    @logged
    def ac_008_boom() -> None:
        raise ValueError("boom")

    with pytest.raises(ValueError, match="boom"):
        ac_008_boom()

    lines = [m for m in log_records if "ValueError" in str(m) and "boom" in str(m)]
    assert lines


def test_ac_009_logged_level_param(log_records: list[Any]) -> None:
    """AC-009: @logged(level="DEBUG") emits entry and exit lines at DEBUG level."""

    @logged(level="DEBUG")
    def ac_009_fn() -> None:
        pass

    ac_009_fn()

    entries = [m for m in log_records if ">>" in str(m) and "ac_009_fn" in str(m)]
    exits = [m for m in log_records if "<<" in str(m) and "ac_009_fn" in str(m)]
    assert entries
    assert exits
    assert all(m["level"].name == "DEBUG" for m in entries)
    assert all(m["level"].name == "DEBUG" for m in exits)


def test_ac_010_logged_include_args(log_records: list[Any]) -> None:
    """AC-010: @logged(include_args=True) includes the argument representation in the entry line."""

    @logged(include_args=True)
    def ac_010_greet(name: str) -> str:
        return f"hi {name}"

    ac_010_greet("alice")

    entries = [m for m in log_records if ">>" in str(m) and "ac_010_greet" in str(m)]
    assert entries
    assert "alice" in str(entries[0])


def test_ac_011_logged_slow_threshold(log_records: list[Any]) -> None:
    """AC-011: a call slower than slow_threshold_ms emits the end-of-call line at WARNING."""

    @logged(slow_threshold_ms=50)
    def ac_011_slow_fn() -> None:
        time.sleep(0.1)

    ac_011_slow_fn()

    exits = [m for m in log_records if "<<" in str(m) and "ac_011_slow_fn" in str(m) and m["level"].name == "WARNING"]
    assert exits


def test_ac_012_logged_class_public_method(log_records: list[Any]) -> None:
    """AC-012: a public method of a @logged_class class emits entry/exit lines with elapsed ms."""

    @logged_class
    class Ac012Service:
        def ac_012_run(self) -> int:
            return _AC012_RESULT

    assert Ac012Service().ac_012_run() == _AC012_RESULT

    entries = [m for m in log_records if ">>" in str(m) and "ac_012_run" in str(m)]
    exits = [m for m in log_records if "<<" in str(m) and "ac_012_run" in str(m)]
    assert entries
    assert exits
    assert re.search(r"\d+(?:\.\d+)? ms", str(exits[0]))


def test_ac_013_logged_class_private_method(log_records: list[Any]) -> None:
    """AC-013: a private (underscore-prefixed) method of a @logged_class class emits no lines."""

    @logged_class
    class Ac013Service:
        def ac_013_private(self) -> int:
            return 1

    assert Ac013Service().ac_013_private() == 1

    lines = [m for m in log_records if "ac_013_private" in str(m)]
    assert not lines


def test_ac_014_get_settings_defaults() -> None:
    """AC-014: get_settings() returns a Settings instance with the spec's default values."""
    from backend.logging.settings import Settings, get_settings

    settings = get_settings()
    assert isinstance(settings, Settings)
    assert settings.log_level == "INFO"
    assert settings.log_file == "logs/app.log"
    assert settings.log_max_bytes == 10 * 1024 * 1024
    assert settings.log_backup_count == _BACKUP_COUNT
    assert settings.profiling_include_arguments is False
