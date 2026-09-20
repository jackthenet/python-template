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

### S4.3 — deps + deptry config (mkdocs trio, [tool.deptry]) (DOCS/CHORE, make the change)

**Date:** 2026-09-21
**Commit:** `d615f4054ef663086b3defa8d8c2a2cded6cad28`
(`chore(dev-tooling-wiring): deps + deptry config (mkdocs trio, [tool.deptry])`)

**Change made (scope item 1):**

- `pyproject.toml` dev group: added `"mkdocs>=1.6"` and `"mkdocs-material>=9.5"`
  (alphabetical position, before mkdocstrings); replaced
  `"mkdocstrings>=1.0.6"` with `"mkdocstrings[python]>=1.0.6"`; the group's
  comment style/ordering preserved (new comments: MkDocs static site build
  system / MkDocs Material theme; mkdocstrings comment updated for the
  `[python]` extra).
- `pyproject.toml` new `[tool.deptry]` section (placed with the other
  `[tool.*]` sections, between `[tool.coverage.report]` and `[tool.mypy]`):
  - `known_first_party = ["backend"]` (the source is a `backend.*` namespace
    package under `src/`); `package_module_name_map = { "ruamel-yaml" = "ruamel" }`
    (the ruamel-yaml distribution is imported as the top-level module `ruamel`;
    justified dry-run addition).
  - `per_rule_ignores` (each entry commented):
    - `DEP002` = the 14 feedback entries (bandit, complexipy, mkdocs,
      mkdocs-material, mkdocstrings, mypy, pip-audit, pre-commit, py-spy,
      pytest-cov, pytest-randomly, pytest-xdist, ruff, ty) + `httpx`, `orjson`
      (declared runtime capabilities not yet imported from source).
    - `DEP001` = `webauthn` (optional production dependency: deferred-imported
      inside `PyWebAuthnProvider`, the fake provider is the test seam —
      documented design, ADR-031; intentionally not declared).
    - `DEP003` = `sqlalchemy` (transitive runtime dep via sqlmodel, directly
      imported by the repositories and the alembic scaffold `migrations/env.py`).
    - `DEP004` = `alembic` (the `migrations/` scaffold is tooling code that
      legitimately imports alembic, a dev dependency).
- `uv sync`: installed mkdocs, mkdocs-material, mkdocstrings[python] (+
  transitive deps: babel, backrefs, griffelib, paginate, mkdocs-material-
  extensions, mkdocstrings-python); `uv.lock` updated, including the stale
  self-version entry 0.4.0 → 0.4.1 (deliberately absorbed in this step).
- **Root-cause fix for a false-positive finding (1-line change, documented):**
  the unanchored `.gitignore` pattern `settings/` made deptry's
  gitignore-aware file finder exclude `src/backend/settings/` (and
  `tests/**/settings/`) from the scan, producing a false `DEP002 ruamel-yaml`
  finding (the dependency IS imported in `src/backend/settings/repository.py`).
  The pattern is now anchored to `/settings/` — the entry's stated intent
  (the repo-root test-run artifact directory of the default
  `YamlValueRepository('settings')`; the root artifact stays ignored; tracked
  files unaffected — no behavior delta). A `DEP002` ignore for ruamel-yaml was
  deliberately NOT added: it would have permanently masked the settings feature
  from the unused-dependency check. After the anchor fix, `package_module_name_map`
  makes ruamel-yaml "used" correctly.

**Deviations from the task's baseline `[tool.deptry]` block (justified by the dry run):**

- Baseline `DEP001 = ["sqlalchemy"]` → the actual finding is `DEP003` (a
  transitive import, not a missing one), so sqlalchemy is ignored under
  `DEP003` (same intent; the baseline's DEP001 entry would have been dead
  config).
- Baseline `DEP002` (14 entries) → + `httpx`, `orjson` (declared but not yet
  imported — scope-allowed justified dry-run additions).
- + `DEP001 = ["webauthn"]` (intentionally optional dependency; deferred
  import; not a real dependency issue — the design is documented in
  `src/backend/authentication/webauthn.py`).
- + `DEP004 = ["alembic"]` (tooling-scaffold import of a dev dependency).
- + `package_module_name_map` (ruamel-yaml → ruamel).
- No finding was a real dependency issue: no dependency declarations were
  added/removed to silence anything; nothing genuinely problematic was
  ignored.

**Gate commands + results:**

| Command | Result |
|---|---|
| `uv sync` | PASS — mkdocs, mkdocs-material, mkdocstrings[python] (+ transitive deps) installed; `uv.lock` updated (self-version entry 0.4.0 → 0.4.1 absorbed) |
| `uv run deptry .` (final config, pre-commit) | PASS — "Success! No dependency issues found." (exit 0; scanning 59 files) |
| `uv run deptry .` (post-commit re-run) | PASS — exit 0 (committed state verified) |

**Ruff:** n/a — no Python written in this step (dependency declarations + tool configuration only).

### S4.4 — mkdocs site (userdocs/ + mkdocs.yml) (DOCS/CHORE, make the change)

**Date:** 2026-09-21
**Commit:** `e5c4890428ee259800467bb322c2497c7bb00db0`
(`chore(dev-tooling-wiring): mkdocs site (userdocs/ + mkdocs.yml)`)

**Change made (scope items 3 and 4):**

- `mkdocs.yml` (repo root, minimal and clean):
  - `site_name: python-template`; `docs_dir: userdocs` (binding Q-64 — `docs/`
    is the internal process record and is not part of the site);
  - Material theme (`theme: name: material`; `mkdocs-material` installed in
    S4.3);
  - plugins: `search` + `mkdocstrings` with `default_handler: python`;
  - no `site_url` (no hosting configured), no deploy step.
- `userdocs/` (new, repo root):
  - `index.md` — concise project overview: project name/description matching
    the template's identity (`python-template` / "Default template for Python
    projects."), the eight backend features, a link to the API reference, and
    a short "building the site" note (`uv run mkdocs build --strict`; the
    `userdocs/` vs `docs/` separation).
  - `api.md` — API reference auto-documenting each backend feature's public
    API via mkdocstrings (`::: backend.<feature>` per feature):
    authentication, eventbus, filemanagement, logging, mail,
    sessionmanagement, settings, usermanagement (each exposes its public API
    from its package `__init__`).
- `.gitignore`: no change — the build-artifact `site/` directory is already
  ignored (`.gitignore:155` `/site`), so nothing new was added; `site/` was
  never committable.
- No other files touched; no `src/`, no `tests/`, no behavior delta.

**Gate commands + results:**

| Command | Result |
|---|---|
| `uv run mkdocs build --strict` | PASS — exit 0 ("Documentation built in 1.54 seconds"; strict mode: every warning fails the build). The "Warning from the Material for MkDocs team" block on stderr is the theme's promotional banner (an MkDocs 2.0 announcement), not an MkDocs warning — the build exited 0. |
| render sanity check (not a gate) | `site/api/index.html` contains rendered mkdocstrings content for all eight `backend.*` modules (234 `mkdocstrings` references) |

**Ruff:** n/a — no Python written in this step (MkDocs site: YAML + Markdown only).

### S4.5 — pre-commit hooks + CI jobs (deptry, docs, migrations) (DOCS/CHORE, make the change)

**Date:** 2026-09-21
**Commit:** `35b580f3a8e21637006b5229b6a9fdb4ffa478bc`
(`chore(dev-tooling-wiring): pre-commit hooks + CI jobs (deptry, docs, migrations)`)

**Change made (scope items 5 and 6):**

- `.pre-commit-config.yaml`: appended a `repo: local` entry at the end (language: system,
  pass_filenames: false) with two hooks, following the file's existing style (comment
  conventions, hook ordering):
  - `deptry`: entry `uv run deptry .`, `stages: [pre-commit]` (the fast check —
    pre-commit is the right stage for it), `files: ^(pyproject\.toml|uv\.lock|src/|tests/|scripts/|migrations/)`
    (the paths deptry scans).
  - `mkdocs-build`: entry `uv run mkdocs build --strict`, `stages: [pre-push]`
    (overrides the file's `default_stages: [pre-commit]` — the build is slower; pre-push
    is the right stage for it), `files: ^(mkdocs\.yml|userdocs/|pyproject\.toml)`.
- `.github/workflows/quality.yml`: three new jobs appended after `dependency-review`
  (consistent with the scope's placement note), each mirroring the existing jobs' setup
  steps exactly (actions/checkout@v7, astral-sh/setup-uv@v7, actions/setup-python@v7
  with python-version '3.14', `uv sync --only-group dev`):
  - `dependencies`: `uv run deptry .` (gate).
  - `docs`: `uv run mkdocs build --strict` (gate).
  - `migrations`: `uv run alembic upgrade head` with `ALEMBIC_DATABASE_URL` set to
    `sqlite:////tmp/alembic-ci.db` (a temp file-based SQLite path on the ubuntu-latest
    runner) — validates the alembic scaffold end-to-end.
- `uv.lock`: not touched by the gate runs (the lock was in date after S4.3's sync).

**Gate commands + results:**

| Command | Result |
|---|---|
| `uv run pre-commit validate-config .pre-commit-config.yaml` | PASS — exit 0 |
| `uv run pre-commit run deptry --all-files` | PASS — exit 0 ("deptry (unused dependencies) ... Passed") |
| `uv run pre-commit run mkdocs-build --all-files --hook-stage pre-push` | PASS — exit 0 ("mkdocs build --strict ... Passed") |
| `uv run pre-commit run check-yaml --all-files` | PASS — exit 0 ("check yaml ... Passed") — validates the modified YAML, including the CI workflow |

**Gate invocation note (documented deviation from the task's literal command):**
The task's gate command `uv run pre-commit run mkdocs-build --all-files` (without a
stage flag) cannot pass while the hook is a pre-push-stage hook by design: `pre-commit
run` defaults to the `pre-commit` stage and reports "No hook with id `mkdocs-build` in
stage `pre-commit`" (exit 1). The hook's stage override (`stages: [pre-push]`) is the
explicit task requirement (the build is slower; pre-commit is the right stage for the
fast deptry check), so the hook configuration is kept exactly as specified and the
end-to-end check is run with `--hook-stage pre-push` (exit 0). Both requirements are
recorded here as resolved in favor of the explicit stage override.

**Ruff:** n/a — no Python written in this step (pre-commit hook + CI job configuration only).

### S5.1 — Full test suite (DOCS/CHORE light: confirm no regression)

**Date:** 2026-09-21
**Tree under test:** `e29688833dd18a03508eda0a072c0d3ac86605f8` (HEAD at run time)

**Command:** `uv run pytest tests/ -v`

**Result: GREEN — 557 passed, 0 failed, 0 errors, 1 skipped (183.69s, exit 0).**

- The 1 skip is platform-conditional and pre-existing:
  `tests/acceptance/filemanagement/test_filemanagement.py::test_ac_031_symlink_rejected`
  — "symlinks not available on this host" (win32). Not a failure; no change
  in skip behavior vs baseline.
- **Helper collection check (scope gate):** `tests/tooling_test_helpers.py` was
  **NOT collected** — zero collection/execution lines for it in the `-v` output
  (the filename does not match pytest's default `test_*.py` pattern; it starts
  with `tooling_`). No scope violation.
- **No-behavior-delta confirmation:** the change touches no `src/` file and no
  existing test file; the suite ran to completion with 0 failures and 0 errors,
  so no regression is present. Nothing required classification (no failures).

**Ruff:** n/a — no code written in this step (test run only).
