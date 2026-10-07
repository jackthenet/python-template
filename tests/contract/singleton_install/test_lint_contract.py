"""AC-018 / EDGE-009 / NFR-004: the ruff ``TID251`` guard for the five private singleton slots.

Spec: ``docs/specs/settings-public-registry-setter.md`` REQ-013 (the second guard of D12),
AC-018, EDGE-009, NFR-004, and ``docs/decisions/ADR-084`` (two guards). The scan-test half of
REQ-013 is T-007's ``tests/unit/architecture/test_singleton_slots.py``; this file witnesses the
lint half — ruff sees the import that makes a foreign slot write possible, at edit time, in the
lint job that already runs on every push (``.github/workflows/lint.yml:37``).

The measured facts this test is built on (spec §10, ADR-084's probes, re-measured on this
branch on 2026-10-07):

* with a ``banned-api`` table present but ``TID251`` **not** in ``[tool.ruff.lint] select``,
  ruff reports nothing — the whole table is inert. That is exactly what the RED gate observes:
  the planted import runs cleanly and no ``TID251`` comes back;
* a bare-name key flags nothing, so the five keys must be fully qualified (EDGE-009's width);
* both AC-018 reference forms are reported: the ``ImportFrom`` of the slot, and the module-alias
  form (``import backend.settings.registry as reg`` followed by a subscript write through it);
* the owning module's own slot statements are **not** reported (``TID251`` sees cross-module
  references only), and neither is an import of a public name (EDGE-009).

Every file ruff is asked about is planted in pytest's ``tmp_path``, never inside the repository:
the lint job runs ``ruff check .``, so a planted violation committed into the repo would break
CI (T-008 design constraint, ADR-084). The fixture source is assembled from the owner table with
f-strings, so no string constant in this file ever places a slot name next to a subscript write —
the T-007 scan test reads this file too (its F-36).

The tool runs use ``sys.executable -m ruff`` / ``-m mypy`` with an **absolute** ``--config`` and
``cwd=_REPO_ROOT``: the repository configuration is resolved from this file's own location, never
from the caller's CWD (PROBLEMS.md P-57), and the interpreter is the one already running the test,
so no environment re-resolution happens mid-test.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tomllib
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[3]
_PYPROJECT = _REPO_ROOT / "pyproject.toml"

# Owner table (spec §3.4 / ADR-084): owning module, its private slot, its install operation,
# and a public symbol of that same module (EDGE-009: the module path itself is not banned).
_OWNERS: tuple[tuple[str, str, str, str], ...] = (
    ("backend.settings.registry", "_registry", "set_settings_registry", "SettingsRegistry"),
    ("backend.eventbus.eventbus", "_default_bus", "set_event_bus", "EventBus"),
    ("backend.permissions.service", "_permission_service", "set_permission_service", "PermissionService"),
    ("backend.search.service", "_singleton", "set_search_service", "SearchService"),
    ("backend.sessionmanagement.service", "_session_service", "set_session_service", "SessionService"),
)

_TID251 = "TID251"

# AC-018 names two reference forms per slot: the ImportFrom of the slot, and the module-alias
# form (import the module, then write through it). One planted file holds both, so a working
# ban reports exactly this many findings per slot.
_REFERENCE_FORMS = 2


def _foreign_source(module: str, slot: str) -> str:
    """A file importing another package's slot in **both** AC-018 reference forms.

    Built from the owner table so this file holds no literal spelling of the write (F-36).
    """
    return f"import {module} as _mod\nfrom {module} import {slot}\n\n_ = {slot}\n_mod.{slot}[0] = None\n"


def _public_source(module: str, install: str, symbol: str) -> str:
    """A file importing only public names: the feature's install operation and a public symbol
    imported from the owning module path itself (EDGE-009)."""
    package = module.rpartition(".")[0]
    return f"from {package} import {install}\nfrom {module} import {symbol}\n\n_ = {install}\n_ = {symbol}\n"


def _ruff_findings(*paths: Path, cwd: Path = _REPO_ROOT) -> list[dict[str, Any]]:
    """Run ruff with the **repository** configuration over ``paths`` and return its findings.

    ``sys.executable -m ruff`` is the same ruff the ``lint`` job runs (same venv as the test
    process); ``--config`` is absolute, so the configuration never depends on the caller's CWD.
    Exit code 0 (clean) or 1 (findings) means the invocation ran; anything above 1 is a ruff
    error and must not be mistaken for "no violation found".
    """
    proc = subprocess.run(
        [sys.executable, "-m", "ruff", "check", "--output-format=json", "--config", str(_PYPROJECT), *map(str, paths)],
        capture_output=True,
        text=True,
        cwd=str(cwd),
        check=False,
    )
    assert proc.returncode in (0, 1), f"ruff invocation failed (exit {proc.returncode}):\n{proc.stdout}\n{proc.stderr}"
    try:
        findings = json.loads(proc.stdout)
    except json.JSONDecodeError as error:  # an empty/garbled stdout is a broken invocation, not a pass
        raise AssertionError(f"ruff returned no JSON (exit {proc.returncode}): {proc.stdout[:400]!r}") from error
    assert isinstance(findings, list), f"unexpected ruff JSON payload: {findings!r}"
    return findings


def _tid251(findings: list[dict[str, Any]], name: str | None = None) -> list[dict[str, Any]]:
    """The ``TID251`` findings, optionally restricted to one file (matched on its name)."""
    return [
        finding
        for finding in findings
        if finding["code"] == _TID251 and (name is None or finding["filename"].replace("\\", "/").endswith(name))
    ]


def _config() -> dict[str, Any]:
    """The repository's ``pyproject.toml`` as data (the configuration half of AC-018/NFR-004)."""
    return tomllib.loads(_PYPROJECT.read_text(encoding="utf-8"))


def test_ac_018_ruff_bans_private_slot_import(tmp_path: Path) -> None:
    """AC-018 (REQ-013): ruff run with the repository configuration reports ``TID251`` for a file
    that imports each of the five private slots — in both reference forms — naming that feature's
    public install operation; ``select`` contains ``TID251``; the repository itself reports none;
    and the five owner modules' own slot statements are not reported.
    """
    # Keyed on the slot, not the module leaf: three of the five owning modules are named
    # ``service.py``, so a leaf-name key would collapse three planted files into one.
    planted = [(tmp_path / f"foreign_{slot}.py", module, slot, install) for module, slot, install, _ in _OWNERS]
    assert len({path.name for path, *_ in planted}) == len(_OWNERS), (
        "fixture collision: planted file names must be unique"
    )
    for path, module, slot, _ in planted:
        path.write_text(_foreign_source(module, slot), encoding="utf-8")
    findings = _ruff_findings(*(path for path, _, _, _ in planted))

    for path, module, slot, install in planted:
        hits = _tid251(findings, path.name)
        assert len(hits) == _REFERENCE_FORMS, (
            f"AC-018: importing {module}.{slot} must be reported in both reference forms "
            f"(the ImportFrom and the module-alias write), got {len(hits)}: "
            f"{[(f['code'], f['location']['row']) for f in findings if f['filename'].endswith(path.name)]}"
        )
        assert all(f"{module}.{slot}" in f["message"] and install in f["message"] for f in hits), (
            f"AC-018: each TID251 for {module}.{slot} must name the banned path and the public"
            f" install operation {install}(); got {[f['message'] for f in hits]}"
        )

    select = _config()["tool"]["ruff"]["lint"]["select"]
    assert _TID251 in select, (
        f"AC-018: [tool.ruff.lint] select must contain {_TID251}, without it the banned-api table is inert"
    )

    assert _tid251(_ruff_findings(Path("."))) == [], "AC-018: the repository itself must report no TID251 violation"

    owner_modules = [Path("src", *module.split(".")).with_suffix(".py") for module, *_ in _OWNERS]
    assert _tid251(_ruff_findings(*owner_modules)) == [], (
        "AC-018 / EDGE-008: the five owner modules write their own slot and must not be reported"
        " — the ban is cross-package, not the module itself"
    )


def test_edge_009_public_api_not_banned(tmp_path: Path) -> None:
    """EDGE-009: importing the public install operation, or a public symbol from the owning
    module path, is never flagged — the ban is by fully-qualified private-slot path, not by module.
    """
    planted = [(tmp_path / f"public_{slot}.py", module, install, symbol) for module, slot, install, symbol in _OWNERS]
    assert len({path.name for path, *_ in planted}) == len(_OWNERS), (
        "fixture collision: planted file names must be unique"
    )
    for path, module, install, symbol in planted:
        path.write_text(_public_source(module, install, symbol), encoding="utf-8")
    control = tmp_path / "control_foreign_settings.py"
    control.write_text(_foreign_source(*_OWNERS[0][:2]), encoding="utf-8")

    findings = _ruff_findings(*(path for path, _, _, _ in planted), control)
    for path, module, install, symbol in planted:
        assert _tid251(findings, path.name) == [], (
            f"EDGE-009: {install} / {module}.{symbol} are public API and must never be banned;"
            f" got {[f['message'] for f in _tid251(findings, path.name)]}"
        )

    assert _tid251(findings, control.name), (
        "EDGE-009 anti-vacuity: the same ruff run must report TID251 for a private-slot import —"
        " while the ban is inert, 'the public API is not banned' proves nothing"
    )


def test_nfr_004_ruff_and_mypy_clean() -> None:
    """NFR-004: the ``banned-api`` table stays configured in ``pyproject.toml`` with the five
    fully-qualified keys, ``ruff check .`` reports no ``TID251`` in the repository, and
    ``mypy src/`` is clean with the new API.
    """
    banned = _config()["tool"]["ruff"]["lint"].get("flake8-tidy-imports", {}).get("banned-api", {})
    missing = [f"{module}.{slot}" for module, slot, _, _ in _OWNERS if f"{module}.{slot}" not in banned]
    assert missing == [], (
        f"NFR-004 / REQ-013: [tool.ruff.lint.flake8-tidy-imports.banned-api] must configure these"
        f" fully-qualified keys: {missing} (a bare-name key flags nothing — measured)"
    )
    assert all(isinstance(entry, dict) and entry.get("msg") for entry in banned.values()), (
        f"NFR-004: every banned-api entry needs a .msg naming the public trio; got {banned!r}"
    )

    assert _tid251(_ruff_findings(Path("."))) == [], (
        "NFR-004: ruff check . must report no TID251 violation in the repository"
    )

    mypy = subprocess.run(
        [sys.executable, "-m", "mypy", "src"],
        capture_output=True,
        text=True,
        cwd=str(_REPO_ROOT),
        check=False,
    )
    assert mypy.returncode == 0, (
        f"NFR-004: mypy src/ must be clean with the new API\n{mypy.stdout[-2000:]}\n{mypy.stderr[-500:]}"
    )
