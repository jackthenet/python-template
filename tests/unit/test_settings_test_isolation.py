"""Reproduction test for the settings-test-isolation defect (ISSUE).

The defect
----------
Multiple tests instantiate the **shared default settings registry** —
``get_settings_registry()`` (no args) or ``SettingsRegistry(...)`` without a
``value_repository`` — which defaults to ``YamlValueRepository("settings")``
(a ``settings/`` directory in the repo root). All such tests construct/write
the **same** ``settings/values.yaml``. On **Windows**, the atomic write
(``os.replace`` in ``src/backend/settings/repository.py``) fails with
``PermissionError [WinError 32]`` when another xdist worker has the file open —
so **xdist parallel runs** fail, while **sequential runs** pass.

This violates the AGENTS.md rule (``AGENTS.md`` → "Using the Settings
Feature"):
    "Test registries MUST pass an explicit isolated value repository
    (e.g., ``YamlValueRepository(tempfile.mkdtemp())``)."

The primary offender is ``tests/conftest.py``'s ``_logging_session_setup``
fixture (session-scoped, autouse) — it runs for **every** test and calls
``set_value("logging.log_file", ...)`` + ``set_value("logging.log_level", ...)``
on the shared default registry. Other offenders are listed in the triage
record ``docs/verification/settings-test-isolation.md``.

Reproduction (deterministic)
-----------------------------
Run a representative offending test in a **subprocess** (``cwd`` = repo root),
then assert the shared ``settings/`` directory at the repo root was **NOT**
created by that run. Because the session-scoped autouse
``_logging_session_setup`` fixture runs for every test and writes to the shared
default registry, any test run reproduces the defect on the current code.

This test **FAILS** on the current (defective) code (the ``settings/``
directory is created) and **PASSES** after the fix (offending fixtures use an
isolated value repository).
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

# The repo (worktree) root: this file lives at tests/unit/, so parents[2].
_REPO_ROOT = Path(__file__).resolve().parents[2]
# The shared default value repository directory (the defect artifact).
_SHARED_SETTINGS_DIR = _REPO_ROOT / "settings"

# A representative offending test. The session-scoped autouse
# ``_logging_session_setup`` fixture (tests/conftest.py) runs for every test
# and writes to the shared default registry, so any test under tests/
# reproduces the defect. A fast, reliable test keeps the subprocess run short.
_REPRESENTATIVE_TEST = "tests/acceptance/settings/test_settings.py::test_ac_018_singleton"


def _remove_shared_settings_dir() -> None:
    """Remove the shared settings dir (an artifact of the defect, not a repo file)."""
    if _SHARED_SETTINGS_DIR.exists():
        shutil.rmtree(_SHARED_SETTINGS_DIR, ignore_errors=True)


def test_offending_tests_do_not_create_shared_settings_dir() -> None:
    """Running an offending test must not create the shared settings dir.

    The shared ``settings/`` directory at the repo root is the defect: tests
    must use an isolated value repository (``YamlValueRepository(
    tempfile.mkdtemp())``), not the shared default registry. Traces to the
    AGENTS.md rule and the offending fixtures (see module docstring).
    """
    # Ensure a clean "before" state: remove any pre-existing shared settings
    # dir (e.g., created by the session's autouse fixture) so the subprocess
    # run's effect is unambiguous.
    _remove_shared_settings_dir()

    try:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                _REPRESENTATIVE_TEST,
                "-p",
                "no:cacheprovider",
                "-q",
            ],
            cwd=_REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        # The representative test itself must pass (it's a valid test); the
        # defect is the side effect on the shared settings dir, not the test
        # result.
        assert result.returncode == 0, (
            "representative test failed to run (is it a valid test?): "
            f"returncode={result.returncode}\n"
            f"stdout={result.stdout}\nstderr={result.stderr}"
        )

        # The shared settings dir must NOT have been created by the run.
        assert not _SHARED_SETTINGS_DIR.exists(), (
            "DEFECT (settings-test-isolation): running the offending test "
            f"created the shared {_SHARED_SETTINGS_DIR} directory at the repo "
            "root. Tests must use an isolated value repository "
            "(YamlValueRepository(tempfile.mkdtemp())), not the shared default "
            "registry. See AGENTS.md 'Using the Settings Feature'."
        )
    finally:
        # Keep the worktree clean: remove the shared settings dir if the run
        # created it (it's an artifact of the defect, not a repo file).
        _remove_shared_settings_dir()
