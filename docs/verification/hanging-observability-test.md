# ISSUE Triage: hanging-observability-test

## Type

**ISSUE** — a deviation from approved spec behavior (a defect). No new behavior is introduced.

## Affected Requirements

### From `docs/specs/session-management.md`

- **AC-045** (REQ-022): **Given** `SessionService`, **When** its methods are called, **Then** entry/exit/exception records are produced by `@logged_class` **and** no log record contains a raw token or token hash.
- **REQ-022**: Observability: `SessionService` is traced with `@logged_class` (`include_args=False`, `slow_threshold_ms=100`); the module functions (`register_settings`, `get_session_service`, `reset_session_service`) are traced with `@logged`.
- **AC-044** (REQ-021): **Given** any `SessionEntry`, log record, published event, or error message produced by this feature, **When** inspected, **Then** no raw session token or token hash appears (only session ids).
- **REQ-021**: Secrets: raw session tokens and token hashes never appear in list entries, log records, events, or error messages (only session ids).
- **NFR-004**: Observability — `SessionService` is traced with `@logged_class` (`include_args=False`, `slow_threshold_ms=100`; entry/exit/exception per public method); module functions are traced with `@logged`; lifecycle events are published to the injected publisher.

### From `docs/specs/logging.md`

- **REQ-001**: The logging feature provides a `setup_logger()` function that configures loguru with a console sink (stderr, colorized, backtrace enabled) and a rotating file sink (UTF-8, **enqueued**, backtrace enabled, `diagnose=False`).
- **AC-001** (REQ-001): **Given** a fresh Python environment, **When** `setup_logger()` is called, **Then** loguru has a console sink on stderr with colorize and backtrace enabled, **And** a rotating file sink with UTF-8 encoding, **enqueue**, backtrace, and `diagnose=False`.
- **NFR-001**: Performance — `setup_logger()` must complete in < 50 ms.
- **NFR-002**: Performance — `@logged` decorator overhead per call must be < 1 ms.

## Defect Confirmation

### Observed Behavior

- The AC-045 acceptance test `tests/acceptance/sessionmanagement/test_observability.py::test_ac_045_traced_methods_no_tokens_in_logs` **hangs and never finishes** (reproduced locally: `timeout 90 uv run pytest ...` → pytest exit 124 after 90 s).
- The hang is in a **loguru `enqueue=True` (queued) file handler** whose `multiprocessing.SimpleQueue` pipe deadlocks:
  - **Main thread**: `test_observability.py:87` (`session_service.list_sessions(token=...)`) → `src/backend/logging/_decorator.py:104` (`@logged` wrapper) → loguru `log` → `_log` → `emit` → `multiprocessing/queues.py:394 put` → `multiprocessing/connection.py:303 _send_bytes` (blocked writing to a pipe).
  - **`loguru-writer-2` thread**: `loguru/_handler.py:300 _queued_writer` → `queues.py:387 get` (waiting on the queue).
- The queued file handler is added by the **logging feature's `setup_logger`**: `src/backend/logging/_setup.py:85` (`"enqueue": True` in `_file_sink_options`) and `_setup.py:143` (`logger.add(str(log_file), **_file_sink_options(settings))`).
- The test's own `log_records` fixture (`tests/conftest.py`) only adds a plain function sink — so the queued handler comes from `setup_logger` (invoked by the session-scoped `_logging_session_setup` fixture in `tests/conftest.py`).

### Required Behavior (per cited spec IDs)

- Per **session-management AC-045 / REQ-022**: when `SessionService` methods are called, entry/exit/exception records are produced by `@logged_class` **and** no log record contains a raw token or token hash — i.e., the test must **complete and pass**.
- Per **logging NFR-002**: `@logged` decorator overhead per call must be < 1 ms — i.e., logging/tracing must **not block or hang**.
- Per **logging NFR-001**: `setup_logger()` must complete in < 50 ms — i.e., logging setup must **not block or hang**.

### Deviation

The observed behavior (the AC-045 test hangs and never finishes) deviates from the required behavior (the test must complete and pass; logging must not block/hang). The enqueued file handler (mandated by logging REQ-001/AC-001) deadlocks when a `@logged` method emits a record during the test, causing the test to hang.

## Reproduction Plan

### Failing Test

- `tests/acceptance/sessionmanagement/test_observability.py::test_ac_045_traced_methods_no_tokens_in_logs`
- Reproduce with: `timeout 90 uv run pytest tests/acceptance/sessionmanagement/test_observability.py::test_ac_045_traced_methods_no_tokens_in_logs -v` (exit 124 = hang).

### Fix Scope

- The fix is a **test-side fix**: the test must be set up so the enqueued file handler (mandated by logging REQ-001/AC-001) does not deadlock. The logging feature must **preserve `enqueue=True`** (per the logging spec), so the fix cannot remove `enqueue=True`.
- The test should be configured to avoid the deadlock (e.g., by reconfiguring logging to remove the file sink in the test context after `setup_logger` adds it, or by running the test in a subprocess so the enqueued file handler is in a separate process).
- The underlying loguru/Python-stdlib pipe behavior is not controllable by the logging feature (it only passes `enqueue=True` to loguru), so the fix cannot be in the logging feature without changing `enqueue=True`.

### Files Expected to Change

- `tests/acceptance/sessionmanagement/test_observability.py` (the failing test).
- Possibly `tests/conftest.py` (if the fix involves the `log_records` fixture or the session-scoped `_logging_session_setup` fixture).

## Escalation Check

- The fix must preserve `enqueue=True` (per logging REQ-001/AC-001). If the fix turns out to require **removing `enqueue=True`** or **changing the logging feature to not deadlock** (behavior the spec does not state), it must be **escalated** (Spec Amendment PR or reclassification per the Escalation Rules).
- Based on the current analysis, the fix is a **test-side fix** that does not require behavior the spec does not state. So **no escalation is needed** at this time.

## RED Evidence

Reproduction test: `tests/acceptance/sessionmanagement/test_observability.py::test_ac_045_traced_methods_no_tokens_in_logs` (already exists; not modified).

**RED for this issue = the test hangs (never finishes).** The defect is a deadlock, not a wrong assertion: the test does not fail — it never completes. RED was therefore re-confirmed by running the test under a 90 s timeout; exit 124 (timeout) is the observed RED signal.

### AC-045 (REQ-022) — reproduction test

RED:
  command: timeout 90 uv run pytest tests/acceptance/sessionmanagement/test_observability.py::test_ac_045_traced_methods_no_tokens_in_logs -v
  result: HANG — exit 124 after 90 s (test never completes)
  failure mode: hang (deadlock in the loguru `enqueue=True` file-sink `multiprocessing.SimpleQueue` pipe when a `@logged` method emits a record during the test) — not an assertion failure and not a setup error; the test contract sanity check passes because the hang is the spec-defined defect (logging must not block/hang: logging NFR-001/NFR-002)
  affected IDs covered by this reproduction test: session-management AC-045/REQ-022, AC-044/REQ-021, NFR-004; logging REQ-001/AC-001, NFR-001, NFR-002
  date: 2026-09-20
  commit: (this commit — `issue(hanging-observability-test): RED confirmed`)

GREEN:
  command: timeout 120 uv run pytest tests/acceptance/sessionmanagement/test_observability.py -v -p no:randomly
  result: 3 passed in 0.57 s (test_ac_044_no_tokens_in_outputs PASSED, test_ac_045_traced_methods_no_tokens_in_logs PASSED, test_nfr_004_traced_service_publishes_events PASSED) — no hang, completes well under the 60 s budget
  fix: test-side only — compute hash_token(token) / hash_token("bogus-token") once before the assertion loop and iterate over a snapshot (list(log_records)) so the @logged hash_token calls no longer grow the list while it is iterated (root cause: infinite loop in the test's own assertion loop, not a queue deadlock); removed the conftest `_reconfigure_file_sink_non_enqueued` reconfigure fix (secondary effect, deviates from the spec-mandated enqueue=True file sink, logging REQ-001/AC-001); asserted AC-045 behavior unchanged (no log record contains a raw token or token hash)
  date: 2026-09-20 13:22 (local)
  commit: (this commit — `issue(hanging-observability-test): fix infinite loop in AC-045 assertion loop (GREEN)`)

## GREEN Evidence (Phase 4 — minimal fix)

- command: `timeout 120 uv run pytest tests/acceptance/sessionmanagement/test_observability.py -v -p no:randomly`
- result: **3 passed in 0.57 s** — `test_ac_044_no_tokens_in_outputs` PASSED, `test_ac_045_traced_methods_no_tokens_in_logs` PASSED, `test_nfr_004_traced_service_publishes_events` PASSED (no hang; completes well under the 60 s budget)
- ruff: `uv run ruff check .` → All checks passed!
- timestamp: 2026-09-20 13:22 (local)
