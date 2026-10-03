# TODO: python-3.15

Backlog item for one planned change, created at **P.1 Frame** from this template and named `python-3.15.md`. One file per change.

This is a **planning record, not normative**: like `docs/questions/`, it is committed directly to `main` (see "Phase P: PREPARE" in `AGENTS.md`). It carries no approval gate — the spec does.

- **Status:** QUESTIONS-ANSWERED  <!-- PREPARING | QUESTIONS-ANSWERED | READY | IN-WORKFLOW | WAITING | MERGED -->
- **Change type:** DOCS/CHORE  <!-- config/tooling only; escalates to REFACTOR if 3.15-only features are adopted in src/, or to ISSUE if an upgrade exposes a defect -->
- **Created:** 2026-10-03
- **Question file:** `docs/questions/python-3.15.md`
- **Spec:** n/a  <!-- DOCS/CHORE: no spec -->
- **Worktree:** <created at P.4> `../python-template_kopie-worktrees/chore/python-3.15`
- **Depends on:** none
- **Related specs:** none directly; every feature's tests run under the new interpreter

## Goal (one line)
Move the project's Python target from **3.14 to 3.15** — interpreter floor, tool pins and CI — with **no change in observable behavior**.

## Why
The template is pinned to 3.14 in five places: `requires-python = ">=3.14"` (`pyproject.toml:7`), mypy `python_version = "3.14"` (`:132`), ty `python-version = "3.14"` (`:143`, with the comment that it is pinned "explicitly for documentation"), and **11** `python-version: '3.14'` pins across `.github/workflows/quality.yml` (8), `lint.yml` (1) and `spec-validation.yml` (3 → 2). The local venv is 3.14.5. Python 3.15 was scheduled for release on **2026-10-01** (PEP 790, two days ago), and the project's own skill gates 3.15 features on exactly this: *"Use a 3.15-only feature only if the project's `requires-python` is `>=3.15` and CI runs on 3.15"* (`.agents/skills/python-best-practices/references/python-3.15.md:7`). So today the skill documents `frozendict`, `sentinel`, lazy imports (PEP 810), comprehension unpacking (PEP 798), `re.prefixmatch`, `TaskGroup.cancel()` and the Tachyon sampling profiler (PEP 799) — and the project is not allowed to use any of them.

**Reality check (measured 2026-10-03):** `uv python list` offers only `cpython-3.15.0b1` (plus `+freethreaded`) — no final 3.15.0 build is installed or downloadable through uv on this machine. Pinning CI to a beta would make every failure ambiguous.

## In scope
**Decided at P.3 (2026-10-04): Option C — defer.** Nothing is pinned and no CI job changes.
- Record the **measured blocker** in `docs/verification/python-3.15.md`: only `3.15.0b1` exists, and the project has **no wheel-only solution on 3.15** — `pydantic==2.13.5` pins `pydantic-core==2.46.5`, which has no cp315 wheel; only the pre-release `pydantic 2.14.0b2` resolves. The code itself scores **0** against the 3.15 removal checklist.
- Record the **re-check trigger**: 3.15 final **and** a final `pydantic` shipping a cp315 wheel.
- Record the project's **support window**: the **latest two CPython versions** (Q-4) — with `requires-python >=3.14`, that is 3.14 + 3.15 once 3.15 is final.
- Point at the follow-up backlog item **`docs/todo/python-3.15-upgrade.md`** (framed 2026-10-04), which carries the trigger and inherits the checklist below — so the re-check is a scheduled change, not a note only findable in a closed record.
- The upgrade check the skill already prescribes (for that follow-up): `uv run --isolated --python 3.15 pytest -W error::DeprecationWarning`.
- The 3.15 behavior-change checklist applied to this repo (from `references/python-3.15.md`): `@contextmanager` now keeps the context open while the generator runs; `sqlite3.connect()` keyword-only arguments (the repo is SQLite-heavy via SQLModel — user-management, authentication, session-management, file-management, permissions, settings); `datetime.strptime` day-without-year → `ValueError`; `argparse` dest change; removals (`sre_*`, `http.server` CGI handler, `platform.java_ver()`, keyword-argument `NamedTuple`); `typing.ByteString` deprecation; UTF-8 default encoding (PEP 686) — but keep passing `encoding="utf-8"` explicitly.
- The concrete 3.15-era idiom hits in this repo: `re.match` → `re.prefixmatch` at `src/backend/filemanagement/service.py:366,370`, `src/backend/filemanagement/storage.py:103`, `src/backend/search/service.py:84,88` (5 sites; `re.match` is soft-deprecated, never removed — so this is optional and only under Option B).
- Dependency wheel availability for 3.15 before anything is pinned: `pydantic-core`, `pillow`, `argon2-cffi(-ffi)`, `sqlalchemy/sqlmodel`, `ruamel-yaml`, `httpx`, plus the dev tools (ruff, mypy, ty, pytest).
- Docs touch-ups where the version is stated (`README.md`, `userdocs/`, `AGENTS.md` "Python 3.14+" line) — text only.

## Out of scope
- Any pin change at all — `requires-python`, mypy/ty, the 11 CI `python-version` literals, `uv.lock` (Q-1 = C).
- Consolidating the 11 CI `python-version` literals into one `strategy.env`/matrix value — follow-up for `python-3.15-upgrade`.
- `re.match` → `re.prefixmatch` (5 sites) — the skill's version gate forbids 3.15-only features until `requires-python >=3.15` **and** CI runs 3.15; follow-up for `python-3.15-upgrade`.
- Free-threaded (`+freethreaded`) builds / PEP 703 support (Q-5, moot).
- Dropping Windows/Linux parity, changing `uv` configuration, or re-pinning unrelated dependencies.
- The JIT (`PYTHON_JIT=1`) — measure first, decide later; not part of this change.

## Affected features
No `src/` path under Option A. Under Option B: the five `re.match` sites above plus any 3.15 fixups the check reveals. Config: `pyproject.toml`, `.github/workflows/{quality,lint,spec-validation}.yml`, optionally a `.python-version` file (none exists today).

## Constraints and risks
- **Beta vs final.** `uv python list` shows only `3.15.0b1` today. A beta in CI makes red builds uninterpretable; P.3 must decide: wait for the final release, or add it as an `allow-failure` matrix entry.
- **Compiled wheels gate everything.** pydantic-core, pillow and argon2-cffi must ship 3.15 wheels or `uv sync` fails in CI — check before writing the pin, not after.
- **Tool support lags the language.** mypy 2.3.1 / ty 0.0.84 / ruff 0.16.9 must understand 3.15 syntax and the new typing forms (`TypeForm`, `TypedDict(closed=True)`, `extra_items`) — the skill warns mypy did not yet accept `extra_items`.
- **Behavior changes are the escalation trigger.** If the 3.15 run surfaces a real defect (e.g. a `sqlite3.connect` call passing positional args through SQLModel, or a `@contextmanager` assumption), that is an ISSUE, not a chore; if a fixup changes observable behavior, reclassify per the Escalation Rules.
- **Suite parity is the gate.** The full suite result under 3.15 must match the 3.14 baseline with **zero test changes** — the same discipline REFACTOR uses.
- **11 CI pins are easy to half-do.** A half-migrated matrix (some jobs 3.14, some 3.15) silently tests two different things; sweep all three workflow files in one step.

## Value triage (2026-10-03, pre-workflow)
- **Overlap:** the *procedure* already exists as guidance — `references/python-3.15.md` has the version gate, the behavior-change list and the exact upgrade-check command; nothing in the repo *applies* it. So this change is mostly executing a documented checklist against 3 config files + 11 CI pins, not designing anything.
- **Beneficiary:** future changes (they get permission to use 3.15 features and the skill's own gate stops blocking them) and anyone who installs the template on a current interpreter.
- **Score: 3/5** — genuine maintenance value and it unblocks the 3.15 features the skill recommends, but it delivers nothing user-visible, and it is partly blocked on external facts (final release, compiled wheels).
- **Recommendation: implement Option A now** (prove 3.15 compatibility, keep the 3.14 floor), **defer Option B** (raise the floor + adopt features) until 3.15 final wheels exist — that split keeps the cheap part unblocked and is one file-set per change.

## Acceptance signal (plain language)
CI is green on 3.15 (matrix entry under Option A, sole version under Option B), `uv run --isolated --python 3.15 pytest -W error::DeprecationWarning` passes locally with no deprecation warnings, the full suite result is identical to the 3.14 baseline with no test file touched, and the version statement in the docs matches the pin. `git diff --name-status` shows only `pyproject.toml`, the three workflow files, and doc text.

## Prep log
| Step | Date | Result |
|---|---|---|
| P.1 Frame | 2026-10-03 | TODO + question file created on `main`; type DOCS/CHORE (escalation candidates REFACTOR/ISSUE); todo set created; **value triage 3/5, implement Option A, defer Option B** |
| P.2 Interrogate (6 questions) | 2026-10-03 | **BLOCKED-USER** — 6 questions, 7 points closed from evidence, all facts **re-measured today**. 3.15 is still beta-only (`uv python list 3.15` → `cpython-3.15.0b1` only). **The hard blocker is pydantic, not the interpreter:** `uv pip install --python <3.15> --dry-run --no-build -r pyproject.toml` fails — `pydantic-core==2.46.5` has no cp315 wheel and `pydantic==2.13.5` pins it; with `--prerelease=allow` it resolves only to `pydantic==2.14.0b2`. Every other compiled dep already has a cp315 wheel (orjson, pillow, argon2-cffi-bindings, cffi, sqlalchemy, greenlet, pydantic-core 2.49.0). The code is clean on 3.15: the removal checklist scores **0** against `src/`, and PEP 758 (`src/backend/shared/principal.py:96`) **parses on 3.15.0b1**. Pin inventory re-counted: **14 pins + 1 comment** (`pyproject.toml:7,132,143`; `quality.yml:19,37,54,75,90,105,120`; `lint.yml:33`; `spec-validation.yml:35,64,78`) + `uv.lock:3`. **Reframe:** `requires-python >= 3.14` already permits 3.15 — the gap is CI *evidence*, not permission; and **no CI matrix exists** (11 jobs hard-pin the literal), so "add 3.15 to the matrix" is structural. **Collision:** `pyproject-tooling-gaps` edits the same 8 workflow job blocks (`quality.yml:19,37,…`) and `pyproject.toml:132` — sequence after it, or take Option C (defer) so the two never touch the same lines |
| P.3 Answer (7 answered) | 2026-10-04 | **RESOLVED** — Q-1 = **(C) defer**; Q-4 = **latest two CPython versions**; Q-2, Q-3, Q-5, Q-6 **closed as moot** by Q-1 = (C). Follow-up backlog item `python-3.15-upgrade` framed to carry the trigger |
| P.4 Draft scope + create branch/worktree | | |
| P.5 Self-consistency | | n/a (DOCS/CHORE) |
