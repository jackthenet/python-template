# Spec: Event Bus

## Changelog
- v2 (2026-10-06): REQ-008 added — public install operation for the shared default bus (`set_event_bus()`), with REQ-006's singleton-surface enumeration and NFR-004's public-API list extended to name it, and AC-013..AC-016, EDGE-011, EDGE-012 added. Change `settings-public-registry-setter` (CROSS-CUTTING); see `docs/specs/settings-public-registry-setter.md`. No existing ID was renumbered, restated or deleted.

## 1. Overview & Objectives
- **Feature Name:** Event Bus
- **Target Component:** `src/backend/eventbus/`
- **Goal:** Provide an in-memory, asynchronous event bus for decoupled communication between backend features. Features publish typed events without importing each other; a background worker dispatches events to the registered handlers without blocking the publisher, so nothing in the backend is delayed by a slow handler.
- **Scope:** In-memory pub/sub within the backend runtime. Typed events, async non-blocking delivery, handler error isolation, bounded-queue backpressure, graceful lifecycle, and a shared default instance.
- **Out of Scope:** Cross-runtime (frontend↔backend) communication, event persistence/durability, event replay/history, wildcard/glob topics, and any external broker (e.g., Redis, Kafka).

## 2. Architecture & Design Decisions
- **Design Pattern:** In-memory pub/sub: a bounded `queue.Queue` fed by non-blocking `publish()`, drained by a single background worker thread that dispatches each event to its handlers.
- **Dependencies:** stdlib only (`queue`, `threading`); uses the shared logging feature (`backend.logging`) to log dropped events and handler errors. No new external dependencies.
- **Constraints:** `publish()` MUST be non-blocking (never wait for handlers). Memory MUST be bounded by `max_queue_size`. The bus MUST be thread-safe. Exactly one background worker thread.
- **Design Decisions (WHAT; WHY goes to ADRs in Phase 2):**
  - D1: Asynchronous delivery — `publish()` enqueues and returns; a single background worker dispatches.
  - D2: Typed events — a handler is registered for an event type via `subscribe()`; a published event is matched to handlers by `isinstance`.
  - D3: Handler error isolation — a handler's exception is caught and logged; other handlers for the same event run; the publisher is unaffected.
  - D4: Bounded queue with drop-on-full backpressure — queue capped at `max_queue_size` (default 1000); excess events dropped, logged, and counted.
  - D5: Lazy start + graceful drain — the worker auto-starts on the first `publish()`; `shutdown()` drains then stops; `start()`/`shutdown()` are idempotent; the bus is a context manager.
  - D6: Module singleton + instantiable — `get_event_bus()` returns a shared default; `EventBus` is instantiable for tests/DI; `reset_event_bus()` resets the default for tests.
  - D7: Single background worker — events are dispatched FIFO, one at a time; handlers for a single event run in subscription order.

## 3. Data Structures & API Schemas

```python
from __future__ import annotations
from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")

class EventBus:
    def __init__(self, max_queue_size: int = 1000) -> None: ...
    def subscribe(self, event_type: type[T], handler: Callable[[T], None]) -> None: ...
    def unsubscribe(self, event_type: type[T], handler: Callable[[T], None]) -> None: ...
    def publish(self, event: T) -> None: ...          # non-blocking
    def start(self) -> None: ...                       # idempotent
    def shutdown(self) -> None: ...                   # idempotent, graceful drain
    @property
    def is_running(self) -> bool: ...
    @property
    def pending_count(self) -> int: ...               # events currently queued
    @property
    def dropped_count(self) -> int: ...               # events dropped (backpressure)
    def __enter__(self) -> "EventBus": ...
    def __exit__(self, *exc: object) -> None: ...

def get_event_bus() -> EventBus: ...                  # shared default (singleton)
def set_event_bus(bus: EventBus) -> None: ...         # install a configured bus as the shared default
def reset_event_bus() -> None: ...                    # reset the default (tests)
```

Example typed events (features define their own; any class is a valid event type, typically a Pydantic model or dataclass):

```python
from pydantic import BaseModel

class BaseEvent(BaseModel):
    """Optional base for catch-all subscriptions (isinstance matching)."""

class UserCreated(BaseEvent):
    user_id: str
    email: str

class OrderPlaced(BaseEvent):
    order_id: str
    user_id: str
    total_cents: int
```

## 4. Requirements

| ID | Requirement |
|----|-------------|
| REQ-001 | The event bus provides asynchronous, non-blocking delivery: `publish()` enqueues the event and returns without waiting for handlers; a single background worker dispatches events to handlers. |
| REQ-002 | The event bus supports typed event subscription: a handler is registered for an event type via `subscribe()`, and a published event is dispatched to every handler whose registered type matches the event by `isinstance`. |
| REQ-003 | The event bus isolates handler errors: a handler's exception is caught and logged, other handlers for the same event still run, and the exception never propagates to the publisher. |
| REQ-004 | The event bus is thread-safe: `publish()`, `subscribe()`, and `unsubscribe()` may be called from multiple threads concurrently without lost events or crashes. |
| REQ-005 | The event bus manages its worker lifecycle: the worker starts lazily on the first `publish()`, `shutdown()` gracefully drains events enqueued before it then stops, `start()`/`shutdown()` are idempotent, and the bus is usable as a context manager. |
| REQ-006 | The event bus provides a shared default instance: `get_event_bus()` returns a singleton for features, the `EventBus` class is instantiable for tests/DI, `set_event_bus()` installs a configured bus as the shared default (REQ-008), and `reset_event_bus()` resets the default for tests. |
| REQ-007 | The event bus bounds memory via a bounded queue: the queue is capped at `max_queue_size`, and when full, excess events are dropped, logged, and counted. |
| REQ-008 | The event bus provides a public install operation: `set_event_bus(bus)` installs the given `EventBus` as the shared default, so a later `get_event_bus()` returns exactly that instance. It replaces a non-empty default unconditionally and logs one WARNING when it does (none when the slot was empty); it is not retroactive; it accepts no `None` (clearing stays `reset_event_bus()`); it performs no runtime type check; it publishes no event; it neither shuts down nor starts the bus it replaces (lifecycle stays with the caller — only `reset_event_bus()` shuts down, REQ-005); and install, lazy create and reset are mutually exclusive under one module-level lock. |

## 5. Acceptance Criteria

| ID | References | Criterion |
|----|------------|-----------|
| AC-001 | REQ-001 | **Given** a bus with a handler that sleeps 100 ms, **When** `publish(event)` is called, **Then** `publish()` returns in < 10 ms, **And** the handler runs on the background worker after `publish()` returns. |
| AC-002 | REQ-002 | **Given** a bus, **When** `subscribe(UserCreated, handler)` is called and `publish(UserCreated(...))` is called, **Then** `handler` is called with the `UserCreated` event. |
| AC-003 | REQ-002 | **Given** a bus, **When** `subscribe(UserCreated, handler)` is called and `publish(OrderPlaced(...))` is called, **Then** `handler` is NOT called (different event type). |
| AC-004 | REQ-002 | **Given** a bus, **When** `subscribe(BaseEvent, handler)` is called and `publish(UserCreated(...))` is called where `UserCreated` is a subclass of `BaseEvent`, **Then** `handler` is called (isinstance matching). |
| AC-005 | REQ-003 | **Given** a bus with two handlers for `UserCreated` (one raises, one doesn't), **When** `publish(UserCreated(...))` is called, **Then** the non-raising handler is called, **And** the exception is logged. |
| AC-006 | REQ-003 | **Given** a bus, **When** a handler raises an exception, **Then** the exception does NOT propagate to the publisher (`publish()` completes normally). |
| AC-007 | REQ-004 | **Given** a bus, **When** `publish()` is called from multiple threads concurrently, **Then** every event is delivered to matching handlers, **And** no event is lost and no thread crashes. |
| AC-008 | REQ-005 | **Given** a bus, **When** `shutdown()` is called, **Then** the bus stops, **And** events enqueued before `shutdown()` are processed, **And** `publish()` after `shutdown()` is a no-op. |
| AC-009 | REQ-005 | **Given** a bus, **When** `shutdown()` is called twice, **Then** the second call is a no-op (idempotent). |
| AC-010 | REQ-005 | **Given** a bus used as a context manager, **When** the `with` block exits, **Then** the bus is shut down. |
| AC-011 | REQ-006 | **Given** the event bus module, **When** `get_event_bus()` is called twice, **Then** the same instance is returned (singleton). |
| AC-012 | REQ-007 | **Given** a bus with `max_queue_size=N`, **When** more than N events are published faster than they are consumed, **Then** the queue size never exceeds N, **And** excess events are dropped and `dropped_count` increases. |
| AC-013 | REQ-008 | **Given** the shared default is unset and a fresh `EventBus`, **When** `set_event_bus(bus)` is called, **Then** it returns `None`, **And** `get_event_bus()` returns that exact bus. |
| AC-014 | REQ-008 | **Given** the shared default already holds a bus, **When** `set_event_bus(other)` is called, **Then** no exception is raised, **And** `get_event_bus()` returns `other`, **And** exactly one WARNING record is logged naming the shared default; **And** **Given** the shared default is unset, **When** `set_event_bus(bus)` is called, **Then** no WARNING record is logged. |
| AC-015 | REQ-008 | **Given** the shared default is unset, **When** 8 threads call `get_event_bus()` concurrently, **Then** all return the same bus; **And** **Given** the shared default holds a bus, **When** threads install, read and reset concurrently, **Then** every read returns a whole bus and no thread crashes. |
| AC-016 | REQ-008 | **Given** a bus installed with `set_event_bus(a)`, **When** `reset_event_bus()` is called and then `get_event_bus()`, **Then** the returned bus is a freshly created default and is not `a`. |

## 6. Invariants

| ID | Invariant |
|----|-----------|
| INV-001 | For any event published before `shutdown()` and not dropped, the event is dispatched to each matching handler exactly once. |
| INV-002 | For any handler that raises, every other handler for the same event is still invoked (isolation holds). |
| INV-003 | For any number of concurrent `publish()` calls, the queue size never exceeds `max_queue_size`. |
| INV-004 | For any single event, its handlers are invoked in subscription order. |

## 7. Edge Cases & Error Conditions

| ID | Condition | Expected Behavior |
|----|-----------|-------------------|
| EDGE-001 | `publish()` before any prior publish (worker not yet started) | The worker starts lazily; the event is enqueued and processed. |
| EDGE-002 | `publish()` when the queue is full | The event is dropped, an error is logged, `dropped_count` increases; `publish()` does not block. |
| EDGE-003 | `subscribe()` with a non-callable handler | Raises `TypeError`. |
| EDGE-004 | `subscribe()` with a non-class event type | Raises `TypeError`. |
| EDGE-005 | `unsubscribe()` for a handler that is not subscribed | No-op (no error). |
| EDGE-006 | `subscribe()` the same handler for the same event type twice | The handler is registered once (dedup); invoked once per event. |
| EDGE-007 | `publish()` after `shutdown()` | No-op (the event is not enqueued). |
| EDGE-008 | A handler that raises | The exception is caught, logged, other handlers continue; the publisher is unaffected. |
| EDGE-009 | `start()` when the worker is already running | No-op (idempotent). |
| EDGE-010 | `publish()` with an event type that has no registered handlers | The event is enqueued and dispatched to no handlers (no error). |
| EDGE-011 | `set_event_bus(other)` replacing a shared default bus whose worker is running | The replaced bus is not shut down by the install and keeps dispatching until its owner shuts it down; the installed bus is not started before its first `publish()`. |
| EDGE-012 | Two threads lazily create the shared default bus at the same moment | Exactly one bus becomes the shared default and both callers receive it (the create race is closed by the module lock). |

## 8. Non-Functional Requirements

| ID | Category | Requirement |
|----|----------|-------------|
| NFR-001 | Performance | `publish()` is non-blocking: it returns without waiting for handlers, in < 1 ms (median) under normal load. |
| NFR-002 | Reliability | A handler's failure never prevents other handlers from receiving the event and never crashes the worker. |
| NFR-003 | Resource | The event bus uses exactly one background worker thread and a bounded queue; memory usage is bounded by `max_queue_size`. |
| NFR-004 | Contract | The public API (`EventBus`, `get_event_bus`, `set_event_bus`, `reset_event_bus`) is backward-compatible; adding optional parameters must not break existing callers. |

## 9. Test Strategy

| ID | Test Category | Test File | Test Function |
|----|---------------|-----------|---------------|
| AC-001 | acceptance | `tests/acceptance/eventbus/test_eventbus.py` | `test_ac_001_publish_non_blocking` |
| AC-002 | acceptance | `tests/acceptance/eventbus/test_eventbus.py` | `test_ac_002_subscribe_matching_event` |
| AC-003 | acceptance | `tests/acceptance/eventbus/test_eventbus.py` | `test_ac_003_no_match_different_type` |
| AC-004 | acceptance | `tests/acceptance/eventbus/test_eventbus.py` | `test_ac_004_isinstance_matching` |
| AC-005 | acceptance | `tests/acceptance/eventbus/test_eventbus.py` | `test_ac_005_error_isolation` |
| AC-006 | acceptance | `tests/acceptance/eventbus/test_eventbus.py` | `test_ac_006_exception_no_propagate` |
| AC-007 | acceptance | `tests/acceptance/eventbus/test_eventbus.py` | `test_ac_007_thread_safe_publish` |
| AC-008 | acceptance | `tests/acceptance/eventbus/test_eventbus.py` | `test_ac_008_shutdown_drains` |
| AC-009 | acceptance | `tests/acceptance/eventbus/test_eventbus.py` | `test_ac_009_shutdown_idempotent` |
| AC-010 | acceptance | `tests/acceptance/eventbus/test_eventbus.py` | `test_ac_010_context_manager` |
| AC-011 | acceptance | `tests/acceptance/eventbus/test_eventbus.py` | `test_ac_011_singleton` |
| AC-012 | acceptance | `tests/acceptance/eventbus/test_eventbus.py` | `test_ac_012_bounded_queue_drop` |
| REQ-008 | acceptance | `tests/acceptance/eventbus/test_eventbus.py` | `test_ac_013_set_event_bus_installs_default` |
| AC-013 | acceptance | `tests/acceptance/eventbus/test_eventbus.py` | `test_ac_013_set_event_bus_installs_default` |
| AC-014 | acceptance | `tests/acceptance/eventbus/test_eventbus.py` | `test_ac_014_replace_logs_one_warning` |
| AC-015 | acceptance | `tests/acceptance/eventbus/test_eventbus.py` | `test_ac_015_concurrent_install_read_reset` |
| AC-016 | acceptance | `tests/acceptance/eventbus/test_eventbus.py` | `test_ac_016_install_then_reset_then_default` |
| INV-001 | property | `tests/property/eventbus/test_eventbus_properties.py` | `test_inv_001_exactly_once` |
| INV-002 | property | `tests/property/eventbus/test_eventbus_properties.py` | `test_inv_002_isolation` |
| INV-003 | property | `tests/property/eventbus/test_eventbus_properties.py` | `test_inv_003_queue_bounded` |
| INV-004 | property | `tests/property/eventbus/test_eventbus_properties.py` | `test_inv_004_handler_order` |
| EDGE-001 | unit | `tests/unit/eventbus/test_eventbus_edges.py` | `test_edge_001_lazy_start` |
| EDGE-002 | unit | `tests/unit/eventbus/test_eventbus_edges.py` | `test_edge_002_drop_on_full` |
| EDGE-003 | unit | `tests/unit/eventbus/test_eventbus_edges.py` | `test_edge_003_non_callable_handler` |
| EDGE-004 | unit | `tests/unit/eventbus/test_eventbus_edges.py` | `test_edge_004_non_class_event` |
| EDGE-005 | unit | `tests/unit/eventbus/test_eventbus_edges.py` | `test_edge_005_unsubscribe_not_subscribed` |
| EDGE-006 | unit | `tests/unit/eventbus/test_eventbus_edges.py` | `test_edge_006_dedup` |
| EDGE-007 | unit | `tests/unit/eventbus/test_eventbus_edges.py` | `test_edge_007_publish_after_shutdown` |
| EDGE-008 | unit | `tests/unit/eventbus/test_eventbus_edges.py` | `test_edge_008_handler_raises` |
| EDGE-009 | unit | `tests/unit/eventbus/test_eventbus_edges.py` | `test_edge_009_start_idempotent` |
| EDGE-010 | unit | `tests/unit/eventbus/test_eventbus_edges.py` | `test_edge_010_no_handlers` |
| EDGE-011 | unit | `tests/unit/eventbus/test_eventbus_edges.py` | `test_edge_011_replaced_bus_not_shut_down` |
| EDGE-012 | unit | `tests/unit/eventbus/test_eventbus_edges.py` | `test_edge_012_concurrent_lazy_create` |
| NFR-001 | contract | `tests/contract/eventbus/test_eventbus_contracts.py` | `test_nfr_001_publish_non_blocking_budget` |
| NFR-002 | contract | `tests/contract/eventbus/test_eventbus_contracts.py` | `test_nfr_002_handler_failure_isolation` |
| NFR-003 | contract | `tests/contract/eventbus/test_eventbus_contracts.py` | `test_nfr_003_single_worker_bounded_queue` |
| NFR-004 | contract | `tests/contract/eventbus/test_eventbus_contracts.py` | `test_nfr_004_api_backward_compatible` |
| — | integration | `tests/integration/eventbus/test_eventbus_integration.py` | `test_multi_feature_publish_subscribe` |

## 10. Traceability Matrix

Maintain this matrix as tests are written and pass. Every normative requirement MUST have at least one executable test.

| Requirement | Acceptance Criterion | Test | Status |
|-------------|---------------------|------|--------|
| REQ-001 | AC-001 | `test_ac_001_publish_non_blocking` | PENDING |
| REQ-002 | AC-002 | `test_ac_002_subscribe_matching_event` | PENDING |
| REQ-002 | AC-003 | `test_ac_003_no_match_different_type` | PENDING |
| REQ-002 | AC-004 | `test_ac_004_isinstance_matching` | PENDING |
| REQ-003 | AC-005 | `test_ac_005_error_isolation` | PENDING |
| REQ-003 | AC-006 | `test_ac_006_exception_no_propagate` | PENDING |
| REQ-004 | AC-007 | `test_ac_007_thread_safe_publish` | PENDING |
| REQ-005 | AC-008 | `test_ac_008_shutdown_drains` | PENDING |
| REQ-005 | AC-009 | `test_ac_009_shutdown_idempotent` | PENDING |
| REQ-005 | AC-010 | `test_ac_010_context_manager` | PENDING |
| REQ-006 | AC-011 | `test_ac_011_singleton` | PENDING |
| REQ-007 | AC-012 | `test_ac_012_bounded_queue_drop` | PENDING |
| REQ-008 | AC-013 | `test_ac_013_set_event_bus_installs_default` | PENDING |
| REQ-008 | AC-014 | `test_ac_014_replace_logs_one_warning` | PENDING |
| REQ-008 | AC-015 | `test_ac_015_concurrent_install_read_reset` | PENDING |
| REQ-008 | AC-016 | `test_ac_016_install_then_reset_then_default` | PENDING |
| EDGE-011 | — | `test_edge_011_replaced_bus_not_shut_down` | PENDING |
| EDGE-012 | — | `test_edge_012_concurrent_lazy_create` | PENDING |
| INV-001 | — | `test_inv_001_exactly_once` | PENDING |
| INV-002 | — | `test_inv_002_isolation` | PENDING |
| INV-003 | — | `test_inv_003_queue_bounded` | PENDING |
| INV-004 | — | `test_inv_004_handler_order` | PENDING |
| NFR-001 | — | `test_nfr_001_publish_non_blocking_budget` | PENDING |
| NFR-002 | — | `test_nfr_002_handler_failure_isolation` | PENDING |
| NFR-003 | — | `test_nfr_003_single_worker_bounded_queue` | PENDING |
| NFR-004 | — | `test_nfr_004_api_backward_compatible` | PENDING |
