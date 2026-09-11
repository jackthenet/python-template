"""Exception hierarchy for the settings feature."""

from __future__ import annotations


class SettingsError(Exception):
    """Base class for all settings feature errors."""


class SettingsNotFoundError(SettingsError):
    """Raised when a lookup references an unknown setting key."""


class SettingsValidationError(SettingsError):
    """Raised when a value or definition is invalid for its kind."""


class SettingsRegistrationError(SettingsError):
    """Raised when registration violates the registry's invariants."""


class TemplateNotFoundError(SettingsError):
    """Raised when a template operation references an unknown template."""


class TemplateValidationError(SettingsError):
    """Raised when a template violates scope-coverage or name rules."""


class TemplateStorageError(SettingsError):
    """Raised when template storage is corrupted or schema-invalid."""


class ValueStorageError(SettingsError, ValueError):
    """Raised when value storage is corrupted or schema-invalid."""
