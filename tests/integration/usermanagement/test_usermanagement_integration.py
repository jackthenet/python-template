"""Integration tests for the usermanagement feature (docs/specs/user-management.md).

Covers multi-component interactions: the full user lifecycle across
create/read/update/password/role/activation/delete, and events + persistence
across repository instances.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from backend.usermanagement import (
    SqliteUserRepository,
    UserActivated,
    UserCreate,
    UserCreated,
    UserDeactivated,
    UserDeleted,
    UserManager,
    UserNotFoundError,
    UserPasswordChanged,
    UserRoleChanged,
    UserUpdate,
    UserUpdated,
)
from usermanagement_test_helpers import EventCollector, db_url, valid_create


def test_full_user_lifecycle(tmp_path: Path) -> None:
    """The full lifecycle: create → read → update → password → role → deactivate → activate → delete."""
    collector = EventCollector()
    repo = SqliteUserRepository(db_url(tmp_path))
    manager = UserManager(repo, event_bus=collector)

    user = manager.create_user(UserCreate(**valid_create()))
    # Creation is observable through the read API.
    assert manager.get_user(user.id).username == "alice"

    # Update (username stays immutable).
    updated = manager.update_user(user.id, UserUpdate(display_name="Alice A.", email="alice.a@example.com"))
    assert updated.display_name == "Alice A."
    assert updated.email == "alice.a@example.com"
    assert updated.username == "alice"

    # Password.
    manager.change_password(user.id, "new-password-1")
    assert manager.verify_password(user.id, "new-password-1") is True
    assert manager.verify_password(user.id, "correct-horse-1") is False

    # Role.
    promoted = manager.set_role(user.id, "admin")
    assert promoted.role == "admin"

    # Activation.
    inactive = manager.deactivate_user(user.id)
    assert inactive.is_active is False
    assert all(u.id != user.id for u in manager.list_users())
    active = manager.activate_user(user.id)
    assert active.is_active is True

    # Delete.
    manager.delete_user(user.id)
    with pytest.raises(UserNotFoundError):
        manager.get_user(user.id)

    # Every successful mutation published exactly one event.
    assert len(collector.of_type(UserCreated)) == 1
    assert len(collector.of_type(UserPasswordChanged)) == 1
    assert len(collector.of_type(UserRoleChanged)) == 1
    assert len(collector.of_type(UserDeactivated)) == 1
    assert len(collector.of_type(UserActivated)) == 1
    assert len(collector.of_type(UserDeleted)) == 1


def test_events_and_persistence_across_instances(tmp_path: Path) -> None:
    """Users persist across repository instances; events are not persisted."""
    url = db_url(tmp_path)
    collector1 = EventCollector()
    repo1 = SqliteUserRepository(url)
    manager1 = UserManager(repo1, event_bus=collector1)
    user = manager1.create_user(UserCreate(**valid_create()))
    manager1.update_user(user.id, UserUpdate(display_name="persisted"))
    # Both mutations are visible in the collector.
    assert len(collector1.of_type(UserCreated)) == 1
    assert len(collector1.of_type(UserUpdated)) == 1

    # A second instance on the same file sees the persisted state.
    collector2 = EventCollector()
    repo2 = SqliteUserRepository(url)
    manager2 = UserManager(repo2, event_bus=collector2)
    stored = manager2.get_user(user.id)
    assert stored.display_name == "persisted"
    assert stored.email == "alice@example.com"
    # Events are in-process only: the fresh collector starts empty.
    assert collector2.events == []
    # Operating through the second instance publishes through its publisher.
    manager2.delete_user(user.id)
    assert len(collector2.of_type(UserDeleted)) == 1
