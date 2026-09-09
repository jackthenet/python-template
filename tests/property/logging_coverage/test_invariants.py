"""Property tests for the logging-coverage invariants (INV-001..INV-004).

These hold over a large input space and are verified with Hypothesis. Tracing is
verified by capturing log records. A ``tempfile.TemporaryDirectory`` context
manager is used (not the function-scoped ``tmp_path`` fixture) so Hypothesis
does not raise a function-scoped-fixture health check.
"""

from __future__ import annotations

import tempfile
import time
from datetime import timedelta
from pathlib import Path
from typing import Any, Callable

from hypothesis import given, settings
from hypothesis import strategies as st
from loguru import logger

from logging_coverage_test_helpers import (
    capture_records,
    entry_records,
    exit_records,
    for_qualname,
    parse_elapsed_ms,
)
from backend.authentication.tokens import hash_token, new_token
from backend.authentication.tracker import InMemoryAttemptTracker
from backend.logging import logged
from backend.settings.registry import SettingsRegistry
from backend.settings.repository import MemoryTemplateRepository
from backend.usermanagement.repository import SqliteUserRepository


def _subjects(tmp_path: Path) -> list[tuple[str, Callable[[], Any]]]:
    """Lightweight (qualname, zero-arg callable) pairs over the inventory.

    Uses ``sqlite:///:memory:`` (no file) so the ``TemporaryDirectory`` cleanup
    does not hit a Windows SQLite file-lock ``PermissionError`` — the in-memory
    connection is never locked on disk.
    """
    db = "sqlite:///:memory:"
    reg = SettingsRegistry(template_repository=MemoryTemplateRepository())
    tracker = InMemoryAttemptTracker(3, timedelta(minutes=5))
    urepo = SqliteUserRepository(db)
    mem = MemoryTemplateRepository()
    return [
        ("new_token", new_token),
        ("hash_token", lambda: hash_token("x")),
        ("SettingsRegistry.has", lambda: reg.has("k")),
        ("InMemoryAttemptTracker.is_locked", lambda: tracker.is_locked("id")),
        ("SqliteUserRepository.get_by_username", lambda: urepo.get_by_username("nobody")),
        ("MemoryTemplateRepository.list", mem.list),
    ]


_N_SUBJECTS = 6


@given(idx=st.integers(min_value=0, max_value=_N_SUBJECTS - 1))
@settings(max_examples=25, deadline=None)
def test_one_entry_one_exit_per_call(idx: int) -> None:
    """INV-001: a single call to a traced method produces exactly one entry and
    exactly one exit log record."""
    with tempfile.TemporaryDirectory() as tmp:
        qualname, invoke = _subjects(Path(tmp))[idx]
        with capture_records() as records:
            invoke()
        assert len(for_qualname(entry_records(records), qualname)) == 1, (
            f"{qualname}: expected exactly one entry record"
        )
        assert len(for_qualname(exit_records(records), qualname)) == 1, (
            f"{qualname}: expected exactly one exit record"
        )


@given(secret=st.from_regex(r"secret-[a-z0-9]{16}", fullmatch=True))
@settings(max_examples=25, deadline=None)
def test_secret_args_never_logged(secret: str) -> None:
    """INV-002: for any arguments, a secret handler's log records never include the
    raw argument values."""
    with capture_records() as records:
        hash_token(secret)
    for record in records:
        assert secret not in str(record), f"raw secret leaked into log record: {secret!r}"
    # Tracing is active (records were produced).
    assert any("hash_token" in str(r) for r in entry_records(records))


@given(idx=st.integers(min_value=0, max_value=_N_SUBJECTS - 1))
@settings(max_examples=25, deadline=None)
def test_elapsed_ms_non_negative(idx: int) -> None:
    """INV-003: for any traced call, the exit record's elapsed milliseconds is
    non-negative."""
    with tempfile.TemporaryDirectory() as tmp:
        qualname, invoke = _subjects(Path(tmp))[idx]
        with capture_records() as records:
            invoke()
        exits = for_qualname(exit_records(records), qualname)
        assert exits, f"{qualname}: no exit record produced"
        for record in exits:
            ms = parse_elapsed_ms(str(record))
            assert ms is not None, f"{qualname}: exit record has no elapsed ms"
            assert ms >= 0, f"{qualname}: elapsed ms is negative"


@given(sleep_ms=st.integers(min_value=0, max_value=20))
@settings(max_examples=25, deadline=None)
def test_tracing_never_interrupts_call(sleep_ms: int) -> None:
    """INV-004: regardless of whether the slow threshold is exceeded or a sink fails,
    the traced call completes normally."""

    @logged(slow_threshold_ms=0)
    def slow() -> None:
        time.sleep(sleep_ms / 1000.0)

    def failing_sink(message: Any) -> None:
        raise RuntimeError("sink failure")

    with tempfile.TemporaryDirectory() as tmp:
        handler_id = logger.add(failing_sink, level="DEBUG", catch=True)
        try:
            with capture_records() as records:
                slow()  # slow call completes despite the failing sink
                _qualname, invoke = _subjects(Path(tmp))[0]
                invoke()  # inventory call completes despite the failing sink
        finally:
            logger.remove(handler_id)
        # Both completed; the inventory call is traced.
        assert any("new_token" in str(r) for r in records)
