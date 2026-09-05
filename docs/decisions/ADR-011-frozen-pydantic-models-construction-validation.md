# ADR-011: Frozen Pydantic models with construction-time validation

## Status
Accepted

## Context
The spec defines a family of immutable metadata models
(`SliderSpec`, `SelectOption`, `SelectSpec`, `SettingDefinition`,
`SettingView`, `Template`, `SettingChanged`) and requires that invalid
definitions are rejected with `SettingsValidationError` at construction
(REQ-004, AC-009, AC-010, EDGE-014 … EDGE-019, EDGE-029). Pydantic's native
validation raises `pydantic.ValidationError`, which is a different exception
type and would leak implementation details to callers.

## Decision
All public models are frozen Pydantic `BaseModel` subclasses. Cross-field and
kind-specific rules (key format, default validity per kind, slider/select
spec presence and mismatch, step-grid alignment, option uniqueness) are
enforced in model validators that raise `SettingsValidationError`; any
underlying `pydantic.ValidationError` is mapped to
`SettingsValidationError` so the public error contract is a single
`SettingsError` hierarchy.

## Consequences
- Callers see one stable error type (`SettingsValidationError`) for all
  construction failures — the spec's error contract holds.
- Frozen models guarantee definitions cannot mutate after registration,
  simplifying thread-safety reasoning.
- Validation logic lives in the models, so the registry can trust
  registered definitions without re-validating structure.

## Alternatives Considered
- Dataclasses with manual validation — rejected: Pydantic is already a
  project dependency and gives serialization plus validation for free.
- Letting `pydantic.ValidationError` escape — rejected: violates the spec's
  error contract (AC-009/AC-010 expect `SettingsValidationError`).

## References
- `docs/specs/settings.md` — REQ-001, REQ-002, REQ-004, AC-009, AC-010,
  EDGE-014 … EDGE-019, EDGE-029
