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

## P-1 — S7.1 done-criteria ambiguous when local `main` lags `origin/main`
- **Problem:** `git branch -d feature/mail-service` emitted the warning "has been merged to 'refs/remotes/origin/feature/mail-service', but not yet merged to HEAD" because the local `main` ref (ff26c4d) lagged `origin/main` (which contains the PR #23 merge). Harmless, but the S7.1 done-criterion "the merge commit is present on `main`" is ambiguous: it must mean reachable from `origin/main` (after `git fetch`), not from the local `main` ref — otherwise a lagging local `main` makes a correct cleanup look incomplete.
- **Step / Phase:** S7.1 Post-merge cleanup — Post-merge
- **Change:** mail-service / FEATURE
- **Duration / iterations:** single run, no relaunch
- **Resolution:** verified against `origin/main` (`git merge-base --is-ancestor <merge-commit> origin/main`); cleanup completed correctly. Follow-up: amend the S7.1 done-criteria in AGENTS.md + git skill to say "reachable from `origin/main` (after fetch)" so future runs don't rely on the local `main` ref.
- **Date:** 2026-09-12
