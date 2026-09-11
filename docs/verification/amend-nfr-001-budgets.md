# Verification: amend-nfr-001-budgets

## Type
Spec Amendment (user-authorized) — amends NFR-001 in `docs/specs/settings.md` and `docs/specs/logging.md`; re-derives the affected contract tests from the amended specs. No implementation change; no behavior change.

## Rationale
- **Settings NFR-001** budgeted all six single-setting ops at < 1 ms (median) with 1000 registered settings. AC-013 requires `set_value` to persist all current values **synchronously** (the acceptance test loads via `repo.load()` immediately after `set_value`). With 1000 values, persisting = full `values.yaml` rewrite: observed 13.6 ms local / 28.06 ms CI. The < 1 ms budget for mutating ops is unachievable by any implementation satisfying AC-013. Read-only ops (`get_value`, `to_view`, `get_status`) do not persist and meet < 1 ms.
- **Logging NFR-001** budgeted `setup_logger()` at < 10 ms; CI observed 15.55 ms (passes locally). Cost is loguru sink setup + file-sink worker thread (`enqueue=True`) + mkdir; 10 ms has no CI headroom.

## Amendment (user decision, 2026-09-11)
- **Settings NFR-001:** read-only ops (`get_value`, `to_view`, `get_status`) < 1 ms (median) with 1000 registered settings (unchanged); mutating ops (`register`, `set_value`, `reset`) < 50 ms (median) with 1000 registered settings — consistent with the spec's own template YAML I/O budget (< 50 ms), 1.8x headroom over the 28.06 ms CI observation.
- **Logging NFR-001:** `setup_logger()` < 50 ms — 3.2x headroom over the 15.55 ms CI observation.

## Files changed
- `docs/specs/settings.md` (NFR-001 row + Changelog entry)
- `docs/specs/logging.md` (NFR-001 row + Changelog entry)
- `tests/contract/settings/test_settings_contracts.py` (re-derive `test_nfr_001_performance_budgets`)
- `tests/contract/logging/test_logging_contracts.py` (re-derive `test_nfr_001_setup_time_budget`)
- `docs/verification/traceability.md` (NFR-001 rows for the two re-derived tests)

## RED/GREEN
The re-derived tests pass against the **unchanged** implementation (it already meets the amended budgets), so no RED phase applies — RED would only occur if the implementation deviated from the amended spec. Evidence below.

## Evidence
- `uv run pytest tests/contract/settings/test_settings_contracts.py::test_nfr_001_performance_budgets tests/contract/logging/test_logging_contracts.py::test_nfr_001_setup_time_budget -v` → **2 passed** (re-derived tests GREEN).
- `uv run pytest tests/contract/` → **28 passed** (full contract suite, no new failures).
- `uv run ruff check .` → 4 errors, all pre-existing on `main` (F401/F811 in `tests/settings_test_helpers.py` — fixed in open PR #18, not merged yet). Zero new lint errors from this change (the `50.0` magic values were extracted to `_MUTATING_OP_BUDGET_MS` per PLR2004).
- `uv run mypy src/` → Success in 33 source files.

## Notes
- No implementation change: `src/` untouched. No behavior change.
- CI expectation: settings mutating ops observed 28.06 ms median on CI < 50 ms budget (1.8x headroom); logging `setup_logger` observed 15.55 ms on CI < 50 ms budget (3.2x headroom).
