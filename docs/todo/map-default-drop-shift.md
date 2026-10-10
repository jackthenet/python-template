# TODO: map-default-drop-shift

Backlog item for one planned change, created at **P.1 Frame** from this template and named `<change-name>.md`. One file per change.

This is a **planning record, not normative**: like `docs/questions/`, it is committed directly to `main` (see "Phase P: PREPARE" in `AGENTS.md`). It carries no approval gate — the spec does.

- **Status:** WAITING  <!-- PREPARING | QUESTIONS-ANSWERED | READY | IN-WORKFLOW | WAITING | MERGED | DROPPED -->
  <!-- IN-WORKFLOW -> WAITING 2026-10-10: Phase 5 closed (S5.1–S5.4, spec coverage 100% of the 4 affected IDs) and Phase 6 review report CLEAN (S6.1 `87f2ad4`, S6.2 `1b0da55`, S6.3 `081082c`); **PR #80** opened (`issue/map-default-drop-shift` -> `main`, 1.1.0 -> 1.1.1, all 12 CI checks SUCCESS, mergeable). Human gate S6.4: waiting for the merge, then S7.1 cleanup. -->
  <!-- QUESTIONS-ANSWERED 2026-10-09: all 19 questions in docs/questions/map-default-drop-shift.md ANSWERED + incorporated (4 rounds); value-triage decision recorded (implement, 3/5) -> P.4 gate open -->
- **Change type:** ISSUE  <!-- likely needs a Spec Amendment first: see "Why" -->
- **Created:** 2026-10-09
- **Question file:** `docs/questions/map-default-drop-shift.md`
- **Spec:** n/a — the defect lives against `docs/specs/structure-map.md` (REQ-014 / AC-014)
- **Worktree:** <created at P.4> `../python-template_kopie-worktrees/issue/map-default-drop-shift`
- **Depends on:** structure-map — **satisfied 2026-10-09**: PR #75 merged into `main` at 2026-10-09T20:09:53Z (merge commit `7dfaa23`), so `scripts/make_map.py` and `STRUCTURE.md` exist on `main` and a RED reproduction is observable on a branch cut from `main`
- **Related specs:** `docs/specs/structure-map.md`

## Goal (one line)
Make the structure map's signature rendering drop over-long parameter defaults without changing the meaning of the signature that is shown.

## Why
Found as finding **F-08** while refactoring `scripts/make_map.py` at S4.3 (T-004) of `structure-map` (recorded in `docs/verification/structure-map.md` and in that branch's `docs/workflow/PROBLEMS.md` P-78).

`_drop_long_defaults` shortens a signature when a parameter's default is too long to render (`_DEFAULT_MAX_CHARS = 20`). When the dropped default belongs to a **positional** parameter, the remaining defaults shift onto earlier parameters: the map then shows a signature whose callability differs from the real function's. The witness set does not cover this case (AC-014 pins only three `ast.unparse` needles), so the defect is real but unwitnessed.

It was deliberately **not** fixed inside `structure-map`: that change may not introduce behavior its approved spec does not state, and any fix changes AC-014 output — so it needs either a Spec Amendment to `docs/specs/structure-map.md` or a reclassification as FEATURE.

## In scope
- The drop rule in `scripts/make_map.py::_drop_long_defaults` (keyword-only vs positional handling).
- A reproduction test that pins the rendered signature for a function with a long **positional** default.
- A Spec Amendment to `docs/specs/structure-map.md` REQ-014/AC-014 if the required rendering is not stated there.

## Out of scope
- The rest of the symbol layer (REQ-015..REQ-018).
- The `_DEFAULT_MAX_CHARS = 20` threshold value itself, unless the triage shows the shift is only reachable through it.

## Affected features
`scripts/make_map.py` (the structure-map generator) — no `src/` code is involved.

## Constraints and risks
- `scripts/make_map.py` output is byte-compared by AC-021 (committed `STRUCTURE.md` freshness), so a fix must regenerate and commit the map in the same change.
- Complexity ceiling: **corrected 2026-10-09 (P.2/Q-15)** — CI runs `uv run complexipy src tests --max-complexity-allowed 15` (`.github/workflows/quality.yml:146`); `scripts/` is **not** analyzed today, so the ceiling does **not** apply to `scripts/make_map.py` for this change. Extending it to `scripts/` was decided (Q-15/Q-19) but lands in a **separate** change, `chore/complexipy-scripts` — measured at `7dfaa23`, `make_map.py` is clean (max 12) while 4 pre-existing functions in `check_traceability.py` / `validate_task_dag.py` / `verify_spec.py` exceed 15.
- Per the escalation rules, if the fix requires behavior the approved spec does not state, it becomes a Spec Amendment PR (or FEATURE) before implementation.

## Value triage (2026-10-09, pre-workflow)
- **Overlap:** none — `_drop_long_defaults` in `scripts/make_map.py` is the only default-shortening code in the repository; no other feature renders signatures.
- **Beneficiary:** a reader of `STRUCTURE.md` who infers a function's call signature from the map; the benefit is correctness of that documentation, not a runtime behavior. Narrow but real: a shifted signature is actively misleading.
- **Score: 3/5** — re-rated from 2/5 on 2026-10-09 at P.3: the original score rested on the premise that the defect was unwitnessed, and P.2 found it **live in the committed `STRUCTURE.md` on `main`** (`STRUCTURE.md:1813`, `simple_template`). A genuine, localized defect with a small fix; still documentation-facing, but the wrong signature is shipped in the artifact readers are told to trust.
- **Recommendation:** implement — as a **light-tier ISSUE** (2 non-test files: `scripts/make_map.py` + regenerated `STRUCTURE.md`), preceded by a **Spec Amendment PR** to `docs/specs/structure-map.md` (REQ-014/AC-014 + new `INV-007`/`EDGE-017`), because REQ-014 does not settle the required rendering.
- **Decision:** **IMPLEMENT** (user, 2026-10-09, P.3 round 1) — amendment PR A first, then PR B as a light-tier ISSUE with a patch bump (1.1.0 → 1.1.1). Not merged into another change, not dropped. P.4 (branch + worktree) is now permitted.

## Acceptance signal (plain language)
A function with a long positional default appears in `STRUCTURE.md` with a signature that still means the same thing as the real function — the parameters that keep their defaults keep them — and a new test proves it.

## Prep log
| Step | Date | Result |
|---|---|---|
| P.1 Frame | 2026-10-09 | classified ISSUE (possible Spec Amendment); TODO + question file created on `main`; value triage recorded, decision PENDING |
| P.2 Interrogate (18 questions) | 2026-10-09 | DONE — 18 entries recorded in `docs/questions/map-default-drop-shift.md` in one `BLOCKED-USER` batch (5 blocking). Key findings: the required rendering is **not** settled by REQ-014 (Q-1); the defect is **already live** in the committed map (`STRUCTURE.md:1813`); exactly one function in Packages scope has a >20-char positional default; the AC-014 unit witnesses do not cover the shift; the TODO's complexipy constraint is inaccurate. Overlap checked against `docs/specs/` and every TODO in `docs/todo/` |
| P.3 Answer (19 answered) | 2026-10-09 | DONE — 4 `ask_user_question` rounds, all 19 questions ANSWERED + incorporated (Q-19 derived from Q-15). Decisions: ISSUE + **Spec Amendment PR A first** (Q-1); **placeholder `…` in position** as the normative rendering (Q-2); uniform across positional / positional-only / keyword-only defaults (Q-6/Q-7); new **`INV-007` + `EDGE-017`** ⇒ Hypothesis property test mandatory (Q-9); **both** reproduction witnesses (Q-10); **light-tier** Phase 5 with the full suite at the S6.4 pre-merge gate (Q-12); existing AC-014 witnesses **authorized to be re-derived**, not weakened (Q-11); threshold 20 untouched (Q-8); bare-ID matrix rows + rows for the new IDs (Q-14); gate set confirmed and the complexipy line corrected (Q-15); complexipy extension deferred to **`chore/complexipy-scripts`** (Q-19); hard scope boundary = the parameter-default rule only (Q-16); no compatibility flag (Q-18); PR shape = amendment PR (no bump) + ISSUE PR (patch bump 1.1.0 → 1.1.1) (Q-3/Q-4/Q-13/Q-17) |
| P.4 Draft spec / triage / baseline / scope | | next — PR A: Spec Amendment to `docs/specs/structure-map.md`; PR B: triage record in the change worktree |
| P.5 Self-consistency (FEATURE/CROSS-CUTTING) | | n/a — ISSUE (no spec authored; the amendment is a separate change) |
