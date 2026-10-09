# TODO: map-default-drop-shift

Backlog item for one planned change, created at **P.1 Frame** from this template and named `<change-name>.md`. One file per change.

This is a **planning record, not normative**: like `docs/questions/`, it is committed directly to `main` (see "Phase P: PREPARE" in `AGENTS.md`). It carries no approval gate — the spec does.

- **Status:** PREPARING  <!-- PREPARING | QUESTIONS-ANSWERED | READY | IN-WORKFLOW | WAITING | MERGED | DROPPED -->
- **Change type:** ISSUE  <!-- likely needs a Spec Amendment first: see "Why" -->
- **Created:** 2026-10-09
- **Question file:** `docs/questions/map-default-drop-shift.md`
- **Spec:** n/a — the defect lives against `docs/specs/structure-map.md` (REQ-014 / AC-014)
- **Worktree:** <created at P.4> `../python-template_kopie-worktrees/issue/map-default-drop-shift`
- **Depends on:** structure-map (must merge first — the defective helper is created by it)
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
- Complexity ceiling: `complexipy max-complexity-allowed = 15` applies to `scripts/` via the CI job added by structure-map T-001.
- Per the escalation rules, if the fix requires behavior the approved spec does not state, it becomes a Spec Amendment PR (or FEATURE) before implementation.

## Value triage (2026-10-09, pre-workflow)
- **Overlap:** none — `_drop_long_defaults` in `scripts/make_map.py` is the only default-shortening code in the repository; no other feature renders signatures.
- **Beneficiary:** a reader of `STRUCTURE.md` who infers a function's call signature from the map; the benefit is correctness of that documentation, not a runtime behavior. Narrow but real: a shifted signature is actively misleading.
- **Score: 2/5** — a genuine, localized defect with a small fix, but it affects only generated documentation, is currently unwitnessed, and is only reachable for functions whose positional defaults exceed 20 characters.
- **Recommendation:** implement — after `structure-map` merges, as a light-tier ISSUE (single file, ≤ 3 files touched, no new dependency); open the Spec Amendment PR first if the triage shows REQ-014 does not already settle the required rendering.
- **Decision:** **PENDING** — awaiting the user's implement / merge / drop choice (the user is away; no `P.4` branch may be created until this is recorded).

## Acceptance signal (plain language)
A function with a long positional default appears in `STRUCTURE.md` with a signature that still means the same thing as the real function — the parameters that keep their defaults keep them — and a new test proves it.

## Prep log
| Step | Date | Result |
|---|---|---|
| P.1 Frame | 2026-10-09 | classified ISSUE (possible Spec Amendment); TODO + question file created on `main`; value triage recorded, decision PENDING |
| P.2 Interrogate (<n> questions) | | |
| P.3 Answer (<n> answered) | | |
| P.4 Draft spec / triage / baseline / scope | | |
| P.5 Self-consistency (FEATURE/CROSS-CUTTING) | | |
