---
name: git
description: "Cross-cutting git operations for the Spec-TDD workflow: committing the planning records (docs/todo/, docs/questions/) and their status advances directly to main from the primary worktree, creating change branches and worktrees per change type (at P.4), detecting a cleared human gate so a WAITING change can resume, opening PRs (Phase 6), and post-merge cleanup (verify merge on main, remove worktree, delete local + remote branches). Use when a phase skill delegates a git operation, or when inspecting, managing, or recovering worktrees, branches, or PRs."
---

# Git

Cross-cutting git operations for the Spec-TDD workflow. This skill owns the **how** — commands, procedures, edge cases. The **what/where** — layout, naming, the primary worktree's role, safety rules — lives in the "Git Worktrees" section of `AGENTS.md`. Read that section first; this skill assumes its conventions.

## When to Use

- **Orchestrator (Phase P and every later status advance)** delegate: commit the change's planning records (`docs/todo/<name>.md`, `docs/questions/<name>.md`) and every `Status:` advance through `MERGED` directly to `main`.
- **P.4 (specify)** delegates: create the change branch and its worktree (per change type) — the worktree is created at P.4, after the questions are answered, NOT at Phase 0/Phase 1.
- Phase 6 (review) delegates: open the PR for the change branch.
- After a PR is merged (human governance): post-merge cleanup.
- Multi-change scheduling: detect that a WAITING change's gate has cleared and resume it.
- Any time you need to inspect or recover worktree/branch state.

## Execution Context (Atomic Step, Synchronous Subagent)

Per "Phase Execution (Atomic Steps, Synchronous Subagents)" in `AGENTS.md`:
- **Commit planning artifacts and status advances (orchestrator, `main`)** — orchestrator only, always in the **primary worktree**, committed directly to `main`; covers the creation at P.1–P.3 **and every TODO `Status:` advance through `MERGED`**.
- **Create change worktree (P.4)** — performed by the **P.4 Draft step subagent** as its first action (this skill owns the how); the orchestrator does NOT create it. It runs at P.4, after the questions are answered.
- **Detect a cleared gate** — orchestrator, between steps, when scheduling which change to run next.
- **Create PR** — runs inside the Phase 6 (review) subagent (atomic step **S6.4**).
- **Post-merge cleanup** — runs in a **new, synchronous subagent** (atomic step **S7.1**, launched by the orchestrator after the human merges the PR).
- **Inspect / recover** — orchestrator or any step subagent, as needed.

Subagents are always **synchronous** (never background); the workflow waits for each to complete and return its handoff.

## Conventions (from AGENTS.md — assumed)

- Primary worktree (the repo) is always on `main`, never switched.
- Change worktrees: `../<repo-name>-worktrees/<type>/<name>/` — `<type>` is `feature`, `issue`, `crosscut`, `refactor`, or `chore`; `<name>` is the plain change name.
- Branch naming: `feature/<name>`, `issue/<name>`, `crosscut/<name>`, `refactor/<name>`, `chore/<name>`.
- Each change branch lives in exactly one worktree at a time.
- Never check out a change branch in the primary worktree.

## Todo

Per the AGENTS.md Todo Tracking Discipline: mark the Post-merge cleanup item `in_progress` after the human merges the PR; `completed` when the worktree is removed and the local + remote branches are deleted. Each in-flight change has **its own todo set**, and at most **one item per change** is `in_progress` — a WAITING change's step stays `in_progress` with an `activeForm` naming the wait (e.g. "waiting for spec PR merge").

## Atomic Steps

The git skill's phase steps are decomposed into two atomic steps (S6.4 Create PR, S7.1 Post-merge cleanup). Each has a **single objective**, **inputs**, **outputs**, and a **done criterion**. The task-definition points at the specific step to execute; the subagent executes exactly that step (and only that step).

### S6.4 Create PR

- **Objective:** Open a PR for the change branch to `main` and present it for human review/merge (then STOP — do NOT merge it).
- **Inputs:** the change branch (with the review report clean).
- **Outputs:** a PR open for the change branch to `main`.
- **Done-criteria:** a PR is open for the change branch to `main` (via `gh pr create --head <type>/<name> --base main`); the PR is presented for human review/merge; the PR is NOT merged (human governance).

### S7.1 Post-merge cleanup

- **Objective:** After the human merges the PR, verify the merge is reachable from `origin/main` (after `git fetch`), remove the worktree, and delete the local + remote branches.
- **Inputs:** the merged PR.
- **Outputs:** the merge verified as reachable from `origin/main` (after `git fetch`); the worktree removed; the local + remote branches deleted.
- **Done-criteria:** the merge commit is verified reachable from `origin/main` (run `git fetch` first, then `git merge-base --is-ancestor <merge-commit> origin/main` — do NOT rely on the local `main` ref, which may lag); the worktree is removed (`git worktree remove`); the local branch is deleted (`git branch -d`); the remote branch is deleted (`git push origin --delete`); `git worktree list` shows only the primary (`main`) worktree.

## Operations

### Commit planning artifacts and status advances (orchestrator, `main`)

`docs/todo/<name>.md` and `docs/questions/<name>.md` are **planning records, not normative**: they carry no approval gate, so they are committed **directly to `main`**, always from the **primary worktree**. This operation covers **every commit of** those two files: P.1 creates them, **P.2 records the questions (written by the P.2 step subagent in the primary worktree)**, P.3 records the answers, and the orchestrator then commits **every `Status:` advance** — `PREPARING` → `QUESTIONS-ANSWERED` → `READY` → `IN-WORKFLOW` → `WAITING` → `MERGED` — plus any late (`Phases 2–6`) question a step returned in its handoff (AGENTS.md, "Planning records (owner: the orchestrator)"):

```bash
git add docs/todo/<name>.md docs/questions/<name>.md
git commit -m "chore(<name>): prepare"          # P.1–P.3
git commit -m "chore(<name>): status <STATUS>"  # every later Status: advance
```

- They are the **only** files the workflow may commit directly to `main`. NOTHING else — no spec, no verification record, no source, no test — may be committed directly to `main`; it reaches `main` only through a merged PR.
- **Both paths are written only in the primary worktree**: P.1–P.3 and every `Status:` advance by the **orchestrator**, and **P.2 by its step subagent** (which runs in the primary worktree because no change worktree exists yet, and writes only the question file). **No write to them may happen inside a change worktree** (a later step reports the gate / the late question in its handoff instead), and a change branch and its PR therefore never contain them (the branch carries the P.1–P.3 copies inherited at P.4 but never modifies them). Because the change branch never modifies those paths, a direct-to-`main` status update made while the change is in flight is never reverted when its PR merges.
- The change worktree is created afterwards, at **P.4**, from `main` — so the change branch already carries the TODO file and the answered questions **as they were at P.3**; its copy is never updated afterwards.

### Create change worktree (P.4)

Run from the primary worktree; the **P.4 Draft step subagent** performs it as its first action, at **P.4 Draft** (after the questions are answered):

```bash
git worktree add ../<repo-name>-worktrees/<type>/<name> -b <type>/<name> main
```

- `<type>` is the change type (`feature`, `issue`, `crosscut`, `refactor`, `chore`); `<name>` is the plain change name; the branch is `<type>/<name>`.
- The parent directory is created automatically if it doesn't exist.
- If the branch already exists (re-entering the change), omit `-b`:
  `git worktree add ../<repo-name>-worktrees/<type>/<name> <type>/<name>`
- All subsequent work for the change (**P.4** through Phase 6) happens inside the change worktree.
- Because the worktree branches from `main` at P.4, it carries the TODO file and the answered question file committed there at P.1–P.3.

### Detect a cleared gate (resume a WAITING change)

A change is **WAITING** while it sits on a human gate (S1.4 spec approval, S6.4 PR merge, or a `BLOCKED-USER` question). Between steps, check whether a WAITING change's gate has cleared, then launch a **fresh** subagent at its next atomic step:

```bash
git fetch
# spec-approval PR (S1.4) or change PR (S6.4): is the merge reachable from origin/main?
git merge-base --is-ancestor <merge-commit> origin/main   # exit 0 = cleared
```

- For a `BLOCKED-USER` gate: the change's `docs/questions/<name>.md` has **no** entry with `**Answer:** PENDING` (every entry `ANSWERED`) — then the answers are recorded and the step is relaunched once with the full answer set.
- Do NOT rely on the local `main` ref, which may lag; `git fetch` first.
- Never idle on a gate: while one change is WAITING, take the next ready step of another READY change (see "Multi-change scheduling (never idle)" in `AGENTS.md`).

### Create PR (Phase 6)

```bash
gh pr create --head <type>/<name> --base main --title "<title>" --body "<body>"
```

- Present the PR for human review/merge, then STOP. Do NOT merge it (human governance).

### Post-merge cleanup

After the human merges the PR:

1. Verify the merge is reachable from `origin/main` (run `git fetch` first, then `git merge-base --is-ancestor <merge-commit> origin/main`) — do NOT rely on the local `main` ref, which may lag (from the primary worktree):
   ```bash
   git fetch
   git merge-base --is-ancestor <merge-commit> origin/main
   ```
   The command must exit 0 (the merge commit is an ancestor of `origin/main`).
2. Remove the worktree:
   ```bash
   git worktree remove ../<repo-name>-worktrees/<type>/<name>
   ```
3. Delete the local branch:
   ```bash
   git branch -d <type>/<name>
   ```
4. Delete the remote branch:
   ```bash
   git push origin --delete <type>/<name>
   ```

### Inspect / recover

- `git worktree list` — after cleanup, only the primary (`main`) worktree should remain.
- `git worktree prune` — after a worktree directory was deleted manually.
- `git fetch --prune` — after remote branches were deleted on the server (removes stale remote refs).
- `git ls-remote --heads origin` — to see which remote branches actually exist.

## Edge Cases

- **Dirty worktree on remove**: `git worktree remove` fails if the worktree has uncommitted changes or commits not on any branch. Do NOT use `--force` on an unmerged change — force-removal is only permitted when the changes are intentionally discarded.
- **Remote ref already gone**: `git push origin --delete <branch>` errors with "remote ref does not exist" if the branch was already deleted on the server (e.g., GitHub auto-deletes merged branches). Not an error to fix — prune the stale ref: `git fetch --prune`.
- **Multi-ref delete partially fails**: `git push origin --delete a b c` reports per-ref errors; check `git ls-remote --heads origin` for what remains and delete the rest individually.
- **Branch checked out in a worktree**: `git branch -d` refuses to delete a branch that is current in any worktree — remove that worktree first.
- **Change re-entry**: if a change is re-opened after cleanup, re-create its worktree per "Create change worktree (P.4)" (with `-b` for a new branch, or without `-b` if the branch still exists).

## Rules

- Never check out a change branch in the primary worktree.
- Commit **directly to `main`** only for the planning records under `docs/todo/` and `docs/questions/` — their creation at P.1–P.3 and every `Status:` advance through `MERGED` — and only from the primary worktree. Everything else reaches `main` only through a merged PR.
- Never write `docs/todo/` or `docs/questions/` inside a change worktree: those paths are written only in the primary worktree — P.1–P.3 and every `Status:` advance by the orchestrator, and P.2 by its step subagent — so a change branch and its PR never contain them.
- Never create two worktrees for the same change branch.
- Do NOT merge PRs (human governance).
- Do NOT force-remove worktrees (`git worktree remove --force`) or force-delete branches (`git branch -D`) on unmerged changes.
- After cleanup: `git worktree list` shows only the primary worktree, and `git branch -a` shows only `main` (and its remote).
