# Spec: logging-coverage

## 1. Overview & Objectives
- **Feature Name:** logging-coverage
- **Target Component:** Cross-cutting change to existing backend features (`src/backend/eventbus/`, `src/backend/settings/`, `src/backend/usermanagement/`, `src/backend/authentication/`, `src/backend/logging/`) plus the entrypoint (`src/main.py`). No new feature directory.
- **Goal:** Apply the agreed logging policy to every existing backend class and public module function so that logging is useful for discovering issues and locating performance problems: public classes are traced by default via the shared logging feature, one-off facts stay as direct loguru, log levels reflect semantic significance, sensible slow-call thresholds are set, and `setup_logger` is wired once in the entrypoint.

## 2. Architecture & Design Decisions
- **Design Pattern:** Cross-cutting observability. Public classes are traced with `@logged_class` (classes) or `@logged` (module functions) from the shared logging feature (`backend.logging`). Existing direct loguru statements (one-off facts) are kept unchanged. The entrypoint calls `setup_logger(Settings(...))` exactly once.
- **Dependencies:** `backend.logging` (feature — `logged`, `logged_class`, `setup_logger`, `Settings`, `get_settings`), `loguru` (existing). No new dependencies required (allowed if needed).
- **Constraints:**
  - No new `src/` feature directory; the change is cross-cutting.
  - Tracing adds observability only — it MUST NOT change public API signatures, behavior, or business logic.
  - Tracing MUST preserve ABC abstractness where ABCs are traced.
  - No raw tokens, passwords, or hashes in any log record (hard NFR).
- **Design Decisions:**
  - D1: `@logged_class` is the default for public classes; `@logged` for public module functions. Direct loguru is kept for one-off statements.
  - D2: Log levels reflect semantic significance (DEBUG for routine tracing, INFO for significant lifecycle, WARNING for recoverable issues, ERROR for failures) — not just DEBUG.
  - D3: Every traced class sets a sensible `slow_threshold_ms` for slow-call detection. Exceeding the threshold logs a WARNING and does NOT interrupt the call (observability, not enforcement).
  - D4: Secret/credential handlers use `include_args=False` so arguments never appear in log records.
  - D5: The entrypoint calls `setup_logger(Settings(...))` exactly once at startup (idempotent, thread-safe).
  - D6: Traced classes' docstrings mention tracing (AuthService pattern).
  - D7: New public classes MUST be traced by default (forward-looking policy).

## 3. Data Structures & API Schemas

### 3.1 Class & function inventory

The normative inventory of every public class and public module function across all
backend features, with the required tracing treatment. Exception classes, pure data
models (Pydantic/SQLModel/enum), and Protocol classes are excluded (no behavior to
trace).

| Class / Function | Feature | Kind | Tracing | `include_args` | `slow_threshold_ms` |
|------------------|---------|------|---------|----------------|---------------------|
| `AuthService` | authentication | service | `@logged_class` (existing) | `False` | sensible |
| `UserManager` | usermanagement | service | `@logged_class` (existing) | default | sensible |
| `EventBus` | eventbus | service | `@logged_class` | default | sensible |
| `SettingsRegistry` | settings | service | `@logged_class` | default | sensible |
| `SessionRepository` | authentication | repository ABC | `@logged_class` | default | sensible |
| `PasswordResetRepository` | authentication | repository ABC | `@logged_class` | default | sensible |
| `WebAuthnCredentialRepository` | authentication | repository ABC | `@logged_class` | default | sensible |
| `AttemptTracker` | authentication | provider ABC | `@logged_class` | default | sensible |
| `WebAuthnProvider` | authentication | provider ABC | `@logged_class` | default | sensible |
| `UserRepository` | usermanagement | repository ABC | `@logged_class` | default | sensible |
| `TemplateRepository` | settings | repository ABC | `@logged_class` | default | sensible |
| `SqliteSessionRepository` | authentication | repository | `@logged_class` | `False` | sensible |
| `SqlitePasswordResetRepository` | authentication | repository | `@logged_class` | `False` | sensible |
| `SqliteWebAuthnCredentialRepository` | authentication | repository | `@logged_class` | default | sensible |
| `InMemoryAttemptTracker` | authentication | provider | `@logged_class` | `False` | sensible |
| `PyWebAuthnProvider` | authentication | provider | `@logged_class` | `False` | sensible |
| `SqliteUserRepository` | usermanagement | repository | `@logged_class` | default | sensible |
| `MemoryTemplateRepository` | settings | repository | `@logged_class` | default | sensible |
| `YamlTemplateRepository` | settings | repository | `@logged_class` | default | sensible |
| `new_token()` | authentication | module function | `@logged` | `False` | sensible |
| `hash_token(token)` | authentication | module function | `@logged` | `False` | sensible |
| `get_event_bus()` | eventbus | module function | `@logged` | default | sensible |
| `reset_event_bus()` | eventbus | module function | `@logged` | default | sensible |
| `get_settings_registry()` | settings | module function | `@logged` | default | sensible |
| `reset_settings_registry()` | settings | module function | `@logged` | default | sensible |
| `get_settings()` | logging | module function | `@logged` | default | sensible |
| `setup_logger()` | logging | module function | `@logged` | default | sensible |

Notes:
- "sensible" `slow_threshold_ms` is a per-item value (class or module function) chosen
  for the item's expected latency (see Section 9.1). It is a concrete value in the
  implementation, not `None`.
- "default" `include_args` means the decorator default (arguments are formatted into
  the log record). Secret/credential handlers MUST use `False`.
- `logged` / `logged_class` (the decorators themselves) are NOT traced (they are the
  tracing mechanism).

### 3.2 Tracing annotation patterns

```python
# Public class — default tracing with a sensible slow threshold.
@logged_class
class EventBus: ...

# Public class — secret/credential handler: arguments never appear in log records.
@logged_class  # applied via @logged(..., include_args=False) per method, or a class-level equivalent
class SqlitePasswordResetRepository: ...

# Public module function.
@logged
def get_event_bus() -> EventBus: ...

# Public module function — secret handler.
@logged(include_args=False)
def hash_token(token: str) -> str: ...
```

### 3.3 Entrypoint configuration

```python
# src/main.py — called exactly once at startup, before any feature code runs.
from backend.logging import Settings, setup_logger

setup_logger(Settings(log_level="INFO"))
```

## 4. Requirements

Each normative requirement MUST have a stable ID. These IDs propagate through the
lifecycle: `REQ-001 → AC-001 → test → task → implementation`.

| ID | Requirement |
|----|-------------|
| REQ-001 | The feature defines the normative inventory of every public class and public module function across all backend features, each with its required tracing treatment (Section 3.1). |
| REQ-002 | Every public service and registry class that contains untraced code is traced with `@logged_class` so its public methods produce entry and exit log records (`EventBus`, `SettingsRegistry`). |
| REQ-003 | Every public repository and provider ABC is traced with `@logged_class` so that concrete subclasses inherit tracing; tracing MUST preserve the ABC's abstractness. |
| REQ-004 | Every public concrete repository and provider class is traced with `@logged_class` so its public methods produce entry and exit log records, and the exit record includes elapsed milliseconds. |
| REQ-005 | Every public module-level function is traced with `@logged` so it produces entry and exit log records. |
| REQ-006 | Every traced class or function that handles secrets or credentials uses `include_args=False` so arguments never appear in log records (`SqlitePasswordResetRepository`, `SqliteSessionRepository`, `PyWebAuthnProvider`, `InMemoryAttemptTracker`, `new_token`, `hash_token`). |
| REQ-007 | Every traced class and module function sets a sensible, concrete `slow_threshold_ms` (not `None`) for slow-call detection. |
| REQ-008 | Traced classes use semantic log levels reflecting event significance (DEBUG for routine tracing, INFO for significant lifecycle, WARNING for recoverable issues, ERROR for failures), not only DEBUG. |
| REQ-009 | Every traced class's docstring mentions that the class is traced via the shared logging feature (AuthService pattern). |
| REQ-010 | All existing direct loguru statements are kept unchanged (one-off facts remain direct loguru). |
| REQ-011 | The entrypoint (`src/main.py`) calls `setup_logger(Settings(...))` exactly once at startup, before any feature code runs; a second call is a no-op. |
| REQ-012 | New public classes MUST be traced by default (forward-looking policy), with `include_args=False` where secrets are handled. |
| REQ-013 | A log sink failure MUST NOT interrupt the traced call; the call completes normally (logging is best-effort and non-blocking). |
| REQ-014 | A traced call that exceeds its `slow_threshold_ms` logs a WARNING (slow-call detection) and is NOT interrupted. |
| REQ-015 | No raw tokens, passwords, or hashes appear in any log record. |
| REQ-016 | Tracing MUST NOT change public API signatures, observable behavior, or business logic (observability only). |

## 5. Acceptance Criteria

Each acceptance criterion MUST have a stable ID and MUST reference at least one
requirement. Use Given/When/Then format.

| ID | References | Criterion |
|----|------------|-----------|
| AC-001 | REQ-001 | **Given** the feature, **When** the class and function inventory is reviewed, **Then** every public class and public module function across all backend features is listed, **And** each is marked with its required tracing treatment. |
| AC-002 | REQ-002 | **Given** a public service/registry class (`EventBus`, `SettingsRegistry`), **When** a public method is called, **Then** an entry and an exit log record are produced. |
| AC-003 | REQ-003 | **Given** a public repository/provider ABC traced with `@logged_class`, **When** a concrete subclass is instantiated and a public method is called, **Then** entry and exit log records are produced, **And** the ABC remains abstract (concrete implementation is still required). |
| AC-004 | REQ-004 | **Given** a public concrete repository/provider class, **When** a public method is called, **Then** an entry and an exit log record are produced, **And** the exit record includes elapsed milliseconds. |
| AC-005 | REQ-005 | **Given** a public module-level function, **When** it is called, **Then** an entry and an exit log record are produced. |
| AC-006 | REQ-006 | **Given** a traced class or function that handles secrets/credentials, **When** a public method is called with arguments, **Then** the log records do not include the argument values. |
| AC-007 | REQ-007 | **Given** a traced class, **When** it is inspected, **Then** it has a concrete (non-`None`) `slow_threshold_ms` set. |
| AC-008 | REQ-008 | **Given** a traced class, **When** a significant lifecycle event occurs, **Then** it is logged at a semantic level (INFO/WARNING/ERROR) appropriate to its significance, not only DEBUG. |
| AC-009 | REQ-009 | **Given** a traced class, **When** its docstring is reviewed, **Then** it mentions that the class is traced via the shared logging feature. |
| AC-010 | REQ-010 | **Given** the existing direct loguru statements, **When** the feature is implemented, **Then** all are kept unchanged. |
| AC-011 | REQ-011 | **Given** the entrypoint, **When** the application starts, **Then** `setup_logger(Settings(...))` is called exactly once before any feature code runs, **And** a second call is a no-op. |
| AC-012 | REQ-012 | **Given** a new public class, **When** it is added, **Then** it is traced by default, **And** it uses `include_args=False` where secrets are handled. |
| AC-013 | REQ-013 | **Given** a failing log sink, **When** a traced call is made, **Then** the call completes normally and is not interrupted by the sink failure. |
| AC-014 | REQ-014 | **Given** a traced call that exceeds its `slow_threshold_ms`, **When** it completes, **Then** a WARNING log record is produced and the call is not interrupted. |
| AC-015 | REQ-015 | **Given** any traced class or function, **When** its methods are called, **Then** no raw tokens, passwords, or hashes appear in any log record. |
| AC-016 | REQ-016 | **Given** a traced class or function, **When** it is called, **Then** its public API signature and observable behavior are unchanged by tracing. |

## 6. Invariants

State invariants that hold over a large input space. These become Hypothesis
property-based tests.

| ID | Invariant |
|----|-----------|
| INV-001 | For any traced class and any public method, a single call produces exactly one entry log record and exactly one exit log record. |
| INV-002 | For any traced class or function that handles secrets, for any arguments, the produced log records never include the raw argument values. |
| INV-003 | For any traced call, the exit log record's elapsed milliseconds is non-negative. |
| INV-004 | For any traced call, regardless of whether the slow threshold is exceeded or a sink fails, the call completes normally (tracing never interrupts the call). |

## 7. Edge Cases & Error Conditions

| ID | Condition | Expected Behavior |
|----|-----------|-------------------|
| EDGE-001 | A traced call exceeds its `slow_threshold_ms` | A WARNING log record is produced; the call is NOT interrupted. |
| EDGE-002 | A log sink fails during a traced call | The call completes normally; the sink failure is handled gracefully (best-effort). |
| EDGE-003 | A concrete subclass inherits from a traced ABC | The subclass's public methods produce log records; the ABC remains abstract. |
| EDGE-004 | A traced method raises an exception | An exception log record is produced; the exception propagates to the caller (not swallowed). |
| EDGE-005 | `setup_logger` is called twice | The second call is a no-op (idempotent). |
| EDGE-006 | A traced method is called with no arguments | Entry/exit log records are produced without argument context. |

## 8. Non-Functional Requirements

| ID | Category | Requirement |
|----|----------|-------------|
| NFR-001 | Performance | Tracing must not cause an observable regression; log-record creation overhead is bounded. The slow threshold is an observability mechanism, not enforcement (exceeding it logs a WARNING, does not interrupt). |
| NFR-002 | Security | No raw tokens, passwords, or hashes appear in any log record (hard NFR). |
| NFR-003 | Observability | Log levels reflect semantic significance; entry/exit with elapsed-ms is always logged for traced calls. |
| NFR-004 | Contract | The public API of traced classes is unchanged — tracing adds observability without altering signatures or behavior. |
| NFR-005 | Usability | Logging is useful for discovering issues and locating performance problems (semantic levels, slow-call detection, elapsed-ms). |

## 9. Observability & Logging

Every feature MUST be observable. The logging behavior for traced classes:

| Operation / Event | Level | Context |
|-------------------|-------|---------|
| Method entry (traced) | DEBUG | class, method, arguments (only if `include_args` is not `False`) |
| Method exit (traced) | DEBUG | class, method, elapsed ms |
| Method exception (traced) | ERROR | class, method, exception |
| Slow call detected | WARNING | class, method, elapsed ms, threshold |
| Worker started (EventBus) | INFO | thread name |
| Queue full / event dropped (EventBus) | WARNING | event type, dropped count |
| Handler error (EventBus) | ERROR | handler name, exception |
| Setting registered (SettingsRegistry) | DEBUG | key, kind |
| Value set (SettingsRegistry) | DEBUG | key |
| Value set rejected — invalid (SettingsRegistry) | WARNING | key |
| Template created / loaded / updated / deleted (SettingsRegistry) | INFO | name, scope |
| Login succeeded / failed (AuthService) | INFO | user_id, method |
| Session revoked (AuthService) | INFO | user_id |

- **Default level:** Routine tracing (entry/exit) at DEBUG; significant lifecycle at INFO; recoverable issues at WARNING; failures at ERROR. Production can run at INFO to suppress verbose tracing.
- **Error conditions:** A traced method raising is logged at ERROR and the exception propagates. A slow call is logged at WARNING. A sink failure is handled gracefully (best-effort) and does not interrupt the call.

### 9.1 Sensible `slow_threshold_ms` per class type

Concrete, non-`None` values. The implementation MUST set a concrete value per class;
these are the sensible defaults by class type:

| Class type | `slow_threshold_ms` |
|------------|---------------------|
| DB repositories (`Sqlite*`) | 100 |
| Services / registries (`AuthService`, `UserManager`, `EventBus`, `SettingsRegistry`) | 250 |
| WebAuthn provider (`PyWebAuthnProvider`) | 500 |
| In-memory provider (`InMemoryAttemptTracker`) | 10 |
| Token functions (`new_token`, `hash_token`) | 10 |
| Singleton getters (`get_event_bus`, `get_settings_registry`, `get_settings`) | 5 |

## 10. Test Strategy

Map each requirement/AC to a test category. This drives the test file layout. Tests
verify tracing by capturing log records (attach a loguru sink, call the method,
assert the produced records).

| ID | Test Category | Test File | Test Function |
|----|---------------|-----------|---------------|
| AC-001 | acceptance | `tests/acceptance/logging_coverage/test_inventory.py` | `test_inventory_covers_all_public_classes` |
| AC-002 | acceptance | `tests/acceptance/logging_coverage/test_services_traced.py` | `test_service_registry_classes_traced` |
| AC-003 | acceptance | `tests/acceptance/logging_coverage/test_abc_traced.py` | `test_abc_traced_subclass_inherits` |
| AC-004 | acceptance | `tests/acceptance/logging_coverage/test_services_traced.py` | `test_concrete_repo_provider_traced` |
| AC-005 | acceptance | `tests/acceptance/logging_coverage/test_services_traced.py` | `test_module_functions_traced` |
| AC-006 | acceptance | `tests/acceptance/logging_coverage/test_secret_args.py` | `test_secret_handler_args_not_logged` |
| AC-007 | acceptance | `tests/acceptance/logging_coverage/test_slow_threshold.py` | `test_traced_classes_have_concrete_threshold` |
| AC-008 | acceptance | `tests/acceptance/logging_coverage/test_levels.py` | `test_semantic_log_levels` |
| AC-009 | acceptance | `tests/acceptance/logging_coverage/test_docstrings.py` | `test_traced_class_docstrings_mention_tracing` |
| AC-010 | acceptance | `tests/acceptance/logging_coverage/test_direct_loguru_kept.py` | `test_existing_direct_loguru_kept` |
| AC-011 | acceptance | `tests/acceptance/logging_coverage/test_setup_logger.py` | `test_entrypoint_calls_setup_logger_once` |
| AC-012 | acceptance | `tests/acceptance/logging_coverage/test_new_classes_traced.py` | `test_new_public_classes_traced_by_default` |
| AC-013 | acceptance | `tests/acceptance/logging_coverage/test_sink_failure.py` | `test_sink_failure_does_not_interrupt` |
| AC-014 | acceptance | `tests/acceptance/logging_coverage/test_slow_threshold.py` | `test_slow_call_logs_warning_not_interrupted` |
| AC-015 | acceptance | `tests/acceptance/logging_coverage/test_secret_args.py` | `test_no_raw_secrets_in_any_log_record` |
| AC-016 | acceptance | `tests/acceptance/logging_coverage/test_behavior_unchanged.py` | `test_tracing_does_not_change_behavior` |
| INV-001 | property | `tests/property/logging_coverage/test_invariants.py` | `test_one_entry_one_exit_per_call` |
| INV-002 | property | `tests/property/logging_coverage/test_invariants.py` | `test_secret_args_never_logged` |
| INV-003 | property | `tests/property/logging_coverage/test_invariants.py` | `test_elapsed_ms_non_negative` |
| INV-004 | property | `tests/property/logging_coverage/test_invariants.py` | `test_tracing_never_interrupts_call` |
| EDGE-001 | unit | `tests/unit/logging_coverage/test_edge_cases.py` | `test_slow_threshold_exceeded` |
| EDGE-002 | unit | `tests/unit/logging_coverage/test_edge_cases.py` | `test_sink_failure_graceful` |
| EDGE-003 | unit | `tests/unit/logging_coverage/test_edge_cases.py` | `test_abc_subclass_traced` |
| EDGE-004 | unit | `tests/unit/logging_coverage/test_edge_cases.py` | `test_traced_method_exception_propagates` |
| EDGE-005 | unit | `tests/unit/logging_coverage/test_edge_cases.py` | `test_setup_logger_idempotent` |
| EDGE-006 | unit | `tests/unit/logging_coverage/test_edge_cases.py` | `test_traced_method_no_args` |
| NFR-001 | acceptance | `tests/acceptance/logging_coverage/test_slow_threshold.py` | `test_slow_call_logs_warning_not_interrupted` |
| NFR-002 | acceptance | `tests/acceptance/logging_coverage/test_secret_args.py` | `test_no_raw_secrets_in_any_log_record` |
| NFR-003 | acceptance | `tests/acceptance/logging_coverage/test_levels.py` | `test_semantic_log_levels` |
| NFR-004 | acceptance | `tests/acceptance/logging_coverage/test_behavior_unchanged.py` | `test_tracing_does_not_change_behavior` |
| NFR-005 | acceptance | `tests/acceptance/logging_coverage/test_levels.py` | `test_semantic_log_levels` |

## 11. Traceability Matrix

Maintain this matrix as tests are written and pass. Every normative requirement MUST
have at least one executable test.

| Requirement | Acceptance Criterion | Test | Status |
|-------------|---------------------|------|--------|
| REQ-001 | AC-001 | `test_inventory_covers_all_public_classes` | PENDING |
| REQ-002 | AC-002 | `test_service_registry_classes_traced` | PENDING |
| REQ-003 | AC-003 | `test_abc_traced_subclass_inherits` | PENDING |
| REQ-004 | AC-004 | `test_concrete_repo_provider_traced` | PENDING |
| REQ-005 | AC-005 | `test_module_functions_traced` | PENDING |
| REQ-006 | AC-006 | `test_secret_handler_args_not_logged` | PENDING |
| REQ-007 | AC-007 | `test_traced_classes_have_concrete_threshold` | PENDING |
| REQ-008 | AC-008 | `test_semantic_log_levels` | PENDING |
| REQ-009 | AC-009 | `test_traced_class_docstrings_mention_tracing` | PENDING |
| REQ-010 | AC-010 | `test_existing_direct_loguru_kept` | PENDING |
| REQ-011 | AC-011 | `test_entrypoint_calls_setup_logger_once` | PENDING |
| REQ-012 | AC-012 | `test_new_public_classes_traced_by_default` | PENDING |
| REQ-013 | AC-013 | `test_sink_failure_does_not_interrupt` | PENDING |
| REQ-014 | AC-014 | `test_slow_call_logs_warning_not_interrupted` | PENDING |
| REQ-015 | AC-015 | `test_no_raw_secrets_in_any_log_record` | PENDING |
| REQ-016 | AC-016 | `test_tracing_does_not_change_behavior` | PENDING |
| INV-001 | — | `test_one_entry_one_exit_per_call` | PENDING |
| INV-002 | — | `test_secret_args_never_logged` | PENDING |
| INV-003 | — | `test_elapsed_ms_non_negative` | PENDING |
| INV-004 | — | `test_tracing_never_interrupts_call` | PENDING |
