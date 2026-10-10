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

import logging
import re
from collections import namedtuple
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from typing import Any

# --- The normative inventory: classes (spec section 3.1) -----------------
from backend.authentication.protocols import AttemptTracker, WebAuthnProvider
from backend.authentication.repositories import (
    PasswordResetRepository,
    SessionRepository,
    WebAuthnCredentialRepository,
)
from backend.authentication.repository import (
    SqlitePasswordResetRepository,
    SqliteSessionRepository,
    SqliteWebAuthnCredentialRepository,
)
from backend.authentication.service import AuthService
from backend.authentication.tokens import hash_token, new_token
from backend.authentication.tracker import InMemoryAttemptTracker
from backend.authentication.webauthn import PyWebAuthnProvider
from backend.eventbus.eventbus import EventBus, get_event_bus, reset_event_bus, set_event_bus
from backend.logging import get_settings, setup_logger
from backend.permissions.service import get_permission_service, set_permission_service
from backend.search.service import set_search_service
from backend.sessionmanagement.service import set_session_service
from backend.settings.registry import (
    SettingsRegistry,
    get_settings_registry,
    reset_settings_registry,
    set_settings_registry,
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
    "set_event_bus": set_event_bus,
    "get_settings_registry": get_settings_registry,
    "reset_settings_registry": reset_settings_registry,
    "set_settings_registry": set_settings_registry,
    "get_permission_service": get_permission_service,
    "set_permission_service": set_permission_service,
    "set_search_service": set_search_service,
    "set_session_service": set_session_service,
    "get_settings": get_settings,
    "setup_logger": setup_logger,
}

# The five install operations of change ``settings-public-registry-setter`` (spec §3.1 rows added
# by its v3 amendment). Each takes the object it installs, so the bare-call probe in
# ``test_services_traced.test_module_functions_traced`` cannot call them. Their entry/exit pair is
# witnessed per function by that change's AC-014 witness
# (``tests/acceptance/singleton_install/test_install.py::test_ac_014_install_is_traced``), which
# installs a real instance of each feature's own type and restores the slot afterwards — a stronger
# witness than a bare call would be. The probe covers exactly the rest of the inventory.
INVENTORY_INSTALL_OPERATIONS: frozenset[str] = frozenset(
    {
        "set_settings_registry",
        "set_event_bus",
        "set_permission_service",
        "set_search_service",
        "set_session_service",
    }
)


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


# --- Record capture -------------------------------------------------------
# The suite reads a captured record in exactly three ways: ``str(record)`` for the
# message text, ``record["level"].name`` for the level, and ``record["record"]`` for
# the whole record. Every record reaches the capture through the logging pipeline, so
# one normalised shape covers the whole suite (structlog-logging T-006 removed the
# loguru half of the dual capture together with the backend).

_LevelName = namedtuple("_LevelName", "name")

# structlog's ProcessorFormatter bookkeeping plus the exception markers: never part of
# a rendered record (AC-003), so never part of a captured one either.
_CAPTURED_DROP = ("_record", "_from_structlog", "exc_info", "stack_info")


class CaptureRecord:
    """One captured log record, presented the way the suite reads records."""

    __slots__ = ("_fields", "_level", "_text")

    def __init__(self, text: str, level: str, fields: dict[str, Any]) -> None:
        self._text = text
        self._level = level
        self._fields = fields

    def __str__(self) -> str:
        return self._text

    def __repr__(self) -> str:
        return self._text

    def __getitem__(self, key: str) -> Any:
        if key == "level":
            return _LevelName(self._level)
        if key == "record":
            return self._fields
        return self._fields[key]


def capture_from_logrecord(record: logging.LogRecord) -> CaptureRecord:
    """Normalise a pipeline record.

    With ``ProcessorFormatter.wrap_for_formatter`` the record's ``msg`` **is** the
    structlog event dict, and the render chain runs later, inside the formatter, on
    the listener thread — so the capture reads the event dict as it stands at the
    emitting call site (only the emitting chain has run) and copies it, because the
    formatter mutates that same dict in place.
    """
    if isinstance(record.msg, dict):
        fields = {key: value for key, value in record.msg.items() if key not in _CAPTURED_DROP}
        text = str(fields.get("event", ""))
    else:  # a foreign stdlib record forwarded into the pipeline (AC-006)
        fields = {"message": record.getMessage()}
        text = fields["message"]
    return CaptureRecord(text, record.levelname, fields)


class PipelineCaptureHandler(logging.Handler):
    """Collect the pipeline's records for the duration of a test.

    Attached to the pipeline's own logger: that logger is non-propagating by design
    (AC-001), so a handler on the root logger never sees the feature's records. The
    ``_harness_capture`` marker is what ``logging_test_helpers._is_harness_handler``
    uses to keep this handler out of the managed-sink count (REQ-002/INV-001).
    """

    _harness_capture = True

    def __init__(self, records: list[Any], level: str = "DEBUG") -> None:
        super().__init__(level)
        self._records = records

    def emit(self, record: logging.LogRecord) -> None:
        self._records.append(capture_from_logrecord(record))


class FailingHandler(logging.Handler):
    """A sink whose ``emit`` always raises (EDGE-002 / AC-013 witness).

    Harness-marked, so ``logging_test_helpers._is_harness_handler`` keeps it out of the
    managed-sink count (REQ-002/INV-001).
    """

    _harness_capture = True

    def emit(self, record: logging.LogRecord) -> None:
        raise RuntimeError("sink failure")


@contextmanager
def failing_sink_attached() -> Iterator[None]:
    """Attach a :class:`FailingHandler` to the pipeline logger for a block (REQ-013 witness).

    Enter it *after* any capture handler is already attached: stdlib does not guard one
    handler's emit from the next, so the capture must be earlier in the chain to observe
    the records the failing sink does not stop.
    """
    from logging_test_helpers import pipeline_logger

    feature = pipeline_logger()
    handler = FailingHandler()
    feature.addHandler(handler)
    try:
        yield
    finally:
        feature.removeHandler(handler)


@contextmanager
def pipeline_capture(records: list[Any], level: str = "DEBUG") -> Iterator[None]:
    """Attach a :class:`PipelineCaptureHandler` to the pipeline logger for a block.

    The pipeline logger is also set to the capture level for the block and restored
    afterwards. The pipeline gates a record's level on the *logger*, where the retired
    loguru sink gated it on the *handler* (``logger.add(sink, level="DEBUG")``): a
    capture that only attached the handler would silently miss every record of a level
    another test had re-levelled the pipeline above (the level, not the traced call, is
    what changes).
    """
    from logging_test_helpers import pipeline_logger

    feature = pipeline_logger()
    handler = PipelineCaptureHandler(records, level)
    previous_level = feature.level
    feature.addHandler(handler)
    feature.setLevel(level)
    try:
        yield
    finally:
        feature.setLevel(previous_level)
        feature.removeHandler(handler)


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
        return [str(r) for r in self._raw]

    def __len__(self) -> int:
        return len(self._raw)

    def __iter__(self) -> Iterator[str]:
        return iter(self._texts())

    def __getitem__(self, i: int) -> str:
        return self._texts()[i]


@contextmanager
def capture_records(level: str = "DEBUG") -> Iterator[_LiveMessages]:
    """Capture log records for the duration of the ``with`` block.

    Yields a fresh live view of message-text strings per invocation, so
    Hypothesis iterations do not accumulate across each other. The view
    reflects records added while the block is active. Every record arrives
    through the logging pipeline (the loguru half of the dual capture was removed
    by structlog-logging T-006).
    """
    raw: list[Any] = []

    with pipeline_capture(raw, level):
        yield _LiveMessages(raw)
