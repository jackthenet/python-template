"""Property tests for the logging feature (docs/specs/logging.md).

Covers the spec's invariants with Hypothesis: concurrent setup sink counts,
non-negative elapsed time, and unchanged exception propagation.
"""

from __future__ import annotations

import asyncio
import re
import time
from pathlib import Path
from typing import Any

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from logging_test_helpers import run_python

from backend.logging import logged


def test_inv_001_concurrent_setup_logger_sinks(tmp_path: Path) -> None:
    """INV-001: for any number of concurrent setup_logger() calls, exactly one console + one file sink.

    Each example runs in a subprocess because setup_logger() is idempotent
    per process and the in-process session setup already configured the sinks.
    """

    @settings(deadline=None)
    @given(st.integers(min_value=1, max_value=16))
    def inner(n: int) -> None:
        log_file = tmp_path / f"inv_001_{n}.log"
        code = f"""
import threading
from backend.settings import get_settings_registry
from backend.logging import register_settings as logging_register, setup_logger
from loguru import logger

reg = get_settings_registry()
logging_register(reg)
reg.set_value('logging.log_file', {str(log_file)!r})
reg.set_value('logging.log_level', 'INFO')
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
print("HANDLERS", len(logger._core.handlers))
"""
        result = run_python(code)
        assert result.returncode == 0, result.stderr
        assert "ERRORS 0" in result.stdout
        assert "HANDLERS 2" in result.stdout

    inner()


def test_inv_002_elapsed_time_non_negative(log_records: list[Any]) -> None:
    """INV-002: for any sync or async @logged function, the reported elapsed time is non-negative."""

    @given(st.booleans(), st.floats(min_value=0.0, max_value=0.05, allow_nan=False, allow_infinity=False))
    def inner(is_async: bool, sleep_s: float) -> None:
        log_records.clear()

        @logged
        def inv_002_sync() -> None:
            time.sleep(sleep_s)

        @logged
        async def inv_002_async() -> None:
            await asyncio.sleep(sleep_s)

        if is_async:
            asyncio.run(inv_002_async())
        else:
            inv_002_sync()

        name = "inv_002_async" if is_async else "inv_002_sync"
        exits = [m for m in log_records if "<<" in str(m) and name in str(m)]
        assert exits, f"no exit line for {name}"
        for m in exits:
            match = re.search(r"(\d+(?:\.\d+)?) ms", str(m))
            assert match, f"no elapsed ms in {str(m)!r}"
            assert float(match.group(1)) >= 0.0

    inner()


def test_inv_003_exception_propagates_unchanged() -> None:
    """INV-003: for any raising @logged function, the exception propagates unchanged (type + args)."""

    @given(
        st.sampled_from([ValueError, RuntimeError, KeyError]),
        st.text(min_size=0, max_size=20),
    )
    def inner(exc_type: type[BaseException], message: str) -> None:
        @logged
        def inv_003_boom() -> None:
            raise exc_type(message)

        with pytest.raises(exc_type) as exc_info:
            inv_003_boom()

        assert type(exc_info.value) is exc_type
        assert exc_info.value.args == (message,)

    inner()
