# Verification: session-management

- **Change type:** FEATURE
- **Classified:** Phase 0 (orchestrator)
- **Rationale:** The change adds externally observable session-management capabilities (active sessions/devices, logout from current/all sessions, session expiration, session revocation) not covered by the approved `docs/specs/authentication.md` spec, which only covers basic session creation/info/logout and revocation on password change/reset. Not a defect (ISSUE); confined to the authentication feature (not CROSS-CUTTING).
- **Overlap check (pending S1.1):** existing session behavior lives in `src/backend/authentication/` (session repository, `session_info`, `logout`); the spec's session-related REQ/AC IDs must be cited in the spec to avoid double work.

## Phase 1 Progress

- **S1.1 Interrogate:** questions Q-34…Q-62 asked and answered (recorded in `AI_Questions.md`); feature brief folded into the spec.
- **S1.2 Draft spec:** `docs/specs/session-management.md` created — **22 REQ, 45 AC, 5 INV, 12 EDGE, 5 NFR**, all with stable IDs, Given/When/Then acceptance criteria, and a test strategy mapping every normative ID.
- **S1.3 Verify self-consistency:** the specification passed the Self-Consistency Checklist (configurability, parameter coverage, REQ↔AC wording, terminology drift, test strategy coverage, ID references, scope consistency, performance budget vs. observability).
- **S1.4 Present for approval — spec approval:** **HUMAN PRE-APPROVAL** recorded in `AI_Questions.md` **Q-62** (2026-09-15: "the pr approval is not necessary for this feature, it is auto approved"). This is a deviation from the standard PR-review gate, authorized by the human: the workflow does NOT stop at the spec-PR-merge gate, and Phase 2 proceeds on this recorded pre-approval. The agent-side human-governance boundary is preserved — the agent still opens the PR and does NOT merge it.
- **S1.4 Present for approval — spec PR:** opened for `feature/session-management` → `main` for traceability: **PR #38** (https://github.com/jackthenet/python-template/pull/38). NOT merged (agent-side human-governance boundary).

## Phase 3 Progress (Test & RED)

### S3.1 Derive tests (per task T-001…T-009)

All 68 DAG `tests_to_create` functions derived and committed to disk:

- `tests/acceptance/sessionmanagement/` (12 test modules + `conftest.py`)
- `tests/integration/sessionmanagement/` (concurrency, device fields, user lifecycle)
- `tests/property/sessionmanagement/` (Hypothesis property tests for INV-001…INV-005)
- `tests/contract/sessionmanagement/` (NFR-001 performance budgets, NFR-003 public API contract)
- `tests/unit/sessionmanagement/` (EDGE-006…EDGE-009 validation)
- `tests/sessionmanagement_test_helpers.py` (shared helpers: `build_session_service`, `make_session`, `EventCollector`, `db_url`)

### S3.2 Ruff + confirm RED

**Ruff gate — `uv run ruff check .`:**

- This phase's contributions are clean. Fixed the 4 ruff errors in this phase's test files (scoped to the two changed files only, `uv run ruff check --fix` + `uv run ruff format`):
  - `tests/acceptance/sessionmanagement/test_events.py:184` (PLR2004) — extracted `num_sessions = 3` constant (preserves the “3 sessions, none revoked” intent).
  - `tests/integration/sessionmanagement/test_concurrency.py:41,55,97` (RUF100) — removed the 3 unused `# noqa: BLE001` directives (BLE001 not enabled).
- Remaining: **6 pre-existing PLR0917 errors in `src/`** — verified present on the `main` baseline (identical file:line set in the primary worktree `C:/workspace/active-projects/python-template_kopie`): `src/backend/authentication/service.py:86`, `src/backend/filemanagement/errors.py:63`, `src/backend/filemanagement/service.py:284`, `src/backend/logging/_decorator.py:71`, `src/backend/logging/_decorator.py:109`, `src/backend/mail/transport.py:44`. These are OUT OF STEP SCOPE (no `src/` touched).

**RED gate — `uv run pytest tests/ -v` (2026-09-17):**

- Result: **20 failed, 489 passed, 1 skipped, 48 errors** (558 collected; collection clean).
- **All 68 session-management tests FAIL** — 48 as `ERROR at setup` (the `session_service` fixture calls `build_session_service`) + 20 as `FAILED` (test body calls `build_session_service` directly).
- **Failure kind (per test):** `ModuleNotFoundError: No module named 'backend.sessionmanagement'` raised at `tests/sessionmanagement_test_helpers.py:97` (`from backend.sessionmanagement import SessionService`) — the house lazy-import pattern: the feature package is imported lazily so the RED state (module missing) surfaces as a per-test fixture/test error, not a collection error. This is the expected RED for a not-yet-implemented feature; no implementation code exists yet.
- **No other new failures vs. the main baseline:** the main baseline (primary worktree, `uv run pytest tests/ -v`) is **489 passed, 1 skipped, 0 failed, 0 errors**. The 489 passed + 1 skipped counts match exactly; the only 1 skip is the pre-existing `tests/acceptance/filemanagement/test_filemanagement.py:364` symlink skip. Zero non-session-management failures. No regressions.

**Evidence:** this section + the traceability matrix (`docs/verification/traceability.md` → “Session Management Matrix”, all 68 tests `RED`).

## Phase 4 Progress (Implement)

### S4.1 (T-001) Pick task + confirm RED

**Task selected:** **T-001** — "Foundation: extend authentication (Session columns, LoginRequest fields, SessionRepository ABC + SqliteSessionRepository), create the sessionmanagement package (events, SessionEntry), and implement SessionService with constructor DI + list_sessions" (from `.github/task-runner/tasks.json`; `dependencies: []` — the first ready task; T-002…T-008 depend on T-001, T-009 on T-002…T-008). Its `implementation_steps` (9 steps), `tests_to_create` (20 tests), `design_constraints` (8), and `green_command` are read from the DAG.

**RED gate — T-001 `red_command` (2026-09-17):**

- Command: `uv run pytest tests/acceptance/sessionmanagement/ tests/property/sessionmanagement/ tests/unit/sessionmanagement/ tests/contract/sessionmanagement/ tests/integration/sessionmanagement/ -v`
- Result: **20 failed, 48 errors in 5.34s** (68 tests; collection clean).
- **Failure kind (per test):** `ModuleNotFoundError: No module named 'backend.sessionmanagement'` — 48 as `ERROR at setup` (the `session_service` fixture → `tests/sessionmanagement_test_helpers.py:97` lazy import) + 20 as `FAILED` (test body calls `build_session_service` directly). The feature package `src/backend/sessionmanagement/` does not exist yet (T-001 creates it) — the expected RED for T-001, consistent with the Phase 3 RED state.
- **RED confirmed:** T-001's tests FAIL before implementation. No implementation code written in this step; no test modifications.

### S4.2 (T-001) Implement + confirm GREEN

**Implementation (per T-001 `implementation_steps`, 9 steps; no test modifications):**

1. `src/backend/authentication/models.py` — `Session` table gains nullable columns `user_agent`, `ip`, `device_name`, `login_method` (all default `None`; existing rows remain `NULL`) (REQ-016, ADR-062); `LoginRequest` gains optional `user_agent`, `ip`, `device_name` fields (all default `None`) (REQ-016, ADR-062).
2. `src/backend/authentication/repositories.py` — `SessionRepository` ABC extended additively (REQ-017, ADR-061, authentication NFR-003): new abstract methods `get(session_id) -> Session | None`, `list_for_user(user_id) -> Sequence[Session]`, `revoke_user_sessions(user_id, exclude_session_id=None) -> int`; `delete_expired` signature extended to `delete_expired(limit: int | None = None) -> int` (backward-compatible optional `limit`, `None` = all = previous behavior). All existing ABC methods retain their behavior.
3. `src/backend/authentication/repository.py` — `SqliteSessionRepository` implements the new methods: `get` (row by id, any revocation state), `list_for_user` (ALL rows for the user, any revocation state, `created_at` descending), `revoke_user_sessions` (revoke all for the user except the excluded, return the count of newly revoked), `delete_expired(limit)` (delete up to `limit` expired rows, return the count).
4. `src/backend/sessionmanagement/events.py` — NEW: `SessionRevoked`, `AllSessionsRevoked`, `ExpiredSessionsDeleted`, `SessionsListed` (frozen Pydantic models; non-sensitive data only — user ids, session ids, counts; never raw tokens or token hashes, REQ-018, REQ-021, NFR-002) + structural `EventPublisher` protocol.
5. `src/backend/sessionmanagement/models.py` — NEW: `SessionEntry` frozen Pydantic model (`session_id`, `created_at`, `expires_at`, `is_current`, `user_agent`, `ip`, `device_name`, `login_method`) (REQ-004, NFR-002).
6. `src/backend/sessionmanagement/service.py` — NEW: `SessionService(repository, event_bus=None, settings_registry=None)` (constructor DI, REQ-020, ADR-065; a `None` event bus means no events and no subscriptions; a `None` settings registry uses the shared `get_settings_registry()`) with `list_sessions(token=None, user_id=None, limit=None)`: exactly-one-of `token`/`user_id` validation (`ValueError`, REQ-001, EDGE-008); token path resolves via the reused store's `get_by_token_hash(hash_token(token))` and re-raises `InvalidSessionError` for unknown/revoked/expired (REQ-002, ADR-067); valid-only listing (REQ-003, INV-002); device fields `None` for pre-feature rows (REQ-004, EDGE-006); `is_current` True for exactly the token's session, all False on the admin path (REQ-005); ordering `created_at` descending with the current session pinned first (REQ-006, INV-005, ADR-066); bounded by `limit` with no offset — default the live-read `sessionmanagement.max_listed_sessions`, `limit < 1` → `ValueError`, truncate to `limit` (REQ-007, EDGE-009, ADR-066); publishes `SessionsListed(user_id, count)` (REQ-018, AC-037, ADR-068). `_read_setting(registry, key, fallback)` live-read helper (unregistered key → fallback, REQ-019). Traced via `@logged_class(slow_threshold_ms=100, include_args=False)` (REQ-022, NFR-004 — raw tokens never appear in log records).
7. `src/backend/sessionmanagement/__init__.py` — NEW: public API (`SessionService`, `SessionEntry`, the 4 events, `EventPublisher`).
8. No new exception types: argument errors are `ValueError`; invalid-token failures re-raise authentication's `InvalidSessionError` (design constraint 8). No second session store (design constraint 1). Raw tokens/hashes never in entries (only session ids) (design constraint 7).

**GREEN gate — T-001 `green_command` (2026-09-17):**

- Command: `uv run pytest tests/acceptance/sessionmanagement/ tests/property/sessionmanagement/ tests/unit/sessionmanagement/ tests/contract/sessionmanagement/ tests/integration/sessionmanagement/ -v`
- Result: **22 passed, 44 failed, 2 errors** (68 tests).
- **T-001's 20 `tests_to_create` all PASS:** `test_ac_001_list_token_returns_entries_with_current_flag`, `test_ac_002_list_user_id_admin_all_not_current`, `test_ac_003_both_or_neither_token_user_id_value_error`, `test_ac_004_list_invalid_token_raises`, `test_ac_005_list_excludes_expired_rows`, `test_ac_006_list_zero_sessions_empty`, `test_ac_007_pre_feature_row_null_device_fields`, `test_ac_009_list_current_session_pinned_first`, `test_ac_010_list_ordered_created_at_desc`, `test_ac_011_list_default_limit_100`, `test_ac_012_list_explicit_limit_truncates`, `test_ac_013_limit_below_one_value_error`, `test_ac_033_same_sessions_table_as_authentication`, `test_ac_037_sessions_listed_event`, `test_edge_006_pre_feature_null_fields`, `test_edge_007_expired_rows_excluded`, `test_edge_008_both_or_neither_value_error`, `test_edge_009_limit_below_one_value_error`, `test_inv_002_valid_only_listing`, `test_inv_005_current_session_first`.
- **Side-effect passes (2, outside T-001's `tests_to_create`, legitimately satisfied by T-001 behavior):** `test_ac_040_live_read_max_listed_sessions` (live-read of `max_listed_sessions` — implemented in T-001) and `test_nfr_001_list_100_sessions_budget` (listing performance budget — listing is implemented in T-001).
- **Expected-still-failing: 46** (T-002…T-009 operations not implemented yet — revocation, cleanup, cap eviction, lifecycle subscriptions, settings registration, singleton, observability, device storage at login, concurrency): 44 `FAILED` + 2 `ERROR at setup` (`test_ac_041`/`test_ac_043` — `ImportError: cannot import name 'reset_session_service'`, the later-task singleton API).
- **No regressions vs. the main baseline:** `uv run pytest tests/ --ignore=tests/acceptance/sessionmanagement --ignore=tests/property/sessionmanagement --ignore=tests/unit/sessionmanagement --ignore=tests/contract/sessionmanagement --ignore=tests/integration/sessionmanagement` → **489 passed, 1 skipped** (identical to the main baseline's 489 passed + 1 skipped; the single skip is the pre-existing `tests/acceptance/filemanagement/test_filemanagement.py:364` symlink skip). Zero non-session-management failures.

**Ruff gate — `uv run ruff check .` (2026-09-17):**

- Result: **6 errors** — exactly the 6 pre-existing PLR0917 errors on the `main` baseline (`src/backend/authentication/service.py:86`, `src/backend/filemanagement/errors.py:63`, `src/backend/filemanagement/service.py:284`, `src/backend/logging/_decorator.py:71`, `src/backend/logging/_decorator.py:109`, `src/backend/mail/transport.py:44`). No new lint errors from this step's changes; `uv run ruff format --check` is clean on all changed paths (formatting scoped to the changed paths only).

**Evidence:** this section. No commits in this step (S4.5 commits). No test modifications.

### S4.3 (T-001) Ruff

**Ruff gate — `uv run ruff check .` (2026-09-17):**

- Result: **6 errors** — exactly the 6 pre-existing PLR0917 baseline errors (`src/backend/authentication/service.py:86`, `src/backend/filemanagement/errors.py:63`, `src/backend/filemanagement/service.py:284`, `src/backend/logging/_decorator.py:71`, `src/backend/logging/_decorator.py:109`, `src/backend/mail/transport.py:44`). **Zero errors in T-001's changed paths** (`src/backend/authentication/models.py`, `src/backend/authentication/repositories.py`, `src/backend/authentication/repository.py`, `src/backend/sessionmanagement/`).
- **Format gate — `uv run ruff format --check` on T-001's changed paths:** clean — `7 files already formatted` (the 3 authentication files + the 4 `sessionmanagement/` files). No format fixes needed.
- No lint/format fixes were applied, so no test re-run was required (T-001's 20/20 GREEN from S4.2 stands).

**Evidence:** this section. No commits in this step (S4.5 commits). No implementation changes beyond lint/format fixes on T-001's paths (none were needed).

### S4.4 (T-001) Refactor (keep GREEN)

**Refactor applied (2 small, focused, behavior-preserving changes in `src/backend/sessionmanagement/service.py`; all other T-001 paths reviewed and left unchanged):**

1. **Removed an unnecessary lazy import.** `_registry()` imported `get_settings_registry` inside the method body, but the module already imports `from backend.settings import SettingsRegistry` at top level — `backend.settings` is fully loaded at module import time, so the lazy import avoided no circularity. `get_settings_registry` is now part of the top-level import. Pure clarity; zero behavior change.
2. **Single "now at call time" snapshot in `list_sessions`.** The token-path validity check and the valid-only filter each called `datetime.now(UTC)` separately (two instants). Both now evaluate validity against one snapshot taken at call time, matching the INV-002 wording ("`expires_at > now` (at call time)") and making the current-session validity check and the valid-only filter consistent with each other. Behavior-preserving: the current session is valid at the snapshot iff it is in the valid-only list.

**Reviewed, no refactor warranted (recorded per done criterion 1):**
- `src/backend/sessionmanagement/events.py` (frozen `_FrozenEvent` base already dedupes config; non-sensitive-only fields), `models.py` (frozen `SessionEntry`), `__init__.py` (public API = NFR-003 contract) — clean as implemented.
- `src/backend/authentication/models.py` (nullable device columns + optional `LoginRequest` fields, documented) — clean as implemented.
- `src/backend/authentication/repositories.py` (additive ABC extension, documented per method) — clean as implemented.
- `src/backend/authentication/repository.py` — clean as implemented. The `revoke_all_for_user`/`revoke_user_sessions` loop similarity and the three repositories' shared `__init__` blocks are pre-existing (not introduced by T-001) and out of T-001's refactor scope; deduplicating them would also add an internal tracing record on the `revoke_all_for_user` path (not done).

**GREEN gate — T-001 `green_command` after refactor (2026-09-17):**

- Command: `uv run pytest tests/acceptance/sessionmanagement/ tests/property/sessionmanagement/ tests/unit/sessionmanagement/ tests/contract/sessionmanagement/ tests/integration/sessionmanagement/ -v`
- Result: **22 passed, 44 failed, 2 errors** (68 tests) — identical to S4.2.
- **T-001's 20 `tests_to_create` all PASS** (same set as S4.2: AC-001…AC-013 listing/validation tests, AC-033 store reuse, AC-037 event, EDGE-006/007/008/009, INV-002/INV-005).
- **Side-effect passes (2, same as S4.2):** `test_ac_040_live_read_max_listed_sessions`, `test_nfr_001_list_100_sessions_budget`.
- **Expected-still-failing: 46, unchanged (44 FAILED + 2 ERROR at setup).** The 2 errors (`test_ac_041`/`test_ac_043`) fail for the same reason as S4.2: `ImportError: cannot import name 'reset_session_service' from 'backend.sessionmanagement'` (the later-task singleton API, T-007). All 44 FAILED are later-task features (T-002…T-009: revocation, cleanup, cap eviction, lifecycle subscriptions, settings registration, singleton, device storage at login, concurrency).
- **No regressions vs. the main baseline:** `uv run pytest tests/ --ignore=tests/acceptance/sessionmanagement --ignore=tests/property/sessionmanagement --ignore=tests/unit/sessionmanagement --ignore=tests/contract/sessionmanagement --ignore=tests/integration/sessionmanagement` → **489 passed, 1 skipped** (identical to the main baseline's 489 passed + 1 skipped; the single skip is the pre-existing `tests/acceptance/filemanagement/test_filemanagement.py:364` symlink skip). Zero non-session-management failures.

**Ruff gate — `uv run ruff check .` after refactor (2026-09-17):**

- Result: **6 errors** — exactly the 6 pre-existing PLR0917 baseline errors (`src/backend/authentication/service.py:86`, `src/backend/filemanagement/errors.py:63`, `src/backend/filemanagement/service.py:284`, `src/backend/logging/_decorator.py:71`, `src/backend/logging/_decorator.py:109`, `src/backend/mail/transport.py:44`). **Zero errors in T-001's changed paths.**
- **Format gate — `uv run ruff format --check` on T-001's changed paths (scoped to changed paths only):** clean — `7 files already formatted`. No `--fix`/`format` was needed or applied.

**No test modifications. No commits in this step (S4.5 commits).**

**Evidence:** this section.

### S4.1 (T-002) Pick task + confirm RED

**Task picked (2026-09-17):**

- **T-002 — "Revocation operations: revoke_session, logout_all_sessions, logout_other_sessions, revoke_all_sessions"** (REQ-008/009/010/011/018; AC-014…AC-023, AC-034, AC-035; 17 `tests_to_create`).
- Ready: its only dependency, **T-001, is VERIFIED**. T-002 is the first ready task in the DAG (all later tasks are SPECIFIED).
- `red_command` / `green_command` (from the DAG): `uv run pytest tests/acceptance/sessionmanagement/ tests/property/sessionmanagement/ tests/unit/sessionmanagement/ tests/contract/sessionmanagement/ tests/integration/sessionmanagement/ -v`

**RED gate — T-002 `red_command` (2026-09-17):**

- Command: `uv run pytest tests/acceptance/sessionmanagement/ tests/property/sessionmanagement/ tests/unit/sessionmanagement/ tests/contract/sessionmanagement/ tests/integration/sessionmanagement/ -v`
- Result: **44 failed, 22 passed, 2 errors** (68 tests) — identical to the S4.4 (T-001) state.
- **T-002's 17 `tests_to_create` all FAIL (17/17):**
  - 15 × `tests/acceptance/sessionmanagement/test_revocation.py`: `test_ac_014_revoke_session_revokes`, `test_ac_015_revoke_unknown_id_noop`, `test_ac_016_revoke_already_revoked_noop`, `test_ac_017_logout_all_revokes_including_caller`, `test_ac_018_logout_all_invalid_token_raises`, `test_ac_019_logout_other_keeps_caller`, `test_ac_020_logout_other_only_caller_noop`, `test_ac_021_revoke_all_returns_count`, `test_ac_022_revoke_all_excludes_session`, `test_ac_023_revoke_all_zero_sessions`, `test_edge_001_zero_sessions_empty_and_noop`, `test_edge_002_revoke_unknown_id_noop`, `test_edge_003_revoke_already_revoked_noop`, `test_edge_004_logout_all_self_lockout`, `test_edge_005_logout_other_only_caller`.
  - 2 × `tests/acceptance/sessionmanagement/test_events.py`: `test_ac_034_session_revoked_event`, `test_ac_035_all_sessions_revoked_event`.
- **Failure kind (T-002's tests): `AttributeError: 'SessionService' object has no attribute 'revoke_session'`** — the revocation operations are not implemented yet (the tests call `service.revoke_session(...)` / `logout_all_sessions(...)` / `logout_other_sessions(...)` / `revoke_all_sessions(...)` on the T-001 `SessionService`). Confirmed by targeted re-run: `uv run pytest tests/acceptance/sessionmanagement/test_revocation.py tests/acceptance/sessionmanagement/test_events.py::test_ac_034_session_revoked_event tests/acceptance/sessionmanagement/test_events.py::test_ac_035_all_sessions_revoked_event -v` → **17 failed** (same kind).
- **Expected-still-failing, unchanged:** 46 (44 FAILED + 2 ERROR). The 2 errors (`test_ac_041`/`test_ac_043` in `test_singleton.py`) fail at setup on `ImportError: cannot import name 'reset_session_service' from 'backend.sessionmanagement'` (the later module-singleton task's API, not T-002). The remaining 27 FAILED (44 − 17) are other later tasks' features (cleanup, cap eviction, lifecycle subscriptions, settings registration, singleton validation, device storage at login, observability, cross-cutting).
- **Passes (22, unchanged):** T-001's 20 `tests_to_create` + 2 side-effect passes (`test_ac_040_live_read_max_listed_sessions`, `test_nfr_001_list_100_sessions_budget`).

**RED confirmed for T-002.** No implementation code written in this step. No test modifications. No commits in this step (S4.5 commits).

**Evidence:** this section.

### S4.2 (T-002) Implement + confirm GREEN

**Implementation (per T-002 `implementation_steps`, 6 steps; no test modifications):**

1. `src/backend/sessionmanagement/service.py` — the T-001 `SessionService` gains `_resolve_token(token) -> Session` (resolves the token path via the reused store's `get_by_token_hash(hash_token(token))`; an unknown, revoked, or expired token re-raises authentication's `InvalidSessionError` (REQ-002, REQ-009/010, ADR-067)) and the four revocation operations:
   - `revoke_session(session_id) -> None` (REQ-008): revoke via the repository; an unknown or already-revoked id is an idempotent no-op (no error, no event, REQ-008, INV-001, EDGE-002/003); publishes `SessionRevoked(user_id, session_id)` when a session is revoked (REQ-018, AC-034).
   - `logout_all_sessions(token) -> None` (REQ-009): resolve the token via the token path (re-raise `InvalidSessionError` for unknown/revoked/expired, AC-018); revoke all sessions for the user including the caller's own (self-lockout accepted, EDGE-004); publishes `AllSessionsRevoked(user_id, excluded_session_id=None)` when at least one session is revoked.
   - `logout_other_sessions(token) -> None` (REQ-010): resolve the token via the token path (re-raise `InvalidSessionError`, AC-018); revoke all sessions for the user except the caller's; publishes `AllSessionsRevoked(user_id, excluded_session_id=<the caller's session id>)` when at least one session is revoked (EDGE-005: revoking nothing publishes no event).
   - `revoke_all_sessions(user_id, exclude_session_id=None) -> int` (REQ-011): admin, open in-process (no token); revoke via the repository's `revoke_user_sessions`; returns the count (a user with zero revocable sessions yields 0 with no error, AC-023); publishes `AllSessionsRevoked(user_id, excluded_session_id)` when the count > 0.
   - An operation that revokes 0 sessions publishes no event (AC-035, ADR-068).
2. No new exception types: invalid-token failures re-raise authentication's `InvalidSessionError` (design constraint). Revocation is idempotent for re-runs (no error, no state change, no duplicate event, INV-001). Events carry non-sensitive data only (user ids, session ids; never raw tokens or token hashes, REQ-018, NFR-002).
3. Public API export in `__init__.py` unchanged: the four operations are methods on the existing `SessionService`, and the events `SessionRevoked`/`AllSessionsRevoked` are already exported (T-001).

**GREEN gate — T-002 `green_command` (2026-09-18):**

- Command: `uv run pytest tests/acceptance/sessionmanagement/ tests/property/sessionmanagement/ tests/unit/sessionmanagement/ tests/contract/sessionmanagement/ tests/integration/sessionmanagement/ -v`
- **T-002's 17 `tests_to_create` all PASS (17/17)** — targeted re-run: `uv run pytest tests/acceptance/sessionmanagement/test_revocation.py tests/acceptance/sessionmanagement/test_events.py::test_ac_034_session_revoked_event tests/acceptance/sessionmanagement/test_events.py::test_ac_035_all_sessions_revoked_event -q` → **17 passed**.
  - 15 × `tests/acceptance/sessionmanagement/test_revocation.py`: `test_ac_014_revoke_session_revokes`, `test_ac_015_revoke_unknown_id_noop`, `test_ac_016_revoke_already_revoked_noop`, `test_ac_017_logout_all_revokes_including_caller`, `test_ac_018_logout_all_invalid_token_raises`, `test_ac_019_logout_other_keeps_caller`, `test_ac_020_logout_other_only_caller_noop`, `test_ac_021_revoke_all_returns_count`, `test_ac_022_revoke_all_excludes_session`, `test_ac_023_revoke_all_zero_sessions`, `test_edge_001_zero_sessions_empty_and_noop`, `test_edge_002_revoke_unknown_id_noop`, `test_edge_003_revoke_already_revoked_noop`, `test_edge_004_logout_all_self_lockout`, `test_edge_005_logout_other_only_caller`.
  - 2 × `tests/acceptance/sessionmanagement/test_events.py`: `test_ac_034_session_revoked_event`, `test_ac_035_all_sessions_revoked_event`.
- **Full-suite state (excluding the hanging T-009 test — see "Known friction" below):** `uv run pytest <the five sessionmanagement dirs> --deselect tests/acceptance/sessionmanagement/test_observability.py::test_ac_045_traced_methods_no_tokens_in_logs -q` → **42 passed, 23 failed, 2 errors** (67 of 68).
  - **Passed (42):** T-001's 20 `tests_to_create` + 2 side-effect passes (`test_ac_040_live_read_max_listed_sessions`, `test_nfr_001_list_100_sessions_budget`) + **T-002's 17 `tests_to_create`** + 3 later-task tests now incidentally passing (their behavior depends on revocation, which T-002 implements).
  - **Expected-still-failing (23 `FAILED` + 2 `ERROR`, all later tasks T-003…T-009):** cleanup, cap eviction, expiration, settings registration, singleton, observability, device storage at login, user-lifecycle subscriptions, concurrency, contract, property. **Zero T-002 test failures** (confirmed: none of T-002's 17 tests appears in the failure list).
  - The 2 errors (`test_ac_041`/`test_ac_043` in `test_singleton.py`) fail at setup on `ImportError: cannot import name 'reset_session_service'` (the later module-singleton task's API, T-007, not T-002).
- **No regressions vs. the main baseline:** `uv run pytest tests/ --ignore=<the five sessionmanagement dirs>` → **488 passed, 1 failed, 1 skipped**. The single failure is `tests/property/filemanagement/test_filemanagement_properties.py::test_inv_005_avatar_url_format` — a **flaky Hypothesis property test** (passes in isolation 3/3; the T-002 change only touched `src/backend/sessionmanagement/service.py` and does not touch filemanagement) — **not a T-002 regression**. The S4.2 (T-001) baseline was 489 passed + 1 skipped; the single skip is the pre-existing `tests/acceptance/filemanagement/test_filemanagement.py:364` symlink skip.

**Ruff gate — `uv run ruff check .` (2026-09-18):**

- Result: **6 errors** — exactly the 6 pre-existing PLR0917 baseline errors (`src/backend/authentication/service.py:86`, `src/backend/filemanagement/errors.py:63`, `src/backend/filemanagement/service.py:284`, `src/backend/logging/_decorator.py:71`, `src/backend/logging/_decorator.py:109`, `src/backend/mail/transport.py:44`). **Zero errors in T-002's changed path** (`uv run ruff check src/backend/sessionmanagement/service.py` → "All checks passed!").

**Known friction (later-task test, not a T-002 regression):**

- **T-009 `test_ac_045_traced_methods_no_tokens_in_logs` hangs** (loguru enqueue-pipe deadlock). After T-002's implementation, this later-task test (AC-045 observability, T-009) progresses past `revoke_session` (now implemented) to `list_sessions(token="bogus")`, where a `@logged` wrapper's exit/exception log record deadlocks in loguru's `enqueue=True` rotating-file-sink pipe (`multiprocessing.connection._send_bytes`; the writer thread waits in `queues.get`). A faulthandler stack dump confirms the main thread is in loguru `_send_bytes` (called from `_decorator.py:103`), not in any T-002 method. This is a logging-infrastructure issue in a later-task test (T-009), not a T-002 logic bug; it prevents the full `green_command` from running to completion, but T-002's 17 tests (T-002's GREEN definition) all pass.

**GREEN confirmed for T-002.** No commits in this step (S4.5 commits). No test modifications.

**Evidence:** this section.

### S4.3 (T-002) Ruff

**Ruff gate — `uv run ruff check .` (2026-09-18):**

- Result: **6 errors** — exactly the 6 pre-existing PLR0917 baseline errors (`src/backend/authentication/service.py:86`, `src/backend/filemanagement/errors.py:63`, `src/backend/filemanagement/service.py:284`, `src/backend/logging/_decorator.py:71`, `src/backend/logging/_decorator.py:109`, `src/backend/mail/transport.py:44`). **Zero errors in T-002's changed path** (`src/backend/sessionmanagement/service.py`).
- **Format gate — `uv run ruff format --check` on T-002's changed paths:** clean — `1 file already formatted` (`src/backend/sessionmanagement/service.py`). No format fixes needed.
- No lint/format fixes were applied, so no test re-run was required (T-002's 17/17 GREEN from S4.2 stands).

**Evidence:** this section. No commits in this step (S4.5 commits). No implementation changes beyond lint/format fixes on T-002's paths (none were needed).

### S4.4 (T-002) Refactor (keep GREEN)

**Refactor applied (1 small, focused, behavior-preserving change in `src/backend/sessionmanagement/service.py`; all other T-002 paths reviewed and left unchanged):**

1. **Extracted the shared revocation pattern into a private helper `_revoke_user_sessions(user_id, exclude_session_id=None) -> int`.** The pattern "call the repository's `revoke_user_sessions` → publish `AllSessionsRevoked(user_id, excluded_session_id)` when `count > 0`" was duplicated verbatim across all three of T-002's revocation operations (`logout_all_sessions`, `logout_other_sessions`, `revoke_all_sessions`). The helper now owns the repository call and the conditional publish (REQ-018, AC-035, INV-001, EDGE-005); the three public methods delegate to it and keep only their token-resolution / return-count specifics. Behavior-preserving:
   - `logout_all_sessions` previously called `self._repository.revoke_user_sessions(session.user_id)` (no exclude); the helper calls `revoke_user_sessions(user_id, exclude_session_id=None)` — identical per the `SessionRepository` ABC signature (`exclude_session_id: UUID | None = None`).
   - `logout_other_sessions` / `revoke_all_sessions` pass the same `exclude_session_id` as before; `revoke_all_sessions` still returns the count.
   - Publish semantics unchanged in all three: `AllSessionsRevoked` only when `count > 0`, same `user_id`/`excluded_session_id` values.
   - No new tracing records: `@logged_class` skips underscore-prefixed methods (`_is_private_method`), so the helper is untraced like the other private helpers (`_resolve_token`, `_publish`, `_to_entry`).

**Reviewed, no refactor warranted (recorded per done criterion 1):**
- `_resolve_token` (T-002): concise, follows authentication's `session_info` contract (REQ-002); its inline `datetime.now(UTC)` is deliberate — `list_sessions` (T-001) keeps its own call-time snapshot for the INV-002 consistency between the token-path validity check and the valid-only filter, so `list_sessions` must NOT be routed through `_resolve_token` (that would introduce a second instant). Left unchanged.
- `revoke_session` (T-002): already minimal — idempotent no-op for unknown/already-revoked ids (REQ-008, INV-001, EDGE-002, EDGE-003), single publish (REQ-018, AC-034). Left unchanged.
- Docstrings of the three revocation operations: accurate, REQ/AC/EDGE-referenced; unchanged.

**GREEN gate — T-002 `tests_to_create` re-run after refactor (2026-09-18):**

- Command: `uv run pytest tests/acceptance/sessionmanagement/test_revocation.py tests/acceptance/sessionmanagement/test_events.py::test_ac_034_session_revoked_event tests/acceptance/sessionmanagement/test_events.py::test_ac_035_all_sessions_revoked_event -q`
- Result: **17 passed** (17/17) — identical to S4.2/S4.3. No regressions.

**Ruff gate — `uv run ruff check .` after refactor (2026-09-18):**

- Result: **6 errors** — exactly the 6 pre-existing PLR0917 baseline errors (`src/backend/authentication/service.py:86`, `src/backend/filemanagement/errors.py:63`, `src/backend/filemanagement/service.py:284`, `src/backend/logging/_decorator.py:71`, `src/backend/logging/_decorator.py:109`, `src/backend/mail/transport.py:44`). **Zero errors in T-002's changed path** (`uv run ruff check src/backend/sessionmanagement/service.py` → "All checks passed!").
- **Format gate — `uv run ruff format --check` on T-002's changed paths (scoped to changed paths only):** clean — `1 file already formatted` (`src/backend/sessionmanagement/service.py`). No `--fix`/`format` was needed or applied.

**No test modifications. No commits in this step (S4.5 commits).**

**Evidence:** this section.
