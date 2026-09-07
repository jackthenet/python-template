# Verification — User Management Feature

**Spec:** `docs/specs/user-management.md`
**Branch:** `feature/user-management`

---

## Phase 3 — RED Evidence

**Date:** 2026-09-07
**Command:** `uv run pytest tests/acceptance/usermanagement/ tests/property/usermanagement/ tests/unit/usermanagement/ tests/contract/usermanagement/ tests/integration/usermanagement/ -v`

**Result: 5 collection errors, 0 passed** — the suite fails before implementation.

All five user-management test modules error at import time with
`ModuleNotFoundError: No module named 'backend.usermanagement'`.
The feature module `src/backend/usermanagement/` does not exist yet, so the
public API (`UserManager`, `UserRepository`, `SqliteUserRepository`, schemas,
events, errors) is not importable.

### Test Inventory (72 tests, spec-derived)

| Category | File | Tests |
|---|---|---|
| Acceptance | `tests/acceptance/usermanagement/test_usermanagement.py` | AC-001 … AC-038 |
| Property | `tests/property/usermanagement/test_usermanagement_properties.py` | INV-001 … INV-006 |
| Unit (edge) | `tests/unit/usermanagement/test_usermanagement_edges.py` | EDGE-001 … EDGE-021 |
| Contract | `tests/contract/usermanagement/test_usermanagement_contracts.py` | NFR-001 … NFR-005 |
| Integration | `tests/integration/usermanagement/test_usermanagement_integration.py` | `test_full_user_lifecycle`, `test_events_and_persistence_across_instances` |

Every test function name encodes its spec ID
(`test_<id>_<spec suffix>`), matching the spec's test strategy.

Shared helpers live in `tests/usermanagement_test_helpers.py`
(`EventCollector`, `valid_create`, `db_url`), mirroring the
settings/event-bus helper pattern.

### Commit

- RED baseline: see Phase 3 commit `test(user-management): add acceptance tests` (RED).
