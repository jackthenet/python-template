# TODO: api-keys

Backlog item for one planned change, created at **P.1 Frame** from this template and named `api-keys.md`. One file per change.

This is a **planning record, not normative**: like `docs/questions/`, it is committed directly to `main` (see "Phase P: PREPARE" in `AGENTS.md`). It carries no approval gate — the spec does.

- **Status:** PREPARING  <!-- PREPARING | QUESTIONS-ANSWERED | READY | IN-WORKFLOW | WAITING | MERGED -->
- **Change type:** FEATURE  <!-- strong escalation candidate → CROSS-CUTTING: it introduces the first runtime boundary and spans authentication + permissions + every enforced feature -->
- **Created:** 2026-10-03
- **Question file:** `docs/questions/api-keys.md`
- **Spec:** `docs/specs/api-keys.md`
- **Worktree:** <created at P.4> `../python-template_kopie-worktrees/feature/api-keys`
- **Depends on:** none (may be depended on by `docs/todo/notifications.md`)
- **Related specs:** `docs/specs/authentication.md` (opaque-token pattern, sessions), `docs/specs/session-management.md` (list/revoke analogue), `docs/specs/user-roles-permissions.md` (catalog, checker, `Principal`), `docs/specs/user-management.md`, `docs/specs/search.md` (pagination conventions to mirror)

## Goal (one line)
An **API an LLM can drive**: non-interactive **API-key authentication** with **create/revoke**, **permissions/scopes**, **expiration**, and an **audit trail of usage** — layered on the permission enforcement the backend already has.

## Why
There is no API at all: `grep -rni "fastapi|flask|starlette|uvicorn|aiohttp" pyproject.toml src` → no match, and every spec explicitly excludes one (`docs/specs/authentication.md:15` "Out of scope: … HTTP/REST/GraphQL API layer"; `docs/specs/session-management.md` "Backend-only in-process service — no HTTP/REST layer"). At the same time the backend is already an unusually machine-friendly surface: ~60 closed `feature.action` catalog actions, one enforcement decorator (`@requires_permission`, ADR-071), one principal model (`src/backend/shared/principal.py`), and uniform typed request/response models + pagination (`backend.search`). What is missing for a machine client — an LLM, an agent, an integration — is a **credential**: today the only token is an interactive session issued by `login()` (7-day TTL, revoked on password change, tied to a device/user-agent by session-management), which is the wrong shape for a long-lived non-interactive client, has no scopes of its own, and leaves **no audit record** (authentication.md lists "persistent audit log" as out of scope). So an LLM client today cannot be authenticated, scoped, expired, or audited.

## In scope
- **Credential**: API key with name/label, owning user, created_at, optional `expires_at`, `last_used_at`, revoked flag; create / list / revoke (single + all-for-owner); raw key returned **exactly once**, stored only as a SHA-256 hash, 256-bit `secrets.token_urlsafe` — the authentication REQ-006 pattern, deliberately reused rather than reinvented.
- **Scopes**: a subset of the existing permission catalog (`feature.action` keys, `<feature>.*` wildcards) — **no new permission vocabulary**; a key's effective grant set = its scopes ∩ the owning user's roles, so revoking a role tightens keys too.
- **Resolution into the existing seam**: key → `Principal` (+ scope check) so every already-enforced service method keeps working unchanged; a `resolve_key(raw) -> Principal` entry point is the integration contract.
- **Expiration + revocation**: expired or revoked keys rejected even with a correct key; last-used tracking; cleanup of expired rows (compare `sessionmanagement.cleanup_expired()`).
- **Usage audit**: append-only record per call — key id (never the key), action key, outcome (allowed / denied / invalid-key), timestamp, and (if decided) caller metadata; queryable per key/user/action with pagination; retention policy.
- **LLM-facing API design** (the user's explicit focus): typed request/response models, machine-readable structured error payloads (code + reason + what to do), a **self-describing catalog** (list the actions a given key may call, with their input/output schemas — e.g. a JSON-schema export of the catalog and the enforced methods), stable pagination and id conventions, and idempotent/no-surprise semantics. Whether this surface is an **HTTP server** (new dependency + ADR) or an in-process "tool API" plus schema export (MCP-style, no server) is the central P.2/P.3 question.
- Feature-owned `register_settings` (e.g. `apikeys.default_ttl`, `apikeys.max_active_keys`, `apikeys.audit_retention_days`) and `register_actions` (e.g. `apikeys.create`, `apikeys.revoke`, `apikeys.list_usage`), events, `ApiKeysError` hierarchy, alembic migration, `@logged_class` with `include_args=False`.

## Out of scope
- OAuth2/OIDC, JWT, mTLS, signed request signing, per-request HMAC.
- Rate limiting / quotas beyond reusing the existing attempt-tracker idea (decide at P.2 whether throttling belongs here at all).
- Frontend UI for key management.
- Changing authentication's session semantics or its login path.
- Outbound webhooks / third-party integrations.
- Multi-tenancy, per-org keys.

## Affected features
New feature: `src/backend/apikeys/` (+ possibly a new boundary, e.g. `src/backend/api/`, if an HTTP layer is chosen). Touched without changing behavior: `src/backend/shared/principal.py` (reuse), `src/backend/permissions` (catalog additions via `register_actions`, checker reuse), `src/backend/authentication` + `src/backend/sessionmanagement` (pattern reuse only — **no** second session store decision is made here). Startup wiring in `src/main.py`.

## Constraints and risks
- **Almost certainly CROSS-CUTTING.** Introducing the first runtime boundary that spans authentication, permissions and every enforced feature is an architecture change; P.2 must run the per-feature Impact Analysis and reclassify (`feature/api-keys` → `crosscut/api-keys`, `git branch -m`).
- **Two token stores = divergent revocation.** Sessions (authentication) and keys must not drift into two half-implemented revocation models. Decide explicitly: separate `api_keys` table (likely) vs. extending the `Session` table (rejected unless P.2 argues otherwise), and record the ADR.
- **Secrets.** The raw key never appears in logs, events, audit rows, error messages or list responses (authentication NFR-002, session-management's "raw tokens never in list entries"). Hashed at rest; leaked-key rotation must be possible (revoke-by-id without knowing the key).
- **Scopes must not bypass the catalog.** REQ-004 of `user-roles-permissions.md` says the catalog is closed and static; key scopes MUST validate against it, never invent permission names.
- **Audit volume and privacy.** Append-only rows grow unbounded and may store user-identifying metadata → retention + what-fields policy; audit must never contain secrets or file contents.
- **New dependency risk.** An HTTP framework (FastAPI/Starlette) is a real architectural addition: ADR + `deptry` + CI + `uv.lock` consequences, and it contradicts the "no HTTP layer" constraint written into five existing specs — that contradiction is a spec-amendment conversation, not a silent override.
- **LLM-facing ≠ undocumented.** A self-describing catalog is only useful if it stays in sync with the closed catalog; a hand-written second list of endpoints would drift immediately. Derive it from `catalog.py`.

## Value triage (2026-10-03, pre-workflow)
- **Overlap:** directly reusable — authentication REQ-006/REQ-007 (opaque 256-bit tokens, SHA-256 at rest, TTL), session-management REQ-001/REQ-008 (list + idempotent revoke by id), permissions REQ-001/REQ-002/REQ-004/REQ-024 + `Principal`/`@requires_permission` (the whole enforcement path). What exists **nowhere**: a non-interactive credential, per-credential scopes, and any usage audit. So: reuse the token and enforcement machinery, add the credential + audit, do **not** build a second auth system.
- **Beneficiary:** the LLM/agent client (the thing the user wants to be able to drive this backend) and the operator (audit trail = the only way to know what a machine client did).
- **Score: 5/5** — clear, new value; it is the prerequisite for every "let a machine use this backend" capability, and the enforcement half it needs already exists, so the diff is mostly credential + audit + a thin surface.
- **Recommendation: implement**, but as **CROSS-CUTTING** after P.2's impact analysis (spec with Impact Analysis + ADRs), not as a small single-feature change.

## Acceptance signal (plain language)
A key created for a user scoped to `usermanagement.list_users` can perform that operation and is denied `usermanagement.create_user`; the raw key is shown once and never again (not in lists, logs, events or audit rows); revoking or expiring a key makes it fail even though the string is still correct; every call leaves exactly one audit row naming the key id, the action and the outcome, and that audit is queryable per key; a client can ask "what may this key do?" and get the action list with schemas, derived from the real catalog; the full existing suite still passes with no weakened tests.

## Prep log
| Step | Date | Result |
|---|---|---|
| P.1 Frame | 2026-10-03 | TODO + question file created on `main`; type FEATURE (escalation candidate CROSS-CUTTING); todo set created; **value triage 5/5, implement** |
| P.2 Interrogate (<n> questions) | | |
| P.3 Answer (<n> answered) | | |
| P.4 Draft spec + create branch/worktree | | |
| P.5 Self-consistency | | |
