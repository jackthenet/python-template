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

- The fixes are **annotations only** (add parameter/return annotations; no logic change). Gate: `uv run mypy src/` → clean, and `uv run ty check src/` (`quality.yml:25`, informational) shows **no new diagnostics** relative to the 151-diagnostic baseline (see invariant 4's correction — `ty` is not a clean gate).

## Invariants that MUST hold

1. **No externally observable behavior change.** No new behavior, no removed behavior, no changed interface, model, event, error type or signature semantics. The `src/` edits are complexity restructuring and type annotations only.
2. **The full suite result is identical to the baseline:** `uv run pytest tests/ -q` → **728 passed, 1 skipped, 0 failed** (the 1 skip is the pre-existing `tests/acceptance/filemanagement/test_filemanagement.py:364` symlink-host skip). The documented pre-existing Hypothesis flakiness (see the baseline table) may recur and is classified as environmental noise only if the node passes in isolation and is unrelated to the files this change touches.
3. **No test is modified, weakened or deleted.** Test bodies may only be restructured for complexity (item 1, rows 6–10) while asserting exactly the same thing: same `@given` strategies and settings, same assertions, same event/record comparisons, same expected exceptions. Any assertion change is a violation and MUST stop the step (AGENTS.md Agent Prohibitions).
4. **Every gate stays green at every step:** `uv run ruff check .` (whole repo, == CI `lint.yml:37`), `uv run ruff format --check .`, `uv run mypy src/`, `uv run deptry .`, `uv run python scripts/check_traceability.py`, `uv run mkdocs build --strict`, `uv run alembic upgrade head`, and — after item 1/2 land — `uv run complexipy src tests --max-complexity-allowed 15` → exit 0.
   **Correction to this invariant (recorded at Phase 4 step 2, 2026-10-04): `uv run ty check src/` is NOT a "stays green" gate.** It is **red at the baseline**: **151 diagnostics** at `5c589d2` and still **151** after Phase 4 steps 1–2 (`95 error[invalid-type-form]`, `23 error[unresolved-attribute]`, `18 warning[unsupported-base]`, `5 invalid-argument-type`, `3 invalid-return-type`, `3 call-non-callable`, `2 missing-argument`, `1 invalid-base`, `1 warning[deprecated]`) — e.g. `invalid-type-form` on `src/backend/authentication/feature_actions.py:20` and `unsupported-base` on `src/backend/authentication/repository.py:63`, caused by the `@logged`/`@logged_class` decorators and the SQLModel table bases, all in files this change does not touch. `ty` is **informational** in CI (`quality.yml:25`, `continue-on-error: true`); **`mypy` is the gate** (`quality.yml:23`) and is clean at every step (**Success: no issues found in 83 source files**). The ty requirement for this change is therefore **"no new diagnostics relative to the 151-diagnostic baseline"**, not "clean" — Phase 5 MUST NOT record the 151 as a regression. (Item 8's "`uv run ty check src/` … still clean" is to be read the same way: no new diagnostics.)
   **Amendment to this invariant (recorded at Phase 4 step 5, 2026-10-04): the requirement is "no new `ty` diagnostics except the SQLModel-table-class class introduced by precise annotations"; exact counts recorded (baseline 151, after S4.5 152, after S4.6 152).** The single accepted addition is `error[invalid-argument-type]` at `src/backend/authentication/service.py:221` (`Expected UserRead, found User`), introduced by the precise `-> User | None` on `AuthService._user_by_identifier`, which is **kept**: mypy types SQLModel table classes as `Any`, so the annotation buys the CI gate nothing, while `ty` types them as real classes and therefore reports the `User`/`UserRead` mismatch that an untyped (`Any`) return hid. `ty` is informational (`quality.yml:25`, `continue-on-error: true`), `mypy` is the gate (`quality.yml:23`) and stays clean. Honest evidence beats a gate that cannot hold: Phase 5 MUST NOT record 151 or 152 as a regression, and MUST NOT be told the count is unchanged.
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


## Phase 4 progress — step 1 (src/ complexity)

**Step:** S4.1 (Phase 4 step order item 1) — refactor the 5 `src/` complexipy offenders. **Type:** REFACTOR. **Date:** 2026-10-04. **Engine:** complexipy 8.0.1, gate `uv run complexipy src tests --max-complexity-allowed 15`.

Re-measured before touching anything: the offender list is **exactly** the 10 rows of the scope table (5 `src/`, 5 `tests/`), scores unchanged.

### Per-function before → after

| # | File | Function | Before | After | Restructuring (behavior-preserving) |
|---|---|---|---|---|---|
| 1 | `src/backend/settings/models.py` | `is_valid_value` | **47** | **8** | Extracted the per-kind rules into five private module-level helpers (`_text_value_valid`, `_number_value_valid`, `_slider_value_valid`, `_select_value_valid`, `_list_value_valid`); `is_valid_value` keeps its exact signature and is now a flat kind-dispatch. `# noqa: PLR0911, PLR0912` → `# noqa: PLR0911` (PLR0912 no longer fires; RUF100 confirms PLR0911 still does). New helpers: 2/3/3/4/6/10. |
| 2 | `src/backend/settings/models.py` | `SettingDefinition::_validate` | **26** | **2** | Extracted `_validate_kind_specs` (12), `_validate_no_kind_specs` (3) and `_validate_kind_exclusive_constraints` (6) as private methods; the if/elif/elif/else shape and every exception message are unchanged. `# noqa: PLR0912` removed (no longer fires). |
| 3 | `src/backend/sessionmanagement/service.py` | `SessionService::list_sessions` | **18** | **12** | Extracted `_listed_limit` (1) and `_order_with_current` (5). The single `now` snapshot (INV-002) and the token-path validity check stay inline — `_resolve_token` is **not** reused because it re-reads the clock. |
| 4 | `src/backend/permissions/service.py` | `PermissionService::_check` | **17** | **10** | Extracted the grant-evaluation tail into `_evaluate_grants` (7); the step order (shape → principal → session → catalog → grants) and the closed reason set are unchanged. `# noqa: PLR0911` **stays** (7 early returns > 6). |
| 5 | `src/backend/search/service.py` | `SearchService::search` | **17** | **13** | Extracted the locked source selection into `_select_sources` (3); the `RLock` scope, the `UnknownSourceError` path and the fan-out/resilient-failure handling are unchanged. |

All five are ≤ 15. No public signature, return value, exception type/message, log record or event changed; no test file was touched (rows 6–10 are step 2); no new dependency, no new public API, every extracted helper is private and inside its own feature directory (invariant 6).

### Remaining offender list after step 1

`uv run complexipy src tests --max-complexity-allowed 15` → exit 1, exactly the 5 `tests/` rows of the scope table (6–10): `test_nfr_005_concurrent_threads_safe` **18**, `FakeSmtpServer::_dialogue` **17**, `test_last_admin_invariant` **23**, `test_inv_006_event_correspondence` **22**, `test_inv_003_last_admin_invariant` **38**. No `src/` offender remains.

### Gates after each refactor

| After | Full suite (`uv run pytest tests/ -q`) | ruff (changed path) | ruff format --check | mypy src/ |
|---|---|---|---|---|
| `is_valid_value` | **728 passed, 1 skipped** (221.52 s) | All checks passed | already formatted | Success (83 files) |
| `SettingDefinition::_validate` | **728 passed, 1 skipped** (228.48 s) | All checks passed | already formatted | Success |
| `list_sessions` | **728 passed, 1 skipped** (221.20 s) | All checks passed | already formatted | Success |
| `_check` | run 1: **1 failed, 727 passed, 1 skipped** → run 2 (authoritative): **728 passed, 1 skipped** (222.51 s) | All checks passed | already formatted | Success |
| `search` | **728 passed, 1 skipped** (221.07 s) | All checks passed | already formatted | Success |

Targeted sets also run per step: settings **85 passed**, sessionmanagement **69 passed**, permissions **68 passed**, search **83 passed**.

**`_check` run-1 failure classification (NOT a regression, NOT caused by this change):** `tests/contract/search/test_search_contracts.py::test_nfr_001_performance_budgets` — a wall-clock budget (`statistics.median(15 × svc.search(...)) < 0.3 s` local / 0.6 s on CI). It **passes in isolation** (`1 passed in 8.23 s`), it is the **documented** load/hardware-sensitive node (`docs/verification/search.md:456` CI failure `assert 0.368 < 0.3`; `docs/workflow/PROBLEMS.md:330` records the ~293 ms measured median vs the 300 ms budget), and the step that was in flight touched only `src/backend/permissions/service.py` — the test's `SearchService` is built with `permission_service=None` (standalone mode, `tests/search_test_helpers.py:201`), so `PermissionService::_check` is not on the measured path at all. The immediate re-run is 728 passed.

### Commits (step 1)

| Commit | Message |
|---|---|
| `5b2b149` | `refactor(pyproject-tooling-gaps): S4.1 reduce complexity of is_valid_value (47 → 8)` |
| `c736105` | `refactor(pyproject-tooling-gaps): S4.1 reduce complexity of SettingDefinition::_validate (26 -> 2)` |
| `eae8fbd` | `refactor(pyproject-tooling-gaps): S4.1 reduce complexity of SessionService::list_sessions (18 -> 12)` |
| `5a430d2` | `refactor(pyproject-tooling-gaps): S4.1 reduce complexity of PermissionService::_check (17 -> 10)` |
| `12338c6` | `refactor(pyproject-tooling-gaps): S4.1 reduce complexity of SearchService::search (17 -> 13)` |

Diff stat `c0dd9ff..HEAD`: 4 files, +127 / −70 — `src/backend/permissions/service.py`, `src/backend/search/service.py`, `src/backend/sessionmanagement/service.py`, `src/backend/settings/models.py`. **No test file, no `pyproject.toml`, no workflow, no config touched** (steps 3–8). `uv.lock` was `git checkout --`-reverted before every commit (P-42 drift) and is not in any commit.

### Note for later steps: complexipy measures **cognitive** complexity

Measured empirically (nesting costs +1 per level, `else` costs nothing): the score is **not** Radon cyclomatic complexity, so a flat if-chain is much cheaper than a nested one — `if/elif/else` with nested bodies scored 16 where the same decisions flattened scored 4. Step 2 (the `tests/` offenders) should flatten nesting first, not just split `if`s.

### Gate note: `uv run ty check src/` is red at baseline (pre-existing, informational)

`uv run ty check src/` reports **151 diagnostics** (e.g. `error[invalid-type-form]` on `src/backend/authentication/feature_actions.py:20`, `warning[unsupported-base]` on `src/backend/authentication/repository.py:63`) — the `@logged`/`@logged_class` decorators and SQLModel bases are outside ty's model. None is in a file this step touched, and the P.4 baseline table records **no** clean `ty` result (only `uv run mypy src/` → Success, which is the CI gate at `quality.yml:23`; `ty` is the informational job at `quality.yml:25`). mypy stays clean (83 files) after every refactor in this step.

## Phase 4 progress — step 2 (tests/ complexity)

**Step:** S4.2 (Phase 4 step order item 2) — refactor the 5 `tests/` complexipy offenders to ≤ 15. **Type:** REFACTOR. **Date:** 2026-10-04. **Engine:** complexipy 8.0.1, gate `uv run complexipy src tests --max-complexity-allowed 15`.

Re-measured before touching anything: the offender list is **exactly** the 5 remaining `tests/` rows of the scope table (6–10), scores unchanged (`test_inv_003_last_admin_invariant` 38, `test_last_admin_invariant` 23, `test_inv_006_event_correspondence` 22, `test_nfr_005_concurrent_threads_safe` 18, `FakeSmtpServer::_dialogue` 17). No `src/` offender (step 1 done).

### Per-function before → after

| # | File | Function | Before | After | Restructuring (assertions unchanged) |
|---|---|---|---|---|---|
| 1 | `tests/property/usermanagement/test_usermanagement_properties.py` | `test_inv_003_last_admin_invariant` | **38** | **6** | Extracted three private module-level helpers: `_admin_users` (**2**), `_mutate_first_admin` (**3**) — the "first admin that accepts the mutation" loop, shared by the delete/deactivate ops — and `_apply_inv_003_op` (**4**), the four-op dispatch. The `nonlocal counter` closure became `itertools.count(start=1)`, advanced by `next()` at the same point in each branch, so the generated usernames/emails are the same strings in the same order. The `try/except … : pass` became `with contextlib.suppress(…)` (ruff `SIM105`; identical suppression). The invariant check (`admin_users` + `assert any(u.is_active …)`) stays **inline in the test**, byte-identical. |
| 2 | `tests/property/usermanagement/test_multi_role_invariants.py` | `test_last_admin_invariant` | **23** | **9** | Extracted `_apply_op` (**9**) — the five-branch dispatch (`create_admin` / `create_user` / `add_admin` / `_apply_admin_op`) that was inline in the loop; the pre-existing `_apply_admin_op` (**8**) is unchanged. Same `count(start=1)` substitution; same `contextlib.suppress` substitution. The initial-admin seeding line, the invariant comment and the inline `admin_users` / `assert any(u.is_active …)` check are unchanged. |
| 3 | `tests/property/usermanagement/test_usermanagement_properties.py` | `test_inv_006_event_correspondence` | **22** | **6** | Extracted `_apply_event_op` (**11**): the non-create branch chain now **returns the event type** the op must publish, or `None` for the two idempotent no-ops (REQ-009) and for an op the sequence does not perform — the same skip decision the two inner `continue`s and the `else: continue` made. The test keeps the create branch (with its `UserCreated` count assert) inline, calls the helper under `contextlib.suppress(LastAdminError, InvalidRoleError, UserNotFoundError)` with `ev = None` pre-set (an exception leaves `ev` `None` → the same `continue` the old `except … : continue` made), then runs the two original asserts. |
| 4 | `tests/integration/sessionmanagement/test_concurrency.py` | `test_nfr_005_concurrent_threads_safe` | **18** | **9** | The nested `worker(uid)` closure became the module-level `_nfr_005_worker(service, uid, rows, all_ids, errors)` (**5**) — the closure's captured variables are passed as arguments; `rows_by_user[uid]` is read on the submitting thread (the dict is never mutated after construction). Concurrency semantics identical: same `ThreadPoolExecutor(max_workers=8)`, same 4 submitted workers, same per-thread sequence (revoke own 10 → 5 × list-and-assert → `revoke_all_sessions` → `cleanup_expired`), same `errors` collection, same `future.result()` joins, same final per-user `list_sessions == []` asserts. |
| 5 | `tests/mail_test_helpers.py` | `FakeSmtpServer::_dialogue` | **17** | **5** | Test **helper**, not a test: the dialogue loop now reads one line and delegates (`_handle_command` **7**, `_handle_auth` **1**, `_handle_mail_from` **1**); the helper returns `False` where the old body `return`ed (QUIT, `auth_fail`, `protocol_fail`). Same `startswith` match order (EHLO, AUTH, MAIL FROM, RCPT TO, DATA, QUIT, else), same response bytes, same `_readline`/`_read_data`/`_send` socket handling, same `_serve`/`_hold`/`close`. Verified by an ordered inventory of every `startswith("…")` command and every `"NNN …\r\n"` response literal: **identical sequence** before/after. |

All five are ≤ 15. **Final gate: `uv run complexipy src tests --max-complexity-allowed 15` → exit 0 (zero offenders).** `pyproject.toml` `max-complexity-allowed` is still **30** and no `quality.yml` job exists yet — that is step 3, deliberately not done here.

### Invariant 3 holds: no assertion, strategy or `@settings` value changed

Per-commit `git diff | grep -cE "^[-+].*assert"` (changed lines containing an assertion):

| Commit | File | Assert lines changed |
|---|---|---|
| `d3ff1ab` | `test_usermanagement_properties.py` (inv_003) | **0** |
| `6db0d5f` | `test_multi_role_invariants.py` | **0** |
| `228a20a` | `test_usermanagement_properties.py` (inv_006) | **0** |
| `754bb6b` | `test_concurrency.py` | **2** — one line: `assert entry.session_id in all_ids` moved with the extracted worker (re-indented by 4); the diff pair is byte-identical modulo indentation |
| `34a6f7e` | `mail_test_helpers.py` | **0** (the file contains no assertion — it is a helper) |

Stronger, indentation-insensitive proof over all four files (`57d6c8e..HEAD`): the **assert inventory** — every line containing `assert`, whitespace-normalized, in order — is **identical** before/after for `test_usermanagement_properties.py`, `test_multi_role_invariants.py` and `test_concurrency.py` (`diff <(git show 57d6c8e:<f> | grep assert | sed 's/^ *//') <(grep assert <f>)` → empty). The **decorator/strategy inventory** — every line containing `@given`, `@settings`, `max_examples`, `deadline`, `sampled_from`, `min_size`, `max_size`, `HealthCheck` or `st.` — is likewise **identical** for all four files: no `@given` strategy, no `@settings` value (including the measured `deadline=1000`), no example count and no `suppress_health_check` changed; no `assume()` was added; no check was deleted or weakened. Diff stat `57d6c8e..HEAD`: **4 files, +171 / −128**, all under `tests/` — no `src/`, no `pyproject.toml`, no `.github/workflows/`, no `.pre-commit-config.yaml`.

### Gates after each refactor

| After | Full suite (`uv run pytest tests/ -q`) | Targeted set | ruff (changed path) | ruff format --check |
|---|---|---|---|---|
| `test_inv_003_last_admin_invariant` 38 → 6 | **728 passed, 1 skipped** (220.20 s) | usermanagement property+unit+acceptance **71 passed** | All checks passed | already formatted |
| `test_last_admin_invariant` 23 → 9 | **728 passed, 1 skipped** (225.03 s) | usermanagement property+unit+acceptance+contract **76 passed** | All checks passed | already formatted |
| `test_inv_006_event_correspondence` 22 → 6 | **728 passed, 1 skipped** (219.77 s) | usermanagement property **7 passed** | All checks passed | already formatted |
| `test_nfr_005_concurrent_threads_safe` 18 → 9 | **728 passed, 1 skipped** (220.79 s) | sessionmanagement integration+unit+contract+acceptance+property **69 passed** | All checks passed | 1 file reformatted (the `pool.submit(…)` list comprehension reflowed to one line, 120-char limit), then already formatted |
| `FakeSmtpServer::_dialogue` 17 → 5 | **728 passed, 1 skipped** (222.82 s) | mail unit+contract+acceptance+integration+property **40 passed** | All checks passed | already formatted |

Suite result identical to the baseline at every step (**728 passed, 1 skipped, 0 failed**; the 1 skip is the pre-existing symlink-host skip). The documented flaky wall-clock node `tests/contract/search/test_search_contracts.py::test_nfr_001_performance_budgets` did **not** recur in any of the five full-suite runs. Whole-repo sweep (extra evidence, the Phase 5 gate): `uv run ruff check .` → **All checks passed!**, `uv run ruff format --check .` → **324 files already formatted**, `uv run mypy src/` → **Success: no issues found in 83 source files**, `uv run ty check src/` → **151 diagnostics = the baseline count, no new diagnostics** (see the invariant-4 correction).

### Commits (step 2)

| Commit | Message |
|---|---|
| `d3ff1ab` | `refactor(pyproject-tooling-gaps): S4.2 reduce complexity of test_inv_003_last_admin_invariant (38 → 6)` |
| `6db0d5f` | `refactor(pyproject-tooling-gaps): S4.2 reduce complexity of test_last_admin_invariant (23 → 9)` |
| `228a20a` | `refactor(pyproject-tooling-gaps): S4.2 reduce complexity of test_inv_006_event_correspondence (22 → 6)` |
| `754bb6b` | `refactor(pyproject-tooling-gaps): S4.2 reduce complexity of test_nfr_005_concurrent_threads_safe (18 → 9)` |
| `34a6f7e` | `refactor(pyproject-tooling-gaps): S4.2 reduce complexity of FakeSmtpServer::_dialogue (17 → 5)` |

`uv.lock` was `git checkout --`-reverted before every commit (P-42 drift) and is in no commit.

### Friction (for the Problem Log)

1. **Helper inserted between a test's decorators and its `def`** (twice: `test_inv_003_last_admin_invariant`, `test_inv_006_event_correspondence`). Anchoring an insertion at the `def` line puts the new helper *after* the `@settings`/`@given` block, so the decorators land on the helper and pytest reports `fixture 'ops' not found` (an ERROR, not a failure). Caught by the targeted run both times, fixed by moving the helper above the decorator block; the decorator inventory proof confirms the decorators themselves are untouched. **Rule for later steps: insert extracted helpers above the decorator block, never at the `def` line.**
2. **ruff `SIM105` fires once a `try/except … : pass` is flattened** to a single statement (it did not fire on the original multi-branch bodies). The fix is `with contextlib.suppress(…)` — semantically identical, and it also removes the `try`/`except` from the cognitive score.
3. One `ruff format` reflow was required (`test_concurrency.py`) because the extracted call fits on one 120-char line.

The step-1 nesting lesson holds: flattening (early return, extracted helper, `if` instead of `if/elif` chains) is what moved these scores — e.g. `test_inv_003_last_admin_invariant` 38 → 6 by extracting the dispatch and the admin loop, not by splitting conditions.

## Phase 4 progress — steps 3–4 (complexipy CI gate at 15 + ruff `DTZ`)

**Steps:** Phase 4 step-order items 3 and 4 (scope items 1–3 and item 5). **Type:** REFACTOR. **Date:** 2026-10-04.

### Step 3 — complexipy becomes a real gate at 15 (scope items 1–3)

| Gate | Command / location | Result |
|---|---|---|
| Complexity at the new threshold | `uv run complexipy src tests --max-complexity-allowed 15` | **exit 0** — "All functions are within the allowed complexity." (zero offenders) |
| Config flip | `pyproject.toml` `[tool.complexipy]` | `max-complexity-allowed = 30` → **15**; `paths = ["src", "tests"]` unchanged (live config now that CI runs the command) |
| Hook removal (item 2) | `.pre-commit-config.yaml` | the 4-line `complexipy-pre-commit` (`rev: v5.1.0`, `id: complexipy`) block deleted; no other hook touched |
| One engine (item 3) | — | the dev pin `complexipy>=8.0.1` is now the only engine; the hook's pre-rewrite 5.1.0 is gone |
| New CI job | `.github/workflows/quality.yml` | **appended** `complexity` job after `migrations`; `git diff` shows **only** an added hunk (`@@ -125,3 +125,20 @@`) — no existing job block edited (collision note (a) respected). Shape mirrors the neighbours: `actions/checkout@v7` → `astral-sh/setup-uv@v7` → `actions/setup-python@v7` (`3.14`) → `uv sync --only-group dev` → `uv run complexipy src tests --max-complexity-allowed 15` |
| pre-commit, changed files | `uv run pre-commit run --files .github/workflows/quality.yml .pre-commit-config.yaml pyproject.toml` | **exit 0** — every hook passes with the complexipy hook removed (ruff hooks *Skipped*: no `.py` in the set) |
| Lint / format | `uv run ruff check .` / `uv run ruff format --check .` | **All checks passed!** / **324 files already formatted** |
| Full suite | `uv run pytest tests/ -q` | **728 passed, 1 skipped, 0 failed** (221.32 s) — identical to the baseline |

**Pre-existing `pre-commit run --all-files` failure found (not caused by this change, not fixed here).** The whole-tree run fails on `end-of-file-fixer` for **17 files** (`AGENTS.md`, `README.md`, `migrations/README`, `.github/CODEOWNERS.md`, `docs/tasks/README.md`, `docs/tasks/template.md`, `docs/tasks/settings.tasks.json`, `docs/verification/search.md`, `docs/verification/tooling-hardening.md`, `.agents/skills/python-best-practices/SKILL.md` + 7 `references/*.md`): their `HEAD` blobs have no final newline (`git show HEAD:migrations/README | tail -c 12` → `nfiguration.` with no `\n`) or carry trailing blank lines. Proof it predates this change: `git diff --name-only main...HEAD` lists 10 files and **none** of the 17 is among them, and `end-of-file-fixer` is untouched by this diff. The hook's modifications were reverted (`git checkout --`) — reformatting 17 unrelated files is out of this change's scope. The hook-removal gate is therefore evidenced by the scoped run above (exit 0 on the three changed files) plus the whole-tree run, in which the **only** failing hook is `end-of-file-fixer` (`trailing-whitespace`, `check-yaml`, `check-added-large-files`, `deptry` all pass). **Recommend a backlog TODO for the EOF backfill**: until it lands, `pre-commit run --all-files` is not usable as a whole-tree gate (relevant to step 8, whose verification list names that command).

### Step 4 — ruff `DTZ` selected + the one fix (scope item 5)

| Gate | Command / location | Result |
|---|---|---|
| Before the fix | `git show HEAD:tests/tooling_test_helpers.py \| uv run ruff check --select DTZ --stdin-filename tests/tooling_test_helpers.py -` | **exactly 1 error**: `DTZ005` at `tests/tooling_test_helpers.py:53` (`yield datetime.now()`) — matches the P.4 measurement |
| The fix | `tests/tooling_test_helpers.py` | `from datetime import UTC, datetime`; `yield datetime.now(UTC)`. **No `noqa`, no per-file ignore.** |
| After the fix | `uv run ruff check --select DTZ .` | **All checks passed!** (exit 0) |
| `select` | `pyproject.toml` `[tool.ruff.lint]` | `"DTZ", # flake8-datetimez: naive datetime objects are a bug` appended after `"C4"` |
| Lint / format / types | `uv run ruff check .` / `uv run ruff format --check .` / `uv run mypy src/` | **All checks passed!** / **324 files already formatted** / **Success: no issues found in 83 source files** |
| Full suite | `uv run pytest tests/ -q` | **728 passed, 1 skipped, 0 failed** (217.37 s) — identical to the baseline |
| Observability check | `grep -rn "tooling_test_helpers" tests/ src/` | **no importer** (only the helper file itself) — re-confirmed at this step, so the naive → aware value is not observable to the current suite; the full-suite run is the confirmation |

Invariant 3 holds: no test was modified, weakened or deleted — the only `tests/` edit is the shared `travel()` helper's yield (a helper with no importer, and the file contains no assertion).

### Commits (steps 3–4)

| Commit | Message | Files |
|---|---|---|
| `e9d0c57` | `refactor(pyproject-tooling-gaps): S4.3 complexipy CI gate at 15, drop the pre-commit hook` | `pyproject.toml`, `.pre-commit-config.yaml`, `.github/workflows/quality.yml` (+18 / −5) |
| `ff98a3a` | `refactor(pyproject-tooling-gaps): S4.4 select ruff DTZ, fix travel() naive datetime` | `pyproject.toml`, `tests/tooling_test_helpers.py` (+3 / −2) |

`uv.lock` was `git checkout --`-reverted before both commits (P-42 drift) and is in neither.

### Remaining Phase 4 steps

5. mypy `disallow_untyped_defs = true` + the 8 annotation fixes. 6. declare `py-webauthn>=2.0.0` + drop the deptry `DEP001` and ty `allowed-unresolved-imports` suppressions. 7. `quality_check` string. 8. docs-group split (README note last).

## Phase 4 progress — steps 5–7 (mypy strictness, webauthn, quality_check)

### Step 5 — mypy `disallow_untyped_defs = true` + the 8 annotation fixes (commit `6d7a8e2`)

Before (scope item 6, measured at `6cc7375` with the flag on): **8 errors in 6 files**, all
`error: Function is missing a return type annotation [no-untyped-def]`:

| # | File | Def |
|---|---|---|
| 1 | `src/backend/authentication/repository.py` | `_attach_utc` |
| 2 | `src/backend/authentication/service.py` | `AuthService._user_by_identifier` |
| 3 | `src/backend/authentication/webauthn.py` | `_webauthn` |
| 4 | `src/backend/permissions/repositories.py` | `_make_engine` |
| 5 | `src/backend/usermanagement/models.py` | `RoleListType.process_bind_param` |
| 6 | `src/backend/usermanagement/models.py` | `RoleListType.process_result_value` |
| 7 | `src/main.py` | `_LazyPermissionService.__getattr__` |
| 8 | `src/main.py` | `_LazyUserManager.__getattr__` |

After: `uv run mypy src/` → **Success: no issues found in 83 source files**. The flag is set in
`[tool.mypy]`; `warn-return-any` deliberately stays off (it reports **20 errors in 12 files**,
recorded in the pyproject comment — enabling it is not in scope). The diff is annotations only:
18 insertions / 10 deletions across the 6 files + `pyproject.toml`, no logic change, no test touched.

**`_attach_utc` — a PEP 695 generic was measured and rejected.** The precise return is generic
(`def _attach_utc[T: (Session, PasswordReset, WebAuthnCredential)](obj: T | None) -> T | None`).
Measured in this worktree: `ty` goes **152 → 155**, adding exactly three
`error[invalid-return-type]` at `src/backend/authentication/repository.py:126:20`, `:155:20`,
`:248:20` — the `return [_attach_utc(row) for row in s.exec(...).all()]` statements of
`SqliteSessionRepository.list_for_user` (126), `SqliteSessionRepository.list_all` (155) and
`SqliteWebAuthnCredentialRepository.list_for_user` (248); the comprehensions start on 124/153/246.
`T | None` does not
satisfy the declared `list[Session]` / `list[WebAuthnCredential]` returns. mypy gains nothing from
it either (it types SQLModel table classes as `Any`). The shipped annotation is therefore
`-> Any` with a reason comment naming the trade-off; the generic is the upgrade path if `ty` ever
narrows SQLModel.

### Step 6 — the `webauthn` dependency: distribution-name finding, API mismatch, revert

**Distribution-name fact.** The authentication spec (Dependencies) and ADR-031 name the library
"py-webauthn". Its PyPI **distribution** is `webauthn` (module `webauthn`, latest 3.0.1). The
distribution literally named `py-webauthn` is an unrelated FIDO-metadata package stuck at 0.0.6, so
`py-webauthn>=2.0.0` is unresolvable ("only py-webauthn<=0.0.6 is available"). `ffe1241` therefore
declared `webauthn>=2.0.0` (resolves 3.0.1).

**API-version mismatch (the blocker).** `PyWebAuthnProvider` (`src/backend/authentication/webauthn.py`)
calls, with these exact keyword arguments:

- `generate_registration_options(rp_id=, rp_name=, user_id=<str>, user_name=, user_display_name=)` → `options.challenge` (str), `options.public_dict`
- `verify_registration_response(registration_response=<dict>, expected_challenge=<str>, expected_rp_id=, expected_origin=, require_user_verification=False)` → `verification["credential"]["id"|"publicKey"|"transports"|"signCount"]`
- `generate_authentication_options(credential_ids=[<str>], rp_id=, user_verification="preferred")`
- `verify_authentication_response(authentication_response=<dict>, expected_challenge=<str>, expected_rp_id=, expected_origin=, require_user_verification=False)` → `verification.get("new_sign_count", 0)`

Signatures probed in a throwaway venv (`%TEMP%/wa-probe`, Python 3.12; the worktree environment was
not churned):

| Distribution / version | `verify_registration_response` | `generate_authentication_options` |
|---|---|---|
| `webauthn` 3.0.1 (what `>=2.0.0` resolves) | `credential=`, `expected_challenge: bytes` → `VerifiedRegistration` object | `allow_credentials=` |
| `webauthn` 2.x | same 2.0 shape (`credential=`, bytes challenge) | `allow_credentials=` |
| `webauthn` 1.11.1 / 1.6.0 / 1.4.0 / 1.2.0 / **1.0.0** | `credential=`, `expected_challenge: bytes` | `allow_credentials=` |
| `webauthn` 0.4.7 | no such function (class API: `WebAuthnRegistrationResponse(...).verify()`) | — |
| `py-webauthn` 0.0.6 | no such function (installs a `webauthn` module that is an attestation/metadata library) | — |

**No released version of either distribution** takes `registration_response=` / `credential_ids=` / a
`str` challenge, and none returns the dict shape the code reads. `verify_authentication_response`
additionally requires `credential_public_key` and `credential_current_sign_count` in every released
version — the provider passes neither.

**Decision: revert (option 4).** At `main` the library is undeclared and absent from `uv.lock`, so the
status quo in a synced environment is that every provider method raises
`InvalidPasskeyResponseError("py-webauthn is required for PyWebAuthnProvider but is not installed")`.
Declaring any released version makes the deferred import succeed and the calls then raise
`TypeError: verify_registration_response() got an unexpected keyword argument 'registration_response'`
— swallowed by `except Exception` into `InvalidPasskeyResponseError("registration response verification
failed")`, a **different message** — or, for `generate_authentication_options`, an **uncaught**
`TypeError` that propagates out of the feature. Either is an externally observable behavior change,
which invariant 1 forbids. `ffe1241` is reverted with a new commit (`git revert --no-commit ffe1241`):
the `webauthn` entry is dropped, the deptry `DEP001 = ["webauthn"]` and ty
`allowed-unresolved-imports = ["webauthn"]` suppressions and their comments are restored verbatim, and
`uv.lock` returns to its pre-S4.6 state (webauthn + cbor2, cryptography, pyasn1, pyasn1-modules,
pyopenssl removed; the P-42 version drift left as at `main`). The worktree venv was re-synced
(`uv sync` uninstalled those 6 packages) so the gates below ran in the same environment as `main`
(`webauthn installed: False`).

**Follow-up defect (separate change, deliberately not fixed here).** `PyWebAuthnProvider` is written
against an API no released `webauthn` provides; adapting it to the current upstream API is its own
change (ISSUE/FEATURE), framed by the orchestrator as a backlog item.

### Gates after the revert (step 6 final state)

| Gate | Result |
|---|---|
| `uv run deptry .` | **Success! No dependency issues found.** (Scanning 89 files) |
| `uv run mypy src/` | **Success: no issues found in 83 source files** |
| `uv run ty check src/` | Found 152 diagnostics (unchanged from S4.5; informational, `quality.yml:25`) |
| `uv run ruff check .` | **All checks passed!** |
| `uv run ruff format --check .` | 324 files already formatted |
| `uv run pytest tests/ -q` | **728 passed, 1 skipped in 217.43s** |

Note: with `webauthn` installed but undeclared, deptry reports `DEP003 'webauthn' imported but it is a
transitive dependency` — the suppression alone is not enough, the environment must match the lock.
`uv sync` (exact) is what makes the reverted state verifiable.

### ty per-rule table (invariant 4, as amended)

| Rule | baseline `5c589d2` | after S4.5 / S4.6 / S4.7 |
|---|---|---|
| `error[invalid-type-form]` | 95 | 95 |
| `error[unresolved-attribute]` | 23 | 23 |
| `warning[unsupported-base]` | 18 | 18 |
| **`error[invalid-argument-type]`** | **5** | **6** |
| `error[invalid-return-type]` | 3 | 3 |
| `error[call-non-callable]` | 3 | 3 |
| `error[missing-argument]` | 2 | 2 |
| `error[invalid-base]` | 1 | 1 |
| `warning[deprecated]` | 1 | 1 |
| **total** | **151** | **152** |

The single addition is `error[invalid-argument-type]` at `src/backend/authentication/service.py:221`
(`Expected UserRead, found User`), from the precise `-> User | None` on
`AuthService._user_by_identifier`: mypy types SQLModel table classes as `Any` (so the annotation buys
the CI gate nothing) while ty types them as real classes. Accepted deviation — `ty` is informational
(`quality.yml:25`, `continue-on-error: true`), `mypy` is the gate (`quality.yml:23`) and is clean.

### Step 7 — `quality_check` at Phase 5 parity (commit `8322f27`, scope item 8)

Before (`pyproject.toml:215`): `quality_check = "uv run ruff check src/ && uv run mypy src/"`
After: `quality_check = "uv run ruff check . && uv run ruff format --check . && uv run mypy src/ && uv run deptry ."`
— the four commands of the Phase 5 lint/types gate (Q-6). complexipy stays out of the per-task loop;
pip-audit, mkdocs, alembic and coverage stay CI-only. All four verified clean (table above).

### Per-step full-suite counts (invariant 2: identical result at every step)

| Step | Commit | `uv run pytest tests/ -q` |
|---|---|---|
| S4.5 mypy strictness | `6d7a8e2` | 728 passed, 1 skipped — 218.05 s |
| S4.6 declare (later reverted) | `ffe1241` | 728 passed, 1 skipped — 218.87 s |
| S4.7 `quality_check` | `8322f27` | 728 passed, 1 skipped (recorded in the commit message) |
| S4.6 revert | `2486b64` | 728 passed, 1 skipped — 217.43 s |

The 1 skip is the pre-existing `tests/acceptance/filemanagement/test_filemanagement.py:364`
("symlinks not available on this host"). No test was modified, weakened or deleted in any of the four
steps (`git log --stat` shows no `tests/` file in `6d7a8e2`, `ffe1241`, `8322f27` or `2486b64`).

### Commits (steps 5–7)

| Commit | Message | Files |
|---|---|---|
| `6d7a8e2` | `refactor(pyproject-tooling-gaps): S4.5 enable mypy disallow_untyped_defs + annotate defs` | `pyproject.toml` + 6 src files (+18 / −10) |
| `ffe1241` | `refactor(pyproject-tooling-gaps): S4.6 declare py-webauthn, drop DEP001 + ty suppressions` | `pyproject.toml`, `uv.lock` (+159 / −9) |
| `8322f27` | `refactor(pyproject-tooling-gaps): S4.7 quality_check to Phase 5 parity` | `pyproject.toml` (+3 / −1) |
| `2486b64` | `refactor(pyproject-tooling-gaps): S4.6 revert webauthn declaration — provider API matches no released version` | `pyproject.toml`, `uv.lock` (+9 / −159, reverts `ffe1241`) |

`uv.lock` was `git checkout --`-reverted before each commit except where the lock change is the point
(`ffe1241`, and `2486b64` restoring it) — P-42 drift.

**Next step: 8** — docs-group split, the 11 `uv sync --only-group dev` lines, the `mkdocs-build`
pre-push hook entry, README note last. Then Phase 5.

---

## Phase 4 progress — step 8 (docs-group split) + Phase 4 complete

### Rebase onto `main` (before step 8)

- Base `5c589d2` → `eb68ed2` (`origin/main`, PRs #63–#67 merged). All **22** commits replayed; HEAD `f70d242` → `03a8f79`.
- **One conflict**, in `docs/workflow/PROBLEMS.md`: a **P-45 ID collision** — `structlog-logging` (merged as #67) had already taken P-45 *and* P-46 on `main`. Resolved per collision note (c): every `main` entry kept verbatim, this change's entry renumbered to **P-47** with a `**Renumbered:**` line naming the original commit `c0dd9ff` (`docs/workflow/PROBLEMS.md:437-442`).
- Post-rebase hash map (old → new, oldest first). Earlier sections of this record cite the **old** hashes; Phase 5 and the PR body use the new ones:

```text
f9d357f → 773ce93  P.4 baseline + refactor scope
c0dd9ff → 4dd95b0  P-45 friction (renumbered to P-47)
5b2b149 → f8cfa26  is_valid_value 47 → 8
c736105 → 8194eff  SettingDefinition::_validate 26 → 2
eae8fbd → 5d17352  SessionService::list_sessions 18 → 12
5a430d2 → 2d1b1a8  PermissionService::_check 17 → 10
12338c6 → 185e734  SearchService::search 17 → 13
57d6c8e → 96ebc95  record src/ complexity refactors
d3ff1ab → 6a50a50  test_inv_003_last_admin_invariant 38 → 6
6db0d5f → faaa4f9  test_last_admin_invariant 23 → 9
228a20a → 027b90c  test_inv_006_event_correspondence 22 → 6
754bb6b → 0d72617  test_nfr_005_concurrent_threads_safe 18 → 9
34a6f7e → fe23e36  FakeSmtpServer::_dialogue 17 → 5
acc1a74 → f9c89dd  record tests/ complexity refactors
e9d0c57 → 88a86f5  complexipy CI gate at 15, drop the pre-commit hook
ff98a3a → a075607  ruff DTZ + travel() aware datetime
6cc7375 → bbb7ff5  record steps 3–4
6d7a8e2 → 73960d8  mypy disallow_untyped_defs + annotations
ffe1241 → 0353d10  declare webauthn (reverted in 63cb54b)
8322f27 → 67d2ea1  quality_check Phase 5 parity
2486b64 → 63cb54b  revert webauthn declaration
f70d242 → 03a8f79  record steps 5–7
```

### Post-rebase gate re-run (measured at `03a8f79`, before step 8)

| Gate | Result |
|---|---|
| `uv run ruff check .` | **All checks passed!** |
| `uv run ruff format --check .` | **324 files already formatted** |
| `uv run mypy src/` | **Success: no issues found in 83 source files** |
| `uv run ty check src/` | **152** diagnostics (baseline 151; the recorded +1 accepted deviation) |
| `uv run deptry .` | **Success! No dependency issues found.** (89 files) |
| `uv run complexipy src tests --max-complexity-allowed 15` | **exit 0** |
| `uv run pytest tests/ -q` | **728 passed, 1 skipped in 216.51 s** |
| `uv run python scripts/check_traceability.py` | **PASS** (765 matrix rows, 129 spec IDs, 714 test functions) |

### Step 8 — docs dependency-group split (scope item 7, commit `47a4f04`)

- **Group move.** The 3 mkdocs entries with their comments (`mkdocs>=1.6`, `mkdocs-material>=9.5`, `mkdocstrings[python]>=1.0.6`) moved out of `[dependency-groups] dev` into a new `docs` group, with a header comment naming why the group exists. `[tool.uv] default-groups = ["dev"]` is **unchanged**, so a plain `uv sync` still installs `dev` only and every other CI job stays docs-free.
- **Sync-line count correction: 12, not 11.** Re-measured on this branch after the rebase: `uv sync --only-group dev` appears **12** times — `quality.yml` **8** (lines 21, 39, 56, 77, 92, 107, 122, 140), `spec-validation.yml` **3** (37, 66, 80), `lint.yml` **1** (35). The scope's "exactly 11" was measured at `5c589d2`; the **12th line is this change's own `complexity` job** (`quality.yml:140`, added in step 3). Only the `docs` job (`quality.yml:107`) was updated; the other 11 stay `--only-group dev`.
- **Correction to scope item 7 (the command it specified is invalid).** `uv sync --only-group dev --group docs` is **rejected by uv 0.11.13** — `--only-group` cannot be combined with `--group` (usage error, verified again in Phase 5). Shipped: `uv sync --only-group dev --only-group docs` → **exit 0**, then `uv run mkdocs build --strict` → **exit 0**. The split is real, not cosmetic: after a plain `uv sync`, `uv run --no-sync mkdocs build --strict` → **exit 2** (`Failed to spawn: mkdocs`).
- **Pre-push hook.** `.pre-commit-config.yaml:35` entry → `uv run --group docs mkdocs build --strict`. Verified: `uv run pre-commit run --hook-stage pre-push --files <changed>` → `mkdocs build --strict ... Passed`.
- **`uv.lock` committed intentionally** (P-42 handling unchanged): the `dev` → `docs` group move (2 lock blocks) plus the pre-existing P-42 version-drift line.
- **README note (last, per collision (b), against the post-#66 README, 96 lines).** One line added to the `## Development` command table (`README.md:66`): `uv run mkdocs build --strict       # docs site (built from userdocs/) — needs \`uv sync --group docs\``. No other README content touched; #66's text adopted as-is.
- **Recorded extension beyond item 7.** The bare `uv run mkdocs build --strict` in live guidance would break for any reader after the split, so it was updated in the two places that state the build gate as an instruction: `AGENTS.md:63` and `AGENTS.md:66` → `uv run --group docs mkdocs build --strict` (plus a group note in the MkDocs-site paragraph), and `userdocs/index.md` "Building the site" gained a `uv sync --group docs` line. Documentation-only; no behavior, no test, no source change.
- **Disclosed side effect.** Saving `AGENTS.md` let pre-commit's `trailing-whitespace` and `end-of-file-fixer` remove two **pre-existing** `AGENTS.md` nits (trailing spaces on line 563, a blank line at EOF, `@@ -560,7 +560,7 @@` and `@@ -1167,4 +1167,3 @@`). Not this change's intent, not hidden — they are in the step-8 diff.
- **Step-8 commit:** `47a4f04` — 7 files, **+29 / −20** (`pyproject.toml`, `uv.lock`, `.github/workflows/quality.yml`, `.pre-commit-config.yaml`, `AGENTS.md`, `README.md`, `userdocs/index.md`). No `src/` or `tests/` file.

## Phase 4 complete — all 8 steps (post-rebase hashes)

| Step | What it did | Commit(s) | Gate after the step |
|---|---|---|---|
| 1 | Refactored the 5 `src/` complexipy offenders: `is_valid_value` 47→8, `SettingDefinition::_validate` 26→2, `SessionService::list_sessions` 18→12, `PermissionService::_check` 17→10, `SearchService::search` 17→13 | `f8cfa26` `8194eff` `5d17352` `2d1b1a8` `185e734` + record `96ebc95` | targeted set GREEN; ruff clean; full suite 728 passed / 1 skipped |
| 2 | Refactored the 5 `tests/` offenders: `test_inv_003_last_admin_invariant` 38→6, `test_last_admin_invariant` 23→9, `test_inv_006_event_correspondence` 22→6, `test_nfr_005_concurrent_threads_safe` 18→9, `FakeSmtpServer::_dialogue` 17→5 — no assertion, strategy or `@settings` value changed | `6a50a50` `faaa4f9` `027b90c` `0d72617` `fe23e36` + record `f9c89dd` | targeted set GREEN; ruff clean; full suite 728 passed / 1 skipped |
| 3 | complexipy became a real CI gate at **15** (threshold flipped, new `complexity` job appended in `quality.yml`), pre-commit complexipy hook deleted | `88a86f5` | `complexipy src tests --max-complexity-allowed 15` exit 0 |
| 4 | Ruff `DTZ` selected + the one fix: `tests/tooling_test_helpers.py:53` naive `datetime.now()` → `datetime.now(UTC)` | `a075607` + record `bbb7ff5` | `ruff check .` clean; full suite 728 passed / 1 skipped |
| 5 | mypy `disallow_untyped_defs = true` + the 8 annotation fixes (annotations only, 6 src files) | `73960d8` | `mypy src/` clean (83 files); ty 151 → 152 (+1, accepted) |
| 6 | `webauthn` declaration attempted, then **reverted** — no released version matches `PyWebAuthnProvider`'s API (finding, follow-up defect filed) | `0353d10` → reverted by `63cb54b` | deptry clean; mypy clean; suite 728 passed / 1 skipped |
| 7 | `[tool.agent-runner] quality_check` raised to Phase 5 parity (`ruff check . && ruff format --check . && mypy src/ && deptry .`) | `67d2ea1` | all four commands clean |
| 8 | Docs dependency-group split (item 7, as corrected above) + README note + guidance updates | `47a4f04` | `uv sync --only-group dev --only-group docs` + `mkdocs build --strict` exit 0; pre-push hook Passed |

Record commits interleaved: `773ce93` (P.4 baseline), `4dd95b0` (P-47 friction), `96ebc95`, `f9c89dd`, `bbb7ff5`, `03a8f79`, `47a4f04`. **Phase 4 gate: GREEN at every step — 728 passed, 1 skipped, identical to the baseline; no test modified, weakened or deleted.**

---

## Phase 5 — VERIFY (REFACTOR)

Worktree `…-worktrees/refactor/pyproject-tooling-gaps`, branch `refactor/pyproject-tooling-gaps`, measured at `b47e568` (HEAD after the step-8 record commit); `origin/main` = `eb68ed2` and `git merge-base HEAD origin/main` = `eb68ed2` (branch is current with `main`). Phase 5 is read-only for `src/` and `tests/`: no code or test file was touched in this phase.

### S5.1 — full regression suite

`uv run pytest tests/ -q` → **728 passed, 1 skipped in 220.04 s (0:03:40)**, 0 failed.

- **Identical to the authoritative baseline** (728 passed, 1 skipped, 0 failed, 223.21 s at `5c589d2`) — AGENTS.md Phase 5 REFACTOR item 15 ("suite result identical to baseline") holds.
- The 1 skip is the pre-existing host-dependent `tests/acceptance/filemanagement/test_filemanagement.py:364` ("symlinks not available on this host").
- No flaky node failed in this run, so the documented wall-clock node `tests/contract/search/test_search_contracts.py::test_nfr_001_performance_budgets` needed no isolation re-run (its classification rule is recorded in step 1's `_check` note and `docs/verification/search.md:456`).

**Zero test changes vs the baseline (REFACTOR invariant 3), proved three ways:**

1. `git diff --stat origin/main...HEAD -- tests/` → 5 files, **+173 / −130**: `tests/integration/sessionmanagement/test_concurrency.py` (38), `tests/mail_test_helpers.py` (62), `tests/property/usermanagement/test_multi_role_invariants.py` (44), `tests/property/usermanagement/test_usermanagement_properties.py` (155), `tests/tooling_test_helpers.py` (4). Every one is a step-2 complexity restructuring (the first four) or the step-4 `DTZ` fix (naive `datetime.now()` → `datetime.now(UTC)` in the shared `travel()` helper). No other test file is touched; no test was deleted, skipped, xfailed or weakened.
2. Assertion inventory: `git diff origin/main...HEAD -- tests/ | grep -cE "^[-+].*assert"` → **2**. Both hits are the *same* line, `assert entry.session_id in all_ids`: it is removed from the nested `worker` closure of `test_nfr_005_concurrent_threads_safe` and re-added verbatim inside the extracted module-level `_nfr_005_worker` helper (the 18 → 9 restructuring). **Moved, not changed** — same expression, still executed once per `list_sessions` call in every worker thread, still surfaced by the unchanged trailing `assert not errors, errors`. This is the single moved-but-unchanged assertion the step-2 record reported.
3. Wider inventory: `git diff origin/main...HEAD -- tests/ | grep -cE "^[-+].*(pytest\.raises|@settings|@given|st\.|hypothesis)"` → **0** changed lines touching expectations, Hypothesis strategies or `@settings`; `grep -cE "^-def test_"` → **0** and `grep -cE "^\+def test_"` → **0** — no test function added or removed.
4. Marker inventory: `grep -cE "^\+.*(skip|xfail|parametrize|no:randomly)"` → **1** hit, and it is a docstring line in `test_usermanagement_properties.py` ("…the correspondence check is skipped:"), not a skip marker; the removal side is **0**. No test was skipped, xfailed or re-parametrized.

### S5.2 — lint + types (+ the remaining Phase 5 gates)

| Gate | Command | Exact result |
|---|---|---|
| Lint (whole repo, == CI `lint.yml:37`) | `uv run ruff check .` | **All checks passed!** |
| Format (== CI `lint.yml:39`) | `uv run ruff format --check .` | **324 files already formatted** |
| Types (== CI `quality.yml:23`) | `uv run mypy src/` | **Success: no issues found in 83 source files** |
| Types, informational (== CI `quality.yml:25`, `continue-on-error: true`) | `uv run ty check src/` | **Found 152 diagnostics** — baseline 151, the recorded **+1 accepted deviation** (`authentication/service.py:221`, `Expected UserRead, found User`) |
| Dependencies (== CI `quality.yml:94`) | `uv run deptry .` | **Success! No dependency issues found.** (Scanning 89 files) |
| Complexity at the new gate **15** (this change's own `complexity` job) | `uv run complexipy src tests --max-complexity-allowed 15` | **exit 0** — "All functions are within the allowed complexity." (baseline: exit 1, 10 offenders) |
| Traceability (== CI `spec-validation.yml:68`) | `uv run python scripts/check_traceability.py` | **Traceability: PASS (765 matrix rows, 129 spec IDs, 714 test functions)** |
| Docs site (== CI `quality.yml` `docs` job) | `uv run --group docs mkdocs build --strict` | **exit 0** — "Documentation built in 1.55 seconds" (the bare `uv run mkdocs build --strict` form is invalid after the item-7 group split — that is the point of the split) |
| Migrations (== CI `quality.yml:126`) | `ALEMBIC_DATABASE_URL=sqlite:////tmp/alembic-p5.db uv run alembic upgrade head` | **exit 0** — both revisions applied to a fresh temp DB (`→ eace2f772150`, `eace2f772150 → d94b7f2e6a31`) |

No gate failed, so no gate was re-run or weakened. `uv.lock` stayed **clean** through every `uv run` in this phase (`git status --porcelain` → only this record): the P-42 drift line is committed on this branch (`uv.lock` `version = "0.6.1"` == `pyproject.toml:4`), so the drift that made every earlier step re-lock is gone — this change closes P-42 as a side effect (collision note (d)).

### Architecture check (manual boundary review — AGENTS.md Phase 6 item 4)

`tests/architecture/` does not exist and is no longer cited anywhere (PR #65 removed the dangling citations), so the REFACTOR architecture gate is the manual review defined in AGENTS.md Phase 6 item 4, performed here read-only:

- **Code stays inside its own feature directory.** All **21** new `def`s this change adds are private helpers or private methods inside the file that owns them: `authentication/repository.py` `_attach_utc`; `authentication/service.py` `_user_by_identifier`; `authentication/webauthn.py` `_webauthn`; `permissions/repositories.py` `_make_engine`; `permissions/service.py` `_evaluate_grants`; `search/service.py` `_select_sources`; `sessionmanagement/service.py` `_listed_limit`, `_order_with_current`; `settings/models.py` `_text_value_valid`, `_number_value_valid`, `_slider_value_valid`, `_select_value_valid`, `_list_value_valid`, `is_valid_value`, `SettingDefinition._validate`, `_validate_kind_specs`, `_validate_no_kind_specs`, `_validate_kind_exclusive_constraints`; `usermanagement/models.py` `process_bind_param`, `process_result_value`; `main.py` two `__getattr__`. No new module, no new directory, nothing added to `shared/`.
- **No extracted helper is imported across a feature boundary.** Grepping every new helper name across `src/`, `tests/`, `scripts/` finds only its defining file. The three apparent extra hits are substring false positives: `test_webauthn_repository_roundtrip` and `test_list_value_validation` (test function names), and `_attach_utc` in `filemanagement/repository.py:37` and `usermanagement/repository.py:41` — each feature already owns **its own** copy of that 3-line helper, so the authentication copy follows the existing convention instead of creating a `shared/` abstraction (`shared/` stays deliberately small). Informational for Phase 6: the helper is now triplicated by convention, not shared by design.
- **Cross-feature imports in the changed files are unchanged from `main`** except one line: `src/backend/authentication/service.py:89` now also imports `User` from `backend.usermanagement` — the feature's **public package root** (`"User"` is in `__all__`, `src/backend/usermanagement/__init__.py:44`) — for the precise `-> User | None` annotation from step 5. Annotation-only; no new internal-module dependency.
- **Pre-existing, untouched, not a finding of this change:** `src/backend/sessionmanagement/service.py:31-32` imports `backend.authentication.models` / `backend.authentication.repositories` (submodules rather than the public root). No import line there was changed by this change; recorded so Phase 6 sees it as out of scope, not as introduced here.
- `model/` / `services/` roles: no file moved between roles; the settings validators stayed in `settings/models.py` (domain rules), the extracted session/search/permission helpers stayed in `services/` (use-case orchestration).

**Architecture check: PASS** — boundaries respected, no cross-feature internal import introduced.

### No observable behavior changed — every changed file classified

`git diff --stat origin/main...HEAD` → **24 files, +973 / −236**. Every file classified (a file that could not be classified would be a finding; there are none):

| File | Class |
|---|---|
| `pyproject.toml` | config (complexipy threshold 30→15, ruff `DTZ`, mypy `disallow_untyped_defs`, `quality_check` parity, `docs` dependency group) |
| `uv.lock` | config — lock metadata (the `dev`→`docs` group move, 2 blocks, + the pre-existing P-42 version line) |
| `.github/workflows/quality.yml` | CI (new `complexity` job; `docs` job sync line) |
| `.pre-commit-config.yaml` | CI/tooling (complexipy hook removed; `mkdocs-build` entry gains `--group docs`) |
| `src/backend/settings/models.py` | complexity-restructure (`is_valid_value` 47→8, `_validate` 26→2) |
| `src/backend/sessionmanagement/service.py` | complexity-restructure (`list_sessions` 18→12) |
| `src/backend/permissions/service.py` | complexity-restructure (`_check` 17→10) |
| `src/backend/search/service.py` | complexity-restructure (`search` 17→13) |
| `src/backend/authentication/repository.py` | annotation-only + complexity-restructure (`_attach_utc` helper) |
| `src/backend/authentication/service.py` | annotation-only + complexity-restructure (`_user_by_identifier`) |
| `src/backend/authentication/webauthn.py` | annotation-only + complexity-restructure (`_webauthn` deferred import) |
| `src/backend/permissions/repositories.py` | annotation-only + complexity-restructure (`_make_engine`) |
| `src/backend/usermanagement/models.py` | annotation-only (`TypeDecorator.process_*` signatures) |
| `src/main.py` | annotation-only (two `__getattr__` signatures) |
| `tests/integration/sessionmanagement/test_concurrency.py` | complexity-restructure (18→9) |
| `tests/mail_test_helpers.py` | complexity-restructure (`_dialogue` 17→5) |
| `tests/property/usermanagement/test_multi_role_invariants.py` | complexity-restructure (23→9) |
| `tests/property/usermanagement/test_usermanagement_properties.py` | complexity-restructure (38→6, 22→6) |
| `tests/tooling_test_helpers.py` | test-helper `DTZ` fix (naive → aware `datetime.now(UTC)`) |
| `AGENTS.md` | docs (mkdocs build gate gains `--group docs`; 2 pre-existing whitespace/EOF nits fixed by pre-commit, disclosed in step 8) |
| `README.md` | docs (one `## Development` table row) |
| `userdocs/index.md` | docs (one `uv sync --group docs` line) |
| `docs/verification/pyproject-tooling-gaps.md` | docs (this record) |
| `docs/workflow/PROBLEMS.md` | docs (P-47 entry) |

No file introduces behavior: the `src/` diffs are helper extractions, added private methods and annotations; the `tests/` diffs are structural; the rest is config/CI/docs. Whether any `src/` restructure altered semantics is Phase 6's bounded-review question (final-state review, not re-running the suite).

**Gate not run, with reason:** `uv run pre-commit run --all-files` — known pre-existing failure at `main` (`end-of-file-fixer` over 17 unrelated files), so a repo-wide run is not a signal here. The hook this change actually modifies was run scoped in step 8: `uv run pre-commit run --hook-stage pre-push --files <changed>` → `mkdocs build --strict ... Passed`.

### Verdict

**VERIFIED** — REFACTOR Phase 5 gate set passes: full suite GREEN and **identical to the baseline (728 passed, 1 skipped, 0 failed)**, with zero test changes beyond the recorded complexity restructuring and the one-line `DTZ` helper fix (proved by diffstat + assertion/strategy/marker inventories); `ruff check .`, `ruff format --check .`, `mypy src/`, `deptry .`, `complexipy … 15`, `check_traceability.py`, `mkdocs build --strict` and `alembic upgrade head` all clean; `ty` at the recorded **+1 accepted deviation** (152 vs 151, informational); architecture boundary review PASS; every changed file classified with no unclassified file. No gate was weakened, no test touched in this phase.

**Next:** Phase 6 (S6.1–S6.3 bounded review of the final state, then S6.4 — **no version bump** for REFACTOR — open the PR to `main`).

---

## Phase 6 — REVIEW (REFACTOR)

Worktree `…-worktrees/refactor/pyproject-tooling-gaps`, branch `refactor/pyproject-tooling-gaps`, HEAD `3fc5e22` (Phase 5 record), `origin/main` = `eb68ed2`. Bounded scope per AGENTS.md Phase 6: the **final state** of the 24 changed files (`git diff --stat origin/main...HEAD`) reviewed against the normative basis — the GREEN baseline + the 8-item refactor scope + the 6 invariants + the Phase 5 verdict. The full suite was **not** re-run (Phase 5: 728 passed, 1 skipped). Read-only for `src/`, `tests/`, config and CI: no file outside this record was modified. Cheap targeted commands run here: the per-file `git diff origin/main...HEAD -- <file>` hunks plus final-state reads, `uv run complexipy src tests --max-complexity-allowed 15` (**exit 0**), `uv run pytest tests/{unit,acceptance,property,contract}/settings -q` (**85 passed** — the highest-risk restructure, `is_valid_value` 47→8), `uv sync --only-group dev --only-group docs --dry-run` (**exit 0** — the corrected docs-job syntax), `def test_` inventories, and import/usage greps.

### S6.1 findings (normative basis: no behavior change beyond the type's contract)

| F-n | Finding | Severity | Resolution |
|---|---|---|---|
| F-1 | `src/backend/authentication/service.py:89` now imports `User` (not only `UserRead`) from `backend.usermanagement` (Phase 5 flag) | Info | **Accepted.** `User` is in `backend.usermanagement.__all__` (`__init__.py:44`) — the feature's declared public interface, not an internal module — and the same statement already imports `UserRead`/`UserManager`/`UserRepository` from that root. `User` occurs at exactly two lines: the import and the `-> User \| None` annotation at `:162`; nothing else in the file uses it. Annotation-only, no new import edge, no runtime behavior change (the module has no `from __future__ import annotations`, so the annotation is evaluated at def time and the import is required — it is present). The `ty` diagnostic it surfaced (`:221 Expected UserRead, found User`) is the recorded **+1 accepted deviation** (informational job, `quality.yml:25`). |
| F-2 | `_attach_utc` now exists in three features (authentication, filemanagement, usermanagement) — Phase 5 flag | Info | **Accepted, and not introduced here.** The authentication copy is on `main` already (`git show origin/main:src/backend/authentication/repository.py:37`); this change only added its `-> Any` return annotation. The filemanagement (`:37`) and usermanagement (`:41`) copies are untouched by the diff. Per-feature copies are the existing convention and keep `shared/` deliberately small; consolidating is a separate REFACTOR if it is ever worth it. |
| F-3 | `src/backend/sessionmanagement/service.py:31-32` import `backend.authentication.models` / `.repositories` (submodules, not the public root) | Info (pre-existing) | **Out of scope, confirmed.** The diff for that file contains **no** import-line change (`git diff … \| grep -E "^[-+](import\|from)"` → empty); the two lines are byte-identical on both sides. Recorded for a future boundary change, not a finding of this one. |
| F-4 | **Scope item 4 (declare `py-webauthn>=2.0.0`) was not delivered — it was reverted.** The largest deviation from the recorded scope | Accepted deviation (highest-value finding) | **Accepted on the evidence.** The scope's premise is factually false: the `py-webauthn` distribution is an unrelated FIDO-metadata package (≤ 0.0.6, so `>=2.0.0` is unresolvable), and no released `webauthn` (0.4.7 → 3.0.1) matches `PyWebAuthnProvider`'s keyword arguments or return shapes. Declaring any released version would flip observable behavior (the deferred import starts succeeding → `TypeError` → a different `InvalidPasskeyResponseError` message, or an uncaught `TypeError` out of `generate_authentication_options`), which invariant 1 forbids. **Final state verified main-equivalent for webauthn:** the `pyproject.toml` hunks are byte-identical to `origin/main` (`DEP001 = ["webauthn"]` + its 3-line comment; `allowed-unresolved-imports = ["webauthn"]` + its 4-line comment), and `git diff origin/main...HEAD -- uv.lock` adds **no** `webauthn`/`cbor2`/`cryptography`/`pyasn1`/`pyasn1-modules`/`pyopenssl` block — only the `dev`→`docs` group move (2 blocks) and the pre-existing P-42 version line. |
| F-5 | The follow-up defect (`PyWebAuthnProvider` is written against an API no released `webauthn` provides) has **no `docs/todo/` file on `main`** yet — neither at `eb68ed2` nor in the primary worktree | Action item (orchestrator, planning record) | **Accepted as an orchestrator action, not a code fix.** The requirement of this review — that the defect is recorded as a separate change rather than half-fixed here — **holds**: it is documented in the step-6 section and the final state is main-equivalent. The orchestrator MUST frame it as its own backlog item (`docs/todo/<name>.md`, ISSUE/FEATURE) before or with S6.4; the PR body should name it. |
| F-6 | `AGENTS.md:63/66` + `userdocs/index.md` + the `README.md` row go beyond the literal text of scope item 7 | Info | **Accepted as a required consequence of the split.** After the group move the bare `uv run mkdocs build --strict` in live guidance is a command that fails (Phase 5 measured **exit 2** for the bare form after a plain `uv sync`), so leaving the guidance stale would ship a documented-but-broken instruction. Editing `AGENTS.md` in a change PR has precedent on `main` (`4c20c5f`, `5902af4`). Documentation-only: no behavior, no test, no source change. |
| F-7 | Two pre-existing `AGENTS.md` nits are in the step-8 diff (trailing spaces at `:563`, blank line at EOF) | Info | **Accepted, disclosed in step 8.** They were applied by the repository's own `trailing-whitespace` / `end-of-file-fixer` hooks on save; reverting them would leave the branch failing its own pre-commit hooks. No behavior. |
| F-8 | The complexity threshold is stated twice: `[tool.complexipy] max-complexity-allowed = 15` and the CI flag `--max-complexity-allowed 15` | Info | **Accepted as deliberate** — the workflow comment says the repeat is intentional ("so CI fails loudly on a bad config"). Both are 15; the gate is exit 0 (re-measured in this review). |
| F-9 | `tests/integration/sessionmanagement/test_concurrency.py` — the extracted `_nfr_005_worker` types `service: Any` rather than `SessionService` | Info (style, test-only) | **Accepted, not fixed here** (this review is read-only for `tests/`). No effect on assertions or concurrency semantics; a one-line typing nit for a future change. |
| F-10 | Review-method note: the `main` form `except UserAlreadyExistsError, LastAdminError, UserNotFoundError:` in the two usermanagement property tests looks like a SyntaxError to any pre-3.14 parser | Info (no finding) | **Verified not a defect.** PEP 758 (Python 3.14) allows unparenthesized `except` lists; the `main` blobs compile under the project interpreter (`.venv` → **Python 3.14.5**) and collect 7 tests. The change's replacement with `contextlib.suppress(…)` is semantically identical (same exception tuple, same suppression scope). |

### S6.1 per-file behavior-preservation verdicts — the 10 `src/` restructures

Each verdict is from the final function read in full **plus** its `git diff origin/main...HEAD -- <file>` hunk: branches, return values, exception types and message strings, evaluation order, side effects (events, log records, DB writes).

| File / function | Verdict | What was checked |
|---|---|---|
| `settings/models.py` `is_valid_value` (47→8) | **EQUIVALENT** | The five extracted helpers (`_text_value_valid`, `_number_value_valid`, `_slider_value_valid`, `_select_value_valid`, `_list_value_valid`) are **verbatim moves** of the five former branch bodies — compared line by line in the hunk (same `isinstance`/`_is_number` guards, same `re.fullmatch`, same `not (… and …)` tails, same `ListSpec()` default, same `allow_duplicates` tail). `is_valid_value` keeps its exact signature and defaults; the dispatch is the same flat `if kind is …` chain in the **same order**; BOOLEAN and EMAIL stay inline; the terminal `return False` fallthrough for an unknown kind is unchanged, so every kind still maps to the same outcome and no branch became unreachable. `noqa` narrowed `PLR0911, PLR0912` → `PLR0911` (RUF100 evidence in step 1). Targeted re-run in this review: settings **85 passed**. |
| `settings/models.py` `SettingDefinition::_validate` (26→2) | **EQUIVALENT** | Order preserved exactly: key format → kind-spec presence/mismatch → TEXT-only → NUMBER-only → default validity → `return self`. The `else` arm moved verbatim into `_validate_no_kind_specs`; `_validate_kind_exclusive_constraints` carries the TEXT-only/NUMBER-only checks in the original order. All six `SettingsValidationError` message strings are byte-identical (the `f"{kind} …"` interpolations re-read `self.kind`, the same value the original local held). The LIST `pass` arm and the validator decorator (`mode="after"`) are unchanged; the new members are private methods, so Pydantic gains no field and `@logged_class` (`_decorator.py:68`, skips `_`-prefixed names) traces nothing new. |
| `sessionmanagement/service.py` `list_sessions` (18→12) | **EQUIVALENT** | The argument guards, the single `now = datetime.now(UTC)` snapshot (INV-002), the token path (`get_by_token_hash` → `InvalidSessionError("invalid session")`), the `AssertionError` guard and the `valid` filter are untouched. `_order_with_current` reproduces the current-session-first ordering: the two comprehensions (`== current` / `!= current`) swapped evaluation order but are pure, and the `current_session_id is None` case returns `valid` itself exactly as the old `ordered = valid` did. `_listed_limit` reads the live `sessionmanagement.max_listed_sessions` **only** when `limit is None`, at the same point relative to `_to_entry` and the `SessionsListed` publish; `_resolve_token` is still **not** used on this path (it re-reads the clock). Same event, same count, same slice bound. |
| `permissions/service.py` `_check` (17→10) | **EQUIVALENT** | `_evaluate_grants` is a **verbatim move** of the former tail — diffed line by line against `origin/main`'s `_check`: system-principal branch (`_system_repository.get_permissions()` live read → `None`/`"unauthorized"`), admin implicit wildcard (`return None`), the role-union loop over `user.roles` with `_any_grant_matches`, and the final `"unauthorized"`. Steps 1–4 of `_check` (permission shape → principal → session → catalog) are unchanged, so the closed reason set and its precedence are unchanged; `# noqa: PLR0911` still needed (7 early returns). |
| `search/service.py` `search` (17→13) | **EQUIVALENT** | `_select_sources` holds `self._lock` over exactly the statements the original `with` block held (single-feature lookup → `UnknownSourceError(feature)`, else `list(self._sources.values())`); `_validate_pagination` was already outside the lock and still is. The `RLock` is re-entrant, so no new deadlock window. Everything after selection — per-source strict validation, free-text normalization, `_effective_limit`, the fan-out with its single-source `SourceQueryFailedError` vs global marker + `SourceQueryFailed` event, and the `SearchResult` — is untouched, and `@requires_permission("search.search")` still wraps `search`. |
| `main.py` (2 sites) | **ANNOTATION-ONLY** | `_LazyPermissionService.__getattr__` / `_LazyUserManager.__getattr__` gained `-> Any`; bodies byte-identical; only `from typing import Any` added. |
| `authentication/webauthn.py` | **ANNOTATION-ONLY** | `_webauthn() -> Any`; the deferred `import webauthn` and the `InvalidPasskeyResponseError("py-webauthn is required …")` fallback are unchanged (and, per F-4, `webauthn` stays undeclared/absent, so the fallback remains the live path). |
| `authentication/service.py` | **ANNOTATION-ONLY** | `_user_by_identifier(...) -> User \| None`; body unchanged (username lookup, then email fallback). Import change is the public-root `User` name (F-1). |
| `usermanagement/models.py` | **ANNOTATION-ONLY** | `RoleListType.process_bind_param(value: Any, dialect: Dialect) -> Any` and `process_result_value(...) -> Any`; bodies byte-identical; `impl`/`cache_ok` unchanged, so the column type and its serialization are unchanged. |
| `permissions/repositories.py` | **ANNOTATION-ONLY** | `_make_engine(database_url: str) -> Engine`; body unchanged; `from sqlalchemy import Engine` added (already a dependency). |
| `authentication/repository.py` | **ANNOTATION-ONLY** | `_attach_utc(...) -> Any` + the 2-line reason comment recording the measured generic trade-off; body unchanged; `from typing import Any` added. |

**Tracing side-effect check (all 10 files):** every helper this change adds is underscore-prefixed, and `@logged_class` skips `_`-prefixed names (`src/backend/logging/_decorator.py:68`), so **no new log record** is emitted by any traced class (`SessionService`, `SearchService`, `PermissionService`, `AuthService`, the repositories). No event, DB write or public signature changed.

### S6.1 test-integrity verdict — the 5 `tests/` restructures assert exactly what they did before

| File / function | Verdict | What was checked |
|---|---|---|
| `tests/integration/sessionmanagement/test_concurrency.py` `test_nfr_005_concurrent_threads_safe` (18→9) | **UNCHANGED SEMANTICS** | The `worker(uid)` closure became `_nfr_005_worker(service, uid, rows, all_ids, errors)` with the captured values passed as arguments. `rows_by_user[uid]` is now read on the submitting thread — verified safe in the final body: the dict is built in one comprehension **before** the pool opens and is never mutated afterwards. Same `ThreadPoolExecutor(max_workers=8)`, same 4 submitted workers, same per-thread sequence (revoke own 10 → 5 × list-and-assert → `revoke_all_sessions` → `cleanup_expired`), same `except BaseException → errors.append`, same `future.result()` joins, same trailing `assert not errors, errors` and the per-user `list_sessions(user_id=uid) == []` asserts. The single assert-line diff pair is `assert entry.session_id in all_ids` moved with the worker (re-indented only). |
| `tests/property/usermanagement/test_usermanagement_properties.py` `test_inv_003_last_admin_invariant` (38→6) | **UNCHANGED SEMANTICS** | `@settings(max_examples=…, suppress_health_check=[too_slow])` and the `@given` list strategy are byte-identical (decorator/strategy inventory in step 2, re-read here). `itertools.count(start=1)` reproduces the `nonlocal counter` sequence exactly for both create ops (username generated first, email uses the post-increment value — checked for `a{n}x`/`a{n}@…` and `m{n}x`/`m{n}@…`). `_mutate_first_admin` reproduces the "first admin that accepts it" loop (`except LastAdminError → continue`, `break` on success), and the `include_inactive` flags match `main` per op: `True` for delete, `False` for deactivate (`main` used `list_users(include_inactive=True)` / `list_users()`). Suppression list identical (`UserAlreadyExistsError, LastAdminError, UserNotFoundError`) via `contextlib.suppress`. The invariant check (`admin_users` + `assert any(u.is_active …)`) stays inline and byte-identical. |
| `tests/property/usermanagement/test_usermanagement_properties.py` `test_inv_006_event_correspondence` (22→6) | **UNCHANGED SEMANTICS** | `_apply_event_op` returns the event type the op must publish, or `None` for the two idempotent no-ops (REQ-009) and for an op the sequence does not perform — the same three skip decisions the two inner `continue`s and the `else: continue` made. The exception path is equivalent: `ev = None` pre-set, `contextlib.suppress(LastAdminError, InvalidRoleError, UserNotFoundError)` leaves it `None` → `continue`, exactly the old `except … : continue`. The `create` branch (with its `UserCreated` count assert) and both trailing asserts (`len(events) >= 1`, `events[-1].user_id == user_id`) are unchanged; `counter` is still incremented once per op in the test and passed by value. |
| `tests/property/usermanagement/test_multi_role_invariants.py` `test_last_admin_invariant` (23→9) | **UNCHANGED SEMANTICS** | `_apply_op` reproduces the four branches in order, including the `else: _apply_admin_op(...)` fallthrough and the `add_admin` target selection (`next((u for u in users if "admin" not in u.roles), None)` + the `None` guard). Same `count(start=1)` substitution, same 4-exception suppression list, initial-admin seeding line, inline invariant comment and the inline `admin_users` / `assert any(u.is_active …)` check all unchanged; the pre-existing `_apply_admin_op` was not touched. |
| `tests/mail_test_helpers.py` `FakeSmtpServer::_dialogue` (17→5) | **UNCHANGED SEMANTICS** | Test **helper** (0 test functions, 0 assertions). The loop now reads one line and delegates to `_handle_command` / `_handle_auth` / `_handle_mail_from`; the helper returns `False` exactly where the old body `return`ed — QUIT, `auth_fail`, `protocol_fail` — and `True` otherwise, so the dialogue ends on the same three commands. Same `startswith` match order (EHLO, AUTH, MAIL FROM, RCPT TO, DATA, QUIT, else), same response bytes (`250 fake.smtp.local`, `535 …`, `235 …`, `550 …`, `250 ok`, `354 go ahead`, `250 queued`, `221 bye`), same `_readline`/`_read_data`/`_send`/`_serve`/`_hold`/`close`. |
| `tests/tooling_test_helpers.py` `travel()` | **INTENDED, SCOPE-APPROVED VALUE CHANGE** | `yield datetime.now()` → `datetime.now(UTC)` (scope item 5, the single `DTZ005`). Re-verified in this review: `grep -rn "tooling_test_helpers|model_factory(|mock_http(|travel(" tests/ src/` excluding the helper file itself → **no importer**, so the naive→aware value is not observable to the current suite; Phase 5's full-suite run is the confirmation. No `noqa`, no per-file ignore. |

**Test-integrity verdict: PASS.** `def test_` count over `tests/`: **733 on `origin/main`, 733 at HEAD** (per-file: concurrency 2/2, multi-role 1/1, usermanagement properties 6/6, helpers 0/0) — nothing added, deleted, skipped or xfailed. `git diff --stat origin/main...HEAD -- tests/acceptance tests/contract tests/unit` → **empty**; the only `tests/integration` file touched is `test_concurrency.py`. No `@given` strategy, `@settings` value (incl. the measured `deadline=1000`), `assume()`, expected exception or assertion was weakened, dropped or made conditional — the single assert-line diff pair is the moved-and-re-indented `assert entry.session_id in all_ids`.

### S6.2 traceability + boundaries verdict

- **Traceability (no spec for this change → scope-item evidence):** all **8** scope items are evidenced in this record — 1 complexipy gate + the 10 refactors (per-function before/after tables, gate exit 0), 2 hook removal (diff + scoped `pre-commit run` exit 0), 3 one engine (the dev pin is the only one once the hook is gone), 4 webauthn (attempt → measured API-mismatch finding → revert, F-4), 5 `DTZ` (before/after `ruff check --select DTZ`, no `noqa`), 6 `quality_check` string (all four commands verified clean), 7 docs-group split (group move, 12 sync lines, hook entry, `mkdocs build --strict` exit 0, README note, guidance updates), 8 mypy `disallow_untyped_defs` (the 8-error list → `mypy src/` clean). `uv run python scripts/check_traceability.py` → **PASS (765 matrix rows, 129 spec IDs, 714 test functions)** is recorded at Phase 5; this change adds no spec ID and no orphaned test (test-function count unchanged).
- **Boundaries / architecture:** every new `def` is private and inside the file that owns it; no new module, directory, or `shared/` addition; no extracted helper is imported anywhere (grep over `src/`, `tests/`, `scripts/`); the only cross-feature import change is the public-root `User` name (F-1, accepted). `model/` vs `services/` roles unchanged. **PASS.**
- **Config / CI / docs introduce no runtime behavior:** the new `complexity` job is appended (no existing job's step list edited — collision note (a) honored), the removed pre-commit hook is redundant with it, `DTZ` only forbids naive datetimes (the one violation fixed), `disallow_untyped_defs` is a checker flag, `quality_check` is the agent-runner's own gate string, and the `docs` group split changes only which optional tooling a sync installs — `default-groups = ["dev"]` is unchanged, so `uv sync` behaves as before; the docs-job syntax was re-verified here (`uv sync --only-group dev --only-group docs --dry-run` → exit 0). The `AGENTS.md`/`userdocs`/`README` edits are the guidance consequence of that split (F-6) plus two disclosed whitespace nits (F-7).
- **Webauthn revert completeness:** verified main-equivalent (F-4) — `pyproject.toml` webauthn hunks byte-identical, `uv.lock` carries no webauthn or transitive block, and the follow-up defect is a separate change (F-5), not half-fixed here.

### Verdict

**CLEAN** — REFACTOR review gate satisfied: the full suite is GREEN with **zero test changes** beyond the recorded complexity restructuring and the one-line `DTZ` helper fix (Phase 5: 728 passed, 1 skipped, identical to the baseline; test-function count 733 → 733), **no observable behavior changed** — all 24 changed files re-classified from the final state (the 10 `src/` restructures verdicted EQUIVALENT or ANNOTATION-ONLY, the 5 `tests/` restructures UNCHANGED SEMANTICS, the one scope-approved `travel()` value change, everything else config/CI/docs), the 6 recorded invariants hold, and all 8 scope items are evidenced — with **one** scope item (4, declare `py-webauthn>=2.0.0`) delivered as a **measured revert** (F-4) rather than as code.

**Findings: 10 — open: 0.** Every finding is closed inside this review; none requires a code change.

| F-n | Finding (short) | Disposition |
|---|---|---|
| F-1 | `authentication/service.py` imports `User` from `backend.usermanagement`'s public root (`__all__`, `__init__.py:44`), used only in the `-> User \| None` annotation at `service.py:162`; the `ty` +1 is the recorded accepted informational deviation | **ACCEPTED** |
| F-2 | `_attach_utc` exists in three features by convention; the `authentication` copy is pre-existing on `main` (`repository.py:37`), the other two untouched by this diff | **ACCEPTED — not introduced here** |
| F-3 | `sessionmanagement/service.py:31-32` imports `backend.authentication.models` / `.repositories` submodules | **PRE-EXISTING, out of scope** (no import-line change in the diff) |
| F-4 | Scope item 4 (declare `py-webauthn>=2.0.0`) **not delivered — reverted**: the PyPI distribution literally named `py-webauthn` (0.0.6) is an unrelated FIDO-metadata package, and no released `webauthn` (0.4.7 → 3.0.1, the probed range) matches `PyWebAuthnProvider`'s call signatures; declaring any version would change observable behavior (invariant 1). Final state verified `main`-equivalent: the `pyproject.toml` webauthn hunks are byte-identical and `uv.lock` has no `webauthn`/`cbor2`/`cryptography`/`pyasn1`/`pyopenssl` block | **ACCEPTED DEVIATION** (the only scope item not delivered as code) |
| F-5 | The follow-up webauthn-provider defect needs its own `docs/todo/` file; the PR body must name it | **ACTION ITEM (orchestrator)** — recorded here and named in the PR body |
| F-6 | The `AGENTS.md`/`userdocs/index.md`/`README` guidance edits go beyond scope item 7's literal text | **ACCEPTED as a required consequence of the docs-group split** (bare `uv run mkdocs build --strict` measured exit 2 after a plain `uv sync`); AGENTS.md-in-a-PR precedent `4c20c5f`, `5902af4` |
| F-7 | Two pre-existing `AGENTS.md` whitespace/EOF nits fixed by the hooks inside the step-8 diff | **ACCEPTED, disclosed** |
| F-8 | The complexity threshold is stated twice (`[tool.complexipy]` 15 + the CI flag 15) | **ACCEPTED, deliberate** (CI fails loudly on a bad config) |
| F-9 | `_nfr_005_worker(service: Any)` typing nit | **ACCEPTED** — the review is read-only for `tests/` |
| F-10 | Method note: `except A, B, C:` on `main` is legal PEP 758 on the project's Python 3.14.5 (compiles, 7 tests collect) | not a defect |

**Phase 6 gate: CLEAN** — no open finding, so per AGENTS.md the branch goes to `main` through a PR for human review/merge (S6.4); the agent does not merge it.

**Version bump: none** — REFACTOR gets no bump per the AGENTS.md versioning table. `pyproject.toml:4` stays `version = "0.6.1"`, identical to `origin/main:pyproject.toml:4`, and `git diff origin/main...HEAD -- pyproject.toml` contains no version-line change (only context matches). `bump-my-version` was not run.

**Pre-merge full-regression evidence:** the Phase 5 run at `b47e568` — `uv run pytest tests/ -q` → **728 passed, 1 skipped in 220.04 s**, identical to the authoritative baseline (728 passed, 1 skipped, 223.21 s). Phase 6 does **not** re-run it (AGENTS.md Phase 6 bounded scope: Phase 5 already confirmed the gate CLEAN).

