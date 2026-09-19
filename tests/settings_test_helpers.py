"""Shared helpers for the settings test suite.

Kept separate from tests/conftest.py so test modules can import the helpers
without going through pytest's conftest machinery. Mirrors the event-bus
helper pattern (async delivery is observed via ``wait_for``).
"""

from __future__ import annotations

import time
from collections.abc import Callable, Iterator
from contextlib import contextmanager

from backend.eventbus import EventBus
from backend.settings import SettingsRegistry


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
    """
    import tempfile

    from backend.settings import YamlValueRepository
    from backend.settings import registry as _registry_module

    _registry_module.reset_settings_registry()
    isolated = SettingsRegistry(value_repository=YamlValueRepository(tempfile.mkdtemp()))
    _registry_module._registry[0] = isolated
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
    )
    from backend.settings import registry as _registry_module

    saved = get_settings_registry(required=False)
    reset_settings_registry()
    if install:
        _registry_module._registry[0] = SettingsRegistry(
            value_repository=YamlValueRepository(tempfile.mkdtemp())
        )
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
    ``install_isolated_registry()``.
    """
    from backend.settings import registry as _registry_module

    _registry_module.reset_settings_registry()
    if saved is not None:
        _registry_module._registry[0] = saved


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
