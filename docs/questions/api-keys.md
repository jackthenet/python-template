# Questions: api-keys

One question file per change, created at **P.1 Frame** from this template and named `<change-name>.md`. It replaces the retired central `AI_Questions.md` (archived at `docs/questions/archive-AI_Questions.md`).

- **Change:** api-keys (FEATURE)
- **TODO file:** `docs/todo/api-keys.md`
- **Spec:** docs/specs/api-keys.md
- **Opened:** 2026-10-03
- **Status:** OPEN  <!-- OPEN | ALL ANSWERED — set OPEN by the orchestrator at P.1; ALL ANSWERED once every question in this file has an answer (the orchestrator records it together with the `QUESTIONS-ANSWERED` TODO advance) -->
- **Answer rounds:** 0

Every question that needs user input is recorded HERE — never in a central file. A step that needs input records **all** of its open questions in one batch and returns `BLOCKED-USER`; the orchestrator presents them (as few `ask_user_question` rounds as possible, <= 4 per round, most blocking first), records the answers here, marks each **ANSWERED** and **incorporated**, and relaunches the step **once** with the full answer set. The change is `WAITING` while its questions are unanswered — the orchestrator works on another change meanwhile, it does not idle.

### Entry format

```markdown
## Q-<n> — <short title>
- **Step:** <P.2 Interrogate, or Sx.x <step name> — Phase <n>>
- **Why needed:** <the ambiguity, missing requirement, or decision>
- **Context:** <what the step had learned at the time>
- **Question:** <the question for the user>
- **Answer:** <the user's answer>  (or **PENDING**)
- **Date:** <YYYY-MM-DD>
- **Status:** PENDING | ANSWERED
- **Incorporated:** no | yes — <where: REQ-XXX / AC-XXX / spec section / decision>
```

## Preparation questions (P.2)

> **Re-scoped on 2026-10-08 (P.3, round 1).** Q-01…Q-04 are answered, and they change the shape of this
> item: the user wants a real HTTP API for the backend (**FastAPI + uvicorn**), authenticated by the
> backend's **own session tokens**, exposing **all 61 enforced catalog actions**, and they approved
> amending `docs/specs/authentication.md` and `docs/specs/session-management.md`, which currently exclude
> an HTTP layer. That boundary is its own change: **`backend-api`** (`docs/todo/backend-api.md`,
> CROSS-CUTTING). This TODO now **depends on `backend-api`** and keeps only the machine-credential half
> (a non-interactive credential + its usage audit). **Q-05…Q-31 stay PENDING** — most of them (scopes,
> prefixes, key caps, audit vocabulary) only exist once the API exists, and several are answered by the
> new change instead.


| ID | Question (one line) | Blocking |
|---|---|---|
| Q-01 | Is the LLM-facing surface an HTTP server, or an in-process tool API + JSON-schema export (no server)? | yes (the central question; decides deps, ADRs, spec amendments) |
| Q-02 | Does the change stay FEATURE, or is it reclassified CROSS-CUTTING now (branch rename, Impact Analysis, `minor`/`major` bump)? | yes (escalation verdict) |
| Q-03 | How does a raw key become a `Principal` — api-keys resolves it, `Principal` gains scopes, or the key store plugs into permissions' `SessionLookup` seam? | yes (escalation verdict) |
| Q-04 | On a key-driven call, which permission is checked — the target action, or an `apikeys.call` wrapper action? | yes |
| Q-05 | Who enforces the key's scopes, and at what single choke point? | yes |
| Q-06 | Bootstrap: with no HTTP layer, how does the first key get created and who is allowed to create one? | yes |
| Q-07 | Storage: a new `api_keys` table in its own SQLite file, or reuse authentication's `sessions` table? | yes |
| Q-08 | Is the usage audit trail api-keys-local, or a shared audit capability every feature writes to? | yes (escalation verdict) |
| Q-09 | How are per-action input schemas derived for "what may this key do?" — signature introspection, a hand-written tool table, or request models on every action? | yes |
| Q-10 | May a key's scopes contain the `<feature>.*` wildcards the grant grammar already allows? | yes |
| Q-11 | Is the effective grant set computed as scopes ∩ owner's roles, and is a scope the owner lacks an error at creation or accepted silently? | yes |
| Q-12 | Do keys die on user deletion / deactivation / password change (the session revocation cascade)? | yes |
| Q-13 | Is expiration optional per key, and what is the default TTL? | yes |
| Q-14 | Is `last_used_at` a stored column written on every call, or derived from the audit table? | yes |
| Q-15 | Key format: reuse `new_token()` verbatim, or add a recognizable `ak_` prefix? | yes |
| Q-16 | May a key or a non-admin user manage (list/revoke) only their own keys, and how is the admin path shaped? | yes |
| Q-17 | Per-user key cap: reject creation, or evict the oldest key (the session-cap precedent)? | yes |
| Q-18 | Are rate limiting / per-key quotas in scope for v1, or explicitly deferred? | yes |
| Q-19 | Which `apikeys.*` catalog actions exist, and what are they named? | yes (escalation verdict) |
| Q-20 | Audit row semantics: exactly one row per call including denials, and which outcome/reason vocabulary? | yes |
| Q-21 | Audit retention and pruning: retention window plus a `cleanup_expired` analogue? | no |
| Q-22 | Does api-keys register a search source (keys and/or the audit log)? | no |
| Q-23 | Which events does api-keys publish, and what do they carry? | no |
| Q-24 | New `ApiKeyError` hierarchy, or plain `ValueError` plus reused authentication errors (the session-management pattern)? | no |
| Q-25 | Confirm the `apikeys.*` settings inventory (keys, kinds, defaults, category, group). | no |
| Q-26 | Confirm the public API surface and representations, including how the raw key is returned exactly once. | yes |
| Q-27 | Thread-safety and write-amplification NFRs for the per-call audit write under concurrent key use. | no |
| Q-28 | Confirm the NFR budgets (resolve + dispatch latency, coverage floor, no weakened tests). | no |
| Q-29 | Confirm the test strategy: which invariants get Hypothesis property tests, and how the no-secret rule is asserted. | no |
| Q-30 | Confirm the migration + `migrations/env.py` + deptry/CI consequences (and which of them only follow from Q-01). | no |
| Q-31 | What is the `Depends on:` relationship to `notifications` (its Q-11 asks exactly this), and the ordering vs `structlog-logging`? | yes (schedule) |

---

### Q-01 — HTTP server, or in-process tool API + schema export?

- **Step:** P.2 (Phase P)
**Answer:** C — FastAPI + uvicorn. The user wants a real API interface: "I want to have an api interface so fastAPI + uvicorn seem to be a good choice." They also approved amending the two specs that exclude an HTTP layer. Consequence: the boundary is re-scoped as the new change `backend-api` (see the re-scope note), which owns it; api-keys becomes a consumer of it.
- **Status:** ANSWERED
- **Date:** 2026-10-08

- **Incorporated:** yes — see the re-scope note at the head of this file

**Context:** The TODO names this the central question. The repo has **no HTTP layer at all**: `grep -rni "fastapi|flask|starlette|uvicorn|aiohttp" pyproject.toml src` returns nothing, and the runtime dependencies (`pyproject.toml:8-24`) are pydantic, loguru, orjson, httpx (client only, unused in `src` — deptry `DEP002` ignore, `pyproject.toml:115`), sqlmodel, argon2-cffi, email-validator, filetype, pillow, ruamel-yaml. Existing specs exclude a server **normatively**: `docs/specs/authentication.md:15` ("Out of scope: … HTTP/REST/GraphQL API layer") and `docs/specs/session-management.md` Constraints ("Backend-only in-process service — no HTTP/REST layer, no frontend").

**Why needed:** It decides whether this change adds a first runtime boundary (new dependency, new ADR, new spec-amendment conversation with two approved specs, deptry/CI/`uv.lock` consequences, a new `src/backend/api/`-style package and its own test category) or stays inside the existing in-process feature model. Every later question (transport auth header parsing, request/response envelopes, status codes) exists only under option B/C.

**Options:**
- **A. In-process tool API + schema export (no server).** api-keys exposes `resolve_key(raw) -> Principal`, a `call(raw_key, action, arguments)` dispatch entry point, and `describe_actions(...)` returning JSON Schemas derived from the real catalog + service signatures. A future server (or an MCP stdio bridge) is a *separate* change that consumes this.
- **B. Stdlib-only HTTP server** (`http.server` / `socketserver`) in a new boundary package — no new dependency, but hand-rolled routing, auth header parsing, JSON envelopes, and a new untested attack surface; no repo precedent for a server test category.
- **C. FastAPI/Starlette + uvicorn** — new runtime dependency, new ADR, amendments to `authentication.md` and `session-management.md` out-of-scope statements, deptry `DEP002` changes, and a large new surface.

**Recommendation:** **A.** It delivers 100% of the TODO's acceptance signal in-process (scoped call allowed/denied, show-once secret, revoke/expiry, one audit row per call, "what may this key do?" with schemas from the real catalog) with **zero new dependencies and zero spec amendments**, and it keeps the server decision reversible: an HTTP or MCP surface becomes a small, later change that only maps requests onto `call()`/`describe_actions()`. Option C additionally requires the user to agree to amend two approved specs, which is a separate governance step, not a P.4 detail.

---

### Q-02 — FEATURE or CROSS-CUTTING?

- **Step:** P.2 (Phase P)
**Answer:** Re-scoped — the change is now `backend-api` (CROSS-CUTTING). The user's answer: "Why is this feature called apikeys shouldn't it simply be the api of the backend?" — accepted. The backend's HTTP boundary is the change; the machine-credential (api-keys) part is deferred to a separate TODO that depends on `backend-api`.
- **Status:** ANSWERED
- **Date:** 2026-10-08

- **Incorporated:** yes — see the re-scope note at the head of this file

**Context:** P.1 classified FEATURE with a note that it is a strong escalation candidate. The Change Types table (#3) makes CROSS-CUTTING the label when a change "intentionally spans two or more features: new shared capability, architecture change, or shared-infrastructure change". The Impact Analysis below (see *Impact Analysis (P.2)*) shows intentional, deliberate touchpoints in **authentication** (token helpers), **user-roles-permissions** (new catalog actions + the enforcement seam), **user-management** (revocation-cascade events), **search** (a new source), **settings** (a new key family), **eventbus** (new events), **logging-coverage** (REQ-012 tracing policy), and the composition root `src/main.py`.

**Why needed:** It decides the spec shape (Impact Analysis section is mandatory for CROSS-CUTTING — see `docs/specs/search.md` §12 as the model), the ADR threshold (S2.1 requires ADRs for new shared capability / cross-feature interfaces), the todo set, and the version bump (`minor`/`major` vs `minor`).

**Options:**
- **A. Keep FEATURE** — treat everything outside `src/backend/apikeys/` as "additive wiring" (the `search.md` §12 argument: "No existing REQ or AC of any affected feature is touched").
- **B. Reclassify CROSS-CUTTING now** — same work, but the spec carries a per-feature Impact Analysis, the DAG is grouped by affected feature, and ADRs are mandatory for the key→principal seam and the audit store.
- **C. Reclassify only if Q-03/Q-08 land on the invasive options** (extending `Principal`, or a shared audit capability).

**Recommendation:** **B.** The change introduces a *new shared capability* (an authorization credential type + a dispatch/audit surface consumed by every enforced feature) and a *new cross-feature interface* (`resolve_key` → `Principal`, `describe_actions` over the closed catalog). That is criterion #3 verbatim, and the `search` precedent shows the CROSS-CUTTING shape costs nothing extra when all touches are additive. Practical consequence: the branch created at P.4 must be `crosscut/api-keys` (or `feature/api-keys` renamed with `git branch -m` per the Escalation Rules), and the bump is `minor` (not breaking → no `major`).

---

### Q-03 — Which seam turns a raw key into an acting principal?

- **Step:** P.2 (Phase P)
**Answer:** Neither A nor B nor C as written — use the backend's own session tokens. The user's answer: "the api should use the tokens etc that the backend provides." That is the existing path: `AuthService.login()` issues a session token, the API puts it in `Principal(user_id, session_token)`, and `PermissionService._validate_session` validates it. **Correction to this entry's Context:** its "Important finding" is stale — `src/main.py:158` passes `session_lookup=_session_repository  # validates a provided session token (REQ-017, AC-020)`, so token validation is wired and live on `main`. No new seam, no `Principal` change.
- **Status:** ANSWERED
- **Date:** 2026-10-08

- **Incorporated:** yes — see the re-scope note at the head of this file

**Context:** `Principal` (`src/backend/shared/principal.py:21-29`) has exactly two fields, `user_id` and `session_token`. `@requires_permission` (`src/backend/shared/principal.py:51-70`) calls `checker.require_permission(principal.user_id, permission_key, session_token=principal.session_token)`. `PermissionService._validate_session` (`src/backend/permissions/service.py:399-418`) already validates a bearer token through the structural `SessionLookup` seam (`get_by_token_hash(token_hash) -> SessionRecord | None`, `src/backend/permissions/models.py:78-81`) — an API-key row has exactly that shape. **Important finding:** the composition root does **not** wire a lookup — `src/main.py:145-153` constructs `PermissionService(...)` with no `session_lookup` argument, so today any `Principal(session_token=...)` denies with `storage_error` (fail-closed, `src/backend/permissions/service.py:407-408`).

**Why needed:** It is the single decision that determines whether `backend.shared` and `docs/specs/user-roles-permissions.md` (REQ-025, EDGE-022) must be amended — i.e. whether the change is forced to CROSS-CUTTING with a spec amendment — and whether scopes are enforced by the permission service or by api-keys.

**Options:**
- **A. api-keys resolves the key itself** and hands the caller a `Principal(user_id=<owner>)`; scopes are checked by api-keys before dispatch. `Principal`, `requires_permission` and the permissions feature are untouched; enforcement becomes **two independent checks** (api-keys: scope ∈ key.scopes; PermissionService: action ∈ owner's roles).
- **B. Extend `Principal` with a scope/credential field** and have `PermissionService._check` intersect it — one check, but it amends `user-roles-permissions.md` REQ-025 and every feature's principal contract, and `backend.shared` is the repo's most-depended-on module.
- **C. Plug the key store into the existing `SessionLookup` seam** (a composite lookup: session, then key) and pass the key as `session_token`. No model change, but the denial reasons become wrong (`invalid_session` for a bad key), and it conflates sessions with keys — exactly the "two half-implemented revocation models" risk the TODO warns about.

**Recommendation:** **A.** It is the smallest correct diff, keeps the fail-closed reason vocabulary honest, and composes with ADR-071 unchanged. Note the consequence for Q-04: with A, the permission service never sees the key, so the *scope* half of the check must live in api-keys. Also record the `session_lookup`-not-wired finding: if any option needs token validation at the composition root, that wiring is a separate, explicit fix (it is currently dead-on-arrival for all features).

---

### Q-04 — Which permission is checked on a key-driven call?

- **Step:** P.2 (Phase P)
**Answer:** A — the target action is the checked permission, via the owner's existing roles. After re-phrasing, the user's answer is that the backend's existing permissions decide access. There is **no per-key scope list in v1**: the API resolves the session token to its owner and calls the feature method with that `Principal`, so `@requires_permission` + the closed 61-action catalog decide. Scope-checking machinery is deferred with the api-keys credential change.
- **Status:** ANSWERED
- **Date:** 2026-10-08

- **Incorporated:** yes — see the re-scope note at the head of this file

**Context:** Every enforced method is decorated with its own action key (ADR-071), and the live catalog holds exactly 61 actions across 7 features (authentication 11, usermanagement 11, settings 19, filemanagement 10, sessionmanagement 6, mail 3, search 1). The TODO's acceptance signal is "a key scoped to `usermanagement.list_users` can perform that action but is denied `usermanagement.create_user`".

**Why needed:** It decides whether an `apikeys.call` action exists at all, what the audit row's `action` column holds, and whether a key can be used to reach an action that is *not* a catalog action (today: none of the permission-management operations — `create_role`, `grant_permission`, `assign_role`, `set_system_permissions` — are catalog actions, because `src/backend/permissions/` has **no** `feature_actions.py`, only `feature_settings.py`).

**Options:**
- **A. The target action is the checked permission.** The gateway checks `action ∈ key.scopes`, then calls the feature method with `Principal(user_id=owner)`; `@requires_permission` checks `action ∈ owner's roles`. No `apikeys.call` action for dispatch.
- **B. An `apikeys.call` wrapper action** gates the dispatch entry point, and the target action is checked additionally.
- **C. Only `apikeys.call`** is checked (scopes become the sole authorization).

**Recommendation:** **A.** It is the only option that satisfies the acceptance signal literally, keeps the closed catalog as the single source of action truth, and never invents a permission that bypasses the per-action rules. **C is unsafe** (it would let a key reach any action regardless of the owner's roles, breaking "revoking a role tightens existing keys"). **B is redundant** unless the user wants a separate kill switch for the whole dispatch surface — if wanted, add `apikeys.call` as an *additional* requirement, and say so in Q-19. Follow-up for the permission-management gap: keep role/grant management **out of scope** for v1 (it is a separate catalog-vocabulary change), so an LLM cannot self-escalate.

---

### Q-05 — Who enforces scopes, and where?

- **Step:** P.2 (Phase P)
- **Status:** PENDING
- **Incorporated:** no

**Context:** Feature boundaries forbid other features importing `backend.apikeys` internals (AGENTS.md "Features should expose explicit public interfaces"; features import only `backend.shared` at runtime, ADR-070). So scope enforcement must live either in an api-keys-owned dispatch entry point, or inside each target feature (impossible without an import), or in the permission service (Q-03 option B).

**Why needed:** It fixes the public API shape (is there a `ToolGateway`/`call()` entry point at all?) and where the audit row is written (the same choke point, or per feature).

**Options:**
- **A. One api-keys-owned gateway** (`ApiKeyService.call(raw_key, action, arguments, ...)` or a separate `ToolGateway` class in the feature) that resolves the key, checks the scope, writes the audit row, and invokes the target callable. Target callables are injected at construction by the composition root (the `_LazyUserManager` / `_LazyPermissionService` pattern, `src/main.py:129-130`), so no cross-feature import is introduced.
- **B. Return a principal + scope set and let each caller enforce** — no gateway; every consumer re-implements the check.
- **C. Enforce inside the permission service** (Q-03 B).

**Recommendation:** **A.** One choke point means one audit write, one scope check, one denial path, and it is the only way the "exactly one audit row per call" acceptance signal is enforceable. Inject the action → callable map at the composition root (the repo already breaks feature cycles that way).

---

### Q-06 — Bootstrap: how does the first key get created?

- **Step:** P.2 (Phase P)
- **Status:** PENDING
- **Incorporated:** no

**Context:** With Q-01 = A there is no HTTP request to authenticate, so key creation is an in-process call. Every enforced method defaults to the **system principal** (`Principal()` with `user_id=None`, `src/backend/shared/principal.py:21-29`, EDGE-022), and the composition root seeds `BOOTSTRAP_SYSTEM_PERMISSIONS` (`src/backend/permissions/models.py`) — so an in-process `create_key()` call is effectively unauthenticated unless something else gates it. A key's `user_id` must reference a real user (the owner), which requires `usermanagement.create_user`-level trust.

**Why needed:** It decides the trust model of the whole feature: who may mint credentials, and whether an LLM that holds one key can mint a second, wider one.

**Options:**
- **A. `apikeys.create_key` is a normal catalog action**, enforced like any other; only a principal whose roles include it (i.e. an admin) may create keys, and the caller names the owner `user_id`.
- **B. ADR-documented bootstrap only:** key creation is permitted for the system principal (composition root / an operator script) and **never** for a key-derived principal — a key can use, list and revoke its own key but cannot mint keys.
- **C. Exchange credentials for a key** (`login` → session token → `create_key` carrying that token) — requires the `session_lookup` wiring that is currently missing (see Q-03).
- **D. A CLI/`scripts/` entry point** for operators (precedent: the `structure-map` TODO ships a CLI as its own FEATURE).

**Recommendation:** **A + B combined.** `apikeys.create_key` is a catalog action (so it is enforceable and auditable), and the spec states normatively that a principal resolved **from a key** may never call the key-minting actions — a key cannot escalate or clone itself. Bootstrap for the very first key is the documented system-principal path (composition root / operator code), recorded in the spec's security section and covered by an EDGE. Reject C for v1 (it needs the missing `session_lookup` wiring); reject D as a separate change (YAGNI — the in-process call is the API).

---

### Q-07 — Storage: new `api_keys` table, or reuse the `sessions` table?

- **Step:** P.2 (Phase P)
- **Status:** PENDING
- **Incorporated:** no

**Context:** `docs/specs/session-management.md` constrains itself to "**no second session store**" and reuses authentication's `Session` table (`src/backend/authentication/models.py`: `id` UUID pk, indexed `user_id`, unique+indexed `token_hash` holding only the SHA-256 hex digest, `created_at`, `expires_at`, `revoked`, plus nullable metadata columns). The composition root gives each feature its own SQLite file (`sqlite:///./data/permissions.db`, `./data/authentication.db`, `./data/usermanagement/users.db`, …). AGENTS.md ("Using Migrations (alembic)") requires a migration for any new SQLModel table and an import added to `migrations/env.py`.

**Why needed:** It decides the schema, the migration, whether authentication's `SessionRepository` ABC grows (an NFR-003 additive-ABC change, ADR-080 precedent), and whether session-management's revocation/cap/eviction logic silently starts applying to long-lived machine credentials.

**Options:**
- **A. Two api-keys-owned tables** in `sqlite:///./data/apikeys.db`: `api_keys` (id, user_id, token_hash, label, scopes, created_at, expires_at, revoked, optional `created_by`) and `api_key_calls` (the audit log). Repository ABC + SQLite concrete, per-feature DB.
- **B. Reuse/extend the `sessions` table** with `kind`, `scopes`, `label`, `last_used_at` columns.
- **C. Same DB as permissions** (`./data/permissions.db`) but separate tables.

**Recommendation:** **A.** The TODO already flags the risk ("two token stores drifting into two half-implemented revocation models") — B *creates* that drift in the worst direction: session-management's cap eviction, `LoginSucceeded` handling and `cleanup_expired` would start touching machine credentials, and session-management's own constraint "no activity tracking, no `last_seen_at`" (`docs/specs/session-management.md` Constraints) directly contradicts api-keys' `last_used_at`. A keeps both specs' semantics intact and is the per-feature-DB convention. C is acceptable but buys nothing.

---

### Q-08 — Feature-local audit log, or a shared audit capability?

- **Step:** P.2 (Phase P)
- **Status:** PENDING
- **Incorporated:** no

**Context:** No audit store exists anywhere in the repo. Four specs list a persistent audit log as explicitly **out of scope**, and the only existing "who did what" signal is the `PermissionDenied(user_id, permission, reason)` event (`docs/specs/user-roles-permissions.md` REQ-020) published to the event bus — nothing subscribes to it for storage.

**Why needed:** A shared audit capability is by definition CROSS-CUTTING *and* invasive (every feature's write path or every feature's events would feed it), which changes the change's size by several multiples.

**Options:**
- **A. api-keys-owned `api_key_calls` table** — one row per key-driven call, written by the gateway (Q-05). Nothing else writes to it.
- **B. A shared `backend/audit/` feature** that api-keys is the first consumer of, fed by event subscriptions from other features.
- **C. No storage at all** — publish `ApiKeyCalled`/`ApiKeyCallDenied` events and let the loguru log be the audit trail.

**Recommendation:** **A.** The TODO's acceptance signal ("every call leaves exactly one audit row naming key id, action and outcome, queryable per key") requires storage, and only the gateway sees both the key and the outcome, so the log belongs to api-keys. **C fails the acceptance signal** (a loguru line is not queryable per key). **B is a different, much larger change** — if the user wants a general audit trail, it should be its own CROSS-CUTTING change that later absorbs this table; say so in the spec's Out of Scope.

---

### Q-09 — How are per-action tool schemas derived?

- **Step:** P.2 (Phase P)
- **Status:** PENDING
- **Incorporated:** no

**Context:** The acceptance signal is "a client can ask *what may this key do?* and get the action list with schemas derived from the real catalog". The catalog read API is `PermissionCatalog.actions(feature=None) -> Sequence[PermissionRead]` with fields `permission`, `feature`, `description` (`src/backend/permissions/catalog.py`) — the action list and descriptions already exist. The **argument** schemas do not: the enforced API is heterogeneous — some actions take a pydantic request model (`login(LoginRequest)`, `create_user(UserCreate)`, `search(SearchQuery)`), most take plain keyword arguments (`upload(source, key=None, namespace="general", ...)`, `list_sessions(token=None, user_id=None, ...)`, `set_value(key, value)`). There is no "effective permissions for a user" API in the permission service either — only `list_permissions(feature)` (the catalog) and `get_role_permissions(role)` — so the effective set must be computed from `UserRead.roles` × `get_role_permissions` × `catalog.actions()` ∩ scopes.

**Why needed:** It decides whether the schema export is honest (derived from real signatures, cannot drift) or a hand-maintained table (drifts), and whether existing feature signatures must change (a large CROSS-CUTTING churn).

**Options:**
- **A. Introspection:** `inspect.signature` + resolved type hints → JSON Schema via `pydantic.TypeAdapter` per parameter (stdlib + pydantic, no new dependency); `PermissionRead.description` supplies the action description; the `principal` parameter is excluded from the schema.
- **B. A hand-written tool table** in `feature_actions.py` (name → JSON Schema).
- **C. Refactor every action to take a single pydantic request model**, then export `Model.model_json_schema()`.

**Recommendation:** **A.** Zero new dependencies, zero drift, and it reuses the catalog the repo already builds at startup (the TODO's "derived from the real catalog"). Accept and document the honest limits as EDGEs: `Any`/untyped parameters export as `{}`; `UUID`/`datetime`/`Enum` map to their pydantic JSON-schema forms; defaults are reported as schema defaults; `**kwargs`-style parameters are excluded. **C is a large, separate refactor** (it would touch every feature's public API and its tests) and must not be smuggled into this change. **B** is exactly the drift the acceptance signal forbids.

---

### Q-10 — May scopes contain wildcards?

- **Step:** P.2 (Phase P)
- **Status:** PENDING
- **Incorporated:** no

**Context:** The grant grammar already allows feature-level wildcards: `_grant_matches` treats a grant ending in `.*` as a prefix match, and `_is_valid_grant_key` accepts a catalog action or `<feature>.*` where the feature is in `catalog.features()` (`src/backend/permissions/service.py:78-90, 485-495`; REQ-003, D18).

**Why needed:** It decides the scope validation rule, the `key_capabilities` expansion (a wildcard must expand to a concrete action list for the client), and whether `*` / `*.*` / partial wildcards (`usermanagement.list_*`) are legal.

**Options:**
- **A. Exactly the grant grammar:** a catalog action, or `<feature>.*` for a feature in `catalog.features()`. Nothing else.
- **B. Exact actions only** (no wildcards).
- **C. Grant grammar plus a global `*`** (all actions the owner has).

**Recommendation:** **A.** Reusing the existing grammar means one validator, no new vocabulary (the TODO's "never invent permission names"), and least surprise for anyone who already understands grants. `describe_actions()`/`key_capabilities()` must return the **expanded concrete action list**, never the raw wildcard, so the client's view is exact. Reject C: a global `*` is a role-level decision, not a credential-level one.

---

### Q-11 — Effective grant set, and creation-time validation of scopes?

- **Step:** P.2 (Phase P)
- **Status:** PENDING
- **Incorporated:** no

**Context:** The TODO fixes the semantics: effective grants = key scopes ∩ the owner's role grants, so revoking a role tightens existing keys immediately (the permission service re-reads grants on every check — `docs/specs/user-roles-permissions.md` REQ-011/AC-005: "Immediate effect on the next check (no re-login, no cache)", `tests/acceptance/permissions/test_check_api.py:915-918`).

**Why needed:** It decides whether `create_key` rejects a scope the owner does not currently hold (fail-fast, but breaks "grant the role later" workflows) or accepts it (the intersection silently decides at call time), and what `key_capabilities` reports when the two sets differ.

**Options:**
- **A. Accept at creation; intersect at call time.** `create_key` validates only that each scope is a legal grant key (Q-10). `key_capabilities` returns the intersection plus, optionally, the scopes that are currently inert.
- **B. Reject at creation** any scope the owner's roles do not already grant.
- **C. Accept with a WARNING** recorded (log + event) that the scope is currently inert.

**Recommendation:** **A + C's warning.** A matches the repo's live-check, no-cache model and keeps role grants the authority (a key can never exceed the owner — that is INV-territory). The warning is one log line and makes the "why is this key denied?" question answerable. `key_capabilities` MUST report the effective (intersected) list, never the raw scopes — otherwise the client is told something the backend will refuse.

---

### Q-12 — Revocation cascade for keys?

- **Step:** P.2 (Phase P)
- **Status:** PENDING
- **Incorporated:** no

**Context:** Sessions are revoked on `UserPasswordChanged`, `UserDeactivated` and `UserDeleted` (ADR-063/ADR-064; `docs/specs/session-management.md` REQ-015), implemented as subscriptions inside session-management, not as changes to user-management. The TODO does not say whether keys follow.

**Why needed:** It is a security-vs-operations trade-off with a direct acceptance-signal consequence (a deactivated user's key must not keep working), and it decides whether api-keys subscribes to three user-management events.

**Options:**
- **A. Revoke on `UserDeleted` and `UserDeactivated`, not on `UserPasswordChanged`.**
- **B. Mirror sessions exactly** (all three).
- **C. Never cascade** — keys are independent credentials an admin revokes explicitly.

**Recommendation:** **A.** A deleted or deactivated account must not retain machine access (a deactivated user's key still working would contradict `inactive_user` denial semantics — the permission service already denies inactive users, so B's password-change leg is the only real question). Password change is a *human* credential rotation; silently killing production automation keys is a surprising side effect, and the spec should instead state that rotating a leaked key is an explicit `revoke_key` (which works by id, without knowing the secret — TODO requirement). Implement as subscriptions inside api-keys (ADR-064 pattern), no user-management change.

---

### Q-13 — Expiration: optional per key, default TTL?

- **Step:** P.2 (Phase P)
- **Status:** PENDING
- **Incorporated:** no

**Context:** The TODO says expiration is *optional*. Sessions use a live setting (`authentication.session_ttl`, default 7 days) and INV-002 ("valid iff unrevoked and unexpired"). Password-reset tokens default to 15 minutes. `docs/specs/session-management.md` explicitly refuses to change expiration semantics or add activity-based extension.

**Why needed:** It sets the default (`expires_at = None` vs a TTL), the settings key, and whether an expired key is *deleted* or kept-and-denied (which determines whether the audit log's per-key queries survive expiry).

**Options:**
- **A. Optional per key; default `None` (never expires)**; a live `apikeys.max_ttl_days` setting may cap it (0/None = uncapped).
- **B. Optional per key; default from a live `apikeys.default_ttl_days` (e.g. 90).**
- **C. Mandatory expiry** on every key.

**Recommendation:** **A**, with the cap in place so an operator can force expiry policy without touching the feature. Expired keys are **kept and denied** (like revoked ones) so the audit trail stays queryable per key; a separate `cleanup_expired`-style pruning step (Q-21) removes old rows. C contradicts the TODO's "optional expiration".

---

### Q-14 — `last_used_at`: stored column or derived from the audit table?

- **Step:** P.2 (Phase P)
- **Status:** PENDING
- **Incorporated:** no

**Context:** The TODO wants last-used tracking. Two facts collide: (1) `docs/specs/session-management.md` Constraints forbid activity tracking for sessions ("no activity tracking, no `last_seen_at`, no `expires_at` updates"); (2) the audit table already records one row per call with a timestamp (Q-20), so `last_used_at` is `max(api_key_calls.created_at)` for that key id — a join, not a column.

**Why needed:** It decides whether every authenticated call performs an extra `UPDATE` on the hot path (write amplification on SQLite under concurrency, Q-27) and whether pruning the audit log silently destroys the last-used signal.

**Options:**
- **A. Derived:** no column; `ApiKeyRead.last_used_at` is computed from the audit table (or `None` when there are no rows).
- **B. Stored column** updated on every call (allowed *and* denied calls, or allowed only).
- **C. Stored column, coalesced** (only written when it lags by more than N seconds).

**Recommendation:** **A.** It is the smaller implementation, it cannot drift from the audit trail (one source of truth), it keeps the hot path to a single INSERT, and it makes the audit log the authority — which is what the acceptance signal already requires. Mark the ceiling honestly (`ponytail:` comment: the per-key last-used query is an indexed `MAX` over the audit table; upgrade path = a materialized column if the audit table grows past the NFR budget). If the user prefers B, C is the acceptable variant (never an unconditional per-call UPDATE).

---

### Q-15 — Key format and prefix?

- **Step:** P.2 (Phase P)
- **Status:** PENDING
- **Incorporated:** no

**Context:** authentication already exports the token helpers: `new_token() -> secrets.token_urlsafe(32)` (43 chars, 256-bit) and `hash_token() -> SHA-256 hex digest`, both `@logged(slow_threshold_ms=10, include_args=False)` (`src/backend/authentication/tokens.py`, exported at `src/backend/authentication/__init__.py:62,108-109`). Session-management reuses them (`hash_token`), and `docs/specs/authentication.md` REQ-006 mandates opaque 256-bit tokens hashed with SHA-256 at rest.

**Why needed:** It decides the wire format, whether the raw string is hashed as-is or normalized first (a lookup-miss class of bug), and whether secret scanners / humans can recognize a leaked key.

**Options:**
- **A. Reuse `new_token()` and prepend a fixed prefix**, e.g. `ak_<43 chars>`; the **entire** string (prefix included) is SHA-256 hashed and stored.
- **B. Bare `new_token()`** (no prefix).
- **C. A structured key** `ak_<key id>_<secret>` (GitHub-style, lets lookup skip a table scan).

**Recommendation:** **A.** The prefix costs one string concat, makes a leaked key recognizable (and lets a secret scanner / log scrubber pattern-match it), and keeps the hash lookup exactly as it is for sessions. **C is unnecessary** — the lookup is already an indexed unique `token_hash` equality, so embedding the id buys nothing (YAGNI). Normative rule for the spec: never normalize, trim, case-fold or strip the prefix before hashing — the whole presented string is the secret (an EDGE for "prefix stripped by the client").

---

### Q-16 — Whose keys may a caller list and revoke?

- **Step:** P.2 (Phase P)
- **Status:** PENDING
- **Incorporated:** no

**Context:** session-management's shape is the precedent: exactly one of `token` (self-service) or `user_id` (admin) is required, and both supplied / neither supplied is a `ValueError` (EDGE-008); revocation of an unknown or already-revoked target is an idempotent no-op (REQ-008). The TODO requires "revoke by id without knowing the secret" (leaked-key rotation).

**Why needed:** It decides the method signatures, the owner check, and whether an admin can act on another user's keys (and who is an admin here).

**Options:**
- **A. Mirror session-management:** `list_keys(user_id=None, principal=...)` — a key-derived principal may only list its own; an explicit `user_id` requires the `apikeys.list_keys` action; `revoke_key(key_id, principal=...)` is owner-checked for key-derived principals and idempotent.
- **B. Self-service only** (no admin path).
- **C. Admin-only management** (a key can never manage keys).

**Recommendation:** **A + C's key-derived restriction from Q-06.** A key may list and revoke **itself and its own owner's keys only** — and per Q-06, minting keys requires a non-key principal. Idempotent revoke (unknown id → no-op, no exception) matches REQ-008 and makes rotation scripts safe. Record the "neither/both arguments" EDGE as `ValueError`, matching session-management's no-new-exceptions stance (Q-24).

---

### Q-17 — Per-user key cap: reject or evict?

- **Step:** P.2 (Phase P)
- **Status:** PENDING
- **Incorporated:** no

**Context:** Sessions have a live cap with **oldest-first eviction** (`sessionmanagement.max_sessions_per_user`, default 5), enforced event-driven on `LoginSucceeded` (`docs/specs/session-management.md` REQ-014). Keys have no login event to hook, and a silently evicted key breaks running automation without anyone knowing.

**Why needed:** It decides whether creation can fail with an error, whether an unbounded number of keys per user is a DoS/audit-growth risk, and whether any event subscription is needed.

**Options:**
- **A. Reject creation over a live `apikeys.max_keys_per_user` (default e.g. 10)** with a typed error; revoked/expired rows do not count toward the cap.
- **B. Evict oldest** (session precedent).
- **C. No cap.**

**Recommendation:** **A.** Silent eviction of a machine credential is the worst failure mode of this whole design (an automation dies with no signal), and keys are not sessions. Rejecting is honest, needs no event hook, and bounds both the key table and the audit table's fan-out. C is unsafe; B contradicts the "keys are not sessions" boundary this change is drawing.

---

### Q-18 — Rate limiting / quotas in v1?

- **Step:** P.2 (Phase P)
- **Status:** PENDING
- **Incorporated:** no

**Context:** The TODO lists this as an open P.2 decision. The repo has no rate limiter, no shared counter, and no middleware layer (Q-01). `docs/todo/tenacity-rich-cachetools.md` (scored 2/5, unscheduled) is the tempting dependency hook, and the notifications change explicitly refused to assume it exists.

**Why needed:** It decides whether the spec carries an NFR/REQ for throttling, whether a counter store is needed, and whether a new dependency enters.

**Options:**
- **A. Out of scope**, stated in the spec's Out of Scope, with the audit log named as the detection mechanism and `apikeys.max_keys_per_user` as the only bound.
- **B. A minimal per-key fixed-window counter** in api-keys (in-process, per-process, live settings for the window/limit).
- **C. Defer, but reserve the settings keys and the audit `outcome` vocabulary** so a later change can add it without a contract break.

**Recommendation:** **A + C.** Build no limiter (YAGNI, and an in-process counter is a false guarantee the moment two processes share a key — mark that ceiling in the spec rather than shipping a misleading half-feature). Reserve the vocabulary: the audit row's `outcome` field and the settings namespace make a later limiter additive. If the user wants real throttling, it is its own CROSS-CUTTING change (shared counter + every entry point).

---

### Q-19 — Which `apikeys.*` catalog actions exist?

- **Step:** P.2 (Phase P)
- **Status:** PENDING
- **Incorporated:** no

**Context:** Actions are declared per feature in `src/backend/<feature>/feature_actions.py` via `register_actions(catalog)` and registered in `src/main.py`; the catalog is closed after startup and keys must match `^[a-z0-9_-]+\.[a-z0-9_-]+$` and start with `<feature>.` (`src/backend/permissions/catalog.py`). Adding a feature's actions is **additive and does not break the AC-006 catalog test** — that test builds its own catalog from the six original features (`tests/acceptance/permissions/test_check_api.py:1001-1035`), which is exactly how `search.search` was added without touching `user-roles-permissions.md`.

**Why needed:** These names are permanent normative vocabulary (the closed catalog), they are what scopes may reference, and they decide which methods are enforced vs. exempt.

**Options (proposed inventory, feature name `apikeys`):**
- **A.** `apikeys.create_key`, `apikeys.list_keys`, `apikeys.revoke_key`, `apikeys.revoke_all_keys`, `apikeys.key_capabilities`, `apikeys.describe_actions`, `apikeys.list_key_calls` — 7 actions, no `apikeys.call` (Q-04 A).
- **B.** A plus `apikeys.call` (8) — a separate kill-switch action for the dispatch entry point.
- **C.** A smaller set (drop `apikeys.list_key_calls` in favour of a search source, Q-22).

**Recommendation:** **A**, with the normative rule that the *dispatch* path is enforced by the **target** action (Q-04) and the key-management actions are enforced by their own keys and unreachable from a key-derived principal (Q-06). Feature name `apikeys` (one word, lowercase, matches the existing `usermanagement`/`filemanagement`/`sessionmanagement` style, and the settings key prefix convention from `docs/specs/settings-coverage.md` REQ-017). Confirm the exact seven names before P.4 — they cannot be renamed later without a breaking change.

---

### Q-20 — Audit row semantics and outcome vocabulary?

- **Step:** P.2 (Phase P)
- **Status:** PENDING
- **Incorporated:** no

**Context:** The TODO requires "every call leaves exactly one audit row naming key id, action and outcome, queryable per key". The permission service already has a **closed** denial-reason set — `malformed_permission`, `unknown_user`, `inactive_user`, `storage_error`, `invalid_session`, `session_principal_mismatch`, `unknown_permission`, `unauthorized` — each denial logged at WARNING and published as `PermissionDenied(user_id, permission, reason)` (REQ-020, ADR-075 fail-closed).

**Why needed:** It decides the table columns, whether denials are recorded (they must be, or the audit is useless), whether key-level failures (unknown/revoked/expired key) reuse the existing reason vocabulary or add new reasons, and whether the audit row is written before or after the target call (a raising call must still leave a row).

**Options:**
- **A. One row per call attempt**, columns: `id`, `key_id`, `user_id` (owner), `action`, `outcome` (`allowed` | `denied` | `error`), `reason` (closed set), `created_at`, optional `duration_ms`. Key-level failures (`unknown_key`, `revoked_key`, `expired_key`, `scope_denied`) get their **own** small closed set in api-keys; permission-service denials reuse its reason strings verbatim.
- **B. Only successful calls are recorded.**
- **C. Reuse `PermissionDenied` events as the audit source** (a subscriber writes rows).

**Recommendation:** **A.** The gateway is the only place that sees the key, the scope decision, and the outcome, so it writes the row itself (C would miss scope denials and key-resolution failures, and would double-write permission denials). Keep the two reason vocabularies **separate and closed** — inventing new values inside the permission service's set would amend `user-roles-permissions.md`. Normative: the row is written even when the target method raises (`outcome=error`), and the row never contains the key secret, the hash, or the call arguments (NFR + INV).

---

### Q-21 — Audit retention and pruning?

- **Step:** P.2 (Phase P)
- **Status:** PENDING
- **Incorporated:** no

**Context:** Every unbounded table in this repo has an application-scheduled pruning analogue: `sessionmanagement.cleanup_expired() -> int` bounded by `sessionmanagement.cleanup_batch_size` (default 1000), called by the application on its own schedule, no threads in the feature (REQ-012). Note Q-14 makes the audit table the source of `last_used_at`, so pruning interacts with it.

**Why needed:** It decides whether a `cleanup` method exists, its settings keys, and whether pruning is allowed to destroy the last-used signal.

**Options:**
- **A. `cleanup_key_calls() -> int`** deleting rows older than a live `apikeys.audit_retention_days` (default e.g. 90) in batches of `apikeys.cleanup_batch_size` (default 1000); keys whose only signal was pruned report `last_used_at = None`.
- **B. No pruning** (append-only forever).
- **C. Prune only for revoked/deleted keys.**

**Recommendation:** **A.** An append-only per-call log is the one part of this design that will grow without bound, and the repo already has the exact pattern to copy. B is unacceptable for a long-lived credential system; C is a rule nobody asked for.

---

### Q-22 — Register a search source?

- **Step:** P.2 (Phase P)
- **Status:** PENDING
- **Incorporated:** no

**Context:** The search feature is the repo's existing read/query surface: features register `SearchSource(name, fields, query)` via `build_*_source(repository)` at the composition root (`build_user_source` / `build_file_source` / `build_session_source`; `docs/specs/search.md` REQ-020…REQ-022, ADR-077 additive-source pattern). Field types are a closed set (string/number/boolean/datetime), filters are a fixed operator DSL, and pagination is offset/limit + total.

**Why needed:** It decides whether the audit query is a dedicated api-keys method (Q-19's `apikeys.list_key_calls`) or a search source, and whether the key table is globally searchable.

**Options:**
- **A. Register `build_apikey_source(repo)`** (fields: `key_id`, `user_id`, `label`, `scopes` as string, `created_at`, `expires_at`, `revoked`) and keep the audit query as the dedicated `apikeys.list_key_calls` method.
- **B. Two sources** (keys + audit rows).
- **C. No source in v1** — dedicated methods only.

**Recommendation:** **A.** It is a small additive module in api-keys (the established pattern), it makes "which keys exist?" answerable from the one place operators already query, and it never exposes the hash (fields are declared explicitly). B is premature (the audit query needs per-key ordering and outcome filtering that the dedicated method already gives); C leaves the feature invisible to the repo's query surface for no benefit.

---

### Q-23 — Which events does api-keys publish?

- **Step:** P.2 (Phase P)
- **Status:** PENDING
- **Incorporated:** no

**Context:** Every feature publishes typed, non-sensitive events for its mutations (user-management: `UserCreated`/`UserUpdated`/…; session-management: `SessionRevoked`/`AllSessionsRevoked`; authentication: `LoginSucceeded`/`Logout`/…), best-effort — "a publisher failure never breaks the operation" — and events never carry secrets.

**Why needed:** It fixes the published-event inventory (a public contract) and whether the audit row and the event are the same signal (they must not be conflated: events are best-effort, the audit row is durable).

**Options:**
- **A.** `ApiKeyCreated`, `ApiKeyRevoked`, `ApiKeyAllRevoked` (fields: `user_id`, `key_id` only) — **no** per-call event (the audit row is the per-call record).
- **B.** A plus `ApiKeyCalled`/`ApiKeyCallDenied` per call.
- **C.** No events at all.

**Recommendation:** **A.** Per-call events would double the event-bus load for a signal that is already durable in the audit table, and the event bus is at-most-once (a dropped event would look like a missing audit row). The notifications change (Q-23 there) is the natural future subscriber.

---

### Q-24 — New exception hierarchy or plain `ValueError` + reused errors?

- **Step:** P.2 (Phase P)
- **Status:** PENDING
- **Incorporated:** no

**Context:** session-management deliberately introduced **no new exception types**: "argument errors are `ValueError`; invalid-token failures re-raise authentication's `InvalidSessionError`" (REQ-002/REQ-009/REQ-010). Most other features own a hierarchy (`MailError`, `FileManagementError`, `SearchError`, `UserManagerError`, `SettingsError`, `AuthenticationError`).

**Why needed:** It decides the public API's error contract, the test set, and whether a caller can distinguish "unknown key" from "scope denied" from "over the cap" programmatically (which matters for an LLM driving the API).

**Options:**
- **A. A small `ApiKeyError` hierarchy**: `ApiKeyNotFoundError`, `ApiKeyRevokedError`/`ApiKeyExpiredError` (or one `ApiKeyInvalidError`), `ApiKeyScopeDeniedError`, `ApiKeyLimitError`, `ApiKeyValidationError`; permission denials keep raising the shared `PermissionDeniedError` unchanged.
- **B. Plain `ValueError` + reused `InvalidSessionError`** (session-management style).
- **C. One `ApiKeyError` with a `reason` attribute** (closed string set, mirroring the denial-reason style).

**Recommendation:** **C.** One class with a closed `reason` set is the smallest contract that is still machine-actionable for an agent client, it matches the permission service's existing closed-reason discipline, and it avoids a five-class hierarchy nobody will catch separately. Argument errors stay `ValueError` (session-management precedent). Never leak the secret or the hash in the message (NFR).

---

### Q-25 — Confirm the `apikeys.*` settings inventory?

- **Step:** P.2 (Phase P)
- **Status:** PENDING
- **Incorporated:** no

**Context:** Feature-owned `register_settings(registry)` with live reads and hardcoded fallbacks is the convention; `docs/specs/settings-coverage.md` REQ-017/REQ-018/REQ-019 fix the key prefix (full feature name), `category` = domain (`application`/`security`) and `group` = feature name, and the inventory table format.

**Why needed:** The inventory becomes REQ/AC rows and a test (`test_inventory_matches` style), and unregistered keys must fall back to documented defaults.

**Options (proposed inventory):**

| Key | Kind | Default | Category | Group |
|---|---|---|---|---|
| `apikeys.max_keys_per_user` | NUMBER | `10` | security | apikeys |
| `apikeys.max_ttl_days` | NUMBER | `0` (0 = uncapped) | security | apikeys |
| `apikeys.audit_retention_days` | NUMBER | `90` | security | apikeys |
| `apikeys.cleanup_batch_size` | NUMBER | `1000` | security | apikeys |
| `apikeys.audit_page_size` | NUMBER | `100` | security | apikeys |

**Recommendation:** Adopt the table above (drop `apikeys.audit_page_size` if the audit query reuses `search.default_page_size` instead — decide with Q-22). No `apikeys.enabled` kill switch unless the user wants one (notifications has one; a kill switch for the whole credential type is a reasonable ask — say so in the answer).

---

### Q-26 — Confirm the public API surface and representations?

- **Step:** P.2 (Phase P)
- **Status:** PENDING
- **Incorporated:** no

**Context:** The session/auth precedent for a show-once secret: `LoginResult.token` is the **only** place a raw token appears, and `SessionInfo` carries no token (`src/backend/authentication/models.py`; authentication REQ-021). The TODO requires the raw key shown exactly once and never again in lists, logs, events, audit rows or error messages.

**Why needed:** It fixes the public API (the NFR contract), the representation models, and where the raw secret may legally appear — every one of which becomes an AC.

**Options (proposed surface, `backend.apikeys`):**
```python
class ApiKeyCreate(BaseModel):  # input
    user_id: UUID
    label: str | None = None
    scopes: list[str]
    expires_at: datetime | None = None

class ApiKeyRead(BaseModel):    # never contains the secret or the hash
    id: UUID
    user_id: UUID
    label: str | None
    scopes: list[str]
    created_at: datetime
    expires_at: datetime | None
    revoked: bool
    last_used_at: datetime | None

class ApiKeyCreatedResult(BaseModel):
    api_key: ApiKeyRead
    key: str                    # the raw secret — returned exactly once, here only

class ApiKeyCallResult(BaseModel):
    allowed: bool
    action: str
    reason: str | None
    value: Any | None           # the target action's return value
    audit_id: UUID

# ApiKeyService
create_key(...) / list_keys(...) / revoke_key(...) / revoke_all_keys(...)
resolve_key(raw) -> Principal            # the seam (Q-03 A)
call(raw_key, action, arguments) -> ApiKeyCallResult   # the gateway (Q-05 A)
key_capabilities(raw_key | key_id) -> list[ActionInfo] # scopes ∩ roles, expanded
describe_actions(feature=None) -> list[ActionInfo]     # catalog + JSON Schema (Q-09)
list_key_calls(key_id=None, ...) -> page               # audit query (Q-20)
cleanup_key_calls() -> int                             # pruning (Q-21)
```
Plus the module-singleton convention (`get_api_key_service()` / `reset_api_key_service()`, `src/backend/permissions/service.py:497-518` precedent) and `register_settings` / `register_actions` / `build_apikey_source`.

**Recommendation:** Adopt it, with two normative rules: (1) the raw key appears in **exactly one** field of **exactly one** return type (`ApiKeyCreatedResult.key`); (2) `resolve_key` is public but returns only a `Principal` — it never returns the row, the hash, or the scopes (a separate `key_capabilities` call does that, by id or by key). Confirm whether `call()` returns the target's raw value (`Any`) or a serialized form — recommendation: raw value in-process (the server question is deferred, Q-01), documented as an NFR contract point.

---

### Q-27 — Thread-safety and write behaviour for the audit row?

- **Step:** P.2 (Phase P)
- **Status:** PENDING
- **Incorporated:** no

**Context:** NFR-005-style reliability is a per-feature norm: the search registry and query path are thread-safe; `SqliteFileRepository` is thread-safe SQLite; authentication NFR-005 mandates thread-safe repositories. The event bus runs one worker thread. P-14 in `docs/workflow/PROBLEMS.md` records a real Windows file-lock failure from a shared default settings repository under `pytest-xdist`.

**Why needed:** An API key is by definition used concurrently (automation), and Q-14's derived `last_used_at` plus Q-20's per-call INSERT put write traffic on the read path.

**Options:**
- **A. State the NFR normatively:** the repository is thread-safe (connection-per-operation, matching `SqliteFileRepository`), the audit INSERT is part of the same operation, and a **failed audit write never breaks the call** (best-effort, logged at WARNING) — or, conversely, a failed audit write **denies the call** (fail-closed audit).
- **B. No concurrency requirement** (single-threaded assumption).

**Recommendation:** **A, and choose fail-closed for the audit write** — i.e. if the audit row cannot be written, the call is denied (`reason=storage_error`, matching the permission service's fail-closed stance, ADR-075). That is the honest reading of "every call leaves exactly one audit row": a call that leaves no row must not have happened. Flag it explicitly, because it is a real availability trade-off the user should own.

---

### Q-28 — Confirm the NFR budgets?

- **Step:** P.2 (Phase P)
- **Status:** PENDING
- **Incorporated:** no

**Context:** NFR budgets in this repo are measured and environment-aware after two corrections: `docs/specs/search.md` NFR-001 (v2 raised 100 ms → ~300 ms local / ~600 ms CI; P-36 in `docs/workflow/PROBLEMS.md` records the original budget being unrealistic for the query path), and the same precedent in settings NFR-001 v3. Coverage floor: `[tool.coverage.report] fail_under = 92` (`pyproject.toml:105`).

**Why needed:** A budget that cannot be met becomes a failed Phase 5 gate and a re-entry (P-36 cost multiple stuck subagents).

**Options (proposed):**
- **NFR-001 Performance:** `resolve_key` < 5 ms median (one indexed lookup + one SHA-256); `call()` overhead (resolve + scope check + audit INSERT + dispatch) < ~20 ms median **excluding** the target action's own cost; `describe_actions()` for the full 61-action catalog < ~100 ms median local / ~200 ms CI.
- **NFR-002 Security:** the raw key and its hash never appear in log records, events, audit rows, error messages, or any representation except `ApiKeyCreatedResult.key`; `@logged_class(include_args=False)`.
- **NFR-003 Contract:** `backend.apikeys` public API evolves additively (the repo default) — or the search-style recorded deviation if the user prefers.
- **NFR-004 Observability / NFR-005 Reliability:** tracing per `docs/specs/logging-coverage.md` REQ-012; thread-safety and fail-closed audit per Q-27.

**Recommendation:** Adopt, with the CI-aware split written into the wording from the start (both precedents had to be corrected later). Do not add a suite-runtime budget (the TODO's "full existing suite still passes" is a Phase 5 gate, not an NFR).

---

### Q-29 — Confirm the test strategy?

- **Step:** P.2 (Phase P)
- **Status:** PENDING
- **Incorporated:** no

**Context:** The category hierarchy is fixed (acceptance / integration / contract / property / unit), property tests use Hypothesis for INV-IDs, and the shared test tooling is mandatory (`tests/tooling_test_helpers.py`: `model_factory`, `travel` for TTL/expiry, `mock_http`). `tests/architecture/` **does not exist** despite AGENTS.md and the verify skill referencing it (recorded as P-32 in `docs/workflow/PROBLEMS.md`), so boundary checks in Phase 6 are manual.

**Why needed:** It fixes the test file layout, the property-test strategies, and how the "no secret anywhere" invariant is actually asserted (the strongest acceptance signal in the TODO).

**Options (proposed):**
- **Acceptance** `tests/acceptance/apikeys/` — one file per acceptance-criterion cluster (scoped call allowed/denied, show-once secret, revoke/expiry denial, one audit row per call, capabilities query).
- **Property** `tests/property/apikeys/` — INV: (a) no secret/hash in any representation, log record, event or error (Hypothesis over generated scopes/labels/arguments + a log-capture fixture, the `tests/acceptance/logging_coverage/test_secret_args.py` pattern); (b) effective grants ⊆ owner's role grants (never wider); (c) exactly one audit row per `call()` regardless of outcome; (d) scope validation is idempotent/closed under the catalog.
- **Contract** `tests/contract/apikeys/` — public API surface, settings inventory, catalog action inventory, NFR budgets.
- **Unit** `tests/unit/apikeys/` — schema derivation (Q-09), scope grammar validation, reason mapping.
- **Integration** `tests/integration/apikeys/` — composition-root wiring (catalog actions, settings, search source, revocation-cascade subscriptions), plus `travel()`-driven expiry tests.

**Recommendation:** Adopt. Add `tests/apikeys_test_helpers.py` (the per-feature helper-module convention) and extend `tests/logging_coverage_test_helpers.py:INVENTORY_CLASSES` + `test_secret_args.py` with the new classes (additive; the inventory list is hand-maintained, so no existing test breaks).

---

### Q-30 — Migration, `migrations/env.py`, deptry and CI consequences?

- **Step:** P.2 (Phase P)
- **Status:** PENDING
- **Incorporated:** no

**Context:** AGENTS.md ("Using Migrations (alembic)"): a change to a SQLModel table schema MUST add a migration, never hand-edit an applied one, and `migrations/env.py` imports the modules that define tables; the `migrations` job in `.github/workflows/quality.yml` runs `alembic upgrade head` against a temp DB. deptry runs in CI with per-rule ignores (`pyproject.toml:112-127`); P-22 records that deptry's first run surfaced 14 findings and that an unanchored `.gitignore` pattern silently excluded a source directory from its scan.

**Why needed:** It confirms which of these are in-scope deliverables of this change, and which only follow if Q-01 chooses a server.

**Options:**
- **A (Q-01 = A):** one alembic revision creating `api_keys` + `api_key_calls`; add `backend.apikeys.models` to `migrations/env.py`; **no** dependency changes (no deptry, `uv.lock`, or new CI job changes).
- **B (Q-01 = B):** same, plus a new boundary package's test category and CI/lint coverage; no dependency change (stdlib server).
- **C (Q-01 = C):** same, plus new runtime dependencies, a new ADR, deptry `DEP002`/`DEP003` review, `uv.lock` churn, and a possible new CI job.

**Recommendation:** **A.** Confirm at P.3 that the migration is a single revision for both tables and that `env.py` gains the import (the CI job will fail otherwise). Note the `uv.lock` staleness hazard (P-26) for any worktree that runs `uv run` before the lock is refreshed.

---

### Q-31 — Schedule: `Depends on:` relationship and ordering vs other changes?

- **Step:** P.2 (Phase P)
- **Status:** PENDING
- **Incorporated:** no

**Context:** `docs/todo/api-keys.md` records `Depends on: none (may be depended on by docs/todo/notifications.md)`, and `docs/questions/notifications.md` Q-11 asks the mirror question ("Does this change take `Depends on: api-keys`, or ship an in-process read API with the consumer deferred?"). `structlog-logging` (CROSS-CUTTING, PREPARING) replaces the logging backend and must re-derive 17 log-assertion test files; `tenacity-rich-cachetools` (2/5, unscheduled) is the tempting-but-unscheduled retry/caching hook referenced by Q-18.

**Why needed:** It resolves the circular question between the two TODO files and sets the ready-selection order (AGENTS.md: ready changes are ordered easiest-first, tie-break FIFO by READY date).

**Options:**
- **A. Neither depends on the other.** api-keys ships first (it is self-contained); notifications ships its in-process read API and defers its consumer.
- **B. `notifications` takes `Depends on: api-keys`.**
- **C. `api-keys` takes `Depends on: structlog-logging`** (build on the final logging backend).

**Recommendation:** **A**, and record it symmetrically in both TODO files: api-keys has **no** dependency; notifications does **not** depend on api-keys (its Q-11 answer should be "ship the in-process read API, defer the consumer"). Reject C: api-keys uses only the public logging API (`@logged_class`, `@logged`, `logger`), so it is backend-agnostic — but note the ordering cost either way: if api-keys lands first, its log-assertion tests join the 17 files `structlog-logging` must re-derive, so **prefer api-keys before structlog-logging** only if structlog-logging is not already in workflow. Do not couple to `tenacity-rich-cachetools` (Q-18).

---

## Interrogation coverage (P.2)

| Category | Covered | Where |
|---|---|---|
| Scope boundary / surface shape | yes | Q-01, Q-02, Q-18, Q-30 |
| Integration with existing features | yes | Q-03, Q-04, Q-05, Q-07, Q-12, Q-22, Q-23 |
| Authorization semantics | yes | Q-04, Q-05, Q-10, Q-11, Q-16, Q-19 |
| Credential lifecycle (create → use → revoke → expire → prune) | yes | Q-06, Q-12, Q-13, Q-14, Q-16, Q-17, Q-21 |
| Secret handling & security | yes | Q-15, Q-24, Q-26, Q-28 (NFR-002), Q-27 |
| Storage & migrations | yes | Q-07, Q-20, Q-21, Q-30 |
| Observability (logs, events, audit) | yes | Q-08, Q-20, Q-23, Q-28 (NFR-004), Q-29 |
| Public API & contract/versioning | yes | Q-19, Q-24, Q-26, Q-28 (NFR-003) |
| Configuration | yes | Q-13, Q-17, Q-21, Q-25 |
| Concurrency / reliability | yes | Q-27, Q-28 (NFR-005) |
| Performance | yes | Q-14, Q-28 (NFR-001) |
| Test strategy & evidence | yes | Q-29, Q-28 |
| Schedule & overlap | yes | Q-31, Overlap check below |
| Frontend / UI | skipped | Fixed out of scope at P.1 ("frontend UI for key management"); no question needed. |
| Multi-tenancy / per-org keys | skipped | Fixed out of scope at P.1. |
| OAuth2 / OIDC / JWT / mTLS / request signing | skipped | Fixed out of scope at P.1; Q-01 keeps the transport question open instead. |
| Outbound webhooks / third-party integrations | skipped | Fixed out of scope at P.1 (the notifications TODO owns outbound delivery; Q-31 covers the ordering). |

## Closed from evidence (no question needed)

| Point | Evidence |
|---|---|
| There is no HTTP layer and no server dependency in the repo. | `grep -rni "fastapi\|flask\|starlette\|uvicorn\|aiohttp" pyproject.toml src` → no match; runtime deps `pyproject.toml:8-24` (`dependencies = [` at line 8). |
| Two approved specs exclude an HTTP layer normatively. | `docs/specs/authentication.md:15`; `docs/specs/session-management.md` Constraints ("Backend-only in-process service — no HTTP/REST layer, no frontend"). |
| Adding a new feature's catalog actions does **not** break the closed-catalog acceptance test. | `tests/acceptance/permissions/test_check_api.py:1001-1035` builds its own `PermissionCatalog` from the six original features and asserts exactly 60 keys; `search.search` was added the same way without amending `user-roles-permissions.md`. |
| The catalog is closed after startup; keys must match `^[a-z0-9_-]+\.[a-z0-9_-]+$` and start with `<feature>.`; read API is `has` / `features` / `actions(feature=None)`. | `src/backend/permissions/catalog.py`. |
| The live catalog holds 61 actions across 7 features (authentication 11, usermanagement 11, settings 19, filemanagement 10, sessionmanagement 6, mail 3, search 1). | each `src/backend/<feature>/feature_actions.py` + `src/main.py` registration. |
| Permission management is **not** permission-enforceable today (no `feature_actions.py` in `backend/permissions`), so an agent cannot manage roles/grants. | `ls src/backend/permissions/` → `feature_settings.py` only. |
| The permission check order and the closed denial-reason set. | `src/backend/permissions/service.py:344-418` (shape → user lookup → session → catalog membership → grants), reasons `malformed_permission`, `unknown_user`, `inactive_user`, `storage_error`, `invalid_session`, `session_principal_mismatch`, `unknown_permission`, `unauthorized`; denial → WARNING log + `PermissionDenied` event (REQ-020). |
| `Principal(session_token=…)` is currently dead at the composition root: no `session_lookup` is wired. | `src/main.py:145-153` (no `session_lookup` argument) + `src/backend/permissions/service.py:407-408` (`return "storage_error"` fail-closed). |
| Grant grammar already allows `<feature>.*` wildcards. | `src/backend/permissions/service.py:78-90, 485-495`. |
| There is no "effective permissions for a user" API; it must be computed from `UserRead.roles` × `get_role_permissions(role)` × `catalog.actions()`. | `src/backend/permissions/service.py:192, 262` (only `list_permissions` and `get_role_permissions`). |
| Token helpers are public and reusable. | `src/backend/authentication/tokens.py` (`new_token`, `hash_token`), exported at `src/backend/authentication/__init__.py:62, 108-109`. |
| The `sessions` table is the template shape for a hashed-token table, and the raw token appears in exactly one return type. | `src/backend/authentication/models.py` (`Session`), `LoginResult.token` vs `SessionInfo`. |
| Session-management forbids activity tracking for sessions — a direct conflict with `last_used_at` if the table were shared. | `docs/specs/session-management.md` Constraints ("no activity tracking, no `last_seen_at`, no `expires_at` updates"). |
| New public classes must be traced by default; the traced-class inventory is a hand-maintained list, so adding a feature is additive. | `docs/specs/logging-coverage.md` REQ-001/REQ-012; `tests/logging_coverage_test_helpers.py:53-61`; `tests/acceptance/logging_coverage/test_inventory.py`. |
| `tests/architecture/` does not exist; Phase 6 boundary checks are manual. | `ls tests/` (no `architecture/`); `docs/workflow/PROBLEMS.md` P-32. |
| Coverage floor is 92%; CI runs `ruff check .`, `mypy src/`, `deptry`, `alembic upgrade head`, the docs build, and the traceability script. | `pyproject.toml:105-107`; `.github/workflows/`. |
| ADR numbering continues from **ADR-081**. | `ls docs/decisions/` → highest is `ADR-080-additive-session-repository-list-all.md`. |

## Impact Analysis (P.2) — draft for P.4

Every touch is **additive** unless the answer to Q-03 or Q-08 says otherwise (those two are the escalation triggers).

| Feature / component | What changes | Existing REQ/AC touched |
|---|---|---|
| `apikeys` (new, `src/backend/apikeys/`) | New feature package: models + repository ABC/SQLite concrete, `ApiKeyService` (create/list/revoke/revoke-all/resolve/call/capabilities/describe/list-calls/cleanup), `feature_settings.py`, `feature_actions.py`, `search_source.py`, errors, events, module singleton. | none (all new IDs) |
| `user-roles-permissions` | New `apikeys.*` actions declared by api-keys' own `feature_actions.py` (ADR-079 pattern). No change to `PermissionService`, `PermissionCatalog`, `Principal`, or `requires_permission` **unless Q-03 = B**, which amends REQ-025/EDGE-022 and forces a spec amendment. | none (Q-03 = A/C); REQ-004/REQ-005/REQ-025 + EDGE-022 if Q-03 = B |
| `authentication` | Reuse only: `new_token`, `hash_token`, the hashed-token table shape, the show-once pattern. No code change **unless Q-07 = B** (then the `Session` table + `SessionRepository` ABC grow, NFR-003 additive-ABC, ADR-080 precedent). | none (Q-07 = A/C); REQ-006/REQ-007/NFR-003 if Q-07 = B |
| `session-management` | No change. It is the structural template (idempotent revoke, bounded list, `cleanup_expired`, no-new-exceptions, event-driven reactions) and the boundary this change must not blur. | none |
| `user-management` | Consumes `UserDeleted` / `UserDeactivated` events inside api-keys (ADR-064 pattern). No `UserManager` change. | none |
| `search` | api-keys registers `build_apikey_source(repo)` at the composition root (ADR-077 / REQ-022 pattern). No search code change. | none |
| `settings` / `settings-coverage` | New `apikeys.*` settings registered via feature-owned `register_settings`; must satisfy REQ-017/REQ-018/REQ-019 (prefix, category/group, inventory). | none (additive; conventions must be respected) |
| `eventbus` | New events published; new subscriptions to user-management events. No bus change. | none |
| `logging` / `logging-coverage` | `@logged_class(include_args=False)` on the service and repositories; additive entries in `tests/logging_coverage_test_helpers.py` and `test_secret_args.py`. REQ-012 (new public classes traced) is satisfied, not amended. | none |
| `shared` | No change (Q-03 = A/C). | none; REQ-025 if Q-03 = B |
| `mail`, `profiling`, `file-management` | No change. | none |
| Composition root `src/main.py` | Additive wiring: `register_actions`, `register_settings`, repository + service construction (lazy-proxy pattern for cycles), search source registration. | none |
| `migrations/` | One new alembic revision (`api_keys`, `api_key_calls`) + `backend.apikeys.models` import in `migrations/env.py`. | n/a |
| `frontend` | None (out of scope at P.1). | n/a |

**Escalation verdict (P.2 recommendation):** reclassify to **CROSS-CUTTING** now (Q-02 = B) — new shared capability + new cross-feature interface, all touches additive, spec carries the §12-style Impact Analysis above; branch `crosscut/api-keys`; bump `minor`.

## Overlap check (P.2)

Checked against all 13 files in `docs/specs/` and all 16 items in `docs/todo/`, plus in-flight worktrees/branches/PRs (2026-10-03).

**Specs — no spec owns API keys, credentials outside sessions, or an audit trail.** Adjacent-but-distinct:

| Spec | Relationship | Verdict |
|---|---|---|
| `user-roles-permissions.md` | the closed catalog, the grant grammar, `Principal`, `@requires_permission`, the closed denial-reason set, `PermissionDenied` | reuse, additive actions only; **amendment only if Q-03 = B** |
| `authentication.md` | REQ-006/REQ-007 hashed opaque tokens, REQ-021 show-once representations, `InvalidSessionError`, the `sessions` table | reuse; **amendment only if Q-07 = B** |
| `session-management.md` | the closest structural template (list + idempotent revoke + `cleanup_expired` + cap + no-new-exceptions) and the "no second session store" / "no activity tracking" boundary | pattern reuse; must not share the table (Q-07) |
| `user-management.md` | owner lookup (`UserRead.roles`), `UserDeleted`/`UserDeactivated` events | reuse, no amendment (Q-12) |
| `search.md` | the read/query surface, additive source pattern (ADR-077), pagination/filter conventions, NFR-001 environment-aware precedent | reuse (Q-22), no amendment |
| `settings.md` / `settings-coverage.md` | feature-owned registration, live reads, key prefix/category/group/inventory (REQ-017/018/019) | reuse (Q-25), no amendment |
| `event-bus.md` | publish/subscribe, at-most-once, handler isolation, structural `EventPublisher` | reuse (Q-23), no amendment |
| `logging.md` / `logging-coverage.md` | `@logged_class`/`@logged` policy, `include_args=False`, secret-free records, REQ-012 forward policy | reuse (Q-28/Q-29), no amendment |
| `mail-service.md` | none (no outbound delivery in this change) | none |
| `profiling.md` | unrelated | none |
| `template.md` | spec format only | n/a |

**TODOs — overlap findings:**

| TODO | Finding |
|---|---|
| `notifications.md` | **The one real coupling, and it is reciprocal.** Its Q-11 asks whether notifications depends on api-keys; this file's Q-31 answers the mirror. Recommendation: **no dependency in either direction** — api-keys ships first (self-contained), notifications ships its in-process read API and defers its consumer. Both TODO files should record it. |
| `structlog-logging.md` | **Ordering cost, no conflict.** It swaps the logging backend behind an unchanged public API and re-derives 17 log-assertion test files. api-keys uses only the public logging API, so either order works, but api-keys' log-assertion tests would join that set if it lands first. |
| `tenacity-rich-cachetools.md` | **Do not couple.** Its retry/caching items are the tempting fix for Q-18/Q-27, but it is scored 2/5 and unscheduled; the spec must not assume a limiter or cache exists. |
| `structure-map.md` | **No conflict, mild adjacency.** It generates a repo map + CLI; api-keys adds a package it will later map. No shared files. |
| `python-3.15.md`, `pyproject-tooling-gaps.md`, `security-changelog-license.md`, `update-readme.md`, `docs-path-ci-trigger.md`, `spec-interview-protocol.md`, `split-archived-qa.md`, `workflow-docs-nits.md`, `remove-spec-tdd-driver.md`, `value-triage-gate.md`, `track-python-skill.md` | No overlap with a backend credential feature (tooling, docs, CI, process changes). |

**In-flight state (checked 2026-10-03):** `git worktree list` → primary (`main`) + `chore/remove-spec-tdd-driver`; `git branch -a` → `main`, `chore/remove-spec-tdd-driver`; `gh pr list --state open` → **PR #62** (chore, deletes the unused spec-tdd driver, OPEN). No in-flight change touches `src/backend/`, so there is no branch conflict with api-keys.

## For P.4 (what the answers change)

- **Surface & classification (Q-01, Q-02, Q-30):** whether the spec is FEATURE or CROSS-CUTTING (Impact Analysis §12 mandatory), whether a new boundary package exists, whether any dependency/ADR/CI/deptry work is in scope, and the bump level (`minor` for CROSS-CUTTING non-breaking).
- **Authorization model (Q-03, Q-04, Q-05, Q-10, Q-11, Q-19):** the `resolve_key` seam, whether `Principal`/`user-roles-permissions.md` must be amended, the scope-check location, the scope grammar, and the seven catalog action names (permanent vocabulary).
- **Data model (Q-07, Q-13, Q-14, Q-17, Q-20, Q-21):** the `api_keys` and `api_key_calls` columns, whether `last_used_at` is a column or a derived value, the retention rule, and the single alembic revision + `migrations/env.py` import.
- **Lifecycle & security (Q-06, Q-12, Q-15, Q-16, Q-24, Q-27):** the bootstrap trust rule (a key may never mint keys), the revocation cascade, the key format and the "hash the whole presented string" rule, the owner/admin rules, the error contract, and the fail-closed audit-write decision.
- **Agent-facing surface (Q-09, Q-22, Q-26):** `describe_actions`/`key_capabilities` shapes, the introspection-based schema derivation and its documented limits, the search source fields, and the show-once representation rule.
- **Normative inventories (Q-19, Q-23, Q-25):** the catalog action list, the published-event list, and the settings inventory — each becomes REQ/AC/EDGE rows with a test.
- **Out of scope (Q-08, Q-18):** the shared-audit and rate-limiting deferrals, stated explicitly so a later change can absorb them additively.
- **Test strategy (Q-28, Q-29):** the five test directories under `tests/*/apikeys/`, `tests/apikeys_test_helpers.py`, the additive logging-coverage inventory entries, the Hypothesis strategies for the four invariants, and the environment-aware NFR budgets.
- **Schedule (Q-31):** the reciprocal `Depends on:` note in `docs/todo/api-keys.md` and `docs/todo/notifications.md`.
- **ADRs (from P.4 onward):** numbering starts at **ADR-081**; expected ADRs — the key→`Principal` seam (new pattern, cross-feature interface), the separate `api_keys` store (rejected: reuse the `sessions` table), the introspection-based tool-schema export (new pattern), and the api-keys-owned audit log (rejected: shared audit capability).

## Late questions (Phases 2–6)

_(none yet — the orchestrator appends entries here, with `Step:` set to the step that found the question.)_

## Prep log

| Step | Date | Result |
|---|---|---|
| P.1 Frame | 2026-10-03 | TODO + question file created on `main`; type FEATURE (escalation candidate CROSS-CUTTING); todo set created; **value triage 5/5, implement** |
| P.2 Interrogate (31 questions) | 2026-10-03 | 31 questions recorded in one `BLOCKED-USER` batch (≥ 20 floor met); 14 coverage categories covered, 3 skipped as P.1-fixed scope; 16 points closed from evidence; Impact Analysis drafted (all touches additive under the recommended answers); escalation verdict = **CROSS-CUTTING**; overlap checked against 13 specs + 16 TODOs + PR #62 |
| P.3 Answer (<n> answered) | | |
| P.4 Draft spec + create branch/worktree | | |
| P.5 Self-consistency | | |
