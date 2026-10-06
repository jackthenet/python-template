# Spec: Public install operation for the five feature singletons (settings-public-registry-setter)

## Changelog
- v1 (2026-10-06): Draft (Phase P, P.4). CROSS-CUTTING. Adds a public install operation to the five singleton-owning features and amends `docs/specs/settings.md` (v5), `docs/specs/event-bus.md` (v2), `docs/specs/user-roles-permissions.md` (v2), `docs/specs/search.md` (v4), `docs/specs/session-management.md` (v2) and `docs/specs/logging-coverage.md` (v3, inventory rows only).

## 1. Overview & Objectives

- **Feature Name:** settings-public-registry-setter
- **Change Type:** CROSS-CUTTING (reclassified from FEATURE at P.3 — Q-2 was answered "all five singletons")
- **Target Component:** the five singleton-owning modules — `src/backend/settings/registry.py`, `src/backend/eventbus/eventbus.py`, `src/backend/permissions/service.py`, `src/backend/search/service.py`, `src/backend/sessionmanagement/service.py` — plus their package `__init__.py` re-exports, the composition root `src/main.py`, the test helpers that currently reach into other packages' private slots, `pyproject.toml` (ruff `TID251`), and `AGENTS.md`.

**Problem.** There is no public operation that installs a configured instance as a feature's shared default. Every caller that wants the shared instance it built must write the owning module's private slot directly. That happens in 12 places outside the module that owns the slot: `src/main.py:138` writes `_settings_registry_singleton[0]` (imported at `src/main.py:68`), and 11 test sites write `backend.settings.registry._registry[0]` or `backend.eventbus.eventbus._default_bus[0]` (`tests/settings_test_helpers.py:132,160,180`, `tests/eventbus_test_helpers.py:77,84`, `tests/acceptance/settings_coverage/test_setup_logger.py:31,55`, `tests/acceptance/settings_coverage/test_wiring.py:18`, `tests/contract/logging/test_logging_contracts.py:35`, `tests/property/logging/test_logging_properties.py:42`, `tests/unit/logging/test_logging_edges.py:32`). Four of those five slots are a bare one-element list with no lock, so a create race can build two instances and lose one.

**Objectives.**
1. Give each of the five singleton-owning features a public install operation (`set_settings_registry`, `set_event_bus`, `set_permission_service`, `set_search_service`, `set_session_service`) that replaces the module singleton with the instance the caller built.
2. Migrate every write to another package's private singleton slot — in `src/` and in `tests/` — to the owning feature's public setter, with identical save/restore semantics and no test weakened.
3. Make the three slot operations (install, lazy create, reset) mutually exclusive in all five owning modules, so the create race is closed on the two paths that still have it.
4. Add two guards so the private-slot pattern cannot come back: a pytest scan test and a ruff `TID251` banned-api rule.

**Scope boundaries.** This spec specifies the install operation, its semantics, its tracing, its concurrency, the migration of the 12 write sites, and the two guards. It does **not** specify who may import the public API (deferred TODO `public-api-import-boundary`), a composition-root factory or dependency injection (deferred TODO `composition-root-factory`), or any change to what the five features do with the instance they hold.

**Out of scope (explicit).**
- No DI container, no factory, no protocol/ABC seam for the singletons (`composition-root-factory`).
- No import-permission rule for `backend.settings` / `backend.eventbus` (`public-api-import-boundary`).
- No runtime type check, no new exception type, no `None`-accepting install (Q-7, Q-8).
- No event published by an install; the five features' event surfaces are unchanged (Q-10).
- No lifecycle side effect on the replaced instance (no `shutdown()`, no `start()`) — the caller owns the instance it installed and the instance it replaced (D14).
- No change to the permission catalog, the settings registration surface, or any feature's observable behavior.

## 2. Architecture & Design Decisions

| ID | Decision | Rationale |
|----|----------|-----------|
| D1 | The install operation is a module-level function named `set_<slot>` beside the existing `get_<slot>()` / `reset_<slot>()` pair, exported from the feature package root. | House naming already pairs `get_*` with `reset_*` in all five modules; a sibling reads as the third member of the same trio and keeps the public API symmetrical (Q-3). |
| D2 | Installing over a **non-empty** slot replaces the instance unconditionally and logs **one WARNING** record naming the slot; installing into an **empty** slot logs no WARNING. | The test helpers legitimately install twice per test (save/restore) and the composition root installs once; raising would break both. A WARNING makes an accidental clobber visible without changing behavior (Q-5). |
| D3 | An install is **not retroactive**: it changes only what a later `get_*()` returns. An object already constructed with an instance keeps that instance. | Constructor injection is the existing pattern (`SettingsRegistry(event_bus=...)`, `SearchService(...)`); silently re-pointing live objects would be a behavior change this change does not claim (Q-6). |
| D4 | The parameter is the feature's concrete class, never `None`. Clearing the slot stays `reset_*()`. | One operation per intent: install installs, reset clears. A `None`-accepting setter would duplicate `reset_*` and erase the WARNING signal (Q-7). |
| D5 | The parameter is validated by its annotation and `mypy src/` only. No `isinstance` check, no new exception. | The five modules are internal backend code with a typed call surface; a runtime check would add an unspecified error path for a mistake the type checker already catches (Q-8). |
| D6 | Each owning module guards **all three** slot operations — install, lazy create, reset — with one module-level `threading.Lock`. | The search module already does this (`src/backend/search/service.py:547,558,571`); the other four use a bare one-element list. One lock per module closes the create race and makes install/reset atomic with respect to reads (Q-9). |
| D7 | An owning module's **own** lazy path keeps its direct slot write and does not call the public setter; it takes the same lock. | Routing the lazy path through `set_*` would emit a second traced entry/exit pair per first read and would make the WARNING path reachable from a read. The lock, not the setter, is what makes the lazy path safe (Q-10). |
| D8 | An install publishes **no** event. | The settings feature's D7 ("`set_value()` publishes `SettingChanged`") is about values, not the slot; the other four features have no slot event. Adding one would be new behavior no requirement asks for (Q-10). |
| D9 | Each new function is traced `@logged(slow_threshold_ms=5)` with the **default** `include_args`. | The logging feature's tracing policy (`docs/specs/logging-coverage.md` REQ-001/REQ-007, ADR-060) requires `@logged` on public module-level functions and a concrete threshold; the installed object is a service instance, not a secret, so the default is right and the five sibling getters already use the same threshold (Q-13, Q-14). |
| D10 | The composition root keeps its module-import-time wiring **in its current position** (`src/main.py:137-138`), installs through the public setter, and reads the global back at its consumer sites. | Moving the wiring to a `create_app()` factory is the deferred `composition-root-factory` TODO; this change only replaces the mechanism, so the diff stays reviewable and `docs/specs/settings-coverage.md` REQ-002 startup wiring is unaffected (Q-11). |
| D11 | The test suite migrates to the public setter with the **same** save/restore semantics it has today (capture the current instance, install the scratch one, restore in a `finally`). | The helpers' isolation contract (`tests/settings_test_helpers.py`, `tests/eventbus_test_helpers.py`) is behavioral, not incidental; migrating must not weaken a single test (Q-12). |
| D12 | Two guards: (a) a pytest scan test under `tests/unit/` that fails on a cross-package private-slot write, and (b) ruff `TID251` banned-api entries for the five private slots. | The scan test is the repo's existing pattern for architecture rules; `TID251` catches the import that makes the write possible before it is ever written. Both are needed: the scan test sees the write, ruff sees the import (Q-16). |
| D13 | `AGENTS.md` gains one bullet per feature in its five "Using the …" sections; no new section, no new pattern prose. | The guidance that makes future features use the setter is a bullet in the section that already tells them which feature to use (Q-17). |
| D14 | An install neither shuts down nor starts the instance it replaces. | `reset_event_bus()` shuts the replaced bus down (event-bus REQ-005); an install that did the same would destroy a bus the caller may still hold. Lifecycle stays with the caller, which is what the existing scratch/park pattern in `tests/eventbus_test_helpers.py:76-85` already assumes. |
| D15 | No ADR is written at P.4. | Q-1 defers the ADR decision to Phase 2 (S2.1); the ADR threshold (new dependency / new pattern / cross-feature interface) is argued in `docs/verification/settings-public-registry-setter.md`. |

## 3. Data Structures & API Schemas

### 3.1 The install operation (new public API, one per singleton-owning feature)

```python
# module: backend.settings           (src/backend/settings/registry.py, re-exported from backend.settings)
def set_settings_registry(registry: SettingsRegistry) -> None: ...

# module: backend.eventbus           (src/backend/eventbus/eventbus.py, re-exported from backend.eventbus)
def set_event_bus(bus: EventBus) -> None: ...

# module: backend.permissions        (src/backend/permissions/service.py, re-exported from backend.permissions)
def set_permission_service(service: PermissionService) -> None: ...

# module: backend.search             (src/backend/search/service.py, re-exported from backend.search)
def set_search_service(service: SearchService) -> None: ...

# module: backend.sessionmanagement  (src/backend/sessionmanagement/service.py, re-exported from backend.sessionmanagement)
def set_session_service(service: SessionService) -> None: ...
```

Each is the third member of the feature's existing singleton trio:

| Feature | Slot (private) | Read | **Install (new)** | Clear |
|---|---|---|---|---|
| settings | `registry._registry` | `get_settings_registry(required: bool = True) -> SettingsRegistry \| None` | `set_settings_registry(registry)` | `reset_settings_registry()` |
| eventbus | `eventbus._default_bus` | `get_event_bus() -> EventBus` | `set_event_bus(bus)` | `reset_event_bus()` (shuts the instance down) |
| permissions | `service._permission_service` | `get_permission_service() -> PermissionService` | `set_permission_service(service)` | `reset_permission_service()` |
| search | `service._singleton` | `get_search_service(...) -> SearchService` | `set_search_service(service)` | `reset_search_service()` |
| sessionmanagement | `service._session_service` | `get_session_service(repository=None, ...) -> SessionService` | `set_session_service(service)` | `reset_session_service()` |

### 3.2 Required shape of the operation (normative)

```python
_registry_lock = threading.Lock()          # one module-level lock per owning module (REQ-006)


@logged(slow_threshold_ms=5)               # REQ-010
def set_settings_registry(registry: SettingsRegistry) -> None:
    """Install ``registry`` as the shared default registry (singleton)."""
    with _registry_lock:                   # REQ-006: the read-and-swap is atomic
        previous = _registry[0]
        _registry[0] = registry
    if previous is not None:               # REQ-002: replace + exactly one WARNING
        logger.warning("settings: shared default registry replaced")
```

The owning module's read and clear paths take the **same** lock and keep their direct slot access (D7):

```python
@logged(slow_threshold_ms=5)
def get_settings_registry(required: bool = True) -> SettingsRegistry | None:
    with _registry_lock:                   # REQ-006: the lazy create is atomic
        reg = _registry[0]
        if reg is None:
            if not required:
                return None                # settings-coverage REQ-012 / EDGE-011 unchanged
            reg = SettingsRegistry()
            _registry[0] = reg             # REQ-007: direct write, no nested set_* call
    return reg


@logged(slow_threshold_ms=5)
def reset_settings_registry() -> None:
    with _registry_lock:                   # REQ-006
        _registry[0] = None
```

The search module already holds `_singleton_lock` and already guards its lazy create and reset (`src/backend/search/service.py:547,558,571`); for search the change is the install function plus the guarantee that all three paths share that one lock.

### 3.3 Composition root (normative shape)

`src/main.py` keeps its module-import-time wiring in its current position (D10). The private-slot import and write are replaced by the public setter:

```python
# before (src/main.py:68, 137-138)
from backend.settings.registry import _registry as _settings_registry_singleton
_settings_registry = SettingsRegistry(...)
_settings_registry_singleton[0] = _settings_registry

# after
from backend.settings import set_settings_registry
_settings_registry = SettingsRegistry(...)
set_settings_registry(_settings_registry)
```

`src/main.py` reads the shared instance back through the public getter at its consumer sites; it does not keep a private handle to the slot.

### 3.4 Guards (normative)

```toml
# pyproject.toml — ruff banned-api (REQ-013)
[tool.ruff.lint.flake8-tidy-imports.banned-api]
"backend.settings.registry._registry".msg = "use backend.settings.set_settings_registry() / get_settings_registry() / reset_settings_registry()"
"backend.eventbus.eventbus._default_bus".msg = "use backend.eventbus.set_event_bus() / get_event_bus() / reset_event_bus()"
"backend.permissions.service._permission_service".msg = "use backend.permissions.set_permission_service() / get_permission_service() / reset_permission_service()"
"backend.search.service._singleton".msg = "use backend.search.set_search_service() / get_search_service() / reset_search_service()"
"backend.sessionmanagement.service._session_service".msg = "use backend.sessionmanagement.set_session_service() / get_session_service() / reset_session_service()"
```

```python
# tests/unit/architecture/test_singleton_slots.py (REQ-012, REQ-013)
# Scans every .py file under src/ and tests/ for an assignment to another package's
# singleton slot (attribute-chain write ending in the private slot name) and fails
# with the offending file:line. A module may still write its OWN slot.
```

## 4. Requirements

| ID | Requirement |
|----|-------------|
| REQ-001 | Each of the five singleton-owning features exports a public install operation — `set_settings_registry`, `set_event_bus`, `set_permission_service`, `set_search_service`, `set_session_service` — that takes one argument of the feature's concrete class and returns `None`, and installs it as the module singleton so a later `get_*()` returns exactly that instance. |
| REQ-002 | An install into a **non-empty** slot replaces the previous instance unconditionally and logs exactly one WARNING record naming the feature's shared default; an install into an **empty** slot logs no WARNING. |
| REQ-003 | An install is not retroactive: it changes only what a later `get_*()` returns. An object constructed earlier with an instance keeps that instance, and an install never mutates, shuts down or starts the instance it replaces. |
| REQ-004 | The install parameter is the feature's concrete instance; it never accepts `None`, and clearing the slot remains the exclusive job of the feature's `reset_*()` operation. |
| REQ-005 | The install parameter is validated by its type annotation and `mypy src/` only: no runtime `isinstance` check, no new exception type, and no error path beyond the lock and the WARNING. |
| REQ-006 | In all five owning modules the three slot operations — install, lazy create (including the `required=False` guarded read), and reset — are mutually exclusive with each other, guarded by one module-level `threading.Lock` per module. |
| REQ-007 | An owning module's own lazy-create path keeps its direct write to its own slot and does not call the public install operation; it performs that write under the module lock. |
| REQ-008 | Install and reset form a pair: after `set_x(instance)` then `reset_x()`, the next `get_x()` returns a lazily created default instance, not the installed one. |
| REQ-009 | An install publishes no event on any event bus, and changes nothing about the five features' event surfaces. |
| REQ-010 | Each install operation is traced with `@logged(slow_threshold_ms=5)` and the decorator's default `include_args`, and each appears as a `module function` row in the `docs/specs/logging-coverage.md` §3.1 inventory. |
| REQ-011 | The composition root `src/main.py` installs the registry it wires through `set_settings_registry()` at its current module-import-time position, imports no private singleton slot, and obtains the shared instance at its consumer sites through `get_settings_registry()`; the startup wiring required by `docs/specs/settings-coverage.md` REQ-002 still runs once, before any feature code. |
| REQ-012 | No file under `src/` or `tests/` writes another package's singleton slot: every one of the 12 existing outside-owner write sites is migrated to the owning feature's install operation, keeping the current capture-install-restore semantics, and no existing test is weakened, converted or deleted. |
| REQ-013 | The private-slot pattern is guarded twice: a pytest scan test under `tests/unit/` fails when any file assigns to a singleton slot it does not own, and ruff `TID251` bans importing the five private slots. |
| REQ-014 | Each install operation is re-exported from its feature package (`__init__.py` `__all__`); no existing public symbol is removed, renamed, or re-typed. |
| REQ-015 | `AGENTS.md` documents the install operation for each of the five features: one bullet in that feature's "Using the …" section naming the function, its replace-plus-WARNING semantics, and that `reset_*()` stays the test seam. |
| REQ-016 | The five install operations are wiring functions, not permission catalog entries: the static catalog defined by `docs/specs/user-roles-permissions.md` (the public non-underscore methods of the six public service classes) is unchanged, and no new action is registered. |

## 5. Acceptance Criteria

| ID | References | Criterion |
|----|------------|-----------|
| AC-001 | REQ-001 | **Given** the settings module with an empty shared slot and a `SettingsRegistry` built with isolated repositories, **When** `set_settings_registry(registry)` is called, **Then** it returns `None`, **And** `get_settings_registry()` returns that exact instance (identity, `is`). |
| AC-002 | REQ-001 | **Given** each of the five singleton-owning features and a fresh instance of its class, **When** its install operation is called, **Then** the matching `get_*()` returns that exact instance (parametrized over `set_settings_registry`/`set_event_bus`/`set_permission_service`/`set_search_service`/`set_session_service`). |
| AC-003 | REQ-002 | **Given** the shared slot already holds instance A, **When** the install operation is called with instance B, **Then** no exception is raised, **And** `get_*()` returns B, **And** exactly one WARNING record is emitted that names the feature's shared default. |
| AC-004 | REQ-002 | **Given** the shared slot is empty, **When** the install operation is called with instance A, **Then** `get_*()` returns A, **And** no WARNING record is emitted. |
| AC-005 | REQ-003 | **Given** a service constructed with instance A injected and the shared slot holding A, **When** `set_x(B)` is called, **Then** the service still uses A (its behavior is unchanged), **And** a later `get_x()` returns B. |
| AC-006 | REQ-003 | **Given** the shared slot holds a running `EventBus`, **When** `set_event_bus(other)` replaces it, **Then** the replaced bus is not shut down (it still dispatches an event published to it), **And** the installed bus is not started by the install. |
| AC-007 | REQ-004, REQ-014 | **Given** the five install operations, **When** their signatures are inspected, **Then** each takes exactly one parameter annotated with the feature's concrete class (not `Optional`/`None`-able), **And** each returns `None`, **And** each is exported from its feature package's `__all__`. |
| AC-008 | REQ-005 | **Given** an install operation called with an instance of the annotated class, **When** it runs, **Then** no exception is raised, **And** the owning feature's public exception hierarchy contains no new type, **And** the module contains no runtime type check on the parameter. |
| AC-009 | REQ-006 | **Given** an empty shared slot, **When** 8 threads call `get_*()` concurrently, **Then** every thread returns the same instance, **And** exactly one default instance was constructed. |
| AC-010 | REQ-006 | **Given** the shared slot holds instance A, **When** 8 threads install B1…B8 concurrently while 8 threads call `get_*()` and 2 threads call `reset_*()` (barrier-synchronised), **Then** no read raises and no read observes a half-written slot, **And** the slot's final value is one of the installed instances or `None` (a reset that ran last), **And** no thread raises. |
| AC-011 | REQ-007 | **Given** an empty shared slot and the logging pipeline active at DEBUG, **When** `get_*()` lazily creates the default, **Then** exactly one traced entry/exit pair is emitted for that read, **And** no entry record for the install operation appears, **And** the created instance is in the slot. |
| AC-012 | REQ-008 | **Given** instance A installed in the shared slot of settings, eventbus, permissions or search, **When** `reset_*()` is called and then `get_*()`, **Then** the returned instance is a freshly created default and is not A. |
| AC-013 | REQ-009 | **Given** a recording event bus, **When** any of the five install operations is called (into an empty slot and over a non-empty slot), **Then** the recorder captured no event. |
| AC-014 | REQ-010 | **Given** the logging pipeline active at DEBUG, **When** an install operation is called, **Then** exactly one entry record and one exit record (with elapsed ms) name that function, **And** the exit record is at DEBUG, **And** no local variable values appear in any record. |
| AC-015 | REQ-010 | **Given** the `docs/specs/logging-coverage.md` §3.1 inventory, **When** it is read after the change, **Then** it contains a `module function` row for each of the five install operations, **And** each of the five functions is actually traced (`__logged__ is True`) with a concrete `slow_threshold_ms`. |
| AC-016 | REQ-011 | **Given** a fresh subprocess that imports `main`, **When** `get_settings_registry()` is called afterwards, **Then** it returns the registry the composition root wired (its feature settings are registered), **And** `src/main.py` contains no import of a private singleton slot. |
| AC-017 | REQ-012, REQ-013 | **Given** every `.py` file under `src/` and `tests/`, **When** the slot-write scanner runs, **Then** it reports no assignment to a singleton slot owned by a different package, **And** a planted violation fixture (a file that writes another package's slot) is reported with its path and line. |
| AC-018 | REQ-013 | **Given** a file that imports one of the five private slots, **When** `ruff check` runs on it, **Then** a `TID251` violation is reported naming the public install/get/reset operations, **And** the repository itself reports no `TID251` violation. |
| AC-019 | REQ-015 | **Given** `AGENTS.md`, **When** its five "Using the …" sections are read, **Then** each names that feature's install operation, **And** each states that installing over a non-empty default logs a WARNING, **And** each keeps `reset_*()` as the test seam. |
| AC-020 | REQ-016 | **Given** the permission catalog built from the six public service classes, **When** it is built after the change, **Then** the set of registered actions is identical to before, **And** none of the five install operations appears as an action. |

## 6. Invariants

| ID | Invariant |
|----|-----------|
| INV-001 | For any sequence of install, reset and read operations applied to one feature's singleton, every `get_*()` call returns exactly the instance installed by the most recent install in the sequence, or a lazily created default when the slot was empty at that read. No install is ever silently lost. |
| INV-002 | For any sequence of installs on one feature's singleton, the number of WARNING records emitted equals the number of installs applied to a slot that was non-empty at the moment of the install — no more, no fewer. |
| INV-003 | For any sequence of installs, no event bus (shared or injected) receives an event caused by the install, and every object that was constructed with an injected instance keeps that exact instance. |

## 7. Edge Cases & Error Conditions

| ID | Condition | Expected Behavior |
|----|-----------|-------------------|
| EDGE-001 | Install over a non-empty slot (the composition root re-imported, a helper that installs twice) | The instance is replaced, exactly one WARNING record is logged, no exception is raised. |
| EDGE-002 | The same instance is installed twice in a row | The second install logs a WARNING (the slot was non-empty), and the slot holds that instance. |
| EDGE-003 | `get_session_service()` after `reset_session_service()` with no `repository` argument | Still raises `ValueError` (session-management AC-042 unchanged); after `set_session_service(instance)` the same call returns the installed instance with no `repository` argument. |
| EDGE-004 | `get_settings_registry(required=False)` after an install / after a reset | Returns the installed instance; after a reset returns `None` and creates nothing (`docs/specs/settings-coverage.md` REQ-012 / EDGE-011 preserved). |
| EDGE-005 | Install executed inside a subprocess (`python -c`) — the four subprocess-embedded test sites | Identical semantics in the fresh interpreter: the installed instance is what a later read returns; the WARNING goes to that process's sink. |
| EDGE-006 | Installing over a live `EventBus` whose worker is running | The replaced bus is not shut down by the install and keeps dispatching until its owner shuts it down; the installed bus is not started until its first `publish()`. |
| EDGE-007 | `reset_event_bus()` | Still shuts the instance down (event-bus REQ-005); the WARNING rule applies to install only, not to reset. |
| EDGE-008 | A module writing its **own** private slot (the five lazy-create and reset paths) | Not reported by the scan test and not banned by ruff: the guard targets cross-package writes/imports only. |
| EDGE-009 | Importing the public trio (`get_*`, `set_*`, `reset_*`) | Never flagged: `TID251` bans the five private slot names, not the public API. |
| EDGE-010 | Install called from several threads at once | One install wins the slot; every install that found a non-empty slot logged its WARNING; no exception, no lost update beyond the last writer (AC-010). |

## 8. Non-Functional Requirements

| ID | Category | Requirement |
|----|----------|-------------|
| NFR-001 | Contract | The five install operations are purely additive: every existing public symbol of the five features keeps its signature and behavior (settings NFR-002, event-bus NFR-004, permissions NFR-003, search NFR-003, session-management NFR-003). |
| NFR-002 | Performance | An install completes in < 1 ms (median), measured with the logging pipeline active at DEBUG (console + queue sinks) — the observability context the feature actually runs in — on the same machine and measurement style as the existing logging NFR-002 budget. |
| NFR-003 | Reliability | The module lock is held only for the slot read/swap: no feature-level work (repository or service construction, event publication, `shutdown()`) happens under the lock in the install path, and the WARNING record is emitted after the lock is released. |
| NFR-004 | Contract | `uv run ruff check .` reports no `TID251` violation in the repository and `uv run mypy src/` is clean with the new API; the `banned-api` table stays configured in `pyproject.toml`. |

## 9. Observability & Logging

| Event | Level | Data |
|-------|-------|------|
| Install into an empty slot | DEBUG (tracing entry/exit only) | function name, elapsed ms |
| Install over a non-empty slot | WARNING | the feature's shared-default name (e.g. `settings: shared default registry replaced`); never the instance's contents |
| Lazy create on first read | DEBUG | unchanged from today (eventbus logs its own create record) |
| Reset | DEBUG | unchanged from today |

Conventions: the five install operations are traced with `@logged(slow_threshold_ms=5)` (the same threshold as the sibling `get_*`/`reset_*` functions); `diagnose=False` stays enforced by the logging feature; the record never contains a password, token or file content; the functions are imported only from the feature package root (`from backend.settings import set_settings_registry`), never from a private module.

## 10. Test Strategy

New test package: `tests/{acceptance,unit,property,contract,integration}/singleton_install/` (the change's own vocabulary, mirroring the `logging_coverage` / `settings_coverage` packages). The existing `tests/acceptance/logging_coverage/test_inventory.py` and `tests/logging_coverage_test_helpers.py` gain additive rows only.

| ID | Test Category | Test File | Test Function |
|----|---------------|-----------|---------------|
| REQ-001 | acceptance | `tests/acceptance/singleton_install/test_install.py` | `test_ac_001_install_then_get_returns_instance` |
| REQ-002 | acceptance | `tests/acceptance/singleton_install/test_install.py` | `test_ac_003_replace_logs_one_warning` |
| REQ-003 | acceptance | `tests/acceptance/singleton_install/test_install.py` | `test_ac_005_install_not_retroactive` |
| REQ-004 | contract | `tests/contract/singleton_install/test_api_contract.py` | `test_ac_007_signature_takes_concrete_instance` |
| REQ-005 | contract | `tests/contract/singleton_install/test_api_contract.py` | `test_ac_008_no_runtime_type_check_no_new_error` |
| REQ-006 | acceptance | `tests/acceptance/singleton_install/test_concurrency.py` | `test_ac_009_concurrent_lazy_create` |
| REQ-007 | acceptance | `tests/acceptance/singleton_install/test_install.py` | `test_ac_011_lazy_path_emits_one_traced_pair` |
| REQ-008 | acceptance | `tests/acceptance/singleton_install/test_install.py` | `test_ac_012_install_then_reset_then_default` |
| REQ-009 | acceptance | `tests/acceptance/singleton_install/test_install.py` | `test_ac_013_install_publishes_no_event` |
| REQ-010 | acceptance | `tests/acceptance/singleton_install/test_install.py` | `test_ac_014_install_is_traced` |
| REQ-011 | integration | `tests/integration/singleton_install/test_composition_root.py` | `test_ac_016_main_installs_through_setter` |
| REQ-012 | unit | `tests/unit/architecture/test_singleton_slots.py` | `test_ac_017_no_cross_package_slot_write` |
| REQ-013 | unit | `tests/unit/architecture/test_singleton_slots.py` | `test_ac_017_scanner_reports_planted_violation` |
| REQ-013 | contract | `tests/contract/singleton_install/test_lint_contract.py` | `test_ac_018_ruff_bans_private_slot_import` |
| REQ-014 | contract | `tests/contract/singleton_install/test_api_contract.py` | `test_ac_007_signature_takes_concrete_instance` |
| REQ-015 | contract | `tests/contract/singleton_install/test_guidance_contract.py` | `test_ac_019_agents_md_names_installer` |
| REQ-016 | contract | `tests/contract/singleton_install/test_api_contract.py` | `test_ac_020_permission_catalog_unchanged` |
| AC-001 | acceptance | `tests/acceptance/singleton_install/test_install.py` | `test_ac_001_install_then_get_returns_instance` |
| AC-002 | acceptance | `tests/acceptance/singleton_install/test_install.py` | `test_ac_002_install_all_five_features` |
| AC-003 | acceptance | `tests/acceptance/singleton_install/test_install.py` | `test_ac_003_replace_logs_one_warning` |
| AC-004 | acceptance | `tests/acceptance/singleton_install/test_install.py` | `test_ac_004_empty_slot_no_warning` |
| AC-005 | acceptance | `tests/acceptance/singleton_install/test_install.py` | `test_ac_005_install_not_retroactive` |
| AC-006 | acceptance | `tests/acceptance/singleton_install/test_install.py` | `test_ac_006_replaced_bus_keeps_lifecycle` |
| AC-007 | contract | `tests/contract/singleton_install/test_api_contract.py` | `test_ac_007_signature_takes_concrete_instance` |
| AC-008 | contract | `tests/contract/singleton_install/test_api_contract.py` | `test_ac_008_no_runtime_type_check_no_new_error` |
| AC-009 | acceptance | `tests/acceptance/singleton_install/test_concurrency.py` | `test_ac_009_concurrent_lazy_create` |
| AC-010 | acceptance | `tests/acceptance/singleton_install/test_concurrency.py` | `test_ac_010_concurrent_install_read_reset` |
| AC-011 | acceptance | `tests/acceptance/singleton_install/test_install.py` | `test_ac_011_lazy_path_emits_one_traced_pair` |
| AC-012 | acceptance | `tests/acceptance/singleton_install/test_install.py` | `test_ac_012_install_then_reset_then_default` |
| AC-013 | acceptance | `tests/acceptance/singleton_install/test_install.py` | `test_ac_013_install_publishes_no_event` |
| AC-014 | acceptance | `tests/acceptance/singleton_install/test_install.py` | `test_ac_014_install_is_traced` |
| AC-015 | acceptance | `tests/acceptance/logging_coverage/test_inventory.py` | `test_inventory_covers_install_operations` |
| AC-016 | integration | `tests/integration/singleton_install/test_composition_root.py` | `test_ac_016_main_installs_through_setter` |
| AC-017 | unit | `tests/unit/architecture/test_singleton_slots.py` | `test_ac_017_no_cross_package_slot_write`, `test_ac_017_scanner_reports_planted_violation` |
| AC-018 | contract | `tests/contract/singleton_install/test_lint_contract.py` | `test_ac_018_ruff_bans_private_slot_import` |
| AC-019 | contract | `tests/contract/singleton_install/test_guidance_contract.py` | `test_ac_019_agents_md_names_installer` |
| AC-020 | contract | `tests/contract/singleton_install/test_api_contract.py` | `test_ac_020_permission_catalog_unchanged` |
| INV-001 | property | `tests/property/singleton_install/test_install_properties.py` | `test_inv_001_last_install_wins` |
| INV-002 | property | `tests/property/singleton_install/test_install_properties.py` | `test_inv_002_warning_count_matches_nonempty_installs` |
| INV-003 | property | `tests/property/singleton_install/test_install_properties.py` | `test_inv_003_no_events_and_no_rebinding` |
| EDGE-001 | unit | `tests/unit/singleton_install/test_edges.py` | `test_edge_001_install_over_nonempty` |
| EDGE-002 | unit | `tests/unit/singleton_install/test_edges.py` | `test_edge_002_same_instance_twice` |
| EDGE-003 | unit | `tests/unit/singleton_install/test_edges.py` | `test_edge_003_session_service_repository_rule` |
| EDGE-004 | unit | `tests/unit/singleton_install/test_edges.py` | `test_edge_004_required_false_after_install_and_reset` |
| EDGE-005 | unit | `tests/unit/singleton_install/test_edges.py` | `test_edge_005_install_in_subprocess` |
| EDGE-006 | unit | `tests/unit/singleton_install/test_edges.py` | `test_edge_006_live_bus_not_shut_down` |
| EDGE-007 | unit | `tests/unit/singleton_install/test_edges.py` | `test_edge_007_reset_event_bus_still_shuts_down` |
| EDGE-008 | unit | `tests/unit/architecture/test_singleton_slots.py` | `test_edge_008_owner_slot_write_allowed` |
| EDGE-009 | contract | `tests/contract/singleton_install/test_lint_contract.py` | `test_edge_009_public_api_not_banned` |
| EDGE-010 | acceptance | `tests/acceptance/singleton_install/test_concurrency.py` | `test_ac_010_concurrent_install_read_reset` |
| NFR-001 | contract | `tests/contract/singleton_install/test_api_contract.py` | `test_nfr_001_public_api_additive` |
| NFR-002 | contract | `tests/contract/singleton_install/test_performance_contract.py` | `test_nfr_002_install_latency` |
| NFR-003 | acceptance | `tests/acceptance/singleton_install/test_concurrency.py` | `test_nfr_003_slot_lock_is_short_lived` |
| NFR-004 | contract | `tests/contract/singleton_install/test_lint_contract.py` | `test_nfr_004_ruff_and_mypy_clean` |
| — | integration | `tests/integration/singleton_install/test_composition_root.py` | `test_installed_registry_serves_feature_registration` |

**Migration coverage (REQ-012).** The 12 migrated write sites are not covered by new tests of their own: each site belongs to an existing test whose behavior must stay identical (`tests/settings_test_helpers.py`, `tests/eventbus_test_helpers.py`, `tests/acceptance/settings_coverage/test_setup_logger.py`, `tests/acceptance/settings_coverage/test_wiring.py`, `tests/contract/logging/test_logging_contracts.py`, `tests/property/logging/test_logging_properties.py`, `tests/unit/logging/test_logging_edges.py`). Their evidence is (a) the scan test AC-017 proving no site writes a foreign slot, and (b) the Phase 5 full-suite regression run showing the migrated tests still GREEN with no test weakened or deleted.

## 11. Traceability Matrix

Maintain this matrix as tests are written and pass. Every normative requirement MUST have at least one executable test.

| Requirement | Acceptance Criterion | Test | Status |
|-------------|---------------------|------|--------|
| REQ-001 | AC-001, AC-002 | `test_ac_001_install_then_get_returns_instance`, `test_ac_002_install_all_five_features` | PENDING |
| REQ-002 | AC-003, AC-004 | `test_ac_003_replace_logs_one_warning`, `test_ac_004_empty_slot_no_warning` | PENDING |
| REQ-003 | AC-005, AC-006 | `test_ac_005_install_not_retroactive`, `test_ac_006_replaced_bus_keeps_lifecycle` | PENDING |
| REQ-004 | AC-007 | `test_ac_007_signature_takes_concrete_instance` | PENDING |
| REQ-005 | AC-008 | `test_ac_008_no_runtime_type_check_no_new_error` | PENDING |
| REQ-006 | AC-009, AC-010 | `test_ac_009_concurrent_lazy_create`, `test_ac_010_concurrent_install_read_reset` | PENDING |
| REQ-007 | AC-011 | `test_ac_011_lazy_path_emits_one_traced_pair` | PENDING |
| REQ-008 | AC-012 | `test_ac_012_install_then_reset_then_default` | PENDING |
| REQ-009 | AC-013 | `test_ac_013_install_publishes_no_event` | PENDING |
| REQ-010 | AC-014, AC-015 | `test_ac_014_install_is_traced`, `test_inventory_covers_install_operations` | PENDING |
| REQ-011 | AC-016 | `test_ac_016_main_installs_through_setter` | PENDING |
| REQ-012 | AC-017 | `test_ac_017_no_cross_package_slot_write` | PENDING |
| REQ-013 | AC-017, AC-018 | `test_ac_017_scanner_reports_planted_violation`, `test_ac_018_ruff_bans_private_slot_import` | PENDING |
| REQ-014 | AC-007 | `test_ac_007_signature_takes_concrete_instance` | PENDING |
| REQ-015 | AC-019 | `test_ac_019_agents_md_names_installer` | PENDING |
| REQ-016 | AC-020 | `test_ac_020_permission_catalog_unchanged` | PENDING |
| INV-001 | — | `test_inv_001_last_install_wins` (property) | PENDING |
| INV-002 | — | `test_inv_002_warning_count_matches_nonempty_installs` (property) | PENDING |
| INV-003 | — | `test_inv_003_no_events_and_no_rebinding` (property) | PENDING |
| EDGE-001 … EDGE-007 | — | `tests/unit/singleton_install/test_edges.py` (one test per ID) | PENDING |
| EDGE-008 | — | `test_edge_008_owner_slot_write_allowed` (unit) | PENDING |
| EDGE-009 | — | `test_edge_009_public_api_not_banned` (contract) | PENDING |
| EDGE-010 | — | `test_ac_010_concurrent_install_read_reset` (acceptance) | PENDING |
| NFR-001 … NFR-004 | — | `tests/contract/singleton_install/` + `test_nfr_003_slot_lock_is_short_lived` | PENDING |
| — | — | `test_installed_registry_serves_feature_registration` (integration) | PENDING |

## 12. Impact Analysis (per affected feature)

| # | Feature / component | What changes | Touched existing IDs (cited, not renumbered) | New IDs (in that spec) |
|---|---------------------|--------------|----------------------------------------------|------------------------|
| 1 | **settings** (`src/backend/settings/registry.py`, `__init__.py`) | New `set_settings_registry()`; one module-level lock now guards install, lazy create (both `required` modes) and reset; `src/main.py` and 9 test sites stop writing `_registry[0]`. | `settings.md` REQ-014 (its singleton-surface enumeration is extended with the install operation), AC-018 (unchanged, cited), NFR-002 (public API backward-compatible, cited); `settings-coverage.md` REQ-012 / AC-016 / EDGE-011 (`required=False` guarded read, unchanged, cited), REQ-002 (startup wiring, unchanged, cited) | `settings.md` **v5**: REQ-026; AC-040, AC-041, AC-042, AC-043; EDGE-030, EDGE-031, EDGE-032, EDGE-033; INV-011 |
| 2 | **eventbus** (`src/backend/eventbus/eventbus.py`, `__init__.py`) | New `set_event_bus()`; a module-level lock now guards install, lazy create and reset (today `_default_bus` is unguarded); `tests/eventbus_test_helpers.py` stops writing `_default_bus[0]`. | `event-bus.md` REQ-006 (enumeration extended), AC-011 (unchanged, cited), NFR-004 (public API list extended with `set_event_bus`), REQ-005 (reset still shuts down, cited) | `event-bus.md` **v2**: REQ-008; AC-013, AC-014, AC-015, AC-016; EDGE-011, EDGE-012 |
| 3 | **permissions / user-roles-permissions** (`src/backend/permissions/service.py`, `__init__.py`) | New `set_permission_service()`; a module-level lock now guards install, lazy create and reset. | `user-roles-permissions.md` REQ-023 (enumeration extended), AC-028 (unchanged, cited), NFR-003 (public API stability, cited); REQ-004, REQ-005, AC-006 (the static 60-key catalog — **unchanged**, cited by this spec's REQ-016) | `user-roles-permissions.md` **v2**: REQ-030; AC-041, AC-042, AC-043, AC-044; EDGE-027, EDGE-028 |
| 4 | **search** (`src/backend/search/service.py`, `__init__.py`) | New `set_search_service()`; the existing `_singleton_lock` now also covers the install path (its lazy create and reset are already guarded). | `search.md` REQ-017 (enumeration extended), AC-032 (unchanged, cited) | `search.md` **v4**: REQ-024; AC-038, AC-039, AC-040, AC-041; EDGE-022, EDGE-023 |
| 5 | **sessionmanagement** (`src/backend/sessionmanagement/service.py`, `__init__.py`) | New `set_session_service()`; a module-level lock now guards install, lazy create and reset. | `session-management.md` REQ-020 (enumeration extended), AC-041, AC-042, AC-043 (unchanged, cited) | `session-management.md` **v2**: REQ-023; AC-046, AC-047, AC-048, AC-049; EDGE-013, EDGE-014 |
| 6 | **logging** (`docs/specs/logging-coverage.md` §3.1 inventory) | Inventory-only impact: five new `module function` rows for the install operations; the test-side inventory helper gains the five entries. **No requirement, AC, invariant, edge or NFR changes.** | `logging-coverage.md` REQ-001 (the inventory is normative, cited), REQ-007 (a concrete `slow_threshold_ms`, cited) | `logging-coverage.md` **v3**: no new IDs — five §3.1 rows only |
| 7 | **composition root** (`src/main.py`) | The private-slot import (`:68`) and write (`:137-138`) are replaced by `set_settings_registry(...)`; consumers read the shared instance through `get_settings_registry()`. Position and order unchanged. | `settings-coverage.md` REQ-002 (startup wiring runs once before feature code — unchanged, cited) | this spec: REQ-011, AC-016 |
| 8 | **test infrastructure** (`tests/settings_test_helpers.py`, `tests/eventbus_test_helpers.py`, 5 logging/settings_coverage test files) | 11 test-side foreign-slot writes replaced by the public install operation; capture-install-restore semantics identical. | `settings-coverage.md` REQ-012 (isolated registries, cited) | this spec: REQ-012, AC-017 |
| 9 | **tooling** (`pyproject.toml`) | `[tool.ruff.lint.flake8-tidy-imports.banned-api]` gains five entries; no new dependency. | — | this spec: REQ-013, AC-018, NFR-004 |
| 10 | **guidance** (`AGENTS.md`) | One bullet per feature in the five "Using the …" sections. | — | this spec: REQ-015, AC-019 |

**No breaking change.** Every public symbol of the five features keeps its signature and behavior; the additions are five new module functions plus five `__all__` entries. The only externally observable differences are (a) a WARNING record when a shared default is replaced, (b) the closed lazy-create race, and (c) a new lint error for code that imports a private singleton slot.

## 13. Out of Scope & Deferred

| Item | Why out of scope | Owner |
|------|------------------|-------|
| Who may import `backend.settings` / `backend.eventbus` (public-API import boundary) | A separate decision with its own guard design; this change only makes the install operation public. | TODO `public-api-import-boundary` |
| A `create_app()` / composition-root factory, moving the wiring out of module import | Explicitly deferred by Q-11; this change keeps the wiring at `src/main.py:137-138` and only replaces the mechanism. | TODO `composition-root-factory` |
| Runtime type validation of the installed instance, a `None`-accepting install, a new exception type | Q-7, Q-8: the annotation plus `mypy src/` is the check. | — |
| Publishing an event on install | Q-10: no requirement asks for it; it would be unspecified new behavior. | — |
| Shutting down or starting the replaced instance | D14: lifecycle belongs to the caller; only `reset_event_bus()` shuts down (event-bus REQ-005). | — |
| Making the install operations permission-catalog actions | REQ-016: the catalog is the public methods of the six service classes; wiring functions are excluded by `user-roles-permissions.md` §3. | — |
| Tracing `get_permission_service()` / `reset_permission_service()` (today untraced and absent from the §3.1 inventory) | A pre-existing logging-coverage gap; fixing it would add inventory rows this change's Q-15 answer does not cover. Recorded as a follow-up candidate. | follow-up candidate |
| Correcting the simplified `get_settings_registry() -> SettingsRegistry` signature block in `docs/specs/settings.md` §3 (the real signature has `required: bool = True` and returns `SettingsRegistry \| None`, normative in `settings-coverage.md` REQ-012) | A code/spec wording gap unrelated to the install operation; it is recorded in `docs/verification/settings-public-registry-setter.md` as a finding for the user, not silently amended. | user decision |
| An ADR | Q-1: the ADR decision is Phase 2's S2.1 gate. | S2.1 |
