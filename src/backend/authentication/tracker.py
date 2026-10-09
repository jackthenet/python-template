"""In-memory brute-force throttling for login identifiers (REQ-004).

:class:`InMemoryAttemptTracker` tracks per-identifier failure counts and
lock-until timestamps. It is thread-safe (NFR-005): an internal lock guards all
state. A successful login clears the identifier's state; an elapsed lock
elapses automatically (``is_locked`` is true only while ``lock_until`` is in
the future).
"""

from __future__ import annotations

import threading
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from backend.logging import logged_class


@dataclass
class _AttemptState:
    """Per-identifier throttle state: failures counted so far, and the lock horizon.

    ``lock_until`` is an absolute instant, so an elapsed lock needs no cleanup — but
    the failure count itself never decays.
    """

    failures: int = 0
    lock_until: datetime | None = None


@logged_class(slow_threshold_ms=10, include_args=False)
class InMemoryAttemptTracker:
    """A thread-safe in-memory attempt tracker.

    The class is traced via the shared logging feature (``@logged_class``) with
    ``include_args=False`` so identifiers never appear in log records.
    """

    def __init__(self, max_failed_attempts: int, lockout_duration: timedelta) -> None:
        """Fix the lockout policy for the tracker's whole lifetime.

        The ``max_failed_attempts``-th failure of an identifier locks it for
        ``lockout_duration`` (REQ-004). State is per identifier and guarded by one
        internal lock, so the tracker can be shared across threads (NFR-005).
        """
        self._max_failed_attempts = max_failed_attempts
        self._lockout_duration = lockout_duration
        self._lock = threading.Lock()
        self._state: dict[str, _AttemptState] = {}

    def record_failure(self, identifier: str) -> None:
        """Count one rejected attempt for an identifier (REQ-004).

        Reaching ``max_failed_attempts`` sets a fresh ``lock_until``; because the
        count is not decayed, a failure after an elapsed lock re-locks the identifier
        immediately.
        """
        with self._lock:
            state = self._state.get(identifier)
            if state is None:
                state = _AttemptState()
                self._state[identifier] = state
            state.failures += 1
            if state.failures >= self._max_failed_attempts:
                state.lock_until = datetime.now(UTC) + self._lockout_duration

    def record_success(self, identifier: str) -> None:
        """Discard all recorded state for an identifier (REQ-004/AC-008); an unknown identifier is a no-op."""
        with self._lock:
            self._state.pop(identifier, None)

    def is_locked(self, identifier: str) -> bool:
        """Whether an identifier is locked right now — true only while ``lock_until`` lies in the future.

        An elapsed lock reports ``False`` without clearing anything, so the caller may
        evaluate the attempt normally (AC-008).
        """
        with self._lock:
            state = self._state.get(identifier)
            if state is None or state.lock_until is None:
                return False
            return state.lock_until > datetime.now(UTC)
