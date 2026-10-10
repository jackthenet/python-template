"""Acceptance tests for the module singleton (docs/specs/session-management.md, AC-041, AC-043,
and — added by ``session-management.md`` v2 — AC-046 .. AC-049).

The singleton is module-level global state, so an autouse fixture resets it
before and after each test (test isolation, AC-043) to guarantee isolation.
The feature package (``backend.sessionmanagement``) is imported lazily inside
the fixture and test bodies so the RED state (module missing) surfaces as a
per-test error rather than a file-level collection error (house pattern).

The install/get/reset trio of the v2 criteria is reached through
``SESSIONMANAGEMENT_SLOT``, which resolves the three names by attribute at call
time: the RED signal then stays inside the test body
(``AttributeError: module 'backend.sessionmanagement' has no attribute
'set_session_service'``) instead of becoming a module-level import error that
would take the pre-existing session-management tests down with it.

Session-management is the **asymmetric** singleton-owning feature: it has no
lazily created default — ``get_session_service()`` without a ``repository``
raises ``ValueError`` (EDGE-003 / AC-042, unchanged by v2). The install → read →
reset pair is therefore observed through ``get_session_service(repository)``
(change REQ-008 / AC-012), and every concurrent read carries a repository.
"""

from __future__ import annotations

import threading
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
from sessionmanagement_test_helpers import db_url
from singleton_install_test_helpers import (
    SESSIONMANAGEMENT_SLOT,
    concurrent_reads,
    non_tracing_warnings,
)

from backend.authentication.repository import SqliteSessionRepository

_CONCURRENT_READERS = 8
_CONCURRENT_INSTALLS = 8
_CONCURRENT_RESETS = 2
_BARRIER_TIMEOUT = 5.0


@pytest.fixture(autouse=True)
def _isolate_singleton():
    """Reset the module singleton before and after each test (test isolation, AC-043)."""
    from backend.sessionmanagement import reset_session_service

    reset_session_service()
    yield
    reset_session_service()


def test_ac_041_singleton_created_once(tmp_path: Path) -> None:
    """AC-041: first call creates the singleton; subsequent calls return the same instance."""
    from backend.sessionmanagement import get_session_service

    # Given: no singleton yet (the fixture reset it)
    repository = SqliteSessionRepository(db_url(tmp_path))
    # When: the first call creates the singleton
    first = get_session_service(repository)
    # Then: subsequent calls (with or without arguments) return the same instance
    assert get_session_service(repository) is first
    assert get_session_service() is first


def test_ac_043_reset_session_service(tmp_path: Path) -> None:
    """AC-043: reset clears the singleton; a subsequent call creates a new instance."""
    from backend.sessionmanagement import get_session_service, reset_session_service

    # Given: an existing singleton
    repository = SqliteSessionRepository(db_url(tmp_path))
    first = get_session_service(repository)
    # When: the singleton is reset
    reset_session_service()
    # Then: a subsequent call creates a new instance
    second = get_session_service(repository)
    assert second is not first


# --- Public install operation (session-management.md v2 REQ-023, AC-046 .. AC-049) ---


def test_ac_046_set_session_service_installs_default() -> None:
    """AC-046: installing a service into the unset shared default returns None and makes it the default."""
    from backend.sessionmanagement import get_session_service

    # Given: the shared default is unset (the autouse fixture reset it) and a service
    # built over a repository (the slot factory supplies one — EDGE-003)
    service = SESSIONMANAGEMENT_SLOT.new()
    # When: the install operation is called
    assert SESSIONMANAGEMENT_SLOT.install(service) is None
    # Then: a later read with no repository argument returns that exact instance
    assert get_session_service() is service


def test_ac_047_replace_logs_one_warning(log_records: list[Any]) -> None:
    """AC-047: replacing a held shared default logs exactly one WARNING naming it; installing into an unset default logs none."""
    from backend.sessionmanagement import get_session_service

    first = SESSIONMANAGEMENT_SLOT.new()
    SESSIONMANAGEMENT_SLOT.install(first)  # unset default: no WARNING
    assert not non_tracing_warnings(log_records), f"install into an unset default warned: {log_records!r}"
    log_records.clear()
    second = SESSIONMANAGEMENT_SLOT.new()
    SESSIONMANAGEMENT_SLOT.install(second)  # held default: no exception, exactly one WARNING
    warnings = non_tracing_warnings(log_records)
    assert len(warnings) == 1, f"expected exactly one replace WARNING, got {warnings!r}"
    assert "session" in str(warnings[0]).lower(), f"the WARNING does not name the shared default: {warnings[0]!r}"
    assert get_session_service() is second


def test_ac_048_concurrent_install_read_reset(tmp_path: Path) -> None:
    """AC-048: concurrent install, read and reset never tear the shared default; every read returns a whole service."""
    from backend.sessionmanagement import SessionService, get_session_service

    # Given: the shared default holds a service (the lazy create with a repository —
    # AC-041, it exists today, so the setup does not need the install operation).
    # Every read carries a repository: this feature creates nothing without one
    # (EDGE-003), so a read racing a reset must not fail on a ValueError.
    repository = SqliteSessionRepository(db_url(tmp_path))
    held = get_session_service(repository)

    # 8 barrier-released reads of the held default: each returns it whole. This half
    # passes today — it is the regression witness that the guarded read still returns
    # one whole instance once the install path joins the module lock (change
    # REQ-006 / REQ-007).
    reads = concurrent_reads(SESSIONMANAGEMENT_SLOT, _CONCURRENT_READERS, args=(repository,))
    assert all(r is held for r in reads), "concurrent reads did not return the held service"

    # Installs, reads and resets interleaved. This is the half that is RED today — the
    # install operation does not exist yet.
    installed = [SESSIONMANAGEMENT_SLOT.new() for _ in range(_CONCURRENT_INSTALLS)]
    errors = _concurrent_install_read_reset(repository, installed)
    assert not errors, f"install/read/reset threads raised: {errors!r}"
    assert isinstance(get_session_service(repository), SessionService), "the shared default ended up torn"


def test_ac_049_install_then_reset_then_default(tmp_path: Path) -> None:
    """AC-049: after install then reset, the getter returns a freshly created service, not the installed one."""
    from backend.sessionmanagement import SessionService, get_session_service

    installed = SESSIONMANAGEMENT_SLOT.new()
    SESSIONMANAGEMENT_SLOT.install(installed)
    SESSIONMANAGEMENT_SLOT.clear()  # reset_session_service(): the shared default is unset again
    # EDGE-003 carve-out (change REQ-008 / AC-012): this feature's default can only be
    # created when a repository is supplied, so the pair is observed through the
    # repository-argument form.
    fresh = get_session_service(SqliteSessionRepository(db_url(tmp_path)))
    assert isinstance(fresh, SessionService)
    assert fresh is not installed


def _concurrent_install_read_reset(repository: SqliteSessionRepository, installed: list[Any]) -> list[BaseException]:
    """Install ``installed``, read and reset the shared default from barrier-released threads.

    Returns every exception the threads raised (an ``AssertionError`` from a read that
    did not get a whole instance included) instead of letting a thread die silently.
    """
    start = threading.Barrier(_CONCURRENT_INSTALLS + _CONCURRENT_READERS + _CONCURRENT_RESETS)
    errors: list[BaseException] = []

    def _run(action: Callable[..., Any], *args: Any) -> None:
        try:
            start.wait(timeout=_BARRIER_TIMEOUT)
            action(*args)
        except BaseException as exc:  # reported through the assertion in the test
            errors.append(exc)

    threads = [threading.Thread(target=_run, args=(SESSIONMANAGEMENT_SLOT.install, service)) for service in installed]
    threads += [
        threading.Thread(target=_run, args=(_read_whole_session_service, repository))
        for _ in range(_CONCURRENT_READERS)
    ]
    threads += [threading.Thread(target=_run, args=(SESSIONMANAGEMENT_SLOT.clear,)) for _ in range(_CONCURRENT_RESETS)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return errors


def _read_whole_session_service(repository: SqliteSessionRepository) -> None:
    """A read must yield a whole ``SessionService`` — never a half-written slot."""
    from backend.sessionmanagement import SessionService

    assert isinstance(SESSIONMANAGEMENT_SLOT.read(repository), SessionService)
