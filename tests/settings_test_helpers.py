"""Shared helpers for the settings test suite.

Kept separate from tests/conftest.py so test modules can import the helpers
without going through pytest's conftest machinery. Mirrors the event-bus
helper pattern (async delivery is observed via ``wait_for``).
"""

from __future__ import annotations

import time
from collections.abc import Callable

from backend.eventbus import EventBus
from backend.settings import SettingsRegistry


def wait_for(predicate: Callable[[], bool], timeout: float = 5.0) -> bool:
    """Poll until ``predicate()`` returns true, or until ``timeout`` elapses.

    The event bus delivers asynchronously on a background worker, so event
    tests wait for observable effects (handler invocations) rather than
    assuming synchronous delivery.
    """
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return True
        time.sleep(0.005)
    return False


def make_registry(event_bus: EventBus | None = None) -> tuple[SettingsRegistry, EventBus]:
    """Build a registry wired to ``event_bus`` (or a fresh bus) for a test.

    Returns ``(registry, bus)``. The caller is responsible for shutting the
    bus down when it created the bus (or always, to be safe).
    """
    bus = event_bus if event_bus is not None else EventBus()
    registry = SettingsRegistry(event_bus=bus)
    return registry, bus


class EventCollector:
    """A synchronous event publisher for exact event counting in tests.

    Structurally satisfies the event publisher protocol (a ``publish`` method),
    so it can be injected as the registry's event bus. Events are recorded
    synchronously, making exact-count invariants (INV-008) deterministic.
    """

    def __init__(self) -> None:
        self.events: list[object] = []

    def publish(self, event: object) -> None:
        self.events.append(event)
