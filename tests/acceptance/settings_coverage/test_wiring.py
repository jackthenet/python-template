"""AC-003: src/main.py wires all features' settings at startup."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]


def test_main_wires_all_features() -> None:
    """AC-003: executing src/main.py registers all features' settings in the shared registry."""
    code = (
        "import sys; sys.path.insert(0, 'src');\n"
        "import main;\n"
        "from backend.settings import get_settings_registry;\n"
        "reg = get_settings_registry();\n"
        "keys = ('logging.log_level', 'authentication.session_ttl', 'usermanagement.roles', 'eventbus.max_queue_size');\n"
        "print([reg.has(k) for k in keys]);\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        cwd=_REPO_ROOT,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip().endswith("[True, True, True, True]"), result.stdout
