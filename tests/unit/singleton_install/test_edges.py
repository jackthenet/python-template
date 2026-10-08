"""Unit tests for the edge cases of the shared install operation (EDGE-001 … EDGE-007).

Normative source: ``docs/specs/settings-public-registry-setter.md`` EDGE-001…EDGE-007
(change-level IDs — PROBLEMS.md P-53), plus the feature specs cited per test
(``docs/specs/session-management.md``, ``docs/specs/settings-coverage.md``,
``docs/specs/event-bus.md``).

The install operation is reached through the shared slot table
(``tests/singleton_install_test_helpers.py``) with ``getattr`` at call time, so a
missing installer fails inside the test body instead of at collection.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
from pathlib import Path
from typing import Any

import pytest
from eventbus_test_helpers import isolated_event_bus, wait_for
from singleton_install_test_helpers import (
    EVENTBUS_SLOT,
    SESSIONMANAGEMENT_SLOT,
    SETTINGS_SLOT,
    SLOTS,
    non_tracing_warnings,
)

from backend.settings import get_settings_registry

# tests/unit/singleton_install/test_edges.py -> the worktree root. Paths are resolved
# absolutely, never from CWD (findings F-41 / PROBLEMS.md P-57).
_REPO_ROOT = Path(__file__).resolve().parents[3]


class _Sentinel:
    """A private event type for the bus witnesses (any class is a valid event, event-bus.md)."""


def _bus_workers() -> int:
    """How many event-bus worker threads are alive (``EventBus`` names its worker)."""
    return sum(1 for thread in threading.enumerate() if thread.name == "eventbus-worker")


def test_edge_001_install_over_nonempty(log_records: list[Any]) -> None:
    """EDGE-001: installing over a non-empty slot raises nothing, logs exactly one WARNING, and leaves the replaced instance usable."""
    with isolated_event_bus():  # these installs replace the slot's bus; park the suite's live bus
        for slot in SLOTS:
            slot.clear()
            replaced, probe = slot.stamp()
            replacement = slot.new()
            try:
                slot.install(replaced)  # the slot is now non-empty
                log_records.clear()
                slot.install(replacement)  # EDGE-001: no exception on the replacing path
                warnings = non_tracing_warnings(log_records)
                assert len(warnings) == 1, f"{slot.name()}: replacing a held instance logged {warnings!r}"
                assert slot.read() is replacement, f"{slot.name()}: the slot does not hold the replacement"
                assert probe(replaced), (
                    f"{slot.name()}: the install cleared or closed the instance it replaced "
                    "(the caller still holds it — change AC-005)"
                )
            finally:
                slot.dispose(replaced)
                slot.dispose(replacement)
                slot.clear()


def test_edge_002_same_instance_twice(log_records: list[Any]) -> None:
    """EDGE-002: installing the same instance twice logs a WARNING the second time (the slot was non-empty) and the slot holds it."""
    with isolated_event_bus():
        for slot in SLOTS:
            slot.clear()
            instance = slot.new()
            try:
                slot.install(instance)
                log_records.clear()
                slot.install(instance)  # the slot was non-empty, even though the instance is the same
                warnings = non_tracing_warnings(log_records)
                assert len(warnings) == 1, f"{slot.name()}: re-installing the same instance logged {warnings!r}"
                assert slot.read() is instance, f"{slot.name()}: the slot no longer holds the instance"
            finally:
                slot.dispose(instance)
                slot.clear()


def test_edge_003_session_service_repository_rule() -> None:
    """EDGE-003 (session-management.md AC-042): the no-repository read still raises ValueError, and after an install it returns the installed instance."""
    SESSIONMANAGEMENT_SLOT.clear()
    with pytest.raises(ValueError):
        SESSIONMANAGEMENT_SLOT.read()  # no lazily created default without a repository

    service = SESSIONMANAGEMENT_SLOT.new()  # the factory supplies the repository EDGE-003 requires
    try:
        SESSIONMANAGEMENT_SLOT.install(service)
        assert SESSIONMANAGEMENT_SLOT.read() is service, (
            "EDGE-003: after set_session_service() the no-repository read must return the installed instance"
        )
    finally:
        SESSIONMANAGEMENT_SLOT.clear()

    with pytest.raises(ValueError):
        SESSIONMANAGEMENT_SLOT.read()  # the install did not weaken the repository rule


def test_edge_004_required_false_after_install_and_reset() -> None:
    """EDGE-004 (settings-coverage.md REQ-012 / EDGE-011 preserved): required=False sees the installed instance, and None after a reset."""
    SETTINGS_SLOT.clear()
    assert get_settings_registry(required=False) is None, "the settings slot is not empty at the start of the witness"

    registry = SETTINGS_SLOT.new()
    try:
        SETTINGS_SLOT.install(registry)
        assert get_settings_registry(required=False) is registry, (
            "EDGE-004: required=False does not return the installed registry"
        )
    finally:
        SETTINGS_SLOT.clear()

    assert get_settings_registry(required=False) is None, "EDGE-004: required=False created a registry after the reset"
    assert get_settings_registry(required=False) is None, "EDGE-004: the second required=False read created a registry"


_CHILD = """
import json
import logging

import backend.settings as settings_api

_levels: list[str] = []


class _Capture(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        _levels.append(record.levelname)


# ADR-082: the pipeline is stdlib handlers, and one dedicated non-propagating logger
# (``backend.logging``) owns the managed sinks. A stdlib capture handler on that
# logger IS this child process's own sink — the EDGE-005 clause under test.
_pipeline = logging.getLogger("backend.logging")
_pipeline.addHandler(_Capture(level=logging.DEBUG))
_pipeline.setLevel(logging.DEBUG)

settings_api.reset_settings_registry()
first = settings_api.get_settings_registry()
settings_api.reset_settings_registry()
second = settings_api.get_settings_registry()
settings_api.set_settings_registry(first)  # non-empty slot: exactly one WARNING, in THIS process
after = settings_api.get_settings_registry()

print(
    json.dumps(
        {
            "read_is_installed": after is first,
            "read_is_not_previous_default": after is not second,
            "warnings": _levels.count("WARNING"),
        }
    )
)
"""


def test_edge_005_install_in_subprocess(tmp_path: Path) -> None:
    """EDGE-005: the install has identical semantics in a fresh interpreter, and its WARNING goes to that process's own sink."""
    script = tmp_path / "install_in_child.py"
    script.write_text(_CHILD, encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(script)],
        cwd=tmp_path,  # the composition root writes ./data and ./settings relative to CWD
        env={**os.environ, "PYTHONPATH": str(_REPO_ROOT / "src")},
        capture_output=True,
        text=True,
        timeout=120,
        check=False,  # the returncode assertion below is the witness (findings F-41): a raised CalledProcessError would hide which side failed
    )
    assert result.returncode == 0, f"the child process did not run: {result.stderr[-2000:]}"

    payload = json.loads(result.stdout.splitlines()[-1])
    assert payload["read_is_installed"], "EDGE-005: a later read in the fresh interpreter is not the installed instance"
    assert payload["read_is_not_previous_default"], (
        "EDGE-005: the install did not replace the fresh interpreter's default"
    )
    assert payload["warnings"] == 1, f"EDGE-005: the child's sink logged {payload['warnings']!r} WARNING records"


def test_edge_006_live_bus_not_shut_down() -> None:
    """EDGE-006 (event-bus.md REQ-005): installing over a live bus leaves it dispatching; the installed bus starts only on its first publish()."""
    with isolated_event_bus():
        replaced, probe = EVENTBUS_SLOT.stamp()
        EVENTBUS_SLOT.install(replaced)
        assert probe(replaced), "the stamped bus's worker is not running before the install — the witness is vacuous"
        workers_before = _bus_workers()

        installed = EVENTBUS_SLOT.new()
        received: list[object] = []
        installed.subscribe(_Sentinel, received.append)
        try:
            EVENTBUS_SLOT.install(installed)
            assert EVENTBUS_SLOT.read() is installed, "the installed bus is not the shared default"
            assert _bus_workers() == workers_before, (
                "EDGE-006: the install started the installed bus's worker (it must start on its first publish)"
            )
            assert probe(replaced), "EDGE-006: the install shut the replaced bus down; only its owner may shut it down"
            installed.publish(_Sentinel())
            assert wait_for(lambda: bool(received), timeout=1.0), (
                "EDGE-006: the installed bus does not dispatch on its first publish()"
            )
        finally:
            EVENTBUS_SLOT.dispose(replaced)
            EVENTBUS_SLOT.dispose(installed)
            EVENTBUS_SLOT.clear()


def test_edge_007_reset_event_bus_still_shuts_down(log_records: list[Any]) -> None:
    """EDGE-007 (event-bus.md REQ-005): reset_event_bus() still shuts the instance down; the WARNING rule applies to install only."""
    with isolated_event_bus():
        EVENTBUS_SLOT.clear()
        log_records.clear()  # only this test's installs may count (the helper's scratch install/restore warned)
        replaced = EVENTBUS_SLOT.new()
        EVENTBUS_SLOT.install(replaced)  # empty slot: no WARNING (AC-004)
        installed = EVENTBUS_SLOT.new()
        EVENTBUS_SLOT.install(installed)  # non-empty slot: exactly one WARNING (AC-003) — the rule is about install
        assert len(non_tracing_warnings(log_records)) == 1, (
            "EDGE-007: installing over a held bus did not warn, so the reset contrast below is vacuous"
        )

        received: list[object] = []
        installed.subscribe(_Sentinel, received.append)
        installed.publish(_Sentinel())
        assert wait_for(lambda: bool(received), timeout=1.0), "the installed bus is not dispatching before the reset"
        received.clear()
        log_records.clear()

        try:
            EVENTBUS_SLOT.clear()  # reset_event_bus()

            warnings = non_tracing_warnings(log_records)
            assert not warnings, f"EDGE-007: reset_event_bus() logged a replace WARNING: {warnings!r}"
            installed.publish(_Sentinel())
            assert not wait_for(lambda: bool(received), timeout=0.2), (
                "EDGE-007: reset_event_bus() left the instance dispatching (event-bus.md REQ-005)"
            )
            assert EVENTBUS_SLOT.read() is not installed, "EDGE-007: the reset did not clear the slot"
        finally:
            EVENTBUS_SLOT.dispose(replaced)
            EVENTBUS_SLOT.dispose(installed)
            EVENTBUS_SLOT.clear()
