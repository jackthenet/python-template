---
name: verify
description: Produces evidence that the change satisfies its type-specific gates (Phase Matrix in AGENTS.md) by running acceptance tests, regression suites, lint, type checks, coverage, architecture rules, and spec validation. Use when implementation is complete and the type's GREEN gate has been achieved, to confirm the change is verified.
---

# Verify

Produce evidence that the change satisfies its type-specific gates (Phase Matrix in `AGENTS.md`).

## Entry Conditions

- [ ] Implementation is complete (FEATURE/CROSS-CUTTING/ISSUE: GREEN achieved; REFACTOR: steps done, suite GREEN; DOCS/CHORE: change made).
- [ ] FEATURE/CROSS-CUTTING: acceptance tests exist; RED was previously confirmed; GREEN evidence is recorded in `docs/verification/<name>.md`.
- [ ] ISSUE: reproduction tests exist; RED was previously confirmed; GREEN evidence is recorded in `docs/verification/<name>.md`.
- [ ] REFACTOR: GREEN baseline is recorded in `docs/verification/<name>.md`.
- [ ] Working tree is clean.

## Input

Spec + tests + implementation (FEATURE/CROSS-CUTTING); triage record + reproduction tests (ISSUE); baseline + scope (REFACTOR); scope (DOCS/CHORE).

## Output

Verification report at `docs/verification/<name>.md`.

## MUST

### FEATURE / CROSS-CUTTING

- Verify every `REQ-XXX` has one or more `AC-XXX`.
- Verify every `AC-XXX` has one or more executable tests.
- Verify no orphaned tests (tests without spec reference).
- Verify every `INV-XXX` has a property test where appropriate.
- Run all acceptance tests and confirm they pass.
- Run the full regression suite and confirm it passes.
- When the full regression suite has a failure, classify it before proceeding: run the failing test against the change's base commit (without the change's changes, e.g. `git stash` the change's `src/` changes or `git checkout <base> -- <failing-test-file>`). If it fails on the base too, it is a **pre-existing failure** (out of scope — record it in the verification report and do NOT fix it as part of this change). If it passes on the base, it is a **regression** introduced by this change (fix it before marking the change verified). Never spend time debugging a pre-existing failure as if it were a regression.
- Run lint (`uv run ruff check .`) and confirm it passes. This must match CI exactly (`.github/workflows/lint.yml` runs `uv run ruff check .` on the whole repo). Pre-existing lint errors anywhere in the repo are in scope: fix them before marking the change verified, never as out of scope.
- Run type checks (`uv run mypy src/`) and confirm they pass.
- Run coverage (`uv run pytest tests/ --cov`) and confirm threshold passes.
- Run architecture rules (`uv run pytest tests/architecture/ -v`) and confirm they pass.
- Run `uv run python scripts/verify_spec.py docs/specs/<name>.md` and confirm it passes.
- CROSS-CUTTING: update the traceability matrix rows of every affected feature.

### ISSUE

- Run the reproduction tests and confirm they pass (GREEN).
- Run the full regression suite and confirm no new failures (classify failures as in the FEATURE path).
- Run lint (`uv run ruff check .`) and type checks (`uv run mypy src/`) and confirm they pass.
- Update the traceability matrix with the issue's evidence rows.

### REFACTOR

- Run the full regression suite and confirm it is GREEN with zero test changes.
- Run architecture rules (`uv run pytest tests/architecture/ -v`) and confirm they pass.
- Run lint (`uv run ruff check .`) and type checks (`uv run mypy src/`) and confirm they pass.
- Confirm no observable behavior changed (suite result identical to baseline).

### DOCS/CHORE

- Run lint (`uv run ruff check .`) and type checks (`uv run mypy src/`) where applicable and confirm they pass.
- Confirm no test files or behavior were touched.

### All types

- Produce a verification report with pass/fail status per check.
- Commit verification artifacts: `docs(<name>): add verification report`.

## MUST-NOT

- Mark the change verified without evidence.
- Skip any verification check.
- Weaken verification criteria to make them pass.
- Treat "I think this is implemented" as evidence.

## Git Responsibilities

Before work:
- Verify implementation is complete.
- Verify the type's GREEN gate has been achieved (FEATURE/CROSS-CUTTING/ISSUE: GREEN; REFACTOR: suite GREEN, zero test changes; DOCS/CHORE: change made).
- Verify the working tree is clean.

After work:
- Commit verification artifacts.

Commit:
    docs(<name>): add verification report

## Verification

- All checks pass.
- Verification report produced and committed.
- `verify_spec.py` exits 0 (FEATURE/CROSS-CUTTING).
- Task status is `VERIFIED` (FEATURE/CROSS-CUTTING).
