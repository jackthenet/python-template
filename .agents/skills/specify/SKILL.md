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

#### 1. Check existing features and specs (no double work)

5. Read the specs in `docs/specs/` (all features, including any spec already on the current branch) and the existing feature directories under `src/`.
6. Determine what has already been built and what is planned elsewhere. If any part of this feature overlaps an existing or planned feature, reuse or extend that work instead of re-specifying it, and record the overlap in the feature brief.

#### 2. Interrogate the feature idea (discover)

7. Restate the feature idea in one sentence.
8. Ask: what is the goal? Who is the user? What problem does it solve?
9. Ask: what are the constraints? What must NOT change? What is out of scope?
10. Ask: what are the edge cases? What could go wrong? What are the failure modes?
11. Ask: what are the hidden requirements? What assumptions are being made?
12. Ask: what are the scope boundaries? Where does this feature end?
13. Ask at least 20 questions in total. A single `ask_user_question` call accepts at most 4 questions — call it multiple times (batches of up to 4) until at least 20 questions have been asked, covering goals, users, constraints, out-of-scope, edge cases, failure modes, hidden requirements, assumptions, scope boundaries, and non-functional concerns.
14. Capture the answers into a feature brief (goals, constraints, out-of-scope items, edge cases). The brief is an **intermediate artifact** — do **not** save it as a separate `.brief.md` file; it feeds the spec, which is the single kept artifact.

#### 3. Write the specification

15. Read the feature brief and the specification template.
16. Identify every normative requirement. Assign each a stable `REQ-XXX` ID.
17. For each requirement, write one or more acceptance criteria in Given/When/Then form. Assign each an `AC-XXX` ID.
18. Identify invariants the system must always maintain. Assign each an `INV-XXX` ID.
19. Identify edge cases and error conditions. Assign each an `EDGE-XXX` ID.
20. Identify non-functional requirements (performance, security, usability, compliance). Assign each an `NFR-XXX` ID.
21. Define the test strategy: map each AC/INV/EDGE to a test category (acceptance, integration, contract, property, unit) and a test function name.
22. Build `docs/specs/<name>.md` incrementally with several small `write`/`edit` tool calls: write the first chunk (header + first sections) with `write`, then append subsequent sections with `edit` calls. Do NOT do one giant `write` call and do NOT rewrite the whole file multiple times.

#### 4. Verify self-consistency

23. Run the self-consistency checklist (below) against the written specification. Fix every inconsistency in the spec itself — do NOT defer to implementation or review.

#### 5. Present for approval

24. Commit the specification file.
25. Open a PR for human review.
26. STOP and present the specification for human approval.

### B. ISSUE path (triage — no spec, no PR)

27. Identify the affected requirements (`REQ-XXX`) and acceptance criteria (`AC-XXX`) from the **existing approved specs** in `docs/specs/`. Cite the spec files and IDs.
28. Confirm the defect: state the observed behavior and the required behavior (per the cited spec IDs). The observed behavior MUST deviate from what the spec requires.
29. If the fix requires behavior the spec does not state, STOP: open a Spec Amendment PR (Spec Amendment Workflow) or reclassify as FEATURE per the Escalation Rules.
30. Write the reproduction plan: the failing test(s) that reproduce the defect (test names, files), the fix scope, and the files expected to change.
31. Record the triage in `docs/verification/<name>.md` (type: ISSUE, affected REQ/AC, defect confirmation, reproduction plan). Commit: `issue(<name>): triage`.

### C. CROSS-CUTTING path

32. Interrogate the change adversarially (same depth as the FEATURE path; at least 20 questions): goals, affected features, constraints, out-of-scope, edge cases, failure modes.
33. Draft the spec at `docs/specs/<name>.md` with an **Impact Analysis** section: every affected feature, what changes in each, and which of their REQ/AC IDs are touched.
34. Assign stable IDs (`REQ-XXX`, `AC-XXX`, `INV-XXX`, `EDGE-XXX`, `NFR-XXX`) and define the test strategy (map each AC/INV/EDGE to a test category and test function), as for FEATURE.
35. Run the self-consistency checklist (below) against the written specification. Fix every inconsistency.
36. Commit the specification file. Open a PR for human review. STOP and present the specification for human approval.

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

## Rules

- A change branch **and its worktree** MUST be created before any Phase 1 work (all types).
- The change type MUST be classified (Phase 0) before any other work, and recorded in `docs/verification/<name>.md`.
- Stay strictly on the change's branch/worktree. Do not modify unrelated changes, branches, or worktrees. Keep all changes isolated to this change.
- Ask MORE questions than feels necessary during interrogation (FEATURE/CROSS-CUTTING).
- Ask at least 20 questions during interrogation (FEATURE/CROSS-CUTTING). Since one `ask_user_question` call accepts at most 4 questions, call it multiple times until the total reaches at least 20.
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
  - At least 20 questions were asked during interrogation (multiple `ask_user_question` calls of up to 4 each).
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
