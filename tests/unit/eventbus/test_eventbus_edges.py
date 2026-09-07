"""Unit tests for the event bus feature (docs/specs/event-bus.md).

Covers the spec's edge cases: lazy start, drop-on-full, non-callable handler,
non-class event type, unsubscribe no-op, dedup, publish-after-shutdown,
handler raising, start idempotent, and no registered handlers.
"""

from __future__ import annotations

import threading
import time

import pytest
from eventbus_test_helpers import UserCreated, wait_for

from backend.eventbus import EventBus


def test_edge_001_lazy_start() -> None:
    """EDGE-001: the worker starts lazily on the first publish()."""
    bus = EventBus()
    called = threading.Event()
    bus.subscribe(UserCreated, lambda e: called.set())
    bus.publish(UserCreated("u", "e"))
    assert called.wait(timeout=5.0), "event not processed (worker did not start lazily)"
    bus.shutdown()


def test_edge_002_drop_on_full() -> None:
    """EDGE-002: when the queue is full, the event is dropped and counted; publish() doesn't block."""
    bus = EventBus(max_queue_size=2)
    try:

        def slow_handler(event: object) -> None:
            time.sleep(0.05)  # keep the worker busy so the queue fills

        bus.subscribe(UserCreated, slow_handler)
        for _ in range(20):
            bus.publish(UserCreated("u", "e"))
        assert wait_for(lambda: bus.dropped_count > 0, timeout=10.0), "no drops under backpressure"
    finally:
        bus.shutdown()


def test_edge_003_non_callable_handler() -> None:
    """EDGE-003: subscribe() with a non-callable handler raises TypeError."""
    bus = EventBus()
    try:
        with pytest.raises(TypeError):
            bus.subscribe(UserCreated, 12345)  # type: ignore[arg-type]
    finally:
        bus.shutdown()


def test_edge_004_non_class_event() -> None:
    """EDGE-004: subscribe() with a non-class event type raises TypeError."""
    bus = EventBus()
    try:
        with pytest.raises(TypeError):
            bus.subscribe("not-a-class", lambda e: None)  # type: ignore[arg-type]
    finally:
        bus.shutdown()


def test_edge_005_unsubscribe_not_subscribed() -> None:
    """EDGE-005: unsubscribe() for a handler that is not subscribed is a no-op."""
    bus = EventBus()
    try:

        def handler(event: object) -> None:
            pass

        bus.unsubscribe(UserCreated, handler)  # not subscribed; must be a no-op
    finally:
        bus.shutdown()


def test_edge_006_dedup() -> None:
    """EDGE-006: subscribing the same handler twice registers it once (invoked once per event)."""
    bus = EventBus()
    count = 0
    lock = threading.Lock()

    def handler(event: object) -> None:
        nonlocal count
        with lock:
            count += 1

    bus.subscribe(UserCreated, handler)
    bus.subscribe(UserCreated, handler)  # dedup: still registered once
    bus.publish(UserCreated("u", "e"))
    assert wait_for(lambda: count >= 1, timeout=5.0), "handler not invoked"
    time.sleep(0.3)  # allow a second (dedup-failing) invocation to occur
    bus.shutdown()
    assert count == 1, f"handler invoked {count} times, expected 1 (dedup)"


def test_edge_007_publish_after_shutdown() -> None:
    """EDGE-007: publish() after shutdown() is a no-op."""
    bus = EventBus()
    count = 0
    lock = threading.Lock()

    def handler(event: object) -> None:
        nonlocal count
        with lock:
            count += 1

    bus.subscribe(UserCreated, handler)
    bus.shutdown()
    bus.publish(UserCreated("u", "e"))  # no-op
    time.sleep(0.3)
    assert count == 0, "publish() after shutdown should be a no-op"


def test_edge_008_handler_raises() -> None:
    """EDGE-008: a raising handler is caught and logged; other handlers continue."""
    bus = EventBus()
    ok = threading.Event()

    def bad_handler(event: object) -> None:
        raise ValueError("boom")

    def good_handler(event: object) -> None:
        ok.set()

    bus.subscribe(UserCreated, bad_handler)
    bus.subscribe(UserCreated, good_handler)
    bus.publish(UserCreated("u", "e"))  # must not raise
    assert ok.wait(timeout=5.0), "other handler did not continue after a raising handler"
    bus.shutdown()


def test_edge_009_start_idempotent() -> None:
    """EDGE-009: start() when the worker is already running is a no-op."""
    bus = EventBus()
    try:
        bus.start()
        bus.start()  # must not raise
        assert bus.is_running
    finally:
        bus.shutdown()


def test_edge_010_no_handlers() -> None:
    """EDGE-010: publish() with no registered handlers is a no-op (no error)."""
    bus = EventBus()
    try:
        bus.publish(UserCreated("u", "e"))  # no handlers for UserCreated
        time.sleep(0.3)  # allow the worker to process
    finally:
        bus.shutdown()
