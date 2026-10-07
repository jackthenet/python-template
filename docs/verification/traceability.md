# Traceability Matrix

This matrix maintains bidirectional traceability between requirements, acceptance criteria, tests, and implementation.

> **The Status column is a historical gate record** (decision Q-129, convention B): each row records the state observed by the change that wrote it (change name + date are inside the cell), and a later change touches only the REQs/ACs it changes — it never refreshes rows it did not change, so a dated `RED`/`PENDING` row is a legal record of a past gate. What is enforced is **referential integrity** (coverage, dangling IDs, missing tests, undeclared status values), by `uv run python scripts/check_traceability.py` in CI.

## Invariants

- Every normative requirement MUST have one or more executable tests.
- Every acceptance test MUST trace back to a normative requirement.
- Acceptance tests are the authoritative executable representation of externally observable behavior. Unit tests must not replace missing acceptance tests.
- Status values: `PENDING`, `RED`, `GREEN`, `REFACTORED`, `VERIFIED`, `N/A`.

## Matrix

| Requirement | Acceptance Criterion | Test | Status |
|-------------|---------------------|------|--------|
| REQ-001 | AC-001 | `test_ac_001_setup_logger_adds_sinks` (re-derived from `logging.md` v3 AC-001 by structlog-logging T-001: the two managed standard-library sinks and the records they write, replacing the removed backend's handler-count and sink-option assertions); `test_reconfigure_replaces_only_the_managed_sinks`, `test_reconfigure_keeps_foreign_sink`, `test_reconfigure_after_external_removal_of_a_managed_sink` (issue main-ci-green, item E — witnesses re-pointed at the pipeline's own handlers); the "colorized text" clause of the amended AC-001 wording is witnessed by `test_ac_002_console_color_is_selected_only_for_a_terminal_stream` (`tests/unit/logging/test_renderers.py`, structlog-logging S6.1 F-S6.1-01) | GREEN (structlog-logging S5.1 full suite: 760 passed, 1 skipped — re-run after the S5.2 test refactor, 2026-10-07, commits `c5ab5f7` / `de31ea9`; the `test_ac_002_console_color_is_selected_only_for_a_terminal_stream` witness cited above is included in the structlog-logging S4.2 re-entry full-suite run — 761 passed, 1 skipped, 0 failed at `e776c36`, 2026-10-07; earlier: issue main-ci-green Phase 5 S5.1, 2026-10-02) |
| REQ-002 | AC-002 | `test_ac_002_setup_logger_idempotent` (witness re-pointed at the feature logger's managed handlers by structlog-logging T-001; assertion unchanged) | GREEN (structlog-logging S5.1 full suite: 760 passed, 1 skipped — re-run after the S5.2 test refactor, 2026-10-07, commits `c5ab5f7` / `de31ea9`) |
| REQ-002 | AC-003 | `test_ac_003_setup_logger_thread_safe` (victim of the items G/H pollution — assertion unchanged; witness re-pointed at the two managed handlers by structlog-logging T-001) | GREEN (structlog-logging S5.1 full suite: 760 passed, 1 skipped — re-run after the S5.2 test refactor, 2026-10-07, commits `c5ab5f7` / `de31ea9`) |
| REQ-003 | AC-004 | `test_ac_004_intercept_handler_routes_records` (re-derived from `logging.md` v3 AC-004 by structlog-logging T-002: the single root forwarding handler routes the foreign record into both managed sinks with its level and message); `test_reconfigure_keeps_foreign_sink` (item E); autouse `tests/conftest.py::_stdlib_root_logging_restored` (item I — restores the stdlib root handlers the alembic `fileConfig` call replaced; adapted to the pipeline by structlog-logging, EDGE-003) | GREEN (structlog-logging S5.1 full suite: 760 passed, 1 skipped — re-run after the S5.2 test refactor, 2026-10-07, commits `c5ab5f7` / `de31ea9`) |
| REQ-003 | AC-005 | — (AC-005 deleted by the `structlog-logging` amendment, 2026-10-04 — the importlib bootstrap-frame rule only existed for the removed backend; its witness (the intercept-bootstrap case in `tests/unit/logging/test_logging.py`) was deleted in the implementation PR, T-001 commit `fcce934`, spec §11; the case survives as this change's AC-007 `test_ac_007_location_of_emitting_call`) | GREEN (full suite: 727 passed, 1 skipped ×3 runs, zero failures — search S5.1 re-run on base `e8dd2bc`, 2026-10-02, commit `7bbc05a`) — retired by logging.md v3 |
| REQ-004 | AC-006 | `test_ac_006_logged_sync_entry_exit` | GREEN (full suite: 727 passed, 1 skipped ×3 runs, zero failures — search S5.1 re-run on base `e8dd2bc`, 2026-10-02, commit `7bbc05a`) |
| REQ-004 | AC-007 | `test_ac_007_logged_async_entry_exit` | GREEN (full suite: 727 passed, 1 skipped ×3 runs, zero failures — search S5.1 re-run on base `e8dd2bc`, 2026-10-02, commit `7bbc05a`) |
| REQ-004 | AC-008 | `test_ac_008_logged_exception_propagates` | GREEN (full suite: 727 passed, 1 skipped ×3 runs, zero failures — search S5.1 re-run on base `e8dd2bc`, 2026-10-02, commit `7bbc05a`) |
| REQ-005 | AC-009 | `test_ac_009_logged_level_param` | GREEN (full suite: 727 passed, 1 skipped ×3 runs, zero failures — search S5.1 re-run on base `e8dd2bc`, 2026-10-02, commit `7bbc05a`) |
| REQ-005 | AC-010 | `test_ac_010_logged_include_args` | GREEN (full suite: 727 passed, 1 skipped ×3 runs, zero failures — search S5.1 re-run on base `e8dd2bc`, 2026-10-02, commit `7bbc05a`) |
| REQ-006 | AC-011 | `test_ac_011_logged_slow_threshold` | GREEN (full suite: 727 passed, 1 skipped ×3 runs, zero failures — search S5.1 re-run on base `e8dd2bc`, 2026-10-02, commit `7bbc05a`) |
| REQ-007 | AC-012 | `test_ac_012_logged_class_public_method` | GREEN (full suite: 727 passed, 1 skipped ×3 runs, zero failures — search S5.1 re-run on base `e8dd2bc`, 2026-10-02, commit `7bbc05a`) |
| REQ-007 | AC-013 | `test_ac_013_logged_class_private_method` | GREEN (full suite: 727 passed, 1 skipped ×3 runs, zero failures — search S5.1 re-run on base `e8dd2bc`, 2026-10-02, commit `7bbc05a`) |
| REQ-008 | AC-014 | `test_ac_014_get_settings_defaults` | GREEN (full suite: 727 passed, 1 skipped ×3 runs, zero failures — search S5.1 re-run on base `e8dd2bc`, 2026-10-02, commit `7bbc05a`) |
| REQ-009 | AC-015 | `test_ac_015_obsolete_module_deleted` | GREEN (full suite: 727 passed, 1 skipped ×3 runs, zero failures — search S5.1 re-run on base `e8dd2bc`, 2026-10-02, commit `7bbc05a`) |
| INV-001 | — | `test_inv_001_concurrent_setup_logger_sinks` (re-derived from `logging.md` v3 INV-001 by structlog-logging T-002: exactly one console handler + one file handler owned by the feature logger, replacing the removed backend's handler table); `test_reconfigure_replaces_only_the_managed_sinks`, `test_reconfigure_after_external_removal_of_a_managed_sink` (item E) | GREEN (structlog-logging S5.1 full suite: 760 passed, 1 skipped — re-run after the S5.2 test refactor, 2026-10-07, commits `c5ab5f7` / `de31ea9`) |
| INV-002 | — | `test_inv_002_elapsed_time_non_negative` | GREEN (full suite: 727 passed, 1 skipped ×3 runs, zero failures — search S5.1 re-run on base `e8dd2bc`, 2026-10-02, commit `7bbc05a`) |
| INV-003 | — | `test_inv_003_exception_propagates_unchanged` | GREEN (full suite: 727 passed, 1 skipped ×3 runs, zero failures — search S5.1 re-run on base `e8dd2bc`, 2026-10-02, commit `7bbc05a`) |
| EDGE-001 | — | `test_edge_001_log_file_parent_created` | GREEN (full suite: 727 passed, 1 skipped ×3 runs, zero failures — search S5.1 re-run on base `e8dd2bc`, 2026-10-02, commit `7bbc05a`) |
| EDGE-002 | — | `test_edge_002_logged_no_args` | GREEN (full suite: 727 passed, 1 skipped ×3 runs, zero failures — search S5.1 re-run on base `e8dd2bc`, 2026-10-02, commit `7bbc05a`) |
| EDGE-003 | — | `test_edge_003_logged_nonexistent_setting` | GREEN (full suite: 727 passed, 1 skipped ×3 runs, zero failures — search S5.1 re-run on base `e8dd2bc`, 2026-10-02, commit `7bbc05a`) |
| EDGE-004 | — | `test_edge_004_logged_class_no_public_methods` | GREEN (full suite: 727 passed, 1 skipped ×3 runs, zero failures — search S5.1 re-run on base `e8dd2bc`, 2026-10-02, commit `7bbc05a`) |
| EDGE-005 | — | — (EDGE-005 deleted by the `structlog-logging` amendment, 2026-10-04 — restated in capability terms as EDGE-004 of `docs/specs/structlog-logging.md`; its witness (the unknown-level case in `tests/unit/logging/test_logging_edges.py`) was deleted in the implementation PR, T-001 commit `fcce934`, spec §11, and the case is witnessed by `test_edge_004_unknown_numeric_level`) | GREEN (full suite: 727 passed, 1 skipped ×3 runs, zero failures — search S5.1 re-run on base `e8dd2bc`, 2026-10-02, commit `7bbc05a`) — retired by logging.md v3 |
| NFR-001 | — | `test_nfr_001_setup_time_budget` (budget amended to 25 ms by structlog-logging NFR-001 / `logging.md` v3) | GREEN (structlog-logging S5.1 full suite: 760 passed, 1 skipped — re-run after the S5.2 test refactor, 2026-10-07, commits `c5ab5f7` / `de31ea9`) |
| NFR-002 | — | `test_nfr_002_decorator_overhead_budget` (amended by structlog-logging NFR-002 / `logging.md` v3: measured with both managed sinks active at DEBUG instead of the removed backend's logging disabled) | GREEN (structlog-logging S5.1 full suite: 760 passed, 1 skipped — re-run after the S5.2 test refactor, 2026-10-07, commits `c5ab5f7` / `de31ea9`) |
| NFR-003 | — | `test_nfr_003_diagnose_false` (emission re-pointed at the feature's own entry point by structlog-logging T-002; the no-local-value assertion is unchanged) | GREEN (structlog-logging S5.1 full suite: 760 passed, 1 skipped — re-run after the S5.2 test refactor, 2026-10-07, commits `c5ab5f7` / `de31ea9`) |
| NFR-004 | — | `test_nfr_004_backward_compatible_api` (amended by `logging.md` v3 NFR-004: the compatibility promise covers the import path and names, and asserts the reduced `@logged` parameter set — `context_getter` / `depth` gone, `setup_logger()` still callable with no arguments) | GREEN (structlog-logging S5.1 full suite: 760 passed, 1 skipped — re-run after the S5.2 test refactor, 2026-10-07, commits `c5ab5f7` / `de31ea9`) |
| — | — | `test_stdlib_decorator_pipeline` (integration — renamed from test_stdlib_loguru_decorator_pipeline by structlog-logging S6.1 finding F-S6.1-06, the name having outlived the backend; the loguru line is retired with the backend and replaced by a foreign-logger record forwarded through the root handler, structlog-logging T-002) | GREEN (structlog-logging S5.1 full suite: 760 passed, 1 skipped — re-run after the S5.2 test refactor, 2026-10-07, commits `c5ab5f7` / `de31ea9`; re-run after the S6.1 findings resolution, 2026-10-07) |

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
| REQ-005 | AC-008 | `test_ac_008_shutdown_drains`; `tests/eventbus_test_helpers.py::isolated_event_bus` (issue main-ci-green item H — the helper now **parks** the shared singleton instead of resetting/shutting it down, so a later test's publish is no longer silently dropped) | GREEN |
| REQ-005 | AC-009 | `test_ac_009_shutdown_idempotent` | GREEN |
| REQ-005 | AC-010 | `test_ac_010_context_manager` | GREEN |
| REQ-006 | AC-011 | `test_ac_011_singleton` | GREEN |
| REQ-007 | AC-012 | `test_ac_012_bounded_queue_drop` | GREEN |
| INV-001 | — | `test_inv_001_exactly_once` | GREEN |
| INV-002 | — | `test_inv_002_isolation`; `isolated_event_bus` (item H: instance isolation without shutting down the shared bus) | GREEN |
| INV-003 | — | `test_inv_003_queue_bounded` | GREEN |
| INV-004 | — | `test_inv_004_handler_order` | GREEN |
| EDGE-001 | — | `test_edge_001_lazy_start` | GREEN |
| EDGE-002 | — | `test_edge_002_drop_on_full` | GREEN |
| EDGE-003 | — | `test_edge_003_non_callable_handler` | GREEN |
| EDGE-004 | — | `test_edge_004_non_class_event` | GREEN |
| EDGE-005 | — | `test_edge_005_unsubscribe_not_subscribed` | GREEN |
| EDGE-006 | — | `test_edge_006_dedup` | GREEN |
| EDGE-007 | — | `test_edge_007_publish_after_shutdown` (the early-return-on-shut-down behaviour that made the item-H pollution silent); `isolated_event_bus` | GREEN |
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
| REQ-010 | AC-014 | `test_ac_014_unknown_key`; `test_yaml_value_roundtrip_nel` (issue main-ci-green item A — `YamlValueRepository` round-trips U+0085) | GREEN |
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
| REQ-022 | AC-030 | `test_ac_030_yaml_file_written`; `test_yaml_template_roundtrip_nel` (issue main-ci-green item A) | GREEN |
| REQ-021, REQ-022 | AC-031 | `test_ac_031_persistence_across_instances`; `test_yaml_template_roundtrip_nel` (item A) | GREEN |
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
| INV-009 | — | `test_inv_009_yaml_roundtrip` (property; alphabet widened to always generate U+0085); `test_yaml_template_roundtrip_nel` (issue main-ci-green item A) | GREEN (Phase 5 S5.1, 2026-10-02; was RED) |
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
| INV-003 | — | `test_inv_003_last_admin_invariant` (`@settings(deadline=1000)`, measured — issue main-ci-green items B/H) | GREEN |
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
| REQ-005 | AC-005 | `test_module_functions_traced` (structlog-logging: a `setup_logger()` re-run added to the teardown so the inventory's own setup cannot leak the default-level pipeline into later tests; assertions unchanged) | GREEN (structlog-logging S5.1 full suite: 760 passed, 1 skipped — re-run after the S5.2 test refactor, 2026-10-07, commits `c5ab5f7` / `de31ea9`) |
| REQ-006 | AC-006 | `test_secret_handler_args_not_logged` | GREEN |
| REQ-007 | AC-007 | `test_traced_classes_have_concrete_threshold` | GREEN |
| REQ-008 | AC-008 | `test_semantic_log_levels` | GREEN |
| REQ-009 | AC-009 | `test_traced_class_docstrings_mention_tracing` | GREEN |
| REQ-010 | AC-010 | `test_ac_009_statements_go_through_get_logger` — restated v2 wording (all existing one-off statements are kept as statements, written through the shared logging feature's exported logger; no feature module imports a logging backend directly); replaces the retired direct-backend witness (the deleted file `tests/acceptance/logging_coverage/test_direct_loguru_kept.py`, removed by structlog-logging T-006 per spec §11) | GREEN (structlog-logging S5.1 full suite: 760 passed, 1 skipped, 2026-10-07, commits `c5ab5f7` / `de31ea9`; re-pointed by T-006 — earlier: logging-coverage Phase 5) |
| REQ-011 | AC-011 | `test_entrypoint_calls_setup_logger_once` | GREEN |
| REQ-012 | AC-012 | `test_new_public_classes_traced_by_default` | GREEN |
| REQ-013 | AC-013 | `test_sink_failure_does_not_interrupt` (structlog-logging T-002: the failing sink is now a handler on the pipeline's own logger — `failing_sink_attached()` — in place of the removed backend's `logger.add(..., catch=True)`; assertion unchanged) | GREEN (structlog-logging S5.1 full suite: 760 passed, 1 skipped — re-run after the S5.2 test refactor, 2026-10-07, commits `c5ab5f7` / `de31ea9`) |
| REQ-014 | AC-014 | `test_slow_call_logs_warning_not_interrupted` | GREEN |
| REQ-015 | AC-015 | `test_no_raw_secrets_in_any_log_record` | GREEN |
| REQ-016 | AC-016 | `test_tracing_does_not_change_behavior` | GREEN |
| INV-001 | — | `test_one_entry_one_exit_per_call` | GREEN |
| INV-002 | — | `test_secret_args_never_logged` | GREEN |
| INV-003 | — | `test_elapsed_ms_non_negative` | GREEN |
| INV-004 | — | `test_tracing_never_interrupts_call` (structlog-logging T-002: failing sink attached to the pipeline's own logger; invariant, strategies and assertions unchanged) | GREEN (structlog-logging S5.1 full suite: 760 passed, 1 skipped — re-run after the S5.2 test refactor, 2026-10-07, commits `c5ab5f7` / `de31ea9`) |
| EDGE-001 | — | `test_slow_threshold_exceeded` | GREEN |
| EDGE-002 | — | `test_sink_failure_graceful` (structlog-logging T-002: failing sink attached to the pipeline's own logger instead of the removed backend; assertion unchanged) | GREEN (structlog-logging S5.1 full suite: 760 passed, 1 skipped — re-run after the S5.2 test refactor, 2026-10-07, commits `c5ab5f7` / `de31ea9`) |
| EDGE-003 | — | `test_abc_subclass_traced` | GREEN |
| EDGE-004 | — | `test_traced_method_exception_propagates` | GREEN |
| EDGE-005 | — | `test_setup_logger_idempotent` (`tests/unit/logging_coverage/test_edge_cases.py`; structlog-logging T-002: the witness is the pipeline's own two managed sinks, not the removed backend's handler table — strengthened, not weakened) | GREEN (structlog-logging S5.1 full suite: 760 passed, 1 skipped — re-run after the S5.2 test refactor, 2026-10-07, commits `c5ab5f7` / `de31ea9`) |
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
| REQ-001 | AC-001 | `test_register_settings_registers` | GREEN (full suite: 727 passed, 1 skipped ×3 runs, zero failures — search S5.1 re-run on base `e8dd2bc`, 2026-10-02, commit `7bbc05a`) |
| REQ-001 | AC-002 | `test_no_import_side_effects` | GREEN (full suite: 727 passed, 1 skipped ×3 runs, zero failures — search S5.1 re-run on base `e8dd2bc`, 2026-10-02, commit `7bbc05a`) |
| REQ-002 | AC-003 | `test_main_wires_all_features` | GREEN (full suite: 727 passed, 1 skipped ×3 runs, zero failures — search S5.1 re-run on base `e8dd2bc`, 2026-10-02, commit `7bbc05a`) |
| REQ-003 | AC-004 | `test_set_value_affects_running_feature` | GREEN (full suite: 727 passed, 1 skipped ×3 runs, zero failures — search S5.1 re-run on base `e8dd2bc`, 2026-10-02, commit `7bbc05a`) |
| REQ-004 | AC-005 | `test_constructor_default_registry_value` | GREEN (full suite: 727 passed, 1 skipped ×3 runs, zero failures — search S5.1 re-run on base `e8dd2bc`, 2026-10-02, commit `7bbc05a`) |
| REQ-005 | AC-006 | `test_unregistered_key_fallback` | GREEN (full suite: 727 passed, 1 skipped ×3 runs, zero failures — search S5.1 re-run on base `e8dd2bc`, 2026-10-02, commit `7bbc05a`) |
| REQ-006 | AC-007 | `test_list_definition_accepted` | GREEN (full suite: 727 passed, 1 skipped ×3 runs, zero failures — search S5.1 re-run on base `e8dd2bc`, 2026-10-02, commit `7bbc05a`) |
| REQ-007 | AC-008 | `test_list_value_validation` | GREEN (full suite: 727 passed, 1 skipped ×3 runs, zero failures — search S5.1 re-run on base `e8dd2bc`, 2026-10-02, commit `7bbc05a`) |
| REQ-007 | AC-009 | `test_list_min_items` | GREEN (full suite: 727 passed, 1 skipped ×3 runs, zero failures — search S5.1 re-run on base `e8dd2bc`, 2026-10-02, commit `7bbc05a`) |
| REQ-007 | AC-010 | `test_list_no_duplicates` | GREEN (full suite: 727 passed, 1 skipped ×3 runs, zero failures — search S5.1 re-run on base `e8dd2bc`, 2026-10-02, commit `7bbc05a`) |
| REQ-008 | AC-011 | `test_list_min_gt_max_rejected` | GREEN (full suite: 727 passed, 1 skipped ×3 runs, zero failures — search S5.1 re-run on base `e8dd2bc`, 2026-10-02, commit `7bbc05a`) |
| REQ-008 | AC-012 | `test_list_spec_on_text_rejected` | GREEN (full suite: 727 passed, 1 skipped ×3 runs, zero failures — search S5.1 re-run on base `e8dd2bc`, 2026-10-02, commit `7bbc05a`) |
| REQ-009 | AC-013 | `test_set_value_persists` | GREEN (full suite: 727 passed, 1 skipped ×3 runs, zero failures — search S5.1 re-run on base `e8dd2bc`, 2026-10-02, commit `7bbc05a`) |
| REQ-010 | AC-014 | `test_yaml_value_repository`; `test_yaml_value_roundtrip_nel` (issue main-ci-green item A) | GREEN (full suite: 727 passed, 1 skipped ×3 runs, zero failures — search S5.1 re-run on base `e8dd2bc`, 2026-10-02, commit `7bbc05a`) |
| REQ-011 | AC-015 | `test_persisted_precedence` | GREEN (full suite: 727 passed, 1 skipped ×3 runs, zero failures — search S5.1 re-run on base `e8dd2bc`, 2026-10-02, commit `7bbc05a`) |
| REQ-012 | AC-016 | `test_guarded_read_no_side_effect` | GREEN (full suite: 727 passed, 1 skipped ×3 runs, zero failures — search S5.1 re-run on base `e8dd2bc`, 2026-10-02, commit `7bbc05a`) |
| REQ-013 | AC-017 | `test_eventbus_no_registry_default` | GREEN (full suite: 727 passed, 1 skipped ×3 runs, zero failures — search S5.1 re-run on base `e8dd2bc`, 2026-10-02, commit `7bbc05a`) |
| REQ-013 | AC-018 | `test_eventbus_registry_value` | GREEN (full suite: 727 passed, 1 skipped ×3 runs, zero failures — search S5.1 re-run on base `e8dd2bc`, 2026-10-02, commit `7bbc05a`) |
| REQ-014 | AC-019 | `test_setup_logger_reads_registry` (re-derived from settings-coverage v2 by structlog-logging T-003); `tests/unit/logging/test_logging_sink_ownership.py` (item E — the reconfigure touches only the sinks it owns; witnesses re-pointed at the pipeline's handlers) | GREEN (structlog-logging S5.1 full suite: 760 passed, 1 skipped — re-run after the S5.2 test refactor, 2026-10-07, commits `c5ab5f7` / `de31ea9`; RED at S3.2, 2026-10-06) |
| REQ-015 | AC-020 | `test_sink_reconfigured_on_change` (re-derived from settings-coverage v2 by structlog-logging T-003: the live reconfigure mutates the managed handlers in place, no subprocess probe); `tests/settings_test_helpers.py::set_value_settled` (item G — awaits the write's dispatch) and `isolated_event_bus` (item H — the publish is no longer dropped by a shut-down bus) | GREEN (structlog-logging S5.1 full suite: 760 passed, 1 skipped — re-run after the S5.2 test refactor, 2026-10-07, commits `c5ab5f7` / `de31ea9`; RED at S3.2, 2026-10-06) |
| REQ-016 | AC-021 | `test_logging_stub_removed` (re-derived from settings-coverage v2 by structlog-logging T-003: `Settings` must be a plain container of the five `logging.*` values, not a validation model — and the values must come from the live registry) | GREEN (structlog-logging S5.1 full suite: 760 passed, 1 skipped — re-run after the S5.2 test refactor, 2026-10-07, commits `c5ab5f7` / `de31ea9`; already GREEN at S3.2, 2026-10-06 — assertion strengthened, not weakened) |
| REQ-017 | AC-022 | `test_key_prefix` | GREEN (full suite: 727 passed, 1 skipped ×3 runs, zero failures — search S5.1 re-run on base `e8dd2bc`, 2026-10-02, commit `7bbc05a`) |
| REQ-018 | AC-023 | `test_category_group` | GREEN (full suite: 727 passed, 1 skipped ×3 runs, zero failures — search S5.1 re-run on base `e8dd2bc`, 2026-10-02, commit `7bbc05a`) |
| REQ-019 | AC-024 | `test_inventory_matches` | GREEN (full suite: 727 passed, 1 skipped ×3 runs, zero failures — search S5.1 re-run on base `e8dd2bc`, 2026-10-02, commit `7bbc05a`) |
| REQ-020 | AC-025 | `test_tracing` | GREEN (full suite: 727 passed, 1 skipped ×3 runs, zero failures — search S5.1 re-run on base `e8dd2bc`, 2026-10-02, commit `7bbc05a`) |
| REQ-021 | AC-026 | `test_no_env_vars` | GREEN (full suite: 727 passed, 1 skipped ×3 runs, zero failures — search S5.1 re-run on base `e8dd2bc`, 2026-10-02, commit `7bbc05a`) |
| REQ-022 | AC-027 | `test_settings_registers_nothing` | GREEN (full suite: 727 passed, 1 skipped ×3 runs, zero failures — search S5.1 re-run on base `e8dd2bc`, 2026-10-02, commit `7bbc05a`) |
| INV-001 | — | `test_get_value_valid_for_kind` | GREEN (full suite: 727 passed, 1 skipped ×3 runs, zero failures — search S5.1 re-run on base `e8dd2bc`, 2026-10-02, commit `7bbc05a`) |
| INV-002 | — | `test_list_round_trip`; `test_yaml_value_roundtrip_nel` (issue main-ci-green item A) | RED (reproduction GREEN after the fix; row status predates the fix) |
| INV-003 | — | `test_live_read_after_set` | GREEN (full suite: 727 passed, 1 skipped ×3 runs, zero failures — search S5.1 re-run on base `e8dd2bc`, 2026-10-02, commit `7bbc05a`) |
| INV-004 | — | `test_register_idempotent_fresh` | GREEN (full suite: 727 passed, 1 skipped ×3 runs, zero failures — search S5.1 re-run on base `e8dd2bc`, 2026-10-02, commit `7bbc05a`) |
| INV-005 | — | `test_persisted_precedence_invariant` | GREEN (full suite: 727 passed, 1 skipped ×3 runs, zero failures — search S5.1 re-run on base `e8dd2bc`, 2026-10-02, commit `7bbc05a`) |
| EDGE-001 | — | `test_eventbus_bootstrap_cycle` | GREEN (full suite: 727 passed, 1 skipped ×3 runs, zero failures — search S5.1 re-run on base `e8dd2bc`, 2026-10-02, commit `7bbc05a`) |
| EDGE-002 | — | `test_unregistered_key_warning` | GREEN (full suite: 727 passed, 1 skipped ×3 runs, zero failures — search S5.1 re-run on base `e8dd2bc`, 2026-10-02, commit `7bbc05a`) |
| EDGE-003 | — | `test_corrupted_values_yaml` | GREEN (full suite: 727 passed, 1 skipped ×3 runs, zero failures — search S5.1 re-run on base `e8dd2bc`, 2026-10-02, commit `7bbc05a`) |
| EDGE-004 | — | `test_missing_values_yaml` | GREEN (full suite: 727 passed, 1 skipped ×3 runs, zero failures — search S5.1 re-run on base `e8dd2bc`, 2026-10-02, commit `7bbc05a`) |
| EDGE-005 | — | `test_list_item_pattern_mismatch` | GREEN (full suite: 727 passed, 1 skipped ×3 runs, zero failures — search S5.1 re-run on base `e8dd2bc`, 2026-10-02, commit `7bbc05a`) |
| EDGE-006 | — | `test_list_min_gt_max` | GREEN (full suite: 727 passed, 1 skipped ×3 runs, zero failures — search S5.1 re-run on base `e8dd2bc`, 2026-10-02, commit `7bbc05a`) |
| EDGE-007 | — | `test_setup_logger_idempotent` | GREEN (full suite: 727 passed, 1 skipped ×3 runs, zero failures — search S5.1 re-run on base `e8dd2bc`, 2026-10-02, commit `7bbc05a`) |
| EDGE-008 | — | `test_sink_reconfigured_rotation` (re-derived from settings-coverage v2 by structlog-logging T-003: exactly one managed rotating file sink, every current value re-applied — rotation size, backup count, file path, UTF-8 encoding and the live level; routes its `logging.*` writes through `set_value_settled` — issue main-ci-green item G) | GREEN (structlog-logging S5.1 full suite: 760 passed, 1 skipped — re-run after the S5.2 test refactor, 2026-10-07, commits `c5ab5f7` / `de31ea9`; RED at S3.2, 2026-10-06) |
| EDGE-009 | — | `test_persist_all_values` | GREEN (full suite: 727 passed, 1 skipped ×3 runs, zero failures — search S5.1 re-run on base `e8dd2bc`, 2026-10-02, commit `7bbc05a`) |
| EDGE-010 | — | `test_live_read_no_trace_on_same` | GREEN (full suite: 727 passed, 1 skipped ×3 runs, zero failures — search S5.1 re-run on base `e8dd2bc`, 2026-10-02, commit `7bbc05a`) |
| EDGE-011 | — | `test_guarded_read_none` | GREEN (full suite: 727 passed, 1 skipped ×3 runs, zero failures — search S5.1 re-run on base `e8dd2bc`, 2026-10-02, commit `7bbc05a`) |
| EDGE-012 | — | `test_list_non_string_rejected` | GREEN (full suite: 727 passed, 1 skipped ×3 runs, zero failures — search S5.1 re-run on base `e8dd2bc`, 2026-10-02, commit `7bbc05a`) |
| NFR-001 | — | `test_live_read_in_memory` | GREEN (full suite: 727 passed, 1 skipped ×3 runs, zero failures — search S5.1 re-run on base `e8dd2bc`, 2026-10-02, commit `7bbc05a`) |
| NFR-002 | — | `test_no_secret_settings` | GREEN (full suite: 727 passed, 1 skipped ×3 runs, zero failures — search S5.1 re-run on base `e8dd2bc`, 2026-10-02, commit `7bbc05a`) |
| NFR-003 | — | `test_inventory_backward_compatible` | GREEN (full suite: 727 passed, 1 skipped ×3 runs, zero failures — search S5.1 re-run on base `e8dd2bc`, 2026-10-02, commit `7bbc05a`) |
| NFR-004 | — | `test_observability_tracing` (re-derived from settings.md v4 §9 by structlog-logging T-003: the settings feature's operations are logged through the logging feature's pipeline — the record must arrive in the managed file sink with its key context) | GREEN (structlog-logging S5.1 full suite: 760 passed, 1 skipped — re-run after the S5.2 test refactor, 2026-10-07, commits `c5ab5f7` / `de31ea9`; RED at S3.2, 2026-10-06) |
| NFR-005 | — | `test_atomic_write` | GREEN (full suite: 727 passed, 1 skipped ×3 runs, zero failures — search S5.1 re-run on base `e8dd2bc`, 2026-10-02, commit `7bbc05a`) |
| NFR-006 | — | `test_thread_safety` | GREEN (full suite: 727 passed, 1 skipped ×3 runs, zero failures — search S5.1 re-run on base `e8dd2bc`, 2026-10-02, commit `7bbc05a`) |

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
| INV-002 | — | `test_inv_002_concurrent_same_key_last_write_wins` (`@settings(deadline=500)`, measured — issue main-ci-green item I; assertion unchanged) | GREEN |
| INV-003 | — | `test_inv_003_metadata_matches_content` | GREEN |
| INV-004 | — | `test_inv_004_at_most_one_avatar_per_user` | GREEN |
| INV-005 | — | `test_inv_005_avatar_url_format` | GREEN |
| INV-006 | — | `test_inv_006_event_correspondence` | GREEN |
| INV-007 | — | `test_inv_007_key_containment` | GREEN |
| INV-008 | — | `test_inv_008_variant_consistency` (`deadline=500`, item I; assertion unchanged) | GREEN |
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
| INV-003 | — | `test_last_admin_invariant` (`tests/property/usermanagement/test_multi_role_invariants.py`, `@settings(deadline=1000)`, measured 246–356 ms CI examples; strategy, `max_size=10`, `max_examples=20` and the assertion unchanged) | GREEN (issue main-ci-green item B closed, Phase 5 S5.1 2026-10-02) |
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

## Issue: session-lookup-unwired (composition-root session lookup — S5.3, 2026-10-04)

Issue `session-lookup-unwired` (type **ISSUE, light tier**; triage + RED/GREEN evidence: `docs/verification/session-lookup-unwired.md`; spec `docs/specs/user-roles-permissions.md`). **Defect:** the composition root built `PermissionService` without a session lookup, so in the composed application every check carrying a session token denied with `storage_error` — REQ-017's validation path never ran and AC-020's positive branch was reachable only in tests that inject a **fake** lookup. **Fix** (`src/main.py`, commit `f85deba`): the session repository is constructed above the `PermissionService` and passed as `session_lookup=`; no `src/backend/permissions/` line changed, so the fail-closed branches (EDGE-007, INV-002) are untouched.

The reproduction test is the first permissions test that exercises the **real** composition root (`import main` in a fresh interpreter), which is why it is a new row rather than a refreshed one. **No existing row is rewritten or refreshed** (decision **Q-02**, convention B): the `GREEN` rows above — `test_session_validation_in_check` (AC-020), `test_session_validation_skipped_when_token_none` (AC-021), `test_unavailable_session_lookup_denied` (EDGE-007), `test_revoked_expired_token_denied` / `test_mismatched_token_denied` (EDGE-005/006) — stay as the **service-level** record written by the change that observed them; they were re-run GREEN at S5.1 (`tests/acceptance/permissions tests/unit/permissions tests/property/permissions` → `64 passed`) but not edited. The spec's own §11 matrix rows for REQ-017/AC-020 and REQ-017/AC-021 stay `PENDING` (Q-02: no Spec Amendment).

| Feature | Requirement | Acceptance Criterion | Test | Status |
|---------|-------------|---------------------|------|--------|
| permissions (composition root, `src/main.py`) | REQ-017 | AC-020 | `test_ac_020_composition_root_validates_session_token` (new, `tests/acceptance/permissions/test_composition_wiring.py` — `import main` in a fresh interpreter, then `main._permission_service.has_permission(alice.id, "usermanagement.get_user", session_token=…)` → `[True, False, False, False]`: valid token proceeds, revoked / another user's / unknown still deny) | GREEN (session-lookup-unwired S5.3, 2026-10-04, commit `f85deba`) |

## Issue: main-ci-green (nine items — Phase 3 S3.1 → Phase 5 S5.3, 2026-10-02)

Issue `main-ci-green` (type ISSUE; triage, RED and GREEN evidence: `docs/verification/main-ci-green.md` §1 scope table, §7, and the Phase 3/4/5 sections). Every affected spec ID below points at an executable test that is GREEN on the branch.

**GREEN evidence (all rows).** Phase 5 S5.1 re-run (`docs/verification/main-ci-green.md` §"Phase 5 (S5.1 re-run)"): two consecutive full-suite runs `639 passed, 1 skipped` (the single skip is the host symlink limitation), plus four consecutive green randomized-order runs recorded in the item-I section; targeted `tests/unit/settings/test_repository_roundtrip.py tests/unit/logging/test_logging_sink_ownership.py` → `5 passed`. Lint/types gate: S5.2 (`uv run ruff check .` → `All checks passed!`).

| Item | Spec | ID | Test / evidence | Status | Commit |
|---|---|---|---|---|---|
| **A** | settings.md | INV-009, REQ-022, AC-030, AC-031 | `test_yaml_template_roundtrip_nel` (new, `tests/unit/settings/test_repository_roundtrip.py`); property `test_inv_009_yaml_roundtrip` (`tests/property/settings/test_settings_properties.py`, alphabet widened so U+0085 is always generated) | GREEN (was RED) | `d2f8f32` RED · `f9cfe45` fix · `9611757` test |
| **A** (value side) | settings-coverage.md | INV-002, REQ-009, REQ-010, REQ-011 | `test_yaml_value_roundtrip_nel` (new, same file — the two repositories share one serializer) | GREEN (was RED) | `d2f8f32` · `f9cfe45` |
| **B** | user-roles-permissions.md; user-management.md | INV-003, REQ-013, AC-015, AC-036; REQ-008, AC-017..019 | `test_last_admin_invariant` (`tests/property/usermanagement/test_multi_role_invariants.py`) with measured `@settings(deadline=1000)`; invariant, strategy, `max_size=10`, `max_examples=20` unchanged | GREEN (flake closed) | `91cee38` |
| **C** | — (chore, no spec ID) | — | `tests/acceptance/permissions/test_check_api.py`, `tests/acceptance/permissions/test_enforcement.py`, `tests/contract/permissions/test_performance.py` — import blocks sorted; no behavior change | GREEN (S5.2 ruff clean) | `b52d032` |
| **D** | — (chore, no spec ID) | — | `uv.lock` — urllib3 2.8.0, virtualenv 21.14.3, python-discovery 1.6.1 (pip-audit) | n/a (no test; full suite still GREEN) | `772d9dc` |
| **E** | logging.md; settings-coverage.md | REQ-001/002/003, AC-001/002/004/005, INV-001, EDGE-005; REQ-014/015, AC-019/020 | new `tests/unit/logging/test_logging_sink_ownership.py` — `test_reconfigure_replaces_only_the_managed_sinks`, `test_reconfigure_keeps_foreign_sink`, `test_reconfigure_after_external_removal_of_a_managed_sink`; helper changes (`install_isolated_registry` keeps every `logging.*` key, `_SinkState`) | GREEN (was RED — the CI `tests`-job failure) | `d2f8f32` RED · `4d9514e` fix · `9fec0a1` · `0f41dc8` |
| **F** | — (chore, CI config, no spec ID) | — | `.github/workflows/quality.yml` — `dependency-review` runs on `pull_request` only | n/a (no test) | `dd27702` |
| **G** | logging.md; settings-coverage.md | AC-003, REQ-002 (victim, unchanged); EDGE-008, REQ-015, AC-020 | `tests/settings_test_helpers.py::set_value_settled` (ordered drain of the write's own dispatch) applied in `tests/unit/test_settings_coverage.py::test_sink_reconfigured_rotation` | GREEN (flake closed) | `52c70b5` |
| **H** | event-bus.md; settings-coverage.md; logging.md; user-management.md | REQ-005 (AC-008/009/010), REQ-006/AC-011, INV-002, EDGE-007; REQ-015/AC-020; AC-003/REQ-002; REQ-008/INV-003 | `tests/eventbus_test_helpers.py::isolated_event_bus` (parks the shared singleton instead of shutting it down); eventbus test groups `31 passed`; `tests/property/usermanagement/test_usermanagement_properties.py::test_inv_003_last_admin_invariant` (`deadline=1000`) | GREEN | `6c40147` · `983fe2a` |
| **I** | logging.md; file-management.md | REQ-003, AC-004, AC-005, EDGE-005; INV-002, INV-008 | autouse `tests/conftest.py::_stdlib_root_logging_restored` (snapshots/restores root handlers, level and per-logger `disabled` around every test); `tests/property/filemanagement/test_filemanagement_properties.py` — 7 property tests at measured `deadline=500` (assertions, example counts and skips unchanged) | GREEN (was the ≈1-in-3 red full-suite run) | `e1508ec` · `f03f9ce` |

**Traceability-path drift (recorded, not a behavior issue).** `docs/specs/user-roles-permissions.md:725` binds INV-003 to `tests/property/permissions/test_invariants.py::test_last_admin_invariant`; the implemented copies are `tests/property/usermanagement/test_multi_role_invariants.py::test_last_admin_invariant` and `tests/property/usermanagement/test_usermanagement_properties.py::test_inv_003_last_admin_invariant` (both GREEN). The spec's test-strategy path is the drift; a spec amendment is not required by this ISSUE (no behavior change).

## Search Matrix

The search change (type CROSS-CUTTING; spec `docs/specs/search.md`) uses its own REQ/AC ID space (REQ-001..023, AC-001..037, INV-001..005, EDGE-001..021, NFR-001..005) that overlaps the other features' matrices, so it is kept separate. Phase 3 (S3.2) confirmed all 70 newly derived tests RED (failure modes: `ModuleNotFoundError` on the unimplemented `backend.search` module; `ImportError` on the additive `build_user_source` / `build_file_source` / `build_session_source` modules; `AttributeError` on the additive `SessionRepository.list_all`). Status `GREEN`: all 73 rows pass — **re-confirmed on the rebased base** `origin/main` = `e8dd2bc` (Phase 5 S5.1 re-run, 2026-10-02, commit `7bbc05a`: `uv run pytest tests/ -v` → **727 passed, 1 skipped** in each of 3 runs, zero failures; search-family smoke `tests/{acceptance,unit,contract,integration,property}/search` → **87 passed**; S5.2 lint/types/deps/security clean, commit `55a9f73`). Earlier evidence (2026-09-25): Phase 5 S5.1 re-run + S5.3 targeted re-check — every REQ has at least one GREEN test, every AC has at least one executable (GREEN) test, every INV has a property test (GREEN), every EDGE has a test (GREEN), every NFR has a test (GREEN). Targeted re-check (S5.3): `uv run pytest -q tests/acceptance/search/ tests/contract/search/ tests/integration/search/ tests/property/search/ tests/unit/search/ tests/unit/authentication/test_sessions.py` → **74 passed** (the 70 newly derived search tests + the 4 pre-existing authentication session tests in that file); all 8 task DAG tasks are `VERIFIED` (`.github/task-runner/tasks.json`).

| Requirement | Acceptance Criterion | Test | Status |
|-------------|---------------------|------|--------|
| REQ-001 | AC-001 | `test_ac_001_register_source` | GREEN |
| REQ-002 | AC-001 | `test_ac_001_register_source` | GREEN |
| REQ-003 | AC-002 | `test_ac_002_replace_same_name` | GREEN |
| REQ-003 | AC-003 | `test_ac_003_identical_reregistration_noop` | GREEN |
| REQ-003 | AC-004 | `test_ac_004_unregister_source` | GREEN |
| REQ-004 | AC-005 | `test_ac_005_search_free_text_returns_items` | GREEN |
| REQ-004 | AC-006 | `test_ac_006_global_fanout_combined_pagination` | GREEN |
| REQ-005 | AC-007 | `test_ac_007_no_constraints_match_all` | GREEN |
| REQ-005 | AC-008 | `test_ac_008_empty_free_text_no_constraint` | GREEN |
| REQ-006 | AC-009 | `test_ac_009_filter_equals` | GREEN |
| REQ-006 | AC-010 | `test_ac_010_filter_contains_case_insensitive` | GREEN |
| REQ-006 | AC-011 | `test_ac_011_filter_and_group` | GREEN |
| REQ-006 | AC-012 | `test_ac_012_filter_or_group` | GREEN |
| REQ-006 | AC-013 | `test_ac_013_filter_number_comparisons` | GREEN |
| REQ-006 | AC-014 | `test_ac_014_filter_in_list` | GREEN |
| REQ-006 | AC-015 | `test_ac_015_filter_is_null` | GREEN |
| REQ-007 | AC-016 | `test_ac_016_default_page_size` | GREEN |
| REQ-007 | AC-017 | `test_ac_017_limit_clamped_to_max` | GREEN |
| REQ-007 | AC-018 | `test_ac_018_offset_pagination` | GREEN |
| REQ-007 | AC-019 | `test_ac_019_offset_beyond_end_empty` | GREEN |
| REQ-008 | AC-020 | `test_ac_020_sort_overrides_default_order` | GREEN |
| REQ-008 | AC-021 | `test_ac_021_sort_stable_tie_break` | GREEN |
| REQ-009 | AC-005 | `test_ac_005_search_free_text_returns_items` | GREEN |
| REQ-009 | AC-022 | `test_ac_022_result_item_shape` | GREEN |
| REQ-010 | AC-023 | `test_ac_023_unknown_feature_error` | GREEN |
| REQ-010 | AC-024 | `test_ac_024_malformed_query_errors` | GREEN |
| REQ-010 | AC-026 | `test_ac_026_single_source_failure_error` | GREEN |
| REQ-011 | AC-025 | `test_ac_025_global_fanout_source_failure_partial` (integration) | GREEN |
| REQ-012 | AC-027 | `test_ac_027_normalization_invariance` | GREEN |
| REQ-013 | AC-028 | `test_ac_028_register_settings_live_read` | GREEN |
| REQ-014 | AC-029 | `test_ac_029_lifecycle_and_failure_events` | GREEN |
| REQ-015 | AC-030 | `test_ac_030_traced_no_query_in_logs` | GREEN |
| REQ-016 | AC-031 | `test_ac_031_permission_enforcement` | GREEN |
| REQ-017 | AC-032 | `test_ac_032_singleton_and_reset` | GREEN |
| REQ-018 | — | `test_edge_019_concurrent_register_search` (integration), `test_nfr_005_thread_safe_registry` (integration) | GREEN |
| REQ-019 | AC-033 | `test_ac_033_source_timeout` | GREEN |
| REQ-020 | AC-034 | `test_ac_034_user_source` | GREEN |
| REQ-021 | AC-035 | `test_ac_035_file_source` | GREEN |
| REQ-022 | AC-036 | `test_ac_036_session_source` | GREEN |
| REQ-022 | AC-036 | `test_list_all_returns_all_sessions_created_at_desc` (authentication, T-004 additive `SessionRepository.list_all`) | GREEN |
| REQ-023 | AC-037 | `test_ac_037_backend_only_api` | GREEN |
| INV-001 | — | `test_inv_001_registration_idempotent_atomic` | GREEN |
| INV-002 | — | `test_inv_002_query_deterministic` | GREEN |
| INV-003 | — | `test_inv_003_pagination_consistency` | GREEN |
| INV-004 | — | `test_inv_004_normalization_invariance` | GREEN |
| INV-005 | — | `test_inv_005_no_secrets_in_outputs` | GREEN |
| EDGE-001 | — | `test_edge_001_unknown_feature` | GREEN |
| EDGE-002 | — | `test_edge_002_global_no_sources_empty` | GREEN |
| EDGE-003 | — | `test_edge_003_invalid_limit_offset` | GREEN |
| EDGE-004 | — | `test_edge_004_non_filterable_field` | GREEN |
| EDGE-005 | — | `test_edge_005_invalid_operator_for_type` | GREEN |
| EDGE-006 | — | `test_edge_006_non_sortable_field` | GREEN |
| EDGE-007 | — | `test_edge_007_limit_clamped` | GREEN |
| EDGE-008 | — | `test_edge_008_offset_beyond_end` | GREEN |
| EDGE-009 | — | `test_edge_009_global_source_raises_partial` | GREEN |
| EDGE-010 | — | `test_edge_010_single_source_raises_error` | GREEN |
| EDGE-011 | — | `test_edge_011_source_timeout` | GREEN |
| EDGE-012 | — | `test_edge_012_no_searchable_fields_zero_matches` | GREEN |
| EDGE-013 | — | `test_edge_013_unregister_unknown_noop` | GREEN |
| EDGE-014 | — | `test_edge_014_identical_reregistration_noop` | GREEN |
| EDGE-015 | — | `test_edge_015_replace_concurrent_consistent` | GREEN |
| EDGE-016 | — | `test_edge_016_reset_clears_no_events` | GREEN |
| EDGE-017 | — | `test_edge_017_is_null_matches_none` | GREEN |
| EDGE-018 | — | `test_edge_018_in_list_empty_matches_nothing` | GREEN |
| EDGE-019 | — | `test_edge_019_concurrent_register_search` (integration) | GREEN |
| EDGE-020 | — | `test_edge_020_fanout_strict_validation` | GREEN |
| EDGE-021 | — | `test_edge_021_invalid_source_declaration` | GREEN |
| NFR-001 | — | `test_nfr_001_performance_budgets` | GREEN |
| NFR-002 | — | `test_nfr_002_no_query_or_results_in_logs_events` | GREEN |
| NFR-003 | — | `test_nfr_003_public_api_contract` | GREEN |
| NFR-004 | — | `test_nfr_004_traced_service_events` | GREEN |
| NFR-005 | — | `test_nfr_005_thread_safe_registry` (integration) | GREEN |
| — | — | `test_startup_wiring_all_sources` (integration — all three feature sources wired at startup, no single AC) | GREEN |

### Affected Features (CROSS-CUTTING — per-feature source wiring)

The change wires existing features' content as search sources via additive `search_source.py` modules (ADR-077) and one additive repository method (ADR-080). **No existing REQ or AC of any affected feature is touched** — every change is additive, and each affected feature's own suite stays GREEN on the rebased base (Phase 5 S5.1 re-run, 2026-10-02: the full suite is GREEN — `727 passed, 1 skipped` ×3 runs, zero failures — which covers `tests/*/usermanagement`, `tests/*/filemanagement`, `tests/*/authentication`, `tests/*/sessionmanagement`, `tests/*/permissions` and the startup-wiring tests; the PR #58 fixed flaky families did not reappear in any of the 3 runs, see `docs/verification/search.md` §"PR #58 fixed families — reappearance check"). Each affected feature's wiring is covered by a dedicated test (all GREEN):

| Feature | Wiring | Wiring test | Status |
|---------|--------|-------------|--------|
| user-management | `build_user_source` (additive `search_source.py`, source name `usermanagement`, REQ-020) | `test_ac_034_user_source` (AC-034) | GREEN |
| file-management | `build_file_source` (additive `search_source.py`, source name `filemanagement`, REQ-021) | `test_ac_035_file_source` (AC-035) | GREEN |
| session-management | `build_session_source` (additive `search_source.py`, source name `sessionmanagement`, REQ-022) | `test_ac_036_session_source` (AC-036) | GREEN |
| authentication | `SessionRepository.list_all()` (additive ABC method, backward-compatible per authentication NFR-003, REQ-022) | `test_list_all_returns_all_sessions_created_at_desc` (T-004) | GREEN |
| user-roles-permissions | `search.search` action declaration (additive catalog action via the feature-owned `register_actions`, REQ-016) | `test_ac_031_permission_enforcement` (AC-031) | GREEN |
| startup (application entrypoint) | all three feature sources wired at startup (additive wiring, REQ-023) | `test_startup_wiring_all_sources` (integration) | GREEN |
| user-management (supplementary query coverage) | `build_user_source` field/filter/group/sort/pagination behaviour (AC-034) | `tests/unit/search/test_feature_source_queries.py` — `test_user_source_free_text_all_fields`, `test_user_source_string_filter_ops`, `test_user_source_exact_filter_ops`, `test_user_source_nested_groups`, `test_user_source_sort`, `test_user_source_pagination` | GREEN (87-test search-family smoke, `7bbc05a`) |
| file-management (supplementary query coverage) | `build_file_source` field/filter/group/sort/pagination behaviour (AC-035) | `tests/unit/search/test_feature_source_queries.py` — `test_file_source_free_text_all_fields`, `test_file_source_string_filter_ops`, `test_file_source_exact_filter_ops`, `test_file_source_nested_groups`, `test_file_source_sort`, `test_file_source_pagination` | GREEN (87-test search-family smoke, `7bbc05a`) |
| session-management (supplementary query coverage) | `build_session_source` field/filter/group/sort/pagination behaviour (AC-036) | `tests/unit/search/test_feature_source_queries.py` — `test_session_source_free_text`, `test_session_source_string_filter_ops`, `test_session_source_exact_filter_ops`, `test_session_source_nested_groups`, `test_session_source_sort`, `test_session_source_pagination` | GREEN (87-test search-family smoke, `7bbc05a`) |
| authentication (own-spec contract) | `SessionRepository` ABC widened additively with `list_all()` — the authentication public-API backward-compatibility contract must still hold | `test_nfr_003_public_api_stable` (`tests/contract/authentication/test_public_api.py`, authentication NFR-003) + `test_list_all_returns_all_sessions_created_at_desc` | GREEN (full suite `7bbc05a`) |
| user-roles-permissions (own-spec contract) | the `search.search` action joins the static catalog built from feature-owned `register_actions` (permissions REQ-004, REQ-005, REQ-010) | `test_ac_031_permission_enforcement` (AC-031) + the permissions catalog/contract suite (`tests/acceptance/permissions/`, `tests/contract/permissions/`) | GREEN (full suite `7bbc05a`) |

## Structlog Logging Matrix (amendment PR, 2026-10-04)

Rows for `docs/specs/structlog-logging.md` (CROSS-CUTTING, ADR-082). P.4 recorded the rows, Phase 3 (S3.1 per DAG task, gate S3.2, 2026-10-06) filled the Test column and observed the RED gate. Test paths are given where a function name is shared with another spec's matrix (e.g. `test_edge_001_log_file_parent_created` exists both in `tests/unit/logging/test_logging_edges.py` for `logging.md` EDGE-001 and in `tests/unit/logging/test_pipeline_edges.py` for this spec's EDGE-001).

**Phase 5 (S5.3, 2026-10-07).** All 37 rows are `GREEN` as observed at S5.1 — `uv run pytest tests/ -v` → **760 passed, 1 skipped** (761 collected, 0 failed), re-confirmed after the two behaviour-preserving property-test refactors of S5.2 (`c5ab5f7`, `de31ea9`); the S3.2 RED observation stays inside each cell (decision **Q-129**, convention B). The per-feature breakdown required for a CROSS-CUTTING change is in the **Affected Features** table below the matrix.

| Requirement | Acceptance Criterion | Test | Status |
|-------------|---------------------|------|--------|
| REQ-001 | AC-001 | `test_ac_001_no_backend_import_and_stdlib_chain` (`tests/acceptance/logging/test_pipeline_backend.py`) | GREEN (structlog-logging S5.1 full suite: 760 passed, 1 skipped, 2026-10-07, commits `c5ab5f7` / `de31ea9`; RED at S3.2, 2026-10-06 — the pipeline still imported a logging backend) |
| REQ-002 | AC-002 | `test_ac_002_two_managed_handlers`; the "colorized text to standard error" clause: `test_ac_002_console_color_is_selected_only_for_a_terminal_stream` (`tests/unit/logging/test_renderers.py`, added for S6.1 finding F-S6.1-01) | GREEN (structlog-logging S6.2, 2026-10-07: the colorized clause re-observed **GREEN** — `test_ac_002_console_color_is_selected_only_for_a_terminal_stream` passes unmodified after the one-line fix at `src/backend/logging/_renderers.py:231` (`e776c36`), and the full suite at that commit is 761 passed, 1 skipped, 0 failed. The row's own S5.1 observation stays as written: `uv run pytest tests/ -v` → 760 passed, 1 skipped, 2026-10-07, commits `c5ab5f7` / `de31ea9`. Earlier records kept inside this cell as this change's gate history (convention B, decision Q-129): RED for the colorized clause (structlog-logging S6.1 findings resolution, 2026-10-07: the new witness failed — `LEVEL_COLORS` is keyed lowercase while the record's `level` field is the uppercase `levelname`, so the console sink never colorizes; see `docs/verification/structlog-logging.md` § S6.1 findings — resolution, F-S6.1-01). The rest of the row stayed GREEN as observed at S5.1; RED at S3.2, 2026-10-06 — the feature logger did not own exactly two managed sinks) |
| REQ-002 | AC-003 | `test_ac_003_file_record_fields_as_json` | GREEN (structlog-logging S5.1 full suite: 760 passed, 1 skipped, 2026-10-07, commits `c5ab5f7` / `de31ea9`; RED at S3.2, 2026-10-06 — the file record was not the required JSON field set) |
| REQ-003 | AC-004 | `test_ac_004_foreign_handlers_untouched` | GREEN (structlog-logging S5.1 full suite: 760 passed, 1 skipped, 2026-10-07, commits `c5ab5f7` / `de31ea9`; already GREEN at S3.2, 2026-10-06 — the re-derived no-collateral guard holds before and after the change) |
| REQ-003 | AC-005 | `test_ac_005_no_duplicate_records` | GREEN (structlog-logging S5.1 full suite: 760 passed, 1 skipped, 2026-10-07, commits `c5ab5f7` / `de31ea9`; RED at S3.2, 2026-10-06 — a third-party record reached a sink twice) |
| REQ-004 | AC-006 | `test_ac_006_third_party_reaches_both_sinks` | GREEN (structlog-logging S5.1 full suite: 760 passed, 1 skipped, 2026-10-07, commits `c5ab5f7` / `de31ea9`; RED at S3.2, 2026-10-06 — a stdlib-logger record did not reach both managed sinks) |
| REQ-004 | AC-007 | `test_ac_007_location_of_emitting_call` | GREEN (structlog-logging S5.1 full suite: 760 passed, 1 skipped, 2026-10-07, commits `c5ab5f7` / `de31ea9`; RED at S3.2, 2026-10-06 — the record named the wrapper, not the emitting call) |
| REQ-005 | AC-008 | `test_ac_008_get_logger_emits_to_sinks` | GREEN (structlog-logging S5.1 full suite: 760 passed, 1 skipped, 2026-10-07, commits `c5ab5f7` / `de31ea9`; RED at S3.2, 2026-10-06 — `backend.logging` exported no `get_logger()`) |
| REQ-005 | AC-009 | `test_ac_009_statements_go_through_get_logger`; per-feature witnesses `test_ac_009_settings_statements_go_through_get_logger`, `test_ac_009_eventbus_statements_go_through_get_logger` (`tests/acceptance/logging_coverage/test_statements_via_feature.py` — since the S6.1 findings resolution each per-feature witness also asserts the migrated statements' unchanged wording reaches the pipeline capture, closing F-S6.1-02) | GREEN (structlog-logging S5.1 full suite: 760 passed, 1 skipped, 2026-10-07, commits `c5ab5f7` / `de31ea9`; re-run with the added message-content assertions at the S6.1 findings resolution, 2026-10-07; RED at S3.2, 2026-10-06 — feature statements bypassed the feature logger and the modules named a backend import) |
| REQ-006 | AC-010 | `test_ac_010_renderer_selection` | GREEN (structlog-logging S5.1 full suite: 760 passed, 1 skipped, 2026-10-07, commits `c5ab5f7` / `de31ea9`; RED at S3.2, 2026-10-06 — `setup_logger(renderer=…)` was not accepted / the selected renderer was not applied) |
| REQ-007 | AC-011 | `test_ac_011_sync_and_async_traced_records` | GREEN (structlog-logging S5.1 full suite: 760 passed, 1 skipped, 2026-10-07, commits `c5ab5f7` / `de31ea9`; RED at S3.2, 2026-10-06 — the traced entry/exit records lacked the required fields) |
| REQ-007 | AC-012 | `test_ac_012_exception_record_and_propagation` | GREEN (structlog-logging S5.1 full suite: 760 passed, 1 skipped, 2026-10-07, commits `c5ab5f7` / `de31ea9`; RED at S3.2, 2026-10-06 — the exception record did not carry the required fields) |
| REQ-007 | AC-013 | `test_ac_013_removed_parameters`; `test_nfr_004_backward_compatible_api` (`tests/contract/logging/`) | GREEN (structlog-logging S5.1 full suite: 760 passed, 1 skipped, 2026-10-07, commits `c5ab5f7` / `de31ea9`; RED at S3.2, 2026-10-06 — `context_getter` / `depth` were still accepted parameters) |
| REQ-008 | AC-014 | `test_ac_014_logged_class_records` | GREEN (structlog-logging S5.1 full suite: 760 passed, 1 skipped, 2026-10-07, commits `c5ab5f7` / `de31ea9`; RED at S3.2, 2026-10-06 — `@logged_class` records did not match the required shape) |
| REQ-009 | AC-015 | `test_ac_015_no_local_values_in_exception_record` | GREEN (structlog-logging S5.1 full suite: 760 passed, 1 skipped, 2026-10-07, commits `c5ab5f7` / `de31ea9`; RED at S3.2, 2026-10-06 — local variable values appeared in the exception record) |
| REQ-010 | AC-016 | `test_ac_016_call_unaffected_by_failing_file_sink`; `test_ac_016_file_sink_keeps_working_after_a_failing_sink` (both in `tests/acceptance/logging_coverage/test_sink_failure.py` — the second is the surviving-sink half of AC-016: the file sink keeps writing after a managed sink fails) | GREEN (structlog-logging S5.1 full suite: 760 passed, 1 skipped, 2026-10-07, commits `c5ab5f7` / `de31ea9`; RED at S3.2, 2026-10-06 — a failing file sink still interrupted the call) |
| REQ-011 | AC-003 | `test_ac_003_file_record_fields_as_json` (same witness as REQ-002 / AC-003) | GREEN (structlog-logging S5.1 full suite: 760 passed, 1 skipped, 2026-10-07, commits `c5ab5f7` / `de31ea9`; RED at S3.2, 2026-10-06) |
| REQ-012 | AC-017 | `test_ac_017_live_reconfigure` | GREEN (structlog-logging S5.1 full suite: 760 passed, 1 skipped, 2026-10-07, commits `c5ab5f7` / `de31ea9`; RED at S3.2, 2026-10-06 — a `logging.*` registry change did not reconfigure the live pipeline) |
| REQ-013 | AC-018 | `test_ac_018_dependency_report_clean` | GREEN (structlog-logging S5.1 full suite: 760 passed, 1 skipped, 2026-10-07, commits `c5ab5f7` / `de31ea9`; RED at S3.2, 2026-10-06 — the removed backend was still a declared/imported dependency; `uv run deptry .` clean at S5.2) |
| REQ-014 | AC-019 | `test_ac_019_guidance_names_feature_entry_points` | GREEN (structlog-logging S5.1 full suite: 760 passed, 1 skipped, 2026-10-07, commits `c5ab5f7` / `de31ea9`; RED at S3.2, 2026-10-06 — 24 violated guidance clauses, `AGENTS.md` + 3 skill files) |
| REQ-015 | AC-020 | `test_ac_020_public_export_surface` | GREEN (structlog-logging S5.1 full suite: 760 passed, 1 skipped, 2026-10-07, commits `c5ab5f7` / `de31ea9`; RED at S3.2, 2026-10-06 — the export surface lacked `get_logger` and still exported removed names) |
| INV-001 | — | `test_inv_001_concurrent_setup_owns_two_handlers` (`tests/property/logging/test_pipeline_invariants.py`) | GREEN (structlog-logging S5.1 full suite: 760 passed, 1 skipped, 2026-10-07, commits `c5ab5f7` / `de31ea9`; RED at S3.2, 2026-10-06 — Hypothesis, assertion on handler ownership; body restructured in S5.2 for the complexipy gate, strategies and assertions unchanged) |
| INV-002 | — | `test_inv_002_no_local_value_ever_recorded` | GREEN (structlog-logging S5.1 full suite: 760 passed, 1 skipped, 2026-10-07, commits `c5ab5f7` / `de31ea9`; RED at S3.2, 2026-10-06 — Hypothesis, a local value reached a record) |
| INV-003 | — | `test_inv_003_elapsed_non_negative` | GREEN (structlog-logging S5.1 full suite: 760 passed, 1 skipped, 2026-10-07, commits `c5ab5f7` / `de31ea9`; RED at S3.2, 2026-10-06 — Hypothesis, assertion on the elapsed field) |
| INV-004 | — | `test_inv_004_other_loggers_untouched` | GREEN (structlog-logging S5.1 full suite: 760 passed, 1 skipped, 2026-10-07, commits `c5ab5f7` / `de31ea9`; RED at S3.2, 2026-10-06 — Hypothesis, no logger owned the managed console sink) |
| INV-005 | — | `test_inv_005_required_fields_present` (`tests/property/logging/test_pipeline_invariants.py`) | GREEN (structlog-logging S5.1 full suite: 760 passed, 1 skipped, 2026-10-07, commits `c5ab5f7` / `de31ea9`; RED at S3.2, 2026-10-06 — Hypothesis, assertion on the required record fields; body restructured in S5.2 for the complexipy gate, strategies and assertions unchanged) |
| EDGE-001 | — | `test_edge_001_log_file_parent_created` (`tests/unit/logging/test_pipeline_edges.py`) | GREEN (structlog-logging S5.1 full suite: 760 passed, 1 skipped, 2026-10-07, commits `c5ab5f7` / `de31ea9`; RED at S3.2, 2026-10-06 — the log-file parent directory was not created) |
| EDGE-002 | — | `test_edge_002_rotation_with_open_handle` | GREEN (structlog-logging S5.1 full suite: 760 passed, 1 skipped, 2026-10-07, commits `c5ab5f7` / `de31ea9`; RED at S3.2, 2026-10-06 — assertion on rotation with an open handle) |
| EDGE-003 | — | `test_edge_003_file_config_keeps_managed_handlers` (`tests/integration/logging/test_external_reconfiguration.py`) | GREEN (structlog-logging S5.1 full suite: 760 passed, 1 skipped, 2026-10-07, commits `c5ab5f7` / `de31ea9`; RED at S3.2, 2026-10-06 — an external `fileConfig` dropped the managed handlers) |
| EDGE-004 | — | `test_edge_004_unknown_numeric_level` | GREEN (structlog-logging S5.1 full suite: 760 passed, 1 skipped, 2026-10-07, commits `c5ab5f7` / `de31ea9`; RED at S3.2, 2026-10-06 — assertion on the unknown-numeric-level case) |
| EDGE-005 | — | `test_edge_005_unknown_renderer` | GREEN (structlog-logging S5.1 full suite: 760 passed, 1 skipped, 2026-10-07, commits `c5ab5f7` / `de31ea9`; RED at S3.2, 2026-10-06 — an unknown renderer name was not rejected as specified) |
| EDGE-006 | — | `test_edge_006_get_logger_before_setup` | GREEN (structlog-logging S5.1 full suite: 760 passed, 1 skipped, 2026-10-07, commits `c5ab5f7` / `de31ea9`; RED at S3.2, 2026-10-06 — `get_logger()` before setup raised / was absent) |
| NFR-001 | — | `test_nfr_001_setup_time_budget` (`tests/contract/logging/test_logging_contracts.py`) | GREEN (structlog-logging S5.1 full suite: 760 passed, 1 skipped, 2026-10-07, commits `c5ab5f7` / `de31ea9`; already GREEN at S3.2, 2026-10-06 — the amended 25 ms budget already held on the current pipeline; re-measured, no regression) |
| NFR-002 | — | `test_nfr_002_decorator_overhead_budget` | GREEN (structlog-logging S5.1 full suite: 760 passed, 1 skipped, 2026-10-07, commits `c5ab5f7` / `de31ea9`; RED at S3.2, 2026-10-06 — the amended DEBUG-sinks budget was exceeded; reference measurement 0.148 ms/call with both managed sinks active at DEBUG, n = 3) |
| NFR-003 | — | `test_inv_002_no_local_value_ever_recorded` (same witness as INV-002) | GREEN (structlog-logging S5.1 full suite: 760 passed, 1 skipped, 2026-10-07, commits `c5ab5f7` / `de31ea9`; RED at S3.2, 2026-10-06) |
| NFR-004 | — | `test_ac_018_dependency_report_clean` | GREEN (structlog-logging S5.1 full suite: 760 passed, 1 skipped, 2026-10-07, commits `c5ab5f7` / `de31ea9`; RED at S3.2, 2026-10-06 — the dependency report still named the removed backend) |
| NFR-005 | — | `test_nfr_005_single_listener_thread` | GREEN (structlog-logging S5.1 full suite: 760 passed, 1 skipped, 2026-10-07, commits `c5ab5f7` / `de31ea9`; RED at S3.2, 2026-10-06 — no single queue listener thread existed) |

### Affected Features (CROSS-CUTTING — per-feature rows, spec §10 Impact Analysis)

The change re-homes the logging backend and re-points the witnesses of the features it touches. No REQ or AC of another feature is redefined beyond the four approved amendments (`logging.md` v3, `logging-coverage.md` v2, `settings-coverage.md` v2, `settings.md` v4 wording); everything else is a witness adaptation to the new pipeline. Rows updated in place in each affected feature's own matrix (evidence: structlog-logging S5.1, 2026-10-07):

| Affected feature | What this change did there | Matrix rows updated in that feature's section | Status |
|------------------|---------------------------|------------------------------------------------|--------|
| logging (owner) | new structlog pipeline over stdlib handlers; `get_logger()` entry point; reduced `@logged` parameter set; loguru removed / structlog + orjson added (ADR-082) | the 37 rows of the **Structlog Logging Matrix** above; `logging.md` rows REQ-001/AC-001, REQ-002/AC-002, REQ-002/AC-003, REQ-003/AC-004, INV-001, NFR-001, NFR-002, NFR-003, NFR-004 and the `test_stdlib_decorator_pipeline` integration row (renamed at S6.1, F-S6.1-06); the retired REQ-003/AC-005 and EDGE-005 cells now record the deletion of the intercept-bootstrap and unknown-level witnesses (`tests/unit/logging/test_logging.py`, `tests/unit/logging/test_logging_edges.py`; spec §11, T-001 `fcce934`) | GREEN |
| logging-coverage | witnesses re-pointed at the pipeline's own handlers and the `failing_sink_attached()` helper; the direct-loguru policy witness deleted with the retired `REQ-010` / `AC-010` wording | `REQ-005/AC-005`, `REQ-010/AC-010` (re-pointed in T-006 to `test_ac_009_statements_go_through_get_logger`), `REQ-013/AC-013`, `INV-004`, `EDGE-002`, `EDGE-005` | GREEN |
| settings | 28 direct statements (registry 17, repository 11) now go through `get_logger("backend.settings")`; live reconfigure mutates the managed handlers; amended `settings-coverage.md` v2 wording | `REQ-014/AC-019`, `REQ-015/AC-020`, `REQ-016/AC-021`, `EDGE-008`, `NFR-004` | GREEN |
| eventbus | 10 direct statements now go through `get_logger("backend.eventbus")`; no event-bus REQ/AC touched | none — event-bus rows are unchanged (no event-bus witness was modified); the feature's suite is GREEN in the S5.1 full-suite run | GREEN (full suite) |
| permissions | 1 direct statement now goes through `get_logger("backend.permissions")`; no permissions REQ/AC touched | none — permissions rows are unchanged; the feature's suite is GREEN in the S5.1 full-suite run | GREEN (full suite) |
| tooling (`pyproject.toml`, `uv.lock`) | loguru removed, structlog + orjson added; dependency report clean | `REQ-013/AC-018` and `NFR-004` in the Structlog Logging Matrix — both witnessed by `test_ac_018_dependency_report_clean`; `uv run deptry .` clean at S5.2 | GREEN |
| guidance files (`AGENTS.md`, 3 `python-best-practices` skill files) | 24 clauses re-pointed at the feature's public entry points | `REQ-014/AC-019` (`test_ac_019_guidance_names_feature_entry_points`) | GREEN |

## Settings Public Registry Setter Matrix (spec amendment PR, 2026-10-06)

Rows for `docs/specs/settings-public-registry-setter.md` (CROSS-CUTTING) and for the new IDs the
change adds to the six amended specs (`settings.md` v5, `event-bus.md` v2,
`user-roles-permissions.md` v2, `search.md` v4, `session-management.md` v2,
`logging-coverage.md` v3). The tests are derived in Phase 3 of the implementation change; the Test
column is filled then (P.4 records the rows, not the tests). **No existing row of any affected
feature is rewritten or refreshed** (convention B) — the cited IDs (`settings.md` REQ-014/AC-018,
`event-bus.md` REQ-006/AC-011/REQ-005, `user-roles-permissions.md` REQ-023/AC-028,
`search.md` REQ-017/AC-032, `session-management.md` REQ-020/AC-041/AC-042/AC-043,
`logging-coverage.md` REQ-001/REQ-007, `settings-coverage.md` REQ-002/REQ-012) keep their dated
records; only the enumeration wording of the singleton requirements and the public-API lists is
extended.

### The change spec (`docs/specs/settings-public-registry-setter.md`)

| Requirement | Acceptance Criterion | Test | Status |
|-------------|---------------------|------|--------|
| REQ-001 | AC-001, AC-002 | — | PENDING (settings-public-registry-setter P.4, 2026-10-06) |
| REQ-002 | AC-003, AC-004 | — | PENDING (settings-public-registry-setter P.4, 2026-10-06) |
| REQ-003 | AC-005, AC-006 | — | PENDING (settings-public-registry-setter P.4, 2026-10-06) |
| REQ-004 | AC-007 | — | PENDING (settings-public-registry-setter P.4, 2026-10-06) |
| REQ-005 | AC-008 | — | PENDING (settings-public-registry-setter P.4, 2026-10-06) |
| REQ-006 | AC-009, AC-010 | — | PENDING (settings-public-registry-setter P.4, 2026-10-06) |
| REQ-007 | AC-011 | — | PENDING (settings-public-registry-setter P.4, 2026-10-06) |
| REQ-008 | AC-012 | — | PENDING (settings-public-registry-setter P.4, 2026-10-06) |
| REQ-009 | AC-013 | — | PENDING (settings-public-registry-setter P.4, 2026-10-06) |
| REQ-010 | AC-014, AC-015 | — | PENDING (settings-public-registry-setter P.4, 2026-10-06) |
| REQ-011 | AC-016 | — | PENDING (settings-public-registry-setter P.4, 2026-10-06) |
| REQ-012 | AC-017 | — | PENDING (settings-public-registry-setter P.4, 2026-10-06) |
| REQ-013 | AC-017, AC-018 | — | PENDING (settings-public-registry-setter P.4, 2026-10-06) |
| REQ-014 | AC-007 | — | PENDING (settings-public-registry-setter P.4, 2026-10-06) |
| REQ-015 | AC-019 | — | PENDING (settings-public-registry-setter P.4, 2026-10-06) |
| REQ-016 | AC-020 | — | PENDING (settings-public-registry-setter P.4, 2026-10-06) |
| INV-001, INV-002, INV-003 | — | — | PENDING (settings-public-registry-setter P.4, 2026-10-06) |
| EDGE-001 … EDGE-010 | — | — | PENDING (settings-public-registry-setter P.4, 2026-10-06) |
| NFR-001 … NFR-004 | — | — | PENDING (settings-public-registry-setter P.4, 2026-10-06) |

### The amended feature specs (new IDs only)

| Requirement | Acceptance Criterion | Test | Status |
|-------------|---------------------|------|--------|
| REQ-026 (`settings.md` v5) | AC-040, AC-041, AC-042, AC-043 | — | PENDING (settings-public-registry-setter P.4, 2026-10-06) |
| INV-011 (`settings.md` v5) | — | — | PENDING (settings-public-registry-setter P.4, 2026-10-06) |
| EDGE-030 … EDGE-033 (`settings.md` v5) | — | — | PENDING (settings-public-registry-setter P.4, 2026-10-06) |
| REQ-008 (`event-bus.md` v2) | AC-013, AC-014, AC-015, AC-016 | — | PENDING (settings-public-registry-setter P.4, 2026-10-06) |
| EDGE-011, EDGE-012 (`event-bus.md` v2) | — | — | PENDING (settings-public-registry-setter P.4, 2026-10-06) |
| REQ-030 (`user-roles-permissions.md` v2) | AC-041, AC-042, AC-043, AC-044 | — | PENDING (settings-public-registry-setter P.4, 2026-10-06) |
| EDGE-027, EDGE-028 (`user-roles-permissions.md` v2) | — | — | PENDING (settings-public-registry-setter P.4, 2026-10-06) |
| REQ-024 (`search.md` v4) | AC-038, AC-039, AC-040, AC-041 | — | PENDING (settings-public-registry-setter P.4, 2026-10-06) |
| EDGE-022, EDGE-023 (`search.md` v4) | — | — | PENDING (settings-public-registry-setter P.4, 2026-10-06) |
| REQ-023 (`session-management.md` v2) | AC-046, AC-047, AC-048, AC-049 | — | PENDING (settings-public-registry-setter P.4, 2026-10-06) |
| EDGE-013, EDGE-014 (`session-management.md` v2) | — | — | PENDING (settings-public-registry-setter P.4, 2026-10-06) |
| REQ-001 (`logging-coverage.md` v3 — inventory rows only, no new ID) | — | — | N/A (inventory-only amendment; covered by the change spec's AC-015) |

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

## Rebase reconciliation (2026-10-02, search S5.3)

- Union of `main`'s `main-ci-green` rows with the Search Matrix (rebase onto `origin/main` = `e8dd2bc`); the union was verified, not re-derived: no conflict markers, no duplicate section headings, no duplicate rows, no duplicated requirement IDs (73 Search rows; the two repeated test names — `test_ac_001_register_source`, `test_ac_005_search_free_text_returns_items` — are legitimate many-to-one REQ/AC mappings).
- Defects found and fixed: (1) the Search Matrix and the per-feature wiring rows still cited the pre-rebase 2026-09-25 evidence — re-labelled with the rebased-run evidence (S5.1 `727 passed, 1 skipped` ×3, commit `7bbc05a`; S5.2 clean, commit `55a9f73`); (2) 75 legacy rows in the pre-existing feature matrices (logging `Matrix`, settings-coverage, …) were still `RED` although GREEN — byte-identical on `origin/main`, i.e. pre-existing staleness, not a union defect — flipped to GREEN with the rebased-run evidence label; (3) the 18 per-feature source query tests had no matrix row — added as supplementary rows (AC-034/035/036) plus own-spec contract rows for authentication NFR-003 and permissions REQ-004/005/010.
- Search spec IDs covered: **91/91** (`comm -23` of the IDs in `docs/specs/search.md` against the matrix → 0 missing).
- Orphans: **none** — all 87 search test functions are either named in the matrix or trace to a spec ID in their docstrings.
- No test or source file was modified in this step (docs only).
