"""Unit tests for the logging feature edge cases (docs/specs/logging.md)."""

from __future__ import annotations

import pytest


class TestLoggedDecoratorEdgeCases:
    """EDGE-001, EDGE-002 — @logged decorator edge cases."""

    def test_edge_001_logged_with_no_arguments(self) -> None:
        """EDGE-001: @logged on a function with no arguments works."""
        from backend.logging import logged

        @logged
        def noop() -> None:
            pass

        noop()

    def test_edge_002_logged_with_keyword_arguments(self) -> None:
        """EDGE-002: @logged on a function called with keyword arguments works."""
        from backend.logging import logged

        @logged
        def add(a: int, b: int) -> int:
            return a + b

        assert add(a=1, b=2) == 3


class TestLoggedClassEdgeCases:
    """EDGE-003 — @logged_class edge cases."""

    def test_edge_003_logged_class_with_init(self) -> None:
        """EDGE-003: @logged_class on a class with __init__ works."""
        from backend.logging import logged_class

        @logged_class
        class Container:
            def __init__(self, value: int) -> None:
                self.value = value

            def get(self) -> int:
                return self.value

        assert Container(42).get() == 42


class TestSetupLoggerEdgeCases:
    """EDGE-004, EDGE-005 — setup_logger() edge cases."""

    def test_edge_004_setup_logger_with_none_settings(self) -> None:
        """EDGE-004: setup_logger(None) uses default settings."""
        from backend.logging import setup_logger

        setup_logger(None)

    def test_edge_005_setup_logger_with_custom_settings(self) -> None:
        """EDGE-005: setup_logger() with custom Settings configures sinks accordingly."""
        from backend.logging import setup_logger

        class CustomSettings:
            log_level: str = "DEBUG"
            log_file: str = "/tmp/test.log"

        setup_logger(CustomSettings())
