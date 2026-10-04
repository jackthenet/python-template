# Spec: Logging

## Changelog
- v3 (2026-10-04): Backend swap amendment (change `structlog-logging`, ADR-082 supersedes ADR-002). REQ-001, REQ-003, REQ-005, AC-001, AC-004, INV-001 restated in capability terms (no logging backend named, standard-library handler machinery); **AC-005 and EDGE-005 deleted** (they only existed to serve the removed backend's call-frame arithmetic — the unknown-level case is restated as `EDGE-004` of `docs/specs/structlog-logging.md`); NFR-001, NFR-002, NFR-003 re-measured/restated; NFR-004 restated (the parameter surface is the amended REQ-005 list and `setup_logger()` stays callable with no arguments — the backward-compatibility it requires is the import path, not the removed parameters); Goal and Dependencies rows corrected (the Dependencies row referenced the removed backend, not an ID). §9/§10 test-file paths and function names corrected to the tests that exist on disk (no ID change, no status change).
- v2 (2026-09-11): NFR-001 amended — `setup_logger()` budget relaxed from < 10 ms to < 50 ms (CI observed 15.55 ms; cost is loguru sink setup + file-sink worker thread + mkdir, which 10 ms has no CI headroom for).

## 1. Overview & Objectives
- **Feature Name:** Logging
- **Target Component:** `src/backend/logging/`
- **Goal:** Provide a self-contained logging feature with `setup_logger()` sink setup (console + rotating file), interception of records emitted by third-party code through the standard library, and `@logged` / `@logged_class` decorators for function entry/exit/elapsed-time tracing. The sinks are standard-library handlers owned by the feature; the record format is text on the console and JSON in the file (ADR-082).

## 2. Architecture & Design Decisions
- **Design Pattern:** Feature module with `setup_logger()` entry point, a forwarding handler for records emitted through the standard library, and decorator utilities.
- **Dependencies:** the standard library `logging` handler machinery, a processor/renderer layer over it, and `orjson` for the file sink's JSON records (ADR-082). One-off statements are written through the feature's own `get_logger()` export — feature code does not import a logging backend.
- **Constraints:** Must be importable without application wiring. Must be safe to call multiple times (idempotent). Must never record local variable values (NFR-003). Must never modify handlers, levels or loggers it does not own.
- **Design Decisions:**
  - The obsolete `src/core/logging/` module is deleted and replaced at `src/backend/logging/`.
  - A stub `Settings` module is created at `src/backend/logging/settings.py` providing the fields the logging feature needs. A dedicated `settings` feature will follow later.
  - The core structure (`src/core/`) is no longer supported per `AGENTS.md`; backend features live under `src/backend/`.

## 3. Data Structures & API Schemas
```python
# Stub Settings module — provides configuration fields for the logging feature.
from pydantic import BaseModel


class Settings(BaseModel):
    log_level: str = "INFO"
    log_file: str = "logs/app.log"
    log_max_bytes: int = 10 * 1024 * 1024  # 10 MB rotation
    log_backup_count: int = 5
    profiling_include_arguments: bool = False


def get_settings() -> Settings:
    """Return the current Settings instance."""
    return Settings()
```

```python
# Public API of the logging feature.
from backend.logging import setup_logger, logged, logged_class, get_logger

# Consumer usage:
logger = get_logger("backend.feature")

setup_logger()

@logged
def save(): ...

@logged(level="INFO", slow_threshold_ms=200)
async def generate(): ...

@logged_class(slow_threshold_setting="profiling_include_arguments")
class Service:
    def run(self): ...
```

## 4. Requirements

Each normative requirement MUST have a stable ID. These IDs propagate through the lifecycle:
`REQ-001 → AC-001 → test → task → implementation`.

| ID | Requirement |
|----|-------------|
| REQ-001 | The logging feature provides a `setup_logger()` function that installs a console sink (standard error, colorized human-readable text) and a rotating file sink (UTF-8, JSON records, rotation size and backup count from the settings). The sinks are standard-library handlers owned by the feature; exception records carry traceback frames without local variable values. |
| REQ-002 | `setup_logger()` is idempotent: subsequent calls are no-ops. Thread-safe via a `threading.Event`. |
| REQ-003 | The logging feature forwards records emitted through the standard library's `logging` machinery by third-party code into its own two sinks, preserving the record's level, logger name and originating location. |
| REQ-004 | The logging feature provides a `@logged` decorator that traces sync and async function entry, exit, elapsed time in milliseconds, and exceptions. |
| REQ-005 | `@logged` supports optional parameters: `level`, `slow_threshold_ms`, `slow_threshold_setting`, `include_args`. |
| REQ-006 | When elapsed time exceeds `slow_threshold_ms`, the end-of-call log line escalates to a configurable `slow_level` (default `WARNING`). |
| REQ-007 | The logging feature provides a `@logged_class` decorator that decorates public class methods with the same tracing as `@logged`. |
| REQ-008 | The logging feature provides a stub `Settings` module with fields: `log_level`, `log_file`, `log_max_bytes`, `log_backup_count`, `profiling_include_arguments`. |
| REQ-009 | The obsolete `src/core/logging/` module is deleted. |

## 5. Acceptance Criteria

Each acceptance criterion MUST have a stable ID and MUST reference at least one requirement. Use Given/When/Then format.

| ID | References | Criterion |
|----|------------|-----------|
| AC-001 | REQ-001 | **Given** a fresh Python environment, **When** `setup_logger()` is called, **Then** the feature owns exactly one console sink on standard error writing colorized text, **And** one rotating file sink with UTF-8 encoding, JSON records, and the configured rotation size and backup count. |
| AC-002 | REQ-002 | **Given** `setup_logger()` has been called once, **When** it is called again, **Then** the second call is a no-op and no new sinks are added. |
| AC-003 | REQ-002 | **Given** two threads calling `setup_logger()` concurrently, **When** both complete, **Then** exactly one thread performs the setup and the other is a no-op. |
| AC-004 | REQ-003 | **Given** a record emitted by a third-party logger through the standard library, **When** the logging feature is set up, **Then** the record reaches both of the feature's sinks with its original level, logger name and message, **And** the file record names the emitting source file and line. |
| AC-006 | REQ-004 | **Given** a sync function decorated with `@logged`, **When** the function is called, **Then** an entry log line is emitted, **And** an exit log line with elapsed time in ms is emitted on completion. |
| AC-007 | REQ-004 | **Given** an async function decorated with `@logged`, **When** the function is awaited, **Then** an entry log line is emitted, **And** an exit log line with elapsed time in ms is emitted on completion. |
| AC-008 | REQ-004 | **Given** a function decorated with `@logged` that raises an exception, **When** the function is called, **Then** an exception log line is emitted with the exception type and message, **And** the exception propagates. |
| AC-009 | REQ-005 | **Given** a function decorated with `@logged(level="DEBUG")`, **When** the function is called, **Then** the entry and exit log lines are emitted at DEBUG level. |
| AC-010 | REQ-005 | **Given** a function decorated with `@logged(include_args=True)`, **When** the function is called with arguments, **Then** the entry log line includes the truncated argument representation. |
| AC-011 | REQ-006 | **Given** a function decorated with `@logged(slow_threshold_ms=50)`, **When** the function takes 100 ms, **Then** the end-of-call log line is emitted at WARNING level (the default `slow_level`). |
| AC-012 | REQ-007 | **Given** a class decorated with `@logged_class`, **When** a public method is called, **Then** entry and exit log lines with elapsed time are emitted for that method. |
| AC-013 | REQ-007 | **Given** a class decorated with `@logged_class`, **When** a private method (prefixed with `_`) is called, **Then** no log lines are emitted for that method. |
| AC-014 | REQ-008 | **Given** the logging feature is imported, **When** `get_settings()` is called, **Then** a `Settings` instance is returned with default values for `log_level`, `log_file`, `log_max_bytes`, `log_backup_count`, and `profiling_include_arguments`. |
| AC-015 | REQ-009 | **Given** the logging feature is implemented, **When** the repository is inspected, **Then** `src/core/logging/` does not exist. |

## 6. Invariants

State invariants that hold over a large input space. These become Hypothesis property-based tests.

| ID | Invariant |
|----|-----------|
| INV-001 | For any number of concurrent `setup_logger()` calls, the feature owns exactly one console sink and one file sink. |
| INV-002 | For any sync or async function decorated with `@logged`, the elapsed time reported in the exit log line is non-negative. |
| INV-003 | For any function decorated with `@logged` that raises an exception, the exception propagates unchanged (same type, same args). |

## 7. Edge Cases & Error Conditions

| ID | Condition | Expected Behavior |
|----|-----------|-------------------|
| EDGE-001 | `setup_logger()` called with a `log_file` path whose parent directory does not exist | Parent directory is created automatically. |
| EDGE-002 | `@logged` applied to a function with no arguments | Entry log line emitted without argument representation. |
| EDGE-003 | `@logged` with `slow_threshold_setting` referencing a non-existent Settings field | `slow_threshold_ms` is `None`; no escalation occurs. |
| EDGE-004 | `@logged_class` applied to a class with no public methods | Decorator returns the class unchanged; no error. |

## 8. Non-Functional Requirements

| ID | Category | Requirement |
|----|----------|-------------|
| NFR-001 | Performance | `setup_logger()` must complete in < 25 ms (median of 3 fresh processes). Re-measured for the current pipeline: 0.85 ms median on the reference machine; the previous 50 ms budget was set for the removed backend, which measured 5.18 ms locally and 15.55 ms on CI (`docs/verification/structlog-logging.md`). |
| NFR-002 | Performance | `@logged` decorator overhead per call must be < 1 ms **measured with the two configured sinks active at the configured level** (the context the observability policy requires). Measured: 0.148 ms/call with sinks active at DEBUG, 0.006 ms/call for the tracing machinery alone. |
| NFR-003 | Security | No record may contain local variable values: an exception record carries the exception type, its message and the traceback frames only. |
| NFR-004 | Contract | The public API (`setup_logger`, `logged`, `logged_class`, `get_logger`) stays importable from `backend.logging`; the backward compatibility this requires is the **import path**, not the parameter surface — the parameter list is the amended REQ-005 list, and `setup_logger()` stays callable with no arguments (any parameter it accepts is optional and keyword-only). |

## 9. Test Strategy

Map each requirement/AC to a test category. This drives the test file layout.

| ID | Test Category | Test File | Test Function |
|----|---------------|-----------|---------------|
| AC-001 | acceptance | `tests/acceptance/logging/test_logging.py` | `test_ac_001_setup_logger_adds_sinks` |
| AC-002 | acceptance | `tests/acceptance/logging/test_logging.py` | `test_ac_002_setup_logger_idempotent` |
| AC-003 | unit | `tests/unit/logging/test_logging.py` | `test_ac_003_setup_logger_thread_safe` |
| AC-004 | unit | `tests/unit/logging/test_logging.py` | `test_ac_004_intercept_handler_routes_records` |
| AC-006 | unit | `tests/unit/logging/test_logging.py` | `test_ac_006_logged_sync_entry_exit` |
| AC-007 | unit | `tests/unit/logging/test_logging.py` | `test_ac_007_logged_async_entry_exit` |
| AC-008 | unit | `tests/unit/logging/test_logging.py` | `test_ac_008_logged_exception_propagates` |
| AC-009 | unit | `tests/unit/logging/test_logging.py` | `test_ac_009_logged_level_param` |
| AC-010 | unit | `tests/unit/logging/test_logging.py` | `test_ac_010_logged_include_args` |
| AC-011 | unit | `tests/unit/logging/test_logging.py` | `test_ac_011_logged_slow_threshold` |
| AC-012 | unit | `tests/unit/logging/test_logging.py` | `test_ac_012_logged_class_public_method` |
| AC-013 | unit | `tests/unit/logging/test_logging.py` | `test_ac_013_logged_class_private_method` |
| AC-014 | unit | `tests/unit/logging/test_logging.py` | `test_ac_014_get_settings_defaults` |
| AC-015 | acceptance | `tests/acceptance/logging/test_logging.py` | `test_ac_015_obsolete_module_deleted` |
| INV-001 | property | `tests/property/logging/test_logging_properties.py` | `test_inv_001_concurrent_setup_logger_sinks` |
| INV-002 | property | `tests/property/logging/test_logging_properties.py` | `test_inv_002_elapsed_time_non_negative` |
| INV-003 | property | `tests/property/logging/test_logging_properties.py` | `test_inv_003_exception_propagates_unchanged` |
| EDGE-001 | unit | `tests/unit/logging/test_logging_edges.py` | `test_edge_001_log_file_parent_created` |
| EDGE-002 | unit | `tests/unit/logging/test_logging_edges.py` | `test_edge_002_logged_no_args` |
| EDGE-003 | unit | `tests/unit/logging/test_logging_edges.py` | `test_edge_003_logged_nonexistent_setting` |
| EDGE-004 | unit | `tests/unit/logging/test_logging_edges.py` | `test_edge_004_logged_class_no_public_methods` |
| NFR-004 | contract | `tests/contract/logging/test_logging_contracts.py` | `test_nfr_004_backward_compatible_api` |

## 10. Traceability Matrix

Maintain this matrix as tests are written and pass. Every normative requirement MUST have at least one executable test.

| Requirement | Acceptance Criterion | Test | Status |
|-------------|---------------------|------|--------|
| REQ-001 | AC-001 | `test_ac_001_setup_logger_adds_sinks` | PENDING |
| REQ-002 | AC-002 | `test_ac_002_setup_logger_idempotent` | PENDING |
| REQ-002 | AC-003 | `test_ac_003_setup_logger_thread_safe` | PENDING |
| REQ-003 | AC-004 | `test_ac_004_intercept_handler_routes_records` | PENDING |
| REQ-004 | AC-006 | `test_ac_006_logged_sync_entry_exit` | PENDING |
| REQ-004 | AC-007 | `test_ac_007_logged_async_entry_exit` | PENDING |
| REQ-004 | AC-008 | `test_ac_008_logged_exception_propagates` | PENDING |
| REQ-005 | AC-009 | `test_ac_009_logged_level_param` | PENDING |
| REQ-005 | AC-010 | `test_ac_010_logged_include_args` | PENDING |
| REQ-006 | AC-011 | `test_ac_011_logged_slow_threshold` | PENDING |
| REQ-007 | AC-012 | `test_ac_012_logged_class_public_method` | PENDING |
| REQ-007 | AC-013 | `test_ac_013_logged_class_private_method` | PENDING |
| REQ-008 | AC-014 | `test_ac_014_get_settings_defaults` | PENDING |
| REQ-009 | AC-015 | `test_ac_015_obsolete_module_deleted` | PENDING |
| INV-001 | — | `test_inv_001_concurrent_setup_logger_sinks` | PENDING |
| INV-002 | — | `test_inv_002_elapsed_time_non_negative` | PENDING |
| INV-003 | — | `test_inv_003_exception_propagates_unchanged` | PENDING |
| EDGE-001 | — | `test_edge_001_log_file_parent_created` | PENDING |
| EDGE-002 | — | `test_edge_002_logged_no_args` | PENDING |
| EDGE-003 | — | `test_edge_003_logged_nonexistent_setting` | PENDING |
| EDGE-004 | — | `test_edge_004_logged_class_no_public_methods` | PENDING |
| NFR-004 | — | `test_nfr_004_backward_compatible_api` | PENDING |
