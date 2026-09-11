# Verification: todo-tracking

## Type
DOCS/CHORE — agent-instructions documentation only. No `src/`, `test/`, or behavior change.

## Scope (exact non-behavior changes)
The Spec-TDD workflow in AGENTS.md did not reference the `todo` tool. This change adds a **Todo Tracking Discipline** so every in-flight change is tracked as linked todos with explicit status orders at each phase.

### Files changed
1. **`Agents.md`**
   - New section **"Todo Tracking Discipline (todo tool)"** (after *Skill-to-Phase Mapping*): create one todo per workflow step the change type runs, link them with `blockedBy` in phase order, and the status orders — `in_progress` before starting a step (exactly one at a time), `completed` immediately when the step's type-specific gate passes; per-type example todo sets; reclassification handling; post-merge cleanup as a first-class todo.
   - **Agent Prohibitions**: new bullet — MUST NOT advance a phase without the todo status discipline.
   - **Agent Obligations**: new item — MUST track the change with the `todo` tool per the discipline.
2. **Skill pointers** (concise `## Todo` section in each, placed before the main-work section): `specify`, `decompose`, `test`, `implement`, `verify`, `review`, `git` — each gives the step-specific `in_progress`/`completed` order for that phase.

### No-behavior confirmation
- Only `.md` files are modified (AGENTS.md + 7 skill SKILL.md files).
- No `src/`, `test/`, `pyproject.toml`, or CI changes. Externally observable behavior is unchanged.

## Evidence
- `git diff main --name-only` → only `.md` files (7 skill SKILL.md + `Agents.md` + `docs/verification/todo-tracking.md`).
- `uv run ruff check .` → **All checks passed!** (repo still lints clean).
- Internal consistency: every phase the type runs (per the Phase Matrix) has a todo item + a status order in the new section; skipped phases get no item (shown in the ISSUE example).
