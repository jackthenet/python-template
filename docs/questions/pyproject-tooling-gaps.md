# Questions: pyproject-tooling-gaps

One question file per change, created at **P.1 Frame** from this template and named `pyproject-tooling-gaps.md`. It replaces the retired central `AI_Questions.md` (archived at `docs/questions/archive-AI_Questions.md`).

- **Change:** pyproject-tooling-gaps (DOCS/CHORE)
- **TODO file:** `docs/todo/pyproject-tooling-gaps.md`
- **Spec:** n/a
- **Opened:** 2026-10-03
- **Status:** ALL ANSWERED  <!-- OPEN | ALL ANSWERED — set OPEN by the orchestrator at P.1; ALL ANSWERED once every question in this file has an answer (the orchestrator records it together with the `QUESTIONS-ANSWERED` TODO advance) -->
- **Answer rounds:** 3 (2026-10-04: round 1 Q-1, Q-4, Q-5, Q-6; round 2 Q-1 follow-up, Q-2, Q-3, Q-10; round 3 Q-7, Q-8, Q-9)

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

DOCS/CHORE — no ≥ 20 floor. 10 questions, all genuinely user-owned decisions; every fact that could be measured was measured instead of asked (see *Re-measured facts* and *Closed from evidence* below).

Date of all measurements: **2026-10-03**, on `main` @ `cb8e63c`, primary worktree.

---

## Q-1 — Does complexipy stay a gate at all?
- **Step:** P.2 Interrogate
- **Why needed:** The whole complexipy item (CI job? threshold? comment?) follows from this, and the two engines disagree. It is the largest surviving item in the TODO.
- **Context:** `complexipy` appears in exactly two places — the dev group (`pyproject.toml:36`, `complexipy>=8.0.1`) and the pre-commit hook (`.pre-commit-config.yaml:23-26`, `rev: v5.1.0`). `rg -n complexipy .github/workflows/*.yml` → **no match**: it runs in no CI job. Meanwhile ruff already gates complexity in CI: `select` includes `PL` (`pyproject.toml` `[tool.ruff.lint]`), and `uv run ruff check --select PLR0911,PLR0912,PLR0915 .` → **All checks passed** (two documented suppressions: `src/backend/settings/models.py:69` `# noqa: PLR0911, PLR0912`, `:230` `# noqa: PLR0912`, plus `permissions/service.py:344`).
- **Question:** Which of these is the intended end state?
  - **(A) Drop complexipy entirely** — remove the hook, the dev pin, the `[tool.complexipy]` block (`pyproject.toml:92-94`) and its `DEP002` entry (`pyproject.toml:116`); ruff `PLR0911/0912/0915` already enforces complexity in CI with named, justified `noqa`s. *(recommended)*
  - **(B) Keep it pre-commit-only** and add a one-line comment saying it is a local advisory report, CI-enforced complexity is ruff `PLR091x`.
  - **(C) Add a CI job** at a threshold the tree passes today (≥ 47, or `src/`-only at ≥ 47) — a third engine, permanently above ruff's limits.
  - **(D) Add a CI job at 30** — red on day one (see Q-3), not a no-op.
- **Answer:** **(C') New CI job at complexipy's default threshold 15** — the user's own option, not (A)/(B)/(C)/(D). Consequence measured 2026-10-04: at 15 the tree is red on **10 functions** — `src/`: `permissions/service.py::PermissionService::_check` 17, `search/service.py::SearchService::search` 17, `sessionmanagement/service.py::SessionService::list_sessions` 18, `settings/models.py::SettingDefinition::_validate` 26, `settings/models.py::is_valid_value` 47; `tests/`: `test_nfr_005_concurrent_threads_safe` 18, `mail_test_helpers.py::FakeSmtpServer::_dialogue` 17, `test_last_admin_invariant` 23, `test_inv_006_event_correspondence` 22, `test_inv_003_last_admin_invariant` 38 (`uv run complexipy src tests --max-complexity-allowed 15` → exit 1). The **snapshot ratchet** (`complexipy-snapshot.json`, 1949 bytes, auto-loaded → exit 0) and **threshold 47** were both offered and **rejected**: the 10 offenders are refactored first, and (round 3) folded into this change — see Q-2/Q-3 and the TODO's reclassification.
- **Date:** 2026-10-04
- **Status:** ANSWERED
- **Incorporated:** yes — new complexipy CI job at 15 + the 10-function refactor are now In scope; drove the REFACTOR reclassification

## Q-2 — If complexipy stays: which version pin wins, the hook's `v5.1.0` or the dev group's `>=8.0.1`?
- **Step:** P.2 Interrogate
- **Why needed:** The two pins are different implementations (pre-rewrite Python engine vs the Rust rewrite) and score the same code differently, so the configured `threshold: 30` is not a single meaningful number.
- **Context:** Measured on the same tree, same `max-complexity-allowed = 30`:
  | function | hook `v5.1.0` | dev `8.0.1` |
  |---|---|---|
  | `settings/models.py::is_valid_value` | **47 FAILED** | **47 FAILED** |
  | `tests/property/usermanagement/test_usermanagement_properties.py::test_inv_003_last_admin_invariant` | **20 PASSED** | **38 FAILED** |
  | `test_inv_006_event_correspondence` | 25 | 22 |
  | `SettingDefinition::_validate` | 26 | 26 |
  Also: the hook receives filenames from pre-commit, so it scans `scripts/` and `migrations/env.py` too — `[tool.complexipy] paths = ["src", "tests"]` (`pyproject.toml:93`) is dead config under the hook.
- **Question:** If Q-1 is B/C/D: align the hook `rev` up to the 8.x line (hook follows the dev pin), or pin the dev group down to 5.x (dev pin follows the hook)? *(recommended: hook `rev` → the current 8.x tag; the dev pin is what agents run.)* If Q-1 is A, this question is moot — answer "moot".
- **Answer:** **8.0.1 only.** The dev group's `complexipy>=8.0.1` is authoritative and the CI job runs `uv run complexipy`; the hook is removed (Q-3), so the pre-rewrite 5.1.0 scorer stops existing and the two-engine scoring split (`test_inv_003`: 20 under 5.1.0 vs 38 under 8.0.1) disappears. No dev-pin downgrade.
- **Date:** 2026-10-04
- **Status:** ANSWERED
- **Incorporated:** yes — dev pin `complexipy>=8.0.1` is the only pin; hook removed — see In scope

## Q-3 — The complexipy pre-commit hook fails on `main` today. Fix, exempt, or raise the threshold?
- **Step:** P.2 Interrogate
- **Why needed:** This is the escalation trigger for the change type. Any option except "raise the threshold / drop the tool" requires touching `src/` — that is a REFACTOR change, not a DOCS/CHORE.
- **Context:** `uv run pre-commit run complexipy --all-files` → **exit 1**, `complexipy...Failed`, `Failed functions: - models.py: is_valid_value`. So committing `src/backend/settings/models.py` currently needs `--no-verify`. Under the dev-pinned 8.0.1 there are **2** offenders (47 and 38); everything else is ≤ 26 (`SettingDefinition::_validate` 26, `test_last_admin_invariant` 23, `check_acyclic` 22). `is_valid_value` is already `# noqa: PLR0911, PLR0912`-suppressed in ruff (`src/backend/settings/models.py:69`).
- **Question:** (a) raise/exempt so the gate passes without code changes; (b) leave the hook failing and record it; (c) split out a separate REFACTOR change for `is_valid_value` (47) and `test_inv_003_last_admin_invariant` (38) and keep this change config-only? *(recommended: (c) if the gate stays at all — a 47-scoring function split is not a chore; (a)/drop if Q-1 = A.)*
- **Answer:** **Drop the hook** — remove `.pre-commit-config.yaml:23-26`. With complexipy becoming a CI job the hook is redundant, and it fails on `main` today (`is_valid_value` 47 > 30), which is why commits touching `src/backend/settings/models.py` currently need `--no-verify`. One engine (8.0.1), one place (CI). The `is_valid_value` split itself is folded into this change as part of the 10-function refactor.
- **Date:** 2026-10-04
- **Status:** ANSWERED
- **Incorporated:** yes — hook removal (`.pre-commit-config.yaml:23-26`) is In scope

## Q-4 — `py-webauthn` is undeclared, but the approved spec and ADR-031 both list it as a dependency. Declare it, make it an extra, or leave it?
- **Step:** P.2 Interrogate
- **Why needed:** The TODO frames this as "add `[project.optional-dependencies] webauthn`", but the normative documents say it is a plain dependency. An extra would contradict them; declaring it adds a runtime dependency, which the TODO lists out of scope. Only the user can resolve the contradiction.
- **Context:** `rg -n "optional-dependencies|extras" pyproject.toml` → no match; `py-webauthn` is in **neither** `[project.dependencies]`, `[dependency-groups]` nor `uv.lock`. `uv run python -c "import webauthn"` → `ModuleNotFoundError`. The import is deferred (`src/backend/authentication/webauthn.py:22-28`) and raises `InvalidPasskeyResponseError("py-webauthn is required …")`. It is suppressed in deptry by `DEP001 = ["webauthn"]` (`pyproject.toml:123`) and in ty by `allowed-unresolved-imports = ["webauthn"]` (`:155`). Against that: `docs/specs/authentication.md:21` — *"Dependencies: … `py-webauthn>=2.0.0`"* — and `docs/decisions/ADR-031-py-webauthn-provider.md:48` — *"`pyproject.toml` (`py-webauthn>=2.0.0`)"*. Tests never need the package (`PyWebAuthnProvider` appears only in the logging-coverage and public-API contract tests, which do not call the WebAuthn functions).
- **Question:** (a) declare `py-webauthn>=2.0.0` in `[project.dependencies]` — matches spec + ADR, removes the `DEP001`/ty suppressions, but adds a real dependency and changes `uv.lock`; (b) add the `[project.optional-dependencies] webauthn` extra — discoverable, but deviates from the spec's dependency list → needs a Spec Amendment PR for `docs/specs/authentication.md`; (c) leave undeclared and only improve the comment. *(recommended: (a) — it is not a "dependency addition", it is declaring one the approved spec already requires; (b) is the only option that triggers a spec amendment.)*
- **Answer:** **(a) Declare `py-webauthn>=2.0.0`** in `[project.dependencies]`, and drop the two suppressions it exists behind: deptry `DEP001 = ["webauthn"]` (`pyproject.toml:123`) and ty `allowed-unresolved-imports = ["webauthn"]` (`:155`). `uv.lock` changes. This matches `docs/specs/authentication.md:21` and `ADR-031-py-webauthn-provider.md:48`, so **no Spec Amendment** is needed; the extra (b) was rejected.
- **Date:** 2026-10-04
- **Status:** ANSWERED
- **Incorporated:** yes — `py-webauthn>=2.0.0` declared; `DEP001` + ty suppressions dropped — see In scope

## Q-5 — Enable ruff `DTZ`? It has exactly 1 violation, and fixing it is not comment-only.
- **Step:** P.2 Interrogate
- **Why needed:** The TODO records `DTZ` as "near-free / no naive `datetime.now()` found" — that is true for `src/` but false repo-wide, and `lint.yml:37` runs `ruff check .` (whole repo, tests included). Enabling it therefore turns CI red unless the one site changes.
- **Context:** `uv run ruff check --select DTZ .` → **1 error**: `DTZ005 datetime.now() called without a tz argument` at `tests/tooling_test_helpers.py:53` (`yield datetime.now()` inside the `time-machine` helper). `src/` is clean. The fix is one line, but it changes the value the shared `travel()` helper yields (naive → aware), which is observable to the tests that use it — so it needs a suite run, not just a config edit.
- **Question:** (a) select `DTZ` **and** fix `tests/tooling_test_helpers.py:53` in this change (verify the full suite stays green); (b) select `DTZ` with a `noqa`/per-file ignore on that helper; (c) leave `DTZ` off and add a one-line comment saying why. *(recommended: (a) — one line, and the helper is the right place to be tz-aware.)*
- **Answer:** **(a)** select `DTZ` **and** fix `tests/tooling_test_helpers.py:53` (naive → aware `datetime.now()`) inside this change; the full suite must stay green, since the value the shared `travel()` helper yields is observable to its users. No `noqa`, no per-file ignore.
- **Date:** 2026-10-04
- **Status:** ANSWERED
- **Incorporated:** yes — `DTZ` selected + `tests/tooling_test_helpers.py:53` fixed — see In scope

## Q-6 — How far should `[tool.agent-runner] quality_check` mirror CI? (It also lints only `src/`, while CI lints the whole repo.)
- **Step:** P.2 Interrogate
- **Why needed:** "Full parity" is not one edit — CI gates nine things, and the current string is narrower than CI in two independent ways (missing tools **and** narrower path scope).
- **Context:** `pyproject.toml:214`: `quality_check = "uv run ruff check src/ && uv run mypy src/"`. CI gates: `ruff check .` + `ruff format --check .` (`lint.yml:37,39`), `mypy src/` (`quality.yml:23`), `ty check src/` (`:25`), `pip-audit` (`:41`), `bandit -r src/` (`:43`), `pytest tests/ --cov` with `fail_under = 92` (`:59`, `pyproject.toml:105`), `deptry .` (`:94`), `mkdocs build --strict` (`:109`), `alembic upgrade head` (`:127`), `check_traceability.py` (`spec-validation.yml:68`). Note: **nothing in this repository reads `[tool.agent-runner]`** (`rg -n "agent-runner|quality_check" --glob '!docs/**'` → only `pyproject.toml:211,214`), so the string is advisory for the external runner — a full-parity string would put `pip-audit`, `mkdocs` and `alembic` in every task loop. Baseline check: `uv run ruff check .` → *All checks passed*, so widening `src/` → `.` is free today.
- **Question:** (a) AGENTS.md Phase 5 parity — `uv run ruff check . && uv run mypy src/ && uv run deptry .`; (b) add only `deptry`; (c) leave as-is with a comment naming what CI adds. *(recommended: (a) — it matches the documented Phase 5 gate set exactly and is free today; coverage/complexipy/pip-audit/mkdocs/alembic stay CI-only.)* If Q-1 keeps complexipy as a CI job (option C), does it join `quality_check` too?
- **Answer:** **(a) Phase 5 parity** — `uv run ruff check . && uv run ruff format --check . && uv run mypy src/ && uv run deptry .`. Free today (`uv run ruff check .` → All checks passed). `pip-audit`, `mkdocs`, `alembic` and the coverage gate stay CI-only. complexipy does **not** join `quality_check` — it is a CI gate, not a per-task loop gate.
- **Date:** 2026-10-04
- **Status:** ANSWERED
- **Incorporated:** yes — `quality_check` rewritten to the Phase 5 gate set — see In scope

## Q-7 — Docs dependency-group split: do it or drop it?
- **Step:** P.2 Interrogate
- **Why needed:** It is the only item whose diff is wider than its benefit, and the TODO left it explicitly to P.3.
- **Context:** Moving `mkdocs`, `mkdocs-material`, `mkdocstrings[python]` (`pyproject.toml:42,44,46`) to a separate group touches **11** `uv sync --only-group dev` lines — `quality.yml:21,39,56,77,92,107,122` (7), `spec-validation.yml:37,66,80` (3), `lint.yml:35` (1) — plus the `mkdocs-build` pre-push hook (`.pre-commit-config.yaml:37-43`) and the README quickstart (`README.md:5-9`, currently just `uv sync`). The `docs` job (`quality.yml:107-109`) is the only consumer that needs the three packages.
- **Question:** Split (and update all 11 lines + hook + README), or drop the item? *(recommended: drop — 3 packages against an 11-line CI diff and a new way to break the docs job.)*
- **Answer:** **Do the split.** Move `mkdocs`, `mkdocs-material`, `mkdocstrings[python]` (`pyproject.toml:42,44,46`) into a `docs` dependency group and update every consumer: the 11 `uv sync --only-group dev` lines (`quality.yml:21,39,56,77,92,107,122`; `spec-validation.yml:37,66,80`; `lint.yml:35`), the `mkdocs-build` pre-push hook (`.pre-commit-config.yaml:37-43`), and the README quickstart (`README.md:5-9`). Collision recorded: `update-readme` also edits the README quickstart — the two README edits must be sequenced.
- **Date:** 2026-10-04
- **Status:** ANSWERED
- **Incorporated:** yes — docs dependency group split is In scope, incl. the 11 CI lines + hook + README

## Q-8 — mypy permissiveness: comment only, or tighten now that the cost is measured?
- **Step:** P.2 Interrogate
- **Why needed:** The TODO says "cost unmeasured" and warns of a cascade; it is now measured, and it is small enough that the user may want the flag on rather than a comment about it.
- **Context:** `[tool.mypy]` (`pyproject.toml:131-138`) sets only `check_untyped_defs`, `ignore_missing_imports`, `explicit_package_bases`, `namespace_packages`. Measured over 83 source files: `uv run mypy src/ --disallow-untyped-defs` → **8 errors in 6 files**; `uv run mypy src/ --warn-return-any` → **20 errors in 12 files**. Both are `src/` edits → enabling either is a REFACTOR-sized change, not a chore.
- **Question:** (a) comment only, recording the measured numbers (chore-safe); (b) also enable `disallow_untyped_defs` and fix the 8 (escalates this change to REFACTOR or needs a follow-up change first); (c) open a separate backlog TODO for the strictness step and reference it in the comment. *(recommended: (a) or (c).)*
- **Answer:** **(b) Enable `disallow_untyped_defs` and fix the 8 errors in 6 files in this change.** Together with the 10-function complexity refactor this is a `src/` + `tests/` restructuring, so it **reclassifies this change from DOCS/CHORE to REFACTOR** (GREEN baseline required, no test weakened or deleted). `warn-return-any` (20 errors in 12 files) stays off, with the measured number recorded in the comment.
- **Date:** 2026-10-04
- **Status:** ANSWERED
- **Incorporated:** yes — `disallow_untyped_defs` enabled + 8 fixes; `warn-return-any` left off with the number recorded

## Q-9 — Ruff `D` (pydocstyle): confirm it stays out of scope.
- **Step:** P.2 Interrogate
- **Why needed:** The TODO defers the decision to P.3 and its own estimate (156) understates the measured cost.
- **Context:** `uv run ruff check --select D src` → **379 errors** (the TODO's "156 of 515 public defs lack a docstring" counts only the `D1xx` family; `D` also pulls in `D2xx`/`D4xx` formatting rules). No `D` code is in `select` today.
- **Question:** Confirm (a) leave `D` off entirely (recommended), or (b) select `D` with a per-file ignore list now, or (c) record a separate backlog TODO for the docstring backfill?
- **Answer:** **Leave `D` off, and open a backlog TODO for the backfill.** Framed as **`ruff-d-docstrings`** on 2026-10-04 carrying the measured cost (`uv run ruff check --select D src` → **379 errors**; the TODO's 156 counted only the `D1xx` family), so the gap is scheduled rather than invisible. No `D` code enters `select`.
- **Date:** 2026-10-04
- **Status:** ANSWERED
- **Incorporated:** yes — `D` stays off; backlog item `ruff-d-docstrings` framed 2026-10-04

## Q-10 — Sequencing against `python-3.15` and the other config-touching backlog items.
- **Step:** P.2 Interrogate
- **Why needed:** Three backlog items edit the same workflow job blocks; the order decides whether the two changes conflict.
- **Context:** See the *Overlap and collision analysis* table below. `python-3.15` (`docs/todo/python-3.15.md`, `Status: WAITING`, not yet READY) edits `pyproject.toml:7,132,143` and **11** `python-version: '3.14'` pins (`quality.yml:19,37,54,75,90,105,120`; `lint.yml:33`; `spec-validation.yml:35,64,78`) — re-measured today, its own TODO says to sequence after this change. `docs-path-ci-trigger` (PREPARING, recommendation "drop") edits `spec-validation.yml` `paths:` blocks; `update-readme` and `security-changelog-license` both edit `README.md`, which this change touches **only** if Q-7 = split.
- **Question:** Confirm the order **pyproject-tooling-gaps → python-3.15** (and that a new complexipy CI job, if Q-1 = C, is added as a *new* job block rather than by editing existing job blocks, to keep the two diffs disjoint)?
- **Answer:** **pyproject-tooling-gaps first.** `python-3.15` was **DROPPED as satisfied** on 2026-10-04, so its collision on the 11 `python-version` pins disappears; that work now lives in `python-3.15-upgrade`, which is trigger-gated (3.15 final + a final pydantic with a cp315 wheel) and therefore rebases on this change later, not the reverse. Any new complexipy job is added as a **new job block** in `quality.yml`, never by editing existing job blocks, keeping the diffs disjoint. `architecture-tests-missing` and `value-triage-gate` touch different files and are independent.
- **Date:** 2026-10-04
- **Status:** ANSWERED
- **Incorporated:** yes — TODO `Depends on:` updated — this change is the predecessor of `python-3.15-upgrade`

---

## Re-measured facts (claim → verdict → evidence)

| # | Claim (from P.1 / external review) | Verdict | Re-measured evidence (2026-10-03, `main` @ `cb8e63c`) |
|---|---|---|---|
| 1 | `quality_check` is only `ruff check src/ && mypy src/`, omitting CI-gated tools | **TRUE** (and understated) | `pyproject.toml:214`. CI gates it omits: `ruff check .` + `ruff format --check .` (`lint.yml:37,39`), `ty` (`quality.yml:25`), `pip-audit` (`:41`), `bandit` (`:43`), `pytest --cov` (`:59`), `deptry .` (`:94`), `mkdocs` (`:109`), `alembic` (`:127`), `check_traceability.py` (`spec-validation.yml:68`). Also narrower path scope: `src/` vs CI's `.` |
| 2 | The 92 % coverage floor **is** enforced; `deptry` **is** enforced → the two headline review claims are false | **TRUE** (claims are false) | `pyproject.toml:105` `fail_under = 92`; `quality.yml:58-59` comment + `uv run pytest tests/ --cov --cov-report=xml`. deptry: `quality.yml:94` + local hook `.pre-commit-config.yaml:28-36` (`entry: uv run deptry .`, `files: ^(pyproject\.toml|uv\.lock|src/|tests/|scripts/|migrations/)`) |
| 3 | complexipy runs nowhere in CI; hook pins `v5.1.0`, dev group pins `>=8.0.1` → two engines | **TRUE** | `rg -n complexipy .github/workflows/*.yml` → no match. `.pre-commit-config.yaml:23-26` `rev: v5.1.0`; `pyproject.toml:36` `complexipy>=8.0.1`; installed: `complexipy 8.0.1`. Divergence table in Q-2 (47/47, **20 vs 38**, 25 vs 22, 26/26) |
| 4 | The tree already violates `threshold: 30`: `is_valid_value` = 47, `test_inv_003_last_admin_invariant` = 38 | **PARTLY TRUE — engine-dependent** | Under the dev pin 8.0.1 (`uv run complexipy`, exit **1**): 47 and 38 both FAILED. Under the pinned hook `v5.1.0` (`uv run pre-commit run complexipy --all-files`, exit **1**): only `is_valid_value` 47 FAILED; `test_inv_003…` scores **20 PASSED**. So the hook *does* fail today, but on **one** function, not two. Next-highest: 26 (`SettingDefinition::_validate`) |
| 5a | webauthn optional-extra | **PARTLY TRUE / contradicts the normative docs** | No `optional-dependencies` anywhere; `py-webauthn` absent from deps and `uv.lock`; `import webauthn` → `ModuleNotFoundError`; deferred import `src/backend/authentication/webauthn.py:22-28`; suppressed by `DEP001` (`pyproject.toml:123`) and ty `:155`. But `docs/specs/authentication.md:21` and `ADR-031:48` both state `py-webauthn>=2.0.0` **as a dependency** → Q-4 |
| 5b | ruff `DTZ` is near-free | **PARTLY TRUE** | `uv run ruff check --select DTZ .` → **1 error**, `tests/tooling_test_helpers.py:53` (`datetime.now()` naive). `src/` clean. `lint.yml:37` lints the whole repo → enabling `DTZ` is red until that line changes → Q-5 |
| 5c | docs-dependency-group split | **TRUE but wider than the TODO states** | **11** `uv sync --only-group dev` lines (`quality.yml:21,39,56,77,92,107,122`; `spec-validation.yml:37,66,80`; `lint.yml:35`) — the TODO said 8 — plus `.pre-commit-config.yaml:37-43` and `README.md:5-9` → Q-7 |
| 6 | mypy permissiveness cost unmeasured | **MEASURED — small** | `--disallow-untyped-defs` → 8 errors / 6 files; `--warn-return-any` → 20 errors / 12 files (83 source files) → Q-8 |
| 7 | ruff `D` backfill ≈ 156 | **UNDERSTATED** | `uv run ruff check --select D src` → **379 errors** → Q-9 |
| 8 | (new) complexity is already CI-gated | **NEW FINDING** | `PL` is in `[tool.ruff.lint] select`; `uv run ruff check --select PLR0911,PLR0912,PLR0915 .` → **All checks passed** with 2 documented `noqa`s (`src/backend/settings/models.py:69,230`). `PLR0913` is globally ignored (`ignore` list) → 22 violations if enabled. This is the strongest argument for Q-1 (A) |
| 9 | (new) `[tool.complexipy] paths = ["src","tests"]` is dead config | **NEW FINDING** | The hook is invoked with filenames by pre-commit, so it also scored `scripts/ruff-post-edit.py`, `scripts/check_traceability.py`, `scripts/validate_task_dag.py`, `scripts/verify_spec.py` and `migrations/env.py` |
| 10 | (new) nothing consumes `[tool.agent-runner]` | **NEW FINDING** | `rg -n "agent-runner|quality_check" --glob '!docs/**'` → only `pyproject.toml:211,214`. The string is advisory for the external runner → Q-6 |

## Closed from evidence (no question needed)

1. **Coverage floor** — enforced in CI (`pyproject.toml:105` + `quality.yml:59`); nothing to do, and the TODO already puts raising it out of scope.
2. **deptry** — enforced twice (`quality.yml:94`, `.pre-commit-config.yaml:28-36`); nothing to do.
3. **`ruff check .` is clean today** (`All checks passed!`), so widening `quality_check` from `src/` to `.` costs nothing (Q-6 option (a) is free).
4. **pre-commit is not a CI job** — `.pre-commit-config.yaml` appears in `lint.yml:10,19` only as a `paths:` trigger. So "the hook gates it in CI" is not true for any hook.
5. **No spec pins a tool version or the coverage floor** — `rg -n "92 ?%|fail_under|complexipy|deptry|DTZ" docs/specs/*.md` → no NFR/AC pins them (the 92 % figure appears only in `docs/questions/`, `docs/verification/` and `docs/todo/`). Changing the floor would **not** need a spec amendment — but it stays out of scope.
6. **The only spec/ADR conflict in scope is py-webauthn** (`docs/specs/authentication.md:21`, `ADR-031:48`) → raised as Q-4 rather than silently "fixed".
7. **In-flight state is clear**: `git worktree list` → primary only (`C:/workspace/active-projects/python-template_kopie  cb8e63c [main]`); `gh pr list --state open` → none. So no in-flight change is disturbed by a new CI gate — the TODO's "land it when few changes are in flight" constraint is satisfied today.

## Overlap and collision analysis (vs the 18 `docs/todo/` items)

| Backlog item | Status | Touches | Collision with this change |
|---|---|---|---|
| `python-3.15` | WAITING (P.2 answered, not READY) | `pyproject.toml:7,132,143` + 11 `python-version: '3.14'` pins: `quality.yml:19,37,54,75,90,105,120`, `lint.yml:33`, `spec-validation.yml:35,64,78` (+ `uv.lock:3`) | **Highest.** Same job blocks. `quality.yml:19` and `:21` are 2 lines apart; `pyproject.toml:132/:143` sit between the mypy/ty blocks this change may annotate. Its own TODO already says *"sequence after `pyproject-tooling-gaps`"* |
| `docs-path-ci-trigger` | PREPARING, own recommendation **drop (1/5)** | `spec-validation.yml` `paths:` blocks (`:6-14` + push block) | Low; same file, different lines. If it is ever picked up it must not edit job blocks |
| `update-readme` | PREPARING | `README.md` (+ badges) | Only if Q-7 = split (this change would edit `README.md:5-9`) |
| `security-changelog-license` | WAITING | `LICENSE`/`SECURITY.md`/`CHANGELOG.md`, maybe `README.md`, maybe `[tool.bumpversion.files]` (`pyproject.toml:79-91`) | Low — different `pyproject.toml` section; `README.md` shared only with Q-7 |
| `tenacity-rich-cachetools` | PREPARING | `[project.dependencies]` / `[dependency-groups]` | Medium if Q-4 = (a)/(b) — same region (`pyproject.toml:8-25` deps, `:27-58` groups) |
| `structure-map` | WAITING | new `scripts/` + tests | Indirect: new tests shift coverage against the 92 floor; no textual overlap |
| `architecture-tests-missing`, `session-lookup-unwired`, `remove-spec-tdd-driver`, `structlog-logging`, `api-keys`, `notifications`, `spec-interview-protocol`, `split-archived-qa`, `track-python-skill` (MERGED), `value-triage-gate`, `workflow-docs-nits` | mixed | no config overlap | none |

**Recommended order:** land **`pyproject-tooling-gaps` first**, then `python-3.15`. Reasons: (1) this change is config-only and small, and it *decides* whether a complexipy job block exists — `python-3.15` must then add its pin to that block rather than have it appear under it; (2) `python-3.15` is not READY (WAITING on its 6 P.2 answers, and its own P.2 found a hard blocker: `pydantic-core==2.46.5` has no cp315 wheel), so it cannot start first anyway; (3) if Q-1 = C (new CI job), add it as a **new job block appended after the existing jobs** in `quality.yml`, never by editing an existing job's step list — that keeps the two diffs disjoint even though both touch the file. If the user prefers the reverse order, `python-3.15` must land and its 11 pins re-measured before this change re-derives its own line list.

## For P.4 (scope record) — safe no-ops vs not

**True no-ops (config/comment only; every CI job keeps its current result):**
- Extend `[tool.agent-runner] quality_check` (`pyproject.toml:214`) — nothing in the repo consumes it; `ruff check .` and `deptry .` both pass today, so even a full-parity string cannot turn CI red.
- Add explanatory comments: complexipy scope/threshold rationale, mypy permissiveness (with the measured 8 / 20 numbers), `DTZ` decision, `DEP001` pointer.
- Remove complexipy entirely (Q-1 = A): deletes the hook (`.pre-commit-config.yaml:23-26`), the dev pin (`:36`), `[tool.complexipy]` (`:92-94`), the `DEP002` entry (`:116`). No CI job references complexipy, so no job changes result — and it *stops* a locally failing hook. **Cheapest honest outcome.**
- Keep complexipy pre-commit-only + comment (Q-1 = B) — no CI delta, but leaves the failing hook (Q-3).

**Not no-ops (they change a gate's outcome or touch code → need an explicit decision / a different change type):**
- **Add a complexipy CI job at 30** → red on day one (47 under both engines; 38 under 8.0.1). Requires a threshold ≥ 47, a `src/`-only scope, or exemptions.
- **Fix `is_valid_value` (47) / `test_inv_003_last_admin_invariant` (38)** → `src/` + `tests/` restructuring → **REFACTOR change**, out of scope here (Q-3 option c).
- **Align the complexipy pins** (Q-2) → changes which functions the hook flags (20 → 38 flips a PASSED to a FAILED), i.e. it changes a gate's outcome even though the edit is one line.
- **Select `DTZ`** → 1 violation at `tests/tooling_test_helpers.py:53`; enabling it alone turns `lint.yml` red. Safe only together with the one-line tz fix + a full-suite run.
- **Declare `py-webauthn`** (Q-4 a/b) → changes the install contract and `uv.lock`; option (b) additionally contradicts `docs/specs/authentication.md:21` → **Spec Amendment PR** required.
- **Enable `disallow_untyped_defs` / `warn_return-any`** (Q-8 b) → 8 / 20 `src/` errors → REFACTOR-sized, not a chore.
- **Docs-group split** (Q-7) → 11 CI lines + hook + README; a missed line breaks the `docs` job. Recommend dropping.
- **Select `D`** (Q-9) → 379 errors → not a chore.

## Late questions (Phases 2–6)

<none yet — DOCS/CHORE runs no Phase 1–2; append here if a later step needs input>
