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


def _inv002_count_line_claim(map_text: str) -> None:
    """INV-002: a `.py` outside a code dir appears only in its top-level directory's count line."""
    counts = [line for line in _count_lines(map_text) if line.startswith(".github/")]
    assert len(counts) == 1 and f"{len(_OUTSIDE_CODE_DIRS)} files" in counts[0], (
        f"the .github/ count line is {counts!r}, expected one line counting "
        f"{len(_OUTSIDE_CODE_DIRS)} files (INV-002: a .py outside a code dir appears nowhere else)"
    )


def _inv002_path_claim(path: str, max_depth: int, entries: set[str], modules: set[str]) -> str | None:
    """The INV-002 claim `path` violates in a tree rendered at `--max-depth`, or None if it holds."""
    top, path_depth = path.split("/", 1)[0], _depth(path)
    if top not in _CODE_DIRS:
        if path in entries or path in modules:
            return f"{path} is outside every code dir but appears in the tree or Packages scope"
        return None
    if path_depth <= max_depth:
        if path not in entries:
            return (
                f"{path} (depth {path_depth}) is missing from the tree at --max-depth {max_depth}: {sorted(entries)!r}"
            )
        return None
    if path in entries:
        return f"{path} (depth {path_depth}) is rendered although --max-depth is {max_depth}"
    return None


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

            violations = [
                claim for claim in (_inv002_path_claim(p, max_depth, entries, modules) for p in tree) if claim
            ]
            assert not violations, f"--max-depth {max_depth}: {'; '.join(violations)}"

            _inv002_count_line_claim(map_text)

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


# --- T-005: determinism, --check byte equality, --check writes nothing, hook-clean output -------
# (INV-001, INV-004, INV-005, INV-006 / REQ-004, REQ-005, REQ-019)

_EXIT_MISSING = 3  # REQ-004: --check found no --out file


def _check_run(root: Path, out: Path, max_depth: int) -> subprocess.CompletedProcess[str]:
    """Run `--check` for `root` against `out` at `--max-depth max_depth` (the exit code is the witness)."""
    if not _GENERATOR.is_file():
        pytest.fail(f"{_GENERATOR} does not exist — T-002 Phase 4 has not implemented the generator")
    return subprocess.run(
        [
            sys.executable,
            str(_GENERATOR),
            "--root",
            str(root),
            "--out",
            str(out),
            "--check",
            "--max-depth",
            str(max_depth),
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=_REPO_ROOT,
        check=False,
    )


def _hook_clean(text: str) -> str:
    """The active `trailing-whitespace` and `end-of-file-fixer` transforms applied to `text` (INV-006).

    Re-implemented at this layer (the same two transforms as the acceptance witness) because the
    property node asserts the byte-level effect for every generated tree, not the config entry.
    """
    stripped = "\n".join(line.rstrip(" \t") for line in text.split("\n"))
    return stripped.rstrip("\n") + "\n" if stripped.strip() else stripped


def _snapshot(base: Path) -> dict[str, bytes]:
    """Every working-tree file under `base` as path -> bytes (INV-005: `--check` changes none of them).

    `.git/` is excluded: INV-005 protects the working tree, and a git command may legitimately rewrite
    the index without touching a single tracked file.
    """
    return {
        path.relative_to(base).as_posix(): path.read_bytes()
        for path in sorted(base.rglob("*"))
        if path.is_file() and ".git" not in path.relative_to(base).parts
    }


def test_inv_001_render_is_deterministic() -> None:
    """INV-001 (REQ-019): for any tree state, two generator runs with the same options produce
    byte-identical output — and so does a run over the same tree whose files were created in the
    opposite order (the render is sorted by `--root`-relative POSIX path, never by walk order)."""
    if not _GENERATOR.is_file():
        pytest.fail(f"{_GENERATOR} does not exist — T-002 Phase 4 has not implemented the generator")

    @settings(max_examples=_MAX_EXAMPLES, deadline=None, suppress_health_check=[HealthCheck.too_slow])
    @given(tree=_tree(), max_depth=st.integers(min_value=1, max_value=5))
    def check(tree: tuple[str, ...], max_depth: int) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            files = {path: _source(path) for path in tree}
            root = _git_tree(base / "tree", files)
            _render(root, base / "first.md", max_depth)
            _render(root, base / "second.md", max_depth)
            first = (base / "first.md").read_bytes()
            second = (base / "second.md").read_bytes()
            assert first == second, f"INV-001: two runs over the same tree differ:\n{first!r}\n{second!r}"

            reversed_root = _git_tree(base / "reversed", dict(reversed(list(files.items()))))
            _render(reversed_root, base / "third.md", max_depth)
            third = (base / "third.md").read_bytes()
            assert third == first, f"INV-001/REQ-019: creation order changed the render for tree {sorted(tree)}"

    check()


def test_inv_004_check_matches_byte_equality() -> None:
    """INV-004 (REQ-005): `--check` exits 0 if and only if the on-disk bytes equal a fresh render after
    `\r\n` -> `\n` normalisation; every other difference — added, removed, reordered or whitespace-only
    — exits 1."""
    if not _GENERATOR.is_file():
        pytest.fail(f"{_GENERATOR} does not exist — T-002 Phase 4 has not implemented the generator")

    @settings(max_examples=_MAX_EXAMPLES, deadline=None, suppress_health_check=[HealthCheck.too_slow])
    @given(tree=_tree(), max_depth=st.integers(min_value=1, max_value=5))
    def check(tree: tuple[str, ...], max_depth: int) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            root = _git_tree(base / "tree", {path: _source(path) for path in tree})
            out = base / "map.md"
            rendered = _render(root, out, max_depth)
            rendered_bytes = out.read_bytes()
            lines = rendered.split("\n")

            def code(content: bytes) -> int:
                out.write_bytes(content)
                return _check_run(root, out, max_depth).returncode

            assert code(rendered_bytes) == 0, "INV-004: a byte-identical map must exit 0"
            assert code(rendered_bytes.replace(b"\n", b"\r\n")) == 0, "INV-004/EDGE-016: a CRLF-only map must exit 0"

            whitespace = "\n".join([f"{lines[0]} ", *lines[1:]]).encode("utf-8")
            variants = {
                "added": rendered_bytes + b"x",
                "removed": "\n".join(lines[1:]).encode("utf-8"),
                "reordered": "\n".join([lines[1], lines[0], *lines[2:]]).encode("utf-8"),
                "whitespace-only": whitespace,
            }
            for label, content in variants.items():
                assert content != rendered_bytes, f"INV-004 fixture: the {label} variant is not a real difference"
                assert code(content) == 1, f"INV-004: a {label} difference must exit 1"

    check()


def test_inv_005_check_writes_nothing() -> None:
    """INV-005: the generator writes no file other than `--out` and only in generate mode — `--check`
    leaves every working-tree path and its bytes unchanged, and a missing `--out` is reported (exit 3),
    never created."""
    if not _GENERATOR.is_file():
        pytest.fail(f"{_GENERATOR} does not exist — T-002 Phase 4 has not implemented the generator")

    @settings(max_examples=_MAX_EXAMPLES, deadline=None, suppress_health_check=[HealthCheck.too_slow])
    @given(tree=_tree(), max_depth=st.integers(min_value=1, max_value=5))
    def check(tree: tuple[str, ...], max_depth: int) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            root = _git_tree(base / "tree", {path: _source(path) for path in tree})
            out = base / "map.md"
            _render(root, out, max_depth)
            before = _snapshot(base)
            assert "map.md" in before, "INV-005 fixture: generate mode wrote no --out"

            fresh = _check_run(root, out, max_depth)
            assert fresh.returncode == 0, f"INV-005 fixture: --check on a fresh map exits {fresh.returncode}"
            after = _snapshot(base)
            assert after == before, (
                f"INV-005: --check modified the working tree: {sorted(set(before) ^ set(after)) or 'bytes changed'}"
            )

            out.unlink()
            missing = _snapshot(base)
            absent = _check_run(root, out, max_depth)
            assert absent.returncode == _EXIT_MISSING, (
                f"INV-005/REQ-004: --check with a missing --out exits {absent.returncode}, not 3"
            )
            assert not out.exists(), "INV-005: --check must not create the missing --out"
            assert _snapshot(base) == missing, "INV-005: --check wrote a file other than --out"

    check()


def test_inv_006_output_is_hook_clean() -> None:
    """INV-006 (REQ-019): for any generated map the active `trailing-whitespace` and `end-of-file-fixer`
    hooks leave the file unchanged — no line carries trailing whitespace, the bytes end with exactly one
    LF, and the two hook transforms are the identity on the render."""
    if not _GENERATOR.is_file():
        pytest.fail(f"{_GENERATOR} does not exist — T-002 Phase 4 has not implemented the generator")

    @settings(max_examples=_MAX_EXAMPLES, deadline=None, suppress_health_check=[HealthCheck.too_slow])
    @given(tree=_tree(), max_depth=st.integers(min_value=1, max_value=5))
    def check(tree: tuple[str, ...], max_depth: int) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            root = _git_tree(base / "tree", {path: _source(path) for path in tree})
            out = base / "map.md"
            _render(root, out, max_depth)
            data = out.read_bytes()
            assert b"\r" not in data, "INV-006 fixture: generate mode wrote a CR"
            assert data.endswith(b"\n") and not data.endswith(b"\n\n"), (
                "INV-006: the map does not end with exactly one LF"
            )
            text = data.decode("utf-8")
            assert _hook_clean(text) == text, (
                "INV-006: the trailing-whitespace / end-of-file-fixer hooks change the map: "
                f"{[ln for ln in text.split(chr(10)) if ln != ln.rstrip(' \t')][:3]!r}"
            )

    check()
