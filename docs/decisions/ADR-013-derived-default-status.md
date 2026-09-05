# ADR-013: Derived default status

## Status
Accepted

## Context
Each setting exposes a default status: `MODIFIED` when the current value
differs from the default, otherwise `DEFAULT` (REQ-013, AC-017, INV-010).
The status could be stored as a field updated on every change, or derived
on demand.

## Decision
The status is always derived: `get_status(key)` and `SettingView.status`
compute `MODIFIED` iff the current value `!=` the default. No status field
is stored anywhere.

## Consequences
- INV-010 (status ⇔ value differs from default) holds by construction;
  there is no state that can drift out of sync.
- `reset`/`reset_all`/template loads need no extra bookkeeping.
- Value comparison uses Python `!=` on the stored values, which is correct
  for the six kinds (all values are scalars or strings).

## Alternatives Considered
- Stored status flag updated in `set_value`/`reset` — rejected: duplicates
  the value state and invites drift (a missed update site breaks INV-010).

## References
- `docs/specs/settings.md` — REQ-013, AC-017, INV-010
