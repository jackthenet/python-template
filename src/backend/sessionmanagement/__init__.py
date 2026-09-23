"""Public API of the session-management feature (module: backend.sessionmanagement).

The public API is the NFR-003 backward-compatibility contract: the service,
the listing representation, and the typed events.
"""

from __future__ import annotations

from backend.sessionmanagement.events import (
    AllSessionsRevoked,
    EventPublisher,
    ExpiredSessionsDeleted,
    SessionRevoked,
    SessionsListed,
)
from backend.sessionmanagement.feature_actions import register_actions
from backend.sessionmanagement.feature_settings import register_settings
from backend.sessionmanagement.models import SessionEntry
from backend.sessionmanagement.service import SessionService, get_session_service, reset_session_service

__all__ = [
    "AllSessionsRevoked",
    "EventPublisher",
    "ExpiredSessionsDeleted",
    "SessionEntry",
    "SessionRevoked",
    "SessionService",
    "SessionsListed",
    "get_session_service",
    "register_actions",
    "register_settings",
    "reset_session_service",
]
