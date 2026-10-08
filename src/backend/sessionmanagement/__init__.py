"""Public API of the session-management feature (module: backend.sessionmanagement).

The public API is the NFR-003 backward-compatibility contract: the service,
the listing representation, and the typed events. ``build_session_source``
(the search feature, REQ-022) is an additive re-export, and the singleton
trio ``get_session_service`` / ``set_session_service`` (REQ-023) /
``reset_session_service`` is the only public way to read, install or clear the
shared default.
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
from backend.sessionmanagement.search_source import build_session_source
from backend.sessionmanagement.service import (
    SessionService,
    get_session_service,
    reset_session_service,
    set_session_service,
)

__all__ = [
    "AllSessionsRevoked",
    "EventPublisher",
    "ExpiredSessionsDeleted",
    "SessionEntry",
    "SessionRevoked",
    "SessionService",
    "SessionsListed",
    "build_session_source",
    "get_session_service",
    "register_actions",
    "register_settings",
    "reset_session_service",
    "set_session_service",
]
