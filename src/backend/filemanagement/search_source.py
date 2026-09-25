"""The file-management search source (docs/specs/search.md, REQ-021, D19).

An additive module that exposes files as a search source named
``filemanagement`` (ADR-077): the source's field schema plus a sync query
function over the existing :class:`FileRepository` (``list_by_namespace``
called with ``namespace=None`` and a large ``limit`` for a full fetch,
because the repository applies the ``LIMIT`` in SQL). No new persistence,
no new behavior in the feature's operations — the source queries the
feature's existing repository (D19).

The query function applies free text, filters, sort, and pagination with
the spec's normalization and per-type semantics (D13, D4, D8): text
matching is case-insensitive (case-folded + NFC + trimmed); number/datetime
are exact. The default ordering (``sort`` is ``None``) is ``created_at``
ascending.
"""

from __future__ import annotations

import operator
import unicodedata
from typing import Any

from backend.filemanagement.models import FileRecord
from backend.filemanagement.repository import FileRepository
from backend.search import (
    FieldType,
    FilterCondition,
    FilterGroup,
    FilterOperator,
    SearchSource,
    SourceField,
    SourceItem,
    SourcePage,
    SourceQueryContext,
)

# The source name (the feature name; REQ-021).
_SOURCE_NAME = "filemanagement"

# The full-fetch limit for ``list_by_namespace`` (the repository applies the
# LIMIT in SQL, so a large limit is the full fetch; REQ-021).
_FULL_FETCH_LIMIT = 100_000

# The field schema (REQ-021): key/namespace/original_filename — string,
# searchable/filterable/sortable/display; detected_mime_type — string,
# filterable/sortable/display; size — number, filterable/sortable/display;
# created_at/updated_at — datetime, filterable/sortable/display.
_FIELDS: list[SourceField] = [
    SourceField(
        name="key",
        type=FieldType.STRING,
        searchable=True,
        filterable=True,
        sortable=True,
        display=True,
    ),
    SourceField(
        name="namespace",
        type=FieldType.STRING,
        searchable=True,
        filterable=True,
        sortable=True,
        display=True,
    ),
    SourceField(
        name="original_filename",
        type=FieldType.STRING,
        searchable=True,
        filterable=True,
        sortable=True,
        display=True,
    ),
    SourceField(name="detected_mime_type", type=FieldType.STRING, filterable=True, sortable=True, display=True),
    SourceField(name="size", type=FieldType.NUMBER, filterable=True, sortable=True, display=True),
    SourceField(name="created_at", type=FieldType.DATETIME, filterable=True, sortable=True, display=True),
    SourceField(name="updated_at", type=FieldType.DATETIME, filterable=True, sortable=True, display=True),
]

# The searchable string fields (free text; REQ-021).
_SEARCHABLE = ("key", "namespace", "original_filename")

# The comparison operators for exact (number/datetime) fields (D4).
_COMPARISONS: dict[FilterOperator, Any] = {
    FilterOperator.GT: operator.gt,
    FilterOperator.GTE: operator.ge,
    FilterOperator.LT: operator.lt,
    FilterOperator.LTE: operator.le,
}


def _normalize(value: str) -> str:
    """Normalize text for matching: case-fold + NFC + trim (D13, REQ-012)."""
    v = value.casefold()
    v = unicodedata.normalize("NFC", v)
    return v.strip()


def _file_fields(record: FileRecord) -> dict[str, Any]:
    """The declared display field values for ``record`` (REQ-021)."""
    return {
        "key": record.key,
        "namespace": record.namespace,
        "original_filename": record.original_filename,
        "detected_mime_type": record.detected_mime_type,
        "size": record.size,
        "created_at": record.created_at,
        "updated_at": record.updated_at,
    }


def _free_text_matches(fields: dict[str, Any], free_text: str) -> bool:
    """A non-empty (normalized) free text matches if any searchable string
    field contains it (REQ-005, D13)."""
    for name in _SEARCHABLE:
        value = fields.get(name)
        if isinstance(value, str) and free_text in _normalize(value):
            return True
    return False


def _eval_group(group: FilterGroup, fields: dict[str, Any]) -> bool:
    """Evaluate a (nestable) AND/OR filter group over the field values
    (REQ-006, D4)."""
    results = [
        _eval_group(cond, fields) if isinstance(cond, FilterGroup) else _eval_condition(cond, fields)
        for cond in group.conditions
    ]
    return all(results) if group.operator == "and" else any(results)


def _eval_condition(cond: FilterCondition, fields: dict[str, Any]) -> bool:
    """Evaluate a single filter condition over the field values (REQ-006, D4):
    string matching is case-insensitive (normalized); number/datetime are
    exact (REQ-012)."""
    value = fields.get(cond.field)
    if cond.operator is FilterOperator.IS_NULL:
        return value is None
    if value is None or cond.value is None:
        return False  # a None value or filter value matches no non-null operator
    if isinstance(value, str):
        return _apply_string_operator(value, cond.operator, cond.value)
    return _apply_exact_operator(value, cond.operator, cond.value)


def _apply_string_operator(value: str, op: FilterOperator, fv: Any) -> bool:
    """String operators (D4): case-insensitive via the normalized value."""
    v = _normalize(value)
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
    """number / datetime operators: exact (REQ-012)."""
    if op is FilterOperator.EQUALS:
        return value == fv
    if op is FilterOperator.IN_LIST:
        return value in fv if isinstance(fv, (list, tuple)) else False
    comparison = _COMPARISONS.get(op)
    return comparison(value, fv) if comparison is not None else False


def _sort_key(value: Any) -> tuple:
    """A sort key: ``None`` last, strings by their normalized value, others
    exact (D8; deterministic)."""
    if value is None:
        return (1, "")
    if isinstance(value, str):
        return (0, _normalize(value))
    return (0, value)


def _query(repository: FileRepository, ctx: SourceQueryContext) -> SourcePage:
    """The source's query function (REQ-021): over the existing
    ``FileRepository.list_by_namespace`` (full fetch via
    ``list_by_namespace(None, limit=<large>, offset=0)`` because the
    repository applies the LIMIT in SQL); applies free text, filters, sort,
    and pagination; the default ordering is ``created_at`` ascending."""
    records = repository.list_by_namespace(None, limit=_FULL_FETCH_LIMIT, offset=0)
    items = [SourceItem(item_id=str(record.id), fields=_file_fields(record)) for record in records]
    matched = [
        item
        for item in items
        if (ctx.free_text is None or _free_text_matches(item.fields, ctx.free_text))
        and (ctx.filters is None or _eval_group(ctx.filters, item.fields))
    ]
    total = len(matched)
    if ctx.sort is not None:
        sort_field = ctx.sort.field
        reverse = ctx.sort.direction == "desc"
        matched = sorted(matched, key=lambda item: _sort_key(item.fields.get(sort_field)), reverse=reverse)
    else:
        # Default ordering: created_at ascending (REQ-021).
        matched = sorted(matched, key=lambda item: _sort_key(item.fields.get("created_at")))
    page = matched[ctx.offset : ctx.offset + ctx.limit]
    return SourcePage(items=page, total=total)


def build_file_source(repository: FileRepository) -> SearchSource:
    """Build the file-management search source over ``repository``
    (REQ-021, D19, ADR-077): name ``filemanagement``, the field schema, and
    the sync query function over the existing ``FileRepository.list_by_namespace``.
    """
    return SearchSource(name=_SOURCE_NAME, fields=list(_FIELDS), query=lambda ctx: _query(repository, ctx))
