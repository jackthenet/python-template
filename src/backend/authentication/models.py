"""Domain models, request schemas, and representations for authentication.

Field-format validation is schema-level (D9, ADR-023): violations raise
``pydantic.ValidationError`` identifying the offending field. Domain rules
(credentials, lockout, session validity, reset single-use, hijack detection)
are enforced by the service with the :mod:`backend.authentication.errors`
hierarchy.

Representations never expose ``password_hash`` or the raw session token except
``LoginResult.token`` (REQ-021, D11).
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, EmailStr, Field, field_validator
from sqlmodel import Field as SField
from sqlmodel import SQLModel

from backend.usermanagement import UserRead

# Shared password rules (must match the user-management feature, ADR-023):
# 8..128 characters, at least one letter and at least one digit.
_PASSWORD_MIN_LEN = 8
_PASSWORD_MAX_LEN = 128


def _validate_password(value: str) -> str:
    if not _PASSWORD_MIN_LEN <= len(value) <= _PASSWORD_MAX_LEN:
        raise ValueError(f"password must be {_PASSWORD_MIN_LEN}..{_PASSWORD_MAX_LEN} characters")
    if not any(c.isalpha() for c in value):
        raise ValueError("password must contain at least one letter")
    if not any(c.isdigit() for c in value):
        raise ValueError("password must contain at least one digit")
    return value


# --- Table models (persistence) ---


class Session(SQLModel, table=True):
    """The ``sessions`` table.

    The raw table object is not a service representation: the service returns
    :class:`SessionInfo` only, which has no ``token_hash``.
    """

    __tablename__ = "sessions"

    id: UUID = SField(default_factory=uuid4, primary_key=True)
    user_id: UUID = SField(index=True)
    token_hash: str = SField(unique=True, index=True)  # SHA-256 hex only (REQ-006)
    created_at: datetime  # UTC
    expires_at: datetime  # UTC
    revoked: bool = False


class PasswordReset(SQLModel, table=True):
    """The ``password_resets`` table."""

    __tablename__ = "password_resets"

    id: UUID = SField(default_factory=uuid4, primary_key=True)
    user_id: UUID = SField(index=True)
    email: str = SField(index=True)  # stored lowercased
    token_hash: str = SField(unique=True, index=True)  # SHA-256 hex only
    created_at: datetime  # UTC
    expires_at: datetime  # UTC
    used: bool = False


class WebAuthnCredential(SQLModel, table=True):
    """The ``webauthn_credentials`` table."""

    __tablename__ = "webauthn_credentials"

    id: UUID = SField(default_factory=uuid4, primary_key=True)
    user_id: UUID = SField(index=True)
    credential_id: str = SField(unique=True, index=True)  # base64url
    public_key: str  # base64
    transports: str  # JSON-encoded list[str]
    sign_count: int = 0
    created_at: datetime  # UTC


# --- Request schemas (schema-level validation) ---


class LoginRequest(BaseModel):
    """A password login attempt (identifier is a username or email)."""

    identifier: str = Field(min_length=1, max_length=320)
    password: str = Field(min_length=1, max_length=1024)


class PasswordResetRequest(BaseModel):
    """A password-reset request for an email."""

    email: EmailStr


class PasswordResetComplete(BaseModel):
    """Completion of a password reset with a new password."""

    token: str = Field(min_length=1, max_length=256)
    new_password: str

    @field_validator("new_password")
    @classmethod
    def _check_password(cls, value: str) -> str:
        return _validate_password(value)


class PasskeyRegistrationBegin(BaseModel):
    """Start of a passkey (WebAuthn) registration."""

    user_id: UUID
    username: str = Field(min_length=1, max_length=320)
    display_name: str | None = None


class PasskeyRegistrationComplete(BaseModel):
    """Completion of a passkey registration with the browser response."""

    user_id: UUID
    response: dict[str, Any]


class PasskeyLoginBegin(BaseModel):
    """Start of a passkey (WebAuthn) login."""

    credential_id: str = Field(min_length=1, max_length=512)


class PasskeyLoginComplete(BaseModel):
    """Completion of a passkey login with the browser response."""

    credential_id: str = Field(min_length=1, max_length=512)
    response: dict[str, Any]


# --- Representations (service output; no secrets) ---


class SessionInfo(BaseModel):
    """A valid session's metadata (no token)."""

    user_id: UUID
    created_at: datetime
    expires_at: datetime


class LoginResult(BaseModel):
    """The result of a successful login (the only place the raw token appears)."""

    user: UserRead
    session: SessionInfo
    token: str


class WebAuthnCredentialRead(BaseModel):
    """A stored passkey credential's metadata (no public key)."""

    credential_id: str
    transports: list[str]
    created_at: datetime


class VerifiedCredential(BaseModel):
    """A verified WebAuthn registration response (stored by the service)."""

    credential_id: str
    public_key: str
    transports: list[str]
    sign_count: int


class VerifiedAssertion(BaseModel):
    """A verified WebAuthn authentication response."""

    credential_id: str
    sign_count: int
