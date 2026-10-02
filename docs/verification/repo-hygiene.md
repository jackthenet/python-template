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
