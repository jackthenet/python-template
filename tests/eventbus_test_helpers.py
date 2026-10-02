"""Shared helpers for the event bus test suite.

Kept separate from tests/conftest.py (which holds fixtures) so test modules
can import the helpers without going through pytest's conftest machinery.
"""

from __future__ import annotations

import time
from collections.abc import Callable, Iterator
from contextlib import contextmanager


class BaseEvent:
    """Base event class used for isinstance-matching tests."""


class UserCreated(BaseEvent):
    """A sample event (subclass of BaseEvent)."""

    def __init__(self, user_id: str, email: str) -> None:
        self.user_id = user_id
        self.email = email


class OrderPlaced(BaseEvent):
    """A second sample event (subclass of BaseEvent)."""

    def __init__(self, order_id: str, user_id: str, total_cents: int) -> None:
        self.order_id = order_id
        self.user_id = user_id
        self.total_cents = total_cents


def wait_for(predicate: Callable[[], bool], timeout: float = 5.0) -> bool:
    """Poll until ``predicate()`` returns true, or until ``timeout`` elapses.

    The event bus delivers asynchronously on a background worker, so tests wait
    for observable effects (handler invocations) rather than assuming
    synchronous delivery.
    """
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return True
        time.sleep(0.01)
    return False


@contextmanager
def isolated_event_bus() -> Iterator[None]:
    """Park the real shared bus, run the block on a scratch bus, then put it back.

    ``reset_event_bus()`` SHUTS DOWN the instance it resets — a later
    ``publish()`` on a shut-down bus is a silent no-op. A test that resets the
    real shared instance therefore permanently disconnects every long-lived
    holder of that instance: the settings registry built earlier publishes its
    ``SettingChanged`` events on the dead bus, and the logging feature's
    AC-020 ``SettingChanged`` subscription lives on that same bus. Every later
    ``logging.*`` write is then published into the dead bus and never
    dispatches, so the sink reconfiguration never happens and the logging
    sink-ownership tests time out (main-ci-green item H: the whole suite's
    bus wiring dies after the first test that resets the shared instance).

    The real instance is therefore only PARKED for the duration of the block:
    a scratch instance is installed in the slot, the block's own resets act on
    the scratch, and on exit the scratch is shut down and the parked instance
    is restored — so the suite state after the block is exactly the state
    before it (same live singleton instance, same subscribers). The block still
    sees a fresh, handler-free bus: the scratch instance has no subscribers of
    its own, and callers that reset the slot first get a brand-new one.
    """
    from backend.eventbus import eventbus as _eventbus_module
    from backend.eventbus.eventbus import EventBus

    saved = _eventbus_module._default_bus[0]
    _eventbus_module._default_bus[0] = EventBus()
    try:
        yield
    finally:
        scratch = _eventbus_module._default_bus[0]
        if scratch is not None and scratch is not saved:
            scratch.shutdown()
        _eventbus_module._default_bus[0] = saved
        if _eventbus_module._default_bus[0] is None:
            _eventbus_module.get_event_bus()
