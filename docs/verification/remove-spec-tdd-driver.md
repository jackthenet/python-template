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
