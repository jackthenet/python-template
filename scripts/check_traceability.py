"""Check referential integrity of the traceability matrix (docs/verification/traceability.md).

Convention B (Q-129): a matrix row is a HISTORICAL gate record — it records the state
observed by the change that wrote it. This check therefore verifies REFERENCES only
(coverage, dangling IDs, missing tests, undeclared status values); it never asserts
that a row's status is current, and it never fails on a dated RED/PENDING record.
"""

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

ID_RE = re.compile(r"\b(?:REQ|AC|INV|EDGE|NFR)-\d+\b")
REQ_OR_AC_RE = re.compile(r"\b(?:REQ|AC)-\d+\b")
BACKTICK_RE = re.compile(r"`([^`]+)`")
TEST_NAME_RE = re.compile(r"^test_[A-Za-z0-9_]+$")
TEST_DEF_RE = re.compile(r"def\s+(test_\w+)")
STATUS_TOKEN_RE = re.compile(r"^[A-Za-z/]+")

# A matrix table needs a header row, a separator row, and at least one data row.
MIN_TABLE_LINES = 3

# The vocabulary declared by the matrix's own §Invariants, plus N/A (which legitimately
# occurs in the wiring tables). Convention B: a value is a record of a past gate, so
# every declared value is legal — RED/PENDING included.
DECLARED_STATUSES = frozenset({"PENDING", "RED", "GREEN", "REFACTORED", "VERIFIED", "N/A"})


@dataclass
class MatrixRow:
    """One data row of a matrix table."""

    line: int
    ids: set[str] = field(default_factory=set)
    tests: set[str] = field(default_factory=set)
    status: str = ""


def spec_files(spec_dir: Path) -> list[Path]:
    """Spec files that define normative IDs (the template's IDs are formatting examples)."""
    return sorted(p for p in spec_dir.glob("*.md") if p.name != "template.md")


def defined_ids(spec_dir: Path) -> set[str]:
    """Every normative ID defined by any spec."""
    ids: set[str] = set()
    for path in spec_files(spec_dir):
        ids.update(ID_RE.findall(path.read_text(encoding="utf-8")))
    return ids


def test_names(test_dir: Path) -> set[str]:
    """Every test function name defined anywhere under tests/."""
    names: set[str] = set()
    for path in sorted(test_dir.rglob("*.py")):
        names.update(TEST_DEF_RE.findall(path.read_text(encoding="utf-8")))
    return names


def table_blocks(matrix_path: Path) -> list[list[tuple[int, list[str]]]]:
    """Every pipe-table in the matrix as (line number, cells); the prose between tables is dropped."""
    blocks: list[list[tuple[int, list[str]]]] = []
    block: list[tuple[int, list[str]]] = []
    for line_no, line in enumerate(matrix_path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            block.append((line_no, [c.strip() for c in stripped.strip("|").split("|")]))
        elif block:
            blocks.append(block)
            block = []
    if block:
        blocks.append(block)
    return blocks


def status_index(header: list[str]) -> int:
    """Index of a table's Status column, or -1 when the table has none (such tables are not rows)."""
    lowered = [cell.strip().lower() for cell in header]
    return lowered.index("status") if "status" in lowered else -1


def matrix_row(line_no: int, cells: list[str], status_idx: int) -> MatrixRow:
    """One data row: the normative IDs and backticked test names it cites, plus its Status cell."""
    text = " ".join(cells)
    return MatrixRow(
        line=line_no,
        ids=set(ID_RE.findall(text)),
        tests={t for t in BACKTICK_RE.findall(text) if TEST_NAME_RE.match(t.strip())},
        status=cells[status_idx],
    )


def table_rows(block: list[tuple[int, list[str]]]) -> list[MatrixRow]:
    """Data rows of one block; a block too short to be a table, or without a Status column, has none."""
    if len(block) < MIN_TABLE_LINES:
        return []
    status_idx = status_index(block[0][1])
    if status_idx < 0:
        return []
    return [matrix_row(no, cells, status_idx) for no, cells in block[2:] if len(cells) > status_idx]


def matrix_rows(matrix_path: Path) -> list[MatrixRow]:
    """Parse the matrix tables, keeping only tables that have a Status column."""
    return [row for block in table_blocks(matrix_path) for row in table_rows(block)]


def ids_without_row(matrix_path: Path, rows: list[MatrixRow], specs: set[str]) -> list[str]:
    """Rule 1: every REQ/AC defined by a spec has at least one matrix row."""
    referenced = {id_ for row in rows for id_ in row.ids}
    return [
        f"{id_} defined in docs/specs/ has no row in {matrix_path}"
        for id_ in sorted(specs)
        if REQ_OR_AC_RE.fullmatch(id_) and id_ not in referenced
    ]


def rows_citing_undefined_ids(matrix_path: Path, rows: list[MatrixRow], specs: set[str]) -> list[str]:
    """Rule 2: no matrix row references an ID that no spec defines."""
    return [
        f"{matrix_path}:{row.line}: row references undefined {id_}" for row in rows for id_ in sorted(row.ids - specs)
    ]


def rows_citing_missing_tests(matrix_path: Path, rows: list[MatrixRow], tests: set[str]) -> list[str]:
    """Rule 3: every backticked test function cited by a matrix row exists under tests/."""
    return [
        f"{matrix_path}:{row.line}: row references missing test {name}"
        for row in rows
        for name in sorted(row.tests - tests)
    ]


def status_token(status: str) -> str:
    """The vocabulary token a Status cell starts with; the cell itself when it starts with no letters."""
    match = STATUS_TOKEN_RE.match(status)
    return match.group(0).upper() if match else status[:20]


def rows_with_undeclared_status(matrix_path: Path, rows: list[MatrixRow]) -> list[str]:
    """Rule 4: every Status cell uses a declared value."""
    violations: list[str] = []
    for row in rows:
        if status_token(row.status) not in DECLARED_STATUSES:
            violations.append(f"{matrix_path}:{row.line}: undeclared Status value {row.status!r}")
    return violations


def check(matrix_path: Path, rows: list[MatrixRow], specs: set[str], tests: set[str]) -> list[str]:
    """Return one message per referential-integrity violation.

    The concatenation order IS the printed contract (Q-07): missing row → undefined ID →
    missing test → undeclared Status value. Reordering it would change the CI log.
    """
    return (
        ids_without_row(matrix_path, rows, specs)
        + rows_citing_undefined_ids(matrix_path, rows, specs)
        + rows_citing_missing_tests(matrix_path, rows, tests)
        + rows_with_undeclared_status(matrix_path, rows)
    )


def main() -> int:
    root = Path(".")
    matrix_path = root / "docs/verification/traceability.md"
    spec_dir = root / "docs/specs"
    test_dir = root / "tests"
    for path in (matrix_path, spec_dir, test_dir):
        if not path.exists():
            print(f"Traceability: FAIL (missing input: {path})")
            return 1

    rows = matrix_rows(matrix_path)
    specs = defined_ids(spec_dir)
    tests = test_names(test_dir)

    violations = check(matrix_path, rows, specs, tests)
    if violations:
        print(f"Traceability: FAIL ({len(violations)} violation(s))")
        for violation in violations:
            print(f"  {violation}")
        return 1

    print(f"Traceability: PASS ({len(rows)} matrix rows, {len(specs)} spec IDs, {len(tests)} test functions)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
