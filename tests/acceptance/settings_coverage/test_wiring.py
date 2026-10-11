"""AC-003: src/main.py wires all features' settings at startup.

Reproduction witness for issue ``startup-settings-registration-gaps`` (D-1/D-2): the
composition root registers six features' settings and never calls the filemanagement,
mail and sessionmanagement registrations, so 16 of the 34 specified keys are absent
from the live registry. The previous version of this witness sampled four keys from
four already-registered features, so it passed with the defect present — the guard was
as incomplete as the wiring (docs/verification/startup-settings-registration-gaps.md
§3 D-2).

The expected key set is **derived from the source**, never hardcoded (Q-06): every
``src/backend/*/feature_settings.py`` module registers its settings into a scratch
registry, and every key that produces must be present in the registry ``import main``
installs. A tenth feature that is never registered therefore turns this witness RED.

``cwd`` is the test's temp directory and ``sys.path`` carries an **absolute** ``src``
entry (Q-22, the pattern of ``tests/acceptance/permissions/test_composition_wiring.py``):
``import main`` creates ``settings/``, ``data/`` and ``logs/`` in its working directory,
and a repository-root ``settings/values.yaml`` would feed its persisted values back into
the next run by REQ-011 and change what the witness asserts.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from collections.abc import Iterator
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[3]
_SRC = _REPO_ROOT / "src"

# The child program: probe every feature's own registration, then the composition root's.
# main's registry cannot be enumerated (its system principal holds no ``settings.views``,
# Q-07), so the expected set comes from the scratch registry and main's is probed with has().
_CODE = f"""
import importlib
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, {str(_SRC)!r})

from backend.settings import SettingsRegistry, YamlValueRepository, get_settings_registry

# The expected set: every feature that owns a feature_settings module, registered into a
# scratch registry (no permission check, so views() can enumerate it).
scratch = SettingsRegistry(value_repository=YamlValueRepository(tempfile.mkdtemp()))
for module in sorted(Path({str(_SRC)!r}).glob("backend/*/feature_settings.py")):
    importlib.import_module("backend." + module.parent.name + ".feature_settings").register_settings(scratch)
expected = sorted(view.key for view in scratch.views())

import main

reg = get_settings_registry()
missing = [key for key in expected if not reg.has(key)]
print("PROBED %d / REGISTERED %d / MISSING %s" % (len(expected), len(expected) - len(missing), missing))
positive = ("logging.log_level", "authentication.session_ttl", "usermanagement.roles", "eventbus.max_queue_size")
print([reg.has(key) for key in positive])
"""

_REPORT = re.compile(r"PROBED (\d+) / REGISTERED (\d+) / MISSING (\[.*\])")


@pytest.fixture(autouse=True)
def _no_repo_root_settings_dir() -> Iterator[None]:
    """Remove a repository-root ``settings/`` directory this run created (Q-22 hygiene).

    ``src/main.py`` builds its registry with the default ``YamlValueRepository("settings")``,
    so any witness that runs it with ``cwd=_REPO_ROOT`` leaves ``settings/values.yaml`` behind;
    its persisted values then win over every definition default by REQ-011 in the next run.
    A directory that already existed is left alone — it is the developer's own state.
    """
    existed = (_REPO_ROOT / "settings").is_dir()
    yield
    if not existed:
        shutil.rmtree(_REPO_ROOT / "settings", ignore_errors=True)


def test_main_wires_all_features(tmp_path: Path) -> None:
    """AC-003 / REQ-002: the composition root registers every feature's settings.

    Every key the nine ``feature_settings`` modules register is present in the registry
    ``import main`` installs (0 missing), and the four keys the original witness sampled
    stay registered.
    """
    result = subprocess.run(
        [sys.executable, "-c", _CODE],
        capture_output=True,
        text=True,
        cwd=tmp_path,
        check=False,
    )
    assert result.returncode == 0, result.stderr

    report, positive = result.stdout.strip().splitlines()[-2:]
    # The four-key positive check of the original witness is kept (AC-003, REQ-002).
    assert positive == "[True, True, True, True]", result.stdout

    match = _REPORT.fullmatch(report)
    assert match, f"unexpected composition-root registration report: {report!r}"
    probed, registered, missing = int(match[1]), int(match[2]), match[3]
    assert probed > 0, f"no feature_settings module was probed: {report!r}"
    assert missing == "[]", f"the composition root never registers these settings: {missing}"
    assert registered == probed, report
