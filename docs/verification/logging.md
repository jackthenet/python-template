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

**Date:** 2026-09-04
**Command:** `uv run python -m pytest tests/ -q`

**Result: 28 passed, 0 failed** — the full re-derived suite is GREEN.

### Implementation delivered

| Module | Purpose |
|---|---|
| `src/backend/logging/settings.py` | `Settings` (pydantic) + `get_settings()` stub (REQ-008/009, AC-014) |
| `src/backend/logging/_setup.py` | `setup_logger()` console + rotating file sinks, idempotent/thread-safe (REQ-001/002); `_InterceptHandler` stdlib → loguru routing with bootstrap-frame skipping (REQ-003, AC-005) |
| `src/backend/logging/_decorator.py` | `logged` / `logged_class` entry/exit/elapsed/exception tracing with `level`, `slow_threshold_ms`, `slow_threshold_setting`, `include_args`, `context_getter`, `depth` (REQ-004..007, AC-006..013) |
| `src/backend/logging/__init__.py` | Public API exports (AC-015) |

### Test-infrastructure fixes (permitted, non-weakening)

The re-derived suite (commit `70e9689`) referenced environment APIs that do not exist in the pinned toolchain. Each was fixed at the scaffolding level only; no behavioral assertion was weakened or removed.

| Fix | Reason |
|---|---|
| `tests/conftest.py` `log_records` fixture wraps captured records in a `_Captured` exposing `str(m)` and `m["level"]` / `m["record"]` | loguru sink `Message` is a `str` subclass; raw string indexing raised `TypeError`. The fixture now exposes the record the tests index. |
| `tests/property/.../test_logging_properties.py`: `st.floats(..., allow_inf=False)` → `allow_infinity=False` | hypothesis 6.155.0's parameter is `allow_infinity`; `allow_inf` is an invalid keyword. Bounded `min_value`/`max_value` already exclude infinity. |
| `tests/contract/.../test_logging_contracts.py`: `logger.enable()` → `logger.enable("DEBUG")` | loguru 0.7.3's `Logger.enable(name)` requires `name` (no-arg is a `TypeError`); no newer loguru exists in the index. This is the exact inverse of the preceding `logger.disable("DEBUG")`. |

**NFR-002** measured overhead (median, decorated no-op minus bare no-op) is ~0.16 ms/call — comfortably under the 1 ms budget.

---

## Phase 5 — Verification Report

**Date:** 2026-09-04

### Quality gates

| Gate | Command | Result |
|---|---|---|
| Lint | `uv run ruff check src/` | All checks passed |
| Format | `uv run ruff format --check src/backend/logging/` | 4 files already formatted |
| Types | `uv run mypy --explicit-package-bases --namespace-packages src/` | Success: no issues found in 5 source files |

> The `mypy` invocation uses `--explicit-package-bases --namespace-packages` because `src/backend/` is a namespace package (no `__init__.py`). With default mypy module resolution the `logging/` subpackage is ambiguous between module `logging` and `backend.logging`. This is a pre-existing project-structure property, not an implementation defect.

### Spec coverage

Every normative requirement (REQ-001 … REQ-009) has at least one GREEN test; every acceptance criterion (AC-001 … AC-015), invariant (INV-001 … INV-003), edge case (EDGE-001 … EDGE-005), and NFR (NFR-001 … NFR-004) is covered by a GREEN test. **Spec coverage = 100%.**

| Spec ID | GREEN test(s) |
|---|---|
| REQ-001 / AC-001 | `test_ac_001_setup_logger_adds_sinks` |
| REQ-002 / AC-002, AC-003 | `test_ac_002_setup_logger_idempotent`, `test_ac_003_setup_logger_thread_safe` |
| REQ-003 / AC-004, AC-005 | `test_ac_004_intercept_handler_routes_records`, `test_ac_005_intercept_handler_skips_bootstrap` |
| REQ-004 / AC-006, AC-008 | `test_ac_006_logged_sync_entry_exit`, `test_ac_008_logged_exception_propagates` |
| REQ-005 / AC-007, AC-009, AC-010, AC-011 | `test_ac_007_logged_async_entry_exit`, `test_ac_009_logged_level_param`, `test_ac_010_logged_include_args`, `test_ac_011_logged_slow_threshold` |
| REQ-006 / AC-012 | `test_ac_012_logged_class_public_method` |
| REQ-007 / AC-013 | `test_ac_013_logged_class_private_method` |
| REQ-008 / AC-014 | `test_ac_014_get_settings_defaults` |
| REQ-009 / AC-015 | `test_ac_015_obsolete_module_deleted` |
| INV-001 … INV-003 | `test_inv_001_concurrent_setup_logger_sinks`, `test_inv_002_elapsed_time_non_negative`, `test_inv_003_exception_propagates_unchanged` |
| EDGE-001 … EDGE-005 | `test_edge_001_log_file_parent_created`, `test_edge_002_logged_no_args`, `test_edge_003_logged_nonexistent_setting`, `test_edge_004_logged_class_no_public_methods`, `test_edge_005_intercept_unknown_level` |
| NFR-001 … NFR-004 | `test_nfr_001_setup_time_budget`, `test_nfr_002_decorator_overhead_budget`, `test_nfr_003_diagnose_false`, `test_nfr_004_backward_compatible_api` |
| Integration | `test_stdlib_loguru_decorator_pipeline` |

### Regression

`uv run python -m pytest tests/ -q` → **28 passed** (full suite).

---

## Phase 6 — Review Report

*(pending)*
