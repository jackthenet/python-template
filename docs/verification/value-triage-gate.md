# Verification: value-triage-gate

**Type:** DOCS/CHORE (no-behavior)

**Phase P / P.4 (Draft — DOCS/CHORE path):** the exact non-behavior scope of the change, with the no-behavior-delta confirmation. No spec, no spec-approval PR (DOCS/CHORE). Created at P.4 in the change worktree.

- **Change branch / worktree:** `chore/value-triage-gate` at `../python-template_kopie-worktrees/chore/value-triage-gate`
- **Base commit (`main` at P.4):** `535816c5f4d0f417248d575ea9dbad963cee3bbd` (`535816c`)
- **TODO file:** `docs/todo/value-triage-gate.md` (orchestrator-owned, on `main`) — `Status: QUESTIONS-ANSWERED`, value triage **5/5, implement as one bundle**
- **Question file:** `docs/questions/value-triage-gate.md` — **all 6 questions ANSWERED** (Q-1, Q-2, Q-3, Q-4, Q-5, Q-7; 2026-10-04), none PENDING
- **Depends on:** `prepared-workflow` (merged `4b42c58`) and **`workflow-docs-nits` (merged: PR #64 as `5d59374`, status advance `be42d2d`)** — both satisfied at base `535816c`, so the P.4 gate (Q-2) is met and this change builds on the merged qualifiers (re-measured below, not restated)
- **Related specs:** none (no `docs/specs/` file is touched)

---

## Classification (Phase 0, recorded at P.1, re-confirmed at P.4)

**DOCS/CHORE** — criterion 5 in the Change Types table (`AGENTS.md:197`): "The change **does not alter behavior**: documentation, comments, configuration, CI, tooling." The change adds process guidance to `AGENTS.md`, two skill files and the TODO template.

Why no earlier criterion matches (first-match order, `AGENTS.md:191-197`):

- **Not ISSUE** — no approved spec states the behavior being "fixed". `grep -rln "P.1 Frame|alue triage|Phase P\b" docs/specs/` returns exactly one file, `docs/specs/structlog-logging.md`, and its only hit is a changelog line ("Draft (Phase P, P.4)") — no spec defines or requires Phase P step wording, the planning templates, or a value-triage step. There is no defect against a spec, so **no REQ/AC is affected** and no Spec Amendment is needed.
- **Not FEATURE / CROSS-CUTTING** — no externally observable product capability is added and no `src/backend/` or `src/frontend/` feature is touched. The new human ⏸ (the triage ask) is a protocol step, not a product behavior; the same classification was applied to `spec-interview-protocol`, which likewise only edits Phase P/P.2/P.3 guidance (`docs/todo/spec-interview-protocol.md:8`).
- **Not REFACTOR** — no code is restructured.

### Affected requirements (process guidance — no REQ-XXX IDs exist)

Process guidance in `AGENTS.md` and the skills has **no `REQ-XXX` / `AC-XXX` IDs**: the ID scheme is defined for feature specifications (`docs/specs/`, `docs/specs/template.md`) and `scripts/check_traceability.py` reads only `docs/specs/*.md`, `docs/verification/traceability.md` and `tests/`. **No IDs are invented for this change.** The normative basis it amends is the passage set below, cited by file + section + line (measured at `535816c`):

| Passage amended | Location | What it currently establishes |
|---|---|---|
| Phase P — Preparation artifacts | `AGENTS.md:126-135` | the two planning records and where they are committed |
| Phase P — atomic steps, **P.1 Frame** row | `AGENTS.md:141` | P.1's objective and done-criterion |
| Phase P — Planning records (owner: the orchestrator) | `AGENTS.md:149-164` | who writes the two records, and the `Status:` advance table |
| Phase P — Preparing many changes | `AGENTS.md:177-179` | backlog preparation is parallel and cheap |
| Phase Matrix note | `AGENTS.md:215` | the per-type Phase P outputs and the PR rule |
| Multi-change scheduling (never idle) | `AGENTS.md:407-414` | Ready-selection order, the cleared-gate test |
| Agent Prohibitions | `AGENTS.md:658-680` | what an agent MUST NOT do |
| Agent Obligations | `AGENTS.md:684-704` | obligation 17 (prepare every change) |
| TODO template | `docs/todo/template.md:7`, `:31-34` | the `Status:` vocabulary; the section order of a TODO |
| `specify` skill — P.1 Frame, Rules, Outputs, Definition of Done | `.agents/skills/specify/SKILL.md:62-67`, `:167-171`, `:192-205`, `:209-224` | the Phase P step contract |
| `git` skill — planning-commit, S7.1, Post-merge cleanup, Rules | `.agents/skills/git/SKILL.md:22`, `:55-59`, `:63-75`, `:114-135`, `:152-160` | planning-record ownership, the status chain, post-merge cleanup |

### Escalation triggers (reclassification, per AGENTS.md Escalation Rules)

Stop and reclassify if Phase 4 or review finds any of these:

| Trigger | New type |
|---|---|
| Any `src/`, `tests/`, `docs/specs/` or `.github/workflows/` file is touched | re-check — a behavior delta means **FEATURE** (new capability) or **ISSUE** (defect against a stated rule) |
| The wording changes what an **existing gate** requires (READY gate `AGENTS.md:147`, the Spec Approval Gate, RED/GREEN, Phase 5/6 gates) — the TODO puts those out of scope | **CROSS-CUTTING** review of the protocol, at minimum a spec-free re-scope |
| The stop becomes **global** (the agent must halt everything until the user answers) instead of per-item at P.4 — that would force edits to `AGENTS.md:305`, `:410`, `:676` | a scheduling-protocol change → re-scope and re-triage (Q-2 = (a) explicitly forbids it) |
| A script, CI job or machine-readable score validation is added | **DOCS/CHORE still holds** only if it changes no product behavior; a new validator is a tooling change that must be re-scoped, not silently added |

**Wording hazard for Phase 6 review** (TODO "Constraints and risks"): the new text must read as **one batched backlog gate plus a per-item stop at P.4**, never as a blocking gate on every change. The `never idle` bullet (`AGENTS.md:410`), the WAITING rules (`:124`, `:305`, `:388`) and the corresponding Prohibition (`:676`) stay byte-identical — review MUST confirm they are not in the diff.

---

## Scope (exact, verified against the tree at `535816c`)

**22 edits in 4 files, all Markdown.** Every "before" below was re-read from the file in this worktree at P.4 with `grep -n` (line numbers are from the base commit `535816c`, **not** copied from the question file). The `workflow-docs-nits` qualifiers are **already live** and are re-measured, not restated:

| `workflow-docs-nits` edit (merged) | Live text at `535816c` (re-measured) |
|---|---|
| `docs/todo/template.md:44` Prep-log row | the Prep-log row now reads "P.5 Self-consistency (FEATURE/CROSS-CUTTING)" — qualifier present |
| `.agents/skills/specify/SKILL.md:14` | "…now **P.2 / P.4 / P.5** (FEATURE/CROSS-CUTTING) — same content…" — qualifier present |
| `.agents/skills/specify/SKILL.md:45` | "…**P.5 Verify self-consistency** (FEATURE/CROSS-CUTTING only) → **S1.4 Present for approval** (FEATURE/CROSS-CUTTING only)…" — qualifier present |
| `.agents/skills/specify/SKILL.md:46` | "…P.2, P.4, P.5 and S1.4 (the latter two FEATURE/CROSS-CUTTING only) each run in their own subagent…" — qualifier present |

This change **builds on** those four lines and does not touch them (Q-1 = (b) + Q-4 = (a)); the collision the question file predicted is dissolved.

### Edit index

| ID | File | Location (at `535816c`) | Decided by |
|---|---|---|---|
| A1 | `AGENTS.md` | `:130-131` (Preparation artifacts table, two rows) | Q-7 |
| A2 | `AGENTS.md` | `:141` (P.1 Frame row) | Q-1, Q-5 |
| A3 | `AGENTS.md` | `:151` (Planning records paragraph, append) | Q-7 |
| A4 | `AGENTS.md` | `:162` + new row after it (status-advance table) | Q-3, Q-7 |
| A5 | `AGENTS.md` | after `:179` (new `### Backlog value triage` subsection) | Q-1, Q-2, Q-5 |
| A6 | `AGENTS.md` | `:215` (Phase Matrix note, append one sentence) | Q-1, Q-2 |
| A7 | `AGENTS.md` | `:411` (Ready selection order, append) | Q-7 |
| A8 | `AGENTS.md` | `:412` (Resume / cleared-gate bullet, append) | Q-7 |
| A9 | `AGENTS.md` | after `:661` (new Prohibition bullet) | Q-2 |
| A10 | `AGENTS.md` | `:703` (Obligation 17, append clause) | Q-1 |
| T1 | `docs/todo/template.md` | `:7` (`Status:` comment vocabulary) | Q-3 |
| T2 | `docs/todo/template.md` | new `## Value triage` section between `:32` and `:34` | Q-1, Q-5 |
| S1 | `.agents/skills/specify/SKILL.md` | `:64-67` (P.1 Frame step section) | Q-1, Q-5 |
| S2 | `.agents/skills/specify/SKILL.md` | `:169` (Rules — status chain) | Q-3 |
| S3 | `.agents/skills/specify/SKILL.md` | `:171` (Rules — planning-record paths) | Q-7 |
| S4 | `.agents/skills/specify/SKILL.md` | `:196-198` (Outputs — Phase P list) | Q-1, Q-2 |
| S5 | `.agents/skills/specify/SKILL.md` | `:211` (Definition of Done, first bullet) | Q-1 |
| G1 | `.agents/skills/git/SKILL.md` | `:22` (Execution Context — planning-commit bullet) | Q-3, Q-7 |
| G2 | `.agents/skills/git/SKILL.md` | `:65` + the code block at `:67-71` (planning-commit operation) | Q-3, Q-7 |
| G3 | `.agents/skills/git/SKILL.md` | `:59` (S7.1 done-criteria) | Q-7 |
| G4 | `.agents/skills/git/SKILL.md` | `:114-135` (Post-merge cleanup — new step 5) | Q-7 |
| G5 | `.agents/skills/git/SKILL.md` | `:155` (Rules — direct-to-`main` rule) | Q-3, Q-7 |

### A1 — `AGENTS.md:130-131`, Preparation artifacts table

- **Before (verbatim):**
  ```markdown
  | `docs/todo/<name>.md` (from `docs/todo/template.md`) | P.1 | `main` |
  | `docs/questions/<name>.md` (from `docs/questions/template.md`) | P.1, answered at P.3 | `main` |
  ```
- **After:** the `Committed to` cell of each row gains the archive destination — `` `main` (→ `docs/todo/archive/<name>.md` once `DROPPED`/`MERGED`) `` and `` `main` (→ `docs/questions/archive/<name>.md` once `DROPPED`/`MERGED`) ``. No new row (the triage lives **inside** the TODO file — question-file closed point 2).
- **Q-7 verbatim:** "`docs/todo/archive/<name>.md` + `docs/questions/archive/<name>.md` … the live guidance that names those two paths must be updated in the same change: the Phase P preparation-artifacts table, …".

### A2 — `AGENTS.md:141`, the P.1 Frame row (the mandatory clause, Q-1 = (b))

- **Before (verbatim):**
  ```markdown
  | **P.1 Frame** | orchestrator | classify the change type (Phase 0); create the TODO file and the question file from their templates; create the change's todo set | both files exist on `main`; the orchestrator sets TODO `Status: PREPARING` |
  ```
- **After:** the Objective gains "; **value-triage the TODO** (existing overlap, beneficiary, 1–5 score, recommendation — see "Backlog value triage")"; the *Done when* gains "; the TODO's `## Value triage` section is filled in (the user's decision is recorded **before P.4**)".
- **Not** a new numbered `P.0` row, **no** change to the Workflow Diagram (`AGENTS.md:221-236`), the Ownership sentence (`:329` area, `:335`, `:365`), the Atomic Steps chain (`:339`) or the todo-set rules (`:420`, `:422`) — Q-1 = (b) verbatim: "No new numbered step, no Phase P table/diagram/todo-set edits".

### A3 — `AGENTS.md:151`, Planning records (append one sentence)

- **Before (tail of the paragraph, verbatim):** "…because the branch does not modify those paths, a later direct-to-`main` status update is never reverted by the merge."
- **After:** append — "The orchestrator also **moves** the two files **together** — `docs/todo/<name>.md` → `docs/todo/archive/<name>.md` and `docs/questions/<name>.md` → `docs/questions/archive/<name>.md` — at the **drop** decision and at **post-merge cleanup (S7.1)**; the question file always moves with its TODO file, and the move is itself a direct-to-`main` planning-record commit. `docs/questions/archive-AI_Questions.md` (the retired central file) is unrelated to the new folder and stays where it is."

### A4 — `AGENTS.md:155-162`, the status-advance table (Q-3 = (a))

- **Before (verbatim, the last row):**
  ```markdown
  | after post-merge cleanup | `MERGED` |
  ```
- **After:** that row becomes `| after post-merge cleanup (the two records then move to `docs/todo/archive/` and `docs/questions/archive/`) | `MERGED` |`, and one row is added after it:
  ```markdown
  | when the user's value-triage decision is **drop** (the two records then move to `docs/todo/archive/` and `docs/questions/archive/`) | `DROPPED` |
  ```
- **Evidence that no machine reader breaks:** `grep -rn "PREPARING|QUESTIONS-ANSWERED|DROPPED" scripts/ .github/workflows/` → **no match**. The vocabulary is prose guidance read by the agent only.

### A5 — new `### Backlog value triage` subsection after `AGENTS.md:179`

The one short paragraph Q-1 = (b) requires, placed at the end of the Phase P section (after "Preparing many changes"). Planned text (final wording may be tightened in Phase 4 without changing any of the clauses):

```markdown
### Backlog value triage

Before implementing any TODO, decide whether it is worth doing. At **P.1 Frame** the orchestrator fills in the TODO's `## Value triage` section: **(1)** check the codebase for existing functionality that covers it and name the file/function — if it overlaps, propose extending that feature instead of building a new one; **(2)** identify who benefits and how (the end user of this project), and say so instead of guessing when the value is unclear or the TODO is too vague to judge; **(3)** score it **1–5** (`5` = clear user value, new, small change · `3` = some value, or partly overlapping, or moderate effort · `1` = no clear value, duplicate, or large/risky change) with one sentence explaining the score; **(4)** recommend **implement / merge into <existing feature> / drop**. Present the results as a table (`ID | TODO | score | recommendation | reason`) and ask the user which to implement, merge, or drop: over a backlog sweep that is **one triage batch**, presented in as few rounds as possible (≤ 4 per round, most blocking first); a single TODO framed outside a sweep gets its ask **immediately**, as a one-row table riding that change's existing P.3 round-trip — no extra ⏸. The ask and the decision are recorded **only in the TODO's `## Value triage` section**, never as a question-file entry. **No TODO may pass P.4 (create its branch and worktree) until its own value-triage decision is recorded**; already-decided and READY changes keep running, so "never idle" is unaffected. Prefer reusing existing code and the smallest diff that delivers the value — dropping a low-value or duplicate TODO is a good outcome. The code-level counterpart is the "Ponytail, lazy senior dev mode" ladder (rungs 1–2), which this rule cross-references instead of restating. A dropped TODO gets `Status: DROPPED` and its two records move to the archive folders (see "Planning records (owner: the orchestrator)").
```

- The 1–5 anchors are quoted **verbatim** from the rule text in `docs/todo/value-triage-gate.md:31-56` (question-file closed point 4 — the anti-subjectivity device).
- "one triage **batch**, … ≤ 4 per round" is the wording instruction from closed point 6, so "one ask" is never read as a single round.
- No auto-drop threshold is introduced (closed point 5): the user always decides.
- The paragraph **references** `AGENTS.md:19-51` (Ponytail) and does not edit it (TODO Out of scope).

### A6 — `AGENTS.md:215`, Phase Matrix note (append one sentence, not five cell edits)

- **Before (verbatim):**
  ```text
  "Full gate set" = the Phase 5 FEATURE checks below. Every type ends with a PR to `main` for human review/merge (human governance).
  ```
- **After:** append — "Every Phase P output in the row above presupposes a recorded **Value triage** decision for that TODO (see "Backlog value triage"); a TODO whose decision is not recorded may not reach P.4." The five `**P Prepare**` cells (`:207`) stay byte-identical (closed point 10).

### A7 — `AGENTS.md:411`, Ready selection order (append)

- **Before (verbatim):**
  ```text
  - **Ready selection order.** (1) a change whose `Depends on:` changes are already merged; (2) among ready changes, **easiest first** (see Todo Tracking Discipline); (3) tie-break **FIFO by READY date**.
  ```
- **After:** append — " A `DROPPED` or `MERGED` change's records live under `docs/todo/archive/` and `docs/questions/archive/`, so the two live folders are the backlog to select from."

### A8 — `AGENTS.md:412`, the cleared-gate bullet (append)

- **Before (verbatim):**
  ```text
  - **Resume.** A WAITING change's gate is cleared when its spec PR / PR merge is reachable from `origin/main` after `git fetch` (`git merge-base --is-ancestor <merge-commit> origin/main`), or when its question file shows every answer. Then launch a **fresh** subagent at its next atomic step.
  ```
- **After:** append — " A change whose records have moved to `docs/todo/archive/` / `docs/questions/archive/` is finished (`MERGED`) or dead (`DROPPED`) — it is not resumed; read its question file there if its record must be checked."

### A9 — new Prohibition after `AGENTS.md:661`

- **Anchor (verbatim, `:661`):** `- Start implementation work before classifying the change type (Phase 0, at P.1).`
- **New bullet after it:** `- Start **P.4** (create the change branch and worktree) for a TODO whose `## Value triage` section is empty or whose implement / merge / drop decision is not recorded (see "Backlog value triage").`
- This enforces Q-2 = (a) as a **boundary rule**, not a gate change (closed point 9). `:676` ("Idle or wait in place on a human gate …") and `:410` ("**Never idle.**") are **not** in the diff.

### A10 — `AGENTS.md:703`, Obligation 17 (append a clause)

- **Before (verbatim):** `17. Prepare every change before running its workflow (Phase P): TODO file, ≥ 20 interrogation questions for FEATURE/CROSS-CUTTING, all answers recorded, draft spec / triage / baseline / scope, self-consistency check (FEATURE/CROSS-CUTTING).`
- **After:** append before the final period — "; the **value triage** (overlap, beneficiary, 1–5 score, recommendation) with the user's implement / merge / drop decision recorded before P.4". The `≥ 20` floor itself is untouched (owned by `spec-interview-protocol`, closed point 12).

### T1 — `docs/todo/template.md:7`, the `Status:` comment vocabulary (Q-3 = (a))

- **Before (verbatim):**
  ```markdown
  - **Status:** PREPARING  <!-- PREPARING | QUESTIONS-ANSWERED | READY | IN-WORKFLOW | WAITING | MERGED -->
  ```
- **After:** the comment becomes `<!-- PREPARING | QUESTIONS-ANSWERED | READY | IN-WORKFLOW | WAITING | MERGED | DROPPED -->`. The `Status:` value itself stays `PREPARING` (a fresh TODO is live).
- **Not touched:** the 16 existing backlog TODO files (they are historical planning records; the orchestrator updates a file only when it moves or advances it — see "Follow-up actions").

### T2 — `docs/todo/template.md`, new `## Value triage` section between `:32` and `:34`

- **Anchor (verbatim, `:31-34`):**
  ```markdown
  ## Constraints and risks
  - <bullet>

  ## Acceptance signal (plain language)
  ```
- **Insert between them** (the block settled in the question file's "For P.4" section, matching the five hand-written sections already in `docs/todo/docs-path-ci-trigger.md:35`, `split-archived-qa.md:35`, `workflow-docs-nits.md:40`, `track-python-skill.md:39`, `remove-spec-tdd-driver.md:39`):
  ```markdown
  ## Value triage (<YYYY-MM-DD>, pre-workflow)
  - **Overlap:** <what in this repository already covers it — name the file/function; "none">. If it overlaps: <the existing feature to extend instead of a new one>
  - **Beneficiary:** <who benefits and how (the end user of this project); "unclear" / "too vague to judge" instead of guessing>
  - **Score: <1-5>/5** — <one sentence explaining the score>  <!-- 5 = clear user value, new, small change · 3 = some value, or partly overlapping, or moderate effort · 1 = no clear value, duplicate, or large/risky change -->
  - **Recommendation:** implement / merge into <existing feature> / drop
  - **Decision:** <the user's answer + date>  <!-- recorded when the user answers; a dropped TODO moves to docs/todo/archive/ with its question file -->
  ```
- The `**Decision:**` bullet is the superset of the two shapes the five live records actually use (3 use `Recommendation:` only, 2 record the user's decision) — Q-5 = "recorded **only** in the TODO's `## Value triage` section".
- **No Prep-log row is added** (the template's Prep log stays as merged: `:40-44`); 3 of the 5 live records log the triage inside the existing `P.1 Frame` row.
- **Line-shift note:** this insertion is **above** the `workflow-docs-nits` edit at `:44`, so that row shifts to `:51` after this change — content unchanged, and this change does not re-touch it.

### S1 — `.agents/skills/specify/SKILL.md:64-67`, the P.1 Frame step section

- **Before (verbatim):**
  ```markdown
  - **Objective:** Classify the change type (Phase 0) and open the change's planning record.
  - **Inputs:** the change idea; `docs/todo/template.md`; `docs/questions/template.md`; the existing TODO files in `docs/todo/`.
  - **Outputs:** `docs/todo/<name>.md` and `docs/questions/<name>.md` created from their templates **on `main`** and committed directly to `main` (git skill, "Commit planning artifacts and status advances (orchestrator, `main`)"); the change's todo set.
  - **Done-criteria:** both files exist on `main` with the orchestrator having set TODO `Status: PREPARING` and question file `Status: OPEN`; the change type is recorded in the TODO file. No worktree yet — it is created at P.4.
  ```
- **After:** Objective gains "; value-triage the change (overlap, beneficiary, 1–5 score, recommendation)"; Inputs gains "the codebase (to check for existing functionality that covers the idea)"; Outputs gains "the TODO's `## Value triage` section filled in"; Done-criteria gains "the `## Value triage` section is filled in, and the user's implement / merge / drop decision is recorded in it **before P.4** creates the branch and worktree".
- **Not touched:** `:45` and `:46` (the step-order and ownership lists — already qualified by `workflow-docs-nits`, and Q-1 = (b) puts them out of scope), `:69-75` (P.2 — owned by `spec-interview-protocol`), and the manually numbered Process lists (`:117`-`:142`) — no item is inserted, so nothing renumbers.

### S2 — `.agents/skills/specify/SKILL.md:169`, Rules — the status chain

- **Before (tail, verbatim):** "…→ **IN-WORKFLOW** / **WAITING** / **MERGED**."
- **After:** "…→ **IN-WORKFLOW** / **WAITING** / **MERGED** / **DROPPED** (the user's value-triage decision is **drop**; the orchestrator then moves both records to the archive folders)."

### S3 — `.agents/skills/specify/SKILL.md:171`, Rules — the planning-record paths

- **Before (verbatim, `:171`):**
  ```markdown
  - `docs/todo/` and `docs/questions/` are the **only** files committed directly to `main`, and only by the **orchestrator** from the primary worktree; everything normative reaches `main` through a merged PR from the change worktree. A change branch never edits those two files and its PR never contains them.
  ```
- **After:** append — " The orchestrator also moves a dead or finished change's two records **together** into `docs/todo/archive/` and `docs/questions/archive/` (at the drop decision and at post-merge cleanup); the move is a planning-record commit, still `main`-only and still orchestrator-only."

### S4 — `.agents/skills/specify/SKILL.md:196-198`, Outputs — the Phase P list

- **Before (verbatim, `:198`):**
  ```markdown
  - A change branch `<type>/<name>` and its worktree at `<repo-name>-worktrees/<type>/<name>`, created at **P.4** from `main` (so the branch carries the TODO file and the answered questions).
  ```
- **After:** that bullet gains "— only after that change's own value-triage decision is recorded"; and one bullet is added after `:196`: `- the TODO's `## Value triage` section — overlap, beneficiary, 1–5 score, recommendation, and the user's implement / merge / drop decision.`

### S5 — `.agents/skills/specify/SKILL.md:211`, Definition of Done, first bullet

- **Before (tail, verbatim):** "…and the question file exists with **every** question `ANSWERED` and incorporated."
- **After:** append — " The TODO's `## Value triage` section records the overlap check, the beneficiary, the 1–5 score with its one-sentence reason, the recommendation, and the user's decision."

### G1 — `.agents/skills/git/SKILL.md:22`, Execution Context bullet

- **Before (verbatim):**
  ```markdown
  - **Commit planning artifacts and status advances (orchestrator, `main`)** — orchestrator only, always in the **primary worktree**, committed directly to `main`; covers the creation at P.1–P.3 **and every TODO `Status:` advance through `MERGED`**.
  ```
- **After:** "…through `MERGED`** **and `DROPPED`, and the archive move of both records**." (one sentence, no new bullet)

### G2 — `.agents/skills/git/SKILL.md:65` + the code block at `:67-71`, the planning-commit operation (Q-3 + Q-7)

- **Before (tail of `:65`, verbatim):** "…and the orchestrator then commits **every `Status:` advance** — `PREPARING` → `QUESTIONS-ANSWERED` → `READY` → `IN-WORKFLOW` → `WAITING` → `MERGED` — plus any late (`Phases 2–6`) question a step returned in its handoff (AGENTS.md, "Planning records (owner: the orchestrator)"):"
- **After:** the chain gains `→ DROPPED`; after the existing code block add one sentence and one command pair:
  ```bash
  # at the drop decision, and at post-merge cleanup (S7.1) — both records move together
  git mv docs/todo/<name>.md docs/todo/archive/<name>.md
  git mv docs/questions/<name>.md docs/questions/archive/<name>.md
  git commit -m "chore(<name>): archive <DROPPED|MERGED>"
  ```
- The `archive/` subdirectories do not exist yet (`ls docs/todo/archive` → no such directory); they are created by the first move, on `main`, by the orchestrator — **not** by this PR (see "Follow-up actions").

### G3 — `.agents/skills/git/SKILL.md:59`, S7.1 done-criteria

- **Before (tail, verbatim):** "…the remote branch is deleted (`git push origin --delete`); `git worktree list` shows only the primary (`main`) worktree."
- **After:** append — " the change's TODO and question files are moved to `docs/todo/archive/` and `docs/questions/archive/` (the question file always moves with its TODO file)."

### G4 — `.agents/skills/git/SKILL.md:114-135`, Post-merge cleanup — new step 5

- **Anchor (verbatim, the last numbered step, `:132-135`):** `4. Delete the remote branch:` followed by a `bash` block containing `git push origin --delete <type>/<name>`.
- **Add step 5** after it: "Move the planning records to the archive (from the primary worktree, after the `Status: MERGED` advance): `git mv docs/todo/<name>.md docs/todo/archive/<name>.md && git mv docs/questions/<name>.md docs/questions/archive/<name>.md`, committed as `chore(<name>): archive MERGED`."

### G5 — `.agents/skills/git/SKILL.md:155`, Rules — the direct-to-`main` rule

- **Before (verbatim):**
  ```markdown
  - Commit **directly to `main`** only for the planning records under `docs/todo/` and `docs/questions/` — their creation at P.1–P.3 and every `Status:` advance through `MERGED` — and only from the primary worktree. Everything else reaches `main` only through a merged PR.
  ```
- **After:** "…every `Status:` advance through `MERGED` **and `DROPPED`, and the archive move of the two records into `docs/todo/archive/` and `docs/questions/archive/`** — …".

### Deliberate non-edit (measured, so the scope stays minimal)

- `.agents/skills/git/SKILL.md:102` (the `BLOCKED-USER` cleared-gate test reads `docs/questions/<name>.md`) — **unchanged**: a change is archived only at the drop decision or after merge, and a WAITING change is by definition neither, so the test never has to look in the archive. `AGENTS.md:412` (A8) is the one place the archive is named, because that bullet is where the orchestrator decides whether to resume at all.
- `AGENTS.md:118` and `:135` ("the planning records **under** `docs/todo/` and `docs/questions/`") — **unchanged**: `docs/todo/archive/` is already inside those paths, so the direct-to-`main` permission needs no rewording there.
- `AGENTS.md:677` (the Prohibition "Commit anything except the Phase P planning artifacts … directly to `main`") — **unchanged** for the same reason.

---

## Explicitly out of scope (each with the answer that excludes it)

| Excluded | Decided by |
|---|---|
| A new numbered `P.0 Value triage` step; the Phase P atomic-steps table beyond the P.1 row; the Workflow Diagram (`AGENTS.md:221-236`); the Ownership sentences (`:329`/`:335`/`:365`); the Atomic Steps chain (`:339`); the todo-set rules (`:420`, `:422`) | **Q-1 = (b)** — "a mandatory Value triage clause inside P.1 Frame, plus one short 'Backlog value triage' paragraph under Phase P. No new numbered step, no Phase P table/diagram/todo-set edits" |
| `.agents/skills/specify/SKILL.md:14`, `:45`, `:46` | **Q-1 = (b)** + **Q-4 = (a)** — "`specify/SKILL.md:45`/`:46` are out of scope (the `workflow-docs-nits` collision dissolves)"; those three lines already carry the merged qualifiers (re-measured above) |
| `AGENTS.md:305`, `:410` ("**Never idle.**"), `:388`, `:676` (the idle Prohibition); any global stop | **Q-2 = (a)** — per-item stop at P.4; "the 'never idle' rule, the WAITING rules and the corresponding Prohibition stay untouched (no reclassification)" |
| Any change to the READY gate (`AGENTS.md:147`), the Spec Approval Gate, RED/GREEN, or the Phase 5/6 gates | TODO Out of scope — "Changing what any existing gate requires … the triage sits **before** them" |
| `docs/questions/template.md` (all of it, incl. `:18-25`), `docs/specs/template.md`, `specify/SKILL.md:69-75` (P.2/P.3), the `≥ 20`-question floor (`AGENTS.md:142`), any `Recommended:` field | **closed point 12** — those are owned by `spec-interview-protocol`, which lands **after** this change (Q-4 = (a)) |
| A question-file entry for the triage ask or the decision | **Q-5 = (ii)** — "recorded **only** in the TODO's `## Value triage` section … no question-file entry, so a dropped item's question file stays clean" |
| `AGENTS.md:19-51` (the Ponytail ladder) | TODO Out of scope — the new text **references** it (A5) instead of restating it (closed point 3) |
| Any script, CI job, or machine-readable score/threshold validation | TODO Out of scope — "the triage is a documented step, not a checker"; no auto-drop threshold exists (closed point 5) |
| `src/`, `tests/`, `docs/specs/`, `docs/verification/traceability.md`, `.github/workflows/`, `pyproject.toml`, `userdocs/` | DOCS/CHORE — no behavior delta; **no version bump** (Versioning: `REFACTOR / DOCS-CHORE → none`) |
| The archive **move** of the already-dead/merged records, and setting `Status: DROPPED` on `docs-path-ci-trigger` / `split-archived-qa` | **not in this PR** — `docs/todo/` and `docs/questions/` are never written in a change worktree (AGENTS.md "Planning records", `git/SKILL.md` Rules); they are orchestrator `main` actions **after** this change merges |

---

## No-behavior-delta confirmation

The change touches **only Markdown process guidance**. Measured against the base commit:

| Check | Result | Evidence (measured at `535816c`) |
|---|---|---|
| `src/` | **none** | no edit row names a `src/` path |
| `tests/` | **none** | no edit row names a `tests/` path |
| CI (`.github/workflows/`) | **none** | no edit row names a workflow file |
| Dependencies (`pyproject.toml`, lockfile) | **none** | no dependency is added or removed |
| Spec files (`docs/specs/`) | **none** | no spec is touched, added or amended — and no spec governs this guidance (grep above) |
| Version bump | **none** | `AGENTS.md` Versioning: "`REFACTOR / DOCS-CHORE` → none" |
| Externally observable product behavior | **none** | the only new human interaction (the triage ask) is a protocol step in Phase P; it is not reachable from any product interface |

### Quality gates: which still apply, and why they are unaffected

| Gate | Runs for this PR? | Why unaffected |
|---|---|---|
| `uv run ruff check .` / `ruff format` | **Not in CI** — `lint.yml` is path-filtered to `src/**`, `tests/**`, `pyproject.toml`, `.pre-commit-config.yaml`, `.github/workflows/lint.yml`, `.github/hooks/**`; a docs-only PR does not trigger it. The pre-commit `ruff-check` / `ruff-format` hooks still run locally | no Python file is edited, so there is nothing for ruff to check |
| `uv run mypy src/` | `quality.yml` has **no** path filter, so the `mypy` job runs | no file under `src/` is edited; the check is byte-identical to `main` |
| `uv run --group docs mkdocs build --strict` | runs (`quality.yml`, unfiltered; also the `mkdocs-build` pre-commit hook) | `mkdocs.yml` sets `docs_dir: userdocs`, so `AGENTS.md` and `.agents/skills/` are **outside** the mkdocs build; `grep -rln "AGENTS.md" userdocs/` → no match, so no nav/link can break |
| `uv run python scripts/check_traceability.py` | runs (`spec-validation.yml` fires because `docs/verification/value-triage-gate.md` is in its paths filter) | the script reads only `docs/specs/*.md` (excluding `template.md`), `docs/verification/traceability.md` and `tests/**/*.py` — never `AGENTS.md`, `docs/todo/`, `docs/questions/` or a per-change verification record; no REQ/AC ID is invented, so referential integrity cannot break |
| `uv run pytest tests/` | runs (`quality.yml`) | no test or source file changes; the suite result is identical to `main` |
| `alembic upgrade head`, `deptry .` | run (`quality.yml`) | no models, no migrations, no dependency changes |
| `markdown-formatting` (mdformat) | runs | the edits keep pipe tables, fenced blocks, one blank line between blocks, no trailing whitespace, final newline (pre-commit `trailing-whitespace` / `end-of-file-fixer` enforce it) |

**Phase 5 for this change** therefore reduces to: the full suite unchanged vs `main`, `ruff check .` clean, `mypy src/` clean, `mkdocs build --strict` clean, `check_traceability.py` clean, and the diff limited to the 22 rows above.

---

## Collision and sequencing (measured at `535816c`)

**No in-flight branch modifies any file this change edits.** Measured with `git diff --name-only main...<branch>`:

| Branch / PR | Diff vs `main` today | Overlap with this scope |
|---|---|---|
| `crosscut/structlog-logging` (worktree exists; spec PR #67 OPEN, TODO `WAITING`) | `tests/…`, `docs/verification/structlog-logging.md`, `docs/tasks/structlog-logging.tasks.json`, `.github/task-runner/tasks.json` | **none now**; its Phase 4 will edit `AGENTS.md:767`/`:769` (Using the Logging Feature, its Q-23) — a different section |
| `feature/structure-map` (worktree exists; spec PR #69 OPEN, TODO `WAITING`) | `docs/specs/structure-map.md`, `docs/verification/structure-map.md` | **none now**; its implementation will edit `AGENTS.md` Tooling (`:52-68`), Skill-to-Phase Mapping (`:308-321`, its Q-14 `(ambient)` row), Project Structure (`:1112`+), and a `mypy scripts/` Tooling line (its Q-28a) — all different sections |
| `issue/pytest-randomly` (worktree exists) | empty | none |

**Prospective collisions and the required order** (the TODO's "Depends on" plus the live backlog):

| Other change | Its planned edit | Required order |
|---|---|---|
| `workflow-docs-nits` — **MERGED** (PR #64 as `5d59374`) | `AGENTS.md:144`/`:160`/`:207`, `docs/todo/template.md:44`, `specify/SKILL.md:14`/`:45`/`:46` | **already landed before this base**; its qualifiers are re-measured above and built on, not restated (Q-4 = (a)) |
| `spec-interview-protocol` — `QUESTIONS-ANSWERED`, **lands after this change** (Q-4 = (a)) | `docs/questions/template.md`, `docs/specs/template.md` §1, `specify/SKILL.md:71-75` (P.2), possibly `AGENTS.md:142` (the **P.2 Interrogate** row) | **must rebase on top of this change**: its `AGENTS.md:142` edit is the row directly below this change's A2 at `:141` in the same table. It must re-measure line numbers after this change lands |
| `structure-map` implementation (after PR #69 merges) | `AGENTS.md` Tooling / Skill-to-Phase Mapping / Project Structure | no textual overlap with A1–A10; if it opens after this PR merges, rebase for line shifts only |
| `structlog-logging` implementation (after PR #67 merges) | `AGENTS.md:767`/`:769` | no overlap; rebase for line shifts only |
| `codecov-coverage-badge`, `ruff-d-docstrings`, `python-3.15`, `tenacity-rich-cachetools` (all `PREPARING`) | CI / `pyproject.toml` / `src/` docstrings / README badge; `AGENTS.md` is cited as a convention, not edited | none |
| `docs-path-ci-trigger` — **DROPPED** (1/5), `split-archived-qa` — **DROPPED** (1/5) | none (dead) | they are the **first users** of the new `DROPPED` status and the archive move — as orchestrator `main` actions after this change merges |
| `remove-spec-tdd-driver` — `MERGED` (PR #62, 2026-10-03) | none | archive move only |

**Rebase rule for this PR:** the branch is based on `535816c`, which already contains the `workflow-docs-nits` merge. If any other `AGENTS.md` edit merges before this PR, rebase and **re-measure every line number in the Scope table** before Phase 4 — the anchors are the record's traceability, not decoration.

---

## Follow-up actions (orchestrator, on `main`, **after** this change merges — never part of this PR)

The two `Disposition:` workaround lines exist precisely because the vocabulary had no `DROPPED`; once this change is merged they become real status values:

| Record | Action |
|---|---|
| `docs/todo/docs-path-ci-trigger.md` (+ its question file) | set `Status: DROPPED`, move both to `docs/todo/archive/` and `docs/questions/archive/` |
| `docs/todo/split-archived-qa.md` (+ its question file) | same |
| the 7 `Status: MERGED` records (`architecture-tests-missing`, `pyproject-tooling-gaps`, `remove-spec-tdd-driver`, `session-lookup-unwired`, `track-python-skill`, `update-readme`, `workflow-docs-nits`) | move to the archive folders at the next convenient `main` commit (they are finished; their question files move with them) |
| `docs/todo/remove-spec-tdd-driver.md:7` | the line literally starts with a stray `^` (`^- **Status:** MERGED`) — fix it while moving the file (a planning-record typo, out of scope for this change) |
| `docs/todo/tenacity-rich-cachetools.md:8` | carries an open note asking the user to confirm the "keep" reading of a conflicting answer — orchestrator to confirm with the user, not part of this change |

---

## P.4 self-check (every answer → an edit, every edit → an answer)

### Forward: each ANSWERED question and where it lands

| Question (all ANSWERED 2026-10-04) | Binding answer | Edit rows | Also enforced as a non-edit |
|---|---|---|---|
| **Q-1** Where the triage is codified | **(b)** clause inside P.1 Frame + one paragraph | A2, A5, A6, A10, S1, S4, S5, T2 | no `P.0` row; diagram `:221-236`, ownership `:329`/`:335`/`:365`, atomic-steps chain `:339`, todo-set rules `:420`/`:422`, `specify:14`/`:45`/`:46` untouched |
| **Q-2** When the user must answer | **(a)** per-item stop at P.4 | A5 (the stop sentence), A6, A9, S1, S4 | `AGENTS.md:305`, `:410` (never idle), `:388`, `:676` byte-identical — no reclassification |
| **Q-3** `DROPPED` in the vocabulary | **(a)** yes, minimal | A4, T1, S2, G1, G2, G5 | the 16 existing backlog files are not rewritten |
| **Q-4** Landing order | **(a)** nits → this → interview-protocol | the Collision and sequencing table; the re-measured qualifier table; the T2 line-shift note | `docs/questions/template.md`, `docs/specs/template.md`, `specify:69-75`, the `≥ 20` floor left to `spec-interview-protocol` |
| **Q-5** Single TODO outside a sweep | **(ii)** immediate ask, riding the existing P.3 round-trip; recorded only in the TODO | A2 (done-when), A5 (ask timing + "never as a question-file entry"), T2 (`**Decision:**` bullet), S1, S4, S5 | no question-file entry anywhere; `docs/questions/template.md` untouched |
| **Q-7** Where dead items go | **(i)** `docs/todo/archive/` + `docs/questions/archive/`, moved by the orchestrator at the drop decision and at S7.1, question file always moves with the TODO | A1, A3, A4, A7, A8, S3, G1, G2, G3, G4, G5 | `git/SKILL.md:102` and `AGENTS.md:118`/`:135`/`:677` unchanged (measured, reasons recorded above) |

**Every ANSWERED question produces at least one edit row; no answer is left unimplemented.**

### Reverse: each edit row is decided by an answer

The **Edit index** table above carries a `Decided by` column for all 22 rows (A1–A10, T1–T2, S1–S5, G1–G5). Checked: **no row is unattributed**, and no row cites an answer that does not exist (the file has exactly Q-1, Q-2, Q-3, Q-4, Q-5, Q-7 — Q-6 was closed as a duplicate of Q-5 and generates no edit of its own; its content is in A5/T2 via Q-5).

### Consistency checks run at P.4

| Check | Result |
|---|---|
| Line numbers re-measured at the base commit, not copied from the question file | ✅ `grep -n` over `AGENTS.md`, `docs/todo/template.md`, `docs/questions/template.md`, `specify/SKILL.md`, `git/SKILL.md` at `535816c` |
| The question file's cited numbers that have **drifted** | `AGENTS.md:141` (P.1 row) and `:155`-`:162` (status table) match; `AGENTS.md:411`/`:412` (Ready order / Resume) match; `:661`/`:703` match; `specify/SKILL.md:64`-`:67`, `:167`-`:171`, `:196`-`:198`, `:211` match; `git/SKILL.md:22`, `:59`, `:65`, `:114`-`:135`, `:155` match; `docs/todo/template.md:7` matches |
| `workflow-docs-nits` qualifiers present in the live tree | ✅ all four (`template.md:44`, `specify:14`, `:45`, `:46`) — re-measured, and this change does not re-touch them |
| The 1–5 anchors match the rule text verbatim | ✅ copied from `docs/todo/value-triage-gate.md:31`-`:56` |
| The `## Value triage` block matches the shape the live records already use | ✅ 5 of the 16 backlog TODOs already carry a hand-written `## Value triage` section; the template block is their superset (adds `**Decision:**`) |
| No REQ/AC ID invented | ✅ process guidance has no IDs; `check_traceability.py` cannot be affected |
| No existing gate weakened | ✅ READY gate, Spec Approval Gate, RED/GREEN, Phase 5/6 gates are not in the edit list |
| Archive folders do not yet exist | ✅ `ls docs/todo/archive` → no such directory; created by the orchestrator on `main`, not in this PR |

---

## P.4 done-criteria checklist (this step)

- [x] Change branch `chore/value-triage-gate` and worktree `../python-template_kopie-worktrees/chore/value-triage-gate` created from `main` (`535816c`) — the branch carries the TODO file and the answered questions
- [x] `docs/todo/` and `docs/questions/` **not modified** in this worktree (orchestrator-owned on `main`) — `git status` after the commit shows only `docs/verification/value-triage-gate.md`
- [x] The **exact non-behavior scope** is recorded: 22 edits in 4 files, each with its location, verbatim current text, planned change, and the deciding answer
- [x] **No-behavior-delta confirmation** recorded (no `src/`, no `tests/`, no CI, no dependency, no spec file, no version bump) with the gate-by-gate applicability table
- [x] Collision / sequencing table recorded, with the rebase rule and the required order relative to `workflow-docs-nits` (merged), `spec-interview-protocol` (after) and the two in-flight worktrees
- [x] Follow-up orchestrator actions on `main` listed separately so they cannot be mistaken for this PR's content
- [x] No implementation edit made (that is Phase 4); no P.5 run (DOCS/CHORE has no self-consistency step)
- [x] Committed in the worktree as `chore(value-triage-gate): P.4 scope record (DOCS/CHORE)`

---

## S4.2 Implement (Phase 4, DOCS/CHORE — "make the scoped non-behavior changes")

Run in the change worktree on top of `77ae870`. No RED/GREEN (DOCS/CHORE has no test step), no new tests, no test file touched.

### Row-by-row confirmation — all 22 rows applied, every "before" anchor matched verbatim

Located by the quoted text (not the recorded line number), as instructed. **Zero anchor mismatches** — no row needed an improvised edit, so no row deviates from the deciding Q-ID's decision.

| Row | File | Applied | Anchor matched verbatim | Resulting location |
|---|---|---|---|---|
| A1 | `AGENTS.md` | ✅ archive destination added to both `Committed to` cells; no new row | ✅ | `:130-131` |
| A2 | `AGENTS.md` | ✅ P.1 Frame row: objective + done-when clauses | ✅ | `:141` |
| A3 | `AGENTS.md` | ✅ Planning-records paragraph: the joint **move** sentence + the `archive-AI_Questions.md` disclaimer | ✅ | `:151` |
| A4 | `AGENTS.md` | ✅ `MERGED` row qualified + new `DROPPED` row added after it | ✅ | `:162-163` |
| A5 | `AGENTS.md` | ✅ new `### Backlog value triage` subsection (planned text used verbatim) | ✅ | `:182-184` |
| A6 | `AGENTS.md` | ✅ Phase Matrix note: one appended sentence; the five `**P Prepare**` cells untouched | ✅ | `:220` |
| A7 | `AGENTS.md` | ✅ Ready selection order: appended sentence | ✅ | `:416` |
| A8 | `AGENTS.md` | ✅ Resume / cleared-gate bullet: appended sentence | ✅ | `:417` |
| A9 | `AGENTS.md` | ✅ new Prohibition bullet after the classify-before-implement bullet | ✅ | `:667` |
| A10 | `AGENTS.md` | ✅ Obligation 17: appended clause before the final period; `≥ 20` floor untouched | ✅ | `:709` |
| T1 | `docs/todo/template.md` | ✅ `DROPPED` added to the `Status:` comment vocabulary; value stays `PREPARING` | ✅ | `:7` |
| T2 | `docs/todo/template.md` | ✅ new `## Value triage` section between `## Constraints and risks` and `## Acceptance signal (plain language)`; **no** Prep-log row | ✅ | `:34-39` |
| S1 | `.agents/skills/specify/SKILL.md` | ✅ P.1 Frame: Objective / Inputs / Outputs / Done-criteria clauses | ✅ | `:64-67` |
| S2 | `.agents/skills/specify/SKILL.md` | ✅ status chain gains `**DROPPED**` + the archive-move gloss | ✅ | `:169` |
| S3 | `.agents/skills/specify/SKILL.md` | ✅ planning-record-paths rule: appended joint-archive sentence | ✅ | `:171` |
| S4 | `.agents/skills/specify/SKILL.md` | ✅ new Value-triage Outputs bullet after the TODO bullet + the P.4 branch bullet clause | ✅ | `:197`, `:199` |
| S5 | `.agents/skills/specify/SKILL.md` | ✅ Definition of Done, first bullet: appended sentence | ✅ | `:212` |
| G1 | `.agents/skills/git/SKILL.md` | ✅ Execution Context bullet: `DROPPED` + the archive move, one sentence, no new bullet | ✅ | `:22` |
| G2 | `.agents/skills/git/SKILL.md` | ✅ status chain gains `→ DROPPED`; one sentence + one fenced `git mv`/commit block after the existing block | ✅ | `:65`, `:73-80` |
| G3 | `.agents/skills/git/SKILL.md` | ✅ S7.1 done-criteria: appended archive clause | ✅ | `:59` |
| G4 | `.agents/skills/git/SKILL.md` | ✅ Post-merge cleanup: new step 5 (the two `git mv` + the `archive MERGED` commit) | ✅ | `:146-151` |
| G5 | `.agents/skills/git/SKILL.md` | ✅ Rules: direct-to-`main` permission extended to `DROPPED` + the archive move | ✅ | `:171` |

**Wording normalizations inside the planned text (no decision changed):**

- **G1** — the planned text had two adjacent bold spans (`…through \`MERGED\`** **and \`DROPPED\`…`); they are merged into one span (`**and every TODO \`Status:\` advance through \`MERGED\` and \`DROPPED\`, and the archive move of both records**`). Same Q-3 + Q-7 decision, valid Markdown.
- **G4** — the scope record quoted step 5 inline; it is rendered as a numbered list item with a fenced `bash` block, matching steps 1–4 in the same operation.

### Diff scope proof

`git diff --name-status` (before the evidence commit):

```text
M       .agents/skills/git/SKILL.md
M       .agents/skills/specify/SKILL.md
M       AGENTS.md
M       docs/todo/template.md
```

- **Only the 4 scoped files** — 52 insertions, 22 deletions; every hunk maps to one of the 22 rows (checked hunk by hunk against the diff).
- **No** `src/`, `tests/`, `docs/specs/`, `docs/verification/traceability.md`, `.github/workflows/`, `pyproject.toml`, `uv.lock`, `userdocs/`, `docs/questions/` or backlog TODO file is touched — and `docs/todo/` is touched **only** at `docs/todo/template.md` (the template, not a planning record).
- **Wording hazard (TODO "Constraints and risks") checked:** `git diff -U0 | grep -c "Never idle\|Idle or wait in place\|Non-blocking:"` → **0**. `AGENTS.md` `:310` (Non-blocking), `:415` (Never idle), `:682` (the idle Prohibition) and the READY gate (`:147`) are byte-identical — the new text reads as one batched backlog gate plus a per-item stop at P.4, not a blocking gate on every change.
- **Deliberate non-edits respected:** `git/SKILL.md:102` at base → `:111` after this step (the `BLOCKED-USER` cleared-gate test), `AGENTS.md:118`/`:135`/`:677`, `AGENTS.md:19-51` (Ponytail), `docs/questions/template.md`, `specify/SKILL.md:14`/`:45`/`:46`/`:69-75`, the Workflow Diagram, the Ownership sentences, the Atomic Steps chain and the todo-set rules — none in the diff.
- No trailing whitespace (`git diff --check` clean), final newline present in all four files.

### No-behavior-delta checks — base (`77ae870`) vs after, no delta

| Command | Base (`77ae870`, before the edits) | After the 22 rows | Delta |
|---|---|---|---|
| `uv run ruff check .` | `All checks passed!` | `All checks passed!` | **none** |
| `uv run mypy src/` | `Success: no issues found in 83 source files` | `Success: no issues found in 83 source files` | **none** |
| `uv run python scripts/check_traceability.py` | `Traceability: PASS (765 matrix rows, 129 spec IDs, 714 test functions)` | `Traceability: PASS (765 matrix rows, 129 spec IDs, 714 test functions)` | **none** |
| `uv run --group docs mkdocs build --strict` | `Documentation built in 2.64 seconds`, no warning/error | `Documentation built in 1.54 seconds`, no warning/error | **none** |

`ruff` is reported here as the whole-repo sweep because the step's changed paths are Markdown only — there is nothing for ruff to check in them; the sweep is the delta proof against `main`. (`lint.yml` is path-filtered to `src/**`, `tests/**`, `pyproject.toml`, `.pre-commit-config.yaml`, `.github/workflows/lint.yml`, `.github/hooks/**`, so this PR does not trigger the lint job at all.)

**Record correction for Phase 5/6:** the P.4 gate table lists a `markdown-formatting (mdformat)` check that "runs". Measured: there is **no mdformat hook** in `.pre-commit-config.yaml` and **no markdown job** in `.github/workflows/` (`grep -rn -i "mdformat\|markdown" .github/ pyproject.toml` → only a `pyproject.toml` comment about Markdown code blocks in ruff's exclusion). The formatting requirements the row describes were therefore verified by hand (`git diff --check`, final newlines, pipe tables and fenced blocks intact) rather than by a tool.

### Consistency sweep — places the scope record did not cover (reported, **not** edited)

Grepped the status vocabulary (`PREPARING`/`QUESTIONS-ANSWERED`/`READY`/`IN-WORKFLOW`/`WAITING`/`MERGED`/`DROPPED`) and `docs/todo/`/`docs/questions/` path mentions over `AGENTS.md`, `.agents/skills/*/SKILL.md`, `docs/*/template.md`, `userdocs/`, `scripts/`. `userdocs/` and `scripts/` name neither (so the mkdocs site and `check_traceability.py` cannot go stale). Every hit inside the 22 rows is updated; these are **outside** the 22 rows and are left byte-identical for Phase 5/6 to adjudicate:

| # | Place | What it enumerates | Assessment |
|---|---|---|---|
| 1 | `AGENTS.md:118` (Git Worktrees → Rules) | "every later `Status:` advance **through `MERGED`**" | **Scope finding.** The P.4 record lists `:118` as a deliberate non-edit, but its stated reason covers only the *path* argument (`docs/todo/archive/` is inside `docs/todo/`). It does not cover the *chain endpoint*: `DROPPED` is a status advance that follows `MERGED` in the sentence's ordering. Harmless (the archive move is inside the permitted paths, and A3/G5 state it explicitly), but the sentence is now slightly under-inclusive |
| 2 | `.agents/skills/git/SKILL.md:12` (Purpose → delegate list) | "every `Status:` advance through `MERGED` directly to `main`" | **Scope finding** — same under-inclusiveness as #1; G1 (`:22`) and G5 (`:171`) carry the full wording, `:12` is the summary line above them |
| 3 | `AGENTS.md:419` (Multi-change scheduling → "Backlog status on `main`") | "**WAITING**, **IN-WORKFLOW** and **MERGED** are written to the change's TODO file **on `main`**" | **Scope finding** — `DROPPED` is also written on `main` (A4 adds that advance); the enumeration is now incomplete |
| 4 | `docs/questions/template.md:3`, `:6` | the TODO-file cross-reference; no archive destination | **Known out of scope** (closed point 12 — the whole file is owned by `spec-interview-protocol`). The question file's archive move is stated in A3/A4/S3/G2/G3/G4/G5, so the guidance is not contradicted, only not restated in the template |
| 5 | `docs/todo/template.md:5` | "like `docs/questions/`, it is committed directly to `main`" | **Scope finding (minor)** — T1/T2 cover `:7` and the new section; `:5` does not mention the archive move |
| 6 | `.agents/skills/specify/SKILL.md:12` (Purpose summary) | the skill's output list: TODO + question file + draft spec / triage / baseline / scope | **Scope finding (minor)** — the summary does not name the `## Value triage` section; `:45`/`:46` are explicitly out of scope (Q-1 = (b), Q-4 = (a)), `:12` was simply never in the 22 rows |
| 7 | `AGENTS.md:370` (Roles → Orchestrator) | P.1's description: classify, create the two records, create the todo set | **Deliberately out of scope** per Q-1 = (b) ("the Ownership sentences `:329`/`:335`/`:365`") — recorded here for completeness |

No place in the tree now *contradicts* the new `DROPPED` status or the two archive folders; #1–#3 and #5–#6 are enumerations that stop short of naming them.

### S4.2 done-criteria checklist (this step)

- [x] All **22 rows** applied; every "before" anchor matched verbatim (0 mismatches, 0 improvised edits)
- [x] The diff touches **only the 4 scoped files** (`git diff --name-status` above); no `src/`, `tests/`, `docs/specs/`, `traceability.md`, `.github/workflows/`, `pyproject.toml` change
- [x] Every hunk maps to one of the 22 rows
- [x] The four quality commands report **no new failure** vs the `77ae870` base (identical output)
- [x] The wording hazard checked: the never-idle rules, the WAITING rules and the idle Prohibition are not in the diff
- [x] Consistency sweep run; 7 uncovered places **reported**, none edited
- [x] No test file, no spec, no behavior touched; no version bump (DOCS/CHORE)
- [x] Evidence recorded here and committed in the worktree
