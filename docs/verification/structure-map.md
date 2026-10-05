# Verification: structure-map

- **Change type:** FEATURE
- **Classified:** Phase 0 at **P.1** (orchestrator, `docs/todo/structure-map.md:8`); re-confirmed at P.4.
- **Rationale:** The change adds externally observable behaviour — a new generator (`scripts/make_map.py`) with a
  documented CLI and a documented exit-code contract (`0`/`1`/`2`/`3`/`4`), a new committed artifact
  (`STRUCTURE.md`), a new local pre-commit hook, and new agent-facing guidance. It is not a defect (nothing in an
  approved spec describes a repository map), and it is confined to one new capability plus documentation edits, so it
  does not meet the CROSS-CUTTING criterion (no new shared runtime capability, no architecture change, no
  cross-feature interface). The DOCS/CHORE classification was considered and rejected at P.1 because the `--check`
  exit code is externally observable behaviour.
- **Version bump (Phase 6):** `minor` (FEATURE).
- **Phase P status at hand-off:** P.1 (2026-10-03), P.2 (2026-10-03, Q-1…Q-31), P.3 (rounds 1–2 2026-10-03, rounds
  3–8 2026-10-05) — **all 31 questions ANSWERED and incorporated**; P.4 this record; **P.5 not yet run**.
- **Value triage:** 4/5, *implement as one change* (`docs/todo/structure-map.md`).

## Phase P progress

- **P.4 Draft (this step, 2026-10-05):** `docs/specs/structure-map.md` created — **27 REQ, 27 AC, 6 INV, 16 EDGE,
  7 NFR**, all with stable IDs, Given/When/Then acceptance criteria mapped 1:1 onto the REQs, a CLI contract table,
  an output-format grammar, and a test strategy naming **every** normative ID. No implementation file, test file,
  `STRUCTURE.md`, `AGENTS.md`, workflow or `pyproject.toml` change is made by this step.

## Repository measurements at the base commit (freshly measured, 2026-10-05)

Measured in this worktree at `249bb32` with `git ls-files` + a one-pass `ast` scan. These supersede both the
`docs/todo/structure-map.md` *Why* figures (522 tracked files, 33 701 Python lines) and the P.2 figures (548 tracked
files, 323 `.py`, 32 343 lines) — the base commit moved when `chore/architecture-tests-missing` (PR #65) merged.

| Measurement | Value |
|---|---|
| Tracked files (all) | **570** |
| Tracked `.py` files | **324** (33 918 lines) |
| `src/` | 84 files (83 `.py`, 10 905 lines, 208 classes, 419 methods, 141 module-level functions, 343 annotated class fields, 216 decorators, 11 `__init__.py`) |
| `tests/` | 239 files (234 `.py`, 22 185 lines, 17 `conftest.py`, 11 `*_test_helpers.py`, **42 modules with no docstring**) |
| `scripts/` / `migrations/` | 3 files / 6 files |
| `docs/` / `.agents/` / `.github/` / `userdocs/` | 200 / 16 / 9 / 2 |
| `.py` path depth | depth 2: 17, depth 3: 11, depth 4: 296 |
| Nested classes | 12 (all under `tests/`) |
| `async def` | 3 files, 3 definitions |
| Module-level assignments | 2 242 (not rendered — REQ-017) |
| Read + `ast.parse` of all 324 `.py` | **0.13 s** (CPython 3.14.5, this host) — NFR-001 floor |
| Projected `STRUCTURE.md` size | **≈1 924 lines** (tree 408 + Packages ≈1 506) — NFR-002 ceiling 2 000 |
| `uv run mypy scripts/` at base | **1 pre-existing error**: `scripts/verify_spec.py:74: Item "TextIO" of "TextIO \| Any" has no attribute "reconfigure" [union-attr]` (REQ-025) |
| `uv run ruff check .` at base | clean |
| `uv run pytest tests/ -q` on `main` | 728 passed, 1 skipped (the skip is `tests/acceptance/filemanagement/test_filemanagement.py:364`, symlinks unavailable on this host — pre-existing/environmental) |

## Spec self-check evidence (P.4)

- `uv run python scripts/verify_spec.py docs/specs/structure-map.md` → **exit 0** (structure, ID uniqueness,
  INV→property-test mapping, `Traceability: PASS`).
- `uv run python scripts/verify_spec.py docs/specs/template.md` → **exit 0** (re-run after the REQ-025 fix is part of
  Phase 4; the `spec-validation` job lists `scripts/verify_spec.py` as a trigger).
- ID inventory: REQ-001…REQ-027, AC-001…AC-027, INV-001…INV-006, EDGE-001…EDGE-015, NFR-001…NFR-007 — **no gaps, no
  extra numbers, no reference to an undefined ID, and every normative ID appears in §11 Test Strategy**.
- `uv run python scripts/check_traceability.py` → **PASS** (765 matrix rows, 130 spec IDs, 714 test functions).
  See the finding below: the pass is not evidence that this change's rows exist.
- `uv run ruff check .` → clean (no code written by this step).

## Findings and deviations

1. **Deviation from Q-7 (map size).** The question-file budget of ~900–1 000 lines is arithmetically incompatible
   with the content policy fixed by Q-8/Q-9/Q-19/Q-20 at this repository size (projection ≈1 924 lines). The content
   policy is implemented unchanged and NFR-002 sets the ceiling at **≤ 2 000 lines**. The knobs that would reach
   ~1 000 lines, if the ceiling is ever breached: drop method docstring summaries (−≈480), render `tests/` helpers as
   module headers only (−≈120), lower the per-class field cap from 15 to 8 (−≈160).
2. **`check_traceability.py` cannot police this change's IDs.** The checker treats `REQ-XXX`/`AC-XXX` as one global
   namespace: all 54 REQ/AC IDs this spec defines are already defined by other specs in `docs/specs/`, so its rule
   "every REQ/AC defined in `docs/specs/` has a matrix row" is satisfied by other changes' rows. The *Structure Map*
   rows in `docs/verification/traceability.md` are therefore a **workflow obligation (Phase 3 adds them, Phase 5
   replaces the status with GREEN evidence), not a CI-enforced one** — recorded in spec §12 so the reviewer does not
   read the checker's PASS as coverage evidence.
3. **`AGENTS.md` Project Structure contradicts the repository** (the defect Q-11 fixes): it prescribes per-feature
   `model/` and `services/` subdirectories and a `src/frontend/` tree, but `src/frontend/` does not exist at all, no
   feature has `model/` or `services/`, and the only nested directory under `src/backend/` is
   `src/backend/filemanagement/assets/` (an asset directory, not an architecture layer). `[tool.coverage.run]` still
   names `src/frontend`.
4. **`tests/architecture/` is already resolved.** `chore/architecture-tests-missing` merged as PR #65 (merge commit
   `4f684f8`); at this base commit `rg -n 'tests/architecture' AGENTS.md .agents` returns nothing. This change only
   adds an acceptance test (AC-024) that no live guidance reintroduces those citations; it does not re-do that edit and
   does not create `tests/architecture/`.
5. **Collision with `value-triage-gate`.** That change will edit the `AGENTS.md` Phase Matrix *P Prepare* row, the
   Phase P table, the Workflow Diagram and the Agent Obligations/Prohibitions, plus `specify/SKILL.md`. This change
   edits different `AGENTS.md` regions (Tooling, Skill-to-Phase Mapping, Project Structure) and adds **one advisory
   sentence** to `specify/SKILL.md` P.1, so the two remain independently mergeable (spec §14).
6. **Collision with `chore/remove-spec-tdd-driver` (PR #62, open).** It deletes files under `.github/`, which changes
   the tracked-file counts the map reports. `STRUCTURE.md` must be regenerated after that PR merges; it touches no
   file this change edits.
7. **Tooling gotcha (Problem Log P-42).** The first `uv run` in a fresh worktree rewrites `uv.lock`
   (`0.6.0` → `0.6.1`) because `[tool.bumpversion.files]` does not list `uv.lock`. `git checkout -- uv.lock` before
   every commit on this branch; the durable fix (add `uv.lock` to `[tool.bumpversion.files]`) is a separate chore.
8. **No `.gitattributes` + `core.autocrlf=true` breaks a naive byte-exact `--check` (found at P.4).** The repository
   has no `.gitattributes`, and `git config core.autocrlf` is `true` on the development host, so a committed LF blob
   is checked out with CRLF on Windows. A byte-exact `--check` would then report the freshly committed `STRUCTURE.md`
   as stale on every Windows checkout (exit 1 on a clean tree). Resolved in the spec: `--check` normalises
   `\r\n` → `\n` before comparing (REQ-005, INV-004, AC-005, EDGE-016, `test_edge_016_crlf_checkout_is_not_stale`),
   generate mode always writes LF, and a repo-wide `.gitattributes` rule was rejected as out of scope (spec §13).

## Open questions

None. All 31 P.2 questions are ANSWERED; P.4 raised no new question. Two places where the answers were silent — the
exact non-git fallback ignore list and the exact pruning-marker wording — were fixed by explicit spec choices (REQ-024,
§5.5), and the `core.autocrlf` hole in the `--check` contract (finding 8) was closed by an explicit spec choice
(newline normalisation in `--check`) rather than by a new question, because none of the three changes a decision the
user made.
