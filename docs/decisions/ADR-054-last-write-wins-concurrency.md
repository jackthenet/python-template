# ADR-054: Last-write-wins concurrency for same-key uploads

## Status
Accepted

## Context
Concurrent uploads to the same key must have a well-defined outcome
(REQ-009, INV-002, EDGE-017). There is no HTTP layer or versioning
requirement; the store is flat and object-store-like. The semantics must be
simple, correct under concurrency, and require no error handling by callers
who are not expecting a conflict.

## Decision
Concurrent uploads to the same key are **last-write-wins**: `put()`
atomically replaces any existing content (temp file + rename), and the
repository `add()` atomically replaces the existing record (the replaced
record is deleted). Exactly one winner, no error is raised. A concurrent
`download` returns either the old or the new content — a complete file,
never partial (EDGE-017).

## Consequences
- Simplest correct concurrency semantics: no conflict errors, no versioning
  state, no locks to manage.
- A concurrent uploader can silently replace another's file — accepted for
  user files where the caller owns the key.
- Readers always observe a complete file (old or new), never partial
  (INV-001/INV-002, EDGE-017).
- The final state is exactly one file record and one storage content for
  the key (REQ-009).

## Alternatives Considered
- Reject concurrent writes (conflict error) — rejected: complex, forces
  callers to handle a conflict they did not expect, and is not object-store
  semantics.
- File versioning — rejected: explicitly out of scope.
- Optimistic locking (ETag/compare-and-swap) — rejected: no HTTP layer, no
  versioning requirement; unnecessary complexity.

## References
- `docs/specs/file-management.md` (REQ-009, INV-002, EDGE-017; D5)
- `docs/decisions/ADR-053-atomic-no-partial-state-writes.md`
