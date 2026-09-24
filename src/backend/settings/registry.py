"""The settings registry: registration, validated value access, resets,
hierarchy/views, and template CRUD.
"""

from __future__ import annotations

import threading
from typing import TYPE_CHECKING, Any

from loguru import logger

from backend.logging import logged, logged_class
from backend.shared import PermissionChecker, Principal, requires_permission

if TYPE_CHECKING:
    from backend.eventbus import EventBus
from backend.settings.exceptions import (
    SettingsNotFoundError,
    SettingsRegistrationError,
    SettingsValidationError,
    TemplateNotFoundError,
    TemplateValidationError,
)
from backend.settings.models import (
    SettingChanged,
    SettingDefinition,
    SettingStatus,
    SettingView,
    Template,
    is_template_name_valid,
    value_valid_for,
)
from backend.settings.repository import (
    MemoryTemplateRepository,
    TemplateRepository,
    ValueRepository,
    YamlValueRepository,
)

# ADR-071: the default trailing principal of every enforced method is the
# system principal (user_id=None; EDGE-022). A module-level singleton keeps
# the argument defaults lint-clean (B008) and identical across methods.
_SYSTEM_PRINCIPAL = Principal()

_registry: list[SettingsRegistry | None] = [None]


@logged_class(slow_threshold_ms=250)
class SettingsRegistry:
    """Central registry of typed settings with template support.

    The class is traced via the shared logging feature (``@logged_class``);
    each public method produces entry and exit log records.
    """

    def __init__(
        self,
        event_bus: EventBus | None = None,
        template_repository: TemplateRepository | None = None,
        value_repository: ValueRepository | None = None,
        permission_service: PermissionChecker | None = None,
    ) -> None:
        # Lazy import: backend.eventbus imports backend.settings (via its
        # feature_settings module), so importing it at module level here would
        # create a circular import.
        from backend.eventbus import get_event_bus

        self._event_bus = event_bus if event_bus is not None else get_event_bus()
        self._repository = template_repository if template_repository is not None else MemoryTemplateRepository()
        self._value_repository = (
            value_repository if value_repository is not None else YamlValueRepository("settings")
        )
        self._definitions: dict[str, SettingDefinition] = {}
        self._values: dict[str, Any] = {}
        self._lock = threading.Lock()
        # Persisted values are loaded once at construction (REQ-009 / NFR-001);
        # they take precedence over definition defaults (REQ-011).
        self._persisted: dict[str, Any] = self._value_repository.load() or {}
        # D13/ADR-071: the injected checker enforces settings.<method> at
        # entry (REQ-024); None = standalone mode (no enforcement,
        # today's behavior — AC-031).
        self._permission_service = permission_service

    # -- Registration --

    @requires_permission("settings.register")
    def register(self, definition: SettingDefinition, principal: Principal = _SYSTEM_PRINCIPAL) -> None:
        """Register a setting. Duplicate keys are rejected."""
        with self._lock:
            if definition.key in self._definitions:
                logger.warning("duplicate registration: key={}", definition.key)
                raise SettingsRegistrationError(f"duplicate key {definition.key}")
            self._definitions[definition.key] = definition
            # Persisted values take precedence over definition defaults (REQ-011).
            self._values[definition.key] = self._persisted.get(
                definition.key, definition.default
            )
        logger.debug("setting registered: key={} kind={}", definition.key, definition.kind)
        self._persist_values()

    @property
    def value_repository(self) -> ValueRepository:
        """The value repository backing this registry (REQ-010)."""
        return self._value_repository

    @requires_permission("settings.register_feature")
    def register_feature(
        self, feature: str, definitions: list[SettingDefinition], principal: Principal = _SYSTEM_PRINCIPAL
    ) -> None:
        """Register a feature's settings; each key must start with ``f"{feature}."``."""
        prefix = f"{feature}."
        for d in definitions:
            if not d.key.startswith(prefix):
                raise SettingsRegistrationError(f"key {d.key} does not start with {prefix}")
        for d in definitions:
            self.register(d)
        logger.debug("feature settings registered: feature={} count={}", feature, len(definitions))

    # -- Lookup --

    @requires_permission("settings.has")
    def has(self, key: str, principal: Principal = _SYSTEM_PRINCIPAL) -> bool:
        """Return True iff ``key`` is registered."""
        with self._lock:
            return key in self._definitions

    @requires_permission("settings.get_definition")
    def get_definition(self, key: str, principal: Principal = _SYSTEM_PRINCIPAL) -> SettingDefinition:
        """Return the definition of ``key`` (SettingsNotFoundError if unknown)."""
        with self._lock:
            return self._require_definition(key)

    @requires_permission("settings.get_value")
    def get_value(self, key: str, principal: Principal = _SYSTEM_PRINCIPAL) -> Any:
        """Return the current value of ``key`` (SettingsNotFoundError if unknown)."""
        with self._lock:
            self._require_definition(key)
            return self._values[key]

    @requires_permission("settings.set_value")
    def set_value(self, key: str, value: Any, principal: Principal = _SYSTEM_PRINCIPAL) -> Any:
        """Validate and store ``value`` for ``key``; publish SettingChanged."""
        with self._lock:
            d = self._require_definition(key)
            if not value_valid_for(d, value):
                logger.warning("value set rejected (invalid): key={}", key)
                raise SettingsValidationError(f"value is invalid for {key}")
            previous = self._values[key]
            self._values[key] = value
        logger.debug("value set: key={}", key)
        self._persist_values()
        self._publish_setting_changed(key, value, previous)
        return value

    # -- Resets --

    @requires_permission("settings.reset")
    def reset(self, key: str, principal: Principal = _SYSTEM_PRINCIPAL) -> None:
        """Restore the default of ``key``; publish SettingChanged."""
        with self._lock:
            d = self._require_definition(key)
            previous = self._values[key]
            self._values[key] = d.default
        logger.debug("value reset: key={}", key)
        self._persist_values()
        self._publish_setting_changed(key, d.default, previous)

    @requires_permission("settings.reset_all")
    def reset_all(self, principal: Principal = _SYSTEM_PRINCIPAL) -> None:
        """Restore all settings to their defaults; one event per setting."""
        with self._lock:
            items = list(self._definitions.items())
        for key, d in items:
            with self._lock:
                previous = self._values[key]
                self._values[key] = d.default
            logger.debug("value reset: key={}", key)
            self._publish_setting_changed(key, d.default, previous)
        self._persist_values()

    # -- Status / views --

    @requires_permission("settings.get_status")
    def get_status(self, key: str, principal: Principal = _SYSTEM_PRINCIPAL) -> SettingStatus:
        """Return the derived status of ``key``."""
        with self._lock:
            d = self._require_definition(key)
            current = self._values[key]
        return SettingStatus.DEFAULT if current == d.default else SettingStatus.MODIFIED

    @requires_permission("settings.to_view")
    def to_view(self, key: str, principal: Principal = _SYSTEM_PRINCIPAL) -> SettingView:
        """Return the renderable view of ``key``."""
        with self._lock:
            d = self._require_definition(key)
            view = SettingView(
                key=d.key,
                kind=d.kind,
                title=d.title,
                description=d.description,
                category=d.category,
                group=d.group,
                default=d.default,
                value=self._values[key],
                status=SettingStatus.DEFAULT if self._values[key] == d.default else SettingStatus.MODIFIED,
                slider=d.slider,
                select=d.select,
                list_spec=d.list_spec,
                pattern=d.pattern,
                min_length=d.min_length,
                max_length=d.max_length,
                min_value=d.min_value,
                max_value=d.max_value,
            )
        return view

    @requires_permission("settings.views")
    def views(self, principal: Principal = _SYSTEM_PRINCIPAL) -> list[SettingView]:
        """Return the views of all registered settings."""
        with self._lock:
            keys = list(self._definitions)
        return [self.to_view(k) for k in keys]

    @requires_permission("settings.grouped_views")
    def grouped_views(self, principal: Principal = _SYSTEM_PRINCIPAL) -> dict[str, dict[str, list[SettingView]]]:
        """Return the category -> group -> views structure."""
        with self._lock:
            items = list(self._definitions.items())
        result: dict[str, dict[str, list[SettingView]]] = {}
        for key, d in items:
            view = self.to_view(key)
            result.setdefault(d.category or "", {}).setdefault(d.group or "", []).append(view)
        return result

    # -- Templates --

    @requires_permission("settings.create_template")
    def create_template(
        self,
        name: str,
        category: str,
        group: str | None,
        values: dict[str, Any] | None = None,
        principal: Principal = _SYSTEM_PRINCIPAL,
    ) -> Template:
        """Create a template scoped to (category, group)."""
        if not is_template_name_valid(name):
            logger.warning("template create rejected (invalid name): name={}", name)
            raise TemplateValidationError(f"invalid template name {name}")
        with self._lock:
            if self._repository.get(name) is not None:
                logger.warning("template create rejected (duplicate): name={}", name)
                raise TemplateValidationError(f"template name {name} already exists")
            scope_keys = self._scope_keys(category, group)
            if values is None:
                captured = {k: self._values[k] for k in scope_keys}
            else:
                if set(values.keys()) != set(scope_keys):
                    logger.warning("template create rejected (scope): name={}", name)
                    raise TemplateValidationError("values must exactly cover the scope")
                for k in scope_keys:
                    if not value_valid_for(self._definitions[k], values[k]):
                        logger.warning("template create rejected (invalid value): name={} key={}", name, k)
                        raise TemplateValidationError(f"value for {k} is invalid")
                captured = dict(values)
            template = Template(name=name, category=category, group=group, values=captured)
            self._repository.save(template)
        logger.debug("template created: name={} category={} group={}", name, category, group)
        return template

    @requires_permission("settings.load_template")
    def load_template(self, name: str, principal: Principal = _SYSTEM_PRINCIPAL) -> None:
        """Set each of the template's values (validated at creation); others left as-is."""
        with self._lock:
            template = self._repository.get(name)
        if template is None:
            raise TemplateNotFoundError(f"unknown template {name}")
        # Batch-apply values: skip re-validation (values were validated at
        # template creation) but still check key registration.
        with self._lock:
            for key, value in template.values.items():
                if key not in self._definitions:
                    raise SettingsNotFoundError(f"unknown setting {key}")
                previous = self._values[key]
                self._values[key] = value
                self._publish_setting_changed(key, value, previous)
        logger.debug("template loaded: name={} count={}", name, len(template.values))

    @requires_permission("settings.update_template")
    def update_template(self, name: str, values: dict[str, Any], principal: Principal = _SYSTEM_PRINCIPAL) -> None:
        """Replace the stored values of a template (must cover the scope)."""
        with self._lock:
            existing = self._repository.get(name)
        if existing is None:
            raise TemplateNotFoundError(f"unknown template {name}")
        with self._lock:
            scope_keys = self._scope_keys(existing.category, existing.group)
            if set(values.keys()) != set(scope_keys):
                logger.warning("template update rejected (scope): name={}", name)
                raise TemplateValidationError("values must exactly cover the scope")
            for k in scope_keys:
                if not value_valid_for(self._definitions[k], values[k]):
                    logger.warning("template update rejected (invalid value): name={} key={}", name, k)
                    raise TemplateValidationError(f"value for {k} is invalid")
            updated = Template(
                name=name,
                category=existing.category,
                group=existing.group,
                values=dict(values),
            )
            self._repository.save(updated)
        logger.debug("template updated: name={}", name)

    @requires_permission("settings.delete_template")
    def delete_template(self, name: str, principal: Principal = _SYSTEM_PRINCIPAL) -> None:
        """Delete a template (TemplateNotFoundError if unknown)."""
        with self._lock:
            if self._repository.get(name) is None:
                raise TemplateNotFoundError(f"unknown template {name}")
            self._repository.delete(name)
        logger.debug("template deleted: name={}", name)

    @requires_permission("settings.get_template")
    def get_template(self, name: str, principal: Principal = _SYSTEM_PRINCIPAL) -> Template | None:
        """Return the template of ``name``, or None if it does not exist."""
        with self._lock:
            return self._repository.get(name)

    @requires_permission("settings.has_template")
    def has_template(self, name: str, principal: Principal = _SYSTEM_PRINCIPAL) -> bool:
        """Return True iff a template of ``name`` exists."""
        with self._lock:
            return self._repository.get(name) is not None

    @requires_permission("settings.list_templates")
    def list_templates(self, principal: Principal = _SYSTEM_PRINCIPAL) -> list[Template]:
        """Return all stored templates, name-ordered."""
        with self._lock:
            return self._repository.list()

    # -- internal --

    def _require_definition(self, key: str) -> SettingDefinition:
        d = self._definitions.get(key)
        if d is None:
            raise SettingsNotFoundError(f"unknown setting {key}")
        return d

    def _scope_keys(self, category: str, group: str | None) -> list[str]:
        return [key for key, d in self._definitions.items() if d.category == category and d.group == group]

    def _publish_setting_changed(self, key: str, value: Any, previous: Any) -> None:
        # Publishing is best-effort: the bus drops events when shut down.
        self._event_bus.publish(SettingChanged(key=key, value=value, previous=previous))

    def _persist_values(self) -> None:
        # All current values are persisted (REQ-009), including those equal
        # to their defaults (EDGE-009).
        with self._lock:
            values = dict(self._values)
        self._value_repository.save(values)


@logged(slow_threshold_ms=5)
def get_settings_registry(required: bool = True) -> SettingsRegistry | None:
    """Return the shared default registry (singleton).

    With ``required=True`` (default) the singleton is created on first use.
    With ``required=False`` the existing singleton is returned, or ``None`` if
    it has not been created yet (no side effect).
    """
    reg = _registry[0]
    if reg is None:
        if not required:
            return None
        reg = SettingsRegistry()
        _registry[0] = reg
    return reg


@logged(slow_threshold_ms=5)
def reset_settings_registry() -> None:
    """Reset the shared default registry (for tests)."""
    _registry[0] = None
