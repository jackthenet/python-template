"""AC-019 / REQ-015: `AGENTS.md` names each feature's public install operation.

Spec: ``docs/specs/settings-public-registry-setter.md`` REQ-015 and AC-019, and
``docs/decisions/ADR-083`` (the public install operation is the discoverable way to replace a
feature singleton — the guidance is what makes a future change find it instead of the private slot).

AC-019 as written: **Given** ``AGENTS.md``, **When** its five "Using the …" sections are read,
**Then** each names that feature's install operation, **And** each states that installing over a
non-empty default logs a WARNING, **And** each keeps ``reset_*()`` as the test seam. REQ-015 fixes
the granularity: **one bullet** in that feature's section naming the function, its
replace-plus-WARNING semantics, and that ``reset_*()`` stays the test seam. So the witness looks
for one bullet per feature carrying all three, inside that feature's own section — a bullet in the
wrong section does not satisfy AC-019's "its feature's … section".

Derivation notes (this test is derived from the spec text, not from the implementation):

* the five install/reset names come from the spec's §3.1 owner table (lines 78-82);
* the two section headings that do not exist yet — ``Using the Permissions Feature`` and
  ``Using the Session Management Feature`` — are fixed by the recorded answer to **Q-30**
  (``docs/questions/settings-public-registry-setter.md``, 2026-10-07): AC-019 is satisfied
  literally, ``AGENTS.md`` gains those two sections in the existing house form, and D13's
  "no new section" clause is amended in this change's own PR;
* "replace-plus-WARNING semantics" is witnessed by a bullet that contains both the literal
  ``WARNING`` (the level AC-003 requires) and a replace marker (``non-empty`` / ``replace*``) —
  the two words the requirement itself uses. Nothing else about the wording is pinned: the test
  does not care how the bullet is phrased, where in the section it sits, or how the section is
  otherwise written, so it cannot force a particular prose style on T-012's implementation;
* the reset clause accepts the feature's own ``reset_<slot>()`` name **or** the generic
  ``reset_*()`` spelling AC-019 uses.

``AGENTS.md`` is read from the repository root resolved through this file's own location, never
from the caller's CWD (PROBLEMS.md P-57). The file is documentation, so the test asserts on its
text; it is not part of the mkdocs site (that builds ``userdocs/``), so the docs gate is
unaffected by what T-012 writes here.
"""

from __future__ import annotations

from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
_AGENTS_MD = _REPO_ROOT / "AGENTS.md"

# (feature, its "Using the …" section heading, install operation, reset operation).
# Names: docs/specs/settings-public-registry-setter.md §3.1; headings: the three existing
# AGENTS.md sections plus the two Q-30 adds.
_FEATURES: tuple[tuple[str, str, str, str], ...] = (
    ("settings", "Using the Settings Feature", "set_settings_registry", "reset_settings_registry"),
    ("eventbus", "Using the Event Bus Feature", "set_event_bus", "reset_event_bus"),
    ("permissions", "Using the Permissions Feature", "set_permission_service", "reset_permission_service"),
    ("search", "Using the Search Feature", "set_search_service", "reset_search_service"),
    ("sessionmanagement", "Using the Session Management Feature", "set_session_service", "reset_session_service"),
)

# AC-003's level, quoted as the spec spells it, and the two words REQ-015 uses for the
# "replace-plus-WARNING semantics" the bullet must state.
_WARNING = "WARNING"
_REPLACE_MARKERS: tuple[str, ...] = ("non-empty", "replace")

# AC-019 writes the test seam as `reset_*()`; accepting that spelling alongside the feature's own
# reset name keeps the witness on the requirement's wording instead of on one implementation's.
_GENERIC_RESET = "reset_*"


def _section(text: str, heading: str) -> str | None:
    """The body of ``## <heading>``, up to the next level-2 heading (``None`` if absent)."""
    marker = f"## {heading}\n"
    start = text.find(marker)
    if start < 0:
        return None
    rest = text[start + len(marker) :]
    end = rest.find("\n## ")
    return rest if end < 0 else rest[:end]


def _bullets(section: str) -> list[str]:
    """The top-level ``- `` bullets of ``section``, each joined across its continuation lines.

    AGENTS.md writes one long line per bullet, but a wrapped bullet must read as one bullet, so a
    non-blank line that opens no new bullet continues the current one.
    """
    bullets: list[str] = []
    current: list[str] = []
    for line in section.splitlines():
        if line.startswith("- "):
            if current:
                bullets.append(" ".join(current))
            current = [line[2:]]
        elif not line.strip():
            if current:
                bullets.append(" ".join(current))
                current = []
        elif current and not line.startswith(("#", "```")):
            current.append(line.strip())
    if current:
        bullets.append(" ".join(current))
    return bullets


def _names_install_rule(bullet: str, install: str, reset: str) -> bool:
    """Does this one bullet carry all three AC-019 clauses (REQ-015's "one bullet")?"""
    return (
        install in bullet
        and _WARNING in bullet
        and any(marker in bullet for marker in _REPLACE_MARKERS)
        and (reset in bullet or _GENERIC_RESET in bullet)
    )


def _guidance_findings(text: str) -> list[str]:
    """Every AC-019 clause that ``text`` (an AGENTS.md body) fails, one message per feature."""
    findings: list[str] = []
    for feature, heading, install, reset in _FEATURES:
        section = _section(text, heading)
        if section is None:
            findings.append(f"{feature}: AGENTS.md has no '## {heading}' section, so it cannot name {install}()")
            continue
        if install not in section:
            findings.append(f"{feature}: the '## {heading}' section never names {install}()")
            continue
        if not any(_names_install_rule(bullet, install, reset) for bullet in _bullets(section)):
            findings.append(
                f"{feature}: no single bullet in '## {heading}' names {install}() together with the"
                f" replace-plus-{_WARNING} semantics and {reset}() as the test seam"
                f" ('{heading}' has {len(_bullets(section))} bullet(s); none of them carries all three clauses)"
            )
    return findings


def test_ac_019_agents_md_names_installer() -> None:
    """AC-019 (REQ-015): each of the five features' ``## Using the … Feature`` section in
    ``AGENTS.md`` names its install operation, states that installing over a non-empty default logs
    a WARNING, and keeps ``reset_*()`` as the test seam.
    """
    assert _AGENTS_MD.is_file(), f"AGENTS.md not found at {_AGENTS_MD} — the guidance file is part of the contract"

    installs = [install for _, _, install, _ in _FEATURES]
    headings = [heading for _, heading, _, _ in _FEATURES]
    assert len(set(installs)) == len(_FEATURES), "fixture collision: the five install operations must be distinct"
    assert len(set(headings)) == len(_FEATURES), "fixture collision: the five section headings must be distinct"

    findings = _guidance_findings(_AGENTS_MD.read_text(encoding="utf-8"))
    assert findings == [], "AC-019 / REQ-015: AGENTS.md guidance for the five install operations:\n" + "\n".join(
        f"  - {finding}" for finding in findings
    )
