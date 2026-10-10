# TODO: complexipy-scripts

Backlog item for one planned change, created at **P.1 Frame** from this template and named `complexipy-scripts.md`. One file per change.

This is a **planning record, not normative**: like `docs/questions/`, it is committed directly to `main` (see "Phase P: PREPARE" in `AGENTS.md`). It carries no approval gate — the spec does.

- **Status:** WAITING  <!-- PREPARING | QUESTIONS-ANSWERED | READY | IN-WORKFLOW | WAITING | MERGED | DROPPED -->
- **Change type:** REFACTOR  <!-- first-match #4: restructures existing code without altering externally observable behavior; the CI-invocation line is chore-like and rides along — P.2 may re-examine, Escalation Rules apply -->
- **Created:** 2026-10-09
- **Question file:** `docs/questions/complexipy-scripts.md`
- **Spec:** n/a  <!-- no spec is authored; the gate is CI config + complexity evidence -->
- **Worktree:** <created at P.4> `../python-template_kopie-worktrees/refactor/complexipy-scripts`
- **Depends on:** none hard; **sequenced after `map-default-drop-shift`** (that change edits `scripts/make_map.py`; refactoring the same tree in parallel would collide)
- **Related specs:** none (no `docs/specs/` file is touched)

## Goal (one line)
Bring `scripts/` under the cognitive-complexity gate (`uv run complexipy src tests scripts --max-complexity-allowed 15`) by refactoring the four functions that exceed the ceiling today.

## Why
Raised as **Q-15 / Q-19** while preparing `map-default-drop-shift`. The complexity gate covers `src` and `tests` only (`.github/workflows/quality.yml:146`), so the repository's own tooling — the spec checker, the task-DAG validator, the map generator — is unbounded. Measured at `7dfaa23` with `uv run complexipy scripts --max-complexity-allowed 15`, four functions fail:

| File | Function | Complexity |
|---|---|---|
| `scripts/check_traceability.py` | `check` | 17 |
| `scripts/check_traceability.py` | `matrix_rows` | 19 |
| `scripts/validate_task_dag.py` | `check_acyclic` | 22 |
| `scripts/verify_spec.py` | `main` | 22 |

`scripts/make_map.py` is already clean (max 12; `_drop_long_defaults` = 6). The user decided (2026-10-09) to close the gap as its **own** change rather than inside `map-default-drop-shift`, so that change stays a light-tier ISSUE with a two-file diff.

## In scope
- Extending the CI invocation in `.github/workflows/quality.yml` to `src tests scripts`.
- Behavior-preserving refactors of the four functions above until the gate passes.
- Keeping every existing test green with **zero test changes** (the REFACTOR contract).

## Out of scope
- Raising or parameterising the `15` ceiling, and any per-file carve-out/baseline — the point is to meet the existing ceiling, not to encode debt.
- Any behavior change to the CI checks themselves (what `check_traceability.py`, `validate_task_dag.py` and `verify_spec.py` detect stays exactly as it is).
- `scripts/make_map.py` (already under the ceiling; it is edited by `map-default-drop-shift`).

## Affected features
No `src/` code. `scripts/check_traceability.py`, `scripts/validate_task_dag.py`, `scripts/verify_spec.py`, `.github/workflows/quality.yml`.

## Constraints and risks
- REFACTOR requires a **GREEN baseline of the full suite** before any restructuring, and the suite must stay GREEN after every step, with no test modified, weakened or deleted.
- These three scripts are what CI uses to enforce spec traceability and DAG well-formedness — a silent behavior change here weakens the workflow's own gates. The existing tests for them are the contract.
- `check_acyclic` (22) and `verify_spec.py::main` (22) are far above 15; the refactor may need to introduce helper functions, which changes their signatures — acceptable only because nothing imports them across module boundaries (verify at P.2).
- Ruff covers `scripts/` (`lint.yml`); ruff rule `D` is per-file-ignored for `scripts/*` (PR #76), so new helpers need no docstrings, though a *why* docstring is still expected in review.
- No version bump (REFACTOR).

## Value triage (2026-10-09, pre-workflow)
- **Overlap:** none — the only complexity gate is the `complexipy` job in `.github/workflows/quality.yml:146`, and it analyzes `src tests` only; no other lint/config enforces complexity on `scripts/`.
- **Beneficiary:** the repo's own guardrails and the next change that touches `scripts/` — today an agent can push a 22-complexity function into the tooling and CI stays silent. No end-user-visible value.
- **Score: 3/5** — real, cheap-to-prevent rot in the code that enforces the workflow, but partly mechanical (four refactors) and benefits the maintainers/agent rather than the end user.
- **Recommendation:** implement — as a REFACTOR change, after `map-default-drop-shift` lands.
- **Decision:** **IMPLEMENT** (user, 2026-10-09, recorded via `map-default-drop-shift` Q-19: "separate chore change"). Not merged into another change, not dropped.

## Acceptance signal (plain language)
`uv run complexipy src tests scripts --max-complexity-allowed 15` exits 0 in CI and locally, the full test suite is GREEN with no test file touched, and the three CI scripts detect exactly what they detected before.

## Prep log
| Step | Date | Result |
|---|---|---|
| P.1 Frame | 2026-10-09 | classified REFACTOR (first-match #4); TODO + question file created on `main`; value triage recorded, decision IMPLEMENT (carried from `map-default-drop-shift` Q-19) |
| P.2 Interrogate (<n> questions) | | |
| P.3 Answer (<n> answered) | | |
| P.4 Draft spec / triage / baseline / scope | | |
| P.5 Self-consistency (FEATURE/CROSS-CUTTING) | | n/a — REFACTOR |
