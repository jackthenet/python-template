"""Property tests for the structure-map change (spec: `docs/specs/structure-map.md`).

The §11 invariant witnesses for T-003: **INV-002** (pruning never hides an in-scope module) and
**INV-003** (no absolute path, drive letter, UNC path, timestamp, host name or user name).
Placement is fixed by spec §11 / Q-10: `tests/property/test_structure_map.py`.

Every witness drives the generator as a **subprocess** over a generated throwaway git tree. The
generator is never imported, so its absence is a test failure, not a collection error (a setup
error is not a valid RED). Each example builds its tree in a fresh `TemporaryDirectory` —
Hypothesis reuses one function-scoped `tmp_path` across examples, and the generator's file set is
read from disk.
"""

from __future__ import annotations

import getpass
import platform
import re
import subprocess
import sys
import tempfile
from collections.abc import Mapping
from pathlib import Path, PurePosixPath

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

_REPO_ROOT = Path(__file__).resolve().parents[2]
_GENERATOR = _REPO_ROOT / "scripts" / "make_map.py"

# REQ-009 code dirs (rendered in full in the tree) and REQ-011 Packages dirs.
_CODE_DIRS: tuple[str, ...] = ("src", "tests", "scripts", "migrations")
_PACKAGES_DIRS: tuple[str, ...] = ("src", "scripts", "migrations")

_MAX_EXAMPLES = 12

_ENTRY_PATH = re.compile(r"[\w./-]+/?")
_PRUNE_MARKER = re.compile(r"\(\+\d+ (?:dirs|files)(?:, \d+ (?:dirs|files))? not shown\)")

# INV-003: content that must never appear anywhere in a generated map (the set AC-008 pins too).
_FORBIDDEN: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("a timestamp", re.compile(r"\d{4}-\d{2}-\d{2}|\b\d{1,2}:\d{2}:\d{2}\b")),
    ("a drive letter or UNC path", re.compile(r"[A-Za-z]:[\\/]")),
    ("a Windows path separator", re.compile(r"\\")),
    ("an absolute POSIX path", re.compile(r"(^|\s)/[A-Za-z0-9_.]")),
)

# A `.py` outside every code dir — INV-002's last clause: it is parsed but appears in neither the
# tree nor Packages, only in its top-level directory's count line — plus a second file in the same
# directory, so that count line has to count more than the `.py`.
_OUTSIDE_CODE_DIRS: tuple[str, ...] = (".github/hooks/ruff-post-edit.py", ".github/workflows/ci.yml")

_DIR_SEGMENTS = st.sampled_from(("pkg", "sub", "deep"))
_FILE_NAMES = st.sampled_from(("mod.py", "conftest.py", "helpers_test_helpers.py", "a.py", "b.py"))


def _file_name(path: str) -> str:
    """The last segment of a `/`-separated path."""
    return path.rsplit("/", 1)[-1]


def _depth(path: str) -> int:
    """REQ-010 depth: counted in path segments from the root (`src`=1, `src/backend`=2, ...)."""
    return len(PurePosixPath(path).parts)


def _in_packages_scope(path: str) -> bool:
    """REQ-011: every module under `src/`, `scripts/`, `migrations/`, plus tests/ conftest/test-helpers."""
    top = path.split("/", 1)[0]
    name = _file_name(path)
    return path.endswith(".py") and (
        top in _PACKAGES_DIRS or name == "conftest.py" or name.endswith("_test_helpers.py")
    )


@st.composite
def _module_path(draw: st.DrawFn) -> str:
    """A generated module path under a code dir, 1-4 segments deep, in-domain names only."""
    parts = [draw(st.sampled_from(_CODE_DIRS))]
    for _ in range(draw(st.integers(min_value=0, max_value=3))):
        parts.append(draw(_DIR_SEGMENTS))
    parts.append(draw(_FILE_NAMES))
    return "/".join(parts)


@st.composite
def _tree(draw: st.DrawFn) -> tuple[str, ...]:
    """A generated tracked file set: unique module paths under the code dirs, plus the fixed files
    outside every code dir."""
    paths = draw(st.lists(_module_path(), min_size=3, max_size=10, unique=True))
    return tuple(sorted({*paths, *_OUTSIDE_CODE_DIRS}))


def _source(path: str) -> str:
    """In-domain content for a generated module path (a docstring, so a summary line is rendered)."""
    return f'"""The {_file_name(path).removesuffix(".py")} module."""\n'


def _git_tree(root: Path, files: Mapping[str, str]) -> Path:
    """A throwaway git tree: `git init`, write `files`, stage them (REQ-003 needs no commit)."""
    for name, text in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    for args in (["init", "-q", "-b", "main"], ["add", "-A"]):
        proc = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, encoding="utf-8", check=False)
        if proc.returncode != 0:
            pytest.fail(f"git {' '.join(args)} failed in {root}: {proc.stderr.strip()}")
    return root


def _render(root: Path, out: Path, max_depth: int) -> str:
    """Generate the map for `root` at `--max-depth max_depth` and return its text."""
    if not _GENERATOR.is_file():
        pytest.fail(f"{_GENERATOR} does not exist — T-002 Phase 4 has not implemented the generator")
    proc = subprocess.run(
        [sys.executable, str(_GENERATOR), "--root", str(root), "--out", str(out), "--max-depth", str(max_depth)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=_REPO_ROOT,
        check=False,
    )
    if proc.returncode != 0:
        pytest.fail(f"generate run exits {proc.returncode}: {proc.stdout!r} {proc.stderr!r}")
    if not out.is_file():
        pytest.fail(f"no map file at {out}: {proc.stdout!r} {proc.stderr!r}")
    return out.read_text(encoding="utf-8")


def _section_lines(map_text: str, heading: str) -> list[str]:
    """The lines after `heading` up to the next `## ` heading."""
    lines = map_text.splitlines()
    start = lines.index(heading)
    body: list[str] = []
    for line in lines[start + 1 :]:
        if line.startswith("## "):
            break
        body.append(line)
    return body


def _tree_entries(map_text: str) -> list[tuple[int, str]]:
    """The Directory tree section as `(indent, entry text)` pairs — count lines, prune markers and
    blank lines dropped, so a path can never be matched inside another line's text."""
    entries: list[tuple[int, str]] = []
    for line in _section_lines(map_text, "## Directory tree"):
        text = line.strip()
        if not text or text.startswith("#") or not _ENTRY_PATH.fullmatch(text) or _PRUNE_MARKER.fullmatch(text):
            continue
        entries.append((len(line) - len(line.lstrip()), text))
    return entries


def _tree_paths(map_text: str) -> set[str]:
    """Every path the Directory tree renders (directories with their trailing `/` stripped)."""
    return {text.rstrip("/") for _, text in _tree_entries(map_text)}


def _count_lines(map_text: str) -> list[str]:
    """The top-level count lines of the Directory tree (REQ-009 clause 3)."""
    return [
        line.strip()
        for line in _section_lines(map_text, "## Directory tree")
        if line.strip() and not _ENTRY_PATH.fullmatch(line.strip()) and not line.strip().startswith("#")
    ]


def _module_paths(map_text: str) -> set[str]:
    """The paths of every `#### ` module header in the Packages section."""
    paths: set[str] = set()
    for line in _section_lines(map_text, "## Packages"):
        if match := re.match(r"#### (\S+\.py) \(", line):
            paths.add(match.group(1))
    return paths


def test_inv_002_no_module_hidden_by_pruning() -> None:
    """INV-002 (REQ-009/REQ-010/REQ-011): for any generated tree and any `--max-depth >= 1`, every
    `.py` under a code dir at depth <= `--max-depth` appears in the Directory tree, every in-scope
    module appears in the Packages section, and a `.py` outside a code dir appears only in its
    top-level directory's count line."""
    if not _GENERATOR.is_file():
        pytest.fail(f"{_GENERATOR} does not exist — T-002 Phase 4 has not implemented the generator")

    @settings(max_examples=_MAX_EXAMPLES, deadline=None, suppress_health_check=[HealthCheck.too_slow])
    @given(tree=_tree(), max_depth=st.integers(min_value=1, max_value=5))
    def check(tree: tuple[str, ...], max_depth: int) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            root = _git_tree(base / "tree", {path: _source(path) for path in tree})
            map_text = _render(root, base / "map.md", max_depth)
            entries = _tree_paths(map_text)
            modules = _module_paths(map_text)

            in_scope = {path for path in tree if _in_packages_scope(path)}
            assert modules == in_scope, (
                f"--max-depth {max_depth}: Packages section {sorted(modules)} is not the REQ-011 scope {sorted(in_scope)}"
            )

            for path in tree:
                top, path_depth = path.split("/", 1)[0], _depth(path)
                if top in _CODE_DIRS:
                    if path_depth <= max_depth:
                        assert path in entries, (
                            f"{path} (depth {path_depth}) is missing from the tree at --max-depth {max_depth}: "
                            f"{sorted(entries)!r}"
                        )
                    else:
                        assert path not in entries, (
                            f"{path} (depth {path_depth}) is rendered although --max-depth is {max_depth}"
                        )
                else:
                    assert path not in entries and path not in modules, (
                        f"{path} is outside every code dir but appears in the tree or Packages scope"
                    )

            counts = [line for line in _count_lines(map_text) if line.startswith(".github/")]
            assert len(counts) == 1 and f"{len(_OUTSIDE_CODE_DIRS)} files" in counts[0], (
                f"the .github/ count line is {counts!r}, expected one line counting "
                f"{len(_OUTSIDE_CODE_DIRS)} files (INV-002: a .py outside a code dir appears nowhere else)"
            )

    check()


def test_inv_003_no_absolute_path_or_timestamp() -> None:
    """INV-003 (REQ-008/REQ-020): for any generated tree and any `--max-depth >= 1`, the output
    contains no absolute path, drive letter, UNC path, timestamp, host name or user name — and never
    the `--root` it was handed."""
    if not _GENERATOR.is_file():
        pytest.fail(f"{_GENERATOR} does not exist — T-002 Phase 4 has not implemented the generator")

    @settings(max_examples=_MAX_EXAMPLES, deadline=None, suppress_health_check=[HealthCheck.too_slow])
    @given(tree=_tree(), max_depth=st.integers(min_value=1, max_value=5))
    def check(tree: tuple[str, ...], max_depth: int) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            root = _git_tree(base / "tree", {path: _source(path) for path in tree})
            map_text = _render(root, base / "map.md", max_depth)

            for label, pattern in _FORBIDDEN:
                hit = pattern.search(map_text)
                assert hit is None, f"the map contains {label}: {hit.group(0)!r}"

            for identity in (platform.node(), getpass.getuser()):
                if identity:
                    assert not re.search(rf"\b{re.escape(identity)}\b", map_text), (
                        f"the map contains the host/user name {identity!r}"
                    )

            for absolute in (str(root), root.as_posix(), str(base)):
                assert absolute not in map_text, f"the map contains the absolute host path {absolute!r}"

    check()
