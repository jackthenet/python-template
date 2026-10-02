"""Acceptance tests for the search feature (docs/specs/search.md).

One test function per acceptance criterion AC-001 .. AC-033 (the search
feature's own criteria; the feature-source criteria AC-034 .. AC-036 live in
``test_feature_sources.py``). These tests verify externally observable
behavior only: the registration lifecycle, the query entry point (free text,
filters, sorting, pagination, result shape), the error hierarchy, the
resilient global fan-out, normalization, settings, events, tracing,
permission enforcement, the per-source timeout, and the module singleton.

The ``backend.search`` imports are deferred into the test bodies (and the
``search_test_helpers`` builders) so the module collects cleanly before the
feature is implemented (RED).
"""

from __future__ import annotations

import pytest
from logging_coverage_test_helpers import entry_records, exit_records
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

# Settings defaults (spec REQ-013).
_DEFAULT_PAGE_SIZE = 100
_MAX_PAGE_SIZE = 1000
_SOURCE_TIMEOUT_MS = 5000

# --- AC-001 .. AC-005, AC-007, AC-008: registration + free text (T-001) ---


def test_ac_001_register_source() -> None:
    """AC-001: register a source; ``list_sources`` includes it; it is queryable."""
    svc = service()
    n = 5
    svc.register_source(demo_source("demo", n=n))
    assert svc.list_sources() == ["demo"]
    result = svc.search(search_query(feature="demo"))
    assert result.total == n
    assert len(result.items) == n


def test_ac_002_replace_same_name() -> None:
    """AC-002: re-registration with the same name replaces; the new source's
    query function is used; ``SourceRegistered`` is published."""
    from backend.search import SourceRegistered

    collector = EventCollector()
    svc = service(event_bus=collector)
    n_old = 5
    n_new = 3
    svc.register_source(demo_source("demo", n=n_old))
    svc.register_source(demo_source("demo", n=n_new))  # replace (different items)
    result = svc.search(search_query(feature="demo"))
    assert result.total == n_new  # the new source's query function is used
    n_registered = 2  # register + replace
    assert len(collector.of_type(SourceRegistered)) == n_registered


def test_ac_003_identical_reregistration_noop() -> None:
    """AC-003: identical re-registration (same object) is a no-op (no event)."""
    from backend.search import SourceRegistered

    collector = EventCollector()
    svc = service(event_bus=collector)
    src = demo_source("demo")
    svc.register_source(src)
    svc.register_source(src)  # identical (same name + equal fields + same query function)
    assert len(collector.of_type(SourceRegistered)) == 1  # no-op, no second event
    assert svc.list_sources() == ["demo"]


def test_ac_004_unregister_source() -> None:
    """AC-004: unregister removes the source; ``SourceUnregistered`` is
    published; a subsequent query raises ``UnknownSourceError``."""
    from backend.search import SourceUnregistered, UnknownSourceError

    collector = EventCollector()
    svc = service(event_bus=collector)
    svc.register_source(demo_source("demo"))
    svc.unregister_source("demo")
    assert "demo" not in svc.list_sources()
    assert len(collector.of_type(SourceUnregistered)) == 1
    with pytest.raises(UnknownSourceError):
        svc.search(search_query(feature="demo"))


def test_ac_005_search_free_text_returns_items() -> None:
    """AC-005: a free-text search returns ``SearchResultItem``s for the
    matching items, with page metadata set."""
    svc = service()
    n = 5
    svc.register_source(demo_source("demo", n=n))
    result = svc.search(search_query(feature="demo", free_text="item"))
    # All 5 demo items have "item" in the title.
    assert result.total == n
    for it in result.items:
        assert it.feature == "demo"
        assert it.item_id is not None
        assert "title" in it.fields
    # Page metadata.
    assert result.offset == 0
    assert result.limit >= 1


def test_ac_007_no_constraints_match_all() -> None:
    """AC-007: no free text + no filters = match all (total == N)."""
    svc = service()
    n = 7
    svc.register_source(demo_source("demo", n=n))
    result = svc.search(search_query(feature="demo"))
    assert result.total == n


def test_ac_008_empty_free_text_no_constraint() -> None:
    """AC-008: ``free_text=""`` equals ``free_text=None`` (no constraint)."""
    svc = service()
    n = 4
    svc.register_source(demo_source("demo", n=n))
    r_empty = svc.search(search_query(feature="demo", free_text=""))
    r_none = svc.search(search_query(feature="demo"))
    assert r_empty.total == r_none.total == n
    assert [it.item_id for it in r_empty.items] == [it.item_id for it in r_none.items]


# --- AC-006, AC-025 .. AC-026, AC-028 .. AC-031, AC-033: fan-out + cross-cutting (T-003) ---


def test_ac_006_global_fanout_combined_pagination() -> None:
    """AC-006: a query without ``feature`` fans out to all sources; the
    combined page concatenates the per-source pages in registration order;
    ``total`` is the sum of the per-source totals."""
    svc = service()
    n_alpha = 3
    n_beta = 2
    svc.register_source(demo_source("alpha", n=n_alpha))
    svc.register_source(demo_source("beta", n=n_beta))
    result = svc.search(search_query())  # no feature = global fan-out
    assert result.total == n_alpha + n_beta  # sum of the per-source totals
    features = [it.feature for it in result.items]
    # alpha's items first (registration order), then beta's.
    assert features[:n_alpha] == ["alpha"] * n_alpha
    assert features[n_alpha:] == ["beta"] * n_beta


def test_ac_026_single_source_failure_error() -> None:
    """AC-026: a source raising during a single-source query raises
    ``SourceQueryFailedError`` (source + reason + error kind)."""
    from backend.search import SourceQueryFailedError

    svc = service()
    svc.register_source(failing_source("failing"))
    with pytest.raises(SourceQueryFailedError) as exc_info:
        svc.search(search_query(feature="failing"))
    assert exc_info.value.source == "failing"
    assert exc_info.value.reason == "query_failed"


def test_ac_028_register_settings_live_read() -> None:
    """AC-028: ``register_settings`` registers the three keys with defaults
    100/1000/5000; changing a key changes the behavior on the next operation
    (live read)."""
    from backend.search import register_settings

    reg = fresh_registry()
    register_settings(reg)
    assert reg.get_value("search.default_page_size") == _DEFAULT_PAGE_SIZE
    assert reg.get_value("search.max_page_size") == _MAX_PAGE_SIZE
    assert reg.get_value("search.source_timeout") == _SOURCE_TIMEOUT_MS
    # Changing a key changes the behavior on the next operation (live read).
    small_page = 2
    reg.set_value("search.default_page_size", small_page)
    svc = service(settings_registry=reg)
    n = 5
    svc.register_source(demo_source("demo", n=n))
    result = svc.search(search_query(feature="demo"))
    assert len(result.items) == small_page  # live read of the changed default page size


def test_ac_029_lifecycle_and_failure_events() -> None:
    """AC-029: ``SourceRegistered``/``SourceUnregistered``/``SourceQueryFailed``
    are published respectively; NO per-query event is published."""
    from backend.search import SourceQueryFailed, SourceRegistered, SourceUnregistered

    collector = EventCollector()
    svc = service(event_bus=collector)
    # Register → SourceRegistered.
    svc.register_source(demo_source("demo"))
    assert len(collector.of_type(SourceRegistered)) == 1
    # A successful search publishes NO per-query event.
    before = len(collector.events)
    svc.search(search_query(feature="demo"))
    assert len(collector.events) == before  # no per-query event
    # Unregister → SourceUnregistered.
    svc.unregister_source("demo")
    assert len(collector.of_type(SourceUnregistered)) == 1
    # A source query failure → SourceQueryFailed.
    svc.register_source(failing_source("failing"))
    svc.search(search_query())  # global fan-out; "failing" raises
    assert len(collector.of_type(SourceQueryFailed)) == 1


def test_ac_030_traced_no_query_in_logs(log_records: list) -> None:
    """AC-030: entry/exit tracing occurs via ``@logged_class``; query text and
    result content never appear in log records."""
    svc = service()
    svc.register_source(demo_source("demo"))
    unique_query = "UNIQUE-QUERY-TEXT-XYZ-123"
    svc.search(search_query(feature="demo", free_text=unique_query))
    # Query text and result content never appear in log records.
    for rec in log_records:
        msg = str(rec)
        assert unique_query not in msg
        assert "item 0" not in msg  # result content (a demo item title)
    # Entry/exit tracing occurred via @logged_class.
    assert entry_records(log_records) or exit_records(log_records)


class _Denial(Exception):
    """A denial raised by the fake permission checker."""


class _FakePermissionChecker:
    """A structural ``PermissionChecker`` (spec D14) that records the checks it receives.

    ``require_permission`` raises ``_Denial`` on denial (the denial
    propagates); ``has_permission`` reports the decision.
    """

    def __init__(self, deny: bool) -> None:
        self.deny = deny
        self.calls: list[tuple] = []

    def require_permission(self, user_id, permission, session_token=None) -> None:
        self.calls.append((user_id, permission, session_token))
        if self.deny:
            raise _Denial("denied")

    def has_permission(self, user_id, permission, session_token=None) -> bool:
        return not self.deny


def test_ac_031_permission_enforcement() -> None:
    """AC-031: a denying checker's denial is raised and propagates (no result,
    no source queried); an allowing checker returns the result normally."""
    # Denying checker: the denial is raised and propagates.
    denying = _FakePermissionChecker(deny=True)
    svc = service(permission_service=denying)
    svc.register_source(demo_source("demo"))
    with pytest.raises(_Denial):
        svc.search(search_query(feature="demo"))
    # Allowing checker: the result is returned normally.
    allowing = _FakePermissionChecker(deny=False)
    svc2 = service(permission_service=allowing)
    n = 5
    svc2.register_source(demo_source("demo", n=n))
    result = svc2.search(search_query(feature="demo"))
    assert result.total == n


def test_ac_033_source_timeout() -> None:
    """AC-033: a source whose query exceeds the live ``search.source_timeout``
    → (single-source) a ``SourceQueryFailedError`` with reason ``timeout``."""
    from backend.search import SourceQueryFailedError, register_settings

    reg = fresh_registry()
    register_settings(reg)
    reg.set_value("search.source_timeout", 50)  # 50 ms
    svc = service(settings_registry=reg)
    svc.register_source(slow_source("slow", sleep_s=0.5))  # sleeps 500 ms > 50 ms
    with pytest.raises(SourceQueryFailedError) as exc_info:
        svc.search(search_query(feature="slow"))
    assert exc_info.value.reason == "timeout"


# --- AC-009 .. AC-024, AC-027: query semantics (T-002) ---


def test_ac_009_filter_equals() -> None:
    """AC-009: an ``equals`` filter returns only items whose field equals the
    value (case-insensitive)."""
    svc = service()
    svc.register_source(demo_source("demo"))
    result = svc.search(
        search_query(feature="demo", filters=filter_group("and", [filter_condition("title", "equals", "item 2")]))
    )
    assert result.total == 1
    assert result.items[0].fields["title"] == "item 2"


def test_ac_010_filter_contains_case_insensitive() -> None:
    """AC-010: a ``contains`` filter matches case-insensitively."""
    svc = service()
    n = 5
    svc.register_source(demo_source("demo", n=n))
    # "ITEM" (uppercase) matches titles "item 0".."item 4".
    result = svc.search(
        search_query(feature="demo", filters=filter_group("and", [filter_condition("title", "contains", "ITEM")]))
    )
    assert result.total == n


def test_ac_011_filter_and_group() -> None:
    """AC-011: an AND group returns only items satisfying both conditions."""
    svc = service()
    svc.register_source(demo_source("demo"))
    # Item 2: count=2, active=True (2 % 2 == 0).
    count_value = 2
    result = svc.search(
        search_query(
            feature="demo",
            filters=filter_group(
                "and", [filter_condition("count", "equals", count_value), filter_condition("active", "equals", True)]
            ),
        )
    )
    assert result.total == 1
    assert result.items[0].fields["count"] == count_value


def test_ac_012_filter_or_group() -> None:
    """AC-012: an OR group returns items satisfying either condition."""
    svc = service()
    svc.register_source(demo_source("demo"))
    # count == 0 OR count == 4 → items 0 and 4.
    result = svc.search(
        search_query(
            feature="demo",
            filters=filter_group(
                "or", [filter_condition("count", "equals", 0), filter_condition("count", "equals", 4)]
            ),
        )
    )
    n_matched = 2  # items 0 and 4
    assert result.total == n_matched


def test_ac_013_filter_number_comparisons() -> None:
    """AC-013: gt/gte/lt/lte filters on a number field."""
    svc = service()
    svc.register_source(demo_source("demo"))  # count 0..4
    r_gt = svc.search(search_query(feature="demo", filters=filter_group("and", [filter_condition("count", "gt", 2)])))
    n_gt = 2  # count 3, 4
    assert r_gt.total == n_gt
    r_gte = svc.search(
        search_query(feature="demo", filters=filter_group("and", [filter_condition("count", "gte", 2)]))
    )
    n_gte = 3  # count 2, 3, 4
    assert r_gte.total == n_gte
    r_lt = svc.search(search_query(feature="demo", filters=filter_group("and", [filter_condition("count", "lt", 2)])))
    n_lt = 2  # count 0, 1
    assert r_lt.total == n_lt
    r_lte = svc.search(
        search_query(feature="demo", filters=filter_group("and", [filter_condition("count", "lte", 2)]))
    )
    n_lte = 3  # count 0, 1, 2
    assert r_lte.total == n_lte


def test_ac_014_filter_in_list() -> None:
    """AC-014: an ``in_list`` filter returns items whose field value is in the list."""
    svc = service()
    svc.register_source(demo_source("demo"))
    result = svc.search(
        search_query(feature="demo", filters=filter_group("and", [filter_condition("count", "in_list", [1, 3])]))
    )
    n_matched = 2  # counts 1 and 3
    assert result.total == n_matched


def test_ac_015_filter_is_null() -> None:
    """AC-015: an ``is_null`` filter returns only items whose field is None."""
    svc = service()
    svc.register_source(demo_source("demo"))  # tag is None for i % 3 == 0 → items 0, 3
    result = svc.search(
        search_query(feature="demo", filters=filter_group("and", [filter_condition("tag", "is_null")]))
    )
    n_null = 2  # items 0, 3
    assert result.total == n_null
    assert all(it.fields["tag"] is None for it in result.items)


def test_ac_016_default_page_size() -> None:
    """AC-016: a search without ``limit`` returns at most
    ``search.default_page_size`` items; ``total`` reflects all matches."""
    from backend.search import register_settings

    reg = fresh_registry()
    register_settings(reg)
    page_size = 3
    reg.set_value("search.default_page_size", page_size)
    svc = service(settings_registry=reg)
    n = 5
    svc.register_source(demo_source("demo", n=n))
    result = svc.search(search_query(feature="demo"))  # no limit
    assert result.total == n  # total reflects all matches
    assert len(result.items) == page_size  # at most default_page_size


def test_ac_017_limit_clamped_to_max() -> None:
    """AC-017: ``limit > search.max_page_size`` is clamped to the cap (no error)."""
    from backend.search import register_settings

    reg = fresh_registry()
    register_settings(reg)
    cap = 2
    reg.set_value("search.max_page_size", cap)
    svc = service(settings_registry=reg)
    n = 5
    svc.register_source(demo_source("demo", n=n))
    result = svc.search(search_query(feature="demo", limit=10))  # limit > max
    assert len(result.items) == cap  # clamped to max_page_size
    assert result.total == n


def test_ac_018_offset_pagination() -> None:
    """AC-018: successive offsets skip correctly (no overlap, no gaps);
    ``total`` is unchanged across pages."""
    svc = service()
    n = 5
    svc.register_source(demo_source("demo", n=n))
    page_size = 2
    page0 = svc.search(search_query(feature="demo", offset=0, limit=page_size))
    page1 = svc.search(search_query(feature="demo", offset=page_size, limit=page_size))
    page2 = svc.search(search_query(feature="demo", offset=page_size * 2, limit=page_size))
    all_ids = [it.item_id for it in page0.items] + [it.item_id for it in page1.items] + [
        it.item_id for it in page2.items
    ]
    # No overlap, no gaps.
    assert len(set(all_ids)) == len(all_ids) == n
    assert page0.total == page1.total == page2.total == n


def test_ac_019_offset_beyond_end_empty() -> None:
    """AC-019: an offset beyond the last match returns an empty item list
    (no error); ``total == M``."""
    svc = service()
    n = 3
    svc.register_source(demo_source("demo", n=n))
    result = svc.search(search_query(feature="demo", offset=n, limit=5))
    assert result.items == []
    assert result.total == n


def test_ac_020_sort_overrides_default_order() -> None:
    """AC-020: a sort on a declared-sortable field overrides the source's
    default ordering."""
    svc = service()
    n = 5
    svc.register_source(demo_source("demo", n=n))
    # Default ordering is insertion order (0..4). Sort by count desc → 4,3,2,1,0.
    result = svc.search(search_query(feature="demo", sort=sort("count", "desc")))
    counts = [it.fields["count"] for it in result.items]
    assert counts == list(range(n - 1, -1, -1))


def test_ac_021_sort_stable_tie_break() -> None:
    """AC-021: ties on the sort field are broken stably by the source's
    default (insertion) ordering."""
    from backend.search import FieldType, InMemorySource, SourceField, SourceItem

    fields = [
        SourceField(name="title", type=FieldType.STRING, searchable=True, filterable=True, sortable=True, display=True),
        SourceField(name="count", type=FieldType.NUMBER, filterable=True, sortable=True, display=True),
    ]
    # Three items all tie on count=5; insertion order A, B, C.
    items = [
        SourceItem(item_id="a", fields={"title": "A", "count": 5}),
        SourceItem(item_id="b", fields={"title": "B", "count": 5}),
        SourceItem(item_id="c", fields={"title": "C", "count": 5}),
    ]
    src = InMemorySource(name="ties", fields=fields, items=items).to_source()
    svc = service()
    svc.register_source(src)
    result = svc.search(search_query(feature="ties", sort=sort("count", "asc")))
    assert [it.item_id for it in result.items] == ["a", "b", "c"]  # stable tie-break


def test_ac_022_result_item_shape() -> None:
    """AC-022: each result item = ``feature`` + ``item_id`` + the declared
    display field values; the caller can render without the source feature."""
    svc = service()
    svc.register_source(demo_source("demo", n=1))
    result = svc.search(search_query(feature="demo"))
    item = result.items[0]
    assert item.feature == "demo"
    assert item.item_id == "0"
    # Exactly the declared display fields.
    assert set(item.fields.keys()) == {"title", "count", "active", "created", "tag"}


def test_ac_024_malformed_query_errors() -> None:
    """AC-024: malformed queries raise ``MalformedQueryError`` identifying the
    reason (and the field/source where applicable)."""
    from backend.search import (
        FieldType,
        InMemorySource,
        MalformedQueryError,
        SourceField,
        SourceItem,
    )

    svc = service()
    svc.register_source(demo_source("demo"))
    # limit < 1
    with pytest.raises(MalformedQueryError):
        svc.search(search_query(feature="demo", limit=0))
    # offset < 0
    with pytest.raises(MalformedQueryError):
        svc.search(search_query(feature="demo", offset=-1))
    # invalid operator for a field's type: contains on a number field
    with pytest.raises(MalformedQueryError):
        svc.search(
            search_query(feature="demo", filters=filter_group("and", [filter_condition("count", "contains", "x")]))
        )
    # value of the wrong type: a string value for a number field
    with pytest.raises(MalformedQueryError):
        svc.search(
            search_query(
                feature="demo", filters=filter_group("and", [filter_condition("count", "equals", "not-a-number")])
            )
        )
    # filter on a non-filterable field / sort on a non-sortable field:
    # a source with a field that is neither filterable nor sortable.
    fields = [
        SourceField(name="title", type=FieldType.STRING, searchable=True, filterable=False, sortable=False, display=True)
    ]
    src = InMemorySource(name="locked", fields=fields, items=[SourceItem(item_id="0", fields={"title": "x"})]).to_source()
    svc.register_source(src)
    with pytest.raises(MalformedQueryError):
        svc.search(
            search_query(feature="locked", filters=filter_group("and", [filter_condition("title", "equals", "x")]))
        )
    with pytest.raises(MalformedQueryError):
        svc.search(search_query(feature="locked", sort=sort("title")))


def test_ac_027_normalization_invariance() -> None:
    """AC-027: free text/filters differing only in case, surrounding
    whitespace, or Unicode normalization form yield an identical result."""
    svc = service()
    svc.register_source(demo_source("demo"))
    r1 = svc.search(search_query(feature="demo", free_text="item"))
    r2 = svc.search(search_query(feature="demo", free_text="  ITEM  "))  # case + whitespace
    assert r1.total == r2.total
    assert [it.item_id for it in r1.items] == [it.item_id for it in r2.items]


# --- AC-023, AC-032: errors + singleton (T-001) ---


def test_ac_023_unknown_feature_error() -> None:
    """AC-023: a query with an unknown feature raises ``UnknownSourceError``
    (a ``SearchError`` subclass, not ValueError)."""
    from backend.search import SearchError, UnknownSourceError

    svc = service()
    svc.register_source(demo_source("demo"))
    with pytest.raises(UnknownSourceError) as exc_info:
        svc.search(search_query(feature="unknown"))
    assert isinstance(exc_info.value, SearchError)
    assert not isinstance(exc_info.value, ValueError)


def test_ac_032_singleton_and_reset() -> None:
    """AC-032: ``get_search_service`` is a module singleton;
    ``reset_search_service`` clears it; ``SearchService.reset`` clears all
    registrations."""
    from backend.search import get_search_service, reset_search_service

    reset_search_service()  # ensure a clean singleton
    reg = fresh_registry()
    s1 = get_search_service(settings_registry=reg)
    s2 = get_search_service(settings_registry=reg)
    assert s1 is s2  # singleton
    # SearchService.reset() clears all registrations.
    s1.register_source(demo_source("demo"))
    assert "demo" in s1.list_sources()
    s1.reset()
    assert s1.list_sources() == []
    # reset_search_service() clears the singleton.
    reset_search_service()
    s3 = get_search_service(settings_registry=reg)
    assert s3 is not s1  # a new instance after reset
