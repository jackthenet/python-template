"""Acceptance tests for the usermanagement feature (docs/specs/user-management.md).

These tests verify externally observable behavior only: user creation with
schema + domain validation, uniqueness, Argon2id hashing, reads, updates,
deletion, password and role operations, last-admin protection, activation,
and typed lifecycle events.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from uuid import UUID, uuid4

import pydantic
import pytest
from usermanagement_test_helpers import EventCollector, db_url, valid_create

from backend.usermanagement import (
    InvalidRoleError,
    LastAdminError,
    SqliteUserRepository,
    User,
    UserActivated,
    UserAlreadyExistsError,
    UserCreate,
    UserCreated,
    UserDeactivated,
    UserDeleted,
    UserManager,
    UserNotFoundError,
    UserPasswordChanged,
    UserRead,
    UserRoleChanged,
    UserUpdate,
    UserUpdated,
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


# --- AC-001 .. AC-003: creation, uniqueness ---


def test_ac_001_create_valid_user(manager: UserManager) -> None:
    data = valid_create()
    created = manager.create_user(UserCreate(**data))
    assert isinstance(created, UserRead)
    assert created.username == data["username"]
    assert created.email == data["email"]
    assert created.display_name == data["display_name"]
    assert created.role == data["role"]
    assert created.profile_picture_url == data["profile_picture_url"]
    assert created.is_active is True
    assert isinstance(created.id, UUID)
    assert created.created_at is not None
    assert created.updated_at is not None
    fetched = manager.get_user(created.id)
    assert fetched.id == created.id


def test_ac_002_duplicate_username(manager: UserManager) -> None:
    manager.create_user(UserCreate(**valid_create()))
    with pytest.raises(UserAlreadyExistsError) as exc:
        manager.create_user(UserCreate(**valid_create(email="other@example.com")))
    assert exc.value.field == "username"
    assert len(manager.list_users(include_inactive=True)) == 1


def test_ac_003_duplicate_email_case_insensitive(manager: UserManager) -> None:
    manager.create_user(UserCreate(**valid_create(username="bob", email="Alice@Example.com")))
    with pytest.raises(UserAlreadyExistsError) as exc:
        manager.create_user(UserCreate(**valid_create(username="carol", email="alice@example.com")))
    assert exc.value.field == "email"


# --- AC-004 .. AC-007: schema-level validation ---


def _loc(exc: pytest.ExceptionInfo[pydantic.ValidationError], field: str) -> bool:
    return any(e["loc"] and e["loc"][0] == field for e in exc.value.errors())


def test_ac_004_username_too_short() -> None:
    with pytest.raises(pydantic.ValidationError) as exc:
        UserCreate(**valid_create(username="ab"))
    assert _loc(exc, "username")


def test_ac_005_password_too_short() -> None:
    with pytest.raises(pydantic.ValidationError) as exc:
        UserCreate(**valid_create(password="short1"))
    assert _loc(exc, "password")


def test_ac_006_invalid_email() -> None:
    with pytest.raises(pydantic.ValidationError) as exc:
        UserCreate(**valid_create(email="not-an-email"))
    assert _loc(exc, "email")


def test_ac_007_non_http_profile_picture_url() -> None:
    with pytest.raises(pydantic.ValidationError) as exc:
        UserCreate(**valid_create(profile_picture_url="ftp://example.com/p.png"))
    assert _loc(exc, "profile_picture_url")


# --- AC-008 .. AC-009: configurable role set ---


def test_ac_008_role_not_in_set_create(tmp_path: Path) -> None:
    repo = SqliteUserRepository(db_url(tmp_path))
    manager = UserManager(repo, roles=("admin", "member"))
    with pytest.raises(InvalidRoleError):
        manager.create_user(UserCreate(**valid_create(role="superuser")))


def test_ac_009_custom_role_set(tmp_path: Path) -> None:
    repo = SqliteUserRepository(db_url(tmp_path))
    manager = UserManager(repo, roles=("owner", "worker"))
    assert manager.create_user(UserCreate(**valid_create(role="worker"))).role == "worker"
    with pytest.raises(InvalidRoleError):
        manager.create_user(UserCreate(**valid_create(role="member")))


# --- AC-010: Argon2id hashing ---


def test_ac_010_argon2_hash_stored_not_exposed(manager: UserManager, repo: SqliteUserRepository) -> None:
    data = valid_create()
    created = manager.create_user(UserCreate(**data))
    stored = repo.get_by_id(created.id)
    assert stored is not None
    assert stored.password_hash.startswith("$argon2id$")
    assert stored.password_hash != data["password"]
    assert "password_hash" not in type(created).model_fields
    assert "password_hash" not in created.model_dump()


# --- AC-011 .. AC-014: password operations ---


def test_ac_011_change_password(manager: UserManager) -> None:
    created = manager.create_user(UserCreate(**valid_create()))
    manager.change_password(created.id, "new-password-1")
    assert manager.verify_password(created.id, "new-password-1") is True
    assert manager.verify_password(created.id, "correct-horse-battery") is False


def test_ac_012_verify_password(manager: UserManager) -> None:
    data = valid_create()
    created = manager.create_user(UserCreate(**data))
    assert manager.verify_password(created.id, data["password"]) is True
    assert manager.verify_password(created.id, "wrong-password-1") is False


def test_ac_013_change_password_weak(manager: UserManager) -> None:
    created = manager.create_user(UserCreate(**valid_create()))
    with pytest.raises(pydantic.ValidationError):
        manager.change_password(created.id, "abcdef1")


def test_ac_014_password_ops_unknown_user(manager: UserManager) -> None:
    unknown = uuid4()
    with pytest.raises(UserNotFoundError):
        manager.change_password(unknown, "new-password-1")
    with pytest.raises(UserNotFoundError):
        manager.verify_password(unknown, "whatever-1")


# --- AC-015 .. AC-019: roles and last-admin protection ---


def test_ac_015_set_role(manager: UserManager) -> None:
    created = manager.create_user(UserCreate(**valid_create()))
    result = manager.set_role(created.id, "admin")
    assert result.role == "admin"
    assert manager.get_user(created.id).role == "admin"


def test_ac_016_set_role_not_in_set(manager: UserManager) -> None:
    created = manager.create_user(UserCreate(**valid_create()))
    with pytest.raises(InvalidRoleError):
        manager.set_role(created.id, "superuser")


def test_ac_017_delete_last_admin(manager: UserManager) -> None:
    admin = manager.create_user(UserCreate(**valid_create(username="root", role="admin")))
    with pytest.raises(LastAdminError):
        manager.delete_user(admin.id)
    assert manager.get_user(admin.id).is_active is True


def test_ac_018_deactivate_last_admin(manager: UserManager) -> None:
    admin = manager.create_user(UserCreate(**valid_create(username="root", role="admin")))
    with pytest.raises(LastAdminError):
        manager.deactivate_user(admin.id)


def test_ac_019_demote_last_admin(manager: UserManager) -> None:
    admin = manager.create_user(UserCreate(**valid_create(username="root", role="admin")))
    with pytest.raises(LastAdminError):
        manager.set_role(admin.id, "member")


# --- AC-020 .. AC-021: activation ---


def test_ac_020_deactivate_activate(manager: UserManager) -> None:
    user = manager.create_user(UserCreate(**valid_create()))
    deactivated = manager.deactivate_user(user.id)
    assert deactivated.is_active is False
    assert all(u.id != user.id for u in manager.list_users())
    activated = manager.activate_user(user.id)
    assert activated.is_active is True


def test_ac_021_activate_idempotent(manager: UserManager, collector: EventCollector) -> None:
    user = manager.create_user(UserCreate(**valid_create()))
    result = manager.activate_user(user.id)
    assert result.is_active is True
    assert collector.of_type(UserActivated) == []


# --- AC-022 .. AC-024: reads ---


def test_ac_022_get_user(manager: UserManager) -> None:
    created = manager.create_user(UserCreate(**valid_create()))
    assert manager.get_user(created.id).id == created.id
    with pytest.raises(UserNotFoundError):
        manager.get_user(uuid4())


def test_ac_023_get_user_by_username(manager: UserManager) -> None:
    created = manager.create_user(UserCreate(**valid_create(username="bob")))
    assert manager.get_user_by_username("bob").id == created.id
    with pytest.raises(UserNotFoundError):
        manager.get_user_by_username("ghost")


def test_ac_024_list_users_excludes_inactive(manager: UserManager) -> None:
    a = manager.create_user(UserCreate(**valid_create(username="aa1")))
    b = manager.create_user(UserCreate(**valid_create(username="bb2", email="bb2@example.com")))
    c = manager.create_user(UserCreate(**valid_create(username="cc3", email="cc3@example.com")))
    manager.deactivate_user(c.id)
    active = {u.id for u in manager.list_users()}
    assert active == {a.id, b.id}
    all_users = {u.id for u in manager.list_users(include_inactive=True)}
    assert all_users == {a.id, b.id, c.id}


# --- AC-025: update ---


def test_ac_025_update_user(manager: UserManager) -> None:
    user = manager.create_user(UserCreate(**valid_create()))
    updated = manager.update_user(user.id, UserUpdate(email="new@example.com", display_name="New Name"))
    assert updated.email == "new@example.com"
    assert updated.display_name == "New Name"
    assert updated.username == user.username
    assert updated.id == user.id
    assert updated.created_at == user.created_at
    assert updated.updated_at > user.updated_at


# --- AC-026: delete ---


def test_ac_026_delete_user(manager: UserManager) -> None:
    user = manager.create_user(UserCreate(**valid_create()))
    manager.delete_user(user.id)
    with pytest.raises(UserNotFoundError):
        manager.get_user(user.id)
    assert all(u.id != user.id for u in manager.list_users(include_inactive=True))


# --- AC-027 .. AC-028: persistence and repository swappability ---


def test_ac_027_persistence_across_instances(tmp_path: Path) -> None:
    url = db_url(tmp_path)
    repo1 = SqliteUserRepository(url)
    manager1 = UserManager(repo1)
    created = manager1.create_user(UserCreate(**valid_create()))
    repo2 = SqliteUserRepository(url)
    manager2 = UserManager(repo2)
    assert manager2.get_user(created.id).username == created.username


class _FakeUserStore:
    """An in-memory, non-SQLite ``UserRepository`` implementation (AC-028)."""

    def __init__(self) -> None:
        self._users: dict[UUID, User] = {}

    def add(self, user: User) -> User:
        if any(u.username == user.username for u in self._users.values()):
            raise UserAlreadyExistsError(field="username")
        if any(u.email == user.email.lower() for u in self._users.values()):
            raise UserAlreadyExistsError(field="email")
        self._users[user.id] = user
        return user

    def get_by_id(self, user_id: UUID) -> User | None:
        return self._users.get(user_id)

    def get_by_username(self, username: str) -> User | None:
        return next((u for u in self._users.values() if u.username == username), None)

    def get_by_email(self, email: str) -> User | None:
        return next((u for u in self._users.values() if u.email == email.lower()), None)

    def update(self, user: User) -> User:
        self._users[user.id] = user
        return user

    def delete(self, user_id: UUID) -> None:
        self._users.pop(user_id, None)

    def list_all(self, include_inactive: bool = False) -> Sequence[User]:
        users = list(self._users.values())
        return users if include_inactive else [u for u in users if u.is_active]

    def count_active_by_role(self, role: str) -> int:
        return sum(1 for u in self._users.values() if u.role == role and u.is_active)


def test_ac_028_service_with_fake_repository() -> None:
    from backend.usermanagement import UserRepository

    # _FakeUserStore must precede UserRepository in the bases: otherwise the
    # ABC's own abstract-method namespace shadows the fake's implementations
    # in the MRO and instantiation fails (all methods stay abstract).
    class FakeRepository(_FakeUserStore, UserRepository):
        pass

    manager = UserManager(FakeRepository())
    a = manager.create_user(UserCreate(**valid_create(username="aa1", role="admin")))
    b = manager.create_user(UserCreate(**valid_create(username="bb2", email="bb2@example.com")))
    assert manager.get_user(a.id).username == "aa1"
    assert manager.get_user_by_username("bb2").id == b.id
    assert {u.id for u in manager.list_users()} == {a.id, b.id}
    manager.update_user(b.id, UserUpdate(display_name="Bee"))
    manager.change_password(b.id, "new-password-1")
    assert manager.verify_password(b.id, "new-password-1") is True
    manager.deactivate_user(b.id)
    manager.activate_user(b.id)
    manager.set_role(b.id, "admin")
    manager.delete_user(b.id)
    remaining = manager.list_users(include_inactive=True)
    assert len(remaining) == 1
    assert remaining[0].id == a.id


# --- AC-029: error hierarchy ---


def test_ac_029_error_hierarchy_context() -> None:
    from backend.usermanagement import (
        InvalidRoleError as _InvalidRoleError,
    )
    from backend.usermanagement import (
        LastAdminError as _LastAdminError,
    )
    from backend.usermanagement import (
        UserAlreadyExistsError as _UserAlreadyExistsError,
    )
    from backend.usermanagement import (
        UserManagerError,
    )
    from backend.usermanagement import (
        UserNotFoundError as _UserNotFoundError,
    )

    assert issubclass(UserManagerError, Exception)
    for cls in (
        _UserAlreadyExistsError,
        _UserNotFoundError,
        _InvalidRoleError,
        _LastAdminError,
    ):
        assert issubclass(cls, UserManagerError)
    exists = _UserAlreadyExistsError(field="username")
    assert exists.field == "username"
    role_err = _InvalidRoleError(role="superuser", allowed=frozenset({"admin", "member"}))
    assert role_err.role == "superuser"
    assert role_err.allowed == frozenset({"admin", "member"})


# --- AC-030 .. AC-038: typed lifecycle events ---


def test_ac_030_event_user_created(manager: UserManager, collector: EventCollector) -> None:
    data = valid_create()
    created = manager.create_user(UserCreate(**data))
    events = collector.of_type(UserCreated)
    assert len(events) == 1
    assert events[0].user_id == created.id
    assert events[0].username == created.username
    assert events[0].email == created.email
    assert events[0].role == created.role


def test_ac_031_event_user_updated(manager: UserManager, collector: EventCollector) -> None:
    user = manager.create_user(UserCreate(**valid_create()))
    manager.update_user(user.id, UserUpdate(email="changed@example.com"))
    events = collector.of_type(UserUpdated)
    assert len(events) == 1
    assert events[0].user_id == user.id
    assert "email" in events[0].changed_fields


def test_ac_032_event_user_deleted(manager: UserManager, collector: EventCollector) -> None:
    user = manager.create_user(UserCreate(**valid_create()))
    manager.delete_user(user.id)
    events = collector.of_type(UserDeleted)
    assert len(events) == 1
    assert events[0].user_id == user.id
    assert events[0].username == user.username


def test_ac_033_event_password_changed(manager: UserManager, collector: EventCollector) -> None:
    user = manager.create_user(UserCreate(**valid_create()))
    manager.change_password(user.id, "new-password-1")
    events = collector.of_type(UserPasswordChanged)
    assert len(events) == 1
    assert events[0].user_id == user.id


def test_ac_034_event_role_changed(manager: UserManager, collector: EventCollector) -> None:
    user = manager.create_user(UserCreate(**valid_create()))
    manager.set_role(user.id, "admin")
    events = collector.of_type(UserRoleChanged)
    assert len(events) == 1
    assert events[0].user_id == user.id
    assert events[0].old_role == "member"
    assert events[0].new_role == "admin"


def test_ac_035_event_activated(manager: UserManager, collector: EventCollector) -> None:
    user = manager.create_user(UserCreate(**valid_create()))
    manager.deactivate_user(user.id)
    before = len(collector.of_type(UserActivated))
    manager.activate_user(user.id)
    events = collector.of_type(UserActivated)
    assert len(events) == before + 1
    assert events[-1].user_id == user.id


def test_ac_036_event_deactivated(manager: UserManager, collector: EventCollector) -> None:
    user = manager.create_user(UserCreate(**valid_create()))
    before = len(collector.of_type(UserDeactivated))
    manager.deactivate_user(user.id)
    events = collector.of_type(UserDeactivated)
    assert len(events) == before + 1
    assert events[-1].user_id == user.id


def test_ac_037_no_event_on_failure(manager: UserManager, collector: EventCollector) -> None:
    manager.create_user(UserCreate(**valid_create()))
    collector.events.clear()
    with pytest.raises(UserAlreadyExistsError):
        manager.create_user(UserCreate(**valid_create(email="other@example.com")))
    assert collector.events == []


def test_ac_038_no_publisher(tmp_path: Path) -> None:
    repo = SqliteUserRepository(db_url(tmp_path))
    manager = UserManager(repo)
    created = manager.create_user(UserCreate(**valid_create()))
    manager.update_user(created.id, UserUpdate(display_name="X"))
    manager.delete_user(created.id)
    assert manager.list_users(include_inactive=True) == []
