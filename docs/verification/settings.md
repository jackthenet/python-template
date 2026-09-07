# Verification — Settings Feature

**Spec:** `docs/specs/settings.md`
**Branch:** `feature/settings`

---

## Phase 3 — RED Evidence

**Date:** 2026-09-06
**Command:** `uv run pytest tests/acceptance/settings/ tests/property/settings/ tests/unit/settings/ tests/contract/settings/ tests/integration/settings/ -v`

**Result: 5 collection errors, 0 passed** — the suite fails before implementation.

All five settings test modules error at import time with
`ModuleNotFoundError: No module named 'backend.settings'`. The feature module
`src/backend/settings/` does not exist yet, so the public API
(`SettingsRegistry`, models, repository, exceptions) is not importable.

### Test Inventory (84 tests, spec-derived)

| Category | File | Tests |
|---|---|---|
| Acceptance | `tests/acceptance/settings/test_settings.py` | AC-001 … AC-039 (39) |
| Property | `tests/property/settings/test_settings_properties.py` | INV-001 … INV-010 (10) |
| Unit (edge) | `tests/unit/settings/test_settings_edges.py` | EDGE-001 … EDGE-029 (29) |
| Contract | `tests/contract/settings/test_settings_contracts.py` | NFR-001 … NFR-004 (4) |
| Integration | `tests/integration/settings/test_settings_integration.py` | multi-feature reactive + capture/restore (2) |

Every test function name encodes its spec ID
(`test_ac_XXX_…`, `test_inv_XXX_…`, `test_edge_XXX_…`, `test_nfr_XXX_…`),
matching the spec's test strategy.

### Commit

- RED baseline: see git log for `test(settings): add acceptance, property, unit, contract, integration tests (RED)`.

---

## Phase 4 — GREEN Evidence

**Date:** 2026-09-07
**Command:** `uv run pytest tests/acceptance/settings/ tests/property/settings/ tests/unit/settings/ tests/contract/settings/ tests/integration/settings/ -q`

**Result: 84 passed** — all spec-derived tests pass.

### Quality Gates

| Gate | Command | Result |
|---|---|---|
| Ruff (lint) | `uv run ruff check src/` | All checks passed |
| Ruff (format) | `uv run ruff format --check src/` | 12 files already formatted |
| Mypy | `uv run mypy src/` | Success: no issues found in 12 source files |

### Implementation Notes

- Public API exported from `backend.settings`; exceptions from `backend.settings.exceptions`; repository ABC + YAML implementation from `backend.settings.repository`.
- Construction-time validation raises `SettingsValidationError` (never raw `pydantic.ValidationError`), so the public error contract is the `SettingsError` hierarchy.
- `SettingsRegistry(event_bus=None, template_repository=None)`; a `None` bus uses the shared `get_event_bus()`, a `None` repository uses in-memory storage.
- Event publishing is best-effort; a shut-down bus may drop events.
- Template create/update require exact `(category, group)` scope coverage; `load_template` leaves missing values as-is and routes through `set_value`, publishing one `SettingChanged` per setting set.
- SLIDER values are valid only on the step grid `min + k*step` within `[min, max]`; `SliderSpec` guarantees `max` lies on the grid.

### Test-Setup Fixes (not weakenings)

- **AC-039 (`test_ac_039_reset_publishes_events`)**: The async event bus dispatches queued events to handlers registered *at dispatch time*. The original setup called `set_value` (publishing setup events) *before* `subscribe`, so a late handler could receive the setup events and `received[0]` would be a setup event (value="x"), not the reset event (value="a0"). Fixed by subscribing *before* the setup writes, waiting for those setup events to be delivered, then clearing — so no setup event is in flight when asserting on the reset events. All assertions preserved.
- **NFR-001 (`test_nfr_001_performance_budgets`)**: Replaced a buggy `delete_template` loop (deleting the same template 10×, which raised `TemplateNotFoundError` on the 2nd call) with a create-then-delete helper that exercises the delete budget via a fresh template per sample. Create+delete < 50 ms is a valid proxy for the delete budget (delete < create+delete).

### Performance Budget (NFR-001) — `load_template`

- Measured in the pytest context (session `setup_logger` with the synchronous console sink active): `load_template` (100 settings) median ≈ 8.6 ms, under the 10 ms budget. The per-`set_value` DEBUG log (mandated by the spec's observability table) is the dominant cost (~0.086 ms/log × 100 logs). The budget is satisfied by the median; individual samples can exceed 10 ms under load, so the test asserts on the median as specified.

### Commit

- GREEN: see git log for `feat(settings): implement settings registry, models, repository, exceptions (GREEN)`.
