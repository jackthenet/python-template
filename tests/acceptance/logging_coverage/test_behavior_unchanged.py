"""AC-016: tracing MUST NOT change public API signatures, observable behavior, or
business logic (observability only).

REQ-016 / NFR-004: the public API of traced classes is unchanged — tracing adds
observability without altering signatures or behavior.
"""

from __future__ import annotations

import inspect
import uuid
from typing import Any

from logging_coverage_test_helpers import INVENTORY_CLASSES

from backend.eventbus.eventbus import EventBus
from backend.settings.models import SettingDefinition, SettingKind
from backend.settings.registry import SettingsRegistry
from backend.settings.repository import MemoryTemplateRepository
from backend.usermanagement.errors import UserNotFoundError
from backend.usermanagement.models import UserCreate
from backend.usermanagement.repository import SqliteUserRepository
from backend.usermanagement.service import UserManager


def _param_names(func: Any) -> list[str]:
    sig = inspect.signature(func)
    return [p for p in sig.parameters if p != "self"]


def test_tracing_does_not_change_behavior(log_records: list[Any], tmp_path: Any) -> None:
    """AC-016 / NFR-004: public API signatures and observable behavior are unchanged
    by tracing."""
    # The subjects are traced classes.
    for name in ("EventBus", "SettingsRegistry", "UserManager"):
        assert getattr(INVENTORY_CLASSES[name], "__logged_class__", False) is True, (
            f"{name} is not traced"
        )

    # Public API signatures are unchanged.
    assert _param_names(EventBus.publish) == ["event"]
    assert _param_names(SettingsRegistry.set_value) == ["key", "value"]
    assert _param_names(UserManager.create_user) == ["data"]

    # Observable behavior is unchanged: SettingsRegistry set/get round-trip.
    reg = SettingsRegistry(template_repository=MemoryTemplateRepository())
    reg.register(SettingDefinition(key="x.y", kind=SettingKind.TEXT, default="default"))
    reg.set_value("x.y", "changed")
    assert reg.get_value("x.y") == "changed"

    # Observable behavior is unchanged: EventBus deliver to a subscriber.
    from eventbus_test_helpers import UserCreated, wait_for

    bus = EventBus()
    received: list[Any] = []

    def _handler(e: Any) -> None:
        received.append(e)

    try:
        bus.subscribe(UserCreated, _handler)
        bus.publish(UserCreated(user_id="u1", email="e1"))
        assert wait_for(lambda: len(received) == 1)
    finally:
        bus.shutdown()

    # Observable behavior is unchanged: UserManager create + a missing read raises.
    manager = UserManager(SqliteUserRepository(f"sqlite:///{tmp_path}/behav.db"))
    user = manager.create_user(
        UserCreate(username="alice", email="alice@example.com", password="s3cret!x", role="member")
    )
    assert manager.get_user(user.id).username == "alice"
    try:
        manager.get_user(uuid.uuid4())
        raise AssertionError("expected UserNotFoundError")
    except UserNotFoundError:
        pass
