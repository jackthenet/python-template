# ADR-085: `STRUCTURE.md` as a committed generated artifact with a check-only local hook (no CI gate)

## Status
Accepted

## Context
The repository's documented architecture is false. `AGENTS.md` *Project Structure* (measured at
`AGENTS.md:1120` on this branch) prescribes `src/frontend/` and per-feature `model/` + `services/`
subdirectories; none of it exists — there is no `src/frontend/` directory, no feature has a `model/`
or `services/` subdirectory, and the only nested directory under `src/backend/` is
`src/backend/filemanagement/assets/` (an asset directory, not an architecture layer). Every change
re-walks the tree to answer "which modules exist and what do they expose", and the answer is never
recorded. Measured at this branch head (`aabf878`, `git ls-files`): **595 tracked files, 339 `.py`,
84 `.py` under `src/`, 70 `__init__.py`**, and **118 Packages-scope modules** (84 `src/` + 3
`scripts/` + 3 `migrations/` + 17 `conftest.py` + 11 `*_test_helpers.py`).

Two facts make this a decision and not a restatement of the spec:

1. **No repo-owned generated committed artifact exists.** `uv.lock` is the only committed generated
   file, it is produced by an external tool, and nothing checks its freshness (CI runs
   `uv sync --only-group dev`, not `--locked`). A committed artifact produced by the repository's own
   generator, whose freshness is machine-checkable, is a new element in this repository.
2. **The repository's quality model is the opposite of advisory.** There are **12 CI jobs across 3
   workflows** (`lint.yml` 1, `quality.yml` 8, `spec-validation.yml` 3) and two hooks in the
   `repo: local` block (`deptry` at the `pre-commit` stage, `mkdocs-build` at `pre-push`); the two
   formatter hooks (`ruff-check --fix`, `ruff-format`) **rewrite files** during a commit. A hook that only *checks*, and a mechanism that
   is deliberately **not** a CI job and **not** a workflow gate, depart from that convention on both
   axes at once — that departure has to be recorded, because the default assumption in this repo is
   "if it matters, it is a gate".

The host environment adds a constraint the mechanism must absorb: this repository has **no
`.gitattributes`** and `git config core.autocrlf` is **`true`** on the development host, so a
committed LF blob is checked out with CRLF on Windows. A naive byte-exact freshness check would
report a freshly committed map as stale on every Windows checkout.

## Decision
`STRUCTURE.md` at the repository root is a **committed artifact produced only by the generator**, and
its freshness is enforced by exactly one **local, check-only** mechanism, with **no CI job and no
workflow gate**:

- **Committed, generated, never hand-edited** (REQ-021). Its content is the fresh render for the
  commit it is recorded at; a hand-edit or a leftover conflict marker is a staleness signal, not a
  state to repair by hand (EDGE-010).
- **One enforcement point**: a `repo: local` pre-commit hook `structure-map-check` running
  `uv run python scripts/make_map.py --check` with `language: system`, `pass_filenames: false`,
  `stages: [pre-commit]`, `files: \.py$` (REQ-023). It **never rewrites the map** — it exits `1` and
  prints one line naming the regeneration command (REQ-005).
- **Advisory, never a gate** (REQ-026): no phase gate, todo status, handoff field or prohibition
  depends on the map; no GitHub Actions workflow mentions `make_map.py` (AC-023, AC-026). The only
  workflow-side obligation is documentation — the regeneration and conflict rules appear in the skill
  and in the `AGENTS.md` pointer line (REQ-022, REQ-027).
- **Byte-exact check with one normalisation**: `--check` compares the whole file after `\r\n` → `\n`
  normalisation and nothing else (REQ-005, INV-004); generate mode always writes LF (REQ-019).
- **Determinism is normative, because it is what makes a byte-exact check meaningful**: sorted
  `--root`-relative POSIX paths, `ast.unparse`-canonical signatures, LF newlines, no trailing
  whitespace, exactly one final newline, no timestamp / generator-version banner / absolute path /
  host or user name (REQ-008, REQ-018, REQ-019, REQ-020; INV-001, INV-003, INV-006; AC-019, AC-020).
- **Conflict policy**: on a merge conflict in `STRUCTURE.md`, take either side and regenerate —
  never hand-merge the generated file (REQ-027).

## Consequences
- **Positive:** the documented layout and the real layout agree at a commit and stay agreeable,
  because the real one is now machine-readable and machine-checkable (G-4); an agent answers
  "which modules exist, what do they expose, what is their signature" by reading one file instead of
  walking 339 (G-3); the artifact is reviewable in a PR diff, unlike a generated site; the generated
  file passes the existing `trailing-whitespace` and `end-of-file-fixer` hooks unchanged (INV-006).
- **Costs / accepted risks:**
  - **Staleness can reach a pushed commit.** The hook is local: `git commit --no-verify`, a CI-only
    edit, or a clone without `pre-commit install` bypasses it, and no CI job catches it afterwards.
    This is chosen knowingly — the map is documentation-grade, not correctness-grade, and a wrong map
    costs a re-read, not a broken build (REQ-026).
  - **A per-change tax and a guaranteed conflict point.** Any change that adds, deletes or renames a
    `.py` file also changes `STRUCTURE.md` (the hook fires on `\.py$`), so parallel worktrees — three
    change worktrees are in flight at measurement — will conflict on it. The resolution is
    regeneration, and it is cheap and lossless precisely because the file is never hand-edited
    (REQ-027, EDGE-010).
  - **Untracked files leak into the committed map.** The file set is index *plus* untracked-but-not-ignored
    (REQ-003), so a file that is generated-and-never-committed makes the committed map stale for the
    next clone (EDGE-009); regeneration is the fix, and the skill states it.
  - **Size ceiling.** NFR-002 caps the map at ≤ 2 000 lines; the P.5 projection for the base-commit
    tree was ≈1 875 (margin ≈125). The tree has since grown (339 `.py` vs 324, 118 Packages-scope
    modules vs 117), so the margin is thinner than the spec states; the per-class field cap (REQ-017)
    is the safety valve and Phase 5 records the actual line count.
- **Sequencing:** `STRUCTURE.md` is generated **last** inside this change (after the generator, the
  skill, the hook and the `AGENTS.md` edits exist), so the committed map reflects the post-change
  tree. The regeneration-after-merge condition spec §14 attaches to `chore/remove-spec-tdd-driver`
  (PR #62) is **already satisfied**: that PR is merged (`a2000c2`, reachable from this branch) and
  `.github/` now holds 9 tracked files, so the counts the map will report already include it.
- **Numbering:** ADR-081 stays unclaimed on disk for `api-keys` (`docs/todo/api-keys.md:64`), and
  **ADR-083/ADR-084 are authored on the in-flight branch `crosscut/settings-public-registry-setter`**
  (`ADR-083-public-install-operation-feature-singletons.md`,
  `ADR-084-two-guards-singleton-slot-tid251-scan-test.md`) — verified with
  `git ls-tree -r --name-only crosscut/settings-public-registry-setter docs/decisions`. This change
  therefore starts at **ADR-085**; the highest ADR file on this branch before it is ADR-082.

## Alternatives Considered
- **A CI job running `make_map.py --check`** — rejected (REQ-023). `STRUCTURE.md` is one root file
  that every `.py`-adding change invalidates; with several worktrees in flight a CI freshness gate
  would fail unrelated PRs on another change's staleness, and the fix would be a rebase-and-regenerate
  loop on a file nobody edited. The local hook catches the same mistake at the moment it is made.
- **Auto-regenerating hook (the `ruff-check --fix` pattern)** — rejected. It would rewrite ≈1 800
  generated lines inside a commit the author never reviewed, and it would erase the exact signal the
  check exists to produce: a hand-edited map or a map with conflict markers (EDGE-010) would be
  silently overwritten instead of reported.
- **A workflow gate ("the map must be fresh before Phase 5")** — rejected (REQ-026). It adds a
  failure mode with no correctness benefit, and it would collide with the in-flight
  `value-triage-gate` change, which rewrites the Phase P table and the Workflow Diagram (spec §14).
- **A repo-wide `.gitattributes` rule (`*.md text eol=lf`) instead of the `--check` normalisation** —
  rejected: it changes the checkout of every Markdown file on Windows (210 tracked files under
  `docs/` alone) to fix one comparison; two lines inside the generator cover it, and the asymmetry is
  documented (EDGE-016, spec §13).
- **Keep correcting `AGENTS.md` by hand** — the status quo that produced the defect (a documented tree
  that does not exist); rejected by the change's own premise (G-4).
- **Generate on demand, do not commit the map** — rejected: an uncommitted map is not in the
  repository an agent reads, so it cannot be read before walking the tree (G-3), and the
  `AGENTS.md`-vs-reality drift it exists to close would persist.

## References
- `docs/specs/structure-map.md` — REQ-003, REQ-004, REQ-005, REQ-008, REQ-018, REQ-019, REQ-020,
  REQ-021, REQ-022, REQ-023, REQ-026, REQ-027; AC-005, AC-008, AC-019, AC-020, AC-021, AC-022,
  AC-023, AC-026, AC-027; INV-001, INV-003, INV-004, INV-006; EDGE-009, EDGE-010, EDGE-016;
  NFR-002, NFR-007; §13 (design notes), §14 (sequencing and collisions)
- `docs/verification/structure-map.md` — repository measurements, finding 1 (size deviation from
  Q-7), finding 8 (`core.autocrlf` and the byte-exact check)
- `.pre-commit-config.yaml` — the existing `repo: local` hooks (`deptry`, `mkdocs-build`) and the
  auto-fixing formatter hooks
- `.github/workflows/` — `lint.yml`, `quality.yml`, `spec-validation.yml` (12 jobs; none of them
  gains a map job)
- `docs/decisions/ADR-086-scripts-type-checked-tree.md` (the generator's home and its type gate)
