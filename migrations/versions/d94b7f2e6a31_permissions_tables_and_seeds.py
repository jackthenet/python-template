"""permissions persistence (roles, role_permissions, system_principal_permissions + seeds)

Schema migration for the permissions feature (REQ-022, ADR-069): creates the
``roles``, ``role_permissions``, and ``system_principal_permissions`` tables
(SQLModel/SQLite, behind the repository ABCs) and seeds the built-in roles
(``admin`` / ``user``, both ``is_builtin=True``) and the bootstrap system set
into ``system_principal_permissions``. Idempotent: table creation is guarded
by a table-name inspection (an ORM-bootstrapped database is a no-op) and the
seeds use ``INSERT OR IGNORE`` (re-seeding is a no-op).

Revision ID: d94b7f2e6a31
Revises: eace2f772150
Create Date: 2026-09-23 12:34:05.000000

"""

from collections.abc import Sequence
from datetime import UTC, datetime

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d94b7f2e6a31"
down_revision: str | Sequence[str] | None = "eace2f772150"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# The built-in roles seeded by the migration (REQ-007, REQ-022).
BUILTIN_ROLES: tuple[str, ...] = ("admin", "user")

# The bootstrap system set seeded into ``system_principal_permissions``
# (spec D10; the default of ``permissions.system_principal``).
BOOTSTRAP_SYSTEM_PERMISSIONS: tuple[str, ...] = (
    "usermanagement.get_user",
    "usermanagement.verify_password",
    "usermanagement.change_password",
    "settings.register",
    "settings.register_feature",
    "mail.send_email",
    "mail.send_password_reset_email",
    "mail.send_email_verification_email",
    "sessionmanagement.cleanup_expired",
)


def _existing_tables() -> set[str]:
    """The table names in the migrated database."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return set(inspector.get_table_names())


def upgrade() -> None:
    tables = _existing_tables()
    if "roles" not in tables:
        op.create_table(
            "roles",
            sa.Column("role", sa.String(), nullable=False),
            sa.Column("description", sa.String(), nullable=True),
            sa.Column("is_builtin", sa.Boolean(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint("role"),
        )
    if "role_permissions" not in tables:
        op.create_table(
            "role_permissions",
            sa.Column("role", sa.String(), nullable=False),
            sa.Column("permission", sa.String(), nullable=False),
            sa.Column("granted_at", sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(["role"], ["roles.role"]),
            sa.PrimaryKeyConstraint("role", "permission"),
        )
    if "system_principal_permissions" not in tables:
        op.create_table(
            "system_principal_permissions",
            sa.Column("permission", sa.String(), nullable=False),
            sa.Column("granted_at", sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint("permission"),
        )
    # Seeds (idempotent: INSERT OR IGNORE; a re-run or an ORM-bootstrapped
    # database is a no-op).
    bind = op.get_bind()
    now = datetime.now(UTC)
    for role in BUILTIN_ROLES:
        bind.execute(
            sa.text(
                "INSERT OR IGNORE INTO roles "
                "(role, description, is_builtin, created_at) "
                "VALUES (:role, :description, :is_builtin, :created_at)"
            ),
            {"role": role, "description": None, "is_builtin": True, "created_at": now},
        )
    for permission in BOOTSTRAP_SYSTEM_PERMISSIONS:
        bind.execute(
            sa.text(
                "INSERT OR IGNORE INTO system_principal_permissions "
                "(permission, granted_at) "
                "VALUES (:permission, :granted_at)"
            ),
            {"permission": permission, "granted_at": now},
        )


def downgrade() -> None:
    op.drop_table("system_principal_permissions")
    op.drop_table("role_permissions")
    op.drop_table("roles")
