# TODO: ruff-d-docstrings

Backlog item for one planned change, created at **P.1 Frame** from this template and named `ruff-d-docstrings.md`. One file per change.

This is a **planning record, not normative**: like `docs/questions/`, it is committed directly to `main` (see "Phase P: PREPARE" in `AGENTS.md`). It carries no approval gate — the spec does.

- **Status:** WAITING  <!-- PREPARING | QUESTIONS-ANSWERED | READY | IN-WORKFLOW | WAITING | MERGED -->
  <!-- IN-WORKFLOW 2026-10-09: entered Phase 4 (S4.1 baseline recorded at 84b25bd), 11 commit groups landed on branch chore/ruff-d-docstrings -->
  <!-- WAITING 2026-10-09: Phase 4 complete (41 src/ files + 4 config files, 37 commits), Phase 5 VERIFIED (full suite 761 passed / 1 skipped vs baseline 1 failed / 760 passed / 1 skipped — only delta is the known pre-existing search timing flake; ruff check . clean with D selected; ruff format --check . 339 files; mypy src/ Success 84 files; mkdocs build --strict ok; deptry clean; check_traceability.py PASS 825 rows; docstring-stripped AST digest 64fc1d6e… byte-identical to base with a non-vacuity control; scope 45/45 DONE, invariants INV-A…INV-J 10/10 HELD), Phase 6 review report CLEAN (0 blockers / 1 minor M-1 fixed at 32b9e2f / 10 notes), no version bump (DOCS/CHORE, stays 1.0.0), change PR #76 opened (https://github.com/jackthenet/python-template/pull/76) -> waiting for the human merge (S6.4 gate) -->
  <!-- READY gate 2026-10-08: all 29 questions ANSWERED + the P.4 artifact (docs/verification/ruff-d-docstrings.md, commit 8ec2edf) verified. DOCS/CHORE has no P.5, so the P.4 artifact is the READY gate. -->
- **Change type:** DOCS/CHORE  <!-- docstrings + ruff select only; no externally observable behavior delta. A docstring that reveals a wrong behavior claim does NOT reclassify this change: it becomes a finding + a separate ISSUE TODO (Q-26, 2026-10-07). -->
- **Created:** 2026-10-04
- **Question file:** `docs/questions/ruff-d-docstrings.md`
- **Spec:** n/a  <!-- DOCS/CHORE: no spec -->
- **Worktree:** created at P.4 (2026-10-08) from `main` @ `45aa61c` — `../python-template_kopie-worktrees/chore/ruff-d-docstrings`, branch `chore/ruff-d-docstrings`
- **Depends on:** none — `pyproject-tooling-gaps` (which deferred this work at its Q-9 and edits the same `select` list) **merged** 2026-10-06 (PR #68, `a278bd2`), so this change branches from a `main` that already contains it. `structlog-logging` also merged (2026-10-07, `c7a9119`) — no sequencing left (Q-21).
- **Depended on by:** `docstrings-tests` (the `tests/` backfill + gate, framed 2026-10-07), and `structure-map` — this change **lands first** (Q-22, 2026-10-07)
- **Related specs:** `docs/specs/logging-coverage.md` (REQ-009 / AC-009 traced-class docstring wording — an invariant this change must not break)

## Goal (one line)
Document the public API so `userdocs/api.md` renders real docstrings instead of blanks, and make that state **enforced** by adding ruff `D` to `[tool.ruff.lint] select`.

## Why
`userdocs/api.md:7-14` renders every feature's public API through mkdocstrings (`::: backend.authentication`, `::: backend.eventbus`, …, driven by the `mkdocstrings` plugin at `mkdocs.yml:13`). Whatever a public object's docstring says **is** the published API documentation — so the missing docstrings are not a style gap, they are gaps in the shipped docs.

Measured 2026-10-04: `uv run ruff check --select D src` → **379 errors**. Re-measured 2026-10-07 on `main` @ `305add3` (ruff 0.16.9): `src/` **386**, `tests/` 762, `migrations/` 11, `scripts/` 3, `.github/hooks/` 1, repo-wide 1 164. The earlier estimate in `pyproject-tooling-gaps` ("156 of 515 public defs lack a docstring") counted only the `D1xx` missing-docstring family and is not reproducible under any `D` rule — the `src/` missing-docstring family is **198** (D102 131, D107 51, D101 14, D105 2), 195 of them on objects listed in a feature's `__all__`.

## In scope
Fixed by the P.3 answers (2026-10-07, `docs/questions/ruff-d-docstrings.md` Q-1 … Q-29). One change, **one commit per feature**, the config edit last:
- **Rule set (Q-1):** `"D"` added to `[tool.ruff.lint] select`, plus a new `[tool.ruff.lint.pydocstyle]` section with `convention = "google"` (328 `src/` sites under that convention; `D401` is off, so descriptive noun-phrase first lines stay).
- **Style (Q-2):** Google style — `Args:` / `Returns:` / `Raises:` sections on callables that have parameters or a return. mkdocstrings/griffe's default parser already matches.
- **Trees gated (Q-3, Q-23, Q-29):** `src/` only. New `[tool.ruff.lint.per-file-ignores]` section exempts `tests/*`, `scripts/*`, `migrations/*`, `.github/*`. The `tests/` backfill + gate is the sibling change `docstrings-tests`.
- **Docstring content (Q-9, Q-13, Q-14, Q-16):** all 51 `D107` `__init__` sites included (no `errors.py` exemption); the two `D105` `EventBus.__enter__`/`__exit__` documented; private helpers **inside the touched files** documented too (review-checked, not gate-checked); `REQ-XXX`/`AC-XXX` IDs stay cited inside docstrings.
- **Formatting (Q-11):** the 123 `src/` format sites (`D205` 66, `D209` 57, `D301` 3, `D403` 4) are fixed in **separate commits** from the docstring additions.
- **`fixable` (Q-12):** `[tool.ruff.lint] fixable` gains the fixable `D` codes; `--fix` stays scoped to the step's changed paths (AGENTS.md P-6).
- **Config commit (Q-7, Q-18, Q-28):** `pyproject.toml` (`select`, `pydocstyle`, `per-file-ignores`, `fixable`) + `mkdocs.yml` (`docstring_style: google`) + `.pre-commit-config.yaml` (hook rev `v0.15.12` → `v0.16.9`) — last commit, so `lint.yml` is green at every commit on `main`.
- **Guidance (Q-24):** extend the `AGENTS.md` "Documentation" line (currently `AGENTS.md:737`) with the enforced convention and the no-filler rule.
- **Invariant (Q-17):** never drop the "traced"/"logged" mention from any of the 45 `@logged_class` classes' docstrings (logging-coverage REQ-009 / AC-009); `tests/acceptance/logging_coverage/test_docstrings.py::test_traced_class_docstrings_mention_tracing` is re-run in Phase 5.
- **No-filler rule (Q-15):** stated in the scope record and added to the Phase 6 review checklist — no scripted checker.

## Out of scope
- Any change to what the code **does** — docstrings and config only. **Procedure when a docstring reveals a wrong behavior claim (Q-26):** record it as a finding, write the docstring that matches the code, open a separate ISSUE TODO — this change stays DOCS/CHORE and finishes.
- `userdocs/` prose (Q-20): `userdocs/api.md` keeps its 8 packages, so `permissions` (32 `D1xx` sites), `search` (6) and `shared` stay unrendered — a known gap, not an oversight.
- `tests/`, `scripts/`, `migrations/`, `.github/` docstrings and their gate — the sibling change `docstrings-tests` (Q-29).
- Type-annotation work — that belongs to the mypy strictness step (`pyproject-tooling-gaps` Q-8 enabled `disallow_untyped_defs`; a follow-up may enable `warn-return_any`, measured at 20 errors in 12 files).
- The `python-best-practices` skill (Q-24) and the `mkdocs-build` pre-push hook's `files:` filter (Q-19).

## Affected features
All rendered features, docstrings only: `backend/{authentication,eventbus,filemanagement,logging,mail,sessionmanagement,settings,usermanagement,permissions,search}`. Config: `pyproject.toml` `[tool.ruff.lint] select`.

## Constraints and risks
- **386 `src/` sites is a lot for one PR** (328 under the chosen google convention). Mitigated by the per-feature commit split (Q-5 a): authentication 50, usermanagement 45, filemanagement 37, permissions 32, settings 14, mail 6, search 6, eventbus 3, sessionmanagement 2 published `D1xx` sites.
- **Filler docstrings** are the TODO's own named risk and nothing detects them mechanically (Q-15: reviewer rule + Phase 6 checklist). Q-9's "all 51 `D107`, no exemption" and Q-14's "private helpers too" both raise that risk — they are the two places the no-filler check has to be applied hardest.
- **Docstrings are published output.** `mkdocs build --strict` is a CI gate, and the `mkdocs-build` pre-push hook does **not** fire on a `src/`-only change — so Phase 5 runs `uv run --group docs mkdocs build --strict` itself (Q-19).
- **Gate must land green.** `ruff check .` is green on `main` today; the `select` edit is the **last** commit (Q-7 a).
- **No behavior delta must be proven, not asserted** (Q-25): full suite + `ruff check .` + `ruff format --check .` + `mkdocs build --strict` + a one-off AST-equality check with docstrings stripped, recorded in `docs/verification/ruff-d-docstrings.md`.
- **`AGENTS.md` is shared with `structure-map`** — this change lands first (Q-22), so `structure-map` rebases.
- **Version: no bump** (Q-27, DOCS/CHORE). The version is 1.0.0 today.

## P.3 decisions (2026-10-07) — binding inputs for P.4
Q-1 `"D"` + `convention = "google"` · Q-2 Google sections · Q-3 `src/` only + `per-file-ignores` · Q-4 test docstrings mandatory, delivered by the follow-up · Q-5 one change, per-feature commits · Q-6 sibling TODO created · Q-7 docstrings first, config last · Q-8 no gap (single PR) · Q-9 all 51 `D107` · Q-10 `D401` off · Q-11 formatting in, separate commits · Q-12 `fixable` widened · Q-13 dunders documented · Q-14 private helpers in touched files · Q-15 reviewer rule · Q-16 spec IDs stay · Q-17 traced-wording invariant · Q-18 pin `docstring_style: google` · Q-19 mkdocs strict in Phase 5 · Q-20 `api.md` untouched · Q-21 moot (structlog merged) · Q-22 this change first · Q-23 `migrations/` exempt · Q-24 `AGENTS.md` line · Q-25 AST-equality evidence · Q-26 finding + separate ISSUE TODO · Q-27 no bump · Q-28 hook rev to v0.16.9 · Q-29 conflict resolved → `docstrings-tests`.

## Acceptance signal (plain language)
`uv run ruff check .` is green **with `D` selected over `src/`**, every public object in the 11 backend packages has a docstring that says something its signature does not, `userdocs/api.md` renders real text instead of blanks, and `mkdocs build --strict` still passes — while the full test suite and `mypy src/` are unchanged.

## Value triage (2026-10-04, pre-workflow)
- **Overlap:** none — no other backlog item does docstring work; `pyproject-tooling-gaps` explicitly deferred it to this item (Q-9).
- **Beneficiary:** readers of the published API reference (`userdocs/api.md` via mkdocstrings) and every future change, because the `D` gate stops further drift.
- **Verdict:** **ACCEPT — 3/5, incremental.** Real consumer, mechanical work, but large: it must be scoped per feature at P.3, not attempted as one 379-error sweep.

## Preparation log

| Step | Date | Result |
|---|---|---|
| P.1 Frame | 2026-10-04 | Framed from `pyproject-tooling-gaps` Q-9 (user decision: `D` off + backlog TODO). Measured cost re-checked: `ruff check --select D src` → 379 errors; consumer confirmed at `userdocs/api.md:7-14` + `mkdocs.yml:13` |
| P.2 Interrogate (28 questions) | 2026-10-05 | **BLOCKED-USER** — 28 questions (**Q-1 … Q-28**) recorded in `docs/questions/ruff-d-docstrings.md`, one batch, most-blocking first (Q-1 the `D` code subset, Q-2 the docstring style, Q-3/Q-4 which trees the gate covers, Q-5/Q-6/Q-7 the increment shape and how `select` lands green). Re-measured on `main` @ `305add3`: `src/` **386** (`D1xx` 198 — 195 of them on `__all__`-published objects), `tests/` 762, `migrations/` 11, `scripts/` 3, `.github/hooks/` 1, repo-wide 1 164; 43 `src/` files affected (18 docstring-only, 8 format-only, 17 both). **Two numbers in this TODO are stale** — "379 errors" is now 386, and "156 of 515 public defs lack a docstring" is not reproducible under any `D` rule (the `src/` missing-docstring family is 198: D102 131, D107 51, D101 14, D105 2); the preamble carries the measured figures and a Problem Log entry is owed at P.4 in the change worktree |
| P.3 Answer (29 answered) | 2026-10-07 | **7 rounds, all ANSWERED + incorporated** (Q-1…Q-29; Q-8, Q-10, Q-21 closed by implication). Two conflicts found and resolved by the orchestrator: **Q-3 vs Q-4** (gate `src/` only vs gate `tests/`) → Q-29: `src/` now, `tests/` moved to the new sibling TODO `docstrings-tests`; **Q-2's premise** (plain prose) was overridden by the user's Google-style choice, which re-opened Q-18 → `mkdocs.yml` pins `docstring_style: google`. Two question premises were found stale and corrected: Q-21 (`structlog-logging` had already merged) and Q-27 (version is 1.0.0, not 0.6.1). TODO advanced PREPARING → QUESTIONS-ANSWERED |
| P.4 Draft scope + create branch/worktree | 2026-10-08 | **DONE** — branch `chore/ruff-d-docstrings` + worktree from `main` @ `45aa61c`; `docs/verification/ruff-d-docstrings.md` (239 lines, commit `8ec2edf`) carries the DOCS/CHORE classification + the Q-26 escalation amendment, the exact file-level scope (`pyproject.toml` `select`/`pydocstyle`/`per-file-ignores`/`fixable`, `mkdocs.yml`, `.pre-commit-config.yaml`, `AGENTS.md:743`, 41 `src/` files in a 10-feature + 1-config commit split, config last), the Phase-5 no-behavior-delta **proof** plan (full suite, `ruff check .`, `ruff format --check .`, `mypy src/`, `mkdocs build --strict`, the AC-009 docstring test, and the AST-equality digest `64fc1d6e…` with a control run), and invariants INV-A…INV-J. **Fresh figures (ruff 0.16.10 @ `45aa61c`):** `src/` 398 bare / **328 under `convention = "google"`** (D1xx 198), `tests/` 827/743, `migrations/` 11/7, `scripts/` 3, `.github/` 2. **9 findings** F-1…F-9: the TODO's 379 and "156 of 515" are stale, `@logged_class` is 41 not 45, the per-feature D1xx split moved (usermanagement 47, permissions 33), the format-family count is 130 not 123 with only 61 auto-fixable, Q-28's hook rev is `v0.16.10` not `v0.16.9`, `docstring_style: google` is an inert pin (mkdocstrings-python 2.0.8 default), and **F-9: `uv.lock` on `main` records `python-template 0.6.1` while `pyproject.toml` says `1.0.0`, so every `uv run` rewrites `uv.lock`** — orchestrator decision at P.4: fold the one-line refresh into this change's config commit, every other step reverts incidental `uv.lock` churn (logged as P-74) |
| P.5 Self-consistency (FEATURE/CROSS-CUTTING) | | |
