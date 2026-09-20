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

## Phase 5 — Verify

ISSUE Phase 5 gate: reproduction test GREEN (no hang) + full regression suite with no new failures + lint clean + type checks reported + traceability matrix updated.

### 1. Reproduction test (GREEN, no hang)

- command: `uv run pytest tests/acceptance/sessionmanagement/test_observability.py::test_ac_045_traced_methods_no_tokens_in_logs -v` (run under a 180 s timeout guard)
- result: **1 passed in 0.25 s** — no hang; completes in a fraction of the guard budget.

### 2. Full regression suite (no new failures)

- command: `uv run pytest tests/ -q -p no:randomly` (600 s timeout guard)
- result: **557 passed, 1 skipped, 0 failed** in 161.34 s (0:02:41).
- Classification: zero failures — no pre-existing failures and no regressions to classify. The single skip is environmental and pre-existing: `tests/acceptance/filemanagement/test_filemanagement.py:364` — "symlinks not available on this host" (legitimate environment skip, unrelated to this change).
- The AC-045 reproduction test was included in the full-suite run (no deselect exists in `pyproject.toml`/`conftest.py`) and passed.

### 3. Lint

- command: `uv run ruff check .`
- result: **All checks passed!** (clean)

### 4. Type checks

- command: `uv run mypy src/`
- result: **Success: no issues found in 56 source files** (clean; no pre-existing mypy errors — this change touched no `src/` file).

### 5. Traceability matrix update

- `docs/verification/traceability.md`:
  - "Issue: hanging-observability-test (reproduction test)" section: all six affected-ID rows updated from `RED (hang)` to `GREEN (Phase 5, 2026-09-20; was RED/hang)`, with the Phase 5 evidence (reproduction test GREEN under timeout guard; full regression suite 557 passed / 1 skipped / 0 failed; no new failures) recorded in the section intro.
  - Session Management Matrix note: the stale "known hanging test … deselected in full-suite runs" note corrected — the hang is fixed by this issue (root cause: infinite loop in the test's own assertion loop; fix commit `fe35f82`, test-side only) and GREEN re-confirmed in Phase 5; the AC-045 row remains GREEN.

### Gate result

| Check | Result |
|-------|--------|
| Reproduction test GREEN (no hang) | PASS (1 passed in 0.25 s, 180 s guard) |
| Full regression suite — no NEW failures | PASS (557 passed, 1 skipped (environmental, pre-existing), 0 failed) |
| Lint (`uv run ruff check .`) | PASS (clean) |
| Type checks (`uv run mypy src/`) | PASS (clean, 56 source files) |
| Traceability matrix updated | PASS (`docs/verification/traceability.md`) |

**ISSUE Phase 5 gate: SATISFIED.**

- timestamp: 2026-09-20 13:48 (local)
- branch: `issue/hanging-observability-test`

## Phase 6 — Review

ISSUE Phase 6 gate: review the change against its normative basis (the triage record + affected spec IDs), confirm no test was weakened/deleted, no `src/` change, feature boundaries/architecture respected, traceability intact, and no behavior introduced beyond the affected spec IDs. The review report is CLEAN if all checks pass.

### Scope reviewed

- Diff: `git diff 51b530a..HEAD` (branch `issue/hanging-observability-test`, 5 commits ahead of `main` at `51b530a`):
  - `tests/acceptance/sessionmanagement/test_observability.py` (+13/−5, single hunk: the AC-045 assertion loop)
  - `docs/verification/hanging-observability-test.md` (triage + RED/GREEN + Phase 5 evidence)
  - `docs/verification/traceability.md` (issue section + session-management matrix note)
  - `docs/workflow/PROBLEMS.md` (P-21 entry)
- Normative basis: this triage record + affected spec IDs (session-management AC-045/REQ-022, AC-044/REQ-021, NFR-004; logging REQ-001/AC-001, NFR-001, NFR-002).

### Findings

| # | Check | Result | Evidence / resolution |
|---|-------|--------|----------------------|
| 1 | **Normative basis (ISSUE)** — fix consistent with the triage record; no behavior beyond the affected spec IDs | PASS | The triage record mandates a **test-side fix** that preserves `enqueue=True` (logging REQ-001/AC-001) and requires no escalation. The applied fix is test-side only (single hunk in the failing test; `enqueue=True` untouched in `src/`). It introduces no behavior beyond the affected spec IDs: the asserted AC-045 behavior (entry/exit/exception records produced; no log record contains a raw token or token hash) is unchanged. Note: the triage record's initial root-cause analysis (queue deadlock) was corrected to the actual root cause (infinite loop in the test's own assertion loop; the queue block was a secondary effect) — the correction is logged as P-21 (`docs/workflow/PROBLEMS.md`) and reflected in the GREEN evidence section and the traceability note; the final fix is consistent with the corrected analysis. |
| 2 | **No test weakened/deleted** — asserted AC-045 behavior preserved | PASS | The test was not deleted (re-confirmed GREEN this review: `uv run pytest tests/acceptance/sessionmanagement/test_observability.py::test_ac_045_traced_methods_no_tokens_in_logs -v` → **1 passed in 0.24 s**, no hang). All assertions are still present and meaningful: per-record `token not in dumped`, `token_hash not in dumped`, `"bogus-token" not in dumped`, `bogus_hash not in dumped`; plus `token not in joined`, `token_hash not in joined`, `"bogus-token" not in joined`. The fix computes `hash_token(token)` / `hash_token("bogus-token")` **once** before the loop and iterates over a **snapshot** `list(log_records)`. Semantic equivalence holds because `hash_token` is pure/deterministic (`hashlib.sha256(token.encode("utf-8")).hexdigest()` — `src/backend/authentication/tokens.py`), so a once-computed hash equals a per-record computation. The snapshot is taken **after** the two `hash_token` calls, so it includes their log records; the loop body performs no logging, so no records are missed. Coverage of the asserted behavior is therefore complete, not weakened. |
| 3 | **No `src/` change** — fix is test-side only | PASS | `git diff 51b530a..HEAD --stat`: only the test file + 3 docs files. `git diff 51b530a..HEAD -- tests/conftest.py` is empty (the prior failed subagent's uncommitted conftest reconfigure fix was removed; `tests/conftest.py` matches the committed version). No `src/` file was modified. |
| 4 | **Feature boundaries / architecture** — confined to test + docs; no cross-feature imports; no architecture violation | PASS | The code change is a single hunk inside `tests/acceptance/sessionmanagement/test_observability.py` (the session-management test directory). No imports were added or changed (the test's existing imports are untouched). No `src/` change ⇒ no dependency/architecture change. No cross-feature internal imports introduced. |
| 5 | **Traceability** — every affected REQ/AC references the reproduction test as GREEN | PASS | `docs/verification/traceability.md` has an "Issue: hanging-observability-test (reproduction test)" section mapping all six affected IDs (session-management REQ-022/AC-045, REQ-021/AC-044, NFR-004; logging REQ-001/AC-001, NFR-001, NFR-002) to the reproduction test `test_ac_045_traced_methods_no_tokens_in_logs`, each **GREEN (Phase 5, 2026-09-20; was RED/hang)**, with the Phase 5 evidence (reproduction test GREEN under timeout guard; full regression suite 557 passed / 1 skipped (environmental, pre-existing) / 0 failed; no new failures) recorded in the section intro. The Session Management Matrix note was corrected (the stale "known hanging test … deselected" note replaced with the fix + GREEN re-confirmation). No orphaned tests, no missing traceability links. |
| 6 | **No behavior introduced** — fix is a test-side loop-termination fix; asserted behavior unchanged | PASS | No `src/` change ⇒ zero runtime behavior change. The test-side change only makes the assertion loop terminate (hashes computed once + snapshot iteration); the asserted AC-045 behavior is byte-for-byte the same set of assertions (modulo the once-computed deterministic hashes, which are semantically identical). No new behavior was introduced. |
| 7 | **Regression suite** (ISSUE: no new failures) | PASS | Phase 5: `uv run pytest tests/ -q -p no:randomly` → **557 passed, 1 skipped, 0 failed** (the skip is environmental and pre-existing: "symlinks not available on this host"); no new failures, no regression. Lint clean (`uv run ruff check .`), type checks clean (`uv run mypy src/`, 56 source files). |
| 8 | **Reusable shared capability → AGENTS.md note** | N/A | This is a test-side loop-termination fix, not a reusable shared capability — no AGENTS.md note required. |

### Gate result

| Check | Result |
|-------|--------|
| Normative basis (ISSUE) — fix consistent with triage record; no behavior beyond affected spec IDs | PASS |
| No test weakened/deleted — asserted AC-045 behavior preserved | PASS |
| No `src/` change — fix is test-side only | PASS |
| Feature boundaries / architecture respected | PASS |
| Traceability — all affected REQ/AC reference the reproduction test as GREEN | PASS |
| No behavior introduced | PASS |
| Regression suite — no new failures | PASS |

**ISSUE Phase 6 review report: CLEAN.**

- timestamp: 2026-09-20 (local)
- branch: `issue/hanging-observability-test`
