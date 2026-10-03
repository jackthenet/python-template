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
- **Date:** 2026-10-03
- **Status:** Solved (2026-10-03) — recipe noted in this entry.
