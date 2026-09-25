"""Search feature — cross-feature search over registered sources.

Public API:
- Models: ``SearchSource``, ``SourceField``, ``FieldType``, ``SourceItem``,
  ``SourcePage``, ``SourceQueryContext``, ``SearchQuery``, ``FilterCondition``,
  ``FilterGroup``, ``FilterOperator``, ``Sort``, ``SearchResult``,
  ``SearchResultItem``, ``SourceFailure``.
- Errors: the ``SearchError`` hierarchy (``UnknownSourceError``,
  ``MalformedQueryError``, ``SourceQueryFailedError``).
- Events: ``SourceRegistered``, ``SourceUnregistered``, ``SourceQueryFailed``.
- Settings: ``register_settings`` (feature-owned settings registration).
- Service: ``SearchService``, ``InMemorySource`` plus the module singleton
  ``get_search_service()`` / ``reset_search_service()``.
"""

from backend.search.errors import (
    MalformedQueryError,
    SearchError,
    SourceQueryFailedError,
    UnknownSourceError,
)
from backend.search.events import (
    SourceQueryFailed,
    SourceRegistered,
    SourceUnregistered,
)
from backend.search.feature_settings import register_settings
from backend.search.models import (
    FieldType,
    FilterCondition,
    FilterGroup,
    FilterOperator,
    SearchQuery,
    SearchResult,
    SearchResultItem,
    SearchSource,
    Sort,
    SourceFailure,
    SourceField,
    SourceItem,
    SourcePage,
    SourceQueryContext,
)
from backend.search.service import (
    InMemorySource,
    SearchService,
    get_search_service,
    reset_search_service,
)

__all__ = [
    "FieldType",
    "FilterCondition",
    "FilterGroup",
    "FilterOperator",
    "InMemorySource",
    "MalformedQueryError",
    "SearchError",
    "SearchQuery",
    "SearchResult",
    "SearchResultItem",
    "SearchService",
    "SearchSource",
    "Sort",
    "SourceFailure",
    "SourceField",
    "SourceItem",
    "SourcePage",
    "SourceQueryContext",
    "SourceQueryFailed",
    "SourceQueryFailedError",
    "SourceRegistered",
    "SourceUnregistered",
    "UnknownSourceError",
    "get_search_service",
    "register_settings",
    "reset_search_service",
]
