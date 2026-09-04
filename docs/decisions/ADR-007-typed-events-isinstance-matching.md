# ADR-007: Typed Events with isinstance Matching

## Status
Accepted

## Context
Handlers must subscribe to specific kinds of events, and a published event must be routed to the right handlers. The events are typed objects (typically Pydantic models or dataclasses). The question is how a published event is matched to subscribed handlers: by exact type, or by type hierarchy.

## Decision
A handler is registered for an event type via `subscribe(event_type, handler)`. A published event is dispatched to every handler whose registered type matches the event by `isinstance(event, event_type)`. This means subscribing to a base event type also receives subclass events (catch-all), while subscribing to a leaf type receives only that type and its subclasses.

## Consequences
- Flexible, Pythonic matching: base-type subscription is a catch-all (REQ-002, AC-004).
- Leaf-type subscription is precise (REQ-002, AC-002, AC-003).
- Events need no required base class; any class is a valid event type.
- Matching is O(handlers) per event (acceptable at this scale).

## Alternatives Considered
- Exact type match (`type(event) is event_type`) — rejected; loses the catch-all convenience of subscribing to a base type.
- String topic names — rejected; the discovery process chose typed event classes over untyped topics.
- Wildcard/glob topics — rejected; out of scope.

## References
- `docs/specs/event-bus.md` (REQ-002, AC-002, AC-003, AC-004, design decision D2)
