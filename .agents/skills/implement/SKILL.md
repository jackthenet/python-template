---
name: implement
description: Implements the minimum behavior required to turn failing tests (RED) into passing tests (GREEN) (FEATURE/CROSS-CUTTING/ISSUE), performs behavior-preserving restructuring steps (REFACTOR), or makes scoped non-behavior changes (DOCS/CHORE), then refactors to improve code structure without changing specified behavior. Follows feature boundaries, records evidence, re-runs tests after every meaningful step, and passes quality gates. Use when implementation is needed to achieve GREEN.
---

# Implement

## Purpose

Implement the change: turn failing tests (RED) into passing tests (GREEN) (FEATURE/CROSS-CUTTING/ISSUE), perform behavior-preserving restructuring steps (REFACTOR), or make scoped non-behavior changes (DOCS/CHORE). Follow feature boundaries, record evidence, re-run tests after every meaningful step, and pass quality gates.

## When to Use

- FEATURE/CROSS-CUTTING: an approved specification and failing acceptance tests (RED) exist; a ready task from the task DAG is available.
- ISSUE: a triage record and a failing reproduction test (RED) exist.
- REFACTOR: a GREEN baseline and refactor scope exist.
- DOCS/CHORE: a no-behavior scope exists.
- Implementation is GREEN and code structure needs improvement (duplication, complexity, naming, boundaries).

## Inputs

- FEATURE/CROSS-CUTTING: an approved specification at `docs/specs/[name].md`, failing acceptance tests (RED) in `tests/`, a ready task from the task DAG at `docs/tasks/[name].tasks.json`.
- ISSUE: the triage record at `docs/verification/[name].md`, the failing reproduction test (RED) in `tests/`.
- REFACTOR: the baseline + scope at `docs/verification/[name].md`.
- DOCS/CHORE: the scope at `docs/verification/[name].md`.

## Execution Context (Atomic Step, Synchronous Subagent)

This phase runs in a **new, synchronous subagent** launched by the orchestrator via the `subagent` tool (see "Phase Execution (Atomic Steps, Synchronous Subagents)" in `AGENTS.md`). The subagent is **never** run in the background — the workflow waits for it to complete and return its handoff.

- **Atomic steps:** execute this phase's atomic steps in order (see the Workflow Diagram in `AGENTS.md`): **S4.1 Pick task + confirm RED** → **S4.2 Implement + confirm GREEN** → **S4.3 Ruff** → **S4.4 Refactor (keep GREEN)** → **S4.5 Commit + update status**. Repeat per task in the DAG. Each has a single objective, inputs, expected outputs, and a done criterion.
- **Inputs from the orchestrator:** the change name and type, the change worktree path, this skill file, the previous step's handoff, and the **required skills + context** for the current step (the task-definition).
- **Todo:** the orchestrator manages this phase's todo item (`in_progress` before launch, `completed` after verifying the handoff). The subagent never touches the todo list.
- **User questions (the trigger):** do NOT call `ask_user_question`. When you meet an ambiguity, missing requirement, or decision that requires user input, **record a question in `AI_Questions.md`** (step, why needed, context, question, answer, status, incorporated) and return `BLOCKED-USER`. The orchestrator presents the question to the user, records the answer in `AI_Questions.md`, and relaunches this subagent with the answer.
- **Handoff:** end with the structured handoff required by `AGENTS.md`: `status` / `gate` / `artifacts` / `questions` / `problem` / `next`.
- **Scope:** execute exactly this phase's atomic steps. Do not execute another phase, do not launch a subagent, do not talk to the user.

## Todo

Per the AGENTS.md Todo Tracking Discipline, the orchestrator (not this subagent) manages the Phase 4 item: `in_progress` before launching this subagent; `completed` only after verifying the handoff that GREEN is achieved and recorded in `docs/verification/[name].md`.

## Atomic Steps

The implement phase is decomposed into five atomic steps (repeated per task in the DAG). Each has a **single objective**, **inputs**, **outputs**, and a **done criterion**. The task-definition points at the specific step to execute; the subagent executes exactly that step (and only that step).

### S4.1 Pick task + confirm RED

- **Objective:** Pick a ready task from the task DAG (FEATURE/CROSS-CUTTING) and confirm RED (the task's tests fail before implementation).
- **Inputs:** the task DAG at `docs/tasks/[name].tasks.json`; the failing tests (RED).
- **Outputs:** a picked ready task; RED confirmed (the task's tests fail).
- **Done-criteria:** a ready task is picked from the task DAG; the task's tests are confirmed to FAIL (`red_command`); RED evidence is recorded in `docs/verification/<name>.md`.

### S4.2 Implement + confirm GREEN

- **Objective:** Implement the minimum behavior in `allowed_files.source_files` (following `implementation_steps` or the triage's fix scope) and confirm GREEN (the task's tests pass 100%).
- **Inputs:** the picked task; the failing tests (RED).
- **Outputs:** implemented logic in `allowed_files.source_files`; GREEN confirmed (the task's tests pass 100%).
- **Done-criteria:** the implementation follows `implementation_steps` (FEATURE/CROSS-CUTTING) or the triage's fix scope (ISSUE); the task's tests PASS 100% (`green_command` — **targeted**: the task's tests, not the full suite; the full suite is a Phase 5 gate); GREEN evidence is recorded in `docs/verification/<name>.md`.

### S4.3 Ruff

- **Objective:** Run ruff and fix any lint errors (formatting, unused imports, etc.) without changing behavior.
- **Inputs:** the implemented code.
- **Outputs:** a clean ruff run.
- **Done-criteria:** ruff is clean on the task's changed paths (`uv run ruff check <changed-paths>`; the whole-repo sweep is a Phase 5 gate); no behavior changed.

### S4.4 Refactor (keep GREEN)

- **Objective:** Improve code structure (duplication, complexity, naming, boundaries) without changing observable behavior; keep GREEN.
- **Inputs:** the implemented code.
- **Outputs:** improved code structure; GREEN maintained.
- **Done-criteria:** the code structure is improved (duplication, complexity, naming, boundaries); the task's tests stay GREEN (`green_command`) after every meaningful refactoring step (the full suite is a Phase 5 gate); if the step made zero file changes (nothing to refactor), the `green_command` re-run is skipped — the GREEN from S4.2/S4.3 still holds; ruff stays clean on the task's changed paths; no observable behavior changed.

### S4.5 Commit + update status

- **Objective:** Commit the implementation and set the task status to `VERIFIED`.
- **Inputs:** the committed-ready implementation.
- **Outputs:** a committed implementation; the task status set to `VERIFIED` in `.github/task-runner/tasks.json` (synced to `docs/tasks/[name].tasks.json`).
- **Done-criteria:** the implementation is committed; the task status is set to `VERIFIED` in `.github/task-runner/tasks.json`; the final statuses are synced back to `docs/tasks/[name].tasks.json`.

## Process

### 1. Red (failing tests) — FEATURE/CROSS-CUTTING/ISSUE

1. FEATURE/CROSS-CUTTING: pick a ready task from the task DAG.
2. **QA Agent (Red):** Write failing tests in `allowed_files.test_files`. Run `red_command`. Confirm tests FAIL.
3. **ISSUE:** confirm the reproduction test from Phase 3 fails on the current (defective) code.
4. **Record RED evidence** in `docs/verification/[name].md`.

### 2. Green (minimum implementation) — FEATURE/CROSS-CUTTING/ISSUE

5. **Coder Agent (Green):** Implement logic in `allowed_files.source_files` following `implementation_steps` (FEATURE/CROSS-CUTTING) or the triage's fix scope (ISSUE). Run `green_command`. Confirm tests PASS 100%.
6. **Record GREEN evidence** in `docs/verification/[name].md`.

### 3. Ruff (lint gate) — FEATURE/CROSS-CUTTING/ISSUE

7. **Ruff:** run `uv run ruff check <changed-paths>` (the task's changed paths; the whole-repo sweep is a Phase 5 gate) after implementation (S4.2) and after refactoring (S4.4). It MUST be clean before the other gates. Fix any lint errors (formatting, unused imports, etc.) without changing behavior.

### 4. Refactor (improve structure, keep GREEN) — FEATURE/CROSS-CUTTING

8. **Refactor:** Identify code structure issues (duplication, complexity, naming, boundaries). Make small, focused refactoring changes without changing observable behavior. Re-run `green_command` and `uv run ruff check <changed-paths>` after every meaningful refactoring step. If the step made zero file changes (nothing to refactor), the `green_command` re-run is skipped — the GREEN from S4.2/S4.3 still holds. Confirm GREEN is maintained and ruff stays clean.

### 5. REFACTOR (behavior-preserving steps)

9. Perform small, focused behavior-preserving steps per the refactor scope. Re-run the full suite (`uv run pytest tests/ -v`) after every step; it MUST stay GREEN.
10. Do not modify, weaken, or delete any test.

### 6. DOCS/CHORE (make the change)

11. Make the scoped non-behavior changes. Do not touch test files or behavior.

### 7. Commit & update status — FEATURE/CROSS-CUTTING

12. **Commit & Update Status:** Set `"status": "VERIFIED"` in `.github/task-runner/tasks.json`. Sync final statuses back to `docs/tasks/[name].tasks.json`.

## Rules

- Implementation MUST follow the `implementation_steps` in the task DAG (FEATURE/CROSS-CUTTING) or the triage's fix scope (ISSUE).
- Implementation MUST only touch `allowed_files.source_files`.
- Tests MUST only be touched in `allowed_files.test_files`.
- RED evidence MUST be recorded before implementation.
- GREEN evidence MUST be recorded after implementation.
- ISSUE: the fix MUST be minimal — no new behavior beyond the affected spec IDs.
- REFACTOR: steps MUST be behavior-preserving; the full suite MUST stay GREEN; no test changes.
- DOCS/CHORE: only the scoped non-behavior changes; no test files, no behavior.
- Refactoring MUST NOT change observable behavior.
- Tests MUST be re-run after every meaningful refactoring step.
- **Ruff MUST be clean** after implementation (S4.2) and after refactoring (S4.4) — run `uv run ruff check <changed-paths>` (the task's changed paths; the whole-repo sweep is a Phase 5 gate) and require it to pass before the other gates.
- GREEN MUST be maintained throughout refactoring.
- The task status MUST be set to `VERIFIED` when complete (FEATURE/CROSS-CUTTING).
- Do NOT modify the specification in this phase.
- Do NOT weaken or delete acceptance tests.
- Do NOT add new behavior during refactoring.

## Outputs

- Implemented logic in `allowed_files.source_files` (FEATURE/CROSS-CUTTING/ISSUE).
- Improved code structure (refactored, GREEN maintained).
- RED and GREEN evidence in `docs/verification/[name].md`.
- Updated task status in `.github/task-runner/tasks.json` and `docs/tasks/[name].tasks.json` (FEATURE/CROSS-CUTTING).

## Definition of Done

- The task's acceptance tests pass (GREEN).
- RED and GREEN evidence are recorded.
- The code structure is improved with observable behavior unchanged.
- The task's tests are GREEN after refactoring (the full suite is a Phase 5 gate).
- The task status is set to `VERIFIED`.
- The specification was not modified.
