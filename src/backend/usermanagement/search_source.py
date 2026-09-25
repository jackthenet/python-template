"""The user-management search source (docs/specs/search.md, REQ-020, D19).

An additive module that exposes users as a search source named
``usermanagement`` (ADR-077): the source's field schema plus a sync query
function over the existing :class:`UserRepository` (``list_all`` called with
``include_inactive=True`` so the ``is_active`` field is meaningful). No new
persistence, no new behavior in the feature's operations — the source queries
the feature's existing repository (D19).

The query function applies free text, filters, sort, and pagination with the
spec's normalization and per-type semantics (D13, D4, D8): text matching is
case-insensitive (case-folded + NFC + trimmed); boolean/datetime are exact.
The default ordering (``sort`` is ``None``) is ``username`` ascending.
"""

from __future__ import annotations

import operator
import unicodedata
from typing import Any

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
from backend.usermanagement.models import User
from backend.usermanagement.repository import UserRepository

# The source name (the feature name; REQ-020).
_SOURCE_NAME = "usermanagement"

# The field schema (REQ-020): username/email/display_name — string,
# searchable/filterable/sortable/display; is_active — boolean,
# filterable/sortable/display; created_at/updated_at — datetime,
# filterable/sortable/display.
_FIELDS: list[SourceField] = [
    SourceField(
        name="username",
        type=FieldType.STRING,
        searchable=True,
        filterable=True,
        sortable=True,
        display=True,
    ),
    SourceField(
        name="email",
        type=FieldType.STRING,
        searchable=True,
        filterable=True,
        sortable=True,
        display=True,
    ),
    SourceField(
        name="display_name",
        type=FieldType.STRING,
        searchable=True,
        filterable=True,
        sortable=True,
        display=True,
    ),
    SourceField(name="is_active", type=FieldType.BOOLEAN, filterable=True, sortable=True, display=True),
    SourceField(name="created_at", type=FieldType.DATETIME, filterable=True, sortable=True, display=True),
    SourceField(name="updated_at", type=FieldType.DATETIME, filterable=True, sortable=True, display=True),
]

# The searchable string fields (free text; REQ-020).
_SEARCHABLE = ("username", "email", "display_name")

# The comparison operators for exact (boolean/datetime) fields (D4).
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


def _user_fields(user: User) -> dict[str, Any]:
    """The declared display field values for ``user`` (REQ-020)."""
    return {
        "username": user.username,
        "email": user.email,
        "display_name": user.display_name,
        "is_active": user.is_active,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
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
    string matching is case-insensitive (normalized); boolean/datetime are
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
    """boolean / datetime operators: exact (REQ-012)."""
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


def _query(repository: UserRepository, ctx: SourceQueryContext) -> SourcePage:
    """The source's query function (REQ-020): over the existing
    ``UserRepository.list_all`` (``include_inactive=True`` so the
    ``is_active`` field is meaningful); applies free text, filters, sort, and
    pagination; the default ordering is ``username`` ascending."""
    users = repository.list_all(include_inactive=True)
    items = [SourceItem(item_id=str(user.id), fields=_user_fields(user)) for user in users]
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
        # Default ordering: username ascending (REQ-020).
        matched = sorted(matched, key=lambda item: _sort_key(item.fields.get("username")))
    page = matched[ctx.offset : ctx.offset + ctx.limit]
    return SourcePage(items=page, total=total)


def build_user_source(repository: UserRepository) -> SearchSource:
    """Build the user-management search source over ``repository``
    (REQ-020, D19, ADR-077): name ``usermanagement``, the field schema, and
    the sync query function over the existing ``UserRepository.list_all``.
    """
    return SearchSource(name=_SOURCE_NAME, fields=list(_FIELDS), query=lambda ctx: _query(repository, ctx))
