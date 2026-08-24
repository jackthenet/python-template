"""Property tests for the logging feature invariants (docs/specs/logging.md)."""

from __future__ import annotations

import threading
from typing import Any

import pytest
from hypothesis import given, settings, strategies as st


class TestSetupLoggerIdempotency:
    """INV-001: setup_logger() is idempotent — calling it N times yields the same sink count."""

    @given(st.integers(min_value=1, max_value=10))
    @settings(max_examples=5)
    def test_inv_001_setup_logger_idempotent(self, n: int) -> None:
        """INV-001: calling setup_logger() n times produces the same sink count."""
        from features.logging import setup_logger
        import loguru

        for _ in range(n):
            setup_logger()

        count_after_n = len(loguru.logger._core.handlers)
        setup_logger()
        count_after_n_plus_1 = len(loguru.logger._core.handlers)
        assert count_after_n == count_after_n_plus_1


class TestSetupLoggerThreadSafety:
    """INV-002: concurrent setup_logger() calls are thread-safe."""

    @given(st.integers(min_value=2, max_value=16))
    @settings(max_examples=3)
    def test_inv_002_setup_logger_thread_safe(self, n_threads: int) -> None:
        """INV-002: n concurrent threads calling setup_logger() produce no errors."""
        from features.logging import setup_logger

        errors: list[BaseException] = []

        def worker() -> None:
            try:
                setup_logger()
            except BaseException as exc:
                errors.append(exc)

        threads = [threading.Thread(target=worker) for _ in range(n_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors


class TestLoggedDecoratorPreservesBehavior:
    """INV-003: @logged preserves the decorated function's return value and exception behavior."""

    @given(st.integers(min_value=-1000, max_value=1000), st.integers(min_value=-1000, max_value=1000))
    @settings(max_examples=10)
    def test_inv_003_logged_preserves_return_value(self, a: int, b: int) -> None:
        """INV-003: @logged(f)(a, b) == f(a, b) for all inputs."""
        from features.logging import logged

        @logged
        def add(x: int, y: int) -> int:
            return x + y

        assert add(a, b) == a + b

    @given(st.text(min_size=0, max_size=50))
    @settings(max_examples=5)
    def test_inv_003_logged_preserves_exceptions(self, msg: str) -> None:
        """INV-003: @logged(f) raises the same exception as f."""
        from features.logging import logged

        @logged
        def fail(m: str) -> None:
            raise ValueError(m)

        with pytest.raises(ValueError, match=msg if msg else "."):
            fail(msg)
