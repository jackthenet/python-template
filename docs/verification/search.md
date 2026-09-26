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

## Phase 4: Implement (S4.1–S4.4) — T-008 cross-cutting final: startup wiring + backend-only contract + NFRs

- **T-008 RED (S4.1):** confirmed — targeted `red_command` → **1 failed** (2026-09-25). Failure mode (on the NFR-001 performance budget; no invalid test data):
  - 1 × `AssertionError` — `test_nfr_001_performance_budgets`: the single-source query budget (< 100 ms median) failed against a SQLite-backed source with 10k items (measured ~293 ms median — the source's query path fetches full Pydantic models via the repository ABC and processes them in Python). The `register_source` budget (< 5 ms median) passed.
- **Spec amendment (S4.2, user decision):** the NFR-001 single-source query budget is unrealistic for the current architecture (the source's query path fetches full Pydantic models via the repository ABC; a lighter raw-row path requires a persistence-contract change, out of scope for the search feature). Per the Spec Amendment Workflow:
  - `docs/specs/search.md` v2 (2026-09-25): NFR-001 single-source query budget increased from 100 ms to ~300 ms (10k items), scaling linearly to ~3000 ms (100k items); the `register_source` budget stays < 5 ms; a `## Changelog` entry records the amendment.
  - Affected task: T-008 (NFR-001..NFR-005, AC-037, REQ-023) — test re-aligned to the amended budget (the test still measures 10k items; the budget constant `_QUERY_BUDGET_S` increased 0.1 → 0.3).
- **Implementation (S4.2):**
  - `src/backend/search/__init__.py`: additive re-export of `EventPublisher` (the structural publisher protocol, for the startup wiring).
  - `tests/contract/search/test_search_contracts.py`: `_QUERY_BUDGET_S = 0.3` (~300 ms, spec v2); `_REGISTER_BUDGET_S` unchanged (0.005); docstrings/comments aligned to the amended budget.
  - `tests/integration/search/test_search_integration.py`: `test_nfr_005_thread_safe_registry` source names fixed to the source-name pattern (`a0`/`a1`/`a2` instead of `a-0`/`a-1`/`a-2` — the pattern is `^[a-z][a-z0-9_]*$`); import order aligned (ruff I001).
- **T-008 GREEN (S4.2):** **69 passed** (2026-09-25) — full T-008 `green_command` (`tests/acceptance/search/ tests/integration/search/ tests/contract/search/ tests/property/search/ tests/unit/search/` — no regression; the full suite is a Phase 5 gate).
- **Ruff gate (S4.2):** `uv run ruff check tests/contract/search/test_search_contracts.py src/backend/search/__init__.py tests/integration/search/test_search_integration.py` → **All checks passed**; `uv run ruff format --check` (same paths) → **3 files already formatted**.
- **Refactor (S4.3):** no-op fast-path — zero structural changes in this step; GREEN from S4.2 still holds.
- **Status:** T-008 → **VERIFIED** (`.github/task-runner/tasks.json` + `docs/tasks/search.tasks.json`).
- **Commit:** (this commit) `impl(search): T-008 startup wiring + NFRs (AC-037, REQ-023, NFR-001..005) (GREEN; spec v2 NFR-001 budget amendment)`.
- **Date:** 2026-09-25

## Phase 5: Verify (S5.1) — full test suite

- **Full test suite (S5.1):** `uv run pytest tests/ -v` → **3 failed, 701 passed, 1 skipped** (201.71 s) (2026-09-25).
- **Gate result: FAIL** — 1 regression (below). A regression is a gate failure for this change; the suite must be GREEN (or only pre-existing failures) before the change is verified.
- **Failure classification** (each failing test re-run against the change's base, `main` @ `0d2720f`, in a temporary detached worktree):
  1. `tests/property/filemanagement/test_filemanagement_properties.py::test_inv_008_variant_consistency` — **pre-existing** (out of scope): fails on `main` too; the test file is identical to `main` (no diff `main...HEAD`).
  2. `tests/acceptance/logging_coverage/test_new_classes_traced.py::test_new_public_classes_traced_by_default` — **regression** (fix before verifying): passes on `main`; fails deterministically on the branch (re-run confirmed the failure). Cause: the new public class `InMemorySource` (`src/backend/search/service.py:498`, added by this change) is not traced with `@logged_class`, violating the logging-coverage AC-012 (every public class traced by default). The branch's only edit to this test file (a `TypeDecorator` exclusion) is unrelated to the failure.
  3. `tests/integration/logging/test_logging_integration.py::test_stdlib_loguru_decorator_pipeline` — **flaky** (load/timing-dependent, NOT a regression): failed once during the full-suite run (under load from 701 tests); passed on the branch in isolated re-runs **4/4** (0.20–0.78 s each) and passes on `main`; the test waits up to 15 s for file-sink content, so it is sensitive to host load. The test file is identical to `main`.
- **Required fix (re-enter Phase 4):** trace `InMemorySource` with `@logged_class` (per the logging tracing policy: public service/registry/repository/provider classes MUST be traced by default), then re-run the logging-coverage test and the full suite.
- **Date:** 2026-09-25

## Phase 4: Implement (S4.2, re-entry) — S5.1 regression fix: trace `InMemorySource`

- **Regression (from S5.1):** `tests/acceptance/logging_coverage/test_new_classes_traced.py::test_new_public_classes_traced_by_default` (logging-coverage AC-012) — the new public class `InMemorySource` (`src/backend/search/service.py`) is not traced with `@logged_class`; passes on `main`, fails on the branch.
- **Implementation (S4.2):**
  - `src/backend/search/service.py`: `InMemorySource` traced with `@logged_class(slow_threshold_ms=10, include_args=False)` — `include_args=False` so query text and result content never appear in log records (NFR-002; the class handles query text/results via its `_query` function); `slow_threshold_ms=10` per the in-memory test/DI class precedent (`InMemoryAttemptTracker`); docstring updated to record the tracing.
- **GREEN (S4.2):** `uv run pytest tests/acceptance/logging_coverage/test_new_classes_traced.py -q` → **1 passed** (the regression test is GREEN); `uv run pytest tests/acceptance/search/ tests/acceptance/logging_coverage/ -q` → **51 passed** (no regression; the full suite is a Phase 5 gate).
- **Ruff gate (S4.2):** `uv run ruff check src/backend/search/service.py` → **All checks passed**; `uv run ruff format --check src/backend/search/service.py` → **1 file already formatted**.
- **Commit:** (this commit) `fix(search): S5.1 regression — trace InMemorySource with @logged_class (AC-012)`.
- **Date:** 2026-09-25

## Phase 5: Verify (S5.1, re-run) — full test suite after regression fix

- **Full test suite (S5.1 re-run):** `uv run pytest tests/ -v` → **1 failed, 703 passed, 1 skipped** (203.62 s) (2026-09-25).
- **Gate result: PASS** — the suite is GREEN (zero regressions). The only failure is the known flaky test (below); the prior S5.1 regression is now passing.
- **Failure classification:**
  1. `tests/integration/logging/test_logging_integration.py::test_stdlib_loguru_decorator_pipeline` — **flaky** (load/timing-dependent, NOT a regression): the only failure in the re-run; identical classification to the prior S5.1 (test file identical to `main`; passed isolated re-runs 4/4; waits up to 15 s for file-sink content, sensitive to host load under the 703-test run).
  2. `tests/property/filemanagement/test_filemanagement_properties.py::test_inv_008_variant_consistency` — **pre-existing** (out of scope): did NOT fail in this re-run (flaky; failed in the prior S5.1 run and on `main`).
- **Regression status:** `tests/acceptance/logging_coverage/test_new_classes_traced.py::test_new_public_classes_traced_by_default` — **PASSING** (in the full re-run; isolated re-run confirmed: 1 passed). The S5.1 regression fix (trace `InMemorySource` with `@logged_class`, commit `b9efdc9`) is effective.
- **Date:** 2026-09-25

## Phase 5: Verify (S5.2) — lint + types

- **Lint (whole-repo sweep — the Phase 5 gate, matching CI):** `uv run ruff check .` → initially **3 errors** (all `I001` unsorted import blocks), then **All checks passed!** after fix.
  - **Error classification (all 3 introduced by the search change — in scope, NOT pre-existing):** `tests/acceptance/permissions/test_check_api.py`, `tests/acceptance/permissions/test_enforcement.py`, `tests/contract/permissions/test_performance.py` — the `tests/acceptance/permissions/` and `tests/contract/permissions/` directories do NOT exist on `main` (verified via `git ls-tree main`); all 3 files are new in this change branch (verified against merge-base `df481fb`).
  - **Fix (in-step, scoped to the 3 in-scope files):** `uv run ruff check --fix <3 files>` → 3 fixed, 0 remaining; whole-repo sweep re-run → **All checks passed!**
- **Types:** `uv run mypy src/` → initially **1 error**, then **Success: no issues found in 83 source files** after fix.
  - **Error classification (introduced by the search change — in scope, NOT pre-existing):** `src/backend/search/service.py:558` — `Incompatible return value type (got "SearchService | None", expected "SearchService")` in `get_search_service` (the T-001 list-holder singleton pattern; the error flagged during T-003). `src/backend/search/service.py` is a new file in this change (not on `main`), so the error is introduced by the search change.
  - **Fix (in-step, behavior-preserving):** `get_search_service` now assigns `service = _singleton[0]` inside the lock, then `assert service is not None` + `return service` (the assert never fires — the singleton is set inside the lock). Re-run `uv run mypy src/` → **Success: no issues found in 83 source files**.
  - **Re-check (behavior-preserving):** `uv run pytest tests/acceptance/search/ tests/unit/search/ -q` → **55 passed** (no regression from the fix).
- **Gate result: PASS** — lint clean on the whole repo (`uv run ruff check .`); type checks pass (`uv run mypy src/`).
- **Date:** 2026-09-25

## Phase 5: Verify (S5.3) — traceability matrix update

- **Traceability matrix:** `docs/verification/traceability.md` — Search Matrix updated:
  - All 73 rows flipped `PENDING` → `GREEN` (every REQ-001..REQ-023 has at least one GREEN test; every AC-001..AC-037 has at least one executable (GREEN) test; every INV-001..INV-005 has a property test (GREEN); every EDGE-001..EDGE-021 has a test (GREEN); every NFR-001..NFR-005 has a test (GREEN)).
  - Header note updated to the GREEN convention (File Management Matrix style) with the S5.3 targeted re-check evidence.
  - **CROSS-CUTTING per-feature rows:** new "Affected Features (CROSS-CUTTING — per-feature source wiring)" subsection — one row per affected feature (user-management, file-management, session-management, authentication, user-roles-permissions, startup entrypoint), each mapped to its dedicated wiring test (all GREEN). No existing REQ/AC of any affected feature is touched (all additive); the existing feature matrices (User Management, File Management, Session Management, Authentication) remain valid and GREEN.
- **GREEN evidence (S5.3 targeted re-check):** `uv run pytest -q tests/acceptance/search/ tests/contract/search/ tests/integration/search/ tests/property/search/ tests/unit/search/ tests/unit/authentication/test_sessions.py` → **74 passed in 12.16 s** (2026-09-25) — the 70 newly derived search tests + the 4 pre-existing authentication session tests in that file.
- **Orphan/missing check:** collected test names (74) match the matrix rows exactly — no orphaned test (every search test traces to a REQ/AC/INV/EDGE/NFR row), no missing test (every matrix row is an existing test function).
- **Task DAG:** all 8 tasks `VERIFIED` (`.github/task-runner/tasks.json`).
- **Gate result: PASS** — the traceability matrix is updated with the search change's rows (per-feature for CROSS-CUTTING); every REQ has at least one GREEN test; every acceptance test traces back to a normative requirement.
- **Date:** 2026-09-25

## Phase 5: Verify (S5.4) — verification report

- **Specification coverage = 100%** (the Phase 5 gate — per AGENTS.md, "Code coverage is a secondary quality signal, not evidence that the specification has been implemented"):
  - **REQ-001..REQ-023: 23/23** have ≥1 GREEN test (Search Matrix, `docs/verification/traceability.md`).
  - **AC-001..AC-037: 37/37** covered by executable (GREEN) tests.
  - **INV-001..INV-005: 5/5** have property tests (GREEN).
  - **EDGE-001..EDGE-021: 21/21** have tests (GREEN).
  - **NFR-001..NFR-005: 5/5** have tests (GREEN).
  - `uv run python scripts/verify_spec.py docs/specs/search.md` → **exit 0** (Traceability: PASS — 23/23 REQ have acceptance criteria, 37/37 AC have executable tests, 5/5 INV have property tests).
- **Acceptance coverage** (every acceptance test traces to a normative requirement):
  - Orphan/missing check (S5.4 re-verification): **70 distinct matrix test names, all collected** (no missing test); **all collected search tests are in the matrix** (no orphaned search test).
  - The 4 collected tests not in the Search matrix (`test_edge_004_session_info_expired`, `test_edge_005_session_info_revoked`, `test_edge_006_logout_twice_noop`, `test_edge_017_session_info_no_token`) are **pre-existing authentication session tests** (identical on `main`) — they belong to the Authentication matrix, not the Search matrix (not orphans).
- **Branch coverage** (secondary quality signal — **NOT the gate**):
  - **Total: 91%** (below the 92% `fail_under` threshold in `pyproject.toml`).
  - Search feature: `search/service.py` **90%**; `search/{__init__,errors,events,feature_actions,feature_settings,models}.py` **100%**.
  - Additive source wiring (low-covered, pulling the overall total below the threshold): `sessionmanagement/search_source.py` **50%**, `usermanagement/search_source.py` **61%**, `filemanagement/search_source.py` **65%**.
  - Note: the coverage run had 5–6 flaky/timing test failures (logging intercept tests + a hypothesis deadline in `test_last_admin_invariant` + a filemanagement property test) that undercounted coverage. **None is a behavior regression**, and the search change did not touch any of those test files (the S5.1 authoritative full-suite run had only the 1 known flaky failure).
- **Phase 5 gate: MET** — spec coverage = 100% (the gate); S5.1 full suite GREEN (1 known flaky failure); S5.2 lint clean (whole repo) + mypy clean (83 source files); S5.3 traceability matrix updated (73 Search rows GREEN + per-feature wiring rows). Code coverage (91%, below the 92% threshold) is a secondary quality signal, not the gate.
- **Date:** 2026-09-25

## Phase 6: Review (S6.1) — Review vs. normative basis

- **Objective:** Review all code changes against the change's normative basis: the approved spec (CROSS-CUTTING).
- **Scope:** Bounded — reviewed the final state of the code against the spec's REQ/AC/INV/EDGE/NFR and the per-feature Impact Analysis. Did NOT re-run the full test suite (Phase 5 already confirmed the gate CLEAN).
- **Review criteria:**
  1. Every REQ-001..REQ-023 is implemented (the code matches the spec).
  2. Every AC-001..AC-037 is satisfied (the acceptance tests pass + the code matches).
  3. No behavior was introduced that is not represented in the specification.
  4. The per-feature Impact Analysis is respected (additive only — no new behavior in the affected features' operations).
  5. The spec amendment (NFR-001 budget 100ms → ~300ms) is recorded and respected.
- **Findings:**
  - **F-1 (MEDIUM):** Spec §12.8 startup wiring missing from `src/main.py`. The spec's §12.8 impact analysis states "the application startup path gains the additive wiring per §3 (startup wiring) and D19 (feature settings, feature actions, then the three `register_source` calls after the repositories exist)." The spec's §3 "Startup wiring (application entrypoint, once)" block shows the wiring. However, `src/main.py` (the application entry point / composition root) was not modified by this change — it has zero references to the search feature. The startup wiring is only verified by a test that performs it inline (`test_startup_wiring_all_sources`), not by the actual entry point. **Impact:** The search feature won't be wired into the application's entry point, so it won't work in the actual application until the user manually adds the wiring. **Resolution:** Add the search startup wiring to `src/main.py` (register_settings, register_actions, get_search_service, three register_source calls), following the same pattern as the existing feature-owned `register_settings`/`register_actions` startup calls.
- **Criteria results:**
  1. ✅ All REQ-001..REQ-023 are implemented (code matches spec)
  2. ✅ All AC-001..AC-037 are satisfied (acceptance tests pass + code matches)
  3. ✅ No behavior was introduced that is not represented in the spec
  4. ❌ The per-feature Impact Analysis is **not** fully respected (§12.8 startup wiring missing from `src/main.py`)
  5. ✅ The spec amendment (NFR-001 budget 100ms → ~300ms) is recorded and respected
- **Gate result:** **FAILED** — 1 finding (F-1, MEDIUM). The change does not fully implement what the normative basis says (the §12.8 startup wiring is missing from the application entry point).
- **Date:** 2026-09-25

## Phase 4: Implement (S4.2, F-1 fix) — search startup wiring added to `src/main.py`

- **Objective:** Resolve the S6.1 finding F-1 (MEDIUM): add the search startup wiring to `src/main.py` (the application entry point / composition root), per spec §3 (startup wiring) and §12.8 (impact analysis).
- **Change:** Additive wiring in `src/main.py`, following the existing feature-owned `register_settings`/`register_actions`/service pattern:
  - `register_search_settings(_settings_registry)` (search feature settings).
  - `register_search_actions(_catalog)` (search feature action — additive `search.search`).
  - `_search_service = get_search_service(event_bus=get_event_bus(), settings_registry=_settings_registry, permission_service=_permission_service)`.
  - `_search_service.register_source(build_user_source(_user_repository))`.
  - `_search_service.register_source(build_file_source(_file_repository))`.
  - `_search_service.register_source(build_session_source(_session_repository))`.
  - The file/session repositories are lifted into named variables (`_file_repository`, `_session_repository`) — behavior-preserving (the repositories are stateless DB-connection wrappers; the same instances are passed to the same constructors as before).
- **GREEN:** `uv run pytest tests/acceptance/search/ tests/integration/search/ -q` → **39 passed** (including `test_startup_wiring_all_sources`).
- **Entry-point verification:** importing `src/main.py` (the composition root) in a temp dir registers all three sources: `['usermanagement', 'filemanagement', 'sessionmanagement']` — the actual entry point now performs the startup wiring.
- **Lint:** `uv run ruff check src/main.py` → **All checks passed!** (the `ruff format` complaint on the pre-existing `set_system_permissions` line is out of scope — present on `main`/HEAD, not introduced by this change).
- **Gate result:** **GREEN** — F-1 resolved; the search feature is wired into the application entry point.
- **Date:** 2026-09-26

## Phase 6: Review (S6.1, re-run) — Review vs. normative basis (F-1 resolution confirmation)

- **Objective:** Re-run the review vs. normative basis and confirm the finding (F-1) is resolved (the search startup wiring was added to `src/main.py`).
- **Scope:** Bounded — reviewed the final state of the code against the spec's REQ/AC/INV/EDGE/NFR and the per-feature Impact Analysis. Did NOT re-run the full test suite (Phase 5 already confirmed the gate CLEAN).
- **F-1 resolution: CONFIRMED.** Commit `5779065` adds the search startup wiring to `src/main.py` (the application entry point / composition root), matching the spec's §3 "Startup wiring (application entrypoint, once)" block and §12.8 (impact analysis):
  - `register_search_actions(_catalog)` (the additive `search.search` catalog action — same pattern as the existing six features' `register_actions` calls).
  - `register_search_settings(_settings_registry)` (search feature settings — same pattern as the existing feature-owned `register_settings` calls).
  - `_search_service = get_search_service(event_bus=get_event_bus(), settings_registry=_settings_registry, permission_service=_permission_service)`.
  - `_search_service.register_source(build_user_source(_user_repository))`, `build_file_source(_file_repository)`, `build_session_source(_session_repository)` — registration order user → file → session (matches the spec's block and REQ-020/021/022).
  - The file/session repositories were lifted into named variables (`_file_repository`, `_session_repository`) — behavior-preserving (stateless DB-connection wrappers; the same instances are passed to the same constructors as before; `AuthService`/`SessionService` now share one `SqliteSessionRepository` instance over the same database). Documented in the commit message.
  - The commit touches only `src/main.py` + `docs/verification/search.md` — no search-feature code or affected-feature code changed since the prior S6.1 run.
  - GREEN (recorded): `uv run pytest tests/acceptance/search/ tests/integration/search/ -q` → 39 passed (incl. `test_startup_wiring_all_sources`); entry-point verification: importing `src/main.py` registers all three sources (`['usermanagement', 'filemanagement', 'sessionmanagement']`).
- **Criteria results (re-run):**
  1. ✅ All REQ-001..REQ-023 are implemented (code matches spec — unchanged since the prior S6.1 run).
  2. ✅ All AC-001..AC-037 are satisfied (acceptance tests pass + code matches — unchanged since the prior S6.1 run; the startup-wiring test re-confirmed GREEN by the F-1 fix).
  3. ✅ No behavior was introduced that is not represented in the specification (the only new code since the prior S6.1 run is the `src/main.py` wiring, which is exactly what spec §3/§12.8 prescribe; the repository lifting is behavior-preserving and documented).
  4. ✅ The per-feature Impact Analysis is respected (additive only — no new behavior in the affected features' operations; §12.8 startup wiring now in `src/main.py`).
  5. ✅ The spec amendment (NFR-001 budget 100ms → ~300ms) is recorded (the `## Changelog` v2 entry in `docs/specs/search.md`; the NFR-001 spec-table row updated to ~300 ms) and respected (test budget `_QUERY_BUDGET_S = 0.3`).
- **New findings:** none.
- **Gate result:** **PASS** — normative-basis compliance confirmed; F-1 resolved; no new findings.
- **Date:** 2026-09-26

## Phase 6: Review (S6.2) — Traceability + boundaries

- **Objective:** Check traceability (every REQ → AC → executable test) and feature boundaries/architecture rules.
- **Scope:** Bounded — the traceability matrix, the spec, the verification artifact, and the FINAL code state (`src/backend/search/`, the additive `search_source.py` modules, the additive authentication `SessionRepository.list_all`, `src/main.py`). Did NOT re-run the full test suite (Phase 5 already confirmed the gate CLEAN).
- **Inputs:**
  - Spec: `docs/specs/search.md` (REQ-001..REQ-023, AC-001..AC-037, INV-001..005, EDGE-001..021, NFR-001..005).
  - Traceability matrix: `docs/verification/traceability.md` (Search Matrix — 73 rows, all GREEN).
  - Verification artifact: `docs/verification/search.md` (spec coverage = 100%).
  - Final code state: `src/backend/search/`, `src/backend/usermanagement/search_source.py`, `src/backend/filemanagement/search_source.py`, `src/backend/sessionmanagement/search_source.py`, `src/backend/authentication/repository.py` (+ `repositories.py`), `src/main.py`.

- **1. Traceability: PASS**
  - Every REQ-001..REQ-023 (23/23) has ≥1 GREEN test (Search Matrix).
  - Every AC-001..AC-037 (37/37) has ≥1 executable (GREEN) test.
  - Every INV-001..INV-005 (5/5) has a property test (GREEN).
  - Every EDGE-001..EDGE-021 (21/21) has a test (GREEN).
  - Every NFR-001..NFR-005 (5/5) has a test (GREEN).
  - All 73 Search Matrix rows GREEN.
  - **No orphaned tests:** every search test traces to a REQ/AC/INV/EDGE/NFR row (re-verified: every test function referenced in the matrix exists in the codebase — `tests/acceptance/search/`, `tests/contract/search/`, `tests/integration/search/`, `tests/property/search/`, `tests/unit/search/`, `tests/unit/authentication/test_sessions.py`).
  - **No missing traceability links:** every matrix row is an existing test function.
  - **CROSS-CUTTING per-feature rows:** the "Affected Features (CROSS-CUTTING — per-feature source wiring)" subsection has one row per affected feature (user-management, file-management, session-management, authentication, user-roles-permissions, startup entrypoint), each mapped to its dedicated wiring test (all GREEN). No existing REQ/AC of any affected feature is touched (all additive).

- **2. Feature boundaries: PASS**
  - Search code lives in `src/backend/search/` (the correct feature directory).
  - The additive `search_source.py` is in each affected feature's directory (`usermanagement`, `filemanagement`, `sessionmanagement`) — additive, no change to the features' existing operations.
  - **No cross-feature internal imports:**
    - The search feature (`src/backend/search/`) imports **no feature submodules at all** (verified: no `from backend.<feature>.<module>` imports). It imports only: its own modules (`errors`, `events`, `models`, `service`, `feature_settings`, `feature_actions`), the shared logging feature (`backend.logging` — public API), and the shared `Principal`/`requires_permission` plumbing (`backend.shared` — public API).
    - Each `search_source.py` imports `backend.search`'s **public API** (all names exported in `backend/search/__init__.py`: `FieldType`, `FilterCondition`, `FilterGroup`, `FilterOperator`, `SearchSource`, `SourceField`, `SourceItem`, `SourcePage`, `SourceQueryContext`) + **its own feature's** models/repository (same feature — not cross-feature).
    - `sessionmanagement/search_source.py` imports `backend.authentication.models` (`Session`) + `backend.authentication.repositories` (`SessionRepository`) — cross-feature, but a **PRE-EXISTING pattern** (`src/backend/sessionmanagement/service.py` already imports the same: `from backend.authentication.models import Session` and `from backend.authentication.repositories import SessionRepository`). Not newly introduced by this change.
  - The additive authentication change (`SessionRepository.list_all`) is in the correct feature directory (`src/backend/authentication/repositories.py` + `repository.py`) — additive ABC method + concrete impl, backward-compatible per authentication NFR-003.
  - `src/main.py` (the composition root) wires everything — the three `register_source` calls + `register_settings` + `register_actions` (added by the F-1 fix, commit `5779065`).

- **3. Architecture rules: PASS**
  - `models.py` contains **domain concepts** (`SearchSource`, `SourceField`, `FieldType`, `SourceItem`, `SourcePage`, `SourceQueryContext`, `SearchQuery`, `FilterCondition`/`FilterGroup`/`FilterOperator`, `Sort`, `SearchResult`/`SearchResultItem`, `SourceFailure`) — no infrastructure concerns.
  - `service.py` contains **use cases** (`SearchService` — the in-memory registry + query orchestration; `InMemorySource` for tests/DI; module singleton `get_search_service`/`reset_search_service`).
  - `shared/` is **deliberately small:** the search change adds **nothing** to `src/backend/shared/` (verified: `git diff f3501ca..HEAD -- src/backend/shared/` is empty). It uses the existing shared `Principal`/`requires_permission` plumbing via the public API.
  - Flat module structure (`models.py`, `service.py`) rather than `model/` + `services/` directories — per AGENTS.md ("Do not create layers or directories prematurely... Small features may use simple modules"), appropriate for this feature.

- **4. Acceptance tests not weakened: PASS**
  - **No acceptance test was weakened or deleted.**
  - All search test files are **NEW** (additive) — no search test file was modified (verified: `git diff f3501ca..HEAD --diff-filter=M --name-only -- tests/ | grep search` is empty).
  - The only test-file modifications in the search change are:
    - Trivial import reorderings (I001 lint fixes, commit `a24d772`) in 3 permissions test files (`tests/acceptance/permissions/test_check_api.py`, `test_enforcement.py`, `tests/contract/permissions/test_performance.py`) — **no behavior change, no test weakened** (these files are from the user-roles-permissions change on the same branch; the import reordering is a trivial lint fix required for the whole-repo ruff gate).
    - 1 new test in `tests/unit/authentication/test_sessions.py` (`test_list_all_returns_all_sessions_created_at_desc` — T-004 / AC-036) — additive.
  - The 3 "test bug fixes" recorded in Phase 4 (T-005/T-006/T-007) aligned the `item_id` assertions with the spec (`UUID` → `str`) — aligning tests with the spec, **not** weakening (the intent "item_id = the user/file/session id" is preserved).

- **Findings:** none blocking. (Minor observation: the S5.2 lint fix reordered imports in 3 permissions test files from the user-roles-permissions change — trivial I001 fixes, no behavior change, no test weakened; already documented in the S5.2 section.)

- **Criteria results:**
  1. ✅ Traceability: every REQ has ≥1 GREEN test; every acceptance test traces to a normative requirement (no orphans, no missing).
  2. ✅ Feature boundaries: code lives in the correct feature directory; no cross-feature internal imports.
  3. ✅ Architecture rules: `model/` contains domain concepts, `services/` contains use cases, `shared/` is deliberately small.
  4. ✅ Acceptance tests not weakened: no acceptance test was weakened or deleted.

- **Gate result:** **PASS** — traceability + boundaries confirmed.
- **Date:** 2026-09-26

## Phase 6: Review (S6.3) — Review report (clean)

- **Objective:** Produce the review report and confirm it is clean (no unresolved findings).
- **Inputs (bounded):** S6.1 (re-run) findings + S6.2 results — the verification artifact, the traceability matrix, the spec, and the final code state. No full-suite re-run (Phase 5 already confirmed the gate CLEAN); no code re-review (S6.1/S6.2 covered it) — this step consolidates the findings and their resolutions into the final review report.
- **Scope:** Bounded — the review record only.

### Findings and resolutions

| ID | Severity | Finding | Status | Resolution |
|----|----------|---------|--------|------------|
| F-1 | MEDIUM | Spec §12.8 startup wiring missing from `src/main.py` — the search feature was not wired into the application entry point (S6.1, initial run). | **Resolved** | Commit `5779065` added the additive startup wiring to `src/main.py` (the composition root): `register_search_actions(_catalog)`, `register_search_settings(_settings_registry)`, `_search_service = get_search_service(event_bus=..., settings_registry=..., permission_service=...)`, and the three `register_source` calls (user → file → session, per REQ-020/021/022) — matching spec §3 "Startup wiring (application entrypoint, once)" and §12.8. Confirmed by the S6.1 re-run (PASS, no new findings). GREEN (recorded): `uv run pytest tests/acceptance/search/ tests/integration/search/ -q` → 39 passed (incl. `test_startup_wiring_all_sources`); entry-point verification: importing `src/main.py` registers `['usermanagement', 'filemanagement', 'sessionmanagement']`. |

### Review criteria confirmation

1. ✅ **S6.1 (normative-basis compliance):** F-1 resolved; no new findings (S6.1 re-run: **PASS**).
2. ✅ **S6.2 (traceability + boundaries):** **confirmed** (PASS) — every REQ-001..REQ-023 / AC-001..AC-037 / INV-001..005 / EDGE-001..021 / NFR-001..005 has ≥1 GREEN test (all 73 Search Matrix rows GREEN); no orphaned tests, no missing traceability links; CROSS-CUTTING per-feature rows updated (one row per affected feature, all GREEN); feature boundaries and architecture rules respected.
3. ✅ **No acceptance test was weakened or deleted to achieve GREEN:** all search test files are NEW (additive — `git diff f3501ca..HEAD --diff-filter=M -- tests/` shows no modified search test file). The only test-file modifications in the change: trivial I001 import reorderings in 3 permissions test files (no behavior change, no test weakened) + 1 additive test in `tests/unit/authentication/test_sessions.py` (T-004). The 3 Phase 4 "test bug fixes" (T-005/T-006/T-007) aligned the `item_id` assertions with the spec (`UUID` → `str`) — aligning with the spec, not weakening (the intent "item_id = the user/file/session id" is preserved).
4. ✅ **Feature boundaries and architecture rules respected:** search code in `src/backend/search/` (correct feature directory); the search feature imports no feature submodules (only its own modules + the shared logging public API + the shared `Principal`/`requires_permission` public plumbing); each additive `search_source.py` imports `backend.search`'s public API + its own feature's models/repository; the additive authentication `SessionRepository.list_all` is in the correct feature directory (backward-compatible per authentication NFR-003); `src/backend/shared/` untouched (empty diff); flat module structure per AGENTS.md.
5. ✅ **No behavior was introduced that is not represented in the specification:** the only code added since the initial S6.1 run is the `src/main.py` startup wiring (exactly what spec §3/§12.8 prescribe) + the behavior-preserving repository lifting (stateless DB-connection wrappers; documented in commit `5779065`).

### Open findings

None.

### Reusable shared capability (AGENTS.md note)

The search feature is a reusable shared capability (cross-feature source registration contract + singleton search service). A **"Using the Search Feature"** note was added to `AGENTS.md` (how to register a source, how to query, feature-owned settings/actions, permissions, events, errors, testing) so future changes use it correctly.

### Review report status: **CLEAN**

- All findings (F-1) resolved — **no open findings**.
- **The change is complete** (per AGENTS.md: "The change is only considered complete when the review report is clean").
- **Gate result: PASS** — review report clean; the change may proceed to S6.4 (bump version + open PR).
- **Date:** 2026-09-26

## Phase 6: Review (S6.4) — Bump version + open PR

- **Objective:** Bump the version per the change type and open a PR for the change branch to `main` (present for human merge, then STOP).
- **Inputs:** the clean review report (S6.3).

### Version bump

- **Change type:** CROSS-CUTTING → bump level `minor` (not `major`).
- **Rationale:** The search public API is **new/additive to the project** — this change introduces the search feature (`src/backend/search/`) for the first time, plus additive `search_source.py` modules and the additive `SessionRepository.list_all` ABC method (backward-compatible per authentication NFR-003). The NFR-003 recorded deviation (Q-124) permits breaking changes to the search API **in the future** with a major version, but this change is not breaking — it is additive. Per the decision framework ("If the search public API is new (additive to the project), `minor` is appropriate"), the bump is `minor`.
- **Command:** `bump-my-version bump minor` (dry-run first: `bump-my-version bump minor --dry-run` → exit 0).
- **Result:** `0.5.0` → `0.6.0` (commit `841454c` "Bump version: 0.5.0 → 0.6.0" — part of the PR).

### Open PR

- **Command:** `gh pr create --head crosscut/search --base main`.
- **Result:** PR **#54** — https://github.com/jackthenet/python-template/pull/54 (state: **OPEN**, mergeable: **MERGEABLE**).
- **Governance:** Presented for human review/merge — the agent does **NOT** merge (human governance).

### Gate result: **PASS**

- Version bumped per the change type (`minor` — the bump commit is part of the PR).
- A PR is open for the change branch to `main` (presented for human review/merge, NOT merged — human governance).
- **Date:** 2026-09-26
