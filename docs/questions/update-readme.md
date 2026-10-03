# Questions: update-readme

One question file per change, created at **P.1 Frame** from this template and named `update-readme.md`. It replaces the retired central `AI_Questions.md` (archived at `docs/questions/archive-AI_Questions.md`).

- **Change:** update-readme (DOCS/CHORE)
- **TODO file:** `docs/todo/update-readme.md`
- **Spec:** n/a
- **Opened:** 2026-10-03
- **Status:** OPEN  <!-- OPEN | ALL ANSWERED -->  <!-- 5 PENDING: Q-2…Q-6 -->
- **Answer rounds:** 1  <!-- P.2 recorded 6 questions needing user input; 12 interrogation points closed from repository evidence; Q-1 answered 2026-10-04 -->

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

P.2 ran 2026-10-03 in the primary worktree. Result: **6 questions need user input** (Q-1…Q-6, one `BLOCKED-USER` batch, most blocking first), and **12 interrogation points were closed from repository evidence** (E-1…E-12 below) — including the one that decides whether the change is executable at all: the verbatim procedure text **is already in the repository**, so the user does not have to re-paste it.

### Overlap check (P.2 requirement: `docs/specs/` + every TODO in `docs/todo/`)

- **`docs/specs/`** — no spec requires or describes `README.md` or a README procedure (`grep -rn "README" docs/specs` → no match outside vendored noise). No REQ/AC is touched → nothing here contradicts an approved spec → **DOCS/CHORE holds**, no reclassification to ISSUE/REFACTOR.
- **`docs/todo/` (17 change files + template) — three real collisions on `README.md`:**
  - `security-changelog-license` (WAITING) — its own P.2 log already ceded the file to this change: *"Collisions: `update-readme` already owns `README.md` incl. its License section (`update-readme.md:41,58,84,87`) — this change must not write README"* (`docs/todo/security-changelog-license.md:58`), and it plans to add `LICENSE` (`:24`), which is exactly the fact a **License badge** needs. Sequencing decision → **Q-2**.
  - `pyproject-tooling-gaps` (WAITING) — lists `README.md:8` (the `uv sync` quickstart line) among the files it would edit if the docs-group split is taken (`docs/todo/pyproject-tooling-gaps.md:41,51`). Line-level collision only; whichever lands second rebases. Not a blocker, recorded for the Phase 6 review.
  - `structure-map` (WAITING) — plans `.agents/skills/code-structure-map/SKILL.md` + a generated `STRUCTURE.md` (`docs/questions/structure-map.md:215,413-416`). It would own the *structure map* this change also rewrites (`README.md:17-35`). Decision → **Q-4**.
  - No collision with `value-triage-gate` / `spec-interview-protocol` / `workflow-docs-nits` (they edit `AGENTS.md` + `specify/SKILL.md` + the templates, not `README.md` and not a new skill dir), and none with `remove-spec-tdd-driver` (PR #62, one deleted `.ts` file).
- **Backlog verdict already on record:** `docs/questions/value-triage-gate.md:92` scores this change **3/5 — "real gap (30-line README), low value per unit effort" → implement**. The TODO repeats the score and defers the go/no-go to P.3 (`docs/todo/update-readme.md:101-105`) → the go/no-go is **Q-1**.

### Closed from evidence (no user input needed)

1. **E-1 — Current README state.** 35 lines (34 newlines), exactly 4 headings: `# python-template` (`README.md:1`), `## Setup` (`:5`), `## Run` (`:11`), `## Structure` (`:17`). **Zero badges, zero links, zero images** (`grep -nE "img|badge|shields|\[.*\]\(" README.md` → no match). The TODO's "30 lines" is a 5-line understatement — cosmetic, no scope effect. `Status: ANSWERED — Answer source: EVIDENCE`.
2. **E-2 — The README drifts from reality, in three checkable ways.** (a) `README.md:24,27` document `src/frontend/features/` and `src/backend/features/`; the real layout has **no `features/` level** — `src/backend/` holds 11 feature packages directly (`authentication, eventbus, filemanagement, logging, mail, permissions, search, sessionmanagement, settings, shared, usermanagement`) — and `git ls-files src/frontend` → **0 tracked files** (the frontend tree is empty). (b) `README.md:21` says `scripts/ Utility scripts (verify_spec.py)` but `scripts/` holds three (`check_traceability.py`, `validate_task_dag.py`, `verify_spec.py`). (c) The tree omits paths that exist at the root: `userdocs/`, `migrations/`, `alembic.ini`, `.agents/`, `logs/`. This matches `AGENTS.md` "Project Structure" (features directly under `src/backend/`), so the README is the stale artifact, not the code. Whether *this* change fixes it → **Q-4**. `Status: ANSWERED — Answer source: EVIDENCE`.
3. **E-3 — Skill-file format this repo actually uses.** Path convention `.agents/skills/<name>/SKILL.md`; 8 tracked skills (`git ls-files .agents` → 15 paths: 8 `SKILL.md` + 7 `python-best-practices/references/*.md`). Frontmatter has **exactly two keys, `name:` and `description:`** — verified in all 8 (`decompose`, `git`, `implement`, `python-best-practices`, `review`, `specify`, `test`, `verify`); no `version`, `license`, `allowed-tools` or similar anywhere. Names are lowercase and hyphenated (`python-best-practices`), so `update-readme` fits with no rename. Bodies open with a single `# Title` and use free-form `##` sections — there is **no shared section contract** (`git/SKILL.md`: When to Use / Execution Context / Conventions / Todo / Atomic Steps / Operations / Edge Cases / Rules; `python-best-practices/SKILL.md`: Core rules / References / Verify before finishing). Length 45–229 lines, so a ~50-line skill is normal. The user's 5-section layout (Purpose / Inputs / Procedure / Constraints / Output) is therefore **compatible but novel** — no existing skill uses those exact headings; that is not a conflict. `Status: ANSWERED — Answer source: EVIDENCE`.
4. **E-4 — A skill is the right mechanism (not a prompt template, not a `docs/` page).** The repo's only tracked agent-guidance mechanism is `.agents/skills/` (8 skills, one of them — `python-best-practices` — a pure *how-to* skill with no phase mapping, i.e. the exact precedent for a procedure skill). There is **no prompt-template convention in this repository**: `.pi/` contains only `subagents.json` (gitignored pi runtime state), no `prompts/` directory exists, and `AGENTS.md` never mentions prompt templates. A `docs/`-level page is the wrong home: `AGENTS.md` defines `docs/` as the *internal process record* and the published site is built from `userdocs/` (`mkdocs.yml:6` `docs_dir: userdocs`), so a `docs/` page would be neither loaded by the harness nor published. `Status: ANSWERED — Answer source: EVIDENCE`.
5. **E-5 — The verbatim text is recoverable from the repository; the user does NOT need to re-paste it.** `grep -rn "Task: Update the GitHub README" .` → **exactly one match: `docs/todo/update-readme.md:29`**, inside the fenced block at `docs/todo/update-readme.md:28-70` under `## Supplied instruction set (verbatim, re-supplied 2026-10-03)` (`:24`), with the five sections at `:33` (Inspect), `:37` (Badges), `:49` (Structure and content), `:60` (Quality rules), `:67` (Output). P.4 can transcribe the skill body from that block verbatim. **The change is executable without the user re-supplying anything.** `Status: ANSWERED — Answer source: EVIDENCE`.
6. **E-6 — No conflict with the existing skills; one procedural gap, already reconciled.** `python-best-practices` is Python-code conventions (no README/badge content — `grep -rn -i readme .agents/skills/*/SKILL.md` → no match); `git` owns worktree/PR mechanics and is *invoked by* this change, not contradicted by it; the phase skills never mention `README.md`. The only friction is the supplied §5 "Edit `README.md` in place" vs. `AGENTS.md` ("Direct-to-`main` commits are allowed only for the planning records"; `README.md` reaches `main` only through a merged PR) and §5's "list what changed" vs. the evidence trail in `docs/verification/update-readme.md`. Both are **silence, not contradiction**, and the TODO already reconciles them explicitly (`docs/todo/update-readme.md:71-74`). Whether the skill file may therefore carry a short repo-protocol note → **Q-5**. `Status: ANSWERED — Answer source: EVIDENCE`.
7. **E-7 — No registration is required anywhere; the precedent is "don't list it".** Skills are auto-discovered from `.agents/skills/*/SKILL.md` (the harness's live skill list is exactly the 8 tracked directories — no manifest file exists). `AGENTS.md:308-319` "Skill-to-Phase Mapping" lists only the 7 workflow skills; **`python-best-practices` is tracked and loaded but absent from that table**, and the change that tracked it (`docs/todo/track-python-skill.md`, `Status: MERGED`) explicitly put "any change to `AGENTS.md`, the other skills" out of scope (`:28`). No script or CI job validates the skill set (`grep -rn "skills" scripts/*.py` → no match; the three workflows contain no skills step). `userdocs/` has only `api.md` and `index.md` and never mentions skills → mkdocs nav is unaffected. So: **nothing must be updated for the skill to work**; whether to add a discoverability pointer anyway → **Q-6**. `Status: ANSWERED — Answer source: EVIDENCE`.
8. **E-8 — DOCS/CHORE no-behavior-delta proof and the gates that apply.** The diff is two Markdown files (`README.md`, `.agents/skills/update-readme/SKILL.md`) plus the P.4 scope record `docs/verification/update-readme.md`. No `src/`, `tests/`, `pyproject.toml`, `.github/` or config path → **pytest is not the evidence**; `README.md` is referenced only as package metadata (`pyproject.toml:6` `readme = "README.md"`), and the mkdocs site builds from `userdocs/` (`mkdocs.yml:6`), so `uv run mkdocs build --strict` cannot be affected but is cheap Phase 5 evidence. Gates that apply per `AGENTS.md` Phase Matrix (DOCS/CHORE → "Light: lint/types where applicable") and Phase 5 item 16: **ruff** (nothing to lint — ruff checks Python only; the `.pre-commit-config.yaml:14-17` ruff hooks never touch `.md`), **mkdocs build --strict**, and **`uv run python scripts/check_traceability.py`** (referential integrity — unaffected, no new spec IDs). Two pre-commit hooks **do** apply to Markdown: `trailing-whitespace` and `end-of-file-fixer` (`.pre-commit-config.yaml:19-20`) — note `.editorconfig:9-10` sets `trim_trailing_whitespace = false` for `*.md`, but the pre-commit hook does not read `.editorconfig`, so **markdown hard line breaks (two trailing spaces) will be stripped** — the skill/README must not rely on them. `Status: ANSWERED — Answer source: EVIDENCE`.
9. **E-9 — Version bump: none.** `AGENTS.md` Versioning bump mapping: "REFACTOR / DOCS-CHORE → none". No `bump-my-version bump` commit in Phase 6; `version = "0.6.0"` (`pyproject.toml:4`) stays. `Status: ANSWERED — Answer source: EVIDENCE`.
10. **E-10 — Which CI jobs actually run for this diff (and which do not).** `Quality` has **no path filter** (`quality.yml:3-7`) → all 7 jobs run: `type-check` (mypy gate), `security` (pip-audit, bandit), `coverage` (`pytest --cov`, `pyproject.toml:105` `fail_under = 92`), `dependency-review`, `dependencies` (deptry), `docs` (`mkdocs build --strict`, `quality.yml:109`), `migrations`. `Spec Validation` **does** run, because the change adds `docs/verification/update-readme.md` and its filter lists `docs/verification/**` (`spec-validation.yml:9`) → `spec-validation`, `traceability`, `tests` jobs run. `Lint` **does not run** — its path filter is `src/**`, `tests/**`, `pyproject.toml`, `.pre-commit-config.yaml`, `.github/workflows/lint.yml`, `.github/hooks/**` (`lint.yml:6-21`), none of which this change touches. Consequence: the ruff gate for this change is **local-only**, and a **Lint-status badge** reflects the last `main` run of a workflow that skips doc-only changes — its status can read stale/"skipped" for exactly this kind of PR. `Status: ANSWERED — Answer source: EVIDENCE`.
11. **E-11 — Badge facts that are settled, and the one that is not.** Settled from the repo: `owner/repo = jackthenet/python-template` (`git remote get-url origin` → `https://github.com/jackthenet/python-template`); three workflows `lint.yml` / `quality.yml` / `spec-validation.yml`; `requires-python = ">=3.14"` (`pyproject.toml:7`); **no `LICENSE` file** (`ls LICENSE*` → none) and no `license` field → the skill's own rule ("only badges backed by something real", `docs/todo/update-readme.md:57`) **forbids a License badge today**; **not published to any registry** (no publish/release workflow among the three files) → no version/downloads badge; coverage **is** configured (`pytest-cov`, `fail_under = 92`, the `coverage` job) but **no external coverage service** exists → the coverage badge is the genuinely ambiguous case → **Q-3**. Not settleable offline at all: the *live status* a workflow badge would show depends on GitHub run history (no network in this step) — P.4 must phrase such badges so they cannot lie, and flag the unverifiable ones in the report as the supplied §5 requires. `Status: ANSWERED — Answer source: EVIDENCE`.
12. **E-12 — "Contributing" / "License" sections the supplied §3 lists.** §3 says "skipping sections that don't apply" (`docs/todo/update-readme.md:49`), and the TODO puts `LICENSE` / `CONTRIBUTING.md` / Codecov / PyPI out of scope (`:86-88`). So the skill's 8-section order is satisfiable by omission without inventing anything, and no contradiction with `AGENTS.md` arises. `Status: ANSWERED — Answer source: EVIDENCE`.

### Open questions (need user input)

## Q-1 — Is the change the skill file only, or skill + README rewrite now?
- **Step:** P.2 Interrogate
- **Why needed:** The TODO scopes **two** deliverables (skill + rewritten `README.md`, `docs/todo/update-readme.md:76-80`) but its own value triage defers the go/no-go to P.3 ("Decision: user asked for the TODO file; implementation decision pending at P.3", `:105`). The two halves have very different cost and different collision surfaces: the skill alone is a 1-file addition with zero collisions; the README rewrite collides with three other backlog changes (E: Overlap check).
- **Context:** README is 35 lines with no badges/links and three factual errors (E-1, E-2). Backlog score is 3/5 "implement" (`docs/questions/value-triage-gate.md:92`).
- **Question:** Which scope do you want? (a) **Both** — add the skill and apply it to `README.md` in this one change (the TODO's current scope, one PR, 2 files); (b) **Skill only** — commit `.agents/skills/update-readme/SKILL.md` now and run it as a separate change later; (c) **README only** — apply the procedure without tracking a skill (then the "reusable procedure" rationale in `docs/todo/update-readme.md:22` is not delivered); (d) **Drop** — the skill is guidance nothing consumes until a README change actually runs.
- **Answer:** **(a) Both** — add the skill and apply it to `README.md` in this one change (the TODO's current scope: `.agents/skills/update-readme/SKILL.md` + `README.md`, one PR).
- **Date:** 2026-10-04
- **Status:** ANSWERED
- **Incorporated:** yes — scope confirmed; the remaining questions (Q-2…Q-6) now set the content of both files

## Q-2 — Sequence this change before or after `security-changelog-license` (the License badge)?
- **Step:** P.2 Interrogate
- **Why needed:** A License badge is impossible today (no `LICENSE` file — E-11), and the skill forbids inventing one. But `security-changelog-license` (WAITING) is the change that would add `LICENSE`, and it has already ceded `README.md` to this change ("this change must not write README", `docs/todo/security-changelog-license.md:58`). So the two changes are mutually blocking in one direction: whoever writes README first owns it, and the license badge can only exist after the other lands.
- **Context:** `docs/todo/security-changelog-license.md:24` (LICENSE in scope, choice is the user's), `:58` (collision note). `docs/todo/update-readme.md:86-88` puts adding a LICENSE out of scope here.
- **Question:** Do you want (a) **this change now, no License badge** (README gets CI/Python/tooling badges; the License badge is added by `security-changelog-license` later — that change then needs a small README edit, reversing its own "must not write README" note); (b) **wait** — land `security-changelog-license` first (LICENSE + SECURITY + CHANGELOG), then this change adds the full badge row including License; or (c) **this change now and you accept** that the License badge is permanently a follow-up?
- **Answer:** **PENDING**
- **Date:** 2026-10-03
- **Status:** PENDING
- **Incorporated:** no

## Q-3 — Coverage badge: static, workflow-linked, or omitted?
- **Step:** P.2 Interrogate
- **Why needed:** Flagged as "the one genuinely ambiguous case" in the TODO (`docs/todo/update-readme.md:99`) and explicitly assigned to P.2. Coverage *is* configured (`pytest-cov`, `pyproject.toml:105` `fail_under = 92`, the `coverage` job in `quality.yml:45-59`) but **no coverage service** (Codecov etc.) exists, so a shields.io coverage badge has no live data source.
- **Context:** The skill's rule is "Never invent URLs or badges for services the project doesn't use" (`docs/todo/update-readme.md:47`) and "Badge honesty is the whole point" (`:98`). A static `?message=92%25` badge is a hand-maintained number that drifts the moment coverage moves — the TODO calls that a defect, not polish.
- **Question:** (a) **No coverage badge** — the CI badge already links the `Quality` run that enforces the gate (strictly honest, nothing to maintain); (b) **static badge** pinned to the current `fail_under` threshold (e.g. "coverage ≥ 92%") worded as a *gate*, not a measurement — needs no maintenance but reads like a metric; (c) **static measured value** (drifts — the TODO's stated defect); (d) add a Codecov/upload step (out of scope here — it is a `.github/workflows/` change, i.e. a separate change).
- **Answer:** **PENDING**
- **Date:** 2026-10-03
- **Status:** PENDING
- **Incorporated:** no

## Q-4 — Fix the wrong `Structure` tree here, or leave it to `structure-map`?
- **Step:** P.2 Interrogate
- **Why needed:** The README's `Structure` section is factually wrong (E-2: no `features/` level, `src/frontend/` has 0 tracked files, `scripts/` list incomplete, `userdocs/`/`migrations/`/`alembic.ini`/`.agents/` missing). The TODO's acceptance signal says the current tree must stay "accurate" (`docs/todo/update-readme.md:107`) — which can be read as *preserve as-is* or *correct it*. The two readings produce different diffs, and a third change plans to own structure maps.
- **Context:** `structure-map` (WAITING) would add `.agents/skills/code-structure-map/SKILL.md` + a generated `STRUCTURE.md` (`docs/questions/structure-map.md:215`). `AGENTS.md` "Project Structure" already documents the correct layout, so a corrected README tree duplicates it by hand — and hand-maintained trees are exactly what drifted here.
- **Question:** (a) **Correct the tree by hand in this change** (fix `features/`, drop the empty frontend or mark it "not yet implemented", list the real root paths) — biggest diff, and it will drift again; (b) **Trim it** — replace the tree with a 4-line summary plus a relative link to `AGENTS.md` "Project Structure" (smallest honest diff, single source of truth); (c) **Leave it untouched** and let `structure-map` fix it (this change then ships a README that is still wrong in the one section it preserved).
- **Answer:** **PENDING**
- **Date:** 2026-10-03
- **Status:** PENDING
- **Incorporated:** no

## Q-5 — Verbatim skill body only, or verbatim + a short repo-protocol note?
- **Step:** P.2 Interrogate
- **Why needed:** The TODO says "verbatim, no editorial rewrite" (`docs/todo/update-readme.md:77`) and "the skill file is committed as supplied; content edits beyond a recorded conflict fix exceed the no-behavior-delta scope" (`:100`). The supplied §5 ("Edit `README.md` in place. Afterwards, list what changed") is silent on this repo's PR-only rule and its evidence trail — silence, not contradiction (E-6), and the TODO already reconciles it in prose (`:71-74`). Whether that reconciliation lives *outside* the skill (TODO only) or *inside* it (a 2–3 line note) is a content decision only you can make, and it decides whether P.4's file is byte-identical to `docs/todo/update-readme.md:28-70`.
- **Context:** The skill is generic (it says "`pyproject.toml` / `package.json` (or equivalent)"), so a repo-specific note would make it less reusable across projects — the stated rationale for tracking it at all (`docs/todo/update-readme.md:22`).
- **Question:** (a) **Strictly verbatim** — the skill body is exactly the recorded text; the repo reconciliation stays in the TODO/verification record only (an agent reading just the skill could edit `README.md` directly on `main`); (b) **Verbatim + a 2–3 line "Repo protocol" note** appended, pointing at the change-worktree/PR rule and `docs/verification/<name>.md`; (c) **Verbatim + the note phrased generically** ("respect the repository's own contribution workflow and record its evidence") to keep the skill portable.
- **Answer:** **PENDING**
- **Date:** 2026-10-03
- **Status:** PENDING
- **Incorporated:** no

## Q-6 — Should the new skill be listed anywhere for discoverability?
- **Step:** P.2 Interrogate
- **Why needed:** Nothing *must* be registered for the skill to load (E-7: auto-discovery, no manifest, no CI/script check, mkdocs unaffected). But `AGENTS.md:308-319` "Skill-to-Phase Mapping" is the only human-facing index, and `python-best-practices` — the closest precedent, a non-phase how-to skill — is deliberately **not** in it. Whether a README-refresh procedure should be findable from `AGENTS.md` is a documentation decision, and editing `AGENTS.md` widens the diff and collides with `value-triage-gate` / `workflow-docs-nits` (both edit `AGENTS.md`).
- **Context:** `docs/todo/track-python-skill.md:28` set the precedent (skill tracked, `AGENTS.md` explicitly out of scope). `AGENTS.md` Phase 6 item 9 tells agents to document reusable shared capabilities in `AGENTS.md` — but that obligation is scoped to FEATURE/CROSS-CUTTING, so it does not apply to this DOCS/CHORE change.
- **Question:** (a) **No listing** — follow the `python-best-practices` precedent; the harness surfaces the skill by description (recommended by evidence); (b) **One line in `AGENTS.md`** (e.g. a "non-phase skills" note) — discoverable for humans, but a second file in the diff and a possible conflict with two WAITING changes; (c) **A line in `userdocs/`** — publishes it, but the docs site is user-facing product docs, not agent tooling.
- **Answer:** **PENDING**
- **Date:** 2026-10-03
- **Status:** PENDING
- **Incorporated:** no

### Category coverage

DOCS/CHORE has **no ≥ 20-question floor** (`AGENTS.md` P.2 done-criteria and the `specify` skill's Rules apply the floor to FEATURE/CROSS-CUTTING only; precedent: `docs/questions/remove-spec-tdd-driver.md:28` recorded 0 questions for a DOCS/CHORE change). Interrogation covered 18 points; 12 closed from evidence, 6 became questions.

| Category | Covered? | Where |
|---|---|---|
| Current state / baseline facts | yes | E-1, E-2 |
| Format & convention compliance | yes | E-3 |
| Mechanism choice (skill vs prompt template vs docs page) | yes | E-4 |
| Recoverability of the supplied input | yes | E-5 |
| Conflict / overlap with existing guidance & other changes | yes | E-6, Overlap check, Q-2, Q-4 |
| Registration / discoverability | yes | E-7, Q-6 |
| No-behavior-delta proof & applicable gates | yes | E-8 |
| CI jobs that will actually run | yes | E-10 |
| Version bump | yes | E-9 (none) |
| Factual honesty of the output (badges) | yes | E-11, E-12, Q-3 |
| Scope boundary / go-no-go | yes | Q-1 |
| Sequencing with in-flight & backlog changes | yes | Q-2, Q-4 |
| Content fidelity vs. local adaptation | yes | Q-5 |
| Edge cases (empty `src/frontend/`, path-filtered workflows, pre-commit whitespace hook) | yes | E-2, E-10, E-8 |
| Data/API contracts, validation schemas | **skipped** | no schema, model or interface is touched — Markdown only |
| Error handling / failure modes | **skipped** | no executable code; the only failure mode is a wrong badge, handled as a content rule (E-11) |
| Security | **skipped** | no secret, auth or input-handling path; the skill's own "never invent a badge URL" rule is the only safety constraint (E-11) |
| Performance / concurrency / dependency / licensing / testability | **skipped** | no runtime, no new dependency, no test-visible behavior; adding a `LICENSE` is explicitly out of scope here and is `security-changelog-license`'s decision (Q-2) |

### Classification verdict

**DOCS/CHORE holds** (criterion #5: documentation/tooling, no behavior change). Evidence: the diff is two Markdown files plus the P.4 scope record; no `src/`, `tests/`, `docs/specs/`, `.github/workflows/` or config path is touched; `README.md` is consumed only as package metadata (`pyproject.toml:6`) and the mkdocs site builds from `userdocs/` (`mkdocs.yml:6`); no approved spec requires or describes the README (Overlap check). No escalation trigger fired — the supplied skill's silence about the PR/evidence trail is reconciled in the TODO, not a contradiction (E-6). **Reclassification watch-outs for P.4/P.6:** if the answer to Q-1/Q-2 pulls a `LICENSE`, `CONTRIBUTING.md` or a coverage-upload workflow step into this diff, that is a different change (`security-changelog-license` / a CI change) and this one must not absorb it; if the skill body is edited beyond Q-5's chosen option, the "no content edit" constraint (`docs/todo/update-readme.md:100`) is violated and Phase 6 must flag it.

### Recommendation

**Do it, and keep it to two files.** This is a genuinely small chore: the skill is a ~50-line Markdown file transcribed verbatim from `docs/todo/update-readme.md:28-70` (E-5 — nothing needs re-pasting), and the README rewrite is one file. Cost: one DOCS/CHORE change (Phase P → Phase 4 → light Phase 5 → light review → PR), **no version bump** (E-9), no spec, no task DAG, no tests. The visible payoff is real — the front page currently shows no CI status, no Python version, no way to run the checks, and a structure tree that is wrong in three ways (E-1, E-2).

Minimal recommended scope, if you want the cheapest honest version: **Q-1 (a) both halves, Q-2 (a) now without a License badge, Q-3 (a) no coverage badge, Q-4 (b) trim the tree and link `AGENTS.md`, Q-5 (c) verbatim + one generic protocol line, Q-6 (a) no listing.** That is 2 files, 4–5 badges that all point at things that exist (`Quality`, `Lint`, `Spec Validation`, Python 3.14, Ruff/uv/pre-commit), and every unverifiable claim left out rather than guessed — which is the skill's own rule applied to itself.

If you would rather not spend a change on the front page, the honest alternative is **Q-1 (b)**: track the skill (1 file, zero collisions, reusable) and defer the README rewrite until after `security-changelog-license` and `structure-map` land, so the badge row and the structure section are written once against facts that already exist. What is **not** worth doing is Q-1 (d) plus keeping the procedure in the TODO — the text is already recorded there, so a skill that is never applied adds a file for no benefit.

### For P.4 (scope record) — what is still outstanding

Blocked on Q-1…Q-6. Once answered, the scope record writes itself: the exact file list (skill + `README.md`), the verbatim source block (`docs/todo/update-readme.md:28-70`), the badge allow-list with the fact behind each (E-11), the forbidden badges and why (License — no `LICENSE`; PyPI/downloads — not published; coverage — per Q-3), the no-behavior-delta proof (E-8), the applicable gates (ruff local-only, `mkdocs build --strict`, `scripts/check_traceability.py`, pre-commit whitespace hooks), the CI jobs that will run and which will not (E-10), and the "flag what could not be verified" list — badge *status* on GitHub is not observable offline (E-11).

## Late questions (Phases 2–6)

<questions discovered after the change entered the workflow; same entry format, Step field set to the step that found it>
