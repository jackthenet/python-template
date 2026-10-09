"""Unit tests for the structure-map generator: the unreadable-source contract (T-002).

Spec: `docs/specs/structure-map.md`. This file holds the §11 rows for AC-006, AC-007 and
EDGE-003/004/005 (placement fixed by Q-10: parser/CLI internals in `tests/unit/test_make_map.py`).

Every witness drives the generator as a **subprocess** over a throwaway tree in `tmp_path`.
`scripts/make_map.py` does not exist until T-002's Phase 4, and a module-level import of it would
turn the whole file into a collection error — a setup error is not a valid RED (test contract
sanity check). The CLI is the generator's public contract (REQ-002/REQ-004/REQ-006), so these
assertions hold whatever internal structure Phase 4 picks.
"""

from __future__ import annotations

import ast
import contextlib
import importlib
import os
import re
import subprocess
import sys
from collections.abc import Iterator, Mapping, Sequence
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_GENERATOR = _REPO_ROOT / "scripts" / "make_map.py"

# Sources the running interpreter (CPython 3.14, REQ-007) cannot parse. Names chosen so the
# expected sorted order differs from the creation order.
_UNPARSEABLE: dict[str, str] = {
    "src/z_bad.py": "def f(:\n    return 1\n",
    "src/a_bad.py": "class C(:\n    pass\n",
}

# REQ-004 exit codes these witnesses assert.
_EXIT_USAGE = 2
_EXIT_UNREADABLE = 4

# Exception types that satisfy REQ-006's "could not be read" branch (OSError family).
_OSError_FAMILY: frozenset[str] = frozenset({"OSError", "PermissionError", "IsADirectoryError", "BlockingIOError"})


def _run_generator(root: Path | str, out: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    """Run the generator over `root`, writing/checking `out`.

    `root` may be a `Path` or a path string, so NFR-007 can pass the same tree through two
    spellings of `--root`.

    `pytest.fail` on a missing module: the unimplemented generator is the behavior under test, so
    it must surface as a test failure, never as a collection/import error. `encoding="utf-8"` is
    explicit because the Windows default codec is cp1252 (PROBLEMS.md P-67).
    """
    if not _GENERATOR.is_file():
        pytest.fail(f"{_GENERATOR} does not exist — T-002 Phase 4 has not implemented the generator")
    return subprocess.run(
        [sys.executable, str(_GENERATOR), "--root", str(root), "--out", str(out), *extra],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=_REPO_ROOT,
        check=False,
    )


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
        proc = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, encoding="utf-8", check=False)
        if proc.returncode != 0:
            pytest.fail(f"git {' '.join(args)} failed in {root}: {proc.stderr.strip()}")
    return root


def _reported_paths(proc: subprocess.CompletedProcess[str], expected: Sequence[str], exception: str) -> list[str]:
    """Check REQ-006's report: one line per offending path, sorted, `--root`-relative, naming the
    exception type, and nothing else printed."""
    failures: list[str] = []
    lines = [line for line in proc.stderr.splitlines() if line.strip()]
    if len(lines) != len(expected):
        failures.append(f"stderr has {len(lines)} line(s) {lines!r}, expected one per offending path")
    for path in expected:
        hits = [line for line in lines if path in line]
        if len(hits) != 1:
            failures.append(f"{path} reported {len(hits)} time(s) in {lines!r}")
        elif exception not in hits[0]:
            failures.append(f"the line for {path} does not name {exception}: {hits[0]!r}")
    positions = {path: proc.stderr.find(path) for path in expected if path in proc.stderr}
    if list(positions) != sorted(positions, key=lambda path: positions[path]):
        failures.append(f"the reported paths are not sorted: {list(positions)}")
    return failures


def _is_unparseable(source: str) -> bool:
    """True when the running interpreter rejects `source` (the fixture validity check for EDGE-003)."""
    with contextlib.suppress(SyntaxError, ValueError):
        ast.parse(source)
        return False
    return True


@contextlib.contextmanager
def _unopenable(path: Path) -> Iterator[None]:
    """Make a real file unreadable by another process.

    Windows: an exclusive byte-range lock — the sharing violation EDGE-005 names. Elsewhere: mode
    000 (CI runs as a non-root user).
    """
    if sys.platform == "win32":
        msvcrt = importlib.import_module("msvcrt")
        with path.open("rb") as handle:
            msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, path.stat().st_size)
            try:
                yield
            finally:
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, path.stat().st_size)
    else:
        mode = path.stat().st_mode
        path.chmod(0)
        try:
            yield
        finally:
            path.chmod(mode)


def test_ac_006_parse_error_is_hard_failure(tmp_path: Path) -> None:
    """AC-006 (REQ-006): an unparseable file is a hard failure — exit 4, every offending
    `--root`-relative path reported once and sorted with the exception type, no output file
    written, and a pre-existing output file left byte-unchanged."""
    root = _git_tree(tmp_path / "tree", {"src/good.py": "x = 1\n", **_UNPARSEABLE})
    existing = tmp_path / "existing.md"
    existing.write_bytes(b"pre-existing bytes\n")
    before = existing.read_bytes()

    proc = _run_generator(root, existing)
    fresh = tmp_path / "fresh.md"
    second = _run_generator(root, fresh)

    failures: list[str] = []
    if proc.returncode != _EXIT_UNREADABLE:
        failures.append(f"clause 1: exit {proc.returncode}, expected 4 (stdout {proc.stdout!r})")
    failures += [f"clause 2: {f}" for f in _reported_paths(proc, sorted(_UNPARSEABLE), "SyntaxError")]
    if proc.stdout.strip():
        failures.append(f"clause 3: generate mode prints nothing, got stdout {proc.stdout!r}")
    if existing.read_bytes() != before:
        failures.append("clause 4: the pre-existing output file was modified")
    if fresh.exists():
        failures.append(f"clause 5: no output file may be written (second run exit {second.returncode})")
    assert not failures, "\n".join(failures)


def test_ac_007_grammar_is_the_running_interpreter(tmp_path: Path) -> None:
    """AC-007 (REQ-007): the supported grammar is the running interpreter's — syntax it accepts is
    not an unparseable file, and the CLI exposes no grammar/`feature_version` option."""
    modern = "type Alias = int | None\n\n\ndef first[T](items: list[T]) -> T:\n    return items[0]\n"
    ast.parse(modern)  # fixture validity: the running interpreter must accept this
    root = _git_tree(tmp_path / "tree", {"src/modern.py": modern, "src/plain.py": "x = 1\n"})
    out = tmp_path / "STRUCTURE.md"

    accepted = _run_generator(root, out)
    pinned = _run_generator(root, out, "--feature-version", "3.12")
    help_text = _run_generator(root, out, "--help")

    failures: list[str] = []
    if accepted.returncode != 0:
        failures.append(
            f"clause 1: exit {accepted.returncode}, expected 0 for syntax the interpreter accepts: {accepted.stderr!r}"
        )
    if pinned.returncode != _EXIT_USAGE:
        failures.append(
            f"clause 2: --feature-version exits {pinned.returncode}, expected 2 (no grammar option, REQ-002)"
        )
    if help_text.returncode != 0:
        failures.append(f"clause 3: --help exits {help_text.returncode}, expected 0")
    if "feature_version" in help_text.stdout or "grammar" in help_text.stdout.lower():
        failures.append(f"clause 4: --help advertises a grammar option: {help_text.stdout!r}")
    assert not failures, "\n".join(failures)


def test_edge_003_newer_syntax_is_hard_failure(tmp_path: Path) -> None:
    """EDGE-003 (REQ-006/REQ-007): a file using syntax newer than the running interpreter is a
    `SyntaxError` → path reported, exit 4, no output written."""
    source = "def f(a,) -> int:\n    return a\n\n\nclass C[:\n    pass\n"
    if not _is_unparseable(source):
        pytest.fail("the EDGE-003 fixture parses on the running interpreter — invalid test data")
    root = _git_tree(tmp_path / "tree", {"src/good.py": "x = 1\n", "src/future.py": source})
    out = tmp_path / "STRUCTURE.md"

    proc = _run_generator(root, out)

    failures: list[str] = []
    if proc.returncode != _EXIT_UNREADABLE:
        failures.append(f"clause 1: exit {proc.returncode}, expected 4")
    failures += [f"clause 2: {f}" for f in _reported_paths(proc, ["src/future.py"], "SyntaxError")]
    if out.exists():
        failures.append("clause 3: no output file may be written")
    assert not failures, "\n".join(failures)


def test_edge_004_non_utf8_is_hard_failure(tmp_path: Path) -> None:
    """EDGE-004 (REQ-006): a file that is not valid UTF-8 raises `UnicodeDecodeError` → the same
    single hard failure: path reported, exit 4, no output written."""
    root = _git_tree(tmp_path / "tree", {"src/good.py": "x = 1\n"})
    (root / "src" / "latin.py").write_bytes(b"note = '\xff\xfe\xfa'\n")
    try:
        (root / "src" / "latin.py").read_text(encoding="utf-8")
    except UnicodeDecodeError:
        pass
    else:
        pytest.fail("the EDGE-004 fixture decodes as UTF-8 — invalid test data")
    out = tmp_path / "STRUCTURE.md"

    proc = _run_generator(root, out)

    failures: list[str] = []
    if proc.returncode != _EXIT_UNREADABLE:
        failures.append(f"clause 1: exit {proc.returncode}, expected 4")
    failures += [f"clause 2: {f}" for f in _reported_paths(proc, ["src/latin.py"], "UnicodeDecodeError")]
    if out.exists():
        failures.append("clause 3: no output file may be written")
    assert not failures, "\n".join(failures)


def test_edge_005_unopenable_file_is_hard_failure(tmp_path: Path) -> None:
    """EDGE-005 (REQ-006): a file that cannot be opened (`OSError`, here a Windows sharing
    violation) is the same hard failure: path reported, exit 4, no output written."""
    if os.name != "nt" and hasattr(os, "geteuid") and os.geteuid() == 0:
        pytest.skip("mode 000 does not block root — the fixture cannot make the file unreadable")
    root = _git_tree(tmp_path / "tree", {"src/good.py": "x = 1\n", "src/locked.py": "x = 2\n"})
    out = tmp_path / "STRUCTURE.md"

    with _unopenable(root / "src" / "locked.py"):
        proc = _run_generator(root, out)

    failures: list[str] = []
    if proc.returncode != _EXIT_UNREADABLE:
        failures.append(f"clause 1: exit {proc.returncode}, expected 4 (stderr {proc.stderr!r})")
    reported = [line for line in proc.stderr.splitlines() if "src/locked.py" in line]
    if len(reported) != 1:
        failures.append(f"src/locked.py reported {len(reported)} time(s): {proc.stderr!r}")
    elif not any(name in reported[0] for name in _OSError_FAMILY):
        failures.append(f"the line for src/locked.py names no OSError-family type: {reported[0]!r}")
    if out.exists():
        failures.append("clause 3: no output file may be written")
    assert not failures, "\n".join(failures)


# --- T-003: module header + summary, exports line, path form ---------------------------------
# (REQ-012/REQ-013/REQ-020, EDGE-001/EDGE-002/EDGE-013, NFR-007)

# One fixture tree for the T-003 unit set: a module with a docstring (4 lines, of which 3 are
# non-blank, so the header count cannot be a non-blank/node count), one with no docstring, one with
# only a comment, an empty file, and two packages covering both exports branches of REQ-012.
_T003_FILES: dict[str, str] = {
    "src/all_pkg/__init__.py": '__all__ = ["Zeta", "Alpha"]\n\nfrom .alpha import Alpha\nfrom .zeta import Zeta\n',
    "src/all_pkg/alpha.py": '"""The alpha module."""\n',
    "src/all_pkg/zeta.py": '"""The zeta module."""\n',
    "src/pub_pkg/__init__.py": '"""Public imports, no __all__."""\n\nfrom .beta import Beta\nfrom .gamma import Gamma\n',
    "src/pub_pkg/beta.py": '"""Beta."""\n',
    "src/pub_pkg/gamma.py": '"""Gamma."""\n',
    "src/nopub_pkg/__init__.py": '"""Neither __all__ nor public imports."""\n\nfrom ._internal import _helper\n',
    "src/nopub_pkg/_internal.py": '"""Internal helper."""\n\n_helper = 1\n',
    "src/with_doc.py": '"""A module with a docstring."""\n\nVALUE = 1\nOTHER = 2\n',
    "src/no_doc.py": "VALUE = 1\nOTHER = 2\n",
    "src/comment_only.py": "# A comment, not a docstring.\nVALUE = 1\nOTHER = 2\n",
    "src/empty.py": "",
}

# REQ-020: the path forms that must never appear in a map rendered from a --root-relative file set.
_NOT_PATH_FORM: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("a Windows path separator", re.compile(r"\\")),
    ("a drive letter or UNC path", re.compile(r"[A-Za-z]:[\\/]")),
    ("an absolute POSIX path", re.compile(r"(^|\s)/[A-Za-z0-9_.]")),
)

# The index of the summary line inside a module block (block[0] is the REQ-013 header).
_SUMMARY_LINE = 1


def _line_count(source: str) -> int:
    """The number of lines in a fixture source — the count REQ-013's module header carries."""
    return len(source.splitlines())


def _map_text(out: Path, proc: subprocess.CompletedProcess[str]) -> str:
    """The generated map's text, or a failure naming the run that produced no file."""
    if not out.is_file():
        pytest.fail(f"no map file at {out} (exit {proc.returncode}): {proc.stdout!r} {proc.stderr!r}")
    return out.read_text(encoding="utf-8")


def _module_block(map_text: str, path: str) -> list[str]:
    """One module's section: its `#### ` header plus its body lines, up to the next header."""
    lines = map_text.splitlines()
    start = next((index for index, line in enumerate(lines) if line.startswith(f"#### {path} ")), None)
    if start is None:
        return []
    block = [lines[start]]
    for line in lines[start + 1 :]:
        if line.startswith(("## ", "### ", "#### ")):
            break
        if line.strip():
            block.append(line.strip())
    return block


def _group_block(map_text: str, dir_path: str) -> list[str]:
    """The lines of the group whose `### ` header ends with `dir_path`, up to the next group header."""
    lines = map_text.splitlines()
    start = next(
        (index for index, line in enumerate(lines) if line.startswith("### ") and line.rstrip().endswith(dir_path)),
        None,
    )
    if start is None:
        return []
    body: list[str] = []
    for line in lines[start + 1 :]:
        if line.startswith(("## ", "### ")):
            break
        if line.strip():
            body.append(line.strip())
    return body


def _first_diff(left: bytes, right: bytes) -> str:
    """The first line pair in which two renders differ — a readable NFR-007 failure message."""
    a_lines, b_lines = left.decode("utf-8").splitlines(), right.decode("utf-8").splitlines()
    for index in range(max(len(a_lines), len(b_lines))):
        a_line = a_lines[index] if index < len(a_lines) else "<end of file>"
        b_line = b_lines[index] if index < len(b_lines) else "<end of file>"
        if a_line != b_line:
            return f"line {index + 1}: {a_line!r} vs {b_line!r}"
    return f"identical lines, different byte counts ({len(left)} vs {len(right)})"


def test_ac_013_module_header_and_summary(tmp_path: Path) -> None:
    """AC-013 (REQ-013): a module with a docstring renders `#### <path> (<N> lines)` carrying the
    file's own line count, followed by its summary line; a module without a docstring renders the
    header and no summary line."""
    root = _git_tree(tmp_path / "tree", _T003_FILES)
    out = tmp_path / "STRUCTURE.md"

    proc = _run_generator(root, out)
    text = _map_text(out, proc)
    failures: list[str] = []

    if proc.returncode != 0:
        failures.append(f"clause 1: exit {proc.returncode}: {proc.stderr!r}")
    documented = _module_block(text, "src/with_doc.py")
    expected_header = f"#### src/with_doc.py ({_line_count(_T003_FILES['src/with_doc.py'])} lines)"
    if documented[:1] != [expected_header]:
        failures.append(
            f"clause 1: the header is {documented[:1]!r}, expected {expected_header!r} — the file's line count"
        )
    if len(documented) <= _SUMMARY_LINE or "A module with a docstring." not in documented[_SUMMARY_LINE]:
        failures.append(f"clause 1: no summary line after the header: {documented!r}")

    undocumented = _module_block(text, "src/no_doc.py")
    if undocumented[:1] != ["#### src/no_doc.py (2 lines)"]:
        failures.append(f"clause 2: the header is {undocumented[:1]!r}, expected '#### src/no_doc.py (2 lines)'")
    if len(undocumented) > 1:
        failures.append(f"clause 2: a module with no docstring renders a summary line: {undocumented[1:]!r}")
    assert not failures, "\n".join(failures)


def test_edge_001_missing_docstring_renders_no_summary(tmp_path: Path) -> None:
    """EDGE-001 (REQ-013, module half): a module with no docstring still renders its header — and
    renders no summary line, and the header carries no trailing colon."""
    root = _git_tree(tmp_path / "tree", _T003_FILES)
    out = tmp_path / "STRUCTURE.md"

    proc = _run_generator(root, out)
    text = _map_text(out, proc)
    failures: list[str] = []

    if proc.returncode != 0:
        failures.append(f"clause 1: exit {proc.returncode}: {proc.stderr!r}")
    for path, count in (("src/no_doc.py", 2), ("src/comment_only.py", 3)):
        block = _module_block(text, path)
        if block[:1] != [f"#### {path} ({count} lines)"]:
            failures.append(f"clause 2: {path} renders {block[:1]!r}, expected its header line")
        elif block[0].endswith(":"):
            failures.append(f"clause 3: {block[0]!r} ends with a colon")
        if len(block) > 1:
            failures.append(f"clause 2: {path} renders a summary line: {block[1:]!r}")
    assert not failures, "\n".join(failures)


def test_edge_002_empty_file_renders_header_only(tmp_path: Path) -> None:
    """EDGE-002 (REQ-013): an empty file renders `#### src/empty.py (0 lines)` and no symbol line,
    and is not an error — exit 0, nothing reported about it."""
    root = _git_tree(tmp_path / "tree", _T003_FILES)
    out = tmp_path / "STRUCTURE.md"

    proc = _run_generator(root, out)
    text = _map_text(out, proc)
    failures: list[str] = []

    if proc.returncode != 0:
        failures.append(f"clause 1: exit {proc.returncode}, an empty file is not an error: {proc.stderr!r}")
    block = _module_block(text, "src/empty.py")
    if block != ["#### src/empty.py (0 lines)"]:
        failures.append(f"clause 2: the empty module renders {block!r}, expected only its header with (0 lines)")
    if "empty.py" in proc.stderr:
        failures.append(f"clause 3: the empty file is reported on stderr: {proc.stderr!r}")
    assert not failures, "\n".join(failures)


def test_edge_013_package_without_exports(tmp_path: Path) -> None:
    """EDGE-013 (REQ-012): a package `__init__.py` with neither `__all__` nor public imports renders
    no `exports:` line; a package with public imports but no `__all__` renders those names, sorted."""
    root = _git_tree(tmp_path / "tree", _T003_FILES)
    out = tmp_path / "STRUCTURE.md"

    proc = _run_generator(root, out)
    text = _map_text(out, proc)
    failures: list[str] = []

    if proc.returncode != 0:
        failures.append(f"clause 1: exit {proc.returncode}: {proc.stderr!r}")
    for group in ("src/nopub_pkg/", "src/pub_pkg/"):
        if not _group_block(text, group):
            failures.append(f"clause 2: no group section for the package {group}")
    nopub = _group_block(text, "src/nopub_pkg/")
    if exports := [line for line in nopub if "exports:" in line]:
        failures.append(
            f"clause 2: {exports!r} — a package with neither __all__ nor public imports renders no exports line"
        )
    pub_exports = [line for line in _group_block(text, "src/pub_pkg/") if "exports:" in line]
    if len(pub_exports) != 1:
        failures.append(
            f"clause 3: {len(pub_exports)} exports line(s) for src/pub_pkg/: {_group_block(text, 'src/pub_pkg/')!r}"
        )
    elif "Beta" not in pub_exports[0] or "Gamma" not in pub_exports[0]:
        failures.append(f"clause 3: {pub_exports[0]!r} does not list the public names the package imports")
    elif pub_exports[0].index("Beta") > pub_exports[0].index("Gamma"):
        failures.append(f"clause 3: {pub_exports[0]!r} is not sorted")
    assert not failures, "\n".join(failures)


def test_ac_020_paths_are_relative_posix(tmp_path: Path) -> None:
    """AC-020 (REQ-020): every path in the map is --root-relative with '/' separators — no
    backslash, drive letter, UNC path or absolute path — whatever spelling `--root` had on this
    host, and every module header names the fixture's relative path."""
    root = _git_tree(tmp_path / "tree", _T003_FILES)
    out = tmp_path / "STRUCTURE.md"

    proc = _run_generator(root, out)
    text = _map_text(out, proc)
    failures: list[str] = []

    for label, pattern in _NOT_PATH_FORM:
        if hit := pattern.search(text):
            failures.append(f"clause 1: the map contains {label}: {hit.group(0)!r}")
    for absolute in (str(root), root.as_posix(), str(root.parent)):
        if absolute in text:
            failures.append(f"clause 2: the absolute host path {absolute!r} appears in the map")
    headers = {line for line in text.splitlines() if line.startswith("#### ")}
    expected = {f"#### {path} ({_line_count(source)} lines)" for path, source in _T003_FILES.items()}
    if headers != expected:
        failures.append(
            f"clause 3: module headers are not the --root-relative posix paths: "
            f"missing {sorted(expected - headers)!r}, unexpected {sorted(headers - expected)!r}"
        )
    assert not failures, "\n".join(failures)


def test_nfr_007_output_identical_across_platforms(tmp_path: Path) -> None:
    """NFR-007 (REQ-020): the render is byte-identical for the same tree regardless of the host path
    it was rendered from — two trees at different absolute locations, and one tree reached through
    two spellings of `--root`, produce the same bytes, with LF newlines."""
    near = _git_tree(tmp_path / "one" / "tree", _T003_FILES)
    far = _git_tree(tmp_path / "a" / "b" / "c" / "d" / "elsewhere" / "tree", _T003_FILES)
    out_near, out_far, out_spelled = tmp_path / "near.md", tmp_path / "far.md", tmp_path / "spelled.md"

    runs = (
        ("same location", _run_generator(near, out_near)),
        ("other absolute location", _run_generator(far, out_far)),
        ("posix-spelled --root", _run_generator(near.as_posix(), out_spelled)),
    )
    near_bytes = out_near.read_bytes() if out_near.is_file() else b""
    failures: list[str] = []

    for label, proc in runs:
        if proc.returncode != 0:
            failures.append(f"clause 1: the {label} run exits {proc.returncode}: {proc.stderr!r}")
    if out_far.is_file() and near_bytes != out_far.read_bytes():
        failures.append(
            f"clause 2: the same tree at two absolute locations renders different bytes: {_first_diff(near_bytes, out_far.read_bytes())}"
        )
    if out_spelled.is_file() and near_bytes != out_spelled.read_bytes():
        failures.append(
            f"clause 3: --root spelled with host separators vs posix separators renders different bytes: {_first_diff(near_bytes, out_spelled.read_bytes())}"
        )
    if b"\r" in near_bytes:
        failures.append("clause 4: the render is not LF-only")
    assert not failures, "\n".join(failures)
