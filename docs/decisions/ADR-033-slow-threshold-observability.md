# ADR-033: Slow threshold is observability, not enforcement

## Status
Accepted

## Context
The logging-coverage spec (REQ-007, REQ-014) requires every traced class and
module function to set a sensible, concrete `slow_threshold_ms`, and a traced
call that exceeds it to log a WARNING and be **not** interrupted.

The design question is the semantics of `slow_threshold_ms`: is it a hard
performance budget that the call must meet (and that the framework enforces by
interrupting or failing the call), or is it an observability mechanism that
surfaces slow calls for diagnosis?

## Decision
`slow_threshold_ms` is an **observability mechanism, not enforcement**:
- Exceeding the threshold logs a WARNING (slow-call detection) and does **not**
  interrupt, fail, or otherwise alter the call.
- The threshold is set per class type to the value the class is *expected* to
  take, so that a WARNING indicates the call is slower than expected (a signal to
  investigate), not that the call violated a hard limit.
- The threshold is a concrete, non-`None` value (REQ-007), chosen per the
  sensible defaults in the spec (§9.1).

## Consequences
- Slow calls are surfaced for diagnosis without changing runtime behavior.
- The threshold does not become a hidden performance contract; performance
  budgets (if any) are stated explicitly in NFRs, not implied by the threshold.
- Tracing remains non-intrusive: it never interrupts the traced call (REQ-013,
  REQ-014, INV-004).

## Alternatives Considered
- Treating the threshold as a hard budget that the framework enforces (interrupt/
  fail the call on exceed) — rejected: this would make tracing intrusive and would
  couple observability to runtime behavior; the spec's goal is discovery, not
  enforcement.
- Leaving `slow_threshold_ms` as `None` (disabled) — rejected: REQ-007 requires a
  concrete value so slow calls are actually surfaced.

## References
- `docs/specs/logging-coverage.md` (REQ-007, REQ-014, EDGE-001, §9.1)
- `docs/specs/logging.md` (slow-threshold behavior of `@logged`)
