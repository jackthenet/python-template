# Skill: implement

Implement the minimum behavior required to turn RED into GREEN.

## Entry Conditions

- [ ] An approved specification exists at `docs/specs/<feature>.md` (merged PR).
- [ ] The task references the specification.
- [ ] Acceptance criteria are identified in the spec.
- [ ] Acceptance tests exist.
- [ ] Acceptance tests have been executed.
- [ ] RED has been confirmed.
- [ ] RED evidence is recorded in `docs/verification/<feature>.md`.
- [ ] Working tree is clean.

## Input

Approved spec + approved task + failing acceptance tests.

## Output

Implementation code in `src/` that makes the failing tests pass.

## MUST

- Implement the minimum behavior required by the acceptance criteria.
- Follow feature boundaries: code lives in `frontend/features/<feature>/` or `backend/features/<feature>/`.
- Do not modify acceptance criteria or tests.
- Do not weaken tests.
- Do not introduce unspecified behavior.
- Run `green_command` and confirm tests PASS 100%.
- Run regression tests to confirm no other behavior broke.
- Record GREEN evidence in `docs/verification/<feature>.md`.
- Pass quality gates: lint, type checks, coverage threshold.
- Commit the implementation: `feat(<feature>): implement <behavior>`.

## MUST-NOT

- Modify acceptance tests to make them pass.
- Delete or weaken tests.
- Convert a failing test into a weaker passing test.
- Introduce behavior not in the spec.
- Add functionality beyond what the acceptance criteria require.
- Skip GREEN confirmation.
- Mark the task complete without evidence.

## Git Responsibilities

Before work:
- Verify acceptance tests exist.
- Verify RED has been demonstrated.
- Verify the working tree is clean.

After work:
- Run GREEN verification.
- Commit implementation.

Commit:
    feat(<feature>): implement <behavior>

## Verification

- `green_command` passes 100%.
- Regression suite passes.
- Lint and type checks pass.
- GREEN evidence recorded.
- Implementation committed.
- Task status updated to `VERIFIED`.
