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
  | **TOTAL** | **556 passed, 1 skipped, 0 failed, 1 broken (hanging)** | — |

  - **TOTAL row corrected (S4.5):** the original "616 passed" was an internal doc error; the per-category rows sum to **556 passed**, confirmed by S4.4's collection count (557 collected = 556 row-sum + 1 skipped).

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

## Phase 4 (continued — S4.5, re-entry #2)

### S4.5 Fix the settings/event-bus singleton leak at the source + full regression

**User decision (Q-65, commit `e46ddc6`):** fix the leak at the source (restore-on-teardown fixture pattern in the affected test files). **No test weakening: ZERO assertion changes** (only registry/event-bus acquisition + teardown changes).

**Two-singleton leak mechanism (verified):**
- The failing test `tests/acceptance/logging_coverage/test_services_traced.py::test_service_registry_classes_traced` expects exactly **2** `SettingsRegistry.has` entry records: one from its explicit `bus = EventBus()` (the constructor's guarded read, AC-017/AC-018 — happens only when the settings-registry module singleton exists) and one from its own `reg.has("some.key")`.
- `SettingsRegistry.__init__` calls `get_event_bus()`; if the **event-bus** module singleton does NOT exist, it creates a new `EventBus()` — whose constructor (when the settings singleton exists) makes ANOTHER `has` call → 3 records → also a failure.
- So the test requires **BOTH** singletons to exist at test time; the suite must leave both singletons in a well-defined state after every test (restore-on-teardown). Failure modes: settings singleton missing → 1 record (`assert 1 == 2`, the observed S4.4 failure); event-bus singleton missing → 3 records.

**Leak sources (all fixed):**
1. **Settings-registry singleton** — tests that called `reset_settings_registry()` without restoring:
   - `tests/acceptance/settings/test_settings.py` (`test_ac_018_singleton`)
   - `tests/acceptance/settings_coverage/{test_constructor_defaults,test_live_reads,test_persistence,test_registration}.py` (autouse `_reset_registry` fixtures)
   - `tests/contract/settings_coverage/test_inventory.py`, `tests/property/test_settings_coverage.py`, `tests/unit/test_settings_coverage.py` (autouse fixtures)
   - `tests/{acceptance,contract,integration,property,unit}/mail/conftest.py` (autouse fixtures)
2. **Event-bus singleton** — tests that called `reset_event_bus()` without restoring:
   - `tests/acceptance/eventbus/test_eventbus.py` (`test_ac_011_singleton`)
   - `tests/acceptance/sessionmanagement/test_cap_eviction.py` (autouse `fresh_shared_bus` fixture)
   - `tests/acceptance/sessionmanagement/test_events.py` (`test_ac_038`)
   - `tests/contract/eventbus/test_eventbus_contracts.py` (`test_nfr_004`)
   - `tests/integration/eventbus/test_eventbus_integration.py` (`test_multi_feature_publish_subscribe`)
   - `tests/property/sessionmanagement/test_sessionmanagement_properties.py` (`test_inv_003`)
3. **Inventory-based reset (the source missed by the first S4.5 pass):** `tests/acceptance/logging_coverage/test_services_traced.py` (`test_module_functions_traced`) calls `INVENTORY_MODULE_FUNCTIONS`, which includes `reset_settings_registry` and `reset_event_bus` (module functions under test), and never restored. Found via a temporary state-probe pytest plugin (recorded the singleton slots before/after each test; the probe also confirmed the restore-on-teardown fixtures work for the settings/mail suites — the inventory test was the only additional true leak source). The probe plugin was deleted after use.

**Fix (fixture pattern, zero assertion changes):**
- `tests/settings_test_helpers.py`: new `isolated_registry(install=True|False)` context manager + `restore_singleton(saved)` — setup: save the current singleton (`get_settings_registry(required=False)`; may be `None`), reset, optionally install a fresh isolated registry (temp-dir value repository); teardown: restore the saved object into the module singleton slot (same mechanism as `install_isolated_registry()`); if the saved was `None`, leave it reset.
- `tests/eventbus_test_helpers.py`: new `isolated_event_bus()` context manager — teardown: if the event-bus singleton slot is missing (the test's own `reset_event_bus()` call shuts down the previous instance and leaves the slot missing), install a fresh singleton so a well-defined singleton exists after every test.
- Affected test files: bare reset calls replaced with the context managers (tests obtain the registry/bus from the fixtures); where a test reset AND installed a specific instance, that exact behavior is preserved — only the restore-on-teardown was added.
- **Leftover-state decision:** the previous (cut-off) S4.5 run left uncommitted changes covering the settings-singleton side (`isolated_registry`/`restore_singleton` helpers + the settings/mail test files). Evaluated via `git diff`: sound, consistent with the design, zero assertion changes → **completed from this state** (settings side kept; event-bus side + inventory-test fix added). The leftover temp file `regression_out.txt` was deleted.

**Per-file summary (what changed — ZERO assertion changes anywhere):**
- `tests/settings_test_helpers.py` — added `isolated_registry()` + `restore_singleton()` helpers (new code; no test changed).
- `tests/eventbus_test_helpers.py` — added `isolated_event_bus()` helper (new code; no test changed).
- `tests/mail_test_helpers.py` — removed now-unused `reset_registry()`/`setup_isolated_registry()` (superseded by `isolated_registry()`).
- `tests/acceptance/settings/test_settings.py` — `test_ac_018_singleton`: save the singleton + `restore_singleton` in `finally` (was: bare `reset_settings_registry()` in `finally`).
- `tests/acceptance/settings_coverage/test_constructor_defaults.py`, `test_live_reads.py` — autouse fixture: `with isolated_registry():` (was: install + bare reset in teardown).
- `tests/acceptance/settings_coverage/test_persistence.py`, `test_registration.py` — autouse fixture: `with isolated_registry(install=False):` (was: bare reset setup + teardown).
- `tests/contract/settings_coverage/test_inventory.py`, `tests/property/test_settings_coverage.py`, `tests/unit/test_settings_coverage.py` — autouse fixture: `with isolated_registry(install=False):` (was: bare reset setup + teardown).
- `tests/{acceptance,contract,integration,property,unit}/mail/conftest.py` — autouse fixture: `with isolated_registry():` (was: `setup_isolated_registry()` + bare reset in teardown).
- `tests/acceptance/eventbus/test_eventbus.py` — `test_ac_011_singleton`: wrapped in `with isolated_event_bus():`.
- `tests/acceptance/sessionmanagement/test_cap_eviction.py` — autouse `fresh_shared_bus`: wrapped in `with isolated_event_bus():`.
- `tests/acceptance/sessionmanagement/test_events.py` — `test_ac_038`: reset block wrapped in `with isolated_event_bus():`.
- `tests/contract/eventbus/test_eventbus_contracts.py` — `test_nfr_004`: reset block wrapped in `with isolated_event_bus():`.
- `tests/integration/eventbus/test_eventbus_integration.py` — `test_multi_feature_publish_subscribe`: body wrapped in `with isolated_event_bus():`.
- `tests/property/sessionmanagement/test_sessionmanagement_properties.py` — `test_inv_003`: body wrapped in `with isolated_event_bus():`.
- `tests/acceptance/logging_coverage/test_services_traced.py` — `test_module_functions_traced`: saves the settings singleton before the inventory call; body wrapped in `isolated_event_bus()`; settings singleton restored in `finally` (the inventory includes `reset_settings_registry`/`reset_event_bus` as module functions under test).

**Verification:**
- **Adversarial-order run** (settings + mail tests first, then the previously failing test):
  `uv run pytest tests/acceptance/settings tests/acceptance/settings_coverage tests/contract/settings tests/contract/settings_coverage tests/property/test_settings_coverage.py tests/unit/test_settings_coverage.py tests/acceptance/mail tests/contract/mail tests/acceptance/logging_coverage/test_services_traced.py -q` → **119 passed** (all GREEN).
- **Full regression** (300 s cap on the pytest run; broken hanging test deselected):
  - Run 1: **556 passed, 1 skipped, 0 failed** (1 deselected) in 161.41 s.
  - Run 2: **556 passed, 1 skipped, 0 failed** (1 deselected) in 162.46 s.
  - (Additionally, a probe-instrumented run: 556 passed — the state probe confirmed **no test leaves either singleton missing**; the only state change in the run was the session fixture's installation before the first test.)
- **Baseline comparison: IDENTICAL** — the true baseline is **556 passed, 1 skipped, 0 failed** (per-category row-sum; the Baseline TOTAL row was corrected in this step: the original "616" was an internal doc error, confirmed by S4.4's collection count).
- **Ruff:** `uv run ruff check .` → **All checks passed!** (clean).

**Gate: MET** — the REFACTOR invariant "no NEW test failures beyond the marked broken test" holds under the `pytest-randomly` ordering; the full regression is identical to the true baseline.

---

## Phase 5 — S5.1 (REFACTOR) — full regression + architecture rules

**Command:** full regression with 300 s cap on the pytest run, broken hanging test deselected (P-20):
`uv run pytest tests/ -q --deselect tests/acceptance/sessionmanagement/test_observability.py::test_ac_045_traced_methods_no_tokens_in_logs`

**Full regression result (independent confirmation — Phase 5 run):**
- **556 passed, 1 skipped, 0 failed** (1 deselected — the broken hanging test, may remain broken per P-20).
- Duration: **160.38 s** (0:02:40) — **timeout NOT hit** (cap 300 s).
- Skipped: `tests/acceptance/filemanagement/test_filemanagement.py:364` (symlinks not available on this host) — same as baseline.

**Baseline comparison: IDENTICAL** — true baseline is **556 passed, 1 skipped, 0 failed** (docs/verification/dependency-updates.md, Baseline section). No diff.

**Architecture rules:** `uv run pytest tests/architecture/ -v` → **N/A — no architecture test directory in this repo** (`tests/architecture/` does not exist).

**Gate: MET** — the REFACTOR invariant "suite result identical to baseline" holds on an independent Phase 5 run.

---

## Phase 5 — S5.2 (REFACTOR) — lint + types

**Lint (whole repo, matching CI):** `uv run ruff check .` → **All checks passed!** (0 errors, clean).

**Type check (the gate):** `uv run mypy src/` → **Success: no issues found in 56 source files** (PASS).

**Gate: MET** — lint clean and type checks pass over the whole repo (including the change's `src/backend/settings/repository.py` migration + test files + dependency changes).

---

## Phase 5 — Verification report (REFACTOR)

**Gate summary (REFACTOR gate set):**

| Check | Result | Evidence |
|---|---|---|
| Full regression suite (S5.1) | **556 passed, 1 skipped, 0 failed** (160.38 s; 1 deselected — the broken hanging test P-20) — **IDENTICAL to true baseline** | S5.1 section above |
| Architecture rules | **N/A** — no `tests/architecture/` directory in this repo | S5.1 section above |
| Lint (S5.2, whole repo, matching CI) | `uv run ruff check .` → **All checks passed!** (clean) | S5.2 section above |
| Type check (S5.2, the gate) | `uv run mypy src/` → **Success: no issues found in 56 source files** (PASS) | S5.2 section above |

**Spec coverage: N/A for REFACTOR** — no spec change, no new requirements; REFACTOR changes no externally observable behavior and is not tracked against REQ/AC IDs.

**Traceability: matrix UNCHANGED** — REFACTOR introduces no new requirements and changes no behavior, so `docs/verification/traceability.md` is not affected.
- Evidence: `git diff main...HEAD -- docs/verification/traceability.md` → **empty** (no diff). File present (43,600 bytes).

**Test-change audit (REFACTOR: no test weakened/deleted — authorized test changes documented):**
- `git diff main...HEAD --stat -- tests/` → **26 files changed, 260 insertions(+), 190 deletions(-)**.
- **No test deleted:** `git diff main...HEAD --diff-filter=D --name-only -- tests/` → empty. **No test file added:** `--diff-filter=A` → empty. **No test function removed or added:** diff contains zero removed/added `def test_` lines.
- **Zero assertion changes:** the diff removes 8 assertion lines and adds 8 assertion lines; after whitespace normalization the two sets are **identical** (every removed assertion is re-added verbatim — only re-indented, moved inside the restore-on-teardown context-manager blocks). One further removed line containing "assert" is a docstring comment ("this changes no test assertion"), not an assertion.
- **The 26 changed test files fall into exactly the two authorized categories:**
  - **(a) Mechanical pyyaml → ruamel.yaml import migration** (user instruction "replace pyyaml with ruamel.yaml") — exactly 4 settings test files: `tests/acceptance/settings/test_settings.py`, `tests/contract/settings/test_settings_contracts.py`, `tests/contract/settings_coverage/test_value_repository.py`, `tests/unit/settings/test_settings_edges.py`. Changes are limited to `import yaml` → `from ruamel.yaml import YAML`, `yaml.safe_load(...)` → `YAML(typ="safe").load(...)`, `yaml.safe_dump(...)` → ruamel block-style dump. Zero assertion changes.
  - **(b) Singleton-leak source fix (Q-65 — restore-on-teardown fixture pattern)** — helpers: `tests/settings_test_helpers.py` (new `isolated_registry()` + `restore_singleton()`), `tests/eventbus_test_helpers.py` (new `isolated_event_bus()`), `tests/mail_test_helpers.py` (removed superseded `reset_registry()`/`setup_isolated_registry()` — helper functions only, no assertions); plus 23 test/conftest files (settings/mail/eventbus/sessionmanagement/logging-coverage) whose fixtures/test bodies are wrapped in the context managers. Zero assertion changes.
  - The 4 files of category (a) also received the category (b) fixture pattern (overlap); no file shows any other kind of change.

**Invariant check — no observable behavior change:**
- Suite result **identical to baseline** (556 passed, 1 skipped, 0 failed; same skip — symlinks unavailable on host; same deselected broken test).
- Settings YAML format semantics preserved per the S4.2 format probe: **safe YAML, block style, sorted keys** (ruamel `YAML(typ="safe")` with `default_flow_style = False` reproduces the pyyaml `safe_dump`/`safe_load` semantics for the settings store).

**Known/broken (out of scope, user-authorized):** the hanging pre-existing test `tests/acceptance/sessionmanagement/test_observability.py::test_ac_045_traced_methods_no_tokens_in_logs` (P-20) remains broken — it hangs on `main` as well; it is deselected in the regression runs and may remain broken.

**VERDICT: VERIFIED** — REFACTOR gates satisfied: full regression GREEN and identical to baseline (zero test changes beyond the two documented, zero-assertion-change categories), architecture N/A, lint clean, mypy PASS, traceability matrix unchanged, no observable behavior change.

---

## Phase 6 — Review report (REFACTOR)

**Normative basis (REFACTOR):** baseline + scope — GREEN baseline (556 passed, 1 skipped, 0 failed; the true per-category row-sum baseline, with the user-authorized "GREEN except the marked broken tests" deviation and the 300 s run cap recorded in the Baseline section) plus the exact refactor scope (dev-group additions, `pytest-random` → `pytest-randomly` rename, `pyyaml` → `ruamel.yaml` replacement WITH behavior-preserving code migration, `pillow` update). The REFACTOR contract: no externally observable behavior change, no test weakened or deleted, no new behavior, no NEW test failures beyond the baseline's marked broken test.

### S6.1 — Review vs. normative basis

- **Inventory:** all **32 changed files** classified against the scope — **2 scoped dependency files** (`pyproject.toml`, lockfile), **1 scoped src migration** (`src/backend/settings/repository.py`), **26 authorized test files** (the 4 mechanical pyyaml → ruamel.yaml import-migration files + the Q-65 singleton-leak source-fix set, all zero assertion changes), **3 process records** (verification doc, problem log, AI questions), **0 unexpected files**.
- **Scope check: PASS** — no change beyond the scoped changes; no more, no less.
- **Invariant check: PASS** — no observable behavior change (settings YAML semantics preserved: safe YAML, block style, sorted keys; suite result identical to baseline); no test weakened or deleted (zero assertion changes; no test function/file removed or added); no new behavior; no NEW test failures beyond the marked broken test.
- **Finding F-1 (cosmetic, ACCEPTED):** the historical P-20 problem-log entry carries a stale "616" test count; the verification doc (this file) is the authoritative record (true baseline = 556 passed, 1 skipped, 0 failed; the "616" was an internal doc error already corrected in the Baseline section and in S4.5). No action — accepted as a historical-entry artifact.

### S6.2 — Traceability + boundaries

- **Traceability: PASS** — `docs/verification/traceability.md` unchanged (`git diff main...HEAD` empty); the requirement mapping of the changed tests is unchanged (REFACTOR introduces no new requirements and changes no behavior).
- **Feature boundaries: PASS** — the only `src/` change is the settings feature's own `src/backend/settings/repository.py`; no cross-feature internal imports introduced.
- **Architecture rules: PASS** — no `model/`, `services/`, or `shared/` paths touched.
- **Tests not weakened: PASS** — 0 test functions removed/added; no test file deleted; 8/8 assert statements identical after whitespace normalization (every removed assertion re-added verbatim, only re-indented/moved inside the restore-on-teardown context-manager blocks).
- **Finding F-2 (informational, RESOLVED):** a raw grep miscounted a docstring line in a removed helper as an assert; it is not an assertion — resolved, no impact on the zero-assertion-change conclusion.

### Findings

| ID | Severity | Status | Disposition |
|---|---|---|---|
| F-1 | Cosmetic | **Accepted** | Stale "616" count in the historical P-20 problem-log entry; the verification doc is authoritative. No action. |
| F-2 | Informational | **Resolved** | Docstring line miscounted as an assert by raw grep; not an assertion. No action. |

**All findings resolved/accepted — none open.**

### Review verdict

**CLEAN** — the change is complete per the Review Gate (REFACTOR): every REFACTOR gate satisfied — full suite GREEN (556 passed, 1 skipped, 0 failed) and identical to baseline with zero test weakening/deletion (only the two documented, zero-assertion-change categories), no observable behavior changed, feature boundaries and architecture rules respected, lint clean, mypy PASS, traceability matrix unchanged.

---

# Verification: dependency-updates — Cycle 2 (REFACTOR, 2026-09-20)

> New change cycle, branched from `main` @ `51b530a` (merge of PR #40, the previous dependency-updates cycle recorded above). The previous cycle's record is preserved as-is for history.

## Classification

- **Type:** REFACTOR
- **Rationale:** Update all project dependencies (in `pyproject.toml`) to their current releases, per repo precedent (PR #40 did the same). Behavior-preserving: no observable behavior change; the full test suite stays GREEN (identical to the baseline below, with the same known-hanging test deselected); no test changes.
- **Date:** 2026-09-20.
- **Base:** `main` @ `51b530a`.

## Baseline (Phase 1 — GREEN)

- **Command (all full-suite runs for this change):**
  ```
  timeout 600 uv run pytest tests/ -q -p no:randomly --deselect tests/acceptance/sessionmanagement/test_observability.py::test_ac_045_traced_methods_no_tokens_in_logs
  ```
- **Known-hanging test deselected (documented, per change instruction):** `tests/acceptance/sessionmanagement/test_observability.py::test_ac_045_traced_methods_no_tokens_in_logs` — a known-hanging test on `main` (infinite loop in the test's own assertion loop). It is **fixed in a separate in-flight change** `hanging-observability-test` (PR #44, not yet merged into `main`). The deselect is **not a regression of this change** and applies to the baseline and all subsequent full-suite runs for this change.
- **Runs (2026-09-20):**

  | Run | Result | Duration | Note |
  |---|---|---|---|
  | 1 | 1 failed, 555 passed, 1 skipped, 1 deselected | 162.86 s | Failure: `tests/property/settings/test_settings_properties.py::test_inv_002_get_value_always_valid` (pre-existing flaky; passes in isolation and in subsequent runs — see classification below) |
  | 2 | **556 passed, 1 skipped, 1 deselected** | 159.02 s | **GREEN — the baseline** |
  | 3 | 1 failed, 555 passed, 1 skipped, 1 deselected | 162.76 s | Failure: `tests/property/filemanagement/test_filemanagement_properties.py::test_inv_005_avatar_url_format` with `hypothesis.errors.DeadlineExceeded` (288.56 ms > default 200 ms deadline) wrapped in `FlakyFailure` (pre-existing timing flakiness under full-suite load) |

- **Baseline determination: GREEN** — Run 2: **556 passed, 1 skipped, 1 deselected** (0 failed).
- **Skipped test (pre-existing environmental skip, part of the baseline):** `tests/acceptance/filemanagement/test_filemanagement.py::test_ac_031_symlink_rejected` — "symlinks not available on this host".
- **Classification of the flaky property-test failures (Runs 1 and 3):**
  - **Pre-existing:** this change has not started — no file changes, no dependency updates (working tree clean at `51b530a`). Any failure observed is pre-existing by definition.
  - **Environmental (timing):** Hypothesis's default 200 ms per-example deadline is occasionally exceeded when the full suite runs on this Windows host under load. The affected property tests set `max_examples` (and health-check suppressions) but **no `deadline` override**, so the 200 ms default applies. Both failing tests pass in isolation and in subsequent runs; a different property test is hit on each run. This is a known class of host-timing flakiness, not a behavior defect.
  - **Not caused by this change; not fixed in this step** (out of scope — see Refactor scope / Out of scope).

## Refactor scope

- **What changes (Phase 4):** update all project dependencies (in `pyproject.toml`) to their current releases.
- **Invariants that MUST hold:**
  1. **No observable behavior change** — the full suite stays GREEN, identical to the baseline (same command, same known-hanging-test deselect): **556 passed, 1 skipped, 1 deselected** (modulo the documented pre-existing flaky Hypothesis-deadline failures, which are environmental noise, not behavior).
  2. **No test changes** — no test added, removed, or modified (no assertion changes, no test weakening or deletion).
  3. **No `src/` behavior change** beyond what the dependency updates require (e.g., a behavior-preserving code migration forced by a dependency API change is in scope, per the PR #40 precedent).
- **Out of scope:**
  - Fixing the hanging test `tests/acceptance/sessionmanagement/test_observability.py::test_ac_045_traced_methods_no_tokens_in_logs` (that is PR #44, a separate in-flight change).
  - Any behavior change that a dependency update might require: **if a dependency update breaks the suite, STOP and report — do not force it** (Escalation Rules apply).
  - Fixing the pre-existing flaky Hypothesis-deadline property-test failures (environmental; out of scope for this change).

## Phase 4 — Implement (REFACTOR — behavior-preserving steps)

**Date:** 2026-09-20 15:57.

### Dependencies updated to current releases

All 29 direct project dependencies (runtime + dev groups) were checked against PyPI. Exactly **4 were outdated** and updated to their current releases; the other 25 were already at their current release. Two additional lower bounds (those packages already at the current release) were raised to the current release to reflect it (PR #40 pattern: bound = current release; no installed-version change).

| Package | Group | Old (installed / bound) | → Current release | Bound change |
|---|---|---|---|---|
| `pydantic` | runtime | 2.13.4 / `>=2.13.1` | **2.13.5** | `>=2.13.1` → `>=2.13.5` |
| `hypothesis` | dev | 6.155.0 / `>=6.155.0` | **6.168.0** | `>=6.155.0` → `>=6.168.0` |
| `ruff` | dev | 0.16.7 / `>=0.16.7` | **0.16.8** | `>=0.16.7` → `>=0.16.8` |
| `ty` | dev | 0.0.81 / `>=0.0.81` | **0.0.82** | `>=0.0.81` → `>=0.0.82` |
| `mypy` | dev | 2.3.1 / `>=1.10` | 2.3.1 (already current) | `>=1.10` → `>=2.3.1` (bound only) |
| `pytest-cov` | dev | 7.1.0 / `>=6.0` | 7.1.0 (already current) | `>=6.0` → `>=7.1.0` (bound only) |

**Transitive (lockfile only, no `pyproject.toml` change):** `pydantic-core` 2.46.4 → 2.46.5 (required by `pydantic` 2.13.5).

**Already at current release (no change):** loguru 0.7.3, orjson 3.12.0, httpx 0.28.1, sqlmodel 0.0.42, argon2-cffi 25.1.0, email-validator 2.3.0, filetype 1.2.0, pillow 12.3.0, ruamel-yaml 0.19.1, alembic 1.20.0, bandit 1.9.4, complexipy 8.0.1, deptry 0.25.1, mkdocstrings 1.0.6, pip-audit 2.10.1, polyfactory 3.3.0, pre-commit 4.6.2, py-spy 0.4.2, pytest 9.1.1, pytest-randomly 5.0.0, pytest-xdist 3.8.0, respx 0.23.1, time-machine 3.5.1.

### Behavior-preserving code migration

**None required.** No dependency update introduced a breaking API change in `src/`. The `pydantic` 2.13.4 → 2.13.5, `hypothesis` 6.155.0 → 6.168.0, `ruff` 0.16.7 → 0.16.8, and `ty` 0.0.81 → 0.0.82 updates are all backward-compatible (no `src/` changes needed). No `src/` files were modified.

### Full-suite results (hanging test deselected, deterministic ordering)

**Command (all runs):**
```
timeout 600 uv run pytest tests/ -q -p no:randomly --deselect tests/acceptance/sessionmanagement/test_observability.py::test_ac_045_traced_methods_no_tokens_in_logs
```

| Run | Result | Duration | Note |
|---|---|---|---|
| 1 | 1 failed, 555 passed, 1 skipped, 1 deselected | 161.17 s | Failure: `tests/property/filemanagement/test_filemanagement_properties.py::test_inv_005_avatar_url_format` (pre-existing flaky — see classification) |
| 2 | 1 failed, 555 passed, 1 skipped, 1 deselected | 159.32 s | Same pre-existing flaky failure |
| 3 | **556 passed, 1 skipped, 1 deselected** | 159.27 s | **GREEN — identical to baseline** |
| 4 | **556 passed, 1 skipped, 1 deselected** | (n/a) | **GREEN — identical to baseline** |
| 5 | **556 passed, 1 skipped, 1 deselected** | (n/a) | **GREEN — identical to baseline** |
| 6 | **556 passed, 1 skipped, 1 deselected** | 161.91 s | **GREEN — identical to baseline** |

**Baseline comparison: IDENTICAL** — the GREEN runs (3–6) are **556 passed, 1 skipped, 1 deselected** (0 failed), identical to the Phase 1 baseline (Run 2: 556 passed, 1 skipped, 1 deselected). The skip is the pre-existing filemanagement symlink skip (`test_ac_031_symlink_rejected` — symlinks not available on this host).

### Classification of the flaky failure (Runs 1–2)

- **Test:** `tests/property/filemanagement/test_filemanagement_properties.py::test_inv_005_avatar_url_format`.
- **Pre-existing:** this is the exact test documented in the Phase 1 baseline (Run 3) as a `hypothesis.errors.DeadlineExceeded` failure (Hypothesis's default 200 ms per-example deadline exceeded under full-suite load on this Windows host; the test sets `max_examples` but no `deadline` override). It is a documented pre-existing environmental flaky failure, NOT a regression of this change.
- **Not a behavior defect:** the test **passes in isolation** (1 passed in 1.80 s) and **passed on 4 of 6 full-suite runs** (Runs 3–6). A real behavior regression would fail consistently (in isolation and in the full suite); this fails only under load.
- **Not fixed in this step** (out of scope — see Refactor scope / Out of scope).

### Invariant check

- **No observable behavior change:** suite result identical to baseline (GREEN runs: 556 passed, 1 skipped, 1 deselected, 0 failed); the dependency updates are backward-compatible (no `src/` changes).
- **No test changes:** no test added, removed, or modified (only `pyproject.toml` + `uv.lock` changed).
- **No `src/` behavior change:** no `src/` files changed.

### Gate: MET

The REFACTOR invariant "no observable behavior change; full suite stays GREEN, identical to the baseline" holds: 4 consecutive GREEN full-suite runs (556 passed, 1 skipped, 1 deselected, 0 failed), identical to the Phase 1 baseline, modulo the documented pre-existing flaky Hypothesis-deadline failure (which passed on 4 of 6 runs and in isolation).

---

## Phase 5 — Verify (REFACTOR)

**Date:** 2026-09-20 16:55 (all runs 2026-09-20 16:35–16:55).

### S5.1 — Full regression suite (MUST be GREEN, zero test changes, identical to baseline)

**Command (all runs):**
```
timeout 600 uv run pytest tests/ -q -p no:randomly --deselect tests/acceptance/sessionmanagement/test_observability.py::test_ac_045_traced_methods_no_tokens_in_logs
```

**Runs (3):**

| Run | Result | Duration | Note |
|---|---|---|---|
| 1 | **556 passed, 1 skipped, 1 deselected** (0 failed) | 158.24 s | **GREEN — identical to baseline** |
| 2 | 1 failed, 555 passed, 1 skipped, 1 deselected | 160.86 s | Failure: `tests/property/filemanagement/test_filemanagement_properties.py::test_inv_003_metadata_matches_content` — documented pre-existing flaky class (see classification) |
| 3 | **556 passed, 1 skipped, 1 deselected** (0 failed) | 160.65 s | **GREEN — identical to baseline** |

**Baseline comparison: IDENTICAL** — the two clean GREEN runs (1 and 3) are **556 passed, 1 skipped, 1 deselected** (0 failed), identical to the Phase 1 baseline (556 passed, 1 skipped, 1 deselected). The skip is the pre-existing filemanagement symlink skip (`test_ac_031_symlink_rejected` — symlinks not available on this host); the deselect is the documented known-hanging test (fixed in PR #44, a separate in-flight change).

**Classification of the Run 2 failure (pre-existing / environmental — NOT a regression):**
- **Test:** `tests/property/filemanagement/test_filemanagement_properties.py::test_inv_003_metadata_matches_content`.
- **Documented pre-existing class:** this is the exact class documented in the Phase 1 baseline and change instruction — Hypothesis's default 200 ms per-example deadline is occasionally exceeded when the full suite runs on this Windows host under load; the affected property tests set `max_examples` but no `deadline` override; **a different property test is hit on each run** (Phase 1: `settings::test_inv_002_get_value_always_valid`, `filemanagement::test_inv_005_avatar_url_format`; Phase 4: `filemanagement::test_inv_005_avatar_url_format`; Phase 5 Run 2: `filemanagement::test_inv_003_metadata_matches_content`).
- **Environmental, not a behavior defect:** the test **passes in isolation** (`1 passed in 1.13 s`) and **passed on the other two Phase 5 full-suite runs** (Runs 1 and 3). A real behavior regression would fail consistently (in isolation and in the full suite); this fails only under load.
- **Not fixed in this step** (out of scope — environmental noise, per change instruction).

**Zero test changes: CONFIRMED** — `git diff 51b530a..HEAD -- tests/` → **empty** (no test added, removed, or modified). `git diff 51b530a..HEAD --stat -- src/` → **empty** (no `src/` file changed). The only changed files vs. base are `pyproject.toml` and `uv.lock` (plus this verification record).

**Gate: MET** — full regression suite GREEN and identical to the baseline (2 clean GREEN runs), zero test changes.

### S5.2 — Architecture rules + lint + types

**Architecture rules:** `uv run pytest tests/architecture/ -q -p no:randomly` → **N/A — no `tests/architecture/` directory in this repo** (same as Cycle 1). No architecture rules to run; nothing to violate.

**Lint (whole repo, matching CI):** `uv run ruff check .` → **All checks passed!** (0 errors, clean).

**Type check (the gate):** `uv run mypy src/` → **Success: no issues found in 56 source files** (PASS). This change touched no `src/` file, so no new mypy errors — confirmed.

**Gate: MET** — architecture N/A, lint clean, types pass.

### No observable behavior change (REFACTOR invariant)

- Suite result **identical to the baseline** on both clean Phase 5 runs: **556 passed, 1 skipped, 1 deselected, 0 failed** (same skip — filemanagement symlink; same deselect — the known-hanging test, PR #44).
- No `src/` file changed; no test file changed; only `pyproject.toml` + `uv.lock` (dependency lower bounds raised to current releases; all updates backward-compatible — no behavior-preserving code migration was required).

### Gate summary (REFACTOR Phase 5 gate set)

| Check | Result | Evidence |
|---|---|---|
| Full regression suite (S5.1) | **556 passed, 1 skipped, 1 deselected, 0 failed** (Runs 1 and 3; 158.24 s / 160.65 s) — **IDENTICAL to baseline**; Run 2 hit the documented pre-existing flaky class (passes in isolation) | S5.1 section above |
| Zero test changes | `git diff 51b530a..HEAD -- tests/` → **empty** (and `-- src/` → empty) | S5.1 section above |
| Architecture rules (S5.2) | **N/A** — no `tests/architecture/` directory in this repo | S5.2 section above |
| Lint (S5.2, whole repo, matching CI) | `uv run ruff check .` → **All checks passed!** (clean) | S5.2 section above |
| Type check (S5.2, the gate) | `uv run mypy src/` → **Success: no issues found in 56 source files** (PASS; no new errors — no `src/` file touched) | S5.2 section above |
| No observable behavior change | Suite result identical to the baseline; only `pyproject.toml` + `uv.lock` changed | "No observable behavior change" section above |

**VERDICT: VERIFIED** — REFACTOR Phase 5 gates satisfied: full regression suite GREEN and identical to the baseline (556 passed, 1 skipped, 1 deselected, 0 failed; 2 clean GREEN runs), zero test changes, architecture N/A, lint clean, mypy PASS, no observable behavior change.

---

## Phase 6 — Review (REFACTOR)

**Date:** 2026-09-20.
**Scope reviewed:** `git diff 51b530a..HEAD` (branch `refactor/dependency-updates`, 3 commits ahead of `main` @ `51b530a` — `e571cec` Phase 1 baseline, `aedc54b` Phase 4 implement, `73afcba` Phase 5 verify).

**Normative basis (REFACTOR):** baseline + refactor scope (Cycle 2 sections above) — GREEN baseline (Run 2: 556 passed, 1 skipped, 1 deselected, 0 failed, with the known-hanging test deselected per change instruction; that test is fixed in PR #44) plus the exact refactor scope (update all project dependencies in `pyproject.toml` to their current releases). REFACTOR contract: no observable behavior change, no test changes, no `src/` behavior change beyond what the dependency updates require, no NEW test failures.

### S6.1 — Review vs. normative basis

- **Diff scope check: PASS** — `git diff 51b530a..HEAD --name-only` → exactly **3 files**: `pyproject.toml`, `uv.lock`, `docs/verification/dependency-updates.md` (this verification record). No other file changed — no more, no less than the scoped change.
- **No test changes: PASS** — `git diff 51b530a..HEAD -- tests/` → **empty** (no test added, removed, or modified; zero assertion changes).
- **No `src/` behavior change: PASS** — `git diff 51b530a..HEAD -- src/` → **empty** (no `src/` file changed — all dependency updates are backward-compatible; no behavior-preserving code migration was required).
- **`pyproject.toml` check: PASS** — exactly **6 lower-bound raises** and nothing else:

  | Package | Bound change |
  |---|---|
  | `pydantic` | `>=2.13.1` → `>=2.13.5` |
  | `hypothesis` | `>=6.155.0` → `>=6.168.0` |
  | `mypy` | `>=1.10` → `>=2.3.1` (bound only; installed version already 2.3.1) |
  | `pytest-cov` | `>=6.0` → `>=7.1.0` (bound only; installed version already 7.1.0) |
  | `ruff` | `>=0.16.7` → `>=0.16.8` |
  | `ty` | `>=0.0.81` → `>=0.0.82` |

- **`uv.lock` check: PASS** — exactly **5 package version bumps** + **6 manifest specifier updates**, no other dependency-graph changes:

  | Package | Lockfile change |
  |---|---|
  | `hypothesis` | 6.155.0 → 6.168.0 (wheel set now per-platform `cp310-abi3` wheels — expected for the version bump) |
  | `pydantic` | 2.13.4 → 2.13.5 |
  | `pydantic-core` | 2.46.4 → 2.46.5 (transitive; required by `pydantic` 2.13.5) |
  | `ruff` | 0.16.7 → 0.16.8 |
  | `ty` | 0.0.81 → 0.0.82 |

- **Dependencies at current releases: PASS** — re-verified against PyPI (2026-09-20): pydantic **2.13.5**, hypothesis **6.168.0**, mypy **2.3.1**, pytest-cov **7.1.0**, ruff **0.16.8**, ty **0.0.82** — all 6 bounds equal the current PyPI releases.
- **No observable behavior change: PASS** — independent Phase 6 full-suite run (same command as baseline / Phase 4 / Phase 5):
  ```
  timeout 600 uv run pytest tests/ -q -p no:randomly --deselect tests/acceptance/sessionmanagement/test_observability.py::test_ac_045_traced_methods_no_tokens_in_logs
  ```
  → **556 passed, 1 skipped, 1 deselected** (0 failed) in 158.56 s (600 s cap NOT hit) — **IDENTICAL to the Phase 1 baseline** (Run 2). The skip is the pre-existing filemanagement symlink skip (`test_ac_031_symlink_rejected` — symlinks not available on this host); the deselect is the documented known-hanging test (fixed in PR #44, a separate in-flight change).

### S6.2 — Traceability + boundaries

- **Traceability: PASS** — REFACTOR introduces no new requirements and changes no behavior; `docs/verification/traceability.md` is not in the diff (unchanged).
- **Feature boundaries / architecture: PASS** — no `src/` file touched; no feature directory, `model/`, `services/`, or `shared/` path touched.
- **Tests not weakened: PASS** — zero test changes (empty `tests/` diff; nothing added, removed, or modified).

### Findings

| ID | Severity | Status | Disposition |
|---|---|---|---|
| — | — | — | No findings. |

**No open findings.**

### Review verdict

**CLEAN** — the change is complete per the Review Gate (REFACTOR): the diff is confined to `pyproject.toml` + `uv.lock` + this verification record; exactly 6 lower bounds raised to the current PyPI releases (re-verified against PyPI); the lockfile carries exactly the 5 expected version bumps (incl. transitive `pydantic-core`) and nothing else; zero test changes; zero `src/` changes; the full suite is GREEN and identical to the baseline (independent Phase 6 run: 556 passed, 1 skipped, 1 deselected, 0 failed); no observable behavior changed.

**Version bump: NONE** — REFACTOR → no version bump (per the Versioning section).
