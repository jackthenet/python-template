# Verification: file-management

## Change Type

- **Type:** FEATURE
- **Classified:** Phase 0 (orchestrator), 2026-08-16
- **Rationale:** Adds externally observable behavior/capability (file upload/download, user avatars, file metadata, storage abstraction, size/type validation) not covered by any approved spec in `docs/specs/`. Single new backend feature (like `mail`, `logging`); does not span two or more existing features, so not CROSS-CUTTING.
- **Branch:** `feature/file-management`
- **Worktree:** `../python-template_kopie-worktrees/feature/file-management`

## Governance Delegation (human authority)

- **Delegation:** The human governance authority (the user) explicitly delegated their spec-approval authority for the file-management spec PR to the agent: "auto approve the pr at the end of phase 1 by my authority" (2026-09-13).
- **Execution:** At S1.4 (end of Phase 1), the spec PR is approved AND merged via `gh pr merge` (through the GitHub PR process — NOT a direct push to `main`, which does not constitute approval per the Spec Approval Gate).
- **Note:** This exercises the human-controls-WHAT boundary by explicit delegation rather than by review. Recorded for traceability.

## Phase 1 — Spec approval

- **PR:** #24 — `spec(file-management): user file storage feature specification` (https://github.com/jackthenet/python-template/pull/24)
- **Merged:** 2026-09-13 (squash merge via `gh pr merge 24 --squash`)
- **Merge commit (on `main`):** `d0c99e1428121ac7be5f92c907266eeba0eba84e`
- **Merge-landed verification:** `git log origin/main -- docs/specs/file-management.md` shows commit `d0c99e1` touching the spec file; the spec file (715 lines) is present on `origin/main`. (The pre-merge commit `f4e45fc` is not a SHA ancestor of `origin/main` because the merge was a squash merge — the content landed via the new squash commit.)
- **CI checks:** `spec-validation` SUCCESS, `tests` SUCCESS (both completed before merge).
- **Approval authority:** executed on the explicit human governance delegation recorded in the "Governance Delegation (human authority)" section above ("auto approve the pr at the end of phase 1 by my authority", 2026-09-13). The approval was performed through the GitHub PR process (PR → merge), not a direct push to `main`, satisfying the Spec Approval Gate.
- **Note:** self-approval via `gh pr review --approve` is rejected by GitHub for the PR author's own PR; the merge step (with all CI checks green) constitutes the approval execution on the delegation.

## Phase 3 — Test & RED

- **Step:** S3.1 (derive tests), 2026-09-13.
- **Tests derived** from `docs/specs/file-management.md` (test strategy table, 90 test functions):
  - `tests/acceptance/filemanagement/test_filemanagement.py` — AC-001 .. AC-055 (55 acceptance tests).
  - `tests/property/filemanagement/test_filemanagement_properties.py` — INV-001 .. INV-008 (8 property tests, Hypothesis).
  - `tests/unit/filemanagement/test_filemanagement_edges.py` — EDGE-001 .. EDGE-019 (19 unit tests).
  - `tests/contract/filemanagement/test_filemanagement_contracts.py` — NFR-001 .. NFR-005 (5 contract tests).
  - `tests/integration/filemanagement/test_filemanagement_integration.py` — 3 integration tests (full file lifecycle, avatar lifecycle with variants, concurrent same-key upload).
  - `tests/filemanagement_test_helpers.py` — shared helpers (content factories, wiring helpers, fault-injection doubles).
  - Per-directory `conftest.py` in the five `filemanagement` test directories (shared `events` / `registry` / `repo` / `backend` / `service` fixtures).
- **Test-name check:** every written test function name matches the spec's test strategy table exactly (90/90; verified by diffing `def test_*` names in the written files against the spec table).
- **RED state confirmed:**
  - `uv run pytest tests/acceptance/filemanagement tests/property/filemanagement tests/unit/filemanagement tests/contract/filemanagement tests/integration/filemanagement -q` → **exit code 4** (collection error), failing with `ModuleNotFoundError: No module named 'backend.filemanagement'` (the feature is unimplemented; the helpers import the feature public API at module level).
  - `uv run pytest --collect-only` on the same paths shows the same `ModuleNotFoundError` at conftest import.
  - **Failure mode per test category** (all five categories fail identically at collection — each per-directory `conftest.py` and `tests/filemanagement_test_helpers.py` import the feature public API `backend.filemanagement` at module level, so no individual test function is reached; this is the valid RED signal for a new, unimplemented FEATURE, not a broken test contract):

    | Test category | Path | Failure mode |
    |---------------|------|--------------|
    | Acceptance | `tests/acceptance/filemanagement/` | Collection error — `ModuleNotFoundError: No module named 'backend.filemanagement'` (conftest import) |
    | Property | `tests/property/filemanagement/` | Collection error — `ModuleNotFoundError: No module named 'backend.filemanagement'` (conftest import) |
    | Unit | `tests/unit/filemanagement/` | Collection error — `ModuleNotFoundError: No module named 'backend.filemanagement'` (conftest import) |
    | Contract | `tests/contract/filemanagement/` | Collection error — `ModuleNotFoundError: No module named 'backend.filemanagement'` (conftest import) |
    | Integration | `tests/integration/filemanagement/` | Collection error — `ModuleNotFoundError: No module named 'backend.filemanagement'` (conftest import) |
- **Ruff:** `uv run ruff check` on all six new file-management test paths → **All checks passed** (exit 0). Repo-wide `uv run ruff check .` additionally reports 23 pre-existing `I001` import-sort errors in `tests/**/mail/**` that also exist on `main` (out of scope for this step; recorded for the verify phase).
- **Traceability:** `docs/verification/traceability.md` gained a **File Management Matrix** section mapping every REQ/AC/INV/EDGE/NFR to its test with status `RED`.

## Phase 4 — Implement (T-001)

- **Step:** S4.5 (commit + update status), completing the partially-finished S4.5 for task T-001, 2026-09-13.
- **T-001 scope:** foundation — `src/backend/filemanagement/{__init__,errors,events,models}.py` (error hierarchy with context, event types, domain models), committed as `c6b70c0` (plus the user-authorized test-helper import fixes Q-30/Q-31/Q-32).
- **GREEN confirmed (T-001 gate — "Acceptance test for AC-051 passes"):**
  - `uv run pytest tests/acceptance/filemanagement/test_filemanagement.py::test_ac_051_error_hierarchy_context -v` → `tests/acceptance/filemanagement/test_filemanagement.py::test_ac_051_error_hierarchy_context PASSED [100%]` — **1 passed in 0.13s**.
  - Note: the task's full-suite `green_command` (`uv run pytest tests/acceptance/filemanagement/ tests/property/filemanagement/ tests/unit/filemanagement/ tests/contract/filemanagement/ tests/integration/filemanagement/ -v`) is NOT expected to be fully green at this point — later tasks T-002..T-008 are unimplemented, so their tests still fail with the unimplemented signal. The T-001 completion gate is specifically the AC-051 acceptance test, which passes.
- **Ruff:** repo-wide `uv run ruff check .` → 23 errors, all pre-existing `I001` import-sort errors in `tests/**/mail/**` (same set recorded in Phase 3; out of scope). File-management paths (`src/backend/filemanagement/` + all five `tests/**/filemanagement/` test directories) → **All checks passed** (0 errors; no new errors introduced by T-001).
- **Task status:** `SPECIFIED → VERIFIED` for T-001 in both `.github/task-runner/tasks.json` and `docs/tasks/file-management.tasks.json` (synced), committed together with this evidence.

## Phase 4 — Implement (T-002)

- **Step:** S4.5 (commit + update status), for task T-002, 2026-09-13.
- **T-002 scope:** feature settings registration — `src/backend/filemanagement/feature_settings.py` with `register_settings(registry)` (traced with `@logged(slow_threshold_ms=5)`) that calls `registry.register_feature('filemanagement', [...])` registering the 5 `SettingDefinition`s (category `application`, group `filemanagement`): `filemanagement.storage_root` (TEXT, default `./data/files`), `filemanagement.max_file_size` (NUMBER, default `10485760`), `filemanagement.avatar_max_size` (NUMBER, default `2097152`), `filemanagement.allowed_types` (LIST, 9 MIME defaults), `filemanagement.avatar_base_url` (TEXT, default `files.example.com`); live-read pattern (settings read live on each operation, unregistered keys fall back to the hardcoded defaults); no import side effects (`register_settings` is an explicit function called at wiring time, not at import); re-exported from `src/backend/filemanagement/__init__.py` (REQ-024, ADR-057). Committed as `65425e0`.
- **Gate (NARROWED by DAG correction P-5):** "Acceptance test for AC-052 passes." AC-053 / `test_ac_053_unregistered_settings_defaults` was moved to T-008 (see "DAG Correction (T-002 gate, discovered in Phase 4)").
- **GREEN confirmed (T-002 gate — "Acceptance test for AC-052 passes"):**
  - `uv run pytest tests/acceptance/filemanagement/test_filemanagement.py::test_ac_052_register_settings -v` → `tests/acceptance/filemanagement/test_filemanagement.py::test_ac_052_register_settings PASSED [100%]` — **1 passed in 0.14s**.
  - Note: the task's full-suite `green_command` (`uv run pytest tests/acceptance/filemanagement/ tests/property/filemanagement/ tests/unit/filemanagement/ tests/contract/filemanagement/ tests/integration/filemanagement/ -v`) is NOT expected to be fully green at this point — later tasks T-003..T-008 are unimplemented, so their tests still fail with the unimplemented signal. The T-002 completion gate is specifically the AC-052 acceptance test, which passes.
- **Ruff:** repo-wide `uv run ruff check .` → 23 errors, all pre-existing `I001` import-sort errors in `tests/**/mail/**` (same set recorded in Phase 3; out of scope). File-management paths (`src/backend/filemanagement/` + all five `tests/**/filemanagement/` test directories) → **All checks passed** (0 errors; no new errors introduced by T-002).
- **Task status:** `SPECIFIED → VERIFIED` for T-002 in both `.github/task-runner/tasks.json` and `docs/tasks/file-management.tasks.json` (synced), committed together with this evidence.

## DAG Correction (T-002 gate, discovered in Phase 4)

- **When:** 2026-09-13, during S4.1 (pick T-002 + confirm RED).
- **Flaw:** T-002's completion gate ("Acceptance tests for AC-052, AC-053 pass") could not be satisfied by T-002 alone. `test_ac_052_register_settings` needs only `register_settings` (T-002), but `test_ac_053_unregistered_settings_defaults` is an integration-level test that also requires `InMemoryStorageBackend` (T-003), `SqliteFileRepository` (T-004), `FileService.upload` (T-005), and `FileService.upload_avatar` (T-007). Since T-005 depends on T-002 (must be VERIFIED), this created a deadlock: T-002 could not be VERIFIED until `test_ac_053` passed, but `test_ac_053` needs T-005/T-007.
- **Correction (decomposition fix, NOT a test weakening — `test_ac_053` is preserved, only moved to the task that can make it pass):**
  - T-002: `tests_to_create` → `[test_ac_052_register_settings]`; `acceptance_criteria` → `[AC-052]`; `completion_gates` → `["Acceptance test for AC-052 passes"]`.
  - T-008 (final cross-cutting task; depends on T-006 + T-007, so the full stack is available): added `test_ac_053_unregistered_settings_defaults` to `tests_to_create`, `AC-053` to `acceptance_criteria`, and `"Acceptance test for AC-053 passes"` to `completion_gates`.
  - Applied to both `.github/task-runner/tasks.json` and `docs/tasks/file-management.tasks.json` (kept in sync).
- **Rationale:** DAG ordering is T-001 → (T-002, T-003, T-004) → T-005 → (T-006, T-007) → T-008. `test_ac_053` can only pass after T-007, so T-008 is the earliest task where it is satisfiable. This respects "tests are the contract" (the test is neither weakened nor deleted).

## Evidence

- Phase 1 (Specify): spec committed, PR #24 opened + merged on human delegation (see "Phase 1 — Spec approval").
- Phase 3 (Test & RED): 90 tests derived from the spec, RED confirmed (`ModuleNotFoundError: backend.filemanagement`, pytest exit 4), ruff clean on the new files (see "Phase 3 — Test & RED").
- Phase 4 (Implement, T-001): foundation (errors, events, models) committed as `c6b70c0`; AC-051 acceptance test `test_ac_051_error_hierarchy_context` PASSED (GREEN); ruff clean on file-management paths (23 pre-existing mail `I001`s remain, out of scope); task status `VERIFIED` in both task files (see "Phase 4 — Implement (T-001)").
- Phase 4 (Implement, T-002): feature settings registration (`feature_settings.py` — `register_settings`, 5 `SettingDefinition`s, live-read pattern, no import side effects) committed as `65425e0`; AC-052 acceptance test `test_ac_052_register_settings` PASSED (GREEN; gate NARROWED by P-5 — AC-053 / `test_ac_053` moved to T-008); ruff clean on file-management paths (23 pre-existing mail `I001`s remain, out of scope); task status `VERIFIED` in both task files (see "Phase 4 — Implement (T-002)").
