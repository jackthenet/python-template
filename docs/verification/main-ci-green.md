# ISSUE Triage: main-ci-green

## Type

**ISSUE** — a deviation from approved spec behavior (a defect). No new behavior is introduced.

- **Date:** 2026-10-02
- **Base:** `origin/main` @ `75ca243` ("Merge pull request #56 from jackthenet/dependabot/uv/test-tooling-091a29ec65")
- **Branch:** `issue/main-ci-green`
- **Worktree:** `C:/workspace/active-projects/python-template_kopie-worktrees/issue/main-ci-green`
- **Why this change exists:** `main`'s CI is red after three merged dependabot PRs (#55 lint-and-types, #56 test-tooling, #57 runtime-core). The user decided to fix `main` in one dedicated change before PR #54 (crosscut/search) merges into it.

### Scope composition (six items — extended by Q-127, answered 2026-10-02)

| Item | Nature | Type | Affected spec IDs | Expected files |
|---|---|---|---|---|
| **A** | settings YAML round-trip loses `'\x85'` (NEL) | **defect** — the ISSUE core | `settings.md` INV-009, REQ-022, AC-030; `settings-coverage.md` REQ-009/010/011, INV-002 | `src/backend/settings/repository.py` |
| **B** | hypothesis `DeadlineExceeded` in `test_last_admin_invariant` | **defect** (test-harness; no product-behavior deviation) | `user-roles-permissions.md` INV-003, REQ-013, AC-015/036; `user-management.md` REQ-008, AC-017..019 | `tests/property/usermanagement/test_multi_role_invariants.py` |
| **C** | 3 ruff `I001` errors on `main` | **chore** (non-behavior) | none | `tests/acceptance/permissions/test_check_api.py`, `tests/acceptance/permissions/test_enforcement.py`, `tests/contract/permissions/test_performance.py` |
| **D** | pip-audit CVEs in two transitive dev dependencies | **chore** (non-behavior) | none | `uv.lock` |
| **E** | the logging feature's runtime reconfigure deletes loguru sinks it does not own (the actual CI `tests`-job failure) | **defect** (feature lifecycle / test isolation) | `logging.md` REQ-001/002/003, AC-001/002/004/005, INV-001, EDGE-005; `settings-coverage.md` REQ-014/015, AC-019/020 | `src/backend/logging/_setup.py`, `tests/conftest.py`, `tests/logging_test_helpers.py`, `tests/settings_test_helpers.py` |
| **F** | `dependency-review` job runs on `push` and fails by construction | **chore** (CI config, non-behavior) | none | `.github/workflows/quality.yml` |

Items C, D and F alter no externally observable behavior; they ride along by user decision. A is the ISSUE core. B is a test-harness defect (the specified invariant itself still holds). E is a real product-side defect in the logging feature's reconfiguration path (it mutates global loguru state it does not own) and is the only item that currently reddens CI's `tests` job.

**Scope extension (no reclassification).** Q-127 (answered) moved E and F from "recorded scope gap" to in-scope. The change type stays **ISSUE**: E fixes a deviation from specified observability without introducing new behavior (see §6.3, spec-compliance verdict COMPLIANT — no Spec Amendment needed), and C/D/F remain non-behavior chore items inside the same change. No todo-set or phase-matrix change results (the ISSUE path already runs Phases 1, 3, 4, 5, 6).

---

## 0. Reproduction-environment note (why local ≠ CI)

Two environment facts explain the difference between "the suite looks green locally" and "the suite is red on main":

1. **Per-worktree `.hypothesis` example database.** Hypothesis stores failing examples under `<worktree>/.hypothesis/` (gitignored, per-worktree, cold in a fresh worktree; overridable with `HYPOTHESIS_STORAGE_DIRECTORY`). A worktree whose database already contains the stored counterexample replays it first and fails **deterministically**; a fresh worktree does not replay it and can pass. `test_inv_009_yaml_roundtrip` is therefore a **latent defect discovered by hypothesis**, not a random flake — confirmed below by reproducing it from a clean database with an explicit seed and with `hypothesis.find`.
2. **`pytest-randomly` reorders the suite every run** (`pytest-randomly` is a dev dependency and is active by default; CI runs `uv run pytest tests/ -v` in `spec-validation.yml:70` and `uv run pytest tests/ --cov` in `quality.yml:59`). Order-dependent failures therefore appear with a varying count from run to run.

Deterministic reproduction recipes used in this triage:

```bash
# A — deterministic (no dependency on the stored example database)
uv run pytest tests/property/settings/test_settings_properties.py::test_inv_009_yaml_roundtrip \
  -p no:randomly --hypothesis-seed=99          # FAILED (falsifying example found)
# minimal falsifying value found with hypothesis.find: '\x85'

# B — deterministic per seed (3 of 5 seeds fail on this machine)
uv run pytest tests/property/usermanagement/test_multi_role_invariants.py::test_last_admin_invariant \
  -p no:randomly --hypothesis-seed=7           # DeadlineExceeded: 246.47 ms > 200 ms
                                               # seed=101 → 355.59 ms, seed=2024 → 251.62 ms
```

Both nodes **pass** in CI (see §6) — they are local-side defects; the CI test-job failures are a different family (logging sink pollution, item E).

---

## 1. Affected Requirements

### Item A — from `docs/specs/settings.md`

- **INV-009** (the normative source for the defect): *"For any valid `Template`: `repository.save(t)` followed by `repository.get(t.name)` returns a template equal to t (YAML round-trip)."*
- **REQ-022**: *"The first repository implementation is `YamlTemplateRepository(directory)`: one file per template named `<name>.yaml`, safe YAML, atomic writes (a template file is always either absent or valid YAML), the directory is created if it does not exist, and operations are thread-safe."*
- **AC-030** (REQ-022): *"**Given** a `YamlTemplateRepository` with a directory, **When** a template is created via the registry, **Then** a file `<name>.yaml` exists in the directory, **And** it is valid YAML containing the template's fields (name, category, group, values)."*
- **AC-031** (REQ-021, REQ-022): persistence across registry instances sharing a directory — *"the template is returned (persistence across instances)"*.
- Test-strategy binding (spec §Test strategy): `INV-009 | property | tests/property/settings/test_settings_properties.py | test_inv_009_yaml_roundtrip`.
- "Valid `Template`" is not narrower than the model: `Template` (`src/backend/settings/models.py:323`) is `name: str`, `category: str`, `group: str | None`, `values: dict[str, Any]` — no string constraint; and a TEXT setting with no `pattern`/`min_length`/`max_length` accepts any `str`. So `values={"app.a": "\x85"}` **is** a valid template value, and INV-009 covers it. **The requirement exists — no spec amendment is needed for A.**

### Item A (same defect, value side) — from `docs/specs/settings-coverage.md`

- **REQ-010**: *"The settings feature provides the `ValueRepository` abstraction (`load`/`save`) and a `YamlValueRepository` (single `values.yaml`, safe YAML, atomic write, thread-safe, directory created if missing)."*
- **REQ-009**: *"The settings feature persists **all** current values to the value repository on every change (`set_value`, `reset`, `reset_all`, template loads), and loads them at construction."*
- **REQ-011**: *"Persisted values take precedence over definition defaults (priority: persisted > default). A persisted value is applied to the setting at load time."*
- **INV-002**: *"For a `LIST` setting, a persisted value round-trips: `save(values)` then `load()` returns the same value."*
- Both repositories share one serializer (`_dump_yaml` / `_load_yaml` in `src/backend/settings/repository.py:31`/`:45`), so the defect is common to the template and the value path.

### Item B — from `docs/specs/user-roles-permissions.md` (multi-role amendment)

- **INV-003**: *"For any sequence of assignment operations that does not raise: if any user has `admin` in their roles, at least one such user is active (the last-admin invariant)."* — the invariant `tests/property/usermanagement/test_multi_role_invariants.py::test_last_admin_invariant` implements.
- **REQ-013**: *"The last-admin guard is preserved on every role-assignment path (no bypass): demoting, deactivating, or deleting the last active admin raises `LastAdminError`."*
- **AC-015** (REQ-013), **AC-036** (REQ-026): the concrete `LastAdminError` criteria on `remove_role` / `set_roles`.
- Amended guard statement (spec line 469): *"Operations that remove `admin` from the last active admin's roles — `set_role`, `set_roles`, `remove_role`, `delete_user`, `deactivate_user` — raise `LastAdminError`."*

### Item B — from `docs/specs/user-management.md` (original guard)

- **REQ-008**: *"Last-admin protection: while `admin` is in the configured role set, operations that would leave zero active admins (delete, deactivate, demote) are rejected with `LastAdminError`."*
- **AC-017 / AC-018 / AC-019** (REQ-008): `test_ac_017_delete_last_admin`, `test_ac_018_deactivate_last_admin`, `test_ac_019_demote_last_admin`.

> Note: the orchestrator's node path `tests/acceptance/usermanagement/test_multi_role_invariants.py` is actually **`tests/property/usermanagement/test_multi_role_invariants.py`** (property category). `docs/specs/user-roles-permissions.md:725` binds `INV-003` to `tests/property/permissions/test_invariants.py::test_last_admin_invariant`; the implemented copies live in `tests/property/usermanagement/test_multi_role_invariants.py` and `tests/property/usermanagement/test_usermanagement_properties.py::test_inv_003_last_admin_invariant` — a traceability-path drift to fix in Phase 5 (S5.3), not a behavior issue.

### Item E — from `docs/specs/logging.md`

Quoted verbatim (`docs/specs/logging.md`):

- **REQ-001** (line 66): *"The logging feature provides a `setup_logger()` function that configures loguru with a console sink (stderr, colorized, backtrace enabled) and a rotating file sink (UTF-8, enqueued, backtrace enabled, `diagnose=False`)."*
- **REQ-002** (67): *"`setup_logger()` is idempotent: subsequent calls are no-ops. Thread-safe via a `threading.Event`."*
- **REQ-003** (68): *"The logging feature provides an `_InterceptHandler` that routes stdlib `logging` records into loguru sinks, skipping frozen importlib bootstrap frames."*
- **AC-001** (82): *"**Given** a fresh Python environment, **When** `setup_logger()` is called, **Then** loguru has a console sink on stderr with colorize and backtrace enabled, **And** a rotating file sink with UTF-8 encoding, enqueue, backtrace, and `diagnose=False`."*
- **AC-002** (83): *"**Given** `setup_logger()` has been called once, **When** it is called again, **Then** the second call is a no-op and no new sinks are added."*
- **AC-004** (85): *"**Given** a stdlib `logging` record emitted by a third-party library, **When** the record passes through `_InterceptHandler`, **Then** the record is routed into loguru sinks with the correct level and message."*
- **AC-005** (86): *"**Given** a stdlib `logging` record originating from a frozen importlib bootstrap frame, **When** the record passes through `_InterceptHandler`, **Then** the bootstrap frame is skipped in depth calculation."*
- **INV-001** (104): *"For any number of concurrent `setup_logger()` calls, the number of loguru sinks **added** is exactly one console sink and one file sink."* (emphasis added — the quantifier is over sinks *added by the feature*, not over the process-global handler set)
- **EDGE-005** (116): *"Stdlib `logging` record with a level not recognized by loguru | Record is routed using the numeric level number instead of the name."*

### Item E — from `docs/specs/settings-coverage.md`

- **REQ-014** (line 141): *"`setup_logger()` takes no arguments and reads `logging.*` from the shared registry (falling back to the logging defaults with a warning if unregistered). It is idempotent (a second call is a no-op)."*
- **REQ-015** (142): *"The logging feature subscribes to `SettingChanged` and reconfigures **the sink** at runtime when any `logging.*` setting changes, re-applying all current `logging.*` values."* — the mechanism the pollution runs through; note the singular "the sink" (the feature's own sink), which is at least as faithful a reading as removing every sink in the process.
- **AC-019** (175): *"**Given** the shared registry, **When** `setup_logger()` is called, **Then** `logging.*` is read from the registry."*
- **AC-020** (176): *"**Given** a configured logging sink, **When** `set_value("logging.log_level", "DEBUG")` is called, **Then** the sink is reconfigured to `DEBUG`."* — the observable half of REQ-015 (the feature's own sink must follow the new value; nothing is said about other sinks).

### Items C, D and F

No REQ/AC is affected: C is a lint-only import-ordering change in three test files, D is a dependency-manifest change, F is a GitHub-Actions trigger-condition change. All three are non-behavior (chore) scope.

---

## 2. Defect confirmation — A (settings YAML round-trip loses U+0085 NEL)

### Observed behavior

`YamlTemplateRepository.save(t)` then `.get(t.name)` returns a template **not equal** to `t` when a value contains U+0085 (NEL).

Minimal falsifying value found with `hypothesis.find` (clean example database, `st.text(min_size=0, max_size=10)`):

```text
minimal failing example: '\x85'
dumped document      : "a: '\x85  '\n"      # literal NEL inside a single-quoted scalar
loaded back          : ' '                  # NEL folded to a line break → single space
```

Same failure through the real repository, and through the value path:

```text
'\x85'      -> "a: '\x85  '\n"  -> ' '        MISMATCH
'a\x85b'    -> "a: 'a\x85  b'\n" -> 'a b'     MISMATCH   (embedded NEL also lost)
'\x85  '    -> 'a: "\\N  "\n'    -> '\x85  '  ok  (trailing spaces force the escaped style)
{'k': ['\x85', 'ok']}  ->  "k:\n- '\x85    '\n- ok\n"  ->  [' ', 'ok']   MISMATCH
```

Observed in the suite:

```bash
uv run pytest tests/property/settings/test_settings_properties.py::test_inv_009_yaml_roundtrip \
  -p no:randomly --hypothesis-seed=99        # → 1 failed
```

Characterisation (scan of code points `0x0020`–`0x1FFF`, one probe value per code point): **exactly one failing code point, `0x85` (NEL)**. `U+2028`/`U+2029`, NBSP, `U+009C`, control characters (`\x1c`, `\r`, `\n`) and all other tested characters round-trip correctly. So the defect class is narrow: strings containing U+0085.

Mechanism: the serializer is ruamel.yaml (`ruamel.yaml 0.19.1`, `YAML(typ="safe")` in `src/backend/settings/repository.py:31-43`). Its YAML-1.1 **reader** treats U+0085 as a line break, while its **emitter** writes the character literally inside a single-quoted scalar instead of forcing a double-quoted (escaped) style. The written document is valid YAML but denotes a different string. Verified: `YAML(typ="safe")` with `typ="rt"` fails identically; a scalar emitted double-quoted (`app.a: "\N"`) loads back as `'\x85'` correctly.

Not a dependency regression: the three merged dependabot PRs changed only `hypothesis 6.168.0→6.168.1`, `ruff 0.16.8→0.16.9`, `sqlmodel 0.0.42→0.0.47`, `ty 0.0.82→0.0.84`, and the project version. `ruamel-yaml` is unchanged at `0.19.1` (also the current release) — the defect is **latent/pre-existing**, surfaced by hypothesis's example search.

### Required behavior (per cited spec IDs)

- **INV-009**: for **any valid `Template`**, `repository.save(t)` followed by `repository.get(t.name)` returns a template **equal to `t`**. For `values={"app.a": "\x85"}` the loaded value must be `'\x85'`, not `' '`.
- **settings-coverage INV-002**: a persisted LIST value round-trips (`save(values)` then `load()` returns the same value) — a LIST item containing U+0085 must survive.
- **REQ-022 / settings-coverage REQ-010**: the persisted document must faithfully carry the template's / the values' content ("safe YAML"; AC-030: "valid YAML containing the template's fields … values").

### Deviation

The stored document silently changes the value: a valid setting/template value that round-trips through the repository comes back different (and, per settings-coverage REQ-011, the corrupted value then **overrides** the registered default at construction). This is a data-integrity deviation from INV-009 (and settings-coverage INV-002) — the ISSUE core.

### Fix options (Phase 4 decides; no implementation here)

1. **Recommended — emit affected strings double-quoted.** In `_dump_yaml`, recursively wrap `str` values that contain a YAML-1.1 line-break character (`\x85`, `\u2028`, `\u2029`) so they are emitted in double-quoted (escaped) style, registering a representer for the wrapper type on the safe representer. Verified working in this worktree: `{'values': {'app.a': '\x85', …}}` → `app.a: "\N"` → loads back equal (`roundtrip_ok=True`), while `null`/numbers/booleans stay unquoted and unchanged. One file, both repositories, on-disk format stays valid YAML and old files keep loading.
2. `default_style='"'` on the YAML instance — **rejected**: it also double-quotes `null` (`group: null` → `group: "null"`), which changes types and breaks the template schema.
3. `DoubleQuotedScalarString` without a representer — **rejected as-is**: `YAML(typ="safe")` raises `RepresenterError: cannot represent an object: '\x85'` for `str` subclasses, so a representer must be registered (this is variant of option 1).
4. Store values as JSON inside YAML, or switch serializer — rejected: larger schema/format change, conflicts with AC-030's "valid YAML containing the template's fields", and needs a Spec Amendment.

---

## 3. Defect confirmation — B (hypothesis `DeadlineExceeded` in `test_last_admin_invariant`)

### Observed behavior

`tests/property/usermanagement/test_multi_role_invariants.py::test_last_admin_invariant` fails with hypothesis's **default per-example deadline (200 ms)**:

```text
hypothesis.errors.DeadlineExceeded: Test took 246.47ms, which exceeds the deadline of 200.00ms.
```

Reproduced from a clean example database, `-p no:randomly`, one run per seed:

| seed | result |
|---|---|
| 1 | passed |
| 7 | **DeadlineExceeded — 246.47 ms** |
| 42 | passed |
| 101 | **DeadlineExceeded — 355.59 ms** |
| 2024 | **DeadlineExceeded — 251.62 ms** |

3 of 5 seeds fail on this machine (the orchestrator's earlier observation of 3/3 with the stored counterexample replaying, `259.45 ms > 200 ms`, is the same failure). The test's `@settings` is `max_examples=20, suppress_health_check=[HealthCheck.too_slow]` — **no `deadline`**, so hypothesis's 200 ms default applies. The invariant assertion itself never fails; the example is simply slower than the default deadline (each example builds a fresh in-memory SQLite repository + `UserManager` and replays up to 10 operations with list/role round-trips).

### Required behavior (per cited spec IDs)

- **user-roles-permissions INV-003**: for any sequence of assignment operations that does not raise, if any user has `admin` in their roles, at least one such user is active.
- **user-roles-permissions REQ-013 / AC-015 / AC-036** and **user-management REQ-008 / AC-017..AC-019**: the last-admin guard raises `LastAdminError` on every path.
- No spec ID sets a per-example time budget for property tests; the specs require the **invariant** to hold, not a runtime bound.

### Deviation and classification note

The **product behavior does not deviate** from INV-003/REQ-013: no example ever violated the invariant; the failure is hypothesis's harness deadline being tighter than this machine's per-example runtime. Strictly, B is a **test-infrastructure defect** (the test cannot reliably exercise INV-003), not a deviation from approved spec behavior — it is carried in this ISSUE as a test-only fix, and it must not weaken the invariant.

### Fix policy — DECIDED (Q-128, answered 2026-10-02)

**Option 1 is the fix: an explicit measured `@settings(deadline=1000)` with an explanatory comment** on `test_last_admin_invariant`. The user first asked whether the per-example cost could be reduced instead; the analysis is that the cost is **argon2id hashing** (~50–100 ms per `create_user`, ADR-019) — up to ~11 creates in a `max_size=10` operation sequence ≈ 300 ms — so shrinking `max_size` to 4 would still land at ~150–200 ms (borderline, keeps flaking) **and** would shrink the operation-interleaving space that INV-003 coverage depends on, i.e. a **real weakening** of the invariant's coverage. `max_size=10`, `max_examples=20`, the strategy and the invariant assertion stay byte-identical. Hypothesis's `deadline` is a harness health check on per-example runtime, not a product performance budget (those live in explicit NFR budget tests), so raising it to a measured 1000 ms weakens nothing.

### Fix options considered (recorded for the review gate)

1. **CHOSEN — explicit, measured `deadline` on the test's `@settings`** (e.g. `deadline=1000`), justified by the measured distribution (246–356 ms observed for the slowest examples on this machine, i.e. the 200 ms default has no headroom) and recorded in the verification artifact. The invariant, the strategy, and the assertion stay byte-identical — nothing is weakened; only the harness tolerance is made explicit and machine-independent.
2. `deadline=None` — legitimate per hypothesis for slow suites, but it removes the (weak) per-example performance signal entirely; acceptable only with a recorded justification. Prefer option 1.
3. Reduce per-example work (reuse one repository/manager per example via a lighter fixture, shorten the operation list) — changes the test's coverage profile; only worth it if the measured runtime cannot be made stable. Not recommended as the primary fix.

---

## 4. Chore scope — C (3 ruff errors on main)

Reproduced in this worktree (`ruff 0.16.9` from `uv.lock`): `uv run ruff check .` → **"Found 3 errors. [*] 3 fixable with the `--fix` option."** All three are the same rule:

| File:line | Rule | Message |
|---|---|---|
| `tests/acceptance/permissions/test_check_api.py:1008` | `I001` | Import block is un-sorted or un-formatted (a blank line splits one `backend.*` block; `backend.permissions` must sort between `mail` and `sessionmanagement`) |
| `tests/acceptance/permissions/test_enforcement.py:222` | `I001` | Import block is un-sorted or un-formatted (`authentication_test_helpers` block must be separated from the `backend.permissions` block) |
| `tests/contract/permissions/test_performance.py:37` | `I001` | Import block is un-sorted or un-formatted (`alembic` block must be separated from the `backend.permissions` block) |

All three are **function-local imports inside test bodies** (`PLC0415` is ignored in `[tool.ruff.lint]`), and the fix is purely ordering/blank-line formatting within one import block — no import is added, removed, or moved across a statement. **Non-behavior (chore): the fix does not change any test's meaning.** No flag needed.

Provenance correction: these errors are **not** introduced by the ruff bump in #55. The identical three errors (`I001` at the same three locations, "Found 3 errors") are in the Lint job of run `36061497656` (merge of PR #52, `crosscut/user-roles-permissions`, 2026-09-24) — i.e. pre-existing lint debt from that change; the last green Lint run on main is `35653895135` (2026-09-21).

---

## 5. Chore scope — D (pip-audit CVEs) and the CI jobs that guard them

Guarding jobs in `.github/workflows/quality.yml`: `security` (`uv run pip-audit` + `uv run bandit -r src/`), `dependencies` (`uv run deptry .`), `dependency-review` (`actions/dependency-review-action@v5`). Plus `lint.yml` (`lint`) and `spec-validation.yml` (`spec-validation`, `tests`).

Status of run `36894698244` (Quality, merge of #56): `migrations` ✅, `type-check` ✅, `docs` ✅, `dependencies` ✅, `coverage` ✅, **`security` ❌**, **`dependency-review` ❌**.

### pip-audit (job `security`, run `36894698244`) — "Found 11 known vulnerabilities in 2 packages"

| Package | Version | Advisory | Fix version |
|---|---|---|---|
| `urllib3` | 2.7.0 | CVE-2026-97687, CVE-2026-97688, CVE-2026-97689 | 2.8.0 |
| `virtualenv` | 21.3.3 | PYSEC-2026-4011 | 21.7.12 |
| `virtualenv` | 21.3.3 | PYSEC-2026-4012 | 21.7.11 |
| `virtualenv` | 21.3.3 | PYSEC-2026-4013 | 21.7.13 |
| `virtualenv` | 21.3.3 | PYSEC-2026-4014 | 21.7.12 |

(The orchestrator's list omitted PYSEC-2026-4013/-4014; the CI table lists each advisory twice from two sources, hence "11" rows over 4 distinct virtualenv advisories.)

### Direct vs. transitive (`uv tree --invert`)

- `urllib3 2.7.0` ← `requests 2.34.2` ← {`cachecontrol[filecache] 0.14.4` ← `pip-audit 2.10.1`, `mkdocs-material 9.7.7`, `pip-audit 2.10.1`} ← **dev group**.
- `virtualenv 21.3.3` ← `pre-commit 4.6.2` ← **dev group**.

**Neither is a direct dependency** — `pyproject.toml` declares neither. Both are transitive **dev-group** packages, and `pip-audit` scans the dev environment, so dev-only transitives are gated.

### Intended remedy (Phase 4)

Transitive bumps only — no `pyproject.toml` change needed. Verified with a dry run in this worktree:

```bash
uv lock --upgrade-package urllib3 --upgrade-package virtualenv --dry-run
# Update urllib3 v2.7.0 -> v2.8.0
# Update virtualenv v21.3.3 -> v21.14.3
# Update python-discovery v1.3.1 -> v1.6.1
```

Then re-run `uv run pip-audit` (the `security` job's command) to confirm zero findings, and `uv run deptry .` (the `dependencies` job) to confirm the dependency check stays clean. Only if the resolver cannot reach the fixed versions (a pin from an intermediate requirement) add a `[tool.uv] constraint-dependencies` entry — `override-dependencies` only with a recorded justification, since it silently breaks the resolver's guarantees.

---

## 6. Items E and F — IN SCOPE (Q-127 answered 2026-10-02)

### 6.0 Items A and B do not fail in CI (the reason E exists)

The triage MUST record this: **items A and B do not fail in CI.** In run `36894698181` (`Spec Validation` → `tests`, `uv run pytest tests/ -v`) both are logged PASSED:

```text
tests/property/settings/test_settings_properties.py::test_inv_009_yaml_roundtrip PASSED [ 51%]
tests/property/usermanagement/test_multi_role_invariants.py::test_last_admin_invariant PASSED [ 51%]
```

### 6.1 E — the defect: mechanism and observed behavior (confirmed, no longer a hypothesis)

```text
run 36894698181: 2 failed, 633 passed
  tests/integration/logging/test_logging_integration.py::test_stdlib_loguru_decorator_pipeline - AssertionError: assert False
  tests/unit/logging/test_logging_edges.py::test_edge_005_intercept_unknown_level - assert []
run 36894698244-adjacent 36894649854: 4 failed   (+ test_ac_004_intercept_handler_routes_records, test_ac_005_intercept_handler_skips_bootstrap)
run 36894622789 (#55): 4 failed (same family)     run 36061497823 (#52, 2026-09-24): 4 failed (same family)
run 36175233161 (#53, 2026-09-25): 6 failed       (also test_ac_001_setup_logger_adds_sinks)
```

Current CI state on the base commit (re-verified with `gh run view 36894698181 --log-failed`, `Spec Validation` → `tests`, `uv run pytest tests/ -v`, head `75ca243`): **2 failed, 633 passed** — exactly the two nodes listed above.

Mechanism, confirmed by direct observation in this worktree:

1. `tests/conftest.py:21-44` performs the one session-scoped `setup_logger()`; the first setup ends with `_subscribe_to_setting_changes()` (`src/backend/logging/_setup.py:116-127`), which registers `_on_setting_changed` on the **shared** event bus.
2. `_configure()` (`src/backend/logging/_setup.py:128-152`) opens with a **blanket `logger.remove()`** — no handler id — which removes **every** loguru handler in the process, including sinks the logging feature never created.
3. Any write to a `logging.*` key on a registry whose events reach the shared bus re-enters `_configure()` **asynchronously on the bus worker thread** (settings-coverage REQ-015 / AC-020).
4. The per-test capture sink installed by the `log_records` fixture (`tests/conftest.py:77-92`) is exactly such a foreign sink (28 test files use the fixture). When the reconfigure lands while one of those tests is running, its sink is gone and the test's capture list stays empty — the CI signature `assert []` / `AssertionError: assert False`.

Deterministic in-process reproduction (run from this worktree against `75ca243`; a standalone script, since Phase 1 must not add test files):

```bash
PYTHONPATH="src;tests" uv run python <repro-script>
# sink added, id=3, handlers_before=[1, 2, 3]        # 1=console, 2=file (added by _configure), 3=log_records capture sink
# registry.set_value("logging.log_level", "INFO")    # the offender's call
# capture sink removed by reconfigure: True
# handlers_after=[4, 5]                              # new console + file; the capture sink is gone
# records captured: [… only records emitted BEFORE the removal …]   # "probe-after-reconfigure" never arrives
# REPRODUCED: the logging feature's reconfigure dropped a sink it does not own
```

3/3 runs reproduce on the current code; 3/3 runs do **not** reproduce against the re-homed fix (§6.5). The same script also shows the file/console sinks being re-added (`[1,2]` → `[4,5]`), i.e. the feature churns its own sinks while silently destroying someone else's.

**Offender inventory** — in-process publishers of a `logging.*` key on the shared bus, after the logging subscription exists (the brief listed two; there are **three**):

| Publisher | Key | Note |
|---|---|---|
| `tests/contract/filemanagement/test_filemanagement_contracts.py:93` (restore at `:120`) | `logging.log_level` | inside `test_nfr_001_performance_budgets` |
| `tests/contract/permissions/test_performance.py:56` (restore at `:106`) | `logging.log_level` | inside `test_check_latency_under_5ms_median` |
| `tests/unit/test_settings_coverage.py:338` (`test_sink_reconfigured_rotation`) | `logging.log_max_bytes` | **third offender, omitted by the brief** — it is the trigger of the local 4/5 reproduction in §6.4 |

Explicitly **not** offenders: `tests/integration/settings/test_settings_integration.py:53` builds its `SettingsRegistry` with a **local** `EventBus`, so the logging feature's subscription on the shared bus never sees the event; the `set_value('logging.*', …)` occurrences in `tests/acceptance/settings_coverage/test_setup_logger.py`, `tests/contract/logging/test_logging_contracts.py`, `tests/property/logging/test_logging_properties.py` and `tests/unit/logging/test_logging_edges.py:34-35` are **subprocess** code strings (`run_python`) — different process, no shared bus; `tests/conftest.py:42-43` publishes **before** `setup_logger()` has subscribed (the subscription is installed at the end of the first setup), so it cannot re-enter `_configure()`.

Mapping of the CI failure family to the parts of the fix:

| CI node | mechanism | fix part |
|---|---|---|
| `test_edge_005_intercept_unknown_level`, `test_ac_004_intercept_handler_routes_records`, `test_ac_005_intercept_handler_skips_bootstrap` | the `log_records` capture sink is deleted mid-test | `f25e2ec` (`_SinkState`: remove only managed ids) + its `tests/conftest.py` bus drain |
| `tests/integration/logging/test_logging_integration.py::test_stdlib_loguru_decorator_pipeline` | the enqueued file sink's pending write is not flushed before the 15 s poll; the file sink can also be re-added mid-test | `b1e61ea` (`logger.complete()` in `wait_for_file_content`) + `f25e2ec` |
| `tests/acceptance/logging/test_logging.py::test_ac_001_setup_logger_adds_sinks` | global handler-count assertion + `captured_stderr()` bound to the wrong fd after a worker-thread reconfigure | `f25e2ec` (`_console_sink_fd()` takes the fd from the console sink's own stream) |
| `contract/filemanagement::test_nfr_001_performance_budgets`, `contract/permissions::test_check_latency_under_5ms_median` (`SettingsRegistrationError: duplicate key logging.log_file`) | `install_isolated_registry` restored only `logging.log_file`, leaving a partial `logging.*` state | `e973821` — **not currently red on `main`** (both nodes pass in run `36894698181`); it is the family observed on the `crosscut/search` runs, carried along because the re-homed helper fix is the same file |

### 6.2 E — required behavior per the cited IDs

- **logging REQ-001 / AC-001**: after setup, loguru **has** a console sink on stderr and a rotating file sink with the stated options (presence, with the option contract).
- **logging REQ-002 / AC-002**: a second `setup_logger()` adds no sinks.
- **logging INV-001**: the number of sinks **added** by `setup_logger()` calls is exactly one console + one file.
- **logging REQ-003 / AC-004 / AC-005 / EDGE-005**: a stdlib record is routed into loguru sinks with the correct level/message/origin — observable at the sink the caller installed.
- **settings-coverage REQ-014 / AC-019**: `setup_logger()` is no-arg and reads `logging.*` from the shared registry.
- **settings-coverage REQ-015 / AC-020**: a `logging.*` change **reconfigures the sink** (the feature's own), re-applying all current `logging.*` values.

**Observed deviation:** a `logging.*` write made by an unrelated feature's test deletes the sink another component installed, so the routed record required by AC-004/AC-005/EDGE-005 is no longer observable at that sink, and the feature's own sink set churns (`[1,2]` → `[4,5]`) under a caller that only asked for a level change. The feature mutates global loguru state it does not own.

### 6.3 E — spec-compliance verdict: **COMPLIANT** (no Spec Amendment, no reclassification)

Question: does the logging spec require "the handler set is exactly the two configured sinks" in a way that the fix (remove only the sinks `_configure()` added) violates?

**No — the blanket `logger.remove()` is an implementation detail.** Verified against the spec text, not assumed:

- `grep -rn "handler set|logger.remove|remove()" docs/specs/*.md` → **zero matches**. The sentence "the handler set is exactly the two configured sinks" exists **only in the implementation comment** (`src/backend/logging/_setup.py:130-132`); it is the implementer's gloss on REQ-001/INV-001, not spec text.
- The only normative statement about sink counts is **INV-001**, and it quantifies over "the number of loguru sinks **added**" by `setup_logger()` calls — not over the process-global handler set. Removing only the feature's own sinks keeps exactly one console + one file added per configure/reconfigure.
- **REQ-001 / AC-001** require the **presence** of the two configured sinks with the stated options; neither forbids another component from registering its own loguru sink, and neither requires its removal.
- **REQ-015** (settings-coverage) says the feature "reconfigures **the sink**" (singular — its own) and "re-appl[ies] all current `logging.*` values"; the fix does exactly that, and is at least as faithful a reading as removing every sink in the process.
- `grep -n "exactly" docs/specs/logging.md docs/specs/logging-coverage.md docs/specs/settings-coverage.md` returns only AC-003 (one thread wins), INV-001 (sinks added), logging-coverage REQ-011/D5 (`setup_logger` called once at startup) and INV-001 of logging-coverage (one entry + one exit record) — none of them mandates a two-sink global set.

The fix therefore preserves every specified property: the first `_configure()` call still removes loguru's **default** sink (its only spec-anchored purpose), later calls remove only the ids `_configure()` added (`ValueError` suppressed for sinks already removed externally) and re-add exactly one console + one file sink. Nothing specified is removed and nothing unspecified is added → the AGENTS prohibition "introduce behavior not represented in the specification" is not triggered, and the change stays **ISSUE** (a defect fix), not a spec amendment.

**Note for S6.2 (traceability/test-coupling, not a test change):** two tests assert the **process-global** handler count — `tests/unit/logging/test_logging.py:22,46` (`_EXPECTED_HANDLER_COUNT = 2`) and `tests/acceptance/logging/test_logging.py:26` — which is stricter than INV-001's wording ("sinks added"). They pass under the fix as long as no foreign sink is registered at that moment and no reconfigure races mid-test. They MUST NOT be weakened; if a future change registers a process-wide sink, those assertions become order-coupled and belong in a separate change.

**Note for S5.3/S6.2 (traceability drift, not a behavior issue):** `src/backend/logging/_setup.py` cites "AC-019"/"AC-020" in its comments for the registry read and the runtime reconfiguration; those IDs exist in `docs/specs/settings-coverage.md` (AC-019/AC-020), **not** in `docs/specs/logging.md` or `docs/specs/logging-coverage.md` — the citations are ambiguous as written and should name the spec file. Likewise `docs/specs/logging.md:133-155` binds AC-001/AC-004/AC-005/EDGE-005 to `tests/acceptance/test_logging.py` / `tests/unit/test_logging.py`, while the implemented tests live in `tests/acceptance/logging/test_logging.py`, `tests/unit/logging/test_logging.py` and `tests/unit/logging/test_logging_edges.py`. Fix the matrix rows in S5.3; do not move tests.

### 6.4 E — deterministic reproduction (and why an ordering recipe is not one)

Ordering recipe (fixed collection order, `-p no:randomly`) — **reproduces 4/5, i.e. NOT deterministic**:

```bash
uv run pytest tests/unit/test_settings_coverage.py::test_sink_reconfigured_rotation \
  tests/unit/logging/test_logging.py tests/unit/logging/test_logging_edges.py -p no:randomly -q
# run 1: 1 failed, 17 passed   FAILED tests/unit/logging/test_logging.py::test_ac_003_setup_logger_thread_safe
# run 2: 1 failed, 17 passed   FAILED (same node)
# run 3: 18 passed
# run 4: 1 failed, 17 passed   FAILED (same node)
# run 5: 1 failed, 17 passed   FAILED (same node)
```

`-p no:randomly` pins the collection order but not the moment the bus worker dispatches the queued `SettingChanged`, so the failure stays a race; a fixed `pytest-randomly` seed cannot pin it either. (The node this recipe reddens, `test_ac_003_setup_logger_thread_safe`, is the same root cause seen from the other side: the reconfigure races the 8 concurrent `setup_logger()` threads and the global handler-count assertion. It is a **different node from CI's four**, which is why the brief's "run the offending contract test, then the logging nodes" recipe is recorded here as corroboration, not as the contract.)

**The deterministic reproduction is in-process and order-free** (§6.1): install a capture sink → write a `logging.*` value → wait for the reconfigure to be dispatched → assert the capture sink still receives a record emitted afterwards. 3/3 RED on `75ca243`, 3/3 GREEN with the re-homed fix. Phase 3 writes exactly this as a test (§7, item E).

### 6.5 E — fix scope and the re-home plan (cherry-pick)

Files: `src/backend/logging/_setup.py` (1 source file) + `tests/conftest.py`, `tests/logging_test_helpers.py`, `tests/settings_test_helpers.py` (3 test helpers).

Phase 4 re-home: **`git cherry-pick b1e61ea f25e2ec e973821`** onto `issue/main-ci-green`.

**Correction to the brief (important).** The brief names only `f25e2ec` and `e973821`. That two-commit sequence does **not** apply:

```bash
git show f25e2ec | git apply --check   # error: tests/logging_test_helpers.py: patch does not apply
git show e973821 | git apply --check   # error: tests/settings_test_helpers.py: patch does not apply
```

Both helper files were themselves changed on `crosscut/search` by **`b1e61ea`** ("test(logging): make enqueued-sink waits and registry isolation deterministic", 2026-09-28), which is **not on `main`** and is a **prerequisite**: `e973821` rewrites the `install_isolated_registry` behavior `b1e61ea` introduced, and `b1e61ea`'s `logger.complete()` drain in `wait_for_file_content` is the fix for the `test_stdlib_loguru_decorator_pipeline` CI failure. The re-home is therefore **three** commits, not two.

Conflict analysis — the brief's premise is half right. Main's 7 commits since the merge-base touch **none** of the four files:

```bash
git log --oneline be838ef..75ca243 -- tests/conftest.py tests/settings_test_helpers.py \
  tests/logging_test_helpers.py src/backend/logging/_setup.py
# (empty — be838ef = git merge-base origin/main crosscut/search)
```

so there is no main-side conflict; the divergence is entirely on the **search side** (`b1e61ea`), which is exactly why the third commit is required.

Verified conflict-free in a throwaway `git clone --shared` in a temp directory (the change branch, the search branch and every worktree were left untouched; the clone was deleted afterwards):

```bash
git checkout -b sim 75ca243
git cherry-pick b1e61ea f25e2ec e973821     # 3 commits applied, zero conflicts
# and, for each of the four files:
#   git rev-parse HEAD:<f> == git rev-parse origin/crosscut/search:<f>   → IDENTICAL
```

i.e. the re-homed result is **byte-identical** to the search branch's version of all four files, and the fix was re-verified against the deterministic reproduction (§6.1: 3/3 NOT REPRODUCED).

`crosscut/search` is **not modified** by this change (read-only per the step's constraints). When it later rebases onto the fixed `main`, these three commits become duplicates and drop out; PR #54 becomes search-only (user decision recorded in Q-127).

### 6.6 F — the `dependency-review` job cannot pass on `push`

Evidence (re-verified with `gh`):

```bash
gh run view 36894698244 --json name,headSha,jobs
# Quality @ headSha 75ca243: dependency-review=failure, security=failure; migrations/type-check/docs/dependencies/coverage=success
gh run view 36894698244 --log-failed | grep error
# ##[error]Both a base ref and head ref must be provided, either via the `base_ref`/`head_ref` config
# options, `base-ref`/`head-ref` workflow action options, or by running a
# `pull_request`/`pull_request_target`/`merge_group` workflow.
```

Exact wiring (`.github/workflows/quality.yml`): `on:` at line 3 with `pull_request: branches: [ main ]` (lines 4–5) and `push: branches: [ main ]` (lines 6–7); the `dependency-review` job is declared at line 61 and uses `actions/dependency-review-action@v5` at line 74. `grep -rn "dependency-review" .github/` matches only those two lines — it is the only job in the repository that needs a PR context. On a push there is no base/head pair, so the job fails **by construction**: `main` can never be green while that job runs on push. (`lint.yml` and `spec-validation.yml` also run on `push`, but contain no such job.)

Remedy (CI chore, one file, `.github/workflows/quality.yml`):

1. **Recommended — gate the job:** add `if: github.event_name != 'push'` to the `dependency-review` job (one added line; the job stays next to the other dependency jobs and still runs on every PR).
2. Alternative — move the job to a new `.github/workflows/dependency-review.yml` with `on: pull_request` (larger diff, no functional gain; the repository has no merge queue, so `merge_group` is not needed).

Risk check: a skipped job cannot block a merge — `gh api repos/jackthenet/python-template/branches/main/protection` → **404 (no branch protection configured)**, so there is no required-check list that a skipped context could stall.

Classification: **chore** (CI configuration; no externally observable product behavior changes; no REQ/AC affected). No test is possible — verification is CI evidence: the PR run must show `dependency-review` executed, and the post-merge push run on `main` must show it skipped. The second half is observable only after merge and MUST be recorded in the review report (S6.3/S6.4).

### 6.7 Consequence for the change objective

With A–F, every red job on `main` is addressed: `tests` (E), `security` (D), `dependency-review` (F), `lint` (C). A and B are local-side defects that the same change fixes so the suite is deterministic off CI as well.

---

## 7. Reproduction plan (Phase 3) — items A–F

Phase 3 writes new tests for **A** and **E** (the two defects with a deterministic, order-free reproduction). **B**'s RED is the pinned-seed `DeadlineExceeded` on an existing test (no new test). **C**, **D** and **F** are chores: no RED, no new test — their evidence is the command output recorded in this file.

### Item A — reproduction test (deterministic, no `.hypothesis` dependency)

New tests, written before the fix, that must FAIL on current code:

1. **Unit/property regression test pinning the exact counterexample** — `tests/unit/settings/test_repository_roundtrip.py::test_yaml_template_roundtrip_nel` (new file): build `Template(name="prof", category="app", group=None, values={"app.a": "\x85"})`, `YamlTemplateRepository(tmpdir).save(t)`, `get("prof")`, assert equality; plus an explicit assertion on the written document (the value must be emitted in an escaped/double-quoted form, e.g. the file text contains `"\N"`, not a bare NEL byte).
2. **Value-repository counterpart** — `tests/unit/settings/test_repository_roundtrip.py::test_yaml_value_roundtrip_nel`: `YamlValueRepository(tmpdir).save({"app.list": ["\x85", "ok"]})` then `load()` returns the identical mapping (settings-coverage INV-002).
3. **Property test that does not depend on the example database** — extend/keep `test_inv_009_yaml_roundtrip` and add `test_inv_009_yaml_roundtrip_value_repository` for the value path, with the strategy explicitly including U+0085 (e.g. `st.text(alphabet=st.characters(blacklist_categories=("Cs",)) )` or `st.sampled_from` mixed in) so the character is always exercised rather than discovered by chance.
4. **Determinism guard:** the pinned unit tests (1–2) are the reproduction; they must fail with a fresh `.hypothesis` directory and with `--hypothesis-seed=0`.

RED command (targeted): `uv run pytest tests/unit/settings/test_repository_roundtrip.py -v` → must fail on behavior (assertion on the loaded value, not a `ValidationError`).

Fix scope / files expected to change: **`src/backend/settings/repository.py`** (`_dump_yaml`, possibly `_load_yaml` untouched) — one implementation file. Tests: `tests/unit/settings/test_repository_roundtrip.py` (new), `tests/property/settings/test_settings_properties.py` (strategy hardening).

### Item B — making the test deterministic

Reproduction: `uv run pytest tests/property/usermanagement/test_multi_role_invariants.py::test_last_admin_invariant -p no:randomly --hypothesis-seed=101` → `DeadlineExceeded` (355.59 ms).

Phase 3 records the RED as the deadline failure at a pinned seed; Phase 4 applies the **decided** fix (Q-128) — `@settings(deadline=1000)` plus an explanatory comment recording the measured distribution (246–356 ms) and the argon2id per-example cost (ADR-019) — and re-runs the **same pinned seeds** (7, 101, 2024) plus the default profile. The invariant assertion, the strategy, `max_size=10` and `max_examples=20` stay unchanged (shrinking `max_size` was rejected as a real weakening of INV-003 coverage). Files expected to change: **`tests/property/usermanagement/test_multi_role_invariants.py`** only.

### Item C — chore

`uv run ruff check --fix tests/acceptance/permissions/test_check_api.py tests/acceptance/permissions/test_enforcement.py tests/contract/permissions/test_performance.py` (scoped to the three paths, per the AGENTS ruff-gate rule), then `uv run ruff check .` clean at Phase 5. Files expected to change: the three test files (import blocks only). Confirm the three tests still pass unchanged afterwards.

### Item D — chore

`uv lock --upgrade-package urllib3 --upgrade-package virtualenv`; verify with `uv run pip-audit` (zero findings) and `uv run deptry .` (clean). Files expected to change: **`uv.lock`** (no `pyproject.toml` change unless the resolver needs a constraint).

### Item E — reproduction test (deterministic, order-free)

New file `tests/unit/logging/test_logging_sink_ownership.py` (the §6.1 mechanism as executable tests):

1. `test_reconfigure_keeps_foreign_sinks` — **Given** the session's real logging setup and a capture sink added the way `tests/conftest.py::log_records` adds one, **When** a `logging.*` value is written on the shared registry and the reconfiguration has been dispatched (awaited with `settings_test_helpers.wait_for`, never a sleep), **Then** a record emitted afterwards still reaches that capture sink. RED on `75ca243`: the sink is deleted by `_configure()`'s blanket `logger.remove()` and the capture list stays empty (3/3 in the §6.1 script).
2. `test_reconfigure_keeps_one_console_and_one_file_sink` — guards INV-001 / REQ-001 / AC-001 **under** the fix: after a `logging.*` change the logging feature's own sink set is still exactly one console + one file sink (so the fix cannot regress into "re-add without removing").
3. `test_first_configure_removes_loguru_default_sink` — pins the spec-anchored half of the behavior the fix **keeps** (loguru's default sink is gone after the first configure), so the fix is provably not "never remove".

RED command (targeted, run **before** the cherry-pick): `uv run pytest tests/unit/logging/test_logging_sink_ownership.py -v` → must fail on behavior (empty capture / missing sink), not on an import or fixture error.

Must stay GREEN under the fix (existing spec evidence, do not touch): `tests/acceptance/settings_coverage/test_setup_logger.py::test_sink_reconfigured_on_change` — the spec-mandated AC-019/AC-020 evidence, which asserts that the handler level set follows a `logging.*` change (subprocess-isolated, so it is unaffected by the pollution but it is the behavior the fix must preserve).

Corroboration only (NOT the contract, see §6.4): `uv run pytest tests/unit/test_settings_coverage.py::test_sink_reconfigured_rotation tests/unit/logging/test_logging.py tests/unit/logging/test_logging_edges.py -p no:randomly -q` → `test_ac_003_setup_logger_thread_safe` failed 4/5 locally.

Phase 4 (GREEN): `git cherry-pick b1e61ea f25e2ec e973821` (§6.5), then re-run the new file, the whole logging family (`uv run pytest tests/unit/logging tests/integration/logging tests/acceptance/logging tests/contract/logging -v`), and the §6.4 recipe (expected 5/5 clean). Files expected to change: `src/backend/logging/_setup.py`, `tests/conftest.py`, `tests/logging_test_helpers.py`, `tests/settings_test_helpers.py` (all via the cherry-pick) + the new test file.

### Item F — chore (no test, no RED)

Change `.github/workflows/quality.yml`: add `if: github.event_name != 'push'` to the `dependency-review` job (§6.6). Verification is CI evidence, not a test: the PR run must show the job executed, the post-merge push run on `main` must show it skipped. Record both in the verification/review artifacts; the second is observable only after merge.

---

## 8. Light-tier assessment (AGENTS.md "Light ISSUE tier")

Qualification requires **all** of: single feature; fix touches ≤ 3 files excluding tests; no new dependency, no new public interface, no cross-feature change.

- Single feature: **no.** A is `backend/settings`; B is `backend/usermanagement` (test-only); C is `tests/{acceptance,contract}/permissions`; D is the dependency manifests; **E is `backend/logging` + three shared test helpers**; **F is CI configuration** (`.github/workflows/`).
- ≤ 3 files excluding tests: **no** (A: 1 source file; D: `uv.lock`; F: 1 workflow file; E: 1 source file + 3 test helpers).
- No new dependency / public interface / cross-feature change: **no** (D changes dependency versions; E changes the shared logging feature's reconfiguration behavior and the shared test helpers used by 28 test files).

**Conclusion: this change does NOT qualify for the Light ISSUE tier** (it did not qualify even at four items; the six-item scope makes it unambiguous). Phase 5 therefore runs the **full ISSUE gate set**:

```bash
uv run pytest tests/ -v            # reproduction tests GREEN + full regression, no new failures
uv run pytest tests/unit/logging tests/integration/logging tests/acceptance/logging tests/contract/logging -v   # E's family
uv run ruff check .                # whole-repo sweep (matches CI lint.yml)
uv run mypy src/                   # type gate
uv run pip-audit                   # D's job command (security)
uv run deptry .                    # dependency check after the lock change
```

plus the traceability matrix updated with the issue's evidence rows (A: settings INV-002/INV-009; E: logging REQ-001/003, AC-001/004/005, EDGE-005, settings-coverage REQ-015/AC-020). F's evidence is CI-side (post-merge push run) and is recorded in the review report.

---

## 9. State machine

Entry state: **`TESTS_WRITTEN`** (ISSUE entry, after triage). Next step: **S3.1** (write the reproduction tests for A and E from §7, record B's pinned-seed RED, and confirm RED).

---

## 10. Questions (both ANSWERED — recorded in `AI_Questions.md`, incorporated)

- **Q-127 — ANSWERED (2026-10-02): E and F are IN scope.** E is **re-homed** from `crosscut/search` into this change (`b1e61ea` + `f25e2ec` + `e973821`, see §6.5 — the brief listed two commits; the third is a prerequisite), and `crosscut/search` drops those commits when it rebases onto the fixed `main`, making PR #54 search-only. PR #54 stays open and is held until `main-ci-green` is merged and the rebase is done. Consequence: main's `tests` job goes green with this change.
- **Q-128 — ANSWERED (2026-10-02): option 1, an explicit measured `@settings(deadline=1000)` with an explanatory comment.** Shrinking `max_size` was rejected (argon2id per-example cost, ADR-019: a `max_size=4` sequence would still land at ~150–200 ms and would shrink the operation-interleaving space INV-003 coverage depends on — a real weakening). `max_size=10`, `max_examples=20`, the strategy and the invariant assertion are untouched.

Both entries carry the full answer text, the generating step, the context and the "incorporated: yes" flag in `AI_Questions.md` (repo root). No new question arose in the S1.1 re-run: the two open decisions were the scope boundary and the B fix policy, and both are now settled; E's spec-compliance question was answerable from the spec text alone (§6.3), so it needed no user input.

---

## 11. Corrections to the S1.1 re-run brief (verified, not restated)

The re-run brief was checked command-by-command. Four corrections:

1. **The cherry-pick is three commits, not two.** The brief listed `f25e2ec` + `e973821`; that sequence does not apply (`git apply --check` fails on `tests/logging_test_helpers.py` and `tests/settings_test_helpers.py`). `b1e61ea` (search branch, 2026-09-28) is the prerequisite for both — it introduced the `install_isolated_registry` behavior `e973821` rewrites, and its `logger.complete()` drain in `wait_for_file_content` is the fix for the `test_stdlib_loguru_decorator_pipeline` CI failure. `git cherry-pick b1e61ea f25e2ec e973821` onto `75ca243` applies with zero conflicts and yields byte-identical blobs to `crosscut/search` for all four files (§6.5).
2. **The brief's conflict premise is half right.** "The search branch's `tests/conftest.py` / helpers are otherwise untouched by main's 7 new commits" is true (`git log --oneline be838ef..75ca243 -- <the four files>` is empty), but it is the *search-side* divergence (`b1e61ea`) that breaks the two-commit pick — so "no expected conflict" was the wrong conclusion.
3. **The ordering-based reproduction is not deterministic.** The brief proposed a fixed `pytest-randomly` seed or a two-file invocation. Measured: the two-file invocation with `-p no:randomly` reddens `test_ac_003_setup_logger_thread_safe` in **4 of 5** runs (§6.4) — the failure depends on when the bus worker dispatches the queued event, so no seed pins it. The deterministic reproduction is the in-process, order-free one in §6.1 (3/3 RED on `75ca243`, 3/3 clean with the fix), and that is what Phase 3 turns into a test.
4. **There are three in-process offenders, not two.** The brief named `tests/contract/filemanagement/test_filemanagement_contracts.py:93` and `tests/contract/permissions/test_performance.py:56`; `tests/unit/test_settings_coverage.py:338` (`test_sink_reconfigured_rotation`, `logging.log_max_bytes`) is a third, and it is the one that reproduces locally. Conversely `tests/integration/settings/test_settings_integration.py:53` is **not** an offender (local `EventBus`), and the `logging.*` writes in the acceptance/contract/property/unit-logging files are subprocess code (§6.1).

Confirmed as stated by the brief: the E/F scope decision (Q-127), the B fix policy (Q-128), the `dependency-review` error text and the failing job (`gh run view 36894698244`), the current CI `tests`-job failure set (2 failed on `75ca243`), the spec IDs for E (logging REQ-001/002/003, AC-001/002/004/005, INV-001, EDGE-005; settings-coverage REQ-014/015, AC-019/020), and the COMPLIANT verdict for E (re-derived independently in §6.3).

Base note: this branch's base is `origin/main` @ `75ca243`. Local `main` has since moved to `0d2720f` ("chore(workflow-optimization)…", skills/AGENTS/PROBLEMS only — no `src/`, no `tests/`, no workflow files), which does not affect any item's scope or the cherry-pick.

---

## Phase 3 (S3.1) — reproduction tests, RED confirmed (2026-10-02)

Two new test files (items A and E). No `src/` change, no existing test touched, no cherry-pick (Phase 4).

### Files added

- `tests/unit/settings/test_repository_roundtrip.py` — item A (settings YAML persistence round-trip, U+0085 NEL)
- `tests/unit/logging/test_logging_sink_ownership.py` — item E (loguru sink ownership across a settings-driven reconfigure)

### RED gate (targeted, verbatim)

```bash
uv run pytest tests/unit/settings/test_repository_roundtrip.py tests/unit/logging/test_logging_sink_ownership.py -q -p no:randomly --tb=no
```

```text
FFFF.                                                                    [100%]
=========================== short test summary info ===========================
FAILED tests/unit/settings/test_repository_roundtrip.py::test_yaml_value_roundtrip_nel
FAILED tests/unit/settings/test_repository_roundtrip.py::test_yaml_template_roundtrip_nel
FAILED tests/unit/logging/test_logging_sink_ownership.py::test_reconfigure_keeps_foreign_sink
FAILED tests/unit/logging/test_logging_sink_ownership.py::test_reconfigure_replaces_only_the_managed_sinks
4 failed, 1 passed in 5.33s
```

Every failure is an assertion on behavior (no setup error, no `ValidationError`, no collection/import error):

```text
E   AssertionError: assert {'app.a': ' '} == {'app.a': '\x85'}          # test_yaml_template_roundtrip_nel
E   Differing items:
E   {'app.a': ' '} != {'app.a': '\x85'}

E   AssertionError: assert {'app.embedde...pp.text': ' '} == {'app.list': ...ed': 'a\x85b'}   # test_yaml_value_roundtrip_nel
E   Differing items:
E   {'app.list': [' ', 'ok']} != {'app.list': ['\x85', 'ok']}
E   {'app.text': ' '} != {'app.text': '\x85'}
E   {'app.embedded': 'a b'} != {'app.embedded': 'a\x85b'}

E   AssertionError: the reconfigure removed a sink it does not own: records emitted after it are lost
E   AssertionError: the reconfigure removed a sink it does not own
```

### What each new test pins (non-vacuity)

| Test | Pins |
|---|---|
| `test_yaml_value_roundtrip_nel` | `YamlValueRepository.save(values)` → `load()` returns the identical mapping, including a LIST item and an embedded U+0085 (settings-coverage INV-002). |
| `test_yaml_template_roundtrip_nel` | `YamlTemplateRepository.save(t)` → `get(name)` returns a template whose `values` are exactly the stored ones for `{"app.a": "\x85"}` (settings INV-009). |
| `test_reconfigure_keeps_foreign_sink` | A third-party loguru sink (added exactly the way `tests/conftest.py::log_records` adds one) still receives a record emitted **after** a `logging.*`-driven reconfigure (logging REQ-003/AC-004 observability; settings-coverage REQ-015 reconfigures *its own* sink). |
| `test_reconfigure_replaces_only_the_managed_sinks` | After a reconfigure the logging feature's own sink set is exactly one console + one file sink (REQ-001/AC-001/INV-001 — the fix may not "re-add without removing"), **and** the foreign sink id is still installed (the defect). |
| `test_reconfigure_after_external_removal_of_a_managed_sink` | A reconfigure whose managed console sink was removed by someone else still re-establishes exactly one console + one file sink and raises nothing on the event bus worker (no `ValueError` from removing an already-removed id). |

Determinism: pinned literals, no hypothesis, no sleeps (`settings_test_helpers.wait_for`), no timing assertions — sink identity/count and console level only. The reconfigure is driven through the public path (a `logging.log_level` write on the shared registry; the feature's `SettingChanged` subscription reconfigures on the bus worker) and observed by the console sink's level reaching the written value, a signal specific to the test's own write, so a queued reconfigure from another test can never satisfy it. The fixture restores the original level and awaits its reconfigure, so no reconfigure leaks into the next test.

Item E RED stability (defective code, `3cd35cf`): `-p no:randomly` 3/3 runs → `2 failed, 1 passed`; default (randomized) order 10/10 runs → `2 failed, 1 passed`, always the same two nodes. `test_reconfigure_after_external_removal_of_a_managed_sink` is **GREEN on the current code by design** — it is the pin that reddens a naive "remove the ids I remember" fix, and it must stay GREEN under the real one.

Not in S3.1's deliverable set: §7 item A.3 (hardening the `test_inv_009_yaml_roundtrip` strategy so U+0085 is always generated rather than found by chance) — the existing property test stays untouched here; the pinned unit tests are the deterministic reproduction (§7 item A.4).

### Item B — pinned-seed evidence (no new test; fix is Phase 4)

```bash
uv run pytest tests/property/usermanagement/test_multi_role_invariants.py::test_last_admin_invariant -q -p no:randomly --hypothesis-seed=101
# 1 passed in 2.30s
uv run pytest ... --hypothesis-seed=7      # 1 passed in 2.21s
uv run pytest ... --hypothesis-seed=2024   # 1 passed in 2.97s
uv run pytest tests/property/usermanagement/test_multi_role_invariants.py -q -p no:randomly --hypothesis-seed=101
# 1 passed in 2.29s
```

**Finding:** the pinned seeds do **not** reproduce `DeadlineExceeded` on this host today — the failure is load-dependent (the recorded CI/observed per-example cost is 246–356 ms against the 200 ms default deadline, §3). The authoritative RED evidence for B therefore stays the CI record in §3 (`DeadlineExceeded`, 355.59 ms at seed 101 on `75ca243`); B's RED cannot be re-observed on demand locally, which is exactly why the decided fix (Q-128, `deadline=1000`) is a flake fix rather than a behavior fix. No test change made here.

### Ruff (changed paths)

```bash
uv run ruff check tests/unit/settings/test_repository_roundtrip.py tests/unit/logging/test_logging_sink_ownership.py   # All checks passed!
uv run ruff format --check tests/unit/settings/test_repository_roundtrip.py tests/unit/logging/test_logging_sink_ownership.py  # 2 files already formatted
```
