"""AC-009: every traced class's docstring mentions that the class is traced via
the shared logging feature (AuthService pattern).

REQ-009: every traced class's docstring mentions that the class is traced via
the shared logging feature.
"""

from __future__ import annotations

from logging_coverage_test_helpers import INVENTORY_CLASSES


def test_traced_class_docstrings_mention_tracing() -> None:
    """AC-009: each inventory class's docstring mentions tracing (``traced`` +
    ``logged``)."""
    for name, cls in INVENTORY_CLASSES.items():
        doc = (cls.__doc__ or "").lower()
        assert "traced" in doc, f"{name} docstring does not mention that it is traced"
        assert "logged" in doc, f"{name} docstring does not mention the logging feature"
