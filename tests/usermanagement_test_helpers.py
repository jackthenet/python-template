"""Shared helpers for the usermanagement test suite.

Mirrors the settings/event-bus helper pattern: a synchronous event collector
for deterministic event assertions, a valid ``UserCreate`` field factory, and
cross-platform absolute SQLite file URL construction.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


class EventCollector:
    """A synchronous ``EventPublisher`` that collects published events.

    The spec's event ACs are phrased as "Given a publisher that collects
    events", so a synchronous collector (not the async event bus) gives
    deterministic assertions.
    """

    def __init__(self) -> None:
        self.events: list[Any] = []

    def publish(self, event: object) -> None:
        self.events.append(event)

    def of_type(self, event_type: type) -> list[Any]:
        return [e for e in self.events if isinstance(e, event_type)]


def valid_create(**overrides: Any) -> dict[str, Any]:
    """A valid ``UserCreate`` field mapping; ``overrides`` replace fields.

    The defaults satisfy the schema rules: username pattern, valid email,
    password with >= 1 letter and >= 1 digit (8..128 chars), display name
    1..64 chars after strip, lowercase role, and an https profile picture URL.
    """
    data: dict[str, Any] = {
        "username": "alice",
        "email": "alice@example.com",
        "password": "correct-horse-1",
        "display_name": "Alice",
        "role": "member",
        "profile_picture_url": "https://example.com/alice.png",
    }
    data.update(overrides)
    return data


def db_url(tmp_path: Path, name: str = "users.db") -> str:
    """A cross-platform absolute SQLite file URL under ``tmp_path``.

    POSIX absolute paths need four slashes (``sqlite:////abs``); Windows
    paths (``C:/...``) are already absolute and use three.
    """
    p = str(tmp_path / name).replace("\\", "/")
    prefix = "sqlite:////" if p.startswith("/") else "sqlite:///"
    return f"{prefix}{p}"
