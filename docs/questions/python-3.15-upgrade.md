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

**P.2 Interrogate — 2026-10-05; completion pass 2026-10-11.** **35 questions** (Q-1 … Q-34 recorded 2026-10-05; **Q-35 added 2026-10-11** as the required non-goals / scope-boundary question), one decision each, most blocking first. The trigger is re-measured on both dates (below) and **has not fired on either**, so Q-1…Q-3 decide startability and the trigger's own definition, Q-4…Q-6 are the **trigger-independent** scope (pin consolidation is doable today), and the rest are the decisions the upgrade forces once it is startable. Questions that cannot be answered before the trigger fires say so in `Why needed:`. Every entry carries a `- **Recommended:**` answer (added by the 2026-10-11 completion pass from that entry's own `Options:`), and the batch ends with a `### Category coverage` table.

### Trigger measurement — 2026-10-05: **NOT FIRED** (re-run 2026-10-11: still **NOT FIRED**, but one of the two blockers has cleared)

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

**Re-run 2026-10-11 (P.2 completion pass) — still NOT FIRED, and the blocker set has moved:**

| # | Command | Result (2026-10-11) |
|---|---|---|
| T1′ | `uv python list 3.15` | `cpython-3.15.0b1-windows-x86_64-none` — **still beta**, still installed |
| T2′ | `uv python list --all-versions \| rg 3\.15` | `3.15.0b1` and `3.15.0b1+freethreaded` only — **no final 3.15.0, no RC** |
| T3′ | `uv python list --only-installed` | `cpython-3.15.0b1`, `cpython-3.14.5` (uv-managed), `cpython-3.12.3` (miniconda) |
| T4′ | `uv run python -V` | **`Python 3.14.5`** — the project venv is unchanged |
| T5′ | `uv venv $TEMP/py315-probe-2 --python 3.15` (temp venv **outside** the repo) | `Using CPython 3.15.0b1` → probe interpreter `Python 3.15.0b1` |
| T6′ | `uv pip install --python <probe> --dry-run --no-build -r pyproject.toml` | **RESOLVES wheel-only**: `pydantic==2.14.0`, `pydantic-core==2.50.0`, `sqlalchemy==2.1.4`, `pillow==12.3.0`, `orjson==3.13.0`, `structlog==26.1.0`, … — **the `pydantic` blocker of T6 has cleared**. Caveat: that is a **fresh** resolve; the committed `uv.lock` still pins `pydantic 2.13.5` (`uv.lock:1485`) → `pydantic-core 2.46.5` (`uv.lock:1501`), the wheel-less pair, and `pyyaml 6.0.3` (`uv.lock:1738`) — so CI on a 3.15 interpreter would still fail on the lock as committed until it is regenerated |
| T7′ | `uv pip install --python <probe> --dry-run --no-build --group dev` | still `× No solution found … complexipy==8.0.1 has no usable wheels` — unchanged (sdist-only, pure Python) |
| T8′ | `uv pip install --python <probe> --dry-run --no-build pyyaml bandit pre-commit` | `× … Because all versions of pyyaml have no usable wheels …` + hint `Pre-releases are available for pyyaml (e.g., 6.0.2rc1)` — **`pyyaml` is still the second blocker** |

**Verdict 2026-10-11: NOT FIRED.** 3.15 is still pre-release (T1′/T2′) and the dev group still does not resolve wheel-only (T7′/T8′). What changed since 2026-10-05 is the **reason**: `pydantic` is no longer a blocker, so the TODO's trigger wording ("3.15 final **and** a final `pydantic` with a cp315 wheel") is now satisfied on its dependency half and would fire on the interpreter half alone — straight into red `security`/`pre-commit` jobs, because `pyyaml` still ships no cp315 wheel. Q-2's concern is now measured, not predicted.

### Re-measured pin inventory (the TODO's numbers are stale) — re-measured 2026-10-11

| Where | Today (2026-10-11) | TODO says |
|---|---|---|
| `pyproject.toml:9` | `requires-python = ">=3.14"` | `:7` (shifted) |
| `pyproject.toml:4` + `:87` | `version = "1.2.0"` and `[tool.bumpversion] current_version = "1.2.0"` — **not** the `0.6.1` this batch quoted | — |
| `pyproject.toml:139` | mypy `python_version = "3.14"` | `:132` |
| `pyproject.toml:152` + comment `:150-151` | ty `python-version = "3.14"` | `:143` |
| `pyproject.toml:169` | **ruff `target-version = "py314"` — still missing from the TODO inventory** (the 2026-10-03 grep searched for `3.14`, and `py314` does not match it) | not listed |
| `pyproject.toml:64` | dev-group pin `"ruff>=0.16.10"` | — |
| `.github/workflows/quality.yml:19,39,56,77,92,107,122,140` | **8** `python-version: '3.14'` literals — every one shifted **+2** since 2026-10-05 by the `uv run mypy scripts/` step (`:25`) added by `structure-map` | 7 (`:19,37,54,75,90,105,120`) |
| `.github/workflows/lint.yml:33` | 1 | 1 |
| `.github/workflows/spec-validation.yml:35,64,78` | 3 | 3 |
| **CI total** | **12 literals, 12 jobs, no `strategy.matrix` anywhere** | "11" |
| `uv sync` steps | `quality.yml:21,41,58,79,94,109,124,142`, `lint.yml:35`, `spec-validation.yml:37,66,80` — **none** passes `--locked`/`--frozen` (Q-13) | — |
| `uv.lock:3` | `requires-python = ">=3.14"`; the lock's `resolution-markers` (`uv.lock:4-7`) already carry `python_full_version >= '3.15'` | same |
| `.pre-commit-config.yaml:11` | ruff-pre-commit `rev: v0.16.10` — **equal to the project's own `ruff>=0.16.10` (`pyproject.toml:64`): the drift this batch recorded (`v0.15.12` vs `ruff>=0.16.9`) is gone** | not listed |
| `.pre-commit-config.yaml:24-46` | three **local** hooks now exist (`deptry`, `structure-map-check`, `mkdocs-build`) — added since the batch by `structure-map` and `settings-public-registry-setter` | not listed |
| `README.md:6` | `[![Python >=3.14](…python-%3E%3D3.14-blue)…](pyproject.toml)` | "docs touch-ups" |
| `AGENTS.md:743` | `- **Language & Runtime:** Python 3.14+` | `:733` |
| `docs/specs/structlog-logging.md:190` | NFR-001 budget measured on "Windows 11 / **Python 3.14.5** / 32 CPU" | `:189` |
| `docs/specs/structure-map.md:191` | **new since the batch:** REQ-007 ties the map's supported grammar to "CPython 3.14, matching `[tool.mypy] python_version = \"3.14\"`" — an **approved spec** now names a pin this change edits | not listed |
| `docs/specs/structure-map.md:462` (EDGE-003), `:636` | EDGE-003 names "after a future `python-3.15` upgrade" as the case where newer syntax becomes an exit-4 hard failure; §14 Sequencing already carries a `python-3.15` / `python-3.15-upgrade` row | not listed |
| `userdocs/` | **no** Python version anywhere (`grep -rniE "python 3\.[0-9]{2}|3\.14|3\.15" userdocs/` → no output) | assumed a touch-up |
| `.python-version` | **does not exist** | "optionally" |

### 3.15 behavior-change checklist — measured 2026-10-05, **re-measured 2026-10-11** (both interpreters run again today)

| Item | 3.15.0b1 | 3.14.5 | Repo exposure |
|---|---|---|---|
| `re.prefixmatch` / `re.Pattern.prefixmatch` | both **present** | both absent | 5 module-level `re.match` sites (`src/backend/search/service.py:93,97`, `src/backend/filemanagement/service.py:382,386`, `src/backend/filemanagement/storage.py:108`) **+ 5 compiled-pattern `.match()` sites the TODO misses** (`src/backend/permissions/catalog.py:47`, `src/backend/permissions/service.py:228,379`, `src/backend/settings/models.py:257,375`) = **10** (the TODO lists 5, this batch counted 8) |
| `re.match` DeprecationWarning | **none** (soft-deprecation emits no warning) | none | the prescribed `-W error::DeprecationWarning` check does **not** force the rename |
| `sqlite3.connect()` keyword-only | `TypeError: connect() takes at most 1 positional arguments (2 given)` | DeprecationWarning | **closed**: 0 uses in `src/`; the 2 test uses pass the path only (`tests/acceptance/usermanagement/test_multi_role.py:150`, `tests/integration/permissions/test_persistence.py:161`); SQLAlchemy 2.0.52's pysqlite dialect builds `create_connect_args` → `(cargs, cparams)` and passes `timeout`/`check_same_thread`/`uri` as **keywords** (`.venv/Lib/site-packages/sqlalchemy/dialects/sqlite/pysqlite.py:642-675`) |
| `datetime.strptime` day-without-year | `ValueError: Day of month directive '%d' may not be used without a year directive` | ValueError with the old wording + DeprecationWarning | **closed**: 0 `strptime` uses in `src/`, `tests/`, `scripts/`, `migrations/` |
| `argparse` dest change (`add_argument("-f", "-foo")` now stores under `foo`) | — | — | **closed, but not for the reason recorded on 2026-10-05**: `argparse` **is** used — `scripts/make_map.py:110-139` (5 options, added by `structure-map`) — but **every option declares a single flag form**, so the dest rule has no site; the CLI contract is asserted in `tests/acceptance/test_structure_map.py:138,483` |
| `sre_compile`/`sre_constants`/`sre_parse` | `ModuleNotFoundError` | DeprecationWarning | **closed**: 0 uses |
| `http.server` CGI handler | absent | **present** (`hasattr(http.server, "CGIHTTPRequestHandler")` → `True`) — the 2026-10-05 row had this backwards | **closed / moot**: 0 uses anywhere |
| `platform.java_ver()` | absent | present | **closed**: 0 uses |
| keyword-argument `NamedTuple("P", x=int)` | `TypeError` | DeprecationWarning | **closed**: 0 uses |
| `typing.ByteString` | importable, `DeprecationWarning` (removal 3.17) | silent | **closed**: 0 uses — but a **third-party** import of it would break the `-W error::DeprecationWarning` check (unmeasurable until the deps install on 3.15) |
| PEP 686 default encoding | `sys.getdefaultencoding() == 'utf-8'` | **already `utf-8` on 3.14.5** | 101 explicit `encoding="utf-8"` sites (6 `src/`, 11 `scripts/`, 84 `tests/`) + two `reconfigure(encoding="utf-8")` calls (`scripts/verify_spec.py:75`, `scripts/make_map.py:532`) |
| `@contextmanager` generator timing | probed 2 shapes (normal exit + exception-with-retry): **identical order** on both | identical | **0 uses in `src/`/`scripts/`/`migrations/`; 13 in `tests/`** (decorator-anchored scan, 2026-10-11) — `tests/eventbus_test_helpers.py:50`, `tests/logging_coverage_test_helpers.py:244,263,314`, `tests/logging_test_helpers.py:185`, `tests/settings_test_helpers.py:140`, `tests/singleton_install_test_helpers.py:472,565`, `tests/tooling_test_helpers.py:43,56`, `tests/acceptance/logging_coverage/test_sink_failure.py:36`, `tests/acceptance/permissions/test_singleton_install.py:41`, `tests/acceptance/search/test_singleton_install.py:50` — `python-3.15` F10 grepped only `src/` and reported 0; the batch's 6 line numbers were a bare `contextmanager` grep and do not all land on decorators |
| `frozendict` / `sentinel` builtins | present | absent | not used (out of scope per the TODO) |

**Tool support measured 2026-10-11:** `uv run mypy --python-version 3.15 -c "x: int = 1"` → `Success` (**mypy 2.4.0**); `uv run ty check --python-version 3.15 <file>` → `All checks passed!` (**ty 0.0.84**); `uv run ruff check --no-cache --target-version py315 <file>` → `warning: Support for Python 3.15 is under development and may be unstable. Enable preview to remove this warning.` + `All checks passed!` (**ruff 0.16.10** — the warning is still there, so Q-16's answer is unchanged).

**Suite baseline — the parity gate's number.** 2026-10-05: `uv run pytest tests/ -q` on 3.14.5 → `728 passed, 1 skipped in 193.54s`. **Re-measured 2026-10-11: `2 failed, 888 passed, 1 skipped in 358.38s`** — the suite is **not green on this host today**, and neither failure is interpreter-driven: `tests/acceptance/test_structure_map.py::test_ac_021_committed_map_matches_fresh_render` (the CRLF artifact `docs/verification/complexipy-scripts.md` — on `chore/complexipy-scripts`, not yet on `main` — already records — the committed map is LF, a fresh render on this host is CRLF) and `tests/property/usermanagement/test_usermanagement_properties.py::test_inv_002_password_round_trip`, which **passes in isolation** (`1 passed in 3.93s`), i.e. it is order-dependent under `pytest-randomly`. The one skip is host-dependent (`tests/acceptance/filemanagement/test_filemanagement.py:364` `pytest.skip("symlinks not available on this host")`). This is Q-24's evidence: a local run cannot be the parity gate.

### Overlap check (all 11 live TODO files read 2026-10-11 plus the 20 archived ones; `docs/specs/` grepped)

The live set has turned over completely since 2026-10-05 — **every change this batch listed as a live collision is now closed**, and the collisions that remain are different files.

- **Closed since the batch:** `pyproject-tooling-gaps` **MERGED** (PR #68, `a278bd2`) — it is *why* the inventory is stale (added the `complexity` job, hence **12** literals not 11); `structure-map` **MERGED**; `ruff-d-docstrings` **MERGED**; `security-changelog-license` **MERGED**; `value-triage-gate` **MERGED**; `codecov-coverage-badge` **DROPPED**; `docs-path-ci-trigger` **DROPPED**; `track-python-skill` **MERGED** — it delivered `.agents/skills/python-best-practices/references/python-3.15.md`, the file whose version gate and check command this change executes.
- **`structure-map` — MERGED, and it created the one binding collision.** Its Q-28a answer landed `uv run mypy scripts/` in the `type-check` job (`quality.yml:25`), which **shifted all eight `quality.yml` literals by two lines**, and its spec `docs/specs/structure-map.md:191` (REQ-007) now states "Today that is CPython 3.14, matching `[tool.mypy] python_version = \"3.14\"`" — so an **approved spec names a pin this change edits**, and `EDGE-003` (`:462`) plus the §14 Sequencing row (`:636`) already anticipate this change. The map itself (`STRUCTURE.md`) and the `structure-map-check` pre-commit hook (`.pre-commit-config.yaml:33-39`) must be regenerated with any `.py` change. Q-27/Q-31 carry the decision.
- **`tenacity-rich-cachetools` — PREPARING (FEATURE, 34 questions PENDING).** Would add `tenacity`/`rich`/`cachetools` to `pyproject.toml` + `uv.lock` — the same region as `requires-python` (`:9`) and the dev group, and it **adds packages the 3.15 trigger must resolve** (Q-2) and a `tests/` helper this change's parity gate runs (Q-12, Q-31).
- **`complexipy-scripts` — WAITING (DOCS/CHORE, spec PR #69 open).** Edits `pyproject.toml:100` (`[tool.complexipy] paths`, section at `:99-101`) and `quality.yml:146` (the `complexipy` run line in the `complexity` job) — the same file and the same job that carries the `python-version` literal at `quality.yml:140`; it also records the `test_ac_021` CRLF failure that pollutes the local parity baseline (Q-24).
- **`docstrings-tests` — PREPARING (DOCS/CHORE).** Would edit `[tool.ruff.lint.per-file-ignores]` (`pyproject.toml:235-238`, where `"tests/*" = ["D"]` is already annotated `→ sibling change docstrings-tests`) — the same `[tool.ruff]` table as `target-version` (`:169`) — and `src/`/`tests/` docstrings, i.e. it regenerates `STRUCTURE.md` (Q-31).
- **`public-api-import-boundary` — PREPARING (CROSS-CUTTING).** Would add ruff `TID251` banned-API config (same `[tool.ruff.lint]` area) and rewrite imports across `src/`/`tests/` — that moves every `re.match` line number in Q-19/Q-20 (Q-31).
- **`gitattributes-line-endings` — PREPARING (DOCS/CHORE).** Would add `.gitattributes` and fix the CRLF-sensitive map test — the exact failure that breaks this change's local parity baseline (Q-24); doing it first makes the parity gate measurable locally.
- **`api-keys`, `backend-api`, `composition-root-factory`, `notifications`, `startup-settings-registration-gaps` — PREPARING.** New features/deps → `pyproject.toml` dependency churn (Q-2's package set, Q-12's lockfile) and new `src/` code that must parse on both interpreters (Q-30).
- **`docs/specs/`:** no spec pins a Python version as a requirement, but `docs/specs/structure-map.md:191` now **names** the mypy pin (new since the batch) and `docs/specs/structlog-logging.md:190` records the 3.14.5 measurement environment (Q-28).

### Closed from evidence (not asked)

- **`sqlite3.connect()` keyword-only, `strptime`, `argparse`, `sre_*`, `http.server` CGI, `platform.java_ver()`, keyword-arg `NamedTuple`, `typing.ByteString`:** **zero applicable sites** in `src/`, `tests/`, `scripts/`, `migrations/` (table above, re-measured 2026-10-11). No scope item, no question. `argparse` **is** now used (`scripts/make_map.py:110-139`) but every option has a single flag form, so the dest rule still has no site.
- **PEP 758 (`except TypeError, ValueError:`) at `src/backend/shared/principal.py:92`:** re-verified by `ast.parse` on **both** 3.14.5 and 3.15.0b1 today — it parses on each, so it is not a 3.15-only exposure and needs no scope item.
- **The upgrade-check command** is settled by the skill (`uv run --isolated --python 3.15 pytest -W error::DeprecationWarning`); it belongs in the P.4 scope record, not in a question.
- **`re.prefixmatch` is a pure rename, not a semantic change:** measured `re.prefixmatch` ≡ `re.match` on 3.15.0b1, and all 5 module-level patterns are `^…$`-anchored (`src/backend/filemanagement/models.py:94-95`, `src/backend/search/models.py:35-36`), so no behavior delta is possible — the REFACTOR gate (zero test changes) is satisfiable.
- **`docs/specs/` needs no amendment for the pins themselves** (no spec requires a version) — the two exceptions are the NFR-001 measurement note (Q-28) and the grammar/pin sentence `structure-map` added after this batch was written (`docs/specs/structure-map.md:191`, asked as Q-27).

## Q-1 — Is this change startable today?

- **Step:** P.2 (Phase P)
- **Why needed:** the TODO says the item is "not startable" until the trigger fires; today's re-measurement (T1–T8) says it has **not** fired. Whether P.4 runs at all — and whether the change enters the workflow with unanswered questions — depends on this answer.
- **Context:** T1/T2 — only `3.15.0b1` exists (no final, no RC). T6 — `pydantic==2.13.5` pins `pydantic-core==2.46.5`, which has no cp315 wheel; only `pydantic 2.14.0b2` resolves. **Re-measured 2026-10-11 (T6′): `pydantic 2.14.0` + `pydantic-core 2.50.0` now resolve wheel-only — that blocker is gone; `pyyaml` (T8′) and the pre-release interpreter (T1′/T2′) are what remain.** `python-3.15` Q-1 chose (C) defer for exactly this reason. Meanwhile the pin consolidation (Q-4) is trigger-independent and doable today.
- **Options:**
  1. (Recommended) **Not startable for the 3.15 part; answer the trigger-independent questions now.** P.4 stays blocked; the scope record is drafted but the pins are not written until the trigger re-fires, and the answer batch is still worth recording because it fixes the trigger definition (Q-2/Q-3) and the scope boundary.
  2. **Split now:** keep this TODO blocked on 3.15, and open a separate `chore/ci-python-pin-consolidation` TODO (Q-4) that is startable today.
  3. **Start today against `3.15.0b1` + `pydantic 2.14.0b2`** — re-litigates `python-3.15` Q-1 and makes every future red CI build ambiguous.
- **Question:** Does this change stay blocked until the trigger fires, or does it (also) start now on the trigger-independent part?
- **Recommended:** **Option 1 — stay blocked for the 3.15 part, answer the trigger-independent questions now.** The trigger has not fired on either measurement date (T1′/T2′/T7′/T8′) and pinning CI to a beta makes every red build uninterpretable, while the answers still fix the trigger definition (Q-2/Q-3) and the scope boundary (Q-35).
- **Answer:** **PENDING**
- **Date:** 2026-10-05
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
- **Recommended:** **Option 1 — wheels for the compiled packages in both groups, pure-Python sdists like `complexipy` exempt.** CI installs the dev group, so a trigger that checks only the runtime group (and misses `pyyaml`, still wheel-less at T8′) fires straight into red `security`/`pre-commit` jobs.
- **Answer:** **PENDING**
- **Date:** 2026-10-05
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
- **Recommended:** **Option 1 — `uv python list 3.15` offers a non-pre-release `3.15.x`.** It is the one command the scope record already re-runs, so the trigger stays a single checkable line instead of two external watches — and it is still false today (T1′ offers only `3.15.0b1`).
- **Answer:** **PENDING**
- **Date:** 2026-10-05
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
- **Recommended:** **Option 2 — a separate startable-now change.** It is trigger-independent, and it turns the eventual 3.15 bump into a one-line edit instead of 12; measured today the literals have already drifted twice (TODO `:19,37,54,…` vs live `:19,39,56,…`), which is exactly the maintenance the consolidation removes.
- **Answer:** **PENDING**
- **Date:** 2026-10-05
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
- **Recommended:** **Option 1 — a workflow-level `env: PYTHON_VERSION` in each of the three files.** Three lines to edit, no job/artifact renames, no extra CI minutes; a repo variable is unreadable from fork PRs and a blanket matrix doubles the minutes, which Q-8 wants reserved for the jobs that actually prove something.
- **Answer:** **PENDING**
- **Date:** 2026-10-05
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
- **Recommended:** **Option 1 — keep `actions/setup-python` as the provider.** It is the status quo and the smallest diff; whether it supports `'3.15'` then becomes an explicit clause of the trigger (Q-2) instead of a hidden failure mode at the moment of the bump.
- **Answer:** **PENDING**
- **Date:** 2026-10-05
- **Status:** PENDING
- **Incorporated:** no

## Q-7 — What does `requires-python` become?

- **Step:** P.2 (Phase P)
- **Why needed:** it is the compatibility promise the template makes to whoever installs it, and it decides whether `uv.lock` is regenerated (Q-12) and whether 3.14 users are cut off.
- **Context:** `pyproject.toml:9` is `>=3.14`; `python-3.15` Q-4 fixed the support window at **latest two CPython versions**; `uv.lock:3` mirrors it and must be regenerated if it moves. `requires-python >=3.14` already *permits* 3.15 — the gap is CI evidence, not permission.
- **Options:**
  1. (Recommended) **Keep `>=3.14`** — matches the "latest two" window; 3.15 becomes tested, not required; the floor itself needs no lock change (the lock refresh a 3.15 job requires is a separate matter, Q-12).
  2. **Raise to `>=3.15`** — one supported version, unlocks 3.15-only features (`re.prefixmatch`, `frozendict`) unconditionally, but drops 3.14 users of the template and forces the local venv and lockfile move.
  3. **Decide at P.4 from the facts then current** (wheel availability, whether 3.16 is out) — honest, but leaves the scope record without a floor.
- **Question:** Does the floor stay `>=3.14` or move to `>=3.15` when the change runs?
- **Recommended:** **Option 1 — keep `>=3.14`.** It matches the recorded "latest two" window and makes 3.15 tested rather than required; raising the floor would additionally drag the local venv (Q-11) into a config-only PR. Note that keeping the floor does **not** remove the lock refresh a 3.15 job needs — see the corrected Q-12.
- **Answer:** **PENDING**
- **Date:** 2026-10-05
- **Status:** PENDING
- **Incorporated:** no

## Q-8 — Which CI jobs run on 3.15, and in what shape?

- **Step:** P.2 (Phase P)
- **Why needed:** "CI runs on 3.15" is the skill's gate for using 3.15 features, but the repo has no matrix, so the shape decides the CI-minute cost and what "CI runs on 3.15" actually proves.
- **Context:** 12 jobs, no matrix; only two execute the test suite (`quality.yml:56` `coverage`, `spec-validation.yml:78` `tests`); the rest are lint/type/security/docs/migrations/complexity gates whose interpreter matters less. `python-3.15` Q-3 (same question there) was closed as moot by the defer decision, so it is genuinely open here.
- **Options:**
  1. (Recommended) **Matrix the two suite-executing jobs on `[3.14, 3.15]`**, leave the other ten on the single supported floor version — the suite is what proves interpreter compatibility, at ~2× the cost of two jobs.
  2. **Matrix all 12 jobs** — strongest signal (mypy/ty/ruff behavior on 3.15 is covered too), roughly doubles total CI minutes.
  3. **One dedicated 3.15 job** alongside the 3.14 jobs — cheapest, but a new job to keep in sync with the other gates.
  4. **Switch every job to 3.15 only** — no dual coverage at all; contradicts the "latest two" window unless Q-7 raises the floor.
- **Question:** Which jobs run 3.15, and as a matrix or as separate jobs?
- **Recommended:** **Option 1 — matrix only the two suite-executing jobs (`quality.yml:56` `coverage`, `spec-validation.yml:78` `tests`) on `[3.14, 3.15]`.** The suite is what proves interpreter compatibility; matrixing all 12 jobs doubles CI minutes for gates whose interpreter barely matters, and a third dedicated job is one more block to keep in sync.
- **Answer:** **PENDING**
- **Date:** 2026-10-05
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
- **Recommended:** **Option 1 — slide the window: 3.14 leaves when 3.16 goes final.** It keeps the matrix at exactly two versions, which is what the recorded "latest two" promise says and what caps the CI cost the TODO worries about; option 2 would leave the `>=3.14` floor untested.
- **Answer:** **PENDING**
- **Date:** 2026-10-05
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
- **Recommended:** **Option 1 — do not add one.** `requires-python` plus the CI pins already state the interpreter twice, and measured today there is no `.python-version` file at all, so adding one creates a third place to drift with no new guarantee.
- **Answer:** **PENDING**
- **Date:** 2026-10-05
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
- **Recommended:** **Option 1 — out of scope for the PR; each developer's `uv sync` follows `requires-python`.** The venv is per-worktree and gitignored, so a PR cannot deliver machine state; under the recommended floor (Q-7 option 1) `uv sync` does not even rebuild it.
- **Answer:** **PENDING**
- **Date:** 2026-10-05
- **Status:** PENDING
- **Incorporated:** no

## Q-12 — Is `uv.lock` regenerated as part of this change?

- **Step:** P.2 (Phase P)
- **Why needed:** the TODO counts "one lockfile regeneration" as part of the cost, and the batch assumed that under the recommended floor (Q-7 option 1) nothing in the lock changes. Re-measured 2026-10-11 that assumption is **false**: the committed lock pins the wheel-less pair, so a 3.15 job cannot install from it as committed.
- **Context:** `uv.lock:3` `requires-python = ">=3.14"`, and the lock **already contains** `python_full_version >= '3.15'` resolution markers (`uv.lock:4-7`), so 3.15 resolution is partly recorded today. But the lock pins `pydantic 2.13.5` (`uv.lock:1485`) → `pydantic-core 2.46.5` (`uv.lock:1501`) and `pyyaml 6.0.3` (`uv.lock:1738`) — and `pydantic-core 2.46.5` has **no cp315 wheel** (T6). Every CI job installs with `uv sync --only-group dev` and no `--no-build` (Q-13), so a 3.15 job on the lock as committed would have to **compile** `pydantic-core` (and `pyyaml`) from source. A fresh resolve picks `pydantic 2.14.0` / `pydantic-core 2.50.0` wheel-only (T6′), so the lock has to move for the 3.15 jobs to install at all, floor change or not.
- **Options:**
  1. **Only if `requires-python` changes** — the batch's answer; measured 2026-10-11 it is wrong, because the committed lock's `pydantic-core 2.46.5` has no cp315 wheel.
  2. (Recommended) **Regenerate as part of this change**, minimally (`uv lock`, no `--upgrade` sweep), so the lock records a wheel-only 3.15 resolution — a 3.15 CI job cannot install from the lock as committed.
  3. **Regenerate in a separate dependency-update change** (the existing `dependency-updates` verification record shows that pattern) and make this change `Depends on:` it — keeps this PR pin-only, at the cost of a declared dependency (Q-31 recommends no dependencies).
- **Question:** Does this change regenerate `uv.lock`?
- **Recommended:** **Option 2 — regenerate it here, minimally.** The committed lock pins `pydantic-core 2.46.5` (`uv.lock:1501`), which has no cp315 wheel, so a 3.15 job would otherwise compile it from source; `uv lock` without `--upgrade` keeps the churn to what 3.15 resolution forces, and it can only run once the trigger's wheel conditions hold (Q-2).
- **Answer:** **PENDING**
- **Date:** 2026-10-05
- **Status:** PENDING
- **Incorporated:** no

## Q-13 — Should CI verify the lockfile (`--locked`) as part of this change?

- **Step:** P.2 (Phase P)
- **Why needed:** no CI job currently checks that `uv.lock` matches `pyproject.toml`, so a version-pin change can silently leave the lock stale — exactly the failure mode this change creates if it edits `requires-python`.
- **Context:** every job runs `uv sync --only-group dev` with no `--locked`/`--frozen` (`quality.yml:21,41,58,79,94,109,124,142`, `lint.yml:35`, `spec-validation.yml:37,66,80` — re-measured 2026-10-11); `uv.lock:3` is a derived artifact nobody gates.
- **Options:**
  1. (Recommended) **Out of scope here** — open it as its own chore; this change stays pin-only.
  2. **Add `--locked` to the existing sync steps in this change** — one flag per job, catches drift forever, but widens the diff to 12 lines that are not about versions.
  3. **Add a dedicated `lock-drift` job** (`uv sync --locked` only) — clear signal, one more job.
- **Question:** Does this change add lockfile-freshness enforcement to CI?
- **Recommended:** **Option 1 — out of scope; open it as its own chore.** `--locked` is a real improvement but it is not about interpreter versions, and adding it to 12 sync steps widens this PR past its stated scope and collides with every change that touches the same job blocks (Q-31).
- **Answer:** **PENDING**
- **Date:** 2026-10-05
- **Status:** PENDING
- **Incorporated:** no

## Q-14 — Do the mypy and ty pins move to 3.15?

- **Step:** P.2 (Phase P)
- **Why needed:** the two tool pins are the only place that decides which language version the type checkers *check against*, and they can move independently of the floor — an inconsistency the `ty` comment at `pyproject.toml:150-151` explicitly documents.
- **Context:** `pyproject.toml:139` mypy `python_version = "3.14"`, `:152` ty `python-version = "3.14"` (re-measured 2026-10-11); measured again today: mypy **2.4.0** accepts `--python-version 3.15`, ty 0.0.84 accepts `--python-version 3.15`. The `ty` comment says it is pinned "explicitly for documentation" even though ty infers from `requires-python`.
- **Options:**
  1. (Recommended) **Keep both at the floor version** (3.14 while `requires-python` is `>=3.14`) — the checkers must accept everything the supported range allows; they move only if the floor moves.
  2. **Move both to 3.15** — checks against the newest interpreter, but stops flagging 3.15-only syntax as unavailable to 3.14 users.
  3. **Delete the explicit pins and let both infer from `requires-python`** — one source of truth, loses the documented intent the comment records.
- **Question:** What do the mypy and ty version pins become when 3.15 lands?
- **Recommended:** **Keep both at the floor version** (option 1 of this entry's framing): the checkers must accept everything the supported range allows, so pinning them to 3.15 would stop flagging 3.15-only syntax as unavailable to the `>=3.14` promise the template makes.
- **Answer:** **PENDING**
- **Date:** 2026-10-05
- **Status:** PENDING
- **Incorporated:** no

## Q-15 — Is ruff's `target-version = "py314"` in scope?

- **Step:** P.2 (Phase P)
- **Why needed:** it is a **fourth version pin in `pyproject.toml` that the TODO's inventory does not list**, and leaving it behind is exactly the "half-migrated" state the TODO forbids — ruff would keep rewriting code to 3.14 idioms under a 3.15 target.
- **Context:** `pyproject.toml:169` `target-version = "py314"` (re-measured 2026-10-11); the 2026-10-03 inventory grepped `3.14`, which `py314` does not match, so it was never counted; ruff infers the target from `requires-python` when the key is absent.
- **Options:**
  1. (Recommended) **In scope: it moves with the floor** (and is added to the pin inventory in the scope record).
  2. **In scope but stays `py314` while the floor is 3.14** — i.e. explicitly tied to `requires-python`, not to the CI matrix.
  3. **Out of scope** — treat ruff's target as tooling detail; risks `UP` rules never firing for 3.15 idioms.
  4. **Delete the key** and let ruff infer from `requires-python` — removes a pin, loses an explicit statement.
- **Question:** Is `target-version` part of this change's pin set, and what does it become?
- **Recommended:** **Option 1 — in scope, it moves with the floor, and it is added to the pin inventory in the scope record.** It is a real fourth pin (`pyproject.toml:169`) that the TODO never counted, and leaving it behind is the half-migrated state the TODO forbids; Q-16 still governs *when* it may say `py315`.
- **Answer:** **PENDING**
- **Date:** 2026-10-05
- **Status:** PENDING
- **Incorporated:** no

## Q-16 — How is ruff's "3.15 is under development" warning handled?

- **Step:** P.2 (Phase P)
- **Why needed:** setting `target-version = "py315"` on the installed ruff prints a warning on **every** ruff run (local, pre-commit, the lint job), and the lint job's output is the project's quality signal — a permanent warning is a decision, not an accident.
- **Context:** measured 2026-10-11: `uv run ruff check --no-cache --target-version py315 <file>` → `warning: Support for Python 3.15 is under development and may be unstable. Enable preview to remove this warning.` then `All checks passed!` (**ruff 0.16.10** — the warning is still present six days later).
- **Options:**
  1. (Recommended) **Defer the ruff target until ruff ships stable 3.15 support** — keep `py314`, record the deferral with the ruff version that clears it.
  2. **Accept the warning** — the target is set, the lint job still passes, the warning is noise in every run.
  3. **Set `preview = true` to silence it** — changes the whole rule set to preview rules, which is a much larger behavior change than a version bump.
- **Question:** What does the change do about ruff's unstable-3.15 warning?
- **Recommended:** **Option 1 — defer the ruff target until ruff ships stable 3.15 support**, keeping `py314` and recording the deferral against the ruff version that clears it. Measured today ruff 0.16.10 still prints the warning on every run, so setting `py315` would put permanent noise in the project's quality signal, and `preview = true` changes the whole rule set.
- **Answer:** **PENDING**
- **Date:** 2026-10-05
- **Status:** PENDING
- **Incorporated:** no

## Q-17 — Is the pre-commit ruff revision drift fixed in this change?

- **Step:** P.2 (Phase P)
- **Why needed:** the pre-commit hook pins an **older ruff than the project requires**, so local autofixes and the CI lint gate can disagree — and the config's own comment says the revs are to be reviewed "any time the Python or CI toolchain changes materially", which is this change.
- **Context:** **re-measured 2026-10-11: the drift this entry was written about is already closed** — `.pre-commit-config.yaml:11` is `rev: v0.16.10`, equal to the project's own `"ruff>=0.16.10"` (`pyproject.toml:64`); on 2026-10-05 it was `rev: v0.15.12` vs `"ruff>=0.16.9"` (`:62`). `structure-map` has since **merged** and did add a local hook to the same file (`.pre-commit-config.yaml:33-39`), alongside `deptry` (`:24-29`) and `mkdocs-build` (`:41-46`).
- **Options:**
  1. (Recommended) **In scope: align the hook rev with the project's ruff pin** — one line, same toolchain, removes a known inconsistency.
  2. **Out of scope: a separate chore** — keeps this PR strictly about interpreter versions.
  3. **Leave it** — accept that local ruff ≠ CI ruff.
- **Question:** Does this change bump `.pre-commit-config.yaml`'s ruff revision?
- **Recommended:** **Reframe: nothing to align today — take it as a review step, not a bump.** Measured 2026-10-11 the hook rev (`v0.16.10`) already equals the project pin (`ruff>=0.16.10`), so option 1 costs no diff; what remains is the config's own order to review the revs "any time the Python or CI toolchain changes materially", which this change is — record the check in the scope record.
- **Answer:** **PENDING**
- **Date:** 2026-10-05
- **Status:** PENDING
- **Incorporated:** no

## Q-18 — Must the tool pins be bumped before the CI literals move?

- **Step:** P.2 (Phase P)
- **Why needed:** "tool support lags the language" is listed as a risk, but today's measurement shows the installed tools already accept a 3.15 target — so the change either needs a version gate or it does not, and that decides whether dependency bumps ride along (which would end the DOCS/CHORE classification).
- **Context:** measured 2026-10-11: **mypy 2.4.0**, ty 0.0.84 and **ruff 0.16.10** all accept a 3.15 target (ruff with the Q-16 warning); the TODO's risk line assumes they may not; `python-3.15` Q-2 (is a dependency bump in scope?) was closed as moot by the defer decision, so it is open again here.
- **Options:**
  1. (Recommended) **No bump** — the installed versions already accept 3.15; the change stays config-only and DOCS/CHORE.
  2. **Require an official 3.15 support statement from each tool first** — safest, adds an external wait on top of the interpreter wait.
  3. **Bump ruff/mypy/ty to latest in the same PR** — one-shot modernization, but a dependency change inside a DOCS/CHORE scope.
- **Question:** Does the change require tool version bumps as a precondition?
- **Recommended:** **Option 1 — no bump.** Measured 2026-10-11 the installed mypy 2.4.0, ty 0.0.84 and ruff 0.16.10 all accept a 3.15 target, so dependency churn is not a precondition and the change stays config-only (the DOCS/CHORE classification holds).
- **Answer:** **PENDING**
- **Date:** 2026-10-05
- **Status:** PENDING
- **Incorporated:** no

## Q-19 — Is `re.prefixmatch` taken in this change?

- **Step:** P.2 (Phase P)
- **Why needed:** it is the escalation trigger written into the TODO: taking it makes the change **REFACTOR** (GREEN baseline, different todo set, different Phase 5 gate), and the skill's version gate only permits it once `requires-python >=3.15` **and** CI runs 3.15.
- **Context:** 5 module-level sites (`src/backend/search/service.py:93,97`, `src/backend/filemanagement/service.py:382,386`, `src/backend/filemanagement/storage.py:108`) plus 5 compiled-pattern sites (Q-20) = **10**, re-measured 2026-10-11; measured: `re.prefixmatch` ≡ `re.match` on 3.15.0b1, all patterns are `^…$`-anchored, and `re.match` emits **no** DeprecationWarning — so the `-W error::DeprecationWarning` check will **not** force the rename.
- **Options:**
  1. (Recommended) **Defer to its own REFACTOR change** once the floor/CI gate is met — keeps this change config-only and DOCS/CHORE, and gives the rename its own GREEN-baseline discipline.
  2. **Take it here** — reclassifies this change to REFACTOR (baseline, full regression, no version bump) and couples an `src/` edit to a CI change.
  3. **Never** — `re.match` is soft-deprecated and never removed, so the sites are harmless.
- **Question:** Does the 3.15 upgrade change include the `re.prefixmatch` migration, or is it a separate change?
- **Recommended:** **Option 1 — defer it to its own REFACTOR change** once the floor/CI gate is met. It is a pure rename with no forced trigger (`re.match` emits no DeprecationWarning, measured), and keeping it out of this PR is what keeps the change config-only and DOCS/CHORE while giving the rename its own GREEN-baseline discipline.
- **Answer:** **PENDING**
- **Date:** 2026-10-05
- **Status:** PENDING
- **Incorporated:** no

## Q-20 — If `prefixmatch` is taken: does it cover the compiled-pattern `.match()` sites too?

- **Step:** P.2 (Phase P)
- **Why needed:** the TODO's inventory says 5 sites; the count measured 2026-10-11 is **10**, and 5 of them use the compiled-method form, which is a different API surface. A partial rename leaves the codebase in two idioms.
- **Context:** `src/backend/permissions/catalog.py:47`, `src/backend/permissions/service.py:228,379` use `_PERMISSION_KEY_PATTERN.match(...)` / `_ROLE_NAME_PATTERN.match(...)`, and **two more compiled-method sites exist since the batch** — `src/backend/settings/models.py:257,375` (`_KEY_RE.match(...)`, `_TEMPLATE_NAME_RE.match(...)`); measured on 3.15.0b1: `re.Pattern.prefixmatch` **exists** (`hasattr(re.compile('a'), 'prefixmatch') == True`). The `re.fullmatch` sites in the same file (`src/backend/settings/models.py:72,109`) are unaffected.
- **Options:**
  1. (Recommended) **All 10 sites** — module-level and compiled-method in one sweep, so no `re.match` remains.
  2. **Only the 5 module-level sites** — matches the TODO as written, leaves 5 `.match()` calls behind.
  3. **Module-level only, and additionally switch the 5 compiled patterns to module-level calls** — uniform style, larger diff.
- **Question:** Which call sites does the rename cover?
- **Recommended:** **Option 1 — all 10 sites in one sweep** (5 module-level + 5 compiled-method, including the two `src/backend/settings/models.py` sites added since this batch was written): a partial rename leaves the codebase in two idioms, which is the same half-migrated state the TODO forbids for pins.
- **Answer:** **PENDING**
- **Date:** 2026-10-05
- **Status:** PENDING
- **Incorporated:** no

## Q-21 — Is the `@contextmanager` behavior change audited in scope?

- **Step:** P.2 (Phase P)
- **Why needed:** the checklist names it first, the earlier change reported "0 sites" because it grepped only `src/`, and the real exposure is in the **test helpers** — which are the contract the parity gate relies on. Whether the change audits them, or trusts the suite, must be recorded.
- **Context:** 0 uses in `src/`, `scripts/`, `migrations/`; **13 uses in `tests/`** (re-measured 2026-10-11 with a decorator-anchored scan: `tests/eventbus_test_helpers.py:50`, `tests/logging_coverage_test_helpers.py:244,263,314`, `tests/logging_test_helpers.py:185`, `tests/settings_test_helpers.py:140`, `tests/singleton_install_test_helpers.py:472,565`, `tests/tooling_test_helpers.py:43,56`, `tests/acceptance/logging_coverage/test_sink_failure.py:36`, `tests/acceptance/permissions/test_singleton_install.py:41`, `tests/acceptance/search/test_singleton_install.py:50`; the batch counted 6 from a bare `contextmanager` grep, so some of its line numbers are not decorators); probed two shapes (normal exit, exception + re-raise) on 3.15.0b1 vs 3.14.5 — **identical** ordering.
- **Options:**
  1. (Recommended) **No separate audit** — the full-suite parity gate (Q-24) is the check; record the 13 sites and the probe result in the scope record.
  2. **Explicit audit item** — read all 13 helpers against the 3.15 semantics and record a per-site verdict.
  3. **Restructure the helpers** to not depend on finalization order — a test-only refactor inside a config change.
- **Question:** Does the change audit the 13 test-helper `@contextmanager` uses, or rely on the suite?
- **Recommended:** **Option 1 — no separate audit; the full-suite parity gate (Q-24) is the check**, with the site list recorded in the scope record. Measured 2026-10-11 the count is **13, not 6**, and still **zero** outside `tests/`; the two probed shapes order identically on both interpreters, so the suite comparison already covers every site.
- **Answer:** **PENDING**
- **Date:** 2026-10-05
- **Status:** PENDING
- **Incorporated:** no

## Q-22 — What does the change do about explicit `encoding="utf-8"` (PEP 686)?

- **Step:** P.2 (Phase P)
- **Why needed:** the skill says keep passing it explicitly, the default is already UTF-8 on 3.14.5 (measured), and the repo has **101** explicit sites plus two `reconfigure` calls (re-counted 2026-10-11; the batch recorded 22 + 1) — so "handle PEP 686" is either a no-op or a lint change, and the scope record must say which.
- **Context:** 6 `src/` sites (`src/backend/logging/_pipeline.py:272`, `src/backend/settings/repository.py:155,170,297,314,342`), 11 in `scripts/`, 84 in `tests/`; two `reconfigure(encoding="utf-8")` calls (`scripts/verify_spec.py:75`, `scripts/make_map.py:532`); `sys.getdefaultencoding()` is already `utf-8` on 3.14.5.
- **Options:**
  1. (Recommended) **No change** — keep every explicit `encoding="utf-8"`; record PEP 686 as a no-op for this repo.
  2. **Add a lint rule** that forbids opening text without an explicit encoding — enforces the convention, but ruff has no such rule today, so it means a custom check.
  3. **Drop the now-redundant `sys.stdout.reconfigure(encoding="utf-8")`** in `scripts/verify_spec.py:75` — a one-line simplification that changes behavior on non-UTF-8 consoles.
- **Question:** Is there any encoding-related work item in this change?
- **Recommended:** **Option 1 — no change; record PEP 686 as a no-op for this repo.** The default encoding is already UTF-8 on 3.14.5 (measured again 2026-10-11), the skill says keep passing it explicitly, and 101 explicit sites are the convention rather than a defect; option 3 would change behavior on non-UTF-8 consoles.
- **Answer:** **PENDING**
- **Date:** 2026-10-05
- **Status:** PENDING
- **Incorporated:** no

## Q-23 — What happens if a performance-budget test fails under 3.15?

- **Step:** P.2 (Phase P)
- **Why needed:** the repo's spec-defined time budgets were measured on 3.14.5, and 3.15 changes interpreter performance characteristics (JIT available, Tachyon, faster startup paths). A budget failure is a spec conflict, not a code bug, and the repo has already been through exactly this once.
- **Context:** `docs/verification/perf-budget-env-aware.md` — the settings NFR-001 budget failed at 65.4 ms vs 50 ms on CI and was resolved by a **Spec Amendment** (50 ms local / 100 ms CI); budgets live in `docs/specs/settings.md:357` NFR-001 (already amended twice for environment sensitivity — v2/v3 in that file's Changelog), `docs/specs/structlog-logging.md:190` NFR-001 (`< 25 ms`, measured 0.85 ms on 3.14.5) and `tests/acceptance/eventbus/test_eventbus.py:27,55` (`_PUBLISH_BUDGET_S = 0.01`, re-cited 2026-10-11).
- **Options:**
  1. (Recommended) **Spec Amendment PR** for the affected budget (the precedent in `perf-budget-env-aware`), re-measured on 3.15 — this change then stays config-only and waits on that PR.
  2. **Reclassify this change to ISSUE** and fix the budget inside it — conflates a spec-budget change with the upgrade.
  3. **Quarantine the budget test** (`xfail` marked BROKEN + Problem Log entry) — keeps CI green but leaves an unmet NFR on record.
- **Question:** What is the pre-agreed response to a perf-budget failure under 3.15?
- **Recommended:** **Option 1 — a Spec Amendment PR for the affected budget**, re-measured on 3.15, following the `docs/verification/perf-budget-env-aware.md` precedent. A time budget is a spec fact rather than a code bug, so this change must not absorb it (option 2) and quarantining it (option 3) would leave an unmet NFR on record.
- **Answer:** **PENDING**
- **Date:** 2026-10-05
- **Status:** PENDING
- **Incorporated:** no

## Q-24 — What exactly must the parity gate compare, and where?

- **Step:** P.2 (Phase P)
- **Why needed:** "the full suite under 3.15 must match the 3.14 baseline with zero test changes" is the change's gate, but the baseline number is environment-dependent (today's host run has a host-caused skip), so the gate needs a defined environment and a defined equality.
- **Context:** the 2026-10-05 baseline `uv run pytest tests/ -q` on 3.14.5 → **728 passed, 1 skipped**; **re-measured 2026-10-11: `2 failed, 888 passed, 1 skipped in 358.38s`** — the two failures are host artifacts, not behavior (the CRLF map test `test_ac_021_committed_map_matches_fresh_render`, recorded in `docs/verification/complexipy-scripts.md` (on `chore/complexipy-scripts`, not yet on `main`), and an order-dependent `tests/property/usermanagement/test_usermanagement_properties.py::test_inv_002_password_round_trip` that passes in isolation). The skip is `tests/acceptance/filemanagement/test_filemanagement.py:364`, "symlinks not available on this host"; CI runs `ubuntu-latest` (`quality.yml:11` etc.), where it is not skipped; the suite now takes ~358 s locally.
- **Options:**
  1. (Recommended) **The CI run is the gate:** 3.14 and 3.15 matrix jobs on the same runner must produce identical pass/fail counts; the local host run is informational evidence.
  2. **Both environments must match their own 3.14 baseline** — strongest, but a Windows host baseline is not reproducible for anyone else.
  3. **Zero failures is the gate** — counts may differ; weakest, since a silently skipped test would pass the gate.
- **Question:** Which run is the parity baseline, and what does "identical" mean?
- **Recommended:** **Option 1 — the CI run is the gate** (3.14 and 3.15 matrix jobs on the same runner, identical pass/fail counts). Re-measured 2026-10-11 the local host run is not even green (`2 failed, 888 passed, 1 skipped`, both failures host/order artifacts), so a local baseline cannot carry an equality claim; option 3 would let a silently skipped test pass the gate.
- **Answer:** **PENDING**
- **Date:** 2026-10-05
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
- **Recommended:** **Option 1 — stop and reclassify to ISSUE** (mechanic in Q-26). An interpreter-driven divergence is a deviation from approved spec behavior, which is the ISSUE definition; AGENTS.md forbids weakening the test, and the fast-path exception does not cover it.
- **Answer:** **PENDING**
- **Date:** 2026-10-05
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
- **Recommended:** **Escalate in place per the AGENTS.md Escalation Rules** — keep the worktree, `git branch -m` to the new type, re-run that type's Phase P from P.1, record the reclassification in `docs/verification/python-3.15-upgrade.md`. It is the mechanic the handbook already prescribes, so it needs no new TODO and leaves no orphaned scope record.
- **Answer:** **PENDING**
- **Date:** 2026-10-05
- **Status:** PENDING
- **Incorporated:** no

## Q-27 — Which version statements in text are updated by this change?

- **Step:** P.2 (Phase P)
- **Why needed:** the TODO says "docs touch-ups where the version is stated", but the real set is two places (one a CI-backed badge) and `userdocs/` has none — and `AGENTS.md` is also edited by the `structure-map` change (now merged), which added the map-regeneration line to it.
- **Context:** `README.md:6` badge `Python >=3.14` (links to `pyproject.toml`), `AGENTS.md:743` "Python 3.14+" (re-cited 2026-10-11), `userdocs/` has **no** Python version, `docs/specs/` has none as a requirement (except Q-28 and the grammar sentence `structure-map` added at `docs/specs/structure-map.md:191`); `security-changelog-license` has since **merged**, so the README badge row is settled.
- **Options:**
  1. (Recommended) **Both, in the same PR as the pins** — the badge and the AGENTS line must never disagree with `requires-python`.
  2. **Only what the pin change actually invalidates** — e.g. if the floor stays `>=3.14`, touch nothing.
  3. **Docs in a follow-up PR** — risks the badge lying for a while.
- **Question:** Which text files does this change update?
- **Recommended:** **Option 1 — both (`README.md:6` and `AGENTS.md:743`), in the same PR as the pins.** The badge and the AGENTS line must never disagree with `requires-python`, and measured today those two are the complete set (`userdocs/` states no version), so the sweep is exactly two lines — under the recommended floor (Q-7 option 1) neither becomes false, and the check still belongs in the scope record.
- **Answer:** **PENDING**
- **Date:** 2026-10-05
- **Status:** PENDING
- **Incorporated:** no

## Q-28 — Is the Python version inside `docs/specs/structlog-logging.md` NFR-001 touched?

- **Step:** P.2 (Phase P)
- **Why needed:** it is the only spec text that names an interpreter, it is inside an **approved spec** (so editing it requires the Spec Amendment Workflow, not a chore PR), and leaving it is a defensible choice that must be recorded rather than assumed.
- **Context:** `docs/specs/structlog-logging.md:190` records the NFR-001 measurement environment as "Windows 11 / Python 3.14.5 / 32 CPU" (re-cited 2026-10-11); AGENTS.md forbids direct edits to `docs/specs/` on `main` and requires a Spec Amendment PR with a Changelog entry.
- **Options:**
  1. (Recommended) **Leave it** — it is a dated measurement record of how the budget was derived, not a version requirement; note the decision in the verification record.
  2. **Spec Amendment PR** to re-measure NFR-001 on 3.15 and update the environment note — correct but a second approval cycle for a historical note.
  3. **Add a note in this change's verification record** pointing at the 3.14.5 measurement, without touching the spec.
- **Question:** Does the change touch the interpreter reference inside the structlog spec?
- **Recommended:** **Option 1 — leave it.** It is a dated record of how the budget was measured, not a version requirement, and editing an approved spec costs a Spec Amendment cycle for no gain; option 3 (a pointer in this change's verification record) is free and is what the scope record should carry.
- **Answer:** **PENDING**
- **Date:** 2026-10-05
- **Status:** PENDING
- **Incorporated:** no

## Q-29 — Is there a version bump?

- **Step:** P.2 (Phase P)
- **Why needed:** the bump rule is per change type, and this change has three possible types (DOCS/CHORE now, REFACTOR or ISSUE after escalation) with different bumps — and a CI-visible change to a *template* arguably affects downstream users of it.
- **Context:** AGENTS.md Versioning: ISSUE → `patch`, FEATURE → `minor`, CROSS-CUTTING → `minor`/`major`, **REFACTOR / DOCS-CHORE → none**; current version **`1.2.0`** (`pyproject.toml:4`, mirrored at `[tool.bumpversion] current_version`, `pyproject.toml:87`) — the `0.6.1` this entry quoted is two releases stale.
- **Options:**
  1. (Recommended) **No bump** — DOCS/CHORE (and REFACTOR) get none; a bump happens only if the change ends as ISSUE.
  2. **`patch` bump** — the CI/interpreter contract is part of what the template ships, so users see a change.
  3. **Decide at S6.4 from the final type** — defers the rule rather than stating it.
- **Question:** Does this change bump the project version?
- **Recommended:** **Option 1 — no bump** while the change stays DOCS/CHORE (or ends as REFACTOR): AGENTS.md gives those types none. Measured today the version is `1.2.0`, so a bump would appear only if the change escalates to ISSUE (`patch` → `1.2.1`), decided by the final type at S6.4.
- **Answer:** **PENDING**
- **Date:** 2026-10-05
- **Status:** PENDING
- **Incorporated:** no

## Q-30 — How is "all 12 literals move in one step" enforced?

- **Step:** P.2 (Phase P)
- **Why needed:** the TODO states the risk ("half-migrated CI is worse than none") but not the mechanism; a 12-file-line sweep is exactly the kind of change where one job is missed, and the review phase needs something to check against.
- **Context:** 12 literals across 3 files (inventory above); no matrix today; `scripts/` already hosts CI helper checks that CI runs (`scripts/check_traceability.py`, `scripts/validate_task_dag.py`, `scripts/verify_spec.py`, and since `structure-map` merged, `scripts/make_map.py` with its `--check` mode wired into a pre-commit hook), so a guard is cheap.
- **Options:**
  1. (Recommended) **Make it structurally impossible** — Q-4/Q-5's consolidation means there is one value per file, so half-migration cannot happen; the review check becomes "no `python-version: '3.1x'` literal remains".
  2. **A grep in the verification record** — the scope record lists all 12 line numbers and the reviewer ticks them off.
  3. **A CI guard script** that fails when the workflow files disagree on the interpreter version — permanent protection, one more script and job step.
- **Question:** What enforces the all-at-once sweep?
- **Recommended:** **Option 1 — make it structurally impossible via Q-4/Q-5.** With one `PYTHON_VERSION` per file there is nothing to half-migrate, and the review check collapses to "no `python-version: '3.1x'` literal remains" — a single grep, which is what the measured line-number drift in this very file argues for.
- **Answer:** **PENDING**
- **Date:** 2026-10-05
- **Status:** PENDING
- **Incorporated:** no

## Q-31 — Does this change declare `Depends on:` any in-flight change?

- **Step:** P.2 (Phase P)
- **Why needed:** several prepared changes will edit the same job blocks and files, and the TODO's stated collision (`pyproject-tooling-gaps`) is already merged — so its `Depends on:` line is wrong and must be replaced with the real sequencing decision.
- **Context:** re-measured 2026-10-11 — of the five changes this entry named, `structure-map` and `ruff-d-docstrings` have **merged**, and `codecov-coverage-badge` and `docs-path-ci-trigger` were **DROPPED**. The live overlaps are now `tenacity-rich-cachetools` (PREPARING, would add deps to `pyproject.toml` + `uv.lock`), `complexipy-scripts` (WAITING, edits `quality.yml:146` in the job that carries the literal at `:140`, plus `pyproject.toml:100`), `docstrings-tests` and `public-api-import-boundary` (PREPARING, both edit the `[tool.ruff]` area and `src/`/`tests/`), and `gitattributes-line-endings` (PREPARING, would fix the CRLF map failure that pollutes the parity baseline, Q-24).
- **Options:**
  1. (Recommended) **No dependency; rebase at merge time** — the version lines are one-liners that rebase trivially, and the trigger wait makes this change the last to merge anyway.
  2. **Depend on `structure-map`** — spent: it merged before this batch was re-verified, so there is nothing left to wait for.
  3. **Sequence the consolidation (Q-4) *before* `structure-map`** — then `structure-map` and every later workflow change inherits the single-value pattern.
- **Question:** What is the merge-order rule for this change against the in-flight changes that touch the same files?
- **Recommended:** **Option 1 — no `Depends on:`; rebase at merge time.** Measured 2026-10-11 the two changes this entry treated as live blockers are closed (one merged, two dropped), the remaining overlaps touch different keys of the same files, and the trigger wait makes this change the last to merge anyway — so option 2's blocker no longer exists to depend on.
- **Answer:** **PENDING**
- **Date:** 2026-10-05
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
- **Recommended:** **Option 1 — out of scope, own backlog item with its own trigger** (free-threaded wheels for the compiled deps). Measured 2026-10-11 the GIL build of `pyyaml` still has no cp315 wheel (T8′), so the free-threaded wheel question is strictly harder, and a `3.15t` job would make a red build ambiguous — the exact reason the 3.15 upgrade itself was deferred.
- **Answer:** **PENDING**
- **Date:** 2026-10-05
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
- **Recommended:** **Option 1 — out of scope, recorded as a non-goal.** The JIT is off by default, so "CI runs on 3.15" does not exercise it, and enabling it is a deployment decision that would immediately put the spec perf budgets (Q-23) in play; if a signal is ever wanted, option 2's local measurement is the cheapest form of it.
- **Answer:** **PENDING**
- **Date:** 2026-10-05
- **Status:** PENDING
- **Incorporated:** no

## Q-34 — Must the P.4 scope record re-measure the trigger before any pin is written?

- **Step:** P.2 (Phase P)
- **Why needed:** every fact in this batch is date-stamped and perishable (the 2026-10-03 numbers were still true today, but the pin inventory was not); the scope record needs a rule for how fresh its evidence must be, or a later P.4 will reuse stale numbers.
- **Context:** the TODO's In scope already lists the two re-measurement commands; `python-3.15`'s measurements were 2 days old when the 2026-10-05 step re-ran them and one blocker (`pyyaml`) had gone unnoticed; **the 2026-10-11 completion pass is the rule's proof in the other direction** — six days later the `pydantic` blocker had cleared (T6′), every `quality.yml` literal had shifted by two lines, two more `re.match` sites existed, and the version had moved `0.6.1` → `1.2.0`.
- **Options:**
  1. (Recommended) **Yes — P.4 opens with a fresh dated run of both commands plus the pin re-count**, and the scope record is invalid if they are older than the PR it feeds.
  2. **Reuse this batch if P.4 runs within 30 days**, re-measure otherwise.
  3. **No rule** — the agent decides at P.4.
- **Question:** What freshness rule applies to the trigger evidence at P.4?
- **Recommended:** **Option 1 — P.4 opens with a fresh dated re-run of both trigger commands plus the pin re-count.** Measured across this file's own two passes, six days are enough to clear a blocker, shift every cited line number and add call sites, so any number carried forward is already a candidate for being wrong.
- **Answer:** **PENDING**
- **Date:** 2026-10-05
- **Status:** PENDING
- **Incorporated:** no

## Q-35 — What does this change explicitly NOT do?

- **Step:** P.2 (Phase P) — added by the 2026-10-11 completion pass; the batch had per-item deferrals but no scope-boundary question
- **Why needed:** the TODO classifies the change as DOCS/CHORE **provisionally** and names the conditions that would escalate it (REFACTOR if 3.15-only features are adopted in `src/`, ISSUE if the upgrade exposes a defect). Nothing in the record states the boundary that classification rests on, so an escalation would be drift rather than a decision, and P.4's scope record would have no non-goals list to check the diff against.
- **Context:** measured 2026-10-11: nothing in `src/` is forced by the interpreter — `src/backend/shared/principal.py:92` parses on 3.15.0b1, the behavior checklist closes with zero applicable sites, and the 3.15-only features the skill lists have either no site (`frozendict`/`sentinel`: 0 uses) or a deferred one (`re.match`: 10 sites, Q-19/Q-20). The TODO's own `Out of scope` already names 3.15-only syntax, free-threaded CI and the JIT, but no question records them as an accepted decision.
- **Options:**
  1. (Recommended) **Record a non-goals list in the P.4 scope record:** no 3.15-only syntax anywhere (`re.prefixmatch`, `frozendict`, `sentinel`, lazy imports, Tachyon), no free-threaded (`3.15t`) CI job, no JIT, no ruff/mypy/ty version bumps, no `uv.lock` regeneration beyond the minimal refresh 3.15 wheel-only resolution forces (Q-12), no `.python-version` file, no lockfile-freshness gate, no local-venv work.
  2. **Leave the boundary implicit** — let the DOCS/CHORE label carry it. Risks an agent "helpfully" modernizing syntax in the same PR and silently reclassifying the change mid-workflow.
  3. **Put the non-goals in the TODO instead** — visible in the backlog, but `docs/todo/` is a planning record that never reaches the reviewed PR, so the reviewer would not see them.
- **Question:** Which non-goals does the change record as its scope boundary, and where are they recorded?
- **Recommended:** **Option 1 — a written non-goals list in the P.4 scope record**, exactly the set in option 1 (it is the union of the recommendations in Q-10, Q-11, Q-12, Q-13, Q-18, Q-19, Q-22, Q-32 and Q-33). It is what keeps the change DOCS/CHORE and config-only, and measured today `src/` needs no edit at all to run on 3.15, so adopting any of those features would be a choice, not a consequence — and would trigger the Escalation Rules (Q-26).
- **Answer:** **PENDING**
- **Date:** 2026-10-11
- **Status:** PENDING
- **Incorporated:** no

### Category coverage

| Category | Status |
|---|---|
| Trigger & Startability | covered (Q-1, Q-2, Q-3, Q-34) |
| Scope & Goals | covered (Q-4, Q-5, Q-6, Q-7, Q-8, Q-9) |
| Non-goals / scope boundary | covered (Q-35 — the explicit list; per-item deferrals in Q-11, Q-12, Q-13, Q-19, Q-22, Q-32, Q-33) |
| Data & State (the pin/config inventory) | covered (Q-7, Q-10, Q-12, Q-14, Q-15, Q-17, Q-27) |
| Behavior & Edge Cases (3.15 semantics) | covered (Q-19, Q-20, Q-21, Q-22, Q-23) |
| Interfaces & Contracts (CI contract, the template's compatibility promise) | covered (Q-6, Q-7, Q-8, Q-9, Q-27) |
| Tooling & Constraints | covered (Q-2, Q-14, Q-15, Q-16, Q-18) |
| Testing & Acceptance (the parity gate) | covered (Q-21, Q-24, Q-25, Q-30) |
| Performance & Capacity | covered (Q-23, Q-33; CI-minute cost in Q-5 and Q-8) |
| Spec, Traceability & Governance | covered (Q-23, Q-27, Q-28, Q-29) |
| Architecture & Conventions | covered (Q-5, Q-10, Q-14, Q-32) |
| Sequencing & Backlog | covered (Q-4, Q-30, Q-31) |
| Release & Changelog | covered (Q-29) — the `CHANGELOG.md` entry itself is not a question: Phase 6 item 10 requires one for every change type, this one under `Changed` |
| Persistent storage / migration | covered (Q-8) — the `migrations` job (`quality.yml:122`) runs `alembic upgrade head` on the interpreter, so it is part of the "which jobs run 3.15" decision; no schema change and no new migration is in scope |
| Security & Privacy | skipped — the change moves no secret, no auth path and no input-handling code; the only security-adjacent fact is that the `security` job's `bandit`/`pyyaml` wheel availability gates the trigger, and that is asked as Q-2 |
| Frontend / UX | skipped — `src/frontend/` contains no files (measured 2026-10-11: `find src/frontend -type f` → 0) and the change alters no user-visible surface; the only outward-facing text is the version badge, asked as Q-27 |

## Late questions (Phases 2–6)

<questions discovered after the change entered the workflow; same entry format, Step field set to the step that found it>
