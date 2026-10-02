---
name: specify
description: "Single entry point for all change types: runs Phase P (PREPARE) — classifies the change at P.1 (ISSUE, FEATURE, CROSS-CUTTING, REFACTOR, DOCS/CHORE), adversarially interrogates the idea, records the questions in the change's question file and gets them answered, then drafts the type's Phase 1 output (an approved-quality specification with stable REQ, AC, INV, EDGE, and NFR IDs for FEATURE/CROSS-CUTTING, a triage record for ISSUE, a GREEN baseline for REFACTOR, a no-behavior scope for DOCS/CHORE) and verifies it self-consistent — and then Phase 1's S1.4, which commits the prepared spec and opens the approval PR. Use when a change idea is being prepared ahead of the workflow, when starting any change from a user request, GitHub issue, or problem description, or when a prepared (READY) change needs its spec committed and its approval PR opened."
---

# Specify

## Purpose

Single entry point for all change types. Run **Phase P (PREPARE)** — classify the change at **P.1**, interrogate it, get every question answered, produce the type's Phase 1 output, and verify it self-consistent — then run **S1.4** in the normal workflow to commit the prepared spec and open the approval PR.

The skill's output is a **prepared change**: a TODO file (`docs/todo/<name>.md`), a **fully answered** question file (`docs/questions/<name>.md`), and the draft spec / triage / baseline / scope. With that in place the normal workflow (Phases 1–6) runs **without human input** — the only human actions left are merging the spec PR and the change PR (see "Phase P: PREPARE" in `AGENTS.md`).

The former steps **S1.1 / S1.2 / S1.3** are now **P.2 / P.4 / P.5** — same content, run during preparation. Only **S1.4** stays inside the normal workflow, and the change branch and worktree are created at **P.4**, not at classification.

Phase P per change type:

- **FEATURE / CROSS-CUTTING** — adversarially interrogate the idea into a feature brief, turn the brief into an approved-quality specification with stable IDs and Given/When/Then acceptance criteria (CROSS-CUTTING adds a per-feature impact analysis), commit to `docs/specs/`, and present to a human for approval.
- **ISSUE** — triage: identify the affected REQ/AC from existing approved specs, confirm the defect, and write the reproduction plan. No spec, no PR.
- **REFACTOR** — establish a GREEN baseline and the refactor scope. No spec, no PR.
- **DOCS/CHORE** — define the exact no-behavior scope. No spec, no PR.

## When to Use

- Any change is requested from a user, GitHub issue, or problem description.
- The change idea is not yet concrete enough to start implementation.
- A change idea is being prepared ahead of the workflow (Phase P).
- A prepared (READY) change needs its spec committed and its approval PR opened (**S1.4**).
- You need the TODO file, the answered question file, and the type-specific Phase 1 artifact before any implementation.

## Inputs

- A change request (user message, GitHub issue, or problem description).
- The change-type criteria, Phase Matrix, and Escalation Rules in `AGENTS.md`.
- The specification template at `docs/specs/template.md` (FEATURE/CROSS-CUTTING).
- The planning templates at `docs/todo/template.md` and `docs/questions/template.md` (P.1).
- The existing TODO files in `docs/todo/` — one per planned change; the overlap check reads them alongside `docs/specs/`.
- Any existing codebase context relevant to the change.
- The current state of the repository (to pick a clean base branch).

## Execution Context (Atomic Step, Synchronous Subagent)

This phase runs in a **new, synchronous subagent** launched by the orchestrator via the `subagent` tool (see "Phase Execution (Atomic Steps, Synchronous Subagents)" in `AGENTS.md`). The subagent is **never** run in the background — the workflow waits for it to complete and return its handoff.

- **Atomic steps:** execute this skill's atomic steps in order (see the Workflow Diagram in `AGENTS.md`): **P.2 Interrogate** → **P.3 Answer** (orchestrator ⏸) → **P.4 Draft** → **P.5 Verify self-consistency** → **S1.4 Present for approval**. Each has a single objective, inputs, expected outputs, and a done criterion.
- **Ownership:** **P.1 Frame** and **P.3 Answer** are **orchestrator** steps (no subagent); P.2, P.4, P.5 and S1.4 each run in their own subagent. P.2 and P.3 run in the **primary worktree** (no change worktree exists yet); the change branch and worktree are created at **P.4**, and P.5 and S1.4 run inside it.
- **Inputs from the orchestrator:** the change name and type, the change worktree path, this skill file, the previous step's handoff, and the **required skills + context** for the current step (the task-definition).
- **Todo:** the orchestrator manages this phase's todo item (`in_progress` before launch, `completed` after verifying the handoff). The subagent never touches the todo list.
- **User questions (the trigger):** do NOT call `ask_user_question`. When you meet an ambiguity, missing requirement, or decision that requires user input, **record a question in the change's question file `docs/questions/<name>.md`** (step, why needed, context, question, answer, status, incorporated) and return `BLOCKED-USER`. The orchestrator presents the question to the user, records the answer in that file, and relaunches this subagent with the answer.
- **BLOCKED-USER = WAITING, not idle:** a `BLOCKED-USER` handoff puts **this change** in **WAITING** state; the orchestrator presents the questions and continues with another READY change instead of idling, then resumes this change with a fresh subagent (see "Multi-change scheduling (never idle)" in `AGENTS.md`).
- **Handoff:** end with the structured handoff required by `AGENTS.md`: `status` / `gate` / `artifacts` / `questions` / `problem` / `next`.
- **Scope:** execute exactly this phase's atomic steps. Do not execute another phase, do not launch a subagent, do not talk to the user.

## Todo

Per the AGENTS.md Todo Tracking Discipline, the orchestrator (not this subagent) creates the change's todo set at **P.1** and manages the Phase P item: `in_progress` while the P-steps run, `completed` only at the **READY** gate (TODO `Status: READY`, every question `ANSWERED`, the type's Phase 1 output recorded). The Phase 1 item (FEATURE/CROSS-CUTTING only) is `completed` when the spec PR is opened at S1.4.

## Atomic Steps (FEATURE / CROSS-CUTTING)

The FEATURE/CROSS-CUTTING path is decomposed into atomic steps. Each has a **single objective**, **inputs**, **outputs**, and a **done criterion**. The task-definition points at the specific step to execute; the subagent executes exactly that step (and only that step). **P.1 Frame** runs for **every** change type and belongs to the orchestrator.

### P.1 Frame (orchestrator)

- **Objective:** Classify the change type (Phase 0) and open the change's planning record.
- **Inputs:** the change idea; `docs/todo/template.md`; `docs/questions/template.md`; the existing TODO files in `docs/todo/`.
- **Outputs:** `docs/todo/<name>.md` and `docs/questions/<name>.md` created from their templates **on `main`** and committed directly to `main` (git skill, "Commit Phase P planning artifacts"); the change's todo set.
- **Done-criteria:** both files exist on `main` with TODO `Status: PREPARING` and question file `Status: OPEN`; the change type is recorded in the TODO file. No worktree yet — it is created at P.4.

### P.2 Interrogate

- **Objective:** Adversarially interrogate the feature idea to discover ambiguity, hidden requirements, edge cases, and scope boundaries; capture a feature brief.
- **Inputs:** the feature idea; the existing features' specs in `docs/specs/` **and every TODO file in `docs/todo/`** (to check overlap); the primary worktree (no change worktree exists yet).
- **Outputs:** a feature brief (goals, constraints, out-of-scope, edge cases) — intermediate, folded into the spec (not a separate `.brief.md`); the questions recorded in `docs/questions/<name>.md`.
- **Done-criteria:** at least 20 questions asked and recorded in `docs/questions/<name>.md` in **one** `BLOCKED-USER` batch (the orchestrator presents the batch in as few `ask_user_question` rounds as possible, ≤ 4 per round, most blocking first); the feature brief captures goals, constraints, out-of-scope, edge cases; overlap checked against `docs/specs/` **and** every TODO in `docs/todo/` (no double work).
- **MUST create questions** (the trigger): record each question in `docs/questions/<name>.md` (step P.2, why needed, context, question, answer, status, incorporated). Do NOT call `ask_user_question`.

### P.4 Draft spec

- **Objective:** Create the change branch and worktree, then turn the feature brief into an approved-quality specification with stable IDs and Given/When/Then acceptance criteria (CROSS-CUTTING adds a per-feature Impact Analysis).
- **Inputs:** the feature brief; the answered `docs/questions/<name>.md`; the specification template at `docs/specs/template.md`.
- **First action:** create the change branch **and its worktree** from `main` (git skill, "Create change worktree (P.4)") — the branch then carries the TODO file and the answered questions — and only then draft the spec.
- **Outputs:** `docs/specs/<name>.md` with stable `REQ-XXX` / `AC-XXX` / `INV-XXX` / `EDGE-XXX` / `NFR-XXX` IDs and a test strategy.
- **Done-criteria:** every normative requirement has a stable ID; every acceptance criterion is in Given/When/Then form; every invariant/edge/NFR has an ID; the test strategy maps each AC/INV/EDGE to a test category and test function; the file is built incrementally (several small `write`/`edit` calls, not one giant `write`).

### P.5 Verify self-consistency

- **Objective:** Run the self-consistency checklist against the written specification and fix every inconsistency in the spec itself (never defer to implementation or review).
- **Inputs:** the written specification; the Self-Consistency Checklist (below) + the Dependency Smoke-Test (below).
- **Outputs:** a consistent specification (no internal inconsistencies).
- **Done-criteria:** the specification passes the self-consistency checklist (configurability, parameter coverage, REQ↔AC wording, terminology drift, test strategy coverage, ID references, scope consistency, performance budget vs. observability) **and** every newly named dependency has been smoke-tested on the host.

### S1.4 Present for approval

- **Objective:** Commit the specification, open a PR for human review, and STOP (present for human approval).
- **Inputs:** the consistent specification.
- **Outputs:** a committed specification file at `docs/specs/<name>.md`; a PR open for human review.
- **Done-criteria:** the specification is committed to `docs/specs/`; a PR is open for human review; the specification has NOT been approved yet (approval is a human action).

## Process

### 0. Classify the change type (Phase 0, at **P.1 Frame**, in the primary worktree)

1. Classify the change using the **first matching criterion, in this order**:
   - **ISSUE** — fixes a deviation from **approved spec behavior** (a defect); no new behavior is introduced.
   - **FEATURE** — adds externally observable behavior or capability **not covered by an approved spec**.
   - **CROSS-CUTTING** — intentionally spans **two or more features** (new shared capability, architecture change, shared-infrastructure change).
   - **REFACTOR** — restructures existing code **without altering externally observable behavior**.
   - **DOCS/CHORE** — **does not alter behavior** (documentation, comments, configuration, CI, tooling).
2. Create `docs/todo/<name>.md` and `docs/questions/<name>.md` from their templates and commit them **directly to `main`** (git skill, "Commit Phase P planning artifacts") — these two folders are the **only** files the workflow may commit directly to `main`. Create the change's todo set (Phase P item + the phases its type runs). No worktree yet.
3. Record the type in the TODO file, then in `docs/verification/<name>.md` (created with a type header at **P.4**, in the change worktree).
4. Route to the matching path below. If a later step reveals a different type, apply the **Escalation Rules** in `AGENTS.md`.

The change branch **and its worktree** are created at **P.4** — after the answers are recorded, so the branch carries the TODO file and the answered questions — per the git skill (`.agents/skills/git/SKILL.md`, operation "Create change worktree (P.4)") and the "Git Worktrees" section of `AGENTS.md`. Branch: `<type>/<name>` (`feature/`, `issue/`, `crosscut/`, `refactor/`, `chore/`). All work from P.4 onward happens inside the change worktree. Other changes are in flight in parallel in their own worktrees — stay strictly on this branch/worktree.

### A. FEATURE path (runs at **P.2 / P.4 / P.5**, then **S1.4** in the workflow)

Execute the **Atomic Steps (FEATURE / CROSS-CUTTING)** in order: **P.2 Interrogate** → **P.3 Answer** (orchestrator) → **P.4 Draft spec** → **P.5 Verify self-consistency** → **S1.4 Present for approval**.

Before P.2, check existing features and specs (no double work): read the specs in `docs/specs/` (all features, including any spec already on `main`) and every TODO file in `docs/todo/` (every planned change), and the existing feature directories under `src/`; determine what has already been built and what is planned elsewhere; if any part of this feature overlaps an existing or planned feature, reuse or extend that work instead of re-specifying it, and record the overlap in the feature brief.

### B. ISSUE path (triage — no spec, no PR; runs at **P.4**, questions at **P.2**)

27. Identify the affected requirements (`REQ-XXX`) and acceptance criteria (`AC-XXX`) from the **existing approved specs** in `docs/specs/`. Cite the spec files and IDs.
28. Confirm the defect: state the observed behavior and the required behavior (per the cited spec IDs). The observed behavior MUST deviate from what the spec requires.
29. If the fix requires behavior the spec does not state, STOP: open a Spec Amendment PR (Spec Amendment Workflow) or reclassify as FEATURE per the Escalation Rules.
30. Write the reproduction plan: the failing test(s) that reproduce the defect (test names, files), the fix scope, and the files expected to change.
31. Record the triage in `docs/verification/<name>.md` (type: ISSUE, affected REQ/AC, defect confirmation, reproduction plan). Commit: `issue(<name>): triage`.

### C. CROSS-CUTTING path (runs at **P.2 / P.4 / P.5**, then **S1.4** in the workflow)

Execute the **Atomic Steps (FEATURE / CROSS-CUTTING)** in order: **P.2 Interrogate** → **P.3 Answer** (orchestrator) → **P.4 Draft spec** → **P.5 Verify self-consistency** → **S1.4 Present for approval**. P.4 additionally requires an **Impact Analysis** section: every affected feature, what changes in each, and which of their REQ/AC IDs are touched.

### D. REFACTOR path (baseline — no spec, no PR; runs at **P.4**, questions at **P.2**)

37. Run the full suite (`uv run pytest tests/ -v`) and confirm it is GREEN. If it is not GREEN, STOP: resolve the pre-existing failures first or reclassify.
38. Record the baseline (suite result, date) in `docs/verification/<name>.md`.
39. Define the refactor scope: which code moves/renames/simplifies, and the invariants that MUST hold (no observable behavior change, no test changes).

### E. DOCS/CHORE path (scope — no spec, no PR; runs at **P.4**, questions at **P.2**)

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

- A change branch **and its worktree** MUST be created at **P.4**, before any normative artifact is written (all types); before P.4 the work happens in the primary worktree and touches only `docs/todo/` and `docs/questions/`.
- The change type MUST be classified (**P.1**) before any other work, and recorded in the TODO file and in `docs/verification/<name>.md`.
- The TODO file's `Status:` field MUST be updated at each Phase P step: **PREPARING** (P.1) → **QUESTIONS-ANSWERED** (P.3) → **READY** (P.5 gate) → **IN-WORKFLOW** / **WAITING** / **MERGED**.
- A change is **READY** only when **every** question in its question file is `ANSWERED` **and** the P.4 artifact exists (draft spec / triage / baseline / scope) and passed P.5. Only a READY change may enter the normal workflow.
- `docs/todo/` and `docs/questions/` are the **only** files committed directly to `main`; everything normative reaches `main` through a merged PR from the change worktree.
- Stay strictly on the change's branch/worktree. Do not modify unrelated changes, branches, or worktrees. Keep all changes isolated to this change.
- Ask MORE questions than feels necessary during interrogation (FEATURE/CROSS-CUTTING).
- Ask at least 20 questions during interrogation (FEATURE/CROSS-CUTTING). **Record each in the change's question file `docs/questions/<name>.md`** and return the **complete batch in a single** `BLOCKED-USER` handoff (the orchestrator presents the batch in as few `ask_user_question` rounds as possible — ≤ 4 per round, most blocking first — records the answers in that file, and relaunches this step **once** with the full answer set). Do not return partial batches across multiple round-trips.
- Check other features' specs (`docs/specs/`) **and every planned change's TODO file (`docs/todo/`)** before specifying (FEATURE/CROSS-CUTTING). Reuse or extend existing/planned work — do not do double work.
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

**Phase P (the prepared change):**

- `docs/todo/<name>.md` (from `docs/todo/template.md`), committed to `main`, its `Status:` advanced to **READY**.
- `docs/questions/<name>.md` (from `docs/questions/template.md`), committed to `main`, **every** entry `ANSWERED` and incorporated.
- A change branch `<type>/<name>` and its worktree at `<repo-name>-worktrees/<type>/<name>`, created at **P.4** from `main` (so the branch carries the TODO file and the answered questions).
- A recorded change type in the TODO file and in `docs/verification/<name>.md`.
- FEATURE/CROSS-CUTTING: the draft specification at `docs/specs/<name>.md` (committed on the change branch), self-consistent per the checklist.
- ISSUE: a triage record in `docs/verification/<name>.md` (affected REQ/AC, defect confirmation, reproduction plan).
- REFACTOR: a GREEN baseline and refactor scope in `docs/verification/<name>.md`.
- DOCS/CHORE: a no-behavior scope in `docs/verification/<name>.md`.

**S1.4 (normal workflow, FEATURE/CROSS-CUTTING only):** the prepared specification is committed to `docs/specs/` and a PR is open for human review, with a clear statement that it is awaiting human approval.

## Definition of Done

**Phase P — the READY gate (all types):**

- The TODO file exists on `main` with `Status: READY`, and the question file exists with **every** question `ANSWERED` and incorporated.
- The change branch and its worktree exist (created at P.4).
- The change type is classified and recorded in the TODO file and in `docs/verification/<name>.md`.
- FEATURE/CROSS-CUTTING:
  - The feature brief captures goals, constraints, out-of-scope items, and edge cases (intermediate — folded into the spec, not a separate file).
  - At least 20 questions were asked during interrogation and **recorded in `docs/questions/<name>.md`** (one `BLOCKED-USER` batch; the orchestrator presents it in as few rounds as possible, ≤ 4 per round, and records the answers).
  - Existing specs in `docs/specs/` and every planned TODO in `docs/todo/` were checked for overlap; no work was double-specified.
  - The specification has stable IDs for every requirement, acceptance criterion, invariant, edge case, and non-functional requirement.
  - The specification passes the self-consistency checklist (no internal inconsistencies).
  - The specification is drafted and committed to `docs/specs/` on the change branch.
- ISSUE: the triage record is committed; affected REQ/AC are cited; the defect is confirmed (observed vs. required); the reproduction plan names the failing test(s).
- REFACTOR: the baseline is GREEN and recorded; the refactor scope is defined.
- DOCS/CHORE: the scope is recorded; no behavior delta is confirmed.
- No implementation code has been written.

**S1.4 only (FEATURE/CROSS-CUTTING, inside the normal workflow):**

- The specification is committed to `docs/specs/` and a PR is open for human review.
- The specification has NOT been approved yet (approval is a human action).
