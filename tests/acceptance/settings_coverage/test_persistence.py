"""AC-013 / AC-015: value persistence and precedence."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from logging_coverage_test_helpers import level_name
from settings_test_helpers import make_registry

from backend.settings import SettingDefinition, SettingKind, SettingsRegistry, YamlValueRepository


@pytest.fixture(autouse=True)
def _reset_registry() -> Iterator[None]:
    # Reset the singleton for the test; the previous singleton is restored on
    # teardown (no state leak).
    from settings_test_helpers import isolated_registry

    with isolated_registry(install=False):
        yield


def test_set_value_persists() -> None:
    """AC-013: set_value persists all current values to the value repository."""
    reg, _bus = make_registry()
    reg.register(SettingDefinition(key="a", kind=SettingKind.TEXT, default="x"))
    reg.set_value("a", "y")

    repo = reg.value_repository
    assert repo is not None
    loaded = repo.load()
    assert loaded is not None
    assert loaded["a"] == "y"


def test_persisted_precedence(tmp_path: Path) -> None:
    """AC-015: persisted values take precedence over definition defaults."""
    directory = tmp_path / "values"
    repo = YamlValueRepository(str(directory))
    repo.save({"a": "persisted"})

    from backend.settings import SettingsRegistry

    reg = SettingsRegistry(value_repository=repo)
    reg.register(SettingDefinition(key="a", kind=SettingKind.TEXT, default="default"))
    assert reg.get_value("a") == "persisted"


def test_ac_028_persisted_override_warns(tmp_path: Path, log_records: list[Any]) -> None:
    """AC-028 / REQ-023 (LQ-02): startup warns about every persisted value that overrode its default.

    The override itself is required by REQ-022 / AC-027 and is already witnessed by
    ``test_persisted_precedence``; what the feature lacks is the one-off ``WARNING`` that makes the
    override visible at startup (defect D-5). The record is matched by level and by the key it names,
    not by exact wording -- the AC-028 sentence is written in the same change as the fix.
    """
    overridden = str(tmp_path / "overridden")
    YamlValueRepository(overridden).save({"app.name": "persisted"})

    before = len(log_records)
    reg = SettingsRegistry(value_repository=YamlValueRepository(overridden))
    reg.register(SettingDefinition(key="app.name", kind=SettingKind.TEXT, default="default", category="app"))
    records = log_records[before:]

    assert reg.get_value("app.name") == "persisted", "REQ-022 / AC-027 precedence must not change"
    warnings = [str(r) for r in records if level_name(r) == "WARNING"]
    assert any("app.name" in text for text in warnings), (
        f"no WARNING named the persisted override of app.name; records: {[str(r) for r in records]}"
    )

    # A persisted value equal to the definition default is not an override, so no WARNING names it.
    equal = str(tmp_path / "equal")
    YamlValueRepository(equal).save({"app.equal": "default"})
    before_equal = len(log_records)
    equal_registry = SettingsRegistry(value_repository=YamlValueRepository(equal))
    equal_registry.register(
        SettingDefinition(key="app.equal", kind=SettingKind.TEXT, default="default", category="app")
    )
    quiet = [str(r) for r in log_records[before_equal:] if level_name(r) == "WARNING" and "app.equal" in str(r)]
    assert quiet == [], f"a persisted value equal to the default is not an override: {quiet}"
