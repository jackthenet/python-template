"""The SessionService use-case service (docs/specs/session-management.md).

``SessionService`` manages the sessions owned by the authentication feature
over the reused authentication session store (REQ-017, ADR-061): it lists a
user's valid sessions with device identification and a current-session marker,
resolving the token path through the same token-at-rest contract
(``hash_token``) that authentication's ``session_info`` uses (REQ-002,
REQ-008/REQ-017 of the authentication spec).

The service is traced with ``@logged_class`` (``include_args=False`` so raw
tokens never appear in log records; ``slow_threshold_ms=100``) (REQ-022,
NFR-004).
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from backend.authentication import InvalidSessionError, hash_token
from backend.authentication.models import Session
from backend.authentication.repositories import SessionRepository
from backend.logging import logged_class
from backend.sessionmanagement.events import (
    AllSessionsRevoked,
    EventPublisher,
    ExpiredSessionsDeleted,
    SessionRevoked,
    SessionsListed,
)
from backend.sessionmanagement.models import SessionEntry
from backend.settings import SettingsRegistry, get_settings_registry

# Hardcoded fallbacks for the live settings reads (REQ-019): unregistered
# keys fall back to these defaults.
DEFAULT_MAX_LISTED_SESSIONS = 100
DEFAULT_CLEANUP_BATCH_SIZE = 1000


@logged_class(slow_threshold_ms=100, include_args=False)
class SessionService:
    """Manages the sessions owned by the authentication feature (REQ-001..REQ-018).

    The constructor takes the authentication ``SessionRepository`` ABC
    (constructor DI, REQ-020, ADR-065); a ``None`` event bus means no events
    and no subscriptions; a ``None`` settings registry uses the shared
    ``get_settings_registry()`` (REQ-020).
    """

    def __init__(
        self,
        repository: SessionRepository,
        event_bus: EventPublisher | None = None,
        settings_registry: SettingsRegistry | None = None,
    ) -> None:
        self._repository = repository
        self._event_bus = event_bus
        self._settings_registry = settings_registry

    # -- Wiring helpers -------------------------------------------------------

    def _registry(self) -> SettingsRegistry:
        """The settings registry: the injected one, or the shared singleton."""
        if self._settings_registry is not None:
            return self._settings_registry
        return get_settings_registry()

    def _read_setting(self, registry: SettingsRegistry, key: str, fallback: Any) -> Any:
        """The live value of ``key``, or ``fallback`` when unregistered (REQ-019)."""
        if registry.has(key):
            return registry.get_value(key)
        return fallback

    def _publish(self, event: object) -> None:
        """Publish ``event``; a ``None`` publisher means no events and no error."""
        if self._event_bus is not None:
            self._event_bus.publish(event)

    # -- Operations -----------------------------------------------------------

    def list_sessions(
        self,
        token: str | None = None,
        user_id: UUID | None = None,
        limit: int | None = None,
    ) -> list[SessionEntry]:
        """List the user's valid sessions (REQ-001..REQ-007).

        Exactly one of ``token`` (self-service) or ``user_id`` (admin) is
        required (REQ-001, EDGE-008). The token path resolves the user and
        the current session, re-raising ``InvalidSessionError`` for an
        unknown, revoked, or expired token (REQ-002). The list contains only
        valid sessions (REQ-003, INV-002), ordered ``created_at`` descending
        with the current session (token path) pinned first (REQ-006, INV-005),
        bounded by ``limit`` (default the live-read
        ``sessionmanagement.max_listed_sessions``; ``limit < 1`` ->
        ``ValueError``) (REQ-007, EDGE-009).
        """
        if (token is None) == (user_id is None):
            raise ValueError("exactly one of token or user_id is required")
        if limit is not None and limit < 1:
            raise ValueError("limit must be >= 1")
        # One "now at call time" snapshot: the current-session validity check
        # and the valid-only filter evaluate validity against the same instant
        # (INV-002, authentication INV-002).
        now = datetime.now(UTC)
        current_session_id: UUID | None = None
        if token is not None:
            session = self._repository.get_by_token_hash(hash_token(token))
            if session is None or session.revoked or session.expires_at <= now:
                raise InvalidSessionError("invalid session")
            current_session_id = session.id
            user_id = session.user_id
        assert user_id is not None  # validated above (exactly one of token/user_id)
        valid = [row for row in self._repository.list_for_user(user_id) if not row.revoked and row.expires_at > now]
        if current_session_id is not None:
            # Pin the current session first; the remainder is already
            # created_at descending from list_for_user (REQ-006, INV-005).
            rest = [row for row in valid if row.id != current_session_id]
            ordered = [row for row in valid if row.id == current_session_id] + rest
        else:
            ordered = valid
        if limit is None:
            limit = int(
                self._read_setting(
                    self._registry(), "sessionmanagement.max_listed_sessions", DEFAULT_MAX_LISTED_SESSIONS
                )
            )
        entries = [self._to_entry(row, current_session_id) for row in ordered[:limit]]
        self._publish(SessionsListed(user_id=user_id, count=len(entries)))
        return entries

    def _resolve_token(self, token: str) -> Session:
        """Resolve the token path (authentication's ``session_info`` contract, REQ-002).

        Returns the session row for a valid token; an unknown, revoked, or
        expired token raises ``InvalidSessionError`` (authentication).
        """
        session = self._repository.get_by_token_hash(hash_token(token))
        if session is None or session.revoked or session.expires_at <= datetime.now(UTC):
            raise InvalidSessionError("invalid session")
        return session

    def revoke_session(self, session_id: UUID) -> None:
        """Revoke the session with that id (REQ-008).

        An unknown or already-revoked id is an idempotent no-op — no error,
        no event (REQ-008, INV-001, EDGE-002, EDGE-003). When a session is
        revoked, ``SessionRevoked(user_id, session_id)`` is published
        (REQ-018, AC-034).
        """
        row = self._repository.get(session_id)
        if row is None or row.revoked:
            return
        self._repository.revoke(session_id)
        self._publish(SessionRevoked(user_id=row.user_id, session_id=session_id))

    def _revoke_user_sessions(self, user_id: UUID, exclude_session_id: UUID | None = None) -> int:
        """Revoke the user's sessions and return the count (REQ-009..REQ-011).

        Publishes ``AllSessionsRevoked(user_id, excluded_session_id)`` when at
        least one session is revoked; revoking nothing publishes no event
        (REQ-018, AC-035, INV-001, EDGE-005).
        """
        count = self._repository.revoke_user_sessions(user_id, exclude_session_id=exclude_session_id)
        if count > 0:
            self._publish(AllSessionsRevoked(user_id=user_id, excluded_session_id=exclude_session_id))
        return count

    def logout_all_sessions(self, token: str) -> None:
        """Revoke all sessions for the token's user, including the caller's (REQ-009).

        The token is resolved via the token path; an unknown, revoked, or
        expired token raises ``InvalidSessionError`` (REQ-009, AC-018). The
        caller's own session is revoked too (self-lockout accepted,
        EDGE-004). ``AllSessionsRevoked(user_id,
        excluded_session_id=None)`` is published when at least one session is
        revoked (REQ-018, AC-035, INV-001).
        """
        session = self._resolve_token(token)
        self._revoke_user_sessions(session.user_id)

    def logout_other_sessions(self, token: str) -> None:
        """Revoke all sessions for the token's user except the caller's (REQ-010).

        The token is resolved via the token path; an unknown, revoked, or
        expired token raises ``InvalidSessionError`` (REQ-010, AC-018).
        ``AllSessionsRevoked(user_id, excluded_session_id=<the caller's
        session id>)`` is published when at least one session is revoked
        (REQ-018, AC-035, INV-001); revoking nothing publishes no event
        (EDGE-005).
        """
        session = self._resolve_token(token)
        self._revoke_user_sessions(session.user_id, exclude_session_id=session.id)

    def revoke_all_sessions(self, user_id: UUID, exclude_session_id: UUID | None = None) -> int:
        """Revoke all sessions for the user except the excluded one (REQ-011).

        Admin; open in-process, no token. Returns the number of sessions
        revoked; a user with zero revocable sessions yields 0 with no error
        (REQ-011, AC-023). ``AllSessionsRevoked(user_id,
        excluded_session_id)`` is published when at least one session is
        revoked (REQ-018, AC-035, INV-001).
        """
        return self._revoke_user_sessions(user_id, exclude_session_id=exclude_session_id)

    def cleanup_expired(self) -> int:
        """Delete expired session rows and return the number deleted (REQ-012).

        Bounded by the live-read ``sessionmanagement.cleanup_batch_size``
        (default 1000) (REQ-012, REQ-019); the application calls this on
        its own schedule — no threads or background workers in the feature
        (REQ-012). When at least one row is deleted,
        ``ExpiredSessionsDeleted(count)`` is published; deleting 0 rows
        publishes no event (REQ-018, AC-036, ADR-068).
        """
        batch_size = int(
            self._read_setting(self._registry(), "sessionmanagement.cleanup_batch_size", DEFAULT_CLEANUP_BATCH_SIZE)
        )
        count = self._repository.delete_expired(batch_size)
        if count > 0:
            self._publish(ExpiredSessionsDeleted(count=count))
        return count

    # -- Mapping --------------------------------------------------------------

    def _to_entry(self, row: Session, current_session_id: UUID | None) -> SessionEntry:
        """Map a session row to its listing entry (REQ-004; no tokens/hashes)."""
        return SessionEntry(
            session_id=row.id,
            created_at=row.created_at,
            expires_at=row.expires_at,
            is_current=row.id == current_session_id,
            user_agent=row.user_agent,
            ip=row.ip,
            device_name=row.device_name,
            login_method=row.login_method,
        )
