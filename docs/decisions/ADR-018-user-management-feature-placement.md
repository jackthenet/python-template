# ADR-018: User management feature placement

## Status
Accepted

## Context
The user management feature is a backend capability: it manages user account
records (create, read, update, delete, password, role, activation) and
persists them in SQLite. The project organizes code around features as the
primary architectural boundary, with `frontend` and `backend` as runtime
boundaries inside `src/`. The frontend is out of scope for this feature
(implemented in a separate workflow).

## Decision
The user management feature lives at `src/backend/usermanagement/` as a
backend feature package using the service + repository pattern: `UserManager`
(use cases, validation, domain rules) depends only on the `UserRepository`
ABC, and `SqliteUserRepository` implements the ABC with SQLModel/SQLite. The
public API is exposed through the package `__init__.py`
(`backend.usermanagement`), and no other feature imports its internal modules
directly.

## Consequences
- The feature is discoverable and traceable from spec to implementation
  (`docs/specs/user-management.md` → `src/backend/usermanagement/` →
  `tests/*/usermanagement/`).
- The service is testable against any `UserRepository` implementation
  (fakes, SQLite, a future database) without changing service code.
- Consumers depend on the `backend.usermanagement` public API only.

## Alternatives Considered
- A shared `src/backend/shared/usermanagement/` location — rejected: user
  management is a feature, not shared infrastructure; `shared/` is
  deliberately small.
- A top-level `src/usermanagement/` outside the runtime boundaries —
  rejected: violates the frontend/backend boundary rule.
- A single flat module instead of service + repository — rejected: the spec
  requires the database to be swappable later (REQ-013), which the
  repository ABC provides.

## References
- `docs/specs/user-management.md` (Target Component: `src/backend/usermanagement/`; D1)
- `AGENTS.md` — Project Structure
- ADR-010 (Settings feature placement)
