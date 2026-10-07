# Workflow Problems (Friction Log)

Persistent record of **problems that take a lot of time** (friction points) during the workflow. This file is the feedback loop for the **after-workflow-optimization**: the workflow logs its friction here, and the optimization (a meta-task) reads this file to know where the friction was and to improve the workflow.

## When problems are logged

A step MUST log a problem when it:
- (a) fails and is relaunched,
- (b) takes more than one iteration to complete,
- (c) is blocked on a non-trivial user decision, or
- (d) takes disproportionately long relative to its objective.

**Who logs:** the orchestrator (it sees the relaunches, iterations, and blocks). A step subagent flags a problem in its handoff (`status: FAILED` with reason, or the `problem` field); the orchestrator records it here.

## Entry format

```markdown
## P-<n> — <short title>
- **Problem:** <what happened>
- **Step / Phase:** <step ID + phase> (e.g., S4.2 Implement — Phase 4)
- **Change:** <change name + type>
- **Duration / iterations:** <how long / how many iterations>
- **Resolution:** <how it was resolved>
- **Date:** <YYYY-MM-DD>
```

## Problems

## P-10 — T-004 latent bug: SqliteFileRepository.add broken for sequential same-key replacement (discovered in T-005)
- **Problem:** `SqliteFileRepository.add` was broken even for **sequential** same-key replacement. The ORM pattern (deferred `session.delete` + deferred `session.add` in one commit) flushed the INSERT before the DELETE → `IntegrityError` (UNIQUE `files.key`) → rollback, violating the ADR-054 no-error atomic-replacement contract. T-004's gate (EDGE-015 only) never exercised the replacement path, so the bug was latent — it surfaced only when T-005's `upload` exercised same-key replacement. Fixed minimally in T-005 S4.2: the same-key deletion is now an immediate bulk `delete` statement (executes before the deferred insert flushes); the bounded service-side retry (`_persist_record`) is kept for the true inter-connection race.
- **Step / Phase:** S4.2 (T-005 implement + confirm GREEN) — Phase 4 (T-005); latent bug in T-004 (`repository.py`)
- **Change:** file-management / FEATURE
- **Duration / iterations:** 1 iteration (caught during T-005 GREEN; T-004 regression test re-confirmed)
- **Resolution:** T-004 `repository.py` fixed (immediate bulk delete for same-key replacement); T-004 regression test `test_edge_015_repo_creates_parent_dir` re-confirmed PASSED; T-005 29/29 tests GREEN. Committed as `a4d75c0`.
- **Date:** 2026-09-14
- **Status:** Solved (2026-09-15) — `.agents/skills/decompose/SKILL.md` (narrowed gate coverage note).

## P-9 — DAG decomposition flaw (3rd instance): T-005 gate included 5 upload tests using T-006 service methods (get_file/download/delete/list_files) (deadlock)
- **Problem:** T-005's completion gate (all 34 tests) could not be satisfied by T-005 alone. 5 tests use T-006 **service** methods (called on the `FileService` instance): `test_ac_001` (AC-001, `get_file`), `test_ac_014` (AC-014, `get_file`), `test_ac_026` (AC-026, `delete`/`download`/`get_file`/`list_files`), `test_ac_030` (AC-030, `delete`/`download`), `test_ac_050` (AC-050, `delete`/`download`). Since T-006 depends on T-005 being VERIFIED, this created a deadlock. The other 29 T-005 tests use only **repository** methods (`repo.list_by_namespace`, etc.) which are T-004 (already VERIFIED), so they are satisfiable by T-005 alone. Root cause (same as P-5/P-8): the Phase 2 (S2.2) decomposition wrote the upload tests (T-005) assuming the queries service methods (T-006) are available, and assigned them to T-005 without checking that the tests' runtime dependencies (T-006) were available at that task.
- **Step / Phase:** before S4.1 (pick T-005 + confirm RED) — Phase 4 (T-005); root cause in Phase 2 (S2.2 Decompose)
- **Change:** file-management / FEATURE
- **Duration / iterations:** 1 iteration (caught before S4.1, so no rework)
- **Resolution:** DAG correction (decomposition fix, NOT a test weakening — all 5 tests preserved, only moved): T-005 removed the 5 tests (29 remain) + AC-001/AC-014/AC-026/AC-030/AC-050 (19 ACs remain); T-006 (queries, depends on T-005 so get_file/download/delete/list_files available) took on the 5 tests (20 total) + the 5 ACs (14 total). Applied to both task files. Recorded in `docs/verification/file-management.md` ("DAG Correction (T-005 gate)").
- **Guidance (reinforces P-5/P-8):** When decomposing a spec into a task DAG (S2.2), for EACH task verify that every test in `tests_to_create` can pass using ONLY that task's implementation plus its declared `dependencies` (already-VERIFIED tasks). Distinguish **service** methods (called on the `FileService` instance) from **repository** methods (called on the repository instance) — only the service methods of a LATER task create a deadlock. A task's completion gate must be satisfiable by that task alone. For the file-management feature specifically: the upload tests (T-005) that verify via `get_file`/`download`/`delete`/`list_files` (T-006) must be assigned to T-006, not T-005.
- **Date:** 2026-09-14
- **Status:** Solved (2026-09-15) — `.agents/skills/decompose/SKILL.md` (DAG validation step).

## P-8 — DAG decomposition flaw (2nd instance): T-004 gate included service-level tests (test_ac_025, test_edge_010) needing T-005/T-006 (deadlock)
- **Problem:** T-004's completion gate ("Acceptance test for AC-025 passes" + "Unit tests for EDGE-010, EDGE-015 pass") could not be satisfied by T-004 alone. `test_ac_025_persistence_across_instances` needs `FileService.upload` (T-005) + `FileService.get_file` (T-006); `test_edge_010_sequential_key_replacement` needs `FileService.upload` (T-005) + `FileService.download` (T-006). Only `test_edge_015_repo_creates_parent_dir` needs T-004 alone (`SqliteFileRepository`). Since T-005 depends on T-004 being VERIFIED, this created a deadlock. Root cause (same as P-5): the Phase 2 (S2.2) decomposition wrote the repository tests (REQ-013) at the SERVICE level (using upload/download) rather than the repository level, and assigned them to the repository task without checking that the tests' runtime dependencies (T-005/T-006) were available at that task.
- **Step / Phase:** before S4.1 (pick T-004 + confirm RED) — Phase 4 (T-004); root cause in Phase 2 (S2.2 Decompose)
- **Change:** file-management / FEATURE
- **Duration / iterations:** 1 iteration (caught before S4.1, so no rework)
- **Resolution:** DAG correction (decomposition fix, NOT a test weakening — both tests preserved, only moved): T-004 narrowed to `[test_edge_015_repo_creates_parent_dir]` / `acceptance_criteria []` / gate `"Unit test for EDGE-015 passes"`; T-006 (queries, depends on T-005 so upload+download available) took on `test_ac_025` / `test_edge_010` / `AC-025` / gates for AC-025 + EDGE-010. Applied to both task files. Recorded in `docs/verification/file-management.md` ("DAG Correction (T-004 gate)").
- **Guidance (reinforces P-5):** When decomposing a spec into a task DAG (S2.2), for EACH task verify that every test in `tests_to_create` can pass using ONLY that task's implementation plus its declared `dependencies` (already-VERIFIED tasks). A common trap: writing a foundation task's tests (e.g., a repository) at the SERVICE level (using upload/download) when the service is implemented in a LATER task — such a test must be assigned to the earliest task where all its runtime dependencies are available (typically the task that implements the service's read path). A task's completion gate must be satisfiable by that task alone.
- **Date:** 2026-09-14
- **Status:** Solved (2026-09-15) — `.agents/skills/decompose/SKILL.md` (DAG validation step).

## P-7 — S4.1 (T-003) subagent ended prematurely (no handoff) + surfaced a Hypothesis health-check error on test_inv_007
- **Problem:** The T-003 S4.1 subagent (confirm RED) ended after 10 tool uses returning an intermediate sentence ("Let me examine the property test that failed with a health check error (not the unimplemented signal).") instead of a structured handoff — the same premature-end failure mode as P-3. The useful signal it surfaced before ending: 3 of the 4 T-003 tests (test_ac_031, test_ac_032, test_edge_016) are clean unimplemented-signal REDs, but the property test `test_inv_007_key_containment` failed with a **Hypothesis health-check error** rather than the unimplemented signal. This needs investigation: either the health check is masking the unimplemented signal (acceptable RED), or the test's `key` strategy is genuinely problematic (a test bug that must be flagged, not fixed by weakening).
- **Step / Phase:** S4.1 Pick task + confirm RED — Phase 4 (T-003)
- **Change:** file-management / FEATURE
- **Duration / iterations:** 1 iteration (relaunched with a fresh subagent)
- **Resolution / guidance:** Relaunched S4.1 (T-003) with a fresh subagent, instructed to (a) confirm the 3 non-property tests are clean unimplemented-signal REDs, and (b) investigate the test_inv_007 health-check error — determine whether it masks the unimplemented signal (acceptable) or is a genuine strategy/test issue (flag as a finding). For future steps: a step subagent MUST end with the structured handoff even when it hits an unexpected failure — record the failure in the handoff (`status: FAILED` with the exact output) rather than ending mid-investigation.
- **Date:** 2026-09-13
- **Status:** Solved (2026-09-15) — AGENTS.md (completion guard rule).

## P-6 — Repo-wide `ruff check --fix .` + `ruff format .` modifies out-of-scope files (conflicts with "commit only this task's files")
- **Problem:** The T-002 implementation subagent (Phase 4) ran the prescribed whole-repo ruff gate (`uv run ruff check --fix .` + `uv run ruff format .`). It modified 51 out-of-scope files (including fixing the 23 pre-existing mail `I001`s and reformatting 28 files) and the reformat of `tests/property/mail/test_secrets.py` introduced 4 NEW `RUF001`/`RUF100` errors (a line-level `# noqa: RUF001` was lost when the noqa list was split across lines). The subagent had to revert ALL out-of-scope changes to restore the expected end state (23 pre-existing mail I001s + clean tree) before committing only the 2 task files. This wasted tool calls and time and is a recurring trap: the P-4 guidance ("use `ruff --fix`") is correct for the TASK's files but wrong when applied repo-wide against a "commit only this task's files" + "clean tree" expectation.
- **Step / Phase:** S4.3 Ruff — Phase 4 (T-002)
- **Change:** file-management / FEATURE
- **Duration / iterations:** 1 iteration (subagent recovered by reverting out-of-scope changes; no rework of the task)
- **Resolution / guidance (for future steps):** Step subagents that write or modify tests/implementation MUST scope the ruff gate to the TASK's changed paths, not the whole repo: run `uv run ruff check --fix <task-changed-paths>` + `uv run ruff format <task-changed-paths>` (e.g., `uv run ruff check --fix src/backend/filemanagement/feature_settings.py src/backend/filemanagement/__init__.py`), then verify with `uv run ruff check .` (expect only the known pre-existing out-of-scope errors). Do NOT run repo-wide `ruff --fix`/`ruff format` during a task step — if repo-wide lint fixes are desired, they are a separate, explicit step (or handled in the verify phase). The orchestrator's task-definitions for implementation/test steps MUST state this ("scope `ruff check --fix`/`ruff format` to the task's changed paths; do not run repo-wide").
- **Date:** 2026-09-13
- **Status:** Solved (2026-09-15) — AGENTS.md (Ruff gate: scoped `--fix`, no repo-wide during a task).

## P-5 — DAG decomposition flaw: T-002 gate included an integration test needing T-005/T-007 (deadlock)
- **Problem:** T-002's completion gate ("Acceptance tests for AC-052, AC-053 pass") could not be satisfied by T-002 alone. `test_ac_053_unregistered_settings_defaults` is an integration-level test requiring `InMemoryStorageBackend` (T-003), `SqliteFileRepository` (T-004), `FileService.upload` (T-005), and `FileService.upload_avatar` (T-007) — but T-005 depends on T-002 being VERIFIED. This created a deadlock: T-002 could not be VERIFIED until `test_ac_053` passed, but `test_ac_053` needed T-005/T-007. Root cause: the Phase 2 (S2.2) decomposition assigned an integration-level test to a foundation task without checking that the test's runtime dependencies were all available at that task.
- **Step / Phase:** S4.1 Pick task + confirm RED — Phase 4 (T-002); root cause in Phase 2 (S2.2 Decompose)
- **Change:** file-management / FEATURE
- **Duration / iterations:** 1 iteration (caught at S4.1 before implementation, so no rework)
- **Resolution:** DAG correction (decomposition fix, NOT a test weakening — `test_ac_053` preserved, only moved): T-002 narrowed to `[test_ac_052_register_settings]` / `[AC-052]` / gate `"Acceptance test for AC-052 passes"`; T-008 (final task, full stack available) took on `test_ac_053` / `AC-053` / gate `"Acceptance test for AC-053 passes"`. Applied to both task files. Recorded in `docs/verification/file-management.md` ("DAG Correction").
- **Guidance (for future decompositions):** When decomposing a spec into a task DAG (S2.2), for EACH task verify that every test in `tests_to_create` can pass using ONLY that task's implementation plus its declared `dependencies` (already-VERIFIED tasks). If a test needs a component implemented in a LATER task, assign the test to the earliest task where all its runtime dependencies are available (typically the final cross-cutting task). A task's completion gate must be satisfiable by that task alone — otherwise it deadlocks the DAG.
- **Date:** 2026-09-13
- **Status:** Solved (2026-09-15) — `.agents/skills/decompose/SKILL.md` (DAG validation step).

## P-4 — Subagent probed/guessed at a ruff issue instead of using `ruff --fix`
- **Problem:** The T-001 implementation subagent (Phase 4) spent tool calls probing/guessing at a ruff issue (probing the project's import-sort/classification behavior with minimal files) instead of just applying the fix. ruff has an auto-fix for most lint issues (import sorting, unused imports, formatting); the subagent should have run `uv run ruff check --fix .` (and `uv run ruff format .`) rather than diagnosing by hand.
- **Step / Phase:** S4.3 Ruff — Phase 4 (T-001)
- **Change:** file-management / FEATURE
- **Duration / iterations:** 1 iteration (subagent stopped by user mid-probe)
- **Resolution / guidance (for future steps):** Step subagents that write or modify tests/implementation MUST run `uv run ruff check --fix .` + `uv run ruff format .` (auto-fix) BEFORE diagnosing any lint issue by hand. Only if `ruff --fix` does not resolve an issue (or the issue is not auto-fixable) should the subagent investigate. The orchestrator's task-definitions for implementation/test steps MUST state this ("use `ruff check --fix .` + `ruff format .`; do not probe/guess at lint issues").
- **Date:** 2026-09-13
- **Status:** Solved (2026-09-15) — AGENTS.md (Ruff gate: scoped `--fix` to task's changed paths).

## P-2 — S1.1 BLOCKED-USER resume unavailable after subagent retention window
- **Problem:** S1.1 returned BLOCKED-USER (28 questions). The orchestrator completed the user round-trips (7 batches + 1 re-ask + user-initiated Q-29), recorded all answers in AI_Questions.md, and attempted to resume the BLOCKED-USER subagent to complete the step — but the subagent's session had been released after its retention window ("resume is unavailable"). Per the workflow, a non-returning subagent is re-entered with a fresh subagent for the same step.
- **Step / Phase:** S1.1 Interrogate — Phase 1
- **Change:** file-management / FEATURE
- **Duration / iterations:** 2 iterations (initial BLOCKED-USER run + fresh relaunch); ~7 user round-trips
- **Resolution:** relaunched a fresh S1.1 subagent with the recorded answers (it verifies all questions answered, reconciles the brief, and completes the step). Follow-up: the after-workflow-optimization should consider (a) a shorter retention window for BLOCKED-USER subagents, or (b) letting the orchestrator record answers and mark the step done directly when the only remaining work is verification of recorded answers.
- **Date:** 2026-09-13
- **Status:** Solved (2026-09-15) — AGENTS.md (BLOCKED-USER retention rule).

## P-3 — S1.3 subagent ended prematurely (no handoff)
- **Problem:** The S1.3 Verify self-consistency subagent completed after only 3 tool uses and returned an intermediate statement ("I've read the first part of the spec. Let me read the remainder.") instead of the structured handoff. It did not finish the Self-Consistency Checklist or commit. The spec file was left in the working tree (untracked).
- **Step / Phase:** S1.3 Verify self-consistency — Phase 1
- **Change:** file-management / FEATURE
- **Duration / iterations:** 1 failed run + fresh relaunch
- **Resolution:** relaunched a fresh S1.3 subagent for the same step (it reads the current spec, runs the full checklist, fixes inconsistencies, and commits). Follow-up: the after-workflow-optimization should consider a completion guard for step subagents (a step that does not end with the structured handoff is treated as failed and relaunched).
- **Date:** 2026-09-13
- **Status:** Solved (2026-09-15) — AGENTS.md (completion guard rule).

## P-1 — S7.1 done-criteria ambiguous when local `main` lags `origin/main`
- **Problem:** `git branch -d feature/mail-service` emitted the warning "has been merged to 'refs/remotes/origin/feature/mail-service', but not yet merged to HEAD" because the local `main` ref (ff26c4d) lagged `origin/main` (which contains the PR #23 merge). Harmless, but the S7.1 done-criterion "the merge commit is present on `main`" is ambiguous: it must mean reachable from `origin/main` (after `git fetch`), not from the local `main` ref — otherwise a lagging local `main` makes a correct cleanup look incomplete.
- **Step / Phase:** S7.1 Post-merge cleanup — Post-merge
- **Change:** mail-service / FEATURE
- **Duration / iterations:** single run, no relaunch
- **Resolution:** verified against `origin/main` (`git merge-base --is-ancestor <merge-commit> origin/main`); cleanup completed correctly. Follow-up: amend the S7.1 done-criteria in AGENTS.md + git skill to say "reachable from `origin/main` (after fetch)" so future runs don't rely on the local `main` ref.
- **Date:** 2026-09-12
- **Status:** Solved (2026-09-15) — `.agents/skills/git/SKILL.md` (S7.1 done-criteria: "reachable from `origin/main` after fetch").

## P-14 — xdist parallel run fails on Windows: shared default settings repository (settings/values.yaml) file lock
- **Problem:** `uv run pytest tests/ -n auto` → 486 errors: `PermissionError [WinError 32]` in `YamlValueRepository.save` (`os.replace` on `settings/values.yaml` — file in use by another process). Root cause: multiple tests instantiate the shared default settings registry (`get_settings_registry()` → default `YamlValueRepository('settings')`) and all write the same repo-root `settings/values.yaml`; the concurrent replace collides under Windows file locking. Sequential runs pass. Also the cause of the transient untracked `settings/` directory (P-13). Violates the AGENTS.md rule "Test registries MUST pass an explicit isolated value repository".
- **Step / Phase:** Phase 5 (S5.1 full-suite run, xdist) — file-management; pre-existing (any xdist run)
- **Change:** file-management / FEATURE (discovered); pre-existing defect
- **Duration / iterations:** discovered during after-workflow coverage measurement (2026-09-15)
- **Resolution:** fixed in ISSUE change `issue/settings-test-isolation` (test fixtures pass an isolated `YamlValueRepository(tempdir)`); until then, run the suite sequentially on Windows.
- **Date:** 2026-09-15

## P-13 — Transient untracked `settings/` directory in repo root after pytest runs
- **Problem:** Any test run that instantiates the default settings registry writes runtime values to `settings/values.yaml` (repo root) via the default `YamlValueRepository('settings')`. The directory appears as untracked clutter (deleted as a transient artifact during the file-management run).
- **Step / Phase:** any test run (pre-existing)
- **Change:** file-management / FEATURE (discovered); pre-existing behavior
- **Duration / iterations:** recurring
- **Resolution:** root cause = P-14 (shared default repository in tests); fixed in `issue/settings-test-isolation`. Mitigation: `.gitignore` entry `settings/` (chore/tooling-hardening).
- **Date:** 2026-09-15

## P-12 — Subagent sessions restored/resumed with full context + no naming convention
- **Problem:** The orchestrator resumed/restored previously launched step subagents (e.g., "Implement T-001 (retry after Q-30/31/32)") — restored sessions carry full/stale context, wasting time and risking confusion; step subagents also had no consistent naming, making session lists hard to map to steps.
- **Step / Phase:** Phase 4 (S4.x retries) — file-management
- **Change:** file-management / FEATURE
- **Duration / iterations:** 3+ relaunches of the same step with restored sessions
- **Resolution:** AGENTS.md updated (chore/workflow-subagent-ergonomics): (a) the orchestrator never resumes/restores a previously launched subagent — every (re-)entry launches a new subagent (the BLOCKED-USER resume exception is removed; user answers go into the new launch prompt); (b) subagent description naming template `Sx.x: <short objective>` (include the task ID for per-task steps, e.g., `S4.2 (T-005): implement FileService.upload`).
- **Date:** 2026-09-15

## P-11 — S3.1 Derive tests took ~8h / 158 tool calls for one subagent
- **Problem:** A single S3.1 subagent derived all tests for the file-management spec (8 DAG tasks, ~55 ACs) — 158 tool calls, ~29185s. The step's scope (all tasks' tests) was too large for one subagent's context.
- **Step / Phase:** S3.1 Derive tests — Phase 3
- **Change:** file-management / FEATURE
- **Duration / iterations:** 1 run (completed, but disproportionately long)
- **Resolution:** AGENTS.md updated (chore/workflow-subagent-ergonomics): S3.1 is now per-task in the DAG — one fresh subagent derives one task's `tests_to_create`; S3.2 stays a single ruff+RED gate over the whole suite.
- **Date:** 2026-09-15

## P-15 — S5 subagent edit loop: verification section inserted ~180 times (session anomaly)
- **Problem:** The A:S5 (light verify) subagent for `workflow-subagent-ergonomics` got stuck in a loop: it repeatedly inserted the same `## Verification (Phase 5)` section into `docs/verification/workflow-subagent-ergonomics.md` (~180 times) before detecting the anomaly and deduplicating to a single section. The step took 22441.8s / 190 tool uses for a 3-check light verification.
- **Step / Phase:** S5 (light verify) — Phase 5
- **Change:** workflow-subagent-ergonomics / DOCS/CHORE
- **Duration / iterations:** 1 run (recovered by the subagent itself: file deduplicated, committed cleanly)
- **Resolution:** Handoff verified by the orchestrator (section count = 1; diff = 4 in-scope files; tree clean). Follow-up: (a) step subagents that edit a file MUST re-read it after the edit to verify the edit landed exactly once before the next tool call; (b) when a handoff reports a loop/anomaly, the orchestrator MUST verify artifact counts (e.g., `grep -c` on the section header) before marking the step complete.
- **Date:** 2026-09-15

## P-16 — S4.2 (T-002) subagent stopped mid-run by user request (no handoff) left complete uncommitted work
- **Problem:** The S4.2 (T-002) Implement subagent was stopped by user request after 6469.7s / 23 tool uses with no output/handoff. It left a complete, uncommitted implementation in the working tree (`src/backend/sessionmanagement/service.py` + `docs/verification/session-management.md`): all four revocation operations (`revoke_session`, `logout_all_sessions`, `logout_other_sessions`, `revoke_all_sessions`) plus the `_resolve_token` helper. Orchestrator re-ran T-002's 17 tests: **17/17 PASS** (GREEN) — the work was actually done, just not recorded/handed off.
- **Step / Phase:** S4.2 Implement — Phase 4 (T-002)
- **Change:** session-management / FEATURE
- **Duration / iterations:** 1 stopped run + 1 fresh relaunch (S4.2 T-002) to verify GREEN and record the handoff
- **Resolution:** Per the execution model (a subagent that does not return is a failed step; never resume a stuck one), the orchestrator logged this problem and relaunched S4.2 (T-002) with a fresh subagent to verify the in-tree implementation is GREEN, record evidence, and return the structured handoff. The in-tree work was preserved (not reverted).
- **Date:** 2026-09-18

## P-17 — S4.2 (T-004) subagent stopped mid-run (no handoff) left uncommitted cap-eviction implementation
- **Problem:** The S4.2 (T-004) Implement subagent stopped mid-run with no output/handoff. It left an uncommitted cap-eviction implementation in the working tree (`src/backend/sessionmanagement/service.py`: `DEFAULT_MAX_SESSIONS_PER_USER = 5`, the constructor `LoginSucceeded` subscription on the shared event bus, and the `_on_login_succeeded` handler) plus the S4.1 (T-004) RED record and the S3.1 (T-004) test-fix record in `docs/verification/session-management.md`, and the two-line test fix in `tests/acceptance/sessionmanagement/test_cap_eviction.py`. GREEN was never confirmed or recorded.
- **Step / Phase:** S4.2 (T-004 implement + confirm GREEN) — Phase 4 (T-004)
- **Change:** session-management / FEATURE
- **Duration / iterations:** 1 stopped run + 1 fresh relaunch (S4.2 T-004) to verify GREEN and record the handoff
- **Resolution:** Per the execution model (a subagent that does not return is a failed step; never resume a stuck one), the orchestrator logged this problem and relaunched S4.2 (T-004) with a fresh subagent to verify the in-tree implementation is GREEN, record evidence, and return the structured handoff. The in-tree work was preserved (not reverted).
- **Date:** 2026-09-18

## P-18 — T-004 test-contract bug: `test_edge_011` final assertion incompatible with spec-mandated token-path listing (discovered in S4.2 T-004 GREEN)
- **Problem:** `test_edge_011_cap_eviction_at_exact_cap` (derived in S3.1) has a final assertion incompatible with the spec-mandated token-path listing: `assert [e.session_id for e in token_entries] == [new_row.id]` compares the full 5-entry valid-session list (new session pinned first + the 4 other valid sessions, `created_at` descending) to the 1-element list `[new_row.id]`. No implementation satisfying REQ-006/AC-009/INV-005 can make the token path return a single entry, so T-004's GREEN gate (all 4 `tests_to_create` pass) was blocked by the test, not the implementation. The implementation correctly evicts the oldest and keeps the new session (EDGE-011/REQ-014) — the test's own preceding assertions (`oldest_row.id not in ids`, `second_oldest_row.id in ids`, `len(entries) == cap`) all pass.
- **Step / Phase:** S4.2 (T-004 implement + confirm GREEN) — Phase 4 (T-004); test-contract bug in S3.1-derived `tests/acceptance/sessionmanagement/test_cap_eviction.py`
- **Change:** session-management / FEATURE
- **Duration / iterations:** 1 iteration (caught during S4.2 (T-004) GREEN; routed to a fresh test-skill fix step)
- **Resolution:** The S4.2 (T-004) subagent flagged the bug precisely (line 143; correct assertion: `token_entries[0].session_id == new_row.id` — new session valid through the token path and pinned first, per REQ-006/INV-005). A fresh test-skill step re-derives ONLY that assertion line (mechanical alignment, not a weakening; the asserted EDGE-011/REQ-014 behavior is unchanged), then S4.2 (T-004) is re-entered for GREEN.
- **Date:** 2026-09-18

## P-19 — T-009 test-contract bug: 3 tests access `.id` on the tuple returned by `make_session` (discovered in S4.1 T-009 RED)
- **Problem:** Three T-009 tests fail with `AttributeError: 'tuple' object has no attribute 'id'` — the test helper `make_session` (tests/sessionmanagement_test_helpers.py) returns `tuple[Session, str]` = `(row, raw_token)`, and the tests build `rows = [make_session(...) ...]` (a list of tuples). They correctly unpack `_, token = rows[1]`, but then call `service.revoke_session(rows[0].id)` — `rows[0]` is a tuple, not a `Session`, so `.id` raises `AttributeError` at argument evaluation, BEFORE the feature code under test runs. The bug masks the real RED reason (unimplemented None-publisher/observability/tracing behavior). Affected: `tests/acceptance/sessionmanagement/test_events.py::test_ac_038_none_publisher_no_events_no_subscriptions`, `tests/acceptance/sessionmanagement/test_observability.py::test_ac_044_no_tokens_in_outputs`, `tests/acceptance/sessionmanagement/test_observability.py::test_nfr_004_traced_service_publishes_events`.
- **Step / Phase:** S4.1 (T-009 pick task + confirm RED) — Phase 4 (T-009); test-contract bug in S3.1-derived tests
- **Change:** session-management / FEATURE
- **Duration / iterations:** 1 iteration (caught during S4.1 (T-009) RED; routed to a fresh test-skill fix step)
- **Resolution:** A fresh test-skill step fixes ONLY the tuple access in the 3 tests (mechanical alignment, not a weakening; the asserted AC-038/AC-044/NFR-004 behavior is unchanged): `rows[0].id` → `rows[0][0].id` (access the `Session` object from the tuple). After the fix, S4.1 (T-009) is re-entered to confirm the real RED reason.
- **Date:** 2026-09-19

## P-20 — Pre-existing broken test in baseline suite: `test_ac_045_traced_methods_no_tokens_in_logs` HANGS (discovered at REFACTOR baseline)
- **Problem:** Pre-existing broken test(s) in the baseline suite — 1 failing test, a HANG (never completes within the 300 s cap, even in isolation): `tests/acceptance/sessionmanagement/test_observability.py::test_ac_045_traced_methods_no_tokens_in_logs`. The test body is a simple synchronous assertion sequence; the hang is in its fixture/service interaction (the session-management service publishes events to the event-bus background worker; the run never returns). All other 616 tests in the full suite PASS (1 skipped: `test_ac_031_symlink_rejected` — symlinks not available on this host).
- **Step / Phase:** S1 (Phase 1 REFACTOR baseline) — dependency-updates
- **Change:** dependency-updates / REFACTOR
- **Duration / iterations:** 1 (discovered at baseline)
- **Resolution:** marked BROKEN per user instruction (2026-09-16) — out of scope for dependency-updates; baseline = "GREEN except the marked broken tests"; Phase 4/5 invariant = no NEW failures beyond these marked tests (they may remain broken; do not fix them in this change).
- **Date:** 2026-09-16

## P-21 — Phase 4 (minimal fix) subagent looped 30 min; root cause was misdiagnosed as a queue deadlock (it is an infinite loop in the test's assertion loop)
- **Problem:** The Phase 4 (minimal fix → GREEN) subagent for hanging-observability-test ran ~1803.9s / 24 tool uses and was stopped by the user ("the subagent was in an endless loop"). It left an uncommitted test-side fix in `tests/conftest.py` (`_reconfigure_file_sink_non_enqueued`, +32 lines) that reconfigures the `enqueue=True` file sink to non-enqueued after `setup_logger()`. That fix does NOT make the test pass — the test still hangs (exit 124 under timeout).
- **Step / Phase:** Phase 4 (minimal fix → GREEN) — hanging-observability-test / ISSUE
- **Change:** hanging-observability-test / ISSUE
- **Duration / iterations:** 1 failed run (30 min) + orchestrator investigation + 1 fresh relaunch
- **Root cause (orchestrator investigation, 2026-09-20):** The hang is NOT a `multiprocessing.SimpleQueue` pipe deadlock. A py-spy/standalone diagnosis + a diagnostic pytest test using the same fixtures showed no `enqueue=True` handler is present and `list_sessions(token=...)` returns OK. The real hang is an **infinite loop in the test's own assertion loop** (`tests/acceptance/sessionmanagement/test_observability.py::test_ac_045_traced_methods_no_tokens_in_logs`):
  ```python
  for record in log_records:
      dumped = str(record["record"])
      assert hash_token(token) not in dumped   # hash_token is @logged
  ```
  `hash_token` is `@logged` (AGENTS.md mandates `@logged` on public module-level functions), so each call appends **new** records to `log_records` (the `log_records` fixture's sink). The loop iterates over a list that grows as it iterates → infinite loop. The captured run produced **808,286 lines** and `hash_token` was called **404,071 times**. The original "queue deadlock" stack trace (main thread blocked at `multiprocessing/queues.py:394 put` → `connection.py:303 _send_bytes`) was a **secondary effect**: the infinite loop produced records faster than the `enqueue=True` pipe could drain, blocking `queue.put`.
- **Resolution:** The conftest reconfigure fix addresses the secondary effect, not the root cause, and deviates from the spec-mandated `enqueue=True` (logging REQ-001/AC-001) — it is removed. The correct fix is in the test: compute `hash_token(token)` / `hash_token("bogus-token")` **once** before the loop and iterate over a **snapshot** of `log_records` (`list(log_records)`), so the loop body no longer appends records and terminates. A fresh Phase 4 subagent is relaunched with this context.
- **Date:** 2026-09-20

## P-22 — deptry's first run surfaced 14 findings beyond the baseline config; the baseline's `DEP001 sqlalchemy` prediction was actually a `DEP003`; an unanchored `.gitignore` pattern was silently excluding `src/backend/settings/` from deptry's scan (discovered in S4.3)
- **Problem:** The scope's `[tool.deptry]` baseline (14 DEP002 entries + `DEP001 = ["sqlalchemy"]`) did not cover reality: `sqlalchemy` is a DEP003 (transitive) finding, not DEP001; `webauthn` (optional, deferred import — ADR-031) fires DEP001; `alembic` (dev dep imported by the `migrations/` scaffold) fires DEP004; `httpx`/`orjson` (declared runtime deps, not yet imported) fire DEP002; `ruamel-yaml` (imported as top-level `ruamel`) needed `package_module_name_map`. Worse, the unanchored `.gitignore` pattern `settings/` made deptry's gitignore-aware file finder silently exclude `src/backend/settings/` (and settings tests) from the scan, producing a *false* `DEP002 ruamel-yaml` finding.
- **Step / Phase:** S4.3 (deps + deptry config) — Phase 4
- **Change:** dev-tooling-wiring / DOCS/CHORE
- **Duration / iterations:** 1 (resolved in-step; gate `uv run deptry .` exit 0)
- **Resolution:** Each finding resolved with a justified, commented config entry (per-rule ignores / `package_module_name_map`); the `.gitignore` `settings/` → `/settings/` anchor fix (1 line, documented as a root-cause scope deviation in the verification file) removed the false positive — deliberately NOT masked with a `ruamel-yaml` DEP002 ignore (which would permanently mask the settings feature).
- **Date:** 2026-09-20

## P-23 — Orchestrator task definition was internally inconsistent: the mkdocs-build hook is a pre-push-stage hook, but the gate command was the bare `pre-commit run mkdocs-build --all-files` (discovered in S4.5)
- **Problem:** The S4.5 task definition required both `stages: [pre-push]` for the mkdocs-build hook (context note: the slower build belongs in pre-push) and a passing bare `uv run pre-commit run mkdocs-build --all-files` (gate) — the latter defaults to the `pre-commit` stage and exits 1 with "No hook with id `mkdocs-build` in stage `pre-commit`" by construction.
- **Step / Phase:** S4.5 (pre-commit hooks + CI jobs) — Phase 4
- **Change:** dev-tooling-wiring / DOCS/CHORE
- **Duration / iterations:** 1 (resolved in-step; the hook config was kept as designed)
- **Resolution:** The end-to-end check was run as `uv run pre-commit run mkdocs-build --all-files --hook-stage pre-push` (exit 0); the deviation was recorded in the verification file ("Gate invocation note"). Lesson: when a task definition pairs a stage override with a gate command, the gate command must carry the matching `--hook-stage` flag.
- **Date:** 2026-09-20

## P-24 — polyfactory 3.x API differs from the expected shape: `PydanticModelFactory` does not exist; the real entry point is `ModelFactory.create_factory` (discovered in S4.1)
- **Problem:** The scope expected a `PydanticModelFactory`-style class; polyfactory 3.3.0's actual API is `polyfactory.factories.pydantic_factory.ModelFactory` + `ModelFactory.create_factory(model)` (no `PydanticModelFactory` in 3.x).
- **Step / Phase:** S4.1 (shared test tooling helpers) — Phase 4
- **Change:** dev-tooling-wiring / DOCS/CHORE
- **Duration / iterations:** 1 (adapted in-step per the task definition's "verify, do not assume" guidance)
- **Resolution:** The helper wraps the real API (`model_factory(MyModel)` → `ModelFactory.create_factory(MyModel)`); the smoke test exercised factory build/override/batch.
- **Date:** 2026-09-20

## P-25 — S5.2 subagent ended with an intermediate statement (no structured handoff, no commit); step relaunched with a fresh subagent
- **Problem:** The S5.2 subagent (lint + types + no-delta confirmation + verification report) terminated with an intermediate statement ("Now the whole-repo lint gate:") instead of the required structured handoff. No S5.2 commit exists, no evidence was recorded, working tree clean — the step is incomplete (the diff review it reported passing was not persisted).
- **Step / Phase:** S5.2 (lint + types + verification report) — Phase 5
- **Change:** dev-tooling-wiring / DOCS/CHORE
- **Duration / iterations:** 1 failed run + 1 fresh relaunch
- **Resolution:** Relaunched with a fresh subagent (completion guard, P-3/P-7); the relaunch prompt re-states all done criteria so the step is self-contained.
- **Date:** 2026-09-21

## P-26 — main's `uv.lock` is stale relative to `pyproject.toml` (self-version 0.4.0 vs 0.4.1): any `uv run` in the primary worktree re-locks and dirties it (discovered in S5.2)
- **Problem:** main's `uv.lock` still carries the pre-bump self-version (0.4.0) while main's `pyproject.toml` is 0.4.1 (the bump-my-version config updates only `pyproject.toml`, not the lock). Consequence: any `uv run` in the **primary** worktree auto-re-locks and transiently dirties main's `uv.lock`. The S5.2 subagent hit this while verifying pre-existing state in the primary worktree and restored it via `git checkout -- uv.lock`.
- **Step / Phase:** S5.2 (lint + types + verification report) — Phase 5
- **Change:** dev-tooling-wiring / DOCS/CHORE
- **Duration / iterations:** 1 (transient dirtiness, restored; no impact on the change)
- **Resolution:** The change branch's S4.3 lock sync (self-version 0.4.0 → 0.4.1) fixes main's stale lock when the PR merges. Lesson recorded for the orchestrator: verify pre-existing state with `git show main:<file>` (or a worktree-local run), never with `uv run` in the primary worktree.
- **Date:** 2026-09-21

## P-27 — Phase 6 review subagent entered a loop and was aborted (no output produced); step relaunched with a fresh subagent
- **Problem:** The Phase 6 review subagent (launched for S6.1, review vs. normative basis) entered a repeated-execution loop and was aborted by the user. It produced no review findings, no structured handoff, and no uncommitted work (worktree clean except untracked `data/`). Cause (inferred): the review was scoped to the whole 84-commit implementation diff without a bounded input surface, so the subagent re-ran a large diff/test command repeatedly instead of producing findings.
- **Step / Phase:** S6.1 (review vs. normative basis) — Phase 6
- **Change:** user-roles-permissions / CROSS-CUTTING
- **Duration / iterations:** 1 aborted run + 1 fresh relaunch
- **Resolution:** Relaunched S6.1 with a fresh subagent (completion guard, P-3/P-7) whose prompt is strictly bounded: single objective (normative-basis compliance), explicit inputs (spec + verification file + final `src/` state), an explicit instruction NOT to re-run the full test suite (Phase 5 already confirmed the gate CLEAN) and NOT to do S6.2–S6.4, and a required structured handoff.
- **Date:** 2026-09-22

## P-28 — three step subagents exhausted the model context window in one change (S3.1, S4.2-H, S4.2-I); the cause was the change's own verification doc, not the task
- **Problem:** The S3.1 test-derivation run failed with `prompt (80579 tokens) + max tokens exceeds the context`; the S4.2 (item H) run failed the same way at `prompt (127442 tokens)`; the S4.2 (item I) run died on a `Connection error` after ~25 min. `docs/verification/main-ci-green.md` had grown to 1454–1600 lines, and each subagent read it whole (several times), while verbose pytest output (`-v`, long tracebacks, full-suite logs of 639 tests) added the rest.
- **Step / Phase:** S3.1 (Phase 3), S4.2 items H and I (Phase 4)
- **Change:** main-ci-green / ISSUE
- **Duration / iterations:** 2 failed runs + 1 aborted run, 3 fresh relaunches
- **Resolution:** Relaunches carried explicit context budgets: grep-first + windowed reads (≤15–25 lines) and **never read the verification doc whole**; **append evidence with a heredoc instead of read-and-rewrite**; every pytest run terse (`-q --tb=line --color=no 2>&1 | tail -8`), never `-v`; explicit run and tool-call budgets; and the step was split into **part 1 (verify + commit code, no docs)** and **part 2 (record the evidence, no code)**. After that the same class of step ran in 86–715s with 7–24 tool calls.
- **Date:** 2026-10-02

## P-29 — Phase 5 S5.1 gate FAILED: the full suite was red in 2 of 6 runs; re-entered Phase 4 with a new item (I)
- **Problem:** After items A–H, every targeted group was GREEN but `uv run pytest tests/ -q` failed in ~1 of 3 runs (`test_ac_004_intercept_handler_routes_records`, `test_ac_005_intercept_handler_skips_bootstrap`, `test_stdlib_loguru_decorator_pipeline`). Each node passes in isolation (0/5) and in the known polluting groups (0/5), so the trigger was only visible in the full-suite randomized permutation — and CI runs the same randomized suite, so "green locally" was not evidence.
- **Step / Phase:** S5.1 (Phase 5) → re-entry to S4.2 (item I) → S5.1 re-run
- **Change:** main-ci-green / ISSUE
- **Duration / iterations:** 3 full-suite runs to observe + 10 probe/bisect runs + ~25 min of full-suite runs to separate the channels + 4-run proof + 2-run re-confirmation
- **Resolution:** Two independent channels, found by capturing the `pytest-randomly` seed of a red run and bisecting the test tree with that seed: (1) `migrations/env.py:27` calls `logging.config.fileConfig(...)`, which replaces the stdlib root logger's handlers/level and disables existing loggers, killing the logging feature's intercept handler (REQ-003) for every later test — closed by an autouse snapshot/restore fixture in `tests/conftest.py`; (2) Hypothesis' 200 ms default deadline on I/O-bound filemanagement property tests — closed with the file's own existing `deadline=500`. Lesson: for a flaky-suite change the Phase 5 gate must be **N consecutive full-suite runs**, and seed-capture + bisect is the efficient diagnosis; a single green run proves nothing under `pytest-randomly`.
- **Date:** 2026-10-02

## P-30 — the orchestrator's S1.1 launch brief asserted wrong premises about which CI jobs were failing
- **Problem:** The change was opened with a brief asserting main's CI failed on the settings YAML round-trip and the hypothesis deadline defects. The triage subagent proved both **pass on CI** (they are local-only findings replayed from the per-worktree `.hypothesis` example DB) and that the real `tests`-job failure was a logging-interception family whose failing set varies run to run. Two of the brief's premises were wrong; the scope had to be re-asked (Q-127).
- **Step / Phase:** S1.1 (Phase 1, ISSUE triage)
- **Change:** main-ci-green / ISSUE
- **Duration / iterations:** 1 BLOCKED-USER round + 1 triage re-run
- **Resolution:** The triage record's §6/§11 corrections are now the authoritative statement. Lesson for the orchestrator: when opening a CI-related change, attach the **per-job** failure evidence (`gh run view <id> --log-failed` per job, plus the job list) to the launch brief instead of summarizing from memory.
- **Date:** 2026-10-02

## P-31 — a single large heredoc append was truncated mid-write by the tool's command-size limit (S5.4)
- **Problem:** The Phase 5 verification report (~103 lines) was appended in one heredoc; the write was cut mid-line, leaving a partial row in the file.
- **Step / Phase:** S5.4 (Phase 5)
- **Change:** main-ci-green / ISSUE
- **Duration / iterations:** 1 extra iteration (truncate the partial line, re-append in two smaller heredocs)
- **Resolution:** Verified no duplicated rows and the correct net insertion count. Lesson: keep heredoc appends under ~50 lines and verify with `git diff --stat` after each append.
- **Date:** 2026-10-02

## P-32 — `tests/architecture/` is referenced by AGENTS.md and the verify skill but does not exist in the repository
- **Problem:** Phase 5 (REFACTOR/FEATURE gate) and Phase 6 (architecture check) name `uv run pytest tests/architecture/ -v`, and the verify skill runs it as a gate. The directory exists on neither this branch nor `origin/main`, so the gate is unrunnable and had to be recorded as N/A.
- **Step / Phase:** S5.2 (Phase 5)
- **Change:** main-ci-green / ISSUE
- **Duration / iterations:** 1 (discovery + N/A record)
- **Resolution:** Recorded as a follow-up reconciliation item (either add the architecture tests or correct AGENTS.md/the skill). Not fixed in this change (out of scope).
- **Date:** 2026-10-02

## P-33 — `bump-my-version` under `uvx` produced no output and `show` crashed; the bump had to be verified from git instead (S6.4)
- **Problem:** `uvx bump-my-version bump patch` (and `--dry-run`) exited 0 with **no stdout** (rich logging swallowed on this host), and `uvx bump-my-version show` raised a rich-click traceback, so the tool gave no evidence that it bumped anything.
- **Step / Phase:** S6.4 (version bump + open PR) — Phase 6
- **Change:** main-ci-green / ISSUE
- **Duration / iterations:** 1 extra verification round
- **Resolution:** Verified the bump with `git show --stat HEAD` + `git diff HEAD~1` (`pyproject.toml` `version` and `[tool.bumpversion] current_version`, 0.5.0 → 0.5.1, no tag). Lesson: after a tool run that reports nothing, verify the effect from the VCS state, not from the tool's report.
- **Date:** 2026-10-02

## P-34 — fixing `pip-audit` unmasked a never-executed `bandit` failure; Phase 6 re-entered Phase 4 with a new item (J)
- **Problem:** PR #58's `security` job failed in 12s on `bandit -r src/` with 6 low-severity findings, although the Phase 5 gate had run `pip-audit` and `deptry` locally. Cause: the job runs `pip-audit` (`.github/workflows/quality.yml:41`) **before** `bandit -r src/` (:43), and pip-audit had been failing on `main` for weeks — so bandit had never actually executed in CI and its findings were invisible. The Phase 5 gate set did not include bandit, so the change's verification was incomplete.
- **Step / Phase:** S6.4 (Phase 6) → re-entry to S4.2 (item J) → S5.2-equivalent security gate
- **Change:** main-ci-green / ISSUE
- **Duration / iterations:** 1 CI failure + 1 new item (fix + record), 2 extra subagent runs
- **Resolution:** Item J applied the repo's existing inline `# nosec BXXX` pattern (5× B105 on permission **description** strings in the `feature_actions.py` files, 1× B110 in `permissions/service.py`), comment-only, `+6/−6`, `bandit -r src/` now reports 0 issues and exits 0; CI `security` is green. Lessons: (a) when a CI job has multiple sequential steps, a green local run of the *first* one is not evidence about the later ones — enumerate every step of each red job; (b) the verify skill's gate list should include `uv run bandit -r src/` for any change that touches the security job.
- **Date:** 2026-10-02

## P-35 — a locally calibrated Hypothesis deadline tripped on CI; the `coverage` job failed after `tests` passed
- **Problem:** Item I set `deadline=500` on the filemanagement property tests (copied from a sibling test) after local measurement. CI's `coverage` job then failed: `test_inv_001_no_partial_state_on_failure - DeadlineExceeded('Test took 739.77ms, which exceeds the deadline of 500.00ms')`, while the `tests` job on the same commit **passed** (different `pytest-randomly` seed). Coverage itself was fine (93.57% vs 92).
- **Step / Phase:** S6.4 follow-up (Phase 6) → re-entry to S4.2 (item K)
- **Change:** main-ci-green / ISSUE
- **Duration / iterations:** 1 CI failure + 1 fix/record run (~2.5 min CI each)
- **Resolution:** Item K made the file uniform at `deadline=2000` (≈2.7× the CI worst) with the CI run id recorded in the docstring; decorator-only, no assertion/strategy change. Lessons: (a) a Hypothesis deadline must be calibrated against **CI** timings, not local ones; (b) the `tests` and `coverage` jobs run the same suite with **different seeds**, so one green job is not evidence about the other — check both.
- **Date:** 2026-10-02

## P-36 — NFR-001 performance budget (100 ms) unrealistic given the source's query path (fetches full Pydantic models via the repository ABC); T-008 subagents stuck
- **Problem:** The NFR-001 budget is "a single-source query < 100 ms median; 10k–100k items per source on local hardware against SQLite-backed sources". The test (`test_nfr_001_performance_budgets`) uses 10k items. The source's query function (`build_user_source`'s `_query`) fetches ALL items via the repository ABC's `list_all` (which returns full Pydantic `User` models) and processes them in Python — measured ~293 ms (median) for 10k items (fetch ~216 ms + processing ~77 ms). A lighter path (raw-row fetch + `SourceItem` build + sort) would be ~41 ms (under budget), but the source only sees the `UserRepository` ABC (whose `list_all` returns full models); using a lighter path requires changing the persistence contract (adding a lighter method to the repository), which is out of scope for the search feature (additive only — no new behavior in the feature's operations).
- **Step / Phase:** S4.2 (T-008) — Phase 4
- **Change:** search / CROSS-CUTTING
- **Duration / iterations:** 2 subagent runs (both returned without a structured handoff, stuck on the optimization)
- **Resolution:** User decision (2026-09-25): increase the budget via spec amendment (option 2) — `docs/specs/search.md` v2: NFR-001 single-source query budget increased from 100 ms to ~300 ms (10k items, scaling linearly to ~3000 ms for 100k items); the test's `_QUERY_BUDGET_S` re-aligned to 0.3 (10k items kept); T-008 GREEN (69 passed).
- **Date:** 2026-09-25
## After-workflow-optimization — user-roles-permissions (2026-09-22)
- **Trigger:** the user-roles-permissions change (~48.5h subagent time, ~90 subagents) reached Phase 6; the after-workflow-optimization meta-task analyzed the friction (this file + the change worktree's PROBLEMS.md P-27 + the subagent timing data) and improved the workflow.
- **Friction found (with timing evidence):**
  1. Redundant S4.3 (ruff) step — ~36m + 13 launches (S4.2 already runs the ruff gate).
  2. Invalid test data reached Phase 4 (recurring 2-char usernames, T-004/5/6) — ~1.3h + 4 launches (S3.1 generated `u1`/`u2`; S3.2 confirmed RED without separating `ValidationError` setup errors from behavioral failures).
  3. Pre-existing test breaks deferred to Phase 5 (T-002 `role→roles` amendment, 118 breaks) — ~3.6h + 3 launches (gate not-clean on first pass).
  4. S4.4 (refactor) mostly no-ops for repetitive-pattern tasks — ~2.7h + 14 launches.
  5. Phase 6 review looped (aborted) — 6404.8s (unbounded "review the whole diff" scope).
- **Workflow changes (AGENTS.md + skills):**
  1. Removed the redundant S4.3 (ruff) step → 4-step Phase 4 protocol (S4.1 pick+RED, S4.2 implement+GREEN+ruff gate, S4.3 refactor+ruff gate+no-op fast-path, S4.4 commit).
  2. Added test-data validity to S3.1 (fixtures construct valid model instances) + S3.2 sanity check (a `ValidationError` building test data = invalid test data, not RED) — test skill + AGENTS.md Phase 3.
  3. Added the breaking-change rule to decompose S2.2 (a breaking API change's task MUST fix the pre-existing tests it breaks within its scope, not defer to Phase 5) — decompose skill + AGENTS.md.
  4. Added the S4.4 (refactor) no-op fast-path (a small/clean-pattern change confirms "no structural changes" without a full-suite re-run) — AGENTS.md Phase 4.
  5. Added the bounded-scope rule to the review skill (each S6.x step reviews bounded inputs — spec + verification + final code state — not the full diff; no test re-run) — review skill + AGENTS.md Phase 6.
- **Date:** 2026-09-22

## P-37 — CI never triggered on a PR that had become CONFLICTING; 18 poll iterations (~18 min) wasted (S6.4)
- **Problem:** PR #54 (`crosscut/search`) showed **no** `pull_request` checks at all after the head was pushed. 18 `gh pr checks` polls (60 s each, ~18 min) reported nothing, and were read as "CI pending". In fact `gh pr view --json mergeable` returned `CONFLICTING`: `origin/main` had advanced (`e8dd2bc → a0c0897`, PR #59) and both changes append to `AGENTS.md` and `docs/workflow/PROBLEMS.md`, so GitHub triggered **zero** `pull_request` runs — a pending run and a never-triggered run look identical through `gh pr checks`.
- **Step / Phase:** S6.4 (Phase 6) — CI polling
- **Change:** search / CROSS-CUTTING
- **Duration / iterations:** 18 poll iterations (~18 min) + 1 merge/resolve run
- **Resolution:** merged `origin/main` into `crosscut/search` (normal push, no rebase/force-push); the single conflict (`docs/workflow/PROBLEMS.md`) was resolved as a **union** — `P-36` (branch) and main's `## After-workflow-optimization — user-roles-permissions` section both kept, no entry dropped; `AGENTS.md` auto-merged with both sides' content intact. Main's delta was docs/skills-only (no `src/`/`tests/`), so the Phase 5 evidence stays valid.
- **Durable lesson:** check `gh pr view --json mergeable` **before** polling, and use `gh api repos/<repo>/actions/runs?head_sha=<sha> --jq .total_count` to tell "not triggered" (0) from "pending" (>0). A CONFLICTING PR runs no CI — poll `mergeable` first, then checks.
- **Date:** 2026-10-02

## P-38 — a ~200-line report appended with a bash here-doc was silently truncated by the shell; the append had to be redone (S5.4)
- **Problem:** The Phase 5 verification report (~200 lines) was appended to `docs/verification/prepared-workflow.md` with a bash here-doc (`cat >> file <<'EOF' … EOF`). The shell truncated the payload silently — the command exited 0, and only a follow-up read of the file showed the append was incomplete, so the whole append had to be redone.
- **Related:** recurrence of **P-31** (same friction class — a large here-doc append; there the tool reported the command-size limit, here the truncation was silent).
- **Step / Phase:** S5.4 Verification report — Phase 5 (change prepared-workflow)
- **Change:** prepared-workflow / DOCS/CHORE
- **Duration / iterations:** 1 extra iteration.
- **Resolution:** wrote the report to a temp file and appended with `cat >>`; use a temp file (or `write` + `edit`) instead of large here-docs in this harness.
- **Date:** 2026-10-03
- **Status:** Solved (2026-10-03) — recipe noted in this entry.

## P-39 — three documentation fix rounds each closed findings while introducing new ones of the same class (gate signal with no reachable producer / ownership sentence that over-widened)
- **Problem:** Three consecutive documentation fix rounds (**S5.5 → S6.5 → S6.7**) each closed findings while introducing new ones of the same class: a gate signal with **no reachable producer** (F-1/F-4, then F-5/F-6, then F-11 — `Status: READY` required a P.5 handoff that never runs for ISSUE / REFACTOR / DOCS/CHORE), or an **ownership sentence that over-widened and forbade a step's own required write** (F-12 — "only the orchestrator edits them; step subagents never do" forbade the P.2 question write the same protocol mandates, and "a change branch must never **contain** those paths" contradicted the branch carrying the P.1–P.3 copies inherited at P.4).
- **Step / Phase:** S6.5 + S6.7 — Phase 6 review loop (change prepared-workflow)
- **Change:** prepared-workflow / DOCS/CHORE
- **Duration / iterations:** 3 fix rounds, ~2 review rounds.
- **Resolution:** state each new/changed gate signal with its **type applicability** (which change types it applies to) and its **producer** (who writes it, from which worktree) in the same sentence, and re-check the step that must perform the write before declaring the rule done.
  - when narrowing a step id or a producer clause, grep that id across **all** live-guidance files, not only the file being edited; the S6.7 fix narrowed P.5 in AGENTS.md but left three READY clauses in the same-named skill pointing at it (F-15, round 4).
- **Date:** 2026-10-03
- **Status:** Solved (2026-10-03) — recipe noted in this entry.

## P-40 — `bump-my-version bump --dry-run` prints nothing on success; 3 invocations to get usable evidence (S6.4)
- **Problem:** `uv tool run bump-my-version bump patch --dry-run` exits 0 with **empty stdout**, so a successful dry run is indistinguishable from a no-op — the S6.4 bump gate had no before/after evidence. Adding `-v 1` broke differently: `--verbose` is a **count** flag, so the `1` was parsed as a FILE argument and the run died with `FileNotFoundError: File not found: '1'`.
- **Step / Phase:** S6.4 Bump version + open PR — Phase 6 (change session-lookup-unwired)
- **Change:** session-lookup-unwired / ISSUE
- **Duration / iterations:** 3 invocations (~2 min).
- **Resolution:** run `bump-my-version bump <level> --dry-run -v` (bare `-v`, no count argument) — the verbose output carries the before/after diff. Then the real bump with a clean tree.
- **Date:** 2026-10-04

## P-41 — a light-tier ISSUE's Phase 5 + Phase 6 cost 4 subagent launches (~25 min) for a 10-line fix (S5.x, S6.x)
- **Problem:** For a light-tier ISSUE whose whole fix is 2 moved lines + 1 keyword, the atomic-step breakdown (S5.1, S5.2, S5.3, S5.4, then S6.1, S6.2, S6.3, S6.4) meant 8 launches, each re-reading the skill file, the triage record and the verification artifact from scratch (~150–500k tokens each). The step overhead dominated the work; the objective was met by the first launch's evidence.
- **Step / Phase:** S5.1–S5.4 (Phase 5) + S6.1–S6.4 (Phase 6) — light-tier ISSUE
- **Change:** session-lookup-unwired / ISSUE
- **Duration / iterations:** 8 launches, ~45 min of step time for a 10-line diff (no failures, no re-launches).
- **Resolution (what was actually done):** the read-only gate runs were executed as **S5.1+S5.2** in one subagent and the record writes as **S5.3+S5.4** in one, and the bounded review as **S6.1–S6.3** in one — each combination is recorded in the verification artifact. Suggestion for the after-workflow-optimization: make the light-tier ISSUE Phase 5/6 step set explicitly coalescible (gates-in-one, records-in-one, review-in-one, S6.4 always separate because it bumps and opens the PR).
- **Date:** 2026-10-04

## P-45 — approved specs' test-strategy sections cite test function names that no longer exist on disk; the traceability script does not check spec strategy tables, so the drift survived until P.5 (P.5)
- **Problem:** The test-strategy sections of already-approved specs name test files and functions that are not on disk: `docs/specs/logging.md` §9/§10 (`tests/acceptance/test_logging.py::test_setup_logger_sinks_configured`, `tests/unit/test_logging.py::test_intercept_handler_routes_records`, …) and `docs/specs/settings-coverage.md`. `scripts/check_traceability.py` validates the **matrix** (`docs/verification/traceability.md`) — a `REQ`/`AC` with no matrix row, a row citing a dead ID, a row citing a test function that no longer exists — so it never looks at the **spec's own** strategy tables. The drift was therefore invisible to CI and only became visible at P.5, where the new `structlog-logging.md` §11 named the real functions and directly contradicted the amended `logging.md` (finding F-P5-02, already noted once before at `docs/verification/main-ci-green.md:368`).
- **Step / Phase:** P.5 Verify self-consistency — Phase P (change structlog-logging)
- **Change:** structlog-logging / CROSS-CUTTING
- **Duration / iterations:** found during the P.5 checklist; 1 spec-side fix round (wording only, no ID or status change), recorded in the `logging.md` v3 changelog.
- **Resolution:** the amended specs were corrected to the on-disk names (`tests/acceptance/logging/test_logging.py::test_ac_001_setup_logger_adds_sinks`, `tests/unit/logging/test_logging.py::test_ac_004_intercept_handler_routes_records`, `tests/unit/logging/test_logging_edges.py::test_edge_001…004`, `tests/property/logging/test_logging_properties.py::test_inv_001…003`). Durable fix (a follow-up chore, not this change): extend `scripts/check_traceability.py` to parse the **spec** strategy tables as well as the matrix, so a spec row citing a test function that does not exist under `tests/` fails the `traceability` job like a matrix row does.
- **Date:** 2026-10-04

## P-46 — the P.5 dependency smoke-test took 3 rounds (~20 min) because structlog 26.1.0's real API differs from the spec's assumptions (P.5)
- **Problem:** The P.4 draft spec and ADR-082 described the pipeline with the API the older structlog documentation shows. Against the installed-candidate version (structlog 26.1.0, orjson 3.12.0, Python 3.14.5, Windows 11) six assumptions were wrong, and each surfaced only as a runtime failure in the smoke script: (1) the JSON renderer's serializer option is `serializer=`, not `json_dumps=`, and an unknown keyword fails only at **render** time, not at construction; (2) `orjson.dumps` returns **bytes**, so the adapter must decode to `str`; (3) `JSONRenderer` forwards `default=None` to the serializer, which orjson rejects; (4) `ProcessorFormatter` injects the bookkeeping keys `_record` / `_from_structlog` that nothing strips by default, so they reach the rendered record; (5) `logging.handlers.QueueHandler.prepare()` formats the record while enqueueing, which destroys the structured event dict the file sink renders from; (6) `logger.exception()` puts `exc_info` on the **record**, not in the event dict, so the pipeline must render it into a field and suppress the stdlib's own formatting. The callsite step also resolves inside the listener thread when it sits in the formatter chain, so it must run at the emitting call site.
- **Step / Phase:** P.5 Verify self-consistency (Dependency Smoke-Test) — Phase P (change structlog-logging)
- **Change:** structlog-logging / CROSS-CUTTING
- **Duration / iterations:** 3 smoke-test rounds, ~20 min.
- **Resolution:** all six facts were pinned in ADR-082 § Decision and in the spec's design decisions D3/D4/D7 **before any implementation code exists**, so Phase 4 cannot re-discover them; the smoke script itself is left uncommitted in the temp directory and the dependency was **not** added (`uv run --with structlog`). Durable lesson: run the dependency smoke-test against the **real library version** early (P.5 is that place) rather than trusting the API as documented, and state verified library constraints as design decisions, not as implementation freedom.
- **Date:** 2026-10-04
## P-42 — a version bump leaves `main`'s working tree dirty because `uv.lock` is not in `[tool.bumpversion.files]` (S7.1)
- **Problem:** `[tool.bumpversion.files]` in `pyproject.toml` lists only `pyproject.toml`, so `bump-my-version bump patch` (`0.6.0 → 0.6.1`, change session-lookup-unwired, S6.4) bumped the project version but left `uv.lock` pinning `0.6.0`. `uv.lock` records the local editable package's version, so **every** `uv run` on `main` re-locks it and rewrites the file — `git status` on `main` shows ` M uv.lock` after any command, and a dirty tree breaks the `allow_dirty` precondition of the next bump and hides real changes in the noise.
- **Step / Phase:** S7.1 Post-merge cleanup — Phase 6 / post-merge (change session-lookup-unwired)
- **Change:** session-lookup-unwired / ISSUE
- **Duration / iterations:** found during the `architecture-tests-missing` Phase 5 gate run (the first `uv run` in a fresh worktree rewrote `uv.lock`); 1 investigation + 1 revert.
- **Resolution:** revert the regenerated lock (`git checkout -- uv.lock`) and **do not commit it to `main`** — it is out of scope for any change that did not touch dependencies. Durable fix: add `uv.lock` to `[tool.bumpversion.files]` so a bump updates the lock's pinned version in the same commit — a follow-up chore (`pyproject.toml` only, no behavior).
- **Date:** 2026-10-04

## P-43 — Q-5 assumed 4 actionable private-import fixes; only 3 are DOCS/CHORE-actionable (the 4th needs new public API) (P.4)
- **Problem:** the `architecture-tests-missing` question file's **Q-5** folded "fix the 4 private-module imports" into this DOCS/CHORE change as 4 one-line rewrites. Three are true one-liners (`from backend.logging._decorator import logged` → `from backend.logging import logged`, the name is re-exported in `__all__`). The fourth — `src/main.py:67` `from backend.settings.registry import _registry as _settings_registry_singleton` — has **no public symbol to switch to**: the settings feature exposes only `get_settings_registry(required=True)` and `reset_settings_registry()`, `get_settings_registry()` lazily creates a **default** registry with no `permission_service`, and `permission_service` is constructor-only, so any substitution discards the wired singleton and **changes behavior**. `docs/specs/settings.md` REQ-014 specifies no setter, so adding one is a spec amendment, not import hygiene: the Q-5 premise ("4 equivalent fixes") was wrong.
- **Step / Phase:** P.4 Draft (scope record) — Phase P (change architecture-tests-missing)
- **Change:** architecture-tests-missing / DOCS/CHORE
- **Duration / iterations:** 1 verification pass over the settings public API (`registry.py:361-381`, `settings/__init__.py` `__all__`, `docs/specs/settings.md:175,234`) before the scope was written; no wasted implementation.
- **Resolution:** recorded as **finding F-1** in `docs/verification/architecture-tests-missing.md` and left **out of scope** (the private import stays, recorded rather than hidden); the change fixes 3 of the 4 imports. Framed as a separate prepared change — `docs/todo/settings-public-registry-setter.md` (FEATURE + settings-spec REQ-014 amendment), which is also the shared fix for the 6 test files / 9 sites that write `_registry` directly.
- **Durable lesson:** when a question folds "same-kind" fixes into a small change, verify each site has a **public equivalent** before promising it; an import rewrite is only non-behavior if the public API already exports the same object.
- **Date:** 2026-10-04
## P-44 — the orchestrator's P.4 launch prompt carried an invented answer set; the scope record had to be rewritten on a P.4 re-entry (P.4 Draft)
- **Problem:** The launch prompt for **P.4 Draft** of `update-readme` restated the answers from memory instead of quoting the on-disk records, and invented decisions that no question ever asked: a `.agents/skills/docs-as-code/SKILL.md`, an 11-row README feature table, a "Project layout" section, a Status/version block, and a whole new `AGENTS.md` "Documentation & traceability" section. The question file has exactly **6** questions (Q-1…Q-6); the prompt asserted a 10-item "Q-1…Q-10" list. The result was a **246-line scope record** (`5a59bc7`) describing scope nobody approved — caught only because the P.4 re-entry re-read `docs/todo/update-readme.md` and `docs/questions/update-readme.md`.
- **Step / Phase:** P.4 Draft — Phase P (change update-readme)
- **Change:** update-readme / DOCS/CHORE
- **Duration / iterations:** 1 wasted scope record + 1 full P.4 re-entry (the record rewritten as `be65b0e`).
- **Resolution:** the on-disk planning records (`docs/todo/`, `docs/questions/`) are **authoritative** — a launch prompt must **quote** them, never restate them from memory. The rewritten record carries a "Correction" note naming the superseded commit and listing exactly what was removed, so the wrong draft stays auditable instead of being silently replaced.
- **Date:** 2026-10-04
- **Status:** Solved (2026-10-04) — recipe noted in this entry.

## P-47 — orchestrator re-launched a finished step with a wrong-scope prompt
- **Problem:** after P.4 for `pyproject-tooling-gaps` had already completed (`f9d357f`, branch `refactor/pyproject-tooling-gaps`, TODO already `READY`), the orchestrator launched a **second** P.4 subagent whose prompt listed a scope (`[tool.deptry]` config, `ty` in dev, a `ty` pre-commit hook, a `ty` CI job, an AGENTS.md Type-Safety fix) that appears in **neither** `docs/todo/pyproject-tooling-gaps.md` nor `docs/questions/pyproject-tooling-gaps.md`, and named the wrong branch type (`chore/` instead of the reclassified `refactor/`). Every premise was already false on `main`.
- **Step / Phase:** P.4 Draft (duplicate re-entry).
- **Change:** `pyproject-tooling-gaps` (REFACTOR).
- **Duration / iterations:** one wasted subagent launch (462 s, 161.8k tokens).
- **Renumbered:** logged as **P-45** on this change's branch (`c0dd9ff`); renumbered to **P-47** when this branch was rebased onto `main`, because `structlog-logging` had already taken P-45 there. Collision note (c) in `docs/verification/pyproject-tooling-gaps.md`: resolve as a union of the appended entries — no existing entry on `main` is reordered or renumbered.
- **Resolution:** the step subagent did **not** comply blindly — it re-measured each premise against `main`, created nothing, and returned `BLOCKED-HUMAN` with the evidence and three options. The orchestrator chose (A): accept the existing P.4. This is the second occurrence of the P-44 root cause (launch prompt restated from memory instead of quoting the on-disk records) and the first case where the subagent's own verification caught it. Suggested for the after-workflow-optimization: a step subagent should always re-verify that its step is not already complete before executing it, and the orchestrator should paste the scope section of `docs/todo/<name>.md` and `docs/verification/<name>.md` into the launch prompt verbatim.
- **Date:** 2026-10-04

## P-48 — a guidance change needed **three S4.2 re-entries** because its scope enumerated edits by location, not by rule (S4.2 ×3)
- **Numbering note:** next free id taken by scanning `^## P-` headings (highest on `main` = **P-47**); entries are appended, never renumbered — the P-42…P-47 out-of-order placement in this file is the established collision convention (see P-47's **Renumbered** line).
- **Problem:** the P.4 scope of `value-triage-gate` listed **22 edits by file + line anchor** (`AGENTS.md:151`, `git:59`, …). Every review pass then found **another place where the same new rule had to be stated**, and each one cost a full S4.2 re-entry: (1) after S5, three stale statements of the extended direct-to-`main` / status-chain rule (`AGENTS.md:118`, `AGENTS.md:419`, `git:12`) → rows **A11/A12/G6** (22 → 25); (2) after S6.1, the S7.1 **completion rule** stated in five places where only one had been updated (`git:56`, `git:58`, `git:41`, `AGENTS.md:443`) → **G7/G8/G9/A13/G2a** (→ 30); (3) after S6.2, the archive-move **producer** and the todo-set **closure** rule → **G10/G11/A14/V1/V2** (→ 35). The scope grew 22 → 35 rows across three re-entries of the *same* step, i.e. three subagent launches that the approved scope should have covered.
- **Step / Phase:** S4.2 Implement + re-entries #1/#2/#3 — Phase 4 (change value-triage-gate)
- **Change:** value-triage-gate / DOCS/CHORE
- **Duration / iterations:** 3 extra S4.2 re-entries (each a full launch: skill read + record read + gate re-run).
- **Resolution:** the change closed all of them and its S6.3 report is **CLEAN**, but the cost was avoidable. **Durable lesson for guidance changes: enumerate by *rule*, not by *anchor*.** Before a DOCS/CHORE scope is approved, name every rule the change touches (status chain, completion rule, direct-to-`main` exclusivity, entry precondition, producer of each new action), then `grep` each rule's vocabulary across **all** live-guidance files (`AGENTS.md`, `.agents/skills/*/SKILL.md`, `docs/*/template.md`) and put **one scope row per statement of the rule**, not one per file/line. The completeness sweeps that finally did this (re-entry #2 and #3) are cheap — a handful of greps — and are what made the third pass the last one. Same class as **P-39** (fix rounds closing findings while introducing same-class ones); this is the scope-side cause of that symptom.
- **Date:** 2026-10-06

## P-49 — the archive-move guidance this change wrote would have failed on first run: `git mv` does not create the destination directory (S6.2 finding B-1)
- **Problem:** the new S7.1 / planning-commit guidance told the orchestrator to run `git mv docs/todo/<name>.md docs/todo/archive/<name>.md` (and the questions pair), and the P.4 record asserted the `archive/` folders "are created by the first move". Neither `docs/todo/archive/` nor `docs/questions/archive/` exists, and **`git mv` does not create the destination directory**: measured in a scratch repo (`git init` → commit → `git mv docs/todo/demo.md docs/todo/archive/demo.md`) → `fatal: renaming 'docs/todo/demo.md' failed: No such file or directory`, exit **128**; the identical sequence succeeds only after `mkdir -p docs/todo/archive docs/questions/archive`. `grep -rn mkdir AGENTS.md .agents/skills docs/todo/template.md` → **0 hits**: no step created the folders. So the **first drop decision or first S7.1 cleanup after this change merged would have failed mid-step**, and the P.4 claim was never checked against the tool it described.
- **Step / Phase:** S6.2 Traceability + boundaries (found) → S4.2 re-entry #3 (fixed, rows G10/G11/V1) — Phase 6 / Phase 4 (change value-triage-gate)
- **Change:** value-triage-gate / DOCS/CHORE
- **Duration / iterations:** 1 scratch-repo measurement + 1 S4.2 re-entry (2 added lines + the reason clause + the record correction).
- **Resolution:** `mkdir -p docs/todo/archive docs/questions/archive` is now the **first command of both blocks** (`git:77`, `git:149`), with the reason stated inline so a later reader does not delete it as redundant; the false claim in the record is corrected with the measurement quoted, not silently rewritten. **Durable lesson: any command sequence written into a skill must be run once in a throwaway repo before the scope is approved** — a DOCS/CHORE change whose whole product is executable guidance is only verified when the commands are executed, not when their wording is reviewed. Cheap form: `git init /tmp/probe && …` in the step that drafts the block, and paste the exit code into the scope record.
- **Date:** 2026-10-06

## P-50 — third recurrence of silent heredoc truncation: three subagents on this change lost ≥ ~10 KB appends with exit code 0 (S4.2/S6.x record writes)
- **Problem:** step subagents appending a long record section to `docs/verification/value-triage-gate.md` with a shell here-doc (`cat >> file <<'EOF' … EOF`) had the payload **silently truncated**: the command exits **0**, the file is short of the intended content, and nothing in the tool output signals it. Three separate subagents on this change hit it (the record is ~1.4 k lines and grew in large appends at every re-entry). At this point the failure was only caught because the next step re-read the file and the row/line counts did not match.
- **Step / Phase:** record writes in S4.2 re-entries and S6.x — Phase 4 / Phase 6 (change value-triage-gate)
- **Change:** value-triage-gate / DOCS/CHORE
- **Duration / iterations:** 3 occurrences across the change (each ~1 extra pass to detect and re-append).
- **Related:** **third recurrence** of **P-31** (S5.4, tool reported a command-size limit) and **P-38** (S5.4, silent truncation of a ~200-line report) — the class keeps recurring because each change re-discovers it locally.
- **Resolution (recipe to apply, and the reason this entry exists):** append long record sections in **≤ ~5 KB chunks** (roughly ≤ 50–60 lines per append), or write the section with the file-write / edit tool instead of a shell here-doc, and **re-verify after every append** with `wc -l <file>` plus a row count (`grep -c '^| <id-prefix>' <file>`) compared against the intended numbers — never trust the exit code. Suggested for the after-workflow-optimization: put the chunk-size + post-append count check into the `verify`/`implement`/`review` skills' record-writing step so it stops being per-change folklore.
- **Date:** 2026-10-06

## P-51 — the P.4 draft's ruff guard would have been inert: `banned-api` entries without `TID251` in `select` enforce nothing (P.5)
- **Problem:** the P.4 spec (§3.4, REQ-013, AC-018, §12 row 9) added five `[tool.ruff.lint.flake8-tidy-imports.banned-api]` entries and stopped there. The repository's `[tool.ruff.lint] select` is `["I","E","W","B","F","UP","RUF","PL","Q","SIM","C4","DTZ"]` — **`TID` is not selected**, and ruff does not auto-enable a rule just because its rule-specific table is configured. Measured with the project's own select list plus a `banned-api` entry on a planted `from backend.settings.registry import _registry`: the only diagnostic is `F401`, **no `TID251`**. So the guard the spec calls one of the two reasons the pattern "cannot come back" would have enforced nothing, and AC-018's repository-wide half ("the repository reports no `TID251` violation") would have passed **vacuously** — a green gate proving nothing.
- **Step / Phase:** P.5 Verify self-consistency — Dependency Smoke-Test (change settings-public-registry-setter / CROSS-CUTTING)
- **Duration / iterations:** 4 ruff probes on temporary fixture files (~3 min) + 1 spec edit.
- **Resolution:** §3.4 and §12 row 9 now require **`"TID251"` added to `[tool.ruff.lint] select`** beside the five entries, with the reason stated inline so a later reader does not drop it as redundant; §10 records that selecting it introduces **zero** pre-existing violations (`uv run ruff check --isolated --select TID src tests` → `All checks passed!`), so the guard cannot break the lint gate. The probes also pinned three semantics the spec now states instead of assuming: a **bare-name** key (`"_registry"`) flags nothing — keys must be fully qualified (`backend.settings.registry._registry`); **both** reference forms are caught (`from m import _slot` and `import m as a` + `a._slot = …`); and the **owner module's own** writes to its own slot are **not** caught, which is what EDGE-008 requires and means the ten inside-owner sites need no `noqa`. **Durable lesson for the Dependency Smoke-Test: smoke-test the *activation* of a named tooling capability, not only its existence** — a rule that is configured but not selected, or a config key in the wrong table, is a guard that silently does nothing. Same class as **P-49** (guidance that was never run against the tool it describes).
- **Date:** 2026-10-06

## P-52 — a rule generalized over "all five features" was unsatisfiable for one of them (session-management has no lazy default) (P.5)
- **Problem:** REQ-008, INV-001 and AC-009/AC-010/AC-011 as drafted asserted, for **all five** singletons, that after `set_x()` + `reset_x()` the next `get_x()` returns a lazily created default, that "no read raises", and that "exactly one default instance was constructed". `get_session_service()` with no `repository` argument **raises `ValueError`** (`session-management.md` EDGE-003 / AC-042) — session-management has no lazily created default at all. Had Phase 3 derived tests from the draft, three ACs and one invariant would have been RED for reasons no implementation can fix, and Phase 5 would have re-entered Phase 4 chasing an unimplementable requirement.
- **Step / Phase:** P.5 Verify self-consistency — REQ↔AC wording (change settings-public-registry-setter / CROSS-CUTTING)
- **Duration / iterations:** 1 measurement (`get_session_service` signature + its spec EDGE/AC) + 1 spec edit across 5 rows.
- **Resolution:** the lazy-create assertions are scoped to **the four features whose `get_*()` builds a default**, with session-management covered by an explicit injected-repository variant, and AC-010's final slot value allowed to be a lazily created default. Nothing was weakened: the four-feature rule is unchanged and the fifth feature gained its own assertion. **Durable lesson for CROSS-CUTTING specs that generalize a rule over N features: check each feature's documented exception before writing the general form** — grep the affected specs for `ValueError` / "raises" / "no default" on the API being generalized, and state the carve-out in the requirement, not in a footnote.
- **Date:** 2026-10-06

## P-53 — cross-spec ID citations are wrong twice in one draft, and no CI check catches them (P.5)
- **Problem:** two cited IDs were wrong in the P.4 draft. (1) NFR-002 benchmarked install latency against "the existing logging **NFR-002** budget", but `docs/specs/logging-coverage.md` NFR-002 is **Security** (no raw tokens, passwords or hashes in any log record); the performance budget is **NFR-001**. (2) EDGE-005 cited "the **four** subprocess-embedded test sites"; `rg` measures **three** (`tests/acceptance/settings_coverage/test_wiring.py:18`, `tests/acceptance/settings_coverage/test_setup_logger.py:31,55`). Neither is caught by any gate: `scripts/check_traceability.py` only checks that IDs *defined in a spec* have matrix rows (and treats IDs as one **global** namespace, so a citation to an ID that exists in *some* spec always looks fine — see the P.4 record on this change), and `verify_spec.py` does not resolve citations.
- **Step / Phase:** P.5 Verify self-consistency — ID references / scope consistency (change settings-public-registry-setter / CROSS-CUTTING)
- **Duration / iterations:** 2 lookups + 1 spec edit (plus the §12 Impact Analysis rows that had omitted `search.md` REQ-015/NFR-003 and `session-management.md` REQ-022/NFR-003).
- **Resolution:** both citations corrected, and every ID cited by the change spec re-checked against the spec that defines it. **Durable lesson: a citation to another spec's ID MUST be opened and read, never recalled** — per-spec ID namespaces collide (`AC-041` exists in both `settings.md` and `user-roles-permissions.md`; `EDGE-011` in both `event-bus.md` and `settings-coverage.md`), so a wrong citation still "resolves" and CI stays silent. Suggested for the after-workflow-optimization: have `verify_spec.py` flag a citation whose ID is defined in a spec other than the one cited.
- **Date:** 2026-10-06

## P-54 — the orchestrator's brief asserted a count it had not measured (14 outside-owner write sites; measurement is 12) (P.4 → P.5)
- **Problem:** `docs/todo/settings-public-registry-setter.md` ("In scope (settled by P.3)") and the P.4 launch brief state **14** outside-owner singleton-slot write sites. `rg` over `src/` and `tests/` measures **12**: `src/main.py:138` plus 11 test sites. The 14 double-counts the 3 subprocess-embedded writes (`tests/acceptance/settings_coverage/test_wiring.py:18`, `tests/acceptance/settings_coverage/test_setup_logger.py:31,55`), which are already inside the 9 settings sites the same sentence lists. A wrong count in a planning record propagates: it was in the spec's §1 and REQ-012, and an acceptance gate phrased around a count ("migrate all 14 sites") is unfalsifiable when the number is wrong.
- **Step / Phase:** P.4 Draft → P.5 Verify self-consistency (change settings-public-registry-setter / CROSS-CUTTING)
- **Duration / iterations:** 1 `rg` re-measurement + spec/record corrections; the TODO file itself is orchestrator-owned (`main`) and was **not** edited by P.5, so the correction is carried in `docs/verification/settings-public-registry-setter.md` and this entry.
- **Resolution:** the spec and this record now state the measured 12 with the site list inline so the number is checkable. **Durable lesson: the orchestrator MUST NOT assert a count it has not measured** — any number that enters a TODO, a launch brief or a spec gets produced by a command whose output is pasted into the record. Same class as **P-30** (launch brief asserted wrong premises about failing CI jobs) and **P-43** (Q-5 assumed 4 actionable fixes, only 3 were).
- **Date:** 2026-10-06

## P-50 (recurrence 4) — silent here-doc truncation hit again, in this change's P.5 record write
- **Problem:** appending the P.5 section to `docs/verification/settings-public-registry-setter.md` with `cat >> file <<'EOF' … EOF` truncated the payload mid-sentence (the file ended at "…may not edit the TOD") while the command reported only a *warning* about the here-doc delimiter. Caught only because the follow-up `wc -l` / `tail` check was run.
- **Step / Phase:** P.5 record write — Phase P (change settings-public-registry-setter / CROSS-CUTTING)
- **Duration / iterations:** 1 wasted append + 1 `git checkout --` restore + 1 rewrite via the file-write tool.
- **Resolution:** the section was written with the file-write tool to a scratch file and appended with `cat scratch >> record`, then verified with `wc -l` (151 → 243 lines). **Fourth recurrence of P-50** — the recipe holds: never here-doc a long record section; write it to a file and append, and verify line counts after every append.
- **Date:** 2026-10-06

## P-55 — the DAG's `allowed_files` omitted 3 test modules a task's own acceptance criterion names; found only at Phase 4 (S4.1 T-006)
- **Numbering note:** logged as **P-48** on the `crosscut/structlog-logging` branch; renumbered to **P-55** (next free id, main's highest being P-54) when this branch merged `origin/main`, which had already taken P-48. Same collision convention as **P-47** and **P-48**: union of the appended entries, no entry already on `main` reordered or renumbered.
- **Problem:** T-006's `allowed_files.test_files` lists 4 files, but its own AC-001 witness searches **`src/` and `tests/`** (`_SEARCHED_TREES = ("src", "tests")`) and therefore fails while `tests/conftest.py`, `tests/logging_coverage_test_helpers.py` and `tests/acceptance/logging/test_logging.py` still import the removed backend. The gap was internal to the DAG: T-006's `design_constraints[1]` names those test-tree imports as its precondition, and `tests/conftest.py:90-93` already says in prose *"T-006 removes the loguru half"* — the plan assigned the work, the machine-readable `allowed_files` never listed it. A step subagent that obeys the rule "tests may only be touched in `allowed_files.test_files`" cannot make the task's own `red_command` pass, so the task is unsatisfiable as written. It surfaced at the **pick** step, not at S2.2: S4.1 measured the loguru inventory against `allowed_files` and returned the scope flag (gate row f), which is the only reason it was not discovered mid-implementation.
- **Step / Phase:** S4.1 Pick task + confirm RED → S4.2 Implement + confirm GREEN — Phase 4 (change structlog-logging)
- **Change:** structlog-logging / CROSS-CUTTING
- **Duration / iterations:** 1 orchestrator decision round-trip between S4.1 and S4.2 (no failed step, no re-launch); the correction itself is 3 added lines per task file.
- **Resolution:** the orchestrator approved extending T-006's `allowed_files.test_files` with the three files, annotated in place in **both** `.github/task-runner/tasks.json` and `docs/tasks/structlog-logging.tasks.json`; the correction and its rationale are recorded in `docs/verification/structlog-logging.md` §1 of the S4.2 section. This is a DAG `allowed_files` correction, not a spec change — no spec file, requirement ID or task scope moved. Durable fix for the after-workflow-optimization: at S2.2, derive each task's `allowed_files.test_files` from the **witness's own search scope** (which trees a parsed-search test walks, which helper modules the shared fixtures import), not only from the spec's test-strategy table — a criterion that searches `tests/` makes every file in that search part of the task that must turn it green. Cheap check at S4.1: diff the task's red-message file list against its `allowed_files` before implementing (that is exactly what caught this).
- **Date:** 2026-10-07

## P-56 — the S5.2 gate set in the launch brief omitted CI's `complexity` job; the PR would have gone red (S5.2)
- **Problem:** the S5.2 (Lint + types) brief listed ruff (check + format), mypy, ty and deptry, and the docs build — but `.github/workflows/quality.yml` also carries a **`complexity`** job (`uv run complexipy src tests --max-complexity-allowed 15`, a gate). It **failed** on this branch: two functions introduced by this change's own Phase 3 tests exceeded the ceiling — `_backend_import_offenders` at **28** in `tests/acceptance/logging/test_pipeline_backend.py` and `test_inv_005_required_fields_present` at **21** in `tests/property/logging/test_pipeline_invariants.py` — while passing on `main`. Nothing in Phases 3–5 runs it, so the first signal would have been a red check on the Phase 6 PR.
- **Step / Phase:** S5.2 Lint + types — Phase 5 (change structlog-logging / CROSS-CUTTING)
- **Duration / iterations:** 1 gate failure + 2 refactors + 1 full-suite re-run (760 passed / 1 skipped, unchanged) — ~15 min.
- **Resolution:** both functions were split at their natural seams (`_imports_removed_backend` / `_imported_names` / `_first_backend_import`; the invariant's dispatch extracted to module-level `_emit_probe`), every assertion kept byte-for-byte, complexipy re-checked to exit 0, and the full suite re-run because test code changed after S5.1. **Durable lesson: the S5.2 brief must enumerate the CI gate set by reading `.github/workflows/` rather than from memory** — the Phase 5 job is "reproduce CI locally", so any job omitted from the brief is a gate the change silently skips. Suggested for the after-workflow-optimization: have S5.2 derive its command list from the workflow files (one line per gate job) and record the job name beside each command, as this change's S5.2 gate table now does.
- **Date:** 2026-10-07

## P-57 — a step subagent's bash CWD drifted to the primary worktree (`main`), so it measured the wrong file (S5.3)
- **Problem:** partway through S5.3 (Update traceability) the shell's working directory drifted from the change worktree to the **primary worktree on `main`**. The step then read `main`'s `docs/verification/traceability.md` and reported **432 matrix rows** as if it were the change's — the authoritative change-worktree figure is **822 rows / 136 spec IDs / 745 test functions**. A count taken from the wrong worktree would have entered the verification record and the S5.4 report, and an edit issued from that CWD could have written to `main`'s working tree (a direct-to-`main` commit risk, which the worktree rules exist to prevent).
- **Step / Phase:** S5.3 Update traceability — Phase 5 (change structlog-logging / CROSS-CUTTING)
- **Duration / iterations:** 1 wrong measurement + a full re-verification pass with explicit `cd` into the change worktree and absolute worktree paths for every edit (~10 min of the step).
- **Resolution:** every measurement and edit was re-run against absolute worktree paths and the corrected numbers recorded. **Durable lesson: a step subagent in a multi-worktree repo must pin its CWD** — start every command with an absolute `cd <change-worktree> && …` (or use absolute paths) and print `git rev-parse --show-toplevel` beside any count that enters a record. Suggested for the after-workflow-optimization: have the task-definition contract state the change worktree as an absolute path (it already does) and require the step's first command to echo `git rev-parse --show-toplevel` so a drift is visible in the evidence rather than in the numbers.
- **Date:** 2026-10-07

## P-58 — the S6.1 review asserted "no implementation behavior deviates from the spec"; a directed witness disproved it (S6.1 → S4.2 re-entry)
- **Problem:** the S6.1 review (Phase 6) classified **F-S6.1-01** as a *coverage gap* — "AC-002's colorized-text-to-stderr clause has no executable witness" — and closed with "No behavior deviates from the spec." The orchestrator directed a test-only witness for the clause; the witness (`tests/unit/logging/test_renderers.py:59`) **failed on the implementation**: `src/backend/logging/_renderers.py:231` looked up `LEVEL_COLORS.get(level, "")` with `record.levelname` (uppercase) against a **lowercase-keyed** map, so the console sink never emitted the ANSI level color on any stream — a live defect against `structlog-logging.md` AC-002 and `logging.md` v3 AC-001, present since T-001. Had the review's classification been taken at face value, the change would have shipped an unimplemented spec clause with a green suite.
- **Step / Phase:** S6.1 Review vs. normative basis → S6.1-fix → S4.2 re-entry (RED → GREEN) — Phase 6 (change structlog-logging / CROSS-CUTTING)
- **Duration / iterations:** 1 extra Phase-4/3 round-trip (witness commit `856f483`, one-line fix `e776c36`) + a full-suite re-run (761 passed / 1 skipped) — ~40 min.
- **Resolution:** one-line normalization at `_renderers.py:231` (`LEVEL_COLORS.get(level.lower(), "")`); the RED witness was committed **before** the fix, so the clause is now witnessed. **Durable lesson: a review finding of the form "clause X has no witness" MUST be resolved by writing the witness, never by asserting compliance** — the witness is what tells you whether the clause is implemented, unimplemented or mis-specified. Corollary for the reviewer's verdict wording: "no behavior deviates" is only admissible for clauses that have a witness; for unwitnessed clauses the review must say "unverified" and hand the gap to a step that produces the witness. Same class as **P-49** (guidance never run against the tool it describes) and **P-56** (a CI gate omitted from a brief is a gate nobody runs).
- **Date:** 2026-10-07

## P-50 (recurrence 5) — long here-doc append truncated again, this time inside a Phase 6 review step
- **Problem:** while appending the `### S6.2 — traceability + boundaries` section to `docs/verification/structlog-logging.md`, a `cat >> file <<'EOF' … EOF` append truncated mid-line (the heredoc terminator was lost by the shell), exactly the failure mode recorded in **P-50** and its third recurrence. Repaired inside the same step with targeted edits and a line-by-line re-verification, so no evidence was lost — but the step spent time it did not need to.
- **Step / Phase:** S6.2 Traceability + boundaries — Phase 6 (change structlog-logging / CROSS-CUTTING)
- **Duration / iterations:** 1 wasted append + 1 repair pass (~5 min).
- **Resolution:** the section was completed with targeted edits and verified. **Fifth recurrence of P-50** — the recipe is now binding for every step brief: never here-doc a long record section; write it with the file-write tool (to the target or a scratch file) and verify `wc -l` before and after. Step briefs should state it explicitly rather than relying on the agent having read `PROBLEMS.md`.
- **Date:** 2026-10-07

## P-60 — the S6.4 brief stated the wrong resulting version, and `bump-my-version` prints nothing on this host without `PYTHONUTF8=1`
- **Problem:** two pieces of friction in one step. (1) The S6.4 launch brief said `major` from `0.6.1` yields **`0.7.0`**; semver and the tool both give **`1.0.0`** (`0.7.0` would be a `minor` bump). The step subagent caught the mismatch, kept the **normative** level (`major` — spec §2 D6, REQ-015, Q-22, AGENTS.md Versioning "CROSS-CUTTING → major if breaking") and reported the discrepancy instead of silently following the wrong number. Had it obeyed the brief's number, the release would have understated a breaking change. (2) `bump-my-version` 1.5.1 produced **no output at all** on this Windows host: its commit template contains `→`, which raises `UnicodeEncodeError` under the `cp1252` code page, and the dry-run output was swallowed — a tool that looks like it did nothing.
- **Step / Phase:** S6.4 Bump version + open PR — Phase 6 (change structlog-logging / CROSS-CUTTING)
- **Duration / iterations:** 1 mid-step question round + 1 retry with the encoding fixed (~10 min).
- **Resolution:** bumped `0.6.1 → 1.0.0` (commit `137b7e9`), recorded in PR #74. **Durable lessons:** (a) the orchestrator MUST NOT state a derived value it has not computed — give the **level** and let the tool produce the number, or paste the `--dry-run` output (same class as **P-54**: an unmeasured count in a brief); (b) the recipe for this host is `PYTHONUTF8=1 uv tool run bump-my-version bump <level> --dry-run --verbose` — any tool whose output is empty on this shell is a code-page problem before it is a tool problem.
<!-- Numbering note: P-55..P-60 are taken by the unmerged crosscut/structlog-logging branch, so the next free id on main is P-61. Never renumber an entry that already exists. -->

## P-61 — the task-DAG JSON schema is undocumented and the existing DAGs disagree (S2.2)
- **Problem:** `docs/tasks/template.md` is a **Markdown** template, but the DAG is JSON, and the JSON DAGs on disk disagree with each other: `structlog-logging.tasks.json` uses `amended_ids` / `blocked_on`, `search.tasks.json` uses `dependencies` / `description`, and `scripts/validate_task_dag.py` enforces only **9 of the 21** keys actually in use. The S2.2 generator aborted on a key-set mismatch and the DAG had to be regenerated — a full write/abort/regenerate cycle for a naming question no document answers.
- **Step / Phase:** S2.2 Decompose into task DAG (change settings-public-registry-setter / CROSS-CUTTING)
- **Duration / iterations:** 1 wasted DAG generation + 1 regeneration; ~1 of the step's 104 tool uses spent on schema archaeology (reading three other DAGs to infer the key set).
- **Resolution:** the DAG was written with the superset key set (`id`, `requirements`, `acceptance_criteria`, `tests_to_create`, `red_command`, `implementation_steps`, `green_command`, `design_constraints`, `completion_gates`, `allowed_files`, `depends_on`, `status` + top-level `id_coverage` / `ci_gates_read_from` / `interlock`), validated (`PASSED: 12 tasks, acyclic, well-formed`), and the key set recorded in `docs/verification/settings-public-registry-setter.md`. **Durable fix (a chore TODO, not this change):** document the JSON schema in `docs/tasks/` or make `validate_task_dag.py` strict, so S2.2 does not re-infer it every time.
- **Date:** 2026-10-07

## P-62 — `git commit --amend` on the tip silently folded step S2.2's files into step S2.1's commit (S2.2)
- **Problem:** while repairing the regenerated DAG, `git commit --amend` on the branch tip merged the S2.2 task files into the **S2.1** commit, so the two steps' outputs became one commit and the per-step commit history (which the verification record cites) stopped matching the atomic-step model.
- **Step / Phase:** S2.2 Decompose into task DAG (change settings-public-registry-setter / CROSS-CUTTING)
- **Duration / iterations:** 1 `git reset --soft` + 2 re-commits to rebuild `aeda963` (S2.1) and `f8c3cc1` (S2.2).
- **Resolution:** history rebuilt; each step now commits exactly once, on its own, and **never amends a previous step's commit** — the verification record cites commit shas per step, so an amend invalidates the evidence trail. If a step needs to fix its own output, it adds a follow-up commit or amends **only its own** commit before the next step starts.
- **Date:** 2026-10-07

## P-65 — a single-shot write of a 7-task DAG JSON exceeded the model output limit and was discarded (S2.2)
- **Problem:** the S2.2 subagent wrote `docs/tasks/structure-map.tasks.json` (596 lines, 7 tasks × 20 keys) in **one** file-write call; the call exceeded the model's output-token limit and the whole write was discarded, so the step had to rewrite the file in 4 chunks (one write + three marker-anchored edits). The same shape appeared in P-61, where a DAG regeneration also cost a full write/abort cycle.
- **Step / Phase:** S2.2 Decompose into task DAG (change structure-map / FEATURE)
- **Duration / iterations:** 1 discarded 596-line write + 4-chunk rewrite; the step ran 2891 s / 39 tool uses / ~2.0 M tokens, of which the retry accounted for roughly a third.
- **Resolution:** the file was written task-group by task-group with the file-write tool plus marker-anchored edits, then verified by hash against its `.github/task-runner/` copy (`sha256 520a1958…e2dc` both) and by `validate_task_dag.py` (`PASSED: 7 tasks, acyclic, well-formed`). **Durable rule:** an S2.2 DAG above ~4 tasks is written **in per-task chunks by default**, never in one write; the byte-identity hash and the validator run are the completion check, not the write's return value.
- **Date:** 2026-10-07

## P-66 — an S3.1 step subagent died on a context overflow because its brief told it to read whole large files
- **Problem:** the **S3.1 (T-001)** subagent of `structure-map` was told to "read the spec fully", "read the ADRs and both verification sections", and "read the DAG". Those files measure 636 + 491 + 596 + 105 lines at this head, and the skill file plus the test-tree listing added more; the transcript reached **90 617 prompt tokens** and the run was rejected with `400: prompt + max tokens exceeds the context (131072)` before it wrote a single file. No work was lost, but the whole step launch was.
- **Step / Phase:** S3.1 Derive tests (T-001) — change structure-map / FEATURE
- **Duration / iterations:** 1 wasted step launch (~0 work produced), plus the re-launch.
- **Resolution:** relaunched with a **context-budgeted brief**: the task's JSON definition is pasted into the brief instead of being read from the 596-line DAG; the spec is read by **section** (locate with `grep -n "REQ-025\|AC-025\|NFR-004"`, then read that line range); the verification record is read only from its `## Phase 2 — S2.2 task DAG` hand-off note. **Durable rule:** a step brief names the exact sections/line ranges to read and never instructs a full read of a file above ~300 lines; the orchestrator pastes small inputs (a task object, a hand-off note) into the brief rather than pointing at a large file.
- **Date:** 2026-10-07
