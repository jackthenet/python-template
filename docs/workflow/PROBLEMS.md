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

## P-7 — S4.1 (T-003) subagent ended prematurely (no handoff) + surfaced a Hypothesis health-check error on test_inv_007
- **Problem:** The T-003 S4.1 subagent (confirm RED) ended after 10 tool uses returning an intermediate sentence ("Let me examine the property test that failed with a health check error (not the unimplemented signal).") instead of a structured handoff — the same premature-end failure mode as P-3. The useful signal it surfaced before ending: 3 of the 4 T-003 tests (test_ac_031, test_ac_032, test_edge_016) are clean unimplemented-signal REDs, but the property test `test_inv_007_key_containment` failed with a **Hypothesis health-check error** rather than the unimplemented signal. This needs investigation: either the health check is masking the unimplemented signal (acceptable RED), or the test's `key` strategy is genuinely problematic (a test bug that must be flagged, not fixed by weakening).
- **Step / Phase:** S4.1 Pick task + confirm RED — Phase 4 (T-003)
- **Change:** file-management / FEATURE
- **Duration / iterations:** 1 iteration (relaunched with a fresh subagent)
- **Resolution / guidance:** Relaunched S4.1 (T-003) with a fresh subagent, instructed to (a) confirm the 3 non-property tests are clean unimplemented-signal REDs, and (b) investigate the test_inv_007 health-check error — determine whether it masks the unimplemented signal (acceptable) or is a genuine strategy/test issue (flag as a finding). For future steps: a step subagent MUST end with the structured handoff even when it hits an unexpected failure — record the failure in the handoff (`status: FAILED` with the exact output) rather than ending mid-investigation.
- **Date:** 2026-09-13

## P-6 — Repo-wide `ruff check --fix .` + `ruff format .` modifies out-of-scope files (conflicts with "commit only this task's files")
- **Problem:** The T-002 implementation subagent (Phase 4) ran the prescribed whole-repo ruff gate (`uv run ruff check --fix .` + `uv run ruff format .`). It modified 51 out-of-scope files (including fixing the 23 pre-existing mail `I001`s and reformatting 28 files) and the reformat of `tests/property/mail/test_secrets.py` introduced 4 NEW `RUF001`/`RUF100` errors (a line-level `# noqa: RUF001` was lost when the noqa list was split across lines). The subagent had to revert ALL out-of-scope changes to restore the expected end state (23 pre-existing mail I001s + clean tree) before committing only the 2 task files. This wasted tool calls and time and is a recurring trap: the P-4 guidance ("use `ruff --fix`") is correct for the TASK's files but wrong when applied repo-wide against a "commit only this task's files" + "clean tree" expectation.
- **Step / Phase:** S4.3 Ruff — Phase 4 (T-002)
- **Change:** file-management / FEATURE
- **Duration / iterations:** 1 iteration (subagent recovered by reverting out-of-scope changes; no rework of the task)
- **Resolution / guidance (for future steps):** Step subagents that write or modify tests/implementation MUST scope the ruff gate to the TASK's changed paths, not the whole repo: run `uv run ruff check --fix <task-changed-paths>` + `uv run ruff format <task-changed-paths>` (e.g., `uv run ruff check --fix src/backend/filemanagement/feature_settings.py src/backend/filemanagement/__init__.py`), then verify with `uv run ruff check .` (expect only the known pre-existing out-of-scope errors). Do NOT run repo-wide `ruff --fix`/`ruff format` during a task step — if repo-wide lint fixes are desired, they are a separate, explicit step (or handled in the verify phase). The orchestrator's task-definitions for implementation/test steps MUST state this ("scope `ruff check --fix`/`ruff format` to the task's changed paths; do not run repo-wide").
- **Date:** 2026-09-13

## P-5 — DAG decomposition flaw: T-002 gate included an integration test needing T-005/T-007 (deadlock)
- **Problem:** T-002's completion gate ("Acceptance tests for AC-052, AC-053 pass") could not be satisfied by T-002 alone. `test_ac_053_unregistered_settings_defaults` is an integration-level test requiring `InMemoryStorageBackend` (T-003), `SqliteFileRepository` (T-004), `FileService.upload` (T-005), and `FileService.upload_avatar` (T-007) — but T-005 depends on T-002 being VERIFIED. This created a deadlock: T-002 could not be VERIFIED until `test_ac_053` passed, but `test_ac_053` needed T-005/T-007. Root cause: the Phase 2 (S2.2) decomposition assigned an integration-level test to a foundation task without checking that the test's runtime dependencies were all available at that task.
- **Step / Phase:** S4.1 Pick task + confirm RED — Phase 4 (T-002); root cause in Phase 2 (S2.2 Decompose)
- **Change:** file-management / FEATURE
- **Duration / iterations:** 1 iteration (caught at S4.1 before implementation, so no rework)
- **Resolution:** DAG correction (decomposition fix, NOT a test weakening — `test_ac_053` preserved, only moved): T-002 narrowed to `[test_ac_052_register_settings]` / `[AC-052]` / gate `"Acceptance test for AC-052 passes"`; T-008 (final task, full stack available) took on `test_ac_053` / `AC-053` / gate `"Acceptance test for AC-053 passes"`. Applied to both task files. Recorded in `docs/verification/file-management.md` ("DAG Correction").
- **Guidance (for future decompositions):** When decomposing a spec into a task DAG (S2.2), for EACH task verify that every test in `tests_to_create` can pass using ONLY that task's implementation plus its declared `dependencies` (already-VERIFIED tasks). If a test needs a component implemented in a LATER task, assign the test to the earliest task where all its runtime dependencies are available (typically the final cross-cutting task). A task's completion gate must be satisfiable by that task alone — otherwise it deadlocks the DAG.
- **Date:** 2026-09-13

## P-4 — Subagent probed/guessed at a ruff issue instead of using `ruff --fix`
- **Problem:** The T-001 implementation subagent (Phase 4) spent tool calls probing/guessing at a ruff issue (probing the project's import-sort/classification behavior with minimal files) instead of just applying the fix. ruff has an auto-fix for most lint issues (import sorting, unused imports, formatting); the subagent should have run `uv run ruff check --fix .` (and `uv run ruff format .`) rather than diagnosing by hand.
- **Step / Phase:** S4.3 Ruff — Phase 4 (T-001)
- **Change:** file-management / FEATURE
- **Duration / iterations:** 1 iteration (subagent stopped by user mid-probe)
- **Resolution / guidance (for future steps):** Step subagents that write or modify tests/implementation MUST run `uv run ruff check --fix .` + `uv run ruff format .` (auto-fix) BEFORE diagnosing any lint issue by hand. Only if `ruff --fix` does not resolve an issue (or the issue is not auto-fixable) should the subagent investigate. The orchestrator's task-definitions for implementation/test steps MUST state this ("use `ruff check --fix .` + `ruff format .`; do not probe/guess at lint issues").
- **Date:** 2026-09-13

## P-2 — S1.1 BLOCKED-USER resume unavailable after subagent retention window
- **Problem:** S1.1 returned BLOCKED-USER (28 questions). The orchestrator completed the user round-trips (7 batches + 1 re-ask + user-initiated Q-29), recorded all answers in AI_Questions.md, and attempted to resume the BLOCKED-USER subagent to complete the step — but the subagent's session had been released after its retention window ("resume is unavailable"). Per the workflow, a non-returning subagent is re-entered with a fresh subagent for the same step.
- **Step / Phase:** S1.1 Interrogate — Phase 1
- **Change:** file-management / FEATURE
- **Duration / iterations:** 2 iterations (initial BLOCKED-USER run + fresh relaunch); ~7 user round-trips
- **Resolution:** relaunched a fresh S1.1 subagent with the recorded answers (it verifies all questions answered, reconciles the brief, and completes the step). Follow-up: the after-workflow-optimization should consider (a) a shorter retention window for BLOCKED-USER subagents, or (b) letting the orchestrator record answers and mark the step done directly when the only remaining work is verification of recorded answers.
- **Date:** 2026-09-13

## P-3 — S1.3 subagent ended prematurely (no handoff)
- **Problem:** The S1.3 Verify self-consistency subagent completed after only 3 tool uses and returned an intermediate statement ("I've read the first part of the spec. Let me read the remainder.") instead of the structured handoff. It did not finish the Self-Consistency Checklist or commit. The spec file was left in the working tree (untracked).
- **Step / Phase:** S1.3 Verify self-consistency — Phase 1
- **Change:** file-management / FEATURE
- **Duration / iterations:** 1 failed run + fresh relaunch
- **Resolution:** relaunched a fresh S1.3 subagent for the same step (it reads the current spec, runs the full checklist, fixes inconsistencies, and commits). Follow-up: the after-workflow-optimization should consider a completion guard for step subagents (a step that does not end with the structured handoff is treated as failed and relaunched).
- **Date:** 2026-09-13

## P-1 — S7.1 done-criteria ambiguous when local `main` lags `origin/main`
- **Problem:** `git branch -d feature/mail-service` emitted the warning "has been merged to 'refs/remotes/origin/feature/mail-service', but not yet merged to HEAD" because the local `main` ref (ff26c4d) lagged `origin/main` (which contains the PR #23 merge). Harmless, but the S7.1 done-criterion "the merge commit is present on `main`" is ambiguous: it must mean reachable from `origin/main` (after `git fetch`), not from the local `main` ref — otherwise a lagging local `main` makes a correct cleanup look incomplete.
- **Step / Phase:** S7.1 Post-merge cleanup — Post-merge
- **Change:** mail-service / FEATURE
- **Duration / iterations:** single run, no relaunch
- **Resolution:** verified against `origin/main` (`git merge-base --is-ancestor <merge-commit> origin/main`); cleanup completed correctly. Follow-up: amend the S7.1 done-criteria in AGENTS.md + git skill to say "reachable from `origin/main` (after fetch)" so future runs don't rely on the local `main` ref.
- **Date:** 2026-09-12
