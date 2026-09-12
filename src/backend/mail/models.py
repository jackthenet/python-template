"""Request/representation models and the structural publisher protocol.

Request schemas perform schema-level validation (violations raise
``pydantic.ValidationError`` identifying the offending field, never the field
value) (D11). The representation ``EmailSendResult`` is frozen and carries no
body, no token, and no password.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from backend.logging import logged_class


class PasswordResetEmailRequest(BaseModel):
    """A request to send a password-reset email."""

    to: EmailStr
    display_name: str = Field(min_length=1, max_length=320)
    reset_url: str = Field(min_length=1, max_length=2048)


class EmailVerificationEmailRequest(BaseModel):
    """A request to send an email-verification email."""

    to: EmailStr
    display_name: str = Field(min_length=1, max_length=320)
    verification_url: str = Field(min_length=1, max_length=2048)


class EmailSendResult(BaseModel):
    """The result of a successful send (non-sensitive data only)."""

    model_config = ConfigDict(frozen=True)

    to: str
    template: str


@logged_class(slow_threshold_ms=10)
class EventPublisher(ABC):
    """Structural publisher protocol (satisfied by the shared event bus).

    The ABC is traced via the shared logging feature (``@logged_class``);
    concrete publishers inherit the tracing.
    """

    @abstractmethod
    def publish(self, event: object) -> None: ...
