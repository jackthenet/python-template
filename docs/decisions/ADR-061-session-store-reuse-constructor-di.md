# ADR-061: Session store reuse via constructor DI (no second session store)

## Status
Accepted

## Context
The session-management feature must list, revoke, and clean up the sessions
that the authentication feature creates and owns (REQ-017). Authentication
owns the `Session` table, the `SessionRepository` ABC (`add`,
`get_by_token_hash`, `revoke`, `revoke_all_for_user`, `delete_expired`), and
`AuthService.session_info(token)` (authentication REQ-008). The feature
needs per-user listing, per-user revocation with an excluded session, and
bounded cleanup — operations the current ABC does not expose. Authentication's
public API is a backward-compatibility contract (authentication NFR-003), and
the approved `authentication.md` spec does not cover session listing or
cleanup.

## Decision
Create `src/backend/sessionmanagement/` as a standalone feature that reuses
authentication's `Session` table and `SessionRepository` ABC via constructor
injection (REQ-017). The ABC is extended additively with `get(session_id)`,
`list_for_user(user_id)`, `revoke_user_sessions(user_id,
exclude_session_id=None)`, and an optional `limit` parameter on
`delete_expired` (`None` = all, the previous behavior). All existing ABC
methods retain their behavior, so existing implementors and call sites remain
valid (authentication NFR-003). There is no second session store: every
operation acts on the same `sessions` table as authentication. No spec
amendment to `authentication.md` (recorded decision, spec §2).

## Consequences
- One source of truth for session state; authentication's
  `session_info(token)` stays the token-path resolution point for all
  token-based operations (REQ-002).
- The feature depends on authentication's public API only (consistent with
  the composition pattern of ADR-025).
- The additive ABC extension keeps existing repositories valid; the new
  methods are implemented there (e.g., `SqliteSessionRepository`).
- Test fakes implement the extended ABC; the feature's store-reuse contract
  is testable (AC-033).

## Alternatives Considered
- Extending authentication's `AuthService` with session-management methods
  (spec amendment to `authentication.md`) — rejected: session
  listing/revocation/cleanup is a distinct concern from authentication
  (login, recovery, passkeys, throttling); mixing them would couple
  unrelated change drivers and require amending an approved spec (Q-34).
- A feature-owned read-only repository over the same `sessions` table with
  zero changes to authentication — rejected: a read-only repository cannot
  perform revocation or cleanup; bypassing the ABC would duplicate SQL
  against the same table and drift from authentication's storage contract
  (Q-34).

## References
- `docs/specs/session-management.md` (REQ-017, REQ-002; §2)
- `docs/specs/authentication.md` (REQ-008, NFR-003)
- `docs/decisions/ADR-025-authentication-feature-placement.md`
- `AI_Questions.md` (Q-34)
