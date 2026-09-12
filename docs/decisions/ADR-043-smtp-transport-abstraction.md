# ADR-043: SMTP transport abstraction (`SmtpTransport` ABC + smtplib-backed default)

## Status
Accepted

## Context
The mail service must physically deliver emails over SMTP. The spec requires the SMTP backend to be swappable (the public API is a backward-compatibility contract, REQ-015/NFR-003), and the feature must be testable without a real SMTP server (no network in the test suite).

If the service used `smtplib` directly, every send would require a live SMTP server, the tests would need network infrastructure, and the service would carry a hard dependency on `smtplib` call details (connection, authentication, TLS) that belong to the transport, not to the use cases.

## Decision
Abstract the physical SMTP send behind a `SmtpTransport` ABC with a single `send(message: EmailMessage) -> None` operation, and provide `SmtpTransportImpl` as the smtplib-backed default:

- `SmtpTransport` (ABC) — the seam. `send` raises `MailTransportError` on failure.
- `SmtpTransportImpl(host, port, username, password, use_tls, timeout)` — connects per send (TLS when `use_tls` is true), authenticates when `username` is non-empty, sends the message, and closes. Wraps `smtplib`/`socket`/`OSError` failures in `MailTransportError` with a secret-free `reason` (`"connection"`, `"authentication"`, `"smtp"`, `"timeout"`).
- `MailService` accepts an optional `transport` in its constructor; when `None` it builds a `SmtpTransportImpl` from the live settings on each send.
- The service code references only the `SmtpTransport` ABC; tests inject a fake transport that records messages without a network.

## Consequences
- The SMTP backend is swappable: the service, the tests, and the public API never see `smtplib` details.
- Tests verify sending behavior (message content, failure mapping, events) without a network or an SMTP server.
- The per-send transport construction pairs with the independence decision (ADR-046): a failure in one send does not affect subsequent sends.
- The public API surface grows by one ABC (`SmtpTransport`) that is part of the backward-compatibility contract (REQ-015).

## Alternatives Considered
- Direct `smtplib` use in the service — rejected: no test seam; every test would need a live SMTP server; the service would own transport details that belong to the transport.
- A long-lived, pooled SMTP connection with reconnection — rejected: connection state would leak across sends, defeating failure independence (ADR-046); pool lifecycle and thread-safety add complexity the feature does not need (mail is low-frequency).
- A third-party SMTP client library — rejected: `smtplib` is in the standard library and sufficient; a new dependency adds maintenance and licensing surface for no value (the spec explicitly uses the standard library).
- A transport factory returned by the settings feature — rejected: the transport is constructed by the service from the live settings it already reads; a factory would invert the dependency.

## References
- `docs/specs/mail-service.md` (D1, D12, D13; REQ-011, REQ-015, REQ-016; NFR-003, NFR-005)
- `docs/decisions/ADR-046-per-send-transport-independence.md` (per-send construction)
- `docs/decisions/ADR-045-mailerror-hierarchy-secret-free-reasons.md` (failure wrapping)
