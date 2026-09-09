# ADR-041: No-arg `setup_logger()` reading `logging.*` from the registry

## Status
Accepted

## Context
The settings-coverage spec requires the logging feature's configuration (`log_level`, `log_file`, `log_max_bytes`, `log_backup_count`, `profiling_include_arguments`) to be managed by the settings feature, not by the logging feature's own stub `Settings` model.

Currently `setup_logger(settings: Settings)` takes a `Settings` instance (the logging feature's own Pydantic model), and `src/main.py` builds the `Settings` directly. The design question is how `setup_logger` reads the logging configuration from the shared registry and how the logging feature's stub `Settings` model is removed.

## Decision
`setup_logger()` takes **no arguments** and reads `logging.*` from the shared registry:

- `setup_logger()` calls `get_settings_registry()` and reads `logging.log_level`, `logging.log_file`, `logging.log_max_bytes`, `logging.log_backup_count`, and `logging.profiling_include_arguments`.
- If a `logging.*` key is unregistered, `setup_logger` falls back to the logging defaults with a warning (REQ-005).
- `setup_logger` is idempotent (a second call is a no-op), consistent with the current behavior.
- The logging feature's stub `Settings` model (`src/backend/logging/settings.py`) is **removed**; the logging feature reads `log_*` values from the registry.
- The logging feature subscribes to `SettingChanged` and reconfigures the sink at runtime when any `logging.*` setting changes, re-applying all current `logging.*` values (REQ-015).

## Consequences
- The logging feature's configuration is managed by the settings feature (single source of truth).
- `setup_logger()` is simpler (no arguments); the caller does not build a `Settings` instance.
- The logging stub `Settings` model is removed; the logging feature reads from the registry.
- The sink is reconfigured at runtime when a `logging.*` setting changes (event subscription), so a `set_value` takes effect without re-calling `setup_logger`.
- If the logging settings are unregistered, `setup_logger` falls back to the logging defaults with a warning (the feature works without wiring).

## Alternatives Considered
- Keep `setup_logger(settings: Settings)` but build the `Settings` from the registry — rejected: the stub `Settings` model is redundant; reading directly from the registry is simpler and removes the stub.
- Make `setup_logger` read the registry but keep the stub `Settings` model — rejected: the stub model is the thing being removed; keeping it defeats the purpose.
- Reconfigure the sink on each `setup_logger` call (not on `SettingChanged`) — rejected: the sink is a single shared resource; reconfiguring on `SettingChanged` (event subscription) is more direct and takes effect without re-calling `setup_logger`.

## References
- `docs/specs/settings-coverage.md` (REQ-014, REQ-015, REQ-016, AC-019 through AC-021, D6, D7)
- `docs/specs/logging.md` (setup_logger, the stub Settings model)
- `docs/decisions/ADR-035-setup-logger-once-in-entrypoint.md` (setup_logger called once in the entrypoint)
