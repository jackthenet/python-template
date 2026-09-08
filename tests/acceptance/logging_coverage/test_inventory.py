"""AC-001: the normative inventory covers every public class and module function.

REQ-001: the feature defines the normative inventory of every public class and
public module function across all backend features, each with its required
tracing treatment.
"""

from __future__ import annotations

from logging_coverage_test_helpers import (
    INVENTORY_CLASSES,
    INVENTORY_MODULE_FUNCTIONS,
)


def test_inventory_covers_all_public_classes() -> None:
    """AC-001: every inventory class is traced; every inventory module function is traced."""
    # Every public class in the normative inventory is traced (@logged_class).
    for name, cls in INVENTORY_CLASSES.items():
        assert getattr(cls, "__logged_class__", False) is True, (
            f"{name} is not traced with @logged_class"
        )

    # Every public module function in the normative inventory is traced (@logged).
    for name, fn in INVENTORY_MODULE_FUNCTIONS.items():
        assert getattr(fn, "__logged__", False) is True, (
            f"{name} is not traced with @logged"
        )
