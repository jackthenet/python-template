---
name: git
description: "Cross-cutting git operations for the Spec-TDD workflow: creating change branches and worktrees per change type (Phase 1), opening PRs (Phase 6), and post-merge cleanup (verify merge on main, remove worktree, delete local + remote branches). Use when a phase skill delegates a git operation, or when inspecting, managing, or recovering worktrees, branches, or PRs."
---

# Git

Cross-cutting git operations for the Spec-TDD workflow. This skill owns the **how** — commands, procedures, edge cases. The **what/where** — layout, naming, the primary worktree's role, safety rules — lives in the "Git Worktrees" section of `AGENTS.md`. Read that section first; this skill assumes its conventions.

## When to Use

- Phase 1 (specify) delegates: create the change branch and its worktree (per change type).
- Phase 6 (review) delegates: open the PR for the change branch.
- After a PR is merged (human governance): post-merge cleanup.
- Any time you need to inspect or recover worktree/branch state.

## Execution Context (Subagents)

Per "Phase Execution (Subagents)" in `AGENTS.md`:
- **Create change worktree** — orchestrator (Phase 0), not a subagent.
- **Create PR** — runs inside the Phase 6 (review) subagent.
- **Post-merge cleanup** — runs in a **new subagent** (a workflow step launched by the orchestrator after the human merges the PR).
- **Inspect / recover** — orchestrator or any step subagent, as needed.

## Conventions (from AGENTS.md — assumed)

- Primary worktree (the repo) is always on `main`, never switched.
- Change worktrees: `../<repo-name>-worktrees/<type>/<name>/` — `<type>` is `feature`, `issue`, `crosscut`, `refactor`, or `chore`; `<name>` is the plain change name.
- Branch naming: `feature/<name>`, `issue/<name>`, `crosscut/<name>`, `refactor/<name>`, `chore/<name>`.
- Each change branch lives in exactly one worktree at a time.
- Never check out a change branch in the primary worktree.

## Todo

Per the AGENTS.md Todo Tracking Discipline: mark the Post-merge cleanup item `in_progress` after the human merges the PR; `completed` when the worktree is removed and the local + remote branches are deleted.

## Operations

### Create change worktree (Phase 1)

Run from the primary worktree:

```bash
git worktree add ../<repo-name>-worktrees/<type>/<name> -b <type>/<name> main
```

- `<type>` is the change type (`feature`, `issue`, `crosscut`, `refactor`, `chore`); `<name>` is the plain change name; the branch is `<type>/<name>`.
- The parent directory is created automatically if it doesn't exist.
- If the branch already exists (re-entering the change), omit `-b`:
  `git worktree add ../<repo-name>-worktrees/<type>/<name> <type>/<name>`
- All subsequent work for the change (Phases 1–6) happens inside the change worktree.

### Create PR (Phase 6)

```bash
gh pr create --head <type>/<name> --base main --title "<title>" --body "<body>"
```

- Present the PR for human review/merge, then STOP. Do NOT merge it (human governance).

### Post-merge cleanup

After the human merges the PR:

1. Verify the merge landed on `main` (from the primary worktree):
   ```bash
   git fetch
   git log main --oneline -5
   ```
   The merge commit must be present.
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
- **Change re-entry**: if a change is re-opened after cleanup, re-create its worktree per "Create change worktree" (with `-b` for a new branch, or without `-b` if the branch still exists).

## Rules

- Never check out a change branch in the primary worktree.
- Never create two worktrees for the same change branch.
- Do NOT merge PRs (human governance).
- Do NOT force-remove worktrees (`git worktree remove --force`) or force-delete branches (`git branch -D`) on unmerged changes.
- After cleanup: `git worktree list` shows only the primary worktree, and `git branch -a` shows only `main` (and its remote).
