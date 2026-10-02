"""Shared fixtures for the logging feature test suite.

setup_logger() is idempotent (REQ-002), so the in-process suite performs the
real setup exactly once, in a session-scoped fixture. Tests that need a fresh
setup (concurrency invariants, timing budgets, nested log paths) run Python
code in a subprocess via logging_test_helpers.run_python().
"""

from __future__ import annotations

import logging
from collections.abc import Iterator
from typing import Any

import pytest
from loguru import logger

from backend.logging import setup_logger


@pytest.fixture(scope="session", autouse=True)
def _logging_session_setup(tmp_path_factory: pytest.TempPathFactory) -> Iterator[Any]:
    """Perform the one-time in-process setup before the first test.

    This call configures the real sinks for the whole session. The log file
    lives in a session temp directory so file-content assertions have a stable
    path. Settings is imported lazily so the RED state (module missing) shows
    up as a fixture error rather than a collection error.
    """
    from settings_test_helpers import install_isolated_registry

    from backend.logging import Settings
    from backend.logging import register_settings as logging_register

    session_dir = tmp_path_factory.mktemp("logging_session")
    settings = Settings(log_file=str(session_dir / "logs" / "app.log"), log_level="DEBUG")
    # setup_logger() is no-arg (REQ-014) and reads logging.* from the shared
    # registry (AC-019), so the session's log path/level are set there first.
    # The registry is isolated (temp-dir value repository) so no test writes
    # to the shared default "settings/" directory (test isolation).
    registry = install_isolated_registry()
    logging_register(registry)
    registry.set_value("logging.log_file", settings.log_file)
    registry.set_value("logging.log_level", settings.log_level)
    setup_logger()
    yield settings


@pytest.fixture(scope="session")
def session_settings(_logging_session_setup: Any) -> Any:
    """The Settings instance used for the session's real setup."""
    return _logging_session_setup


@pytest.fixture(autouse=True)
def _stdlib_root_logging_restored() -> Iterator[None]:
    """Restore the stdlib root logger's routing state around every test.

    Three tests apply the alembic migration in-process, and ``migrations/env.py``
    calls ``fileConfig(alembic.ini)``, which replaces the root logger's handler
    list and level and disables the pre-existing non-root loggers. That drops the
    logging feature's stdlib intercept handler (REQ-003) and raises the root level
    above INFO, so every later test that routes stdlib records into loguru
    (AC-004, AC-005, EDGE-005, the logging integration pipeline) silently loses
    them — the full-suite flake, since the order is randomized. The snapshot and
    restore keep the process-global state installed by ``setup_logger()`` intact;
    no test's assertions change.
    """
    root = logging.getLogger()
    handlers: list[logging.Handler] = list(root.handlers)
    level = root.level
    manager = logging.Logger.manager
    disabled = {name: lg.disabled for name, lg in manager.loggerDict.items() if isinstance(lg, logging.Logger)}
    yield
    root.handlers[:] = handlers
    root.setLevel(level)
    for name, was_disabled in disabled.items():
        lg = manager.loggerDict.get(name)
        if isinstance(lg, logging.Logger):
            lg.disabled = was_disabled


class _Captured:
    """A captured loguru record.

    Exposes the message text via ``str(m)`` and the record fields via
    ``m["level"]``/``m["function"]``/... plus ``m["record"]`` for the whole
    record dict, matching the suite's assertions.
    """

    __slots__ = ("_record",)

    def __init__(self, record: dict[str, Any]) -> None:
        self._record = record

    def __str__(self) -> str:
        return str(self._record.get("message", ""))

    def __getitem__(self, key: str) -> Any:
        if key == "record":
            return self._record
        return self._record[key]


@pytest.fixture
def log_records() -> Iterator[list[Any]]:
    """Capture loguru records for the duration of a test.

    Each record supports ``str(m)`` (the message text) and ``m["level"]`` /
    ``m["record"]`` (record fields), matching the suite's assertions.

    The shared event bus is drained before the sink is added: the bus
    dispatches events asynchronously on a background worker, so stale events
    from previous tests (e.g. ``SettingChanged`` events from ``set_value``
    calls) can otherwise be dispatched during this test, triggering the
    logging feature's ``_configure()`` (which calls ``logger.remove()``) and
    removing the sink added here. Draining first ensures the stale events are
    dispatched before the sink exists, so the sink is safe for the test.
    """
    records: list[Any] = []

    def _sink(message: Any) -> None:
        records.append(_Captured(message.record))

    _drain_event_bus()
    handler_id = logger.add(_sink, level="DEBUG", catch=False)
    try:
        yield records
    finally:
        logger.remove(handler_id)


def _drain_event_bus() -> None:
    """Wait for the shared event bus to dispatch all queued events.

    The event bus dispatches events asynchronously on a background worker
    thread. Waiting for the queue to be empty (plus a short grace period for
    the worker to finish the in-flight dispatch) ensures no stale event is
    dispatched after this point. Used by the ``log_records`` fixture so a
    stale ``SettingChanged`` event does not trigger ``_configure()`` (which
    calls ``logger.remove()``) and remove the fixture's sink mid-test.
    """
    import time

    from settings_test_helpers import wait_for

    from backend.eventbus import get_event_bus

    bus = get_event_bus()
    if wait_for(lambda: bus.pending_count == 0):
        # Grace period for the worker to finish the in-flight dispatch.
        time.sleep(0.05)
