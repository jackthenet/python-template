"""Shared helpers for the settings test suite.

Kept separate from tests/conftest.py so test modules can import the helpers
without going through pytest's conftest machinery. Mirrors the event-bus
helper pattern (async delivery is observed via ``wait_for``).
"""

from __future__ import annotations

import threading
import time
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from typing import Any

from backend.eventbus import EventBus
from backend.settings import SettingChanged, SettingDefinition, SettingsRegistry


def wait_for(predicate: Callable[[], bool], timeout: float = 5.0) -> bool:
    """Poll until ``predicate()`` returns true, or until ``timeout`` elapses.

    The event bus delivers asynchronously on a background worker, so event
    tests wait for observable effects (handler invocations) rather than
    assuming synchronous delivery.
    """
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return True
        time.sleep(0.005)
    return False


def set_value_settled(registry: SettingsRegistry, key: str, value: Any, timeout: float = 5.0) -> Any:
    """``registry.set_value(key, value)`` with the resulting dispatch awaited.

    ``set_value`` publishes ``SettingChanged`` to the shared event bus, which
    dispatches it asynchronously on a background worker. A write whose dispatch
    is not awaited runs its handlers during whatever test happens to run next:
    a ``logging.*`` write reconfigures the logging feature's sinks (settings-coverage
    REQ-015 / AC-020), and that reconfigure's remove-then-add window transiently
    changes process-global state (the loguru handler set) inside an unrelated test.

    The wait is ordered, not timed. The bus dispatches one event to its handlers
    in subscription order on a single worker thread, and drains its queue FIFO, so
    a sentinel handler subscribed here — after every handler that can react to the
    write — is invoked for this event only once those handlers have returned. The
    sentinel matches this write's key **and** value, so a stale ``SettingChanged``
    for another key (or an earlier value of this one) cannot satisfy it, and FIFO
    order means every event queued before this one has also been dispatched. The
    timeout only bounds a hang; it is not part of the ordering argument.

    Applies to a registry publishing on the shared bus (the module singleton);
    a registry wired to its own ``EventBus`` has its own lifecycle. Raises
    ``AssertionError`` if the event is never dispatched.
    """
    bus: EventBus = registry._event_bus  # the registry exposes no public bus accessor
    dispatched = threading.Event()

    def _sentinel(event: SettingChanged) -> None:
        if event.key == key and event.value == value:
            dispatched.set()

    bus.subscribe(SettingChanged, _sentinel)
    try:
        result = registry.set_value(key, value)
        if not dispatched.wait(timeout):
            raise AssertionError(f"SettingChanged for {key!r} was never dispatched within {timeout}s")
        return result
    finally:
        bus.unsubscribe(SettingChanged, _sentinel)


def make_registry(event_bus: EventBus | None = None) -> tuple[SettingsRegistry, EventBus]:
    """Build a registry wired to ``event_bus`` (or a fresh bus) for a test.

    Returns ``(registry, bus)``. The caller is responsible for shutting the
    bus down when it created the bus (or always, to be safe).

    Uses an isolated value repository (temp directory) to prevent cross-test
    contamination from the shared default ``settings/`` directory.
    """
    import tempfile

    from backend.settings import YamlValueRepository

    bus = event_bus if event_bus is not None else EventBus()
    repo = YamlValueRepository(tempfile.mkdtemp(prefix="settings_values_"))
    registry = SettingsRegistry(event_bus=bus, value_repository=repo)
    return registry, bus


def install_isolated_registry() -> SettingsRegistry:
    """Install a fresh isolated registry into the module singleton.

    The registry is backed by a temp-dir value repository, so no value is ever
    persisted to the shared default ``settings/`` directory and nothing written
    by one test leaks into another (test isolation). Returns the installed
    registry.

    Preserves the current ``logging.*`` settings (definitions + values) so the
    logging feature's file sink keeps pointing at the session log file and the
    installed registry is in a consistent state (all ``logging.*`` settings
    registered, or none). Restoring only ``logging.log_file`` (the previous
    behavior) left a partial state: a test that then re-registered the logging
    settings (because ``logging.log_level`` was absent) hit a duplicate-key error
    on the already-restored ``logging.log_file``. Without preserving the
    ``logging.*`` settings, a test that installs a fresh isolated registry would
    trigger a sink re-configure that re-points the file sink to the default file,
    leaking state into later tests that assert on the session log file.
    """
    import tempfile

    from backend.settings import (
        YamlValueRepository,
        get_settings_registry,
        reset_settings_registry,
        set_settings_registry,
    )

    # The previous registry's logging.* definitions paired with their values.
    previous = get_settings_registry(required=False)
    logging_settings: list[tuple[SettingDefinition, Any]] = []
    if previous is not None:
        for view in previous.views():
            if view.key.startswith("logging."):
                logging_settings.append((previous.get_definition(view.key), previous.get_value(view.key)))

    reset_settings_registry()
    isolated = SettingsRegistry(value_repository=YamlValueRepository(tempfile.mkdtemp()))
    # set_value only accepts a registered key, so each definition precedes its value.
    for definition, value in logging_settings:
        isolated.register(definition)
        isolated.set_value(definition.key, value)
    set_settings_registry(isolated)
    return isolated


@contextmanager
def isolated_registry(install: bool = True) -> Iterator[None]:
    """Save the settings singleton, reset it, and restore it on exit (no leak).

    With ``install=True`` (the default) a fresh isolated registry (temp-dir
    value repository, as ``install_isolated_registry()`` installs) is put in
    the singleton slot for the duration of the block; with ``install=False``
    the singleton stays reset for the duration of the block. On exit the
    previously saved singleton object is restored into the module singleton
    slot (or the slot stays reset if there was no singleton) — the suite state
    after the block is exactly the state before it (no state leak).
    """
    import tempfile

    from backend.settings import (
        YamlValueRepository,
        get_settings_registry,
        reset_settings_registry,
        set_settings_registry,
    )

    saved = get_settings_registry(required=False)
    reset_settings_registry()
    if install:
        set_settings_registry(SettingsRegistry(value_repository=YamlValueRepository(tempfile.mkdtemp())))
    try:
        yield
    finally:
        restore_singleton(saved)


def restore_singleton(saved: SettingsRegistry | None) -> None:
    """Restore a previously saved singleton into the module singleton slot.

    Pairs with ``get_settings_registry(required=False)`` (the save). The slot
    is reset first, then the saved object is put back (or the slot stays
    reset if ``saved`` is None) — the suite state after the call is exactly
    the state before the save (no state leak). Uses the same mechanism as
    ``install_isolated_registry()``: the public install operation, which never
    accepts ``None`` (REQ-004), so an empty restore stays a plain reset.
    """
    from backend.settings import reset_settings_registry, set_settings_registry

    reset_settings_registry()
    if saved is not None:
        set_settings_registry(saved)


class EventCollector:
    """A synchronous event publisher for exact event counting in tests.

    Structurally satisfies the event publisher protocol (a ``publish`` method),
    so it can be injected as the registry's event bus. Events are recorded
    synchronously, making exact-count invariants (INV-008) deterministic.
    """

    def __init__(self) -> None:
        self.events: list[object] = []

    def publish(self, event: object) -> None:
        self.events.append(event)
