# ADR-009: Module Singleton + Instantiable Sharing

## Status
Accepted

## Context
For features to communicate via the bus, they must share a single bus instance. A global default makes this convenient (features just import and use it). But tests and explicit dependency injection need isolated instances. The question is how the shared instance is provided while keeping the bus instantiable.

## Decision
`get_event_bus()` returns a module-level default singleton for features to share. The `EventBus` class is also directly instantiable for tests and dependency injection. `reset_event_bus()` resets the default instance (for tests).

## Consequences
- Features share one bus via `get_event_bus()` without wiring (REQ-006, AC-011).
- Tests use isolated `EventBus()` instances (no cross-test contamination).
- `reset_event_bus()` enables clean test teardown of the default.
- The singleton is lazily created on first `get_event_bus()`.

## Alternatives Considered
- Instantiable only (no global) — rejected; forces every feature to receive the bus instance, adding wiring.
- Singleton only (no instantiable class) — rejected; makes isolated testing hard.
- Per-feature bus namespaces — rejected; over-engineered for this scope.

## References
- `docs/specs/event-bus.md` (REQ-006, AC-011, design decision D6)
