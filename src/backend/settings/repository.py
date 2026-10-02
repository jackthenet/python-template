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
from io import StringIO
from pathlib import Path
from typing import Any

from loguru import logger
from ruamel.yaml import YAML
from ruamel.yaml.error import YAMLError
from ruamel.yaml.nodes import ScalarNode
from ruamel.yaml.representer import SafeRepresenter

from backend.logging import logged_class
from backend.settings.exceptions import TemplateStorageError, ValueStorageError
from backend.settings.models import Template

# The characters the YAML-1.1 reader (the reader ``typ="safe"`` uses) treats as
# line breaks: inside a plain or single-quoted scalar they fold to a line break
# on load, so a scalar containing one has to be emitted in an escaped
# (double-quoted) style. A full-BMP scan (docs/verification/main-ci-green.md,
# item A) showed U+0085 (NEL) is the only code point the pre-fix serializer
# actually corrupted — it wrote NEL literally inside a single-quoted scalar while
# its reader folded it away — and U+2028/U+2029 are listed alongside it so the
# rule follows the reader instead of the emitter's incidental behaviour.
_YAML_LINE_BREAKS = "\x85\u2028\u2029"


def _str_representer(dumper: Any, data: str) -> ScalarNode:
    """Represent ``str`` scalars, forcing double-quoted style on affected ones.

    ruamel's emitter writes U+0085 (NEL) literally inside a single-quoted
    scalar while its reader folds that same character to a line break, so a
    stored value silently comes back changed (settings INV-009 /
    settings-coverage INV-002: ``'\\x85'`` loaded as ``' '``). Only scalars that
    actually contain such a character get the escaped style, so the on-disk
    format stays byte-identical for every other value (keys, ``null``, numbers
    and unaffected strings are untouched).
    """
    style = '"' if any(ch in data for ch in _YAML_LINE_BREAKS) else None
    return ScalarNode("tag:yaml.org,2002:str", data, style=style)


# The safe representer table with the ``str`` entry replaced (a copy, so the
# shared ruamel table is never mutated).
_YAML_REPRESENTERS: dict[Any, Any] = {**SafeRepresenter.yaml_representers, str: _str_representer}


class _SafeRepresenter(SafeRepresenter):
    """The safe representer with the ``str`` override above.

    Subclassing keeps the override instance-scoped: ``add_representer`` is a
    classmethod that mutates the shared ``SafeRepresenter`` class, which would
    change the output of every other ruamel user in the process.
    """

    yaml_representers = _YAML_REPRESENTERS


def _dump_yaml(data: dict[str, Any]) -> str:
    """Dump ``data`` as safe YAML: block style, sorted keys.

    A fresh ``YAML`` instance is used per call: ruamel instances hold
    per-call state and are not thread-safe, so this keeps the dump
    stateless (and thread-safe) per invocation.

    The representer swap is per instance, and the loader is untouched, so the
    safe-YAML semantics of REQ-022 / settings-coverage REQ-010 are unchanged:
    the document stays plain YAML (no custom tags, no object loading) and files
    written before the fix keep loading.
    """
    yaml = YAML(typ="safe")
    yaml.default_flow_style = False
    yaml.Representer = _SafeRepresenter
    buf = StringIO()
    yaml.dump(data, buf)
    return buf.getvalue()


def _load_yaml(text: str) -> Any:
    """Load ``text`` as safe YAML (unsafe tags are rejected)."""
    return YAML(typ="safe").load(text)


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
            text = _dump_yaml(values)
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
                data = _load_yaml(path.read_text(encoding="utf-8"))
                result = self._parse(data)
        except YAMLError as e:
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
            text = _dump_yaml(data)
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
                data = _load_yaml(path.read_text(encoding="utf-8"))
                result = self._parse(name, data)
        except YAMLError as e:
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
                    data = _load_yaml(path.read_text(encoding="utf-8"))
                    templates.append(self._parse(path.stem, data))
        except YAMLError as e:
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
