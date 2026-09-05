# ADR-010: Settings feature placement

## Status
Accepted

## Context
The settings feature is a backend capability: it manages in-memory setting
definitions/values and persists template files. The project organizes code
around features as the primary architectural boundary, with `frontend` and
`backend` as runtime boundaries inside `src/`.

## Decision
The settings feature lives at `src/backend/settings/` as a backend feature
package. Its public API is exposed through the package `__init__.py`
(`backend.settings`), and no other feature imports its internal modules
directly.

## Consequences
- The feature is discoverable and traceable from spec to implementation
  (`docs/specs/settings.md` → `src/backend/settings/` →
  `tests/*/settings/`).
- Template file I/O is a backend concern; no frontend boundary is involved.
- Consumers depend on the `backend.settings` public API only.

## Alternatives Considered
- A shared `src/backend/shared/settings/` location — rejected: settings is a
  feature, not shared infrastructure; `shared/` is deliberately small.
- A top-level `src/settings/` outside the runtime boundaries — rejected:
  violates the frontend/backend boundary rule.

## References
- `docs/specs/settings.md` (Target Component: `src/backend/settings/`)
- `AGENTS.md` — Project Structure
