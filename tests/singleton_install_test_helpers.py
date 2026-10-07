"""Shared helpers for the singleton install witnesses (settings-public-registry-setter).

Two things live here because more than one test category needs them:

* ``SLOTS`` — the table the parametrized witnesses run over: one entry per
  singleton-owning feature, holding its public-API module, the names of its
  ``set_*`` / ``get_*`` / ``reset_*`` trio, and a factory for a fresh, isolated
  instance. T-001 adds the settings entry; T-002 (eventbus), T-003
  (permissions), T-004 (search) and T-005 (sessionmanagement) append their own
  entry here, so no earlier task's tests change when a feature joins the table.
* ``widened_lazy_create_window`` — makes the owning module's lazy-create race
  observable (EDGE-033, AC-042, event-bus EDGE-012) instead of leaving it to
  the scheduler.
* ``concurrent_reads`` — the same slot read from N barrier-released threads, so
  a concurrency AC (AC-042, ``event-bus.md`` AC-015, ...) is witnessed against
  a simultaneous release rather than against the scheduler's ordering.
* ``non_tracing_warnings`` — counts the replace WARNING (REQ-002) without
  counting the tracing decorator's own records.

The trio is resolved by attribute name at call time, never imported: a feature
whose install operation does not exist yet then fails **inside** the test with
an ``AttributeError`` naming the missing public function — the RED signal for
the absent behaviour — instead of failing at import and taking every other test
in the file down with it.
"""

from __future__ import annotations

import tempfile
import threading
import time
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from types import ModuleType
from typing import Any, NamedTuple

import pytest

import backend.eventbus
import backend.permissions
import backend.search
import backend.settings
from backend.eventbus import EventBus
from backend.permissions import (
    MemoryGrantRepository,
    MemoryRoleRepository,
    MemorySystemPrincipalRepository,
    PermissionService,
)
from backend.search import SearchService
from backend.settings import SettingsRegistry, YamlValueRepository
from backend.usermanagement import SqliteUserRepository, UserManager

# The tracing decorator's own record prefixes (entry / exit / exception). A slow
# traced call escalates its exit record to WARNING, so a WARNING count that has
# to see the replace record has to exclude them.
_TRACING_PREFIXES = (">>", "<<", "!!")


class SingletonSlot(NamedTuple):
    """One singleton-owning feature: its public module, its trio, and a fresh instance."""

    module: ModuleType
    installer: str
    getter: str
    reset: str
    factory: Callable[[], Any]

    def install(self, instance: Any) -> Any:
        """Call the feature's public install operation (``AttributeError`` until it exists)."""
        return getattr(self.module, self.installer)(instance)

    def read(self, *args: Any) -> Any:
        """Call the feature's public getter (``args`` for a getter that needs them)."""
        return getattr(self.module, self.getter)(*args)

    def clear(self) -> None:
        """Call the feature's public reset operation."""
        getattr(self.module, self.reset)()

    def new(self) -> Any:
        """Build a fresh, isolated instance of the feature's singleton class."""
        return self.factory()


def _new_settings_registry() -> SettingsRegistry:
    """A settings registry with an isolated (temp-dir) value repository."""
    return SettingsRegistry(value_repository=YamlValueRepository(tempfile.mkdtemp(prefix="singleton_values_")))


SETTINGS_SLOT = SingletonSlot(
    module=backend.settings,
    installer="set_settings_registry",
    getter="get_settings_registry",
    reset="reset_settings_registry",
    factory=_new_settings_registry,
)

EVENTBUS_SLOT = SingletonSlot(
    module=backend.eventbus,
    installer="set_event_bus",
    getter="get_event_bus",
    reset="reset_event_bus",
    factory=EventBus,
)


def _new_permission_service() -> PermissionService:
    """A permission service over in-memory repositories (user-roles-permissions.md REQ-023)."""
    return PermissionService(
        MemoryRoleRepository(),
        MemoryGrantRepository(),
        MemorySystemPrincipalRepository(),
        UserManager(SqliteUserRepository("sqlite:///:memory:")),
    )


PERMISSIONS_SLOT = SingletonSlot(
    module=backend.permissions,
    installer="set_permission_service",
    getter="get_permission_service",
    reset="reset_permission_service",
    factory=_new_permission_service,
)


def _new_search_service() -> SearchService:
    """A search service over an isolated (temp-dir) settings registry (search.md REQ-013).

    Its source registry is per-instance by construction, so a fresh instance is also
    an isolated source registry (search.md AC-038); nothing is shared with the
    composition root's service and its three feature sources.
    """
    return SearchService(settings_registry=_new_settings_registry())


SEARCH_SLOT = SingletonSlot(
    module=backend.search,
    installer="set_search_service",
    getter="get_search_service",
    reset="reset_search_service",
    factory=_new_search_service,
)

# One entry per singleton-owning feature (settings-public-registry-setter REQ-001).
# settings at T-001, eventbus at T-002, permissions at T-003, search at T-004;
# T-005 (sessionmanagement) appends its entry here.
SLOTS: tuple[SingletonSlot, ...] = (SETTINGS_SLOT, EVENTBUS_SLOT, PERMISSIONS_SLOT, SEARCH_SLOT)


class _CreateWindow:
    """What a widened lazy-create window observed."""

    def __init__(self) -> None:
        self.creating = threading.Event()  # set once a create has built its instance
        self.instances: list[Any] = []  # every instance built while the window was open


@contextmanager
def widened_lazy_create_window(
    monkeypatch: pytest.MonkeyPatch, cls: type, hold_seconds: float = 0.05
) -> Iterator[_CreateWindow]:
    """Hold a creating thread inside ``cls.__init__`` so a second reader can race it.

    The unguarded lazy path reads the slot, builds a default and writes it back;
    under the GIL that window is microseconds wide, so a plain two-thread test
    passes whether or not the module lock exists. Holding the creating thread
    inside its constructor (after the instance is built, before the slot write)
    makes the difference observable and deterministic: with the module lock the
    second reader blocks and receives the first instance; without it both create.
    """
    window = _CreateWindow()
    real_init = cls.__init__

    def _slow_init(self: Any, *args: Any, **kwargs: Any) -> None:
        real_init(self, *args, **kwargs)
        window.instances.append(self)
        window.creating.set()
        time.sleep(hold_seconds)

    monkeypatch.setattr(cls, "__init__", _slow_init)
    try:
        yield window
    finally:
        window.creating.set()  # never leave a waiter blocked on a create that failed


def concurrent_reads(slot: SingletonSlot, count: int, args: tuple[Any, ...] = (), timeout: float = 5.0) -> list[Any]:
    """``slot.read(*args)`` from ``count`` threads released by one barrier.

    ``args`` is for a getter that needs them (session-management's takes a
    ``repository``). Every thread's exception is collected, so a concurrency
    witness fails on the behaviour instead of losing a thread silently.
    """
    start = threading.Barrier(count)
    results: list[Any] = []
    errors: list[BaseException] = []
    guard = threading.Lock()

    def _reader() -> None:
        try:
            start.wait(timeout=timeout)
            value = slot.read(*args)
        except BaseException as exc:  # reported through the assertion below
            with guard:
                errors.append(exc)
            return
        with guard:
            results.append(value)

    threads = [threading.Thread(target=_reader) for _ in range(count)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert not errors, f"reader threads raised: {errors!r}"
    assert len(results) == count, f"only {len(results)} of {count} readers completed"
    return results


def non_tracing_warnings(records: list[Any]) -> list[Any]:
    """Captured WARNING records that are not the tracing decorator's own output."""
    return [r for r in records if r["level"].name == "WARNING" and not str(r).startswith(_TRACING_PREFIXES)]
