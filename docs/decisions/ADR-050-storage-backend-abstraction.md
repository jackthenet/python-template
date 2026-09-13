# ADR-050: StorageBackend ABC with local-disk default and public in-memory backend

## Status
Accepted

## Context
File content must be stored durably, but the service must not hardcode a
disk layout: cloud backends (e.g. S3) are explicitly out of scope now but
"can be added later behind the `StorageBackend` interface" (spec, Out of
Scope, REQ-015). Tests and dependency injection need an isolated storage
that does not pollute the real disk. The service code must reference only
the abstraction so that the storage mechanism is swappable later.

## Decision
Define a `StorageBackend` ABC (put/get/delete/exists/stat). Provide two
implementations: `LocalDiskStorageBackend` (the default — flat layout, one
file per key directly under the root, root from the live
`filemanagement.storage_root` setting, with path containment and symlink
rejection per D13) and `InMemoryStorageBackend` (a dict of key → bytes,
**public** for tests/DI, instances isolated). The backend is a constructor
argument; `None` constructs the local-disk backend from the live setting.

## Consequences
- Swappable storage: a cloud backend can be added later without touching
  `FileService`.
- Test isolation: tests and DI use the public in-memory backend; no test
  pollutes the real disk (AC-030, EDGE-016).
- The in-memory backend is part of the public API (NFR-003 backward
  compatibility contract).
- Two implementations to maintain; the local backend carries the security
  enforcement (containment, symlink rejection).

## Alternatives Considered
- Disk-only storage — rejected: tests would pollute the real disk and there
  would be no seam for a cloud backend (REQ-015).
- A private in-memory backend — rejected: the spec makes it public for
  tests/DI so callers can inject it (AC-030).
- A filesystem access object (open/stat directly) — rejected: not an
  established pattern and it would leak disk semantics into the service.

## References
- `docs/specs/file-management.md` (REQ-015, REQ-016, NFR-003; D1, D13)
- `docs/decisions/ADR-051-sqlite-file-repository.md` (the metadata-side twin)
