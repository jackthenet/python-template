# ADR-063: Event-driven session-cap eviction on LoginSucceeded (oldest first)

## Status
Accepted

## Context
The per-user session cap (default 5, configurable via
`sessionmanagement.max_sessions_per_user`) must evict the oldest valid
sessions when a new login exceeds the cap (REQ-014, Q-49). The login path is
owned by authentication (`AuthService.login`), and its approved spec does not
mention a session cap. A direct call from authentication's login path to the
new feature would create an authentication → session-management dependency —
the reverse of the natural composition direction, since this feature already
depends on authentication's store (ADR-061) — and would require amending
authentication's spec.

## Decision
Enforce the cap event-driven: the feature subscribes to authentication's
`LoginSucceeded` (authentication REQ-020) and, if the user's valid session
count exceeds the live-read `sessionmanagement.max_sessions_per_user`,
revokes the oldest valid sessions (`created_at` ascending) until the count
equals the cap (REQ-014). The newly issued session is always kept.
Authentication's login path is not modified beyond the additive login schema
fields (ADR-062).

## Consequences
- After `LoginSucceeded` handling, the user's valid session count is at most
  the cap (INV-003); at the exact cap, the oldest session is evicted and the
  new session is kept (AC-027, EDGE-011).
- Authentication remains unchanged: no new dependency, no spec amendment;
  the eviction is a subscription in this feature.
- The cap is live-read on each login (REQ-019), so a registry change takes
  effect at the next login.
- Eviction is idempotent for re-runs (INV-001).

## Alternatives Considered
- A direct call from authentication's login path (authentication calls
  session-management after issuing the session) — rejected: creates an
  authentication → session-management dependency (the reverse of ADR-061's
  direction), couples the login path to the cap policy, and requires amending
  authentication's spec (Q-49).
- No cap (unlimited concurrent sessions) — rejected: a configurable per-user
  cap with oldest-first eviction was explicitly requested (Q-49).

## References
- `docs/specs/session-management.md` (REQ-014, REQ-019; INV-003; AC-027,
  AC-028; EDGE-011)
- `docs/specs/authentication.md` (REQ-020)
- `AI_Questions.md` (Q-49)
