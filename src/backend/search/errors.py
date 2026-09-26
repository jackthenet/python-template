"""The domain ``SearchError`` hierarchy (docs/specs/search.md, D10, REQ-010).

Domain errors (NOT ``ValueError``): an unknown feature in a query, a malformed
query, and a source raising during a single-source query. Messages carry
structural metadata only (source names, field names, reasons, error kinds) —
never query text, result content, or source data (NFR-002).
"""

from __future__ import annotations


class SearchError(Exception):
    """The domain error root for the search feature (REQ-010)."""


class UnknownSourceError(SearchError):
    """A query named a feature that is not registered (REQ-010, EDGE-001)."""

    def __init__(self, source: str) -> None:
        self.source = source
        super().__init__(f"unknown source: {source}")


class MalformedQueryError(SearchError):
    """A malformed query (REQ-010, AC-024).

    ``reason`` is one of ``invalid_limit`` / ``invalid_offset`` /
    ``invalid_operator`` / ``non_filterable_field`` / ``non_sortable_field`` /
    ``invalid_value_type``; ``field`` and ``source`` identify the field and the
    source the query was validated against (where applicable).
    """

    def __init__(self, reason: str, field: str | None = None, source: str | None = None) -> None:
        self.reason = reason
        self.field = field
        self.source = source
        message = f"malformed query: {reason}"
        if field is not None:
            message += f" (field: {field})"
        if source is not None:
            message += f" (source: {source})"
        super().__init__(message)


class SourceQueryFailedError(SearchError):
    """A source raising (or timing out) during a single-source query (REQ-010):
    the source, the reason (``query_failed``/``timeout``), and the error kind
    (no sensitive data)."""

    def __init__(self, source: str, reason: str, error: str) -> None:
        self.source = source
        self.reason = reason
        self.error = error
        super().__init__(f"source query failed: {source} ({reason}: {error})")
