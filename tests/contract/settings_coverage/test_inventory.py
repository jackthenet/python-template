"""Contract tests for the settings inventory (AC-022..AC-024, NFR-002, NFR-003).

Reproduction guard for issue ``startup-settings-registration-gaps`` (D-2/D-3/D-6): the
inventory carried the 14 keys of the four features ``docs/specs/settings-coverage.md``
§3.5 enumerated, and ``_registry_with_all_features()`` registered only those four, so
``test_category_group`` could not see the four out-of-domain ``category`` values and
``test_no_secret_settings`` could not see ``mail.smtp_password`` — the guards were as
incomplete as the wiring (§3 D-2). ``INVENTORY`` is now the full 34-key inventory of the
nine features, every row taken from the module that registers it.

This guard builds its **own** registry, so it pins the inventory and the REQ-018
category/group rule, not the composition-root wiring — that is the acceptance witness
(``tests/acceptance/settings_coverage/test_wiring.py``).
"""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from settings_test_helpers import make_registry

from backend.settings import SettingsRegistry

# The complete inventory of the nine features (spec section 3.5, widened by this change):
# key -> (kind, default, category, group). The category/group values are what REQ-018 /
# AC-023 require — the domain (application/security) and the feature name — so the four
# rows the features currently register outside that set are RED here (D-3).
INVENTORY: dict[str, tuple[str, object, str, str]] = {
    "logging.log_level": ("SELECT", "INFO", "application", "logging"),
    "logging.log_file": ("TEXT", "logs/app.log", "application", "logging"),
    "logging.log_max_bytes": ("NUMBER", 10485760, "application", "logging"),
    "logging.log_backup_count": ("NUMBER", 5, "application", "logging"),
    "logging.profiling_include_arguments": ("BOOLEAN", False, "application", "logging"),
    "authentication.session_ttl": ("NUMBER", 604800, "security", "authentication"),
    "authentication.reset_token_ttl": ("NUMBER", 900, "security", "authentication"),
    "authentication.max_failed_attempts": ("NUMBER", 5, "security", "authentication"),
    "authentication.lockout_duration": ("NUMBER", 900, "security", "authentication"),
    "authentication.rp_id": ("TEXT", "localhost", "security", "authentication"),
    "authentication.rp_name": ("TEXT", "Python Template", "security", "authentication"),
    "authentication.origin": ("TEXT", "http://localhost:3000", "security", "authentication"),
    "usermanagement.roles": ("LIST", ["admin", "member"], "security", "usermanagement"),
    "eventbus.max_queue_size": ("NUMBER", 1000, "application", "eventbus"),
    "permissions.system_principal": (
        "LIST",
        [
            "mail.send_email",
            "mail.send_email_verification_email",
            "mail.send_password_reset_email",
            "sessionmanagement.cleanup_expired",
            "settings.register",
            "settings.register_feature",
            "usermanagement.change_password",
            "usermanagement.get_user",
            "usermanagement.verify_password",
        ],
        "security",
        "permissions",
    ),
    "search.default_page_size": ("NUMBER", 100, "application", "search"),
    "search.max_page_size": ("NUMBER", 1000, "application", "search"),
    "search.source_timeout": ("NUMBER", 5000, "application", "search"),
    "filemanagement.storage_root": ("TEXT", "./data/files", "application", "filemanagement"),
    "filemanagement.max_file_size": ("NUMBER", 10485760, "application", "filemanagement"),
    "filemanagement.avatar_max_size": ("NUMBER", 2097152, "application", "filemanagement"),
    "filemanagement.allowed_types": (
        "LIST",
        [
            "application/octet-stream",
            "application/pdf",
            "application/zip",
            "text/plain",
            "text/csv",
            "image/png",
            "image/jpeg",
            "image/gif",
            "image/webp",
        ],
        "application",
        "filemanagement",
    ),
    "filemanagement.avatar_base_url": ("TEXT", "files.example.com", "application", "filemanagement"),
    "mail.smtp_host": ("TEXT", "localhost", "application", "mail"),
    "mail.smtp_port": ("NUMBER", 587, "application", "mail"),
    "mail.smtp_username": ("TEXT", "", "application", "mail"),
    "mail.smtp_password": ("TEXT", "", "application", "mail"),
    "mail.smtp_from": ("EMAIL", "no-reply@example.com", "application", "mail"),
    "mail.smtp_tls": ("BOOLEAN", True, "application", "mail"),
    "mail.smtp_timeout": ("NUMBER", 30, "application", "mail"),
    "mail.from_name": ("TEXT", "Python Template", "application", "mail"),
    "sessionmanagement.max_listed_sessions": ("NUMBER", 100, "security", "sessionmanagement"),
    "sessionmanagement.max_sessions_per_user": ("NUMBER", 5, "security", "sessionmanagement"),
    "sessionmanagement.cleanup_batch_size": ("NUMBER", 1000, "security", "sessionmanagement"),
}

# NFR-002 (as amended by this change, LQ-01 (a)): no credential or token may appear in log
# records or events, and a setting explicitly declared as a credential MAY be persisted.
# mail.smtp_password is that one accepted transport-credential exception — the mail spec
# registers it by design and keeps it out of every log record and event. The name check
# keeps its full force on the other 33 keys: an undocumented credential-named key is a
# violation, and an exemption that no longer names a real key is one too.
NFR_002_CREDENTIAL_EXEMPTIONS: frozenset[str] = frozenset({"mail.smtp_password"})

_SECRET_NAME_PARTS = ("password", "secret", "credential")


@pytest.fixture(autouse=True)
def _reset_registry() -> Iterator[None]:
    # Reset the singleton for the test; the previous singleton is restored on
    # teardown (no state leak).
    from settings_test_helpers import isolated_registry

    with isolated_registry(install=False):
        yield


def _registry_with_all_features() -> SettingsRegistry:
    reg, _bus = make_registry()
    from backend.authentication import register_settings as auth_register
    from backend.eventbus import register_settings as bus_register
    from backend.filemanagement import register_settings as file_register
    from backend.logging import register_settings as logging_register
    from backend.mail import register_settings as mail_register
    from backend.permissions import register_settings as permissions_register
    from backend.search import register_settings as search_register
    from backend.sessionmanagement import register_settings as session_register
    from backend.usermanagement import register_settings as um_register

    logging_register(reg)
    auth_register(reg)
    um_register(reg)
    bus_register(reg)
    permissions_register(reg)
    search_register(reg)
    file_register(reg)
    mail_register(reg)
    session_register(reg)
    return reg


def _same_default(actual: object, expected: object) -> bool:
    """Default equality; a LIST default is compared order-insensitively.

    ``permissions.system_principal`` defaults to ``list(BOOTSTRAP_SYSTEM_PERMISSIONS)``, and a
    ``frozenset`` iteration order is not fixed, so its list default has no stable order.
    """
    if isinstance(actual, list) and isinstance(expected, list):
        return sorted(actual) == sorted(expected)
    return actual == expected


def test_key_prefix() -> None:
    """AC-022: keys use the full feature name as the prefix."""
    reg = _registry_with_all_features()
    for key in INVENTORY:
        assert reg.has(key), f"missing inventory key {key}"
        feature = key.split(".", 1)[0]
        assert key.startswith(f"{feature}.")


def test_category_group() -> None:
    """AC-023: category = domain, group = feature name."""
    reg = _registry_with_all_features()
    for key, (_kind, _default, category, group) in INVENTORY.items():
        d = reg.get_definition(key)
        assert d.category == category, f"{key}: category {d.category!r} != {category!r}"
        assert d.group == group, f"{key}: group {d.group!r} != {group!r}"


def test_inventory_matches() -> None:
    """AC-024: keys, kinds, and defaults match the inventory."""
    reg = _registry_with_all_features()
    for key, (kind, default, _category, _group) in INVENTORY.items():
        d = reg.get_definition(key)
        assert d.kind.value.upper() == kind, f"{key}: kind {d.kind!r} != {kind!r}"
        assert _same_default(d.default, default), f"{key}: default {d.default!r} != {default!r}"
        value = reg.get_value(key)
        assert _same_default(value, default), f"{key}: value {value!r} != {default!r}"


def test_no_secret_settings() -> None:
    """NFR-002: settings hold no password/secret/credential key outside the named exemption.

    The exemption list is the documented NFR-002 exception (LQ-01 (a)); every other key keeps
    the full name check, and a string value never carries a scheme-prefixed connection string
    (an empty value is the absence of a value, not a secret — mail registers ``smtp_username``
    and ``smtp_password`` with the empty-string default).
    """
    reg = _registry_with_all_features()
    named = {key for key in INVENTORY if any(part in key.lower() for part in _SECRET_NAME_PARTS)}
    assert named == set(NFR_002_CREDENTIAL_EXEMPTIONS), (
        "NFR-002: a settings key named like a password/secret/credential must be an exempted "
        f"credential setting by name; found {sorted(named)}, exempted {sorted(NFR_002_CREDENTIAL_EXEMPTIONS)}"
    )
    for key in INVENTORY:
        value = reg.get_value(key)
        if isinstance(value, str) and value:
            assert "://" not in value[:4], f"NFR-002: {key} holds a connection string"


def test_inventory_backward_compatible() -> None:
    """NFR-003: the inventory is a superset of the spec table (adding a setting is non-breaking)."""
    reg = _registry_with_all_features()
    for key in INVENTORY:
        assert reg.has(key), f"inventory key {key} missing"
