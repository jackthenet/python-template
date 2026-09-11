"""Frozen Pydantic models for the settings feature.

All public models are frozen. Cross-field and kind-specific rules are enforced
at construction time and raise ``SettingsValidationError`` (never
``pydantic.ValidationError``) so the public error contract is the
``SettingsError`` hierarchy.
"""

from __future__ import annotations

import re
from enum import StrEnum
from typing import Any

import email_validator
from pydantic import BaseModel, ConfigDict, model_validator

from backend.settings.exceptions import SettingsValidationError

_KEY_RE = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*(\.[a-zA-Z_][a-zA-Z0-9_]*)*$")
_TEMPLATE_NAME_RE = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")
# Tolerance used only to absorb floating-point representation error when
# checking step-grid membership; it does not widen the valid-value domain.
_STEP_EPSILON = 1e-9


class SettingKind(StrEnum):
    """The seven supported setting kinds."""

    TEXT = "text"
    NUMBER = "number"
    BOOLEAN = "boolean"
    EMAIL = "email"
    SLIDER = "slider"
    SELECT = "select"
    LIST = "list"


class SettingStatus(StrEnum):
    """Default status of a setting, derived from its value."""

    DEFAULT = "default"
    MODIFIED = "modified"


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _email_valid(value: str) -> bool:
    try:
        # check_deliverability=False: format-only validation (no DNS lookups),
        # keeping validation fast and deterministic.
        email_validator.validate_email(value, check_deliverability=False)
    except email_validator.EmailNotValidError:
        return False
    return True


def _slider_on_grid(value: float, min_: float, max_: float, step: float) -> bool:
    if value < min_ - _STEP_EPSILON or value > max_ + _STEP_EPSILON:
        return False
    k = round((value - min_) / step)
    if k < 0:
        return False
    return abs(value - (min_ + k * step)) <= _STEP_EPSILON


def is_valid_value(  # noqa: PLR0911, PLR0912
    kind: SettingKind,
    value: Any,
    *,
    slider_min: float | None = None,
    slider_max: float | None = None,
    slider_step: float | None = None,
    select_options: tuple[str, ...] | None = None,
    pattern: str | None = None,
    min_length: int | None = None,
    max_length: int | None = None,
    min_value: float | None = None,
    max_value: float | None = None,
    list_spec: ListSpec | None = None,
) -> bool:
    """Return True iff ``value`` is valid for ``kind`` with the given params."""
    if kind is SettingKind.TEXT:
        if not isinstance(value, str):
            return False
        if pattern is not None and re.fullmatch(pattern, value) is None:
            return False
        if min_length is not None and len(value) < min_length:
            return False
        return not (max_length is not None and len(value) > max_length)
    if kind is SettingKind.NUMBER:
        if not _is_number(value):
            return False
        if min_value is not None and value < min_value:
            return False
        return not (max_value is not None and value > max_value)
    if kind is SettingKind.BOOLEAN:
        return isinstance(value, bool)
    if kind is SettingKind.EMAIL:
        return isinstance(value, str) and _email_valid(value)
    if kind is SettingKind.SLIDER:
        if not _is_number(value):
            return False
        if slider_min is None or slider_max is None or slider_step is None:
            return False
        return _slider_on_grid(value, slider_min, slider_max, slider_step)
    if kind is SettingKind.SELECT:
        if select_options is None:
            return False
        return isinstance(value, str) and value in select_options
    if kind is SettingKind.LIST:
        if not isinstance(value, list):
            return False
        if not all(isinstance(item, str) for item in value):
            return False
        spec = list_spec if list_spec is not None else ListSpec()
        if spec.item_pattern is not None and any(
            re.fullmatch(spec.item_pattern, item) is None for item in value
        ):
            return False
        if spec.min_items is not None and len(value) < spec.min_items:
            return False
        if spec.max_items is not None and len(value) > spec.max_items:
            return False
        return spec.allow_duplicates or len(set(value)) == len(value)
    return False


class SelectOption(BaseModel):
    """One alternative of a SELECT setting."""

    model_config = ConfigDict(frozen=True)

    value: str
    label: str | None = None

    @model_validator(mode="after")
    def _validate(self) -> SelectOption:
        if self.value == "":
            raise SettingsValidationError("option value must be non-empty")
        return self


class SelectSpec(BaseModel):
    """Parameters for a SELECT setting."""

    model_config = ConfigDict(frozen=True)

    options: list[SelectOption]

    @model_validator(mode="after")
    def _validate(self) -> SelectSpec:
        if not self.options:
            raise SettingsValidationError("select options must be non-empty")
        values = [o.value for o in self.options]
        if len(set(values)) != len(values):
            raise SettingsValidationError("select option values must be unique")
        return self


class ListSpec(BaseModel):
    """Kind-specific parameters for the LIST setting kind (REQ-006)."""

    model_config = ConfigDict(frozen=True)

    item_pattern: str | None = None
    min_items: int | None = None
    max_items: int | None = None
    allow_duplicates: bool = True

    @model_validator(mode="after")
    def _validate(self) -> ListSpec:
        if self.min_items is not None and self.min_items < 0:
            raise SettingsValidationError("list min_items must be >= 0")
        if self.max_items is not None and self.max_items < 0:
            raise SettingsValidationError("list max_items must be >= 0")
        if (
            self.min_items is not None
            and self.max_items is not None
            and self.min_items > self.max_items
        ):
            raise SettingsValidationError("list min_items must be <= max_items")
        if self.item_pattern is not None:
            try:
                re.compile(self.item_pattern)
            except re.error as e:
                raise SettingsValidationError(
                    f"list item_pattern is not a valid regex: {e}"
                ) from e
        return self


class SliderSpec(BaseModel):
    """Parameters for a SLIDER setting."""

    model_config = ConfigDict(frozen=True)

    min: float
    max: float
    step: float = 1.0

    @model_validator(mode="after")
    def _validate(self) -> SliderSpec:
        if self.step <= 0:
            raise SettingsValidationError("slider step must be > 0")
        if self.min > self.max:
            raise SettingsValidationError("slider min must be <= max")
        span = (self.max - self.min) / self.step
        if abs(span - round(span)) > _STEP_EPSILON:
            raise SettingsValidationError("slider max must lie on the step grid")
        return self


class SettingDefinition(BaseModel):
    """Complete metadata for one setting."""

    model_config = ConfigDict(frozen=True)

    key: str
    kind: SettingKind
    default: Any
    title: str | None = None
    description: str | None = None
    category: str | None = None
    group: str | None = None
    slider: SliderSpec | None = None
    select: SelectSpec | None = None
    list_spec: ListSpec | None = None
    pattern: str | None = None
    min_length: int | None = None
    max_length: int | None = None
    min_value: float | None = None
    max_value: float | None = None

    @model_validator(mode="after")
    def _validate(self) -> SettingDefinition:  # noqa: PLR0912
        if not _KEY_RE.match(self.key):
            raise SettingsValidationError("setting key has an invalid format")
        kind = self.kind
        # Kind-specific parameter presence/mismatch.
        if kind is SettingKind.SLIDER:
            if self.slider is None:
                raise SettingsValidationError("SLIDER requires a slider spec")
            if self.select is not None:
                raise SettingsValidationError("SLIDER forbids a select spec")
        elif kind is SettingKind.SELECT:
            if self.select is None:
                raise SettingsValidationError("SELECT requires a select spec")
            if self.slider is not None:
                raise SettingsValidationError("SELECT forbids a slider spec")
        elif kind is SettingKind.LIST:
            # LIST always accepts: a ListSpec is optional (defaults to ListSpec()).
            pass
        else:
            if self.slider is not None:
                raise SettingsValidationError(f"{kind} forbids a slider spec")
            if self.select is not None:
                raise SettingsValidationError(f"{kind} forbids a select spec")
            if self.list_spec is not None:
                raise SettingsValidationError(f"{kind} forbids a list spec")
        # TEXT-only constraints are rejected on other kinds.
        if kind is not SettingKind.TEXT and (
            self.pattern is not None or self.min_length is not None or self.max_length is not None
        ):
            raise SettingsValidationError(f"{kind} forbids TEXT-only constraints")
        # NUMBER-only constraints are rejected on other kinds.
        if kind is not SettingKind.NUMBER and (self.min_value is not None or self.max_value is not None):
            raise SettingsValidationError(f"{kind} forbids NUMBER-only constraints")
        # Default validity.
        if not _definition_default_valid(self):
            raise SettingsValidationError("default is invalid for its kind")
        return self


def value_valid_for(d: SettingDefinition, value: Any) -> bool:
    """Return True iff ``value`` is valid for the setting ``d``."""
    return is_valid_value(
        d.kind,
        value,
        slider_min=d.slider.min if d.slider else None,
        slider_max=d.slider.max if d.slider else None,
        slider_step=d.slider.step if d.slider else None,
        select_options=tuple(o.value for o in d.select.options) if d.select else None,
        pattern=d.pattern,
        min_length=d.min_length,
        max_length=d.max_length,
        min_value=d.min_value,
        max_value=d.max_value,
        list_spec=d.list_spec,
    )


def _definition_default_valid(d: SettingDefinition) -> bool:
    return value_valid_for(d, d.default)


class SettingView(BaseModel):
    """Renderable representation of a setting."""

    model_config = ConfigDict(frozen=True)

    key: str
    kind: SettingKind
    title: str | None
    description: str | None
    category: str | None
    group: str | None
    default: Any
    value: Any
    status: SettingStatus
    slider: SliderSpec | None
    select: SelectSpec | None
    list_spec: ListSpec | None
    pattern: str | None
    min_length: int | None
    max_length: int | None
    min_value: float | None
    max_value: float | None


class Template(BaseModel):
    """A named value profile scoped to a category (and optionally a group)."""

    model_config = ConfigDict(frozen=True)

    name: str
    category: str
    group: str | None = None
    values: dict[str, Any]


class SettingChanged(BaseModel):
    """Published to the event bus whenever a setting value changes."""

    model_config = ConfigDict(frozen=True)

    key: str
    value: Any
    previous: Any


def is_template_name_valid(name: str) -> bool:
    """Return True iff ``name`` matches the template name format."""
    return bool(_TEMPLATE_NAME_RE.match(name))
