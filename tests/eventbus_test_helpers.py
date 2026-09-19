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
    """Ensure the event-bus singleton is well-defined after the block.

    A test that calls ``reset_event_bus`` leaves the module singleton missing
    (the previous instance is shut down) — a state leak that changes what
    later tests observe (a ``SettingsRegistry`` built after the leak creates a
    fresh ``EventBus`` instead of reusing the singleton). On exit, if the slot
    is missing, a fresh singleton is installed so the suite state after the
    block is a well-defined singleton (no "missing" state leak). The block's
    own resets are untouched — only the post-block state is guaranteed.
    """
    from backend.eventbus import eventbus as _eventbus_module

    try:
        yield
    finally:
        if _eventbus_module._default_bus[0] is None:
            _eventbus_module.get_event_bus()
