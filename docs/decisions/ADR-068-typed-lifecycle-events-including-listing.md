# ADR-068: Typed lifecycle events on the structural publisher (including listing)

## Status
Accepted

## Context
Per the repo pattern, features publish typed lifecycle events to an injected
structural `EventPublisher` (ADR-021, ADR-058 pattern). This feature's
events must be distinguished from authentication's existing `Logout(user_id)`
event (authentication publishes it on `logout(token)`), and it must be
decided whether listing — a read operation — is an event at all (Q-46).

## Decision
The feature publishes `SessionRevoked(user_id, session_id)`,
`AllSessionsRevoked(user_id, excluded_session_id)` (distinct from
authentication's `Logout`), `ExpiredSessionsDeleted(count)`, and
`SessionsListed(user_id, count)` (listing is also published) to the injected
publisher (REQ-018). A `None` publisher means no events and no subscriptions
(AC-038). Events carry non-sensitive data only — user ids, session ids,
counts; never raw tokens or token hashes (NFR-002). An operation that
revokes 0 sessions publishes no event (AC-035).

## Consequences
- `AllSessionsRevoked` is distinct from authentication's `Logout`:
  consumers can distinguish a single-token logout from a bulk revocation, and
  `AllSessionsRevoked` carries the excluded session id (AC-035).
- Publishing `SessionsListed` gives consumers an audit point for listing
  (AC-037).
- Consistent with the structural `EventPublisher` protocol (no base class
  required) and the other features' event contracts.

## Alternatives Considered
- Reusing authentication's `Logout` event for logout-all — rejected:
  `Logout` carries no exclusion information and would conflate a
  single-token logout with a bulk revocation; a distinct event preserves the
  meaning of both (Q-46).
- Not publishing listing (read operations are not events) — rejected:
  listing was explicitly included in the published event set (Q-46).

## References
- `docs/specs/session-management.md` (REQ-018, NFR-002; AC-034, AC-035,
  AC-036, AC-037, AC-038)
- `docs/specs/authentication.md` (`Logout` event)
- `docs/decisions/ADR-058-typed-lifecycle-events-structural-publisher.md`
- `AI_Questions.md` (Q-46)
