"""NFR contract tests for the shared install operation (NFR-002).

Spec: ``docs/specs/settings-public-registry-setter.md`` — NFR-002 ("an install
operation completes in under 1 ms (median, measured with the logging pipeline at
DEBUG) on both the empty-slot and the replacing path"), REQ-004, REQ-005.

The measurement times **only the install call**: the instance is built and the
slot is cleared outside the timed region, so the budget is charged to the install
operation and not to instance construction or to a repository reset. The WARNING
record the replacing path emits is inside the timed region on purpose — the spec
measures the install as the caller experiences it — and the captured records show
that the pipeline really was at DEBUG for the whole measurement.

The median over a fixed sample with a generous margin is the assertion, and it
lives in the test rather than in CI timing, so the witness is not flaky (T-009
design constraint). ``time-machine`` does not help here: it freezes ``datetime``,
not ``time.perf_counter``.
"""

from __future__ import annotations

import time
from typing import Any

from eventbus_test_helpers import isolated_event_bus
from singleton_install_test_helpers import SLOTS, SingletonSlot, non_tracing_warnings

# NFR-002: "under 1 ms (median)". The margin is generous: the install is a slot
# write plus one log record, so the assertion fails only on a real regression, not
# on a slow CI runner.
_BUDGET_MS = 1.0

# Fixed sample size: a median over this many samples is stable, and the whole
# measurement stays well under a second per feature.
_REPEATS = 100


def _install_median(slot: SingletonSlot, *, replacing: bool, log_records: list[Any]) -> float:
    """Median install latency in milliseconds for one of the two NFR-002 paths."""
    timings: list[float] = []
    log_records.clear()
    previous = None
    try:
        for _ in range(_REPEATS):
            slot.clear()  # untimed: the budget is the install, not the reset
            previous = None
            if replacing:
                previous = slot.new()
                slot.install(previous)
            instance = slot.new()
            start = time.perf_counter()
            slot.install(instance)
            timings.append((time.perf_counter() - start) * 1000.0)
            if previous is not None:
                slot.dispose(previous)
    finally:
        slot.clear()
        if previous is not None:
            slot.dispose(previous)

    # NFR-002 measures "with the logging pipeline at DEBUG": the traced install's own
    # DEBUG records and (on the replacing path) its one WARNING per install have to be
    # in the capture, which also pins that the WARNING is inside the timed region.
    debugs = [record for record in log_records if record["level"].name == "DEBUG"]
    assert len(debugs) >= _REPEATS, (
        f"{slot.name()}: the logging pipeline was not at DEBUG ({len(debugs)} DEBUG records)"
    )
    warnings = len(non_tracing_warnings(log_records))
    assert warnings == (_REPEATS if replacing else 0), (
        f"{slot.name()}: the {'replacing' if replacing else 'empty-slot'} path logged "
        f"{warnings} WARNING records over {_REPEATS} installs"
    )
    return sorted(timings)[len(timings) // 2]


def test_nfr_002_install_latency(log_records: list[Any]) -> None:
    """NFR-002 (settings-public-registry-setter.md): both install paths install in under 1 ms (median), with the pipeline at DEBUG."""
    measured: dict[str, dict[str, float]] = {}
    with isolated_event_bus():  # these installs reset the event bus slot; park the suite's live bus
        for slot in SLOTS:
            path = {
                "empty-slot": _install_median(slot, replacing=False, log_records=log_records),
                "replacing": _install_median(slot, replacing=True, log_records=log_records),
            }
            measured[slot.name] = path
            for path_name, median in path.items():
                assert median < _BUDGET_MS, (
                    f"NFR-002: {slot.name} install on the {path_name} path took {median:.3f} ms "
                    f"(median of {_REPEATS}) — the budget is {_BUDGET_MS} ms"
                )
    print(f"NFR-002 install latency (ms, median of {_REPEATS}): {measured}")
