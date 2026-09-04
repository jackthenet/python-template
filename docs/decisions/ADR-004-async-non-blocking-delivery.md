# ADR-004: Async Non-Blocking Delivery via a Single Background Worker

## Status
Accepted

## Context
The core value of the event bus is decoupling: a publisher should not be delayed by slow handlers. A synchronous inline dispatch would block the publisher until every handler completes — which the discovery process judged equivalent to calling the handler's feature directly, so nothing is gained. The publisher must return immediately and the handlers must run elsewhere. The question is how dispatch is executed and how many worker threads are used.

## Decision
`publish()` enqueues the event onto a bounded queue and returns without waiting for handlers. A single background worker thread drains the queue and dispatches each event to its matching handlers, FIFO, one event at a time. Handlers for a single event run in subscription order.

## Consequences
- The publisher is never blocked by handler execution (REQ-001, NFR-001).
- A single worker preserves FIFO ordering and avoids dispatch-level thread-safety complexity (D7).
- A slow handler delays subsequent events (but never the publisher).
- Exactly one worker thread is used (NFR-003).

## Alternatives Considered
- Synchronous inline dispatch — rejected; blocks the publisher, no decoupling benefit.
- Multiple worker threads — rejected for the template; adds dispatch thread-safety complexity and loses ordering, with little benefit at this scale.
- `asyncio`-based worker — rejected; the bus is consumed from plain (non-async) feature code and must not require an event loop.

## References
- `docs/specs/event-bus.md` (REQ-001, NFR-001, NFR-003, design decisions D1, D7)
