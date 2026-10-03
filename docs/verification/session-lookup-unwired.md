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

---

## Phase 4 / GREEN evidence (S4.2, 2026-10-03)

**Minimal fix, exactly the §6 fix scope — `src/main.py` only.** `git diff --stat` → `1 file changed, 8 insertions(+), 2 deletions(-)` (2 moved lines + 1 keyword + 4 comment lines). No test file, no other `src/` file, no spec file touched.

### Diff summary

| Location | Change |
|---|---|
| `src/main.py` (new block above `_PERMISSION_DB`) | `_AUTH_DB = "sqlite:///./data/authentication.db"` and `_session_repository = SqliteSessionRepository(_AUTH_DB)` **moved** from the "remaining five services" block to just above the `PermissionService` construction, with a 4-line comment recording why no lazy proxy is needed (the repository depends only on its database URL — §6) |
| `src/main.py` (`PermissionService(...)` call) | `session_lookup=_session_repository,` added as the 5th argument (its declared position in the constructor, `src/backend/permissions/service.py:134`) |
| `src/main.py` (old location) | the two lines removed; `_auth_service = AuthService(...)` still receives the same `_session_repository` instance and `_AUTH_DB` — the same objects, constructed earlier |

**Wiring order otherwise unchanged (constraint 1).** The deliberate cycle-avoidance is intact and untouched by the diff: `_permission_service_proxy` / `_user_manager_proxy` are still created before the registry, `PermissionService` still receives `_user_manager_proxy` (not the real manager), `_permission_service_proxy.set_service(...)` still runs before the settings registration, and `_user_manager_proxy.set_manager(_user_manager)` still runs after `UserManager` is built. The only reordering is the two session-repository lines (§6). `SqliteSessionRepository.__init__` touches no settings, no permissions and no other service (`src/backend/authentication/repository.py`: mkdir parent → `create_engine` → `SQLModel.metadata.create_all`), so constructing it earlier has no side effect on the rest of the composition root.

**Fail-closed untouched (hard invariant, §8).** No line of `src/backend/permissions/` changed: the `self._session_lookup is None → "storage_error"` branch (`service.py:407-408`) and the `except Exception → "storage_error"` branch (`:412-413`) are unchanged; the fix only supplies a lookup in the composition root.

### Commands and results (targeted — the full suite is the Phase 5 gate / Phase 6 pre-merge gate)

| Gate | Command | Result |
|---|---|---|
| **GREEN (the §5 `green_command`)** | `uv run pytest tests/acceptance/permissions/test_composition_wiring.py tests/acceptance/permissions/test_check_api.py tests/unit/permissions/test_edge_cases.py -v` | **`45 passed in 3.36s`** |
| **GREEN (the reproduction test, done-criterion 2)** | `uv run pytest tests/acceptance/permissions/test_composition_wiring.py -v` | **`1 passed in 1.55s`** — `test_ac_020_composition_root_validates_session_token PASSED`; the composed check now yields `[True, False, False, False]` (valid token proceeds; revoked / another user's / unknown still deny) |
| **EDGE-007 fail-closed (done-criterion 3)** — every test file `rg -l "storage_error" tests` finds, plus the INV-002 property | `uv run pytest tests/unit/permissions/test_edge_cases.py tests/acceptance/permissions/test_check_api.py "tests/property/permissions/test_invariants.py::test_undeterminable_never_true" -q` | **`45 passed in 2.70s`** — incl. `test_unavailable_session_lookup_denied` (EDGE-007, `test_edge_cases.py:307`), `test_lookup_raises_denied` (`:383`), `test_storage_error_denied_fail_closed` (`test_check_api.py:264`), `test_revoked_expired_token_denied` / `test_mismatched_token_denied` (REQ-017 negative branches), INV-002 `test_undeterminable_never_true` over the `lookup_none` / `lookup_raises_session` scenarios |
| **Affected-feature smoke (done-criterion 4)** | `uv run pytest tests/acceptance/permissions tests/unit/permissions -q` | **`59 passed in 3.91s`** — no new failures |
| Composition-root guard (extra, cheap) | `uv run pytest tests/acceptance/settings_coverage/test_wiring.py -q` | `1 passed in 1.27s` — the reordered composition root still wires all features |
| **ruff (changed paths only)** | `uv run ruff check src/main.py` | **`All checks passed!`** |
| ruff format (changed path) | `uv run ruff format src/main.py` | `1 file left unchanged` |

**No test was weakened, changed or deleted** — `git diff --stat` shows only `src/main.py`; the reproduction test is byte-identical to the S3.1/S3.2 RED version, and it flipped from `1 failed` to `1 passed` on the source change alone.

**Not run here by design:** the full suite (Phase 5 S5.1 / Phase 6 pre-merge gate), the repo-wide `ruff check .` (Phase 5 S5.2), and `mypy src/` (Phase 5 S5.2). No untyped code was introduced (the change is one keyword argument on an existing typed parameter and two already-typed module-level assignments).

**Gate: GREEN CONFIRMED.** AC-020's positive branch is now reachable in the composed application; REQ-017's validation path runs; EDGE-007 and INV-002 fail-closed behavior is unchanged. Traceability row still deferred to S5.3 (Q-02).

---

## Phase 5 / verification (S5.1 + S5.2, light tier, 2026-10-03)

**Combined execution (recorded per the task-definition).** S5.1 (test gates) and S5.2 (lint + types) were run in **one** subagent execution. Both are read-only gate runs with no artifact dependency between them, and for a **light-tier ISSUE** S5.1 is not the full-suite run the standard step prescribes — it is the targeted + smoke set the triage §7 defines — so the two gate runs share one worktree warm-up (`uv` env, ruff/mypy caches) and produce one evidence section. No implementation, test, spec or traceability file was modified in this step; the only write is this section.

**Light-tier statement.** Per §7 (all four criteria hold: 1 source file, no new dependency, no new public interface / cross-feature change, existing suite covers the area), Phase 5 runs **targeted + smoke instead of the full regression suite**. The **full regression suite is deferred to the Phase 6 pre-merge gate (S6.4)** and must pass there, with the result recorded in the review report — because the change is in the composition root, the full suite is the real safety net and must not be skipped at S6.4.

### Gate results

| # | Gate | Command | Result |
|---|---|---|---|
| 1 | **Reproduction test GREEN** (AC-020 / REQ-017) | `uv run pytest tests/acceptance/permissions/test_composition_wiring.py -v` | **`1 passed in 1.33s`** — `test_ac_020_composition_root_validates_session_token PASSED` (composed check yields `[True, False, False, False]`) |
| 2 | **Covering tests named in the triage §7 + affected feature's test directories** (AC-020/AC-021 `test_check_api.py`, EDGE-007 `test_edge_cases.py`, INV-002 fail-closed property) | `uv run pytest tests/acceptance/permissions tests/unit/permissions tests/property/permissions -v` | **`64 passed in 7.69s`** — incl. `test_session_validation_in_check`, `test_session_validation_skipped_when_token_none`, `test_unavailable_session_lookup_denied` (EDGE-007), `test_lookup_raises_denied`, `test_storage_error_denied_fail_closed`, `test_undeterminable_never_true` (INV-002) |
| 3a | **Smoke — composition-root wiring** | `uv run pytest tests/acceptance/settings_coverage -v` (run inside 3b) | passed — incl. `test_main_wires_all_features` (the reordered composition root still wires all features) |
| 3b | **Smoke — affected features (session-management + authentication, all existing test dirs)** | `uv run pytest tests/acceptance/settings_coverage tests/acceptance/sessionmanagement tests/unit/sessionmanagement tests/property/sessionmanagement tests/acceptance/authentication tests/unit/authentication tests/property/authentication -v` | **`126 passed in 27.75s`** — incl. `tests/acceptance/sessionmanagement/test_store_reuse.py::test_ac_033_same_sessions_table_as_authentication` (the reused session store) and `tests/acceptance/authentication/test_enforcement_wiring.py` |
| 4 | **Lint — whole repo (the one Phase 5 full-repo sweep, matches CI `.github/workflows/lint.yml`)** | `uv run ruff check .` | **`All checks passed!`** (exit `0`) — **zero errors repo-wide**, therefore **zero in the change's diff**; nothing pre-existing to report or leave out of scope |
| 5 | **Types** | `uv run mypy src/` | **`Success: no issues found in 83 source files`** |

Smoke directory set was adjusted to the directories that actually exist (`ls tests/acceptance tests/unit tests/property`): the three permissions directories of gate 2 plus `settings_coverage`, `sessionmanagement` and `authentication` at acceptance/unit/property level — the features whose wiring the diff touches (the session repository construction moved above `PermissionService`; the same `_session_repository` instance and `_AUTH_DB` still feed `AuthService`).

**Named-test spot re-run (evidence for the names cited above, not a separate gate):** `uv run pytest <the 9 named tests> -v` → **`9 passed in 2.18s`** — `test_session_validation_in_check`, `test_session_validation_skipped_when_token_none`, `test_storage_error_denied_fail_closed`, `test_lookup_raises_denied`, `test_unavailable_session_lookup_denied`, `test_undeterminable_never_true`, `test_main_wires_all_features`, `test_ac_033_same_sessions_table_as_authentication`, `test_authentication_enforcement_wiring`.

**Change diff at this point** (`git diff --stat ab4b4f8 HEAD`): `src/main.py` `10 +-` (8 insertions, 2 deletions), `tests/acceptance/permissions/test_composition_wiring.py` `+105`, `docs/verification/session-lookup-unwired.md`. One source file — consistent with the §7 light-tier criterion.

**Phase 5 gate: PASS (light tier).** Reproduction test GREEN, covering tests GREEN (EDGE-007 / INV-002 fail-closed intact), smoke GREEN, ruff clean repo-wide, mypy clean. Deferred by design: the full regression suite (S6.4 pre-merge gate). Remaining Phase 5 steps: **S5.3** traceability row (Q-02), **S5.4** verification report / spec-coverage statement for the issue's affected IDs.

---

## Phase 5 report (S5.3 + S5.4)

**Change type: ISSUE, light tier** (§7 qualification; AGENTS.md "Light ISSUE tier"). Combined execution (recorded per the task-definition): S5.3 (traceability) and S5.4 (verification report) are the two record-writing steps of Phase 5 and share one execution; **no implementation, test or spec file was touched** — the only writes are the traceability row and this section.

### S5.3 — traceability matrix updated

`docs/verification/traceability.md`: new section **"Issue: session-lookup-unwired (composition-root session lookup — S5.3, 2026-10-04)"** with one evidence row:

> `| permissions (composition root, src/main.py) | REQ-017 | AC-020 | test_ac_020_composition_root_validates_session_token (new, tests/acceptance/permissions/test_composition_wiring.py — import main in a fresh interpreter, then main._permission_service.has_permission(alice.id, "usermanagement.get_user", session_token=…) → [True, False, False, False]: valid token proceeds, revoked / another user's / unknown still deny) | GREEN (session-lookup-unwired S5.3, 2026-10-04, commit f85deba) |`

Why a **new row** and not an added reference in the existing REQ-017 / AC-020 / AC-021 / EDGE-007 rows: those rows are the **service-level** record written by the change that observed them (convention B, Q-129), and their tests inject a **fake** lookup (`tests/acceptance/permissions/test_check_api.py:398`, `:459`, `:494`) — which is exactly why the composition root was uncovered. Refreshing them would erase that record and would still leave the composition-root coverage uncited. **No existing row was rewritten or refreshed**, and the spec's own §11 `PENDING` rows for REQ-017/AC-020 and REQ-017/AC-021 (`docs/specs/user-roles-permissions.md:786-787`) stay untouched — **decision Q-02**: no Spec Amendment, no Changelog entry; only `docs/verification/traceability.md` gains the evidence row.

**Referential-integrity gate (the CI `traceability` job):** `uv run python scripts/check_traceability.py` → **`Traceability: PASS (747 matrix rows, 129 spec IDs, 714 test functions)`**, exit `0` — the new row's IDs are defined in `docs/specs/`, its cited test function exists under `tests/`, and its Status cell uses a declared value.

### S5.4 — verification report (spec coverage for the affected IDs = 100%)

**Affected IDs** — all from the existing approved spec **`docs/specs/user-roles-permissions.md`** (§2); this ISSUE has no spec of its own:

| ID | Required behaviour | GREEN test(s) (named) | Evidence |
|---|---|---|---|
| **REQ-017** | a provided session token is validated via the session lookup; unknown / revoked / expired / mismatched → deny | `test_ac_020_composition_root_validates_session_token` (`tests/acceptance/permissions/test_composition_wiring.py`, **composition root**, new); `test_session_validation_in_check` (`tests/acceptance/permissions/test_check_api.py:351`); `test_revoked_expired_token_denied` (`tests/unit/permissions/test_edge_cases.py:232`); `test_mismatched_token_denied` (`:272`); `test_undeterminable_never_true` (`tests/property/permissions/test_invariants.py:297`, INV-002) | S5.1 gates 1 + 2 (`1 passed`, `64 passed`) |
| **AC-020** | valid session token → the check **proceeds**; revoked → `False`; another user's token → `False` | `test_ac_020_composition_root_validates_session_token` — the only test that reaches AC-020's positive branch **in the composed application** (`[True, False, False, False]`); plus the service-level `test_session_validation_in_check` | S5.1 gate 1 (`1 passed in 1.33s`); RED at S3.2 (`1 failed`) → GREEN at S4.2 (`1 passed`) |
| **AC-021** | `session_token=None` → validation skipped, evaluation proceeds | `test_session_validation_skipped_when_token_none` (`tests/acceptance/permissions/test_check_api.py:433`) | S5.1 gate 2 (`64 passed`) — unchanged by the fix, re-run GREEN, row not refreshed |
| **EDGE-007** | lookup unavailable (`None` or raising) → deny (`storage_error`) | `test_unavailable_session_lookup_denied` (`tests/unit/permissions/test_edge_cases.py:307`); supporting: `test_lookup_raises_denied` (`:383`), `test_storage_error_denied_fail_closed` (`test_check_api.py:264`), INV-002 `test_undeterminable_never_true` | S5.1 gate 2 (`64 passed`) — the fail-closed branches (`src/backend/permissions/service.py:407-408`, `:412-413`) are untouched by the diff |

**Spec coverage for the affected IDs = 100%** — **4/4** (REQ-017, AC-020, AC-021, EDGE-007) each have at least one GREEN test; REQ-017 and AC-020 additionally have a test that exercises the real composition root, which is the coverage the defect was missing. (Full-spec coverage of `user-roles-permissions.md` is not this change's gate — an ISSUE verifies its affected IDs, not the whole spec; the spec's own §11 matrix stays as the historical record per Q-02.)

**No test was weakened, changed or deleted.** `git diff --stat ab4b4f8 HEAD -- tests/ src/` → `src/main.py 10 +-` and `tests/acceptance/permissions/test_composition_wiring.py +105` (the new reproduction test, added at S3.1 and byte-identical since); **no pre-existing test file appears in the diff**. The reproduction test flipped from `1 failed` (S3.2) to `1 passed` (S4.2) on the source change alone, and its three negative guards (revoked / another user's / unknown token) are GREEN before and after — the fix is not a blanket allow.

**Check summary (Phase 5, light tier).**

| Check | Result |
|---|---|
| Reproduction test GREEN (AC-020 / REQ-017) | **PASS** — `1 passed` |
| Covering tests + affected feature directories | **PASS** — `64 passed` (permissions acceptance/unit/property) |
| Smoke (composition-root wiring + session-management + authentication) | **PASS** — `126 passed` |
| Lint, whole repo (`uv run ruff check .`, matches CI) | **PASS** — `All checks passed!` |
| Types (`uv run mypy src/`) | **PASS** — `Success: no issues found in 83 source files` |
| Traceability referential integrity (`uv run python scripts/check_traceability.py`) | **PASS** — exit `0`, `747 matrix rows` |
| Full regression suite | **Deferred by design to the Phase 6 pre-merge gate (S6.4)** — light tier; must pass there and the result is recorded in the review report (the change is in the composition root, so the full suite is the real safety net) |
| `verify_spec.py` | n/a — FEATURE/CROSS-CUTTING only (this change has no spec file) |

**Phase 5 gate: PASS (final, light tier).** Every affected ID has GREEN evidence, the traceability matrix carries the composition-root row, lint and types are clean, and no test was weakened. Phase 5 is closed; the change may enter **Phase 6 (S6.1 review)**, with the full regression suite as the S6.4 pre-merge gate and a `patch` version bump (AGENTS.md Versioning: `ISSUE → patch`).

---

## Phase 6 review (S6.1–S6.3, 2026-10-04)

**Combined execution (recorded per the task-definition):** S6.1 (review vs. normative basis) + S6.2 (traceability + boundaries) + S6.3 (review report) in one bounded review pass. Inputs: the approved spec `docs/specs/user-roles-permissions.md` (REQ-017 `:513`, AC-020 `:552`, AC-021 `:553`, EDGE-007 `:597`, INV-002 `:581`, Impact Analysis `:827`), this triage record + the Phase 3/4/5 evidence, and the **FINAL code state** (`git diff main...HEAD -- src tests`, then the final files read directly). Per the bounded-scope rule (P-27) the full test suite and the Phase 5 gates were **not** re-run — Phase 5 closed them PASS (light tier). The full regression suite stays deferred to the **S6.4 pre-merge gate** and its result must be recorded there.

**Change diff under review** (`git diff --name-status main...HEAD`) — exactly four files, matching the §6 fix scope with nothing extra:

| File | Status |
|---|---|
| `src/main.py` | `M` — the only source file (`10 +-`: 2 moved lines, 1 keyword, 4 comment lines) |
| `tests/acceptance/permissions/test_composition_wiring.py` | `A` — the only test file (`+105`) |
| `docs/verification/session-lookup-unwired.md` | `A` — this record |
| `docs/verification/traceability.md` | `M` — the S5.3 evidence row |

`git diff --name-only main...HEAD -- docs/specs` → **0 files**: no approved spec was edited, so the Spec Amendment Workflow is not triggered.

### S6.1 — review vs. the normative basis (ISSUE)

**1. No behavior beyond the affected spec IDs — PASS.** The fix supplies the dependency the spec already requires at `:827` ("the session repository (`get_by_token_hash`) **is used by the check**") through the parameter the public constructor already declares (`src/backend/permissions/service.py:134`, `session_lookup: SessionLookup | None = None`). Verified in the final state: `src/main.py:157` `session_lookup=_session_repository,  # validates a provided session token (REQ-017, AC-020)`. No signature change, no new type, no new module, no new dependency (`SqliteSessionRepository` was already imported and used), no new public interface, no CLI/API surface. The resulting behaviour **is** REQ-017 / AC-020: the composed check now reaches the positive branch (`[True, False, False, False]`), and AC-021's skip-on-`None` path is untouched (`_validate_session` returns `None` immediately when `session_token is None`).

**2. Fail-closed invariant (EDGE-007 / INV-002) intact — PASS.** `git diff main...HEAD -- src/backend` is **empty**: not one line of the permissions feature changed. Read of the final `src/backend/permissions/service.py:_validate_session` confirms both fail-closed branches are verbatim: `if self._session_lookup is None: return "storage_error"  # Unavailable lookup: fail-closed (EDGE-007).` and `except Exception: return "storage_error"  # Raising lookup: fail-closed (EDGE-007).` The negative branches (`invalid_session` for unknown/revoked/expired, `session_principal_mismatch` for another user's session) are likewise unchanged. Supplying a lookup in the composition root cannot turn a storage failure into an allow — INV-002 (`:581`) holds structurally, and its property test `test_undeterminable_never_true` was re-run GREEN at S5.1.

**3. Reproduction tests GREEN — PASS (per the Phase 5 record, not re-run here).** `test_ac_020_composition_root_validates_session_token`: RED at S3.2 (`1 failed`, `AssertionError: [False, False, False, False]`, denial reason `storage_error` in the subprocess log — a failure **on behaviour**, no fixture/`ValidationError`) → GREEN at S4.2 and S5.1 (`1 passed in 1.33s`). EDGE-007 / INV-002 fail-closed tests re-run GREEN (`64 passed` across the three permissions test directories).

**4. Composition-root correctness — PASS.** Read of the final `src/main.py` (the only reordered code):
- **Ordering:** `_AUTH_DB` / `_session_repository` are now at `:143-144`, i.e. constructed **before** their first use at `:157`, and before `_permission_service` at `:152`. The old location (below `AuthService`) is removed, so there is exactly one `_session_repository` object — `AuthService` (`:185-193`), `SessionService` (`:201-205`) and the search source (`build_session_source(_session_repository)`, `:218`) all still receive the **same instance** over the same `_AUTH_DB`. No duplicate engine, no second store.
- **Cycle avoidance untouched:** `_permission_service_proxy` / `_user_manager_proxy` are still created at `:129-130`, before the settings registry (`:136-137`); `PermissionService` still receives `_user_manager_proxy`, not the real manager; `_permission_service_proxy.set_service(...)` still runs before the settings registration; `_user_manager_proxy.set_manager(_user_manager)` still runs after `UserManager` is built (`:181-182`). The two real cycles (PermissionService↔UserManager, PermissionService↔settings registry) are broken exactly as before, and the diff adds **no third proxy** — correct, because `SqliteSessionRepository.__init__` (read in the final state, `src/backend/authentication/repository.py:70-81`) touches only its database URL (mkdir parent → `create_engine` → `SQLModel.metadata.create_all`): no settings read, no permission check, no other service. Constructing it earlier therefore has no side effect on the rest of the root, including on `set_system_permissions(...)` which still runs after the service is built.
- **No other dependency silently defaulted:** the constructor takes 8 dependencies; the final call site supplies all 8 — `SqliteRoleRepository` / `SqliteGrantRepository` / `SqliteSystemPrincipalRepository` (positional), `_user_manager_proxy`, `session_lookup`, `catalog`, `event_bus`, `settings_registry`. `session_lookup` was the only gap (triage C-5), and it is now closed.
- **Q-01 / C-5 scope decision respected:** `grep -rn "PermissionService(" src` finds exactly two construction sites — `src/main.py:152` (now wired) and the module-singleton fallback inside `get_permission_service()` (`src/backend/permissions/service.py:508`), which **still omits `session_lookup`** as the triage decided (no caller in `src/`; used only by `tests/integration/permissions/test_persistence.py`). The change did not creep into it.

**5. Tests not weakened — PASS.** `git diff --name-status main...HEAD -- tests` → **`A` only** (`tests/acceptance/permissions/test_composition_wiring.py`): no existing test file was modified, weakened or deleted anywhere in the repo. The new test asserts **both directions** in one call list — the positive guard (valid, unrevoked, unexpired token for the acting user → `True`) **and** three negative guards (revoked → `False`, another user's token → `False`, unknown token → `False`), asserted as the exact tuple `[True, False, False, False]`, so a blanket allow cannot pass. Its fixture data is valid and in-domain (real `User`/`Session` rows written through the composed stores, the SHA-256 hash the check itself computes, a key present in the closed catalog), and it is hermetic: `cwd=tmp_path` keeps the relative SQLite URLs and the `settings/` dir inside the temp dir, and `_SRC` is derived from `Path(__file__).resolve().parents[3]` — `grep -n "C:/workspace" <file>` → no match, so no hard-coded worktree path.

### S6.2 — traceability + boundaries

**Traceability — PASS.** `docs/verification/traceability.md` gained the section *"Issue: session-lookup-unwired (composition-root session lookup — S5.3, 2026-10-04)"* with one row: `permissions (composition root, src/main.py) | REQ-017 | AC-020 | test_ac_020_composition_root_validates_session_token | GREEN (session-lookup-unwired S5.3, 2026-10-04, commit f85deba)`. The cited test function **exists** (`tests/acceptance/permissions/test_composition_wiring.py`, the only test that reaches AC-020's positive branch through the real composition root), so the row is not orphaned, and the REQ→AC→test chain for every affected ID is complete (S5.4 table: REQ-017, AC-020, AC-021, EDGE-007 = 4/4 GREEN, spec coverage for the affected IDs 100%). Writing a **new** row rather than refreshing the service-level rows is correct per convention B / Q-129 (a row records the gate as observed by the change that wrote it; the existing rows' tests inject a fake lookup, which is precisely the uncovered gap), and the spec's own §11 `PENDING` rows stay untouched per decision Q-02 — no Spec Amendment. Referential-integrity gate re-run in this step (cheap, read-only): `uv run python scripts/check_traceability.py` → **`Traceability: PASS (747 matrix rows, 129 spec IDs, 714 test functions)`**, exit `0`.

**Feature boundaries & architecture rules — PASS.**
- `git diff main...HEAD -- src/backend` is empty: **no feature module was touched**. The composition root is the shared wiring layer, so a wiring defect belongs exactly there.
- `src/main.py` imports **only public feature interfaces** — `SqliteSessionRepository` comes from `backend.authentication` (it is in that package's `__all__`), as do `AuthService`, `SqlitePasswordResetRepository`, `SqliteWebAuthnCredentialRepository`, `SqliteUserRepository`, `UserManager`, `SessionService` and the permissions repositories. `git diff main...HEAD -- src/main.py` shows **no import added, moved or removed by this change** — the session repository was already imported for `AuthService`. No private (`_`-prefixed) module import was introduced.
- Dependency direction stays clean: `grep -rn "from backend\." src/backend/permissions/` (excluding its own package) → **no cross-feature import**. The permissions feature depends only on the structural `SessionLookup` protocol (`src/backend/permissions/models.py:78-81`); `SqliteSessionRepository.get_by_token_hash(token_hash) -> Session | None` (`src/backend/authentication/repository.py:92`) satisfies it structurally, and the store is passed **as a value** at the composition root — permissions never imports authentication. This is the ADR-073 seam used as specified, not a new pattern.
- `model/` / `services/` / `shared/` rules: nothing moved or added; no new directory, no new layer, and no abstraction invented — the fix deliberately did **not** add a third lazy proxy (§6), which would have been the larger, wrong solution.
- Architecture test directory: `tests/architecture/` does **not exist** in this repository (the test tree is `acceptance / integration / contract / property / unit`), so the architecture rules cannot be machine-checked here — pre-existing repo state, recorded as **F-4** (informational, out of this ISSUE's scope); the rules were verified by inspection as above.

**Observability — PASS (unchanged).** The path the fix activates is already observable: `SqliteSessionRepository` is traced with `@logged_class(slow_threshold_ms=100, include_args=False)` (token hashes never in a record), `PermissionService` with `@logged_class(include_args=False)` (the session token never in a record, REQ-028/NFR-002), and every denial is logged at WARNING with its reason by `_deny` — the S3.2 RED evidence shows exactly those `reason=storage_error` records, which is what made the defect diagnosable. The diff adds no logging and removes none.

### Findings and resolutions

| # | Severity | Finding | Resolution |
|---|---|---|---|
| F-1 | Minor / observation | The composition-root test asserts the boolean **outcomes**, not the denial **reason strings** (`invalid_session`, `session_principal_mismatch`) that AC-020's "And" clauses name. | **Accepted.** The test's contract is the *wiring* — does the composed service consult the lookup at all. The reason strings are asserted at the service level by `tests/unit/permissions/test_edge_cases.py::test_revoked_expired_token_denied`, `::test_mismatched_token_denied` and `tests/acceptance/permissions/test_check_api.py::test_session_validation_in_check` (all re-run GREEN at S5.1, none modified). Re-asserting reasons through subprocess stdout would duplicate that coverage for no added guard, and the exact-tuple assertion already rules out a blanket allow. |
| F-2 | Minor / observation | The module-singleton fallback `get_permission_service()` (`src/backend/permissions/service.py:508`) still constructs `PermissionService` **without** `session_lookup`, so a caller of that fallback would still deny every token-bearing check. | **Accepted — deliberate scope boundary, not an open finding.** The triage (C-5, §6 "Explicitly out of scope", TODO out-of-scope list) excluded it: it has **no caller in `src/`** and is used only by `tests/integration/permissions/test_persistence.py`; wiring it would add behaviour nobody calls (YAGNI). Re-verified in the final state that this change did **not** silently widen into it. Pointer for the future: if a change gives the fallback a production caller, that change must wire the lookup too. |
| F-3 | Minor / observation | The new test reads the composition root's private module globals (`main._permission_service`, `main._user_repository`, `main._session_repository`). | **Accepted.** `src/main.py` is a script-style composition root with no public API, and this is the **established** pattern for testing it (`tests/acceptance/settings_coverage/test_wiring.py` does the same). Adding a public accessor purely for a test would be new, unspecified API. |
| F-4 | Informational | `tests/architecture/` (named in AGENTS.md Phase 5 REFACTOR) does not exist in this repo, so the architecture rules are not machine-checkable. | **Out of scope for this ISSUE** (pre-existing repo state; this change adds no architecture element). Rules verified by inspection (S6.2). Flagged for a future DOCS/CHORE or REFACTOR change, not for this PR. |

**No open findings.** Every finding is resolved or explicitly accepted with its rationale.

**AGENTS.md "how to use this" note (S6.3 item 9): skipped, with rationale.** The change adds no reusable shared capability — it repairs one missing argument in the existing composition-root wiring; the permissions feature's public interface, the `SessionLookup` seam (ADR-073) and the composition-root pattern are pre-existing and already documented (AGENTS.md "Using the … Feature" sections). The reusable knowledge this change produces is a *test* fact, and it is recorded where future changes will find it: the new test module's docstring (why no existing permissions test could see the defect, and the `import main` subprocess pattern to reuse) plus this record.

### Verdict

**REVIEW: CLEAN.** The fix is minimal (one source file: one keyword + a two-line move); it restores exactly the REQ-017 / AC-020 behaviour the approved spec already requires at `:827`; it introduces no behaviour beyond the affected spec IDs; it leaves the fail-closed invariant (EDGE-007 / INV-002) byte-for-byte untouched (`git diff main...HEAD -- src/backend` empty); it keeps the composition root's deliberate cycle-avoidance and single-instance sharing intact and wires no other dependency by accident (all 8 constructor dependencies supplied, the `get_permission_service()` fallback left unwired per Q-01/C-5); it adds the first composition-root-level GREEN test for AC-020 with a positive **and** three negative guards; it modifies, weakens or deletes **no** test; and the traceability chain is complete and referentially valid (`check_traceability.py` exit `0`).

**Phase 6 gate: PASS (S6.1–S6.3).** Next: **S6.4** — run the **full regression suite** (the light-tier pre-merge gate; it must pass and its result must be recorded in this file, since the change is in the composition root), bump the version `patch` (`pyproject.toml:4`, `0.6.0` → `0.6.1`, `bump-my-version bump patch` with a clean tree), and open the PR to `main` for human review/merge — the agent must not merge it.

---

## Phase 6 pre-merge gate (S6.4, 2026-10-04)

The light-tier deferral (§7, Phase 5) is discharged here: the **full regression suite** is the Phase 6 pre-merge gate and must pass before the version bump and the PR.

| Gate | Command | Result |
|---|---|---|
| **Full regression suite (pre-merge gate)** | `uv run pytest tests/ -q` (change worktree, `issue/session-lookup-unwired` @ `8a67bc3`) | **`728 passed, 1 skipped in 202.11s (0:03:22)`** — **0 failed, 0 errors** |

**Skip is pre-existing and environmental, not a regression:** `SKIPPED [1] tests\acceptance\filemanagement\test_filemanagement.py:364: symlinks not available on this host` — the same single skip recorded by every prior full-suite run (e.g. `docs/verification/traceability.md:420`, `hanging-observability-test` Phase 5).

**Delta vs. the `main` baseline (regression check):** the most recent full-suite baseline on `main` is **`727 passed, 1 skipped`** (search S5.1 re-run on base `e8dd2bc`, 2026-10-02, commit `7bbc05a`; cited at `docs/verification/traceability.md:420` and in the Search Matrix). This branch: **`728 passed, 1 skipped`** — exactly **+1 test, +0 failures, +0 skips**, and the +1 is this change's new reproduction test `test_ac_020_composition_root_validates_session_token`. No pre-existing test changed status, none was weakened or deleted, and nothing regressed — the composition-root reordering is safe across the whole suite.

**Gate: PASS.** Full regression GREEN → the version bump (`patch`, `0.6.0` → `0.6.1`, per AGENTS.md Versioning `ISSUE → patch`) and the PR to `main` follow in this same step. The PR is opened for human review/merge; the agent does not merge it (human governance).
