# ADR-058: Typed lifecycle events via a structural EventPublisher

## Status
Accepted

## Context
Features communicate asynchronously via the event bus (repository pattern).
file-management must publish lifecycle events (REQ-022) so that other
features can react (e.g. an audit feature), but it must **not** hard-depend
on `backend.eventbus`'s source — the event integration is a structural
protocol, consistent with user-management and authentication (ADR-021).
Events must carry non-sensitive data only (NFR-002).

## Decision
The service publishes **typed lifecycle events** — `FileUploaded`,
`FileDownloaded`, `FileDeleted`, `FileValidationFailed`, `AvatarUploaded`,
`AvatarDeleted` — to an injected **structural `EventPublisher`** (an object
with a `publish(event)` method; the real event bus satisfies it and is
injected at wiring time). A `None` publisher means no events and no error
(AC-050). Events carry non-sensitive data only (no file content). A
publisher that raises propagates to the caller **after** the operation is
committed (EDGE-014). No event is published on failure except
`FileValidationFailed` on a validation failure (INV-006).

## Consequences
- No import of `backend.eventbus`: loose coupling; the feature is testable
  with a collector publisher and usable with no publisher.
- Event consumers can subscribe to the typed lifecycle (audit, analytics).
- Non-sensitive data only (NFR-002); file content never appears in events.
- A publisher exception propagates after commit — documented (EDGE-014),
  so a failing subscriber cannot roll back a committed operation.

## Alternatives Considered
- Importing the shared `get_event_bus()` singleton — rejected: a hard
  dependency on the event-bus feature's source; the structural protocol is
  the established pattern (ADR-021).
- Callbacks — rejected: not an established pattern in this repository.
- No events — rejected: breaks the repository pattern and leaves no seam
  for reactive features.

## References
- `docs/specs/file-management.md` (REQ-022, INV-006, EDGE-014; D10)
- `docs/decisions/ADR-021-structural-event-publisher-protocol.md`
