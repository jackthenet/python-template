# Questions: docstrings-tests

One question file per change, created at **P.1 Frame** from this template and named `docstrings-tests.md`. It replaces the retired central `AI_Questions.md` (archived at `docs/questions/archive-AI_Questions.md`).

- **Change:** docstrings-tests (DOCS/CHORE)
- **TODO file:** `docs/todo/docstrings-tests.md`
- **Spec:** n/a
- **Opened:** 2026-10-07
- **Status:** OPEN  <!-- OPEN | ALL ANSWERED -->
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

_None yet — **P.2 Interrogate has not run.** It may not run before `ruff-d-docstrings` merges, because that change owns `[tool.ruff.lint] select` and the `per-file-ignores` entry this change removes; interrogating earlier would ask about a config state that is about to move._

Answers already inherited from the parent change (`docs/questions/ruff-d-docstrings.md`, 2026-10-07 — these are settled and must not be re-asked here):
- **Q-29 / Q-4:** test docstrings are mandatory and enforced; the `tests/` backfill + gate is this change.
- **Q-3 / Q-23:** `scripts/*`, `migrations/*`, `.github/*` stay permanently exempt — this change touches `tests/*` only.
- **Q-1 / Q-2:** `"D"` is in `select` with `convention = "google"`; Google sections are the house style.
- **Q-7:** the config edit lands last, so `lint.yml` is green at every commit.
- **Q-15:** the no-filler rule is a reviewer rule + Phase 6 checklist, not a script.
- **Q-26:** a docstring that reveals a wrong claim becomes a finding + a separate ISSUE TODO.
- **Q-27:** DOCS/CHORE → no version bump.

Questions P.2 is expected to interrogate (not yet recorded as Q-entries): how `tests/*` is gated (full `D` vs missing-docstring codes only), the increment shape across the six test trees, whether every `test_*` must cite an ID or only acceptance tests, how the cited ID is checked against what the test asserts, and whether `tests/architecture/` + `tests/tooling_test_helpers.py` helpers are exempt.

## Late questions (Phases 2–6)

<questions discovered after the change entered the workflow; same entry format, Step field set to the step that found it>
