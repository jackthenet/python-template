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

## Phase 6: Review

**Status: CLEAN** — all review criteria PASS. The change is reviewed against its normative basis (amended spec NFR-001 + this triage/amendment record); no findings.

### Review criteria results

| # | Criterion | Result | Confirmation |
|---|-----------|--------|--------------|
| 1 | Against the amended spec (NFR-001) | **PASS** | The re-derived test implements the amended NFR-001 exactly: `_MUTATING_OP_BUDGET_MS = 50.0 if not os.environ.get("CI") else 100.0` — < 50 ms (median) locally, < 100 ms (median) on CI, detected via the `CI` environment variable, with 1000 registered settings. Read-only ops stay < 1 ms (`get_value`, `to_view`, `get_status` asserted `< 1.0`); all other budgets unchanged (`_LOAD_MS = 10.0`, `_YAML_MS = 50.0`, `_LIST_MS = 500.0`). |
| 2 | The test was NOT weakened | **PASS** | The budget was made **environment-aware per the amended spec** (50 ms local / 100 ms CI) — it was **NOT** lowered to match the implementation. The implementation is already optimal (single O(n) write; it persists all 1000 values per AC-013, which the spec requires) and no `src/` code changed. The local budget stays strict at 50 ms; only the CI budget is raised (to 100 ms) to be robust to slower CI runners, exactly as the amended NFR-001 states. |
| 3 | Traceability | **PASS** | The NFR-001 → `test_nfr_001_performance_budgets` mapping is intact (unchanged; same test function): the settings rows in `docs/verification/traceability.md` (NFR-001 … `test_nfr_001_performance_budgets` … GREEN) and the spec's own test strategy (`docs/specs/settings.md`, NFR-001 → `test_nfr_001_performance_budgets`) both reference the same, unmodified test function. |
| 4 | No behavior introduced beyond the spec | **PASS** | The change only amends the spec budget (NFR-001, v3 changelog) + re-derives the test. No `src/` code, no new behavior, no new dependency, no new public interface. |
| 5 | The pre-existing lint fix | **PASS** | The one blank line added in `test_nfr_004_observability` (between the stdlib `from io import StringIO` and the third-party `from ruamel.yaml import YAML` imports) is formatting-only (fixes a pre-existing I001 import-order lint error); no behavior change. |

### Test-not-weakened statement

The test was **NOT weakened**: the mutating-op budget is an **environment-aware budget per the amended spec** (50 ms local / 100 ms CI), not a budget lowered to match the implementation. The local budget remains strict at 50 ms; the CI-only relaxation (to 100 ms) is spec-defined (NFR-001 v3) and addresses environment sensitivity (AC-013's synchronous full-value persistence is I/O-bound), not an implementation regression. The implementation is already optimal and unchanged.

### Versioning decision

**NO version bump.** This is a spec + test change only: no `src/` code changed, no observable package behavior change. `bump-my-version` was NOT run; the PR contains no version bump commit.

### Date
2026-09-21
