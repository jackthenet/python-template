# Verification — Authentication Feature

**Spec:** `docs/specs/authentication.md`
**Branch:** `feature/authentication`

---

## Phase 3 — RED Evidence

**Date:** 2026-09-07
**Command:** `uv run pytest tests/acceptance/authentication/ tests/property/authentication/ tests/unit/authentication/ tests/contract/authentication/ tests/integration/authentication/ -v`

**Result: 5 collection errors, 0 passed** — the suite fails before implementation.

All five authentication test directories error at import time with
`ModuleNotFoundError: No module named 'backend.authentication'`.
The feature module `src/backend/authentication/` does not exist yet, so the
public API (`AuthService`, request models, representations, the error
hierarchy, repository ABCs + SQLite implementations, the `WebAuthnProvider`
ABC + `PyWebAuthnProvider`, `InMemoryAttemptTracker`, table models, and
events) is not importable.

### Test Inventory (67 tests, spec-derived)

| Category | File | Tests |
|---|---|---|
| Acceptance | `tests/acceptance/authentication/test_login.py` | AC-001 … AC-005 |
| Acceptance | `tests/acceptance/authentication/test_lockout.py` | AC-006 … AC-008 |
| Acceptance | `tests/acceptance/authentication/test_timing.py` | AC-009 |
| Acceptance | `tests/acceptance/authentication/test_sessions.py` | AC-010 … AC-014 |
| Acceptance | `tests/acceptance/authentication/test_password_reset.py` | AC-015 … AC-021 |
| Acceptance | `tests/acceptance/authentication/test_passkey.py` | AC-022 … AC-029 |
| Acceptance | `tests/acceptance/authentication/test_validation.py` | AC-030 |
| Acceptance | `tests/acceptance/authentication/test_events.py` | AC-031 … AC-033 |
| Acceptance | `tests/acceptance/authentication/test_representation.py` | AC-034 |
| Acceptance | `tests/acceptance/authentication/test_logging.py` | AC-035 |
| Property | `tests/property/authentication/test_tokens.py` | INV-001 |
| Property | `tests/property/authentication/test_sessions.py` | INV-002 |
| Property | `tests/property/authentication/test_reset.py` | INV-003 |
| Property | `tests/property/authentication/test_lockout.py` | INV-004 |
| Property | `tests/property/authentication/test_secrets.py` | INV-005 |
| Unit (edge) | `tests/unit/authentication/test_login.py` | EDGE-001, EDGE-002, EDGE-018 |
| Unit (edge) | `tests/unit/authentication/test_lockout.py` | EDGE-003 |
| Unit (edge) | `tests/unit/authentication/test_sessions.py` | EDGE-004 … EDGE-006, EDGE-017 |
| Unit (edge) | `tests/unit/authentication/test_reset.py` | EDGE-007 … EDGE-012 |
| Unit (edge) | `tests/unit/authentication/test_passkey.py` | EDGE-013 … EDGE-016 |
| Contract | `tests/contract/authentication/test_performance.py` | NFR-001 |
| Contract | `tests/contract/authentication/test_secrets.py` | NFR-002 |
| Contract | `tests/contract/authentication/test_public_api.py` | NFR-003 |
| Contract | `tests/contract/authentication/test_logging.py` | NFR-004 |
| Integration | `tests/integration/authentication/test_concurrency.py` | NFR-005 |
| Integration | `tests/integration/authentication/test_sqlite_repositories.py` | `test_session_repository_roundtrip`, `test_reset_repository_roundtrip`, `test_webauthn_repository_roundtrip`, `test_full_flow_login_reset_logout` |

Every test function name encodes its spec ID
(`test_<id>_<spec suffix>`), matching the spec's test strategy.

Shared helpers live in `tests/authentication_test_helpers.py`
(`EventCollector`, `valid_login`, `create_user`, `FakeWebAuthnProvider`,
`build_auth_service`, `build_memory_auth_service`, and the `auth` /
`auth_service` / `user_manager` / `collector` fixtures), mirroring the
user-management helper pattern.

### Commit

- RED baseline: see Phase 3 commit `test(authentication): add acceptance tests` (RED).

---

## Phase 4 — GREEN Evidence

**Date:** 2026-09-08
**Command:** `uv run pytest tests/acceptance/authentication/ tests/property/authentication/ tests/unit/authentication/ tests/contract/authentication/ tests/integration/authentication/ -q`

**Result: 67 passed** — the full authentication suite is GREEN.

The feature module `src/backend/authentication/` now exists and implements the
specification. All 67 spec-derived tests (10 acceptance, 5 property, 5 unit,
4 contract, 2 integration) pass. The full repository suite (282 tests across
all features) also passes, confirming no regression.

### Quality Gates

| Gate | Command | Result |
|---|---|---|
| Lint | `uv run ruff check src/backend/authentication/` | All checks passed |
| Format | `uv run ruff format --check src/backend/authentication/` | 11 files already formatted |
| Types | `uv run mypy src/backend/authentication/` | Success: no issues found in 11 source files |
| Full suite | `uv run pytest tests/ -q` | 282 passed |

### Implementation Summary

| Task | Module(s) | Status |
|---|---|---|
| T-001 (foundation) | `errors.py`, `tokens.py`, `models.py`, `protocols.py`, `repositories.py`, `events.py`, `__init__.py` | VERIFIED |
| T-002 (SQLite repositories) | `repository.py` (`SqliteSessionRepository`, `SqlitePasswordResetRepository`, `SqliteWebAuthnCredentialRepository`) | VERIFIED |
| T-003 (attempt tracker) | `tracker.py` (`InMemoryAttemptTracker`) | VERIFIED |
| T-004 (login/sessions) | `service.py` (`AuthService.login`, `session_info`, `logout`, `_issue_session`) | VERIFIED |
| T-005 (password recovery) | `service.py` (`AuthService.request_password_reset`, `complete_password_reset`) | VERIFIED |
| T-006 (passkey/WebAuthn) | `service.py` (passkey methods), `webauthn.py` (`PyWebAuthnProvider`) | VERIFIED |
| T-007 (integration/cross-cutting) | `service.py` (events, `@logged_class`, timing), full suite | VERIFIED |

### Refactor Notes

- `delete_expired` uses SQLModel `select()` so `s.exec` yields mapped objects
  (a raw `sa_select` returned rows, raising `UnmappedInstanceError`).
- `_dummy_verify` uses `contextlib.suppress(Argon2Error)` (SIM105).
- The class is traced via `@logged_class` (shared logging feature); `include_args`
  stays `False` so passwords and tokens never appear in log records (REQ-022).

### Test Fixes (Phase 3 helper/test bugs, not weakenings)

- `tests/authentication_test_helpers.py`: `FakeWebAuthnProvider.sign_count` was
  `0`; the AC-025/AC-026 contract expects the stored sign count to become `1`
  after a login ("the fake provider's assertion sign count"). Set to `1` so the
  standard WebAuthn logic (`stored = assertion.sign_count`) holds; a lower value
  (e.g. `0`) is the hijack regression.
- `tests/acceptance/authentication/test_sessions.py` (AC-014) and
  `tests/acceptance/authentication/test_events.py` (AC-033): the second service
  was built on the same `tmp_path` as the `auth` fixture, violating the `users`
  UNIQUE constraint. The second service now uses a separate subdirectory.
- `tests/property/authentication/test_sessions.py` (INV-002): added
  `deadline=None` to `@settings` — the test intentionally sleeps 150–350 ms for
  the expired phase, exceeding Hypothesis's default 200 ms per-case deadline.

### Commit

- GREEN: see Phase 4 commit (this change).

---
