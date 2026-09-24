# ADR-075: Fail-closed security posture (undeterminable checks deny + warn)

## Status
Accepted

## Context
The check operates over live state — user, roles, grants, system set,
session — any of which can be unknown, inactive, malformed, or unavailable
(storage error). A security check that cannot determine the answer must not
allow (Q-74). Inactive (deactivated) users must be denied all permissions
(Q-85). The session token is a secret that never appears in log records,
events, or error messages (NFR-002). A persistent audit log is out of scope;
denials are transient logs + events only (Q-91).

## Decision
Fail-closed is a hard invariant: every undeterminable check denies (D12,
REQ-015). `has_permission` returns `False` and `require_permission` raises
`PermissionDeniedError` with a `reason` from a closed set
(`unauthorized`, `unknown_user`, `inactive_user`, `unknown_permission`,
`malformed_permission`, `invalid_session`, `session_principal_mismatch`,
`storage_error`), plus a WARNING log (user_id, permission, reason — never
the session token) and a `PermissionDenied` event (REQ-020). A check for an
inactive user denies all permissions, even with `admin` (REQ-016, Q-85). The
check never returns `True` in an undeterminable state (INV-002, NFR-002).
Denials are observable via the WARNING log + `PermissionDenied` event, with
no persistent audit log (Q-91).

## Consequences
- Deny-by-default on every failure mode: unknown user, inactive user,
  malformed/unknown permission, invalid/mismatched session, storage error
  (REQ-015, REQ-016, INV-002).
- The closed reason set makes denials diagnosable without a free-text log
  (REQ-015).
- The WARNING log + `PermissionDenied` event give observability without a
  persistent audit log (Q-91, REQ-020).
- The session token stays a secret across the denial path (NFR-002, REQ-028).
- Fail-closed is a hard invariant, not a configurable default (NFR-002).

## Alternatives Considered
- Fail-open on storage errors (treat as allowed) — rejected: a security check
  must not grant on uncertainty; fail-open would let a storage blip authorize
  access (Q-74, INV-002).
- Raising a distinct exception per failure mode (instead of a single
  `PermissionDeniedError` + closed reason) — rejected: the check API raises
  only `PermissionDeniedError` (with a closed reason); a reason set keeps the
  API uniform and the denial path single (D12, REQ-015).
- Allowing inactive users their granted permissions — rejected: a deactivated
  user must be denied all permissions, even with `admin` (Q-85, REQ-016).
- A persistent audit log of denials — rejected: out of scope; denials are
  transient logs + events only (Q-91).

## References
- `docs/specs/user-roles-permissions.md` (D12, REQ-015, REQ-016, REQ-020;
  INV-002; NFR-002; EDGE-001..EDGE-011)
- `AI_Questions.md` (Q-74, Q-85, Q-91, Q-94)
