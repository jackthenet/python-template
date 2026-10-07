"""Property tests for the shared install operation (INV-002, INV-003).

Normative source: ``docs/specs/settings-public-registry-setter.md`` INV-002 and
INV-003 (change-level IDs — PROBLEMS.md P-53), over REQ-001…REQ-005 and REQ-009.

The strategy domain is the sequence the spec quantifies over — "for any sequence
of installs on one feature's singleton": a list of booleans, each ``True`` an
install of a fresh instance, each ``False`` a ``reset_*()`` (the only other
operation the two invariants mention). INV-001 (last-install-wins under
concurrency) is T-010's witness and is not here.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from eventbus_test_helpers import isolated_event_bus
from hypothesis import given, settings
from hypothesis import strategies as st
from singleton_install_test_helpers import SLOTS, EventWatcher, SingletonSlot, non_tracing_warnings

from backend.eventbus import get_event_bus

# Bounded by what a witness can afford: every install builds a real instance (an
# in-memory store for two of the five features). The invariant is about the shape of
# the sequence, not its length.
_SEQUENCE = st.lists(st.booleans(), min_size=1, max_size=6)


class _Holder:
    """A caller constructed with an injected instance (INV-003: "every object that was constructed with an injected instance").

    ``ponytail:`` it holds the instance directly — two of the five singleton classes
    have no consuming service at all in the public API, so a real consumer would
    couple this change's tests to another feature's internals. The injected-consumer
    form is witnessed by the feature specs (search.md EDGE-022,
    session-management.md EDGE-014, event-bus.md EDGE-011).
    """

    def __init__(self, instance: Any) -> None:
        self.instance = instance


def _run_sequence(slot: SingletonSlot, sequence: list[bool], watch: Callable[[Any], None]) -> list[Any]:
    """Apply one install/reset sequence to one feature's slot, watching each instance before it is installed."""
    installed: list[Any] = []
    for install_new in sequence:
        if install_new:
            instance = slot.new()
            watch(instance)  # subscribe before the install: an event an install publishes is already queued by then
            installed.append(instance)
            slot.install(instance)
        else:
            slot.clear()
    return installed


def _watcher_over(watcher: EventWatcher) -> Callable[[Any], None]:
    """``watcher.watch`` without duplicate subscriptions (a duplicate handler would double-deliver)."""
    watched: set[int] = set()

    def watch(instance: Any) -> None:
        if id(instance) not in watched:
            watched.add(id(instance))
            watcher.watch(instance)

    return watch


def _count_installs_on_nonempty_slot(
    slot: SingletonSlot, sequence: list[bool], log_records: list[Any]
) -> tuple[int, list[Any]]:
    """Apply one install/reset sequence to one slot; return the installs that met a non-empty slot and the WARNINGs captured."""
    slot.clear()
    log_records.clear()  # only this sequence's records may count
    expected = 0
    empty = True
    installed: list[Any] = []
    try:
        for install_new in sequence:
            if install_new:
                instance = slot.new()
                installed.append(instance)
                slot.install(instance)
                expected += 0 if empty else 1
                empty = False
            else:
                slot.clear()
                empty = True
        return expected, non_tracing_warnings(log_records)
    finally:
        for instance in installed:
            slot.dispose(instance)
        slot.clear()


def test_inv_002_warning_count_matches_nonempty_installs(log_records: list[Any]) -> None:
    """INV-002: for any install sequence the WARNING count equals the number of installs applied to a non-empty slot — no more, no fewer."""

    @given(sequence=_SEQUENCE)
    @settings(max_examples=15, deadline=None)
    def inner(sequence: list[bool]) -> None:
        for slot in SLOTS:
            expected, warnings = _count_installs_on_nonempty_slot(slot, sequence, log_records)
            assert len(warnings) == expected, (
                f"{slot.name()}: the sequence {sequence!r} applied {expected} install(s) to a "
                f"non-empty slot but logged {warnings!r}"
            )

    inner()


def _assert_no_install_events(slot: SingletonSlot, sequence: list[bool]) -> None:
    """INV-003, first half: no bus — the shared default or an installed instance — receives an event caused by an install."""
    watcher = EventWatcher()
    watch = _watcher_over(watcher)
    slot.clear()
    watch(get_event_bus())  # the shared default an install would publish on
    installed = _run_sequence(slot, sequence, watch)
    current = get_event_bus()
    watch(current)
    current.publish(object())  # anti-vacuity: this one demonstrably arrives
    watcher.drain()  # shutdown drains the queue (event-bus.md AC-008): nothing is still in flight
    try:
        assert len(watcher.received) == 1, (
            f"{slot.name()}: the sequence {sequence!r} published {len(watcher.received) - 1} "
            f"event(s) beyond the witness's own: {watcher.received!r}"
        )
    finally:
        for instance in installed:
            slot.dispose(instance)
        slot.clear()


def _assert_holder_keeps_instance(slot: SingletonSlot, sequence: list[bool]) -> None:
    """INV-003, second half: an object constructed with an injected instance keeps that exact instance."""
    slot.clear()
    held, probe = slot.stamp()
    try:
        slot.install(held)
        holder = _Holder(held)
        installed = _run_sequence(slot, sequence, lambda _instance: None)
        try:
            assert probe(holder.instance), (
                f"{slot.name()}: the sequence {sequence!r} changed how the instance a caller holds behaves — "
                "an install rebound the caller's object, not just the slot"
            )
        finally:
            for instance in installed:
                slot.dispose(instance)
    finally:
        slot.dispose(held)
        slot.clear()


def test_inv_003_no_events_and_no_rebinding() -> None:
    """INV-003: for any install sequence no bus receives an install-caused event, and every constructed holder keeps its instance."""

    @given(sequence=_SEQUENCE)
    @settings(max_examples=15, deadline=None)
    def inner(sequence: list[bool]) -> None:
        for slot in SLOTS:
            # The two halves run apart from each other: the first drains (shuts down) every
            # bus it touched, and a stamp on a bus publishes — so one pass would feed the
            # stamp's own marker event into the event collector.
            _assert_no_install_events(slot, sequence)
            _assert_holder_keeps_instance(slot, sequence)

    with isolated_event_bus():  # these sequences reset the event bus slot; park the suite's live bus
        inner()
