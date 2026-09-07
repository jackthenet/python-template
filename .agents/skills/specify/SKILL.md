---
name: specify
description: "Orchestrates discovery and specification of a new feature: creates a feature branch, adversarially interrogates the feature idea into a feature brief, and turns the brief into an approved-quality specification with stable REQ, AC, INV, EDGE, and NFR IDs in Given/When/Then form. Commits the specification and opens a PR for human review. Use when starting a new feature from a user request, GitHub issue, or problem description."
---

# Specify

## Purpose

Discover and specify a new feature end to end: create a feature branch, adversarially interrogate the feature idea to surface ambiguity and hidden requirements, capture a feature brief, and turn the brief into an approved-quality specification with stable IDs and Given/When/Then acceptance criteria. The specification is committed to `docs/specs/` and presented to a human for approval before any implementation begins.

## When to Use

- A new feature is requested from a user, GitHub issue, or problem description.
- The feature idea is not yet concrete enough to write acceptance tests.
- You need to set up the branch, brief, and specification before any implementation.

## Inputs

- A feature request (user message, GitHub issue, or problem description).
- The specification template at `docs/specs/template.md`.
- Any existing codebase context relevant to the feature.
- The current state of the repository (to pick a clean base branch).

## Process

### 1. Create the feature branch

1. Create a feature branch `feature/[feature-name]` from `main` (or the configured base branch).
2. Other features are being implemented in parallel. Stay strictly on this branch/worktree: do not modify unrelated features, branches, or worktrees, and keep all changes isolated to this feature.

### 2. Check existing features and specs (no double work)

3. Read the specs in `docs/specs/` (all features, including any spec already on the current branch) and the existing feature directories under `src/`.
4. Determine what has already been built and what is planned elsewhere. If any part of this feature overlaps an existing or planned feature, reuse or extend that work instead of re-specifying it, and record the overlap in the feature brief.

### 3. Interrogate the feature idea (discover)

5. Restate the feature idea in one sentence.
6. Ask: what is the goal? Who is the user? What problem does it solve?
7. Ask: what are the constraints? What must NOT change? What is out of scope?
8. Ask: what are the edge cases? What could go wrong? What are the failure modes?
9. Ask: what are the hidden requirements? What assumptions are being made?
10. Ask: what are the scope boundaries? Where does this feature end?
11. Ask at least 20 questions in total. A single `ask_user_question` call accepts at most 4 questions — call it multiple times (batches of up to 4) until at least 20 questions have been asked, covering goals, users, constraints, out-of-scope, edge cases, failure modes, hidden requirements, assumptions, scope boundaries, and non-functional concerns.
12. Capture the answers into a feature brief (goals, constraints, out-of-scope items, edge cases).

### 4. Write the specification

13. Read the feature brief and the specification template.
14. Identify every normative requirement. Assign each a stable `REQ-XXX` ID.
15. For each requirement, write one or more acceptance criteria in Given/When/Then form. Assign each an `AC-XXX` ID.
16. Identify invariants the system must always maintain. Assign each an `INV-XXX` ID.
17. Identify edge cases and error conditions. Assign each an `EDGE-XXX` ID.
18. Identify non-functional requirements (performance, security, usability, compliance). Assign each an `NFR-XXX` ID.
19. Define the test strategy: map each AC/INV/EDGE to a test category (acceptance, integration, contract, property, unit) and a test function name.
20. Build `docs/specs/[feature-name].md` incrementally with several small `write`/`edit` tool calls: write the first chunk (header + first sections) with `write`, then append subsequent sections with `edit` calls. Do NOT do one giant `write` call and do NOT rewrite the whole file multiple times.

### 5. Verify self-consistency

21. Run the self-consistency checklist (below) against the written specification. Fix every inconsistency in the spec itself — do NOT defer to implementation or review.

### 6. Present for approval

22. Commit the specification file.
23. Open a PR for human review.
24. STOP and present the specification for human approval.

## Self-Consistency Checklist

Run this against the written specification before presenting it for approval. Fix every failure in the spec itself (never defer to implementation or review).

- **Configurability**: every "configurable X" / "X can be set" claim names a real parameter in the API/signature, and that parameter has a stated default or a matching AC. No aspirational parameters that don't exist.
- **Parameter coverage**: every parameter in the API/signature is either configurable-by-spec or has a stated default. No orphan parameters.
- **REQ↔AC wording**: every AC's Given/When/Then is consistent with the REQ it satisfies — same terms, no contradictory or stricter/looser wording.
- **Terminology drift**: every defined term (e.g., "private method", "public method") is used consistently in every definition, example, and AC. The definition and every example must agree (if "private" means "underscore-prefixed", no example uses a non-underscore name).
- **Test strategy coverage**: every normative ID (REQ/AC/INV/EDGE/NFR) appears in the test strategy with a test category and test function.
- **ID references**: every cross-reference (e.g., "see REQ-005", "per AC-011") points to an ID that exists.
- **Scope consistency**: every in-scope item has at least one REQ; every out-of-scope item is not accidentally covered by a REQ/AC.
- **Performance budget vs. observability**: every performance budget that covers an operation which the observability table requires to log must (a) be achievable *including* that per-call logging overhead, and (b) state the logging context (e.g., synchronous console sink) under which the budget is measured. A budget that only holds with logging disabled (or that is unachievable with the mandated logging) is inconsistent.

## Rules

- A feature branch MUST be created before any brief or specification work.
- Stay strictly on the feature's branch/worktree. Do not modify unrelated features, branches, or worktrees. Keep all changes isolated to this feature.
- Ask MORE questions than feels necessary during interrogation.
- Ask at least 20 questions during interrogation. Since one `ask_user_question` call accepts at most 4 questions, call it multiple times until the total reaches at least 20.
- Check other features' specs and the current branch's specs before specifying. Reuse or extend existing/planned work — do not do double work.
- The feature brief MUST capture goals, constraints, out-of-scope items, and edge cases.
- Every normative requirement MUST have a stable `REQ-XXX` ID.
- Every acceptance criterion MUST be in Given/When/Then form with an `AC-XXX` ID.
- Every invariant MUST have an `INV-XXX` ID.
- Every edge case MUST have an `EDGE-XXX` ID.
- Every non-functional requirement MUST have an `NFR-XXX` ID.
- The specification MUST be committed to `docs/specs/`.
- Build the specification file incrementally with several small `write`/`edit` calls — not one giant `write` call and not multiple full rewrites.
- The specification MUST pass the self-consistency checklist before it is presented for approval.
- The specification MUST be presented to a human for approval before implementation.
- Do NOT write implementation code in this phase.
- Do NOT derive acceptance tests in this phase.

## Outputs

- A feature branch `feature/[feature-name]`.
- A feature brief (goals, constraints, out-of-scope items, edge cases).
- A committed specification file at `docs/specs/[feature-name].md`.
- A PR open for human review.
- A clear statement that the specification is awaiting human approval.

## Definition of Done

- The feature branch exists.
- The feature brief captures goals, constraints, out-of-scope items, and edge cases.
- At least 20 questions were asked during interrogation (multiple `ask_user_question` calls of up to 4 each).
- Existing features' specs and the current branch's specs were checked for overlap; no work was double-specified.
- The specification has stable IDs for every requirement, acceptance criterion, invariant, edge case, and non-functional requirement.
- The specification passes the self-consistency checklist (no internal inconsistencies).
- The specification is committed to `docs/specs/`.
- A PR is open for human review.
- The specification has NOT been approved yet (approval is a human action).
- No implementation code has been written.
