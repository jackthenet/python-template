# ADR-014: Template scope-coverage semantics

## Status
Accepted

## Context
Templates are named value profiles scoped to a category (and optionally a
group) (REQ-015). The scope — the set of settings in that category/group —
can change over time: new settings may be registered in the scope after a
template is created, and the spec requires that loads leave settings not in
the template as-is (AC-024, REQ-015).

## Decision
A template's `values` map is a complete snapshot of its scope at creation
and update time: every in-scope setting must be present, and no
out-of-scope key may appear. At load time, each stored `(key, value)` pair
is applied (in key-sorted order) and any in-scope setting absent from the
template is left as-is. This "complete at write, leave-as-is at read" rule
keeps templates stable snapshots while tolerating a growing scope.

## Consequences
- Create/update validation is a set-equality check between the provided
  keys and the current scope keys, plus per-value validation — simple and
  deterministic (AC-021, AC-027).
- Loads never surprise: a template created for scope {A, B} applied later
  to scope {A, B, C} sets A and B and leaves C alone (AC-024).
- Loads validate each value through the normal `set_value` path, so
  `SettingChanged` events and validation failures behave uniformly
  (REQ-024, EDGE-027).

## Alternatives Considered
- Partial templates (subset of scope) — rejected: ambiguous "what is the
  value of an omitted setting?" and makes coverage validation meaningless.
- Freezing the scope at creation (rejecting new in-scope settings) —
  rejected: registration is a registry concern and must not be blocked by
  template state.

## References
- `docs/specs/settings.md` — REQ-015 … REQ-018, AC-019 … AC-028, EDGE-026,
  EDGE-027
