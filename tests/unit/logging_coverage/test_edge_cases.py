"""Unit tests for the logging-coverage edge cases (EDGE-001..EDGE-006).

These cover the edge conditions and error conditions from the spec.
"""

from __future__ import annotations

import time
import uuid
from pathlib import Path
from typing import Any

import pytest
from logging_coverage_test_helpers import (
    INVENTORY_CLASSES,
    entry_records,
    exception_records,
    exit_records,
    level_name,
)
from loguru import logger

from backend.authentication.tracker import InMemoryAttemptTracker
from backend.logging import logged, setup_logger
from backend.usermanagement.errors import UserNotFoundError
from backend.usermanagement.repository import SqliteUserRepository, UserRepository
from backend.usermanagement.service import UserManager


def _is_concrete_threshold(value: Any) -> bool:
    return (
        value is not None
        and isinstance(value, (int, float))
        and not isinstance(value, bool)
        and value > 0
    )


def test_slow_threshold_exceeded(log_records: list[Any]) -> None:
    """EDGE-001: a traced call exceeding its ``slow_threshold_ms`` logs a WARNING and
    is NOT interrupted."""
    @logged(slow_threshold_ms=1)
    def slow() -> None:
        time.sleep(0.05)

    slow()  # must not raise
    warnings = [r for r in exit_records(log_records) if level_name(r) == "WARNING"]
    assert len(warnings) == 1, "expected exactly one WARNING exit record"
    # A real traced class has a concrete threshold, so its slow calls are detected.
    assert _is_concrete_threshold(getattr(InMemoryAttemptTracker, "slow_threshold_ms", None))


def test_sink_failure_graceful(log_records: list[Any], tmp_path: Any) -> None:
    """EDGE-002: a log sink failure during a traced call is handled gracefully; the
    call completes normally."""

    def failing_sink(message: Any) -> None:
        raise RuntimeError("sink failure")

    handler_id = logger.add(failing_sink, level="DEBUG", catch=True)
    try:
        repo = SqliteUserRepository(f"sqlite:///{tmp_path}/edge.db")
        result = repo.get_by_username("probe")  # must not raise
        assert result is None
    finally:
        logger.remove(handler_id)
    # The traced call still produced an entry record (via the working sink).
    assert any(
        "SqliteUserRepository.get_by_username" in str(r) for r in entry_records(log_records)
    )


def test_abc_subclass_traced(log_records: list[Any], tmp_path: Any) -> None:
    """EDGE-003: a concrete subclass of a traced ABC produces log records; the ABC
    remains abstract."""
    # The ABC remains abstract.
    with pytest.raises(TypeError):
        UserRepository()  # type: ignore[call-arg]
    # The concrete subclass is traced.
    repo = SqliteUserRepository(f"sqlite:///{tmp_path}/edge3.db")
    repo.get_by_username("probe")
    assert any(
        "SqliteUserRepository.get_by_username" in str(r) for r in entry_records(log_records)
    )


def test_traced_method_exception_propagates(log_records: list[Any], tmp_path: Any) -> None:
    """EDGE-004: a traced method that raises produces an exception record and the
    exception propagates to the caller (not swallowed)."""
    manager = UserManager(SqliteUserRepository(f"sqlite:///{tmp_path}/edge4.db"))
    try:
        manager.get_user(uuid.uuid4())
        raise AssertionError("expected UserNotFoundError")
    except UserNotFoundError:
        pass
    # An exception record was produced for the traced method, and the ABC subject is
    # traced.
    assert any("UserManager.get_user" in str(r) for r in exception_records(log_records))
    assert getattr(INVENTORY_CLASSES["UserManager"], "__logged_class__", False) is True


def test_setup_logger_idempotent() -> None:
    """EDGE-005: ``setup_logger`` is idempotent — a second call adds no sinks; the
    entrypoint relies on this (it calls ``setup_logger`` exactly once)."""
    setup_logger()
    first = len(logger._core.handlers)
    setup_logger()
    second = len(logger._core.handlers)
    assert first == second, "a second setup_logger call must be a no-op"
    # The entrypoint relies on this idempotency: main.py calls setup_logger exactly once.
    main_src = Path("src/main.py").read_text(encoding="utf-8")
    assert main_src.count("setup_logger(") == 1, "src/main.py must call setup_logger exactly once"


def test_traced_method_no_args(log_records: list[Any]) -> None:
    """EDGE-006: a traced method called with no arguments produces entry/exit records
    without argument context."""
    from backend.eventbus.eventbus import get_event_bus

    get_event_bus()
    entries = [r for r in entry_records(log_records) if str(r).startswith(">> get_event_bus called")]
    exits = [r for r in exit_records(log_records) if str(r).startswith("<< get_event_bus returned")]
    assert len(entries) == 1, "expected an entry record for the no-arg call"
    assert len(exits) == 1, "expected an exit record for the no-arg call"
