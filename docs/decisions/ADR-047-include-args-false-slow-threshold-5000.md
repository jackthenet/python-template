# ADR-047: `include_args=False` and `slow_threshold_ms=5000` for network-dependent sends

## Status
Accepted

## Context
The mail service is traced with the shared logging feature's `@logged_class` (REQ-014, NFR-004). Two properties of this feature make the defaults wrong:

1. **Secrets in arguments.** The high-level operations carry a `reset_url`/`verification_url` (which contains a token) and the core send carries the recipient. With the decorator default (`include_args=True`), argument values are formatted into the entry log records — tokens would reach the logs, violating the hard security requirement (NFR-002).
2. **Network-dependent latency.** The SMTP send is network-dependent: its latency is dominated by the network, not by the service. The usual slow-call threshold would fire "slow" warnings for ordinary network sends, producing false warnings.

## Decision
Trace `MailService` with `@logged_class(slow_threshold_ms=5000, include_args=False)`:

- `include_args=False` — argument values are **never** formatted into log records (consistent with the secret-handler convention): the `reset_url`/`verification_url` (token) and the recipient never appear in log records. The exit record (elapsed ms) and exception records do not include argument values regardless.
- `slow_threshold_ms=5000` — a slow call (elapsed > 5000 ms) is logged at WARNING; the high threshold avoids false "slow" warnings for network-dependent SMTP sends.
- The feature-owned `register_settings` is traced with `@logged(slow_threshold_ms=5)` (consistent with the other features).

The observable contract (REQ-014, AC-016, NFR-002): for any send (success or failure), no log record contains the SMTP password or a token.

## Consequences
- Secrets are guaranteed not to leak into log records via traced method entry records (NFR-002, REQ-014).
- The guarantee is enforced by the decorator parameter, not by convention, so it is verifiable (AC-016).
- Slow-call warnings are meaningful: only genuinely slow sends (> 5 s) are flagged, not ordinary network latency.
- Routine method tracing stays at DEBUG (off by default at the INFO default level); exceptions are logged with secret-free messages (the `MailError` hierarchy already guarantees this, ADR-045).

## Alternatives Considered
- The decorator default (`include_args=True`) — rejected: tokens and the recipient would be formatted into entry records, violating NFR-002.
- Redacting secret values in the log sink — rejected: more complex, and the sink is shared across all features; `include_args=False` at the source is simpler and local to the secret handler (consistent with the existing secret-handler convention).
- `include_args=True` with per-field token redaction — rejected: redaction is fragile (a new argument field could bypass it); `include_args=False` is a mechanical guarantee.
- The usual slow threshold — rejected: false "slow" warnings for network-dependent sends; the threshold must reflect the dominant cost (the network).

## References
- `docs/specs/mail-service.md` (D10, D11; REQ-014; NFR-002, NFR-004; §9 Observability & Logging)
- `docs/decisions/ADR-034-include-args-false-for-secrets.md` (secret-handler convention)
- `docs/decisions/ADR-033-slow-threshold-observability.md` (slow-call threshold convention)
