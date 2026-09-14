# ADR-057: Settings-registry integration with live reads

## Status
Accepted

## Context
The operational limits (max file size, avatar max size, allowed types,
storage root, avatar base URL) must be configurable at runtime without a
restart (REQ-024, AC-007, AC-012, AC-040, AC-052, AC-053). The
feature-owned `register_settings` + live-read pattern is the established
pattern in this repository (ADR-036, ADR-037). Repository/backend injection
stays constructor args (structural dependencies), while tunable limits move
to the settings registry.

## Decision
The feature-owned `register_settings(registry)` registers the feature's
settings via `register_feature("filemanagement", [...])` (category
`application`, group `filemanagement`); all settings are read **live on
each operation**; unregistered keys fall back to hardcoded defaults
(AC-053). The registration name is `filemanagement` (no hyphen) because the
settings key format forbids hyphens, while the change/feature name remains
`file-management`. Repository/backend injection stays constructor args.

## Consequences
- Live-configurable limits: changing a setting takes effect on the next
  operation without a restart (AC-007, AC-012, AC-040).
- A negligible per-operation settings read cost.
- Unregistered keys fall back to hardcoded defaults, so the feature works
  even before `register_settings` is called (AC-053).
- The registration name differs from the feature name (`filemanagement`
  vs. `file-management`) — a documented quirk of the key format.

## Alternatives Considered
- Hardcoded constants — rejected: not configurable at runtime (REQ-024).
- Constructor args for the limits — rejected: inconsistent with the
  repository pattern; limits are tunable, not structural.
- A config file — rejected: no live updates without a reload mechanism.

## References
- `docs/specs/file-management.md` (REQ-024, AC-007, AC-012, AC-040,
  AC-052, AC-053; D12)
- `docs/decisions/ADR-036-feature-owned-registration.md`
- `docs/decisions/ADR-037-live-reads.md`
