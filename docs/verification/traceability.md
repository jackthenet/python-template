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

### Settings

| Requirement | Acceptance Criterion | Test | Status |
|-------------|---------------------|------|--------|
| REQ-002, REQ-003 | AC-001 | `test_ac_001_text_roundtrip` | RED |
| REQ-002, REQ-003 | AC-002 | `test_ac_002_number_roundtrip` | RED |
| REQ-002, REQ-003 | AC-003 | `test_ac_003_boolean_roundtrip` | RED |
| REQ-002, REQ-003 | AC-004 | `test_ac_004_email_roundtrip` | RED |
| REQ-002, REQ-003 | AC-005 | `test_ac_005_slider_roundtrip` | RED |
| REQ-002, REQ-003 | AC-006 | `test_ac_006_select_roundtrip` | RED |
| REQ-007 | AC-007 | `test_ac_007_default_before_set` | RED |
| REQ-008 | AC-008 | `test_ac_008_set_stores_value` | RED |
| REQ-004 | AC-009 | `test_ac_009_invalid_default` | RED |
| REQ-004 | AC-010 | `test_ac_010_missing_kind_params` | RED |
| REQ-005 | AC-011 | `test_ac_011_duplicate_registration` | RED |
| REQ-006 | AC-012 | `test_ac_012_register_feature` | RED |
| REQ-009 | AC-013 | `test_ac_013_reset_to_default` | RED |
| REQ-010 | AC-014 | `test_ac_014_unknown_key` | RED |
| REQ-011 | AC-015 | `test_ac_015_grouped_views` | RED |
| REQ-012, REQ-001 | AC-016 | `test_ac_016_to_view` | RED |
| REQ-013 | AC-017 | `test_ac_017_status_transitions` | RED |
| REQ-014 | AC-018 | `test_ac_018_singleton` | RED |
| REQ-016, REQ-015 | AC-019 | `test_ac_019_create_template_explicit` | RED |
| REQ-016 | AC-020 | `test_ac_020_create_template_capture` | RED |
| REQ-016 | AC-021 | `test_ac_021_create_template_incomplete` | RED |
| REQ-016 | AC-022 | `test_ac_022_create_template_duplicate` | RED |
| REQ-017 | AC-023 | `test_ac_023_load_template_sets_values` | RED |
| REQ-017 | AC-024 | `test_ac_024_load_template_leave_as_is` | RED |
| REQ-017 | AC-025 | `test_ac_025_load_template_unknown` | RED |
| REQ-018 | AC-026 | `test_ac_026_update_template` | RED |
| REQ-018 | AC-027 | `test_ac_027_update_template_invalid` | RED |
| REQ-019 | AC-028 | `test_ac_028_delete_template` | RED |
| REQ-020 | AC-029 | `test_ac_029_template_access` | RED |
| REQ-022 | AC-030 | `test_ac_030_yaml_file_written` | RED |
| REQ-021, REQ-022 | AC-031 | `test_ac_031_persistence_across_instances` | RED |
| REQ-023 | AC-032 | `test_ac_032_corrupted_file` | RED |
| REQ-023 | AC-033 | `test_ac_033_missing_file` | RED |
| REQ-021 | AC-034 | `test_ac_034_storage_agnostic` | RED |
| REQ-024 | AC-035 | `test_ac_035_set_value_publishes_event` | RED |
| REQ-024 | AC-036 | `test_ac_036_load_template_publishes_events` | RED |
| REQ-025 | AC-037 | `test_ac_037_custom_bus` | RED |
| REQ-005 | AC-038 | `test_ac_038_thread_safe_registration` | RED |
| REQ-024 | AC-039 | `test_ac_039_reset_publishes_events` | RED |
| INV-001 | — | `test_inv_001_set_get_roundtrip` | RED |
| INV-002 | — | `test_inv_002_get_value_always_valid` | RED |
| INV-003 | — | `test_inv_003_reset_to_default` | RED |
| INV-004 | — | `test_inv_004_select_options_valid` | RED |
| INV-005 | — | `test_inv_005_slider_grid_valid` | RED |
| INV-006 | — | `test_inv_006_views_match_values` | RED |
| INV-007 | — | `test_inv_007_load_scope_valid` | RED |
| INV-008 | — | `test_inv_008_exactly_one_event_per_change` | RED |
| INV-009 | — | `test_inv_009_yaml_roundtrip` | RED |
| INV-010 | — | `test_inv_010_status_derivation` | RED |
| EDGE-001 | — | `test_edge_001_unknown_key_lookups` | RED |
| EDGE-002 | — | `test_edge_002_duplicate_registration` | RED |
| EDGE-003 | — | `test_edge_003_wrong_type` | RED |
| EDGE-004 | — | `test_edge_004_bool_for_numeric` | RED |
| EDGE-005 | — | `test_edge_005_number_out_of_bounds` | RED |
| EDGE-006 | — | `test_edge_006_invalid_email` | RED |
| EDGE-007 | — | `test_edge_007_slider_off_grid` | RED |
| EDGE-008 | — | `test_edge_008_slider_out_of_range` | RED |
| EDGE-009 | — | `test_edge_009_select_not_an_option` | RED |
| EDGE-010 | — | `test_edge_010_text_pattern` | RED |
| EDGE-011 | — | `test_edge_011_text_length` | RED |
| EDGE-012 | — | `test_edge_012_reset_unknown` | RED |
| EDGE-013 | — | `test_edge_013_reset_all` | RED |
| EDGE-014 | — | `test_edge_014_slider_min_gt_max` | RED |
| EDGE-015 | — | `test_edge_015_slider_step_nonpositive` | RED |
| EDGE-016 | — | `test_edge_016_select_empty` | RED |
| EDGE-017 | — | `test_edge_017_select_duplicate_options` | RED |
| EDGE-018 | — | `test_edge_018_kind_param_mismatch` | RED |
| EDGE-019 | — | `test_edge_019_invalid_key_format` | RED |
| EDGE-020 | — | `test_edge_020_feature_prefix` | RED |
| EDGE-021 | — | `test_edge_021_unchanged_value_event` | RED |
| EDGE-022 | — | `test_edge_022_bus_shutdown` | RED |
| EDGE-023 | — | `test_edge_023_list_templates_empty` | RED |
| EDGE-024 | — | `test_edge_024_directory_created` | RED |
| EDGE-025 | — | `test_edge_025_schema_invalid_file` | RED |
| EDGE-026 | — | `test_edge_026_empty_scope_template` | RED |
| EDGE-027 | — | `test_edge_027_load_unregistered_settings` | RED |
| EDGE-028 | — | `test_edge_028_invalid_template_name` | RED |
| EDGE-029 | — | `test_edge_029_slider_max_off_grid` | RED |
| NFR-001 | — | `test_nfr_001_performance_budgets` | RED |
| NFR-002 | — | `test_nfr_002_api_and_repository_contract` | RED |
| NFR-003 | — | `test_nfr_003_resource_contract` | RED |
| NFR-004 | — | `test_nfr_004_observability` | RED |
| — | — | `test_multi_feature_reactive_settings` (integration) | RED |
| — | — | `test_template_capture_restore_workflow` (integration) | RED |

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
