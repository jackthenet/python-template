"""AC-009 (structlog-logging) / REQ-010 + AC-010 v2 (logging-coverage): a feature's
one-off statements stay statements, but they are written through the shared logging
feature's exported ``get_logger()`` and the feature module imports no logging backend.

The witness is per file (spec AC-009 names the four files and the statement count in
each): the module's source is parsed, its one-off statement call sites are counted —
the statements are kept as statements, none added, none removed — and every one of
them must be written on a logger the module obtained from ``get_logger()``.
"""

from __future__ import annotations

import ast
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]

# REQ-001 / REQ-005: the logging backends a feature module must never import.
_BACKEND_PACKAGES = frozenset({"loguru", "structlog"})

# The level methods through which a one-off statement is written (REQ-005).
_LEVEL_METHODS = frozenset({"debug", "info", "warning", "warn", "error", "exception", "critical", "fatal", "log"})


def _callee_name(func: ast.expr) -> str | None:
    """The final name of a callee: ``get_logger(...)`` and ``<mod>.get_logger(...)`` both give ``get_logger``."""
    if isinstance(func, ast.Attribute):
        return func.attr
    if isinstance(func, ast.Name):
        return func.id
    return None


def _parse(relative_path: str) -> ast.Module:
    """The parsed module at ``relative_path``, relative to the repository root."""
    return ast.parse((_REPO_ROOT / relative_path).read_text(encoding="utf-8"), filename=relative_path)


def _backend_imports(tree: ast.AST) -> list[str]:
    """Every import of a logging backend package inside ``tree`` (REQ-001 / REQ-005)."""
    found: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found += [alias.name for alias in node.names if alias.name.split(".")[0] in _BACKEND_PACKAGES]
        elif isinstance(node, ast.ImportFrom) and (node.module or "").split(".")[0] in _BACKEND_PACKAGES:
            found += [f"{node.module}.{alias.name}" for alias in node.names]
    return found


def _feature_logger_names(tree: ast.AST) -> set[str]:
    """Every name the module binds to a ``get_logger()`` call (its feature loggers)."""
    names: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign | ast.AnnAssign) or not isinstance(node.value, ast.Call):
            continue
        if _callee_name(node.value.func) != "get_logger":
            continue
        if isinstance(node.target, ast.Name):
            names.add(node.target.id)
        elif isinstance(node.target, ast.Attribute):
            names.add(node.target.attr)
    return names


def _statement_calls(tree: ast.AST) -> list[ast.Call]:
    """The one-off statement call sites in ``tree``: a call of the form ``<logger>.<level>(...)``."""
    return [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in _LEVEL_METHODS
    ]


def _written_via_get_logger(call: ast.Call, feature_names: set[str]) -> bool:
    """True when the call's receiver is a ``get_logger(...)`` call or a name bound to one."""
    receiver = call.func.value
    if isinstance(receiver, ast.Call):
        return _callee_name(receiver.func) == "get_logger"
    if isinstance(receiver, ast.Name):
        return receiver.id in feature_names
    if isinstance(receiver, ast.Attribute):
        return receiver.attr in feature_names
    return False


def _statement_violations(relative_path: str, expected_statements: int) -> list[str]:
    """AC-009's three clauses for one module, as violation strings (empty means it holds).

    The clauses are collected instead of asserted one by one, so one run names every
    violation — in both files — and a clause that already holds is visible in the
    evidence by its absence.
    """
    tree = _parse(relative_path)
    violations: list[str] = []

    if backends := _backend_imports(tree):
        violations.append(f"{relative_path} imports a logging backend: {backends}")

    statements = _statement_calls(tree)
    if len(statements) != expected_statements:
        violations.append(f"{relative_path} keeps {expected_statements} one-off statements, found {len(statements)}")

    feature_names = _feature_logger_names(tree)
    if not_migrated := sorted(call.lineno for call in statements if not _written_via_get_logger(call, feature_names)):
        violations.append(f"{relative_path} statements not written through get_logger(): line(s) {not_migrated}")

    return violations


def test_ac_009_settings_statements_go_through_get_logger() -> None:
    """AC-009 (settings half): the 17 statements in ``registry.py`` and the 11 in
    ``repository.py`` are written through ``get_logger()``, and neither module — nor
    any other module of the settings feature — imports a logging backend."""
    # REQ-005 fixes the statement count per file; logging-coverage REQ-010 v2 keeps each of them a statement.
    violations = [
        *_statement_violations("src/backend/settings/registry.py", 17),
        *_statement_violations("src/backend/settings/repository.py", 11),
    ]

    # T-004's completion gate: the whole settings feature is backend-free.
    settings_dir = _REPO_ROOT / "src" / "backend" / "settings"
    offenders = sorted(
        relative
        for relative in (path.relative_to(_REPO_ROOT).as_posix() for path in settings_dir.rglob("*.py"))
        if _backend_imports(_parse(relative))
    )
    if offenders:
        violations.append(f"a module under src/backend/settings/ imports a logging backend: {offenders}")

    assert not violations, "AC-009 / REQ-005 (logging-coverage REQ-010 v2): " + "; ".join(violations)
