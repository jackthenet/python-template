"""Integration tests for the logging feature (docs/specs/logging.md).

Covers multi-component interactions: a stdlib logging record, a loguru line,
and a @logged call must all reach the file sink through the same setup.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from logging_test_helpers import wait_for_file_content
from loguru import logger

from backend.logging import logged

_EXPECTED_RESULT = 7


def test_stdlib_loguru_decorator_pipeline(session_settings: Any) -> None:
    """A stdlib record, a loguru line, and a @logged call all reach the file sink."""
    import logging

    @logged
    def integration_work_fn() -> int:
        return _EXPECTED_RESULT

    assert integration_work_fn() == _EXPECTED_RESULT
    logging.getLogger("integration").info("integration stdlib line")
    logger.info("integration loguru line")

    log_file = Path(session_settings.log_file)
    assert wait_for_file_content(log_file, lambda c: "integration stdlib line" in c, timeout=5)
    assert wait_for_file_content(log_file, lambda c: "integration loguru line" in c, timeout=5)
    assert wait_for_file_content(log_file, lambda c: "integration_work_fn" in c and "<<" in c, timeout=5)
