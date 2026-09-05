"""Contract tests for the event bus feature (docs/specs/event-bus.md).

Covers the spec's NFRs: non-blocking publish budget, handler-failure
isolation, single worker + bounded queue, and backward-compatible API.
"""

from __future__ import annotations

import threading
import time

from eventbus_test_helpers import OrderPlaced, UserCreated

from backend.eventbus import EventBus, get_event_bus, reset_event_bus

_PUBLISH_BUDGET_S = 0.001
_MAX_QUEUE_SIZE = 5


def test_nfr_001_publish_non_blocking_budget() -> None:
    """NFR-001: publish() returns in < 1 ms (median) under normal load."""
    bus = EventBus()
    try:
        bus.subscribe(UserCreated, lambda e: None)  # fast handler: queue drains
        # Warm up (the first publish starts the worker thread).
        for _ in range(10):
            bus.publish(UserCreated("u", "e"))
        samples: list[float] = []
        for _ in range(100):
            start = time.monotonic()
            bus.publish(UserCreated("u", "e"))
            samples.append(time.monotonic() - start)
        samples.sort()
        median = samples[len(samples) // 2]
        assert median < _PUBLISH_BUDGET_S, f"publish() median {median * 1000:.3f} ms exceeds 1 ms budget"
    finally:
        bus.shutdown()


def test_nfr_002_handler_failure_isolation() -> None:
    """NFR-002: a handler failure never prevents other handlers and never crashes the worker."""
    bus = EventBus()
    ok = threading.Event()

    def bad_handler(event: object) -> None:
        raise RuntimeError("boom")

    def good_handler(event: object) -> None:
        ok.set()

    bus.subscribe(UserCreated, bad_handler)
    bus.subscribe(UserCreated, good_handler)
    # Publish multiple events; the worker must survive all the failures.
    for _ in range(5):
        bus.publish(UserCreated("u", "e"))
    assert ok.wait(timeout=5.0), "other handler not invoked (worker crashed or isolation failed)"
    # The worker is still alive: another event type is processed.
    alive = threading.Event()
    bus.subscribe(OrderPlaced, lambda e: alive.set())
    bus.publish(OrderPlaced("o", "u", 1))
    assert alive.wait(timeout=5.0), "worker did not survive handler failures"
    bus.shutdown()


def test_nfr_003_single_worker_bounded_queue() -> None:
    """NFR-003: the bus uses exactly one background worker thread and a bounded queue."""
    bus = EventBus(max_queue_size=5)
    try:
        active = 0
        max_active = 0
        lock = threading.Lock()

        def handler(event: object) -> None:
            nonlocal active, max_active
            with lock:
                active += 1
                max_active = max(max_active, active)
            time.sleep(0.01)
            with lock:
                active -= 1

        bus.subscribe(UserCreated, handler)
        for _ in range(20):
            bus.publish(UserCreated("u", "e"))
        bus.shutdown()
        # Single worker: handlers never run concurrently.
        assert max_active == 1, f"handlers ran concurrently (max_active={max_active}); expected single worker"
        # Bounded queue.
        assert bus.pending_count <= _MAX_QUEUE_SIZE, f"queue exceeded max_queue_size: {bus.pending_count}"
    finally:
        bus.shutdown()


def test_nfr_004_api_backward_compatible() -> None:
    """NFR-004: the public API (EventBus, get_event_bus, reset_event_bus) is backward-compatible."""
    bus = EventBus()  # default max_queue_size
    try:
        # The documented methods exist.
        assert callable(bus.subscribe)
        assert callable(bus.unsubscribe)
        assert callable(bus.publish)
        assert callable(bus.start)
        assert callable(bus.shutdown)
        # The documented properties exist with the right types.
        assert isinstance(bus.is_running, bool)
        assert isinstance(bus.pending_count, int)
        assert isinstance(bus.dropped_count, int)
    finally:
        bus.shutdown()
    # get_event_bus / reset_event_bus exist and work.
    reset_event_bus()
    try:
        a = get_event_bus()
        b = get_event_bus()
        assert a is b
    finally:
        reset_event_bus()
