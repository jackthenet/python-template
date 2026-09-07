"""Domain models and request/response schemas for user management.

Field-format validation is schema-level (ADR-023): violations raise
``pydantic.ValidationError`` identifying the offending field. Domain rules
(role membership, uniqueness, last-admin protection) are enforced by the
service with the :mod:`backend.usermanagement.errors` hierarchy.
"""

from __future__ import annotations

import re
from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, EmailStr, field_validator
from sqlalchemy import UniqueConstraint
from sqlmodel import Field as SField
from sqlmodel import SQLModel

_USERNAME_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]{1,30}[a-zA-Z0-9]$")
_ROLE_RE = re.compile(r"^[a-z0-9_-]{1,32}$")

# Password / display-name length limits (spec NFR-001, ADR-023).
_PASSWORD_MIN_LEN = 8
_PASSWORD_MAX_LEN = 128
_DISPLAY_NAME_MAX_LEN = 64


def _validate_password(value: str) -> str:
    if not _PASSWORD_MIN_LEN <= len(value) <= _PASSWORD_MAX_LEN:
        raise ValueError(f"password must be {_PASSWORD_MIN_LEN}..{_PASSWORD_MAX_LEN} characters")
    if not any(c.isalpha() for c in value):
        raise ValueError("password must contain at least one letter")
    if not any(c.isdigit() for c in value):
        raise ValueError("password must contain at least one digit")
    return value


def _validate_display_name(value: str | None) -> str | None:
    if value is None:
        return None
    if not value.strip():
        raise ValueError("display_name must not be blank")
    if len(value) > _DISPLAY_NAME_MAX_LEN:
        raise ValueError(f"display_name must be at most {_DISPLAY_NAME_MAX_LEN} characters")
    return value


def _validate_profile_picture_url(value: str | None) -> str | None:
    if value is None:
        return None
    if not (value.startswith("http://") or value.startswith("https://")):
        raise ValueError("profile_picture_url must start with http:// or https://")
    return value


class User(SQLModel, table=True):
    """The ``users`` table (persistence).

    The raw table object is not a service representation (ADR-024): the
    service returns :class:`UserRead` only, which has no ``password_hash``.
    """

    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("username", name="uq_users_username"),
        UniqueConstraint("email", name="uq_users_email"),
    )

    id: UUID = SField(default_factory=uuid4, primary_key=True)
    username: str = SField(index=True)
    email: str = SField(index=True)  # stored lowercased (D5)
    display_name: str | None = None
    role: str
    password_hash: str  # Argon2id hash only (D2)
    profile_picture_url: str | None = None
    is_active: bool = True
    created_at: datetime  # UTC
    updated_at: datetime  # UTC


class UserCreate(BaseModel):
    """Request schema for creating a user (schema-level validation)."""

    username: str
    email: EmailStr
    password: str
    display_name: str | None = None
    role: str
    profile_picture_url: str | None = None

    @field_validator("username")
    @classmethod
    def _check_username(cls, value: str) -> str:
        if not _USERNAME_RE.fullmatch(value):
            raise ValueError("username must match ^[a-zA-Z0-9][a-zA-Z0-9._-]{1,30}[a-zA-Z0-9]$")
        return value

    @field_validator("password")
    @classmethod
    def _check_password(cls, value: str) -> str:
        return _validate_password(value)

    @field_validator("display_name")
    @classmethod
    def _check_display_name(cls, value: str | None) -> str | None:
        return _validate_display_name(value)

    @field_validator("role")
    @classmethod
    def _check_role(cls, value: str) -> str:
        if not _ROLE_RE.fullmatch(value):
            raise ValueError("role must match ^[a-z0-9_-]{1,32}$")
        return value

    @field_validator("profile_picture_url")
    @classmethod
    def _check_profile_picture_url(cls, value: str | None) -> str | None:
        return _validate_profile_picture_url(value)


class NewPassword(BaseModel):
    """A standalone password validated with the shared password rules.

    Used by ``change_password`` so the password rules cannot drift from
    ``UserCreate`` (ADR-023).
    """

    password: str

    @field_validator("password")
    @classmethod
    def _check_password(cls, value: str) -> str:
        return _validate_password(value)


class UserUpdate(BaseModel):
    """Request schema for updating a user.

    ``None`` means "no change" (not "clear"). There is no username field:
    usernames are immutable (D5).
    """

    email: EmailStr | None = None
    display_name: str | None = None
    profile_picture_url: str | None = None

    @field_validator("display_name")
    @classmethod
    def _check_display_name(cls, value: str | None) -> str | None:
        return _validate_display_name(value)

    @field_validator("profile_picture_url")
    @classmethod
    def _check_profile_picture_url(cls, value: str | None) -> str | None:
        return _validate_profile_picture_url(value)


class UserRead(BaseModel):
    """The only user representation returned by the service (D9)."""

    id: UUID
    username: str
    email: str
    display_name: str | None
    role: str
    profile_picture_url: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
