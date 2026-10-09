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

from ruamel.yaml import YAML
from ruamel.yaml.error import YAMLError
from ruamel.yaml.nodes import ScalarNode
from ruamel.yaml.representer import SafeRepresenter

from backend.logging import get_logger, logged_class
from backend.settings.exceptions import TemplateStorageError, ValueStorageError
from backend.settings.models import Template

# REQ-005 (structlog-logging): the module's one-off statements go through the
# logging feature's entry point instead of importing a logging backend. The same
# feature name as registry.py keeps the settings records attributable to settings.
_logger = get_logger("settings")


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
    r"""Represent ``str`` scalars, forcing double-quoted style on affected ones.

    ruamel's emitter writes U+0085 (NEL) literally inside a single-quoted
    scalar while its reader folds that same character to a line break, so a
    stored value silently comes back changed (settings INV-009 /
    settings-coverage INV-002: ``'\x85'`` loaded as ``' '``). Only scalars that
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
        """Store all values in ``<directory>/values.yaml``, creating the directory eagerly.

        The lock serialises reads and writes inside this instance only — it
        is not a cross-process lock.
        """
        self._directory = Path(directory)
        self._directory.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()

    def _path(self) -> Path:
        """The one file holding every value: ``<directory>/values.yaml``."""
        return self._directory / "values.yaml"

    def save(self, values: dict[str, Any]) -> None:
        """Write the whole value set atomically: temp file in the same directory, then ``os.replace``.

        A crash mid-write leaves the previous file intact, so the file is
        never partial (REQ-010). The debug record carries the count only, never
        the values.
        """
        with self._lock:
            text = _dump_yaml(values)
            tmp = self._directory / ".values.yaml.tmp"
            tmp.write_text(text, encoding="utf-8")
            os.replace(tmp, self._path())
        _logger.debug(f"values saved to storage: count={len(values)}", count=len(values))

    def load(self) -> dict[str, Any] | None:
        """The stored values, or ``None`` when no file exists yet.

        A missing file is not an error; invalid YAML or a non-mapping document
        raises ``ValueStorageError`` instead of a partial value set (EDGE-003).
        """
        try:
            with self._lock:
                path = self._path()
                if not path.exists():
                    return None
                data = _load_yaml(path.read_text(encoding="utf-8"))
                result = self._parse(data)
        except YAMLError as e:
            _logger.error(f"value storage failure: reason={e}", reason=e)
            raise ValueStorageError(f"corrupted values file: {e}") from e
        except ValueStorageError as e:
            _logger.error(f"value storage failure: reason={e}", reason=e)
            raise
        _logger.debug(f"values loaded from storage: count={len(result)}", count=len(result))
        return result

    def _parse(self, data: Any) -> dict[str, Any]:
        """Coerce a loaded document to a ``str``-keyed mapping.

        Anything that is not a mapping raises ``ValueStorageError``.
        """
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
        """An empty store: nothing is loaded, nothing is persisted."""
        self._store: dict[str, Template] = {}
        self._lock = threading.Lock()

    def save(self, template: Template) -> None:
        """Store ``template`` under its name, replacing an existing one silently.

        The instance itself is kept (not a copy); ``Template`` is frozen, so
        callers cannot mutate what is stored.
        """
        with self._lock:
            self._store[template.name] = template

    def get(self, name: str) -> Template | None:
        """The stored template with this name, or ``None`` when there is none."""
        with self._lock:
            return self._store.get(name)

    def delete(self, name: str) -> None:
        """Drop the named template; an unknown name is a silent no-op."""
        with self._lock:
            self._store.pop(name, None)

    def list(self) -> list[Template]:
        """Every stored template, ordered by name (not by insertion order)."""
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
        """One ``<name>.yaml`` file per template under ``directory``, created eagerly.

        The lock serialises file access inside this instance; it does not
        protect the directory against another writer.
        """
        self._directory = Path(directory)
        self._directory.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()

    def _path(self, name: str) -> Path:
        """The file for a name: ``<directory>/<name>.yaml``.

        The repository does not validate the name — the registry does
        (``is_template_name_valid``), and a name reaching this method
        unvalidated would resolve outside the directory.
        """
        return self._directory / f"{name}.yaml"

    def save(self, template: Template) -> None:
        """Write the template's four fields to its own file, atomically via a ``.<name>.yaml.tmp`` sibling.

        A crash leaves either the old file or the new one, never a partial
        template (REQ-022).
        """
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
        _logger.debug(f"template saved to storage: name={template.name}", name=template.name)

    def get(self, name: str) -> Template | None:
        """Parse the file for ``name``, or ``None`` when the file is absent.

        The requested name only selects the file: the returned template's
        fields come from the file, so a file whose ``name`` field disagrees
        with its stem is returned unchanged. A corrupted or incomplete file
        raises ``TemplateStorageError`` (AC-032).
        """
        try:
            with self._lock:
                path = self._path(name)
                if not path.exists():
                    return None
                data = _load_yaml(path.read_text(encoding="utf-8"))
                result = self._parse(name, data)
        except YAMLError as e:
            _logger.error(f"template storage failure: name={name} reason={e}", name=name, reason=e)
            raise TemplateStorageError(f"corrupted template file {name}: {e}") from e
        except TemplateStorageError as e:
            _logger.error(f"template storage failure: name={name} reason={e}", name=name, reason=e)
            raise
        _logger.debug(f"template loaded from storage: name={name}", name=name)
        return result

    def delete(self, name: str) -> None:
        """Unlink the template file; an absent file is a silent no-op."""
        with self._lock:
            path = self._path(name)
            if path.exists():
                path.unlink()

    def list(self) -> list[Template]:
        """Parse every ``*.yaml`` file in the directory, file-name ordered.

        One corrupted file fails the whole listing with
        ``TemplateStorageError`` — there is no partial result (AC-032).
        """
        templates: list[Template] = []
        try:
            with self._lock:
                for path in sorted(self._directory.glob("*.yaml")):
                    data = _load_yaml(path.read_text(encoding="utf-8"))
                    templates.append(self._parse(path.stem, data))
        except YAMLError as e:
            _logger.error(f"template storage failure: reason={e}", reason=e)
            raise TemplateStorageError(f"corrupted template file: {e}") from e
        except TemplateStorageError as e:
            _logger.error(f"template storage failure: reason={e}", reason=e)
            raise
        _logger.debug(f"templates loaded from storage: count={len(templates)}", count=len(templates))
        return templates

    def _parse(self, name: str, data: Any) -> Template:
        """Build a ``Template`` from a loaded document.

        ``name``, ``category`` and ``values`` are required and ``values`` must
        be a mapping; ``group`` is optional. Every violation raises
        ``TemplateStorageError`` naming the template.
        """
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
