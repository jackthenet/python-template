# ADR-017: Registry singleton and thread safety

## Status
Accepted

## Context
Features need a shared default registry (REQ-014), tests and DI need
instantiable registries, and registration must be thread-safe (REQ-005,
AC-038). The registry holds mutable state: the definition map, the current
values, and the template repository.

## Decision
`get_settings_registry()` returns a module-level shared default
`SettingsRegistry` (created lazily); `reset_settings_registry()` discards
it for tests. `SettingsRegistry` is a plain instantiable class with
constructor injection for the event bus and template repository. All
registry state is guarded by a single `threading.RLock`: reads and writes
of the definition map, the value map, and template operations acquire the
lock, so concurrent registration and value access are safe.

## Consequences
- The singleton pattern matches the event-bus feature
  (`get_event_bus()`/`reset_event_bus()`), keeping the project's shared
  defaults consistent (AC-018).
- A single RLock is sufficient because all operations are short
  in-memory mutations; there are no long-held lock sections that would
  need finer granularity.
- Instantiability means tests can build isolated registries with in-memory
  repositories and custom buses without touching the singleton.

## Alternatives Considered
- A per-feature registry only (no singleton) — rejected: REQ-014 requires a
  shared default for features.
- Lock-free state with immutable snapshots — rejected: adds complexity
  without benefit at this scale, and template repository state is
  inherently mutable.

## References
- `docs/specs/settings.md` — REQ-005, REQ-014, AC-018, AC-038
