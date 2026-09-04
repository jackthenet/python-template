# ADR-006: Handler Error Isolation

## Status
Accepted

## Context
In a decoupled system, one misbehaving handler must not take down the bus or prevent other handlers from receiving the event. The worker thread must survive handler exceptions, and the publisher must never observe handler errors (the publisher is decoupled from handler implementation). The question is how handler exceptions are handled in the dispatch loop.

## Decision
Each handler invocation in the worker dispatch loop is wrapped in a try/except. A handler's exception is caught and logged (via the shared logging feature), other handlers for the same event still run, and the exception never propagates to the publisher or crashes the worker.

## Consequences
- A handler failure never prevents other handlers from receiving the event (REQ-003, INV-002, NFR-002).
- The worker thread is resilient to handler exceptions.
- The publisher is unaffected by handler errors (REQ-003).
- Handler errors are observable via logs.

## Alternatives Considered
- Let the exception propagate — rejected; crashes the worker and/or surfaces handler errors to the publisher, breaking decoupling.
- Kill the worker on a handler exception — rejected; a single bad handler would take down the whole bus.
- Retry failed handlers — rejected; adds complexity and retry semantics not in scope.

## References
- `docs/specs/event-bus.md` (REQ-003, INV-002, NFR-002, EDGE-008, design decision D3)
