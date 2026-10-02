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


def matrix_rows(matrix_path: Path) -> list[MatrixRow]:
    """Parse the matrix tables, keeping only tables that have a Status column."""
    rows: list[MatrixRow] = []
    block: list[tuple[int, list[str]]] = []

    def flush(block: list[tuple[int, list[str]]]) -> None:
        if len(block) < MIN_TABLE_LINES:
            return
        header = [c.strip().lower() for c in block[0][1]]
        if "status" not in header:
            return
        status_idx = header.index("status")
        for line_no, cells in block[2:]:
            if len(cells) <= status_idx:
                continue
            text = " ".join(cells)
            rows.append(
                MatrixRow(
                    line=line_no,
                    ids=set(ID_RE.findall(text)),
                    tests={t for t in (BACKTICK_RE.findall(text)) if TEST_NAME_RE.match(t.strip())},
                    status=cells[status_idx],
                )
            )

    for line_no, line in enumerate(matrix_path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            block.append((line_no, [c.strip() for c in stripped.strip("|").split("|")]))
        else:
            flush(block)
            block = []
    flush(block)
    return rows


def check(matrix_path: Path, spec_dir: Path, test_dir: Path) -> list[str]:
    """Return one message per referential-integrity violation."""
    violations: list[str] = []
    rows = matrix_rows(matrix_path)
    referenced = {id_ for row in rows for id_ in row.ids}
    specs = defined_ids(spec_dir)
    tests = test_names(test_dir)

    # (1) every REQ/AC defined by a spec has at least one matrix row
    for id_ in sorted(specs):
        if REQ_OR_AC_RE.fullmatch(id_) and id_ not in referenced:
            violations.append(f"{id_} defined in docs/specs/ has no row in {matrix_path}")

    # (2) no matrix row references an ID that no spec defines
    for row in rows:
        for id_ in sorted(row.ids - specs):
            violations.append(f"{matrix_path}:{row.line}: row references undefined {id_}")

    # (3) every backticked test function in the matrix exists under tests/
    for row in rows:
        for name in sorted(row.tests - tests):
            violations.append(f"{matrix_path}:{row.line}: row references missing test {name}")

    # (4) every Status cell uses a declared value
    for row in rows:
        match = STATUS_TOKEN_RE.match(row.status)
        token = match.group(0).upper() if match else row.status[:20]
        if token not in DECLARED_STATUSES:
            violations.append(f"{matrix_path}:{row.line}: undeclared Status value {row.status!r}")

    return violations


def main() -> int:
    root = Path(".")
    matrix_path = root / "docs/verification/traceability.md"
    spec_dir = root / "docs/specs"
    test_dir = root / "tests"
    for path in (matrix_path, spec_dir, test_dir):
        if not path.exists():
            print(f"Traceability: FAIL (missing input: {path})")
            return 1

    violations = check(matrix_path, spec_dir, test_dir)
    if violations:
        print(f"Traceability: FAIL ({len(violations)} violation(s))")
        for violation in violations:
            print(f"  {violation}")
        return 1

    rows = matrix_rows(matrix_path)
    print(
        f"Traceability: PASS ({len(rows)} matrix rows, "
        f"{len(defined_ids(spec_dir))} spec IDs, "
        f"{len(test_names(test_dir))} test functions)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
