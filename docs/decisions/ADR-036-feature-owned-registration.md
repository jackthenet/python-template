# ADR-036: Feature-owned registration via `register_settings(registry)`

## Status
Accepted

## Context
The settings-coverage spec requires every feature to register its settings with the shared settings registry so the registry is the single source of truth for configuration. The design question is how features register their settings without creating import side effects or import cycles.

Each feature's `SettingDefinition`s are owned by the feature (the feature knows its own keys, kinds, and defaults). If a feature registered its settings at import time, importing the feature would mutate the registry singleton — making tests order-dependent and risking import cycles (feature import → registry → event bus → feature import).

## Decision
Each feature module exposes an explicit `register_settings(registry)` function (no import side effects). The entrypoint (`src/main.py`) calls `register_settings(registry)` once per feature at startup, using the shared registry from `get_settings_registry()`.

- The feature owns its `SettingDefinition`s (keys, kinds, defaults, parameters, category, group).
- The entrypoint owns the wiring (calls `register_settings` once per feature).
- Importing a feature module never mutates the registry singleton (no import side effects).
- Tests can call `register_settings` on a fresh `SettingsRegistry` without touching the singleton.

## Consequences
- No import side effects; importing a feature is safe and side-effect-free.
- The entrypoint is the single point of registration wiring (consistent with `setup_logger` being called once in the entrypoint, ADR-035).
- Feature code run outside `main.py` (e.g., a script) has unregistered settings — but the spec's fallback (REQ-005) makes features work without wiring (original hardcoded default + warning).
- `register_settings` called twice on the same registry raises `SettingsRegistrationError` (duplicate keys), so accidental double-registration is detected.

## Alternatives Considered
- Self-registration at import time — rejected: import side effects make tests order-dependent and risk import cycles.
- Centralized registration in a single module (all features' definitions in one place) — rejected: violates feature ownership (the feature should know its own settings) and creates a growing central list.
- Registration via a decorator — rejected: less explicit than a named function and harder to reason about.

## References
- `docs/specs/settings-coverage.md` (REQ-001, REQ-002, AC-001, AC-002, AC-003, D1)
- `docs/decisions/ADR-035-setup-logger-once-in-entrypoint.md` (entrypoint wiring convention)
- `AGENTS.md` — Using the Settings Feature
