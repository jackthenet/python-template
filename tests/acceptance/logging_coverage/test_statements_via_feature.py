"""AC-009 (structlog-logging) / REQ-010 + AC-010 v2 (logging-coverage): a feature's
one-off statements stay statements, but they are written through the shared logging
feature's exported ``get_logger()`` and the feature module imports no logging backend.

The witness is per file (spec AC-009 names the four files and the statement count in
each): the module's source is parsed, its one-off statement call sites are counted —
the statements are kept as statements, none added, none removed — and every one of
them must be written on a logger the module obtained from ``get_logger()``.

The static clauses say nothing about the record, so each per-feature witness is
paired with a runtime half: the migrated statements are executed and their message
wording — spec §9 row 2, "unchanged wording" — is asserted on the pipeline capture.
That is the witness the retired direct-backend test carried, re-homed here.
"""

from __future__ import annotations

import ast
import tempfile
from pathlib import Path
from typing import Any

from logging_coverage_test_helpers import messages

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


def _dir_backend_imports(relative_dir: str) -> list[str]:
    """Every module under ``relative_dir`` (repo-relative) that imports a logging backend.

    The per-feature half of REQ-001/REQ-005: migrating one file is not enough when a
    sibling module of the same feature still imports the backend.
    """
    return sorted(
        relative
        for relative in (path.relative_to(_REPO_ROOT).as_posix() for path in (_REPO_ROOT / relative_dir).rglob("*.py"))
        if _backend_imports(_parse(relative))
    )


def _feature_logger_names(tree: ast.AST) -> set[str]:
    """Every name the module binds to a ``get_logger()`` call (its feature loggers)."""
    names: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign | ast.AnnAssign) or not isinstance(node.value, ast.Call):
            continue
        if _callee_name(node.value.func) != "get_logger":
            continue
        # ``ast.Assign`` has a list of targets, ``ast.AnnAssign`` a single one.
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        for target in targets:
            if isinstance(target, ast.Name):
                names.add(target.id)
            elif isinstance(target, ast.Attribute):
                names.add(target.attr)
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


def _run_settings_statements() -> None:
    """Execute two migrated settings statements (register + set value) on an isolated registry."""
    from backend.settings.models import SettingDefinition, SettingKind
    from backend.settings.registry import SettingsRegistry
    from backend.settings.repository import MemoryTemplateRepository, YamlValueRepository

    registry = SettingsRegistry(
        template_repository=MemoryTemplateRepository(), value_repository=YamlValueRepository(tempfile.mkdtemp())
    )
    registry.register(SettingDefinition(key="ac009.probe", kind=SettingKind.TEXT, default="d"))
    registry.set_value("ac009.probe", "v")


def _run_eventbus_statements() -> None:
    """Execute two migrated event bus statements (publish + shutdown)."""
    from eventbus_test_helpers import UserCreated

    from backend.eventbus.eventbus import EventBus

    bus = EventBus()
    try:
        bus.publish(UserCreated(user_id="u1", email="e1"))
    finally:
        bus.shutdown()


def _missing_messages(records: list[Any], expected: tuple[str, ...]) -> list[str]:
    """The expected message wordings that never reached the pipeline capture."""
    seen = messages(records)
    return [text for text in expected if not any(text in record for record in seen)]


# The wording spec §9 row 2 keeps unchanged, as the retired direct-backend test asserted it.
_SETTINGS_STATEMENT_MESSAGES = ("setting registered: key=", "value set: key=")
_EVENTBUS_STATEMENT_MESSAGES = ("event bus: published event type", "event bus: shutdown initiated")


def test_ac_009_settings_statements_go_through_get_logger(log_records: list[Any]) -> None:
    """AC-009 (settings half): the 17 statements in ``registry.py`` and the 11 in
    ``repository.py`` are written through ``get_logger()``, and neither module — nor
    any other module of the settings feature — imports a logging backend."""
    # REQ-005 fixes the statement count per file; logging-coverage REQ-010 v2 keeps each of them a statement.
    violations = [
        *_statement_violations("src/backend/settings/registry.py", 17),
        *_statement_violations("src/backend/settings/repository.py", 11),
    ]

    # T-004's completion gate: the whole settings feature is backend-free.
    if offenders := _dir_backend_imports("src/backend/settings"):
        violations.append(f"a module under src/backend/settings/ imports a logging backend: {offenders}")

    assert not violations, "AC-009 / REQ-005 (logging-coverage REQ-010 v2): " + "; ".join(violations)

    # The kept statements still emit their unchanged wording through the pipeline (spec §9 row 2).
    _run_settings_statements()
    if missing := _missing_messages(log_records, _SETTINGS_STATEMENT_MESSAGES):
        raise AssertionError(f"AC-009: settings statements never emitted {missing}; got {messages(log_records)!r}")


def test_ac_009_eventbus_statements_go_through_get_logger(log_records: list[Any]) -> None:
    """AC-009 (event bus half): the 10 statements in ``eventbus.py`` are written through
    ``get_logger()``, and no module of the event bus feature imports a logging backend."""
    # REQ-005 fixes the statement count per file; logging-coverage REQ-010 v2 keeps each of them a statement.
    violations = _statement_violations("src/backend/eventbus/eventbus.py", 10)

    # T-005's completion gate: the whole event bus feature is backend-free.
    if offenders := _dir_backend_imports("src/backend/eventbus"):
        violations.append(f"a module under src/backend/eventbus/ imports a logging backend: {offenders}")

    assert not violations, "AC-009 / REQ-005 (logging-coverage REQ-010 v2): " + "; ".join(violations)

    # The kept statements still emit their unchanged wording through the pipeline (spec §9 row 2).
    _run_eventbus_statements()
    if missing := _missing_messages(log_records, _EVENTBUS_STATEMENT_MESSAGES):
        raise AssertionError(f"AC-009: event bus statements never emitted {missing}; got {messages(log_records)!r}")


# AC-009's four named files, with the statement count REQ-005 fixes in each.
_AC_009_STATEMENTS: dict[str, int] = {
    "src/backend/settings/registry.py": 17,
    "src/backend/settings/repository.py": 11,
    "src/backend/eventbus/eventbus.py": 10,
    "src/backend/permissions/service.py": 1,
}

# REQ-005 / AC-009 state the total explicitly ("each of the 39 one-off statements").
_AC_009_TOTAL_STATEMENTS = 39


def test_ac_009_statements_go_through_get_logger() -> None:
    """AC-009 (the spec-named all-four witness): none of the four files REQ-005 names imports a
    logging backend, and each of the 39 one-off statements is written through ``get_logger()``.

    The two witnesses above cover one feature each; this is the criterion as the spec states it —
    the four files and the 39 statements together — so it goes green only when the last of them
    (``src/backend/permissions/service.py``) is migrated. REQ-001's repo-wide half ("no module
    under ``src/`` or ``tests/`` imports one") is AC-001's witness, not this one's.
    """
    # Guards the table against drifting from REQ-005's per-file counts (17 + 11 + 10 + 1).
    assert sum(_AC_009_STATEMENTS.values()) == _AC_009_TOTAL_STATEMENTS, (
        "REQ-005 fixes 39 one-off statements across the four named files"
    )

    violations = [v for path, count in _AC_009_STATEMENTS.items() for v in _statement_violations(path, count)]

    assert not violations, "AC-009 / REQ-005 (logging-coverage REQ-010 v2): " + "; ".join(violations)
