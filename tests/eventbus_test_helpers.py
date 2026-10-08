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

    The scratch install and the restore go through the feature's public install
    operation (``set_event_bus``) — never a write to the private slot (settings
    REQ-012 / AC-017); ``set_event_bus`` is lifecycle-neutral (EDGE-011), so the
    parking semantics above are unchanged.
    """
    from backend.eventbus import EventBus, get_event_bus, reset_event_bus, set_event_bus
    from backend.eventbus import eventbus as _eventbus_module

    saved = _eventbus_module._default_bus[0]
    set_event_bus(EventBus())
    try:
        yield
    finally:
        scratch = _eventbus_module._default_bus[0]
        if scratch is not None and scratch is not saved:
            scratch.shutdown()
        if saved is not None:
            set_event_bus(saved)
        else:
            # REQ-004: the install operation never accepts None, so an empty restore
            # goes through the feature's reset (idempotent here: the scratch bus was
            # just shut down), and get_event_bus() then keeps the slot non-empty.
            reset_event_bus()
            get_event_bus()
