# session-lookup-unwired — Triage Record (ISSUE)

- **Change:** session-lookup-unwired · **Type:** ISSUE (classified at P.1, first matching criterion: "fixes a deviation from **approved spec behavior**; no new behavior is introduced")
- **Branch / worktree:** `issue/session-lookup-unwired` @ `ab4b4f8` (== `main`, `pyproject.toml:4` version `0.6.0`), worktree `../python-template_kopie-worktrees/issue/session-lookup-unwired` — created at **P.4** from `main` (git skill, "Create change worktree (P.4)"), so the branch carries the TODO file and the answered question file as of P.3.
- **Normative basis:** the approved spec `docs/specs/user-roles-permissions.md` (no new spec; this change has none — AGENTS.md "ISSUE (triage — no spec, no PR)")
- **Phase Matrix for this type:** Phase P → triage record (this file) · Phase 1–2 skipped · **Phase 3** reproduction test → RED · **Phase 4** minimal fix → GREEN · **Phase 5** targeted + smoke (**light tier**, see §Light-tier) · **Phase 6** review + PR + `patch` bump (AGENTS.md Versioning: `ISSUE → patch`).
- **Date:** 2026-10-03

## Phase P record

| Step | Date | Result |
|---|---|---|
| P.1 Frame (orchestrator, `main`) | 2026-10-03 | `docs/todo/session-lookup-unwired.md` + `docs/questions/session-lookup-unwired.md` created on `main`; type **ISSUE**; found during the `api-keys` P.2 interrogation |
| P.2 Interrogate | 2026-10-03 | **DONE — 0 questions needing user input** (no `BLOCKED-USER`). The full triage evidence — defect confirmation, six closed points (C-1…C-6), reproduction plan, light-tier check, overlap check — is recorded in `docs/questions/session-lookup-unwired.md`. Overlap check clean against `docs/specs/` and all 17 other TODOs |
| P.3 Answer (orchestrator ⏸, `main`) | 2026-10-03 | **no-op** — 0 questions to present, 0 answer rounds; question file `Status: ALL ANSWERED` |
| P.4 Draft triage + create branch/worktree | 2026-10-03 | **this file** — worktree + branch created, triage recorded, every citation re-verified independently in this worktree (below) |
| P.5 Self-consistency | n/a | ISSUE — P.5 runs for FEATURE/CROSS-CUTTING only (AGENTS.md, Phase P table) |

**Why (from the TODO, `docs/todo/session-lookup-unwired.md:17`):** wire the session lookup into the composition root so a session-token-bearing permission check actually validates the session instead of always denying.

---

## 1. Type and classification rationale

**ISSUE.** The observed behaviour deviates from **approved, already-specified** behaviour: REQ-017 and AC-020 (`docs/specs/user-roles-permissions.md:513`, `:552`) require the check to validate a provided session token via the session lookup, and the spec's Impact Analysis (`:827`) asserts that the wiring exists in the composed application. The fix restores that specified behaviour through an **existing, already-public** constructor parameter (`session_lookup`, `src/backend/permissions/service.py:134`) — it introduces no new externally observable behaviour, no new capability, no signature change, and no spec wording change. First matching criterion in the AGENTS.md classification table therefore applies (criterion 1, ISSUE); FEATURE (criterion 2, "not covered by an approved spec") does not, because it **is** covered.

## 2. Affected requirements and acceptance criteria

All IDs are from the existing approved spec **`docs/specs/user-roles-permissions.md`** (AGENTS.md ISSUE item 11 — cite the spec file and IDs). Related: `docs/specs/session-management.md` (the session repository's `get_by_token_hash`, named in the TODO's Related-specs line).

| ID | Spec line | Required behaviour (as written) |
|---|---|---|
| **REQ-017** | `:513` | When `session_token` is provided, the check validates the session via the session lookup: unknown / revoked / expired → deny (`invalid_session`); a session belonging to a different user → deny (`session_principal_mismatch`); token omitted → validation skipped |
| **AC-020** | `:552` | A valid, unrevoked, unexpired session token for `u` → the session is validated and the check **proceeds** with the user/role evaluation; revoked → `False` (`invalid_session`); another user's token → `False` (`session_principal_mismatch`) |
| **AC-021** | `:553` | `session_token=None` → validation skipped, evaluation proceeds |
| **EDGE-007** | `:597` | A check with a token when the session lookup is **unavailable (None or raises)** → deny (reason `storage_error`) |
| **Impact Analysis** | `:827` | "The session repository (`get_by_token_hash`) **is used by the check** for session validation (REQ-017)" — the spec asserts the wiring is real in the composed application |

## 3. Defect confirmation (observed vs required)

Re-verified in this worktree at `ab4b4f8`.

**Observed.** `src/main.py:145-153` constructs `PermissionService(SqliteRoleRepository, SqliteGrantRepository, SqliteSystemPrincipalRepository, _user_manager_proxy, catalog=_catalog, event_bus=get_event_bus(), settings_registry=_settings_registry)` with **no `session_lookup=` argument** — verified: the call at `:145-153` passes three positional repositories, the lazy user-manager proxy (`:149`), and three keywords (`:150-152`). So `self._session_lookup` stays `None` (`src/backend/permissions/service.py:143`, default `None` at `:134`), and `_validate_session` returns `"storage_error"` for **every** non-`None` token (`src/backend/permissions/service.py:407-408`) before the catalog / admin-wildcard / grant steps run. `rg -n "session_lookup\s*=" src tests` (re-run here) finds the argument **only** in tests — `tests/acceptance/permissions/test_check_api.py`, `tests/unit/permissions/test_edge_cases.py`, `tests/property/permissions/test_invariants.py` — and never in `src/`. The path is reachable in production: `@requires_permission` forwards `principal.session_token` to the checker (`src/backend/shared/principal.py:74`), and `Principal.session_token` is a specified field.

**Required.** REQ-017 / AC-020 / `:827`: the check validates the token against the session repository and **proceeds** when the session is valid.

**Deviation.** In the composed application any check carrying a session token denies with `storage_error`; the specified positive branch of AC-020 is unachievable outside tests, and REQ-017's validation path never runs. EDGE-007 is **not** the specified state here — EDGE-007 (`:597`) covers a lookup that is genuinely unavailable or raising, not a composition root that never supplies one. The defect is latent in-repo (no in-repo caller constructs a `Principal` with a token) but live at the public API (`has_permission(..., session_token=…)`, `Principal(session_token=…)`), and the future HTTP / api-keys surface would inherit a check path that cannot validate sessions.

**Traceability state (recorded, not refreshed — decision Q-129, convention B).** The spec's own matrix records REQ-017/AC-020 and REQ-017/AC-021 as **`PENDING`** (`docs/specs/user-roles-permissions.md:786-787`); `docs/verification/traceability.md:680-681` records the same two rows as **`GREEN`** via `test_session_validation_in_check` / `test_session_validation_skipped_when_token_none`. Neither is wrong for what it observed: the GREEN test injects a **fake** lookup (`tests/acceptance/permissions/test_check_api.py:398`, `:459`, `:494` pass stub lookups), so AC-020 is covered at the **service** level and **uncovered at the composition root** — exactly the gap this ISSUE reproduces. The reproduction test is added to the matrix in Phase 3 / Phase 5 (S5.3), no existing row is refreshed.

## 4. Does the fix require behaviour the spec does not state?

**No.** The fix supplies the dependency the spec already requires at `:827` through the parameter the public constructor already declares (`service.py:134`). No spec wording changes, no new public interface, no new type, no new dependency, no behaviour beyond REQ-017 / AC-020 / AC-021 / EDGE-007. Therefore **no Spec Amendment PR and no reclassification to FEATURE** (AGENTS.md ISSUE item 13 and the Escalation Rules are not triggered).

## 5. Reproduction plan (Phase 3)

**New test file / function:** `tests/acceptance/permissions/test_composition_wiring.py::test_ac_020_composition_root_validates_session_token` (AC-020 / REQ-017). It must exercise the **real composition root** — every existing permissions test builds its own `PermissionService` and therefore cannot see the missing wiring.

**Setup pattern to reuse (established — do not invent one):** `tests/acceptance/settings_coverage/test_wiring.py::test_main_wires_all_features` (`:12-31`) already executes the composition root: `subprocess.run([sys.executable, "-c", code], cwd=…, check=False)` where `code` does `sys.path.insert(0, 'src')`, replaces the settings-registry singleton with `SettingsRegistry(value_repository=YamlValueRepository(tempfile.mkdtemp()))` so nothing leaks into the repo's `settings/` dir, then `import main`. The new test passes `cwd=tmp_path` (the existing test uses `cwd=_REPO_ROOT` at `:29`) so the relative SQLite URLs (`sqlite:///./data/…`) create their DBs under the temp dir.

**Body (minimal, no enforcement interference):** after `import main` —
1. insert an **admin** user directly through the composed store: `main._user_repository.add(User(username="alice", email="alice@example.com", password_hash="x", roles=["admin"]))` — admin skips the grant step (REQ-010 implicit wildcard) and skips the enforced `UserManager` path (`usermanagement.create_user` is not in `BOOTSTRAP_SYSTEM_PERMISSIONS`);
2. insert a session row through the composed session store: `main._session_repository.add(Session(user_id=u.id, token_hash=hashlib.sha256(b"tok").hexdigest(), created_at=now, expires_at=now + 7d, revoked=False))` — the same hash the check computes (`service.py:409`, byte-identical to authentication's `hash_token`);
3. `print(main._permission_service.has_permission(u.id, "usermanagement.get_user", session_token="tok"))`.

**The assertion that fails today:** `assert result.stdout.strip().endswith("True")`. Today the composed service returns **`False`** — `_validate_session` returns `"storage_error"` at `service.py:407-408` before the catalog/admin-wildcard steps — so the test is RED **on behaviour**, not on a `ValidationError`: the fixture data is valid and in-domain throughout (a real `User` row, a real `Session` row, a key that exists in the closed catalog). After the fix the same call returns `True` → GREEN.

**Regression guards in the same test (GREEN before and after — they prove the fix is not a blanket allow):** `has_permission(u.id, "usermanagement.get_user", session_token="nope")` → `False` (`invalid_session`), and a token whose session belongs to a different user → `False` (`session_principal_mismatch`). One test function plus these two asserts — no fixtures, no new helper module.

**Commands (targeted, per AGENTS.md "Targeted GREEN" — the full suite is a Phase 5/6 gate):**
- `red_command`: `uv run pytest tests/acceptance/permissions/test_composition_wiring.py -v`
- `green_command`: `uv run pytest tests/acceptance/permissions/test_composition_wiring.py tests/acceptance/permissions/test_check_api.py tests/unit/permissions/test_edge_cases.py -v`

## 6. Fix scope (Phase 4)

**The whole fix, in `src/main.py`:** move `_AUTH_DB = "sqlite:///./data/authentication.db"` (`:177`) and `_session_repository = SqliteSessionRepository(_AUTH_DB)` (`:178`) to just above `_PERMISSION_DB` (`:144`), and add `session_lookup=_session_repository,` to the `PermissionService(...)` call (`:145-153`). Net: **1 file, 2 lines moved + 1 keyword added.**

| File | Change |
|---|---|
| `src/main.py` | the two-line move + one keyword (the only source file) |
| `tests/acceptance/permissions/test_composition_wiring.py` | new reproduction test (Phase 3) |
| `docs/verification/traceability.md` | new row(s) for the reproduction test (S5.3) |

**No lazy proxy is needed — there is no cycle.** `SqliteSessionRepository.__init__(database_url: str)` depends on nothing but the URL (it mkdirs the parent, creates the engine, runs `SQLModel.metadata.create_all`), so constructing it earlier is safe. The `_LazyUserManager` / `_LazyPermissionService` proxies (`src/main.py:92-126`) exist only for the two **real** cycles (PermissionService ↔ UserManager, PermissionService ↔ settings registry); adding a third proxy here would be a **larger** solution than the problem. Nothing depends on the current order (`rg -n "_session_repository|_AUTH_DB" tests` → only `tests/integration/authentication/test_sqlite_repositories.py`, which builds its own repository). The separate DB files are fine (`_PERMISSION_DB` `:144` vs `_AUTH_DB` `:177`): the lookup is a separate object over a separate store and the permission repositories never read the sessions table.

**Explicitly out of scope** (TODO "Out of scope", `docs/todo/session-lookup-unwired.md:26-30`): `PermissionService`'s check logic, the `SessionLookup` protocol, the fail-closed behaviour for a genuinely unavailable lookup, any new session/permission behaviour, and the `api-keys` credential type. Also out of scope: the module-singleton fallback `get_permission_service()` (`src/backend/permissions/service.py:497-514`), which likewise omits `session_lookup` but has **no caller in `src/`** (used only by `tests/integration/permissions/test_persistence.py`) — wiring it would be behaviour nobody calls.

## 7. Light-tier qualification (AGENTS.md "Light ISSUE tier")

**Verdict: QUALIFIES** — all four criteria hold.

| Criterion | Check |
|---|---|
| Single feature; fix touches ≤ 3 files excluding tests | **Yes** — **1 file** (`src/main.py`). The composition root is shared wiring, not another feature's module; no feature module is modified |
| No new dependency | **Yes** — `SqliteSessionRepository` is already imported and used in `src/main.py:178` |
| No new public interface; no cross-feature change | **Yes** — `session_lookup` is already the 5th parameter of the public constructor (`service.py:134`); both features' code is untouched; the session store is reused exactly as already specified at `user-roles-permissions.md:827` |
| Existing suite covers the affected area | **Yes** — covering tests: `tests/acceptance/permissions/test_check_api.py::test_session_validation_in_check` (AC-020, `:351`) and `::test_session_validation_skipped_when_token_none` (AC-021, `:433`); `tests/unit/permissions/test_edge_cases.py::test_unavailable_session_lookup_denied` (EDGE-007, `:307`); `tests/property/permissions/test_invariants.py` (fail-closed invariant); `tests/acceptance/settings_coverage/test_wiring.py::test_main_wires_all_features` (composition-root pattern, `:12`); `tests/acceptance/sessionmanagement/test_store_reuse.py::test_ac_033_same_sessions_table_as_authentication` (the reused session store) |

**Consequence for Phase 5 (targeted + smoke):** `uv run pytest tests/acceptance/permissions tests/unit/permissions tests/property/permissions tests/acceptance/settings_coverage/test_wiring.py -v`, plus `uv run ruff check .` and `uv run mypy src/`. The **full regression suite runs as the Phase 6 pre-merge gate (S6.4)** and must pass, with the result recorded in the review report. Because the change is in the composition root, the full suite is the real safety net — it must not be skipped at S6.4.

## 8. Constraints

- **Fail-closed is a hard invariant** (`docs/specs/user-roles-permissions.md:19`: "Fail-closed on every undeterminable check (hard invariant)"). The fix must not turn a storage failure into an allow: the fail-closed branches (`service.py:407-408` for a `None` lookup, `:412-413` for a raising lookup) stay untouched, and supplying a lookup in the composition root does not weaken them.
- **EDGE-007 tests stay GREEN** — `tests/unit/permissions/test_edge_cases.py::test_unavailable_session_lookup_denied` (spec test-strategy row `:735`) and the property fail-closed invariant must not change.
- **The reproduction test must go through the real composition root** (`src/main.py`), not a hand-built `PermissionService` — a test that builds its own service cannot catch this class of defect (TODO "Constraints and risks", `docs/todo/session-lookup-unwired.md:37`).
- **No test may be weakened or deleted** to reach GREEN; no public API break (spec constraint at `:19`).
- Startup ordering is deliberate elsewhere in `src/main.py` (the lazy proxies break real cycles) — the two-line move is the only reordering this change performs, and it is justified by the absence of a cycle (§6).

## Acceptance signal (from the TODO, `docs/todo/session-lookup-unwired.md:41`)

A test that starts the application's real wiring and calls a permission check with a valid, unrevoked, unexpired session token **passes**; the same check with a revoked or another user's token still **denies**; the full suite and the EDGE-007 fail-closed tests stay green.

---

## Phase 3 / RED evidence (S3.1, 2026-10-03)

**Reproduction test (exactly the §5 plan):** `tests/acceptance/permissions/test_composition_wiring.py::test_ac_020_composition_root_validates_session_token` — one new test module in the affected feature's acceptance directory; **no `src/` change, no existing test modified**.

It exercises the **real composition root**: `import main` in a fresh interpreter (`subprocess.run([sys.executable, "-c", code], cwd=tmp_path)`), then four checks through `main._permission_service.has_permission(alice.id, "usermanagement.get_user", session_token=…)` — never a hand-built `PermissionService`. Fixture data is written through the composed stores (`main._user_repository.add(User(...))`, `main._session_repository.add(Session(...))` with the SHA-256 hash the check computes), all valid and in-domain.

**Deviation from the §5 setup sketch (recorded, not a re-decision):** the subprocess inserts the **absolute** `<worktree>/src` on `sys.path` instead of the relative `'src'` used by `tests/acceptance/settings_coverage/test_wiring.py:15`, because `cwd` is `tmp_path` here (as §5 requires) so a relative entry would not resolve. With `cwd=tmp_path` the composition root's relative SQLite URLs (`sqlite:///./data/…`) and its `settings/` directory are created inside the temp dir, so the settings-registry singleton pre-replacement of that pattern is unnecessary (`src/main.py` installs its own registry into the singleton anyway) and was not copied.

### AC-020 / REQ-017 — RED

- **command:** `uv run pytest tests/acceptance/permissions/test_composition_wiring.py -v`
- **result:** `FAILED tests/acceptance/permissions/test_composition_wiring.py::test_ac_020_composition_root_validates_session_token` — `1 failed in 1.42s`
- **failure mode:** **assertion on behavior** — `AssertionError: [False, False, False, False]` at `tests/acceptance/permissions/test_composition_wiring.py:105`. The composed service denies the valid-token check (the `session_lookup is None` → `storage_error` path, `src/backend/permissions/service.py:407-408`); the expected outcome is `[True, False, False, False]` (valid → proceeds; revoked / another user's / unknown → deny).
- **not a valid-RED violation:** no collection, import or fixture error, no `ValidationError`/`ValueError` from test data — the subprocess exits `0` (the `returncode == 0` guard passes) and only the outcome assertion fails.
- **pre-flight collection check:** `uv run pytest --collect-only tests/acceptance/permissions/test_composition_wiring.py -q` → `1 test collected in 0.12s` (clean, before and after deriving).
- **satisfiability check (test-contract sanity, scratch only, not committed):** the same script with the lookup supplied (`main._permission_service._session_lookup = main._session_repository`) prints `[True, False, False, False]` — the exact GREEN the §6 fix must produce — so the RED is the missing wiring and not a broken fixture (rows, token hash, admin wildcard REQ-010 and the catalog all resolve through the composed stores).
- **negative guards (GREEN before and after the fix — they prove the fix is not a blanket allow):** revoked token, another user's token, unknown token → `False` in both runs.
- **ruff (changed paths):** `uv run ruff check tests/acceptance/permissions/test_composition_wiring.py` → `All checks passed!`; `uv run ruff format tests/acceptance/permissions/test_composition_wiring.py` → `1 file left unchanged`.
- **commit:** this commit (`issue(session-lookup-unwired): S3.1 reproduction test (composition-root session lookup)`).

**Deferred by design:** the RED *gate* record (S3.2) and the `docs/verification/traceability.md` row (S5.3; decision **Q-02** — the spec §11 rows stay as the historical record, no Spec Amendment).

### Phase 3 gate — RED CONFIRMED (S3.2, 2026-10-03)

Independent re-run of the S3.1 test at commit `94d5b59` (no source change, no test change).

| Gate | Command | Result |
|---|---|---|
| pre-flight collection | `uv run pytest --collect-only tests/acceptance/permissions/test_composition_wiring.py -q` | `1 test collected in 0.12s` — clean, no import/collection error |
| **RED** | `uv run pytest tests/acceptance/permissions/test_composition_wiring.py -v` | **`1 failed in 1.42s`** — `FAILED ...::test_ac_020_composition_root_validates_session_token` |
| ruff (changed paths only) | `uv run ruff check tests/acceptance/permissions/test_composition_wiring.py` | `All checks passed!` (repo-wide sweep stays a Phase 5 gate) |

**Failure mode = assertion on behavior (valid RED).** `AssertionError: [False, False, False, False]` — `assert False` + `where False = str.endswith('[True, False, False, False]')`. The subprocess exited `0` (the `returncode == 0` guard passed), so the composition root imported and ran; only the outcome assertion fails. The subprocess log confirms the defect path four times: `backend.permissions.service:_deny:422 - permission check denied: user_id=… permission=usermanagement.get_user reason=storage_error` — i.e. `_validate_session` short-circuits on the `None` lookup (`src/backend/permissions/service.py:407-408`), exactly §3. No setup/fixture/collection error, no `ValidationError`/`ValueError` from test data → the test-contract sanity check passes.

**Path-portability check (S3.1 flag, resolved — no fix needed).** The test derives the subprocess `sys.path` entry from its own file location: `_REPO_ROOT = Path(__file__).resolve().parents[3]` / `_SRC = _REPO_ROOT / "src"` (`tests/acceptance/permissions/test_composition_wiring.py:24-25`), interpolated into the subprocess code as `sys.path.insert(0, {str(_SRC)!r})` (`:35`). `grep -n "C:/workspace" tests/acceptance/permissions/test_composition_wiring.py` → no match, so there is **no hard-coded absolute worktree path** and the test resolves correctly wherever the branch is checked out. The absolute path visible in the pytest output is the *runtime* value of `_SRC`, not a literal in the file.

**Gate: RED CONFIRMED.** Phase 3 exit criterion met; the change may enter Phase 4 (S4.1/S4.2 minimal fix, `green_command` per §5). Traceability row remains deferred to S5.3 (Q-02).
