# tooling-hardening — Verification Record

- **Change type:** DOCS/CHORE (no behavior delta: documentation, configuration, CI, tooling)
- **Phase 1 (Scope):** recorded 2026-09-15
- **Base:** `main` @ `d5f0a94` (branch `chore/tooling-hardening`)

## Scope — exact non-behavior changes

The following files are changed (and ONLY these) in the implementation step (S4). This record is the scope; the implementation step must not add, remove, or re-decide any item.

### 1. `pyproject.toml`

- **dev deps:**
  - REMOVE `mypy>=1.10` (current line: `"mypy>=1.10",` in `[dependency-groups] dev`).
  - ADD `ty` at the current version, via `uv add --dev ty`.
  - ADD `pip-audit` and `bandit` (dev tools used by the CI security job).
- **type-checker config:**
  - REMOVE the `[tool.mypy]` section (current content: `python_version = "3.14"`, `check_untyped_defs = true`, `ignore_missing_imports = true`, `explicit_package_bases = true`, `namespace_packages = true`).
  - ADD the ty configuration equivalent (ty supports `[tool.ty]` in `pyproject.toml`; **verify in the implementation step** — if ty's config location differs, use that instead and note it in this record).
  - Map the mypy settings to the ty equivalents ty supports; drop what ty handles natively or does not support, and **record the mapping** here:
    - `python_version = "3.14"` → (map or note)
    - `check_untyped_defs = true` → (map or note)
    - `ignore_missing_imports = true` → (map or note)
    - `explicit_package_bases = true` → (map or note)
    - `namespace_packages = true` → (map or note)
- **coverage floor:**
  - ADD `[tool.coverage.report]` with `fail_under = 92` (floor of the 2026-09-15 baseline 92.74%; comment in the file: raise as coverage improves).
- **`[tool.agent-runner] quality_check`:**
  - `uv run ruff check src/ && uv run mypy src/` → `uv run ruff check src/ && uv run ty check src/` (**verify ty's CLI command form first**).

### 2. `AGENTS.md`

- "Tooling & Execution Environment" section (current line 23): the mypy type-checking line → ty (`uv run ty check src/`).
- Every other mypy reference in `AGENTS.md` (search `mypy`) → the ty equivalent. Current references: lines 23, 439, 445.

### 3. NEW `.github/workflows/quality.yml`

A quality workflow with four jobs.

- **Triggers:** `pull_request` to `main` + `push` to `main`.
- **Each job:** checkout, setup-uv, setup-python 3.14, `uv sync --only-group dev`.
- **Jobs:**
  - `type-check`: `uv run ty check src/`.
  - `security`: `uv run pip-audit` + `uv run bandit -r src/` (bandit flags to be verified against the current tree in the implementation step).
  - `coverage`: `uv run pytest tests/ --cov --cov-report=xml` (pytest-cov honors `[tool.coverage.report] fail_under` → the job fails below the threshold).
  - `dependency-review`: `dependency-review-action` (PR-time dependency gate).

### 4. NEW `.github/dependabot.yml`

- `version: 2`.
- updates: `pip` ecosystem (directory `/`, weekly — verify the correct config for a uv project) + `github-actions` ecosystem (directory `/`, weekly).

### 5. `.gitignore`

Append (at the end of the file):
- `settings/` — test-run artifact: the settings feature's default `YamlValueRepository('settings')` writes runtime values there during tests.
- `.pi/subagents.json` — pi subagent snapshot state.

### No behavior delta — confirmation

- No `src/` changes.
- No `tests/` changes.
- All changes are documentation, configuration, CI, and tooling. Externally observable behavior is unchanged.

## Verification requirements (for the implementation step — S4)

The implementation step MUST run these and record the results (findings only — do NOT modify `src/` or dependency versions to fix them):

- `uv run ty check src/` passes on the current tree (record any findings; do NOT modify `src/`).
- `uv run bandit -r src/` result recorded (record any pre-existing findings; do NOT modify `src/`).
- `uv run pip-audit` result recorded (record any pre-existing vulnerabilities; do NOT modify `src/` or dependency versions).
- `uv run pytest tests/ --cov` (sequential) passes and coverage ≥ 92 (record the number).
- `uv run ruff check .` → `All checks passed!`.

## Versioning

- DOCS/CHORE: no version bump (per the Versioning section of `AGENTS.md`).
