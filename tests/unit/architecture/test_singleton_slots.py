"""AC-017 / EDGE-008: the architecture guard for the five feature singleton slots.

REQ-012: no file under ``src/`` or ``tests/`` writes another package's singleton
slot — every outside-owner write site uses the owning feature's install operation.
REQ-013 (ADR-084): the pattern is guarded twice; ruff ``TID251`` (T-008) bans the
private import, this scan test bans the write, in real statements **and** inside
string literals handed to ``subprocess`` — an ast-only scan would not see the
subprocess-embedded sites come back.

EDGE-008: a module writing its **own** slot (the five lazy-create and reset paths)
is not reported, and neither is importing a public symbol from the owning module
nor reading a foreign slot — the guard targets the foreign write, not the module.

The planted-violation fixtures are built into ``tmp_path`` in a mirrored
``src/backend/<pkg>/<module>.py`` layout, never inside the repository, so the
repository scan and the lint gate stay clean (ADR-084). The scanner follows the
repository's only existing source-scanning test,
``tests/acceptance/logging_coverage/test_new_classes_traced.py``: ``ast.parse`` over
a CWD-relative ``rglob("*.py")``, because pytest runs from the repository root.
"""

from __future__ import annotations

import ast
import pathlib
import re
from collections.abc import Iterable
from dataclasses import dataclass

# The owner table (spec §3.4 / ADR-084): owning module path -> its private slot.
_OWNERS: tuple[tuple[str, str], ...] = (
    ("backend.settings.registry", "_registry"),
    ("backend.eventbus.eventbus", "_default_bus"),
    ("backend.permissions.service", "_permission_service"),
    ("backend.search.service", "_singleton"),
    ("backend.sessionmanagement.service", "_session_service"),
)
_SLOT_BY_MODULE: dict[str, str] = dict(_OWNERS)
_SLOTS: frozenset[str] = frozenset(_SLOT_BY_MODULE.values())
_REPO_DIRS: tuple[str, ...] = ("src", "tests")

# The string-literal half of the scan. The pattern is built from the owner table at
# import time so this file never contains the pattern itself — the repository scan
# reads this file too, and a literal spelling would be reported (ADR-084 accepts
# that heuristic cost for strings that spell the write out).
_EMBEDDED_WRITE: dict[str, re.Pattern[str]] = {
    slot: re.compile(rf"(?:[A-Za-z_][A-Za-z0-9_]*\.)?{re.escape(slot)}\s*\[\s*0\s*\]\s*=") for slot in _SLOTS
}


@dataclass(frozen=True, slots=True)
class Violation:
    """One slot write by a file that does not own the slot."""

    path: str
    line: int
    slot: str
    form: str  # "import" | "write" | "embedded-write"

    def __str__(self) -> str:
        return f"{self.path}:{self.line}: {self.form} of {self.slot}"


def _owner_path(module: str) -> pathlib.Path:
    """The repository path of an owning module (the scan reaches it through ``src/``)."""
    return pathlib.Path("src", *module.split(".")).with_suffix(".py")


def _owned_slots(path: pathlib.Path) -> frozenset[str]:
    """Slots this file owns — matched on the mirrored ``backend/<pkg>/<module>.py``
    path suffix, so the same rule holds for the repository and for a ``tmp_path`` mirror."""
    owned: set[str] = set()
    location = (*path.parts[:-1], path.stem)
    for module, slot in _OWNERS:
        parts = tuple(module.split("."))
        if location[-len(parts) :] == parts:
            owned.add(slot)
    return frozenset(owned)


def _written_slot(target_value: ast.expr) -> str | None:
    """The slot name a subscript target is rooted on: ``slot[...]`` or ``mod.slot[...]``."""
    if isinstance(target_value, ast.Name):
        return target_value.id
    if isinstance(target_value, ast.Attribute):
        return target_value.attr
    return None


def _embedded(path: pathlib.Path, node: ast.Constant, owned: frozenset[str]) -> list[Violation]:
    """Slot writes spelled out inside a string literal (the subprocess-code form)."""
    text: str = node.value
    found: list[Violation] = []
    for slot, pattern in _EMBEDDED_WRITE.items():
        if slot in owned:
            continue
        match = pattern.search(text)
        if match is not None:
            found.append(Violation(str(path), node.lineno + text[: match.start()].count("\n"), slot, "embedded-write"))
    return found


def _import_violation(path: pathlib.Path, node: ast.stmt, owned: frozenset[str]) -> Violation | None:
    """The import that makes a foreign write possible (the ``TID251`` half, in-test)."""
    if not isinstance(node, ast.ImportFrom) or node.module not in _SLOT_BY_MODULE:
        return None
    slot = _SLOT_BY_MODULE[node.module]
    if slot in owned or not any(alias.name == slot for alias in node.names):
        return None
    return Violation(str(path), node.lineno, slot, "import")


def _write_violations(path: pathlib.Path, node: ast.stmt, owned: frozenset[str]) -> list[Violation]:
    """A subscript write rooted on a slot name: ``slot[0] = ...`` or ``mod.slot[0] = ...``."""
    found: list[Violation] = []
    if not isinstance(node, ast.Assign):
        return found
    for target in node.targets:
        if not isinstance(target, ast.Subscript):
            continue
        slot = _written_slot(target.value)
        if slot in _SLOTS and slot not in owned:
            found.append(Violation(str(path), node.lineno, slot, "write"))
    return found


def _scan_file(path: pathlib.Path) -> list[Violation]:
    """Every foreign slot write in one file: private import, subscript write, embedded write.

    ``ponytail:`` the scanner resolves no import bindings. A write through an import
    alias (``from backend.settings.registry import _registry as _r`` then a write on
    ``_r``) is caught by the import half, not by the write half, and a write built
    through ``getattr`` is not caught at all. Upgrade path: build a per-file
    asname -> slot map from the ``ImportFrom`` nodes and match write targets against it.
    """
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    owned = _owned_slots(path)
    found: list[Violation] = []
    for node in ast.walk(tree):
        imported = _import_violation(path, node, owned)
        if imported is not None:
            found.append(imported)
        found.extend(_write_violations(path, node, owned))
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            found.extend(_embedded(path, node, owned))
    return found


def _python_files(root: pathlib.Path) -> list[pathlib.Path]:
    return sorted(root.rglob("*.py"))


def _scan_files(files: Iterable[pathlib.Path]) -> list[Violation]:
    return [violation for path in files for violation in _scan_file(path)]


def _repo_files() -> list[pathlib.Path]:
    """Every ``.py`` under ``src/`` and ``tests/`` (CWD-relative, as pytest runs)."""
    return [path for name in _REPO_DIRS for path in _python_files(pathlib.Path(name))]


def _plant(root: pathlib.Path, relative: str, lines: list[str]) -> pathlib.Path:
    """Write a fixture file under ``root`` (a mirrored ``src/backend/...`` layout)."""
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def test_ac_017_no_cross_package_slot_write() -> None:
    """AC-017 (REQ-012, REQ-013): no file under ``src/`` or ``tests/`` writes a slot
    owned by a different package."""
    files = _repo_files()
    for module in _SLOT_BY_MODULE:
        assert _owner_path(module) in files, f"{module} is outside the scan scope: the scan would pass vacuously"
    violations = _scan_files(files)
    listed = "\n".join(str(violation) for violation in violations)
    assert not violations, f"{len(violations)} foreign singleton-slot write(s):\n{listed}"


def test_ac_017_scanner_reports_planted_violation(tmp_path: pathlib.Path) -> None:
    """AC-017: a planted violation is reported with its path and line — the private
    import form, the module-alias write form, and the form embedded in a string
    handed to ``subprocess`` — and all five slots are in the table."""
    src = tmp_path / "src"
    module, slot = "backend.settings.registry", "_registry"

    importer = _plant(src, "backend/reporting/importer.py", [f"from {module} import {slot}", f"{slot}[0] = object()"])
    alias_writer = _plant(
        src,
        "backend/reporting/alias_writer.py",
        ["from backend.settings import registry as _mod", f"_mod.{slot}[0] = object()"],
    )
    embedder = _plant(
        src,
        "backend/reporting/embedder.py",
        [
            "import subprocess, sys",
            f'code = "_mod.{slot}[0] = object()"',
            "subprocess.run([sys.executable, '-c', code])",
        ],
    )
    migrated = _plant(
        src,
        "backend/reporting/migrated.py",
        [
            "from backend.settings import registry as _mod",
            "from backend.settings import set_settings_registry",
            "set_settings_registry(_mod.SettingsRegistry())",
        ],
    )

    found = _scan_files(_python_files(src))
    by_file: dict[str, set[tuple[str, int]]] = {}
    for violation in found:
        by_file.setdefault(violation.path, set()).add((violation.form, violation.line))

    assert {form for form, _ in by_file[str(importer)]} == {"import", "write"}, by_file
    assert by_file[str(alias_writer)] == {("write", 2)}, by_file
    assert by_file[str(embedder)] == {("embedded-write", 2)}, by_file
    assert {violation.slot for violation in found} == {slot}, found
    assert str(migrated) not in by_file, by_file

    # Every one of the five slots is guarded, not only the settings one.
    mirror = tmp_path / "mirror"
    for owner_module, owner_slot in _OWNERS:
        _plant(
            mirror,
            f"backend/consumers/writes_{owner_slot.lstrip('_')}.py",
            [f"from {owner_module} import {owner_slot}", f"{owner_slot}[0] = object()"],
        )
    assert {violation.slot for violation in _scan_files(_python_files(mirror))} == _SLOTS


def test_edge_008_owner_slot_write_allowed(tmp_path: pathlib.Path) -> None:
    """EDGE-008: an owning module writing its **own** slot is not reported (the five
    lazy-create and reset paths need no suppression); a foreign *read* and a public
    import are not reported either."""
    src = tmp_path / "src"
    for module, slot in _OWNERS:
        _plant(
            src,
            "/".join(module.split(".")) + ".py",
            [f"{slot}: list[object | None] = [None]", f"{slot}[0] = object()", f"{slot}[0] = None"],
        )
    _plant(
        src,
        "backend/consumer/reader.py",
        [
            "from backend.settings import registry as _mod",
            "from backend.settings.registry import SettingsRegistry",
            "saved = _mod._registry[0]",
        ],
    )
    assert _scan_files(_python_files(src)) == []

    # Measured on the repository itself: the five owner modules keep their own slot
    # statements and report nothing.
    for module in _SLOT_BY_MODULE:
        assert _scan_file(_owner_path(module)) == [], module
