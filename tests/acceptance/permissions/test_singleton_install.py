"""Acceptance tests for the permissions shared-default install operation.

Normative basis: ``docs/specs/user-roles-permissions.md`` v2 REQ-030 and
AC-041 .. AC-044 (change ``settings-public-registry-setter``, CROSS-CUTTING).
Externally observable behavior only: installing a service makes it the shared
default, replacing a held default logs exactly one WARNING, one module lock
keeps install / lazy create / reset mutually exclusive, and install-then-reset
yields a freshly created default.

The ``set_*`` / ``get_*`` / ``reset_*`` trio is reached through
``PERMISSIONS_SLOT``, which resolves the three names by attribute at call time.
That is what keeps the RED signal inside the test body (``AttributeError:
module 'backend.permissions' has no attribute 'set_permission_service'``)
instead of a module-level import that would turn into a collection error and
take the pre-existing permissions tests in these packages down with it.
"""

from __future__ import annotations

import threading
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from typing import Any

import pytest
from singleton_install_test_helpers import (
    PERMISSIONS_SLOT,
    concurrent_reads,
    non_tracing_warnings,
    widened_lazy_create_window,
)

from backend.permissions import PermissionService, get_permission_service, reset_permission_service

_CONCURRENT_READERS = 8
_CONCURRENT_INSTALLS = 8
_CONCURRENT_RESETS = 2
_BARRIER_TIMEOUT = 5.0


@contextmanager
def shared_permission_slot_reset() -> Iterator[None]:
    """Reset the shared permission-service slot for the block, and leave it reset.

    ``get_permission_service()`` has no ``required=False`` form (unlike
    ``get_settings_registry``), so the instance the suite currently holds cannot
    be saved without constructing one — and putting a saved instance back would
    need the install operation this task adds. The slot's state at module import
    is "unset", so resetting before and after the block is the public-API-only
    isolation: the block starts from the AC's "shared default is unset" and ends
    in the same state it found.
    """
    reset_permission_service()
    try:
        yield
    finally:
        reset_permission_service()


# --- Public install operation (user-roles-permissions.md v2 REQ-030, AC-041 .. AC-044) ---


def test_ac_041_set_permission_service_installs_default() -> None:
    """AC-041: installing a service into an unset shared default returns None and makes it the default."""
    with shared_permission_slot_reset():
        service = PERMISSIONS_SLOT.new()  # built with in-memory repositories (REQ-023)
        assert PERMISSIONS_SLOT.install(service) is None
        assert get_permission_service() is service


def test_ac_042_replace_logs_one_warning(log_records: list[Any]) -> None:
    """AC-042: replacing a held default logs exactly one WARNING naming it; installing into an unset slot logs none."""
    with shared_permission_slot_reset():
        first = PERMISSIONS_SLOT.new()
        PERMISSIONS_SLOT.install(first)  # unset slot: no WARNING
        assert not non_tracing_warnings(log_records), f"install into an unset slot warned: {log_records!r}"
        log_records.clear()
        second = PERMISSIONS_SLOT.new()
        PERMISSIONS_SLOT.install(second)  # held slot: no exception, exactly one WARNING
        warnings = non_tracing_warnings(log_records)
        assert len(warnings) == 1, f"expected exactly one replace WARNING, got {warnings!r}"
        assert "permission" in str(warnings[0]).lower(), (
            f"the WARNING does not name the shared default: {warnings[0]!r}"
        )
        assert get_permission_service() is second


def test_ac_043_concurrent_install_read_reset(monkeypatch: pytest.MonkeyPatch) -> None:
    """AC-043: concurrent lazy creates yield one default; concurrent install/read/reset never tear the slot."""
    with shared_permission_slot_reset():
        # Unset default: 8 threads read it into existence at the same moment.
        PERMISSIONS_SLOT.clear()
        with widened_lazy_create_window(monkeypatch, PermissionService) as window:
            services = concurrent_reads(PERMISSIONS_SLOT, _CONCURRENT_READERS)
        assert len(window.instances) == 1, f"lazy create race built {len(window.instances)} services"
        assert all(s is services[0] for s in services), "concurrent readers did not receive one shared service"

        # Held default: installs, reads and resets interleaved.
        PERMISSIONS_SLOT.install(PERMISSIONS_SLOT.new())
        installed = [PERMISSIONS_SLOT.new() for _ in range(_CONCURRENT_INSTALLS)]
        errors = _concurrent_install_read_reset(installed)
        assert not errors, f"install/read/reset threads raised: {errors!r}"
        assert isinstance(get_permission_service(), PermissionService), "the slot ended up torn"


def test_ac_044_install_then_reset_then_default() -> None:
    """AC-044: after install then reset, the getter returns a freshly created default, not the installed one."""
    with shared_permission_slot_reset():
        installed = PERMISSIONS_SLOT.new()
        PERMISSIONS_SLOT.install(installed)
        PERMISSIONS_SLOT.clear()  # reset_permission_service(): the slot is unset again
        default = get_permission_service()
        assert isinstance(default, PermissionService)
        assert default is not installed


def _concurrent_install_read_reset(installed: list[PermissionService]) -> list[BaseException]:
    """Install ``installed``, read and reset the shared slot from barrier-released threads.

    Returns every exception the threads raised (an ``AssertionError`` from a read
    that saw a torn slot included) instead of letting a thread die silently.
    """
    start = threading.Barrier(_CONCURRENT_INSTALLS + _CONCURRENT_READERS + _CONCURRENT_RESETS)
    errors: list[BaseException] = []

    def _run(action: Callable[..., Any], *args: Any) -> None:
        try:
            start.wait(timeout=_BARRIER_TIMEOUT)
            action(*args)
        except BaseException as exc:  # reported through the assertion in the test
            errors.append(exc)

    threads = [threading.Thread(target=_run, args=(PERMISSIONS_SLOT.install, service)) for service in installed]
    threads += [threading.Thread(target=_run, args=(_read_whole_service,)) for _ in range(_CONCURRENT_READERS)]
    threads += [threading.Thread(target=_run, args=(PERMISSIONS_SLOT.clear,)) for _ in range(_CONCURRENT_RESETS)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return errors


def _read_whole_service() -> None:
    """A read must yield a whole ``PermissionService`` — never a half-written slot."""
    assert isinstance(PERMISSIONS_SLOT.read(), PermissionService)
