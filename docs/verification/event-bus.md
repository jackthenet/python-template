# Verification — Event Bus Feature

**Spec:** `docs/specs/event-bus.md`
**Branch:** `feature/event-bus`

---

## Phase 3 — RED Evidence

**Date:** 2026-09-04
**Command:** `uv run python -m pytest tests/acceptance/eventbus/ tests/property/eventbus/ tests/unit/eventbus/ tests/contract/eventbus/ tests/integration/eventbus/ -v`

**Result: 5 collection errors, 0 passed** — the suite fails before implementation.

All five event-bus test modules error at import time with
`ModuleNotFoundError: No module named 'backend.eventbus'`.
The feature module `src/backend/eventbus/` does not exist yet, so the public
API (`EventBus`, `get_event_bus`, `reset_event_bus`) is not importable.

### Test Inventory (31 tests, spec-derived)

| Category | File | Tests |
|---|---|---|
| Acceptance | `tests/acceptance/eventbus/test_eventbus.py` | AC-001 … AC-012 |
| Property | `tests/property/eventbus/test_eventbus_properties.py` | INV-001 … INV-004 |
| Unit (edge) | `tests/unit/eventbus/test_eventbus_edges.py` | EDGE-001 … EDGE-010 |
| Contract | `tests/contract/eventbus/test_eventbus_contracts.py` | NFR-001 … NFR-004 |
| Integration | `tests/integration/eventbus/test_eventbus_integration.py` | multi-feature publish/subscribe |

Every test function name encodes its spec ID
(`test_<id>_<spec suffix>`), matching the spec's test strategy.

### Commit

- RED baseline: `bcbe784` (`test(event-bus): add … tests (RED)`).

---

## Phase 4 — GREEN Evidence

**Date:** 2026-09-04
**Command:** `uv run python -m pytest tests/acceptance/eventbus/ tests/property/eventbus/ tests/unit/eventbus/ tests/contract/eventbus/ tests/integration/eventbus/ -v`

**Result: 31 passed, 0 failed** — the full event-bus suite is GREEN.

### Implementation delivered

| Module | Purpose |
|---|---|
| `src/backend/eventbus/eventbus.py` | `EventBus` (bounded, thread-safe, async in-memory bus), `get_event_bus()` singleton, `reset_event_bus()` (REQ-001..007, AC-001..012, INV-001..004, EDGE-001..010, NFR-001..004) |
| `src/backend/eventbus/__init__.py` | Public API exports (`EventBus`, `get_event_bus`, `reset_event_bus`) |

### Design

- **Async non-blocking delivery:** `publish()` enqueues via `queue.Queue.put_nowait` and returns; a single background worker thread (`eventbus-worker`, daemon) dequeues FIFO and dispatches.
- **Typed events (isinstance):** handlers are registered for an event type; `_dispatch` invokes every handler whose registered type matches the event by `isinstance`, in subscription order.
- **Bounded queue, drop-on-full:** `queue.Queue(maxsize=max_queue_size)`; `put_nowait` raises `queue.Full` → event dropped, logged, `dropped_count` incremented.
- **Handler error isolation:** `_dispatch` wraps each handler call in `try/except`; a handler's exception is caught and logged, remaining handlers still run, the publisher is unaffected.
- **Thread safety:** a `threading.Lock` guards the registry and lifecycle flags; `queue.Queue` is itself thread-safe.
- **Lifecycle:** lazy start on first `publish()`/`start()`; `shutdown()` sets a flag, puts a sentinel, and joins the worker (graceful drain); idempotent; context manager.
- **Singleton:** module-level `list[EventBus | None]` holder (avoids a `global` statement); `get_event_bus()` returns the shared default, `reset_event_bus()` shuts it down and resets.

### Quality gates

| Gate | Command | Result |
|---|---|---|
| Lint | `uv run ruff check src/` | All checks passed |
| Types | `uv run mypy src/` | Success: no issues found in 7 source files |

### Regression

`uv run python -m pytest tests/ -q` → **59 passed** (28 logging + 31 event-bus).

---

## Phase 5 — Verification Report

*(pending)*

---

## Phase 6 — Review Report

*(pending)*
