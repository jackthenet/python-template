# ADR-008: Lazy Start + Graceful Drain Lifecycle

## Status
Accepted

## Context
The bus has a background worker that must be started and eventually stopped. Requiring an explicit `start()` before any use is a footgun (a forgotten start silently drops all events). On shutdown, pending events should not be silently lost if avoidable. The question is when the worker starts and what `shutdown()` does with pending events.

## Decision
The worker starts lazily on the first `publish()` (or explicitly via `start()`). `shutdown()` gracefully drains events enqueued before it, then stops the worker. `start()` and `shutdown()` are idempotent. The bus is usable as a context manager (`__enter__` starts, `__exit__` shuts down). `publish()` after `shutdown()` is a no-op.

## Consequences
- No footgun from a forgotten `start()` (EDGE-001).
- Pending events are processed on shutdown (REQ-005, AC-008).
- Idempotent start/shutdown prevent double-start and double-shutdown errors (AC-009, EDGE-009).
- Context-manager support enables scoped bus usage (AC-010).

## Alternatives Considered
- Explicit `start()` required — rejected; a forgotten start would silently drop events.
- Discard-on-shutdown — rejected; loses in-flight events unnecessarily.
- Auto-restart after shutdown — rejected; surprising and complicates the lifecycle.

## References
- `docs/specs/event-bus.md` (REQ-005, AC-008, AC-009, AC-010, EDGE-007, EDGE-009, design decision D5)
