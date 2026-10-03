# Questions: python-3.15

One question file per change, created at **P.1 Frame** from this template and named `<change-name>.md`. It replaces the retired central `AI_Questions.md` (archived at `docs/questions/archive-AI_Questions.md`).

- **Change:** python-3.15 (DOCS/CHORE)
- **TODO file:** `docs/todo/python-3.15.md`
- **Spec:** n/a
- **Opened:** 2026-10-03
- **Status:** ALL ANSWERED  <!-- ALL ANSWERED | OPEN -->  <!-- 0 PENDING; Q-2, Q-3, Q-5, Q-6 closed as moot by Q-1 = (C) -->
- **Answer rounds:** 1 (2026-10-04: Q-1; Q-2/Q-3/Q-5/Q-6 closed as moot)

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

## Measured facts (P.2, 2026-10-03) — re-verified, not reused from the TODO

| # | Command | Cited output |
|---|---|---|
| F1 | `uv python list 3.15` | `cpython-3.15.0b1-windows-x86_64-none    <download available>` — **beta only**; no final 3.15.0, no RC |
| F2 | `uv python list --all-versions \| rg 3\.15` | `3.15.0b1` (installed) + `3.15.0b1+freethreaded` (`<download available>`) — those two builds only |
| F3 | `uv python list --only-installed` | `cpython-3.14.5-...-none` (uv-managed), `cpython-3.12.3` (miniconda). No 3.15 installed before this step |
| F4 | `uv run python -V` | `Python 3.14.5` (project venv unchanged) |
| F5 | `rg -n "3\.14" pyproject.toml .github/workflows/*.yml` | **15 matches = 14 real pins + 1 comment** (inventory below) |
| F6 | `uv pip install --python /tmp/py315b --dry-run --no-build -r pyproject.toml` | `× No solution found … Because pydantic-core==2.46.5 has no usable wheels and pydantic==2.13.5 depends on pydantic-core==2.46.5 … And because only pydantic<=2.13.5 is available and you require pydantic>=2.13.5` + `hint: Pre-releases are available for pydantic in the requested range` |
| F7 | same with `--prerelease=allow` | resolves only to `pydantic==2.14.0b2` + `pydantic-core==2.49.0` — i.e. **no *final* pydantic ships a cp315 wheel yet** |
| F8 | per-package `--no-build` probe on 3.15.0b1 | cp315 wheels **do** exist for `pydantic-core 2.49.0`, `orjson 3.12.0`, `pillow 12.3.0`, `argon2-cffi-bindings 26.1.0`, `cffi 2.1.1`, `sqlalchemy 2.1.3`, `greenlet 3.5.6` |
| F9 | PEP 758 probe on 3.15.0b1 (`except TypeError, ValueError:`) | `PEP758 OK` — the 3.14-only syntax at `src/backend/shared/principal.py:96` **still parses on 3.15**; not a risk |
| F10 | `rg -n "sqlite3\.connect\|contextmanager\|strptime\|ByteString\|sre_\|java_ver\|CGIRequestHandler" src -g '*.py' \| wc -l` | **0** — none of the 3.15 removals/behavior changes touch this code |
| F11 | `rg -n "asyncio\.|utcfromtimestamp\|utcnow\|configparser\|bcrypt\|argparse" src` | only local `_utcnow()` helpers returning `datetime.now(UTC)` (e.g. `src/backend/usermanagement/service.py:55`) — the removed `datetime.utcnow`/`utcfromtimestamp` are **not used** |
| F12 | job inventory (`quality.yml` 7, `lint.yml` 1, `spec-validation.yml` 3) | **11 jobs, no `strategy.matrix` anywhere** — every job hard-pins `python-version: '3.14'` |
| F13 | `rg -n "3\.14\|3\.15\|python.version\|requires-python" docs/specs/*.md` | **no match** — no spec pins a Python version; no spec depends on 3.14-only syntax |
| F14 | `rg -n "requires-python" uv.lock` | `uv.lock:3  requires-python = ">=3.14"` — the lock **must be regenerated** if the floor moves |
| F15 | `git worktree list` / `gh pr list --state open` | primary worktree only; **no open PRs** — nothing in flight to collide with |

## Closed from evidence (not asked)

- **The complete pin inventory (F5), 14 pins + 1 comment:** `pyproject.toml:7` `requires-python = ">=3.14"`; `pyproject.toml:132` mypy `python_version = "3.14"`; `pyproject.toml:143` ty `python-version = "3.14"` (comment at `:141` quotes it); CI `python-version: '3.14'` at `quality.yml:19,37,54,75,90,105,120` (7), `lint.yml:33` (1), `spec-validation.yml:35,64,78` (3). Plus `uv.lock:3` as a derived artifact.
- **`requires-python = ">=3.14"` already *permits* 3.15.** The gap is **CI coverage, not permission** — nothing in the project *forbids* running on 3.15; nothing *proves* it works. This reframes Option A as "add evidence", not "change a policy".
- **mypy and ty pins must move together** with `requires-python` — `pyproject.toml:141` states ty also infers from `requires-python` and is pinned "explicitly for documentation", so a floor change without the two tool pins is a documented inconsistency, not a silent one. They are one atomic edit.
- **`uv.lock` regeneration** is required only for a `requires-python` change (F14); Option A (CI-only) leaves the lock untouched.
- **No 3.14-only-syntax risk.** PEP 758 verified on 3.15 (F9); no spec pins a version (F13); the 3.15 removal checklist scores 0 against `src/` (F10, F11). The TODO's "3.15 behavior-change checklist" (sqlite3 keyword-only args, `strptime`, `argparse` dest, `typing.ByteString`, `sre_*`, CGI handler, `platform.java_ver`) has **no applicable site in this repo** — `contextlib.suppress` (14 sites) is not the `@contextmanager` decorator and is unaffected.
- **The upgrade-check command is settled:** `uv run --isolated --python 3.15 pytest -W error::DeprecationWarning` (already prescribed by the skill). Not a question; it belongs in the P.4 scope record.
- **`re.match` → `re.prefixmatch` is 5 sites** (`src/backend/search/service.py:84,88`; `src/backend/filemanagement/service.py:366,370`; `src/backend/filemanagement/storage.py:103`) — `re.match` is soft-deprecated, never removed, so this is optional and it is a `src/` change (see Q-6).

## Preparation questions (P.2)

**Q-1 — Which option, given the measured blocker?**
- **Step:** P.2 Interrogate
- **Why needed:** the three options are mutually exclusive policies with different cost and different scope; the choice decides what P.4 scopes at all.
- **Context:** F1/F2 — only `3.15.0b1` exists (no final, no RC). F6/F7 — the project's own `pyproject.toml` has **no wheel-only solution on 3.15**: `pydantic==2.13.5` pins `pydantic-core==2.46.5`, which has no cp315 wheel, and only the **pre-release** `pydantic 2.14.0b2` / `pydantic-core 2.49.0` resolves. F10/F11/F13 — the code itself has **zero** 3.15 incompatibilities.
- **Question:** which option do you want scoped?
  - **A — dual-version CI:** keep `requires-python >=3.14`, add 3.15 to CI. Keeps the compatibility promise; costs CI minutes (see Q-3); cannot run today without a beta interpreter and a pydantic pre-release (F1/F6).
  - **B — raise the floor to `>=3.15`:** single version; drops 3.14, forces the local venv (currently 3.14.5, F4), all 14 pins, and `uv.lock` regeneration (F14). Blocked today by F1/F6.
  - **C — defer (recommended):** record the measured blocker, add a *documented* re-check trigger (3.15 final **and** a final pydantic with a cp315 wheel), change nothing else. Cheapest, honest, and today A and B are both unrunnable without pinning CI to a beta interpreter + a pydantic pre-release — which makes every future CI failure ambiguous.
- **Answer:** **C — defer.** Record the measured blocker and add a **documented re-check trigger**: 3.15 final **and** a final `pydantic` with a cp315 wheel. Nothing else changes: `requires-python` stays `>=3.14`, the 14 pins and 11 CI literals stay as they are.
- **Date:** 2026-10-04
- **Status:** ANSWERED
- **Incorporated:** yes — the P.4 scope is now "record the blocker + the trigger" only; see the TODO's In scope

**Q-2 — Is a dependency bump in scope for a DOCS/CHORE change?**
- **Step:** P.2 Interrogate
- **Why needed:** this is the classification question. DOCS/CHORE requires a confirmed **no-behavior-delta** scope; bumping `pydantic` is a dependency change that can change validation behavior.
- **Context:** F6/F7 — 3.15 support requires `pydantic>=2.14` (currently only `2.14.0b2`) because `pydantic-core 2.46.5` has no cp315 wheel. `pyproject.toml:10` pins `pydantic>=2.13.5`. Every other compiled dep already has a cp315 wheel (F8), so pydantic is the **single** blocker.
- **Question:** if we move to 3.15, do you accept a `pydantic`/`pydantic-core` bump inside this change, or must it be a separate change (and this one stays pure config/CI)? If it is inside, this change is arguably no longer DOCS/CHORE — do you want it reclassified?
- **Answer:** **Closed as moot by Q-1 = (C)** — no dependency bump happens in this change, so the classification question does not arise. The change stays **DOCS/CHORE**. If the re-check trigger ever fires, the `pydantic` bump is its own change (and would be reclassified then).
- **Date:** 2026-10-04
- **Status:** ANSWERED
- **Incorporated:** yes — no bump in scope; DOCS/CHORE confirmed

**Q-3 — If Option A: what CI shape, and how many jobs?**
- **Step:** P.2 Interrogate
- **Why needed:** there is **no matrix in this repo** (F12) — "add 3.15 to the CI matrix" is not a one-line change; it means either introducing `strategy.matrix` across 11 jobs or duplicating a subset.
- **Context:** F12 — 11 jobs hard-pin `python-version: '3.14'` (`quality.yml` 7: type-check, security, coverage, dependency-review, dependencies, docs, migrations; `lint.yml` 1: lint; `spec-validation.yml` 3: spec-validation, traceability, tests). Full duplication ≈ 2× CI minutes.
- **Question:** (a) matrix all 11 jobs on `[3.14, 3.15]` (strongest signal, ~2× cost), or (b) one dedicated 3.15 job — recommended: the `tests` job in `spec-validation.yml` plus `coverage` in `quality.yml` (the two that actually execute the suite; the rest are lint/docs/dependency gates whose interpreter is irrelevant)?
- **Answer:** **Closed as moot by Q-1 = (C)** — Option A was not chosen, so no CI job shape is decided. The `pyproject-tooling-gaps` collision on the same 8 workflow job blocks therefore never materialises for this change.
- **Date:** 2026-10-04
- **Status:** ANSWERED
- **Incorporated:** yes — no workflow edit in scope

**Q-4 — Python support window: keep 3.14 forever, or track "latest two"?**
- **Step:** P.2 Interrogate
- **Why needed:** it decides whether the 11 CI pins become a single reusable variable/matrix (a policy that recurs every release) or stay per-job literals that get hand-edited again next year.
- **Context:** F5 — 11 duplicated literals is why this change exists at all; the same edit recurs annually. PEP 790 gives a fixed ~2-year cadence.
- **Question:** what is the project's stated support window — "latest CPython only", "latest two" (recommended), or "everything `requires-python` permits"? And should the pins be consolidated into one `strategy.env`/matrix value so the next bump is one line?
- **Answer:** **Latest two CPython versions.** With `requires-python >=3.14` that means 3.14 + 3.15 once 3.15 is final — exactly what Q-1's trigger then delivers. "Latest only" (floor moves, 3.14 support ends) and "everything the floor permits" (CI cost grows every year) were rejected. Pin consolidation is **not** pulled into this change — Q-1 = (C) left the 11 literals alone — so the annual one-line-pin problem is recorded as a follow-up for the upgrade change.
- **Date:** 2026-10-04
- **Status:** ANSWERED
- **Incorporated:** yes — the support window is now part of the P.4 scope; see the TODO's In scope

**Q-5 — Test the free-threaded build (`3.15t`) at all?**
- **Step:** P.2 Interrogate
- **Why needed:** it is a separate CI axis with its own cost, and the repo makes thread-safety claims in its specs.
- **Context:** F2 — `cpython-3.15.0b1+freethreaded` is downloadable. `AGENTS.md` claims the logging setup is "idempotent and thread-safe" and the event bus runs background workers; the event bus and settings registry are module singletons.
- **Question:** do you want a free-threaded CI job (recommended: **no** — free-threaded cp315 wheels for `pydantic-core`/`argon2-cffi-bindings`/`greenlet` are a separate availability question, and a free-threaded failure would be indistinguishable from a 3.15 failure while both are pre-release)?
- **Answer:** **Closed as moot by Q-1 = (C)** — no 3.15 CI job exists to add a `3.15t` axis to. Revisit only if the re-check trigger fires; the thread-safety claims (`logging` setup, event-bus worker, module singletons) then get their own question.
- **Date:** 2026-10-04
- **Status:** ANSWERED
- **Incorporated:** yes — out of scope

**Q-6 — Is the `re.match` → `re.prefixmatch` modernization part of this change?**
- **Step:** P.2 Interrogate
- **Why needed:** it is a `src/` edit. Under DOCS/CHORE the scope must be confirmed no-behavior-delta; touching 5 service/storage sites makes it a REFACTOR (GREEN baseline required), which changes the todo set.
- **Context:** 5 sites: `src/backend/search/service.py:84,88`, `src/backend/filemanagement/service.py:366,370`, `src/backend/filemanagement/storage.py:103`. `re.match` is soft-deprecated and never removed, so nothing breaks if it is left alone. The skill's version gate (`.agents/skills/python-best-practices/references/python-3.15.md:7`) forbids 3.15-only features unless `requires-python >=3.15` **and** CI runs 3.15 — so under Option A/C this edit is **not yet permitted**.
- **Question:** include it (→ reclassify REFACTOR), or leave it out of scope?
- **Answer:** **Leave it out of scope** — a consequence of Q-1 = (C): the skill's version gate (`python-best-practices/references/python-3.15.md:7`) forbids 3.15-only features unless `requires-python >=3.15` **and** CI runs 3.15, neither of which holds. The change stays DOCS/CHORE, no `src/` edit, no REFACTOR reclassification. The 5 sites are recorded as a follow-up for whenever the trigger fires.
- **Date:** 2026-10-04
- **Status:** ANSWERED
- **Incorporated:** yes — recorded in the TODO's Out of scope

## Overlap check (P.2)

- **In flight:** `git worktree list` → primary only; `gh pr list --state open` → none (F15). No live collision.
- **`pyproject-tooling-gaps` (the real collision).** It declares its files as `pyproject.toml`, `.pre-commit-config.yaml`, `.github/workflows/lint.yml`, `.github/workflows/quality.yml`, `README.md`. Exact overlapping lines with this change: **`quality.yml:19,37,54,75,90,105,120`** and **`lint.yml:33`** (that TODO rewrites the 8 `uv sync --only-group dev` lines that sit in the same job blocks as these `python-version` pins), and **`pyproject.toml:7/132/143`** (that TODO edits `[tool.mypy]` directly below `:132` and the `[tool.deptry]`/dev-group regions). Whichever merges second must rebase those 8 workflow lines and the mypy block.
- **Other TODOs touching the same files:** `docs-path-ci-trigger` and `workflow-docs-nits` (workflow files), `tenacity-rich-cachetools` (adds deps to `pyproject.toml` — relevant to Q-2), `track-python-skill` (the 3.15 reference file this change's gate cites), `update-readme`/`structure-map` (README quickstart, which states the interpreter).
- **Specs:** no `docs/specs/` file pins a Python version or relies on 3.14-only syntax (F13) — no spec amendment needed under any option.

## For P.4 (scope record) — exact edit list per option

**Option A (CI-only, floor unchanged).** No `pyproject.toml` change, no `uv.lock` change.
- Introduce a matrix/env value or duplicate: `quality.yml:19,37,54,75,90,105,120`, `lint.yml:33`, `spec-validation.yml:35,64,78` — subset per Q-3 (recommended: `spec-validation.yml:78` `tests` + `quality.yml:54` `coverage`).
- Prerequisite gate from F1/F6: needs 3.15 final **and** a final pydantic with a cp315 wheel, else the job runs a beta interpreter + `pydantic 2.14.0b2`.

**Option B (raise the floor).** All 14 pins move together:
- `pyproject.toml:7` `requires-python = ">=3.15"`; `pyproject.toml:132` mypy; `pyproject.toml:143` ty (+ the comment at `:141`).
- `quality.yml:19,37,54,75,90,105,120`; `lint.yml:33`; `spec-validation.yml:35,64,78`.
- `uv.lock:3` regenerated (F14); local venv recreated on 3.15 (F4: currently 3.14.5); `pydantic` floor raised per Q-2.

**Option C (defer, chosen).** No pin changes. Scope = record the measured blocker (F1, F6, F7), the **support window (latest two CPython versions)**, the re-check trigger (3.15 final **and** a final `pydantic` with a cp315 wheel) and the check command (`uv run --isolated --python 3.15 pytest -W error::DeprecationWarning`), and open a **backlog TODO** (`python-3.15-upgrade`) carrying that trigger so the re-check is a visible scheduled change rather than a note only findable in a closed record. Zero CI cost, zero behavior delta — the only option that is honestly DOCS/CHORE today.

## Late questions (Phases 2–6)

<questions discovered after the change entered the workflow; same entry format, Step field set to the step that found it>
