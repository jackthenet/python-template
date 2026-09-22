"""usermanagement multi-role amendment (member to user; role column to roles list)

Data migration for the multi-role amendment (REQ-026, ADR-072): rewrites the
role value ``member`` to ``user`` and converts the single ``role`` column to
the ``roles`` list column (a JSON array, e.g. ``["user"]``). Idempotent and
lossless: a fresh database (no ``users`` table) or an already-migrated
database (no ``role`` column) is a no-op; already-converted values (a JSON
array) are not re-wrapped.

Revision ID: eace2f772150
Revises:
Create Date: 2026-09-22 19:56:41.386866

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "eace2f772150"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _users_columns() -> list[str] | None:
    """The ``users`` table's column names, or ``None`` when the table is absent."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "users" not in inspector.get_table_names():
        return None
    return [column["name"] for column in inspector.get_columns("users")]


def upgrade() -> None:
    columns = _users_columns()
    if columns is None:
        # Fresh database: the users table is bootstrapped by the ORM (no data).
        return
    if "role" not in columns:
        # Already migrated (defensive idempotency).
        return
    bind = op.get_bind()
    # Rewrite role values: member -> user.
    bind.execute(sa.text("UPDATE users SET role = 'user' WHERE role = 'member'"))
    # Convert the single role column to a role list (JSON array). The guard
    # skips already-converted values (idempotent; no double wrapping).
    bind.execute(sa.text("UPDATE users SET role = '[\"' || role || '\"]' WHERE role NOT LIKE '[%'"))
    # Rename the column role -> roles.
    with op.batch_alter_table("users") as batch_op:
        batch_op.alter_column("role", new_column_name="roles")


def downgrade() -> None:
    columns = _users_columns()
    if columns is None:
        return
    if "roles" not in columns:
        return
    # Rename the column roles -> role.
    with op.batch_alter_table("users") as batch_op:
        batch_op.alter_column("roles", new_column_name="role")
    bind = op.get_bind()
    # Convert the role list back to a single role (the first element; strip
    # the JSON wrapper ``["..."]``).
    bind.execute(sa.text("UPDATE users SET role = substr(role, 3, length(role) - 4) WHERE role LIKE '[%'"))
    # Rewrite role values: user -> member.
    bind.execute(sa.text("UPDATE users SET role = 'member' WHERE role = 'user'"))
