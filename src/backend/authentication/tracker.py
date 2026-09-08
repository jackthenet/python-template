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


@dataclass
class _AttemptState:
    failures: int = 0
    lock_until: datetime | None = None


class InMemoryAttemptTracker:
    """A thread-safe in-memory attempt tracker."""

    def __init__(self, max_failed_attempts: int, lockout_duration: timedelta) -> None:
        self._max_failed_attempts = max_failed_attempts
        self._lockout_duration = lockout_duration
        self._lock = threading.Lock()
        self._state: dict[str, _AttemptState] = {}

    def record_failure(self, identifier: str) -> None:
        with self._lock:
            state = self._state.get(identifier)
            if state is None:
                state = _AttemptState()
                self._state[identifier] = state
            state.failures += 1
            if state.failures >= self._max_failed_attempts:
                state.lock_until = datetime.now(UTC) + self._lockout_duration

    def record_success(self, identifier: str) -> None:
        with self._lock:
            self._state.pop(identifier, None)

    def is_locked(self, identifier: str) -> bool:
        with self._lock:
            state = self._state.get(identifier)
            if state is None or state.lock_until is None:
                return False
            return state.lock_until > datetime.now(UTC)
