"""Loguru sink-ownership tests for the logging feature (docs/specs/logging.md).

Reproduction tests for main-ci-green item E: ``_configure()`` opens with a
blanket ``logger.remove()``, so a settings-driven reconfigure
(settings-coverage REQ-015 / AC-020) removes every loguru handler in the
process — including sinks the logging feature never created (the
``tests/conftest.py::log_records`` capture sink, and any other component's).
The feature must remove only the sinks it added, while keeping the two
configured sinks it owns (logging REQ-001 / AC-001 / INV-001).

The reconfiguration is driven through the public path (a ``logging.*`` write on
the shared registry) and observed by the console sink's level changing to the
written value — a signal specific to this test's write, so a queued reconfigure
from another test can never satisfy it. Delivery is awaited with
``settings_test_helpers.wait_for``, never a sleep.
"""

from __future__ import annotations

import contextlib
import logging as std_logging
from collections.abc import Callable, Iterator
from typing import Any

import pytest
from loguru import logger
from settings_test_helpers import wait_for

from backend.logging import register_settings
from backend.settings import get_settings_registry

_CONSOLE_SINK = "StreamSink"  # loguru's sink class for a standard-stream sink
_FILE_SINK = "FileSink"  # loguru's sink class for a path sink


def _handlers() -> dict[int, Any]:
    """Every loguru handler currently installed in the process (loguru has no public API)."""
    return logger._core.handlers


def _sink_ids_of(sink_class: str) -> list[int]:
    """The handler ids whose sink is an instance of ``sink_class``."""
    return [handler_id for handler_id, handler in _handlers().items() if type(handler._sink).__name__ == sink_class]


def _console_levelno() -> int | None:
    """The console sink's level number, or None unless there is exactly one console sink."""
    ids = _sink_ids_of(_CONSOLE_SINK)
    if len(ids) != 1:
        return None
    return int(_handlers()[ids[0]]._levelno)


def _settled() -> bool:
    """The logging feature's own sink set is exactly one console + one file sink."""
    return len(_sink_ids_of(_CONSOLE_SINK)) == 1 and len(_sink_ids_of(_FILE_SINK)) == 1


def _level_no(name: str) -> int:
    return int(std_logging.getLevelName(name))


def _reconfigure_applied(level_name: str) -> bool:
    """A reconfigure has landed: the two managed sinks exist and the console level is ``level_name``.

    The level check makes the signal specific to this test's write (a queued
    reconfigure from another test cannot satisfy it); the settled check covers
    the file sink, which ``_configure()`` adds after the console sink.
    """
    return _settled() and _console_levelno() == _level_no(level_name)


def _captured(records: list[dict[str, Any]], message: str) -> bool:
    return any(message in str(record["message"]) for record in records)


@pytest.fixture(autouse=True)
def settled_sinks() -> None:
    """Start each test from the settled two-sink state (no reconfigure still in flight)."""
    assert wait_for(_settled), "the logging feature's sinks are not settled before the test"


@pytest.fixture
def capture_sink() -> Iterator[tuple[list[dict[str, Any]], int]]:
    """A third-party sink, added exactly the way the ``log_records`` fixture adds one.

    Yields ``(records, handler_id)`` — the captured records and the id of the
    sink the logging feature does not own.
    """
    records: list[dict[str, Any]] = []

    def _sink(message: Any) -> None:
        records.append(message.record)

    handler_id = logger.add(_sink, level="DEBUG", catch=False)
    try:
        yield records, handler_id
    finally:
        # The defect under test may already have removed the sink.
        with contextlib.suppress(ValueError):
            logger.remove(handler_id)


@pytest.fixture
def logging_level_change() -> Iterator[Callable[[], str]]:
    """Trigger the runtime reconfiguration through the public path (AC-020).

    Writes a different ``logging.*`` level on the shared registry (the logging
    feature's ``SettingChanged`` subscription then reconfigures the sink on the
    event bus worker) and returns the level written. The original level is
    restored, and its reconfigure is awaited, inside this fixture — so no
    reconfigure leaks into the next test.
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
    capture_sink: tuple[list[dict[str, Any]], int],
    logging_level_change: Callable[[], str],
) -> None:
    """A sink the feature never created must still receive records after a reconfigure."""
    records, _handler_id = capture_sink
    logger.info("probe-before-reconfigure")
    assert _captured(records, "probe-before-reconfigure"), "capture sink is not receiving records"

    new = logging_level_change()
    assert wait_for(lambda: _reconfigure_applied(new)), "reconfigure never applied"

    records.clear()
    logger.info("probe-after-reconfigure")
    assert wait_for(lambda: _captured(records, "probe-after-reconfigure")), (
        "the reconfigure removed a sink it does not own: records emitted after it are lost"
    )


def test_reconfigure_replaces_only_the_managed_sinks(
    capture_sink: tuple[list[dict[str, Any]], int],
    logging_level_change: Callable[[], str],
) -> None:
    """After a reconfigure: exactly one console + one file sink, plus the foreign sink."""
    _records, handler_id = capture_sink

    new = logging_level_change()
    assert wait_for(lambda: _reconfigure_applied(new)), "reconfigure never applied"

    assert len(_sink_ids_of(_CONSOLE_SINK)) == 1, "REQ-001/INV-001: exactly one console sink"
    assert len(_sink_ids_of(_FILE_SINK)) == 1, "REQ-001/INV-001: exactly one file sink"
    assert handler_id in _handlers(), "the reconfigure removed a sink it does not own"


def test_reconfigure_after_external_removal_of_a_managed_sink(
    capture_sink: tuple[list[dict[str, Any]], int],
    logging_level_change: Callable[[], str],
) -> None:
    """A managed sink removed by someone else must not break the next reconfigure."""
    records, _handler_id = capture_sink
    logger.remove(_sink_ids_of(_CONSOLE_SINK)[0])

    new = logging_level_change()
    assert wait_for(lambda: _reconfigure_applied(new)), (
        "reconfigure did not re-establish the managed sinks after an external removal"
    )

    assert len(_sink_ids_of(_FILE_SINK)) == 1, "REQ-001/INV-001: exactly one file sink"
    errors = [record for record in records if record["level"].name == "ERROR"]
    assert not errors, f"the reconfigure raised on the event bus worker: {errors[-1]['message']}"
