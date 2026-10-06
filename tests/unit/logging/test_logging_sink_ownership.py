"""Sink-ownership tests for the logging feature (docs/specs/logging.md REQ-001/INV-001).

Re-derived from the amended specs for the stdlib pipeline (docs/specs/structlog-logging.md
ADR-082): the managed sinks are ordinary handlers owned by the feature's dedicated
logger, and a third-party sink is an ordinary handler on the root logger. The contract
is unchanged (settings-coverage REQ-015 / AC-020, main-ci-green item E): a
settings-driven reconfigure must touch ONLY the handlers the logging feature owns —
it must leave a foreign handler installed and still receiving records, must keep
exactly one console + one file sink, and must re-establish a managed sink that
someone else removed without raising on the event bus worker.

The reconfiguration is driven through the public path (a ``logging.*`` write on the
shared registry) and observed by the console handler's level changing to the written
value — a signal specific to this test's write, so a queued reconfigure from another
test can never satisfy it. Delivery is awaited with ``settings_test_helpers.wait_for``,
never a sleep.
"""

from __future__ import annotations

import contextlib
import logging
import logging.handlers
from collections.abc import Callable, Iterator

import pytest
from logging_test_helpers import managed_handlers, managed_sinks, pipeline_logger, rotating_file_handlers
from settings_test_helpers import wait_for

from backend.logging import register_settings
from backend.settings import get_settings_registry

_MANAGED_HANDLER_COUNT = 2  # REQ-002: one console handler + one queue handler


class _CaptureHandler(logging.Handler):
    """A third-party handler, added exactly the way another component would add one."""

    def __init__(self) -> None:
        super().__init__(level=logging.DEBUG)
        self.records: list[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(record)

    def mentions(self, message: str) -> bool:
        """A record with ``message`` reached this handler."""
        return any(message in record.getMessage() for record in self.records)

    def error_messages(self) -> list[str]:
        """The ERROR-or-above records this handler received (a worker-thread failure lands here)."""
        return [record.getMessage() for record in self.records if record.levelno >= logging.ERROR]


def _feature_handlers() -> list[logging.Handler]:
    """The handlers the feature logger owns (empty while the pipeline is not installed)."""
    with contextlib.suppress(AssertionError):  # pipeline_logger() asserts when there is no pipeline
        return managed_handlers(pipeline_logger())
    return []


def _settled() -> bool:
    """The feature owns exactly its two managed handlers, and exactly one file handler exists."""
    return len(_feature_handlers()) == _MANAGED_HANDLER_COUNT and len(rotating_file_handlers()) == 1


def _console_levelno() -> int | None:
    """The console handler's level number, or None unless the managed sinks are in place."""
    with contextlib.suppress(AssertionError):
        console, _file_sink = managed_sinks()
        return int(console.level)
    return None


def _level_no(name: str) -> int:
    return int(logging.getLevelName(name))


def _reconfigure_applied(level_name: str) -> bool:
    """A reconfigure has landed: the managed sinks are intact and the console level is ``level_name``.

    The level check makes the signal specific to this test's write (a queued
    reconfigure from another test cannot satisfy it); the settled check covers the
    file sink, which a reconfigure re-points after the console handler.
    """
    return _settled() and _console_levelno() == _level_no(level_name)


@pytest.fixture(autouse=True)
def settled_sinks() -> None:
    """Start each test from the settled two-handler state (no reconfigure still in flight)."""
    assert wait_for(_settled), "the logging feature's managed sinks are not settled before the test"


@pytest.fixture
def capture_handler() -> Iterator[_CaptureHandler]:
    """A handler the logging feature does not own, installed on the root logger."""
    handler = _CaptureHandler()
    logging.getLogger().addHandler(handler)
    try:
        yield handler
    finally:
        # The defect under test may already have removed the handler.
        with contextlib.suppress(ValueError):
            logging.getLogger().removeHandler(handler)


@pytest.fixture
def logging_level_change() -> Iterator[Callable[[], str]]:
    """Trigger the runtime reconfiguration through the public path (AC-020).

    Writes a different ``logging.*`` level on the shared registry (the logging
    feature's ``SettingChanged`` subscription then reconfigures the handlers on the
    event bus worker) and returns the level written. The original level is restored,
    and its reconfigure is awaited, inside this fixture — so no reconfigure leaks
    into the next test.
    """
    registry = get_settings_registry()
    if not registry.has("logging.log_level"):
        register_settings(registry)
    original = str(registry.get_value("logging.log_level"))
    new = "INFO" if original != "INFO" else "DEBUG"

    def _change() -> str:
        registry.set_value("logging.log_level", new)
        return new

    yield _change

    registry.set_value("logging.log_level", original)
    wait_for(lambda: _reconfigure_applied(original))


def test_reconfigure_keeps_foreign_sink(
    capture_handler: _CaptureHandler,
    logging_level_change: Callable[[], str],
) -> None:
    """A handler the feature never created must still receive records after a reconfigure."""
    logging.getLogger("ownership_probe").warning("probe-before-reconfigure")
    assert capture_handler.mentions("probe-before-reconfigure"), "capture handler is not receiving records"

    new = logging_level_change()
    assert wait_for(lambda: _reconfigure_applied(new)), "reconfigure never applied"

    capture_handler.records.clear()
    logging.getLogger("ownership_probe").warning("probe-after-reconfigure")
    assert wait_for(lambda: capture_handler.mentions("probe-after-reconfigure")), (
        "the reconfigure removed a handler it does not own: records emitted after it are lost"
    )


def test_reconfigure_replaces_only_the_managed_sinks(
    capture_handler: _CaptureHandler,
    logging_level_change: Callable[[], str],
) -> None:
    """After a reconfigure: exactly one console + one file sink, plus the foreign handler."""
    new = logging_level_change()
    assert wait_for(lambda: _reconfigure_applied(new)), "reconfigure never applied"

    console, file_sink = managed_sinks()
    assert type(console) is logging.StreamHandler, "REQ-001/INV-001: exactly one console handler"
    assert isinstance(file_sink, logging.handlers.QueueHandler | logging.handlers.RotatingFileHandler), (
        "REQ-001/INV-001: exactly one file sink"
    )
    assert len(rotating_file_handlers()) == 1, "INV-001: a reconfigure must not grow a second file handler"
    assert capture_handler in logging.getLogger().handlers, "the reconfigure removed a handler it does not own"


def test_reconfigure_after_external_removal_of_a_managed_sink(
    capture_handler: _CaptureHandler,
    logging_level_change: Callable[[], str],
) -> None:
    """A managed handler removed by someone else must not break the next reconfigure."""
    console, _file_sink = managed_sinks()
    pipeline_logger().removeHandler(console)

    new = logging_level_change()
    assert wait_for(lambda: _reconfigure_applied(new)), (
        "reconfigure did not re-establish the managed handlers after an external removal"
    )

    assert len(rotating_file_handlers()) == 1, "REQ-001/INV-001: exactly one file sink"
    errors = capture_handler.error_messages()
    assert not errors, f"the reconfigure raised on the event bus worker: {errors[-1]}"
