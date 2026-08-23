# Skill: verify

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
- Run lint (`uv run ruff check src/ tests/`) and confirm it passes.
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
