"""Integration tests for the logging feature (docs/specs/logging.md).

Covers multi-component interactions: a record emitted on the feature's own logger,
a record emitted on a foreign (third-party) logger that reaches the pipeline only
through the root forwarding handler, and a @logged call must all reach the file
sink through the same setup. The function name keeps the historical wording of the
matrix row; the loguru line it once asserted is retired with the backend
(docs/specs/structlog-logging.md).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from logging_test_helpers import wait_for_file_content

from backend.logging import logged

_EXPECTED_RESULT = 7


def test_stdlib_loguru_decorator_pipeline(session_settings: Any) -> None:
    """A feature record, a forwarded foreign record, and a @logged call all reach the file sink."""
    import logging

    @logged
    def integration_work_fn() -> int:
        return _EXPECTED_RESULT

    assert integration_work_fn() == _EXPECTED_RESULT
    logging.getLogger("integration").info("integration stdlib line")
    logging.getLogger("integration.third_party").info("integration foreign line")

    log_file = Path(session_settings.log_file)
    assert wait_for_file_content(log_file, lambda c: "integration stdlib line" in c, timeout=15)
    assert wait_for_file_content(log_file, lambda c: "integration foreign line" in c, timeout=15)
    assert wait_for_file_content(log_file, lambda c: "integration_work_fn" in c and "<<" in c, timeout=15)
