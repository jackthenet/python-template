# Verification: search

- **Change type:** CROSS-CUTTING (reclassified from FEATURE — see below)
- **Branch:** `crosscut/search` (worktree: `../python-template_kopie-worktrees/crosscut/search`, based on `origin/main` @ `f3501ca`)
- **Date:** 2026-09-24

## Reclassification record

- **From:** FEATURE → **To:** CROSS-CUTTING
- **Trigger:** S1.1 Interrogate, question Q-108 — the user answered "Also wire existing features (CROSS-CUTTING)": this change not only builds the new `search` abstraction but also registers the content of existing features (user-management, file-management, session-management) as search sources.
- **Affected features:** `search` (new), `user-management`, `file-management`, `session-management`.
- **Action taken (per Escalation Rules):** kept the same worktree, renamed the branch `feature/search` → `crosscut/search`, moved the worktree to the `crosscut/` directory, re-running Phase 1 for CROSS-CUTTING (spec gains a per-feature Impact Analysis).
- **Date:** 2026-09-25

## User governance override (Phase 2 entry)

- The user explicitly pre-authorized: **continue into Phase 2 after Phase 1 completes, even without the spec PR being merged.** The normal Spec Approval Gate (verify `git log main -- docs/specs/search.md` before Phase 2) is waived by this explicit user instruction. The spec PR is still opened in S1.4 for review/merge; Phase 2 proceeds on the change branch regardless of merge state.
- **Date:** 2026-09-25

## Phase 2: ADRs (S2.1)

Five ADRs created — each clears the threshold (new pattern/architecture element or cross-feature interface):

| ADR | Decision | Threshold met |
|-----|----------|---------------|
| `docs/decisions/ADR-076-search-feature-placement.md` | New `search` feature at `src/backend/search/` (standalone feature, singleton + reset, `InMemorySource` for tests/DI) | New architecture element |
| `docs/decisions/ADR-077-source-registration-contract.md` | Cross-feature source registration contract (name + field schema + sync query function; additive `search_source.py` modules) | Cross-feature interface |
| `docs/decisions/ADR-078-stateless-live-query.md` | Stateless live query — no index, no cache, no persistence | New architecture element (significant design decision) |
| `docs/decisions/ADR-079-search-permission-enforcement.md` | Search access control via the shared `Principal`/`PermissionChecker` enforcement plumbing + additive `search.search` action | Cross-feature interface |
| `docs/decisions/ADR-080-additive-session-repository-list-all.md` | Additive `SessionRepository.list_all()` ABC method in authentication | Cross-feature interface (additive ABC extension) |

- **Date:** 2026-09-25

## Phase 3: Test & RED (S3.2)

- **Ruff gate (step's changed paths):** `uv run ruff check tests/acceptance/search/ tests/contract/search/ tests/integration/search/ tests/property/search/ tests/unit/search/ tests/search_test_helpers.py tests/unit/authentication/test_sessions.py` → **All checks passed!** (clean; the whole-repo sweep is a Phase 5 gate).
- **Collection pre-check:** `uv run pytest --collect-only -q` (same paths) → **74 tests collected, 0 collection errors** (the `backend.search` imports are deferred into the test bodies — house pattern, so the RED surfaces per-test, not at collection).
- **RED command (targeted — the newly derived tests only; the full suite is a Phase 5 gate):**
  `uv run pytest -q tests/acceptance/search/ tests/contract/search/ tests/integration/search/ tests/property/search/ tests/unit/search/ tests/unit/authentication/test_sessions.py`
- **RED result:** **70 failed, 4 passed** (2026-09-25). The 4 passed are **pre-existing** tests in `tests/unit/authentication/test_sessions.py` (`test_edge_004_session_info_expired`, `test_edge_005_session_info_revoked`, `test_edge_006_logout_twice_noop`, `test_edge_017_session_info_no_token`) — not part of this change. **All 70 newly derived tests failed.**
- **Failure modes (test contract sanity check — every failure is on unimplemented behavior; no invalid test data):**
  - 65 × `ModuleNotFoundError: No module named 'backend.search'` (the unimplemented search feature module)
  - 2 × `ImportError: cannot import name 'build_user_source' from 'backend.usermanagement'` (additive user-management source module, REQ-020 — `test_ac_034_user_source`, `test_startup_wiring_all_sources`)
  - 1 × `ImportError: cannot import name 'build_file_source' from 'backend.filemanagement'` (REQ-021 — `test_ac_035_file_source`)
  - 1 × `ImportError: cannot import name 'build_session_source' from 'backend.sessionmanagement'` (REQ-022 — `test_ac_036_session_source`)
  - 1 × `AttributeError: 'SqliteSessionRepository' object has no attribute 'list_all'` (T-004 additive ABC method, REQ-022 — `test_list_all_returns_all_sessions_created_at_desc`)
  - No `ValidationError`/`ValueError` during test-data construction (no invalid test data).
- **Date:** 2026-09-25

## Phase 4: Implement (S4.1–S4.4) — T-001 foundation + registration

- **T-001 RED (S4.1):** confirmed — all 15 T-001 targeted tests failed with `ModuleNotFoundError: No module named 'backend.search'` (the unimplemented search feature module).
- **Implementation (S4.2):** `src/backend/search/` package created — `models.py` (SearchSource, SourceField, FieldType, SourceItem, SourcePage, SourceQueryContext, SearchQuery, FilterCondition/FilterGroup/FilterOperator, Sort, SearchResult/SearchResultItem, SourceFailure), `errors.py` (SearchError hierarchy: UnknownSourceError, MalformedQueryError, SourceQueryFailedError), `events.py` (SourceRegistered, SourceUnregistered, SourceQueryFailed), `service.py` (SearchService thread-safe in-memory registry + InMemorySource + module singleton), `__init__.py` (public API).
  - House patterns: `@logged_class(slow_threshold_ms=100, include_args=False)` on the service; `@requires_permission('search.search')` on the enforced method (ADR-071); live settings read for `search.default_page_size`/`search.max_page_size` (REQ-013, D14); list-holder module singleton (`_singleton[0]`, matching `settings` house pattern — no `global`).
- **T-001 GREEN (S4.2):** **15 passed** (2026-09-25) — targeted `green_command`:
  - `uv run pytest tests/acceptance/search/test_search.py -k "ac_001 or ac_002 or ac_003 or ac_004 or ac_005 or ac_007 or ac_008 or ac_023 or ac_032"` → **9 passed**
  - `uv run pytest tests/unit/search/test_search_edges.py -k "edge_001 or edge_013 or edge_014 or edge_016 or edge_021"` → **5 passed**
  - `uv run pytest tests/property/search/test_search_properties.py -k "inv_001"` → **1 passed**
  - (The full suite is a Phase 5 gate, not a per-task run.)
- **Ruff gate (S4.2):** `uv run ruff check src/backend/search/` → **All checks passed**; `uv run ruff format --check src/backend/search/` → **5 files already formatted**.
- **Refactor (S4.3):** `_apply_operator` split into `_apply_string_operator` / `_apply_exact_operator` with a `_COMPARISONS` dispatch table (PLR0911/PLR0912); `zip(..., strict=True)` (B905); list-holder singleton (PLW0603). No observable behavior change — T-001 tests remain GREEN (re-confirmed 15/15).
- **Status:** T-001 → **VERIFIED** (`.github/task-runner/tasks.json` + `docs/tasks/search.tasks.json`).
- **Commit:** `84ebf8d` `feat(search): T-001 foundation + registration (module, models, errors, events, service, singleton)`.
- **Date:** 2026-09-25

## Phase 4: Implement (S4.1–S4.4) — T-002 query semantics (filter/sort/pagination/result-shape)

- **T-002 RED (S4.1):** confirmed — targeted `red_command` → **8 failed, 20 passed** (2026-09-25). Failure modes (all on unimplemented T-002 behavior; no invalid test data):
  - 5 × `DID NOT RAISE MalformedQueryError` — no query validation in the service's query path (`test_edge_003_invalid_limit_offset`, `test_edge_004_non_filterable_field`, `test_edge_005_invalid_operator_for_type`, `test_edge_006_non_sortable_field`, `test_ac_024_malformed_query_errors`).
  - 3 × `ImportError: cannot import name 'register_settings' from 'backend.search'` — feature-owned settings registration not yet created (`test_edge_007_limit_clamped`, `test_ac_016_default_page_size`, `test_ac_017_limit_clamped_to_max`).
- **Implementation (S4.2):**
  - `src/backend/search/feature_settings.py` (new): `register_settings(registry)` registers `search.default_page_size` (NUMBER, 100), `search.max_page_size` (NUMBER, 1000), `search.source_timeout` (NUMBER, 5000) — category `application`, group `search` (REQ-013, D14; house pattern per mail). Exported from `__init__.py`.
  - `src/backend/search/service.py`: query validation in the service's query path (REQ-010, AC-024) — `_validate_pagination` (`limit < 1` → `MalformedQueryError(reason='invalid_limit')`; `offset < 0` → `reason='invalid_offset'`); `_validate_query_against_source` (single-source path: filters restricted to declared-filterable fields with per-type operator restrictions from the D4 table `_VALID_OPERATORS` and value-type checks per D3 — string: str; number: int/float not bool; boolean: bool; datetime: datetime; `in_list`: a list of such values; `is_null` requires no value — plus sort on a declared-sortable field). Each error identifies the reason and the field/source.
  - The free-text/filter/sort/pagination/result-shape semantics themselves were already applied in-memory by T-001's `InMemorySource._query` (normalization D13, per-type operator semantics D4, stable sort D8, pagination D5) — T-002 adds the service-side validation + the feature-owned settings registration the live page-size reads require.
- **T-002 GREEN (S4.2):** **43 passed** (2026-09-25) — targeted `green_command` (T-001's 15 + T-002's 28 tests; the full suite is a Phase 5 gate).
- **Ruff gate (S4.2):** `uv run ruff check src/backend/search/service.py src/backend/search/feature_settings.py src/backend/search/__init__.py` → **All checks passed**; `uv run ruff format --check` (same paths) → **3 files already formatted**.
- **Refactor (S4.3):** no-op fast-path — the implementation is small and follows the module's established pattern (module-level private helpers with REQ-referenced docstrings, declarative D4 table); no structural changes needed. GREEN from S4.2/S4.3 still holds (zero file changes in the step).
- **Status:** T-002 → **VERIFIED** (`.github/task-runner/tasks.json` + `docs/tasks/search.tasks.json`).
- **Commit:** `0542144` `impl(search): T-002 free-text + filter/sort/pagination/result-shape (GREEN)`.
- **Date:** 2026-09-25

## Phase 4: Implement (S4.1–S4.4) — T-003 fan-out + timeout + events + tracing + permissions

- **T-003 RED (S4.1):** confirmed — targeted `red_command` → **8 failed, 7 passed** (2026-09-25). Failure modes (all on unimplemented T-003 behavior; no invalid test data):
  - 3 × source raising propagates raw `RuntimeError` instead of the domain behavior (`test_ac_026_single_source_failure_error`, `test_edge_010_single_source_raises_error`, `test_edge_009_global_source_raises_partial` — no `SourceQueryFailedError` / no resilient failure marker).
  - 2 × no per-source timeout (`test_ac_033_source_timeout`, `test_edge_011_source_timeout` — the slow source's sleep blocks the query thread instead of a `timeout` failure).
  - 1 × no `SourceQueryFailed` event on a source failure (`test_ac_029_lifecycle_and_failure_events`).
  - 1 × no strict fan-out validation (`test_edge_020_fanout_strict_validation` — a global filter valid for one source but not another did not raise `MalformedQueryError`).
  - 1 × integration: no resilient global fan-out marker + event (`test_ac_025_global_fanout_source_failure_partial`).
  - The 7 passed are already covered by T-001/T-002 (global combined pagination, `register_settings` live read, `@logged` tracing, permission enforcement, concurrent replace/register, INV-005 secret-freedom).
- **Implementation (S4.2):**
  - `src/backend/search/service.py`:
    - **Resilient global fan-out (REQ-011, D11, AC-025, EDGE-009):** a source raising during a global search → partial results + a `SourceFailure` marker (feature, reason `query_failed`, error kind = the exception type name — no sensitive data) + a `SourceQueryFailed` event; no exception; the other sources' results are returned.
    - **Single-source failure (REQ-010, AC-026, EDGE-010):** a source raising during a single-source query (`feature` set) → `SourceQueryFailedError` (source + reason + error kind); no event, no marker.
    - **Per-source timeout (REQ-019, D12, AC-033, EDGE-011):** each source query runs in a worker thread of a bounded per-service `ThreadPoolExecutor` (`max_workers=8`, `thread_name_prefix="search-source"`; threads created lazily on first submit); exceeding the live `search.source_timeout` (ms) → reason `timeout` (marker for global; `SourceQueryFailedError` for single-source); the timed-out thread is abandoned (bounded by the pool; its result is discarded, NFR-005).
    - **Strict fan-out validation (REQ-010, D7, EDGE-020):** the global query is validated against **every** source in the fan-out (the single-source path is the one-element case) — a field absent or non-filterable/non-sortable in any source, an invalid operator, or a wrong value type → `MalformedQueryError` identifying the source + field, before any source is queried.
    - New helpers: `_query_source(source, ctx) -> (page, reason, error_kind)` (worker-thread query with the live timeout) and `_read(key, fallback)` (live settings read); `_effective_limit` refactored onto `_read`.
  - `src/backend/search/feature_actions.py` (new): `register_actions(catalog)` (traced with `@logged`) declares the additive `search.search` catalog action (REQ-016, ADR-079; the `PermissionCatalog` annotation is type-checking only — no runtime import of `backend.permissions`, ADR-070). Exported from `__init__.py` (NFR-003 public API).
  - `src/backend/search/feature_settings.py`: `register_settings` traced with `@logged` (REQ-015 — the "Create feature_settings.py" step was a no-op fast-path from T-002; only the tracing remained).
- **T-003 GREEN (S4.2):** **58 passed** (2026-09-25) — targeted `green_command` (T-001's 15 + T-002's 28 + T-003's 15 tests; the full suite is a Phase 5 gate).
- **Ruff gate (S4.2):** `uv run ruff check src/backend/search/` → **All checks passed**; `uv run ruff format --check src/backend/search/` → **7 files already formatted**.
- **Refactor (S4.3):** no-op fast-path — the implementation is small and follows the module's established pattern (module-level/class private helpers with REQ-referenced docstrings, house `feature_actions.py` pattern); no structural changes needed. GREEN from S4.2 still holds (zero file changes in the step).
- **Pre-existing (out of T-003 scope, for Phase 5):** `uv run mypy src/` reports 1 pre-existing error in `get_search_service` (`service.py` — the T-001 list-holder singleton pattern; `Incompatible return value type (got "SearchService | None", expected "SearchService")`); confirmed present on the clean tree (stash check) — mypy is a Phase 5 gate, not a per-task gate.
- **Status:** T-003 → **VERIFIED** (`.github/task-runner/tasks.json` + `docs/tasks/search.tasks.json`).
- **Commit:** (this commit) `impl(search): T-003 fan-out + timeout + events + tracing + permissions (GREEN)`.
- **Date:** 2026-09-25

## Phase 4: Implement (S4.1–S4.4) — T-004 authentication additive `SessionRepository.list_all()`

- **T-004 RED (S4.1):** confirmed — targeted `red_command` → **1 failed** (2026-09-25). Failure mode (on unimplemented T-004 behavior; no invalid test data):
  - 1 × `AttributeError: 'SqliteSessionRepository' object has no attribute 'list_all'` (`test_list_all_returns_all_sessions_created_at_desc` — the additive ABC method, REQ-022).
- **Implementation (S4.2):**
  - `src/backend/authentication/repositories.py`: additive abstract method `SessionRepository.list_all() -> Sequence[Session]` (all sessions, any revocation state, no user filter, `created_at` descending — REQ-022, ADR-080); module docstring documents the additive evolution (custom repository implementations gain a new method; backward-compatible per authentication NFR-003; precedent: session-management REQ-017).
  - `src/backend/authentication/repository.py`: `SqliteSessionRepository.list_all()` — returns the existing rows in `created_at` descending order (tie-break `id` descending), consistent with `list_for_user` (no user filter, any revocation state; `_attach_utc` reconciles storage representation with the tz-aware UTC contract).
  - No change to `AuthService` or any existing operation (REQ-022).
- **T-004 GREEN (S4.2):** **5 passed** (2026-09-25) — targeted `green_command` (`tests/unit/authentication/test_sessions.py`: T-004's test + the 4 existing session edge tests — no regression from the additive ABC method; the full suite is a Phase 5 gate).
- **Ruff gate (S4.2):** `uv run ruff check src/backend/authentication/repositories.py src/backend/authentication/repository.py` → **All checks passed**; `uv run ruff format --check` (same paths) → **2 files already formatted**.
- **Refactor (S4.3):** no-op fast-path — the implementation is small and follows the module's established additive-extension pattern (REQ/ADR-referenced docstring; `list_all` mirrors `list_for_user`); no structural changes needed. GREEN from S4.2 still holds (zero file changes in the step).
- **Status:** T-004 → **VERIFIED** (`.github/task-runner/tasks.json` + `docs/tasks/search.tasks.json`).
- **Commit:** (this commit) `impl(authentication): T-004 additive SessionRepository.list_all (GREEN)`.
- **Date:** 2026-09-25

## Phase 4: Implement (S4.1–S4.4) — T-005 user-management additive `build_user_source`

- **T-005 RED (S4.1):** confirmed — targeted `red_command` → **1 failed** (2026-09-25). Failure mode (on unimplemented T-005 behavior; no invalid test data):
  - 1 × `ModuleNotFoundError` — `build_user_source` not exported from `backend.usermanagement` (`test_ac_034_user_source` — the additive search-source module, REQ-020).
- **Implementation (S4.2):**
  - `src/backend/usermanagement/search_source.py` (new): `build_user_source(repository: UserRepository) -> SearchSource` (REQ-020, ADR-077) — source name `usermanagement`; the field schema (username/email/display_name — string, searchable/filterable/sortable/display; is_active — boolean, filterable/sortable/display; created_at/updated_at — datetime, filterable/sortable/display); the sync query function over the existing `UserRepository.list_all` (called with `include_inactive=True` so the `is_active` field is meaningful); free text (case-fold + NFC + trim, D13), filters (string case-insensitive; boolean/datetime exact, D4), sort (None last, deterministic, D8), and pagination; `item_id` = the user id (a stable string identifier); default ordering `username` ascending (REQ-020).
  - `src/backend/usermanagement/__init__.py`: additive re-export of `build_user_source` (the feature's public API, NFR-003).
  - No change to `UserManager`, `UserRepository`, models, events, or errors (REQ-020).
- **Test bug fix (S4.2):** `test_ac_034_user_source` asserted `item.item_id == users[0].id` — `User.id` is a `UUID` and the spec declares `item_id` a stable string identifier (a `str` can never equal a `UUID`); fixed to `item.item_id == str(users[0].id)` — aligning the test with the spec (the intent "item_id = the user id" is preserved; not a weakening).
- **T-005 GREEN (S4.2):** **44 passed** (2026-09-25) — targeted `green_command` (`test_ac_034_user_source` + `tests/acceptance/usermanagement/` — no regression from the additive module + re-export; the full suite is a Phase 5 gate).
- **Ruff gate (S4.2):** `uv run ruff check src/backend/usermanagement/search_source.py src/backend/usermanagement/__init__.py tests/acceptance/search/test_feature_sources.py` → **All checks passed**; `uv run ruff format --check` (same paths) → **3 files already formatted**.
- **Refactor (S4.3):** no-op fast-path — the implementation is small and follows the module's established pattern (module-level private helpers with REQ-referenced docstrings); no structural changes needed. GREEN from S4.2 still holds (zero file changes in the step).
- **Status:** T-005 → **VERIFIED** (`.github/task-runner/tasks.json` + `docs/tasks/search.tasks.json`).
- **Commit:** (this commit) `impl(usermanagement): T-005 build_user_source (AC-034, REQ-020) (GREEN)`.
- **Date:** 2026-09-25

## Phase 4: Implement (S4.1–S4.4) — T-006 file-management additive `build_file_source`

- **T-006 RED (S4.1):** confirmed — targeted `red_command` → **1 failed** (2026-09-25). Failure mode (on unimplemented T-006 behavior; no invalid test data):
  - 1 × `ModuleNotFoundError` — `build_file_source` not exported from `backend.filemanagement` (`test_ac_035_file_source` — the additive search-source module, REQ-021).
- **Implementation (S4.2):**
  - `src/backend/filemanagement/search_source.py` (new): `build_file_source(repository: FileRepository) -> SearchSource` (REQ-021, ADR-077) — source name `filemanagement`; the field schema (key/namespace/original_filename — string, searchable/filterable/sortable/display; detected_mime_type — string, filterable/sortable/display; size — number, filterable/sortable/display; created_at/updated_at — datetime, filterable/sortable/display); the sync query function over the existing `FileRepository.list_by_namespace` (full fetch via `list_by_namespace(None, limit=<large>, offset=0)` because the repository applies the LIMIT in SQL); free text (case-fold + NFC + trim, D13), filters (string case-insensitive; number/datetime exact, D4), sort (None last, deterministic, D8), and pagination; `item_id` = the file id (a stable string identifier); default ordering `created_at` ascending (REQ-021).
  - `src/backend/filemanagement/__init__.py`: additive re-export of `build_file_source` (the feature's public API, NFR-003).
  - No change to `FileService`, `FileRepository`, models, events, or errors (REQ-021).
- **Test bug fix (S4.2):** `test_ac_035_file_source` asserted `item.item_id == records[0].id` — `FileRecord.id` is a `UUID` and the spec declares `item_id` a stable string identifier (a `str` can never equal a `UUID`); fixed to `item.item_id == str(records[0].id)` — aligning the test with the spec (the intent "item_id = the file id" is preserved; not a weakening).
- **T-006 GREEN (S4.2):** **57 passed, 1 skipped** (2026-09-25) — targeted `green_command` (`test_ac_035_file_source` + `tests/acceptance/filemanagement/` — no regression from the additive module + re-export; the 1 skipped is the pre-existing `test_ac_031_symlink_rejected` — symlinks not available on this host; the full suite is a Phase 5 gate).
- **Ruff gate (S4.2):** `uv run ruff check src/backend/filemanagement/search_source.py src/backend/filemanagement/__init__.py tests/acceptance/search/test_feature_sources.py` → **All checks passed**; `uv run ruff format --check` (same paths) → **3 files already formatted**.
- **Refactor (S4.3):** no-op fast-path — the implementation is small and follows the module's established pattern (module-level private helpers with REQ-referenced docstrings); no structural changes needed. GREEN from S4.2 still holds (zero file changes in the step).
- **Status:** T-006 → **VERIFIED** (`.github/task-runner/tasks.json` + `docs/tasks/search.tasks.json`).
- **Commit:** (this commit) `impl(filemanagement): T-006 build_file_source (AC-035, REQ-021) (GREEN)`.
- **Date:** 2026-09-25

## Phase 4: Implement (S4.1–S4.4) — T-007 session-management additive `build_session_source`

- **T-007 RED (S4.1):** confirmed — targeted `red_command` → **1 failed** (2026-09-25). Failure mode (on unimplemented T-007 behavior; no invalid test data):
  - 1 × `ImportError` — `build_session_source` not exported from `backend.sessionmanagement` (`test_ac_036_session_source` — the additive search-source module, REQ-022).
- **Implementation (S4.2):**
  - `src/backend/sessionmanagement/search_source.py` (new): `build_session_source(repository: SessionRepository) -> SearchSource` (REQ-022, ADR-077) — source name `sessionmanagement`; the field schema (session_id — string, searchable/filterable/sortable/display; user_id — string, filterable/sortable/display; created_at/expires_at — datetime, filterable/sortable/display; revoked — boolean, filterable/sortable/display; login_method — string, filterable/sortable/display); the sync query function over the existing `SessionRepository.list_all` (the additive method from T-004, authentication — all sessions, any revocation state, no user filter); free text (case-fold + NFC + trim, D13), filters (string case-insensitive; boolean/datetime exact, D4), sort (None last, deterministic, D8), and pagination; `item_id` = the session id (a stable string identifier); default ordering `created_at` descending (REQ-022).
  - `src/backend/sessionmanagement/__init__.py`: additive re-export of `build_session_source` (the feature's public API, NFR-003).
  - No change to `SessionService`, events, or errors (REQ-022).
- **Test bug fix (S4.2):** `test_ac_036_session_source` asserted `item.item_id in {rows[0].id, rows[1].id}` — `Session.id` is a `UUID` and the spec declares `item_id` a stable string identifier (a `str` can never equal a `UUID`); fixed to `item.item_id in {str(rows[0].id), str(rows[1].id)}` — aligning the test with the spec (the intent "item_id = the session id" is preserved; not a weakening).
- **T-007 GREEN (S4.2):** **49 passed** (2026-09-25) — targeted `green_command` (`test_ac_036_session_source` + `tests/acceptance/sessionmanagement/` — no regression from the additive module + re-export; the full suite is a Phase 5 gate).
- **Ruff gate (S4.2):** `uv run ruff check src/backend/sessionmanagement/search_source.py src/backend/sessionmanagement/__init__.py tests/acceptance/search/test_feature_sources.py` → **All checks passed**; `uv run ruff format --check` (same paths) → **3 files already formatted**.
- **Refactor (S4.3):** no-op fast-path — the implementation is small and follows the module's established pattern (module-level private helpers with REQ-referenced docstrings); no structural changes needed. GREEN from S4.2 still holds (zero file changes in the step).
- **Status:** T-007 → **VERIFIED** (`.github/task-runner/tasks.json` + `docs/tasks/search.tasks.json`).
- **Commit:** (this commit) `impl(sessionmanagement): T-007 build_session_source (AC-036, REQ-022) (GREEN)`.
- **Date:** 2026-09-25
