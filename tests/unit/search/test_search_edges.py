"""Unit tests for the search feature's edge cases (docs/specs/search.md).

One test function per edge case EDGE-001 .. EDGE-021 (the search feature's
own edge cases). These tests verify externally observable behavior only: the
error conditions, the resilient global fan-out, the per-source timeout, the
registration-lifecycle no-ops, the invalid source declaration, and the
concurrent register/query cases.

The ``backend.search`` imports are deferred into the test bodies (and the
``search_test_helpers`` builders) so the module collects cleanly before the
feature is implemented (RED).
"""

from __future__ import annotations

import threading

import pytest
from search_test_helpers import (
    EventCollector,
    demo_source,
    failing_source,
    filter_condition,
    filter_group,
    fresh_registry,
    search_query,
    service,
    slow_source,
    sort,
)


def test_edge_001_unknown_feature() -> None:
    """EDGE-001: ``search`` with ``feature`` naming an unregistered source
    raises ``UnknownSourceError``."""
    from backend.search import UnknownSourceError

    svc = service()
    svc.register_source(demo_source("demo"))
    with pytest.raises(UnknownSourceError):
        svc.search(search_query(feature="nope"))


def test_edge_002_global_no_sources_empty() -> None:
    """EDGE-002: a global search with no registered sources returns an empty
    result (total 0, no failures), no error."""
    svc = service()
    result = svc.search(search_query())  # no feature, no sources
    assert result.total == 0
    assert result.items == []
    assert result.failures == []


def test_edge_003_invalid_limit_offset() -> None:
    """EDGE-003: ``search`` with ``limit < 1`` or ``offset < 0`` raises
    ``MalformedQueryError``."""
    from backend.search import MalformedQueryError

    svc = service()
    svc.register_source(demo_source("demo"))
    with pytest.raises(MalformedQueryError):
        svc.search(search_query(feature="demo", limit=0))
    with pytest.raises(MalformedQueryError):
        svc.search(search_query(feature="demo", offset=-1))


def test_edge_004_non_filterable_field() -> None:
    """EDGE-004: a filter on a field the source did not declare filterable
    (or absent from the schema) raises ``MalformedQueryError`` (identifying
    the source + field)."""
    from backend.search import FieldType, InMemorySource, MalformedQueryError, SourceField, SourceItem

    svc = service()
    # A source with a field that is not filterable.
    fields = [SourceField(name="title", type=FieldType.STRING, searchable=True, filterable=False, display=True)]
    src = InMemorySource(name="locked", fields=fields, items=[SourceItem(item_id="0", fields={"title": "x"})]).to_source()
    svc.register_source(src)
    with pytest.raises(MalformedQueryError) as exc_info:
        svc.search(
            search_query(feature="locked", filters=filter_group("and", [filter_condition("title", "equals", "x")]))
        )
    # Identifying the source + field.
    assert exc_info.value.source == "locked"
    assert exc_info.value.field == "title"


def test_edge_005_invalid_operator_for_type() -> None:
    """EDGE-005: a filter operator invalid for the field's type (e.g.,
    ``contains`` on a number) raises ``MalformedQueryError``."""
    from backend.search import MalformedQueryError

    svc = service()
    svc.register_source(demo_source("demo"))  # count is a number
    with pytest.raises(MalformedQueryError):
        svc.search(
            search_query(feature="demo", filters=filter_group("and", [filter_condition("count", "contains", "x")]))
        )


def test_edge_006_non_sortable_field() -> None:
    """EDGE-006: a sort on a field the source did not declare sortable raises
    ``MalformedQueryError``."""
    from backend.search import FieldType, InMemorySource, MalformedQueryError, SourceField, SourceItem

    svc = service()
    # A source with a field that is not sortable.
    fields = [SourceField(name="title", type=FieldType.STRING, searchable=True, sortable=False, display=True)]
    src = InMemorySource(name="locked", fields=fields, items=[SourceItem(item_id="0", fields={"title": "x"})]).to_source()
    svc.register_source(src)
    with pytest.raises(MalformedQueryError):
        svc.search(search_query(feature="locked", sort=sort("title")))


def test_edge_007_limit_clamped() -> None:
    """EDGE-007: ``search`` with ``limit > search.max_page_size`` clamps the
    limit to the cap (no error)."""
    from backend.search import register_settings

    reg = fresh_registry()
    register_settings(reg)
    cap = 2
    reg.set_value("search.max_page_size", cap)
    svc = service(settings_registry=reg)
    n = 5
    svc.register_source(demo_source("demo", n=n))
    result = svc.search(search_query(feature="demo", limit=100))  # limit > max
    assert len(result.items) == cap  # clamped to the cap
    assert result.total == n


def test_edge_008_offset_beyond_end() -> None:
    """EDGE-008: an offset beyond the last match returns an empty item list,
    ``total`` unchanged, no error."""
    svc = service()
    n = 3
    svc.register_source(demo_source("demo", n=n))
    result = svc.search(search_query(feature="demo", offset=10, limit=5))
    assert result.items == []
    assert result.total == n


def test_edge_009_global_source_raises_partial() -> None:
    """EDGE-009: a source raising during a global search → partial results +
    a failure marker for the failing source (resilient)."""
    from backend.search import SourceFailure

    svc = service()
    svc.register_source(demo_source("ok", n=2))
    svc.register_source(failing_source("bad"))
    result = svc.search(search_query())  # global fan-out
    # The other source's results are returned.
    assert any(it.feature == "ok" for it in result.items)
    # A failure marker for the failing source.
    assert len(result.failures) == 1
    failure = result.failures[0]
    assert isinstance(failure, SourceFailure)
    assert failure.feature == "bad"
    assert failure.reason == "query_failed"


def test_edge_010_single_source_raises_error() -> None:
    """EDGE-010: a source raising during a single-source query raises
    ``SourceQueryFailedError``."""
    from backend.search import SourceQueryFailedError

    svc = service()
    svc.register_source(failing_source("bad"))
    with pytest.raises(SourceQueryFailedError):
        svc.search(search_query(feature="bad"))


def test_edge_011_source_timeout() -> None:
    """EDGE-011: a source query exceeding ``search.source_timeout`` → a
    failure marker with reason ``timeout`` (global) / ``SourceQueryFailedError``
    with reason ``timeout`` (single-source)."""
    from backend.search import SourceQueryFailedError, register_settings

    reg = fresh_registry()
    register_settings(reg)
    reg.set_value("search.source_timeout", 50)  # 50 ms
    svc = service(settings_registry=reg)
    svc.register_source(slow_source("slow", sleep_s=0.5))  # sleeps 500 ms > 50 ms
    # Single-source: SourceQueryFailedError with reason timeout.
    with pytest.raises(SourceQueryFailedError) as exc_info:
        svc.search(search_query(feature="slow"))
    assert exc_info.value.reason == "timeout"
    # Global: a failure marker with reason timeout.
    svc2 = service(settings_registry=reg)
    svc2.register_source(demo_source("ok", n=1))
    svc2.register_source(slow_source("slow", sleep_s=0.5))
    result = svc2.search(search_query())
    assert any(f.feature == "slow" and f.reason == "timeout" for f in result.failures)


def test_edge_012_no_searchable_fields_zero_matches() -> None:
    """EDGE-012: a source with no searchable fields + a non-empty free text
    contributes 0 matches (no error)."""
    from backend.search import FieldType, InMemorySource, SourceField, SourceItem

    svc = service()
    # A source with no searchable fields.
    fields = [SourceField(name="title", type=FieldType.STRING, searchable=False, filterable=False, display=True)]
    src = InMemorySource(
        name="nosearch", fields=fields, items=[SourceItem(item_id="0", fields={"title": "x"})]
    ).to_source()
    svc.register_source(src)
    result = svc.search(search_query(feature="nosearch", free_text="x"))
    assert result.total == 0
    assert result.items == []


def test_edge_013_unregister_unknown_noop() -> None:
    """EDGE-013: ``unregister_source`` with an unknown name is a no-op (no
    error, no event)."""
    from backend.search import SourceUnregistered

    collector = EventCollector()
    svc = service(event_bus=collector)
    svc.unregister_source("unknown")  # no-op
    assert svc.list_sources() == []
    assert len(collector.of_type(SourceUnregistered)) == 0


def test_edge_014_identical_reregistration_noop() -> None:
    """EDGE-014: ``register_source`` with an identical source (same name +
    equal fields + same query function) is a no-op (no error, no event)."""
    from backend.search import SourceRegistered

    collector = EventCollector()
    svc = service(event_bus=collector)
    src = demo_source("demo")
    svc.register_source(src)
    svc.register_source(src)  # identical
    assert len(collector.of_type(SourceRegistered)) == 1  # no-op, no second event


def test_edge_015_replace_concurrent_consistent() -> None:
    """EDGE-015: a replace is atomic — a concurrent query sees either the old
    or the new source (no partial state)."""
    svc = service()
    svc.register_source(demo_source("demo", n=5))
    errors: list[BaseException] = []

    def replace() -> None:
        try:
            svc.register_source(demo_source("demo", n=3))
        except BaseException as e:
            errors.append(e)

    t = threading.Thread(target=replace)
    t.start()
    # Query concurrently with the replace.
    for _ in range(50):
        try:
            result = svc.search(search_query(feature="demo"))
            assert result.total in (3, 5)  # either the old or the new source
        except BaseException as e:
            errors.append(e)
    t.join()
    assert errors == []  # no crash, no partial state


def test_edge_016_reset_clears_no_events() -> None:
    """EDGE-016: ``reset()`` with registered sources clears all registrations,
    no events."""
    from backend.search import SourceRegistered, SourceUnregistered

    collector = EventCollector()
    svc = service(event_bus=collector)
    svc.register_source(demo_source("demo"))
    svc.register_source(demo_source("other"))
    svc.reset()
    assert svc.list_sources() == []
    # No unregister events (reset publishes no events).
    assert len(collector.of_type(SourceUnregistered)) == 0
    # The register events from before are still there (reset is not a new event).
    n_registered = 2
    assert len(collector.of_type(SourceRegistered)) == n_registered


def test_edge_017_is_null_matches_none() -> None:
    """EDGE-017: a filter with ``is_null`` on a nullable field matches items
    where the field is None."""
    svc = service()
    svc.register_source(demo_source("demo"))  # tag is None for i % 3 == 0 → items 0, 3
    result = svc.search(
        search_query(feature="demo", filters=filter_group("and", [filter_condition("tag", "is_null")]))
    )
    n_null = 2  # items 0, 3
    assert result.total == n_null
    assert all(it.fields["tag"] is None for it in result.items)


def test_edge_018_in_list_empty_matches_nothing() -> None:
    """EDGE-018: an ``in_list`` filter with an empty list matches nothing."""
    svc = service()
    svc.register_source(demo_source("demo"))
    result = svc.search(
        search_query(feature="demo", filters=filter_group("and", [filter_condition("count", "in_list", [])]))
    )
    assert result.total == 0
    assert result.items == []


def test_edge_020_fanout_strict_validation() -> None:
    """EDGE-020: a global fan-out where a filter/sort is valid for some
    sources but references a field absent or non-filterable in another source
    in the fan-out raises ``MalformedQueryError`` (strict validation against
    every source in the fan-out)."""
    from backend.search import FieldType, InMemorySource, MalformedQueryError, SourceField, SourceItem

    svc = service()
    # Two sources: "a" has a filterable "title"; "b" does NOT.
    fields_a = [SourceField(name="title", type=FieldType.STRING, searchable=True, filterable=True, display=True)]
    fields_b = [SourceField(name="title", type=FieldType.STRING, searchable=True, filterable=False, display=True)]
    svc.register_source(
        InMemorySource(name="a", fields=fields_a, items=[SourceItem(item_id="0", fields={"title": "x"})]).to_source()
    )
    svc.register_source(
        InMemorySource(name="b", fields=fields_b, items=[SourceItem(item_id="0", fields={"title": "x"})]).to_source()
    )
    # A global filter on "title" is valid for "a" but not "b" → MalformedQueryError.
    with pytest.raises(MalformedQueryError):
        svc.search(search_query(filters=filter_group("and", [filter_condition("title", "equals", "x")])))


def test_edge_021_invalid_source_declaration() -> None:
    """EDGE-021: ``register_source`` with an invalid source declaration (name/
    field name not matching the patterns, duplicate field names, unknown field
    type) raises ``ValueError`` (argument-level)."""
    from backend.search import FieldType, InMemorySource, SourceField, SourceItem

    svc = service()
    valid_item = [SourceItem(item_id="0", fields={"title": "x"})]
    # A name not matching SOURCE_NAME_PATTERN (uppercase).
    with pytest.raises(ValueError):
        svc.register_source(
            InMemorySource(
                name="Demo",
                fields=[SourceField(name="title", type=FieldType.STRING, display=True)],
                items=valid_item,
            ).to_source()
        )
    # A field name not matching FIELD_NAME_PATTERN (uppercase).
    with pytest.raises(ValueError):
        svc.register_source(
            InMemorySource(
                name="demo",
                fields=[SourceField(name="Title", type=FieldType.STRING, display=True)],
                items=valid_item,
            ).to_source()
        )
    # Duplicate field names.
    with pytest.raises(ValueError):
        svc.register_source(
            InMemorySource(
                name="demo",
                fields=[
                    SourceField(name="title", type=FieldType.STRING, display=True),
                    SourceField(name="title", type=FieldType.STRING, display=True),
                ],
                items=valid_item,
            ).to_source()
        )
