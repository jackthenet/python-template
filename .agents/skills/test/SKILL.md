---
name: test
description: Converts an approved specification into executable acceptance tests, property tests, unit tests, and contract tests. Derives tests from acceptance criteria, confirms RED state, and records evidence. Use when an approved specification exists and acceptance tests need to be created before implementation.
---

# Test

Convert an approved specification into executable acceptance tests.

## Entry Conditions

- [ ] An approved specification exists at `docs/specs/<feature>.md` (merged PR).
- [ ] Acceptance criteria are identified in the spec.
- [ ] No acceptance tests exist for this feature yet.
- [ ] Working tree is clean.

## Input

`docs/specs/<feature>.md`

## Output

`tests/acceptance/<feature>/test_<feature>.py`

## MUST

- Derive one or more test functions per `AC-XXX`.
- Test names MUST reference the `AC-XXX` ID (e.g., `test_ac_001_valid_request`).
- Test externally observable behavior only — not implementation details.
- Run the test suite and confirm RED state (tests fail before implementation).
- Record RED evidence in `docs/verification/<feature>.md` using `TDD-evidence-template.md`.
- Update the traceability matrix in `docs/verification/traceability.md`.
- Write property tests for every `INV-XXX` using Hypothesis in `tests/property/<feature>/`.
- Write unit tests for `EDGE-XXX` cases in `tests/unit/<feature>/`.
- Write contract tests for `NFR-XXX` requirements in `tests/contract/<feature>/`.
- **Async event-bus tests:** the bus dispatches queued events to handlers registered *at dispatch time*. So subscribe BEFORE any setup writes, wait for the setup events to be delivered, then clear the collector — so no setup event is in flight when asserting on the operation under test. Never publish setup events and then subscribe (racy).
- Commit the tests: `test(<feature>): add acceptance tests`.

## MUST-NOT

- Implement missing behavior.
- Weaken the specification.
- Make tests pass by changing expected behavior.
- Test implementation details at the acceptance layer.
- Modify the spec to fit the tests.
- Skip RED confirmation.
- Commit implementation code.

## Git Responsibilities

Before work:
- Verify the current branch is the feature branch.
- Verify the specification is approved (merged PR).
- Verify the working tree is clean.

After work:
- Run the RED command.
- Commit the acceptance tests.
- Do not commit implementation code.

Commit:
    test(<feature>): add acceptance tests

## Verification

- Tests exist and reference `AC-XXX` IDs.
- Tests fail (RED confirmed) before implementation.
- RED evidence recorded.
- Traceability matrix updated.
- Tests committed.
