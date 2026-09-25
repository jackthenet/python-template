"""Property tests for the search feature's invariants (docs/specs/search.md).

One Hypothesis property test per invariant INV-001 .. INV-005. The strategies
match the spec's domain (registration sequences, query shapes, string free
text). The ``backend.search`` imports are deferred into the test bodies (and
the ``search_test_helpers`` builders) so the module collects cleanly before
the feature is implemented (RED).
"""

from __future__ import annotations

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st


@settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.too_slow])
@given(st.lists(st.sampled_from(["register", "unregister", "reset"]), min_size=1, max_size=20))
def test_inv_001_registration_idempotent_atomic(ops: list[str]) -> None:
    """INV-001: for any registration sequence, the registry state is a
    function of the last operation per name; identical re-registration is a
    no-op; a replace is atomic (no partial state)."""
    from search_test_helpers import EventCollector, demo_source, service

    collector = EventCollector()
    svc = service(event_bus=collector)
    expected = False  # is "demo" registered?
    for op in ops:
        if op == "register":
            svc.register_source(demo_source("demo"))
            expected = True
        elif op == "unregister":
            svc.unregister_source("demo")
            expected = False
        elif op == "reset":
            svc.reset()
            expected = False
    # The registry state is a function of the last operation per name.
    assert ("demo" in svc.list_sources()) == expected


@settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.too_slow])
@given(st.integers(min_value=0, max_value=10), st.integers(min_value=1, max_value=10))
def test_inv_002_query_deterministic(offset: int, limit: int) -> None:
    """INV-002: for any query and any source state, the result is
    deterministic — the same input + the same source state yields the same
    items, order, and total."""
    from search_test_helpers import demo_source, search_query, service

    svc = service()
    svc.register_source(demo_source("demo", n=10))
    q = search_query(feature="demo", offset=offset, limit=limit)
    r1 = svc.search(q)
    r2 = svc.search(q)
    assert r1.total == r2.total
    assert [it.item_id for it in r1.items] == [it.item_id for it in r2.items]
    assert [it.feature for it in r1.items] == [it.feature for it in r2.items]


@settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.too_slow])
@given(st.integers(min_value=0, max_value=20), st.integers(min_value=1, max_value=10))
def test_inv_003_pagination_consistency(offset: int, limit: int) -> None:
    """INV-003: for any query, ``len(items) <= limit``, ``total >= 0``, and an
    offset beyond the last match yields an empty item list (no error)."""
    from search_test_helpers import demo_source, search_query, service

    svc = service()
    svc.register_source(demo_source("demo", n=10))
    result = svc.search(search_query(feature="demo", offset=offset, limit=limit))
    assert len(result.items) <= limit
    assert result.total >= 0
    # An offset beyond the last match yields an empty item list.
    if offset >= result.total:
        assert result.items == []


@settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.too_slow])
@given(st.text(min_size=1, max_size=10))
def test_inv_004_normalization_invariance(text: str) -> None:
    """INV-004: for any string free text, the source's matching is invariant
    to the case and surrounding whitespace of the string value (case-folded +
    NFC + trimmed)."""
    from search_test_helpers import demo_source, search_query, service

    svc = service()
    svc.register_source(demo_source("demo", n=5))
    base = svc.search(search_query(feature="demo", free_text=text))
    upper = svc.search(search_query(feature="demo", free_text=text.upper()))
    padded = svc.search(search_query(feature="demo", free_text=f"  {text}  "))
    assert base.total == upper.total
    assert base.total == padded.total
    assert [it.item_id for it in base.items] == [it.item_id for it in upper.items]
    assert [it.item_id for it in base.items] == [it.item_id for it in padded.items]


@settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.too_slow])
@given(st.text(min_size=1, max_size=10))
def test_inv_005_no_secrets_in_outputs(text: str) -> None:
    """INV-005: for any operation output — published events, result items —
    the query text and source data never appear (only structural metadata)."""
    from search_test_helpers import EventCollector, demo_source, search_query, service

    collector = EventCollector()
    svc = service(event_bus=collector)
    svc.register_source(demo_source("demo", n=5))
    unique = f"SECRET-{text}"
    result = svc.search(search_query(feature="demo", free_text=unique))
    # The query text never appears in published events.
    for event in collector.events:
        assert unique not in str(event)
    # The query text never appears in the result items' display fields.
    for item in result.items:
        for value in item.fields.values():
            assert unique not in str(value)
