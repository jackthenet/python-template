"""Public API of the settings feature (module: backend.settings)."""

from __future__ import annotations

from backend.settings.exceptions import (
    SettingsError,
    SettingsNotFoundError,
    SettingsRegistrationError,
    SettingsValidationError,
    TemplateNotFoundError,
    TemplateStorageError,
    TemplateValidationError,
)
from backend.settings.models import (
    SelectOption,
    SelectSpec,
    SettingChanged,
    SettingDefinition,
    SettingKind,
    SettingStatus,
    SettingView,
    SliderSpec,
    Template,
)
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

__all__ = [
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
    "YamlTemplateRepository",
    "get_settings_registry",
    "reset_settings_registry",
]
