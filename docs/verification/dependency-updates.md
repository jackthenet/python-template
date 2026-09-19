# Verification: dependency-updates (REFACTOR)

## Classification

- **Type:** REFACTOR
- **Rationale:** The change is dependency management with a behavior-preserving code migration. The `pyyaml` → `ruamel.yaml` replacement in the runtime dependency group requires a behavior-preserving code migration in `src/backend/settings/repository.py` (dump/load/error-class semantics) plus a mechanical `import yaml` migration in exactly 4 settings test files (assertions unchanged, no test weakened or deleted). All other parts (dev-group additions, `pytest-random` → `pytest-randomly` rename, `pillow` update) are behavior-preserving dependency management. No externally observable behavior change is introduced.
- **Date:** 2026-09-19 (baseline run); user instruction date 2026-09-16.

## Baseline

**User-authorized deviation from the strict GREEN-baseline gate (recorded as such):** the full-suite run carries a **300 s (5-minute) timeout on the pytest run itself** (environment setup time does not count); a run exceeding 300 s is killed and the timeout is recorded. **Pre-existing broken tests do NOT fail the step** — every broken (failing/erroring) test is marked in `docs/workflow/PROBLEMS.md` (entry **P-20**), and the baseline is treated as **"GREEN except the marked broken tests"**.

- **Command:** `uv run pytest tests/ -v` (300 s cap on the pytest process), then per-category / per-feature re-runs under the same cap to complete the evidence.
- **Date:** 2026-09-19.
- **300 s timeout hit:** YES — the full-suite run was killed at 300 s (at the kill point it had reached ~29–30% of the suite, all tests PASSED so far, no summary). The `tests/acceptance` category run and the `tests/acceptance/sessionmanagement` feature run also hit the 300 s cap (caused by the one hanging broken test). Evidence was completed with per-category and per-feature runs, each under the cap.
- **Suite result (complete evidence):**

  | Scope | Result | Duration |
  |---|---|---|
  | `tests/acceptance/authentication` | 35 passed | 9.35 s |
  | `tests/acceptance/eventbus` | 12 passed | 1.59 s |
  | `tests/acceptance/filemanagement` | 56 passed, 1 skipped (`test_ac_031_symlink_rejected` — symlinks not available on this host) | 3.21 s |
  | `tests/acceptance/logging` | 3 passed | 0.27 s |
  | `tests/acceptance/logging_coverage` | 16 passed | 1.24 s |
  | `tests/acceptance/mail` | 19 passed | 0.45 s |
  | `tests/acceptance/sessionmanagement` | 46 passed (+ 1 broken hanging test, deselected) | 7.39 s |
  | `tests/acceptance/settings` | 39 passed | 0.75 s |
  | `tests/acceptance/settings_coverage` | 8 passed | 1.57 s |
  | `tests/acceptance/usermanagement` | 38 passed | 3.29 s |
  | `tests/contract` | 41 passed | 56.49 s |
  | `tests/integration` | 22 passed | 5.37 s |
  | `tests/property` | 55 passed | 47.77 s |
  | `tests/unit` | 166 passed | 17.69 s |
  | **TOTAL** | **616 passed, 1 skipped, 0 failed, 1 broken (hanging)** | — |

- **Broken (marked) test node IDs** (marked in `docs/workflow/PROBLEMS.md`, entry **P-20**):
  - `tests/acceptance/sessionmanagement/test_observability.py::test_ac_045_traced_methods_no_tokens_in_logs` — **HANGS** (never completes within the 300 s cap, even in isolation; pre-existing).
- **User authorization:** "baseline = GREEN except the marked broken tests (user instruction 2026-09-16; broken tests marked in docs/workflow/PROBLEMS.md)".
- **Phase 4/5 invariant:** no NEW test failures beyond the marked broken test(s) above (they may remain broken; they are NOT fixed in this change).

## Refactor scope (exact scoped changes, Phase 0 user instruction)

1. **Add to the dev dependency group:** `alembic`, `polyfactory`, `respx`, `time-machine`, `mkdocstrings`, `deptry`.
2. **Replace in the dev dependency group:** `pytest-random` → `pytest-randomly`.
3. **Replace in the runtime dependency group:** `pyyaml` → `ruamel.yaml`, **WITH code migration**:
   - `src/backend/settings/repository.py`:
     - `yaml.safe_dump(values, sort_keys=True, default_flow_style=False)` → ruamel.yaml equivalent (block style, keys sorted, safe output);
     - `yaml.safe_load(text)` → ruamel.yaml safe-load equivalent;
     - `yaml.YAMLError` → the ruamel.yaml error class.
     - (Exact ruamel API to be pinned in Phase 4; file format semantics MUST stay: safe YAML, block style, sorted keys.)
   - **Mechanical import migration in exactly these 4 test files** (authorized by the user's explicit "replace pyyaml with ruamel.yaml" instruction; ALL assertions unchanged, no test weakened or deleted):
     - `tests/acceptance/settings/test_settings.py` (`import yaml` line 18; `yaml.safe_load` line 438)
     - `tests/contract/settings/test_settings_contracts.py` (`import yaml as _yaml` line 179; `_yaml.safe_dump` line 182)
     - `tests/contract/settings_coverage/test_value_repository.py` (`import yaml` line 7; `yaml.safe_load` line 30)
     - `tests/unit/settings/test_settings_edges.py` (`import yaml` line 13; `yaml.safe_dump` line 283)
4. **Update in the runtime dependency group:** `pillow` → current version (latest on PyPI at Phase 4 time).

### Invariants that MUST hold

- **No observable behavior change:** settings `values.yaml` / template `.yaml` files remain safe YAML, block style, sorted keys; load/dump semantics preserved.
- **No test weakened or deleted:** only the mechanical yaml import migration above (all assertions unchanged).
- **No new behavior.**
- **No NEW test failures beyond the baseline's marked broken test(s)** (`tests/acceptance/sessionmanagement/test_observability.py::test_ac_045_traced_methods_no_tokens_in_logs`).

## Out of scope

- The **MkDocs site setup** (mkdocs dependency, `mkdocs.yml`, `userdocs/` source directory) — separate future change (Q-63).
- The `userdocs/` source-directory naming decision is **binding for that future change** (Q-64).
- The **marked broken test(s)** — not fixed in this change (may remain broken).

## Phase 4 (Implement — behavior-preserving steps)

**Steps (all committed on `refactor/dependency-updates`):**

| Step | Change | Commit |
|---|---|---|
| S4.1 | dev deps: add `alembic`, `polyfactory`, `respx`, `time-machine`, `mkdocstrings`, `deptry`; replace `pytest-random` with `pytest-randomly` | `73db415` |
| S4.2 | runtime: replace `pyyaml` with `ruamel.yaml` (settings repository migration + mechanical import migration in exactly 4 settings test files; format probe: safe YAML, block style, sorted keys preserved) | `ab876bc` |
| S4.3 | runtime: update `pillow` to current version | `adc4ed4` |
| S4.4 | Full regression vs. baseline (this section) | this commit |

### S4.4 Full regression result

- **Command:** `uv run pytest tests/ -q --deselect tests/acceptance/sessionmanagement/test_observability.py::test_ac_045_traced_methods_no_tokens_in_logs` (300 s cap on the pytest run; the broken hanging test deselected — it can never complete — per the user-authorized procedure).
- **Runs (2, for reproducibility under different per-session random seeds):**
  - Run 1: **1 failed, 555 passed, 1 skipped, 1 deselected** in 172.50 s — 300 s cap NOT hit.
  - Run 2: **1 failed, 555 passed, 1 skipped, 1 deselected** in 173.65 s — 300 s cap NOT hit.
- **NEW failure (both runs, deterministic across seeds):** `tests/acceptance/logging_coverage/test_services_traced.py::test_service_registry_classes_traced` — assertion `assert 1 == 2` (entry-record count for `SettingsRegistry.has`).

### Comparison to baseline: NOT IDENTICAL

- Baseline (sum of the per-category rows in the Baseline section): **556 passed, 1 skipped, 0 failed** (+1 broken hanging test, deselected).
  - **Baseline doc inconsistency (flagged):** the Baseline TOTAL row says "616 passed", but the per-category rows sum to **556 passed**. This run collected **557 tests** (555 passed + 1 skipped + 1 failed), exactly the row-sum + the skipped test. The row-sum is therefore the true baseline total; the "616" in the TOTAL row is an internal documentation error.
- **Diff vs. baseline:**
  - **1 NEW failure:** `test_service_registry_classes_traced` (was GREEN in the baseline as part of `tests/acceptance/logging_coverage` = 16 passed).
  - **0 other changed outcomes** (all other tests: same pass/skip outcomes; the 1 skip is the pre-existing filemanagement symlink skip).
  - **Test count identical:** 557 collected in this run vs. 556 passed + 1 skipped = 557 in the baseline row-sum.

### Characterization of the new failure (diagnostic only — NOT fixed in this step)

- The test asserts that the `EventBus()` constructor produces a `SettingsRegistry.has` entry record (expects 2 total: one from the constructor, one from the test's own `reg.has(...)` call).
- `EventBus.__init__` (`src/backend/eventbus/eventbus.py`) calls `registry.has("eventbus.max_queue_size")` **only when the settings-registry module singleton exists** (`get_settings_registry(required=False)` is non-`None`); the singleton is created by other tests during a full-suite run.
- The test **passes in isolation** (`tests/acceptance/logging_coverage/test_services_traced.py`: 3 passed in 0.45 s) and passed in the baseline full-suite ordering (under `pytest-random`).
- Under the new test-ordering regime introduced by **S4.1** (`pytest-random` → `pytest-randomly`, per-session shuffling), the singleton is not created before this test in either full run → an **order/state-dependent test failure exposed by the S4.1 dependency swap** (test file unchanged in this change; verified via `git diff 78286eb..HEAD -- tests/` — only the 4 authorized yaml-migration files touched).

### Ruff gate

- `uv run ruff check .` → **All checks passed!** (clean).

### Invariant check

- **No test weakened or deleted:** only the authorized mechanical yaml import migration (S4.2; 4 settings test files; all assertions unchanged).
- **No observable product behavior change:** settings `values.yaml` / template `.yaml` format semantics preserved per the S4.2 format probe (safe YAML, block style, sorted keys); only `src/backend/settings/repository.py` changed in `src/`.
- **GATE NOT MET:** the REFACTOR invariant "no NEW test failures beyond the marked broken test" is violated by `test_service_registry_classes_traced` under the S4.1 test-ordering change. Phase 4 is **NOT complete**; re-entry is required (decision belongs to the orchestrator/user: e.g., make the order-dependent test robust, or reconsider the `pytest-randomly` swap). No fix was attempted in this step.
