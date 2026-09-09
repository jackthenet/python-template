"""AC-002 / AC-004 / AC-005: services, concrete repos/providers, and module
functions are traced and produce entry + exit log records.

Tests verify tracing by capturing log records (attach a sink, call the method,
assert the produced records).
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import timedelta
from typing import Any

from logging_coverage_test_helpers import (
    INVENTORY_MODULE_FUNCTIONS,
    entry_records,
    exit_records,
    for_qualname,
    parse_elapsed_ms,
)

from backend.authentication.repository import (
    SqlitePasswordResetRepository,
    SqliteSessionRepository,
    SqliteWebAuthnCredentialRepository,
)
from backend.authentication.tracker import InMemoryAttemptTracker
from backend.authentication.webauthn import PyWebAuthnProvider
from backend.eventbus.eventbus import EventBus
from backend.settings.registry import SettingsRegistry
from backend.settings.repository import MemoryTemplateRepository, YamlTemplateRepository
from backend.usermanagement.repository import SqliteUserRepository

# PyWebAuthnProvider's configured slow threshold (spec section 3.3); verified
# via the decorator attribute because its methods require py-webauthn (not
# installed in the test environment).
_WEBAUTHN_SLOW_THRESHOLD_MS = 500


def test_service_registry_classes_traced(log_records: list[Any]) -> None:
    """AC-002: EventBus and SettingsRegistry public methods produce entry + exit records."""
    # EventBus.publish
    bus = EventBus()
    try:
        from eventbus_test_helpers import UserCreated

        bus.publish(UserCreated(user_id="u1", email="e1"))
    finally:
        bus.shutdown()
    assert len([r for r in entry_records(log_records) if "EventBus.publish" in str(r)]) == 1
    assert len([r for r in exit_records(log_records) if "EventBus.publish" in str(r)]) == 1

    # SettingsRegistry.has
    # Note: the EventBus() constructor above also calls SettingsRegistry.has
    # (checking if eventbus.max_queue_size is registered), so we expect 2 entry
    # records total (one from the EventBus constructor, one from the test's call).
    reg = SettingsRegistry(template_repository=MemoryTemplateRepository())
    reg.has("some.key")
    assert len([r for r in entry_records(log_records) if "SettingsRegistry.has" in str(r)]) == 2
    assert len([r for r in exit_records(log_records) if "SettingsRegistry.has" in str(r)]) == 2


def test_concrete_repo_provider_traced(log_records: list[Any], tmp_path: Any) -> None:
    """AC-004: concrete repository/provider classes produce entry + exit records;
    the exit record includes elapsed milliseconds."""
    db = f"sqlite:///{tmp_path}/app.db"

    # (qualname, zero-arg callable that invokes one public method).
    subjects: list[tuple[str, Callable[[], Any]]] = [
        ("SqliteUserRepository.get_by_username", lambda: SqliteUserRepository(db).get_by_username("probe")),
        ("SqliteSessionRepository.delete_expired", lambda: SqliteSessionRepository(db).delete_expired()),
        ("SqlitePasswordResetRepository.get_by_token_hash", lambda: SqlitePasswordResetRepository(db).get_by_token_hash("probe")),
        ("SqliteWebAuthnCredentialRepository.get_by_credential_id", lambda: SqliteWebAuthnCredentialRepository(db).get_by_credential_id("probe")),
        (
            "InMemoryAttemptTracker.is_locked",
            lambda: InMemoryAttemptTracker(3, timedelta(minutes=5)).is_locked("probe"),
        ),
        ("MemoryTemplateRepository.list", lambda: MemoryTemplateRepository().list()),
        ("YamlTemplateRepository.list", lambda: YamlTemplateRepository(tmp_path / "templates").list()),
    ]

    for qualname, invoke in subjects:
        invoke()
        entries = for_qualname(entry_records(log_records), qualname)
        exits = for_qualname(exit_records(log_records), qualname)
        assert len(entries) == 1, f"{qualname}: expected 1 entry record"
        assert len(exits) == 1, f"{qualname}: expected 1 exit record"
        # The exit record includes elapsed milliseconds.
        assert parse_elapsed_ms(str(exits[0])) is not None, f"{qualname}: exit record has no elapsed ms"

    # PyWebAuthnProvider is traced, but its methods require py-webauthn (not
    # installed in the test environment — the auth suite uses a fake provider),
    # so tracing is verified via the decorator attributes instead of a call.
    assert getattr(PyWebAuthnProvider, "__logged_class__", False) is True, "PyWebAuthnProvider: not traced"
    assert getattr(PyWebAuthnProvider, "slow_threshold_ms", None) == _WEBAUTHN_SLOW_THRESHOLD_MS, "PyWebAuthnProvider: wrong slow threshold"


def test_module_functions_traced(log_records: list[Any]) -> None:
    """AC-005: every public module-level function produces entry + exit records."""
    # Call each inventory module function.
    for name, fn in INVENTORY_MODULE_FUNCTIONS.items():
        if name == "hash_token":
            fn("probe")
        else:
            fn()

    for name in INVENTORY_MODULE_FUNCTIONS:
        # Match the exact qualname (module functions have no class prefix).
        # "At least 1" (not "exactly 1"): a traced function may be invoked
        # internally by another traced function (e.g. get_settings_registry
        # calls get_event_bus), so the requirement is that it produces
        # records, not that it is called exactly once.
        entries = [r for r in entry_records(log_records) if str(r).startswith(f">> {name} called")]
        exits = [r for r in exit_records(log_records) if str(r).startswith(f"<< {name} returned")]
        assert len(entries) >= 1, f"{name}: expected at least 1 entry record"
        assert len(exits) >= 1, f"{name}: expected at least 1 exit record"
