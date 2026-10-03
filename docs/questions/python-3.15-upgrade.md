# Questions: python-3.15-upgrade

One question file per change, created at **P.1 Frame** from this template and named `python-3.15-upgrade.md`. It replaces the retired central `AI_Questions.md` (archived at `docs/questions/archive-AI_Questions.md`).

- **Change:** python-3.15-upgrade (DOCS/CHORE, provisional)
- **TODO file:** `docs/todo/python-3.15-upgrade.md`
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

_None yet — **P.2 Interrogate has not run**, and must not run before the item's trigger fires: CPython 3.15 final **and** a final `pydantic` release shipping a cp315 wheel (see `Depends on:` in the TODO). The interrogation will re-measure wheel availability first, since the answers recorded for `python-3.15` on 2026-10-03 are only valid for that date._

## Late questions (Phases 2–6)

<questions discovered after the change entered the workflow; same entry format, Step field set to the step that found it>
