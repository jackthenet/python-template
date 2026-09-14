# ADR-052: Flat opaque keys with logical namespaces

## Status
Accepted

## Context
The store must be safe (nothing can construct a path, REQ-016, INV-007) and
simple. A folder/directory hierarchy in the public API would introduce a
path-traversal surface (keys containing separators), complicate atomic
renames (moving across directories is not atomic), and add directory
lifecycle concerns (creating/deleting empty directories). Object-store
semantics (flat keys, no directories) are simpler and safer.

## Decision
Keys are flat and opaque (object-store style): a caller-specified key must
match `KEY_PATTERN` (no path separators, no null bytes, no traversal), else
`FileValidationError` (reason `invalid_key`); when no key is given, the
service generates a canonical UUID key. A "namespace" is a **logical
metadata field** (e.g. `general`, `avatars`), not a real directory; it is
used for policy (allowed types, size limit) and for prefix listing, not for
layout. "Folders" are not in the public API; the local backend stores one
file per key directly under the root.

## Consequences
- One key pattern plus root containment is the entire path-safety story
  (REQ-016, INV-007); no traversal surface exists.
- Atomic rename at the storage level stays a single-directory operation.
- No directory operations (no empty-directory lifecycle, no nested moves).
- Logical organization lives in metadata (namespace prefix listing), which
  is queryable and independent of the storage layout.

## Alternatives Considered
- Directory-based folders in the public API — rejected: path-traversal
  surface, non-atomic cross-directory moves, directory lifecycle
  (explicitly out of scope: "folders/directories (the store is flat)").
- Key prefixes mapped to real directories — rejected: the same traversal
  concern and unnecessary coupling between metadata and layout.
- Caller-controlled layout — rejected: the service must own the layout so
  the security invariants hold regardless of caller.

## References
- `docs/specs/file-management.md` (REQ-007, REQ-016, INV-007; D2, D13)
- `docs/decisions/ADR-050-storage-backend-abstraction.md`
