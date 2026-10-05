"""Contract tests for the logging feature's public tracing surface.

AC-020 (docs/specs/structlog-logging.md REQ-015) pins the export surface of
``backend.logging``: exactly the §3 public API, and no logging backend is
reachable through the feature. AC-013 (the removed ``context_getter`` / ``depth``
decorator parameters) is added to this module by the tracing-decorator task.
"""

from __future__ import annotations

import pytest

_PUBLIC_API = frozenset(
    {
        "setup_logger",
        "logged",
        "logged_class",
        "get_logger",
        "Settings",
        "get_settings",
        "register_settings",
        "_read_setting",
    }
)


def test_ac_020_public_export_surface() -> None:
    """AC-020: backend.logging exports exactly the §3 public API and re-exports no logging backend."""
    import backend.logging as feature

    assert set(feature.__all__) == set(_PUBLIC_API), "AC-020/REQ-015: the export set must be exactly §3's public API"

    for name in _PUBLIC_API:
        assert hasattr(feature, name), f"AC-020/REQ-015: backend.logging must export {name}()"

    for backend_name in ("logger", "loguru"):
        assert backend_name not in feature.__all__, (
            f"AC-020: no logging backend may be re-exported (found {backend_name})"
        )

    with pytest.raises(ImportError):
        from backend.logging import (
            logger,  # noqa: F401  # AC-020: features must not reach a backend through the feature
        )
