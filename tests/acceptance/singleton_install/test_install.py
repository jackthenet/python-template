"""Acceptance tests for the public install operation of the feature singletons.

Spec: ``docs/specs/settings-public-registry-setter.md`` (AC-001 .. AC-014).
T-001 derives AC-001 (the settings feature); T-009 adds the cross-feature
witnesses of this file — AC-002 (all five features), AC-003 / AC-004 (the
replace WARNING and its absence), AC-005 (install is not retroactive), AC-006
(the replaced bus keeps its lifecycle) and AC-013 (an install publishes
nothing). T-010 / T-011 add the concurrency and tracing witnesses.

Every witness runs over ``SLOTS`` — one entry per singleton-owning feature — and
resolves the ``set_*`` / ``get_*`` / ``reset_*`` trio through the slot by
attribute at call time, so a feature whose install operation does not exist yet
fails **inside** the test with an ``AttributeError`` naming the missing public
function (the RED signal) instead of failing at import.

The change-level IDs cited here are those of ``settings-public-registry-setter``;
the amended feature specs use their own numbering (PROBLEMS.md P-53).
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import pytest
from eventbus_test_helpers import UserCreated, isolated_event_bus, wait_for
from logging_coverage_test_helpers import level_name, parse_elapsed_ms
from settings_test_helpers import restore_singleton
from singleton_install_test_helpers import (
    EVENTBUS_SLOT,
    SESSIONMANAGEMENT_SLOT,
    SETTINGS_SLOT,
    SLOTS,
    EventWatcher,
    SingletonSlot,
    non_tracing_warnings,
)

from backend.eventbus import EventBus, get_event_bus
from backend.logging import setup_logger
from backend.settings import get_settings_registry, reset_settings_registry

# docs/specs/logging-coverage.md §3.1 note: each install operation is traced with
# @logged(slow_threshold_ms=5), the same threshold as its sibling get_* / reset_*.
_INSTALL_SLOW_THRESHOLD_MS = 5


@pytest.fixture(autouse=True)
def _settings_singleton_restored() -> Iterator[None]:
    """Restore the settings singleton around every witness in this file.

    Each witness clears the slots it touches, and the settings slot is read by the rest of the
    suite through a guarded ``get_settings_registry(required=False)``: a slot left cleared makes a
    later test's guarded read return ``None``, so the traced call it counts never happens (finding
    F-81 — the ``logging_coverage`` AC-002/AC-005 witnesses depend on it). Same save/restore
    mechanism as ``test_module_functions_traced``; the re-setup keeps the session's pipeline
    (DEBUG, the session log file) installed for the tests that follow.

    ``ponytail:`` only the settings slot leaks a *counted* call today; the other four slots are
    restored by their own witnesses. If a later witness starts reading another slot through a
    guarded read, widen this fixture to that slot too.
    """
    saved = get_settings_registry(required=False)
    yield
    restore_singleton(saved)
    setup_logger()


class _Holder:
    """A caller constructed with an instance injected (change AC-005, INV-003).

    ``ponytail:`` the holder is the witness's own reference, not a real consuming
    service — search and session-management have no consumer that takes their
    singleton, so a uniform consumer probe does not exist. The consumer form is
    witnessed per feature instead (``search.md`` EDGE-022 keeps the replaced
    service's registrations, ``session-management.md`` EDGE-014 keeps the replaced
    service working, ``event-bus.md`` EDGE-011 keeps the replaced bus dispatching).
    Upgrade path: give ``SingletonSlot`` a consumer factory once a feature grows one.
    """

    __slots__ = ("instance",)

    def __init__(self, instance: Any) -> None:
        self.instance = instance


def test_ac_001_install_then_get_returns_instance() -> None:
    """AC-001 (REQ-001): the install operation returns None and the getter returns that instance."""
    saved = get_settings_registry(required=False)
    try:
        reset_settings_registry()  # Given: the shared slot is empty
        registry = SETTINGS_SLOT.new()  # built with an isolated value repository
        assert SETTINGS_SLOT.install(registry) is None
        assert get_settings_registry() is registry
    finally:
        restore_singleton(saved)


def test_ac_002_install_all_five_features() -> None:
    """AC-002 (REQ-001): all five features expose the install operation and the installed instance becomes the shared default."""
    with isolated_event_bus():  # the event bus slot is reset by these installs; park the suite's live bus
        for slot in SLOTS:
            slot.clear()  # Given: the shared slot is empty
            instance = slot.new()
            try:
                assert slot.install(instance) is None, f"{slot.name()}: {slot.installer}() did not return None"
                assert slot.read() is instance, f"{slot.name()}: {slot.getter}() does not return the installed instance"
            finally:
                slot.dispose(instance)
                slot.clear()


def test_ac_003_replace_logs_one_warning(log_records: list[Any]) -> None:
    """AC-003 (REQ-002): replacing a held default raises nothing and logs exactly one WARNING naming it."""
    with isolated_event_bus():
        for slot in SLOTS:
            slot.clear()
            log_records.clear()
            first, second = slot.new(), slot.new()
            try:
                slot.install(first)  # empty slot: no WARNING (AC-004)
                assert not non_tracing_warnings(log_records), (
                    f"{slot.name()}: installing into an empty slot warned: {non_tracing_warnings(log_records)!r}"
                )
                log_records.clear()
                slot.install(second)  # held slot: no exception, exactly one WARNING
                warnings = non_tracing_warnings(log_records)
                assert len(warnings) == 1, f"{slot.name()}: replacing the shared default logged {warnings!r}"
                assert slot.warning_keyword in str(warnings[0]).lower(), (
                    f"{slot.name()}: the WARNING does not name the shared default: {warnings[0]!r}"
                )
                assert slot.read() is second, f"{slot.name()}: the replacement is not the shared default"
            finally:
                slot.dispose(first)
                slot.dispose(second)
                slot.clear()


def test_ac_004_empty_slot_no_warning(log_records: list[Any]) -> None:
    """AC-004 (REQ-002): installing into an empty slot logs no WARNING."""
    with isolated_event_bus():
        for slot in SLOTS:
            slot.clear()
            log_records.clear()
            instance = slot.new()
            try:
                slot.install(instance)
                assert slot.read() is instance, f"{slot.name()}: the installed instance is not the shared default"
                assert not non_tracing_warnings(log_records), (
                    f"{slot.name()}: installing into an empty slot logged {non_tracing_warnings(log_records)!r}"
                )
            finally:
                slot.dispose(instance)
                slot.clear()


def test_ac_005_install_not_retroactive() -> None:
    """AC-005 (REQ-003): a caller that holds A keeps A's behavior; only a later read sees B."""
    with isolated_event_bus():
        for slot in SLOTS:
            slot.clear()
            first, probe_first = slot.stamp()  # A carries a marker only A has
            second, _ = slot.stamp()
            try:
                slot.install(first)
                holder = _Holder(first)  # Given: an object constructed with A
                slot.install(second)  # When: B is installed
                assert probe_first(holder.instance), (
                    f"{slot.name()}: the instance a caller holds stopped behaving as it was constructed"
                )
                assert not probe_first(second), (
                    f"{slot.name()}: the marker also matches the replacement — this witness is vacuous"
                )
                assert slot.read() is second, f"{slot.name()}: a later read does not see the replacement"
            finally:
                slot.dispose(first)
                slot.dispose(second)
                slot.clear()


def test_ac_006_replaced_bus_keeps_lifecycle() -> None:
    """AC-006 (REQ-003): replacing the shared bus neither shuts down the running one nor starts the installed one."""
    with isolated_event_bus():
        EVENTBUS_SLOT.clear()
        replaced = EventBus()
        received: list[object] = []
        replaced.subscribe(UserCreated, received.append)
        replaced.start()  # Given: the shared default's worker is running
        replacement = EventBus()
        try:
            EVENTBUS_SLOT.install(replaced)
            EVENTBUS_SLOT.install(replacement)  # When: it is replaced
            assert replaced.is_running, "installing over the shared default shut the replaced bus down"
            replaced.publish(UserCreated("u1", "e1"))
            assert wait_for(lambda: len(received) == 1), "the replaced bus stopped dispatching"
            assert not replacement.is_running, "the install started the bus it installed"
        finally:
            replaced.shutdown()
            replacement.shutdown()
            EVENTBUS_SLOT.clear()


def test_ac_013_install_publishes_no_event() -> None:
    """AC-013 (REQ-009): neither install path — empty slot or replace — publishes an event on any bus."""
    with isolated_event_bus():
        watcher = EventWatcher()
        watcher.watch(get_event_bus())  # the shared default an install would publish on
        for slot in SLOTS:
            slot.clear()
            watcher.watch(get_event_bus())  # reset recreated it; watch the current one too
            first, second = slot.new(), slot.new()
            watcher.watch(first)  # for the event bus feature the shared default IS the installed instance
            watcher.watch(second)
            slot.install(first)  # empty slot
            slot.install(second)  # replacing
            slot.dispose(first)
            slot.dispose(second)
            slot.clear()
        sentinel = object()
        get_event_bus().publish(sentinel)  # anti-vacuity: the demonstrably-arriving event proves the collector works
        watcher.drain()  # shutdown drains the queue (event-bus.md AC-008), so nothing is still in flight
        assert watcher.received == [sentinel], f"an install published an event: {watcher.received!r}"


def test_ac_011_lazy_path_emits_one_traced_pair(log_records: list[Any]) -> None:
    """AC-011 (REQ-007): the owner's lazy create emits one traced pair for the getter and none for the install operation.

    The lazy path writes the slot **directly** — it never calls the public install
    operation — so the only entry/exit pair the read produces is the getter's own, and
    the instance whose constructor finished is what the next read returns.
    """
    with isolated_event_bus():
        for slot in SLOTS:
            if slot is SESSIONMANAGEMENT_SLOT:
                # AC-011 names the four features of AC-009; this one creates no default
                # without a repository (session-management.md EDGE-003), so it has no lazy
                # path to trace. Its install/reset pair is AC-012 below.
                continue
            slot.clear()
            log_records.clear()  # only the lazy read's own records may count
            created = slot.read()
            try:
                pair = _traced_pair(log_records, slot.getter)
                assert pair == (1, 1), (
                    f"{slot.name()}: the lazy read emitted {pair[0]} entry / {pair[1]} exit record(s) of its own"
                )
                assert hasattr(slot.module, slot.installer), (
                    f"{slot.name()}: {slot.installer}() does not exist, so 'no entry record for it' would be vacuous"
                )
                installer_entries = _traced_pair(log_records, slot.installer)[0]
                assert installer_entries == 0, (
                    f"{slot.name()}: the lazy path called the public install operation ({installer_entries} entry "
                    "record(s)) — REQ-007 requires the owner to write its own slot directly"
                )
                assert slot.read() is created, f"{slot.name()}: the lazily created instance is not the shared default"
            finally:
                slot.dispose(created)
                slot.clear()


def test_ac_012_install_then_reset_then_default() -> None:
    """AC-012 (REQ-008): install, then reset, and the next read builds a fresh default, not the installed instance."""
    with isolated_event_bus():
        for slot in SLOTS:
            _witness_install_reset_default(slot)


def _witness_install_reset_default(slot: SingletonSlot) -> None:
    """One feature's AC-012 pair: install → read (the installed instance) → reset → read (a fresh default)."""
    slot.clear()
    installed = slot.new()
    try:
        slot.install(installed)  # RED today: the install operation does not exist
        assert slot.read(*slot.read_args()) is installed, (
            f"{slot.name()}: the installed instance is not the shared default"
        )
        slot.clear()  # reset_*(): the slot is empty again
        fresh = slot.read(*slot.read_args())  # EDGE-003 carve-out: this read carries a repository
        assert fresh is not installed, f"{slot.name()}: the reset did not drop the installed instance"
        assert type(fresh) is type(installed), (
            f"{slot.name()}: the read after the reset built no default of the feature's class"
        )
        assert slot.read(*slot.read_args()) is fresh, (
            f"{slot.name()}: the created default did not become the shared default"
        )
    finally:
        slot.dispose(installed)
        slot.clear()  # for the event bus slot this also shuts the created default down


def test_ac_014_install_is_traced(log_records: list[Any]) -> None:
    """AC-014 (REQ-010): every install operation is traced with ``@logged(slow_threshold_ms=5)``.

    The witness is the mirror image of AC-011: there the lazy read must emit the **getter's**
    pair and none of the installer's, here the install must emit **its own** entry/exit pair,
    with elapsed ms on the exit, at DEBUG, and with no argument or local value formatted into
    either record (the decorator's default ``include_args``, REQ-010).
    """
    with isolated_event_bus():
        for slot in SLOTS:
            _witness_install_traced(slot, log_records)


def _witness_install_traced(slot: SingletonSlot, records: list[Any]) -> None:
    """One feature's AC-014 witness: its install operation's own traced entry/exit pair."""
    installer = getattr(slot.module, slot.installer, None)
    assert installer is not None, (
        f"{slot.name()}: {slot.installer}() does not exist, so it cannot be traced with "
        f"@logged(slow_threshold_ms={_INSTALL_SLOW_THRESHOLD_MS}) (REQ-010)"
    )
    assert getattr(installer, "__logged__", False) is True, (
        f"{slot.name()}: {slot.installer}() exists but is not traced with @logged (REQ-010)"
    )
    assert getattr(installer, "slow_threshold_ms", None) == _INSTALL_SLOW_THRESHOLD_MS, (
        f"{slot.name()}: {slot.installer}() slow_threshold_ms is "
        f"{getattr(installer, 'slow_threshold_ms', None)!r}, not {_INSTALL_SLOW_THRESHOLD_MS} "
        "(docs/specs/logging-coverage.md §3.1 note)"
    )

    slot.clear()
    instance = slot.new()  # built before the record window opens: only the install's own records count
    try:
        records.clear()  # Given: the logging pipeline active at DEBUG
        slot.install(instance)  # When: the install operation is called
        entries, exits = _traced_records(records, slot.installer)
        assert (len(entries), len(exits)) == (1, 1), (
            f"{slot.name()}: the install emitted {len(entries)} entry / {len(exits)} exit record(s) of its own: "
            f"{[str(r) for r in records]!r}"
        )
        assert str(entries[0]) == f">> {slot.installer} called", (
            f"{slot.name()}: the entry record formats arguments or local values into the record: {entries[0]!r}"
        )
        elapsed_ms = parse_elapsed_ms(str(exits[0]))
        assert elapsed_ms is not None, f"{slot.name()}: the exit record carries no elapsed ms: {exits[0]!r}"
        assert level_name(exits[0]) == "DEBUG", (
            f"{slot.name()}: the install's exit record is at {level_name(exits[0])}, not DEBUG "
            f"(elapsed {elapsed_ms} ms against the {_INSTALL_SLOW_THRESHOLD_MS} ms slow-call threshold)"
        )
        assert all("object at 0x" not in str(r) for r in (*entries, *exits)), (
            f"{slot.name()}: the installed instance is formatted into the install's records: "
            f"{[str(r) for r in records]!r}"
        )
    finally:
        slot.dispose(instance)
        slot.clear()


def _traced_records(records: list[Any], function_name: str) -> tuple[list[Any], list[Any]]:
    """The entry and exit records of one traced function, matched on its own name."""
    entries = [r for r in records if str(r).startswith(">>") and function_name in str(r)]
    exits = [r for r in records if str(r).startswith("<<") and function_name in str(r)]
    return entries, exits


def _traced_pair(records: list[Any], function_name: str) -> tuple[int, int]:
    """The (entry, exit) record count of one traced function, matched on its own name."""
    entries, exits = _traced_records(records, function_name)
    return len(entries), len(exits)
