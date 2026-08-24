# RED Evidence — Logging Feature

**Spec:** `docs/specs/logging.md`
**Branch:** `feature/logging`
**Date:** 2026-08-24

## RED Command

```bash
uv run pytest tests/acceptance/logging/ tests/property/logging/ tests/unit/logging/ tests/contract/logging/ -v
```

## Result

**28 failed, 0 passed** — all tests fail with `ModuleNotFoundError: No module named 'features'`.

This is the expected RED state: the `features.logging` module does not exist yet.

## Failure Summary

| Category | Tests | Status |
|---|---|---|
| Acceptance | 15 (AC-001..AC-015) | FAILED |
| Property | 4 (INV-001..INV-003) | FAILED |
| Unit | 5 (EDGE-001..EDGE-005) | FAILED |
| Contract | 4 (NFR-001..NFR-004) | FAILED |

## Falsifying Examples (Hypothesis)

- `test_inv_001_setup_logger_idempotent(n=1)` — `ModuleNotFoundError`
- `test_inv_002_setup_logger_thread_safe(n_threads=2)` — `ModuleNotFoundError`
- `test_inv_003_logged_preserves_return_value(a=0, b=0)` — `ModuleNotFoundError`
- `test_inv_003_logged_preserves_exceptions(msg='')` — `ModuleNotFoundError`

## Next Step

Phase 3 (DESIGN): create ADRs and task DAG, then Phase 4 (IMPLEMENT) to achieve GREEN.
