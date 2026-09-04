# ADR-001: Logging Feature Placement Under src/backend/

## Status
Accepted

## Context
The logging feature must be importable without application wiring, and the repository's AGENTS.md defines `src/` as the single source package with `frontend/` and `backend/` as runtime boundaries inside it. The obsolete `src/core/logging/` module was deleted in favor of a self-contained feature module. The question is where the logging feature lives within `src/`.

## Decision
The logging feature is placed at `src/backend/logging/` as a backend feature. It is importable as `backend.logging` and exposes `setup_logger`, `logged`, and `logged_class` through its `__init__.py`.

## Consequences
- Consumers import via `from backend.logging import setup_logger, logged, logged_class`.
- The feature is testable in isolation without frontend wiring.
- Future frontend logging concerns (if any) would live under `src/frontend/` and would not share this module.
- The `features/` intermediate directory is eliminated; features live directly under their runtime boundary.

## Alternatives Considered
- `src/features/logging/` — rejected because AGENTS.md no longer prescribes a `features/` layer; features live directly under `src/frontend/` or `src/backend/`.
- `src/shared/logging/` — rejected because logging is a backend concern (sink setup, stdlib interception, server-side decorators); it is not genuinely shared by multiple features.
- `src/core/logging/` — rejected because the core structure is no longer supported per AGENTS.md.

## References
- `docs/specs/logging.md` (REQ-001 through REQ-009)
- `AGENTS.md` (Project Structure section)
- Commit `7db81ee` (deletion of obsolete `src/core/logging/`)
