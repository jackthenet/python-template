# ADR-067: Idempotent no-op revocation of unknown/already-revoked sessions (no new exception types)

## Status
Accepted

## Context
`revoke_session(session_id)` is list-driven revocation (Q-38): the user
picks a device from the list and revokes it. The session may already be gone
(revoked concurrently, or expired and cleaned up) — a race inherent to
list-driven operations. The error taxonomy must be pinned (Q-47):
authentication's `logout(token)` is an idempotent no-op for
unknown/revoked/expired tokens; file-management raises `FileNotFoundError`
for missing keys.

## Decision
`revoke_session(session_id)` is an idempotent no-op for an unknown or
already-revoked session id — no error, no event (REQ-008, EDGE-002,
EDGE-003). The feature introduces no new exception types: argument errors
are `ValueError` (limit < 1; both/neither `token`+`user_id`; first
`get_session_service()` call without a repository), and invalid-token
failures re-raise authentication's `InvalidSessionError` (REQ-002, REQ-009,
REQ-010). Listing a user with zero valid sessions returns an empty list, no
error (REQ-003, AC-006).

## Consequences
- Re-running any revocation operation after it has succeeded is a no-op — no
  error, no state change, no duplicate event (INV-001).
- No new `SessionManagementError` hierarchy: the feature's error surface is
  `ValueError` + authentication's `InvalidSessionError` + repository
  failures propagated as-is (secret-free).
- List-driven revocation is race-safe: a session revoked between listing and
  revocation is silently skipped.

## Alternatives Considered
- Raising `SessionNotFoundError` (rooted in a new `SessionManagementError`
  hierarchy) — rejected: list-driven revocation inherently races with
  concurrent revocation and cleanup; a missing target is an expected state,
  not an error. The idempotent no-op matches the authentication `logout`
  precedent and keeps the error surface minimal (Q-47).

## References
- `docs/specs/session-management.md` (REQ-008, REQ-003, REQ-002, REQ-009,
  REQ-010; INV-001; AC-015, AC-016; EDGE-002, EDGE-003)
- `docs/specs/authentication.md` (REQ-009, `InvalidSessionError`)
- `AI_Questions.md` (Q-38, Q-47)
