"""Unit tests for the logging feature (docs/specs/logging.md)."""

from features.logging import logged, logged_class, setup_logger


def test_setup_logger_registers_sink() -> None:
    """setup_logger registers a sink with the loguru logger."""
    setup_logger()


def test_setup_logger_is_idempotent() -> None:
    """Calling setup_logger twice does not duplicate sinks."""
    setup_logger()
    setup_logger()


def test_logged_preserves_return_value() -> None:
    """@logged preserves the wrapped function's return value."""

    @logged
    def add(a: int, b: int) -> int:
        return a + b

    assert add(1, 2) == 3


def test_logged_preserves_exceptions() -> None:
    """@logged preserves exceptions raised by the wrapped function."""

    @logged
    def fail(msg: str) -> None:
        raise ValueError(msg)

    try:
        fail("boom")
    except ValueError as exc:
        assert str(exc) == "boom"
    else:
        raise AssertionError("ValueError was not raised")


def test_logged_class_preserves_method_behavior() -> None:
    """@logged_class preserves class method behavior."""

    @logged_class
    class Calculator:
        def add(self, a: int, b: int) -> int:
            return a + b

    assert Calculator().add(1, 2) == 3
