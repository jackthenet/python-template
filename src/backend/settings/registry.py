"""The settings registry: registration, validated value access, resets,
hierarchy/views, and template CRUD.
"""

from __future__ import annotations

import threading
from typing import Any

from loguru import logger

from backend.eventbus import EventBus, get_event_bus
from backend.logging import logged, logged_class
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
from backend.settings.repository import MemoryTemplateRepository, TemplateRepository

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
    ) -> None:
        self._event_bus = event_bus if event_bus is not None else get_event_bus()
        self._repository = template_repository if template_repository is not None else MemoryTemplateRepository()
        self._definitions: dict[str, SettingDefinition] = {}
        self._values: dict[str, Any] = {}
        self._lock = threading.Lock()

    # -- Registration --

    def register(self, definition: SettingDefinition) -> None:
        """Register a setting. Duplicate keys are rejected."""
        with self._lock:
            if definition.key in self._definitions:
                logger.warning("duplicate registration: key={}", definition.key)
                raise SettingsRegistrationError(f"duplicate key {definition.key}")
            self._definitions[definition.key] = definition
            self._values[definition.key] = definition.default
        logger.debug("setting registered: key={} kind={}", definition.key, definition.kind)

    def register_feature(self, feature: str, definitions: list[SettingDefinition]) -> None:
        """Register a feature's settings; each key must start with ``f"{feature}."``."""
        prefix = f"{feature}."
        for d in definitions:
            if not d.key.startswith(prefix):
                raise SettingsRegistrationError(f"key {d.key} does not start with {prefix}")
        for d in definitions:
            self.register(d)
        logger.debug("feature settings registered: feature={} count={}", feature, len(definitions))

    # -- Lookup --

    def has(self, key: str) -> bool:
        """Return True iff ``key`` is registered."""
        with self._lock:
            return key in self._definitions

    def get_definition(self, key: str) -> SettingDefinition:
        """Return the definition of ``key`` (SettingsNotFoundError if unknown)."""
        with self._lock:
            return self._require_definition(key)

    def get_value(self, key: str) -> Any:
        """Return the current value of ``key`` (SettingsNotFoundError if unknown)."""
        with self._lock:
            self._require_definition(key)
            return self._values[key]

    def set_value(self, key: str, value: Any) -> Any:
        """Validate and store ``value`` for ``key``; publish SettingChanged."""
        with self._lock:
            d = self._require_definition(key)
            if not value_valid_for(d, value):
                logger.warning("value set rejected (invalid): key={}", key)
                raise SettingsValidationError(f"value is invalid for {key}")
            previous = self._values[key]
            self._values[key] = value
        logger.debug("value set: key={}", key)
        self._publish_setting_changed(key, value, previous)
        return value

    # -- Resets --

    def reset(self, key: str) -> None:
        """Restore the default of ``key``; publish SettingChanged."""
        with self._lock:
            d = self._require_definition(key)
            previous = self._values[key]
            self._values[key] = d.default
        logger.debug("value reset: key={}", key)
        self._publish_setting_changed(key, d.default, previous)

    def reset_all(self) -> None:
        """Restore all settings to their defaults; one event per setting."""
        with self._lock:
            items = list(self._definitions.items())
        for key, d in items:
            with self._lock:
                previous = self._values[key]
                self._values[key] = d.default
            logger.debug("value reset: key={}", key)
            self._publish_setting_changed(key, d.default, previous)

    # -- Status / views --

    def get_status(self, key: str) -> SettingStatus:
        """Return the derived status of ``key``."""
        with self._lock:
            d = self._require_definition(key)
            current = self._values[key]
        return SettingStatus.DEFAULT if current == d.default else SettingStatus.MODIFIED

    def to_view(self, key: str) -> SettingView:
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
                pattern=d.pattern,
                min_length=d.min_length,
                max_length=d.max_length,
                min_value=d.min_value,
                max_value=d.max_value,
            )
        return view

    def views(self) -> list[SettingView]:
        """Return the views of all registered settings."""
        with self._lock:
            keys = list(self._definitions)
        return [self.to_view(k) for k in keys]

    def grouped_views(self) -> dict[str, dict[str, list[SettingView]]]:
        """Return the category -> group -> views structure."""
        with self._lock:
            items = list(self._definitions.items())
        result: dict[str, dict[str, list[SettingView]]] = {}
        for key, d in items:
            view = self.to_view(key)
            result.setdefault(d.category or "", {}).setdefault(d.group or "", []).append(view)
        return result

    # -- Templates --

    def create_template(
        self,
        name: str,
        category: str,
        group: str | None,
        values: dict[str, Any] | None = None,
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

    def load_template(self, name: str) -> None:
        """Set each of the template's values (validated); others left as-is."""
        with self._lock:
            template = self._repository.get(name)
        if template is None:
            raise TemplateNotFoundError(f"unknown template {name}")
        count = 0
        for key, value in template.values.items():
            self.set_value(key, value)
            count += 1
        logger.debug("template loaded: name={} count={}", name, count)

    def update_template(self, name: str, values: dict[str, Any]) -> None:
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

    def delete_template(self, name: str) -> None:
        """Delete a template (TemplateNotFoundError if unknown)."""
        with self._lock:
            if self._repository.get(name) is None:
                raise TemplateNotFoundError(f"unknown template {name}")
            self._repository.delete(name)
        logger.debug("template deleted: name={}", name)

    def get_template(self, name: str) -> Template | None:
        """Return the template of ``name``, or None if it does not exist."""
        with self._lock:
            return self._repository.get(name)

    def has_template(self, name: str) -> bool:
        """Return True iff a template of ``name`` exists."""
        with self._lock:
            return self._repository.get(name) is not None

    def list_templates(self) -> list[Template]:
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


@logged(slow_threshold_ms=5)
def get_settings_registry() -> SettingsRegistry:
    """Return the shared default registry (singleton)."""
    reg = _registry[0]
    if reg is None:
        reg = SettingsRegistry()
        _registry[0] = reg
    return reg


@logged(slow_threshold_ms=5)
def reset_settings_registry() -> None:
    """Reset the shared default registry (for tests)."""
    _registry[0] = None
