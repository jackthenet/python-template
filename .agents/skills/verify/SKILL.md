---
name: verify
description: Produces evidence that the implementation satisfies the specification by running acceptance tests, regression suites, lint, type checks, coverage, architecture rules, and spec validation. Use when implementation is complete and GREEN has been achieved, to confirm the feature is verified.
---

# Verify

Produce evidence that the implementation satisfies the specification.

## Entry Conditions

- [ ] Implementation is complete.
- [ ] Acceptance tests exist.
- [ ] RED was previously confirmed.
- [ ] GREEN has been achieved.
- [ ] GREEN evidence is recorded in `docs/verification/<feature>.md`.
- [ ] Working tree is clean.

## Input

Spec + tests + implementation.

## Output

Verification report at `docs/verification/<feature>.md`.

## MUST

- Verify every `REQ-XXX` has one or more `AC-XXX`.
- Verify every `AC-XXX` has one or more executable tests.
- Verify no orphaned tests (tests without spec reference).
- Verify every `INV-XXX` has a property test where appropriate.
- Run all acceptance tests and confirm they pass.
- Run the full regression suite and confirm it passes.
- When the full regression suite has a failure, classify it before proceeding: run the failing test against the feature's base commit (without the feature's changes, e.g. `git stash` the feature's `src/` changes or `git checkout <base> -- <failing-test-file>`). If it fails on the base too, it is a **pre-existing failure** (out of scope — record it in the verification report and do NOT fix it as part of this feature). If it passes on the base, it is a **regression** introduced by this feature (fix it before marking the feature verified). Never spend time debugging a pre-existing failure as if it were a regression.
- Run lint (`uv run ruff check .`) and confirm it passes. This must match CI exactly (`.github/workflows/lint.yml` runs `uv run ruff check .` on the whole repo). Pre-existing lint errors anywhere in the repo are in scope: fix them before marking the feature verified, never as out of scope.
- Run type checks (`uv run mypy src/`) and confirm they pass.
- Run coverage (`uv run pytest tests/ --cov`) and confirm threshold passes.
- Run architecture rules (`uv run pytest tests/architecture/ -v`) and confirm they pass.
- Run `uv run python scripts/verify_spec.py docs/specs/<feature>.md` and confirm it passes.
- Produce a verification report with pass/fail status per check.
- Commit verification artifacts: `docs(<feature>): add verification report`.

## MUST-NOT

- Mark the feature verified without evidence.
- Skip any verification check.
- Weaken verification criteria to make them pass.
- Treat "I think this is implemented" as evidence.

## Git Responsibilities

Before work:
- Verify implementation is complete.
- Verify GREEN has been achieved.
- Verify the working tree is clean.

After work:
- Commit verification artifacts.

Commit:
    docs(<feature>): add verification report

## Verification

- All checks pass.
- Verification report produced and committed.
- `verify_spec.py` exits 0.
- Task status is `VERIFIED`.
