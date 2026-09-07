"""Unit tests for the usermanagement feature edge cases (docs/specs/user-management.md).

Covers EDGE-001 .. EDGE-021.
"""

from __future__ import annotations

import threading
from pathlib import Path

import pydantic
import pytest
from usermanagement_test_helpers import EventCollector, db_url, valid_create

from backend.usermanagement import (
    SqliteUserRepository,
    UserAlreadyExistsError,
    UserCreate,
    UserManager,
    UserNotFoundError,
    UserUpdate,
)


@pytest.fixture
def collector() -> EventCollector:
    return EventCollector()


@pytest.fixture
def repo(tmp_path: Path) -> SqliteUserRepository:
    return SqliteUserRepository(db_url(tmp_path))


@pytest.fixture
def manager(repo: SqliteUserRepository, collector: EventCollector) -> UserManager:
    return UserManager(repo, event_bus=collector)


def test_edge_001_update_email_collision(manager: UserManager) -> None:
    a = manager.create_user(UserCreate(**valid_create(username="aa1")))
    manager.create_user(UserCreate(**valid_create(username="bb2", email="aa1@example.com")))
    with pytest.raises(UserAlreadyExistsError) as exc:
        # b owns aa1@example.com, so taking it must collide (EDGE-001).
        manager.update_user(a.id, UserUpdate(email="aa1@example.com"))
    assert exc.value.field == "email"


def test_edge_002_empty_update_noop(manager: UserManager, collector: EventCollector) -> None:
    user = manager.create_user(UserCreate(**valid_create()))
    updated = manager.update_user(user.id, UserUpdate())
    assert updated.id == user.id
    assert updated.updated_at == user.updated_at
    from backend.usermanagement import UserUpdated

    assert collector.of_type(UserUpdated) == []


def test_edge_003_double_delete(manager: UserManager) -> None:
    user = manager.create_user(UserCreate(**valid_create()))
    manager.delete_user(user.id)
    with pytest.raises(UserNotFoundError):
        manager.delete_user(user.id)


def test_edge_004_deactivate_already_inactive(manager: UserManager, collector: EventCollector) -> None:
    user = manager.create_user(UserCreate(**valid_create()))
    manager.deactivate_user(user.id)
    collector.events.clear()
    result = manager.deactivate_user(user.id)
    assert result.is_active is False
    from backend.usermanagement import UserDeactivated

    assert collector.of_type(UserDeactivated) == []


def test_edge_005_set_role_same(manager: UserManager, collector: EventCollector) -> None:
    user = manager.create_user(UserCreate(**valid_create()))
    collector.events.clear()
    result = manager.set_role(user.id, "member")
    assert result.role == "member"
    from backend.usermanagement import UserRoleChanged

    assert collector.of_type(UserRoleChanged) == []


def test_edge_006_verify_unknown(manager: UserManager) -> None:
    import uuid

    with pytest.raises(UserNotFoundError):
        manager.verify_password(uuid.uuid4(), "whatever-1")


def test_edge_007_repo_creates_parent_dir(tmp_path: Path) -> None:
    url = db_url(tmp_path, name="nested/deeper/users.db")
    repo = SqliteUserRepository(url)
    user = _manager_user(repo)
    assert repo.get_by_id(user.id) is not None


def _manager_user(repo: SqliteUserRepository):
    from datetime import UTC, datetime
    from uuid import uuid4

    from backend.usermanagement import User

    user = User(
        id=uuid4(),
        username="edge007",
        email="edge007@example.com",
        display_name=None,
        role="member",
        password_hash="$argon2id$fake",
        profile_picture_url=None,
        is_active=True,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    return repo.add(user)


def test_edge_008_memory_repository() -> None:
    repo1 = SqliteUserRepository("sqlite:///:memory:")
    repo2 = SqliteUserRepository("sqlite:///:memory:")
    from datetime import UTC, datetime
    from uuid import uuid4

    from backend.usermanagement import User

    user = User(
        id=uuid4(),
        username="edge008",
        email="edge008@example.com",
        display_name=None,
        role="member",
        password_hash="$argon2id$fake",
        profile_picture_url=None,
        is_active=True,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    repo1.add(user)
    assert repo1.get_by_id(user.id) is not None
    assert repo2.get_by_id(user.id) is None


def test_edge_009_empty_roles(tmp_path: Path) -> None:
    repo = SqliteUserRepository(db_url(tmp_path))
    with pytest.raises(ValueError):
        UserManager(repo, roles=())


def test_edge_010_uppercase_role(tmp_path: Path) -> None:
    repo = SqliteUserRepository(db_url(tmp_path))
    with pytest.raises(ValueError):
        UserManager(repo, roles=("Admin",))


def test_edge_011_username_whitespace() -> None:
    with pytest.raises(pydantic.ValidationError):
        UserCreate(**valid_create(username="al ice"))


def test_edge_012_password_no_digit() -> None:
    with pytest.raises(pydantic.ValidationError):
        UserCreate(**valid_create(password="abcdefgh"))


def test_edge_013_password_no_letter() -> None:
    with pytest.raises(pydantic.ValidationError):
        UserCreate(**valid_create(password="12345678"))


def test_edge_014_list_empty(manager: UserManager) -> None:
    assert manager.list_users() == []


def test_edge_015_concurrent_duplicate_create(tmp_path: Path) -> None:
    repo = SqliteUserRepository(db_url(tmp_path))
    manager = UserManager(repo)
    ok: list[str] = []
    errors: list[Exception] = []

    def attempt() -> None:
        try:
            manager.create_user(UserCreate(**valid_create()))
            ok.append("ok")
        except UserAlreadyExistsError as e:
            errors.append(e)

    threads = [threading.Thread(target=attempt) for _ in range(2)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert len(ok) == 1
    assert len(errors) == 1


def test_edge_016_delete_admin_with_two_admins(manager: UserManager) -> None:
    a = manager.create_user(UserCreate(**valid_create(username="root1", role="admin")))
    manager.create_user(UserCreate(**valid_create(username="root2", role="admin", email="root2@example.com")))
    manager.delete_user(a.id)
    with pytest.raises(UserNotFoundError):
        manager.get_user(a.id)


def test_edge_017_update_unknown(manager: UserManager) -> None:
    import uuid

    with pytest.raises(UserNotFoundError):
        manager.update_user(uuid.uuid4(), UserUpdate(display_name="X"))


def test_edge_018_display_name_whitespace() -> None:
    with pytest.raises(pydantic.ValidationError):
        UserCreate(**valid_create(display_name="   "))


def test_edge_019_optional_fields_none(manager: UserManager) -> None:
    created = manager.create_user(UserCreate(**valid_create(display_name=None, profile_picture_url=None)))
    assert created.display_name is None
    assert created.profile_picture_url is None


class _RaisingPublisher:
    def publish(self, event: object) -> None:
        raise RuntimeError("boom")


def test_edge_020_publisher_raises(tmp_path: Path) -> None:
    repo = SqliteUserRepository(db_url(tmp_path))
    manager = UserManager(repo, event_bus=_RaisingPublisher())
    with pytest.raises(RuntimeError):
        manager.create_user(UserCreate(**valid_create()))
    assert len(manager.list_users(include_inactive=True)) == 1


def test_edge_021_case_sensitive_usernames(manager: UserManager) -> None:
    a = manager.create_user(UserCreate(**valid_create(username="Alice", email="a@example.com")))
    b = manager.create_user(UserCreate(**valid_create(username="alice", email="b@example.com")))
    assert a.id != b.id
