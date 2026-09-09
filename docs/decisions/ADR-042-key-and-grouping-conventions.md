# ADR-042: Key prefix and category/group conventions

## Status
Accepted

## Context
The settings-coverage spec requires every feature to register its settings with the shared registry. The design question is how to name the keys and how to group them for the views hierarchy.

Each feature registers multiple settings (e.g., the logging feature registers `log_level`, `log_file`, etc.). The design question is how to name these keys (to avoid collisions between features) and how to group them (for the views hierarchy).

## Decision
The key prefix is the **full feature name**, the category is the **domain**, and the group is the **feature name**:

- **Key prefix**: `<feature-name>.<setting-name>` (e.g., `logging.log_level`, `authentication.session_ttl`, `usermanagement.roles`, `eventbus.max_queue_size`). The full feature name is the prefix, so keys are globally unique across features (no collisions).
- **Category**: the domain (e.g., `application` for logging and eventbus, `security` for authentication and usermanagement). The category is the top level of the views hierarchy.
- **Group**: the feature name (e.g., `logging`, `authentication`, `usermanagement`, `eventbus`). The group is the second level of the views hierarchy.

The views hierarchy is `category -> group -> [SettingView]` (consistent with the existing `grouped_views()`).

## Consequences
- Keys are globally unique across features (the full feature name prefix prevents collisions).
- The views hierarchy is `category -> group -> [SettingView]`, consistent with the existing `grouped_views()`.
- Each feature's settings are grouped under its feature name (the group), so the views are organized by feature.
- The category is the domain (application/security), so the views are organized by domain at the top level.

## Alternatives Considered
- Key prefix = short name (e.g., `log.log_level`) — rejected: the short name risks collisions between features (e.g., two features both using `log.`); the full feature name is safer.
- Category = feature name — rejected: the category is the domain (application/security), not the feature; using the feature name as the category loses the domain grouping.
- No group (flat hierarchy) — rejected: the group (feature name) organizes the views by feature, which is useful.
- Dotted keys with a different separator (e.g., `logging/log_level`) — rejected: the existing key format is dotted (`^[a-zA-Z_][a-zA-Z0-9_]*(\.[a-zA-Z_][a-zA-Z0-9_]*)*$`); a different separator is inconsistent.

## References
- `docs/specs/settings-coverage.md` (REQ-017, REQ-018, AC-022, AC-023, D8, §3.6)
- `docs/specs/settings.md` (grouped_views, key format)
- `docs/decisions/ADR-010-settings-feature-placement.md` (settings feature placement)
