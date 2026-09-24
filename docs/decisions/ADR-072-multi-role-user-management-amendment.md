# ADR-072: Multi-role user-management amendment (single role → role list)

## Status
Accepted

## Context
A user may hold multiple roles, and the effective permission set is the union
of the roles' grants (Q-78). The existing user-management schema stores a
single `role: str` per user, with the role value `member`, and a single-role
`set_role` (ADR-018, ADR-022). Role names must be validated against the
permission feature's role store — the single source of truth for which roles
exist, because roles are runtime-managed entities (Q-77). The last-admin
guard (ADR-022) must hold on every assignment path (Q-81). The change
permits breaking changes only as enumerated in Section 13, each fixed within
this change's scope (Q-97).

## Decision
Amend user-management (breaking, fixed in scope): `User.role: str` →
`User.roles: list[str]` (non-empty, enforced by the service); `UserCreate`
gains `roles: list[str]` and `UserRead.roles: list[str]` (REQ-026). Role
existence is validated against an injected `RoleStore` (default
`StaticRoleStore(("admin", "user"))`) — the permission feature's role store
is the single source of truth for role names. New assignment methods
`set_roles` / `add_role` / `remove_role` are added; `set_role` is preserved
as `set_roles([role])` (replace, not add) (Q-76). The last-admin guard
applies to every path that removes `admin` from the last active admin:
`set_role`, `set_roles`, `remove_role`, `delete_user`, `deactivate_user`
(`add_role` never removes `admin`). Events carry lists:
`UserRoleChanged.old_roles` / `new_roles`, `UserCreated.roles`. The role
value `member` is renamed to `user`; an alembic data migration rewrites role
values and converts the single role column to a role list (breaking changes
#1–#5). The permission service's assignment pass-throughs validate role
existence and delegate to the corresponding `UserManager` method (the single
enforcement point of the last-admin guard); the service never mutates user
roles directly (D8, REQ-012).

## Consequences
- Multiple roles per user with union-of-permissions (REQ-009, Q-78).
- The role store is the single source of truth for role names; user-management
  validates against it instead of a hardcoded tuple (Q-77).
- The last-admin guard is preserved on every assignment path — no bypass
  (REQ-013, Q-81; ADR-022 extended).
- Breaking changes are fixed within this change's scope: the alembic data
  migration, consumer updates, and test updates are all part of this change
  (Q-97, Section 13 #1–#5).
- `set_role` is preserved (replace semantics) so existing call sites remain
  valid (Q-76).

## Alternatives Considered
- Keeping a single role and adding a separate user→role join table —
  rejected: a join table is a second source of truth for role names and
  complicates the migration; the role list keeps the user record
  self-contained (Q-78).
- Duplicating the role-name list in user-management (a second hardcoded
  tuple) — rejected: two sources of truth for role names would drift; the
  injected `RoleStore` (default static, overridable with the permission
  feature's store) keeps one source of truth (Q-77).
- Dropping `set_role` for a new-only API — rejected: `set_role` is an
  existing contract; preserving it as `set_roles([role])` keeps call sites
  valid (Q-76, Q-97).
- Extending the last-admin guard only to `set_role` — rejected: the new
  `set_roles` / `remove_role` / `delete_user` / `deactivate_user` paths could
  bypass the guard; the guard must apply to every path that removes `admin`
  from the last active admin (Q-81).

## References
- `docs/specs/user-roles-permissions.md` (D4, D5, D8, REQ-012, REQ-013,
  REQ-026; §3 user-management amendment; §13 #1–#5)
- `docs/specs/user-management.md` (single-role schema, `set_role`)
- `docs/decisions/ADR-018-user-management-feature-placement.md`
- `docs/decisions/ADR-022-last-admin-protection.md`
- `AI_Questions.md` (Q-66, Q-76, Q-77, Q-78, Q-81, Q-97)
