"""Round-trip tests for the settings YAML repositories (docs/specs/settings.md INV-009).

Reproduction tests for main-ci-green item A: the safe YAML dumper emits
U+0085 (NEL) literally inside a single-quoted scalar, while its reader treats
NEL as a line break — so a stored value comes back silently changed
(settings INV-009, settings-coverage INV-002).
"""

from __future__ import annotations

from pathlib import Path

from backend.settings import Template, YamlTemplateRepository, YamlValueRepository

_NEL = "\x85"  # U+0085: the one code point the dumper does not escape


def test_yaml_value_roundtrip_nel(tmp_path: Path) -> None:
    """INV-002: save(values) then load() returns the identical mapping, NEL included."""
    repo = YamlValueRepository(str(tmp_path / "values"))
    values = {"app.list": [_NEL, "ok"], "app.text": _NEL, "app.embedded": f"a{_NEL}b"}

    repo.save(values)

    assert repo.load() == values


def test_yaml_template_roundtrip_nel(tmp_path: Path) -> None:
    """INV-009: save(template) then get(name) returns an equal template."""
    repo = YamlTemplateRepository(tmp_path / "templates")
    template = Template(name="prof", category="app", group=None, values={"app.a": _NEL})

    repo.save(template)

    loaded = repo.get("prof")
    assert loaded is not None
    assert loaded.values == {"app.a": _NEL}
    assert loaded == template
