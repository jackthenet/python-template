"""Shared fixtures for the logging feature test suite.

setup_logger() is idempotent (REQ-002), so the in-process suite performs the
real setup exactly once, in a session-scoped fixture. Tests that need a fresh
setup (concurrency invariants, timing budgets, nested log paths) run Python
code in a subprocess via logging_test_helpers.run_python().
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import pytest
from loguru import logger

from backend.logging import setup_logger


@pytest.fixture(scope="session", autouse=True)
def _logging_session_setup(tmp_path_factory: pytest.TempPathFactory) -> Iterator[Any]:
    """Perform the one-time in-process setup before the first test.

    This call configures the real sinks for the whole session. The log file
    lives in a session temp directory so file-content assertions have a stable
    path. Settings is imported lazily so the RED state (module missing) shows
    up as a fixture error rather than a collection error.
    """
    from backend.logging import Settings, register_settings as logging_register
    from backend.settings import get_settings_registry

    session_dir = tmp_path_factory.mktemp("logging_session")
    settings = Settings(log_file=str(session_dir / "logs" / "app.log"), log_level="DEBUG")
    # setup_logger() is no-arg (REQ-014) and reads logging.* from the shared
    # registry (AC-019), so the session's log path/level are set there first.
    registry = get_settings_registry()
    logging_register(registry)
    registry.set_value("logging.log_file", settings.log_file)
    registry.set_value("logging.log_level", settings.log_level)
    setup_logger()
    yield settings


@pytest.fixture(scope="session")
def session_settings(_logging_session_setup: Any) -> Any:
    """The Settings instance used for the session's real setup."""
    return _logging_session_setup


class _Captured:
    """A captured loguru record.

    Exposes the message text via ``str(m)`` and the record fields via
    ``m["level"]``/``m["function"]``/... plus ``m["record"]`` for the whole
    record dict, matching the suite's assertions.
    """

    __slots__ = ("_record",)

    def __init__(self, record: dict[str, Any]) -> None:
        self._record = record

    def __str__(self) -> str:
        return str(self._record.get("message", ""))

    def __getitem__(self, key: str) -> Any:
        if key == "record":
            return self._record
        return self._record[key]


@pytest.fixture
def log_records() -> Iterator[list[Any]]:
    """Capture loguru records for the duration of a test.

    Each record supports ``str(m)`` (the message text) and ``m["level"]`` /
    ``m["record"]`` (record fields), matching the suite's assertions.
    """
    records: list[Any] = []

    def _sink(message: Any) -> None:
        records.append(_Captured(message.record))

    handler_id = logger.add(_sink, level="DEBUG", catch=False)
    try:
        yield records
    finally:
        logger.remove(handler_id)
