# Verification: file-management

## Change Type

- **Type:** FEATURE
- **Classified:** Phase 0 (orchestrator), 2026-08-16
- **Rationale:** Adds externally observable behavior/capability (file upload/download, user avatars, file metadata, storage abstraction, size/type validation) not covered by any approved spec in `docs/specs/`. Single new backend feature (like `mail`, `logging`); does not span two or more existing features, so not CROSS-CUTTING.
- **Branch:** `feature/file-management`
- **Worktree:** `../python-template_kopie-worktrees/feature/file-management`

## Governance Delegation (human authority)

- **Delegation:** The human governance authority (the user) explicitly delegated their spec-approval authority for the file-management spec PR to the agent: "auto approve the pr at the end of phase 1 by my authority" (2026-09-13).
- **Execution:** At S1.4 (end of Phase 1), the spec PR is approved AND merged via `gh pr merge` (through the GitHub PR process — NOT a direct push to `main`, which does not constitute approval per the Spec Approval Gate).
- **Note:** This exercises the human-controls-WHAT boundary by explicit delegation rather than by review. Recorded for traceability.

## Phase 1 — Spec approval

- **PR:** #24 — `spec(file-management): user file storage feature specification` (https://github.com/jackthenet/python-template/pull/24)
- **Merged:** 2026-09-13 (squash merge via `gh pr merge 24 --squash`)
- **Merge commit (on `main`):** `d0c99e1428121ac7be5f92c907266eeba0eba84e`
- **Merge-landed verification:** `git log origin/main -- docs/specs/file-management.md` shows commit `d0c99e1` touching the spec file; the spec file (715 lines) is present on `origin/main`. (The pre-merge commit `f4e45fc` is not a SHA ancestor of `origin/main` because the merge was a squash merge — the content landed via the new squash commit.)
- **CI checks:** `spec-validation` SUCCESS, `tests` SUCCESS (both completed before merge).
- **Approval authority:** executed on the explicit human governance delegation recorded in the "Governance Delegation (human authority)" section above ("auto approve the pr at the end of phase 1 by my authority", 2026-09-13). The approval was performed through the GitHub PR process (PR → merge), not a direct push to `main`, satisfying the Spec Approval Gate.
- **Note:** self-approval via `gh pr review --approve` is rejected by GitHub for the PR author's own PR; the merge step (with all CI checks green) constitutes the approval execution on the delegation.

## Phase 3 — Test & RED

- **Step:** S3.1 (derive tests), 2026-09-13.
- **Tests derived** from `docs/specs/file-management.md` (test strategy table, 90 test functions):
  - `tests/acceptance/filemanagement/test_filemanagement.py` — AC-001 .. AC-055 (55 acceptance tests).
  - `tests/property/filemanagement/test_filemanagement_properties.py` — INV-001 .. INV-008 (8 property tests, Hypothesis).
  - `tests/unit/filemanagement/test_filemanagement_edges.py` — EDGE-001 .. EDGE-019 (19 unit tests).
  - `tests/contract/filemanagement/test_filemanagement_contracts.py` — NFR-001 .. NFR-005 (5 contract tests).
  - `tests/integration/filemanagement/test_filemanagement_integration.py` — 3 integration tests (full file lifecycle, avatar lifecycle with variants, concurrent same-key upload).
  - `tests/filemanagement_test_helpers.py` — shared helpers (content factories, wiring helpers, fault-injection doubles).
  - Per-directory `conftest.py` in the five `filemanagement` test directories (shared `events` / `registry` / `repo` / `backend` / `service` fixtures).
- **Test-name check:** every written test function name matches the spec's test strategy table exactly (90/90; verified by diffing `def test_*` names in the written files against the spec table).
- **RED state confirmed:**
  - `uv run pytest tests/acceptance/filemanagement tests/property/filemanagement tests/unit/filemanagement tests/contract/filemanagement tests/integration/filemanagement -q` → **exit code 4** (collection error), failing with `ModuleNotFoundError: No module named 'backend.filemanagement'` (the feature is unimplemented; the helpers import the feature public API at module level).
  - `uv run pytest --collect-only` on the same paths shows the same `ModuleNotFoundError` at conftest import.
- **Ruff:** `uv run ruff check` on all six new file-management test paths → **All checks passed** (exit 0). Repo-wide `uv run ruff check .` additionally reports 23 pre-existing `I001` import-sort errors in `tests/**/mail/**` that also exist on `main` (out of scope for this step; recorded for the verify phase).
- **Traceability:** `docs/verification/traceability.md` gained a **File Management Matrix** section mapping every REQ/AC/INV/EDGE/NFR to its test with status `RED`.

## Evidence

- Phase 1 (Specify): spec committed, PR #24 opened + merged on human delegation (see "Phase 1 — Spec approval").
- Phase 3 (Test & RED): 90 tests derived from the spec, RED confirmed (`ModuleNotFoundError: backend.filemanagement`, pytest exit 4), ruff clean on the new files (see "Phase 3 — Test & RED").
