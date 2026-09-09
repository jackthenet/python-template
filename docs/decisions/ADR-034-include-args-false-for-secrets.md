# ADR-034: include_args=False for secret/credential handlers

## Status
Accepted

## Context
The logging-coverage spec (REQ-006, REQ-015) requires every traced class or
function that handles secrets or credentials to use `include_args=False` so
arguments never appear in log records, and no raw tokens, passwords, or hashes
to appear in any log record (hard NFR, NFR-002).

The affected secret/credential handlers are `SqlitePasswordResetRepository`,
`SqliteSessionRepository`, `PyWebAuthnProvider`, `InMemoryAttemptTracker`
(authentication), `new_token`, and `hash_token` (authentication module
functions).

The design question is how to guarantee that secrets never reach log records
when a traced method is called with secret arguments.

## Decision
Secret/credential handlers use `include_args=False` on their traced methods so
that argument values are **never** formatted into log records:
- `@logged_class`-traced classes that handle secrets apply
  `include_args=False` to their public methods (so entry records do not include
  the arguments).
- `@logged`-traced module functions that handle secrets use
  `@logged(include_args=False)`.
- The exit record (elapsed ms) and exception records do not include argument
  values regardless.

The observable contract (REQ-006 / AC-006, REQ-015 / AC-015, INV-002): for any
secret handler, for any arguments, the produced log records never include the
raw argument values.

## Consequences
- Secrets are guaranteed not to leak into log records via traced method entry
  records.
- The guarantee is enforced by the decorator parameter, not by convention, so it
  is verifiable (AC-006, AC-015, INV-002).
- Non-secret handlers keep the decorator default (arguments formatted into the
  record) for diagnostic value.

## Alternatives Considered
- Relying on convention (developers manually avoid logging secrets) — rejected:
  not verifiable and error-prone; the hard NFR (no raw secrets) requires a
  mechanical guarantee.
- Redacting secret values in the log sink — rejected: more complex, and the
  sink is shared across all features; `include_args=False` at the source is
  simpler and local to the secret handler.

## References
- `docs/specs/logging-coverage.md` (REQ-006, REQ-015, AC-006, AC-015, INV-002, NFR-002)
- `docs/specs/authentication.md` (secret/credential handling)
- `AGENTS.md` — Using the Logging Feature (Tracing policy)
