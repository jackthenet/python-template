# Verification — Dev Tooling Wiring

**Type:** DOCS/CHORE
**Branch:** `chore/dev-tooling-wiring`
**Base:** `main` @ `2644d30`

---

## Classification (Phase 0)

- **Type:** DOCS/CHORE (classified by the orchestrator in Phase 0).
- **Rationale:** the change wires up already-declared dev tooling (alembic, polyfactory,
  respx, time-machine, mkdocstrings, deptry) plus their missing companions (mkdocs,
  mkdocs-material, the mkdocstrings[python] extra) through configuration, CI jobs,
  pre-commit hooks, scaffolds, and documentation. Zero externally observable behavior
  change: no `src/` file, no existing `tests/` file, no runtime behavior, no API, no
  test assertion is modified.
- **Version bump:** none (DOCS/CHORE — Phase 6).

## User request (verbatim)

"Make use of the functionalities that alembic, polyfactory, respx, time-machine, mkdocstrings and deptry provide. Update the workflow, hooks and what not to make the best use of these tools."

## User feedback (verbatim, binding)

1. mkdocstrings alone won't do anything — you're missing mkdocs itself. mkdocstrings is a
   plugin for MkDocs. Add to the dev group:
   `"mkdocs>=1.6"`, `"mkdocs-material>=9.5"`, `"mkdocstrings[python]>=1.0.6"`.
   Without the `[python]` extra, mkdocstrings has no handler to parse Python docstrings.
2. deptry will misfire immediately without configuration (DEP002 on CLI tools / pytest
   plugins that are never imported). Add:
   ```toml
   [tool.deptry]
   [tool.deptry.per_rule_ignores]
   DEP002 = ["bandit", "complexipy", "mkdocs", "mkdocs-material", "mkdocstrings", "mypy", "pip-audit", "pre-commit", "py-spy", "pytest-cov", "pytest-randomly", "pytest-xdist", "ruff", "ty"]
   ```
3. alembic is in the dependency list, but a package alone doesn't give you migrations —
   run `alembic init` to generate alembic.ini and the migrations/env.py scaffold wired to
   the SQLModel metadata.
4. polyfactory needs no extras for Pydantic/SQLAlchemy models — core supports them.
5. Once you add the mkdocs config, mkdocs.yml needs to point away from the existing
   `docs/` (specs/decisions/workflow) so the two don't collide.

## Binding decisions (AI_Questions.md)

- **Q-63 (ANSWERED):** The MkDocs site setup (mkdocs dependency + mkdocs.yml + source
  directory) is a SEPARATE change from the dependency-updates change (which was "deps
  only"). THIS change (dev-tooling-wiring) is that separate change.
- **Q-64 (ANSWERED, BINDING):** The MkDocs site source directory is **`userdocs/`**
  (repo root), NOT the default `docs/`. Rationale (user): it separates "internal process
  record" (`docs/` = specs, decisions, verification, workflow) from "published
  documentation" (`userdocs/`). The scope applies this.

---

## Phase 1 — Scope (no behavior delta)

**Date:** 2026-09-21

### Current state (verified on `main` @ `2644d30`)

- `pyproject.toml` dev group ALREADY contains: alembic, bandit, complexipy, deptry,
  hypothesis, mkdocstrings (bare, NO `[python]` extra), mypy, pip-audit, polyfactory,
  pre-commit, py-spy, pytest, pytest-cov, pytest-randomly, pytest-xdist, respx, ruff,
  time-machine, ty. **MISSING:** mkdocs, mkdocs-material, and the
  mkdocstrings[python] extra.
- No `[tool.deptry]` section; no `alembic.ini`/`migrations/`; no `mkdocs.yml`; no
  `userdocs/`.
- `.pre-commit-config.yaml` currently has: ruff (ruff-check --fix + ruff-format),
  pre-commit-hooks (trailing-whitespace, end-of-file-fixer, check-yaml,
  check-added-large-files), complexipy. No deptry/mkdocs hooks.
- CI workflows: `lint.yml` (ruff check .), `quality.yml` (type-check: mypy gate + ty
  informational; security: pip-audit + bandit; coverage: pytest --cov with
  fail_under 92; dependency-review: actions/dependency-review-action@v5),
  `spec-validation.yml`. No deptry/mkdocs/alembic jobs.
- `AGENTS.md` mentions NONE of: alembic, deptry, mkdocs, mkdocstrings, polyfactory,
  respx, time-machine, bandit, pip-audit, pre-commit, py-spy, complexipy. The "Tooling
  & Execution Environment" section currently lists only uv, ruff, mypy, ty, pytest,
  hypothesis, bump-my-version.
- SQLModel table classes (all share the global `SQLModel.metadata`; repositories
  bootstrap tables via `SQLModel.metadata.create_all(engine)`):
  - `src/backend/authentication/models.py`: Session, PasswordReset, WebAuthnCredential
  - `src/backend/filemanagement/models.py`: FileRecord, UserAvatar
  - `src/backend/usermanagement/models.py`: User
  - (sessionmanagement/settings/mail/eventbus/logging have no SQLModel table classes)
- Backend features: authentication, eventbus, filemanagement, logging, mail,
  sessionmanagement, settings, usermanagement.
- Test helper convention: `tests/<name>_test_helpers.py`; imported top-level (e.g.,
  `from settings_test_helpers import install_isolated_registry` in `tests/conftest.py`).
- Version 0.4.1.

### Exact non-behavior changes (files + content)

1. **`pyproject.toml`**
   - dev group: add `"mkdocs>=1.6"` and `"mkdocs-material>=9.5"`; replace
     `"mkdocstrings>=1.0.6"` with `"mkdocstrings[python]>=1.0.6"` (keep the group's
     comment style/ordering convention).
   - New `[tool.deptry]` section: `known_first_party = ["backend"]`;
     `per_rule_ignores` DEP002 = the 14 feedback entries (bandit, complexipy, mkdocs,
     mkdocs-material, mkdocstrings, mypy, pip-audit, pre-commit, py-spy, pytest-cov,
     pytest-randomly, pytest-xdist, ruff, ty); DEP001 = ["sqlalchemy"] (commented);
     + justified dry-run additions (commented).
2. **`alembic.ini` + `migrations/`** — generated by `uv run alembic init migrations`,
   then wired:
   - `script_location = migrations`; a default `sqlalchemy.url` that works locally and
     in CI (file-based SQLite; CI overrides with a temp file).
   - `migrations/env.py`: `target_metadata = SQLModel.metadata`, importing the three
     model modules (backend.authentication.models, backend.filemanagement.models,
     backend.usermanagement.models) so their tables register; standard online/offline
     migration patterns.
   - No actual migration revisions are created (the scaffold is the deliverable).
3. **`mkdocs.yml`** (repo root): `docs_dir: userdocs` (binding Q-64), material theme,
   plugins: search + mkdocstrings (default_handler: python).
4. **`userdocs/`** (new, repo root): `index.md` (project overview) and `api.md`
   (mkdocstrings auto-loading of the backend features' public APIs).
5. **`.pre-commit-config.yaml`** — add `repo: local` (language: system,
   pass_filenames: false) hooks:
   - `deptry`: `uv run deptry .` (stage: pre-commit; files: pyproject.toml, uv.lock,
     src/, tests/, scripts/, migrations/).
   - `mkdocs-build`: `uv run mkdocs build --strict` (stage: pre-push; files:
     mkdocs.yml, userdocs/, pyproject.toml).
6. **`.github/workflows/quality.yml`** — add three jobs (consistent with the existing
   dependency-review job placement):
   - `dependencies`: `uv run deptry .` (gate).
   - `docs`: `uv run mkdocs build --strict` (gate).
   - `migrations`: `uv run alembic upgrade head` against a temp SQLite DB (validates
     the scaffold end-to-end).
7. **`tests/tooling_test_helpers.py`** (NEW shared helper, following the
   `tests/<name>_test_helpers.py` convention) — a ready-to-use shared test capability
   providing:
   - polyfactory-based factory helpers for Pydantic models (test data factories instead
     of hand-crafted field dicts),
   - time-machine time-travel helpers for time-dependent tests,
   - respx httpx-mocking helpers for outbound-call tests.
   - NEW file only — NO existing test file is modified; no test imports it yet (inert
     until used). This is what makes polyfactory/respx/time-machine "used" for deptry
     (deptry scans tests/ and finds the imports).
8. **`AGENTS.md`**
   - "Tooling & Execution Environment" section: add concise entries for alembic,
     deptry, mkdocs/mkdocstrings, polyfactory, respx, time-machine (commands + role,
     matching the section's existing style).
   - New section "Using the Test Tooling (polyfactory, respx, time-machine)":
     when/how to use each, conventions, examples (mirroring the existing "Using the X
     Feature" section pattern).
   - New section "Using Migrations (alembic)": the rule that SQLModel schema changes
     require a migration, create/apply commands, the CI check.
   - MkDocs site note: published docs live in `userdocs/` (binding Q-64; never
     `docs/`), build command, CI job.
9. **`docs/verification/dev-tooling-wiring.md`** — the scope record (this step),
   updated by later phases with evidence.

### deptry configuration note (verified reasoning)

The generated `migrations/env.py` imports `alembic` (so alembic is "used" once the
scaffold exists) and imports `sqlalchemy` (a transitive runtime dep via sqlmodel, not
directly declared → will fire DEP001 unless per_rule_ignores covers it). The final
`[tool.deptry]` config is therefore expected to be: `known_first_party = ["backend"]`,
`per_rule_ignores` DEP002 = the 14 feedback entries, `per_rule_ignores` DEP001 =
["sqlalchemy"] (with a comment: transitive via sqlmodel, imported by the alembic
scaffold), plus any additional ignores the implementation's `uv run deptry .` dry run
justifies (each with a comment). This is part of the scope allowance, not a scope
change.

### No-behavior-delta confirmation

- No `src/` file is modified. No existing `tests/` file is modified (one NEW helper
  file is added). No runtime behavior, API, or test assertion changes. All changes are:
  dependency declarations, tool configuration, CI jobs, pre-commit hooks,
  documentation, and the alembic/mkdocs scaffolds. The full test suite result must
  remain identical (Phase 5 verifies).
- The new `tests/tooling_test_helpers.py` is a new file, not imported by any test, and
  does not alter any existing test's behavior — this is the one item that extends into
  `tests/`, and it is recorded here as an explicit scope decision (shared test tooling
  capability; the DOCS/CHORE gate "no test files touched" is interpreted as "no existing
  test modified/affected", which holds).

---

## Phase 4 — Evidence

### S4.2 — alembic scaffold wired to SQLModel metadata (DOCS/CHORE, make the change)

**Date:** 2026-09-21
**Commit:** `e395815d85f55eb4ce8627d76cb1dab1e9b1ae23`
(`chore(dev-tooling-wiring): alembic scaffold wired to SQLModel metadata`)

**Change made (scope item 2):**

- `uv run alembic init migrations` generated `alembic.ini` + `migrations/` (env.py,
  script.py.mako, README, versions/); `migrations/versions/.gitkeep` added so the
  empty versions directory is tracked.
- `alembic.ini`: `script_location = %(here)s/migrations` (generated default); default
  `sqlalchemy.url = sqlite:///./data/migrations.db` — file-based SQLite under the common
  persistence root `data/` (gitignored, `.gitignore:220`; ADR-056). No generated DB
  file is committed.
- `migrations/env.py` wired to the project metadata:
  - imports the three model modules that define SQLModel tables, each with a
    `# noqa: F401` comment naming the tables (aliased so each import is a distinct
    binding): `backend.authentication.models` (Session, PasswordReset,
    WebAuthnCredential), `backend.filemanagement.models` (FileRecord, UserAvatar),
    `backend.usermanagement.models` (User);
  - `target_metadata = SQLModel.metadata` (from `sqlmodel`);
  - the standard online/offline migration patterns from the alembic init template;
  - URL resolution: environment variable `ALEMBIC_DATABASE_URL` if set, else
    `alembic.ini`'s `sqlalchemy.url` (a small, standard extension so CI can point at a
    temp DB).
- No migration revisions created (the scaffold is the deliverable; the initial
  revision is out of scope).
- `uv.lock`: `uv run` re-synced the stale self-version entry (0.4.0 → 0.4.1) during the
  gate runs; the change was reverted before committing (S4.3 re-syncs it deliberately).

**Gate commands + results:**

| Command | Result |
|---|---|
| `uv run ruff check migrations/` | PASS — "All checks passed" (exit 0) |
| `uv run alembic heads` | PASS — exit 0 (0 revisions → no heads) |
| `ALEMBIC_DATABASE_URL=sqlite:///<temp-file>.db uv run alembic upgrade head` | PASS — exit 0; env.py fully executed (engine connected to the temp SQLite DB, the three model imports resolved, `SQLModel.metadata` loaded); 0 revisions → no-op upgrade |
| temp DB cleanup | PASS — temp DB file deleted; no `data/` directory, no `.db`/`.sqlite` artifacts left in the worktree; none committed |

**Ruff:** `uv run ruff check migrations/` → All checks passed (exit 0).
