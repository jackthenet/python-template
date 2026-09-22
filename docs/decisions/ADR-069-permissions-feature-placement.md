# ADR-069: Permissions feature placement (new shared RBAC feature)

## Status
Accepted

## Context
The backend needs an in-process RBAC authorization capability usable from all
six existing features (usermanagement, authentication, settings,
filemanagement, mail, sessionmanagement): a check API, runtime-managed roles
with dynamic role→permission grants, and a configurable system principal. No
third-party dependency is introduced (the spec confirms none). The repository
pattern is standalone features with service + repository, constructor DI,
module singleton + reset (ADR-018, ADR-025, ADR-061 placement style).

## Decision
Create `src/backend/permissions/` as a standalone feature (REQ-001..REQ-023,
REQ-027..REQ-029). `PermissionService` (use cases, validation, domain rules)
depends only on repository ABCs (`RoleRepository`, `GrantRepository`,
`SystemPrincipalRepository`), the `UserManager` (user lookup +
role-assignment delegation), and a structural session-lookup seam. SQLite
implementations use SQLModel; in-memory implementations serve tests/DI. A
module singleton (`get_permission_service()`) + reset
(`reset_permission_service()`) follow the session-management pattern. The
feature is the cross-feature interface all six features depend on for checks
— reached through the shared enforcement plumbing (ADR-070), never by direct
import from the six features. `PermissionService` is traced via
`@logged_class` with `include_args=False` (REQ-028).

## Consequences
- One shared authorization capability; the six features depend on it without
  importing it (dependency inversion via the shared plumbing).
- No new third-party dependencies; the check path stays in-process over the
  existing SQLite state (NFR-001).
- Consistent with the repository feature pattern: constructor DI, in-memory
  variants for tests, singleton + reset (ADR-065 pattern).
- Role CRUD, grants, and the system principal live on the service; the
  repositories are the storage seam (REQ-022, REQ-023).

## Alternatives Considered
- A third-party RBAC library (e.g., a policy engine) — rejected: the
  vocabulary is a closed 60-action catalog over existing SQLite
  user/session state; a new dependency for in-process checks is not the
  better engineering choice (dependencies section; no new dependency, spec §2).
- Embedding the checks in user-management (the account store) — rejected:
  authorization policy is a distinct concern from account management; the
  other five features would then depend on user-management for
  authorization, coupling unrelated change drivers (the ADR-061
  store-reuse-vs-new-feature reasoning applies in reverse).

## References
- `docs/specs/user-roles-permissions.md` (REQ-001..REQ-023, REQ-027..REQ-029;
  §1, §2, §3)
- `docs/specs/session-management.md` (singleton + reset pattern)
- `docs/decisions/ADR-018-user-management-feature-placement.md`
- `docs/decisions/ADR-025-authentication-feature-placement.md`
- `docs/decisions/ADR-061-session-store-reuse-constructor-di.md`
- `AI_Questions.md` (Q-66, Q-93, Q-96)
