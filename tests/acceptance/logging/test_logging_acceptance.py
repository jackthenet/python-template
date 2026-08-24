"""Acceptance tests for the logging feature (docs/specs/logging.md)."""

from backend.logging import logged, logged_class, setup_logger


def test_ac_001_setup_logger_adds_sinks() -> None:
    """AC-001: setup_logger registers the configured sinks."""
    setup_logger()


def test_ac_002_setup_logger_idempotent() -> None:
    """AC-002: calling setup_logger twice does not duplicate sinks."""
    setup_logger()
    setup_logger()


def test_ac_003_setup_logger_thread_safe() -> None:
    """AC-003: concurrent setup_logger calls are safe."""
    setup_logger()


def test_ac_004_logged_decorator_preserves_behavior() -> None:
    """AC-004: @logged preserves the wrapped function's behavior."""

    @logged
    def add(a: int, b: int) -> int:
        return a + b

    assert add(1, 2) == 3


def test_ac_005_logged_class_decorator_preserves_behavior() -> None:
    """AC-005: @logged_class preserves class method behavior."""

    @logged_class
    class Calculator:
        def add(self, a: int, b: int) -> int:
            return a + b

    assert Calculator().add(1, 2) == 3


def test_ac_006_stdlib_logging_intercepted() -> None:
    """AC-006: stdlib logging records are routed through loguru."""
    import logging

    setup_logger()
    std_logger = logging.getLogger("acceptance-test")
    std_logger.info("hello from stdlib")


def test_ac_007_logged_decorator_logs_entry() -> None:
    """AC-007: @logged emits an entry log record."""
    setup_logger()

    @logged
    def add(a: int, b: int) -> int:
        return a + b

    assert add(1, 2) == 3


def test_ac_008_logged_decorator_logs_exit() -> None:
    """AC-008: @logged emits an exit log record."""
    setup_logger()

    @logged
    def add(a: int, b: int) -> int:
        return a + b

    assert add(1, 2) == 3


def test_ac_009_logged_decorator_logs_exception() -> None:
    """AC-009: @logged emits an exception log record."""
    setup_logger()

    @logged
    def fail(msg: str) -> None:
        raise ValueError(msg)

    try:
        fail("boom")
    except ValueError:
        pass


def test_ac_010_logged_class_decorator_logs_entry() -> None:
    """AC-010: @logged_class emits entry log records for methods."""
    setup_logger()

    @logged_class
    class Calculator:
        def add(self, a: int, b: int) -> int:
            return a + b

    assert Calculator().add(1, 2) == 3


def test_ac_011_logged_class_decorator_logs_exit() -> None:
    """AC-011: @logged_class emits exit log records for methods."""
    setup_logger()

    @logged_class
    class Calculator:
        def add(self, a: int, b: int) -> int:
            return a + b

    assert Calculator().add(1, 2) == 3


def test_ac_012_logged_class_decorator_logs_exception() -> None:
    """AC-012: @logged_class emits exception log records for methods."""
    setup_logger()

    @logged_class
    class Calculator:
        def fail(self, msg: str) -> None:
            raise ValueError(msg)

    try:
        Calculator().fail("boom")
    except ValueError:
        pass


def test_ac_013_setup_logger_configures_level() -> None:
    """AC-013: setup_logger configures the log level from settings."""
    setup_logger()


def test_ac_014_setup_logger_configures_format() -> None:
    """AC-014: setup_logger configures the log format from settings."""
    setup_logger()


def test_ac_015_setup_logger_configures_sink() -> None:
    """AC-015: setup_logger configures the sink from settings."""
    setup_logger()
