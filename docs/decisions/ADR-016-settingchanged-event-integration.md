# ADR-016: SettingChanged event integration

## Status
Accepted

## Context
Value changes must be observable to other features through the shared event
bus (REQ-024): `set_value`, `reset`, `reset_all`, and template loads all
change values. The registry must accept an explicit bus and default to the
shared bus (REQ-025, AC-037).

## Decision
Every value change publishes a `SettingChanged` event (key, value,
previous) to the event bus. The registry resolves its bus once at
construction: an explicitly injected `event_bus` is used when provided,
otherwise the shared default bus from `get_event_bus()`. Template loads
publish one event per setting they set, because loads route through the
normal `set_value` path. No other events are published (registration,
template CRUD, lookups are silent).

## Consequences
- Consumers (e.g., a future frontend renderer) can react to any value
  change with a single subscription (AC-035, AC-036).
- Exactly one event per setting changed, including when the new value
  equals the previous value (INV-008, EDGE-021) — the event is a change
  notification, not a delta.
- Publishing is best-effort: if the bus is shut down, events are dropped
  without error (EDGE-022), so value changes never fail because of
  observability.

## Alternatives Considered
- Publish only when the value actually changes — rejected: the spec
  requires an event per change operation (INV-008, EDGE-021), and
  "no-op" detection would couple the bus to value equality semantics.
- Letting the registry own a bus it creates — rejected: the shared bus is
  the single event backbone; a private bus would fragment events.

## References
- `docs/specs/settings.md` — REQ-024, REQ-025, AC-035 … AC-037, AC-039,
  INV-008, EDGE-021, EDGE-022
