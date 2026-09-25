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
