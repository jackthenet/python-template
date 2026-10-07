"""The cross-feature witness set for the module lock of the five singleton owners.

Normative source: ``docs/specs/settings-public-registry-setter.md`` REQ-006,
REQ-007, REQ-008 · AC-009, AC-010, AC-011, AC-012 · EDGE-010 · INV-001 · NFR-003
(change-level IDs — PROBLEMS.md P-53) and ``docs/decisions/ADR-084`` (one
module-level ``threading.Lock`` per owning module, guarding install, lazy create
and reset as one mutually exclusive set). The five amended feature specs state
the same rule in their own numbering — ``settings.md`` AC-042, ``event-bus.md``
AC-015, ``user-roles-permissions.md`` AC-043, ``search.md`` AC-040,
``session-management.md`` AC-048 — and their per-feature witnesses live in those
features' own test files; this file is the shared set that runs the same race
over all five slots (``SLOTS``).

No test here sleeps or relies on wall-clock ordering (T-010 design constraint):
every interleaving is forced by a barrier or a ``threading.Event``. The only
sleep in the set is inside ``widened_lazy_create_window``
(``tests/singleton_install_test_helpers.py``), which holds a creating thread
inside its constructor so the lazy-create race is observable at all instead of a
few microseconds wide under the GIL — without it an un-widened race witness
passes whether or not the lock exists.

The trio is reached through the slot object, which resolves the three names by
attribute at call time: the missing install operation fails **inside** the test
body (the RED signal) instead of at import.
"""

from __future__ import annotations

import threading
from collections.abc import Callable
from functools import partial
from typing import Any

import pytest
from eventbus_test_helpers import isolated_event_bus
from singleton_install_test_helpers import (
    EVENTBUS_SLOT,
    SESSIONMANAGEMENT_SLOT,
    SLOTS,
    SingletonSlot,
    concurrent_reads,
    non_tracing_warnings,
    record_constructions,
    widened_lazy_create_window,
)

# The spec's AC-010 shape: 8 installers, 8 readers, 2 resets, one barrier.
_INSTALLS = 8
_READERS = 8
_RESETS = 2
_BARRIER_TIMEOUT = 5.0

# The liveness bound of NFR-003's witness: how long an install may take while a
# reset is provably parked inside ``shutdown()``. It is a ceiling on a blocked
# install (the failure direction is deterministic), not an ordering assumption.
_LIVENESS_TIMEOUT = 2.0


def test_ac_009_concurrent_lazy_create(monkeypatch: pytest.MonkeyPatch) -> None:
    """AC-009 (REQ-006, ADR-084): 8 barrier-released reads of an empty slot build exactly one default."""
    with isolated_event_bus():
        for slot in SLOTS:
            if slot is SESSIONMANAGEMENT_SLOT:
                # AC-009 names the four features whose get_*() creates a default itself.
                # This one raises instead (session-management.md EDGE-003), so its
                # concurrency case is AC-010 below, run with a repository supplied.
                slot.clear()
                with pytest.raises(ValueError):
                    slot.read()
                continue
            slot.clear()
            cls = type(slot.new())  # the class whose lazy create the window widens
            with widened_lazy_create_window(monkeypatch, cls) as window:
                reads = concurrent_reads(slot, _READERS)
            try:
                distinct = {id(value) for value in reads}
                assert len(distinct) == 1, (
                    f"{slot.name()}: {_READERS} concurrent reads of an empty slot returned {len(distinct)} "
                    "different instances — the read-and-swap is not one atomic module-lock step"
                )
                assert len(window.instances) == 1, (
                    f"{slot.name()}: the lazy-create race constructed {len(window.instances)} defaults — "
                    "the lazy write is outside the module lock (REQ-006)"
                )
                assert reads[0] is window.instances[0], f"{slot.name()}: the shared default is not the created instance"
            finally:
                slot.dispose(reads[0])
                slot.clear()


def test_ac_010_concurrent_install_read_reset(log_records: list[Any]) -> None:
    """AC-010 (REQ-006, EDGE-010): installs, reads and resets from barrier-released threads never tear the slot."""
    with isolated_event_bus():
        for slot in SLOTS:
            _witness_install_read_reset(slot, log_records)


def test_nfr_003_slot_lock_is_short_lived() -> None:
    """NFR-003: the module lock covers only the slot swap — a reset's ``shutdown()`` does not block a concurrent install."""
    with isolated_event_bus():
        unblocked, errors = _install_during_blocked_shutdown(serialized=False)
        assert not errors, f"the install raised: {errors!r}"
        assert unblocked, (
            "the install did not complete while the reset was still inside shutdown(): the module lock is held "
            "across feature-level work, which NFR-003 forbids (the lock guards the slot read/swap only)"
        )
        control, _ = _install_during_blocked_shutdown(serialized=True)
        assert not control, (
            "the witness is vacuous: it reports an install that provably waited for the shutdown to finish "
            "as unblocked, so it cannot detect a lock held across shutdown()"
        )


def _witness_install_read_reset(slot: SingletonSlot, log_records: list[Any]) -> None:
    """One feature's AC-010 + EDGE-010 witness: ``_INSTALLS`` installs, ``_READERS`` reads, ``_RESETS`` resets, one barrier.

    ``ponytail:`` the "no half-written slot" check is a safety net, not the witness's
    teeth — a Python-level slot write is atomic under the GIL, so removing the module
    lock alone would not tear a read. What this witness can fail on is the lock's actual
    job: the read/swap/create sequence staying mutually exclusive (no thread raising, no
    install lost, the EDGE-010 WARNING bound below). The lock-removal sensitivity of the
    create path is witnessed by AC-009, whose window the helper deliberately widens.
    """
    slot.clear()
    held = slot.new()
    slot.install(held)  # Given: the slot holds instance A (AttributeError until the operation exists)
    args = slot.read_args()  # session-management reads carry a repository (EDGE-003)
    installed = [slot.new() for _ in range(_INSTALLS)]
    log_records.clear()  # only the race's own records may count towards EDGE-010
    with record_constructions(type(held)) as built:
        errors, reads = _install_read_reset_race(slot, args, installed)
        final = slot.read(*args)  # the slot's value once the race has settled
    known = {id(held), *(id(instance) for instance in installed), *(id(instance) for instance in built)}
    try:
        assert not errors, f"{slot.name()}: install/read/reset threads raised: {errors!r}"
        assert len(reads) == _READERS, f"{slot.name()}: only {len(reads)} of {_READERS} reads completed"
        torn = [value for value in reads if id(value) not in known]
        assert not torn, (
            f"{slot.name()}: {len(torn)} read(s) returned an instance no constructor completed — a half-written slot"
        )
        assert id(final) in known, f"{slot.name()}: the slot ended on an instance no constructor completed"
        _assert_no_install_lost_silently(slot, log_records)
    finally:
        for instance in [held, *installed]:
            slot.dispose(instance)
        slot.clear()


def _install_read_reset_race(
    slot: SingletonSlot, args: tuple[Any, ...], installed: list[Any]
) -> tuple[list[BaseException], list[Any]]:
    """Run the installs, reads and resets released together by one barrier; return the errors and the read results."""
    start = threading.Barrier(_INSTALLS + _READERS + _RESETS)
    errors: list[BaseException] = []
    reads: list[Any] = []
    guard = threading.Lock()

    def _run(action: Callable[[], Any], *, record: bool) -> None:
        try:
            start.wait(timeout=_BARRIER_TIMEOUT)
            value = action()
        except BaseException as exc:  # reported through the assertion in the witness
            with guard:
                errors.append(exc)
            return
        if record:
            with guard:
                reads.append(value)

    threads = [
        threading.Thread(target=_run, args=(partial(slot.install, i),), kwargs={"record": False}) for i in installed
    ]
    threads += [
        threading.Thread(target=_run, args=(lambda: slot.read(*args),), kwargs={"record": True})
        for _ in range(_READERS)
    ]
    threads += [threading.Thread(target=_run, args=(slot.clear,), kwargs={"record": False}) for _ in range(_RESETS)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return errors, reads


def _assert_no_install_lost_silently(slot: SingletonSlot, log_records: list[Any]) -> None:
    """EDGE-010: every install that met a non-empty slot logged its WARNING — none replaced the default silently.

    The slot starts non-empty (A) and only the ``_RESETS`` reset threads can empty it, so
    at least ``_INSTALLS - _RESETS`` installs must have met a non-empty slot, and no more
    than ``_INSTALLS`` installs ran at all. The bounds are properties of the schedule, not
    of the scheduler's ordering.
    """
    warnings = [w for w in non_tracing_warnings(log_records) if slot.warning_keyword in str(w).lower()]
    assert _INSTALLS - _RESETS <= len(warnings) <= _INSTALLS, (
        f"{slot.name()}: {len(warnings)} WARNING(s) for {_INSTALLS} concurrent installs and {_RESETS} resets "
        f"(expected {_INSTALLS - _RESETS}…{_INSTALLS}) — an install replaced the shared default silently"
    )


def _install_during_blocked_shutdown(*, serialized: bool) -> tuple[bool, list[BaseException]]:
    """One NFR-003 pass: park an event bus reset inside ``shutdown()``, then install; did the install get through?

    Returns ``(completed_while_blocked, errors)``. ``serialized=True`` is the witness's own
    control pass: the install waits for the shutdown's release itself — exactly what a
    module lock held across ``shutdown()`` would do to it — so that pass must report
    ``False``, which is what makes the real pass able to fail.
    """
    EVENTBUS_SLOT.clear()
    held = EVENTBUS_SLOT.new()
    EVENTBUS_SLOT.install(held)  # RED today: set_event_bus does not exist yet
    replacement = EVENTBUS_SLOT.new()
    shutdown_started = threading.Event()
    release = threading.Event()
    install_done = threading.Event()
    errors: list[BaseException] = []
    held.shutdown = _blocking_shutdown(shutdown_started, release, held.shutdown)

    def _install() -> None:
        try:
            if serialized:
                release.wait(timeout=_BARRIER_TIMEOUT)
            EVENTBUS_SLOT.install(replacement)
        except BaseException as exc:  # reported through the assertion in the witness
            errors.append(exc)
        install_done.set()

    reset_thread = threading.Thread(target=EVENTBUS_SLOT.clear)
    install_thread = threading.Thread(target=_install)
    reset_thread.start()
    assert shutdown_started.wait(timeout=_BARRIER_TIMEOUT), "the reset never reached shutdown()"
    install_thread.start()
    finished = install_done.wait(timeout=_LIVENESS_TIMEOUT)
    completed_while_blocked = finished and shutdown_started.is_set() and not release.is_set()
    release.set()
    install_thread.join()
    reset_thread.join()
    EVENTBUS_SLOT.clear()
    replacement.shutdown()
    return completed_while_blocked, errors


def _blocking_shutdown(
    started: threading.Event, release: threading.Event, real: Callable[[], None]
) -> Callable[[], None]:
    """A ``shutdown`` stand-in that stays inside the call until the witness releases it."""

    def _shutdown() -> None:
        started.set()
        release.wait(timeout=_BARRIER_TIMEOUT)
        real()

    return _shutdown
