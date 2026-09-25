# Spec: Search (Backend, Cross-Cutting)

## 1. Overview & Objectives
- **Feature Name:** Search (Backend, Cross-Cutting)
- **Target Component:** `src/backend/search/` (new feature) plus additive search-source modules in `src/backend/usermanagement/`, `src/backend/filemanagement/`, `src/backend/sessionmanagement/`, and an additive `SessionRepository.list_all` method in `src/backend/authentication/` (backward-compatible per authentication NFR-003)
- **Goal:** Provide a central backend search abstraction: features register a named *source* (feature name + field schema + sync query function); a single search entry point provides free-text + filtering + sorting + pagination over registered content (per-feature and/or global fan-out). This CROSS-CUTTING change ALSO wires three existing features' content as sources: user-management (users), file-management (files), and session-management (sessions).
- **Scope:** In-process Python service (no HTTP layer); stateless live query (no index, no persistence); in-memory registry of sources; static source declaration at startup; optional free-text string + structured AND/OR filters over a closed field-type set (string/number/boolean/datetime); offset/limit pagination with a total match count; deterministic sorting with stable tie-breaking; per-source timeout; resilient global fan-out with per-source failure markers; a domain `SearchError` hierarchy (not ValueError); feature-owned settings (live read); typed lifecycle/failure events; `@logged_class` tracing; permission enforcement via the shared `Principal`/`PermissionChecker` plumbing; a public in-memory source for tests/DI; module singleton + reset.
- **Out of Scope:** External full-text search engines, faceting, synonyms, typo tolerance/fuzzy matching, highlighting, suggestions/autocompletion, stemming/multi-language text analysis, search history, HTTP/REST layer, frontend UI.

## 2. Architecture & Design Decisions
- **Design Pattern:** Registry + live query fan-out. `SearchService` (use cases: registration lifecycle, query validation, fan-out, combined pagination) holds a thread-safe in-memory source registry. Each search fans out to the source query functions (sync; executed in a worker thread with a per-source timeout) and combines the per-source pages. The service never persists and never indexes — every query is live.
- **Dependencies:** `pydantic` (existing project dependency — request/representation models), `sqlmodel` (existing — only via the feature sources' repositories; the search feature itself persists nothing); uses `backend.settings` (feature-owned `register_settings` + live-read pattern), `backend.logging` (`@logged`, `@logged_class`), the shared enforcement plumbing `backend.shared` (`Principal`, `PermissionChecker`, `requires_permission`), and the structural `EventPublisher` protocol (the real event bus is injected at wiring time, consistent with the other features). **No new third-party dependencies.**
- **Constraints:** In-process only (no HTTP/REST layer). Query text, result content, and source data never appear in log records, events, or error messages (only structural metadata: source names, field names, counts, error kinds). The service references only the source query-function contract (sources are swappable). The field-type set is closed (string/number/boolean/datetime) — a list field is not representable and is not exposed.
- **Design Decisions (WHAT; WHY goes to ADRs in Phase 2):**
  - D1: Source model — a `SearchSource` = name + field schema (`SourceField`: name, type, searchable/filterable/sortable/display flags) + sync query function (`SourceQueryContext -> SourcePage`). Static declaration at startup; in-memory registry; no index, no persistence (stateless live query).
  - D2: Registration lifecycle — re-registration with the same name = replace (atomic; an in-flight query sees either the old or the new source, never partial state); identical re-registration (same name + equal fields + same query function) = idempotent no-op (no event); `unregister_source(unknown)` = no-op (no event); `reset()` clears all registrations (no events).
  - D3: Query model — `SearchQuery` = optional free text + optional `FilterGroup` (AND/OR, nestable) + optional `feature` (omitted = fan out to all registered sources, combined pagination) + offset/limit + optional `Sort`. Empty/None free text = no free-text constraint; no free text + no filters = match all (list all).
  - D4: Filter DSL — operators equals/contains/starts_with/gt/gte/lt/lte/in_list/is_null; restricted to fields the source declared filterable; per-type operator restrictions (string: equals/contains/starts_with/in_list/is_null; number: equals/gt/gte/lt/lte/in_list/is_null; boolean: equals/in_list/is_null; datetime: equals/gt/gte/lt/lte/in_list/is_null).
  - D5: Pagination — offset/limit (file-management precedent); the default page size is the live `search.default_page_size`; `limit > search.max_page_size` is clamped to the cap (no error); the response carries the total match count; an offset beyond the last match = empty list, no error.
  - D6: Combined global fan-out — each source in the fan-out receives the same `SourceQueryContext` (same offset/limit); the combined page is the concatenation of the per-source pages in registration order; `total` is the sum of the per-source totals.
  - D7: Strict fan-out validation — a global query is validated against every source in the fan-out: a filter on a field the source did not declare filterable (or that is absent from the source's schema), a sort on a non-sortable field, an operator invalid for the field's type, or a value of the wrong type → `MalformedQueryError` (identifying the source + field). A source with no searchable fields contributes 0 matches to a non-empty free-text query (no error).
  - D8: Sorting — deterministic ordering only (no relevance score); a user sort on a declared-sortable field overrides the source's default ordering; ties are broken stably by the source's default ordering (the order the source's query function returns items when `sort` is None).
  - D9: Result shape — each result item = `feature` (source name) + `item_id` + the declared display field values (`fields` dict); page metadata (total, offset, limit); the caller renders directly (no round-trip to the source feature).
  - D10: Errors — a domain `SearchError` hierarchy (NOT ValueError): `UnknownSourceError` (unknown feature in a query), `MalformedQueryError` (invalid operator for a field's type, filter on a non-filterable field, sort on a non-sortable field, invalid value type, `limit < 1`, `offset < 0`), `SourceQueryFailedError` (a source raising during a single-source query, or a timeout).
  - D11: Resilient global fan-out — a source raising during a global search → partial results + a per-source failure marker (`SourceFailure`: feature, reason `query_failed`/`timeout`, error kind); no exception is raised; a `SourceQueryFailed` event is published.
  - D12: Per-source timeout — each source query runs in a worker thread (bounded pool); exceeding the live `search.source_timeout` (ms) → a source failure with reason `timeout` (failure marker for global; `SourceQueryFailedError` for single-source); the timed-out thread is abandoned (bounded by the pool; its result is discarded).
  - D13: Normalization — text matching is case-insensitive (case-folded) + Unicode NFC + trimmed; number/boolean/datetime are exact. The service normalizes the free text before fan-out; sources apply the same normalization to their own string values for free-text and string filter matching.
  - D14: Settings — the feature-owned `register_settings(registry)` registers `search.default_page_size` (default 100), `search.max_page_size` (default 1000), `search.source_timeout` (default 5000 ms); all are read live on each operation; unregistered keys fall back to the hardcoded defaults.
  - D15: Events — `SourceRegistered(source)`, `SourceUnregistered(source)`, `SourceQueryFailed(source, reason)`; NO per-query event; non-sensitive data only (no query text, no result content).
  - D16: Security — `search` takes a trailing `principal: Principal = Principal()` parameter and is enforced via the shared `requires_permission("search.search")` decorator (the injected `PermissionChecker`; standalone mode when `None`), before returning results; the feature declares the `search.search` action via the feature-owned `register_actions(catalog)` (additive to the user-roles-permissions catalog; no change to the permissions feature's code or behavior).
  - D17: Testability — a public `InMemorySource` (in-memory source for tests/DI, following the `InMemoryStorageBackend` precedent); module singleton `get_search_service()` + `reset_search_service()`; `SearchService.reset()` for registration isolation.
  - D18: Thread safety — the registry is guarded by an internal lock (register/unregister/reset take the lock; `search` snapshots the registrations under the lock and queries outside it); no partial state on concurrent register/query.
  - D19: Feature sources — additive `search_source.py` modules: `build_user_source(UserRepository)`, `build_file_source(FileRepository)`, `build_session_source(SessionRepository)`. Each queries the feature's existing repository (no new persistence, no new behavior in the feature's operations). The session source requires an additive `SessionRepository.list_all()` ABC method (authentication; backward-compatible per authentication NFR-003; precedent: session-management REQ-017).

## 3. Data Structures & API Schemas

```python
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Callable, Literal

from pydantic import BaseModel

# --- Field types (closed set; D1) ---

class FieldType(str, Enum):
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    DATETIME = "datetime"

# --- Source model (D1) ---

SOURCE_NAME_PATTERN: str = r"^[a-z0-9][a-z0-9._]{0,63}$"   # feature name (no hyphen, repo convention)
FIELD_NAME_PATTERN: str = r"^[a-z0-9][a-z0-9._]{0,63}$"

class SourceField(BaseModel):
    name: str                    # matches FIELD_NAME_PATTERN; unique within a source
    type: FieldType              # the closed set
    searchable: bool = False     # free text matches this field
    filterable: bool = False     # filters may reference this field
    sortable: bool = False       # sort may reference this field
    display: bool = False        # the value is included in result items

class SourceItem(BaseModel):
    item_id: str                 # opaque; unique within the source
    fields: dict[str, Any]       # values of the source's declared display fields

class SourcePage(BaseModel):
    items: list[SourceItem]      # at most `limit` items starting at `offset`
    total: int                   # total match count (ignoring pagination)

class SourceQueryContext(BaseModel):
    free_text: str | None = None   # normalized (case-folded, NFC, trimmed); None = no constraint
    filters: FilterGroup | None = None
    offset: int = 0
    limit: int = 100               # effective limit (default applied, cap clamped)
    sort: Sort | None = None       # None = the source's default ordering

SourceQueryFn = Callable[[SourceQueryContext], SourcePage]

class SearchSource(BaseModel):
    name: str                    # matches SOURCE_NAME_PATTERN (the feature name)
    fields: list[SourceField]    # at least 1; names unique within the source
    query: SourceQueryFn         # sync; called per search (in a worker thread, D12)
    # The source's default ordering is the order `query` returns items in when
    # `sort` is None (documented per source; D8).
```

```python
# --- Query model (D3, D4) ---

class FilterOperator(str, Enum):
    EQUALS = "equals"
    CONTAINS = "contains"
    STARTS_WITH = "starts_with"
    GT = "gt"
    GTE = "gte"
    LT = "lt"
    LTE = "lte"
    IN_LIST = "in_list"
    IS_NULL = "is_null"

# Per-type operator restrictions (D4):
#   string:   equals, contains, starts_with, in_list, is_null
#   number:   equals, gt, gte, lt, lte, in_list, is_null
#   boolean:  equals, in_list, is_null
#   datetime: equals, gt, gte, lt, lte, in_list, is_null

class FilterCondition(BaseModel):
    field: str                   # must be declared filterable by the source
    operator: FilterOperator     # must be valid for the field's declared type
    value: Any | None = None     # required for every operator except is_null;
                                 # must match the field's declared type
                                 # (number: int/float; boolean: bool;
                                 #  datetime: datetime; string: str;
                                 #  in_list: a list of such values)

class FilterGroup(BaseModel):
    operator: Literal["and", "or"]
    conditions: list[FilterCondition | FilterGroup]   # at least 1; groups nestable

class Sort(BaseModel):
    field: str                   # must be declared sortable by the source
    direction: Literal["asc", "desc"] = "asc"

class SearchQuery(BaseModel):
    free_text: str | None = None   # empty/None = no free-text constraint
    filters: FilterGroup | None = None
    feature: str | None = None     # omitted = fan out to all registered sources
    offset: int = 0
    limit: int | None = None       # None = the live search.default_page_size
    sort: Sort | None = None
```

```python
# --- Result shapes (D9, D11) ---

class SearchResultItem(BaseModel):
    feature: str                 # the source name
    item_id: str
    fields: dict[str, Any]       # values of the declared display fields

class SourceFailure(BaseModel):
    feature: str
    reason: str                  # "query_failed" | "timeout"
    error: str                   # error kind (no sensitive data)

class SearchResult(BaseModel):
    items: list[SearchResultItem]
    total: int                   # sum of the per-source totals (global) / the source's total (single)
    offset: int
    limit: int                   # effective limit
    failures: list[SourceFailure]  # per-source failure markers (empty for single-source queries)
```

```python
# --- Errors (D10) ---

class SearchError(Exception): ...

class UnknownSourceError(SearchError):
    source: str                  # the unknown feature name

class MalformedQueryError(SearchError):
    reason: str                  # "invalid_limit" | "invalid_offset" | "invalid_operator"
                                 # | "non_filterable_field" | "non_sortable_field"
                                 # | "invalid_value_type"
    field: str | None = None     # the field involved (where applicable)
    source: str | None = None    # the source the query was validated against (fan-out)

class SourceQueryFailedError(SearchError):
    source: str
    reason: str                  # "query_failed" | "timeout"
    error: str                   # error kind (no sensitive data)
```

```python
# --- Events (D15; non-sensitive data only) ---

class SourceRegistered(BaseModel):
    source: str

class SourceUnregistered(BaseModel):
    source: str

class SourceQueryFailed(BaseModel):
    source: str
    reason: str                  # "query_failed" | "timeout"

# --- Publisher protocol (structural; the real EventBus satisfies it) ---

class EventPublisher(Protocol):
    def publish(self, event: object) -> None: ...
```

```python
# --- Service (D2, D3, D5, D6, D12, D16, D17, D18) ---

class SearchService:
    def __init__(
        self,
        event_bus: EventPublisher | None = None,            # None = no events, no error
        settings_registry: SettingsRegistry | None = None,  # None = the shared get_settings_registry()
        permission_service: PermissionChecker | None = None,  # None = standalone mode (no enforcement)
    ) -> None: ...
    def register_source(self, source: SearchSource) -> None: ...
    # Re-registration with the same name = replace (SourceRegistered published);
    # identical re-registration (same name + equal fields + same query function) = no-op (no event);
    # an invalid declaration (name/field name not matching the patterns, duplicate field
    # names, unknown field type) raises ValueError (argument-level, repo precedent)
    def unregister_source(self, name: str) -> None: ...   # unknown name = no-op (no event)
    def list_sources(self) -> list[str]: ...               # registration order
    @requires_permission("search.search")
    def search(self, query: SearchQuery, principal: Principal = Principal()) -> SearchResult: ...
    # Trailing principal parameter (ADR-071 pattern); a denial raises and propagates
    # before any source is queried; standalone mode (no checker) skips the check
    def reset(self) -> None: ...                           # clears all registrations (no events)

class InMemorySource:
    """Public in-memory source for tests/DI (InMemoryStorageBackend precedent)."""
    def __init__(self, name: str, fields: list[SourceField], items: list[SourceItem]) -> None: ...
    # The default ordering = the items' insertion order; the query function applies
    # free text, filters, sort, and pagination in memory with the spec's normalization
    # and per-type semantics (D13, D4)
    def to_source(self) -> SearchSource: ...

def get_search_service(
    event_bus: EventPublisher | None = None,
    settings_registry: SettingsRegistry | None = None,
    permission_service: PermissionChecker | None = None,
) -> SearchService: ...   # module singleton (first call creates it; later calls return it)

def reset_search_service() -> None: ...   # clears the singleton (tests)
```

### 3.1 Feature settings (registered via `register_settings`)

The feature-owned `register_settings(registry)` (in `feature_settings.py`) registers the feature's settings with the settings registry (no import side effects, consistent with the other features; category `application`, group `search`). Each setting is read live on each operation (REQ-013).

| Key | Kind | Default |
|-----|------|---------|
| `search.default_page_size` | NUMBER | `100` |
| `search.max_page_size` | NUMBER | `1000` |
| `search.source_timeout` | NUMBER | `5000` (ms) |

### 3.2 Feature actions (registered via `register_actions`)

The feature-owned `register_actions(catalog)` (in `feature_actions.py`) declares the search feature's catalog actions at startup (mirroring `register_settings`; the `PermissionCatalog` annotation is type-checking only — the feature never imports `backend.permissions` at runtime, ADR-070):

| Action key | Description |
|------------|-------------|
| `search.search` | Search registered sources |

**Package layout:**

```text
src/backend/search/
├── __init__.py    # re-exports the public API
├── models.py      # FieldType, SourceField, SourceItem, SourcePage, SourceQueryContext,
│                 # SearchSource, FilterOperator, FilterCondition, FilterGroup, Sort,
│                 # SearchQuery, SearchResultItem, SourceFailure, SearchResult
├── errors.py      # SearchError hierarchy
├── events.py      # SourceRegistered, SourceUnregistered, SourceQueryFailed, EventPublisher
├── feature_settings.py  # register_settings
├── feature_actions.py   # register_actions (search.search)
└── service.py     # SearchService, InMemorySource, get_search_service, reset_search_service
```

**Public API** (the NFR-003 contract): `SearchService`, `InMemorySource`, `SearchSource`, `SourceField`, `SourceItem`, `SourcePage`, `SourceQueryContext`, `FieldType`, `FilterOperator`, `FilterCondition`, `FilterGroup`, `Sort`, `SearchQuery`, `SearchResultItem`, `SourceFailure`, `SearchResult`, `SearchError`, `UnknownSourceError`, `MalformedQueryError`, `SourceQueryFailedError`, `SourceRegistered`, `SourceUnregistered`, `SourceQueryFailed`, `EventPublisher`, `register_settings`, `register_actions`, `get_search_service`, `reset_search_service`.

**Feature-source modules (additive; D19):**

```text
src/backend/usermanagement/search_source.py     # build_user_source(UserRepository) -> SearchSource
src/backend/filemanagement/search_source.py     # build_file_source(FileRepository) -> SearchSource
src/backend/sessionmanagement/search_source.py  # build_session_source(SessionRepository) -> SearchSource
```

Each `build_*_source` function is re-exported from its feature's `__init__.py` (additive to the feature's public API).

**Startup wiring (application entrypoint, once):**

```python
register_settings(get_settings_registry())   # search feature
register_actions(permission_catalog)         # search feature (additive catalog action)
search_service = get_search_service(event_bus=event_bus, permission_service=permission_service)
search_service.register_source(build_user_source(user_repository))
search_service.register_source(build_file_source(file_repository))
search_service.register_source(build_session_source(session_repository))
```

## 4. Requirements

Each normative requirement MUST have a stable ID. These IDs propagate through the lifecycle:
`REQ-001 → AC-001 → test → task → implementation`.

| ID | Requirement |
|----|-------------|
| REQ-001 | Source registration: a feature registers a named source (name + field schema + sync query function) with the search service; the registry is in-memory (no index, no persistence); `list_sources` returns the registered names in registration order. |
| REQ-002 | Field schema: a source declares fields with a name (matching `FIELD_NAME_PATTERN`, unique within the source), a type from the closed set {string, number, boolean, datetime}, and searchable/filterable/sortable/display flags. |
| REQ-003 | Registration lifecycle: re-registration with the same name replaces the source (atomic); identical re-registration (same name + equal fields + same query function) is an idempotent no-op (no event); `unregister_source` removes the source (unknown name → no-op, no event); `reset()` clears all registrations (no events). |
| REQ-004 | Query entry point: `search(query)` accepts an optional free-text string, optional structured filters, an optional `feature` (omitted = fan out to all registered sources, combined pagination), offset/limit, and an optional sort. |
| REQ-005 | Free-text semantics: empty/None free text = no free-text constraint; no free text + no filters = match all (list all); a non-empty free text matches items where any declared-searchable field contains the normalized text (case-insensitive substring). |
| REQ-006 | Filter DSL: operators equals/contains/starts_with/gt/gte/lt/lte/in_list/is_null; AND/OR groups (nestable); filters are restricted to fields the source declared filterable; per-type operator restrictions apply. |
| REQ-007 | Pagination: offset/limit; the default page size is the live `search.default_page_size`; `limit > search.max_page_size` is clamped to the cap; the response carries the total match count; an offset beyond the last match = empty list, no error. |
| REQ-008 | Sorting: deterministic ordering only (no relevance score); a sort on a declared-sortable field overrides the source's default ordering; ties are broken stably by the source's default ordering. |
| REQ-009 | Result shape: each result item = `feature` (source name) + `item_id` + the declared display field values; page metadata (total, offset, limit); the caller renders directly (no round-trip to the source feature). |
| REQ-010 | Errors: a domain `SearchError` hierarchy (NOT ValueError): unknown feature in a query → `UnknownSourceError`; malformed query (invalid operator for a field's type, filter on a non-filterable field, sort on a non-sortable field, invalid value type, `limit < 1`, `offset < 0`) → `MalformedQueryError`; a source raising during a single-source query → `SourceQueryFailedError`. |
| REQ-011 | Resilient global fan-out: a source raising during a global search → partial results with a per-source failure marker (feature, reason, error kind); no exception is raised; the other sources' results are returned. |
| REQ-012 | Normalization: text matching is case-insensitive (case-folded) + Unicode NFC + trimmed; number/boolean/datetime are exact; the service normalizes the free text before fan-out; sources apply the same normalization to their string values. |
| REQ-013 | Settings: the feature-owned `register_settings(registry)` registers `search.default_page_size` (default 100), `search.max_page_size` (default 1000), `search.source_timeout` (default 5000 ms); all are read live on each operation; unregistered keys fall back to the hardcoded defaults. |
| REQ-014 | Events: `SourceRegistered`/`SourceUnregistered`/`SourceQueryFailed` are published to the injected publisher; NO per-query event; non-sensitive data only (no query text, no result content); a `None` publisher means no events and no error. |
| REQ-015 | Observability: the service is traced with `@logged_class` (`include_args=False`, `slow_threshold_ms=100`); the module functions (`register_settings`, `register_actions`, `get_search_service`, `reset_search_service`) are traced with `@logged`; query text and result content never appear in log records. |
| REQ-016 | Security: `search` enforces `require_permission("search.search")` at entry via the shared `Principal`/`PermissionChecker` plumbing (trailing `principal` parameter; standalone mode when no checker is injected) before returning results; the feature declares the `search.search` action via the feature-owned `register_actions(catalog)`. |
| REQ-017 | Testability: a public `InMemorySource` for tests/DI; module singleton `get_search_service()` + `reset_search_service()`; `SearchService.reset()` for registration isolation. |
| REQ-018 | Thread safety: the registry and the query path are safe for concurrent use; no partial state on concurrent register/query (a query sees either the old or the new registration). |
| REQ-019 | Per-source timeout: each source query runs in a worker thread; exceeding the live `search.source_timeout` (ms) → a source failure with reason `timeout` (failure marker for global; `SourceQueryFailedError` for single-source); the timed-out thread is abandoned (bounded by the pool). |
| REQ-020 | user-management source: an additive `search_source.py` module exposes users as a search source named `usermanagement` (fields: `username`, `email`, `display_name` — string, searchable/filterable/sortable/display; `is_active` — boolean, filterable/sortable/display; `created_at`, `updated_at` — datetime, filterable/sortable/display; the query function over the existing `UserRepository.list_all` (called with `include_inactive=True` so the `is_active` field is meaningful); `item_id` = the user id; default ordering `username` ascending). |
| REQ-021 | file-management source: an additive `search_source.py` module exposes files as a search source named `filemanagement` (fields: `key`, `namespace`, `original_filename` — string, searchable/filterable/sortable/display; `detected_mime_type` — string, filterable/sortable/display; `size` — number, filterable/sortable/display; `created_at`, `updated_at` — datetime, filterable/sortable/display; the query function over the existing `FileRepository.list_by_namespace`; `item_id` = the file id; default ordering `created_at` ascending). |
| REQ-022 | session-management source: an additive `search_source.py` module exposes sessions as a search source named `sessionmanagement` (fields: `session_id` — string, searchable/filterable/sortable/display; `user_id` — string, filterable/sortable/display; `created_at`, `expires_at` — datetime, filterable/sortable/display; `revoked` — boolean, filterable/sortable/display; `login_method` — string, filterable/sortable/display; the query function over the existing `SessionRepository.list_all`; `item_id` = the session id; default ordering `created_at` descending); requires the additive `SessionRepository.list_all()` ABC method (authentication; backward-compatible per authentication NFR-003). |
| REQ-023 | Backend-only: an in-process service (no HTTP/REST layer, no frontend); any in-process caller may use it. |

## 5. Acceptance Criteria

Each acceptance criterion MUST have a stable ID and MUST reference at least one requirement. Use Given/When/Then format.

| ID | References | Criterion |
|----|------------|-----------|
| AC-001 | REQ-001, REQ-002 | **Given** a `SearchSource` named `demo` with fields and a query function, **When** `register_source(source)` is called, **Then** `list_sources()` includes `demo`, **And** the source is queryable via `search`. |
| AC-002 | REQ-003 | **Given** a registered source named `demo`, **When** `register_source` is called with a different source of the same name, **Then** the new source replaces the old one, **And** a subsequent `search` uses the new source's query function, **And** `SourceRegistered` is published. |
| AC-003 | REQ-003 | **Given** a registered source, **When** `register_source` is called with an identical source (same name + equal fields + same query function), **Then** it is a no-op (no error), **And** no event is published. |
| AC-004 | REQ-003 | **Given** a registered source named `demo`, **When** `unregister_source("demo")` is called, **Then** `list_sources()` no longer includes `demo`, **And** `SourceUnregistered` is published, **And** a subsequent `search` with `feature="demo"` raises `UnknownSourceError`. |
| AC-005 | REQ-004, REQ-009 | **Given** a registered source with items, **When** `search(SearchQuery(free_text="..."))` is called, **Then** a `SearchResult` is returned whose items are `SearchResultItem`(feature, item_id, fields) for the matching items, **And** the page metadata (total, offset, limit) is set. |
| AC-006 | REQ-004 | **Given** two or more registered sources, **When** `search` is called without `feature`, **Then** the query fans out to all registered sources, **And** the combined page concatenates the per-source pages in registration order, **And** `total` equals the sum of the per-source totals. |
| AC-007 | REQ-005 | **Given** a registered source with N items, **When** `search` is called with no free text and no filters, **Then** all N items match (total == N). |
| AC-008 | REQ-005 | **Given** a registered source with N items, **When** `search` is called with `free_text=""`, **Then** the result equals the result for `free_text=None` (no free-text constraint). |
| AC-009 | REQ-006 | **Given** a source with a filterable string field, **When** `search` is called with an `equals` filter, **Then** only items whose field equals the value (case-insensitive) are returned. |
| AC-010 | REQ-006 | **Given** a source with a filterable string field, **When** `search` is called with a `contains` filter, **Then** matching is case-insensitive (a value differing only in case also matches). |
| AC-011 | REQ-006 | **Given** a source with two filterable fields, **When** `search` is called with an AND group over both, **Then** only items satisfying both conditions are returned. |
| AC-012 | REQ-006 | **Given** a source with two filterable fields, **When** `search` is called with an OR group over both, **Then** items satisfying either condition are returned. |
| AC-013 | REQ-006 | **Given** a source with a filterable number field, **When** `search` is called with gt/gte/lt/lte filters, **Then** only items with a value strictly greater / greater-or-equal / strictly less / less-or-equal are returned. |
| AC-014 | REQ-006 | **Given** a source with a filterable field, **When** `search` is called with an `in_list` filter, **Then** only items whose field value is in the list are returned. |
| AC-015 | REQ-006 | **Given** a source with a nullable filterable field, **When** `search` is called with an `is_null` filter, **Then** only items whose field is None are returned. |
| AC-016 | REQ-007 | **Given** a source with more items than the default page size, **When** `search` is called without `limit`, **Then** at most `search.default_page_size` items are returned, **And** `total` reflects all matches. |
| AC-017 | REQ-007 | **Given** a source, **When** `search` is called with `limit > search.max_page_size`, **Then** the effective limit is clamped to `search.max_page_size` (no error). |
| AC-018 | REQ-007 | **Given** a source with matches, **When** `search` is called with successive offsets, **Then** the pages skip correctly (no overlap, no gaps), **And** `total` is unchanged across pages. |
| AC-019 | REQ-007 | **Given** a source with M matches, **When** `search` is called with `offset >= M`, **Then** an empty item list is returned (no error), **And** `total == M`. |
| AC-020 | REQ-008 | **Given** a source with a sortable field, **When** `search` is called with `Sort(field, direction)`, **Then** the items are ordered by that field in the given direction (overriding the source's default ordering). |
| AC-021 | REQ-008 | **Given** a source whose items tie on the sort field, **When** `search` is called with that sort, **Then** the ties are broken by the source's default ordering (stable). |
| AC-022 | REQ-009 | **Given** a source with declared display fields, **When** `search` returns items, **Then** each item's `fields` contains exactly the declared display fields' values, **And** the caller can render the item without calling the source feature. |
| AC-023 | REQ-010 | **Given** a query with `feature="unknown"`, **When** `search` is called, **Then** an `UnknownSourceError` is raised (a `SearchError` subclass, not ValueError). |
| AC-024 | REQ-010 | **Given** a malformed query (`limit < 1`, `offset < 0`, an invalid operator for a field's type, a filter on a non-filterable field, a sort on a non-sortable field, or a value of the wrong type), **When** `search` is called, **Then** a `MalformedQueryError` is raised identifying the reason (and the field/source where applicable). |
| AC-025 | REQ-011 | **Given** a global fan-out where one source raises during its query, **When** `search` is called, **Then** a `SearchResult` is returned with the other sources' items, **And** a failure marker for the failing source (feature, reason `query_failed`, error kind), **And** a `SourceQueryFailed` event is published. |
| AC-026 | REQ-010 | **Given** a single-source query (`feature` set) where the source raises, **When** `search` is called, **Then** a `SourceQueryFailedError` is raised (source + reason + error kind). |
| AC-027 | REQ-012 | **Given** a source with string values, **When** `search` is called with free text/filters differing only in case, surrounding whitespace, or Unicode normalization form, **Then** the matching result is identical (case-folded + NFC + trimmed). |
| AC-028 | REQ-013 | **Given** a settings registry, **When** `register_settings(registry)` is called, **Then** the three keys are registered with defaults 100 / 1000 / 5000, **And** changing a key changes the behavior on the next operation (live read). |
| AC-029 | REQ-014 | **Given** a collector publisher, **When** a source is registered, unregistered, and a source query fails, **Then** `SourceRegistered`, `SourceUnregistered`, and `SourceQueryFailed` are published respectively, **And** no event is published per query. |
| AC-030 | REQ-015 | **Given** the shared logging feature configured at the default level, **When** service methods are invoked, **Then** entry/exit tracing occurs via `@logged_class`, **And** query text and result content never appear in log records. |
| AC-031 | REQ-016 | **Given** a service constructed with a denying `PermissionChecker`, **When** `search` is called, **Then** the checker's denial is raised and propagates (no result is returned, no source is queried); **And** given an allowing checker, **When** `search` is called, **Then** the result is returned normally. |
| AC-032 | REQ-017 | **Given** no singleton yet, **When** `get_search_service()` is called, **Then** the singleton is created, **And** subsequent calls return the same instance, **And** `reset_search_service()` clears it; **And** `SearchService.reset()` clears all registrations. |
| AC-033 | REQ-019 | **Given** a source whose query exceeds the live `search.source_timeout`, **When** `search` is called, **Then** (global) a failure marker with reason `timeout` is returned, **And** (single-source) a `SourceQueryFailedError` with reason `timeout` is raised. |
| AC-034 | REQ-020 | **Given** a `UserRepository` with users, **When** `build_user_source(repository)` is registered and `search` is called over users (free text on username/email/display_name; filters on is_active/created_at/updated_at), **Then** matching users are returned with `feature == "usermanagement"`, `item_id` = the user id, and the declared display fields. |
| AC-035 | REQ-021 | **Given** a `FileRepository` with files, **When** `build_file_source(repository)` is registered and `search` is called over files (free text on key/namespace/original_filename; filters on detected_mime_type/size/created_at/updated_at), **Then** matching files are returned with `feature == "filemanagement"`, `item_id` = the file id, and the declared display fields. |
| AC-036 | REQ-022 | **Given** a `SessionRepository` with sessions, **When** `build_session_source(repository)` is registered and `search` is called over sessions (filters on user_id/created_at/expires_at/revoked/login_method), **Then** matching sessions are returned with `feature == "sessionmanagement"`, `item_id` = the session id, and the declared display fields. |
| AC-037 | REQ-023 | **Given** the search feature's public API, **When** inspected, **Then** it is an in-process service only (no HTTP/REST surface, no frontend dependency). |

## 6. Invariants

State invariants that hold over a large input space. These become Hypothesis property-based tests.

| ID | Invariant |
|----|-----------|
| INV-001 | Registration idempotency and atomicity: for any registration sequence, the registry state is a function of the last operation per name; identical re-registration is a no-op; a replace is atomic — a concurrent query sees either the old or the new source, never a partial state. |
| INV-002 | Query determinism: for any query and any source state, the result is deterministic — the same input + the same source state yields the same items, order, and total. |
| INV-003 | Pagination consistency: for any query, `len(items) <= limit`, `total >= 0`, `total` equals the sum of the per-source totals (global) or the source's total (single-source), and an offset beyond the last match yields an empty item list (no error). |
| INV-004 | Normalization invariance: for any string free text and any string filter value, the service passes the case-folded + NFC + trimmed form, and the source's matching is invariant to the case, Unicode normalization form, and surrounding whitespace of string values. |
| INV-005 | Secret-freedom: for any operation output — returned results, published events, raised error messages, log records — the query text, result content, and source data never appear (only structural metadata: source names, field names, counts, error kinds). |

## 7. Edge Cases & Error Conditions

| ID | Condition | Expected Behavior |
|----|-----------|-------------------|
| EDGE-001 | `search` with `feature` naming an unregistered source | An `UnknownSourceError` is raised |
| EDGE-002 | `search` (global) with no registered sources | An empty result (total 0, no failures) is returned, no error |
| EDGE-003 | `search` with `limit < 1` or `offset < 0` | A `MalformedQueryError` is raised |
| EDGE-004 | `search` with a filter on a field the source did not declare filterable (or the field is absent from the source's schema) | A `MalformedQueryError` is raised (identifying the source + field) |
| EDGE-005 | `search` with a filter operator invalid for the field's type (e.g., `contains` on a number) | A `MalformedQueryError` is raised |
| EDGE-006 | `search` with a sort on a field the source did not declare sortable | A `MalformedQueryError` is raised |
| EDGE-007 | `search` with `limit > search.max_page_size` | The limit is clamped to the cap (no error) |
| EDGE-008 | `search` with an offset beyond the last match | An empty item list is returned, `total` unchanged, no error |
| EDGE-009 | A source raising during a global search | Partial results + a failure marker for the failing source (resilient) |
| EDGE-010 | A source raising during a single-source query | A `SourceQueryFailedError` is raised |
| EDGE-011 | A source query exceeding `search.source_timeout` | A failure marker with reason `timeout` (global) / a `SourceQueryFailedError` with reason `timeout` (single-source) |
| EDGE-012 | A source with no searchable fields + a non-empty free text | The source contributes 0 matches (no error) |
| EDGE-013 | `unregister_source` with an unknown name | A no-op (no error, no event) |
| EDGE-014 | `register_source` with an identical source (same name + equal fields + same query function) | A no-op (no error, no event) |
| EDGE-015 | `register_source` with the same name but a different source | A replace (`SourceRegistered` is published); a concurrent in-flight query sees either the old or the new source (no partial state) |
| EDGE-016 | `reset()` with registered sources | All registrations are cleared, no events |
| EDGE-017 | A filter with `is_null` on a nullable field | Matches items where the field is None |
| EDGE-018 | An `in_list` filter with an empty list | Matches nothing |
| EDGE-019 | A concurrent register + search (one thread registers while another searches) | No crash; the search sees either the old or the new registration (no partial state) |
| EDGE-020 | A global fan-out where a filter/sort is valid for some sources but references a field absent or non-filterable in another source in the fan-out | A `MalformedQueryError` is raised (strict validation against every source in the fan-out) |
| EDGE-021 | `register_source` with an invalid source declaration (name/field name not matching the patterns, duplicate field names, unknown field type) | A `ValueError` is raised (argument-level) |

## 8. Non-Functional Requirements

| ID | Category | Requirement |
|----|----------|-------------|
| NFR-001 | Performance | A single-source query completes in < 100 ms (median) INCLUDING the `@logged` per-call overhead; `register_source` completes in < 5 ms (median); the budgets assume 10k–100k items per source, measured on local hardware against SQLite-backed sources with the shared logging feature configured at its default INFO level with a synchronous console sink (DEBUG method tracing off); the budgets hold including the per-call logging overhead at that level. |
| NFR-002 | Security | Query text, result content, and source data never appear in log records, events, error messages, or result payloads beyond the declared display fields; permission checks are fail-closed (a denial raises before any result is returned). |
| NFR-003 | Contract | The public API of `backend.search` allows breaking changes with a major version. **Recorded deviation:** the user explicitly deviated from the repository's additive-only NFR pattern for this feature — breaking changes are permitted and do not require a spec amendment; the deviation is recorded here per the user's decision (Q-124). |
| NFR-004 | Observability | Service methods are traced via the shared logging feature (`@logged_class`, `include_args=False`); source lifecycle and failure events are published to the injected publisher; no per-query events. |
| NFR-005 | Reliability | The registry and the query path are thread-safe; a source failure leaves no partial state; abandoned timeout threads are bounded by the worker pool; a failed operation leaves the registry unchanged. |

## 9. Observability & Logging

Every feature MUST be observable. Specify the logging behavior: which operations are logged, at what level, and with what context.

| Operation / Event | Level | Context |
|-------------------|-------|---------|
| Public method entry/exit (all `SearchService` methods) | DEBUG | Method qualname, elapsed ms; no arguments (`include_args` stays `False`) |
| Slow call (elapsed > `slow_threshold_ms` = 100 ms) | WARNING | Method qualname, elapsed ms |
| Method exception (`UnknownSourceError`, `MalformedQueryError`, `SourceQueryFailedError`) | DEBUG (exception line) | Exception type + secret-free message (no query text, no result content) |
| Source failure during a query (a source raises / a timeout) | WARNING | Source name, reason (`query_failed`/`timeout`) — no source data |
| Registration lifecycle (register/replace/unregister/reset) | DEBUG | Source name |
| Events (`SourceRegistered`, `SourceUnregistered`, `SourceQueryFailed`) | — | Published to the injected `EventPublisher` (not logged by this feature); non-sensitive data only (source names, reasons — no query text, no result content) |

- **Default level:** INFO; routine method tracing at DEBUG (off by default at the INFO default level); source failures are logged at WARNING.
- **Error conditions:** domain errors are logged via `@logged` exception tracing; query text and result content never appear in any log record (NFR-002).

## 10. Test Strategy

Map each requirement/AC to a test category. This drives the test file layout.

| ID | Test Category | Test File | Test Function |
|----|---------------|-----------|---------------|
| AC-001 | acceptance | `tests/acceptance/search/test_search.py` | `test_ac_001_register_source` |
| AC-002 | acceptance | `tests/acceptance/search/test_search.py` | `test_ac_002_replace_same_name` |
| AC-003 | acceptance | `tests/acceptance/search/test_search.py` | `test_ac_003_identical_reregistration_noop` |
| AC-004 | acceptance | `tests/acceptance/search/test_search.py` | `test_ac_004_unregister_source` |
| AC-005 | acceptance | `tests/acceptance/search/test_search.py` | `test_ac_005_search_free_text_returns_items` |
| AC-006 | acceptance | `tests/acceptance/search/test_search.py` | `test_ac_006_global_fanout_combined_pagination` |
| AC-007 | acceptance | `tests/acceptance/search/test_search.py` | `test_ac_007_no_constraints_match_all` |
| AC-008 | acceptance | `tests/acceptance/search/test_search.py` | `test_ac_008_empty_free_text_no_constraint` |
| AC-009 | acceptance | `tests/acceptance/search/test_search.py` | `test_ac_009_filter_equals` |
| AC-010 | acceptance | `tests/acceptance/search/test_search.py` | `test_ac_010_filter_contains_case_insensitive` |
| AC-011 | acceptance | `tests/acceptance/search/test_search.py` | `test_ac_011_filter_and_group` |
| AC-012 | acceptance | `tests/acceptance/search/test_search.py` | `test_ac_012_filter_or_group` |
| AC-013 | acceptance | `tests/acceptance/search/test_search.py` | `test_ac_013_filter_number_comparisons` |
| AC-014 | acceptance | `tests/acceptance/search/test_search.py` | `test_ac_014_filter_in_list` |
| AC-015 | acceptance | `tests/acceptance/search/test_search.py` | `test_ac_015_filter_is_null` |
| AC-016 | acceptance | `tests/acceptance/search/test_search.py` | `test_ac_016_default_page_size` |
| AC-017 | acceptance | `tests/acceptance/search/test_search.py` | `test_ac_017_limit_clamped_to_max` |
| AC-018 | acceptance | `tests/acceptance/search/test_search.py` | `test_ac_018_offset_pagination` |
| AC-019 | acceptance | `tests/acceptance/search/test_search.py` | `test_ac_019_offset_beyond_end_empty` |
| AC-020 | acceptance | `tests/acceptance/search/test_search.py` | `test_ac_020_sort_overrides_default_order` |
| AC-021 | acceptance | `tests/acceptance/search/test_search.py` | `test_ac_021_sort_stable_tie_break` |
| AC-022 | acceptance | `tests/acceptance/search/test_search.py` | `test_ac_022_result_item_shape` |
| AC-023 | acceptance | `tests/acceptance/search/test_search.py` | `test_ac_023_unknown_feature_error` |
| AC-024 | acceptance | `tests/acceptance/search/test_search.py` | `test_ac_024_malformed_query_errors` |
| AC-025 | integration | `tests/integration/search/test_search_integration.py` | `test_ac_025_global_fanout_source_failure_partial` |
| AC-026 | acceptance | `tests/acceptance/search/test_search.py` | `test_ac_026_single_source_failure_error` |
| AC-027 | acceptance | `tests/acceptance/search/test_search.py` | `test_ac_027_normalization_invariance` |
| AC-028 | acceptance | `tests/acceptance/search/test_search.py` | `test_ac_028_register_settings_live_read` |
| AC-029 | acceptance | `tests/acceptance/search/test_search.py` | `test_ac_029_lifecycle_and_failure_events` |
| AC-030 | acceptance | `tests/acceptance/search/test_search.py` | `test_ac_030_traced_no_query_in_logs` |
| AC-031 | acceptance | `tests/acceptance/search/test_search.py` | `test_ac_031_permission_enforcement` |
| AC-032 | acceptance | `tests/acceptance/search/test_search.py` | `test_ac_032_singleton_and_reset` |
| AC-033 | acceptance | `tests/acceptance/search/test_search.py` | `test_ac_033_source_timeout` |
| AC-034 | acceptance | `tests/acceptance/search/test_feature_sources.py` | `test_ac_034_user_source` |
| AC-035 | acceptance | `tests/acceptance/search/test_feature_sources.py` | `test_ac_035_file_source` |
| AC-036 | acceptance | `tests/acceptance/search/test_feature_sources.py` | `test_ac_036_session_source` |
| AC-037 | contract | `tests/contract/search/test_search_contracts.py` | `test_ac_037_backend_only_api` |
| INV-001 | property | `tests/property/search/test_search_properties.py` | `test_inv_001_registration_idempotent_atomic` |
| INV-002 | property | `tests/property/search/test_search_properties.py` | `test_inv_002_query_deterministic` |
| INV-003 | property | `tests/property/search/test_search_properties.py` | `test_inv_003_pagination_consistency` |
| INV-004 | property | `tests/property/search/test_search_properties.py` | `test_inv_004_normalization_invariance` |
| INV-005 | property | `tests/property/search/test_search_properties.py` | `test_inv_005_no_secrets_in_outputs` |
| EDGE-001 | unit | `tests/unit/search/test_search_edges.py` | `test_edge_001_unknown_feature` |
| EDGE-002 | unit | `tests/unit/search/test_search_edges.py` | `test_edge_002_global_no_sources_empty` |
| EDGE-003 | unit | `tests/unit/search/test_search_edges.py` | `test_edge_003_invalid_limit_offset` |
| EDGE-004 | unit | `tests/unit/search/test_search_edges.py` | `test_edge_004_non_filterable_field` |
| EDGE-005 | unit | `tests/unit/search/test_search_edges.py` | `test_edge_005_invalid_operator_for_type` |
| EDGE-006 | unit | `tests/unit/search/test_search_edges.py` | `test_edge_006_non_sortable_field` |
| EDGE-007 | unit | `tests/unit/search/test_search_edges.py` | `test_edge_007_limit_clamped` |
| EDGE-008 | unit | `tests/unit/search/test_search_edges.py` | `test_edge_008_offset_beyond_end` |
| EDGE-009 | unit | `tests/unit/search/test_search_edges.py` | `test_edge_009_global_source_raises_partial` |
| EDGE-010 | unit | `tests/unit/search/test_search_edges.py` | `test_edge_010_single_source_raises_error` |
| EDGE-011 | unit | `tests/unit/search/test_search_edges.py` | `test_edge_011_source_timeout` |
| EDGE-012 | unit | `tests/unit/search/test_search_edges.py` | `test_edge_012_no_searchable_fields_zero_matches` |
| EDGE-013 | unit | `tests/unit/search/test_search_edges.py` | `test_edge_013_unregister_unknown_noop` |
| EDGE-014 | unit | `tests/unit/search/test_search_edges.py` | `test_edge_014_identical_reregistration_noop` |
| EDGE-015 | unit | `tests/unit/search/test_search_edges.py` | `test_edge_015_replace_concurrent_consistent` |
| EDGE-016 | unit | `tests/unit/search/test_search_edges.py` | `test_edge_016_reset_clears_no_events` |
| EDGE-017 | unit | `tests/unit/search/test_search_edges.py` | `test_edge_017_is_null_matches_none` |
| EDGE-018 | unit | `tests/unit/search/test_search_edges.py` | `test_edge_018_in_list_empty_matches_nothing` |
| EDGE-019 | integration | `tests/integration/search/test_search_integration.py` | `test_edge_019_concurrent_register_search` |
| EDGE-020 | unit | `tests/unit/search/test_search_edges.py` | `test_edge_020_fanout_strict_validation` |
| EDGE-021 | unit | `tests/unit/search/test_search_edges.py` | `test_edge_021_invalid_source_declaration` |
| NFR-001 | contract | `tests/contract/search/test_search_contracts.py` | `test_nfr_001_performance_budgets` |
| NFR-002 | contract | `tests/contract/search/test_search_contracts.py` | `test_nfr_002_no_query_or_results_in_logs_events` |
| NFR-003 | contract | `tests/contract/search/test_search_contracts.py` | `test_nfr_003_public_api_contract` |
| NFR-004 | contract | `tests/contract/search/test_search_contracts.py` | `test_nfr_004_traced_service_events` |
| NFR-005 | integration | `tests/integration/search/test_search_integration.py` | `test_nfr_005_thread_safe_registry` |
| — | integration | `tests/integration/search/test_search_integration.py` | `test_startup_wiring_all_sources` |

## 11. Traceability Matrix

Maintain this matrix as tests are written and pass. Every normative requirement MUST have at least one executable test. (The live matrix is also maintained at `docs/verification/traceability.md`; this section is the spec's normative map.)

| Requirement | Acceptance Criterion | Test | Status |
|-------------|----------------------|------|--------|
| REQ-001 | AC-001 | `test_ac_001_register_source` | PENDING |
| REQ-002 | AC-001 | `test_ac_001_register_source` | PENDING |
| REQ-003 | AC-002 | `test_ac_002_replace_same_name` | PENDING |
| REQ-003 | AC-003 | `test_ac_003_identical_reregistration_noop` | PENDING |
| REQ-003 | AC-004 | `test_ac_004_unregister_source` | PENDING |
| REQ-004 | AC-005 | `test_ac_005_search_free_text_returns_items` | PENDING |
| REQ-004 | AC-006 | `test_ac_006_global_fanout_combined_pagination` | PENDING |
| REQ-005 | AC-007 | `test_ac_007_no_constraints_match_all` | PENDING |
| REQ-005 | AC-008 | `test_ac_008_empty_free_text_no_constraint` | PENDING |
| REQ-006 | AC-009 | `test_ac_009_filter_equals` | PENDING |
| REQ-006 | AC-010 | `test_ac_010_filter_contains_case_insensitive` | PENDING |
| REQ-006 | AC-011 | `test_ac_011_filter_and_group` | PENDING |
| REQ-006 | AC-012 | `test_ac_012_filter_or_group` | PENDING |
| REQ-006 | AC-013 | `test_ac_013_filter_number_comparisons` | PENDING |
| REQ-006 | AC-014 | `test_ac_014_filter_in_list` | PENDING |
| REQ-006 | AC-015 | `test_ac_015_filter_is_null` | PENDING |
| REQ-007 | AC-016 | `test_ac_016_default_page_size` | PENDING |
| REQ-007 | AC-017 | `test_ac_017_limit_clamped_to_max` | PENDING |
| REQ-007 | AC-018 | `test_ac_018_offset_pagination` | PENDING |
| REQ-007 | AC-019 | `test_ac_019_offset_beyond_end_empty` | PENDING |
| REQ-008 | AC-020 | `test_ac_020_sort_overrides_default_order` | PENDING |
| REQ-008 | AC-021 | `test_ac_021_sort_stable_tie_break` | PENDING |
| REQ-009 | AC-005 | `test_ac_005_search_free_text_returns_items` | PENDING |
| REQ-009 | AC-022 | `test_ac_022_result_item_shape` | PENDING |
| REQ-010 | AC-023 | `test_ac_023_unknown_feature_error` | PENDING |
| REQ-010 | AC-024 | `test_ac_024_malformed_query_errors` | PENDING |
| REQ-010 | AC-026 | `test_ac_026_single_source_failure_error` | PENDING |
| REQ-011 | AC-025 | `test_ac_025_global_fanout_source_failure_partial` | PENDING |
| REQ-012 | AC-027 | `test_ac_027_normalization_invariance` | PENDING |
| REQ-013 | AC-028 | `test_ac_028_register_settings_live_read` | PENDING |
| REQ-014 | AC-029 | `test_ac_029_lifecycle_and_failure_events` | PENDING |
| REQ-015 | AC-030 | `test_ac_030_traced_no_query_in_logs` | PENDING |
| REQ-016 | AC-031 | `test_ac_031_permission_enforcement` | PENDING |
| REQ-017 | AC-032 | `test_ac_032_singleton_and_reset` | PENDING |
| REQ-018 | INV-001 | `test_inv_001_registration_idempotent_atomic` | PENDING |
| REQ-019 | AC-033 | `test_ac_033_source_timeout` | PENDING |
| REQ-020 | AC-034 | `test_ac_034_user_source` | PENDING |
| REQ-021 | AC-035 | `test_ac_035_file_source` | PENDING |
| REQ-022 | AC-036 | `test_ac_036_session_source` | PENDING |
| REQ-023 | AC-037 | `test_ac_037_backend_only_api` | PENDING |
| INV-001 | — | `test_inv_001_registration_idempotent_atomic` | PENDING |
| INV-002 | — | `test_inv_002_query_deterministic` | PENDING |
| INV-003 | — | `test_inv_003_pagination_consistency` | PENDING |
| INV-004 | — | `test_inv_004_normalization_invariance` | PENDING |
| INV-005 | — | `test_inv_005_no_secrets_in_outputs` | PENDING |

## 12. Impact Analysis (CROSS-CUTTING)

Per-feature impact of this change. **No existing REQ or AC of any affected feature is touched** — every change is additive.

### 12.1 `search` (new feature — the change itself)

- **What changes:** a new backend feature `src/backend/search/` (source model, query model, result model, errors, events, `SearchService`, `feature_settings.py`, `feature_actions.py`) plus its test directories.
- **REQ/AC touched:** none existing — all new (REQ-001…REQ-023, AC-001…AC-037, INV-001…INV-005, EDGE-001…EDGE-021, NFR-001…NFR-005).
- **Public interface:** `backend.search` exports (§3); additive; the feature's public API is versioned per NFR-003 (breaking changes allowed with a major version, per Q-124).

### 12.2 `user-management` (source wiring)

- **What changes:** a new module `src/backend/usermanagement/search_source.py` with `build_user_source(repo) -> SearchSource` (name `usermanagement`, per §2 D19). No change to `UserManager`, `UserRepository`, models, events, or errors.
- **REQ/AC touched:** none.
- **Verification:** `tests/acceptance/search/test_feature_sources.py::test_ac_034_user_source` (AC-034); the user-management test suite stays GREEN (Phase 5 regression).

### 12.3 `file-management` (source wiring)

- **What changes:** a new module `src/backend/filemanagement/search_source.py` with `build_file_source(repo) -> SearchSource` (name `filemanagement`; full fetch via `list_by_namespace(None, limit=<large>, offset=0)` because the repository applies the LIMIT in SQL, per D19). No change to `FileService`, `FileRepository`, models, events, or errors.
- **REQ/AC touched:** none.
- **Verification:** `tests/acceptance/search/test_feature_sources.py::test_ac_035_file_source` (AC-035); the file-management test suite stays GREEN (Phase 5 regression).

### 12.4 `session-management` (source wiring)

- **What changes:** a new module `src/backend/sessionmanagement/search_source.py` with `build_session_source(repo) -> SearchSource` (name `sessionmanagement`, per §2 D19). No change to `SessionService`, events, or errors.
- **REQ/AC touched:** none.
- **Verification:** `tests/acceptance/search/test_feature_sources.py::test_ac_036_session_source` (AC-036); the session-management test suite stays GREEN (Phase 5 regression).

### 12.5 `authentication` (one additive repository method)

- **What changes:** a new **additive** `SessionRepository.list_all() -> Sequence[Session]` ABC method (all sessions, including revoked and expired, no user filter; implementation in `SqliteSessionRepository` returning the existing rows in `created_at` descending order, consistent with `list_for_user`). Backward-compatible per authentication NFR-003 (additive-only evolution — precedent: session-management REQ-017); custom repository implementations gain a new method (documented in the module docstring). No change to `AuthService` or any existing operation.
- **REQ/AC touched:** none.
- **Verification:** the `list_all` behavior is covered by `tests/acceptance/search/test_feature_sources.py::test_ac_036_session_source` (AC-036); the authentication test suite stays GREEN (Phase 5 regression).

### 12.6 `user-roles-permissions` (action declaration — additive)

- **What changes:** none in the permissions feature itself. The search feature declares its `search.search` action via its own `feature_actions.py` (`register_actions(catalog)`, D16); the catalog is additive. No change to `PermissionChecker`, `PermissionCatalog`, or any existing action.
- **REQ/AC touched:** none.
- **Verification:** `tests/acceptance/search/test_search.py::test_ac_031_permission_enforcement` (AC-031).

### 12.7 `shared` (no change)

- **What changes:** none. The search feature **consumes** `backend.shared` (`Principal`, `PermissionChecker`, `requires_permission`) and the shared logging feature; no shared code is added or modified.

### 12.8 Startup (application entrypoint)

- **What changes:** the application startup path gains the additive wiring per §3 (startup wiring) and D19 (feature settings, feature actions, then the three `register_source` calls after the repositories exist). This is the same pattern as the existing feature-owned `register_settings`/`register_actions` startup calls; no existing startup behavior changes.
- **Verification:** `tests/integration/search/test_search_integration.py::test_startup_wiring_all_sources` (REQ-023).

## 13. Out of Scope

- Any index, cache, or persistence for search results (D1, Q-101).
- Any frontend/UI for search (backend-only; the entry point is the `SearchService` API).
- Cross-source relevance ranking, facets, or analytics (Q-103: plain combined pagination).
- Source-side permission filtering beyond the source's own query function (each source decides what it returns; the search feature enforces the `search.search` action, not per-item access).
- Incremental indexing or change-event-driven index maintenance (stateless live query, Q-101).
- Any modification of existing features' behavior, models, events, or errors (all wiring is additive, §12).

## 14. Open Questions

None — all 27 decisions are answered (Q-100…Q-126, `AI_Questions.md`).
