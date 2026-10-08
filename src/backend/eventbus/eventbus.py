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

from backend.logging import get_logger, logged, logged_class

T = TypeVar("T")

# REQ-005 (structlog-logging): the module's one-off statements go through the logging
# feature's entry point instead of importing a logging backend. The feature name keeps
# the records attributable to the event bus.
_logger = get_logger("eventbus")

# Sentinel placed in the queue to tell the worker to stop after draining.
_SENTINEL = object()

# AC-017/AC-018 fallback: the queue size used when the settings registry has no
# ``eventbus.max_queue_size`` (event-bus.md D4 default).
_DEFAULT_MAX_QUEUE_SIZE = 1000


def _handler_name(handler: Callable[..., None]) -> str:
    """Best-effort human-readable name for a handler (for logging)."""
    qualname = getattr(handler, "__qualname__", None)
    return qualname if qualname is not None else repr(handler)


def _resolve_max_queue_size() -> int:
    """Resolve the default queue size from the settings registry (AC-017/AC-018).

    The guarded read (``required=False``) never creates the settings singleton, so
    there is no import side effect. It does take the settings module lock, so a
    caller that holds the event-bus slot lock must resolve the value **before**
    taking it and pass it in (finding F-72: the acquisition order is settings →
    bus everywhere, never bus → settings).
    """
    # Lazy import: backend.settings' registry reaches back into this module, so a
    # module-level import here would be circular.
    from backend.settings import get_settings_registry

    registry = get_settings_registry(required=False)
    if registry is not None and registry.has("eventbus.max_queue_size"):
        return registry.get_value("eventbus.max_queue_size")
    return _DEFAULT_MAX_QUEUE_SIZE


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
            # hardcoded default.
            max_queue_size = _resolve_max_queue_size()
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
            handler_name, event_name = _handler_name(handler), event_type.__name__
            _logger.debug(
                f"event bus: subscribed handler '{handler_name}' for event type '{event_name}'",
                handler=handler_name,
                event_type=event_name,
            )

    def unsubscribe(self, event_type: type[T], handler: Callable[[T], None]) -> None:
        """Remove ``handler`` for ``event_type``. No-op if not subscribed."""
        with self._lock:
            for i, (et, h) in enumerate(self._registry):
                if et is event_type and h is handler:
                    del self._registry[i]
                    handler_name, event_name = _handler_name(handler), event_type.__name__
                    _logger.debug(
                        f"event bus: unsubscribed handler '{handler_name}' for event type '{event_name}'",
                        handler=handler_name,
                        event_type=event_name,
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
        event_name = type(event).__name__
        try:
            self._queue.put_nowait(event)
            _logger.debug(f"event bus: published event type '{event_name}'", event_type=event_name)
        except queue.Full:
            with self._lock:
                self._dropped += 1
                dropped = self._dropped
            _logger.warning(
                f"event bus: queue full; dropping event type '{event_name}' (dropped={dropped})",
                event_type=event_name,
                dropped=dropped,
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
        _logger.debug("event bus: shutdown initiated")
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
        _logger.debug("event bus: started background worker thread")

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
                handler_name, event_name = _handler_name(handler), type(event).__name__
                _logger.debug(
                    f"event bus: dispatching event type '{event_name}' to handler '{handler_name}'",
                    event_type=event_name,
                    handler=handler_name,
                )
                try:
                    handler(event)
                except Exception:
                    _logger.exception(
                        f"event bus: handler '{handler_name}' raised for event type '{event_name}'",
                        handler=handler_name,
                        event_type=event_name,
                    )


_default_bus: list[EventBus | None] = [None]

# REQ-006 / ADR-084: one module-level lock guards all three slot operations —
# install, lazy create and reset. It is held only for the slot read/swap: no
# settings read, no shutdown() and no worker start happens under it (NFR-003,
# finding F-72).
_default_bus_lock = threading.Lock()


@logged(slow_threshold_ms=5)
def get_event_bus() -> EventBus:
    """Return the shared default event bus (singleton)."""
    # F-76: the settings value only matters when a bus is about to be constructed,
    # so a resolved slot is returned on a plain reference read. Resolving it on
    # every call reached the settings registry's enforced methods from the
    # composition root while its permission service was still unset, so
    # ``import main`` raised AttributeError (the settings read stays on the
    # lazy-create path, exactly as before the module lock was added).
    bus = _default_bus[0]
    if bus is not None:
        return bus
    # F-72: the settings read is resolved BEFORE the slot lock is taken. The
    # settings lazy create constructs a SettingsRegistry, which calls back into
    # this function, so a thread that reached settings while holding the bus lock
    # would close an ABBA cycle with a thread doing the opposite. Passing the
    # resolved value in keeps ``EventBus.__init__`` out of the settings module.
    max_queue_size = _resolve_max_queue_size()
    with _default_bus_lock:
        bus = _default_bus[0]
        if bus is None:
            # REQ-007: the owner's lazy create writes its own slot directly and
            # never calls set_event_bus() — it is not an install, so it must not
            # emit the replace WARNING.
            bus = EventBus(max_queue_size=max_queue_size)
            _default_bus[0] = bus
            _logger.debug("event bus: created shared default instance")
        return bus


@logged(slow_threshold_ms=5)
def set_event_bus(bus: EventBus) -> None:
    """Install ``bus`` as the shared default event bus (singleton).

    Replaces a non-empty default unconditionally and is never retroactive: an
    object constructed earlier with a bus keeps that bus. The install is
    lifecycle-neutral (EDGE-011) — it neither starts the installed bus nor shuts
    down the one it replaces; only ``reset_event_bus()`` shuts down (REQ-005).
    The parameter is never ``None`` — clearing stays the job of
    ``reset_event_bus()``.
    """
    with _default_bus_lock:
        previous = _default_bus[0]
        _default_bus[0] = bus
    if previous is not None:
        # REQ-002: exactly one WARNING naming the shared default (never the
        # instance), emitted after the lock is released (NFR-003).
        _logger.warning("event bus: shared default bus replaced")


@logged(slow_threshold_ms=5)
def reset_event_bus() -> None:
    """Reset the shared default event bus (for tests) — still shuts it down."""
    with _default_bus_lock:
        bus = _default_bus[0]
        _default_bus[0] = None
    if bus is not None:
        # event-bus.md REQ-005 / EDGE-007: reset keeps its shutdown semantics.
        # Draining and joining the worker is feature-level work, so it runs
        # outside the slot lock (NFR-003).
        bus.shutdown()
    _logger.debug("event bus: reset shared default instance")
