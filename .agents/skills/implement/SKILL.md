---
name: implement
description: Implements the minimum behavior required to turn failing acceptance tests (RED) into passing tests (GREEN), then refactors to improve code structure without changing specified behavior. Follows feature boundaries, records evidence, re-runs tests after every meaningful refactoring step, and passes quality gates. Use when an approved specification and failing acceptance tests exist, and implementation is needed to achieve GREEN.
---

# Implement

## Purpose

Implement the minimum behavior required to turn failing acceptance tests (RED) into passing tests (GREEN), then refactor to improve code structure without changing specified behavior. Follow feature boundaries, record evidence, re-run tests after every meaningful refactoring step, and pass quality gates.

## When to Use

- An approved specification and failing acceptance tests (RED) exist.
- Implementation is needed to achieve GREEN.
- A ready task from the task DAG is available to execute.
- Implementation is GREEN and code structure needs improvement (duplication, complexity, naming, boundaries).

## Inputs

- An approved specification at `docs/specs/[feature-name].md`.
- Failing acceptance tests (RED) in `tests/`.
- A ready task from the task DAG at `docs/tasks/[feature-name].tasks.json`.

## Process

### 1. Red (failing tests)

1. Pick a ready task from the task DAG.
2. **QA Agent (Red):** Write failing tests in `allowed_files.test_files`. Run `red_command`. Confirm tests FAIL.
3. **Record RED evidence** in `docs/verification/[feature-name].md`.

### 2. Green (minimum implementation)

4. **Coder Agent (Green):** Implement logic in `allowed_files.source_files` following `implementation_steps`. Run `green_command`. Confirm tests PASS 100%.
5. **Record GREEN evidence** in `docs/verification/[feature-name].md`.

### 3. Refactor (improve structure, keep GREEN)

6. **Refactor:** Identify code structure issues (duplication, complexity, naming, boundaries). Make small, focused refactoring changes without changing observable behavior. Re-run `green_command` after every meaningful refactoring step. Confirm GREEN is maintained.

### 4. Commit & update status

7. **Commit & Update Status:** Set `"status": "VERIFIED"` in `.github/task-runner/tasks.json`. Sync final statuses back to `docs/tasks/[feature-name].tasks.json`.

## Rules

- Implementation MUST follow the `implementation_steps` in the task DAG.
- Implementation MUST only touch `allowed_files.source_files`.
- Tests MUST only be touched in `allowed_files.test_files`.
- RED evidence MUST be recorded before implementation.
- GREEN evidence MUST be recorded after implementation.
- Refactoring MUST NOT change observable behavior.
- Tests MUST be re-run after every meaningful refactoring step.
- GREEN MUST be maintained throughout refactoring.
- The task status MUST be set to `VERIFIED` when complete.
- Do NOT modify the specification in this phase.
- Do NOT weaken or delete acceptance tests.
- Do NOT add new behavior during refactoring.

## Outputs

- Implemented logic in `allowed_files.source_files`.
- Improved code structure (refactored, GREEN maintained).
- RED and GREEN evidence in `docs/verification/[feature-name].md`.
- Updated task status in `.github/task-runner/tasks.json` and `docs/tasks/[feature-name].tasks.json`.

## Definition of Done

- The task's acceptance tests pass (GREEN).
- RED and GREEN evidence are recorded.
- The code structure is improved with observable behavior unchanged.
- The test suite is GREEN after refactoring.
- The task status is set to `VERIFIED`.
- The specification was not modified.
