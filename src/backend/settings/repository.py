"""Template storage (repository pattern).

``TemplateRepository`` is the stable storage interface. The first
implementation is ``YamlTemplateRepository`` (one file per template, safe
YAML, atomic writes). Alternative format implementations (JSON, etc.) must
satisfy the same interface and observable behavior.

``ValueRepository`` is the stable interface for persisting the registry's
current values. The first implementation is ``YamlValueRepository`` (a single
``values.yaml``, safe YAML, atomic writes).
"""

from __future__ import annotations

import os
import threading
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import yaml
from loguru import logger

from backend.logging import logged_class
from backend.settings.exceptions import TemplateStorageError, ValueStorageError
from backend.settings.models import Template


@logged_class(slow_threshold_ms=100)
class ValueRepository(ABC):
    """Persists the registry's current values (REQ-010).

    The ABC is traced via the shared logging feature (``@logged_class``);
    concrete subclasses inherit the tracing.
    """

    @abstractmethod
    def load(self) -> dict[str, Any] | None:
        """Return the persisted values, or None if none are persisted."""

    @abstractmethod
    def save(self, values: dict[str, Any]) -> None:
        """Persist ``values`` (overwriting any existing values)."""


@logged_class(slow_threshold_ms=100)
class YamlValueRepository(ValueRepository):
    """Single ``values.yaml`` file, safe YAML, atomic write, thread-safe (REQ-010).

    The class is traced via the shared logging feature (``@logged_class``).

    Writes are atomic (a temp file in the same directory is renamed over the
target), so the file is always either absent or valid YAML.
    """

    def __init__(self, directory: str) -> None:
        self._directory = Path(directory)
        self._directory.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()

    def _path(self) -> Path:
        return self._directory / "values.yaml"

    def save(self, values: dict[str, Any]) -> None:
        with self._lock:
            text = yaml.safe_dump(values, sort_keys=True, default_flow_style=False)
            tmp = self._directory / ".values.yaml.tmp"
            tmp.write_text(text, encoding="utf-8")
            os.replace(tmp, self._path())
        logger.debug("values saved to storage: count={}", len(values))

    def load(self) -> dict[str, Any] | None:
        try:
            with self._lock:
                path = self._path()
                if not path.exists():
                    return None
                data = yaml.safe_load(path.read_text(encoding="utf-8"))
                result = self._parse(data)
        except yaml.YAMLError as e:
            logger.error("value storage failure: reason={}", e)
            raise ValueStorageError(f"corrupted values file: {e}") from e
        except ValueStorageError as e:
            logger.error("value storage failure: reason={}", e)
            raise
        logger.debug("values loaded from storage: count={}", len(result))
        return result

    def _parse(self, data: Any) -> dict[str, Any]:
        if not isinstance(data, dict):
            raise ValueStorageError("values file is not a mapping")
        return {str(k): v for k, v in data.items()}


@logged_class(slow_threshold_ms=100)
class TemplateRepository(ABC):
    """Storage-agnostic interface for named templates.

    The ABC is traced via the shared logging feature (``@logged_class``);
    concrete subclasses inherit the tracing.
    """

    @abstractmethod
    def save(self, template: Template) -> None:
        """Persist ``template`` (overwriting any existing template of the name)."""

    @abstractmethod
    def get(self, name: str) -> Template | None:
        """Return the template of ``name``, or None if it does not exist."""

    @abstractmethod
    def delete(self, name: str) -> None:
        """Delete the template of ``name`` (idempotent)."""

    @abstractmethod
    def list(self) -> list[Template]:
        """Return all stored templates, name-ordered."""


@logged_class(slow_threshold_ms=100)
class MemoryTemplateRepository(TemplateRepository):
    """In-memory template storage (the default when none is supplied).

    The class is traced via the shared logging feature (``@logged_class``).
    """

    def __init__(self) -> None:
        self._store: dict[str, Template] = {}
        self._lock = threading.Lock()

    def save(self, template: Template) -> None:
        with self._lock:
            self._store[template.name] = template

    def get(self, name: str) -> Template | None:
        with self._lock:
            return self._store.get(name)

    def delete(self, name: str) -> None:
        with self._lock:
            self._store.pop(name, None)

    def list(self) -> list[Template]:
        with self._lock:
            return [self._store[n] for n in sorted(self._store)]


@logged_class(slow_threshold_ms=100)
class YamlTemplateRepository(TemplateRepository):
    """YAML file storage: one ``<name>.yaml`` file per template.

    The class is traced via the shared logging feature (``@logged_class``).

    Writes are atomic (a temp file in the same directory is renamed over the
    target), so a template file is always either absent or valid YAML.
    """

    def __init__(self, directory: Path | str) -> None:
        self._directory = Path(directory)
        self._directory.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()

    def _path(self, name: str) -> Path:
        return self._directory / f"{name}.yaml"

    def save(self, template: Template) -> None:
        with self._lock:
            data = {
                "name": template.name,
                "category": template.category,
                "group": template.group,
                "values": template.values,
            }
            text = yaml.safe_dump(data, sort_keys=True, default_flow_style=False)
            tmp = self._directory / f".{template.name}.yaml.tmp"
            tmp.write_text(text, encoding="utf-8")
            os.replace(tmp, self._path(template.name))
        logger.debug("template saved to storage: name={}", template.name)

    def get(self, name: str) -> Template | None:
        try:
            with self._lock:
                path = self._path(name)
                if not path.exists():
                    return None
                data = yaml.safe_load(path.read_text(encoding="utf-8"))
                result = self._parse(name, data)
        except yaml.YAMLError as e:
            logger.error("template storage failure: name={} reason={}", name, e)
            raise TemplateStorageError(f"corrupted template file {name}: {e}") from e
        except TemplateStorageError as e:
            logger.error("template storage failure: name={} reason={}", name, e)
            raise
        logger.debug("template loaded from storage: name={}", name)
        return result

    def delete(self, name: str) -> None:
        with self._lock:
            path = self._path(name)
            if path.exists():
                path.unlink()

    def list(self) -> list[Template]:
        templates: list[Template] = []
        try:
            with self._lock:
                for path in sorted(self._directory.glob("*.yaml")):
                    data = yaml.safe_load(path.read_text(encoding="utf-8"))
                    templates.append(self._parse(path.stem, data))
        except yaml.YAMLError as e:
            logger.error("template storage failure: reason={}", e)
            raise TemplateStorageError(f"corrupted template file: {e}") from e
        except TemplateStorageError as e:
            logger.error("template storage failure: reason={}", e)
            raise
        logger.debug("templates loaded from storage: count={}", len(templates))
        return templates

    def _parse(self, name: str, data: Any) -> Template:
        if not isinstance(data, dict):
            raise TemplateStorageError(f"template {name} is not a mapping")
        if "name" not in data or "category" not in data or "values" not in data:
            raise TemplateStorageError(f"template {name} is missing required fields")
        values = data["values"]
        if not isinstance(values, dict):
            raise TemplateStorageError(f"template {name} values must be a mapping")
        return Template(
            name=data["name"],
            category=data["category"],
            group=data.get("group"),
            values=values,
        )
