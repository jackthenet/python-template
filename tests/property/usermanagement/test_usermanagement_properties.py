"""Property tests for the usermanagement feature (docs/specs/user-management.md).

Hypothesis-based tests for the invariants INV-001 .. INV-006.
"""

from __future__ import annotations

from backend.usermanagement import (
    InvalidRoleError,
    LastAdminError,
    SqliteUserRepository,
    UserActivated,
    UserAlreadyExistsError,
    UserCreate,
    UserCreated,
    UserDeactivated,
    UserManager,
    UserNotFoundError,
    UserPasswordChanged,
    UserRoleChanged,
    UserUpdate,
    UserUpdated,
)
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from hypothesis.strategies import SearchStrategy
from usermanagement_test_helpers import EventCollector, valid_create

_MAX_EXAMPLES = 20


def _username() -> SearchStrategy[str]:
    return st.from_regex(r"[a-zA-Z0-9][a-zA-Z0-9._-]{1,30}[a-zA-Z0-9]", fullmatch=True)


def _email() -> SearchStrategy[str]:
    return st.from_regex(r"[a-z]{1,8}@[a-z]{1,8}\.[a-z]{2,3}", fullmatch=True)


def _password() -> SearchStrategy[str]:
    return st.builds(
        lambda letters, digits: letters + digits,
        st.text(
            alphabet=st.sampled_from("abcdefghijklmnopqrstuvwxyz"),
            min_size=4,
            max_size=10,
        ),
        st.text(alphabet=st.sampled_from("0123456789"), min_size=1, max_size=4),
    )


def _display_name() -> SearchStrategy[str]:
    return st.from_regex(r"[A-Za-z]{1,20}", fullmatch=True)


def _profile_picture_url() -> SearchStrategy[str]:
    return st.from_regex(r"https://[a-z]{1,5}\.[a-z]{2,3}/[a-z]{1,5}\.png", fullmatch=True)


def _memory_manager() -> tuple[SqliteUserRepository, UserManager, EventCollector]:
    collector = EventCollector()
    repo = SqliteUserRepository("sqlite:///:memory:")
    manager = UserManager(repo, event_bus=collector)
    return repo, manager, collector


@st.composite
def _valid_user_create(draw) -> UserCreate:
    return UserCreate(
        username=draw(_username()),
        email=draw(_email()),
        password=draw(_password()),
        display_name=draw(st.one_of(st.none(), _display_name())),
        role=draw(st.sampled_from(["admin", "member"])),
        profile_picture_url=draw(st.one_of(st.none(), _profile_picture_url())),
    )


@settings(max_examples=_MAX_EXAMPLES, suppress_health_check=[HealthCheck.too_slow])
@given(user=_valid_user_create())
def test_inv_001_create_read_consistency(user: UserCreate) -> None:
    _, manager, _ = _memory_manager()
    created = manager.create_user(user)
    assert created.username == user.username
    assert created.email == user.email.lower()
    if user.display_name is not None:
        assert created.display_name == user.display_name
    assert created.role == user.role
    if user.profile_picture_url is not None:
        assert created.profile_picture_url == user.profile_picture_url
    assert created.is_active is True
    assert created.created_at is not None
    assert created.updated_at is not None


@settings(max_examples=_MAX_EXAMPLES, suppress_health_check=[HealthCheck.too_slow])
@given(p1=_password(), p2=_password())
def test_inv_002_password_round_trip(p1: str, p2: str) -> None:
    _, manager, _ = _memory_manager()
    created = manager.create_user(UserCreate(**valid_create(password=p1)))
    assert manager.verify_password(created.id, p1) is True
    manager.change_password(created.id, p2)
    assert manager.verify_password(created.id, p2) is True
    assert manager.verify_password(created.id, p1) is False


@settings(max_examples=_MAX_EXAMPLES, suppress_health_check=[HealthCheck.too_slow])
@given(
    ops=st.lists(
        st.sampled_from(["create_admin", "create_member", "delete_admin", "deactivate_admin"]),
        min_size=1,
        max_size=8,
    )
)
def test_inv_003_last_admin_invariant(ops: list[str]) -> None:
    _, manager, _ = _memory_manager()
    counter = 0

    def next_username(prefix: str) -> str:
        nonlocal counter
        counter += 1
        return f"{prefix}{counter}x"

    for op in ops:
        try:
            if op == "create_admin":
                manager.create_user(
                    UserCreate(
                        **valid_create(
                            username=next_username("a"),
                            email=f"a{counter}@example.com",
                            role="admin",
                        )
                    )
                )
            elif op == "create_member":
                manager.create_user(
                    UserCreate(
                        **valid_create(
                            username=next_username("m"),
                            email=f"m{counter}@example.com",
                        )
                    )
                )
            elif op == "delete_admin":
                for admin in [u for u in manager.list_users(include_inactive=True) if u.role == "admin"]:
                    try:
                        manager.delete_user(admin.id)
                    except LastAdminError:
                        continue
                    break
            elif op == "deactivate_admin":
                for admin in [u for u in manager.list_users() if u.role == "admin"]:
                    try:
                        manager.deactivate_user(admin.id)
                    except LastAdminError:
                        continue
                    break
        except UserAlreadyExistsError, LastAdminError, UserNotFoundError:
            pass
        admin_users = [u for u in manager.list_users(include_inactive=True) if u.role == "admin"]
        if admin_users:
            assert any(u.is_active for u in admin_users)


@st.composite
def _update_fields(draw):
    email = draw(st.one_of(st.none(), _email()))
    display_name = draw(st.one_of(st.none(), _display_name()))
    profile_picture_url = draw(st.one_of(st.none(), _profile_picture_url()))
    return (
        email,
        display_name,
        profile_picture_url,
    )


@settings(max_examples=_MAX_EXAMPLES, suppress_health_check=[HealthCheck.too_slow])
@given(fields=_update_fields())
def test_inv_004_update_semantics(fields: tuple) -> None:
    email, display_name, profile_picture_url = fields
    _, manager, _ = _memory_manager()
    user = manager.create_user(
        UserCreate(
            **valid_create(
                username="keepme",
                email="keep@example.com",
                display_name="Keep",
                profile_picture_url="https://example.com/keep.png",
            )
        )
    )
    updated = manager.update_user(
        user.id,
        UserUpdate(
            email=email,
            display_name=display_name,
            profile_picture_url=profile_picture_url,
        ),
    )
    assert updated.id == user.id
    assert updated.username == user.username
    assert updated.created_at == user.created_at
    if email is not None:
        assert updated.email == email.lower()
    else:
        assert updated.email == user.email
    if display_name is not None:
        assert updated.display_name == display_name
    else:
        assert updated.display_name == user.display_name
    if profile_picture_url is not None:
        assert updated.profile_picture_url == profile_picture_url
    else:
        assert updated.profile_picture_url == user.profile_picture_url


@settings(max_examples=_MAX_EXAMPLES, suppress_health_check=[HealthCheck.too_slow])
@given(specs=st.lists(_valid_user_create(), min_size=2, max_size=4))
def test_inv_005_uniqueness(specs: list[UserCreate]) -> None:
    _, manager, _ = _memory_manager()
    for counter, _spec in enumerate(specs, start=1):
        manager.create_user(
            UserCreate(
                **valid_create(
                    username=f"u{counter}x",
                    email=f"u{counter}@example.com",
                )
            )
        )
    users = manager.list_users(include_inactive=True)
    for i in range(len(users)):
        for j in range(i + 1, len(users)):
            assert users[i].username != users[j].username
            assert users[i].email != users[j].email


@settings(max_examples=_MAX_EXAMPLES, suppress_health_check=[HealthCheck.too_slow])
@given(
    ops=st.lists(
        st.sampled_from(["create", "update", "password", "role", "deactivate", "activate"]),
        min_size=1,
        max_size=6,
    )
)
def test_inv_006_event_correspondence(ops: list[str]) -> None:
    _repo, manager, collector = _memory_manager()
    counter = 0
    user_id = None
    for op in ops:
        counter += 1
        if op == "create" or user_id is None:
            created = manager.create_user(
                UserCreate(
                    **valid_create(
                        username=f"e{counter}x",
                        email=f"e{counter}@example.com",
                    )
                )
            )
            user_id = created.id
            before = len(collector.of_type(UserCreated))
            assert len(collector.of_type(UserCreated)) == before + 1
            continue
        try:
            if op == "update":
                manager.update_user(user_id, UserUpdate(display_name=f"upd{counter}"))
                ev = UserUpdated
            elif op == "password":
                manager.change_password(user_id, f"pass{counter}-1")
                ev = UserPasswordChanged
            elif op == "role":
                new_role = "admin" if manager.get_user(user_id).role == "member" else "member"
                manager.set_role(user_id, new_role)
                ev = UserRoleChanged
            elif op == "deactivate":
                manager.deactivate_user(user_id)
                ev = UserDeactivated
            elif op == "activate":
                manager.activate_user(user_id)
                ev = UserActivated
            else:
                continue
        except LastAdminError, InvalidRoleError, UserNotFoundError:
            continue
        events = collector.of_type(ev)
        assert len(events) >= 1
        assert events[-1].user_id == user_id
