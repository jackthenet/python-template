# Questions: value-triage-gate

One question file per change, created at **P.1 Frame** from this template and named `value-triage-gate.md`. It replaces the retired central `AI_Questions.md` (archived at `docs/questions/archive-AI_Questions.md`).

- **Change:** value-triage-gate (DOCS/CHORE)
- **TODO file:** `docs/todo/value-triage-gate.md`
- **Spec:** n/a
- **Opened:** 2026-10-03
- **Status:** ALL ANSWERED  <!-- 0 PENDING -->
- **Answer rounds:** 4 (2026-10-04: Q-1, Q-2, Q-3, Q-4, Q-5, Q-7)

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

**5 questions need user input (Q-1..Q-5, one `BLOCKED-USER` batch); 15 interrogation points were closed from repository evidence** and are recorded below with `file:line` evidence, together with a "For P.4" section carrying the settled, line-cited edits. DOCS/CHORE carries no ≥ 20-question floor (`AGENTS.md:142` parenthesises it "(FEATURE/CROSS-CUTTING)"; `specify/SKILL.md:74` sits under `## Atomic Steps (FEATURE / CROSS-CUTTING)`). **Classification check: DOCS/CHORE holds** (see "Classification"), with one wording hazard that belongs in Phase 6 review, not a reclassification.

## Q-1 — is the triage a new numbered Phase P step (P.0), or a mandatory clause inside P.1 Frame?

- **Step:** P.2 Interrogate
- **Why needed:** the TODO's In-scope line commits to "One new **orchestrator** step in Phase P, working name **P.0 Value triage** … exact placement — a standalone step vs. a P.1 sub-item — is decided at P.2". The two placements differ by ~7 vs ~13 coordinated `AGENTS.md`/skill edits, and the standalone-step option collides with three existing rules (todo-set creation, the `Status:` vocabulary, the READY gate). This is a protocol-shape decision, not a wording choice, so the user makes it.
- **Context:** the cost table is in "Placement cost analysis" below. The decisive facts: Phase P is defined **per change** (`AGENTS.md:126` "Preparation artifacts (**per change**)", `:221` "PHASE P PREPARE (**per change**, before the workflow …)"), while the rule text describes a **backlog-wide sweep** over several TODOs (`docs/todo/value-triage-gate.md:57` "one table over the backlog, one ask"); a P.0 runs **before** the TODO/question file exists (`AGENTS.md:141` P.1 creates them), so it has no record to write into, no `Status:` to set (`:157` the table starts at `P.1 Frame → PREPARING`), and no todo item ("Sets are created at **P.1**", `:418`; "**Creating the todo set (P.1).** … create one todo item per workflow step the change type executes", `:420`). All five triages that were actually performed are recorded **inside the P.1 record** — in the TODO body plus the P.1 Prep-log row (`docs/todo/docs-path-ci-trigger.md:35-39` + `:47`, `split-archived-qa.md:35-39` + `:47`, `workflow-docs-nits.md:40-44` + `:52`, `remove-spec-tdd-driver.md:39-43` + `:54`) — i.e. the practice as performed **is** a P.1 sub-item, not a separate step.
- **Question:** which placement? **(a)** a new numbered step **P.0 Value triage** in the Phase P atomic-steps table (`AGENTS.md:139-145`) — matches the TODO's current wording, but forces ~13 coordinated edits and needs new rules for the todo set (`:418`/`:420`), the status vocabulary (`:155-162`) and possibly the READY gate (`:147`, which the TODO puts out of scope); **(b)** a mandatory **Value triage clause inside P.1 Frame** + one short "Backlog value triage" paragraph under Phase P (`AGENTS.md:177-179`) — ~6 edits, no rule collision, and it matches the five records the practice actually produced *(recommended: smallest diff, no new machinery, and it also removes the `specify/SKILL.md:45` collision with `workflow-docs-nits` — see Q-4)*; **(c)** a named pre-Phase-P gate documented in prose but outside the `P.x` numbering (a middle ground: one new subsection, no table/diagram/todo changes).
- **Answer:** **(b) — a mandatory Value triage clause inside P.1 Frame**, plus one short "Backlog value triage" paragraph under Phase P. No new numbered step, no Phase P table/diagram/todo-set edits, and `specify/SKILL.md:45`/`:46` are out of scope (the `workflow-docs-nits` collision dissolves).
- **Date:** 2026-10-04
- **Status:** ANSWERED
- **Incorporated:** yes — the TODO's In-scope first bullet is rewritten to the P.1-clause form

## Q-2 — "Do not implement anything until I answer": does the triage stop the whole agent, or only the triaged items?

- **Step:** P.2 Interrogate
- **Why needed:** the verbatim rule text ends "Do not implement anything until I answer." Read literally that is a global stop, which contradicts five live rules that the TODO explicitly keeps out of scope. The wording decides whether this change silently inverts the scheduling protocol — the TODO's own "Constraints and risks" flags it as "a wording trap to catch in review".
- **Context:** `AGENTS.md:124` "**None of them stops the agent** — a late question puts the change in WAITING and the agent switches to another prepared change"; `:219` legend "**⏸** = user input (the **change** stops until answered)"; `:305` "**Non-blocking:** a change that reaches a ⏸ gate goes **WAITING** and the orchestrator immediately works on another READY change … the workflow never idles"; `:386` "**Change stop, not workflow stop**"; `:406` "**Never idle.** … It stops only when every in-flight change is WAITING **and** no prepared change is READY"; Prohibition `:674` "**Idle or wait in place** on a human gate … while another change is READY". Today 2 of 16 backlog items are WAITING and 13 are PREPARING — a literal global stop would forbid exactly the work the backlog needs.
- **Question:** scope the hard rule to the triaged items or to the agent? **(a)** per-item: no TODO may pass **P.4** (create its branch/worktree) until *its own* Value triage decision is recorded; already-decided and READY changes keep running, so "never idle" is untouched *(recommended — consistent with `:124`/`:305`/`:386`/`:406`/`:674`, and it still guarantees nothing is implemented before the user answers **that** item)*; **(b)** literal global stop — then this change must also amend `AGENTS.md:305`, `:406` and `:674`, which its Out-of-scope currently forbids (that would be a scheduling-protocol change, i.e. a reclassification trigger); **(c)** another formulation.
- **Answer:** **(a) — per-item stop at P.4.** No TODO may pass **P.4** (create its branch/worktree) until its own Value triage decision is recorded; already-decided and READY changes keep running, so "never idle" (`AGENTS.md:406`), the WAITING rules (`:124`, `:305`, `:386`) and the Prohibition at `:674` stay untouched — no reclassification trigger. It still guarantees nothing is implemented before the user answers **that** item.
- **Date:** 2026-10-04
- **Status:** ANSWERED
- **Incorporated:** yes — the hard rule in the TODO's In scope is reworded to the P.4 gate

## Q-3 — how is a **dropped** TODO recorded: a new `DROPPED` status, or the TODO body only?

- **Step:** P.2 Interrogate
- **Why needed:** the TODO's In scope says the drop decision "stays in the TODO file, like the two 1/5 records do today", but the `Status:` vocabulary has no value for a dead item, so after this change a dropped backlog item is indistinguishable from a live one to anything that scans the backlog — including the orchestrator's own "Ready selection order".
- **Context:** the vocabulary is `PREPARING | QUESTIONS-ANSWERED | READY | IN-WORKFLOW | WAITING | MERGED` (`AGENTS.md:155-162`, `docs/todo/template.md:7`, `specify/SKILL.md:169`, `.agents/skills/git/SKILL.md:65`). **Nothing machine-reads it**: `grep -rn "PREPARING|QUESTIONS-ANSWERED" scripts/ .github/workflows/` → no match, and `scripts/check_traceability.py` scans only `docs/specs/`, `docs/verification/traceability.md` and `tests/`. Observed state today: the two 1/5 items are still `Status: PREPARING` (`docs/todo/docs-path-ci-trigger.md:7`, `docs/todo/split-archived-qa.md:7`) with their drop recorded only in the body (`:35-39` in both) and the P.1 Prep-log row (`:47` in both); 13 of 16 backlog TODOs are `PREPARING`; "DROPPED" appears in the repo only as prose in `docs/todo/remove-spec-tdd-driver.md:55` ("split-archived-qa DROPPED 1/5, docs-path-ci-trigger DROPPED 1/5 …").
- **Question:** **(a)** add `DROPPED` to the vocabulary — one row in the `AGENTS.md:155-162` table ("when the user's value-triage decision is **drop**"), one value in the `docs/todo/template.md:7` comment, one mention in `git/SKILL.md:65`; a dropped item stays on disk with its reason and its TODO file never enters the workflow *(recommended: 3 small edits, no machine reader to break, and it makes the backlog scannable)*; **(b)** body-only, exactly as the two 1/5 records do today (smallest diff, but a dead item keeps `Status: PREPARING` forever and the orchestrator must read every body to find it); **(c)** body-only plus a `DROPPED` marker inside the `## Value triage` section only (no vocabulary change).
- **Answer:** **(a) — add `DROPPED` to the vocabulary**, plus the user's addition: *"how about we also move them to a different folder, same for merged"* — a dead item (dropped, or merged) should leave the live backlog folder rather than sit in it with a status flag. The folder layout, the moment of the move, and whether `docs/questions/<name>.md` moves with it are **Q-7**.
- **Date:** 2026-10-04
- **Status:** ANSWERED
- **Incorporated:** yes — scope grows from 3 edits to 3 edits + the archive-location rule (Q-7); the two items dropped on 2026-10-04 (`docs-path-ci-trigger`, `split-archived-qa`) are the first candidates for the move

## Q-4 — sequencing/ownership against `workflow-docs-nits` (its Q-3 is the same decision) and `spec-interview-protocol`

- **Step:** P.2 Interrogate
- **Why needed:** two other backlog items plan edits to the same files, and one of them (`workflow-docs-nits`, now **WAITING** with 3 open questions) already asks the user the reciprocal question — `docs/questions/workflow-docs-nits.md` Q-3: "collision with `value-triage-gate` on `specify/SKILL.md:45` and `docs/todo/template.md`: sequence or fold?" The answer decides whether **this** change's scope grows (it absorbs their items (a)+(b)) or stays as drafted, so it must be answered for this change too. The orchestrator should ask it **once** and record it in both files.
- **Context:** `workflow-docs-nits` In scope (`docs/todo/workflow-docs-nits.md:23-24`): `docs/todo/template.md:44` (the Prep-log `P.5 Self-consistency` row) and `specify/SKILL.md:14`, `:45`, `:46`. This change touches `docs/todo/template.md` (new `## Value triage` section between `:32` and `:34` — a **different line**, mergeable) and, **if Q-1 = (a)**, `specify/SKILL.md:45`/`:46` (the step-order and ownership lists) — **the same lines** as their item (b) → a real conflict. **If Q-1 = (b) or (c), this change does not touch `:45`/`:46` at all** (P.1 is not in those two lists; `:46` names P.1 only as an orchestrator step), which dissolves the collision. Second collision surface: if Q-3 = (a), this change adds a row to the `AGENTS.md:155-162` status table — the exact table `workflow-docs-nits` Q-1 (b) might also add a row to. Third: `spec-interview-protocol` declares the order itself — `docs/todo/spec-interview-protocol.md:13` "**Depends on:** `value-triage-gate` (recommended: land **after** it — both edit the same P.2/P.3 guidance surface, and the value-triage step is inserted before interrogation)", `:60` "land it second, or land them as one change", `:51` "Value triage placement (owned by `docs/todo/value-triage-gate.md`)".
- **Question:** how do the three land? **(a)** `workflow-docs-nits` first (its guaranteed core is a 4-line qualifier diff in the same two files), then this change builds on it *(matches "easiest first", `AGENTS.md:422`)*; **(b)** drop `workflow-docs-nits` items (a)+(b) and **fold them into this change's PR** — one change instead of two touching the same lines, so this change's scope grows by the two qualifier edits (still DOCS/CHORE); **(c)** this change first with Q-1 = (b)/(c) so it never touches `specify/SKILL.md:45`/`:46`, leaving `workflow-docs-nits` conflict-free *(note: `workflow-docs-nits` is WAITING on its own 3 questions, so (a) cannot run before those are answered)*. Also confirm: `spec-interview-protocol` stays **after** this change (its own TODO says so) and must not re-open the value-triage placement.
- **Answer:** **(a) — `workflow-docs-nits` first, then this change, then `spec-interview-protocol`** (confirmed as the backlog-wide landing order, 2026-10-04). `workflow-docs-nits` items (a)+(b) are **not** folded here; this change builds on their qualifiers, so it gains `Depends on: workflow-docs-nits`. `spec-interview-protocol` stays after this change and must not re-open the value-triage placement.
- **Date:** 2026-10-04
- **Status:** ANSWERED
- **Incorporated:** yes — recorded as `Depends on: workflow-docs-nits` in the TODO; the collision note is settled (this change lands second)

## Q-5 — how is the triage ask packaged and where is it recorded?

- **Step:** P.2 Interrogate
- **Why needed:** the rule text says "Present the results as a table (ID | TODO | score | recommendation | reason), then ask me which to implement, merge, or drop" — a table implies a multi-item sweep, but TODOs are framed one at a time (P.1), and the repo has two contradictory precedents for where the ask/decision is recorded. Without a rule, the next agent either adds a new ⏸ round-trip per change or silently skips the ask.
- **Context:** the batching rule already allows many rounds — `AGENTS.md:143` "present the batch (**≤ 4 per `ask_user_question` round**, most blocking first)", and `docs/workflow/PROBLEMS.md:96` (P-1) records the observed cost of one batch: "28 questions … 7 batches + 1 re-ask". So "one batched ask" = one **batch**, not one round: 16 backlog rows → up to 4 rounds, legal today (closed point 6). Recording, however, is contradictory: Obligation 14 (`AGENTS.md:698") says "Record **every** `BLOCKED-USER` question in the change's question file", but the two dropped items' question files are **untouched templates** (`docs/questions/docs-path-ci-trigger.md` and `docs/questions/split-archived-qa.md` still carry the literal `<the interrogation batch — at least 20 questions for FEATURE/CROSS-CUTTING>` placeholder) while the decision lives only in the TODO body; the two items the user did decide record it in the TODO's Value triage section (`track-python-skill.md:43` "**Decision:** user chose **implement**", `remove-spec-tdd-driver.md:43` + Prep-log row `:54`).
- **Question:** two parts. **(i) Packaging:** when a single TODO is framed outside a sweep, is the ask issued **immediately** as a one-row table riding the change's existing P.3 round-trip (no extra ⏸, recommended), or **deferred** to the next backlog sweep (the item waits, one round-trip per sweep)? **(ii) Recording:** is the triage ask + decision recorded **only in the TODO's `## Value triage` section** (the precedent for all five items, and it keeps a dropped item's question file clean), or **also as a question-file entry** per Obligation 14 (protocol-consistent, but then a dropped item has a question file with an `ANSWERED` entry for a change that will never run)?
- **Answer:** **immediate + TODO section only.** (i) A single TODO framed outside a sweep gets its ask **immediately**, as a one-row table riding that change's existing P.3 round-trip — no extra ⏸. (ii) The ask and the decision are recorded **only in the TODO's `## Value triage` section** (the precedent of all five items); no question-file entry, so a dropped item's question file stays clean.
- **Date:** 2026-10-04
- **Status:** ANSWERED
- **Incorporated:** yes — recorded in the TODO's In scope; the protocol-consistency concern is closed by the Q-2 (a) per-item gate

### Placement cost analysis (the evidence behind Q-1)

What a **new numbered P.0 step** forces, location by location, with the current text quoted:

| # | Location | Current text | What P.0 forces |
|---|---|---|---|
| 1 | `AGENTS.md:139-145` (Phase P atomic steps) | `| **P.1 Frame** | orchestrator | classify the change type (Phase 0); create the TODO file and the question file from their templates; create the change's todo set | both files exist on `main`; the orchestrator sets TODO `Status: PREPARING` |` | a row **above** the step that creates the TODO file — a step whose own record does not exist yet |
| 2 | `AGENTS.md:147` (prep gate) | "**Prep gate ◆ READY.** A change is **READY** when its TODO file says `Status: READY`, **every** question in its question file is `ANSWERED`, and the P.4 artifact exists." | either a 4th READY condition (Out of scope per the TODO) or a step with no gate |
| 3 | `AGENTS.md:153-162` (status advances) | first row `| P.1 Frame | `PREPARING` |` | P.0 has no status to set; a dropped item never gets one (→ Q-3) |
| 4 | `AGENTS.md:219-236` (Workflow Diagram) | legend "**⏸** = user input (the **change** stops until answered)"; "PHASE P PREPARE (**per change**, before the workflow — all scheduled human input here)" | a new block + ⏸, and "per change" is wrong for a backlog-wide sweep (→ Q-2) |
| 5 | `AGENTS.md:303` | "**Ownership:** Phase P's **P.1 Frame** and **P.3 Answer** are the orchestrator; every other step is a dedicated, **synchronous** subagent" | name a 3rd orchestrator step |
| 6 | `AGENTS.md:335` | "Phase P's **P.1 Frame** and **P.3 Answer** stay on the **orchestrator** (the worktree is created at P.4)." | same |
| 7 | `AGENTS.md:339` | `| **P Prepare** | **P.1 Frame** (orchestrator) → **P.2 Interrogate** → **P.3 Answer** (orchestrator ⏸) → **P.4 Draft** → **P.5 Verify self-consistency** (FEATURE/CROSS-CUTTING only) ◆ READY |` | insert P.0 in the chain |
| 8 | `AGENTS.md:363` | "**Orchestrator** — performs Phase 0 **at P.1** … and runs **P.3** (present the question batch, record the answers)" | add P.0 to the role sentence |
| 9 | `AGENTS.md:418`, `:420` | "Sets are created at **P.1** and completed by the **Post-merge cleanup** item." / "**Creating the todo set (P.1).** … create one todo item per workflow step the change type executes" | a P.0 item cannot exist in a set created at P.1 → new exemption, or a conflict with Prohibition `:670` ("Advance a workflow phase without the todo status discipline") |
| 10 | `AGENTS.md:205-215` (Phase Matrix) | the `**P Prepare**` row is per type (5 cells listing Phase P outputs) | 5 cell edits (or one sentence at `:215`) |
| 11 | `AGENTS.md:659`, `:701-702` | "- Start implementation work before classifying the change type (Phase 0, at P.1)." / Obligations 17–18 | one new clause each |
| 12 | `specify/SKILL.md:14`, `:45`, `:46`, `:58-67`, `:117`, `:131`, `:167-170`, `:192-203`, `:207-224` | the step-order lists, the P.1/P.2 sections, Rules, Outputs, Definition of Done | every list that names the Phase P steps; note the Process lists are **manually numbered** (`27`–`41`), so inserting an item inside B/C/D renumbers ~15 lines |
| 13 | `.agents/skills/git/SKILL.md:22`, `:65` | "covers the creation at P.1–P.3 **and every TODO `Status:` advance through `MERGED`**"; the chain `PREPARING → … → MERGED` | a new write-ownership sentence for a record written **before** P.1 |

Under **Q-1 (b)** (a P.1 clause) the whole change is: `AGENTS.md:141` (P.1 row — Objective + "Done when"), `AGENTS.md:179` (one sentence in "Preparing many changes"), `AGENTS.md:215` (one sentence under the Phase Matrix, not 5 cells), `AGENTS.md:659` + `:701` (one clause each), `specify/SKILL.md:62-67` (the P.1 Frame section) + `:192-203`/`:207-224` if the Outputs/DoD lists gain the section, and `docs/todo/template.md` (the new section). Nothing in the todo-set rules, the status vocabulary, the Workflow Diagram or the READY gate has to move — and `specify/SKILL.md:45`/`:46` are **not** touched (P.1 is absent from `:45`; `:46` names P.1 only as an orchestrator step), which is what dissolves the Q-4 collision.

### Overlap / collision check (P.2 requirement)

- **`docs/specs/` (13 files: authentication, event-bus, file-management, logging, logging-coverage, mail-service, search, session-management, settings, settings-coverage, user-management, user-roles-permissions, template).** No spec defines or requires Phase P step wording, the planning templates, or a value-triage step (`grep -rln "alue triage" docs/specs/` → no match; the specs describe backend features). The TODO's "Related specs: none" holds, no REQ/AC is touched, and no **Spec Amendment** is needed → no reclassification trigger. Note `docs/specs/template.md` is a template, not a spec, and is **not** touched by this change (it belongs to `spec-interview-protocol`).
- **`docs/todo/` (16 backlog items + `template.md`):**

| TODO | Status | Triage | Overlap with this change |
|---|---|---|---|
| `value-triage-gate` | PREPARING | 5/5 implement | this change |
| `workflow-docs-nits` | **WAITING** (3 open questions) | 2/5 | **real collision** — `docs/todo/template.md` (`:44` vs our `:33-38`) and, only under Q-1 (a), `specify/SKILL.md:45`/`:46` (same lines). Its Q-3 is the reciprocal question → Q-4 |
| `spec-interview-protocol` | PREPARING | 4/5 | **declared order**: `:13` "Depends on: `value-triage-gate` … land **after** it", `:60`, `:51` "Value triage placement (owned by `docs/todo/value-triage-gate.md`)". It owns `docs/questions/template.md:18-25` (entry format), `docs/specs/template.md` §1, the `specify` P.2/P.3 sections (`:69-75`) and possibly `AGENTS.md:142` (the ≥ 20 floor). This change must stay off all of those → closed point 12 |
| `remove-spec-tdd-driver` | WAITING (PR #62) | 4/5 | none — its scope is one deleted `.ts` + its own verification record (`docs/todo/remove-spec-tdd-driver.md:22-29`) |
| `docs-path-ci-trigger` | PREPARING | **1/5 drop** | none; it is one of the two drop precedents (Q-3) |
| `split-archived-qa` | PREPARING | **1/5 drop** | none; the other drop precedent (Q-3) |
| `structure-map` | PREPARING | 4/5 | `AGENTS.md` is touched by it too (`docs/todo/structure-map.md:72` "Add a one-line note to AGENTS.md … pointing to STRUCTURE.md") — a different section (tooling), mergeable, no line conflict |
| `python-3.15` | PREPARING | 3/5 | `AGENTS.md` "Python 3.14+" line (`docs/todo/python-3.15.md:32` → `AGENTS.md:731`) — different section, mergeable |
| `update-readme` | PREPARING | 3/5 | `AGENTS.md` explicitly out of scope (`docs/todo/update-readme.md:88`) — none |
| `security-changelog-license` | PREPARING | 4/5 | `AGENTS.md` versioning out of scope; it defers "making CHANGELOG a workflow rule" to its own change — none |
| `api-keys`, `notifications`, `pyproject-tooling-gaps`, `structlog-logging`, `tenacity-rich-cachetools` | PREPARING | 5/4/3/3/2 | no `AGENTS.md`/template/skill edit planned — none |
| `track-python-skill` | MERGED | 4/5 | already landed (`c2342b6`); it is a triage precedent, not a collision |

- **In-flight worktrees / branches / PRs:** `git worktree list` → primary (`main` @ `2a0ee8e`) + `python-template_kopie-worktrees/chore/remove-spec-tdd-driver` (`4bd9247`); `git branch -a` → `main`, `chore/remove-spec-tdd-driver` (+ their remotes); `gh pr list --state open` → exactly **#62** (`chore/remove-spec-tdd-driver`, opened 2026-10-03). PR #62's diff is one deleted `.pi/workflows/spec-tdd.workflow.ts` + its verification record — **none** of this change's four target files (`AGENTS.md`, `docs/todo/template.md`, `.agents/skills/specify/SKILL.md`, and possibly `.agents/skills/git/SKILL.md`) → no conflict with in-flight work.
- **`docs/questions/`**: only `template.md` (untouched by this change unless Q-5 (ii) says otherwise) and the per-change files; `archive-AI_Questions.md` stays frozen (`AGENTS.md` "Central file retired").

### Points raised and closed from evidence (not asked)

1. **The template section's exact slot and shape** — all five existing records insert `## Value triage (2026-10-03, pre-workflow)` **between `## Constraints and risks` and `## Acceptance signal (plain language)`** (`docs-path-ci-trigger.md:35`, `split-archived-qa.md:35`, `workflow-docs-nits.md:40`, `track-python-skill.md:39`, `remove-spec-tdd-driver.md:39`), with bullets `**Overlap:**`, `**Beneficiary:**`, `**Score: N/5** — one sentence`, then `**Recommendation:**` (3 of 5) or `**Decision:**` (2 of 5, after the user answered). In `docs/todo/template.md` the slot is between `:32` (the `Constraints and risks` bullet) and `:34` (`## Acceptance signal (plain language)`). Exact block for P.4 is in "For P.4".
2. **No new artifact, no new write-permission rule** — the triage lives **inside** the TODO file, so the "Preparation artifacts (per change)" table (`AGENTS.md:126-133`) needs no row, and `AGENTS.md:151` already makes `docs/todo/` orchestrator-written in the primary worktree — which is why an orchestrator-owned P.1 clause needs no new ownership rule (a P.0 does, see cost row 13).
3. **Reference the Ponytail ladder, do not restate it** — `AGENTS.md:19-51`; rungs 1–2 at `:25-26` ("Does this need to be built at all? (YAGNI)" / "Does it already exist in this codebase? Reuse the helper, util, or pattern that's already here"), plus `:44` "Deletion over addition. Boring over clever." and `:45` "Question complex requests". What the ladder lacks — and what this change adds — is the **scored, user-decided, pre-work** form. Closed: the new text cites the section by name and the Ponytail section itself is not edited (TODO Out of scope).
4. **The 1–5 anchors stay verbatim** — the rule text is recorded "verbatim from the request" (`docs/todo/value-triage-gate.md:31-56`) and the anchors are the anti-subjectivity device the TODO's own "Subjectivity" constraint requires. Closed: quote them unchanged, including the "say so instead of guessing" clause.
5. **No auto-drop threshold; always ask** — the rule text ends "then ask me which to implement, merge, or drop"; nothing in the repo defines a score threshold and no script validates one. The two 1/5 items were still recorded and presented (`docs/todo/remove-spec-tdd-driver.md:20` "The 2026-10-03 value triage scored *updating* it 4/5, and **the user decided** the driver is not used at all"). Closed: the placeholder's "score below some threshold auto-drops" option is answered by the user's own text — no threshold.
6. **"One batched ask" ≠ one round — no conflict to resolve** — `AGENTS.md:143` already says "present the batch (**≤ 4 per `ask_user_question` round**, most blocking first)", i.e. one *batch*, several rounds; `docs/workflow/PROBLEMS.md:96` (P-1) records the observed cost of a single batch: 28 questions → "7 batches + 1 re-ask". So 16 backlog rows → up to 4 rounds is already legal. Closed, with one wording instruction for P.4: say "one triage **batch**, presented in as few rounds as possible (≤ 4 per round)" so nobody reads "one ask" as a single round.
7. **Fast-path changes need no triage** — `AGENTS.md:403` ("Emergency/fast-path exceptions … bypass the workflow entirely — no phases") and `:1077-1081`; the fast path needs no TODO file, and the rule is scoped "Before implementing any **TODO**". Closed: no TODO → no triage.
8. **"Any TODO" = every scheduled change** — P.1 creates a TODO for every change type (`AGENTS.md:141`), so the rule is a property of framing, not a separate backlog ritual. This is the same finding that makes Q-1 (b) the smaller diff.
9. **The READY gate is not changed** — `AGENTS.md:147` lists three conditions and the TODO puts "Changing what any existing gate requires (the READY gate …)" out of scope. The minimal consistent enforcement is a **Prohibition** clause (next to `:659` "Start implementation work before classifying the change type (Phase 0, at P.1)") — "start P.4 for a TODO whose Value triage section is empty or whose decision is not recorded" — a boundary rule, not a gate change.
10. **Phase Matrix: one sentence, not five cell edits** — the `**P Prepare**` cells (`AGENTS.md:207`) are per-type Phase P **outputs**; the triage output is type-independent, so the minimal edit is one sentence next to the existing note at `:215` ("\"Full gate set\" = the Phase 5 FEATURE checks below…").
11. **Gates, version, CI** — DOCS/CHORE → **no version bump** (`AGENTS.md` Versioning, `:739-757`); Phase 5 light gate set. `mkdocs.yml:6` is `docs_dir: userdocs` and no `userdocs/` file references `AGENTS.md` or the planning templates (`grep -rl "AGENTS.md" userdocs/` → no match), so the docs site cannot break, but `mkdocs build --strict` and `uv run python scripts/check_traceability.py` are still run as the acceptance signal requires. `check_traceability.py` scans `docs/specs/`, `docs/verification/traceability.md` and `tests/` only → no CI validator needs updating, and no `Status:` vocabulary is machine-checked (Q-3 evidence).
12. **`spec-interview-protocol` owns the P.2/P.3 surface** — its TODO declares the order (`:13`, `:60`) and disclaims this one (`:51`). Closed: this change must **not** touch `docs/questions/template.md:18-25` (entry format), `docs/specs/template.md` §1, the `specify` P.2/P.3 sections (`:69-75`), or the ≥ 20-question floor (`AGENTS.md:142`); it must not add a `Recommended:` field either.
13. **No collision with the in-flight change** — PR #62's scope proof (`docs/todo/remove-spec-tdd-driver.md:46`) shows exactly one deleted `.ts` path; none of this change's target files is in it.
14. **Dropping is already a legitimate, logged outcome** — the two 1/5 records stay on disk with their reason and an explicit "why logged anyway" note (`docs-path-ci-trigger.md:39` "Logged because the user wants the full backlog recorded", `split-archived-qa.md:39`). Closed: the change codifies that behaviour; the only open part is the status vocabulary (Q-3).
15. **Classification (reclassification check): DOCS/CHORE holds.** The change edits only `.md` guidance (`AGENTS.md`, `docs/todo/template.md`, `.agents/skills/specify/SKILL.md`, possibly `.agents/skills/git/SKILL.md`); it touches no `src/`, `tests/`, `docs/specs/` or `.github/workflows/` path, alters no externally observable product behavior, and per the Out-of-scope line it changes **no existing gate**. It does **add a human ⏸ to the protocol** (a triage ask), which is more than the cosmetic `workflow-docs-nits` kind — but adding a documented step is still criterion #5 (documentation/tooling), the same classification `spec-interview-protocol` gives its own P.2/P.3 edits (`docs/todo/spec-interview-protocol.md:8`). Hazard for Phase 6 review, not a reclassification: if Q-2 is answered (b) (global stop), the change must also amend `AGENTS.md:305`/`:406`/`:674` — at that point it changes scheduling rules and should be re-checked against the Escalation Rules.

### For P.4 (scope record) — settled, line-cited

**`docs/todo/template.md`** — insert between `:32` and `:34` (after the `## Constraints and risks` bullet):

```markdown
## Value triage (<YYYY-MM-DD>, pre-workflow)
- **Overlap:** <what in this repository already covers it — name the file/function; "none">. If it overlaps: <the existing feature to extend instead of a new one>
- **Beneficiary:** <who benefits and how (the end user of this project); "unclear" / "too vague to judge" instead of guessing>
- **Score: <1-5>/5** — <one sentence explaining the score>  <!-- 5 = clear user value, new, small change · 3 = some value, or partly overlapping, or moderate effort · 1 = no clear value, duplicate, or large/risky change -->
- **Recommendation:** implement / merge into <existing feature> / drop
- **Decision:** <the user's answer + date>  <!-- recorded when the user answers; a dropped TODO stays on disk with its reason -->
```

The `**Decision:**` bullet is the superset of the two existing shapes (3 records use `Recommendation:`, 2 replaced it with `Decision:` — closed point 1), so the section records both the triage and the outcome. No Prep-log row is added (3 of 5 records log the triage in the existing `P.1 Frame` row; the template stays smallest).

**`AGENTS.md`** (under Q-1 (b); the exact wording is P.4's, the locations and current text are settled here):

| Line | Current text | Edit |
|---|---|---|
| `:141` | "\| **P.1 Frame** \| orchestrator \| classify the change type (Phase 0); create the TODO file and the question file from their templates; create the change's todo set \| both files exist on main; the orchestrator sets TODO Status: PREPARING \|" | add the four checks + score + recommendation to the Objective, and "the `## Value triage` section is filled and the user's decision recorded" to *Done when* |
| `:179` | "Prepare as many changes as you like before starting the workflow …" | one paragraph: the sweep, the `ID \| TODO \| score \| recommendation \| reason` table, "one triage **batch**, presented in as few rounds as possible (≤ 4 per round)", and the Q-2 scoping of "do not implement before the answer" |
| `:215` | "\"Full gate set\" = the Phase 5 FEATURE checks below. Every type ends with a PR …" | one sentence: every Phase P output above presupposes a recorded Value triage decision |
| `:659` | "- Start implementation work before classifying the change type (Phase 0, at P.1)." | a sibling prohibition (closed point 9) |
| `:701` | "17. Prepare every change before running its workflow (Phase P): TODO file, ≥ 20 interrogation questions …" | add "value triage (overlap / beneficiary / 1–5 score / recommendation) and the user's implement-merge-drop decision" |
| `:155-162` + `docs/todo/template.md:7` | the six-value `Status:` table / the `<!-- PREPARING \| … \| MERGED -->` comment | **only if Q-3 = (a)**: add `DROPPED` (and `git/SKILL.md:65`) |

**`.agents/skills/specify/SKILL.md`** — the P.1 Frame section (`:62-67`: Objective `:64`, Inputs `:65`, Outputs `:66`, Done-criteria `:67`) gains the triage; `:192-203` (Outputs) and `:207-224` (Definition of Done, first bullet `:211`) gain the `## Value triage` section as a Phase P output. **Do not touch** `:45`/`:46` (the step-order and ownership lists — that is `workflow-docs-nits`'s line, Q-4), `:69-75` (P.2 — `spec-interview-protocol`), or the numbered Process lists (`27`–`41`, manual numbering; if the DOCS/CHORE path `:139-141` needs an item, append `42`, which renumbers nothing).

**Not in scope for P.4:** `docs/questions/template.md`, `docs/specs/template.md`, `AGENTS.md:19-51` (Ponytail — reference only), any script/CI change, any version bump.

**Nothing else blocks the change:** with Q-1..Q-5 answered, P.4 can draft the scope record directly from this file.

## Q-7 — where do DROPPED and MERGED planning records live: a separate folder?
- **Step:** P.3 Answer round 2 (raised by the user's Q-3 answer)
- **Why needed:** Q-3 = (a) adds the `DROPPED` status, and the user additionally wants dead items (dropped, and merged) moved out of the live backlog folder. That changes paths the live guidance names: `AGENTS.md` Phase P (`docs/todo/<name>.md`, `docs/questions/<name>.md`), the Ready-selection order ("among prepared changes"), the cleared-gate test, and `git/SKILL.md`'s status-advance rule. (`scripts/check_traceability.py` reads only `docs/specs/`, `docs/verification/traceability.md` and `tests/`, so it is unaffected.)
- **Context:** today `docs/todo/` holds 18 live files + template and `docs/questions/` 18 + template; `track-python-skill` and `remove-spec-tdd-driver` are already `Status: MERGED` and sit in the live folder. `AGENTS.md` says a dropped item's TODO file "never enters the workflow", and the Ready-selection order reads the backlog on `main` — so a move must keep both findable, and the git skill's "commit planning artifacts" step names the two paths explicitly.
- **Question:** which layout, and when does the move happen? **(i)** `docs/todo/archive/<name>.md` + `docs/questions/archive/<name>.md`, moved by the orchestrator at the drop decision and at post-merge cleanup (S7.1); **(ii)** one shared `docs/archive/<type>/<name>.md`; **(iii)** keep them in place and rely on the `DROPPED`/`MERGED` status only (Q-3 (a) without the move). Sub-part: does the question file move with the TODO file (recommended: yes — they are one change's record)?
- **Answer:** **(i)** — `docs/todo/archive/<name>.md` and `docs/questions/archive/<name>.md`. The orchestrator moves both **at the drop decision** and **at post-merge cleanup (S7.1)**; the question file always moves with its TODO file. The live guidance that names the two paths must be updated in the same change: the Phase P preparation-artifacts table, the "Planning records (owner: the orchestrator)" section, the Ready-selection order, the cleared-gate test, and `git/SKILL.md`'s planning-commit and post-merge-cleanup steps.
- **Date:** 2026-10-04
- **Status:** ANSWERED
- **Incorporated:** yes — added to the TODO's In scope; the two items dropped on 2026-10-04 and the two `MERGED` items are the first files to move once this change merges

## Late questions (Phases 2–6)

<questions discovered after the change entered the workflow; same entry format, Step field set to the step that found it>
