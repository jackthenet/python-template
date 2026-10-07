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


# ---------------------------------------------------------------------------
# AC-019 / REQ-014 — the agent-facing guidance records
# ---------------------------------------------------------------------------

# The four guidance files REQ-014 names — the whole scope of the guidance correction.
_GUIDANCE_FILES = (
    "AGENTS.md",
    ".agents/skills/python-best-practices/SKILL.md",
    ".agents/skills/python-best-practices/references/modern-python.md",
    ".agents/skills/python-best-practices/references/errors-and-resources.md",
)

# AC-019 clause 1: guidance must not name the removed backend (REQ-013 names it).
_REMOVED_BACKEND_WORD = re.compile(rf"\b{_REMOVED_BACKEND}\b", re.IGNORECASE)

# AC-019 clause 2: the decorator parameters REQ-007 removes with no compatibility shim (REQ-015).
_REMOVED_PARAMETERS = ("context_getter", "depth")

# AC-019 clause 3: the entry points of the feature's public surface (§3 / REQ-015).
_FEATURE_ENTRY_POINTS = ("setup_logger", "logged", "logged_class", "get_logger")

# REQ-005 covers guidance too: an example shows the feature's exported entry points, never a backend
# import or a backend-qualified logger. The processor layer may still be named as a library, so only
# an import of it or a call through it is a defect.
_BACKEND_ENTRY_POINT = re.compile(
    rf"\b(?:import|from)\s+(?:{_PROCESSOR_LAYER}|{_REMOVED_BACKEND})\b"
    rf"|\b(?:{_PROCESSOR_LAYER}|{_REMOVED_BACKEND})\s*\.\s*(?:get_logger|getLogger|logger)\b"
)

# AC-019 clause 4: every shown call must match ``setup_logger(*, renderer: str | None = None)``.
_SETUP_LOGGER_CALL = re.compile(r"setup_logger\s*\(")
_KEYWORD_ONLY_RENDERER_ARGS = re.compile(r"renderer\s*=\s*\S.*", re.DOTALL)


def _line_of(text: str, offset: int) -> int:
    """The 1-based line of ``offset``, so a failure names the offending guidance line."""
    return text.count("\n", 0, offset) + 1


def _setup_logger_calls(text: str) -> list[tuple[int, str]]:
    """Every ``setup_logger(...)`` call the guidance shows, as ``(line, argument text)``.

    The arguments are read with a paren-balancing scan, so the rejected ``setup_logger(Settings(…))``
    shape is captured whole instead of stopping at its inner closing paren.
    """
    calls: list[tuple[int, str]] = []
    for match in _SETUP_LOGGER_CALL.finditer(text):
        depth = 0
        for index in range(match.end() - 1, len(text)):
            if text[index] == "(":
                depth += 1
            elif text[index] == ")":
                depth -= 1
                if depth == 0:
                    calls.append((_line_of(text, match.start()), text[match.end() : index].strip()))
                    break
    return calls


def _amended_signature_accepts(args: str) -> bool:
    """Whether ``setup_logger(<args>)`` is a call the amended signature accepts (REQ-006, §3).

    ``setup_logger(*, renderer: str | None = None)`` takes no positional argument and no ``Settings``
    object: either no argument at all, or the single keyword-only ``renderer``.
    """
    if not args:
        return True
    return "," not in args and _KEYWORD_ONLY_RENDERER_ARGS.fullmatch(args) is not None


def _guidance_violations(rel: str, text: str) -> list[str]:
    """Every AC-019 clause the guidance text violates, each naming its file and line."""
    violations: list[str] = []
    for match in _REMOVED_BACKEND_WORD.finditer(text):
        violations.append(f"{rel}:{_line_of(text, match.start())} names the removed backend {match.group(0)!r}")
    for name in _REMOVED_PARAMETERS:
        for match in re.finditer(rf"\b{name}\b", text):
            violations.append(f"{rel}:{_line_of(text, match.start())} names the removed parameter {name!r}")
    for name in _FEATURE_ENTRY_POINTS:
        if not re.search(rf"\b{name}\b", text):
            violations.append(f"{rel} does not name the feature entry point {name!r}")
    for match in _BACKEND_ENTRY_POINT.finditer(text):
        violations.append(f"{rel}:{_line_of(text, match.start())} shows the backend entry point {match.group(0)!r}")
    for line, args in _setup_logger_calls(text):
        if not _amended_signature_accepts(args):
            violations.append(f"{rel}:{line} shows setup_logger({args}), a call the amended signature rejects")
    return violations


def test_ac_019_guidance_names_feature_entry_points() -> None:
    """AC-019 / REQ-014: none of the four guidance files names the removed backend or a removed
    decorator parameter, each names the shared logging feature's own entry points, and every
    ``setup_logger`` call they show is a call the amended signature accepts."""
    violations: list[str] = []
    for rel in _GUIDANCE_FILES:
        path = _REPO_ROOT / rel
        if not path.is_file():
            violations.append(f"{rel} does not exist")
            continue
        violations.extend(_guidance_violations(rel, path.read_text(encoding="utf-8")))

    assert not violations, "AC-019 / REQ-014: " + "; ".join(violations)
