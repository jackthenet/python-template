# complexipy-scripts — Scope Record (DOCS/CHORE)

- **Change:** complexipy-scripts
- **Type:** **DOCS/CHORE** — reclassified at **P.3 Q-16** (2026-10-11) from P.1's REFACTOR. One-line reason: the
  gate widening is the point of the change and the four function restructures exist only to satisfy it, so
  Change Types criterion **#5** ("does not alter externally observable behavior") matches before **#4**.
  Escalation Rules applied; the branch prefix `chore/` recorded in `map-default-drop-shift` Q-19 is authoritative.
- **Branch / worktree:** `chore/complexipy-scripts` @ `eddf94f` (== `main` at P.4, 2026-10-11), worktree
  `../python-template_kopie-worktrees/chore/complexipy-scripts`
- **Base commit:** `eddf94f` (`docs(startup-settings-registration-gaps): status WAITING — LQ-01 …`)
- **Version:** `1.2.0` (`pyproject.toml:4`) — **no bump** (AGENTS.md Versioning: DOCS/CHORE → none; Q-16)
- **Phase Matrix for this type:** Phase 1 scope (this file, at P.4) · **Phase 2/3 skipped** (no ADR-driven DAG,
  no RED) · Phase 4 make the scoped non-behavior changes · Phase 5 **light** gate · Phase 6 **light** review + PR.
  No spec, no spec PR, no version bump.
- **Question file:** `docs/questions/complexipy-scripts.md` — Q-01 … Q-18, all `ANSWERED` (5 rounds, 2026-10-11).
  Where an answer went against the step's recommendation, the **answer** governs this scope: Q-16 (DOCS/CHORE),
  Q-09 (algorithmic rewrite allowed), Q-10 (public helpers), Q-11 (renaming allowed), Q-13 (target ≤ 12),
  Q-04 (spec amendment **and** ADR-087), Q-08 (accept the stale-map risk).
- **Date:** 2026-10-11 (P.4)

## Phase 0 — classification: DOCS/CHORE

First matching criterion (#5): the change **does not alter externally observable behavior**. It edits two
gate-scope lines (`pyproject.toml` `[tool.complexipy] paths`, the CI `complexipy` invocation), amends one spec
line and adds one decision record, and restructures four function bodies in three repository-tooling scripts
under a **byte-identical stdout + exit-code contract** (Q-07). No CLI argument, no exit code, no printed
message, no detection rule changes; nothing in `src/`, `tests/` or any runtime path is touched.

Not **REFACTOR** (criterion #4): the restructures are instrumental — the change exists to widen the gate, and
its own acceptance signal is the gate scope plus the scores. Consequences accepted at Q-16: Phase 3 is skipped
(no RED), **no GREEN baseline is required to enter Phase 4** (the §Baseline below is recorded as evidence, not
as an entry gate), Phase 5 is the light tier, Phase 6 is a light review, no bump. The trade-off the user
accepted: REFACTOR's full-regression gate is dropped, so the **golden-output byte comparison (§Golden-output
baseline) is the primary no-behavior-delta evidence**.

## Fresh measurement (2026-10-11, this worktree, base `eddf94f`)

All figures below were re-measured in this worktree, not copied from the TODO or the question file.

### Complexity gate today

- `pyproject.toml:99-101` — `[tool.complexipy] paths = ["src", "tests"]`, `max-complexity-allowed = 15`.
- `.github/workflows/quality.yml:145-146` — the `complexity` job runs
  `uv run complexipy src tests --max-complexity-allowed 15` (hard gate, no `continue-on-error`); its comment
  says the threshold "lives in `[tool.complexipy]` and is repeated here so CI fails loudly on a bad config".
- `uv run complexipy scripts --max-complexity-allowed 15` → **exit 1**, **50 functions analysed**, **4 FAILED**:

| File | Function | Score | Target (Q-13) | Reduction |
|---|---|---|---|---|
| `scripts/check_traceability.py` | `check` | **17** | ≤ 12 | −5 |
| `scripts/check_traceability.py` | `matrix_rows` | **19** | ≤ 12 | −7 |
| `scripts/validate_task_dag.py` | `check_acyclic` | **22** | ≤ 12 | −10 |
| `scripts/verify_spec.py` | `main` | **22** | ≤ 12 | −10 |

- Every other function in the three scripts already passes at ≤ 12, so the four above are the **whole** refactor
  set. Full per-file scores (nested closures are scored inside their enclosing function):
  - `check_traceability.py` (6): `defined_ids` 1, `test_names` 1, `spec_files` 2, `main` 6, `check` 17 ✗, `matrix_rows` 19 ✗
  - `validate_task_dag.py` (5): `load_tasks` 0, `main` 6, `check_well_formed` 8, `check_sync` **12**, `check_acyclic` 22 ✗
  - `verify_spec.py` (4): `parse_spec` 0, `check_traceability` 10, `find_test_functions` 10, `main` 22 ✗
- `scripts/make_map.py` is **clean** — 35 functions, max **12** (`_member_lines`), `_drop_long_defaults` 4. It is
  not in scope (TODO/Out of scope; owned by the merged `map-default-drop-shift`).
- `uv run complexipy src tests --max-complexity-allowed 15` → **exit 0**; bare `uv run complexipy` → **exit 0**
  and byte-identical stdout to the CI form (187 539 bytes) — i.e. the config-driven local run is blind to
  `scripts/` today, which is exactly the gap Q-05 closes by widening **both** places.
- Highest passing score anywhere in `scripts/` is **12** (`make_map.py::_member_lines`,
  `validate_task_dag.py::check_sync`) — the Q-13 target is the house maximum, not an invented number.

### Map and baseline state

- `uv run python scripts/make_map.py --check` → **exit 0** (the committed map is fresh modulo line endings).
- `STRUCTURE.md` = **2 004** lines; `docs/specs/structure-map.md` NFR-002 ceiling = **2 200** (v3 amendment) →
  headroom **196 lines** for the new public helper signatures (Q-10, Q-14).
- The map's `docs/ — 234 files (process record)` line (`STRUCTURE.md:477`, `git ls-files docs | wc -l` = 234)
  moves to **235** with this record and **236** with ADR-087 — the file count changes, the line count of the map
  does not. The Packages-section growth comes only from the new/renamed `scripts/*.py` signatures.
- `uv run ruff check .` → **All checks passed!**; `uv run ruff format --check .` → **362 files already formatted**;
  `uv run mypy scripts/` → **Success: no issues found in 4 source files**. The base tree is clean on every gate
  this change's Phase 5 re-runs.
- §Baseline caveat below records the one host-dependent test failure.

## Golden-output baseline (captured BEFORE any restructuring — the primary no-behavior-delta evidence, Q-03)

`check_traceability.py` and `validate_task_dag.py` have **no behavioral tests**; `verify_spec.py` has exactly one
pinned output (`test_ac_025_mypy_covers_scripts`, which compares the `docs/specs/template.md` report byte-for-byte
against `_VERIFY_SPEC_REPORT_BEFORE_FIX`). Because the type is DOCS/CHORE (Q-16) the full-regression gate REFACTOR
would have imposed is replaced by this byte comparison, so it is captured at P.4, before a single line moves.

### Where the capture lives (outside every worktree)

- Scratch root: `C:/workspace/active-projects/complexipy-scratch/` — **outside** the repository and outside
  `python-template_kopie-worktrees/`. Nothing is ever written inside a worktree: a stray file there breaks
  `uv run python scripts/make_map.py --check` (the map would have to list it) and
  `tests/acceptance/test_structure_map.py` witnesses (Problem Log lesson).
- Capture script: `C:/workspace/active-projects/complexipy-scratch/capture.sh` —
  `bash capture.sh <worktree-dir> <out-dir>`; it runs every invocation below and writes
  `<name>.stdout`, `<name>.stderr`, `<name>.exit` into `<out-dir>`, then prints a size + sha256 manifest.
- Baseline directory: `C:/workspace/active-projects/complexipy-scratch/golden-before/` (21 files), manifest
  `C:/workspace/active-projects/complexipy-scratch/MANIFEST-before.txt` (2 382 bytes,
  sha256 `ed053acfd0f6fee8d732300ab13eb7aca6d9ea970e9f0be9fba4d067d695b36b`).
- Reproduce the baseline at any time with
  `bash capture.sh /c/workspace/active-projects/python-template_kopie-worktrees/chore/complexipy-scripts /c/workspace/active-projects/complexipy-scratch/golden-before`
  (run from the base commit `eddf94f` state).

### The invocations, exactly as CI runs them

| Witness | CI source | Command |
|---|---|---|
| `check_traceability` | `.github/workflows/spec-validation.yml:68` (`traceability` job, hard gate) | `uv run python scripts/check_traceability.py` |
| `validate_task_dag` | `.github/workflows/spec-validation.yml:54` (`spec-validation` job; exit code discarded by `\|\| true`, stdout surfaced in the job log) | `uv run python scripts/validate_task_dag.py .github/task-runner/tasks.json` |
| `verify_spec_all` | `.github/workflows/spec-validation.yml:41-51` — one run per `docs/specs/*.md` except `template.md`, `… \|\| exit 1` when acceptance/property/unit tests exist; CI echoes `Validating <spec>` | `for spec in docs/specs/*.md; do [ "$(basename "$spec")" = "template.md" ] && continue; uv run python scripts/verify_spec.py "$spec"; done` |
| `verify_spec_template` | `tests/acceptance/test_structure_map.py::test_ac_025_mypy_covers_scripts` (byte-pinned report) | `uv run python scripts/verify_spec.py docs/specs/template.md` |

### Baseline values (2026-10-11, this worktree, `eddf94f`)

All three scripts write to **stdout only** — every `.stderr` is **0 bytes**
(sha256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`), so stdout + exit code is the whole
observable surface.

| File | Bytes | sha256 | Exit |
|---|---|---|---|
| `check_traceability.stdout` | 72 | `e13c563109236236f73295e614a3425e24b583b317a5d8084de43cc6722e4c3f` | **0** |
| `validate_task_dag.stdout` | 61 | `9234e8306a9b91f53f2085c588e8243635fc2986366f16201f8a16859c1b1158` | **0** |
| `verify_spec_all.stdout` | 31 708 | `9d3d3cdc1485861191011559c9928c8023198e5d04dc91645003c430f65d7b58` | 15/15 specs exit **0** |
| `verify_spec_all.exit` | 475 | `8b4c99ea0d395170ee3d49f282e91dd08db8bd317c5ea43ed0a811ed7f68fb18` | — |
| `verify_spec_template.stdout` | 363 | `0f8ec58e398f714dccf5044ae3384e900edf4041c745999db8b9a0317c104a0b` | **0** |

Verbatim stdout of the two one-line witnesses (the full text, so the record is self-contained):

```text
Traceability: PASS (890 matrix rows, 136 spec IDs, 875 test functions)
Task DAG validation PASSED: 12 tasks, acyclic, well-formed.
```

`verify_spec_all` covers all 15 specs (`authentication`, `event-bus`, `file-management`, `logging-coverage`,
`logging`, `mail-service`, `search`, `session-management`, `settings-coverage`,
`settings-public-registry-setter`, `settings`, `structlog-logging`, `structure-map`, `user-management`,
`user-roles-permissions`), each printing its `✓ …` list and `Traceability: PASS`.

### Complexity baseline files (measurement, not a byte witness)

| File | Bytes | sha256 | Exit |
|---|---|---|---|
| `complexipy_scripts.stdout` (`uv run complexipy scripts --max-complexity-allowed 15`) | 3 774 | `6d71a312b61a017f57e8071d0efdd77c0d4a8eec867b8112b3af4fa447b2946f` | **1** (4 FAILED) |
| `complexipy_ci_form.stdout` (`uv run complexipy src tests --max-complexity-allowed 15`) | 187 539 | `da346575057e57e2325a07b7e1fd2b108d22b3eb25d5cef1eadf01c552e1e237` | **0** |
| `complexipy_config.stdout` (bare `uv run complexipy`) | 187 539 | `da346575057e57e2325a07b7e1fd2b108d22b3eb25d5cef1eadf01c552e1e237` (identical to the CI form) | **0** |

These three are **expected to differ after the change** (that is the point), and complexipy's report embeds ANSI
colour escapes and OS-native path separators (`scripts\make_map.py` on this host), so it is a host-local
measurement, never a cross-platform byte witness. An ANSI-stripped copy of the scripts run is kept at
`complexipy-scratch/complexipy_scripts-before.txt` (2 202 bytes) for the before/after score table.

### How Phase 5 re-runs and compares

1. `bash capture.sh <change worktree> /c/workspace/active-projects/complexipy-scratch/golden-after`
2. `diff golden-before/check_traceability.stdout golden-after/check_traceability.stdout` (and the same for
   `validate_task_dag.stdout`, `verify_spec_all.stdout`, `verify_spec_all.exit`, `verify_spec_template.stdout`,
   and every `.stderr` / `.exit`) — **must be empty**.
3. Re-run `uv run complexipy scripts --max-complexity-allowed 15` → **exit 0**, every function in the three
   scripts **≤ 12**, and record the new score table next to the baseline table.

- **Reproducibility of the baseline (checked the same day).** Re-running `capture.sh` **after** this record and
  its map line landed (the `chore(complexipy-scripts): scope` commit) produced byte-identical output for **all
  21** golden files (`diff -r golden-before golden-recheck` → empty). The scope record is therefore neutral to the
  three scripts' behavior, exactly as the two neutrality arguments below predict. `capture.sh` now refuses an
  `OUT` that resolves inside a worktree or repository — a relative path once created a stray directory in the
  worktree, which is precisely the failure mode this scratch layout exists to avoid.

Two repo edits in this change are provably neutral to the golden outputs, so a diff there is a real finding, not
expected drift:

- The **NFR-005 wording amendment** in `docs/specs/structure-map.md` cannot change `verify_spec.py`'s report:
  `parse_spec` collects IDs with `sorted(set(re.findall(...)))` (`scripts/verify_spec.py:11-19`), so re-wording a
  row and adding a Changelog line that names `NFR-005` changes no ID set.
- **Adding this file** cannot change `check_traceability.py`'s counts: `main` reads the matrix from
  `docs/verification/traceability.md` only (`scripts/check_traceability.py:129`), the spec IDs from `docs/specs/`,
  and the test names from `tests/` — and this change adds no `docs/specs/` ID and touches no test.

### Known ceiling of the witness (recorded honestly)

The repository is clean, so the golden run exercises only the **PASS paths**. The FAIL branches —
`Traceability: FAIL (n violation(s))` and its message order, `Task DAG validation FAILED:` and the
`Cycle detected: A -> B -> A` line, `Specification validation` failure lines — are exactly the code the refactors
touch most, and the golden pair does not reach them. Mitigation inside this change's evidence plan (adds **no**
file to the repository, so Q-12's "no test added" holds): build throwaway broken inputs under the scratch
directory (a matrix row citing an undefined ID, a `tasks.json` with a cycle, a spec with an untested AC) and
byte-compare the three scripts' FAIL-path stdout and exit codes before/after, recording the pair here.

Second ceiling: the CI invocation passes the runner path as `argv[1]`, so `validate_task_dag.py`'s `check_sync`
is **not** exercised by the golden run (`main` skips it when `tasks_path == runner_path`,
`scripts/validate_task_dag.py:118-120`). It scores **12** today, so it is not in the refactor set and the gap
costs nothing here.

## Exact non-behavior changes (the scope, file by file)

| # | File | Exact change | Kind |
|---|---|---|---|
| 1 | `pyproject.toml:100` | `paths = ["src", "tests"]` → `paths = ["src", "tests", "scripts"]`. `max-complexity-allowed = 15` **unchanged**; nothing else in the file is touched (no dependency, no coverage/bandit/ty/mypy/ruff edit, no `[tool.bumpversion]` edit) | configuration |
| 2 | `.github/workflows/quality.yml:146` | `uv run complexipy src tests --max-complexity-allowed 15` → `uv run complexipy src tests scripts --max-complexity-allowed 15` — the positional args stay explicit (**Q-05**) so CI fails loudly on a bad config, as the comment at `:144-145` intends; job name, runner, steps and the hard-gate semantics are unchanged | CI |
| 3 | `scripts/check_traceability.py` | `check` **17 → ≤ 12** and `matrix_rows` **19 → ≤ 12**. Permitted shapes (**Q-09**): a table-driven list of check rules for the four independent loops in `check`; lift the nested `flush` closure out of `matrix_rows` to module level. New helpers are **public, module-level, same file** (**Q-10**); existing names/signatures **may** change (**Q-11**). No new file — **no `scripts/_common.py`** | tooling refactor |
| 4 | `scripts/validate_task_dag.py` | `check_acyclic` **22 → ≤ 12**. Permitted: an iterative DFS replacing the recursive `dfs` closure, extracted graph-build helper. **Frozen:** first-cycle-only short-circuit and the single `Cycle detected: A -> B -> A` line (**Q-07**). `check_sync` (12), `check_well_formed` (8), `load_tasks` (0), `main` (6) are already under the target and are not restructured unless a shared helper needs it | tooling refactor |
| 5 | `scripts/verify_spec.py` | `main` **22 → ≤ 12**. Permitted: a report-rendering data structure; the report for `docs/specs/template.md` stays byte-identical to the AC-025-pinned `_VERIFY_SPEC_REPORT_BEFORE_FIX` | tooling refactor |
| 6 | `docs/specs/structure-map.md:486` | **NFR-005 amended in place** — its tail "`scripts/` is not analyzed by complexipy" becomes false once #1/#2 land, so the row is re-worded to state the widened scope (`paths = ["src", "tests", "scripts"]`, ceiling 15) while its normative clause (the structure-map test files stay under 15) is kept. A `## 15. Changelog` **v4** entry is added at the top of the changelog list (`:642`) in the existing v3/v2 format, naming the change and pointing at this record. No ID is renumbered, restated or deleted (**Q-04**, Spec Amendment Workflow — the amendment rides **this** PR, flagged to the reviewer at the merge gate) | spec amendment |
| 7 | `docs/decisions/ADR-087-complexipy-scope-extended-to-scripts.md` (new; re-check the next free number at write time — `ADR-081` is a permanent gap and no in-flight change claims 087) | Supersedes `ADR-086-scripts-type-checked-tree.md:18` (`complexipy` (CI `complexity`) \| `paths = ["src","tests"]` \| **widen: no**) and its `:48` frozen-scope sentence. Records WHY the widening is now accepted while ADR-086's other frozen scopes (coverage `source`/`fail_under = 92`, bandit `-r src/`, `ty` `root = ["./src"]`) stay closed. **ADR-086 is not edited** — a decision record is superseded, never rewritten (**Q-04**) | decision record |
| 8 | `STRUCTURE.md` | Regenerated with `uv run python scripts/make_map.py` **in the same commit as each `scripts/*.py` commit** and in the commit that adds this record (**Q-14**). Never hand-edited. Headroom 196 lines, so the new public helper signatures and any renamed signatures fit | generated artifact |
| 9 | `CHANGELOG.md` | One entry under `## [Unreleased]` → `### Changed` (the gate widening + the four refactors), traced to what the change actually did. **No version bump** and no new `## [x.y.z]` section (DOCS/CHORE → none, Q-16) | changelog |
| 10 | `docs/verification/complexipy-scripts.md` | This record: scope, baselines, golden outputs, and the Phase 4/5 evidence added as the work proceeds | evidence |

**Commit plan (each `scripts/*.py` commit carries its own regenerated `STRUCTURE.md`):**
`chore(complexipy-scripts): scope` (this file) → one commit per script refactor (+ map) → `chore(complexipy-scripts): gate scope`
(`pyproject.toml` + `quality.yml`) → `docs(complexipy-scripts): NFR-005 amendment + ADR-087` → `chore(complexipy-scripts): changelog`.
The gate-scope commit lands **after** the refactors, so the `complexity` job never goes red mid-PR.

## No-behavior-delta confirmation

The observable surface of the three scripts is **argv, exit code and stdout** (they write nothing to stderr —
every captured `.stderr` is 0 bytes). This change is DOCS/CHORE only if all of the following hold, and each is
checked by the named witness:

| Must stay identical | Why it is the contract | Witness |
|---|---|---|
| `check_traceability.py` stdout **byte-for-byte** and exit code | The `traceability` job's log line is what a reviewer reads, and its counts (today `890 matrix rows, 136 spec IDs, 875 test functions`) are quoted in change records | golden pair `check_traceability.*` |
| `check`'s **fixed message order** — missing row → undefined ID → missing test → undeclared Status value (**Q-07**) | A table-driven rewrite could reorder emissions; the order is part of the printed contract | golden pair + the scratch FAIL-path differential |
| `validate_task_dag.py` stdout and exit code, including **`check_acyclic`'s first-cycle-only** short-circuit (returns after the first cycle, prints exactly one `Cycle detected: …` line) | "Collect all cycles" would change stdout — that rewrite is **illegal** under this change (**Q-07**) | golden pair + scratch cyclic-graph fixture |
| `verify_spec.py` stdout and exit code for **every** spec, and byte-identity with AC-025's `_VERIFY_SPEC_REPORT_BEFORE_FIX` for `template.md` | AC-025 already pins that report byte-for-byte in a test this change may not touch | golden pair `verify_spec_all.*` / `verify_spec_template.*` + the untouched `test_ac_025` |
| What the three scripts **detect** — same violations, same exit status for the same input | They are the workflow's own gates; a silent relaxation weakens every future change | golden pair + FAIL-path differential |
| Every test file, and `docs/verification/traceability.md` | **No test is added or changed** (**Q-03**, **Q-12**) and **no matrix row is written** (**Q-15**) — the evidence lives in this record | `git diff --name-only main…HEAD` contains no `tests/` path and no `docs/verification/traceability.md` |

`test_nfr_005_complexipy_threshold_holds` keeps pinning its own `_COMPLEXIPY_PATHS = ("src", "tests")`
(`tests/acceptance/test_structure_map.py:1427`, passed to complexipy at `:1462`) and is **not** weakened or
amended (**Q-04**, **Q-12**): it never reads `[tool.complexipy] paths`, so widening the config cannot break it,
and it is not extended to cover `scripts/` — that would be a test change under a type that forbids one. Enforcement of the widened scope is the
`complexity` job plus `[tool.complexipy] paths` — deliberately **not** duplicated by a config-contract test.

## Out of scope (copied from `docs/todo/complexipy-scripts.md`, binding)

- Raising or parameterising the `15` ceiling, and any per-file carve-out, baseline or complexipy snapshot — the
  point is to meet the existing ceiling, not to encode debt.
- Any behavior change to the CI checks themselves (what `check_traceability.py`, `validate_task_dag.py` and
  `verify_spec.py` detect **and print** stays exactly as it is — **Q-07**).
- `scripts/make_map.py` (already under the ceiling at max 12; edited by the merged `map-default-drop-shift`).
- The near-miss functions elsewhere: `test_ac_008_document_shape` = 15, `_feature_logger_names` = 14,
  `test_inv_004_other_loggers_untouched` = 14, `test_concurrent_thread_safe` = 14, `SearchService::search` = 13,
  `SettingsRegistry::create_template` = 13 (**Q-17**).
- New scripts; widening coverage (`source = ["src/backend","src/frontend"]`, `fail_under = 92`, frozen by
  ADR-086), bandit (`-r src/`), `ty` (`root = ["./src"]`) or mypy beyond `scripts/`.
- A CI `make_map.py --check` job or a `paths:` filter change — the stale-map mechanism is **accepted risk**, no
  TODO opened (**Q-08**).
- Pinning or downgrading complexipy, or a score ratchet — drift **accepted** (**Q-18**).
- Any `.gitattributes` / line-ending change — owned by the open `gitattributes-line-endings` TODO (**Q-02**).
- A config-contract witness that `scripts/` stays in the gate — CI job is the enforcement (**Q-12**); no
  `docs/verification/traceability.md` rows (**Q-15**).
- Shrinking `STRUCTURE.md` to buy headroom (**Q-14**) — headroom is 196 lines and sufficient.

## Gates this type runs (DOCS/CHORE, Q-16)

| Phase | Runs | Gate |
|---|---|---|
| P | done at P.4 | this scope record + the baselines above |
| 1 Specify | scope only (this file) | no spec PR — the NFR-005 amendment rides the change PR and is flagged to the reviewer at the merge gate |
| 2 Decompose | **skipped** | no ADR-driven task DAG; ADR-087 is a decision record, not a task input |
| 3 Test & RED | **skipped** | no RED, no test written or changed (**Q-12**) |
| 4 Implement | the ten scoped edits | each script commit: `uv run ruff check <changed paths>` clean, `uv run mypy scripts/` clean, `uv run complexipy scripts --max-complexity-allowed 15` clean for the file just refactored, `STRUCTURE.md` regenerated in the same commit |
| 5 Verify | **light tier** | `uv run ruff check .` (repo-wide, matches `.github/workflows/lint.yml`) · `uv run mypy scripts/` · the complexipy gate — `uv run complexipy src tests scripts --max-complexity-allowed 15` **exit 0** with every function in the three scripts **≤ 12**, and bare `uv run complexipy` now analysing `scripts/` · the **golden-output byte comparison** (§How Phase 5 re-runs and compares) · confirmation that no test file and no `docs/verification/traceability.md` row was touched |
| 6 Review | **light review** | the scope above is exactly what the diff contains; the acceptance tests were not weakened (none was touched); the NFR-005 wording and ADR-087 agree with the config; `CHANGELOG.md` entry under `## [Unreleased]`; **no version bump** |
| Post-merge | S7.1 cleanup | worktree removed, `chore/complexipy-scripts` deleted locally and remotely |

**What replaces REFACTOR's full-regression gate:** the golden-output byte comparison. It is stronger than a
regression run for these three scripts — a regression run would not have noticed a changed message (no test
covers them), the byte comparison would. The full suite still runs in CI on the PR (`spec-validation.yml` `tests`
job, `quality.yml` `tests` job), so a regression elsewhere is caught there; it is simply not a Phase 5 gate for
this type.

## Baseline caveat (Q-01 / Q-02) — re-measured here, not copied

Re-measured in this worktree at `eddf94f` on 2026-10-11:

- `uv run python scripts/make_map.py --check` → **exit 0**. The committed map is a fresh render.
- `uv run pytest tests/acceptance/test_structure_map.py::test_ac_021_committed_map_matches_fresh_render -q`
  → **1 failed in 2.39 s**, with
  `AssertionError: REQ-021: the committed map is not a fresh render — line count differs: committed 2004 lines, fresh 2004 lines`
  and `At index 22 diff: b'\r' != b'\n'` — i.e. **identical content (2004 = 2004 lines), differing line endings only**.
- Cause confirmed on the host: `git ls-files --eol STRUCTURE.md` → `i/lf w/crlf`, `core.autocrlf = true`, and no
  `.gitattributes` exists. `make_map.py` renders LF; AC-021 compares bytes.

So the 223/224 file-count mismatch that made P.2's baseline red is **gone** (fixed by the merged
`map-default-drop-shift`), and the one remaining local failure is a **host CRLF artifact, not a content defect**.
It is **not** in this change's scope: adding `.gitattributes` would change checkout behavior repo-wide and is
owned by the open `docs/todo/gitattributes-line-endings.md` (DOCS/CHORE), which already names AC-021 as the
witness it unblocks (**Q-02**).

**`CI` (Linux, `ubuntu-latest`) is the authoritative gate** for the test suite; the local Windows result on this
one test is recorded so the change's own evidence stays distinguishable from the inherited host failure. This
change adds no test and changes no test, so the AC-021 result is identical before and after it.

## P.4 record summary

- Scope defined and confirmed **no behavior delta** (§Exact non-behavior changes, §No-behavior-delta confirmation).
- Golden-output baseline captured **before** any restructuring (§Golden-output baseline).
- Complexity baseline captured: 4 functions over the ceiling (17 / 19 / 22 / 22), target **≤ 12**, `make_map.py`
  clean at max 12, 50 functions analysed in `scripts/`.
- No `scripts/*.py`, `pyproject.toml`, workflow, spec, ADR, `STRUCTURE.md`, `CHANGELOG.md` or test file was
  modified in this step; `docs/todo/` and `docs/questions/` were not touched.
- **Next:** S4.1 — the first Phase 4 refactor step (pick a script, refactor to ≤ 12, re-check the golden pair for
  that script, regenerate the map, commit).

## Phase 4 unit 1 — `scripts/check_traceability.py` (S4.2, 2026-10-11)

Scope item **#3** only. `check` **17** and `matrix_rows` **19** were restructured to the **Q-13** target (≤ 12)
with a **byte-identical stdout + exit-code contract** (**Q-07**). Files touched by this unit:
`scripts/check_traceability.py`, the regenerated `STRUCTURE.md`, and this record — nothing else
(no `pyproject.toml`, no workflow, no spec, no ADR, no `CHANGELOG.md`, **no test file**, no
`docs/verification/traceability.md` row, per **Q-12** / **Q-15**).

### Shape chosen (permitted by Q-09, Q-10, Q-11)

Pure extraction plus one flattening — no algorithm change, so the emission order cannot drift:

- `matrix_rows` (nested `flush` closure) → `table_blocks` (splits the file into pipe-table blocks) +
  `status_index` (Status column or `-1`) + `matrix_row` (one row's IDs / cited tests / Status cell) +
  `table_rows` (one block → its data rows) + a one-line `matrix_rows` comprehension.
- `check` (four loops) → one module-level function per rule — `ids_without_row`, `rows_citing_undefined_ids`,
  `rows_citing_missing_tests`, `rows_with_undeclared_status` (+ `status_token` for the Status vocabulary
  probe) — and `check` is the **concatenation of the four in the frozen order** (missing row → undefined ID →
  missing test → undeclared Status). A table of callables was **not** used: the concatenation is smaller,
  fully typed for `mypy`, and shows the frozen order at the call site.
- All nine new helpers are **public, module-level, same file** (**Q-10**); no `scripts/_common.py`; existing
  names kept where they still read (`matrix_rows`, `check`, `main` unchanged in signature) — renaming was
  **allowed** (**Q-11**) but was not needed, so the map churn stays at 10 added lines.

### Per-function complexity, before → after

`uv run complexipy scripts --max-complexity-allowed 15` (ANSI-stripped), this file only:

| Function | Before | After |
|---|---|---|
| `check` | **17** ✗ | **0** ✅ |
| `matrix_rows` | **19** ✗ | **2** ✅ |
| `defined_ids` | 1 | 1 |
| `test_names` | 1 | 1 |
| `spec_files` | 2 | 2 |
| `main` | 6 | 6 |
| `table_blocks` | — (new) | **9** ✅ |
| `table_rows` | — (new) | 4 ✅ |
| `ids_without_row` | — (new) | 5 ✅ |
| `rows_with_undeclared_status` | — (new) | 3 ✅ |
| `rows_citing_undefined_ids` | — (new) | 2 ✅ |
| `rows_citing_missing_tests` | — (new) | 2 ✅ |
| `status_index` | — (new) | 2 ✅ |
| `status_token` | — (new) | 1 ✅ |
| `matrix_row` | — (new) | 0 ✅ |

The file is now **15 functions, max 9** — under the ≤ 12 target with 3 points of margin, and under the
house maximum already demonstrated by `make_map.py::_member_lines` (12). `check_traceability.py` contributes
**no** FAILED line to the gate any more.

Whole-`scripts/` gate state after this unit (the other two over-ceiling functions are **units 2 and 3**, so the
command still exits **1** — expected mid-change, and the gate widening (**unit 4**) still lands after them):

```text
FAILED  scripts\validate_task_dag.py :: check_acyclic  22   (unit 2)
FAILED  scripts\verify_spec.py       :: main           22   (unit 3)
```

### Golden-output re-run (the primary no-behavior-delta evidence, Q-03)

`bash capture.sh <this worktree> /c/workspace/active-projects/complexipy-scratch/golden-after-unit1`
(absolute, outside every worktree; `capture.sh` refuses anything else), then `diff -r golden-before
golden-after-unit1` — **21 files compared, 20 byte-identical, exactly 1 differs**:

| Witness (18 files) | Result |
|---|---|
| `check_traceability.stdout` (72 B, sha `e13c5631…4c3f`) / `.stderr` (0 B) / `.exit` (`0`) | **identical** |
| `validate_task_dag.stdout` (61 B, sha `9234e830…1158`) / `.stderr` / `.exit` | **identical** |
| `verify_spec_all.stdout` (31 708 B, sha `9d3d3cdc…7b58`) / `.stderr` / `.exit` (475 B, sha `8b4c99ea…fb18`) | **identical** |
| `verify_spec_template.stdout` (363 B, sha `0f8ec58e…4a0b`) / `.stderr` / `.exit` | **identical** |
| `complexipy_ci_form.*`, `complexipy_config.*` | **identical** (they analyse `src` + `tests` only) |
| `complexipy_scripts.stdout` | **differs — expected**: it is the complexity **measurement**, not a witness (§Complexity baseline files: "expected to differ after the change"), and the diff is only this file's score lines (`check 17 ❌` / `matrix_rows 19 ❌` removed; the nine new helpers `0…9 ✅` added) |

`check_traceability.stdout` verbatim, unchanged: `Traceability: PASS (890 matrix rows, 136 spec IDs, 875 test
functions)` — the row/ID/test-function counts the parser produces are identical, so the table-parsing rewrite
sees exactly the same rows.

### FAIL-path differential (closes the §Known ceiling of the witness gap for this file)

The golden set only reaches PASS paths, so the FAIL branches were differential-tested against a **scratch
fixture outside the worktree**: `complexipy-scratch/unit1/faildiff.sh` copies the real `docs/` + `tests/`
(890-row matrix) into `complexipy-scratch/unit1/fail-fixture/`, mutates the **copy**, and runs the pre-refactor
script (`git show HEAD:scripts/check_traceability.py`, saved to the scratch dir) and the post-refactor script
against the same fixture with that fixture as CWD.

| Fixture | before vs after | exit |
|---|---|---|
| unmutated copy (PASS path, second witness) | stdout **byte-identical** (both sha `e13c5631…4c3f`), stderr 0 B both | `0` / `0` |
| mutated copy (all four rules + parser edges) | stdout **byte-identical** (both sha `6b130fe2…fd49` — full value below), stderr 0 B both | `1` / `1` |
| no `tests/` directory (missing-input branch) | stdout **byte-identical** | `1` / `1` |

Mutated-fixture output, identical for both scripts (sha256 `6b130fe208040cd1ae7cc8163e9c45f8a4f19a61895f698bfacc925ea406fd49`
for both stdouts), which exercises **all four rules in the frozen order** and the parser edge cases:

```text
Traceability: FAIL (5 violation(s))
  REQ-9001 defined in docs/specs/ has no row in docs\verification\traceability.md
  docs\verification\traceability.md:1191: row references undefined REQ-9998
  docs\verification\traceability.md:1191: row references missing test test_injected_test_that_does_not_exist
  docs\verification\traceability.md:1191: undeclared Status value 'DONE'
  docs\verification\traceability.md:1192: undeclared Status value '1234'
```

Rule coverage in that run: rule 1 × 1, rule 2 × 1, rule 3 × 1, rule 4 × 2 — and the three parser edges injected
alongside them (a data row with fewer cells than the Status index, a 2-line table below `MIN_TABLE_LINES`, and
two tables with no Status column) produced **no** message in either version, i.e. they are still skipped
identically.

### Gates run for this unit

| Gate | Command | Result |
|---|---|---|
| complexity (this file) | `uv run complexipy scripts --max-complexity-allowed 15` | `check_traceability.py` — **15/15 PASSED, max 9**; whole command still exit **1** on `check_acyclic` 22 + `verify_spec.main` 22 (units 2/3) |
| lint | `uv run ruff check scripts/check_traceability.py` | **All checks passed!** |
| format | `uv run ruff format --check scripts/check_traceability.py` | **1 file already formatted** |
| types | `uv run mypy scripts/` | **Success: no issues found in 4 source files** |
| map | `uv run python scripts/make_map.py` + `--check` | regenerated in this commit; `--check` exit **0**; `STRUCTURE.md` **2 013** lines (was 2 004, +9 signatures +1 line-count line) — NFR-002 ceiling 2 200, headroom **187** |

- **Next:** S4.2 unit 2 — `scripts/validate_task_dag.py::check_acyclic` **22 → ≤ 12** (first-cycle-only
  short-circuit frozen by **Q-07**; the `validate_task_dag.*` golden pair must stay byte-identical).
