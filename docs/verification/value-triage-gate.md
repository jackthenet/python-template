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

**22 edits in 4 files, all Markdown** — **25 with A11/A12/G6**, the three rows added to this table at the **S4.2 re-entry** after the S5 adjudication of finding 1 (see "S4.2 re-entry (A11/A12/G6) + re-verified gate set"), **30 with G7/G8/G9/A13/G2a**, the five rows added at the **S4.2 re-entry #2** after the S6.1 review findings F-1/F-2 (see "S4.2 re-entry #2 (F-1/F-2) + completeness sweep"), and **35 with G10/G11/A14/V1/V2**, the five rows added at the **S4.2 re-entry #3** after the S6.2 findings B-1/N-1/T-1 (see "S4.2 re-entry #3 (B-1, N-1, T-1)"). The 22-row count is the scope as approved at P.4; the guidance file set stays the same **4 files** — **V1/V2 are corrections inside this record** and are the only two rows that are not guidance text. Every "before" below was re-read from the file in this worktree at P.4 with `grep -n` (line numbers are from the base commit `535816c`, **not** copied from the question file). The `workflow-docs-nits` qualifiers are **already live** and are re-measured, not restated:

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
| A11 | `AGENTS.md` | `:118` (Git Worktrees → Rules — the direct-to-`main` permission, chain endpoint) | Q-3 = (a), Q-7 = (i) — **row added at the S4.2 re-entry** (S5 finding 1.1) |
| A12 | `AGENTS.md` | `:414` (Multi-change scheduling → "Backlog status on `main`", the status set) | Q-3 = (a) — **row added at the S4.2 re-entry** (S5 finding 1.3) |
| G6 | `.agents/skills/git/SKILL.md` | `:12` (When to Use — the planning-commit summary line above G1) | Q-3 = (a), Q-7 = (i) — **row added at the S4.2 re-entry** (S5 finding 1.2) |
| G7 | `.agents/skills/git/SKILL.md` | `:56` (S7.1 **Objective** bullet — the action set) | Q-7 = (i) — **row added at the S4.2 re-entry #2** (S6.1 finding F-1) |
| G8 | `.agents/skills/git/SKILL.md` | `:58` (S7.1 **Outputs** bullet — the action set) | Q-7 = (i) — **row added at the S4.2 re-entry #2** (F-1) |
| G9 | `.agents/skills/git/SKILL.md` | `:41` (Todo — the cleanup item's status-order sentence) | Q-7 = (i) — **row added at the S4.2 re-entry #2** (F-1) |
| A13 | `AGENTS.md` | `:443` (Todo Tracking Discipline → "Status orders", the Post-merge cleanup bullet) | Q-7 = (i) — **row added at the S4.2 re-entry #2** (F-1) |
| G2a | `.agents/skills/git/SKILL.md` | `:65` (planning-commit operation — the arrow-rendered `Status:` chain, same place as G2) | Q-3 = (a), Q-7 = (i) — **row added at the S4.2 re-entry #2** (F-2, wording only) |
| G10 | `.agents/skills/git/SKILL.md` | `:73-80` (planning-commit operation — the archive-move code block: `mkdir -p` before the `git mv` pair) | Q-7 = (i) — **row added at the S4.2 re-entry #3** (S6.2 finding B-1) |
| G11 | `.agents/skills/git/SKILL.md` | `:146-151` (Post-merge cleanup step 5 — the same `mkdir -p` line in the S7.1 code block) | Q-7 = (i) — **row added at the S4.2 re-entry #3** (B-1) |
| A14 | `AGENTS.md` | `:425` (Todo Tracking Discipline — "One todo set per change", the closure sentence) | Q-3 = (a) — **row added at the S4.2 re-entry #3** (N-1) |
| V1 | `docs/verification/value-triage-gate.md` (this record) | `:280` (the G2 row's claim that the archive folders "are created by the first move") | Q-7 = (i) — **row added at the S4.2 re-entry #3** (B-1, record correction; no guidance file) |
| V2 | `docs/verification/value-triage-gate.md` (this record) | `:413` (the "Reverse: each edit row is decided by an answer" lead sentence) | **record-consistency fix (T-1)** — no deciding Q, no guidance file — **row added at the S4.2 re-entry #3** |

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
- The `archive/` subdirectories do not exist yet (`ls docs/todo/archive` → no such directory); the **move step creates them** with `mkdir -p docs/todo/archive docs/questions/archive` before the `git mv` pair, on `main`, by the orchestrator — **not** by this PR (see "Follow-up actions").
- **Correction (S4.2 re-entry #3, S6.2 finding B-1 — row V1).** This bullet originally read "they are created by the first move". That claim is **false**: `git mv` does not create the destination directory. Measured in a scratch repo at `81a389b` (`git init` → commit → `git mv docs/todo/demo.md docs/todo/archive/demo.md`): `fatal: renaming 'docs/todo/demo.md' failed: No such file or directory`, exit **128**; the same sequence succeeds only after `mkdir -p` (see "S4.2 re-entry #3 (B-1, N-1, T-1)" for the full proof). The guidance is fixed by **G10/G11**; this record is corrected here rather than silently rewritten.

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
- `AGENTS.md:135` ("the planning records **under** `docs/todo/` and `docs/questions/`") — **unchanged**: `docs/todo/archive/` is already inside those paths, so the direct-to-`main` permission needs no rewording there.
- **Narrowed at the S4.2 re-entry (scope-contract fix).** This entry originally also listed `AGENTS.md:118`. The argument it gives is the **path** argument only — and that half still holds (`docs/todo/archive/` is inside `docs/todo/`). It never argued the **chain endpoint**: `:118` ends its permission at "every later `Status:` advance through `MERGED`", which after this change forbids the `DROPPED` advance and the `git mv` pair the change authorizes. `:118` is therefore **edited by A11**, not left alone; `:135` (and `:677`/`AGENTS.md:683`) stay deliberate non-edits because they are path-only mentions with no chain endpoint.
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

The **Edit index** table above carries a `Decided by` column for all **35 rows** — **A1–A14, T1–T2, S1–S5, G1–G11, G2a, V1–V2** (growth history: 22 as approved at P.4 → 25 with A11/A12/G6 at the S4.2 re-entry → 30 with G7/G8/G9/A13/G2a at re-entry #2 → 35 with G10/G11/A14/V1/V2 at re-entry #3; the table is the authority for the count, **V2**). Every guidance row is attributed to the same Q-3 = (a) / Q-7 = (i) answers that produced A4/T1/S2/G1/G2/G5. Checked: **no guidance row is unattributed**, and no row cites an answer that does not exist (the file has exactly Q-1, Q-2, Q-3, Q-4, Q-5, Q-7 — Q-6 was closed as a duplicate of Q-5 and generates no edit of its own; its content is in A5/T2 via Q-5). The two designed exceptions are both record rows: **V1** cites Q-7 = (i) because it corrects a claim about the archive move, and **V2** cites **no** Q — it is a record-consistency fix (the T-1 note) that touches no guidance file.

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

---

## S5 Verify (Phase 5, DOCS/CHORE light gate set)

Run in the change worktree on top of `ff17c66` (S4.2); working tree clean before (`git status --short` → empty) and after. The applicable gate set is `AGENTS.md` → "Phase 5: VERIFY → DOCS/CHORE": **"Run lint and type checks where applicable; confirm no test files or behavior were touched."**

**Phase 5 step mapping for this type.** S5.1 (full test suite) and S5.3 (traceability) are **not DOCS/CHORE gates**: no spec exists, so **spec coverage is n/a** (there is no REQ/AC to cover — the P.4 record invents no IDs), and `docs/verification/traceability.md` is deliberately untouched, so there is nothing for S5.3 to add. S5.2 (lint + types) and S5.4 (this report) are the running steps, plus the two DOCS/CHORE confirmations (diff scope, no test/behavior touched).

### Gate table — every gate re-run at HEAD and compared with the `77ae870` base recorded in the S4.2 section

| # | Gate | Command (run in the worktree) | Base (`77ae870`) | After (`ff17c66` = HEAD) | Verdict |
|---|---|---|---|---|---|
| G-1 | Lint (whole-repo sweep, matches `lint.yml`) | `uv run ruff check .` | `All checks passed!` | `All checks passed!` | **PASS** — no delta |
| G-2 | Types (CI gate, `quality.yml` → `type-check`) | `uv run mypy src/` | `Success: no issues found in 83 source files` | `Success: no issues found in 83 source files` | **PASS** — no delta |
| G-3 | Traceability referential integrity (`spec-validation.yml` → `traceability`) | `uv run python scripts/check_traceability.py` | `Traceability: PASS (765 matrix rows, 129 spec IDs, 714 test functions)` | `Traceability: PASS (765 matrix rows, 129 spec IDs, 714 test functions)` | **PASS** — identical counts, no delta |
| G-4 | Docs site, strict (`quality.yml` → `docs`) | `uv run --group docs mkdocs build --strict` | exit 0, `Documentation built in 2.64 seconds`, no `WARNING:`/`ERROR:` | exit 0, `Documentation built in 1.54 seconds`, no `WARNING:`/`ERROR:` | **PASS** — no delta (wall-clock only; the only stderr line is the Material-for-MkDocs 2.0 announcement banner, not a build warning) |
| G-5 | Diff scope = the 4 guidance files + this record | `git diff --name-only main...HEAD` | 5 paths expected | exactly 5 paths (below) | **PASS** |
| G-6 | No test file touched | `git diff --name-only main...HEAD -- tests/` | empty | **empty** | **PASS** |
| G-7 | No behavior delta (no Python, no config, no dependency, no spec) | `git diff --name-only main...HEAD \| grep -E "^(src/\|tests/\|docs/specs/\|docs/verification/traceability\.md\|\.github/workflows/\|pyproject\.toml\|uv\.lock\|userdocs/\|docs/questions/\|docs/todo/[^t])"` | no match | **no match**; `\.py` files in the diff: **0** | **PASS** |
| G-8 | Markdown hygiene (the P.4 row's intent — no tool enforces it, see finding 2) | `git diff --check main...HEAD`; final newlines; pipe tables / fenced blocks render | clean | `git diff --check` **clean**; all 5 files end with a newline | **PASS** |
| G-9 | Wording hazard (never-idle / WAITING rules byte-identical) | `git diff -U0 main...HEAD -- AGENTS.md .agents/skills docs/todo/template.md \| grep -cE "^[-+].*(Never idle\|Idle or wait in place\|Non-blocking:)"` — scoped to the guidance files (S4.2 ran the same check unscoped on its then-uncommitted edits) | 0 | **0** — `AGENTS.md:147` (the READY gate), `:310` (Non-blocking), `:415` (Never idle), `:682` (the idle Prohibition) are not in the diff. The same grep over the **whole** range returns **4**, all four inside this record quoting the phrases, not guidance edits | **PASS** |
| G-10 | Version bump | `git diff main...HEAD -- pyproject.toml` | empty | **empty** — `AGENTS.md` Versioning: `REFACTOR / DOCS-CHORE → none` | **PASS** — correctly no bump |

### Diff-scope proof (measured at HEAD)

```text
$ git log --oneline main..HEAD
ff17c66 chore(value-triage-gate): S4.2 apply the 22-row scope (value triage as a P.1 clause, DROPPED status, archive layout)
77ae870 chore(value-triage-gate): P.4 scope record (DOCS/CHORE)

$ git status --short
(empty)

$ git diff --name-only main...HEAD
.agents/skills/git/SKILL.md
.agents/skills/specify/SKILL.md
AGENTS.md
docs/todo/template.md
docs/verification/value-triage-gate.md

$ git diff --numstat main...HEAD
20	4	.agents/skills/git/SKILL.md
9	8	.agents/skills/specify/SKILL.md
15	9	AGENTS.md
8	1	docs/todo/template.md
527	0	docs/verification/value-triage-gate.md
```

- **Exactly the 4 scoped guidance files + this change's own verification record.** Nothing else, on the whole `main...HEAD` range (both commits, P.4 + S4.2).
- **Forbidden-path check (G-7) is empty** for `src/`, `tests/`, `docs/specs/`, `docs/verification/traceability.md`, `.github/workflows/`, `pyproject.toml`, `uv.lock`, `userdocs/`, `docs/questions/` — and for `docs/todo/` **except** `docs/todo/template.md` (the template, not a planning record; the 16 backlog TODO files are untouched, as the P.4 record requires).
- `docs/todo/archive/` and `docs/questions/archive/` still **do not exist** in this branch (`ls` → *No such file or directory*): the archive move is an orchestrator `main` action after merge, not this PR's content (P.4 "Follow-up actions").

### No-test-touched proof, and what CI actually runs for this PR

`git diff --name-only main...HEAD -- tests/` → **empty**. The suite is unaffected **by construction**, which is stronger than a re-run:

- **0 Python files** in the diff (`git diff --name-only main...HEAD | grep -c '\.py$'` → `0`) — no `src/`, no `tests/`, no `conftest.py`;
- **no `pyproject.toml` / `uv.lock`** change, so the pytest configuration, the dependency set and the import path are byte-identical to `main`;
- the 5 changed paths are Markdown that **no test imports and no fixture reads** — `grep -rln "AGENTS.md\|\.agents/skills" tests/ scripts/` finds no reader of them, and `check_traceability.py` reads only `docs/specs/*.md`, `docs/verification/traceability.md` and `tests/**/*.py` (all three unchanged, hence the identical G-3 counts).

What CI will run anyway (measured from the `on:` filters in `.github/workflows/`), so nothing is left unverified by not re-running 728 tests locally:

| Workflow | Trigger for this PR | Jobs that run |
|---|---|---|
| `quality.yml` | **no `paths:` filter** → runs | `type-check` (`uv run mypy src/` gate; `ty check src/` informational), `security` (`pip-audit`, `bandit -r src/`), `coverage` (**`uv run pytest tests/ --cov --cov-report=xml`**), `dependency-review`, `dependencies` (`deptry .`), `docs` (`uv run mkdocs build --strict`), `migrations` (`uv run alembic upgrade head`), `complexity` (`complexipy src tests --max-complexity-allowed 15`) |
| `spec-validation.yml` | `paths:` includes `docs/verification/**` → **runs** (this PR adds `docs/verification/value-triage-gate.md`) | `spec-validation` (`verify_spec.py` over every `docs/specs/*.md`), `traceability` (`check_traceability.py`), `tests` (**`uv run pytest tests/ -v`**) |
| `lint.yml` | `paths:` = `src/**`, `tests/**`, `pyproject.toml`, `.pre-commit-config.yaml`, `.github/workflows/lint.yml`, `.github/hooks/**` → **does not run** | none (no changed path matches) |

So the full suite runs **twice** in CI for this PR (the `coverage` and `tests` jobs) and the ruff job does not — the local G-1 sweep is therefore *more* than CI requires, and the local suite skip costs nothing in evidence.

### Guidance self-consistency check — every live place that enumerates the `Status:` vocabulary or the two archive folders

Grepped `AGENTS.md`, `.agents/skills/*/SKILL.md`, `docs/todo/template.md`, `docs/questions/template.md`, `userdocs/`, `scripts/` for `DROPPED`, `PREPARING`/`QUESTIONS-ANSWERED`, `through \`MERGED\`` and `docs/todo/archive` / `docs/questions/archive`. `userdocs/` and `scripts/` name **neither** (so the mkdocs site and `check_traceability.py` cannot go stale).

| Place (at HEAD) | What it states | Covered? |
|---|---|---|
| `AGENTS.md:130-131` | both records + the archive destination + the `DROPPED`/`MERGED` trigger | **covered** (A1) |
| `AGENTS.md:151` | the joint **move** + the `archive-AI_Questions.md` disclaimer | **covered** (A3) |
| `AGENTS.md:155-163` | the status-advance table, incl. the new `DROPPED` row and both moves | **covered** (A4) |
| `AGENTS.md:184` | `Status: DROPPED` + the archive move | **covered** (A5) |
| `AGENTS.md:416` | the archive folders are the finished/dead set ⇒ the live folders are the backlog | **covered** (A7) |
| `AGENTS.md:417` | an archived change is not resumed | **covered** (A8) |
| **`AGENTS.md:118`** | direct-to-`main` allowed for "every later `Status:` advance **through `MERGED`**" | **NOT covered → finding 1.1** |
| **`AGENTS.md:419`** | "**WAITING**, **IN-WORKFLOW** and **MERGED** are written … on `main`" | **NOT covered → finding 1.3** |
| `AGENTS.md:135`, `:683` (base `:677`) | path-only mentions ("under `docs/todo/` and `docs/questions/`"); **no chain endpoint** | **n/a — correct as-is** (`docs/todo/archive/` is inside those paths); the P.4 deliberate non-edit stands |
| `AGENTS.md:370` (base `:365`, Roles → Orchestrator) | P.1 = classify + create the two records + todo set | **out of scope** — Q-1 = (b) excludes the Ownership sentences |
| `AGENTS.md:394` | the retired central file `docs/questions/archive-AI_Questions.md` | **n/a** — unrelated to the new folder; A3 states the distinction |
| **`.agents/skills/git/SKILL.md:12`** | "every `Status:` advance through `MERGED` directly to `main`" | **NOT covered → finding 1.2** |
| `.agents/skills/git/SKILL.md:22`, `:65`, `:77-79`, `:146-151`, `:171` | the chain + `DROPPED` + the `git mv` pair + the direct-to-`main` rule | **covered** (G1, G2, G4, G5) |
| `.agents/skills/git/SKILL.md:59` | S7.1 done-criteria: both files move to the archive | **covered** (G3) |
| `.agents/skills/git/SKILL.md:111` (base `:102`) | the `BLOCKED-USER` cleared-gate test reads `docs/questions/<name>.md` | **deliberate non-edit** — a WAITING change is by definition neither dropped nor merged, so the test never has to look in the archive |
| `.agents/skills/specify/SKILL.md:169`, `:171`, `:197`, `:199`, `:212` | the chain + `DROPPED` + the archive move + the Value-triage outputs and Definition of Done | **covered** (S2, S3, S4, S5) |
| `.agents/skills/specify/SKILL.md:12` (Purpose output list) | TODO + question file + spec / triage / baseline / scope | **not covered — no action**: the `## Value triage` section lives *inside* the already-listed TODO file, so nothing is contradicted |
| `docs/todo/template.md:7` | the `Status:` comment vocabulary incl. `DROPPED` | **covered** (T1) |
| `docs/todo/template.md:34-39` | the `## Value triage` section incl. the archive note | **covered** (T2) |
| `docs/todo/template.md:5` | "committed directly to `main`" — no chain, no archive | **not covered — no action**: still true, not an enumeration |
| `docs/questions/template.md:3`, `:6`, `:9` | the file's own `OPEN` / `ALL ANSWERED` vocabulary; the retired central file | **out of scope** — closed point 12 (`spec-interview-protocol` owns the whole file); its archive move is stated in A3/A4/S3/G2/G3/G4/G5 |

**Result:** no place in the tree *contradicts* the new status or the archive folders, but **three** statements of the same rule stop short of it — and two of them are the direct-to-`main` permission this change extends.

---

## S5 adjudication of the three S4.2 findings

### Finding 1 — three places state the status chain / backlog-status set without `DROPPED`

**Adjudication: (i) a gap this change must close — fix before Phase 6.**

Why it is a gap and not a nit:

1. **The change creates a contradiction between two statements of the same rule.** The direct-to-`main` permission is stated twice — `AGENTS.md:118` (Git Worktrees → Rules) and `.agents/skills/git/SKILL.md:171` (Rules, G5). G5 now reads "…every `Status:` advance through `MERGED` **and `DROPPED`, and the archive move of the two records**…"; `:118` still ends at `MERGED`. Same for the git skill's own summary (`:12`) versus the operation it summarizes (`:22`, G1). And `AGENTS.md:419` enumerates the statuses written on `main` while `AGENTS.md:163` (A4, added by this change) writes a new one there.
2. **`AGENTS.md:118` is an exclusive rule, not a description**: "Direct-to-`main` commits are allowed **only** … Nothing else … may be committed directly to `main`". Read strictly, after this change it forbids exactly the two actions the change authorizes (the `DROPPED` advance and the `git mv` pair). The git skill tells every reader to read that section first ("Read that section first; this skill assumes its conventions"), so it is the sentence an agent acts on.
3. **Q-7's own binding answer requires it**: "the live guidance that names those two paths must be updated in the same change". `AGENTS.md:118` and `git/SKILL.md:12` name precisely those two paths inside the rule the archive move extends. The P.4 "Deliberate non-edit" entry for `:118` argued only the *path* half ("`docs/todo/archive/` is already inside those paths") — that half still holds; the *chain endpoint* half was never argued.
4. **Cost asymmetry.** Three micro-edits in two already-touched files. Deferring them means a second DOCS/CHORE change (worktree, Phase P, Phase 5/6, PR) to add four words — strictly worse.

**Exact fix list (3 edits; the deciding answers are the same Q-3 = (a) and Q-7 = (i) that produced A4/T1/S2/G1/G2/G5 — record them as new scope rows A11, A12, G6):**

| Row | File:line | Before (verbatim, at HEAD) | After |
|---|---|---|---|
| **A11** | `AGENTS.md:118` | `…their creation at P.1–P.3 **and every later \`Status:\` advance through \`MERGED\`** (see "Planning records (owner: the orchestrator)").` | `…their creation at P.1–P.3 **and every later \`Status:\` advance through \`MERGED\` and \`DROPPED\`, and the archive move of the two records** (see "Planning records (owner: the orchestrator)").` |
| **A12** | `AGENTS.md:419` | `- **Backlog status on \`main\`.** **WAITING**, **IN-WORKFLOW** and **MERGED** are written to the change's TODO file **on \`main\`** …` | `- **Backlog status on \`main\`.** **WAITING**, **IN-WORKFLOW**, **MERGED** and **DROPPED** are written to the change's TODO file **on \`main\`** …` (nothing else in the bullet changes — A7 already covers the archive in the adjacent bullet) |
| **G6** | `.agents/skills/git/SKILL.md:12` | `…commit the change's planning records (\`docs/todo/<name>.md\`, \`docs/questions/<name>.md\`) and every \`Status:\` advance through \`MERGED\` directly to \`main\`.` | `…commit the change's planning records (\`docs/todo/<name>.md\`, \`docs/questions/<name>.md\`) and every \`Status:\` advance through \`MERGED\` and \`DROPPED\`, and the archive move of both records, directly to \`main\`.` |

**Must stay untouched while fixing:** `AGENTS.md:135` and `:683` (path-only, no chain endpoint — verified by grep: neither mentions `MERGED`), `git/SKILL.md:111` (the cleared-gate test), the never-idle rules and the idle Prohibition. The P.4 "Deliberate non-edit" entry for `AGENTS.md:118` must be **narrowed** to the path argument only.

### Finding 2 — the P.4 gate table claims a `markdown-formatting (mdformat)` check runs

**Adjudication: (ii) a record inaccuracy — noted and already corrected in place; no code/CI action, no fix step.**

- Measured at HEAD: `grep -rn -i "mdformat\|markdown" .github/ pyproject.toml .pre-commit-config.yaml` → **one** hit, a `pyproject.toml:170` comment about ruff excluding Markdown code blocks. The pre-commit hooks are `ruff-check`, `ruff-format`, `trailing-whitespace`, `end-of-file-fixer`, `check-yaml`, `check-added-large-files`, `deptry`, `mkdocs-build`; the workflows are `lint.yml`, `quality.yml`, `spec-validation.yml` — **no markdown job**. So the P.4 row named a check that does not exist.
- **Impact on the gate set: none.** Markdown formatting is not part of the DOCS/CHORE gate set (`AGENTS.md` Phase 5: lint + types where applicable + no test/behavior touched). The formatting requirements that row described were verified by hand at S4.2 and re-verified here at S5 (G-8: `git diff --check` clean, final newlines, pipe tables and fenced blocks intact — note `mkdocs --strict` does **not** cover `AGENTS.md`/`.agents/skills/`, `docs_dir: userdocs`).
- **Do not add an mdformat hook in this change**: the P.4 escalation rule states a new script/CI job must be re-scoped, not silently added, and it would alter CI for every other change. If markdown formatting is wanted, it is a separate DOCS/CHORE idea for the backlog.
- **Action:** none. The P.4 table is the historical record of what the scope author measured at P.4; the S4.2 section already carries the correction ("Record correction for Phase 5/6") and this section closes it. Per the historical-record convention (`AGENTS.md`, Traceability: a dated record is a legal record of a past gate, not a defect), the P.4 row is **not** rewritten.

### Finding 3 — two wording normalizations inside planned text (G1 bold spans merged; G4 rendered as a numbered item with a fenced `bash` block)

**Adjudication: (iii) out of scope — not a defect, no action.**

- The P.4 record grants the latitude explicitly for planned text ("final wording may be tightened in Phase 4 without changing any of the clauses", A5), and both normalizations are inside planned text.
- Verified at HEAD: `git/SKILL.md:22` carries the full G1 decision (the `DROPPED` endpoint + the archive move) in one bold span — the planned `…\`MERGED\`** **and…` would have been two adjacent spans, valid but redundant; `git/SKILL.md:146-151` renders step 5 as a numbered item with a fenced `bash` block, matching steps 1–4 of the same operation (`:140-144`), which is what a numbered procedure requires.
- No decision, clause, Q-ID or anchor changed; both are documented in the S4.2 section, so Phase 6 can compare the applied text against the planned text. **No fix.**

---

## Verification verdict

**VERIFIED WITH FINDINGS.** *(superseded — see "S4.2 re-entry (A11/A12/G6) + re-verified gate set": the required fix step ran and the verdict is re-issued there as **VERIFIED**)*

- The **DOCS/CHORE gate set passes in full** (G-1 … G-10): lint clean, mypy clean, traceability clean with identical counts, `mkdocs build --strict` exit 0 with no warnings, the diff limited to the 4 scoped guidance files + this record, **no test file and no behavior touched**, no version bump (correct for the type). Spec coverage is **n/a** — the change has no spec and invents no REQ/AC ID.
- **One open finding:** finding 1 (three stale statements of the rule this change extends — `AGENTS.md:118`, `AGENTS.md:419`, `.agents/skills/git/SKILL.md:12`). It is a direct consequence of adding `DROPPED` and the archive layout, so it belongs to this change and must be closed by a **fix step (S4.2 re-entry, 3 micro-edits, rows A11/A12/G6)** before Phase 6 review. After that step, re-confirm G-1 … G-9 (the same commands) and re-issue this verdict as **VERIFIED**.
- Findings 2 and 3 are closed here: a record inaccuracy already corrected in place, and a wording normalization that is not a defect.

### S5 done-criteria checklist (this step)

- [x] Every gate has a command, a result and a `77ae870` base comparison (G-1 … G-10)
- [x] Diff-scope proof recorded: exactly the 4 guidance files + this record; no `src/`, `tests/`, `docs/specs/`, `traceability.md`, `.github/workflows/`, `pyproject.toml`, `uv.lock`, `userdocs/`, `docs/questions/`, no backlog TODO file
- [x] No-test-touched proof recorded (`tests/` diff empty; 0 Python files) + what CI runs for this PR given the path filters (full suite twice; `lint.yml` not triggered)
- [x] Guidance self-consistency check recorded: every place enumerating the `Status:` vocabulary or the two archive folders, marked covered / not covered / n/a
- [x] All three S4.2 findings adjudicated with an explicit verdict and, for finding 1, an exact 3-edit fix list
- [x] Verdict recorded: **VERIFIED WITH FINDINGS** (one fix step required before Phase 6)
- [x] No implementation/guidance file edited by this step (adjudicate and recommend only); no Phase 6 work, no PR, no version bump; `docs/todo/` and `docs/questions/` untouched in this worktree
- [x] Committed in the worktree as `chore(value-triage-gate): S5 verification report (DOCS/CHORE light gate set)`

---

## S4.2 re-entry (A11/A12/G6) + re-verified gate set

Run in the change worktree on top of `d90ec0c` (S5); working tree clean before (`git status --short` → empty). This is the **fix step the Phase 5 verdict required**: the three micro-edits of the "S5 adjudication of the three S4.2 findings" (finding 1), then the same gate set re-run and the verdict re-issued. Nothing else was touched — no Phase 6 work, no PR, no version bump, no `docs/todo/` or `docs/questions/` write in this worktree.

### The three edits (verbatim before → after; located by text, not by line number)

| Row | File (line at `d90ec0c`) | Before (verbatim) | After (as applied) |
|---|---|---|---|
| **A11** | `AGENTS.md:118` | `…their creation at P.1–P.3 **and every later \`Status:\` advance through \`MERGED\`** (see "Planning records (owner: the orchestrator)").` | `…their creation at P.1–P.3 **and every later \`Status:\` advance through \`MERGED\` and \`DROPPED\`, and the archive move of the two records** (see "Planning records (owner: the orchestrator)").` |
| **A12** | `AGENTS.md:419` | `- **Backlog status on \`main\`.** **WAITING**, **IN-WORKFLOW** and **MERGED** are written to the change's TODO file **on \`main\`** …` | `- **Backlog status on \`main\`.** **WAITING**, **IN-WORKFLOW**, **MERGED** and **DROPPED** are written to the change's TODO file **on \`main\`** …` |
| **G6** | `.agents/skills/git/SKILL.md:12` | `…and every \`Status:\` advance through \`MERGED\` directly to \`main\`.` | `…and every \`Status:\` advance through \`MERGED\` and \`DROPPED\`, and the archive move of both records, directly to \`main\`.` |

- Each anchor matched **exactly once** (`grep -c` → `1` for all three); the replacement is text-only, so the rest of every bullet is byte-identical. `git diff HEAD` for the guidance files: **`2 files changed, 3 insertions(+), 3 deletions(-)`** — one changed line for G6, two for A11/A12.
- Deciding answers: **Q-3 = (a)** and **Q-7 = (i)** — the same answers that produced A4/T1/S2/G1/G2/G5. No new decision, no new clause, no gate changed.
- The three edits close the contradiction the adjudication identified: the direct-to-`main` permission is now stated identically at `AGENTS.md:118` and `git/SKILL.md:171` (G5), the git skill's summary (`:12`) matches the operation it summarizes (`:22`, G1), and the backlog-status set (`AGENTS.md:419`) now includes the `DROPPED` advance that A4 (`:163`) writes on `main`.

### Scope-contract fix in the P.4 record (same step)

- The P.4 **"Deliberate non-edit"** entry no longer lists `AGENTS.md:118`. Its stated reason covered only the **path** argument (`docs/todo/archive/` is inside `docs/todo/`) — that half still holds — and it never argued the **chain endpoint**, which is exactly what A11 changes. `AGENTS.md:135` and `:683` (base `:677`) remain deliberate non-edits: path-only mentions with no chain endpoint.
- The P.4 **Edit index** gained **A11 / A12 / G6** with their deciding Q-IDs, and its lead sentence now reads "22 edits in 4 files … — **25 with A11/A12/G6**, the three rows added at the S4.2 re-entry", explicitly marked as added after the S5 adjudication. The rest of the P.4 record is not rewritten (historical-record convention, `AGENTS.md` Traceability).
- **Scope contract ↔ applied diff:** 25 rows, 4 guidance files; every applied hunk maps to a row, and every row is applied. Guidance-file numstat at this step (`git diff $(git merge-base main HEAD)`): `AGENTS.md` 17/11, `git/SKILL.md` 21/5, `specify/SKILL.md` 9/8, `docs/todo/template.md` 8/1 (the record row grows by this section).

### Must-stay-untouched proof (re-verified after the edits)

| Place | State after A11/A12/G6 |
|---|---|
| `AGENTS.md:135` | **unchanged** — path-only ("the **only** files the workflow may commit directly to `main`"), no `MERGED`, no chain endpoint |
| `AGENTS.md:683` (base `:677`) | **unchanged** — the Prohibition "Commit anything except the Phase P planning artifacts (`docs/todo/`, `docs/questions/`) directly to `main`" |
| `.agents/skills/git/SKILL.md:111` (base `:102`) | **unchanged** — the `BLOCKED-USER` cleared-gate test still reads `docs/questions/<name>.md` |
| `AGENTS.md:310` (Non-blocking), `:415` (Never idle), `:682` (the idle Prohibition) | **unchanged** — the path-scoped wording-hazard grep below returns **0** |
| `AGENTS.md:147` (the READY gate) | **unchanged** — not in the diff |

### Re-confirmed gate set — the same commands as S5, re-run at this step

| # | Gate | Command (in the worktree) | Base (`77ae870`) | After A11/A12/G6 | Verdict |
|---|---|---|---|---|---|
| G-1 | Lint | `uv run ruff check .` | `All checks passed!` | `All checks passed!` | **PASS** — no delta |
| G-2 | Types | `uv run mypy src/` | `Success: no issues found in 83 source files` | `Success: no issues found in 83 source files` | **PASS** — no delta |
| G-3 | Traceability | `uv run python scripts/check_traceability.py` | `Traceability: PASS (765 matrix rows, 129 spec IDs, 714 test functions)` | `Traceability: PASS (765 matrix rows, 129 spec IDs, 714 test functions)` | **PASS** — identical counts |
| G-4 | Docs site, strict | `uv run --group docs mkdocs build --strict` | exit 0, `Documentation built in 2.64 seconds`, no `WARNING:`/`ERROR:` (S5 record) | exit 0, 0 `WARNING:`/`ERROR:` (built in 1.54 s and 2.84 s across the two runs at this step — wall-clock only) | **PASS** — no delta |
| G-5 | Diff scope | `git diff --name-only main...HEAD` | 5 paths | exactly the same **5 paths** (4 guidance files + this record) | **PASS** |
| G-6 | No test file | `git diff --name-only main...HEAD -- tests/` | empty | **empty** | **PASS** |
| G-7 | No behavior delta | the forbidden-path grep over `git diff --name-only main...HEAD` (`src/`, `tests/`, `docs/specs/`, `traceability.md`, `.github/workflows/`, `pyproject.toml`, `uv.lock`, `userdocs/`, `docs/questions/`, `docs/todo/` except the template) | no match | **no match**; `.py` files in the diff: **0** | **PASS** |
| G-8 | Markdown hygiene | `git diff --check main...HEAD`; final newline; pipe tables / fenced blocks intact | clean | `git diff --check` **clean** (exit 0); record and both guidance files end with a newline; the three edits are inline text inside existing bullets, no table or fence touched | **PASS** |
| G-9 | Wording hazard (path-scoped) | `git diff -U0 -- AGENTS.md .agents/skills docs/todo/template.md \| grep -cE "^[-+].*(Never idle\|Idle or wait in place\|Non-blocking:)"` | 0 | **0** | **PASS** |
| G-10 | Version bump | `git diff main...HEAD -- pyproject.toml` | empty | **empty** (0 lines) — `REFACTOR / DOCS-CHORE → none` | **PASS** |

**Branch-vs-`main` note (measured, no action).** `main` advanced by one commit since the P.4 base — `e1b7706 chore(value-triage-gate): status READY`, a planning-record status advance touching only `docs/todo/value-triage-gate.md`. It changes no `AGENTS.md`/skill line, so the P.4 rebase rule ("re-measure every line number if another `AGENTS.md` edit merges first") is **not** triggered; the scope measure stays the three-dot range from the merge-base `535816c`. (A two-dot `git diff main` additionally shows that TODO file for exactly this reason — it is the orchestrator's `main` commit, not this branch's content.)

### Verification verdict (re-issued)

**VERIFIED.**

- The DOCS/CHORE gate set passes in full (G-1 … G-10), with **no delta** against the `77ae870` base on every command; spec coverage is **n/a** (no spec, no invented REQ/AC ID); no test file and no behavior touched; correctly no version bump.
- **Finding 1 is closed** by A11/A12/G6: the `DROPPED` status chain and the archive move are now stated consistently in all five places that enumerate them (`AGENTS.md:118`, `:130-131`, `:151`, `:155-163`, `:419`; `git/SKILL.md:12`, `:22`, `:65`, `:77-79`, `:146-151`, `:171`), and the three must-stay-untouched places are proven byte-identical.
- **Finding 2 stays closed** as a record inaccuracy (the P.4 gate table named an `mdformat` check that does not exist; corrected in place at S4.2/S5, no code/CI action, no hook added).
- **Finding 3 stays closed** as an out-of-scope note (the G1 bold-span merge and the G4 numbered-item rendering are wording normalizations inside planned text, permitted by the P.4 record).

### S4.2 re-entry done-criteria checklist (this step)

- [x] Exactly the three adjudicated edits applied (A11/A12/G6), each anchor matched once, rest of the bullets byte-identical
- [x] The P.4 "Deliberate non-edit" entry for `AGENTS.md:118` narrowed to the path argument; A11/A12/G6 added to the Edit index with Q-3 = (a) / Q-7 = (i) — scope contract (25 rows) matches the applied diff
- [x] Must-stay-untouched set re-verified (`AGENTS.md:135`, `:683`, `git/SKILL.md:111`, the never-idle rules, the idle Prohibition, the READY gate)
- [x] Gate set re-run and recorded with base comparison: ruff / mypy / traceability / mkdocs / diff scope / no-test / no-behavior / markdown hygiene / wording hazard / no bump — all **PASS**, no delta
- [x] Verdict re-issued: **VERIFIED** (the S5 verdict is marked superseded in place)
- [x] No Phase 6 work, no PR, no version bump, no `docs/todo/` or `docs/questions/` write, no test/spec/source file touched
- [x] Committed in the worktree as `chore(value-triage-gate): S4.2 re-entry - close DROPPED status-chain gap (A11/A12/G6), verdict VERIFIED`

---

## S6.1 Review vs. normative basis

Phase 6, step 1 (review skill, **DOCS/CHORE** routing: normative basis = the **P.4 scope record**, there is no spec). Run in the change worktree at HEAD `d800da4`; working tree clean before (`git status --short` → empty).

**Bounded inputs (per the review skill's "Bounded scope" rule):** the P.4 scope contract (25 rows + the out-of-scope table + the deliberate non-edits), the S4.2 / S5 / S4.2-re-entry sections of this record, `docs/questions/value-triage-gate.md` (6 ANSWERED questions), and the **final state** of the 4 changed guidance files. Reviewed as a fresh reader would read the touched passages end-to-end. **Not** reviewed: commit-by-commit history; the full test suite (Phase 5 already confirmed the gate CLEAN — not re-run here); implementation style (out of scope for S6.1).

### Check 1 — scope conformance: all 25 rows present, each saying what its deciding Q-ID requires

Located by text, not by line number. `git diff --numstat main...HEAD` (guidance files): `AGENTS.md` 17/11, `git/SKILL.md` 21/5, `specify/SKILL.md` 9/8, `docs/todo/template.md` 8/1 — **25 removed lines, 55 added lines**, every hunk maps to a row.

| Row | Present in the final text | Says what the deciding Q-ID requires |
|---|---|---|
| A1 (`AGENTS.md:130-131`) | ✅ | both `Committed to` cells carry the archive destination + the `DROPPED`/`MERGED` trigger; **no new row** (Q-7 (i), Q-5 "inside the TODO") |
| A2 (`:141`) | ✅ | P.1 row: objective clause + done-when clause; **no `P.0` row**, the table still has exactly P.1–P.5 (Q-1 (b)) |
| A3 (`:151`) | ✅ | the joint **move** sentence, both moments (drop decision, S7.1), question file moves with the TODO, `archive-AI_Questions.md` disclaimer (Q-7 (i)) |
| A4 (`:162-163`) | ✅ | `MERGED` row qualified + new `DROPPED` row with its trigger moment (Q-3 (a), Q-7 (i)) |
| A5 (`:182-184`) | ✅ | the new `### Backlog value triage` subsection — **byte-identical to the planned text** in the P.4 record (measured: `planned == actual` after stripping the heading) |
| A6 (`:220`) | ✅ | one appended sentence under the Phase Matrix; the five `**P Prepare**` cells untouched (closed point 10) |
| A7 (`:416`) | ✅ | the two live folders are the backlog to select from (Q-7 (i)) |
| A8 (`:417`) | ✅ | an archived change is finished/dead and is **not resumed** — the cleared-gate/resume rule Q-7 named (Q-7 (i)) |
| A9 (`:667`) | ✅ | the new Prohibition is a **P.4 boundary rule**, not a gate change (Q-2 (a), closed point 9) |
| A10 (`:709`) | ✅ | Obligation 17 clause appended; the `≥ 20` floor byte-identical (closed point 12) |
| T1 (`docs/todo/template.md:7`) | ✅ | `DROPPED` added to the comment vocabulary; the value stays `PREPARING` (Q-3 (a)) |
| T2 (`:34-39`) | ✅ | the `## Value triage` section — **byte-identical to the P.4 block** (measured), in the predicted slot; the `workflow-docs-nits` Prep-log row shifted `:44 → :51` exactly as the record predicted, content unchanged; **no Prep-log row added** |
| S1 (`specify:64-67`) | ✅ | all four P.1 Frame bullets carry their clause |
| S2 (`:169`) | ✅ | chain gains `/ **DROPPED**` + the archive gloss (Q-3 (a)) |
| S3 (`:171`) | ✅ | the joint archive move appended to the planning-record-paths rule (Q-7 (i)) |
| S4 (`:197`, `:199`) | ✅ | the new Value-triage Outputs bullet + the "only after that change's own value-triage decision" clause on the P.4 bullet (Q-1 (b), Q-2 (a)) |
| S5 (`:212`) | ✅ | the Definition-of-Done sentence (authorized by the question file's own "For P.4" plan) |
| G1 (`git:22`) | ✅ | one sentence, no new bullet (Q-3, Q-7) |
| G2 (`:65`, `:73-80`) | ✅ | chain + the `git mv` pair block (Q-3, Q-7) |
| G3 (`:59`) | ✅ | S7.1 done-criteria gain the move (Q-7 (i)) — see finding F-1 for the sibling bullets |
| G4 (`:146-151`) | ✅ | new numbered step 5 with the two `git mv` + the `archive MERGED` commit (Q-7 (i)) |
| G5 (`:171`) | ✅ | the direct-to-`main` permission extended to `DROPPED` + the move (Q-3, Q-7) |
| A11 (`AGENTS.md:118`) | ✅ | the chain endpoint + the move — now identical to G5 (the S5 fix) |
| A12 (`:419`) | ✅ | the backlog-status set now includes `DROPPED` (the S5 fix) |
| G6 (`git:12`) | ✅ | the summary line now matches the operation it summarizes (the S5 fix) |

**Nothing outside the rows changed.** `git diff --name-status main...HEAD` → exactly `M AGENTS.md`, `M docs/todo/template.md`, `M .agents/skills/specify/SKILL.md`, `M .agents/skills/git/SKILL.md`, `A docs/verification/value-triage-gate.md`. The deliberate non-edits are byte-identical: `AGENTS.md:135`, `:683`, `:147` (the READY gate), `:19-51` (Ponytail), `:310`/`:415`/`:682` (never-idle + the idle Prohibition), the Workflow Diagram, the Ownership sentences, the Atomic Steps chain, the todo-set rules, `docs/questions/template.md`, `specify:14`/`:45`/`:46`/`:69-75`, `git:111-113` (the cleared-gate test).

### Check 2 — decision fidelity (each ANSWER answer re-read against the final text)

| Answer | Implemented as answered? | Evidence |
|---|---|---|
| **Q-1 = (b)** clause inside P.1 Frame + one paragraph, **no** new numbered step, `specify:45`/`:46` untouched | **yes** | the clause is in the P.1 row (`AGENTS.md:141`) and the P.1 Frame section (`specify:64-67`); exactly one new subsection (`AGENTS.md:182-184`); the Phase P table has P.1–P.5 only; the Workflow Diagram and the Atomic Steps chain have no hunk; `specify:14`/`:45`/`:46` are not in the diff |
| **Q-2 = (a)** per-item stop at P.4, never-idle rules untouched | **yes** | the stop is stated at `AGENTS.md:184` ("No TODO may pass P.4 … already-decided and READY changes keep running, so 'never idle' is unaffected"), `:220` (A6), `:667` (A9), `specify:199`; the path-scoped wording-hazard grep is **0** (`:310`, `:415`, `:682` byte-identical) — no global stop, no reclassification trigger fired |
| **Q-3 = (a)** `DROPPED` in the vocabulary | **yes** | `AGENTS.md:163` (table row), `docs/todo/template.md:7` (comment), `specify:169`, `git:12`/`:22`/`:65`/`:171`; no machine reader exists (`grep -rn "DROPPED\|PREPARING" scripts/ .github/ userdocs/` → **no match**) |
| **Q-4 = (a)** nits → this → interview-protocol | **yes** | the merged qualifiers are built on, not restated (`template.md:51`, `specify:14`/`:45`/`:46` untouched); `docs/questions/template.md`, `docs/specs/template.md`, `specify:69-75` and the `≥ 20` floor are untouched |
| **Q-5** immediate ask, recorded **only** in the TODO's `## Value triage` section, no question-file entry | **yes** | `AGENTS.md:184`: "a single TODO framed outside a sweep gets its ask **immediately**, as a one-row table riding that change's existing P.3 round-trip — no extra ⏸. The ask and the decision are recorded **only in the TODO's `## Value triage` section**, never as a question-file entry."; `template.md:34-39` carries the `**Decision:**` bullet; `docs/questions/template.md` untouched; no new ⏸ symbol anywhere in the diagram |
| **Q-7 = (i)** `docs/todo/archive/` + `docs/questions/archive/`, moved at the drop decision and at S7.1, question file moves with the TODO | **yes** | stated in 11 places (`AGENTS.md:130-131`, `:151`, `:162-163`, `:416-417`, `git:12`/`:22`/`:59`/`:73-80`/`:146-151`/`:171`, `specify:171`); the folders themselves are **not** created by this PR (`ls docs/todo/archive docs/questions/archive` → *No such file or directory*) — correct, they are orchestrator `main` actions (P.4 "Follow-up actions") |

No ANSWER is unimplemented; no edit contradicts an ANSWER.

### Check 3 — internal consistency of the new guidance (every enumeration of the status chain, the archive layout, the `main` permission and the S7.1 action set, in the 4 files)

| Place (final state) | Enumerates | Verdict |
|---|---|---|
| `AGENTS.md:118`, `:130-131`, `:151`, `:157-163`, `:416-417`, `:419` | the `main` permission, the archive destinations, the status table, the backlog set | **consistent** — the permission is now stated identically at `:118` and `git:171` (A11/G5), and the status set at `:419` includes `DROPPED` (A12) |
| `AGENTS.md:135`, `:683` | path-only mentions of the two folders | **correct as-is** — `docs/todo/archive/` is inside `docs/todo/`; neither names a chain endpoint |
| `AGENTS.md:147` (READY gate), `:310`, `:415`, `:682` | the gates and the never-idle rules | **byte-identical**, no contradiction with the per-item stop |
| `AGENTS.md:184` | the triage rule + `Status: DROPPED` + the move | **consistent** with A4/A3 |
| `AGENTS.md:106`, `:304`, `:353`, `:456`, `:466` | S7.1 as "verify + remove + delete" | **summaries that delegate** to the git skill's "Post-merge cleanup" operation, which now has step 5 → note F-3, no action |
| **`AGENTS.md:443`** | the S7.1 **todo completion condition** | **under-inclusive → F-1** |
| `git:12`, `:22`, `:65`, `:73-80`, `:146-151`, `:171` | the chain, the move, the `main` permission | **consistent** (G6/G1/G2/G4/G5) |
| **`git:41`** | the S7.1 **todo completion condition** | **under-inclusive → F-1** |
| **`git:56` / `:58` vs `:59`** | S7.1 Objective / Outputs vs Done-criteria — three consecutive bullets of the step section G3 edited | **inconsistent within one block → F-1** |
| `git:111-113` | the `BLOCKED-USER` cleared-gate test | **correct as-is** — it applies only to a WAITING change, which is by definition neither dropped nor merged (note F-4) |
| `git:3` (skill description) | the skill's operation summary | note F-3 |
| `specify:169`, `:171`, `:197`, `:199`, `:212` | the chain, the move, the P.4 boundary, the DoD | **consistent** (S2/S3/S4/S5) — see note F-7 on the DoD vs `AGENTS.md:147` |
| `docs/todo/template.md:7`, `:34-39` | the status vocabulary, the triage section | **consistent** (T1/T2); `:5` does not restate the move → note F-6 |

**No place now contradicts the `DROPPED` status, the archive folders or the `main` permission.** The remaining gaps are all in one class: the **S7.1 completion rule**, which the change extended in only one of its four statements.

### Check 4 — no behavior delta (the DOCS/CHORE contract)

Measured at HEAD `d800da4` against `main`:

| Check | Result |
|---|---|
| `src/`, `tests/`, `docs/specs/`, `docs/verification/traceability.md`, `.github/`, `pyproject.toml`, `uv.lock`, `userdocs/`, `docs/questions/` in the diff | **none** — the forbidden-path grep over `git diff --name-only main...HEAD` matches only `docs/todo/template.md` (the template, not a planning record) |
| Python files in the diff | **0** |
| Version bump | **none** — `git diff main...HEAD -- pyproject.toml` → 0 lines; `version = "0.6.1"` unchanged (correct: `REFACTOR / DOCS-CHORE → none`) |
| Machine readers of the changed guidance | **none** — `grep -rn "AGENTS\.md\|docs/todo\|docs/questions\|DROPPED\|PREPARING" scripts/ .github/ userdocs/` → no match (only task-runner files, untouched) |
| Markdown hygiene | `git diff --check main...HEAD` clean; all 4 files end with a newline; tables and fences intact |

### Check 5 — nothing weakened (the guidance counterpart of "tests weakened to achieve GREEN")

Compared every removed guidance line against the added lines (25 removed / 55 added):

- **Every removed line is a strict prefix of its added counterpart** — the only "lost" tokens are four sentence-final periods replaced by `;` continuations in the four `specify` P.1 bullets. No clause, modal or negation was dropped.
- Modal / negation counts, removed → added: `MUST` 1 → 1, `NOT` 1 → 1, `never` 5 → 7, `only` 12 → 16, `always` 2 → 4, `SHOULD` 0 → 0. Nothing was softened; the change only adds obligations and permissions.
- No gate's requirements were removed: the READY gate, the Spec Approval Gate, the RED/GREEN gates and the Phase 5/6 gates are not in the diff (the only gate-adjacent edit is the `specify` DoD — note F-7).
### Findings

| # | Finding | Severity | Evidence | Resolution / action |
|---|---|---|---|---|
| **F-1** | The **S7.1 completion rule** is stated in four places and G3 (`git:59`) updated only one. `git:56` (Objective) and `git:58` (Outputs) — the two bullets **directly above** the updated Done-criteria, inside the step section this change edited — still list three actions; `git:41` and `AGENTS.md:443` (the normative Todo Tracking Discipline status-orders list) still state the cleanup todo as `completed` "when the worktree is removed and the local + remote branches are deleted". Same class as S5 finding 1.2/1.3, which this change itself adjudicated as a gap to close, and the same cost asymmetry applies (4 micro-edits in 2 already-touched files vs a whole second DOCS/CHORE change) | **blocking** | `git:56` "…remove the worktree, and delete the local + remote branches." / `git:58` "…the worktree removed; the local + remote branches deleted." vs `git:59` "…; the change's TODO and question files are moved to `docs/todo/archive/` and `docs/questions/archive/` (the question file always moves with its TODO file)." | Exact fix, 4 rows (deciding answers unchanged: **Q-7 = (i)**, the same answer that produced G3/G4). **G7** `git:56` → "…verify the merge is reachable from `origin/main` (after `git fetch`), remove the worktree, delete the local + remote branches, and move the change's TODO and question files to their archive folders." **G8** `git:58` → append "; the change's TODO and question files moved to `docs/todo/archive/` and `docs/questions/archive/` (the question file with its TODO file)". **G9** `git:41` → "`completed` when the worktree is removed, the local + remote branches are deleted, and the two planning records have been moved to the archive folders." **A13** `AGENTS.md:443` → same wording as G9. Must stay untouched: `AGENTS.md:106`/`:304`/`:353` (delegating summaries), `git:111-113`, the never-idle rules, the READY gate |
| **F-2** | `git:65` renders the status chain with arrows — `… → IN-WORKFLOW → WAITING → MERGED → DROPPED` — which reads as if `DROPPED` follows `MERGED`. It does not: a dropped TODO never reaches `IN-WORKFLOW`/`MERGED`, `DROPPED` is an alternative terminal reached from the value-triage decision | **non-blocking** | `git:65` vs `AGENTS.md:157-163` (a moment → status table, unambiguous) and `specify:169` (`/ **MERGED** / **DROPPED**`, the correct alternative form) | Accept, or fold into the F-1 step by replacing `→ DROPPED` with "…→ `MERGED`, or `DROPPED` straight from the value-triage decision". No behavioral consequence — `AGENTS.md:157-163` is the authoritative mapping |
| **F-3** | `AGENTS.md:106`, `:304`, `:353`, `:456`, `:466` and `git:3` summarize post-merge cleanup as verify + remove + delete without the archive move | **note** | each names the git skill's "Post-merge cleanup" operation (`AGENTS.md:106` explicitly: "(git skill: \"Post-merge cleanup\")"), which now has step 5 | **No action** — they delegate to the authoritative procedure; extending the Workflow Diagram (`:304`) and the todo examples would widen the diff for no rule change |
| **F-4** | Q-7's answer lists "the cleared-gate test" among the places to update; `git:101-113` (Detect a cleared gate) is unchanged | **note** | the rule itself **is** updated at `AGENTS.md:417` (A8: an archived change "is not resumed"); the git-skill test fires only for a **WAITING** change, which by definition is neither dropped nor merged, so it never has to look in the archive. The non-edit and its reason are recorded in the P.4 "Deliberate non-edit" entry | **No action** — decision fidelity satisfied; the non-edit is reasoned and correct |
| **F-5** | `AGENTS.md:141` P.1 "Done when" now contains a condition that cannot be met at P.1 (the user's decision, which per Q-5 is recorded between P.3 and P.4) | **note** | the parenthetical "(the user's decision is recorded **before P.4**)" and A5's ask timing ("riding that change's existing P.3 round-trip") resolve the reading; `specify:67` states it identically, so the two files agree | **No action** — consistent, and the enforcement point is the P.4 boundary (A6/A9), not P.1 |
| **F-6** | `docs/todo/template.md:5` and `docs/questions/template.md` do not restate the archive move | **note** | `template.md:5` is a plain statement ("committed directly to `main`"), still true; `docs/questions/template.md` is owned by `spec-interview-protocol` (closed point 12) | **No action** — the move is stated in 11 places; already assessed no-action at S5 |
| **F-7** | `specify:212` adds the value-triage record to the skill's READY-gate Definition of Done while `AGENTS.md:147` (the normative READY gate) keeps its three conditions byte-identical | **note** | the skill's DoD is already a superset checklist (branch/worktree, change type, spec self-consistency) beyond `AGENTS.md:147`; the question file's own "For P.4" plan authorizes the `:207-224` edit; READY is reached after P.4, so the P.4 boundary rule (A6/A9) already implies it | **No action** — not a gate change (`AGENTS.md:147` is the out-of-scope item and is untouched), and it cannot let a change pass a gate it would otherwise fail |

### S6.1 verdict

**Findings — not clean yet.** The change implements its normative basis **exactly**: all 25 rows are present, each says what its deciding Q-ID requires, every ANSWER is implemented as answered (Q-1 (b), Q-2 (a), Q-3 (a), Q-4 (a), Q-5, Q-7 (i)), nothing outside the rows changed, there is no behavior delta and no version bump, and no existing MUST/SHOULD sentence was weakened or diluted. **One blocking finding (F-1)** — the S7.1 completion rule is stated inconsistently in four places, one of them the two-line block this change itself edited — plus one non-blocking wording finding (F-2) and five notes.

F-1 must be closed by an **S4.2 re-entry (4 micro-edits: G7, G8, G9, A13)** before S6.3 can issue a clean report; F-2 may be folded into the same step or explicitly accepted.

### S6.1 done-criteria checklist (this step)

- [x] Check 1 (scope conformance): all 25 rows verified present and faithful; nothing outside the rows changed
- [x] Check 2 (decision fidelity): all 6 ANSWERED questions verified implemented as answered, including the Q-1 / Q-2 / Q-3 / Q-5 / Q-7 specifics named in the task definition
- [x] Check 3 (internal consistency): every enumeration of the status chain, the archive layout, the `main` permission and the S7.1 action set in the 4 files listed with a verdict
- [x] Check 4 (no behavior delta): forbidden-path grep, 0 Python files, no version bump, no machine reader
- [x] Check 5 (nothing weakened): removed-vs-added line analysis and modal-token counts
- [x] Findings classified: **1 blocking (F-1, with the exact 4-edit fix), 1 non-blocking (F-2), 5 notes**
- [x] No S6.2/S6.3/S6.4 work, no PR, no version bump, no `docs/todo/` or `docs/questions/` write, no guidance file edited, no subagent launched, no full test suite re-run

---

## S4.2 re-entry #2 (F-1/F-2) + completeness sweep

Run in the change worktree on top of `9914193` (S6.1 review); working tree clean before (`git status --short` → empty). This is the **fix step the S6.1 verdict required**: close the blocking finding **F-1** (4 micro-edits G7/G8/G9/A13) and the non-blocking finding **F-2** (1 micro-edit, G2a), then run the **completeness sweep** the review asked for, so the next review pass converges instead of finding another sibling statement. Nothing else was touched — no S6.2/S6.3/S6.4 work, no PR, no version bump, no `docs/todo/` or `docs/questions/` write in this worktree, no test/spec/source file.

### The five edits (verbatim before → after; located by text, not by line number)

| Row | File (line at `9914193`) | Before (verbatim) | After (as applied) |
|---|---|---|---|
| **G7** | `.agents/skills/git/SKILL.md:56` (S7.1 **Objective**) | `- **Objective:** After the human merges the PR, verify the merge is reachable from \`origin/main\` (after \`git fetch\`), remove the worktree, and delete the local + remote branches.` | `- **Objective:** After the human merges the PR, verify the merge is reachable from \`origin/main\` (after \`git fetch\`), remove the worktree, delete the local + remote branches, and move the change's TODO and question files to their archive folders.` |
| **G8** | `.agents/skills/git/SKILL.md:58` (S7.1 **Outputs**) | `- **Outputs:** the merge verified as reachable from \`origin/main\` (after \`git fetch\`); the worktree removed; the local + remote branches deleted.` | `- **Outputs:** the merge verified as reachable from \`origin/main\` (after \`git fetch\`); the worktree removed; the local + remote branches deleted; the change's TODO and question files moved to \`docs/todo/archive/\` and \`docs/questions/archive/\` (the question file with its TODO file).` |
| **G9** | `.agents/skills/git/SKILL.md:41` (Todo — the cleanup status-order sentence) | `…\`completed\` when the worktree is removed and the local + remote branches are deleted.` | `…\`completed\` when the worktree is removed, the local + remote branches are deleted, and the two planning records have been moved to the archive folders.` |
| **A13** | `AGENTS.md:443` (Todo Tracking Discipline → "Status orders", Post-merge cleanup bullet) | `  - Post-merge cleanup — \`in_progress\` after the human merges the PR; \`completed\` when the worktree is removed and the local + remote branches are deleted.` | `  - Post-merge cleanup — \`in_progress\` after the human merges the PR; \`completed\` when the worktree is removed, the local + remote branches are deleted, and the two planning records have been moved to the archive folders.` |
| **G2a** | `.agents/skills/git/SKILL.md:65` (planning-commit operation, the arrow chain) | ``…`PREPARING` → `QUESTIONS-ANSWERED` → `READY` → `IN-WORKFLOW` → `WAITING` → `MERGED` → `DROPPED`…`` | ``…`PREPARING` → `QUESTIONS-ANSWERED` → `READY` → `IN-WORKFLOW` → `WAITING` → `MERGED`, or `DROPPED` straight from the value-triage decision…`` |

- Each anchor matched **exactly once** (`grep -cF` → `1` for all five); every replacement is inline text inside an existing bullet/paragraph, so no table, fence or list structure was touched. `git diff` for the guidance files at this step: **`2 files changed, 5 insertions(+), 5 deletions(-)`**.
- **Deciding answers unchanged: Q-7 = (i)** for G7/G8/G9/A13 (the same answer that produced A1/A3/A4/A7/A8/G1/G2/G3/G4/G5/S3), and **Q-3 = (a) + Q-7 = (i)** for G2a. No new decision, no new rule, no gate changed — F-1 and F-2 are statements of rules this change already made, in the places that had not yet been brought in line.
- **G2a is the F-2 fix, applied rather than merely accepted** (the review permitted either): the arrow rendering implied `DROPPED` follows `MERGED`; the new wording matches `specify:169` (`/ **MERGED** / **DROPPED**`, the alternative form) and `AGENTS.md:157-163` (the authoritative moment → status table). `AGENTS.md:157-163` stays the normative mapping.

### Completeness sweep (the reason the review did not converge — run exhaustively this time)

Enumerated **every** place in the four touched guidance files (`AGENTS.md`, `.agents/skills/git/SKILL.md`, `.agents/skills/specify/SKILL.md`, `docs/todo/template.md`) that states (a) the `Status:` chain/vocabulary, (b) the post-merge-cleanup completion rule, or (c) the planning-record paths. Candidate sets produced by three greps over exactly those four files, then classified by reading each hit:

```bash
grep -nE "PREPARING|QUESTIONS-ANSWERED|Status:|Status:\`|\`DROPPED\`|\*\*DROPPED\*\*|IN-WORKFLOW|WAITING.*MERGED|MERGED.*DROPPED" <4 files>   # (a)
grep -nE "worktree is removed|worktree removed|remove the worktree|[Pp]ost-merge cleanup|local \+ remote branches|branches deleted|branches are deleted|verify the merge" <4 files>   # (b)
grep -nE "docs/todo|docs/questions" <4 files>   # (c)  → 27 + 13 + 22 + 3 = 65 raw hits
```

**Totals: 29 statements of rule (a) — 1 updated (G2a), 28 already correct; 17 statements of rule (b) — 4 updated (G7/G8/G9/A13), 7 already correct, 6 deliberately unchanged; 38 statements of rule (c) — 0 updated, all already correct or deliberate non-edits. No sixth edit was required: every remaining under-inclusive statement is a delegating summary the task definition put on the must-stay-untouched list.**

**(a) The `Status:` chain / vocabulary — 29 statements**

| Place | What it states | Verdict |
|---|---|---|
| `AGENTS.md:118` | the `main` permission + chain endpoint `MERGED` **and** `DROPPED` + the archive move | **already correct** (A11) |
| `AGENTS.md:130`, `:131` | artifact table: `main` → the archive path once `DROPPED`/`MERGED` | **already correct** (A1) |
| `AGENTS.md:141`, `:143`, `:145` | the P.1 / P.3 / P.5 done-when cells (`PREPARING`, `QUESTIONS-ANSWERED`, `READY`) | **already correct** — mid-chain, no endpoint claim |
| `AGENTS.md:147` | the **READY gate** (three conditions) | **already correct / must stay untouched** — out-of-scope item, byte-identical |
| `AGENTS.md:151` | the joint **move** at the drop decision and at S7.1 | **already correct** (A3) |
| `AGENTS.md:157-163` | the moment → `Status:` table (7 rows, incl. `MERGED` and `DROPPED`) | **already correct** (A4) — **the authoritative mapping** |
| `AGENTS.md:184` | `Status: DROPPED` + the two records move to the archive | **already correct** (A5) |
| `AGENTS.md:416`, `:417` | archived records = the two live folders are the backlog; an archived change is not resumed | **already correct** (A7/A8) |
| `AGENTS.md:419` | the backlog-status set incl. **DROPPED** | **already correct** (A12) |
| `AGENTS.md:436`, `:647` | the Phase P todo gate and the `PREPARED` state both keyed to `Status: READY` | **already correct** — no chain endpoint; `:647` is the workflow state machine, a different vocabulary |
| `git:12`, `:22` | the planning-commit summary and the Execution Context bullet: through `MERGED` **and** `DROPPED` + the move | **already correct** (G6/G1) |
| **`git:65`** | the arrow-rendered chain | **UPDATED — G2a (F-2)** |
| `git:70`, `:79` | `# every later Status: advance` / `chore(<name>): archive <DROPPED\|MERGED>` | **already correct** — commit-message templates, no chain claim |
| `git:146` | step 5 runs "after the `Status: MERGED` advance" | **already correct** (G4) |
| `git:171` | the Rules direct-to-`main` permission: through `MERGED` **and** `DROPPED` + the move | **already correct** (G5) |
| `specify:56`, `:90`, `:196`, `:212` | the Phase P todo gate, the P.5 handoff, the Outputs and the DoD, all keyed to `READY` | **already correct** (S4/S5) — see note F-7 on `:212` |
| `specify:67` | P.1 done-criteria sets `Status: PREPARING` | **already correct** (S1) |
| `specify:169` | the Rules chain in the **alternative** form `… / **MERGED** / **DROPPED**` + the archive gloss | **already correct** (S2) — the form G2a now matches |
| `docs/todo/template.md:7` | the `Status:` comment vocabulary (7 values incl. `DROPPED`) | **already correct** (T1) |

**(b) The post-merge-cleanup completion rule — 17 statements**

| Place | What it states | Verdict |
|---|---|---|
| **`git:56`** | S7.1 **Objective** — the action set | **UPDATED — G7 (F-1)** |
| **`git:58`** | S7.1 **Outputs** — the action set | **UPDATED — G8 (F-1)** |
| **`git:41`** | the cleanup todo's completion condition | **UPDATED — G9 (F-1)** |
| **`AGENTS.md:443`** | the cleanup todo's completion condition (normative Todo Tracking Discipline) | **UPDATED — A13 (F-1)** |
| `git:59` | S7.1 **Done-criteria** — incl. the two archive moves | **already correct** (G3) |
| `git:123-151` | the **Post-merge cleanup operation** — 5 numbered steps, step 5 = the `git mv` pair + the `archive MERGED` commit | **already correct** (G4) — **the authoritative procedure** |
| `git:73`, `:76` | the move block: "At the drop decision, and at post-merge cleanup (S7.1)" | **already correct** (G2) |
| `AGENTS.md:151`, `:162` | the move at S7.1; `MERGED` is set after post-merge cleanup, then the records move | **already correct** (A3/A4) |
| `specify:171` | the move "(at the drop decision and at post-merge cleanup)" | **already correct** (S3) |
| `docs/todo/template.md:39` | "a dropped TODO moves to `docs/todo/archive/` with its question file" | **already correct** (T2) — the drop moment only, which is what the template is about |
| `AGENTS.md:106` | "verify the merge on `main`, remove the worktree, delete the local and remote change branches" | **deliberately unchanged** — names the git skill's "Post-merge cleanup" operation, which now has step 5 (F-3); on the must-stay-untouched list |
| `AGENTS.md:304` | Workflow Diagram: `S7.1 Verify merge + remove worktree + delete branches ◆` | **deliberately unchanged** — diagram summary, must-stay-untouched (F-3); editing it would widen a fenced ASCII block for no rule change |
| `AGENTS.md:353` | Atomic Steps: `S7.1 Cleanup (verify merge + remove worktree + delete branches)` | **deliberately unchanged** — table summary delegating to the git skill (F-3), must-stay-untouched |
| `AGENTS.md:456`, `:466` | the two todo-set examples: `Post-merge cleanup — verify + remove + delete` | **deliberately unchanged** — illustrative ASCII-aligned examples, must-stay-untouched (F-3) |
| `git:3` | the skill `description:` — "post-merge cleanup (verify merge on main, remove worktree, delete local + remote branches)" | **deliberately unchanged** — the skill's front-matter summary, explicitly must-stay-untouched; it lists the operation's git actions, and the archive move is an orchestrator planning-record action, not a git-worktree action |
| `AGENTS.md:324`, `:425`, `:431`; `git:15`, `:26`, `:45` | name the step/operation without an action set (skill-to-phase row, todo-set rules, When to Use, Execution Context, Atomic Steps intro) | **already correct** — nothing to bring in line |

**(c) The planning-record paths — 38 statements (65 raw path hits, grouped)**

| Place | What it states | Verdict |
|---|---|---|
| `AGENTS.md:118`, `:130-131`, `:151`, `:162-163`, `:416-417` | the two paths + the archive destination + the `main`-only, orchestrator-only rule | **already correct** (A11/A1/A3/A4/A7/A8) |
| `AGENTS.md:98`, `:101`, `:142`, `:165`, `:228`, `:231`, `:234`, `:309`, `:370`, `:381`, `:385`, `:387`, `:391`, `:394`, `:684`, `:686`, `:706` | plain references to the two files/folders (creation, ownership, question-file mechanics) | **already correct** — no path rule, no chain endpoint, no cleanup rule |
| `AGENTS.md:135`, `:683` | "the **only** files the workflow may commit directly to `main`" / the matching Prohibition | **deliberately unchanged** — path-only: `docs/todo/archive/` is inside `docs/todo/`, so the rule already covers the move (P.4 "Deliberate non-edit") |
| `git:12`, `:22`, `:58-59`, `:65`, `:68`, `:77-78`, `:148-149`, `:171-172` | the paths + the `git mv` pair + the primary-worktree / orchestrator-only rule | **already correct** (G6/G1/G8/G3/G2a/G2/G4/G5) |
| `git:111-112` | the `BLOCKED-USER` cleared-gate test reads `docs/questions/<name>.md` (`:113` is the never-idle rule) | **deliberately unchanged** — the test fires only for a **WAITING** change, which is by definition neither dropped nor merged, so it never has to look in the archive (F-4); recorded as a P.4 deliberate non-edit. The whole range `git:111-113` is on the must-stay-untouched list |
| `git:3` | the description's `(docs/todo/, docs/questions/)` | **deliberately unchanged** — must-stay-untouched summary |
| `specify:12`, `:36-37`, `:49`, `:65-66`, `:72-75`, `:80`, `:90`, `:109`, `:119`, `:167`, `:174-175`, `:196`, `:198`, `:217-218` | the templates, the overlap-check inputs, the question-file ownership rule, the Outputs | **already correct** — path references only |
| `specify:171` | the only `specify` path rule that carries the move | **already correct** (S3) |
| `docs/todo/template.md:5`, `:10`, `:39` | "committed directly to `main`", the question-file link, the drop-move note | **already correct / deliberately unchanged** — `:5` is still true as written (F-6); `docs/questions/template.md` is owned by `spec-interview-protocol` and is **not** in this change's file set (0 diff lines) |

**Outside the four files (note, not an edit).** `.agents/skills/review/SKILL.md:103` and `:127` say "perform post-merge cleanup per the git skill (…operation \"Post-merge cleanup\")" — a pure delegation with no action set, so it is already correct. No file outside the four touched guidance files states the cleanup completion rule in a way that contradicts the archive move (`grep -rn "worktree is removed\|Post-merge cleanup" --include="*.md" --include="*.py" --include="*.yml"` over the tree, excluding this record and `docs/todo/`).

### Must-stay-untouched proof (re-verified after the five edits)

Checked by byte-identical string match against `main` (`git show main:<file> | grep -cF -e "<text>"` vs the same grep in the worktree — every pair `1 == 1`):

| Place | State |
|---|---|
| `AGENTS.md:106`, `:304`, `:353`, `:456`, `:466` | **unchanged** — the five delegating summaries (F-3) |
| `.agents/skills/git/SKILL.md:3` | **unchanged** — the skill description |
| `.agents/skills/git/SKILL.md:111-113` | **unchanged** — the `BLOCKED-USER` cleared-gate test (F-4) and the never-idle rule |
| `AGENTS.md:310` (Non-blocking), `:415` (Never idle), `:682` (the idle Prohibition); `git:113` ("Never idle on a gate…") | **unchanged** — the path-scoped wording-hazard grep returns **0** |
| `AGENTS.md:147` (the READY gate) | **unchanged** — not in the diff |
| `docs/questions/template.md` | **unchanged** — `git diff $(git merge-base main HEAD) -- docs/questions/template.md` → **0 lines** (owned by `spec-interview-protocol`) |

### Gate set re-run — the same commands as S5 / the S4.2 re-entry, at this step

| # | Gate | Command (in the worktree) | Base (`77ae870`) | After G7/G8/G9/A13/G2a | Verdict |
|---|---|---|---|---|---|
| G-1 | Lint | `uv run ruff check .` | `All checks passed!` | `All checks passed!` | **PASS** — no delta |
| G-2 | Types | `uv run mypy src/` | `Success: no issues found in 83 source files` | `Success: no issues found in 83 source files` | **PASS** — no delta |
| G-3 | Traceability | `uv run python scripts/check_traceability.py` | `PASS (765 matrix rows, 129 spec IDs, 714 test functions)` | `Traceability: PASS (765 matrix rows, 129 spec IDs, 714 test functions)` | **PASS** — identical counts |
| G-4 | Docs site, strict | `uv run --group docs mkdocs build --strict` | exit 0, no `WARNING:`/`ERROR:` | exit 0, `Documentation built in 2.17 seconds`, `grep -cE "^(WARNING\|ERROR)"` → **0** | **PASS** — no delta |
| G-5 | Diff scope | `git diff --name-only main...HEAD` | 5 paths | the same **5 paths** (4 guidance files + this record) | **PASS** |
| G-6 | Markdown hygiene | `git diff --check main...HEAD` and `git diff --check` | clean | **clean**, exit 0 for both (branch range and worktree) | **PASS** |
| G-7 | Wording hazard (path-scoped) | `git diff -U0 -- AGENTS.md .agents/skills docs/todo/template.md \| grep -cE "^[-+].*(Never idle\|Idle or wait in place\|Non-blocking:)"` | 0 | **0** | **PASS** |
| G-8 | Guidance numstat | `git diff --numstat $(git merge-base main HEAD)` (worktree included) | — | `AGENTS.md` 18/12, `git/SKILL.md` 24/8, `specify/SKILL.md` 9/8, `docs/todo/template.md` 8/1 | **PASS** — 30 rows, 4 files, every hunk maps to a row |
| G-9 | No test / no behavior / no bump | carried from S5 — this step's diff touches only `AGENTS.md`, `.agents/skills/git/SKILL.md` and this record | no `src/`, `tests/`, `docs/specs/`, `pyproject.toml` | **unchanged** — 0 Python files, `pyproject.toml` untouched, `version = "0.6.1"` | **PASS** |

### F-3 … F-7 — no action (each already adjudicated)

- **F-3** (the delegating summaries omit the move): **no action** — they name the git skill's "Post-merge cleanup" operation, which has step 5; the sweep confirms all six (`AGENTS.md:106`/`:304`/`:353`/`:456`/`:466`, `git:3`) are pure delegations, and the task definition put them on the must-stay-untouched list.
- **F-4** (`git:111-113` cleared-gate test unchanged): **no action** — the test applies only to a WAITING change; the rule itself is updated at `AGENTS.md:417`.
- **F-5** (P.1 "Done when" vs the decision's recording moment): **no action** — the parenthetical and A5's ask timing resolve the reading; the enforcement point is the P.4 boundary.
- **F-6** (`docs/todo/template.md:5`, `docs/questions/template.md` do not restate the move): **no action** — `:5` is still true; the question template belongs to `spec-interview-protocol` and is outside this change's file set.
- **F-7** (`specify:212` DoD vs `AGENTS.md:147`): **no action** — not a gate change; `AGENTS.md:147` is byte-identical (proved above).

### S4.2 re-entry #2 done-criteria checklist (this step)

- [x] F-1 closed by exactly the four adjudicated micro-edits (G7/G8/G9/A13), each anchor matched once, wording as the finding specifies
- [x] F-2 closed by G2a — the chain now renders `… → MERGED, or DROPPED straight from the value-triage decision`
- [x] The completeness sweep run over all four touched guidance files for rules (a)/(b)/(c): **29 + 17 + 38 statements classified** — updated / already correct / deliberately unchanged with the reason; **no sixth edit required** (every remaining under-inclusive statement is a delegating summary on the must-stay-untouched list)
- [x] The P.4 Edit index gained **G7/G8/G9/A13/G2a** with their deciding Q-IDs (Q-7 = (i); Q-3 = (a) for G2a) and the lead sentence now reads "22 … **25 with A11/A12/G6** … **30 with G7/G8/G9/A13/G2a**" — the scope contract matches the applied diff
- [x] Must-stay-untouched set re-verified byte-identical (`AGENTS.md:106`/`:304`/`:353`/`:456`/`:466`, `git:3`, `git:111-113`, the never-idle rules, the READY gate, `docs/questions/template.md`)
- [x] Gate set re-run and recorded with base comparison: ruff / mypy / traceability / mkdocs / diff scope / `git diff --check` / wording hazard / numstat — all **PASS**, no delta
- [x] F-3 … F-7 recorded as **no action** with their reasons
- [x] No S6.2/S6.3/S6.4 work, no PR, no version bump, no `docs/todo/` or `docs/questions/` write, no test/spec/source file touched, no subagent launched, no full test suite re-run

---

## S6.2 Traceability + boundaries (Phase 6, review checks 2/3/4/6)

Inputs (bounded, as tasked): the FINAL state of the 4 changed guidance files at `7238395` + this record. NOT the
commit-by-commit diff, and the full test suite was **not** re-run (Phase 5 confirmed the gate clean; the S4.2 re-entry
#2 gate set above re-ran the four DOCS/CHORE gates at this same state).

### Check 1 — traceability for a process change (edit index ⇄ diff ⇄ deciding Q, both directions)

There are no `REQ-XXX`/`AC-XXX` IDs in this change (DOCS/CHORE, no spec), so traceability here = **every applied edit
row maps to a deciding Q-ID, every row has a diff hunk, and every diff hunk has a row.**

**Row count and ID set (measured, not inferred from commit messages).** `docs/verification/value-triage-gate.md:72`
`### Edit index` → **30 rows**: `A1…A13`, `T1`, `T2`, `S1…S5`, `G1…G9`, `G2a`. (The lead sentence at `:413` still
narrates "22 rows … plus the three rows A11/A12/G6" and the later G7/G8/G9/A13/G2a addition — the table itself is the
authority and it has 30. Note T-1, not a finding.)

**Direction A — row → hunk.** Every added line of the diff was extracted
(`git diff main...HEAD -- AGENTS.md .agents/skills docs/todo/template.md | grep '^+'`) and each of the 30 rows was
matched against it as a literal string (`grep -cF`). **All 30 rows matched (≥ 1 added line each); zero rows without a
hunk.**

| Row | added-line hits | Row | added-line hits | Row | added-line hits |
|---|---|---|---|---|---|
| A1 | 1 | A6 | 1 | A11 | 1 |
| A2 | 1 | A7 | 1 | A12 | 1 |
| A3 | 1 | A8 | 1 | A13 | 2 (AGENTS + git, same sentence) |
| A4 | 1 (the `DROPPED` row; the `MERGED` row is the 2nd line of the same hunk) | A9 | 1 | T1 | 1 |
| A5 | 4 (heading + blank + paragraph + blank) | A10 | 1 | T2 | 7 (heading + 5 bullets + blank) |
| S1 | 4 (Objective/Inputs/Outputs/Done-criteria) | S2 | 1 | S3 | 1 |
| S4 | 2 (new bullet + the P.4-output clause) | S5 | 1 | G1 | 1 |
| G2 | 10 (1 changed line `:65` + the 9-line block at `:73-81`) | G3 | 1 | G4 | 7 (step 5 + its code block) |
| G5 | 1 | G6 | 1 | G7 | 1 |
| G8 | 1 | G9 | 2 (AGENTS + git, same sentence) | G2a | 1 (the `:65` chain line) |

**Direction B — hunk → row.** Per-file added/removed line counts match the row attribution exactly:

| File | numstat `main...HEAD` | Attribution arithmetic |
|---|---|---|
| `AGENTS.md` | 18 / 12 | 12 changed lines (A11, A1×2, A2, A3, A4×2, A12, A13, A10, A7, A8) + 6 pure additions (A5 = 4, A6, A9) = **18 added**, 12 removed ✔ |
| `docs/todo/template.md` | 8 / 1 | T1 (1 changed) + T2 (7 added) = **8 added**, 1 removed ✔ |
| `.agents/skills/specify/SKILL.md` | 9 / 8 | S1 (4/4) + S2 (1/1) + S3 (1/1) + S4 (2 added / 1 changed) + S5 (1/1) = **9 added**, 8 removed ✔ |
| `.agents/skills/git/SKILL.md` | 24 / 8 | 8 changed lines (G6, G1, G9, G7, G8, G3, G2/G2a) + 9-line block (G2) + 7-line step-5 block (G4) = **24 added**, 8 removed ✔ |

Total: **59 added content lines** (63 minus the 4 `+++ b/…` headers), every one attributable to a row → **zero hunks
without a row**. Hunk headers confirm the same arithmetic (`git diff -U0`: AGENTS 12 hunks, template 2, specify 6, git
10).

**Direction C — ANSWERED question → realised text.** The question file defines `Q-1…Q-5, Q-7`
(`grep -oE '^## Q-[0-9]+'` → 6 headings; `Q-6` exists nowhere — it was closed as a duplicate), header
`Status: ALL ANSWERED  <!-- 0 PENDING -->`, and `## Late questions (Phases 2–6)` is still the empty template
placeholder. Each answer is realised in the final text:

| Q | Answer (abridged) | Realised as (final text, verified by grep) |
|---|---|---|
| Q-1 | (b) clause inside P.1, one "Backlog value triage" paragraph, no new numbered step | `AGENTS.md:182` `### Backlog value triage`; `AGENTS.md:141` P.1 row carries the clause; `grep -c "P\.0\b"` over the 4 files = **0** (no new step); `specify:45`/`:46` byte-identical (Check 3) |
| Q-2 | (a) per-item stop at P.4; never-idle / WAITING / the Prohibition untouched | `AGENTS.md` A6 ("Every Phase P output … presupposes …"), A9 (Prohibition "Start **P.4** … for a TODO whose `## Value triage` section is empty"), `specify` S4 Done-criteria + S4b P.4 output; the `Never idle.` line and the `Proceed past a BLOCKED-USER step…` prohibition still present once each in `main` and in HEAD |
| Q-3 | (a) add `DROPPED` + the user's folder addition | `DROPPED` in `docs/todo/template.md:7`, `AGENTS.md:163` (the status-table row = the producing moment), `:419`, `specify:169`, `git:12`/`:22`/`:65`/`:79`/`:171` |
| Q-4 | (a) `workflow-docs-nits` → this change → `spec-interview-protocol`; nothing folded in | realised as **non-edits**: `docs/questions/template.md` 0 diff lines, `specify:45`/`:46` untouched, `AGENTS.md:142` byte-identical, `specify:69-75` byte-identical, the `≥ 20` floor byte-identical in both files; `docs/todo/value-triage-gate.md:13` carries `Depends on: workflow-docs-nits` |
| Q-5 | immediate ask, riding the existing P.3 round-trip; recorded **only** in the TODO's `## Value triage` section | `AGENTS.md:184` "a single TODO framed outside a sweep gets its ask **immediately** … no extra ⏸" + "recorded **only in the TODO's `## Value triage` section**, never as a question-file entry"; `docs/todo/template.md` T2 section; `specify` S1/S5 |
| Q-7 | (i) `docs/todo/archive/` + `docs/questions/archive/`, moved at the drop decision and at S7.1, question file always with its TODO file, guidance updated in the same change | `AGENTS.md:130`/`:131`/`:151`/`:162`/`:163`/`:416`; `git:65` + the two `git mv` blocks (`:77-79`, `:148-150`) + `:58`/`:59`; `specify:171`; `template.md:39` |

The edit index's `Decided by` column cites only defined IDs (`Q-1`×8, `Q-2`×4, `Q-3`×10, `Q-5`×4, `Q-7`×18). `Q-4`
cites no row by design — its realisation is a set of non-edits, verified in Check 3.

### Check 2 — no orphaned guidance (rule ⇄ producer, both directions)

**Rule without a producer — none.** Every statement of the new `DROPPED` status and of the archive layout names (or
delegates to a section that names) who performs it and when:

| Statement | Producer named |
|---|---|
| `AGENTS.md:118` (direct-to-`main` permission incl. the archive move) | the orchestrator, via the cross-reference to "Planning records (owner: the orchestrator)" |
| `AGENTS.md:130-131` (artifact table, `→ archive/` once `DROPPED`/`MERGED`) | the trigger column is the moment; the section above it owns the write |
| `AGENTS.md:151` | "the orchestrator … at the drop decision and again at post-merge cleanup (S7.1)" — both moments, both files, `main` only |
| `AGENTS.md:162-163` (status table) | the table's own lead sentence: "The orchestrator advances the TODO `Status:` on `main` at each of these moments, and commits each advance" |
| `AGENTS.md:184` (value triage → `DROPPED` + archive) | "A dropped TODO gets `Status: DROPPED` and its two records move to the archive folders (see …)" |
| `AGENTS.md:416`/`:417`/`:419` | scheduling consequences only — no action claimed; `:419` names the orchestrator as the writer |
| `git:12`/`:22`/`:171` | the operation itself, orchestrator-only, always the primary worktree |
| `git:65` + `:73-81` | the executable `git mv` / `git commit` block |
| `git:58`/`:59` + `:146-151` | S7.1 outputs/done-criteria + step 5 with its own command block |
| `specify:169`/`:171` | the orchestrator owns the `Status:` write and the folder move |
| `docs/todo/template.md:7`/`:39` | template comments — no action claimed; `:39` states the move passively, its producer is `AGENTS.md:151`/`git:65` (F-6 already adjudicated: no action) |

**Producer without a rule — none.** The two `git mv` blocks (`git:77-79`, `git:148-150`) are authorised by
`AGENTS.md:118` + `git:171` (the direct-to-`main` permission now names the archive move) and required by
`AGENTS.md:151`/`:162`/`:163`, `AGENTS.md:419` and the Post-merge-cleanup done-criteria (`git:59`, A13). Nothing
instructs a move or a status that no rule authorises.

**Value-triage rule ⇄ producer — closed in both directions.** Filled by the orchestrator at P.1 (`AGENTS.md:184`,
`specify:64`/`:66`/`:67`); asked by the orchestrator at P.3 (`AGENTS.md:184`, plus the standing rule that a step
subagent never calls `ask_user_question`); enforced at P.4 (`AGENTS.md` A9 Prohibition + `specify:199` P.4 output +
`specify:67` Done-criteria); checked at the READY gate (`specify:212`).

**One gap — the `DROPPED` todo set has no closure rule (finding N-1).** `AGENTS.md:427` "Sets are created at **P.1**
and completed by the **Post-merge cleanup** item" is the only closure rule, and a `DROPPED` change never runs
post-merge cleanup (it never reaches Phase 6). The status is produced and the files move, but nothing says what
happens to that change's todo set.

### Check 3 — boundaries (no drift into another change's territory)

| Boundary | Measurement | Verdict |
|---|---|---|
| `docs/questions/template.md` (owned by `spec-interview-protocol`) | `git diff main...HEAD -- docs/questions/template.md` → **0 lines** | **PASS** |
| `specify/SKILL.md:45`/`:46` (the `workflow-docs-nits` qualifiers) | `git diff -U0 -- .agents/skills/specify/SKILL.md` hunks are `@@ -64,4`, `-169`, `-171`, `-196,0+197`, `-198`, `-211` — **no hunk in 40-50**; final `:45`/`:46` still carry the qualifiers | **PASS** |
| `docs/specs/` (any file) | `git diff main...HEAD -- docs/specs/` → **0 lines**; `docs/specs/template.md` (the `spec-interview-protocol` non-goals slot) untouched | **PASS** |
| CI / `pyproject.toml` / version | `pyproject.toml` diff **0 lines**, `version = "0.6.1"` unchanged (no bump — correct for DOCS/CHORE); no `.github/` path in the diff | **PASS** |
| Diff scope | `git diff --name-only main...HEAD` = 5 paths; the only `docs/todo/`-or-`docs/questions/` path is `docs/todo/template.md` (in scope, T1/T2); no `src/`, `tests/`, `docs/verification/traceability.md`, `userdocs/` | **PASS** |
| `spec-interview-protocol`'s four deltas — **not implemented here** | `Recommended:` field → question template untouched (0 lines); category checklist → `specify:69-75` (P.2) **byte-identical** to `main`; non-goals question → `AGENTS.md:142` **byte-identical**, `docs/specs/template.md` untouched; `≥ 20` floor → `grep -c "≥ 20 questions (FEATURE/CROSS-CUTTING) recorded in"` = 1 in `main` and 1 in HEAD, `Ask at least 20 questions during interrogation` = 1 and 1 | **PASS** |
| `spec-interview-protocol`'s four deltas — **not blocked** | Its own `Depends on: value-triage-gate` (`docs/todo/spec-interview-protocol.md:15`) matches Q-4 = (a); this change edits only the P.1 row (`AGENTS.md:141`, directly above its `:142`) and the P.1 section (`specify:64-67`, above its `:69-75`) → **line shifts only**, no overlapping line; it adds a `## Value triage` section to the **TODO** template, not the question template | **PASS** |

### Check 4 — nothing machine-reads the status vocabulary or the two planning paths

`grep -rnE "PREPARING|QUESTIONS-ANSWERED|IN-WORKFLOW|\bDROPPED\b|\bMERGED\b"` and
`grep -rnE "docs/todo|docs/questions"` over `scripts/`, `.github/workflows/`, `.pre-commit-config.yaml`, `userdocs/`,
`.github/hooks/`, `.github/task-runner/`, `mkdocs.yml`, `pyproject.toml` → **0 hits in every surface**. The three
scripts read only `docs/verification/traceability.md` and `docs/specs/` (`check_traceability.py:129-130`). No workflow
`paths:` filter mentions `docs/todo/**` or `docs/questions/**` (only `docs/specs/**`, `docs/tasks/**`,
`docs/verification/**` in `spec-validation.yml:7-9`/`:17-19`), so the archive move — a `main`-only commit — triggers
no CI job. `mkdocs.yml` has no nav entry for `docs/todo/`/`docs/questions/`, and `mkdocs build --strict` passed at this
state (G-4 above). **PASS — no parser, gate, hook or docs build depends on what this change changes.**

### Check 5 — rebase exposure of the in-flight branches

`git worktree list` → 5 worktrees (primary on `main` at `e1b7706` + 4 change worktrees). Files each in-flight branch
changes vs `main` (`git diff --name-only main...<branch>`):

| Branch | HEAD | Files touched | Overlap with this change's 4 files |
|---|---|---|---|
| `feature/structure-map` | `8eb130b` | `docs/specs/structure-map.md`, `docs/verification/structure-map.md` (spec + record only — Phase 4 not started) | **none today**; its Phase 4 will edit `AGENTS.md` (Tooling / Skill-to-Phase Mapping / Project Structure) → same file, different sections → **line-shift rebase only** |
| `crosscut/structlog-logging` | `f2490a0` | 24 paths, all `tests/` + the task DAG + its record (Phase 3/4 in flight) | **none today**; its Phase 4 will edit `AGENTS.md` "Using the Logging Feature" → **line-shift rebase only** |
| `issue/pytest-randomly` | `249bb32` | **empty diff** (branch still at its base) | none |

Merge simulation (`git merge-tree --write-tree --name-only`, git 2.51): `main` × `chore/value-triage-gate` → exit
**0** (clean); this branch × each of the three → exit **0** (clean) for all three. Staleness vs `main`: structure-map
and pytest-randomly are 3 commits behind their merge-base, structlog-logging 9, this branch 1. **This change creates no
conflict; the only exposure is line shifts in `AGENTS.md` for the two branches that will later edit it.**

### Findings

| ID | Severity | Finding | Evidence | Fix (cost) |
|---|---|---|---|---|
| **B-1** | **blocking** | The archive-move **producer does not run as written**. `git mv` does **not** create the destination directory, and neither `docs/todo/archive/` nor `docs/questions/archive/` exists (`ls` → no such directory; `git ls-tree -r main` → 0 such paths). Measured in a scratch repo: `git mv a.md archive/a.md` → `fatal: renaming 'a.md' failed: No such file or directory`, exit **128** (git 2.51.0.windows.1 — the environment the orchestrator runs in); the identical command succeeds after `mkdir -p archive`. `grep -rn mkdir AGENTS.md .agents/skills docs/todo/template.md` → **0 hits**: no step creates the folders. This also contradicts this record at `:280` ("they are created by the first move"), which the measurement refutes. Consequence: the first drop decision or the first S7.1 cleanup after this change merges fails and the orchestrator has to improvise mid-step. | scratch-repo test (`git init` → `git mv a.md archive/a.md` fails; after `mkdir -p archive` → `R a.md -> archive/a.md`); `git mv -h` offers no directory-creation option | Add `mkdir -p docs/todo/archive docs/questions/archive` as the first command inside both blocks of `.agents/skills/git/SKILL.md` (after `:76` and after `:147`), and correct `:280` of this record to "created by the orchestrator with the first archive commit". **2 lines in an already-touched file.** |
| **N-1** | non-blocking | A `DROPPED` change's **todo set has no closure rule**: `AGENTS.md:427` makes Post-merge cleanup the only completer of a todo set, and a dropped change never reaches it. The status, the ask, the decision and the file move are all produced; the todo-set side is undefined. | `grep -rn "todo set" AGENTS.md` → 8 hits, none about closure on drop; `AGENTS.md:427` ("completed by the **Post-merge cleanup** item"), `:445` | One clause — in the `DROPPED` status row (`AGENTS.md:163`) or the "Todo sets" bullet (`:418`): a `DROPPED` change's todo set is closed at the drop decision (no Post-merge cleanup item runs). |
| **T-1** | note | The edit-index lead sentence (`:413`) still narrates "22 rows … plus the three rows A11/A12/G6"; the table itself has **30** rows and is complete. The table is the authority. | row extraction from `:72` → exactly 30 IDs (`A1…A13 T1 T2 S1…S5 G1…G9 G2a`) | Cosmetic — fold into the S6.3 report wording if that step touches it. |
| **T-2** | note | `docs/questions/archive-AI_Questions.md` is the **only** path in `main` matching the string `docs/questions/archive` (the retired central file — a prefix collision with the new folder name). `AGENTS.md:394` already states it stays where it is and must not be moved; no machine reader globs it (Check 4). | `git ls-tree -r --name-only main \| grep docs/questions/archive` → exactly that 1 path | none — already disambiguated in the text. |
| **T-3** | note | Boundary with `spec-interview-protocol`'s ask mechanics: the value-triage ask is deliberately **not** a question-file entry, so it neither counts toward P.2's `≥ 20` floor nor would carry that change's planned `Recommended:` field. No conflict (the floor counts question-file entries; the ask is an orchestrator P.3 table), and the floor is byte-identical. | `grep -c "never as a question-file entry"` → `AGENTS.md` 1, `specify` 0 (the rule is normative-side only, which is where the ask lives) | none — record the boundary so the later change does not "fix" it. |
| **T-4** | note | The worktree's copy of `docs/todo/value-triage-gate.md:7` still reads `Status: QUESTIONS-ANSWERED` with a stale "P.4 … still to r…" comment; `main` advanced it to `READY` at `e1b7706`. Orchestrator-owned planning record — correctly **not** in this diff. | `grep -n "Status:\|Depends on" docs/todo/value-triage-gate.md` | orchestrator advances the record on `main` (not this change's file). |

### S6.2 done-criteria checklist (this step)

- [x] Check 1: the 30-row edit index verified against `git diff main...HEAD` in **both** directions (0 rows without a hunk, 0 hunks without a row, per-file numstat arithmetic reconciled), and against the 6 ANSWERED questions — each realised in the final text, Q-4 realised as non-edits
- [x] Check 2: rule ⇄ producer verified in both directions for `DROPPED`, the archive layout and the value-triage gate (11 rule statements mapped to a producer; 2 producers mapped to a rule); one gap found (N-1)
- [x] Check 3: all boundaries measured — question template 0 lines, `specify:45/46` no hunk, `docs/specs/` 0 lines, CI/pyproject/version untouched, diff scope 5 paths, and `spec-interview-protocol`'s four deltas neither implemented nor blocked (4 byte-identical anchors proved)
- [x] Check 4: 0 machine readers of the status vocabulary or the two planning paths across 8 surfaces; no CI `paths:` filter, no mkdocs nav entry
- [x] Check 5: rebase exposure measured for all three in-flight branches — no overlap today, `git merge-tree` clean against `main` and against each of them, line-shift-only exposure later
- [x] Full test suite NOT re-run (Phase 5 gate already recorded); no commit-by-commit review; no PR; no version bump; no `docs/todo/` or `docs/questions/` write; no subagent launched; no `ask_user_question`

---

## S4.2 re-entry #3 (B-1, N-1, T-1)

Run in the change worktree on top of `81a389b` (S6.2 traceability + boundaries); working tree clean before (`git status --short` → empty). This is the fix step the S6.2 findings required: close the **blocking** finding **B-1** (the archive-move producer does not run as written) and, in the same pass, **N-1** (no closure rule for a `DROPPED` change's todo set) and **T-1** (the edit-index lead sentence narrates 22 rows while the table has 30). Nothing else — no S6.3/S6.4 work, no PR, no version bump, no `docs/todo/` or `docs/questions/` write in this worktree, no test/spec/source file, no full test suite re-run.

### The five edits (verbatim before → after; located by text, not by line number)

| Row | File (line at `81a389b`) | Before (verbatim) | After (as applied) |
|---|---|---|---|
| **G10** | `.agents/skills/git/SKILL.md:73-80` (planning-commit operation, the archive-move block) | `At the drop decision, and at post-merge cleanup (S7.1), the orchestrator moves the two records to the archive folders **together**:` — then the fenced block whose first command is `git mv docs/todo/<name>.md docs/todo/archive/<name>.md` | intro gains the reason clause — `…to the archive folders **together** (\`git mv\` does **not** create the destination directory, so the folders are created first):` — and the block's first command line is now `mkdir -p docs/todo/archive docs/questions/archive` |
| **G11** | `.agents/skills/git/SKILL.md:146-151` (Post-merge cleanup, step 5 block) | `5. Move the planning records to the archive (from the primary worktree, after the \`Status: MERGED\` advance):` — then the fenced block starting at `git mv docs/todo/<name>.md …` | `5. Move the planning records to the archive (from the primary worktree, after the \`Status: MERGED\` advance; \`mkdir -p\` first — \`git mv\` does not create the destination directory):` and the block's first line is now `   mkdir -p docs/todo/archive docs/questions/archive` |
| **A14** | `AGENTS.md:425` (Todo Tracking Discipline, "One todo set per change", the closure sentence) | `Sets are created at **P.1** and completed by the **Post-merge cleanup** item.` | `Sets are created at **P.1** and completed by the **Post-merge cleanup** item; a **\`DROPPED\`** change's set is closed by the orchestrator at the drop decision (no Post-merge cleanup item runs for it).` — one clause, the section is not restructured |
| **V1** | this record `:280` (the G2 row's archive-folder bullet) | `- The \`archive/\` subdirectories do not exist yet (\`ls docs/todo/archive\` → no such directory); they are created by the first move, on \`main\`, by the orchestrator — **not** by this PR (see "Follow-up actions").` | the bullet now reads "the **move step creates them** with \`mkdir -p docs/todo/archive docs/questions/archive\` before the \`git mv\` pair…", followed by an explicitly labelled **Correction (S4.2 re-entry #3, S6.2 finding B-1 — row V1)** bullet quoting the false claim and the measurement — the earlier record is corrected, not silently rewritten |
| **V2** | this record `:413` (the "Reverse: each edit row is decided by an answer" lead sentence) | `The **Edit index** table above carries a \`Decided by\` column for all 22 rows (A1–A10, T1–T2, S1–S5, G1–G5) — plus the three rows A11/A12/G6 added at the S4.2 re-entry, …` | the sentence now states the count the table actually has — **35 rows: A1–A14, T1–T2, S1–S5, G1–G11, G2a, V1–V2** — with the growth history kept as a parenthetical (`22 → 25 → 30 → 35`) and the note that the table is the authority; the two designed non-Q exceptions (V1 cites Q-7 = (i), V2 cites no Q) are named |

- Each anchor matched **exactly once** (`grep -cF` → `1` for G10/G11/A14/V1/V2); every replacement is inline text inside an existing paragraph, list item, table row or fenced block — no fence, table or list structure was re-flowed. `git diff --numstat HEAD` for this step: `.agents/skills/git/SKILL.md` **4/2**, `AGENTS.md` **1/1** (plus this record's own growth).
- **Deciding answers unchanged.** G10/G11 and V1 follow from **Q-7 = (i)** — the answer that already produced A1/A3/A4/A7/A8/S3/G1/G2/G3/G4/G5/G7/G8/G9 — and A14 from **Q-3 = (a)** (the `DROPPED` status already exists; N-1 only states what happens to its todo set). **V2 cites no Q**: it is a record-consistency fix (T-1) that touches no guidance file. No new decision, no new rule, no gate changed.
- **B-1 is a correctness fix to a command the guidance tells the orchestrator to run**, not a wording change: as written, the first drop decision or the first S7.1 cleanup after this change merges would fail mid-step. The two `mkdir -p` lines are the whole fix (2 lines in an already-touched file), plus the reason clause so a later reader does not delete them as redundant.
- **A14 vs the re-entry #2 sweep — no contradiction.** The re-entry #2 completeness sweep classified `AGENTS.md:425` under rule **(b)** (the post-merge-cleanup *action set*) as "already correct — nothing to bring in line". That verdict stands: the sentence's cleanup clause is untouched. A14 closes a **different** rule the sweep did not enumerate — todo-set **closure** for a change that never reaches Post-merge cleanup (N-1). `AGENTS.md:418` ("Todo sets", the Multi-change-scheduling bullet) is likewise unchanged: the normative closure rule lives in the Todo Tracking Discipline, which is where the sweep's `:425` row points.

### B-1 proof — the fixed sequence run in a throwaway repo (the guidance must be executable, not plausible)

`git init` in a fresh `mktemp -d` repo, two planning records committed, then the exact command sequence as the guidance now reads (git `2.51.0.windows.1`, the environment the orchestrator runs in; the repo was deleted afterwards, `rm -rf` exit 0):

| # | Command | Exit | Output |
|---|---|---|---|
| 1 | `git init -q .` | **0** | — |
| 2 | `git add -A && git commit -qm init` (`docs/todo/demo.md`, `docs/questions/demo.md`) | **0** | — |
| 3 | `git mv docs/todo/demo.md docs/todo/archive/demo.md` — **as the guidance read before B-1** | **128** | `fatal: renaming 'docs/todo/demo.md' failed: No such file or directory` |
| 4 | `git mv docs/questions/demo.md docs/questions/archive/demo.md` — same | **128** | `fatal: renaming 'docs/questions/demo.md' failed: No such file or directory` |
| 5 | `mkdir -p docs/todo/archive docs/questions/archive` — **the G10/G11 line** | **0** | — |
| 6 | `git mv docs/todo/demo.md docs/todo/archive/demo.md` | **0** | — |
| 7 | `git mv docs/questions/demo.md docs/questions/archive/demo.md` | **0** | — |
| 8 | `git commit -qm "chore(demo): archive MERGED"` | **0** | — |
| 9 | `git status --short` | **0** | empty (clean tree) |
| 10 | `git show --stat --oneline HEAD` | **0** | `docs/questions/{ => archive}/demo.md \| 0`, `docs/todo/{ => archive}/demo.md \| 0`, `2 files changed, 0 insertions(+), 0 deletions(-)` |
| 11 | `git ls-files` | **0** | `docs/questions/archive/demo.md`, `docs/todo/archive/demo.md` |

**Verdict: B-1 is real (steps 3–4 fail, exit 128) and B-1 is fixed (steps 5–11 all exit 0, both records end up in their archive folder, tree clean).** The same sequence is what both guidance blocks now state, so the drop-decision move and the S7.1 move are executable on first run.

### Scope contract updated (the edit index and its two count statements)

- The **Edit index** gained **G10, G11, A14, V1, V2** with their deciding Q-IDs (Q-7 = (i) for G10/G11/V1, Q-3 = (a) for A14, none for V2 — labelled a record-consistency fix). The table now has **35 rows**: `A1…A14`, `T1`, `T2`, `S1…S5`, `G1…G11`, `G2a`, `V1`, `V2`.
- The **Scope** lead sentence (`:61`) now reads "…**30 with G7/G8/G9/A13/G2a** … and **35 with G10/G11/A14/V1/V2**, the five rows added at the **S4.2 re-entry #3** after the S6.2 findings B-1/N-1/T-1", and states that the guidance file set stays at **4 files** because **V1/V2 are corrections inside this record** — the only two rows that are not guidance text.
- The **Reverse-direction** lead sentence (`:413`, the T-1 fix = **V2**) now states the same 35-row count and ID set, with the growth history parenthetical, so the two places that narrate the count agree with the table (T-1 closed).
- Historical sections are **not** rewritten: the "all 22 rows applied" statements in the S4.2 / S5 records stay as the dated gate record of those steps (AGENTS.md traceability convention — a dated record is a legal record of a past gate).

### Gate set re-run — the same commands as S5 / the two earlier re-entries, at this step

| # | Gate | Command (in the worktree) | Base (`77ae870`) | After G10/G11/A14/V1/V2 | Verdict |
|---|---|---|---|---|---|
| G-1 | Lint | `uv run ruff check .` | `All checks passed!` | `All checks passed!` | **PASS** — no delta |
| G-2 | Types | `uv run mypy src/` | `Success: no issues found in 83 source files` | `Success: no issues found in 83 source files` | **PASS** — no delta |
| G-3 | Traceability | `uv run python scripts/check_traceability.py` | `PASS (765 matrix rows, 129 spec IDs, 714 test functions)` | `Traceability: PASS (765 matrix rows, 129 spec IDs, 714 test functions)` | **PASS** — identical counts |
| G-4 | Docs site, strict | `uv run --group docs mkdocs build --strict` | exit 0, no `WARNING:`/`ERROR:` | exit **0**, `Documentation built in 1.55 seconds`, `grep -cE "^(WARNING\|ERROR)"` → **0** | **PASS** — no delta |
| G-5 | Diff scope | `git diff --name-only main...HEAD` | 5 paths | the same **5 paths** (4 guidance files + this record) | **PASS** |
| G-6 | Markdown hygiene | `git diff --check main...HEAD` and `git diff --check` | clean | **clean**, exit 0 for both (branch range and worktree) | **PASS** |
| G-7 | Wording hazard (path-scoped) | `git diff -U0 -- AGENTS.md .agents/skills docs/todo/template.md \| grep -cE "^[-+].*(Never idle\|Idle or wait in place\|Non-blocking:)"` | 0 | **0** (and **0** over the whole branch range `$(git merge-base main HEAD)`) | **PASS** |
| G-8 | Guidance numstat | `git diff --numstat $(git merge-base main HEAD)` (worktree included) | — | `AGENTS.md` **19/13** (was 18/12 — A14 is 1 changed line), `git/SKILL.md` **26/8** (was 24/8 — G10/G11 add 2 lines; the two intro clauses sit on lines that are themselves new vs the merge-base, so the removed count does not grow), `specify/SKILL.md` **9/8** (unchanged), `docs/todo/template.md` **8/1** (unchanged) | **PASS** — 35 rows, 4 guidance files, every hunk maps to a row |
| G-9 | No test / no behavior / no bump | carried from S5 — this step's diff touches only `.agents/skills/git/SKILL.md`, `AGENTS.md` and this record | no `src/`, `tests/`, `docs/specs/`, `pyproject.toml` | **unchanged** — 0 Python files, `pyproject.toml` untouched, `version = "0.6.1"` | **PASS** |

### Must-stay-untouched set re-verified after the three guidance edits

Checked by byte-identical string match against `main` (`git show main:<file> \| grep -cF -- "<text>"` vs the same grep in the worktree — every pair `1 == 1`), plus whole-line `cmp` where the line number is stable:

| Place | State |
|---|---|
| `AGENTS.md:106`, `:304`, `:353`, `:456`, `:466` | **unchanged** — the five delegating cleanup summaries (F-3); the `:456`/`:466` example rows still match `main` (2 == 2) |
| `.agents/skills/git/SKILL.md:3` (the skill `description:`) | **unchanged** — `cmp` of line 3 vs `main` → identical |
| `.agents/skills/git/SKILL.md` — the `BLOCKED-USER` cleared-gate test, the "Do NOT rely on the local \`main\` ref, which may lag; \`git fetch\` first." line, and the "Never idle on a gate…" line | **unchanged** — each present exactly once, 1 == 1 (F-4) |
| `AGENTS.md:147` (the READY gate) | **unchanged** — `cmp` of the line vs `main` → identical |
| `AGENTS.md:310` (Non-blocking), `:415` (Never idle), `:682` (the idle Prohibition), `:418` (the "Todo sets" bullet) | **unchanged** — 1 == 1 each; **A14 is confined to `:425`** |
| `docs/questions/template.md` | **unchanged** — `git diff main...HEAD` and `git diff` → **0 lines** (owned by `spec-interview-protocol`) |

### S4.2 re-entry #3 done-criteria checklist (this step)

- [x] **B-1 closed** — `mkdir -p docs/todo/archive docs/questions/archive` added as its own fenced `bash` line before the `git mv` pair in **both** blocks (G10 planning-commit operation, G11 S7.1 step 5), each with a short reason clause so the line is not later deleted as redundant
- [x] **B-1 proved fixed, not merely plausible** — the fixed sequence run in a throwaway `git init` repo: the pre-fix form fails (exit **128**, both moves), the post-fix form exits **0** end to end, both records land in their archive folder, tree clean; recorded above with per-command exit codes
- [x] **B-1's record contradiction corrected (V1)** — `:280` no longer claims the folders "are created by the first move"; the correction is labelled as a correction of the earlier record (original wording quoted, measurement cited), not a silent rewrite
- [x] **N-1 closed (A14)** — one clause added where the todo-set lifecycle is stated: a `DROPPED` change's set is closed by the orchestrator at the drop decision; the section is not restructured and `AGENTS.md:418` is untouched
- [x] **T-1 closed (V2)** — the lead sentence now states the final count (35 rows, full ID set) with the growth history as a parenthetical; the Scope lead sentence and the Reverse-direction lead sentence now agree with the table
- [x] Edit index gained **G10/G11/A14/V1/V2** with their deciding Q-IDs (Q-7 = (i) for G10/G11/V1, Q-3 = (a) for A14, none for V2 — explicitly a record-consistency fix, no guidance file) and the count updated in both places
- [x] Gate set re-run and recorded with base comparison: ruff / mypy / traceability / mkdocs / diff scope / `git diff --check` / wording hazard / numstat — all **PASS**, no delta
- [x] Must-stay-untouched set re-verified byte-identical (`AGENTS.md:106`/`:147`/`:304`/`:310`/`:353`/`:415`/`:418`/`:456`/`:466`/`:682`, `git:3`, the cleared-gate test lines, `docs/questions/template.md` 0 lines)
- [x] No S6.3/S6.4 work, no PR, no version bump, no `docs/todo/` or `docs/questions/` write, no test/spec/source file touched, no subagent launched, no `ask_user_question`, no full test suite re-run
