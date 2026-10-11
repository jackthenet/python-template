# TODO: complexipy-scripts

Backlog item for one planned change, created at **P.1 Frame** from this template and named `complexipy-scripts.md`. One file per change.

This is a **planning record, not normative**: like `docs/questions/`, it is committed directly to `main` (see "Phase P: PREPARE" in `AGENTS.md`). It carries no approval gate — the spec does.

- **Status:** QUESTIONS-ANSWERED  <!-- PREPARING | QUESTIONS-ANSWERED | READY | IN-WORKFLOW | WAITING | MERGED | DROPPED -->
- **Change type:** DOCS/CHORE  <!-- reclassified at P.3 Q-16 (2026-10-11) from P.1's REFACTOR: the gate widening is the point of the change and the four function restructures exist only to satisfy it, so criterion #5 (no behavior delta) matches before #4. Escalation Rules applied; recorded in docs/verification/complexipy-scripts.md -->
- **Created:** 2026-10-09
- **Question file:** `docs/questions/complexipy-scripts.md`
- **Spec:** n/a  <!-- no spec is authored; the gate is CI config + complexity evidence -->
- **Worktree:** <created at P.4> `../python-template_kopie-worktrees/chore/complexipy-scripts`
- **Depends on:** none — **`map-default-drop-shift` MERGED** (PRs #79/#80, 2026-10-10), so the `scripts/make_map.py` collision P.2 named is gone (**Q-06**); `settings-public-registry-setter` MERGED (PR #81) and touches `[tool.ruff.lint]`, not `[tool.complexipy]`
- **Related specs:** `docs/specs/structure-map.md` — **NFR-005 amended in this change's PR** (its tail says "`scripts/` is not analyzed by complexipy"), with a Changelog entry (**Q-04**)

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
- Extending the gate scope in **both** places: `[tool.complexipy] paths = ["src", "tests", "scripts"]` in `pyproject.toml:100` **and** the explicit CI line `uv run complexipy src tests scripts --max-complexity-allowed 15` at `quality.yml:146` (**Q-05**).
- Behavior-preserving refactors of the four functions above until every function in the three scripts scores **<= 12**, not merely <= 15 (**Q-13**).
- **Algorithmic rewrite is allowed** (iterative DFS, table-driven check list, report-rendering data structure) as long as **stdout stays byte-identical** — text, order, and `check_acyclic`'s first-cycle-only semantics included (**Q-07**, **Q-09**).
- New helpers are **public, module-level, in the same file** (no `scripts/_common.py`); existing names **and** signatures may change (**Q-10**, **Q-11**).
- Amending `structure-map.md` NFR-005 and writing **ADR-087** to supersede ADR-086's `complexipy … widen: no` row (**Q-04**).
- Golden-output evidence: the three CI invocations' stdout + exit codes byte-compared before/after, recorded in `docs/verification/complexipy-scripts.md`; **no test file is added or changed** (**Q-03**, **Q-12**).
- `STRUCTURE.md` regenerated in the same commit as each `scripts/*.py` commit (**Q-14**).

## Out of scope
- Raising or parameterising the `15` ceiling, and any per-file carve-out, baseline or complexipy snapshot — the point is to meet the existing ceiling, not to encode debt.
- Any behavior change to the CI checks themselves (what `check_traceability.py`, `validate_task_dag.py` and `verify_spec.py` detect **and print** stays exactly as it is — **Q-07**).
- `scripts/make_map.py` (already under the ceiling at max 12; edited by the merged `map-default-drop-shift`).
- The near-miss functions elsewhere: `test_ac_008_document_shape` = 15, `_feature_logger_names` = 14, `test_inv_004_other_loggers_untouched` = 14, `test_concurrent_thread_safe` = 14, `SearchService::search` = 13, `SettingsRegistry::create_template` = 13 (**Q-17**).
- New scripts; widening coverage (`source = ["src/backend","src/frontend"]`, `fail_under = 92`, frozen by ADR-086), bandit (`-r src/`), `ty` (`root = ["./src"]`) or mypy beyond `scripts/`.
- A CI `make_map.py --check` job or a `paths:` filter change — the stale-map mechanism is **accepted risk**, no TODO opened (**Q-08**).
- Pinning or downgrading complexipy, or a score ratchet — drift **accepted** (**Q-18**).
- Any `.gitattributes` / line-ending change — owned by the open `gitattributes-line-endings` TODO (**Q-02**).
- A config-contract witness that `scripts/` stays in the gate — CI job is the enforcement (**Q-12**); no `docs/verification/traceability.md` rows (**Q-15**).

## Affected features
No `src/` code. `scripts/check_traceability.py`, `scripts/validate_task_dag.py`, `scripts/verify_spec.py`, `.github/workflows/quality.yml`, `pyproject.toml` (`[tool.complexipy]`), `docs/specs/structure-map.md` (NFR-005), `docs/decisions/ADR-087-*.md` (new), `STRUCTURE.md`.

## Constraints and risks
- **DOCS/CHORE gates (Q-16):** Phase 3 is skipped (no RED), no GREEN baseline is required to enter Phase 4, Phase 5 is the light tier (`uv run ruff check .`, `uv run mypy scripts/`, confirm no test file or behavior touched), Phase 6 is a light review, **no version bump**. The full-regression gate REFACTOR would have imposed is dropped — so the **Q-03 golden-output byte comparison is the primary no-behavior-delta evidence**, and it must be captured **before** any restructuring.
- These three scripts are what CI uses to enforce spec traceability and DAG well-formedness — a silent behavior change here weakens the workflow's own gates, and **two of them have no tests at all**.
- `check_acyclic` (22) and `verify_spec.py::main` (22) are far above the <= 12 target; nothing imports these modules (`src/`, `tests/`, `scripts/`, `.github/` searched; `test_ac_025` invokes them as subprocesses), which is why renaming and re-signaturing are safe (**Q-11**).
- Ruff covers `scripts/` (`lint.yml`); rule `D` is per-file-ignored for `scripts/*` (PR #76), so helpers need no docstring, though a *why* docstring is expected in review. `mypy scripts/` (`disallow_untyped_defs = true`) requires full annotations on every helper.
- **Baseline caveat (Q-01/Q-02):** the full suite on `main` has one host-dependent failure — `test_ac_021_committed_map_matches_fresh_render` fails on this Windows checkout for CRLF reasons (`i/lf w/crlf`, `core.autocrlf=true`, no `.gitattributes`) while the map content is identical (2004 = 2004 lines) and `make_map --check` exits 0. The **CI/Linux run is the authoritative gate**; the `gitattributes-line-endings` TODO owns the fix.
- `STRUCTURE.md` headroom is **196** lines (2004 against the NFR-002 ceiling amended to 2 200), so public helpers and renamed signatures fit (**Q-14**).

## Value triage (2026-10-09, pre-workflow)
- **Overlap:** none — the only complexity gate is the `complexipy` job in `.github/workflows/quality.yml:146`, and it analyzes `src tests` only; no other lint/config enforces complexity on `scripts/`.
- **Beneficiary:** the repo's own guardrails and the next change that touches `scripts/` — today an agent can push a 22-complexity function into the tooling and CI stays silent. No end-user-visible value.
- **Score: 3/5** — real, cheap-to-prevent rot in the code that enforces the workflow, but partly mechanical (four refactors) and benefits the maintainers/agent rather than the end user.
- **Recommendation:** implement — as its own change, after `map-default-drop-shift` lands (type later reclassified to DOCS/CHORE at P.3 **Q-16**).
- **Decision:** **IMPLEMENT** (user, 2026-10-09, recorded via `map-default-drop-shift` Q-19: "separate chore change"). Not merged into another change, not dropped.

## Acceptance signal (plain language)
`uv run complexipy src tests scripts --max-complexity-allowed 15` exits 0 in CI and locally with **every** function in the three scripts at **12 or below**, a bare `uv run complexipy` (config-driven) analyses `scripts/` too, the three CI scripts print **byte-identical** output and exit codes to the recorded golden run, and no test file was touched.

## Prep log
| Step | Date | Result |
|---|---|---|
| P.1 Frame | 2026-10-09 | classified REFACTOR (first-match #4); TODO + question file created on `main`; value triage recorded, decision IMPLEMENT (carried from `map-default-drop-shift` Q-19) |
| P.2 Interrogate (18 questions) | 2026-10-10 | **DONE — 18 questions (Q-01…Q-18), every entry with a `Recommended:` + reason; `### Category coverage` filled; non-goals Q-17 and overlap Q-16/Q-19 present.** Measured: 4 functions over 15 in `scripts/` (17/19/22/22), 49 analysed; `make_map.py` max 12; no test exercises `check_traceability.py` / `validate_task_dag.py`; the gate scope is written twice (`pyproject.toml:100`, `quality.yml:146`); nothing imports the three scripts |
| P.3 Answer (18 answered) | 2026-10-11 | **DONE — 18 questions answered (0 PENDING), 5 rounds.** **Reclassified REFACTOR → DOCS/CHORE (Q-16)** → branch `chore/complexipy-scripts`, light Phase 5, no bump. Gate widened in **both** `pyproject.toml` and the CI line (Q-05); target **<= 12** (Q-13); **stdout byte-identical** is the correctness criterion (Q-07) while **algorithmic rewrite, public same-module helpers and renaming are allowed** (Q-09/Q-10/Q-11); witnesses = golden-output byte comparison, **no test added** (Q-03/Q-12); `structure-map.md` **NFR-005 amended in-PR + ADR-087** supersedes ADR-086's row (Q-04); baseline = CI/Linux authoritative with the CRLF `test_ac_021` failure recorded as a host caveat (Q-01/Q-02); map regenerated per commit, headroom 196 (Q-14); no traceability rows (Q-15); stale-map mechanism **accepted risk, no TODO** (Q-08); complexipy drift **accepted, no pin** (Q-18); proceed to P.4 now — both named collisions merged (Q-06). Next: **P.4 Draft** (scope record + branch + worktree) |
| P.4 Draft spec / triage / baseline / scope | | |
| P.5 Self-consistency (FEATURE/CROSS-CUTTING) | | n/a — DOCS/CHORE |
