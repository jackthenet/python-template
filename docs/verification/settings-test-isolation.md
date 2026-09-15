# Triage: settings-test-isolation (ISSUE)

## Type
ISSUE

## Affected REQ/AC
- **REQ-014** (`docs/specs/settings.md`) — "The settings feature provides a shared default registry: `get_settings_registry()` returns a singleton **for features**, `SettingsRegistry` is **instantiable for tests/DI**, and `reset_settings_registry()` resets the default **for tests**." This establishes that the shared default registry is for features, and tests should use the instantiable `SettingsRegistry` (with an isolated repository).
- **AC-018** (`docs/specs/settings.md`) — "When `get_settings_registry()` is called twice, the same instance is returned" (singleton).
- **AGENTS.md** — "Using the Settings Feature" — "Test registries MUST pass an explicit isolated value repository (e.g., `YamlValueRepository(tempfile.mkdtemp())`) to avoid cross-test contamination from the shared default directory."

**Note on spec coverage:** The approved spec does **not** explicitly state (a) the default value repository, or (b) a test-isolation requirement.
- The default value repository is an implementation detail: `src/backend/settings/registry.py` (`SettingsRegistry.__init__`, lines 63–64) defaults `value_repository` to `YamlValueRepository("settings")` when none is passed; `get_settings_registry()` (`registry.py`, line 343) creates `SettingsRegistry()`, so it inherits that default.
- The test-isolation requirement is the **AGENTS.md** rule (cited above), which is the normative basis for this defect.

The fix is to make the offending tests follow the **existing** AGENTS.md rule — no new behavior is introduced, so the change is in scope for an ISSUE.

## Defect confirmation
- **Observed behavior:** Multiple tests instantiate the shared default settings registry — `get_settings_registry()` (no args) or `SettingsRegistry(...)` without a `value_repository` — which defaults to `YamlValueRepository("settings")` (a `settings/` directory in the repo root). All such tests write to the **same** `settings/values.yaml` file. On **Windows**, the atomic write (`os.replace` in `src/backend/settings/repository.py`, line 69) fails with `PermissionError [WinError 32]` when another process/worker has the file open — so **xdist parallel runs** (`pytest -n auto`) fail, while **sequential runs pass**.
- **Required behavior (per AGENTS.md rule + spec REQ-014):** Test registries MUST use an isolated value repository (e.g., `YamlValueRepository(tempfile.mkdtemp())`); the shared default registry is for features, and tests should use the instantiable `SettingsRegistry` with an isolated repository.
- **In scope:** The fix is to make the offending tests follow the existing AGENTS.md rule (no new behavior). If a fix required behavior the spec does not state, it would be out of scope — but it does not.

## Offending tests
Tests that instantiate the shared default settings registry **without** an isolated `value_repository`. Marked **(W)** = writer (calls `set_value`/`reset`/`reset_all` on the shared default registry — the primary cause of the conflict) and **(R)** = reader (creates the shared default registry but does not write — secondary). "(subprocess)" = the shared default registry is used inside a `subprocess.run` child that runs with `cwd` = repo root.

> Compliant (NOT offenders) — already use an isolated repository or do not touch the shared default:
> - `tests/acceptance/mail/`, `tests/contract/mail/`, `tests/integration/mail/`, `tests/property/mail/`, `tests/unit/mail/` — each has a `conftest.py` with an autouse `setup_isolated_registry()` fixture that installs an isolated `SettingsRegistry(value_repository=YamlValueRepository(tempfile.mkdtemp()))` into the singleton.
> - `tests/settings_test_helpers.py::make_registry()` — isolated `YamlValueRepository(tempfile.mkdtemp())`.
> - `tests/filemanagement_test_helpers.py` — isolated `YamlValueRepository(tempfile.mkdtemp())`.
> - `tests/property/settings/test_settings_properties.py` — isolated `YamlValueRepository(tempfile.mkdtemp())`.
> - `tests/property/test_settings_coverage.py` — uses `make_registry()` / isolated repo.
> - `tests/acceptance/settings_coverage/test_persistence.py` — uses `make_registry()` / `tmp_path`.

### `tests/conftest.py`
- fixture `_logging_session_setup` (session-scoped, autouse) — **(W)** `get_settings_registry()` + `set_value("logging.log_file", ...)` + `set_value("logging.log_level", ...)`. Runs for **every** test in the suite.

### `tests/acceptance/settings/test_settings.py`
- fixture `registry` — **(W)** `SettingsRegistry(event_bus=bus)` (no `value_repository`); used by the per-kind round-trip / reset / status tests that call `set_value`.
- fixture `registry_with_bus` — **(W)** `SettingsRegistry(event_bus=bus)` (no `value_repository`); used by the event tests that call `set_value`.
- `test_ac_018_singleton` — **(R)** `get_settings_registry()`.
- `test_ac_030_yaml_file_written` — **(R)** `SettingsRegistry(event_bus=bus, template_repository=repo)` (no `value_repository`).
- `test_ac_031_persistence_across_instances` — **(R)** `SettingsRegistry(...)` (no `value_repository`).
- `test_ac_034_storage_agnostic` — **(R)** `SettingsRegistry(event_bus=bus)` (no `value_repository`).
- `test_ac_037_custom_bus` — **(W)** `SettingsRegistry(event_bus=custom)` (no `value_repository`) + `set_value`.
- `test_ac_038_thread_safe_registration` — **(R)** `SettingsRegistry(event_bus=bus)` (no `value_repository`).

### `tests/acceptance/settings_coverage/`
- `test_constructor_defaults.py::test_constructor_default_registry_value` — **(W)** `get_settings_registry()` + `set_value`.
- `test_live_reads.py::test_set_value_affects_running_feature` — **(W)** `get_settings_registry()` + `set_value`.
- `test_setup_logger.py::test_setup_logger_reads_registry` — **(W, subprocess)** `get_settings_registry()` + `set_value`.
- `test_setup_logger.py::test_sink_reconfigured_on_change` — **(W, subprocess)** `get_settings_registry()` + `set_value`.
- `test_wiring.py::test_main_wires_all_features` — **(R, subprocess)** `get_settings_registry()`.

### `tests/acceptance/logging_coverage/`
- `test_behavior_unchanged.py::test_tracing_does_not_change_behavior` — **(W)** `SettingsRegistry(template_repository=MemoryTemplateRepository())` (no `value_repository`) + `set_value`.
- `test_direct_loguru_kept.py::test_existing_direct_loguru_kept` — **(W)** `SettingsRegistry(template_repository=MemoryTemplateRepository())` (no `value_repository`) + `set_value`.
- `test_levels.py::test_semantic_log_levels` — **(R)** `SettingsRegistry(template_repository=MemoryTemplateRepository())` (no `value_repository`).
- `test_services_traced.py::test_service_registry_classes_traced` — **(R)** `SettingsRegistry(template_repository=MemoryTemplateRepository())` (no `value_repository`).

### `tests/contract/settings/test_settings_contracts.py`
- `test_nfr_001_performance_budgets` — **(W)** `SettingsRegistry(event_bus=collector)` (no `value_repository`) + `set_value`.
- `test_nfr_003_resource_contract` — **(W)** `SettingsRegistry(event_bus=collector)` (no `value_repository`) + `set_value`.
- `test_nfr_004_observability` — **(W)** `SettingsRegistry(event_bus=collector)` (no `value_repository`) + `set_value`.

### `tests/contract/logging/test_logging_contracts.py`
- `test_nfr_001_setup_time_budget` — **(W, subprocess)** `get_settings_registry()` + `set_value`.

### `tests/contract/filemanagement/test_filemanagement_contracts.py`
- `test_nfr_001_performance_budgets` — **(W)** `shared = get_settings_registry()` + `shared.set_value("logging.log_level", ...)` (the filemanagement registry itself is isolated via `isolated_registry()`; only the `logging.log_level` read/write uses the shared default).

### `tests/integration/settings/test_settings_integration.py`
- fixture `registry` — **(W)** `SettingsRegistry(event_bus=bus)` (no `value_repository`); used by `test_template_capture_restore_workflow` which calls `set_value`.
- `test_multi_feature_reactive_settings` — **(W)** `SettingsRegistry(event_bus=bus)` (no `value_repository`) + `set_value`.

### `tests/property/logging/test_logging_properties.py`
- `test_inv_001_concurrent_setup_logger_sinks` — **(W, subprocess)** `get_settings_registry()` + `set_value`.

### `tests/property/logging_coverage/test_invariants.py`
- module helper (builds the subject inventory, ~line 45) — **(R)** `SettingsRegistry(template_repository=MemoryTemplateRepository())` (no `value_repository`).

### `tests/unit/settings/test_settings_edges.py`
- fixture `registry` — **(W)** `SettingsRegistry(event_bus=bus)` (no `value_repository`); used by the edge tests that call `set_value`.
- `test_edge_021_unchanged_value_event` — **(W)** `SettingsRegistry(event_bus=collector)` (no `value_repository`) + `set_value`.
- `test_edge_022_bus_shutdown` — **(W)** `SettingsRegistry(event_bus=bus)` (no `value_repository`) + `set_value`.
- `test_edge_027_load_unregistered_settings` — **(R)** `SettingsRegistry(event_bus=bus_a, template_repository=shared_repo)` (no `value_repository`).

### `tests/unit/logging/test_logging_edges.py`
- `test_edge_001_log_file_parent_created` — **(W, subprocess)** `get_settings_registry()` + `set_value`.

### `tests/unit/test_settings_coverage.py`
- `test_no_import_side_effects` — **(R)** `get_settings_registry()`.
- `test_unregistered_key_fallback` — **(R)** `get_settings_registry()`.
- `test_unregistered_key_warning` — **(R)** `get_settings_registry()`.
- `test_eventbus_registry_value` — **(W)** `get_settings_registry()` + `set_value`.
- `test_settings_registers_nothing` — **(R)** `get_settings_registry()`.
- `test_sink_reconfigured_rotation` — **(W)** `get_settings_registry()` + `set_value`.
- `test_live_read_no_trace_on_same` — **(R)** `get_settings_registry()`.

## Reproduction plan
- **Failing test(s) (C:P3):**
  1. **Root-cause reproduction (deterministic, platform-aware):** a test that reproduces the Windows file-lock conflict at the `YamlValueRepository` level — an atomic `save()` (`os.replace`) on the shared directory's `values.yaml` conflicts with an open file handle (simulating a concurrent xdist worker/reader) → `PermissionError [WinError 32]` on Windows. This demonstrates *why* parallel runs fail.
  2. **Fix-tie reproduction (deterministic):** a test that confirms the offending test fixtures use an isolated value repository (a temp directory) rather than the shared default `settings/` directory. It fails on the current (defective) code (offending fixtures use the shared default) and passes after the fix.
- **Fix scope (C:P4):** Make the offending test fixtures/tests pass an isolated `YamlValueRepository(tempfile.mkdtemp())` (per the AGENTS.md rule), so no test writes to the shared `settings/` directory. For subprocess-based offenders, the child code must also use an isolated repository (or a temp directory) instead of the shared default `settings/`.
- **Files expected to change (C:P4):** the offending test files listed above — `tests/conftest.py`, `tests/acceptance/settings/test_settings.py`, `tests/acceptance/settings_coverage/{test_constructor_defaults,test_live_reads,test_setup_logger,test_wiring}.py`, `tests/acceptance/logging_coverage/{test_behavior_unchanged,test_direct_loguru_kept,test_levels,test_services_traced}.py`, `tests/contract/settings/test_settings_contracts.py`, `tests/contract/logging/test_logging_contracts.py`, `tests/contract/filemanagement/test_filemanagement_contracts.py`, `tests/integration/settings/test_settings_integration.py`, `tests/property/logging/test_logging_properties.py`, `tests/property/logging_coverage/test_invariants.py`, `tests/unit/settings/test_settings_edges.py`, `tests/unit/logging/test_logging_edges.py`, `tests/unit/test_settings_coverage.py`.

## Phase 3 — reproduction test (RED)

**Reproduction test:** `tests/unit/test_settings_test_isolation.py::test_offending_tests_do_not_create_shared_settings_dir`

**Approach (deterministic, cross-platform):** Run a representative offending test in a **subprocess** (`sys.executable -m pytest <test>`, `cwd` = repo root), then assert the shared `settings/` directory at the repo root was **NOT** created by that run. The session-scoped autouse `_logging_session_setup` fixture (`tests/conftest.py`) runs for **every** test and writes to the shared default registry, so any test run reproduces the defect on the current code. The representative test is `tests/acceptance/settings/test_settings.py::test_ac_018_singleton` (fast, ~1s).

**Why it is RED on the current code:** The subprocess run constructs/writes the shared default registry (`YamlValueRepository("settings")`), which creates the shared `settings/` directory at the repo root. The assertion `assert not <repo>/settings.exists()` therefore fails.

**Why it will be GREEN after the fix:** The fix (C:P4) makes the offending fixtures/tests pass an isolated `YamlValueRepository(tempfile.mkdtemp())`, so no test constructs/writes the shared default registry and the shared `settings/` directory is not created.

**Determinism:** The subprocess run is synchronous (the test waits for it) and the `_logging_session_setup` fixture always runs and always writes to the shared default registry on the current code — no race condition. The test also cleans up the `settings/` directory in a `finally` block (it is an untracked, non-ignored defect artifact, not a repo file), keeping the worktree clean.

**RED evidence (failing test output):**

```text
$ uv run python -m pytest tests/unit/test_settings_test_isolation.py::test_offending_tests_do_not_create_shared_settings_dir --no-header -q

E           AssertionError: DEFECT (settings-test-isolation): running the offending test created the shared C:\\...\\settings-test-isolation\\settings directory at the repo root. Tests must use an isolated value repository (YamlValueRepository(tempfile.mkdtemp())), not the shared default registry. See AGENTS.md 'Using the Settings Feature'.
E           assert not True
E            +  where True = exists()
E            +    where exists = WindowsPath('C:/.../settings-test-isolation/settings').exists

tests\unit\test_settings_test_isolation.py:103: AssertionError
=========================== short test summary info ===========================
FAILED tests/unit/test_settings_test_isolation.py::test_offending_tests_do_not_create_shared_settings_dir
1 failed in 1.00s
```

**Ruff gate (this step writes a test file):** `uv run ruff check .` → `All checks passed!`

## Phase 4 — minimal fix (GREEN)

**Fix:** Every offending test fixture/test now uses an **isolated** value repository (a temp directory) instead of the shared default `settings/` directory, per the AGENTS.md rule ("Test registries MUST pass an explicit isolated value repository (e.g., `YamlValueRepository(tempfile.mkdtemp())`)"). No test behavior was changed — only the value repository was made isolated.

**How it was done:**
- A shared helper `install_isolated_registry()` was added to `tests/settings_test_helpers.py` (mirrors the compliant mail suite's `setup_isolated_registry()`): it resets the singleton and installs a fresh `SettingsRegistry(value_repository=YamlValueRepository(tempfile.mkdtemp()))` into the module singleton, returning the installed registry.
- **Primary offender** — `tests/conftest.py`'s session-scoped autouse `_logging_session_setup` fixture now calls `install_isolated_registry()` (instead of `get_settings_registry()`), so the session's `set_value("logging.log_file", ...)` / `set_value("logging.log_level", ...)` write to an isolated temp dir. Because this fixture runs for every test, the shared singleton is isolated for the whole suite.
- **Fixtures building `SettingsRegistry(...)` directly** now pass `value_repository=YamlValueRepository(tempfile.mkdtemp())`:
  - `tests/acceptance/settings/test_settings.py` — `registry`, `registry_with_bus`, and the individual tests `test_ac_030_yaml_file_written`, `test_ac_031_persistence_across_instances`, `test_ac_034_storage_agnostic`, `test_ac_037_custom_bus`, `test_ac_038_thread_safe_registration`.
  - `tests/integration/settings/test_settings_integration.py` — `registry` fixture + `test_multi_feature_reactive_settings`.
  - `tests/unit/settings/test_settings_edges.py` — `registry` fixture + `test_edge_021_unchanged_value_event`, `test_edge_022_bus_shutdown`, `test_edge_027_load_unregistered_settings`.
  - `tests/contract/settings/test_settings_contracts.py` — `test_nfr_001_performance_budgets`, `test_nfr_003_resource_contract`, `test_nfr_004_observability`.
  - `tests/acceptance/logging_coverage/{test_behavior_unchanged,test_direct_loguru_kept,test_levels,test_services_traced}.py` — the `SettingsRegistry(...)` construction in each.
  - `tests/property/logging_coverage/test_invariants.py` — the `_subjects` module helper.
- **Tests that read/write the shared singleton via `get_settings_registry()`** now install an isolated registry first (so the singleton is isolated, not a fresh default `YamlValueRepository("settings")`):
  - `tests/acceptance/settings_coverage/test_constructor_defaults.py` + `test_live_reads.py` — the autouse `_reset_registry` fixture now installs an isolated registry.
  - `tests/unit/test_settings_coverage.py` — the reader/writer tests (`test_no_import_side_effects`, `test_unregistered_key_fallback`, `test_unregistered_key_warning`, `test_eventbus_registry_value`, `test_settings_registers_nothing`, `test_sink_reconfigured_rotation`, `test_live_read_no_trace_on_same`) call `install_isolated_registry()` before `get_settings_registry()`. (The autouse `_reset_registry` fixture was kept as a bare reset so the guarded-read tests `test_guarded_read_no_side_effect` / `test_guarded_read_none` still observe a non-existent singleton.)
  - `tests/contract/filemanagement/test_filemanagement_contracts.py` — `test_nfr_001_performance_budgets` uses `install_isolated_registry()` for the `logging.log_level` read/write.
- **Subprocess offenders** (child processes run with `cwd` = repo root and do not inherit the conftest session fixture) — the child code now installs an isolated registry into the child's singleton before `set_value`/`setup_logger()`, so the child does not create the shared `settings/` dir:
  - `tests/acceptance/settings_coverage/test_setup_logger.py` — `test_setup_logger_reads_registry`, `test_sink_reconfigured_on_change`.
  - `tests/acceptance/settings_coverage/test_wiring.py` — `test_main_wires_all_features` (reader; the child's `get_settings_registry()` would otherwise create the shared dir).
  - `tests/contract/logging/test_logging_contracts.py` — `test_nfr_001_setup_time_budget`.
  - `tests/property/logging/test_logging_properties.py` — `test_inv_001_concurrent_setup_logger_sinks`.
  - `tests/unit/logging/test_logging_edges.py` — `test_edge_001_log_file_parent_created`.

**GREEN confirmation (reproduction test passes):**

```text
$ uv run python -m pytest tests/unit/test_settings_test_isolation.py -q -p no:cacheprovider
.
1 passed in 0.99s
```

**Regression suite (no new failures):**

```text
$ uv run pytest tests/ -q -p no:cacheprovider
489 passed, 1 skipped in 109.06s
```

(The single skip is pre-existing: `tests/acceptance/filemanagement/test_filemanagement.py:364` — "symlinks not available on this host".)

**Root-cause confirmation (parallel run — the original failure mode):**

```text
$ uv run pytest tests/acceptance/settings/ tests/unit/settings/ tests/contract/settings/ tests/integration/settings/ tests/acceptance/settings_coverage/ -n auto -q -p no:cacheprovider
82 passed in 19.11s
```

No `PermissionError [WinError 32]` on the parallel run — no test writes to the shared `settings/` directory.

**Ruff gate:** `uv run ruff check .` → `All checks passed!`

## Date
2026-09-15
