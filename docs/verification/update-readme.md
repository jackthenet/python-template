# update-readme — Scope Record (DOCS/CHORE)

- **Change:** update-readme · **Type:** DOCS/CHORE — classified at **P.1**, first matching criterion #5 ("does not alter behavior: documentation, comments, configuration, CI, tooling"). Rationale: the diff is Markdown only (`README.md`, one new skill file, one line of `AGENTS.md`, this record); no `src/`, `tests/`, `docs/specs/`, `.github/workflows/` or config path is touched; no approved spec requires or describes `README.md` (P.2 overlap check: `grep -rn "README" docs/specs` → no match). Confirmed by the P.2 Classification verdict (`docs/questions/update-readme.md`, "Classification verdict").
- **Branch / worktree:** `chore/update-readme` @ base **`a274b6ac534fe8cd8085d00ec1e4c11784ec519e`** (== `main` at P.4), worktree `../python-template_kopie-worktrees/chore/update-readme` — created at **P.4** from `main` (git skill, "Create change worktree (P.4)"), so the branch carries the TODO file and the answered question file as of P.3.
- **Phase Matrix for this type:** Phase P → scope record (this file) · Phases 1–3 skipped · **Phase 4** make the change · **Phase 5** light gate · **Phase 6** light review + PR. No spec, no spec-approval PR, **no version bump** (AGENTS.md Versioning: `REFACTOR / DOCS-CHORE → none`).
- **Date:** 2026-10-04 (P.4 re-entry; supersedes the first P.4 draft — see Correction)

## Correction — this record replaces the first P.4 draft

The first P.4 execution (commit `5a59bc7`) was launched with an **incorrect answer set**: a 10-item "Q-1…Q-10" decision list that does not exist in `docs/questions/update-readme.md` (on disk there are exactly **6** questions, Q-1…Q-6, all `ANSWERED`). That draft therefore recorded scope that was never decided — a `.agents/skills/docs-as-code/SKILL.md`, a full new `AGENTS.md` "Documentation & traceability" section, an 11-row README feature table, a "Project layout" section and a "Status"/version block. **All of that is removed here.** This re-entry re-derives the scope from the authoritative on-disk planning records (`docs/todo/update-readme.md`, `docs/questions/update-readme.md`). The worktree and branch are unchanged; only this record file is rewritten.

## Phase P record

| Step | Date | Result |
|---|---|---|
| P.1 Frame (orchestrator, `main`) | 2026-10-03 | `docs/todo/update-readme.md` + `docs/questions/update-readme.md` created on `main`; type **DOCS/CHORE**; todo set created |
| P.2 Interrogate | 2026-10-04 | **DONE** — 6 questions needing user input (Q-1…Q-6, one `BLOCKED-USER` batch) + 12 interrogation points closed from repository evidence (E-1…E-12). DOCS/CHORE has no 20-question floor |
| P.3 Answer (orchestrator ⏸, `main`) | 2026-10-04 | **3 rounds, all 6 ANSWERED** — question file `Status: ALL ANSWERED` |
| P.4 Draft scope + create branch/worktree | 2026-10-04 | worktree + branch created from `main` at `a274b6a`; first draft `5a59bc7` **replaced by this record** (see Correction); every fact below re-verified in this worktree |
| P.5 Self-consistency | n/a | DOCS/CHORE — P.5 runs for FEATURE/CROSS-CUTTING only (AGENTS.md, Phase P table) |

## Answers this scope is built from (traceability)

| Q | Answer (recorded) | Where it lands in this scope |
|---|---|---|
| Q-1 | **(a) Both** — the skill file **and** the `README.md` rewrite, one change | Scope items 1 + 2 |
| Q-2 | **(a)** land now, **no License badge**; `security-changelog-license` adds it later | Badge deny-list; `## License` section skipped |
| Q-3 | **(d)** Codecov is a **separate change** (`codecov-coverage-badge`) → **no coverage badge here** | Badge deny-list; out-of-scope list |
| Q-4 | **(b)** trim the `Structure` tree → short summary + relative link to `AGENTS.md` "Project Structure" | Scope item 3 |
| Q-5 | **(b)** verbatim skill body **+ a 2–3 line "Repo protocol" note** | Scope item 1 |
| Q-6 | **(b)** **one line** in `AGENTS.md` — a "non-phase skills" note naming the skill | Scope item 4 |

## Scope — the exact non-behavior change

| # | Action | Path | Kind |
|---|---|---|---|
| 1 | New file | `.agents/skills/update-readme/SKILL.md` | agent tooling (guidance, not runtime code) |
| 2 | Rewrite in place (35 lines → ~70 lines) | `README.md` | documentation |
| 3 | Insert **one line** | `AGENTS.md` (after the Skill-to-Phase Mapping table, `AGENTS.md:319`) | documentation |
| 4 | Evidence record (this file) | `docs/verification/update-readme.md` | documentation |

**Nothing else.** No `src/`, `tests/`, `docs/specs/`, `userdocs/`, `mkdocs.yml`, `pyproject.toml`, `.github/`, `alembic.ini`, `migrations/`, `.pre-commit-config.yaml` or any other config path.

---

## Item 1 — `.agents/skills/update-readme/SKILL.md` (Q-1 = (a), Q-5 = (b))

**Body = the verbatim instruction set recorded at `docs/todo/update-readme.md:28-70`** ("verbatim, no editorial rewrite", `:77`; "the skill file is committed as supplied", `:100`). P.2 E-5 verified the text is recoverable from that fenced block — the five sections are `### 1. Inspect first (don't guess)`, `### 2. Badges`, `### 3. Structure and content`, `### 4. Quality rules`, `### 5. Output`. No re-paste from the user is needed and no wording may be rewritten.

**Front matter (verified against all 8 existing skills).** Every `.agents/skills/*/SKILL.md` has YAML front matter with **exactly two keys, `name:` and `description:`** — no `version`, `license`, `allowed-tools` or any other key anywhere; `name` is lowercase/hyphenated (`python-best-practices`); `description` is one string ending in a "Use when …" trigger clause. Bodies open with one `# Title` and use free-form `##` sections (no shared section contract). Length 45–229 lines, so a ~55-line skill is normal. Skills are auto-discovered — **no manifest, no registration, no CI/script check** (`grep -rn "skills" scripts/*.py` → no match; no workflow has a skills step), so nothing else must change for it to load (E-7).

Planned file:

```text
---
name: update-readme
description: "Updates the project's README.md to current GitHub front-page practice:
  inspect the repo first (README, pyproject.toml, LICENSE, .github/workflows/, git
  remote), add a badge row only for things that really exist, lay the page out in the
  8-section order skipping what does not apply, keep every command copy-pasteable and
  every relative link resolving, and report what changed plus anything unverifiable.
  Use when README.md needs a refresh, when a badge or command in it is stale or wrong,
  and when a new tool, workflow or feature must become visible on the front page."
---
# Task: Update the GitHub README          ← verbatim from docs/todo/update-readme.md:29
   (intro line + sections 1–5, transcribed unchanged)
## Repo protocol                          ← the ONLY addition (Q-5 = (b)), 2–3 lines
```

**"Repo protocol" note (2–3 lines, Q-5 = (b)):** the edit happens in the **change worktree** and reaches `main` only through the **merged PR** (`README.md` may never be committed directly to `main`); "list what changed and flag anything you couldn't verify" is recorded in the change's **`docs/verification/<name>.md`**, not only in a chat reply. This is the reconciliation already written at `docs/todo/update-readme.md:71-74` (E-6: silence, not contradiction).

The skill is **agent guidance in Markdown**: never imported, never packaged, no runtime path reads it.

## Item 2 — `README.md` rewritten in place (Q-1 = (a))

### Current state and the stale lines being replaced (verified at `a274b6a`)

35 lines, four headings (`# python-template` `:1`, `## Setup` `:5`, `## Run` `:11`, `## Structure` `:17`), **zero badges, zero links, zero images**.

| # | Quoted current line(s) | What replaces it |
|---|---|---|
| R-1 | `:11` `## Run` and `:14` `uv run pytest` | `uv run pytest` is **accurate, so it is preserved** — moved into **Development** as one of the real check commands. `## Run` as a heading disappears because the repo has **no app run command**: `src/main.py` has no `__main__` guard and `pyproject.toml` declares no `[project.scripts]` (verified). The README must not invent one |
| R-2 | `:21` `scripts/      Utility scripts (verify_spec.py)` | The hand-drawn tree is deleted (R-4). The three real scripts — `check_traceability.py`, `validate_task_dag.py`, `verify_spec.py` — appear as commands in **Development** |
| R-3 | `:23` `  frontend/   Frontend features`, `:24` `    features/ Feature-based frontend code`, `:25` `    shared/   Shared frontend utilities`, `:27` `    features/ Feature-based backend code` | Deleted with the tree. There is **no `features/` level** and **no `src/frontend/` at all** (`git ls-files src/frontend` → **0 files**; `ls src` → `backend/`, `main.py`) |
| R-4 | the whole fenced tree `:19-35` | Replaced by the trimmed **`## Structure`** section (item 3, Q-4 = (b)) |
| R-5 | `:3` `Default template for Python projects.` | Kept as the one-sentence description under the badge row (matches `pyproject.toml:5` `description`) |
| R-6 | — (missing) | Badge row under the single H1 (below) |
| R-7 | — (missing) | Contributing → `AGENTS.md` + the worktree/PR rule. **No `CONTRIBUTING.md` is invented** (out of scope) |

### Badge row (directly under the single H1; Q-2 = (a), Q-3 = (d))

Written as consecutive lines in one paragraph (no blank lines between them) so it renders as a single row; every badge has alt text and a link. `owner/repo` = `jackthenet/python-template` (`git remote get-url origin` → `https://github.com/jackthenet/python-template`).

| Badge (alt text) | Image URL | Links to | Fact that justifies it |
|---|---|---|---|
| `Quality` | `https://github.com/jackthenet/python-template/actions/workflows/quality.yml/badge.svg` | `…/actions/workflows/quality.yml` | `.github/workflows/quality.yml:1` `name: Quality`; no path filter → runs on every PR/push to `main` |
| `Lint` | `…/actions/workflows/lint.yml/badge.svg` | `…/actions/workflows/lint.yml` | `.github/workflows/lint.yml:1` `name: Lint` |
| `Spec Validation` | `…/actions/workflows/spec-validation.yml/badge.svg` | `…/actions/workflows/spec-validation.yml` | `.github/workflows/spec-validation.yml:1` `name: Spec Validation` |
| `Python >=3.14` | `https://img.shields.io/badge/python-%3E%3D3.14-blue` | `pyproject.toml` (relative link) | `requires-python = ">=3.14"` (`pyproject.toml:7`) |
| `Ruff` | `https://img.shields.io/badge/lint-ruff-blue` | `https://docs.astral.sh/ruff/` | `ruff` is a dev dependency (`pyproject.toml` dev group) and the `lint` job runs `uv run ruff check .` |
| `uv` | `https://img.shields.io/badge/env-uv-blue` | `https://docs.astral.sh/uv/` | the whole toolchain runs through `uv` (AGENTS.md "Tooling & Execution Environment"; `[tool.uv]` at `pyproject.toml:75`) |
| `pre-commit` | `https://img.shields.io/badge/hooks-pre--commit-blue` | `https://pre-commit.com/` | `.pre-commit-config.yaml` exists; `pre-commit` is a dev dependency |

7 badges — inside the TODO's acceptance signal (4–7). **Deny-list (must not appear):** **License** — no `LICENSE` file (`ls LICENSE*` → none) and no `license` field in `pyproject.toml` (Q-2 = (a): `security-changelog-license` adds it later); **coverage/Codecov** — no coverage service exists (Q-3 = (d), owned by the separate `codecov-coverage-badge` change); **PyPI version/downloads** — not published, no publish workflow among the three files; **docs-site** badge — no deploy workflow, so there is no hosted URL. **Flag in the Phase 5/6 report** (unverifiable, per the procedure's §5): the *status colour* each workflow badge renders is GitHub run history, not observable offline; and `Lint` / `Spec Validation` are **path-filtered**, so their badge can read stale/"skipped" for a doc-only PR like this one (E-10).

### Section plan — the procedure's 8-section order, skipping what does not apply

1. `# python-template` (single H1) + badge row + the one-sentence description (R-5)
2. `## Why this exists` — 3–4 lines: what the template gives you (backend feature packages, the Spec-TDD workflow, the CI/tooling gates). **No feature table** — none was decided, and a hand-maintained per-feature index is exactly the drift pattern Q-4 = (b) rejects
3. `## Installation` — `uv sync` (preserves the existing `## Setup` content)
4. `## Quick start` — one verified, copy-pasteable example (below)
5. `## Configuration` — 3–4 lines: typed settings come from the shared settings registry; relative links to `docs/specs/settings.md` and `src/backend/settings/`; `log_level`/`log_file` from `docs/specs/logging.md`. Links, does not duplicate
6. `## Development` — the verified command list (below) + where each gate runs (local pre-commit, `Lint`, `Quality`, `Spec Validation`)
7. `## Structure` — trimmed per item 3 (Q-4 = (b)); existing heading preserved, tree deleted
8. `## Contributing` — `AGENTS.md` (the Spec-TDD workflow), change worktrees, PR-only-to-`main`. **No `CONTRIBUTING.md`**
9. `## License` — **skipped** (Q-2 = (a): no `LICENSE` file; the procedure's own "skip sections that don't apply" + "never invent" rule)

No table of contents (the result stays short — the procedure's own rule). Single H1, fenced blocks with language tags (`bash`, `python`, `text`), relative links only for in-repo paths.

### Verified command list (every command checked against `pyproject.toml`, `.github/workflows/*`, `scripts/`, `alembic.ini`)

| Command | Verified against |
|---|---|
| `uv sync` | `[tool.uv] default-groups = ["dev"]` (`pyproject.toml:75-77`) |
| `uv run pytest tests/` | `[tool.pytest.ini_options] testpaths = ["tests"]` (`pyproject.toml:207-209`); the `tests` job runs `uv run pytest tests/ -v` (`spec-validation.yml:82-87`) |
| `uv run pytest tests/acceptance/ -v` (likewise `integration/`, `contract/`, `property/`, `unit/`) | the five real test directories exist under `tests/` (AGENTS.md "Test Category Hierarchy") |
| `uv run pytest tests/ --cov --cov-report=xml` | the `coverage` job, `quality.yml:59`; `[tool.coverage.report] fail_under = 92` (`pyproject.toml:103-106`) |
| `uv run ruff check .` / `uv run ruff format .` | the `lint` job: `uv run ruff check .` + `uv run ruff format --check .` (`lint.yml`) |
| `uv run mypy src/` | the `type-check` job gate, `quality.yml:23` |
| `uv run ty check src/` | the informational step of the same job, `quality.yml:25` |
| `uv run deptry .` | the `dependencies` job gate, `quality.yml:94` |
| `uv run pip-audit` / `uv run bandit -r src/` | the `security` job, `quality.yml:41,43` |
| `uv run mkdocs build --strict` | the `docs` job gate, `quality.yml:109`; the `mkdocs-build` pre-push hook, `.pre-commit-config.yaml` |
| `uv run alembic upgrade head` / `uv run alembic revision -m "<description>"` | `alembic.ini:8` `script_location = %(here)s/migrations`; the `migrations` job gate, `quality.yml:127` |
| `uv run python scripts/check_traceability.py` | the `traceability` job, `spec-validation.yml:68` |
| `uv run python scripts/verify_spec.py docs/specs/<name>.md` | the `spec-validation` job loop, `spec-validation.yml:39-51` |
| `uv run python scripts/validate_task_dag.py .github/task-runner/tasks.json` | `spec-validation.yml:54` — **informational** there (`|| true`); the README says so rather than implying it gates |
| `uv run pre-commit install` | `pre-commit` dev dependency + `.pre-commit-config.yaml` |

**Not listed** (does not exist): any app/server/CLI run command (R-1), `make`/`tox`/`nox`/`poetry`/`pip install -e .`, a hosted docs-site URL (no deploy workflow), a coverage badge/upload, and `bump-my-version` as a `uv run` command (it is a standalone tool: `uv tool install bump-my-version`, AGENTS.md Versioning).

### Verified quick-start example (run in this worktree at `a274b6a`)

```python
from backend.usermanagement import SqliteUserRepository, UserCreate, UserManager

manager = UserManager(SqliteUserRepository("sqlite:///:memory:"))
user = manager.create_user(
    UserCreate(username="alice", email="alice@example.com", password="s3cret!x", roles=["user"])
)
assert manager.verify_password(user.id, "s3cret!x")
```

Output: `verify_password` returned `True` (`user.roles == ['user']`). Two facts the snippet must get right, both verified by running it: `UserCreate.roles` is a **non-empty list** (`src/backend/usermanagement/models.py:117`) — the singular `role=` in the AGENTS.md usage example is **stale**; and the default allowed role set is `["admin", "user"]` (`UserManager._validate_roles` → `InvalidRoleError` for `"member"`). The stale AGENTS.md example is **flagged in the report, not fixed here** (any `AGENTS.md` change beyond item 4 is out of scope).

## Item 3 — trim `README.md`'s `Structure` section (Q-4 = (b))

Delete the hand-drawn tree (`README.md:19-35`, including the wrong `features/` lines at `:24` and `:27`) and replace it with a 2–3 line summary plus a relative link:

- what lives where in one breath: `src/backend/<feature>/` holds the feature packages directly; `tests/` is split by category (`acceptance/`, `integration/`, `contract/`, `property/`, `unit/`); `docs/` is the internal process record and `userdocs/` is the published mkdocs site; `scripts/` holds the three spec/traceability checkers.
- then: the authoritative layout is **`AGENTS.md`, "Project Structure"** (`[AGENTS.md](AGENTS.md)` — the heading is at `AGENTS.md:1110`).

The tree is **not hand-corrected** — a hand-maintained copy is what drifted (E-2), and `AGENTS.md` already documents the layout (single source of truth). `structure-map` may deepen it later.

## Item 4 — one line in `AGENTS.md` (Q-6 = (b))

**Exact insertion point:** immediately after the last row of the **Skill-to-Phase Mapping** table — `AGENTS.md:319` (`| (cross-cutting) | \`git\` | all | Branch/worktree creation, PR creation, post-merge cleanup. |`) — as a standalone line under the table, before the blank line and `### Phase Execution (Atomic Steps, Synchronous Subagents)` at `AGENTS.md:321`. No existing line is edited.

**The line (one line, naming the skill):**

```markdown
Non-phase skills: `.agents/skills/update-readme/` (refresh `README.md` to current GitHub front-page practice, badges backed only by facts that exist) maps to no workflow phase.
```

Nothing else in `AGENTS.md` changes — no new section, no edit to the Skill-to-Phase table itself, and `python-best-practices` stays unlisted (its own precedent, `docs/todo/track-python-skill.md:28`).

## No-behavior-delta confirmation (re-verified in this worktree at `a274b6a`)

| # | Check | Command / evidence | Result |
|---|---|---|---|
| 1 | No Python is touched | the scope's file list is `.agents/skills/update-readme/SKILL.md`, `README.md`, `AGENTS.md`, `docs/verification/update-readme.md` | no `.py` path → ruff/mypy inputs unchanged |
| 2 | No test is touched | same | `tests/` untouched → pytest results cannot change |
| 3 | `README.md` has no consumer beyond package metadata | `grep -n "README" pyproject.toml` | `readme = "README.md"` (`pyproject.toml:6`) — metadata only; no code, script or test reads it |
| 4 | The mkdocs site does not read `README.md` or `AGENTS.md` | `mkdocs.yml:6` `docs_dir: userdocs`; `ls userdocs` | the site is `userdocs/` only → site content unchanged |
| 5 | No skill is loaded by runtime code | `grep -rn "skills" scripts/*.py .github/workflows` | no match — skills are harness-side guidance |
| 6 | Baseline lint | `uv run ruff check .` | **All checks passed!** |
| 7 | Baseline traceability | `uv run python scripts/check_traceability.py` | **PASS (747 matrix rows, 129 spec IDs, 714 test functions)** |
| 8 | The quick-start snippet really runs | `uv run python -c "…"` (the snippet above) | **runs, `verify_password` → `True`** |
| 9 | Markdown whitespace rules | `.pre-commit-config.yaml:19-20` (`trailing-whitespace`, `end-of-file-fixer`) vs `.editorconfig` (`trim_trailing_whitespace = false` for `*.md`) | the hooks do **not** read `.editorconfig` → the new Markdown must not rely on two-space hard line breaks and must end with a final newline |

**Conclusion: no externally observable behavior change.** Documentation plus agent guidance; no runtime, build, packaging, CI, migration or test path is touched.

## Out of scope (explicit)

- **No `LICENSE`** file and **no License badge / `## License` section** — owned by `security-changelog-license` (Q-2 = (a)).
- **No `CONTRIBUTING.md`**, no PyPI publish workflow, no release workflow.
- **No coverage/Codecov badge and no coverage-upload step** — owned by the separate `codecov-coverage-badge` change (Q-3 = (d)).
- **No `userdocs/` change and no `mkdocs.yml` change** — the docs site is not touched by this change.
- **No `docs/specs/` change** (no new spec, no spec amendment — that is a separate PR by rule).
- **No `src/`, `tests/`, `.github/workflows/`, `pyproject.toml`, `alembic.ini`, `migrations/`, `.pre-commit-config.yaml`** or any other config file; no dependency added.
- **No `AGENTS.md` change beyond the one line** of item 4 — the Phase Matrix, Phase 5 items, atomic-step tables, Skill-to-Phase table rows and every other normative region stay untouched.
- No other skill file, no `docs/todo/` or `docs/questions/` edit (orchestrator-owned), no version bump.

## Phase 5 gate for this type (DOCS/CHORE — "Light: lint/types where applicable")

| Gate | Command | Applies? |
|---|---|---|
| Lint | `uv run ruff check .` (whole-repo sweep, once at Phase 5, matching `.github/workflows/lint.yml`) | yes — expected clean (baseline check 6). The `Lint` **workflow** is path-filtered to `src/**`, `tests/**`, `pyproject.toml`, `.pre-commit-config.yaml`, `.github/workflows/lint.yml`, `.github/hooks/**` (`lint.yml:6-21`), none of which this change touches → the ruff gate here is **local-only** |
| Docs build | `uv run mkdocs build --strict` | **`userdocs/` is NOT touched** (out of scope), so the pre-push `mkdocs-build` hook (`files: ^(mkdocs\.yml\|userdocs/\|pyproject\.toml)`) does **not** fire. Still run **once** at Phase 5 as cheap downstream evidence, because the `docs` job in `quality.yml` has **no path filter** and runs on this PR regardless |
| Types | `uv run mypy src/` | not applicable (no `.py` changed) — recorded as such rather than skipped silently |
| Traceability / spec drift | `uv run python scripts/check_traceability.py` | yes — and the `Spec Validation` workflow **does** run for this PR, because its path filter includes `docs/verification/**` (`spec-validation.yml:9`) and this change adds `docs/verification/update-readme.md` |
| Scope proof | `git diff --name-only main...HEAD` | must list **exactly** the four paths in the Scope table — **no `src/` or `tests/` path** |
| Full test suite | `uv run pytest tests/` | not a DOCS/CHORE gate; run only if the scope proof shows an unexpected path |

## Version bump

**None.** AGENTS.md Versioning: `REFACTOR / DOCS-CHORE → none`. No `bump-my-version` commit in Phase 6. Note for the record: `pyproject.toml:4` is **`0.6.1`** at this base — the TODO's "`version = "0.6.0"`" fact (`docs/todo/update-readme.md:96`) is stale; the bump decision is unaffected.

## Conflict note — `AGENTS.md` is also edited by open PRs

- **PR #65** (`chore/architecture-tests-missing`, **OPEN**) edits `AGENTS.md` in two places: the Phase Matrix **"5 Verify"** REFACTOR cell (`AGENTS.md:212`) and **Phase 5 REFACTOR item 13** (`AGENTS.md:579`) — verified with `git diff main...chore/architecture-tests-missing -- AGENTS.md`.
- **PR #64** (`chore/workflow-docs-nits`, **OPEN**) is the specify-skill / `docs/todo/template.md` change; verified with `git diff main...chore/workflow-docs-nits --stat` that it touches `.agents/skills/specify/SKILL.md`, `docs/todo/template.md` and `docs/verification/workflow-docs-nits.md` — **not `AGENTS.md`**. So the only live `AGENTS.md` collision is PR #65.
- This change adds **one line at `AGENTS.md:~320`** and edits **no existing line**; PR #65's two edits are at `:212` and `:579` → **no textual overlap; GitHub merges automatically**. If a conflict ever appears (e.g. `value-triage-gate` / `spec-interview-protocol` land their `AGENTS.md` edits first, as the Q-6 answer anticipates), the resolution is **take both**, and **whoever lands second re-reads `AGENTS.md` before editing** — no `Depends on:` is added.

## For Phase 4 (what the scoped edit must produce)

1. `.agents/skills/update-readme/SKILL.md` — the verbatim body from `docs/todo/update-readme.md:28-70` + two-key front matter + the 2–3 line "Repo protocol" note (item 1). No other wording change.
2. `README.md` — single H1, the 7-badge row from the allow-list, the 8-section plan above (License skipped), the verified command list, the verified quick-start snippet, the trimmed `## Structure` with a relative link to `AGENTS.md`, fenced blocks with language tags, no TOC, no invented URL/badge/run command.
3. `AGENTS.md` — the one line after `AGENTS.md:319`; nothing else.
4. Every claim the README makes must be backed by a row above; anything unverifiable (badge status colours, the path-filtered `Lint`/`Spec Validation` badges on a doc-only PR) is listed in the Phase 5/6 report instead of printed in the README — the procedure's own §5 rule.
