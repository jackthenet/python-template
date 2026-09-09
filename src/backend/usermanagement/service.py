"""The user-management service (use cases, domain rules, events).

``UserManager`` depends only on the :class:`UserRepository` ABC (REQ-013),
stores only Argon2id hashes (REQ-004), returns only :class:`UserRead`
(ADR-024), and publishes exactly one typed event per successful mutation to
the injected :class:`EventPublisher` (REQ-016, REQ-017).

The class is traced via the shared logging feature (``@logged_class``);
``include_args`` stays at its default ``False`` so method arguments —
including the password — are never logged (REQ-015, NFR-002).
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from datetime import UTC, datetime
from uuid import UUID, uuid4

from argon2 import PasswordHasher
from argon2.exceptions import Argon2Error

from backend.logging import logged_class
from backend.usermanagement.errors import (
    InvalidRoleError,
    LastAdminError,
    UserAlreadyExistsError,
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
from backend.usermanagement.models import NewPassword, User, UserCreate, UserRead, UserUpdate
from backend.usermanagement.repository import UserRepository

_ROLE_RE = re.compile(r"^[a-z0-9_-]{1,32}$")


def _utcnow() -> datetime:
    return datetime.now(UTC)


def _to_read(user: User) -> UserRead:
    """Map a table row to the service representation (no ``password_hash``, ADR-024)."""
    return UserRead.model_validate(user.model_dump())


@logged_class(slow_threshold_ms=250)
class UserManager:
    """Use-case entry point for managing user account records.

    The class is traced via the shared logging feature (``@logged_class``);
    each public method produces entry and exit log records.
    """

    def __init__(
        self,
        repository: UserRepository,
        roles: Iterable[str] = ("admin", "member"),
        event_bus: EventPublisher | None = None,
    ) -> None:
        role_tuple = tuple(roles)
        if not role_tuple:
            raise ValueError("roles must be non-empty")
        for role in role_tuple:
            if not _ROLE_RE.fullmatch(role):
                raise ValueError(f"role {role!r} must match ^[a-z0-9_-]{{1,32}}$")
        self._repository = repository
        self._roles = frozenset(role_tuple)
        self._event_bus = event_bus
        self._hasher = PasswordHasher()

    # --- reads ---

    def get_user(self, user_id: UUID) -> UserRead:
        user = self._repository.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError(f"user {user_id} not found")
        return _to_read(user)

    def get_user_by_username(self, username: str) -> UserRead:
        user = self._repository.get_by_username(username)
        if user is None:
            raise UserNotFoundError(f"user {username!r} not found")
        return _to_read(user)

    def list_users(self, include_inactive: bool = False) -> list[UserRead]:
        users = self._repository.list_all(include_inactive)
        return [_to_read(user) for user in users]

    # --- create ---

    def create_user(self, data: UserCreate) -> UserRead:
        if data.role not in self._roles:
            raise InvalidRoleError(role=data.role, allowed=self._roles)
        now = _utcnow()
        user = User(
            id=uuid4(),
            username=data.username,
            email=data.email.lower(),
            display_name=data.display_name,
            role=data.role,
            password_hash=self._hasher.hash(data.password),
            profile_picture_url=data.profile_picture_url,
            is_active=True,
            created_at=now,
            updated_at=now,
        )
        self._repository.add(user)
        self._publish(UserCreated(user_id=user.id, username=user.username, email=user.email, role=user.role))
        return _to_read(user)

    # --- update / delete ---

    def update_user(self, user_id: UUID, data: UserUpdate) -> UserRead:
        user = self._repository.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError(f"user {user_id} not found")
        changed_fields: list[str] = []
        if data.email is not None:
            new_email = data.email.lower()
            existing = self._repository.get_by_email(new_email)
            if existing is not None and existing.id != user.id:
                raise UserAlreadyExistsError(field="email")
            user.email = new_email
            changed_fields.append("email")
        if data.display_name is not None:
            user.display_name = data.display_name
            changed_fields.append("display_name")
        if data.profile_picture_url is not None:
            user.profile_picture_url = data.profile_picture_url
            changed_fields.append("profile_picture_url")
        if not changed_fields:
            # Empty update: idempotent no-op — no event, updated_at unchanged.
            return _to_read(user)
        user.updated_at = _utcnow()
        self._repository.update(user)
        self._publish(UserUpdated(user_id=user.id, changed_fields=changed_fields))
        return _to_read(user)

    def delete_user(self, user_id: UUID) -> None:
        user = self._repository.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError(f"user {user_id} not found")
        self._assert_not_last_admin(user)
        self._repository.delete(user_id)
        self._publish(UserDeleted(user_id=user.id, username=user.username))

    # --- password ---

    def change_password(self, user_id: UUID, new_password: str) -> None:
        user = self._repository.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError(f"user {user_id} not found")
        NewPassword(password=new_password)  # raises pydantic.ValidationError
        user.password_hash = self._hasher.hash(new_password)
        self._repository.update(user)
        self._publish(UserPasswordChanged(user_id=user.id))

    def verify_password(self, user_id: UUID, password: str) -> bool:
        user = self._repository.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError(f"user {user_id} not found")
        try:
            return self._hasher.verify(user.password_hash, password)
        except Argon2Error:
            return False

    # --- role ---

    def set_role(self, user_id: UUID, role: str) -> UserRead:
        user = self._repository.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError(f"user {user_id} not found")
        if role not in self._roles:
            raise InvalidRoleError(role=role, allowed=self._roles)
        if user.role == role:
            # Same role: idempotent no-op — no event.
            return _to_read(user)
        self._assert_not_last_admin(user, new_role=role)
        old_role = user.role
        user.role = role
        self._repository.update(user)
        self._publish(UserRoleChanged(user_id=user.id, old_role=old_role, new_role=role))
        return _to_read(user)

    # --- activation ---

    def activate_user(self, user_id: UUID) -> UserRead:
        user = self._repository.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError(f"user {user_id} not found")
        if user.is_active:
            # Already active: idempotent no-op — no event.
            return _to_read(user)
        user.is_active = True
        self._repository.update(user)
        self._publish(UserActivated(user_id=user.id))
        return _to_read(user)

    def deactivate_user(self, user_id: UUID) -> UserRead:
        user = self._repository.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError(f"user {user_id} not found")
        if not user.is_active:
            # Already inactive: idempotent no-op — no event.
            return _to_read(user)
        self._assert_not_last_admin(user)
        user.is_active = False
        self._repository.update(user)
        self._publish(UserDeactivated(user_id=user.id))
        return _to_read(user)

    # --- internals ---

    def _assert_not_last_admin(self, user: User, new_role: str | None = None) -> None:
        """Raise :class:`LastAdminError` if the operation would leave zero
        active admins (only while ``admin`` is in the configured role set,
        ADR-022)."""
        if "admin" not in self._roles:
            return
        if user.role != "admin" or not user.is_active:
            return
        if new_role is not None and new_role == "admin":
            return
        if self._repository.count_active_by_role("admin") == 1:
            raise LastAdminError()

    def _publish(self, event: UserEvent) -> None:
        """Publish ``event`` if a publisher was injected; a ``None`` publisher
        means no events and no errors (REQ-017). Publisher exceptions
        propagate to the caller with the mutation already committed
        (EDGE-020)."""
        if self._event_bus is not None:
            self._event_bus.publish(event)
