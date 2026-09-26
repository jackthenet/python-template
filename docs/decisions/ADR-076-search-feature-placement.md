# ADR-076: Search feature placement (new shared search feature)

## Status
Accepted

## Context
The backend needs a central in-process search abstraction: features register a
named *source* (feature name + field schema + sync query function) and a single
search entry point provides free-text + filtering + sorting + pagination over
registered content, per-feature and/or global fan-out (spec §1). No new
third-party dependency is introduced (spec §2 confirms none — `pydantic` and
`sqlmodel` are existing project dependencies; the search feature itself
persists nothing). The repository pattern is standalone features under
`src/backend/` with service + constructor DI + module singleton + reset
(ADR-018, ADR-025, ADR-069 placement style).

## Decision
Create `src/backend/search/` as a standalone feature (REQ-001..REQ-023).
`SearchService` (use cases: registration lifecycle, query validation, fan-out,
combined pagination) holds a thread-safe in-memory source registry. The service
depends only on the source query-function contract (sources are swappable), the
structural `EventPublisher` protocol, the settings registry (feature-owned
`register_settings` + live-read, ADR-036/ADR-037), the shared logging feature
(`@logged_class`, `include_args=False`, ADR-060), and the shared enforcement
plumbing (`Principal`, `PermissionChecker`, `requires_permission`,
ADR-070/ADR-071). A module singleton (`get_search_service()`) + reset
(`reset_search_service()`) and a public `InMemorySource` for tests/DI follow
the `InMemoryStorageBackend` precedent. The feature is backend-only: an
in-process service with no HTTP/REST layer and no frontend (REQ-023).

## Consequences
- One shared search capability; any in-process caller uses it, and features
  expose content through the registration contract (ADR-077) without search
  importing their internals.
- No new third-party dependencies; the query path stays in-process over the
  source query functions (NFR-001).
- Consistent with the repository feature pattern: constructor DI, in-memory
  variant for tests, singleton + reset (ADR-065 pattern).
- The service persists nothing and indexes nothing — stateless live query
  (ADR-078).

## Alternatives Considered
- Placing search in `backend/shared/` — rejected: `shared/` is deliberately
  small and holds no feature-specific business logic; search is a feature with
  its own spec and requirements, not shared infrastructure (AGENTS.md
  Project Structure & Principles).
- Embedding search in one of the source features (e.g., user-management) —
  rejected: search spans user/file/session content; it would couple unrelated
  change drivers and force the other features to import the host feature for
  authorization-adjacent search.
- A third-party search engine (Elasticsearch/Meilisearch) — rejected:
  out of scope (spec §13); the corpus is small and in-process over existing
  SQLite repositories; a new engine + dependency is not the better engineering
  choice at this scale.

## References
- `docs/specs/search.md` (REQ-001..REQ-023; §1, §2, §3)
- `docs/decisions/ADR-018-user-management-feature-placement.md`
- `docs/decisions/ADR-025-authentication-feature-placement.md`
- `docs/decisions/ADR-069-permissions-feature-placement.md`
- `docs/decisions/ADR-036-feature-owned-registration.md`
- `docs/decisions/ADR-037-live-reads.md`
- `AGENTS.md` — Project Structure & Principles
