"""Shared helpers for the logging-coverage test suite.

Holds the normative inventory (spec section 3.1) — every public class and public
module function that MUST be traced — plus log-record filtering helpers and a
``capture_records`` context manager for Hypothesis property tests.

The inventory is the contract: each listed class and module function must be
traced per the spec (``@logged_class`` for classes, ``@logged`` for module
functions), with a concrete ``slow_threshold_ms`` and ``include_args=False``
where secrets are handled.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from contextlib import contextmanager
from typing import Any, Iterator

from loguru import logger

# --- The normative inventory: classes (spec section 3.1) -----------------
from backend.authentication.protocols import AttemptTracker, WebAuthnProvider
from backend.authentication.repository import (
    SqlitePasswordResetRepository,
    SqliteSessionRepository,
    SqliteWebAuthnCredentialRepository,
)
from backend.authentication.repositories import (
    PasswordResetRepository,
    SessionRepository,
    WebAuthnCredentialRepository,
)
from backend.authentication.service import AuthService
from backend.authentication.tokens import hash_token, new_token
from backend.authentication.tracker import InMemoryAttemptTracker
from backend.authentication.webauthn import PyWebAuthnProvider
from backend.eventbus.eventbus import EventBus, get_event_bus, reset_event_bus
from backend.logging import get_settings, setup_logger
from backend.settings.registry import (
    SettingsRegistry,
    get_settings_registry,
    reset_settings_registry,
)
from backend.settings.repository import (
    MemoryTemplateRepository,
    TemplateRepository,
    YamlTemplateRepository,
)
from backend.usermanagement.repository import SqliteUserRepository, UserRepository
from backend.usermanagement.service import UserManager

INVENTORY_CLASSES: dict[str, type] = {
    "AuthService": AuthService,
    "UserManager": UserManager,
    "EventBus": EventBus,
    "SettingsRegistry": SettingsRegistry,
    "SessionRepository": SessionRepository,
    "PasswordResetRepository": PasswordResetRepository,
    "WebAuthnCredentialRepository": WebAuthnCredentialRepository,
    "AttemptTracker": AttemptTracker,
    "WebAuthnProvider": WebAuthnProvider,
    "UserRepository": UserRepository,
    "TemplateRepository": TemplateRepository,
    "SqliteSessionRepository": SqliteSessionRepository,
    "SqlitePasswordResetRepository": SqlitePasswordResetRepository,
    "SqliteWebAuthnCredentialRepository": SqliteWebAuthnCredentialRepository,
    "InMemoryAttemptTracker": InMemoryAttemptTracker,
    "PyWebAuthnProvider": PyWebAuthnProvider,
    "SqliteUserRepository": SqliteUserRepository,
    "MemoryTemplateRepository": MemoryTemplateRepository,
    "YamlTemplateRepository": YamlTemplateRepository,
}

# --- The normative inventory: module functions (spec section 3.1) ---------
INVENTORY_MODULE_FUNCTIONS: dict[str, Callable[..., Any]] = {
    "new_token": new_token,
    "hash_token": hash_token,
    "get_event_bus": get_event_bus,
    "reset_event_bus": reset_event_bus,
    "get_settings_registry": get_settings_registry,
    "reset_settings_registry": reset_settings_registry,
    "get_settings": get_settings,
    "setup_logger": setup_logger,
}


# --- Log-record filtering helpers -----------------------------------------
def messages(records: list[Any]) -> list[str]:
    """The message text of each captured record."""
    return [str(r) for r in records]


def entry_records(records: list[Any]) -> list[Any]:
    """Entry records (``>> {qualname} called``)."""
    return [r for r in records if str(r).startswith(">>")]


def exit_records(records: list[Any]) -> list[Any]:
    """Exit records (``<< {qualname} returned in {ms} ms``)."""
    return [r for r in records if str(r).startswith("<<")]


def exception_records(records: list[Any]) -> list[Any]:
    """Exception records (``!! {qualname} raised {Type}({msg})``)."""
    return [r for r in records if str(r).startswith("!!")]


def level_name(record: Any) -> str:
    """The log level name of a captured record (e.g. ``WARNING``)."""
    return record["level"].name


def for_qualname(records: list[Any], qualname_fragment: str) -> list[Any]:
    """Records whose message mentions the given qualname fragment."""
    return [r for r in records if qualname_fragment in str(r)]


def parse_elapsed_ms(message: str) -> float | None:
    """Extract the elapsed milliseconds from an exit record's message.

    Returns ``None`` when the message is not an exit record (no
    ``returned in {ms} ms`` clause).
    """
    m = re.search(r"returned in ([\d.]+) ms", message)
    return float(m.group(1)) if m else None


# --- Record capture for Hypothesis property tests -------------------------
class _LiveMessages:
    """A live view of captured records as message-text strings.

    Reflects records added while the underlying capture block is active, so a
    test can read it after the traced calls. Each element is the record's
    message text, matching the suite's ``entry_records``/``exit_records``
    helpers (which filter on ``str(record)``).
    """

    def __init__(self, raw: list[Any]) -> None:
        self._raw = raw

    def _texts(self) -> list[str]:
        return [str(r.get("message", "")) for r in self._raw]

    def __len__(self) -> int:
        return len(self._raw)

    def __iter__(self) -> Iterator[str]:
        return iter(self._texts())

    def __getitem__(self, i: int) -> str:
        return self._texts()[i]


@contextmanager
def capture_records(level: str = "DEBUG") -> Iterator[_LiveMessages]:
    """Capture loguru records for the duration of the ``with`` block.

    Yields a fresh live view of message-text strings per invocation, so
    Hypothesis iterations do not accumulate across each other. The view
    reflects records added while the block is active.
    """
    raw: list[Any] = []

    def _sink(message: Any) -> None:
        raw.append(message.record)

    handler_id = logger.add(_sink, level=level, catch=False)
    try:
        yield _LiveMessages(raw)
    finally:
        logger.remove(handler_id)
