"""Contract tests for the settings-coverage value repository (AC-014, NFR-005)."""

from __future__ import annotations

from pathlib import Path

import yaml

from backend.settings import YamlValueRepository


def test_yaml_value_repository(tmp_path: Path) -> None:
    """AC-014: save writes values.yaml; load returns the values."""
    repo = YamlValueRepository(str(tmp_path / "values"))
    values = {"a": "x", "b": 1, "c": ["admin", "member"]}
    repo.save(values)

    path = tmp_path / "values" / "values.yaml"
    assert path.exists()
    assert repo.load() == values


def test_atomic_write(tmp_path: Path) -> None:
    """NFR-005: the file is always either absent or valid YAML (atomic write)."""
    repo = YamlValueRepository(str(tmp_path / "values"))
    repo.save({"a": "x"})

    path = tmp_path / "values" / "values.yaml"
    # The written file parses as valid YAML.
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert data == {"a": "x"}
    # No temp files remain in the directory.
    leftovers = [p for p in (tmp_path / "values").iterdir() if p.name.endswith(".tmp")]
    assert not leftovers
