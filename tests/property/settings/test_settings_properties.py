"""Property tests for the settings feature (docs/specs/settings.md).

Hypothesis-based tests for the invariants INV-001 .. INV-010.
"""

from __future__ import annotations

from collections.abc import SearchStrategy

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from settings_test_helpers import EventCollector

from backend.settings import (
    SelectOption,
    SelectSpec,
    SettingDefinition,
    SettingKind,
    SettingRegistry,
    SettingStatus,
    SliderSpec,
    Template,
)
from backend.settings.repository import YamlTemplateRepository

_MAX_EXAMPLES = 40


def _text_value() -> SearchStrategy[str]:
    return st.text(min_size=0, max_size=20)


def _number_value() -> SearchStrategy[int]:
    return st.integers(min_value=-10**6, max_value=10**6)


def _email_value() -> SearchStrategy[str]:
    return st.from_regex(r"[a-z]{1,10}@[a-z]{1,10}\.[a-z]{2,3}", fullmatch=True)


@st.composite
def _setting_with_valid_value(draw):
    """A fully-valid (SettingDefinition, value) pair for a random kind."""
    kind = draw(st.sampled_from([
        SettingKind.TEXT, SettingKind.NUMBER, SettingKind.BOOLEAN,
        SettingKind.EMAIL, SettingKind.SLIDER, SettingKind.SELECT,
    ]))
    key = "app.k"
    if kind is SettingKind.TEXT:
        default = draw(_text_value())
        value = draw(_text_value())
        definition = SettingDefinition(key=key, kind=kind, default=default)
    elif kind is SettingKind.NUMBER:
        default = draw(_number_value())
        value = draw(_number_value())
        definition = SettingDefinition(key=key, kind=kind, default=default)
    elif kind is SettingKind.BOOLEAN:
        default = draw(st.booleans())
        value = draw(st.booleans())
        definition = SettingDefinition(key=key, kind=kind, default=default)
    elif kind is SettingKind.EMAIL:
        default = draw(_email_value())
        value = draw(_email_value())
        definition = SettingDefinition(key=key, kind=kind, default=default)
    elif kind is SettingKind.SLIDER:
        maxv = draw(st.integers(min_value=1, max_value=100))
        value = draw(st.integers(min_value=0, max_value=maxv))
        definition = SettingDefinition(
            key=key, kind=kind, default=0,
            slider=SliderSpec(min=0, max=maxv, step=1),
        )
    else:  # SELECT
        value = draw(st.sampled_from(["a", "b"]))
        definition = SettingDefinition(
            key=key, kind=kind, default="a",
            select=SelectSpec(options=[SelectOption(value="a"), SelectOption(value="b")]),
        )
    return definition, value


def _make_registry() -> SettingsRegistry:
    collector = EventCollector()
    return SettingsRegistry(event_bus=collector)


@settings(max_examples=_MAX_EXAMPLES)
@given(pair=_setting_with_valid_value())
def test_inv_001_set_get_roundtrip(pair) -> None:
    """INV-001: set_value(key, v) succeeds and get_value(key) == v."""
    definition, value = pair
    registry = _make_registry()
    registry.register(definition)
    assert registry.set_value(definition.key, value) == value
    assert registry.get_value(definition.key) == value


@settings(max_examples=_MAX_EXAMPLES)
@given(pair=_setting_with_valid_value())
def test_inv_002_get_value_always_valid(pair) -> None:
    """INV-002: get_value returns a value that is valid for its kind."""
    definition, value = pair
    registry = _make_registry()
    registry.register(definition)
    # The default (returned before any set) is valid for the kind.
    current = registry.get_value(definition.key)
    _assert_kind_shape(definition.kind, current)
    # After a validated set, the stored value is valid for the kind.
    registry.set_value(definition.key, value)
    _assert_kind_shape(definition.kind, registry.get_value(definition.key))


def _assert_kind_shape(kind: SettingKind, value: object) -> None:
    if kind is SettingKind.TEXT or kind is SettingKind.EMAIL:
        assert isinstance(value, str)
    elif kind is SettingKind.NUMBER or kind is SettingKind.SLIDER:
        assert isinstance(value, (int, float)) and not isinstance(value, bool)
    elif kind is SettingKind.BOOLEAN:
        assert isinstance(value, bool)
    elif kind is SettingKind.SELECT:
        assert isinstance(value, str)


@settings(max_examples=_MAX_EXAMPLES)
@given(pair=_setting_with_valid_value())
def test_inv_003_reset_to_default(pair) -> None:
    """INV-003: after reset(key), get_value(key) == default."""
    definition, value = pair
    registry = _make_registry()
    registry.register(definition)
    registry.set_value(definition.key, value)
    registry.reset(definition.key)
    assert registry.get_value(definition.key) == definition.default


@settings(max_examples=_MAX_EXAMPLES)
@given(n_options=st.integers(min_value=1, max_value=10))
def test_inv_004_select_options_valid(n_options: int) -> None:
    """INV-004: every option value of a SELECT setting is a valid value."""
    options = [SelectOption(value=f"opt{i}") for i in range(n_options)]
    definition = SettingDefinition(
        key="app.sel", kind=SettingKind.SELECT, default="opt0",
        select=SelectSpec(options=options),
    )
    registry = _make_registry()
    registry.register(definition)
    for opt in options:
        assert registry.set_value("app.sel", opt.value) == opt.value


@settings(max_examples=_MAX_EXAMPLES)
@given(maxv=st.integers(min_value=1, max_value=100))
def test_inv_005_slider_grid_valid(maxv: int) -> None:
    """INV-005: min, max, and every grid point are valid SLIDER values."""
    definition = SettingDefinition(
        key="app.sld", kind=SettingKind.SLIDER, default=0,
        slider=SliderSpec(min=0, max=maxv, step=1),
    )
    registry = _make_registry()
    registry.register(definition)
    for k in range(maxv + 1):  # min + k*step for k in [0, maxv]
        assert registry.set_value("app.sld", k) == k


@settings(max_examples=_MAX_EXAMPLES)
@given(pair=_setting_with_valid_value())
def test_inv_006_views_match_values(pair) -> None:
    """INV-006: views() contains a SettingView matching value and status."""
    definition, value = pair
    registry = _make_registry()
    registry.register(definition)
    registry.set_value(definition.key, value)
    views = registry.views()
    match = [v for v in views if v.key == definition.key]
    assert len(match) == 1
    view = match[0]
    assert view.value == registry.get_value(definition.key)
    expected_status = (
        SettingStatus.MODIFIED if view.value != definition.default else SettingStatus.DEFAULT
    )
    assert view.status == expected_status


@settings(max_examples=_MAX_EXAMPLES)
@given(n=st.integers(min_value=1, max_value=5))
def test_inv_007_load_scope_valid(n: int) -> None:
    """INV-007: after load_template, every in-scope setting is valid."""
    registry = _make_registry()
    for i in range(n):
        registry.register(SettingDefinition(
            key=f"app.s{i}", kind=SettingKind.TEXT, default=f"d{i}", category="app",
        ))
    values = {f"app.s{i}": f"v{i}" for i in range(n)}
    registry.create_template("t1", "app", None, values)
    registry.load_template("t1")
    for i in range(n):
        current = registry.get_value(f"app.s{i}")
        assert isinstance(current, str)


@settings(max_examples=20)
@given(values=st.lists(st.text(min_size=1, max_size=10), min_size=1, max_size=10))
def test_inv_008_exactly_one_event_per_change(values: list[str]) -> None:
    """INV-008: exactly one SettingChanged per setting changed (even no-op)."""
    collector = EventCollector()
    registry = SettingsRegistry(event_bus=collector)
    registry.register(SettingDefinition(key="app.name", kind=SettingKind.TEXT, default="orig"))
    previous = "orig"
    for i, v in enumerate(values):
        registry.set_value("app.name", v)
        assert len(collector.events) == i + 1, "expected exactly one new event"
        event = collector.events[-1]
        assert event.value == v
        assert event.previous == previous
        previous = v


@settings(max_examples=_MAX_EXAMPLES)
@given(
    name=st.from_regex(r"[a-z][a-z0-9]{0,9}", fullmatch=True),
    value=st.text(min_size=0, max_size=10),
)
def test_inv_009_yaml_roundtrip(name: str, value: str) -> None:
    """INV-009: repository.save(t) then get(t.name) returns an equal template."""
    import tempfile

    with tempfile.TemporaryDirectory() as d:
        repo = YamlTemplateRepository(d)
        template = Template(name=name, category="app", group=None, values={"app.a": value})
        repo.save(template)
        loaded = repo.get(name)
        assert loaded is not None
        assert loaded == template


@settings(max_examples=_MAX_EXAMPLES)
@given(pair=_setting_with_valid_value())
def test_inv_010_status_derivation(pair) -> None:
    """INV-010: get_status == MODIFIED iff get_value != default."""
    definition, value = pair
    registry = _make_registry()
    registry.register(definition)
    registry.set_value(definition.key, value)
    current = registry.get_value(definition.key)
    expected = SettingStatus.MODIFIED if current != definition.default else SettingStatus.DEFAULT
    assert registry.get_status(definition.key) == expected
