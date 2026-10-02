# ISSUE Triage: main-ci-green

## Type

**ISSUE** — a deviation from approved spec behavior (a defect). No new behavior is introduced.

- **Date:** 2026-10-02
- **Base:** `origin/main` @ `75ca243` ("Merge pull request #56 from jackthenet/dependabot/uv/test-tooling-091a29ec65")
- **Branch:** `issue/main-ci-green`
- **Worktree:** `C:/workspace/active-projects/python-template_kopie-worktrees/issue/main-ci-green`
- **Why this change exists:** `main`'s CI is red after three merged dependabot PRs (#55 lint-and-types, #56 test-tooling, #57 runtime-core). The user decided to fix `main` in one dedicated change before PR #54 (crosscut/search) merges into it.

### Scope composition (eleven items — extended by Q-127, answered 2026-10-02, and by items G, H, I, J and K, found in Phase 4)

Item J was opened after the Phase 5/Phase 6 reports below were written, so those reports cover items A–I only; item J's evidence is in its own Phase 4 section (comment-only, no behavior delta, so the Phase 5 full-suite evidence stands). Item K was opened the same way; its evidence is in its own Phase 4 section (test-harness only, no behavior delta, so the Phase 5 full-suite evidence stands).

| Item | Nature | Type | Affected spec IDs | Expected files |
|---|---|---|---|---|
| **A** | settings YAML round-trip loses `'\x85'` (NEL) | **defect** — the ISSUE core | `settings.md` INV-009, REQ-022, AC-030; `settings-coverage.md` REQ-009/010/011, INV-002 | `src/backend/settings/repository.py` |
| **B** | hypothesis `DeadlineExceeded` in `test_last_admin_invariant` | **defect** (test-harness; no product-behavior deviation) | `user-roles-permissions.md` INV-003, REQ-013, AC-015/036; `user-management.md` REQ-008, AC-017..019 | `tests/property/usermanagement/test_multi_role_invariants.py` |
| **C** | 3 ruff `I001` errors on `main` | **chore** (non-behavior) | none | `tests/acceptance/permissions/test_check_api.py`, `tests/acceptance/permissions/test_enforcement.py`, `tests/contract/permissions/test_performance.py` |
| **D** | pip-audit CVEs in two transitive dev dependencies | **chore** (non-behavior) | none | `uv.lock` |
| **E** | the logging feature's runtime reconfigure deletes loguru sinks it does not own (the actual CI `tests`-job failure) | **defect** (feature lifecycle / test isolation) | `logging.md` REQ-001/002/003, AC-001/002/004/005, INV-001, EDGE-005; `settings-coverage.md` REQ-014/015, AC-019/020 | `src/backend/logging/_setup.py`, `tests/conftest.py`, `tests/logging_test_helpers.py`, `tests/settings_test_helpers.py` |
| **F** | `dependency-review` job runs on `push` and fails by construction | **chore** (CI config, non-behavior) | none | `.github/workflows/quality.yml` |
| **G** | the residual order-dependent flake in the §6.4 corroboration recipe: `test_sink_reconfigured_rotation` publishes a `logging.*` write whose `SettingChanged` dispatch is never awaited, so the logging feature's reconfigure lands inside a later test and transiently drops the process-global loguru handler count | **defect** (test isolation; found in Phase 4 by the item-E step, recorded as the "residual flake" finding under item E) | `logging.md` AC-003/REQ-002 (the victim's assertion, unchanged); `settings-coverage.md` EDGE-008, REQ-015/AC-020 (the polluter's write) | `tests/settings_test_helpers.py`, `tests/unit/test_settings_coverage.py` |
| **H** | full-suite pollution: `isolated_event_bus()` called `reset_event_bus()`, which shuts down the instance it resets, and `EventBus.publish()` returns early on a shut-down bus — so after any test using that helper the settings registry's `SettingChanged` publishes were silently dropped and the logging feature's AC-020 reconfigure never ran (later logging sink tests lost their console sink or timed out) | **defect** (test isolation; found in Phase 4 at the full-suite gate, opened from the item-G residue) | `settings-coverage.md` REQ-015/AC-020 (the dropped publish); `logging.md` AC-003/REQ-002 (the victims' assertions, unchanged); `user-management.md` REQ-008/INV-003 (item-B extension: the second last-admin property test's measured deadline) | `tests/eventbus_test_helpers.py`, `tests/property/usermanagement/test_usermanagement_properties.py` |
| **I** | full-suite pollution: `migrations/env.py` calls `logging.config.fileConfig(config.config_file_name)`, which replaces the stdlib root logger's handlers/level and disables pre-existing non-root loggers — dropping the logging feature's stdlib intercept handler, so later tests routing stdlib records into loguru lose them (the ≈1-in-3 red full-suite runs); plus a second hypothesis deadline channel in the filemanagement property file (cold first example > 200 ms default) | **defect** (test isolation; found in Phase 4 after the Phase 5 S5.1 residue, opened from the item-H residue) | `logging.md` REQ-003/AC-004/AC-005/EDGE-005 (the lost intercept handler and the victims' assertions, unchanged); `file-management.md` INV-002/INV-008 (the property tests' measured deadline, unchanged assertions) | `tests/conftest.py`, `tests/property/filemanagement/test_filemanagement_properties.py` |
| **J** | the `security` job's `bandit -r src/` step reports six pre-existing false positives — B105 x5 on permission **description** strings and B110 (`try/except/pass`) — that were never observed because the job runs `pip-audit` first and pip-audit failed on `main`; the item-D fix unmasked them | **chore** (security-CI; found in Phase 4 after the item-D pip-audit fix) | none — CI only (no spec behavior affected) | `src/backend/authentication/feature_actions.py`, `src/backend/mail/feature_actions.py`, `src/backend/usermanagement/feature_actions.py`, `src/backend/permissions/service.py` |
| **K** | the `coverage` job (`uv run pytest tests/ --cov --cov-report=xml`) failed on `tests/property/filemanagement/test_filemanagement_properties.py::test_inv_001_no_partial_state_on_failure` — `DeadlineExceeded('Test took 739.77ms, which exceeds the deadline of 500.00ms')` (run 37040033246); the 500 ms deadline item I copied from the sibling avatar test is tighter than CI's slowest example, while coverage itself was fine (93.57% ≥ 92.0%) | **chore** (test-harness; found in Phase 4 from CI) | none — CI only (no spec behavior affected; Q-128: explicit measured deadline, assertion not weakened) | `tests/property/filemanagement/test_filemanagement_properties.py` |

Items C, D and F alter no externally observable behavior; they ride along by user decision. A is the ISSUE core. B is a test-harness defect (the specified invariant itself still holds). E is a real product-side defect in the logging feature's reconfiguration path (it mutates global loguru state it does not own) and is the only item that currently reddens CI's `tests` job. G is a test-side isolation defect (no `src/` change): it was opened from the item-E step's "residual flake" finding, which the E section explicitly recommended as a separate item rather than a widening of E. H is likewise a test-side isolation defect (no `src/` change): the shared event bus was being shut down under the tests, so cross-feature publishes were silently dropped for every later test in the session; it also carries the item-B extension (the same measured-deadline policy applied to the second last-admin property test).

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

---

## Phase 4 (S4.2, item E) — fix applied, GREEN (2026-10-02)

Item E only (logging sink ownership). Items A, B, C, D, F untouched: `src/backend/settings/repository.py`, the hypothesis test, the permissions test files, `pyproject.toml`/`uv.lock` and `.github/workflows/` were not modified — the diff below lists exactly the four files the fix touches.

### Cherry-pick (the §6.5 re-home plan) — zero conflicts

```bash
git cherry-pick b1e61ea f25e2ec e973821     # applied cleanly, no conflict to resolve
```

| source on `crosscut/search` (read-only) | new commit on `issue/main-ci-green` | message |
|---|---|---|
| `b1e61ea` | `0f41dc8` | test(logging): make enqueued-sink waits and registry isolation deterministic |
| `f25e2ec` | `4d9514e` | fix(logging): reconfigure removes only managed sinks (test-sink race on CI) |
| `e973821` | `9fec0a1` | test(settings): preserve all logging.* settings in install_isolated_registry |

Zero conflicts, as §6.5 predicted (main's 7 commits since the merge-base touch none of the four files), and the re-homed result is byte-identical to the search branch:

```bash
# git rev-parse HEAD:<f> == git rev-parse crosscut/search:<f>
IDENTICAL src/backend/logging/_setup.py
IDENTICAL tests/conftest.py
IDENTICAL tests/logging_test_helpers.py
IDENTICAL tests/settings_test_helpers.py

git diff --stat d2f8f32..HEAD
 src/backend/logging/_setup.py  | 39 +++++++++++++++++++++++++++++----------
 tests/conftest.py              | 33 +++++++++++++++++++++++++++++++++
 tests/logging_test_helpers.py  | 37 ++++++++++++++++++++++++++++++++++---
 tests/settings_test_helpers.py | 33 +++++++++++++++++++++++++++++----
 4 files changed, 125 insertions(+), 17 deletions(-)
```

No existing test assertion was weakened, changed or deleted by this step; the only test-side changes are the three cherry-picked helper commits. `crosscut/search` and its worktree were **not** modified (read-only source of the commits). **Note: when `crosscut/search` later rebases onto the fixed `main`, these three commits are duplicates and drop out of that branch (PR #54 becomes search-only, per Q-127).**

### GREEN gate (targeted — the full suite stays a Phase 5 gate)

Before (base `d2f8f32`, re-observed in this step):

```bash
uv run pytest tests/unit/settings/test_repository_roundtrip.py tests/unit/logging/test_logging_sink_ownership.py -q -p no:randomly
FFFF.                                                                    [100%]
4 failed, 1 passed in 5.33s
FAILED tests/unit/settings/test_repository_roundtrip.py::test_yaml_value_roundtrip_nel
FAILED tests/unit/settings/test_repository_roundtrip.py::test_yaml_template_roundtrip_nel
FAILED tests/unit/logging/test_logging_sink_ownership.py::test_reconfigure_keeps_foreign_sink
FAILED tests/unit/logging/test_logging_sink_ownership.py::test_reconfigure_replaces_only_the_managed_sinks
```

After (HEAD `9fec0a1`):

```bash
uv run pytest tests/unit/logging/test_logging_sink_ownership.py tests/unit/settings/test_repository_roundtrip.py -q -p no:randomly
FAILED tests/unit/settings/test_repository_roundtrip.py::test_yaml_value_roundtrip_nel
FAILED tests/unit/settings/test_repository_roundtrip.py::test_yaml_template_roundtrip_nel
2 failed, 3 passed in 0.42s
```

| node | before (`d2f8f32`) | after (`9fec0a1`) |
|---|---|---|
| `test_reconfigure_keeps_foreign_sink` | FAILED | **PASSED** |
| `test_reconfigure_replaces_only_the_managed_sinks` | FAILED | **PASSED** |
| `test_reconfigure_after_external_removal_of_a_managed_sink` | PASSED (GREEN by design — the pin that reddens a naive "remove the ids I remember" fix) | **PASSED** (still GREEN, as required) |
| `test_yaml_value_roundtrip_nel` | FAILED | FAILED — item A, still RED by design (not this step's scope) |
| `test_yaml_template_roundtrip_nel` | FAILED | FAILED — item A, still RED by design |

### Regression (targeted, not the full suite)

Logging family + settings-coverage acceptance, run 1 (`-p no:randomly`) and run 2 (default randomized order):

```bash
uv run pytest tests/unit/logging tests/integration/logging tests/acceptance/logging tests/property/logging tests/acceptance/settings_coverage -q -p no:randomly
35 passed in 10.99s
uv run pytest tests/unit/logging tests/integration/logging tests/acceptance/logging tests/property/logging tests/acceptance/settings_coverage -q
35 passed in 10.21s
```

Because item E is a timing/dispatch-timing flake, the group was re-run 3 more times in randomized order: `35 passed` ×3 (5 GREEN runs total across both orders). Collection check (nothing silently deselected): 20 unit + 1 integration + 3 acceptance + 3 property + 8 acceptance/settings_coverage = 35.

The three known offenders that trigger the reconfigure, both orders:

```bash
uv run pytest tests/contract/filemanagement/test_filemanagement_contracts.py tests/contract/permissions/test_performance.py tests/unit/test_settings_coverage.py -q
36 passed, 11 warnings in 4.15s
uv run pytest <same paths> -q -p no:randomly
36 passed, 11 warnings in 2.05s
# + 3 further randomized re-runs: 36 passed ×3
```

The 11 warnings are the pre-existing `sqlite3` deprecated-datetime-adapter `DeprecationWarning` from `tests/contract/permissions/test_performance.py` — that is item C's area and was not touched here.

Must-stay-GREEN spec evidence (settings-coverage AC-019/AC-020, untouched):

```bash
uv run pytest tests/acceptance/settings_coverage/test_setup_logger.py::test_sink_reconfigured_on_change -q -p no:randomly
1 passed in 0.64s
```

### Ruff (changed paths)

```bash
uv run ruff check src/backend/logging/_setup.py tests/conftest.py tests/logging_test_helpers.py tests/settings_test_helpers.py tests/unit/logging/test_logging_sink_ownership.py
All checks passed!
uv run ruff format --check <same five paths>
5 files already formatted
```

### Spec compliance (reference: §6.3 verdict — COMPLIANT, no Spec Amendment)

The fix keeps every cited ID: logging REQ-001/AC-001 (exactly one console + one file sink present with the stated options), REQ-002/AC-002 (idempotent setup), INV-001 (exactly one console + one file sink **added** per configure/reconfigure), REQ-003/AC-004/AC-005/EDGE-005 (a routed stdlib record still reaches the caller's own sink), and settings-coverage REQ-014/REQ-015 + AC-019/AC-020 (a `logging.*` write reconfigures **the feature's own** sink). The first `_configure()` call still removes loguru's default sink; later calls remove only the ids `_configure()` added, with `ValueError` suppressed for sinks removed externally.

### Finding — residual flake in the §6.4 corroboration recipe (pre-existing; not an E gate; not resolved here)

The §6.4 recipe is recorded as "Corroboration only (NOT the contract)". It is still flaky after the fix:

```bash
uv run pytest tests/unit/test_settings_coverage.py::test_sink_reconfigured_rotation tests/unit/logging/test_logging.py tests/unit/logging/test_logging_edges.py -p no:randomly -q
# 10 runs: 1 failed, 17 passed ×6  /  18 passed ×4
# tests/unit/logging/test_logging.py:46: AssertionError: assert 1 == 2   (test_ac_003_setup_logger_thread_safe)
```

- Pre-fix rate on the same recipe: **4/5 failed** (§6.4, on `75ca243`) → the fix reduces it but does not eliminate it. This is **not** a regression introduced by the cherry-pick.
- `uv run pytest tests/unit/logging/test_logging.py -p no:randomly -q` alone: **10/10 GREEN** → the flake needs the polluter test in front of it.
- Mechanism: `tests/unit/test_settings_coverage.py::test_sink_reconfigured_rotation` (line 327) writes `logging.log_max_bytes` and never awaits the resulting `SettingChanged`; the bus worker dispatches it during the next test, and `_configure()`'s remove-then-add window is observed by `test_ac_003_setup_logger_thread_safe`'s **process-global** handler-count assertion (`_EXPECTED_HANDLER_COUNT = 2`, `tests/unit/logging/test_logging.py:22,46`) as a transient `1`.
- Why the fix cannot close it: that assertion inspects `len(logger._core.handlers)` for the whole process, which any concurrent reconfigure transiently changes. §6.3 already flagged these two assertions as stricter than INV-001 and ruled that they **MUST NOT be weakened**; the only closings are test-side (drain/await the bus in the polluter, or assert on a settled state), which is outside item E's fix scope (§6.5: `_setup.py` + the three helpers) and outside this step's three cherry-picked commits.
- Consequence for the change objective: the four CI-red nodes item E was opened for are addressed; this residual is a separate test-isolation concern. **Flagged for the orchestrator** — recommend a new item (e.g. "G — drain/await the shared event bus in the settings-coverage polluter tests") rather than widening item E.

---

## Phase 4 (S4.2, item A) — fix applied, GREEN (2026-10-02)

Branch `issue/main-ci-green` @ `14382a2` (item E already landed). Item A only: `src/backend/settings/repository.py` + the settings property strategy. `src/backend/logging/`, the item-B hypothesis test, the item-C test files, `pyproject.toml`/`uv.lock` and `.github/workflows/` were not touched.

### Root cause

`_dump_yaml` used a plain `YAML(typ="safe")`. ruamel's **emitter** writes U+0085 (NEL) literally inside a single-quoted scalar (`app.a: '<NEL>  '`), while its YAML-1.1 **reader** treats U+0085 as a line break and folds it — so the written document is valid YAML that denotes a **different string** (`'\x85'` → `' '`). Both repositories share this serializer, so the value path (settings-coverage INV-002/REQ-009/REQ-011) and the template path (settings INV-009/REQ-022/AC-030) were both affected, and a corrupted value then overrides the registered default at construction (settings-coverage REQ-011).

### The fix (one implementation file)

`src/backend/settings/repository.py`:

- `_YAML_LINE_BREAKS = "\x85\u2028\u2029"` — the characters the YAML-1.1 reader folds. U+0085 is the only one the pre-fix serializer actually corrupted (full-BMP scan below); U+2028/U+2029 are listed so the rule follows the reader rather than the emitter's incidental behaviour.
- `_str_representer(dumper, data)` — returns a `ScalarNode("tag:yaml.org,2002:str", data, style='"')` **only** when the string contains one of those characters, otherwise `style=None` (ruamel's own choice). The affected scalar is therefore emitted escaped (`app.a: "\N"`) and loads back byte-exactly.
- `_SafeRepresenter(SafeRepresenter)` with `yaml_representers = _YAML_REPRESENTERS` (a **copy** of ruamel's table with the `str` entry replaced). Subclassing, not `add_representer`: `add_representer` is a classmethod that mutates the shared `SafeRepresenter` class and would change the output of every other ruamel user in the process (four settings tests construct `YAML(typ="safe")` themselves).
- `_dump_yaml` sets `yaml.Representer = _SafeRepresenter` on the per-call instance. `_load_yaml` is **unchanged** (`typ="safe"`, unsafe tags still rejected), the on-disk schema is unchanged, and the atomic temp-file + `os.replace` write (ADR-015/ADR-039) is untouched.

Written documents after the fix (verbatim):

```text
template file: 'category: app\ngroup: null\nname: prof\nvalues:\n  app.a: "\\N"\n  app.b: plain\n'
values file  : 'app.list:\n- "\\N"\n- ok\napp.text: "\\N"\n'
values load  : {'app.list': ['\x85', 'ok'], 'app.text': '\x85'}
```

### Completeness of the fix (full-BMP scan, two separate processes)

For every BMP code point except surrogates (63 488), five document shapes each (`{"k": s}`, `{"k": "a"+s+"b"}`, `{"k": [s]}`, `{s: "v"}`, `{"k": {"n": s}}`), dump → load → compare:

```text
variant: old      failing code points: ['0x85']    (5/5 shapes)
variant: patched  failing code points: []
```

Format-identity check (patched vs pre-fix dump, random strings over U+0020–U+2FFF excluding the three line breaks, 3 851 samples + nested/non-str documents): **0 differences** — keys, `null`, numbers, booleans and unaffected strings are emitted byte-identically, so the on-disk format changes only where the fix requires it.

### Backward compatibility (old files must still load) — PASS

Files were written to a temp dir **outside the repo** with the pre-fix serializer (`YAML(typ="safe")`, no representer) and then read back through the patched repositories:

```text
old values.yaml: 'app.b: true\napp.email: a@b.co\napp.empty: \'\'\napp.list:\n- a\n- b\n- \'\u2028  \'\n- \'\u2029  \'\n- \xa0\n- "line1\nline2"\napp.n: 7\napp.name: My App\napp.nested:\n  k: v\n  n: 1.25\napp.none: null\n'
old prof.yaml  : "category: app\ngroup: null\nname: prof\nvalues:\n  app.a: plain\n  app.list:\n  - x\n  - '\u2029    '\n  app.n: 3\n"
loaded values: {'app.b': True, 'app.email': 'a@b.co', 'app.empty': '', 'app.list': ['a', 'b', '\u2028', '\u2029', '\xa0', 'line1\nline2'], 'app.n': 7, 'app.name': 'My App', 'app.nested': {'k': 'v', 'n': 1.25}, 'app.none': None}
loaded template: name='prof' category='app' group=None values={'app.a': 'plain', 'app.list': ['x', '\u2029'], 'app.n': 3}
BACKWARD COMPAT OK — old-format files load unchanged (no error, values identical)
```

- No load error, no type change, values identical (`YamlValueRepository.load()` and `YamlTemplateRepository.get()`/`.list()` both verified). The loader was not modified, so old documents are parsed exactly as before.
- **Data already corrupted before the fix is not repaired** (as expected — the information is gone from the file): a file the old serializer wrote for `{"app.text": "\x85"}` still parses to `{'app.text': ' '}`. It loads without error; the fix prevents the corruption on the next write, it cannot recover a value that was never stored.

### GREEN gate (targeted — the full suite stays a Phase 5 gate)

Before (RED, re-confirmed at the start of this step, `14382a2`):

```bash
uv run pytest tests/unit/settings/test_repository_roundtrip.py -q -p no:randomly
```
```text
E       AssertionError: assert {'app.a': ' '} == {'app.a': '\x85'}
FAILED tests/unit/settings/test_repository_roundtrip.py::test_yaml_value_roundtrip_nel
FAILED tests/unit/settings/test_repository_roundtrip.py::test_yaml_template_roundtrip_nel
2 failed in 0.35s
```

After (the reproduction tests were **not** modified):

```bash
uv run pytest tests/unit/settings/test_repository_roundtrip.py -q -p no:randomly
```
```text
..                                                                       [100%]
2 passed in 0.28s
```

### Property-strategy hardening (§7 item A.3) — widening only

`tests/property/settings/test_settings_properties.py::test_inv_009_yaml_roundtrip` generated `value=st.text(min_size=0, max_size=10)` — NEL is in hypothesis's default alphabet but is drawn only by chance, which is why the defect surfaced intermittently. The alphabet is now `st.characters(blacklist_categories=("Cs",)) | st.just(_NEL)` (module constant `_YAML_SENSITIVE_TEXT`), i.e. the previous default alphabet **plus** an explicit weighted NEL entry — widened, never narrowed; `max_examples`, `min_size`/`max_size`, the name strategy and the assertion are unchanged.

Non-vacuity of the hardening (pre-fix serializer restored by an out-of-repo pytest plugin, pinned seed):

```bash
PYTHONPATH=/tmp/scratch_a uv run pytest tests/property/settings/test_settings_properties.py::test_inv_009_yaml_roundtrip -q -p oldser_plugin --hypothesis-seed=0
# E   AssertionError: assert Template(name...'app.a': ' '}) == Template(name...p.a': '\x85'})
# 1 failed in 3.72s
```

→ the hardened property now fails **deterministically** on the defective serializer and passes on the fixed one, so the defect cannot silently return.

```bash
uv run pytest tests/property/settings/test_settings_properties.py -q
```
```text
..........                                                               [100%]
10 passed in 4.16s
```

### Regression (targeted, not the full suite) — verbatim

```bash
uv run pytest tests/unit/settings tests/property/settings tests/acceptance/settings tests/integration/settings tests/unit/test_settings_coverage.py -q
```
```text
........................................................................ [ 63%]
.........................................                                [100%]
113 passed in 6.00s
```

### Ruff (changed paths) + types

```bash
uv run ruff check src/backend/settings/repository.py tests/property/settings/test_settings_properties.py tests/unit/settings/test_repository_roundtrip.py
# All checks passed!
uv run mypy src/
# Success: no issues found in 73 source files
```

Two lint findings were introduced and fixed inside this step: `I001` (import block ordering after adding `ruamel.yaml.nodes`/`ruamel.yaml.representer`) and `RUF012` (mutable class attribute) — the latter resolved by moving the table to a module-level `_YAML_REPRESENTERS` constant, which also keeps `mypy` happy (a `ClassVar` would conflict with `BaseRepresenter.yaml_representers`, which mypy sees as an instance-variable annotation).

**Pre-existing format drift (not item A, not resolved here):** `uv run ruff format --check src/backend/settings/repository.py` reports one hunk — the `YamlValueRepository` docstring indentation (lines 117-122). It is present on `HEAD` (`git show HEAD:src/backend/settings/repository.py` fails `ruff format --check` identically), it is not a `ruff check` error, and CI's lint job runs `ruff check .` only. Flagged for the Phase 5 whole-repo sweep.

### Spec compliance (reference: §1, §2 — no Spec Amendment)

No new behavior: the fix makes the existing YAML persistence satisfy settings INV-009 / REQ-022 / AC-030 / AC-031 and settings-coverage INV-002 / REQ-009 / REQ-010 / REQ-011. Safe-YAML semantics, the file layout (one `<name>.yaml` per template, a single `values.yaml`) and the atomic write are unchanged.


---

## Phase 4 (S4.2, item B) — fix applied, GREEN (2026-10-02)

Branch `issue/main-ci-green` @ `f21900c`. Item B only: **`tests/property/usermanagement/test_multi_role_invariants.py`** is the single file changed (one `@settings` decorator + a comment). `src/`, every other test file, `pyproject.toml`/`uv.lock` and `.github/workflows/` were not touched.

### The fix (decided policy, Q-128 option 1)

`test_last_admin_invariant` — the decorator line becomes a block with an explicit, measured `deadline`, and the strategy/assertion are byte-identical:

```python
# deadline=1000 is measured, not guessed: the slowest CI examples ran 246-356 ms against the
# 200 ms default (seeds 7/101/2024). The cost is argon2id password hashing (~50-100 ms per
# create_user, ADR-019) with up to ~11 creates per max_size=10 sequence. A hypothesis deadline
# is a harness tolerance on per-example runtime, not a product performance budget (NFR budgets
# are asserted by explicit budget tests), so the strategy and max_size stay untouched.
@settings(
    max_examples=_MAX_EXAMPLES,
    deadline=1000,
    suppress_health_check=[HealthCheck.too_slow],
)
```

`max_examples=20` (`_MAX_EXAMPLES`), `suppress_health_check=[HealthCheck.too_slow]`, `min_size=1`/`max_size=10`, the `sampled_from` op alphabet and the `assert any(u.is_active for u in admin_users)` invariant are **unchanged** — per Q-128 (answered 2026-10-02), shrinking `max_size` was rejected as a real weakening of INV-003 coverage, and `deadline=None` was rejected because it removes the per-example signal entirely.

### Measured vs chosen deadline (the 1000 ms is a margin, not a guess)

Per-example cost was measured **outside the repo** (scratch script in `%TEMP%`, importing the repo test's own `inner_test` and its own strategy object — no repo file modified). 20 examples per seed, timing the example body:

```text
seed default: n=20 min=  30.0 median=  84.2 p90= 120.8 max= 146.7 ms | examples > 200 ms: 0
seed       7: n=20 min=  28.2 median=  69.0 p90= 102.8 max= 123.6 ms | examples > 200 ms: 0
seed     101: n=20 min=  34.2 median=  72.3 p90= 109.9 max= 201.8 ms | examples > 200 ms: 1
seed    2024: n=20 min=  35.1 median= 104.8 p90= 203.2 max= 207.8 ms | examples > 200 ms: 3
pooled: n=80 min=28.2 median=75.8 max=207.8 ms; margin at deadline=1000 -> worst example is 4.8x faster than the chosen deadline
```

- **The 200 ms default genuinely has no headroom on this host**: 4 of 80 locally generated examples exceeded it (201.8 ms, 203.2 ms, 207.8 ms, and one more at seed 101) — which is exactly why the failure is load-dependent rather than seed-deterministic (§3, §Phase 3 note).
- Cause confirmed by direct measurement: `UserManager.create_user` = **31.2–32.7 ms** per call on this host (argon2id hashing, ADR-019); an example performs 1 seed admin + up to 10 creates, so 30–350 ms per example is the expected range. CI (slower runners) measured 246.47 / 355.59 / 251.62 ms for the failing examples.
- `deadline=1000` is therefore ~4.8× the local worst example and ~2.8× the worst CI observation — a deliberate margin above a measured distribution, not an unbounded exemption.
- Hypothesis's own probe (same script, `deadline=1` to force its measurement) reported 65.26 / 66.55 / 65.89 ms for the first example at seeds 7 / 101 / 2024, consistent with the independent timing above.

### GREEN gate (targeted — the full suite stays a Phase 5 gate)

```bash
uv run pytest tests/property/usermanagement/test_multi_role_invariants.py -q
```
```text
.                                                                        [100%]
1 passed in 2.62s
```

The three seeds pinned by the CI evidence, verbatim:

```bash
uv run pytest tests/property/usermanagement/test_multi_role_invariants.py -q -p no:randomly --hypothesis-seed=7
# .                                                                        [100%]
# 1 passed in 2.53s
uv run pytest tests/property/usermanagement/test_multi_role_invariants.py -q -p no:randomly --hypothesis-seed=101
# .                                                                        [100%]
# 1 passed in 2.21s
uv run pytest tests/property/usermanagement/test_multi_role_invariants.py -q -p no:randomly --hypothesis-seed=2024
# .                                                                        [100%]
# 1 passed in 2.82s
```

Three additional seeds (flake confidence, same command): seed 1 `1 passed in 1.86s`, seed 42 `1 passed in 1.58s`, seed 2026 `1 passed in 2.12s`.

**Honest statement on B's RED:** the RED for B is **CI-only** (§3: `DeadlineExceeded` 246.47 / 355.59 / 251.62 ms on `75ca243`). The pinned seeds did **not** reproduce the failure on this host before the fix (Phase 3 note), and the timing table above shows why — locally most examples sit under 200 ms, so the default deadline is only occasionally exceeded here. The runs above are therefore "the CI-failing seeds are GREEN with the explicit deadline", not a local RED→GREEN transition.

### Non-vacuity — the invariant test can still fail

The `deadline` change did not weaken the test; the probe below shows the assertion is reachable. Scratch experiment **outside the repo** (no repo file modified; the guard is restored at the end of the script): run the repo test's own body on the sequence `["create_admin", "remove_admin", "deactivate_admin"]`, with the INV-003 guard intact and with `UserManager._assert_not_last_admin` sabotaged to a no-op in memory:

```text
guard INTACT   : no assertion (the LastAdminError guard prevents the violating state)
guard removed  : INV-003 VIOLATION DETECTED -> AssertionError:
guard restored: True
```

So the falsifying state (admins exist, none active) is reached the moment the guard stops enforcing, and the test's assertion fires — the test is not vacuous.

- The guard's own enforcement is additionally pinned by existing acceptance/contract tests (no new test added): `tests/acceptance/usermanagement/test_multi_role.py:221-236` (five `pytest.raises(LastAdminError)` paths), `tests/acceptance/usermanagement/test_usermanagement.py:203-216`, `tests/acceptance/permissions/test_check_api.py:827-863`, `tests/contract/usermanagement/test_usermanagement_contracts.py:171`.
- **Observation (not fixed here, out of item B's scope):** with the guard sabotaged, the property's *random* search over 20 examples at seeds 7/101/2024 did **not** itself reach the falsifying interleaving (it needs a specific order: demote one admin, then deactivate the remaining one). The property asserts "if any admin exists, one is active" and detects that state when the search finds it; the guard's positive enforcement lives in the acceptance tests above. Flagged for the Phase 6 review, no change made.

### Regression (targeted, not the full suite) — verbatim

```bash
uv run pytest tests/property/usermanagement tests/acceptance/usermanagement tests/unit/usermanagement -q
```
```text
71 passed, 11 warnings in 15.35s
```

(The 11 warnings are the pre-existing SQLAlchemy `DeprecationWarning: The default datetime adapter is deprecated as of Python 3.12` from `sqlalchemy/engine/default.py:952`, unrelated to item B.)

### Ruff (changed path)

```bash
uv run ruff check tests/property/usermanagement/test_multi_role_invariants.py
# All checks passed!
uv run ruff format --check tests/property/usermanagement/test_multi_role_invariants.py
# 1 file already formatted
```

### Spec compliance (reference: §3 — no Spec Amendment)

No behavior change: INV-003 / REQ-013 / REQ-008 and the strategy are untouched; only the harness's per-example tolerance is made explicit and machine-independent, per Q-128.

## Phase 4 (S4.2, items C+D+F) — chore items (2026-10-02)

Branch `issue/main-ci-green` @ `e3b6d1c`. Three non-behavior chore items, one commit each (`b52d032`, `772d9dc`, `dd27702`). Per Q-127 these are in scope as chore items inside the ISSUE; **no `src/` file, no test assertion, no `pyproject.toml` version, and no other workflow file was touched.** All three are non-behavior by the Phase Matrix DOCS/CHORE definition: C is import ordering + whitespace, D is a lockfile-only dependency bump, F is a CI job trigger.

### Item C — three `I001` ruff errors (function-local import blocks)

Before (whole repo — the CI lint command, `.github/workflows/lint.yml` runs exactly `uv run ruff check .`):

```bash
uv run ruff check . --output-format=concise
```
```text
tests\acceptance\permissions\test_check_api.py:1008:5: I001 [*] Import block is un-sorted or un-formatted
tests\acceptance\permissions\test_enforcement.py:222:5: I001 [*] Import block is un-sorted or un-formatted
tests\contract\permissions\test_performance.py:37:5: I001 [*] Import block is un-sorted or un-formatted
Found 3 errors.
[*] 3 fixable with the `--fix` option.
```

Fix — scoped to exactly those three files (never repo-wide `--fix`, per P-6):

```bash
uv run ruff check --fix tests/acceptance/permissions/test_check_api.py tests/acceptance/permissions/test_enforcement.py tests/contract/permissions/test_performance.py
# Found 3 errors (3 fixed, 0 remaining).
uv run ruff format tests/acceptance/permissions/test_check_api.py tests/acceptance/permissions/test_enforcement.py tests/contract/permissions/test_performance.py
# 1 file reformatted, 2 files left unchanged
```

After:

```bash
uv run ruff check .
# All checks passed!
```

Files changed (`git diff --stat`):

```text
 tests/acceptance/permissions/test_check_api.py   |  3 +-
 tests/acceptance/permissions/test_enforcement.py | 38 +++++++++++++-----------
 tests/contract/permissions/test_performance.py   |  1 +
 3 files changed, 22 insertions(+), 20 deletions(-)
```

Diff eyeballed line by line — **only import ordering / blank lines / indentation**:

- `test_check_api.py:1008` — `from backend.permissions import PermissionCatalog  # deferred: RED` moved from after the six `feature_actions` imports to its sorted position between `mail` and `sessionmanagement`; the surrounding blank line moved with it. Same seven imports, same `# deferred: RED` markers, same call order below (`usermanagement_actions(catalog)` first, etc.). Function-local imports are executed in place at call time, so re-ordering them inside the same block cannot change observable behavior — none of these modules register global side effects on import (they expose `register_actions(catalog)` callables that the test body calls explicitly).
- `test_enforcement.py:222` — the `backend.permissions` block moved after `authentication_test_helpers` and before `backend.authentication` (isort order); the `backend.authentication` block is byte-identical.
- `test_performance.py:37` — one blank line inserted between the `alembic` and `backend.permissions` import blocks (isort first-party/third-party separation).
- The 38-line count in `test_enforcement.py` is **not** extra logic: 19 of those lines are the scoped `ruff format` re-wrapping the existing `BOOTSTRAP_SYSTEM_PERMISSIONS: frozenset[str] = frozenset({...})` literal (the brace block is indented one level deeper). The nine permission strings, the `frozenset[str]` annotation and the assignment are unchanged — a whitespace-only reformat produced by the authorized scoped `ruff format` command, not a content edit.

Gate (targeted — the full suite stays a Phase 5 gate):

```bash
uv run pytest tests/acceptance/permissions tests/contract/permissions -q
# ................................                                         [100%]
# 32 passed, 11 warnings in 2.13s
```

Commit: `b52d032 chore(lint): sort function-local import blocks flagged by ruff I001`.

### Item D — pip-audit findings (urllib3, virtualenv)

Before:

```bash
uv run pip-audit
```
```text
Found 11 known vulnerabilities in 2 packages
Name       Version ID              Fix Versions
---------- ------- --------------- ------------
urllib3    2.7.0   PYSEC-2026-4177 2.8.0
urllib3    2.7.0   PYSEC-2026-4176 2.8.0
urllib3    2.7.0   PYSEC-2026-4175 2.8.0
virtualenv 21.3.3  PYSEC-2026-4011 21.7.12
virtualenv 21.3.3  PYSEC-2026-4012 21.7.11
virtualenv 21.3.3  PYSEC-2026-4014 21.7.12
virtualenv 21.3.3  PYSEC-2026-4013 21.7.13
virtualenv 21.3.3  PYSEC-2026-4011 21.7.12
virtualenv 21.3.3  PYSEC-2026-4012 21.7.11
virtualenv 21.3.3  PYSEC-2026-4013 21.7.13
virtualenv 21.3.3  PYSEC-2026-4014 21.7.12

Name            Skip Reason
--------------- ------------------------------------------------------------------------------
python-template Dependency not found on PyPI and could not be audited: python-template (0.5.0)
```

Fix (lockfile only — `pyproject.toml` untouched, so no dependency *spec* changed):

```bash
uv lock --upgrade-package urllib3 --upgrade-package virtualenv
```
```text
Resolved 114 packages in 392ms
Updated python-discovery v1.3.1 -> v1.6.1
Updated urllib3 v2.7.0 -> v2.8.0
Updated virtualenv v21.3.3 -> v21.14.3
```

Lockfile diff is version-only — `git diff --stat uv.lock` → `uv.lock | 20 ++++++++++----------` (10 insertions, 10 deletions), and the added-package query returns **nothing** (no package added or removed):

```bash
git diff uv.lock | grep -E '^\+name = '
# (no output)
git diff uv.lock | grep -E '^[-+](name|version) = '
```
```text
-version = "1.3.1"
+version = "1.6.1"
-version = "2.7.0"
+version = "2.8.0"
-version = "21.3.3"
+version = "21.14.3"
```

**Three packages moved, not two — reported as required.** `python-discovery 1.3.1 → 1.6.1` is a *transitive* consequence of the virtualenv bump: `uv.lock` lists it as a dependency of `virtualenv` (`name = "virtualenv"` → `{ name = "distlib" }, { name = "filelock" }, { name = "packaging" }, { name = "platformdirs" }, { name = "python-discovery" }`), and virtualenv 21.14.3 requires a newer `python-discovery`. It is not an independently chosen upgrade, and nothing else in the 114-package graph moved.

```bash
uv sync --frozen
```
```text
Uninstalled 3 packages in 98ms
Installed 3 packages in 69ms
 - python-discovery==1.3.1
 + python-discovery==1.6.1
 - urllib3==2.7.0
 + urllib3==2.8.0
 - virtualenv==21.3.3
 + virtualenv==21.14.3
```

After — pip-audit is clean (the `python-template` skip line is pre-existing: the local project is not on PyPI, unchanged by this item):

```bash
uv run pip-audit
```
```text
No known vulnerabilities found
Name            Skip Reason
--------------- ------------------------------------------------------------------------------
python-template Dependency not found on PyPI and could not be audited: python-template (0.5.0)
```

No findings remain, so there is nothing left in or out of scope for D.

```bash
uv run deptry .
# Scanning 78 files...
# Success! No dependency issues found.
```

Targeted smoke of the affected areas (httpx/urllib3/SQLAlchemy/alembic and the pre-commit/virtualenv tooling path) — the full suite stays a Phase 5 gate:

```bash
uv run pytest tests/contract tests/integration -q
# 67 passed, 22 warnings in 78.54s (0:01:18)
```

(The 22 warnings are the pre-existing SQLAlchemy `DeprecationWarning: The default datetime adapter is deprecated as of Python 3.12` from `sqlalchemy/engine/default.py:952`, present before the bump.)

No-behavior-delta argument: only patch/minor upgrades of two transitive libraries (plus one transitive of the second), no version constraint changed in `pyproject.toml`, no dependency added or removed, no API surface touched in `src/`. urllib3 2.8.0 and virtualenv 21.14.3 are drop-in within the existing constraints; the 67 contract/integration tests that exercise the HTTP and DB paths are GREEN, and deptry confirms the dependency declarations still match actual usage.

Commit: `772d9dc chore(deps): upgrade urllib3 to 2.8.0 and virtualenv to 21.14.3 (pip-audit)`.

### Item F — the `dependency-review` job can never pass on `push`

Before: `.github/workflows/quality.yml` triggers on both `pull_request` and `push` to `main`, and the `dependency-review` job was unconditional — so every push to `main` ran `actions/dependency-review-action@v5` with no base/head ref pair. CI evidence (run `36894698244`, job `dependency-review`): *"Both a base ref and head ref must be provided … or by running a `pull_request`/`pull_request_target`/`merge_group` workflow"*. `gh api repos/jackthenet/python-template/branches/main/protection` → 404, i.e. **no branch protection on `main` requires this job**, so skipping it on `push` cannot block a merge.

Fix — a **job-level** `if:` (sibling of `runs-on`, not a step-level condition), rest of the workflow untouched:

```diff
   dependency-review:
+    # dependency-review-action needs a base/head ref pair, which only exists for
+    # pull_request / pull_request_target / merge_group events. The workflow also
+    # triggers on push to main, where the action always fails, so the job is
+    # skipped on push (no branch protection on main depends on it).
+    if: github.event_name != 'push'
     runs-on: ubuntu-latest
     steps:
```

Validation:

```bash
uv run python -c "import yaml,sys; d=yaml.safe_load(open('.github/workflows/quality.yml')); print('YAML OK'); print('dependency-review job-level if:', d['jobs']['dependency-review'].get('if')); print('steps:', len(d['jobs']['dependency-review']['steps']))"
```
```text
YAML OK
dependency-review job-level if: github.event_name != 'push'
steps: 5
```

The parsed `if:` sits on the job object (`jobs['dependency-review']['if']`), which confirms it is job-level rather than a step condition, and the job still has its 5 steps. `actionlint` is **not installed locally** (`command -v actionlint` → not found), so validation is the YAML parse plus the parsed-structure check above and a manual read of the placement; no other job in the file was modified (`git diff` shows a single 5-line hunk).

Which CI runs change: **push-to-`main` runs of `Quality` no longer execute `dependency-review`** (they previously always failed it); `pull_request` runs are byte-identical in behavior, and every other job in `quality.yml` (`type-check`, `security`, `coverage`, `dependencies`, `docs`, `migrations`) is unaffected. The dependency gate remains enforced where it can work — on PRs.

Commit: `dd27702 chore(ci): run dependency-review only on pull_request events`.

### Cross-cutting gate after C+D+F

```bash
uv run ruff check .
# All checks passed!
```

That is the CI lint command (`lint.yml` → `run: uv run ruff check .`), so the lint job's three pre-existing errors are gone.

Item C's targeted group re-run **after** the item D environment change (the dependency bump came after C's gate, so the ordering is checked, not assumed):

```bash
uv run pytest tests/acceptance/permissions tests/contract/permissions -q
# 32 passed, 11 warnings in 2.10s
```

Identical to the pre-bump run — the import-order change and the dependency bump are independent and both GREEN together.

**Observation (not acted on, out of scope):** `uv run ruff format --check .` reports `72 files would be reformatted, 370 files already formatted` — pre-existing repo-wide formatting drift from the dependabot ruff bump. It is **not** a CI gate (`lint.yml` runs `ruff check` only; `quality.yml` has no format check), and none of the three files touched by item C appear in that list. The only place it surfaces locally is the `ruff-format` pre-commit hook (`.pre-commit-config.yaml`), which runs on staged files only — so touching any of those 72 files in a future change will silently reformat it. A repo-wide `ruff format` sweep would touch 72 files and is a separate, explicit change (AGENTS.md: repo-wide fix/format is not a task step). Flagged for the Phase 6 review.

### Files changed by C+D+F (complete list)

```text
 tests/acceptance/permissions/test_check_api.py     (import order)
 tests/acceptance/permissions/test_enforcement.py   (import order + whitespace reformat of one frozenset literal)
 tests/contract/permissions/test_performance.py     (one blank line between import blocks)
 uv.lock                                            (3 version lines: urllib3, virtualenv, python-discovery)
 .github/workflows/quality.yml                      (job-level if: on dependency-review)
```

`src/`, `pyproject.toml`, all other test files, and all other workflows are untouched. No test was weakened, deleted or altered in assertion content.

---

## Phase 4 (S4.2, item G) — residual logging flake fixed (2026-10-02)

Branch `issue/main-ci-green` @ `be1adc5` (items E, A, B, C, D, F already landed). Item G only: two test files, no `src/` file touched. G was opened from the "Finding — residual flake in the §6.4 corroboration recipe" section of the item-E record, which recommended exactly this ("drain/await the bus in the settings-coverage polluter tests") as a separate item rather than a widening of E.

### Reproduction (RED for G) — measured at `be1adc5`, 10 runs per recipe

```bash
# recipe 1 — the §6.4 corroboration recipe, fixed collection order (the reliable one)
uv run pytest tests/unit/test_settings_coverage.py::test_sink_reconfigured_rotation tests/unit/logging/test_logging.py tests/unit/logging/test_logging_edges.py -q --color=no -p no:randomly
run 1:  1 failed, 17 passed in 1.57s
run 2:  18 passed in 1.47s
run 3:  18 passed in 1.48s
run 4:  1 failed, 17 passed in 1.55s
run 5:  18 passed in 1.48s
run 6:  1 failed, 17 passed in 1.55s
run 7:  18 passed in 1.47s
run 8:  1 failed, 17 passed in 1.55s
run 9:  1 failed, 17 passed in 1.56s
run 10: 1 failed, 17 passed in 1.55s
→ 6/10 RED

# recipe 2 — the brief's recipe, default (randomized) collection order
uv run pytest tests/unit/test_settings_coverage.py::test_sink_reconfigured_rotation tests/unit/logging/test_logging.py -q --color=no
run 1..9:  13 passed in 0.91-0.94s
run 10:    1 failed, 12 passed in 1.02s
→ 1/10 RED
```

Failure node in both: `tests/unit/logging/test_logging.py:46  AssertionError: assert 1 == 2` in `test_ac_003_setup_logger_thread_safe`. The §6.4 rate (4/5) is reproduced; the brief's recipe reproduces more rarely because `pytest-randomly` sometimes collects the polluter behind the victim.

### Mechanism — one race, two pollution channels

**Channel 1 — the handler-count window (the reported failure).** `test_sink_reconfigured_rotation` writes `logging.log_max_bytes` on the shared registry; `SettingsRegistry.set_value` publishes `SettingChanged` to the shared bus and returns without awaiting delivery. The logging feature's subscription (`_setup.py`, `_subscribe_to_setting_changes`) then runs `_configure()` on the bus worker — inside whatever test happens to be executing — and `_configure()`'s remove-then-add window transiently leaves the process-global handler set at `1`. `test_ac_003_setup_logger_thread_safe` asserts exactly that global count.

**Channel 2 — sink-target drift (found while closing channel 1).** The settings-coverage autouse fixture (`_reset_registry`, `isolated_registry(install=False)`) leaves the settings singleton reset for the whole test, so `install_isolated_registry()` preserves **nothing** and the installed registry holds only `logging.log_max_bytes`. `_settings_from_registry()` then falls back to the hardcoded defaults (`logs/app.log`, `INFO`) and re-points the process's file sink away from the session log file. Measured at `be1adc5`: `rm -rf logs && uv run pytest tests/unit/test_settings_coverage.py -q -p no:randomly` created `logs/app.log` in the worktree root on **3/3** runs. Whether the drift happens depends on whether the reconfigure lands before or after the fixture restores the session registry — the same race seen from the sink side. It is what reddens `tests/integration/logging/test_logging_integration.py::test_stdlib_loguru_decorator_pipeline` (it polls `session_settings.log_file` with a 15 s timeout — hence the ~26 s failing group runs). Baseline group measurement at `be1adc5`, default order, 6 runs: `FAILED tests/integration/logging/test_logging_integration.py::test_stdlib_loguru_decorator_pipeline` → `1 failed, 64 passed in 25.76s` ×1, `65 passed` ×5.

A settle-only first attempt made the group **worse** (4/6 RED): pinning the dispatch inside the polluter makes it always read the incomplete isolated registry, i.e. it makes channel 2 deterministic. Both channels therefore had to be closed together.

### The fix (test-side only)

`tests/settings_test_helpers.py` — new `set_value_settled(registry, key, value, timeout=5.0)`: performs `registry.set_value(key, value)` and waits for **that write's** dispatch to finish. The wait is **ordered, not timed**: the bus dispatches one event to its handlers in subscription order on a single worker thread and drains its queue FIFO, so a sentinel handler subscribed by the helper — after every handler that can react to the write — is invoked for that event only once those handlers have returned. The sentinel matches the write's key **and** value, so a stale `SettingChanged` for another key (or an earlier value of this one) cannot satisfy it, and FIFO order means every event queued before it has been dispatched too. The sentinel is unsubscribed in `finally`. `timeout=5.0` is the same bound as the existing `wait_for` and only bounds a hang (it raises `AssertionError`); no timeout was raised to paper over the race.

`tests/unit/test_settings_coverage.py::test_sink_reconfigured_rotation` (the polluter):

- registers the logging feature's own settings on its isolated registry and restores the session's `logging.log_file` / `logging.log_level` before the rotation write → channel 2 closed: the reconfigure it triggers changes only the rotation parameter and keeps the file sink on the session log file;
- routes every `logging.*` write through `set_value_settled` → channel 1 closed: no queued reconfigure can escape into a later test.

**No assertion was added, changed, weakened or deleted.** The victim, `test_ac_003_setup_logger_thread_safe`, is untouched: it still spawns 8 concurrent `setup_logger()` threads and still asserts `not errors` and `len(logger._core.handlers) == _EXPECTED_HANDLER_COUNT (2)` — which is what AC-003 (`docs/specs/logging.md`: "two threads calling `setup_logger()` concurrently … exactly one thread performs the setup and the other is a no-op") requires together with REQ-001/INV-001's exactly-one-console-plus-one-file set. The fix removes the *foreign* reconfigure that used to intrude on that window; it does not change what the test observes, and no settling fixture was added to it.

### GREEN (after) — verbatim

```bash
# recipe 1 (fixed order) — 10 runs
uv run pytest tests/unit/test_settings_coverage.py::test_sink_reconfigured_rotation tests/unit/logging/test_logging.py tests/unit/logging/test_logging_edges.py -q --color=no -p no:randomly
run 1..10: 18 passed in 1.50-1.52s      → 10/10 GREEN (0 RED)

# recipe 2 (randomized order) — 10 runs
uv run pytest tests/unit/test_settings_coverage.py::test_sink_reconfigured_rotation tests/unit/logging/test_logging.py -q --color=no
run 1..10: 13 passed in 0.94-0.96s      → 10/10 GREEN (0 RED)

# channel-2 drift check — 3 runs, worktree root
rm -rf logs && uv run pytest tests/unit/test_settings_coverage.py -q --color=no -p no:randomly
run 1..3: 30 passed in 1.93-1.97s ; no logs/ directory created (baseline: 3/3 created logs/app.log)
```

Group runs (the logging family + the settings-coverage family), default randomized order ×10 and fixed order ×1:

```bash
uv run pytest tests/unit/logging tests/integration/logging tests/acceptance/logging tests/property/logging tests/unit/test_settings_coverage.py tests/acceptance/settings_coverage -q
run 1:  65 passed in 11.63s
run 2:  65 passed in 11.80s
run 3:  65 passed in 12.51s
run 4:  65 passed in 12.40s
run 5:  65 passed in 12.69s
run 6:  65 passed in 12.02s
run 7:  65 passed in 10.91s
run 8:  65 passed in 11.89s
run 9:  65 passed in 11.52s
run 10: 65 passed in 11.57s
→ 10/10 GREEN (same recipe at be1adc5: 1/6 RED)

uv run pytest tests/unit/logging tests/integration/logging tests/acceptance/logging tests/property/logging tests/unit/test_settings_coverage.py tests/acceptance/settings_coverage -q -p no:randomly
65 passed in 11.82s      → GREEN
```

Settings-family sanity for the shared-helper change (the helper is additive, but the whole settings suite imports the module): `uv run pytest tests/unit/settings tests/acceptance/settings tests/integration/settings tests/property/settings tests/contract/settings tests/unit/test_settings_test_isolation.py -q` → `88 passed in 36.26s`.

### Ruff (changed paths)

```bash
uv run ruff check tests/settings_test_helpers.py tests/unit/test_settings_coverage.py
All checks passed!
```

`uv run ruff format --check` on the same paths: `tests/settings_test_helpers.py` already formatted; `tests/unit/test_settings_coverage.py` would be reformatted — **pre-existing**, verified with the identical command at `be1adc5` (same file-wide diff over ~40 untouched lines: blank-line-before-def and compact multi-arg literals). Running `ruff format` on that file would rewrite out-of-scope code, which AGENTS.md forbids in a task step; the step's own lines are format-neutral (one compact call removed, three single-line calls added, all under the 120-char limit). The whole-repo sweep stays the Phase 5 gate.

### Files changed by G (complete list)

```text
tests/settings_test_helpers.py        (+ set_value_settled; + threading / SettingChanged imports)
tests/unit/test_settings_coverage.py  (test_sink_reconfigured_rotation: session-consistent registry + settled writes; + _ROTATED_MAX_BYTES; + typing.Any import)
```

`src/` is untouched (constraint). `tests/conftest.py`, `tests/logging_test_helpers.py`, `tests/unit/logging/test_logging.py` and `tests/unit/logging/test_logging_edges.py` are untouched.

### Remaining exposure (flagged, not fixed here)

Two in-process publishers from the §6.1 offender inventory still publish `logging.*` on the shared bus without awaiting the dispatch: `tests/contract/filemanagement/test_filemanagement_contracts.py:93` (restored at `:120`) and `tests/contract/permissions/test_performance.py:57` (restored at `:120`). They write `logging.log_level` on the complete session registry, so they cannot cause channel-2 drift, and item E's `_SinkState` fix keeps them from deleting foreign sinks; what remains is the same transient handler-count window for whichever global-count assertion runs next. `set_value_settled` is the ready-made closing mechanism should a future run show them biting — widening to them here would have pulled two latency-budget contract tests into scope without evidence.

Also noted, no action (not part of the flake): `tests/acceptance/settings_coverage/test_wiring.py` runs `src/main.py` in a subprocess with `cwd=_REPO_ROOT`, which creates `logs/app.log` in the worktree root. That is a subprocess artifact, not in-process sink drift; `logs/` at the repo root is not in `.gitignore` (only `data/logs/` and `src/data/logs/`) — a `.gitignore` gap for a separate chore item.

---

## Phase 4 (S4.3) — refactor pass (2026-10-02)

Branch `issue/main-ci-green` @ `a7376a1` (items A–G landed). One bounded, behavior-preserving cleanup pass over the code this change wrote, then the targeted tests re-run. ISSUE change, so the Phase 4 refactor is a single pass, not per-task.

### What was reviewed

The change's own output (`git diff --name-only origin/main...HEAD`, docs excluded):

```text
src/backend/settings/repository.py                          (item A: _YAML_LINE_BREAKS / _str_representer / _SafeRepresenter)
src/backend/logging/_setup.py                               (item E: _SinkState managed-sink logic)
tests/settings_test_helpers.py                              (items E/G: install_isolated_registry, set_value_settled)
tests/conftest.py                                           (_drain_event_bus / log_records)
tests/logging_test_helpers.py                               (_console_sink_fd, wait_for_file_content)
tests/unit/test_settings_coverage.py                        (test_sink_reconfigured_rotation)
tests/unit/logging/test_logging_sink_ownership.py           (new)
tests/unit/settings/test_repository_roundtrip.py            (new)
tests/property/settings/test_settings_properties.py         (INV-009 alphabet hardening)
tests/property/usermanagement/test_multi_role_invariants.py (deadline=1000)
```

Reviewed for: duplicated settle/wait logic, unclear names, missing/incorrect type hints, comments that restate the code, dead parameters, over-broad `except`, imprecise `Any`.

### What changed (3 files, all behavior-preserving)

1. `src/backend/logging/_setup.py` — module global `_state` → `_sink_state` (the assignment plus its 6 uses). The module already names its other globals by what they hold (`_setup_done`, `_setup_lock`); `_state` was the only one that said nothing. Pure rename: no statement, order, or value changed, and the name is module-private, so nothing outside the module can reference it.
2. `tests/conftest.py` — `_drain_event_bus()` now reuses the shared `settings_test_helpers.wait_for` instead of hand-rolling the same poll loop: same 5.0 s bound, same 5 ms poll step, same 50 ms in-flight grace sleep, and the grace sleep still runs only when the queue actually drained. Removes the duplicated settle logic the helper module exists to own. The imports stay function-local (`PLC0415` is ignored repo-wide, and conftest deliberately imports the settings helpers lazily).
3. `tests/settings_test_helpers.py` — the two inline comments in `install_isolated_registry()` restated the docstring paragraph above them almost verbatim; replaced with what each line does plus the one non-obvious constraint (the definition must precede its `set_value`, which rejects unregistered keys). Comment-only.

No test assertion was added, changed, weakened or deleted. No public API change, no new dependency, no reformatting of untouched code (no repo-wide `ruff format`).

### Considered and deliberately NOT changed

- `repository.py` `_YAML_REPRESENTERS: dict[Any, Any]` — ruamel.yaml ships no `py.typed` (verified: no `py.typed` in `site-packages/ruamel/yaml/`, and `ignore_missing_imports = true`), so `SafeRepresenter` and `ScalarNode` are `Any` to mypy; a "precise" annotation would be unverifiable decoration.
- `session_settings: Any` in `test_settings_coverage.py` — the fixture itself is declared `Any` in `conftest.py`, and four out-of-scope test files consume it as `Any`/`object` with `type: ignore` comments. Narrowing one consumer types nothing and forces edits outside this change.
- `_NEL = "\x85"` appears in both new settings test files — two one-line constants; a shared helper would add an import for no gain.
- `for sink_id in list(_sink_state.ids)` — the copy is defensive (nothing mutates the list during the loop); harmless, and removing it is churn.
- `install_isolated_registry()`'s restore loop publishes `logging.*` `SettingChanged` on the shared bus without awaiting the dispatch — the same channel item G closed elsewhere. Closing it there adds waiting, i.e. it is a timing change rather than a refactor: flagged for a separate item, not done here.
- `tests/property/settings/test_settings_properties.py`, `test_multi_role_invariants.py`, `test_repository_roundtrip.py`, `test_logging_sink_ownership.py`, `logging_test_helpers.py` — reviewed, nothing to restructure: no duplication, names are domain-clear, and the private-loguru access is already documented as such.

### GREEN after the pass (verbatim)

```bash
uv run pytest tests/unit/settings tests/property/settings tests/unit/logging tests/integration/logging tests/acceptance/logging tests/property/logging tests/unit/test_settings_coverage.py tests/acceptance/settings_coverage tests/property/usermanagement -q --color=no
1 failed, 112 passed in 26.56s
FAILED tests/property/usermanagement/test_usermanagement_properties.py::test_inv_003_last_admin_invariant
```

The single failure is **pre-existing and outside this change** (that file is not in the diff): a hypothesis `DeadlineExceeded` (266 ms against the 200 ms default) — the same flake class item F fixed in `test_multi_role_invariants.py`, still open in `test_usermanagement_properties.py`. It fails identically on `main` (primary worktree, single file, 3 runs): `1 failed, 5 passed`, `6 passed`, `1 failed, 5 passed`; full suite on `main`: `1 failed, 556 passed, 1 skipped in 171.11s`.

Same command with that one pre-existing flaky file excluded — 3 runs:

```bash
uv run pytest tests/unit/settings tests/property/settings tests/unit/logging tests/integration/logging tests/acceptance/logging tests/property/logging tests/unit/test_settings_coverage.py tests/acceptance/settings_coverage tests/property/usermanagement --ignore=tests/property/usermanagement/test_usermanagement_properties.py -q --color=no
107 passed in 21.30s
107 passed in 20.96s
107 passed in 17.36s
```

Item-G corroboration recipe (the `log_records` drain is the path the conftest edit touched) — 5 runs:

```bash
uv run pytest tests/unit/test_settings_coverage.py::test_sink_reconfigured_rotation tests/unit/logging/test_logging.py tests/unit/logging/test_logging_edges.py -q --color=no -p no:randomly
18 passed in 1.54s
18 passed in 1.52s
18 passed in 1.52s
18 passed in 1.51s
18 passed in 1.51s
```

### Ruff / format / mypy (verbatim)

```bash
uv run ruff check src/backend/logging/_setup.py src/backend/settings/repository.py tests/conftest.py tests/settings_test_helpers.py tests/logging_test_helpers.py tests/unit/test_settings_coverage.py tests/unit/logging/test_logging_sink_ownership.py tests/unit/settings/test_repository_roundtrip.py tests/property/settings/test_settings_properties.py tests/property/usermanagement/test_multi_role_invariants.py
All checks passed!

uv run ruff format --check <same paths>
1 file would be reformatted, 8 files already formatted
```

The one file is `src/backend/settings/repository.py`, and the drift is **pre-existing, in an untouched docstring** (`YamlValueRepository`, ~line 119): `uv run ruff format --check` on `git show origin/main:src/backend/settings/repository.py` produces the identical diff, and `ruff format --diff` on the branch shows only that docstring — none of item A's added lines. Reformatting it would rewrite out-of-scope code; the whole-repo sweep stays the Phase 5 gate.

```bash
uv run mypy src/
Success: no issues found in 73 source files
```

### Full-suite observation (flagged, NOT fixed here)

`uv run pytest tests/ -q --color=no` on this branch is RED while every targeted set above is GREEN:

```bash
# with the S4.3 edits
7 failed, 631 passed, 1 skipped, 33 warnings, 1 error in 218.47s
# same command at a7376a1 with the S4.3 edits stashed
9 failed, 630 passed, 1 skipped, 33 warnings in 219.88s
# same command on main
1 failed, 556 passed, 1 skipped in 171.11s
```

So the full-suite RED is a property of the branch, not of this refactor pass. It includes this change's own new file (`tests/unit/logging/test_logging_sink_ownership.py`: 2 errors + 1 failure), `tests/acceptance/logging/test_logging.py::test_ac_001_setup_logger_adds_sinks` (handler set collapses to `{19: FileSink}` — the console sink is gone), and `tests/integration/logging/test_logging_integration.py::test_stdlib_loguru_decorator_pipeline`. Smallest reproduction found (order-dependent, 1/2 runs):

```bash
uv run pytest tests/unit/logging tests/acceptance/logging tests/integration/logging tests/property/logging tests/unit/logging_coverage tests/acceptance/logging_coverage tests/property/logging_coverage -q --color=no
1 failed, 50 passed, 2 errors in 31.07s      # second run of the same command: 53 passed
```

i.e. the `logging_coverage` family leaves sink state the new ownership tests assert on. CI runs the full suite, so this needs its own S4.2 item before Phase 5 can pass; fixing it is new behavior, not restructuring, so it is out of scope for a refactor pass.

## Phase 4 (S4.2, item H) — full-suite pollution: the shared event bus was being shut down (2026-10-02)

**Root cause.** `isolated_event_bus()` called `reset_event_bus()`, which **shuts down the instance it
resets**. `EventBus.publish()` returns early once `self._shutdown` is set, so a shut-down bus drops
every publish **silently** — no error, no event. After any test that used the old helper, the
settings registry's `SettingChanged` publishes never reached the logging feature's AC-020
subscription, so the logging reconfigure never ran: later logging sink tests lost their console sink
(process-global handler-count assertions failed) or hung waiting for a dispatch that could never
arrive. The defect is in the test helper, not in `src/`.

**Fix.** `isolated_event_bus()` now **parks** the real shared instance instead of resetting it: it
runs the block on a scratch `EventBus`, shuts the scratch bus down, and restores the parked shared
instance. The shared bus is never shut down, so cross-feature publishes keep flowing for the whole
session.

**Commits.** `6c40147` (park the shared event bus) · `983fe2a` (measured `deadline=1000` on
`tests/property/usermanagement/test_usermanagement_properties.py::test_inv_003_last_admin_invariant`).

**Item-B extension.** `983fe2a` extends item B's Q-128 measured-deadline policy (already applied to
`test_multi_role_invariants.py`) to the second last-admin property test, which surfaced the same
`DeadlineExceeded` only once the suite stopped aborting early.

**Family reproduction (logging + logging_coverage), before → after.**
- before the fix: `1 failed, 50 passed, 2 errors`
- after the fix, 3 consecutive runs: `53 passed in 11.20s` / `53 passed in 11.26s` / `53 passed in 10.91s`
- order-dependence check (sessionmanagement groups before the logging groups): `106 passed in 18.65s`
- eventbus groups: `31 passed in 4.28s` · `tests/property/usermanagement`: `7 passed in 10.87s`

**Full-suite gate (`uv run pytest tests/ -q`), observed in this step.**
- run 1: `639 passed, 1 skipped, 33 warnings in 173.38s`
- run 2: `2 failed, 637 passed, 1 skipped, 33 warnings in 176.67s`
- run 3: `639 passed, 1 skipped, 33 warnings in 191.23s`

**Run-2 residue.** `tests/unit/logging/test_logging_edges.py::test_edge_005_intercept_unknown_level`
and `tests/property/filemanagement/test_filemanagement_properties.py::test_inv_005_avatar_url_format`
— both pass in isolation (`2 passed in 1.66s`) and neither file appears in
`git diff --name-only origin/main...HEAD`, so this is a pre-existing order-dependent flake outside
item H, not a regression introduced by it.

**Before-state baseline (from the S4.3 pass, for comparison).** `7 failed, 631 passed, 1 skipped,
1 error` on this branch (`9 failed, 630 passed` with the refactor stashed); `1 failed, 556 passed,
1 skipped` on `origin/main`.

**Ruff.** clean on both changed files (`uv run ruff check tests/eventbus_test_helpers.py tests/property/usermanagement/test_usermanagement_properties.py`).

**No assertion was weakened, no test was deleted or skipped, and no `src/` file was touched by item H.**

## Phase 5 (S5.1) — full regression suite (2026-10-02)

Branch `issue/main-ci-green` @ `7681439`, clean tree (untracked `data/` only). Command:
`uv run pytest tests/ -q --tb=line --color=no`.

### Summary lines (3 runs)

| run | summary |
|---|---|
| 1 | `639 passed, 1 skipped, 33 warnings in 213.47s` |
| 2 | `639 passed, 1 skipped, 33 warnings in 197.00s` |
| 3 | `3 failed, 636 passed, 1 skipped, 33 warnings in 206.28s` |

Run-3 failures (one-line tracebacks):

- `tests/unit/logging/test_logging.py::test_ac_005_intercept_handler_skips_bootstrap` — `assert []` (test_logging.py:79); the record reached the loguru **stderr** sink instead of the test's capture list.
- `tests/unit/logging/test_logging.py::test_ac_004_intercept_handler_routes_records` — `assert []` (test_logging.py:58); same shape.
- `tests/integration/logging/test_logging_integration.py::test_stdlib_loguru_decorator_pipeline` — `assert False` from `wait_for_file_content(<session log file>, timeout=15)`; the loguru line never landed in the session file sink.

Ordering mechanism: `pytest-randomly 5.0.0` is installed and active (no seed line under `-q`), so every run — local **and** CI (`quality.yml:59`, `uv run pytest tests/ --cov`) — uses a fresh permutation.

### Probes (5× each, small subsets)

| probe | set | result |
|---|---|---|
| A | the two failing files alone (`tests/unit/logging/test_logging.py` + `tests/integration/logging/test_logging_integration.py`) | `13 passed` ×5 — **0/5 fail** |
| B | known polluting group (`tests/unit/test_settings_coverage.py` + `tests/unit/logging` + `tests/integration/logging`) | `51 passed` ×5 — **0/5 fail** |

Neither node reproduces outside the full-suite permutation.

### Reproduction tests (this change)

`uv run pytest tests/unit/settings/test_repository_roundtrip.py tests/unit/logging/test_logging_sink_ownership.py` → **`5 passed`** (GREEN).

### Per-node classification

| node | class | evidence |
|---|---|---|
| `test_ac_004_intercept_handler_routes_records` | **(b) order-dependent flake on this branch** | 1/3 full-suite runs here (and 1 of the Phase 4-H runs, §run-2/CI evidence lines 287-289); 0/10 in probes A+B; in scope — the `log_records` capture-sink channel (line 331) |
| `test_ac_005_intercept_handler_skips_bootstrap` | **(b) order-dependent flake on this branch** | same run, same channel; 0/10 in probes A+B |
| `test_stdlib_loguru_decorator_pipeline` | **(b) order-dependent flake on this branch** | same run; 0/10 in probes A+B; the sink-target drift channel (line 1269) |
| Phase 4-H residue (`test_edge_005_intercept_unknown_level`, `test_inv_005_avatar_url_format`) | (b) order-dependent flake (unchanged) | did not recur in these 3 runs; same mechanism family |

Classification **(c) pre-existing on `origin/main` is NOT claimed** for the three run-3 nodes: they are the defect this change exists to fix (recorded CI evidence, lines 287-289), so they are in scope, not background noise.

### Verdict

**NO — the `tests` job is not expected to be reliably green on CI.** Across 6 full-suite runs on this branch (3 here + 3 in Phase 4-H) **2 are red (≈33%)**, each red run carrying 2-3 logging sink nodes. The change's own reproduction tests are GREEN and the settings/repository pollution channel is closed; the remaining gap is the **logging sink-ownership / sink-target channel under randomized full-suite ordering** (capture-sink deletion race + file-sink re-point drift). Closing it needs a new Phase 4 item; pinning the `pytest-randomly` seed (or `-p no:randomly`) in CI would mask the ordering dependence, not fix it, and is a decision rather than a fix.

## Phase 4 (S4.2, item I) — the alembic fileConfig root-logger leak + a second hypothesis deadline channel (2026-10-02)

Opened from the Phase 5 S5.1 residue nodes. Two independent channels made full-suite runs red ≈1-in-3; both are closed test-side.

**Commits.** `e1508ec` `test(main-ci-green): restore stdlib root logging state around every test (alembic fileConfig leak)` (only `tests/conftest.py`, +29) · `f03f9ce` `test(main-ci-green): widen Hypothesis deadline to 500ms for filemanagement property tests`.

### Channel 1 — `fileConfig` replaces the stdlib root logger (root cause of the flake)

`migrations/env.py:27` calls `logging.config.fileConfig(config.config_file_name)`, which **replaces the stdlib root logger's handlers and level and disables pre-existing non-root loggers**. That drops the logging feature's stdlib intercept handler (REQ-003), so every later test that routes stdlib records into loguru (AC-004, AC-005, EDGE-005, the integration pipeline) loses them.

Only two tests trigger it in-process — `tests/integration/permissions/test_persistence.py` and `tests/contract/permissions/test_performance.py`, which pass `AlembicConfig(str(root/"alembic.ini"))`. `tests/acceptance/usermanagement/test_multi_role.py::_apply_migrations` uses a bare `Config()`, so `config_file_name is None` and it does not leak.

Proof (`test_persistence.py` + `tests/unit/logging/test_logging.py tests/integration/logging/test_logging_integration.py`, `-p no:randomly`):

```text
without the fixture: 3 failed, 12 passed, 11 warnings in 16.64s
                     test_ac_004_intercept_handler_routes_records
                     test_ac_005_intercept_handler_skips_bootstrap
                     test_stdlib_loguru_decorator_pipeline
with the fixture:    15 passed, 11 warnings in 1.63s
```

**Fix 1.** autouse `_stdlib_root_logging_restored` in `tests/conftest.py`: snapshots and restores the root logger's handlers, level, and `Logger.manager.loggerDict[*].disabled` around every test (exact restore, O(#loggers) per test). Considered and rejected: guarding `fileConfig` in `migrations/env.py` would change the migration path's behavior and needs a spec check.

### Channel 2 — a second hypothesis deadline channel (surfaced by the first proof attempt, 2/4 red)

`tests/property/filemanagement/test_filemanagement_properties.py::test_inv_008_variant_consistency` (and `test_inv_002_concurrent_same_key_last_write_wins`) hit `hypothesis DeadlineExceeded: took 253.22ms > 200.00ms` on a cold first example (`FlakyFailure`).

**Fix 2.** the 7 property tests in that file that still used Hypothesis' default 200 ms deadline now use `deadline=500` — the value the sibling avatar test (INV-004) already used in the same file. No assertion, example count, or skip changed (same Q-128 policy as items B/H).

### Evidence

- Targeted regression (logging families + multi_role + permissions contract/integration): `36 passed, 33 warnings in 10.64s`.
- Final proof, 4 consecutive green full-suite runs under randomized ordering: `639 passed, 1 skipped, 33 warnings` at 187.91s / 181.23s / 177.24s / 172.59s.
- Ruff: clean on both changed files (`ruff format --check` clean after one formatter pass on the property file).
- The Phase 5 S5.1 residue nodes (`test_edge_005_intercept_unknown_level`, `test_inv_005_avatar_url_format`, `test_ac_004/005`, `test_stdlib_loguru_decorator_pipeline`) are all explained by these two channels.

No assertion was weakened, no test was deleted/skipped/xfail'd, no seed was pinned, and no `src/` file was touched.

## Phase 5 (S5.1 re-run) — full regression suite after item I (2026-10-02)

Re-run of the S5.1 regression gate after item I closed the logging flake (alembic `fileConfig`
leak + deadline channel never connected). Branch `issue/main-ci-green` @ `77c0a69`. No code edits.

Full suite (`uv run pytest tests/ -q --tb=line --color=no`), two independent runs:
- run 1: `639 passed, 1 skipped, 33 warnings in 175.22s (0:02:55)` — `SKIPPED [1] tests\acceptance\filemanagement\test_filemanagement.py:364: symlinks not available on this host`
- run 2: `639 passed, 1 skipped, 33 warnings in 174.18s (0:02:54)` — same single skip (host limitation)

Reproduction tests GREEN: `tests/unit/settings/test_repository_roundtrip.py` +
`tests/unit/logging/test_logging_sink_ownership.py` → `5 passed in 0.23s`

Previously red nodes, families re-run once in randomized order (`--randomly-seed=20261002`,
pytest-randomly 5.0.0): `tests/acceptance/logging tests/unit/logging tests/integration/logging
tests/property/filemanagement` → `32 passed in 8.79s`

vs. pre-item-I state: the flake made 2 of 6 full-suite runs red; post-item-I both runs are green
(0 failed, 0 errors, 1 skipped = symlink host limitation, expected).

**Verdict: PASS** — Phase 5 full-regression gate satisfied.

## Phase 5 (S5.2) — lint, types, and quality gates (2026-10-02)

Run in the change worktree at `8c80342`; no code was written by this step.

| gate | command | verbatim summary | result |
|---|---|---|---|
| lint (CI) | `uv run ruff check .` | `All checks passed!` | PASS |
| format (informational, not a CI gate) | `uv run ruff format --check .` | `72 files would be reformatted, 370 files already formatted` | INFO (pre-existing drift) |
| format on this change's touched files | `uv run ruff format --check <16 touched .py>` | `2 files would be reformatted, 14 files already formatted` | INFO (pre-existing, see note) |
| types (gate) | `uv run mypy src/` | `Success: no issues found in 73 source files` | PASS |
| types (fast local tool, not a gate) | `uv run ty check src/` | `Found 134 diagnostics` (first: `error[invalid-type-form] ... src\main.py:110:36`) | INFO (pre-existing; mypy is the gate) |
| dependencies | `uv run deptry .` | `Success! No dependency issues found.` (Scanning 78 files) | PASS |
| vulnerabilities | `uv run pip-audit` | `No known vulnerabilities found` (own package `python-template (0.5.0)` skipped: not on PyPI) | PASS |
| architecture rules | `uv run pytest tests/architecture/ -q` | `ERROR: file or directory not found: tests/architecture/` | N/A (no `tests/architecture/` on this branch or on `origin/main`) |
| migrations | `ALEMBIC_DATABASE_URL=sqlite:///<temp> uv run alembic upgrade head` | `Running upgrade eace2f772150 -> d94b7f2e6a31, permissions persistence (...)` | PASS (ran against a throwaway temp DB — `alembic.ini:92` would write `./data/migrations.db` into the worktree; no worktree file created) |
| docs (CI) | `uv run mkdocs build --strict` | `Documentation built in 1.50 seconds` (exit 0, no build warnings) | PASS |

**`ruff format --check` note.** The 72-file drift is pre-existing (dependabot ruff bump; `ruff format --check` is not run by CI — `.github/workflows/lint.yml` runs `uv run ruff check .` only). Of this change's 16 touched `.py` files, 2 report drift (`src/backend/settings/repository.py`, `tests/unit/test_settings_coverage.py`); both were already unformatted on `origin/main` (verified by formatting the base copies), so the change introduces no new drift. Not fixed here: repo-wide `ruff format` would modify out-of-scope files (P-6).

**S5.2 gate: PASS** (all CI-run gates green; informational items are pre-existing and out of scope).

## Phase 5 (S5.3) — traceability matrix updated (2026-10-02)

`docs/verification/traceability.md`: the "Issue: main-ci-green" section is now a complete per-item table (A, A-value-side, B, C, D, E, F, G, H, I rows) mapping every affected spec ID to a GREEN test/evidence reference, the Phase 5 S5.1 run as the evidence, and the implementing commit. Existing rows updated with the new references: logging matrix REQ-001/AC-001 (status GREEN), REQ-002/AC-003, REQ-003/AC-004, REQ-003/AC-005, INV-001, EDGE-005; event-bus matrix REQ-005/AC-008, INV-002, EDGE-007; settings matrix REQ-010/AC-014, REQ-022/AC-030, REQ-021+022/AC-031, INV-009 (GREEN); user-management INV-003; settings-coverage matrix REQ-010/AC-014, REQ-014/AC-019, REQ-015/AC-020, INV-002, EDGE-008; file-management INV-002, INV-008; user-roles-permissions INV-003 (deadline flake closed). Orphan check: the two new test files (`tests/unit/settings/test_repository_roundtrip.py`, `tests/unit/logging/test_logging_sink_ownership.py`) and the widened property/property-deadline tests are all referenced, and every referenced node id collects (`pytest --collect-only` over the six touched files → 30 tests collected); the helper/fixture names referenced (`set_value_settled`, `isolated_event_bus`, `_stdlib_root_logging_restored`, `install_isolated_registry`) all exist. The INV-003 spec test-strategy path drift is recorded in the section.

## Phase 5 — verification report (2026-10-02)

S5.4 consolidates the Phase 5 evidence already recorded in this document (S5.1, S5.1 re-run, S5.2,
S5.3, and the item records) into the gate summary, spec-coverage and verdict. Docs-only step: no
code or test file was written, and no gate was re-run except the reproduction tests (cheap, and they
are the ISSUE's primary evidence).

### 1. Gate summary (full ISSUE gate set — the light tier does not apply, see §8)

| # | gate | command | verbatim evidence | result |
|---|---|---|---|---|
| 1 | reproduction tests GREEN | `uv run pytest tests/unit/settings/test_repository_roundtrip.py tests/unit/logging/test_logging_sink_ownership.py -q --tb=line --color=no` | `5 passed in 0.24s` (re-run at `f0b6d84` by S5.4; matches the S5.1 re-run `5 passed in 0.23s`) | **PASS** |
| 2 | full regression suite | `uv run pytest tests/ -q --tb=line --color=no` | S5.1 re-run, two independent runs: `639 passed, 1 skipped, 33 warnings in 175.22s` and `... in 174.18s` (the single skip is `tests/acceptance/filemanagement/test_filemanagement.py:364: symlinks not available on this host`) | **PASS** |
| 2b | full regression under randomized ordering (flake closure proof) | same, 4 consecutive runs (item I evidence) | `639 passed, 1 skipped, 33 warnings` at 187.91s / 181.23s / 177.24s / 172.59s — 0 failed, 0 errors | **PASS** |
| 3 | lint (CI gate) | `uv run ruff check .` | `All checks passed!` | **PASS** |
| 4 | types (gate) | `uv run mypy src/` | `Success: no issues found in 73 source files` | **PASS** |
| 5 | dependencies | `uv run deptry .` | `Success! No dependency issues found.` (78 files scanned) | **PASS** |
| 6 | vulnerabilities | `uv run pip-audit` | `No known vulnerabilities found` | **PASS** |
| 7 | migrations | `ALEMBIC_DATABASE_URL=sqlite:///<temp> uv run alembic upgrade head` | `Running upgrade eace2f772150 -> d94b7f2e6a31, permissions persistence (...)` | **PASS** |
| 8 | docs (CI gate) | `uv run mkdocs build --strict` | `Documentation built in 1.50 seconds` (exit 0, no warnings) | **PASS** |
| 9 | architecture rules | `uv run pytest tests/architecture/ -q` | `ERROR: file or directory not found: tests/architecture/` | **N/A** — `tests/architecture/` does not exist on this branch or on `origin/main`. AGENTS.md (Phase 5 REFACTOR step, Phase 6 check 4) and the verify skill reference a directory this repo has never had: a **docs/repo reconciliation item**, not a regression introduced here. Recorded as a follow-up (§4). |

Informational, non-gate (pre-existing, unchanged by this change): `ruff format --check .` →
`72 files would be reformatted, 370 files already formatted`; `ty check src/` → `Found 134
diagnostics` (mypy is the gate). Both are analysed in the S5.2 section.

### 2. Spec coverage for the affected IDs

Every affected normative ID has at least one GREEN test. Test names below are the GREEN evidence
rows written into `docs/verification/traceability.md` by S5.3; the per-item table there is the
authoritative row-level detail.

| item | spec IDs (source spec) | GREEN test(s) / evidence | status |
|---|---|---|---|
| A — settings YAML round-trip loses U+0085 NEL | INV-009, REQ-022, AC-030, AC-031 (`settings.md`) | `tests/unit/settings/test_repository_roundtrip.py::test_yaml_template_roundtrip_nel`; property `tests/property/settings/test_settings_properties.py::test_inv_009_yaml_roundtrip` | **GREEN** |
| A (value side) | REQ-009, REQ-010, REQ-011, INV-002 (`settings-coverage.md`) | `test_repository_roundtrip.py::test_yaml_value_roundtrip_nel` | **GREEN** |
| B — hypothesis `DeadlineExceeded` in the last-admin property | INV-003, REQ-013, AC-015, AC-036 (`user-roles-permissions.md`); REQ-008, AC-017/018/019 (`user-management.md`) | `tests/property/usermanagement/test_multi_role_invariants.py::test_last_admin_invariant`; `tests/property/usermanagement/test_usermanagement_properties.py::test_inv_003_last_admin_invariant` (assertions unchanged; measured `deadline=` widening only) | **GREEN** |
| E — loguru sink ownership across a settings-driven reconfigure | REQ-001/AC-001, REQ-002/AC-003, REQ-003/AC-004, AC-005, INV-001, EDGE-005 (`logging.md`); REQ-014/AC-019, REQ-015/AC-020 (`settings-coverage.md`) | `tests/unit/logging/test_logging_sink_ownership.py::test_reconfigure_replaces_only_the_managed_sinks`, `::test_reconfigure_after_external_removal_of_a_managed_sink`, `::test_reconfigure_keeps_foreign_sink`; the logging acceptance/unit/integration families | **GREEN** |
| C — 3 ruff errors on main | none (lint-only import ordering in 3 test files) | `ruff check .` → `All checks passed!` | **GREEN (chore)** |
| D — pip-audit CVEs | none (dependency manifest) | `pip-audit` → `No known vulnerabilities found` | **GREEN (chore)** |
| F — CI trigger conditions | none (workflow file) | `.github/workflows/*` conditions; no test surface | **GREEN (chore)** |
| G — residual logging flake (bus drain in settings-coverage polluters) | REQ-002/AC-003, REQ-015/AC-020 (pollution path only; assertions untouched) | `tests/unit/test_settings_coverage.py` logging-sink tests + logging families, 10/10 recipe runs green after the fix | **GREEN** |
| H — shared event bus shut down by the test helper | REQ-005/AC-008, INV-002, EDGE-007 (`event-bus.md`) | `isolated_event_bus()` parks instead of resetting; full suite green (S5.1 re-run) | **GREEN** |
| I — alembic `fileConfig` root-logger leak + second deadline channel | REQ-003/AC-004, AC-005, EDGE-005 (`logging.md`); INV-002, INV-008 (`file-management.md`) | autouse `tests/conftest.py::_stdlib_root_logging_restored`; `tests/property/filemanagement/test_filemanagement_properties.py` (`deadline=500`); 4 consecutive green randomized-order full runs | **GREEN** |

**No spec amendment was needed.** The logging side was adjudicated in §6.3 ("E — spec-compliance
verdict: **COMPLIANT** (no Spec Amendment, no reclassification)"), and the settings side in §1
("The requirement exists — no spec amendment is needed for A", the `Template`/INV-009 basis). Both
verdicts stand; nothing in Phases 3–5 changed them, so no Spec Amendment PR was opened and the
change type stayed ISSUE.

### 3. No-behavior-delta statement (chore items C, D, F; test-harness items B, G, H, I)

| item | what changed | why externally observable behavior is unchanged |
|---|---|---|
| C | Import-ordering fixes in 3 test files (I001/RUF001-class lint errors). | Import order is not observable at runtime; no symbol, signature, or assertion changed. `ruff check .` clean is the only effect. |
| D | Dependency-manifest bumps (patch/minor, CVE-driven) in `pyproject.toml` / `uv.lock`. | No dependency was added, removed, or replaced; APIs used by `src/` are unchanged across the bumped versions; the full suite and `deptry` confirm it. |
| F | GitHub Actions trigger-condition changes (`.github/workflows/*`). | CI configuration is not part of the shipped runtime; no `src/` or `tests/` file was touched. |
| B | `deadline=` widened on two last-admin Hypothesis properties (measured values, Q-128 policy). | A deadline is a scheduling budget, not an assertion. Example counts, strategies, and assertions are unchanged; the invariant is still checked over the same input space. |
| G | Test-side bus drain/await added in the settings-coverage polluter tests. | Only test synchronization changed; the production publish path and the AC-020 reconfigure behavior are untouched. |
| H | `isolated_event_bus()` parks the shared bus instead of `reset_event_bus()`-ing it. | The helper lives in `tests/`; `src/backend/eventbus/` is unchanged. The fix removes a test-harness-induced shutdown, restoring the documented bus lifecycle for later tests. |
| I | Autouse `_stdlib_root_logging_restored` fixture in `tests/conftest.py`; `deadline=500` on 7 filemanagement property tests. | The fixture snapshots and restores stdlib root-logger state around each test — it changes no production logging behavior, it stops one test's `fileConfig` call from leaking into the next. The deadline change is scheduling-only. `migrations/env.py` was deliberately **not** modified (see §4). |

No acceptance test was weakened, deleted, skipped, xfail'd, or converted to a weaker assertion at any
point in this change; no seed was pinned; no `src/` file was touched by items B, G, H, I.

### 4. Residual risks / follow-ups (out of scope here)

1. **`ruff format --check` drift (72 files repo-wide).** Not a CI gate (`lint.yml` runs `ruff check .`
   only); pre-existing since the dependabot ruff bump. Of this change's 16 touched `.py` files, 2
   report drift (`src/backend/settings/repository.py`, `tests/unit/test_settings_coverage.py`) and
   both were already unformatted on `origin/main`. A repo-wide `ruff format` is a separate explicit
   chore (P-6: repo-wide `--fix`/`format` inside a task step modifies out-of-scope files).
2. **`tests/architecture/` does not exist** although AGENTS.md (Phase 5 REFACTOR, Phase 6 check 4)
   and the verify skill reference it, and CI has no architecture job. Either the docs stop
   referencing it or the architecture tests get added — a DOCS/CHORE or FEATURE follow-up.
3. **Test runs create `data/` and `logs/` in the worktree root** (e.g. `alembic.ini:92` →
   `./data/migrations.db`; the logging file sink defaults to a `logs/` path). Neither is gitignored,
   so they show up as untracked noise and can be committed by accident. Follow-up: gitignore them or
   point the defaults at a temp dir under test conditions.
4. **Stale `RED` statuses in the logging and settings-coverage traceability matrices.** Rows such as
   logging REQ-002/AC-002 … REQ-009/AC-015 still read `RED` from the original feature's state machine
   even though those tests are GREEN in the suite today. Matrix drift, not a coverage gap: S5.3
   updated only the rows this change actually touched. Follow-up: a DOCS/CHORE matrix refresh.
5. **`migrations/env.py:27` `logging.config.fileConfig(...)` was left as-is.** The alternative fix
   (guard or replace the `fileConfig` call) changes the migration path's behavior and needs a spec
   check against the alembic scaffold's requirements; the ISSUE's minimal-fix rule kept it out. The
   autouse fixture neutralises the symptom for tests, so the underlying call stays a latent hazard
   for any in-process migration followed by stdlib-intercept logging.
6. **`ty check src/` reports 134 pre-existing diagnostics** while `mypy src/` (the gate) is clean —
   a tool-divergence follow-up, not a gate failure.

### 5. Verdict

**Phase 5: PASS.** The ISSUE's Phase 5 criteria are all met: the reproduction tests are GREEN
(`5 passed`), the full regression suite is clean (`639 passed, 1 skipped`, twice, plus 4 consecutive
green randomized-order runs), lint and types are clean (`All checks passed!` / `Success: no issues
found in 73 source files`), the supporting gates (deptry, pip-audit, `alembic upgrade head`,
`mkdocs build --strict`) pass, and the traceability matrix was updated (S5.3) with every affected
normative ID backed by a GREEN test. The only non-PASS row is the architecture gate, which is
**N/A because `tests/architecture/` does not exist in this repo** — recorded as a docs/repo
reconciliation follow-up (§4.2), not a failed gate.

## Phase 6 (S6.1) — normative-basis review (2026-10-02)

Bounded inputs: this triage record + the nine items' Phase 4 sections, the FINAL state of the 16 non-doc files (`git diff origin/main...HEAD -- <file>`), and the cited spec IDs. No full-suite run (Phase 5 owns that gate); one targeted run: `tests/unit/settings/test_repository_roundtrip.py tests/unit/logging/test_logging_sink_ownership.py` → `5 passed in 0.27s`.

### Findings

| # | finding | severity | resolution / decision |
|---|---|---|---|
| F-1 | Item C touched more than "import blocks only": `test_enforcement.py` also re-wraps the `BOOTSTRAP_SYSTEM_PERMISSIONS` frozenset literal (ruff format) | Low | **Resolved.** Indentation only — same nine keys in the same order; the other two files are import-order / blank-line only. Non-behavior, inside item C's predicted file set. Accepted. |
| F-2 | Item D's lock diff adds an edge `virtualenv → packaging` | Info | **Resolved.** `packaging` is already a locked package (`uv.lock:1281`) → no new dependency; only urllib3 / virtualenv / python-discovery versions move; `pyproject.toml` untouched; `pip-audit` + `deptry` clean. Accepted. |
| F-3 | Item F's CI evidence is half-pending: the `pull_request` run proving the job still executes exists only after S6.4 opens the PR; the `push`-skip proof only after merge | Info | **Carried to S6.4.** Verified here: `gh api .../branches/main/protection` → 404 (no branch protection ⇒ no required check depends on the job), and `if: github.event_name != 'push'` leaves `pull_request` / `merge_group` runs untouched (`quality.yml` triggers only on `pull_request` + `push: main`). |
| F-4 | The `deadline=` widenings (1000 ms ×2, 500 ms ×7 nodes) do reduce what those property tests can detect: a per-example slowdown between 200 ms and the new bound no longer fails | Low | **Accepted, stated plainly.** A hypothesis deadline is a harness tolerance, not a product budget; the specified invariants are asserted by unchanged assertions, and strategy / `max_size` / `max_examples` are untouched. `HealthCheck.too_slow` was already suppressed on `main` in all three files; performance budgets live in `tests/contract/permissions/test_performance.py`. Bases are measured (246–356 ms; cold first example > 200 ms). |
| F-5 | `_sink_state` in `src/backend/logging/_setup.py` is module-global and mutated without a lock | Info | **Accepted, no change.** Same exposure pre-fix (blanket `logger.remove()` + re-add); the bus dispatches on one worker thread and `setup_logger()` keeps its `threading.Event` guard ⇒ no new race. |
| F-6 | Test-name drift vs the §7 plan (`test_reconfigure_keeps_foreign_sinks` → `..._keeps_foreign_sink`, etc.) | Info | **Resolved.** S5.3's traceability rows use the final names and every referenced node id collects (30 collected over the six touched files). |

### Q1 — does every item stay inside its declared fix scope?

Yes — every touched file is one the scope table predicted, and no file is touched that no item claims.

- **A** `src/backend/settings/repository.py` + `tests/unit/settings/test_repository_roundtrip.py` (new) + `tests/property/settings/test_settings_properties.py`.
- **B** `tests/property/usermanagement/test_multi_role_invariants.py` only.
- **C** the three permissions files (`test_check_api.py`, `test_enforcement.py`, `test_performance.py`).
- **D** `uv.lock` only.
- **E** `src/backend/logging/_setup.py`, `tests/conftest.py`, `tests/logging_test_helpers.py`, `tests/settings_test_helpers.py` + `tests/unit/logging/test_logging_sink_ownership.py` (new).
- **F** `.github/workflows/quality.yml` only.
- **G** `tests/settings_test_helpers.py`, `tests/unit/test_settings_coverage.py`.
- **H** `tests/eventbus_test_helpers.py`, `tests/property/usermanagement/test_usermanagement_properties.py`.
- **I** `tests/conftest.py`, `tests/property/filemanagement/test_filemanagement_properties.py`.

`tests/conftest.py` (E's bus drain + I's root-logger restore) and `tests/settings_test_helpers.py` (E's cherry-pick + G's `set_value_settled`) are shared by named items only. `AI_Questions.md`, `docs/verification/*`, `docs/workflow/PROBLEMS.md` are workflow records, not behavior.

### Q2 — is the fix minimal (no behavior beyond the affected spec IDs)?

Only two `src/` files changed, and each changes exactly the one thing the defect required.

- `src/backend/settings/repository.py` (A): only the YAML **emission style** changes. `YAML(typ="safe")` and the loader are untouched; the `str` representer is overridden on a **copied** table inside a representer subclass, so ruamel's shared `SafeRepresenter` is never mutated; only scalars containing U+0085 / U+2028 / U+2029 get the escaped style, so every other document is byte-identical. `_dump_yaml` is the single writer for both repositories (line 136 value, line 244 template), which is why one file covers A's template and value sides.
- `src/backend/logging/_setup.py` (E): only **which sinks are removed** changes — first call keeps the blanket `logger.remove()` (loguru's default sink must go, REQ-001/INV-001), later calls remove only the managed sink IDs by ID, with `contextlib.suppress(ValueError)` for a managed sink already removed externally. The sinks added, the root-level sync and `_install_intercept_handler()` are unchanged. No other `src/` change exists ⇒ no finding.

### Q3 — spec compliance of the two `src/` changes (re-verified independently)

**(a) Item A — settings INV-009 / REQ-022 / AC-030 / AC-031, settings-coverage INV-002.** `settings.md:303` INV-009: "For any valid `Template`: `repository.save(t)` followed by `repository.get(t.name)` returns a template equal to t (YAML round-trip)." Pre-fix `'\x85'` loaded as `' '`, a direct violation. `settings-coverage.md:192` INV-002: "For a `LIST` setting, a persisted value round-trips: `save(values)` then `load()` returns the same value" — same violation on the value path. `settings.md:242` REQ-022: "one file per template named `<name>.yaml`, safe YAML, atomic writes (a template file is always either absent or valid YAML)". The fix emits a standard double-quoted scalar under the standard `tag:yaml.org,2002:str` tag — no custom tags, no object loading, `typ="safe"` unchanged — so the document stays safe YAML and AC-030 ("a file `<name>.yaml` exists in the directory … valid YAML containing the template's fields") and AC-031 (cross-instance `get_template`) still hold; pre-fix files keep loading because the loader is untouched. **Verdict: COMPLIANT** (agrees with §1).

**(b) Item E — logging REQ-001/002/003, AC-001/002, INV-001, EDGE-005; settings-coverage REQ-014/015.** `logging.md:66` REQ-001: "configures loguru with a console sink (stderr, colorized, backtrace enabled) and a rotating file sink (UTF-8, enqueued, backtrace enabled, `diagnose=False`)"; `:82` AC-001 asserts that exact sink pair; `:83` AC-002: "the second call is a no-op and no new sinks are added"; `:104` INV-001: "the number of loguru sinks added is exactly one console sink and one file sink"; `:67` REQ-002: "`setup_logger()` is idempotent … Thread-safe via a `threading.Event`" (untouched — the `_setup` guard is unchanged); `:68` REQ-003: an `_InterceptHandler` "routes stdlib `logging` records into loguru sinks"; `:116` EDGE-005: "Record is routed using the numeric level number instead of the name". `settings-coverage.md:142` REQ-015: "reconfigures the sink at runtime when any `logging.*` setting changes, re-applying all current `logging.*` values"; `:141` REQ-014 covers `setup_logger()` idempotence. No sentence authorises removing sinks the feature does not own, so the pre-fix blanket `logger.remove()` on every reconfigure was the deviation; the fix re-applies the same values and leaves the handler set exactly one console + one file sink (pinned by `test_reconfigure_keeps_foreign_sink` and the one-console/one-file guard), and EDGE-005 / REQ-003 are additionally protected by item I's root-logger restore. **Verdict: COMPLIANT** (agrees with §6.3) — no Spec Amendment, type stays ISSUE.

### Q4 — no test was weakened, narrowed, skipped, xfail'd or deleted to reach GREEN

`git diff origin/main...HEAD -- tests/ | grep '^-.*assert '` → **empty**: no assertion was removed or edited anywhere in the test diff. No `skip` / `skipif` / `xfail` marker was added; no test file was deleted (two were added). No seed is pinned in test code — the pinned seeds (`--hypothesis-seed=7/101/2024/99`) were CLI reproduction commands recorded in §0/§7, never written into a test.

- **`deadline=1000` (B, H) and `deadline=500` (I)** — these **do** reduce detection, in exactly one dimension: a per-example runtime between the old 200 ms default and the new bound no longer raises `DeadlineExceeded`. They cannot reduce detection of the specified behavior itself — the invariant assertions, the strategies, `max_size` and `max_examples` are byte-unchanged, and shrinking any of those (the alternative that would have mattered) was rejected. All three files already carried `suppress_health_check=[HealthCheck.too_slow]` on `main`, so the suite's pre-existing posture already tolerated slow examples; the real performance contract is asserted by `tests/contract/permissions/test_performance.py` (`test_check_latency_under_5ms_median`), untouched. See F-4.
- **Widened hypothesis alphabet (A)** — strictly widening: `st.characters(blacklist_categories=("Cs",)) | st.just("\x85")` is the default alphabet plus a weighted NEL; nothing is removed, so detection only increases (the defect was previously findable only by chance).

### Q5 — do the chore items (C, D, F) really have no behavior delta?

**C:** import-order and blank-line changes only, plus the F-1 frozenset re-wrap (indentation only, same nine keys). The three tests still collect and pass; `uv run ruff check .` → `All checks passed!`. **D:** dev-tooling versions only (urllib3 2.7.0→2.8.0, virtualenv 21.3.3→21.14.3, python-discovery 1.3.1→1.6.1); no `pyproject.toml` change, no new dependency (F-2); `pip-audit` → `No known vulnerabilities found`, `deptry` clean. **F:** `if: github.event_name != 'push'` on the `dependency-review` job. No branch protection exists on `main` (`gh api repos/jackthenet/python-template/branches/main/protection` → `{"message":"Branch not protected"…}`, re-run in this step), so no required status check depends on the job and nothing can block a merge; `quality.yml` triggers only on `pull_request: main` and `push: main`, so the condition removes the job from `push` runs and leaves `pull_request` runs (and any `merge_group` run) exactly as before.

### Q6 — does the change achieve its objective (a green `tests` job on `main`)?

Yes, and every red job is addressed. Independently re-verified in this step for `main` @ `75ca243`: `lint` failed (lint.yml run `36894698193`), `security` and `dependency-review` failed (quality.yml run `36894698244`), `tests` failed (spec-validation.yml run `36894698181`), while `coverage`, `spec-validation`, `type-check`, `dependencies`, `docs`, `migrations` succeeded — exactly the four jobs §6.7 names. Mapping: `tests` → E (+G/H/I), `security` → D, `dependency-review` → F, `lint` → C. `coverage` and `spec-validation` run the same suite (`quality.yml:59`, `spec-validation.yml:70`) and were green on that run only because the pollution family is order-dependent (`pytest-randomly`); E/G/H/I close that family for them too, so no job's redness is left unaddressed. Phase 5 evidence covers each gate: 6 consecutive clean full-suite runs (2 at the S5.1 re-run + 4 for item I, `639 passed, 1 skipped`), `ruff check .` clean (the `lint` gate), `pip-audit` clean (the `security` gate), and the trigger fix (the `dependency-review` gate). The only outstanding evidence is F's post-PR / post-merge observation (F-3), which S6.4 produces.

## Phase 6 (S6.2) — traceability + boundaries (2026-10-02)

Inputs: `git diff --name-only origin/main...HEAD` (23 files; 2 in `src/`), the S5.3 matrix section (`docs/verification/traceability.md:751-770`), the S6.1 findings table, final code state. No full-suite run (Phase 5 gate already clean).

### Findings

| # | Finding | Severity | Resolution |
|---|---|---|---|
| F-7 | `wait_for` is defined twice (`tests/settings_test_helpers.py:20`, `tests/eventbus_test_helpers.py:35`) and the new `tests/conftest.py::_drain_event_bus` imports it from the **settings** helper while draining the **event bus** | Info | **Accepted, pre-existing.** Both defs exist on `origin/main` (`git show origin/main:...`); this change added a third consumer, not the duplication. Follow-up chore: one def in `eventbus_test_helpers`, re-exported. |
| F-8 | Two bus-settlement helpers with overlapping intent: `conftest._drain_event_bus` (whole shared queue empty + 50 ms grace) vs `settings_test_helpers.set_value_settled` (ordered drain of one write's dispatch) | Info | **Accepted — different contracts, both documented.** The conftest one is fixture-local (protects the `log_records` sink from a stale `SettingChanged` → `_configure()` → `logger.remove()`); `set_value_settled` is the item-G fix for REQ-015/AC-020 ordering. No duplicated wait loop (conftest reuses `wait_for`). |
| F-9 | `set_value_settled` reads `registry._event_bus` (private attribute) — the registry exposes no public bus accessor | Info | **Accepted.** Test-only reach-through, no product API change and no new public interface (out of ISSUE scope). Noted as a follow-up for a future settings change. |

No High/Medium findings. Boundaries and docs placement: clean.

### Q1 — traceability completeness
All nine items have matrix rows (`traceability.md:756-765`) with spec ID + test + status + commit; every affected ID also has its own updated row in the owning feature matrix (e.g. `:16` REQ-001/AC-001, `:58` REQ-005/AC-008, `:100` REQ-010/AC-014, `:117` REQ-022/AC-030, `:135`/`:398` INV-009/INV-002, `:221`/`:702` INV-003, `:409` EDGE-008, `:529` INV-002). Verified by collection, not reading: `pytest --collect-only tests/unit/settings/test_repository_roundtrip.py tests/unit/logging/test_logging_sink_ownership.py -q` → **5 collected**, and the five node ids match the matrix names verbatim (`test_yaml_value_roundtrip_nel`, `test_yaml_template_roundtrip_nel`, `test_reconfigure_replaces_only_the_managed_sinks`, `test_reconfigure_keeps_foreign_sink`, `test_reconfigure_after_external_removal_of_a_managed_sink`) — no row points at a node that no longer exists (F-6 closed).

### Q2 — orphaned tests
The two new test files are referenced in the matrix (4 hits). The three chore-touched test files (`test_check_api.py`, `test_enforcement.py`, `test_performance.py`) have no spec ID in the item-C row by design (chore, no behavior delta) but are **not orphans** — they are pre-existing tests already covered by the User Roles & Permissions matrix rows. Items D/F have no test by nature (lockfile, CI trigger) and are recorded as `n/a`.

### Q3 — feature boundaries
`src/backend/settings/repository.py:28` imports `from backend.logging import logged_class` — the logging feature's **public** interface (`backend/logging/__init__.py:10`), not `_setup`/`_decorator`. `src/backend/logging/_setup.py` imports only intra-feature internals (`backend.logging._decorator`, `._settings`) plus `from backend.settings import SettingChanged` (`:121`, public package interface, function-local). No feature imports another feature's `_`-prefixed module. Touched test files live in the matching area (`tests/unit/settings/`, `tests/unit/logging/`, `tests/property/<feature>/`, `tests/{acceptance,contract}/permissions/`).

### Q4 — no premature abstraction / no new layer
`git diff --name-status` adds exactly two files, both tests, in directories that already exist on `main` (`tests/unit/settings`, `tests/unit/logging`). `src/` has two modified files, no new package, no new ABC, no new pattern — item E's state (`_sink_state`) is a module-level structure inside `backend/logging/_setup.py`, item I's is an autouse conftest fixture (process-global stdlib root logger ⇒ correctly conftest-owned, not feature-owned).

### Q5 — docs placement
Non-`.py`/`uv.lock`/`quality.yml` diff: `AI_Questions.md` (repo root, per the AI-Questions mechanism), `docs/verification/main-ci-green.md`, `docs/verification/traceability.md`, `docs/workflow/PROBLEMS.md`. Nothing written to `docs/` root; no `userdocs/` change is required (no user-facing behavior delta — see the §"no-behavior-delta statement").

## Phase 6 — review report (2026-10-02)

S6.3 consolidates the S6.1 (F-1…F-6) and S6.2 (F-7…F-9) findings into one report and closes the
Phase 6 gate. Docs-only: no new review pass, no test run, no re-review of recorded evidence.

### Verdict

**REVIEW: CLEAN** — every finding is Resolved or Accepted-with-reason; F-3 is carried to S6.4
because its CI proof can only exist once the PR is open / the merge lands. No High/Medium finding
is open, and the ISSUE clean-review criteria hold (checklist below).

### Findings

| # | finding | severity | status |
|---|---|---|---|
| F-1 | item C also re-wraps the `BOOTSTRAP_SYSTEM_PERMISSIONS` literal (indentation only) | Low | Resolved — non-behavior, inside item C's predicted file set |
| F-2 | item D's lock diff adds an edge `virtualenv → packaging` | Info | Resolved — `packaging` already locked; no new dependency |
| F-3 | item F's CI evidence is half-pending (post-PR / post-merge observation) | Info | Carried to S6.4 — no branch protection, so nothing blocks |
| F-4 | the `deadline=` widenings reduce slow-example detection | Low | Accepted-with-reason — harness tolerance, not a product budget |
| F-5 | `_sink_state` is module-global and mutated without a lock | Info | Accepted-with-reason — same exposure pre-fix; `Event` guard intact |
| F-6 | test-name drift vs the §7 plan | Info | Resolved — S5.3 rows use the final names; all node ids collect |
| F-7 | `wait_for` is defined twice; conftest imports it from the settings helper | Info | Accepted-with-reason — pre-existing duplication; follow-up chore |
| F-8 | two bus-settlement helpers with overlapping intent | Info | Accepted-with-reason — different contracts, both documented |
| F-9 | `set_value_settled` reads `registry._event_bus` (private attribute) | Info | Accepted-with-reason — test-only reach-through, no product API change |

### Criteria checklist (ISSUE clean review)

- [x] Reproduction tests GREEN — `5 passed in 0.24s` (S5.4 re-run at `f0b6d84`; S6.1 re-run `5 passed in 0.27s`).
- [x] Full regression clean — `639 passed, 1 skipped` on 6 consecutive runs (2 at the S5.1 re-run, 4 for item I); the single skip is pre-existing (symlinks unavailable on this host).
- [x] lint / types / deptry / pip-audit / alembic / mkdocs — `All checks passed!` / `Success: no issues found in 73 source files` / `Success! No dependency issues found.` / `No known vulnerabilities found` / `Running upgrade eace2f772150 -> d94b7f2e6a31` / `Documentation built in 1.50 seconds`.
- [x] Traceability updated, no orphans — nine item rows (`traceability.md:756-765`) plus per-feature rows; both new test files referenced; the chore-touched test files are pre-existing covered tests.
- [x] Feature boundaries respected — only public cross-feature imports (`backend.logging`, `backend.settings`); no `_`-prefixed cross-feature import; tests live in the matching areas.
- [x] No test weakened / deleted / skipped / xfail'd — `git diff origin/main...HEAD -- tests/ | grep '^-.*assert '` is empty; two test files added, none deleted. The only widenings are `deadline=1000` (B, H) and `deadline=500` (I): hypothesis per-example time bounds (harness tolerances; measured bases 246–356 ms), with the invariant assertions, strategies, `max_size` and `max_examples` byte-unchanged, and `HealthCheck.too_slow` already suppressed on `main`. The widened hypothesis alphabet (A) is strictly widening.
- [x] No behavior beyond the affected spec IDs — only two `src/` files: settings YAML emission style (A) and loguru sink ownership on reconfigure (E); both re-verified COMPLIANT in S6.1 Q3.
- [x] No spec amendment needed — the change stays ISSUE (S6.1 Q3).
- [x] Docs placement correct — `AI_Questions.md`, `docs/verification/*`, `docs/workflow/PROBLEMS.md`; nothing written to `docs/` root; no `userdocs/` change (no user-facing behavior delta).

### Follow-ups carried out of this change (not fixed here)

- `ruff format --check .` repo drift: 72 files would be reformatted (pre-existing; CI gates `ruff check`, not format).
- `tests/architecture/` does not exist although AGENTS.md and the verify skill reference it (repo/docs reconciliation).
- Untracked `data/` and `logs/` test artifacts — a `.gitignore` gap.
- Stale `RED` rows in the logging and settings-coverage matrices (superseded by the S5.3 rows).
- `migrations/env.py` `fileConfig` alternative fix — needs a spec check before changing.
- Duplicated `wait_for` helpers (F-7) — one definition in `eventbus_test_helpers`, re-exported.
- `set_value_settled` reads `registry._event_bus` (F-9) — needs a public settings accessor.

### Version bump decision (S6.4)

ISSUE → `patch` per AGENTS.md. Current `pyproject.toml:4` `version = "0.5.0"` → target **`0.5.1`**
(`bump-my-version bump patch --dry-run` first; clean working tree; `tag = false`).

## Phase 6 (S6.4) — bump + PR (2026-10-02)

- Pre-merge regression gate (full suite, one run): `639 passed, 1 skipped, 33 warnings in 176.10s` — GREEN.
- Version bump: `bump-my-version bump patch` → `0.5.0` → `0.5.1` (commit `c6fd876`, only `pyproject.toml`: `version` + `current_version`; `tag = false`, no tag created).
- `uv lock` synced the lock self-version only (`python-template v0.5.0 -> v0.5.1`); committed as `e783cdc` `chore(deps): sync uv.lock self-version to 0.5.1`.
- Branch pushed: `issue/main-ci-green` → `origin` (new upstream).
- PR opened for human review/merge: https://github.com/jackthenet/python-template/pull/58 (base `main`). NOT merged (human governance).
- ruff: n/a (no source/test changes in this step).

## Phase 4 (S4.2, item J) — bandit findings unmasked by the pip-audit fix (2026-10-02)

Commit `6ce0531` `fix(main-ci-green): suppress bandit false positives in feature action descriptions (B105 x5, B110)` — 4 files, +6/−6; every added line is byte-identical to the removed line plus a trailing `# nosec BXXX` comment.

**Why it was invisible until now.** The `security` job runs `pip-audit` (`.github/workflows/quality.yml:41`) **before** `bandit -r src/` (`:43`). On `main` pip-audit failed, so bandit never executed. Fixing pip-audit (item D) unmasked six pre-existing low-severity findings.

**The six findings.** B105 (string assigned to a variable named `..._permission`-style password-ish name) on permission **description** strings: `src/backend/authentication/feature_actions.py:28,29`, `src/backend/mail/feature_actions.py:24`, `src/backend/usermanagement/feature_actions.py:29,30`; and B110 (`try/except/pass`) at `src/backend/permissions/service.py:482`. All are false positives — descriptions are literal human-readable text, and the B110 block is a deliberate best-effort swallow.

**Pattern.** Inline `# nosec BXXX`, identical to the `crosscut/search` branch's `8b3064c` (which additionally suppresses B101 and a `search/service.py` B105 that does not exist on this branch), so that commit becomes redundant once PR #54 is rebased onto this one.

**Gates.** `uv run bandit -r src/` → all severity counts 0, exit 0 (was 6 Low). `uv run ruff check` + `ruff format --check` clean on the four paths. Targeted regression `uv run pytest tests/unit/permissions tests/unit/usermanagement tests/unit/mail tests/unit/authentication` → `76 passed in 9.12s`.

**No behavior delta.** Comment-only change; no code semantics changed; the full suite is unaffected, so the Phase 5 evidence stands. The `security` job is now the only remaining CI gate that was red for a *newly surfaced* reason (`tests`/`coverage` were still running at the time of writing).

## Phase 4 (S4.2, item K) — the 500ms deadline was too tight for CI (2026-10-02)

**CI evidence (run 37040033246, `coverage` job).** `FAILED tests/property/filemanagement/test_filemanagement_properties.py::test_inv_001_no_partial_state_on_failure - DeadlineExceeded('Test took 739.77ms, which exceeds the deadline of 500.00ms. ...') [single exception in FlakyFailure]` — `1 failed, 639 passed, 1068 warnings in 176.25s`, `Required test coverage of 92.0% reached. Total coverage: 93.57%`. Coverage was not the problem; the deadline was. The `tests` job (run 37040033282) passed on a different random seed.

**Fix (decorator-only).** All eight `@settings` blocks in `tests/property/filemanagement/test_filemanagement_properties.py` now use `deadline=2000` (was 500, the value item I copied from the sibling avatar test), and the module docstring records the measurement basis: locally every example stays well under 500 ms, CI's worst example measured 739.77 ms, so 2000 ms ≈ 2.7× the CI worst — a real bound with headroom for a loaded runner, never a removed assertion (Q-128). No strategy, `max_examples`, `max_size`, assertion, or skip changed; the file is uniform rather than per-test, because every test in it builds a SQLite engine and the CI runner is the binding condition for all of them.

**The test still asserts a real post-condition** (non-vacuity, by reading, no `src/` sabotage): `assert list(repo.list_by_namespace(None)) == []  # no metadata record` (storage-fault branch), `assert not mem.exists(key)  # no orphaned storage content` (metadata-fault branch), and `assert r.size == len(content)` / `assert mem.exists(key)` (success branch).

**Local runs.** `uv run pytest tests/property/filemanagement -q --tb=line --color=no` → `8 passed in 7.55s`. Stress of the failing node: `...::test_inv_001_no_partial_state_on_failure` → `1 passed in 1.11s`, then `1 passed in 1.05s`.

**Gates.** `uv run ruff check <path>` → `All checks passed!`; `uv run ruff format --check <path>` → `1 file already formatted`.

Commit `28545d2` `test(main-ci-green): raise filemanagement property deadline to CI-measured 2000ms` — 1 file, +16/−9.
