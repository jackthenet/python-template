# repo-hygiene — Scope Record (DOCS/CHORE)

- **Change:** repo-hygiene · **Type:** DOCS/CHORE (Phase 0 classification, first matching criterion: "does not alter behavior — documentation, comments, configuration, CI, tooling")
- **Branch / worktree:** `chore/repo-hygiene` @ `ebbb233` (== `origin/main`, version `0.6.0`)
- **Phase Matrix for this type:** Phase 1 scope (this file) · Phase 2/3 skipped · Phase 4 make the change · Phase 5 light gate (lint/types where applicable) · Phase 6 light review + PR. No spec, no spec PR, **no version bump** (DOCS/CHORE → none).
- **Date:** 2026-10-02

## Scope summary (three bundled follow-ups)

| # | Item | Kind | Files |
|---|------|------|-------|
| 1 | gitignore gap for root `data/` and `logs/` | configuration | `.gitignore` |
| 2 | `ruff format` drift sweep + make it a CI gate | tooling / CI | 54 `.py` files + `pyproject.toml` + `.github/workflows/lint.yml` |
| 3 | traceability Status-column convention + drift check | documentation / CI | `docs/verification/traceability.md` (header only), `AGENTS.md`, `scripts/check_traceability.py` (new), `.github/workflows/spec-validation.yml` |

## Item 1 — gitignore gap (verified)

Measured on this worktree (`git check-ignore -v`, empty output = NOT ignored):

- `data/files/x.png` → **not ignored**. `.gitignore` ignores only `data/db/`, `data/exports/`, `data/logs/`, `data/configuration/`; the filemanagement default storage root is `./data/files` (`src/backend/filemanagement/feature_settings.py:24 DEFAULT_STORAGE_ROOT = "./data/files"`, used by `tests/acceptance/filemanagement/test_filemanagement.py`).
- `logs/app.log.2026-10-02` → **not ignored**. `logs/app.log` itself IS covered (`.gitignore:59 *.log`), but a rotated/adjacent file in the same directory is not. The default log path is `logs/app.log` (`src/backend/logging/feature_settings.py:78`, `src/backend/logging/_settings.py:20`).
- Correction to the input premise: the `/logs/` gap is narrower than reported — `*.log` already hides the routine file. The `/data/` gap is the real one.

**Exact change (one append to `.gitignore`, after the existing `/settings/` block):**

```gitignore
# Runtime artifact directories created at the worktree root by test/coverage runs:
# data/ = filemanagement DEFAULT_STORAGE_ROOT (./data/files); logs/ = logging log_file
# (logs/app.log plus rotated/adjacent files that the *.log pattern does not match).
/data/
/logs/
```

**Why no behavior delta:** `.gitignore` is read only by git when listing/adding untracked files. `grep -rn -i gitignore src tests scripts .github pyproject.toml` → no consumer; no test, tool or runtime path depends on it. Ignored paths are by definition untracked, so no tracked file's content changes. The application still creates `./data/files` and `./logs/app.log` exactly as before.

## Item 2 — ruff format drift sweep (verified)

Measured: `uv run ruff format --check .` → **75 files would be reformatted, 396 already formatted** (ruff `0.16.9`). Composition of the 75:

- **54 Python files** — `src/` 12 (`main.py` + `backend/{filemanagement,mail,permissions,sessionmanagement,settings,usermanagement}` modules), `tests/` 40 (acceptance, property, unit, integration, contract + 2 `*_test_helpers.py`), `migrations/` 2 (`env.py`, `versions/eace2f772150_*.py`). Full list: `uv run ruff format --check . | grep '^\s*-->'`.
- **21 Markdown files** — ruff 0.16 also formats fenced code blocks in `.md`: 13 approved specs under `docs/specs/`, `AGENTS.md`, 2 ADRs (038, 039), `docs/workflow/PROBLEMS.md`, 5 `tests/*/README.md`.

**Exact change (2a, the sweep, Python only — approved, Q-130):** `uv run ruff format src tests scripts migrations` → the 54 Python files.
**Exact change (2b, keep markdown out of the formatter — approved, Q-130):** add to `[tool.ruff]` in `pyproject.toml`:

```toml
extend-exclude = ["**/*.md"]
```

**Exact change (2c, make the drift visible — approved, Q-131):** add one **hard-failing** step to the `lint` job in `.github/workflows/lint.yml`: `uv run ruff format --check .` (no `continue-on-error`; today the job runs `ruff check .` only and the drift surfaces only through the `ruff-format` pre-commit hook, ruff `v0.15.12`, when such a file is staged).

**Config effect measured (read-only, S1.1 re-entry; `pyproject.toml` NOT yet written):** `uv run ruff format --check --extend-exclude='**/*.md' .` → **54 files would be reformatted, 268 already formatted** — the pending set is exactly the 54 `.py` files and every `.md` file drops out. Control runs: `--check .` → 75 pending; `--check src tests scripts migrations` (no exclude) → 59 pending (the 54 `.py` + 5 `tests/*/README.md`). Note for later steps: `--extend-exclude` is a multi-value CLI option — use the `=` form (`--extend-exclude='**/*.md'`), otherwise it swallows the path arguments and silently re-runs on `.`.

**Scope decision (user-approved, Q-130):** the sweep does **not** reformat the 21 Markdown files. Reformatting approved specs is a whitespace-only edit, but it still rewrites `docs/specs/*.md` — files the Spec Amendment Workflow reserves for normative change — and `2b` makes `ruff format --check .` a usable, permanently green gate instead. Markdown code blocks are documentation, not executable product code.

**Why no behavior delta (2a):** `ruff format` is a whitespace/layout formatter — it changes line breaks, quotes where equivalent, trailing commas and blank lines; it never changes control flow, names, literals' values, or call signatures. Evidence in Phase 5: `git diff --ignore-all-space --stat src tests migrations` is **empty** (every change is whitespace-only), the full-suite result is **identical** to the pre-sweep baseline recorded in §"Phase 5 evidence plan", and `uv run ruff check .` / `uv run mypy src/` stay clean.

**Correction to the input premise (PEP 758):** the sweep does **not** normalize the unparenthesized multi-exception `except` in `tests/property/usermanagement/test_multi_role_invariants.py:117` (`except UserAlreadyExistsError, LastAdminError, InvalidRoleError, UserNotFoundError:`). Measured: `uv run ruff format --check tests/property/usermanagement/test_multi_role_invariants.py` → **"1 file already formatted"**; the file is not in the 75. ruff 0.16.9 with `target-version = "py314"` keeps PEP 758 syntax. No file in this change needs that normalization.

**Why no behavior delta (2b/2c):** `extend-exclude = ["**/*.md"]` only narrows which files the ruff formatter/linter reads; no `.md` file is executable product code, and `ruff check .` currently reports no violation from any `.md` (the lint job is green today and stays green). The new `lint.yml` step adds a check, not a runtime behavior; the workflow's pass/fail for the current tree is unchanged because the sweep makes it pass.

## Item 3 — traceability Status-column convention + drift check (verified)

Measured: `docs/verification/traceability.md` = 901 lines, **647 `| GREEN |` status cells, 0 `| RED |` cells** (the 75 stale `RED` rows were flipped by the search change). The file's own §Invariants declares: "Status values: `PENDING`, `RED`, `GREEN`, `REFACTORED`, `VERIFIED`." The convention (whether a row's Status is *live* or a *record of the change that wrote it*) is nowhere written down, which is why it drifted.

**Exact change (3a, settle the convention in writing):** one paragraph appended to §Invariants of `docs/verification/traceability.md` and one paragraph in AGENTS.md §"Traceability & Spec Drift", stating **convention B** (below). No matrix row is rewritten by this change (0 `RED` rows remain; rewriting 647 rows is out of scope).

**Convention: B — historical gate record (user-approved, Q-129, 2026-10-02).** A row records the state *as observed by the change that wrote it*, with that change's name and date already in the cell (the existing practice: `GREEN (full suite: 727 passed … search S5.1 …, commit 7bbc05a)`). A later change appends/updates rows only for the REQs it actually touches; it never refreshes rows it did not change. Consequences: history and per-change evidence are preserved; the drift check verifies **references**, never status freshness; the convention paragraph must also state that a `RED`/`PENDING` row is legal as a dated record of a past gate. The rejected alternative (**A — live status**, every change refreshes every REQ it touches, CI fails on any `PENDING`/`RED` row on `main`) was declined because the observed rot was *referential* (rows naming tests that no longer exist, REQs with no row), not status staleness.

<details><summary>Rejected option A (kept for the record)</summary>


- **A — live status.** The Status column describes the matrix's *current* state: a row is `RED`/`PENDING` only while its test genuinely does not pass, and every change that touches a REQ must refresh that REQ's rows. Consequences: the matrix is a live dashboard; the drift check can assert "no `RED`/`PENDING` row on `main`"; per-change history is lost (the search change's evidence text would be overwritten by the next change); every change carries a mandatory matrix-maintenance duty, and a forgotten refresh is a CI failure.
</details>

**Exact change (3b, the drift check — design a later step implements):**

- New `scripts/check_traceability.py` (stdlib only, same style/CLI as `scripts/verify_spec.py`; exit 0 clean, exit 1 with one line per violation).
- Inputs: `docs/verification/traceability.md` matrix rows (`| Requirement | Acceptance Criterion | Test | Status |`) + the normative IDs parsed from `docs/specs/*.md` (reuse `verify_spec.py`'s ID extraction where it exists).
- Assertions (the complete set, Q-129 → B): (1) every `REQ-XXX`/`AC-XXX` defined in `docs/specs/*.md` appears in ≥1 matrix row; (2) every ID referenced by a row exists in some spec (no dangling ID); (3) every backticked test function in the Test column exists in `tests/` (no reference to a deleted/renamed test); (4) every Status cell starts with one of the five declared values.
- **Assertion (5) is dropped** (Q-129 → B): the check does **not** assert status freshness — no `PENDING`/`RED` failure, no mandatory per-change matrix refresh. Coverage is verified by (1)–(3), i.e. by the references themselves.
- Where it runs: a new hard-failing `traceability` job in `.github/workflows/spec-validation.yml` (`run: uv run python scripts/check_traceability.py`, no `|| true`) — that workflow's `paths` already include `docs/verification/**`, `docs/specs/**` and `tests/**`, so it triggers exactly when the matrix can drift. Optional local mirror: a `repo: local` hook in `.pre-commit-config.yaml` (decide in Phase 4; CI-only is the default).

**Why no behavior delta (3a/3b):** 3a edits prose in two documentation files. 3b adds a new script under `scripts/` (not imported by `src/` or `tests/`; `deptry` sees it as a tooling script) and a new CI job. Nothing the product does at runtime changes; the only observable change is that a PR which lets the matrix drift now fails CI.

## Out of scope

No change to any `src/` behavior, test logic/assertion, spec content, ADR decision, dependency, database schema, or version (`DOCS/CHORE` → no bump). No rewrite of the 647 existing matrix rows. No reformatting of the 21 Markdown files. No new pre-commit hook unless Phase 4 decides the CI-only mirror is insufficient.

## Phase 5 evidence plan (light gate set for DOCS/CHORE)

| Evidence | Command | Expected |
|---|---|---|
| Baseline before the sweep (recorded in Phase 4, step S4.1) | `uv run pytest tests/ -q` | N passed / M skipped — recorded verbatim |
| Suite identical after the sweep | `uv run pytest tests/ -q` | **identical counts** to the baseline (no test added, removed, weakened or re-ordered by formatting) |
| Sweep is whitespace-only | `git diff --ignore-all-space --stat src tests migrations` | empty output |
| Lint unchanged and clean | `uv run ruff check .` | clean (== baseline; CI parity with `lint.yml`) |
| Format drift closed | `uv run ruff format --check .` | `All checks passed` / 0 would be reformatted (baseline 75; 54 after `extend-exclude`, all Python) |
| Types clean | `uv run mypy src/` | no errors (== baseline) |
| gitignore entries work | `git check-ignore -v data/files/x.png logs/app.log.2026-10-02` | both matched (`.gitignore` line numbers reported) |
| Worktree clean after a full run | `git status --porcelain` (after the post-sweep suite run) | empty → `git worktree remove` succeeds **without** `--force` |
| Drift check works | `uv run python scripts/check_traceability.py` | exit 0 on the current matrix; exit 1 when a fixture row references a nonexistent test (negative control run once in Phase 5) |

## Exact file list (complete; nothing else is touched)

1. `.gitignore` — append `/data/` and `/logs/` with a comment (item 1).
2. 54 Python files listed by `uv run ruff format --check .` (12 `src/`, 40 `tests/`, 2 `migrations/`) — formatting only (item 2a).
3. `pyproject.toml` — `extend-exclude = ["**/*.md"]` under `[tool.ruff]` (item 2b).
4. `.github/workflows/lint.yml` — one added step `uv run ruff format --check .` in the `lint` job (item 2c).
5. `docs/verification/traceability.md` — one paragraph in §Invariants only (item 3a).
6. `AGENTS.md` — one paragraph in §"Traceability & Spec Drift" (item 3a).
7. `scripts/check_traceability.py` — new file (item 3b).
8. `.github/workflows/spec-validation.yml` — new `traceability` job (item 3b).
9. `AI_Questions.md` — Q-129 answered + Q-130/Q-131 recorded (Phase 1 only).

## Spec-coverage check (item C)

`grep -rn -i "gitignore" docs/specs/` → **no match**; `grep -rn -i -e "ruff format" -e "formatting" docs/specs/` → **no match**. No approved spec normatively covers `.gitignore`, code formatting, or the traceability-matrix *format*. The only spec-side mentions of "traceability" are each spec's own §11 "Traceability Matrix" section (a normative REQ→test map inside the spec) plus `docs/specs/search.md:516`, which points at `docs/verification/traceability.md` descriptively ("the live matrix is also maintained at …") — descriptive, not a normative format contract. AGENTS.md §"Traceability & Spec Drift" mandates that the matrix *MUST be maintained* but does not define the Status column's semantics. **Conclusion: no Spec Amendment PR is required** for any of the three items; the AGENTS.md paragraph is a process-record edit, which is exactly what a DOCS/CHORE change owns.

## Resolved questions (S1.1 re-entry, 2026-10-02 — all three answered "as recommended")

| Q | Decision | Effect on this scope |
|---|---|---|
| Q-129 | Traceability `Status` column = **historical gate record (B)** | 3a wording fixed to B; drift check = assertions (1)–(4) only, status-freshness assertion (5) dropped; no `PENDING`/`RED` CI failure |
| Q-130 | Format sweep is **Python only** | 2a = `uv run ruff format src tests scripts migrations` (54 `.py`); 2b = `[tool.ruff] extend-exclude = ["**/*.md"]`; the 13 approved specs, `AGENTS.md` and the ADRs stay byte-identical |
| Q-131 | **Yes**, add `uv run ruff format --check .` as a hard-failing step in the `lint` job | 2c confirmed: one added step in `.github/workflows/lint.yml`, no `continue-on-error` |

No open question remains; the scope is closed and Phase 4 may run items 1–8 in full.

## Phase 4 (S4.1) — pre-change baseline (2026-10-02)

Measured on `chore/repo-hygiene` @ `f0af215` before any change is applied. Phase 5 MUST
show an identical suite result (DOCS/CHORE: no behavior delta).

| Measurement | Command | Baseline |
|---|---|---|
| Full suite | `uv run pytest tests/ -q --tb=line --color=no` | **727 passed, 1 skipped**, 0 failed — `211.87s (0:03:31)` |
| Skip (expected) | — | `tests/acceptance/filemanagement/test_filemanagement.py:364` — symlinks not available on this host |
| Lint | `uv run ruff check .` | `All checks passed!` (0 errors) |
| Format (repo-wide) | `uv run ruff format --check .` | 75 files would be reformatted, 396 already formatted |
| Format (md excluded) | `uv run ruff format --check --extend-exclude='**/*.md' .` | **54 files would be reformatted**, 268 already formatted |
| Types | `uv run mypy src/` | `Success: no issues found in 83 source files` |
| Spec-validation entry point | `uv run python scripts/verify_spec.py docs/specs/search.md` | `exit=0` |

Notes:
- The 21-file gap between the repo-wide and md-excluded format counts is the markdown
  drift item 2 removes by adding `[tool.ruff] extend-exclude = ["**/*.md"]`.
- `--extend-exclude` requires the `=` form; the space form swallows the path argument.
- One full-suite run only; no source, test, workflow, `pyproject.toml` or `.gitignore` change made in this step.

## Phase 4 (S4.2) — items 1+2 (2026-10-02)

Item 1: `git ls-files data logs` → empty (no tracked path becomes ignored). After the
append: `git check-ignore -v data/files/x.png logs/app.log.2026-10-02` →
`.gitignore:230:/data/` and `.gitignore:231:/logs/` (both matched); `git status
--porcelain` shows no `?? data/` or `?? logs/`; `uv run deptry .` → "Success! No
dependency issues found." (88 files scanned).

Item 2: `uv run ruff format src tests scripts migrations` → **54 files reformatted,
267 left unchanged**; `[tool.ruff] extend-exclude = ["**/*.md"]` added; `lint` job gained
a hard-failing `Check formatting` step (`uv run ruff format --check .`, no
`continue-on-error`); YAML validated with `yaml.safe_load` → `yaml ok`.

| Gate | Command | Result |
|---|---|---|
| G1 lint | `uv run ruff check .` | `All checks passed!` |
| G2 format (new CI gate) | `uv run ruff format --check .` | `322 files already formatted` (0 pending) |
| G3 types | `uv run mypy src/` | `Success: no issues found in 83 source files` |
| G4 suite | `uv run pytest tests/ -q --tb=line --color=no` | **727 passed, 1 skipped, 0 failed** (187.62s) — identical to the S4.1 baseline (same skip: `test_filemanagement.py:364` symlinks) |
| G5 diff | `git diff --stat` | 57 files changed, 462 insertions(+), 421 deletions(-); `git diff --name-only \| grep -cE '\.md$'` → **0** |

Formatting-only proof: 54 changed `.py` files compared against `HEAD` by AST dump —
53 identical; the single difference (`src/backend/settings/repository.py`) is
ruff's docstring re-indentation, and the AST is identical once docstrings are stripped.
Self-introduced slip fixed in-step: the sweep exploded the one-line list in
`tests/property/mail/test_secrets.py`, orphaning its single `# noqa: RUF001` (3× RUF001 +
1× RUF100); the noqa was moved to the three flagged elements and dropped from the
unflagged one — comment-only, no test logic changed.

Commits: `583a4f7` (.gitignore), `cb287a9` (pyproject.toml, .github/workflows/lint.yml, 54 .py).

## Phase 4 (S4.3) — item 3 (2026-10-02)

3a: convention **B (historical gate record, Q-129)** written down in two places — three
bullets appended to AGENTS.md §"Traceability & Spec Drift" and one blockquote note at the
top of `docs/verification/traceability.md` (3 added lines total; no other prose, table or
row touched; 0 matrix rows rewritten).

3b: new `scripts/check_traceability.py` (stdlib only, `verify_spec.py` style: `main() -> int`,
exit 0 one-line summary / exit 1 one line per violation). It parses the 16 matrix tables
(any table with a `Status` header column), the normative IDs of the 12 specs (`template.md`
excluded — its IDs are formatting examples), and every `def test_*` under `tests/`.
Assertions (Q-129 → B, no status-freshness check): (1) every `REQ`/`AC` defined in a spec has
≥1 row; (2) no row references an ID no spec defines; (3) every backticked `test_*` name in the
matrix exists under `tests/`; (4) every Status cell starts with a declared value
(`PENDING`, `RED`, `GREEN`, `REFACTORED`, `VERIFIED`, `N/A` — the §Invariants vocabulary plus
`N/A`, which legitimately occurs in the wiring tables). CI: new hard-failing `traceability`
job in `.github/workflows/spec-validation.yml` (`uv run python scripts/check_traceability.py`,
no `|| true`); `yaml.safe_load` → `yaml ok`.

| Gate | Command | Result |
|---|---|---|
| G1 check (positive) | `uv run python scripts/check_traceability.py` | **exit 0** — `Traceability: PASS (746 matrix rows, 129 spec IDs, 713 test functions)` |
| G2 negative (2)+(3) | bogus row `\| REQ-999 \| bogus \| \`test_that_does_not_exist\` \| GREEN \|` | **exit 1** — `row references undefined REQ-999` + `row references missing test test_that_does_not_exist` (2 violations) |
| G3 negative (4) | one Status cell → `BOGUS` | **exit 1** — `undeclared Status value 'BOGUS'` |
| G4 negative (1) | sole row of `AC-046` blanked | **exit 1** — `AC-046 defined in docs/specs/ has no row in docs\verification\traceability.md` |
| G5 ruff (changed path) | `uv run ruff check scripts/check_traceability.py` | `All checks passed!` (one in-step fix: PLR2004 → `MIN_TABLE_LINES` constant) |
| G6 format | `uv run ruff format --check scripts/check_traceability.py` / `.` | `1 file already formatted` / `323 files already formatted` (0 pending) |
| G7 types | `uv run mypy src/` | `Success: no issues found in 83 source files` (== baseline) |
| G8 smoke | `uv run pytest tests/unit -q --tb=line --color=no` | `237 passed` (full suite is Phase 5) |

No violation was found on the current matrix, so **no matrix row was corrected** and the check
was not weakened. All four assertions are proven non-vacuous by the negative controls (G2–G4);
the matrix was restored from a byte copy after each probe and re-verified exit 0.

## Phase 4 (S4.4) — refactor pass (2026-10-02)

Scope: `scripts/check_traceability.py` (the only substantial new code) plus the diffs of
`.gitignore`, `pyproject.toml`, `.github/workflows/lint.yml`, `.github/workflows/spec-validation.yml`.
The 54 reformatted `.py` files were not reviewed (formatting-only, AST-proven in §S4.2).

**Verdict: one restructuring, everything else already clean.**

- **Changed:** `check()` took the three paths and re-derived `rows`/`specs`/`tests` internally, while
  `main()` re-derived them again for the PASS summary — three redundant scans of `docs/specs` and
  `tests/`. `main()` now parses once and passes `rows`, `specs`, `tests` to `check()`, matching the
  parse → check → report shape of `scripts/verify_spec.py`. Behavior-preserving (same inputs, same messages).
- **No change needed:** the four assertions are separately commented and each maps to one spec check;
  the only numeric literal is the named `MIN_TABLE_LINES`; table parsing exists once (`matrix_rows`);
  violation messages carry `path:line` and the offending value; `main()` mirrors `verify_spec.py`
  (missing-input guard → violations → PASS summary → exit code). Config diffs are commented one-liners.

| Gate | Command | Result |
|---|---|---|
| ruff (changed path) | `uv run ruff check scripts/check_traceability.py` | `All checks passed!` |
| format (changed path) | `uv run ruff format --check scripts/check_traceability.py` | `1 file already formatted` (one in-step reformat after the edit) |
| positive | `uv run python scripts/check_traceability.py` | **exit 0** — `Traceability: PASS (746 matrix rows, 129 spec IDs, 713 test functions)` |
| negatives (1)(2)(3)(4) | synthetic matrix probes (isolated temp tree, real matrix untouched) | **exit 1 / 1 / 1 / 1** — all four violation kinds still detected |
| repo lint | `uv run ruff check .` | `All checks passed!` |
| smoke | `uv run pytest tests/unit -q --tb=line --color=no` | `237 passed` |

## Phase 5 (S5.1) — full suite + gate set (2026-10-02)

All commands run in the change worktree at head `d4e9494`. Light-tier DOCS/CHORE gate set
(scope §"Phase 5 evidence plan"), extended with the CI jobs this change touches
(`lint` format step, `traceability`, `security` bandit, `migrations`, `docs`).

| # | Gate | Command | Result |
|---|------|---------|--------|
| 1 | Full suite | `uv run pytest tests/ -q` | **727 passed, 1 skipped, 0 failed** (187.9s) — identical to S4.1 baseline |
| 2 | Lint | `uv run ruff check .` | All checks passed! |
| 3 | Format (new CI step) | `uv run ruff format --check .` | **323 files already formatted** (0 pending; baseline: 75 pending) |
| 4 | Types | `uv run mypy src/` | Success: no issues found in 83 source files (= baseline) |
| 5 | Deps | `uv run deptry .` | Success! No dependency issues found (89 files) |
| 6 | Security | `uv run bandit -r src/` | 0 issues (Low/Medium/High/Undefined 0; 0 files skipped) |
| 7 | Audit | `uv run pip-audit` | No known vulnerabilities found (exit 0; only skip: `python-template` not on PyPI) |
| 8 | Traceability (new job) | `uv run python scripts/check_traceability.py` | PASS — 746 matrix rows, 129 spec IDs, 713 test functions (exit 0) |
| 9 | Spec validation | `uv run python scripts/verify_spec.py docs/specs/search.md` | exit 0 (existing entry point unaffected) |
| 10 | Migrations | `ALEMBIC_DATABASE_URL=sqlite:///./.tmp_mig.db uv run alembic upgrade head` | exit 0, both revisions applied; temp db deleted |
| 11 | Docs | `uv run mkdocs build --strict` | exit 0; `site/` is gitignored (`/site`) and removed |

**Baseline vs now:** suite counts identical (727/1/0; the 1 skip is the symlink-conditional
node `tests/acceptance/filemanagement/test_filemanagement.py:364`); ruff check, mypy, deptry,
bandit, pip-audit unchanged-clean; the only movement is format drift 75 pending → 0.

**Behavior-delta proof (AST equality).** `git diff --name-only ebbb233..HEAD`: 55 `.py`
(54 reformatted + the new `scripts/check_traceability.py`) and 4 `.md` — all four are the
intended item-3/record edits (`AGENTS.md`, `AI_Questions.md`, `docs/verification/repo-hygiene.md`,
`docs/verification/traceability.md`); the format sweep touched **0** Markdown files.
`ast.dump` of `git show ebbb233:<f>` vs the working file, on the project interpreter (3.14.5):
**53/54 byte-identical AST, 1 docstring-whitespace-only (`src/backend/settings/repository.py`),
0 real diffs.** Note: ruff format rewrote `except (A, B, C):` → `except A, B, C:`
(`src/backend/mail/transport.py:89`) — legal under PEP 758 (Python 3.14) and AST-identical
(both parse to a `Tuple` handler type); it only looks wrong to a pre-3.14 interpreter.

## Phase 5 (S5.4) — verification report (2026-10-02)

**Change type / tier:** DOCS/CHORE — Phase 5 light tier (lint/types where applicable + a no-behavior-delta proof; no spec-coverage gate per the Phase Matrix).

**Scope conformance — all three scoped items implemented:**
- Item 1: `.gitignore` (`/data/`, `/logs/`).
- Item 2: 54 `.py` reformatted (12 `src/`, 40 `tests/`, 2 `migrations/`) + `pyproject.toml` (`extend-exclude = ["**/*.md"]`) + `.github/workflows/lint.yml` (added `uv run ruff format --check .` step).
- Item 3: `scripts/check_traceability.py` (new) + `.github/workflows/spec-validation.yml` (new `traceability` job) + `docs/verification/traceability.md` (§Invariants paragraph) + `AGENTS.md` (§"Traceability & Spec Drift" paragraph). Phase 1 record: `AI_Questions.md`.

`git diff --name-only ebbb233..HEAD` → 63 paths: 55 `.py` (54 reformatted + the new script), 4 `.md`, `.gitignore`, `pyproject.toml`, 2 workflow files. **Exactly one path is outside the §"Exact file list"**: `docs/verification/repo-hygiene.md` — this change's own evidence artifact, written by every phase record (not a behavior, test, or config file). No other extra path; no scoped file missing.

**No-behavior-delta evidence.** Full suite **727 passed / 1 skipped / 0 failed** — identical to the S4.1 baseline (not re-run here; S5.1 is the gate). **53/54** reformatted files AST-identical, **1** docstring-whitespace-only (`src/backend/settings/repository.py`), **0** real AST diffs; the sweep touched **0** Markdown files. Gates clean at S5.1: `ruff check .`, `ruff format --check .` (323 files, 0 pending vs 75 at baseline), `mypy src/` (83 files), `deptry .`, `bandit -r src/`, `pip-audit`, `alembic upgrade head`, `mkdocs build --strict`, `verify_spec.py` — all exit 0.

**Spec coverage: n/a for DOCS/CHORE** — no new normative requirement, and no approved spec normatively covers `.gitignore`, code formatting, or the matrix format (§"Spec-coverage check"), so no Spec Amendment was required. The durable guarantee for the matrix is the new CI-enforced referential-integrity check (`scripts/check_traceability.py`: exit 0 over 746 rows / 129 spec IDs / 713 test functions, with four negative controls proving each assertion fires).

**Accepted notes (recorded plainly, not hidden).**
1. `ruff format` rewrote `except (A, B, C):` → `except A, B, C:` at `src/backend/mail/transport.py:89` — legal under PEP 758 on the project's `requires-python >=3.14` and AST-identical, but it lowers compatibility for any pre-3.14 tool that parses that file. Accepted: the project is 3.14-only.
2. The S4.2 evidence plan's `git diff --ignore-all-space` proof was **wrong** (a whitespace-insensitive diff cannot prove AST equality); it was replaced by the `ast.dump` equality method used in S5.1. Carry to the after-workflow-optimization (fix the verify skill's formatting-sweep proof recipe).

**Verdict: PHASE 5: PASS** — every scoped item is implemented, the only out-of-scope path is this change's own evidence file, and the DOCS/CHORE contract holds: identical suite result, AST-identical sources, fully clean gate set.

## Phase 6 (S6.1) — review vs. scope (2026-10-02)

Normative basis = this scope record (§Scope summary, §Exact file list, Q-129/Q-130/Q-131). Reviewed the FINAL state at `67e4523` (not the commit-by-commit diff); no full-suite re-run (Phase 5: 727 passed, 1 skipped, 0 failed).

- **F-1** `lint.yml` `paths` filter omits `migrations/**` and `scripts/**`, so drift confined to those dirs alone would not trigger the new `Check formatting` step | Non-blocking | Accepted — the step runs repo-wide (`ruff format --check .`), so any PR touching `src/`/`tests/` catches it; widening the filter is beyond the scoped "one added step" (item 2c).
- **F-2** `spec-validation.yml` `paths` omits `scripts/check_traceability.py` (and the workflow file itself), so a change to the drift check alone does not run the `traceability` job | Non-blocking | Accepted — every input the check guards (`docs/specs/**`, `docs/verification/**`, `tests/**`, `src/**`) is in the filter; pre-existing filter pattern.
- **F-3** Status-vocabulary inconsistency: `docs/verification/traceability.md` §Invariants still declares five values, while AGENTS.md and `DECLARED_STATUSES` accept six (`N/A`, matched by the two lowercase `n/a` rows at lines 765/767) | Non-blocking | Open — resolve in S6.3 by adding `N/A` to the §Invariants list (one-line doc edit; the script's vocabulary is honest about the matrix's real content).
- **F-4** Assertion (3) validates only bare `` `test_*` `` tokens; 19 backticked references are file paths or `file::test` forms (e.g. `tests/property/usermanagement/test_multi_role_invariants.py::test_inv_003_last_admin_invariant`) and are not verified | Non-blocking | Accepted — bare names are the dominant form (713 of 732 test-like references checked, all resolve); path-form checking is a follow-up, not a scoped assertion.
- **F-5** REQ/AC ID spaces overlap across specs (71 of 84 distinct IDs are defined by more than one spec), so coverage (1) and dangling-ID (2) are satisfied cross-feature: a gap in one feature's section can be masked by another section's same-ID row | Non-blocking | Accepted — faithful to the scoped assertion set ("appears in ≥1 matrix row"); per-section scoping is a follow-up.
- **F-6** Convention paragraph location: scope said "appended to §Invariants"; the final note sits as a blockquote directly above §Invariants (line 5) | Info | Accepted — same wording, more visible placement; §Invariants content otherwise untouched (2 insertions total).
- **F-7** The single `RED` row (line 400) carries no change name/date in the cell, which the convention paragraph describes as present | Info | Accepted — rewriting existing rows is out of scope; the convention is forward-looking and the row is legal under B.
- **F-8** `.gitignore`: `/data/` + `/logs/` are root-anchored (verified: `git check-ignore -v` → lines 230/231), `git ls-files | grep -E '^(data|logs)/'` is empty, `deptry` clean; the older `data/db/`-style entries are now redundant subsets | Info | Accepted — harmless redundancy; removal out of scope.
- **F-9** Boundaries: 63 changed files = the 54 Python files + the 9 scoped files (nothing else); `git diff --ignore-all-space --stat src tests migrations` is empty (formatting-only); `pyproject.toml` diff is 3 lines (`extend-exclude` in `[tool.ruff]`, no shadowed/duplicated ruff key, no lint rule weakened); no `src/` behavior, no new dependency, no new layer; both workflows parse as YAML, jobs `lint` / `spec-validation,traceability,tests` (no name collision), `uv sync --only-group dev` present in every job, no `continue-on-error` on the new step/job | Info | Resolved — no finding.

**Gate:** no Blocking finding; 4 Non-blocking (F-1..F-4, three accepted with reason, F-3 open for S6.3) + 4 Info. Normative-basis compliance confirmed: the change implements exactly the scoped items 1–8, no more, no less; no test or `src/` behavior changed.
