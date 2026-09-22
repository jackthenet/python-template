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
from backend.usermanagement.role_store import RoleStore, StaticRoleStore


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
        role_store: RoleStore | None = None,
        event_bus: EventPublisher | None = None,
    ) -> None:
        self._repository = repository
        self._event_bus = event_bus
        self._hasher = PasswordHasher()
        # D4/ADR-072: role existence is validated against the injected
        # RoleStore (default StaticRoleStore(("admin", "user"))); the store
        # is the single source of truth for role names (Q-77).
        self._role_store = role_store if role_store is not None else StaticRoleStore(("admin", "user"))

    # --- reads ---

    def get_user(self, user_id: UUID) -> UserRead:
        return _to_read(self._get_user_or_raise(user_id))

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
        self._validate_roles(data.roles)
        now = _utcnow()
        user = User(
            id=uuid4(),
            username=data.username,
            email=data.email.lower(),
            display_name=data.display_name,
            roles=list(data.roles),
            password_hash=self._hasher.hash(data.password),
            profile_picture_url=data.profile_picture_url,
            is_active=True,
            created_at=now,
            updated_at=now,
        )
        self._repository.add(user)
        self._publish(
            UserCreated(user_id=user.id, username=user.username, email=user.email, roles=list(user.roles))
        )
        return _to_read(user)

    # --- update / delete ---

    def update_user(self, user_id: UUID, data: UserUpdate) -> UserRead:
        user = self._get_user_or_raise(user_id)
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
        user = self._get_user_or_raise(user_id)
        self._assert_not_last_admin(user, keeps_active_admin=False)
        self._repository.delete(user_id)
        self._publish(UserDeleted(user_id=user.id, username=user.username))

    # --- password ---

    def change_password(self, user_id: UUID, new_password: str) -> None:
        user = self._get_user_or_raise(user_id)
        NewPassword(password=new_password)  # raises pydantic.ValidationError
        user.password_hash = self._hasher.hash(new_password)
        self._repository.update(user)
        self._publish(UserPasswordChanged(user_id=user.id))

    def verify_password(self, user_id: UUID, password: str) -> bool:
        user = self._get_user_or_raise(user_id)
        try:
            return self._hasher.verify(user.password_hash, password)
        except Argon2Error:
            return False

    # --- roles ---

    def set_role(self, user_id: UUID, role: str) -> UserRead:
        # Preserved (replace semantics): set_role = set_roles([role]) (Q-76).
        return self.set_roles(user_id, [role])

    def set_roles(self, user_id: UUID, roles: Iterable[str]) -> UserRead:
        user = self._get_user_or_raise(user_id)
        new_roles = self._validate_roles(roles)
        if new_roles == list(user.roles):
            # Same roles: idempotent no-op — no event.
            return _to_read(user)
        return self._apply_roles(user, new_roles, guard=True)

    def add_role(self, user_id: UUID, role: str) -> UserRead:
        user = self._get_user_or_raise(user_id)
        self._validate_roles([role])
        if role in user.roles:
            # Already present: idempotent no-op — no event.
            return _to_read(user)
        # add_role cannot remove admin and is never rejected by the guard.
        return self._apply_roles(user, [*user.roles, role], guard=False)

    def remove_role(self, user_id: UUID, role: str) -> UserRead:
        user = self._get_user_or_raise(user_id)
        if role not in user.roles:
            # Not present: idempotent no-op — no event.
            return _to_read(user)
        new_roles = [r for r in user.roles if r != role]
        if not new_roles:
            raise ValueError("roles must be non-empty")
        return self._apply_roles(user, new_roles, guard=True)

    # --- activation ---

    def activate_user(self, user_id: UUID) -> UserRead:
        user = self._get_user_or_raise(user_id)
        if user.is_active:
            # Already active: idempotent no-op — no event.
            return _to_read(user)
        user.is_active = True
        self._repository.update(user)
        self._publish(UserActivated(user_id=user.id))
        return _to_read(user)

    def deactivate_user(self, user_id: UUID) -> UserRead:
        user = self._get_user_or_raise(user_id)
        if not user.is_active:
            # Already inactive: idempotent no-op — no event.
            return _to_read(user)
        self._assert_not_last_admin(user, keeps_active_admin=False)
        user.is_active = False
        self._repository.update(user)
        self._publish(UserDeactivated(user_id=user.id))
        return _to_read(user)

    # --- internals ---

    def _get_user_or_raise(self, user_id: UUID) -> User:
        """Fetch ``user_id`` from the repository or raise
        :class:`UserNotFoundError` (D9)."""
        user = self._repository.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError(f"user {user_id} not found")
        return user

    def _apply_roles(self, user: User, new_roles: list[str], guard: bool) -> UserRead:
        """Persist ``new_roles`` on ``user`` and publish
        :class:`UserRoleChanged` (D10). ``guard`` runs the last-admin check
        first; ``add_role`` never removes admin and skips it (``guard=False``)."""
        if guard:
            self._assert_not_last_admin(user, keeps_active_admin=("admin" in new_roles))
        old_roles = list(user.roles)
        user.roles = new_roles
        self._repository.update(user)
        self._publish(UserRoleChanged(user_id=user.id, old_roles=old_roles, new_roles=new_roles))
        return _to_read(user)

    def _validate_roles(self, roles: Iterable[str]) -> list[str]:
        """Validate each role against the RoleStore; return the role list.

        Raises :class:`InvalidRoleError` for a role the store does not have
        and ``ValueError`` for an empty list (REQ-026: non-empty).
        """
        role_list = list(roles)
        if not role_list:
            raise ValueError("roles must be non-empty")
        for role in role_list:
            if not self._role_store.has_role(role):
                raise InvalidRoleError(role=role, allowed=self._role_store.list_roles())
        return role_list

    def _assert_not_last_admin(self, user: User, keeps_active_admin: bool) -> None:
        """Raise :class:`LastAdminError` if the operation would leave zero
        active admins (ADR-022 extended to every assignment path, ADR-072).

        An "active admin" is an active user whose ``roles`` include
        ``admin``. ``keeps_active_admin`` is whether the user remains an
        active admin after the operation.

        The guard is scoped to a last active admin who holds ``admin``
        alongside at least one other role: a single-role admin
        (``roles == ["admin"]``) is not protected on these paths, so
        demoting/deactivating/deleting it is allowed (AC-034 vs AC-036).
        """
        if "admin" not in self._role_store.list_roles():
            return
        if "admin" not in user.roles or not user.is_active:
            return
        if len(user.roles) <= 1:
            return
        if keeps_active_admin:
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
