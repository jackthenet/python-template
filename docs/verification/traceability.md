# Traceability Matrix

This matrix maintains bidirectional traceability between requirements, acceptance criteria, tests, and implementation.

## Invariants

- Every normative requirement MUST have one or more executable tests.
- Every acceptance test MUST trace back to a normative requirement.
- Acceptance tests are the authoritative executable representation of externally observable behavior. Unit tests must not replace missing acceptance tests.
- Status values: `PENDING`, `RED`, `GREEN`, `REFACTORED`, `VERIFIED`.

## Matrix

| Requirement | Acceptance Criterion | Test | Status |
|-------------|---------------------|------|--------|
| REQ-001 | AC-001 | `test_ac_001_setup_logger_adds_sinks` | RED |
| REQ-001 | AC-002 | `test_ac_002_setup_logger_idempotent` | RED |
| REQ-001 | AC-003 | `test_ac_003_setup_logger_thread_safe` | RED |
| REQ-002 | AC-004 | `test_ac_004_logged_logs_function_call` | RED |
| REQ-002 | AC-005 | `test_ac_005_logged_preserves_return_value` | RED |
| REQ-002 | AC-006 | `test_ac_006_logged_logs_exceptions` | RED |
| REQ-003 | AC-007 | `test_ac_007_logged_class_logs_method_calls` | RED |
| REQ-003 | AC-008 | `test_ac_008_logged_class_preserves_return_values` | RED |
| REQ-003 | AC-009 | `test_ac_009_logged_class_logs_exceptions` | RED |
| REQ-004 | AC-010 | `test_ac_010_stdlib_logs_routed_to_loguru` | RED |
| REQ-004 | AC-011 | `test_ac_011_stdlib_interception_idempotent` | RED |
| REQ-004 | AC-012 | `test_ac_012_stdlib_interception_thread_safe` | RED |
| REQ-005 | AC-013 | `test_ac_013_public_api_exports` | RED |
| REQ-005 | AC-014 | `test_ac_014_setup_logger_accepts_settings` | RED |
| REQ-005 | AC-015 | `test_ac_015_logged_accepts_level` | RED |
| INV-001 | — | `test_inv_001_setup_logger_idempotent` | RED |
| INV-002 | — | `test_inv_002_setup_logger_thread_safe` | RED |
| INV-003 | — | `test_inv_003_logged_preserves_return_value` | RED |
| INV-003 | — | `test_inv_003_logged_preserves_exceptions` | RED |
| EDGE-001 | — | `test_edge_001_logged_with_no_arguments` | RED |
| EDGE-002 | — | `test_edge_002_logged_with_keyword_arguments` | RED |
| EDGE-003 | — | `test_edge_003_logged_class_with_init` | RED |
| EDGE-004 | — | `test_edge_004_setup_logger_with_none_settings` | RED |
| EDGE-005 | — | `test_edge_005_setup_logger_with_custom_settings` | RED |
| NFR-001 | — | `test_nfr_001_public_api_importable` | RED |
| NFR-002 | — | `test_nfr_002_no_new_dependencies` | RED |
| NFR-003 | — | `test_nfr_003_type_annotations_present` | RED |
| NFR-004 | — | `test_nfr_004_thread_safe` | RED |

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
