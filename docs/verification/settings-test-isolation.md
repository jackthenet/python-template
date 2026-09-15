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

## Date
2026-09-15
