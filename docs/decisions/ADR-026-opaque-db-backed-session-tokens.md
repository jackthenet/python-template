# ADR-026: Opaque DB-backed session tokens (JWT rejected)

## Status
Accepted

## Context
Login must issue a session that supports server-side revocation (logout,
password reset, compromise response) and expiry (REQ-006 … REQ-009). The
project has no HTTP layer; sessions are consumed in-process by other
features. Session management is a security-sensitive choice where the
default recommendation (OWASP Session Management Cheat Sheet) is opaque,
server-side sessions.

## Decision
Session tokens are 256-bit opaque random tokens
(`secrets.token_urlsafe(32)`), URL-safe, returned exactly once at login, and
stored **only as their SHA-256 hash** in a `sessions` table with a
server-side `revoked` flag and an `expires_at` timestamp
(`session_ttl`, default 7 days). Validation is a single indexed lookup by
token hash; revocation is an immediate server-side write.

## Consequences
- Instant revocation: logout, completed password reset, or a compromise
  response invalidate a token with one write; no denylist needed.
- A database leak exposes token hashes, not usable tokens; sessions can be
  rotated.
- One indexed SQLite lookup per `session_info`/`logout` call — negligible at
  this scale.
- The raw token exists only in the initial `LoginResult` return and in
  memory of the caller.

## Alternatives Considered
- JWT session tokens — rejected: no instant revocation without a server-side
  denylist (which reintroduces the store JWT avoids); a larger verification
  surface (algorithm-confusion history, clock skew); a new dependency for a
  statelessness benefit this project does not need (SQLite is already the
  state); OWASP explicitly recommends against JWT for session management.
- Storing raw tokens in the database — rejected: a database leak would
  directly expose usable tokens; hashing at rest keeps them unusable.
- In-memory session map — rejected: sessions must survive process restarts
  and be shared across concurrently constructed service instances.

## References
- `docs/specs/authentication.md` (D2; REQ-006 … REQ-009)
- OWASP Session Management Cheat Sheet
- `docs/decisions/ADR-020-sqlite-sqlmodel-repository.md` (storage pattern)
