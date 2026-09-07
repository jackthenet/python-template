# ADR-029: In-memory brute-force throttling

## Status
Accepted

## Context
Login must be protected against brute-force attacks (REQ-004): after
`max_failed_attempts` failures for an identifier, the identifier is locked
for `lockout_duration`; a success clears the state. The feature is simple
auth without new infrastructure, and the service and repositories must be
safe for concurrent use from multiple threads (NFR-005).

## Decision
Use an in-memory `InMemoryAttemptTracker` behind the `AttemptTracker` ABC:
per-identifier failure counts, lock-until timestamps, and success-clears
semantics, guarded by an internal lock (thread-safe). The tracker is
injected into `AuthService` (default: `InMemoryAttemptTracker`
constructed with `max_failed_attempts` and `lockout_duration`). State resets
on process restart — documented and accepted for simple auth.

## Consequences
- Brute-force protection with zero new infrastructure and no write
  amplification on every login attempt.
- The ABC keeps the mechanism swappable (e.g., a persistent or distributed
  tracker later) without service changes.
- A process restart clears lockouts; an attacker cannot force a reset, and
  the restart window is bounded by deployment cadence.

## Alternatives Considered
- A database-backed attempt log — rejected: persistence for ephemeral,
  per-process throttling state adds write load and storage to every login
  attempt for a benefit simple auth does not need; the state is per-process
  by design.
- HTTP-layer rate limiting — rejected: the feature has no HTTP layer.
- No throttling — rejected: leaves brute-force against weak passwords
  unmitigated.

## References
- `docs/specs/authentication.md` (D5; REQ-004, NFR-005)
- `docs/decisions/ADR-028-unified-invalid-credentials-error.md`
