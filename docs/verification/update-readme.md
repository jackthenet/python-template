# update-readme — Scope Record (DOCS/CHORE)

- **Change:** update-readme · **Type:** DOCS/CHORE (classified at P.1, first matching criterion #5: "does not alter behavior — documentation, comments, configuration, CI, tooling")
- **Branch / worktree:** `chore/update-readme` @ base **`a274b6ac534fe8cd8085d00ec1e4c11784ec519e`** (== `main` at P.4), worktree `../python-template_kopie-worktrees/chore/update-readme` — created at **P.4** from `main` (git skill, "Create change worktree (P.4)"), so the branch carries the TODO file and the answered question file as of P.3. `pyproject.toml:4` version at base: **`0.6.1`**.
- **Phase Matrix for this type:** Phase P → scope record (this file) · Phases 1–3 skipped · **Phase 4** make the change · **Phase 5** light gate (scope proof + lint/types where applicable) · **Phase 6** light review + PR. No spec, no spec-approval PR, **no version bump** (AGENTS.md Versioning: `REFACTOR / DOCS-CHORE → none`).
- **Date:** 2026-10-04

## Phase P record

| Step | Date | Result |
|---|---|---|
| P.1 Frame (orchestrator, `main`) | 2026-10-03 | `docs/todo/update-readme.md` + `docs/questions/update-readme.md` created on `main`; type **DOCS/CHORE**; todo set created |
| P.2 Interrogate | 2026-10-04 | **DONE** — 6 questions needing user input (Q-1…Q-6, one `BLOCKED-USER` batch) + 12 interrogation points closed from repository evidence (E-1…E-12). DOCS/CHORE has no 20-question floor |
| P.3 Answer (orchestrator ⏸, `main`) | 2026-10-04 | **3 rounds, all 6 ANSWERED** — question file `Status: ALL ANSWERED` |
| P.4 Draft scope + create branch/worktree | 2026-10-04 | **this file** — worktree + branch created from `main` at `a274b6a`, scope recorded, every command and fact re-verified in this worktree (below) |
| P.5 Self-consistency | n/a | DOCS/CHORE — P.5 runs for FEATURE/CROSS-CUTTING only (AGENTS.md, Phase P table) |

## Divergence from the on-disk planning records (flagged for the orchestrator; not re-decided here)

The P.4 task-definition carries a **10-answer decision set (Q-1…Q-10)** that is broader than the 6 answers recorded in `docs/questions/update-readme.md`. The scope below follows the **task-definition** (it is the authoritative launch prompt and says "already decided — do not re-decide"). The differences, which only the orchestrator may reconcile (it owns `docs/todo/` and `docs/questions/`; this subagent must not edit them):

| Item | On-disk record (`docs/todo` + `docs/questions/update-readme.md`) | P.4 task-definition (followed here) |
|---|---|---|
| New skill | `.agents/skills/update-readme/SKILL.md`, body = the verbatim README-refresh procedure recorded at `docs/todo/update-readme.md:28-70` ("verbatim, no editorial rewrite", `:100`) | **`.agents/skills/docs-as-code/SKILL.md`**, scope = create/update a spec, keep the traceability matrix, spec-drift checks (Q-4, Q-5) |
| `AGENTS.md` | "one line … a 'non-phase skills' note naming `.agents/skills/update-readme/`" (Q-6 = (b)) | a full new **"Documentation & traceability"** section (Q-6) — which also carries the skill pointer, so the discoverability intent of the on-disk Q-6 is still satisfied |
| README content | badge row + the skill's 8-section order; `Structure` trimmed to a summary + link (Q-4 = (b)) | map + entry point (Q-1), **feature table as the maintenance point** (Q-2), link to the mkdocs site rather than duplicate it (Q-3), actual commands (Q-7), project layout (Q-8), status/version + quick-start (Q-9), CI badges/quality gates where they really exist (Q-10) |
| Version at base | `0.6.0` (`docs/todo/update-readme.md:96`) | **`0.6.1`** (`pyproject.toml:4` at `a274b6a`) — the TODO fact is stale; bump is still **none** |

What is **unchanged** between the two records and therefore applied as decided: no License badge (no `LICENSE` file), **no coverage badge** (Codecov is the separate `codecov-coverage-badge` change), no `Depends on:` on `security-changelog-license`, the skill carries a short "Repo protocol" note, and the README keeps a single H1 with fenced, copy-pasteable commands and relative links only.

---

## Scope — the exact non-behavior change

| # | Action | Path | Kind |
|---|---|---|---|
| 1 | Rewrite in place (35 lines → ~90 lines) | `README.md` | documentation |
| 2 | New file | `.agents/skills/docs-as-code/SKILL.md` | agent tooling (guidance, not runtime code) |
| 3 | Insert one new section | `AGENTS.md` (new `## Documentation & traceability`, inserted after `## Traceability & Spec Drift`, i.e. after `AGENTS.md:729`, before `## General Code & Style Conventions` at `:730`) | documentation |
| 4 | Evidence record (this file) | `docs/verification/update-readme.md` | documentation |

**Nothing else.** No `src/`, `tests/`, `docs/specs/`, `userdocs/`, `mkdocs.yml`, `pyproject.toml`, `.github/`, `alembic.ini`, `migrations/` or any config path.

## Current README state — what is stale or missing (verified at `a274b6a`)

`README.md` is 35 lines, four headings (`# python-template` `:1`, `## Setup` `:5`, `## Run` `:11`, `## Structure` `:17`), **zero badges, zero links, zero images**.

| # | Stale / missing | Quoted current line(s) | What replaces it |
|---|---|---|---|
| S-1 | A `features/` level that does not exist | `:24` `    features/ Feature-based frontend code` and `:27` `    features/ Feature-based backend code` | Deleted. `src/backend/` holds the feature packages **directly** (`authentication`, `eventbus`, `filemanagement`, `logging`, `mail`, `permissions`, `search`, `sessionmanagement`, `settings`, `shared`, `usermanagement`) — matching AGENTS.md "Project Structure" |
| S-2 | Documents a frontend that has no tracked files | `:23` `  frontend/   Frontend features`, `:25` `    shared/   Shared frontend utilities` | `git ls-files src/frontend` → **0 files**. The layout section states `src/frontend/` is an empty placeholder for the second runtime boundary (Q-8) — it is not deleted from the description, it is labelled honestly |
| S-3 | Incomplete `scripts/` list | `:21` `scripts/      Utility scripts (verify_spec.py)` | Three scripts exist: `check_traceability.py`, `validate_task_dag.py`, `verify_spec.py` — all three appear in the Development section with their real commands (Q-7) |
| S-4 | Root paths missing from the tree | the tree (`:19-35`) omits `userdocs/`, `migrations/`, `alembic.ini`, `.agents/`, `docs/` sub-structure | The hand-drawn tree is **replaced by a short prose summary + a relative link to `AGENTS.md` "Project Structure"** (on-disk Q-4 = (b)) — the single source of truth, no hand-maintained drift |
| S-5 | `## Run` presents `uv run pytest` as the whole workflow | `:11` `## Run`, `:14` `uv run pytest` | Replaced by **Quick start** (Q-9) + **Development** (Q-7): the real command set, verified below. `src/main.py` has **no `__main__` guard** and `pyproject.toml` declares **no `[project.scripts]`**, so the README must **not** claim an app run command — it states that `src/main.py` is the composition root (wires the features) and there is no server/CLI entry point yet |
| S-6 | No status/version, no quick start | — | New **Status** block (Q-9): version `0.6.1` from `pyproject.toml:4`, `requires-python = ">=3.14"` (`pyproject.toml:7`), "in-process backend features, no HTTP layer", `src/frontend/` empty |
| S-7 | No feature list, no link to any spec | — | New **Features** table (Q-2, the maintenance point) — content below |
| S-8 | No link to the published docs site | — | New line linking `mkdocs.yml` + `userdocs/` and the build command (Q-3). **No site URL** — there is no deploy/publish workflow in `.github/workflows/`, so the site is built, not hosted; a URL would be an invented badge-equivalent |
| S-9 | No CI status, no quality gates | — | Badge row under the single H1 (Q-10) — allow-list below |
| S-10 | No Contributing / process entry point | — | New **Contributing** section linking `AGENTS.md` (the Spec-TDD workflow) and `docs/`. **No `CONTRIBUTING.md`** is invented |
| S-11 | No License section | — | **Omitted, and flagged in the report**: no `LICENSE` file exists (`ls LICENSE*` → none) and `pyproject.toml` has no `license` field. Adding one is `security-changelog-license`'s change (on-disk Q-2 = (a)) |

### Features absent from the README today (verified against `src/backend/` and `docs/specs/`)

`search`, `permissions` (RBAC roles + grants), `sessionmanagement`, and the two cross-cutting coverage specs (`logging-coverage`, `settings-coverage`) are entirely absent; `usermanagement`'s roles and `permissions`' roles are the "roles" the task list names. Two names in the task list are **not** features and must not be invented as rows: there is **no `groups` feature** (`grep -rln "groups" src/backend/*/` → no match; roles are the only grouping concept, in `usermanagement` + `permissions`), and **profiling is not a feature** — it is the logging feature's `profiling_include_arguments` setting plus the `py-spy` dev dependency.

## README target — outline and content

Section order follows the recorded procedure (`docs/todo/update-readme.md:49-58`), skipping what does not apply:

1. `# python-template` (single H1) + badge row + one-sentence description
2. `## Status` — version, Python, what the project is (Q-9)
3. `## Features` — the maintenance-point table (Q-2)
4. `## Installation` — `uv sync`
5. `## Quick start` — one minimal, copy-pasteable, verified example (Q-9)
6. `## Configuration` — the settings feature, 4 lines + spec link
7. `## Documentation` — the mkdocs site: `userdocs/` is the source, `docs/` is the internal process record, build command (Q-3)
8. `## Development` — the verified command list (Q-7) + the quality gates and where they run (Q-10)
9. `## Project layout` — short summary + relative link to `AGENTS.md` "Project Structure" (Q-8, on-disk Q-4 = (b))
10. `## Contributing` — the Spec-TDD workflow, `AGENTS.md`, PR-only-to-`main`, worktrees
11. `## License` — **omitted** (S-11)

No table of contents (the result stays short — the procedure's own rule).

### Feature table content (each row verified: package exists in `src/backend/`, spec file exists in `docs/specs/`)

| Feature | Purpose (one line) | Spec |
|---|---|---|
| `authentication` | Password or passkey login, opaque server-side sessions, password recovery. | `docs/specs/authentication.md` |
| `eventbus` | In-memory async pub/sub so features communicate without importing each other. | `docs/specs/event-bus.md` |
| `filemanagement` | User-file storage: validation, atomic writes, avatars and variants. | `docs/specs/file-management.md` |
| `logging` | loguru sinks plus the `@logged` / `@logged_class` tracing decorators. | `docs/specs/logging.md` (+ `docs/specs/logging-coverage.md`) |
| `mail` | SMTP email sending with typed templates, password-reset and verification sends. | `docs/specs/mail-service.md` |
| `permissions` | RBAC: roles, dynamic grants over `feature.action` permissions, fail-closed checks. | `docs/specs/user-roles-permissions.md` |
| `search` | One query entry point over feature-registered sources (free text, filters, sort, pagination). | `docs/specs/search.md` |
| `sessionmanagement` | List and revoke a user's sessions, expiry cleanup, per-user session cap. | `docs/specs/session-management.md` |
| `settings` | Typed, validated settings registry with templates and YAML persistence. | `docs/specs/settings.md` (+ `docs/specs/settings-coverage.md`) |
| `usermanagement` | User account records, argon2id password hashing, roles, activation. | `docs/specs/user-management.md` |
| `shared` | Deliberately small shared code (`principal.py`): the `Principal` / `PermissionChecker` enforcement plumbing. | no spec — see `AGENTS.md` "Project Structure" |

### Verified command list (every command checked against `pyproject.toml`, `.github/workflows/*`, `scripts/`, `alembic.ini`, `mkdocs.yml`)

| Command | Verified against |
|---|---|
| `uv sync` | the standard uv workflow; `[tool.uv] default-groups = ["dev"]` (`pyproject.toml:77`) |
| `uv run pytest tests/` | `[tool.pytest.ini_options] testpaths = ["tests"]`; the `tests` job of `spec-validation.yml` |
| `uv run pytest tests/acceptance/ -v` / `tests/integration/` / `tests/contract/` / `tests/property/` / `tests/unit/` | the five real test directories (AGENTS.md "Test Category Hierarchy") |
| `uv run pytest tests/ --cov --cov-report=xml` | the `coverage` job, `quality.yml`; `[tool.coverage.report] fail_under = 92` |
| `uv run ruff check .` / `uv run ruff format .` | the `lint` job, `lint.yml` (`ruff check .` + `ruff format --check .`) |
| `uv run mypy src/` | the `type-check` job gate, `quality.yml` |
| `uv run ty check src/` | the informational step of the same job |
| `uv run deptry .` | the `dependencies` job gate, `quality.yml` |
| `uv run pip-audit` / `uv run bandit -r src/` | the `security` job, `quality.yml` |
| `uv run mkdocs build --strict` | the `docs` job gate, `quality.yml`; the `mkdocs-build` pre-push hook, `.pre-commit-config.yaml` |
| `uv run alembic upgrade head` / `uv run alembic revision -m "<description>"` | `alembic.ini` (`script_location = %(here)s/migrations`) + the `migrations` job, `quality.yml` |
| `uv run python scripts/check_traceability.py` | the `traceability` job, `spec-validation.yml` |
| `uv run python scripts/verify_spec.py docs/specs/<name>.md` | the `spec-validation` job, `spec-validation.yml` |
| `uv run python scripts/validate_task_dag.py .github/task-runner/tasks.json` | the `spec-validation` job, `spec-validation.yml` |
| `uv run pre-commit install` | `pre-commit` is a dev dependency; `.pre-commit-config.yaml` exists |
| `bump-my-version bump <level>` | AGENTS.md Versioning (`uv tool install bump-my-version`, **not** a project dependency) — listed in Contributing, marked as a standalone tool |

**Not listed** (does not exist): any app/server/CLI run command (S-5), `make`, `tox`, `nox`, `poetry`, `pip install -e .`, a docs `serve` deploy URL, `uv run complexipy` as a standalone gate (complexipy runs only as a pre-commit hook).

### Badge allow-list (Q-10 — only badges backed by something that exists)

| Badge | Fact behind it |
|---|---|
| `Quality` workflow status | `.github/workflows/quality.yml` (`name: Quality`), no path filter → runs on every PR/push to `main` |
| `Spec Validation` workflow status | `.github/workflows/spec-validation.yml` (`name: Spec Validation`) |
| `Lint` workflow status | `.github/workflows/lint.yml` (`name: Lint`) |
| Python `3.14` | `requires-python = ">=3.14"` (`pyproject.toml:7`) |
| Ruff / uv / pre-commit | declared dev dependencies + `.pre-commit-config.yaml` |

`owner/repo` = `jackthenet/python-template` (`git remote get-url origin`). **Deny-list (must not appear):** License (no `LICENSE` file), PyPI version/downloads (no publish workflow, not published), **coverage** (no coverage service — owned by the separate `codecov-coverage-badge` change), any "docs site" badge (no deploy workflow). **Flag in the report** (unverifiable offline): the *status colour* each workflow badge renders, and the fact that `Lint` and `Spec Validation` are **path-filtered**, so their badge can read stale/"skipped" for a doc-only PR like this one.

---

## New file — `.agents/skills/docs-as-code/SKILL.md` (Q-4, Q-5)

**Front-matter format (verified against all 8 existing skills).** Every `.agents/skills/*/SKILL.md` has YAML front-matter with **exactly two keys, `name:` and `description:`** — no `version`, `license`, `allowed-tools` or any other key anywhere. `name` is lowercase and hyphenated (`python-best-practices`); `description` is a single long string, quoted in `git`/`specify` and unquoted in the other six, and always ends with a "Use when …" trigger clause. Bodies open with one `# Title` and use free-form `##` sections (there is **no shared section contract**: `git` uses When to Use / Execution Context / Conventions / Todo / Atomic Steps / Operations / Edge Cases / Rules; `python-best-practices` uses Core rules / References / Verify before finishing). Length 45–229 lines, so a ~60-line skill is normal. Skills are auto-discovered — **no manifest, no registration, no CI/script check** exists (`grep -rn "skills" scripts/*.py` → no match; no workflow has a skills step), so nothing else must change for the skill to load.

Planned file (outline, ~60 lines):

```text
---
name: docs-as-code
description: "Keeps the documentation layer in sync with the code: create or update a
  feature specification in docs/specs/ from docs/specs/template.md with stable REQ/AC/
  INV/EDGE/NFR IDs, keep the traceability matrix in docs/verification/traceability.md,
  and run the spec-drift checks (scripts/check_traceability.py, verify_spec.py,
  validate_task_dag.py). Use when a feature is added or changed and its spec, matrix
  rows or docs links must follow, when a spec-drift or traceability finding appears,
  and when the README feature table or the docs site links must be kept current."
---
# Docs as Code
## Purpose          — docs are part of the change, not a follow-up: spec → matrix → site/README links move together
## When to Use      — new/changed feature behavior, a spec-drift finding, a broken matrix row, a new feature package
## Inputs           — docs/specs/template.md, the existing docs/specs/*.md, docs/verification/traceability.md,
                     src/backend/<feature>/, the change's docs/verification/<name>.md
## Procedure
  1. Inspect first: read the spec(s), the matrix rows for the touched IDs, and the feature package.
  2. Create/update the spec from docs/specs/template.md; assign stable IDs (REQ/AC/INV/EDGE/NFR);
     an approved spec is edited ONLY through the Spec Amendment Workflow (new PR + Changelog entry).
  3. Keep the matrix: add/update a row for every ID the change actually touches; never refresh rows
     it did not touch (a dated RED/PENDING row is a legal historical record).
  4. Spec-drift checks: uv run python scripts/check_traceability.py (referential integrity),
     uv run python scripts/verify_spec.py docs/specs/<name>.md,
     uv run python scripts/validate_task_dag.py .github/task-runner/tasks.json.
  5. Keep the map honest: README feature table row + docs/specs link, and userdocs/ only when the
     published API surface changed (the site source is userdocs/, never docs/).
## Constraints      — no direct edit of an approved spec on main; tests are the contract (a conflicting
                     spec wording is resolved by amending the spec, never by weakening a test);
                     CI checks referential integrity, not status freshness; docs/ is the internal process
                     record and is never the published site
## Output           — the spec file, the matrix rows, and a short "what changed / what could not be
                     verified" list recorded in the change's docs/verification/<name>.md
## Repo protocol    — 2–3 lines (on-disk Q-5 = (b)): the edit happens in the change worktree and reaches
                     main only through the merged PR; the report is the evidence file, not a chat reply
```

The skill is **agent guidance in Markdown**: it is never imported, never packaged (`ruff` excludes `**/*.md`, `pyproject.toml:165`), and no runtime path reads it.

## `AGENTS.md` — new "Documentation & traceability" section (Q-6)

**Insertion point (verified):** a new `## Documentation & traceability` block inserted immediately **before `## General Code & Style Conventions` (`AGENTS.md:730`)**, i.e. after the `---` at `AGENTS.md:728` that closes `## Traceability & Spec Drift` (`:718`). It is a **new section between two existing ones** — no existing line is edited.

Content (what it says, ~10 bullets):

- **Where each kind of doc lives** — `docs/specs/` (normative, the only place behavior is defined), `docs/decisions/` (ADRs: why), `docs/tasks/` (task DAGs), `docs/verification/` (evidence + `traceability.md`), `docs/todo/` + `docs/questions/` (planning records, `main`-only, not normative), `userdocs/` (**the published mkdocs site** — `mkdocs.yml:6 docs_dir: userdocs`), `docs/` (**never** the site — internal process record), `README.md` (a **map + entry point**, not a manual).
- **The maintenance rule** — a new backend feature means: a spec from `docs/specs/template.md` with stable IDs, a feature-table row in `README.md` linking that spec, and matrix rows for its IDs. The README feature table is the index; the spec is the authority; the site is the published view.
- **The checks** — `uv run python scripts/check_traceability.py` (the `traceability` CI job), `uv run python scripts/verify_spec.py docs/specs/<name>.md`, `uv run python scripts/validate_task_dag.py .github/task-runner/tasks.json` (the `Spec Validation` workflow), and `uv run mkdocs build --strict` (the `docs` job gate + the `mkdocs-build` pre-push hook).
- **Drift policy** — pointer to the Spec Amendment Workflow and to "Tests are the contract"; approved specs are never edited directly on `main`.
- **The skill pointer** — one line naming `.agents/skills/docs-as-code/` as a **non-phase skill** (this also delivers the discoverability intent of the on-disk Q-6 = (b), following the `python-best-practices` precedent of a skill that is not in the Skill-to-Phase Mapping table).

## No-behavior-delta confirmation (re-verified in this worktree at `a274b6a`)

| # | Check | Command | Result |
|---|---|---|---|
| 1 | No Python is touched | the scope's file list is `README.md`, `.agents/skills/docs-as-code/SKILL.md`, `AGENTS.md`, `docs/verification/update-readme.md` | no `.py` path; `ruff`/`mypy` inputs are unchanged → **type check not applicable** (AGENTS.md Phase 5 item 16: "where applicable") |
| 2 | No test is touched | same | `tests/` untouched → pytest results cannot change |
| 3 | `README.md` has no consumer beyond package metadata | `grep -n "README" pyproject.toml` | `readme = "README.md"` (`pyproject.toml:6`) — metadata only; no code, script or test reads the file |
| 4 | The mkdocs site does not read `README.md` or `AGENTS.md` | `cat mkdocs.yml`; `ls userdocs` | `docs_dir: userdocs`; the site is `userdocs/index.md` + `userdocs/api.md` only → the site content is unchanged |
| 5 | No skill is loaded by runtime code | `grep -rn "skills" scripts/*.py .github/workflows` | no match — skills are harness-side guidance; adding one cannot alter behavior |
| 6 | Baseline: lint is clean before the change | `uv run ruff check .` | **All checks passed!** |
| 7 | Baseline: traceability is clean before the change | `uv run python scripts/check_traceability.py` | **PASS (747 matrix rows, 129 spec IDs, 714 test functions)** |
| 8 | The quick-start example really runs | `uv run python -c "import backend.usermanagement"` | **import ok** — `backend.*` is importable after `uv sync`, so the snippet is copy-pasteable |
| 9 | Markdown whitespace rules | `.pre-commit-config.yaml:19-20` (`trailing-whitespace`, `end-of-file-fixer`) vs `.editorconfig:9-10` (`trim_trailing_whitespace = false` for `*.md`) | the pre-commit hooks do **not** read `.editorconfig` → the new Markdown must not rely on two-space hard line breaks and must end with a final newline |

**Conclusion: no externally observable behavior change.** The change is documentation plus agent guidance; it touches no runtime, build, packaging, CI, migration or test path.

## Out of scope (explicit)

- **No `userdocs/` rewrite** and no `mkdocs.yml` change — the site is linked, not duplicated (Q-3).
- **No coverage/Codecov badge** and no coverage-upload step — owned by the separate `codecov-coverage-badge` change (on-disk Q-3 = (d)).
- **No `LICENSE`, `CONTRIBUTING.md`, or PyPI publish workflow** — owned by `security-changelog-license` / separate changes.
- **No new spec files** in `docs/specs/` and no edit of any approved spec (that would be a Spec Amendment PR, a different change).
- **No `AGENTS.md` workflow-phase change** — the Phase Matrix, Phase 5 items, atomic-step tables, Skill-to-Phase Mapping and every other normative workflow region stay untouched; only the new section is added.
- No `src/`, `tests/`, `pyproject.toml`, `.github/`, `alembic.ini`, `migrations/`, `.pre-commit-config.yaml` change; no dependency added; no version bump.

## Phase 5 gate for this type (DOCS/CHORE — "Light: lint/types where applicable")

| Gate | Command | Applies? |
|---|---|---|
| Docs build | `uv run mkdocs build --strict` | **`userdocs/` is NOT touched** (out of scope), so the pre-push `mkdocs-build` hook (`files: ^(mkdocs\.yml\|userdocs/\|pyproject\.toml)`) does **not** fire. It is still run **once** at Phase 5 as cheap downstream evidence, because the `docs` job in `quality.yml` has **no path filter** and runs on this PR regardless |
| Lint | `uv run ruff check .` (whole-repo sweep, once at Phase 5, matching `.github/workflows/lint.yml`) | yes — expected clean (baseline check 6). Note: the `Lint` **workflow** is path-filtered to `src/**`, `tests/**`, `pyproject.toml`, `.pre-commit-config.yaml`, `.github/workflows/lint.yml`, `.github/hooks/**`, none of which this change touches → the ruff gate here is **local-only** |
| Types | `uv run mypy src/` | not applicable (no `.py` changed) — recorded as such rather than skipped silently |
| Traceability / spec drift | `uv run python scripts/check_traceability.py` | yes — and the `Spec Validation` workflow **does** run for this PR, because its path filter includes `docs/verification/**` (`spec-validation.yml:9`) and this change adds `docs/verification/update-readme.md` |
| Scope proof | `git diff --name-only main...HEAD` | must list **exactly** the four paths in the Scope table |
| Full test suite | `uv run pytest tests/` | not a DOCS/CHORE gate; run only if the scope proof shows an unexpected path |

## Version bump

**None.** AGENTS.md Versioning: `REFACTOR / DOCS-CHORE → none`. `pyproject.toml:4` stays at **`0.6.1`** (the TODO's `0.6.0` is stale — see the Divergence table). No `bump-my-version` commit in Phase 6.

## Conflict note — `AGENTS.md` and PR #65 (`chore/architecture-tests-missing`)

- PR #65 is **OPEN** (`gh pr view 65` → `state: OPEN`, head `chore/architecture-tests-missing`) and edits `AGENTS.md` in exactly two places: the **Phase Matrix "5 Verify" REFACTOR cell** (`AGENTS.md:212`) and **Phase 5 REFACTOR item 13** (`AGENTS.md:579`) — verified with `git diff main...chore/architecture-tests-missing -- AGENTS.md`.
- This change adds **one new section at `AGENTS.md:~729`** and edits **no existing line**. The two regions are ~500 lines apart → **no textual overlap; GitHub merges it automatically**.
- If a conflict does appear (e.g. another change rewrites the same region), the resolution is **take both**: keep PR #65's wording in the Phase Matrix cell and Phase 5 item 13, keep this change's new section verbatim; whoever lands second re-reads `AGENTS.md` and rebases (the on-disk Q-6 answer already records this rule for `workflow-docs-nits` / `value-triage-gate` / `spec-interview-protocol`).
- Checked and clear: `chore/workflow-docs-nits` (PR #64, open) does **not** touch `AGENTS.md` at all (`git diff main...chore/workflow-docs-nits --stat` → `.agents/skills/specify/SKILL.md`, `docs/todo/template.md`, `docs/verification/workflow-docs-nits.md`). `chore/architecture-tests-missing` also edits three `src/backend/*/feature_settings.py` files — irrelevant to this diff, but a reason not to merge the two PRs out of order without a re-read.

## For Phase 4 (what the scoped edit must produce)

1. `README.md` rewritten per the outline above: single H1, badge row from the allow-list, Status block, the 11-row feature table with relative spec links that resolve, `uv sync`, one verified quick-start snippet, the Configuration and Documentation pointers, the verified Development commands, the trimmed layout summary + link to `AGENTS.md` "Project Structure", Contributing → `AGENTS.md`; **no** License section, **no** coverage badge, **no** invented URL or run command.
2. `.agents/skills/docs-as-code/SKILL.md` per the outline above (two-key front-matter).
3. `AGENTS.md`: the new `## Documentation & traceability` section inserted before `## General Code & Style Conventions`; no other line touched.
4. Every claim the README makes must be backed by a row in the tables above; anything unverifiable is listed in the Phase 5/6 report instead of printed in the README (the procedure's own quality rule, `docs/todo/update-readme.md:59-64`).
