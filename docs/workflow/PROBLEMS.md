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
