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
