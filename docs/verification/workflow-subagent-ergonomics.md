# workflow-subagent-ergonomics — Verification

- **Change type:** DOCS/CHORE
- **Date:** 2026-09-15

## Scope (Phase 1 — DOCS/CHORE)

Exact non-behavior changes. Files to change (and ONLY these) in a later step:

### 1. `AGENTS.md`

- **S3.1 per-task split:** the Phase 3 atomic step "S3.1 Derive tests" becomes per-task in the DAG: one fresh subagent derives one DAG task's `tests_to_create`. Update: (a) the "Atomic Steps" table Phase 3 row, (b) the Workflow Diagram PHASE 3 block, (c) any other S3.1 reference (e.g., the Phase 3 TEST & RED protocol section) so all references stay consistent.
- **Always-fresh subagents (never resume/restore):** in the "One subagent per atomic step" paragraph, REMOVE the exception "The only exception: a `BLOCKED-USER` subagent may be **resumed** to deliver the user's answers, which continues the **same** step (never a different one)." and replace it with: a BLOCKED-USER step is re-entered with a FRESH subagent; the orchestrator includes the user's recorded answers in the new launch prompt. Add the explicit rule: the orchestrator NEVER resumes/restores a previously launched subagent session (its context is full/stale); every (re-)entry — including after BLOCKED-USER, after a failed gate, and after reclassification — launches a new subagent.
- **Naming template:** add the rule that the orchestrator names each step subagent's description `Sx.x: <short objective>` (e.g., `S4.2: implement FileService.upload`); for per-task steps include the task ID (e.g., `S4.2 (T-005): implement FileService.upload`).

### 2. `.agents/skills/test/SKILL.md`

- "Execution Context" bullet listing the atomic steps: mark S3.1 as per-task.
- "Atomic Steps" section: rewrite the S3.1 entry — objective: derive the tests for the single DAG task assigned in the task definition (its `tests_to_create`); inputs: the approved spec + the task definition (task ID, requirements, ACs); outputs: that task's test functions; done-criteria: that task's AC/INV/EDGE tests are committed.

### 3. `docs/workflow/PROBLEMS.md`

- Append the four entries P-11, P-12, P-13, P-14 (exact content provided by the orchestrator — copy verbatim).

## No behavior delta — confirmed

- No `src/` changes.
- No `tests/` changes.
- No `pyproject.toml` changes.
- No `.github/` changes.

All changes are documentation/workflow-ergonomics only; externally observable behavior is unchanged.

## Verification (Phase 5 — DOCS/CHORE)

- **Date:** 2026-09-15

### Check 1 — `git diff d5f0a94..HEAD --stat` (scope: docs-only, no behavior)

```text
.agents/skills/test/SKILL.md                      | 10 +++----
 AGENTS.md                                         |  9 ++++---
 docs/verification/workflow-subagent-ergonomics.md | 32 +++++++++++++++++++++++
 docs/workflow/PROBLEMS.md                         | 32 +++++++++++++++++++++++
 4 files changed, 75 insertions(+), 8 deletions(-)
```

**Result: PASS.** Only the four expected files changed: `AGENTS.md`, `.agents/skills/test/SKILL.md`, `docs/workflow/PROBLEMS.md`, `docs/verification/workflow-subagent-ergonomics.md`. No `src/`, no `tests/`, no `pyproject.toml`, no `.github/`.

### Check 2 — `uv run ruff check .` (lint state)

```text
All checks passed!
```

**Result: PASS.** Identical to main's state; a docs-only change cannot alter it.

### Check 3 — `git status --short` (clean tree)

```text
(no output)
```

**Result: PASS.** Working tree is clean.

### Conclusion

No behavior delta: the change touches no `src/`, no `tests/`, no `pyproject.toml`, no `.github/`; lint state is identical to main (`All checks passed!`); tree clean. DOCS/CHORE light-verify gate passed.

## Review (Phase 6 — DOCS/CHORE)

- **Date:** 2026-09-15
- **Scope basis:** the Phase 1 scope record (above) + the Phase 5 light-verify record (above).

### Check 1 — `git diff d5f0a94..HEAD --stat` (docs-only, no behavior)

```text
.agents/skills/test/SKILL.md                      | 10 ++--
 AGENTS.md                                         |  9 ++-
 docs/verification/workflow-subagent-ergonomics.md | 68 +++++++++++++++++++++++
 docs/workflow/PROBLEMS.md                         | 40 +++++++++++++
 4 files changed, 119 insertions(+), 8 deletions(-)
```

**Result: PASS.** Only `AGENTS.md`, `.agents/skills/test/SKILL.md`, `docs/workflow/PROBLEMS.md`, `docs/verification/workflow-subagent-ergonomics.md`. No `src/`, no `tests/`, no `pyproject.toml`, no `.github/`.

### Check 2 — AGENTS.md content consistency

- S3.1 per-task is consistently marked in all its references: Workflow Diagram (`S3.1 Derive tests (per task in the DAG)`), Atomic Steps table (Phase 3 row), Phase 3 TEST & RED protocol section ("Test derivation is **per task in the DAG** (S3.1)…"). **PASS.**
- The old BLOCKED-USER resume exception sentence ("The only exception: a `BLOCKED-USER` subagent may be **resumed**…") is GONE (`grep "The only exception" AGENTS.md` → no match); the fresh-subagent rule is present ("The orchestrator **NEVER** resumes/restores a previously launched subagent session (its context is full/stale) — every (re-)entry, including after BLOCKED-USER, after a failed gate, and after reclassification, launches a **new** subagent."). **PASS.**
- The naming rule is present ("The orchestrator names each step subagent's description `Sx.x: <short objective>`…; for per-task steps it includes the task ID (e.g., `S4.2 (T-005): implement FileService.upload`)."). **PASS.**

### Check 3 — `.agents/skills/test/SKILL.md`

- The S3.1 entry is per-task and consistent with AGENTS.md: Execution Context bullet marked per-task; S3.1 objective = derive the tests for the single DAG task assigned in the task definition (its `tests_to_create`); inputs include the task definition (task ID, requirements, ACs); outputs = that task's test functions; done-criteria = that task's AC/INV/EDGE/NFR tests committed. **PASS.**

### Check 4 — `docs/workflow/PROBLEMS.md`

- Entries P-11…P-15 are well-formed: each has Problem / Step / Phase / Change / Duration / iterations / Resolution / Date. All are appended after the last pre-existing entry (P-1, 2026-09-12). **PASS.**
- Note: P-15 was added during S5 (S5 edit-loop friction, commit `5eb66b0`) — an expected Problem Log addition within the scoped `PROBLEMS.md` file, not a scope deviation.

### Check 5 — No behavior delta

- Confirmed by the Phase 5 light-verify record: diff limited to the four in-scope files, `uv run ruff check .` → `All checks passed!` (identical to main's state), working tree clean. **PASS.**

### Findings

None.

### Conclusion

**CLEAN.** All five light-review checks pass; no findings. The change is documentation/workflow-ergonomics only, with no behavior delta.
