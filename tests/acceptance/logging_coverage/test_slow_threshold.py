"""AC-007 / AC-014: every traced class and module function sets a concrete
``slow_threshold_ms``; a traced call exceeding its threshold logs a WARNING and
is not interrupted.

REQ-007: every traced class and module function sets a sensible, concrete
``slow_threshold_ms`` (not ``None``).
REQ-014 / NFR-001: a traced call that exceeds its ``slow_threshold_ms`` logs a
WARNING (slow-call detection) and is NOT interrupted (observability, not
enforcement).
"""

from __future__ import annotations

import time
from typing import Any

from logging_coverage_test_helpers import (
    INVENTORY_CLASSES,
    INVENTORY_MODULE_FUNCTIONS,
    exit_records,
    level_name,
)

from backend.authentication.tracker import InMemoryAttemptTracker
from backend.logging import logged


def _is_concrete_threshold(value: Any) -> bool:
    return (
        value is not None
        and isinstance(value, (int, float))
        and not isinstance(value, bool)
        and value > 0
    )


def test_traced_classes_have_concrete_threshold() -> None:
    """AC-007: every inventory class and module function has a concrete (non-None)
    ``slow_threshold_ms``."""
    for name, cls in INVENTORY_CLASSES.items():
        threshold = getattr(cls, "slow_threshold_ms", None)
        assert _is_concrete_threshold(threshold), (
            f"{name} has no concrete slow_threshold_ms (got {threshold!r})"
        )

    for name, fn in INVENTORY_MODULE_FUNCTIONS.items():
        threshold = getattr(fn, "slow_threshold_ms", None)
        assert _is_concrete_threshold(threshold), (
            f"{name} has no concrete slow_threshold_ms (got {threshold!r})"
        )


def test_slow_call_logs_warning_not_interrupted(log_records: list[Any]) -> None:
    """AC-014 / NFR-001: a traced call exceeding its threshold logs a WARNING and
    completes normally."""
    # The slow-call mechanism: a traced call slower than its threshold.
    @logged(slow_threshold_ms=1)
    def slow() -> None:
        time.sleep(0.05)

    slow()  # must not raise

    warnings = [r for r in exit_records(log_records) if level_name(r) == "WARNING"]
    assert len(warnings) == 1, "expected exactly one WARNING exit record for the slow call"

    # A real traced class has a concrete threshold, so its slow calls are detected.
    assert _is_concrete_threshold(getattr(InMemoryAttemptTracker, "slow_threshold_ms", None))
