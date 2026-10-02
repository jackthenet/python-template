# ISSUE Triage: main-ci-green

## Type

**ISSUE** — a deviation from approved spec behavior (a defect). No new behavior is introduced.

- **Date:** 2026-10-02
- **Base:** `origin/main` @ `75ca243` ("Merge pull request #56 from jackthenet/dependabot/uv/test-tooling-091a29ec65")
- **Branch:** `issue/main-ci-green`
- **Worktree:** `C:/workspace/active-projects/python-template_kopie-worktrees/issue/main-ci-green`
- **Why this change exists:** `main`'s CI is red after three merged dependabot PRs (#55 lint-and-types, #56 test-tooling, #57 runtime-core). The user decided to fix `main` in one dedicated change before PR #54 (crosscut/search) merges into it.

### Scope composition (user-approved four items)

| Item | Nature | Classification inside this change |
|---|---|---|
| **A** | settings YAML round-trip loses `'\x85'` (NEL) | **the defect that makes this an ISSUE** (deviation from `docs/specs/settings.md` INV-009) |
| **B** | hypothesis `DeadlineExceeded` in `test_last_admin_invariant` | test-infrastructure defect (no product-behavior deviation — see "Defect confirmation B / Classification note") |
| **C** | 3 ruff `I001` errors on `main` | non-behavior **chore** riding along (user decision) |
| **D** | pip-audit CVEs in two transitive dev dependencies | non-behavior **chore** riding along (user decision) |

Items C and D alter no externally observable behavior; they ride along by user decision. A is the ISSUE core. B is a test-harness defect (the specified invariant itself still holds).

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

Both nodes **pass** in CI (see §5, item E) — they are local-side defects; the CI test-job failures are a different family (logging interception).

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

### Items C and D

No REQ/AC is affected: C is a lint-only import-ordering change in three test files, D is a dependency-manifest change. Both are non-behavior (chore) scope.

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

### Fix options (Phase 4 decides; recommendation stated, not implemented)

1. **Recommended — explicit, measured `deadline` on the test's `@settings`** (e.g. `deadline=1000`), justified by the measured distribution (246–356 ms observed for the slowest examples on this machine, i.e. the 200 ms default has no headroom) and recorded in the verification artifact. The invariant, the strategy, and the assertion stay byte-identical — nothing is weakened; only the harness tolerance is made explicit and machine-independent.
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

## 6. Scope gap found during triage (E, F) — the CI test job is red for a different reason

The triage MUST record this: **items A and B do not fail in CI.** In run `36894698181` (`Spec Validation` → `tests`, `uv run pytest tests/ -v`) both are logged PASSED:

```text
tests/property/settings/test_settings_properties.py::test_inv_009_yaml_roundtrip PASSED [ 51%]
tests/property/usermanagement/test_multi_role_invariants.py::test_last_admin_invariant PASSED [ 51%]
```

### E — logging-interception test family (the actual CI test-job failure)

```text
run 36894698181: 2 failed, 633 passed
  tests/integration/logging/test_logging_integration.py::test_stdlib_loguru_decorator_pipeline - AssertionError: assert False
  tests/unit/logging/test_logging_edges.py::test_edge_005_intercept_unknown_level - assert []
run 36894698244-adjacent 36894649854: 4 failed   (+ test_ac_004_intercept_handler_routes_records, test_ac_005_intercept_handler_skips_bootstrap)
run 36894622789 (#55): 4 failed (same family)     run 36061497823 (#52, 2026-09-24): 4 failed (same family)
run 36175233161 (#53, 2026-09-25): 6 failed       (also test_ac_001_setup_logger_adds_sinks)
```

Affected spec IDs — `docs/specs/logging.md`: **REQ-003** (*"The logging feature provides an `_InterceptHandler` that routes stdlib `logging` records into loguru sinks, skipping frozen importlib bootstrap frames."*), **AC-004**, **AC-005**, **EDGE-005** (*"Stdlib `logging` record with a level not recognized by loguru | Record is routed using the numeric level number instead of the name."*), **REQ-001** (the mandated sink set), **REQ-002** (*"`setup_logger()` is idempotent: subsequent calls are no-ops."*); and `docs/specs/settings-coverage.md`: **REQ-014** (*"`setup_logger()` takes no arguments and reads `logging.*` from the shared registry … It is idempotent (a second call is a no-op)."*), **REQ-015** (*"The logging feature subscribes to `SettingChanged` and reconfigures the sink at runtime when any `logging.*` setting changes, re-applying all current `logging.*` values."*) — REQ-015 is the mechanism the interference runs through.

Traceability drift noted (for S5.3/S6.2, not a behavior issue): `src/backend/logging/_setup.py` cites "AC-019"/"AC-020" for the registry read and the runtime reconfiguration, but no such IDs exist in `docs/specs/logging.md` or `docs/specs/logging-coverage.md`; the normative source is `docs/specs/settings-coverage.md` REQ-014/REQ-015. Likewise `docs/specs/logging.md:136-155` binds AC-004/AC-005/EDGE-005 to `tests/unit/test_logging.py`, while the implemented tests live in `tests/unit/logging/test_logging.py` and `tests/unit/logging/test_logging_edges.py`.

Evidence-backed root-cause hypothesis (for Phase 3/4 to confirm, not established here): `tests/conftest.py:20-44` performs one session-scoped `setup_logger()`; `setup_logger()` subscribes to `SettingChanged` and re-runs `_configure()` on any `logging.*` change (`src/backend/logging/_setup.py:112-124`, AC-020), and `_configure()` calls `logger.remove()` — which drops **all** loguru sinks, including the per-test capture sink added by the `log_records` fixture (`tests/conftest.py:77-95`). Tests that mutate a `logging.*` value (`tests/contract/filemanagement/test_filemanagement_contracts.py:93`, `tests/contract/permissions/test_performance.py:56`) therefore remove other tests' sinks — asynchronously (event-bus worker) and only when the order is unlucky, which is exactly the run-to-run variance observed. All four nodes pass locally in isolation and in a logging-only run (verified: `uv run pytest tests/unit/logging tests/integration/logging -q` → 18 passed, 3/3 repeats).

### F — `dependency-review` can never pass on a push to main

```text
run 36894698244, job dependency-review:
##[error]Both a base ref and head ref must be provided, either via the `base_ref`/`head_ref` config
options, `base-ref`/`head-ref` workflow action options, or by running a
`pull_request`/`pull_request_target`/`merge_group` workflow.
```

`actions/dependency-review-action@v5` is wired into the `Quality` workflow, which also runs on `push` to `main`. On a push there is no base/head pair, so the job fails by construction — `main` can never be green while that job runs on push. Remedy is a CI-config change (run it only on `pull_request`/`merge_group`, e.g. split it into a PR-only workflow or add an `if:` guard). Non-behavior (chore).

**Consequence:** with the user-approved scope A+B+C+D only, `main`'s CI stays red (the `tests` job and the `dependency-review` job still fail). E and F are recorded here as a scope gap and raised as **Q-127**.

---

## 7. Reproduction plan (Phase 3)

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

Phase 3 records the RED as the deadline failure at a pinned seed; Phase 4 applies fix option 1 (explicit measured `deadline` in `@settings`) and re-runs the **same pinned seeds** (7, 101, 2024) plus the default profile — the invariant assertion, the strategy, and `max_examples` stay unchanged (no weakening). Files expected to change: **`tests/property/usermanagement/test_multi_role_invariants.py`** only.

### Item C — chore

`uv run ruff check --fix tests/acceptance/permissions/test_check_api.py tests/acceptance/permissions/test_enforcement.py tests/contract/permissions/test_performance.py` (scoped to the three paths, per the AGENTS ruff-gate rule), then `uv run ruff check .` clean at Phase 5. Files expected to change: the three test files (import blocks only). Confirm the three tests still pass unchanged afterwards.

### Item D — chore

`uv lock --upgrade-package urllib3 --upgrade-package virtualenv`; verify with `uv run pip-audit` (zero findings) and `uv run deptry .` (clean). Files expected to change: **`uv.lock`** (no `pyproject.toml` change unless the resolver needs a constraint).

### Items E / F — pending the scope decision (Q-127)

If in scope: E's reproduction test is a deterministic ordering reproduction (run the triggering test and the affected logging tests in the failing order, e.g. `uv run pytest tests/contract/permissions/test_performance.py tests/unit/logging -p no:randomly`, or a dedicated isolation test asserting the `log_records` sink survives a `logging.*` change); fix candidates are test-side (isolate/re-register the capture sink, or stop mutating shared `logging.*` values in contract tests) or feature-side (make `_configure` re-entrant without dropping third-party sinks — needs care with logging REQ-001/AC-001's mandated sink set). F's fix is `.github/workflows/quality.yml` (job trigger guard) — no test.

---

## 8. Light-tier assessment (AGENTS.md "Light ISSUE tier")

Qualification requires **all** of: single feature; fix touches ≤ 3 files excluding tests; no new dependency, no new public interface, no cross-feature change.

- Single feature: **no.** A is `backend/settings`; B is `backend/usermanagement` (test-only); C is `tests/{acceptance,contract}/permissions`; D is the dependency manifests; E (if in scope) is `backend/logging` + `tests/conftest.py`; F is CI config.
- ≤ 3 files excluding tests: **no** (A: 1 source file; D: `uv.lock`; F: workflow file; E: source + conftest).
- No new dependency / public interface / cross-feature change: **no** (D changes dependency versions; E would touch shared logging behavior).

**Conclusion: this change does NOT qualify for the Light ISSUE tier.** Phase 5 must run the full gate set for the ISSUE path — reproduction tests GREEN, **full regression suite** with no new failures, `uv run ruff check .`, `uv run mypy src/` — and the traceability matrix updated with the issue's evidence rows. (The full regression suite is required anyway because the CI `tests` job is the thing being fixed.)

---

## 9. State machine

Entry state: **`TESTS_WRITTEN`** (ISSUE entry, after triage). Next step: **S3.1** (write the reproduction tests from §7 and confirm RED).

---

## 10. Open questions

- **Q-127** — scope: must `main-ci-green` also fix E (the logging-interception test family that actually fails CI's `tests` job) and F (`dependency-review` failing by construction on push), or is the change deliberately limited to A+B+C+D (leaving main red)?
- **Q-128** — item B fix policy: is an explicit measured `@settings(deadline=…)` on `test_last_admin_invariant` acceptable (harness tolerance only; invariant, strategy and example count unchanged), or does the user require the per-example work to be reduced instead?

Both recorded in `AI_Questions.md` (repo root), status OPEN/PENDING.
