"""Contract tests for the settings feature (docs/specs/settings.md).

Covers NFR-001 .. NFR-004: performance budgets, API/repository contract,
resource contract, and observability.
"""

from __future__ import annotations

import statistics
import threading
import time
from collections.abc import Iterator
from pathlib import Path

import pytest
from settings_test_helpers import EventCollector

from backend.settings import (
    SettingDefinition,
    SettingKind,
    SettingsRegistry,
    TemplateRepository,
    YamlTemplateRepository,
)


def _text(key: str, default: str = "d", category: str | None = None) -> SettingDefinition:
    return SettingDefinition(key=key, kind=SettingKind.TEXT, default=default, category=category)


def _median_ms(fn, n: int = 200) -> float:
    samples: list[float] = []
    for _ in range(n):
        start = time.perf_counter()
        fn()
        samples.append((time.perf_counter() - start) * 1000.0)
    return statistics.median(samples)


def test_nfr_001_performance_budgets(tmp_path: Path) -> None:
    collector = EventCollector()
    registry = SettingsRegistry(event_bus=collector)
    for i in range(1000):
        registry.register(_text(f"app.s{i}"))
    key = "app.s500"
    registry.set_value(key, "x")

    # Single-setting operations < 1 ms (median) with 1000 registered settings.
    assert _median_ms(lambda: registry.get_value(key)) < 1.0
    assert _median_ms(lambda: registry.set_value(key, "x")) < 1.0
    assert _median_ms(lambda: registry.reset(key)) < 1.0
    assert _median_ms(lambda: registry.to_view(key)) < 1.0
    assert _median_ms(lambda: registry.get_status(key)) < 1.0
    register_counter = iter(range(1000, 1020))
    create_counter = iter(range(1000, 1010))

    def _register_once() -> None:
        registry.register(_text(f"app.extra{next(register_counter)}"))

    assert _median_ms(_register_once, n=20) < 1.0

    # load_template < 10 ms for a scope of 100 settings.
    scope_registry = SettingsRegistry(event_bus=collector)
    for i in range(100):
        scope_registry.register(_text(f"scope.s{i}", category="scope"))
    scope_registry.create_template("t1", "scope", None, None)
    assert _median_ms(lambda: scope_registry.load_template("t1"), n=50) < 10.0

    # create/update/delete (YAML file I/O) < 50 ms; list < 500 ms with 100 stored.
    yaml_registry = SettingsRegistry(event_bus=collector, template_repository=YamlTemplateRepository(tmp_path))
    for i in range(100):
        yaml_registry.register(_text(f"y.s{i}", category="y"))
    assert _median_ms(lambda: yaml_registry.create_template(f"ct{next(create_counter)}", "y", None, None), n=10) < 50.0
    assert (
        _median_ms(lambda: yaml_registry.update_template("ct1000", {f"y.s{i}": "v" for i in range(100)}), n=10) < 50.0
    )
    delete_counter = iter(range(2000, 2010))

    def _delete_once() -> None:
        name = f"dt{next(delete_counter)}"
        yaml_registry.create_template(name, "y", None, None)
        yaml_registry.delete_template(name)

    assert _median_ms(_delete_once, n=10) < 50.0
    assert _median_ms(lambda: yaml_registry.list_templates(), n=20) < 500.0


def test_nfr_002_api_and_repository_contract() -> None:
    import backend.settings as s

    public = [
        "SettingsRegistry",
        "SettingDefinition",
        "SettingKind",
        "SettingStatus",
        "SettingView",
        "SliderSpec",
        "SelectSpec",
        "SelectOption",
        "Template",
        "SettingChanged",
        "get_settings_registry",
        "reset_settings_registry",
        "TemplateRepository",
        "YamlTemplateRepository",
    ]
    for name in public:
        assert hasattr(s, name), f"missing public API: {name}"

    from backend.settings import exceptions as ex

    for name in [
        "SettingsError",
        "SettingsNotFoundError",
        "SettingsValidationError",
        "SettingsRegistrationError",
        "TemplateNotFoundError",
        "TemplateValidationError",
        "TemplateStorageError",
    ]:
        assert hasattr(ex, name), f"missing exception: {name}"

    for method in ("save", "get", "delete", "list"):
        assert hasattr(TemplateRepository, method), f"TemplateRepository missing {method}"


def test_nfr_003_resource_contract(tmp_path: Path) -> None:
    collector = EventCollector()
    registry = SettingsRegistry(event_bus=collector)
    before = threading.active_count()
    for i in range(50):
        registry.register(_text(f"app.s{i}", category="app"))
    registry.set_value("app.s0", "x")
    registry.create_template("t1", "app", None, None)
    registry.load_template("t1")
    after = threading.active_count()
    assert after == before, "the settings feature must not create threads of its own"

    # Templates persist as YAML files when a YAML repository is used.
    repo = YamlTemplateRepository(tmp_path)
    yaml_registry = SettingsRegistry(event_bus=collector, template_repository=repo)
    yaml_registry.register(_text("y.a", category="y"))
    yaml_registry.create_template("t1", "y", None, None)
    assert (tmp_path / "t1.yaml").exists()


def test_nfr_004_observability(log_records: list, tmp_path: Path) -> None:
    collector = EventCollector()
    registry = SettingsRegistry(event_bus=collector)
    registry.register(_text("app.name", default="orig", category="app"))
    registry.set_value("app.name", "new")
    registry.create_template("t1", "app", None, {"app.name": "new"})

    def _levels(key: str) -> list[str]:
        return [r["level"].name for r in log_records if key in str(r)]

    # Registration, value change, and template creation are logged at DEBUG.
    assert "DEBUG" in _levels("app.name"), "registration/value change not logged at DEBUG"
    assert "DEBUG" in _levels("t1"), "template creation not logged at DEBUG"

    # Storage failure is logged at ERROR.
    import yaml as _yaml

    (tmp_path / "bad.yaml").write_text(
        _yaml.safe_dump({"name": "bad", "category": "app", "group": None, "values": ["x"]})
    )
    repo = YamlTemplateRepository(tmp_path)
    with pytest.raises(Exception):
        repo.get("bad")
    assert any(r["level"].name == "ERROR" for r in log_records), "storage failure not logged at ERROR"
