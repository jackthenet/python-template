# AI Questions

Persistent record of questions that arise during the workflow and need user input. This file is the **single source of truth** for unresolved decisions and user answers, so they are not lost between steps.

A step subagent records a question here when it returns `BLOCKED-USER`. The orchestrator presents the question to the user, records the answer here, marks it **incorporated**, and relaunches the same step with the answer. The workflow never proceeds past a `BLOCKED-USER` step until the user has answered.

## When questions are created

- **MAY:** any atomic step, when it meets an ambiguity, a missing requirement, or a decision that requires user input.
- **MUST:** the **Interrogate** step (**S1.1**, Phase 1) — it MUST create a question for every ambiguity, missing requirement, edge case, and scope boundary it identifies. Any step that returns `BLOCKED-USER` MUST have its questions recorded here.

## Entry format

Each question is a section with the following fields:

```markdown
## Q-<n> — <short title>
- **Step:** <step ID + phase> (e.g., S1.1 Interrogate — Phase 1)
- **Change:** <change name + type>
- **Why needed:** <why this question is needed — the ambiguity / missing requirement / decision>
- **Context:** <the available context at the time — what the step had learned>
- **Question:** <the question for the user>
- **Answer:** <the user's answer> (or **PENDING**)
- **Date:** <YYYY-MM-DD>
- **Status:** PENDING | ANSWERED
- **Incorporated:** <yes/no — whether the answer has been folded into the workflow (spec, tests, implementation)>
```

## Questions

(no questions yet)
