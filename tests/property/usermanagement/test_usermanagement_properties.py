"""Property tests for the usermanagement feature (docs/specs/user-management.md).

Hypothesis-based tests for the invariants INV-001 .. INV-006.
"""

from __future__ import annotations

import contextlib
from collections.abc import Callable, Iterator
from itertools import count
from uuid import UUID

from hypothesis import HealthCheck, assume, given, settings
from hypothesis import strategies as st
from hypothesis.strategies import SearchStrategy
from usermanagement_test_helpers import EventCollector, valid_create

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
    UserRead,
    UserRoleChanged,
    UserUpdate,
    UserUpdated,
)

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
            min_size=7,
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
        roles=draw(st.sampled_from([["admin"], ["user"]])),
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
    assert created.roles == user.roles
    if user.profile_picture_url is not None:
        assert created.profile_picture_url == user.profile_picture_url
    assert created.is_active is True
    assert created.created_at is not None
    assert created.updated_at is not None


@settings(max_examples=_MAX_EXAMPLES, suppress_health_check=[HealthCheck.too_slow])
@given(p1=_password(), p2=_password())
def test_inv_002_password_round_trip(p1: str, p2: str) -> None:
    assume(p1 != p2)  # changing to the same password keeps the old one valid
    _, manager, _ = _memory_manager()
    created = manager.create_user(UserCreate(**valid_create(password=p1)))
    assert manager.verify_password(created.id, p1) is True
    manager.change_password(created.id, p2)
    assert manager.verify_password(created.id, p2) is True
    assert manager.verify_password(created.id, p1) is False


def _admin_users(manager: UserManager, *, include_inactive: bool) -> list[UserRead]:
    """The users that currently hold the ``admin`` role (in the requested active state)."""
    return [u for u in manager.list_users(include_inactive=include_inactive) if "admin" in u.roles]


def _mutate_first_admin(admins: list[UserRead], mutate: Callable[[UUID], object]) -> None:
    """Apply ``mutate`` to the first admin that accepts it (a ``LastAdminError`` moves to the next)."""
    for admin in admins:
        try:
            mutate(admin.id)
        except LastAdminError:
            continue
        break


def _apply_inv_003_op(manager: UserManager, op: str, counter: Iterator[int]) -> None:
    """Apply one operation of the INV-003 sequence (the same four ops, the same arguments)."""
    if op == "create_admin":
        n = next(counter)
        manager.create_user(
            UserCreate(
                **valid_create(
                    username=f"a{n}x",
                    email=f"a{n}@example.com",
                    roles=["admin", "user"],
                )
            )
        )
    elif op == "create_member":
        n = next(counter)
        manager.create_user(
            UserCreate(
                **valid_create(
                    username=f"m{n}x",
                    email=f"m{n}@example.com",
                )
            )
        )
    elif op == "delete_admin":
        _mutate_first_admin(_admin_users(manager, include_inactive=True), manager.delete_user)
    elif op == "deactivate_admin":
        _mutate_first_admin(_admin_users(manager, include_inactive=False), manager.deactivate_user)


# deadline=1000 is measured, not guessed: the slowest local examples ran 258-270 ms against the
# 200 ms default (seed 101 and the default random seed; this file is byte-identical to
# origin/main, so the flake predates this change). The cost is argon2id password hashing
# (~50-100 ms per create_user, ADR-019) with up to 8 creates per max_size=8 sequence. A hypothesis
# deadline is a harness tolerance on per-example runtime, not a product performance budget (NFR
# budgets are asserted by explicit budget tests), so the strategy and max_size stay untouched.
@settings(
    max_examples=_MAX_EXAMPLES,
    deadline=1000,
    suppress_health_check=[HealthCheck.too_slow],
)
@given(
    ops=st.lists(
        st.sampled_from(["create_admin", "create_member", "delete_admin", "deactivate_admin"]),
        min_size=1,
        max_size=8,
    )
)
def test_inv_003_last_admin_invariant(ops: list[str]) -> None:
    _, manager, _ = _memory_manager()
    counter = count(start=1)
    for op in ops:
        with contextlib.suppress(UserAlreadyExistsError, LastAdminError, UserNotFoundError):
            _apply_inv_003_op(manager, op, counter)
        admin_users = _admin_users(manager, include_inactive=True)
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


def _apply_event_op(manager: UserManager, op: str, user_id: UUID, counter: int) -> type | None:
    """Apply one non-create operation; return the event type it must publish.

    ``None`` means the operation published no event and the correspondence check is skipped:
    an idempotent no-op (REQ-009) or an operation the sequence does not perform.
    """
    if op == "update":
        manager.update_user(user_id, UserUpdate(display_name=f"upd{counter}"))
        return UserUpdated
    if op == "password":
        manager.change_password(user_id, f"pass{counter}-1x")
        return UserPasswordChanged
    if op == "role":
        new_role = "admin" if manager.get_user(user_id).roles == ["user"] else "user"
        manager.set_role(user_id, new_role)
        return UserRoleChanged
    if op == "deactivate":
        was_active = manager.get_user(user_id).is_active
        manager.deactivate_user(user_id)
        return None if not was_active else UserDeactivated  # idempotent no-op: no event (REQ-009)
    if op == "activate":
        was_inactive = not manager.get_user(user_id).is_active
        manager.activate_user(user_id)
        return None if not was_inactive else UserActivated  # idempotent no-op: no event (REQ-009)
    return None


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
            before = len(collector.of_type(UserCreated))
            created = manager.create_user(
                UserCreate(
                    **valid_create(
                        username=f"e{counter}x",
                        email=f"e{counter}@example.com",
                    )
                )
            )
            user_id = created.id
            assert len(collector.of_type(UserCreated)) == before + 1
            continue
        ev = None
        with contextlib.suppress(LastAdminError, InvalidRoleError, UserNotFoundError):
            ev = _apply_event_op(manager, op, user_id, counter)
        if ev is None:
            continue
        events = collector.of_type(ev)
        assert len(events) >= 1
        assert events[-1].user_id == user_id
