# Traceability Matrix

This matrix maintains bidirectional traceability between requirements, acceptance criteria, tests, and implementation.

## Invariants

- Every normative requirement MUST have at least one executable test.
- Every acceptance test MUST trace back to a normative requirement.
- Status values: `PENDING`, `RED`, `GREEN`, `REFACTORED`, `VERIFIED`.

## Matrix

| Requirement | Acceptance Criterion | Test | Status |
|-------------|---------------------|------|--------|
| REQ-001 | AC-001 | `test_valid_request` | PENDING |
| REQ-001 | AC-002 | `test_missing_customer_id` | PENDING |
| REQ-002 | AC-003 | `test_invalid_customer_id` | PENDING |
| INV-001 | — | `test_normalize_idempotent` | PENDING |

## Drift Checks

Run these checks at CI time to detect spec drift:

- **Missing test:** An AC has no corresponding test function.
- **Orphaned test:** A test function has no spec reference.
- **Missing evidence:** A requirement has tests but no successful verification record.
- **Changed behavior:** A PR changes externally observable behavior without changing the corresponding spec.

## Verification Commands

```bash
# Run all acceptance tests
uv run pytest tests/acceptance/ -v

# Run all property tests
uv run pytest tests/property/ -v

# Run all unit tests
uv run pytest tests/unit/ -v

# Run full suite
uv run pytest tests/ -v
```
