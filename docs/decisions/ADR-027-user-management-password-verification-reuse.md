# ADR-027: User-management password verification reuse with dummy verification

## Status
Accepted

## Context
Password verification must use the stored Argon2id hash (REQ-002), and the
service must never store or return the hash. Timing must not reveal whether
an identifier exists (REQ-005): a fast "unknown user" path is a user
enumeration oracle. Password changes on reset completion must respect the
shared password rules (REQ-012).

## Decision
Reuse the user-management feature for all password operations:
`UserManager.verify_password` for found users, and a **dummy Argon2id
verification against a fixed dummy hash** for unknown users so every login
attempt performs one Argon2id verification. Completed password resets change
the password via `UserManager.change_password` (shared rules, re-hashing,
`UserPasswordChanged` event). The service holds no hash and no hashing logic.

## Consequences
- Password rules, hashing parameters, and re-hashing behavior stay in one
  place (user-management, ADR-019); authentication cannot drift.
- Every login attempt has the same Argon2id cost regardless of whether the
  identifier exists, equalizing timing at the dominant cost term.
- The service depends on user-management's public API only (ADR-025).

## Alternatives Considered
- The service reads `User.password_hash` and verifies directly — rejected:
  duplicates hashing logic, exposes the hash to a second feature, and
  violates "the service never stores or returns the hash" (REQ-002).
- Skipping dummy verification and relying on the unified error alone —
  rejected: the unified error hides *identity*, not *timing*; the timing
  oracle remains.
- A constant-time padding strategy without Argon2id — rejected: Argon2id is
  the dominant cost term; padding other work does not equalize it.

## References
- `docs/specs/authentication.md` (D3; REQ-002, REQ-005, REQ-012)
- `docs/decisions/ADR-019-argon2id-password-hashing.md`
- OWASP User Enumeration Prevention
