# Questions: python-3.15-upgrade

One question file per change, created at **P.1 Frame** from this template and named `python-3.15-upgrade.md`. It replaces the retired central `AI_Questions.md` (archived at `docs/questions/archive-AI_Questions.md`).

- **Change:** python-3.15-upgrade (DOCS/CHORE, provisional)
- **TODO file:** `docs/todo/python-3.15-upgrade.md`
- **Spec:** n/a
- **Opened:** 2026-10-04
- **Status:** OPEN  <!-- OPEN | ALL ANSWERED — set OPEN by the orchestrator at P.1; ALL ANSWERED once every question in this file has an answer (the orchestrator records it together with the `QUESTIONS-ANSWERED` TODO advance) -->
- **Answer rounds:** 0

Every question that needs user input is recorded HERE — never in a central file. A step that needs input records **all** of its open questions in one batch and returns `BLOCKED-USER`; the orchestrator presents them (as few `ask_user_question` rounds as possible, <= 4 per round, most blocking first), records the answers here, marks each **ANSWERED** and **incorporated**, and relaunches the step **once** with the full answer set. The change is `WAITING` while its questions are unanswered — the orchestrator works on another change meanwhile, it does not idle.

### Entry format

```markdown
## Q-<n> — <short title>
- **Step:** <P.2 Interrogate, or Sx.x <step name> — Phase <n>>
- **Why needed:** <the ambiguity, missing requirement, or decision>
- **Context:** <what the step had learned at the time>
- **Question:** <the question for the user>
- **Answer:** <the user's answer>  (or **PENDING**)
- **Date:** <YYYY-MM-DD>
- **Status:** PENDING | ANSWERED
- **Incorporated:** no | yes — <where: REQ-XXX / AC-XXX / spec section / decision>
```

## Preparation questions (P.2)

**P.2 Interrogate — 2026-10-05.** **34 questions**, one decision each, most blocking first. The trigger is re-measured today (below) and **has not fired**, so Q-1…Q-3 decide startability and the trigger's own definition, Q-4…Q-6 are the **trigger-independent** scope (pin consolidation is doable today), and the rest are the decisions the upgrade forces once it is startable. Questions that cannot be answered before the trigger fires say so in `Why needed:`.

### Trigger measurement — 2026-10-05: **NOT FIRED**

| # | Command | Result |
|---|---|---|
| T1 | `uv python list 3.15` | `cpython-3.15.0b1-windows-x86_64-none  C:\Users\domin\AppData\Roaming\uv\python\cpython-3.15-windows-x86_64-none\python.exe` — **beta only**, and it is now **installed** (on 2026-10-03 it was `<download available>`) |
| T2 | `uv python list --all-versions \| rg 3\.15` | `3.15.0b1` + `3.15.0b1+freethreaded` only — **no final 3.15.0, no RC** |
| T3 | `uv python list --only-installed` | `cpython-3.15.0b1`, `cpython-3.14.5` (uv-managed), `cpython-3.12.3` (miniconda) |
| T4 | `uv python find` / `uv run python -V` | `.venv\Scripts\python.exe` → **`Python 3.14.5`** (project venv unchanged by this step) |
| T5 | `uv venv $TEMP/py315-probe --python 3.15` (temp venv **outside** the repo) | `Using CPython 3.15.0b1` → probe interpreter is `Python 3.15.0b1` |
| T6 | `uv pip install --python <probe> --dry-run --no-build -r pyproject.toml` | `× No solution found … Because pydantic-core==2.46.5 has no usable wheels and pydantic==2.13.5 depends on pydantic-core==2.46.5 … And because only pydantic<=2.13.5 is available and python-template depends on pydantic>=2.13.5` + `hint: Pre-releases are available for pydantic in the requested range (e.g., 2.14.0b2)` — **identical to the 2026-10-03 blocker** |
| T7 | `uv pip install --python <probe> --dry-run --no-build --group dev` | `× No solution found … Because complexipy==8.0.1 has no usable wheels` — `complexipy` ships **no wheel at all** (sdist-only, pure Python), so `--no-build` can never install it; this is **not** a 3.15 fact and the TODO's trigger command never sees it (`-r pyproject.toml` reads `[project].dependencies` only, while every CI job installs the **dev** group: `uv sync --only-group dev`) |
| T8 | per-package `--dry-run --no-build` probe on 3.15.0b1 | **cp315 wheels exist** for `pydantic-core` (2.49.0), `pillow`, `argon2-cffi-bindings`, `cffi`, `greenlet`, `sqlalchemy`, `orjson`, `py-spy`, `time-machine`, `ruff`, `mypy`, `ty`, `pytest`, `pre-commit`'s deps except pyyaml, `filetype`, `ruamel-yaml`, `loguru`, `email-validator`, `httpx`, `alembic`. **No cp315 wheel:** `pyyaml` (pulled by `bandit` and `pre-commit`) and `complexipy` (no wheel for any version) |

**Verdict: the trigger has NOT fired as of 2026-10-05.** 3.15 is still pre-release (`3.15.0b1` only, T1/T2) and the project still has **no wheel-only resolution on 3.15** (T6). Two blockers, not one: `pydantic` (the one recorded by `python-3.15` Q-1) **and `pyyaml`** (T8, new — it gates the `security` and `pre-commit` paths, and the TODO's trigger names neither). Everything else already ships cp315 wheels.

### Re-measured pin inventory (the TODO's numbers are stale)

| Where | Today (2026-10-05) | TODO says |
|---|---|---|
| `pyproject.toml:7` | `requires-python = ">=3.14"` | same |
| `pyproject.toml:137` | mypy `python_version = "3.14"` | `:132` (shifted by `pyproject-tooling-gaps`) |
| `pyproject.toml:150` + comment `:148-149` | ty `python-version = "3.14"` | `:143` |
| `pyproject.toml:167` | **ruff `target-version = "py314"` — missing from the TODO inventory entirely** (the 2026-10-03 grep searched for `3.14`, and `py314` does not match it) | not listed |
| `.github/workflows/quality.yml:19,37,54,75,90,105,120,138` | **8** `python-version: '3.14'` literals (the `complexity` job at `:138` was added by `pyproject-tooling-gaps`, merged as PR #68) | 7 (`:19,37,54,75,90,105,120`) |
| `.github/workflows/lint.yml:33` | 1 | 1 |
| `.github/workflows/spec-validation.yml:35,64,78` | 3 | 3 |
| **CI total** | **12 literals, 12 jobs, no `strategy.matrix` anywhere** | "11" |
| `uv.lock:3` | `requires-python = ">=3.14"` — and the lock already carries a `python_full_version >= '3.15'` resolution marker (`uv.lock:5`) | same |
| `.pre-commit-config.yaml:11` | ruff-pre-commit `rev: v0.15.12` — **older than the project's own `ruff>=0.16.9`** (`pyproject.toml:62`) | not listed |
| `README.md:6` | `[![Python >=3.14](…python-%3E%3D3.14-blue)…](pyproject.toml)` | "docs touch-ups" |
| `AGENTS.md:733` | `- **Language & Runtime:** Python 3.14+` | same |
| `docs/specs/structlog-logging.md:189` | NFR-001 budget measured on "Windows 11 / **Python 3.14.5** / 32 CPU" — the only spec text naming an interpreter | not listed |
| `userdocs/` | **no** Python version anywhere | assumed a touch-up |
| `.python-version` | **does not exist** | "optionally" |

### 3.15 behavior-change checklist, measured on 3.15.0b1 vs 3.14.5 (both run today)

| Item | 3.15.0b1 | 3.14.5 | Repo exposure |
|---|---|---|---|
| `re.prefixmatch` / `re.Pattern.prefixmatch` | both **present** | both absent | 5 module-level `re.match` sites (`src/backend/search/service.py:84,88`, `src/backend/filemanagement/service.py:366,370`, `src/backend/filemanagement/storage.py:103`) **+ 3 compiled-pattern `.match()` sites the TODO misses** (`src/backend/permissions/catalog.py:41`, `src/backend/permissions/service.py:209,355`) = **8** |
| `re.match` DeprecationWarning | **none** (soft-deprecation emits no warning) | none | the prescribed `-W error::DeprecationWarning` check does **not** force the rename |
| `sqlite3.connect()` keyword-only | `TypeError: connect() takes at most 1 positional arguments (2 given)` | DeprecationWarning | **closed**: 0 uses in `src/`; the 2 test uses pass the path only (`tests/acceptance/usermanagement/test_multi_role.py:150`, `tests/integration/permissions/test_persistence.py:158`); SQLAlchemy 2.0.52's pysqlite dialect builds `create_connect_args` → `(cargs, cparams)` and passes `timeout`/`check_same_thread`/`uri` as **keywords** (`.venv/Lib/site-packages/sqlalchemy/dialects/sqlite/pysqlite.py:642-675`) |
| `datetime.strptime` day-without-year | `ValueError: Day of month directive '%d' may not be used without a year directive` | ValueError with the old wording + DeprecationWarning | **closed**: 0 `strptime` uses in `src/`, `tests/`, `scripts/`, `migrations/` |
| `argparse` dest change | — | — | **closed**: 0 `argparse` uses anywhere |
| `sre_compile`/`sre_constants`/`sre_parse` | `ModuleNotFoundError` | DeprecationWarning | **closed**: 0 uses |
| `http.server` CGI handler | absent | **already absent on 3.14.5** | **closed / moot** |
| `platform.java_ver()` | absent | present | **closed**: 0 uses |
| keyword-argument `NamedTuple("P", x=int)` | `TypeError` | DeprecationWarning | **closed**: 0 uses |
| `typing.ByteString` | importable, `DeprecationWarning` (removal 3.17) | silent | **closed**: 0 uses — but a **third-party** import of it would break the `-W error::DeprecationWarning` check (unmeasurable until the deps install on 3.15) |
| PEP 686 default encoding | `sys.getdefaultencoding() == 'utf-8'` | **already `utf-8` on 3.14.5** | 22 explicit `encoding="utf-8"` sites (5 `src/`, 9 `scripts/`, 8 `tests/`) + `sys.stdout.reconfigure(encoding="utf-8")` (`scripts/verify_spec.py:74`) |
| `@contextmanager` generator timing | probed 2 shapes (normal exit + exception-with-retry): **identical order** on both | identical | **0 uses in `src/`/`scripts/`/`migrations/`; 6 in `tests/`** (`tests/eventbus_test_helpers.py:50`, `tests/logging_coverage_test_helpers.py:155`, `tests/logging_test_helpers.py:41`, `tests/settings_test_helpers.py:136`, `tests/tooling_test_helpers.py:43,56`) — `python-3.15` F10 grepped only `src/` and reported 0 |
| `frozendict` / `sentinel` builtins | present | absent | not used (out of scope per the TODO) |

**Tool support measured today:** `uv run mypy --python-version 3.15 -c "x: int = 1"` → `Success` (mypy 2.3.1); `uv run ty check --python-version 3.15 <file>` → `All checks passed!` (ty 0.0.84); `uv run ruff check --no-cache --target-version py315 <file>` → `warning: Support for Python 3.15 is under development and may be unstable. Enable preview to remove this warning.` + `All checks passed!` (ruff 0.16.9).

**Suite baseline today (the parity gate's number):** `uv run pytest tests/ -q` on 3.14.5 → **`728 passed, 1 skipped in 193.54s`**; the single skip is host-dependent (`tests/acceptance/filemanagement/test_filemanagement.py:364` `pytest.skip("symlinks not available on this host")`).

### Overlap check (all 22 non-template TODO files read; `docs/specs/` grepped)

- **`pyproject-tooling-gaps` — MERGED (PR #68, merged as `a278bd2`, S7.1 cleanup 2026-10-05).** The collision the TODO lists as a live risk is **already resolved**: it landed, and it is *why* the inventory is stale — it added the `complexity` job (`quality.yml:138`, hence **12** literals not 11) and shifted mypy to `:137` / ty to `:150`. Nothing to sequence against; the TODO's "Collision" risk line is stale and should be corrected at P.4.
- **`structure-map` — QUESTIONS-ANSWERED, next step P.4 (live collision).** Its Q-28a answer is binding: "`uv run mypy scripts/` joins the gate … the CI quality job (`quality.yml`)", and it also adds a `.pre-commit-config.yaml` local hook and one `AGENTS.md` line — i.e. it edits the **same `type-check` job block** as `quality.yml:19`, plus two files this change would touch (`.pre-commit-config.yaml:11`, `AGENTS.md:733`). Q-31 decides the sequence.
- **`codecov-coverage-badge` — PREPARING.** Owns `.github/workflows/quality.yml` + `README.md`; it edits the `coverage` job block (`quality.yml:45-58`) that contains the `python-version` literal at `:54`, and the README badge row that contains `README.md:6`.
- **`docs-path-ci-trigger` — PREPARING.** Edits `on.paths` in the workflow files (same files, different keys).
- **`ruff-d-docstrings` — PREPARING.** Edits `[tool.ruff.lint] select` — the same `[tool.ruff]` config area as `target-version` (`pyproject.toml:167`).
- **`tenacity-rich-cachetools` — PREPARING (FEATURE).** Would add dependencies → `pyproject.toml` + `uv.lock` churn in the same region; relevant to Q-12 (lockfile) and Q-31 (sequence).
- **`value-triage-gate` — QUESTIONS-ANSWERED.** Adds the `DROPPED` status and `docs/todo/archive/`; affects how this TODO file is retired, not this change's scope.
- **`security-changelog-license` — QUESTIONS-ANSWERED.** Would add badges to `README.md` — same badge row as `README.md:6` (Q-27).
- **`track-python-skill` — MERGED.** It delivered `.agents/skills/python-best-practices/references/python-3.15.md`, the file whose version gate and check command this change executes — the procedure is not re-specified here.
- **`update-readme` / `workflow-docs-nits` / `architecture-tests-missing` / `session-lookup-unwired` — MERGED.** No open collision.
- **`docs/specs/`:** no spec pins a Python version or relies on 3.14-only syntax; the only interpreter text is the NFR-001 measurement environment in `docs/specs/structlog-logging.md:189` (Q-28).

### Closed from evidence (not asked)

- **`sqlite3.connect()` keyword-only, `strptime`, `argparse`, `sre_*`, `http.server` CGI, `platform.java_ver()`, keyword-arg `NamedTuple`, `typing.ByteString`:** **zero applicable sites** in `src/`, `tests/`, `scripts/`, `migrations/` (table above, measured today). No scope item, no question.
- **PEP 758 (`except A, B:`) at `src/backend/shared/principal.py:96`:** verified parsing on 3.15.0b1 by `python-3.15` F9; unchanged today.
- **The upgrade-check command** is settled by the skill (`uv run --isolated --python 3.15 pytest -W error::DeprecationWarning`); it belongs in the P.4 scope record, not in a question.
- **`re.prefixmatch` is a pure rename, not a semantic change:** measured `re.prefixmatch` ≡ `re.match` on 3.15.0b1, and all 5 module-level patterns are `^…$`-anchored (`src/backend/filemanagement/models.py:94-95`, `src/backend/search/models.py:33-34`), so no behavior delta is possible — the REFACTOR gate (zero test changes) is satisfiable.
- **`docs/specs/` needs no amendment for the pins themselves** (no spec cites a version) — the one exception is the NFR-001 measurement note, asked as Q-28.

## Q-1 — Is this change startable today?

- **Step:** P.2 (Phase P)
- **Why needed:** the TODO says the item is "not startable" until the trigger fires; today's re-measurement (T1–T8) says it has **not** fired. Whether P.4 runs at all — and whether the change enters the workflow with unanswered questions — depends on this answer.
- **Context:** T1/T2 — only `3.15.0b1` exists (no final, no RC). T6 — `pydantic==2.13.5` pins `pydantic-core==2.46.5`, which has no cp315 wheel; only `pydantic 2.14.0b2` resolves. `python-3.15` Q-1 chose (C) defer for exactly this reason. Meanwhile the pin consolidation (Q-4) is trigger-independent and doable today.
- **Options:**
  1. (Recommended) **Not startable for the 3.15 part; answer the trigger-independent questions now.** P.4 stays blocked; the scope record is drafted but the pins are not written until the trigger re-fires, and the answer batch is still worth recording because it fixes the trigger definition (Q-2/Q-3) and the scope boundary.
  2. **Split now:** keep this TODO blocked on 3.15, and open a separate `chore/ci-python-pin-consolidation` TODO (Q-4) that is startable today.
  3. **Start today against `3.15.0b1` + `pydantic 2.14.0b2`** — re-litigates `python-3.15` Q-1 and makes every future red CI build ambiguous.
- **Question:** Does this change stay blocked until the trigger fires, or does it (also) start now on the trigger-independent part?
- **Answer:** **PENDING**
- **Date:** -
- **Status:** PENDING
- **Incorporated:** no

## Q-2 — What exactly is the trigger condition (which package set)?

- **Step:** P.2 (Phase P)
- **Why needed:** the TODO's trigger ("3.15 final **and** a final `pydantic` with a cp315 wheel") is narrower than what CI actually installs, and today's measurement found a **second** missing wheel (`pyyaml`) that the trigger does not mention. A trigger that is satisfiable on paper but not in CI would let the change start into red builds.
- **Context:** T6 (runtime deps: pydantic blocks), T7 (dev group: `complexipy` has no wheel at all, so `--no-build` can never resolve the dev group), T8 (`pyyaml` has no cp315 wheel; it is pulled by `bandit` — the `security` job — and by `pre-commit`). Every CI job installs the dev group (`quality.yml:21`, `lint.yml`, `spec-validation.yml`), not the runtime group alone.
- **Options:**
  1. (Recommended) **Runtime + dev group resolve on a final 3.15, with pure-Python sdists exempted:** require wheels for compiled packages only (`pydantic-core`, `pillow`, `argon2-cffi-bindings`, `cffi`, `greenlet`, `sqlalchemy`, `orjson`, `pyyaml`, `py-spy`, `time-machine`) and allow source builds for wheel-less pure-Python packages (`complexipy`).
  2. **Keep the TODO's wording** (3.15 final + final `pydantic` with a cp315 wheel) — cheapest to state, but it ignores `pyyaml` and the dev group.
  3. **Strict wheel-only for every package in both groups** — never satisfiable today because `complexipy` ships no wheel at all.
  4. **`uv sync` simply succeeds on 3.15** (source builds allowed everywhere) — weakest signal; a slow or failing source build in CI is then indistinguishable from a real failure.
- **Question:** Which package set must resolve (and how) before this change may start?
- **Answer:** **PENDING**
- **Date:** -
- **Status:** PENDING
- **Incorporated:** no

## Q-3 — What counts as "3.15 final"?

- **Step:** P.2 (Phase P)
- **Why needed:** the trigger's first half is an external release fact, and three different observable conditions are possible. The change needs one checkable condition, or the re-check will be argued again in six months.
- **Context:** T1/T2 — `uv` offers only `3.15.0b1` on this machine; PEP 790 scheduled 3.15.0 for 2026-10-01, which has passed, so the release itself is late rather than the tooling. CI runs `actions/setup-python@v7` on `ubuntu-latest`, which has its own availability lag.
- **Options:**
  1. (Recommended) **`uv python list 3.15` offers a non-pre-release `3.15.x`** — the same command the scope record already re-runs, so the check is one line.
  2. **python.org has released 3.15.0 final** regardless of whether `uv` or `setup-python` can install it yet.
  3. **Both `uv` and `actions/setup-python` can install it on `ubuntu-latest`** — strongest, but adds a second external dependency to the wait.
- **Question:** Which observable condition marks "3.15 final" for this trigger?
- **Answer:** **PENDING**
- **Date:** -
- **Status:** PENDING
- **Incorporated:** no

## Q-4 — Pin consolidation: separate change, or part of this one?

- **Step:** P.2 (Phase P)
- **Why needed:** this is the one scope item that is **fully doable today** (no 3.15 needed), and the answer decides whether the orchestrator opens another TODO now and whether this item's "not startable" status is even accurate.
- **Context:** 12 duplicated `python-version: '3.14'` literals (inventory above); `python-3.15` Q-4 decided the support window is "latest two CPython versions" and explicitly left consolidation out as a follow-up for *this* change; the annual re-edit is what makes the pin inventory go stale (it already went stale once: `pyproject-tooling-gaps` added a 12th literal).
- **Options:**
  1. (Recommended) **Separate change, opened now** (`chore/ci-python-pin-consolidation`): trigger-independent, startable today, and it makes the eventual 3.15 bump a one-line edit — this change then only changes one value.
  2. **Part of this change** — one PR, but it makes this change startable today for that half and mixes a CI refactor with a blocked upgrade.
  3. **Never** — keep the literals and accept the annual 12-line edit.
- **Question:** Is the 12-literal consolidation a separate startable-now change, part of this blocked change, or dropped?
- **Answer:** **PENDING**
- **Date:** -
- **Status:** PENDING
- **Incorporated:** no

## Q-5 — If consolidated: which mechanism?

- **Step:** P.2 (Phase P)
- **Why needed:** there is no matrix in this repo (12 jobs, each hard-pinned), so "one place to change the version" has four different implementations with different costs and different failure modes.
- **Context:** `quality.yml:19,37,54,75,90,105,120,138`, `lint.yml:33`, `spec-validation.yml:35,64,78`; all use `actions/setup-python@v7`; `astral-sh/setup-uv@v7` precedes each. A matrix renames job artifacts (`coverage (3.14)`), which the codecov badge change (`codecov-coverage-badge`) and the README badges then have to account for.
- **Options:**
  1. (Recommended) **Workflow-level `env: PYTHON_VERSION: '3.14'`** in each of the three files, with `python-version: ${{ env.PYTHON_VERSION }}` per job — three lines to edit, no job-name change, no CI-minute cost.
  2. **`strategy.matrix.python-version: ['3.14']`** per job — ready for two versions immediately, but renames jobs/artifacts and doubles minutes when the list grows.
  3. **A composite action** (`.github/actions/setup-python-uv/action.yml`) used by all 12 jobs — one place total, but a new CI element to maintain.
  4. **A repository variable** (`vars.PYTHON_VERSION`) — single source across files, but unavailable to fork PRs, so it silently breaks external contributions.
- **Question:** Which consolidation mechanism should the change use?
- **Answer:** **PENDING**
- **Date:** -
- **Status:** PENDING
- **Incorporated:** no

## Q-6 — Who installs the interpreter in CI: `setup-python` or `uv`?

- **Step:** P.2 (Phase P)
- **Why needed:** the repo has two interpreter providers in every job, and a 3.15 rollout can fail in one and not the other. The answer decides which pin actually gates the upgrade.
- **Context:** every job runs `astral-sh/setup-uv@v7` **then** `actions/setup-python@v7` with the literal, then `uv sync --only-group dev` (e.g. `quality.yml:14-21`). `uv` can install and select the interpreter itself (`uv python install 3.15`, `uv run --python 3.15`), and T1 shows `uv` already has 3.15.0b1 while `setup-python` may lag.
- **Options:**
  1. (Recommended) **Keep `setup-python` as the provider** (status quo) and treat its support for `'3.15'` as part of the trigger — smallest diff, no new CI element.
  2. **Let `uv` own the interpreter** (`uv python install` + drop `setup-python`) — one provider, uv's faster availability, but 12 job blocks change and the `uv.lock`/`.venv` story shifts.
  3. **Both, pinned consistently** — `setup-python` for the runner PATH and `uv python pin` for the venv; strongest, most moving parts.
- **Question:** Which tool is the authoritative interpreter provider in CI after the upgrade?
- **Answer:** **PENDING**
- **Date:** -
- **Status:** PENDING
- **Incorporated:** no

## Q-7 — What does `requires-python` become?

- **Step:** P.2 (Phase P)
- **Why needed:** it is the compatibility promise the template makes to whoever installs it, and it decides whether `uv.lock` is regenerated (Q-12) and whether 3.14 users are cut off.
- **Context:** `pyproject.toml:7` is `>=3.14`; `python-3.15` Q-4 fixed the support window at **latest two CPython versions**; `uv.lock:3` mirrors it and must be regenerated if it moves. `requires-python >=3.14` already *permits* 3.15 — the gap is CI evidence, not permission.
- **Options:**
  1. (Recommended) **Keep `>=3.14`** — matches the "latest two" window; 3.15 becomes tested, not required; no lockfile regeneration.
  2. **Raise to `>=3.15`** — one supported version, unlocks 3.15-only features (`re.prefixmatch`, `frozendict`) unconditionally, but drops 3.14 users of the template and forces the local venv and lockfile move.
  3. **Decide at P.4 from the facts then current** (wheel availability, whether 3.16 is out) — honest, but leaves the scope record without a floor.
- **Question:** Does the floor stay `>=3.14` or move to `>=3.15` when the change runs?
- **Answer:** **PENDING**
- **Date:** -
- **Status:** PENDING
- **Incorporated:** no

## Q-8 — Which CI jobs run on 3.15, and in what shape?

- **Step:** P.2 (Phase P)
- **Why needed:** "CI runs on 3.15" is the skill's gate for using 3.15 features, but the repo has no matrix, so the shape decides the CI-minute cost and what "CI runs on 3.15" actually proves.
- **Context:** 12 jobs, no matrix; only two execute the test suite (`quality.yml:54` `coverage`, `spec-validation.yml:78` `tests`); the rest are lint/type/security/docs/migrations/complexity gates whose interpreter matters less. `python-3.15` Q-3 (same question there) was closed as moot by the defer decision, so it is genuinely open here.
- **Options:**
  1. (Recommended) **Matrix the two suite-executing jobs on `[3.14, 3.15]`**, leave the other ten on the single supported floor version — the suite is what proves interpreter compatibility, at ~2× the cost of two jobs.
  2. **Matrix all 12 jobs** — strongest signal (mypy/ty/ruff behavior on 3.15 is covered too), roughly doubles total CI minutes.
  3. **One dedicated 3.15 job** alongside the 3.14 jobs — cheapest, but a new job to keep in sync with the other gates.
  4. **Switch every job to 3.15 only** — no dual coverage at all; contradicts the "latest two" window unless Q-7 raises the floor.
- **Question:** Which jobs run 3.15, and as a matrix or as separate jobs?
- **Answer:** **PENDING**
- **Date:** -
- **Status:** PENDING
- **Incorporated:** no

## Q-9 — When does 3.14 leave the matrix?

- **Step:** P.2 (Phase P)
- **Why needed:** the "latest two" window implies a drop date, and without one the matrix grows every release (3.14+3.15, then 3.14+3.15+3.16) and the CI cost the TODO worries about returns.
- **Context:** `python-3.15` Q-4 = "latest two CPython versions"; PEP 790's fixed cadence means 3.16 is scheduled for 2027-10; the TODO's Constraints say half-migrated CI is worse than none.
- **Options:**
  1. (Recommended) **Slide at the next release:** 3.14 stays until 3.16 is final, then this same change pattern drops it — the window is always exactly two.
  2. **Drop 3.14 as soon as 3.15 is green in CI** — cheapest CI, but leaves the `>=3.14` floor untested (a promise the template makes but does not verify).
  3. **No drop policy** — record the window but leave the matrix decision to whoever edits it next.
- **Question:** What is the recorded rule for ending 3.14 coverage?
- **Answer:** **PENDING**
- **Date:** -
- **Status:** PENDING
- **Incorporated:** no

## Q-10 — Add a `.python-version` file?

- **Step:** P.2 (Phase P)
- **Why needed:** it would be a **new** version pin — a fourth place the interpreter is stated — and it interacts with both `uv` (which reads it for `uv run`/`uv sync`) and CI (which currently pins via `setup-python`).
- **Context:** no `.python-version` exists today (verified); the TODO lists it as "optionally"; the local venv is 3.14.5 (T4) purely because that is what `uv` resolved from `requires-python`.
- **Options:**
  1. (Recommended) **Do not add one** — `requires-python` plus the CI pins stay the only statements; fewer places to drift.
  2. **Add `.python-version` = the newest supported version** and have CI read it (via Q-5's mechanism) — one file becomes the source of truth for local and CI.
  3. **Add it pinned to the floor (3.14)** for local dev reproducibility only, CI unchanged.
- **Question:** Does the change introduce a `.python-version` file, and if so what does it pin?
- **Answer:** **PENDING**
- **Date:** -
- **Status:** PENDING
- **Incorporated:** no

## Q-11 — Is recreating the local `.venv` part of the change?

- **Step:** P.2 (Phase P)
- **Why needed:** the venv is per-worktree and gitignored, so "the local venv is on 3.15" is not something a PR can deliver — yet the acceptance signal in the sibling change assumed it. The scope record must say who does it.
- **Context:** T4 — the project venv is `Python 3.14.5`; AGENTS.md notes each worktree has its own `uv` environment; a floor change (Q-7 option 2) would make `uv sync` rebuild it automatically, a CI-only change would not.
- **Options:**
  1. (Recommended) **Out of scope for the PR; each developer's `uv sync` follows `requires-python`** — the change records the command, not the machine state.
  2. **In scope for the change worktree:** the agent runs `uv sync` there and records the resulting interpreter version as evidence.
  3. **Explicitly documented as a manual step** in the verification record with a checklist for developers.
- **Question:** Does the change own the local venv, or only the pins?
- **Answer:** **PENDING**
- **Date:** -
- **Status:** PENDING
- **Incorporated:** no

## Q-12 — Is `uv.lock` regenerated as part of this change?

- **Step:** P.2 (Phase P)
- **Why needed:** the TODO counts "one lockfile regeneration" as part of the cost, but under the recommended floor (Q-7 option 1) nothing in the lock changes — and regenerating it anyway would sweep unrelated dependency drift into a config-only PR.
- **Context:** `uv.lock:3` `requires-python = ">=3.14"`, and the lock **already contains** a `python_full_version >= '3.15'` resolution marker (`uv.lock:5`), so 3.15 resolution is partly recorded today; a full regeneration would also pull in whatever new releases exist (the `tenacity-rich-cachetools` TODO would add deps to the same region), and `pydantic` cannot resolve on 3.15 at all (T6).
- **Options:**
  1. (Recommended) **Only if `requires-python` changes** — a CI-only upgrade leaves the lock untouched.
  2. **Regenerate unconditionally** so the lock records the 3.15-era resolution — drags unrelated version churn into the PR.
  3. **Regenerate in a separate dependency-update change** (the existing `dependency-updates` verification record shows that pattern) and keep this PR pin-only.
- **Question:** Does this change regenerate `uv.lock`?
- **Answer:** **PENDING**
- **Date:** -
- **Status:** PENDING
- **Incorporated:** no

## Q-13 — Should CI verify the lockfile (`--locked`) as part of this change?

- **Step:** P.2 (Phase P)
- **Why needed:** no CI job currently checks that `uv.lock` matches `pyproject.toml`, so a version-pin change can silently leave the lock stale — exactly the failure mode this change creates if it edits `requires-python`.
- **Context:** every job runs `uv sync --only-group dev` with no `--locked`/`--frozen` (`quality.yml:21,39,56,77,92,107,122,140`, plus `lint.yml` and `spec-validation.yml`); `uv.lock:3` is a derived artifact nobody gates.
- **Options:**
  1. (Recommended) **Out of scope here** — open it as its own chore; this change stays pin-only.
  2. **Add `--locked` to the existing sync steps in this change** — one flag per job, catches drift forever, but widens the diff to 12 lines that are not about versions.
  3. **Add a dedicated `lock-drift` job** (`uv sync --locked` only) — clear signal, one more job.
- **Question:** Does this change add lockfile-freshness enforcement to CI?
- **Answer:** **PENDING**
- **Date:** -
- **Status:** PENDING
- **Incorporated:** no

## Q-14 — Do the mypy and ty pins move to 3.15?

- **Step:** P.2 (Phase P)
- **Why needed:** the two tool pins are the only place that decides which language version the type checkers *check against*, and they can move independently of the floor — an inconsistency the `ty` comment at `pyproject.toml:148-149` explicitly documents.
- **Context:** `pyproject.toml:137` mypy `python_version = "3.14"`, `:150` ty `python-version = "3.14"`; measured today: mypy 2.3.1 accepts `--python-version 3.15`, ty 0.0.84 accepts `--python-version 3.15`. The `ty` comment says it is pinned "explicitly for documentation" even though ty infers from `requires-python`.
- **Options:**
  1. (Recommended) **Keep both at the floor version** (3.14 while `requires-python` is `>=3.14`) — the checkers must accept everything the supported range allows; they move only if the floor moves.
  2. **Move both to 3.15** — checks against the newest interpreter, but stops flagging 3.15-only syntax as unavailable to 3.14 users.
  3. **Delete the explicit pins and let both infer from `requires-python`** — one source of truth, loses the documented intent the comment records.
- **Question:** What do the mypy and ty version pins become when 3.15 lands?
- **Answer:** **PENDING**
- **Date:** -
- **Status:** PENDING
- **Incorporated:** no

## Q-15 — Is ruff's `target-version = "py314"` in scope?

- **Step:** P.2 (Phase P)
- **Why needed:** it is a **fourth version pin in `pyproject.toml` that the TODO's inventory does not list**, and leaving it behind is exactly the "half-migrated" state the TODO forbids — ruff would keep rewriting code to 3.14 idioms under a 3.15 target.
- **Context:** `pyproject.toml:167` `target-version = "py314"`; the 2026-10-03 inventory grepped `3.14`, which `py314` does not match, so it was never counted; ruff infers the target from `requires-python` when the key is absent.
- **Options:**
  1. (Recommended) **In scope: it moves with the floor** (and is added to the pin inventory in the scope record).
  2. **In scope but stays `py314` while the floor is 3.14** — i.e. explicitly tied to `requires-python`, not to the CI matrix.
  3. **Out of scope** — treat ruff's target as tooling detail; risks `UP` rules never firing for 3.15 idioms.
  4. **Delete the key** and let ruff infer from `requires-python` — removes a pin, loses an explicit statement.
- **Question:** Is `target-version` part of this change's pin set, and what does it become?
- **Answer:** **PENDING**
- **Date:** -
- **Status:** PENDING
- **Incorporated:** no

## Q-16 — How is ruff's "3.15 is under development" warning handled?

- **Step:** P.2 (Phase P)
- **Why needed:** setting `target-version = "py315"` on the installed ruff prints a warning on **every** ruff run (local, pre-commit, the lint job), and the lint job's output is the project's quality signal — a permanent warning is a decision, not an accident.
- **Context:** measured today: `uv run ruff check --no-cache --target-version py315 <file>` → `warning: Support for Python 3.15 is under development and may be unstable. Enable preview to remove this warning.` then `All checks passed!` (ruff 0.16.9).
- **Options:**
  1. (Recommended) **Defer the ruff target until ruff ships stable 3.15 support** — keep `py314`, record the deferral with the ruff version that clears it.
  2. **Accept the warning** — the target is set, the lint job still passes, the warning is noise in every run.
  3. **Set `preview = true` to silence it** — changes the whole rule set to preview rules, which is a much larger behavior change than a version bump.
- **Question:** What does the change do about ruff's unstable-3.15 warning?
- **Answer:** **PENDING**
- **Date:** -
- **Status:** PENDING
- **Incorporated:** no

## Q-17 — Is the pre-commit ruff revision drift fixed in this change?

- **Step:** P.2 (Phase P)
- **Why needed:** the pre-commit hook pins an **older ruff than the project requires**, so local autofixes and the CI lint gate can disagree — and the config's own comment says the revs are to be reviewed "any time the Python or CI toolchain changes materially", which is this change.
- **Context:** `.pre-commit-config.yaml:11` `rev: v0.15.12` vs `pyproject.toml:62` `"ruff>=0.16.9"`; `structure-map` also plans to add a local hook to the same file.
- **Options:**
  1. (Recommended) **In scope: align the hook rev with the project's ruff pin** — one line, same toolchain, removes a known inconsistency.
  2. **Out of scope: a separate chore** — keeps this PR strictly about interpreter versions.
  3. **Leave it** — accept that local ruff ≠ CI ruff.
- **Question:** Does this change bump `.pre-commit-config.yaml`'s ruff revision?
- **Answer:** **PENDING**
- **Date:** -
- **Status:** PENDING
- **Incorporated:** no

## Q-18 — Must the tool pins be bumped before the CI literals move?

- **Step:** P.2 (Phase P)
- **Why needed:** "tool support lags the language" is listed as a risk, but today's measurement shows the installed tools already accept a 3.15 target — so the change either needs a version gate or it does not, and that decides whether dependency bumps ride along (which would end the DOCS/CHORE classification).
- **Context:** measured: mypy 2.3.1, ty 0.0.84 and ruff 0.16.9 all accept a 3.15 target today (ruff with the Q-16 warning); the TODO's risk line assumes they may not; `python-3.15` Q-2 (is a dependency bump in scope?) was closed as moot by the defer decision, so it is open again here.
- **Options:**
  1. (Recommended) **No bump** — the installed versions already accept 3.15; the change stays config-only and DOCS/CHORE.
  2. **Require an official 3.15 support statement from each tool first** — safest, adds an external wait on top of the interpreter wait.
  3. **Bump ruff/mypy/ty to latest in the same PR** — one-shot modernization, but a dependency change inside a DOCS/CHORE scope.
- **Question:** Does the change require tool version bumps as a precondition?
- **Answer:** **PENDING**
- **Date:** -
- **Status:** PENDING
- **Incorporated:** no

## Q-19 — Is `re.prefixmatch` taken in this change?

- **Step:** P.2 (Phase P)
- **Why needed:** it is the escalation trigger written into the TODO: taking it makes the change **REFACTOR** (GREEN baseline, different todo set, different Phase 5 gate), and the skill's version gate only permits it once `requires-python >=3.15` **and** CI runs 3.15.
- **Context:** 5 module-level sites (`src/backend/search/service.py:84,88`, `src/backend/filemanagement/service.py:366,370`, `src/backend/filemanagement/storage.py:103`) plus 3 compiled-pattern sites (Q-20); measured: `re.prefixmatch` ≡ `re.match` on 3.15.0b1, all patterns are `^…$`-anchored, and `re.match` emits **no** DeprecationWarning — so the `-W error::DeprecationWarning` check will **not** force the rename.
- **Options:**
  1. (Recommended) **Defer to its own REFACTOR change** once the floor/CI gate is met — keeps this change config-only and DOCS/CHORE, and gives the rename its own GREEN-baseline discipline.
  2. **Take it here** — reclassifies this change to REFACTOR (baseline, full regression, no version bump) and couples an `src/` edit to a CI change.
  3. **Never** — `re.match` is soft-deprecated and never removed, so the sites are harmless.
- **Question:** Does the 3.15 upgrade change include the `re.prefixmatch` migration, or is it a separate change?
- **Answer:** **PENDING**
- **Date:** -
- **Status:** PENDING
- **Incorporated:** no

## Q-20 — If `prefixmatch` is taken: does it cover the compiled-pattern `.match()` sites too?

- **Step:** P.2 (Phase P)
- **Why needed:** the TODO's inventory says 5 sites; the real count is 8, and the 3 extra ones use the compiled-method form, which is a different API surface. A partial rename leaves the codebase in two idioms.
- **Context:** `src/backend/permissions/catalog.py:41`, `src/backend/permissions/service.py:209,355` use `_PERMISSION_KEY_PATTERN.match(...)` / `_ROLE_NAME_PATTERN.match(...)`; measured on 3.15.0b1: `re.Pattern.prefixmatch` **exists** (`hasattr(re.compile('a'), 'prefixmatch') == True`); `src/backend/settings/models.py:72,109` use `re.fullmatch` and are unaffected.
- **Options:**
  1. (Recommended) **All 8 sites** — module-level and compiled-method in one sweep, so no `re.match` remains.
  2. **Only the 5 module-level sites** — matches the TODO as written, leaves 3 `.match()` calls behind.
  3. **Module-level only, and additionally switch the 3 compiled patterns to module-level calls** — uniform style, slightly larger diff.
- **Question:** Which call sites does the rename cover?
- **Answer:** **PENDING**
- **Date:** -
- **Status:** PENDING
- **Incorporated:** no

## Q-21 — Is the `@contextmanager` behavior change audited in scope?

- **Step:** P.2 (Phase P)
- **Why needed:** the checklist names it first, the earlier change reported "0 sites" because it grepped only `src/`, and the real exposure is in the **test helpers** — which are the contract the parity gate relies on. Whether the change audits them, or trusts the suite, must be recorded.
- **Context:** 0 uses in `src/`, `scripts/`, `migrations/`; **6 uses in `tests/`** (`tests/eventbus_test_helpers.py:50`, `tests/logging_coverage_test_helpers.py:155`, `tests/logging_test_helpers.py:41`, `tests/settings_test_helpers.py:136`, `tests/tooling_test_helpers.py:43,56`); probed two shapes (normal exit, exception + re-raise) on 3.15.0b1 vs 3.14.5 — **identical** ordering.
- **Options:**
  1. (Recommended) **No separate audit** — the full-suite parity gate (Q-24) is the check; record the 6 sites and the probe result in the scope record.
  2. **Explicit audit item** — read all 6 helpers against the 3.15 semantics and record a per-site verdict.
  3. **Restructure the helpers** to not depend on finalization order — a test-only refactor inside a config change.
- **Question:** Does the change audit the 6 test-helper `@contextmanager` uses, or rely on the suite?
- **Answer:** **PENDING**
- **Date:** -
- **Status:** PENDING
- **Incorporated:** no

## Q-22 — What does the change do about explicit `encoding="utf-8"` (PEP 686)?

- **Step:** P.2 (Phase P)
- **Why needed:** the skill says keep passing it explicitly, the default is already UTF-8 on 3.14.5 (measured), and the repo has 22 explicit sites plus one `reconfigure` call — so "handle PEP 686" is either a no-op or a lint change, and the scope record must say which.
- **Context:** 5 `src/` sites (all `src/backend/settings/repository.py:138,148,246,256,278`), 9 in `scripts/`, 8 in `tests/`; `scripts/verify_spec.py:74` `sys.stdout.reconfigure(encoding="utf-8")`; `sys.getdefaultencoding()` is already `utf-8` on 3.14.5.
- **Options:**
  1. (Recommended) **No change** — keep every explicit `encoding="utf-8"`; record PEP 686 as a no-op for this repo.
  2. **Add a lint rule** that forbids opening text without an explicit encoding — enforces the convention, but ruff has no such rule today, so it means a custom check.
  3. **Drop the now-redundant `sys.stdout.reconfigure(encoding="utf-8")`** in `scripts/verify_spec.py:74` — a one-line simplification that changes behavior on non-UTF-8 consoles.
- **Question:** Is there any encoding-related work item in this change?
- **Answer:** **PENDING**
- **Date:** -
- **Status:** PENDING
- **Incorporated:** no

## Q-23 — What happens if a performance-budget test fails under 3.15?

- **Step:** P.2 (Phase P)
- **Why needed:** the repo's spec-defined time budgets were measured on 3.14.5, and 3.15 changes interpreter performance characteristics (JIT available, Tachyon, faster startup paths). A budget failure is a spec conflict, not a code bug, and the repo has already been through exactly this once.
- **Context:** `docs/verification/perf-budget-env-aware.md` — the settings NFR-001 budget failed at 65.4 ms vs 50 ms on CI and was resolved by a **Spec Amendment** (50 ms local / 100 ms CI); budgets live in `docs/specs/settings.md:345` NFR-001 (already amended twice for environment sensitivity), `docs/specs/structlog-logging.md:189` NFR-001 (`< 25 ms`, measured 0.85 ms on 3.14.5) and `tests/acceptance/eventbus/test_eventbus.py:19,45` (`_PUBLISH_BUDGET_S = 0.01`).
- **Options:**
  1. (Recommended) **Spec Amendment PR** for the affected budget (the precedent in `perf-budget-env-aware`), re-measured on 3.15 — this change then stays config-only and waits on that PR.
  2. **Reclassify this change to ISSUE** and fix the budget inside it — conflates a spec-budget change with the upgrade.
  3. **Quarantine the budget test** (`xfail` marked BROKEN + Problem Log entry) — keeps CI green but leaves an unmet NFR on record.
- **Question:** What is the pre-agreed response to a perf-budget failure under 3.15?
- **Answer:** **PENDING**
- **Date:** -
- **Status:** PENDING
- **Incorporated:** no

## Q-24 — What exactly must the parity gate compare, and where?

- **Step:** P.2 (Phase P)
- **Why needed:** "the full suite under 3.15 must match the 3.14 baseline with zero test changes" is the change's gate, but the baseline number is environment-dependent (today's host run has a host-caused skip), so the gate needs a defined environment and a defined equality.
- **Context:** today's baseline `uv run pytest tests/ -q` on 3.14.5 → **728 passed, 1 skipped** (skip: `tests/acceptance/filemanagement/test_filemanagement.py:364`, "symlinks not available on this host"); CI runs `ubuntu-latest` (`quality.yml:11` etc.), where that test is not skipped; the suite takes ~194 s locally.
- **Options:**
  1. (Recommended) **The CI run is the gate:** 3.14 and 3.15 matrix jobs on the same runner must produce identical pass/fail counts; the local host run is informational evidence.
  2. **Both environments must match their own 3.14 baseline** — strongest, but a Windows host baseline is not reproducible for anyone else.
  3. **Zero failures is the gate** — counts may differ; weakest, since a silently skipped test would pass the gate.
- **Question:** Which run is the parity baseline, and what does "identical" mean?
- **Answer:** **PENDING**
- **Date:** -
- **Status:** PENDING
- **Incorporated:** no

## Q-25 — If exactly one test behaves differently under 3.15, what is the default action?

- **Step:** P.2 (Phase P)
- **Why needed:** the change's premise is "no behavior delta", but an interpreter upgrade is exactly where a single test diverges; without a pre-agreed action the agent either stalls the change or quietly weakens a test (a prohibited move).
- **Context:** AGENTS.md prohibits weakening/deleting a test to reach GREEN; the Escalation Rules make a behavior change an **ISSUE**; the fast-path exception allows a ≤ 2-line fix only with an existing failing test; the TODO lists this as the escalation trigger.
- **Options:**
  1. (Recommended) **Stop and reclassify to ISSUE** (Q-26) — an interpreter-driven difference is a defect against the approved spec, and the ISSUE type's RED/GREEN discipline fits it.
  2. **Fix inside this change** if the cause is config-only (e.g. a pin), and reclassify only if `src/` must change.
  3. **Quarantine** with `xfail(strict=False)` marked BROKEN + a Problem Log entry + a follow-up TODO — keeps the upgrade shippable, at the cost of a known gap.
- **Question:** What is the pre-agreed handling of a single 3.15-only test divergence?
- **Answer:** **PENDING**
- **Date:** -
- **Status:** PENDING
- **Incorporated:** no

## Q-26 — When the change escalates, does it reclassify in place or open a new change?

- **Step:** P.2 (Phase P)
- **Why needed:** the TODO names two escalation targets (REFACTOR for `prefixmatch`, ISSUE for a defect), and AGENTS.md's reclassification procedure (rename the branch, re-run that type's P.4, record it) is one option; the other is to keep this change config-only and split. The orchestrator needs the rule before Phase 4.
- **Context:** AGENTS.md "Escalation Rules (Type Conversion)": keep the same worktree, `git branch -m`, re-run the new type's Phase P from P.1, record in `docs/verification/<name>.md`; the todo set must be re-derived.
- **Options:**
  1. (Recommended) **In place** per the Escalation Rules — same worktree/branch renamed, todo set re-derived, reclassification recorded in the verification record.
  2. **Split:** this change stays DOCS/CHORE (pins only) and the escalation becomes a new change with its own TODO; the upgrade PR waits on it.
  3. **Decide per case:** REFACTOR in place (no behavior risk), ISSUE as a separate change (a defect deserves its own triage).
- **Question:** What is the escalation mechanic for this change?
- **Answer:** **PENDING**
- **Date:** -
- **Status:** PENDING
- **Incorporated:** no

## Q-27 — Which version statements in text are updated by this change?

- **Step:** P.2 (Phase P)
- **Why needed:** the TODO says "docs touch-ups where the version is stated", but the real set is two places (one a CI-backed badge) and `userdocs/` has none — and one of them (`AGENTS.md`) is also being edited by `structure-map`.
- **Context:** `README.md:6` badge `Python >=3.14` (links to `pyproject.toml`), `AGENTS.md:733` "Python 3.14+", `userdocs/` has **no** Python version, `docs/specs/` has none (except Q-28); `security-changelog-license` would add badges to the same README row.
- **Options:**
  1. (Recommended) **Both, in the same PR as the pins** — the badge and the AGENTS line must never disagree with `requires-python`.
  2. **Only what the pin change actually invalidates** — e.g. if the floor stays `>=3.14`, touch nothing.
  3. **Docs in a follow-up PR** — risks the badge lying for a while.
- **Question:** Which text files does this change update?
- **Answer:** **PENDING**
- **Date:** -
- **Status:** PENDING
- **Incorporated:** no

## Q-28 — Is the Python version inside `docs/specs/structlog-logging.md` NFR-001 touched?

- **Step:** P.2 (Phase P)
- **Why needed:** it is the only spec text that names an interpreter, it is inside an **approved spec** (so editing it requires the Spec Amendment Workflow, not a chore PR), and leaving it is a defensible choice that must be recorded rather than assumed.
- **Context:** `docs/specs/structlog-logging.md:189` records the NFR-001 measurement environment as "Windows 11 / Python 3.14.5 / 32 CPU"; AGENTS.md forbids direct edits to `docs/specs/` on `main` and requires a Spec Amendment PR with a Changelog entry.
- **Options:**
  1. (Recommended) **Leave it** — it is a dated measurement record of how the budget was derived, not a version requirement; note the decision in the verification record.
  2. **Spec Amendment PR** to re-measure NFR-001 on 3.15 and update the environment note — correct but a second approval cycle for a historical note.
  3. **Add a note in this change's verification record** pointing at the 3.14.5 measurement, without touching the spec.
- **Question:** Does the change touch the interpreter reference inside the structlog spec?
- **Answer:** **PENDING**
- **Date:** -
- **Status:** PENDING
- **Incorporated:** no

## Q-29 — Is there a version bump?

- **Step:** P.2 (Phase P)
- **Why needed:** the bump rule is per change type, and this change has three possible types (DOCS/CHORE now, REFACTOR or ISSUE after escalation) with different bumps — and a CI-visible change to a *template* arguably affects downstream users of it.
- **Context:** AGENTS.md Versioning: ISSUE → `patch`, FEATURE → `minor`, CROSS-CUTTING → `minor`/`major`, **REFACTOR / DOCS-CHORE → none**; current version `0.6.1` (`pyproject.toml:4`, mirrored in `[tool.bumpversion]`).
- **Options:**
  1. (Recommended) **No bump** — DOCS/CHORE (and REFACTOR) get none; a bump happens only if the change ends as ISSUE.
  2. **`patch` bump** — the CI/interpreter contract is part of what the template ships, so users see a change.
  3. **Decide at S6.4 from the final type** — defers the rule rather than stating it.
- **Question:** Does this change bump the project version?
- **Answer:** **PENDING**
- **Date:** -
- **Status:** PENDING
- **Incorporated:** no

## Q-30 — How is "all 12 literals move in one step" enforced?

- **Step:** P.2 (Phase P)
- **Why needed:** the TODO states the risk ("half-migrated CI is worse than none") but not the mechanism; a 12-file-line sweep is exactly the kind of change where one job is missed, and the review phase needs something to check against.
- **Context:** 12 literals across 3 files (inventory above); no matrix today; `scripts/` already hosts CI helper checks (`scripts/check_traceability.py`, `scripts/validate_task_dag.py`) that CI runs, so a guard is cheap.
- **Options:**
  1. (Recommended) **Make it structurally impossible** — Q-4/Q-5's consolidation means there is one value per file, so half-migration cannot happen; the review check becomes "no `python-version: '3.1x'` literal remains".
  2. **A grep in the verification record** — the scope record lists all 12 line numbers and the reviewer ticks them off.
  3. **A CI guard script** that fails when the workflow files disagree on the interpreter version — permanent protection, one more script and job step.
- **Question:** What enforces the all-at-once sweep?
- **Answer:** **PENDING**
- **Date:** -
- **Status:** PENDING
- **Incorporated:** no

## Q-31 — Does this change declare `Depends on:` any in-flight change?

- **Step:** P.2 (Phase P)
- **Why needed:** three prepared changes will edit the same job blocks and files, and the TODO's stated collision (`pyproject-tooling-gaps`) is already merged — so its `Depends on:` line is wrong and must be replaced with the real sequencing decision.
- **Context:** `structure-map` (QUESTIONS-ANSWERED → P.4 next) edits `quality.yml`'s `type-check` job, `.pre-commit-config.yaml` and `AGENTS.md`; `codecov-coverage-badge` (PREPARING) edits the `coverage` job block and the README badge row; `docs-path-ci-trigger` (PREPARING) edits `on.paths`; `ruff-d-docstrings` (PREPARING) edits `[tool.ruff.lint]`; `tenacity-rich-cachetools` (PREPARING) churns `pyproject.toml` + `uv.lock`.
- **Options:**
  1. (Recommended) **No dependency; rebase at merge time** — the version lines are one-liners that rebase trivially, and the trigger wait makes this change the last to merge anyway.
  2. **Depend on `structure-map`** — it edits the same `type-check` job block and will merge first, so this change rebases on a settled file.
  3. **Sequence the consolidation (Q-4) *before* `structure-map`** — then `structure-map` and every later workflow change inherits the single-value pattern.
- **Question:** What is the merge-order rule for this change against those five?
- **Answer:** **PENDING**
- **Date:** -
- **Status:** PENDING
- **Incorporated:** no

## Q-32 — Is the free-threaded build (`3.15t`) in scope?

- **Step:** P.2 (Phase P)
- **Why needed:** the TODO defers it with "decide at P.2/P.3", so this is the decision; it is a separate CI axis with its own wheel-availability question, and the repo makes thread-safety claims (event-bus worker, module singletons, "idempotent and thread-safe" logging setup) that a `3.15t` job would actually test.
- **Context:** T2 — `cpython-3.15.0b1+freethreaded` is downloadable; `python-3.15` Q-5 (same question) was closed as moot by the defer decision; free-threaded wheels for `pydantic-core`/`argon2-cffi-bindings`/`greenlet`/`pyyaml` are unmeasured (T8 covers the GIL builds only).
- **Options:**
  1. (Recommended) **Out of scope, own backlog item** with its own trigger (free-threaded wheels for the compiled deps) — keeps this change's signal interpretable.
  2. **Measure locally at P.4 and record only** — a `uv venv --python 3.15t` probe plus the suite, no CI job.
  3. **Add a `3.15t` job with `continue-on-error: true`** — early signal, but a red-but-ignored job is the ambiguity the defer decision was meant to avoid.
- **Question:** Does the free-threaded build get tested, measured, or deferred?
- **Answer:** **PENDING**
- **Date:** -
- **Status:** PENDING
- **Incorporated:** no

## Q-33 — Is the JIT (`PYTHON_JIT=1`) in scope?

- **Step:** P.2 (Phase P)
- **Why needed:** the TODO says "measure first, decide later" and this is the decision point; the JIT is off by default, so "running on 3.15" does not exercise it, and the repo's spec-defined perf budgets (Q-23) are the only place it could show up.
- **Context:** the skill: "The experimental JIT is faster but off by default (`PYTHON_JIT=1`). Measure before enabling it."; perf budgets exist in `docs/specs/settings.md` NFR-001 and `docs/specs/structlog-logging.md` NFR-001.
- **Options:**
  1. (Recommended) **Out of scope** — the JIT is off by default and enabling it is a deployment decision, not an upgrade step; record it as out of scope.
  2. **One local measurement recorded** (`PYTHON_JIT=1 uv run pytest tests/contract -q`) as evidence in the verification record, no CI change.
  3. **A CI job with `PYTHON_JIT=1`** — continuous signal on the budgets, more CI minutes and a new failure mode.
- **Question:** Does the change do anything about the JIT?
- **Answer:** **PENDING**
- **Date:** -
- **Status:** PENDING
- **Incorporated:** no

## Q-34 — Must the P.4 scope record re-measure the trigger before any pin is written?

- **Step:** P.2 (Phase P)
- **Why needed:** every fact in this batch is date-stamped and perishable (the 2026-10-03 numbers were still true today, but the pin inventory was not); the scope record needs a rule for how fresh its evidence must be, or a later P.4 will reuse stale numbers.
- **Context:** the TODO's In scope already lists the two re-measurement commands; `python-3.15`'s measurements were 2 days old when this step re-ran them and one blocker (`pyyaml`) had gone unnoticed; the trigger may fire months after this batch is answered.
- **Options:**
  1. (Recommended) **Yes — P.4 opens with a fresh dated run of both commands plus the pin re-count**, and the scope record is invalid if they are older than the PR it feeds.
  2. **Reuse this batch if P.4 runs within 30 days**, re-measure otherwise.
  3. **No rule** — the agent decides at P.4.
- **Question:** What freshness rule applies to the trigger evidence at P.4?
- **Answer:** **PENDING**
- **Date:** -
- **Status:** PENDING
- **Incorporated:** no

## Late questions (Phases 2–6)

<questions discovered after the change entered the workflow; same entry format, Step field set to the step that found it>
