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

## DAG Correction (T-005 gate, discovered in Phase 4)

- **When:** 2026-09-14, before S4.1 (pick T-005 + confirm RED).
- **Flaw:** T-005's completion gate (all 34 tests) could not be satisfied by T-005 alone. 5 of the 34 tests use T-006 **service** methods (called on the `FileService` instance, not the repository): `test_ac_001` (AC-001, `get_file`), `test_ac_014` (AC-014, `get_file`), `test_ac_026` (AC-026, `delete`/`download`/`get_file`/`list_files`), `test_ac_030` (AC-030, `delete`/`download`), `test_ac_050` (AC-050, `delete`/`download`). Since T-006 depends on T-005 (must be VERIFIED), this created a deadlock: T-005 could not be VERIFIED until those 5 tests passed, but they need T-006's `get_file`/`download`/`delete`/`list_files`. (Note: the other 29 T-005 tests use only **repository** methods (`repo.list_by_namespace`, etc.) which are T-004, already VERIFIED — so they are satisfiable by T-005 alone.)
- **Correction (decomposition fix, NOT a test weakening — all 5 tests preserved, only moved to the task that can make them pass):**
  - T-005: removed the 5 tests from `tests_to_create` (29 remain) and AC-001/AC-014/AC-026/AC-030/AC-050 from `acceptance_criteria` (19 remain); `completion_gates` updated to the 19 remaining ACs + the EDGE/INV gates.
  - T-006 (queries; depends on T-005, so `get_file`/`download`/`delete`/`list_files` are available): added the 5 tests to `tests_to_create` (20 total) and AC-001/AC-014/AC-026/AC-030/AC-050 to `acceptance_criteria` (14 total); the acceptance completion gate updated to the full 14-AC list.
  - Applied to both `.github/task-runner/tasks.json` and `docs/tasks/file-management.tasks.json` (kept in sync).
- **Rationale:** Same P-5/P-8 pattern — a task's completion gate must be satisfiable by that task alone. The 5 upload tests are written assuming the queries methods (`get_file`/`download`/`delete`/`list_files`) are available, but those are T-006. T-006 is the earliest task where they are satisfiable. This respects "tests are the contract" (no test is weakened nor deleted).
- **Guidance (reinforces P-5/P-8):** When decomposing a spec into a task DAG (S2.2), for EACH task verify that every test in `tests_to_create` can pass using ONLY that task's implementation plus its declared `dependencies` (already-VERIFIED tasks). Distinguish **service** methods (called on the `FileService` instance) from **repository** methods (called on the repository instance) — only the service methods of a LATER task create a deadlock. A task's completion gate must be satisfiable by that task alone.

## DAG Correction (T-004 gate, discovered in Phase 4)

- **When:** 2026-09-14, before S4.1 (pick T-004 + confirm RED).
- **Flaw:** T-004's completion gate ("Acceptance test for AC-025 passes" + "Unit tests for EDGE-010, EDGE-015 pass") could not be satisfied by T-004 alone. `test_edge_015_repo_creates_parent_dir` needs only `SqliteFileRepository` (T-004), but `test_ac_025_persistence_across_instances` needs `FileService.upload` (T-005) + `FileService.get_file` (T-006), and `test_edge_010_sequential_key_replacement` needs `FileService.upload` (T-005) + `FileService.download` (T-006). Since T-005 depends on T-004 (must be VERIFIED), this created a deadlock: T-004 could not be VERIFIED until `test_ac_025`/`test_edge_010` passed, but those need T-005/T-006.
- **Correction (decomposition fix, NOT a test weakening — both tests preserved, only moved to the task that can make them pass):**
  - T-004: `tests_to_create` → `[test_edge_015_repo_creates_parent_dir]`; `acceptance_criteria` → `[]` (AC-025 moved to T-006); `completion_gates` → `["Unit test for EDGE-015 passes"]`.
  - T-006 (queries; depends on T-005, so `upload` + `download`/`get_file` are available): added `test_ac_025_persistence_across_instances` + `test_edge_010_sequential_key_replacement` to `tests_to_create`, `AC-025` to `acceptance_criteria`, and updated the two completion gates to include AC-025 and EDGE-010.
  - Applied to both `.github/task-runner/tasks.json` and `docs/tasks/file-management.tasks.json` (kept in sync).
- **Rationale:** Same P-5 pattern — a task's completion gate must be satisfiable by that task alone. `test_ac_025`/`test_edge_010` can only pass after T-006, so T-006 is the earliest task where they are satisfiable. This respects "tests are the contract" (neither test is weakened nor deleted).

## DAG Correction (T-002 gate, discovered in Phase 4)

- **When:** 2026-09-13, during S4.1 (pick T-002 + confirm RED).
- **Flaw:** T-002's completion gate ("Acceptance tests for AC-052, AC-053 pass") could not be satisfied by T-002 alone. `test_ac_052_register_settings` needs only `register_settings` (T-002), but `test_ac_053_unregistered_settings_defaults` is an integration-level test that also requires `InMemoryStorageBackend` (T-003), `SqliteFileRepository` (T-004), `FileService.upload` (T-005), and `FileService.upload_avatar` (T-007). Since T-005 depends on T-002 (must be VERIFIED), this created a deadlock: T-002 could not be VERIFIED until `test_ac_053` passed, but `test_ac_053` needs T-005/T-007.
- **Correction (decomposition fix, NOT a test weakening — `test_ac_053` is preserved, only moved to the task that can make it pass):**
  - T-002: `tests_to_create` → `[test_ac_052_register_settings]`; `acceptance_criteria` → `[AC-052]`; `completion_gates` → `["Acceptance test for AC-052 passes"]`.
  - T-008 (final cross-cutting task; depends on T-006 + T-007, so the full stack is available): added `test_ac_053_unregistered_settings_defaults` to `tests_to_create`, `AC-053` to `acceptance_criteria`, and `"Acceptance test for AC-053 passes"` to `completion_gates`.
  - Applied to both `.github/task-runner/tasks.json` and `docs/tasks/file-management.tasks.json` (kept in sync).
- **Rationale:** DAG ordering is T-001 → (T-002, T-003, T-004) → T-005 → (T-006, T-007) → T-008. `test_ac_053` can only pass after T-007, so T-008 is the earliest task where it is satisfiable. This respects "tests are the contract" (the test is neither weakened nor deleted).

## Phase 4 — Implement (T-003)

- **Step:** S4.5 (commit + update status), for task T-003, 2026-09-13.
- **T-003 scope:** storage backends — `src/backend/filemanagement/storage.py`:
  - `StorageBackend` ABC: `put(key, data: bytes | BinaryIO)` (atomically write the content to key, replacing any existing content — last-write-wins; `StorageError` reason `io` | `symlink` | `path_escape`), `get(key) -> BinaryIO` (file-like stream of the content; reason `not_found` if the key is absent), `delete(key)` (no-op if the key is absent), `exists(key) -> bool`, `stat(key) -> StorageStat | None` (D1, ADR-050).
  - `LocalDiskStorageBackend(root: Path)`: flat layout (one file per key directly under root, the key is the filename); KEY_PATTERN enforcement (a violating key → `StorageError` reason `path_escape`); resolved-path containment (a path resolving outside root → `StorageError` reason `path_escape`); symlink rejection at the target path or any path component (reason `symlink`, never followed); `put` writes to a temp file (`mkstemp`) then `os.replace` (atomic rename, last-write-wins) (D4, D5, D13, ADR-050, ADR-053).
  - `InMemoryStorageBackend`: a dict of key → bytes; public for tests/DI; instances are isolated (no shared state between instances) (REQ-015, EDGE-016).
  - `StorageStat` (size, updated_at). Re-exported from `src/backend/filemanagement/__init__.py`. Committed as `8c22d0d`.
- **Q-33 test fix (separate commit):** `161f772` — suppresses the `function_scoped_fixture` health check in all 8 property tests (false-positive health-check signal; no assertion changes).
- **GREEN confirmed (T-003 gate — "Acceptance tests for AC-031, AC-032 pass"; "Unit test for EDGE-016 passes"; "Property test for INV-007 passes"):**
  - `test_ac_032_path_escape_rejected` PASSED (AC-032), `test_edge_016_in_memory_isolation` PASSED (EDGE-016), `test_inv_007_key_containment` PASSED (INV-007), `test_ac_031_symlink_rejected` SKIPPED — symlinks unavailable on this host (WinError 1314), acceptable per task (AC-031). Summary: **3 passed, 1 skipped**.
  - Note: the task's full-suite `green_command` (`uv run pytest tests/acceptance/filemanagement/ tests/property/filemanagement/ tests/unit/filemanagement/ tests/contract/filemanagement/ tests/integration/filemanagement/ -v`) is NOT expected to be fully green at this point — later tasks T-004..T-008 are unimplemented, so their tests still fail with the unimplemented signal. The T-003 completion gates are the AC-031/AC-032 acceptance tests, the EDGE-016 unit test, and the INV-007 property test, which pass (AC-031 skipped as host-acceptable).
- **Ruff:** repo-wide `uv run ruff check .` → 23 errors, all pre-existing `I001` import-sort errors in `tests/**/mail/**` (same set recorded in Phase 3; out of scope). File-management paths (`src/backend/filemanagement/` + all five `tests/**/filemanagement/` test directories) → **All checks passed** (0 errors; no new errors introduced by T-003).
- **Task status:** `SPECIFIED → VERIFIED` for T-003 in both `.github/task-runner/tasks.json` and `docs/tasks/file-management.tasks.json` (synced), committed together with this evidence.

## Phase 4 — Implement (T-004)

- **Step:** S4.5 (commit + update status), for task T-004, 2026-09-14.
- **T-004 scope:** metadata repository — `src/backend/filemanagement/repository.py`:
  - `FileRepository` ABC: `add`, `get_by_key`, `get_by_id`, `update`, `delete`, `list_by_namespace`, `set_user_avatar`, `get_user_avatar`, `clear_user_avatar`.
  - `SqliteFileRepository`: auto-creates the DB file's parent directory (EDGE-015), bootstraps tables via `SQLModel.metadata.create_all`, thread-safe SQLite (per-thread connections), atomic same-key replacement in `add`, `list_by_namespace` (prefix match + `created_at` ordering + limit/offset pagination), user→avatar mapping.
  - Both classes traced via `@logged_class(slow_threshold_ms=100)`. Re-exported from `src/backend/filemanagement/__init__.py`. Committed as `7966c40`.
- **Gate (NARROWED by DAG correction P-8):** "Unit test for EDGE-015 passes." `test_ac_025_persistence_across_instances` + `test_edge_010_sequential_key_replacement` were moved to T-006 (see "DAG Correction (T-004 gate, discovered in Phase 4)").
- **GREEN confirmed (T-004 gate — "Unit test for EDGE-015 passes"):**
  - `uv run pytest tests/unit/filemanagement/test_filemanagement_edges.py::test_edge_015_repo_creates_parent_dir -v` → `tests/unit/filemanagement/test_filemanagement_edges.py::test_edge_015_repo_creates_parent_dir PASSED [100%]` — **1 passed in 0.16s**.
  - Note: the task's full-suite `green_command` (`uv run pytest tests/acceptance/filemanagement/ tests/property/filemanagement/ tests/unit/filemanagement/ tests/contract/filemanagement/ tests/integration/filemanagement/ -v`) is NOT expected to be fully green at this point — later tasks T-005..T-008 are unimplemented, so their tests still fail with the unimplemented signal. The T-004 completion gate is specifically the EDGE-015 unit test, which passes.
- **Ruff:** repo-wide `uv run ruff check .` → 23 errors, all pre-existing `I001` import-sort errors in `tests/**/mail/**` (same set recorded in Phase 3; out of scope). File-management paths (`src/backend/filemanagement/` + all five `tests/**/filemanagement/` test directories) → **All checks passed** (0 errors; no new errors introduced by T-004).
- **Task status:** `SPECIFIED → VERIFIED` for T-004 in both `.github/task-runner/tasks.json` and `docs/tasks/file-management.tasks.json` (synced), committed together with this evidence.

## Phase 4 — Implement (T-005)

- **Step:** S4.2 (implement + confirm GREEN), for task T-005, 2026-09-14.
- **T-005 scope:** `FileService.upload` — `src/backend/filemanagement/service.py`:
  - `FileService(repository, backend=None, event_bus=None, settings_registry=None)`; `upload(source, key=None, namespace="general", declared_mime_type=None, original_filename=None, uploader=None) -> FileRecord`.
  - Behavior per T-005 implementation_steps: key/namespace pattern validation (traversal/null-byte/absolute-path rejected), live max-file-size limit (general vs avatar), zero-byte rejection, magic-byte content detection via `filetype` + text fallback (ADR-048 amendment; `python-magic` unusable on host), declared-type conflict rejection, filename-type conflict rejection, live allowed-type set enforcement, generated UUID key when omitted, atomic write with mutual rollback (storage content rolled back on metadata failure and vice versa), `FileUploaded` / `FileValidationFailed` events (best-effort; a publisher failure never breaks the operation), `@logged_class(slow_threshold_ms=5000, include_args=False)` traced.
  - `__init__.py`: re-exports the real `FileService` (the `NotImplementedError` placeholder removed).
  - **T-004 fix (discovered in S4.2):** `SqliteFileRepository.add` same-key replacement now uses an immediate bulk `delete` statement (`session.execute(delete(...))`), which executes before the deferred insert flushes. The previous ORM pattern (deferred `session.delete` + deferred `session.add` in one commit) flushed the insert first → `IntegrityError` (UNIQUE `files.key`) even for sequential replacement, violating the ADR-054 no-error atomic-replacement contract. T-004's gate (EDGE-015 only) never exercised the replacement path, so the bug was latent. The bounded service-side retry (`_persist_record`, `_ADD_ATTEMPTS`) is kept as defense for the true inter-connection race (the winner committing between the loser's delete and insert).
  - **Dependency:** `pillow>=10.0.0` added (`pyproject.toml`, `uv.lock`) — image decode validation (spec REQ-019 dependency; the approved spec lists Pillow; the test helper `png_bytes` imports PIL).
  - Committed as `a4d75c0`.
- **Gate (NARROWED by DAG correction P-9):** the 29 T-005 tests = `tests_to_create` in `.github/task-runner/tasks.json` (AC-002..AC-013, AC-015..AC-018, AC-024, AC-029, AC-049 + EDGE-001..EDGE-005, EDGE-014, EDGE-019 + INV-001..INV-003). The 5 upload tests moved to T-006 (see "DAG Correction (T-005 gate, discovered in Phase 4)").
- **GREEN confirmed (T-005 gate — all 29 tests):**
  - `uv run pytest` (29 node IDs: 19 acceptance in `tests/acceptance/filemanagement/test_filemanagement.py`, 7 unit in `tests/unit/filemanagement/test_filemanagement_edges.py`, 3 property in `tests/property/filemanagement/test_filemanagement_properties.py`) → **31 passed in 4.52s** (29 test functions; 2 are parameterized into 2 items each — all PASS, 0 failed).
  - Regression check (T-004 fix touched `repository.py`): `test_edge_015_repo_creates_parent_dir` PASSED. The 4 failing contract tests (`test_nfr_001/003/004/005`) are owned by T-008 (status SPECIFIED, unimplemented) — pre-existing RED, not a regression.
- **Ruff:** `uv run ruff check src/backend/filemanagement/` → **All checks passed**; `uv run ruff format --check src/backend/filemanagement/` → 8 files already formatted.
- **Task status:** `SPECIFIED → GREEN` for T-005 (S4.2 done; S4.3/S4.4/S4.5 follow).

## Phase 4 — Implement (T-006)

- **Step:** S4.2 (implement + confirm GREEN), for task T-006, 2026-09-14.
- **T-006 scope:** `FileService` query methods — `src/backend/filemanagement/service.py`:
  - `download(key) -> bytes` (record lookup → `backend.get` → read+close → publish `FileDownloaded`), `open(key) -> BinaryIO` (file-like stream, usable as a context manager), `delete(key)` (record lookup → `backend.delete` no-op if content missing → `repository.delete` → publish `FileDeleted`), `get_file(key) -> FileRead`, `list_files(namespace=None, limit=100, offset=0) -> list[FileRead]` (pagination validation `limit >= 1` / `offset >= 0` else `ValueError`).
  - Behavior per T-006 implementation_steps/design_constraints: missing file → `FileManagementNotFoundError`; record without content → `StorageError(reason='not_found')` and NOT auto-deleted (EDGE-006); delete of a file whose content is already missing still deletes the record (storage delete no-op, EDGE-007); a download concurrent with a same-key upload returns a complete file, never partial (EDGE-017).
  - `upload` and the content-detection logic (T-005) were NOT modified. Committed as `4772a94`.
- **Gate:** the 20 T-006 tests = `tests_to_create` in `.github/task-runner/tasks.json` (EDGE-006..EDGE-009, EDGE-010, EDGE-017 + AC-001, AC-014, AC-019..AC-023, AC-025..AC-028, AC-030, AC-048, AC-050). No deadlock (T-006's tests use only T-005 `upload` + T-006 methods; no T-007/T-008 methods).
- **GREEN confirmed (T-006 gate — all 20 tests):** `uv run pytest` (20 node IDs: 14 acceptance, 6 unit) → **20 passed in 1.05s** (0 failed).
- **Ruff:** `uv run ruff check src/backend/filemanagement/` → All checks passed; `ruff format` applied + `--check` clean.
- **Task status:** `SPECIFIED → VERIFIED` for T-006 (both task files).

## Dependency Replacement (python-magic → filetype, discovered in Phase 4)

- **When:** during T-005 S4.2 (FileService.upload), 2026-09-14. The T-005 implementation subagent deadlocked probing `python-magic` (`import magic` → segfault exit 139; `magic.loader.load_lib()` → hang/timeout). The user directed the replacement ("If python-magic has problem replace it").
- **Root cause:** `python-magic` (libmagic bindings) is unusable on the Windows host — no bundled libmagic, and loading it either segfaults or deadlocks.
- **Replacement:** the pure-Python `filetype` package (magic-byte detection: `filetype.guess_mime(data)` → MIME type or `None`) **plus a text fallback** in the implementation: text content (no null bytes in the leading 8 KiB) → `text/plain`; unidentified binary → `application/octet-stream`. This preserves the spec's behavior (magic-byte detection as the source of truth, conflicting signals rejected); only the library changes.
- **Verified on host:** `filetype` detects the types the spec's acceptance criteria exercise — image/png, image/jpeg, image/webp, image/gif, application/pdf, application/zip — and the text fallback yields text/plain for `text_bytes(n)` (= `b"x" * n`). `puremagic` was evaluated and rejected (2.x returns extensions, not MIME types, and raises for unidentified content).
- **Spec drift:** `docs/specs/file-management.md` names `python-magic` (REQ-004, REQ-005, D3). The normative behavior is preserved; only the library name is now stale. A spec-amendment rename is deferred (the behavior, not the library name, is what the spec governs).
- **Recorded in:** ADR-048 (amended), `pyproject.toml` (`filetype>=1.2.0`; `python-magic` removed), `uv.lock`.

## Evidence

- Phase 1 (Specify): spec committed, PR #24 opened + merged on human delegation (see "Phase 1 — Spec approval").
- Phase 3 (Test & RED): 90 tests derived from the spec, RED confirmed (`ModuleNotFoundError: backend.filemanagement`, pytest exit 4), ruff clean on the new files (see "Phase 3 — Test & RED").
- Phase 4 (Implement, T-001): foundation (errors, events, models) committed as `c6b70c0`; AC-051 acceptance test `test_ac_051_error_hierarchy_context` PASSED (GREEN); ruff clean on file-management paths (23 pre-existing mail `I001`s remain, out of scope); task status `VERIFIED` in both task files (see "Phase 4 — Implement (T-001)").
- Phase 4 (Implement, T-002): feature settings registration (`feature_settings.py` — `register_settings`, 5 `SettingDefinition`s, live-read pattern, no import side effects) committed as `65425e0`; AC-052 acceptance test `test_ac_052_register_settings` PASSED (GREEN; gate NARROWED by P-5 — AC-053 / `test_ac_053` moved to T-008); ruff clean on file-management paths (23 pre-existing mail `I001`s remain, out of scope); task status `VERIFIED` in both task files (see "Phase 4 — Implement (T-002)").
- Phase 4 (Implement, T-003): storage backends (`storage.py` — `StorageBackend` ABC, `LocalDiskStorageBackend` (flat layout, KEY_PATTERN → `path_escape`, symlink rejection → `symlink`, resolved-path containment → `path_escape`, atomic `put` via `mkstemp`+`os.replace`, last-write-wins), `InMemoryStorageBackend` (dict, public, instance-isolated), `StorageStat`) committed as `8c22d0d`; Q-33 test fix (suppress `function_scoped_fixture` in all 8 property tests) committed as `161f772`; gate: AC-032 / EDGE-016 / INV-007 PASSED, AC-031 SKIPPED (symlinks unavailable on this host — WinError 1314, acceptable per task); ruff clean on file-management paths (23 pre-existing mail `I001`s remain, out of scope); task status `VERIFIED` in both task files (see "Phase 4 — Implement (T-003)").
- Phase 4 (Implement, T-004): metadata repository (`repository.py` — `FileRepository` ABC (`add`/`get_by_key`/`get_by_id`/`update`/`delete`/`list_by_namespace`/`set_user_avatar`/`get_user_avatar`/`clear_user_avatar`), `SqliteFileRepository` (auto-creates the DB file's parent directory, `create_all` bootstrap, thread-safe SQLite, atomic same-key replacement in `add`, `list_by_namespace` prefix match + `created_at` ordering + limit/offset pagination, user→avatar mapping), both traced via `@logged_class(slow_threshold_ms=100)`) committed as `7966c40`; EDGE-015 unit test `test_edge_015_repo_creates_parent_dir` PASSED (GREEN; gate NARROWED by P-8 — `test_ac_025` + `test_edge_010` moved to T-006); ruff clean on file-management paths (23 pre-existing mail `I001`s remain, out of scope); task status `VERIFIED` in both task files (see "Phase 4 — Implement (T-004)").
