# ADR-022: Last-admin protection semantics

## Status
Accepted

## Context
The system must never reach a state with zero active admins while `admin` is
in the configured role set (REQ-008). Three operations can demote or remove
an admin: `delete_user`, `deactivate_user`, and `set_role` (demotion). The
store exposes `count_active_by_role(role)` for the check. Only the last admin
is protected (EDGE-016).

## Decision
While `admin` is in the configured role set, any operation that would leave
zero active admins is rejected with `LastAdminError` before the mutation is
applied: deleting or deactivating the only active admin, and demoting the only
active admin via `set_role`. The check counts active admins via
`count_active_by_role("admin")`; if the count is 1 and the target user's role
is `admin`, the operation is rejected. With two or more active admins, admin
deletion/deactivation/demotion is allowed.

## Consequences
- The invariant INV-003 (at least one active admin while any admin-role user
  exists) holds for any operation sequence.
- The protection is conditional on the configured role set: a service
  constructed without `admin` in `roles` has no last-admin protection.
- The check is a service-level domain rule (not a database constraint), so it
  is enforced identically for every `UserRepository` implementation.

## Alternatives Considered
- A database trigger/constraint enforcing the rule — rejected: the rule is a
  domain rule (depends on the configured role set), not a schema constraint;
  DB triggers are engine-specific and would break repository swappability.
- Rejecting only deletion of the last admin — rejected: deactivation and
  demotion can equally leave zero active admins (AC-018, AC-019).
- Protecting the last *role* admin regardless of active state — rejected: the
  spec protects active admins; an inactive-only admin set is a recoverable
  state, and the check is on `count_active_by_role`.

## References
- `docs/specs/user-management.md` (REQ-008, INV-003; D4; AC-017, AC-018, AC-019; EDGE-016)
