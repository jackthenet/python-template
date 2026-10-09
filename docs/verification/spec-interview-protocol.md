# Verification: spec-interview-protocol

**Type:** DOCS/CHORE (no-behavior)

**Phase P / P.4 (Draft — DOCS/CHORE path, specify skill items 40–41):** the exact non-behavior scope, plus the no-behavior-delta confirmation. No spec, no spec-approval PR, and **P.5 (Verify self-consistency) does not run for this type** (`AGENTS.md` Phase P atomic-steps table: "P.5 Verify self-consistency — subagent (specify skill) — **FEATURE/CROSS-CUTTING only**"; the READY gate for DOCS/CHORE is the verified **P.4 artifact**). Created at P.4 in the change worktree.

- **Change branch / worktree:** `chore/spec-interview-protocol` at `../python-template_kopie-worktrees/chore/spec-interview-protocol`
- **Base commit (`main` at P.4):** `3ad83a016e9100da6caf31d7acf5b48fe73203b8` (`3ad83a0`)
- **Date:** 2026-10-09
- **TODO file:** `docs/todo/spec-interview-protocol.md` (orchestrator-owned, on `main`; `Status: QUESTIONS-ANSWERED`, Value triage decision = **implement**, score 4/5)
- **Question file:** `docs/questions/spec-interview-protocol.md` — **all 6 questions ANSWERED** (Q-1…Q-6, 2 rounds, 2026-10-04), all marked incorporated
- **Related specs:** none. `docs/specs/template.md` is edited (Edit 4) — it is the **template**, not an approved spec, and both CI checkers exclude it by name (see Edit 4).

---

## Classification (Phase 0, recorded at P.1, re-confirmed at P.4)

**DOCS/CHORE** — the change "does not alter behavior: documentation, comments, configuration, CI, tooling" (`AGENTS.md`, Change Types table, criterion 5). It adds four small rules/fields to the **P.2 Interrogate / P.3 Answer** guidance and to two templates.

- Not **ISSUE** — no approved spec is contradicted; the deltas are *absent* from the guidance, not violations of it (question file E-1…E-4, grep-proven).
- Not **FEATURE** / **CROSS-CUTTING** — no externally observable capability, no `src/backend/` feature touched; editing several guidance documents is not a cross-feature change.
- Not **REFACTOR** — no code is restructured.
- **No reclassification trigger in P.4:** nothing found while re-reading the current text changes the type.

## Line-number correction applied at P.4 (mandatory)

The question file's `file:line` citations were written on 2026-10-04, **before** `workflow-docs-nits` (PR #64, merged `5d59374`) and `value-triage-gate` (PR #70, merged `d77e833`) landed. Both edited `AGENTS.md` and `.agents/skills/specify/SKILL.md`, so the cited numbers are stale. **Every target below was re-located by content in the current tree at `3ad83a0`**, and the current line number is given. The mapping:

| Question-file citation | Current location (at `3ad83a0`) |
|---|---|
| `AGENTS.md:142` (P.2 row) | `AGENTS.md:143` — the `**P.2 Interrogate**` row of the "Phase P atomic steps" table |
| `AGENTS.md:143` (P.3 row) | `AGENTS.md:144` — the `**P.3 Answer**` row |
| `AGENTS.md:701` (Obligation 17) | `AGENTS.md:712` — Agent Obligation **17** |
| (question-file entry list) | `AGENTS.md:390` — `#### Question files (docs/questions/<name>.md)`, first paragraph |
| `specify/SKILL.md:71` (P.2 objective prose) | `specify/SKILL.md:72` — `### P.2 Interrogate` → `- **Objective:**` |
| `specify/SKILL.md:74` (P.2 done-criteria) | `specify/SKILL.md:75` — `### P.2 Interrogate` → `- **Done-criteria:**` |
| `specify/SKILL.md:173-174` (Rules) | `specify/SKILL.md:174-175` — "Ask MORE questions…" / "Ask at least 20 questions…" |
| `specify/SKILL.md:216` (Definition of Done) | `specify/SKILL.md:218` — "At least 20 questions were asked…" (under `**Phase P — the READY gate (all types):**`) |
| `docs/questions/template.md:21` / `:28-30` | unchanged: `:21` `- **Question:**` line of the Entry format; `:28-30` the `## Preparation questions (P.2)` block |
| `docs/specs/template.md:3-6` (§1) | unchanged: `:3` `## 1. Overview & Objectives`, `:6` the `- **Goal:**` bullet |
| `check_traceability.py:105` | `scripts/check_traceability.py:100-103` — check (1) "every REQ/AC defined by a spec has at least one matrix row" (violation message at `:102`); the template exclusion is at `:42` |

**AGENTS.md is normative, the skill is operational.** Every done-criterion change is therefore made in **both** files in this one change, or the step and the handoff verification disagree (the P-39 failure class, `docs/workflow/PROBLEMS.md`).

---

## Scope (exact, verified against the current tree at `3ad83a0`)

**Four files, seven edits.** Every "before" below was re-read verbatim from the file in this worktree at P.4; **none of the deltas is already present** (verified by `grep -in recommend` over `AGENTS.md` and `.agents/skills/*/SKILL.md` → no match, and by reading each target line). Each edit names the question answer that authorises it.

### Edit 1 — `docs/questions/template.md` (Q-1 = (A) MUST; Q-2 = (A) MUST)

**1a — Entry format, insert one field between `Question:` (`:21`) and `Answer:` (`:22`)**

- **Before (verbatim, `:21-22`):**
  ```markdown
  - **Question:** <the question for the user>
  - **Answer:** <the user's answer>  (or **PENDING**)
  ```
- **After (verbatim):**
  ```markdown
  - **Question:** <the question for the user>
  - **Recommended:** <the step's proposed answer + one-line reason>
  - **Answer:** <the user's answer>  (or **PENDING**)
  ```
- **Authorised by:** Q-1 = **(A)** — the field is a **MUST**, added to the Entry format and required by P.2's done-criteria (Edit 2a/3a).

**1b — `## Preparation questions (P.2)` block (`:28-30`): one line stating every question carries a recommended answer, plus the `### Category coverage` block**

- **Before (verbatim, `:28-30`):**
  ```markdown
  ## Preparation questions (P.2)

  <the interrogation batch — at least 20 questions for FEATURE/CROSS-CUTTING>
  ```
- **After (verbatim):**
  ```markdown
  ## Preparation questions (P.2)

  <the interrogation batch — at least 20 questions for FEATURE/CROSS-CUTTING; **every** entry carries a `Recommended:` answer>

  ### Category coverage

  <one row per interrogation category this change uses: `covered (Q-nn / E-nn)` or `skipped — <reason>`. Required for every change type; it sits **on top of** the ≥ 20-question floor, never instead of it.>
  ```
- **Authorised by:** Q-1 = (A) (the "every entry carries a `Recommended:`" line) and Q-2 = (A) (the `### Category coverage` table lives **in the question file**, matching the five precedent files `structlog-logging.md`, `api-keys.md`, `structure-map.md`, `update-readme.md`, `session-lookup-unwired.md`).
- **Not touched in this file:** `:9` (`Status:` comment) and `:12` (the batching paragraph) — `:9` is owned by the already-merged `workflow-docs-nits`; the batching rule is explicitly out of scope.

### Edit 2 — `.agents/skills/specify/SKILL.md` (Q-1, Q-2, Q-3, Q-4)

**2a — `### P.2 Interrogate` → `- **Done-criteria:**` (`:75`)** — the gate location for all three new P.2 obligations.

- **Before (verbatim, `:75`):**
  ```text
  - **Done-criteria:** at least 20 questions asked and recorded in `docs/questions/<name>.md` in **one** `BLOCKED-USER` batch (the orchestrator presents the batch in as few `ask_user_question` rounds as possible, ≤ 4 per round, most blocking first); the feature brief captures goals, constraints, out-of-scope, edge cases; overlap checked against `docs/specs/` **and** every TODO in `docs/todo/` (no double work).
  ```
- **After (verbatim):** the same sentence with three clauses inserted **after** the batching parenthetical and **before** "the feature brief captures" — the "at least 20 questions" wording is **kept unchanged**:
  ```text
  - **Done-criteria:** at least 20 questions asked and recorded in `docs/questions/<name>.md` in **one** `BLOCKED-USER` batch (the orchestrator presents the batch in as few `ask_user_question` rounds as possible, ≤ 4 per round, most blocking first); **every** entry carries a `- **Recommended:**` answer with a one-line reason; the question file carries a `### Category coverage` table marking each interrogation category `covered (Q-nn / E-nn)` or `skipped — <reason>` (use this change's own dimensions — Scope & Goals, Data & State, Behavior & Edge Cases, Interfaces, Constraints, Testing & Acceptance, Architecture & Conventions are a **starting checklist, not a closed set**); a non-goals / scope-boundary question is asked and recorded; the feature brief captures goals, constraints, out-of-scope, edge cases; overlap checked against `docs/specs/` **and** every TODO in `docs/todo/` (no double work).
  ```
- **Authorised by:** Q-1 = (A) (recommended answer per entry is a MUST in P.2's done-criteria), Q-2 = (A) (coverage table, own dimensions, seven categories as a starting checklist not a closed set), Q-4 = (1) (the **mandatory** non-goals / scope-boundary question), Q-3 = (A) (the ≥ 20 floor is **kept** — the new clauses are layered on top).
- **Why the clause goes in Done-criteria and not the Objective line (`:72`):** Q-4's answer cites "one clause in `specify/SKILL.md:71`", which at P.2-writing time was the P.2 block; a **MUST** belongs in the step's done-criteria (the gate the orchestrator verifies), not in the Objective prose, or it is a rule with no gate. The Objective line at `:72` already says "…edge cases, and **scope boundaries**", so no prose change is needed there — recorded as a deliberate P.4 decision, not an omission.

**2b — `## Rules`: one new bullet after the two interrogation rules (`:174-175`)**

- **Before (verbatim, `:174-175` — both lines are **kept unchanged**):**
  ```text
  - Ask MORE questions than feels necessary during interrogation (FEATURE/CROSS-CUTTING).
  - Ask at least 20 questions during interrogation (FEATURE/CROSS-CUTTING). **Record each in the change's question file `docs/questions/<name>.md`** and return the **complete batch in a single** `BLOCKED-USER` handoff (the orchestrator presents the batch in as few `ask_user_question` rounds as possible — ≤ 4 per round, most blocking first — records the answers in that file, and relaunches this step **once** with the full answer set). Do not return partial batches across multiple round-trips.
  ```
- **After:** the two lines unchanged, plus **one new bullet inserted immediately after `:175`**:
  ```text
  - Every P.2 question entry MUST carry a `- **Recommended:**` answer (the step's proposed answer + one-line reason), the question file MUST carry a `### Category coverage` table (each category `covered (Q-nn / E-nn)` or `skipped — <reason>`), and a non-goals / scope-boundary question MUST be asked. These sit **on top of** the ≥ 20-question floor — they never replace it (the coverage table applies to every change type; the floor stays FEATURE/CROSS-CUTTING).
  ```
- **Authorised by:** Q-1, Q-2, Q-3 = (A), Q-4 = (1).

**2c — `## Definition of Done` → `**Phase P — the READY gate (all types):**`: one new top-level bullet after `:215` ("The change type is classified and recorded…")**

- **Before (verbatim, `:215` and `:218` — both **kept unchanged**):**
  ```text
  - The change type is classified and recorded in the TODO file and in `docs/verification/<name>.md`.
  …
    - At least 20 questions were asked during interrogation and **recorded in `docs/questions/<name>.md`** (one `BLOCKED-USER` batch; the orchestrator presents it in as few rounds as possible, ≤ 4 per round, and records the answers).
  ```
- **After:** `:215` and `:218` unchanged, plus **one new top-level bullet after `:215`** (top level = applies to all types, which is what Q-2 implies and what the five precedents show):
  ```text
  - Every P.2 question entry carries a `Recommended:` answer, the question file carries a `### Category coverage` table (each category `covered (Q-nn / E-nn)` or `skipped — <reason>`), and a non-goals / scope-boundary question was asked and recorded — **in addition to** the ≥ 20-question floor for FEATURE/CROSS-CUTTING, never instead of it.
  ```
- **Authorised by:** Q-1, Q-2, Q-3 = (A), Q-4 = (1). Placing it at top level (all types) rather than inside the FEATURE/CROSS-CUTTING sub-list keeps the ≥ 20 bullet untouched and matches the ISSUE/DOCS-CHORE precedents.
- **Not touched in this file:** `:14`, `:45`, `:46` (owned by the merged `workflow-docs-nits` — this change adds **no** step, so the step-order lists stay), `:189` ("The DOCS/CHORE scope MUST confirm no behavior delta"), the P.5 checklist, and the FEATURE/CROSS-CUTTING path prose.

### Edit 3 — `AGENTS.md` (normative mirror of Edit 2 — Q-1, Q-2, Q-3, Q-4)

**3a — the `**P.2 Interrogate**` row of the "Phase P atomic steps" table (`:143`)** — only the **Done when** cell changes; the Step / Owner / Objective cells stay.

- **Before (verbatim, `:143`, the Done-when cell):**
  ```text
  ≥ 20 questions (FEATURE/CROSS-CUTTING) recorded in **one** `BLOCKED-USER` batch; overlap checked against `docs/specs/` **and** every TODO in `docs/todo/`
  ```
- **After (verbatim):**
  ```text
  ≥ 20 questions (FEATURE/CROSS-CUTTING) recorded in **one** `BLOCKED-USER` batch, **every** entry carrying a `Recommended:` answer with a one-line reason, and a `### Category coverage` table marking each interrogation category `covered (Q-nn / E-nn)` or `skipped — <reason>` (on top of the floor, never instead of it); a non-goals / scope-boundary question asked and recorded; overlap checked against `docs/specs/` **and** every TODO in `docs/todo/`
  ```
- **Authorised by:** Q-1 = (A), Q-2 = (A), Q-3 = (A) (the "≥ 20 questions (FEATURE/CROSS-CUTTING)" wording is kept verbatim), Q-4 = (1).

**3b — the `**P.3 Answer**` row (`:144`): NO EDIT.** Recorded explicitly: Q-5 = **(C)** dropped the per-round "what is decided now" recap, and the row's existing wording ("present the batch (≤ 4 per `ask_user_question` round, most blocking first) and record the answers") needs no change for the `Recommended:` field — the field is an entry property gated at P.2, not a P.3 action. Adding anything here would re-introduce the dropped item.

**3c — `#### Question files (docs/questions/<name>.md)`, first paragraph (`:390`)** — the normative description of an entry must list the new field, or the template (Edit 1a) and the normative text disagree.

- **Before (verbatim, the second sentence of `:390`):**
  ```text
  Each entry has: the question, the generating step (step ID `P.x` / `Sx.x` + phase), why it is needed, the context at the time, the user's answer, the date/status, and whether the answer has been incorporated.
  ```
- **After (verbatim):**
  ```text
  Each entry has: the question, the generating step (step ID `P.x` / `Sx.x` + phase), why it is needed, the context at the time, the step's recommended answer with a one-line reason, the user's answer, the date/status, and whether the answer has been incorporated.
  ```
- **Authorised by:** Q-1 = (A).
- **Deliberately not added here:** the `### Category coverage` table. Its gate is the P.2 row (3a) and the skill's P.2 done-criteria (2a); the Question-files subsection describes an **entry**, and the coverage table is not an entry. Recorded so Phase 6 review reads it as a decision, not a miss.

**3d — Agent Obligation 17 (`:712`)**

- **Before (verbatim, `:712`):**
  ```text
  17. Prepare every change before running its workflow (Phase P): TODO file, ≥ 20 interrogation questions for FEATURE/CROSS-CUTTING, all answers recorded, draft spec / triage / baseline / scope, self-consistency check (FEATURE/CROSS-CUTTING); the **value triage** (overlap, beneficiary, 1–5 score, recommendation) with the user's implement / merge / drop decision recorded before P.4.
  ```
- **After (verbatim):**
  ```text
  17. Prepare every change before running its workflow (Phase P): TODO file, ≥ 20 interrogation questions for FEATURE/CROSS-CUTTING — plus, for every type, a `Recommended:` answer on every question entry, a `### Category coverage` table in the question file, and a non-goals / scope-boundary question (all three **on top of** the floor, never instead of it) — all answers recorded, draft spec / triage / baseline / scope, self-consistency check (FEATURE/CROSS-CUTTING); the **value triage** (overlap, beneficiary, 1–5 score, recommendation) with the user's implement / merge / drop decision recorded before P.4.
  ```
- **Authorised by:** Q-1, Q-2, Q-3 = (A), Q-4 = (1). Obligation 17 is the fifth and last site naming the ≥ 20 floor; all five sites (2a, 2b, 2c, 3a, 3d) are changed in this one commit so none can disagree (P-39).
- **Not touched in `AGENTS.md`:** the P.4/P.5 rows, the Phase Matrix, the Workflow Diagram, the Skill-to-Phase Mapping, the Batching bullet in the Question-files subsection (`≤ 4 per round` — out of scope), the Agent Prohibitions list (no new prohibition is needed: question file E-15 shows "one interview procedure, not two" is satisfied by construction when the change is edits-only), the Phase 5/6 text, and the Versioning section.

### Edit 4 — `docs/specs/template.md` §1 (Q-4 = (2))

- **Before (verbatim, `:3-6`):**
  ```markdown
  ## 1. Overview & Objectives
  - **Feature Name:** [e.g., Redis Rate Limiter]
  - **Target Component:** [e.g., `src/middleware/rate_limit.py`]
  - **Goal:** [1-2 sentences on what this feature achieves and why it is needed]
  ```
- **After (verbatim):** one bullet appended after the `- **Goal:**` line (still inside §1, before the blank line that precedes `## 2.`):
  ```markdown
  - **Out of Scope / Non-goals:** [what this feature explicitly does NOT do — keep this bullet ID-free: a `REQ-XXX`/`AC-XXX` ID here would make `scripts/check_traceability.py` demand a traceability matrix row for it]
  ```
- **Authorised by:** Q-4 = **(2)** — a §1 **bullet, not a numbered section**, and it **must stay ID-free**.
- **Why a bullet and not a numbered section:** `scripts/check_traceability.py` never parses headings — it extracts IDs by regex and, in check (1) at `scripts/check_traceability.py:100-103`, fails when a `REQ`/`AC` ID defined in `docs/specs/` has **no row** in `docs/verification/traceability.md`. A numbered "Out of Scope" section invites an ID (the `docs/specs/settings-coverage.md:148` `REQ-021` pattern); an ID-free bullet in §1 cannot trip that check. The template itself is already excluded from ID extraction (`check_traceability.py:42`, `spec_files()` skips `template.md`) and from the CI spec job (`.github/workflows/spec-validation.yml:45` skips `basename == "template.md"`), so the edit is provably inert for CI — but the ID-free rule is what keeps it inert **for the specs written from the template**.
- **Matches existing practice:** 8 of the 12 approved specs already carry an explicit out-of-scope line (`authentication.md`, `event-bus.md`, `file-management.md`, `mail-service.md`, `settings.md`, `user-management.md`, `user-roles-permissions.md`, and `search.md`'s full `## 13. Out of Scope`), so the template catches up with practice rather than inventing a field.

---

## Explicitly NOT in scope

| Item | Why |
|---|---|
| The per-round "what is decided now" recap line | **Q-5 = (C) dropped.** No artifact, no producer, no evidence path — a MUST would be a gate signal with no reachable producer (the P-39 class, `docs/workflow/PROBLEMS.md`); the question file plus the recorded `Recommended:` field already carry it durably |
| Backfilling non-goals into `docs/specs/logging.md`, `docs/specs/logging-coverage.md`, `docs/specs/session-management.md` | **Q-4 = (3) no backfill.** They are approved specs; each would need its own Spec Amendment PR (Spec Amendment Workflow: "Direct edits to `docs/specs/` on `main` are rejected"). The template binds **new** specs only |
| Any `src/`, `tests/`, `scripts/`, `migrations/`, `pyproject.toml`, `.github/`, `userdocs/` change | no behavior may change; the DOCS/CHORE scope is Markdown guidance and templates only |
| Any version bump | `AGENTS.md` → Versioning → bump mapping: `REFACTOR / DOCS-CHORE → none`; `bump-my-version` is not run |
| Any change to `docs/todo/` or `docs/questions/` (including this change's own two records) | orchestrator-owned, `main`-only; a change branch must never contain them. `docs/todo/template.md` and `docs/questions/template.md` are **different** paths — only the **question** template is in scope (Edit 1), the TODO template is not |
| The ≤ 4-per-round batching rule, the single `BLOCKED-USER` batch rule, the Spec Approval Gate | already correct and already enforced; the TODO lists them as out of scope |
| A new interview-protocol document or a new workflow step | the whole point of the change is one procedure, not two (question file E-15); no step is added, so no step-list/ownership/diagram text changes |
| Replacing `docs/specs/template.md`'s structure with the interview's five headings | would drop REQ/AC/INV/EDGE/NFR IDs, the test-strategy map and the traceability matrix, and break `scripts/check_traceability.py` |
| The value-triage placement | owned by `docs/todo/value-triage-gate.md` (merged); **Q-6** confirms this change does not re-open it |
| `specify/SKILL.md:14`, `:45`, `:46` and `docs/questions/template.md:9` | owned by the already-merged `workflow-docs-nits` |

---

## No-behavior-delta confirmation (specify skill item 40: "confirm they do not alter externally observable behavior")

**Why each edit is behavior-free.** All four files are Markdown process guidance and templates: `AGENTS.md` (normative workflow contract), `.agents/skills/specify/SKILL.md` (operational procedure), `docs/questions/template.md` and `docs/specs/template.md` (fill-in templates). No `src/`, `tests/`, `scripts/`, `migrations/`, `pyproject.toml`, `.github/workflows/`, `mkdocs.yml` or `userdocs/` path is touched, so no runtime code, no test, no dependency, no CI definition, no build/coverage/type configuration and no published-site page changes. The published site's `docs_dir` is `userdocs` (`mkdocs.yml:6`) and `grep -rn "AGENTS.md|\.agents/skills|docs/specs/template" userdocs` → **no match**, so the site content cannot change.

**Correction to the P.2 evidence (E-11) — re-verified at `3ad83a0`.** E-11 claimed "no test can fail" because nothing machine-reads the edited content. That was true on 2026-10-04 and is **no longer fully true**: since `feature/structure-map` (PR #75, merged `7dfaa23`), `tests/acceptance/test_structure_map.py` **reads `AGENTS.md` and `.agents/skills/specify/SKILL.md`** (`:938-939`, `_SPECIFY_SKILL` / `_AGENTS_MD`). The externally observable program behavior still cannot change (no runtime code is involved), so the DOCS/CHORE classification holds — but a test **can** now fail on these edits, so the scope carries four hard constraints, each verified against the current test source:

| # | Constraint the edits must respect | Test | Status of the planned edits |
|---|---|---|---|
| C-1 | No `AGENTS.md` line that mentions `STRUCTURE.md` / `make_map` / `code-structure-map` outside the sections `Tooling & Execution Environment`, `Skill-to-Phase Mapping`, `Project Structure`, and none that pairs such a mention with gate/todo/prohibition vocabulary (`_MAP_MENTION` × `_MACHINERY`) | `test_ac_026_map_hook_is_advisory` → `_agents_md_map_machinery_lines()` (`:1372-1381`) | **satisfied** — none of the three `AGENTS.md` edits (3a, 3c, 3d) mentions the map |
| C-2 | No phase skill other than the map skill may mention the map; the specify skill is explicitly skipped, and its `### P.1 Frame (orchestrator)` section must keep **exactly one** advisory map sentence, free of machinery vocabulary | same test → `_assert_phase_skills_not_wired()` + the P.1 assertions (`:1383-1405`) | **satisfied** — Edit 2 touches `:75`, `:175+`, `:215+`; it does not touch `### P.1 Frame (orchestrator)` and adds no map mention |
| C-3 | Neither `AGENTS.md` nor any file under `.agents/skills/` may cite `tests/architecture` | `test_ac_024_agents_md_layout_matches_the_map` (`:1337`, assertion at `:1368`) | **satisfied** — no edited text contains that path |
| C-4 | The `AGENTS.md` sections `## Tooling & Execution Environment`, `### Skill-to-Phase Mapping` (rows for `code-structure-map` and `python-best-practices`, each marked `(ambient)`) and `## Project Structure` must keep their content | same test (`:1341-1361`) | **satisfied** — the three edits are in the Phase-P table, the Question-files subsection and the Obligations list; none of those sections is touched |

**Base guard result (recorded now, so Phase 5 does not misattribute it).** In this worktree at `3ad83a0`, before any edit: `uv run pytest tests/acceptance/test_structure_map.py -q` → **`1 failed, 30 passed`**. The failure is `test_ac_021_committed_map_matches_fresh_render`, and it is **pre-existing on `main`**: `uv run python scripts/make_map.py --check` exits **1** in both the primary worktree and this one at `3ad83a0`, i.e. the committed `STRUCTURE.md` is already stale at the base commit. This change adds **no `.py` file** and renames/moves none, so it owes **no** map regeneration (`AGENTS.md`: regenerate when a `.py` is added/renamed/moved/deleted), and `STRUCTURE.md` is **not** in scope — fixing the pre-existing staleness is a separate chore, not this change's.

**Gate-strength confirmation (no gate weakened).** Q-3 = (A): the ≥ 20-question floor keeps its exact wording at all five sites (`specify/SKILL.md:75`, `:175`, `:218`; `AGENTS.md:143`, `:712`) and the new obligations are **additive** — every one is a MUST that narrows P.2, never loosens it. Nothing is deleted from any gate, done-criteria, rule, obligation, or template line in this change: all seven edits are insertions (or, for 3a/3c/3d, one line rewritten to a strict superset of its previous content). The batching rule (≤ 4 per round, one `BLOCKED-USER` batch), the Spec Approval Gate, the overlap check, the P.5 checklist, the READY gate and the Phase 5/6 gates are untouched. Net effect: P.2's done-criteria go from 3 clauses to 6 — **strictly stronger**.

---

## Phase 5 checks this change will run (DOCS/CHORE light tier)

`AGENTS.md` Phase Matrix, DOCS/CHORE Phase 5 = "Light: lint/types where applicable"; Phase 5 item 16 = "Run lint and type checks where applicable; confirm no test files or behavior were touched".

| Check | Command | Why it runs / expected result |
|---|---|---|
| Lint (whole-repo sweep, the Phase 5 gate, matches CI `lint` job) | `uv run ruff check .` | required by the Phase 5 gate; ruff scans Python only, so the result must be **identical to base** (`All checks passed!`) — no Python is added |
| Types | `uv run mypy src/` | required by the Phase 5 gate; no `src/` file is in the diff, so the result cannot differ from base |
| Spec referential integrity | `uv run python scripts/check_traceability.py` | **required — `docs/specs/template.md` is touched** (Edit 4). Must exit 0: the template is excluded from ID extraction (`check_traceability.py:42`) and the new §1 bullet is ID-free, so check (1) at `:100-103` cannot trip |
| Scope proof | `git diff --name-status main...HEAD` | must list **only** `AGENTS.md`, `.agents/skills/specify/SKILL.md`, `docs/questions/template.md`, `docs/specs/template.md`, `docs/verification/spec-interview-protocol.md` — no `src/`, `tests/`, `scripts/`, `migrations/`, `pyproject.toml`, `.github/`, `userdocs/`, `docs/todo/`, `docs/questions/<name>.md` path |
| Guidance-reading acceptance guard (added at P.4, see C-1…C-4) | `uv run pytest tests/acceptance/test_structure_map.py -q` | these tests read `AGENTS.md` and `specify/SKILL.md`, so they are the only executable check that can observe this change. Expected: **`1 failed, 30 passed`** — the same as the base guard result above; any **new** failure means a C-1…C-4 constraint was violated |
| Docs site | `uv run --group docs mkdocs build --strict` | **skipped — and recorded as skipped**: the change touches no `userdocs/` path (`docs_dir: userdocs`, `mkdocs.yml:6`), and none of the four edited files is part of the published site (grep evidence above), so the CI `docs` job outcome cannot change. It becomes required only if a later step adds a `userdocs/` edit — it must not |
| Full test suite | `uv run pytest tests/` | not a DOCS/CHORE gate; the targeted guard above plus the scope proof are the evidence. (If the reviewer wants it, it is the CI job's job.) |

**CI note.** `spec-validation.yml` triggers on `docs/specs/**` **and** `docs/verification/**` — both are in this diff, so the Spec Validation workflow **will** run and must pass (it skips `template.md` by name at `:45`). `lint.yml`'s paths filter (`:5-11`) excludes `docs/`, `AGENTS.md` and `.agents/`, so the Lint workflow will not trigger on this branch — the local `uv run ruff check .` is the authoritative lint evidence. `quality.yml` has no paths filter and runs regardless. The live local gates on the edited Markdown are the pre-commit `trailing-whitespace` / `end-of-file-fixer` hooks, so the diff must be clean at commit time.

**Version bump: none** (`AGENTS.md` → Versioning → `REFACTOR / DOCS-CHORE → none`).

---

## Merge-order note

This change must merge **before `security-changelog-license`** (`docs/todo/security-changelog-license.md:13`: "land after `workflow-docs-nits` → `value-triage-gate` → `architecture-tests-missing` → `spec-interview-protocol`"; its Q-7 = (b) adds a changelog rule to `AGENTS.md` **and** `.agents/skills/`, so the two collide on the same files). Its two predecessors — `workflow-docs-nits` (PR #64, merged `5d59374`) and `value-triage-gate` (PR #70, merged `d77e833`) — are **already merged on `main`**, so **Q-6's ordering constraint is satisfied for this P.4**: the branch was cut from `3ad83a0`, which carries both, and every target line above was read from that settled text. `architecture-tests-missing` is no longer a live backlog item (it is not in `docs/todo/`), so the ordering chain reduces to: **this change → `security-changelog-license`**.

---

## P.4 done-criteria checklist

| Criterion (specify skill, DOCS/CHORE items 40–41) | Result |
|---|---|
| Change branch + worktree created from `main` as the first action | `chore/spec-interview-protocol` @ `../python-template_kopie-worktrees/chore/spec-interview-protocol`, base `3ad83a0` |
| Scope recorded in `docs/verification/spec-interview-protocol.md` | this file, built incrementally (1 `write` + 4 `edit` calls, not one giant write) |
| Exact non-behavior changes defined (file + line + before/after verbatim) | **4 files, 7 edits**, each citing the authorising question answer |
| Targets located by **content**, not by the stale P.2 line numbers | yes — mapping table above; all targets re-read at `3ad83a0` |
| No-behavior delta confirmed | yes — section above, incl. the corrected E-11 claim and constraints C-1…C-4 |
| No gate weakened; ≥ 20 floor kept verbatim at all five sites | yes — gate-strength confirmation above |
| P.5 does not run for this type | recorded in the header (READY gate = verified P.4 artifact) |
| No implementation code, no tests, no scoped doc edit made in Phase P | confirmed — the only file this step writes is this record; `git status` in the worktree shows exactly this file |
| Planning records untouched by this branch | confirmed — `docs/todo/` and `docs/questions/` are not written here |
| Commit | `chore(spec-interview-protocol): scope` |

---

## Phase 4 — implementation (DOCS/CHORE path, implement skill item 12: "make the scoped non-behavior changes")

All **seven** edits of the scope above were applied verbatim, in the change worktree, and nothing else. No RED/GREEN gate applies to this type; the Phase 4 evidence is the **scope proof**, the **floor-wording check**, and the **C-1…C-4** confirmation.

### Scope proof — `git diff --name-status main...HEAD` (before the Phase 4 commit)

```text
M	.agents/skills/specify/SKILL.md
M	AGENTS.md
M	docs/questions/template.md
M	docs/specs/template.md
```

(plus this record itself). Exactly the four files the scope names — **no** `src/`, `tests/`, `scripts/`, `migrations/`, `pyproject.toml`, `.github/`, `userdocs/`, `STRUCTURE.md`, `docs/todo/`, `docs/questions/<name>.md` path, no version bump. Diffstat for the four guidance files: `4 files changed, 13 insertions(+), 5 deletions(-)`; the 5 deletions are the 5 lines rewritten to a **strict superset** of their previous content (skill `:75`, `AGENTS.md:143`, `:390`, `:712`, and the `docs/questions/template.md` placeholder line) — nothing was removed from any gate, rule, obligation or template line. Hunk locations (`git diff -U0 | grep '^@@'`): skill `@@ -75 +75 @@`, `@@ -175,0 +176 @@`, `@@ -215,0 +217 @@`; `AGENTS.md` `@@ -143 +143 @@`, `@@ -390 +390 @@`, `@@ -712 +712 @@` — i.e. exactly the seven planned targets, no drift from the P.4 line map.

### Floor-wording check (done criterion 2 — the ≥ 20 floor survives at all five sites)

`grep -n` on the five sites at HEAD:

```text
.agents/skills/specify/SKILL.md:75   - **Done-criteria:** at least 20 questions asked and recorded in …   ← site 1 (clauses appended after the batching parenthetical)
.agents/skills/specify/SKILL.md:175  - Ask at least 20 questions during interrogation (FEATURE/CROSS-CUTTING). …  ← site 2 (byte-identical to main)
.agents/skills/specify/SKILL.md:220    - At least 20 questions were asked during interrogation and …      ← site 3 (byte-identical to main; moved 218 → 220 by the insert above it)
AGENTS.md:143                        | ≥ 20 questions (FEATURE/CROSS-CUTTING) recorded in **one** `BLOCKED-USER` batch, …  ← site 4
AGENTS.md:712                        17. … ≥ 20 interrogation questions for FEATURE/CROSS-CUTTING — plus, …  ← site 5
```

`grep -ci "20 questions\|20 interrogation"` — **HEAD 3 / main 3** in `specify/SKILL.md`, **HEAD 2 / main 2** in `AGENTS.md`: the same number of floor-bearing lines, none deleted. A line-by-line `diff` of the floor lines (`main` vs HEAD) shows only the two `AGENTS.md` lines and the two skill lines that the scope plans to rewrite, each rewritten to a superset that still contains the original floor wording verbatim; the Rules bullet (`:175`) and the Definition-of-Done bullet (`:220`) are **unchanged**. Net gate strength: P.2's done-criteria go from 3 clauses to 6 — strictly stronger, never weaker.

### AGENTS.md ↔ skill agreement (done criterion 3)

Both files now carry the same three MUSTs in the same words — (1) a `Recommended:` answer on **every** question entry with a one-line reason, (2) a `### Category coverage` table with each category `covered (Q-nn / E-nn)` or `skipped — <reason>`, (3) a non-goals / scope-boundary question asked and recorded — and both state the additive relation to the floor in the same terms: `AGENTS.md:143` "(on top of the floor, never instead of it)", `AGENTS.md:712` "(all three **on top of** the floor, never instead of it)", `specify/SKILL.md:176` "These sit **on top of** the ≥ 20-question floor — they never replace it", `specify/SKILL.md:217` "**in addition to** the ≥ 20-question floor for FEATURE/CROSS-CUTTING, never instead of it". `grep -c 'Recommended:'` → **2** in `AGENTS.md` (the P.2 row, Obligation 17), **3** in `specify/SKILL.md` (P.2 done-criteria, the new Rules bullet, the new Definition-of-Done bullet), **2** in `docs/questions/template.md` (the entry format + the P.2 placeholder line); `grep -c 'Category coverage'` → **2 / 3 / 1**; `grep -c 'non-goals'` → **2 / 3 / 0** (the two `AGENTS.md` sites and the three skill sites carry all three rules; the templates carry the field, not the rule). No site loosens a gate.

### Constraints C-1…C-4 (the `tests/acceptance/test_structure_map.py` guards)

| # | Check run | Result |
|---|---|---|
| C-1 | `git diff -U0 -- AGENTS.md .agents/skills/specify/SKILL.md \| grep '^+' \| grep -i "STRUCTURE.md\|make_map\|code-structure-map"` | **no match (grep exit 1)** — no added line mentions the map, so no map×machinery line exists |
| C-2 | `git diff -U0 -- .agents/skills/specify/SKILL.md \| grep -c Advisory` | **0** — `### P.1 Frame (orchestrator)`'s advisory sentence is untouched; the skill hunks are at `:75`, `:176`, `:217` only, and no map mention was added |
| C-3 | `grep -rn "tests/architecture" AGENTS.md .agents/skills/` | **no match (grep exit 1)** — the forbidden string is absent |
| C-4 | `diff <(git show main:AGENTS.md \| grep -n '^## Tooling…\|^### Skill-to-Phase Mapping\|^## Project Structure') <(grep -n … AGENTS.md)` | **identical, same line numbers** (`:52`, `:314`, `:1123`) — and the `AGENTS.md` hunks (`143`, `390`, `712`) fall outside all three sections |

### Gates run in Phase 4

| Gate | Command | Result |
|---|---|---|
| Lint | `uv run ruff check .` | **`All checks passed!`** — identical to base (no Python touched) |
| Spec referential integrity (required: `docs/specs/template.md` touched) | `uv run python scripts/check_traceability.py` | **`Traceability: PASS (881 matrix rows, 136 spec IDs, 801 test functions)`**, exit 0 — the new §1 bullet is ID-free, so check (1) cannot trip |
| Guidance-reading guard | `uv run pytest tests/acceptance/test_structure_map.py -q` | **`1 failed, 30 passed`** — exactly the base guard result. The single failure is `test_ac_021_committed_map_matches_fresh_render` (committed `STRUCTURE.md` says `docs/ — 220 files`, a fresh render says `223`), **pre-existing on `main`**: `uv run python scripts/make_map.py --check` exits **1** here, as recorded at the base commit `3ad83a0`. No other test failed, so C-1…C-4 hold. No test was touched |
| Markdown hygiene (the live local gate) | `git diff --check` → exit **0**; `git diff \| awk '/^\+/ && /[ \t]$/ {n++}'` → **0** added lines with trailing space/tab; `tail -c 1` on all four files → `\n` | clean: no trailing whitespace, no whitespace errors, every file ends with a newline (pre-commit `trailing-whitespace` / `end-of-file-fixer`) |
| Map regeneration | `uv run python scripts/make_map.py` (generate mode) | **not run** — this change adds/renames/moves **no** `.py` file, so no regeneration is owed, and `STRUCTURE.md` is out of scope (only `--check` was run, which does not write) |
| Types / docs site / full suite | `mypy src/`, `mkdocs build --strict`, `pytest tests/` | Phase 5 items — see the "Phase 5 checks" table above (docs site stays **skipped**: no `userdocs/` path entered the diff) |

### Deliberate decisions recorded in Phase 4 (not omissions)

- **Edit 2c placement.** The new Definition-of-Done bullet is inserted at **top level after the "change type is classified and recorded" bullet** (`:216`), exactly as the scope's Edit 2c specifies ("one new top-level bullet after `:215`"), **not** inside the `FEATURE/CROSS-CUTTING:` sub-list. A top-level bullet is required because the three MUSTs apply to every change type (Q-2), and inserting it inside the sub-list would sit under the FEATURE/CROSS-CUTTING heading and contradict it; the existing ≥ 20 sub-bullet is byte-identical to `main`.
- **`docs/questions/template.md:9` (`Status:` comment) and the batching paragraph** were not touched (owned by the merged `workflow-docs-nits`; batching is out of scope).
- **No `### Category coverage` text was added to `AGENTS.md:390`** (the Question-files subsection) — per Edit 3c, its gate is the P.2 row (3a) and the skill's P.2 done-criteria (2a); the subsection describes an **entry**, and the coverage table is not an entry.
- **`AGENTS.md:144` (the P.3 Answer row) has no edit** — Q-5 = (C) dropped the recap line (Edit 3b).

### Phase 4 commit

`chore(spec-interview-protocol): interview-protocol guidance edits` — the four scoped Markdown files plus this record. No code, no test, no version bump, no PR (Phase 6 opens it).
