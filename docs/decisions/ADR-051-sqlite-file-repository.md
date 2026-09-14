# ADR-051: FileRepository ABC with SQLite/SQLModel default

## Status
Accepted

## Context
File metadata (REQ-012) must persist durably across service instances
(REQ-013, AC-025) and support queries (get by key/id, list by namespace
prefix with pagination, REQ-014). The database must remain changeable later,
and the service must depend only on the abstraction. The repository-ABC
pattern is the established pattern in this repository (user-management,
ADR-020).

## Decision
Define a `FileRepository` ABC (add/get_by_key/get_by_id/update/delete/
list_by_namespace plus the avatar mapping operations set_user_avatar/
get_user_avatar/clear_user_avatar). Provide `SqliteFileRepository` as the
default concrete repository: SQLite via SQLModel, bootstrap via
`create_all` (no migration framework), the DB file's parent directory
auto-created. `FileService` depends only on the ABC (constructor
injection), so a non-SQLite repository works (AC-026).

## Consequences
- Durable, queryable metadata with persistence across instances (AC-025).
- Swappable metadata storage: the service is insulated from the database.
- Reuses the existing `sqlmodel`/`sqlalchemy` project dependency; no new
  dependency.
- No migration/upgrade framework (bootstrap via `create_all` only) — an
  accepted scope boundary.
- The service works with a test fake repository (AC-026), keeping tests
  fast and isolated.

## Alternatives Considered
- JSON/YAML file storage for metadata — rejected: no concurrency safety
  (NFR-004) and no query support (prefix listing, pagination).
- A full ORM abstraction layer — rejected: premature; the repository ABC is
  the established, lighter pattern in this repository.
- In-memory-only metadata — rejected: no durability (REQ-013, AC-025).

## References
- `docs/specs/file-management.md` (REQ-012, REQ-013, REQ-014, NFR-004; D1)
- `docs/decisions/ADR-020-sqlite-sqlmodel-repository.md` (user-management)
