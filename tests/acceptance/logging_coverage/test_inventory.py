"""AC-001: the normative inventory covers every public class and module function.

REQ-001: the feature defines the normative inventory of every public class and
public module function across all backend features, each with its required
tracing treatment.

AC-015 of change ``settings-public-registry-setter`` (its REQ-010) is witnessed
here too: the ``docs/specs/logging-coverage.md`` §3.1 table gained a `module
function` row for each of that change's five install operations, and the
executable inventory the whole logging-coverage suite reads
(``tests/logging_coverage_test_helpers.INVENTORY_MODULE_FUNCTIONS``) has to carry
those rows. The spec table is the normative list — the expectation below is read
from it, never the other way round.
"""

from __future__ import annotations

import pathlib

from logging_coverage_test_helpers import (
    INVENTORY_CLASSES,
    INVENTORY_MODULE_FUNCTIONS,
)

# docs/specs/logging-coverage.md §3.1 — the normative inventory table.
_SPEC = pathlib.Path("docs/specs/logging-coverage.md")

# The five install operations of docs/specs/settings-public-registry-setter.md AC-015.
_INSTALL_OPERATIONS = frozenset(
    {
        "set_settings_registry",
        "set_event_bus",
        "set_permission_service",
        "set_search_service",
        "set_session_service",
    }
)

# logging-coverage.md §3.1 note: each install operation is traced with
# @logged(slow_threshold_ms=5), the same threshold as its sibling get_* / reset_*.
_INSTALL_SLOW_THRESHOLD_MS = 5

# A §3.1 table row starts ``| Name(...) | Feature | Kind |`` — three cells minimum.
_MIN_ROW_CELLS = 3


def _spec_inventory_rows() -> list[tuple[str, str]]:
    """``(name, kind)`` for every row of the §3.1 inventory table in the spec.

    The table is the normative artifact, so the expectation is read from it rather
    than restated here: a row is a table line whose first cell is a backticked
    ``Name(...)`` (the header and separator rows are not).
    """
    lines = _SPEC.read_text(encoding="utf-8").splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith("### 3.1"))
    stop = next(i for i, line in enumerate(lines) if line.startswith("### 3.2"))
    rows: list[tuple[str, str]] = []
    for line in lines[start:stop]:
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < _MIN_ROW_CELLS or not cells[0].startswith("`"):
            continue
        rows.append((cells[0].strip("`").split("(")[0], cells[2]))
    return rows


def test_inventory_covers_all_public_classes() -> None:
    """AC-001: every inventory class is traced; every inventory module function is traced."""
    # Every public class in the normative inventory is traced (@logged_class).
    for name, cls in INVENTORY_CLASSES.items():
        assert getattr(cls, "__logged_class__", False) is True, f"{name} is not traced with @logged_class"

    # Every public module function in the normative inventory is traced (@logged).
    for name, fn in INVENTORY_MODULE_FUNCTIONS.items():
        assert getattr(fn, "__logged__", False) is True, f"{name} is not traced with @logged"


def test_inventory_covers_install_operations() -> None:
    """AC-015 (settings-public-registry-setter REQ-010): the inventory covers the five install operations.

    Two separate claims, both from the spec: the executable inventory carries a
    ``module function`` row for each of the five install operations §3.1 lists, and
    each of the five is actually traced with a concrete ``slow_threshold_ms``.
    """
    install_rows = {
        name for name, kind in _spec_inventory_rows() if kind == "module function" and name.startswith("set_")
    }
    assert install_rows == _INSTALL_OPERATIONS, (
        f"docs/specs/logging-coverage.md §3.1 lists the install-operation rows {sorted(install_rows)}, "
        f"expected {sorted(_INSTALL_OPERATIONS)} (AC-015)"
    )

    missing = sorted(name for name in install_rows if name not in INVENTORY_MODULE_FUNCTIONS)
    assert not missing, (
        f"the executable inventory has no 'module function' row for {missing}, which "
        f"docs/specs/logging-coverage.md §3.1 lists (AC-015)"
    )

    for name in sorted(install_rows):
        fn = INVENTORY_MODULE_FUNCTIONS[name]
        assert getattr(fn, "__logged__", False) is True, f"{name} is not traced with @logged (AC-015)"
        assert getattr(fn, "slow_threshold_ms", None) == _INSTALL_SLOW_THRESHOLD_MS, (
            f"{name} is not traced with @logged(slow_threshold_ms={_INSTALL_SLOW_THRESHOLD_MS}) "
            "(docs/specs/logging-coverage.md §3.1 note)"
        )
