# Spec: Structlog logging pipeline (structlog-logging)

## Changelog
- v1 (2026-10-04): Draft (Phase P, P.4). CROSS-CUTTING. Supersedes the logging-backend choice recorded in ADR-002 and amends `docs/specs/logging.md` (v3), `docs/specs/logging-coverage.md` (v2), `docs/specs/settings-coverage.md` (v2) and `docs/specs/settings.md` (v4).

## 1. Overview & Objectives
- **Feature Name:** structlog-logging
- **Target Component:** `src/backend/logging/` (owner) plus the direct log statements in `src/backend/settings/registry.py`, `src/backend/settings/repository.py`, `src/backend/eventbus/eventbus.py`, `src/backend/permissions/service.py`, and the project guidance files listed in REQ-014.
- **Change Type:** CROSS-CUTTING — one new shared capability (the record pipeline) intentionally spans four features (logging, settings, event bus, permissions) plus the tooling and guidance records.
- **Goal:** Replace the third-party logging backend used by the shared logging feature with a processor/renderer pipeline built on the standard library's logging handler machinery, so that (a) the guidance the repository publishes about logging is true of the code it publishes, (b) the sinks are ordinary standard-library handlers that any third-party library, tool or test can attach to, (c) records are structured (key/value) where a machine reads them and human-readable where a human reads them, and (d) the one-off log statements in other features go through one exported entry point instead of importing a backend themselves.
- **Objectives:**
  1. One logging entry point for feature code: `get_logger()` from the shared logging feature.
  2. Two managed sinks with the same configuration surface as today (console + rotating file), expressed as standard-library handlers.
  3. Structured (JSON) records in the file sink, human-readable colorized records on the console.
  4. The tracing decorators (`@logged`, `@logged_class`) keep their observable record contract (entry / exit-with-elapsed / exception) after being rebuilt on the pipeline's own binding machinery.
  5. Third-party records emitted through the standard library still reach the same two sinks with correct level and originating location.
- **Out of scope (explicit boundaries):**
  - No new settings keys. The five `logging.*` keys (`log_level`, `log_file`, `log_max_bytes`, `log_backup_count`, `profiling_include_arguments`) and their defaults are unchanged.
  - No new sink, no network/syslog sink, no log shipping, no log aggregation deployment, no retention policy change.
  - No claim of a present consumer of structured records: `src/frontend/` is empty, there is no HTTP layer, and nothing in `src/` parses log output. Structured file records are justified as future-proofing for the machine-driven surface the `api-keys` change would create and for later log aggregation — the spec does not assert a consumer exists today.
  - No change to what is logged (the observability policy of `docs/specs/logging-coverage.md` stays; only *how* a statement is written changes).
  - No change to the settings feature's own behavior (only its log statements and the spec wording that names a backend).
  - No deprecation shim or compatibility alias for the removed decorator parameters (the break is stated in REQ-015), and no compatibility layer for the removed backend.

## 2. Architecture & Design Decisions
- **Design Pattern:** Feature module with a `setup_logger()` entry point that owns exactly two standard-library handlers on a dedicated, non-propagating logger; a processor/renderer layer formats records for each sink; third-party records are forwarded into those handlers; the tracing decorators bind call metadata (elapsed time, arguments, exception) onto the pipeline's own bound logger.
- **Dependencies:** `structlog` (new — the processor/renderer and binding layer over standard-library handlers, **not** a logging backend), `orjson` (already declared in `pyproject.toml` and currently unused; becomes the JSON serializer of the file sink, which retires its unused-dependency suppression), standard library `logging` (handler, formatter, queue and rotation machinery). `loguru` is removed from the dependency set. Decision: ADR-082 (supersedes ADR-002; absorbs the loguru wording of ADR-035 and ADR-060).
- **Constraints:**
  - Importable without application wiring; `setup_logger()` stays idempotent and thread-safe (ADR-035 unchanged).
  - No record may contain local variable values, passwords or tokens (NFR-003, unchanged policy).
  - The logging feature must never touch handlers, levels or loggers it does not own (INV-004).
  - Windows is a first-class runtime (rotation while a handle is open, `pytest-xdist` on CI).
- **Design Decisions:**
  - **D1 — Handler ownership.** A dedicated, non-propagating logger owns the console handler and the rotating file handler. Third-party reconfiguration of the root logger (alembic's `migrations/env.py` calls `logging.config.fileConfig`) can therefore never remove or replace the two managed handlers (EDGE-003).
  - **D2 — Interception by forwarding, not by re-emitting.** A single forwarding handler installed on the root logger passes foreign records to the two managed handlers, so the record's own level, logger name and location survive; no call-depth arithmetic is needed (this is what replaces the deleted `AC-005`/`EDGE-005` of `docs/specs/logging.md`).
  - **D3 — Renderer per sink.** Console: human-readable, colorized text. File: JSON objects serialized with `orjson`. `setup_logger(renderer=...)` can override the pair (REQ-006). The spec fixes the **record fields**, never the format string (the format string is an implementation detail).
  - **D4 — Asynchronous file writes.** The file handler is fed through a queue handler with a single listener thread, replacing the backend's built-in enqueueing (REQ-010).
  - **D5 — One statement entry point.** `get_logger()` is the only supported way to obtain a logger for one-off statements; features stop importing a backend directly (REQ-005). This retires the "direct backend statements are kept" policy recorded in `docs/specs/logging-coverage.md` REQ-010/AC-010.
  - **D6 — Breaking surface, no shim.** `context_getter` and `depth` are removed (they existed to work around the old backend's frame arithmetic); `renderer` is added to `setup_logger()`; `get_logger()` is added. The version bump is `major` (Q-22).

## 3. Data Structures & API Schemas

```python
# Public API of the shared logging feature after this change (backend.logging).
# The library names below are the implementation-level types; the normative
# statements in §4-§8 are written in capability terms.

def setup_logger(*, renderer: str | None = None) -> None:
    """Install the two managed sinks (idempotent, thread-safe).

    renderer: "text" | "json" | None. None (default) = text console + JSON file.
    Raises ValueError for an unknown renderer value, before any handler is installed.
    """

def get_logger(name: str | None = None) -> BoundLogger:
    """Return the logger feature code uses for one-off statements.

    The returned logger exposes debug/info/warning/error/exception and accepts
    keyword fields in addition to the message.
    """

def logged(
    func: Callable | None = None,
    *,
    level: str = "DEBUG",
    slow_threshold_ms: float | None = None,
    slow_threshold_setting: str | None = None,
    include_args: bool = False,
) -> Callable:
    """Trace entry / exit-with-elapsed / exception. `context_getter` and `depth` are removed."""

def logged_class(
    cls: type | None = None,
    *,
    slow_threshold_ms: float | None = None,
    include_args: bool = False,
) -> type: ...

# Unchanged exports: Settings, get_settings, register_settings, _read_setting.
```

Record fields (the file sink serializes these as JSON object members; the console sink renders the same information as text):

| Field | Meaning | Present on |
|---|---|---|
| `level` | Level name of the record | every record |
| `logger` | Logger name the record was emitted through | every record |
| `event` | The message | every record |
| `timestamp` | ISO-8601 UTC timestamp | every record |
| `elapsed_ms` | Call duration in milliseconds | traced exit records (REQ-011) |
| `file`, `line` | Originating source file and line | every record, including forwarded third-party records |
| `exception` | Exception type, message and traceback **frames** (never local values) | exception records (REQ-009) |

Public API surface (REQ-015): `setup_logger`, `logged`, `logged_class`, `get_logger`, `Settings`, `get_settings`, `register_settings`, `_read_setting`. Removed from the decorator surface: `context_getter`, `depth`. Added: `get_logger`, `setup_logger(renderer=...)`.

## 4. Requirements

| ID | Requirement |
|----|-------------|
| REQ-001 | The shared logging feature renders and emits records through the standard library's logging handler machinery with a processor/renderer layer; no third-party logging backend is used, and no module under `src/` or `tests/` imports one. |
| REQ-002 | `setup_logger()` installs exactly two managed sinks: a console sink on standard error writing colorized human-readable text, and a rotating file sink (UTF-8, JSON records, rotation size = `log_max_bytes`, backup count = `log_backup_count`). |
| REQ-003 | The two managed handlers are owned by a dedicated, non-propagating logger; the logging feature never attaches, removes or reconfigures a handler, level or logger that it does not own. |
| REQ-004 | Records emitted through the standard library by third-party loggers reach the same two managed sinks with the correct level, logger name, message and originating file and line. |
| REQ-005 | The feature exports `get_logger()`; it is the only supported way for feature code to obtain a logger for one-off statements, and every direct backend statement in `src/backend/settings/registry.py` (17), `src/backend/settings/repository.py` (11), `src/backend/eventbus/eventbus.py` (10) and `src/backend/permissions/service.py` (1) is migrated to it. |
| REQ-006 | `setup_logger()` accepts an optional keyword-only `renderer` parameter (`"text"`, `"json"`, or `None`); called with no argument it stays settings-driven and uses the default renderer pair (text console, JSON file). |
| REQ-007 | `@logged` traces synchronous and asynchronous calls — entry, exit with elapsed milliseconds, exception — through the pipeline's bound-logger machinery; its parameters are `level`, `slow_threshold_ms`, `slow_threshold_setting` and `include_args`; `context_getter` and `depth` are removed. |
| REQ-008 | `@logged_class` traces the public methods of a class with the same records, skips private methods, marks the class as traced and exposes the resolved slow-call threshold. |
| REQ-009 | An exception record carries the exception type, its message and the traceback frames, and never the values of local variables. |
| REQ-010 | The file sink is fed through a queue: a traced or logged call never blocks on file I/O, and a failing or blocked file sink never interrupts, delays unboundedly, or fails that call. |
| REQ-011 | Every record carries the level, the logger name, the message and a timestamp; a traced exit record additionally carries the elapsed milliseconds; every record carries the originating file and line. |
| REQ-012 | A change to any `logging.*` setting reconfigures the feature's own handlers in place, re-applying all current `logging.*` values, without restarting the process. |
| REQ-013 | The dependency set changes: `structlog` is added, `loguru` is removed, and `orjson` becomes used by the file renderer so that its unused-dependency suppression is removed. |
| REQ-014 | The project guidance that names the removed backend is corrected to the shared logging feature's own entry points in `AGENTS.md`, `.agents/skills/python-best-practices/SKILL.md`, `.agents/skills/python-best-practices/references/modern-python.md` and `.agents/skills/python-best-practices/references/errors-and-resources.md`. |
| REQ-015 | The feature's public API is exactly the set listed in §3; the change to the decorator parameter set is breaking, no compatibility shim is provided, and the version bump is `major`. |

### Amended requirements in approved specs (this change's amendment PR)

These IDs are restated in the amendment PR (see §10 Impact Analysis); they are listed here so the change is traceable end to end, and their normative text lives in the amended specs:

| Spec | ID | Amendment |
|---|---|---|
| `logging.md` | REQ-001 | Restated in capability terms (no backend named); sinks are standard-library handlers, file records are JSON. |
| `logging.md` | REQ-003 | Restated: foreign records emitted through the standard library are forwarded to the two managed sinks; no frame-skipping requirement. |
| `logging.md` | REQ-005 | Parameter list reduced to `level`, `slow_threshold_ms`, `slow_threshold_setting`, `include_args`. |
| `logging.md` | AC-001 | Restated to the two standard-library sinks and their record formats. |
| `logging.md` | AC-004 | Restated: forwarded third-party records reach both managed sinks with correct level, logger name, message, file and line. |
| `logging.md` | AC-005 | **Deleted** (the importlib bootstrap-frame rule only exists to serve the removed backend's frame arithmetic). |
| `logging.md` | INV-001 | Restated: exactly one console handler and one file handler are owned by the feature logger. |
| `logging.md` | EDGE-005 | **Deleted**; the unknown-level case is restated as `EDGE-004` of this spec in capability terms. |
| `logging.md` | NFR-001, NFR-002, NFR-003 | Re-measured budgets and capability wording (see §9). |
| `logging-coverage.md` | REQ-010, AC-010 | Restated: one-off statements are kept as statements, but written through the logging feature's exported logger instead of a directly imported backend. |
| `settings-coverage.md` | REQ-014, REQ-015, REQ-016, AC-019, AC-020, AC-021, EDGE-008 | Restated: `setup_logger()` stays callable with no arguments (the new `renderer` parameter is optional and keyword-only), live reconfiguration mutates the managed handlers, and the rotation case re-applies all current values. |
| `settings.md` | Scope, Dependencies, observability wording | Wording only: the settings feature uses the shared logging feature's logger, not a named backend. No ID change. |

## 5. Acceptance Criteria

| ID | Requirement | Given / When / Then |
|----|-------------|---------------------|
| AC-001 | REQ-001 | **Given** the repository after the swap, **When** `src/` and `tests/` are searched for an import of the removed logging backend, **Then** there is no match, **And** a record emitted by the feature passes through the standard-library handler chain (a handler attached to the feature logger observes it). |
| AC-002 | REQ-002 | **Given** a fresh process, **When** `setup_logger()` is called, **Then** the feature logger owns exactly two handlers, **And** one writes colorized text to standard error, **And** the other is a rotating file handler with the configured rotation size, backup count and UTF-8 encoding. |
| AC-003 | REQ-002 | **Given** the file sink, **When** a traced call completes, **Then** the file record parses as a JSON object containing `level`, `logger`, `event`, `timestamp`, `elapsed_ms`, `file` and `line`. |
| AC-004 | REQ-003 | **Given** a handler attached to the root logger and to another feature's logger, **When** `setup_logger()` runs and a `logging.*` setting changes, **Then** both foreign handlers are still attached and unmodified. |
| AC-005 | REQ-003 | **Given** the feature logger, **When** it emits one record, **Then** the record appears exactly once in each managed sink (the feature logger does not propagate). |
| AC-006 | REQ-004 | **Given** a third-party logger with no handlers of its own, **When** it emits a record at or above the configured level, **Then** the record reaches both managed sinks with its original level and message. |
| AC-007 | REQ-004 | **Given** the same forwarded record, **When** the file record is read, **Then** `file` and `line` name the emitting source location, not the logging feature's own code. |
| AC-008 | REQ-005 | **Given** `get_logger("x")`, **When** a level method is called with a message and keyword fields, **Then** one record reaches each managed sink carrying the message and the fields. |
| AC-009 | REQ-005 | **Given** the four named files, **When** the change is implemented, **Then** none of them imports a logging backend, **And** each of the 39 one-off statements is written through `get_logger()`. |
| AC-010 | REQ-006 | **Given** `setup_logger(renderer="json")`, **When** a record is emitted, **Then** the console record is a JSON object; **Given** `setup_logger(renderer="text")`, **Then** the file record is human-readable text; **Given** `setup_logger()`, **Then** the console record is text and the file record is JSON. |
| AC-011 | REQ-007 | **Given** a traced synchronous function and a traced `async` function, **When** each is called, **Then** an entry record and an exit record carrying `elapsed_ms` are emitted at the configured level. |
| AC-012 | REQ-007 | **Given** a traced function that raises, **When** it is called, **Then** an exception record carrying the exception type and message is emitted, **And** the exception propagates unchanged. |
| AC-013 | REQ-007 | **Given** `@logged(context_getter=...)` or `@logged(depth=1)`, **When** it is applied, **Then** a `TypeError` is raised; **And** `level`, `slow_threshold_ms`, `slow_threshold_setting` and `include_args` behave as before the change. |
| AC-014 | REQ-008 | **Given** a class decorated with `@logged_class`, **When** a public method is called, **Then** entry and exit records with `elapsed_ms` are emitted; **When** a private method is called, **Then** no records are emitted; **And** the class carries the traced marker and the resolved threshold. |
| AC-015 | REQ-009 | **Given** a traced function that raises while holding a secret local value, **When** the exception record is written to the file sink, **Then** the record contains the exception type, message and traceback frames, **And** the secret value appears in no record. |
| AC-016 | REQ-010 | **Given** the file sink pointed at an unwritable path or a stopped listener, **When** a traced call runs, **Then** the call returns its normal result and no exception escapes from logging. |
| AC-017 | REQ-012 | **Given** a running process, **When** `set_value("logging.log_level", "DEBUG")` and then `set_value("logging.log_max_bytes", ...)` are called, **Then** DEBUG records reach both sinks without a restart, **And** the rotation parameters are re-applied, **And** only the feature's own handlers change. |
| AC-018 | REQ-013 | **Given** the implemented change, **When** the dependency check runs, **Then** it reports no unused and no missing dependency, **And** the removed backend is absent from the dependency set, **And** the JSON serializer is used. |
| AC-019 | REQ-014 | **Given** the four guidance files, **When** the change is implemented, **Then** none names the removed backend, **And** each names the shared logging feature's own entry points (`setup_logger`, `logged`, `logged_class`, `get_logger`). |
| AC-020 | REQ-015 | **Given** `backend.logging`, **When** its public exports are inspected, **Then** they are exactly the set in §3, **And** importing `context_getter`/`depth`-style parameters or a backend module through the feature fails. |

## 6. Invariants

| ID | Invariant |
|----|-----------|
| INV-001 | For any number of concurrent `setup_logger()` calls, the feature logger owns exactly one console handler and one file handler. |
| INV-002 | For any traced function and any value held in a local variable, no emitted record contains that value. |
| INV-003 | For any traced synchronous or asynchronous call, the `elapsed_ms` of the exit record is non-negative. |
| INV-004 | For any logging-feature operation (setup, reconfigure, renderer change), the handler set, level and disabled state of every logger other than the feature's own logger are unchanged, except for the single forwarding handler the feature installs on the root logger. |
| INV-005 | Every record emitted through the pipeline carries the fields required by REQ-011. |

## 7. Edge Cases

| ID | Edge Case | Expected Behavior |
|----|-----------|-------------------|
| EDGE-001 | `log_file` path whose parent directory does not exist | The parent directory is created (unchanged from `logging.md` EDGE-001). |
| EDGE-002 | Rotation is triggered while the file handle is open (Windows runtime; `pytest-xdist` workers on CI) | Rotation happens without an exception escaping to the emitting call; the record is not lost silently. |
| EDGE-003 | A third party reconfigures the root logger — `migrations/env.py` calls `logging.config.fileConfig` (alembic), which replaces the root handler list and disables pre-existing non-root loggers | The two managed handlers survive on the feature logger and no foreign handler is modified; the feature re-enables its own logger and re-installs the forwarding handler at the next logging reconfigure; records emitted between the third-party call and that reconfigure are not captured (documented, not silently "fixed"). The autouse `tests/conftest.py::_stdlib_root_logging_restored` fixture stays as the test-suite guard. |
| EDGE-004 | A standard-library record whose level is a non-standard numeric level | The record reaches both sinks with the numeric level preserved (capability restatement of the deleted `logging.md` EDGE-005). |
| EDGE-005 | `setup_logger(renderer="yaml")` (unknown value) | `ValueError` is raised before any handler is installed; the previous sink configuration is left intact. |
| EDGE-006 | `get_logger()` is used before `setup_logger()` has been called | No exception; the record is emitted through the standard library's default handling and is not routed to the managed sinks (the setup requirement is unchanged: setup happens once in the entrypoint before feature code runs). |

## 8. Non-Functional Requirements

| ID | Category | Requirement |
|----|----------|-------------|
| NFR-001 | Performance | `setup_logger()` completes in **< 25 ms** (median of 3 fresh processes, same gate shape as the existing contract test). Re-measured for this pipeline: **0.85 ms median** (min 0.84, max 0.87, n = 5 fresh processes, Windows 11 / Python 3.14.5 / 32 CPU, INFO level, console + queue + rotating file + root forwarding handler + listener started). Amends `logging.md` NFR-001 (was < 50 ms, measured 5.18 ms median for the removed backend on the same machine; CI observed 15.55 ms for that backend, a ~3× penalty that keeps ~10× headroom at 25 ms). |
| NFR-002 | Performance | `@logged` overhead per call is **< 1 ms measured with the two managed sinks active at DEBUG** — the context the observability policy actually requires. Re-measured for this pipeline: **0.148 ms/call** with console + queue + rotating file active at DEBUG (n = 3, same machine), and **0.006 ms/call** for the tracing machinery alone with no handler attached. Amends `logging.md` NFR-002, whose budget was only ever measured with logging disabled (removed backend: 0.156 ms/call with sinks active, 0.023 ms/call disabled). |
| NFR-003 | Security | No record may contain local variable values: an exception record carries the exception type, message and traceback frames only. Passwords, tokens and file content never appear in a record; `include_args` semantics are unchanged (`False` by default, secret-handling methods keep it `False`). |
| NFR-004 | Dependency | The dependency check reports no unused and no missing dependency after the swap: `structlog` used, `loguru` absent, `orjson` used (its unused-dependency suppression removed). |
| NFR-005 | Concurrency | The pipeline adds at most one runtime thread (the file-sink listener); no per-call thread, no busy wait, no sleep in any test. |

## 9. Observability & Logging (of this change itself)

| Event | Level | Message / fields |
|---|---|---|
| Logging pipeline installed / reconfigured | INFO | `logging configured` — level, file, rotation size, renderer |
| Feature-level one-off statements (settings registry, repositories, event bus, permissions) | DEBUG/INFO/WARNING as today | through `get_logger()`, message + keyword fields, unchanged wording |
| Traced call entry / exit / exception | DEBUG / WARNING (slow) / as configured | unchanged record contract (REQ-007, REQ-009) |

## 10. Impact Analysis (CROSS-CUTTING)

| # | Affected feature / area | What changes there | Touched IDs of that feature |
|---|---|---|---|
| 1 | `backend.logging` (owner) | Backend swap; two standard-library managed sinks; dedicated non-propagating logger; forwarding interception; `get_logger()`; `renderer` parameter; decorators rebuilt; `context_getter`/`depth` removed. | New REQ-001…REQ-012, AC-001…AC-013, INV-001…INV-005, EDGE-001…EDGE-006, NFR-001…NFR-005. Amended in `logging.md`: REQ-001, REQ-003, REQ-005, AC-001, AC-004, AC-005 (deleted), INV-001, EDGE-005 (deleted), NFR-001, NFR-002, NFR-003. Amended in `logging-coverage.md`: REQ-010, AC-010. |
| 2 | `backend.settings` | 28 direct statements (registry 17, repository 11) migrate to `get_logger()`; live reconfiguration mutates the managed handlers instead of replacing sinks. | Amended in `settings-coverage.md`: REQ-014, REQ-015, REQ-016, AC-019, AC-020, AC-021, EDGE-008. Wording-only in `settings.md`: Scope row, Dependencies row, observability paragraph (no ID change). |
| 3 | `backend.eventbus` | 10 direct statements migrate to `get_logger()`. No spec ID change — `docs/specs/event-bus.md` names no backend. | none |
| 4 | `backend.permissions` | 1 direct statement migrates to `get_logger()`. No spec ID change. | none |
| 5 | `migrations` / alembic | No code change. The `fileConfig` interaction becomes EDGE-003; the autouse root-logging fixture in `tests/conftest.py` stays. | none (new EDGE-003 in this spec) |
| 6 | Tooling (`pyproject.toml`) | `structlog` added, `loguru` removed, `orjson` becomes used and its unused-dependency suppression is deleted. | REQ-013, AC-018, NFR-004 |
| 7 | Guidance (`AGENTS.md`, 3 skill reference files) | Corrected to the feature's own entry points. | REQ-014, AC-019 |
| 8 | Test suite | Tests re-derived from the amended IDs; `tests/acceptance/logging_coverage/test_direct_loguru_kept.py` is deleted (it exists solely to enforce the retired REQ-010 wording); `tests/logging_test_helpers.py`, `tests/logging_coverage_test_helpers.py`, `tests/settings_test_helpers.py` and `tests/conftest.py` are adapted to the new backend; the NFR contract gates are re-measured. No test is weakened. | AC-001…AC-020 (test strategy §11) |

**Sequencing (binding):** the amendment PR (4 specs + ADR-082 + ADR-002 status) merges **first**; the implementation PR follows. This change lands **after** `pyproject-tooling-gaps` (which owns `[tool.deptry]` and `quality_check`) and **before** `api-keys` and `notifications` implement; it clears `tenacity-rich-cachetools`'s `Depends on: decision on docs/todo/structlog-logging.md`.

## 11. Test Strategy

| ID | Test Category | Test File | Test Function |
|----|---------------|-----------|---------------|
| AC-001 | acceptance | `tests/acceptance/logging/test_pipeline_backend.py` | `test_ac_001_no_backend_import_and_stdlib_chain` |
| AC-002 | acceptance | `tests/acceptance/logging/test_pipeline_backend.py` | `test_ac_002_two_managed_handlers` |
| AC-003 | acceptance | `tests/acceptance/logging/test_pipeline_backend.py` | `test_ac_003_file_record_fields_as_json` |
| AC-004 | unit | `tests/unit/logging/test_sink_ownership.py` | `test_ac_004_foreign_handlers_untouched` |
| AC-005 | unit | `tests/unit/logging/test_sink_ownership.py` | `test_ac_005_no_duplicate_records` |
| AC-006 | acceptance | `tests/acceptance/logging/test_third_party_records.py` | `test_ac_006_third_party_reaches_both_sinks` |
| AC-007 | unit | `tests/unit/logging/test_third_party_records.py` | `test_ac_007_location_of_emitting_call` |
| AC-008 | acceptance | `tests/acceptance/logging/test_get_logger.py` | `test_ac_008_get_logger_emits_to_sinks` |
| AC-009 | acceptance | `tests/acceptance/logging_coverage/test_statements_via_feature.py` | `test_ac_009_statements_go_through_get_logger` |
| AC-010 | acceptance | `tests/acceptance/logging/test_renderer.py` | `test_ac_010_renderer_selection` |
| AC-011 | acceptance | `tests/acceptance/logging/test_tracing_records.py` | `test_ac_011_sync_and_async_traced_records` |
| AC-012 | acceptance | `tests/acceptance/logging/test_tracing_records.py` | `test_ac_012_exception_record_and_propagation` |
| AC-013 | contract | `tests/contract/logging/test_tracing_surface.py` | `test_ac_013_removed_parameters` |
| AC-014 | acceptance | `tests/acceptance/logging/test_tracing_records.py` | `test_ac_014_logged_class_records` |
| AC-015 | acceptance | `tests/acceptance/logging/test_secrets.py` | `test_ac_015_no_local_values_in_exception_record` |
| AC-016 | acceptance | `tests/acceptance/logging_coverage/test_sink_failure.py` | `test_ac_016_call_unaffected_by_failing_file_sink` |
| AC-017 | acceptance | `tests/acceptance/settings_coverage/test_setup_logger.py` | `test_ac_017_live_reconfigure` |
| AC-018 | contract | `tests/contract/logging/test_dependency_contract.py` | `test_ac_018_dependency_report_clean` |
| AC-019 | contract | `tests/contract/logging/test_dependency_contract.py` | `test_ac_019_guidance_names_feature_entry_points` |
| AC-020 | contract | `tests/contract/logging/test_tracing_surface.py` | `test_ac_020_public_export_surface` |
| INV-001 | property | `tests/property/logging/test_pipeline_invariants.py` | `test_inv_001_concurrent_setup_owns_two_handlers` |
| INV-002 | property | `tests/property/logging/test_pipeline_invariants.py` | `test_inv_002_no_local_value_ever_recorded` |
| INV-003 | property | `tests/property/logging/test_pipeline_invariants.py` | `test_inv_003_elapsed_non_negative` |
| INV-004 | property | `tests/property/logging/test_pipeline_invariants.py` | `test_inv_004_other_loggers_untouched` |
| INV-005 | property | `tests/property/logging/test_pipeline_invariants.py` | `test_inv_005_required_fields_present` |
| EDGE-001 | unit | `tests/unit/logging/test_pipeline_edges.py` | `test_edge_001_log_file_parent_created` |
| EDGE-002 | unit | `tests/unit/logging/test_pipeline_edges.py` | `test_edge_002_rotation_with_open_handle` |
| EDGE-003 | integration | `tests/integration/logging/test_external_reconfiguration.py` | `test_edge_003_file_config_keeps_managed_handlers` |
| EDGE-004 | unit | `tests/unit/logging/test_pipeline_edges.py` | `test_edge_004_unknown_numeric_level` |
| EDGE-005 | unit | `tests/unit/logging/test_pipeline_edges.py` | `test_edge_005_unknown_renderer` |
| EDGE-006 | unit | `tests/unit/logging/test_pipeline_edges.py` | `test_edge_006_get_logger_before_setup` |
| NFR-001 | contract | `tests/contract/logging/test_logging_contracts.py` | `test_nfr_001_setup_time_budget` (amended budget) |
| NFR-002 | contract | `tests/contract/logging/test_logging_contracts.py` | `test_nfr_002_decorator_overhead_budget` (amended: sinks active at DEBUG, no backend-specific disable/enable) |
| NFR-003 | property | `tests/property/logging/test_pipeline_invariants.py` | `test_inv_002_no_local_value_ever_recorded` (same witness as INV-002) |
| NFR-004 | contract | `tests/contract/logging/test_dependency_contract.py` | `test_ac_018_dependency_report_clean` |
| NFR-005 | unit | `tests/unit/logging/test_pipeline_edges.py` | `test_nfr_005_single_listener_thread` |

Amended and deleted IDs from the approved specs (existing tests re-derived from the amended wording, named in those specs' own test strategies):

| ID (approved spec) | Test Category | Test File | Test Function |
|---|---|---|---|
| `logging.md` AC-001 | acceptance | `tests/acceptance/logging/test_logging.py` | `test_ac_001_setup_logger_adds_sinks` (re-derived) |
| `logging.md` AC-004 | unit | `tests/unit/logging/test_logging.py` | `test_ac_004_intercept_handler_routes_records` (re-derived as the forwarding-handler case) |
| `logging.md` REQ-005 | contract | `tests/contract/logging/test_logging_contracts.py` | `test_nfr_004_backward_compatible_api` (amended: asserts the reduced parameter set) |
| `logging.md` INV-001 | property | `tests/property/logging/test_logging_properties.py` | `test_inv_001_concurrent_setup_logger_sinks` (re-derived) |
| `logging.md` NFR-001 / NFR-002 | contract | `tests/contract/logging/test_logging_contracts.py` | `test_nfr_001_setup_time_budget`, `test_nfr_002_decorator_overhead_budget` (amended budgets) |
| `logging.md` AC-005 (**deleted**) | unit | `tests/unit/logging/test_logging.py` | `test_ac_005_intercept_handler_skips_bootstrap` (deleted; replaced by this spec's AC-007) |
| `logging.md` EDGE-005 (**deleted**) | unit | `tests/unit/logging/test_logging_edges.py` | `test_edge_005_intercept_unknown_level` (deleted; case survives as this spec's EDGE-004) |
| `logging-coverage.md` REQ-010 / AC-010 | acceptance | `tests/acceptance/logging_coverage/test_direct_loguru_kept.py` | `test_existing_direct_loguru_kept` (deleted; replaced by this spec's AC-009) |
| `settings-coverage.md` AC-019 | acceptance | `tests/acceptance/settings_coverage/test_setup_logger.py` | `test_setup_logger_reads_registry` (re-derived) |
| `settings-coverage.md` AC-020 | acceptance | `tests/acceptance/settings_coverage/test_setup_logger.py` | `test_sink_reconfigured_on_change` (re-derived) |
| `settings-coverage.md` AC-021 | unit | `tests/unit/test_settings_coverage.py` | `test_logging_stub_removed` (re-derived) |
| `settings-coverage.md` EDGE-008 | unit | `tests/unit/test_settings_coverage.py` | `test_sink_reconfigured_rotation` (re-derived) |
| `settings.md` §351 (no ID) | unit | `tests/unit/test_settings_coverage.py` | `test_observability_tracing` (re-derived) |

Deletions authorized by this change (each named in `docs/verification/structlog-logging.md`): the three tests marked **deleted** above — the sole enforcers of the retired `logging-coverage.md` REQ-010/AC-010 wording and of the deleted `logging.md` AC-005 / EDGE-005 frame arithmetic. No other test may be deleted or weakened.

## 12. Traceability

The matrix rows for this spec are added in `docs/verification/traceability.md` (§ *Structlog Logging Matrix*) with `PENDING` status; Phase 3 replaces them with the derived tests and the RED gate, Phase 5 with the GREEN evidence. Spec coverage for this change is 100% when every REQ-001…REQ-015 and AC-001…AC-020 above, and every amended ID in §4's amendment table, has a GREEN test.
