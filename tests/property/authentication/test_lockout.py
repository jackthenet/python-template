"""Property tests for lockout (docs/specs/authentication.md, INV-004)."""

from __future__ import annotations

from datetime import timedelta

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from backend.authentication import InMemoryAttemptTracker

_MAX_EXAMPLES = 10


@settings(max_examples=_MAX_EXAMPLES, suppress_health_check=[HealthCheck.too_slow])
@given(max_failures=st.integers(min_value=2, max_value=10), failures=st.integers(min_value=0, max_value=12))
def test_inv_004_lockout_threshold(max_failures: int, failures: int) -> None:
    tracker = InMemoryAttemptTracker(
        max_failed_attempts=max_failures, lockout_duration=timedelta(minutes=15)
    )
    for _ in range(failures):
        tracker.record_failure("alice")
    if failures < max_failures:
        assert tracker.is_locked("alice") is False
    else:
        assert tracker.is_locked("alice") is True
    # after a success it is never locked
    tracker.record_success("alice")
    assert tracker.is_locked("alice") is False
    # a fresh failure sequence locks again, and a success clears it
    for _ in range(max_failures):
        tracker.record_failure("alice")
    assert tracker.is_locked("alice") is True
    tracker.record_success("alice")
    assert tracker.is_locked("alice") is False
