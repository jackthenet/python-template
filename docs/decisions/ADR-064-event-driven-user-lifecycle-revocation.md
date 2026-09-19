# ADR-064: Event-driven revocation on user lifecycle events

## Status
Accepted

## Context
A user's sessions must be revoked when the user's password changes, when the
user is deactivated, or when the user is deleted (REQ-015). Today only the
reset-completion path revokes all sessions (authentication REQ-012); a plain
`change_password` does not, and neither deactivation nor deletion revokes
sessions — a deactivated user's tokens remain valid until TTL, and a deleted
user leaves orphaned session rows (`sessions` has no foreign key to users).
The new revocation behavior must not modify user-management.

## Decision
The feature subscribes to user-management's `UserPasswordChanged`,
`UserDeactivated`, and `UserDeleted` events and revokes all sessions for the
affected user on each (REQ-015). The `UserPasswordChanged` subscription is
idempotent with authentication's existing reset-completion revocation
(authentication REQ-012), which remains unchanged and is not re-specified
here.

## Consequences
- A plain `change_password` (without reset) now revokes all sessions for the
  user (AC-029) — the security behavior requested in Q-54.
- Deactivated users lose their valid sessions immediately (AC-030); deleted
  users no longer leave orphaned session rows (AC-031).
- user-management is unchanged: the new behavior is a subscription in this
  feature (no user-management → session-management dependency).
- Re-runs change no state and publish no events (INV-001).

## Alternatives Considered
- Direct calls from user-management (user-management calls session-management
  on password change/deactivation/deletion) — rejected: creates a
  user-management → session-management dependency, couples user mutations to
  session policy, and requires amending user-management's spec; a
  subscription keeps user-management unchanged (Q-54, Q-55).
- Only cleaning up orphaned rows on `UserDeleted` (deactivated users keep
  valid sessions) — rejected: a deactivated user's tokens remaining valid
  until TTL was explicitly rejected (Q-55).
- Out of scope (orphaned rows remain, caller responsibility) — rejected: the
  file-management caller-responsibility precedent does not apply; revocation
  on lifecycle events was explicitly in scope (Q-55).

## References
- `docs/specs/session-management.md` (REQ-015; AC-029, AC-030, AC-031)
- `docs/specs/authentication.md` (REQ-012)
- `docs/specs/user-management.md` (`UserPasswordChanged`,
  `UserDeactivated`, `UserDeleted` events)
- `AI_Questions.md` (Q-54, Q-55)
