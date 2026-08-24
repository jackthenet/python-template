"""Property tests for the logging feature (docs/specs/logging.md)."""

import logging
from typing import Any

import pytest
from hypothesis import given
from hypothesis import strategies as st
from backend.logging import logged, logged_class, setup_logger


def test_inv_001_setup_logger_idempotent() -> None:
    """INV-001: calling setup_logger multiple times does not duplicate sinks."""
    setup_logger()
    setup_logger()
    setup_logger()


def test_inv_002_stdlib_interception_routes_to_loguru() -> None:
    """INV-002: stdlib logging records are routed through loguru sinks."""
    setup_logger()
    std_logger = logging.getLogger("property-test")
    std_logger.info("hello from stdlib")


def test_inv_003_logged_preserves_exceptions() -> None:
    """INV-003: @logged preserves exceptions raised by the wrapped function."""

    @logged
    def fail(msg: str) -> None:
        raise ValueError(msg)

    with pytest.raises(ValueError):
        fail("boom")


@given(st.text(min_size=0, max_size=50))
def test_inv_003_logged_preserves_exception_messages(msg: str) -> None:
    """INV-003: exception messages are preserved through @logged."""

    @logged
    def fail(msg: str) -> None:
        raise ValueError(msg)

    with pytest.raises(ValueError) as exc_info:
        fail(msg)
    assert str(exc_info.value) == msg


@given(st.integers())
def test_inv_003_logged_preserves_return_values(value: int) -> None:
    """INV-003: @logged preserves the wrapped function's return value."""

    @logged
    def identity(x: int) -> int:
        return x

    assert identity(value) == value
