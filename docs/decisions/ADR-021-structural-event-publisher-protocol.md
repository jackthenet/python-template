# ADR-021: Structural EventPublisher protocol instead of a hard event-bus dependency

## Status
Accepted

## Context
The service must publish typed lifecycle events after each successful mutation
(REQ-016, REQ-017). The project already has a shared event bus feature
(`backend.eventbus`), but importing it directly would make this feature
hard-depend on another feature's source. The publisher is optional
(`None` → no events, no errors) and a publisher exception propagates to the
caller with the mutation already committed (EDGE-020).

## Decision
Define a structural `EventPublisher` protocol (`def publish(self, event:
object) -> None`) in this feature (`events.py`). `UserManager` receives an
`EventPublisher | None` via constructor injection; the real event bus is
injected at wiring time. This feature does not import `backend.eventbus`.

## Consequences
- The feature boundary is preserved: `backend.usermanagement` has no
  compile-time dependency on `backend.eventbus` source.
- Tests use trivial collector fakes; no event-bus lifecycle (worker,
  shutdown) is needed to verify events.
- The structural protocol is satisfied by any object with a `publish`
  method, including the shared event bus, so wiring is a one-line injection.

## Alternatives Considered
- Import `get_event_bus()` from `backend.eventbus` inside the service —
  rejected: hard cross-feature dependency; the spec explicitly forbids
  importing `backend.eventbus` from this feature.
- A base class that events must inherit from — rejected: events are plain
  Pydantic models; the publisher protocol is on the publisher, not the
  event.
- Synchronous in-process event dispatch owned by this feature — rejected:
  reinvents the shared event bus feature.

## References
- `docs/specs/user-management.md` (REQ-016, REQ-017; D10, D11; EDGE-020)
- `docs/specs/event-bus.md`
- ADR-016 (SettingChanged event integration)
