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

## Execution Context (Atomic Step, Synchronous Subagent)

This phase runs in a **new, synchronous subagent** launched by the orchestrator via the `subagent` tool (see "Phase Execution (Atomic Steps, Synchronous Subagents)" in `AGENTS.md`). The subagent is **never** run in the background — the workflow waits for it to complete and return its handoff.

- **Atomic steps:** execute this phase's atomic steps in order (see the Workflow Diagram in `AGENTS.md`): **S2.1 Create ADRs** → **S2.2 Decompose into task DAG** (copy to `.github/task-runner/tasks.json`). Each has a single objective, inputs, expected outputs, and a done criterion.
- **Inputs from the orchestrator:** the change name and type, the change worktree path, this skill file, the previous step's handoff, and the **required skills + context** for the current step (the task-definition).
- **Todo:** the orchestrator manages this phase's todo item (`in_progress` before launch, `completed` after verifying the handoff). The subagent never touches the todo list.
- **User questions (the trigger):** do NOT call `ask_user_question`. When you meet an ambiguity, missing requirement, or decision that requires user input, **record a question in `AI_Questions.md`** (step, why needed, context, question, answer, status, incorporated) and return `BLOCKED-USER`. The orchestrator presents the question to the user, records the answer in `AI_Questions.md`, and relaunches this subagent with the answer.
- **Handoff:** end with the structured handoff required by `AGENTS.md`: `status` / `gate` / `artifacts` / `questions` / `problem` / `next`.
- **Scope:** execute exactly this phase's atomic steps. Do not execute another phase, do not launch a subagent, do not talk to the user.

## Todo

Per the AGENTS.md Todo Tracking Discipline, the orchestrator (not this subagent) manages the Phase 2 item: `in_progress` before launching this subagent; `completed` only after verifying the handoff that the task DAG is initialized (copied to `.github/task-runner/tasks.json`).

## Atomic Steps

The decompose phase is decomposed into two atomic steps. Each has a **single objective**, **inputs**, **outputs**, and a **done criterion**. The task-definition points at the specific step to execute; the subagent executes exactly that step (and only that step).

### S2.1 Create ADRs

- **Objective:** Create ADRs in `docs/decisions/` for significant design decisions (WHY, not WHAT) — or record a justified skip when none qualify.
- **Inputs:** the approved specification; the significant design decisions to record.
- **Threshold (when an ADR is required):** a decision that introduces a **new dependency**, a **new pattern/architecture element**, or a **cross-feature interface**. A small change (no new dependency, no new pattern, impact confined to one feature and a handful of files) qualifies for **no** ADRs.
- **Outputs:** ADRs in `docs/decisions/` — or, when nothing qualifies, the skip + rationale recorded in `docs/verification/[name].md`.
- **Done-criteria:** an ADR is created for every significant design decision (WHY, not WHAT); the ADRs (or the skip + rationale) are committed.

### S2.2 Decompose into task DAG

- **Objective:** Decompose the spec into a machine-readable JSON task DAG at `docs/tasks/[name].tasks.json`, then copy it to `.github/task-runner/tasks.json` to initialize the active build environment.
- **Inputs:** the approved specification; the existing task DAG format (see `docs/tasks/`).
- **Outputs:** a committed task DAG at `docs/tasks/[name].tasks.json`; the task DAG copied to `.github/task-runner/tasks.json`.
- **Done-criteria:** the task DAG is machine-readable JSON; every task specifies `requirements`, `acceptance_criteria`, `tests_to_create`, `red_command`, `implementation_steps`, `green_command`, `design_constraints`, and `completion_gates`; CROSS-CUTTING tasks are grouped by affected feature; the task DAG is copied to `.github/task-runner/tasks.json`; the ADRs and the task DAG are committed.

## Process

1. Verify the specification is approved — read the **cached** approval result from `docs/verification/[name].md` (verified once before Phase 2; do NOT re-run `git log main -- ...`). If the cached result is missing (re-entry), run the check once and record it.
2. Create ADRs in `docs/decisions/` for significant design decisions (WHY, not WHAT).
3. Decompose the spec into a machine-readable JSON task DAG at `docs/tasks/[name].tasks.json`.
4. For each task, specify:
   - `requirements`: REQ-XXX IDs covered by this task.
   - `acceptance_criteria`: AC-XXX IDs covered by this task.
   - `tests_to_create`: Test functions to write (MUST come before implementation scope).
   - `red_command`: Command to confirm RED state — **targeted** (the task's `tests_to_create` + directly affected tests), not the full suite.
   - `implementation_steps`: Explicit steps for implementation.
   - `green_command`: Command to confirm GREEN state — **targeted** (the task's tests), not the full suite (the full suite is a Phase 5 gate).
   - `design_constraints`: Constraints that must be respected.
   - `completion_gates`: Gates that must pass before the task is complete.
5. CROSS-CUTTING: group tasks by affected feature so each feature's changes are independently verifiable.
6. Copy `docs/tasks/[name].tasks.json` to `.github/task-runner/tasks.json` to initialize the active build environment.
7. Commit the ADRs and the task DAG.

## DAG Validation (gate satisfiability)

Before the task DAG is considered complete, validate gate satisfiability. For **each** task, verify that every test in `tests_to_create` can pass using **only** that task's implementation plus its declared `dependencies` (already-VERIFIED tasks). Distinguish **service** methods (called on the service instance, e.g., `FileService.get_file`/`download`/`delete`/`list_files`) from **repository** methods (called on the repository instance) — only **service methods of a LATER task** create a deadlock (a task cannot be VERIFIED until a test passes, but the test needs a task that depends on it). A task's completion gate must be satisfiable by that task alone. If a test needs a component implemented in a LATER task, assign the test to the **earliest task where all its runtime dependencies are available** (typically the final cross-cutting task), and move it (do not delete it — a DAG correction is a decomposition fix, not a test weakening).

### Narrowed gate coverage

When a task's gate is narrowed (a DAG correction), record that the **un-exercised path(s)** must be covered by the task that DOES exercise them. A narrowed gate may leave a code path untested in that task (e.g., a repository's same-key replacement path), so a latent bug can surface later — the later task that exercises the path is responsible for catching it.

## Rules

- ADRs MUST be created for significant design decisions (WHY, not WHAT) — per the S2.1 threshold (new dependency, new pattern/architecture element, or cross-feature interface); a small change records a justified skip instead.
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

- ADRs are created for significant design decisions (or a justified skip is recorded for a small change, per the S2.1 threshold).
- The task DAG is committed to `docs/tasks/`.
- Every task has requirements, acceptance_criteria, tests_to_create, red_command, implementation_steps, green_command, design_constraints, and completion_gates.
- The task DAG is copied to `.github/task-runner/tasks.json`.
- No implementation code has been written.
