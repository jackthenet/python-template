# Verification — Settings-Coverage Feature

**Spec:** `docs/specs/settings-coverage.md`
**Branch:** `feature/settings-coverage`

---

## Phase 3 — RED Evidence

**Date:** 2026-09-09
**Command:** `uv run pytest tests/acceptance/settings_coverage/ tests/unit/test_settings_coverage.py tests/property/test_settings_coverage.py tests/contract/settings_coverage/ -v`

**Result: 10 failed, 5 collection errors, 0 passed** — the suite fails before implementation.

Before implementation the new APIs do not exist:

- `ListSpec`, `SettingKind.LIST`, `list_spec` (T-001) — collection errors
  (`ImportError: cannot import name 'ListSpec' from 'backend.settings'`).
- `YamlValueRepository`, `ValueRepository`, `ValueStorageError`, registry
  `value_repository` (T-002) — collection errors
  (`ImportError: cannot import name 'YamlValueRepository' from 'backend.settings'`).
- `get_settings_registry(required=False)` (T-003) — assertion failures
  (the parameter does not exist yet).
- `EventBus` guarded read / `max_queue_size` attribute (T-004) — assertion
  failures (the attribute does not exist yet).
- Feature `register_settings` functions, `_read_setting`, live reads,
  constructor defaults (T-005) — `ImportError: cannot import name
  'register_settings' from 'backend.<feature>'`.
- No-arg `setup_logger`, sink reconfiguration, stub removal (T-006) —
  assertion failures (the stub `Settings` model still exists; `setup_logger`
  still requires an argument).
- `src/main.py` wiring (T-007) — the subprocess wiring check fails (main.py
  does not register any feature settings).

### Test Inventory (44 tests, spec-derived)

| Category | File | Tests |
|---|---|---|
| Acceptance | `tests/acceptance/settings_coverage/test_registration.py` | AC-001 |
| Acceptance | `tests/acceptance/settings_coverage/test_wiring.py` | AC-003 |
| Acceptance | `tests/acceptance/settings_coverage/test_live_reads.py` | AC-004 |
| Acceptance | `tests/acceptance/settings_coverage/test_constructor_defaults.py` | AC-005 |
| Acceptance | `tests/acceptance/settings_coverage/test_persistence.py` | AC-013, AC-015 |
| Acceptance | `tests/acceptance/settings_coverage/test_setup_logger.py` | AC-019, AC-020 |
| Contract | `tests/contract/settings_coverage/test_value_repository.py` | AC-014, NFR-005 |
| Contract | `tests/contract/settings_coverage/test_inventory.py` | AC-022, AC-023, AC-024, NFR-002, NFR-003 |
| Property | `tests/property/test_settings_coverage.py` | INV-001 … INV-005 |
| Unit | `tests/unit/test_settings_coverage.py` | AC-002, AC-006, AC-007…AC-012, AC-016…AC-018, AC-021, AC-025, AC-026, AC-027, EDGE-001…EDGE-012, NFR-001, NFR-004, NFR-006 |

### Notes

- The unit test file (`tests/unit/test_settings_coverage.py`) was drafted before
  the acceptance/contract/property files; all four categories were completed to
  match the spec's test strategy (section 10).
- Existing tests that import the logging stub `Settings` model
  (`tests/conftest.py`, `tests/unit/logging/`, `tests/contract/logging/`,
  `tests/property/logging/`, `tests/logging_coverage_test_helpers.py`) are
  updated as part of T-006 (REQ-016 removes the stub; spec-authorized change).

---

## Phase 4 — GREEN Evidence

**Command:** `uv run pytest tests/acceptance/settings_coverage/ tests/unit/test_settings_coverage.py tests/property/test_settings_coverage.py tests/contract/settings_coverage/ -v`

**Result:** All 50 settings-coverage spec-derived tests pass (GREEN).

**Full suite:** `uv run pytest tests/ -q` → 357 passed, 1 failed (pre-existing `test_nfr_001_performance_budgets`, confirmed via git stash to fail without Phase 4 changes).

### Task completion

| Task | Scope | Status |
|------|-------|--------|
| T-001 | LIST kind + ListSpec validation | GREEN |
| T-002 | ValueRepository ABC + YamlValueRepository + ValueStorageError | GREEN |
| T-003 | Guarded getter `get_settings_registry(required=False)` | GREEN |
| T-004 | EventBus constructor reads `eventbus.max_queue_size` from registry | GREEN |
| T-005 | `register_settings` + `_read_setting` + live reads + constructor defaults (4 features) | GREEN |
| T-006 | No-arg `setup_logger` + sink reconfiguration + stub removal (REQ-016) | GREEN |
| T-007 | `src/main.py` wiring | GREEN |

### Test-isolation notes

- Two original logging tests (`test_nfr_003_diagnose_false`, `test_service_registry_classes_traced`) show flaky failures when run in a large combined suite due to concurrent EventBus worker threads and log-file timing. They pass in isolation and in the full `uv run pytest tests/` run.
- The `test_service_registry_classes_traced` assertion was updated to expect 2 `SettingsRegistry.has` entry records (one from the EventBus constructor's lazy registry read, one from the test's direct call).
