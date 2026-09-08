"""AC-010: all existing direct loguru statements are kept unchanged (one-off
facts remain direct loguru).

REQ-010: all existing direct loguru statements are kept unchanged.
"""

from __future__ import annotations

from typing import Any

from logging_coverage_test_helpers import INVENTORY_CLASSES, messages
from backend.eventbus.eventbus import EventBus
from backend.settings.models import SettingDefinition, SettingKind
from backend.settings.registry import SettingsRegistry
from backend.settings.repository import MemoryTemplateRepository


def test_existing_direct_loguru_kept(log_records: list[Any]) -> None:
    """AC-010: the existing direct loguru statements still fire unchanged."""
    # The subjects are traced classes.
    assert getattr(INVENTORY_CLASSES["EventBus"], "__logged_class__", False) is True
    assert getattr(INVENTORY_CLASSES["SettingsRegistry"], "__logged_class__", False) is True

    # EventBus one-off facts.
    bus = EventBus()
    try:
        from eventbus_test_helpers import UserCreated

        bus.publish(UserCreated(user_id="u1", email="e1"))
    finally:
        bus.shutdown()

    # SettingsRegistry one-off facts.
    reg = SettingsRegistry(template_repository=MemoryTemplateRepository())
    reg.register(SettingDefinition(key="x.y", kind=SettingKind.TEXT, default="d"))
    reg.set_value("x.y", "v")

    msgs = messages(log_records)
    # EventBus direct statements (unchanged wording).
    assert any("event bus: published event type" in m for m in msgs), (
        "EventBus 'published event type' direct statement is missing"
    )
    assert any("event bus: shutdown initiated" in m for m in msgs), (
        "EventBus 'shutdown initiated' direct statement is missing"
    )
    # SettingsRegistry direct statements (unchanged wording).
    assert any("setting registered: key=" in m for m in msgs), (
        "SettingsRegistry 'setting registered' direct statement is missing"
    )
    assert any("value set: key=" in m for m in msgs), (
        "SettingsRegistry 'value set' direct statement is missing"
    )
