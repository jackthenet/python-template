# Verification: user-roles-permissions

## Change Type: CROSS-CUTTING

- **Date:** 2026-07-10
- **Branch:** `crosscut/user-roles-permissions`
- **Worktree:** `../python-template_kopie-worktrees/crosscut/user-roles-permissions`

## Classification Rationale

The change is a **new shared capability** (a permissions/authorization system) that
intentionally spans two or more features:

- **usermanagement** — role model and role assignment (existing: `"admin"` / `"member"`
  roles, `set_role`, `LastAdminError` guard).
- **New shared permissions feature** — per-feature/action permission model and the
  backend permission-check capability that other features depend on.

It is not an ISSUE (no deviation from approved spec behavior), not a REFACTOR
(externally observable behavior is added), and not a DOCS/CHORE (behavior changes).

## Request (as received)

> ## User roles & permissions
> Roles such as Admin/User
> Permissions per feature/action
> Role assignment
> Permission checks in the backend

## Phases

### Phase 1: Specify — COMPLETE

- **Spec:** `docs/specs/user-roles-permissions.md` (commit `34227d0`), 13 sections, 106 stable IDs (29 REQ, 40 AC, 6 INV, 26 EDGE, 5 NFR).
- **Steps:** S1.1 Interrogate (33 questions, Q-66…Q-98, all answered) → S1.2 Draft spec → S1.3 Verify self-consistency (all 8 checklist items pass; 1 fix applied in-spec) → S1.4 Present for approval.
- **PR:** #51 open (https://github.com/jackthenet/python-template/pull/51), `crosscut/user-roles-permissions` → `main`, **NOT merged** (`mergedAt: null`).

### Spec Approval (cached — verified once, before Phase 2)

- **Status:** HUMAN APPROVED (pre-approved).
- **Basis:** User governance directive **Q-99** (`AI_Questions.md`): the user pre-approves the spec PR (going to bed) and instructs NOT to merge it; the pre-approval satisfies the approval gate (a human-governance override of the merge-based entry check), so Phase 2 proceeds on the pre-approval WITHOUT the merge.
- **Approve action:** `gh pr review --approve 51` attempted, blocked by GitHub self-approval policy ("Can not approve your own pull request") — the documented pre-approval Q-99 governs; the spec is treated as HUMAN APPROVED regardless.
- **PR:** #51 (open, unmerged; the user will merge it later).
- **Date:** 2026-07-10.

### Phase 2: Decompose — COMPLETE

- **Steps:** S2.1 Create ADRs → S2.2 Decompose into task DAG.
- **ADRs (7):** ADR-069 (permissions feature placement), ADR-070 (shared enforcement plumbing, no circular imports), ADR-071 (enforcement wiring via trailing `principal` param + decorator, standalone mode), ADR-072 (multi-role user-management amendment), ADR-073 (session validation via structural `SessionLookup` seam), ADR-074 (dynamic role→permission mapping), ADR-075 (fail-closed security posture). Commit `572637d`.
- **Task DAG:** `docs/tasks/user-roles-permissions.tasks.json` — 14 tasks (T-001…T-014), grouped by affected feature (shared plumbing, usermanagement, permissions, per-feature enforcement, cross-cutting integration), covering all 29 REQs + 40 ACs (77 tests), acyclic + gate-satisfiable. Copied to `.github/task-runner/tasks.json`. Commit `a07651f`.
- **House-format refinements:** `tests_to_create` + red/green use `file::function` paths (name collision + same-directory multi-task); red/green are targeted (not the full suite).

### Phase 3: Test & RED — COMPLETE

- **Steps:** S3.1 Derive tests (per task: 14 fresh subagents, one commit per task, T-001…T-014) → S3.2 Ruff + confirm RED.
- **Tests derived (77):** 18 test files — `tests/acceptance/permissions/` (6 files: `test_enforcement.py`, `test_errors.py`, `test_check_api.py`, `test_system_principal.py`, `test_role_management.py`, `test_events.py`), `tests/acceptance/usermanagement/test_multi_role.py`, `tests/acceptance/authentication/test_enforcement_wiring.py`, `tests/acceptance/settings/test_enforcement_wiring.py`, `tests/acceptance/mail/test_enforcement_wiring.py`, `tests/acceptance/sessionmanagement/test_enforcement_wiring.py`, `tests/property/permissions/test_invariants.py`, `tests/property/usermanagement/test_multi_role_invariants.py`, `tests/unit/permissions/test_edge_cases.py`, `tests/unit/permissions/test_enforcement_plumbing.py`, `tests/integration/permissions/test_persistence.py`, `tests/integration/permissions/test_thread_safety.py`, `tests/contract/permissions/test_performance.py` (plus `__init__.py` for the new test packages). Commits `9a5e552`…`a7c3e9e` (one per DAG task).
- **Ruff (S3.2):** `uv run ruff check tests/acceptance/authentication/test_enforcement_wiring.py tests/acceptance/mail/test_enforcement_wiring.py tests/acceptance/permissions/ tests/acceptance/sessionmanagement/test_enforcement_wiring.py tests/acceptance/settings/test_enforcement_wiring.py tests/acceptance/usermanagement/test_multi_role.py tests/contract/permissions/ tests/integration/permissions/ tests/property/permissions/ tests/property/usermanagement/test_multi_role_invariants.py tests/unit/permissions/` → **All checks passed** (clean on all changed test paths; no fixes needed).
- **RED command (targeted — the 77 newly derived tests, the union of the DAG's `red_command`s; the full suite is a Phase 5 gate):**
  `uv run pytest tests/acceptance/permissions/ tests/acceptance/usermanagement/test_multi_role.py tests/acceptance/authentication/test_enforcement_wiring.py tests/acceptance/settings/test_enforcement_wiring.py tests/acceptance/mail/test_enforcement_wiring.py tests/acceptance/sessionmanagement/test_enforcement_wiring.py tests/property/permissions/ tests/property/usermanagement/test_multi_role_invariants.py tests/unit/permissions/ tests/integration/permissions/ tests/contract/permissions/ -v`
- **Result:** **77 failed, 0 passed, 0 errors, 0 collection errors** (1.1 s) — RED confirmed before any implementation.
- **Test contract sanity check (PASSED):** all 77 tests collect cleanly (the `backend.permissions` / `backend.shared` / `feature_actions` imports are deferred into the test bodies, so collection succeeds before the feature exists); every failure is in the **test body (call phase)** — none in setup/fixture/collection/import; no fixture collisions; Hypothesis strategies match the spec's domain (role sets, catalog keys, session scenarios). The 6 T-002 amendment tests fail against the pre-amendment `usermanagement` models (the amended `UserCreate(roles=[...])` / `UserRead.roles` API does not exist yet) — the established RED pattern for the amendment task, not a broken test contract.
- **Failure mode per test** (the established RED pattern for this change):

| Failure mode | Count | Meaning |
|---|---|---|
| `ModuleNotFoundError: No module named 'backend.permissions'` | 63 | deferred import of the unimplemented permissions feature (test bodies) |
| `ModuleNotFoundError: No module named 'backend.shared'` | 3 | deferred import of the unimplemented shared enforcement plumbing (`Principal`, `requires_permission`) |
| `ModuleNotFoundError: No module named 'backend.authentication.feature_actions'` | 1 | deferred import of the unimplemented feature-owned action declarations (the initial-catalog test) |
| `AssertionError` (trailing parameter is not `principal`) | 4 | per-feature enforcement-wiring signature checks against the current (un-wired) services |
| `pydantic_core.ValidationError` (`UserCreate`: `role` field required) | 5 | T-002 amendment: the tests construct the amended `UserCreate(roles=[...])`; the pre-amendment model requires `role` |
| `AttributeError` (`UserRead` object has no attribute `roles`) | 1 | T-002 amendment: the test reads the amended `UserRead.roles` on the pre-amendment model |

**Per-test failure modes (77):**

| Test | Failure mode | Location |
|---|---|---|
| `tests/acceptance/permissions/test_check_api.py::test_denied_permission_raises_with_context` | ModuleNotFoundError: No module named 'backend.permissions' | `tests/acceptance/permissions/test_check_api.py:93` |
| `tests/acceptance/permissions/test_check_api.py::test_malformed_permission_denied` | ModuleNotFoundError: No module named 'backend.permissions' | `tests/acceptance/permissions/test_check_api.py:134` |
| `tests/acceptance/permissions/test_check_api.py::test_admin_wildcard_allows_all` | ModuleNotFoundError: No module named 'backend.permissions' | `tests/acceptance/permissions/test_check_api.py:172` |
| `tests/acceptance/permissions/test_check_api.py::test_user_role_starts_with_zero_permissions` | ModuleNotFoundError: No module named 'backend.permissions' | `tests/acceptance/permissions/test_check_api.py:203` |
| `tests/acceptance/permissions/test_check_api.py::test_unknown_user_denied` | ModuleNotFoundError: No module named 'backend.permissions' | `tests/acceptance/permissions/test_check_api.py:234` |
| `tests/acceptance/permissions/test_check_api.py::test_storage_error_denied_fail_closed` | ModuleNotFoundError: No module named 'backend.permissions' | `tests/acceptance/permissions/test_check_api.py:271` |
| `tests/acceptance/permissions/test_check_api.py::test_inactive_user_denied_even_admin` | ModuleNotFoundError: No module named 'backend.permissions' | `tests/acceptance/permissions/test_check_api.py:316` |
| `tests/acceptance/permissions/test_check_api.py::test_session_validation_in_check` | ModuleNotFoundError: No module named 'backend.permissions' | `tests/acceptance/permissions/test_check_api.py:361` |
| `tests/acceptance/permissions/test_check_api.py::test_session_validation_skipped_when_token_none` | ModuleNotFoundError: No module named 'backend.permissions' | `tests/acceptance/permissions/test_check_api.py:440` |
| `tests/acceptance/permissions/test_check_api.py::test_denial_log_and_no_token_leak` | ModuleNotFoundError: No module named 'backend.permissions' | `tests/acceptance/permissions/test_check_api.py:475` |
| `tests/acceptance/permissions/test_check_api.py::test_granted_permission_allowed` | ModuleNotFoundError: No module named 'backend.permissions' | `tests/acceptance/permissions/test_check_api.py:582` |
| `tests/acceptance/permissions/test_check_api.py::test_feature_wildcard_grant` | ModuleNotFoundError: No module named 'backend.permissions' | `tests/acceptance/permissions/test_check_api.py:615` |
| `tests/acceptance/permissions/test_check_api.py::test_unknown_permission_denied_and_grant_rejected` | ModuleNotFoundError: No module named 'backend.permissions' | `tests/acceptance/permissions/test_check_api.py:648` |
| `tests/acceptance/permissions/test_check_api.py::test_multi_role_union_of_permissions` | ModuleNotFoundError: No module named 'backend.permissions' | `tests/acceptance/permissions/test_check_api.py:690` |
| `tests/acceptance/permissions/test_check_api.py::test_assignment_delegates_to_user_manager` | ModuleNotFoundError: No module named 'backend.permissions' | `tests/acceptance/permissions/test_check_api.py:765` |
| `tests/acceptance/permissions/test_check_api.py::test_last_admin_guard_preserved_via_service` | ModuleNotFoundError: No module named 'backend.permissions' | `tests/acceptance/permissions/test_check_api.py:826` |
| `tests/acceptance/permissions/test_check_api.py::test_grant_change_takes_effect_immediately` | ModuleNotFoundError: No module named 'backend.permissions' | `tests/acceptance/permissions/test_check_api.py:876` |
| `tests/acceptance/permissions/test_check_api.py::test_initial_catalog_exactly_60_keys` | ModuleNotFoundError: No module named 'backend.authentication.feature_actions' | `tests/acceptance/permissions/test_check_api.py:1006` |
| `tests/acceptance/permissions/test_enforcement.py::test_principal_defaults_and_fields` | ModuleNotFoundError: No module named 'backend.shared' | `tests/acceptance/permissions/test_enforcement.py:75` |
| `tests/acceptance/permissions/test_enforcement.py::test_standalone_mode_no_check` | ModuleNotFoundError: No module named 'backend.shared' | `tests/acceptance/permissions/test_enforcement.py:102` |
| `tests/acceptance/permissions/test_enforcement.py::test_enforced_method_denies_without_permission` | ModuleNotFoundError: No module named 'backend.permissions' | `tests/acceptance/permissions/test_enforcement.py:128` |
| `tests/acceptance/permissions/test_enforcement.py::test_exempt_login_no_check` | ModuleNotFoundError: No module named 'backend.permissions' | `tests/acceptance/permissions/test_enforcement.py:223` |
| `tests/acceptance/permissions/test_errors.py::test_error_context_attributes` | ModuleNotFoundError: No module named 'backend.permissions' | `tests/acceptance/permissions/test_errors.py:24` |
| `tests/acceptance/permissions/test_events.py::test_events_published_on_operations` | ModuleNotFoundError: No module named 'backend.permissions' | `tests/acceptance/permissions/test_events.py:101` |
| `tests/acceptance/permissions/test_events.py::test_no_publisher_still_works` | ModuleNotFoundError: No module named 'backend.permissions' | `tests/acceptance/permissions/test_events.py:192` |
| `tests/acceptance/permissions/test_role_management.py::test_create_role_and_list` | ModuleNotFoundError: No module named 'backend.permissions' | `tests/acceptance/permissions/test_role_management.py:82` |
| `tests/acceptance/permissions/test_role_management.py::test_delete_role_guards` | ModuleNotFoundError: No module named 'backend.permissions' | `tests/acceptance/permissions/test_role_management.py:118` |
| `tests/acceptance/permissions/test_role_management.py::test_grant_and_revoke_role_permission` | ModuleNotFoundError: No module named 'backend.permissions' | `tests/acceptance/permissions/test_role_management.py:175` |
| `tests/acceptance/permissions/test_role_management.py::test_wildcard_grant_stored_and_matches` | ModuleNotFoundError: No module named 'backend.permissions' | `tests/acceptance/permissions/test_role_management.py:211` |
| `tests/acceptance/permissions/test_system_principal.py::test_system_principal_check_and_set` | ModuleNotFoundError: No module named 'backend.permissions' | `tests/acceptance/permissions/test_system_principal.py:55` |
| `tests/acceptance/permissions/test_system_principal.py::test_system_set_settings_alias_sync` | ModuleNotFoundError: No module named 'backend.permissions' | `tests/acceptance/permissions/test_system_principal.py:100` |
| `tests/acceptance/usermanagement/test_multi_role.py::test_create_user_with_roles_list` | pydantic_core._pydantic_core.ValidationError: 1 validation error for UserCreate | `—` |
| `tests/acceptance/usermanagement/test_multi_role.py::test_add_remove_set_roles` | pydantic_core._pydantic_core.ValidationError: 1 validation error for UserCreate | `—` |
| `tests/acceptance/usermanagement/test_multi_role.py::test_migration_member_to_user_and_role_list` | AttributeError: 'UserRead' object has no attribute 'roles'. Did you mean: 'role'? | `C:/workspace/active-projects/python-template_kopie-worktrees/crosscut/user-roles-permissions/.venv/Lib/site-packages/pydantic/main.py:1042` |
| `tests/acceptance/usermanagement/test_multi_role.py::test_last_admin_guard_all_paths` | pydantic_core._pydantic_core.ValidationError: 1 validation error for UserCreate | `—` |
| `tests/acceptance/usermanagement/test_multi_role.py::test_role_events_carry_lists` | pydantic_core._pydantic_core.ValidationError: 1 validation error for UserCreate | `—` |
| `tests/acceptance/authentication/test_enforcement_wiring.py::test_authentication_enforcement_wiring` | AssertionError: AuthService.begin_passkey_registration: trailing parameter is 'request', expected 'principal' | `tests/acceptance/authentication/test_enforcement_wiring.py:113` |
| `tests/acceptance/settings/test_enforcement_wiring.py::test_settings_enforcement_wiring` | AssertionError: SettingsRegistry.register: trailing parameter is 'definition', expected 'principal' | `tests/acceptance/settings/test_enforcement_wiring.py:110` |
| `tests/acceptance/mail/test_enforcement_wiring.py::test_mail_enforcement_wiring` | AssertionError: MailService.send_email: trailing parameter is 'context', expected 'principal' | `tests/acceptance/mail/test_enforcement_wiring.py:117` |
| `tests/acceptance/sessionmanagement/test_enforcement_wiring.py::test_sessionmanagement_enforcement_wiring` | AssertionError: SessionService.list_sessions: trailing parameter is 'limit', expected 'principal' | `tests/acceptance/sessionmanagement/test_enforcement_wiring.py:100` |
| `tests/property/permissions/test_invariants.py::test_check_true_iff_granted_and_active` | ModuleNotFoundError: No module named 'backend.permissions' | `tests/property/permissions/test_invariants.py:228` |
| `tests/property/permissions/test_invariants.py::test_undeterminable_never_true` | ModuleNotFoundError: No module named 'backend.permissions' | `tests/property/permissions/test_invariants.py:301` |
| `tests/property/permissions/test_invariants.py::test_admin_passes_any_catalog_permission` | ModuleNotFoundError: No module named 'backend.permissions' | `tests/property/permissions/test_invariants.py:371` |
| `tests/property/permissions/test_invariants.py::test_effective_set_monotone` | ModuleNotFoundError: No module named 'backend.permissions' | `tests/property/permissions/test_invariants.py:412` |
| `tests/property/permissions/test_invariants.py::test_valid_grant_keys_exactly_catalog_plus_wildcards` | ModuleNotFoundError: No module named 'backend.permissions' | `tests/property/permissions/test_invariants.py:469` |
| `tests/property/usermanagement/test_multi_role_invariants.py::test_last_admin_invariant` | pydantic_core._pydantic_core.ValidationError: 1 validation error for UserCreate | `—` |
| `tests/unit/permissions/test_edge_cases.py::test_malformed_key_denied` | ModuleNotFoundError: No module named 'backend.permissions' | `tests/unit/permissions/test_edge_cases.py:119` |
| `tests/unit/permissions/test_edge_cases.py::test_unknown_permission_denied` | ModuleNotFoundError: No module named 'backend.permissions' | `tests/unit/permissions/test_edge_cases.py:144` |
| `tests/unit/permissions/test_edge_cases.py::test_unknown_user_denied` | ModuleNotFoundError: No module named 'backend.permissions' | `tests/unit/permissions/test_edge_cases.py:168` |
| `tests/unit/permissions/test_edge_cases.py::test_inactive_user_denied` | ModuleNotFoundError: No module named 'backend.permissions' | `tests/unit/permissions/test_edge_cases.py:192` |
| `tests/unit/permissions/test_edge_cases.py::test_revoked_expired_token_denied` | ModuleNotFoundError: No module named 'backend.permissions' | `tests/unit/permissions/test_edge_cases.py:217` |
| `tests/unit/permissions/test_edge_cases.py::test_mismatched_token_denied` | ModuleNotFoundError: No module named 'backend.permissions' | `tests/unit/permissions/test_edge_cases.py:253` |
| `tests/unit/permissions/test_edge_cases.py::test_unavailable_session_lookup_denied` | ModuleNotFoundError: No module named 'backend.permissions' | `tests/unit/permissions/test_edge_cases.py:283` |
| `tests/unit/permissions/test_edge_cases.py::test_user_deleted_concurrent_denied` | ModuleNotFoundError: No module named 'backend.permissions' | `tests/unit/permissions/test_edge_cases.py:319` |
| `tests/unit/permissions/test_edge_cases.py::test_lookup_raises_denied` | ModuleNotFoundError: No module named 'backend.permissions' | `tests/unit/permissions/test_edge_cases.py:345` |
| `tests/unit/permissions/test_edge_cases.py::test_set_system_unknown_permission` | ModuleNotFoundError: No module named 'backend.permissions' | `tests/unit/permissions/test_edge_cases.py:370` |
| `tests/unit/permissions/test_edge_cases.py::test_set_system_wildcard_allowed` | ModuleNotFoundError: No module named 'backend.permissions' | `tests/unit/permissions/test_edge_cases.py:393` |
| `tests/unit/permissions/test_edge_cases.py::test_token_deleted_user_denied` | ModuleNotFoundError: No module named 'backend.permissions' | `tests/unit/permissions/test_edge_cases.py:415` |
| `tests/unit/permissions/test_edge_cases.py::test_expired_session_denied` | ModuleNotFoundError: No module named 'backend.permissions' | `tests/unit/permissions/test_edge_cases.py:448` |
| `tests/unit/permissions/test_edge_cases.py::test_role_no_mapping_zero_permissions` | ModuleNotFoundError: No module named 'backend.permissions' | `tests/unit/permissions/test_edge_cases.py:533` |
| `tests/unit/permissions/test_edge_cases.py::test_concurrent_thread_safe` | ModuleNotFoundError: No module named 'backend.permissions' | `tests/unit/permissions/test_edge_cases.py:561` |
| `tests/unit/permissions/test_edge_cases.py::test_delete_builtin_role_protected` | ModuleNotFoundError: No module named 'backend.permissions' | `tests/unit/permissions/test_edge_cases.py:611` |
| `tests/unit/permissions/test_edge_cases.py::test_delete_in_use_role` | ModuleNotFoundError: No module named 'backend.permissions' | `tests/unit/permissions/test_edge_cases.py:638` |
| `tests/unit/permissions/test_edge_cases.py::test_create_duplicate_role` | ModuleNotFoundError: No module named 'backend.permissions' | `tests/unit/permissions/test_edge_cases.py:668` |
| `tests/unit/permissions/test_edge_cases.py::test_create_malformed_name` | ModuleNotFoundError: No module named 'backend.permissions' | `tests/unit/permissions/test_edge_cases.py:694` |
| `tests/unit/permissions/test_edge_cases.py::test_grant_unknown_permission` | ModuleNotFoundError: No module named 'backend.permissions' | `tests/unit/permissions/test_edge_cases.py:719` |
| `tests/unit/permissions/test_edge_cases.py::test_unknown_role_operations` | ModuleNotFoundError: No module named 'backend.permissions' | `tests/unit/permissions/test_edge_cases.py:745` |
| `tests/unit/permissions/test_edge_cases.py::test_revoke_absent_idempotent` | ModuleNotFoundError: No module named 'backend.permissions' | `tests/unit/permissions/test_edge_cases.py:774` |
| `tests/unit/permissions/test_edge_cases.py::test_grant_existing_idempotent` | ModuleNotFoundError: No module named 'backend.permissions' | `tests/unit/permissions/test_edge_cases.py:798` |
| `tests/unit/permissions/test_edge_cases.py::test_assignment_unknown_role` | ModuleNotFoundError: No module named 'backend.permissions' | `tests/unit/permissions/test_edge_cases.py:827` |
| `tests/unit/permissions/test_edge_cases.py::test_default_principal_system` | ModuleNotFoundError: No module named 'backend.permissions' | `tests/unit/permissions/test_edge_cases.py:899` |
| `tests/unit/permissions/test_edge_cases.py::test_login_before_permissions` | ModuleNotFoundError: No module named 'backend.permissions' | `tests/unit/permissions/test_edge_cases.py:955` |
| `tests/unit/permissions/test_enforcement_plumbing.py::test_requires_permission_decorator` | ModuleNotFoundError: No module named 'backend.shared' | `tests/unit/permissions/test_enforcement_plumbing.py:58` |
| `tests/integration/permissions/test_persistence.py::test_in_memory_repos_and_singleton` | ModuleNotFoundError: No module named 'backend.permissions' | `tests/integration/permissions/test_persistence.py:48` |
| `tests/integration/permissions/test_persistence.py::test_migration_seeds_roles_and_system_set` | ModuleNotFoundError: No module named 'backend.permissions' | `tests/integration/permissions/test_persistence.py:143` |
| `tests/integration/permissions/test_thread_safety.py::test_concurrent_checks_and_changes` | ModuleNotFoundError: No module named 'backend.permissions' | `tests/integration/permissions/test_thread_safety.py:27` |
| `tests/contract/permissions/test_performance.py::test_check_latency_under_5ms_median` | ModuleNotFoundError: No module named 'backend.permissions' | `tests/contract/permissions/test_performance.py:39` |

- **TDD evidence:** all 77 tests are RED before implementation (Phase 4 turns them GREEN per task).
- **Traceability:** `docs/verification/traceability.md` — new "User Roles & Permissions Matrix" section (40 AC + 6 INV + 26 EDGE + 5 NFR rows + the REQ-024 per-feature wiring tests, all RED).

### Phase 4: Implement — IN PROGRESS

Per-task RED/GREEN evidence (one S4.1 RED confirmation + S4.2 GREEN per DAG task, repeated per task in the DAG).

#### T-001 — S4.1 Pick task + confirm RED — RED CONFIRMED

- **Task:** T-001 "shared enforcement plumbing (Principal, PermissionChecker protocol, requires_permission decorator)" — REQ-025, AC-032.
- **Ready:** confirmed — `dependencies: []` (no dependencies; T-001 is ready).
- **RED command (targeted — the task's 2 tests, from the DAG):**
  `uv run pytest tests/acceptance/permissions/test_enforcement.py::test_principal_defaults_and_fields tests/unit/permissions/test_enforcement_plumbing.py::test_requires_permission_decorator -v`
- **Result:** **2 failed, 0 passed** — RED confirmed before implementation.
- **Failure mode per test** (the established RED pattern for this change — deferred import of the unimplemented shared enforcement plumbing, in the test body, not a setup/collection error):

| Test | Failure mode | Location |
|---|---|---|
| `tests/acceptance/permissions/test_enforcement.py::test_principal_defaults_and_fields` | ModuleNotFoundError: No module named 'backend.shared' | `tests/acceptance/permissions/test_enforcement.py:75` |
| `tests/unit/permissions/test_enforcement_plumbing.py::test_requires_permission_decorator` | ModuleNotFoundError: No module named 'backend.shared' | `tests/unit/permissions/test_enforcement_plumbing.py:58` |

- **Next:** S4.2 (T-001) — implement the shared enforcement plumbing in `src/backend/shared/` and confirm GREEN.

#### T-001 — S4.2 Implement + confirm GREEN — GREEN CONFIRMED

- **Implementation (per T-001 `implementation_steps`, ADR-070/ADR-071):** created the additive `src/backend/shared/` package:
  - `src/backend/shared/principal.py` — the `Principal` model (`user_id: UUID | None = None`, `session_token: str | None = None`; `Principal()` = the system principal, REQ-025), the structural `PermissionChecker` protocol (`require_permission(user_id, permission, session_token=None) -> None`, `has_permission(user_id, permission, session_token=None) -> bool`), and the `requires_permission(permission_key)` decorator: it resolves the wrapped method's trailing `principal` parameter (default `Principal()`), and — when `self._permission_service` is injected — calls `checker.require_permission(principal.user_id, permission_key, session_token=principal.session_token)` at entry; a denial raises and propagates (the method body never runs); with no checker injected (standalone mode) the method runs open.
  - `src/backend/shared/__init__.py` — exports the public API: `Principal`, `PermissionChecker`, `requires_permission`.
  - **No circular import (completion gate):** the package never imports `backend.permissions` (verified at runtime: after `import backend.shared`, `backend.permissions` is absent from `sys.modules`); the decorator calls the injected checker and lets the denial propagate (ADR-070).
- **GREEN command (targeted — the task's 2 tests, from the DAG; run with the DAG's `::` shorthand expanded to real file paths):**
  `uv run pytest tests/acceptance/permissions/test_enforcement.py::test_principal_defaults_and_fields tests/unit/permissions/test_enforcement_plumbing.py::test_requires_permission_decorator -v`
- **Result:** **2 passed, 0 failed** — GREEN confirmed.

| Test | Result |
|---|---|
| `tests/acceptance/permissions/test_enforcement.py::test_principal_defaults_and_fields` (AC-032 / REQ-025) | PASSED |
| `tests/unit/permissions/test_enforcement_plumbing.py::test_requires_permission_decorator` (REQ-025; ADR-070/ADR-071) | PASSED |

- **Ruff (changed paths):** `uv run ruff check src/backend/shared/principal.py src/backend/shared/__init__.py` → All checks passed; `uv run ruff format --check` on the same paths → 2 files already formatted (after an in-step `ruff format` on the new files; GREEN re-confirmed after the format change).
- **Next:** S4.3 (T-001) — ruff gate on the changed paths.

#### T-002 — S4.1 Pick task + confirm RED — RED CONFIRMED

- **Task:** T-002 "usermanagement multi-role amendment (User.roles list, RoleStore, set_roles/add_role/remove_role, last-admin guard on all paths, member→user rename, data migration)" — REQ-013, REQ-026; AC-033, AC-034, AC-035, AC-036, AC-037.
- **Ready:** confirmed — `dependencies: []` (no dependencies; T-002 is ready).
- **RED command (targeted — the task's 6 tests, from the DAG; the DAG's `::` shorthand in the directory part is rejected by pytest, so run with real file paths):**
  `uv run pytest tests/acceptance/usermanagement/test_multi_role.py::test_create_user_with_roles_list tests/acceptance/usermanagement/test_multi_role.py::test_add_remove_set_roles tests/acceptance/usermanagement/test_multi_role.py::test_migration_member_to_user_and_role_list tests/acceptance/usermanagement/test_multi_role.py::test_last_admin_guard_all_paths tests/acceptance/usermanagement/test_multi_role.py::test_role_events_carry_lists tests/property/usermanagement/test_multi_role_invariants.py::test_last_admin_invariant -v`
- **Result:** **6 failed, 0 passed** — RED confirmed before implementation.
- **Failure mode per test** (the established RED pattern for this task — `ValidationError`/`AttributeError` on the pre-amendment model in the test body, not a setup/collection error):

| Test | Failure mode | Location |
|---|---|---|
| `tests/acceptance/usermanagement/test_multi_role.py::test_create_user_with_roles_list` | ValidationError: 1 validation error for UserCreate (pre-amendment model requires `role`; `roles` not accepted) | `tests/acceptance/usermanagement/test_multi_role.py:81` |
| `tests/acceptance/usermanagement/test_multi_role.py::test_add_remove_set_roles` | ValidationError: 1 validation error for UserCreate | `tests/acceptance/usermanagement/test_multi_role.py:104` |
| `tests/acceptance/usermanagement/test_multi_role.py::test_migration_member_to_user_and_role_list` | ValidationError: 1 validation error for UserCreate | `tests/acceptance/usermanagement/test_multi_role.py:263` |
| `tests/acceptance/usermanagement/test_multi_role.py::test_last_admin_guard_all_paths` | AttributeError: 'UserRead' object has no attribute 'roles'. Did you mean: 'role'? | `tests/acceptance/usermanagement/test_multi_role.py` (UserRead attribute access) |
| `tests/acceptance/usermanagement/test_multi_role.py::test_role_events_carry_lists` | ValidationError: 1 validation error for UserCreate | `tests/acceptance/usermanagement/test_multi_role.py:225` |
| `tests/property/usermanagement/test_multi_role_invariants.py::test_last_admin_invariant` | ValidationError: 1 validation error for UserCreate | `tests/property/usermanagement/test_multi_role_invariants.py:36` |

- **Next:** S4.2 (T-002) — implement the usermanagement multi-role amendment (User.roles list, RoleStore, set_roles/add_role/remove_role, last-admin guard on all paths, member→user rename, alembic data migration) and confirm GREEN.
