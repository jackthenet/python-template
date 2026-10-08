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
* ``concurrent_installs`` / ``record_constructions`` — the two pieces the
  concurrency witnesses (change AC-010, EDGE-010, INV-001) need: N installs
  released by one barrier, and a list of every instance whose **constructor
  completed** inside a block, so "a read returned a half-written slot" is a
  checkable statement rather than a phrase.
* ``SingletonSlot.stamp`` / ``EventWatcher`` — the two pieces the cross-feature
  witnesses (change AC-005, AC-013, INV-002, INV-003) need on top of the trio:
  a way to mark one instance so a later read can tell it from every other
  instance of the same class, and a collector that sees every event published on
  every bus a witness touches. ``SingletonSlot.stamp_identity`` is the identity
  form of the same marking, for the witness whose claim is literally "that exact
  instance" (INV-003) rather than "still behaves as constructed" (AC-005).

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
from datetime import UTC, datetime
from types import ModuleType
from typing import Any, NamedTuple
from uuid import uuid4

import pytest
from eventbus_test_helpers import wait_for
from search_test_helpers import demo_source
from sessionmanagement_test_helpers import make_session

import backend.eventbus
import backend.permissions
import backend.search
import backend.sessionmanagement
import backend.settings
from backend.authentication.repository import SqliteSessionRepository
from backend.eventbus import EventBus
from backend.permissions import (
    MemoryGrantRepository,
    MemoryRoleRepository,
    MemorySystemPrincipalRepository,
    PermissionService,
)
from backend.search import SearchService
from backend.sessionmanagement import SessionService
from backend.settings import (
    SettingDefinition,
    SettingKind,
    SettingsNotFoundError,
    SettingsRegistry,
    YamlValueRepository,
)
from backend.usermanagement import SqliteUserRepository, UserManager

# The tracing decorator's own record prefixes (entry / exit / exception). A slow
# traced call escalates its exit record to WARNING, so a WARNING count that has
# to see the replace record has to exclude them.
_TRACING_PREFIXES = (">>", "<<", "!!")


# A probe recognizes the one instance a stamper marked (see ``SingletonSlot.stamp``).
Probe = Callable[[Any], bool]


def _recognizes(instance: Any) -> Probe:
    """A probe that is true for ``instance`` and for no other object (``stamp_identity``)."""
    return lambda candidate: candidate is instance


def _keep(instance: Any) -> None:
    """Dispose of nothing: a feature whose instance needs no teardown."""


def _no_reader_args() -> tuple[Any, ...]:
    """The arguments a feature's getter needs on a bare read: none, for four of the five."""
    return ()


class SingletonSlot(NamedTuple):
    """One singleton-owning feature: its public module, its trio, and a fresh instance."""

    module: ModuleType
    installer: str
    getter: str
    reset: str
    factory: Callable[[], Any]
    stamper: Callable[[], tuple[Any, Probe]]
    dispose: Callable[[Any], None] = _keep
    warning_keyword: str = ""
    reader_args: Callable[[], tuple[Any, ...]] = _no_reader_args

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

    def read_args(self) -> tuple[Any, ...]:
        """The arguments this feature's getter needs on a bare read.

        Session-management's default can only be created when a ``repository`` is
        supplied (``session-management.md`` EDGE-003), so its reads carry one; the
        other four getters take nothing. A witness calls this once per race so the
        same repository is shared by the racing reads.
        """
        return self.reader_args()

    def stamp(self) -> tuple[Any, Probe]:
        """Build a fresh instance carrying a marker only that instance has.

        Returns ``(instance, probe)`` where ``probe(candidate)`` is true exactly for
        the returned instance. Two instances of the same class are otherwise
        indistinguishable, so a cross-feature witness could not tell "the caller
        still gets the instance it was given" (change AC-005, INV-003) from "the
        install swapped it out". The marker is written and read through the
        instance's own public API only.

        The probe therefore also answers a **liveness** question — the bus probe
        publishes and waits for a dispatch — so it is only usable by a witness whose
        instance is never reset away. A ``reset_*()`` shuts its instance down by spec
        (``event-bus.md`` REQ-005, change EDGE-007), and after that the probe is false
        for a reason the witness does not claim. Use ``stamp_identity`` for a witness
        that quantifies over sequences containing resets.
        """
        return self.stamper()

    def stamp_identity(self) -> tuple[Any, Probe]:
        """Build a fresh instance and a probe recognizing exactly it, by identity.

        INV-003's wording is "keeps **that exact instance**", which is an identity
        question, not a liveness one: the invariant quantifies over install sequences
        that include ``reset_*()``, and a reset legitimately shuts the instance down
        (``event-bus.md`` REQ-005, change EDGE-007 — witnessed by ``test_edge_007``),
        after which the behavioral ``stamp()`` probe can never return True. The
        behavioral claim AC-005/EDGE-001 make ("still behaves as it was constructed")
        keeps ``stamp()``; their sequences never reset the held instance away.
        """
        instance = self.new()
        return instance, _recognizes(instance)

    def name(self) -> str:
        """The feature's short name, for assertion messages."""
        return self.module.__name__.removeprefix("backend.")


def _new_settings_registry() -> SettingsRegistry:
    """A settings registry with an isolated (temp-dir) value repository."""
    return SettingsRegistry(value_repository=YamlValueRepository(tempfile.mkdtemp(prefix="singleton_values_")))


def _stamp_settings() -> tuple[Any, Probe]:
    """A registry holding one uniquely valued TEXT setting; the probe reads the value back."""
    marker = f"stamp-{uuid4()}"
    registry = _new_settings_registry()
    registry.register(SettingDefinition(key="app.name", kind=SettingKind.TEXT, default=marker, category="app"))

    def probe(candidate: Any) -> bool:
        try:
            return candidate.get_value("app.name") == marker
        except SettingsNotFoundError:
            return False

    return registry, probe


SETTINGS_SLOT = SingletonSlot(
    module=backend.settings,
    installer="set_settings_registry",
    getter="get_settings_registry",
    reset="reset_settings_registry",
    factory=_new_settings_registry,
    stamper=_stamp_settings,
    warning_keyword="settings",
)


def _stamp_eventbus() -> tuple[Any, Probe]:
    """A bus subscribed for a private event class; the probe publishes that class and waits.

    The probe starts the bus's worker (publish is what starts it, event-bus.md
    EDGE-001), so a stamped bus has to be shut down by the witness — hence the
    slot's ``dispose``.
    """
    bus = EventBus()
    marker_event = type("StampedEvent", (), {})
    received: list[object] = []
    bus.subscribe(marker_event, received.append)

    def probe(candidate: Any) -> bool:
        received.clear()
        candidate.publish(marker_event())
        return wait_for(lambda: bool(received), timeout=1.0)

    return bus, probe


EVENTBUS_SLOT = SingletonSlot(
    module=backend.eventbus,
    installer="set_event_bus",
    getter="get_event_bus",
    reset="reset_event_bus",
    factory=EventBus,
    stamper=_stamp_eventbus,
    dispose=EventBus.shutdown,
    warning_keyword="bus",
)


def _new_permission_service() -> PermissionService:
    """A permission service over in-memory repositories (user-roles-permissions.md REQ-023)."""
    return PermissionService(
        MemoryRoleRepository(),
        MemoryGrantRepository(),
        MemorySystemPrincipalRepository(),
        UserManager(SqliteUserRepository("sqlite:///:memory:")),
    )


def _stamp_permissions() -> tuple[Any, Probe]:
    """A service with one runtime role of its own; the probe looks that role up.

    A role (not a grant) is the marker: a grant would need a catalog the isolated
    service does not carry (its default ``PermissionCatalog`` is empty).
    """
    service = _new_permission_service()
    role = f"stamp_{uuid4().hex[:16]}"  # user-roles-permissions.md: ^[a-z0-9_-]{1,32}$
    service.create_role(role)

    def probe(candidate: Any) -> bool:
        return any(declared.role == role for declared in candidate.list_roles())

    return service, probe


PERMISSIONS_SLOT = SingletonSlot(
    module=backend.permissions,
    installer="set_permission_service",
    getter="get_permission_service",
    reset="reset_permission_service",
    factory=_new_permission_service,
    stamper=_stamp_permissions,
    warning_keyword="permission",
)


def _new_search_service() -> SearchService:
    """A search service over an isolated (temp-dir) settings registry (search.md REQ-013).

    Its source registry is per-instance by construction, so a fresh instance is also
    an isolated source registry (search.md AC-038); nothing is shared with the
    composition root's service and its three feature sources.
    """
    return SearchService(settings_registry=_new_settings_registry())


def _stamp_search() -> tuple[Any, Probe]:
    """A service with one uniquely named source registered; the probe looks the name up."""
    service = _new_search_service()
    name = f"stamp_{uuid4().hex[:16]}"  # search.md source-name pattern
    service.register_source(demo_source(name))

    def probe(candidate: Any) -> bool:
        return name in candidate.list_sources()

    return service, probe


SEARCH_SLOT = SingletonSlot(
    module=backend.search,
    installer="set_search_service",
    getter="get_search_service",
    reset="reset_search_service",
    factory=_new_search_service,
    stamper=_stamp_search,
    warning_keyword="search",
)


def _new_session_service() -> SessionService:
    """A session service over an isolated in-memory session store and settings registry.

    ``SessionService`` has no default construction — its ``repository`` is a required
    constructor argument (``session-management.md`` EDGE-003) — so the factory supplies
    one, and every read of this slot in a concurrency witness has to pass a repository
    too (change REQ-008 / AC-012). The settings registry is the isolated temp-dir one,
    so the service's live setting reads never touch the shared ``settings/`` directory.
    """
    return SessionService(
        SqliteSessionRepository("sqlite:///:memory:"),
        settings_registry=_new_settings_registry(),
    )


def _stamp_sessionmanagement() -> tuple[Any, Probe]:
    """A service over a store holding one session row of its own; the probe lists that user's sessions.

    The service owns no state of its own — its observable state is its store — so the
    stamp builds the store and the service together (the slot's plain ``new()`` keeps
    its own private store, finding F-24).
    """
    repository = SqliteSessionRepository("sqlite:///:memory:")
    service = SessionService(repository, settings_registry=_new_settings_registry())
    owner = uuid4()
    make_session(repository, owner, created_at=datetime.now(UTC))

    def probe(candidate: Any) -> bool:
        return bool(candidate.list_sessions(user_id=owner))

    return service, probe


def _session_reader_args() -> tuple[Any, ...]:
    """A repository for the session-management getter (EDGE-003: no default without one)."""
    return (SqliteSessionRepository("sqlite:///:memory:"),)


SESSIONMANAGEMENT_SLOT = SingletonSlot(
    module=backend.sessionmanagement,
    installer="set_session_service",
    getter="get_session_service",
    reset="reset_session_service",
    factory=_new_session_service,
    stamper=_stamp_sessionmanagement,
    warning_keyword="session",
    reader_args=_session_reader_args,
)

# One entry per singleton-owning feature (settings-public-registry-setter REQ-001).
# settings at T-001, eventbus at T-002, permissions at T-003, search at T-004,
# sessionmanagement at T-005.
SLOTS: tuple[SingletonSlot, ...] = (
    SETTINGS_SLOT,
    EVENTBUS_SLOT,
    PERMISSIONS_SLOT,
    SEARCH_SLOT,
    SESSIONMANAGEMENT_SLOT,
)


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


def concurrent_installs(slot: SingletonSlot, instances: list[Any], timeout: float = 5.0) -> list[BaseException]:
    """``slot.install(instance)`` for every instance, each from its own barrier-released thread.

    Every thread's exception is returned instead of the thread dying silently, so the
    witness fails on the behaviour (EDGE-010: no install lost, no exception raised).
    """
    start = threading.Barrier(len(instances))
    errors: list[BaseException] = []
    guard = threading.Lock()

    def _installer(instance: Any) -> None:
        try:
            start.wait(timeout=timeout)
            slot.install(instance)
        except BaseException as exc:  # reported through the assertion in the witness
            with guard:
                errors.append(exc)

    threads = [threading.Thread(target=_installer, args=(instance,)) for instance in instances]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return errors


@contextmanager
def record_constructions(cls: type) -> Iterator[list[Any]]:
    """Every ``cls`` instance whose **constructor completed** inside the block.

    A slot read that returns an object absent from this list returned something written
    before its constructor finished — the half-written slot AC-010 forbids. Unlike
    ``widened_lazy_create_window`` this records without holding anyone inside the
    constructor, so it does not manufacture a race.
    """
    built: list[Any] = []
    real_init = cls.__init__

    def _recorded(self: Any, *args: Any, **kwargs: Any) -> None:
        real_init(self, *args, **kwargs)
        built.append(self)

    cls.__init__ = _recorded
    try:
        yield built
    finally:
        cls.__init__ = real_init


class EventWatcher:
    """Collect every event published on every bus a witness touches (change AC-013, INV-003).

    An install that published an event would publish it on the shared default bus —
    which, for the event bus feature itself, is the instance that was just installed,
    not the bus that was shared before. So the collector subscribes to **each** bus
    the witness creates, for ``object``: the bus matches handlers by ``isinstance``
    (event-bus.md AC-004), so an ``object`` subscription receives every event type.

    One subscription **per bus instance**: a witness re-reads the shared default after
    every reset, and only the event bus feature's reset recreates it, so the same live
    bus reaches ``watch`` repeatedly. A second identical subscription would deliver the
    witness's own sentinel twice, and an exact-list assertion would then read as an
    install having published an event.

    ``drain()`` shuts every watched bus down, and shutdown drains the queue
    (event-bus.md AC-008) — so "no event arrived" is a settled fact rather than a
    race against the worker.
    """

    def __init__(self) -> None:
        self.received: list[object] = []
        self._buses: list[Any] = []
        self._watched: set[int] = set()

    def watch(self, instance: Any) -> None:
        """Subscribe the collector to ``instance`` once, if it is a bus (has ``subscribe``).

        Keyed on ``id`` — two distinct buses must both be watched — and safe because
        ``_buses`` keeps every watched instance alive, so an id can never be recycled
        by a garbage-collected bus.
        """
        subscribe = getattr(instance, "subscribe", None)
        if callable(subscribe) and id(instance) not in self._watched:
            self._watched.add(id(instance))
            subscribe(object, self.received.append)
            self._buses.append(instance)

    def drain(self) -> None:
        """Shut every watched bus down so its queued events are delivered first."""
        for bus in self._buses:
            bus.shutdown()
