# ADR-074: Dynamic role→permission mapping (runtime-managed roles, SQLite grants)

## Status
Accepted

## Context
The role→permission mapping must be changeable at runtime without a
redeployment (Q-67), and roles must be manageable entities — create/list/
delete — not a fixed set (Q-77). The permission vocabulary itself is a
closed, static catalog (60 actions, declared at startup), so grants are
validated against it (INV-006). The `admin` role is an implicit wildcard
(Q-79) and the non-admin (`user`) role starts with zero permissions (Q-80).
Role and activity changes must take effect on the next check with no
re-login and no caching (Q-84, Q-86).

## Decision
Roles are runtime-managed entities in the `roles` table (permission feature):
`create_role` / `list_roles` / `delete_role`, with guards — built-in roles
(`admin`, `user`) cannot be deleted (`RoleProtectedError`), a role assigned
to any user cannot be deleted (`RoleInUseError`), deleting an unknown role
raises `RoleNotFoundError` (REQ-006, REQ-007). Role→permission grants are
dynamic in the `role_permissions` table: `grant_permission` /
`revoke_permission` / `get_role_permissions`, validated against the catalog
(an action key or a feature wildcard `<feature>.*`; an unknown permission
raises `UnknownPermissionError`, an unknown role raises
`RoleNotFoundError`); grants are idempotent (REQ-008). The `admin` role is
an implicit wildcard — a holder is granted every catalog permission without
an explicit grant (REQ-010, Q-79); the non-admin (`user`) role starts with
zero permissions (REQ-011, Q-80). The effective set is the union of the
roles' explicit grants (including wildcards); the check performs live
lookups (no caching), so role and grant changes take effect on the next
check (REQ-014, Q-84, Q-86).

## Consequences
- Roles and grants are runtime-managed: an operator can create a role, grant
  permissions, and assign it without a redeployment (Q-67, Q-77).
- The `admin` implicit wildcard means an admin passes any catalog permission,
  including permissions declared after the admin's creation (REQ-010, INV-005).
- The non-admin role starts with zero permissions; its permissions come only
  from dynamic grants (REQ-011, Q-80).
- Live lookups (no caching) make role/grant changes take effect immediately,
  with no re-login (REQ-014, Q-84, Q-86).
- Grants are validated against the closed catalog, so the valid grant-key set
  is exactly the catalog actions ∪ feature wildcards (INV-006).

## Alternatives Considered
- A static (hardcoded) role→permission mapping — rejected: it could not be
  changed at runtime, defeating the point of runtime-managed roles (Q-67).
- A fixed role set (no role CRUD) — rejected: roles must be manageable
  entities, not a closed set; CRUD is in scope (Q-77).
- Per-user (non-role) permission grants — rejected: out of scope (Q-95);
  roles are the unit of grant, and per-user grants would bypass the role
  model.
- Caching the effective permission set — rejected: caching would delay
  role/grant changes and require invalidation; live lookups keep changes
  immediate and the check simple (Q-84, Q-86).

## References
- `docs/specs/user-roles-permissions.md` (D4, D6, D7, D11, REQ-006..REQ-011,
  REQ-014; INV-001, INV-004, INV-005, INV-006)
- `docs/decisions/ADR-069-permissions-feature-placement.md`
- `AI_Questions.md` (Q-67, Q-77, Q-79, Q-80, Q-84, Q-86, Q-95)
