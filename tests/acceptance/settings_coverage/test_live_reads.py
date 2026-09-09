"""AC-004: a set_value affects a running feature's next operation (no re-construction)."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest

from backend.settings import ListSpec, SettingDefinition, SettingKind
from settings_test_helpers import make_registry
from usermanagement_test_helpers import db_url, valid_create


@pytest.fixture(autouse=True)
def _reset_registry() -> Iterator[None]:
    from backend.settings import reset_settings_registry

    reset_settings_registry()
    yield
    reset_settings_registry()


def test_set_value_affects_running_feature(tmp_path: Path) -> None:
    """AC-004: a running feature reads its settings live; set_value affects the next operation."""
    reg, _bus = make_registry()
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
    manager = UserManager(repo)  # no explicit roles: the registry value is used

    # Initial: "member" is a valid role (registry default).
    user = manager.create_user(UserCreate(**valid_create(role="member")))
    assert user.role == "member"

    # Change the registry: only "admin" remains a valid role.
    reg.set_value("usermanagement.roles", ["admin"])

    # The next operation uses the new value: "member" is now rejected.
    with pytest.raises(InvalidRoleError):
        manager.create_user(UserCreate(**valid_create(role="member")))
