# Spec: Settings

## Changelog
- v2 (2026-09-11): NFR-001 amended — single-setting op budgets split: read-only ops (`get_value`, `to_view`, `get_status`) < 1 ms (median) with 1000 registered settings (unchanged); mutating ops (`register`, `set_value`, `reset`), which persist all current values to the value repository (AC-013), < 50 ms (median) with 1000 registered settings. Was: all six ops < 1 ms — unachievable given AC-013's synchronous full-value persistence (observed 13.6 ms local / 28.06 ms CI).

## 1. Overview & Objectives
- **Feature Name:** Settings
- **Target Component:** `src/backend/settings/`
- **Goal:** Provide a central, extensible settings/configuration management system for the backend. Features register typed settings with full metadata; the system validates values, provides sensible defaults, derives each setting's default status, and publishes value changes to the shared event bus. Named templates (value profiles scoped to a category/group) can be created, loaded, updated, and deleted; templates persist via a repository pattern (first implementation: YAML files), so later formats (JSON, etc.) can be swapped in.
- **Scope:** In-memory settings registry with per-kind validation; category/group hierarchy; feature-scoped registration API; renderable metadata (`SettingView`) for a future frontend; template CRUD with scope-coverage save and leave-as-is load semantics; YAML template storage via the repository pattern; event-bus integration (`SettingChanged`); loguru observability.
- **Out of Scope:** Persistence of setting definitions/values (only templates persist); HTTP API; frontend rendering; environment-variable overrides; migration of the logging feature's stub `Settings` module; multi-process synchronization; template formats other than YAML (the repository pattern is the extension point); deregistration of settings.

## 2. Architecture & Design Decisions
- **Design Pattern:** Registry with frozen Pydantic models, repository pattern for template storage, and event-bus integration.
- **Dependencies:** `pydantic` (existing), `email-validator` (new — EMAIL validation), `pyyaml` (new — YAML template storage), `backend.eventbus` (feature), `backend.logging`/loguru (feature).
- **Constraints:** Setting definitions and values are in-memory. The registry is thread-safe. Current values are always valid for their kind. The feature creates no threads or sockets of its own (file I/O only, for templates). A template's values form a complete map of its scope at creation and update time.
- **Design Decisions (WHAT; WHY goes to Phase 2 ADRs):**
  - D1: Six setting kinds (TEXT, NUMBER, BOOLEAN, EMAIL, SLIDER, SELECT), each with kind-specific parameters and per-kind validation.
  - D2: `SettingDefinition` is the single metadata model (key, kind, default, display metadata, category/group, kind parameters, validation constraints), validated at construction.
  - D3: `SettingsRegistry` is the central registry: registration (global and feature-scoped), validated value access, resets, hierarchy views, renderable views.
  - D4: Each setting's default status is derived from its value: MODIFIED when the current value differs from the default, otherwise DEFAULT.
  - D5: Templates are named value profiles scoped to a single category (and optionally one group); a template's values exactly cover the scope at creation/update time; loading sets the template's values and leaves settings not in the template as-is.
  - D6: Template storage goes through a `TemplateRepository` abstraction; the first implementation is `YamlTemplateRepository` (one file per template, safe YAML, atomic writes).
  - D7: Value changes publish `SettingChanged` to the event bus (`set_value`, `reset`, `reset_all`, and template loads); no other events are published.
  - D8: A shared default registry singleton (`get_settings_registry()` / `reset_settings_registry()`); `SettingsRegistry` is instantiable for tests/DI.

## 3. Data Structures & API Schemas

```python
from __future__ import annotations
from enum import Enum
from typing import Any

from pydantic import BaseModel


class SettingKind(str, Enum):
    """The six supported setting kinds."""

    TEXT = "text"
    NUMBER = "number"
    BOOLEAN = "boolean"
    EMAIL = "email"
    SLIDER = "slider"
    SELECT = "select"


class SettingStatus(str, Enum):
    """Default status of a setting, derived from its value."""

    DEFAULT = "default"      # current value == default
    MODIFIED = "modified"    # current value != default


class SliderSpec(BaseModel):  # frozen
    """Parameters for a SLIDER setting. Validated: min <= max, step > 0, and max lies on the step grid ((max - min) is a non-negative multiple of step)."""

    min: float
    max: float
    step: float = 1.0


class SelectOption(BaseModel):  # frozen
    """One alternative of a SELECT setting. `value` is non-empty; `label` is display metadata."""

    value: str
    label: str | None = None


class SelectSpec(BaseModel):  # frozen
    """Parameters for a SELECT setting. Validated: options non-empty, option values unique."""

    options: list[SelectOption]


class SettingDefinition(BaseModel):  # frozen
    """Complete metadata for one setting. Validated at construction (REQ-001, REQ-004)."""

    key: str            # matches ^[a-zA-Z_][a-zA-Z0-9_]*(\.[a-zA-Z_][a-zA-Z0-9_]*)*$
    kind: SettingKind
    default: Any        # must be a valid value for `kind`
    title: str | None = None
    description: str | None = None
    category: str | None = None
    group: str | None = None
    slider: SliderSpec | None = None    # required for SLIDER, forbidden for all other kinds
    select: SelectSpec | None = None    # required for SELECT, forbidden for all other kinds
    pattern: str | None = None          # TEXT only: regex the value must match
    min_length: int | None = None       # TEXT only
    max_length: int | None = None       # TEXT only
    min_value: float | None = None      # NUMBER only
    max_value: float | None = None      # NUMBER only


class SettingView(BaseModel):  # frozen
    """Renderable representation of a setting: metadata + current value + status (REQ-012)."""

    key: str
    kind: SettingKind
    title: str | None
    description: str | None
    category: str | None
    group: str | None
    default: Any
    value: Any                # current value
    status: SettingStatus     # derived: MODIFIED iff value != default
    slider: SliderSpec | None
    select: SelectSpec | None
    pattern: str | None
    min_length: int | None
    max_length: int | None
    min_value: float | None
    max_value: float | None


class Template(BaseModel):  # frozen
    """A named value profile scoped to a category (and optionally a group)."""

    name: str                 # matches ^[a-zA-Z_][a-zA-Z0-9_]*$
    category: str
    group: str | None = None
    values: dict[str, Any]    # setting key -> value; exactly covers the scope


class SettingChanged(BaseModel):  # frozen
    """Published to the event bus whenever a setting value changes (REQ-024)."""

    key: str
    value: Any                # the new value
    previous: Any             # the value before the change
```

Validation rules per kind (REQ-003):

| Kind | Valid value |
|------|-------------|
| TEXT | `str`; if `pattern` is set, the value must match it; `min_length`/`max_length` bound the length |
| NUMBER | `int` or `float` (bool excluded); if set, `min_value <= value <= max_value` |
| BOOLEAN | `bool` |
| EMAIL | `str` that is a valid email address (per `email-validator`) |
| SLIDER | `int` or `float` (bool excluded); `min <= value <= max`; `value == min + k * step` for some integer `k >= 0` (step grid; `SliderSpec` guarantees `max` lies on the grid, so `min` and `max` are always valid) |
| SELECT | one of the `SelectSpec` option values |

```python
# Public API of the settings feature (module: backend.settings).
class SettingsRegistry:
    def __init__(self, event_bus: EventBus | None = None,
                 template_repository: TemplateRepository | None = None) -> None: ...
    # Settings
    def register(self, definition: SettingDefinition) -> None: ...
    def register_feature(self, feature: str, definitions: list[SettingDefinition]) -> None: ...
    def has(self, key: str) -> bool: ...
    def get_definition(self, key: str) -> SettingDefinition: ...
    def get_value(self, key: str) -> Any: ...
    def set_value(self, key: str, value: Any) -> Any: ...
    def reset(self, key: str) -> None: ...
    def reset_all(self) -> None: ...
    def get_status(self, key: str) -> SettingStatus: ...
    # Hierarchy / views
    def views(self) -> list[SettingView]: ...
    def to_view(self, key: str) -> SettingView: ...
    def grouped_views(self) -> dict[str, dict[str, list[SettingView]]]: ...
    # Templates
    def create_template(self, name: str, category: str, group: str | None,
                        values: dict[str, Any] | None = None) -> Template: ...
    def load_template(self, name: str) -> None: ...
    def update_template(self, name: str, values: dict[str, Any]) -> None: ...
    def delete_template(self, name: str) -> None: ...
    def get_template(self, name: str) -> Template: ...
    def has_template(self, name: str) -> bool: ...
    def list_templates(self) -> list[Template]: ...


def get_settings_registry() -> SettingsRegistry: ...   # shared default (singleton)
def reset_settings_registry() -> None: ...            # reset the default (tests)


# Template storage (repository pattern).
class TemplateRepository(ABC):
    def save(self, template: Template) -> None: ...
    def get(self, name: str) -> Template | None: ...
    def delete(self, name: str) -> None: ...          # idempotent
    def list(self) -> list[Template]: ...             # name order


class YamlTemplateRepository(TemplateRepository):
    def __init__(self, directory: str | Path) -> None: ...  # ensures the directory exists
```

```python
# Exception hierarchy (module: backend.settings.exceptions).
class SettingsError(Exception): ...
class SettingsNotFoundError(SettingsError): ...
class SettingsValidationError(SettingsError): ...
class SettingsRegistrationError(SettingsError): ...
class TemplateNotFoundError(SettingsError): ...
class TemplateValidationError(SettingsError): ...
class TemplateStorageError(SettingsError): ...
```

Semantics notes:
- `register()` / `register_feature()`: duplicate keys are rejected (`SettingsRegistrationError`); `register_feature(feature, definitions)` rejects any definition whose key does not start with `f"{feature}."`.
- `get_value(key)`: returns the current value, or the setting's default if never set.
- `set_value(key, value)`: validates per kind; on success stores and returns the value; on failure raises `SettingsValidationError`.
- `reset(key)` / `reset_all()`: restore the default(s).
- `get_status(key)`: `MODIFIED` iff the current value differs from the default, else `DEFAULT`.
- `views()`: all settings in registration order. `to_view(key)`: one renderable view.
- `grouped_views()`: `category -> group -> views`; settings without a category are excluded; settings without a group are under the inner key `""`.
- `create_template(name, category, group, values=None)`: if `values` is None, the template's values are the current values of all settings in the scope; otherwise `values` must exactly cover the scope (every in-scope setting is present, no out-of-scope keys) and every value must be valid. Duplicate names are rejected. Violations raise `TemplateValidationError`.
- `load_template(name)`: sets each `(key, value)` in the template's values (in key-sorted order); settings in the current scope that are not in the template are left as-is. Unknown names raise `TemplateNotFoundError`.
- `update_template(name, values)`: replaces the stored values; `values` must exactly cover the scope (same rule as create). Unknown names raise `TemplateNotFoundError`.
- `delete_template(name)`: removes the template. Unknown names raise `TemplateNotFoundError`.
- `list_templates()`: stored templates in name order.
- Template scope: the settings `s` with `s.category == template.category` and (`template.group is None` or `s.group == template.group`). Settings without a category are in no template's scope.

## 4. Requirements

| ID | Requirement |
|----|-------------|
| REQ-001 | The settings feature provides a `SettingDefinition` model capturing a setting's full metadata: unique dot-separated key, kind, default value, optional display metadata (title, description), optional grouping (category, group), kind-specific parameters (slider min/max/step, select options), and validation constraints (pattern, min/max length, min/max value). |
| REQ-002 | The settings feature supports six setting kinds: TEXT, NUMBER, BOOLEAN, EMAIL, SLIDER, SELECT. |
| REQ-003 | The settings feature validates values per kind: TEXT is a string with optional pattern/length constraints; NUMBER is a number (bool excluded) with optional min/max bounds; BOOLEAN is a boolean; EMAIL is a string with a valid email address; SLIDER is a number within [min, max] on the step grid; SELECT is one of the predefined option values. |
| REQ-004 | A `SettingDefinition` is rejected with `SettingsValidationError` when its key does not match the key format, its default is invalid for its kind, its kind-specific parameters are missing or mismatched (SLIDER requires a valid `SliderSpec`, SELECT requires a valid `SelectSpec`, all other kinds forbid slider/select specs, TEXT-only and NUMBER-only constraints are rejected on other kinds), or its `SliderSpec`/`SelectSpec` is invalid (min > max, step <= 0, max off the step grid, empty options, duplicate option values). |
| REQ-005 | The settings feature provides registry registration: `register(definition)` adds a definition; duplicate keys are rejected with `SettingsRegistrationError`; registration is thread-safe. |
| REQ-006 | The settings feature provides feature-scoped registration: `register_feature(feature, definitions)` registers a feature's settings and rejects any definition whose key does not start with `f"{feature}."` (`SettingsRegistrationError`). |
| REQ-007 | The settings feature provides value access with defaults: `get_value(key)` returns the current value, or the setting's default if never set. |
| REQ-008 | The settings feature provides validated value updates: `set_value(key, value)` validates the value per kind, stores and returns it on success, and raises `SettingsValidationError` on failure. |
| REQ-009 | The settings feature provides resets: `reset(key)` restores the setting's default; `reset_all()` restores all settings to their defaults. |
| REQ-010 | Unknown keys raise `SettingsNotFoundError` on every lookup: `get_definition`, `get_value`, `set_value`, `reset`, `get_status`, `to_view`. |
| REQ-011 | The settings feature exposes the settings hierarchy: settings are organized by category then group; `grouped_views()` returns the category -> group -> views structure. |
| REQ-012 | The settings feature provides renderable metadata for a future frontend: `to_view(key)` and `views()` produce `SettingView` objects combining the setting's metadata, its current value, and its status. |
| REQ-013 | Each setting exposes a default status derived from its value: `get_status(key)` returns `MODIFIED` when the current value differs from the default, otherwise `DEFAULT`; the status is included in `SettingView`. |
| REQ-014 | The settings feature provides a shared default registry: `get_settings_registry()` returns a singleton for features, `SettingsRegistry` is instantiable for tests/DI, and `reset_settings_registry()` resets the default for tests. |
| REQ-015 | Templates are named value profiles scoped to a single category (and optionally one group); a template's values form a complete map of its scope at creation and update time (the scope may grow afterwards; loads leave settings not in the template as-is). |
| REQ-016 | The settings feature supports template creation: `create_template(name, category, group, values=None)`; when `values` is None the template captures the current values of all settings in the scope; when given, `values` must exactly cover the scope with valid values; names are unique; violations raise `TemplateValidationError`. |
| REQ-017 | The settings feature supports template loading: `load_template(name)` sets each of the template's values (validated); settings in the current scope that are not in the template are left as-is; unknown names raise `TemplateNotFoundError`. |
| REQ-018 | The settings feature supports template updates: `update_template(name, values)` replaces the stored values; `values` must exactly cover the scope; unknown names raise `TemplateNotFoundError`. |
| REQ-019 | The settings feature supports template deletion: `delete_template(name)` removes the template; unknown names raise `TemplateNotFoundError`. |
| REQ-020 | The settings feature provides template access: `get_template(name)`, `has_template(name)`, and `list_templates()` (name order). |
| REQ-021 | Template storage goes through the `TemplateRepository` abstraction (`save`, `get`, `delete`, `list`): the registry stores and retrieves templates via the repository, and alternative format implementations (JSON, etc.) satisfy the same interface. |
| REQ-022 | The first repository implementation is `YamlTemplateRepository(directory)`: one file per template named `<name>.yaml`, safe YAML, atomic writes (a template file is always either absent or valid YAML), the directory is created if it does not exist, and operations are thread-safe. |
| REQ-023 | Storage errors are handled: a corrupted or schema-invalid template file raises `TemplateStorageError` on `get`/`list`; `get` for a missing file returns None; `delete` for a missing file is a no-op. |
| REQ-024 | Value changes publish a `SettingChanged` event (key, value, previous) to the event bus: `set_value`, `reset`, `reset_all`, and the `set_value` calls triggered by template loads. |
| REQ-025 | The settings registry accepts an explicit event bus: `SettingsRegistry(event_bus=...)`; when omitted, the shared default bus from `get_event_bus()` is used. |

## 5. Acceptance Criteria

| ID | References | Criterion |
|----|------------|-----------|
| AC-001 | REQ-002, REQ-003 | **Given** a registry with a TEXT setting, **When** `set_value(key, "hello")` is called, **Then** `"hello"` is returned, **And** `get_value(key) == "hello"`. |
| AC-002 | REQ-002, REQ-003 | **Given** a registry with a NUMBER setting, **When** `set_value(key, 42)` is called, **Then** `42` is returned, **And** `get_value(key) == 42`. |
| AC-003 | REQ-002, REQ-003 | **Given** a registry with a BOOLEAN setting, **When** `set_value(key, True)` is called, **Then** `True` is returned, **And** `get_value(key) is True`. |
| AC-004 | REQ-002, REQ-003 | **Given** a registry with an EMAIL setting, **When** `set_value(key, "user@example.com")` is called, **Then** the value is returned, **And** `get_value(key) == "user@example.com"`. |
| AC-005 | REQ-002, REQ-003 | **Given** a registry with a SLIDER setting (min=0, max=10, step=2), **When** `set_value(key, 4)` is called, **Then** `4` is returned, **And** `get_value(key) == 4`. |
| AC-006 | REQ-002, REQ-003 | **Given** a registry with a SELECT setting (options "a", "b"), **When** `set_value(key, "b")` is called, **Then** `"b"` is returned, **And** `get_value(key) == "b"`. |
| AC-007 | REQ-007 | **Given** a registered setting with a default, **When** `get_value(key)` is called before any `set_value`, **Then** the default is returned. |
| AC-008 | REQ-008 | **Given** a registered setting, **When** `set_value(key, value)` is called with a valid value, **Then** the value is stored, **And** `get_value(key)` returns it. |
| AC-009 | REQ-004 | **Given** a `SettingDefinition(kind=NUMBER, default="abc")`, **When** the definition is constructed, **Then** `SettingsValidationError` is raised. |
| AC-010 | REQ-004 | **Given** a `SettingDefinition` with missing or mismatched kind-specific parameters (SLIDER without a slider spec, SELECT without a select spec, a slider spec on a TEXT setting), **When** the definition is constructed, **Then** `SettingsValidationError` is raised. |
| AC-011 | REQ-005 | **Given** a registry, **When** `register(definition)` is called twice for the same key, **Then** the second call raises `SettingsRegistrationError`. |
| AC-012 | REQ-006 | **Given** a feature "logging" and a definition with key "logging.log_level", **When** `register_feature("logging", [definition])` is called, **Then** the setting is registered under that key. |
| AC-013 | REQ-009 | **Given** a setting set to a non-default value, **When** `reset(key)` is called, **Then** `get_value(key)` returns the default. |
| AC-014 | REQ-010 | **Given** an unknown key, **When** `get_value(unknown)` is called, **Then** `SettingsNotFoundError` is raised. |
| AC-015 | REQ-011 | **Given** settings in category "logging" (groups "file" and "console"), **When** `grouped_views()` is called, **Then** the views are organized by category then group. |
| AC-016 | REQ-012 | **Given** a registered setting, **When** `to_view(key)` is called, **Then** a `SettingView` is returned with the setting's metadata, its current value, and its status. |
| AC-017 | REQ-013 | **Given** a registered setting, **When** it has not been set, **Then** `get_status(key)` is DEFAULT; **And** after `set_value(key, non_default)`, **Then** `get_status(key)` is MODIFIED; **And** after `reset(key)`, **Then** `get_status(key)` is DEFAULT; **And** after `set_value(key, the_default)`, **Then** `get_status(key)` is DEFAULT. |
| AC-018 | REQ-014 | **Given** the settings feature module, **When** `get_settings_registry()` is called twice, **Then** the same instance is returned. |
| AC-019 | REQ-016 | **Given** a category "app" with registered settings, **When** `create_template("t1", "app", None, values)` is called with `values` exactly covering the scope, **Then** the template is stored with those values. |
| AC-020 | REQ-016 | **Given** a category "app" with registered settings, **When** `create_template("t1", "app", None, None)` is called, **Then** the template's values are the current values of all settings in the scope. |
| AC-021 | REQ-016 | **Given** a category "app" with settings A and B, **When** `create_template` is called with values missing B or containing an out-of-scope key, **Then** `TemplateValidationError` is raised. |
| AC-022 | REQ-016 | **Given** an existing template "t1", **When** `create_template("t1", ...)` is called again, **Then** `TemplateValidationError` is raised. |
| AC-023 | REQ-017 | **Given** a template "t1" for category "app", **When** `load_template("t1")` is called, **Then** each setting in the template's values is set to the template's value. |
| AC-024 | REQ-017 | **Given** a template created before setting B was registered in the scope, **When** `load_template` is called, **Then** B keeps its current value (left as-is), **And** the template's settings are set to the template's values. |
| AC-025 | REQ-017 | **Given** an unknown template name, **When** `load_template(name)` is called, **Then** `TemplateNotFoundError` is raised. |
| AC-026 | REQ-018 | **Given** an existing template, **When** `update_template(name, values)` is called with values exactly covering the scope, **Then** the template's stored values are replaced. |
| AC-027 | REQ-018 | **Given** an existing template, **When** `update_template` is called with values not exactly covering the scope, **Then** `TemplateValidationError` is raised; **And** **Given** an unknown template name, **When** `update_template` is called, **Then** `TemplateNotFoundError` is raised. |
| AC-028 | REQ-019 | **Given** an existing template, **When** `delete_template(name)` is called, **Then** the template is removed; **And** **Given** an unknown name, **When** `delete_template(name)` is called, **Then** `TemplateNotFoundError` is raised. |
| AC-029 | REQ-020 | **Given** created templates, **When** `get_template(name)`, `has_template(name)`, and `list_templates()` are called, **Then** they return/contain the templates, **And** `list_templates()` returns them in name order. |
| AC-030 | REQ-022 | **Given** a `YamlTemplateRepository` with a directory, **When** a template is created via the registry, **Then** a file `<name>.yaml` exists in the directory, **And** it is valid YAML containing the template's fields (name, category, group, values). |
| AC-031 | REQ-021, REQ-022 | **Given** a template created via one registry instance, **When** another registry instance sharing the same directory/repository calls `get_template(name)`, **Then** the template is returned (persistence across instances). |
| AC-032 | REQ-023 | **Given** a corrupted template file (invalid YAML or schema-invalid content), **When** `get(name)` or `list()` is called, **Then** `TemplateStorageError` is raised. |
| AC-033 | REQ-023 | **Given** a missing template file, **When** `get(name)` is called, **Then** None is returned; **And** **Given** a missing template file, **When** `delete(name)` is called, **Then** no error is raised (idempotent). |
| AC-034 | REQ-021 | **Given** a registry configured with an alternative `TemplateRepository` implementation (in-memory), **When** templates are created, loaded, updated, and deleted, **Then** the behavior is identical to the YAML implementation (storage-agnostic). |
| AC-035 | REQ-024 | **Given** a handler subscribed to `SettingChanged` on the bus, **When** `set_value(key, value)` is called, **Then** the handler receives a `SettingChanged` with the key, the new value, and the previous value. |
| AC-036 | REQ-024 | **Given** a handler subscribed to `SettingChanged`, **When** `load_template(name)` is called, **Then** the handler receives a `SettingChanged` for each setting set by the load. |
| AC-037 | REQ-025 | **Given** `SettingsRegistry(event_bus=custom_bus)`, **When** `set_value(key, value)` is called, **Then** the event is published on `custom_bus`, not on the shared bus. |
| AC-038 | REQ-005 | **Given** a registry, **When** `register(definition)` is called concurrently from multiple threads with distinct keys, **Then** every setting is registered, **And** no thread crashes. |
| AC-039 | REQ-024 | **Given** a setting set to a non-default value, **When** `reset(key)` is called, **Then** a `SettingChanged` is published with `value == default` and `previous ==` the old value; **And** **Given** multiple settings set to non-default values, **When** `reset_all()` is called, **Then** a `SettingChanged` is published for each setting, with `value` equal to its default. |

## 6. Invariants

| ID | Invariant |
|----|-----------|
| INV-001 | For any registered setting and any value v valid for its kind: `set_value(key, v)` succeeds, **And** `get_value(key) == v`. |
| INV-002 | For any registered setting: `get_value(key)` returns a value that is valid for its kind. |
| INV-003 | For any registered setting: after `reset(key)`, `get_value(key) == default`. |
| INV-004 | For any SELECT setting: every option value is a valid value for the setting. |
| INV-005 | For any SLIDER setting: `min`, `max`, and `min + k * step` (for every integer `k >= 0` with `min + k * step <= max`) are valid values. |
| INV-006 | For any registered setting: `views()` contains a `SettingView` whose `value` equals `get_value(key)` and whose `status` equals the derived status. |
| INV-007 | After `load_template(name)`: every setting in the scope has a value that is valid for its kind. |
| INV-008 | For any value-change operation (`set_value`, `reset`, `reset_all`, template load): exactly one `SettingChanged` is published per setting the operation sets — including when the new value equals the previous value. |
| INV-009 | For any valid `Template`: `repository.save(t)` followed by `repository.get(t.name)` returns a template equal to t (YAML round-trip). |
| INV-010 | For any registered setting: `get_status(key) == MODIFIED` if and only if `get_value(key) != default`. |

## 7. Edge Cases & Error Conditions

| ID | Condition | Expected Behavior |
|----|-----------|-------------------|
| EDGE-001 | `get_definition` / `get_value` / `set_value` / `reset` / `get_status` / `to_view` with an unknown key | Raises `SettingsNotFoundError`. |
| EDGE-002 | `register()` with a key that is already registered | Raises `SettingsRegistrationError`. |
| EDGE-003 | `set_value` with a wrong-typed value (e.g., `str` for a NUMBER setting) | Raises `SettingsValidationError`. |
| EDGE-004 | `set_value` with a `bool` for a numeric kind (NUMBER or SLIDER) | Raises `SettingsValidationError` (bool is not a number here). |
| EDGE-005 | `set_value` with a NUMBER outside `min_value`/`max_value` | Raises `SettingsValidationError`. |
| EDGE-006 | `set_value` with an invalid email address | Raises `SettingsValidationError`. |
| EDGE-007 | `set_value` with a SLIDER value off the step grid | Raises `SettingsValidationError`. |
| EDGE-008 | `set_value` with a SLIDER value outside [min, max] | Raises `SettingsValidationError`. |
| EDGE-009 | `set_value` with a SELECT value that is not an option | Raises `SettingsValidationError`. |
| EDGE-010 | `set_value` with a TEXT value violating `pattern` | Raises `SettingsValidationError`. |
| EDGE-011 | `set_value` with a TEXT value violating `min_length`/`max_length` | Raises `SettingsValidationError`. |
| EDGE-012 | `reset()` with an unknown key | Raises `SettingsNotFoundError`. |
| EDGE-013 | `reset_all()` | Every setting returns to its default. |
| EDGE-014 | `SliderSpec` with `min > max` | Raises `SettingsValidationError` at construction. |
| EDGE-015 | `SliderSpec` with `step <= 0` | Raises `SettingsValidationError` at construction. |
| EDGE-016 | `SelectSpec` with no options | Raises `SettingsValidationError` at construction. |
| EDGE-017 | `SelectSpec` with duplicate option values | Raises `SettingsValidationError` at construction. |
| EDGE-018 | `SettingDefinition` with mismatched kind-specific parameters (slider spec on a TEXT setting, `pattern` on a NUMBER setting) | Raises `SettingsValidationError` at construction. |
| EDGE-019 | `SettingDefinition` with a key that violates the key format (e.g., `"a..b"`, `"1abc"`, `"a.b.."`) | Raises `SettingsValidationError` at construction. |
| EDGE-020 | `register_feature(feature, definitions)` with a key that does not start with `f"{feature}."` | Raises `SettingsRegistrationError`. |
| EDGE-021 | `set_value(key, value)` where `value` equals the current value | The value is stored, **And** a `SettingChanged` is published with `previous == value`. |
| EDGE-022 | `set_value` when the event bus is shut down | `set_value` still succeeds (the event is dropped, no error). |
| EDGE-023 | `list_templates()` with no stored templates | Returns an empty list. |
| EDGE-024 | `YamlTemplateRepository` with a directory that does not exist | The directory is created. |
| EDGE-025 | A template file with valid YAML but schema-invalid content (e.g., `values` is a list) | Raises `TemplateStorageError` on `get`/`list`. |
| EDGE-026 | `create_template` for a scope with no registered settings | Succeeds with an empty `values` map. |
| EDGE-027 | `load_template` when the template's settings are not registered in this registry | Raises `SettingsNotFoundError` for the first missing key. |
| EDGE-028 | `create_template` with a name that violates the name format (e.g., `"bad name"`, `"1name"`) | Raises `TemplateValidationError`. |
| EDGE-029 | `SliderSpec` with `max` off the step grid (e.g., `min=0, max=11, step=2`) | Raises `SettingsValidationError` at construction. |

## 8. Non-Functional Requirements

| ID | Category | Requirement |
|----|----------|-------------|
| NFR-001 | Performance | Read-only single-setting operations (`get_value`, `to_view`, `get_status`) complete in < 1 ms (median) with 1000 registered settings; mutating single-setting operations (`register`, `set_value`, `reset`), which persist all current values to the value repository (AC-013), complete in < 50 ms (median) with 1000 registered settings; `load_template` completes in < 10 ms for a scope of 100 settings; `create_template`/`update_template`/`delete_template` (with YAML file I/O) complete in < 50 ms; `list_templates` completes in < 500 ms with 100 stored templates. |
| NFR-002 | Contract | The public API (models, registry, repository, exceptions, module functions) is backward-compatible; `TemplateRepository` is the stable storage interface — alternative format implementations (JSON, etc.) must satisfy the same interface and observable behavior. |
| NFR-003 | Resource | Setting definitions and values are in-memory; templates persist as YAML files; the feature creates no threads or sockets of its own. |
| NFR-004 | Observability | Registration, value changes, template operations, and storage failures are logged at appropriate levels with key/name context. |

## 9. Observability & Logging

The feature uses loguru's `logger` (configured by the shared logging feature) for one-off statements.

| Operation / Event | Level | Context |
|-------------------|-------|---------|
| Setting registered | DEBUG | key, kind |
| Feature settings registered | DEBUG | feature, count |
| Value set | DEBUG | key |
| Value reset | DEBUG | key |
| Validation failure | WARNING | key, reason |
| Duplicate registration | WARNING | key |
| Template created | DEBUG | name, category, group |
| Template loaded | DEBUG | name, count of settings set |
| Template updated | DEBUG | name |
| Template deleted | DEBUG | name |
| Template validation failure | WARNING | name, reason |
| Template saved to storage | DEBUG | name |
| Template loaded from storage | DEBUG | name |
| Template storage failure | ERROR | name, reason |

- **Default level:** DEBUG for operations; WARNING for validation failures; ERROR for storage integrity failures.
- **Error conditions:** validation failures are logged at WARNING before raising; duplicate registrations are logged at WARNING before raising; storage failures are logged at ERROR before raising; unknown-key and unknown-template lookups raise without logging (caller errors).

## 10. Test Strategy

| ID | Test Category | Test File | Test Function |
|----|---------------|-----------|---------------|
| AC-001 | acceptance | `tests/acceptance/settings/test_settings.py` | `test_ac_001_text_roundtrip` |
| AC-002 | acceptance | `tests/acceptance/settings/test_settings.py` | `test_ac_002_number_roundtrip` |
| AC-003 | acceptance | `tests/acceptance/settings/test_settings.py` | `test_ac_003_boolean_roundtrip` |
| AC-004 | acceptance | `tests/acceptance/settings/test_settings.py` | `test_ac_004_email_roundtrip` |
| AC-005 | acceptance | `tests/acceptance/settings/test_settings.py` | `test_ac_005_slider_roundtrip` |
| AC-006 | acceptance | `tests/acceptance/settings/test_settings.py` | `test_ac_006_select_roundtrip` |
| AC-007 | acceptance | `tests/acceptance/settings/test_settings.py` | `test_ac_007_default_before_set` |
| AC-008 | acceptance | `tests/acceptance/settings/test_settings.py` | `test_ac_008_set_stores_value` |
| AC-009 | acceptance | `tests/acceptance/settings/test_settings.py` | `test_ac_009_invalid_default` |
| AC-010 | acceptance | `tests/acceptance/settings/test_settings.py` | `test_ac_010_missing_kind_params` |
| AC-011 | acceptance | `tests/acceptance/settings/test_settings.py` | `test_ac_011_duplicate_registration` |
| AC-012 | acceptance | `tests/acceptance/settings/test_settings.py` | `test_ac_012_register_feature` |
| AC-013 | acceptance | `tests/acceptance/settings/test_settings.py` | `test_ac_013_reset_to_default` |
| AC-014 | acceptance | `tests/acceptance/settings/test_settings.py` | `test_ac_014_unknown_key` |
| AC-015 | acceptance | `tests/acceptance/settings/test_settings.py` | `test_ac_015_grouped_views` |
| AC-016 | acceptance | `tests/acceptance/settings/test_settings.py` | `test_ac_016_to_view` |
| AC-017 | acceptance | `tests/acceptance/settings/test_settings.py` | `test_ac_017_status_transitions` |
| AC-018 | acceptance | `tests/acceptance/settings/test_settings.py` | `test_ac_018_singleton` |
| AC-019 | acceptance | `tests/acceptance/settings/test_settings.py` | `test_ac_019_create_template_explicit` |
| AC-020 | acceptance | `tests/acceptance/settings/test_settings.py` | `test_ac_020_create_template_capture` |
| AC-021 | acceptance | `tests/acceptance/settings/test_settings.py` | `test_ac_021_create_template_incomplete` |
| AC-022 | acceptance | `tests/acceptance/settings/test_settings.py` | `test_ac_022_create_template_duplicate` |
| AC-023 | acceptance | `tests/acceptance/settings/test_settings.py` | `test_ac_023_load_template_sets_values` |
| AC-024 | acceptance | `tests/acceptance/settings/test_settings.py` | `test_ac_024_load_template_leave_as_is` |
| AC-025 | acceptance | `tests/acceptance/settings/test_settings.py` | `test_ac_025_load_template_unknown` |
| AC-026 | acceptance | `tests/acceptance/settings/test_settings.py` | `test_ac_026_update_template` |
| AC-027 | acceptance | `tests/acceptance/settings/test_settings.py` | `test_ac_027_update_template_invalid` |
| AC-028 | acceptance | `tests/acceptance/settings/test_settings.py` | `test_ac_028_delete_template` |
| AC-029 | acceptance | `tests/acceptance/settings/test_settings.py` | `test_ac_029_template_access` |
| AC-030 | acceptance | `tests/acceptance/settings/test_settings.py` | `test_ac_030_yaml_file_written` |
| AC-031 | acceptance | `tests/acceptance/settings/test_settings.py` | `test_ac_031_persistence_across_instances` |
| AC-032 | acceptance | `tests/acceptance/settings/test_settings.py` | `test_ac_032_corrupted_file` |
| AC-033 | acceptance | `tests/acceptance/settings/test_settings.py` | `test_ac_033_missing_file` |
| AC-034 | acceptance | `tests/acceptance/settings/test_settings.py` | `test_ac_034_storage_agnostic` |
| AC-035 | acceptance | `tests/acceptance/settings/test_settings.py` | `test_ac_035_set_value_publishes_event` |
| AC-036 | acceptance | `tests/acceptance/settings/test_settings.py` | `test_ac_036_load_template_publishes_events` |
| AC-037 | acceptance | `tests/acceptance/settings/test_settings.py` | `test_ac_037_custom_bus` |
| AC-038 | acceptance | `tests/acceptance/settings/test_settings.py` | `test_ac_038_thread_safe_registration` |
| AC-039 | acceptance | `tests/acceptance/settings/test_settings.py` | `test_ac_039_reset_publishes_events` |
| INV-001 | property | `tests/property/settings/test_settings_properties.py` | `test_inv_001_set_get_roundtrip` |
| INV-002 | property | `tests/property/settings/test_settings_properties.py` | `test_inv_002_get_value_always_valid` |
| INV-003 | property | `tests/property/settings/test_settings_properties.py` | `test_inv_003_reset_to_default` |
| INV-004 | property | `tests/property/settings/test_settings_properties.py` | `test_inv_004_select_options_valid` |
| INV-005 | property | `tests/property/settings/test_settings_properties.py` | `test_inv_005_slider_grid_valid` |
| INV-006 | property | `tests/property/settings/test_settings_properties.py` | `test_inv_006_views_match_values` |
| INV-007 | property | `tests/property/settings/test_settings_properties.py` | `test_inv_007_load_scope_valid` |
| INV-008 | property | `tests/property/settings/test_settings_properties.py` | `test_inv_008_exactly_one_event_per_change` |
| INV-009 | property | `tests/property/settings/test_settings_properties.py` | `test_inv_009_yaml_roundtrip` |
| INV-010 | property | `tests/property/settings/test_settings_properties.py` | `test_inv_010_status_derivation` |
| EDGE-001 | unit | `tests/unit/settings/test_settings_edges.py` | `test_edge_001_unknown_key_lookups` |
| EDGE-002 | unit | `tests/unit/settings/test_settings_edges.py` | `test_edge_002_duplicate_registration` |
| EDGE-003 | unit | `tests/unit/settings/test_settings_edges.py` | `test_edge_003_wrong_type` |
| EDGE-004 | unit | `tests/unit/settings/test_settings_edges.py` | `test_edge_004_bool_for_numeric` |
| EDGE-005 | unit | `tests/unit/settings/test_settings_edges.py` | `test_edge_005_number_out_of_bounds` |
| EDGE-006 | unit | `tests/unit/settings/test_settings_edges.py` | `test_edge_006_invalid_email` |
| EDGE-007 | unit | `tests/unit/settings/test_settings_edges.py` | `test_edge_007_slider_off_grid` |
| EDGE-008 | unit | `tests/unit/settings/test_settings_edges.py` | `test_edge_008_slider_out_of_range` |
| EDGE-009 | unit | `tests/unit/settings/test_settings_edges.py` | `test_edge_009_select_not_an_option` |
| EDGE-010 | unit | `tests/unit/settings/test_settings_edges.py` | `test_edge_010_text_pattern` |
| EDGE-011 | unit | `tests/unit/settings/test_settings_edges.py` | `test_edge_011_text_length` |
| EDGE-012 | unit | `tests/unit/settings/test_settings_edges.py` | `test_edge_012_reset_unknown` |
| EDGE-013 | unit | `tests/unit/settings/test_settings_edges.py` | `test_edge_013_reset_all` |
| EDGE-014 | unit | `tests/unit/settings/test_settings_edges.py` | `test_edge_014_slider_min_gt_max` |
| EDGE-015 | unit | `tests/unit/settings/test_settings_edges.py` | `test_edge_015_slider_step_nonpositive` |
| EDGE-016 | unit | `tests/unit/settings/test_settings_edges.py` | `test_edge_016_select_empty` |
| EDGE-017 | unit | `tests/unit/settings/test_settings_edges.py` | `test_edge_017_select_duplicate_options` |
| EDGE-018 | unit | `tests/unit/settings/test_settings_edges.py` | `test_edge_018_kind_param_mismatch` |
| EDGE-019 | unit | `tests/unit/settings/test_settings_edges.py` | `test_edge_019_invalid_key_format` |
| EDGE-020 | unit | `tests/unit/settings/test_settings_edges.py` | `test_edge_020_feature_prefix` |
| EDGE-021 | unit | `tests/unit/settings/test_settings_edges.py` | `test_edge_021_unchanged_value_event` |
| EDGE-022 | unit | `tests/unit/settings/test_settings_edges.py` | `test_edge_022_bus_shutdown` |
| EDGE-023 | unit | `tests/unit/settings/test_settings_edges.py` | `test_edge_023_list_templates_empty` |
| EDGE-024 | unit | `tests/unit/settings/test_settings_edges.py` | `test_edge_024_directory_created` |
| EDGE-025 | unit | `tests/unit/settings/test_settings_edges.py` | `test_edge_025_schema_invalid_file` |
| EDGE-026 | unit | `tests/unit/settings/test_settings_edges.py` | `test_edge_026_empty_scope_template` |
| EDGE-027 | unit | `tests/unit/settings/test_settings_edges.py` | `test_edge_027_load_unregistered_settings` |
| EDGE-028 | unit | `tests/unit/settings/test_settings_edges.py` | `test_edge_028_invalid_template_name` |
| EDGE-029 | unit | `tests/unit/settings/test_settings_edges.py` | `test_edge_029_slider_max_off_grid` |
| NFR-001 | contract | `tests/contract/settings/test_settings_contracts.py` | `test_nfr_001_performance_budgets` |
| NFR-002 | contract | `tests/contract/settings/test_settings_contracts.py` | `test_nfr_002_api_and_repository_contract` |
| NFR-003 | contract | `tests/contract/settings/test_settings_contracts.py` | `test_nfr_003_resource_contract` |
| NFR-004 | contract | `tests/contract/settings/test_settings_contracts.py` | `test_nfr_004_observability` |
| — | integration | `tests/integration/settings/test_settings_integration.py` | `test_multi_feature_reactive_settings` |
| — | integration | `tests/integration/settings/test_settings_integration.py` | `test_template_capture_restore_workflow` |

## 11. Traceability Matrix

Maintain this matrix as tests are written and pass. Every normative requirement MUST have at least one executable test.

| Requirement | Acceptance Criterion | Test | Status |
|-------------|---------------------|------|--------|
| REQ-002, REQ-003 | AC-001 | `test_ac_001_text_roundtrip` | PENDING |
| REQ-002, REQ-003 | AC-002 | `test_ac_002_number_roundtrip` | PENDING |
| REQ-002, REQ-003 | AC-003 | `test_ac_003_boolean_roundtrip` | PENDING |
| REQ-002, REQ-003 | AC-004 | `test_ac_004_email_roundtrip` | PENDING |
| REQ-002, REQ-003 | AC-005 | `test_ac_005_slider_roundtrip` | PENDING |
| REQ-002, REQ-003 | AC-006 | `test_ac_006_select_roundtrip` | PENDING |
| REQ-007 | AC-007 | `test_ac_007_default_before_set` | PENDING |
| REQ-008 | AC-008 | `test_ac_008_set_stores_value` | PENDING |
| REQ-004 | AC-009 | `test_ac_009_invalid_default` | PENDING |
| REQ-004 | AC-010 | `test_ac_010_missing_kind_params` | PENDING |
| REQ-005 | AC-011 | `test_ac_011_duplicate_registration` | PENDING |
| REQ-006 | AC-012 | `test_ac_012_register_feature` | PENDING |
| REQ-009 | AC-013 | `test_ac_013_reset_to_default` | PENDING |
| REQ-010 | AC-014 | `test_ac_014_unknown_key` | PENDING |
| REQ-011 | AC-015 | `test_ac_015_grouped_views` | PENDING |
| REQ-012 | AC-016 | `test_ac_016_to_view` | PENDING |
| REQ-013 | AC-017 | `test_ac_017_status_transitions` | PENDING |
| REQ-014 | AC-018 | `test_ac_018_singleton` | PENDING |
| REQ-016 | AC-019 | `test_ac_019_create_template_explicit` | PENDING |
| REQ-016 | AC-020 | `test_ac_020_create_template_capture` | PENDING |
| REQ-016 | AC-021 | `test_ac_021_create_template_incomplete` | PENDING |
| REQ-016 | AC-022 | `test_ac_022_create_template_duplicate` | PENDING |
| REQ-017 | AC-023 | `test_ac_023_load_template_sets_values` | PENDING |
| REQ-017 | AC-024 | `test_ac_024_load_template_leave_as_is` | PENDING |
| REQ-017 | AC-025 | `test_ac_025_load_template_unknown` | PENDING |
| REQ-018 | AC-026 | `test_ac_026_update_template` | PENDING |
| REQ-018 | AC-027 | `test_ac_027_update_template_invalid` | PENDING |
| REQ-019 | AC-028 | `test_ac_028_delete_template` | PENDING |
| REQ-020 | AC-029 | `test_ac_029_template_access` | PENDING |
| REQ-022 | AC-030 | `test_ac_030_yaml_file_written` | PENDING |
| REQ-021, REQ-022 | AC-031 | `test_ac_031_persistence_across_instances` | PENDING |
| REQ-023 | AC-032 | `test_ac_032_corrupted_file` | PENDING |
| REQ-023 | AC-033 | `test_ac_033_missing_file` | PENDING |
| REQ-021 | AC-034 | `test_ac_034_storage_agnostic` | PENDING |
| REQ-024 | AC-035 | `test_ac_035_set_value_publishes_event` | PENDING |
| REQ-024 | AC-036 | `test_ac_036_load_template_publishes_events` | PENDING |
| REQ-025 | AC-037 | `test_ac_037_custom_bus` | PENDING |
| REQ-005 | AC-038 | `test_ac_038_thread_safe_registration` | PENDING |
| REQ-024 | AC-039 | `test_ac_039_reset_publishes_events` | PENDING |
| REQ-001 | AC-016 | `test_ac_016_to_view` | PENDING |
| REQ-015 | AC-019 | `test_ac_019_create_template_explicit` | PENDING |
| INV-001 | — | `test_inv_001_set_get_roundtrip` | PENDING |
| INV-002 | — | `test_inv_002_get_value_always_valid` | PENDING |
| INV-003 | — | `test_inv_003_reset_to_default` | PENDING |
| INV-004 | — | `test_inv_004_select_options_valid` | PENDING |
| INV-005 | — | `test_inv_005_slider_grid_valid` | PENDING |
| INV-006 | — | `test_inv_006_views_match_values` | PENDING |
| INV-007 | — | `test_inv_007_load_scope_valid` | PENDING |
| INV-008 | — | `test_inv_008_exactly_one_event_per_change` | PENDING |
| INV-009 | — | `test_inv_009_yaml_roundtrip` | PENDING |
| INV-010 | — | `test_inv_010_status_derivation` | PENDING |
| EDGE-001 | — | `test_edge_001_unknown_key_lookups` | PENDING |
| EDGE-002 | — | `test_edge_002_duplicate_registration` | PENDING |
| EDGE-003 | — | `test_edge_003_wrong_type` | PENDING |
| EDGE-004 | — | `test_edge_004_bool_for_numeric` | PENDING |
| EDGE-005 | — | `test_edge_005_number_out_of_bounds` | PENDING |
| EDGE-006 | — | `test_edge_006_invalid_email` | PENDING |
| EDGE-007 | — | `test_edge_007_slider_off_grid` | PENDING |
| EDGE-008 | — | `test_edge_008_slider_out_of_range` | PENDING |
| EDGE-009 | — | `test_edge_009_select_not_an_option` | PENDING |
| EDGE-010 | — | `test_edge_010_text_pattern` | PENDING |
| EDGE-011 | — | `test_edge_011_text_length` | PENDING |
| EDGE-012 | — | `test_edge_012_reset_unknown` | PENDING |
| EDGE-013 | — | `test_edge_013_reset_all` | PENDING |
| EDGE-014 | — | `test_edge_014_slider_min_gt_max` | PENDING |
| EDGE-015 | — | `test_edge_015_slider_step_nonpositive` | PENDING |
| EDGE-016 | — | `test_edge_016_select_empty` | PENDING |
| EDGE-017 | — | `test_edge_017_select_duplicate_options` | PENDING |
| EDGE-018 | — | `test_edge_018_kind_param_mismatch` | PENDING |
| EDGE-019 | — | `test_edge_019_invalid_key_format` | PENDING |
| EDGE-020 | — | `test_edge_020_feature_prefix` | PENDING |
| EDGE-021 | — | `test_edge_021_unchanged_value_event` | PENDING |
| EDGE-022 | — | `test_edge_022_bus_shutdown` | PENDING |
| EDGE-023 | — | `test_edge_023_list_templates_empty` | PENDING |
| EDGE-024 | — | `test_edge_024_directory_created` | PENDING |
| EDGE-025 | — | `test_edge_025_schema_invalid_file` | PENDING |
| EDGE-026 | — | `test_edge_026_empty_scope_template` | PENDING |
| EDGE-027 | — | `test_edge_027_load_unregistered_settings` | PENDING |
| EDGE-028 | — | `test_edge_028_invalid_template_name` | PENDING |
| EDGE-029 | — | `test_edge_029_slider_max_off_grid` | PENDING |
| NFR-001 | — | `test_nfr_001_performance_budgets` | PENDING |
| NFR-002 | — | `test_nfr_002_api_and_repository_contract` | PENDING |
| NFR-003 | — | `test_nfr_003_resource_contract` | PENDING |
| NFR-004 | — | `test_nfr_004_observability` | PENDING |
| — | — | `test_multi_feature_reactive_settings` (integration) | PENDING |
| — | — | `test_template_capture_restore_workflow` (integration) | PENDING |
