"""Contract tests for the logging feature (docs/specs/logging.md)."""

import inspect

from backend.logging import logged, logged_class, setup_logger


def test_setup_logger_signature() -> None:
    """setup_logger exposes a stable public signature."""
    sig = inspect.signature(setup_logger)
    assert len(sig.parameters) == 0


def test_logged_is_a_decorator_factory() -> None:
    """@logged accepts a function and returns a callable."""

    @logged
    def add(a: int, b: int) -> int:
        return a + b

    assert callable(add)


def test_logged_class_is_a_class_decorator() -> None:
    """@logged_class accepts a class and returns a class."""

    @logged_class
    class Calculator:
        def add(self, a: int, b: int) -> int:
            return a + b

    assert inspect.isclass(Calculator)
