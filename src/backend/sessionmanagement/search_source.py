"""The session-management search source (docs/specs/search.md, REQ-022, D19).

An additive module that exposes sessions as a search source named
``sessionmanagement`` (ADR-077): the source's field schema plus a sync query
function over the existing :class:`SessionRepository` (``list_all`` — the
additive method from T-004, authentication — all sessions, any revocation
state, no user filter). No new persistence, no new behavior in the
feature's operations — the source queries the feature's existing repository
(D19).

The query function applies free text, filters, sort, and pagination with
the spec's normalization and per-type semantics (D13, D4, D8): text
matching is case-insensitive (case-folded + NFC + trimmed); boolean/datetime
are exact. The default ordering (``sort`` is ``None``) is ``created_at``
descending.
"""

from __future__ import annotations

import operator
import unicodedata
from typing import Any

from backend.authentication.models import Session
from backend.authentication.repositories import SessionRepository
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

# The source name (the feature name; REQ-022).
_SOURCE_NAME = "sessionmanagement"

# The field schema (REQ-022): session_id — string,
# searchable/filterable/sortable/display; user_id — string,
# filterable/sortable/display; created_at/expires_at — datetime,
# filterable/sortable/display; revoked — boolean,
# filterable/sortable/display; login_method — string,
# filterable/sortable/display.
_FIELDS: list[SourceField] = [
    SourceField(
        name="session_id",
        type=FieldType.STRING,
        searchable=True,
        filterable=True,
        sortable=True,
        display=True,
    ),
    SourceField(name="user_id", type=FieldType.STRING, filterable=True, sortable=True, display=True),
    SourceField(name="created_at", type=FieldType.DATETIME, filterable=True, sortable=True, display=True),
    SourceField(name="expires_at", type=FieldType.DATETIME, filterable=True, sortable=True, display=True),
    SourceField(name="revoked", type=FieldType.BOOLEAN, filterable=True, sortable=True, display=True),
    SourceField(name="login_method", type=FieldType.STRING, filterable=True, sortable=True, display=True),
]

# The searchable string fields (free text; REQ-022).
_SEARCHABLE = ("session_id",)

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


def _session_fields(session: Session) -> dict[str, Any]:
    """The declared display field values for ``session`` (REQ-022)."""
    return {
        "session_id": str(session.id),
        "user_id": str(session.user_id),
        "created_at": session.created_at,
        "expires_at": session.expires_at,
        "revoked": session.revoked,
        "login_method": session.login_method,
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


def _query(repository: SessionRepository, ctx: SourceQueryContext) -> SourcePage:
    """The source's query function (REQ-022): over the existing
    ``SessionRepository.list_all`` (the additive method from T-004,
    authentication — all sessions, any revocation state, no user filter);
    applies free text, filters, sort, and pagination; the default ordering
    is ``created_at`` descending."""
    sessions = repository.list_all()
    items = [SourceItem(item_id=str(session.id), fields=_session_fields(session)) for session in sessions]
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
        # Default ordering: created_at descending (REQ-022).
        matched = sorted(matched, key=lambda item: _sort_key(item.fields.get("created_at")), reverse=True)
    page = matched[ctx.offset : ctx.offset + ctx.limit]
    return SourcePage(items=page, total=total)


def build_session_source(repository: SessionRepository) -> SearchSource:
    """Build the session-management search source over ``repository``
    (REQ-022, D19, ADR-077): name ``sessionmanagement``, the field schema,
    and the sync query function over the existing
    ``SessionRepository.list_all``.
    """
    return SearchSource(name=_SOURCE_NAME, fields=list(_FIELDS), query=lambda ctx: _query(repository, ctx))
