"""Contract tests for the permissions feature (docs/specs/user-roles-permissions.md).

NFR-001 (REQ-029): a check (``has_permission`` / ``require_permission``)
completes in < 5 ms (median) in-process, including the user/role/grant
SQLite lookups and the ``@logged`` tracing overhead, measured against a
local SQLite database with the shared logging feature at the default INFO
level and the synchronous console sink active.

The ``backend.permissions`` imports are deferred into the test body so the
module collects cleanly before the feature is implemented (RED).
"""

from __future__ import annotations

import statistics
import time
from pathlib import Path

from settings_test_helpers import install_isolated_registry

from backend.logging import register_settings as register_logging_settings
from backend.usermanagement import SqliteUserRepository, UserCreate, UserManager

_CHECK_BUDGET_MS = 5.0
_WARMUP_RUNS = 1
_SAMPLE_RUNS = 21
_PERMISSION = "mail.send_email"


def test_check_latency_under_5ms_median(tmp_path: Path) -> None:
    """AC-040 / NFR-001 / REQ-029: the check completes in < 5 ms (median).

    Given the measurement context (local SQLite, the shared logging feature at
    the default INFO level with the synchronous console sink active, ``@logged``
    tracing on), when a check is measured, then it completes in < 5 ms (median).
    """
    from alembic import command
    from alembic.config import Config as AlembicConfig

    from backend.permissions import (
        PermissionCatalog,
        PermissionService,
        SqliteGrantRepository,
        SqliteRoleRepository,
        SqliteSystemPrincipalRepository,
    )

    # Measurement context: the shared logging feature at the default INFO level.
    # A logging.* change reconfigures the sinks at runtime (including the
    # synchronous console sink). The isolated registry (temp-dir value
    # repository) keeps the measurement away from the shared default
    # "settings/" directory (test isolation).
    shared = install_isolated_registry()
    if not shared.has("logging.log_level"):
        register_logging_settings(shared)
    previous = shared.get_value("logging.log_level")
    shared.set_value("logging.log_level", "INFO")
    try:
        root = Path(__file__).resolve().parents[3]
        db_path = tmp_path / "app.db"
        cfg = AlembicConfig(str(root / "alembic.ini"))
        cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
        command.upgrade(cfg, "head")
        url = f"sqlite:///{db_path}"

        # Local SQLite: the migrated permissions tables + a user with the
        # non-admin role (zero permissions; the check denies).
        user_repo = SqliteUserRepository(url)
        manager = UserManager(user_repo)
        user = manager.create_user(
            UserCreate(
                username="perf-user",
                email="perf@example.com",
                password="correct-horse-1",
                roles=["user"],
            )
        )

        catalog = PermissionCatalog()
        catalog.register_feature(
            "mail",
            {
                "mail.send_email": "Send an email via the shared mail service",
                "mail.send_password_reset_email": "Send the built-in password-reset email",
                "mail.send_email_verification_email": "Send the built-in email-verification email",
            },
        )

        service = PermissionService(
            SqliteRoleRepository(url),
            SqliteGrantRepository(url),
            SqliteSystemPrincipalRepository(url),
            manager,
            catalog=catalog,
        )

        # Warm-up: the first call opens the SQLite connections.
        for _ in range(_WARMUP_RUNS):
            service.has_permission(user.id, _PERMISSION)

        samples: list[float] = []
        for _ in range(_SAMPLE_RUNS):
            t0 = time.perf_counter()
            service.has_permission(user.id, _PERMISSION)
            samples.append((time.perf_counter() - t0) * 1000)
    finally:
        shared.set_value("logging.log_level", previous)
    assert statistics.median(samples) < _CHECK_BUDGET_MS, (
        f"check median {statistics.median(samples):.3f} ms exceeds 5 ms budget"
    )
