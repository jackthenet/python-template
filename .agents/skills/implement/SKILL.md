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

## Process

### 1. Red (failing tests) — FEATURE/CROSS-CUTTING/ISSUE

1. FEATURE/CROSS-CUTTING: pick a ready task from the task DAG.
2. **QA Agent (Red):** Write failing tests in `allowed_files.test_files`. Run `red_command`. Confirm tests FAIL.
3. **ISSUE:** confirm the reproduction test from Phase 3 fails on the current (defective) code.
4. **Record RED evidence** in `docs/verification/[name].md`.

### 2. Green (minimum implementation) — FEATURE/CROSS-CUTTING/ISSUE

5. **Coder Agent (Green):** Implement logic in `allowed_files.source_files` following `implementation_steps` (FEATURE/CROSS-CUTTING) or the triage's fix scope (ISSUE). Run `green_command`. Confirm tests PASS 100%.
6. **Record GREEN evidence** in `docs/verification/[name].md`.

### 3. Refactor (improve structure, keep GREEN) — FEATURE/CROSS-CUTTING

7. **Refactor:** Identify code structure issues (duplication, complexity, naming, boundaries). Make small, focused refactoring changes without changing observable behavior. Re-run `green_command` after every meaningful refactoring step. Confirm GREEN is maintained.

### 4. REFACTOR (behavior-preserving steps)

8. Perform small, focused behavior-preserving steps per the refactor scope. Re-run the full suite (`uv run pytest tests/ -v`) after every step; it MUST stay GREEN.
9. Do not modify, weaken, or delete any test.

### 5. DOCS/CHORE (make the change)

10. Make the scoped non-behavior changes. Do not touch test files or behavior.

### 6. Commit & update status — FEATURE/CROSS-CUTTING

11. **Commit & Update Status:** Set `"status": "VERIFIED"` in `.github/task-runner/tasks.json`. Sync final statuses back to `docs/tasks/[name].tasks.json`.

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
- The test suite is GREEN after refactoring.
- The task status is set to `VERIFIED`.
- The specification was not modified.
