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

### S4.1 (T-003) Pick task + confirm RED

**Task picked (2026-09-18):**

- **T-003 — "cleanup_expired (bounded by sessionmanagement.cleanup_batch_size)"** (REQ-012/018; AC-024, AC-025, AC-036; 4 `tests_to_create`).
- Ready: its only dependency, **T-001, is VERIFIED** (T-002 is also VERIFIED). T-003 is the first ready task in the DAG (all later tasks are SPECIFIED).
- `red_command` / `green_command` (from the DAG): `uv run pytest tests/acceptance/sessionmanagement/ tests/property/sessionmanagement/ tests/unit/sessionmanagement/ tests/contract/sessionmanagement/ tests/integration/sessionmanagement/ -v`

**RED gate — T-003 `red_command` (2026-09-18):**

- Command: `uv run pytest tests/acceptance/sessionmanagement/ tests/property/sessionmanagement/ tests/unit/sessionmanagement/ tests/contract/sessionmanagement/ tests/integration/sessionmanagement/ -v`
- **Hang note (known environment issue, not a T-003 logic bug):** the full `red_command` hangs on the later-task T-009 test `test_ac_045_traced_methods_no_tokens_in_logs` (loguru `enqueue=True` file-sink pipe deadlock in a `@logged` wrapper). Recorded with that one test deselected: `uv run pytest <the five sessionmanagement dirs> --deselect tests/acceptance/sessionmanagement/test_observability.py::test_ac_045_traced_methods_no_tokens_in_logs -q`.
- Result: **23 failed, 42 passed, 1 deselected, 2 errors** (67 of 68) — identical to the S4.2 (T-002) GREEN state (nothing has been implemented since T-002).
- **T-003's 4 `tests_to_create` all FAIL (4/4):**
  - 3 × `tests/acceptance/sessionmanagement/test_cleanup.py`: `test_ac_024_cleanup_bounded_by_batch_size`, `test_ac_025_cleanup_no_expired_returns_zero`, `test_edge_012_cleanup_below_batch_size`.
  - 1 × `tests/acceptance/sessionmanagement/test_events.py`: `test_ac_036_expired_sessions_deleted_event`.
- **Failure kind (T-003's tests): `AttributeError: 'SessionService' object has no attribute 'cleanup_expired'`** — `cleanup_expired` is not implemented yet (the tests call `session_service.cleanup_expired()` on the T-001 `SessionService`). Confirmed by targeted re-run: `uv run pytest tests/acceptance/sessionmanagement/test_cleanup.py::test_ac_024_cleanup_bounded_by_batch_size tests/acceptance/sessionmanagement/test_cleanup.py::test_ac_025_cleanup_no_expired_returns_zero tests/acceptance/sessionmanagement/test_cleanup.py::test_edge_012_cleanup_below_batch_size tests/acceptance/sessionmanagement/test_events.py::test_ac_036_expired_sessions_deleted_event -v` → **4 failed** (same kind).
- **Expected-still-failing, unchanged:** 21 (19 FAILED + 2 ERROR). The 2 errors (`test_ac_041`/`test_ac_043` in `test_singleton.py`) fail at setup on `ImportError: cannot import name 'reset_session_service' from 'backend.sessionmanagement'` (the later module-singleton task's API, T-007, not T-003). The remaining 19 FAILED (23 − 4) are other later tasks' features (cap eviction, expiration-unchanged, user-lifecycle subscriptions, settings registration, singleton validation, device storage at login, observability, cross-cutting).
- **Passes (42, unchanged):** T-001's 20 `tests_to_create` + 2 side-effect passes (`test_ac_040_live_read_max_listed_sessions`, `test_nfr_001_list_100_sessions_budget`) + T-002's 17 `tests_to_create` + 3 later-task tests now incidentally passing (their behavior depends on revocation, which T-002 implements).

**RED confirmed for T-003.** No implementation code written in this step. No test modifications. No commits in this step (S4.5 commits).

**Evidence:** this section.

### S4.2 (T-003) Implement + confirm GREEN

**Implementation (per T-003 `implementation_steps`, 4 steps; no test modifications):**

1. `src/backend/sessionmanagement/service.py` — the `SessionService` gains `cleanup_expired() -> int` (REQ-012, REQ-018, ADR-068):
   - Reads the live `sessionmanagement.cleanup_batch_size` via the existing `_read_setting`/`_registry` helpers (default `DEFAULT_CLEANUP_BATCH_SIZE = 1000`, a new hardcoded fallback constant alongside `DEFAULT_MAX_LISTED_SESSIONS`) (REQ-012, REQ-019).
   - Deletes up to that bound via the repository's `delete_expired(limit)` (the T-001 additive `SessionRepository` extension; `None` = all is the previous behavior, here a bound is always passed) and returns the count (REQ-012).
   - Publishes `ExpiredSessionsDeleted(count)` when the count > 0; deleting 0 rows publishes no event (REQ-018, AC-036, ADR-068). The event already existed (T-001) and is already exported in `__init__.py`.
   - The application calls `cleanup_expired` on its own schedule — no threads or background workers in the feature (REQ-012).
2. No new exception types, no new events, no new repository methods: the method reuses the T-001 `SessionRepository.delete_expired(limit)` and the T-001 `ExpiredSessionsDeleted` event. Expiration semantics are unchanged — cleanup only deletes expired rows (sessions expire per `authentication.session_ttl`; cleanup does not extend, renew, or track activity) (REQ-013, REQ-017). Events carry non-sensitive data only — the count; never raw tokens or token hashes (REQ-018, NFR-002, ADR-068).
3. Public API export in `__init__.py` unchanged: `cleanup_expired` is a method on the existing `SessionService`, and `ExpiredSessionsDeleted` is already exported (T-001). No `__init__.py` change needed.
4. Tracing: `SessionService` is `@logged_class` (T-001); `cleanup_expired` is a public method so it is traced automatically (entry/exit/exception), consistent with the other public operations. No tracing-specific code was added.

**GREEN gate — T-003 `green_command` (2026-09-18):**

- Command: `uv run pytest tests/acceptance/sessionmanagement/ tests/property/sessionmanagement/ tests/unit/sessionmanagement/ tests/contract/sessionmanagement/ tests/integration/sessionmanagement/ -v`
- **T-003's 4 `tests_to_create` all PASS (4/4)** — targeted re-run: `uv run pytest tests/acceptance/sessionmanagement/test_cleanup.py::test_ac_024_cleanup_bounded_by_batch_size tests/acceptance/sessionmanagement/test_cleanup.py::test_ac_025_cleanup_no_expired_returns_zero tests/acceptance/sessionmanagement/test_cleanup.py::test_edge_012_cleanup_below_batch_size tests/acceptance/sessionmanagement/test_events.py::test_ac_036_expired_sessions_deleted_event -v` → **4 passed**.
  - 3 × `tests/acceptance/sessionmanagement/test_cleanup.py`: `test_ac_024_cleanup_bounded_by_batch_size` (AC-024: 150 expired rows, `cleanup_batch_size` 100 → 100 deleted, 100 returned), `test_ac_025_cleanup_no_expired_returns_zero` (AC-025: no expired rows → 0 returned, no error, valid rows untouched), `test_edge_012_cleanup_below_batch_size` (EDGE-012: 3 expired rows < `cleanup_batch_size` 100 → all deleted, count returned).
  - 1 × `tests/acceptance/sessionmanagement/test_events.py`: `test_ac_036_expired_sessions_deleted_event` (AC-036: `cleanup_expired` deletes `n > 0` rows → `ExpiredSessionsDeleted(n)` published with `count == n`; deleting 0 rows → no event).
- **Full-suite state (excluding the hanging T-009 test — see "Known friction" below):** `uv run pytest <the five sessionmanagement dirs> --deselect tests/acceptance/sessionmanagement/test_observability.py::test_ac_045_traced_methods_no_tokens_in_logs -q` → **50 passed, 15 failed, 2 errors** (67 of 68).
  - **Passed (50):** T-001's 20 `tests_to_create` + 2 side-effect passes (`test_ac_040_live_read_max_listed_sessions`, `test_nfr_001_list_100_sessions_budget`) + T-002's 17 `tests_to_create` + 3 later-task tests incidentally passing (revocation-dependent) + **T-003's 4 `tests_to_create`** + **4 later-task tests now incidentally passing** (their tests call `cleanup_expired`, which T-003 implements): `test_ac_026_expiration_unchanged_no_activity_tracking` (expiration), `test_nfr_001_cleanup_1000_rows_budget` (performance), `test_nfr_005_concurrent_threads_safe` (concurrency), `test_inv_004_no_tokens_in_outputs` (property).
  - **Expected-still-failing (15 `FAILED` + 2 `ERROR`, all later tasks T-004…T-009):** cap eviction (`test_ac_027`, `test_ac_028`, `test_edge_011`, `test_inv_003`), user-lifecycle subscriptions (`test_ac_029`, `test_ac_030`, `test_ac_031`, `test_ac_038`), settings registration (`test_ac_039`), singleton (`test_ac_042` + the 2 setup errors `test_ac_041`/`test_ac_043`), device storage at login (`test_ac_008`, `test_ac_032`), observability (`test_ac_044`, `test_nfr_004`), contract (`test_nfr_003`). **Zero T-003 test failures** (confirmed: none of T-003's 4 tests appears in the failure list).
  - The 2 errors (`test_ac_041`/`test_ac_043` in `test_singleton.py`) fail at setup on `ImportError: cannot import name 'reset_session_service'` (the later module-singleton task's API, T-007, not T-003).
- **No regressions vs. the S4.1 (T-003) RED state:** the RED state was 42 passed / 23 failed / 2 errors; the GREEN state is 50 passed / 15 failed / 2 errors. The delta is exactly +8 passed / −8 failed = T-003's 4 `tests_to_create` (RED → GREEN) + 4 later-task tests that call `cleanup_expired` (RED → GREEN incidentally). No previously-passing test now fails; the 2 errors are unchanged (T-007 singleton setup, not T-003).

**Ruff gate — `uv run ruff check .` (2026-09-18):**

- Result: **6 errors** — exactly the 6 pre-existing PLR0917 baseline errors (`src/backend/authentication/service.py:86`, `src/backend/filemanagement/errors.py:63`, `src/backend/filemanagement/service.py:284`, `src/backend/logging/_decorator.py:71`, `src/backend/logging/_decorator.py:109`, `src/backend/mail/transport.py:44`). **Zero errors in T-003's changed path** (`uv run ruff check src/backend/sessionmanagement/service.py` → "All checks passed!").
- **Format gate — `uv run ruff format --check` on T-003's changed path:** clean — `1 file already formatted` (`src/backend/sessionmanagement/service.py`). One cosmetic reformat of the new `cleanup_expired` body (collapsing the `_read_setting` call to one line, within the 120 line-length) was applied during this step; T-003's 4 tests were re-run after it and still pass 4/4.

**Known friction (later-task test, not a T-003 regression):**

- **T-009 `test_ac_045_traced_methods_no_tokens_in_logs` hangs** (loguru `enqueue=True` file-sink pipe deadlock in a `@logged` wrapper). This later-task test (AC-045 observability, T-009) prevents the full `green_command` from running to completion; it was deselected for the full-suite state above. This is a logging-infrastructure issue in a later-task test (T-009), not a T-003 logic bug; T-003's 4 tests (T-003's GREEN definition) all pass.

**GREEN confirmed for T-003.** No commits in this step (S4.5 commits). No test modifications.

**Evidence:** this section.

### S4.3 (T-003) Ruff

**Ruff gate — `uv run ruff check .` (2026-09-18):**

- Result: **6 errors** — exactly the 6 pre-existing PLR0917 baseline errors (`src/backend/authentication/service.py:86`, `src/backend/filemanagement/errors.py:63`, `src/backend/filemanagement/service.py:284`, `src/backend/logging/_decorator.py:71`, `src/backend/logging/_decorator.py:109`, `src/backend/mail/transport.py:44`). **Zero errors in T-003's changed path** (`src/backend/sessionmanagement/service.py`; `uv run ruff check src/backend/sessionmanagement/service.py` → "All checks passed!").
- **Format gate — `uv run ruff format --check` on T-003's changed paths:** clean — `1 file already formatted` (`src/backend/sessionmanagement/service.py`). No format fixes needed.
- No lint/format fixes were applied, so no test re-run was required (T-003's 4/4 GREEN from S4.2 stands).

**Evidence:** this section. No commits in this step (S4.5 commits). No implementation changes beyond lint/format fixes on T-003's paths (none were needed).

### S4.4 (T-003) Refactor (keep GREEN)

**No refactor applied (recorded per done criterion 1 — the code is already clean and there is no safe, in-scope improvement; no change forced):**

T-003's implementation is a single public method `cleanup_expired() -> int` plus the hardcoded fallback constant `DEFAULT_CLEANUP_BATCH_SIZE = 1000` (alongside `DEFAULT_MAX_LISTED_SESSIONS`). Structure review (duplication, complexity, naming, boundaries):

- **Duplication — none in scope.** The live setting read reuses the existing `_read_setting`/`_registry` helpers (no settings-logic duplication); the same 2-line `int(self._read_setting(self._registry(), key, fallback))` pattern also appears in `list_sessions` (T-001). Extracting a `_read_int_setting` helper would (a) require modifying `list_sessions` (T-001's code, outside T-003's scope) and (b) if only `cleanup_expired` used it, leave a single-caller helper with zero dedup benefit — an unjustified abstraction. The conditional publish `if count > 0: self._publish(...)` mirrors the pattern in `_revoke_user_sessions` (T-002) but with a different event (`ExpiredSessionsDeleted(count)` vs. `AllSessionsRevoked(user_id, excluded_session_id)`); a generic helper would require an event factory — over-abstraction.
- **Complexity — minimal.** One branch (`if count > 0`), one repository call (`delete_expired(batch_size)`), one publish. Nothing to simplify.
- **Naming — clean.** `cleanup_expired` / `batch_size` / `count` are descriptive and consistent with the other operations.
- **Boundaries — correct.** Uses the T-001 `SessionRepository.delete_expired(limit)` ABC extension, the T-001 `ExpiredSessionsDeleted` event, the existing private helpers, and the shared settings registry (REQ-019). No cross-feature internal imports; no new public API (`cleanup_expired` is a method on the existing `SessionService`; the event is already exported).
- **Tracing — unchanged.** `cleanup_expired` is a public method, so it is traced automatically by `@logged_class` (entry/exit/exception); no new private helper means no new untraced method.

**GREEN gate — T-003 `tests_to_create` re-run (2026-09-18):**

- Command: `uv run pytest tests/acceptance/sessionmanagement/test_cleanup.py::test_ac_024_cleanup_bounded_by_batch_size tests/acceptance/sessionmanagement/test_cleanup.py::test_ac_025_cleanup_no_expired_returns_zero tests/acceptance/sessionmanagement/test_cleanup.py::test_edge_012_cleanup_below_batch_size tests/acceptance/sessionmanagement/test_events.py::test_ac_036_expired_sessions_deleted_event -v`
- Result: **4 passed** (4/4) — identical to S4.2/S4.3. No regressions.

**Ruff gate:** n/a — no implementation files were modified in this step (the S4.3 (T-003) ruff gate stands: 6 pre-existing PLR0917 baseline errors, zero in T-003's paths).

**No test modifications. No commits in this step (S4.5 commits). No implementation changes.**

**Evidence:** this section.

### S4.1 (T-004) Pick task + confirm RED

**Task picked (2026-09-18):**

- **T-004 — "Per-user session cap: event-driven eviction on LoginSucceeded (oldest first)"** (REQ-014, REQ-019; AC-027, AC-028; 4 `tests_to_create`).
- Ready: its only dependency, **T-001, is VERIFIED** (T-002 and T-003 are also VERIFIED). T-004 is the first ready task in the DAG (all later tasks T-005…T-009 are SPECIFIED).
- `red_command` / `green_command` (from the DAG): `uv run pytest tests/acceptance/sessionmanagement/ tests/property/sessionmanagement/ tests/unit/sessionmanagement/ tests/contract/sessionmanagement/ tests/integration/sessionmanagement/ -v`

**RED gate — T-004 `red_command` (2026-09-18):**

- Command: `uv run pytest tests/acceptance/sessionmanagement/ tests/property/sessionmanagement/ tests/unit/sessionmanagement/ tests/contract/sessionmanagement/ tests/integration/sessionmanagement/ -v`
- **Hang note (known environment issue, not a T-004 logic bug):** the full `red_command` hangs on the later-task T-009 test `test_ac_045_traced_methods_no_tokens_in_logs` (loguru `enqueue=True` file-sink pipe deadlock in a `@logged` wrapper). Confirmed this run: the full command collected 68 items and hung at that test. Recorded with that one test deselected: `uv run pytest <the five sessionmanagement dirs> --deselect tests/acceptance/sessionmanagement/test_observability.py::test_ac_045_traced_methods_no_tokens_in_logs -v`.
- Result: **15 failed, 50 passed, 1 deselected, 2 errors** (67 of 68) — identical to the S4.2 (T-003) GREEN state (nothing has been implemented since T-003).
- **T-004's 4 `tests_to_create` all FAIL (4/4):**
  - 3 × `tests/acceptance/sessionmanagement/test_cap_eviction.py`: `test_ac_027_cap_evicts_oldest_at_sixth_login`, `test_ac_028_no_eviction_below_cap`, `test_edge_011_cap_eviction_at_exact_cap`.
  - 1 × `tests/property/sessionmanagement/test_sessionmanagement_properties.py`: `test_inv_003_cap_held_after_login`.
- **Failure kind (T-004's tests):**
  - `test_ac_027`: `AssertionError` (line 93, `oldest_row.id not in ids` — the oldest session is still listed after the 6th login; the cap-eviction handler is not implemented).
  - `test_ac_028`: `AttributeError: 'tuple' object has no attribute 'id'` (line 117 — see the potential-test-bug note below; the first assert, `len(entries) == existing + 1`, passes).
  - `test_edge_011`: `AssertionError` (line 138, `oldest_row.id not in ids` — the oldest session is still listed at exactly the cap).
  - `test_inv_003`: `AssertionError` (line 101, `len(entries) <= cap` → `assert 2 <= 1` — the cap is not held after login; Hypothesis falsifying example `existing=1, cap=1`).
- Confirmed by targeted re-run: `uv run pytest tests/acceptance/sessionmanagement/test_cap_eviction.py::test_ac_027_cap_evicts_oldest_at_sixth_login tests/acceptance/sessionmanagement/test_cap_eviction.py::test_ac_028_no_eviction_below_cap tests/acceptance/sessionmanagement/test_cap_eviction.py::test_edge_011_cap_eviction_at_exact_cap tests/property/sessionmanagement/test_sessionmanagement_properties.py::test_inv_003_cap_held_after_login -v` → **4 failed** (same kinds).
- **Potential test bug (flagged for the orchestrator; this step does NOT modify tests):** `test_ac_027` (line 94) and `test_ac_028` (line 117) both evaluate `{r.id for r in rows...}`, but `rows` is a list of `(Session, str)` tuples — `make_session` (`tests/sessionmanagement_test_helpers.py`) returns `(row, raw_token)`. `test_ac_027` currently fails earlier (line 93, missing eviction), but with a correct implementation it would crash with `AttributeError` on line 94; `test_ac_028` crashes on line 117 today. **Consequence: T-004's GREEN gate (all 4 pass) cannot be achieved by implementation alone — these two test lines need a test fix (re-derived via the appropriate workflow step) before/with S4.2.**
- **Expected-still-failing, unchanged:** 13 (11 FAILED + 2 ERROR) — later tasks T-005…T-009:
  - T-005 user-lifecycle subscriptions: `test_ac_029_password_change_revokes_all`, `test_ac_030_deactivation_revokes_all`, `test_ac_031_deletion_revokes_all` (3 FAILED).
  - T-006 device storage at login: `test_ac_008_login_stores_device_fields`, `test_ac_032_passkey_login_stores_method` (2 FAILED).
  - T-007 settings registration: `test_ac_039_register_settings_defaults` (1 FAILED).
  - T-008 module singleton: `test_ac_042_singleton_first_call_without_repository_value_error` (1 FAILED) + `test_ac_041`/`test_ac_043` (2 ERROR at setup on `ImportError: cannot import name 'reset_session_service' from 'backend.sessionmanagement'` — the later singleton API, not T-004).
  - T-009 cross-cutting: `test_ac_038_none_publisher_no_events_no_subscriptions`, `test_ac_044_no_tokens_in_outputs`, `test_nfr_004_traced_service_publishes_events`, `test_nfr_003_public_api_contract` (4 FAILED) + `test_ac_045_traced_methods_no_tokens_in_logs` (HANG — the deselected test).
- **Passes (50, unchanged):** identical to the S4.2 (T-003) GREEN state — T-001's 20 `tests_to_create` + 2 side-effect passes (`test_ac_040_live_read_max_listed_sessions`, `test_nfr_001_list_100_sessions_budget`) + T-002's 17 `tests_to_create` + 3 revocation-dependent later-task passes + T-003's 4 `tests_to_create` + 4 cleanup-dependent later-task passes.

**RED confirmed for T-004.** No implementation code written in this step. No test modifications. No commits in this step (S4.5 commits).

**Evidence:** this section.

### S3.1 (T-004) Fix test bug — re-derive buggy assertion lines

**Date:** 2026-09-18

**Scope:** fix ONLY the two set-comprehension lines flagged by S4.1 (T-004) that call `.id` on `(Session, str)` tuples, aligning the tests with the `make_session` helper contract (`tests/sessionmanagement_test_helpers.py` — returns `(row, raw_token)`). The asserted behavior (AC-027, AC-028, EDGE-011, INV-003; REQ-014) is unchanged — this is a mechanical alignment, not a weakening.

**The two exact line changes** in `tests/acceptance/sessionmanagement/test_cap_eviction.py`:

1. `test_ac_027_cap_evicts_oldest_at_sixth_login` (line 94):
   - before: `assert ids == {r.id for r in rows[1:]} | {new_row.id}`
   - after:  `assert ids == {r[0].id for r in rows[1:]} | {new_row.id}`
2. `test_ac_028_no_eviction_below_cap` (line 117):
   - before: `assert {e.session_id for e in entries} == {r.id for r in rows} | {new_row.id}`
   - after:  `assert {e.session_id for e in entries} == {r[0].id for r in rows} | {new_row.id}`

No other test changes, no implementation changes, no helper changes.

**Bug-pattern grep result (sanity):** grepped all sessionmanagement test dirs (`tests/acceptance/sessionmanagement/`, `tests/property/sessionmanagement/`, `tests/integration/sessionmanagement/`, `tests/unit/sessionmanagement/`, `tests/contract/sessionmanagement/`) for set comprehensions / loops over the tuple-returning `make_session` results (single-variable `for r in rows` / `for row in ...` followed by `.id` on the tuple) and audited every `make_session` call site. **No other occurrence.** All other tuple-consuming sites unpack correctly (`row, _ in rows`, `rows[i][0].id`, `for _, token in rows`).

**Targeted re-run (2026-09-18):**

- Command: `uv run pytest tests/acceptance/sessionmanagement/test_cap_eviction.py tests/property/sessionmanagement/test_sessionmanagement_properties.py -v`
- Result: **3 failed, 5 passed** — T-004's 4 tests:
  - `test_ac_027_cap_evicts_oldest_at_sixth_login` — **FAIL** (`AssertionError`, line 93, `oldest_row.id not in ids` — the oldest session is still listed after the 6th login; the cap-eviction handler is not implemented. Correct RED reason.)
  - `test_ac_028_no_eviction_below_cap` — **PASS** (below-cap login revokes nothing — that IS the correct behavior, so it is legitimately GREEN pre-implementation.)
  - `test_edge_011_cap_eviction_at_exact_cap` — **FAIL** (`AssertionError`, line 138, `oldest_row.id not in ids` — the oldest session is still listed at exactly the cap. Correct RED reason.)
  - `test_inv_003_cap_held_after_login` — **FAIL** (`AssertionError`, line 101, `len(entries) <= cap` → `assert 2 <= 1` — the cap is not held after login. Correct RED reason.)
  - The other 4 passed tests are the unrelated property tests (`test_inv_001`, `test_inv_002`, `test_inv_004`, `test_inv_005`).
- **Failure kind:** all 3 failures are `AssertionError` on behavior lines (no eviction), **not** setup/fixture/`AttributeError` errors — the test contract is sound; RED is now for the correct reason.

**Ruff gate:** `uv run ruff check .` → 6 pre-existing PLR0917 errors, all in `src/backend/` files NOT touched by this change branch (`authentication/service.py`, `filemanagement/errors.py`, `filemanagement/service.py`, `logging/_decorator.py` ×2, `mail/transport.py`) — confirmed pre-existing by stashing this step's change and re-running (same 6). Zero in this step's changed paths: `uv run ruff check tests/` → "All checks passed!".

**RED re-confirmed for T-004** (3 of the 4 fail for the correct reason; `test_ac_028` legitimately GREEN pre-implementation).

No implementation changes. No commits in this step (S4.5 commits).

**Evidence:** this section.

### S3.1 (T-004) Fix test bug (2) — re-derive test_edge_011 final assertion

**Date:** 2026-09-18

**Scope:** fix ONLY the final assertion of `test_edge_011_cap_eviction_at_exact_cap` (`tests/acceptance/sessionmanagement/test_cap_eviction.py`, the last line of the test) so it asserts the spec-mandated behavior — the new session is valid through the token path and pinned first — instead of comparing incompatible things. The asserted behavior (EDGE-011 / REQ-014) is unchanged — this is a mechanical alignment, not a weakening.

**Why it is a test-contract bug (spec IDs):** the spec mandates the token path returns the FULL valid list with the current session pinned first — **REQ-006** (list ordered `created_at` descending, current session pinned first), **AC-009** (`list_sessions(token)` returns the current entry first AND the remaining entries ordered `created_at` descending), **INV-005** (first entry of `list_sessions(token)` is the resolved session). After the eviction at exactly the cap, the token path correctly returns **5 entries** (new session pinned first + the 4 other valid sessions). The buggy right-hand side `[new_row.id]` is a 1-element list — the comparison could never pass under any correct implementation.

**The exact line change** in `tests/acceptance/sessionmanagement/test_cap_eviction.py` (final assertion of `test_edge_011_cap_eviction_at_exact_cap`):

- before: `assert [e.session_id for e in token_entries] == [new_row.id]`
- after:  `assert token_entries[0].session_id == new_row.id`
- added (spec-mandated size, INV-003): `assert len(token_entries) == cap`

The size assertion is spec-mandated: the token path returns the full valid list (REQ-006, INV-005) and, after eviction at exactly the cap, the user has exactly `cap` valid sessions (INV-003); `max_listed_sessions` is unregistered in this test (fallback 100 > cap 5), so no truncation. No other test changes, no implementation changes, no helper changes.

**Targeted re-run (2026-09-18):**

- Command: `uv run pytest tests/acceptance/sessionmanagement/test_cap_eviction.py tests/property/sessionmanagement/test_sessionmanagement_properties.py::test_inv_003_cap_held_after_login -v`
- Result: **4 passed** (4/4) — T-004's 4 `tests_to_create` all PASS (the implementation is in the tree, so GREEN is now achievable):
  - `test_ac_027_cap_evicts_oldest_at_sixth_login` — PASS
  - `test_ac_028_no_eviction_below_cap` — PASS
  - `test_edge_011_cap_eviction_at_exact_cap` — PASS (the fixed final assertion now passes)
  - `test_inv_003_cap_held_after_login` — PASS

**Ruff gate:** `uv run ruff check tests/` → "All checks passed!" (zero errors in the changed path).

No implementation changes. No commits in this step (S4.5 commits).

**Evidence:** this section.

### S4.2 (T-004) Implement + confirm GREEN

**Implementation (already in place per T-004 `implementation_steps`, 4 steps; no test modifications, no implementation modifications in this step — this step only confirms GREEN, runs ruff, and records evidence):**

1. `src/backend/sessionmanagement/service.py` — `SessionService.__init__` subscribes the authentication `LoginSucceeded` event to `self._on_login_succeeded` on the shared event bus, only when `event_bus is not None` (REQ-014, ADR-063).
2. `_on_login_succeeded` live-reads `sessionmanagement.max_sessions_per_user` (default `DEFAULT_MAX_SESSIONS_PER_USER = 5`); if the user's valid (unrevoked, unexpired) session count exceeds the cap, it revokes the OLDEST valid sessions (`created_at` ascending) until the count equals the cap — the newly-issued session is always kept (REQ-014, REQ-019, ADR-063).
3. Idempotent no-op at/below cap: no error, no state change, no duplicate event (INV-001, ADR-063).
4. After `LoginSucceeded` handling, the user's valid session count is at most the cap (INV-003).

**GREEN gate — T-004 `green_command` (2026-09-18):**

- Broader-suite command (the hanging later-task T-009 test deselected): `uv run pytest tests/acceptance/sessionmanagement/ tests/property/sessionmanagement/ tests/unit/sessionmanagement/ tests/contract/sessionmanagement/ tests/integration/sessionmanagement/ --deselect tests/acceptance/sessionmanagement/test_observability.py::test_ac_045_traced_methods_no_tokens_in_logs -v`
- Result: **11 failed, 54 passed, 1 deselected, 2 errors** (67 of 68).
- **T-004's 4 `tests_to_create` all PASS (4/4)** — targeted re-run: `uv run pytest tests/acceptance/sessionmanagement/test_cap_eviction.py tests/property/sessionmanagement/ -k "ac_027 or ac_028 or edge_011 or inv_003" -v` → **4 passed, 4 deselected**:
  - `test_ac_027_cap_evicts_oldest_at_sixth_login` (AC-027) — PASSED
  - `test_ac_028_no_eviction_below_cap` (AC-028) — PASSED
  - `test_edge_011_cap_eviction_at_exact_cap` (EDGE-011) — PASSED
  - `test_inv_003_cap_held_after_login` (INV-003, property) — PASSED
- **Completion gates met:** AC-027/AC-028 acceptance tests pass; EDGE-011 acceptance test passes; INV-003 property test passes.
- **Pass count vs. S4.1 (T-004) RED baseline:** RED was 50 passed / 15 failed / 2 errors; GREEN is 54 passed / 11 failed / 2 errors. Delta is exactly **+4 passed / −4 failed = T-004's 4 `tests_to_create`** (RED → GREEN). No previously-passing test now fails.
- **The 13 expected-still-failing later-task tests (T-005…T-009) are STILL failing for their OWN reasons** (their tasks are not implemented yet) — **not newly broken by T-004**. The 11 `FAILED` + 2 `ERROR` in the GREEN run are exactly the baseline's 13 later-task tests:
  - T-005 user-lifecycle subscriptions: `test_ac_029_password_change_revokes_all`, `test_ac_030_deactivation_revokes_all`, `test_ac_031_deletion_revokes_all` (3 FAILED) — unchanged.
  - T-006 device storage at login: `test_ac_008_login_stores_device_fields`, `test_ac_032_passkey_login_stores_method` (2 FAILED) — unchanged.
  - T-007 settings registration: `test_ac_039_register_settings_defaults` (1 FAILED) — unchanged.
  - T-008 module singleton: `test_ac_042_singleton_first_call_without_repository_value_error` (1 FAILED) + `test_ac_041`/`test_ac_043` (2 ERROR at setup on `ImportError: cannot import name 'reset_session_service'`) — unchanged.
  - T-009 cross-cutting: `test_ac_038_none_publisher_no_events_no_subscriptions`, `test_ac_044_no_tokens_in_outputs`, `test_nfr_004_traced_service_publishes_events`, `test_nfr_003_public_api_contract` (4 FAILED) + `test_ac_045_traced_methods_no_tokens_in_logs` (HANG — deselected) — unchanged.
  - **No legitimate state change to note:** none of the 13 later-task tests flipped to passing in this run; every one still fails for its own (unimplemented-task) reason. No T-004 test appears in the failure list.
- **Known friction (later-task test, not a T-004 regression):** T-009 `test_ac_045_traced_methods_no_tokens_in_logs` hangs (loguru `enqueue=True` file-sink pipe deadlock in a `@logged` wrapper) — deselected, as in the RED baseline.

**Ruff gate — `uv run ruff check .` (2026-09-18):**

- Result: **6 errors** — exactly the 6 pre-existing PLR0917 baseline errors in other `src/backend/` files (`src/backend/authentication/service.py:86`, `src/backend/filemanagement/errors.py:63`, `src/backend/filemanagement/service.py:284`, `src/backend/logging/_decorator.py:71`, `src/backend/logging/_decorator.py:109`, `src/backend/mail/transport.py:44`). **Zero errors in T-004's changed path** (`src/backend/sessionmanagement/service.py`). Zero NEW errors introduced by T-004.

**GREEN confirmed for T-004.** No commits in this step (S4.5 commits). No test modifications. No implementation modifications.

**Evidence:** this section.

### S4.3 (T-004) Ruff

**Ruff gate (S4.3) — T-004's changed paths (2026-09-18):**

- Command: `uv run ruff check src/backend/sessionmanagement/service.py tests/acceptance/sessionmanagement/test_cap_eviction.py`
- Result: **All checks passed! — ZERO errors in T-004's changed paths.**
- Whole-repo confirmation: `uv run ruff check .` → **6 errors** — exactly the 6 pre-existing PLR0917 baseline errors in other `src/backend/` files (`src/backend/authentication/service.py:86`, `src/backend/filemanagement/errors.py:63`, `src/backend/filemanagement/service.py:284`, `src/backend/logging/_decorator.py:71`, `src/backend/logging/_decorator.py:109`, `src/backend/mail/transport.py:44`). **Zero NEW errors introduced by T-004.**
- No test or implementation modifications in this step (S4.3 only runs ruff and records). No commits (S4.5 commits).

**Evidence:** this section.

### S4.4 (T-004) Refactor (keep GREEN)

**No refactor applied (recorded per done criterion — the code is already clean and minimal; no safe, in-scope improvement; no change forced):**

T-004's implementation is the module constant `DEFAULT_MAX_SESSIONS_PER_USER = 5`, the constructor's `LoginSucceeded` subscription block, and the private cap-eviction handler `_on_login_succeeded()`. Structure review (duplication, complexity, naming, boundaries):

- **Duplication — none in scope.** The valid-sessions filter (`not row.revoked and row.expires_at > now`) also appears in `list_sessions` (T-001's code). Extracting a shared `_valid_sessions` helper would (a) require modifying `list_sessions` (T-001's code, outside T-004's scope) and (b) if used only in `_on_login_succeeded`, leave a single-caller helper with zero dedup benefit — an unjustified abstraction (same reasoning as S4.4 (T-003)). The live cap read already reuses the existing `_read_setting`/`_registry` helpers (no settings-logic duplication).
- **Complexity — minimal.** Read the cap, filter the user's valid sessions, compute `excess = len(valid) - cap`, early-return at/below cap (idempotent no-op — INV-001), revoke the oldest `excess` entries via `valid[-excess:]`. One early return, one loop, no nested branches. The `valid[-excess:]` slice relies on `list_for_user`'s `created_at` descending order (oldest-first eviction) — documented in a comment; the newly issued session (most recent, first entry) is always kept.
- **Naming — clean.** `cap` / `now` / `valid` / `excess` / `_on_login_succeeded` are descriptive and consistent with the service's other members.
- **Boundaries — correct.** Event-driven on authentication's `LoginSucceeded` via the shared event bus — authentication's login path is not modified (REQ-014, ADR-063); a `None` publisher means no subscriptions (REQ-018, AC-038); the cap is live-read on each login (REQ-019); uses the existing `SessionRepository` ABC. No cross-feature internal imports; no new public API.
- **Tracing — unchanged.** `_on_login_succeeded` is private, so it is not traced by `@logged_class` (public methods only), consistent with the other private handlers/helpers; no raw tokens/hashes in any output.

**Observable behavior unchanged:** no code changes in this step; the specified behavior (REQ-014, REQ-019, AC-027, AC-028, EDGE-011, INV-001, INV-003) remains identical.

**GREEN gate — T-004 `tests_to_create` re-run (2026-09-18):**

- Command: `uv run pytest tests/acceptance/sessionmanagement/test_cap_eviction.py tests/property/sessionmanagement/ -k "ac_027 or ac_028 or edge_011 or inv_003" -v`
- Result: **4 passed** (4/4) — identical to S4.2/S4.3. No regressions.

**Ruff gate:** n/a — no implementation files were modified in this step (the S4.3 (T-004) ruff gate stands: zero errors in T-004's changed paths).

**No test modifications. No commits in this step (S4.5 commits). No implementation changes.**

**Evidence:** this section.

### S4.1 (T-005) Pick task + confirm RED

**Date:** 2026-09-18

**Task picked:** T-005 — "Revocation on user lifecycle: subscriptions to UserPasswordChanged, UserDeactivated, UserDeleted" (REQ-015; AC-029, AC-030, AC-031; 3 `tests_to_create`).

**Ready confirmed:** T-005's only dependency is **T-001 (VERIFIED)** — ready. No other task precedes it in the DAG.

**RED gate — T-005 `red_command` (full suite; the hanging later-task T-009 test deselected):**

- Command: `uv run pytest tests/acceptance/sessionmanagement/ tests/property/sessionmanagement/ tests/unit/sessionmanagement/ tests/contract/sessionmanagement/ tests/integration/sessionmanagement/ --deselect tests/acceptance/sessionmanagement/test_observability.py::test_ac_045_traced_methods_no_tokens_in_logs -v`
- Result: **11 failed, 54 passed, 1 deselected, 2 errors** (67 of 68) — **identical counts to the S4.2 (T-004) GREEN baseline** (11 failed / 54 passed / 1 deselected / 2 errors). No previously-passing test now fails.

**T-005's 3 `tests_to_create` — all FAIL (RED) for the CORRECT reason (behavior, not setup/fixture/import):**

| Test | Status | Failure kind |
|------|--------|--------------|
| `test_ac_029_password_change_revokes_all` | FAILED | Behavior assertion at the `wait_for` "Then" clause: `AssertionError: UserPasswordChanged did not revoke all sessions` — the Given (user + 3 valid sessions created, list verified) and When (`change_password` succeeded) both ran; only the expected revocation is absent because the user-lifecycle revocation subscription is **not implemented yet**. |
| `test_ac_030_deactivation_revokes_all` | FAILED | Behavior assertion at the `wait_for` "Then" clause: `AssertionError: UserDeactivated did not revoke all sessions` — same reason (deactivation ran; revocation subscription not implemented). |
| `test_ac_031_deletion_revokes_all` | FAILED | Behavior assertion at the `wait_for` "Then" clause: `AssertionError: UserDeleted did not revoke all sessions` — same reason (deletion ran; revocation subscription not implemented). |

- Targeted re-run confirming the failure kind: `uv run pytest tests/integration/sessionmanagement/test_user_lifecycle.py -v --tb=short` → **3 failed** (16.24s); each traceback's only failing line is the `wait_for(...)` assertion (the "Then" clause) — no setup/fixture/ImportError. This is the expected RED for T-005 (the revocation subscription is the unimplemented behavior).

**T-001…T-004 still GREEN (no regression):** the **54 passed** are unchanged from the S4.2 (T-004) GREEN baseline; no T-001/T-002/T-003/T-004 test appears in the failure list. No previously-passing test now fails.

**The 13 expected-still-failing later-task tests (T-005…T-009) are STILL failing for their OWN reasons** (their tasks are not implemented yet) — **not newly broken by T-005**. The 11 `FAILED` + 2 `ERROR` in this run are exactly the baseline's 13 later-task tests:
  - T-005 user-lifecycle subscriptions: `test_ac_029_password_change_revokes_all`, `test_ac_030_deactivation_revokes_all`, `test_ac_031_deletion_revokes_all` (3 FAILED) — the picked task, RED as expected.
  - T-006 device storage at login: `test_ac_008_login_stores_device_fields`, `test_ac_032_passkey_login_stores_method` (2 FAILED) — unchanged.
  - T-007 settings registration: `test_ac_039_register_settings_defaults` (1 FAILED) — unchanged.
  - T-008 module singleton: `test_ac_042_singleton_first_call_without_repository_value_error` (1 FAILED) + `test_ac_041`/`test_ac_043` (2 ERROR at setup on `ImportError: cannot import name 'reset_session_service'`) — unchanged.
  - T-009 cross-cutting: `test_ac_038_none_publisher_no_events_no_subscriptions`, `test_ac_044_no_tokens_in_outputs`, `test_nfr_004_traced_service_publishes_events`, `test_nfr_003_public_api_contract` (4 FAILED) + `test_ac_045_traced_methods_no_tokens_in_logs` (HANG — deselected) — unchanged.

**RED confirmed for T-005.** No implementation code written in this step; no commits in this step (S4.5 commits). No test modifications.

**Evidence:** this section.

### S4.2 (T-005) Implement + confirm GREEN

- **Date:** 2026-09-18 19:57
- **Objective:** Implement T-005 (user-lifecycle revocation subscriptions) to turn T-005's 3 `tests_to_create` GREEN, then confirm the full GREEN gate.

**Implementation summary** (file changed: `src/backend/sessionmanagement/service.py` only):

1. **Imports:** added `from backend.usermanagement import UserDeactivated, UserDeleted, UserEvent, UserPasswordChanged` (the user-management lifecycle events; `UserEvent` is their common base, used for the handler's parameter type).
2. **Subscriptions (in `SessionService.__init__`, inside the existing `if event_bus is not None:` block):** registered one handler for each of `UserPasswordChanged`, `UserDeactivated`, and `UserDeleted` on the **injected** event bus — the bus where user-management publishes its lifecycle events (user-management is not modified, REQ-015, ADR-064). Guarded by `if hasattr(event_bus, "subscribe"):` so a publisher without subscribe capability (a bare `EventCollector`) gets no subscriptions; a `None` publisher means no subscriptions (REQ-018, REQ-020, AC-038). This is consistent with the T-004 `LoginSucceeded` subscription pattern (a `None`-bus no-subscription guarantee), with the subscription target being the injected bus because that is where the T-005 integration tests' `UserManager` publishes.
3. **Handler:** added `_on_user_lifecycle(self, event: UserEvent) -> None` — on any of the three events it calls the existing `_revoke_user_sessions(event.user_id)` helper, which revokes **all** of the user's sessions via the repository's `revoke_user_sessions` (no exclusion — the newly-issued session is NOT kept; this is a full revocation, unlike cap-eviction) and publishes `AllSessionsRevoked(user_id, excluded_session_id=None)` **only when at least one session is revoked**. Re-runs that revoke nothing change no state and publish no event (INV-001, ADR-064). The `UserPasswordChanged` subscription is idempotent with authentication's reset-completion revocation (authentication REQ-012), which remains unchanged.

No other file changed. No test modified. No new behavior beyond REQ-015/AC-029..AC-031.

**Broader-suite command** (hanging T-009 test deselected, per the known environment issue):

```
uv run pytest tests/acceptance/sessionmanagement/ tests/property/sessionmanagement/ tests/unit/sessionmanagement/ tests/contract/sessionmanagement/ tests/integration/sessionmanagement/ --deselect tests/acceptance/sessionmanagement/test_observability.py::test_ac_045_traced_methods_no_tokens_in_logs -v
```

**Result counts:** **8 failed, 57 passed, 1 deselected, 2 errors** (47.70s).

- **RED baseline (S4.1 (T-005)):** 11 failed, 54 passed, 1 deselected, 2 errors.
- **Delta:** exactly **−3 failed / +3 passed** — T-005's 3 tests moved from failing to passing. Pass count 57 ≥ RED baseline 54.

**T-005's 3 tests PASS** (targeted re-run `uv run pytest tests/integration/sessionmanagement/test_user_lifecycle.py -v` → **3 passed**, 1.17s):

| Test | Status |
|------|--------|
| `test_ac_029_password_change_revokes_all` | PASSED |
| `test_ac_030_deactivation_revokes_all` | PASSED |
| `test_ac_031_deletion_revokes_all` | PASSED |

**T-001…T-004 still GREEN (no regression):** the 57 passed include all T-001/T-002/T-003/T-004 tests; none of `test_list_sessions.py`, `test_store_reuse.py`, `test_revocation.py`, `test_cleanup.py`, `test_cap_eviction.py` (nor `test_user_lifecycle.py`) appears in the failure/error list. No previously-passing test now fails.

**The 10 expected-still-failing later-task tests (T-006…T-009) are STILL failing for their OWN reasons** (their tasks are not implemented yet) — **not newly broken by T-005**. The 8 `FAILED` + 2 `ERROR` in this run are exactly the later-task tests:
  - T-006 device storage at login: `test_ac_008_login_stores_device_fields`, `test_ac_032_passkey_login_stores_method` (2 FAILED) — unchanged.
  - T-007 settings registration: `test_ac_039_register_settings_defaults` (1 FAILED) — unchanged.
  - T-008 module singleton: `test_ac_042_singleton_first_call_without_repository_value_error` (1 FAILED) + `test_ac_041`/`test_ac_043` (2 ERROR at setup on `ImportError: cannot import name 'reset_session_service'`) — unchanged.
  - T-009 cross-cutting: `test_ac_038_none_publisher_no_events_no_subscriptions`, `test_ac_044_no_tokens_in_outputs`, `test_nfr_004_traced_service_publishes_events`, `test_nfr_003_public_api_contract` (4 FAILED) + `test_ac_045_traced_methods_no_tokens_in_logs` (HANG — deselected) — unchanged.

**Ruff:** `uv run ruff check .` → 6 errors, all **pre-existing PLR0917** in other files (`src/backend/authentication/service.py`, `src/backend/filemanagement/errors.py`, `src/backend/filemanagement/service.py`, `src/backend/logging/_decorator.py`, `src/backend/mail/transport.py`). **Zero in T-005's changed path** — `uv run ruff check src/backend/sessionmanagement/` → "All checks passed!".

**No commits in this step (S4.5 commits).** No test modifications.

**Evidence:** this section.

### S4.3 (T-005) Ruff

**Ruff gate (S4.3 (T-005)) — T-005's changed path (2026-09-18):**

- Command: `uv run ruff check src/backend/sessionmanagement/service.py`
- Result: **All checks passed! — ZERO errors in T-005's changed path.**
- Whole-repo confirmation: `uv run ruff check .` → **6 errors** — exactly the 6 pre-existing PLR0917 baseline errors in other `src/backend/` files (`src/backend/authentication/service.py:86`, `src/backend/filemanagement/errors.py:63`, `src/backend/filemanagement/service.py:284`, `src/backend/logging/_decorator.py:71`, `src/backend/logging/_decorator.py:109`, `src/backend/mail/transport.py:44`). **Zero NEW errors introduced by T-005.**
- No test or implementation modifications in this step (S4.3 only runs ruff and records). No commits (S4.5 commits).

**Evidence:** this section.

### S4.4 (T-005) Refactor (keep GREEN)

**Refactor decision (S4.4 (T-005)) — 2026-09-18:**

- **No refactor was made.** The T-005 implementation was reviewed for behavior-preserving structure improvements (duplication, complexity, naming, boundaries) and is already clean and minimal:
  - `_on_user_lifecycle` is a one-line pass-through to the **existing** `_revoke_user_sessions` helper — no duplication introduced, no helper worth extracting (a helper would add indirection without gain).
  - The subscription block is explicit (3 user-management event types → the one handler), with an accurate REQ/ADR-cited comment consistent with the file's style; a loop over a tuple of event types would reduce explicitness, not clarity.
  - The `hasattr(event_bus, "subscribe")` guard is required by the spec (a publisher without `subscribe` — a bare collector — must get no subscriptions without raising); simplifying it would change observable behavior.
  - The import line is single and correctly placed.
- **Observable behavior unchanged:** no code changes were made, so the specified behavior (REQ-015, AC-029, AC-030, AC-031, INV-001) is trivially identical.
- **Sanity GREEN re-run (no changes made, confirmation only):** `uv run pytest tests/ -k "test_ac_029_password_change_revokes_all or test_ac_030_deactivation_revokes_all or test_ac_031_deletion_revokes_all" -v` → **3 passed** (all T-005 tests still GREEN).
- **Ruff:** `n/a` (no changes made; S4.3 (T-005) already confirmed T-005's path clean).
- **No commits in this step (S4.5 commits).** No test modifications.

**Evidence:** this section.

### S4.1 (T-006) Pick task + confirm RED

**Date:** 2026-09-18

**Task picked:** T-006 — "Device identification at login: store device fields + login method on the issued Session row (password + passkey paths)" (REQ-016; AC-008, AC-032; 2 `tests_to_create`).

**Ready confirmed:** T-006's only dependency is **T-001 (VERIFIED)** — ready. No other unverified task precedes it in the DAG (T-002/T-003/T-004/T-005 are VERIFIED and committed).

**RED gate — T-006 `red_command` (full suite; the hanging later-task T-009 test deselected):**

- Command: `uv run pytest tests/acceptance/sessionmanagement/ tests/property/sessionmanagement/ tests/unit/sessionmanagement/ tests/contract/sessionmanagement/ tests/integration/sessionmanagement/ --deselect tests/acceptance/sessionmanagement/test_observability.py::test_ac_045_traced_methods_no_tokens_in_logs -v`
- Result: **8 failed, 57 passed, 1 deselected, 2 errors** (67 of 68) — **identical counts to the S4.2 (T-005) GREEN baseline** (8 failed / 57 passed / 1 deselected / 2 errors). No previously-passing test now fails.

**T-006's 2 `tests_to_create` — both FAIL (RED) for the CORRECT reason (behavior, not setup/fixture/import):**

| Test | Status | Failure kind |
|------|--------|--------------|
| `test_ac_008_login_stores_device_fields` | FAILED | Behavior assertion at the "Then" clause: `AssertionError: assert None == 'Mozilla/5.0 (X11; Linux x86_64) test-agent/1.0'` (`entry.user_agent` is `None`) — the Given (auth service + session service built) and When (password `login` succeeded, a session row was issued, `list_sessions` returned 1 entry with `is_current=True`) all ran; only the expected device-field storage is absent because device identification at login is **not implemented yet** (the Session row's `user_agent`/`ip`/`device_name` remain `None`). |
| `test_ac_032_passkey_login_stores_method` | FAILED | Behavior assertion at the "Then" clause: `AssertionError: assert None == 'passkey'` (`entry.login_method` is `None`) — the Given (user + passkey registered + `begin_passkey_login`) and When (`complete_passkey_login` succeeded, a session row was issued) all ran; only the expected login-method storage is absent because the passkey path does not yet store `login_method='passkey'`. |

- Targeted re-run confirming the failure kind: `uv run pytest "tests/integration/sessionmanagement/test_device_fields.py::test_ac_008_login_stores_device_fields" "tests/integration/sessionmanagement/test_device_fields.py::test_ac_032_passkey_login_stores_method" -v` → **2 failed** (1.15s); each traceback's only failing line is the "Then"-clause assertion on the issued `SessionEntry` (all device fields `None`) — no setup/fixture/ImportError. This is the expected RED for T-006 (storing device fields + login method at login is the unimplemented behavior).

**T-001…T-005 still GREEN (no regression):** the **57 passed** are unchanged from the S4.2 (T-005) GREEN baseline; no T-001/T-002/T-003/T-004/T-005 test appears in the failure list. No previously-passing test now fails.

**The 8 expected-still-failing later-task tests (T-007…T-009) are STILL failing for their OWN reasons** (their tasks are not implemented yet) — **not newly broken by T-006**. The 8 `FAILED` + 2 `ERROR` in this run are exactly the baseline's 10 later-task tests (the 2 T-006 tests are the picked task, RED as expected):
  - T-006 device storage at login: `test_ac_008_login_stores_device_fields`, `test_ac_032_passkey_login_stores_method` (2 FAILED) — the picked task, RED as expected.
  - T-007 settings registration: `test_ac_039_register_settings_defaults` (1 FAILED) — unchanged.
  - T-008 module singleton: `test_ac_042_singleton_first_call_without_repository_value_error` (1 FAILED) + `test_ac_041_singleton_created_once`/`test_ac_043_reset_session_service` (2 ERROR at setup on `ImportError: cannot import name 'reset_session_service'`) — unchanged.
  - T-009 cross-cutting: `test_ac_038_none_publisher_no_events_no_subscriptions`, `test_ac_044_no_tokens_in_outputs`, `test_nfr_004_traced_service_publishes_events`, `test_nfr_003_public_api_contract` (4 FAILED) + `test_ac_045_traced_methods_no_tokens_in_logs` (HANG — deselected) — unchanged.

**RED confirmed for T-006.** No implementation code written in this step; no commits in this step (S4.5 commits). No test modifications.

**Evidence:** this section.

### S4.2 (T-006) Implement + confirm GREEN

**Date:** 2026-09-18

**Task:** T-006 — "Device identification at login: store device fields + login method on the issued Session row (password + passkey paths)" (REQ-016; AC-008, AC-032).

**Implementation summary** (follows T-006 `implementation_steps` exactly; minimal, additive, backward-compatible):

- `src/backend/authentication/service.py` — the only file changed:
  - `_issue_session(user, method, user_agent=None, ip=None, device_name=None)`: now accepts optional `user_agent`/`ip`/`device_name` parameters and stores them on the issued `Session` row together with `login_method=method` (so `login_method` is `"password"` for the password path and `"passkey"` for the passkey path). Omitted device fields are stored as `None`; pre-feature rows remain `NULL` (REQ-016, ADR-062).
  - `login` (password path): now passes the device fields from the `LoginRequest` (`request.user_agent`/`request.ip`/`request.device_name`) to `_issue_session` (REQ-016, ADR-062).
  - `complete_passkey_login` (passkey path): unchanged — it already calls `_issue_session(user, method="passkey")`; with the new signature the device fields default to `None` and `login_method` is stored as `"passkey"` (REQ-016, AC-032).

**Design constraints honored:** device identification captured at login (login path stores provided fields + method); additive/backward-compatible per authentication NFR-003 (all existing behavior remains valid); omitted device fields → `None` stored, existing rows remain `NULL`; `login_method` distinguishes password and passkey sessions (AC-008, AC-032, ADR-062). No raw tokens/hashes in outputs. No test modifications.

**GREEN gate — targeted T-006 tests:** `uv run pytest tests/integration/sessionmanagement/test_device_fields.py -v` → **2 passed** (0.92s):
- `test_ac_008_login_stores_device_fields` — **PASSED**
- `test_ac_032_passkey_login_stores_method` — **PASSED**

**GREEN gate — full suite (the hanging later-task T-009 test deselected):**

- Command: `uv run pytest tests/acceptance/sessionmanagement/ tests/property/sessionmanagement/ tests/unit/sessionmanagement/ tests/contract/sessionmanagement/ tests/integration/sessionmanagement/ --deselect tests/acceptance/sessionmanagement/test_observability.py::test_ac_045_traced_methods_no_tokens_in_logs -v`
- Result: **6 failed, 59 passed, 1 deselected, 2 errors** (45.30s).
- **Pass count vs. S4.1 (T-006) RED baseline:** RED was **8 failed / 57 passed / 2 errors**; GREEN is **6 failed / 59 passed / 2 errors**. Delta is exactly **−2 failed / +2 passed = T-006's 2 `tests_to_create`** (RED → GREEN). Pass count 59 ≥ RED baseline 57. No previously-passing test now fails.

**T-001…T-005 still GREEN (no regression):** all T-001/T-002/T-003/T-004/T-005 tests remain in the **59 passed**; none appears in the failure list. No previously-passing test now fails.

**The 6 expected-still-failing later-task tests (T-007…T-009) are STILL failing for their OWN reasons** (their tasks are not implemented yet) — **unchanged vs. the RED baseline** (identical set, minus T-006's 2 which are now GREEN):
- T-007 settings registration: `test_ac_039_register_settings_defaults` (1 FAILED) — unchanged.
- T-008 module singleton: `test_ac_042_singleton_first_call_without_repository_value_error` (1 FAILED) + `test_ac_041_singleton_created_once`/`test_ac_043_reset_session_service` (2 ERROR at setup on `ImportError: cannot import name 'reset_session_service'`) — unchanged.
- T-009 cross-cutting: `test_ac_038_none_publisher_no_events_no_subscriptions`, `test_ac_044_no_tokens_in_outputs`, `test_nfr_004_traced_service_publishes_events`, `test_nfr_003_public_api_contract` (4 FAILED) + `test_ac_045_traced_methods_no_tokens_in_logs` (HANG — deselected) — unchanged.

**Ruff gate:** `uv run ruff check .` → **6 errors, all pre-existing PLR0917** (5 in other `src/backend/` files: `filemanagement/errors.py`, `filemanagement/service.py`, `logging/_decorator.py` ×2, `mail/transport.py`; 1 in `src/backend/authentication/service.py:86` = the pre-existing `AuthService.__init__` (15 positional args), which is **not** in T-006's changed region — confirmed pre-existing by re-running ruff on the committed-HEAD baseline of `service.py`, which also reports exactly that 1 PLR0917 at line 86). **Zero NEW ruff errors in T-006's changed paths.** Pre-existing PLR0917 noted, not fixed (out of scope for S4.2).

**No commits in this step (S4.5 commits).** No test modifications. GREEN confirmed for T-006.

**Evidence:** this section.

### S4.3 (T-006) Ruff

**Date:** 2026-09-18

**Task:** T-006 — Ruff gate on T-006's changed paths (only changed path: `src/backend/authentication/service.py`).

**Ruff gate — changed path:** `uv run ruff check src/backend/authentication/service.py` → **1 error**, the **pre-existing PLR0917 at line 86** (`AuthService.__init__`, 15 positional args) — **not** in T-006's changed region (`_issue_session` device-field/login-method storage). **Zero NEW errors in T-006's changed region.**

**Ruff gate — whole repo:** `uv run ruff check .` → **6 errors, all pre-existing PLR0917** (5 in other files: `filemanagement/errors.py:63`, `filemanagement/service.py:284`, `logging/_decorator.py:71`, `logging/_decorator.py:109`, `mail/transport.py:44`; 1 in `src/backend/authentication/service.py:86`). **No NEW errors introduced by T-006.**

**Gate result: PASS** — zero new lint errors in T-006's changed paths. Pre-existing PLR0917 noted, not fixed (out of scope for S4.3; a repo-wide lint fix is a separate, explicit step).

**No commits in this step (S4.5 commits).** No test or implementation modifications.

**Evidence:** this section.

### S4.4 (T-006) Refactor (keep GREEN)

**Date:** 2026-09-18

**Task:** T-006 — Refactor the T-006 implementation's code structure WITHOUT changing observable behavior (re-run the GREEN gate after the refactor and confirm it stays GREEN).

**Refactor decision: NO refactor made — the T-006 implementation is already clean and minimal.**

The T-006 changed region in `src/backend/authentication/service.py` was reviewed:
- `_issue_session` — the signature extension is additive (3 optional params, `None` defaults), exactly per the design constraint "additive and backward-compatible per authentication NFR-003".
- The `Session` constructor stores `user_agent`/`ip`/`device_name` + `login_method=method` with a 2-line comment documenting the *why* (REQ-016, ADR-062; omitted → `None`; pre-feature rows remain NULL) — it explains the design rationale, not the code.
- `login` (password path) — explicit keyword pass of `request.user_agent`/`request.ip`/`request.device_name`; no indirection, no duplication.
- The passkey path is unchanged (device fields default to `None`), per AC-032.

No duplication, dead code, or complexity was found; the parameter pass is already the simplest form. There is no worthwhile, behavior-preserving refactor to make, so **no changes were made** (a valid DONE per the step objective).

**Observable behavior unchanged:** no code was modified, so the specified behavior (REQ-016, AC-008, AC-032) is identical by construction. The S4.2 (T-006) GREEN state stands: T-006's 2 `tests_to_create` (`test_ac_008_login_stores_device_fields`, `test_ac_032_passkey_login_stores_method`) remain **2/2 PASS**, and the full-suite state (6 failed / 59 passed / 1 deselected / 2 errors — all failures/errors are later-task T-007…T-009 tests failing for their own reasons) is unchanged. No GREEN re-run was required (no changes made).

**Ruff:** not re-run (no changes made). The S4.3 (T-006) result stands: zero new errors in T-006's changed region (only the pre-existing PLR0917 at line 86, outside the changed region).

**No commits in this step (S4.5 commits).** No test modifications.

**Evidence:** this section.
