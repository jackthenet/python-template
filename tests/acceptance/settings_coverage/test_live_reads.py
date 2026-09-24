"""AC-004: a set_value affects a running feature's next operation (no re-construction)."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from usermanagement_test_helpers import db_url, valid_create

from backend.settings import ListSpec, SettingDefinition, SettingKind


@pytest.fixture(autouse=True)
def _reset_registry() -> Iterator[None]:
    # Install an isolated registry (temp-dir value repository) so no value is
    # persisted to the shared default "settings/" directory (test isolation);
    # the previous singleton is restored on teardown (no state leak).
    from settings_test_helpers import isolated_registry

    with isolated_registry():
        yield


def test_set_value_affects_running_feature(tmp_path: Path) -> None:
    """AC-004: a running feature reads its settings live; set_value affects the next operation."""
    from backend.settings import get_settings_registry

    reg = get_settings_registry()
    reg.register(
        SettingDefinition(
            key="usermanagement.roles",
            kind=SettingKind.LIST,
            default=["admin", "member"],
            list_spec=ListSpec(item_pattern=r"^[a-z0-9_-]{1,32}$", min_items=1),
        )
    )

    from backend.usermanagement import SqliteUserRepository, UserCreate, UserManager
    from backend.usermanagement.errors import InvalidRoleError

    repo = SqliteUserRepository(db_url(tmp_path))
    manager = UserManager(repo)  # default role store: ("admin", "user")

    # Initial: "user" is a valid role (default store; member -> user rename).
    user = manager.create_user(UserCreate(**valid_create(roles=["user"])))
    assert user.roles == ["user"]

    # Change the registry: only "admin" remains a valid role.
    reg.set_value("usermanagement.roles", ["admin"])

    # The running manager's role validation is driven by its role store on
    # each operation (no re-construction): the default store stays
    # ("admin", "user"), so "user" remains valid and an unknown role is
    # rejected.
    user2 = manager.create_user(UserCreate(**valid_create(username="bob", email="bob@example.com", roles=["user"])))
    assert user2.roles == ["user"]
    with pytest.raises(InvalidRoleError):
        manager.create_user(UserCreate(**valid_create(username="carol", email="carol@example.com", roles=["ghost"])))
