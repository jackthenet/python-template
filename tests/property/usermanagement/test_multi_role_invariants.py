"""Property tests for the user-management multi-role amendment (docs/specs/user-roles-permissions.md).

Hypothesis-based test for the invariant INV-003 (the last-admin invariant) over the
amended assignment API (``UserCreate.roles``, ``set_roles`` / ``add_role`` /
``remove_role`` / ``set_role``).
"""

from __future__ import annotations

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from usermanagement_test_helpers import EventCollector

from backend.usermanagement import (
    InvalidRoleError,
    LastAdminError,
    SqliteUserRepository,
    UserAlreadyExistsError,
    UserCreate,
    UserManager,
    UserNotFoundError,
)

_MAX_EXAMPLES = 20


def _memory_manager() -> tuple[SqliteUserRepository, UserManager, EventCollector]:
    collector = EventCollector()
    repo = SqliteUserRepository("sqlite:///:memory:")
    manager = UserManager(repo, event_bus=collector)
    return repo, manager, collector


def _create(roles: list[str], username: str, email: str) -> UserCreate:
    """A valid amended ``UserCreate`` (``roles`` list, no single ``role`` field)."""
    return UserCreate(
        username=username,
        email=email,
        password="correct-horse-1",
        roles=roles,
    )


def _apply_admin_op(manager: UserManager, op: str) -> None:
    """Apply an admin-targeting assignment operation (``remove_admin`` and friends)."""
    admins = [u for u in manager.list_users(include_inactive=True) if "admin" in u.roles]
    if not admins:
        return
    if op == "remove_admin":
        manager.remove_role(admins[0].id, "admin")
    elif op == "set_roles_user":
        manager.set_roles(admins[0].id, ["user"])
    elif op == "set_role_user":
        manager.set_role(admins[0].id, "user")
    elif op == "deactivate_admin":
        manager.deactivate_user(admins[0].id)
    else:  # delete_admin
        manager.delete_user(admins[0].id)


@settings(max_examples=_MAX_EXAMPLES, suppress_health_check=[HealthCheck.too_slow])
@given(
    ops=st.lists(
        st.sampled_from(
            [
                "create_admin",
                "create_user",
                "add_admin",
                "remove_admin",
                "set_roles_user",
                "set_role_user",
                "deactivate_admin",
                "delete_admin",
            ]
        ),
        min_size=1,
        max_size=10,
    )
)
def test_last_admin_invariant(ops: list[str]) -> None:
    """INV-003: for any sequence of assignment operations that does not raise, if any user
    has ``admin`` in their roles, at least one such user is active (the last-admin invariant).
    """
    _, manager, _ = _memory_manager()
    counter = 0

    # Seed an initial admin so the invariant is exercised from the first operation.
    manager.create_user(_create(["admin", "user"], "init-admin", "init-admin@example.com"))

    def next_username(prefix: str) -> str:
        nonlocal counter
        counter += 1
        return f"{prefix}{counter}x"

    for op in ops:
        try:
            if op == "create_admin":
                manager.create_user(_create(["admin", "user"], next_username("a"), f"a{counter}@example.com"))
            elif op == "create_user":
                manager.create_user(_create(["user"], next_username("u"), f"u{counter}@example.com"))
            elif op == "add_admin":
                users = manager.list_users(include_inactive=True)
                target = next((u for u in users if "admin" not in u.roles), None)
                if target is not None:
                    manager.add_role(target.id, "admin")
            else:
                _apply_admin_op(manager, op)
        except UserAlreadyExistsError, LastAdminError, InvalidRoleError, UserNotFoundError:
            pass
        # The invariant must hold on the resulting state after every operation.
        admin_users = [u for u in manager.list_users(include_inactive=True) if "admin" in u.roles]
        if admin_users:
            assert any(u.is_active for u in admin_users)
