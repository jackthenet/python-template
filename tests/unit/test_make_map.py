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


# --- T-004: symbol inventory, decorators, visibility, class fields, summaries ----------------
# (REQ-014/REQ-015/REQ-016/REQ-017/REQ-018, EDGE-011/EDGE-012)

# The constants REQ-017/REQ-018 hardcode, named here so every witness states the rule it pins.
_FIELD_CAP = 15
_SUMMARY_LIMIT = 100
_ELLIPSIS = "…"
_MEMBER = "  - "  # REQ-014: a class member line (field, method, nested class) is a 2-space bullet
_NESTED = "    - "  # a nested class's own members sit at the next indent level


def _field_source(count: int, first: int = 1) -> str:
    """`count` annotated class-level assignments (`field_01 …`) at class-body indent: the REQ-017
    fixture body. Unannotated assignments and defaults are added by the callers that need them."""
    return "".join(f"    field_{index:02d}: str\n" for index in range(first, first + count))


def _field_symbol_lines(count: int, first: int = 1) -> list[str]:
    """The REQ-017 rendering of `_field_source`: one `name: annotation` line per field, no default."""
    return [f"{_MEMBER}`field_{index:02d}: str`" for index in range(first, first + count)]


def _t004_tree(tmp_path: Path, files: Mapping[str, str]) -> Path:
    """A git tree of T-004 fixture modules, each checked to parse first (fixture validity: a
    fixture the generator cannot parse would be an EDGE-003 hard failure, not a symbol witness)."""
    for path, source in files.items():
        try:
            ast.parse(source)
        except SyntaxError as error:
            pytest.fail(f"the T-004 fixture {path} does not parse — invalid test data: {error}")
    return _git_tree(tmp_path / "tree", files)


def _module_body(map_text: str, path: str) -> list[str]:
    """One module's rendered body: every line after its `#### ` header up to the next header,
    exactly as rendered — unlike `_module_block`, the two-space member indent is preserved."""
    lines = map_text.splitlines()
    start = next((index for index, line in enumerate(lines) if line.startswith(f"#### {path} ")), None)
    if start is None:
        return []
    body: list[str] = []
    for line in lines[start + 1 :]:
        if line.startswith(("## ", "### ", "#### ")):
            break
        if line.strip():
            body.append(line)
    return body


def _symbol_lines(map_text: str, path: str) -> list[str]:
    """The REQ-014 symbol lines of one module, in rendered order, indent preserved."""
    return [line for line in _module_body(map_text, path) if line.lstrip().startswith("- ")]


def _all_symbol_lines(map_text: str) -> list[str]:
    """Every symbol line in the whole map — the scope of the "never rendered" clauses."""
    return [line for line in map_text.splitlines() if line.lstrip().startswith("- ")]


def _section_headers(map_text: str) -> list[str]:
    """The package (`### `) and module (`#### `) headers of a map — the AC-016 third clause
    compares these between two runs, so `--include-private` cannot add or hide a module."""
    return [line for line in map_text.splitlines() if line.startswith(("### ", "#### "))]


def _seq_failures(actual: list[str], expected: list[str], clause: str) -> list[str]:
    """One readable failure for an exact rendered-line-sequence comparison."""
    if actual == expected:
        return []
    rendered = "\n".join(repr(line) for line in actual)
    wanted = "\n".join(repr(line) for line in expected)
    return [f"clause {clause}: the rendered lines are\n{rendered}\nexpected\n{wanted}"]


_AC014_MODULE = """
import typing
from base import Base, Mixin

MODULE_VALUE = 1

if typing.TYPE_CHECKING:
    from collections.abc import Sequence


def spaced(  a : int ,b : str = "xy" ) -> None:
    'Spaced source formatting.'


async def fetch() -> None:
    'Fetch the remote map.'


class Widget(Base, Mixin):
    'A widget.'

    name: str
    size: int = 3
    unannotated = "not a field"

    def __init__(self, name: str) -> None:
        'Create a widget.'

    def resize(
        self,
        size: int,
        *,
        step: int = 4,
        data: dict[str, int] = {"alpha": 1, "beta": 2},
        exact: str = "0123456789abcdefgh",
        over: str = "0123456789abcdefghi",
    ) -> None:
        'Resize the widget.'


class Outer:
    'An outer widget.'

    class Inner:
        'A nested widget.'

        depth: int

        def build(self) -> int:
            'Build the inner widget.'


def items(pool: list[int] = [1, 2, 3, 4, 5, 6, 7]) -> None:
    'A long positional default.'


def make_widget() -> Widget:
    'Build a widget locally.'

    class Local:
        'A function-local class.'

    return Local()
"""

# The exact REQ-014 rendering of `_AC014_MODULE`: classes first (source order), then functions
# (source order) — so `spaced`/`fetch`, which come first in the source, render after the classes.
# The signature text is the `ast.unparse` rendering (`b: str='xy'`, `step: int=4`), not the source
# spacing, and a default whose unparsed text exceeds 20 characters (`data` 23, `over` 21, `pool` 21)
# is abbreviated to the `…` placeholder **in its own slot** — never dropped, so no neighbouring
# default shifts onto an earlier parameter — while the exactly-20-character default of `exact` is
# kept verbatim (REQ-014 v2, EDGE-017).
_AC014_LINES = [
    "- class `Widget(Base, Mixin)`: A widget.",
    f"{_MEMBER}`name: str`",
    f"{_MEMBER}`size: int`",
    f"{_MEMBER}`__init__(self, name: str) -> None`: Create a widget.",
    (
        f"{_MEMBER}`resize(self, size: int, *, step: int=4, data: dict[str, int]={_ELLIPSIS}, "
        f"exact: str='0123456789abcdefgh', over: str={_ELLIPSIS}) -> None`: Resize the widget."
    ),
    "- class `Outer`: An outer widget.",
    f"{_MEMBER}class `Inner`: A nested widget.",
    f"{_NESTED}`depth: int`",
    f"{_NESTED}`build(self) -> int`: Build the inner widget.",
    "- def `spaced(a: int, b: str='xy') -> None`: Spaced source formatting.",
    "- def `async fetch() -> None`: Fetch the remote map.",
    f"- def `items(pool: list[int]={_ELLIPSIS}) -> None`: A long positional default.",
    "- def `make_widget() -> Widget`: Build a widget locally.",
]

# (needle, must-be-present) — the REQ-014 default rule at its boundary, spelled out so a wrong
# implementation is attributed to the clause it breaks rather than only to the sequence check.
_AC014_DEFAULTS: tuple[tuple[str, bool], ...] = (
    ("step: int=4", True),  # 1 character: shown
    ("b: str='xy'", True),  # 4 characters: shown
    ("exact: str='0123456789abcdefgh'", True),  # exactly 20 characters: shown verbatim (Q-8)
    ("{'alpha': 1, 'beta': 2}", False),  # 23 characters: abbreviated, its text never rendered
    ("'0123456789abcdefghi'", False),  # 21 characters: abbreviated, its text never rendered
    ("[1, 2, 3, 4, 5, 6, 7]", False),  # 21 characters, positional: abbreviated, never shifted
    (f"data: dict[str, int]={_ELLIPSIS}", True),  # keyword-only over-long: `=…` in its own slot
    (f"over: str={_ELLIPSIS}", True),  # keyword-only over-long: the `=` separator survives
    (f"pool: list[int]={_ELLIPSIS}", True),  # positional over-long: the parameter keeps a default
)

# EDGE-017 (REQ-014 v2): every slot the amended edge case names, plus the two shapes that do not
# occur in the tracked tree (finding F-12) — a positional-only over-long default and a function
# whose *only* default is over-long. `keys` carries the F-08 trap: `need` has **no** default in the
# source, so a rule that abbreviates every entry would wrongly render it as optional.
_EDGE017_MODULE = """
def shift(a: int = 1, b: str = "xy", c: list[int] = [1, 2, 3, 4, 5, 6, 7]) -> None:
    'Shift the defaults.'


def only(pool: list[int] = [1, 2, 3, 4, 5, 6, 7]) -> None:
    'The only default in the module.'


def posonly(a: int = 1, b: str = "0123456789abcdefghij0", /) -> None:
    'A positional-only over-long default.'


def keys(*, need: int, k: int = 1, m: str = "0123456789abcdefghij0") -> None:
    'A keyword-only parameter with no default at all.'


def edge(exact: str = "0123456789abcdefgh") -> None:
    'A default of exactly 20 characters.'
"""

# The required rendering of `_EDGE017_MODULE`: the over-long default is abbreviated in its own slot
# in all three slots, the `/` marker survives, `need` stays default-free, and the 20-character
# boundary is unchanged.
_EDGE017_LINES = [
    f"- def `shift(a: int=1, b: str='xy', c: list[int]={_ELLIPSIS}) -> None`: Shift the defaults.",
    f"- def `only(pool: list[int]={_ELLIPSIS}) -> None`: The only default in the module.",
    f"- def `posonly(a: int=1, b: str={_ELLIPSIS}, /) -> None`: A positional-only over-long default.",
    (
        f"- def `keys(*, need: int, k: int=1, m: str={_ELLIPSIS}) -> None`: "
        "A keyword-only parameter with no default at all."
    ),
    "- def `edge(exact: str='0123456789abcdefgh') -> None`: A default of exactly 20 characters.",
]

# (needle, must-be-present) — the EDGE-017 clauses per slot, so a wrong implementation is
# attributed to the clause it breaks rather than only to the sequence check. The negative needles
# are the shift itself: `a`'s default on `b`, and `b`'s default on `c`.
_EDGE017_NEEDLES: tuple[tuple[str, bool], ...] = (
    (f"c: list[int]={_ELLIPSIS}", True),  # positional slot: abbreviated in its own slot
    (f"pool: list[int]={_ELLIPSIS}", True),  # a function whose only default is over-long keeps it
    (f"b: str={_ELLIPSIS}, /", True),  # positional-only slot, and the `/` marker survives
    (f"m: str={_ELLIPSIS}", True),  # keyword-only slot
    ("need: int,", True),  # a keyword-only parameter with no default stays default-free
    (f"need: int={_ELLIPSIS}", False),  # ... and is never given a placeholder default (F-08)
    ("b: str=1", False),  # `a`'s default never shifts onto `b`
    ("c: list[int]='xy'", False),  # `b`'s default never shifts onto `c`
    ("exact: str='0123456789abcdefgh'", True),  # exactly 20 characters: verbatim, threshold intact
)

_AC015_MODULE = """
import pytest
from backend.logging import logged, logged_class
from functools import cache, lru_cache
from typing import override


@logged_class
class Registry:
    'A registry of entries.'

    entries: int

    @property
    def count(self) -> int:
        'Number of entries.'

    @staticmethod
    def build() -> None:
        'Build nothing.'

    @classmethod
    def named(cls, name: str) -> None:
        'Name nothing.'

    @override
    def to_text(self) -> str:
        'Render it.'


@logged
def helper() -> None:
    'A helper.'


@logged
@cache
def stacked() -> None:
    'Stacked decorators.'


@pytest.fixture
def backend_name() -> str:
    'The backend name.'


@lru_cache(maxsize=8)
def cached(value: int) -> int:
    'A cached value.'
"""

# A decorator that is not a plain name or attribute chain renders as its `ast.unparse` text.
_AC015_CALL_DECORATOR = "@lru_cache(maxsize=8)"

_AC015_LINES = [
    "- @logged_class class `Registry`: A registry of entries.",
    f"{_MEMBER}`entries: int`",
    f"{_MEMBER}@property `count(self) -> int`: Number of entries.",
    f"{_MEMBER}@staticmethod `build() -> None`: Build nothing.",
    f"{_MEMBER}@classmethod `named(cls, name: str) -> None`: Name nothing.",
    f"{_MEMBER}@override `to_text(self) -> str`: Render it.",
    "- @logged def `helper() -> None`: A helper.",
    "- @logged @cache def `stacked() -> None`: Stacked decorators.",
    "- @pytest.fixture def `backend_name() -> str`: The backend name.",
    f"- {_AC015_CALL_DECORATOR} def `cached(value: int) -> int`: A cached value.",
]

_AC016_MODULE = """
class Widget:
    'A widget.'

    def __init__(self) -> None:
        'Create a widget.'

    def __repr__(self) -> str:
        'Render the widget.'

    def _internal(self) -> None:
        'Internal work.'

    def public(self) -> None:
        'Public work.'


class _Helper:
    'A helper class.'

    def go(self) -> None:
        'Go.'


def _private() -> None:
    'A private function.'


def public_fn() -> None:
    'A public function.'
"""

_AC016_PRIVATE_MODULE = """
def visible_in_private_module() -> None:
    'Rendered with and without the flag.'
"""

_AC016_PACKAGE_INIT = """
def package_init_symbol() -> None:
    'Rendered with and without the flag.'
"""

_AC016_PACKAGE_MODULE = """
def package_inner_symbol() -> None:
    'Rendered with and without the flag.'
"""

_AC016_FILES: dict[str, str] = {
    "src/vis.py": _AC016_MODULE,
    "src/_hidden.py": _AC016_PRIVATE_MODULE,
    "src/_pkg/__init__.py": _AC016_PACKAGE_INIT,
    "src/_pkg/inner.py": _AC016_PACKAGE_MODULE,
}

_AC016_LINES_DEFAULT = [
    "- class `Widget`: A widget.",
    f"{_MEMBER}`__init__(self) -> None`: Create a widget.",
    f"{_MEMBER}`__repr__(self) -> str`: Render the widget.",
    f"{_MEMBER}`public(self) -> None`: Public work.",
    "- def `public_fn() -> None`: A public function.",
]

_AC016_LINES_PRIVATE = [
    "- class `Widget`: A widget.",
    f"{_MEMBER}`__init__(self) -> None`: Create a widget.",
    f"{_MEMBER}`__repr__(self) -> str`: Render the widget.",
    f"{_MEMBER}`_internal(self) -> None`: Internal work.",
    f"{_MEMBER}`public(self) -> None`: Public work.",
    "- class `_Helper`: A helper class.",
    f"{_MEMBER}`go(self) -> None`: Go.",
    "- def `_private() -> None`: A private function.",
    "- def `public_fn() -> None`: A public function.",
]

# The symbols the flag alone reveals — the difference between the two renderings of `src/vis.py`.
_AC016_PRIVATE_ONLY = [line for line in _AC016_LINES_PRIVATE if line not in _AC016_LINES_DEFAULT]

# The `_name` modules and packages the flag must never hide or add (REQ-016 third clause).
_AC016_PRIVATE_PATHS = ("src/_hidden.py", "src/_pkg/__init__.py", "src/_pkg/inner.py")

_AC017_MODULE = (
    "from pydantic import Field\n"
    "\n"
    "\n"
    "class Settings:\n"
    "    'Settings model.'\n"
    "\n"
    '    alpha: str = Field(default="a")\n'
    "    beta: int\n"
    "    gamma: bool = True\n"
    + _field_source(12, first=4)  # field_04 … field_15: the cap boundary
    + '    unannotated = "not a field"\n'  # not a field, and not counted by the cap
    + _field_source(2, first=16)  # field_16, field_17: elided by the cap
)

_AC017_FIELD_LINES = [
    f"{_MEMBER}`alpha: str`",
    f"{_MEMBER}`beta: int`",
    f"{_MEMBER}`gamma: bool`",
    *_field_symbol_lines(12, first=4),
]

_AC017_LINES = [
    "- class `Settings`: Settings model.",
    *_AC017_FIELD_LINES,
    f"{_MEMBER}{_ELLIPSIS} +2 fields",
]

# (class name, annotated fields, elided count) — EDGE-011 at the cap and past it.
_EDGE011_CLASSES: tuple[tuple[str, int, int], ...] = (
    ("AtCap", _FIELD_CAP, 0),
    ("OverByOne", _FIELD_CAP + 1, 1),
    ("OverByFive", _FIELD_CAP + 5, 5),
)

_EDGE011_MODULE = "".join(
    f"class {name}:\n    'The {name} model.'\n\n{_field_source(count)}\n" for name, count, _ in _EDGE011_CLASSES
)

_EDGE011_LINES = [
    line
    for name, count, elided in _EDGE011_CLASSES
    for line in [
        f"- class `{name}`: The {name} model.",
        *_field_symbol_lines(min(count, _FIELD_CAP)),
        *([f"{_MEMBER}{_ELLIPSIS} +{elided} fields"] if elided else []),
    ]
]

_AC018_MODULE = """
'Module summary with `backticks`   and   spaces.'


def multi() -> None:
    '''First   logical line
    spanning   physical lines
    with `backticks` inside.

    Second paragraph, never rendered.
    '''


def empty_doc() -> None:
    ''


def no_doc() -> None:
    pass


class Undocumented:
    pass
"""

_AC018_MODULE_SUMMARY = "Module summary with backticks and spaces."
_AC018_LINES = [
    "- class `Undocumented`",
    "- def `multi() -> None`: First logical line spanning physical lines with backticks inside.",
    "- def `empty_doc() -> None`",
    "- def `no_doc() -> None`",
]

# EDGE-012: the raw docstring first line has backticks and doubled spaces inside the first 100
# characters, so normalizing must happen before the truncation is measured.
_EDGE012_RAW = (
    "Normalizing `backticks` and   spaces   first, this summary keeps running well past "
    "the one hundred character limit so the marker must appear."
)
_EDGE012_NORMALIZED = (
    "Normalizing backticks and spaces first, this summary keeps running well past "
    "the one hundred character limit so the marker must appear."
)
_EDGE012_AT_LIMIT = (
    "Exactly one hundred characters of normalized summary text, no more and no less, so no marker appears"
)

_EDGE012_MODULE = (
    f"def long_summary() -> None:\n    '{_EDGE012_RAW}'\n\ndef exactly_limit() -> None:\n    '{_EDGE012_AT_LIMIT}'\n"
)

_EDGE012_LINES = [
    f"- def `long_summary() -> None`: {_EDGE012_NORMALIZED[:_SUMMARY_LIMIT]}{_ELLIPSIS}",
    f"- def `exactly_limit() -> None`: {_EDGE012_AT_LIMIT}",
]


def test_ac_014_symbol_inventory_and_unparsed_signatures(tmp_path: Path) -> None:
    """AC-014 (REQ-014): a module's classes render before its functions (each group in source
    order), a class's fields before its methods, in the stated line form with `ast.unparse`
    signatures — `async ` kept inside the backticks, a nested class as a member line with its own
    members one level deeper, a parameter default of ≤ 20 characters shown verbatim while a longer
    one is abbreviated to the `…` placeholder in its own slot (EDGE-017) — while a function-local
    class and the module's assignments and imports never render."""
    root = _t004_tree(tmp_path, {"src/inventory.py": _AC014_MODULE})
    out = tmp_path / "STRUCTURE.md"

    proc = _run_generator(root, out)
    text = _map_text(out, proc)
    lines = _symbol_lines(text, "src/inventory.py")
    failures: list[str] = []

    if proc.returncode != 0:
        failures.append(f"clause 1: exit {proc.returncode}: {proc.stderr!r}")
    failures += _seq_failures(lines, _AC014_LINES, "1")
    joined = "\n".join(lines)
    for needle, present in _AC014_DEFAULTS:
        if (needle in joined) is not present:
            failures.append(
                f"clause 2: {needle!r} {'rendered' if present else 'omitted'}, expected the opposite: {joined!r}"
            )
    for never in ("Local", "A function-local class.", "MODULE_VALUE", "Sequence", "unannotated"):
        if any(never in line for line in _all_symbol_lines(text)):
            failures.append(f"clause 3: {never!r} is rendered — it is not a module- or class-level symbol")
    if len(lines) != len(set(lines)):
        failures.append(f"clause 4: a symbol is rendered more than once: {lines!r}")
    assert not failures, "\n".join(failures)


def test_edge_017_over_long_default_keeps_its_slot(tmp_path: Path) -> None:
    """EDGE-017 (REQ-014): a parameter default whose unparsed text exceeds 20 characters is
    abbreviated to the `…` placeholder in its own slot — positional, positional-only and
    keyword-only alike, including a function whose only default is over-long — so no neighbouring
    default shifts onto an earlier parameter, a keyword-only parameter that has no default is
    never given one, and a default of exactly 20 characters still renders verbatim."""
    root = _t004_tree(tmp_path, {"src/edge017.py": _EDGE017_MODULE})
    out = tmp_path / "STRUCTURE.md"

    proc = _run_generator(root, out)
    text = _map_text(out, proc)
    lines = _symbol_lines(text, "src/edge017.py")
    failures: list[str] = []

    if proc.returncode != 0:
        failures.append(f"clause 1: exit {proc.returncode}: {proc.stderr!r}")
    failures += _seq_failures(lines, _EDGE017_LINES, "1")
    joined = "\n".join(lines)
    for needle, present in _EDGE017_NEEDLES:
        if (needle in joined) is not present:
            failures.append(
                f"clause 2: {needle!r} is {'rendered' if needle in joined else 'absent'}, "
                f"expected the opposite: {joined!r}"
            )
    assert not failures, "\n".join(failures)


def test_ac_015_decorators_render_as_prefix(tmp_path: Path) -> None:
    """AC-015 (REQ-015): every decorator renders as a compact `@name` prefix before the
    `class`/`def`/signature token in source order — `@logged_class`, `@property`, `@staticmethod`,
    `@classmethod`, `@override`, `@pytest.fixture`, a stacked pair — and a decorator call renders
    as its `ast.unparse` text."""
    root = _t004_tree(tmp_path, {"src/deco.py": _AC015_MODULE})
    out = tmp_path / "STRUCTURE.md"

    proc = _run_generator(root, out)
    text = _map_text(out, proc)
    lines = _symbol_lines(text, "src/deco.py")
    failures: list[str] = []

    if proc.returncode != 0:
        failures.append(f"clause 1: exit {proc.returncode}: {proc.stderr!r}")
    failures += _seq_failures(lines, _AC015_LINES, "1")
    for name in ("logged_class", "property", "staticmethod", "classmethod", "override", "pytest.fixture"):
        if not any(line.lstrip().startswith(f"- @{name} ") for line in lines):
            failures.append(f"clause 2: no line carries the @{name} decorator prefix: {lines!r}")
    if not any(_AC015_CALL_DECORATOR in line for line in lines):
        failures.append(f"clause 3: the decorator call is not rendered as its ast.unparse text: {lines!r}")
    assert not failures, "\n".join(failures)


def _ac016_dunder_failures(default_text: str, private_text: str) -> list[str]:
    """AC-016 clause 1: each dunder renders exactly once in both renders."""
    failures: list[str] = []
    for needle in ("__init__(self) -> None", "__repr__(self) -> str"):
        for label, text in (("default", default_text), ("--include-private", private_text)):
            if sum(needle in line for line in _symbol_lines(text, "src/vis.py")) != 1:
                failures.append(f"clause 1: {needle!r} is not rendered exactly once {label}: {text!r}")
    return failures


def _ac016_private_only_failures(default_text: str, private_text: str) -> list[str]:
    """AC-016 clause 2: the `_name` symbols render only with `--include-private`."""
    failures: list[str] = []
    for needle in _AC016_PRIVATE_ONLY:
        if any(needle == line for line in _all_symbol_lines(default_text)):
            failures.append(f"clause 2: {needle!r} renders without --include-private")
        if not any(needle == line for line in _all_symbol_lines(private_text)):
            failures.append(f"clause 2: {needle!r} does not render with --include-private")
    return failures


def _ac016_module_header_failures(default_text: str, private_text: str) -> list[str]:
    """AC-016 clause 3: the `_name` module and package headers render identically with and without the flag."""
    failures: list[str] = []
    for header in _AC016_PRIVATE_PATHS:
        for label, text in (("default", default_text), ("--include-private", private_text)):
            if not any(line.startswith(f"#### {header} ") for line in text.splitlines()):
                failures.append(f"clause 3: the module header for {header} is missing {label}")
    if _section_headers(default_text) != _section_headers(private_text):
        failures.append(
            f"clause 3: --include-private changed the rendered modules/packages: "
            f"{_section_headers(default_text)!r} vs {_section_headers(private_text)!r}"
        )
    return failures


def test_ac_016_private_symbols_and_dunders(tmp_path: Path) -> None:
    """AC-016 (REQ-016): the dunders `__init__` and `__repr__` render with or without
    `--include-private`; `_helper`, `_Helper` and `_internal` render only with the flag; and the
    set of rendered modules and packages — including the `_name` module and the `_name` package —
    is identical with and without it."""
    root = _t004_tree(tmp_path, _AC016_FILES)
    out = tmp_path / "STRUCTURE.md"

    default = _run_generator(root, out)
    default_text = _map_text(out, default)
    private = _run_generator(root, out, "--include-private")
    private_text = _map_text(out, private)
    failures: list[str] = []

    if default.returncode != 0 or private.returncode != 0:
        failures.append(f"clause 1: exit {default.returncode} / {private.returncode}")
    failures += _seq_failures(_symbol_lines(default_text, "src/vis.py"), _AC016_LINES_DEFAULT, "1")
    failures += _seq_failures(_symbol_lines(private_text, "src/vis.py"), _AC016_LINES_PRIVATE, "1")
    failures += _ac016_dunder_failures(default_text, private_text)
    failures += _ac016_private_only_failures(default_text, private_text)
    failures += _ac016_module_header_failures(default_text, private_text)
    assert not failures, "\n".join(failures)


def test_ac_017_class_fields_capped_untyped_omitted(tmp_path: Path) -> None:
    """AC-017 (REQ-017): each annotated class field renders as `name: annotation` with no default
    and no `Field(...)` payload, in source order; the unannotated assignment renders neither as a
    field nor as part of the elided count; and the class with 17 annotated fields renders 15 field
    lines plus `… +2 fields`."""
    root = _t004_tree(tmp_path, {"src/fields.py": _AC017_MODULE})
    out = tmp_path / "STRUCTURE.md"

    proc = _run_generator(root, out)
    text = _map_text(out, proc)
    lines = _symbol_lines(text, "src/fields.py")
    failures: list[str] = []

    if proc.returncode != 0:
        failures.append(f"clause 1: exit {proc.returncode}: {proc.stderr!r}")
    failures += _seq_failures(lines, _AC017_LINES, "1")
    for needle in ("Field(", "default=", "unannotated", "field_16", "field_17"):
        if any(needle in line for line in lines):
            failures.append(f"clause 2: {needle!r} is rendered in a field line")
    rendered_fields = [line for line in lines if line in _AC017_FIELD_LINES]
    if len(rendered_fields) != _FIELD_CAP:
        failures.append(
            f"clause 3: {len(rendered_fields)} field lines rendered, expected exactly {_FIELD_CAP} of the 17"
        )
    assert not failures, "\n".join(failures)


def test_ac_018_summary_normalization(tmp_path: Path) -> None:
    """AC-018 (REQ-018): a docstring whose first logical line spans several physical lines and
    contains backticks renders as that line with whitespace runs collapsed and backticks removed —
    for the module summary line as well as for a symbol — while an empty docstring, no docstring at
    all, and a second paragraph render no summary and no trailing `:`."""
    root = _t004_tree(tmp_path, {"src/summ.py": _AC018_MODULE})
    out = tmp_path / "STRUCTURE.md"

    proc = _run_generator(root, out)
    text = _map_text(out, proc)
    body = _module_body(text, "src/summ.py")
    lines = _symbol_lines(text, "src/summ.py")
    failures: list[str] = []

    if proc.returncode != 0:
        failures.append(f"clause 1: exit {proc.returncode}: {proc.stderr!r}")
    failures += _seq_failures(lines, _AC018_LINES, "1")
    if not body or _AC018_MODULE_SUMMARY not in body[0]:
        failures.append(f"clause 2: the module summary line is not normalized: {body[:1]!r}")
    if any("`backticks`" in line or "   " in line for line in lines):
        failures.append(f"clause 2: a summary keeps its backticks or its doubled spaces: {lines!r}")
    for line in lines:
        if line.endswith(":"):
            failures.append(f"clause 3: {line!r} ends with a colon although it has no summary")
    if "Second paragraph" in text:
        failures.append("clause 3: a docstring paragraph after the first logical line is rendered")
    assert not failures, "\n".join(failures)


def test_edge_011_field_cap_marker(tmp_path: Path) -> None:
    """EDGE-011 (REQ-017): a class with exactly 15 annotated fields renders 15 field lines and no
    marker; a class with 16 renders 15 lines plus `  - … +1 fields`; a class with 20 renders 15
    lines plus `  - … +5 fields`."""
    root = _t004_tree(tmp_path, {"src/caps.py": _EDGE011_MODULE})
    out = tmp_path / "STRUCTURE.md"

    proc = _run_generator(root, out)
    text = _map_text(out, proc)
    lines = _symbol_lines(text, "src/caps.py")
    failures: list[str] = []

    if proc.returncode != 0:
        failures.append(f"clause 1: exit {proc.returncode}: {proc.stderr!r}")
    failures += _seq_failures(lines, _EDGE011_LINES, "1")
    markers = [line for line in lines if _ELLIPSIS in line]
    if len(markers) != sum(1 for _, _, elided in _EDGE011_CLASSES if elided):
        failures.append(f"clause 2: {len(markers)} elision marker line(s) rendered, expected 2: {markers!r}")
    for _, _, elided in _EDGE011_CLASSES:
        if elided and not any(f"{_ELLIPSIS} +{elided} fields" in line for line in markers):
            failures.append(f"clause 2: no marker line reporting +{elided} elided fields: {markers!r}")
    at_cap = lines[: 1 + _FIELD_CAP]
    if any(_ELLIPSIS in line for line in at_cap):
        failures.append(f"clause 2: the class with exactly {_FIELD_CAP} fields renders an elision marker: {at_cap!r}")
    assert not failures, "\n".join(failures)


def test_edge_012_long_summary_truncated(tmp_path: Path) -> None:
    """EDGE-012 (REQ-018): a docstring first logical line longer than 100 characters is truncated
    at 100 characters of normalized text with a trailing `…`, and a summary of exactly 100
    characters renders in full with no marker."""
    if not len(_EDGE012_NORMALIZED) > _SUMMARY_LIMIT or len(_EDGE012_AT_LIMIT) != _SUMMARY_LIMIT:
        pytest.fail("the EDGE-012 fixture is not over/at the 100-character limit — invalid test data")
    root = _t004_tree(tmp_path, {"src/long.py": _EDGE012_MODULE})
    out = tmp_path / "STRUCTURE.md"

    proc = _run_generator(root, out)
    text = _map_text(out, proc)
    lines = _symbol_lines(text, "src/long.py")
    failures: list[str] = []

    if proc.returncode != 0:
        failures.append(f"clause 1: exit {proc.returncode}: {proc.stderr!r}")
    failures += _seq_failures(lines, _EDGE012_LINES, "1")
    truncated = [line for line in lines if "long_summary" in line]
    if truncated and _EDGE012_NORMALIZED[:_SUMMARY_LIMIT] not in truncated[0]:
        failures.append(
            f"clause 2: the summary is not truncated at {_SUMMARY_LIMIT} normalized characters: {truncated[0]!r}"
        )
    if truncated and not truncated[0].endswith(_ELLIPSIS):
        failures.append(f"clause 3: the truncated summary has no trailing {_ELLIPSIS!r}: {truncated[0]!r}")
    if _EDGE012_NORMALIZED[_SUMMARY_LIMIT:] in text:
        failures.append("clause 2: the part past the limit is rendered")
    if any(_ELLIPSIS in line and "exactly_limit" in line for line in lines):
        failures.append(f"clause 4: a summary of exactly {_SUMMARY_LIMIT} characters carries the marker")
    assert not failures, "\n".join(failures)
