# ADR-024: UserRead as the only user representation returned by the service

## Status
Accepted

## Context
The service API must not expose `password_hash` or the raw `User` table
object (spec constraint, REQ-004, NFR-002, D9). Returning the SQLModel table
object directly would leak the hash and couple callers to the persistence
model; returning ad-hoc dicts would give no type contract.

## Decision
`UserRead` is the only user representation returned by the service
(`create_user`, `get_user`, `get_user_by_username`, `list_users`,
`update_user`, `set_role`, `activate_user`, `deactivate_user`). It carries
`id`, `username`, `email`, `display_name`, `role`, `profile_picture_url`,
`is_active`, `created_at`, `updated_at` — and no `password_hash` field. The
raw `User` table object stays inside the repository/service boundary.

## Consequences
- The hash and the persistence model are never exposed through the public
  API (AC-010, NFR-002); adding a field to `UserRead` is a deliberate,
  backward-compatible contract change (NFR-003).
- Callers get a typed, Pydantic-validated read model that is stable across
  database swaps.
- The service must construct `UserRead` explicitly from `User` (a small
  mapping step) rather than returning table objects.

## Alternatives Considered
- Returning the `User` SQLModel object with the hash field hidden via model
  configuration — rejected: the table object is still reachable and the
  persistence model leaks into the API contract.
- Returning plain dicts — rejected: no type contract; field typos become
  silent.
- Separate read models per operation — rejected: all operations return the
  same user shape; one model is simpler and satisfies NFR-003.

## References
- `docs/specs/user-management.md` (REQ-004, NFR-002, NFR-003; D9; AC-010)
