# ADR-030: Password recovery design

## Status
Accepted

## Context
Users who forget their password need a recovery path (REQ-010 … REQ-013).
The flow must not enable user enumeration, reset tokens must expire and be
invalidated, and a completed reset must neutralize existing sessions. The
project has no email feature; reset delivery is handled by a separate email
feature.

## Decision
`request_password_reset(email)` **always succeeds** (no error, no
enumeration); a reset token is created only when the email is registered.
Tokens are 256-bit random, stored only as SHA-256 hashes, **single-use**,
and expire after `reset_token_ttl` (default 15 minutes, configurable). A new
reset request for the same email invalidates all prior tokens for that email
(supersede-on-new-request). `complete_password_reset` with a valid token
changes the password via `UserManager.change_password` (shared rules),
consumes the token, and revokes all sessions for the user. Invalid tokens
raise `InvalidResetTokenError` with `reason` `"unknown"`, `"expired"`, or
`"used"`.

## Consequences
- Enumeration is closed at both endpoints (request and completion).
- A leaked or intercepted token has a bounded misuse window (default 15
  minutes) and dies on the next legitimate request for the same email.
- A completed reset is a full credential rotation: old sessions cannot
  survive a password change, which is the point of recovery.
- The `reason` field distinguishes token states for the client without
  leaking user existence (the token was already in the client's possession).

## Alternatives Considered
- Raising an error for unknown emails — rejected: an enumeration oracle.
- Long-lived or non-expiring tokens — rejected: an unbounded misuse window
  for leaked tokens.
- No session revocation on completed reset — rejected: pre-reset sessions
  survive the password change, defeating the purpose of recovery.
- Email one-time links — rejected: the project has no email feature; the
  reset delivery is a separate concern handled by the email feature.

## References
- `docs/specs/authentication.md` (D6; REQ-010 … REQ-013)
- `docs/decisions/ADR-027-user-management-password-verification-reuse.md`
- OWASP Password Storage Cheat Sheet
