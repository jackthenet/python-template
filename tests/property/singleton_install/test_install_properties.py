"""Property tests for the shared install operation (INV-002, INV-003).

Normative source: ``docs/specs/settings-public-registry-setter.md`` INV-002 and
INV-003 (change-level IDs — PROBLEMS.md P-53), over REQ-001…REQ-005 and REQ-009.

The strategy domain is the sequence the spec quantifies over — "for any sequence
of installs on one feature's singleton": a list of booleans, each ``True`` an
install of a fresh instance, each ``False`` a ``reset_*()`` (the only other
operation the two invariants mention).

T-010 adds INV-001 (last-install-wins). Its strategy is the same shape widened to
the three operations the invariant names — install, reset, read — and its second
half is the concurrency clause of the same invariant ("concurrent installs are
last-writer-wins, and no install is lost silently"), run once per feature because
a Hypothesis loop would only multiply the thread count, not the input space.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from eventbus_test_helpers import isolated_event_bus
from hypothesis import given, settings
from hypothesis import strategies as st
from singleton_install_test_helpers import (
    EVENTBUS_SLOT,
    SLOTS,
    EventWatcher,
    SingletonSlot,
    concurrent_installs,
    non_tracing_warnings,
)

from backend.eventbus import get_event_bus

# Bounded by what a witness can afford: every install builds a real instance (an
# in-memory store for two of the five features). The invariant is about the shape of
# the sequence, not its length.
_SEQUENCE = st.lists(st.booleans(), min_size=1, max_size=6)

# INV-001 quantifies over the three operations its wording names. ``read`` is in the
# domain because the invariant is about what a read returns, not only about writes.
_OPS = st.lists(st.sampled_from(("install", "reset", "read")), min_size=1, max_size=8)

# The concurrency clause: installs racing for one slot. Small on purpose — the clause
# is about the race, not about volume, and every racer is a real instance.
_CONCURRENT_INSTALLS = 4


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
    watcher = EventWatcher()  # subscribes at most once per bus instance, so re-watching one cannot double-deliver
    # The previous slot's witness drained (shut down) the shared bus it watched, and only
    # the event bus feature's own reset empties that slot — so the shared default would be
    # read back as a dead bus, and a publish on a shut-down bus is a silent no-op
    # (event-bus.md REQ-005, change EDGE-007): the anti-vacuity sentinel would never
    # arrive and "no event" would stop being evidence. Clearing first makes the watched
    # shared default a live instance for every slot.
    EVENTBUS_SLOT.clear()
    slot.clear()
    watcher.watch(get_event_bus())  # the shared default an install would publish on
    installed = _run_sequence(slot, sequence, watcher.watch)
    current = get_event_bus()
    watcher.watch(current)
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
    """INV-003, second half: an object constructed with an injected instance keeps that exact instance.

    The probe is the identity form of the stamp (``SingletonSlot.stamp_identity``):
    INV-003's claim is "keeps that exact instance", and its domain contains
    ``reset_*()``, which shuts the instance down by spec (``event-bus.md`` REQ-005,
    change EDGE-007) — a liveness probe would then be false for a reason the invariant
    does not name. The behavioral claim stays witnessed by AC-005 and EDGE-001, whose
    sequences never reset the held instance away.
    """
    slot.clear()
    held, probe = slot.stamp_identity()
    other, _ = slot.stamp_identity()  # anti-vacuity: the probe must not match every instance
    try:
        assert not probe(other), f"{slot.name()}: the identity probe matches another instance — this witness is vacuous"
        slot.install(held)
        holder = _Holder(held)
        installed = _run_sequence(slot, sequence, lambda _instance: None)
        try:
            assert probe(holder.instance), (
                f"{slot.name()}: the sequence {sequence!r} changed which instance the caller holds — "
                "an install rebound the caller's object, not just the slot"
            )
        finally:
            for instance in installed:
                slot.dispose(instance)
    finally:
        for instance in (held, other):
            slot.dispose(instance)
        slot.clear()


def test_inv_003_no_events_and_no_rebinding() -> None:
    """INV-003: for any install sequence no bus receives an install-caused event, and every constructed holder keeps its instance."""

    @given(sequence=_SEQUENCE)
    @settings(max_examples=15, deadline=None)
    def inner(sequence: list[bool]) -> None:
        for slot in SLOTS:
            # The two halves run apart from each other: the first drains (shuts down) every
            # bus it touched, and a behavioral stamp on a bus publishes — so one pass would
            # feed the stamp's own marker event into the event collector. (The second half's
            # stamp is identity-based and publishes nothing; the separation is kept so the
            # two halves stay independent witnesses.)
            _assert_no_install_events(slot, sequence)
            _assert_holder_keeps_instance(slot, sequence)

    with isolated_event_bus():  # these sequences reset the event bus slot; park the suite's live bus
        inner()


def test_inv_001_last_install_wins(log_records: list[Any]) -> None:
    """INV-001: for any install/reset/read sequence a read returns the most recent install's instance, and concurrent installs are last-writer-wins with no install lost silently.

    The sequence half is the model check; the concurrency half is the same
    invariant's second clause (``EDGE-010``), run once per feature outside the
    Hypothesis loop — more examples would add threads, not input space.
    """

    @given(ops=_OPS)
    @settings(max_examples=15, deadline=None)
    def inner(ops: list[str]) -> None:
        for slot in SLOTS:
            _assert_read_returns_last_write(slot, ops)

    with isolated_event_bus():  # these sequences reset the event bus slot; park the suite's live bus
        inner()
        for slot in SLOTS:
            _assert_concurrent_installs_last_writer_wins(slot, log_records)


def _assert_read_returns_last_write(slot: SingletonSlot, ops: list[str]) -> None:
    """One feature, one sequence: every read returns the instance the model says the slot holds."""
    slot.clear()
    built: list[Any] = []  # every instance the sequence put in front of the slot: installed, or created by a read
    current: Any = None  # what the model says the slot holds; None means empty
    try:
        for op in ops:
            if op == "install":
                instance = slot.new()
                slot.install(instance)  # RED today: the install operation does not exist
                built.append(instance)
                current = instance
            elif op == "reset":
                slot.clear()
                current = None
            else:
                read = slot.read(*slot.read_args())
                if current is None:
                    assert not any(read is instance for instance in built), (
                        f"{slot.name()}: a read after a reset returned an instance the sequence had installed — "
                        "the reset did not drop it"
                    )
                    built.append(read)
                    current = read
                else:
                    assert read is current, (
                        f"{slot.name()}: the read returned neither the last install nor a fresh default"
                    )
    finally:
        for instance in built:
            slot.dispose(instance)
        slot.clear()


def _assert_concurrent_installs_last_writer_wins(slot: SingletonSlot, log_records: list[Any]) -> None:
    """INV-001's concurrency clause (EDGE-010): racing installs lose none of their writes, and every one of them warns."""
    slot.clear()
    first = slot.new()
    slot.install(first)  # the slot is non-empty before the race and nothing empties it during it
    racers = [slot.new() for _ in range(_CONCURRENT_INSTALLS)]
    log_records.clear()
    errors = concurrent_installs(slot, racers)
    warnings = [w for w in non_tracing_warnings(log_records) if slot.warning_keyword in str(w).lower()]
    try:
        assert not errors, f"{slot.name()}: concurrent installs raised: {errors!r}"
        final = slot.read(*slot.read_args())
        assert any(final is racer for racer in racers), (
            f"{slot.name()}: the slot ended on neither of the concurrently installed instances — an install was lost"
        )
        assert len(warnings) == _CONCURRENT_INSTALLS, (
            f"{slot.name()}: {len(warnings)} WARNING(s) for {_CONCURRENT_INSTALLS} installs into a slot that stayed "
            "non-empty throughout — one replaced the shared default silently"
        )
    finally:
        for instance in [first, *racers]:
            slot.dispose(instance)
        slot.clear()
