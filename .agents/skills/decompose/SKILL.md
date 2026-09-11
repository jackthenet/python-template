---
name: decompose
description: Decomposes an approved specification (FEATURE and CROSS-CUTTING changes) into design decisions and a machine-readable JSON task DAG. Creates ADRs for significant design decisions and a task graph where each task covers specific requirements and acceptance criteria with explicit RED/GREEN commands, grouped by affected feature for CROSS-CUTTING. Use when an approved specification exists and needs to be broken into implementable tasks before acceptance testing.
---

# Decompose

## Purpose

Decompose an approved specification into design decisions and a machine-readable JSON task DAG. **Applies to FEATURE and CROSS-CUTTING changes** (the only types that produce a spec). Create ADRs for significant design decisions (WHY, not WHAT) and a task graph where each task covers specific requirements and acceptance criteria with explicit RED/GREEN commands. The task DAG is committed to `docs/tasks/` and copied to `.github/task-runner/tasks.json` to initialize the active build environment.

## When to Use

- An approved specification exists (merged into `main`) for a FEATURE or CROSS-CUTTING change and needs to be broken into implementable tasks.
- Significant design decisions need to be recorded as ADRs.
- A machine-readable task DAG is needed to drive the RED/GREEN implementation loop.

## Inputs

- An approved specification at `docs/specs/[name].md` (merged into `main`).
- Any significant design decisions to record.
- The existing task DAG format (see `docs/tasks/`).

## Todo

Per the AGENTS.md Todo Tracking Discipline: mark the Phase 2 item `in_progress` before starting; `completed` only when the task DAG is initialized (copied to `.github/task-runner/tasks.json`).

## Process

1. Verify the specification is approved (merged into `main`).
2. Create ADRs in `docs/decisions/` for significant design decisions (WHY, not WHAT).
3. Decompose the spec into a machine-readable JSON task DAG at `docs/tasks/[name].tasks.json`.
4. For each task, specify:
   - `requirements`: REQ-XXX IDs covered by this task.
   - `acceptance_criteria`: AC-XXX IDs covered by this task.
   - `tests_to_create`: Test functions to write (MUST come before implementation scope).
   - `red_command`: Command to confirm RED state.
   - `implementation_steps`: Explicit steps for implementation.
   - `green_command`: Command to confirm GREEN state.
   - `design_constraints`: Constraints that must be respected.
   - `completion_gates`: Gates that must pass before the task is complete.
5. CROSS-CUTTING: group tasks by affected feature so each feature's changes are independently verifiable.
6. Copy `docs/tasks/[name].tasks.json` to `.github/task-runner/tasks.json` to initialize the active build environment.
7. Commit the ADRs and the task DAG.

## Rules

- ADRs MUST be created for significant design decisions (WHY, not WHAT).
- The task DAG MUST be machine-readable JSON.
- Every task MUST specify `requirements` (REQ-XXX IDs).
- Every task MUST specify `acceptance_criteria` (AC-XXX IDs).
- Every task MUST specify `tests_to_create` (test functions, before implementation scope).
- Every task MUST specify `red_command`, `implementation_steps`, `green_command`.
- Every task MUST specify `design_constraints` and `completion_gates`.
- CROSS-CUTTING: tasks MUST be grouped by affected feature so each feature's changes are independently verifiable.
- The task DAG MUST be committed to `docs/tasks/`.
- The task DAG MUST be copied to `.github/task-runner/tasks.json`.
- Do NOT write implementation code in this phase.
- Do NOT derive acceptance tests in this phase.

## Outputs

- ADRs in `docs/decisions/`.
- A committed task DAG at `docs/tasks/[name].tasks.json`.
- The task DAG copied to `.github/task-runner/tasks.json`.

## Definition of Done

- ADRs are created for significant design decisions.
- The task DAG is committed to `docs/tasks/`.
- Every task has requirements, acceptance_criteria, tests_to_create, red_command, implementation_steps, green_command, design_constraints, and completion_gates.
- The task DAG is copied to `.github/task-runner/tasks.json`.
- No implementation code has been written.
