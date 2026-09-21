# Verification: perf-budget-env-aware

## Type
Spec Amendment (triggered by an ISSUE) — amends NFR-001 in `docs/specs/settings.md`; the affected contract test is re-derived from the amended spec in Phase 3. No implementation change; no behavior change.

## Defect (the ISSUE)
- The perf-budget contract test `tests/contract/settings/test_settings_contracts.py::test_nfr_001_performance_budgets` failed at **65.4 ms** vs the **50 ms** budget on the (slow) CI runner.
- The 50 ms budget is spec-defined (NFR-001, amended in v2 when CI was ~28 ms; read-only ops stay < 1 ms).

## Root Cause
- **Environment-sensitive budget — not a code bug.** The implementation is already optimal: `set_value` → `_persist_values()` → `YamlValueRepository.save()` = one `_dump_yaml` of all 1000 values + one temp-file write + one atomic `os.replace` (single O(n) write). It persists all 1000 values per AC-013, which the spec requires.
- The budget is environment-sensitive: AC-013's synchronous full-value persistence is I/O-bound, so a slower CI runner hits 65 ms — beyond the ~2× headroom the 50 ms budget had over the ~28 ms CI baseline at v2.

## Amendment (user decision, 2026-09-21)
- **Settings NFR-001 (mutating-op budget only):** environment-aware — < 50 ms (median) locally, or < 100 ms (median) on CI (detected via the `CI` environment variable), with 1000 registered settings. Was: < 50 ms (median) for all environments.
- **Unchanged:** read-only ops (< 1 ms) and all other budgets (load_template 10 ms, create/update/delete 50 ms, list 500 ms) — only the mutating-op budget is failing and gets amended.

## Files changed
- `docs/specs/settings.md` (NFR-001 row + Changelog entry v3)
- `docs/verification/perf-budget-env-aware.md` (this record)

## Phase 5: Verify

**Scope note:** This is a **spec + test change only** — no `src/` code changed (the type-check gate confirms `src/` is clean, 56 source files).

### Gate results

1. **Full test suite** — `uv run pytest tests/ -v`: **556 passed, 1 skipped, 1 deselected** (exit 0, 158.49 s).
   - The re-derived test `tests/contract/settings/test_settings_contracts.py::test_nfr_001_performance_budgets` **PASSED** (local budget 50 ms; local median well under it).
   - **No new failures** beyond the marked broken tests:
     - **Deselected (pre-existing, marked BROKEN, P-20, user instruction 2026-09-16):** `tests/acceptance/sessionmanagement/test_observability.py::test_ac_045_traced_methods_no_tokens_in_logs` — a pre-existing hanging test (infinite loop in the test's own assertion loop; P-21). It hangs indefinitely, so it is deselected from the full-suite run and remains out of scope; its expected broken state is unchanged by this amendment.
     - **Skipped (pre-existing, environment):** `tests/acceptance/filemanagement/test_filemanagement.py::test_ac_031_symlink_rejected` — symlinks not available on this host.
   - No other failures, no errors.
2. **Lint** — `uv run ruff check .`: **clean** ("All checks passed!").
3. **Type check** — `uv run mypy src/`: **clean** ("Success: no issues found in 56 source files").

### Gate set

| Gate | Command | Result |
|------|---------|--------|
| Full test suite | `uv run pytest tests/ -v` (P-20 broken test deselected) | 556 passed, 1 skipped, 1 deselected — re-derived test PASSED; no new failures beyond marked broken tests |
| Lint | `uv run ruff check .` | clean |
| Types | `uv run mypy src/` | clean (56 source files) |

## Date
2026-09-21
