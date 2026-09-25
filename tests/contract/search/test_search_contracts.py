"""Contract tests for the search feature (docs/specs/search.md).

Covers the search feature's contract criteria: the backend-only API (AC-037)
and the NFRs — performance budgets (NFR-001), secret-freedom (NFR-002), the
public API contract (NFR-003), and the traced service + events (NFR-004).

The ``backend.search`` imports are deferred into the test bodies so the module
collects cleanly before the feature is implemented (RED).
"""

from __future__ import annotations

import importlib
import statistics
import time
from datetime import UTC, datetime
from pathlib import Path

from logging_coverage_test_helpers import entry_records, exit_records
from search_test_helpers import (
    EventCollector,
    demo_source,
    search_query,
    service,
)

_BASE = datetime(2024, 1, 1, tzinfo=UTC)

# NFR-001 performance budgets (median, including the @logged per-call overhead).
_REGISTER_BUDGET_S = 0.005  # 5 ms
_QUERY_BUDGET_S = 0.3  # ~300 ms (10k items; spec v2 — full Pydantic models via the repository ABC)

# The NFR-003 public API contract (spec Section 3, "Public API").
_EXPECTED_API = [
    # service + source
    "SearchService",
    "InMemorySource",
    "SearchSource",
    "SourceField",
    "SourceItem",
    "SourcePage",
    "SourceQueryContext",
    "FieldType",
    "FilterOperator",
    "FilterCondition",
    "FilterGroup",
    "Sort",
    "SearchQuery",
    "SearchResultItem",
    "SourceFailure",
    "SearchResult",
    # errors
    "SearchError",
    "UnknownSourceError",
    "MalformedQueryError",
    "SourceQueryFailedError",
    # events
    "SourceRegistered",
    "SourceUnregistered",
    "SourceQueryFailed",
    "EventPublisher",
    # module functions
    "register_settings",
    "register_actions",
    "get_search_service",
    "reset_search_service",
]


def _is_http_surface(obj: object) -> bool:
    """Whether ``obj`` is an HTTP/REST surface object (FastAPI/Starlette/Flask)."""
    cls = obj if isinstance(obj, type) else type(obj)
    mod = (getattr(cls, "__module__", "") or "").split(".")[0]
    return mod in {"fastapi", "starlette", "flask"}


def _event_text(event: object) -> str:
    """A string form of an event for the secret-freedom assertions."""
    dump = getattr(event, "model_dump", None)
    if callable(dump):
        try:
            return str(dump(mode="json"))
        except Exception:
            pass
    return str(event)


def test_ac_037_backend_only_api() -> None:
    """AC-037: the search feature's public API is an in-process service only
    (no HTTP/REST surface, no frontend dependency)."""
    module = importlib.import_module("backend.search")
    # No frontend dependency: the module lives under backend (not frontend).
    parts = Path(module.__file__).parts
    assert "backend" in parts
    assert "frontend" not in parts
    # No HTTP/REST surface: no public API object is a FastAPI/Starlette/Flask object.
    for name in dir(module):
        if name.startswith("_"):
            continue
        assert not _is_http_surface(getattr(module, name)), f"backend.search.{name} is an HTTP surface"


def test_nfr_001_performance_budgets() -> None:
    """NFR-001: a single-source query completes in < ~300 ms (median) for 10k
    items and ``register_source`` in < 5 ms (median), against a SQLite-backed
    source with 10k items (including the ``@logged`` per-call overhead).

    The ~300 ms budget reflects the current architecture (spec v2): the
    source's query path fetches full Pydantic models via the repository ABC
    and processes them in Python."""
    from backend.usermanagement import SqliteUserRepository, User, build_user_source

    # A SQLite-backed source with 10k items.
    repo = SqliteUserRepository("sqlite:///:memory:")
    for i in range(10_000):
        repo.add(
            User(
                username=f"user{i}",
                email=f"user{i}@example.com",
                display_name=f"User {i}",
                roles=["user"],
                password_hash="argon2id:fake",
                profile_picture_url=None,
                is_active=True,
                created_at=_BASE,
                updated_at=_BASE,
            )
        )
    source = build_user_source(repo)

    svc = service()
    svc.register_source(source)

    # register_source budget (< 5 ms median): the idempotent re-registration
    # path (same name + equal fields + same query function).
    reg_samples: list[float] = []
    for _ in range(15):
        start = time.monotonic()
        svc.register_source(source)
        reg_samples.append(time.monotonic() - start)
    assert statistics.median(reg_samples) < _REGISTER_BUDGET_S

    # Single-source query budget (< ~300 ms median for 10k items).
    query_samples: list[float] = []
    for _ in range(15):
        start = time.monotonic()
        svc.search(search_query(feature="usermanagement"))
        query_samples.append(time.monotonic() - start)
    assert statistics.median(query_samples) < _QUERY_BUDGET_S


def test_nfr_002_no_query_or_results_in_logs_events(log_records: list) -> None:
    """NFR-002: query text, result content, and source data never appear in log
    records or events (only structural metadata)."""
    collector = EventCollector()
    svc = service(event_bus=collector)
    svc.register_source(demo_source("demo"))
    unique_query = "UNIQUE-QUERY-SECRET-ABC-987"
    svc.search(search_query(feature="demo", free_text=unique_query))

    # Query text and result content never appear in log records.
    for rec in log_records:
        msg = str(rec)
        assert unique_query not in msg
        assert "item 0" not in msg  # result content (a demo item title)

    # Query text and result content never appear in events.
    for event in collector.events:
        text = _event_text(event)
        assert unique_query not in text
        assert "item 0" not in text


def test_nfr_003_public_api_contract() -> None:
    """NFR-003: the public API of ``backend.search`` is the recorded contract.

    Recorded deviation: the user explicitly deviated from the repository's
    additive-only NFR pattern for this feature — breaking changes are permitted
    and do not require a spec amendment (Q-124).
    """
    module = importlib.import_module("backend.search")
    for name in _EXPECTED_API:
        assert hasattr(module, name), f"backend.search.{name} is missing"


def test_nfr_004_traced_service_events(log_records: list) -> None:
    """NFR-004: service methods are traced via the shared logging feature
    (``@logged_class``, ``include_args=False``); source lifecycle and failure
    events are published to the injected publisher; no per-query events."""
    from backend.search import SourceRegistered, SourceUnregistered

    collector = EventCollector()
    svc = service(event_bus=collector)
    svc.register_source(demo_source("demo"))
    assert len(collector.of_type(SourceRegistered)) == 1
    # A successful search publishes NO per-query event.
    before = len(collector.events)
    svc.search(search_query(feature="demo"))
    assert len(collector.events) == before  # no per-query event
    svc.unregister_source("demo")
    assert len(collector.of_type(SourceUnregistered)) == 1
    # Tracing occurred via @logged_class.
    assert entry_records(log_records) or exit_records(log_records)
