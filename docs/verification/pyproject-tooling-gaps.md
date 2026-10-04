# Verification: pyproject-tooling-gaps (REFACTOR)

## Classification

- **Type:** **REFACTOR** (reclassified from DOCS/CHORE at P.3, 2026-10-04).
- **Rationale:** Q-1 folds a complexity refactor of **10 functions in `src/` and `tests/`** into this change, and Q-8 enables mypy `disallow_untyped_defs` and fixes **8 untyped defs in 6 `src/` files**. Both restructure existing code **without altering externally observable behavior** — the REFACTOR criterion (AGENTS.md Change Types, #4). The remaining items (complexipy CI job, hook removal, dependency declaration, ruff `DTZ`, `quality_check`, docs-group split) are config/CI/dependency changes that ride along. Not CROSS-CUTTING: no new shared capability, no architecture element, no shared feature-infrastructure — a complexity/type gate is tooling, and the four touched features (`permissions`, `search`, `sessionmanagement`, `settings`) each get a purely local restructuring with no interface, model or cross-feature change.

### Reclassification record (Escalation Rules)

| Field | Value |
|---|---|
| Original type | **DOCS/CHORE** (framed at P.1, 2026-10-03 — config/comments/CI only) |
| Reclassified to | **REFACTOR** |
| When | **P.3 Answer, 2026-10-04** (round 2 + round 3 answers), recorded here at **P.4** |
| Trigger | **Q-1** — the user chose "new complexipy CI job at the default threshold **15**" and, after being shown that 15 is red on 10 functions, chose to **refactor the 10 first, inside this change** (the snapshot ratchet and a 47 threshold were both offered and rejected). **Q-8** — enable `disallow_untyped_defs` and fix the 8 errors. Both edit `src/` and `tests/` bodies. |
| Why REFACTOR and not DOCS/CHORE | The TODO's own escalation trigger says: *"if any item changes externally observable behavior (e.g. … a refactor forced by a complexity gate), reclassify per the Escalation Rules."* The restructuring does **not** change observable behavior, so the REFACTOR row (not FEATURE/ISSUE) applies. |
| Consequences (binding for Phases 4–6) | (1) a **GREEN baseline of the full suite is required before any restructuring** — recorded below; (2) **full regression at Phase 5** (S5.1) — the suite result MUST be identical to the baseline; (3) **no test may be modified, weakened or deleted** — the existing tests are the contract; (4) **no version bump** (AGENTS.md Versioning: REFACTOR → none); (5) Phase 1 (no spec) and Phase 2 (no task DAG) stay skipped — the refactor scope below is the plan; (6) branch type changed `chore/` → **`refactor/`** (the branch was created fresh at P.4 with the new prefix, so no `git branch -m` was needed). |

## Baseline (REFACTOR entry gate — GREEN, measured before any restructuring)

- **Worktree:** `C:/workspace/active-projects/python-template_kopie-worktrees/refactor/pyproject-tooling-gaps`
- **Branch:** `refactor/pyproject-tooling-gaps`
- **Measured at commit:** `5c589d2c29774b228fb8c1618f4e64babb073c85` (`main` @ 2026-10-04, *"chore(structlog-logging): status WAITING (PR #67 approval PR open) + S1.4 recorded"*) — the worktree base commit.
- **Date:** 2026-10-04.

### Full suite (`uv run pytest tests/ -q`)

| Run | Result | Duration | Note |
|---|---|---|---|
| 1 | **2 failed, 726 passed, 1 skipped** | 234.25 s | Failures: `tests/property/authentication/test_tokens.py::test_inv_001_token_hash_uniqueness`, `tests/property/usermanagement/test_usermanagement_properties.py::test_inv_006_event_correspondence` |
| 2 (**authoritative baseline**) | **728 passed, 1 skipped, 0 failed** | **223.21 s (0:03:43)** | GREEN |

- **Flaky-failure classification (Run 1, NOT a defect and not fixed here):** both Run-1 nodes pass in isolation (`uv run pytest tests/property/authentication/test_tokens.py::test_inv_001_token_hash_uniqueness tests/property/usermanagement/test_usermanagement_properties.py::test_inv_006_event_correspondence -q -p no:randomly` → **2 passed in 3.07 s**) and pass in the full-suite Run 2 with no source or test change. This is the **documented pre-existing flaky class** of Hypothesis property tests under full-suite load on this Windows host (`hypothesis.errors.DeadlineExceeded` / `FlakyFailure`, random-example discovery order): see `docs/workflow/PROBLEMS.md`, `docs/verification/dependency-updates.md` (Runs 1/3, "pre-existing flaky Hypothesis-deadline failures … environmental noise, not behavior"), `docs/verification/settings-test-isolation.md`, `docs/verification/search.md`, `docs/verification/workflow-optimization.md`. Neither test file is in this change's scope.
- **Skip (1, pre-existing, host-dependent):** `tests/acceptance/filemanagement/test_filemanagement.py:364` — *"symlinks not available on this host"*. Not related to this change; it stays skipped on this host.
- **Baseline gate: GREEN — REFACTOR may proceed.** The Phase 5 invariant is **728 passed, 1 skipped, 0 failed** (modulo the documented flaky class, which must be classified the same way: passes in isolation, no source/test relation to this change).

### Targeted regression set for the refactor (Phase 4 `green_command` basis)

`uv run pytest tests/{acceptance,contract,property,unit,integration}/<feature>` for the four touched `src/` features plus the touched test areas:

```
uv run pytest tests/acceptance/permissions tests/contract/permissions tests/property/permissions \
  tests/unit/permissions tests/integration/permissions tests/acceptance/search tests/contract/search \
  tests/property/search tests/unit/search tests/acceptance/sessionmanagement tests/contract/sessionmanagement \
  tests/property/sessionmanagement tests/unit/sessionmanagement tests/integration/sessionmanagement \
  tests/acceptance/settings tests/contract/settings tests/property/settings tests/unit/settings \
  tests/acceptance/mail tests/unit/mail tests/property/mail tests/integration/mail \
  tests/mail_test_helpers.py tests/property/usermanagement -q
```

Baseline: **348 passed, 0 failed in 138.78 s**. Phase 4 runs this targeted set (AGENTS.md "Targeted GREEN"); the full suite is the Phase 5 gate.

### Other baseline evidence (all measured at `5c589d2`)

| Gate | Command | Result |
|---|---|---|
| Lint (whole repo, == CI `lint.yml:37`) | `uv run ruff check .` | **All checks passed!** |
| Format (== CI `lint.yml:39`) | `uv run ruff format --check .` | **324 files already formatted** |
| Types (== CI `quality.yml:23`) | `uv run mypy src/` | **Success: no issues found in 83 source files** |
| Dependencies (== CI `quality.yml:94`) | `uv run deptry .` | **Success! No dependency issues found.** (Scanning 89 files) |
| Complexity at the **configured 30** | `uv run complexipy src tests` | **exit 1** — 2 FAILED: `is_valid_value` **47**, `test_inv_003_last_admin_invariant` **38** (the reason the pre-commit hook fails on `main` today) |
| Complexity at the **target 15** | `uv run complexipy src tests --max-complexity-allowed 15` | **exit 1** — **10 FAILED** (full list in the refactor scope below) |
| Traceability (== CI `spec-validation.yml:68`) | `uv run python scripts/check_traceability.py` | **PASS (747 matrix rows, 129 spec IDs, 714 test functions)** |
| complexipy engine | `uv run complexipy --version` | **complexipy 8.0.1** (the dev pin `complexipy>=8.0.1`, `pyproject.toml:36`) |

### Baseline working-tree note (`uv.lock`)

`uv run …` in the fresh worktree re-locked `uv.lock`: a **one-line** diff, `[[package]] name = "python-template"` `version = "0.6.0"` → `"0.6.1"` — the pre-existing lock drift recorded as **P-42** (`pyproject.toml:4` already says `0.6.1`). Handled in "Sequencing and collision notes (d)". The line was reverted before the P.4 commit so that commit is a docs-only diff; note that **every `uv run` re-dirties `uv.lock` with this line** until it is committed (measured at P.4: it reappeared after `uv run ruff check .`), so a dirty `uv.lock` in this worktree is expected and is not a change artifact.

## Refactor scope (exact targets, measured numbers as of `5c589d2`)

Eight in-scope items, each decided at P.3 (Q-1 … Q-8). Items 1 and 8 are the code restructuring that makes this a REFACTOR; items 2–7 are the config/CI/dependency edits that ride along.

### 1. complexipy becomes a real CI gate at threshold **15** (Q-1) — and the 10 offenders are refactored first

- `pyproject.toml:92-94` `[tool.complexipy]`: `max-complexity-allowed = 30` → **`15`**; `paths = ["src", "tests"]` (`:93`) stays (it becomes live config once CI runs `uv run complexipy` instead of the hook passing filenames).
- `.github/workflows/quality.yml`: add a **new job block appended after the existing jobs** (after `migrations`, `quality.yml:111-127`) — never by editing an existing job's step list (Q-10, keeps the diff disjoint from `python-3.15-upgrade`). The job mirrors the existing job shape: `Setup uv` (`astral-sh/setup-uv@v7`) → `Setup Python` (`3.14`) → `uv sync --only-group dev` → `uv run complexipy src tests --max-complexity-allowed 15` (gate).
- **Refactor target list** — re-measured at `5c589d2`: `uv run complexipy src tests --max-complexity-allowed 15` → **exit 1**, exactly these **10** functions (scores under the single engine, complexipy **8.0.1**):

| # | File | Function | Score | Must reach |
|---|---|---|---|---|
| 1 | `src/backend/permissions/service.py` | `PermissionService::_check` | **17** | ≤ 15 |
| 2 | `src/backend/search/service.py` | `SearchService::search` | **17** | ≤ 15 |
| 3 | `src/backend/sessionmanagement/service.py` | `SessionService::list_sessions` | **18** | ≤ 15 |
| 4 | `src/backend/settings/models.py` | `SettingDefinition::_validate` | **26** | ≤ 15 |
| 5 | `src/backend/settings/models.py` | `is_valid_value` | **47** | ≤ 15 |
| 6 | `tests/integration/sessionmanagement/test_concurrency.py` | `test_nfr_005_concurrent_threads_safe` | **18** | ≤ 15 |
| 7 | `tests/mail_test_helpers.py` | `FakeSmtpServer::_dialogue` | **17** | ≤ 15 |
| 8 | `tests/property/usermanagement/test_multi_role_invariants.py` | `test_last_admin_invariant` | **23** | ≤ 15 |
| 9 | `tests/property/usermanagement/test_usermanagement_properties.py` | `test_inv_006_event_correspondence` | **22** | ≤ 15 |
| 10 | `tests/property/usermanagement/test_usermanagement_properties.py` | `test_inv_003_last_admin_invariant` | **38** | ≤ 15 |

- **Invariant for these 10:** each is restructured (extract helper, early return, table/lookup, split branch) so its **behavior and its tests are unchanged** — for the 5 `src/` functions the feature's existing tests (`tests/*/{permissions,search,sessionmanagement,settings}`) stay byte-identical and keep passing; for the 5 test/helper bodies the **assertions, strategies, `@given` parameters and event/record checks stay semantically identical** — only the body shape changes (AGENTS.md: "Do not modify, weaken, or delete any test"; extracting a helper out of a test body is allowed only if the test still asserts exactly the same thing). The ruff `# noqa: PLR0911, PLR0912` suppressions at `src/backend/settings/models.py:69` and `:230` and at `permissions/service.py:344` stay unless the refactor makes them unnecessary; removing a now-unneeded `noqa` is a ruff requirement, not a behavior change.
- Gate after the refactor: `uv run complexipy src tests --max-complexity-allowed 15` → **exit 0**.

### 2. Remove the complexipy pre-commit hook (Q-3)

- Delete `.pre-commit-config.yaml:23-26` (`repo: https://github.com/rohaquinlop/complexipy-pre-commit`, `rev: v5.1.0`, `hooks: - id: complexipy`). It is redundant once CI gates complexity, and it **fails on `main` today** (`is_valid_value` 47 > 30), which is why commits touching `src/backend/settings/models.py` currently need `--no-verify`.

### 3. One complexipy engine (Q-2)

- The dev pin `complexipy>=8.0.1` (`pyproject.toml:36`) is the only pin; no downgrade to the hook's pre-rewrite 5.1.0 (which scores `test_inv_003_last_admin_invariant` 20 vs 38). Removing the hook (item 2) removes the second engine.

### 4. Declare `py-webauthn>=2.0.0` (Q-4)

- Add `"py-webauthn>=2.0.0"` to `[project.dependencies]` (`pyproject.toml:8-25`) — this **declares** a dependency the approved spec (`docs/specs/authentication.md:21`) and `docs/decisions/ADR-031-py-webauthn-provider.md:48` already require; it is **not** a new dependency and needs **no Spec Amendment**.
- Drop the suppressions it lived behind: deptry `DEP001 = ["webauthn"]` (`pyproject.toml:123`) **and its comment** (`:120-122`), and ty `allowed-unresolved-imports = ["webauthn"]` (`pyproject.toml:155`) **and its comment** (`:151-154`, which is the mypy-equivalence note — keep the note that `check_untyped_defs` has no ty equivalent, `:156-157`).
- `uv.lock` changes (webauthn and its transitive packages). Verify after: `uv run deptry .` clean (no `DEP002` entry needed for `py-webauthn` — it is imported in `src/backend/authentication/webauthn.py`), `uv run mypy src/` clean, `uv run ty check src/` clean, and the full suite still green (the deferred import in `src/backend/authentication/webauthn.py:21-27` keeps working; the `InvalidPasskeyResponseError("py-webauthn is required …")` branch stays in place as the fallback).

### 5. Ruff `DTZ` selected + the one fix (Q-5)

- Add `"DTZ"` to `[tool.ruff.lint] select` (`pyproject.toml:175-187`).
- Fix `tests/tooling_test_helpers.py:53`: `yield datetime.now()` → aware (`datetime.now(UTC)`; `from datetime import UTC, datetime`). Measured: `uv run ruff check --select DTZ .` → **1 error** (`DTZ005` at that exact line); `src/` is clean.
- The value the shared `travel()` helper yields changes from naive to aware, which **would be observable to its users** — measured at `5c589d2`, however, **no test imports `tests/tooling_test_helpers.py` today** (`grep -rn "tooling_test_helpers|model_factory|mock_http|travel(" tests/` matches only the helper file itself), so the change is not observable to the current suite. The full-suite run is the confirmation, not a suspicion. No `noqa`, no per-file ignore.

### 6. `[tool.agent-runner] quality_check` → Phase 5 parity (Q-6)

- `pyproject.toml:214`: `"uv run ruff check src/ && uv run mypy src/"` → `"uv run ruff check . && uv run ruff format --check . && uv run mypy src/ && uv run deptry ."`. Free today (both lint commands and deptry are clean at the baseline). complexipy stays **out** of the task loop (it is a CI gate, not a per-task gate); `pip-audit`, `mkdocs`, `alembic` and the coverage gate stay CI-only.

### 7. Docs dependency-group split (Q-7)

- Move `"mkdocs>=1.6"` (`pyproject.toml:42`), `"mkdocs-material>=9.5"` (`:44`), `"mkdocstrings[python]>=1.0.6"` (`:46`) — with their comments (`:41`, `:43`, `:45`) — out of `dev` into a new `docs` dependency group.
- Update **all 11** `uv sync --only-group dev` lines (re-measured at `5c589d2`, exactly 11): `.github/workflows/quality.yml:21,39,56,77,92,107,122` (7), `.github/workflows/spec-validation.yml:37,66,80` (3), `.github/workflows/lint.yml:35` (1). Only the `docs` job (`quality.yml:96-109`, sync at `:107`) needs the docs group: `uv sync --only-group dev --group docs` (or `uv sync --group docs`); the other 10 stay `--only-group dev`.
- The `mkdocs-build` **pre-push** hook (`.pre-commit-config.yaml:37-43`): its `entry: uv run mkdocs build --strict` (`:39`) must become `uv run --group docs mkdocs build --strict`, otherwise it breaks after the split (mkdocs is no longer in the default group).
- `README.md:5-9` quickstart: `uv sync` still installs `dev` (`[tool.uv] default-groups = ["dev"]`, `pyproject.toml:75-77` stays), so the edit is a **note** that building the docs site needs `uv sync --group docs` — see the collision note (b) for how Phase 4 sequences it against PR #66.
- Verify: `uv sync --group docs && uv run mkdocs build --strict` in the worktree, `uv run deptry .` still clean (the `DEP002` entries `"mkdocs", "mkdocs-material", "mkdocstrings"` at `pyproject.toml:116` stay — they are still never imported from source), and `uv run pre-commit run --all-files` still passes.

### 8. mypy `disallow_untyped_defs` enabled + the 8 fixes (Q-8)

- Add `disallow_untyped_defs = true` to `[tool.mypy]` (`pyproject.toml:131-138`), with a one-line comment recording the two measured numbers: `warn-return-any` = **20 errors in 12 files** → deliberately **not** enabled.
- Re-measured at `5c589d2`: `uv run mypy src/ --disallow-untyped-defs` → **8 errors in 6 files** — the exact fix list:

| File | Line | Error |
|---|---|---|
| `src/main.py` | 112 | missing return type annotation `[no-untyped-def]` |
| `src/main.py` | 125 | missing return type annotation `[no-untyped-def]` |
| `src/backend/authentication/webauthn.py` | 21 | missing return type annotation `[no-untyped-def]` |
| `src/backend/authentication/service.py` | 162 | missing return type annotation `[no-untyped-def]` |
| `src/backend/usermanagement/models.py` | 38 | missing type annotation `[no-untyped-def]` |
| `src/backend/usermanagement/models.py` | 43 | missing type annotation `[no-untyped-def]` |
| `src/backend/permissions/repositories.py` | 50 | missing return type annotation `[no-untyped-def]` |
| `src/backend/authentication/repository.py` | 37 | missing return type annotation `[no-untyped-def]` |

- The fixes are **annotations only** (add parameter/return annotations; no logic change). Gate: `uv run mypy src/` → clean, and `uv run ty check src/` (`quality.yml:25`, informational) still clean.

## Invariants that MUST hold

1. **No externally observable behavior change.** No new behavior, no removed behavior, no changed interface, model, event, error type or signature semantics. The `src/` edits are complexity restructuring and type annotations only.
2. **The full suite result is identical to the baseline:** `uv run pytest tests/ -q` → **728 passed, 1 skipped, 0 failed** (the 1 skip is the pre-existing `tests/acceptance/filemanagement/test_filemanagement.py:364` symlink-host skip). The documented pre-existing Hypothesis flakiness (see the baseline table) may recur and is classified as environmental noise only if the node passes in isolation and is unrelated to the files this change touches.
3. **No test is modified, weakened or deleted.** Test bodies may only be restructured for complexity (item 1, rows 6–10) while asserting exactly the same thing: same `@given` strategies and settings, same assertions, same event/record comparisons, same expected exceptions. Any assertion change is a violation and MUST stop the step (AGENTS.md Agent Prohibitions).
4. **Every gate stays green at every step:** `uv run ruff check .` (whole repo, == CI `lint.yml:37`), `uv run ruff format --check .`, `uv run mypy src/`, `uv run ty check src/`, `uv run deptry .`, `uv run python scripts/check_traceability.py`, `uv run mkdocs build --strict`, `uv run alembic upgrade head`, and — after item 1/2 land — `uv run complexipy src tests --max-complexity-allowed 15` → exit 0.
5. **A new CI gate must pass on day one:** the complexipy job is added to `quality.yml` only after the 10 functions are under 15 in the same branch.
6. **Feature boundaries respected:** each of the four touched features keeps its code inside its own feature directory; no cross-feature internal import is introduced by the extracted helpers.

## Out of scope (copied from `docs/todo/pyproject-tooling-gaps.md`)

- Raising `fail_under` above 92, or changing what coverage measures.
- Adding `--cov` to `[tool.pytest.ini_options] addopts` — **explicitly not recommended**: CI already passes `--cov` explicitly, and putting it in `addopts` slows every targeted per-task `red_command`/`green_command` run (Phase 4 runs targeted tests, not the suite) and every `pytest -x` loop. The floor is not decorative; it is CI-enforced.
- Ruff `D1xx` backfill of the undocumented public defs (the TODO's original count was 156; see the next row for the measured cost). The backfill itself is a separate change either way.
- ~~Any dependency addition (see `docs/todo/tenacity-rich-cachetools.md`).~~ → superseded by Q-4 (declare `py-webauthn`, which the approved spec already requires); the *new*-dependency prohibition stands.
- ~~Any source refactor forced by a lowered complexity threshold — that is a REFACTOR change, not this one.~~ → **superseded by Q-1**: the user folded the 10-function refactor into this change, which is what reclassified it to REFACTOR.
- Ruff `D` (pydocstyle) — **Q-9: stays out of `select`**; the backfill is its own backlog item, **`docs/todo/ruff-d-docstrings.md`** (framed 2026-10-04; measured cost **379 errors**, re-confirmed at `5c589d2`: `uv run ruff check --select D src` → **379 errors**).
- Enabling `warn-return-any` (**20 errors in 12 files**, re-confirmed at `5c589d2`) — recorded with the number in the `[tool.mypy]` comment, not enabled.

## Version bump

**None.** AGENTS.md Versioning: REFACTOR → no bump. `pyproject.toml:4` `version = "0.6.1"` and `[tool.bumpversion] current_version = "0.6.1"` (`:80`) stay unchanged; `bump-my-version` is not run in this change.

## Sequencing and collision notes

**(a) This change is the predecessor.** `structlog-logging` (approval PR **#67**) and `python-3.15-upgrade` (`docs/todo/python-3.15-upgrade.md`, `Status: PREPARING`, trigger-gated on 3.15 final + a pydantic cp315 wheel) **rebase on this change**, not the reverse (Q-10). The complexipy job is added as a **new job block appended after the existing jobs** in `quality.yml`, never by editing an existing job's step list, so `python-3.15-upgrade`'s 11 `python-version` pins and this change's sync-line edits stay disjoint.

**(b) `README.md` collision (the sharp one).** Open PR **#66** (`chore/update-readme`) **rewrites `README.md` entirely** — verified: +562 / −20, and its new `## Installation` section preserves the old `## Setup` `uv sync` block while its `## Development` section carries a verified command table whose `uv sync` row cites `[tool.uv] default-groups = ["dev"]` (`pyproject.toml:75-77`). This change edits the same quickstart (`README.md:5-9`) for the docs-group split. **Phase 4 handling:** the README edit is the **last** sub-step of item 7, and it is one note, not a rewrite — *"building the docs site needs `uv sync --group docs`"*. If #66 has merged when Phase 4 reaches it, rebase this branch on `main` first and attach the note to the post-#66 text (the `## Installation` block and the `## Development` command table row for `uv run mkdocs build --strict`). If #66 is still open, edit the current `README.md:5-9` and record in the PR body that a `README.md` rebase conflict is expected; resolve it by **re-applying this change's one-line note to the post-#66 text** — never by dropping the note and never by adopting or re-resolving #66's README content, which belongs to that change. `default-groups = ["dev"]` is unchanged, so `uv sync` keeps working as both READMEs describe it.

**(c) `docs/workflow/PROBLEMS.md` is append-only** and PRs **#65** (`architecture-tests-missing`), **#66** (`update-readme`) and **#67** (`structlog-logging`) each append to it (verified via `gh pr view --json files`). If a merge conflict appears, resolve it as a **union of the appended entries** — keep every entry, append this change's entries at the end, never reorder or renumber an existing entry.

**(d) `uv.lock` and the pre-existing lock drift (P-42).** Declaring `py-webauthn>=2.0.0` (item 4) necessarily re-locks `uv.lock`. Independently, the baseline worktree already shows a **one-line** lock diff from the pre-existing drift recorded as **P-42**: `[[package]] name = "python-template"` `version = "0.6.0"` → `"0.6.1"` (the lock lagged `pyproject.toml:4`). **Decision: this change commits the re-locked file, including that one line** (in item 6's commit — the P.4 baseline commit contains only this record; the drift line was `git checkout -- uv.lock`-reverted here so the baseline commit stays a docs-only diff). Reason: `uv lock` regenerates the whole file, so the project-version line cannot be excluded without hand-editing the lock — and a hand-edited lock that does not match its own `pyproject.toml` is exactly the P-42 defect this change would be re-introducing; the next `uv run` would flip it back anyway. The line is lock **metadata**, not a behavior or version change: the project version stays `0.6.1` and no `bump-my-version` run happens (REFACTOR → no bump). The PR body MUST call the line out explicitly so the reviewer sees one unrelated, pre-existing correction rather than an unexplained version change.

## Phase 4 step order (small, behavior-preserving steps)

1. Refactor the 5 `src/` offenders (`is_valid_value` 47 → `SettingDefinition::_validate` 26 → `list_sessions` 18 → `_check` 17 / `search` 17) — targeted tests + ruff per step.
2. Refactor the 5 `tests/` offenders (same order of size) — targeted set + ruff; assertions untouched.
3. `uv run complexipy src tests --max-complexity-allowed 15` → exit 0; then flip `max-complexity-allowed` to 15, append the new `quality.yml` job block, delete the pre-commit hook (`:23-26`).
4. `DTZ` in `select` + `tests/tooling_test_helpers.py:53` aware `datetime.now(UTC)`; the helper has no importer today, but the full suite is re-run for this step because the shared `travel()` value is observable to any future importer.
5. mypy `disallow_untyped_defs = true` + the 8 annotation fixes; `uv run mypy src/` clean.
6. Declare `py-webauthn>=2.0.0`, drop `DEP001` + ty suppressions and their comments, `uv lock`; deptry / ty / mypy / suite re-checked.
7. `quality_check` string (item 6).
8. Docs-group split: `pyproject.toml` group move → the 11 sync lines → the `mkdocs-build` hook entry → `mkdocs build --strict` + `pre-commit run --all-files` → **README note last** (collision (b)).

## Next

Phase 4 (REFACTOR): small behavior-preserving steps per the order above, full suite re-run after every step (AGENTS.md Phase 4 REFACTOR: "Re-run the full suite after every step; it MUST stay GREEN"), no test modified/weakened/deleted, then Phase 5 (full regression + lint + types, no spec coverage) and Phase 6 (review, **no version bump**, PR to `main`).

