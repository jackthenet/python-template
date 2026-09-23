import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlmodel import SQLModel

# Import the model modules that define SQLModel tables so their tables register
# on the shared SQLModel.metadata (used as target_metadata below). The imports
# are intentionally unused at runtime (the aliases keep each import a distinct
# binding); each noqa comment names the tables pulled in: authentication
# (Session, PasswordReset, WebAuthnCredential), filemanagement (FileRecord,
# UserAvatar), permissions (Role, RolePermission, SystemPrincipalPermission),
# usermanagement (User).
import backend.authentication.models as authentication_models  # noqa: F401  # Session, PasswordReset, WebAuthnCredential
import backend.filemanagement.models as filemanagement_models  # noqa: F401  # FileRecord, UserAvatar
import backend.permissions.models as permissions_models  # noqa: F401  # Role, RolePermission, SystemPrincipalPermission
import backend.usermanagement.models as usermanagement_models  # noqa: F401  # User

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = SQLModel.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def get_database_url() -> str:
    """Return the database URL migrations run against.

    Reads the ALEMBIC_DATABASE_URL environment variable if set (so CI can point
    at a temporary database), otherwise falls back to the sqlalchemy.url value
    in alembic.ini.
    """
    return os.environ.get("ALEMBIC_DATABASE_URL") or config.get_main_option("sqlalchemy.url")


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    context.configure(
        url=get_database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        {"sqlalchemy.url": get_database_url()},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
