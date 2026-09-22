"""Integration tests for the permissions thread safety (docs/specs/user-roles-permissions.md).

Covers AC-038 / REQ-027 (NFR-004): concurrent checks and role/grant changes from
multiple threads raise no exception, leave no partial state, and the results are
consistent with the final state.

The ``backend.permissions`` imports are deferred into the test body so the module
collects cleanly before the feature is implemented (RED).
"""

from __future__ import annotations

import tempfile
import threading
from pathlib import Path

from backend.usermanagement import SqliteUserRepository, UserCreate, UserManager


def test_concurrent_checks_and_changes() -> None:
    """AC-038 / REQ-027: concurrent checks and role/grant changes from multiple threads.

    Given concurrent checks and role/grant changes from multiple threads, when they
    are executed, then no exception is raised, no partial state is left, and the
    results are consistent with the final state.
    """
    from backend.permissions import (
        PermissionCatalog,
        PermissionService,
        SqliteGrantRepository,
        SqliteRoleRepository,
        SqliteSystemPrincipalRepository,
    )

    with tempfile.TemporaryDirectory() as tmp:
        db = f"sqlite:///{Path(tmp) / 'permissions.db'}"
        catalog = PermissionCatalog()
        catalog.register_feature(
            "usermanagement",
            {
                "usermanagement.get_user": "Read a user by id",
                "usermanagement.delete_user": "Delete a user account",
            },
        )

        role_repo = SqliteRoleRepository(db)
        role_repo.add("user", None, True)
        grant_repo = SqliteGrantRepository(db)
        system_repo = SqliteSystemPrincipalRepository(db)
        manager = UserManager(SqliteUserRepository("sqlite:///:memory:"))
        user = manager.create_user(
            UserCreate(username="u1", email="u1@example.com", password="correct-horse-1", roles=["user"])
        )
        service = PermissionService(role_repo, grant_repo, system_repo, manager, catalog=catalog)

        perm = "usermanagement.get_user"
        errors: list[BaseException] = []
        barrier = threading.Barrier(4)

        def checker() -> None:
            barrier.wait()
            try:
                for _ in range(25):
                    service.has_permission(user.id, perm)
            except BaseException as exc:
                errors.append(exc)

        def changer() -> None:
            barrier.wait()
            try:
                for i in range(20):
                    if i % 2 == 0:
                        service.grant_permission("user", perm)
                    else:
                        service.revoke_permission("user", perm)
            except BaseException as exc:
                errors.append(exc)

        def role_changer() -> None:
            barrier.wait()
            try:
                for _ in range(10):
                    service.create_role("tmp")
                    service.grant_permission("tmp", perm)
                    service.delete_role("tmp")
            except BaseException as exc:
                errors.append(exc)

        threads = [
            threading.Thread(target=checker),
            threading.Thread(target=checker),
            threading.Thread(target=changer),
            threading.Thread(target=role_changer),
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # No exception from any thread.
        assert not errors, f"unexpected exceptions: {errors}"

        # No partial state: the temporary role is gone (the loop completed) and the
        # user role's grants contain at most the toggled permission.
        listed_roles = {role.role for role in service.list_roles()}
        assert "tmp" not in listed_roles
        final_grants = service.get_role_permissions("user")
        assert final_grants <= frozenset({perm})

        # The final check is consistent with the final grant state.
        assert service.has_permission(user.id, perm) is (perm in final_grants)
