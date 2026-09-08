"""Repository ABCs for authentication persistence.

Each ABC is implemented by a ``Sqlite*`` class (T-002) and could be swapped for
another backend. The service depends only on these ABCs.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from uuid import UUID

from backend.authentication.models import PasswordReset, Session, WebAuthnCredential


class SessionRepository(ABC):
    """Persistence for opaque session rows."""

    @abstractmethod
    def add(self, session: Session) -> Session:
        """Insert a session row and return it."""

    @abstractmethod
    def get_by_token_hash(self, token_hash: str) -> Session | None:
        """Return the session for a token hash, or ``None``."""

    @abstractmethod
    def revoke(self, session_id: UUID) -> None:
        """Mark a session revoked (idempotent)."""

    @abstractmethod
    def revoke_all_for_user(self, user_id: UUID) -> None:
        """Mark all of a user's sessions revoked."""

    @abstractmethod
    def delete_expired(self) -> int:
        """Delete expired sessions and return the count."""


class PasswordResetRepository(ABC):
    """Persistence for password-reset token rows."""

    @abstractmethod
    def add(self, reset: PasswordReset) -> PasswordReset:
        """Insert a reset row and return it."""

    @abstractmethod
    def get_by_token_hash(self, token_hash: str) -> PasswordReset | None:
        """Return the reset row for a token hash, or ``None``."""

    @abstractmethod
    def invalidate_all_for_user(self, user_id: UUID) -> None:
        """Invalidate (mark used) all of a user's pending reset rows."""

    @abstractmethod
    def mark_used(self, reset_id: UUID) -> None:
        """Mark a reset row used (single-use consumption)."""


class WebAuthnCredentialRepository(ABC):
    """Persistence for stored WebAuthn (passkey) credentials."""

    @abstractmethod
    def add(self, credential: WebAuthnCredential) -> WebAuthnCredential:
        """Insert a credential row and return it."""

    @abstractmethod
    def get_by_credential_id(self, credential_id: str) -> WebAuthnCredential | None:
        """Return the credential for a credential id, or ``None``."""

    @abstractmethod
    def list_for_user(self, user_id: UUID) -> Sequence[WebAuthnCredential]:
        """Return all of a user's stored credentials."""

    @abstractmethod
    def update_sign_count(self, credential_id: str, sign_count: int) -> None:
        """Update a credential's sign count."""

    @abstractmethod
    def delete(self, credential_id: str) -> None:
        """Delete a credential row."""
