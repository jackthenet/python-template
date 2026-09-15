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
    - `python_version = "3.14"` → `[tool.ty.environment] python-version = "3.14"`
    - `check_untyped_defs = true` → dropped (ty analyzes all function bodies by default; no setting exists or needed)
    - `ignore_missing_imports = true` → `[tool.ty.analysis] allowed-unresolved-imports = ["*"]` (suppresses `unresolved-import` for all modules)
    - `explicit_package_bases = true` → dropped (ty auto-detects the `./src` first-party root; no setting exists or needed)
    - `namespace_packages = true` → dropped (same as above — the namespace-package layout is handled natively; `ty check src/` resolves `backend.*` without config, verified on the current tree)
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

## S4 — Implementation (scoped tooling changes applied)

- **Date:** 2026-09-15
- **Scope:** exactly the non-behavior changes per the Scope section above; nothing re-decided.

### Changes applied

- `pyproject.toml`:
  - `uv add --dev ty pip-audit bandit` → `ty>=0.0.81`, `pip-audit>=2.10.1`, `bandit>=1.9.4` (dev group); `uv remove --dev mypy`; `uv.lock` updated by uv (committed with the change).
  - `[tool.mypy]` removed; `[tool.ty.environment]` + `[tool.ty.analysis]` added (ty config mapping per the placeholders above; ty CLI form verified via `ty --help`: `ty check [PATH]...`).
  - `[tool.coverage.report]` added: `fail_under = 92` (floor of the 2026-09-15 baseline 92.74%; raise as coverage improves).
  - `[tool.agent-runner] quality_check` → `uv run ruff check src/ && uv run ty check src/`.
- `AGENTS.md`: all 3 mypy references (old lines 23, 439, 445) → ty (`uv run ty check src/`).
- NEW `.github/workflows/quality.yml`: jobs `type-check` (`uv run ty check src/`), `security` (`uv run pip-audit` + `uv run bandit -r src/`), `coverage` (`uv run pytest tests/ --cov --cov-report=xml`), `dependency-review` (`actions/dependency-review-action@v5` — current major verified via the GitHub API; PR-time dependency gate). Triggers: `pull_request` + `push` to `main`. Each job: checkout@v4, setup-uv@v6, setup-python@v5 (3.14), `uv sync --only-group dev`.
- NEW `.github/dependabot.yml`: `package-ecosystem: "uv"` (the dedicated ecosystem for uv-managed projects per the uv docs — updates `uv.lock`; the correct uv-project config) + `github-actions`, both `directory: "/"`, weekly.
- `.gitignore`: appended `settings/` (test-run artifact of the settings feature's default `YamlValueRepository('settings')`) and `.pi/subagents.json` (pi subagent snapshot state).

### Verification results

| # | Requirement | Result |
|---|-------------|--------|
| 1 | `uv run ty check src/` | **FAILS — 71 pre-existing diagnostics (full mode; 59 in concise mode)** on the current tree. ty is a new type checker whose diagnostics differ from mypy (which passed on this tree); NOT caused by this change. `src/` not modified (per scope). Concise-mode breakdown — errors: 34 `invalid-type-form`, 7 `unresolved-attribute`, 5 `invalid-argument-type`, 3 `invalid-return-type`; warnings: 9 `unsupported-base`, 1 `deprecated`. Full list below. |
| 2 | `uv run bandit -r src/` | PASS — "No issues identified." (exit 0; 5166 lines scanned) |
| 3 | `uv run pip-audit` | PASS — "No known vulnerabilities found" (exit 0; local `python-template` package skipped as expected) |
| 4 | `uv run pytest tests/ --cov` (sequential) | PASS — 488 passed, 1 skipped; **TOTAL coverage 92.74%** ≥ 92 floor ("Required test coverage of 92.0% reached. Total coverage: 92.74%") |
| 5 | `uv run ruff check .` | PASS — "All checks passed!" |

### Pre-existing ty findings (concise mode, exact)

```
src\backend\authentication\feature_settings.py:14:33: error[invalid-type-form] Variable of type `type` is not allowed in a parameter annotation
src\backend\authentication\repository.py:63:31: warning[unsupported-base] Unsupported class base with type `Any | type`
src\backend\authentication\repository.py:126:37: warning[unsupported-base] Unsupported class base with type `Any | type`
src\backend\authentication\repository.py:179:42: warning[unsupported-base] Unsupported class base with type `Any | type`
src\backend\authentication\service.py:88:23: error[invalid-type-form] Variable of type `type` is not allowed in a parameter annotation
src\backend\authentication\service.py:89:26: error[invalid-type-form] Variable of type `type` is not allowed in a parameter annotation
src\backend\authentication\service.py:90:29: error[invalid-type-form] Variable of type `type` is not allowed in a parameter annotation
src\backend\authentication\service.py:91:27: error[invalid-type-form] Variable of type `type` is not allowed in a parameter annotation
src\backend\authentication\service.py:92:30: error[invalid-type-form] Variable of type `type` is not allowed in a parameter annotation
src\backend\authentication\service.py:93:28: error[invalid-type-form] Variable of type `type` is not allowed in a parameter annotation
src\backend\authentication\service.py:95:26: error[invalid-type-form] Variable of type `type` is not allowed in a parameter annotation
src\backend\authentication\webauthn.py:33:26: warning[unsupported-base] Unsupported class base with type `Any | type`
src\backend\eventbus\eventbus.py:158:28: error[invalid-type-form] Variable of type `type` is not allowed in a return type annotation
src\backend\eventbus\eventbus.py:212:20: error[invalid-type-form] Variable of type `type` is not allowed in a type expression
src\backend\eventbus\eventbus.py:216:24: error[invalid-type-form] Variable of type `type` is not allowed in a return type annotation
src\backend\eventbus\feature_settings.py:14:33: error[invalid-type-form] Variable of type `type` is not allowed in a parameter annotation
src\backend\filemanagement\feature_settings.py:45:33: error[invalid-type-form] Variable of type `type` is not allowed in a parameter annotation
src\backend\filemanagement\repository.py:111:28: warning[unsupported-base] Unsupported class base with type `Any | type`
src\backend\filemanagement\repository.py:147:21: warning[deprecated] The function `execute` is deprecated
src\backend\filemanagement\repository.py:147:54: error[invalid-argument-type] Argument to bound method `DMLWhereBase.where` is incorrect
src\backend\filemanagement\repository.py:164:20: error[invalid-return-type] Return type does not match returned value: expected `FileRecord`, found `FileRecord | None`
src\backend\filemanagement\repository.py:182:45: error[unresolved-attribute] Object of type `str` has no attribute `like`
src\backend\filemanagement\repository.py:184:44: error[invalid-argument-type] Argument to bound method `GenerativeSelect.order_by` is incorrect
src\backend\filemanagement\repository.py:186:20: error[invalid-return-type] Return type does not match returned value: expected `Sequence[FileRecord]`, found `list[FileRecord | None]`
src\backend\filemanagement\service.py:161:21: error[invalid-type-form] Variable of type `type` is not allowed in a parameter annotation
src\backend\filemanagement\service.py:162:18: error[invalid-type-form] Variable of type `type` is not allowed in a parameter annotation
src\backend\filemanagement\service.py:164:28: error[invalid-type-form] Variable of type `type` is not allowed in a parameter annotation
src\backend\filemanagement\service.py:173:28: error[invalid-type-form] Variable of type `type` is not allowed in a return type annotation
src\backend\filemanagement\service.py:181:39: error[invalid-type-form] Variable of type `type` is not allowed in a parameter annotation
src\backend\filemanagement\service.py:187:42: error[invalid-type-form] Variable of type `type` is not allowed in a parameter annotation
src\backend\filemanagement\service.py:193:40: error[invalid-type-form] Variable of type `type` is not allowed in a parameter annotation
src\backend\filemanagement\service.py:199:38: error[invalid-type-form] Variable of type `type` is not allowed in a parameter annotation
src\backend\filemanagement\service.py:199:59: error[invalid-type-form] Variable of type `type` is not allowed in a return type annotation
src\backend\filemanagement\service.py:231:40: error[invalid-type-form] Variable of type `type` is not allowed in a parameter annotation
src\backend\filemanagement\service.py:290:19: error[invalid-type-form] Variable of type `type` is not allowed in a parameter annotation
src\backend\filemanagement\service.py:542:37: error[invalid-type-form] Variable of type `type` is not allowed in a parameter annotation
src\backend\filemanagement\storage.py:75:31: warning[unsupported-base] Unsupported class base with type `Any | type`
src\backend\filemanagement\storage.py:168:30: warning[unsupported-base] Unsupported class base with type `Any | type`
src\backend\logging\_decorator.py:80:16: error[unresolved-attribute] Object of type `(...) -> Any` has no attribute `__qualname__`
src\backend\logging\_decorator.py:118:16: error[unresolved-attribute] Object of type `(...) -> Any` has no attribute `__qualname__`
src\backend\logging\_decorator.py:173:9: error[unresolved-attribute] Unresolved attribute `__logged__` on type `(...) -> Any`
src\backend\logging\_decorator.py:174:9: error[unresolved-attribute] Unresolved attribute `slow_threshold_ms` on type `(...) -> Any`
src\backend\logging\_decorator.py:201:9: error[unresolved-attribute] Unresolved attribute `__logged_class__` on type `type`
src\backend\logging\_decorator.py:202:9: error[unresolved-attribute] Unresolved attribute `slow_threshold_ms` on type `type`
src\backend\logging\feature_settings.py:28:29: error[invalid-type-form] Variable of type `type` is not allowed in a parameter annotation
src\backend\logging\feature_settings.py:47:33: error[invalid-type-form] Variable of type `type` is not allowed in a parameter annotation
src\backend\mail\feature_settings.py:36:29: error[invalid-type-form] Variable of type `type` is not allowed in a parameter annotation
src\backend\mail\feature_settings.py:66:33: error[invalid-type-form] Variable of type `type` is not allowed in a parameter annotation
src\backend\mail\service.py:38:20: error[invalid-type-form] Variable of type `type` is not allowed in a parameter annotation
src\backend\mail\service.py:39:20: error[invalid-type-form] Variable of type `type` is not allowed in a parameter annotation
src\backend\mail\service.py:77:53: error[invalid-type-form] Variable of type `type` is not allowed in a return type annotation
src\backend\mail\transport.py:37:25: warning[unsupported-base] Unsupported class base with type `Any | type`
src\backend\usermanagement\feature_settings.py:14:33: error[invalid-type-form] Variable of type `type` is not allowed in a parameter annotation
src\backend\usermanagement\repository.py:103:28: warning[unsupported-base] Unsupported class base with type `Any | type`
src\backend\usermanagement\repository.py:184:20: error[invalid-return-type] Return type does not match returned value: expected `Sequence[User]`, found `list[User | None]`
src\backend\usermanagement\repository.py:192:21: error[invalid-argument-type] Argument to bound method `Select.where` is incorrect
src\backend\usermanagement\repository.py:193:21: error[invalid-argument-type] Argument to bound method `Select.where` is incorrect
src\backend\usermanagement\repository.py:196:24: error[invalid-argument-type] Argument to constructor `int.__new__` is incorrect
src\backend\usermanagement\service.py:66:21: error[invalid-type-form] Variable of type `type` is not allowed in a parameter annotation
Found 59 diagnostics (concise mode; 71 in full mode)
```
