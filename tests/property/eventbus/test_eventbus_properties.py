"""Property tests for the event bus feature (docs/specs/event-bus.md).

Covers the spec's invariants with Hypothesis: exactly-once dispatch, handler
isolation, bounded queue, and subscription-order dispatch.
"""

from __future__ import annotations

import threading
import time

from hypothesis import given
from hypothesis import strategies as st

from backend.eventbus import EventBus
from eventbus_test_helpers import UserCreated, wait_for


def test_inv_001_exactly_once() -> None:
    """INV-001: each non-dropped event is dispatched to each matching handler exactly once."""

    @given(st.integers(min_value=1, max_value=20))
    def inner(n: int) -> None:
        bus = EventBus()
        count = 0
        lock = threading.Lock()

        def handler(event: object) -> None:
            nonlocal count
            with lock:
                count += 1

        bus.subscribe(UserCreated, handler)
        for _ in range(n):
            bus.publish(UserCreated("u", "e"))
        bus.shutdown()
        assert wait_for(lambda: count == n, timeout=10.0), f"expected {n} invocations, got {count}"

    inner()


def test_inv_002_isolation() -> None:
    """INV-002: a raising handler does not prevent other handlers for the same event."""

    @given(st.integers(min_value=1, max_value=3))
    def inner(n: int) -> None:
        bus = EventBus()
        called = threading.Event()

        def bad_handler(event: object) -> None:
            raise RuntimeError("boom")

        def good_handler(event: object) -> None:
            called.set()

        bus.subscribe(UserCreated, bad_handler)
        bus.subscribe(UserCreated, good_handler)
        for _ in range(n):
            bus.publish(UserCreated("u", "e"))
        bus.shutdown()
        assert called.wait(timeout=5.0), "good handler not invoked despite a raising handler"

    inner()


def test_inv_003_queue_bounded() -> None:
    """INV-003: the queue size never exceeds max_queue_size under concurrent publish."""

    @given(st.integers(min_value=1, max_value=8))
    def inner(n_threads: int) -> None:
        bus = EventBus(max_queue_size=10)

        def handler(event: object) -> None:
            time.sleep(0.01)  # keep the worker busy so the queue fills

        bus.subscribe(UserCreated, handler)

        def publisher() -> None:
            for _ in range(20):
                bus.publish(UserCreated("u", "e"))
                assert bus.pending_count <= 10, f"queue exceeded max: {bus.pending_count}"

        threads = [threading.Thread(target=publisher) for _ in range(n_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        bus.shutdown()

    inner()


def test_inv_004_handler_order() -> None:
    """INV-004: handlers for a single event are invoked in subscription order."""

    @given(st.integers(min_value=2, max_value=6))
    def inner(n: int) -> None:
        bus = EventBus()
        order: list[int] = []
        lock = threading.Lock()

        def make_handler(idx: int):
            def handler(event: object) -> None:
                with lock:
                    order.append(idx)

            return handler

        for i in range(n):
            bus.subscribe(UserCreated, make_handler(i))
        bus.publish(UserCreated("u", "e"))
        bus.shutdown()
        assert wait_for(lambda: len(order) == n, timeout=5.0), f"not all handlers invoked: {order}"
        assert order == list(range(n)), f"handlers not in subscription order: {order}"

    inner()
