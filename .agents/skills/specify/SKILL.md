---
name: specify
description: Orchestrates discovery and specification of a new feature: creates a feature branch, adversarially interrogates the feature idea into a feature brief, and turns the brief into an approved-quality specification with stable REQ, AC, INV, EDGE, and NFR IDs in Given/When/Then form. Commits the specification and opens a PR for human review. Use when starting a new feature from a user request, GitHub issue, or problem description.
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

### 2. Interrogate the feature idea (discover)

2. Restate the feature idea in one sentence.
3. Ask: what is the goal? Who is the user? What problem does it solve?
4. Ask: what are the constraints? What must NOT change? What is out of scope?
5. Ask: what are the edge cases? What could go wrong? What are the failure modes?
6. Ask: what are the hidden requirements? What assumptions are being made?
7. Ask: what are the scope boundaries? Where does this feature end?
8. Capture the answers into a feature brief (goals, constraints, out-of-scope items, edge cases).

### 3. Write the specification

9. Read the feature brief and the specification template.
10. Identify every normative requirement. Assign each a stable `REQ-XXX` ID.
11. For each requirement, write one or more acceptance criteria in Given/When/Then form. Assign each an `AC-XXX` ID.
12. Identify invariants the system must always maintain. Assign each an `INV-XXX` ID.
13. Identify edge cases and error conditions. Assign each an `EDGE-XXX` ID.
14. Identify non-functional requirements (performance, security, usability, compliance). Assign each an `NFR-XXX` ID.
15. Define the test strategy: map each AC/INV/EDGE to a test category (acceptance, integration, contract, property, unit) and a test function name.
16. Write the complete specification to `docs/specs/[feature-name].md`.

### 4. Present for approval

17. Commit the specification file.
18. Open a PR for human review.
19. STOP and present the specification for human approval.

## Rules

- A feature branch MUST be created before any brief or specification work.
- Ask MORE questions than feels necessary during interrogation.
- The feature brief MUST capture goals, constraints, out-of-scope items, and edge cases.
- Every normative requirement MUST have a stable `REQ-XXX` ID.
- Every acceptance criterion MUST be in Given/When/Then form with an `AC-XXX` ID.
- Every invariant MUST have an `INV-XXX` ID.
- Every edge case MUST have an `EDGE-XXX` ID.
- Every non-functional requirement MUST have an `NFR-XXX` ID.
- The specification MUST be committed to `docs/specs/`.
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
- The specification has stable IDs for every requirement, acceptance criterion, invariant, edge case, and non-functional requirement.
- The specification is committed to `docs/specs/`.
- A PR is open for human review.
- The specification has NOT been approved yet (approval is a human action).
- No implementation code has been written.
