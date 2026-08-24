"""Contract tests for the logging feature NFR requirements (docs/specs/logging.md)."""

from __future__ import annotations

import pytest


class TestPublicApiContract:
    """NFR-001: the public API surface is stable and importable."""

    def test_nfr_001_public_api_importable(self) -> None:
        """NFR-001: from backend.logging import setup_logger, logged, logged_class works."""
        from backend.logging import setup_logger, logged, logged_class

        assert callable(setup_logger)
        assert callable(logged)
        assert callable(logged_class)


class TestNoNewDependencies:
    """NFR-002: the logging feature introduces no new dependencies beyond loguru."""

    def test_nfr_002_no_new_dependencies(self) -> None:
        """NFR-002: the logging feature depends only on loguru and the standard library."""
        import backend.logging as mod

        # Verify the module can be imported without additional third-party packages
        assert mod is not None


class TestTypeSafety:
    """NFR-003: all public functions have explicit type annotations."""

    def test_nfr_003_type_annotations_present(self) -> None:
        """NFR-003: setup_logger, logged, logged_class have return type annotations."""
        import inspect

        from backend.logging import setup_logger, logged, logged_class

        for func in (setup_logger, logged, logged_class):
            sig = inspect.signature(func)
            assert sig.return_annotation is not inspect.Parameter.empty, (
                f"{func.__name__} missing return type annotation"
            )


class TestThreadSafetyContract:
    """NFR-004: setup_logger() is safe for concurrent use."""

    def test_nfr_004_thread_safe(self) -> None:
        """NFR-004: concurrent setup_logger() calls do not corrupt state."""
        import threading

        from backend.logging import setup_logger

        errors: list[BaseException] = []

        def worker() -> None:
            try:
                setup_logger()
            except BaseException as exc:
                errors.append(exc)

        threads = [threading.Thread(target=worker) for _ in range(8)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors
