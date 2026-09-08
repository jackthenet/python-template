# Verification — Logging-Coverage Feature

**Spec:** `docs/specs/logging-coverage.md`
**Branch:** `feature/logging-coverage`

---

## Phase 3 — RED Evidence

**Date:** 2026-09-08
**Command:** `uv run pytest tests/acceptance/logging_coverage/ tests/property/logging_coverage/ tests/unit/logging_coverage/ -v`

**Result: 26 failed, 0 passed, 0 errors** — the suite fails before implementation, and every
failure is an assertion failure (not a setup/collection/Hypothesis-health error).

Before implementation the inventory classes and module functions are not yet traced with the
enhanced decorators (no `__logged_class__` / `__logged__` markers, no concrete
`slow_threshold_ms` class attributes), the entrypoint (`src/main.py`) is empty (no
`setup_logger` call), and the traced-class docstrings do not mention tracing. The tests therefore
fail on their assertions:

- Inventory/tracing tests fail because the classes/functions carry no tracing markers.
- `test_entrypoint_calls_setup_logger_once` / `test_setup_logger_idempotent` fail because
  `src/main.py` contains no `setup_logger(` call (count is 0, not 1).
- `test_traced_class_docstrings_mention_tracing` fails because the not-yet-traced classes'
  docstrings do not mention tracing.
- Property tests fail because the untraced subjects produce no entry/exit records
  (`assert 0 == 1`).

### Test Inventory (26 tests, spec-derived)

| Category | File | Tests |
|---|---|---|
| Acceptance | `tests/acceptance/logging_coverage/test_inventory.py` | AC-001 |
| Acceptance | `tests/acceptance/logging_coverage/test_services_traced.py` | AC-002, AC-004, AC-005 |
| Acceptance | `tests/acceptance/logging_coverage/test_abc_traced.py` | AC-003 |
| Acceptance | `tests/acceptance/logging_coverage/test_secret_args.py` | AC-006, AC-015 |
| Acceptance | `tests/acceptance/logging_coverage/test_slow_threshold.py` | AC-007, AC-014 |
| Acceptance | `tests/acceptance/logging_coverage/test_levels.py` | AC-008 |
| Acceptance | `tests/acceptance/logging_coverage/test_docstrings.py` | AC-009 |
| Acceptance | `tests/acceptance/logging_coverage/test_direct_loguru_kept.py` | AC-010 |
| Acceptance | `tests/acceptance/logging_coverage/test_setup_logger.py` | AC-011 |
| Acceptance | `tests/acceptance/logging_coverage/test_new_classes_traced.py` | AC-012 |
| Acceptance | `tests/acceptance/logging_coverage/test_sink_failure.py` | AC-013 |
| Acceptance | `tests/acceptance/logging_coverage/test_behavior_unchanged.py` | AC-016 |
| Property | `tests/property/logging_coverage/test_invariants.py` | INV-001 … INV-004 |
| Unit | `tests/unit/logging_coverage/test_edge_cases.py` | EDGE-001 … EDGE-006 |

### Notes

- The property tests use a `tempfile.TemporaryDirectory()` context manager (not the
  function-scoped `tmp_path` fixture) so Hypothesis does not raise a
  function-scoped-fixture health check; they fail on their assertions, not on health checks.
- `UserManager` (usermanagement) and `AuthService` (authentication) are already traced with the
  *old* parameterless `@logged_class` before implementation; the feature enhances
  `@logged_class`/`@logged` (adds `slow_threshold_ms` / `include_args` parameters, the
  `__logged_class__` / `__logged__` markers, and the concrete `slow_threshold_ms` class
  attribute) and traces the remaining untraced classes/functions.
- Spec-vs-code conflict recorded for Phase 4: the spec section 9 table lists "Worker started
  (EventBus) | INFO", but the existing direct statement logs it at DEBUG. REQ-010/AC-010 (keep
  existing direct statements unchanged) wins, so the worker-started statement stays DEBUG.
