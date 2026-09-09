# ADR-040: Guarded registry getter to resolve the EventBus bootstrapping cycle

## Status
Accepted

## Context
The settings-coverage spec requires the `EventBus` constructor to read `eventbus.max_queue_size` from the registry. But there is a bootstrapping cycle:

1. `get_event_bus()` lazily creates `EventBus()`.
2. `SettingsRegistry()` (with the default event bus) calls `get_event_bus()`.
3. If `EventBus.__init__` reads `eventbus.max_queue_size` from the registry (via `get_settings_registry()`), and `get_settings_registry()` creates the registry (which calls `get_event_bus()`), this is **infinite recursion**.

The design question is how to resolve this cycle so the `EventBus` can read its setting without recursing.

## Decision
The registry getter supports a **guarded read**: `get_settings_registry(required: bool = True) -> SettingsRegistry | None`.

- `required=True` (default): current behavior — returns the singleton, creating it if missing.
- `required=False`: returns the singleton **if it already exists**, else `None` — **no side effect** (the singleton is never created).

The `EventBus` constructor uses the guarded read:
- If the registry already exists (`get_settings_registry(required=False)` is not `None`), it reads `eventbus.max_queue_size` from the registry.
- Otherwise (the registry does not exist yet), it uses the hardcoded default `1000`.

This resolves the cycle: the first `EventBus` (created during the first `get_settings_registry()`) uses the hardcoded default `1000` (the registry does not exist yet); a later `EventBus` (created after the registry exists) reads `eventbus.max_queue_size` from the registry.

## Consequences
- No infinite recursion; the bootstrapping cycle is resolved.
- The first `EventBus` uses the hardcoded default `1000` (the registry does not exist yet); a later `EventBus` reads the registry value.
- The guarded read is a no-side-effect read (the singleton is never created), so it is safe to call at any time.
- `required=True` (default) preserves the current create-if-missing behavior, so existing callers are unchanged.

## Alternatives Considered
- Create the registry before the event bus (explicit ordering) — rejected: the registry needs an event bus (to publish `SettingChanged`), so the registry cannot be created before the event bus; the cycle is inherent.
- Inject the event bus into the registry explicitly (no default) — rejected: the registry's default event bus (the shared bus) is convenient; requiring explicit injection is more verbose.
- Read the setting lazily (on first publish, not in `__init__`) — rejected: the queue size is needed at construction (to size the queue); lazy reading is too late.
- Use a module-level flag to break the cycle — rejected: a flag is fragile and hard to reason about; the guarded read is cleaner.

## References
- `docs/specs/settings-coverage.md` (REQ-012, REQ-013, AC-016 through AC-018, D5, §3.4)
- `docs/specs/event-bus.md` (get_event_bus, EventBus)
- `docs/specs/settings.md` (get_settings_registry, SettingsRegistry)
