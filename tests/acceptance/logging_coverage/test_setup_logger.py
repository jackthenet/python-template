"""AC-011: the entrypoint (``src/main.py``) calls ``setup_logger(Settings(...))``
exactly once at startup, before any feature code runs; a second call is a no-op.

REQ-011 / ADR-035: the entrypoint calls ``setup_logger`` exactly once at
startup; the call is idempotent and thread-safe (a second call is a no-op).
"""

from __future__ import annotations

import ast
from pathlib import Path

_MAIN = Path("src/main.py")


def _is_setup_logger_call(node: ast.expr) -> bool:
    """True when the expression is a call to ``setup_logger`` (bare or qualified)."""
    if not isinstance(node, ast.Call):
        return False
    func = node.func
    if isinstance(func, ast.Name):
        return func.id == "setup_logger"
    if isinstance(func, ast.Attribute):
        return func.attr == "setup_logger"
    return False


def test_entrypoint_calls_setup_logger_once() -> None:
    """AC-011: ``src/main.py`` calls ``setup_logger`` exactly once, at module level,
    before any feature code runs."""
    source = _MAIN.read_text(encoding="utf-8")
    tree = ast.parse(source)

    # Count every setup_logger(...) call in the module.
    all_calls = [n for n in ast.walk(tree) if _is_setup_logger_call(n)]
    assert len(all_calls) == 1, (
        f"src/main.py must call setup_logger exactly once (found {len(all_calls)})"
    )

    # The call must be at module level (a top-level expression statement), i.e.
    # it runs at startup before any feature code is invoked.
    module_level_calls = [
        stmt
        for stmt in tree.body
        if isinstance(stmt, ast.Expr) and _is_setup_logger_call(stmt.value)
    ]
    assert len(module_level_calls) == 1, (
        "the setup_logger call must be a top-level module statement (runs at startup)"
    )
