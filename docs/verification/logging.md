# Verification — Logging Feature

**Spec:** `docs/specs/logging.md`
**Branch:** `feature/logging`

---

## Phase 3 — RED Evidence

**Date:** 2026-09-04
**Command:** `uv run pytest tests/ -q`

**Result: 28 errors, 0 passed** — the suite fails before implementation.

All 28 tests error in the session setup fixture with
`ModuleNotFoundError: No module named 'backend.logging.settings'`.
The settings module (REQ-008 / AC-014) is the foundational missing piece:
the approved spec's `backend/logging/settings.py` does not exist, and the
in-process session setup (which configures the real sinks for the suite)
cannot run without it.

### Test Inventory (28 tests, spec-derived)

| Category | File | Tests |
|---|---|---|
| Acceptance | `tests/acceptance/logging/test_logging.py` | AC-001, AC-002, AC-015 |
| Unit | `tests/unit/logging/test_logging.py` | AC-003 … AC-014 |
| Unit (edge) | `tests/unit/logging/test_logging_edges.py` | EDGE-001 … EDGE-005 |
| Property | `tests/property/logging/test_logging_properties.py` | INV-001 … INV-003 |
| Contract | `tests/contract/logging/test_logging_contracts.py` | NFR-001 … NFR-004 |
| Integration | `tests/integration/logging/test_logging_integration.py` | stdlib + loguru + @logged pipeline |

Every test function name encodes its spec ID
(`test_<id>_<spec suffix>`), matching the spec's test strategy.

### Known gaps the tests will exercise once setup runs

Derived from the spec-vs-implementation analysis (the current
`backend/logging/` implementation predates the approved spec):

| Spec item | Expected failure mode |
|---|---|
| AC-001 / AC-002 | No real console/file sinks (no-op lambda sink; no `logger.remove()`) |
| AC-005 | No bootstrap-frame skipping in `_InterceptHandler` (wrong caller attribution) |
| AC-007 | No async support in `@logged` (elapsed time excludes execution) |
| AC-010 | No `include_args` parameter |
| AC-011 | No `slow_threshold_ms` parameter / no WARNING escalation |
| AC-014 | `backend/logging/settings.py` missing |
| EDGE-001 | No log-file parent directory creation |
| EDGE-003 | No `slow_threshold_setting` parameter |
| INV-001 | Handler count 1 (no-op sink), not exactly one console + one file |
| NFR-003 | No file sink (nothing to write) |
| NFR-004 | `logged` missing `slow_threshold_ms`, `slow_threshold_setting`, `include_args`, `context_getter`, `depth` |

---

## Phase 4 — GREEN Evidence

*(pending — implementation in progress)*

---

## Phase 5 — Verification Report

*(pending)*

---

## Phase 6 — Review Report

*(pending)*
