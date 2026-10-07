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


def _run_generator(root: Path, out: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    """Run the generator over `root`, writing/checking `out`.

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
