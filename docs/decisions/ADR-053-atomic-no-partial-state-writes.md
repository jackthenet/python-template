# ADR-053: Atomic no-partial-state writes (temp file + rename, mutual rollback)

## Status
Accepted

## Context
A failed or interrupted upload must leave no partial state (REQ-008,
INV-001 — a HARD invariant): no temp file, no orphaned storage content, no
orphaned metadata record. An upload produces **two** artifacts that can fail
independently — the storage content (written to disk) and the metadata
record (written to SQLite) — and avatar uploads add variant files. Any
failure point between "start writing" and "fully committed" must roll back
to the pre-upload state.

## Decision
Content is written to a **temp file** in the storage root and **atomically
renamed** (`os.replace`) into the key path at the storage level, so the key
path never holds a partially written file. At the service level, the two
artifacts are **rolled back against each other**: if the storage write
fails, no metadata record is created; if the metadata record cannot be
created, the storage content (and any variant content) is deleted. A variant
generation failure rolls back the entire upload (EDGE-013).

## Consequences
- No orphaned/partial state at any failure point (INV-001); a reader never
  observes a half-written file (the key path appears atomically).
- The upload path is slightly more complex (temp file, rename, rollback of
  the two-artifact boundary).
- Rollback is best-effort cleanup of artifacts this operation created; it
  never deletes pre-existing state.
- The invariant is testable by injecting faults at each stage (AC-016,
  AC-017, EDGE-013).

## Alternatives Considered
- Write directly to the key path and clean up on error — rejected: the
  cleanup itself can fail, leaving orphans, and a concurrent reader could
  observe a partial file.
- A database transaction spanning the filesystem — rejected: impossible
  across the storage/metadata boundary.
- At-least-once writes with a reconciliation job — rejected: adds a
  background system for a problem the temp-file + rename + rollback design
  solves synchronously.

## References
- `docs/specs/file-management.md` (REQ-008, INV-001, EDGE-013; D4)
- `docs/decisions/ADR-054-last-write-wins-concurrency.md`
