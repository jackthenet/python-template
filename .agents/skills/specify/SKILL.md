---
name: specify
description: Turns a feature brief into an approved-quality specification with stable REQ, AC, INV, EDGE, and NFR IDs in Given/When/Then form. Commits the specification and opens a PR for human review. Use when a feature brief exists and a specification needs to be written before acceptance testing.
---

# Specify

Turn a feature brief into an approved-quality specification.

## Entry Conditions

- [ ] A feature branch exists (created by `feature` skill).
- [ ] A feature brief exists (produced by `grill` skill).
- [ ] No specification exists for this feature yet.

## Input

Feature brief: decisions, scope, actors, out-of-scope, open questions.

## Output

`docs/specs/<feature>.md`

## MUST

- Identify normative requirements and assign stable `REQ-XXX` IDs.
- Define acceptance criteria with stable `AC-XXX` IDs in Given/When/Then form.
- Every `REQ-XXX` MUST have one or more `AC-XXX`.
- Define invariants with stable `INV-XXX` IDs.
- Identify edge cases with `EDGE-XXX` IDs.
- Define non-functional requirements with `NFR-XXX` IDs where applicable.
- Define the test strategy: which test category proves which requirement.
- State scope and out-of-scope behavior explicitly.
- Incorporate all decisions from the feature brief.
- Commit the specification: `spec(<feature>): add specification`.
- Push the feature branch and open a PR for human review.

## MUST-NOT

- Implement code.
- Modify production code or tests.
- Invent requirements not grounded in the feature brief or user input.
- Describe tests — the specification generates the tests; it does not describe them.
- Treat a direct commit to `main` as approval.
- Merge the spec PR (human governance).

## Git Responsibilities

Before work:
- Verify the current branch is the feature branch.
- Verify the feature brief exists.
- Verify the working tree is clean.

After work:
- Commit the specification.
- Push the feature branch.
- Open a PR for human review.
- Do NOT merge the PR.

Commit:
    spec(<feature>): add specification

## Verification

- Spec file exists at `docs/specs/<feature>.md`.
- Every `REQ-XXX` maps to one or more `AC-XXX`.
- All feature brief decisions incorporated.
- Spec PR opened for human review.
