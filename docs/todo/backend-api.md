# TODO: backend-api

Backlog item for one planned change, created at **P.1 Frame** from this template and named `backend-api.md`. One file per change.

This is a **planning record, not normative**: like `docs/questions/`, it is committed directly to `main` (see "Phase P: PREPARE" in `AGENTS.md`). It carries no approval gate — the spec does.

- **Status:** WAITING  <!-- PREPARING | QUESTIONS-ANSWERED | READY | IN-WORKFLOW | WAITING | MERGED | DROPPED -->
- **Change type:** CROSS-CUTTING  <!-- split out of `api-keys` at P.3 round 1, 2026-10-08; confirmed by P.2 -->
- **Created:** 2026-10-08
- **Question file:** `docs/questions/backend-api.md`
- **Spec:** `docs/specs/backend-api.md`
- **Worktree:** <created at P.4> `../python-template_kopie-worktrees/crosscut/backend-api`
- **Depends on:** **`composition-root-factory`** (added 2026-10-10 at P.3 round 1, Q-07 = B: the HTTP app is built on that change's `create_app()`, so this change may not pass P.4 until it is merged; that change is itself gated on `settings-public-registry-setter` (IN-WORKFLOW) and has 29 unanswered P.2 questions) — it **blocks** `api-keys`, which depends on this change
- **Related specs:** `docs/specs/authentication.md` (its §Out of scope line 15 excludes an HTTP/REST/GraphQL API layer — **amendment required**), `docs/specs/session-management.md` (Constraints: "Backend-only in-process service — no HTTP/REST layer, no frontend" — **amendment required**), `docs/specs/user-roles-permissions.md` (the 61-action catalog + `@requires_permission` enforcement, consumed unchanged), `docs/specs/logging-coverage.md` (REQ-012 tracing policy for the new module), `docs/specs/settings.md` (a new `api.*` settings family)

## Goal (one line)
Expose the backend's already-enforced operations over an HTTP JSON API so an external client — first the user's LLM/agent client — can log in with the backend's own session token and call any action its role permits.

## Why
The user asked for machine access to this backend (`api-keys`). Answering the first four P.2 questions on 2026-10-08 showed the real request is the boundary itself: *"I want to have an api interface so fastAPI + uvicorn seem to be a good choice"* and *"shouldn't it simply be the api of the backend?"*. Today every capability exists only in-process (`src/backend/<feature>/services`), so no external client can reach any of it. The permission layer is already designed for this: 61 catalog actions across 7 features, `@requires_permission`, and a `Principal(user_id, session_token)` that `PermissionService._validate_session` already validates through the wired `session_lookup` (`src/main.py:158`).

## In scope
- A new boundary package (`src/backend/api/`) hosting a **FastAPI** app served by **uvicorn**.
- Authentication by the backend's **existing session tokens** (Bearer) — no new credential type.
- Routes for the enforced catalog actions — **60 of the 61** (P.3 round 1, Q-02 = 2026-10-10: `usermanagement.verify_password` is **withheld** from the HTTP surface; the deviation from the "all 61" decision is recorded in the spec's not-exposed list), each calling the feature method with the caller's `Principal`.
- Request/response models derived from the existing Pydantic/SQLModel models; error → HTTP status mapping from the existing exception hierarchies.
- Feature-owned `api.*` settings (bind host/port, and whatever P.2 shows is needed) via the settings registry.
- Tracing per the logging-coverage policy (`@logged_class` / `@logged`, `include_args=False` where tokens are involved).
- Tests: acceptance (satisfy the spec), contract (the HTTP contract), unit (edge cases), plus the server-startup precedent this repo does not yet have.
- **Spec amendments** to `authentication.md` and `session-management.md` (approved by the user 2026-10-08) in the same PR, so the governance review is one review.
- ADRs: the framework choice (fastapi + uvicorn — new runtime dependency) and the boundary/architecture element.

## Out of scope
- Machine **API keys** and their audit — the `api-keys` TODO, which now depends on this change.
- Per-credential **scopes** (v1 authorization is the owner's roles, decided 2026-10-08).
- OAuth/OIDC, WebAuthn-over-HTTP changes beyond what login already does, WebSockets, OpenAPI client generation, a frontend/UI, rate limiting and quotas (unless P.2 forces them into the spec).

## Affected features
New: `src/backend/api/`. Wiring: `src/main.py`. Consumed unchanged: `authentication`, `usermanagement`, `permissions`, `settings`, `filemanagement`, `sessionmanagement`, `mail`, `search`, `eventbus`, `logging`. Spec amendments: `authentication.md`, `session-management.md`.

## Constraints and risks
- Two **approved specs normatively exclude an HTTP layer**; the amendments must merge before implementation (Spec Amendment Workflow), and the user has approved them.
- New runtime dependencies (`fastapi`, `uvicorn`, transitively `starlette`) → ADR + `deptry` + `uv.lock` churn (never staged, PROBLEMS.md P-42).
- No precedent in this repo for testing a running server; the test category and the fixture strategy must be decided at P.2 (FastAPI's `TestClient` needs no port and no new dependency).
- The API must not become a second authorization path: every route calls the **same** enforced service method with a real `Principal`; no route may reach a method that is not a catalog action (role/grant management is deliberately not a catalog action today — an agent must not be able to self-escalate).
- Secrets: session tokens and passwords must never reach log records or error bodies (`include_args=False`, error mapping that does not echo internals).
- Safe defaults: bind to localhost by default; CORS off unless configured.
- `src/frontend/` is empty and `src/main.py` is the only entrypoint — the CLI-client idea (the user's `rich` answer) is a separate TODO and must not be smuggled in here.

## Value triage (2026-10-08, pre-workflow)
- **Overlap:** no HTTP layer exists anywhere — `grep -rni "fastapi|flask|starlette|uvicorn|aiohttp" pyproject.toml src` returns nothing, and the runtime deps are pydantic, loguru, orjson, httpx (client only, unused in `src`), sqlmodel, argon2-cffi, email-validator, filetype, pillow, ruamel-yaml. What **does** exist is everything the API would expose: the 61-action catalog, `@requires_permission` (`src/backend/shared/principal.py:51-70`), the session-token validation path (`src/backend/permissions/service.py:412-426`, wired at `src/main.py:158`), and the six features' services. So this is a **boundary over existing capability, not new capability** — the design rule is "map routes onto existing enforced methods, add no second authorization path".
- **Beneficiary:** the user's LLM/agent client (the original ask: drive this backend from an agent), and every future external surface — a CLI client (the user's `rich` idea), a web UI, and `api-keys` all become consumers of this one boundary instead of three bespoke integrations.
- **Score: 4/5** — the highest-value boundary in the backlog and it unblocks `api-keys`, the CLI client and any UI; docked one point because it is the largest kind of change this repo has taken (new runtime dependency, a new boundary package, and two approved-spec amendments).
- **Recommendation:** implement as **CROSS-CUTTING**, with the two spec amendments riding the same PR; reuse the existing session/permission path rather than inventing auth at the boundary.
- **Decision:** **implement** (user, 2026-10-08): FastAPI + uvicorn; authenticate with the backend's existing session tokens; expose all enforced catalog actions; amend both specs.

## Acceptance signal (plain language)
`uv run uvicorn …` starts the app; `POST /auth/login` with a username and password returns a session token; `GET /users` with that token returns the user list; the same request with no token, or with a token whose user lacks the action, is refused (401/403) and nothing is written; the generated OpenAPI document lists the exposed actions; no password or session token appears in any log record.

## Prep log
| Step | Date | Result |
|---|---|---|
| P.1 Frame | 2026-10-08 | split out of `api-keys` at P.3 round 1; CROSS-CUTTING; value triage recorded and the user decided **implement** |
| P.2 Interrogate (28 questions) | 2026-10-08 | **BLOCKED-USER** — 28 questions in one batch (CROSS-CUTTING floor ≥ 20 met), 13 points closed from evidence, Impact Analysis over 11 components, overlap check + P.4 notes. Ordered most blocking first; rounds planned: 7 × ≤4. **Security-led questions (Q-01 raw password-reset token, Q-02 `verify_password` as a password oracle, Q-03 the 9 declared-but-unenforced actions, Q-04 Bearer→`Principal.user_id` or the SYSTEM grant set) each narrow settled decision 5 explicitly.** P.2 also corrects three brief premises: no TID251 config on `main` (that belongs to `public-api-import-boundary`), `docs/decisions/` tops out at **ADR-082** (ADR-081 reserved-but-absent), and `docs/workflow/PROBLEMS.md` on `main` ends at **P-62**. Spec-drift finding for P.4: `docs/specs/user-roles-permissions.md:369` says "53 enforced; 7 exempt; 60 declared" while an AST scan finds **52** `@requires_permission` methods and **9** unenforced declared actions. |
| P.2 Completion pass (contract audit) | 2026-10-11 | **DONE — commit `26b9f04`, `docs/questions/backend-api.md` only (+50/−4).** The file predates the current P.2 wording, so it was audited against it: **`### Category coverage` added** (15 rows — 13 `covered (Q-nn / E-nn)`, 2 `skipped — <reason>`: Release & Changelog fixed by AGENTS Versioning, UI/Accessibility because `src/frontend/` has no files; all 29 `Q-nn` refs and all `E-nn` refs verified to resolve); the missing **non-goals / scope-boundary** question added as **Q-29** (the boundary against `api-keys`, `composition-root-factory` and a future CLI client) → **29 entries, 25 PENDING, 4 ANSWERED**; the overlap table refreshed to all **11 live TODOs** (two rows marked MERGED/archived, the lumped "various" row split per TODO); all 28 pre-existing entries already carried `Options:` + `Recommendation:` (28/28 verified, none added). **Stale figure corrected for P.4:** `pyproject.toml:4` is `1.2.0`, so the CROSS-CUTTING `minor` bump target is **1.3.0**, not 1.0.0. Status stays **WAITING** — P.3 needs the user. Next: **P.3 Answer** (⏸ user, 8 rounds at ≤ 4, most blocking first; Q-29 can ride the last round) |
| P.3 Answer (<n> answered) | | |
| P.4 Draft spec / triage / baseline / scope | | |
| P.5 Self-consistency (FEATURE/CROSS-CUTTING) | | |
