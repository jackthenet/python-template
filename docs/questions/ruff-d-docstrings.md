# Questions: ruff-d-docstrings

One question file per change, created at **P.1 Frame** from this template and named `ruff-d-docstrings.md`. It replaces the retired central `AI_Questions.md` (archived at `docs/questions/archive-AI_Questions.md`).

- **Change:** ruff-d-docstrings (DOCS/CHORE)
- **TODO file:** `docs/todo/ruff-d-docstrings.md`
- **Spec:** n/a
- **Opened:** 2026-10-04
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

_None yet — **P.2 Interrogate has not run**. It is gated behind `pyproject-tooling-gaps`, which owns the same `[tool.ruff.lint] select` list and decided (Q-9) that this backfill is a separate item. The interrogation must at least settle: the rule subset (`D1xx` only vs full `D`), the increment shape (per feature vs one sweep), whether `__init__` re-exports and test modules are in scope, and how the gate lands without ever turning `lint.yml` red._

## Late questions (Phases 2–6)

<questions discovered after the change entered the workflow; same entry format, Step field set to the step that found it>
