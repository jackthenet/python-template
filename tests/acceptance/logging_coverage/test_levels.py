"""AC-008: traced classes use semantic log levels reflecting event significance
(DEBUG for routine tracing, INFO for significant lifecycle, WARNING for
recoverable issues, ERROR for failures), not only DEBUG.

REQ-008 / NFR-003 / NFR-005: log levels reflect semantic significance;
significant lifecycle events are logged at INFO/WARNING/ERROR, not only DEBUG.
"""

from __future__ import annotations

import contextlib
import time
from typing import Any

from logging_coverage_test_helpers import (
    INVENTORY_CLASSES,
    level_name,
)

from backend.eventbus.eventbus import EventBus
from backend.settings.models import SettingDefinition, SettingKind
from backend.settings.registry import SettingsRegistry
from backend.settings.repository import MemoryTemplateRepository


def test_semantic_log_levels(log_records: list[Any]) -> None:
    """AC-008: significant lifecycle events on traced classes are logged at a
    semantic level (WARNING/ERROR), not only DEBUG."""
    # The subjects are traced classes.
    assert getattr(INVENTORY_CLASSES["EventBus"], "__logged_class__", False) is True
    assert getattr(INVENTORY_CLASSES["SettingsRegistry"], "__logged_class__", False) is True

    # EventBus: a failing handler is a recoverable failure logged at ERROR.
    bus = EventBus()
    try:
        from eventbus_test_helpers import UserCreated

        def bad_handler(event: Any) -> None:
            raise RuntimeError("handler boom")

        bus.subscribe(UserCreated, bad_handler)
        bus.publish(UserCreated(user_id="u1", email="e1"))
        # Wait for the background worker to dispatch (and log the handler error).
        deadline = time.monotonic() + 5.0
        while time.monotonic() < deadline:
            if any(level_name(r) == "ERROR" for r in log_records):
                break
            time.sleep(0.01)
    finally:
        bus.shutdown()
    assert any(level_name(r) == "ERROR" for r in log_records), (
        "expected an ERROR-level record for the failing handler"
    )

    # SettingsRegistry: a duplicate registration is a recoverable issue logged at
    # WARNING (the implementation logs the warning and then raises
    # SettingsRegistrationError, which the test catches).
    from backend.settings.exceptions import SettingsRegistrationError

    reg = SettingsRegistry(template_repository=MemoryTemplateRepository())
    definition = SettingDefinition(key="x.y", kind=SettingKind.TEXT, default="d")
    reg.register(definition)
    with contextlib.suppress(SettingsRegistrationError):
        reg.register(definition)  # duplicate
    assert any(
        level_name(r) == "WARNING" and "duplicate registration" in str(r) for r in log_records
    ), "expected a WARNING-level record for the duplicate registration"

    # Not only DEBUG: at least one non-DEBUG record was produced.
    assert any(level_name(r) != "DEBUG" for r in log_records)
