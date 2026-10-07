"""Acceptance tests for the event bus feature (docs/specs/event-bus.md).

These tests verify externally observable behavior only: non-blocking publish,
typed event dispatch, handler error isolation, thread safety, lifecycle, the
shared default instance, bounded-queue backpressure, and (event-bus.md v2) the
public install operation for the shared default.
"""

from __future__ import annotations

import threading
import time
from collections.abc import Callable, Iterator
from typing import Any

import pytest
from eventbus_test_helpers import BaseEvent, OrderPlaced, UserCreated, isolated_event_bus, wait_for
from singleton_install_test_helpers import (
    EVENTBUS_SLOT,
    concurrent_reads,
    non_tracing_warnings,
    widened_lazy_create_window,
)

from backend.eventbus import EventBus, get_event_bus, reset_event_bus

_PUBLISH_BUDGET_S = 0.01
_MAX_QUEUE_SIZE = 3
_MIN_DROPPED = 1
_DRAIN_COUNT = 2
_CONCURRENT_READERS = 8
_CONCURRENT_INSTALLS = 8
_CONCURRENT_RESETS = 2
_BARRIER_TIMEOUT = 5.0


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
    assert elapsed < _PUBLISH_BUDGET_S, f"publish() blocked for {elapsed:.3f}s"
    assert done.wait(timeout=5.0), "handler did not run on the background worker"


def test_ac_002_subscribe_matching_event(bus: EventBus) -> None:
    """AC-002: a handler registered for UserCreated receives UserCreated events."""
    received: list[object] = []

    def handler(event: object) -> None:
        received.append(event)

    bus.subscribe(UserCreated, handler)
    bus.publish(UserCreated("u1", "e1"))
    assert wait_for(lambda: len(received) == 1), "handler not called for matching event"
    assert isinstance(received[0], UserCreated)


def test_ac_003_no_match_different_type(bus: EventBus) -> None:
    """AC-003: a handler registered for UserCreated is NOT called for OrderPlaced."""
    received: list[object] = []

    def handler(event: object) -> None:
        received.append(event)

    bus.subscribe(UserCreated, handler)
    bus.publish(OrderPlaced("o1", "u1", 100))
    # Give the worker time; the handler must NOT be called.
    time.sleep(0.3)
    assert received == [], "handler called for a non-matching event type"


def test_ac_004_isinstance_matching(bus: EventBus) -> None:
    """AC-004: a handler registered for BaseEvent receives subclass events (isinstance)."""
    received: list[object] = []

    def handler(event: object) -> None:
        received.append(event)

    bus.subscribe(BaseEvent, handler)
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
    assert wait_for(lambda: count == _DRAIN_COUNT, timeout=10.0), "shutdown did not drain pending events"
    # publish() after shutdown is a no-op.
    bus.publish(UserCreated("u3", "e3"))
    time.sleep(0.3)
    assert count == _DRAIN_COUNT, "publish() after shutdown should be a no-op"


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
    with isolated_event_bus():
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
        assert wait_for(lambda: b.dropped_count >= _MIN_DROPPED, timeout=10.0), "no events dropped under backpressure"
        # The queue size never exceeds max_queue_size.
        assert b.pending_count <= _MAX_QUEUE_SIZE, f"queue exceeded max_queue_size: {b.pending_count}"
    finally:
        b.shutdown()


# --- Public install operation (event-bus.md v2 REQ-008, AC-013 .. AC-016) ---


def test_ac_013_set_event_bus_installs_default() -> None:
    """AC-013: installing a bus into an unset shared default returns None and makes it the default."""
    with isolated_event_bus():
        EVENTBUS_SLOT.clear()  # Given: the shared default is unset
        bus = EVENTBUS_SLOT.new()
        try:
            assert EVENTBUS_SLOT.install(bus) is None
            assert get_event_bus() is bus
        finally:
            bus.shutdown()


def test_ac_014_replace_logs_one_warning(log_records: list[Any]) -> None:
    """AC-014: replacing a held default logs exactly one WARNING naming it; installing into an unset slot logs none."""
    with isolated_event_bus():
        EVENTBUS_SLOT.clear()
        first = EVENTBUS_SLOT.new()
        EVENTBUS_SLOT.install(first)  # unset slot: no WARNING
        assert not non_tracing_warnings(log_records), f"install into an unset slot warned: {log_records!r}"
        log_records.clear()
        second = EVENTBUS_SLOT.new()
        EVENTBUS_SLOT.install(second)  # held slot: exactly one WARNING, no exception
        warnings = non_tracing_warnings(log_records)
        assert len(warnings) == 1, f"expected exactly one replace WARNING, got {warnings!r}"
        assert "bus" in str(warnings[0]).lower(), f"the WARNING does not name the shared default: {warnings[0]!r}"
        assert get_event_bus() is second
        first.shutdown()
        second.shutdown()


def test_ac_015_concurrent_install_read_reset(monkeypatch: pytest.MonkeyPatch) -> None:
    """AC-015: concurrent lazy creates yield one bus; concurrent install/read/reset never tear the slot."""
    with isolated_event_bus():
        # Unset default: 8 threads read it into existence at the same moment.
        EVENTBUS_SLOT.clear()
        with widened_lazy_create_window(monkeypatch, EventBus) as window:
            reads = concurrent_reads(EVENTBUS_SLOT, _CONCURRENT_READERS)
        assert len(window.instances) == 1, f"lazy create race built {len(window.instances)} buses"
        assert all(b is reads[0] for b in reads), "concurrent readers did not receive one shared bus"

        # Held default: installs, reads and resets interleaved (EDGE-010 for this feature).
        EVENTBUS_SLOT.install(EVENTBUS_SLOT.new())
        installed = [EVENTBUS_SLOT.new() for _ in range(_CONCURRENT_INSTALLS)]
        try:
            errors = _concurrent_install_read_reset(installed)
            assert not errors, f"install/read/reset threads raised: {errors!r}"
            assert isinstance(get_event_bus(), EventBus), "the slot ended up torn"
        finally:
            for bus in installed:
                bus.shutdown()


def test_ac_016_install_then_reset_then_default() -> None:
    """AC-016: after install then reset, the getter returns a freshly created bus, not the installed one."""
    with isolated_event_bus():
        installed = EVENTBUS_SLOT.new()
        EVENTBUS_SLOT.install(installed)
        EVENTBUS_SLOT.clear()  # reset_event_bus(): clears the slot and shuts this bus down
        default = get_event_bus()
        assert isinstance(default, EventBus)
        assert default is not installed


def _concurrent_install_read_reset(installed: list[EventBus]) -> list[BaseException]:
    """Install ``installed``, read and reset the shared slot from barrier-released threads.

    Returns every exception the threads raised (an ``AssertionError`` from a read
    that saw a torn slot included) instead of letting a thread die silently.
    """
    start = threading.Barrier(_CONCURRENT_INSTALLS + _CONCURRENT_READERS + _CONCURRENT_RESETS)
    errors: list[BaseException] = []

    def _run(action: Callable[..., Any], *args: Any) -> None:
        try:
            start.wait(timeout=_BARRIER_TIMEOUT)
            action(*args)
        except BaseException as exc:
            errors.append(exc)

    threads = [threading.Thread(target=_run, args=(EVENTBUS_SLOT.install, bus)) for bus in installed]
    threads += [threading.Thread(target=_run, args=(_read_whole_bus,)) for _ in range(_CONCURRENT_READERS)]
    threads += [threading.Thread(target=_run, args=(EVENTBUS_SLOT.clear,)) for _ in range(_CONCURRENT_RESETS)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return errors


def _read_whole_bus() -> None:
    """A read must yield a whole ``EventBus`` — never a half-written slot."""
    assert isinstance(EVENTBUS_SLOT.read(), EventBus)
