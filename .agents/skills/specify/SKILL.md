# Skill: specify

Turn an issue or problem description into an approved-quality specification.

## Entry Conditions

- [ ] A GitHub issue or user requirement exists.
- [ ] No approved specification exists for this feature.

## Input

GitHub issue / user requirement.

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
- Submit the spec via a GitHub PR for human review.

## MUST-NOT

- Implement code.
- Modify production code or tests.
- Invent requirements not grounded in the issue or user input.
- Describe tests — the specification generates the tests; it does not describe them.
- Treat a direct commit to `main` as approval.

## Verification

- Spec file exists at `docs/specs/<feature>.md`.
- Every `REQ-XXX` maps to one or more `AC-XXX`.
- Spec PR is merged (human approval).
