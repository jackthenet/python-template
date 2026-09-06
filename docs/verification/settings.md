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
