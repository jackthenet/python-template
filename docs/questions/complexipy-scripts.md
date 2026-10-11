# Questions: complexipy-scripts

One question file per change, created at **P.1 Frame** from this template and named `complexipy-scripts.md`. It replaces the retired central `AI_Questions.md` (archived at `docs/questions/archive-AI_Questions.md`).

- **Change:** complexipy-scripts (DOCS/CHORE — reclassified at P.3 **Q-16** from P.1's REFACTOR)
- **TODO file:** `docs/todo/complexipy-scripts.md`
- **Spec:** n/a
- **Opened:** 2026-10-09
- **Status:** ALL ANSWERED  <!-- OPEN | ALL ANSWERED — set OPEN by the orchestrator at P.1; ALL ANSWERED once every question in this file has an answer (the orchestrator records it together with the `QUESTIONS-ANSWERED` TODO advance) -->
- **Answer rounds:** 5 (all on 2026-10-11 — 18 entries Q-01…Q-18, 0 PENDING)

Every question that needs user input is recorded HERE — never in a central file. A step that needs input records **all** of its open questions in one batch and returns `BLOCKED-USER`; the orchestrator presents them (as few `ask_user_question` rounds as possible, <= 4 per round, most blocking first), records the answers here, marks each **ANSWERED** and **incorporated**, and relaunches the step **once** with the full answer set. The change is `WAITING` while its questions are unanswered — the orchestrator works on another change meanwhile, it does not idle.

### Entry format

```markdown
## Q-<n> — <short title>
- **Step:** <P.2 Interrogate, or Sx.x <step name> — Phase <n>>
- **Why needed:** <the ambiguity, missing requirement, or decision>
- **Context:** <what the step had learned at the time>
- **Question:** <the question for the user>
- **Recommended:** <the step's proposed answer + one-line reason>
- **Answer:** <the user's answer>  (or **PENDING**)
- **Date:** <YYYY-MM-DD>
- **Status:** PENDING | ANSWERED
- **Incorporated:** no | yes — <where: REQ-XXX / AC-XXX / spec section / decision>
```

## Preparation questions (P.2)

18 entries, one `BLOCKED-USER` batch, most-blocking first (Q-01…Q-04 are the gate blockers; the orchestrator can present them as round 1).

**Measured at `be1eb5a` (2026-10-10), the facts every entry below is grounded in:**

- `uv run pytest tests/ -q -p no:randomly` → **1 failed, 815 passed, 1 skipped in 248 s** — the suite is **not** GREEN on `main` (Q-01/Q-02).
- `uv run complexipy scripts --max-complexity-allowed 15` → exit 1, 49 functions analysed, exactly 4 FAILED: `check_traceability.py::check` **17**, `check_traceability.py::matrix_rows` **19**, `validate_task_dag.py::check_acyclic` **22**, `verify_spec.py::main` **22**. `make_map.py` max = 12 (`_member_lines`), `_drop_long_defaults` = 6.
- Gate scope is named in **two** places: `pyproject.toml:99-101` `[tool.complexipy] paths = ["src","tests"]`, `max-complexity-allowed = 15`; and `.github/workflows/quality.yml:146` `uv run complexipy src tests --max-complexity-allowed 15` (comment at `:144`: the threshold "lives in `[tool.complexipy]` and is repeated here so CI fails loudly on a bad config"). Measured: positional args override the config `paths`; `uv run complexipy` with no args analyses `src`+`tests` only and exits **0** today.
- `scripts/` is already inside other gates: `mypy scripts/` is a CI gate (`quality.yml`, and `test_nfr_004_mypy_and_ruff_clean` runs it), ruff covers the whole repo (`lint.yml`, `D` per-file-ignored for `scripts/*`), `deptry .` includes `scripts/` (pre-commit `files:` pattern `…|scripts/|…`). Coverage stays `source = ["src/backend","src/frontend"]`, `fail_under = 92`; bandit `-r src/`; `ty` `root = ["./src"]` — none of them sees `scripts/`.
- Test coverage of the three scripts: **only** `tests/acceptance/test_structure_map.py` — `test_ac_025_mypy_covers_scripts` (runs `verify_spec.py docs/specs/template.md` and compares stdout byte-for-byte to `_VERIFY_SPEC_REPORT_BEFORE_FIX`), `test_nfr_004_mypy_and_ruff_clean`, and `:336` (a map-content string). Nothing exercises `check_traceability.py` or `validate_task_dag.py` behaviorally, and CI runs the DAG validator with `|| true` (exit code discarded) (Q-03).
- Golden outputs measured today: `check_traceability.py` → `Traceability: PASS (881 matrix rows, 136 spec IDs, 801 test functions)` exit 0 (0.17 s); `validate_task_dag.py .github/task-runner/tasks.json` → `Task DAG validation PASSED: 7 tasks, acyclic, well-formed.` exit 0 (0.09 s); `verify_spec.py docs/specs/structure-map.md` → `Traceability: PASS` exit 0 (0.13 s).
- Nothing imports the three modules (`src/`, `tests/`, `scripts/`, `.github/` searched) — they are invoked as programs only.
- **Overlap check** (against `docs/specs/` and every TODO in `docs/todo/`, live and archive): `docs/specs/structure-map.md` NFR-005 + `ADR-086` pin the current gate scope (Q-04); `docs/todo/map-default-drop-shift.md` (WAITING, PR #79; branch diff = `STRUCTURE.md`, `docs/specs/structure-map.md`, `docs/verification/map-default-drop-shift.md`, and its ISSUE PR will edit `scripts/make_map.py`) collides on `STRUCTURE.md` only (Q-06, Q-14); `docs/todo/archive/pyproject-tooling-gaps.md` (MERGED) is the precedent — it created the `complexity` job, chose 15, and **rejected** the snapshot ratchet and any threshold raise (Q-13, Q-17); `docs/todo/python-3.15-upgrade.md` edits the same `quality.yml` job blocks but different lines; `docs/todo/settings-public-registry-setter.md` (IN-WORKFLOW) edits `pyproject.toml` at `[tool.ruff.lint]` (192-226), not `[tool.complexipy]` (99-101); `docs/todo/docstrings-tests.md` touches the `tests/*` ruff `D` ignore, not `scripts/*`. **No double work found.**

## Q-01 — The REFACTOR baseline is RED on `main`
- **Step:** P.2 Interrogate
- **Why needed:** the REFACTOR path requires a GREEN full-suite baseline before any restructuring, and "if it is not GREEN, STOP: resolve the pre-existing failures first or reclassify". The baseline is not GREEN, so P.4 cannot record it as it stands.
- **Context:** measured 2026-10-10 at `be1eb5a`: `uv run pytest tests/ -q -p no:randomly` → **1 failed, 815 passed, 1 skipped in 248 s**. The single failure is `tests/acceptance/test_structure_map.py::test_ac_021_committed_map_matches_fresh_render` (REQ-021/AC-021): committed `STRUCTURE.md:452` says `docs/ — 223 files (process record)`, a fresh render says **224** (`git ls-files docs | wc -l` = 224). Cause: `docs/verification/spec-interview-protocol.md` was added by `b3df25c` after the last map regeneration (`8ec73ee`). CI could not have caught it — the `tests` job's `paths:` filter in `spec-validation.yml` omits `docs/todo/**` and `docs/questions/**`, and there is no CI map job (ADR-085/AC-023). This change adds `docs/verification/complexipy-scripts.md` and edits `scripts/*.py`, so it must regenerate the map anyway.
- **Question:** how is the GREEN baseline established — (a) regenerate `STRUCTURE.md` as the first commit of this change and record the pre-existing red in the baseline; (b) split the one-line map refresh into a separate ISSUE change that lands first; (c) reclassify/stop?
- **Recommended:** (a) — regenerate `STRUCTURE.md` in this change's first commit and record the pre-existing failure in `docs/verification/complexipy-scripts.md`; the map is stale by exactly one generated line, this change has to regenerate it regardless, and a separate ISSUE PR for a generated-file refresh costs more than it saves.
**Answer:** **(a) — record the baseline with the pre-existing red named, on re-measured facts.** Re-measured 2026-10-11 at `3980c14`: `uv run python scripts/make_map.py --check` exits **0** and the committed map is a fresh render (committed 2004 lines = fresh 2004), so the 223/224 count mismatch that made the P.2 baseline red is **already fixed** by `map-default-drop-shift` (MERGED, PRs #79/#80). The only remaining local failure is the CRLF byte diff in the same witness (**Q-02**). The baseline record states this so the change's own evidence stays distinguishable from the inherited failure.
- **Date:** 2026-10-11
- **Status:** ANSWERED
- **Incorporated:** yes — P.4 baseline record: full suite on `main` with one named host-dependent failure, CI/Linux run authoritative

## Q-02 — AC-021 can never pass on this Windows host (CRLF)
- **Step:** P.2 Interrogate
- **Why needed:** even after Q-01, the same witness fails locally for a second, independent reason, so "full suite GREEN" is unachievable on the host the agent runs on — the gate would be permanently unverifiable locally.
- **Context:** `git ls-files --eol STRUCTURE.md` → `i/lf w/crlf`, `core.autocrlf = true`, no `.gitattributes` exists in the repository. The working-tree map has 1941 CRLF pairs; `make_map.py` renders LF; AC-021 compares bytes, so it fails with `At index 22 diff: b'\r' != b'\n'` before the content difference is even reached. On Linux CI the same test fails only on the 223/224 count.
- **Question:** how should the baseline be established given the host-dependent failure — add a `.gitattributes` (e.g. `*.md text eol=lf`) inside this change, treat the CI (Linux) run as the authoritative GREEN gate and record the host caveat, switch the local checkout to `core.autocrlf=input`, or accept AC-021 as environment-blocked?
- **Recommended:** treat the CI/Linux run as authoritative and record the host caveat in the baseline; do **not** add `.gitattributes` here — it changes checkout behaviour repo-wide and is its own DOCS/CHORE change (open a TODO).
**Answer:** **Treat the CI (Linux) run as the authoritative GREEN gate and record the host caveat** — the recommendation. `git ls-files --eol STRUCTURE.md` is still `i/lf w/crlf` with `core.autocrlf=true` and no `.gitattributes`, so `test_ac_021_committed_map_matches_fresh_render` fails locally with `At index 22 diff: b'
' != b'
'` while the line counts are identical (2004 = 2004); measured 2026-10-11: `1 failed, 31 passed` in `tests/acceptance/test_structure_map.py`. **No `.gitattributes` in this change.** The TODO the recommendation asked for **already exists**: `docs/todo/gitattributes-line-endings.md` (DOCS/CHORE, PREPARING, 23 questions open), and it already names AC-021 as the witness it unblocks — the follow-up is recorded as satisfied, not re-opened. The baseline names the failure, its cause, and the TODO that owns the fix.
- **Date:** 2026-10-11
- **Status:** ANSWERED
- **Incorporated:** yes — P.4 baseline: host caveat + pointer to `gitattributes-line-endings`; no EOL policy change here

## Q-03 — Two of the three scripts have no tests: what witnesses the refactor?
- **Step:** P.2 Interrogate
- **Why needed:** REFACTOR's contract is "the existing suite is the contract, zero test changes" — but for `check_traceability.py` and `validate_task_dag.py` the suite contains no contract at all, and these two scripts are what CI uses to enforce traceability and DAG well-formedness. A silent behavior change here weakens the workflow's own gates.
- **Context:** measured — the only test references to the three scripts are in `tests/acceptance/test_structure_map.py` (`test_ac_025_mypy_covers_scripts`, `test_nfr_004_mypy_and_ruff_clean`, and the map-string at `:336`). Nothing exercises `check_traceability.py` or `validate_task_dag.py` behaviorally; CI runs the DAG validator with `|| true`, so even its exit code is advisory. Golden outputs today: `Traceability: PASS (881 matrix rows, 136 spec IDs, 801 test functions)`; `Task DAG validation PASSED: 7 tasks, acyclic, well-formed.`; `verify_spec.py docs/specs/structure-map.md` → `Traceability: PASS` — all exit 0.
- **Question:** what proves the refactor preserved behavior — (a) golden-output witnesses (run the three CI invocations before and after, byte-compare, record in `docs/verification/complexipy-scripts.md`, no test file added); (b) authorize **adding** a characterization test file (a test addition, which the REFACTOR "zero test changes" gate reads literally); (c) refuse to refactor the untested two and reclassify?
- **Recommended:** (a) — before/after byte-comparison of the real CI invocations is the smallest witness that fails if the logic breaks, and it keeps the REFACTOR gate literal; permanent characterization tests are a separate change the user can open as a TODO.
**Answer:** **(a) golden-output witnesses** — the recommendation. Before any restructuring, run the three CI invocations and record stdout + exit codes byte-for-byte in `docs/verification/complexipy-scripts.md`: `uv run python scripts/check_traceability.py` (→ `Traceability: PASS (881 matrix rows, 136 spec IDs, 801 test functions)`), `uv run python scripts/validate_task_dag.py` (→ `Task DAG validation PASSED: 7 tasks, acyclic, well-formed.`), `uv run python scripts/verify_spec.py docs/specs/structure-map.md`; re-run after the refactor and byte-compare. **No test file is added**, so the zero-test-changes contract holds literally. Because the type is now **DOCS/CHORE** (**Q-16**), this comparison is not decoration — it is the change's evidence that the required no-behavior-delta holds for the two scripts the suite does not cover.
- **Date:** 2026-10-11
- **Status:** ANSWERED
- **Incorporated:** yes — P.4 scope: golden-output pair recorded before/after in the verification artifact

## Q-04 — The approved spec and ADR-086 say the opposite of this change
- **Step:** P.2 Interrogate
- **Why needed:** widening the gate makes a sentence in an **approved** spec false and contradicts an ADR's explicit "do not widen" decision; AGENTS forbids leaving an approved spec contradicted without the Spec Amendment Workflow, and an agent may not edit `docs/specs/` on `main`.
- **Context:** `docs/specs/structure-map.md:479` NFR-005: "The new test files stay under `[tool.complexipy] max-complexity-allowed = 15` (`paths = ["src", "tests"]`); **`scripts/` is not analyzed by complexipy**." `docs/decisions/ADR-086-scripts-type-checked-tree.md:18` lists `complexipy (CI complexity) | paths = ["src","tests"] | widen: no`, and its frozen-scope section (quoted in `.github/task-runner/tasks.json:8`) says complexipy's scope is "unchanged by every task". The witness `test_nfr_005_complexipy_threshold_holds` pins `_COMPLEXIPY_PATHS = ("src","tests")` explicitly, so it keeps passing either way (measured: passes today).
- **Question:** does this change need a Spec Amendment PR for `structure-map.md` NFR-005 (the shape `map-default-drop-shift` used with PR A), a superseding ADR, both, or neither (NFR-005's normative clause is about that change's three test files and stays true; only its descriptive tail goes stale)?
- **Recommended:** a superseding ADR (next free number — ADR-087 unless an in-flight change claims it; numbering is by merge order) plus a note in `docs/verification/complexipy-scripts.md`; **no** spec amendment, because NFR-005's normative clause (the three structure-map test files stay under 15) is unchanged by this change.
**Answer:** **Both — amend NFR-005 in this change's PR and write a superseding ADR-087.** Re-measured 2026-10-11: `docs/specs/structure-map.md:486` NFR-005 still reads "`scripts/` is not analyzed by complexipy" and `docs/decisions/ADR-086-scripts-type-checked-tree.md:18` still says `complexipy (CI complexity) | paths = ["src","tests"] | widen: no`. NFR-005 is a spec line, so it is amended in place with a Changelog entry and flagged to the reviewer at the merge gate (the user's standing practice — `settings-coverage`, `logging-coverage`, `settings-public-registry-setter`, and `structure-map.md` NFR-002 v3 were all amended this way). ADR-086 is a frozen-scope **decision record** and cannot be edited in place, so **ADR-087** supersedes its complexipy row (numbering by merge order; re-check the next free number at P.4 — no in-flight change claims it today). The witness `test_nfr_005_complexipy_threshold_holds` pins `_COMPLEXIPY_PATHS = ("src","tests")` and is **not** weakened (**Q-12**).
- **Date:** 2026-10-11
- **Status:** ANSWERED
- **Incorporated:** yes — P.4 scope now includes `docs/specs/structure-map.md` NFR-005 + `docs/decisions/ADR-087-*.md`; the TODO's `Related specs: none` is corrected

## Q-05 — Where the widening lives: CI line, `[tool.complexipy] paths`, or both
- **Step:** P.2 Interrogate
- **Why needed:** the gate scope is written in two places and the TODO only names one; leaving the other stale re-creates exactly the config-vs-CI drift `pyproject-tooling-gaps` was created to close.
- **Context:** `pyproject.toml:99-101` `[tool.complexipy] paths = ["src","tests"]`, `max-complexity-allowed = 15`; `quality.yml:146` `uv run complexipy src tests --max-complexity-allowed 15`. Measured: positional args override the config `paths` (`uv run complexipy scripts` analyses only `scripts/`), and `uv run complexipy` with no args analyses `src`+`tests` and exits **0** today — i.e. a local run would still not see `scripts/` if only the CI line changes.
- **Question:** update the CI invocation only, `[tool.complexipy] paths` only, or both — and if both, does CI keep the explicit `src tests scripts` positional args or drop them and rely on the config?
- **Recommended:** both, with the positional args kept explicit in CI (`uv run complexipy src tests scripts --max-complexity-allowed 15`) — the config becomes the source of truth for a local `uv run complexipy`, and the explicit CI line stays loud on a bad config, as its comment intends.
**Answer:** **Both, with the CI positional args kept explicit** — the recommendation. `pyproject.toml:99-101` becomes `paths = ["src", "tests", "scripts"]` and `.github/workflows/quality.yml:146` becomes `uv run complexipy src tests scripts --max-complexity-allowed 15`. Measured: positional args override the config (`uv run complexipy scripts` analyses only `scripts/`), and a bare `uv run complexipy` analyses `src`+`tests` and exits 0 today — so a CI-only change would leave local runs blind to `scripts/`, and a config-only change would leave the CI comment "repeated here so CI fails loudly on a bad config" false and re-create exactly the config-vs-CI drift `pyproject-tooling-gaps` was created to close.
- **Date:** 2026-10-11
- **Status:** ANSWERED
- **Incorporated:** yes — P.4 scope: both files, CI args explicit

## Q-06 — Sequencing and collision with `map-default-drop-shift`
- **Step:** P.2 Interrogate
- **Why needed:** the two changes both rewrite `STRUCTURE.md`, and the other change is at a human gate; the answer decides whether P.4 runs now or waits, and how the conflict is resolved.
- **Context:** `git worktree list` shows two in-flight worktrees. `issue/map-default-drop-shift` (TODO `Status: WAITING`, PR #79 open) diffs `STRUCTURE.md`, `docs/specs/structure-map.md`, `docs/verification/map-default-drop-shift.md`; its ISSUE PR will edit `scripts/make_map.py` + `STRUCTURE.md`. This change regenerates `STRUCTURE.md` (map obligation, Q-14) but touches none of `make_map.py`'s functions. The TODO's own `Depends on:` says "none hard; sequenced after `map-default-drop-shift`". `crosscut/settings-public-registry-setter` edits `pyproject.toml` at `[tool.ruff.lint]` (192-226), not `[tool.complexipy]` (99-101).
- **Question:** create the worktree now from `main` and regenerate the map at PR-open time (AGENTS: on a `STRUCTURE.md` conflict take either side and regenerate), or hold P.4 until both `map-default-drop-shift` PRs merge?
- **Recommended:** proceed to P.4 now — the four functions are disjoint from `make_map.py`, and `STRUCTURE.md` is a generated file that is regenerate-on-conflict, so waiting buys nothing while the change sits behind a human gate.
**Answer:** **Proceed to P.4 now** — the recommendation, on the re-measured picture. Both collisions P.2 named have since **merged**: `map-default-drop-shift` (PRs #79/#80 — it edited `scripts/make_map.py` and amended NFR-002 to 2 200 lines) and `settings-public-registry-setter` (PR #81). `git worktree list` at `3980c14` shows **only the primary worktree**, so there is no parallel edit of `scripts/` or of `pyproject.toml`'s `[tool.complexipy]` block. P.4 creates `chore/complexipy-scripts` (**Q-16**) from `main`; this change touches none of `make_map.py`'s functions, and `STRUCTURE.md` is a generated file that is regenerate-on-conflict (**Q-14**), so waiting behind the two open changes buys nothing.
- **Date:** 2026-10-11
- **Status:** ANSWERED
- **Incorporated:** yes — TODO `Depends on:` rewritten to 'none hard — sequenced after the merged map-default-drop-shift'

## Q-07 — What counts as "behavior" for a CLI script: exit codes only, or stdout byte-for-byte
- **Step:** P.2 Interrogate
- **Why needed:** the refactor's correctness criterion depends on it — one natural rewrite of `check_acyclic` changes the output, and the answer decides whether that rewrite is legal.
- **Context:** `check_acyclic` short-circuits: it returns after the **first** cycle found (`return True`) and prints one `Cycle detected: A -> B -> A` line; collecting all cycles instead would change stdout. `check_traceability.check` emits messages in a fixed order (missing row → undefined ID → missing test → undeclared Status). `verify_spec.main`'s report is already pinned byte-for-byte for `docs/specs/template.md` by AC-025's `_VERIFY_SPEC_REPORT_BEFORE_FIX`.
- **Question:** must stdout (text, order, and `check_acyclic`'s first-cycle-only semantics) be preserved exactly, or only the exit codes?
- **Recommended:** preserve stdout exactly — exit codes plus message text and order, first-cycle-only included; CI logs are read by humans and one acceptance witness already compares a report byte-for-byte, so byte-identity is the observable contract this repo has already adopted.
**Answer:** **stdout byte-identical** — the recommendation. The observable contract is exit codes **plus** message text and order, including `check_acyclic`'s first-cycle-only short-circuit (it returns after the first cycle and prints one `Cycle detected: A -> B -> A` line). Consequences: the "collect all cycles" rewrite of `check_acyclic` is **not** legal under this change (it changes stdout), `check`'s fixed message order (missing row → undefined ID → missing test → undeclared Status) is frozen, and `verify_spec.main`'s report stays byte-identical to the `_VERIFY_SPEC_REPORT_BEFORE_FIX` string already pinned by AC-025. Rationale the user accepted: CI logs are read by humans, and this repo has already adopted byte-identity as the contract for these scripts.
- **Date:** 2026-10-11
- **Status:** ANSWERED
- **Incorporated:** yes — P.4 scope: byte-identity is the refactor's correctness criterion; the Q-03 golden outputs are the comparison basis

## Q-08 — Fix the root cause of the stale map here, or open a TODO
- **Step:** P.2 Interrogate
- **Why needed:** the red baseline in Q-01 is a symptom of a mechanism that will redden `main` again on the next planning-record commit; whether it is in scope changes this change's file list.
- **Context:** the staleness came from a `docs/` commit that did not regenerate the map, and CI cannot see it: `spec-validation.yml`'s `tests` job `paths:` filter omits `docs/todo/**` and `docs/questions/**`, and ADR-085/AC-023 record that **no** CI job runs `make_map.py --check` (the check is a local pre-commit hook only). AGENTS already requires regenerating the map in the same commit as a `.py` change — but a planning-record commit is not a `.py` change.
- **Question:** fix it inside this change (add `docs/**` to the `tests` job `paths:` filter, add a CI `make_map.py --check` job, or extend the AGENTS regeneration rule to planning records), or open a new TODO and keep this change to the four refactors?
- **Recommended:** open a new TODO (ISSUE: "the committed map can go stale undetected") and keep this change in scope — a CI map job contradicts ADR-085/AC-023 and an AGENTS rule change is governance, not a refactor.
**Answer:** **Accept the risk — fix nothing and open nothing** (against the recommendation). The map is fresh on `main` today (`make_map --check` exits 0) and the `mkdocs-build`/map pre-commit hook covers `.py` commits, so the user takes the residual risk rather than widening CI trigger scope in a change whose **Q-17** boundary excludes CI map work. Recorded honestly as a real ceiling: the mechanism is still open — `spec-validation.yml`'s `tests` job `paths:` filter omits `docs/todo/**` and `docs/questions/**`, and ADR-085/AC-023 record that **no** CI job runs `make_map.py --check`, while AGENTS' regeneration rule is scoped to `.py` changes, so a planning-record commit that adds a `docs/` file can redden `test_ac_021_committed_map_matches_fresh_render` on `main` undetected until the next full-suite run. Upgrade path if it bites: an ISSUE TODO for the CI trigger scope, or a CI map-check job (which would need an ADR superseding ADR-085 alongside **ADR-087**).

## Q-09 — Refactor style: pure extraction, or algorithm rewrite
- **Step:** P.2 Interrogate
- **Why needed:** it decides how much of the stdout contract (Q-07) has to be argued for, and how large the diff is.
- **Context:** reductions needed to reach 15: `check` −2, `matrix_rows` −4, `check_acyclic` −7, `verify_spec.main` −7. The hot structures are: four independent check loops in `check`; a table scanner with a nested `flush` closure in `matrix_rows`; a graph build plus a recursive `dfs` closure in `check_acyclic`; setup + input checks + report printing in `verify_spec.main`. `scripts/make_map.py` already shows the house style: 30 small module-level `_`-helpers, max 12.
- **Question:** extraction only (move the nested closures and loops into module-level helpers), or is an algorithmic rewrite allowed (iterative DFS, table-driven check lists, a report-rendering data structure)?
- **Recommended:** extraction first, rewrite only if extraction cannot reach the target — extraction keeps stdout provably identical, and the recursion depth is irrelevant at 7 tasks (measured), so the iterative DFS buys nothing here.
**Answer:** **Algorithmic rewrite allowed** (against the recommendation). The refactor may replace the structures, not just relocate them: an iterative DFS in `check_acyclic`, a table-driven list of check rules in `check_traceability.check`, a report-rendering data structure in `verify_spec.main`. The constraint that still binds is **Q-07**: stdout must stay **byte-identical** (text, order, and `check_acyclic`'s first-cycle-only semantics), so a rewrite that changes what is printed — e.g. reporting all cycles instead of the first — is out. The **Q-03** golden-output byte comparison is what proves the rewrite preserved behavior, and the **Q-13** target is <= 12, so the rewrite must actually reduce complexity rather than move it. Rationale the user accepted: extraction alone may not reach 12 from 22, and byte-identity of output — not the shape of the code — is the contract.

## Q-10 — Helper placement and naming
- **Step:** P.2 Interrogate
- **Why needed:** the refactor necessarily introduces helpers; where they live decides whether new files appear and how the generated map changes.
- **Context:** nothing imports these modules (`src/`, `tests/`, `scripts/`, `.github/` searched) — they are invoked as programs by CI and by one subprocess in `test_ac_025`. `make_map.py` uses module-level `_`-prefixed helpers; ruff `D` is per-file-ignored for `scripts/*`, so helpers need no docstring (a *why* docstring is still expected in review); `mypy scripts/` is a gate, so every helper needs full annotations (`disallow_untyped_defs = true`).
- **Question:** same-module `_`-prefixed helpers, a shared `scripts/_common.py`, or public (ununderscored) helpers?
- **Recommended:** same-module `_`-prefixed helpers — no new file, no shared module for three unrelated CLIs to invent, and the `STRUCTURE.md` Packages diff stays minimal.
**Answer:** **Public (ununderscored) module-level helpers** (against the recommendation). The new helpers are public names in their own module, so `STRUCTURE.md` lists them in the Packages section as public API and a later change may import them. Consequences accepted: the generated map grows by one header + signature line per helper (headroom is **196** lines after the NFR-002 amendment to 2 200 — see **Q-14**), and `mypy scripts/` (`disallow_untyped_defs = true`) requires full annotations on every helper. Still **no `scripts/_common.py`** — three unrelated CLIs do not invent a shared module — and ruff `D` stays per-file-ignored for `scripts/*`, so a *why* docstring is a review expectation, not a lint gate. Divergence from `make_map.py`'s `_`-prefixed house style is accepted deliberately.

## Q-11 — May existing function names and signatures change?
- **Step:** P.2 Interrogate
- **Why needed:** the TODO allows signature changes ("acceptable only because nothing imports them") but the generated map and an approved spec's prose both name the current ones.
- **Context:** `STRUCTURE.md` lists `spec_files`, `defined_ids`, `test_names`, `matrix_rows`, `check`, `main`, `load_tasks`, `check_well_formed`, `check_acyclic`, `check_sync`, `parse_spec`, `find_test_functions`, `check_traceability`; `docs/specs/structure-map.md:576,585` describes `check_traceability.py`'s behavior in prose. No caller imports them (Q-10 context).
- **Question:** may the refactor rename or re-signature the existing public functions (e.g. `check` → `_check_rows`, `check_acyclic(tasks)` → `check_acyclic(graph)`), or must every current name and signature stay?
- **Recommended:** keep every existing name and signature and add helpers only — renaming churns the generated map and an approved spec's prose for zero behavioral gain.
**Answer:** **Renaming and re-signaturing are allowed** (against the recommendation). Verified 2026-10-11 that this is cheaper than P.2 assumed: **no** file under `docs/specs/` or `docs/decisions/` names any of these functions — `docs/specs/structure-map.md` §12 describes `check_traceability.py`'s *behavior* in prose without naming `matrix_rows`, `check`, `check_acyclic`, `parse_spec`, `find_test_functions` or `check_well_formed`. So the only artifact that changes is the generated `STRUCTURE.md` signature list, regenerated in the same commit (**Q-14**). Nothing imports these modules (`src/`, `tests/`, `scripts/`, `.github/` searched; `test_ac_025` invokes them as subprocesses), so no caller breaks. Combined with **Q-10**, the module surface after the refactor is whatever reads best, not the current name set.

## Q-12 — Is there a witness that the gate stays widened?
- **Step:** P.2 Interrogate
- **Why needed:** after this change nothing in the test suite forces `scripts/` to stay inside the complexity gate, and adding such a witness is a test addition under a REFACTOR gate that reads "zero test changes".
- **Context:** `test_nfr_005_complexipy_threshold_holds` deliberately pins `_COMPLEXIPY_PATHS = ("src","tests")` and would not notice the CI line regressing (measured: it passes today and keeps passing after the widening). The only enforcement is the `complexity` job in `quality.yml` (a hard gate — no `continue-on-error`) plus `[tool.complexipy] paths`.
- **Question:** add a witness for the gate scope (e.g. an acceptance test asserting the `complexity` job line and `[tool.complexipy] paths` both include `scripts`), or rely on the CI job itself?
- **Recommended:** rely on the CI job — no new test; a test that asserts a config string duplicates the gate it is meant to protect and would sit awkwardly beside structure-map's NFR-005 witness.
**Answer:** **Rely on the CI job — no new test** — the recommendation. Enforcement is the `complexity` job in `.github/workflows/quality.yml` (a hard gate, no `continue-on-error`) plus `[tool.complexipy] paths` (**Q-05**). A test that asserts a config string duplicates the gate it is meant to protect, and under the **Q-16** DOCS/CHORE type Phase 5 must confirm **no test file was touched** — so adding one would contradict the chosen type. The existing witness `test_nfr_005_complexipy_threshold_holds` keeps pinning `_COMPLEXIPY_PATHS = ("src","tests")` and is neither weakened nor amended (its spec line NFR-005 is amended at **Q-04**, but the test stays as written and keeps passing). Noted for the record: a config-contract test would have precedent in `tests/contract/singleton_install/test_lint_contract.py`, which reads `pyproject.toml` as data — the user declined it here.

## Q-13 — Target margin below the ceiling
- **Step:** P.2 Interrogate
- **Why needed:** it decides how far the refactors go and whether the next edit to these scripts reddens CI.
- **Context:** complexipy passes a function at exactly 15 (measured: `tests/acceptance/test_structure_map.py::test_ac_008_document_shape` = **15 PASSED**). The four offenders are 17/19/22/22. `make_map.py`, written under the same house style, tops out at 12. `pyproject-tooling-gaps` (MERGED) fixed 10 offenders rather than raise the ceiling, and rejected the snapshot ratchet.
- **Question:** refactor to ≤ 15 (the minimum that passes), or to a margin such as ≤ 12?
- **Recommended:** ≤ 12 — a function parked at exactly 15 is one `if` away from a red gate, and the extra extraction is a few lines; it also matches `make_map.py`, the only `scripts/` file written under the gate.
**Answer:** **<= 12** — the recommendation. The four offenders (17 / 19 / 22 / 22) are refactored to at most 12, matching `scripts/make_map.py`, the only `scripts/` file written under the gate (measured max 12). complexipy passes a function at exactly 15 (`tests/acceptance/test_structure_map.py::test_ac_008_document_shape` = 15 PASSED), so a function parked at 15 is one `if` from a red gate; the margin also absorbs the **Q-18** rescoring risk. `pyproject-tooling-gaps` set the precedent by fixing 10 offenders rather than raising the ceiling.
- **Date:** 2026-10-11
- **Status:** ANSWERED
- **Incorporated:** yes — P.4 done-criteria: every function in the three scripts scores <= 12, not merely <= 15

## Q-14 — Generated-artifact obligation and the map's line budget
- **Step:** P.2 Interrogate
- **Why needed:** every refactor step changes `STRUCTURE.md` (line counts plus one Packages line per new helper), and the map has a hard ceiling enforced by an acceptance test.
- **Context:** `STRUCTURE.md` is **1941** lines against NFR-002's ≤ 2 000 ceiling (`test_nfr_002_map_line_budget`); the `scripts/` block currently lists 4 modules with their function signatures (`check_traceability.py` 153 lines, `make_map.py` 567, `validate_task_dag.py` 134, `verify_spec.py` 123). AGENTS and the `code-structure-map` skill require regeneration in the same commit as the `.py` change; there is no CI map job (ADR-085). This change also adds `docs/verification/complexipy-scripts.md`, which moves the `docs/` file count again.
- **Question:** confirm the map is regenerated in the same commit as each `.py` commit (headroom ≈ 59 lines for ~10 new helper lines plus the docs count), or should the change also shrink the map to buy headroom?
- **Recommended:** regenerate per commit and do not shrink the map — ~10 helper lines fit the 59-line headroom; if the budget is ever tight, that is structure-map's problem, not this change's.
**Answer:** **Regenerate per commit, do not shrink the map** — the recommendation, on corrected facts. `STRUCTURE.md` is regenerated with `uv run python scripts/make_map.py` in the same commit as each `scripts/*.py` commit (AGENTS + the `code-structure-map` skill). Re-measured 2026-10-11: the map is **2004** lines and `structure-map.md` **NFR-002 was amended to <= 2 200** by `map-default-drop-shift` (spec v3, `docs/specs/structure-map.md:483`), so headroom is **196 lines**, not the ~59 P.2 recorded — the public helpers (**Q-10**) and any renamed signatures (**Q-11**) fit with room to spare. The `scripts/` block currently lists 4 modules with their signatures (`check_traceability.py` 153, `make_map.py` 581, `validate_task_dag.py` 134, `verify_spec.py` 123 lines). `docs/verification/complexipy-scripts.md` also moves the `docs/` file count, which is why the map is regenerated in the same commit as the artifact's own commit. Shrinking the map (e.g. the REQ-017 field cap) stays out of scope (**Q-17**).

## Q-15 — Traceability matrix: rows or none
- **Step:** P.2 Interrogate
- **Why needed:** the state machine says an agent must not move GREEN → VERIFIED without updating the traceability matrix, but REFACTOR's Phase 5 list does not mention it, and this change defines no normative IDs.
- **Context:** the `traceability` CI job (`scripts/check_traceability.py`) enforces referential integrity only and passes today (881 rows / 136 spec IDs / 801 test functions); Convention B makes each row a historical record written by the change that owns the IDs. No `REQ-XXX`/`AC-XXX` is defined by this change.
- **Question:** add matrix row(s) recording this change's evidence, or leave `docs/verification/traceability.md` untouched and keep the evidence in `docs/verification/complexipy-scripts.md`?
- **Recommended:** leave the matrix untouched — a row without a normative ID is exactly what `check_traceability.py` cannot police and what Convention B does not need.
**Answer:** **No matrix rows** — the recommendation. `docs/verification/traceability.md` is left untouched; the evidence lives in `docs/verification/complexipy-scripts.md` (baseline, golden outputs before/after, complexipy scores before/after). This change defines no `REQ-XXX`/`AC-XXX`, `scripts/check_traceability.py` polices referential integrity only (it passes today: 881 matrix rows, 136 spec IDs, 801 test functions), and Convention B makes each row a historical record written by the change that owns the IDs — a row without a normative ID is exactly what the checker cannot police. The amended **NFR-005** wording (**Q-04**) does not get a row either: `NFR` rows are not required by the checker, and its existing witness row in `docs/specs/structure-map.md:575` is unchanged.

## Q-16 — Classification and branch prefix: REFACTOR or the `chore/` name Q-19 recorded
- **Step:** P.2 Interrogate
- **Why needed:** the records disagree, and the type decides the gates (GREEN baseline, full regression, zero test changes) and the branch name created at P.4.
- **Context:** P.1 classified **REFACTOR** (first-match #4). `docs/questions/map-default-drop-shift.md` Q-19 recorded the follow-up as `chore/complexipy-scripts`. The CI/config half of the change is chore-shaped (`quality.yml`, `pyproject.toml`), the four function bodies are restructures. Bump mapping: REFACTOR and DOCS/CHORE both → **no version bump**.
- **Question:** confirm REFACTOR (branch `refactor/complexipy-scripts`), or reclassify to DOCS/CHORE (branch `chore/complexipy-scripts`) with the refactors riding along?
- **Recommended:** REFACTOR — four function bodies are restructured (criterion #4 matches before #5), and the stricter gates (GREEN baseline, full regression, zero test changes) are exactly the protection these CI-critical scripts need; the `chore/` label in Q-19 was written before P.1 classified it.
**Answer:** **DOCS/CHORE** (against P.1's REFACTOR and against the recommendation) — branch **`chore/complexipy-scripts`**. The gate-widening is the point of the change and the four function refactors exist only to satisfy it, so it classifies by criterion #5 (does not alter externally observable behavior) rather than #4. Consequences, all accepted: **Phase 3 is skipped** (no RED); **no GREEN baseline is required** to enter Phase 4 (the **Q-01** baseline is still recorded, as evidence rather than as a gate); **Phase 5 is the light tier** — `uv run ruff check .`, `uv run mypy scripts/`, and confirmation that no test file or behavior was touched; **Phase 6 is a light review**; **no version bump** (unchanged — both types map to none). The trade-off the user accepted: REFACTOR's full-regression gate is dropped, so the **Q-03 golden-output comparison is the primary no-behavior-delta evidence**, and the `Depends on:` sequencing note is what protects `scripts/make_map.py` in place of the suite. The `chore/` label recorded in `map-default-drop-shift` Q-19 is now authoritative.
- **Date:** 2026-10-11
- **Status:** ANSWERED
- **Incorporated:** yes — TODO `Change type:` → DOCS/CHORE, worktree path → `chore/complexipy-scripts`, Phase Matrix gates recorded

## Q-17 — Non-goals: confirm the boundary (mandatory)
- **Step:** P.2 Interrogate
- **Why needed:** the ceiling and the gate scope are one knob each, and the tree is full of near-misses an agent could pull into this change; the boundary must be explicit before P.4 writes the scope.
- **Context:** concrete near-misses measured at `be1eb5a`: `test_ac_008_document_shape` = **15** (exactly at the ceiling), `_feature_logger_names` 14, `test_inv_004_other_loggers_untouched` 14, `test_concurrent_thread_safe` 14, `SearchService::search` 13, `SettingsRegistry::create_template` 13; `scripts/make_map.py` max 12 and owned by `map-default-drop-shift`; coverage stays `source = ["src/backend","src/frontend"]` with `fail_under = 92` (ADR-086 freezes it); bandit `-r src/`; `ty` `root = ["./src"]`; `migrations/` and `.github/` are analyzed by no complexity gate at all; complexipy is a dev-group dependency (`pyproject.toml:38`) with its own dependabot group (`dependabot.yml:15`).
- **Question:** confirm all of these are **out** of scope: raising or parameterising the 15 ceiling; a per-file carve-out or complexipy snapshot; refactoring the `src/`/`tests/` functions at 13–15 listed above; touching `scripts/make_map.py`; adding new scripts; widening coverage/bandit/ty/mypy to `scripts/`; adding a CI map job (Q-08); pinning or downgrading complexipy (Q-18).
- **Recommended:** all out — the change is exactly "four functions under the ceiling plus the gate-scope lines"; each near-miss is either another change's file or a decision (`ceiling`, `snapshot`) that `pyproject-tooling-gaps` already rejected once.
**Answer:** **All confirmed out** — the recommendation, with the EOL item added because **Q-02** raised it. Out of scope: raising or parameterising the `15` ceiling; a per-file carve-out or complexipy snapshot; refactoring the near-miss functions measured at `3980c14` (`test_ac_008_document_shape` = 15, `_feature_logger_names` = 14, `test_inv_004_other_loggers_untouched` = 14, `test_concurrent_thread_safe` = 14, `SearchService::search` = 13, `SettingsRegistry::create_template` = 13); touching `scripts/make_map.py` (owned by the merged `map-default-drop-shift`, max 12 today); adding new scripts; widening coverage (`source = ["src/backend","src/frontend"]`, `fail_under = 92`, frozen by ADR-086), bandit (`-r src/`), `ty` (`root = ["./src"]`) or mypy beyond `scripts/`; a CI map job (**Q-08**); pinning or downgrading complexipy (**Q-18**); and any `.gitattributes` / line-ending change (**Q-02**, owned by `gitattributes-line-endings`). In scope: the two gate-scope lines (**Q-05**), the four function refactors to <= 12 (**Q-13**), the NFR-005 amendment + ADR-087 (**Q-04**), the golden-output evidence (**Q-03**), and the `STRUCTURE.md` regeneration (**Q-14**).
- **Date:** 2026-10-11
- **Status:** ANSWERED
- **Incorporated:** yes — P.4 scope boundary recorded verbatim in docs/verification/complexipy-scripts.md

## Q-18 — complexipy version drift against a widened scope
- **Step:** P.2 Interrogate
- **Why needed:** widening the gate adds 49 functions whose scores depend on a tool dependabot updates; the engine has already changed scoring once.
- **Context:** `complexipy>=8.0.1` (dev group) with a dependabot entry (`dependabot.yml:15`). `pyproject-tooling-gaps` P.2 measured the engine difference concretely: v5.1.0 scored `test_inv_003_last_admin_invariant` **20 PASSED**, 8.0.1 scored it **38 FAILED** — same code, different numbers. Today `scripts/` has 49 analysed functions, 4 over 15.
- **Question:** accept the drift (no pin, fix forward if a rescore reddens `scripts/`), or pin complexipy / record a ratchet?
- **Recommended:** accept — the repo already chose one engine (`>=8.0.1`) and rejected snapshots; a rescore that pushes a ≤12 function over 15 is a tooling event that deserves its own TODO, not a pin in this change.
**Answer:** **Accept the drift** — the recommendation. No pin, no snapshot, no ratchet baseline. `complexipy>=8.0.1` stays as a dev-group dependency (`pyproject.toml:38`) with its dependabot entry (`dependabot.yml:15`) intact. The scoring engine has already moved once (measured by `pyproject-tooling-gaps`: v5.1.0 scored `test_inv_003_last_admin_invariant` 20 PASSED, 8.0.1 scored it 38 FAILED — same code, different numbers), and today `scripts/` has 49 analysed functions with 4 over 15. The **Q-13** <= 12 target is the mitigation: a modest rescore cannot push a <= 12 function over 15. If a dependabot bump does redden `scripts/`, that is a tooling event that gets its own TODO, not a pin retrofitted into this change. `pyproject-tooling-gaps` already rejected a snapshot ratchet, so this is consistent with the existing decision.

### Category coverage

| Category | Result |
|---|---|
| Environment & baseline (can the REFACTOR gate be met at all) | covered (Q-01, Q-02) |
| Testing & witnesses (what proves behavior was preserved) | covered (Q-03, Q-12, Q-15) |
| Specified vs unspecified contract (approved spec/ADR statements) | covered (Q-04) |
| Tooling & gate configuration (where the gate lives, ceiling, drift) | covered (Q-05, Q-13, Q-18) |
| Sequencing & merge conflicts (other in-flight/backlog changes) | covered (Q-06, Q-08) |
| Behavior preservation (stdout/exit-code contract, refactor style) | covered (Q-07, Q-09, Q-11) |
| Naming & module boundaries (helpers, signatures) | covered (Q-10, Q-11) |
| Generated artifacts (`STRUCTURE.md` regeneration, NFR-002 budget) | covered (Q-14, Q-08) |
| Interfaces (the scripts' CLI contract: argv, exit codes, stdout) | covered (Q-07, Q-11) |
| Scope & boundaries / non-goals | covered (Q-17, Q-08) |
| Versioning & governance (type, branch, bump) | covered (Q-16) |
| Data & state | skipped — the three scripts are stateless readers of repository text files; no schema, database, or persisted state is touched (no SQLModel/alembic import anywhere in `scripts/`) |
| Performance | skipped — measured runtimes 0.09–0.17 s and no performance requirement exists; extraction only moves code |

## Late questions (Phases 2–6)

_none_
