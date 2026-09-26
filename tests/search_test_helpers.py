"""Shared helpers for the search test suite (docs/specs/search.md).

Mirrors the house feature-helper pattern: a synchronous event collector, a
fresh isolated settings registry, cross-platform SQLite file URL
construction, and builders for the search public API (source doubles, query
models, the service). Every ``backend.search`` import is deferred into the
builder functions so the RED state (module missing) surfaces as a per-test
error rather than a file-level collection error (house pattern, see
``tests/conftest.py`` and ``tests/sessionmanagement_test_helpers.py``).

Import top-level, like the other ``*_test_helpers`` modules (``tests/`` is on
``sys.path``).
"""

from __future__ import annotations

import tempfile
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

# A fixed in-domain base moment for the demo source's datetime values.
_BASE = datetime(2024, 1, 1, tzinfo=UTC)


class EventCollector:
    """A synchronous ``EventPublisher`` that collects published events.

    The spec's event ACs are phrased as "Given a publisher that collects
    events", so a synchronous collector (not the async event bus) gives
    deterministic assertions.
    """

    def __init__(self) -> None:
        self.events: list[Any] = []

    def publish(self, event: object) -> None:
        self.events.append(event)

    def of_type(self, event_type: type) -> list[Any]:
        return [e for e in self.events if isinstance(e, event_type)]


def db_url(tmp_path: Path, name: str = "search.db") -> str:
    """A cross-platform absolute SQLite file URL under ``tmp_path``.

    POSIX absolute paths need four slashes (``sqlite:////abs``); Windows
    paths (``C:/...``) are already absolute and use three.
    """
    p = str(tmp_path / name).replace("\\", "/")
    prefix = "sqlite:////" if p.startswith("/") else "sqlite:///"
    return f"{prefix}{p}"


def fresh_registry() -> Any:
    """A fresh isolated settings registry (temp-dir value repository).

    No value is ever persisted to the shared default ``settings/`` directory
    and nothing written by one test leaks into another (test isolation).
    """
    from backend.settings import SettingsRegistry, YamlValueRepository

    return SettingsRegistry(value_repository=YamlValueRepository(tempfile.mkdtemp()))


# --- Source doubles (backend.search deferred) -----------------------------


def demo_fields() -> list[Any]:
    """The demo source's declared fields (spanning the closed field-type set).

    ``title``/``tag`` are strings (``tag`` is nullable), ``count`` is a number,
    ``active`` is a boolean, and ``created`` is a datetime. All are
    filterable/display; all but ``tag`` are also searchable/sortable.
    """
    from backend.search import FieldType, SourceField

    return [
        SourceField(name="title", type=FieldType.STRING, searchable=True, filterable=True, sortable=True, display=True),
        SourceField(name="count", type=FieldType.NUMBER, filterable=True, sortable=True, display=True),
        SourceField(name="active", type=FieldType.BOOLEAN, filterable=True, sortable=True, display=True),
        SourceField(name="created", type=FieldType.DATETIME, filterable=True, sortable=True, display=True),
        SourceField(name="tag", type=FieldType.STRING, filterable=True, display=True),
    ]


def demo_items(n: int) -> list[Any]:
    """``n`` in-domain demo items (display-field values only).

    Deterministic per index: a searchable title (``"item {i}"``), a number
    (``i``), a boolean (``i % 2 == 0``), a datetime (base + ``i`` seconds),
    and a nullable tag (``None`` for every third item, for the ``is_null``
    cases).
    """
    from backend.search import SourceItem

    items: list[Any] = []
    for i in range(n):
        items.append(
            SourceItem(
                item_id=str(i),
                fields={
                    "title": f"item {i}",
                    "count": i,
                    "active": i % 2 == 0,
                    "created": _BASE + timedelta(seconds=i),
                    "tag": None if i % 3 == 0 else f"tag{i}",
                },
            )
        )
    return items


def demo_source(name: str = "demo", n: int = 5) -> Any:
    """A public in-memory source with ``n`` demo items (the spec's test double).

    The default ordering is the items' insertion order (``item 0`` ..
    ``item {n-1}``).
    """
    from backend.search import InMemorySource

    return InMemorySource(name=name, fields=demo_fields(), items=demo_items(n)).to_source()


def failing_source(name: str = "failing") -> Any:
    """A source whose query function always raises (failure-marker cases)."""
    from backend.search import FieldType, SearchSource, SourceField

    def query(ctx: Any) -> Any:
        raise RuntimeError("injected source failure")

    return SearchSource(
        name=name,
        fields=[
            SourceField(name="title", type=FieldType.STRING, searchable=True, filterable=True, sortable=True, display=True),
        ],
        query=query,
    )


def slow_source(name: str = "slow", sleep_s: float = 0.5) -> Any:
    """A source whose query function sleeps ``sleep_s`` seconds (timeout cases)."""
    import time

    from backend.search import FieldType, SearchSource, SourceField, SourcePage

    def query(ctx: Any) -> Any:
        time.sleep(sleep_s)
        return SourcePage(items=[], total=0)

    return SearchSource(
        name=name,
        fields=[
            SourceField(name="title", type=FieldType.STRING, searchable=True, filterable=True, sortable=True, display=True),
        ],
        query=query,
    )


# --- Query models (backend.search deferred) -------------------------------


def search_query(**kwargs: Any) -> Any:
    """A ``SearchQuery`` from keyword fields (``free_text``, ``filters``,
    ``feature``, ``offset``, ``limit``, ``sort``)."""
    from backend.search import SearchQuery

    return SearchQuery(**kwargs)


def filter_condition(field: str, operator: Any, value: Any = None) -> Any:
    """A ``FilterCondition``; ``operator`` may be a ``FilterOperator`` or its value."""
    from backend.search import FilterCondition, FilterOperator

    if not isinstance(operator, FilterOperator):
        operator = FilterOperator(operator)
    return FilterCondition(field=field, operator=operator, value=value)


def filter_group(operator: str, conditions: list[Any]) -> Any:
    """A ``FilterGroup`` (``"and"``/``"or"``) over ``conditions``."""
    from backend.search import FilterGroup

    return FilterGroup(operator=operator, conditions=conditions)


def sort(field: str, direction: str = "asc") -> Any:
    """A ``Sort`` (``"asc"``/``"desc"``) on ``field``."""
    from backend.search import Sort

    return Sort(field=field, direction=direction)


# --- Service (backend.search deferred) ------------------------------------


def service(event_bus: Any = None, settings_registry: Any = None, permission_service: Any = None) -> Any:
    """A fresh ``SearchService`` (an isolated settings registry by default)."""
    from backend.search import SearchService

    if settings_registry is None:
        settings_registry = fresh_registry()
    return SearchService(
        event_bus=event_bus,
        settings_registry=settings_registry,
        permission_service=permission_service,
    )
