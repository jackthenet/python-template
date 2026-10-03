# Questions: session-lookup-unwired

One question file per change, created at **P.1 Frame** from the template.

- **Change:** session-lookup-unwired (ISSUE)
- **TODO file:** `docs/todo/session-lookup-unwired.md`
- **Spec:** n/a (defect against `docs/specs/user-roles-permissions.md`)
- **Opened:** 2026-10-03
- **Status:** OPEN  <!-- OPEN | ALL ANSWERED -->  <!-- 2 PENDING: Q-01, Q-02 (added by the P.2 second pass) -->
- **Answer rounds:** 0

## Preparation questions (P.2)

**First pass recorded 0 questions; the second P.2 pass (full parameter coverage + governance sweep, below) found 2 that evidence cannot settle (Q-01, Q-02).** The defect itself is confirmed against approved spec IDs, and the fix restores specified behaviour without touching any public signature, protocol or spec *behaviour* wording: no new dependency, no new public interface, no new behaviour beyond the affected IDs. What evidence does **not** settle is (a) whether the second, caller-less `PermissionService` construction site is in scope, and (b) whether the `PENDING` rows inside the **approved spec's own** §11 matrix get closed by this change (that would edit an approved spec → Spec Amendment Workflow). Everything else is closed from the code — see §Closed points (C-1…C-6) and §P.2 second pass (E-1…E-9). The two P.1 context points are closed below.

- **Step:** P.2 Interrogate
- **Status:** OPEN — 2 questions PENDING (Q-01, Q-02); all other interrogation points CLOSED from evidence
- **Incorporated:** yes (defect confirmation, closed points, reproduction plan, light-tier, overlap check); Q-01/Q-02 pending the user

### Defect confirmation (ISSUE triage, spec `docs/specs/user-roles-permissions.md`)

| ID | Spec line | Required behaviour |
|---|---|---|
| REQ-017 | `:513` | When `session_token` is provided, the check **validates the session via the session lookup**: unknown/revoked/expired → `invalid_session`; another user's session → `session_principal_mismatch`; omitted token → skipped. |
| AC-020 | `:552` | A valid, unrevoked, unexpired session token for `u` → the session is validated and the check **proceeds** with the user/role evaluation (revoked → `invalid_session`, other user's token → `session_principal_mismatch`). |
| AC-021 | `:553` | `session_token=None` → validation skipped, evaluation proceeds. |
| EDGE-007 | `:597` | A check with a token when the session lookup is **unavailable (None or raises)** → deny `storage_error`. |
| Impact Analysis | `:827` | "**The session repository (`get_by_token_hash`) is used by the check for session validation (REQ-017)**" — the spec asserts the wiring exists in the composed application. |

**Observed vs required (one paragraph).** In the composed application the session lookup is never provided: `src/main.py:145-153` constructs `PermissionService(SqliteRoleRepository, SqliteGrantRepository, SqliteSystemPrincipalRepository, _user_manager_proxy, catalog=…, event_bus=…, settings_registry=…)` with **no `session_lookup=` argument**, so `self._session_lookup` stays `None` (`src/backend/permissions/service.py:143`) and `_validate_session` returns `"storage_error"` for every non-`None` token (`:407-408`) before the catalog and grant steps run (`:368`, i.e. after the user lookup, per EDGE-024). `rg -n "session_lookup\s*=" src tests` finds the argument **only** in tests (`tests/acceptance/permissions/test_check_api.py`, `tests/unit/permissions/test_edge_cases.py`, `tests/property/permissions/test_invariants.py`) — no production call site. The path is reachable in production: `@requires_permission` forwards `principal.session_token` to the checker (`src/backend/shared/principal.py:74`), and `Principal.session_token` is a specified field (`:32`). So **observed**: any check carrying a session token in the composed app denies with `storage_error`; **required** (REQ-017 / AC-020 / `:827`): the check validates the token against the session repository and proceeds when it is valid. EDGE-007 is *not* the specified state here — EDGE-007 covers a lookup that is genuinely unavailable or raising, not a composition root that never supplies one. Current latency: no in-repo caller constructs a `Principal` with a token (every `Principal(` in `src/` is the system principal), so the defect is latent-but-live at the public API (`has_permission(..., session_token=…)`, `Principal(session_token=…)`), and the future HTTP/api-keys surface would inherit a check path that cannot validate sessions.

**Traceability status (recorded, both matrices).** `docs/specs/user-roles-permissions.md:786-787` records REQ-017/AC-020 and REQ-017/AC-021 as **PENDING**; `docs/verification/traceability.md:680-681` records the same two rows as **GREEN** via `test_session_validation_in_check` / `test_session_validation_skipped_when_token_none`. Both are historical gate records (decision Q-129, convention B) and neither is wrong for what it observed: the GREEN test injects a **fake** lookup (`tests/acceptance/permissions/test_check_api.py:385,449,484` define `get_by_token_hash` stubs), so AC-020 is covered at the service level and **uncovered at the composition root** — which is exactly the gap this ISSUE reproduces. No matrix row is refreshed by the triage beyond adding the reproduction test (Phase 3 obligation).

### Closed points (evidence, no user input needed)

- **C-1 — the lookup object.** `SessionLookup` is a one-method structural protocol: `def get_by_token_hash(self, token_hash: str) -> SessionRecord | None` (`src/backend/permissions/models.py:78-81`), where `SessionRecord` needs `user_id: UUID`, `expires_at: datetime`, `revoked: bool` (`:69-74`). `SqliteSessionRepository.get_by_token_hash(self, token_hash: str) -> Session | None` (`src/backend/authentication/repository.py:92-94`) satisfies it: `Session` has `user_id` (`src/backend/authentication/models.py:54`), `expires_at` (`:57`), `revoked` (`:58`). Two compatibility details verified, not assumed: (a) `_attach_utc` (`src/backend/authentication/repository.py:37-49`) re-attaches `UTC` to the naive datetimes SQLite materializes, so the `record.expires_at < datetime.now(UTC)` comparison at `src/backend/permissions/service.py:414` cannot raise `TypeError`; (b) the permissions hash `hashlib.sha256(token.encode("utf-8")).hexdigest()` (`service.py:409`) is byte-identical to authentication's `hash_token` (`src/backend/authentication/tokens.py:32`), so a token issued by `AuthService.login` resolves through the permissions check. The session feature owns no repository of its own — `SessionService` uses the reused authentication store (`src/main.py:196`, `tests/acceptance/sessionmanagement/test_store_reuse.py::test_ac_033_same_sessions_table_as_authentication`), so the same object is the right lookup.
- **C-2 — startup ordering (the P.1 open question).** The session repository is constructed **after** the permission service: `_AUTH_DB` at `src/main.py:177`, `_session_repository = SqliteSessionRepository(_AUTH_DB)` at `:178`, versus `_permission_service` at `:145`. **No lazy proxy is needed**: `SqliteSessionRepository.__init__(database_url: str)` (`src/backend/authentication/repository.py:71-82`) depends on nothing but the URL (it mkdirs the parent, creates the engine, `SQLModel.metadata.create_all`) — there is no cycle, so the `_LazyUserManager` / `_LazyPermissionService` proxies (`src/main.py:90-126`, which exist only for the two real cycles: PermissionService↔UserManager and PermissionService↔settings registry) would be a **larger** solution than the problem. The smaller fix is a two-line move: relocate `src/main.py:177-178` above `_PERMISSION_DB` (`:144`) and pass the object. Nothing depends on the current order (`rg -n "_session_repository|_AUTH_DB" tests` → only `tests/integration/authentication/test_sqlite_repositories.py`, which builds its own repo).
- **C-3 — the exact wiring change (the whole fix).** In `src/main.py`: move `_AUTH_DB = "sqlite:///./data/authentication.db"` (`:177`) and `_session_repository = SqliteSessionRepository(_AUTH_DB)` (`:178`) to just above `_PERMISSION_DB` (`:144`), and add `session_lookup=_session_repository,` to the `PermissionService(...)` call (`:145-153`). Net: **1 file, 2 lines moved + 1 keyword added.** `session_lookup` is already the 5th parameter of the public constructor (`src/backend/permissions/service.py:134`) — no signature change, no new type, no new module.
- **C-4 — different DB file is fine (recorded).** `_PERMISSION_DB = "sqlite:///./data/permissions.db"` (`src/main.py:144`) vs `_AUTH_DB = "sqlite:///./data/authentication.db"` (`:177`). The lookup is a separate object over a separate store; the permission repositories never read the sessions table. No change.
- **C-5 — nothing else on that construction path is defaulted.** The same call passes `catalog=_catalog` (`:149`), `event_bus=get_event_bus()` (`:150`), `settings_registry=_settings_registry` (`:151`) — all wired, only `session_lookup` is missing. The only other `PermissionService(` in `src/` is inside `get_permission_service()` (`src/backend/permissions/service.py:497-514`), the module-singleton fallback, which also omits `session_lookup`; it has **no caller in `src/`** (`rg -n "get_permission_service\(\)" src` → the definition only) and is used solely by `tests/integration/permissions/test_persistence.py`. **Out of scope** (no production path; wiring it would be behaviour nobody calls — YAGNI), recorded so the triage is complete.
- **C-6 — EDGE-007 stays as specified.** The fail-closed branches (`service.py:407-408` for `None`, `:412-413` for a raising lookup) are untouched; supplying a lookup in the composition root does not turn a storage failure into an allow. Their tests (`tests/unit/permissions/test_edge_cases.py::test_unavailable_session_lookup_denied`, spec `:735`) must stay GREEN.

### Reproduction plan (Phase 3)

**Target:** new file `tests/acceptance/permissions/test_composition_wiring.py`, function `test_ac_020_composition_root_validates_session_token` (AC-020 / REQ-017). It must exercise the **real composition root**, because every existing permissions test builds its own `PermissionService` and cannot see the missing wiring.

**Pattern to reuse (established, do not invent one):** `tests/acceptance/settings_coverage/test_wiring.py::test_main_wires_all_features` (`:12-31`) already executes the composition root — it runs `sys.path.insert(0, 'src')`, replaces the settings-registry singleton (`_reg_mod._registry[0] = SettingsRegistry(value_repository=YamlValueRepository(tempfile.mkdtemp()))`) so nothing leaks into the repo's `settings/` dir, then `import main`, in a `subprocess.run([sys.executable, "-c", code], cwd=…, check=False)` and asserts on stdout. Run it with `cwd=tmp_path` so the relative SQLite URLs (`sqlite:///./data/…`) create their DBs under the temp dir instead of the repo.

**Body (minimal, no enforcement interference):** after `import main` —
1. insert an **admin** user directly through the composed store: `main._user_repository.add(User(username="alice", email="alice@example.com", password_hash="x", roles=["admin"]))` (`src/backend/usermanagement/repository.py:143`, model `models.py:85-105`). Admin avoids the grant step entirely (REQ-010 implicit wildcard, `service.py:379-381`) and avoids the enforced `UserManager` path (`usermanagement.create_user` is **not** in `BOOTSTRAP_SYSTEM_PERMISSIONS`, `models.py:90-101`).
2. insert a session row through the composed session store: `main._session_repository.add(Session(user_id=u.id, token_hash=hashlib.sha256(b"tok").hexdigest(), created_at=now, expires_at=now + 7d, revoked=False))` — the same hash the check computes (`C-1b`).
3. `print(main._permission_service.has_permission(u.id, "usermanagement.get_user", session_token="tok"))`.

**The assertion that fails today:** `assert result.stdout.strip().endswith("True")` — today the composed service returns **`False`** (step 3 of `_check` returns `"storage_error"` at `service.py:407-408` before the catalog/admin-wildcard steps at `:371-381`), so the test is RED on behaviour, not on a `ValidationError` (valid in-domain data throughout: a real `User` row, a real `Session` row, a catalog key that exists in the closed catalog). After the fix the same call returns `True` → GREEN.

**Regression guards in the same test (GREEN before and after — they prove the fix is not a blanket allow):** a second `has_permission(u.id, "usermanagement.get_user", session_token="nope")` → `False` (`invalid_session`), and a token whose session belongs to a different user → `False` (`session_principal_mismatch`). Keep it to one test function plus these two asserts — no fixtures, no new helper module.

### Light-tier check (AGENTS.md "Light ISSUE tier")

**Verdict: QUALIFIES.**
- Single feature area, and the fix touches **1 file** (`src/main.py`) ≤ 3, excluding tests. No feature module is modified — the composition root is shared wiring, not another feature's code.
- No new dependency, no new public interface (`session_lookup` is already a constructor parameter, `service.py:134`), no cross-feature behaviour change (both features' code is untouched; the session store is reused as already specified at `docs/specs/user-roles-permissions.md:827`).
- The affected area is already covered — covering tests to name in the triage: `tests/acceptance/permissions/test_check_api.py::test_session_validation_in_check` (AC-020) and `::test_session_validation_skipped_when_token_none` (AC-021), `tests/unit/permissions/test_edge_cases.py::test_unavailable_session_lookup_denied` (EDGE-007), `tests/property/permissions/test_invariants.py` (fail-closed invariant), `tests/acceptance/settings_coverage/test_wiring.py::test_main_wires_all_features` (the composition-root pattern), `tests/acceptance/sessionmanagement/test_store_reuse.py::test_ac_033_same_sessions_table_as_authentication` (the reused session store).
- Consequence for Phase 5: targeted + smoke = `uv run pytest tests/acceptance/permissions tests/unit/permissions tests/property/permissions tests/acceptance/settings_coverage/test_wiring.py -v` plus `uv run ruff check src/main.py` and `uv run mypy src/`; the **full regression suite runs as the Phase 6 pre-merge gate (S6.4)** and its result goes in the review report. Because the change is in the composition root, the full suite is the real safety net — do not skip it at S6.4.

### Overlap check

- **`docs/todo/` (17 items besides this one):** no in-flight change collides. Two touch `src/main.py` startup wiring — `notifications` (WAITING, `docs/todo/notifications.md:40`) and `api-keys` (WAITING, `docs/todo/api-keys.md:40`) — but neither is IN-WORKFLOW, and `git worktree list` shows **only the primary worktree** (`main` @ `1b19440`), `gh pr list --state open` → **no open PRs**. At most a textual conflict in `src/main.py` if one of them runs concurrently; no semantic conflict.
- **Does this ISSUE pre-decide anything for `api-keys` Q-03? No — explicitly not.** `docs/questions/api-keys.md:104-116` asks which seam turns a raw key into an acting principal (A: api-keys resolves it itself; B: extend `Principal`; C: the key store plugs into permissions' `SessionLookup` seam). This fix supplies the **session repository** as the lookup for **session tokens** — the behaviour REQ-017 and `:827` already require — and changes no signature, no `Principal` field, and no protocol. `session_lookup` remains a single per-instance dependency, so all three api-keys options stay open; if api-keys later picks C it would need its own composite/second lookup, which is api-keys' decision at its own P.3/P.4. Two facts to hand over (enabling, not deciding): (1) `api-keys` Q-06 option C was rejected partly because "it needs the missing `session_lookup` wiring" (`docs/questions/api-keys.md:174,177`) — after this fix that objection no longer holds; (2) the composition root's lookup is the session store, so option C is not free. Nothing in this triage closes or biases Q-03.
- **Other TODOs:** `architecture-tests-missing`, `pyproject-tooling-gaps`, `structlog-logging`, `python-3.15` touch `src/backend/permissions/` or `src/` tooling but not the composition root's session wiring; no ID or spec-section collision.

### P.1 context points — both closed

- The reproduction test must exercise the **real composition root** (`src/main.py`), because every existing test constructs its own `PermissionService` and therefore cannot see the missing wiring. → **Confirmed**, and the reusable pattern exists: `tests/acceptance/settings_coverage/test_wiring.py::test_main_wires_all_features` (subprocess + `import main` + temp settings registry + `cwd=tmp_path`). See "Reproduction plan".
- Whether the session repository is already constructed before `_permission_service`, or needs a lazy proxy, is a P.2/P.4 finding from the code, not a user decision. → **Closed (C-2):** it is constructed later (`src/main.py:177-178` vs `:145`), but it has no dependency cycle, so the fix is a two-line move, **not** a lazy proxy.

### P.2 second pass — points closed from evidence (E-1…E-9)

**E-1 — full constructor-parameter coverage (the "is anything else unwired?" check).** `PermissionService.__init__` (`src/backend/permissions/service.py:128-137`) takes exactly **8** dependencies; the call site is `src/main.py:145-153`. Checked one by one:

| Parameter (`service.py`) | Default | At the `main.py` call site | Verdict |
|---|---|---|---|
| `role_repository: RoleRepository` (`:129`) | required | positional 1 — `SqliteRoleRepository(_PERMISSION_DB)` (`main.py:146`) | wired |
| `grant_repository: GrantRepository` (`:130`) | required | positional 2 — `SqliteGrantRepository(_PERMISSION_DB)` (`:147`) | wired |
| `system_repository: SystemPrincipalRepository` (`:131`) | required | positional 3 — `SqliteSystemPrincipalRepository(_PERMISSION_DB)` (`:148`) | wired |
| `user_manager: UserManager` (`:132`) | required | positional 4 — `_user_manager_proxy` (`:149`) | wired (lazy, real cycle) |
| `session_lookup: SessionLookup \| None = None` (`:134`) | `None` | **absent** | **the defect** |
| `catalog: PermissionCatalog \| None = None` (`:135`) | `PermissionCatalog()` (`:144`) | `catalog=_catalog` (`:150`) | wired |
| `event_bus: EventPublisher \| None = None` (`:136`) | `None` | `event_bus=get_event_bus()` (`:151`) | wired |
| `settings_registry: SettingsRegistry \| None = None` (`:137`) | `None` | `settings_registry=_settings_registry` (`:152`) | wired |

**Exactly one unwired parameter on the specified construction path: `session_lookup`.** No other defaulted parameter is left defaulted, so the fix scope has nothing extra to wire.

> **Correction to the launch-prompt premise (recorded so P.4 does not chase it).** The step brief stated the call site passes `user_lookup=`, `group_lookup=`, `role_lookup=`, `permission_lookup=`. Those parameter names **do not exist in this repository**: `grep -rn "user_lookup=|group_lookup=|role_lookup=|permission_lookup=" src tests --include=*.py` → **no match**, and they are not in `PermissionService.__init__`. The real signature is the 8-parameter one in the table above. The conclusion the brief drew (only `session_lookup` is missing) is correct; only the parameter names were wrong.

**E-2 — no adapter is needed (the `SessionLookup` seam is already satisfied).** Protocol: `def get_by_token_hash(self, token_hash: str) -> SessionRecord | None` (`src/backend/permissions/models.py:78-81`), `SessionRecord` needing `user_id: UUID`, `expires_at: datetime`, `revoked: bool` (`:69-74`). Implementation: `SqliteSessionRepository.get_by_token_hash(self, token_hash: str) -> Session | None` (`src/backend/authentication/repository.py:92`), and `Session` carries all three fields. Structural match, no wrapper, no new module — the fix passes the existing `_session_repository` object.

**E-3 — is a distinct reason code for expired vs. invalid required? No — closed from the spec, not asked.** REQ-017 (`docs/specs/user-roles-permissions.md:513`) already fixes the mapping: "unknown, revoked, **or expired** → deny (`invalid_session`)"; a different user's session → `session_principal_mismatch`. The code implements exactly that (`service.py:414-417`: `record is None or record.revoked or record.expires_at < datetime.now(UTC)` → `invalid_session`). A distinct `expired_session` code would be **new behaviour beyond the approved spec** → out of scope for an ISSUE (it would be a Spec Amendment / FEATURE). Not asked; recorded so a reviewer does not read the single code as an oversight.

**E-4 — reachability today (blast radius at the moment of the fix).** No in-repo caller supplies a session token: every `Principal(` construction in `src/` is the bare system principal (`authentication/service.py:97`, `filemanagement/service.py:79`, `mail/service.py:35`, `search/service.py:50`, `sessionmanagement/service.py:56`, `settings/registry.py:43`, `shared/principal.py:93,95,98`), and `Principal.session_token` defaults to `None` (`shared/principal.py:32`). The forwarding path exists and is specified (`shared/principal.py:74` passes `principal.session_token` to `require_permission`). So: **no live user-visible symptom today**, but the defect is immediately reachable through the public API (`has_permission/require_permission(..., session_token=…)`, `Principal(session_token=…)`) and any HTTP/api-keys surface would inherit a check path that can never validate a session.

**E-5 — no reproduction test exists, and why the suite could not catch it.** `grep -rn "session_lookup" tests/` → the argument appears **only** in `tests/acceptance/permissions/test_check_api.py:33,75,398,459,494`, `tests/unit/permissions/test_edge_cases.py:71,104,252,293,342,487,525`, `tests/property/permissions/test_invariants.py:129,165,207,344` — every one of them builds its **own** `PermissionService` (a local factory helper), so none of them can observe the composition root. The only test that executes `src/main.py` is `tests/acceptance/settings_coverage/test_wiring.py::test_main_wires_all_features` (`:12-31`), and it asserts only on registered settings keys (`:21`) — it never calls a permission check. Hence AC-020's positive branch is GREEN at the service level (fake lookup) and **untested at the composition root**: exactly the gap the new test fills.

**E-6 — regression risk when session validation actually starts running.** Enumerated, not hand-waved:
- **Deny → allow flip is narrow.** Only a check that (a) passes a non-`None` token **and** (b) whose token resolves to an unrevoked, unexpired session **owned by the same `user_id`** changes from `False` to `True` (`service.py:407-408` → `:414-417` then the catalog/admin/grant steps at `:371-385`). Every other token still denies — with a **different reason code**: `storage_error` → `invalid_session` / `session_principal_mismatch`. That reason is externally observable (WARNING log `service.py:421-427` and the `PermissionDenied` event `:430`, REQ-020), so the reproduction test asserts the two negative cases too.
- **No test asserts the unwired state.** The `storage_error` assertions in the permissions tests (`test_check_api.py:303`, `test_edge_cases.py:333,349,409`) all belong to checks with an explicitly injected `None`/raising lookup on a locally built service — unaffected by `main.py`. `tests/acceptance/settings_coverage/test_wiring.py` is the only `import main` test and does not touch checks.
- **EDGE-007 stays intact** (C-6): the fail-closed branches (`:407-408`, `:412-413`) are untouched; supplying a lookup never turns a storage failure into an allow.
- **Startup reorder is safe.** `SqliteSessionRepository.__init__(database_url: str)` (`repository.py:70-81`) depends on nothing but the URL (mkdir parent, engine, `SQLModel.metadata.create_all`); nothing between `main.py:153` and `:178` reads `_session_repository`/`_AUTH_DB`, and its later users (`:182-184`, `:196`, `:212`) only see it earlier. `SqliteSessionRepository` is already imported at `main.py:25`, so no import change.
- **Architecture gate: none to satisfy.** `tests/architecture/` does not exist in this repo (that is the separate `architecture-tests-missing` TODO), so Phase 5 has no architecture suite to run for this change.

**E-7 — version bump (governance, closed by AGENTS.md).** ISSUE → **patch**. `pyproject.toml:4` / `[tool.bumpversion] current_version = "0.6.0"` (`:79-80`) → `bump-my-version bump patch` at **S6.4** (clean tree, `tag = false`), the bump commit part of the PR.

**E-8 — the two traceability matrices are different obligations (this is where Q-02 comes from).** `scripts/check_traceability.py:129` validates **only** `docs/verification/traceability.md` (rows vs. IDs defined in `docs/specs/` vs. test functions that still exist) — it never reads the spec's own §11 table. So:
- **Closed from evidence:** the Phase 5 ISSUE obligation (AGENTS.md Phase 5 item 11) is to add the issue's evidence row to `docs/verification/traceability.md` — a new row for the composition-root test (REQ-017 / AC-020). The existing GREEN rows (`docs/verification/traceability.md:680-681`) are historical gate records (decision Q-129, convention B) and are **not** refreshed.
- **Not closed:** `docs/specs/user-roles-permissions.md:786-787` (inside the approved spec's own `## 11. Traceability Matrix`, header at `:761`) still says `PENDING`. Editing that file is editing an approved spec → the **Spec Amendment Workflow** (own PR, changelog entry). Whether this change carries that touch is a human-governance call → **Q-02**. CI will not fail either way.

**E-9 — reproduction-plan correction (carried to P.4/Phase 3).** The reusable pattern runs the subprocess with `cwd=_REPO_ROOT` (`tests/acceptance/settings_coverage/test_wiring.py:26`), which lets `import main` create `./data/*.db` inside the repository. For this test that is not acceptable — it writes real user/session rows into the repo's stores — so the new test MUST run with `cwd=tmp_path` (the relative SQLite URLs `sqlite:///./data/…` then resolve under the temp dir). Everything else in the pattern (temp settings registry injected into `_reg_mod._registry[0]` before `import main`, stdout assertion) is reused as-is.

## Q-01 — also wire the caller-less singleton fallback `get_permission_service()`?
- **Step:** P.2 Interrogate — Phase P
- **Why needed:** scope decision. There is a **second** `PermissionService(...)` construction in `src/` that also omits `session_lookup`, so the same defect exists there. Whether the ISSUE fixes both sites or only the composition root changes the file count and the light-tier claim.
- **Context:** `get_permission_service()` (`src/backend/permissions/service.py:497-514`) builds a default singleton with the three permissions repositories and no `session_lookup`. `grep -rn "get_permission_service()" src` → the definition only, **no caller in `src/`**; its only users are `tests/integration/permissions/test_persistence.py`. Wiring it would mean the permissions feature constructing an **authentication** repository (a cross-feature import inside a feature, against the boundary rule), or a new lazy/optional seam — i.e. more code than the one-line composition-root fix.
- **Question:** Should this ISSUE wire only the composition root (`src/main.py`, 1 file), or also wire `get_permission_service()`'s fallback (2 files, cross-feature import inside `backend/permissions/`)? Recommended: **A — composition root only** (no production path reaches the fallback; wiring it would be behaviour nobody calls, and it would add a cross-feature import).
- **Answer:** **PENDING**
- **Date:** 2026-10-03
- **Status:** PENDING
- **Incorporated:** no

## Q-02 — close the `PENDING` REQ-017/AC-020 rows inside the approved spec's §11 matrix?
- **Step:** P.2 Interrogate — Phase P
- **Why needed:** governance. The `PENDING` rows are inside an **approved spec file**, and AGENTS.md forbids editing an approved spec outside the Spec Amendment Workflow. The change type does not depend on the answer (ISSUE either way), but the PR content does (one extra spec touch + changelog, or none).
- **Context:** `docs/specs/user-roles-permissions.md:786-787` record REQ-017/AC-020 and REQ-017/AC-021 as `PENDING`; `docs/verification/traceability.md:680-681` record the same pairs as `GREEN` via the fake-lookup tests. CI (`scripts/check_traceability.py:129`) validates only `docs/verification/traceability.md`, so nothing fails either way. AGENTS.md: "A later change adds or updates rows only for the REQs/ACs it actually touches; a dated `RED`/`PENDING` row is a legal record of a past gate."
- **Question:** Does this change close those two spec-internal rows (→ a Spec Amendment touch to `docs/specs/user-roles-permissions.md` §11 + a Changelog entry in the same PR), or leave them as the historical gate record and add only the new evidence row to `docs/verification/traceability.md` at Phase 5? Recommended: **B — leave the spec §11 rows untouched** (convention B; the spec-internal table is the spec's own pre-implementation plan, and a spec edit for a matrix cell would need its own amendment PR for no CI or traceability gain).
- **Answer:** **PENDING**
- **Date:** 2026-10-03
- **Status:** PENDING
- **Incorporated:** no

### Category coverage (ISSUE — no ≥ 20 floor)

| Category | Covered | Where |
|---|---|---|
| Defect mechanism (root cause, not symptom) | yes | Observed-vs-required paragraph; `main.py:145-153` vs `service.py:143,407-408`; E-1 parameter sweep |
| Spec traceability (affected IDs, both matrices) | yes | Defect-confirmation table (`:513,552,553,597,827`); E-8 |
| Reproduction plan (failing test naming a real pattern) | yes | Reproduction plan + E-5 (why the suite missed it) + E-9 (`cwd=tmp_path`) |
| Blast radius / reachability today | yes | E-4 (no token-bearing caller; public API + future HTTP surface) |
| Fix scope (files, adapter needed or not) | yes | C-2, C-3, C-4, E-2 |
| Regression risk | yes | E-6 (deny→allow flip is narrow; reason-code change is observable; no test asserts the unwired state; startup reorder safe) |
| Governance (version bump, traceability, spec amendment, light tier) | yes | E-7, E-8, Q-02, Light-tier check |
| Scope overlap with other in-flight changes | yes | Overlap check (incl. the explicit "does not pre-decide api-keys Q-03") |
| Skipped: configurability / NFR / performance budget | skipped | No new parameter, setting or budget is introduced; the fix passes an existing object to an existing parameter (E-1) |
| Skipped: data model / migration | skipped | No SQLModel table changes → no `alembic revision` (AGENTS.md "Using Migrations") |
| Skipped: security / secret handling | skipped | The token is already hashed before the lookup (`service.py:409`) and `@logged_class` keeps `include_args=False`; the fix adds no logging and no new secret path |
| Skipped: dependency evaluation | skipped | No dependency is added or removed → no ADR/deptry impact |
| Skipped: UX / API surface | skipped | No public signature, endpoint or response shape changes (`session_lookup` is already a constructor parameter, `service.py:134`) |

## Classification verdict

**ISSUE — confirmed, no reclassification.** Per the Change Types table (first matching criterion): the change fixes a deviation from **approved spec behaviour** — REQ-017 (`docs/specs/user-roles-permissions.md:513`) and AC-020 (`:552`) require the check to validate a provided session token, and the Impact Analysis (`:827`) states the session repository's `get_by_token_hash` **is used** by the check; the composed application never supplies the lookup, so the positive branch of AC-020 is unachievable outside tests. No new capability is introduced, so FEATURE does not match first. Not CROSS-CUTTING: the change is one wiring line in the composition root; it intentionally spans no feature's behaviour (the session store is reused exactly as `:827` already specifies). Not REFACTOR/DOCS-CHORE: externally observable behaviour changes (a previously always-denied check can now allow).

**Spec amendment: NOT required for the behaviour.** The behaviour to be restored is already specified (`:513`, `:552`, `:827`); EDGE-007 (`:597`) covers a genuinely unavailable/raising lookup, not a composition root that never provides one, so there is no spec silence to fill. The **only** candidate spec edit is the §11 matrix cell (`:786-787`) — a record-keeping touch, not a behaviour amendment → **Q-02**, and if the user chooses to close it, it rides the change PR as a Spec Amendment touch with a Changelog entry, without changing the classification.

## Recommendation

**Minimal fix (the whole change):** in `src/main.py`, move `_AUTH_DB` (`:177`) and `_session_repository = SqliteSessionRepository(_AUTH_DB)` (`:178`) above `_PERMISSION_DB` (`:144`) and add `session_lookup=_session_repository,` to the `PermissionService(...)` call (`:145-153`). **1 file, 2 lines moved + 1 keyword** — no new type, no adapter (E-2), no lazy proxy (C-2), no signature change, no migration, no dependency.

**Cost:** one new acceptance test (`tests/acceptance/permissions/test_composition_wiring.py::test_ac_020_composition_root_validates_session_token`, plus its two negative asserts) reusing the existing `import main` subprocess pattern with `cwd=tmp_path` (E-9); targeted gate `uv run pytest tests/acceptance/permissions tests/unit/permissions tests/property/permissions tests/acceptance/settings_coverage/test_wiring.py -v` + `uv run ruff check src/main.py` + `uv run mypy src/`; full regression suite as the **S6.4 pre-merge gate** (the composition root is exactly where a targeted run under-tests); `bump-my-version bump patch` at S6.4 (E-7).

**Light ISSUE tier: QUALIFIES** (all four conditions checked in §Light-tier check): single feature area, 1 file ≤ 3 excluding tests, no new dependency or public interface, affected area already covered by the named tests. Caveat to carry into Phase 6: because the change is in the composition root, the full suite at S6.4 is the real safety net — do not skip it.

**Not blocked on anything else:** P.4 can draft the triage record as soon as Q-01 and Q-02 are answered; both answers only adjust scope/PR content, not the defect confirmation or the reproduction plan.

## Late questions (Phases 2–6)

<questions discovered after the change entered the workflow; same entry format, Step field set to the step that found it>
