"""Acceptance tests for the settings feature (docs/specs/settings.md).

These tests verify externally observable behavior only: per-kind value
validation, registry registration, value access with defaults, resets,
status derivation, views/hierarchy, template CRUD with scope-coverage and
leave-as-is load semantics, YAML template storage, and event-bus integration.
"""

from __future__ import annotations

import threading
import time
from collections.abc import Iterator
from pathlib import Path

import pytest
import yaml
from settings_test_helpers import wait_for

from backend.eventbus import EventBus
from backend.settings import (
    SelectOption,
    SelectSpec,
    SettingChanged,
    SettingDefinition,
    SettingKind,
    SettingsRegistry,
    SettingStatus,
    SettingView,
    SliderSpec,
    get_settings_registry,
    reset_settings_registry,
)
from backend.settings.exceptions import (
    SettingsNotFoundError,
    SettingsRegistrationError,
    SettingsValidationError,
    TemplateNotFoundError,
    TemplateStorageError,
    TemplateValidationError,
)
from backend.settings.repository import YamlTemplateRepository


def _text(key: str, default: str = "x") -> SettingDefinition:
    return SettingDefinition(key=key, kind=SettingKind.TEXT, default=default)


def _number(key: str, default: int = 1) -> SettingDefinition:
    return SettingDefinition(key=key, kind=SettingKind.NUMBER, default=default)


def _boolean(key: str, default: bool = True) -> SettingDefinition:
    return SettingDefinition(key=key, kind=SettingKind.BOOLEAN, default=default)


def _email(key: str, default: str = "a@b.com") -> SettingDefinition:
    return SettingDefinition(key=key, kind=SettingKind.EMAIL, default=default)


def _slider(key: str, default: float = 0) -> SettingDefinition:
    return SettingDefinition(
        key=key,
        kind=SettingKind.SLIDER,
        default=default,
        slider=SliderSpec(min=0, max=10, step=2),
    )


def _select(key: str, default: str = "a") -> SettingDefinition:
    return SettingDefinition(
        key=key,
        kind=SettingKind.SELECT,
        default=default,
        select=SelectSpec(options=[SelectOption(value="a"), SelectOption(value="b")]),
    )


@pytest.fixture
def registry() -> Iterator[SettingsRegistry]:
    """A fresh registry wired to a fresh bus, shut down afterwards."""
    bus = EventBus()
    r = SettingsRegistry(event_bus=bus)
    yield r
    bus.shutdown()


@pytest.fixture
def registry_with_bus() -> Iterator[tuple[SettingsRegistry, EventBus]]:
    """A fresh registry plus its bus (for event subscription)."""
    bus = EventBus()
    r = SettingsRegistry(event_bus=bus)
    yield r, bus
    bus.shutdown()


# --- Per-kind round trips (AC-001 .. AC-006) ---


def test_ac_001_text_roundtrip(registry: SettingsRegistry) -> None:
    registry.register(_text("app.name"))
    assert registry.set_value("app.name", "hello") == "hello"
    assert registry.get_value("app.name") == "hello"


def test_ac_002_number_roundtrip(registry: SettingsRegistry) -> None:
    registry.register(_number("app.count"))
    assert registry.set_value("app.count", 42) == 42
    assert registry.get_value("app.count") == 42


def test_ac_003_boolean_roundtrip(registry: SettingsRegistry) -> None:
    registry.register(_boolean("app.flag"))
    assert registry.set_value("app.flag", True) is True
    assert registry.get_value("app.flag") is True


def test_ac_004_email_roundtrip(registry: SettingsRegistry) -> None:
    registry.register(_email("app.contact"))
    assert registry.set_value("app.contact", "user@example.com") == "user@example.com"
    assert registry.get_value("app.contact") == "user@example.com"


def test_ac_005_slider_roundtrip(registry: SettingsRegistry) -> None:
    registry.register(_slider("app.volume"))
    assert registry.set_value("app.volume", 4) == 4
    assert registry.get_value("app.volume") == 4


def test_ac_006_select_roundtrip(registry: SettingsRegistry) -> None:
    registry.register(_select("app.mode"))
    assert registry.set_value("app.mode", "b") == "b"
    assert registry.get_value("app.mode") == "b"


# --- Defaults and storage (AC-007, AC-008) ---


def test_ac_007_default_before_set(registry: SettingsRegistry) -> None:
    registry.register(_text("app.name", default="sensible"))
    assert registry.get_value("app.name") == "sensible"


def test_ac_008_set_stores_value(registry: SettingsRegistry) -> None:
    registry.register(_text("app.name"))
    registry.set_value("app.name", "stored")
    assert registry.get_value("app.name") == "stored"


# --- Construction-time validation (AC-009, AC-010) ---


def test_ac_009_invalid_default() -> None:
    with pytest.raises(SettingsValidationError):
        SettingDefinition(key="app.bad", kind=SettingKind.NUMBER, default="abc")


def test_ac_010_missing_kind_params() -> None:
    # SLIDER without a slider spec.
    with pytest.raises(SettingsValidationError):
        SettingDefinition(key="app.s1", kind=SettingKind.SLIDER, default=0)
    # SELECT without a select spec.
    with pytest.raises(SettingsValidationError):
        SettingDefinition(key="app.s2", kind=SettingKind.SELECT, default="a")
    # A slider spec on a TEXT setting.
    with pytest.raises(SettingsValidationError):
        SettingDefinition(
            key="app.s3",
            kind=SettingKind.TEXT,
            default="x",
            slider=SliderSpec(min=0, max=1, step=1),
        )


# --- Registration (AC-011, AC-012) ---


def test_ac_011_duplicate_registration(registry: SettingsRegistry) -> None:
    registry.register(_text("app.name"))
    with pytest.raises(SettingsRegistrationError):
        registry.register(_text("app.name"))


def test_ac_012_register_feature(registry: SettingsRegistry) -> None:
    registry.register_feature("logging", [_text("logging.log_level", default="INFO")])
    assert registry.has("logging.log_level")
    assert registry.get_value("logging.log_level") == "INFO"


# --- Resets (AC-013) ---


def test_ac_013_reset_to_default(registry: SettingsRegistry) -> None:
    registry.register(_text("app.name", default="orig"))
    registry.set_value("app.name", "changed")
    registry.reset("app.name")
    assert registry.get_value("app.name") == "orig"


# --- Unknown keys (AC-014) ---


def test_ac_014_unknown_key(registry: SettingsRegistry) -> None:
    with pytest.raises(SettingsNotFoundError):
        registry.get_value("nope")


# --- Hierarchy and views (AC-015, AC-016) ---


def test_ac_015_grouped_views(registry: SettingsRegistry) -> None:
    registry.register(
        SettingDefinition(
            key="logging.file_level",
            kind=SettingKind.TEXT,
            default="INFO",
            category="logging",
            group="file",
        )
    )
    registry.register(
        SettingDefinition(
            key="logging.console_level",
            kind=SettingKind.TEXT,
            default="DEBUG",
            category="logging",
            group="console",
        )
    )
    grouped = registry.grouped_views()
    assert "logging" in grouped
    assert "file" in grouped["logging"]
    assert "console" in grouped["logging"]
    assert any(v.key == "logging.file_level" for v in grouped["logging"]["file"])
    assert any(v.key == "logging.console_level" for v in grouped["logging"]["console"])


def test_ac_016_to_view(registry: SettingsRegistry) -> None:
    registry.register(
        SettingDefinition(
            key="app.name",
            kind=SettingKind.TEXT,
            default="orig",
            title="Name",
        )
    )
    view = registry.to_view("app.name")
    assert isinstance(view, SettingView)
    assert view.key == "app.name"
    assert view.value == "orig"
    assert view.status == SettingStatus.DEFAULT
    assert view.title == "Name"


# --- Status transitions (AC-017) ---


def test_ac_017_status_transitions(registry: SettingsRegistry) -> None:
    registry.register(_text("app.name", default="orig"))
    assert registry.get_status("app.name") == SettingStatus.DEFAULT
    registry.set_value("app.name", "changed")
    assert registry.get_status("app.name") == SettingStatus.MODIFIED
    registry.reset("app.name")
    assert registry.get_status("app.name") == SettingStatus.DEFAULT
    registry.set_value("app.name", "orig")
    assert registry.get_status("app.name") == SettingStatus.DEFAULT


# --- Singleton (AC-018) ---


def test_ac_018_singleton() -> None:
    try:
        a = get_settings_registry()
        b = get_settings_registry()
        assert a is b
    finally:
        reset_settings_registry()


# --- Template CRUD (AC-019 .. AC-029) ---


def _register_app_scope(registry: SettingsRegistry) -> None:
    registry.register(
        SettingDefinition(
            key="app.a",
            kind=SettingKind.TEXT,
            default="a0",
            category="app",
        )
    )
    registry.register(
        SettingDefinition(
            key="app.b",
            kind=SettingKind.NUMBER,
            default=0,
            category="app",
        )
    )


def test_ac_019_create_template_explicit(registry: SettingsRegistry) -> None:
    _register_app_scope(registry)
    registry.create_template("t1", "app", None, {"app.a": "x", "app.b": 5})
    t = registry.get_template("t1")
    assert t.values == {"app.a": "x", "app.b": 5}


def test_ac_020_create_template_capture(registry: SettingsRegistry) -> None:
    _register_app_scope(registry)
    registry.set_value("app.a", "cur")
    registry.set_value("app.b", 9)
    registry.create_template("t1", "app", None, None)
    t = registry.get_template("t1")
    assert t.values == {"app.a": "cur", "app.b": 9}


def test_ac_021_create_template_incomplete(registry: SettingsRegistry) -> None:
    _register_app_scope(registry)
    # Missing B.
    with pytest.raises(TemplateValidationError):
        registry.create_template("t1", "app", None, {"app.a": "x"})
    # Out-of-scope key.
    registry.register(
        SettingDefinition(
            key="other.c",
            kind=SettingKind.TEXT,
            default="z",
            category="other",
        )
    )
    with pytest.raises(TemplateValidationError):
        registry.create_template("t2", "app", None, {"app.a": "x", "app.b": 1, "other.c": "z"})


def test_ac_022_create_template_duplicate(registry: SettingsRegistry) -> None:
    _register_app_scope(registry)
    registry.create_template("t1", "app", None, {"app.a": "x", "app.b": 1})
    with pytest.raises(TemplateValidationError):
        registry.create_template("t1", "app", None, {"app.a": "y", "app.b": 2})


def test_ac_023_load_template_sets_values(registry: SettingsRegistry) -> None:
    _register_app_scope(registry)
    registry.create_template("t1", "app", None, {"app.a": "loaded", "app.b": 7})
    registry.load_template("t1")
    assert registry.get_value("app.a") == "loaded"
    assert registry.get_value("app.b") == 7


def test_ac_024_load_template_leave_as_is(registry: SettingsRegistry) -> None:
    # Create the template for scope {app.a} before app.b is registered.
    registry.register(
        SettingDefinition(
            key="app.a",
            kind=SettingKind.TEXT,
            default="a0",
            category="app",
        )
    )
    registry.create_template("t1", "app", None, {"app.a": "snap"})
    # Now register app.b (scope grows) and set it to a non-template value.
    registry.register(
        SettingDefinition(
            key="app.b",
            kind=SettingKind.NUMBER,
            default=0,
            category="app",
        )
    )
    registry.set_value("app.b", 42)
    registry.load_template("t1")
    assert registry.get_value("app.a") == "snap"
    assert registry.get_value("app.b") == 42  # left as-is


def test_ac_025_load_template_unknown(registry: SettingsRegistry) -> None:
    with pytest.raises(TemplateNotFoundError):
        registry.load_template("nope")


def test_ac_026_update_template(registry: SettingsRegistry) -> None:
    _register_app_scope(registry)
    registry.create_template("t1", "app", None, {"app.a": "x", "app.b": 1})
    registry.update_template("t1", {"app.a": "y", "app.b": 2})
    assert registry.get_template("t1").values == {"app.a": "y", "app.b": 2}


def test_ac_027_update_template_invalid(registry: SettingsRegistry) -> None:
    _register_app_scope(registry)
    registry.create_template("t1", "app", None, {"app.a": "x", "app.b": 1})
    # Not exactly covering the scope.
    with pytest.raises(TemplateValidationError):
        registry.update_template("t1", {"app.a": "x"})
    # Unknown template name.
    with pytest.raises(TemplateNotFoundError):
        registry.update_template("nope", {"app.a": "x", "app.b": 1})


def test_ac_028_delete_template(registry: SettingsRegistry) -> None:
    _register_app_scope(registry)
    registry.create_template("t1", "app", None, {"app.a": "x", "app.b": 1})
    registry.delete_template("t1")
    assert not registry.has_template("t1")
    with pytest.raises(TemplateNotFoundError):
        registry.delete_template("nope")


def test_ac_029_template_access(registry: SettingsRegistry) -> None:
    _register_app_scope(registry)
    registry.create_template("b", "app", None, {"app.a": "x", "app.b": 1})
    registry.create_template("a", "app", None, {"app.a": "y", "app.b": 2})
    assert registry.get_template("a").values == {"app.a": "y", "app.b": 2}
    assert registry.has_template("a")
    assert [t.name for t in registry.list_templates()] == ["a", "b"]


# --- YAML storage (AC-030 .. AC-034) ---


def test_ac_030_yaml_file_written(tmp_path: Path) -> None:
    repo = YamlTemplateRepository(tmp_path)
    bus = EventBus()
    registry = SettingsRegistry(event_bus=bus, template_repository=repo)
    _register_app_scope(registry)
    registry.create_template("t1", "app", None, {"app.a": "x", "app.b": 1})
    f = tmp_path / "t1.yaml"
    assert f.exists()
    data = yaml.safe_load(f.read_text())
    assert data["name"] == "t1"
    assert data["category"] == "app"
    assert data["values"] == {"app.a": "x", "app.b": 1}
    bus.shutdown()


def test_ac_031_persistence_across_instances(tmp_path: Path) -> None:
    bus1 = EventBus()
    r1 = SettingsRegistry(event_bus=bus1, template_repository=YamlTemplateRepository(tmp_path))
    _register_app_scope(r1)
    r1.create_template("t1", "app", None, {"app.a": "x", "app.b": 1})
    bus1.shutdown()

    bus2 = EventBus()
    r2 = SettingsRegistry(event_bus=bus2, template_repository=YamlTemplateRepository(tmp_path))
    t = r2.get_template("t1")
    assert t.values == {"app.a": "x", "app.b": 1}
    bus2.shutdown()


def test_ac_032_corrupted_file(tmp_path: Path) -> None:
    (tmp_path / "bad.yaml").write_text("not: [valid: yaml")
    repo = YamlTemplateRepository(tmp_path)
    with pytest.raises(TemplateStorageError):
        repo.get("bad")


def test_ac_033_missing_file(tmp_path: Path) -> None:
    repo = YamlTemplateRepository(tmp_path)
    assert repo.get("missing") is None
    repo.delete("missing")  # idempotent, no error


def test_ac_034_storage_agnostic() -> None:
    # An in-memory repository (default) must behave like the YAML one.
    bus = EventBus()
    registry = SettingsRegistry(event_bus=bus)  # default in-memory repo
    _register_app_scope(registry)
    registry.create_template("t1", "app", None, {"app.a": "x", "app.b": 1})
    registry.load_template("t1")
    registry.update_template("t1", {"app.a": "y", "app.b": 2})
    assert registry.get_template("t1").values == {"app.a": "y", "app.b": 2}
    registry.delete_template("t1")
    assert not registry.has_template("t1")
    bus.shutdown()


# --- Event-bus integration (AC-035 .. AC-037, AC-039) ---


def test_ac_035_set_value_publishes_event(registry_with_bus) -> None:
    registry, bus = registry_with_bus
    registry.register(_text("app.name", default="orig"))
    received: list[SettingChanged] = []
    bus.subscribe(SettingChanged, lambda e: received.append(e))
    registry.set_value("app.name", "new")
    assert wait_for(lambda: len(received) == 1), "SettingChanged not published"
    assert received[0].key == "app.name"
    assert received[0].value == "new"
    assert received[0].previous == "orig"


def test_ac_036_load_template_publishes_events(registry_with_bus) -> None:
    registry, bus = registry_with_bus
    _register_app_scope(registry)
    registry.create_template("t1", "app", None, {"app.a": "x", "app.b": 1})
    received: list[SettingChanged] = []
    bus.subscribe(SettingChanged, lambda e: received.append(e))
    registry.load_template("t1")
    assert wait_for(lambda: len(received) == 2), "expected one event per setting set"
    keys = {e.key for e in received}
    assert keys == {"app.a", "app.b"}


def test_ac_037_custom_bus() -> None:
    custom = EventBus()
    shared = EventBus()
    registry = SettingsRegistry(event_bus=custom)
    registry.register(_text("app.name", default="orig"))
    on_custom: list[SettingChanged] = []
    on_shared: list[SettingChanged] = []
    custom.subscribe(SettingChanged, lambda e: on_custom.append(e))
    shared.subscribe(SettingChanged, lambda e: on_shared.append(e))
    registry.set_value("app.name", "new")
    assert wait_for(lambda: len(on_custom) == 1), "event not on custom bus"
    time.sleep(0.2)  # give the shared bus a chance to (wrongly) deliver
    assert len(on_shared) == 0, "event leaked to the shared bus"
    custom.shutdown()
    shared.shutdown()


def test_ac_039_reset_publishes_events(registry_with_bus) -> None:
    registry, bus = registry_with_bus
    _register_app_scope(registry)  # app.a (default "a0"), app.b (default 0)
    # Subscribe BEFORE the setup writes so their events are delivered to the
    # handler; we then wait for and clear them, so no setup event is in flight
    # when we assert on the reset events (the bus is asynchronous).
    received: list[SettingChanged] = []
    bus.subscribe(SettingChanged, lambda e: received.append(e))
    registry.set_value("app.a", "x")
    registry.set_value("app.b", 5)
    assert wait_for(lambda: len(received) == 2)  # setup events delivered
    received.clear()
    # reset(key) publishes value=default, previous=old
    registry.reset("app.a")
    assert wait_for(lambda: len(received) == 1)
    assert received[0].key == "app.a"
    assert received[0].value == "a0"  # the default
    assert received[0].previous == "x"
    # reset_all() restores all settings to their defaults and publishes one
    # event per setting it sets (value == its default), including app.a which
    # is already at its default.
    received.clear()
    registry.reset_all()
    assert wait_for(lambda: len(received) == 2)
    by_key = {e.key: e for e in received}
    assert set(by_key) == {"app.a", "app.b"}
    assert by_key["app.a"].value == "a0"  # its default
    assert by_key["app.b"].value == 0  # its default


# --- Thread safety (AC-038) ---


def test_ac_038_thread_safe_registration() -> None:
    bus = EventBus()
    registry = SettingsRegistry(event_bus=bus)
    errors: list[BaseException] = []

    def worker(i: int) -> None:
        try:
            registry.register(_text(f"app.k{i}"))
        except BaseException as e:  # noqa: BLE001
            errors.append(e)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(32)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert not errors
    for i in range(32):
        assert registry.has(f"app.k{i}")
    bus.shutdown()
