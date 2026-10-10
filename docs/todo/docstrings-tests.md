# TODO: docstrings-tests

Backlog item for one planned change, created at **P.1 Frame** from this template and named `docstrings-tests.md`. One file per change.

This is a **planning record, not normative**: like `docs/questions/`, it is committed directly to `main` (see "Phase P: PREPARE" in `AGENTS.md`). It carries no approval gate — the spec does.

- **Status:** WAITING  <!-- PREPARING | QUESTIONS-ANSWERED | READY | IN-WORKFLOW | WAITING | MERGED | DROPPED -->
- **Change type:** DOCS/CHORE  <!-- test docstrings + removing one per-file-ignores entry; no externally observable behavior delta -->
- **Created:** 2026-10-07
- **Question file:** `docs/questions/docstrings-tests.md`
- **Spec:** n/a  <!-- DOCS/CHORE: no spec -->
- **Worktree:** <created at P.4> `../python-template_kopie-worktrees/chore/docstrings-tests`
- **Depends on:** `ruff-d-docstrings` — it owns `[tool.ruff.lint] select`, the `pydocstyle` convention and the `per-file-ignores` entry for `tests/*` that this change removes
- **Related specs:** none directly; the traceability convention it makes enforceable is defined in `AGENTS.md` ("Traceability & Spec Drift") and exercised by `scripts/check_traceability.py`

## Goal (one line)
Give every test function a docstring that names the requirement or acceptance criterion it proves, and make `ruff` enforce that over `tests/` as it now does over `src/`.

## Why
`ruff-d-docstrings` (framed 2026-10-04, scoped 2026-10-07) gates `src/` only and explicitly defers `tests/` (its Q-4 + Q-29). The deferral is a real gap: `tests/` holds **762** `D` sites — 468 missing-docstring (`D103` 358, `D102` 49, `D104` 42, `D107` 19) plus 294 format/phrasing — and 313 of the 727 `test_*` functions carry no docstring at all (measured 2026-10-07, AST count of undocumented `test_*` functions; ruff counts 358 `D103` because helpers count too).

The repo's traceability model already leans on test docstrings as the human-readable link from a test to a `REQ-XXX`/`AC-XXX` — 414 test functions have one, and the house style writes `AC-009: …` at the start of the docstring. But nothing enforces it: `scripts/verify_spec.py:63` (the "No orphaned acceptance tests" check that would read them) is **skipped**, and `scripts/check_traceability.py` does not parse docstrings. So the convention holds only where a human remembered it.

## In scope
To be fixed at this item's P.2/P.3. Candidate scope (inherited from `ruff-d-docstrings` Q-29):
- Remove `tests/*` from `[tool.ruff.lint.per-file-ignores]` — either fully, or keeping only the format/phrasing families ignored (`"tests/*" = ["D2", "D3", "D4"]`) so a missing docstring is an error but test formatting stays free.
- Backfill the missing test docstrings, in the existing `AC-XXX: <what this proves>` house style, feature by feature.
- Decide whether the `D401`-free google convention chosen for `src/` also governs `tests/` (it applies automatically once `tests/*` leaves the exemption).
- Keep the `ruff-d-docstrings` no-filler rule (its Q-15) as the review check.

## Out of scope
- Any change to what the tests **assert** — docstrings and ruff config only. A docstring that reveals a test does not prove what it claims is a finding for a separate ISSUE TODO (the `ruff-d-docstrings` Q-26 procedure).
- `scripts/`, `migrations/`, `.github/` — permanently exempt per `ruff-d-docstrings` Q-3/Q-23.
- Making `scripts/verify_spec.py:63` parse test docstrings, or adding a docstring↔traceability checker — that is separate tooling work, not a docstring backfill.
- Splitting the 727 test functions into a different test layout.

## Affected features
All test trees: `tests/{acceptance,integration,contract,property,unit,architecture}`. Config: `pyproject.toml` `[tool.ruff.lint.per-file-ignores]`.

## Constraints and risks
- **762 sites is the largest backfill in the repository** — bigger than the `src/` change that precedes it. It must be cut per test tree/feature at P.3, not attempted as one sweep.
- **Gate must land green** — `tests/*` leaves `per-file-ignores` in the **last** commit, exactly as `ruff-d-docstrings` Q-7 does for `src/`.
- **A test docstring is not a test.** Backfilling 313 docstrings proves nothing about coverage; the risk is decorative `AC-XXX:` tags on tests that do not prove the criterion. The Phase 6 review has to spot-check that the cited ID matches what the test asserts.
- **Do not fight `ruff-d-docstrings`** — same `pyproject.toml` list; it must merge first.

## Value triage (2026-10-07, pre-workflow)
- **Overlap:** partly by construction — `ruff-d-docstrings` owns `[tool.ruff.lint] select` / `per-file-ignores` and deliberately excludes `tests/*` (its Q-3 + Q-29), so this item is that decision's second half rather than a duplicate. No other live TODO touches test docstrings.
- **Beneficiary:** future changes and reviewers — a test that names its `AC-XXX` is greppable from spec to test, and the gate stops the convention from decaying again. No end-user-visible effect.
- **Score: 2/5** — real maintainability value and it makes an existing convention enforceable, but it is the largest diff in the repo (762 sites), it changes nothing a user sees, and nothing in CI parses test docstrings today, so the payoff is review quality only.
- **Recommendation:** implement — but only after `ruff-d-docstrings` merges, and prefer the narrow gate (`tests/*` exempt for format families only) so the diff is dominated by real docstrings rather than reformatting.
- **Decision:** **implement** — the user chose this shape at `ruff-d-docstrings` Q-29 ("src/ now, tests/ as follow-up") and Q-6 ("create the sibling pair now"), 2026-10-07.

## Acceptance signal (plain language)
`uv run ruff check .` is green with `D` applied to `tests/` (at least for the missing-docstring codes), every `test_*` function states which requirement or acceptance criterion it proves, and a new undocumented test fails CI the same way an undocumented public function now does.

## Prep log
| Step | Date | Result |
|---|---|---|
| P.1 Frame | 2026-10-07 | Framed from `ruff-d-docstrings` Q-29 + Q-6 (user answers). Measured on `main` @ `f4c5dc0`: `tests/` 762 `D` sites (D1xx 468: D103 358, D102 49, D104 42, D107 19), 727 `test_*` functions, 414 with a docstring / 313 without; `scripts/verify_spec.py:63` skipped, so no CI reader of test docstrings |
| P.2 Interrogate (<n> questions) | | |
| P.3 Answer (<n> answered) | | |
| P.4 Draft scope + create branch/worktree | | |
| P.5 Self-consistency (FEATURE/CROSS-CUTTING) | | |
