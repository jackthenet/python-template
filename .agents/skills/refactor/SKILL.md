---
name: refactor
description: Improves code structure without changing specified behavior. Re-runs tests after every meaningful refactoring step to confirm GREEN is maintained. Use when implementation is GREEN and code structure needs improvement (duplication, complexity, naming, boundaries).
---

# Refactor

Improve code structure without changing specified behavior.

## Entry Conditions

- [ ] GREEN has been achieved.
- [ ] GREEN evidence is recorded in `docs/verification/<feature>.md`.
- [ ] All acceptance tests pass.

## Input

Implementation code that is GREEN.

## Output

Refactored code that is still GREEN.

## Fundamental Rule

Refactoring may change structure but must not change specified behavior.

## MUST

- Start from GREEN.
- After every meaningful refactoring step, re-run the test suite and confirm GREEN.
- Look for: duplication, unnecessary abstractions, excessive complexity, poor naming, feature-boundary violations, inappropriate dependencies.
- Do not add functionality.
- Commit after refactoring: `refactor(<feature>): <description>`.

## MUST-NOT

- Change specified behavior.
- Add functionality.
- Modify acceptance tests.
- Skip GREEN re-verification after refactoring steps.
- Refactor while tests are failing.

## Git Responsibilities

Before work:
- Verify GREEN is confirmed.
- Verify working tree is clean.

After work:
- Commit refactored code.

Commit:
    refactor(<feature>): <description>

## Verification

- All acceptance tests still pass.
- Full regression suite passes.
- Lint and type checks pass.
- No behavior change (tests prove this).
