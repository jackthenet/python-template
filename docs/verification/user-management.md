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

---

## Phase 4 — GREEN Evidence

**Date:** 2026-09-07
**Tasks:** T-001 … T-005 (all implemented, refactored, committed).

**Command:** `uv run pytest tests/ -q`

**Result: 215 passed, 0 failed.**

| Suite | Command | Result |
|---|---|---|
| Acceptance | `uv run pytest tests/acceptance/usermanagement/ -q` | 38 passed |
| Property | `uv run pytest tests/property/usermanagement/ -q` | 6 passed |
| Contract | `uv run pytest tests/contract/usermanagement/ -q` | 5 passed |
| Full regression | `uv run pytest tests/ -q` | 215 passed |

### Test bug fixes (Phase 3 RED artifacts, flagged as findings)

The Phase 3 suite contained test-side defects (not implementation defects).
Each was fixed minimally without weakening any contract assertion:

- `datetime.UTC` alias + local imports in edge tests (setup, not assertions).
- Hypothesis `_password()` strategy min length 5 → 8 (spec NFR-001).
- Duplicate default emails in multi-user setups (acceptance AC-024/AC-028,
  edge EDGE-016) — each user now gets a unique email.
- Fake-repo ABC base-class order (MRO shadowing) in AC-028.
- `test_inv_002` `assume(p1 != p2)` (changing to the same password keeps the
  old one valid — the invariant only applies to distinct passwords).
- `test_inv_006` `before` snapshot moved before `create_user`; no-op
  activate/deactivate skip the event assertion (REQ-009: no-ops publish no
  event); `password` op uses an 8-char password (NFR-001).
- NFR-004 unambiguous username collision (a full duplicate violates both
  UNIQUE constraints; SQLite reports an ambiguous one).
- `test_full_user_lifecycle` guardian admin (REQ-008: the primary user's
  admin deactivation/activation/deletion must not leave zero active admins).

### Commit

- `feat(usermanagement): implement UserManager service, repository, models (T-001..T-005)`
- `chore(usermanagement): mark T-001..T-005 VERIFIED in task DAGs`

---

## Phase 5 — Verification Report

**Date:** 2026-09-07
**Spec:** `docs/specs/user-management.md`

### Check results

| # | Check | Command / Method | Result |
|---|---|---|---|
| 1 | Every `REQ-XXX` has ≥ 1 `AC-XXX` | `scripts/verify_spec.py` | PASS (REQ-001…REQ-017) |
| 2 | Every `AC-XXX` has ≥ 1 executable test | `scripts/verify_spec.py` | PASS (AC-001…AC-038) |
| 3 | No orphaned tests | manual (72 test funcs) | PASS (70 named with spec IDs; 2 cross-cutting integration tests referenced in spec test strategy L427–428) |
| 4 | Every `INV-XXX` has a property test | `scripts/verify_spec.py` | PASS (INV-001…INV-006) |
| 5 | All acceptance tests pass | `pytest tests/acceptance/usermanagement/ -q` | PASS (38) |
| 6 | Full regression suite passes | `pytest tests/ -q` | PASS (215) |
| 7 | Lint (feature files) | `ruff check` on usermanagement paths | PASS (0 errors) |
| 7b | Lint (repo-wide) | `ruff check src/ tests/` | 27 pre-existing errors in `settings` test files (not usermanagement) — see Findings |
| 8 | Type check | `mypy src/` | PASS (18 source files, no issues) |
| 9 | Coverage (feature) | `pytest tests/ --cov=src/backend/usermanagement --cov-branch` | 96% branch (secondary signal) |
| 10 | Architecture rules | `tests/architecture/` | N/A (no such suite in this project; manual check in Phase 6) |
| 11 | Spec validation | `scripts/verify_spec.py` | PASS (exit 0, Traceability: PASS) |

### Coverage detail (branch)

| File | Stmts | Miss | Branch | Cover |
|---|---|---|---|---|
| `__init__.py` | 7 | 0 | 0 | 100% |
| `errors.py` | 17 | 0 | 0 | 100% |
| `events.py` | 31 | 0 | 0 | 100% |
| `models.py` | 107 | 2 | 20 | 97% |
| `repository.py` | 94 | 3 | 20 | 96% |
| `service.py` | 145 | 5 | 54 | 95% |
| **TOTAL** | **401** | **10** | **94** | **96%** |

### Spec coverage

**Spec coverage = 100%.** Every normative requirement (`REQ-001…REQ-017`)
maps to ≥ 1 acceptance criterion, every acceptance criterion (`AC-001…AC-038`)
maps to ≥ 1 GREEN executable test, and every invariant (`INV-001…INV-006`)
maps to ≥ 1 GREEN property test. Code coverage (96%) is a secondary quality
signal; specification coverage is the primary evidence and is complete.

### Findings

1. **Pre-existing repo-wide lint failures (settings feature).**
   `uv run ruff check src/ tests/` reports 27 errors, all in `settings` test
   files (`tests/acceptance/settings/test_settings.py`,
   `tests/contract/settings/test_settings_contracts.py`,
   `tests/property/settings/test_settings_properties.py`,
   `tests/unit/settings/test_settings_edges.py`,
   `tests/integration/settings/test_settings_integration.py`). These are not
   part of the usermanagement feature and were not introduced by this work.
   All usermanagement files pass lint with 0 errors. This is a pre-existing
   issue for the settings feature owner to address.

2. **`pytest-cov` added as a dev dependency.** The project venv did not have
   `pytest-cov`/`coverage` (the `[tool.coverage.run]` config expected them but
   they were not in the dev group). `pytest-cov>=5.0` was added via
   `uv add --dev` to enable the coverage check required by the verify skill.

### Verdict

**VERIFIED.** All verification checks pass for the usermanagement feature.
Spec coverage = 100%. The two findings are non-blocking (pre-existing
repo-wide lint in another feature; a dev dependency addition).
