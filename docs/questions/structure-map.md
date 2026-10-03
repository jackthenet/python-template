# Questions: structure-map

One question file per change, created at **P.1 Frame** from this template and named `structure-map.md`. It replaces the retired central `AI_Questions.md` (archived at `docs/questions/archive-AI_Questions.md`).

- **Change:** structure-map (FEATURE)
- **TODO file:** `docs/todo/structure-map.md`
- **Spec:** `docs/specs/structure-map.md`
- **Opened:** 2026-10-03
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

_P.2 Interrogate ran 2026-10-03: **27 new questions (Q-4 … Q-30)**, one `BLOCKED-USER` batch, most-blocking first. The three instruction-vs-convention conflicts found at P.1 (Q-1…Q-3) are already answered and do **not** count toward the P.2 minimum; the fourth P.1 flag (change type) is Q-4 below._

### P.2 interrogation record (coverage, evidence, overlap)

**Category coverage** (P.2 adversarial interrogation):

| Category | Result | Where settled |
|---|---|---|
| Change type / classification | asked | Q-4 |
| "Does something already do this?" (Ponytail rungs 1–2) | asked + verdict below | Q-5 |
| Artifact committed vs. generated (churn, conflicts) | asked | Q-6, Q-15 |
| Output format, size budget, truncation | asked (measured, see below) | Q-7, Q-8, Q-9 |
| Test strategy & test placement vs. spec coverage | asked | Q-10, Q-28 |
| Architecture rules / `shared/` boundary | asked + evidence (no `tests/architecture/` exists) | Q-11, Q-12 |
| Workflow integration (who calls it, when; P.1 hook) | asked | Q-13, Q-14 |
| CLI surface (`--max-depth`, `--include-private`, `--check`, `--root/--out`) | asked | Q-16, Q-17, Q-22, Q-23, Q-30 |
| Public-API extraction (`__init__.py`, fields, decorators, dunders) | asked | Q-17…Q-20 |
| Determinism (ordering, paths, whitespace) | asked + evidence | Q-21, Q-24 |
| Docstring/summary normalization | asked | Q-25 |
| Error handling (parse errors, undecodable, missing output) | asked | Q-23, Q-26 |
| Signature rendering & grammar version | asked | Q-27 |
| Performance (NFR) | asked | Q-29 |
| Settings / events / tracing | **closed from evidence** (see below) | — |
| Permissions / readability / secrets | **closed from evidence** (see below) | — |
| Dependencies | **closed from evidence** (stdlib-only; deptry stays clean) | — |
| mkdocs interaction | **closed from evidence** (`mkdocs.yml:6` `docs_dir: userdocs`) | — |

**Closed from evidence (no question spent):**
- **Settings / event bus / tracing do not apply.** AGENTS.md scopes those mandates to "new backend features" under `src/backend/`; the generator is repo tooling in `scripts/` (precedent: `scripts/check_traceability.py`, `scripts/verify_spec.py` — no logging, no DI, no events). If Q-12 places code under `src/backend/shared/`, this answer flips.
- **Permissions/readability:** the map contains only tracked paths, line counts, signatures and docstring first lines — no bodies, no secrets; every tracked file is already readable in the repo, so no filtering is required.
- **Dependencies:** stdlib-only (`ast`, `pathlib`, `argparse`) keeps `deptry` clean; `deptry` already scans `scripts/` (`.pre-commit-config.yaml`, `files: ^(pyproject\.toml|uv\.lock|src/|tests/|scripts/|migrations/)`).
- **mkdocs is unaffected:** `docs_dir: userdocs` (`mkdocs.yml:6`), so a root `STRUCTURE.md` is not a site page and `mkdocs build --strict` cannot warn about it.
- **Coverage floor gives the new tests no credit:** `[tool.coverage.run] source = ["src/backend", "src/frontend"]`, `fail_under = 92` (`pyproject.toml:101,105`) — a `scripts/` test file is outside the measured source.
- **`complexipy` WILL see the new test file:** `[tool.complexipy] paths = ["src", "tests"]`, `max-complexity-allowed = 30` (`pyproject.toml:92-94`); `scripts/` itself is not analyzed.
- **Test placement precedent:** `tests/unit/` already holds top-level `test_settings_coverage.py` and `test_settings_test_isolation.py` alongside per-feature dirs, so `tests/unit/test_make_map.py` needs no new directory.
- **`src/frontend/` is empty** (only `src/backend/`, `src/main.py` are populated) — the map will show a placeholder package; AGENTS.md's "Project Structure" tree (`model/`, `services/`) is aspirational: `src/backend/settings/` is flat (`__init__.py exceptions.py feature_actions.py models.py registry.py repository.py`), and the only nested dir under `src/backend/` is `filemanagement/assets`.
- **Path depth:** 82 of 84 tracked `src/` files sit at depth 4 (`src/backend/<feature>/<module>.py`) — a `--max-depth 3` default would erase all of `src/backend/` (feeds Q-16).
- **Docstring availability:** all 83 `src/` modules have a module docstring; 42 of 233 `tests/` modules have none — a tests-included map would render 42 empty summary lines (feeds Q-8).

**Measured sizes (the 400-line budget is the load-bearing risk; `git ls-files` = 548 tracked files, 323 `.py`):**

| Scope | files | lines | classes | methods | top-level defs | ≈ map lines (symbols + module headers) |
|---|---|---|---|---|---|---|
| `src/` | 83 | 10 413 | 204 | 407 | 126 | **≈ 820** |
| `tests/` | 233 | 21 102 | 53 | 156 | 944 | **≈ 1 386** |
| `scripts/` | 3 | 409 | 1 | 0 | 15 | ≈ 19 |
| `migrations/` | 3 | 301 | 0 | 0 | 14 | ≈ 17 |
| Directory tree (one line per tracked path) | 548 | — | — | — | — | **≈ 548** |

So: the **directory tree alone (≈548 lines) already exceeds the 400-line budget**, and `src/`-only modules add ≈820 more. Any policy that keeps the budget must drop either tree breadth or module depth — this is Q-7/Q-8/Q-9, not an edge case.

**Overlap & collision analysis** (all 13 `docs/specs/` files, all 16 `docs/todo/` items, worktrees/branches/PRs):
- **Specs:** no `docs/specs/` file specifies a code-structure map, a generator, or a repo-layout artifact. The only structure-adjacent text is `docs/specs/user-roles-permissions.md:34,484` (D14: `Principal`/`PermissionChecker`/`requires_permission` live in `src/backend/shared/`) and the per-spec "Package layout" blocks (`user-management.md:198`, `user-roles-permissions.md:471`). Nothing to extend; no spec is touched → "Related specs: none" in the TODO holds.
- **`src/backend/shared/` today = `__init__.py` + `principal.py` only** — deliberately small, exactly as AGENTS.md requires. A repo-map generator is not domain plumbing, so it does not belong there (Q-12).
- **TODO collisions:** `value-triage-gate` (WAITING) edits `AGENTS.md` Phase-P table / Phase Matrix / Workflow Diagram / Agent Obligations + Prohibitions and `.agents/skills/specify/SKILL.md` P.1/P.2 area (`docs/todo/value-triage-gate.md:51`); `workflow-docs-nits` (WAITING, scored 2/5, recommended "merge into #1 or drop" at `value-triage-gate.md:93`) edits `specify/SKILL.md:14,45,46`. This change's Q-13/Q-14 hook text would land in the **same files** (`AGENTS.md` Agent Obligations / Tooling, `specify/SKILL.md` P.1). `docs/questions/value-triage-gate.md:122` already triaged structure-map as "a different section (tooling), mergeable, no line conflict" — that still holds **only if** the hook stays a one-line pointer in AGENTS.md "Tooling & Execution Environment" and does not touch the Phase P table or Obligation 1. If the user picks the "P.1 must cite the map" option (Q-13), it **becomes a line conflict** with `value-triage-gate` and the two PRs must be sequenced.
- **Other TODOs:** no overlap with `api-keys`, `notifications`, `pyproject-tooling-gaps`, `python-3.15`, `remove-spec-tdd-driver`, `security-changelog-license`, `spec-interview-protocol`, `split-archived-qa`, `structlog-logging`, `tenacity-rich-cachetools`, `update-readme`, `docs-path-ci-trigger`, `track-python-skill` (MERGED — it tracked `.agents/skills/python-best-practices/`, which is why a new skill dir is the right home, Q-14).
- **In-flight work:** one worktree only — `chore/remove-spec-tdd-driver` (PR #62 OPEN, deletes the unused spec-tdd driver under `.github/`). It touches no file this change touches (`scripts/`, `STRUCTURE.md`, `.pre-commit-config.yaml`, `AGENTS.md`, `.agents/skills/`) — except that deleting the driver changes tracked-file counts the map reports, so the map must be regenerated after #62 merges. No branch collision.

**"Does something already do this?" verdict (Ponytail rungs 1–2):** nothing in the repo produces a codebase overview. `mkdocstrings` (`mkdocs.yml`, `userdocs/api.md`) renders per-module API pages for humans — not one agent-readable file, no tree, no line counts. `scripts/check_traceability.py` / `verify_spec.py` analyse docs, not code. `python-best-practices/references/structure.md` is convention text (where code *should* go), not a map of what is here. **Honest caveat:** a shell one-liner (`git ls-files '*.py' | xargs wc -l`, plus `rg -n '^(class|def|async def) '`) already covers roughly 80% of the tree + signature value with zero new code — what it does not give the agent is docstring summaries, base classes, determinism, or a single cached file. That trade-off is Q-5, not a silent spec decision.

**For P.4 (draft spec)** — inputs the answers below feed:
- REQ set must pin: file-set source (Q-22), path form (Q-21), symbol-selection rules (Q-17…Q-20), summary normalization (Q-25), size/truncation policy (Q-7…Q-9), `--check` contract (Q-23), CLI path resolution (Q-30).
- INV set: byte-identical output on unchanged code (Q-24); no absolute paths / timestamps / host data; output passes `trailing-whitespace` + `end-of-file-fixer` unchanged (both are active hooks in `.pre-commit-config.yaml`) — otherwise the hook and the formatter fight each other.
- EDGE set: syntax-error file, empty file, undecodable file, missing `STRUCTURE.md`, non-git root, file with no docstring (42 exist in `tests/`), a package whose modules exceed the per-section cap, `--max-depth` smaller than the real depth (all of `src/backend/` is depth 4).
- NFR set: run time (Q-29), stdlib-only, ≤ ~250 lines of typed code (Q-28 gate question).
- Test strategy: acceptance (CLI-level) + unit (parser) split per Q-10; every AC/INV/EDGE mapped to a named test function.
- Do **not** reference `tests/architecture/` in the spec — the directory does not exist (see Q-11).

---

## Q-4 — Change type: FEATURE or DOCS/CHORE
- **Step:** P.2 Interrogate (the fourth P.1 conflict, still open)
- **Why needed:** The type decides whether a spec + approval PR + `minor` bump exist at all, and which phases run. The TODO classified FEATURE by first-match (#2 before #5) but flagged that P.2 may re-examine it.
- **Context:** The change ships a CLI with observable exit codes, a generated artifact, and a pre-commit gate that can fail a commit — but touches no `src/` or `tests/` product behavior. `docs/todo/structure-map.md` "Classification note".
- **Question:** Keep **FEATURE** (spec + approval PR + `minor` bump, Phases 1–6), or downgrade to **DOCS/CHORE** (no spec, no bump, Phase 4 direct, requirement set lives in the scope record)?
  - A. FEATURE (as classified) — the new capability + failing-able gate is externally observable tooling behavior.
  - B. DOCS/CHORE — cheaper, but loses the spec and the 100%-spec-coverage evidence trail for ~27 decisions.
  - **Recommendation: A (FEATURE)** — first-match rule #2 applies; the `--check` exit code is observable behavior, not "no behavior change".
- **Answer:** **PENDING**
- **Date:** 2026-10-03
- **Status:** PENDING
- **Incorporated:** no

## Q-5 — Is the generator worth building at all (vs. a one-liner)?
- **Step:** P.2 Interrogate
- **Why needed:** Ponytail rung 1–2 ("does this need to be built? / does it already exist?"). The honest answer is "nothing exists, but a `git ls-files` + `rg` one-liner covers ~80% of the value with zero new code" — that is a user decision, not a silent spec choice.
- **Context:** Measured cost side: 548 tracked files, 323 `.py`, 32 343 lines; the map must be kept fresh by a hook on every `.py` commit. What the one-liner cannot do: docstring summaries, base classes, deterministic single-file artifact, cached read.
- **Question:** Build the full deliverable (script + map + skill + hook), or shrink to the cheap version — a skill + an AGENTS.md line telling agents to run `git ls-files '*.py' | xargs wc -l` / `rg '^(class|def) '` on demand, with no committed artifact and no hook?
  - A. Full deliverable (as the instruction states).
  - B. Script + skill, **no committed map, no hook** (generate on demand — see Q-6).
  - C. Skill + one-liner only (no script).
  - **Recommendation: A** if the map is committed and kept fresh (the value is one cheap read per task); otherwise B.
- **Answer:** **PENDING**
- **Date:** 2026-10-03
- **Status:** PENDING
- **Incorporated:** no

## Q-6 — Is `STRUCTURE.md` committed to git, or generated on demand?
- **Step:** P.2 Interrogate
- **Why needed:** Decides whether the freshness gate (`--check`) exists at all, and whether every change branch carries a generated ~400-line diff.
- **Context:** Q-2 already chose a check-only pre-commit hook, which only makes sense for a committed file. A committed map means: every commit touching a `.py` file must regenerate it; PR diffs contain generated noise; parallel worktrees both rewrite it (Q-15).
- **Question:** Commit `STRUCTURE.md` (hook enforces freshness), or gitignore it and have the skill regenerate it when missing/stale?
  - A. Committed + check-only hook (instruction-faithful; the map is always readable without running anything).
  - B. Gitignored + generated on demand (zero PR noise, no hook friction, but an agent may read a stale/absent map).
  - **Recommendation: A**, with the regeneration duty stated in the skill and in the AGENTS.md line, and the map section kept small (Q-7…Q-9) so the diff stays readable.
- **Answer:** **PENDING**
- **Date:** 2026-10-03
- **Status:** PENDING
- **Incorporated:** no

## Q-7 — The 400-line budget: exact truncation policy
- **Step:** P.2 Interrogate
- **Why needed:** The instruction's "if it exceeds about 400 lines, group by package and truncate with a note" is load-bearing here, not an edge case, and it is not deterministic as written. Measured: tree alone ≈548 lines; `src/` modules ≈820; `tests/` ≈1 386.
- **Context:** `docs/todo/structure-map.md` "Constraints and risks" already flags this. Options below are mutually compatible in part; the answer must be precise enough to implement deterministically and to test.
- **Question:** What is the size policy?
  - A. **Raise the budget** to ~900–1 000 lines and cover `src/` + `scripts/` + `migrations/` fully (tree limited to code dirs) — no elision, no information loss, still one read.
  - B. **Keep 400**: per-module cap (e.g. max 8 methods per class, max 12 symbols per module) + `… +N more` elision markers, and per-package grouping.
  - C. **Keep 400**: drop whole low-value packages (`tests/`, `migrations/`) from the Modules section and cap per-class methods.
  - D. Two artifacts: a small always-committed `STRUCTURE.md` (tree + package summaries) and an optional `--full` run.
  - **Recommendation: A with a hard cap per class (B's cap as a safety valve)** — elision rules are the part most likely to silently hide the file an agent needs; a 900-line file is still ~15k tokens, well inside budget for the payoff.
- **Answer:** **PENDING**
- **Date:** 2026-10-03
- **Status:** PENDING
- **Incorporated:** no

## Q-8 — Does the Modules section cover `tests/`?
- **Step:** P.2 Interrogate
- **Why needed:** `tests/` is 233 of 323 `.py` files and ≈1 386 map lines — the single biggest budget decision after Q-7. It also changes what the map is *for* (finding implementation vs. finding the test that covers it).
- **Context:** 42 of 233 test modules have no module docstring (empty summary lines); test files are mostly `def test_*` (944 top-level defs) whose names are already greppable; `tests/*_test_helpers.py` are the shared fixtures an agent does need to discover.
- **Question:** Include `tests/` in the Modules section, list only `tests/*_test_helpers.py` + `conftest.py`, or keep tests in the directory tree only?
  - **Recommendation: helpers + `conftest.py` only** (that is the discovery value; test-function lists are cheaper via `rg`).
- **Answer:** **PENDING**
- **Date:** 2026-10-03
- **Status:** PENDING
- **Incorporated:** no

## Q-9 — Directory-tree scope
- **Step:** P.2 Interrogate
- **Why needed:** A tree of all 548 tracked paths blows the budget by itself, and `docs/` (179 files) is process record, not code an agent navigates.
- **Context:** Tracked files by top dir: `tests` 238, `docs` 179, `src` 84, `.agents` 15, `.github` 9, `migrations` 6, `scripts` 3, `userdocs` 2, plus root config files.
- **Question:** Which trees appear — all tracked paths, or code dirs (`src/ tests/ scripts/ migrations/`) with a one-line count for the rest (`docs/`, `userdocs/`, `.github/`, `.agents/`)? Any depth cap on the tree itself (distinct from `--max-depth`, Q-16)?
  - **Recommendation: code dirs in full, everything else as a one-line summary** (`docs/ — 179 files (process record)`).
- **Answer:** **PENDING**
- **Date:** 2026-10-03
- **Status:** PENDING
- **Incorporated:** no

## Q-10 — Test strategy: where do the FEATURE's acceptance tests live?
- **Step:** P.2 Interrogate
- **Why needed:** Phase 3 requires acceptance tests derived from the ACs and Phase 5 requires spec coverage = 100%, but this change adds no `src/` code — so "acceptance test" has no obvious home, and coverage gives the new tests no credit (`pyproject.toml:101`).
- **Context:** `tests/unit/` already has top-level `test_settings_coverage.py` / `test_settings_test_isolation.py`; `tests/acceptance/` is per-feature today; the instruction asks for parser tests (nested classes, async, decorators, syntax-error, empty files) plus determinism and `--check`.
- **Question:** Split as `tests/acceptance/test_structure_map.py` (CLI end-to-end: run the script, assert the file, run `--check` exit codes) + `tests/unit/test_make_map.py` (parser internals), or all under `tests/unit/`, or a new `tests/unit/scripts/` dir?
  - **Recommendation: the two-file split** — the CLI contract is the acceptance surface (AC/INV/EDGE trace to it), the parser detail is unit.
- **Answer:** **PENDING**
- **Date:** 2026-10-03
- **Status:** PENDING
- **Incorporated:** no

## Q-11 — Generator vs. architecture rules: which wins (and `tests/architecture/` does not exist)
- **Step:** P.2 Interrogate
- **Why needed:** The step brief asked me to "confirm `tests/architecture/` permits a new `shared/` module" — **there is no `tests/architecture/` directory in this repo** (`find` → no match), yet `AGENTS.md` Phase 5 (REFACTOR) and the `review` skill reference `uv run pytest tests/architecture/ -v`. The prescribed "Project Structure" (`model/`, `services/`, `shared/`) also does not match reality: `src/backend/settings/` is flat, the only nested dir under `src/backend/` is `filemanagement/assets`, and `src/frontend/` is empty.
- **Context:** A generated map is by construction descriptive — it will print the flat layout and the empty `frontend/`, which reads as a contradiction of AGENTS.md.
- **Question:** (a) When the map and AGENTS.md's prescribed structure disagree, which wins — is the map explicitly declared **descriptive, never normative** (AGENTS.md stays the contract)? (b) Is adding a `tests/architecture/` check (asserting the prescribed layout) in scope, out of scope, or a separate TODO? (c) Should the AGENTS.md references to the non-existent `tests/architecture/` be recorded as a new backlog item?
  - **Recommendation: (a) map is descriptive, stated as an INV; (b) out of scope; (c) yes, open a separate DOCS/CHORE TODO.**
- **Answer:** **PENDING**
- **Date:** 2026-10-03
- **Status:** PENDING
- **Incorporated:** no

## Q-12 — Does any code live under `src/backend/shared/`?
- **Step:** P.2 Interrogate
- **Why needed:** The step brief described this change as "a new shared capability under `src/backend/shared/`", but the TODO/instruction place the generator in `scripts/make_map.py`. The two placements have different gates: `src/` code is inside the coverage floor (`source = ["src/backend", "src/frontend"]`, `fail_under = 92`), mypy's scope, and the map it generates; `scripts/` is not.
- **Context:** `src/backend/shared/` today = `__init__.py` + `principal.py` (the D14 authorization plumbing, `docs/specs/user-roles-permissions.md:34`). AGENTS.md: "`shared/` is deliberately small … only when genuinely shared by multiple features and contains no feature-specific business logic."
- **Question:** Confirm placement: everything in `scripts/` (generator + CLI), nothing under `src/`? Or a `src/backend/shared/structure_map/` module with a thin `scripts/` CLI wrapper (then coverage/mypy apply and the map maps itself)?
  - **Recommendation: all in `scripts/`** — a repo-map generator is not domain plumbing and must not become product code.
- **Answer:** **PENDING**
- **Date:** 2026-10-03
- **Status:** PENDING
- **Incorporated:** no

## Q-13 — Where the "read the map first" hook lives (and whether the map is a workflow prerequisite)
- **Step:** P.2 Interrogate
- **Why needed:** The instruction asks for "a one-line note to AGENTS.md"; the brief also floats "P.1 classification cites the generated map" (AGENTS.md Agent Obligation 1). Making it a P.1 prerequisite turns the tool into a hard dependency of every change — with a chicken-and-egg problem for the first run and for every fresh worktree.
- **Context:** `value-triage-gate` (WAITING) is already rewriting the AGENTS.md Phase P table, the Workflow Diagram and Agent Obligations/Prohibitions (`docs/todo/value-triage-gate.md:51`); `docs/questions/value-triage-gate.md:122` cleared structure-map as non-conflicting **only** because it touches a different section.
- **Question:** Which hook?
  - A. Skill only (`.agents/skills/code-structure-map/SKILL.md`) + one line in AGENTS.md "Tooling & Execution Environment" — no phase references the map.
  - B. A + a sentence in the `specify` skill's P.1 ("if `STRUCTURE.md` exists, read it before walking the tree") — advisory, never blocking.
  - C. Make it a prerequisite: P.1/Phase 5 must cite/regenerate the map (hard gate, collides with `value-triage-gate`, adds a regeneration duty to every change).
  - **Recommendation: B** — advisory keeps the value without a new gate; keeps the PR mergeable with `value-triage-gate`.
- **Answer:** **PENDING**
- **Date:** 2026-10-03
- **Status:** PENDING
- **Incorporated:** no

## Q-14 — Register the new skill in AGENTS.md's Skill-to-Phase Mapping?
- **Step:** P.2 Interrogate
- **Why needed:** AGENTS.md's Skill-to-Phase Mapping lists the 8 existing skills; a 9th skill that appears in no table drifts from the protocol (and `track-python-skill` had to be opened precisely because a skill existed outside the tracked/registered set).
- **Context:** The new skill is not a workflow phase skill — it is ambient exploration guidance, like `python-best-practices`, which is also absent from the mapping table.
- **Question:** Add a row (e.g. "(ambient) code-structure-map — optional, before exploring"), leave it unlisted like `python-best-practices`, or list both?
  - **Recommendation: leave it out of the phase table; the one-line AGENTS.md pointer (Q-13) is enough** — and note the precedent that `python-best-practices` is likewise unlisted.
- **Answer:** **PENDING**
- **Date:** 2026-10-03
- **Status:** PENDING
- **Incorporated:** no

## Q-15 — Freshness across parallel worktrees and PRs
- **Step:** P.2 Interrogate
- **Why needed:** Worktrees are per-change and parallel (AGENTS.md "Git Worktrees"). Two branches that each touch a `.py` file each regenerate `STRUCTURE.md` → guaranteed merge conflict on a generated file, and a map generated in a worktree reflects that branch, not `main`.
- **Context:** The hook is check-only (Q-2), so it never rewrites; `git worktree list` currently shows one other change (`chore/remove-spec-tdd-driver`, PR #62) whose merge changes tracked-file counts.
- **Question:** What is the regeneration/conflict policy — regenerate in the same commit as the `.py` change and resolve conflicts by regenerating (never hand-merge)? Or regenerate once at S6.4 before the PR? Or accept staleness on `main` and regenerate in a follow-up chore?
  - **Recommendation: regenerate in the same commit; on conflict, take either side and regenerate** — stated in the skill so no agent hand-edits the file.
- **Answer:** **PENDING**
- **Date:** 2026-10-03
- **Status:** PENDING
- **Incorporated:** no

## Q-16 — `--max-depth` semantics and default
- **Step:** P.2 Interrogate
- **Why needed:** The instruction lists `--max-depth N` without saying whether it prunes the tree, the module list, or both — and a wrong default silently hides the whole codebase.
- **Context:** 82 of 84 tracked `src/` files are at path depth 4 (`src/backend/<feature>/<module>.py`); `src/main.py` is depth 2. A depth-3 default would list no backend module at all.
- **Question:** Does `--max-depth` limit the **tree rendering only** (modules always parsed), or module discovery too? Default value (unlimited? 4?)? Is depth counted in path segments from the root?
  - **Recommendation: tree rendering only, default unlimited for modules, default depth 3 for the tree with a `(+N dirs not shown)` marker.**
- **Answer:** **PENDING**
- **Date:** 2026-10-03
- **Status:** PENDING
- **Incorporated:** no

## Q-17 — `--include-private` semantics and dunder methods
- **Step:** P.2 Interrogate
- **Why needed:** "Skip private names (leading underscore)" would also drop `__init__`, which is usually the constructor signature an agent needs, and it is unclear whether `_foo.py` **modules** are skipped too.
- **Context:** No tracked module in the repo starts with `_` (checked: `git ls-files | rg "/_"` → none), so the module-level rule is currently unobservable — but the flag must still be specified.
- **Question:** (a) Are dunder methods (`__init__`, `__post_init__`, `__eq__`) shown by default, always hidden, or shown only with `--include-private`? (b) Does the flag also include `_`-prefixed modules? (c) Are `_`-prefixed classes hidden while their public methods stay visible?
  - **Recommendation: dunders shown by default (they are public API), `_name` symbols gated by the flag, module inclusion unaffected by the flag.**
- **Answer:** **PENDING**
- **Date:** 2026-10-03
- **Status:** PENDING
- **Incorporated:** no

## Q-18 — How are the feature `__init__.py` public interfaces shown?
- **Step:** P.2 Interrogate
- **Why needed:** This repo's public interface **is** the feature `__init__.py` re-export (11 files, 4–13 import lines each; AGENTS.md: "Features should expose explicit public interfaces"). An AST walk finds no classes or functions in those files, so a naive map renders them empty and the agent sees the wrong API surface.
- **Context:** `src/backend/authentication/__init__.py` has 13 import lines; `src/backend/shared/__init__.py` 3.
- **Question:** For `__init__.py`, emit (a) nothing, (b) an `exports:` line listing `__all__` (or the imported public names, sorted), or (c) a per-package header listing the public API once?
  - **Recommendation: (b)** — one sorted `exports:` line per package `__init__.py`; it is the cheapest accurate statement of the public interface.
- **Answer:** **PENDING**
- **Date:** 2026-10-03
- **Status:** PENDING
- **Incorporated:** no

## Q-19 — Class-level annotated fields (pydantic/SQLModel models)
- **Step:** P.2 Interrogate
- **Why needed:** 204 of the 323-module symbol set are classes, and most are Pydantic/SQLModel models whose API is their **fields**, not methods. Under "classes with base classes and their public methods" they render as a bare header — the map would hide the schema.
- **Context:** e.g. `src/backend/settings/models.py`, `src/backend/*/models.py`; the specs' "Data Structures & API Schemas" sections treat fields as the contract.
- **Question:** Show class-level annotated fields (name + annotation, no default value), or header only, or fields capped at N per class?
  - **Recommendation: show fields as one line each (`field: int`, no defaults, no `Field(...)` payloads), capped at ~15 per class with a `… +N fields` marker.**
- **Answer:** **PENDING**
- **Date:** 2026-10-03
- **Status:** PENDING
- **Incorporated:** no

## Q-20 — Decorators in the map
- **Step:** P.2 Interrogate
- **Why needed:** 65 module-level `@logged` / `@logged_class` / `@requires_permission` decorators exist, plus `@property`, `@staticmethod`, `@classmethod`, `@abstractmethod`, `@contextmanager`. Some change the contract (enforcement, abstract API, protocol), some are pure tracing noise.
- **Context:** AGENTS.md mandates `@logged_class` on traced classes and `@requires_permission` + a `principal` parameter for enforced methods (ADR-079 plumbing in `backend/shared/`) — the second is exactly what a caller must know.
- **Question:** Show decorators for all symbols, only contract-changing ones (`requires_permission`, `abstractmethod`, `property`, `staticmethod`, `classmethod`, `contextmanager`, `override`), or none?
  - **Recommendation: contract-changing only, in a compact prefix; skip logging decorators.**
- **Answer:** **PENDING**
- **Date:** 2026-10-03
- **Status:** PENDING
- **Incorporated:** no

## Q-21 — Path form in the output
- **Step:** P.2 Interrogate
- **Why needed:** The instruction's example (`src/pkg/module.py`) is a filesystem path, but this repo's import names differ (`src/backend/` is a namespace package with no `__init__.py`; `pyproject.toml:135-148` explains `backend.<feature>` resolution). Agents grep with one form and import with the other.
- **Context:** Determinism requires the POSIX form regardless (`as_posix()`), because the local run is Windows and CI is Linux.
- **Question:** Filesystem-relative POSIX paths only (`src/backend/settings/registry.py`), or path plus import path (`backend.settings.registry`) in the module header?
  - **Recommendation: filesystem-relative POSIX everywhere; add the import package once per package header** (one line per package, not per module).
- **Answer:** **PENDING**
- **Date:** 2026-10-03
- **Status:** PENDING
- **Incorporated:** no

## Q-22 — File-set source: git index, working tree, or both
- **Step:** P.2 Interrogate
- **Why needed:** `git ls-files` lists the **index**, so a newly created, not-yet-`git add`ed module is invisible and `--check` still passes — a silently stale map during exactly the phase (IMPLEMENT) where new files appear.
- **Context:** The instruction says "respecting `.gitignore` (use `git ls-files` if inside a git repo, otherwise fall back to a built-in ignore list: `.git`, `.venv`, `node_modules`, `__pycache__`, `dist`, `build`)".
- **Question:** Use `git ls-files` (index only), or `git ls-files --cached --others --exclude-standard` (index + untracked-not-ignored)? In the non-git fallback, does the ignore list also exclude `.venv`-equivalents by name only, and does `.gitignore` get parsed?
  - **Recommendation: `--cached --others --exclude-standard`** (matches what an agent sees on disk); non-git fallback = built-in ignore list, `.gitignore` not parsed (documented limitation).
- **Answer:** **PENDING**
- **Date:** 2026-10-03
- **Status:** PENDING
- **Incorporated:** no

## Q-23 — `--check` contract and exit codes
- **Step:** P.2 Interrogate
- **Why needed:** The hook's behavior and the acceptance tests both depend on the exact contract: byte-exact compare? missing output file? message content? exit code for usage errors (argparse uses 2)? Does a parse-error file change the exit code?
- **Context:** Q-2 fixed the hook as check-only (`pass_filenames: false` implied); the acceptance signal in the TODO says "the second run's `--check` exits 0, touching any `.py` makes it exit 1".
- **Question:** Confirm: exit 0 = fresh, 1 = stale **or missing**, 2 = usage error; comparison is byte-exact on the whole file; on 1 it prints one line (`STRUCTURE.md is out of date — run uv run python scripts/make_map.py`) and no diff; parse errors do **not** change the exit code.
  - **Recommendation: as stated above.**
- **Answer:** **PENDING**
- **Date:** 2026-10-03
- **Status:** PENDING
- **Incorporated:** no

## Q-24 — Determinism contract: symbol ordering and byte-level rules
- **Step:** P.2 Interrogate
- **Why needed:** "Sort everything alphabetically" is the instruction, but alphabetical method order destroys the class's natural reading order (constructor first), and the repo's pre-commit hooks (`trailing-whitespace`, `end-of-file-fixer`) will rewrite the generated file if it has trailing spaces or no final newline — which then makes `--check` fail forever.
- **Context:** `git ls-files` order is not guaranteed locale-stable, so sorting must be explicit on the relative POSIX path string.
- **Question:** (a) Files sorted by POSIX path — agreed; are **symbols** sorted alphabetically (instruction-faithful) or kept in source order (more useful, still deterministic)? (b) Confirm the byte contract: no timestamps, no absolute paths, no host/user info, LF newlines, exactly one trailing newline, no trailing whitespace, encoding UTF-8.
  - **Recommendation: files sorted by path; symbols in source order; byte contract exactly as (b) — and one acceptance test that runs the generator twice and compares bytes, plus one that asserts the output is `trailing-whitespace`/`end-of-file-fixer` clean.**
- **Answer:** **PENDING**
- **Date:** 2026-10-03
- **Status:** PENDING
- **Incorporated:** no

## Q-25 — Docstring summary normalization and escaping
- **Step:** P.2 Interrogate
- **Why needed:** "First line only" is ambiguous for docstrings that open on the next line, contain Markdown, backticks, pipes, or very long text — unnormalized summaries break the compact format and can make the output non-deterministic across formatters.
- **Context:** All 83 `src/` modules have a module docstring; 42 `tests/` modules have none (empty summary → skip the line, don't emit a blank).
- **Question:** Normalize to: first logical line, whitespace collapsed, truncated at N chars (what N — 80? 100?) with an explicit marker, backticks/pipes escaped or stripped? Missing docstring → no summary line at all?
  - **Recommendation: collapse whitespace, truncate at 100 chars with `…`, strip backticks, omit the line when absent.**
- **Answer:** **PENDING**
- **Date:** 2026-10-03
- **Status:** PENDING
- **Incorporated:** no

## Q-26 — Parse errors and unreadable files
- **Step:** P.2 Interrogate
- **Why needed:** "Files that fail to parse must not crash the script. List them with `(parse error)`" — but the error text itself can be Python-version- or locale-dependent (non-deterministic output), and undecodable (non-UTF-8) or vanished-between-listing-and-read files are separate cases.
- **Context:** No `.py` file currently fails to parse (all 317 parsed cleanly in the measurement run).
- **Question:** Emit a bare `(parse error)` marker plus a sorted "Files that could not be parsed" section (no message), or include the message? Are `UnicodeDecodeError`/`OSError` treated as parse errors? Does a parse error affect the exit code or `--check`?
  - **Recommendation: bare marker + sorted section, no message (determinism); decode/OS errors are the same case; exit code unaffected.**
- **Answer:** **PENDING**
- **Date:** 2026-10-03
- **Status:** PENDING
- **Incorporated:** no

## Q-27 — Signature rendering and grammar version
- **Step:** P.2 Interrogate
- **Why needed:** "Signatures with type annotations, no bodies" can be produced by re-slicing source text (breaks on multi-line signatures, keeps formatting drift) or by `ast.unparse` (canonical, deterministic, but rewrites the source text). It also decides which grammar the script can parse — the venv is Python 3.14 (`[tool.mypy] python_version = "3.14"`), and `docs/todo/python-3.15.md` is in the backlog.
- **Context:** `python-best-practices/references/python-3.15.md` exists; a 3.15-syntax file parsed by a 3.14 `ast` would land in the parse-error list.
- **Question:** Use `ast.unparse` for annotations/defaults (canonical) or verbatim source slices? Include default values in the signature or omit them? What is stated as the supported grammar (the running interpreter's)?
  - **Recommendation: `ast.unparse`, defaults included when short (≤ 20 chars), grammar = the running interpreter's, documented as an EDGE.**
- **Answer:** **PENDING**
- **Date:** 2026-10-03
- **Status:** PENDING
- **Incorporated:** no

## Q-28 — Quality gates for the new code (mypy, ruff, complexipy)
- **Step:** P.2 Interrogate
- **Why needed:** The instruction says "keep the code typed", but the gate is `uv run mypy src/` — `scripts/` is never type-checked (and `[tool.ty.environment] root = ["./src"]`). Meanwhile `ruff check .` **does** cover `scripts/` (`.github/workflows/lint.yml:37`), and `complexipy` analyzes `src` + `tests` (`pyproject.toml:92-94`), so the new test file is gated but the script is not.
- **Context:** AGENTS.md Tooling: "mypy runs on `src/`"; the existing `scripts/*.py` are typed informally.
- **Question:** (a) Extend the gate (`uv run mypy scripts/` in AGENTS.md/CI) or keep typing self-imposed and just run `uv run mypy scripts/` once in Phase 5 evidence? (b) Is the ≤ 250-line limit a hard NFR or a target?
  - **Recommendation: (a) self-imposed — run `mypy scripts/make_map.py` in Phase 5 evidence, do not change the gate; (b) target, not a gate (the truncation policy may need more lines).**
- **Answer:** **PENDING**
- **Date:** 2026-10-03
- **Status:** PENDING
- **Incorporated:** no

## Q-29 — Performance budget (NFR)
- **Step:** P.2 Interrogate
- **Why needed:** The hook runs on every commit that touches a `.py` file, and the skill tells agents to regenerate when stale — so run time is a real cost, but the instruction states no budget.
- **Context:** 323 `.py` files, 32 343 lines to read and parse; the script must read each file once (line count + AST) to stay cheap.
- **Question:** What is the NFR — e.g. "a full run over this repository completes in under 2 s (single read per file, no re-reads)", and is it asserted by a test or stated as an untested NFR?
  - **Recommendation: NFR < 2 s, asserted only as a coarse upper-bound test (skip on slow CI), not a strict gate.**
- **Answer:** **PENDING**
- **Date:** 2026-10-03
- **Status:** PENDING
- **Incorporated:** no

## Q-30 — `--root` / `--out` path resolution
- **Step:** P.2 Interrogate
- **Why needed:** The CLI takes both `--root` and `--out`; without a rule, running from a subdirectory (a worktree subdir, or `uv run` from repo root) writes the map to different places, and "no hardcoded absolute paths" must not leak the root into the output.
- **Context:** Worktrees live next to the repo (`../python-template_kopie-worktrees/...`), so relative resolution matters; the hook runs from the repo root.
- **Question:** Is `--out` resolved relative to the CWD or to `--root`? Does the script require `--root` to be a git repo (or fall back)? Is the root path ever written into the output (it must not be)?
  - **Recommendation: `--out` relative to CWD (standard CLI behavior), `--root` defaults to the script's repo root via `pathlib`, root path never appears in the output; non-git root uses the fallback ignore list.**
- **Answer:** **PENDING**
- **Date:** 2026-10-03
- **Status:** PENDING
- **Incorporated:** no

## Q-1 — Skill location
- **Step:** P.1 Frame (conflict flagged while framing; answered out of the P.2 batch)
- **Why needed:** The instruction names `skills/code-structure-map/SKILL.md`, but this repo's skills live in `.agents/skills/<name>/SKILL.md` and are loaded from there; a root `skills/` directory would be dead text.
- **Context:** `.agents/skills/` holds 8 skills (decompose, git, implement, python-best-practices, review, specify, test, verify).
- **Question:** Where should the skill live?
- **Answer:** `.agents/skills/code-structure-map/SKILL.md` — the path the harness actually loads.
- **Date:** 2026-10-03
- **Status:** ANSWERED
- **Incorporated:** yes — `docs/todo/structure-map.md`, "In scope" (skill bullet) and "Affected features"

## Q-2 — How the `--check` gate is enforced
- **Step:** P.1 Frame
- **Why needed:** The instruction offers "a pre-commit hook **or** Makefile target"; the repo has no Makefile, and a check-only hook fails every commit that touches a `.py` file until the map is regenerated.
- **Context:** `.pre-commit-config.yaml` already runs project tooling as local hooks via `uv run` (deptry, mkdocs-build).
- **Question:** pre-commit check-only, pre-commit that regenerates, or also a CI job?
- **Answer:** **pre-commit check-only** — a local hook running `make_map.py --check`. No Makefile, no CI job.
- **Date:** 2026-10-03
- **Status:** ANSWERED
- **Incorporated:** yes — `docs/todo/structure-map.md`, "In scope" (automation bullet) and "Out of scope" (CI job excluded)

## Q-3 — Output path of the generated map
- **Step:** P.1 Frame
- **Why needed:** The repo splits `docs/` (internal process record) from `userdocs/` (published site, `mkdocs.yml` `docs_dir`); a generated root-level artifact is a third category.
- **Context:** Binding decision Q-64 keeps published docs in `userdocs/`, never `docs/`.
- **Question:** Root `STRUCTURE.md`, `docs/STRUCTURE.md`, or `userdocs/STRUCTURE.md`?
- **Answer:** **`STRUCTURE.md` at the repo root** — as the instruction states.
- **Date:** 2026-10-03
- **Status:** ANSWERED
- **Incorporated:** yes — `docs/todo/structure-map.md`, "In scope" (STRUCTURE.md bullet) and "Out of scope" (not published via mkdocs)

## Late questions (Phases 2–6)

<questions discovered after the change entered the workflow; same entry format, Step field set to the step that found it>
