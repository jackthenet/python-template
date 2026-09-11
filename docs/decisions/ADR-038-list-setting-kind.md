# ADR-038: New `LIST` setting kind with `ListSpec`

## Status
Accepted

## Context
The settings-coverage spec requires the `usermanagement.roles` setting to be a list of role strings (e.g., `["admin", "member"]`). The existing settings feature has six kinds (TEXT, NUMBER, BOOLEAN, EMAIL, SLIDER, SELECT), none of which represent a list of strings.

The design question is how to represent a list-of-strings setting in the settings feature. A new `LIST` kind with a `ListSpec` (per-item pattern, min/max item count, duplicate control) is the natural extension, consistent with the existing `SliderSpec` / `SelectSpec` pattern.

## Decision
The settings feature gains a new `LIST` setting kind (the 7th kind) with a `ListSpec`:

```python
class ListSpec(BaseModel):
    item_pattern: str | None = None   # regex each item must fullmatch
    min_items: int | None = None      # minimum number of items (>= 0)
    max_items: int | None = None      # maximum number of items (>= 0)
    allow_duplicates: bool = True     # whether duplicate items are permitted
```

- `SettingKind` gains `LIST`.
- `SettingDefinition` gains an optional `list_spec: ListSpec | None` field, validated exactly like the existing `slider_spec` / `select_spec`:
  - `LIST` **requires** a valid `ListSpec` (present or the default `ListSpec()`).
  - Non-LIST kinds **reject** a `ListSpec` (`SettingsValidationError`).
  - `ListSpec` is invalid when `min_items > max_items`, `item_pattern` is not a valid regex, or `min_items`/`max_items` is negative.
- A `LIST` value is validated as: a list of strings; each item fullmatches `item_pattern` (when set); the item count is within `[min_items, max_items]` (when set); duplicates are rejected when `allow_duplicates` is `False`.

## Consequences
- `usermanagement.roles` (and any future list-of-strings setting) is representable in the settings feature.
- The `LIST` kind is validated at definition time (ListSpec validity) and value time (per-item pattern, count, duplicates), consistent with the other kinds.
- The existing six kinds are unchanged; the `LIST` kind is additive (backward-compatible, NFR-003).
- `ListSpec` validation reuses the existing construction-time validation pattern (frozen Pydantic models, `SettingsValidationError`).

## Alternatives Considered
- Represent roles as a TEXT setting with a delimiter (e.g., `"admin,member"`) — rejected: loses per-item validation and type safety; a list is the correct representation.
- Add a generic list kind without per-item validation — rejected: no per-item pattern/count/duplicate control is less useful and less safe.
- Use a SELECT kind with multiple selection — rejected: SELECT is a single value from a fixed option set; roles are an open list of strings.

## References
- `docs/specs/settings-coverage.md` (REQ-006, REQ-007, REQ-008, AC-007 through AC-012, D3, §3.1)
- `docs/specs/settings.md` (SliderSpec, SelectSpec, kind-specific validation)
- `docs/decisions/ADR-012-step-grid-slider-validation.md` (kind-specific spec pattern)
