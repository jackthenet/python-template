# ADR-028: Unified invalid-credentials error

## Status
Accepted

## Context
Login failures must not enable user enumeration or lock-state signaling
(REQ-003, REQ-004). Distinct error kinds for "unknown user", "wrong
password", "inactive user", or "locked" would let an attacker map the user
base and detect throttling state.

## Decision
All password-login failure conditions — unknown user, wrong password,
inactive user, and locked identifier — raise the single
`InvalidCredentialsError` (an `AuthenticationError` subclass). No other
domain error escapes from `login` for these conditions; the error carries no
context that distinguishes the cause. Passkey flows keep their distinct
domain errors (they are a different method with different client needs).

## Consequences
- The client cannot distinguish failure causes; enumeration and lock-state
  oracles are closed at the API surface.
- The unified error is scoped to password login; `session_info`, reset, and
  passkey failures keep distinct, secret-free errors (they do not leak user
  existence in the same way).
- Debuggability shifts to observability: `LoginFailed` events and DEBUG
  logging carry the context, not the exception.

## Alternatives Considered
- Distinct error subclasses per cause — rejected: an enumeration and
  lock-state oracle by construction.
- A single generic error for *all* authentication failures — rejected:
  over-unification; passkey and reset flows have domain errors the client
  legitimately needs (e.g., "credential not found" vs "hijack"), and they do
  not leak user existence.
- Error codes in a result object instead of exceptions — rejected: the
  project's service API uses exception hierarchies for domain failures
  (two-tier validation, ADR-023 pattern).

## References
- `docs/specs/authentication.md` (D4; REQ-003, REQ-004)
- `docs/decisions/ADR-023-two-tier-validation.md`
- OWASP Authentication Cheat Sheet (generic error messages)
