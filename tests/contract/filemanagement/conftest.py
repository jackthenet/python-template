"""Fixtures for the file-management contract tests."""

from __future__ import annotations

from pathlib import Path

import pytest
from filemanagement_test_helpers import EventCollector, db_url, isolated_registry, make_service

from backend.filemanagement import FileService, InMemoryStorageBackend, SqliteFileRepository
from backend.settings import SettingsRegistry


@pytest.fixture()
def events() -> EventCollector:
    return EventCollector()


@pytest.fixture()
def registry() -> SettingsRegistry:
    return isolated_registry()


@pytest.fixture()
def repo(tmp_path: Path) -> SqliteFileRepository:
    return SqliteFileRepository(db_url(tmp_path))


@pytest.fixture()
def backend() -> InMemoryStorageBackend:
    return InMemoryStorageBackend()


@pytest.fixture()
def service(
    repo: SqliteFileRepository, backend: InMemoryStorageBackend, events: EventCollector, registry: SettingsRegistry
) -> FileService:
    return make_service(repo, backend=backend, event_bus=events, registry=registry)
