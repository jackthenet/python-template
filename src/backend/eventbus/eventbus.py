"""In-memory, asynchronous event bus for decoupled backend communication.

Features publish typed events without importing each other; a single
background worker dispatches each event to its registered handlers without
blocking the publisher. The queue is bounded by ``max_queue_size``; excess
events are dropped, logged, and counted.

Handler errors are isolated: a handler's exception is caught and logged, the
remaining handlers for the same event still run, and the exception never
propagates to the publisher.
"""

from __future__ import annotations

import queue
import threading
from collections.abc import Callable
from typing import TypeVar

from loguru import logger

from backend.logging import logged, logged_class

T = TypeVar("T")

# Sentinel placed in the queue to tell the worker to stop after draining.
_SENTINEL = object()


def _handler_name(handler: Callable[..., None]) -> str:
    """Best-effort human-readable name for a handler (for logging)."""
    qualname = getattr(handler, "__qualname__", None)
    return qualname if qualname is not None else repr(handler)


@logged_class(slow_threshold_ms=250)
class EventBus:
    """A bounded, thread-safe, asynchronous in-memory event bus.

    The class is traced via the shared logging feature (``@logged_class``);
    each public method produces entry and exit log records.
    """

    def __init__(self, max_queue_size: int | None = None) -> None:
        if max_queue_size is None:
            # AC-017/AC-018: read eventbus.max_queue_size from the settings
            # registry when it exists; otherwise fall back to the original
            # hardcoded default. The guarded read (required=False) never
            # creates the singleton, so there is no import side effect.
            from backend.settings import get_settings_registry

            registry = get_settings_registry(required=False)
            if registry is not None and registry.has("eventbus.max_queue_size"):
                max_queue_size = registry.get_value("eventbus.max_queue_size")
            else:
                max_queue_size = 1000
        self._max_queue_size = max_queue_size
        self._queue: queue.Queue = queue.Queue(maxsize=max_queue_size)
        self._registry: list[tuple[type, Callable[..., None]]] = []
        self._lock = threading.Lock()
        self._worker: threading.Thread | None = None
        self._shutdown = False
        self._dropped = 0

    @property
    def max_queue_size(self) -> int:
        """The configured maximum queue size."""
        return self._max_queue_size

    def subscribe(self, event_type: type[T], handler: Callable[[T], None]) -> None:
        """Register ``handler`` for ``event_type``.

        Raises ``TypeError`` if ``handler`` is not callable or ``event_type``
        is not a class. Subscribing the same (event_type, handler) pair twice
        has no additional effect (dedup).
        """
        if not callable(handler):
            raise TypeError("handler must be callable")
        if not isinstance(event_type, type):
            raise TypeError("event_type must be a class")
        with self._lock:
            for et, h in self._registry:
                if et is event_type and h is handler:
                    return
            self._registry.append((event_type, handler))
            logger.debug(
                "event bus: subscribed handler '{}' for event type '{}'", _handler_name(handler), event_type.__name__
            )

    def unsubscribe(self, event_type: type[T], handler: Callable[[T], None]) -> None:
        """Remove ``handler`` for ``event_type``. No-op if not subscribed."""
        with self._lock:
            for i, (et, h) in enumerate(self._registry):
                if et is event_type and h is handler:
                    del self._registry[i]
                    logger.debug(
                        "event bus: unsubscribed handler '{}' for event type '{}'",
                        _handler_name(handler),
                        event_type.__name__,
                    )
                    return

    def publish(self, event: T) -> None:
        """Enqueue ``event`` for asynchronous dispatch (non-blocking).

        If the queue is full, the event is dropped, logged, and counted.
        If the bus is shut down, this is a no-op.
        """
        with self._lock:
            if self._shutdown:
                return
            self._ensure_worker_unlocked()
        try:
            self._queue.put_nowait(event)
            logger.debug("event bus: published event type '{}'", type(event).__name__)
        except queue.Full:
            with self._lock:
                self._dropped += 1
                dropped = self._dropped
            logger.warning(
                "event bus: queue full; dropping event type '{}' (dropped={})", type(event).__name__, dropped
            )

    def start(self) -> None:
        """Start the background worker. Idempotent."""
        with self._lock:
            self._ensure_worker_unlocked()

    def shutdown(self) -> None:
        """Drain events enqueued before this call, then stop. Idempotent."""
        with self._lock:
            if self._shutdown:
                return
            self._shutdown = True
            worker = self._worker
        logger.debug("event bus: shutdown initiated")
        if worker is not None:
            # Blocking put: the worker is draining, so space opens up.
            self._queue.put(_SENTINEL)
            worker.join()

    @property
    def is_running(self) -> bool:
        """True if the background worker is running."""
        return self._worker is not None and not self._shutdown

    @property
    def pending_count(self) -> int:
        """Number of events currently queued."""
        return self._queue.qsize()

    @property
    def dropped_count(self) -> int:
        """Number of events dropped (backpressure)."""
        with self._lock:
            return self._dropped

    def __enter__(self) -> EventBus:
        return self

    def __exit__(self, *exc: object) -> None:
        self.shutdown()

    # -- internal --

    def _ensure_worker_unlocked(self) -> None:
        """Start the worker if not already running. Must be called under self._lock."""
        if self._worker is not None:
            return
        self._worker = threading.Thread(
            target=self._worker_loop,
            name="eventbus-worker",
            daemon=True,
        )
        self._worker.start()
        logger.debug("event bus: started background worker thread")

    def _worker_loop(self) -> None:
        """Drain the queue and dispatch events until the sentinel or shutdown."""
        while True:
            try:
                event = self._queue.get(timeout=0.1)
            except queue.Empty:
                if self._shutdown:
                    break
                continue
            if event is _SENTINEL:
                break
            self._dispatch(event)

    def _dispatch(self, event: object) -> None:
        """Dispatch ``event`` to every matching handler (isinstance), in order."""
        with self._lock:
            registry = list(self._registry)
        for event_type, handler in registry:
            if isinstance(event, event_type):
                logger.debug(
                    "event bus: dispatching event type '{}' to handler '{}'",
                    type(event).__name__,
                    _handler_name(handler),
                )
                try:
                    handler(event)
                except Exception:
                    logger.exception(
                        "event bus: handler '{}' raised for event type '{}'",
                        _handler_name(handler),
                        type(event).__name__,
                    )


_default_bus: list[EventBus | None] = [None]


@logged(slow_threshold_ms=5)
def get_event_bus() -> EventBus:
    """Return the shared default event bus (singleton)."""
    bus = _default_bus[0]
    if bus is None:
        bus = EventBus()
        _default_bus[0] = bus
        logger.debug("event bus: created shared default instance")
    return bus


@logged(slow_threshold_ms=5)
def reset_event_bus() -> None:
    """Reset the shared default event bus (for tests)."""
    bus = _default_bus[0]
    if bus is not None:
        bus.shutdown()
    _default_bus[0] = None
    logger.debug("event bus: reset shared default instance")
