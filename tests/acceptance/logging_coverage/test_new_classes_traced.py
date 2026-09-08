"""AC-012: new public classes MUST be traced by default (forward-looking policy),
with ``include_args=False`` where secrets are handled.

REQ-012: new public classes MUST be traced by default. This is enforced by
scanning every public class across the backend features: each must either be
traced (``@logged_class``) or be an excluded kind (exception, pure data model,
enum, or protocol — no behavior to trace).
"""

from __future__ import annotations

import ast
import importlib
import pathlib
from enum import Enum
from typing import Protocol

from pydantic import BaseModel
from sqlmodel import SQLModel

_ROOT = pathlib.Path("src/backend")


def _public_classes() -> list[tuple[str, str]]:
    """Yield (module_name, class_name) for every public class in the backend."""
    items: list[tuple[str, str]] = []
    for path in sorted(_ROOT.rglob("*.py")):
        if path.name.startswith("_"):
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        rel = path.relative_to(_ROOT).with_suffix("")
        module = "backend." + ".".join(rel.parts)
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and not node.name.startswith("_"):
                items.append((module, node.name))
    return items


def _is_excluded(cls: type) -> bool:
    """True when the class has no behavior to trace (exception, data model, enum,
    or protocol)."""
    return (
        issubclass(cls, Exception)
        or issubclass(cls, BaseModel)
        or issubclass(cls, SQLModel)
        or issubclass(cls, Enum)
        or issubclass(cls, Protocol)
    )


def test_new_public_classes_traced_by_default() -> None:
    """AC-012: every public class is traced by default, unless it is an excluded
    kind (exception / data model / enum / protocol)."""
    for module_name, class_name in _public_classes():
        module = importlib.import_module(module_name)
        cls = getattr(module, class_name)
        if _is_excluded(cls):
            continue
        assert getattr(cls, "__logged_class__", False) is True, (
            f"{class_name} ({module_name}) is a public class but is not traced"
        )
