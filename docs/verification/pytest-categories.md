# pytest Test Category Configuration

The test suite is organized into five categories. Each category has its own directory and serves a distinct purpose.

## Category Directories

| Category | Directory | Purpose |
|----------|-----------|---------|
| Acceptance | `tests/acceptance/` | Derived from spec; proves requirements are satisfied |
| Integration | `tests/integration/` | Verifies multi-component interactions |
| Contract | `tests/contract/` | Pins external/interface contracts |
| Property | `tests/property/` | Verifies invariants over large input spaces (Hypothesis) |
| Unit | `tests/unit/` | Verifies local component behavior in isolation |

## Running Categories

```bash
# All tests
uv run pytest tests/ -v

# Acceptance only
uv run pytest tests/acceptance/ -v

# Integration only
uv run pytest tests/integration/ -v

# Contract only
uv run pytest tests/contract/ -v

# Property only
uv run pytest tests/property/ -v

# Unit only
uv run pytest tests/unit/ -v
```

## CI Ordering

In CI, run categories in this order (fastest/most critical first):

1. **Contract** — fast, deterministic, catches broken interfaces early.
2. **Acceptance** — proves spec requirements are met.
3. **Property** — Hypothesis tests (slower, but critical for invariants).
4. **Unit** — local behavior verification.
5. **Integration** — multi-component tests (slowest, run last).

## Test Naming Convention

- Acceptance tests: `test_<ac_id>_<description>` (e.g., `test_ac001_valid_request`)
- Property tests: `test_<inv_id>_<description>` (e.g., `test_inv001_normalize_idempotent`)
- Unit tests: `test_<component>_<edge_case>` (e.g., `test_validator_empty_body`)
- Contract tests: `test_<interface>_contract` (e.g., `test_api_response_contract`)
- Integration tests: `test_<components>_interaction` (e.g., `test_validation_normalization_pipeline`)

## Coverage Metrics

Two separate metrics MUST be tracked:

- **Code coverage** — implementation quality (branch coverage, line coverage).
- **Spec coverage** — behavioral completeness (every REQ has at least one GREEN test).

Code coverage of 95% does NOT prove 100% acceptance criteria satisfied. Spec coverage is the primary quality signal.
