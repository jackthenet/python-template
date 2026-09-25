"""The search service (docs/specs/search.md).

``SearchService``: the thread-safe in-memory source registry (REQ-001,
REQ-003, REQ-018) and the query entry point (REQ-004, REQ-005, REQ-009,
REQ-010, REQ-012). ``InMemorySource``: the public in-memory source for
tests/DI (REQ-017). Module singleton (REQ-017). The service is traced with
``@logged_class`` (``include_args=False`` so query text and result content
never appear in log records, REQ-015/NFR-002); the module functions are traced
with ``@logged``.
"""

from __future__ import annotations

import operator
import re
import threading
import unicodedata
from typing import TYPE_CHECKING, Any

from backend.logging import logged, logged_class
from backend.search.errors import UnknownSourceError
from backend.search.events import EventPublisher, SourceRegistered, SourceUnregistered
from backend.search.models import (
    FIELD_NAME_PATTERN,
    SOURCE_NAME_PATTERN,
    FieldType,
    FilterCondition,
    FilterGroup,
    FilterOperator,
    SearchQuery,
    SearchResult,
    SearchResultItem,
    SearchSource,
    SourceField,
    SourceItem,
    SourcePage,
    SourceQueryContext,
)
from backend.shared import Principal, requires_permission

if TYPE_CHECKING:
    from backend.settings import SettingsRegistry
    from backend.shared import PermissionChecker

# The system principal (``Principal()`` = ``user_id=None``): the default
# trailing parameter of the enforced ``search`` method (ADR-071 pattern).
_SYSTEM_PRINCIPAL = Principal()

# Settings keys + hardcoded fallback defaults (REQ-013; read live, D14).
_DEFAULT_PAGE_SIZE = 100
_MAX_PAGE_SIZE = 1000


# --- Normalization + declaration helpers (module level) ---------------------


def _normalize(value: str) -> str:
    """Normalize text for matching: case-fold + NFC + trim (D13, REQ-012)."""
    v = value.casefold()
    v = unicodedata.normalize("NFC", v)
    return v.strip()


def _read_setting(registry: SettingsRegistry | None, key: str, fallback: Any) -> Any:
    """Read ``key`` live from ``registry``; return ``fallback`` when the
    registry does not exist or the key is unregistered (REQ-013)."""
    if registry is None or not registry.has(key):
        return fallback
    return registry.get_value(key)


def _validate_source_declaration(source: SearchSource) -> None:
    """Validate a source declaration (EDGE-021): the name/field-name patterns
    and duplicate field names. Raises ``ValueError`` (argument level)."""
    if not re.match(SOURCE_NAME_PATTERN, source.name):
        raise ValueError(f"invalid source name: {source.name!r}")
    seen: set[str] = set()
    for field in source.fields:
        if not re.match(FIELD_NAME_PATTERN, field.name):
            raise ValueError(f"invalid field name: {field.name!r}")
        if field.name in seen:
            raise ValueError(f"duplicate field name: {field.name!r}")
        seen.add(field.name)


def _is_identical_source(existing: SearchSource, source: SearchSource) -> bool:
    """Whether two sources are identical (same name + equal fields + same
    query function) (REQ-003, D2)."""
    if existing.name != source.name:
        return False
    if existing.query is not source.query:
        return False  # the same query function (identity)
    if len(existing.fields) != len(source.fields):
        return False
    return all(a == b for a, b in zip(existing.fields, source.fields, strict=True))


# --- In-memory filter evaluation (the source's query semantics, D4, D13) ----


def _free_text_matches(item: SourceItem, fields: list[SourceField], free_text: str) -> bool:
    """A non-empty free text matches if any declared-searchable string field
    contains the normalized text (REQ-005, D13)."""
    for f in fields:
        if not f.searchable:
            continue
        value = item.fields.get(f.name)
        if value is None:
            continue
        if isinstance(value, str) and free_text in _normalize(value):
            return True
    return False


def _eval_group(group: FilterGroup, fields: dict[str, Any], declared: dict[str, SourceField]) -> bool:
    """Evaluate a (nestable) AND/OR filter group over an item's field values
    (REQ-006, D4)."""
    results = [
        _eval_group(cond, fields, declared)
        if isinstance(cond, FilterGroup)
        else _eval_condition(cond, fields, declared)
        for cond in group.conditions
    ]
    return all(results) if group.operator == "and" else any(results)


def _eval_condition(cond: FilterCondition, fields: dict[str, Any], declared: dict[str, SourceField]) -> bool:
    """Evaluate a single filter condition over an item's field values
    (REQ-006, D4)."""
    field = declared.get(cond.field)
    if field is None:
        return False  # the field is not declared (validation is the service's)
    value = fields.get(cond.field)  # absent → None
    return _apply_operator(field.type, value, cond.operator, cond.value)


_COMPARISONS: dict[FilterOperator, Any] = {
    FilterOperator.GT: operator.gt,
    FilterOperator.GTE: operator.ge,
    FilterOperator.LT: operator.lt,
    FilterOperator.LTE: operator.le,
}


def _apply_string_operator(value: Any, op: FilterOperator, fv: Any) -> bool:
    """String operators (D4): case-insensitive via the normalized value."""
    v = _normalize(str(value))
    if op is FilterOperator.EQUALS:
        return v == _normalize(str(fv))
    if op is FilterOperator.CONTAINS:
        return _normalize(str(fv)) in v
    if op is FilterOperator.STARTS_WITH:
        return v.startswith(_normalize(str(fv)))
    if op is FilterOperator.IN_LIST:
        return any(_normalize(str(x)) == v for x in fv) if isinstance(fv, (list, tuple)) else False
    return False


def _apply_exact_operator(value: Any, op: FilterOperator, fv: Any) -> bool:
    """number / boolean / datetime operators: exact (REQ-012)."""
    if op is FilterOperator.EQUALS:
        return value == fv
    if op is FilterOperator.IN_LIST:
        return value in fv if isinstance(fv, (list, tuple)) else False
    comparison = _COMPARISONS.get(op)
    return comparison(value, fv) if comparison is not None else False


def _apply_operator(ftype: FieldType, value: Any, op: FilterOperator, fv: Any) -> bool:
    """Apply a filter operator to a field value with the per-type semantics
    (D4): string matching is case-insensitive (normalized); number/boolean/
    datetime are exact (REQ-012)."""
    if op is FilterOperator.IS_NULL:
        return value is None
    if value is None or fv is None:
        return False  # a None value or filter value matches no non-null operator
    if ftype is FieldType.STRING:
        return _apply_string_operator(value, op, fv)
    return _apply_exact_operator(value, op, fv)


def _sort_key(value: Any) -> tuple:
    """A sort key: ``None`` last, strings by their normalized value, others
    exact (D8; deterministic)."""
    if value is None:
        return (1, "")
    if isinstance(value, str):
        return (0, _normalize(value))
    return (0, value)


# --- Service -----------------------------------------------------------------


@logged_class(slow_threshold_ms=100, include_args=False)
class SearchService:
    """The search service: the thread-safe in-memory source registry (REQ-001,
    REQ-003, REQ-018) and the query entry point (REQ-004, REQ-005, REQ-009,
    REQ-010, REQ-012).

    The constructor takes an optional ``EventPublisher`` (a ``None`` event bus
    means no events and no error, REQ-014), an optional settings registry (a
    ``None`` registry uses the shared ``get_settings_registry()``, REQ-013),
    and an optional ``PermissionChecker`` (a ``None`` checker is standalone
    mode, no enforcement, REQ-016).
    """

    def __init__(
        self,
        event_bus: EventPublisher | None = None,
        settings_registry: SettingsRegistry | None = None,
        permission_service: PermissionChecker | None = None,
    ) -> None:
        self._event_bus = event_bus
        self._settings_registry = settings_registry
        self._permission_service = permission_service
        self._lock = threading.RLock()
        self._sources: dict[str, SearchSource] = {}

    # -- Registration lifecycle (REQ-001, REQ-003) --------------------------

    def register_source(self, source: SearchSource) -> None:
        """Register a source (REQ-001).

        Re-registration with the same name replaces atomically (a
        ``SourceRegistered`` event is published); an identical re-registration
        (same name + equal fields + same query function) is an idempotent no-op
        (no event); an invalid declaration (name/field name not matching the
        patterns, duplicate field names) raises ``ValueError`` (argument level,
        EDGE-021).
        """
        _validate_source_declaration(source)
        with self._lock:
            existing = self._sources.get(source.name)
            if existing is not None and _is_identical_source(existing, source):
                return  # idempotent no-op (no event)
            self._sources[source.name] = source
        self._publish(SourceRegistered(source=source.name))

    def unregister_source(self, name: str) -> None:
        """Remove a source (REQ-003). An unknown name is a no-op (no event,
        EDGE-013)."""
        with self._lock:
            if name not in self._sources:
                return
            del self._sources[name]
        self._publish(SourceUnregistered(source=name))

    def list_sources(self) -> list[str]:
        """The registered source names in registration order (REQ-001)."""
        with self._lock:
            return list(self._sources)

    def reset(self) -> None:
        """Clear all registrations (no events) (REQ-003, REQ-017, EDGE-016)."""
        with self._lock:
            self._sources.clear()

    # -- Query entry point (REQ-004, REQ-005, REQ-009, REQ-010, REQ-012) ----

    @requires_permission("search.search")
    def search(self, query: SearchQuery, principal: Principal = _SYSTEM_PRINCIPAL) -> SearchResult:
        """Search the registered sources (REQ-004).

        A ``feature`` set queries that single source (an unknown feature raises
        ``UnknownSourceError``, REQ-010/EDGE-001); a ``feature`` omitted fans
        out to all registered sources (combined pagination, REQ-004/D6). The
        free text is normalized (case-folded + NFC + trimmed; empty/None = no
        constraint, REQ-012/REQ-005) before fan-out.
        """
        with self._lock:
            if query.feature is not None:
                source = self._sources.get(query.feature)
                if source is None:
                    raise UnknownSourceError(query.feature)
                sources = [source]
            else:
                sources = list(self._sources.values())
        free_text = _normalize(query.free_text) if query.free_text is not None else None
        if free_text == "":
            free_text = None
        limit = self._effective_limit(query.limit)
        ctx = SourceQueryContext(
            free_text=free_text,
            filters=query.filters,
            offset=query.offset,
            limit=limit,
            sort=query.sort,
        )
        items: list[SearchResultItem] = []
        total = 0
        for source in sources:
            page = source.query(ctx)
            total += page.total
            for item in page.items:
                items.append(SearchResultItem(feature=source.name, item_id=item.item_id, fields=item.fields))
        return SearchResult(items=items, total=total, offset=query.offset, limit=limit, failures=[])

    # -- Wiring helpers -------------------------------------------------------

    def _registry(self) -> SettingsRegistry | None:
        """The settings registry: the injected one, or the shared singleton."""
        if self._settings_registry is not None:
            return self._settings_registry
        from backend.settings import get_settings_registry

        return get_settings_registry(required=False)

    def _effective_limit(self, limit: int | None) -> int:
        """The effective limit: the live ``search.default_page_size`` when
        ``limit`` is None, clamped to the live ``search.max_page_size``
        (REQ-007/D5; read live, REQ-013)."""
        registry = self._registry()
        if limit is None:
            limit = int(_read_setting(registry, "search.default_page_size", _DEFAULT_PAGE_SIZE))
        return min(limit, int(_read_setting(registry, "search.max_page_size", _MAX_PAGE_SIZE)))

    def _publish(self, event: object) -> None:
        """Publish ``event`` to the injected publisher (a ``None`` publisher
        means no events and no error, REQ-014)."""
        if self._event_bus is not None:
            self._event_bus.publish(event)


# --- Public in-memory source (REQ-017, InMemoryStorageBackend precedent) ----


class InMemorySource:
    """Public in-memory source for tests/DI (REQ-017).

    The default ordering = the items' insertion order; the query function
    applies free text, filters, sort, and pagination in memory with the spec's
    normalization and per-type semantics (D13, D4).
    """

    def __init__(self, name: str, fields: list[SourceField], items: list[SourceItem]) -> None:
        self._name = name
        self._fields = list(fields)
        self._items = list(items)
        self._declared = {f.name: f for f in self._fields}

    def to_source(self) -> SearchSource:
        """A ``SearchSource`` over this in-memory source's items."""
        return SearchSource(name=self._name, fields=self._fields, query=self._query)

    def _query(self, ctx: SourceQueryContext) -> SourcePage:
        """Apply free text, filters, sort, and pagination in memory (D13, D4)."""
        free_text = _normalize(ctx.free_text) if ctx.free_text is not None else None
        matched = [
            item
            for item in self._items
            if (free_text is None or _free_text_matches(item, self._fields, free_text))
            and (ctx.filters is None or _eval_group(ctx.filters, item.fields, self._declared))
        ]
        total = len(matched)
        if ctx.sort is not None:
            sort_field = ctx.sort.field
            reverse = ctx.sort.direction == "desc"
            matched = sorted(matched, key=lambda item: _sort_key(item.fields.get(sort_field)), reverse=reverse)
        page = matched[ctx.offset : ctx.offset + ctx.limit]
        return SourcePage(items=page, total=total)


# --- Module singleton (REQ-017) ----------------------------------------------

_singleton: list[SearchService | None] = [None]
_singleton_lock = threading.Lock()


@logged(slow_threshold_ms=5)
def get_search_service(
    event_bus: EventPublisher | None = None,
    settings_registry: SettingsRegistry | None = None,
    permission_service: PermissionChecker | None = None,
) -> SearchService:
    """The module singleton ``SearchService`` (REQ-017): the first call
    creates it; later calls return it."""
    with _singleton_lock:
        if _singleton[0] is None:
            _singleton[0] = SearchService(
                event_bus=event_bus, settings_registry=settings_registry, permission_service=permission_service
            )
        return _singleton[0]


@logged(slow_threshold_ms=5)
def reset_search_service() -> None:
    """Clear the module singleton (tests) (REQ-017)."""
    with _singleton_lock:
        _singleton[0] = None
