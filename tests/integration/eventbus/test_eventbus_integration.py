"""Integration tests for the event bus feature (docs/specs/event-bus.md).

Covers multi-component interactions: multiple features communicating via the
shared bus without importing each other.
"""

from __future__ import annotations

import threading

from backend.eventbus import get_event_bus, reset_event_bus
from eventbus_test_helpers import UserCreated, wait_for


def test_multi_feature_publish_subscribe() -> None:
    """Multiple features communicate via the shared bus without importing each other."""
    reset_event_bus()
    try:
        bus = get_event_bus()
        received: list[object] = []
        lock = threading.Lock()

        def handler(event: object) -> None:
            with lock:
                received.append(event)

        # Feature A publishes; feature B subscribes (no direct import between them).
        bus.subscribe(UserCreated, handler)
        bus.publish(UserCreated("u1", "e1"))
        assert wait_for(lambda: len(received) == 1, timeout=5.0), "event not delivered across features"
    finally:
        reset_event_bus()
