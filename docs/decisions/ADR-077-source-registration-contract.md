# ADR-077: Cross-feature source registration contract (name + field schema + sync query function)

## Status
Accepted

## Context
Search must expose content owned by other features (user-management,
file-management, session-management) without the search feature importing their
internals or duplicating their storage. Each feature owns its own repository
and query semantics; search needs a uniform, swappable handle on that content.
The field-type set is closed (string/number/boolean/datetime) so the filter
DSL, per-type operator restrictions, and fan-out validation stay uniform
(REQ-002, REQ-006, REQ-007).

## Decision
A `SearchSource` = name (the feature name, matching `SOURCE_NAME_PATTERN`) +
field schema (`SourceField`: name, type, searchable/filterable/sortable/display
flags) + sync query function (`SourceQueryContext -> SourcePage`). Features
register at startup via additive `search_source.py` modules —
`build_user_source(UserRepository)`, `build_file_source(FileRepository)`,
`build_session_source(SessionRepository)` — each querying the feature's
existing repository (no new persistence, no new behavior in the feature's
operations, D19). The search service references only the query-function
contract (sources are swappable); the source's default ordering is the order
`query` returns items in when `sort` is None (D8). Registration is
static-at-startup; the registry is in-memory (D1).

## Consequences
- Search stays decoupled from feature internals (dependency inversion): a
  change in any feature's repository does not break search as long as the
  registration contract holds.
- Each feature controls what it exposes (the field flags) and how it queries
  (its own repository over its own data).
- The closed field-type set keeps the filter DSL, per-type operator
  restrictions, and strict fan-out validation (REQ-006, REQ-007, D7) uniform
  across sources.
- Additive `search_source.py` modules grow the features' public APIs without
  touching existing code (impact analysis §12.2–§12.4).

## Alternatives Considered
- Search importing each feature's repository directly — rejected: search would
  depend on three features' storage details; a change in any repository would
  break search; the registration contract keeps search depending on one uniform
  interface.
- Generic reflection over the features' Pydantic/SQLModel models — rejected:
  the closed field schema is explicit and validated at registration; reflection
  would couple search to model internals and make the filter DSL open-ended.
- Event-driven index maintenance (sources push changes to search) — rejected:
  out of scope (spec §13); stateless live query (ADR-078) is simpler and always
  current.

## References
- `docs/specs/search.md` (D1, D8, D19; REQ-001, REQ-002, REQ-020..REQ-022;
  §3, §12.2–§12.4)
- `docs/decisions/ADR-076-search-feature-placement.md`
