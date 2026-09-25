# ADR-079: Search access control via the shared `Principal`/`PermissionChecker` enforcement plumbing

## Status
Accepted

## Context
Search is a cross-feature entry point over content owned by other features;
access to it must be authorized. The user-roles-permissions change
(ADR-069..ADR-075) established the shared enforcement plumbing: `Principal`,
`PermissionChecker`, and `requires_permission` in `backend.shared`, with
trailing `principal` parameter + decorator wiring (ADR-071) and a fail-closed
posture (ADR-075). The search feature must not invent its own access control,
and it must not import `backend.permissions` at runtime (ADR-070).

## Decision
`search` takes a trailing `principal: Principal = Principal()` parameter and is
enforced with `@requires_permission("search.search")` (the injected
`PermissionChecker`; standalone mode when `None`), before returning results —
a denial raises and propagates before any source is queried (D16, REQ-016).
The feature declares the `search.search` action via its own feature-owned
`register_actions(catalog)` (additive to the user-roles-permissions catalog;
no change to the permissions feature's code or behavior, §12.6). The
`PermissionCatalog` annotation is type-checking only — the feature never
imports `backend.permissions` at runtime (ADR-070).

## Consequences
- Search access control reuses the single, uniform enforcement point
  (ADR-071); there is no second permission concept to keep in sync.
- The catalog grows additively (`search.search`); the permissions feature is
  untouched (impact analysis §12.6).
- Standalone mode (no checker injected) keeps the service usable without
  enforcement (tests/DI), consistent with the other features (ADR-071).
- Fail-closed is inherited: a denial raises before any result is returned
  (NFR-002, ADR-075).

## Alternatives Considered
- A search-specific access check (its own permission concept) — rejected: it
  would duplicate the user-roles-permissions machinery and create a second
  enforcement point; the shared plumbing is the single uniform enforcement
  point (ADR-071).
- Per-item access filtering inside the sources — rejected: out of scope
  (spec §13); each source decides what it returns, and the search feature
  enforces the `search.search` action, not per-item access.
- Enforcing per-source actions (e.g., `usermanagement.search`) — rejected: the
  source content is already scoped by the source's own query function; a single
  `search.search` action keeps the authorization surface uniform and minimal
  (D16).

## References
- `docs/specs/search.md` (D16; REQ-016; NFR-002; §12.6)
- `docs/decisions/ADR-069-permissions-feature-placement.md`
- `docs/decisions/ADR-070-shared-enforcement-plumbing-no-circular-imports.md`
- `docs/decisions/ADR-071-enforcement-wiring-principal-parameter-decorator.md`
- `docs/decisions/ADR-075-fail-closed-security-posture.md`
