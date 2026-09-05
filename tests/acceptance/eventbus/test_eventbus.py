"""Acceptance tests for the event bus feature (docs/specs/event-bus.md).

These tests verify externally observable behavior only: non-blocking publish,
typed event dispatch, handler error isolation, thread safety, lifecycle, the
shared default instance, and bounded-queue backpressure.
"""

from __future__ import annotations

import threading
import time
from collections.abc import Iterator

import pytest

from backend.eventbus import EventBus, get_event_bus, reset_event_bus
from eventbus_test_helpers import BaseEvent, OrderPlaced, UserCreated, wait_for


@pytest.fixture
def bus() -> Iterator[EventBus]:
    """A fresh EventBus per test, shut down afterwards to clean the worker."""
    b = EventBus()
    yield b
    b.shutdown()


def test_ac_001_publish_non_blocking(bus: EventBus) -> None:
    """AC-001: publish() returns in < 10 ms and the handler runs on the worker."""
    done = threading.Event()

    def slow_handler(event: object) -> None:
        time.sleep(0.1)
        done.set()

    bus.subscribe(UserCreated, slow_handler)
    start = time.monotonic()
    bus.publish(UserCreated("u1", "e1"))
    elapsed = time.monotonic() - start
    assert elapsed < 0.01, f"publish() blocked for {elapsed:.3f}s"
    assert done.wait(timeout=5.0), "handler did not run on the background worker"


def test_ac_002_subscribe_matching_event(bus: EventBus) -> None:
    """AC-002: a handler registered for UserCreated receives UserCreated events."""
    received: list[object] = []
    bus.subscribe(UserCreated, lambda e: received.append(e))
    bus.publish(UserCreated("u1", "e1"))
    assert wait_for(lambda: len(received) == 1), "handler not called for matching event"
    assert isinstance(received[0], UserCreated)


def test_ac_003_no_match_different_type(bus: EventBus) -> None:
    """AC-003: a handler registered for UserCreated is NOT called for OrderPlaced."""
    received: list[object] = []
    bus.subscribe(UserCreated, lambda e: received.append(e))
    bus.publish(OrderPlaced("o1", "u1", 100))
    # Give the worker time; the handler must NOT be called.
    time.sleep(0.3)
    assert received == [], "handler called for a non-matching event type"


def test_ac_004_isinstance_matching(bus: EventBus) -> None:
    """AC-004: a handler registered for BaseEvent receives subclass events (isinstance)."""
    received: list[object] = []
    bus.subscribe(BaseEvent, lambda e: received.append(e))
    bus.publish(UserCreated("u1", "e1"))
    assert wait_for(lambda: len(received) == 1), "base-type handler not called for subclass event"


def test_ac_005_error_isolation(bus: EventBus) -> None:
    """AC-005: a non-raising handler runs even when another handler raises."""
    ok = threading.Event()

    def bad_handler(event: object) -> None:
        raise RuntimeError("boom")

    def good_handler(event: object) -> None:
        ok.set()

    # Register the bad handler first so it runs before the good one.
    bus.subscribe(UserCreated, bad_handler)
    bus.subscribe(UserCreated, good_handler)
    bus.publish(UserCreated("u1", "e1"))
    assert ok.wait(timeout=5.0), "non-raising handler did not run after a handler raised"


def test_ac_006_exception_no_propagate(bus: EventBus) -> None:
    """AC-006: a handler's exception never propagates to the publisher."""

    def bad_handler(event: object) -> None:
        raise RuntimeError("boom")

    bus.subscribe(UserCreated, bad_handler)
    # publish() must complete normally (no exception).
    bus.publish(UserCreated("u1", "e1"))
    # Allow the worker to process (and swallow) the exception.
    time.sleep(0.3)


def test_ac_007_thread_safe_publish(bus: EventBus) -> None:
    """AC-007: concurrent publish() from multiple threads loses no events."""
    count = 0
    lock = threading.Lock()

    def handler(event: object) -> None:
        nonlocal count
        with lock:
            count += 1

    bus.subscribe(UserCreated, handler)
    n_publishers = 8
    per_thread = 25
    total = n_publishers * per_thread
    errors: list[BaseException] = []

    def publisher() -> None:
        try:
            for i in range(per_thread):
                bus.publish(UserCreated(f"u{i}", "e"))
        except BaseException as e:  # pragma: no cover
            errors.append(e)

    threads = [threading.Thread(target=publisher) for _ in range(n_publishers)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert not errors, f"publisher threads raised: {errors}"
    assert wait_for(lambda: count == total, timeout=10.0), f"lost events: {count}/{total}"


def test_ac_008_shutdown_drains(bus: EventBus) -> None:
    """AC-008: shutdown() processes events enqueued before it; publish() after is a no-op."""
    count = 0
    lock = threading.Lock()

    def handler(event: object) -> None:
        nonlocal count
        with lock:
            count += 1

    bus.subscribe(UserCreated, handler)
    bus.publish(UserCreated("u1", "e1"))
    bus.publish(UserCreated("u2", "e2"))
    bus.shutdown()
    # Graceful drain: both events enqueued before shutdown are processed.
    assert wait_for(lambda: count == 2, timeout=10.0), "shutdown did not drain pending events"
    # publish() after shutdown is a no-op.
    bus.publish(UserCreated("u3", "e3"))
    time.sleep(0.3)
    assert count == 2, "publish() after shutdown should be a no-op"


def test_ac_009_shutdown_idempotent(bus: EventBus) -> None:
    """AC-009: calling shutdown() twice is a no-op (no error)."""
    bus.shutdown()
    bus.shutdown()  # must not raise


def test_ac_010_context_manager() -> None:
    """AC-010: using the bus as a context manager shuts it down on exit."""
    b = EventBus()
    with b:
        pass  # may be lazily started; the point is the context manager works
    assert not b.is_running, "context manager did not shut the bus down on exit"


def test_ac_011_singleton() -> None:
    """AC-011: get_event_bus() returns the same instance (singleton)."""
    reset_event_bus()
    try:
        a = get_event_bus()
        b = get_event_bus()
        assert a is b, "get_event_bus() did not return a singleton"
    finally:
        reset_event_bus()


def test_ac_012_bounded_queue_drop() -> None:
    """AC-012: the queue never exceeds max_queue_size; excess events are dropped."""
    b = EventBus(max_queue_size=3)
    try:
        def slow_handler(event: object) -> None:
            time.sleep(0.05)  # keep the worker busy so the queue fills

        b.subscribe(UserCreated, slow_handler)
        # Publish a burst faster than the worker can drain.
        for i in range(50):
            b.publish(UserCreated(f"u{i}", "e"))
        # The queue is bounded; some events must have been dropped.
        assert wait_for(lambda: b.dropped_count > 0, timeout=10.0), "no events dropped under backpressure"
        # The queue size never exceeds max_queue_size.
        assert b.pending_count <= 3, f"queue exceeded max_queue_size: {b.pending_count}"
    finally:
        b.shutdown()
