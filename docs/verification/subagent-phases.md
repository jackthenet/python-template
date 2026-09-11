# Verification: subagent-phases

## Type
DOCS/CHORE — agent-instruction/documentation files only. No `src/`, no `tests/`, no `pyproject.toml`, no CI, no tooling. No behavior change.

## Scope (exact non-behavior changes)

### Goal
Change the phase workflow so that each workflow step is executed by a **new subagent** via the `subagent` tool (fresh context per step; the orchestrating agent never executes a phase itself).

### Files changed (all Markdown instruction files)
1. **`AGENTS.md`**
   - New section **"Phase Execution (Subagents)"** (after the *Skill-to-Phase Mapping* table) defining:
     - Orchestrator vs. step-subagent roles.
     - Which steps get a subagent: Phases 1–6 + post-merge cleanup; Phase 0 stays on the orchestrator.
     - The orchestrator's launch contract: change name/type, worktree path, phase skill file, previous step's handoff, required handoff output.
     - The step subagent's structured handoff output: `status` / `gate` / `artifacts` / `questions` / `next`.
     - User-question routing: the subagent never calls `ask_user_question` — it returns `BLOCKED-USER`; the orchestrator presents the questions to the user and resumes the **same** subagent with the answers.
     - One subagent per step execution (re-entries get new subagents).
     - Handoff verification by the orchestrator before marking the step's todo completed.
     - The fast-path exception bypasses the workflow entirely.
   - **"Todo Tracking Discipline (todo tool)"**: note that todo management belongs to the orchestrator (step subagents never touch the todo list) and that the orchestrator marks a step `in_progress` before launching its subagent and `completed` after verifying the handoff.
   - **Agent Prohibitions**: matching new bullet — no executing a workflow phase directly in the orchestrator's context.
   - **Agent Obligations**: matching new item — execute each workflow step in a new subagent via the `subagent` tool; verify each handoff.
2. **Skill files** — `.agents/skills/specify/SKILL.md`, `.agents/skills/decompose/SKILL.md`, `.agents/skills/test/SKILL.md`, `.agents/skills/implement/SKILL.md`, `.agents/skills/verify/SKILL.md`, `.agents/skills/review/SKILL.md`
   - New section **"Execution Context (Subagents)"** in each (inserted before its `## Todo` section) stating:
     - This phase runs in a new subagent launched by the orchestrator via the `subagent` tool.
     - Inputs from the orchestrator: change name/type, worktree path, this skill file, previous step's handoff.
     - The orchestrator manages the phase's todo item.
     - Do NOT call `ask_user_question` (return questions in the handoff as `BLOCKED-USER`).
     - End with the structured handoff.
     - Execute exactly this phase only (no other phase, no subagent launches, no user contact).
   - Each skill's existing `## Todo` section updated to state the orchestrator (not the subagent) manages the phase's todo item.
   - **`specify` only**: re-route the 20-question interrogation so the subagent returns questions in the handoff in batches of up to 4 per round-trip (the orchestrator presents them to the user and resumes the subagent with the answers) instead of calling `ask_user_question` itself — update step 13 and the matching Rules bullet.
3. **`.agents/skills/git/SKILL.md`**
   - New **"Execution Context (Subagents)"** note:
     - "Create change worktree" stays on the orchestrator (Phase 0).
     - "Create PR" runs inside the Phase 6 (review) subagent.
     - "Post-merge cleanup" runs in a new subagent (a workflow step launched by the orchestrator after the human merges the PR).
     - "Inspect / recover" may be used by the orchestrator or any step subagent as needed.

### No-behavior confirmation
- Only instruction/documentation Markdown files are modified (`AGENTS.md` + 7 skill `SKILL.md` files + this verification record).
- No `src/`, `tests/`, `pyproject.toml`, CI, or tooling changes.
- The runtime behavior of the project code is unchanged.

## Verification Report (Phase 5 — DOCS/CHORE path)

Commit under verification: `c3444ae` (`chore(subagent-phases): subagent-per-phase execution protocol`) on branch `chore/subagent-phases`.

| # | Check | Status | Evidence |
|---|-------|--------|----------|
| 1 | Diff vs `main` touches ONLY Markdown instruction files | PASS | `git diff main...HEAD --name-status` shows exactly: `M Agents.md`, `M .agents/skills/specify/SKILL.md`, `M .agents/skills/decompose/SKILL.md`, `M .agents/skills/test/SKILL.md`, `M .agents/skills/implement/SKILL.md`, `M .agents/skills/verify/SKILL.md`, `M .agents/skills/review/SKILL.md`, `M .agents/skills/git/SKILL.md`, `A docs/verification/subagent-phases.md` — 9 files, all Markdown instruction files. |
| 2 | No `src/`, no `tests/`, no `pyproject.toml`, no CI, no tooling touched | PASS | The diff name-status above contains no path under `src/`, `tests/`, `.github/`, no `pyproject.toml`, and no tooling/config files. |
| 3 | Lint: `uv run ruff check .` | PASS | `All checks passed!` |
| 4 | Type checks: `uv run mypy src/` | PASS | `Success: no issues found in 33 source files` |
| 5 | No test files or behavior touched | PASS | No `tests/` paths in the diff; only agent-instruction Markdown changed; no behavior delta (DOCS/CHORE scope confirmed in Phase 1). |

**Gate result (DOCS/CHORE): PASS** — lint and type checks pass where applicable; no test files or behavior were touched; the diff is confined to the scoped Markdown instruction files.

## Evidence
- Scope recorded (Phase 1, DOCS/CHORE path, specify skill section E, steps 40–41); no behavior delta confirmed.
- Phase 5 verification report recorded above; all DOCS/CHORE checks PASS (commit `c3444ae`).
- Remaining phase (6 Review) will record its evidence here.
