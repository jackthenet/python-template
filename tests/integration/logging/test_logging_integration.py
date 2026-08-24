"""Integration tests for the logging feature (docs/specs/logging.md)."""

import logging

from features.logging import logged, setup_logger


def test_stdlib_logging_intercepted() -> None:
    """stdlib logging records are routed through loguru."""
    setup_logger()
    std_logger = logging.getLogger("integration-test")
    std_logger.info("hello from stdlib")


def test_logged_decorator_with_logging() -> None:
    """@logged functions emit log records through the configured sinks."""
    setup_logger()

    @logged
    def add(a: int, b: int) -> int:
        return a + b

    assert add(1, 2) == 3
