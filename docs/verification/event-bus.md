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

*(pending implementation)*

---

## Phase 5 — Verification Report

*(pending)*

---

## Phase 6 — Review Report

*(pending)*
