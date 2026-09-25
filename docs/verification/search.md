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
