# ADR-046: Per-send transport independence (no long-lived connection, no persistence)

## Status
Accepted

## Context
The spec requires the service to be safe for concurrent use from multiple threads (REQ-016, NFR-005) and requires that a failure in one send does not affect subsequent sends (INV-005, EDGE-010). A long-lived SMTP connection carries state across sends (connection liveness, authentication, TLS session) — a failure would leave the service in a state that affects the next send, and shared connection state would need synchronization for thread safety.

The spec also scopes out persistence of sent emails (D12): no database, no file.

## Decision
Each send is independent:

- The transport is **created per send** (when the service has no injected transport, it builds a `SmtpTransportImpl` from the live settings on each send): it opens the SMTP connection, sends the message, and closes. There is no long-lived connection and no connection lifecycle to manage.
- The service holds **no per-send mutable state**: a failed send leaves nothing behind that a later send reads.
- The service does **not persist sent emails** (no database, no file): the observable outputs are the returned `EmailSendResult`, the raised `MailError` (on failure), and the published lifecycle events.

## Consequences
- Failure isolation: after a failed send, the next send is evaluated independently (INV-005, EDGE-010) — there is no connection state to carry over.
- Thread safety without locks: concurrent sends each own their transport; there is no shared mutable state to synchronize (REQ-016, NFR-005).
- No connection lifecycle management (no keep-alive, no reconnect policy, no pool) — the feature is simpler and the per-send cost is one SMTP connection, which is acceptable for low-frequency mail.
- No persistence surface: nothing to store, expire, or leak; the security contract (NFR-002) applies only to the in-memory observable outputs.

## Alternatives Considered
- A pooled / long-lived SMTP connection with reconnection — rejected: connection state would leak across sends, defeating failure independence; the pool adds lifecycle, reconnection, and thread-safety complexity the feature does not need.
- Queueing and retry of failed sends — rejected: explicitly out of scope (the spec scopes queueing/retry out); retry would add state (the queue) and complicate the independence contract.
- Persistence of sent emails (an audit store) — rejected: out of scope (D12); it would add a storage dependency and a new leak surface for the tokens in the bodies.
- A single shared transport instance owned by the service — rejected: shared connection state across sends and across threads; a failure would affect subsequent sends.

## References
- `docs/specs/mail-service.md` (D12, D13; REQ-016; INV-005; EDGE-010; NFR-005)
- `docs/decisions/ADR-043-smtp-transport-abstraction.md` (the transport seam this decision builds on)
