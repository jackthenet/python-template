"""Contract test for the project's dependency set (docs/specs/structlog-logging.md AC-018 / NFR-004).

The dependency check is a gate the repository already runs — ``uv run deptry .`` is part of
``quality_check`` (``pyproject.toml``) and of the CI quality job — so the contract is asserted by
running that same check and reading the dependency declaration it checks, not by re-implementing
its rules. AC-018's three clauses are the report being clean, the removed backend being absent
from the dependency set, and the JSON serializer being used.
"""

from __future__ import annotations

import ast
import re
import subprocess
import sys
import tomllib
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]

# REQ-013 / NFR-004: the dependency set after the swap.
_REMOVED_BACKEND = "loguru"
_PROCESSOR_LAYER = "structlog"
_JSON_SERIALIZER = "orjson"

# The tree deptry scans for imports (it does not scan tests/), and the tree the file renderer —
# the consumer that makes the serializer "used" — lives in.
_SCANNED_TREE = "src"


def _pyproject() -> dict:
    """The parsed ``pyproject.toml``."""
    return tomllib.loads((_REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))


def _declared_names() -> set[str]:
    """The declared runtime dependency names, normalised (``loguru>=0.7.3`` -> ``loguru``)."""
    declared = _pyproject()["project"]["dependencies"]
    return {re.split(r"[^A-Za-z0-9.+-]+", spec, maxsplit=1)[0].lower().replace("_", "-") for spec in declared}


def _unused_dependency_suppressions() -> list[str]:
    """The packages suppressed as unused (deptry ``DEP002``) in ``pyproject.toml``."""
    return _pyproject()["tool"]["deptry"]["per_rule_ignores"].get("DEP002", [])


def _serializer_importers() -> list[str]:
    """Every module under ``src/`` that imports the JSON serializer (AC-018: it must be used)."""
    importers: list[str] = []
    for path in sorted((_REPO_ROOT / _SCANNED_TREE).rglob("*.py")):
        module = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(module):
            if isinstance(node, ast.Import) and any(a.name.split(".")[0] == _JSON_SERIALIZER for a in node.names):
                importers.append(path.relative_to(_REPO_ROOT).as_posix())
                break
            if isinstance(node, ast.ImportFrom) and (node.module or "").split(".")[0] == _JSON_SERIALIZER:
                importers.append(path.relative_to(_REPO_ROOT).as_posix())
                break
    return importers


def _dependency_report() -> subprocess.CompletedProcess[str]:
    """Run the dependency check the repository gates on, in this repository."""
    return subprocess.run(
        [sys.executable, "-m", "deptry", "."],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
    )


def test_ac_018_dependency_report_clean() -> None:
    """AC-018 / NFR-004 (REQ-013): the dependency check reports no unused and no missing
    dependency, the removed backend is absent from the dependency set, and the JSON serializer
    is declared and actually imported."""
    violations: list[str] = []
    declared = _declared_names()

    if _REMOVED_BACKEND in declared:
        violations.append(f"{_REMOVED_BACKEND} is still declared in [project].dependencies")
    if _PROCESSOR_LAYER not in declared:
        violations.append(f"{_PROCESSOR_LAYER} is not declared in [project].dependencies")

    if _JSON_SERIALIZER in _unused_dependency_suppressions():
        violations.append(f"{_JSON_SERIALIZER} is still suppressed as an unused dependency (DEP002)")
    if not _serializer_importers():
        violations.append(f"no module under {_SCANNED_TREE}/ imports {_JSON_SERIALIZER}, so it is unused")

    report = _dependency_report()
    if report.returncode != 0:
        output = (report.stdout + report.stderr).strip()
        codes = sorted({match.group(0) for match in re.finditer(r"DEP\d{3}", output)})
        suffix = f" ({codes})" if codes else ""
        violations.append(f"the dependency check reports issues{suffix}: {output}")

    assert not violations, "AC-018 / NFR-004 (REQ-013): " + "; ".join(violations)
