# ADR-012: Step-grid slider validation

## Status
Accepted

## Context
SLIDER settings need a deterministic, finite notion of "valid value" for
validation (REQ-003), invariants (INV-005), and property tests. Floating
point makes epsilon-based range checks ambiguous: a value like `4.000000001`
is "close" to `4` but not equal, and accumulated step arithmetic
(`min + k*step`) drifts.

## Decision
A SLIDER value is valid iff it lies in `[min, max]` and equals
`min + k * step` for some integer `k >= 0` (the "step grid"). Membership is
computed by `k = round((value - min) / step)` with an exactness check
(`abs(value - (min + k*step)) <= 1e-9`), so one epsilon is used only to
absorb representation error, not to widen the domain. `SliderSpec`
construction guarantees `max` lies on the grid, so `min` and `max` are
always valid values (INV-005).

## Consequences
- The valid-value set is exactly enumerable: property tests can generate
  grid values directly and prove round-trip validity.
- Off-grid values are rejected with a clear rule (EDGE-007), not by
  approximate range comparison.
- The 1e-9 tolerance is a representation guard, documented in the ADR; it
  does not change the observable contract for realistic slider parameters.

## Alternatives Considered
- Pure range check (`min <= value <= max`) — rejected: would accept off-grid
  values, violating REQ-003 and INV-005.
- No tolerance (exact float equality) — rejected: `min + k*step` arithmetic
  drift would make legitimately stepped values invalid.

## References
- `docs/specs/settings.md` — REQ-003, INV-005, EDGE-007, EDGE-029
