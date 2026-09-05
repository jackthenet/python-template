# ADR-003: Event Bus Feature Placement Under src/backend/eventbus/

## Status
Accepted

## Context
The event bus is a backend-only capability for decoupling communication between backend features. The repository's AGENTS.md defines `src/` as the single source package with `frontend/` and `backend/` as runtime boundaries inside it, and features live directly under their runtime boundary (no `features/` intermediate layer). The logging feature established the pattern of a self-contained feature module under `src/backend/` (ADR-001).

## Decision
The event bus is placed at `src/backend/eventbus/` as a backend feature. It is importable as `backend.eventbus` and exposes `EventBus`, `get_event_bus`, and `reset_event_bus` through its `__init__.py`.

## Consequences
- Consumers import via `from backend.eventbus import EventBus, get_event_bus, reset_event_bus`.
- The feature is testable in isolation without frontend wiring.
- Frontend concerns (none expected) would live under `src/frontend/` and would not share this module.
- The module name is `eventbus` (no hyphen) because it is a Python identifier; the feature/branch name is `event-bus`.

## Alternatives Considered
- `src/features/eventbus/` — rejected; AGENTS.md no longer prescribes a `features/` layer.
- `src/shared/eventbus/` — rejected; the bus is a backend concern, not genuinely shared across multiple features' runtime boundaries.
- `src/core/eventbus/` — rejected; the core structure is no longer supported per AGENTS.md.

## References
- `docs/specs/event-bus.md` (REQ-001 through REQ-007)
- `AGENTS.md` (Project Structure section)
- ADR-001 (logging feature placement)
