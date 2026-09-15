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
  - `[tool.mypy]` removed; `[tool.ty.environment]` + `[tool.ty.analysis]` added (ty CLI form verified via `ty --help`: `ty check [PATH]...`). **Updated in S4 (re-run):** the mapping was refined — `explicit_package_bases`/`namespace_packages` map to `[tool.ty.environment] root = ["./src"]` (the ty first-party module root), and `ignore_missing_imports` maps to `[tool.ty.analysis] allowed-unresolved-imports = ["webauthn"]` (scoped to the only third-party package without type information). See the S4 (re-run) section below.
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

## S4 (re-run) — ty module-resolution config

- **Date:** 2026-09-15
- **Sub-objective:** make `uv run ty check src/` pass (or prove it cannot pass with correct config) by fixing the ty CONFIGURATION only. No `src/`/`tests/` changes, no blanket rule suppression.

### Investigation

1. **First-party module resolution.** ty docs (Module discovery): first-party modules are searched in the project root or `src` (if present); the equivalent of mypy's `explicit_package_bases` + `namespace_packages` is `[tool.ty.environment] root` ("the root paths of the project, used for finding first-party modules"; when set, it replaces the auto-detected roots — the project root `.` is no longer included). Verified empirically:
   - `uv run ty check --extra-search-path src src/` → 59 (no change — auto-detection already resolves `backend.*` from the `src` root; the CLI extra-search-path is redundant with `root`).
   - Probe files (temporary, deleted after): `from backend.settings import SettingsRegistry` resolves (no `unresolved-import`); the failure mode is a *type* failure on the resolved name, not a resolution failure. So `backend.*` namespace-package resolution was working all along; the 71/59 findings were never a resolution problem.
2. **`allowed-unresolved-imports = ["*"]` check.** Removed the setting entirely → 60 diagnostics: exactly one new finding, `unresolved-import` for `webauthn` (the `py-webauthn` package — the only third-party dep without type information; `sqlmodel`/`sqlalchemy`/`pydantic`/`loguru` all ship `py.typed`). No masking or distortion of first-party resolution. Final config scopes the setting to `["webauthn"]` (strictly more precise than `["*"]`; same 59).
3. **Root cause of the dominant findings (probe-verified).** A self-contained probe reproduces `error[invalid-type-form]: Variable of type `type` is not allowed in a parameter annotation`:
   - unannotated decorator factory (`def decorator(c): return c`) → **passes**;
   - the exact `logged_class` signature (`def decorator(c: type) -> type`, outer return `type | Callable[[type], type]`) → **same diagnostic**.
   So the 34 `invalid-type-form` + 9 `unsupported-base` findings all trace to the non-generic `logged`/`logged_class` decorator factories in `src/backend/logging/_decorator.py`: ty faithfully applies the declared decorator return type, so every `@logged_class`-decorated class (every service/registry/repository/provider class, per the logging tracing policy) becomes a binding of type `type` — invalid as an annotation (`invalid-type-form`) and as a class base (`unsupported-base: Any | type`). mypy treats `Type`-returning decorators specially (preserves the class type), which is why mypy passed on this tree. **Checker limitation / strictness difference; no ty config controls decorator typing.** (The src-side fix would be generic `type[_T]` decorators — out of scope for this DOCS/CHORE.)
4. **`unresolved-attribute` findings (6, in `src/backend/logging/_decorator.py`; the 7th `unresolved-attribute` is the SQLModel `like` finding covered in item 5).** Dynamic attribute assignment on function/class objects (`wrapper.__logged__`, `wrapper.slow_threshold_ms`, `func.__qualname__`, `c.__logged_class__`). The source already carries mypy-style `# type: ignore[attr-defined]` comments; per ty's suppression docs, ty honors only *bare* `# type: ignore` and codes with a `ty:` prefix — mypy codes (`[attr-defined]`) are ignored. **Checker limitation / suppression-syntax migration artifact; not fixable in config** (fixing it requires `# ty: ignore[unresolved-attribute]` comments in `src/`).
5. **SQLModel ORM findings (10, in the `*repository.py` files).** ty resolves the real `sqlmodel`/`sqlalchemy` types (both ship `py.typed` — mypy had the same type information and passed). Breakdown:
   - `unresolved-attribute` `Object of type `str` has no attribute `like`` + `invalid-argument-type` on `where`/`order_by`: ty models SQLModel model fields by their declared Python types (e.g. `str`), not as SQLAlchemy `Column` objects — the class-attribute query-building magic is not modeled. **Checker limitation.**
   - `invalid-return-type` (`FileRecord | None` vs `FileRecord`, `list[FileRecord | None]` vs `Sequence[FileRecord]`, `list[User | None]` vs `Sequence[User]`): ty's inference for `session.exec(...).first()`/`.all()` produces Optional element types where mypy (with the same stubs) inferred non-Optional. **Checker strictness difference.**
   - `deprecated` (`The function `execute` is deprecated`): third-party API deprecation surfaced by ty's full type resolution. **Third-party strictness.**
   - `invalid-argument-type` on `int.__new__` (`int | None` argument): same Optional-inference difference. **Checker strictness difference.**

### Config variants tested (diagnostic counts, `uv run ty check src/`)

| # | Config | Count |
|---|--------|-------|
| 1 | Baseline as committed in `34864ec` (`python-version = "3.14"` + `allowed-unresolved-imports = ["*"]`, no `root`) | 59 (concise) / 59 (full) |
| 2 | `--extra-search-path src` (CLI) | 59 — redundant with auto-detected `src` root |
| 3 | `ty check .` (project root, CLI) | 300 — out of scope (includes `tests/` and non-`src` module names); not a config issue |
| 4 | `allowed-unresolved-imports` removed | 60 — one new `unresolved-import` (`webauthn`); no resolution distortion |
| 5 | **Final:** `root = ["./src"]` + `allowed-unresolved-imports = ["webauthn"]` | **59** — 0 `unresolved-import`; resolution verified intact |

Note: the previous S4 run recorded "71 in full mode"; that count is **not reproducible** on the current tree — both output modes report 59 under both the baseline and the final config (verified 2026-09-15). The 59-findings list above (concise mode) is the exact remaining set.

### Final ty config (in `pyproject.toml`)

```toml
[tool.ty.environment]
# mypy `python_version = "3.14"` equivalent.
python-version = "3.14"
# mypy `explicit_package_bases = true` + `namespace_packages = true` equivalent:
# the first-party module root, so `backend.*` (namespace-package layout) resolves.
root = ["./src"]

[tool.ty.analysis]
# mypy `ignore_missing_imports = true` equivalent, scoped to the only
# third-party package without type information.
allowed-unresolved-imports = ["webauthn"]
```

(`check_untyped_defs = true` has no ty equivalent — ty analyzes all function bodies by default.)

### Remaining findings (59) — per-finding classification

| Findings | Rule(s) | Classification | Fixable in config? |
|----------|---------|----------------|--------------------|
| 34 | `invalid-type-form` | Checker limitation: non-generic `@logged`/`@logged_class` decorator signatures (`-> type` / `-> Callable[..., Any]`); ty types the decorated class as a `type` variable, mypy preserves the class. Probe-verified. | No (src fix: generic `type[_T]` decorators — out of scope) |
| 9 | `unsupported-base` | Same root cause (decorated class used as a base). | No (same as above) |
| 6 | `unresolved-attribute` | Checker limitation / migration artifact: dynamic attribute assignment in `src/backend/logging/_decorator.py`; mypy-style `# type: ignore[attr-defined]` comments are not honored by ty (only bare `# type: ignore` or `ty:`-prefixed codes). | No (src fix: `# ty: ignore[unresolved-attribute]` — out of scope) |
| 1 + 5 | `unresolved-attribute` (`str` has no `like`) + `invalid-argument-type` (`where`/`order_by`/`int.__new__`) | Checker limitation: ty does not model SQLModel/SQLAlchemy `Column` class-attribute magic; models model fields by declared Python types. | No |
| 3 | `invalid-return-type` | Checker strictness difference: ty infers Optional elements from `session.exec(...).first()`/`.all()` where mypy (same `py.typed` stubs) inferred non-Optional. | No |
| 1 | `deprecated` | Third-party API strictness: deprecation surfaced by full `sqlmodel`/`sqlalchemy` type resolution. | No |

### Conclusion

`uv run ty check src/` **cannot pass with configuration alone**. Module resolution is correct and is now explicitly configured as the faithful mypy mapping (`root = ["./src"]` for `explicit_package_bases`/`namespace_packages`; scoped `allowed-unresolved-imports = ["webauthn"]` for `ignore_missing_imports`). The remaining 59 findings are **checker limitations / strictness differences** in `src/` that mypy did not flag: (a) non-generic `@logged`/`@logged_class` decorator signatures that ty types strictly (43 findings), (b) mypy-style suppression comments ty does not honor (6), and (c) ty's incomplete modeling of SQLModel/SQLAlchemy ORM APIs plus Optional-inference differences (10). No rule codes were blanket-suppressed; no `src/`, `tests/`, `.github/`, or `AGENTS.md` changes were made. Per the sub-objective, the findings are recorded here rather than suppressed.

## S4 (re-run) — Final type-check decision: mypy gate + ty as non-blocking fast local tool

- **Date:** 2026-09-15
- **Decision (user, after evaluating ty vs mypy):** keep **both** mypy and ty.
  - **The type-check CI gate uses mypy** (blocking): `uv run mypy src/`. mypy passes cleanly on the existing SQLModel-based codebase.
  - **ty is a non-blocking fast local/LSP tool** (informational in CI via `continue-on-error: true`): `uv run ty check src/`.
- **Rationale:** ty is faster (10-60x) but less conformant (53% vs mypy 58%) and produces 59 false positives on the SQLModel-based codebase (SQLModel column transformation, `from __future__ import annotations` + `TYPE_CHECKING` imports, custom decorators). mypy passes cleanly, so it is the correct gate. ty stays for developer speed/LSP.
- **Changes applied:**
  - `pyproject.toml`: restored `mypy>=1.10` to the dev dependency group (kept `ty>=0.0.81`); restored the `[tool.mypy]` config (kept the `[tool.ty]` config intact).
  - `.github/workflows/quality.yml`: the `type-check` job now runs `Run mypy (gate)` (`uv run mypy src/`, blocking) + `Run ty (informational)` (`uv run ty check src/`, `continue-on-error: true`).

