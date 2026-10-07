# TODO: python-3.15-upgrade

Backlog item for one planned change, created at **P.1 Frame** from this template and named `python-3.15-upgrade.md`. One file per change.

This is a **planning record, not normative**: like `docs/questions/`, it is committed directly to `main` (see "Phase P: PREPARE" in `AGENTS.md`). It carries no approval gate — the spec does.

- **Status:** PREPARING  <!-- PREPARING | QUESTIONS-ANSWERED | READY | IN-WORKFLOW | WAITING | MERGED -->
- **Change type:** DOCS/CHORE  <!-- provisional: config/CI only; escalates to REFACTOR if 3.15-only features are adopted in src/, or to ISSUE if the upgrade exposes a defect -->
- **Created:** 2026-10-04
- **Question file:** `docs/questions/python-3.15-upgrade.md`
- **Spec:** n/a  <!-- DOCS/CHORE: no spec -->
- **Worktree:** <created at P.4> `../python-template_kopie-worktrees/chore/python-3.15-upgrade`
- **Depends on:** **trigger, not a change** — CPython 3.15 final **and** a final `pydantic` release shipping a cp315 wheel. Until both hold this item is not startable.
- **Related specs:** none directly; every feature's tests run under the new interpreter

## Goal (one line)
Move the project's Python target from **3.14 to 3.15** — interpreter floor, tool pins and the 11 CI literals — with **no change in observable behavior**.

## Why
`python-3.15` (framed 2026-10-03) measured the blocker on 2026-10-03 and P.3 chose **Option C — defer** (Q-1): only `cpython-3.15.0b1` existed, and the project has **no wheel-only solution on 3.15** because `pydantic==2.13.5` pins `pydantic-core==2.46.5`, which ships no cp315 wheel — only the pre-release `pydantic 2.14.0b2` / `pydantic-core 2.49.0` resolves. Pinning CI to a beta interpreter plus a pydantic pre-release would make every future CI failure ambiguous. The code itself is clean: the 3.15 removal checklist scores **0** against `src/`, and PEP 758 (`src/backend/shared/principal.py:96`) already parses on 3.15.0b1.

This item is where the deferred work lives, so the re-check is a scheduled change rather than a note buried in a closed verification record. It also inherits the pin-consolidation follow-up: **11** `python-version: '3.14'` literals across `.github/workflows/quality.yml` (8), `lint.yml` (1) and `spec-validation.yml` (3) are hand-edited every year, and the project's stated support window is the **latest two CPython versions** (`python-3.15` Q-4).

## In scope
To be fixed at this item's P.2/P.3 once the trigger fires. Candidate scope carried over from `python-3.15`:
- Re-run the measurement first: `uv python list 3.15`, then `uv pip install --python <3.15> --dry-run --no-build -r pyproject.toml`. If it resolves wheel-only, the trigger has fired.
- The upgrade check the skill prescribes: `uv run --isolated --python 3.15 pytest -W error::DeprecationWarning`.
- The 3.15 behavior-change checklist applied to this repo (from `references/python-3.15.md`): `@contextmanager` now keeps the context open while the generator runs; `sqlite3.connect()` keyword-only arguments (the repo is SQLite-heavy via SQLModel — user-management, authentication, session-management, file-management, permissions, settings); `datetime.strptime` day-without-year → `ValueError`; `argparse` dest change; removals (`sre_*`, `http.server` CGI handler, `platform.java_ver()`, keyword-argument `NamedTuple`); `typing.ByteString` deprecation; UTF-8 default encoding (PEP 686) — but keep passing `encoding="utf-8"` explicitly.
- The pin inventory: `pyproject.toml:7` (`requires-python`), `:132` (mypy), `:143` (ty, plus its comment), `quality.yml:19,37,54,75,90,105,120`, `lint.yml:33`, `spec-validation.yml:35,64,78`, `uv.lock:3`, and the local venv (3.14.5 today).
- **Pin consolidation** (follow-up from `python-3.15` Q-4): replace the 11 duplicated CI literals with one `strategy.env`/matrix value so the next bump is one line, consistent with the "latest two" support window.
- `re.match` → `re.prefixmatch` at 5 sites (`src/backend/search/service.py:84,88`, `src/backend/filemanagement/service.py:366,370`, `src/backend/filemanagement/storage.py:103`) — permitted only once `requires-python >=3.15` **and** CI runs 3.15; if taken, this item reclassifies to REFACTOR.
- Docs touch-ups where the version is stated (`README.md`, `userdocs/`, the `AGENTS.md` "Python 3.14+" line) — text only.

## Out of scope
- 3.15-only **features** in `src/` beyond `re.prefixmatch` (lazy imports, `frozendict`, `sentinel`, Tachyon instead of `py-spy`) — a separate REFACTOR.
- Free-threaded (`3.15t`) CI — a separate axis with its own wheel-availability question; decide at P.2/P.3.
- The JIT (`PYTHON_JIT=1`) — measure first, decide later.
- Re-pinning unrelated dependencies, changing `uv` configuration, or dropping OS parity in CI.

## Affected features
No `src/` path unless `re.prefixmatch` is taken. Config: `pyproject.toml`, `uv.lock`, `.github/workflows/{quality,lint,spec-validation}.yml`, optionally a `.python-version` file (none exists today).

## Constraints and risks
- **Do not start before the trigger fires.** A beta interpreter plus a pydantic pre-release makes every red build uninterpretable — that is exactly why `python-3.15` deferred.
- **Compiled wheels gate everything.** `pydantic-core`, `pillow`, `argon2-cffi-bindings`, `greenlet`, `sqlalchemy` must ship cp315 wheels or `uv sync` fails in CI — check before writing the pin, not after.
- **Tool support lags the language.** mypy / ty / ruff must understand 3.15 syntax and the new typing forms (`TypeForm`, `TypedDict(closed=True)`, `extra_items`).
- **Collision: `pyproject-tooling-gaps`** edits the same 8 workflow job blocks (`quality.yml:19,37,…`) and `pyproject.toml:132`. Whichever merges second rebases those lines.
- **Suite parity is the gate.** The full suite under 3.15 must match the 3.14 baseline with **zero test changes**.
- **Half-migrated CI is worse than none.** A mix of 3.14 and 3.15 jobs silently tests two different things; sweep all three workflow files in one step.

## Value triage (2026-10-04, pre-workflow)
- **Overlap:** the *procedure* already exists as guidance — `.agents/skills/python-best-practices/references/python-3.15.md` carries the version gate, the behavior-change list and the check command; nothing in the repo *applies* it. This item is executing a documented checklist against config + CI, not designing anything.
- **Beneficiary:** future changes (they get permission to use 3.15 features and the skill's own gate stops blocking them) and anyone installing the template on a current interpreter.
- **Verdict:** **ACCEPT — scheduled, not startable.** Blocked on an external condition (3.15 final + a final pydantic with a cp315 wheel), not on a decision. Cost when unblocked is small and mechanical (14 pins + 11 CI literals + one lockfile regeneration).

## Preparation log

| Step | Date | Result |
|---|---|---|
| P.1 Frame | 2026-10-04 | Framed as the follow-up home for the work deferred by `python-3.15` Q-1 = (C); trigger recorded in `Depends on:`; value triage **ACCEPT (scheduled)** |
| P.2 Interrogate (34 questions) | 2026-10-05 | **BLOCKED-USER** — 34 questions (**Q-1 … Q-34**) recorded in `docs/questions/python-3.15-upgrade.md`, one batch, most-blocking first (Q-1 startability, Q-2/Q-3 the trigger definition, Q-4/Q-5 the trigger-independent pin consolidation). **Trigger has NOT fired** (re-measured 2026-10-05): only `cpython-3.15.0b1` exists, and `uv pip install --python 3.15 --dry-run --no-build -r pyproject.toml` is unsatisfiable (`pydantic-core==2.46.5` has no cp315 wheel). **Three corrections to this TODO**: (1) the trigger is under-specified — CI installs the **dev** group, where `pyyaml` has no cp315 wheel and `complexipy` ships no wheel at all, so the trigger command as written could fire into red `security`/`pre-commit` jobs (Q-2); (2) the pin inventory is stale — **12** CI literals, not 11 (`quality.yml:19,37,54,75,90,105,120,138`, `lint.yml:33`, `spec-validation.yml:35,64,78`), and `pyproject.toml:167 target-version = "py314"` was never counted because the 2026-10-03 grep searched `3.14`; (3) the stated `pyproject-tooling-gaps` collision is **already resolved** (MERGED as `a278bd2`) — the live collisions are `structure-map`, `codecov-coverage-badge` and `ruff-d-docstrings`. Checklist items closed from evidence without spending a question: `sqlite3.connect` (0 applicable sites), `strptime`/`argparse`/`sre_*`/`java_ver`/`NamedTuple`/`ByteString` (0 uses), PEP 758 parses; `re.match` emits **no** DeprecationWarning, so the skill's `-W error` check does not force `re.prefixmatch` (Q-19); 6 `@contextmanager` uses are in `tests/`, not `src/`. Parity baseline: **728 passed, 1 skipped** on 3.14.5 |
| P.3 Answer (<n> answered) | | |
| P.4 Draft scope + create branch/worktree | | |
| P.5 Self-consistency (FEATURE/CROSS-CUTTING) | | |
