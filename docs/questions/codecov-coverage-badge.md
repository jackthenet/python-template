# Questions: codecov-coverage-badge

One question file per change, created at **P.1 Frame** from this template and named `codecov-coverage-badge.md`. It replaces the retired central `AI_Questions.md` (archived at `docs/questions/archive-AI_Questions.md`).

- **Change:** codecov-coverage-badge (DOCS/CHORE)
- **TODO file:** `docs/todo/codecov-coverage-badge.md`
- **Spec:** n/a
- **Opened:** 2026-10-04
- **Status:** OPEN  <!-- OPEN | ALL ANSWERED — set OPEN by the orchestrator at P.1; ALL ANSWERED once every question in this file has an answer (the orchestrator records it together with the `QUESTIONS-ANSWERED` TODO advance) -->
- **Answer rounds:** 0  <!-- P.2 Interrogate has not run yet -->

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

**P.2 Interrogate has not run yet** — the change was framed at P.1 on 2026-10-04 from the `update-readme` Q-3 = (d) answer. The batch is not recorded yet, so no question is presented to the user.

Open points the interrogation must cover (recorded here as a pointer, **not** as questions — P.2 writes the real entries with Step/Why/Context): whether Codecov vs an alternative (e.g. a coverage artifact job, or no service at all), the `CODECOV_TOKEN` secret for a private repo, the report format (`--cov-report=xml`), whether the upload may fail the `Quality` run, the action pin/version, whether the badge lands in this change or after the first successful upload, and the interaction with `update-readme`'s badge row.

## Late questions (Phases 2–6)

<questions discovered after the change entered the workflow; same entry format, Step field set to the step that found it>
