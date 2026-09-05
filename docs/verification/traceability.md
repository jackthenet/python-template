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
| REQ-002 | AC-002 | `test_ac_002_setup_logger_idempotent` | RED |
| REQ-002 | AC-003 | `test_ac_003_setup_logger_thread_safe` | RED |
| REQ-003 | AC-004 | `test_ac_004_intercept_handler_routes_records` | RED |
| REQ-003 | AC-005 | `test_ac_005_intercept_handler_skips_bootstrap` | RED |
| REQ-004 | AC-006 | `test_ac_006_logged_sync_entry_exit` | RED |
| REQ-004 | AC-007 | `test_ac_007_logged_async_entry_exit` | RED |
| REQ-004 | AC-008 | `test_ac_008_logged_exception_propagates` | RED |
| REQ-005 | AC-009 | `test_ac_009_logged_level_param` | RED |
| REQ-005 | AC-010 | `test_ac_010_logged_include_args` | RED |
| REQ-006 | AC-011 | `test_ac_011_logged_slow_threshold` | RED |
| REQ-007 | AC-012 | `test_ac_012_logged_class_public_method` | RED |
| REQ-007 | AC-013 | `test_ac_013_logged_class_private_method` | RED |
| REQ-008 | AC-014 | `test_ac_014_get_settings_defaults` | RED |
| REQ-009 | AC-015 | `test_ac_015_obsolete_module_deleted` | RED |
| INV-001 | — | `test_inv_001_concurrent_setup_logger_sinks` | RED |
| INV-002 | — | `test_inv_002_elapsed_time_non_negative` | RED |
| INV-003 | — | `test_inv_003_exception_propagates_unchanged` | RED |
| EDGE-001 | — | `test_edge_001_log_file_parent_created` | RED |
| EDGE-002 | — | `test_edge_002_logged_no_args` | RED |
| EDGE-003 | — | `test_edge_003_logged_nonexistent_setting` | RED |
| EDGE-004 | — | `test_edge_004_logged_class_no_public_methods` | RED |
| EDGE-005 | — | `test_edge_005_intercept_unknown_level` | RED |
| NFR-001 | — | `test_nfr_001_setup_time_budget` | RED |
| NFR-002 | — | `test_nfr_002_decorator_overhead_budget` | RED |
| NFR-003 | — | `test_nfr_003_diagnose_false` | RED |
| NFR-004 | — | `test_nfr_004_backward_compatible_api` | RED |
| — | — | `test_stdlib_loguru_decorator_pipeline` (integration) | RED |

## Event Bus Matrix

The event bus feature (`docs/specs/event-bus.md`) uses its own REQ/AC ID space (REQ-001..007, AC-001..012) that overlaps the logging feature's IDs, so the two matrices are kept separate.

| Requirement | Acceptance Criterion | Test | Status |
|-------------|---------------------|------|--------|
| REQ-001 | AC-001 | `test_ac_001_publish_non_blocking` | GREEN |
| REQ-002 | AC-002 | `test_ac_002_subscribe_matching_event` | GREEN |
| REQ-002 | AC-003 | `test_ac_003_no_match_different_type` | GREEN |
| REQ-002 | AC-004 | `test_ac_004_isinstance_matching` | GREEN |
| REQ-003 | AC-005 | `test_ac_005_error_isolation` | GREEN |
| REQ-003 | AC-006 | `test_ac_006_exception_no_propagate` | GREEN |
| REQ-004 | AC-007 | `test_ac_007_thread_safe_publish` | GREEN |
| REQ-005 | AC-008 | `test_ac_008_shutdown_drains` | GREEN |
| REQ-005 | AC-009 | `test_ac_009_shutdown_idempotent` | GREEN |
| REQ-005 | AC-010 | `test_ac_010_context_manager` | GREEN |
| REQ-006 | AC-011 | `test_ac_011_singleton` | GREEN |
| REQ-007 | AC-012 | `test_ac_012_bounded_queue_drop` | GREEN |
| INV-001 | — | `test_inv_001_exactly_once` | GREEN |
| INV-002 | — | `test_inv_002_isolation` | GREEN |
| INV-003 | — | `test_inv_003_queue_bounded` | GREEN |
| INV-004 | — | `test_inv_004_handler_order` | GREEN |
| EDGE-001 | — | `test_edge_001_lazy_start` | GREEN |
| EDGE-002 | — | `test_edge_002_drop_on_full` | GREEN |
| EDGE-003 | — | `test_edge_003_non_callable_handler` | GREEN |
| EDGE-004 | — | `test_edge_004_non_class_event` | GREEN |
| EDGE-005 | — | `test_edge_005_unsubscribe_not_subscribed` | GREEN |
| EDGE-006 | — | `test_edge_006_dedup` | GREEN |
| EDGE-007 | — | `test_edge_007_publish_after_shutdown` | GREEN |
| EDGE-008 | — | `test_edge_008_handler_raises` | GREEN |
| EDGE-009 | — | `test_edge_009_start_idempotent` | GREEN |
| EDGE-010 | — | `test_edge_010_no_handlers` | GREEN |
| NFR-001 | — | `test_nfr_001_publish_non_blocking_budget` | GREEN |
| NFR-002 | — | `test_nfr_002_handler_failure_isolation` | GREEN |
| NFR-003 | — | `test_nfr_003_single_worker_bounded_queue` | GREEN |
| NFR-004 | — | `test_nfr_004_api_backward_compatible` | GREEN |
| — | — | `test_multi_feature_publish_subscribe` (integration) | GREEN |

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
