# ADR-056: Common persistence root `./data/` as a layout convention

## Status
Accepted

## Context
User files and each feature's own persistence (SQLite databases, YAML
value/template files) were scattered with no common layout. The user wanted
a unified, predictable file layout. However, features must **not** depend on
each other's persistence: centralizing persistence would create a dependency
tangle and is explicitly out of scope ("each feature keeps its own
SQLite/YAML persistence"). The layout must be unified without a code
dependency.

## Decision
Establish a **normative layout convention** (REQ-026): a common persistence
root `./data/`. User files live under `./data/files/` (the default
`filemanagement.storage_root` setting), and each feature's own persistence
lives in its own subdirectory under `./data/`. This is a **layout
convention only, not a code dependency** — no shared persistence service, no
shared module; each feature keeps its own storage. The convention is
enforced by tests (AC-055), not by the type system.

## Consequences
- Unified, predictable file layout across the application; easy to locate,
  back up, or relocate all persisted files.
- No shared code or dependency between features; the convention is cheap to
  state and cheap to break (it is a convention).
- The convention is enforced by tests (AC-055), so drift is caught but not
  prevented by construction.

## Alternatives Considered
- A shared persistence service — rejected: a dependency tangle and scope
  creep; each feature would route its storage through another feature.
- Per-feature arbitrary roots — rejected: the scattered layout the user
  wanted to avoid.
- Centralizing all persistence under file-management — rejected: explicitly
  out of scope; file-management stores user files, not other features'
  metadata.

## References
- `docs/specs/file-management.md` (REQ-026, Out of Scope; D14)
- `docs/decisions/ADR-050-storage-backend-abstraction.md` (the default root)
