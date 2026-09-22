# ADR-073: Session validation in the check via a structural `SessionLookup` seam

## Status
Accepted

## Context
When a `session_token` is provided, the check must validate the session:
unknown, revoked, or expired → deny; a session belonging to a different user
→ deny (Q-82). Authentication owns the session store — opaque 256-bit
tokens, only the SHA-256 hash stored (ADR-026) — and exposes
`get_by_token_hash`. The permission feature must not hard-import
authentication (it would couple the two features' storage contracts and risk
an import cycle through the composition root), and the session token is a
secret that never appears in log records, events, or error messages (NFR-002).

## Decision
The check validates a provided `session_token` through a structural
`SessionLookup` protocol (a `get_by_token_hash(token_hash) -> SessionRecord |
None` seam; the real implementation is authentication's session repository,
which stores SHA-256 token hashes) (D9, REQ-017). Unknown, revoked, or
expired → deny with reason `invalid_session`; a session belonging to a
different user → deny with reason `session_principal_mismatch`; when the
token is omitted, session validation is skipped (AC-021). When the session
lookup is unavailable (`None` or raises), a token-based check denies with
reason `storage_error` (fail-closed, EDGE-007). The user lookup precedes
session validation (EDGE-024). The session token is a secret: it never
appears in log records, events, or error messages (NFR-002).

## Consequences
- The check is coupled to authentication's session store only through the
  structural `SessionLookup` protocol — no hard import, no import cycle
  (D9).
- A provided token is validated on every check, so a revoked/expired/mismatched
  session denies even for a granted permission (REQ-017, Q-82).
- Fail-closed: an unavailable session lookup denies token-based checks
  (EDGE-007, INV-002).
- The session token stays a secret across the check path (NFR-002, REQ-028).

## Alternatives Considered
- A hard import of authentication's `SessionRepository` — rejected: it would
  couple the permission feature to authentication's storage contract and risk
  an import cycle; the structural `SessionLookup` protocol keeps the seam
  loose (D9).
- Validating the session in the enforcement decorator (not the check) —
  rejected: the check API (`has_permission` / `require_permission`) is the
  single decision point; session validation belongs there so both the
  decorator path and direct check calls validate consistently (REQ-017).
- Skipping session validation (trust the token) — rejected: a revoked/expired
  session or a mismatched principal would then pass, defeating the point of
  binding the check to a live session (Q-82).

## References
- `docs/specs/user-roles-permissions.md` (D9, REQ-017; §3 `SessionLookup`
  protocol; EDGE-005, EDGE-006, EDGE-007, EDGE-024, EDGE-025; NFR-002)
- `docs/specs/authentication.md` (opaque session tokens, `get_by_token_hash`)
- `docs/decisions/ADR-026-opaque-db-backed-session-tokens.md`
- `AI_Questions.md` (Q-73, Q-82)
