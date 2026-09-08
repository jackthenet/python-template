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
