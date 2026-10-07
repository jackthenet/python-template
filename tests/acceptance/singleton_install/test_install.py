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

from typing import Any

from eventbus_test_helpers import UserCreated, isolated_event_bus, wait_for
from settings_test_helpers import restore_singleton
from singleton_install_test_helpers import (
    EVENTBUS_SLOT,
    SETTINGS_SLOT,
    SLOTS,
    EventWatcher,
    non_tracing_warnings,
)

from backend.eventbus import EventBus, get_event_bus
from backend.settings import get_settings_registry, reset_settings_registry


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
