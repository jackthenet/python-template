"""Data structures for the search feature (docs/specs/search.md, section 3).

The closed field-type set (REQ-002), the source model (REQ-001), the query
model (REQ-004, REQ-006), and the result shapes (REQ-009, REQ-011). Models are
plain data containers: declaration validation (name/field-name patterns,
duplicate field names) happens at registration (``SearchService.register_source``),
not in the models (EDGE-021).
"""

from __future__ import annotations

from collections.abc import Callable
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel

# --- Field types (closed set; D1) ---


class FieldType(StrEnum):
    """The closed field-type set (REQ-002): a list field is not representable
    and not exposed."""

    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    DATETIME = "datetime"


# --- Name patterns (D1; validated at registration, EDGE-021) ---

SOURCE_NAME_PATTERN: str = r"^[a-z0-9][a-z0-9._]{0,63}$"
FIELD_NAME_PATTERN: str = r"^[a-z0-9][a-z0-9._]{0,63}$"


# --- Source model (D1) ---


class SourceField(BaseModel):
    """A declared source field (REQ-002): a name, a type from the closed set,
    and the searchable/filterable/sortable/display flags."""

    name: str
    type: FieldType
    searchable: bool = False
    filterable: bool = False
    sortable: bool = False
    display: bool = False


class SourceItem(BaseModel):
    """A source item: an opaque ``item_id`` + the declared display field values."""

    item_id: str
    fields: dict[str, Any]


class SourcePage(BaseModel):
    """A source's query result page: at most ``limit`` items starting at
    ``offset``, plus the total match count (ignoring pagination)."""

    items: list[SourceItem]
    total: int


# --- Query model (D3, D4) ---


class FilterOperator(StrEnum):
    """Filter DSL operators (REQ-006, D4)."""

    EQUALS = "equals"
    CONTAINS = "contains"
    STARTS_WITH = "starts_with"
    GT = "gt"
    GTE = "gte"
    LT = "lt"
    LTE = "lte"
    IN_LIST = "in_list"
    IS_NULL = "is_null"


class FilterCondition(BaseModel):
    """A single filter condition (REQ-006): a field, an operator, and a value
    (required for every operator except ``is_null``)."""

    field: str
    operator: FilterOperator
    value: Any | None = None


class FilterGroup(BaseModel):
    """An AND/OR group over conditions (nestable) (REQ-006, D4)."""

    operator: Literal["and", "or"]
    conditions: list[FilterCondition | FilterGroup]


class Sort(BaseModel):
    """A user sort on a declared-sortable field (REQ-008)."""

    field: str
    direction: Literal["asc", "desc"] = "asc"


class SourceQueryContext(BaseModel):
    """The context passed to a source's query function (D1).

    ``free_text`` is normalized (case-folded, NFC, trimmed); ``None`` = no
    free-text constraint. ``limit`` is the effective limit (default applied,
    cap clamped). ``sort`` ``None`` = the source's default ordering.
    """

    free_text: str | None = None
    filters: FilterGroup | None = None
    offset: int = 0
    limit: int = 100
    sort: Sort | None = None


SourceQueryFn = Callable[[SourceQueryContext], SourcePage]


class SearchSource(BaseModel):
    """A named search source: name + field schema + sync query function (D1).

    The source's default ordering is the order ``query`` returns items in when
    ``sort`` is ``None`` (documented per source; D8).
    """

    name: str
    fields: list[SourceField]
    query: SourceQueryFn


class SearchQuery(BaseModel):
    """The query entry point's input (REQ-004, D3).

    ``free_text`` empty/None = no free-text constraint; ``feature`` omitted =
    fan out to all registered sources (combined pagination); ``limit`` None =
    the live ``search.default_page_size``.
    """

    free_text: str | None = None
    filters: FilterGroup | None = None
    feature: str | None = None
    offset: int = 0
    limit: int | None = None
    sort: Sort | None = None


# --- Result shapes (D9, D11) ---


class SearchResultItem(BaseModel):
    """A result item: ``feature`` (the source name) + ``item_id`` + the
    declared display field values (REQ-009)."""

    feature: str
    item_id: str
    fields: dict[str, Any]


class SourceFailure(BaseModel):
    """A per-source failure marker (resilient global fan-out, D11): the
    feature, the reason (``query_failed``/``timeout``), and the error kind
    (no sensitive data)."""

    feature: str
    reason: str
    error: str


class SearchResult(BaseModel):
    """The query entry point's result (REQ-009): the result items, the page
    metadata (total, offset, limit), and the per-source failure markers (empty
    for single-source queries)."""

    items: list[SearchResultItem]
    total: int
    offset: int
    limit: int
    failures: list[SourceFailure]
