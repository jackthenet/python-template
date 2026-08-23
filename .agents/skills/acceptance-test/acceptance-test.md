# Skill: acceptance-test

Convert an approved specification into executable acceptance tests.

## Entry Conditions

- [ ] An approved specification exists at `docs/specs/<feature>.md` (merged PR).
- [ ] Acceptance criteria are identified in the spec.
- [ ] No acceptance tests exist for this feature yet.

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

## MUST-NOT

- Implement missing behavior.
- Weaken the specification.
- Make tests pass by changing expected behavior.
- Test implementation details at the acceptance layer.
- Modify the spec to fit the tests.
- Skip RED confirmation.

## Verification

- Tests exist and reference `AC-XXX` IDs.
- Tests fail (RED confirmed) before implementation.
- RED evidence recorded.
- Traceability matrix updated.
