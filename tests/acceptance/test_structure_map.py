"""Acceptance tests for the structure-map change (spec: docs/specs/structure-map.md).

Every test cites the normative ID it witnesses (spec §11). T-001 creates the REQ-025 /
NFR-004 witnesses; T-002…T-007 append the remaining acceptance rows of §11 to this file.

Gate commands are run as `sys.executable -m <tool>` rather than the literal `uv run <tool>`
string: inside a pytest session `sys.executable` already *is* the uv-managed venv
interpreter, so the tool run is identical, while a nested `uv run` would re-sync and
rewrite `uv.lock` from inside a test (PROBLEMS.md P-42).
"""

from __future__ import annotations

import ast
import getpass
import platform
import re
import subprocess
import sys
import time
from collections.abc import Mapping, Sequence
from pathlib import Path

import pytest

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


def _run(args: Sequence[str], cwd: Path = _REPO_ROOT) -> subprocess.CompletedProcess[str]:
    """Run a repository-level tool command (`sys.executable` + args) from `cwd`.

    `encoding="utf-8"` is explicit: `verify_spec.py` reconfigures stdout to UTF-8 (its report
    uses box-drawing and check-mark characters), and the default locale codec on Windows is
    cp1252, which would mojibake the report it is compared against.
    """
    return subprocess.run(
        [sys.executable, *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=cwd,
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


# --- T-002: the generator harness (REQ-001/002/003/004/006/007/008) --------------------------

_GENERATOR = _REPO_ROOT / "scripts" / "make_map.py"
_GENERATED_BY = "_Generated by `scripts/make_map.py`. Do not edit by hand._"
_CLI_OPTIONS: tuple[str, ...] = ("--root", "--out", "--include-private", "--max-depth", "--check", "-h", "--help")
_READ_METHODS = frozenset({"read_text", "read_bytes"})
_EXIT_USAGE = 2  # REQ-004: usage error (argparse or a --max-depth < 1 rejection)

# AC-008 / INV-003: content that must never appear in a generated map.
_FORBIDDEN: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("a timestamp", re.compile(r"\d{4}-\d{2}-\d{2}|\b\d{1,2}:\d{2}:\d{2}\b")),
    ("a drive letter or UNC path", re.compile(r"[A-Za-z]:[\\/]")),
    ("a Windows path separator", re.compile(r"\\")),
    ("an absolute POSIX path", re.compile(r"(^|\s)/[A-Za-z0-9_.]")),
    ("a timing line", re.compile(r"generated in", re.IGNORECASE)),
)

# NFR-001: the 2 s budget is asserted only on a host that is not much slower than the reference
# host (the spec's "skipped on slow CI" rule). The calibration is a pure-CPU micro-benchmark
# measured at import: parse a fixed 50-function source 40 times, best of 3. Reference value
# measured at S3.1 on this host (CPython 3.14.5, Windows): 0.0114 s — see
# docs/verification/structure-map.md. A host over 6x slower on it skips the NFR-001 test.
_CALIBRATION_SOURCE = "\n".join(f"def f{i}(a: int) -> int:\n    return a + {i}" for i in range(50))
_CALIBRATION_ROUNDS = 40
_CALIBRATION_REFERENCE_SECONDS = 0.011
_NFR_001_BUDGET_SECONDS = 2.0


def _calibrate() -> float:
    """Best-of-3 wall time for the fixed parse micro-benchmark (the NFR-001 skip guard)."""
    best = float("inf")
    for _ in range(3):
        start = time.perf_counter()
        for _ in range(_CALIBRATION_ROUNDS):
            ast.parse(_CALIBRATION_SOURCE)
        best = min(best, time.perf_counter() - start)
    return best


_CALIBRATION_SECONDS = _calibrate()
_NFR_001_SLOW_HOST = _CALIBRATION_SECONDS > 6 * _CALIBRATION_REFERENCE_SECONDS


def _mode_is_write(node: ast.Call) -> bool:
    """True when an `open(...)` call's literal mode writes, so it is not a content read."""
    mode = node.args[1] if len(node.args) > 1 else next((kw.value for kw in node.keywords if kw.arg == "mode"), None)
    return isinstance(mode, ast.Constant) and isinstance(mode.value, str) and any(c in mode.value for c in "wax")


def _read_call_sites(tree: ast.Module) -> list[str]:
    """Call sites that read a file's content.

    REQ-001 requires exactly one (line count and AST from the same read).
    `ponytail:` a static witness of the read *site*, not a runtime count of reads; the upgrade
    path is an `open` audit hook in a wrapper process.
    """
    sites: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Attribute) and func.attr in _READ_METHODS:
            sites.append(func.attr)
        elif isinstance(func, ast.Name) and func.id == "open" and not _mode_is_write(node):
            sites.append("open")
    return sites


def _non_stdlib_imports(tree: ast.Module) -> list[str]:
    """Top-level imported packages that are not standard library (REQ-001's dependency budget)."""
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            names.add(node.module.split(".")[0])
    return sorted(name for name in names if name not in sys.stdlib_module_names)


def _git(args: Sequence[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    """Run a git command in `cwd` (fixtures build their own throwaway repos in tmp_path)."""
    return subprocess.run(["git", *args], capture_output=True, text=True, encoding="utf-8", cwd=cwd, check=False)


def _git_tree(root: Path, files: Mapping[str, str]) -> Path:
    """A throwaway git tree: `git init`, write `files`, stage them.

    Staging is enough — `git ls-files --cached --others --exclude-standard` (REQ-003) lists staged
    and untracked files without a commit, so no committer identity is needed. Fixture paths live
    under `src/` (a code dir, REQ-009) so the map renders them entry by entry.
    """
    for name, text in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    for args in (["init", "-q", "-b", "main"], ["add", "-A"]):
        if _git(args, root).returncode != 0:
            pytest.fail(f"git {' '.join(args)} failed in {root}")
    return root


def _map_text(out: Path, proc: subprocess.CompletedProcess[str]) -> str:
    """The generated map's text, or a test failure naming the run that produced no file."""
    if not out.is_file():
        pytest.fail(f"no map file at {out} (exit {proc.returncode}): {proc.stdout!r} {proc.stderr!r}")
    return out.read_text(encoding="utf-8")


def _help_segment(help_text: str, option: str) -> str:
    """The `--help` text belonging to `option`'s own option line (up to the next option line)."""
    match = re.search(rf"^\s*{re.escape(option)}\b.*?(?=^\s*-\w|\Z)", help_text, re.DOTALL | re.MULTILINE)
    return match.group(0) if match else ""


def test_ac_001_stdlib_only_and_single_read(tmp_path: Path) -> None:
    """AC-001 (REQ-001): the generator runs clean, imports only the standard library, reads each
    source file at one call site, and `deptry .` reports no new dependency."""
    if not _GENERATOR.is_file():
        pytest.fail(f"{_GENERATOR} does not exist — T-002 Phase 4 has not implemented the generator")
    out = tmp_path / "STRUCTURE.md"
    run = _run([str(_GENERATOR), "--out", str(out)])
    tree = ast.parse(_GENERATOR.read_text(encoding="utf-8"))
    deptry = _run(("-m", "deptry", "."))

    failures: list[str] = []
    if run.returncode != 0:
        failures.append(f"clause 1: generate run exits {run.returncode}: {_output(run)}")
    if non_stdlib := _non_stdlib_imports(tree):
        failures.append(f"clause 2: non-stdlib imports {non_stdlib}")
    if (sites := _read_call_sites(tree)) and len(sites) != 1:
        failures.append(f"clause 3: {len(sites)} file-read call sites {sites}, expected exactly one")
    if deptry.returncode != 0:
        failures.append(f"clause 4: deptry exits {deptry.returncode}: {_output(deptry)}")
    assert not failures, "\n".join(failures)


def test_ac_002_cli_options_and_defaults(tmp_path: Path) -> None:
    """AC-002 (REQ-002): --help lists the six options with their defaults, --out resolves against
    the current working directory, --root defaults to the script's repository root, and an
    unknown option is an argparse usage error (exit 2)."""
    cwd = tmp_path / "cwd"
    cwd.mkdir()
    tree = _git_tree(tmp_path / "tree", {"src/mod.py": "x = 1\n"})

    help_proc = _run([str(_GENERATOR), "--help"])
    here = _run([str(_GENERATOR), "--root", str(tree), "--out", "here.md"], cwd=cwd)
    default_root = _run([str(_GENERATOR), "--out", str(tmp_path / "default.md")], cwd=cwd)
    unknown = _run([str(_GENERATOR), "--nope"])

    failures: list[str] = []
    if help_proc.returncode != 0:
        failures.append(f"clause 1: --help exits {help_proc.returncode}: {_output(help_proc)}")
    if missing := [option for option in _CLI_OPTIONS if option not in help_proc.stdout]:
        failures.append(f"clause 1: --help does not list {missing}")
    if "STRUCTURE.md" not in _help_segment(help_proc.stdout, "--out"):
        failures.append("clause 1: --out does not state its STRUCTURE.md default")
    if "4" not in _help_segment(help_proc.stdout, "--max-depth"):
        failures.append("clause 1: --max-depth does not state its 4 default")
    if not (cwd / "here.md").is_file():
        failures.append(f"clause 2: --out here.md was not written against the cwd: {here.returncode} {_output(here)}")
    if (tree / "here.md").exists():
        failures.append("clause 2: --out resolved against --root, not against the current working directory")
    if "scripts/check_traceability.py" not in _map_text(tmp_path / "default.md", default_root):
        failures.append("clause 3: with no --root the map does not describe the script's repository root")
    if unknown.returncode != _EXIT_USAGE or "usage" not in unknown.stderr.lower():
        failures.append(f"clause 4: unknown option exits {unknown.returncode} with stderr {unknown.stderr!r}")
    assert not failures, "\n".join(failures)


def test_ac_003_file_set_includes_untracked_drops_deleted(tmp_path: Path) -> None:
    """AC-003 (REQ-003): a new .py file that is not `git add`ed appears in the map, and a tracked
    file deleted from the working tree (still in the index) is omitted."""
    root = _git_tree(tmp_path / "tree", {"src/kept.py": "x = 1\n", "src/gone.py": "y = 2\n"})
    (root / "src" / "untracked.py").write_text("z = 3\n", encoding="utf-8")
    (root / "src" / "gone.py").unlink()
    out = tmp_path / "STRUCTURE.md"

    proc = _run([str(_GENERATOR), "--root", str(root), "--out", str(out)])
    text = _map_text(out, proc)

    failures: list[str] = []
    if proc.returncode != 0:
        failures.append(f"clause 1: exit {proc.returncode}: {_output(proc)}")
    if "src/untracked.py" not in text:
        failures.append("clause 2: the untracked src/untracked.py is not in the map")
    if "src/gone.py" in text:
        failures.append("clause 3: the deleted-but-tracked src/gone.py is still in the map")
    if "src/kept.py" not in text:
        failures.append("clause 3: the untouched src/kept.py is missing from the map")
    assert not failures, "\n".join(failures)


def test_ac_008_document_shape(tmp_path: Path) -> None:
    """AC-008 (REQ-008): the document is the title, one blank line, the generated-by line, then
    `## Directory tree` and `## Packages` in that order and nothing else, with no timestamp,
    absolute path, drive letter, host name or user name anywhere in it."""
    out = tmp_path / "STRUCTURE.md"
    proc = _run([str(_GENERATOR), "--out", str(out)])
    text = _map_text(out, proc)
    lines = text.splitlines()

    failures: list[str] = []
    if lines[:1] != ["# Repository structure"]:
        failures.append(f"clause 1: first line {lines[:1]!r}")
    if lines[1:2] != [""]:
        failures.append(f"clause 2: line 2 is {lines[1:2]!r}, expected one blank line")
    if lines[2:3] != [_GENERATED_BY]:
        failures.append(f"clause 2: line 3 is {lines[2:3]!r}, expected the generated-by line")
    if [line for line in lines if line.startswith("## ")] != ["## Directory tree", "## Packages"]:
        failures.append(f"clause 3: sections are {[line for line in lines if line.startswith('## ')]!r}")
    for label, pattern in _FORBIDDEN:
        if hit := pattern.search(text):
            failures.append(f"clause 4: the map contains {label}: {hit.group(0)!r}")
    for identity in (platform.node(), getpass.getuser()):
        if identity and re.search(rf"\b{re.escape(identity)}\b", text):
            failures.append(f"clause 4: the map contains the host/user name {identity!r}")
    assert not failures, "\n".join(failures)


def test_edge_006_out_parent_directory_created(tmp_path: Path) -> None:
    """EDGE-006 (REQ-002): a missing --out parent directory is created before writing."""
    root = _git_tree(tmp_path / "tree", {"src/mod.py": "x = 1\n"})
    out = tmp_path / "deep" / "nested" / "STRUCTURE.md"

    proc = _run([str(_GENERATOR), "--root", str(root), "--out", str(out)])

    failures: list[str] = []
    if proc.returncode != 0:
        failures.append(f"clause 1: exit {proc.returncode}: {_output(proc)}")
    if not out.is_file():
        failures.append(f"clause 2: {out} was not written (its parents did not exist)")
    elif not out.read_text(encoding="utf-8").strip():
        failures.append("clause 2: the written map is empty")
    assert not failures, "\n".join(failures)


def test_edge_007_non_git_root_falls_back_to_ignore_list(tmp_path: Path) -> None:
    """EDGE-007 (REQ-003): a --root that is not a git repository uses the built-in ignore list,
    prints exactly one limitation note to stderr, does not parse .gitignore, and still succeeds."""
    root = tmp_path / "plain"
    for name, text in {
        "src/mod.py": "x = 1\n",
        "src/ignored/hidden.py": "y = 2\n",
        ".venv/lib/mod.py": "z = 3\n",
        "__pycache__/mod.py": "w = 4\n",
        "data/mod.py": "v = 5\n",
    }.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    (root / ".gitignore").write_text("src/ignored/\n", encoding="utf-8")
    out = tmp_path / "STRUCTURE.md"

    proc = _run([str(_GENERATOR), "--root", str(root), "--out", str(out)])
    text = _map_text(out, proc)
    notes = [line for line in proc.stderr.splitlines() if line.strip()]

    failures: list[str] = []
    if proc.returncode != 0:
        failures.append(f"clause 1: exit {proc.returncode}: {_output(proc)}")
    if len(notes) != 1 or "git" not in notes[0].lower():
        failures.append(f"clause 2: stderr is {notes!r}, expected exactly one limitation note naming git")
    if "src/mod.py" not in text:
        failures.append("clause 3: src/mod.py is missing from the map of a non-git root")
    for ignored in (".venv", "__pycache__", "data"):
        if ignored in text:
            failures.append(f"clause 4: the ignored directory {ignored} appears in the map")
    if "src/ignored/hidden.py" not in text:
        failures.append("clause 5: .gitignore was parsed — src/ignored/hidden.py is missing from the map")
    assert not failures, "\n".join(failures)


def test_edge_008_deleted_tracked_file_absent(tmp_path: Path) -> None:
    """EDGE-008 (REQ-003): a tracked file deleted from the working tree but still in the index is
    absent from the map, and the run is not an error (exit 0, no report about it)."""
    root = _git_tree(tmp_path / "tree", {"src/kept.py": "x = 1\n", "src/gone.py": "y = 2\n"})
    (root / "src" / "gone.py").unlink()
    out = tmp_path / "STRUCTURE.md"

    proc = _run([str(_GENERATOR), "--root", str(root), "--out", str(out)])
    text = _map_text(out, proc)

    failures: list[str] = []
    if proc.returncode != 0:
        failures.append(f"clause 1: exit {proc.returncode}: {_output(proc)}")
    if "src/gone.py" in text:
        failures.append("clause 2: the deleted src/gone.py is in the map")
    if "gone.py" in proc.stderr:
        failures.append(f"clause 3: the deleted file is reported on stderr: {proc.stderr!r}")
    if "src/kept.py" not in text:
        failures.append("clause 2: src/kept.py is missing from the map")
    assert not failures, "\n".join(failures)


def test_edge_014_max_depth_below_one_is_usage_error(tmp_path: Path) -> None:
    """EDGE-014 (REQ-002): --max-depth 0 or a negative value is a usage error (exit 2) and no
    output file is written."""
    root = _git_tree(tmp_path / "tree", {"src/mod.py": "x = 1\n"})
    failures: list[str] = []

    for value in ("0", "-3"):
        out = tmp_path / f"out_{value}.md"
        proc = _run([str(_GENERATOR), "--root", str(root), "--out", str(out), "--max-depth", value])
        if proc.returncode != _EXIT_USAGE:
            failures.append(f"--max-depth {value}: exit {proc.returncode}, expected 2 (stderr {proc.stderr!r})")
        if "usage" not in proc.stderr.lower():
            failures.append(f"--max-depth {value}: no argparse usage error on stderr: {proc.stderr!r}")
        if out.exists():
            failures.append(f"--max-depth {value}: an output file was written")

    assert not failures, "\n".join(failures)


@pytest.mark.skipif(
    _NFR_001_SLOW_HOST,
    reason=f"calibration {_CALIBRATION_SECONDS:.3f}s is over 6x the reference {_CALIBRATION_REFERENCE_SECONDS}s",
)
def test_nfr_001_full_run_under_two_seconds(tmp_path: Path) -> None:
    """NFR-001 (REQ-001): a full generate run over this repository completes in under 2 s."""
    start = time.perf_counter()
    proc = _run([str(_GENERATOR), "--out", str(tmp_path / "STRUCTURE.md")])
    elapsed = time.perf_counter() - start

    assert proc.returncode == 0, f"generate run exits {proc.returncode}: {_output(proc)}"
    assert elapsed < _NFR_001_BUDGET_SECONDS, (
        f"NFR-001: a full generate run took {elapsed:.2f}s (budget {_NFR_001_BUDGET_SECONDS}s; "
        f"calibration {_CALIBRATION_SECONDS:.3f}s vs reference {_CALIBRATION_REFERENCE_SECONDS}s)"
    )


def test_nfr_003_deptry_clean() -> None:
    """NFR-003 (REQ-001): `deptry .` reports no unused, missing or misplaced dependency — the
    generator is stdlib-only and adds none."""
    proc = _run(("-m", "deptry", "."))
    assert proc.returncode == 0, f"deptry exits {proc.returncode}: {_output(proc)}"


# --- T-003: the Directory tree section, Packages scope, headers, path form ---------------------
# (REQ-009/010/011/012/020, AC-009/010/011/012, EDGE-015)

_CODE_DIRS: tuple[str, ...] = ("src", "tests", "scripts", "migrations")
_PACKAGES_DIRS: tuple[str, ...] = ("src", "scripts", "migrations")
_INDENT_WIDTH = 2  # REQ-009: the tree is indented two spaces per level
_EXPECTED_PACKAGE_COUNT = 15  # the fixture's REQ-011 scope, counted by hand as a cross-check

_SETTINGS_INIT = (
    '"""The settings package."""\n'
    "\n"
    "from .models import Model\n"
    "from .registry import Registry\n"
    "\n"
    '__all__ = ["Zeta", "Alpha"]\n'
)

# One fixture tree for the whole T-003 acceptance set: top-level files, the four code dirs with a
# 4-segment-deep package chain (so --max-depth 2 prunes something), a labelled non-code dir, an
# unlabelled one (EDGE-015), and a .py outside every code dir (REQ-010 / INV-002).
_TREE_FILES: dict[str, str] = {
    "README.md": "# Demo\n",
    "pyproject.toml": '[project]\nname = "demo"\n',
    "src/top.py": '"""A top-level module."""\n',
    "src/empty.py": "",
    "src/backend/__init__.py": '"""The backend package."""\n',
    "src/backend/utils.py": '"""Utilities."""\n',
    "src/backend/settings/__init__.py": _SETTINGS_INIT,
    "src/backend/settings/models.py": '"""The settings models."""\n',
    "src/backend/settings/registry.py": '"""The settings registry."""\n',
    "src/backend/settings/no_doc.py": "VALUE = 1\nOTHER = 2\n",
    "src/nopub/__init__.py": '"""A package with neither __all__ nor public imports."""\n',
    "scripts/build.py": '"""The build tool."""\n',
    "migrations/env.py": '"""The migration environment."""\n',
    "migrations/0001_initial.py": '"""Initial migration."""\n',
    "tests/conftest.py": '"""Shared fixtures."""\n',
    "tests/settings_test_helpers.py": '"""Settings test helpers."""\n',
    "tests/unit/conftest.py": '"""Unit fixtures."""\n',
    "tests/unit/test_deep_behaviour.py": '"""Out of Packages scope."""\n',
    "tests/plain_helpers.py": '"""Out of Packages scope."""\n',
    "tests/README.md": "# Tests\n",  # a non-.py entry under a code dir: REQ-009 renders it too
    "docs/a.md": "# A\n",
    "docs/b.md": "# B\n",
    "docs/sub/c.md": "# C\n",
    "notes/one.md": "# One\n",
    "notes/two.md": "# Two\n",
    "notes/deep/three.md": "# Three\n",
    ".github/workflows/ci.yml": "name: ci\n",
    ".github/hooks/post_edit.py": '"""A hook outside the code dirs."""\n',
}

# REQ-009 clause 3: the built-in role-label table entries the fixture exercises.
_COUNT_LINES: tuple[tuple[str, int, str], ...] = (
    ("docs/", 3, "(process record)"),
    (".github/", 2, "(CI and tooling)"),
)

# The code-dir directories (not only files) REQ-009 clause 2 renders one line for.
_CODE_DIR_DIRS: tuple[str, ...] = ("src/backend/", "src/backend/settings/", "tests/unit/")

_ENTRY_PATH = re.compile(r"[\w./-]+/?")  # a bare tree entry line: a path, dirs with a trailing /
_PRUNE_MARKER = re.compile(r"\(\+\d+ (?:dirs|files)(?:, \d+ (?:dirs|files))? not shown\)")
_COMBINED_MARKER = re.compile(r"\(\+\d+ dirs, \d+ files not shown\)")


def _file_name(path: str) -> str:
    """The last segment of a `/`-separated fixture path (the file name, whatever its depth)."""
    return path.rsplit("/", 1)[-1]


def _in_packages_scope(path: str) -> bool:
    """REQ-011: every module under src/, scripts/ and migrations/, plus tests/ conftest/test-helpers.

    The tests/ rule matches the *file name* at any depth, so `tests/unit/conftest.py` is in scope.
    """
    top = path.split("/", 1)[0]
    name = _file_name(path)
    return path.endswith(".py") and (
        top in _PACKAGES_DIRS or name == "conftest.py" or name.endswith("_test_helpers.py")
    )


_PACKAGES_SCOPE: frozenset[str] = frozenset(p for p in _TREE_FILES if _in_packages_scope(p))

# REQ-009 clause 2 renders one line per tracked entry under a code dir — of ANY file type (this
# repository has 9 non-.py files under code dirs), not one line per parsed module.
_CODE_DIR_ENTRIES: frozenset[str] = frozenset(p for p in _TREE_FILES if p.split("/", 1)[0] in _CODE_DIRS)

# REQ-012: one group header per containing directory of a Packages-scope module, never one per module.
_GROUP_DIRS: frozenset[str] = frozenset(f"{p.rsplit('/', 1)[0]}/" for p in _PACKAGES_SCOPE)


def _tree_map(base: Path, *extra: str) -> str:
    """Render `_TREE_FILES` as a throwaway git tree and return the generated map text."""
    root = _git_tree(base / "tree", _TREE_FILES)
    out = base / "map.md"
    proc = _run([str(_GENERATOR), "--root", str(root), "--out", str(out), *extra], cwd=root)
    return _map_text(out, proc)


def _section_lines(map_text: str, heading: str) -> list[str]:
    """The non-blank lines of one `## ` section, up to the next `## ` heading."""
    lines: list[str] = []
    inside = False
    for line in map_text.splitlines():
        if line.startswith("## "):
            inside = line == heading
        elif inside and line.strip():
            lines.append(line)
    return lines


def _tree_entries(map_text: str) -> list[tuple[int, str]]:
    """(indent, text) for every non-blank Directory tree line."""
    return [(len(line) - len(line.lstrip(" ")), line.strip()) for line in _section_lines(map_text, "## Directory tree")]


def _tree_paths(map_text: str) -> set[str]:
    """The paths named by tree entry lines; count lines and prune markers are not entry lines."""
    return {text.rstrip("/") for _, text in _tree_entries(map_text) if _ENTRY_PATH.fullmatch(text)}


def _module_paths(map_text: str) -> set[str]:
    """The module paths named by the Packages section's `####` headers (REQ-013's header form)."""
    headers = (re.match(r"#### (\S+) \(\d+ lines\)", line) for line in _section_lines(map_text, "## Packages"))
    return {match.group(1) for match in headers if match}


def _prune_marker_in_branch(map_text: str, path: str) -> str:
    """The REQ-010 `(+N … not shown)` marker rendered inside the branch rooted at `path`, else ''.

    The scan stops at the branch's next sibling entry, so a marker belonging to another top-level
    branch is never attributed to this one; the marker itself is accepted at either indent.
    """
    entries = _tree_entries(map_text)
    for index, (indent, text) in enumerate(entries):
        if text.rstrip("/") != path:
            continue
        for deeper_indent, deeper in entries[index + 1 :]:
            if _PRUNE_MARKER.fullmatch(deeper):
                return deeper
            if deeper_indent <= indent and _ENTRY_PATH.fullmatch(deeper):
                break
    return ""


def _group_body(map_text: str, needle: str) -> list[str]:
    """The lines of the group whose `### ` header contains `needle` (up to the next group header)."""
    lines = _section_lines(map_text, "## Packages")
    start = next((i for i, line in enumerate(lines) if line.startswith("### ") and needle in line), None)
    if start is None:
        return []
    body: list[str] = []
    for line in lines[start + 1 :]:
        if line.startswith("### "):
            break
        body.append(line.strip())
    return body


def _code_dir_entry_failures(entries: list[tuple[int, str]]) -> list[str]:
    """REQ-009 clause 2: every entry under a code dir — of **any** file type — gets its own tree
    line, indented two spaces per path segment, and every code dir gets a directory line."""
    failures: list[str] = []
    for path in sorted(_CODE_DIR_ENTRIES):
        expected_indent = _INDENT_WIDTH * (len(Path(path).parts) - 1)
        found = [indent for indent, text in entries if text.rstrip("/") == path]
        if not found:
            failures.append(f"clause 2: no tree line renders the code-dir entry {path}")
        elif found[0] != expected_indent:
            failures.append(f"clause 2: {path} is indented {found[0]}, expected {expected_indent}")
    for directory in (*_CODE_DIRS, *_CODE_DIR_DIRS):
        if not any(text.rstrip("/") == directory.rstrip("/") for _, text in entries):
            failures.append(f"clause 2: no tree line renders the code dir {directory}")
    return failures


def test_ac_009_tree_code_dirs_full_other_dirs_counted(tmp_path: Path) -> None:
    """AC-009 (REQ-009): the tree lists the top-level files by name, renders src/, tests/, scripts/
    and migrations/ entry by entry (one line per directory and per entry, sorted, indented two
    spaces per level), and renders every other top-level directory as one count line carrying its
    role label."""
    map_text = _tree_map(tmp_path)
    entries = _tree_entries(map_text)
    failures: list[str] = []

    top_files = [text for _, text in entries if text in {"README.md", "pyproject.toml"}]
    if top_files != ["README.md", "pyproject.toml"]:
        failures.append(f"clause 1: the top-level files are not listed by name, sorted: {top_files!r}")
    file_rows = [i for i, (_, text) in enumerate(entries) if text in {"README.md", "pyproject.toml"}]
    dir_rows = [i for i, (_, text) in enumerate(entries) if text.split("/")[0] in _CODE_DIRS]
    if file_rows and dir_rows and max(file_rows) > min(dir_rows):
        failures.append("clause 1: the top-level files must be listed before the code dirs (REQ-009 order)")

    failures += _code_dir_entry_failures(entries)

    under_src = [text for indent, text in entries if indent == _INDENT_WIDTH and text.startswith("src/")]
    src_dirs = [text for text in under_src if text.endswith("/")]
    src_files = [text for text in under_src if not text.endswith("/")]
    if src_dirs != sorted(src_dirs) or src_files != sorted(src_files):
        failures.append(f"clause 2: the entries under src/ are not sorted (dirs {src_dirs!r}, files {src_files!r})")

    for directory, count, label in _COUNT_LINES:
        lines = [text for indent, text in entries if indent == 0 and text.startswith(directory)]
        if len(lines) != 1:
            failures.append(f"clause 3: {len(lines)} tree lines for {directory}, expected one count line: {lines!r}")
            continue
        if f"{count} files" not in lines[0]:
            failures.append(f"clause 3: {lines[0]!r} does not count all {count} files under {directory}")
        if label not in lines[0]:
            failures.append(f"clause 3: {lines[0]!r} carries no {label!r} role label")
    for path in (".github/hooks/post_edit.py", "docs/sub/c.md", "notes/deep/three.md"):
        if any(text.startswith(path) for _, text in entries):
            failures.append(f"clause 3: {path} is rendered entry by entry in a count-only directory")
    assert not failures, "\n".join(failures)


def test_ac_010_max_depth_prunes_tree_only(tmp_path: Path) -> None:
    """AC-010 (REQ-010): --max-depth 2 renders no entry under src/backend/ and marks that branch with
    a `(+N … not shown)` line, while the Packages section still lists every src/ module — the same
    modules as the default --max-depth 4."""
    pruned = _tree_map(tmp_path / "pruned", "--max-depth", "2")
    full = _tree_map(tmp_path / "full")
    failures: list[str] = []

    paths = _tree_paths(pruned)
    deep = sorted(p for p in paths if p.startswith("src/backend/"))
    if deep:
        failures.append(f"clause 1: --max-depth 2 still renders {deep}")
    if "src/backend" not in paths:
        failures.append(f"clause 1: src/backend/ itself is not rendered at --max-depth 2: {sorted(paths)!r}")
    marker = _prune_marker_in_branch(pruned, "src/backend")
    if not marker:
        failures.append(f"clause 2: no `(+N … not shown)` marker in the src/backend/ branch: {sorted(paths)!r}")
    elif not _COMBINED_MARKER.fullmatch(marker):
        failures.append(f"clause 2: {marker!r} is not the combined `(+N dirs, M files not shown)` form")
    if hidden := _prune_marker_in_branch(pruned, "scripts"):
        failures.append(f"clause 2: {hidden!r} prunes the scripts/ branch, whose every entry is at depth 2")

    pruned_modules, full_modules = _module_paths(pruned), _module_paths(full)
    if pruned_modules != full_modules:
        failures.append(f"clause 3: Packages differs at --max-depth 2 vs 4: {sorted(pruned_modules ^ full_modules)}")
    src_modules = {p for p in pruned_modules if p.startswith("src/")}
    expected_src = {p for p in _TREE_FILES if p.startswith("src/")}
    if src_modules != expected_src:
        failures.append(f"clause 3: the Packages section misses/added {sorted(src_modules ^ expected_src)} under src/")
    assert not failures, "\n".join(failures)


def test_ac_011_packages_scope(tmp_path: Path) -> None:
    """AC-011 (REQ-011): the Packages section has an entry for every .py under src/, scripts/ and
    migrations/, and for each tests/conftest.py and *_test_helpers.py — and for no other tests/
    module."""
    map_text = _tree_map(tmp_path)
    listed = _module_paths(map_text)
    failures: list[str] = []
    if missing := sorted(_PACKAGES_SCOPE - listed):
        failures.append(f"clause 1/2: no Packages entry for {missing}")
    if extra := sorted(listed - _PACKAGES_SCOPE):
        failures.append(f"clause 3: Packages entry for an out-of-scope module: {extra}")
    if len(listed) != _EXPECTED_PACKAGE_COUNT:
        failures.append(f"the Packages section lists {len(listed)} modules, expected {_EXPECTED_PACKAGE_COUNT}")
    assert not failures, "\n".join(failures)


def test_ac_012_package_header_and_exports(tmp_path: Path) -> None:
    """AC-012 (REQ-012): the backend.settings package has exactly one group header showing
    `backend.settings` and src/backend/settings/, one exports: line listing its __init__.py __all__
    names sorted, and no per-module import line."""
    map_text = _tree_map(tmp_path)
    lines = _section_lines(map_text, "## Packages")
    headers = [line for line in lines if line.startswith("### ")]
    group = [line for line in headers if "backend.settings" in line or "backend/settings" in line]
    failures: list[str] = []
    if len(group) != 1:
        failures.append(f"clause 1: {len(group)} group headers mention backend.settings: {group!r}")
        assert not failures, "\n".join(failures)
    header = group[0]
    if "`backend.settings`" not in header or "src/backend/settings/" not in header:
        failures.append(f"clause 1: {header!r} shows neither the import name nor the directory path")

    body = _group_body(map_text, "src/backend/settings/")
    exports = [line for line in body if "exports:" in line]
    if len(exports) != 1:
        failures.append(f"clause 2: {len(exports)} exports: lines in the group: {body!r}")
    else:
        if "Alpha" not in exports[0] or "Zeta" not in exports[0]:
            failures.append(f"clause 2: {exports[0]!r} does not list the __all__ names")
        elif exports[0].index("Alpha") > exports[0].index("Zeta"):
            failures.append(f"clause 2: {exports[0]!r} is not sorted")
        for imported in ("Registry", "Model"):
            if imported in exports[0]:
                failures.append(f"clause 2: {exports[0]!r} lists the imported name {imported}, not __all__")
    header_paths = [match.group(1) for line in headers if (match := re.search(r"(\S+/)$", line))]
    if len(header_paths) != len(headers):
        failures.append(f"clause 3: a group header names no directory path: {headers!r}")
    if len(header_paths) != len(set(header_paths)):
        failures.append(f"clause 3: duplicate group headers: {header_paths!r}")
    if set(header_paths) != _GROUP_DIRS:
        failures.append(
            f"clause 3: {sorted(set(header_paths))!r} are not one header per containing directory {_GROUP_DIRS!r}"
        )
    assert not failures, "\n".join(failures)


def test_edge_015_unlabelled_dir_counted_without_label(tmp_path: Path) -> None:
    """EDGE-015 (REQ-009): a top-level directory with no entry in the role-label table still gets one
    count line — `<name>/ — <N> files` with no label — and its files are still counted."""
    map_text = _tree_map(tmp_path)
    entries = _tree_entries(map_text)
    lines = [text for indent, text in entries if indent == 0 and text.startswith("notes/")]
    failures: list[str] = []
    if len(lines) != 1:
        failures.append(f"clause 1: {len(lines)} tree lines for notes/, expected one count line: {lines!r}")
    else:
        if "3 files" not in lines[0]:
            failures.append(f"clause 2: {lines[0]!r} does not count all 3 files under notes/")
        if "(" in lines[0]:
            failures.append(f"clause 3: {lines[0]!r} carries a role label")
    if any(text.startswith("notes/deep/") for _, text in entries):
        failures.append("clause 2: notes/deep/ is rendered entry by entry although notes/ is not a code dir")
    assert not failures, "\n".join(failures)


# --- T-005: the exit-code contract, --check semantics, determinism, hook-clean output -----------
# (REQ-004/005/019, AC-004/005/019, EDGE-009/010/016)

_EXIT_STALE = 1  # REQ-004: --check found a stale map
_EXIT_MISSING = 3  # REQ-004: --check found no --out file
_EXIT_UNPARSEABLE = 4  # REQ-004: a source file could not be read or parsed
_RUN_COMMAND = "uv run python scripts/make_map.py"  # the pinned command text of both messages
_PRE_COMMIT = _REPO_ROOT / ".pre-commit-config.yaml"


def _generate(root: Path, out_arg: str, *extra: str) -> subprocess.CompletedProcess[str]:
    """Generate mode for `root`: run from `root` so `out_arg` is the path **as given** (REQ-005)."""
    return _run([str(_GENERATOR), "--root", str(root), "--out", out_arg, *extra], cwd=root)


def _check(root: Path, out_arg: str, *extra: str) -> subprocess.CompletedProcess[str]:
    """`--check` mode for `root`, with `out_arg` given exactly as the message must name it."""
    return _run([str(_GENERATOR), "--root", str(root), "--out", out_arg, "--check", *extra], cwd=root)


def _generate_fixed_point(root: Path, out_arg: str, *extra: str) -> bytes:
    """Generate twice and return the map bytes: the fixed point at which the map file is itself part of
    the file set (REQ-003), so a later `--check` difference is exactly the difference the test
    introduced, not the map gaining its own entry."""
    first, second = _generate(root, out_arg, *extra), _generate(root, out_arg, *extra)
    assert first.returncode == 0 and second.returncode == 0, (
        f"generate mode must exit 0: {first.returncode}/{second.returncode}: {first.stderr!r} {second.stderr!r}"
    )
    return (root / out_arg).read_bytes()


def _stale_message(out_arg: str) -> str:
    """The REQ-005 out-of-date line for an `--out` passed as `out_arg` (em dash, byte-for-byte)."""
    return f"{out_arg} is out of date \u2014 run {_RUN_COMMAND}"


def _missing_message(out_arg: str) -> str:
    """The REQ-005 missing-file line for an `--out` passed as `out_arg` (em dash, byte-for-byte)."""
    return f"{out_arg} is missing \u2014 run {_RUN_COMMAND}"


def _one_line(proc: subprocess.CompletedProcess[str], expected: str, label: str) -> None:
    """Assert REQ-005's 'exactly one line and nothing else': stdout is `expected` alone, stderr empty."""
    assert proc.stdout.splitlines() == [expected], f"{label}: stdout is {proc.stdout!r}, expected exactly {expected!r}"
    assert proc.stderr == "", f"{label}: stderr must be empty, got {proc.stderr!r}"


def _hook_clean(text: str) -> str:
    """The two active hooks' transforms (trailing-whitespace, end-of-file-fixer) applied to `text`.

    Re-implemented here (not imported from pre-commit) because the witness is the byte-level effect of
    the two hooks named in `.pre-commit-config.yaml`; `_active_hook_ids` anchors them to the config.
    """
    stripped = "\n".join(line.rstrip(" \t") for line in text.split("\n"))
    return stripped.rstrip("\n") + "\n" if stripped.strip() else stripped


def _active_hook_ids() -> set[str]:
    """The hook ids active in `.pre-commit-config.yaml` (read-only: AC-019 names these two hooks)."""
    text = _PRE_COMMIT.read_text(encoding="utf-8")
    return set(re.findall(r"^\s*-\s*id:\s*([\w-]+)", text, re.MULTILINE))


# --- T-006: the integration surface (the skill, the local hook, AGENTS.md, the advisory rule) -------

_SKILLS_DIR = _REPO_ROOT / ".agents" / "skills"
_MAP_SKILL = _SKILLS_DIR / "code-structure-map" / "SKILL.md"
_SPECIFY_SKILL = _SKILLS_DIR / "specify" / "SKILL.md"
_AGENTS_MD = _REPO_ROOT / "AGENTS.md"
_WORKFLOWS_DIR = _REPO_ROOT / ".github" / "workflows"
_CHECK_COMMAND = f"{_RUN_COMMAND} --check"  # REQ-023's pinned hook entry
_SKILL_BODY_MAX_LINES = 60  # REQ-022: the skill body stays under this many lines
_MAP_MENTION = re.compile(r"STRUCTURE\.md|make_map|code-structure-map")
_COUNT_LINE = re.compile(r"^([\w.-]+/)\s+[\u2014\u2013-]")  # REQ-009: a non-code top-level dir is one count line
_SAME_COMMIT_RULE = re.compile(r"same commit", re.IGNORECASE)
_CONFLICT_RULE = re.compile(r"either side", re.IGNORECASE)
_HAND_MERGE_RULE = re.compile(r"hand[- ]merge", re.IGNORECASE)
_FRESHNESS_RULES: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("the same-commit regeneration rule", _SAME_COMMIT_RULE),
    ("the take-either-side-and-regenerate conflict rule", _CONFLICT_RULE),
)
# The vocabulary of the workflow machinery (REQ-026): gates, todo statuses, handoff fields,
# prohibitions. A line that names the map *and* this vocabulary wires the map into a gate.
_MACHINERY = re.compile(
    r"\u25c6|blockedBy|BLOCKED-|Status:|VERIFIED|prohibition|prerequisite|fast-path|--skip-spec",
    re.IGNORECASE,
)
# The three AGENTS.md sections REQ-024 allows the map to be named in (its four places, two of which
# sit in Tooling). Anywhere else, a map mention is workflow machinery wiring (REQ-026).
_ALLOWED_MAP_SECTIONS = frozenset({"Tooling & Execution Environment", "Skill-to-Phase Mapping", "Project Structure"})


def _text_of(path: Path) -> str:
    """A repository guidance file as UTF-8 text, or a test failure naming the missing file (P-67)."""
    if not path.is_file():
        pytest.fail(f"{path.relative_to(_REPO_ROOT)} does not exist")
    return path.read_text(encoding="utf-8")


def _md_section(text: str, heading: str) -> list[str]:
    """The body lines of the markdown section `heading`, up to the next heading of the same or a higher level."""
    level = len(heading) - len(heading.lstrip("#"))
    body: list[str] = []
    inside = False
    for line in text.splitlines():
        if line.startswith("#"):
            if line.strip() == heading.strip():
                inside = True
                continue
            if inside and len(line) - len(line.lstrip("#")) <= level:
                break
        if inside:
            body.append(line)
    return body


def _fenced_block(lines: Sequence[str]) -> str:
    """The first fenced code block in `lines` (the layout block of the Project Structure section)."""
    body: list[str] = []
    inside = False
    for line in lines:
        if line.strip().startswith("```"):
            if inside:
                return "\n".join(body)
            inside = True
        elif inside:
            body.append(line)
    pytest.fail("the Project Structure section contains no fenced layout block")


def _block_dir_paths(block: str) -> set[str]:
    """The directory paths a layout block shows, in either form the block may use.

    Explicit path tokens (`src/backend/<feature>/`) are read as written; tree-drawn nesting is
    rebuilt into a full path from the branch-marker column. A `<placeholder>` segment stands for any
    name, so the path is recorded only up to it (REQ-024 item 1).
    """
    paths: set[str] = set()
    stack: list[tuple[int, str]] = []
    for line in block.splitlines():
        head, branch, rest = line.partition("\u2500\u2500")
        name = re.match(r"[\w<>.-]+/?", rest.strip()) if branch else None
        if name is None or set(name.group(0)) == {"."}:
            continue
        column = len(head)
        while stack and stack[-1][0] >= column:
            stack.pop()
        stack.append((column, name.group(0).rstrip("/")))
        segments: list[str] = []
        for _, segment in stack:
            if segment.startswith("<"):
                break
            segments.append(segment)
        if segments:
            paths.add("/".join(segments) + "/")
        for token in re.findall(r"[\w.][\w./-]*/", line.split("<", 1)[0]):
            if "/" in token.rstrip("/"):  # an explicit path token, not a bare tree-drawn name
                paths.add(token)
    return paths


def _map_dir_paths(map_text: str) -> tuple[set[str], set[str]]:
    """The directories the map's tree names: full entry paths, and REQ-009 count-line top-level names."""
    entries = _tree_entries(map_text)
    full = {text.rstrip("/") for _, text in entries if _ENTRY_PATH.fullmatch(text)}
    counted = {m.group(1).rstrip("/") for _, text in entries if (m := _COUNT_LINE.match(text))}
    assert full and counted, f"the map's tree names no directory at all ({len(entries)} entry lines)"
    return full, counted


def _paths_missing_from_map(paths: set[str], full: set[str], counted: set[str]) -> list[str]:
    """The layout paths the map does not name.

    A path below a top-level directory the map renders as a REQ-009 count line is named by that count
    line (REQ-009 never renders `.agents/skills/` as a tree entry); a path below a code dir MUST
    appear as a full tree entry, which is what keeps a `src/frontend/` entry a failure.
    """
    return [path for path in sorted(paths) if path.rstrip("/") not in full and path.split("/", 1)[0] not in counted]


def _hook_block(config: str, hook_id: str) -> str:
    """The YAML lines of hook `hook_id`'s own block, from its `- id:` line to the next hook or repo."""
    lines = config.splitlines()
    start = next(
        (i for i, line in enumerate(lines) if re.match(rf"^\s*-\s*id:\s*{re.escape(hook_id)}\s*$", line)), None
    )
    if start is None:
        pytest.fail(f".pre-commit-config.yaml declares no hook with id {hook_id!r}")
    end = next((i for i in range(start + 1, len(lines)) if re.match(r"^\s*-\s*(id|repo):", lines[i])), len(lines))
    return "\n".join(lines[start:end])


def test_ac_004_exit_code_contract(tmp_path: Path) -> None:
    """AC-004 (REQ-004): every row of the exit-code table is exactly the stated code, `1` and `3`
    never occur in generate mode, and when two conditions apply at once the precedence order
    `2 -> 4 -> 3 -> 1 -> 0` decides (an unparseable file plus a stale map exits 4, not 1)."""
    root = _git_tree(tmp_path / "tree", _TREE_FILES)
    out = root / "map.md"

    fresh = _generate(root, "map.md")
    assert fresh.returncode == 0, f"table row 0: generate success exits {fresh.returncode}: {fresh.stderr!r}"

    # Row 2 (usage) in both modes: --max-depth < 1 and an unknown option (argparse).
    for args in (["--root", str(root), "--max-depth", "0"], ["--nope"]):
        proc = _run([str(_GENERATOR), *args], cwd=root)
        assert proc.returncode == _EXIT_USAGE, f"table row 2: {args} exits {proc.returncode}, not 2"

    # Row 1 (stale) in --check mode only.
    out.write_bytes(out.read_bytes() + b"x")
    stale = _check(root, "map.md")
    assert stale.returncode == _EXIT_STALE, f"table row 1: a stale map in --check exits {stale.returncode}, not 1"

    # Row 3 (missing --out) in --check mode only.
    out.unlink()
    missing = _check(root, "map.md")
    assert missing.returncode == _EXIT_MISSING, (
        f"table row 3: a missing --out in --check exits {missing.returncode}, not 3"
    )

    # "1 and 3 never occur in generate mode": a stale map is rewritten (0), a missing map is created (0).
    out.write_text("hand edited\n", encoding="utf-8")
    rewrite = _generate(root, "map.md")
    assert rewrite.returncode == 0, f"generate mode must not exit 1 on a stale map: got {rewrite.returncode}"
    assert out.read_text(encoding="utf-8") != "hand edited\n", "generate mode must rewrite a stale map"
    out.unlink()
    created = _generate(root, "nested/map.md")
    assert created.returncode == 0, f"generate mode must not exit 3 on a missing --out: got {created.returncode}"
    assert (root / "nested" / "map.md").is_file(), "generate mode must create the missing --out"

    # Row 4 (unreadable/unparseable source) in both modes, and the precedence 4 -> 3: an unparseable
    # file outranks a missing --out, and 4 outranks staleness (4, not 1).
    (root / "src" / "broken.py").write_text("def f(:\n    pass\n", encoding="utf-8")
    unparseable_generate = _generate(root, "other.md")
    assert unparseable_generate.returncode == _EXIT_UNPARSEABLE, (
        f"table row 4: an unparseable source in generate mode exits {unparseable_generate.returncode}, not 4"
    )
    precedence_missing = _check(root, "map.md")
    assert precedence_missing.returncode == _EXIT_UNPARSEABLE, (
        f"precedence 4 -> 3: an unparseable source with a missing --out exits {precedence_missing.returncode}, not 3"
    )
    out.write_text("stale map\n", encoding="utf-8")
    precedence_stale = _check(root, "map.md")
    assert precedence_stale.returncode == _EXIT_UNPARSEABLE, (
        f"precedence 4 -> 1: an unparseable source with a stale map exits {precedence_stale.returncode}, not 1"
    )


def test_ac_005_check_byte_exact_single_message_exit_3(tmp_path: Path) -> None:
    """AC-005 (REQ-005): a single-byte difference exits 1 and prints exactly
    `<out> is out of date — run uv run python scripts/make_map.py` and nothing else; a missing `--out`
    exits 3 and prints exactly `<out> is missing — run uv run python scripts/make_map.py`; a
    whitespace-only difference is still a difference; a CRLF-only difference exits 0."""
    root = _git_tree(tmp_path / "tree", _TREE_FILES)
    out = root / "map.md"
    rendered = _generate_fixed_point(root, "map.md")

    # A single extra byte: exit 1, the one pinned line naming --out as given, nothing else.
    out.write_bytes(rendered + b"x")
    _one_line(_check(root, "map.md"), _stale_message("map.md"), "AC-005 clause 1")

    # A whitespace-only difference is a difference: no whitespace-insensitive diffing (REQ-005).
    lines = rendered.decode("utf-8").split("\n")
    out.write_text("\n".join([f"{lines[0]} ", *lines[1:]]), encoding="utf-8")
    whitespace = _check(root, "map.md")
    assert whitespace.returncode == _EXIT_STALE, (
        f"AC-005/REQ-005: a trailing-space-only difference exits {whitespace.returncode}, not 1"
    )

    # The message names the --out path exactly as given, including a nested relative path.
    nested_bytes = _generate_fixed_point(root, "nested/map.md")
    nested = root / "nested" / "map.md"
    nested.write_bytes(nested_bytes + b"x")
    _one_line(_check(root, "nested/map.md"), _stale_message("nested/map.md"), "AC-005 --out as given")

    # A missing --out: exit 3 and the one pinned missing line (explicit --out and the default).
    out.unlink()
    _one_line(_check(root, "map.md"), _missing_message("map.md"), "AC-005 clause 2")
    default = _run([str(_GENERATOR), "--root", str(root), "--check"], cwd=root)
    assert default.returncode == _EXIT_MISSING, (
        f"AC-005 clause 2: the default --out missing exits {default.returncode}, not 3"
    )
    _one_line(default, _missing_message("STRUCTURE.md"), "AC-005 clause 2 (default --out)")

    # The only difference is CRLF line endings: exit 0, and nothing printed (AC-005 clause 3).
    out.write_bytes(_generate_fixed_point(root, "map.md").replace(b"\n", b"\r\n"))
    crlf = _check(root, "map.md")
    assert crlf.returncode == 0, f"AC-005 clause 3: a CRLF-only map exits {crlf.returncode}, not 0"
    assert crlf.stdout == "", f"AC-005 clause 3: a fresh map prints nothing, got {crlf.stdout!r}"


def test_ac_019_double_run_byte_identical_and_hook_clean(tmp_path: Path) -> None:
    """AC-019 (REQ-019): two consecutive runs on an unchanged tree produce identical bytes, no line
    has trailing whitespace, the file ends with exactly one LF newline, and the active
    `trailing-whitespace` and `end-of-file-fixer` hooks leave the generated file unchanged."""
    assert {"trailing-whitespace", "end-of-file-fixer"} <= _active_hook_ids(), (
        "AC-019 names the two hooks; they are not active in .pre-commit-config.yaml"
    )
    root = _git_tree(tmp_path / "tree", _TREE_FILES)
    first = _run([str(_GENERATOR), "--root", str(root), "--out", str(tmp_path / "first.md")], cwd=root)
    second = _run([str(_GENERATOR), "--root", str(root), "--out", str(tmp_path / "second.md")], cwd=root)
    assert first.returncode == 0 and second.returncode == 0, (
        f"AC-019: generate runs exit {first.returncode}/{second.returncode}"
    )
    a = (tmp_path / "first.md").read_bytes()
    b = (tmp_path / "second.md").read_bytes()
    assert a == b, "AC-019 clause 1: two consecutive runs differ\n--- first ---\n" + a.decode("utf-8", "replace")[:400]
    assert b"\r" not in a, "REQ-019: generate mode always writes LF"
    trailing = [line for line in a.decode("utf-8").split("\n") if line != line.rstrip(" \t")]
    assert not trailing, f"AC-019 clause 2: lines with trailing whitespace: {trailing!r}"
    assert a.endswith(b"\n") and not a.endswith(b"\n\n"), "AC-019 clause 3: the file must end with exactly one LF"
    text = a.decode("utf-8")
    assert _hook_clean(text) == text, (
        "AC-019 clause 4: the trailing-whitespace / end-of-file-fixer hooks change the map"
    )


def test_edge_009_untracked_file_listed_then_stale_on_clone(tmp_path: Path) -> None:
    """EDGE-009: a file that is untracked and not ignored when the map is generated is listed in the
    committed map; on a fresh clone — the same tracked tree without that file — `--check` exits 1
    (stale) and regeneration removes it."""
    root = _git_tree(tmp_path / "tree", _TREE_FILES)
    (root / "src" / "scratch.py").write_text('"""Work in progress, never committed."""\n', encoding="utf-8")
    status = _git(["status", "--porcelain", "src/scratch.py"], root)
    assert status.stdout.strip() == "?? src/scratch.py", (
        f"EDGE-009 fixture: src/scratch.py is not untracked-not-ignored: {status.stdout!r}"
    )

    generated = _generate(root, "STRUCTURE.md")
    assert generated.returncode == 0, f"EDGE-009 fixture: generate exits {generated.returncode}: {generated.stderr!r}"
    # The second run is the state the map is committed at: STRUCTURE.md is now itself in the file set,
    # so the clone's only difference from a fresh render is the absent scratch.py.
    map_text = _generate_fixed_point(root, "STRUCTURE.md").decode("utf-8")
    assert "src/scratch.py" in map_text, "EDGE-009 clause 1 (REQ-003): the untracked file is not listed in the map"

    # The clone: the tracked tree plus the committed map, and no scratch.py.
    clone = _git_tree(tmp_path / "clone", {**_TREE_FILES, "STRUCTURE.md": map_text})
    stale = _check(clone, "STRUCTURE.md")
    assert stale.returncode == _EXIT_STALE, f"EDGE-009 clause 2: --check on the clone exits {stale.returncode}, not 1"
    _one_line(stale, _stale_message("STRUCTURE.md"), "EDGE-009 clause 2")

    regen = _generate(clone, "STRUCTURE.md")
    regenerated = _map_text(clone / "STRUCTURE.md", regen)
    assert "src/scratch.py" not in regenerated, "EDGE-009 clause 3: regeneration did not remove the untracked file"
    assert _check(clone, "STRUCTURE.md").returncode == 0, (
        "EDGE-009 clause 3: the regenerated map is still stale on the clone"
    )


def test_edge_010_hand_edited_map_is_stale(tmp_path: Path) -> None:
    """EDGE-010: a hand-edited `STRUCTURE.md`, or one a merge left with conflict markers, is stale —
    `--check` exits 1 with the pinned line, and the resolution is regeneration (exit 0, then fresh)."""
    root = _git_tree(tmp_path / "tree", _TREE_FILES)
    out = root / "STRUCTURE.md"
    generated = _generate_fixed_point(root, "STRUCTURE.md").decode("utf-8")

    out.write_text(f"{generated}\nA hand-written note.\n", encoding="utf-8")
    hand = _check(root, "STRUCTURE.md")
    assert hand.returncode == _EXIT_STALE, f"EDGE-010: a hand-edited map exits {hand.returncode}, not 1"
    _one_line(hand, _stale_message("STRUCTURE.md"), "EDGE-010 hand edit")

    markers = "\n<<<<<<< HEAD\n## Packages\n=======\n## Packages\n>>>>>>> other branch\n"
    out.write_text(generated + markers, encoding="utf-8")
    conflicted = _check(root, "STRUCTURE.md")
    assert conflicted.returncode == _EXIT_STALE, (
        f"EDGE-010: a map with conflict markers exits {conflicted.returncode}, not 1"
    )

    regen = _generate(root, "STRUCTURE.md")
    assert _map_text(out, regen) == generated, "EDGE-010: regeneration must restore the generated bytes"
    assert _check(root, "STRUCTURE.md").returncode == 0, "EDGE-010: after regeneration --check must exit 0"


def test_edge_016_crlf_checkout_is_not_stale(tmp_path: Path) -> None:
    """EDGE-016 (REQ-005): a checked-out map whose only difference from the render is CRLF line
    endings is **not** stale — `--check` normalises `\r\n` -> `\n` and exits 0; the normalisation is
    exactly that (a CRLF map with one extra byte is still stale), and generate mode rewrites LF."""
    root = _git_tree(tmp_path / "tree", _TREE_FILES)
    out = root / "STRUCTURE.md"
    lf = _generate_fixed_point(root, "STRUCTURE.md")
    assert b"\r" not in lf, "EDGE-016 fixture: generate mode did not write LF"

    # Written as explicit CRLF bytes: a core.autocrlf=true checkout of the committed LF blob.
    crlf = lf.replace(b"\n", b"\r\n")
    assert crlf != lf and b"\r\n" in crlf, "EDGE-016 fixture: the map is not a CRLF checkout"
    out.write_bytes(crlf)
    check = _check(root, "STRUCTURE.md")
    assert check.returncode == 0, f"EDGE-016: a CRLF-only checkout exits {check.returncode}, not 0: {check.stdout!r}"
    assert check.stdout == "", f"EDGE-016: a fresh map prints nothing, got {check.stdout!r}"

    out.write_bytes(crlf + b"x")
    stale = _check(root, "STRUCTURE.md")
    assert stale.returncode == _EXIT_STALE, (
        f"REQ-005: the only normalisation is \r\n -> \n; a CRLF map with an extra byte exits {stale.returncode}, not 1"
    )

    regen = _generate(root, "STRUCTURE.md")
    assert regen.returncode == 0 and out.read_bytes() == lf, "EDGE-016: generate mode must rewrite the file with LF"


def test_ac_022_skill_exists_with_four_rules() -> None:
    """AC-022 (REQ-022): the skill exists, follows the skill format, and states the four rules."""
    text = _text_of(_MAP_SKILL)
    assert text.startswith("---\n"), "the skill must open with a frontmatter block"
    front, closed, body = text[4:].partition("\n---")
    assert closed, "the frontmatter block is never closed"
    assert re.search(r"^name:\s*\S", front, re.MULTILINE), "the frontmatter must carry a `name`"
    assert re.search(r"^description:\s*\S", front, re.MULTILINE), "the frontmatter must carry a `description`"
    body_lines = [line for line in body.splitlines() if line.strip()]
    assert body_lines, "the skill body is empty"
    assert len(body_lines) < _SKILL_BODY_MAX_LINES, (
        f"REQ-022: the skill body must stay under {_SKILL_BODY_MAX_LINES} lines, got {len(body_lines)}"
    )
    rules: dict[str, re.Pattern[str]] = {
        "read the map before walking the tree": re.compile(r"STRUCTURE\.md[^\n]*\bbefore[^\n]*\btree", re.IGNORECASE),
        "regenerate when it is stale": re.compile(r"\bstale\b", re.IGNORECASE),
        "regenerate in the same commit as the .py change": _SAME_COMMIT_RULE,
        "on a merge conflict take either side and regenerate": _CONFLICT_RULE,
    }
    missing = [rule for rule, pattern in rules.items() if not pattern.search(text)]
    assert not missing, f"the skill does not state: {missing}"
    assert _RUN_COMMAND in text, "the skill must name the generate command it points the reader at"
    assert _HAND_MERGE_RULE.search(text), "the skill must say the generated map is never hand-merged"


def test_ac_023_hook_is_check_only_and_no_ci_job() -> None:
    """AC-023 (REQ-023): the map hook is a check-only local hook, and no CI job runs the generator."""
    config = _text_of(_PRE_COMMIT)
    assert _active_hook_ids(), ".pre-commit-config.yaml declares no hook at all"
    block = _hook_block(config, "structure-map-check")
    between = config[config.index("- repo: local") : config.index("id: structure-map-check")]
    assert "- repo:" not in between.removeprefix("- repo: local"), "the hook is not in the existing `repo: local` block"
    fields = {
        "entry": f"entry: {_CHECK_COMMAND}",
        "language": "language: system",
        "pass_filenames": "pass_filenames: false",
        "stages": "stages: [pre-commit]",
        "files": r"files: \.py$",
    }
    missing = [f"{name}: {value}" for name, value in fields.items() if value not in block]
    assert not missing, f"the structure-map-check hook is missing {missing}; its block is:\n{block}"
    entry = next(
        (line.split("entry:", 1)[1].strip() for line in block.splitlines() if line.strip().startswith("entry:")), ""
    )
    assert "--check" in entry, f"REQ-023: the hook entry must be check-only, got {entry!r}"
    assert "--out" not in entry and entry != _RUN_COMMAND, f"REQ-023: the hook must never rewrite the map: {entry!r}"
    workflows = sorted(p for p in _WORKFLOWS_DIR.iterdir() if p.is_file())
    assert workflows, f"no workflow file under {_WORKFLOWS_DIR}"
    mentioning = [p.name for p in workflows if "make_map" in p.read_text(encoding="utf-8")]
    assert not mentioning, f"ADR-085: no GitHub Actions workflow may run the generator, found {mentioning}"


def test_ac_024_agents_md_layout_matches_the_map(tmp_path: Path) -> None:
    """AC-024 (REQ-024): the corrected layout block agrees with the generated map and shows no stale form."""
    agents = _text_of(_AGENTS_MD)
    section = _md_section(agents, "## Project Structure")
    assert section, "AGENTS.md has no Project Structure section"
    block = _fenced_block(section)
    paths = _block_dir_paths(block)
    assert paths, "the layout block shows no directory path at all"
    shown = [name for name in ("model/", "services/", "src/frontend/") if name in block]
    assert not shown, f"REQ-024: the layout block still shows {shown}"
    stale = sorted(p for p in paths if {"model", "services", "frontend"} & set(p.split("/")))
    assert not stale, f"REQ-024: the layout block still shows a stale directory: {stale}"
    out = tmp_path / "STRUCTURE.md"
    full, counted = _map_dir_paths(_map_text(out, _generate(_REPO_ROOT, str(out))))
    missing = _paths_missing_from_map(paths, full, counted)
    assert not missing, f"REQ-024: layout paths absent from the generated map's tree: {missing}"
    tooling = "\n".join(_md_section(agents, "## Tooling & Execution Environment"))
    assert tooling, "AGENTS.md has no Tooling & Execution Environment section"
    assert _RUN_COMMAND in tooling, "the Tooling section must name the generate command"
    assert "--check" in tooling, "the Tooling section must name the --check command"
    mapping = _md_section(agents, "### Skill-to-Phase Mapping")
    assert mapping, "AGENTS.md has no Skill-to-Phase Mapping section"
    for skill in ("code-structure-map", "python-best-practices"):
        rows = [line for line in mapping if skill in line]
        assert rows, f"the Skill-to-Phase Mapping has no row for {skill}"
        assert all("(ambient)" in line for line in rows), f"the {skill} row is not marked `(ambient)`"
    cited = [
        str(p.relative_to(_REPO_ROOT))
        for p in (_AGENTS_MD, *sorted(_SKILLS_DIR.rglob("*")))
        if p.is_file() and "tests/architecture" in p.read_text(encoding="utf-8")
    ]
    assert not cited, f"REQ-024: `tests/architecture` is cited again in {cited}"


def test_ac_026_map_hook_is_advisory() -> None:
    """AC-026 (REQ-026): no gate, todo status, handoff field or prohibition depends on the map."""
    heading = ""
    wired: list[str] = []
    for line in _text_of(_AGENTS_MD).splitlines():
        if line.startswith("#"):
            heading = line.lstrip("#").strip()
        if _MAP_MENTION.search(line) and (heading not in _ALLOWED_MAP_SECTIONS or _MACHINERY.search(line)):
            wired.append(f"[{heading}] {line.strip()}")
    assert not wired, f"REQ-026: the map is wired into the workflow machinery: {wired}"
    skills = {p: _text_of(p) for p in sorted(_SKILLS_DIR.rglob("SKILL.md")) if p.parent.name != "code-structure-map"}
    assert skills, f"no phase skill found under {_SKILLS_DIR}"
    for path, text in skills.items():
        if path == _SPECIFY_SKILL:
            continue
        hits = [line.strip() for line in text.splitlines() if _MAP_MENTION.search(line)]
        assert not hits, f"REQ-026: {path.relative_to(_REPO_ROOT)} makes the map part of a phase: {hits}"
    p1 = _md_section(_text_of(_SPECIFY_SKILL), "### P.1 Frame (orchestrator)")
    assert p1, "specify/SKILL.md has no P.1 Frame section"
    advisory = [line.strip() for line in p1 if _MAP_MENTION.search(line)]
    assert len(advisory) == 1, f"REQ-026: P.1 must carry exactly one advisory sentence about the map, got {advisory}"
    assert re.search(r"\bread\b", advisory[0], re.IGNORECASE), (
        f"the P.1 sentence must advise reading the map: {advisory[0]!r}"
    )
    assert not _MACHINERY.search(advisory[0]), f"REQ-026: the P.1 sentence is a gate, not advice: {advisory[0]!r}"


def test_ac_027_freshness_policy_documented_twice() -> None:
    """AC-027 (REQ-027): the skill and the AGENTS.md pointer line both state both freshness rules."""
    skill = _text_of(_MAP_SKILL)
    tooling = "\n".join(_md_section(_text_of(_AGENTS_MD), "## Tooling & Execution Environment"))
    assert tooling, "AGENTS.md has no Tooling & Execution Environment section"
    pointer = [line for line in tooling.splitlines() if _MAP_MENTION.search(line)]
    assert pointer, "the Tooling section carries no pointer line naming the map and the skill"
    for label, text in (("the skill", skill), ("the AGENTS.md Tooling section", tooling)):
        missing = [rule for rule, pattern in _FRESHNESS_RULES if not pattern.search(text)]
        assert not missing, f"{label} does not state: {missing}"
        assert _HAND_MERGE_RULE.search(text), f"{label} does not say the generated map is never hand-merged"


# --- T-007: the committed artifact — STRUCTURE.md (REQ-021, AC-021, NFR-002, NFR-005) -----------

_MAP_FILE = _REPO_ROOT / "STRUCTURE.md"
_NFR_002_LINE_BUDGET = 2_000  # NFR-002: the committed map is ≤ 2 000 lines
_COMPLEXIPY_MAX = "15"  # NFR-005: [tool.complexipy] max-complexity-allowed
_COMPLEXIPY_PATHS: tuple[str, ...] = ("src", "tests")  # NFR-005: [tool.complexipy] paths
_ANSI = re.compile(r"\x1b\[[0-9;]*m")


def _complexipy(max_allowed: str) -> subprocess.CompletedProcess[str]:
    """The CI complexity gate (`complexipy src tests --max-complexity-allowed <n>`) run from the repo root.

    `sys.executable -m complexipy` is impossible — the package ships no `__main__` — so the console
    script next to the interpreter is the same binary `uv run complexipy` resolves in CI (quality.yml).
    """
    script = Path(sys.executable).parent / ("complexipy.exe" if sys.platform == "win32" else "complexipy")
    assert script.is_file(), f"complexipy is not installed in the test venv: {script}"
    return subprocess.run(
        [str(script), *_COMPLEXIPY_PATHS, "--max-complexity-allowed", max_allowed],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=_REPO_ROOT,
        check=False,
    )


def _complexipy_report(stdout: str) -> tuple[list[str], list[str]]:
    """(every analysed function line, the ones over the limit) of a complexipy run, ANSI codes stripped."""
    analysed = [
        line
        for line in (_ANSI.sub("", raw).strip() for raw in stdout.splitlines())
        if "PASSED" in line or "FAILED" in line
    ]
    return analysed, [line for line in analysed if "FAILED" in line]


def _map_line_difference(committed: bytes, fresh: bytes) -> str:
    """The first difference between the committed map and a fresh render, as a readable message."""
    old, new = committed.decode("utf-8").splitlines(), fresh.decode("utf-8").splitlines()
    for number, (before, after) in enumerate(zip(old, new, strict=False), start=1):
        if before != after:
            return f"line {number} differs:\n  committed: {before!r}\n  fresh:     {after!r}"
    return f"line count differs: committed {len(old)} lines, fresh {len(new)} lines"


def test_ac_021_committed_map_matches_fresh_render(tmp_path: Path) -> None:
    """AC-021 (REQ-021): the committed STRUCTURE.md is a fresh render of this tree and `--check` exits 0."""
    assert _MAP_FILE.is_file(), "REQ-021: no STRUCTURE.md is committed at the repository root"
    out = tmp_path / "STRUCTURE.md"
    proc = _generate(_REPO_ROOT, str(out))
    assert proc.returncode == 0, f"generate mode must exit 0 for the repository root: {_output(proc)!r}"
    fresh = out.read_bytes()
    assert fresh, "the fresh render is empty: a byte comparison against an empty render proves nothing"
    committed = _MAP_FILE.read_bytes()
    assert committed == fresh, (
        f"REQ-021: the committed map is not a fresh render — {_map_line_difference(committed, fresh)}"
    )
    check = _check(_REPO_ROOT, str(_MAP_FILE))
    assert check.returncode == 0, f"AC-021: --check exits {check.returncode}, expected 0: {_output(check)!r}"


def test_nfr_002_map_line_budget() -> None:
    """NFR-002: the committed STRUCTURE.md is non-empty and within the ≤ 2 000 line ceiling."""
    assert _MAP_FILE.is_file(), "REQ-021: no STRUCTURE.md is committed at the repository root"
    lines = _MAP_FILE.read_text(encoding="utf-8").splitlines()
    assert any(line.strip() for line in lines), "the committed map is empty: the line budget would pass vacuously"
    assert len(lines) <= _NFR_002_LINE_BUDGET, (
        f"NFR-002: the committed map is {len(lines)} lines, over the {_NFR_002_LINE_BUDGET}-line ceiling"
    )


def test_nfr_005_complexipy_threshold_holds() -> None:
    """NFR-005: the CI complexity gate `complexipy src tests --max-complexity-allowed 15` exits 0."""
    tripwire = _complexipy("0")
    tripwire_code = tripwire.returncode
    assert tripwire_code != 0, "the complexipy run is vacuous: it exits 0 even with a limit of 0 branches"
    proc = _complexipy(_COMPLEXIPY_MAX)
    code = proc.returncode
    analysed, over = _complexipy_report(proc.stdout)
    assert analysed, f"NFR-005: complexipy analysed nothing (exit {code}): {proc.stderr.strip()!r}"
    assert code == 0, (
        f"NFR-005: complexipy exits {code} at max-complexity-allowed {_COMPLEXIPY_MAX}: "
        f"{len(over)} of {len(analysed)} analysed functions are over the limit: {over}"
    )
