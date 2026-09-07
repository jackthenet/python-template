"""Unit tests for the settings feature edge cases (docs/specs/settings.md).

Covers EDGE-001 .. EDGE-029.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
import yaml
from settings_test_helpers import EventCollector

from backend.eventbus import EventBus
from backend.settings import (
    SelectOption,
    SelectSpec,
    SettingDefinition,
    SettingKind,
    SettingsRegistry,
    SliderSpec,
)
from backend.settings.exceptions import (
    SettingsNotFoundError,
    SettingsRegistrationError,
    SettingsValidationError,
    TemplateStorageError,
    TemplateValidationError,
)
from backend.settings.repository import YamlTemplateRepository


@pytest.fixture
def registry() -> Iterator[SettingsRegistry]:
    bus = EventBus()
    r = SettingsRegistry(event_bus=bus)
    yield r
    bus.shutdown()


def _text(key: str, default: str = "x") -> SettingDefinition:
    return SettingDefinition(key=key, kind=SettingKind.TEXT, default=default)


def _number(
    key: str, default: int = 1, min_value: float | None = None, max_value: float | None = None
) -> SettingDefinition:
    return SettingDefinition(
        key=key,
        kind=SettingKind.NUMBER,
        default=default,
        min_value=min_value,
        max_value=max_value,
    )


def test_edge_001_unknown_key_lookups(registry: SettingsRegistry) -> None:
    for op in (
        lambda: registry.get_definition("nope"),
        lambda: registry.get_value("nope"),
        lambda: registry.set_value("nope", 1),
        lambda: registry.reset("nope"),
        lambda: registry.get_status("nope"),
        lambda: registry.to_view("nope"),
    ):
        with pytest.raises(SettingsNotFoundError):
            op()


def test_edge_002_duplicate_registration(registry: SettingsRegistry) -> None:
    registry.register(_text("app.name"))
    with pytest.raises(SettingsRegistrationError):
        registry.register(_text("app.name"))


def test_edge_003_wrong_type(registry: SettingsRegistry) -> None:
    registry.register(_number("app.count"))
    with pytest.raises(SettingsValidationError):
        registry.set_value("app.count", "not a number")


def test_edge_004_bool_for_numeric(registry: SettingsRegistry) -> None:
    registry.register(_number("app.count"))
    with pytest.raises(SettingsValidationError):
        registry.set_value("app.count", True)
    registry.register(
        SettingDefinition(
            key="app.sld",
            kind=SettingKind.SLIDER,
            default=0,
            slider=SliderSpec(min=0, max=10, step=1),
        )
    )
    with pytest.raises(SettingsValidationError):
        registry.set_value("app.sld", False)


def test_edge_005_number_out_of_bounds(registry: SettingsRegistry) -> None:
    registry.register(_number("app.count", default=5, min_value=0, max_value=10))
    with pytest.raises(SettingsValidationError):
        registry.set_value("app.count", 11)
    with pytest.raises(SettingsValidationError):
        registry.set_value("app.count", -1)


def test_edge_006_invalid_email(registry: SettingsRegistry) -> None:
    registry.register(SettingDefinition(key="app.email", kind=SettingKind.EMAIL, default="a@b.com"))
    with pytest.raises(SettingsValidationError):
        registry.set_value("app.email", "not-an-email")


def test_edge_007_slider_off_grid(registry: SettingsRegistry) -> None:
    registry.register(
        SettingDefinition(
            key="app.sld",
            kind=SettingKind.SLIDER,
            default=0,
            slider=SliderSpec(min=0, max=10, step=2),
        )
    )
    with pytest.raises(SettingsValidationError):
        registry.set_value("app.sld", 3)  # off the step grid


def test_edge_008_slider_out_of_range(registry: SettingsRegistry) -> None:
    registry.register(
        SettingDefinition(
            key="app.sld",
            kind=SettingKind.SLIDER,
            default=0,
            slider=SliderSpec(min=0, max=10, step=2),
        )
    )
    with pytest.raises(SettingsValidationError):
        registry.set_value("app.sld", 12)


def test_edge_009_select_not_an_option(registry: SettingsRegistry) -> None:
    registry.register(
        SettingDefinition(
            key="app.sel",
            kind=SettingKind.SELECT,
            default="a",
            select=SelectSpec(options=[SelectOption(value="a"), SelectOption(value="b")]),
        )
    )
    with pytest.raises(SettingsValidationError):
        registry.set_value("app.sel", "c")


def test_edge_010_text_pattern(registry: SettingsRegistry) -> None:
    registry.register(
        SettingDefinition(
            key="app.code",
            kind=SettingKind.TEXT,
            default="abc",
            pattern=r"^[a-z]+$",
        )
    )
    with pytest.raises(SettingsValidationError):
        registry.set_value("app.code", "ABC123")


def test_edge_011_text_length(registry: SettingsRegistry) -> None:
    registry.register(
        SettingDefinition(
            key="app.name",
            kind=SettingKind.TEXT,
            default="abc",
            min_length=2,
            max_length=4,
        )
    )
    with pytest.raises(SettingsValidationError):
        registry.set_value("app.name", "a")  # too short
    with pytest.raises(SettingsValidationError):
        registry.set_value("app.name", "abcde")  # too long


def test_edge_012_reset_unknown(registry: SettingsRegistry) -> None:
    with pytest.raises(SettingsNotFoundError):
        registry.reset("nope")


def test_edge_013_reset_all(registry: SettingsRegistry) -> None:
    registry.register(_text("app.a", default="a0"))
    registry.register(_number("app.b", default=0))
    registry.set_value("app.a", "x")
    registry.set_value("app.b", 9)
    registry.reset_all()
    assert registry.get_value("app.a") == "a0"
    assert registry.get_value("app.b") == 0


def test_edge_014_slider_min_gt_max() -> None:
    with pytest.raises(SettingsValidationError):
        SliderSpec(min=5, max=1, step=1)


def test_edge_015_slider_step_nonpositive() -> None:
    with pytest.raises(SettingsValidationError):
        SliderSpec(min=0, max=10, step=0)
    with pytest.raises(SettingsValidationError):
        SliderSpec(min=0, max=10, step=-1)


def test_edge_016_select_empty() -> None:
    with pytest.raises(SettingsValidationError):
        SelectSpec(options=[])


def test_edge_017_select_duplicate_options() -> None:
    with pytest.raises(SettingsValidationError):
        SelectSpec(options=[SelectOption(value="a"), SelectOption(value="a")])


def test_edge_018_kind_param_mismatch() -> None:
    # slider spec on a TEXT setting
    with pytest.raises(SettingsValidationError):
        SettingDefinition(
            key="app.t",
            kind=SettingKind.TEXT,
            default="x",
            slider=SliderSpec(min=0, max=1, step=1),
        )
    # pattern on a NUMBER setting
    with pytest.raises(SettingsValidationError):
        SettingDefinition(key="app.n", kind=SettingKind.NUMBER, default=1, pattern=r"^1$")


def test_edge_019_invalid_key_format() -> None:
    for bad in ("a..b", "1abc", "a.b.."):
        with pytest.raises(SettingsValidationError):
            SettingDefinition(key=bad, kind=SettingKind.TEXT, default="x")


def test_edge_020_feature_prefix(registry: SettingsRegistry) -> None:
    with pytest.raises(SettingsRegistrationError):
        registry.register_feature("logging", [_text("other.key")])


def test_edge_021_unchanged_value_event() -> None:
    collector = EventCollector()
    registry = SettingsRegistry(event_bus=collector)
    registry.register(_text("app.name", default="orig"))
    registry.set_value("app.name", "same")
    registry.set_value("app.name", "same")  # value equals the current value
    assert len(collector.events) == 2
    event = collector.events[-1]
    assert event.value == "same"
    assert event.previous == "same"


def test_edge_022_bus_shutdown() -> None:
    bus = EventBus()
    bus.shutdown()
    registry = SettingsRegistry(event_bus=bus)
    registry.register(_text("app.name", default="orig"))
    # set_value still succeeds even though the bus is shut down.
    assert registry.set_value("app.name", "new") == "new"
    assert registry.get_value("app.name") == "new"


def test_edge_023_list_templates_empty(registry: SettingsRegistry) -> None:
    assert registry.list_templates() == []


def test_edge_024_directory_created(tmp_path: Path) -> None:
    missing = tmp_path / "does_not_exist"
    repo = YamlTemplateRepository(missing)
    assert missing.exists()
    assert repo.list() == []


def test_edge_025_schema_invalid_file(tmp_path: Path) -> None:
    # Valid YAML but schema-invalid: values is a list, not a map.
    (tmp_path / "bad.yaml").write_text(
        yaml.safe_dump({"name": "bad", "category": "app", "group": None, "values": ["x"]})
    )
    repo = YamlTemplateRepository(tmp_path)
    with pytest.raises(TemplateStorageError):
        repo.get("bad")
    with pytest.raises(TemplateStorageError):
        repo.list()


def test_edge_026_empty_scope_template(registry: SettingsRegistry) -> None:
    # No settings registered in category "empty".
    t = registry.create_template("t1", "empty", None, None)
    assert t.values == {}


def test_edge_027_load_unregistered_settings(tmp_path: Path) -> None:
    shared_repo = YamlTemplateRepository(tmp_path)
    bus_a = EventBus()
    reg_a = SettingsRegistry(event_bus=bus_a, template_repository=shared_repo)
    reg_a.register(
        SettingDefinition(
            key="app.a",
            kind=SettingKind.TEXT,
            default="a0",
            category="app",
        )
    )
    reg_a.create_template("t1", "app", None, {"app.a": "x"})
    bus_a.shutdown()

    # A second registry shares the template store but has app.a unregistered.
    bus_b = EventBus()
    reg_b = SettingsRegistry(event_bus=bus_b, template_repository=shared_repo)
    with pytest.raises(SettingsNotFoundError):
        reg_b.load_template("t1")
    bus_b.shutdown()


def test_edge_028_invalid_template_name(registry: SettingsRegistry) -> None:
    for bad in ("bad name", "1name"):
        with pytest.raises(TemplateValidationError):
            registry.create_template(bad, "app", None, {})


def test_edge_029_slider_max_off_grid() -> None:
    with pytest.raises(SettingsValidationError):
        SliderSpec(min=0, max=11, step=2)
