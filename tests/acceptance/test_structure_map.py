"""Acceptance tests for the structure-map change (spec: docs/specs/structure-map.md).

Every test cites the normative ID it witnesses (spec §11). T-001 creates the REQ-025 /
NFR-004 witnesses; T-002…T-007 append the remaining acceptance rows of §11 to this file.

Gate commands are run as `sys.executable -m <tool>` rather than the literal `uv run <tool>`
string: inside a pytest session `sys.executable` already *is* the uv-managed venv
interpreter, so the tool run is identical, while a nested `uv run` would re-sync and
rewrite `uv.lock` from inside a test (PROBLEMS.md P-42).
"""

from __future__ import annotations

import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_QUALITY_YML = _REPO_ROOT / ".github" / "workflows" / "quality.yml"
_VERIFY_SPEC = _REPO_ROOT / "scripts" / "verify_spec.py"
_JOB_INDENT = 2  # the indentation of a top-level job key in a GitHub Actions workflow

# AC-025 clause 3: the report `scripts/verify_spec.py docs/specs/template.md` produced
# BEFORE the REQ-025 fix — measured at the T-001 base and recorded in
# docs/verification/structure-map.md. The behaviour-preserving fix must not change it.
_VERIFY_SPEC_REPORT_BEFORE_FIX: tuple[str, ...] = (
    "Specification validation",
    "\u2500" * 25,
    "\u2713 REQ-001 has acceptance criteria",
    "\u2713 REQ-002 has acceptance criteria",
    "\u2713 REQ-003 has acceptance criteria",
    "\u2713 AC-001 has executable test",
    "\u2713 AC-002 has executable test",
    "\u2713 AC-003 has executable test",
    "\u2713 INV-001 has property test",
    "",
    "Traceability: PASS",
)

# NFR-004: the four quality gates the spec requires to be clean (mypy scripts/ is the
# widened one, REQ-025; the other three are already clean at the base commit).
_NFR_004_GATES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("mypy scripts/", ("-m", "mypy", "scripts/")),
    ("mypy src/", ("-m", "mypy", "src/")),
    ("ruff check .", ("-m", "ruff", "check", ".")),
    ("ruff format --check .", ("-m", "ruff", "format", "--check", ".")),
)


def _run(args: Sequence[str]) -> subprocess.CompletedProcess[str]:
    """Run a repository-level tool command from the repository root.

    `encoding="utf-8"` is explicit: `verify_spec.py` reconfigures stdout to UTF-8 (its report
    uses box-drawing and check-mark characters), and the default locale codec on Windows is
    cp1252, which would mojibake the report it is compared against.
    """
    return subprocess.run(
        [sys.executable, *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=_REPO_ROOT,
        check=False,
    )


def _output(proc: subprocess.CompletedProcess[str]) -> str:
    """Return the tool's diagnostic output (mypy writes to stdout, ruff to stderr on failure)."""
    return (proc.stdout or proc.stderr).strip()


def _opens_job_key(line: str) -> bool:
    """True when `line` opens a sibling top-level job in a workflow file (indent 2)."""
    at_job_level = line.startswith(" " * _JOB_INDENT) and not line.startswith(" " * (_JOB_INDENT + 1))
    return at_job_level and line.rstrip().endswith(":")


def _workflow_job_block(workflow_text: str, job: str) -> str:
    """Return the YAML text of one top-level job of a GitHub Actions workflow (empty if absent)."""
    lines = workflow_text.splitlines()
    starts = [index for index, line in enumerate(lines) if line.rstrip() == f"  {job}:"]
    if not starts:
        return ""
    stop = next(
        (index for index, line in enumerate(lines[starts[0] + 1 :], starts[0] + 1) if _opens_job_key(line)),
        len(lines),
    )
    return "\n".join(lines[starts[0] : stop])


def test_ac_025_mypy_covers_scripts() -> None:
    """AC-025 (REQ-025): the type-check job runs `uv run mypy scripts/`, that command exits 0,
    and `scripts/verify_spec.py` still exits 0 with the same report as before the fix."""
    failures: list[str] = []

    block = _workflow_job_block(_QUALITY_YML.read_text(encoding="utf-8"), "type-check")
    if "uv run mypy scripts/" not in block:
        failures.append("clause 1: the type-check job of quality.yml does not run 'uv run mypy scripts/'")

    mypy = _run(("-m", "mypy", "scripts/"))
    if mypy.returncode != 0:
        failures.append(f"clause 2: mypy over scripts/ exits {mypy.returncode}: {_output(mypy)}")

    report = _run((str(_VERIFY_SPEC), "docs/specs/template.md"))
    if report.returncode != 0 or tuple(report.stdout.splitlines()) != _VERIFY_SPEC_REPORT_BEFORE_FIX:
        failures.append(
            f"clause 3: verify_spec.py no longer reports the pre-fix result: "
            f"exit {report.returncode}, report {report.stdout.splitlines()!r}"
        )

    assert not failures, "\n".join(failures)


def test_nfr_004_mypy_and_ruff_clean() -> None:
    """NFR-004 (REQ-025): `mypy scripts/`, `mypy src/`, `ruff check .` and
    `ruff format --check .` are all clean on the change branch."""
    dirty: list[str] = []
    for label, args in _NFR_004_GATES:
        proc = _run(args)
        if proc.returncode != 0:
            dirty.append(f"{label}: exit {proc.returncode}: {_output(proc)}")

    assert not dirty, "\n".join(dirty)
