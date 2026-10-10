"""Contract tests for the five install operations' public API.

Normative basis: ``docs/specs/settings-public-registry-setter.md`` REQ-004,
REQ-005, REQ-014, REQ-016 / AC-007, AC-008, AC-020 and NFR-001 (change
``settings-public-registry-setter``, CROSS-CUTTING).

* AC-007 — each install operation is a module-level function of its own feature
  package, exported by it, taking exactly one parameter annotated with the
  feature's concrete class and returning ``None``.
* AC-008 — the install path performs no runtime type check on that parameter and
  adds no exception type to the feature's public error surface.
* AC-020 — the permission catalog is untouched and none of the five wiring
  functions became an action (``user-roles-permissions.md`` REQ-004/REQ-005,
  AC-006 are cited unchanged).
* NFR-001 — the change is purely additive: every pre-change public symbol of the
  five packages is still exported with the same signature. ``user-roles-permissions.md``
  NFR-003 and ``search.md`` NFR-003 do not themselves guarantee that, so the
  baseline is frozen here (the 61 catalog keys and the 104 exported names are the
  pre-change state, recorded before any of the five installers existed).
"""

from __future__ import annotations

import importlib
import inspect
from typing import Any, Final

from singleton_install_test_helpers import SLOTS, witness_slots

from backend.permissions.catalog import PermissionCatalog

# The features that declare catalog actions (the catalog's only input).
_ACTION_MODULES: Final[tuple[str, ...]] = (
    "backend.authentication.feature_actions",
    "backend.filemanagement.feature_actions",
    "backend.mail.feature_actions",
    "backend.search.feature_actions",
    "backend.sessionmanagement.feature_actions",
    "backend.settings.feature_actions",
    "backend.usermanagement.feature_actions",
)

# The catalog as registered before this change: 61 action keys over 7 features.
_CATALOG_BASELINE: Final[dict[str, tuple[str, ...]]] = {
    "authentication": (
        "begin_passkey_login",
        "begin_passkey_registration",
        "complete_passkey_login",
        "complete_passkey_registration",
        "complete_password_reset",
        "delete_passkey",
        "list_passkeys",
        "login",
        "logout",
        "request_password_reset",
        "session_info",
    ),
    "filemanagement": (
        "delete",
        "delete_avatar",
        "download",
        "get_avatar",
        "get_file",
        "list_files",
        "open",
        "replace_avatar",
        "upload",
        "upload_avatar",
    ),
    "mail": ("send_email", "send_email_verification_email", "send_password_reset_email"),
    "search": ("search",),
    "sessionmanagement": (
        "cleanup_expired",
        "list_sessions",
        "logout_all_sessions",
        "logout_other_sessions",
        "revoke_all_sessions",
        "revoke_session",
    ),
    "settings": (
        "create_template",
        "delete_template",
        "get_definition",
        "get_status",
        "get_template",
        "get_value",
        "grouped_views",
        "has",
        "has_template",
        "list_templates",
        "load_template",
        "register",
        "register_feature",
        "reset",
        "reset_all",
        "set_value",
        "to_view",
        "update_template",
        "views",
    ),
    "usermanagement": (
        "activate_user",
        "change_password",
        "create_user",
        "deactivate_user",
        "delete_user",
        "get_user",
        "get_user_by_username",
        "list_users",
        "set_role",
        "update_user",
        "verify_password",
    ),
}

# Each package's ``__all__`` before this change (104 names) — the additive baseline.
_PUBLIC_API_BASELINE: Final[dict[str, frozenset[str]]] = {
    "backend.settings": frozenset(
        {
            "ListSpec",
            "MemoryTemplateRepository",
            "SelectOption",
            "SelectSpec",
            "SettingChanged",
            "SettingDefinition",
            "SettingKind",
            "SettingStatus",
            "SettingView",
            "SettingsError",
            "SettingsNotFoundError",
            "SettingsRegistrationError",
            "SettingsRegistry",
            "SettingsValidationError",
            "SliderSpec",
            "Template",
            "TemplateNotFoundError",
            "TemplateRepository",
            "TemplateStorageError",
            "TemplateValidationError",
            "ValueRepository",
            "ValueStorageError",
            "YamlTemplateRepository",
            "YamlValueRepository",
            "get_settings_registry",
            "register_actions",
            "reset_settings_registry",
        }
    ),
    "backend.eventbus": frozenset({"EventBus", "get_event_bus", "register_settings", "reset_event_bus"}),
    "backend.permissions": frozenset(
        {
            "AuthorizationError",
            "BOOTSTRAP_SYSTEM_PERMISSIONS",
            "EventPublisher",
            "GrantRepository",
            "MemoryGrantRepository",
            "MemoryRoleRepository",
            "MemorySystemPrincipalRepository",
            "PermissionCatalog",
            "PermissionDenied",
            "PermissionDeniedError",
            "PermissionEvent",
            "PermissionRead",
            "PermissionService",
            "Role",
            "RoleAlreadyExistsError",
            "RoleCreated",
            "RoleDeleted",
            "RoleInUseError",
            "RoleNotFoundError",
            "RolePermission",
            "RolePermissionsChanged",
            "RoleProtectedError",
            "RoleRead",
            "RoleRepository",
            "SqliteGrantRepository",
            "SqliteRoleRepository",
            "SqliteSystemPrincipalRepository",
            "SystemPrincipalPermission",
            "SystemPrincipalRepository",
            "UnknownPermissionError",
            "get_permission_service",
            "register_settings",
            "reset_permission_service",
        }
    ),
    "backend.search": frozenset(
        {
            "EventPublisher",
            "FieldType",
            "FilterCondition",
            "FilterGroup",
            "FilterOperator",
            "InMemorySource",
            "MalformedQueryError",
            "SearchError",
            "SearchQuery",
            "SearchResult",
            "SearchResultItem",
            "SearchService",
            "SearchSource",
            "Sort",
            "SourceFailure",
            "SourceField",
            "SourceItem",
            "SourcePage",
            "SourceQueryContext",
            "SourceQueryFailed",
            "SourceQueryFailedError",
            "SourceRegistered",
            "SourceUnregistered",
            "UnknownSourceError",
            "get_search_service",
            "register_actions",
            "register_settings",
            "reset_search_service",
        }
    ),
    "backend.sessionmanagement": frozenset(
        {
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
        }
    ),
}

# The singleton API whose signature must not change (NFR-001 "same signature").
_SINGLETON_SIGNATURE_BASELINE: Final[dict[str, str]] = {
    "backend.settings.get_settings_registry": "(required: 'bool' = True) -> 'SettingsRegistry | None'",
    "backend.settings.reset_settings_registry": "() -> 'None'",
    "backend.eventbus.get_event_bus": "() -> 'EventBus'",
    "backend.eventbus.reset_event_bus": "() -> 'None'",
    "backend.permissions.get_permission_service": "() -> 'PermissionService'",
    "backend.permissions.reset_permission_service": "() -> 'None'",
    "backend.search.get_search_service": (
        "(event_bus: 'EventPublisher | None' = None, settings_registry: 'SettingsRegistry | None' = None, "
        "permission_service: 'PermissionChecker | None' = None) -> 'SearchService'"
    ),
    "backend.search.reset_search_service": "() -> 'None'",
    "backend.sessionmanagement.get_session_service": (
        "(repository: 'SessionRepository | None' = None, event_bus: 'EventPublisher | None' = None, "
        "settings_registry: 'SettingsRegistry | None' = None) -> 'SessionService'"
    ),
    "backend.sessionmanagement.reset_session_service": "() -> 'None'",
}

# The exception names each package exported before this change.
_ERROR_BASELINE: Final[dict[str, frozenset[str]]] = {
    module: frozenset(name for name in names if name.endswith("Error"))
    for module, names in _PUBLIC_API_BASELINE.items()
}


def _annotation_name(annotation: Any) -> str:
    """The bare class name of an annotation, resolved or stringified."""
    return getattr(annotation, "__name__", str(annotation)).rsplit(".", 1)[-1]


def _build_catalog() -> PermissionCatalog:
    """The permission catalog as the composition root builds it at startup."""
    catalog = PermissionCatalog()
    for module_name in _ACTION_MODULES:
        importlib.import_module(module_name).register_actions(catalog)
    return catalog


def _install_error(slot: Any, instance: Any) -> BaseException | None:
    """The exception the install operation raised for a valid instance, or ``None``."""
    try:
        slot.install(instance)
    except BaseException as exc:  # reported through the assertion in the test
        return exc
    return None


@witness_slots
def test_ac_007_signature_takes_concrete_instance() -> None:
    """AC-007 (REQ-004, REQ-014): each install operation is exported and takes exactly one concretely annotated parameter."""
    for slot in SLOTS:
        instance = slot.new()
        installer = getattr(slot.module, slot.installer)  # AttributeError until the operation exists
        signature = inspect.signature(installer)
        parameters = list(signature.parameters.values())
        assert len(parameters) == 1, f"{slot.name()}: {slot.installer}{signature} takes {len(parameters)} parameters"
        parameter = parameters[0]
        assert parameter.kind in (parameter.POSITIONAL_ONLY, parameter.POSITIONAL_OR_KEYWORD), (
            f"{slot.name()}: {slot.installer}'s parameter is {parameter.kind}"
        )
        assert parameter.default is parameter.empty, f"{slot.name()}: {slot.installer}'s parameter has a default"
        assert _annotation_name(parameter.annotation) == type(instance).__name__, (
            f"{slot.name()}: {slot.installer}'s parameter is annotated {parameter.annotation!r}, "
            f"expected the concrete {type(instance).__name__}"
        )
        assert str(signature.return_annotation) == "None", (
            f"{slot.name()}: {slot.installer} returns {signature.return_annotation!r}, expected None"
        )
        assert slot.installer in slot.module.__all__, (
            f"{slot.name()}: {slot.installer} is not exported by the feature package's public API"
        )
        slot.dispose(instance)


@witness_slots
def test_ac_008_no_runtime_type_check_no_new_error() -> None:
    """AC-008 (REQ-005): a valid instance installs without an exception, no type check guards the parameter, no new error type appears."""
    for slot in SLOTS:
        installer = getattr(slot.module, slot.installer)  # AttributeError until the operation exists
        signature = inspect.signature(inspect.unwrap(installer))
        parameter = next(iter(signature.parameters.values()), None)
        assert parameter is not None, f"{slot.name()}: {slot.installer} takes no parameter"
        source = inspect.getsource(inspect.unwrap(installer))
        for check in (f"isinstance({parameter.name}", f"type({parameter.name}", f"cast({parameter.name}"):
            assert check not in source, f"{slot.name()}: {slot.installer} performs a runtime type check ({check})"

        instance = slot.new()
        slot.clear()
        try:
            raised = _install_error(slot, instance)
            assert raised is None, f"{slot.name()}: installing a valid {type(instance).__name__} raised {raised!r}"
            errors = {name for name in slot.module.__all__ if name.endswith("Error")}
            new_errors = errors - _ERROR_BASELINE[slot.module.__name__]
            assert not new_errors, f"{slot.name()}: the change added public error type(s) {sorted(new_errors)}"
        finally:
            slot.dispose(instance)
            slot.clear()


def test_ac_020_permission_catalog_unchanged() -> None:
    """AC-020 (REQ-016): the action set is identical to before and none of the five wiring functions is an action."""
    for slot in SLOTS:
        # Anti-vacuity: "not a catalog entry" is only a fact once the function exists (PROBLEMS.md P-53 reasoning).
        assert hasattr(slot.module, slot.installer), (
            f"{slot.name()}: {slot.installer} does not exist, so 'not a catalog action' is vacuous"
        )

    catalog = _build_catalog()
    registered = {action.permission for action in catalog.actions()}
    baseline = {f"{feature}.{action}" for feature, actions in _CATALOG_BASELINE.items() for action in actions}
    assert registered == baseline, (
        f"the permission catalog changed: added {sorted(registered - baseline)}, "
        f"removed {sorted(baseline - registered)}"
    )
    assert catalog.features() == frozenset(_CATALOG_BASELINE), "the catalog's feature set changed"

    actions = {permission.split(".", 1)[1] for permission in registered}
    installers = {slot.installer for slot in SLOTS}
    assert not (actions & installers), f"an install operation became a catalog action: {sorted(actions & installers)}"


def test_nfr_001_public_api_additive() -> None:
    """NFR-001 (REQ-014): every pre-change public symbol is still exported with the same signature, and the five install operations are the addition."""
    for module_name, baseline in _PUBLIC_API_BASELINE.items():
        current = frozenset(importlib.import_module(module_name).__all__)
        removed = baseline - current
        assert not removed, f"{module_name}: public symbol(s) no longer exported: {sorted(removed)}"

    for dotted, signature in _SINGLETON_SIGNATURE_BASELINE.items():
        module_name, _, name = dotted.rpartition(".")
        actual = str(inspect.signature(getattr(importlib.import_module(module_name), name)))
        assert actual == signature, f"{dotted}: signature changed from {signature!r} to {actual!r}"

    for slot in SLOTS:
        assert slot.installer in slot.module.__all__, (
            f"{slot.name()}: {slot.installer} is missing from the public API, so the change is not additive"
        )
