"""Shared fixtures for the logging feature test suite.

setup_logger() is idempotent (REQ-002), so the in-process suite performs the
real setup exactly once, in a session-scoped fixture. Tests that need a fresh
setup (concurrency invariants, timing budgets, nested log paths) run Python
code in a subprocess via logging_test_helpers.run_python().
"""

from __future__ import annotations

import logging
import sys
from collections.abc import Callable, Iterator
from typing import Any

import pytest

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
    above INFO, so every later test that routes stdlib records into the pipeline
    (AC-004, AC-006, the logging integration pipeline) silently loses them — the
    full-suite flake, since the order is randomized. The snapshot and
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


@pytest.fixture(autouse=True)
def _sqlite_engines_disposed(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Close every engine created during a test (test hygiene, no behavior change).

    The SQLite repositories hold their engine for the instance's lifetime and never
    dispose it, so a finished test's pooled connection is garbage-collected while still
    open and CPython reports ``ResourceWarning: unclosed database`` — 1075 of them per CI
    run, each attributed to whatever statement happened to trigger the collection. The
    repositories' own specs pin no connection-lifecycle contract, so the fix belongs to
    the suite rather than to the features.

    ``Engine.dispose()`` closes the pool's connections and installs a fresh pool, so an
    engine that outlives its test stays usable. ``create_engine`` is wrapped wherever it
    is already bound — the repository modules import it by name, so patching only
    ``sqlmodel``/``sqlalchemy`` would not reach them — and a new SQLite repository needs
    no registration here.
    """
    engines: list[Any] = []

    def _tracking(create: Callable[..., Any]) -> Callable[..., Any]:
        def _create_engine(*args: Any, **kwargs: Any) -> Any:
            engine = create(*args, **kwargs)
            engines.append(engine)
            return engine

        return _create_engine

    for module in list(sys.modules.values()):
        create_engine = getattr(module, "create_engine", None)
        if callable(create_engine):
            monkeypatch.setattr(module, "create_engine", _tracking(create_engine))
    yield
    for engine in engines:
        engine.dispose()


@pytest.fixture
def log_records() -> Iterator[list[Any]]:
    """Capture log records for the duration of a test.

    Each record supports ``str(record)`` (the message text) and ``record["level"]`` /
    ``record["record"]`` (record fields), matching the suite's assertions.

    The capture is the pipeline's own stdlib handler (structlog-logging T-002/T-006):
    traced records and feature statements arrive through it. The loguru sink half of
    the dual capture is gone with the last loguru statement (T-006).

    The shared event bus is drained before the sinks are added: the bus
    dispatches events asynchronously on a background worker, so stale events
    from previous tests (e.g. ``SettingChanged`` events from ``set_value``
    calls) can otherwise be dispatched during this test and reconfigure the
    pipeline mid-test. Draining first ensures the stale events are dispatched
    before the sinks exist, so the capture is stable for the test.
    """
    from logging_coverage_test_helpers import pipeline_capture

    records: list[Any] = []

    _drain_event_bus()
    with pipeline_capture(records):
        yield records


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
