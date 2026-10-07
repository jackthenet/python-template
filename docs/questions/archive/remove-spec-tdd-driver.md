# Questions: remove-spec-tdd-driver

One question file per change, created at **P.1 Frame** from this template and named `remove-spec-tdd-driver.md`. It replaces the retired central `AI_Questions.md` (archived at `docs/questions/archive-AI_Questions.md`).

- **Change:** remove-spec-tdd-driver (DOCS/CHORE)
- **TODO file:** `docs/todo/remove-spec-tdd-driver.md`
- **Spec:** n/a
- **Opened:** 2026-10-03
- **Status:** ALL ANSWERED  <!-- OPEN | ALL ANSWERED -->
- **Answer rounds:** 0 — P.2 recorded **0 questions needing user input**, so P.3 presented none (every interrogation point was closed from repository evidence; see the P.2 section).

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

**No question needs user input — 0 questions recorded, no `BLOCKED-USER`.** The change is a single-file deletion whose every open interrogation point is settled by repository evidence or by a decision already on record (the user's delete-not-update decision, the P.1 TODO scope, and `AGENTS.md`'s DOCS/CHORE gates). DOCS/CHORE has no 20-question floor. The interrogation result, the overlap check, and the points that were raised and closed from evidence are recorded below for P.4 and for the Phase 6 reviewer.

### Overlap check (P.2 requirement)

- **`docs/specs/` (13 files: authentication, event-bus, file-management, logging, logging-coverage, mail-service, search, session-management, settings, settings-coverage, user-management, user-roles-permissions, template).** No spec references `.pi/`, `pi-workflows`, or a workflow driver (`grep -rn "\.pi/" docs/specs` → no match; repo-wide `grep -rn "pi-workflows"` matches only the driver itself, `.pi/workflows/spec-tdd.workflow.ts:9,81`). No spec or REQ/AC requires the driver to exist, so deleting it contradicts no approved spec — the DOCS/CHORE classification holds (no reclassification to ISSUE/REFACTOR).
- **`docs/todo/` (2 files: `template.md`, `remove-spec-tdd-driver.md`).** `template.md` is the P.1 template, not a planned change; the only other TODO file is this change's own. **No other planned change overlaps** — nothing else deletes or updates `.pi/`, and no double work exists. `git worktree list` shows only the primary worktree and `git branch -a` only `main`/`origin/main`: no in-flight change can collide with this one.
- **`docs/questions/`**: `archive-AI_Questions.md` (retired central record) and `template.md` — neither is touched by this change; the archived-Q&A split was triaged as dropped and is explicitly not part of the deletion.

### What the interrogation checked (evidence, all answered without the user)

1. **What breaks if the file goes?** Nothing. `git ls-files .pi` lists exactly one tracked path — `.pi/workflows/spec-tdd.workflow.ts` — so it is the whole of the tracked `.pi/` tree.
2. **Does anything in `.pi/` depend on it?** No. The only other file on disk is `.pi/subagents.json`, confirmed gitignored (`.gitignore:234`, `git check-ignore -v` → `.gitignore:234:.pi/subagents.json`) and containing only pi's subagent runtime settings (`maxConcurrent`, `defaultMaxTurns`, `graceTurns`, retention, `abortAllOnInterrupt`, `midRunUpdates`) — zero occurrences of `spec-tdd`. It is pi's own state, not a protocol artifact, and stays.
3. **Does any tooling, CI or test reference it?** No. No `package.json`/`tsconfig.json`/`deno.json`/lockfile exists, so the driver's `@osolmaz/pi-workflows` import is resolved by pi's own workflow runtime, not by a project dependency — deleting the file leaves **no orphan dependency to clean up** and `deptry` (Python-only) is unaffected. `.github/workflows/` (lint, quality, spec-validation) contains no `.pi`, TypeScript, `tsc` or `deno` step; `.pre-commit-config.yaml` has no `.ts`/`.pi` hook or file filter; `grep -rn "\.pi\b|spec-tdd|workflows/" tests scripts` → no match, so no test or CI script asserts on the file or the directory. `mkdocs.yml` uses `docs_dir: userdocs`, and `userdocs/` never mentions the driver, so the site is unaffected.
4. **Does any config become dead once the only `.ts` file is gone?** No. `.editorconfig` has no `[*.ts]` section (only `*`, `*.md`, `*.py`, `*.{ps1,sh}`, `*.{yml,yaml,toml}`), there is no `.gitattributes`, `pyproject.toml` has no `.pi`/TypeScript entry, and `.vscode/` (launch.json, settings.json) does not reference it. The deletion is therefore a **one-path diff with no dependent cleanup**.
5. **Which mentions remain, and are they correct afterwards?** Only historical records: `docs/verification/prepared-workflow.md:81` (the follow-up list), `:347`, `:383` (F-10), `:567` (final verdict), plus this change's TODO file. Those describe what was true at the time of that change and stay unchanged (TODO "Out of scope"); a repo-wide grep will still show the name inside `docs/verification/`, which the TODO's acceptance signal already accounts for.

### Points raised and closed from evidence (not asked)

- **Delete outright vs. archive the driver** (the repo does archive retired artifacts — `docs/questions/archive-AI_Questions.md`). Closed: the TODO goal is that *no artifact in the repository still describes the pre-Phase-P protocol* (`docs/todo/remove-spec-tdd-driver.md:17`); archiving a stale driver would keep exactly that contradicting artifact in the tree, and `git` history preserves it. The user's decision (delete, not update) plus the goal statement settle it.
- **Should `docs/verification/prepared-workflow.md:79-81` (the Follow-ups list) be annotated to mark the three items dropped/closed?** Closed: that file is the merged change's frozen verification record and rewriting it is explicitly out of scope (`docs/todo/remove-spec-tdd-driver.md:29`); the closure of follow-up #3 by deletion and the drop of the other three are recorded in **this** change's `docs/verification/remove-spec-tdd-driver.md` at P.4, which is where the workflow puts such records.
- **Keep `.pi/` itself?** Closed: `.pi/subagents.json` is live pi state the workflow depends on (AGENTS.md mandates synchronous subagents) and is gitignored; the directory keeps existing locally, and git simply stops tracking a directory that has no tracked files left.
- **Version bump?** Closed by `AGENTS.md` (Versioning): DOCS/CHORE → no bump; no Phase 6 bump commit.
- **Phase 5 depth for a zero-Python-file change.** Closed by `AGENTS.md` Phase Matrix (DOCS/CHORE → "Light: lint/types where applicable") and Phase 5 item 16: the evidence is the scope proof (`git diff --name-status` shows exactly one deleted `.ts` path, no `src/`, `tests/`, `pyproject.toml`, `.github/` change) plus lint/types where applicable — the TODO's "lint, types and the test suite are unchanged from `main`" is satisfied by that scope proof, since no Python or test path is touched. Not a user decision.
- **Empty `.pi/workflows/` directory.** Closed: git does not track empty directories, so the path disappears from the tree with no extra step; other worktrees prune theirs on checkout.

### For P.4 (scope record) — nothing outstanding

The scope is already concrete enough to draft without user input: delete `.pi/workflows/spec-tdd.workflow.ts` (187 lines, the only tracked `.pi` file), record the no-behavior-delta proof (no consumer, no CI/test/config reference — items 1–4 above), and record the three `prepared-workflow` follow-ups as dropped with their triage reasons. No question blocks the change; it may go straight to P.4.

## Late questions (Phases 2–6)

<questions discovered after the change entered the workflow; same entry format, Step field set to the step that found it>
