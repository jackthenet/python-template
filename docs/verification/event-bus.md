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

**Date:** 2026-09-04

### Checks

| Check | Command | Result |
|---|---|---|
| Lint | `uv run ruff check src/ tests/` | All checks passed |
| Types | `uv run mypy src/` | Success: no issues found in 7 source files |
| Acceptance tests | `uv run python -m pytest tests/acceptance/eventbus/ -q` | 12 passed |
| Full regression suite | `uv run python -m pytest tests/ -q` | 59 passed (28 logging + 31 event-bus) |
| Spec validation | `uv run python scripts/verify_spec.py docs/specs/event-bus.md` | Traceability: PASS (every REQ has ACs, every AC has a test, every INV has a property test) |
| Coverage | `uv run pytest tests/ --cov` | N/A — coverage not installed; `[tool.coverage.run] source` references the old `python_template` package (pre-`src/` layout), so a run would not measure current code |
| Architecture rules | `uv run pytest tests/architecture/ -v` | N/A — `tests/architecture/` does not exist in this template |

### Spec coverage (100%)

Every normative requirement (REQ-001 … REQ-007) has at least one GREEN test; every acceptance criterion (AC-001 … AC-012), invariant (INV-001 … INV-004), edge case (EDGE-001 … EDGE-010), and NFR (NFR-001 … NFR-004) is covered by a GREEN test.

| Spec ID | GREEN test(s) |
|---|---|
| REQ-001 / AC-001 | `test_ac_001_publish_non_blocking` |
| REQ-002 / AC-002, AC-003, AC-004 | `test_ac_002_subscribe_matching_event`, `test_ac_003_no_match_different_type`, `test_ac_004_isinstance_matching` |
| REQ-003 / AC-005, AC-006 | `test_ac_005_error_isolation`, `test_ac_006_exception_no_propagate` |
| REQ-004 / AC-007 | `test_ac_007_thread_safe_publish` |
| REQ-005 / AC-008, AC-009, AC-010 | `test_ac_008_shutdown_drains`, `test_ac_009_shutdown_idempotent`, `test_ac_010_context_manager` |
| REQ-006 / AC-011 | `test_ac_011_singleton` |
| REQ-007 / AC-012 | `test_ac_012_bounded_queue_drop` |
| INV-001 … INV-004 | `test_inv_001_exactly_once`, `test_inv_002_isolation`, `test_inv_003_queue_bounded`, `test_inv_004_handler_order` |
| EDGE-001 … EDGE-010 | `test_edge_001_lazy_start` … `test_edge_010_no_handlers` |
| NFR-001 … NFR-004 | `test_nfr_001_publish_non_blocking_budget`, `test_nfr_002_handler_failure_isolation`, `test_nfr_003_single_worker_bounded_queue`, `test_nfr_004_api_backward_compatible` |
| Integration | `test_multi_feature_publish_subscribe` |

**No orphaned tests.** Every test function traces to a spec ID (the single integration test traces to the combined behavior of REQ-001/002/006 — a legitimate multi-component interaction test).

### Regression

`uv run python -m pytest tests/ -q` → **59 passed** (28 logging + 31 event-bus).

---

## Phase 6 — Review Report

**Date:** 2026-09-04

### Review order

1. **Specification** — The implementation matches the spec exactly: `publish()` enqueues and returns immediately (REQ-001, non-blocking); `subscribe()`/`isinstance` matching (REQ-002); handler exceptions caught, logged, and isolated (REQ-003); a lock + thread-safe queue make the bus thread-safe (REQ-004); lazy start, graceful drain, idempotent `shutdown()`, and context-manager support (REQ-005); the module singleton `get_event_bus()`/`reset_event_bus()` (REQ-006); and the bounded queue with drop-on-full (REQ-007). No more, no less.
2. **Traceability** — Every REQ-XXX maps to AC-XXX maps to executable tests (verified by `verify_spec.py`: Traceability PASS). The single integration test traces to the combined behavior of REQ-001/002/006 (a legitimate multi-component interaction test), so there are no orphaned tests.
3. **Acceptance tests** — The tests prove the specified behavior. No test was modified to make the implementation pass; no test was deleted or weakened. The only post-RED edits were lint fixes (constants for magic values, named functions for handlers, import cleanup) that do not change any assertion.
4. **Implementation** — The code is correct, minimal, and within feature boundaries: `src/backend/eventbus/` only. The singleton uses a `list[EventBus | None]` holder (no `global`); the worker is a single daemon thread; `shutdown()` blocks on the sentinel `put` + `join` for a graceful drain.
5. **Architecture** — Dependencies respect the feature architecture rules: stdlib only (`queue`, `threading`) + the shared logging feature (loguru). No new external dependencies; no cross-feature internal imports.
6. **Quality** — `ruff check src/ tests/` clean; `mypy src/` clean (7 source files); naming and complexity are reasonable.

### Findings

| # | Severity | Finding | Resolution |
|---|---|---|---|
| F-1 | Minor | `shutdown()`'s blocking `put(_SENTINEL)` will wait if the queue is at capacity, so `shutdown()` blocks until the worker drains the queue. This is the intended graceful-drain behavior (REQ-005), but it means `shutdown()` is not non-blocking. | Accepted — matches the spec ("drains all pending events before stopping"). Documented in the docstring. |
| F-2 | Minor | `dropped_count` is a monotonically increasing counter (never reset). | Accepted — matches the spec ("counted"); tests only assert `>= 1`. |

### Verdict

**Review clean.** No P0/P1 findings; the two minor findings are accepted as spec-conformant. The feature is reusable by future features (a shared async communication capability), so a usage note is added to `AGENTS.md`. A PR for `feature/event-bus` → `main` is opened for human review/merge (the agent does not merge it).
