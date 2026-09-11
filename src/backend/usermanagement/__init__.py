"""Public API of the user-management feature (module: backend.usermanagement).

The public API is the NFR-003 backward-compatibility contract:
``User``, ``UserCreate``, ``UserUpdate``, ``UserRead``, the lifecycle events,
``EventPublisher``, ``UserRepository``, ``SqliteUserRepository``,
``UserManager``, and the error hierarchy.
"""

from __future__ import annotations

from backend.usermanagement.errors import (
    InvalidRoleError,
    LastAdminError,
    UserAlreadyExistsError,
    UserManagerError,
    UserNotFoundError,
)
from backend.usermanagement.events import (
    EventPublisher,
    UserActivated,
    UserCreated,
    UserDeactivated,
    UserDeleted,
    UserEvent,
    UserPasswordChanged,
    UserRoleChanged,
    UserUpdated,
)
from backend.usermanagement.feature_settings import register_settings
from backend.usermanagement.models import User, UserCreate, UserRead, UserUpdate
from backend.usermanagement.repository import SqliteUserRepository, UserRepository
from backend.usermanagement.service import UserManager

__all__ = [
    "EventPublisher",
    "InvalidRoleError",
    "LastAdminError",
    "SqliteUserRepository",
    "User",
    "UserActivated",
    "UserAlreadyExistsError",
    "UserCreate",
    "UserCreated",
    "UserDeactivated",
    "UserDeleted",
    "UserEvent",
    "UserManager",
    "UserManagerError",
    "UserNotFoundError",
    "UserPasswordChanged",
    "UserRead",
    "UserRepository",
    "UserRoleChanged",
    "UserUpdate",
    "UserUpdated",
    "register_settings",
]
