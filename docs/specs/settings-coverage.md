# Spec: Settings Coverage

## 1. Overview & Objectives
- **Feature Name:** Settings Coverage
- **Target Component:** `src/backend/settings/` (extended), `src/backend/logging/`, `src/backend/authentication/`, `src/backend/usermanagement/`, `src/backend/eventbus/`, `src/main.py`
- **Goal:** Make the settings feature the **single source of truth** for all configuration. No feature may manage its own configuration internally (hardcoded constructor defaults or a private settings model). Every feature registers its settings with the shared settings registry and reads them live, so configuration is centralized, validated, observable, and persisted.

## 2. Architecture & Design Decisions
- **Design Pattern:** Feature-owned registration (each feature exposes a `register_settings(registry)` function), centralized wiring in the entrypoint (`src/main.py`), live reads (features call `get_value` on each use), and a value-persistence repository (single YAML file).
- **Dependencies:** `pydantic` (existing), `pyyaml` (existing — reused for value persistence), `backend.eventbus` (feature), `backend.logging`/loguru (feature). No new third-party packages.
- **Constraints:**
  - The settings registry is the single source of truth for configuration; no feature keeps its own configuration.
  - No environment-variable handling (the settings feature is the single source of truth; env vars are out of scope).
  - Backend only (no frontend renderer in this feature).
  - Live reads must be in-memory (no per-read file I/O); the registry loads persisted values once at construction.
  - Persisted values take precedence over definition defaults (priority: persisted > default).
  - All current values are persisted (including values equal to their default).
  - Existing constructor parameters are retained for DI/testing; their default becomes the registry value, and an explicit argument wins.
  - Reading an unregistered key falls back to the feature's original hardcoded default and logs a warning.
  - The EventBus ↔ registry bootstrapping cycle is resolved with a guarded read (no side effect).
- **Design Decisions:**
  - D1: Feature-owned `register_settings(registry)` functions, called once by `src/main.py` at startup (no import side effects).
  - D2: Features read settings **live** (`get_value` on each use) so `set_value` affects running features; the logging feature is the exception — it subscribes to `SettingChanged` and reconfigures the sink at runtime.
  - D3: A new `LIST` setting kind is added to the settings feature (for `usermanagement.roles`), with a `ListSpec` (per-item pattern, min/max item count, duplicate control).
  - D4: Value persistence via a `ValueRepository` abstraction and a `YamlValueRepository` (single `values.yaml`, atomic write), so the storage format can change in the future.
  - D5: The registry getter supports a guarded read `get_settings_registry(required=False) -> SettingsRegistry | None` (no side effect) to resolve the EventBus bootstrapping cycle.
  - D6: `setup_logger()` takes no arguments and reads `logging.*` from the shared registry.
  - D7: The logging feature's stub `Settings` model is removed; the logging feature reads `log_*` values from the registry.
  - D8: Key prefix = full feature name (`logging.*`, `authentication.*`, `usermanagement.*`, `eventbus.*`); category = domain (`application`/`security`), group = feature name.
  - D9: Tracing — `register_settings` functions are `@logged`; per-operation live reads are traced only when the observed value changes.

## 3. Data Structures & API Schemas

### 3.1 New `LIST` kind — `ListSpec`

```python
# Extension of the settings feature's data structures (module: backend.settings.models).
from pydantic import BaseModel

class ListSpec(BaseModel):
    """Kind-specific parameters for the LIST setting kind (REQ-006)."""
    item_pattern: str | None = None   # regex each item must fullmatch
    min_items: int | None = None      # minimum number of items (>= 0)
    max_items: int | None = None      # maximum number of items (>= 0)
    allow_duplicates: bool = True     # whether duplicate items are permitted
```

- `SettingKind` gains `LIST` (the 7th kind).
- `SettingDefinition` gains an optional `list_spec: ListSpec | None` field, validated exactly like the existing `slider_spec` / `select_spec`:
  - `LIST` **requires** a `ListSpec` (present or the default `ListSpec()`); a `LIST` definition without a valid `ListSpec` is rejected.
  - Non-LIST kinds **reject** a `ListSpec` (`SettingsValidationError`).
  - `ListSpec` is invalid when `min_items > max_items`, or `item_pattern` is not a valid regex, or `min_items`/`max_items` is negative.

### 3.2 Value persistence — `ValueRepository`

```python
# New repository abstraction (module: backend.settings.repository).
class ValueRepository(ABC):
    """Persists the registry's current values (REQ-010)."""
    @abstractmethod
    def load(self) -> dict[str, Any] | None: ...
    @abstractmethod
    def save(self, values: dict[str, Any]) -> None: ...

class YamlValueRepository(ValueRepository):
    """Single `values.yaml` file, safe YAML, atomic write, thread-safe (REQ-010)."""
    def __init__(self, directory: str) -> None: ...
```

- `SettingsRegistry` gains a `value_repository: ValueRepository | None = None` constructor parameter. When `None`, the registry uses a default `YamlValueRepository("settings")` (hardcoded default directory `"settings"`).
- The registry **loads** persisted values at construction (if a value repository is present) and **persists** all current values on every change (`set_value`, `reset`, `reset_all`, and template loads).

### 3.3 Feature-owned registration API

```python
# Each feature module exposes (module: backend.<feature>):
def register_settings(registry: SettingsRegistry) -> None: ...

# Entrypoint wiring (src/main.py):
from backend.settings import get_settings_registry
reg = get_settings_registry()
logging.register_settings(reg)
authentication.register_settings(reg)
usermanagement.register_settings(reg)
eventbus.register_settings(reg)
setup_logger()  # no args; reads logging.* from the registry
```

### 3.4 Guarded registry getter

```python
# Extension of the settings feature's public API (module: backend.settings):
def get_settings_registry(required: bool = True) -> SettingsRegistry | None: ...
```

- `required=True` (default): current behavior — returns the singleton, creating it if missing.
- `required=False`: returns the singleton **if it already exists**, else `None` — **no side effect** (the singleton is never created). Used by the EventBus constructor to resolve the bootstrapping cycle.

### 3.5 Complete settings inventory

| Feature | Key | Kind | Default | Parameters | Category | Group |
|---------|-----|------|---------|------------|----------|-------|
| logging | `logging.log_level` | SELECT | `"INFO"` | options `[DEBUG, INFO, WARNING, ERROR, CRITICAL]` | application | logging |
| logging | `logging.log_file` | TEXT | `"logs/app.log"` | — | application | logging |
| logging | `logging.log_max_bytes` | NUMBER | `10485760` | min `1` | application | logging |
| logging | `logging.log_backup_count` | NUMBER | `5` | min `0` | application | logging |
| logging | `logging.profiling_include_arguments` | BOOLEAN | `False` | — | application | logging |
| authentication | `authentication.session_ttl` | NUMBER | `604800` | min `1` (seconds) | security | authentication |
| authentication | `authentication.reset_token_ttl` | NUMBER | `900` | min `1` (seconds) | security | authentication |
| authentication | `authentication.max_failed_attempts` | NUMBER | `5` | min `1` | security | authentication |
| authentication | `authentication.lockout_duration` | NUMBER | `900` | min `1` (seconds) | security | authentication |
| authentication | `authentication.rp_id` | TEXT | `"localhost"` | — | security | authentication |
| authentication | `authentication.rp_name` | TEXT | `"Python Template"` | — | security | authentication |
| authentication | `authentication.origin` | TEXT | `"http://localhost:3000"` | — | security | authentication |
| usermanagement | `usermanagement.roles` | LIST | `["admin", "member"]` | `item_pattern ^[a-z0-9_-]{1,32}$`, `min_items 1` | security | usermanagement |
| eventbus | `eventbus.max_queue_size` | NUMBER | `1000` | min `1` | application | eventbus |

- Time-based settings are stored as **NUMBER in seconds**; the feature converts to `timedelta` at read time.
- The settings feature (the registry itself) registers no settings of its own (it is the source of truth; its persistence directory is a constructor parameter, default `"settings"`).

## 4. Requirements

Each normative requirement MUST have a stable ID. These IDs propagate through the lifecycle:
`REQ-001 → AC-001 → test → task → implementation`.

| ID | Requirement |
|----|-------------|
| REQ-001 | Each feature module (`logging`, `authentication`, `usermanagement`, `eventbus`) exposes a `register_settings(registry)` function that registers the feature's `SettingDefinition`s with the given registry. Registration has no import side effects (importing a feature module does not mutate the registry singleton). |
| REQ-002 | The entrypoint (`src/main.py`) calls each feature's `register_settings(registry)` once at startup, before any feature code runs, using the shared registry from `get_settings_registry()`. |
| REQ-003 | Features read their settings **live** from the registry (`get_value` on each use), so a `set_value` affects a running feature without re-construction. |
| REQ-004 | Existing feature constructor parameters are retained for DI/testing; their default becomes the registry value, and an explicit argument wins over the registry value. |
| REQ-005 | Reading an unregistered key falls back to the feature's original hardcoded default and logs a warning (the feature works without wiring). |
| REQ-006 | The settings feature provides a new `LIST` setting kind with a `ListSpec` (per-item `item_pattern`, `min_items`, `max_items`, `allow_duplicates`). |
| REQ-007 | The settings feature validates `LIST` values: the value is a list of strings; each item fullmatches `item_pattern` (when set); the item count is within `[min_items, max_items]` (when set); duplicates are rejected when `allow_duplicates` is `False`. Invalid values raise `SettingsValidationError`. |
| REQ-008 | The settings feature validates `LIST` definitions: `LIST` requires a valid `ListSpec`; non-LIST kinds reject a `ListSpec`; a `ListSpec` is invalid when `min_items > max_items`, `item_pattern` is not a valid regex, or `min_items`/`max_items` is negative. Invalid definitions raise `SettingsValidationError`. |
| REQ-009 | The settings feature persists **all** current values to the value repository on every change (`set_value`, `reset`, `reset_all`, template loads), and loads them at construction. |
| REQ-010 | The settings feature provides the `ValueRepository` abstraction (`load`/`save`) and a `YamlValueRepository` (single `values.yaml`, safe YAML, atomic write, thread-safe, directory created if missing). |
| REQ-011 | Persisted values take precedence over definition defaults (priority: persisted > default). A persisted value is applied to the setting at load time. |
| REQ-012 | The registry getter supports a guarded read: `get_settings_registry(required=False) -> SettingsRegistry | None` returns the singleton if it already exists, else `None`, with **no side effect** (the singleton is never created). `required=True` (default) preserves the current create-if-missing behavior. |
| REQ-013 | The `EventBus` constructor resolves the bootstrapping cycle with a guarded read: if the registry already exists (`get_settings_registry(required=False)` is not `None`), it reads `eventbus.max_queue_size` from the registry; otherwise it uses the hardcoded default `1000`. No infinite recursion. |
| REQ-014 | `setup_logger()` takes no arguments and reads `logging.*` from the shared registry (falling back to the logging defaults with a warning if unregistered). It is idempotent (a second call is a no-op). |
| REQ-015 | The logging feature subscribes to `SettingChanged` and reconfigures the sink at runtime when any `logging.*` setting changes, re-applying all current `logging.*` values. |
| REQ-016 | The logging feature's stub `Settings` model (`src/backend/logging/settings.py`) is removed; the logging feature reads `log_*` values from the registry. |
| REQ-017 | Each feature's settings use the full feature name as the key prefix: `logging.*`, `authentication.*`, `usermanagement.*`, `eventbus.*`. |
| REQ-018 | Each feature's settings use `category` = domain (`application`/`security`) and `group` = feature name for the views hierarchy. |
| REQ-019 | The complete settings inventory (key, kind, default, parameters, category, group for every feature setting) is as defined in section 3.5. |
| REQ-020 | Tracing: `register_settings` functions are traced with `@logged`; per-operation live reads are traced only when the observed value differs from the feature's previously observed value for that key. |
| REQ-021 | The settings feature performs no environment-variable handling (the settings feature is the single source of truth; env vars are out of scope). |
| REQ-022 | The settings feature registers no settings of its own; its value-persistence directory is a `SettingsRegistry` constructor parameter (default `YamlValueRepository("settings")`). |

## 5. Acceptance Criteria

Each acceptance criterion MUST have a stable ID and MUST reference at least one requirement. Use Given/When/Then format.

| ID | References | Criterion |
|----|------------|-----------|
| AC-001 | REQ-001 | **Given** a feature module and a registry, **When** `register_settings(registry)` is called, **Then** the feature's `SettingDefinition`s are registered in the registry. |
| AC-002 | REQ-001 | **Given** a feature module, **When** it is imported, **Then** the registry singleton is not mutated (no import side effects). |
| AC-003 | REQ-002 | **Given** `src/main.py`, **When** it is executed, **Then** all features' settings are registered in the shared registry before any feature code runs. |
| AC-004 | REQ-003 | **Given** a running feature, **When** `set_value(key, value)` is called, **Then** the feature's next operation uses `value` (no re-construction). |
| AC-005 | REQ-004 | **Given** a feature constructor, **When** it is called without explicit arguments, **Then** the registry value is used; **When** it is called with an explicit argument, **Then** the explicit argument wins. |
| AC-006 | REQ-005 | **Given** a feature, **When** it reads an unregistered key, **Then** the original hardcoded default is returned **And** a warning is logged. |
| AC-007 | REQ-006 | **Given** the settings feature, **When** a `LIST` `SettingDefinition` is constructed with a `ListSpec`, **Then** it is accepted. |
| AC-008 | REQ-007 | **Given** a `LIST` setting with `item_pattern ^[a-z0-9_-]{1,32}$`, **When** `set_value(key, ["admin", "member"])` is called, **Then** it is accepted; **When** `set_value(key, ["Admin"])` is called, **Then** `SettingsValidationError` is raised. |
| AC-009 | REQ-007 | **Given** a `LIST` setting with `min_items=1`, **When** `set_value(key, [])` is called, **Then** `SettingsValidationError` is raised. |
| AC-010 | REQ-007 | **Given** a `LIST` setting with `allow_duplicates=False`, **When** `set_value(key, ["a", "a"])` is called, **Then** `SettingsValidationError` is raised. |
| AC-011 | REQ-008 | **Given** a `LIST` `SettingDefinition` with `min_items=5, max_items=2`, **When** it is constructed, **Then** `SettingsValidationError` is raised. |
| AC-012 | REQ-008 | **Given** a `TEXT` `SettingDefinition` with a `ListSpec`, **When** it is constructed, **Then** `SettingsValidationError` is raised. |
| AC-013 | REQ-009 | **Given** a registry with a value repository, **When** `set_value(key, value)` is called, **Then** all current values are persisted to the value repository. |
| AC-014 | REQ-010 | **Given** a `YamlValueRepository`, **When** `save(values)` is called, **Then** `values.yaml` is written atomically; **When** `load()` is called, **Then** the values are returned. |
| AC-015 | REQ-011 | **Given** a registry with persisted values, **When** it is constructed, **Then** the persisted values are applied (precedence over the defaults). |
| AC-016 | REQ-012 | **Given** the registry does not exist, **When** `get_settings_registry(required=False)` is called, **Then** `None` is returned **And** the singleton is not created. |
| AC-017 | REQ-013 | **Given** the registry does not exist, **When** `EventBus()` is constructed, **Then** `max_queue_size=1000` is used **And** no infinite recursion occurs. |
| AC-018 | REQ-013 | **Given** the registry exists with `eventbus.max_queue_size=500`, **When** `EventBus()` is constructed, **Then** `max_queue_size=500` is used. |
| AC-019 | REQ-014 | **Given** the shared registry, **When** `setup_logger()` is called, **Then** `logging.*` is read from the registry. |
| AC-020 | REQ-015 | **Given** a configured logging sink, **When** `set_value("logging.log_level", "DEBUG")` is called, **Then** the sink is reconfigured to `DEBUG`. |
| AC-021 | REQ-016 | **Given** the logging feature, **When** it is imported, **Then** the stub `Settings` model does not exist. |
| AC-022 | REQ-017 | **Given** a feature's settings, **When** they are registered, **Then** the keys use the full feature name as the prefix. |
| AC-023 | REQ-018 | **Given** a feature's settings, **When** they are registered, **Then** `category` = domain **And** `group` = feature name. |
| AC-024 | REQ-019 | **Given** the inventory, **When** all features' settings are registered, **Then** the keys, kinds, and defaults match the inventory. |
| AC-025 | REQ-020 | **Given** a `register_settings` function, **When** it is called, **Then** it is traced; **Given** a live read, **When** the observed value changes, **Then** it is traced. |
| AC-026 | REQ-021 | **Given** the settings feature, **When** it is used, **Then** no environment variables are read. |
| AC-027 | REQ-022 | **Given** the settings feature, **When** it is used, **Then** it registers no settings of its own. |

## 6. Invariants

State invariants that hold over a large input space. These become Hypothesis property-based tests.

| ID | Invariant |
|----|-----------|
| INV-001 | For every registered setting, `get_value(key)` returns a value that is valid for the setting's kind. |
| INV-002 | For a `LIST` setting, a persisted value round-trips: `save(values)` then `load()` returns the same value. |
| INV-003 | For any feature, a live read after `set_value(key, value)` returns `value`. |
| INV-004 | `register_settings(registry)` called with a fresh registry always succeeds; called twice on the same registry raises `SettingsRegistrationError` (duplicate keys). |
| INV-005 | For every setting in the inventory, the persisted value (if any) takes precedence over the default: `get_value(key)` returns the persisted value when one exists. |

## 7. Edge Cases & Error Conditions

| ID | Condition | Expected Behavior |
|----|-----------|-------------------|
| EDGE-001 | `EventBus()` constructed when the registry does not exist | `max_queue_size=1000` (hardcoded default); no infinite recursion. |
| EDGE-002 | A feature reads an unregistered key | The original hardcoded default is returned; a warning is logged. |
| EDGE-003 | A corrupted `values.yaml` is loaded | `ValueStorageError` is raised on load (fail-fast, consistent with template behavior). |
| EDGE-004 | A missing `values.yaml` is loaded | `load()` returns `None` (defaults are used). |
| EDGE-005 | A `LIST` value contains an item that does not match `item_pattern` | `SettingsValidationError` is raised. |
| EDGE-006 | A `LIST` `SettingDefinition` has `min_items > max_items` | `SettingsValidationError` is raised on construction. |
| EDGE-007 | `setup_logger()` is called twice | The second call is a no-op (idempotent). |
| EDGE-008 | A `logging.*` setting changes (e.g., `log_max_bytes`) | The sink is reconfigured, re-applying all current `logging.*` values (rotation parameters require sink replacement). |
| EDGE-009 | All values are persisted (including those equal to their default) | All current values are written to `values.yaml`. |
| EDGE-010 | A live read observes a value equal to the previously observed value | No trace is logged (traced only on change). |
| EDGE-011 | `get_settings_registry(required=False)` called when the registry does not exist | `None` is returned; the singleton is never created. |
| EDGE-012 | A `LIST` value is not a list of strings (e.g., a number) | `SettingsValidationError` is raised. |

## 8. Non-Functional Requirements

| ID | Category | Requirement |
|----|----------|-------------|
| NFR-001 | Performance | Live reads are in-memory (no per-read file I/O); the registry loads persisted values once at construction. |
| NFR-002 | Security | Settings values are not secrets; no credential storage. Settings do not contain passwords or tokens. |
| NFR-003 | Contract | The settings inventory (key, kind, default) is backward-compatible; adding a setting is non-breaking. |
| NFR-004 | Observability | `register_settings` functions and change-detection live reads are logged per the logging policy. |
| NFR-005 | Atomicity | Persistence uses atomic writes (the file is always either absent or valid YAML). |
| NFR-006 | Thread safety | The registry and `ValueRepository` are thread-safe. |

## 9. Observability & Logging

Every feature MUST be observable. Specify the logging behavior: which operations are logged, at what level, and with what context. Shared infrastructure features MUST log entry points, errors, and lifecycle events; verbose tracing belongs at DEBUG (off by default).

| Operation / Event | Level | Context |
|-------------------|-------|---------|
| `register_settings` called | DEBUG | feature name, count of settings registered |
| Live read observes a changed value | DEBUG | key, previous value, new value |
| Feature reads an unregistered key | WARNING | key, fallback default used |
| `setup_logger` called | INFO | log level, log file |
| Logging sink reconfigured on change | INFO | key, new value |
| Values persisted | DEBUG | count of values persisted |
| Values loaded | DEBUG | count of values loaded |
| Corrupted `values.yaml` loaded | ERROR | exception |

- **Default level:** INFO; verbose tracing at DEBUG.
- **Error conditions:** A corrupted `values.yaml` is an error (logged at ERROR, `ValueStorageError` raised). An unregistered key is a warning (logged at WARNING, fallback used).

## 10. Test Strategy

Map each requirement/AC to a test category. This drives the test file layout.

| ID | Test Category | Test File | Test Function |
|----|---------------|-----------|---------------|
| AC-001 | acceptance | `tests/acceptance/settings_coverage/test_registration.py` | `test_register_settings_registers` |
| AC-002 | unit | `tests/unit/test_settings_coverage.py` | `test_no_import_side_effects` |
| AC-003 | acceptance | `tests/acceptance/settings_coverage/test_wiring.py` | `test_main_wires_all_features` |
| AC-004 | acceptance | `tests/acceptance/settings_coverage/test_live_reads.py` | `test_set_value_affects_running_feature` |
| AC-005 | acceptance | `tests/acceptance/settings_coverage/test_constructor_defaults.py` | `test_constructor_default_registry_value` |
| AC-006 | unit | `tests/unit/test_settings_coverage.py` | `test_unregistered_key_fallback` |
| AC-007 | unit | `tests/unit/test_settings_coverage.py` | `test_list_definition_accepted` |
| AC-008 | unit | `tests/unit/test_settings_coverage.py` | `test_list_value_validation` |
| AC-009 | unit | `tests/unit/test_settings_coverage.py` | `test_list_min_items` |
| AC-010 | unit | `tests/unit/test_settings_coverage.py` | `test_list_no_duplicates` |
| AC-011 | unit | `tests/unit/test_settings_coverage.py` | `test_list_min_gt_max_rejected` |
| AC-012 | unit | `tests/unit/test_settings_coverage.py` | `test_list_spec_on_text_rejected` |
| AC-013 | acceptance | `tests/acceptance/settings_coverage/test_persistence.py` | `test_set_value_persists` |
| AC-014 | contract | `tests/contract/settings_coverage/test_value_repository.py` | `test_yaml_value_repository` |
| AC-015 | acceptance | `tests/acceptance/settings_coverage/test_persistence.py` | `test_persisted_precedence` |
| AC-016 | unit | `tests/unit/test_settings_coverage.py` | `test_guarded_read_no_side_effect` |
| AC-017 | unit | `tests/unit/test_settings_coverage.py` | `test_eventbus_no_registry_default` |
| AC-018 | unit | `tests/unit/test_settings_coverage.py` | `test_eventbus_registry_value` |
| AC-019 | acceptance | `tests/acceptance/settings_coverage/test_setup_logger.py` | `test_setup_logger_reads_registry` |
| AC-020 | acceptance | `tests/acceptance/settings_coverage/test_setup_logger.py` | `test_sink_reconfigured_on_change` |
| AC-021 | unit | `tests/unit/test_settings_coverage.py` | `test_logging_stub_removed` |
| AC-022 | contract | `tests/contract/settings_coverage/test_inventory.py` | `test_key_prefix` |
| AC-023 | contract | `tests/contract/settings_coverage/test_inventory.py` | `test_category_group` |
| AC-024 | contract | `tests/contract/settings_coverage/test_inventory.py` | `test_inventory_matches` |
| AC-025 | unit | `tests/unit/test_settings_coverage.py` | `test_tracing` |
| AC-026 | unit | `tests/unit/test_settings_coverage.py` | `test_no_env_vars` |
| AC-027 | unit | `tests/unit/test_settings_coverage.py` | `test_settings_registers_nothing` |
| INV-001 | property | `tests/property/test_settings_coverage.py` | `test_get_value_valid_for_kind` |
| INV-002 | property | `tests/property/test_settings_coverage.py` | `test_list_round_trip` |
| INV-003 | property | `tests/property/test_settings_coverage.py` | `test_live_read_after_set` |
| INV-004 | property | `tests/property/test_settings_coverage.py` | `test_register_idempotent_fresh` |
| INV-005 | property | `tests/property/test_settings_coverage.py` | `test_persisted_precedence_invariant` |
| EDGE-001 | unit | `tests/unit/test_settings_coverage.py` | `test_eventbus_bootstrap_cycle` |
| EDGE-002 | unit | `tests/unit/test_settings_coverage.py` | `test_unregistered_key_warning` |
| EDGE-003 | unit | `tests/unit/test_settings_coverage.py` | `test_corrupted_values_yaml` |
| EDGE-004 | unit | `tests/unit/test_settings_coverage.py` | `test_missing_values_yaml` |
| EDGE-005 | unit | `tests/unit/test_settings_coverage.py` | `test_list_item_pattern_mismatch` |
| EDGE-006 | unit | `tests/unit/test_settings_coverage.py` | `test_list_min_gt_max` |
| EDGE-007 | unit | `tests/unit/test_settings_coverage.py` | `test_setup_logger_idempotent` |
| EDGE-008 | unit | `tests/unit/test_settings_coverage.py` | `test_sink_reconfigured_rotation` |
| EDGE-009 | unit | `tests/unit/test_settings_coverage.py` | `test_persist_all_values` |
| EDGE-010 | unit | `tests/unit/test_settings_coverage.py` | `test_live_read_no_trace_on_same` |
| EDGE-011 | unit | `tests/unit/test_settings_coverage.py` | `test_guarded_read_none` |
| EDGE-012 | unit | `tests/unit/test_settings_coverage.py` | `test_list_non_string_rejected` |
| NFR-001 | unit | `tests/unit/test_settings_coverage.py` | `test_live_read_in_memory` |
| NFR-002 | contract | `tests/contract/settings_coverage/test_inventory.py` | `test_no_secret_settings` |
| NFR-003 | contract | `tests/contract/settings_coverage/test_inventory.py` | `test_inventory_backward_compatible` |
| NFR-004 | unit | `tests/unit/test_settings_coverage.py` | `test_observability_tracing` |
| NFR-005 | contract | `tests/contract/settings_coverage/test_value_repository.py` | `test_atomic_write` |
| NFR-006 | unit | `tests/unit/test_settings_coverage.py` | `test_thread_safety` |

## 11. Traceability Matrix

Maintain this matrix as tests are written and pass. Every normative requirement MUST have at least one executable test.

| Requirement | Acceptance Criterion | Test | Status |
|-------------|---------------------|------|--------|
| REQ-001 | AC-001 | `test_register_settings_registers` | PENDING |
| REQ-001 | AC-002 | `test_no_import_side_effects` | PENDING |
| REQ-002 | AC-003 | `test_main_wires_all_features` | PENDING |
| REQ-003 | AC-004 | `test_set_value_affects_running_feature` | PENDING |
| REQ-004 | AC-005 | `test_constructor_default_registry_value` | PENDING |
| REQ-005 | AC-006 | `test_unregistered_key_fallback` | PENDING |
| REQ-006 | AC-007 | `test_list_definition_accepted` | PENDING |
| REQ-007 | AC-008 | `test_list_value_validation` | PENDING |
| REQ-007 | AC-009 | `test_list_min_items` | PENDING |
| REQ-007 | AC-010 | `test_list_no_duplicates` | PENDING |
| REQ-008 | AC-011 | `test_list_min_gt_max_rejected` | PENDING |
| REQ-008 | AC-012 | `test_list_spec_on_text_rejected` | PENDING |
| REQ-009 | AC-013 | `test_set_value_persists` | PENDING |
| REQ-010 | AC-014 | `test_yaml_value_repository` | PENDING |
| REQ-011 | AC-015 | `test_persisted_precedence` | PENDING |
| REQ-012 | AC-016 | `test_guarded_read_no_side_effect` | PENDING |
| REQ-013 | AC-017 | `test_eventbus_no_registry_default` | PENDING |
| REQ-013 | AC-018 | `test_eventbus_registry_value` | PENDING |
| REQ-014 | AC-019 | `test_setup_logger_reads_registry` | PENDING |
| REQ-015 | AC-020 | `test_sink_reconfigured_on_change` | PENDING |
| REQ-016 | AC-021 | `test_logging_stub_removed` | PENDING |
| REQ-017 | AC-022 | `test_key_prefix` | PENDING |
| REQ-018 | AC-023 | `test_category_group` | PENDING |
| REQ-019 | AC-024 | `test_inventory_matches` | PENDING |
| REQ-020 | AC-025 | `test_tracing` | PENDING |
| REQ-021 | AC-026 | `test_no_env_vars` | PENDING |
| REQ-022 | AC-027 | `test_settings_registers_nothing` | PENDING |
| INV-001 | — | `test_get_value_valid_for_kind` | PENDING |
| INV-002 | — | `test_list_round_trip` | PENDING |
| INV-003 | — | `test_live_read_after_set` | PENDING |
| INV-004 | — | `test_register_idempotent_fresh` | PENDING |
| INV-005 | — | `test_persisted_precedence_invariant` | PENDING |
| NFR-001 | — | `test_live_read_in_memory` | PENDING |
| NFR-002 | — | `test_no_secret_settings` | PENDING |
| NFR-003 | — | `test_inventory_backward_compatible` | PENDING |
| NFR-004 | — | `test_observability_tracing` | PENDING |
| NFR-005 | — | `test_atomic_write` | PENDING |
| NFR-006 | — | `test_thread_safety` | PENDING |
