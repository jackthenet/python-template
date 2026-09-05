# ADR-005: Bounded Queue with Drop-on-Full Backpressure

## Status
Accepted

## Context
Because `publish()` must never block, the queue cannot use a blocking put when full. A queue that grows without bound risks unbounded memory growth if handlers are slow or a burst of events arrives. The bus must choose a backpressure policy: cap memory, never block the publisher, and handle the "queue full" case explicitly.

## Decision
The queue is bounded at `max_queue_size` (default 1000). `publish()` enqueues with a non-blocking put; when the queue is full, the event is dropped, an error is logged, and `dropped_count` is incremented. `publish()` never blocks.

## Consequences
- Memory is bounded by `max_queue_size` (REQ-007, NFR-003, INV-003).
- Under backpressure, events can be dropped (logged + counted, not silent).
- The publisher is never blocked by a full queue (REQ-001, NFR-001).
- `dropped_count` and `pending_count` expose backpressure state.

## Alternatives Considered
- Unbounded queue — rejected; risks unbounded memory growth under slow handlers or bursts.
- Bounded queue, reject-on-full (return a status) — rejected for the template; complicates the `publish()` API and pushes drop handling onto every publisher.
- Bounded queue, block-on-full — rejected; violates the non-blocking `publish()` constraint.

## References
- `docs/specs/event-bus.md` (REQ-007, NFR-003, INV-003, EDGE-002, design decision D4)
