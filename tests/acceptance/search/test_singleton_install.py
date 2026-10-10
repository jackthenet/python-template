"""Acceptance tests for the search shared-default install operation.

Normative basis: ``docs/specs/search.md`` v4 REQ-024 and AC-038 .. AC-041
(change ``settings-public-registry-setter``, CROSS-CUTTING). Externally observable
behavior only: installing a service makes it the shared default, replacing a held
default logs exactly one WARNING, install / lazy create / reset stay mutually
exclusive under the module lock, and install-then-reset yields a freshly created
default.

The ``set_*`` / ``get_*`` / ``reset_*`` trio is reached through ``SEARCH_SLOT``,
which resolves the three names by attribute at call time. That is what keeps the
RED signal inside the test body (``AttributeError: module 'backend.search' has no
attribute 'set_search_service'``) instead of a module-level import that would turn
into a collection error and take the pre-existing search tests in these packages
down with it.

Search is **not** symmetric with the other four singleton-owning features: it
already holds a module lock (``src/backend/search/service.py`` ``_singleton_lock``,
taken by ``get_search_service()`` and ``reset_search_service()`` today), so its
lazy-create window is already closed. The concurrency witnesses here therefore
fail on the missing install operation, never on a create race: the widened window
is used to prove the existing lock still serialises a slow constructor once the
install path joins it (change REQ-006/REQ-007), not to manufacture a race the lock
prevents.
"""

from __future__ import annotations

import threading
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from typing import Any

import pytest
from singleton_install_test_helpers import (
    SEARCH_SLOT,
    concurrent_reads,
    non_tracing_warnings,
    widened_lazy_create_window,
)

from backend.search import SearchService, get_search_service, reset_search_service

_CONCURRENT_READERS = 8
_CONCURRENT_INSTALLS = 8
_CONCURRENT_RESETS = 2
_BARRIER_TIMEOUT = 5.0


@contextmanager
def shared_search_slot_reset() -> Iterator[None]:
    """Reset the shared search-service slot for the block, and leave it reset.

    ``get_search_service()`` has no ``required=False`` form (unlike
    ``get_settings_registry``), so the instance the suite currently holds cannot be
    saved without constructing one — and putting a saved instance back would need
    the install operation this task adds. The slot's state at module import is
    "unset", so resetting before and after the block is the public-API-only
    isolation: the block starts from the AC's "shared default is unset" and ends in
    the same state it found.
    """
    reset_search_service()
    try:
        yield
    finally:
        reset_search_service()


# --- Public install operation (search.md v4 REQ-024, AC-038 .. AC-041) ---


def test_ac_038_set_search_service_installs_default() -> None:
    """AC-038: installing a service into an unset shared default returns None and makes it the default."""
    with shared_search_slot_reset():
        service = SEARCH_SLOT.new()  # a fresh SearchService over an isolated settings registry
        assert SEARCH_SLOT.install(service) is None
        assert get_search_service() is service


def test_ac_039_replace_logs_one_warning(log_records: list[Any]) -> None:
    """AC-039: replacing a held default logs exactly one WARNING naming it; installing into an unset slot logs none."""
    with shared_search_slot_reset():
        first = SEARCH_SLOT.new()
        SEARCH_SLOT.install(first)  # unset slot: no WARNING
        assert not non_tracing_warnings(log_records), f"install into an unset slot warned: {log_records!r}"
        log_records.clear()
        second = SEARCH_SLOT.new()
        SEARCH_SLOT.install(second)  # held slot: no exception, exactly one WARNING
        warnings = non_tracing_warnings(log_records)
        assert len(warnings) == 1, f"expected exactly one replace WARNING, got {warnings!r}"
        assert "search" in str(warnings[0]).lower(), f"the WARNING does not name the shared default: {warnings[0]!r}"
        assert get_search_service() is second


def test_ac_040_concurrent_install_read_reset(monkeypatch: pytest.MonkeyPatch) -> None:
    """AC-040: concurrent lazy reads yield one default; concurrent install/read/reset never tear the slot."""
    with shared_search_slot_reset():
        # Unset default: 8 threads read it into existence at the same moment. Search's
        # lazy path already takes the module lock, so this half passes today — it is the
        # regression witness that the direct write stays inside the lock (change
        # REQ-006/REQ-007) when the install path joins it.
        with widened_lazy_create_window(monkeypatch, SearchService) as window:
            services = concurrent_reads(SEARCH_SLOT, _CONCURRENT_READERS)
        assert len(window.instances) == 1, f"lazy create race built {len(window.instances)} services"
        assert all(s is services[0] for s in services), "concurrent readers did not receive one shared service"

        # Held default: installs, reads and resets interleaved. This is the half that is
        # RED today — the install operation does not exist yet.
        SEARCH_SLOT.install(SEARCH_SLOT.new())
        installed = [SEARCH_SLOT.new() for _ in range(_CONCURRENT_INSTALLS)]
        errors = _concurrent_install_read_reset(installed)
        assert not errors, f"install/read/reset threads raised: {errors!r}"
        assert isinstance(get_search_service(), SearchService), "the slot ended up torn"


def test_ac_041_install_then_reset_then_default() -> None:
    """AC-041: after install then reset, the getter returns a freshly created default, not the installed one."""
    with shared_search_slot_reset():
        installed = SEARCH_SLOT.new()
        SEARCH_SLOT.install(installed)
        SEARCH_SLOT.clear()  # reset_search_service(): the slot is unset again
        default = get_search_service()
        assert isinstance(default, SearchService)
        assert default is not installed


def _concurrent_install_read_reset(installed: list[SearchService]) -> list[BaseException]:
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

    threads = [threading.Thread(target=_run, args=(SEARCH_SLOT.install, service)) for service in installed]
    threads += [threading.Thread(target=_run, args=(_read_whole_service,)) for _ in range(_CONCURRENT_READERS)]
    threads += [threading.Thread(target=_run, args=(SEARCH_SLOT.clear,)) for _ in range(_CONCURRENT_RESETS)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return errors


def _read_whole_service() -> None:
    """A read must yield a whole ``SearchService`` — never a half-written slot."""
    assert isinstance(SEARCH_SLOT.read(), SearchService)
