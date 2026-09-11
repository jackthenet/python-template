# Verification — Lint Fix: settings_test_helpers

**Type:** DOCS/CHORE
**Branch:** `chore/lint-settings-test-helpers`

---

## Phase 1 — Scope (no behavior delta)

**Date:** 2026-09-11

### Defect (CI lint gate)

`uv run ruff check .` (matching `.github/workflows/lint.yml`) fails with 4 pre-existing
errors in `tests/settings_test_helpers.py`:

- F401 line 10: `tempfile` imported but unused (module level).
- F401 line 15: `backend.settings.YamlValueRepository` imported but unused (module level).
- F811 line 42: `tempfile` redefined (function-local import inside `make_registry`).
- F811 line 44: `YamlValueRepository` redefined (function-local import inside `make_registry`).

Root cause: `make_registry` re-imports both names locally, leaving the module-level
imports unused duplicates.

### Changes

1. `tests/settings_test_helpers.py`
   - Remove the module-level `import tempfile` (line 10).
   - Remove `YamlValueRepository` from the module-level import (line 15), keeping
     `from backend.settings import SettingsRegistry` (used by the `make_registry`
     return annotation).
   - The function-local imports inside `make_registry` (lines 42–44) stay unchanged.
2. `docs/verification/lint-settings-test-helpers.md` (this file): scope + verification evidence.

### No-behavior-delta confirmation

- Both removed names are unused at module level (ruff F401); no test imports them from
  the helper (callers import only `wait_for`, `make_registry`, `EventCollector`).
- `backend.settings` is still imported at module level (via `SettingsRegistry`), so module
  import side effects are unchanged; `tempfile` is stdlib with no import side effects.
- No `src/` files, no API, no dependency, or test-logic changes.
