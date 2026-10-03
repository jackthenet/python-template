# remove-spec-tdd-driver — Scope Record (DOCS/CHORE)

- **Change:** remove-spec-tdd-driver · **Type:** DOCS/CHORE (classified at P.1, first matching criterion: "does not alter behavior — documentation, comments, configuration, CI, tooling")
- **Branch / worktree:** `chore/remove-spec-tdd-driver` @ `c2342b6` (== `main` == `origin/main`, `pyproject.toml:4` version `0.6.0`), worktree `../python-template_kopie-worktrees/chore/remove-spec-tdd-driver` — created at **P.4** from `main` (git skill, "Create change worktree (P.4)"), so the branch carries the TODO file and the answered question file as of P.3.
- **Phase Matrix for this type:** Phase P → scope record (this file) · Phases 1–3 skipped · **Phase 4** make the change · **Phase 5** light gate (scope proof + lint/types where applicable) · **Phase 6** light review + PR. No spec, no spec-approval PR, **no version bump** (AGENTS.md Versioning: `REFACTOR / DOCS-CHORE → none`).
- **Date:** 2026-10-03

## Phase P record

| Step | Date | Result |
|---|---|---|
| P.1 Frame (orchestrator, `main`) | 2026-10-03 | `docs/todo/remove-spec-tdd-driver.md` + `docs/questions/remove-spec-tdd-driver.md` created on `main`; type **DOCS/CHORE**; todo set #9–#13 |
| P.2 Interrogate | 2026-10-03 | **DONE — 0 questions needing user input** (no `BLOCKED-USER`). DOCS/CHORE has no 20-question floor; every interrogation point was closed from repository evidence (the five evidence points + six points closed without asking, recorded in `docs/questions/remove-spec-tdd-driver.md:28-57`). Overlap check clean against `docs/specs/` and `docs/todo/` |
| P.3 Answer (orchestrator ⏸, `main`) | 2026-10-03 | **no-op** — 0 questions to present, 0 answer rounds; question file `Status: ALL ANSWERED` |
| Value triage (pre-workflow) | 2026-10-03 | **4/5 — user decision: implement as logged** (scope unchanged: delete the driver **and** record the `prepared-workflow` follow-up closures). The alternative — *update* the driver — was rejected: it keeps a second copy of the protocol that must track `AGENTS.md` forever |
| P.4 Draft scope + create branch/worktree | 2026-10-03 | **this file** — worktree + branch created, scope recorded, evidence re-verified independently (below) |
| P.5 Self-consistency | n/a | DOCS/CHORE — P.5 runs for FEATURE/CROSS-CUTTING only (AGENTS.md, Phase P table) |

**Why (from the TODO):** `prepared-workflow` left the driver stale — its Phase 1 node still instructs a subagent to create the branch, interrogate the idea and write the specification (`.pi/workflows/spec-tdd.workflow.ts:65` in the pre-deletion state), which is exactly the work Phase P now front-loads. Accepted as finding **F-10** and deferred as follow-up #3 (`docs/verification/prepared-workflow.md:383`, `:81`).

---

## Scope — the exact non-behavior change

**One path, deleted. Nothing else in the repository is edited.**

| # | Action | Path | Kind |
|---|---|---|---|
| 1 | `git rm` (delete) | `.pi/workflows/spec-tdd.workflow.ts` (187 lines, the **only** tracked `.pi` path and the only tracked `.ts` file in the repository) | tooling / configuration |
| 2 | Record the follow-up closures (this file, §"Follow-up closures" below) | `docs/verification/remove-spec-tdd-driver.md` | documentation |

What the deleted file is: a `defineWorkflow({ name: "spec-tdd" })` driver importing `{ agent, choice, compute, defineHumanChoices, defineWorkflow, humanDecision, humanDecisionEdge } from "@osolmaz/pi-workflows"` (`:1-9`, `:49-53`), whose `specify` node prompt says "Phase 1 (DISCOVER & SPECIFY) … creating the feature branch from main, adversarially interrogating the feature idea into a brief, writing the specification …" (`:65-68`) — the pre-Phase-P protocol.

Tree effect: `.pi/workflows/` becomes empty and therefore stops existing in git's tree (git does not track empty directories). `.pi/subagents.json` stays on disk — it is gitignored (see check 3 below) and was never tracked, so it is not in the diff and not in any worktree's checkout.

**Explicitly NOT part of the change:** no annotation of `docs/verification/prepared-workflow.md`, no `.gitignore` edit (`.gitignore:234` ignores `.pi/subagents.json`, not the driver, so it does not become dead), no removal of the `.pi` directory itself, no replacement driver.

## Follow-up closures (recorded here; no other record is edited)

`prepared-workflow` deferred three items at `docs/verification/prepared-workflow.md:79-81`. Their disposition, with the triage reason for each:

| Follow-up (`prepared-workflow.md:79-81`) | Disposition | Triage reason |
|---|---|---|
| #1 `:79` — split the archived Q&A history (`docs/questions/archive-AI_Questions.md`) into per-change question files | **DROPPED** | Value triage **1/5, "drop"** (`docs/todo/split-archived-qa.md:36-39`): the archive already holds the history in one browsable place, `AGENTS.md` retired the central file and points at it as an archive, and **no gate, skill or script reads it** — it churns a frozen historical record for a nicety nothing consumes |
| #2 `:80` — add a `docs/todo` / `docs/questions` path trigger to `.github/workflows/spec-validation.yml` | **DROPPED** | Value triage **1/5, "drop"** (`docs/todo/docs-path-ci-trigger.md:35-39`): the job validates `docs/verification/traceability.md`, `docs/specs/` and `tests/` (`scripts/check_traceability.py:129-131`), all already in its `paths:` list; planning records carry no gate by design, so the trigger would fire a job that asserts nothing about them — CI cost plus a false signal of coverage |
| #3 `:81` — update `.pi/workflows/spec-tdd.workflow.ts` to include a prep node | **CLOSED BY THIS DELETION** | Superseded: the 2026-10-03 value triage scored *updating* it 4/5 and the user decided the driver is not used at all, so deleting it is the smaller diff that removes the contradicting artifact instead of maintaining a second copy of the protocol (F-10, `prepared-workflow.md:383`) |

The TODO's In-scope list also names **"shared cache dirs"** as a follow-up to close. Provenance correction (record accuracy, not a scope change): `prepared-workflow`'s follow-up list has exactly the three items above — the shared-cache-dirs item is **not** among them. It is the option documented at `AGENTS.md:114` (added by the merged `workflow-docs-ci-timing` change, Change B, `docs/verification/workflow-docs-ci-timing.md:20-29`), which recorded the *option* (`RUFF_CACHE_DIR` / `MYPY_CACHE_DIR`) and verified that `pyproject.toml` sets no shared cache dir. Disposition: **DROPPED** — the per-worktree cache is the deliberate default (each worktree's `.ruff_cache` / `.mypy_cache` is gitignored and cold at creation); sharing them would point two concurrent worktrees at one mutable cache for a speed-up nothing measured, and `AGENTS.md:114` already tells a future change how to opt in if it ever measures a need.

## No-behavior-delta proof (independently re-verified at P.4, in this worktree)

Every check below was re-run in `../python-template_kopie-worktrees/chore/remove-spec-tdd-driver` at `c2342b6`; the results are the observed output, not a copy of the P.2 record.

| # | Check | Command | Result |
|---|---|---|---|
| 1 | The driver is the whole tracked `.pi` tree | `git ls-files .pi` | **`.pi/workflows/spec-tdd.workflow.ts`** — exactly one path, so the deletion is the entire tracked `.pi` delta |
| 2 | No other tracked `.ts` / JS / Node artifact exists | `git ls-files \| grep -Ei "package\.json\|tsconfig\|deno\|bun\|\.ts$\|\.js$"` | **no `package.json`, no `tsconfig.json`, no `deno.json`, no lockfile**; the only other matches are JSON config files (`.github/hooks/*.json`, `.github/task-runner/tasks.json`, `.vscode/*.json`, `docs/tasks/*.json`) — the driver is the repository's **only** TypeScript file, so deleting it leaves **no orphan dependency or config to clean up** |
| 3 | `.pi/subagents.json` is not tracked and stays | `git check-ignore -v .pi/subagents.json` | **`.gitignore:234:.pi/subagents.json`** (exit 0) — pi's own subagent runtime state, not a protocol artifact; it is absent from a fresh worktree's checkout precisely because it is untracked |
| 4 | No CI reference | `grep -rn -E "spec-tdd\|pi-workflows\|\.pi[ /\"']" .github/workflows` | **no match** (lint.yml, quality.yml, spec-validation.yml) — no job, step, path filter or script touches `.pi`, TypeScript, `tsc` or `deno` |
| 5 | No test / script / docs-site / editor reference | `grep -rn -E "spec-tdd\|pi-workflows\|\.pi[ /\"']" tests scripts userdocs docs/specs .vscode` | **no match in any of the five** — no test asserts on the file or the directory; `mkdocs.yml` serves `userdocs/`, which never mentions the driver; no spec or `REQ`/`AC` requires it to exist |
| 6 | No project-config reference | `grep -n -E "spec-tdd\|pi-workflows\|\.pi\|typescript\|deno\|tsc" pyproject.toml .pre-commit-config.yaml mkdocs.yml .editorconfig` | **no match in any of the four**; `.editorconfig` sections are `[*]`, `[*.md]`, `[*.py]`, `[*.{ps1,sh}]`, `[*.{yml,yaml,toml}]` — **no `[*.ts]` section to remove**; `.gitignore`'s only `.pi` entry is `:234` (subagents.json), which stays live |
| 7 | Remaining mentions are historical only | `git grep -n "spec-tdd"` / `git grep -n "pi-workflows"` | Hits are: the driver itself (`:16`, `:50`, `:57`; `:9`, `:81`), this change's planning records (`docs/todo/`, `docs/questions/`), and historical records — `docs/verification/prepared-workflow.md:81`, `:347`, `:383`, `:567`, plus `docs/todo/value-triage-gate.md:20` and `docs/todo/workflow-docs-nits.md:37` (both mention this change by name, not the driver's behavior). `docs/verification/tooling-hardening.md:57`, `:94`, `:273`, `:310` mention only the gitignored `.pi/subagents.json`. **All stay unchanged** (TODO "Out of scope") |
| 8 | Nothing in the installed pi runtime loads it | pi 0.87.1 `docs/configuration.md:25-35` — the project `.pi` table lists `settings.json`, `SYSTEM.md`, `APPEND_SYSTEM.md`, `extensions/`, `skills/`, `prompts/`, `themes/` | **`.pi/workflows/` is not a recognized pi project path**, and `grep -rln "\.pi/workflows"` over pi's docs/README → no match. The repo has no `.pi/settings.json` (no Pi package declaration) and no `.pi/extensions/`, so the driver's `@osolmaz/pi-workflows` import has **no loader installed in this repository** — the file is inert. (Refines P.2 evidence point 3, which attributed resolution to "pi's own workflow runtime": the loader is the third-party extension, which is not declared here. Strengthens the no-consumer case; no contradiction, no reclassification.) |
| 9 | CI trigger surface of the deletion itself | `grep -n -A12 "paths:" .github/workflows/*.yml` | `lint.yml` `paths:` = `src/**`, `tests/**`, `pyproject.toml`, `.pre-commit-config.yaml`, `.github/workflows/lint.yml`, `.github/hooks/**` → the `.pi/**` deletion matches **nothing**; `quality.yml` has **no** `paths:` filter (runs on every PR, incl. its `coverage` job `uv run pytest tests/ --cov`); `spec-validation.yml` `paths:` includes `docs/verification/**` → this change's own record triggers that job. Net: deleting the path cannot break a CI job, and the PR still gets the full quality + spec-validation runs from the other paths it touches |

**Conclusion:** no consumer, no loader, no CI job, no test, no config, no published-doc path depends on `.pi/workflows/spec-tdd.workflow.ts`. Removing it changes no externally observable behavior of the product (no `src/` path), of the test suite (no `tests/` path), of CI (check 9), or of the published docs site (`userdocs/` untouched). The only observable effect is that the stale pre-Phase-P protocol description is no longer in the tree — the intended hygiene outcome. The live protocol (`AGENTS.md` "Phase P: PREPARE" + `.agents/skills/*/SKILL.md`) is untouched and remains the single normative source.

## Out of scope (explicit non-goals)

- `.pi/subagents.json` — pi's own subagent state, gitignored (`.gitignore:234`), not a protocol artifact. It stays.
- Any change to `AGENTS.md`, the skills under `.agents/skills/`, `docs/specs/`, `src/`, `tests/`, `scripts/`, `userdocs/`, `.github/workflows/`, `pyproject.toml`, `.pre-commit-config.yaml`, `mkdocs.yml`, `.editorconfig`, `.vscode/`, `.gitignore`.
- Rewriting the historical records that mention the driver: `docs/verification/prepared-workflow.md:81`, `:347`, `:383`, `:567`. A repo-wide grep will therefore still show the name inside `docs/verification/` — the TODO's acceptance signal already accounts for that.
- Editing `docs/verification/prepared-workflow.md` at all: that file is the merged change's frozen record, and the planned `workflow-docs-nits` change owns any future edit to it (`docs/todo/workflow-docs-nits.md:37` — "if both changes run, this one owns the `prepared-workflow.md` edit and the other must not touch it").
- Deleting or editing the TODO/question files of the dropped follow-ups (`docs/todo/split-archived-qa.md`, `docs/todo/docs-path-ci-trigger.md`) — planning records are orchestrator-owned on `main`; this change only records the disposition above.
- Archiving the driver instead of deleting it (the TODO goal is that **no artifact in the repository** still describes the pre-Phase-P protocol; `git` history preserves the file).

## Overlap re-check at P.4 (P.2 saw 2 TODO files; the backlog has since grown)

`ls docs/todo/` at `c2342b6` → 16 files (`api-keys`, `docs-path-ci-trigger`, `notifications`, `pyproject-tooling-gaps`, `python-3.15`, `remove-spec-tdd-driver`, `security-changelog-license`, `spec-interview-protocol`, `split-archived-qa`, `structlog-logging`, `structure-map`, `template`, `tenacity-rich-cachetools`, `track-python-skill`, `update-readme`, `value-triage-gate`, `workflow-docs-nits`). Re-checked: **none of them touches `.pi/` or deletes a tooling path this change owns.** The two adjacent ones are handled above — `workflow-docs-nits` owns the `prepared-workflow.md` edit (this change must not touch it), and `docs-path-ci-trigger` / `split-archived-qa` are the follow-ups #2/#1 recorded as dropped here (they stay `PREPARING` on `main`; only the orchestrator advances planning records). `git worktree list` → the primary worktree plus this one; no in-flight change collides.

## Version bump

**None** — AGENTS.md Versioning: `REFACTOR / DOCS-CHORE → none`. `bump-my-version` is not run; `pyproject.toml:4` stays `0.6.0`.

## Phase 5 gate set for this change (light DOCS/CHORE)

Per the Phase Matrix (DOCS/CHORE → "Light: lint/types where applicable") and Phase 5 item 16 ("Run lint and type checks where applicable; confirm no test files or behavior were touched"):

| # | Gate | Command | Why it is the gate |
|---|---|---|---|
| 1 | **Scope proof** | `git diff main --name-status -M` | Must show exactly **one** `D  .pi/workflows/spec-tdd.workflow.ts` plus `A docs/verification/remove-spec-tdd-driver.md` (this record) — no `src/`, `tests/`, `scripts/`, `.github/`, `userdocs/`, `pyproject.toml`, `uv.lock` or config path. This *is* the no-behavior-delta evidence |
| 2 | Post-deletion consumer sweep | `git ls-files .pi` (expect empty) + `git grep -n "spec-tdd"` (expect only historical/planning records) | Confirms the TODO acceptance signal and that no reference was orphaned |
| 3 | Lint (whole repo, = CI `lint` job) | `uv run ruff check .` | Must match `main` (`All checks passed!`) — ruff scans Python only, so the result is unchanged by construction; run once at Phase 5 as the repo-wide sweep |
| 4 | Types | `uv run mypy src/` | Must match `main` (`Success: no issues found in 83 source files`) — no Python path is touched |

**No full-suite run is required by this change's gate set**, and the reasoning is stated rather than assumed: the diff touches **no Python and no test path** (gate 1), so there is no code for a test to exercise differently; `AGENTS.md` Phase 5 item 16 asks only for lint/types "where applicable" plus confirmation that no test file or behavior was touched. Independent confirmation still happens upstream: `quality.yml` has no `paths:` filter (check 9), so CI's `coverage` job runs `uv run pytest tests/ --cov` on this PR regardless — the full suite is verified by CI, not duplicated locally. `mkdocs build --strict` is likewise not a local gate (no `userdocs/` or `docs_dir` change); the CI `docs` job runs it anyway for the same reason.

## Acceptance signal (from the TODO) → how Phase 5 checks it

| TODO acceptance signal | Gate |
|---|---|
| `git ls-files .pi` lists no workflow script | gate 2 |
| the only remaining mentions of `spec-tdd.workflow` are inside historical verification records | gate 2 |
| `git diff --name-status` scope proof: exactly one deleted `.ts` path, no `src/`/`tests/`/`pyproject.toml`/`.github/`/config path | gate 1 |
| lint and type checks where applicable; no full-suite run required | gates 3–4 + the reasoning above |

## Phase 4 evidence (S4, make the scoped change) — 2026-10-03

Pre-state: `git ls-files .pi` → `.pi/workflows/spec-tdd.workflow.ts` (exactly one path); `git status --porcelain` → empty; HEAD `de57618`.

Change made: `git rm .pi/workflows/spec-tdd.workflow.ts` — the only action in the scope table (§"Scope"). Nothing else was written.

| Check | Command | Observed |
|---|---|---|
| Scope proof (staged) | `git diff --cached --name-status` | **`D  .pi/workflows/spec-tdd.workflow.ts`** (one entry; the separator is a tab) |
| No out-of-scope path | `git diff --cached --name-only \| grep -E "^(src/\|tests/\|docs/specs/\|scripts/\|\.github/\|migrations/\|userdocs/\|pyproject\.toml\|uv\.lock\|\.pre-commit-config\.yaml\|mkdocs\.yml\|\.editorconfig\|\.gitignore\|\.vscode/\|docs/decisions/\|docs/tasks/)"` | **no match** |
| Tracked `.pi` tree now empty | `git ls-files .pi` | **empty**; `.pi/` no longer exists on disk (git does not track empty directories — as scoped) |
| No dangling reference | `git grep -n "spec-tdd"` / `git grep -n "pi-workflows"` | hits only in `docs/verification/` (historical records + this record) and the planning records `docs/todo/`, `docs/questions/`; the driver itself no longer appears — expected and in scope |
| Lint (no-change sanity check; the repo-wide sweep stays the Phase 5 gate) | `uv run ruff check .` | **`All checks passed!`** — no Python path was touched; `ruff check --fix` / `ruff format` deliberately **not** run (AGENTS.md P-6) |
| No test / behavior touched | `git status --porcelain` | only the staged deletion (plus this record edit); no `tests/` path, no `src/` path |

Commit: this change's single Phase 4 commit (see `git log` — message `chore(remove-spec-tdd-driver): delete the unused spec-tdd workflow driver`). **Phase 5 gate 1 note:** run the scope proof against the merge-base, not the `main` tip — `git diff $(git merge-base main HEAD) --name-status -M` → exactly `D .pi/workflows/spec-tdd.workflow.ts` + `A docs/verification/remove-spec-tdd-driver.md` (the PR diff). `git diff main --name-status` additionally lists `M docs/todo/remove-spec-tdd-driver.md` only because `main` advanced after this branch was cut at `c2342b6` with the orchestrator's planning-record commits (`144a652` READY, `bd038e6` IN-WORKFLOW) — this change never writes that path (planning records are `main`-only).

---

## Phase 5 verification (S5.1–S5.4, DOCS/CHORE light gate set) — 2026-10-03

**Gate set actually run** (AGENTS.md Phase Matrix, DOCS/CHORE → "Light: lint/types where applicable"; Phase 5 item 16 → "Run lint and type checks where applicable; confirm no test files or behavior were touched"; verify skill "MUST → DOCS/CHORE"). S5.1 for this type is the **scope proof**, not a full-suite run — see "Why no full-suite run" below.

Pre-state (verify skill, Entry Conditions + Git Responsibilities): HEAD `a7a6b04` (Phase 4 change made), `git status --porcelain` → empty (clean tree), `git merge-base main HEAD` → `c2342b61c300242659e0f0476858c4e1975685a0`.

| # | Step | Check | Command (run in this worktree) | Observed output | Verdict |
|---|---|---|---|---|---|
| 1 | S5.1 | Scope proof vs merge-base | `git diff --name-status $(git merge-base main HEAD) HEAD` | **exactly two entries**: `D\t.pi/workflows/spec-tdd.workflow.ts` and `A\tdocs/verification/remove-spec-tdd-driver.md` (`git diff --name-only … \| wc -l` → **2**) | **PASS** |
| 2 | S5.1 | No out-of-scope path | `git diff --name-only $(git merge-base main HEAD) HEAD \| grep -E "^(src/\|tests/\|migrations/\|docs/specs/\|\.github/\|pyproject\.toml\|uv\.lock\|\.pre-commit-config\.yaml\|mkdocs\.yml\|userdocs/\|scripts/\|\.editorconfig\|\.gitignore\|\.vscode/\|docs/decisions/\|docs/tasks/\|docs/todo/\|docs/questions/)"` | **no match** (grep exit 1) — no source, test, migration, spec, CI, project-config, docs-site, script or planning-record path is touched | **PASS** |
| 3 | S5.1 | Consumer sweep: tracked `.pi` tree empty | `git ls-files .pi` | **empty** — no workflow script (or any other tracked `.pi` path) remains | **PASS** |
| 4 | S5.1 | No orphaned reference | `git grep -n "spec-tdd"` / `git grep -n "pi-workflows"` (at HEAD) | hits **only** in historical verification records (`docs/verification/prepared-workflow.md:81`, `:347`, `:383`, `:567`), this change's own record, this change's planning records (`docs/todo/`, `docs/questions/`), and two unrelated TODOs that name *this change* (`docs/todo/value-triage-gate.md:20`, `docs/todo/workflow-docs-nits.md:37`). The deleted file itself no longer appears anywhere | **PASS** |
| 5 | S5.2 | Lint, whole repo (= CI `lint` job, the one full-repo sweep) | `uv run ruff check .` | **`All checks passed!`** (exit 0) — identical to the `main` baseline recorded in §"Phase 5 gate set" | **PASS** |
| 6 | S5.2 | Formatting (report-only) | `uv run ruff format --check .` | **`323 files already formatted`** (exit 0). `ruff format` / `ruff check --fix` deliberately **not** run — they would modify out-of-scope files (AGENTS.md P-6) | **PASS** |
| 7 | S5.2 | Types | `uv run mypy src/` | **`Success: no issues found in 83 source files`** (exit 0) — byte-identical to the `main` baseline in §"Phase 5 gate set". No Python path is touched (check 2), so this is the no-regression check, run once as the gate | **PASS** |
| 8 | S5.3 | Traceability referential integrity (CI `traceability` job) | `uv run python scripts/check_traceability.py` | **`Traceability: PASS (746 matrix rows, 129 spec IDs, 713 test functions)`** (exit 0) | **PASS** |
| 9 | S5.4 | Docs site build (CI `docs` job gate) | `uv run mkdocs build --strict` | built to `site/` in **2.78 s**, **exit 0**, **no strict warnings** — the only stderr is the vendor's pre-existing MkDocs 2.0 advisory banner, not a build warning. `site/` is gitignored (`.gitignore:155:/site`), so the worktree stays clean (`git status --porcelain` → empty after the build) | **PASS** |

### Why no full-suite run (stated, not silently skipped)

The Phase Matrix gives DOCS/CHORE the light gate and Phase 5 item 16 asks only for lint/types "where applicable" plus confirmation that **no test file or behavior was touched**. That confirmation is checks 1–2: the diff is one deleted `.ts` file plus this record — **no `src/`, no `tests/`, no `migrations/`, no config path**. There is therefore no Python for a test to exercise differently than it did on `main`, and a local `uv run pytest tests/` would add no evidence for this change's gate set. Independent confirmation still happens upstream: `quality.yml` has **no** `paths:` filter (P.4 no-behavior-delta proof, check 9), so CI runs `uv run pytest tests/ --cov` (plus the `architecture`/`migrations`/`docs` jobs) on this PR regardless — the full suite is verified by CI, not duplicated locally.

Also deliberately not run, with reason: `uv run pytest tests/ --cov` / `tests/architecture/` (no Python or test path touched — see above); `scripts/verify_spec.py` (FEATURE/CROSS-CUTTING only, and this change has no spec); `uv run deptry .` (Python-dependency analysis; no dependency manifest is touched — `pyproject.toml`/`uv.lock` are outside the diff per check 2, and the deleted file is TypeScript with no project manifest of its own).

### S5.3 traceability — n/a, no normative ID touched

The change touches **no** `docs/specs/` file, **no** code, and **no** test, so it defines no `REQ-XXX`/`AC-XXX`/`INV-XXX`/`EDGE-XXX`/`NFR-XXX` and invalidates none: `git diff --name-only $(git merge-base main HEAD) HEAD \| grep -E "docs/specs/\|docs/verification/traceability.md"` → **no match** (exit 1). The matrix therefore needs **no** new row (a DOCS/CHORE change produces no test evidence row) and no existing row is orphaned — evidenced by check 8: `scripts/check_traceability.py` still exits 0 over **746 rows / 129 spec IDs / 713 test functions**, i.e. the deletion broke neither the spec-validation job nor any row's cited test. **Recorded as: n/a — no normative ID touched; traceability gate proven by the script passing.**

### Verdict against the TODO acceptance signal

| TODO acceptance signal (`docs/todo/remove-spec-tdd-driver.md:46`) | Check | Satisfied |
|---|---|---|
| `git ls-files .pi` lists no workflow script | 3 | **yes** — output empty |
| the only remaining mentions of `spec-tdd.workflow` are inside historical verification records | 4 | **yes** — historical verification records + this change's own planning/verification records + two TODOs naming this change; the TODO's Constraints section already accounts for the planning-record mentions |
| `git diff --name-status` scope proof: exactly one deleted `.ts` path, no `src/`/`tests/`/`pyproject.toml`/`.github/`/config path | 1, 2 | **yes** — 2 paths total (`D` the `.ts`, `A` this record) |
| lint and type checks where applicable; no full-suite run required | 5, 6, 7 + §"Why no full-suite run" | **yes** — ruff clean, format clean, mypy clean on 83 files |

**Phase 5 verdict: PASS.** Every gate in this change's DOCS/CHORE gate set has a recorded command and result; no test file or behavior was touched; the additional repo-wide `.md`/tooling gates (`check_traceability.py`, `mkdocs build --strict`) also pass, so the deletion broke neither the spec-validation job nor the docs build. The change is verified at its type's light gate. No version bump (DOCS/CHORE → none); `pyproject.toml:4` stays `0.6.0`.

Commit: `docs(remove-spec-tdd-driver): S5 verification report` (this section).
