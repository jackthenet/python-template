# Questions: map-default-drop-shift

One question file per change, created at **P.1 Frame** from this template and named `<change-name>.md`. It replaces the retired central `AI_Questions.md` (archived at `docs/questions/archive-AI_Questions.md`).

- **Change:** map-default-drop-shift (ISSUE — may need a Spec Amendment to `docs/specs/structure-map.md` first)
- **TODO file:** `docs/todo/map-default-drop-shift.md`
- **Spec:** n/a (defect against `docs/specs/structure-map.md` REQ-014 / AC-014)
- **Opened:** 2026-10-09
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

_None yet — **P.2 Interrogate has not run for this change.** It is the next autonomous step for this change; the value-triage decision (implement / merge / drop) in `docs/todo/map-default-drop-shift.md` must be recorded before P.4 creates the branch and worktree._

## Late questions (Phases 2–6)

_none_
