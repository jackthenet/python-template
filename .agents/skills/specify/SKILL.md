---
name: specify
description: "Single entry point for all change types. Classifies the change (ISSUE, FEATURE, CROSS-CUTTING, REFACTOR, DOCS/CHORE), creates the branch and worktree, and executes the type-specific Phase 1: adversarial interrogation into an approved-quality specification with stable REQ, AC, INV, EDGE, and NFR IDs (FEATURE/CROSS-CUTTING), a triage record (ISSUE), a GREEN baseline (REFACTOR), or a no-behavior scope (DOCS/CHORE). Commits the spec and opens a PR for human review where the type requires it. Use when starting any change from a user request, GitHub issue, or problem description."
---

# Specify

## Purpose

Single entry point for all change types. Classify the change (Phase 0), create its branch and worktree, and execute the type-specific Phase 1:

- **FEATURE / CROSS-CUTTING** — adversarially interrogate the idea into a feature brief, turn the brief into an approved-quality specification with stable IDs and Given/When/Then acceptance criteria (CROSS-CUTTING adds a per-feature impact analysis), commit to `docs/specs/`, and present to a human for approval.
- **ISSUE** — triage: identify the affected REQ/AC from existing approved specs, confirm the defect, and write the reproduction plan. No spec, no PR.
- **REFACTOR** — establish a GREEN baseline and the refactor scope. No spec, no PR.
- **DOCS/CHORE** — define the exact no-behavior scope. No spec, no PR.

## When to Use

- Any change is requested from a user, GitHub issue, or problem description.
- The change idea is not yet concrete enough to start implementation.
- You need to set up the branch, worktree, and type-specific Phase 1 artifact before any implementation.

## Inputs

- A change request (user message, GitHub issue, or problem description).
- The change-type criteria, Phase Matrix, and Escalation Rules in `AGENTS.md`.
- The specification template at `docs/specs/template.md` (FEATURE/CROSS-CUTTING).
- Any existing codebase context relevant to the change.
- The current state of the repository (to pick a clean base branch).

## Execution Context (Atomic Step, Synchronous Subagent)

This phase runs in a **new, synchronous subagent** launched by the orchestrator via the `subagent` tool (see "Phase Execution (Atomic Steps, Synchronous Subagents)" in `AGENTS.md`). The subagent is **never** run in the background — the workflow waits for it to complete and return its handoff.

- **Atomic steps:** execute this phase's atomic steps in order (see the Workflow Diagram in `AGENTS.md`): **S1.1 Interrogate** → **S1.2 Draft spec** → **S1.3 Verify self-consistency** → **S1.4 Present for approval**. Each has a single objective, inputs, expected outputs, and a done criterion.
- **Inputs from the orchestrator:** the change name and type, the change worktree path, this skill file, the previous step's handoff, and the **required skills + context** for the current step (the task-definition).
- **Todo:** the orchestrator manages this phase's todo item (`in_progress` before launch, `completed` after verifying the handoff). The subagent never touches the todo list.
- **User questions (the trigger):** do NOT call `ask_user_question`. When you meet an ambiguity, missing requirement, or decision that requires user input, **record a question in `AI_Questions.md`** (step, why needed, context, question, answer, status, incorporated) and return `BLOCKED-USER`. The orchestrator presents the question to the user, records the answer in `AI_Questions.md`, and relaunches this subagent with the answer.
- **Handoff:** end with the structured handoff required by `AGENTS.md`: `status` / `gate` / `artifacts` / `questions` / `problem` / `next`.
- **Scope:** execute exactly this phase's atomic steps. Do not execute another phase, do not launch a subagent, do not talk to the user.

## Todo

Per the AGENTS.md Todo Tracking Discipline, the orchestrator (not this subagent) creates the change's full todo set in Phase 0 and manages the Phase 1 item: `in_progress` before launching this subagent, `completed` after verifying the handoff (spec PR opened / triage recorded / GREEN baseline / scope recorded).

## Atomic Steps (FEATURE / CROSS-CUTTING)

The FEATURE/CROSS-CUTTING path is decomposed into four atomic steps. Each has a **single objective**, **inputs**, **outputs**, and a **done criterion**. The task-definition points at the specific step to execute; the subagent executes exactly that step (and only that step).

### S1.1 Interrogate

- **Objective:** Adversarially interrogate the feature idea to discover ambiguity, hidden requirements, edge cases, and scope boundaries; capture a feature brief.
- **Inputs:** the feature idea; the existing features' specs in `docs/specs/` (to check overlap); the change worktree.
- **Outputs:** a feature brief (goals, constraints, out-of-scope, edge cases) — intermediate, folded into the spec (not a separate `.brief.md`); the questions recorded in `AI_Questions.md`.
- **Done-criteria:** at least 20 questions asked and recorded in `AI_Questions.md` in **one** `BLOCKED-USER` batch (the orchestrator presents the batch in as few `ask_user_question` rounds as possible, ≤ 4 per round, most blocking first); the feature brief captures goals, constraints, out-of-scope, edge cases; existing features' specs checked for overlap (no double work).
- **MUST create questions** (the trigger): record each question in `AI_Questions.md` (step S1.1, why needed, context, question, answer, status, incorporated). Do NOT call `ask_user_question`.

### S1.2 Draft spec

- **Objective:** Turn the feature brief into an approved-quality specification with stable IDs and Given/When/Then acceptance criteria (CROSS-CUTTING adds a per-feature Impact Analysis).
- **Inputs:** the feature brief; the specification template at `docs/specs/template.md`.
- **Outputs:** `docs/specs/<name>.md` with stable `REQ-XXX` / `AC-XXX` / `INV-XXX` / `EDGE-XXX` / `NFR-XXX` IDs and a test strategy.
- **Done-criteria:** every normative requirement has a stable ID; every acceptance criterion is in Given/When/Then form; every invariant/edge/NFR has an ID; the test strategy maps each AC/INV/EDGE to a test category and test function; the file is built incrementally (several small `write`/`edit` calls, not one giant `write`).

### S1.3 Verify self-consistency

- **Objective:** Run the self-consistency checklist against the written specification and fix every inconsistency in the spec itself (never defer to implementation or review).
- **Inputs:** the written specification; the Self-Consistency Checklist (below).
- **Outputs:** a consistent specification (no internal inconsistencies).
- **Done-criteria:** the specification passes the self-consistency checklist (configurability, parameter coverage, REQ↔AC wording, terminology drift, test strategy coverage, ID references, scope consistency, performance budget vs. observability).

### S1.4 Present for approval

- **Objective:** Commit the specification, open a PR for human review, and STOP (present for human approval).
- **Inputs:** the consistent specification.
- **Outputs:** a committed specification file at `docs/specs/<name>.md`; a PR open for human review.
- **Done-criteria:** the specification is committed to `docs/specs/`; a PR is open for human review; the specification has NOT been approved yet (approval is a human action).

## Process

### 0. Classify the change type (Phase 0)

1. Create the change branch **and its worktree** from `main` (or the configured base branch), per the git skill (`.agents/skills/git/SKILL.md`, operation "Create change worktree") and the "Git Worktrees" section of `AGENTS.md`. Branch: `<type>/<name>` (`feature/`, `issue/`, `crosscut/`, `refactor/`, `chore/`). All work for this change happens inside the change worktree. Other changes are in flight in parallel in their own worktrees — stay strictly on this branch/worktree.
2. Classify the change using the **first matching criterion, in this order**:
   - **ISSUE** — fixes a deviation from **approved spec behavior** (a defect); no new behavior is introduced.
   - **FEATURE** — adds externally observable behavior or capability **not covered by an approved spec**.
   - **CROSS-CUTTING** — intentionally spans **two or more features** (new shared capability, architecture change, shared-infrastructure change).
   - **REFACTOR** — restructures existing code **without altering externally observable behavior**.
   - **DOCS/CHORE** — **does not alter behavior** (documentation, comments, configuration, CI, tooling).
3. Record the type in `docs/verification/<name>.md` (create the file with a type header).
4. Route to the matching Phase 1 path below. If a later step reveals a different type, apply the **Escalation Rules** in `AGENTS.md`.

### A. FEATURE path

Execute the **Atomic Steps (FEATURE / CROSS-CUTTING)** in order: **S1.1 Interrogate** → **S1.2 Draft spec** → **S1.3 Verify self-consistency** → **S1.4 Present for approval**.

Before S1.1, check existing features and specs (no double work): read the specs in `docs/specs/` (all features, including any spec already on the current branch) and the existing feature directories under `src/`; determine what has already been built and what is planned elsewhere; if any part of this feature overlaps an existing or planned feature, reuse or extend that work instead of re-specifying it, and record the overlap in the feature brief.

### B. ISSUE path (triage — no spec, no PR)

27. Identify the affected requirements (`REQ-XXX`) and acceptance criteria (`AC-XXX`) from the **existing approved specs** in `docs/specs/`. Cite the spec files and IDs.
28. Confirm the defect: state the observed behavior and the required behavior (per the cited spec IDs). The observed behavior MUST deviate from what the spec requires.
29. If the fix requires behavior the spec does not state, STOP: open a Spec Amendment PR (Spec Amendment Workflow) or reclassify as FEATURE per the Escalation Rules.
30. Write the reproduction plan: the failing test(s) that reproduce the defect (test names, files), the fix scope, and the files expected to change.
31. Record the triage in `docs/verification/<name>.md` (type: ISSUE, affected REQ/AC, defect confirmation, reproduction plan). Commit: `issue(<name>): triage`.

### C. CROSS-CUTTING path

Execute the **Atomic Steps (FEATURE / CROSS-CUTTING)** in order: **S1.1 Interrogate** → **S1.2 Draft spec** → **S1.3 Verify self-consistency** → **S1.4 Present for approval**. S1.2 additionally requires an **Impact Analysis** section: every affected feature, what changes in each, and which of their REQ/AC IDs are touched.

### D. REFACTOR path (baseline — no spec, no PR)

37. Run the full suite (`uv run pytest tests/ -v`) and confirm it is GREEN. If it is not GREEN, STOP: resolve the pre-existing failures first or reclassify.
38. Record the baseline (suite result, date) in `docs/verification/<name>.md`.
39. Define the refactor scope: which code moves/renames/simplifies, and the invariants that MUST hold (no observable behavior change, no test changes).

### E. DOCS/CHORE path (scope — no spec, no PR)

40. Define the exact non-behavior changes (files, content) and confirm they do not alter externally observable behavior.
41. Record the scope in `docs/verification/<name>.md`. Commit: `chore(<name>): scope`.

## Self-Consistency Checklist

Run this against the written specification before presenting it for approval. Fix every failure in the spec itself (never defer to implementation or review).

- **Configurability**: every "configurable X" / "X can be set" claim names a real parameter in the API/signature, and that parameter has a stated default or a matching AC. No aspirational parameters that don't exist.
- **Parameter coverage**: every parameter in the API/signature is either configurable-by-spec or has a stated default. No orphan parameters.
- **REQ↔AC wording**: every AC's Given/When/Then is consistent with the REQ it satisfies — same terms, no contradictory or stricter/looser wording.
- **Terminology drift**: every defined term (e.g., "private method", "public method") is used consistently in every definition, example, and AC. The definition and every example must agree (if "private" means "underscore-prefixed", no example uses a non-underscore name).
- **Test strategy coverage**: every normative ID (REQ/AC/INV/EDGE/NFR) appears in the test strategy with a test category and test function.
- **ID references**: every cross-reference (e.g., "see REQ-005", "per AC-011") points to an ID that exists.
- **Scope consistency**: every in-scope item has at least one REQ; every out-of-scope item is not accidentally covered by a REQ/AC. CROSS-CUTTING additionally: the Impact Analysis names every affected feature and the REQ/AC IDs it touches.
- **Performance budget vs. observability**: every performance budget that covers an operation which the observability table requires to log must (a) be achievable *including* that per-call logging overhead, and (b) state the logging context (e.g., synchronous console sink) under which the budget is measured. A budget that only holds with logging disabled (or that is unachievable with the mandated logging) is inconsistent.

## Dependency Smoke-Test

Before a **NEW dependency** is named in a spec or ADR, smoke-test it on the host: a minimal `import` plus one representative call, run with a short timeout (e.g., `timeout 15 uv run python -c "import <lib>; <one call>"`). If it segfaults, hangs, or fails on the host, do NOT bake it into the spec/ADR — replace it with a working alternative and record the replacement in an ADR + the verification artifact.

### Capability, not library

A spec/ADR should name the **CAPABILITY** (e.g., "content-based type detection"), not a specific library, so the implementation can choose a working alternative. A specific library may be named as the **default**, but the capability is the normative requirement — if the default library is unusable on the host, the capability still holds.

## Rules

- A change branch **and its worktree** MUST be created before any Phase 1 work (all types).
- The change type MUST be classified (Phase 0) before any other work, and recorded in `docs/verification/<name>.md`.
- Stay strictly on the change's branch/worktree. Do not modify unrelated changes, branches, or worktrees. Keep all changes isolated to this change.
- Ask MORE questions than feels necessary during interrogation (FEATURE/CROSS-CUTTING).
- Ask at least 20 questions during interrogation (FEATURE/CROSS-CUTTING). **Record each in `AI_Questions.md`** and return the **complete batch in a single** `BLOCKED-USER` handoff (the orchestrator presents the batch in as few `ask_user_question` rounds as possible — ≤ 4 per round, most blocking first — records the answers in `AI_Questions.md`, and relaunches this step **once** with the full answer set). Do not return partial batches across multiple round-trips.
- Check other features' specs and the current branch's specs before specifying (FEATURE/CROSS-CUTTING). Reuse or extend existing/planned work — do not do double work.
- The feature brief MUST capture goals, constraints, out-of-scope items, and edge cases. The brief is intermediate — do **not** commit it as a separate `.brief.md` file; fold it into the spec.
- Every normative requirement MUST have a stable `REQ-XXX` ID.
- Every acceptance criterion MUST be in Given/When/Then form with an `AC-XXX` ID.
- Every invariant MUST have an `INV-XXX` ID.
- Every edge case MUST have an `EDGE-XXX` ID.
- Every non-functional requirement MUST have an `NFR-XXX` ID.
- The specification MUST be committed to `docs/specs/` and presented to a human for approval before implementation (FEATURE/CROSS-CUTTING).
- Build the specification file incrementally with several small `write`/`edit` calls — not one giant `write` call and not multiple full rewrites.
- The specification MUST pass the self-consistency checklist before it is presented for approval (FEATURE/CROSS-CUTTING).
- The ISSUE triage MUST cite existing approved spec IDs (REQ/AC) and confirm the observed-vs-required behavior deviation. The reproduction plan MUST name the failing test(s).
- The CROSS-CUTTING spec MUST include an Impact Analysis naming every affected feature and the REQ/AC IDs it touches.
- The REFACTOR baseline MUST be GREEN before any restructuring.
- The DOCS/CHORE scope MUST confirm no behavior delta.
- Do NOT write implementation code in this phase.
- Do NOT derive acceptance tests in this phase (the ISSUE reproduction test is Phase 3).

## Outputs

- A change branch `<type>/<name>` and its worktree at `<repo-name>-worktrees/<type>/<name>`.
- A recorded change type in `docs/verification/<name>.md`.
- FEATURE/CROSS-CUTTING: a committed specification file at `docs/specs/<name>.md`, a PR open for human review, a clear statement that the specification is awaiting human approval.
- ISSUE: a triage record in `docs/verification/<name>.md` (affected REQ/AC, defect confirmation, reproduction plan).
- REFACTOR: a GREEN baseline and refactor scope in `docs/verification/<name>.md`.
- DOCS/CHORE: a no-behavior scope in `docs/verification/<name>.md`.

## Definition of Done

- The change branch and its worktree exist.
- The change type is classified and recorded in `docs/verification/<name>.md`.
- FEATURE/CROSS-CUTTING:
  - The feature brief captures goals, constraints, out-of-scope items, and edge cases (intermediate — folded into the spec, not a separate file).
  - At least 20 questions were asked during interrogation and **recorded in `AI_Questions.md`** (one `BLOCKED-USER` batch; the orchestrator presents it in as few rounds as possible, ≤ 4 per round, and records the answers).
  - Existing features' specs and the current branch's specs were checked for overlap; no work was double-specified.
  - The specification has stable IDs for every requirement, acceptance criterion, invariant, edge case, and non-functional requirement.
  - The specification passes the self-consistency checklist (no internal inconsistencies).
  - The specification is committed to `docs/specs/`.
  - A PR is open for human review.
  - The specification has NOT been approved yet (approval is a human action).
- ISSUE: the triage record is committed; affected REQ/AC are cited; the defect is confirmed (observed vs. required); the reproduction plan names the failing test(s).
- REFACTOR: the baseline is GREEN and recorded; the refactor scope is defined.
- DOCS/CHORE: the scope is recorded; no behavior delta is confirmed.
- No implementation code has been written.
