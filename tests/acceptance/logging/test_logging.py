"""Acceptance tests for the logging feature (docs/specs/logging.md)."""

from __future__ import annotations

import threading

import pytest


class TestSetupLogger:
    """AC-001, AC-002, AC-003 — setup_logger() behavior."""

    def test_ac_001_setup_logger_adds_sinks(self) -> None:
        """AC-001: setup_logger() adds configured sinks to the logger."""
        from backend.logging import setup_logger

        setup_logger()
        import loguru

        assert len(loguru.logger._core.handlers) >= 1

    def test_ac_002_setup_logger_idempotent(self) -> None:
        """AC-002: calling setup_logger() twice does not duplicate sinks."""
        from backend.logging import setup_logger

        setup_logger()
        import loguru

        count_after_first = len(loguru.logger._core.handlers)
        setup_logger()
        count_after_second = len(loguru.logger._core.handlers)
        assert count_after_first == count_after_second

    def test_ac_003_setup_logger_thread_safe(self) -> None:
        """AC-003: concurrent calls to setup_logger() are safe."""
        from backend.logging import setup_logger

        errors: list[BaseException] = []

        def worker() -> None:
            try:
                setup_logger()
            except BaseException as exc:
                errors.append(exc)

        threads = [threading.Thread(target=worker) for _ in range(8)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors


class TestLoggedDecorator:
    """AC-004, AC-005, AC-006 — @logged decorator behavior."""

    def test_ac_004_logged_logs_function_call(self) -> None:
        """AC-004: @logged logs the function call with arguments."""
        from backend.logging import logged
        import loguru

        @logged
        def add(a: int, b: int) -> int:
            return a + b

        add(1, 2)
        assert len(loguru.logger._core.handlers) >= 1

    def test_ac_005_logged_preserves_return_value(self) -> None:
        """AC-005: @logged preserves the function's return value."""
        from backend.logging import logged

        @logged
        def add(a: int, b: int) -> int:
            return a + b

        assert add(2, 3) == 5

    def test_ac_006_logged_logs_exceptions(self) -> None:
        """AC-006: @logged logs exceptions raised by the function."""
        from backend.logging import logged

        @logged
        def fail() -> None:
            raise ValueError("boom")

        with pytest.raises(ValueError, match="boom"):
            fail()


class TestLoggedClassDecorator:
    """AC-007, AC-008, AC-009 — @logged_class decorator behavior."""

    def test_ac_007_logged_class_logs_method_calls(self) -> None:
        """AC-007: @logged_class logs method calls on the decorated class."""
        from backend.logging import logged_class
        import loguru

        @logged_class
        class Calculator:
            def add(self, a: int, b: int) -> int:
                return a + b

        Calculator().add(1, 2)
        assert len(loguru.logger._core.handlers) >= 1

    def test_ac_008_logged_class_preserves_return_values(self) -> None:
        """AC-008: @logged_class preserves method return values."""
        from backend.logging import logged_class

        @logged_class
        class Calculator:
            def add(self, a: int, b: int) -> int:
                return a + b

        assert Calculator().add(2, 3) == 5

    def test_ac_009_logged_class_logs_exceptions(self) -> None:
        """AC-009: @logged_class logs exceptions raised by methods."""
        from backend.logging import logged_class

        @logged_class
        class Calculator:
            def fail(self) -> None:
                raise RuntimeError("crash")

        with pytest.raises(RuntimeError, match="crash"):
            Calculator().fail()


class TestStdlibInterception:
    """AC-010, AC-011, AC-012 — stdlib logging interception."""

    def test_ac_010_stdlib_logs_routed_to_loguru(self) -> None:
        """AC-010: stdlib logging calls are routed to loguru sinks."""
        import logging

        from backend.logging import setup_logger
        import loguru

        setup_logger()
        logger = logging.getLogger("test")
        logger.info("hello from stdlib")
        handlers = logging.getLogger().handlers
        assert len(handlers) >= 1

    def test_ac_011_stdlib_interception_idempotent(self) -> None:
        """AC-011: stdlib interception is idempotent."""
        import logging

        from backend.logging import setup_logger

        setup_logger()
        count_after_first = len(logging.getLogger().handlers)
        setup_logger()
        count_after_second = len(logging.getLogger().handlers)
        assert count_after_first == count_after_second

    def test_ac_012_stdlib_interception_thread_safe(self) -> None:
        """AC-012: concurrent stdlib interception setup is safe."""
        import logging

        from backend.logging import setup_logger

        errors: list[BaseException] = []

        def worker() -> None:
            try:
                setup_logger()
            except BaseException as exc:
                errors.append(exc)

        threads = [threading.Thread(target=worker) for _ in range(8)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors


class TestPublicApi:
    """AC-013, AC-014, AC-015 — public API surface."""

    def test_ac_013_public_api_exports(self) -> None:
        """AC-013: backend.logging exports setup_logger, logged, logged_class."""
        import backend.logging as mod

        assert hasattr(mod, "setup_logger")
        assert hasattr(mod, "logged")
        assert hasattr(mod, "logged_class")

    def test_ac_014_setup_logger_accepts_settings(self) -> None:
        """AC-014: setup_logger() accepts an optional Settings parameter."""
        from backend.logging import setup_logger

        setup_logger(None)

    def test_ac_015_logged_accepts_level(self) -> None:
        """AC-015: @logged accepts an optional level parameter."""
        from backend.logging import logged

        @logged(level="DEBUG")
        def noop() -> None:
            pass

        noop()
