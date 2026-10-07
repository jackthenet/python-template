"""Shared helpers for the singleton install witnesses (settings-public-registry-setter).

Two things live here because more than one test category needs them:

* ``SLOTS`` — the table the parametrized witnesses run over: one entry per
  singleton-owning feature, holding its public-API module, the names of its
  ``set_*`` / ``get_*`` / ``reset_*`` trio, and a factory for a fresh, isolated
  instance. T-001 adds the settings entry; T-002..T-005 append their own entry
  here, so no earlier task's tests change when a feature joins the table.
* ``widened_lazy_create_window`` — makes the owning module's lazy-create race
  observable (EDGE-033, AC-042) instead of leaving it to the scheduler.
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

import backend.settings
from backend.settings import SettingsRegistry, YamlValueRepository

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

# One entry per singleton-owning feature (settings-public-registry-setter REQ-001).
# Only settings exists at T-001; T-002 (eventbus), T-003 (permissions), T-004
# (search) and T-005 (sessionmanagement) append their entry here.
SLOTS: tuple[SingletonSlot, ...] = (SETTINGS_SLOT,)


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


def non_tracing_warnings(records: list[Any]) -> list[Any]:
    """Captured WARNING records that are not the tracing decorator's own output."""
    return [r for r in records if r["level"].name == "WARNING" and not str(r).startswith(_TRACING_PREFIXES)]
