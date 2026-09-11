"""Public API for the event bus feature.

Exposes the in-memory, asynchronous event bus for decoupled backend
communication. See ``docs/specs/event-bus.md``.
"""

from __future__ import annotations

from backend.eventbus.eventbus import EventBus, get_event_bus, reset_event_bus
from backend.eventbus.feature_settings import register_settings

__all__ = ["EventBus", "get_event_bus", "register_settings", "reset_event_bus"]
