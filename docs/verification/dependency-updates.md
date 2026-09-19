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
