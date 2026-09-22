# Verification: user-roles-permissions

## Change Type: CROSS-CUTTING

- **Date:** 2026-07-10
- **Branch:** `crosscut/user-roles-permissions`
- **Worktree:** `../python-template_kopie-worktrees/crosscut/user-roles-permissions`

## Classification Rationale

The change is a **new shared capability** (a permissions/authorization system) that
intentionally spans two or more features:

- **usermanagement** — role model and role assignment (existing: `"admin"` / `"member"`
  roles, `set_role`, `LastAdminError` guard).
- **New shared permissions feature** — per-feature/action permission model and the
  backend permission-check capability that other features depend on.

It is not an ISSUE (no deviation from approved spec behavior), not a REFACTOR
(externally observable behavior is added), and not a DOCS/CHORE (behavior changes).

## Request (as received)

> ## User roles & permissions
> Roles such as Admin/User
> Permissions per feature/action
> Role assignment
> Permission checks in the backend

## Phases

### Phase 1: Specify — COMPLETE

- **Spec:** `docs/specs/user-roles-permissions.md` (commit `34227d0`), 13 sections, 106 stable IDs (29 REQ, 40 AC, 6 INV, 26 EDGE, 5 NFR).
- **Steps:** S1.1 Interrogate (33 questions, Q-66…Q-98, all answered) → S1.2 Draft spec → S1.3 Verify self-consistency (all 8 checklist items pass; 1 fix applied in-spec) → S1.4 Present for approval.
- **PR:** #51 open (https://github.com/jackthenet/python-template/pull/51), `crosscut/user-roles-permissions` → `main`, **NOT merged** (`mergedAt: null`).

### Spec Approval (cached — verified once, before Phase 2)

- **Status:** HUMAN APPROVED (pre-approved).
- **Basis:** User governance directive **Q-99** (`AI_Questions.md`): the user pre-approves the spec PR (going to bed) and instructs NOT to merge it; the pre-approval satisfies the approval gate (a human-governance override of the merge-based entry check), so Phase 2 proceeds on the pre-approval WITHOUT the merge.
- **Approve action:** `gh pr review --approve 51` attempted, blocked by GitHub self-approval policy ("Can not approve your own pull request") — the documented pre-approval Q-99 governs; the spec is treated as HUMAN APPROVED regardless.
- **PR:** #51 (open, unmerged; the user will merge it later).
- **Date:** 2026-07-10.

### Phase 2: Decompose — COMPLETE

- **Steps:** S2.1 Create ADRs → S2.2 Decompose into task DAG.
- **ADRs (7):** ADR-069 (permissions feature placement), ADR-070 (shared enforcement plumbing, no circular imports), ADR-071 (enforcement wiring via trailing `principal` param + decorator, standalone mode), ADR-072 (multi-role user-management amendment), ADR-073 (session validation via structural `SessionLookup` seam), ADR-074 (dynamic role→permission mapping), ADR-075 (fail-closed security posture). Commit `572637d`.
- **Task DAG:** `docs/tasks/user-roles-permissions.tasks.json` — 14 tasks (T-001…T-014), grouped by affected feature (shared plumbing, usermanagement, permissions, per-feature enforcement, cross-cutting integration), covering all 29 REQs + 40 ACs (77 tests), acyclic + gate-satisfiable. Copied to `.github/task-runner/tasks.json`. Commit `a07651f`.
- **House-format refinements:** `tests_to_create` + red/green use `file::function` paths (name collision + same-directory multi-task); red/green are targeted (not the full suite).
