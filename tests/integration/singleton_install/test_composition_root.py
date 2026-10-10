"""Composition-root integration witnesses for the public install operation.

Spec: ``docs/specs/settings-public-registry-setter.md`` REQ-011 / AC-016 (citing
``docs/specs/settings-coverage.md`` REQ-002 unchanged — the read-back rule is what makes
its "using the shared registry from ``get_settings_registry()``" wording literally true).

Both witnesses run ``import main`` in a **fresh interpreter**: the composition root's
wiring runs at module-import time, so it is observable only in an interpreter that has
not imported ``main`` yet. The pattern is the established composition-root one
(``tests/acceptance/settings_coverage/test_wiring.py``,
``tests/acceptance/permissions/test_composition_wiring.py``), with ``cwd`` set to the
test's temp directory — ``src/main.py`` creates ``./data/*.db``, ``./data/files`` and the
``settings/`` YAML directory relative to its cwd, so the witness leaves nothing in the
repository (``test_wiring.py``'s ``cwd=_REPO_ROOT`` form would).

The install operation is reached by attribute lookup on ``backend.settings`` **before**
``import main`` and is never imported: while the operation does not exist the subprocess
fails with an ``AttributeError`` naming the missing public function, which surfaces as an
assertion failure on ``returncode`` inside the test body rather than as a collection error.
"""

from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
_SRC = _REPO_ROOT / "src"
_MAIN = _SRC / "main.py"

# The local handle REQ-011 removes from src/main.py's consumer sites.
_HANDLE = "_settings_registry"

# One settings key per feature whose ``register_*_settings`` call the composition root
# makes (settings-coverage.md REQ-002): each must be registered in the shared instance.
_FEATURE_KEYS = (
    "logging.log_level",
    "authentication.session_ttl",
    "usermanagement.roles",
    "eventbus.max_queue_size",
    "permissions.system_principal",
    "search.default_page_size",
)

# Patched before ``import main`` because main binds both the install operation and the six
# registration functions at its own import time. The witness then sees which instance main
# installs, and which instance each feature registration registers into.
_INSTRUMENT = f"""\
import sys

sys.path.insert(0, {str(_SRC)!r})

import backend.authentication
import backend.eventbus
import backend.logging
import backend.permissions
import backend.search
import backend.settings
import backend.usermanagement

installs = []
_real_setter = backend.settings.set_settings_registry


def _install(registry):
    installs.append(registry)
    _real_setter(registry)


backend.settings.set_settings_registry = _install

registered = []


def _spy(register_settings):
    def _spyged(registry, *args, **kwargs):
        registered.append(registry)
        return register_settings(registry, *args, **kwargs)

    return _spyged


for _module in (
    backend.logging,
    backend.authentication,
    backend.usermanagement,
    backend.eventbus,
    backend.permissions,
    backend.search,
):
    _module.register_settings = _spy(_module.register_settings)
"""

# AC-016: install through the setter, then read the shared instance back through the getter.
_CODE_AC_016 = (
    _INSTRUMENT
    + f"""
import main
from backend.settings import get_settings_registry

registry = get_settings_registry()
print(
    [
        len(installs) == 1,
        bool(installs) and installs[0] is registry,
        registry is not None and all(registry.has(k) for k in {_FEATURE_KEYS!r}),
    ]
)
"""
)

# REQ-011's ordering rule: the install precedes the six registrations, and the instance it
# installed is the instance those registrations register into.
_CODE_REGISTRATIONS = (
    _INSTRUMENT
    + f"""
import main
from backend.settings import get_settings_registry

registry = get_settings_registry()
print(
    [
        len(installs) == 1,
        len(registered) == 6,
        bool(registered) and all(r is registry for r in registered),
        registry is not None and all(registry.has(k) for k in {_FEATURE_KEYS!r}),
    ]
)
"""
)


def _run_instrumented(code: str, tmp_path: Path) -> subprocess.CompletedProcess[str]:
    """Run ``code`` in a fresh interpreter with a scratch cwd (no repo state left behind)."""
    return subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        cwd=tmp_path,
        check=False,
    )


def _private_slot_imports() -> list[str]:
    """``src/main.py`` imports of a private name or a private module (AC-016, clause 2)."""
    tree = ast.parse(_MAIN.read_text(encoding="utf-8"))
    return [
        f"{node.module}.{alias.name}"
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        for alias in node.names
        if alias.name.startswith("_") or (node.module or "").rpartition(".")[2].startswith("_")
    ]


def _consumer_sites_passing_the_handle() -> list[int]:
    """Lines where a REQ-011 consumer site passes the local handle instead of the getter.

    The consumer sites are the six ``register_*_settings(...)`` calls and the four
    ``settings_registry=`` service-construction sites named by AC-016.
    """
    tree = ast.parse(_MAIN.read_text(encoding="utf-8"))
    sites: list[int] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        name = func.id if isinstance(func, ast.Name) else getattr(func, "attr", "")
        is_consumer = (name.startswith("register_") and name.endswith("_settings")) or any(
            kw.arg == "settings_registry" for kw in node.keywords
        )
        if not is_consumer:
            continue
        passed = [
            value
            for value in [*node.args, *(kw.value for kw in node.keywords)]
            if isinstance(value, ast.Name) and value.id == _HANDLE
        ]
        if passed:
            sites.append(node.lineno)
    return sites


def test_ac_016_main_installs_through_setter(tmp_path: Path) -> None:
    """AC-016 (REQ-011): a fresh interpreter importing ``main`` leaves the wired registry
    reachable through ``get_settings_registry()`` with the feature settings registered, and
    main installed it through the public setter — with no private-slot import and no
    consumer site passed the local handle.
    """
    result = _run_instrumented(_CODE_AC_016, tmp_path)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip().endswith("[True, True, True]"), result.stdout
    assert _private_slot_imports() == [], "AC-016: src/main.py must import no private singleton slot"
    assert _consumer_sites_passing_the_handle() == [], (
        "AC-016: the six register_*_settings calls and the four settings_registry= sites must read"
        f" the shared instance through get_settings_registry(), not the local {_HANDLE} handle"
    )


def test_installed_registry_serves_feature_registration(tmp_path: Path) -> None:
    """REQ-011 / AC-016 (settings-coverage.md REQ-002): the instance installed through the
    setter is the instance all six feature registrations register into — the install
    precedes the registrations, and they use the shared instance rather than a second one.
    """
    result = _run_instrumented(_CODE_REGISTRATIONS, tmp_path)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip().endswith("[True, True, True, True]"), result.stdout
