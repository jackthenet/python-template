# Questions: workflow-docs-nits

One question file per change, created at **P.1 Frame** from this template and named `workflow-docs-nits.md`. It replaces the retired central `AI_Questions.md` (archived at `docs/questions/archive-AI_Questions.md`).

- **Change:** workflow-docs-nits (DOCS/CHORE)
- **TODO file:** `docs/todo/workflow-docs-nits.md`
- **Spec:** n/a
- **Opened:** 2026-10-03
- **Status:** ALL ANSWERED  <!-- 0 PENDING -->
- **Answer rounds:** 1 (2026-10-04: Q-1, Q-2, Q-3)

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

**3 questions need user input (Q-1..Q-3, one `BLOCKED-USER` batch); 9 interrogation points were closed from repository evidence** (recorded below with their evidence). DOCS/CHORE carries no ≥ 20-question floor (`AGENTS.md:142` parenthesises it "(FEATURE/CROSS-CUTTING)"; `specify:74` sits under `## Atomic Steps (FEATURE / CROSS-CUTTING)`). All four In-scope items were verified against the current tree (`main` @ `b68b93a`) with file:line evidence and the exact minimal wording, so P.4 can draft directly from this record. **Classification check: DOCS/CHORE holds — none of the four fixes changes what a gate requires** (evidence under "Classification").

## Q-1 — item (c) targets `AGENTS.md`, which the TODO puts out of scope
- **Step:** P.2 Interrogate
- **Why needed:** the TODO's third In-scope item names `docs/questions/template.md:9`, but the actual fix per the follow-up is a row in the **F-5 ownership table in `AGENTS.md`** — and the TODO's Out-of-scope list says "`AGENTS.md` … out of scope". The scope as written is self-contradictory; only the user can settle it.
- **Context:** verified: `docs/questions/template.md:9` **already names the producer on the header line** — `- **Status:** OPEN  <!-- OPEN | ALL ANSWERED — set OPEN by the orchestrator at P.1; ALL ANSWERED once every question in this file has an answer (the orchestrator records it together with the QUESTIONS-ANSWERED TODO advance) -->` — because F-14 was closed exactly that way (`prepared-workflow.md:489`). There is **nothing left to add at `:9`**. Follow-up 4 (`prepared-workflow.md:588`) reads: "F-14's producer is named on the header line itself; **if the F-5 ownership table is next touched**, adding the row there keeps both places in sync (S6.8 noted this)." The F-5 table is `AGENTS.md:155-162` ("Planning records (owner: the orchestrator)", `| When | Status |` at `:155`) and covers only the TODO `Status:`. F-14 was accepted because "nothing reads the header; the READY gate and the cleared-gate test read the entry-level `ANSWERED` / `PENDING` values" (`prepared-workflow.md:440`). The follow-up is **conditional** — nothing today schedules touching that table.
- **Question:** item (c) as written is a no-op on `docs/questions/template.md:9`; the real edit is one row in the `AGENTS.md:155-162` table, which the TODO excludes. Which: **(a)** drop item (c) — the condition ("if the F-5 table is next touched") is not met and nothing reads the header *(recommended; keeps the change inside its declared scope)*; **(b)** bring `AGENTS.md` into scope for exactly one row (e.g. a row `question file header → OPEN at P.1 / ALL ANSWERED with the QUESTIONS-ANSWERED advance` — still DOCS/CHORE, same kind as `value-triage-gate`'s AGENTS.md text edits); or **(c)** something else?
- **Answer:** **(a) — drop item (c).** The follow-up's own condition ("if the F-5 ownership table is next touched") is not met, `docs/questions/template.md:9` already names the producer inline, and nothing reads the header. The change stays inside its declared scope (no `AGENTS.md`).
- **Date:** 2026-10-04
- **Status:** ANSWERED
- **Incorporated:** yes — item (c) removed from the TODO's In scope

## Q-2 — is editing the frozen merged record `prepared-workflow.md` (item d) legitimate at all?
- **Step:** P.2 Interrogate
- **Why needed:** the fourth item edits a merged, CLEAN-verdict verification record. The repo's precedents cut against editing frozen records, and the TODO's acceptance signal ("the `prepared-workflow.md` sweep counts match the tree") is unachievable as literally written. The user decides whether the record gets touched.
- **Context (re-measured with the sweep's own commands, `grep -rn "P\.5" AGENTS.md .agents/skills docs/workflow docs/todo docs/questions/template.md` and the same for `READY`):** at the merge commit `4b42c58` the counts are **25 / 43** — exactly the record's "final state" claim (`prepared-workflow.md:563`), and the difference vs the table's 24 / 42 (`:509`) is **exactly `docs/workflow/PROBLEMS.md:377`** (the P-39 recipe sub-bullet the same S6.9 commit `6807d38` added; it contains both "P.5" and "READY"; the table lists only `:372`). So the follow-up's factual claim is **confirmed**. Which alternative is factually right: **add the missing `PROBLEMS.md:377` row** (class (c)) — "correct the counts" would misreport the measurement, because 24 / 42 is what the command printed when the sweep ran, before the same commit added `:377`, and the record already reconciles both numbers in its "Sweep arithmetic" paragraph (`:563`, "record nit, not a document defect … the sweep's conclusion is unaffected"). Frozen-record precedents **against** the edit: `prepared-workflow.md:53` (its own scope rule: "historical records (ADRs, old verification files) are NOT rewritten"); `docs/todo/remove-spec-tdd-driver.md:29` (the in-flight change explicitly puts rewriting `prepared-workflow.md:80/:347/:383` out of scope); `docs/todo/split-archived-qa.md:38` scored a frozen-record edit **1/5 — "it churns a frozen historical record for a nicety nothing consumes"** and was recommended dropped; the traceability convention (`AGENTS.md`) treats dated gate records as historical and never refreshes them. **For** the edit: follow-up 3 itself pre-authorizes it — "correct the count or add the row **if the record is next edited**" — and the TODO's constraint already fixes the manner (PR only, no finding rewrites). Also measured: on today's `main` the same commands give **47 / 63** (16 backlog TODO files added after the merge each carry `P.5`/`READY` lines), so any "corrected" count is a point-in-time snapshot that is already stale — the acceptance-signal wording cannot be satisfied literally.
- **Question:** keep item (d) or drop it? **(a)** drop item (d) — the record already discloses the arithmetic, the counts are point-in-time, and the repo's precedents (`remove-spec-tdd-driver` out-of-scope, `split-archived-qa` 1/5) treat frozen-record churn as not worth a change *(recommended)*; **(b)** keep it, scoped to **adding the missing `PROBLEMS.md:377` row** to the S6.9 table (NOT re-numbering 24/42 — that would misstate the measurement), via PR, and reword the acceptance signal to "the S6.9 table lists every hit at the merge state"; or **(c)** keep it and also correct the counts to 25/43 despite the misreporting problem?
- **Answer:** **(a) — drop item (d).** The record already reconciles the arithmetic in its "Sweep arithmetic" paragraph, the counts are point-in-time (the same commands print 47/63 on today's `main`), and repo precedent (`split-archived-qa` scored 1/5 for exactly this kind of frozen-record churn) treats it as not worth a change.
- **Date:** 2026-10-04
- **Status:** ANSWERED
- **Incorporated:** yes — item (d) removed from the TODO's In scope; the change is now items (a)+(b) only

## Q-3 — collision with `value-triage-gate` on `specify/SKILL.md:45` and `docs/todo/template.md`: sequence or fold?
- **Step:** P.2 Interrogate
- **Why needed:** two PREPARING backlog items plan edits to the same lines of the same files; running both without an order/ownership decision risks a merge conflict or a lost qualifier. The order is a backlog decision (the value-triage recommendations are presented to the user), not something P.2 can settle from the tree.
- **Context:** `docs/todo/value-triage-gate.md:51` (PREPARING, 5/5 implement) scopes edits to "`AGENTS.md` — Phase P atomic-steps table, the Phase Matrix …, `docs/todo/template.md` — a `## Value triage` section …, `.agents/skills/specify/SKILL.md` — the P.1/P.2 area and its Outputs/Done sections". Inserting a value-triage step will almost certainly rewrite the step-order list at `specify/SKILL.md:45` — **the exact line item (b) qualifies** — and both items touch `docs/todo/template.md` (item (a) at `:44`; value-triage-gate adds a section around `:33-35` — different lines, mergeable but line-shifted). `spec-interview-protocol` (PREPARING, depends on value-triage-gate) also edits `docs/questions/template.md` (entry format `:18-25`) and the `specify` P.2/P.3 sections — different lines from items (a)-(c), mergeable; its own TODO flags "both edit the same P.2/P.3 guidance surface … land it second". `workflow-docs-nits` records `Depends on: prepared-workflow` only — no dependency between it and the other two.
- **Question:** how to defuse the collision? **(a)** land `workflow-docs-nits` (items a+b) **first** — a two-line qualifier diff that `value-triage-gate` then builds on *(recommended: smallest diff first, matches the easiest-first rule)*; **(b)** drop this change and **fold items (a)+(b) into `value-triage-gate`'s PR** (it already edits both files — one change instead of two touching the same lines); or **(c)** another order/ownership?
- **Answer:** **(a) — this change lands first.** Confirmed landing order for the three colliding items: `workflow-docs-nits` → `value-triage-gate` → `spec-interview-protocol`. Items (a)+(b) are **not** folded into `value-triage-gate`; it gains `Depends on: workflow-docs-nits` and builds on the qualifiers. `architecture-tests-missing` edits different lines and is unconstrained.
- **Date:** 2026-10-04
- **Status:** ANSWERED
- **Incorporated:** yes — recorded in the TODO's Constraints; this change is now the first of the three to run, so its two remaining questions (Q-1, Q-2) are the critical path

### Verification of the four In-scope items (current tree `main` @ `b68b93a`, for P.4)

**(a) `docs/todo/template.md:44` — CONFIRMED, needs the qualifier.** Current: `| P.5 Self-consistency | | |` (the file's only P.5 mention). The `Spec:` row at `:11` **is** already qualified: `- **Spec:** \`docs/specs/<change-name>.md\`  <!-- FEATURE/CROSS-CUTTING only; n/a for the other types -->`. Exact minimal fix (the follow-up's own wording, `prepared-workflow.md:585`): `| P.5 Self-consistency (FEATURE/CROSS-CUTTING) | | |`. No gate reads the Prep log (`prepared-workflow.md:585`: "no gate anywhere in the live guidance reads the Prep log … a one-word clarity nit next to the already-qualified `:11` … row"), so this is non-normative. The 16 backlog TODO files copy the row (e.g. this change's own `docs/todo/workflow-docs-nits.md:52` `| P.5 Self-consistency | | n/a (DOCS/CHORE) |`); template-only edit, existing files stay as historical records.

**(b) `.agents/skills/specify/SKILL.md:14`, `:45`, `:46` — CONFIRMED, all three list P.5/S1.4 unqualified.** Exact current text and minimal fixes:
- `:14`: "The former steps **S1.1 / S1.2 / S1.3** are now **P.2 / P.4 / P.5** — same content, run during preparation. Only **S1.4** stays inside the normal workflow, and the change branch and worktree are created at **P.4**, not at classification." → insert the qualifier: "…are now **P.2 / P.4 / P.5** (FEATURE/CROSS-CUTTING) — same content…" — this makes it read exactly like the model `AGENTS.md:175` ("The former specification steps **S1.1 / S1.2 / S1.3** are now **P.2 / P.4 / P.5** (FEATURE/CROSS-CUTTING) — same content, run during preparation.").
- `:45`: "- **Atomic steps:** execute this skill's atomic steps in order (see the Workflow Diagram in `AGENTS.md`): **P.2 Interrogate** → **P.3 Answer** (orchestrator ⏸) → **P.4 Draft** → **P.5 Verify self-consistency** → **S1.4 Present for approval**. Each has a single objective, inputs, expected outputs, and a done criterion." → "…**P.5 Verify self-consistency** (FEATURE/CROSS-CUTTING only) → **S1.4 Present for approval** (FEATURE/CROSS-CUTTING only).…" — mirrors `AGENTS.md:339` ("**P.5 Verify self-consistency** (FEATURE/CROSS-CUTTING only) ◆ READY") and the Phase Matrix (Phase 1 runs only for FEATURE/CROSS-CUTTING).
- `:46`: "- **Ownership:** **P.1 Frame** and **P.3 Answer** are **orchestrator** steps (no subagent); P.2, P.4, P.5 and S1.4 each run in their own subagent. P.2 and P.3 run in the **primary worktree** (no change worktree exists yet); the change branch and worktree are created at **P.4**, and P.5 and S1.4 run inside it." → "…P.2, P.4, P.5 and S1.4 (the latter two FEATURE/CROSS-CUTTING only) each run in their own subagent.…" — one qualifier on the first mention; the second mention ("P.5 and S1.4 run inside it") inherits it.
- **Wording trap (TODO "Constraints and risks", confirmed):** the qualifier must mirror the `AGENTS.md` wording verbatim so it cannot read as a new gate rule. S6.9 already classifies these three lines as (c) "unqualified restatements of the step mapping … they neither set nor gate READY" (`prepared-workflow.md:513`), so mirroring keeps the change cosmetic.

**(c) `docs/questions/template.md:9` — CONFIRMED, but nothing to add at `:9`** (producer already on the header line; see Q-1). The row belongs in `AGENTS.md:155-162`; blocked on Q-1.

**(d) `docs/verification/prepared-workflow.md` S6.9 sweep — claim CONFIRMED; the factually right alternative is "add the missing `PROBLEMS.md:377` row", not "correct the counts"** (full measurement and precedents in Q-2's Context). Blocked on Q-2.

### Overlap check (P.2 requirement)

- **`docs/specs/` (13 files):** no spec references the planning templates, the `specify` skill, or P.5/S1.4 step wording (the single grep hit `docs/specs/session-management.md:30` is the word "re-specify" — false positive). No approved REQ/AC is touched; the TODO's "Related specs: none" holds. No reclassification trigger.
- **`docs/todo/` (16 backlog items + template):**
  - `value-triage-gate` (PREPARING, 5/5): **real collision** — same files (`docs/todo/template.md`, `specify/SKILL.md`) and likely the same line (`:45` step-order list). → Q-3.
  - `spec-interview-protocol` (PREPARING, depends on value-triage-gate): same files `docs/questions/template.md` (entry format `:18-25` vs item (c)'s `:9`) and `specify/SKILL.md` (P.2/P.3 sections vs items (b)'s `:14/:45/:46`) — different lines, mergeable; it may also touch `AGENTS.md` (≥ 20 floor), which would matter only if Q-1 answer (b) is chosen.
  - `remove-spec-tdd-driver` (WAITING, PR #62 open): explicitly does **not** touch `prepared-workflow.md` (`docs/todo/remove-spec-tdd-driver.md:29`) — the TODO's constraint ("if both changes run, this one owns the `prepared-workflow.md` edit") is already satisfied; **no collision on item (d)**.
  - `split-archived-qa`, `docs-path-ci-trigger` (both recommended **drop**, 1/5): reference `prepared-workflow.md` only as their follow-up source; no edits.
  - The other 9 items (api-keys, notifications, pyproject-tooling-gaps, python-3.15, security-changelog-license, structlog-logging, structure-map, tenacity-rich-cachetools, update-readme): no mention of any of the four target files.
- **In-flight worktrees/branches/PRs:** `git worktree list` → primary (`main` @ `b68b93a`) + `chore/remove-spec-tdd-driver`; `git branch -a` → `main`, `chore/remove-spec-tdd-driver` (+ their remotes); `gh pr list --state open` → exactly **#62** (remove-spec-tdd-driver). No other in-flight change can collide.

### Points raised and closed from evidence (not asked)

1. **Item (a) wording** — closed: use the follow-up's exact qualifier "P.5 Self-consistency (FEATURE/CROSS-CUTTING)" (`prepared-workflow.md:585`); no style question (the `:11` HTML-comment style does not fit a table row).
2. **Item (b) wording** — closed: mirror `AGENTS.md:175`/`:339` verbatim (the follow-up itself says the qualifier "would make them read like `AGENTS.md:175`", `prepared-workflow.md:586`).
3. **Item (d) arithmetic** — closed by re-measurement: 25/43 at `4b42c58`, difference is exactly `PROBLEMS.md:377`, the follow-up's claim is true; and of the two alternatives only "add the row" is factually defensible (the 24/42 counts were true at sweep time and the record already reconciles them at `:563`). (Legitimacy of the edit remains Q-2.)
4. **Item (c) at `:9`** — closed: `docs/questions/template.md:9` already names producer + moment (F-14 closed on the header line, `prepared-workflow.md:489`); the item as literally scoped is a no-op. (Where the row goes remains Q-1.)
5. **Classification (reclassification check)** — closed: **DOCS/CHORE holds for all four items.** (a) no gate reads the Prep log (`prepared-workflow.md:585`); (b) class (c) restatements that "neither set nor gate READY" (`prepared-workflow.md:513`); (c) would add an ownership row for a header status "nothing reads" (`prepared-workflow.md:440`) — process-guidance text in `AGENTS.md`, the same DOCS/CHORE kind `value-triage-gate` performs; (d) record accuracy. No item changes what a gate requires → no ISSUE/FEATURE/CROSS-CUTTING trigger. The only hazard is the (b) wording trap, handled as a P.4/review check (qualifier must mirror `AGENTS.md`), not a reclassification.
6. **Bundling** — closed in principle: four cosmetic fixes in one chore is right at 2/5 (the TODO's own triage: "worth exactly one bundled chore, not four separate changes"); but the bundle's composition depends on Q-1/Q-2 — the guaranteed core is items (a)+(b).
7. **`docs/specs/` overlap** — closed: none (see overlap check).
8. **Collision with `remove-spec-tdd-driver` on `prepared-workflow.md`** — closed: that change disclaims the edit (`docs/todo/remove-spec-tdd-driver.md:29`); PR #62's diff cannot conflict with item (d).
9. **Version bump / gates** — closed by `AGENTS.md`: DOCS/CHORE → no bump; Phase 5 light gate set (`mkdocs build --strict` + traceability check per the acceptance signal; `docs_dir: userdocs` means `docs/` edits are not published, so mkdocs risk is nil — the gate is still run as the acceptance signal requires).

### For P.4 (scope record)

Guaranteed scope (independent of the answers): `docs/todo/template.md:44` qualifier + the three `specify/SKILL.md` qualifiers (`:14`, `:45`, `:46`) with the exact wording above. Pending Q-1: whether an `AGENTS.md:155-162` row joins the scope. Pending Q-2: whether `docs/verification/prepared-workflow.md` (S6.9 table, one added row) joins the scope. Pending Q-3: sequencing vs folding with `value-triage-gate` (affects the scope record's collision note, not the diff).

## Late questions (Phases 2–6)

<questions discovered after the change entered the workflow; same entry format, Step field set to the step that found it>
