"""Repository ABCs for authentication persistence.

Each ABC is implemented by a ``Sqlite*`` class (T-002) and could be swapped for
another backend. The service depends only on these ABCs.

The ABCs evolve additively (backward-compatible per authentication NFR-003):
custom repository implementations gain new methods without changes to existing
ones (precedent: the session-management ``get``/``list_for_user``/
``revoke_user_sessions`` extensions, REQ-017; now ``SessionRepository.list_all``
for the search feature, REQ-022, ADR-080 — the one break for out-of-tree
implementors).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from uuid import UUID

from backend.authentication.models import PasswordReset, Session, WebAuthnCredential
from backend.logging import logged_class


@logged_class(slow_threshold_ms=100)
class SessionRepository(ABC):
    """Persistence for opaque session rows.

    The ABC is traced via the shared logging feature (``@logged_class``);
    concrete subclasses inherit the tracing.
    """

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
    def get(self, session_id: UUID) -> Session | None:
        """Return the session row for a session id (any revocation state), or ``None``.

        Additive extension for the session-management feature (REQ-017, ADR-061).
        """

    @abstractmethod
    def list_for_user(self, user_id: UUID) -> Sequence[Session]:
        """Return ALL rows for a user (any revocation state), ``created_at`` descending.

        Additive extension for the session-management feature (REQ-017, ADR-061).
        """

    @abstractmethod
    def revoke_user_sessions(self, user_id: UUID, exclude_session_id: UUID | None = None) -> int:
        """Revoke all of a user's sessions except the excluded one; return the count revoked.

        Additive extension for the session-management feature (REQ-017, ADR-061).
        """

    @abstractmethod
    def delete_expired(self, limit: int | None = None) -> int:
        """Delete up to ``limit`` expired sessions (``None`` = all, the previous behavior)
        and return the count.

        Backward-compatible signature extension for the session-management feature
        (REQ-017, ADR-061).
        """

    @abstractmethod
    def list_all(self) -> Sequence[Session]:
        """Return ALL sessions (any revocation state, no user filter), ``created_at`` descending.

        Additive extension for the search feature (REQ-022, ADR-080).
        """


@logged_class(slow_threshold_ms=100)
class PasswordResetRepository(ABC):
    """Persistence for password-reset token rows.

    The ABC is traced via the shared logging feature (``@logged_class``);
    concrete subclasses inherit the tracing.
    """

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


@logged_class(slow_threshold_ms=100)
class WebAuthnCredentialRepository(ABC):
    """Persistence for stored WebAuthn (passkey) credentials.

    The ABC is traced via the shared logging feature (``@logged_class``);
    concrete subclasses inherit the tracing.
    """

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
