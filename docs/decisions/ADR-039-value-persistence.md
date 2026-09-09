# ADR-039: Value persistence via `ValueRepository` + `YamlValueRepository`

## Status
Accepted

## Context
The settings-coverage spec requires the settings feature to persist **all** current values so configuration survives restarts. The design question is how to persist values and how to keep the storage format swappable.

The existing settings feature persists **templates** via a `TemplateRepository` (one YAML file per template). But it does not persist the **current values** of settings. The spec requires persisting all current values (including values equal to their default) to a single YAML file.

## Decision
The settings feature gains a `ValueRepository` abstraction and a `YamlValueRepository` (single `values.yaml`, atomic write):

```python
class ValueRepository(ABC):
    def load(self) -> dict[str, Any] | None: ...
    def save(self, values: dict[str, Any]) -> None: ...

class YamlValueRepository(ValueRepository):
    def __init__(self, directory: str) -> None: ...
```

- `SettingsRegistry` gains a `value_repository: ValueRepository | None = None` constructor parameter. When `None`, the registry uses a default `YamlValueRepository("settings")`.
- The registry **loads** persisted values at construction (if a value repository is present) and **persists** all current values on every change (`set_value`, `reset`, `reset_all`, template loads).
- `YamlValueRepository` writes a single `values.yaml` file (safe YAML), atomically (write to a temp file in the same directory and rename over the target), thread-safe, directory created if missing.
- Priority: persisted value > definition default (REQ-011). A persisted value is applied to the setting at load time.

## Consequences
- All current values survive restarts (configuration is persistent).
- The storage format is swappable (a future `ValueRepository` implementation can use a different format without changing the registry).
- Atomic writes guarantee the file is always either absent or valid YAML (NFR-005).
- Persisted values take precedence over defaults (REQ-011); a persisted value is applied at load time.
- All values are persisted (including those equal to their default), so the file is a complete snapshot.
- The settings feature is the single source of truth; no env-var handling (REQ-021).

## Alternatives Considered
- Persist one file per setting — rejected: a single `values.yaml` is simpler and a complete snapshot; one file per setting is overkill and harder to manage.
- Persist only modified values (not those equal to the default) — rejected: the spec requires all current values (a complete snapshot); persisting only modified values loses the snapshot.
- Persist to a database — rejected: YAML is human-readable and consistent with the existing template persistence; a database is overkill for configuration values.
- Reuse the `TemplateRepository` for values — rejected: templates and values are different concepts (a named profile vs. the current snapshot); a separate `ValueRepository` is clearer.

## References
- `docs/specs/settings-coverage.md` (REQ-009, REQ-010, REQ-011, REQ-022, AC-013 through AC-015, D4, §3.2)
- `docs/specs/settings.md` (TemplateRepository, YamlTemplateRepository, atomic writes)
- `docs/decisions/ADR-015-template-repository-yaml-atomic-writes.md` (YAML atomic-write pattern)
