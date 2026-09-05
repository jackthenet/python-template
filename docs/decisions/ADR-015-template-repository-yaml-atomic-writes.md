# ADR-015: TemplateRepository abstraction with YAML as the first implementation

## Status
Accepted

## Context
Templates must persist across registry instances (AC-031) but the storage
format must remain swappable (NFR-002, REQ-021). The first implementation
is YAML files (REQ-022), and storage integrity failures must surface as
`TemplateStorageError` (REQ-023).

## Decision
Template storage goes through a `TemplateRepository` ABC
(`save`, `get`, `delete`, `list`). The first implementation is
`YamlTemplateRepository(directory)`: one file per template named
`<name>.yaml`, written with safe YAML. Writes are atomic: the file is
written to a temporary file in the same directory and renamed over the
target, so a template file is always either absent or valid YAML.
`get` returns `None` for a missing file and raises `TemplateStorageError`
for corrupted or schema-invalid content; `delete` is idempotent; `list`
returns templates in name order.

## Consequences
- The registry is storage-agnostic: an alternative repository (JSON,
  in-memory) satisfies the same interface and observable behavior
  (AC-034, NFR-002).
- Atomic writes guarantee the REQ-022 invariant (file absent or valid)
  even under concurrent writers or crashes mid-write.
- Corruption is detected at read time by re-validating the parsed content
  against the `Template` schema (EDGE-025).

## Alternatives Considered
- One file for all templates — rejected: concurrent updates to different
  templates would collide; per-template files isolate writes.
- `yaml.safe_dump` directly to the target path — rejected: a crash or
  concurrent writer can leave a half-written file, violating REQ-022.

## References
- `docs/specs/settings.md` — REQ-021, REQ-022, REQ-023, AC-030 … AC-034,
  EDGE-024, EDGE-025, NFR-002
