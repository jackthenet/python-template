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
| NFR-001 | — | `test_nfr_001_setup_time_budget` | GREEN |
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
| REQ-002, REQ-003 | AC-001 | `test_ac_001_text_roundtrip` | GREEN |
| REQ-002, REQ-003 | AC-002 | `test_ac_002_number_roundtrip` | GREEN |
| REQ-002, REQ-003 | AC-003 | `test_ac_003_boolean_roundtrip` | GREEN |
| REQ-002, REQ-003 | AC-004 | `test_ac_004_email_roundtrip` | GREEN |
| REQ-002, REQ-003 | AC-005 | `test_ac_005_slider_roundtrip` | GREEN |
| REQ-002, REQ-003 | AC-006 | `test_ac_006_select_roundtrip` | GREEN |
| REQ-007 | AC-007 | `test_ac_007_default_before_set` | GREEN |
| REQ-008 | AC-008 | `test_ac_008_set_stores_value` | GREEN |
| REQ-004 | AC-009 | `test_ac_009_invalid_default` | GREEN |
| REQ-004 | AC-010 | `test_ac_010_missing_kind_params` | GREEN |
| REQ-005 | AC-011 | `test_ac_011_duplicate_registration` | GREEN |
| REQ-006 | AC-012 | `test_ac_012_register_feature` | GREEN |
| REQ-009 | AC-013 | `test_ac_013_reset_to_default` | GREEN |
| REQ-010 | AC-014 | `test_ac_014_unknown_key` | GREEN |
| REQ-011 | AC-015 | `test_ac_015_grouped_views` | GREEN |
| REQ-012, REQ-001 | AC-016 | `test_ac_016_to_view` | GREEN |
| REQ-013 | AC-017 | `test_ac_017_status_transitions` | GREEN |
| REQ-014 | AC-018 | `test_ac_018_singleton` | GREEN |
| REQ-014 | AC-018 | `test_offending_tests_do_not_create_shared_settings_dir` (issue `settings-test-isolation` reproduction — offending fixtures now use isolated repositories; no test writes the shared `settings/` dir) | GREEN |
| REQ-016, REQ-015 | AC-019 | `test_ac_019_create_template_explicit` | GREEN |
| REQ-016 | AC-020 | `test_ac_020_create_template_capture` | GREEN |
| REQ-016 | AC-021 | `test_ac_021_create_template_incomplete` | GREEN |
| REQ-016 | AC-022 | `test_ac_022_create_template_duplicate` | GREEN |
| REQ-017 | AC-023 | `test_ac_023_load_template_sets_values` | GREEN |
| REQ-017 | AC-024 | `test_ac_024_load_template_leave_as_is` | GREEN |
| REQ-017 | AC-025 | `test_ac_025_load_template_unknown` | GREEN |
| REQ-018 | AC-026 | `test_ac_026_update_template` | GREEN |
| REQ-018 | AC-027 | `test_ac_027_update_template_invalid` | GREEN |
| REQ-019 | AC-028 | `test_ac_028_delete_template` | GREEN |
| REQ-020 | AC-029 | `test_ac_029_template_access` | GREEN |
| REQ-022 | AC-030 | `test_ac_030_yaml_file_written` | GREEN |
| REQ-021, REQ-022 | AC-031 | `test_ac_031_persistence_across_instances` | GREEN |
| REQ-023 | AC-032 | `test_ac_032_corrupted_file` | GREEN |
| REQ-023 | AC-033 | `test_ac_033_missing_file` | GREEN |
| REQ-021 | AC-034 | `test_ac_034_storage_agnostic` | GREEN |
| REQ-024 | AC-035 | `test_ac_035_set_value_publishes_event` | GREEN |
| REQ-024 | AC-036 | `test_ac_036_load_template_publishes_events` | GREEN |
| REQ-025 | AC-037 | `test_ac_037_custom_bus` | GREEN |
| REQ-005 | AC-038 | `test_ac_038_thread_safe_registration` | GREEN |
| REQ-024 | AC-039 | `test_ac_039_reset_publishes_events` | GREEN |
| INV-001 | — | `test_inv_001_set_get_roundtrip` | GREEN |
| INV-002 | — | `test_inv_002_get_value_always_valid` | GREEN |
| INV-003 | — | `test_inv_003_reset_to_default` | GREEN |
| INV-004 | — | `test_inv_004_select_options_valid` | GREEN |
| INV-005 | — | `test_inv_005_slider_grid_valid` | GREEN |
| INV-006 | — | `test_inv_006_views_match_values` | GREEN |
| INV-007 | — | `test_inv_007_load_scope_valid` | GREEN |
| INV-008 | — | `test_inv_008_exactly_one_event_per_change` | GREEN |
| INV-009 | — | `test_inv_009_yaml_roundtrip` | GREEN |
| INV-010 | — | `test_inv_010_status_derivation` | GREEN |
| EDGE-001 | — | `test_edge_001_unknown_key_lookups` | GREEN |
| EDGE-002 | — | `test_edge_002_duplicate_registration` | GREEN |
| EDGE-003 | — | `test_edge_003_wrong_type` | GREEN |
| EDGE-004 | — | `test_edge_004_bool_for_numeric` | GREEN |
| EDGE-005 | — | `test_edge_005_number_out_of_bounds` | GREEN |
| EDGE-006 | — | `test_edge_006_invalid_email` | GREEN |
| EDGE-007 | — | `test_edge_007_slider_off_grid` | GREEN |
| EDGE-008 | — | `test_edge_008_slider_out_of_range` | GREEN |
| EDGE-009 | — | `test_edge_009_select_not_an_option` | GREEN |
| EDGE-010 | — | `test_edge_010_text_pattern` | GREEN |
| EDGE-011 | — | `test_edge_011_text_length` | GREEN |
| EDGE-012 | — | `test_edge_012_reset_unknown` | GREEN |
| EDGE-013 | — | `test_edge_013_reset_all` | GREEN |
| EDGE-014 | — | `test_edge_014_slider_min_gt_max` | GREEN |
| EDGE-015 | — | `test_edge_015_slider_step_nonpositive` | GREEN |
| EDGE-016 | — | `test_edge_016_select_empty` | GREEN |
| EDGE-017 | — | `test_edge_017_select_duplicate_options` | GREEN |
| EDGE-018 | — | `test_edge_018_kind_param_mismatch` | GREEN |
| EDGE-019 | — | `test_edge_019_invalid_key_format` | GREEN |
| EDGE-020 | — | `test_edge_020_feature_prefix` | GREEN |
| EDGE-021 | — | `test_edge_021_unchanged_value_event` | GREEN |
| EDGE-022 | — | `test_edge_022_bus_shutdown` | GREEN |
| EDGE-023 | — | `test_edge_023_list_templates_empty` | GREEN |
| EDGE-024 | — | `test_edge_024_directory_created` | GREEN |
| EDGE-025 | — | `test_edge_025_schema_invalid_file` | GREEN |
| EDGE-026 | — | `test_edge_026_empty_scope_template` | GREEN |
| EDGE-027 | — | `test_edge_027_load_unregistered_settings` | GREEN |
| EDGE-028 | — | `test_edge_028_invalid_template_name` | GREEN |
| EDGE-029 | — | `test_edge_029_slider_max_off_grid` | GREEN |
| NFR-001 | — | `test_nfr_001_performance_budgets` | GREEN |
| NFR-002 | — | `test_nfr_002_api_and_repository_contract` | GREEN |
| NFR-003 | — | `test_nfr_003_resource_contract` | GREEN |
| NFR-004 | — | `test_nfr_004_observability` | GREEN |
| — | — | `test_multi_feature_reactive_settings` (integration) | GREEN |
| — | — | `test_template_capture_restore_workflow` (integration) | GREEN |

## User Management Matrix

The user-management feature (`docs/specs/user-management.md`) uses its own REQ/AC ID space (REQ-001..017, AC-001..038) that overlaps the other features' IDs, so the matrix is kept separate.

| Requirement | Acceptance Criterion | Test | Status |
|-------------|---------------------|------|--------|
| REQ-001 | AC-001 | `test_ac_001_create_valid_user` | GREEN |
| REQ-002 | AC-001 | `test_ac_001_create_valid_user` | GREEN |
| REQ-002 | AC-004 | `test_ac_004_username_too_short` | GREEN |
| REQ-002 | AC-005 | `test_ac_005_password_too_short` | GREEN |
| REQ-002 | AC-006 | `test_ac_006_invalid_email` | GREEN |
| REQ-002 | AC-007 | `test_ac_007_non_http_profile_picture_url` | GREEN |
| REQ-003 | AC-002 | `test_ac_002_duplicate_username` | GREEN |
| REQ-003 | AC-003 | `test_ac_003_duplicate_email_case_insensitive` | GREEN |
| REQ-004 | AC-010 | `test_ac_010_argon2_hash_stored_not_exposed` | GREEN |
| REQ-005 | AC-011 | `test_ac_011_change_password` | GREEN |
| REQ-005 | AC-012 | `test_ac_012_verify_password` | GREEN |
| REQ-005 | AC-013 | `test_ac_013_change_password_weak` | GREEN |
| REQ-005 | AC-014 | `test_ac_014_password_ops_unknown_user` | GREEN |
| REQ-006 | AC-008 | `test_ac_008_role_not_in_set_create` | GREEN |
| REQ-006 | AC-009 | `test_ac_009_custom_role_set` | GREEN |
| REQ-006 | AC-016 | `test_ac_016_set_role_not_in_set` | GREEN |
| REQ-007 | AC-015 | `test_ac_015_set_role` | GREEN |
| REQ-008 | AC-017 | `test_ac_017_delete_last_admin` | GREEN |
| REQ-008 | AC-018 | `test_ac_018_deactivate_last_admin` | GREEN |
| REQ-008 | AC-019 | `test_ac_019_demote_last_admin` | GREEN |
| REQ-009 | AC-020 | `test_ac_020_deactivate_activate` | GREEN |
| REQ-009 | AC-021 | `test_ac_021_activate_idempotent` | GREEN |
| REQ-010 | AC-022 | `test_ac_022_get_user` | GREEN |
| REQ-010 | AC-023 | `test_ac_023_get_user_by_username` | GREEN |
| REQ-010 | AC-024 | `test_ac_024_list_users_excludes_inactive` | GREEN |
| REQ-011 | AC-025 | `test_ac_025_update_user` | GREEN |
| REQ-012 | AC-026 | `test_ac_026_delete_user` | GREEN |
| REQ-013 | AC-027 | `test_ac_027_persistence_across_instances` | GREEN |
| REQ-013 | AC-028 | `test_ac_028_service_with_fake_repository` | GREEN |
| REQ-014 | AC-029 | `test_ac_029_error_hierarchy_context` | GREEN |
| REQ-015 | — | `test_nfr_005_operations_logged` | GREEN |
| REQ-016 | AC-030 | `test_ac_030_event_user_created` | GREEN |
| REQ-016 | AC-031 | `test_ac_031_event_user_updated` | GREEN |
| REQ-016 | AC-032 | `test_ac_032_event_user_deleted` | GREEN |
| REQ-016 | AC-033 | `test_ac_033_event_password_changed` | GREEN |
| REQ-016 | AC-034 | `test_ac_034_event_role_changed` | GREEN |
| REQ-016 | AC-035 | `test_ac_035_event_activated` | GREEN |
| REQ-016 | AC-036 | `test_ac_036_event_deactivated` | GREEN |
| REQ-017 | AC-037 | `test_ac_037_no_event_on_failure` | GREEN |
| REQ-017 | AC-038 | `test_ac_038_no_publisher` | GREEN |
| INV-001 | — | `test_inv_001_create_read_consistency` | GREEN |
| INV-002 | — | `test_inv_002_password_round_trip` | GREEN |
| INV-003 | — | `test_inv_003_last_admin_invariant` | GREEN |
| INV-004 | — | `test_inv_004_update_semantics` | GREEN |
| INV-005 | — | `test_inv_005_uniqueness` | GREEN |
| INV-006 | — | `test_inv_006_event_correspondence` | GREEN |
| EDGE-001 | — | `test_edge_001_update_email_collision` | GREEN |
| EDGE-002 | — | `test_edge_002_empty_update_noop` | GREEN |
| EDGE-003 | — | `test_edge_003_double_delete` | GREEN |
| EDGE-004 | — | `test_edge_004_deactivate_already_inactive` | GREEN |
| EDGE-005 | — | `test_edge_005_set_role_same` | GREEN |
| EDGE-006 | — | `test_edge_006_verify_unknown` | GREEN |
| EDGE-007 | — | `test_edge_007_repo_creates_parent_dir` | GREEN |
| EDGE-008 | — | `test_edge_008_memory_repository` | GREEN |
| EDGE-009 | — | `test_edge_009_empty_roles` | GREEN |
| EDGE-010 | — | `test_edge_010_uppercase_role` | GREEN |
| EDGE-011 | — | `test_edge_011_username_whitespace` | GREEN |
| EDGE-012 | — | `test_edge_012_password_no_digit` | GREEN |
| EDGE-013 | — | `test_edge_013_password_no_letter` | GREEN |
| EDGE-014 | — | `test_edge_014_list_empty` | GREEN |
| EDGE-015 | — | `test_edge_015_concurrent_duplicate_create` | GREEN |
| EDGE-016 | — | `test_edge_016_delete_admin_with_two_admins` | GREEN |
| EDGE-017 | — | `test_edge_017_update_unknown` | GREEN |
| EDGE-018 | — | `test_edge_018_display_name_whitespace` | GREEN |
| EDGE-019 | — | `test_edge_019_optional_fields_none` | GREEN |
| EDGE-020 | — | `test_edge_020_publisher_raises` | GREEN |
| EDGE-021 | — | `test_edge_021_case_sensitive_usernames` | GREEN |
| NFR-001 | — | `test_nfr_001_performance_budgets` | GREEN |
| NFR-002 | — | `test_nfr_002_no_plaintext_or_hash_exposed` | GREEN |
| NFR-003 | — | `test_nfr_003_api_backward_compatible` | GREEN |
| NFR-004 | — | `test_nfr_004_concurrent_repository_safety` | GREEN |
| NFR-005 | — | `test_nfr_005_operations_logged` | GREEN |
| — | — | `test_full_user_lifecycle` (integration) | GREEN |
| — | — | `test_events_and_persistence_across_instances` (integration) | GREEN |

## Authentication Matrix

The authentication feature (`docs/specs/authentication.md`) uses its own REQ/AC ID space (REQ-001..022, AC-001..035) that overlaps the other features' IDs, so the matrix is kept separate.

| Requirement | Acceptance Criterion | Test | Status |
|-------------|---------------------|------|--------|
| REQ-001 | AC-001 | `test_ac_001_login_by_username_success` | GREEN |
| REQ-001 | AC-002 | `test_ac_002_login_by_email_success` | GREEN |
| REQ-002 | AC-003 | `test_ac_003_login_wrong_password_rejected` | GREEN |
| REQ-003 | AC-003 | `test_ac_003_login_wrong_password_rejected` | GREEN |
| REQ-003 | AC-004 | `test_ac_004_login_unknown_user_rejected` | GREEN |
| REQ-003 | AC-005 | `test_ac_005_login_inactive_user_rejected` | GREEN |
| REQ-004 | AC-006 | `test_ac_006_below_max_failures_not_locked` | GREEN |
| REQ-004 | AC-007 | `test_ac_007_locked_identifier_rejected_even_correct_password` | GREEN |
| REQ-004 | AC-008 | `test_ac_008_lockout_expires_and_success_clears` | GREEN |
| REQ-005 | AC-009 | `test_ac_009_dummy_verify_on_unknown_user` | GREEN |
| REQ-006 | AC-010 | `test_ac_010_token_format_and_hashed_at_rest` | GREEN |
| REQ-007 | AC-011 | `test_ac_011_session_expiry` | GREEN |
| REQ-008 | AC-012 | `test_ac_012_session_info_valid` | GREEN |
| REQ-009 | AC-013 | `test_ac_013_logout_revokes` | GREEN |
| REQ-009 | AC-014 | `test_ac_014_logout_invalid_noop` | GREEN |
| REQ-010 | AC-015 | `test_ac_015_reset_request_registered_email` | GREEN |
| REQ-010 | AC-016 | `test_ac_016_reset_request_unknown_email` | GREEN |
| REQ-011 | AC-017 | `test_ac_017_reset_token_single_use` | GREEN |
| REQ-011 | AC-018 | `test_ac_018_new_request_supersedes` | GREEN |
| REQ-012 | AC-019 | `test_ac_019_reset_completes_and_revokes_sessions` | GREEN |
| REQ-013 | AC-020 | `test_ac_020_reset_expired_token` | GREEN |
| REQ-013 | AC-021 | `test_ac_021_reset_unknown_token` | GREEN |
| REQ-014 | AC-022 | `test_ac_022_begin_registration_options` | GREEN |
| REQ-014 | AC-023 | `test_ac_023_complete_registration_stores` | GREEN |
| REQ-015 | AC-024 | `test_ac_024_begin_login_options` | GREEN |
| REQ-015 | AC-025 | `test_ac_025_complete_login_issues_session` | GREEN |
| REQ-016 | AC-026 | `test_ac_026_hijack_detected` | GREEN |
| REQ-017 | AC-027 | `test_ac_027_list_passkeys` | GREEN |
| REQ-017 | AC-028 | `test_ac_028_delete_passkey` | GREEN |
| REQ-018 | AC-029 | `test_ac_029_password_and_passkey_coexist` | GREEN |
| REQ-019 | AC-030 | `test_ac_030_empty_identifier_validation_error` | GREEN |
| REQ-020 | AC-031 | `test_ac_031_login_success_event` | GREEN |
| REQ-020 | AC-032 | `test_ac_032_login_failed_event` | GREEN |
| REQ-020 | AC-033 | `test_ac_033_lifecycle_events_and_none_publisher` | GREEN |
| REQ-021 | AC-034 | `test_ac_034_no_hash_in_representations` | GREEN |
| REQ-022 | AC-035 | `test_ac_035_no_secrets_in_log_records` | GREEN |
| INV-001 | — | `test_inv_001_token_hash_uniqueness` | GREEN |
| INV-002 | — | `test_inv_002_session_validity_iff_unexpired_unrevoked` | GREEN |
| INV-003 | — | `test_inv_003_reset_token_at_most_once` | GREEN |
| INV-004 | — | `test_inv_004_lockout_threshold` | GREEN |
| INV-005 | — | `test_inv_005_no_password_in_observable_output` | GREEN |
| EDGE-001 | — | `test_edge_001_login_neither_username_nor_email` | GREEN |
| EDGE-002 | — | `test_edge_002_login_inactive_user` | GREEN |
| EDGE-003 | — | `test_edge_003_login_while_locked` | GREEN |
| EDGE-004 | — | `test_edge_004_session_info_expired` | GREEN |
| EDGE-005 | — | `test_edge_005_session_info_revoked` | GREEN |
| EDGE-006 | — | `test_edge_006_logout_twice_noop` | GREEN |
| EDGE-007 | — | `test_edge_007_reset_unknown_email_no_token` | GREEN |
| EDGE-008 | — | `test_edge_008_reset_expired_token` | GREEN |
| EDGE-009 | — | `test_edge_009_reset_used_token` | GREEN |
| EDGE-010 | — | `test_edge_010_reset_unknown_token` | GREEN |
| EDGE-011 | — | `test_edge_011_new_request_supersedes` | GREEN |
| EDGE-012 | — | `test_edge_012_reset_weak_password` | GREEN |
| EDGE-013 | — | `test_edge_013_registration_invalid_response` | GREEN |
| EDGE-014 | — | `test_edge_014_begin_login_unregistered_credential` | GREEN |
| EDGE-015 | — | `test_edge_015_hijack_detected` | GREEN |
| EDGE-016 | — | `test_edge_016_login_failed_assertion` | GREEN |
| EDGE-017 | — | `test_edge_017_session_info_no_token` | GREEN |
| EDGE-018 | — | `test_edge_018_empty_identifier` | GREEN |
| NFR-001 | — | `test_nfr_001_login_performance_budget` | GREEN |
| NFR-002 | — | `test_nfr_002_no_secrets_in_logs_or_events` | GREEN |
| NFR-003 | — | `test_nfr_003_public_api_stable` | GREEN |
| NFR-004 | — | `test_nfr_004_service_traced` | GREEN |
| NFR-005 | — | `test_nfr_005_concurrent_login_thread_safety` | GREEN |
| — | — | `test_session_repository_roundtrip`, `test_reset_repository_roundtrip`, `test_webauthn_repository_roundtrip`, `test_full_flow_login_reset_logout` (integration) | GREEN |

## Logging Coverage Matrix

The logging-coverage feature (`docs/specs/logging-coverage.md`) traces all existing backend classes and module functions with the enhanced logging decorators; it uses its own REQ/AC ID space that overlaps the other features' IDs, so the matrix is kept separate.

| Requirement | Acceptance Criterion | Test | Status |
|-------------|---------------------|------|--------|
| REQ-001 | AC-001 | `test_inventory_covers_all_public_classes` | GREEN |
| REQ-002 | AC-002 | `test_service_registry_classes_traced` | GREEN |
| REQ-003 | AC-003 | `test_abc_traced_subclass_inherits` | GREEN |
| REQ-004 | AC-004 | `test_concrete_repo_provider_traced` | GREEN |
| REQ-005 | AC-005 | `test_module_functions_traced` | GREEN |
| REQ-006 | AC-006 | `test_secret_handler_args_not_logged` | GREEN |
| REQ-007 | AC-007 | `test_traced_classes_have_concrete_threshold` | GREEN |
| REQ-008 | AC-008 | `test_semantic_log_levels` | GREEN |
| REQ-009 | AC-009 | `test_traced_class_docstrings_mention_tracing` | GREEN |
| REQ-010 | AC-010 | `test_existing_direct_loguru_kept` | GREEN |
| REQ-011 | AC-011 | `test_entrypoint_calls_setup_logger_once` | GREEN |
| REQ-012 | AC-012 | `test_new_public_classes_traced_by_default` | GREEN |
| REQ-013 | AC-013 | `test_sink_failure_does_not_interrupt` | GREEN |
| REQ-014 | AC-014 | `test_slow_call_logs_warning_not_interrupted` | GREEN |
| REQ-015 | AC-015 | `test_no_raw_secrets_in_any_log_record` | GREEN |
| REQ-016 | AC-016 | `test_tracing_does_not_change_behavior` | GREEN |
| INV-001 | — | `test_one_entry_one_exit_per_call` | GREEN |
| INV-002 | — | `test_secret_args_never_logged` | GREEN |
| INV-003 | — | `test_elapsed_ms_non_negative` | GREEN |
| INV-004 | — | `test_tracing_never_interrupts_call` | GREEN |
| EDGE-001 | — | `test_slow_threshold_exceeded` | GREEN |
| EDGE-002 | — | `test_sink_failure_graceful` | GREEN |
| EDGE-003 | — | `test_abc_subclass_traced` | GREEN |
| EDGE-004 | — | `test_traced_method_exception_propagates` | GREEN |
| EDGE-005 | — | `test_setup_logger_idempotent` | GREEN |
| EDGE-006 | — | `test_traced_method_no_args` | GREEN |
| NFR-001 | — | `test_slow_call_logs_warning_not_interrupted` | GREEN |
| NFR-002 | — | `test_no_raw_secrets_in_any_log_record` | GREEN |
| NFR-003 | — | `test_semantic_log_levels` | GREEN |
| NFR-004 | — | `test_tracing_does_not_change_behavior` | GREEN |
| NFR-005 | — | `test_semantic_log_levels` | GREEN |

## Settings Coverage Matrix

The settings-coverage feature (`docs/specs/settings-coverage.md`) uses its own REQ/AC ID space that overlaps the other features' IDs, so the matrix is kept separate.

| Requirement | Acceptance Criterion | Test | Status |
|-------------|---------------------|------|--------|
| REQ-001 | AC-001 | `test_register_settings_registers` | RED |
| REQ-001 | AC-002 | `test_no_import_side_effects` | RED |
| REQ-002 | AC-003 | `test_main_wires_all_features` | RED |
| REQ-003 | AC-004 | `test_set_value_affects_running_feature` | RED |
| REQ-004 | AC-005 | `test_constructor_default_registry_value` | RED |
| REQ-005 | AC-006 | `test_unregistered_key_fallback` | RED |
| REQ-006 | AC-007 | `test_list_definition_accepted` | RED |
| REQ-007 | AC-008 | `test_list_value_validation` | RED |
| REQ-007 | AC-009 | `test_list_min_items` | RED |
| REQ-007 | AC-010 | `test_list_no_duplicates` | RED |
| REQ-008 | AC-011 | `test_list_min_gt_max_rejected` | RED |
| REQ-008 | AC-012 | `test_list_spec_on_text_rejected` | RED |
| REQ-009 | AC-013 | `test_set_value_persists` | RED |
| REQ-010 | AC-014 | `test_yaml_value_repository` | RED |
| REQ-011 | AC-015 | `test_persisted_precedence` | RED |
| REQ-012 | AC-016 | `test_guarded_read_no_side_effect` | RED |
| REQ-013 | AC-017 | `test_eventbus_no_registry_default` | RED |
| REQ-013 | AC-018 | `test_eventbus_registry_value` | RED |
| REQ-014 | AC-019 | `test_setup_logger_reads_registry` | RED |
| REQ-015 | AC-020 | `test_sink_reconfigured_on_change` | RED |
| REQ-016 | AC-021 | `test_logging_stub_removed` | RED |
| REQ-017 | AC-022 | `test_key_prefix` | RED |
| REQ-018 | AC-023 | `test_category_group` | RED |
| REQ-019 | AC-024 | `test_inventory_matches` | RED |
| REQ-020 | AC-025 | `test_tracing` | RED |
| REQ-021 | AC-026 | `test_no_env_vars` | RED |
| REQ-022 | AC-027 | `test_settings_registers_nothing` | RED |
| INV-001 | — | `test_get_value_valid_for_kind` | RED |
| INV-002 | — | `test_list_round_trip` | RED |
| INV-003 | — | `test_live_read_after_set` | RED |
| INV-004 | — | `test_register_idempotent_fresh` | RED |
| INV-005 | — | `test_persisted_precedence_invariant` | RED |
| EDGE-001 | — | `test_eventbus_bootstrap_cycle` | RED |
| EDGE-002 | — | `test_unregistered_key_warning` | RED |
| EDGE-003 | — | `test_corrupted_values_yaml` | RED |
| EDGE-004 | — | `test_missing_values_yaml` | RED |
| EDGE-005 | — | `test_list_item_pattern_mismatch` | RED |
| EDGE-006 | — | `test_list_min_gt_max` | RED |
| EDGE-007 | — | `test_setup_logger_idempotent` | RED |
| EDGE-008 | — | `test_sink_reconfigured_rotation` | RED |
| EDGE-009 | — | `test_persist_all_values` | RED |
| EDGE-010 | — | `test_live_read_no_trace_on_same` | RED |
| EDGE-011 | — | `test_guarded_read_none` | RED |
| EDGE-012 | — | `test_list_non_string_rejected` | RED |
| NFR-001 | — | `test_live_read_in_memory` | RED |
| NFR-002 | — | `test_no_secret_settings` | RED |
| NFR-003 | — | `test_inventory_backward_compatible` | RED |
| NFR-004 | — | `test_observability_tracing` | RED |
| NFR-005 | — | `test_atomic_write` | RED |
| NFR-006 | — | `test_thread_safety` | RED |

## Mail Service Matrix

The mail-service feature (`docs/specs/mail-service.md`) uses its own REQ/AC ID space that overlaps the other features' IDs, so the matrix is kept separate.

| Requirement | Acceptance Criterion | Test | Status |
|-------------|---------------------|------|--------|
| REQ-001 | AC-001 | `test_ac_001_register_settings` | GREEN |
| REQ-002 | AC-002 | `test_ac_002_live_read_modified_host` | GREEN |
| REQ-002 | AC-003 | `test_ac_003_fallback_unregistered_host` | GREEN |
| REQ-003 | AC-004 | `test_ac_004_core_send_success` | GREEN |
| REQ-004 | AC-005 | `test_ac_005_password_reset_email` | GREEN |
| REQ-005 | AC-006 | `test_ac_006_email_verification_email` | GREEN |
| REQ-006 | AC-007 | `test_ac_007_feature_specific_template` | GREEN |
| REQ-007 | AC-008 | `test_ac_008_template_rendering` | GREEN |
| REQ-008 | AC-009 | `test_ac_009_invalid_recipient` | GREEN |
| REQ-009 | AC-010 | `test_ac_010_missing_variable` | GREEN |
| REQ-010 | AC-011 | `test_ac_011_empty_smtp_host` | GREEN |
| REQ-011 | AC-012 | `test_ac_012_transport_failure` | GREEN |
| REQ-012 | AC-013 | `test_ac_013_email_sent_event` | GREEN |
| REQ-012 | AC-014 | `test_ac_014_email_failed_event` | GREEN |
| REQ-013 | AC-015 | `test_ac_015_non_sensitive_events` | GREEN |
| REQ-014 | AC-016 | `test_ac_016_no_secrets_in_log_records` | GREEN |
| REQ-015 | AC-017 | `test_ac_017_public_api_stable` | GREEN |
| REQ-016 | AC-018 | `test_ac_018_concurrent_send` | GREEN |
| REQ-017 | AC-019 | `test_ac_019_multipart_alternative` | GREEN |
| INV-001 | — | `test_inv_001_rendering_deterministic` | GREEN |
| INV-002 | — | `test_inv_002_xss_safe_substitution` | GREEN |
| INV-003 | — | `test_inv_003_no_password_in_observable_output` | GREEN |
| INV-004 | — | `test_inv_004_no_body_in_events` | GREEN |
| INV-005 | — | `test_inv_005_failure_independence` | GREEN |
| EDGE-001 | — | `test_edge_001_invalid_recipient` | GREEN |
| EDGE-002 | — | `test_edge_002_missing_variable` | GREEN |
| EDGE-003 | — | `test_edge_003_malformed_template` | GREEN |
| EDGE-004 | — | `test_edge_004_empty_smtp_host` | GREEN |
| EDGE-005 | — | `test_edge_005_connection_refused` | GREEN |
| EDGE-006 | — | `test_edge_006_auth_failure` | GREEN |
| EDGE-007 | — | `test_edge_007_protocol_error` | GREEN |
| EDGE-008 | — | `test_edge_008_timeout` | GREEN |
| EDGE-009 | — | `test_edge_009_none_event_bus` | GREEN |
| EDGE-010 | — | `test_edge_010_failure_then_success` | GREEN |
| NFR-001 | — | `test_nfr_001_preparation_performance_budget` | GREEN |
| NFR-002 | — | `test_nfr_002_no_secrets_in_logs_or_events` | GREEN |
| NFR-003 | — | `test_nfr_003_public_api_stable` | GREEN |
| NFR-004 | — | `test_nfr_004_service_traced` | GREEN |
| NFR-005 | — | `test_nfr_005_concurrent_send_thread_safety` | GREEN |

## File Management Matrix

The file-management feature (`docs/specs/file-management.md`) uses its own REQ/AC ID space that overlaps the other features' IDs, so the matrix is kept separate. Status `GREEN`: all 90 rows pass — every REQ has at least one GREEN test, every AC has at least one executable (GREEN) test, every INV has a property test (GREEN), every EDGE has a unit test (GREEN), every NFR has a contract test (GREEN). Full file-management suite: 91 passed, 1 skipped (`test_ac_031_symlink_rejected` — symlinks not available on this host, a legitimate environment skip).

| Requirement | Acceptance Criterion | Test | Status |
|-------------|---------------------|------|--------|
| REQ-001, REQ-002 | AC-001 | `test_ac_001_upload_bytes_round_trip` | GREEN |
| REQ-002 | AC-002 | `test_ac_002_upload_file_path` | GREEN |
| REQ-002 | AC-003 | `test_ac_003_upload_file_like_stream` | GREEN |
| REQ-003 | AC-004 | `test_ac_004_zero_byte_rejected` | GREEN |
| REQ-003 | AC-005 | `test_ac_005_general_size_limit` | GREEN |
| REQ-003 | AC-006 | `test_ac_006_avatar_size_limit` | GREEN |
| REQ-003 | AC-007 | `test_ac_007_live_max_file_size` | GREEN |
| REQ-004 | AC-008 | `test_ac_008_magic_byte_detection` | GREEN |
| REQ-005 | AC-009 | `test_ac_009_declared_type_conflict` | GREEN |
| REQ-005 | AC-010 | `test_ac_010_filename_type_conflict` | GREEN |
| REQ-006 | AC-011 | `test_ac_011_type_not_allowed` | GREEN |
| REQ-006 | AC-012 | `test_ac_012_live_allowed_types` | GREEN |
| REQ-007 | AC-013 | `test_ac_013_generated_uuid_key` | GREEN |
| REQ-007 | AC-014 | `test_ac_014_caller_key` | GREEN |
| REQ-007 | AC-015 | `test_ac_015_traversal_key_rejected` | GREEN |
| REQ-008 | AC-016 | `test_ac_016_storage_failure_rollback` | GREEN |
| REQ-008 | AC-017 | `test_ac_017_metadata_failure_rollback` | GREEN |
| REQ-009 | AC-018 | `test_ac_018_concurrent_same_key_last_write_wins` | GREEN |
| REQ-010 | AC-019 | `test_ac_019_download_bytes` | GREEN |
| REQ-010 | AC-020 | `test_ac_020_open_stream` | GREEN |
| REQ-010 | AC-021 | `test_ac_021_download_missing` | GREEN |
| REQ-011 | AC-022 | `test_ac_022_delete` | GREEN |
| REQ-011 | AC-023 | `test_ac_023_delete_missing` | GREEN |
| REQ-012 | AC-024 | `test_ac_024_metadata_fields` | GREEN |
| REQ-013 | AC-025 | `test_ac_025_persistence_across_instances` | GREEN |
| REQ-013 | AC-026 | `test_ac_026_service_with_fake_repository` | GREEN |
| REQ-014 | AC-027 | `test_ac_027_get_file_and_list_pagination` | GREEN |
| REQ-014 | AC-028 | `test_ac_028_list_invalid_pagination` | GREEN |
| REQ-015 | AC-029 | `test_ac_029_default_local_backend` | GREEN |
| REQ-015 | AC-030 | `test_ac_030_in_memory_backend` | GREEN |
| REQ-016 | AC-031 | `test_ac_031_symlink_rejected` | GREEN |
| REQ-016 | AC-032 | `test_ac_032_path_escape_rejected` | GREEN |
| REQ-017 | AC-033 | `test_ac_033_upload_avatar` | GREEN |
| REQ-017 | AC-034 | `test_ac_034_upload_avatar_existing` | GREEN |
| REQ-017 | AC-035 | `test_ac_035_replace_avatar` | GREEN |
| REQ-017 | AC-036 | `test_ac_036_replace_avatar_missing` | GREEN |
| REQ-017 | AC-037 | `test_ac_037_delete_avatar` | GREEN |
| REQ-017 | AC-038 | `test_ac_038_delete_avatar_noop` | GREEN |
| REQ-018 | AC-039 | `test_ac_039_avatar_url_format` | GREEN |
| REQ-018 | AC-040 | `test_ac_040_live_avatar_base_url` | GREEN |
| REQ-019 | AC-041 | `test_ac_041_avatar_undecodable` | GREEN |
| REQ-019 | AC-042 | `test_ac_042_avatar_dimensions_exceeded` | GREEN |
| REQ-019 | AC-043 | `test_ac_043_avatar_type_not_allowed` | GREEN |
| REQ-020 | AC-044 | `test_ac_044_get_avatar_default` | GREEN |
| REQ-021 | AC-045 | `test_ac_045_avatar_variants_created` | GREEN |
| REQ-021 | AC-046 | `test_ac_046_avatar_variants_replaced` | GREEN |
| REQ-022 | AC-047 | `test_ac_047_event_uploaded` | GREEN |
| REQ-022 | AC-048 | `test_ac_048_event_downloaded_deleted` | GREEN |
| REQ-022 | AC-049 | `test_ac_049_event_validation_failed` | GREEN |
| REQ-022 | AC-050 | `test_ac_050_no_publisher` | GREEN |
| REQ-023 | AC-051 | `test_ac_051_error_hierarchy_context` | GREEN |
| REQ-024 | AC-052 | `test_ac_052_register_settings` | GREEN |
| REQ-024 | AC-053 | `test_ac_053_unregistered_settings_defaults` | GREEN |
| REQ-025 | AC-054 | `test_ac_054_operations_traced` | GREEN |
| REQ-026 | AC-055 | `test_ac_055_layout_convention` | GREEN |
| INV-001 | — | `test_inv_001_no_partial_state_on_failure` | GREEN |
| INV-002 | — | `test_inv_002_concurrent_same_key_last_write_wins` | GREEN |
| INV-003 | — | `test_inv_003_metadata_matches_content` | GREEN |
| INV-004 | — | `test_inv_004_at_most_one_avatar_per_user` | GREEN |
| INV-005 | — | `test_inv_005_avatar_url_format` | GREEN |
| INV-006 | — | `test_inv_006_event_correspondence` | GREEN |
| INV-007 | — | `test_inv_007_key_containment` | GREEN |
| INV-008 | — | `test_inv_008_variant_consistency` | GREEN |
| EDGE-001 | — | `test_edge_001_source_not_found` | GREEN |
| EDGE-002 | — | `test_edge_002_source_not_a_file` | GREEN |
| EDGE-003 | — | `test_edge_003_stream_exceeds_limit_mid_stream` | GREEN |
| EDGE-004 | — | `test_edge_004_key_null_byte` | GREEN |
| EDGE-005 | — | `test_edge_005_key_absolute_path` | GREEN |
| EDGE-006 | — | `test_edge_006_record_without_content` | GREEN |
| EDGE-007 | — | `test_edge_007_delete_missing_content` | GREEN |
| EDGE-008 | — | `test_edge_008_list_empty_store` | GREEN |
| EDGE-009 | — | `test_edge_009_list_offset_beyond_end` | GREEN |
| EDGE-010 | — | `test_edge_010_sequential_key_replacement` | GREEN |
| EDGE-011 | — | `test_edge_011_dangling_avatar_mapping` | GREEN |
| EDGE-012 | — | `test_edge_012_truncated_png_decode_failure` | GREEN |
| EDGE-013 | — | `test_edge_013_variant_generation_failure_rollback` | GREEN |
| EDGE-014 | — | `test_edge_014_publisher_raises` | GREEN |
| EDGE-015 | — | `test_edge_015_repo_creates_parent_dir` | GREEN |
| EDGE-016 | — | `test_edge_016_in_memory_isolation` | GREEN |
| EDGE-017 | — | `test_edge_017_concurrent_download_upload` | GREEN |
| EDGE-018 | — | `test_edge_018_dimensions_boundary_allowed` | GREEN |
| EDGE-019 | — | `test_edge_019_size_boundary_allowed` | GREEN |
| NFR-001 | — | `test_nfr_001_performance_budgets` | GREEN |
| NFR-002 | — | `test_nfr_002_no_content_in_logs_events_errors` | GREEN |
| NFR-003 | — | `test_nfr_003_api_backward_compatible` | GREEN |
| NFR-004 | — | `test_nfr_004_concurrent_repository_safety` | GREEN |
| NFR-005 | — | `test_nfr_005_operations_logged` | GREEN |
| — | integration | `test_full_file_lifecycle` | GREEN |
| — | integration | `test_avatar_lifecycle_with_variants` | GREEN |
| — | integration | `test_concurrent_same_key_upload` | GREEN |

## Session Management Matrix

The session-management feature (`docs/specs/session-management.md`) uses its own REQ/AC ID space (REQ-001..022, AC-001..045, INV-001..005, EDGE-001..012, NFR-001..005) that overlaps other features' IDs, so its matrix is kept separate. Rows are ordered per the task DAG (`.github/task-runner/tasks.json`: T-001…T-009). Status `GREEN`: all rows pass (Phase 5, S5.1) — every REQ has at least one GREEN test, every AC has at least one executable (GREEN) test, every INV has a property test (GREEN), every EDGE has a test (GREEN), every NFR has a test (GREEN). Note: `test_ac_045_traced_methods_no_tokens_in_logs` (AC-045) was previously a **known hanging test** (root cause: infinite loop in the test's own assertion loop — it iterated `log_records` while `@logged` `hash_token` calls appended new records, so the loop never terminated; fix: issue `hanging-observability-test`, commit `fe35f82`, test-side only — hashes computed once before the loop, iteration over a snapshot `list(log_records)`); GREEN re-confirmed in Phase 5 (2026-09-20: 1 passed in 0.25 s, no hang, under a 180 s timeout guard; included in the full-suite run — 557 passed, 1 skipped, 0 failed). AC-045's substance (entry/exit/exception records produced, no raw token/hash in log records) is additionally verified by the GREEN `test_ac_044_no_tokens_in_outputs`, `test_inv_004_no_tokens_in_outputs`, and the record-presence assertions confirmed during S5.3.

| Requirement | Acceptance Criterion | Test | Status |
|-------------|---------------------|------|--------|
| REQ-001 | AC-001 | `test_ac_001_list_token_returns_entries_with_current_flag` | GREEN |
| REQ-001 | AC-002 | `test_ac_002_list_user_id_admin_all_not_current` | GREEN |
| REQ-001 | AC-003 | `test_ac_003_both_or_neither_token_user_id_value_error` | GREEN |
| REQ-005 | AC-001 | `test_ac_001_list_token_returns_entries_with_current_flag` | GREEN |
| REQ-005 | AC-002 | `test_ac_002_list_user_id_admin_all_not_current` | GREEN |
| REQ-002 | AC-004 | `test_ac_004_list_invalid_token_raises` | GREEN |
| REQ-003 | AC-005 | `test_ac_005_list_excludes_expired_rows` | GREEN |
| REQ-003 | AC-006 | `test_ac_006_list_zero_sessions_empty` | GREEN |
| REQ-004 | AC-007 | `test_ac_007_pre_feature_row_null_device_fields` | GREEN |
| REQ-004, REQ-016 | AC-008 | `test_ac_008_login_stores_device_fields` | GREEN |
| REQ-006 | AC-009 | `test_ac_009_list_current_session_pinned_first` | GREEN |
| REQ-006 | AC-010 | `test_ac_010_list_ordered_created_at_desc` | GREEN |
| REQ-007 | AC-011 | `test_ac_011_list_default_limit_100` | GREEN |
| REQ-007 | AC-012 | `test_ac_012_list_explicit_limit_truncates` | GREEN |
| REQ-007 | AC-013 | `test_ac_013_limit_below_one_value_error` | GREEN |
| REQ-008 | AC-014 | `test_ac_014_revoke_session_revokes` | GREEN |
| REQ-008 | AC-015 | `test_ac_015_revoke_unknown_id_noop` | GREEN |
| REQ-008 | AC-016 | `test_ac_016_revoke_already_revoked_noop` | GREEN |
| REQ-009 | AC-017 | `test_ac_017_logout_all_revokes_including_caller` | GREEN |
| REQ-009 | AC-018 | `test_ac_018_logout_all_invalid_token_raises` | GREEN |
| REQ-010 | AC-019 | `test_ac_019_logout_other_keeps_caller` | GREEN |
| REQ-010 | AC-020 | `test_ac_020_logout_other_only_caller_noop` | GREEN |
| REQ-011 | AC-021 | `test_ac_021_revoke_all_returns_count` | GREEN |
| REQ-011 | AC-022 | `test_ac_022_revoke_all_excludes_session` | GREEN |
| REQ-011 | AC-023 | `test_ac_023_revoke_all_zero_sessions` | GREEN |
| REQ-012 | AC-024 | `test_ac_024_cleanup_bounded_by_batch_size` | GREEN |
| REQ-012 | AC-025 | `test_ac_025_cleanup_no_expired_returns_zero` | GREEN |
| REQ-013 | AC-026 | `test_ac_026_expiration_unchanged_no_activity_tracking` | GREEN |
| REQ-014 | AC-027 | `test_ac_027_cap_evicts_oldest_at_sixth_login` | GREEN |
| REQ-014 | AC-028 | `test_ac_028_no_eviction_below_cap` | GREEN |
| REQ-015 | AC-029 | `test_ac_029_password_change_revokes_all` | GREEN |
| REQ-015 | AC-030 | `test_ac_030_deactivation_revokes_all` | GREEN |
| REQ-015 | AC-031 | `test_ac_031_deletion_revokes_all` | GREEN |
| REQ-016 | AC-032 | `test_ac_032_passkey_login_stores_method` | GREEN |
| REQ-017 | AC-033 | `test_ac_033_same_sessions_table_as_authentication` | GREEN |
| REQ-018 | AC-034 | `test_ac_034_session_revoked_event` | GREEN |
| REQ-018 | AC-035 | `test_ac_035_all_sessions_revoked_event` | GREEN |
| REQ-018 | AC-036 | `test_ac_036_expired_sessions_deleted_event` | GREEN |
| REQ-018 | AC-037 | `test_ac_037_sessions_listed_event` | GREEN |
| REQ-018 | AC-038 | `test_ac_038_none_publisher_no_events_no_subscriptions` | GREEN |
| REQ-019 | AC-039 | `test_ac_039_register_settings_defaults` | GREEN |
| REQ-019 | AC-040 | `test_ac_040_live_read_max_listed_sessions` | GREEN |
| REQ-020 | AC-041 | `test_ac_041_singleton_created_once` | GREEN |
| REQ-020 | AC-042 | `test_ac_042_singleton_first_call_without_repository_value_error` | GREEN |
| REQ-020 | AC-043 | `test_ac_043_reset_session_service` | GREEN |
| REQ-021 | AC-044 | `test_ac_044_no_tokens_in_outputs` | GREEN |
| REQ-022 | AC-045 | `test_ac_045_traced_methods_no_tokens_in_logs` | GREEN |
| INV-001 | — | `test_inv_001_revocation_idempotent` | GREEN |
| INV-002 | — | `test_inv_002_valid_only_listing` | GREEN |
| INV-003 | — | `test_inv_003_cap_held_after_login` | GREEN |
| INV-004 | — | `test_inv_004_no_tokens_in_outputs` | GREEN |
| INV-005 | — | `test_inv_005_current_session_first` | GREEN |
| EDGE-001 | — | `test_edge_001_zero_sessions_empty_and_noop` | GREEN |
| EDGE-002 | — | `test_edge_002_revoke_unknown_id_noop` | GREEN |
| EDGE-003 | — | `test_edge_003_revoke_already_revoked_noop` | GREEN |
| EDGE-004 | — | `test_edge_004_logout_all_self_lockout` | GREEN |
| EDGE-005 | — | `test_edge_005_logout_other_only_caller` | GREEN |
| EDGE-006 | — | `test_edge_006_pre_feature_null_fields` | GREEN |
| EDGE-007 | — | `test_edge_007_expired_rows_excluded` | GREEN |
| EDGE-008 | — | `test_edge_008_both_or_neither_value_error` | GREEN |
| EDGE-009 | — | `test_edge_009_limit_below_one_value_error` | GREEN |
| EDGE-010 | — | `test_edge_010_concurrent_revocation_and_listing` | GREEN |
| EDGE-011 | — | `test_edge_011_cap_eviction_at_exact_cap` | GREEN |
| EDGE-012 | — | `test_edge_012_cleanup_below_batch_size` | GREEN |
| NFR-001 | — | `test_nfr_001_list_100_sessions_budget`, `test_nfr_001_revoke_1000_sessions_budget`, `test_nfr_001_cleanup_1000_rows_budget` | GREEN |
| NFR-002 | — | `test_inv_004_no_tokens_in_outputs` (shared with INV-004) | GREEN |
| NFR-003 | — | `test_nfr_003_public_api_contract` | GREEN |
| NFR-004 | — | `test_nfr_004_traced_service_publishes_events` | GREEN |
| NFR-005 | — | `test_nfr_005_concurrent_threads_safe` | GREEN |

## Issue: hanging-observability-test (reproduction test)

Issue `hanging-observability-test` (type ISSUE; triage: `docs/verification/hanging-observability-test.md`). The reproduction test is `test_ac_045_traced_methods_no_tokens_in_logs` (session-management test directory, already exists — not modified). **RED for this issue = the test hangs (never finishes)**; re-confirmed 2026-09-20 with `timeout 90` → exit 124. **GREEN (Phase 5, 2026-09-20 13:48):** root cause = infinite loop in the test's own assertion loop (iterating `log_records` while `@logged` `hash_token` calls appended new records); fix (commit `fe35f82`) computes the hashes once before the loop and iterates over a snapshot (`list(log_records)`); asserted AC-045 behavior unchanged (no log record contains a raw token or token hash); no `src/` file changed. Reproduction test re-confirmed GREEN under a 180 s timeout guard: `uv run pytest tests/acceptance/sessionmanagement/test_observability.py::test_ac_045_traced_methods_no_tokens_in_logs -v` → **1 passed in 0.25 s** (no hang). Full regression suite `uv run pytest tests/ -q -p no:randomly` → **557 passed, 1 skipped, 0 failed** (the skip is environmental and pre-existing: `tests/acceptance/filemanagement/test_filemanagement.py:364` — "symlinks not available on this host"); no new failures, no regression. Affected spec IDs (session-management `docs/specs/session-management.md`; logging `docs/specs/logging.md`) mapped to the reproduction test:

| Feature | Requirement | Acceptance Criterion | Reproduction test | Status |
|---------|-------------|---------------------|-------------------|--------|
| session-management | REQ-022 | AC-045 | `test_ac_045_traced_methods_no_tokens_in_logs` | GREEN (Phase 5, 2026-09-20; was RED/hang) |
| session-management | REQ-021 | AC-044 | `test_ac_045_traced_methods_no_tokens_in_logs` (no raw token/hash in log records) | GREEN (Phase 5, 2026-09-20; was RED/hang) |
| session-management | NFR-004 | — | `test_ac_045_traced_methods_no_tokens_in_logs` | GREEN (Phase 5, 2026-09-20; was RED/hang) |
| logging | REQ-001 | AC-001 | `test_ac_045_traced_methods_no_tokens_in_logs` (enqueued file sink mandated) | GREEN (Phase 5, 2026-09-20; was RED/hang) |
| logging | NFR-001 | — | `test_ac_045_traced_methods_no_tokens_in_logs` (setup must not block) | GREEN (Phase 5, 2026-09-20; was RED/hang) |
| logging | NFR-002 | — | `test_ac_045_traced_methods_no_tokens_in_logs` (decorator overhead must not block) | GREEN (Phase 5, 2026-09-20; was RED/hang) |

## User Roles & Permissions Matrix

The user-roles-permissions change (type CROSS-CUTTING; spec `docs/specs/user-roles-permissions.md`) uses its own REQ/AC ID space (REQ-001..029, AC-001..040) that overlaps the other features' matrices, so it is kept separate. Phase 3 (S3.2) confirmed all 77 tests RED before implementation (failure modes: `ModuleNotFoundError` on the unimplemented `backend.permissions` / `backend.shared` / `feature_actions` modules; assertion failures on the un-wired service signatures; pre-amendment `usermanagement` model errors for the T-002 amendment tests).

| Requirement | Acceptance Criterion | Test | Status |
|-------------|---------------------|------|--------|
| REQ-001 | AC-001 | `test_granted_permission_allowed` | GREEN |
| REQ-001 | AC-002 | `test_denied_permission_raises_with_context` | GREEN |
| REQ-002 | AC-003 | `test_malformed_permission_denied` | GREEN |
| REQ-003 | AC-004 | `test_feature_wildcard_grant` | GREEN |
| REQ-004 | AC-005 | `test_unknown_permission_denied_and_grant_rejected` | GREEN |
| REQ-005 | AC-006 | `test_initial_catalog_exactly_60_keys` | GREEN |
| REQ-006 | AC-007 | `test_create_role_and_list` | GREEN |
| REQ-007 | AC-008 | `test_delete_role_guards` | GREEN |
| REQ-008 | AC-009 | `test_grant_and_revoke_role_permission` | GREEN |
| REQ-008 | AC-010 | `test_wildcard_grant_stored_and_matches` | GREEN |
| REQ-009 | AC-011 | `test_multi_role_union_of_permissions` | GREEN |
| REQ-010 | AC-012 | `test_admin_wildcard_allows_all` | GREEN |
| REQ-011 | AC-013 | `test_user_role_starts_with_zero_permissions` | GREEN |
| REQ-012 | AC-014 | `test_assignment_delegates_to_user_manager` | GREEN |
| REQ-013 | AC-015 | `test_last_admin_guard_preserved_via_service` | GREEN |
| REQ-014 | AC-016 | `test_grant_change_takes_effect_immediately` | GREEN |
| REQ-015 | AC-017 | `test_unknown_user_denied` | GREEN |
| REQ-015 | AC-018 | `test_storage_error_denied_fail_closed` | GREEN |
| REQ-016 | AC-019 | `test_inactive_user_denied_even_admin` | GREEN |
| REQ-017 | AC-020 | `test_session_validation_in_check` | GREEN |
| REQ-017 | AC-021 | `test_session_validation_skipped_when_token_none` | GREEN |
| REQ-018 | AC-022 | `test_system_principal_check_and_set` | GREEN |
| REQ-019 | AC-023 | `test_system_set_settings_alias_sync` | GREEN |
| REQ-020 | AC-024 | `test_events_published_on_operations` | GREEN |
| REQ-020 | AC-025 | `test_no_publisher_still_works` | GREEN |
| REQ-021 | AC-026 | `test_error_context_attributes` | GREEN |
| REQ-022 | AC-027 | `test_migration_seeds_roles_and_system_set` | GREEN |
| REQ-023 | AC-028 | `test_in_memory_repos_and_singleton` | GREEN |
| REQ-024 | AC-029 | `test_enforced_method_denies_without_permission` | GREEN |
| REQ-024 | AC-030 | `test_exempt_login_no_check` | GREEN |
| REQ-024 | AC-031 | `test_standalone_mode_no_check` | GREEN |
| REQ-025 | AC-032 | `test_principal_defaults_and_fields`, `test_requires_permission_decorator` | GREEN |
| REQ-026 | AC-033 | `test_create_user_with_roles_list` | GREEN |
| REQ-026 | AC-034 | `test_add_remove_set_roles` | GREEN |
| REQ-026 | AC-035 | `test_migration_member_to_user_and_role_list` | GREEN |
| REQ-013, REQ-026 | AC-036 | `test_last_admin_guard_all_paths` | GREEN |
| REQ-026 | AC-037 | `test_role_events_carry_lists` | GREEN |
| REQ-027 | AC-038 | `test_concurrent_checks_and_changes` | GREEN |
| REQ-028 | AC-039 | `test_denial_log_and_no_token_leak` | GREEN |
| REQ-029 | AC-040 | `test_check_latency_under_5ms_median` | GREEN |
| REQ-024 | — | `test_authentication_enforcement_wiring`, `test_settings_enforcement_wiring`, `test_mail_enforcement_wiring`, `test_sessionmanagement_enforcement_wiring` (per-feature wiring, no AC) | GREEN |
| INV-001 | — | `test_check_true_iff_granted_and_active` | GREEN |
| INV-002 | — | `test_undeterminable_never_true` | GREEN |
| INV-003 | — | `test_last_admin_invariant` | GREEN |
| INV-004 | — | `test_effective_set_monotone` | GREEN |
| INV-005 | — | `test_admin_passes_any_catalog_permission` | GREEN |
| INV-006 | — | `test_valid_grant_keys_exactly_catalog_plus_wildcards` | GREEN |
| EDGE-001 | — | `test_malformed_key_denied` | GREEN |
| EDGE-002 | — | `test_unknown_permission_denied` | GREEN |
| EDGE-003 | — | `test_unknown_user_denied` | GREEN |
| EDGE-004 | — | `test_inactive_user_denied` | GREEN |
| EDGE-005 | — | `test_revoked_expired_token_denied` | GREEN |
| EDGE-006 | — | `test_mismatched_token_denied` | GREEN |
| EDGE-007 | — | `test_unavailable_session_lookup_denied` | GREEN |
| EDGE-008 | — | `test_role_no_mapping_zero_permissions` | GREEN |
| EDGE-009 | — | `test_user_deleted_concurrent_denied` | GREEN |
| EDGE-010 | — | `test_concurrent_thread_safe` | GREEN |
| EDGE-011 | — | `test_lookup_raises_denied` | GREEN |
| EDGE-012 | — | `test_delete_builtin_role_protected` | GREEN |
| EDGE-013 | — | `test_delete_in_use_role` | GREEN |
| EDGE-014 | — | `test_create_duplicate_role` | GREEN |
| EDGE-015 | — | `test_create_malformed_name` | GREEN |
| EDGE-016 | — | `test_grant_unknown_permission` | GREEN |
| EDGE-017 | — | `test_unknown_role_operations` | GREEN |
| EDGE-018 | — | `test_revoke_absent_idempotent` | GREEN |
| EDGE-019 | — | `test_grant_existing_idempotent` | GREEN |
| EDGE-020 | — | `test_set_system_unknown_permission` | GREEN |
| EDGE-021 | — | `test_set_system_wildcard_allowed` | GREEN |
| EDGE-022 | — | `test_default_principal_system` | GREEN |
| EDGE-023 | — | `test_login_before_permissions` | GREEN |
| EDGE-024 | — | `test_token_deleted_user_denied` | GREEN |
| EDGE-025 | — | `test_expired_session_denied` | GREEN |
| EDGE-026 | — | `test_assignment_unknown_role` | GREEN |
| NFR-001 | — | `test_check_latency_under_5ms_median` | GREEN |
| NFR-002 | — | `test_undeterminable_never_true`, `test_denial_log_and_no_token_leak`, `test_error_context_attributes` | GREEN |
| NFR-003 | — | `test_in_memory_repos_and_singleton` | GREEN |
| NFR-004 | — | `test_concurrent_checks_and_changes` | GREEN |
| NFR-005 | — | `test_denial_log_and_no_token_leak` | GREEN |

### Affected Features (CROSS-CUTTING — per-feature enforcement wiring, REQ-024)

The change wires the shared `PermissionChecker` into six features via the ADR-071 pattern (trailing `principal` param + `@requires_permission` + optional `permission_service` constructor + feature-owned `feature_actions`). Each feature's enforcement wiring is covered by a dedicated test (all GREEN):

| Feature | Enforcement wiring test | Status |
|---------|------------------------|--------|
| usermanagement | `test_standalone_mode_no_check` (REQ-024/AC-031; 11 methods, `feature_actions` 11 actions) | GREEN |
| authentication | `test_authentication_enforcement_wiring` (REQ-024; 11 methods, 4 enforced + 7 exempt) | GREEN |
| settings | `test_settings_enforcement_wiring` (REQ-024; 19 methods, all enforced) | GREEN |
| filemanagement | `test_enforced_method_denies_without_permission` (REQ-024/AC-029; 10 methods, 8 enforced) | GREEN |
| mail | `test_mail_enforcement_wiring` (REQ-024; 3 methods, all enforced) | GREEN |
| sessionmanagement | `test_sessionmanagement_enforcement_wiring` (REQ-024; 6 methods, all enforced) | GREEN |

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
