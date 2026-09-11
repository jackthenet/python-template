# ADR-037: Live reads of settings (get_value on each use)

## Status
Accepted

## Context
The settings-coverage spec requires features to read their settings from the shared registry. The design question is whether features read settings once at construction (snapshot) or live on each use.

A snapshot read (read once in `__init__`, store the value) means a `set_value` does not affect a running feature — the feature keeps the old value until re-constructed. A live read (call `get_value` on each use) means a `set_value` affects a running feature immediately.

The spec's goal is centralized configuration: changing a setting should take effect without restarting or re-constructing features. Live reads provide that. The logging feature is the exception — it subscribes to `SettingChanged` and reconfigures the sink (because the sink is a single shared resource, not a per-operation value).

## Decision
Features read their settings **live** from the registry (`get_value` on each use), so a `set_value` affects a running feature without re-construction.

- A feature calls `get_value(key)` when it needs the value (e.g., before an operation), not once in `__init__`.
- Live reads are in-memory (no per-read file I/O); the registry loads persisted values once at construction (NFR-001).
- Existing constructor parameters are retained for DI/testing; their default becomes the registry value, and an explicit argument wins (REQ-004).
- The logging feature is the exception: it subscribes to `SettingChanged` and reconfigures the sink at runtime (REQ-015), because the sink is a single shared resource.

## Consequences
- A `set_value` takes effect on a running feature immediately (centralized configuration).
- Live reads are cheap (in-memory), so per-operation reads have no I/O cost.
- A feature that reads a setting on each use is slightly slower than a snapshot read (one `get_value` call), but the cost is negligible (in-memory map lookup).
- Constructor parameters remain for DI/testing (explicit arguments win), so tests can inject values without the registry.
- The logging feature's sink reconfiguration is a separate mechanism (event subscription), not a live read.

## Alternatives Considered
- Snapshot reads (read once in `__init__`) — rejected: a `set_value` does not affect a running feature, defeating centralized configuration.
- Live reads with a cache — rejected: a cache adds invalidation complexity; the registry is already in-memory and cheap.
- Configuration via environment variables — rejected: the settings feature is the single source of truth; env vars are out of scope (REQ-021).

## References
- `docs/specs/settings-coverage.md` (REQ-003, REQ-004, REQ-015, AC-004, AC-005, D2, D9)
- `docs/specs/settings.md` (get_value, set_value)
- `AGENTS.md` — Using the Settings Feature
