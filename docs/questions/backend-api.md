# Questions: backend-api

One question file per change, created at **P.1 Frame** from this template and named `backend-api.md`. It replaces the retired central `AI_Questions.md` (archived at `docs/questions/archive-AI_Questions.md`).

- **Change:** backend-api (CROSS-CUTTING)
- **TODO file:** `docs/todo/backend-api.md`
- **Spec:** `docs/specs/backend-api.md`  <!-- created at P.4 -->
- **Opened:** 2026-10-08
- **Status:** OPEN  <!-- OPEN | ALL ANSWERED — set OPEN by the orchestrator at P.1; ALL ANSWERED once every question in this file has an answer (the orchestrator records it together with the `QUESTIONS-ANSWERED` TODO advance) -->
- **Answer rounds:** 1 (2026-10-10: Q-01, Q-02, Q-03, Q-07 answered)

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

_(The entries below use the field set of `docs/questions/api-keys.md`, the file this change was split from: `Step / Answer / Status / Date / Incorporated / Context / Why needed / Options / Recommendation`. The `Question:` line is the entry's heading.)_

## Decided before P.2 (from the `api-keys` P.3 round, 2026-10-08)

These are settled and MUST NOT be re-asked; P.2 builds on them:

1. **Transport:** a real HTTP API — **FastAPI + uvicorn** (new runtime dependency, new ADR). Not an in-process tool API, not a stdlib server.
2. **Change identity:** this is **the backend's API** (`backend-api`, CROSS-CUTTING), not an "api-keys" feature. The machine-credential half stays in the `api-keys` TODO, which now depends on this change.
3. **Authentication:** the backend's **own session tokens** (`AuthService.login()` → Bearer token → `Principal(user_id, session_token)`). No new credential type, no `Principal` change, no new seam.
4. **Authorization:** the **owner's existing roles** decide, through `@requires_permission` and the closed 61-action catalog. **No per-credential scope list in v1.**
5. **v1 surface:** **all 61 enforced catalog actions** (authentication 11, usermanagement 11, settings 19, filemanagement 10, sessionmanagement 6, mail 3, search 1).
6. **Spec governance:** the user **approved amending** `docs/specs/authentication.md` (line 15, "Out of scope: … HTTP/REST/GraphQL API layer") and `docs/specs/session-management.md` (Constraints, "no HTTP/REST layer, no frontend") — the amendments ride this change's PR.

## Preparation questions (P.2)

### Q-01 — Does the HTTP surface return the raw password-reset token?

- **Step:** P.2 (Phase P)
- **Answer:** **A** — `POST /auth/password-resets` returns **202 with no body**; the boundary suppresses the returned token. Delivery stays with `MailService.send_password_reset_email`; `complete_password_reset` stays callable with a token the client obtained out-of-band. No new cross-feature call, no new setting, no spec-ID change.
- **Status:** ANSWERED
- **Date:** 2026-10-10
- **Incorporated:** yes — to be written at P.4 as an EDGE + INV ("a reset token never appears in an HTTP response") and in the authentication Impact Analysis
- **Context:** Decision 5 puts `authentication.request_password_reset` in the v1 surface. `AuthService.request_password_reset` returns the **raw reset token to the caller** (authentication REQ-010/REQ-011; AGENTS.md: "returns the raw token exactly once for a registered email"), and the operation is one of the 7 **exempt** actions — `src/backend/authentication/service.py:243` takes `principal: Principal = _SYSTEM_PRINCIPAL`, so no permission is checked in-process.
- **Why needed:** Over HTTP that is account takeover by design: any caller who knows a registered email calls the endpoint, gets the reset token from the response body, and calls `complete_password_reset` (also exempt) with a new password. The in-process contract ("the token is returned once so the caller can deliver it out-of-band") silently becomes a public capability at the boundary. This is the single highest-risk mapping decision in the change.
- **Options:** A. expose `POST /auth/password-resets` as **202 with no body** — the boundary drops the returned token; delivery is only ever through the mail feature (`MailService.send_password_reset_email`), and `complete_password_reset` stays callable with a token the client obtained out-of-band. B. same, **plus** the API itself calls the mail feature on reset request (new cross-feature call, new behaviour not in either spec). C. return the token in the response (in-process parity; dev convenience). D. return the token only when a new setting `api.expose_reset_token` is true (default false). E. keep both reset actions out of the v1 HTTP surface (a documented exception to decision 5).
- **Recommendation:** A. The boundary suppresses the token; no new cross-feature call, no new setting, no spec-ID change (the service contract is untouched — the boundary simply does not echo a secret). Record it as an EDGE + INV ("a reset token never appears in an HTTP response") and in the authentication Impact Analysis.

### Q-02 — Is `usermanagement.verify_password` exposed over HTTP?

- **Step:** P.2 (Phase P)
- **Answer:** **B** — **withheld** from the HTTP surface. The deviation from decision 5 is recorded explicitly as an "not exposed over HTTP" list in the spec, with the reason (no lockout on an arbitrary `user_id` → password oracle) next to the endpoint table. No second authorization path is introduced.
- **Status:** ANSWERED
- **Date:** 2026-10-10
- **Incorporated:** yes — narrows decision 5 ("all 61 actions") to 60 exposed actions; to be written at P.4 in the v1-surface section
- **Context:** `UserManager.verify_password(user_id, password)` (`src/backend/usermanagement/services/usermanager.py:193`) is one of the 11 enforced usermanagement actions, so decision 5 puts it on the wire. The brute-force lockout (`AttemptTracker`, `authentication.max_failed_attempts`, authentication REQ-004) guards **`AuthService.login` only** — it keys on the login identifier, not on an arbitrary `user_id`.
- **Why needed:** `POST /users/{id}/verify-password` is a password oracle for **any** user id with **no** lockout, no tracker, and no rate limit (Q-14), reachable by any caller holding `usermanagement.verify_password`. It is a strictly better attack surface than `/auth/login`.
- **Options:** A. expose it (strict catalog parity). B. **withhold it from the HTTP surface** and record the deviation from decision 5 explicitly in the spec (an explicit "not exposed over HTTP" list). C. expose it only for the caller's own user id (a boundary rule the catalog cannot express — risks a second authorization path, which `docs/todo/backend-api.md` forbids). D. expose it but route the attempt through the authentication tracker.
- **Recommendation:** B. Withhold it, with the reason recorded next to the endpoint table, and keep the "no second authorization path" rule intact. Ask for confirmation because it narrows a settled decision (5).

### Q-03 — What does the boundary do about the 9 declared-but-unenforced actions?

- **Step:** P.2 (Phase P)
- **Answer:** **A** — every route requires a **valid session** except the session-establishment set (`login`, `begin_passkey_login`, `complete_passkey_login`, the two password-reset actions); `filemanagement.download` and `filemanagement.list_files` additionally call the **same** `PermissionService.require_permission(user_id, "filemanagement.download" | "filemanagement.list_files")` at the boundary — same checker, same catalog action string, not a second path.
- **Status:** ANSWERED
- **Date:** 2026-10-10
- **Incorporated:** yes — to be written at P.4 as the boundary authentication rule (INV candidate) + per-route table
- **Context:** 9 of the 61 declared catalog actions carry **no** `@requires_permission`: the 7 exempt authentication operations (`login`, `logout`, `session_info`, `request_password_reset`, `complete_password_reset`, `begin_passkey_login`, `complete_passkey_login` — `docs/specs/user-roles-permissions.md:358` D13/REQ-024/AC-030/EDGE-023; verified in `src/backend/authentication/service.py:198,230,237,243`) **plus** `filemanagement.download` and `filemanagement.list_files` (`src/backend/filemanagement/service.py:726` and `:810` cite ADR-071/AC-029: download performs no permission check; `list_files` returns `[]` under a denying checker). In-process that is safe because the caller is trusted code.
- **Why needed:** Over HTTP those two file actions become readable by **any** authenticated caller (or any caller at all, if the route is anonymous), and the exempt authentication actions become anonymously reachable endpoints. The TODO forbids a second authorization path, so the fix must be a deliberate, specified rule, not an ad-hoc guard.
- **Options:** A. **every route requires a valid session** except the session-establishment set (`login`, `begin_passkey_login`, `complete_passkey_login`, the two password-reset actions); the two filemanagement routes additionally call the same `PermissionService.require_permission(user_id, "filemanagement.download" | "filemanagement.list_files")` at the boundary (same checker, same catalog action — not a second path). B. session required as in A, but **no** boundary check for the two file actions (any authenticated user may download/list any key). C. mirror the service exactly (those two routes anonymous). D. withhold `filemanagement.download` / `list_files` from v1.
- **Recommendation:** A. It keeps the catalog as the single source of truth (the same action string, the same checker) and closes the hole; the exempt authentication set stays exempt because a session cannot exist before login.

### Q-04 — How does the boundary turn a Bearer token into `Principal.user_id`?

- **Step:** P.2 (Phase P)
- **Answer:** PENDING
- **Status:** PENDING
- **Date:** 2026-10-08
- **Incorporated:** no
- **Context:** `PermissionService._check` resolves the principal from `user_id` and only *validates* the token against it (`src/backend/permissions/service.py:407-430`: `record.user_id != user_id` → `session_principal_mismatch`; `_validate_session` returns `None` when the token is `None`). `_evaluate_grants` with `user is None` is the **system principal** path (D10/REQ-018: the configurable system set). So `Principal(user_id=None, session_token=t)` would evaluate grants against the **system set**, not the user's roles.
- **Why needed:** The boundary must resolve `token → user_id` itself, and which seam it may use is a cross-feature interface decision (and a per-request cost decision: `session_info` + the check's own validation = two hashed session lookups per request).
- **Options:** A. `AuthService.session_info(token)` (public, exempt, returns `SessionInfo(user_id, created_at, expires_at)`, raises `InvalidSessionError`) — one extra lookup, no new seam. B. `SessionRepository.get_by_token_hash` directly (a cross-feature internal import; violates the `public-api-import-boundary` TODO rule). C. add a new public read (e.g. `resolve_principal(token)`) to authentication or session-management — a new cross-feature interface, so a spec amendment. D. cache the resolution per request only (no cross-request cache — REQ-014 forbids caching role/activity state).
- **Recommendation:** A, with the double validation kept (the check must still see the token so `session_principal_mismatch`/revocation/expiry stay authoritative). Record the two-lookup cost in the NFR section (Q-27) against user-roles-permissions REQ-029 (`check < 5 ms` median).

### Q-05 — Route ↔ action mapping: REST resources or action-RPC, and what guards drift?

- **Step:** P.2 (Phase P)
- **Answer:** PENDING
- **Status:** PENDING
- **Date:** 2026-10-08
- **Incorporated:** no
- **Context:** The acceptance signal in `docs/todo/backend-api.md` is REST-shaped (`POST /auth/login`, `GET /users`), while the permission catalog is action-shaped (`feature.action`, 61 entries, closed at startup, REQ-004/REQ-005). Nothing in the repo connects the two today.
- **Why needed:** This decides the size of the diff (61 hand-written handlers vs one dispatcher), the OpenAPI document's quality, and whether the API can silently drift from the closed catalog (an endpoint with no action, or an action with no endpoint).
- **Options:** A. hand-written REST routes, one per action, **plus** a contract test asserting exact catalog ↔ route parity (every catalog action maps to exactly one route, every route maps to a declared action, unknown ids 404). B. action-RPC: one dispatcher (`POST /actions/{feature}.{action}`) generated from a table — minimal code, exact parity, poor OpenAPI/REST ergonomics. C. hybrid: REST routes for the resource-shaped majority, generated parity test as in A. D. REST routes with no parity test.
- **Recommendation:** A (or C if the handler count proves unwieldy at S2.2), with the parity test as a normative invariant (INV candidate) — it is the mechanism that keeps "the catalog stays the single source of truth" testable.

### Q-06 — The file/avatar URL: which route path, and can an `<img>` fetch it?

- **Step:** P.2 (Phase P)
- **Answer:** PENDING
- **Status:** PENDING
- **Date:** 2026-10-08
- **Incorporated:** no
- **Context:** file-management REQ-018 / AC-039 / AC-040 and D7 pin the avatar URL to `https://<filemanagement.avatar_base_url>/files/<file_id>` (default base `files.example.com`, host only, scheme fixed https). `FileService.download(key) -> bytes` and `open(key) -> BinaryIO` are the reads; `filemanagement.download` is one of the two unenforced actions (Q-03).
- **Why needed:** Two couplings the spec does not resolve: (1) the API's file route path must be exactly `/files/{file_id}` for the already-specified avatar URL to resolve, or `avatar_base_url` must carry a path prefix (which REQ-018's "host only" wording forbids); (2) a browser `<img src>` cannot send an `Authorization: Bearer` header, so the specified URL is unusable unless the GET file route is anonymous or accepts a credential in the URL.
- **Options:** A. pin the public GET route to `/files/{file_id}` and make it **anonymous** (avatars are public by design; but that also exposes every file key, not just avatars). B. pin `/files/{file_id}` and require Bearer (the specified avatar URL then only works for API clients, not browsers). C. pin `/files/{file_id}` plus a separate anonymous `/avatars/{user_id}` route that serves only avatar files (needs an avatar lookup — `get_avatar(user_id)` exists). D. short-lived signed URLs (new capability, new settings, new secrets).
- **Recommendation:** A for the avatar case only via C's route: pin `/files/{file_id}` for Bearer clients **and** add `/avatars/{user_id}` (anonymous, avatar-only, `get_avatar`) — record which of the two the REQ-018 URL is meant to point at, since AC-039 asserts the URL shape, not its auth.

### Q-07 — Where does the app factory live, given `src/main.py`'s import side effects?

- **Step:** P.2 (Phase P)
- **Answer:** **B** — **wait for `composition-root-factory`** and build on its `create_app()`. A `Depends on:` edge is added to `docs/todo/backend-api.md`; `backend-api` may not pass P.4 until that change is merged. The recommendation against this (a 4/5 blocker waiting behind a 3/5 REFACTOR) was presented and the user chose the sequencing anyway — no duplicate container, one composition root.
- **Status:** ANSWERED
- **Date:** 2026-10-10
- **Incorporated:** yes — `docs/todo/backend-api.md` `Depends on:` now lists `composition-root-factory`; Q-07's shape is that change's, not this one's
- **Context:** `src/main.py` is 221 lines of **module-level** wiring (`_catalog` :82, cycle proxies :130-131, `_settings_registry` :137, service globals :145,153,181,186,194,201,202,212) that opens SQLite repositories and creates files under `./data/` at **import** time — which is why `tests/acceptance/settings_coverage/test_wiring.py` runs `main.py` in a subprocess. `docs/todo/composition-root-factory.md` (PREPARING, REFACTOR) wants exactly a `create_app()`/`build_services()` there, and may need a `docs/specs/settings-coverage.md` REQ-002/AC-003 amendment.
- **Why needed:** A FastAPI app needs the object graph (services, registry, permission service, search sources) without importing a module that writes to disk, and tests need a graph built from in-memory repositories. This is the direct collision point with the `composition-root-factory` TODO.
- **Options:** A. `create_app(deps)` inside `src/backend/api/` taking an explicit dependency container; `src/main.py` stays the only production wiring and calls it; tests build their own container. B. wait for `composition-root-factory` (add a `Depends on:` edge) and build on its `create_app()`. C. build the graph inside the api package (duplicates `main.py` — two graphs, drift guaranteed). D. put `create_app()` in `src/main.py` (keeps one graph, but the api package then depends on `main`).
- **Recommendation:** A now (no dependency edge), with the overlap recorded in the spec's Impact Analysis and a note that `composition-root-factory` may later move the container without changing `create_app`'s signature.

### Q-08 — The `api.*` settings family, and how the server learns host/port

- **Step:** P.2 (Phase P)
- **Answer:** PENDING
- **Status:** PENDING
- **Date:** 2026-10-08
- **Incorporated:** no
- **Context:** settings-coverage REQ-017 (key prefix = full feature name), REQ-018 (category = domain, group = feature name), REQ-019 (the complete inventory lives in spec §3.5), and REQ-021 (**the settings feature performs no environment-variable handling**). Existing families: `logging.*`, `authentication.*`, `usermanagement.*`, `eventbus.*`, `filemanagement.*`, `search.*`, `sessionmanagement.*`, `mail.*`, `permissions.*`. Note: spec §3.5 (`docs/specs/settings-coverage.md:151-164`) lists only 14 keys and is already stale vs. the code, and `tests/contract/settings_coverage/test_inventory.py` asserts only that its own 14 keys exist (additive-safe), while `test_no_secret_settings` (NFR-002) fails on any listed key containing `password`/`secret`.
- **Why needed:** uvicorn needs a bind host/port **before** the app (and therefore the settings registry) exists, and the settings feature refuses to read env vars. Which values are live-read vs. startup-only is also unspecified: `api.docs_enabled`, `api.max_body_size`, `api.cors_origins` can be live; `api.bind_host`/`api.bind_port` cannot be (changing them at runtime does nothing).
- **Options:** A. all `api.*` values in settings (category `application`/`security`, group `api`), read by a launcher entry point (`python -m backend.api`) that builds the registry, then calls `uvicorn.run(app, host=…, port=…)` — settings stay the single source of truth. B. settings for runtime-tunable values only; host/port from the uvicorn CLI (two sources of truth). C. env vars (contradicts REQ-021). D. no `api.*` family at all — hardcoded defaults.
- **Recommendation:** A. Also decide whether the startup-only keys are marked in the view (so the UI cannot pretend they are live), and whether `api.*` keys join the contract test's INVENTORY (they must not contain `password`/`secret`).

### Q-09 — Process and concurrency model: is "exactly one process" normative?

- **Step:** P.2 (Phase P)
- **Answer:** PENDING
- **Status:** PENDING
- **Date:** 2026-10-08
- **Incorporated:** no
- **Context:** The whole object graph is in-process state: `InMemoryAttemptTracker` (lockout), the event bus worker (one per process, `eventbus.max_queue_size`), the search source registry, the settings registry's in-memory values, the CAP eviction state. user-roles-permissions REQ-027 requires thread-safe checks; REQ-029 budgets a check at < 5 ms median.
- **Why needed:** `uvicorn --workers N` / multiple replicas silently break lockout, event delivery and source registration. The spec must state the deployment constraint (INV) and whether route handlers are `def` (run in the anyio threadpool, so the sync services never block the event loop) or `async def` (would block the loop on SQLite/argon2 work).
- **Options:** A. normative single process; handlers are sync `def` (threadpool); threadpool size a setting. B. allow N workers and accept the degraded state (documented). C. require sticky/external state (out of scope).
- **Recommendation:** A, as an INV with a test that the app refuses to start (or warns loudly) when it detects more than one worker — or simply a documented constraint if a detection mechanism is judged out of scope.

### Q-10 — Do request/response bodies reuse the features' Pydantic models?

- **Step:** P.2 (Phase P)
- **Answer:** PENDING
- **Status:** PENDING
- **Date:** 2026-10-08
- **Incorporated:** no
- **Context:** The features already ship validated models: `LoginRequest`, `PasswordResetComplete`, `PasskeyRegistrationBegin/Complete`, `SearchQuery` (with nested `FilterGroup`/`Sort`), `UserCreate/UserUpdate/UserRead`, `SettingDefinition`, `EmailTemplate`, `AvatarRead`, `SessionEntry`. authentication REQ-019 pins schema-level validation via Pydantic; the "show-once representation" pattern (api-keys Q-26) already governs reads.
- **Why needed:** Reusing them means zero drift but makes every feature model change an **API-breaking** change (and puts feature models in the public OpenAPI schema); API-layer DTOs decouple the wire format but duplicate ~30 models and can drift. `get_value/set_value(key, value: Any)` and `SearchResultItem.fields: dict[str, Any]` additionally have no schema at all.
- **Options:** A. reuse the feature models as request/response bodies; pin the wire schema with contract tests. B. API DTOs for everything. C. reuse reads (representations), DTOs only for writes where the in-process signature is HTTP-hostile (`upload`, `list_sessions(token=…)`, `set_value`).
- **Recommendation:** A, with C's exceptions where the signature cannot be expressed (Q-12, Q-21). Record the "feature model change = API change" consequence as an NFR/migration rule.

### Q-11 — Exception → status mapping, and how much of the `reason` reaches the client?

- **Step:** P.2 (Phase P)
- **Answer:** PENDING
- **Status:** PENDING
- **Date:** 2026-10-08
- **Incorporated:** no
- **Context:** Eight hierarchies exist, all with short secret-free `reason` strings: `authentication.errors` (`InvalidCredentialsError`, `InvalidSessionError`, `InvalidResetTokenError` with `unknown`/`expired`/`used`, `PasskeyCredentialNotFoundError`, `InvalidPasskeyResponseError`, `PasskeyHijackError`), `filemanagement.errors` (6 subclasses incl. `FileTooLargeError`, `FileTypeNotAllowedError`, `FileValidationError`), `mail.errors` (3), `permissions.errors` (`PermissionDeniedError` with the closed D12 reason set: `malformed_permission`, `unknown_user`, `inactive_user`, `invalid_session`, `session_principal_mismatch`, `unknown_permission`, `unauthorized`, `storage_error`, …), `search.errors` (3), `usermanagement.errors` (4), `settings.exceptions` (7). **sessionmanagement has no errors module of its own** (it re-raises `InvalidSessionError` and bare `ValueError` for `list_sessions`'s "exactly one of token/user_id" and `limit < 1`).
- **Why needed:** Without one mapping table each route invents a status, and the closed denial-reason set leaks enumeration signals (`unknown_user` vs `inactive_user` tells a caller which usernames exist). Bare `ValueError` from sessionmanagement must not become a 500.
- **Options:** A. one boundary-level mapping table: 401 for `invalid_session`/`session_principal_mismatch`/`InvalidSessionError`; 403 for `unauthorized`/`unknown_permission`/`inactive_user`/`unknown_user` (deliberately merged to kill enumeration); 404 for the not-found class; 409 for the conflict class (`UserAlreadyExistsError`, `RoleInUseError`, `LastAdminError`); 422 for validation (`ValidationError`, `MalformedQueryError`, `SettingsValidationError`, bare `ValueError` from service contracts); 413 for `FileTooLargeError`; 500 for `storage_error`/`StorageError` — with a stable machine-readable `code` field and no internals. B. minimal (400/403/404/500, no reason). C. verbatim reason passthrough (debuggable, leaks the closed set's user-state distinctions).
- **Recommendation:** A, with the exact table normative (an EDGE per class) and the merged 403 group justified by user enumeration.

### Q-12 — File upload wire format (and the path-source hazard)

- **Step:** P.2 (Phase P)
- **Answer:** PENDING
- **Status:** PENDING
- **Date:** 2026-10-08
- **Incorporated:** no
- **Context:** `FileService.upload(source: str | bytes | BinaryIO, key=None, namespace="general", original_filename=None, declared_mime_type=None, uploader=None)` — a **filesystem path** is a valid in-process source. `upload_avatar(user_id: str, source)` / `replace_avatar(user_id: str, source)` take `user_id` as a **str**, while every other user id in the repo is a `UUID`.
- **Why needed:** A path source over HTTP would let a client read arbitrary server files (`upload("/etc/passwd")`, `upload("./data/users.db")`) — the boundary must forbid it explicitly. The body format also decides a dependency: multipart needs `python-multipart` (new runtime dep).
- **Options:** A. `multipart/form-data` with `UploadFile` (needs `python-multipart`), metadata as form fields. B. raw request body (`PUT /files/{key}` with `Content-Type`), metadata as query params — no new dep. C. base64 in JSON (simple, +33% size, memory pressure). D. A for files, and for avatars the same, with `user_id` typed as UUID at the boundary and converted once.
- **Recommendation:** A + D's UUID conversion at the boundary, and an explicit INV: "an HTTP upload never accepts a filesystem path" (the boundary constructs the source as a stream only).

### Q-13 — Request body size cap (uvicorn/starlette impose none)

- **Step:** P.2 (Phase P)
- **Answer:** PENDING
- **Status:** PENDING
- **Date:** 2026-10-08
- **Incorporated:** no
- **Context:** `filemanagement.max_file_size` (default 10 MiB) and `filemanagement.avatar_max_size` are validated **after** the content is read into memory (`FileTooLargeError`), and the settings/mail/search bodies are unbounded. Starlette does not cap request body size.
- **Why needed:** An authenticated (or, per Q-03, anonymous) caller can exhaust memory with an unbounded body before any feature validation runs. This is the boundary's own NFR, not a feature's.
- **Options:** A. a boundary middleware with `api.max_body_size` (reject over-limit with 413 using `Content-Length` plus a streaming byte count). B. rely on the feature limits (memory risk). C. cap only the upload routes.
- **Recommendation:** A, with the relationship to `filemanagement.max_file_size` stated (the boundary cap is the outer limit; the feature cap stays the domain rule).

### Q-14 — Rate limiting / abuse control at the boundary in v1?

- **Step:** P.2 (Phase P)
- **Answer:** PENDING
- **Status:** PENDING
- **Date:** 2026-10-08
- **Incorporated:** no
- **Context:** `docs/todo/backend-api.md` lists rate limiting as an open question; `docs/questions/api-keys.md` Q-18 asks the same for the machine-credential half and explicitly defers it to this change. Today the only throttle is the authentication `AttemptTracker` (in-memory, login-only).
- **Why needed:** It decides whether this change owns the mechanism (and api-keys then reuses it) or both changes document "no limiter, reverse proxy required". A per-session limiter is cheap in-process; a distributed one is not.
- **Options:** A. none in v1; documented as requiring a reverse proxy (recorded as an NFR limitation). B. a simple in-process per-session/per-IP token bucket with `api.rate_limit_*` settings (new INV: per-process only, meaningless behind N workers — see Q-09). C. limiter for the authentication routes only (login, password reset).
- **Recommendation:** A for v1 (lazy, honest, no false sense of safety), with the limitation recorded as an NFR and the decision echoed into api-keys Q-18 so that change stops asking.

### Q-15 — Security defaults: bind address, CORS, `/docs`

- **Step:** P.2 (Phase P)
- **Answer:** PENDING
- **Status:** PENDING
- **Date:** 2026-10-08
- **Incorporated:** no
- **Context:** ruff's `S` (bandit) rules are active and `B104` (hardcoded bind to all interfaces) is in the `B` set; CI runs `ruff check .` on every PR (`lint.yml`). FastAPI ships `/docs`, `/redoc`, `/openapi.json` by default. `authentication.origin` (default `http://localhost:3000`) and `authentication.rp_id` (`localhost`) already exist for WebAuthn, not for CORS.
- **Why needed:** The defaults decide whether a default deployment is internet-exposed, whether a browser SPA may call it, and whether the API's shape is public.
- **Options:** A. bind `127.0.0.1` by default; CORS middleware installed **only** when `api.cors_origins` is non-empty (default empty); `/docs` + `/openapi.json` enabled by default with `api.docs_enabled` to disable. B. same but docs disabled by default. C. bind `0.0.0.0` (fails B104 and the security posture).
- **Recommendation:** A, with the OpenAPI document treated as a deliverable (Q-28) and the bind default justified in the spec so no one "fixes" it to `0.0.0.0`.

### Q-16 — Are `settings.register` / `register_feature` exposed over HTTP?

- **Step:** P.2 (Phase P)
- **Answer:** PENDING
- **Status:** PENDING
- **Date:** 2026-10-08
- **Incorporated:** no
- **Context:** 19 settings actions are in the v1 surface, including `settings.register` and `settings.register_feature`, which take `SettingDefinition` objects — code-level declarations that today happen only at startup (settings REQ-001/REQ-002, feature-owned `register_settings`).
- **Why needed:** Exposing them lets a remote client inject new setting definitions into the running process (kind/default/category), i.e. mutate the application's own schema, and `SettingDefinition` has no natural JSON representation contract. It is the one action pair whose in-process meaning does not survive translation.
- **Options:** A. expose all 19 (parity). B. withhold `settings.register` and `settings.register_feature` (definitions are code, not data) and expose the other 17. C. expose them admin-only (the catalog already implies that via `settings.register` grants).
- **Recommendation:** B, recorded as a documented exception next to Q-02's, so the "all 61" decision has an explicit, small, justified remainder list.

### Q-17 — Is `mail.send_email` with a client-supplied template exposed?

- **Step:** P.2 (Phase P)
- **Answer:** PENDING
- **Status:** PENDING
- **Date:** 2026-10-08
- **Incorporated:** no
- **Context:** `MailService.send_email(to, template: EmailTemplate, context: dict[str, str])` (`src/backend/mail/service.py:143`) takes a **caller-authored** `EmailTemplate` (`name`, `subject`, `body_html`, `body_text`, `{{variable}}` placeholders, HTML-escaped substitution). The two high-level operations (`send_password_reset_email` :181, `send_email_verification_email` :190) use built-in templates.
- **Why needed:** Over HTTP that is an authenticated mail relay with arbitrary subject and HTML body — a phishing/abuse vector and a deliverability risk, and mail-service's spec assumes the template comes from feature code.
- **Options:** A. expose all 3 (parity). B. expose only the two high-level template operations; withhold the core `send_email`. C. expose the core but only with templates registered server-side (a named-template allowlist — new capability, not in the mail spec). D. expose the core, admin-only by grant (the catalog already allows that).
- **Recommendation:** B for v1 (D is acceptable if the user wants parity), with the reason recorded; note that withholding `mail.send_email` also withholds the capability api-keys and notifications would later want.

### Q-18 — Role and grant management stays out of HTTP: how is an API client ever granted anything?

- **Step:** P.2 (Phase P)
- **Answer:** PENDING
- **Status:** PENDING
- **Date:** 2026-10-08
- **Incorporated:** no
- **Context:** `docs/todo/backend-api.md` keeps role management (`create_role`, `grant_permission`, `assign_role`) out of the v1 surface, and `docs/specs/user-roles-permissions.md:17` lists permission management itself as out of scope for the catalog — `PermissionService` has **no** `@requires_permission` on any method (verified: zero decorators in `src/backend/permissions/service.py`) and `src/backend/permissions/` has no `feature_actions.py`. So there is no catalog action to hang such an endpoint on.
- **Why needed:** The acceptance signal ("an authenticated client can call endpoints according to its owner's roles") is untestable end-to-end unless the roles/grants can be set somehow. Today that is in-process only, which means the bootstrap path is "run Python".
- **Options:** A. out of scope for v1; document the in-process bootstrap (a script/CLI) in the spec's deployment section. B. add new catalog actions (`permissions.create_role`, `permissions.grant_permission`, …) — amends user-roles-permissions REQ-004/REQ-005/REQ-024 and adds enforcement wiring to `PermissionService` (a second change's worth of work). C. expose them over HTTP unenforced (dangerous, contradicts the catalog). D. a single admin-only "provision user + roles" endpoint implemented in the api package (new behaviour not in any spec).
- **Recommendation:** A now, and record B as the follow-up TODO so the gap is owned rather than silently accepted.

### Q-19 — Is there a "what am I allowed to do" endpoint?

- **Step:** P.2 (Phase P)
- **Answer:** PENDING
- **Status:** PENDING
- **Date:** 2026-10-08
- **Incorporated:** no
- **Context:** No public API returns a principal's effective permission set (`PermissionService` exposes `has_permission`/`require_permission`, `get_role_permissions(role)`, `catalog.actions()`; api-keys Q-11 already notes the missing "effective grant set" read). OpenAPI describes the surface, not the caller's grants.
- **Why needed:** A client (especially the LLM client in the acceptance signal) otherwise discovers its grants by collecting 403s. Whether this endpoint exists, and whether it needs a permission at all (it is a self-read), is a surface decision — and if it composes `UserRead.roles` × `get_role_permissions` × `catalog.actions()` at the boundary, it is boundary-side logic that no feature spec covers.
- **Options:** A. none in v1 (403 is the discovery mechanism). B. `GET /me/permissions` composed at the boundary from existing public reads; requires a valid session, no catalog action. C. add a public read to the permissions feature (a new cross-feature interface → amends user-roles-permissions). D. include the effective set in the login response (a new field on `LoginResult` → amends authentication REQ-021 representations).
- **Recommendation:** B, with the composition justified as presentation-only (no authorization decision is made there, so the "no second authorization path" rule holds).

### Q-20 — Are the four WebAuthn/passkey endpoints part of v1?

- **Step:** P.2 (Phase P)
- **Answer:** PENDING
- **Status:** PENDING
- **Date:** 2026-10-08
- **Incorporated:** no
- **Context:** `begin_passkey_registration` / `complete_passkey_registration` (enforced), `begin_passkey_login` / `complete_passkey_login` (exempt), plus `list_passkeys` / `delete_passkey`. The models take `PasskeyRegistrationComplete(response: dict[str, Any])` and `PasskeyLoginBegin(credential_id: str)`; the relying-party values are `authentication.rp_id` (`localhost`), `authentication.rp_name`, `authentication.origin` (`http://localhost:3000`); `webauthn` is a deferred import and deptry-ignored (DEP001).
- **Why needed:** Passkey flows only work from a browser against a real origin, and the two login steps are exempt from enforcement, so exposing them is a public, unauthenticated challenge/response oracle. Decision 5 counts them in the 61, but their HTTP usefulness (and the origin/rp_id deployment requirement) needs an explicit statement.
- **Options:** A. expose all four (parity), with the origin/rp_id deployment requirement stated as an NFR. B. expose registration + list/delete, defer the two login steps. C. defer all passkey endpoints to a follow-up change.
- **Recommendation:** A — they are plain JSON request/response pairs and py-webauthn already owns the protocol; state the origin constraint and the `PasskeyHijackError` → status mapping (Q-11).

### Q-21 — Endpoints whose in-process signature takes a session token as an argument

- **Step:** P.2 (Phase P)
- **Answer:** PENDING
- **Status:** PENDING
- **Date:** 2026-10-08
- **Incorporated:** no
- **Context:** `SessionService.list_sessions(token=None, user_id=None, limit=None)` requires **exactly one** of `token`/`user_id` (bare `ValueError` otherwise, REQ-001/AC-003); `logout_all_sessions(token)` (REQ-009) and `logout_other_sessions(token)` (REQ-010) take the token as the identity argument; `revoke_all_sessions(user_id, exclude_session_id=None)` is the admin path ("open in-process, no token", REQ-011); `AuthService.logout(token)` (REQ-009) is idempotent.
- **Why needed:** The caller already sends the token as the Bearer credential. Echoing it in the path/body is a secret in a request body (and in access logs), while deriving it from the header changes which of the two mutually exclusive arguments is used — and `logout_all_sessions` revokes the caller's own session, so the response is followed by 401 on the next call.
- **Options:** A. derive the token from the Authorization header for the self-service routes (no token in the body), keep `user_id` as the admin path, and document the self-revoking 401-after-204 behaviour. B. require the token in the body (literal parity with the service signature). C. split into distinct routes (`GET /sessions`, `DELETE /sessions` for self, `DELETE /sessions/others`, `DELETE /users/{id}/sessions` for admin).
- **Recommendation:** A + C's route split, with an explicit rule "a raw session token never appears in a request body or a URL" (extends session-management REQ-021 and authentication REQ-021 to the wire).

### Q-22 — Search and the `Any`-typed payloads: GET or POST, and what is the schema?

- **Step:** P.2 (Phase P)
- **Answer:** PENDING
- **Status:** PENDING
- **Date:** 2026-10-08
- **Incorporated:** no
- **Context:** `SearchQuery(free_text, filters: FilterGroup | None, feature, offset, limit, sort: Sort | None)` — nested structured filters, not expressible as clean query params; `SearchResultItem.fields: dict[str, Any]` and `SearchResult.failures` are dynamic. `SettingsRegistry.get_value/set_value(key, value: Any)` and `create_template(…, values: dict[str, Any])` are likewise `Any`-typed, validated per kind at runtime, not by schema.
- **Why needed:** It decides the method/shape (`POST /search` with a JSON body vs `GET /search?…`), and how `Any` payloads appear in OpenAPI (a `type: object` with no schema is a weak contract for the generated clients the TODO puts out of scope).
- **Options:** A. `POST /search` with the `SearchQuery` model as the body (reuse, Q-10); settings values as `{"value": <json>}` with the kind validation producing 422. B. `GET /search` with flattened query params and a filter DSL (more surface, more parsing). C. both (GET for the simple case, POST for filters).
- **Recommendation:** A, plus a documented rule that `Any`-typed values are validated by the **feature** (422 with the feature's `reason`), never by the schema, so no second validation layer appears.

### Q-23 — Path prefix, versioning, and non-catalog endpoints (`/health`, `/version`)

- **Step:** P.2 (Phase P)
- **Answer:** PENDING
- **Status:** PENDING
- **Date:** 2026-10-08
- **Incorporated:** no
- **Context:** Decision 5 fixes the surface to the 61 catalog actions, but a deployed server conventionally needs `/health` (and the avatar URL in Q-06 needs a stable path). Any such endpoint is behaviour **not** represented by a catalog action, and AGENTS.md forbids introducing behaviour not represented in the specification.
- **Why needed:** It defines the versioning policy (is `/api/v1` normative, and does a breaking change require a new prefix or a spec amendment?) and legitimises the non-catalog endpoints by naming them in the spec.
- **Options:** A. `/api/v1` prefix normative; `/health` (anonymous, no catalog action) specified explicitly as the only non-catalog endpoint besides the docs routes. B. no prefix (paths as in the acceptance signal), version implied by the project semver. C. prefix + `/health` + `/version` + `/openapi.json` all named.
- **Recommendation:** A, with the closed list "non-catalog endpoints = `/health`, `/docs`, `/redoc`, `/openapi.json` (+ the avatar route if Q-06 chooses one)" as an INV the parity test (Q-05) enforces.

### Q-24 — How many approved specs must be amended, and which at ID level?

- **Step:** P.2 (Phase P)
- **Answer:** PENDING
- **Status:** PENDING
- **Date:** 2026-10-08
- **Incorporated:** no
- **Context:** The TODO assumes **two** amendments (authentication line 15, session-management Constraints — both approved). Evidence: **seven** approved specs normatively exclude an HTTP layer, four of them at requirement/AC level: `docs/specs/file-management.md:10`, `:17`, REQ-001 ("in-process file storage service … no HTTP/REST layer"), REQ-010 ("open to any in-process caller"); `docs/specs/search.md:12`, `:18`, REQ-023, AC-037 ("in-process service only, no HTTP/REST surface"); `docs/specs/mail-service.md:10`, `:13`; `docs/specs/user-management.md:7`; `docs/specs/user-roles-permissions.md:17`; `docs/specs/structlog-logging.md:20` (justifies structured records by the absence of an HTTP layer and names `api-keys` as the future machine-driven consumer).
- **Why needed:** AGENTS.md forbids direct edits to approved specs (Spec Amendment Workflow: own PR, changelog entry, affected-task re-run). Leaving contradicting REQ text in place while shipping the HTTP layer is a spec-drift finding a Phase 6 review must raise; amending seven specs in one PR widens the review surface and touches IDs other changes cite.
- **Options:** A. amend only the two approved ones and add a "the HTTP boundary supersedes these scope lines" note in the backend-api spec. B. amend all seven (prose lines + the four ID-level statements), one changelog entry each, in this PR. C. amend the two approved **plus** the four ID-level conflicts (`file-management` REQ-001/REQ-010, `search` REQ-023/AC-037) and leave the pure-prose scope lines with a superseding note. D. split the amendments into a separate spec-amendment PR merged before this one.
- **Recommendation:** C (the amendments that remove a direct contradiction), with the prose-only lines handled by one explicit supersession paragraph in the backend-api spec; if the user prefers A, the supersession paragraph becomes normative and must be reviewed as such.

### Q-25 — Test strategy for a server: in-process `TestClient` or a live uvicorn, and where do the tests live?

- **Step:** P.2 (Phase P)
- **Answer:** PENDING
- **Status:** PENDING
- **Date:** 2026-10-08
- **Incorporated:** no
- **Context:** `httpx>=0.28.1` is already a declared runtime dependency and is deptry-ignored as "a declared runtime capability not yet imported from source" (`pyproject.toml:16`, `:118-121`) — starlette's `TestClient` needs exactly that. There is no server-test precedent: `tests/{acceptance,integration,contract,property,unit}/<feature>/` is the layout, and `tests/acceptance/settings_coverage/test_wiring.py` is the only subprocess-launched test. Coverage floor is `fail_under = 92` over `src/backend` + `src/frontend` (`pyproject.toml:101-110`), and CI runs `pytest -n auto --cov` (`quality.yml`).
- **Why needed:** 61 handlers must be covered or the floor drops; the app must be constructible with in-memory repositories and an isolated settings registry (no `./data/` writes, no `main.py` import); and nothing tests that uvicorn actually starts unless a live-server test exists.
- **Options:** A. `TestClient` for all categories (`tests/acceptance/api/`, `tests/contract/api/`, `tests/integration/api/`, `tests/unit/api/`) + **one** live-uvicorn smoke test (subprocess, ephemeral port) proving the launcher and the settings-driven bind (Q-08). B. live server for everything (slow, flaky ports). C. `TestClient` only, no live test (uvicorn startup never exercised).
- **Recommendation:** A, with a parametrized contract test that walks the whole route table (one test per catalog action) so the 92% floor holds without 61 hand-written test bodies, and an `api` test-helper module mirroring the existing `*_test_helpers.py` convention.

### Q-26 — Tracing policy for the boundary (logging-coverage REQ-012 binds it automatically)

- **Step:** P.2 (Phase P)
- **Answer:** PENDING
- **Status:** PENDING
- **Date:** 2026-10-08
- **Incorporated:** no
- **Context:** `tests/acceptance/logging_coverage/test_new_classes_traced.py` AST-scans **every public class under `src/backend/**/*.py`** and requires `@logged_class` unless it is an exception, a pydantic `BaseModel`, a SQLModel, a `TypeDecorator`, an enum or a `Protocol` — so any public class in a new `src/backend/api/` package is automatically in scope (logging-coverage REQ-012/AC-012). One-off `get_logger()` statement counts are pinned only for four named files (`settings/registry.py` 17, `settings/repository.py` 11, `eventbus/eventbus.py` 10, `permissions/service.py` 1), so new api modules are unpinned. The logging feature also intercepts third-party stdlib records, which is how uvicorn's own loggers would be routed.
- **Why needed:** `@logged` on 61 handlers means entry/exit records per request on top of uvicorn's access log (double logging, and a token-bearing request must never be logged: authentication REQ-022, session-management REQ-021). The choice also decides whether uvicorn's loggers are re-routed through `setup_logger()` or left on their own handlers.
- **Options:** A. one request middleware emitting **one** record per request (method, matched route, status, elapsed ms, `user_id`; never the token, never headers) + `@logged_class(include_args=False)` on the boundary's own classes; uvicorn's loggers re-routed through the shared pipeline; access log off. B. `@logged` on every handler (61 entry/exit pairs). C. no boundary tracing; rely on uvicorn's access log.
- **Recommendation:** A, and state explicitly that route handler functions are exempt from the "public module functions MUST be traced with `@logged`" convention (they are framework-dispatched, and the middleware covers them) — otherwise the logging-coverage convention reads as a violation.

### Q-27 — NFR budgets for the boundary (measured where?)

- **Step:** P.2 (Phase P)
- **Answer:** PENDING
- **Status:** PENDING
- **Date:** 2026-10-08
- **Incorporated:** no
- **Context:** Existing budgets: user-roles-permissions REQ-029 (a check < 5 ms median, in-process), search NFR-001 (source query < 50 ms, environment-aware: "measured on the host running the suite"), logging NFRs. Each HTTP request adds: token→user_id lookup (Q-04), the check's own session validation, JSON serialization, and the event bus publish. The event bus worker is a background thread per process (Q-09).
- **Why needed:** Without a stated budget there is no contract test for the boundary, and without the environment-aware clause the budget fails in CI (the search spec already had to add that clause).
- **Options:** A. modest budgets with the environment-aware clause: e.g. p95 < 150 ms for a JSON action round-trip (excluding argon2 login), 1 MiB upload < 2 s, ≥ 20 concurrent requests without error, one record per request in the log. B. correctness-only NFRs (no latency numbers). C. strict budgets (risk CI flakes).
- **Recommendation:** A, with the argon2 cost of `/auth/login` excluded from the p95 (REQ-005 forces a dummy verification on every miss) and the numbers recorded as NFR-XXX so the contract test has an ID to trace to.

### Q-28 — Dependency set, transitive cost, and how many ADRs

- **Step:** P.2 (Phase P)
- **Answer:** PENDING
- **Status:** PENDING
- **Date:** 2026-10-08
- **Incorporated:** no
- **Context:** Resolved on this host (2026-10-08) with `uv pip compile` for Python 3.14, against the current lock: `fastapi==0.143.0` pulls `starlette==1.7.0` (**major 1.x**), `pydantic>=2.13.5` (already satisfied), `typing_extensions`, `annotated-types`, and **`opentelemetry-api`**; `uvicorn==0.54.0` pulls `h11`, `click`, `httptools`/`websockets`/`python-dotenv` extras; `python-multipart==0.0.32` is needed only if Q-12 chooses multipart. `py-webauthn` is deliberately undeclared (deptry DEP001) as a deferred import — the same pattern is available for uvicorn if the launcher is optional.
- **Why needed:** It is the change's largest dependency decision (AGENTS.md requires a dependency decision per ADR), and `starlette` 1.x plus an OpenTelemetry transitive are the kind of surprises that must be accepted knowingly. deptry will flag `fastapi`/`uvicorn` if they are only imported in tests (DEP002) or declared but unused.
- **Options:** A. `fastapi` + `uvicorn` (+ `python-multipart` if Q-12=A) as runtime dependencies, one ADR for the framework choice and one for the boundary architecture (mapping table + middleware + principal resolution). B. two ADRs merged into one. C. pin exact versions (the repo uses `>=` floors everywhere).
- **Recommendation:** A with two ADRs; numbering is assigned at S2.1 by merge order (never pre-reserved — `docs/questions/structlog-logging.md:87,272`), and `docs/decisions/` currently tops out at ADR-082 with ADR-081 reserved-but-absent, so the numbers must be re-read at S2.1 rather than quoted from this file.

### Q-29 — What does `backend-api` explicitly NOT do (the boundary against `api-keys`, `composition-root-factory` and the CLI client)?

- **Step:** P.2 (Phase P)
- **Answer:** **PENDING**
- **Status:** PENDING
- **Date:** 2026-10-11
- **Incorporated:** no
- **Context:** `docs/todo/backend-api.md` lists out-of-scope items (machine **API keys** and their audit → the `api-keys` TODO; per-credential **scopes**; OAuth/OIDC; WebSockets; OpenAPI client generation; a frontend/UI; rate limiting and quotas) and warns that the CLI-client idea (the user's `rich` answer) is a separate TODO (`tenacity-rich-cachetools`) that "must not be smuggled in here". Q-07 was answered **B** (2026-10-10), which makes `composition-root-factory` a hard predecessor: the app factory and the object graph are **that** change's deliverable, not this one's (that TODO is now `QUESTIONS-ANSWERED` and was reclassified **CROSS-CUTTING**, so it will carry its own spec and amendment batch). Q-14 recommends no rate limiter in v1 and `docs/questions/api-keys.md` Q-18 defers the limiter to this change; Q-18 here leaves role/grant management out because no catalog action exists for it; Q-02/Q-16/Q-17 each withhold actions from the surface.
- **Why needed:** This is the change's non-goals / scope-boundary question, and none of Q-01…Q-28 asks it globally — they ask per-item scope (which actions, which endpoints, which limiter). The three changes are sequenced (`composition-root-factory` → `backend-api` → `api-keys`) and their scopes were decided in different rounds, so the spec's Scope section would otherwise be assembled bottom-up from 28 answers and can silently absorb a neighbour's work: a credential store, a dependency container, a limiter, a CLI. The answer also decides whether the withheld actions (Q-02/Q-16/Q-17) and the non-catalog endpoints (Q-23) are the **only** reductions from decision 5 — i.e. whether the spec needs an explicit "not in v1" list at all, which AGENTS.md requires for behaviour that is deliberately absent.
- **Options:** A. confirm the TODO's out-of-scope list **verbatim as the spec's non-goals**: machine credentials + their audit → `api-keys`; the composition root and `create_app()` → `composition-root-factory`; the CLI client → `tenacity-rich-cachetools`; rate limiting, quotas, WebSockets, OAuth/OIDC, OpenAPI client generation, frontend → not in v1 — and treat the Q-02/Q-16/Q-17 withholdings as the only in-scope reductions. B. pull rate limiting (Q-14) and/or the permissions-management actions (Q-18 option B: new catalog actions + enforcement wiring) into this change. C. absorb `api-keys`' machine-credential surface here (one change instead of two sequenced ones). D. leave scope implicit — the "all 61" decision plus the per-item answers define it.
- **Recommendation:** A. The sequenced split is already the cheapest correct one — this change ships only the human-session HTTP boundary, and each neighbour keeps exactly one concern, so each PR stays reviewable and `api-keys` reuses the boundary instead of re-deriving it; recording the list verbatim in the spec's Scope section is what stops the limiter/container/credential-store from being smuggled in later.

### Category coverage

`Q-nn` = an entry in this file; `E-nn` = item *nn* of "Closed from evidence (no question needed)" below (resolved on `main`, 2026-10-08/2026-10-11).

| Category | Coverage |
|---|---|
| Classification & Normative Basis (CROSS-CUTTING, which specs/IDs it touches) | covered (Q-24, Q-18, Q-07; E-9 — the spec's "53 enforced / 7 exempt / 60 declared" and the code's "52 / 9 / 61" disagree and must be re-scanned at P.4) |
| Scope & Goals / non-goals (mandatory) | covered (Q-29, Q-18, Q-14, Q-20, Q-23) |
| Overlap & Sequencing against other changes (mandatory) | covered (Q-07, Q-14, Q-18, Q-24; E-1, E-13 — see "Overlap check (P.2)") |
| Interfaces & Public API (route ↔ action mapping, request/response shapes, self-reads) | covered (Q-05, Q-10, Q-19, Q-21, Q-22, Q-06) |
| Behavior & Edge Cases (exempt set, error classes, self-revoking session, withheld actions) | covered (Q-01, Q-03, Q-11, Q-12, Q-16, Q-17, Q-21) |
| Data & State (session state, in-process state, settings values, storage) | covered (Q-04, Q-08, Q-09; E-5 — no new SQLModel table, so no alembic migration; E-8 — `Principal` unchanged) |
| Security & Secrets (token suppression, password oracle, user enumeration, body cap, bind/CORS/docs) | covered (Q-01, Q-02, Q-03, Q-11, Q-13, Q-14, Q-15, Q-21; E-7 — session-token validation is live) |
| Testing & Acceptance (server-test strategy, coverage floor, catalog-parity test) | covered (Q-25, Q-05, Q-27; E-2 — `httpx` already a runtime dep; E-3 — floor 92) |
| Traceability & Spec Drift (which approved specs get amended, matrix rows, drift guard) | covered (Q-24, Q-05, Q-23; E-9, E-10) |
| Architecture & Conventions (composition root, package home, import boundary, tracing policy) | covered (Q-07, Q-26, Q-09; E-11 — the logging-coverage class scan binds the new package; E-12 — `src/frontend/` is an empty placeholder) |
| Constraints & Quality Gates (ruff `B104`, deptry, coverage, mypy, the three CI workflows) | covered (Q-15, Q-28, Q-25; E-3, E-4) |
| NFRs & Performance (latency budgets, payload limits, concurrency, event bus under a server) | covered (Q-27, Q-13, Q-09) |
| Dependencies & Sequencing (fastapi/uvicorn/python-multipart, transitives, ADR count, predecessor) | covered (Q-28, Q-12, Q-07, Q-29; E-1 — no HTTP stack exists anywhere, E-6 — ADR numbering is assigned at S2.1) |
| Release & Changelog (bump level, `CHANGELOG.md` entry) | skipped — no question is possible: AGENTS.md Versioning fixes CROSS-CUTTING → `minor` and Phase 6 item 10 requires the `CHANGELOG.md` entry. Measured 2026-10-11: `pyproject.toml:4` is at **`1.2.0`**, so the bump target is **`1.3.0`** — the `1.0.0 → 1.1.0` figure in the "Version bump" row below and in "For P.4" predates two merged bumps. |
| UI / Accessibility | skipped — the change ships a backend HTTP boundary with no UI surface: `src/frontend/` is empty (measured 2026-10-11: `find src/frontend -type f` → no output; E-12), and the only "interface" a user sees is the generated OpenAPI document (Q-15, Q-28). |

## Interrogation coverage (P.2)

Topic-level detail behind the category table above.

| Topic | Result |
|---|---|
| Scope boundaries (what is and is not the API) | Q-02, Q-03, Q-16, Q-17, Q-18, Q-23 — the "all 61" decision needs an explicit remainder list |
| Route ↔ action mapping and naming; drift guard | Q-05, Q-23 |
| Request/response model derivation; serialization (`Any`, UUID, datetime, enum) | Q-10, Q-11, Q-21, Q-22 |
| File upload / download / streaming | Q-06, Q-12, Q-13 |
| Exception → status mapping, no internal leakage | Q-11 |
| Auth surface; session TTL, lockout, logout, password reset | Q-01, Q-02, Q-04, Q-20, Q-21 |
| Authorization: catalog as the single source of truth; no second path | Q-03, Q-04, Q-18, Q-19 |
| Settings family `api.*` and the startup-vs-live split | Q-08 |
| Composition root, singletons, install order | Q-07, Q-09 |
| Tracing and logging at the boundary | Q-26 |
| Test categories and server-test strategy | Q-25 |
| Spec amendments (which specs, which IDs) | Q-24 |
| Security defaults (bind, CORS, docs, secrets in logs/URLs, rate limiting) | Q-01, Q-06, Q-11, Q-13, Q-14, Q-15, Q-21 |
| NFRs (latency, payload limits, concurrency, event bus under a server) | Q-09, Q-13, Q-27 |
| Dependencies and ADRs | Q-12, Q-28 |
| Version bump | **no question** — CROSS-CUTTING ⇒ `minor` (AGENTS.md Versioning); `pyproject.toml` was at `1.0.0` when this row was written and is at **`1.2.0`** as of 2026-10-11, so the target is `1.3.0` (see "Category coverage") |
| CI consequences | **no question** — see "Closed from evidence" |

## Closed from evidence (no question needed)

1. **No HTTP stack exists anywhere.** `grep -rn "fastapi|flask|starlette|uvicorn|aiohttp"` over `pyproject.toml` and `src/` returns nothing, and none of the three in-flight branches (`crosscut/settings-public-registry-setter` +36 commits, `feature/structure-map` +9, `issue/pytest-randomly` +0) touches it — so there is no dependency collision.
2. **`httpx>=0.28.1` is already a runtime dependency** (`pyproject.toml:16`) and is deptry-ignored as "a declared runtime capability not yet imported from source" (`pyproject.toml:118-121`) — the TestClient dependency is already paid for.
3. **Coverage floor is 92** (`fail_under = 92`, `source = ["src/backend", "src/frontend"]`, `pyproject.toml:101-110`). A new `src/backend/api/` package joins the measured set automatically; the floor is a repo-wide number, so an uncovered 61-handler package would drag it down — handled by the parametrized route test (Q-25), not by lowering the floor.
4. **CI surface is three workflows**: `lint.yml` (ruff check + format-check; paths already include `src/**`, `tests/**`, `pyproject.toml`), `quality.yml` (`complexity` via complexipy, `coverage`, `deptry`, `migrations` = `alembic upgrade head`, `tests` = `pytest -n auto --cov`, `typecheck` = mypy + ty, `docs` = `mkdocs build --strict`), `spec-validation.yml` (`spec-coverage` = `scripts/check_spec_coverage.py`, `traceability` = `scripts/check_traceability.py`). Adding a package needs no workflow edit; adding a runtime dependency does affect `deptry`.
5. **No new SQLModel tables ⇒ no alembic migration** — the boundary owns no storage (decision 3: session tokens already exist). If any api state were added (e.g. rate-limit buckets persisted), `migrations/env.py` would need the new model module imported; nothing in the current decisions requires that.
6. **`docs/decisions/` tops out at ADR-082**; ADR-081 is reserved-but-unwritten (claimed by api-keys). Numbering is assigned at S2.1 by merge order and must never be pre-reserved (`docs/questions/structlog-logging.md:87,272`).
7. **Session-token validation is live**, not dead wiring: `src/main.py:158` passes `session_lookup=_session_repository` to the permission service, so `Principal.session_token` is validated on every enforced call (the "dead wiring" finding in `docs/questions/api-keys.md` is stale and is not re-asked here).
8. **`Principal` is unchanged** (`src/backend/shared/principal.py`: `Principal(user_id: UUID | None = None, session_token: str | None = None)`, user-roles-permissions REQ-025) — decision 3 needs no model change and no new seam.
9. **The exempt set is exactly 9 actions**, not 7: the 7 authentication operations plus `filemanagement.download` and `filemanagement.list_files` (verified by AST scan: 52 `@requires_permission` methods — usermanagement 11, settings 19, filemanagement 8, sessionmanagement 6, mail 3, search 1, authentication 4 — while `docs/specs/user-roles-permissions.md:369` states "53 enforced; 7 exempt; 60 declared"). **No count in this file may be quoted as verified without re-running the scan at P.4**, because the spec's own numbers and the code disagree.
10. **The settings contract test is additive-safe**: `tests/contract/settings_coverage/test_inventory.py` asserts only that its 14 listed keys exist with the right kind/default/category/group, so adding `api.*` keys cannot break it — but `test_no_secret_settings` (NFR-002) fails on any listed key containing `password`/`secret`, which constrains the `api.*` naming (Q-08). Spec §3.5 is already stale (it lists only `logging.*`, `authentication.*`, `usermanagement.*`, `eventbus.*`), so the backend-api spec must carry its own `api.*` inventory rather than assume §3.5 is complete.
11. **The logging-coverage class scan binds the new package automatically** (`tests/acceptance/logging_coverage/test_new_classes_traced.py`), while one-off statement counts are pinned only for four named files — so the api package may add `get_logger()` calls freely but every public class needs `@logged_class` (Q-26).
12. **`src/frontend/` is an empty placeholder** and `src/main.py` is the only entrypoint; the API is backend-only, so no frontend runtime boundary is touched (structure-map spec §Overview confirms the same).
13. **No open PRs** (`gh pr list --state open` → `[]`), and no in-flight change touches the API surface, so the change's base is clean `main`.

## Impact Analysis (P.2) — draft for P.4

CROSS-CUTTING: the change spans **seven** existing features plus one new package. "Spec text changed" = an amendment is needed; "IDs re-verified through the boundary" = the ID's behaviour gains an HTTP path and needs HTTP-level evidence in `docs/verification/traceability.md`.

| Feature | Code change | Spec text changed | IDs touched |
|---|---|---|---|
| **authentication** (`src/backend/authentication/`) | none (the boundary calls the public service) | `docs/specs/authentication.md` Scope/Out-of-scope (line 11/14/15) + Changelog v2 (approved) | REQ-001..REQ-005 (login + lockout over HTTP), REQ-006/REQ-021 (the raw token appears once, never in a response again — Q-01), REQ-008 (`session_info` as the principal-resolution seam — Q-04), REQ-009 (logout semantics), REQ-010..REQ-013 (reset token suppression — Q-01), REQ-014..REQ-018 (passkey over HTTP — Q-20), REQ-019 (validation → 422), REQ-022 (tracing) |
| **usermanagement** (`src/backend/usermanagement/`) | none | `docs/specs/user-management.md:7` out-of-scope prose (Q-24) | REQ-001..REQ-013 through the boundary; the `verify_password` decision (Q-02) is a documented non-exposure, not a spec change |
| **settings** (`src/backend/settings/`) | none; new `api.*` family lives in the api package's `feature_settings.py` | none (the `api.*` inventory belongs to the backend-api spec, not settings-coverage §3.5 — see Closed-from-evidence 10) | REQ-017/REQ-018/REQ-019 (key prefix, category/group, inventory), REQ-021 (no env vars — Q-08); `settings.register`/`register_feature` exposure decision (Q-16) |
| **filemanagement** (`src/backend/filemanagement/`) | none | `docs/specs/file-management.md:10`, `:17`, **REQ-001**, **REQ-010** (ID-level — Q-24) | REQ-001 (in-process wording), REQ-010 (the "open to any in-process caller" actions — Q-03), REQ-018/AC-039/AC-040 (the avatar URL ↔ route-path coupling — Q-06), REQ-024/REQ-026 (settings and the `./data/` layout under a server) |
| **sessionmanagement** (`src/backend/sessionmanagement/`) | none | Constraints section (approved) | REQ-001/REQ-002/AC-003 (token-vs-user_id arguments — Q-21), REQ-009/REQ-010 (self-revoking calls), REQ-011 (admin path), REQ-021 (no raw token in a body or URL) |
| **mail** (`src/backend/mail/`) | none | `docs/specs/mail-service.md:10`, `:13` prose (Q-24) | the `send_email` / template REQs and ACs, subject to the Q-17 exposure decision |
| **search** (`src/backend/search/`) | none | `docs/specs/search.md:12`, `:18`, **REQ-023**, **AC-037** (ID-level — Q-24) | REQ-023/AC-037 ("in-process only"), the query-shape REQs behind Q-22, NFR-001 (the environment-aware clause reused by Q-27) |
| **permissions** (`src/backend/permissions/`) | none (no new actions, no wiring change) | `docs/specs/user-roles-permissions.md:17` out-of-scope prose (Q-18, Q-24) | REQ-024/AC-029/EDGE-023 (the exempt set at the boundary — Q-03), REQ-025 (`Principal` construction — Q-04), REQ-015/D12 (the closed denial-reason set → status mapping — Q-11), REQ-027 (thread safety under the threadpool — Q-09), REQ-029 (the 5 ms check budget inside the HTTP budget — Q-27) |
| **eventbus / logging** | none | `docs/specs/structlog-logging.md:20` factual claim (Q-24) | logging-coverage REQ-012/AC-012 binds the new package's classes (Q-26); eventbus REQs under a single-process server (Q-09) |
| **shared** (`src/backend/shared/`) | none | none | `Principal` unchanged (decision 3) |
| **NEW: `src/backend/api/`** | the whole package: app factory, principal resolution, route table, error mapping, middleware, `feature_settings.py` | new spec `docs/specs/backend-api.md` (new REQ/AC/INV/EDGE/NFR IDs) | n/a |

## Overlap check (P.2)

**Specs** (`docs/specs/`): the seven approved specs listed in the Impact Analysis are the overlap — four of them contradict the change at ID level (Q-24). `docs/specs/settings-coverage.md` §3.5 is stale rather than conflicting (Closed-from-evidence 10). `docs/specs/logging-coverage.md` REQ-012 silently binds the new package. `docs/specs/structure-map.md` (IN-WORKFLOW, `feature/structure-map`, +9 commits) generates a repository map from the tree, so a new `src/backend/api/` package changes its output — no spec conflict, but the map must be regenerated in whichever change lands second.

**TODOs** (`docs/todo/`, live backlog):

| TODO | Status | Relation |
|---|---|---|
| `api-keys` | WAITING | **Downstream.** This change answers its Q-05 (enforcement is the owner's roles, not key scopes), Q-09 (the OpenAPI document is the schema export; `describe_actions` is redundant), Q-10/Q-11 (no scope model in v1), Q-18 (rate limiting — Q-14 here), Q-24/Q-25/Q-26/Q-28/Q-29/Q-30 (error-mapping, settings-family, representation, NFR, test and CI precedents established here), Q-31 (it now `Depends on: backend-api`). It must still answer Q-06, Q-07, Q-08, Q-12, Q-13, Q-14, Q-15, Q-16, Q-17, Q-19, Q-20, Q-21, Q-22, Q-23, Q-27 itself. |
| `composition-root-factory` | PREPARING | **Direct collision** on where the object graph is built (Q-07). Recommendation is to proceed without a `Depends on:` edge and keep `create_app(deps)`'s signature stable so that change can move the container later. |
| `public-api-import-boundary` | PREPARING | **Ordering risk.** It would ban cross-package module-path imports (ruff TID251 — note that **no** TID251/banned-api configuration exists on `main` today: `pyproject.toml` has 225 lines and `[tool.ruff.lint]` ends at the `select`/`ignore` lists). The api package must therefore import features only through their package `__init__` from day one, which is achievable with the current public surfaces (verified: `AuthService`, `UserManager`, `SettingsRegistry`, `FileService`, `SessionService`, `MailService`, `SearchService`, `PermissionService`, `get_permission_service` are all exported). |
| `startup-settings-registration-gaps` | WAITING (ISSUE) | **Same file, different concern.** It adds the three missing `register_settings` calls to `src/main.py` (`filemanagement`, `mail`, `sessionmanagement`); this change adds no registration and only consumes the registry through the composition root. Ordering only — whichever lands second must not re-wire the other's block in `main.py`. Its settings keys are unrelated to the new `api.*` family (Q-08), which belongs to this change's spec, not to settings-coverage §3.5 (E-10). |
| `complexipy-scripts` | WAITING (DOCS/CHORE) | No functional overlap — it restructures four functions in `scripts/` to pass `complexipy … --max-complexity-allowed 15`. Shared surface is the `complexity` CI job (E-4), which will also measure the new api package: the route table, the error-mapping table and the middleware must stay under the ceiling, which is why Q-25 pushes the per-action coverage into one parametrized contract test instead of 61 hand-written bodies. |
| `gitattributes-line-endings` | PREPARING (DOCS/CHORE) | No overlap — it pins working-tree line endings in `.gitattributes` so the byte-comparing gates stop failing on Windows. Only contact: whatever EOL policy it pins applies to the new api package's files, and neither change's gate depends on the other's. |
| `structure-map` | IN-WORKFLOW → **MERGED** (record now in `docs/todo/archive/`) | Map output changes; no conflict. |
| `settings-public-registry-setter` | IN-WORKFLOW | Provides the public singleton install seam the app factory will use; no conflict, but the install order (registry → permission service → app) must be stated in the spec (Q-07). |
| `notifications` | WAITING (FEATURE) | No overlap today: it consumes the event bus and the mail feature in-process. If it later wants an HTTP surface, it becomes a consumer of this boundary (and Q-17's `mail.send_email` decision is the input it depends on). |
| `docstrings-tests` | WAITING (DOCS/CHORE) | No overlap — test docstrings + one `per-file-ignores` removal; it must not be counted as covering the api package's docstrings, which this change writes. |
| `python-3.15-upgrade` | WAITING (DOCS/CHORE) | No overlap; it would re-check the fastapi/starlette wheels for 3.15 (Q-28's transitive set is its input). |
| `tenacity-rich-cachetools` | WAITING (FEATURE) | **The CLI client lives here, not here.** The TODO's Constraints forbid smuggling the CLI-client idea into this change, so this change ships the server and the OpenAPI document only; the client consumes them. Its `cachetools` would also be the natural home of any future cross-request cache — Q-04's per-request-only rule and REQ-014 stay this change's. |
| `ruff-d-docstrings`, `security-changelog-license`, `spec-interview-protocol` | **archived** (`docs/todo/archive/`) | Listed as they stood at P.2 time. `security-changelog-license` may want the boundary's security NFRs (Q-13/Q-14/Q-15) as input. |

**Live backlog re-checked 2026-10-11** (the table above was written 2026-10-08 and predated three of them): the 11 files in `docs/todo/` are `api-keys`, `backend-api`, `complexipy-scripts`, `composition-root-factory`, `docstrings-tests`, `gitattributes-line-endings`, `notifications`, `public-api-import-boundary`, `python-3.15-upgrade`, `startup-settings-registration-gaps`, `tenacity-rich-cachetools` — every one is named above. `structure-map` and `settings-public-registry-setter` have since been **MERGED** and their records archived, so the composition root this change builds on (Q-07 = B) is now a prepared CROSS-CUTTING change (`QUESTIONS-ANSWERED`) rather than a REFACTOR.

## For P.4 (what the answers change)

- Draft `docs/specs/backend-api.md` from the answers, with the **Impact Analysis above carried forward and corrected** (it must name every affected feature and the REQ/AC IDs it touches — AGENTS.md CROSS-CUTTING requirement).
- Name the capability, not the library, in the spec body ("HTTP boundary", "route table", "principal resolution"); FastAPI/uvicorn appear only in the dependency/ADR sections.
- Re-run the enforcement scan before quoting any count (Closed-from-evidence 9): the spec's "53 enforced / 7 exempt / 60 declared" and the code's "52 decorated / 9 unenforced / 61 declared" disagree, and the spec's own numbers must be reconciled or cited as-is with the discrepancy recorded in `docs/verification/backend-api.md`.
- The endpoint table must be **complete**: one row per catalog action (method, path, request model, response model, status codes, action string), plus the closed list of non-catalog endpoints (Q-23) and the explicit non-exposed remainder if Q-02/Q-16/Q-17 withhold any.
- Include the `api.*` settings inventory in the spec's own settings section (do not rely on settings-coverage §3.5), the error→status table verbatim, and the NFR IDs the contract tests will trace to.
- Two ADRs (framework choice; boundary architecture) — numbers assigned at S2.1 by merge order, never pre-reserved.
- Version bump at S6.4: `minor` (CROSS-CUTTING). Re-read `pyproject.toml:4` at S6.4 — it was `1.0.0` at P.2 time and is `1.2.0` on 2026-10-11, so the target is `1.3.0`, not `1.1.0`.
- Smoke-test the dependency set on the host before the ADR is written (done 2026-10-08: `fastapi==0.143.0` + `starlette==1.7.0` + `uvicorn==0.54.0` + `python-multipart==0.0.32` resolve for Python 3.14 against the current lock; fastapi pulls `opentelemetry-api`; **no install was performed and `pyproject.toml`/`uv.lock` were not touched** — this step is write-scoped to `docs/questions/backend-api.md`).

## Late questions (Phases 2–6)

<questions discovered after the change entered the workflow; same entry format, Step field set to the step that found it>

## Prep log

- **P.3 Answer round 1 (2026-10-10):** Q-01 = A, Q-02 = B, Q-03 = A, Q-07 = **B (against the recommendation)**. Q-07 makes `composition-root-factory` a hard predecessor: `backend-api` is now gated behind a REFACTOR that is itself `WAITING` on 29 unanswered questions and on `settings-public-registry-setter` (IN-WORKFLOW). Consequence for scheduling: `composition-root-factory`'s P.3 batch is now the critical path for `backend-api`, and through it for `api-keys`.
- **P.2 completion pass (2026-10-11):** re-checked the file against the current P.2 done-criteria. Floor: 28 entries, all with `Options:` + a `Recommendation:` carrying a one-line reason (verified by count: 28/28). Added the mandatory **`### Category coverage`** table (15 categories — the skill's starting checklist plus this change's own dimensions; 13 `covered`, 2 `skipped` with reasons, every `Q-nn`/`E-nn` reference checked against the entries and the numbered "Closed from evidence" items). Added the mandatory **non-goals / scope-boundary question as Q-29** — Q-01…Q-28 asked per-item scope questions but never the global one (the `backend-api` ↔ `api-keys` / `composition-root-factory` / CLI-client boundary), so the file now has **29** entries. Extended the overlap table with the three live TODOs it predated (`startup-settings-registration-gaps`, `complexipy-scripts`, `gitattributes-line-endings`) and marked the two rows whose changes have since merged. Corrected one stale fact the file would otherwise hand to P.4: the version-bump target (`pyproject.toml:4` is `1.2.0` on 2026-10-11, so `minor` ⇒ `1.3.0`, not `1.1.0`). **No existing entry's wording, numbering, `Answer:` or `Status:` was changed**, and the "Decided before P.2" section was not touched.
- **P.2 Interrogate (2026-10-08):** 28 questions recorded (CROSS-CUTTING floor is 20), ordered most blocking first: Q-01 reset-token exposure, Q-02 the `verify_password` oracle and Q-03 the 9 unenforced actions are the security-critical three. Evidence read: the authentication/filemanagement/permissions/sessionmanagement/settings/search/mail/usermanagement service signatures and models, the eight exception hierarchies, `pyproject.toml` (coverage floor 92, deptry ignores, no TID251 config), the three CI workflows, the logging-coverage and settings-coverage contract tests, and `git worktree list` / `gh pr list` for the overlap check. Dependency set resolved for Python 3.14 with `uv pip compile` (no install, no lock change). Two facts in the launch brief did **not** hold on `main` and are corrected here: there is no ruff `TID251` / `flake8-tidy-imports.banned-api` configuration (so no `fastapi.Depends` exemption exists yet — it belongs to the `public-api-import-boundary` TODO), and `docs/workflow/PROBLEMS.md` ends at P-62.
