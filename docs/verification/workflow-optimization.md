# Verification — workflow-optimization (DOCS/CHORE)

## Change Type
- **Type:** DOCS/CHORE
- **Purpose:** Fix the 10 logged workflow problems (P-1..P-10 in `docs/workflow/PROBLEMS.md`) by updating the workflow documentation (AGENTS.md + the decompose/specify/test/git skills), and mark the problems Solved.
- **Behavior delta:** NONE. Only workflow documentation is changed. No source (`src/`), no tests (`tests/`), no spec (`docs/specs/`) changes.

## Scope (exact non-behavior changes)

### 1. `AGENTS.md`
- **Ruff gate (P-4, P-6):** Amend the "Ruff gate" rule so step subagents scope `uv run ruff check --fix` + `uv run ruff format` to the TASK's changed paths (not repo-wide). Repo-wide `--fix`/`format` during a task step is forbidden (it modifies out-of-scope files and can introduce new errors, as in P-6). A repo-wide lint fix is a separate, explicit step (or the verify phase).
- **Completion guard (P-3, P-7):** Add a rule to the Phase Execution / Execution Model section: a step subagent MUST end with the structured handoff; a step that does not (e.g., ends with an intermediate statement) is treated as a FAILED step and relaunched with a fresh subagent.
- **BLOCKED-USER retention (P-2):** Add a rule: when a BLOCKED-USER subagent's session is released (resume unavailable) and the only remaining work is verifying already-recorded answers, the orchestrator may record the answers, mark the step done directly, and commit — without relaunching.

### 2. `.agents/skills/decompose/SKILL.md`
- **DAG validation (P-5, P-8, P-9):** Add a validation step to the decompose procedure: for EACH task, verify that every test in `tests_to_create` can pass using ONLY that task's implementation plus its declared `dependencies` (already-VERIFIED tasks). Distinguish **service** methods (called on the service instance) from **repository** methods (called on the repository instance) — only service methods of a LATER task create a deadlock. A task's completion gate must be satisfiable by that task alone.
- **Narrowed gate coverage (P-10):** Add a note: when a task's gate is narrowed (a DAG correction), record that the un-exercised path(s) must be covered by the task that DOES exercise them (so a latent bug in the narrowed task's code is caught by the later task's tests).

### 3. `.agents/skills/specify/SKILL.md`
- **Dependency smoke-test (the python-magic issue):** Add a rule: before a NEW dependency is named in a spec/ADR, smoke-test it on the host (a minimal import + one representative call, with a short timeout). If it segfaults, hangs, or fails, replace it with a working alternative (record the replacement in an ADR + the verification artifact).
- **Capability, not library:** Add a rule: a spec/ADR should name the CAPABILITY (e.g., "content-based type detection"), not a specific library, so the implementation can choose a working alternative. A specific library may be named as the default, but the capability is the normative requirement.

### 4. `.agents/skills/test/SKILL.md`
- **Pre-flight collection check:** Add a rule: before (and after) deriving tests, run `uv run pytest --collect-only <test-directory>` to confirm the test files collect cleanly (no import/collection errors). Surface and fix collection blockers (e.g., pre-existing test-infrastructure bugs) before the RED gate, not during it.

### 5. `.agents/skills/git/SKILL.md`
- **S7.1 done-criteria (P-1):** Amend the Post-merge cleanup done-criteria to say the merge is verified as "reachable from `origin/main` (after `git fetch`)" — not from the local `main` ref (which may lag).

### 6. `docs/workflow/PROBLEMS.md`
- **Mark Solved:** Mark P-1 through P-10 as **Solved** (add a `- **Status:** Solved (<date>)` line to each, noting the fix location).

## No-Behavior-Delta Confirmation
- Only the 6 files above are changed (all workflow documentation).
- No `src/`, `tests/`, or `docs/specs/` changes.
- The changes are guidance/rules for future workflow runs; they do not affect the already-merged file-management feature or any executable behavior.
