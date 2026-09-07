# ADR-020: SQLite/SQLModel behind the UserRepository ABC with create_all bootstrap

## Status
Accepted

## Context
User records must be persisted (REQ-013), but the database must be swappable
later. The spec puts a persistent database migration/upgrade framework out of
scope; table bootstrap via `create_all` only is acceptable (D8). The
repository must be safe for concurrent use from multiple threads (NFR-004) and
must auto-create the DB file's parent directory (EDGE-007).

## Decision
Use `SqliteUserRepository` (SQLModel/SQLite) as the default concrete
repository implementing the `UserRepository` ABC. Tables are bootstrapped via
`SQLModel.metadata.create_all` at repository init (no migration framework).
Uniqueness is enforced at the database level (`uq_users_username`,
`uq_users_email`), and constraint violations in `add` are mapped to
`UserAlreadyExistsError.field` as a race guard. The `UserManager` service
references only the ABC, never the concrete class.

## Consequences
- The database can be replaced later by adding a new `UserRepository`
  implementation; service code is untouched (AC-028 proves it with a fake).
- `create_all` bootstrap is simple but non-upgrading: schema changes after
  initial creation are out of scope until a migration framework is specified.
- SQLite file I/O is a backend concern; `sqlite:///:memory:` gives isolated
  per-instance stores for tests (EDGE-008).
- A new runtime dependency (`sqlmodel>=0.0.42`, already in `pyproject.toml`)
  pulling in SQLAlchemy.

## Alternatives Considered
- Raw SQLAlchemy Core/ORM without SQLModel — rejected: SQLModel unifies the
  Pydantic-style models and ORM in one package, matching the spec's model
  definitions.
- A migration framework (Alembic) from day one — rejected: explicitly out of
  scope; `create_all` bootstrap is sufficient for the specified behavior.
- ORM-only enforcement of uniqueness (no DB constraints) — rejected: the
  database constraints are the race guard for concurrent creates (EDGE-015).

## References
- `docs/specs/user-management.md` (REQ-013, NFR-004; D1, D8; EDGE-007, EDGE-008, EDGE-015)
- ADR-018 (User management feature placement)
