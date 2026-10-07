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
