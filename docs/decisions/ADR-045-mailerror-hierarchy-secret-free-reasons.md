# ADR-045: `MailError` hierarchy with secret-free reason strings

## Status
Accepted

## Context
The mail service fails at three distinct phases of a send: preparing the email (recipient validation, template rendering, malformed template), resolving the SMTP configuration (an empty host), and delivering the email (connection, authentication, SMTP protocol error, timeout). Callers need to distinguish these phases, and the spec's hard security requirement (NFR-002) forbids the SMTP password, tokens, and the email body from appearing in error messages.

The underlying `smtplib`/`socket` exceptions are not safe to surface: their messages can include hosts, credentials, and protocol details. The error contract must be secret-free by construction.

## Decision
Define a `MailError` hierarchy rooted at a single base, with three phase-specific subclasses, each carrying a short, secret-free `reason` string:

- `MailError` (base) — the common type callers catch.
- `MailConfigurationError(reason)` — the SMTP settings are missing/invalid at send time (e.g., `"smtp_host_empty"`).
- `MailTransportError(reason)` — SMTP delivery failed (`"connection"`, `"authentication"`, `"smtp"`, `"timeout"`).
- `MailTemplateError(reason)` — the email could not be prepared (`"invalid_recipient"`, `"missing_variable:<name>"`, `"malformed_template"`).

The error kind maps to the `EmailFailed.reason` lifecycle-event kind (`"template"`, `"configuration"`, `"transport"`), so the events carry the phase without carrying the exception.

## Consequences
- Callers can distinguish preparation, configuration, and transport failures by exception type and reason.
- Error messages are secret-free by construction: kind + short reason only; the SMTP password, tokens, and the email body never appear (NFR-002, INV-003).
- The `EmailFailed` event carries only the kind, so the event is serializable and non-sensitive without inspecting the exception (REQ-013).
- The hierarchy is part of the public API and the backward-compatibility contract (REQ-015, NFR-003).

## Alternatives Considered
- A single `MailError` without a reason — rejected: callers cannot distinguish the failure phase or the specific condition; the reason is needed for diagnostics and for the event kind mapping.
- Wrapping the original exception (`__cause__` or chained message) — rejected: `smtplib`/`socket` exception messages can include hosts, credentials, and protocol details; surfacing them violates NFR-002.
- Using the exception class as the event payload — rejected: events must be serializable Pydantic models with non-sensitive data; the exception is an internal detail.
- Distinct exception types per transport condition (connection vs. authentication vs. timeout) — rejected: the reason string on one `MailTransportError` is sufficient; four exception types would bloat the public API for the same information.

## References
- `docs/specs/mail-service.md` (D8, D11; REQ-008, REQ-009, REQ-010, REQ-011, REQ-012; NFR-002; EDGE-001 .. EDGE-008)
- `docs/decisions/ADR-028-unified-invalid-credentials-error.md` (secret-free, unified error pattern)
