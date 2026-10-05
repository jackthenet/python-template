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
exact non-git fallback ignore list and the exact pruning-marker wording — were fixed by explicit spec choices (the
REQ-003 ignore list, the REQ-010 marker wording), and the `core.autocrlf` hole in the `--check` contract (finding 8) was closed by an explicit spec choice
(newline normalisation in `--check`) rather than by a new question, because none of the three changes a decision the
user made.

---

## P.5 Self-Consistency + Dependency Smoke-Test (2026-10-05)

**Verdict: the specification passes the Self-Consistency Checklist and the Dependency Smoke-Test.** Thirteen findings
were found and **every one was fixed in the specification itself** (`docs/specs/structure-map.md`, now 636 lines, 83
normative IDs unchanged). No ID was renumbered or deleted; every fix is a rewording, a tightened scope, or an added
explicit choice.

| # | Fix (all in `docs/specs/structure-map.md`) |
|---|---|
| 1 | REQ-002 states that `--out`'s missing parent directory is created (EDGE-006); INV-005 now carves that directory out of "writes nothing else". |
| 2 | REQ-004 gains an exit-code **precedence order** (`2 → 4 → 3 → 1 → 0`); AC-004 asserts it. |
| 3 | REQ-005 pins the missing-`--out` line byte-for-byte; AC-005 asserts it. |
| 4 | REQ-014/AC-014: symbols are **grouped, each group in source order** (classes before functions), not one flat source order. |
| 5 | REQ-014: a class or function defined inside a **function body** is not rendered; the nested-class rule is re-scoped to a `class` in a class body and re-justified (the base commit's 12 are all function-local). |
| 6 | REQ-010 + INV-002 scoped to **code dirs**: pruning can never hide an *in-scope module*; a `.py` outside a code dir (1 at base) appears only in its top-dir count line. |
| 7 | REQ-016 now uses the defined term **public symbol** as the rule's subject; the hidden-symbol count re-measured to **230**. |
| 8 | AC-009 counts `docs/` from the **file set** (REQ-003), not from `git ls-files` (the index). |
| 9 | AC-002: "with their stated defaults" → "each with its stated default where the table states one" (`--help` has none). |
| 10 | REQ-012 `exports:` counts stated as **11 of 27** package groups; REQ-013 docstring counts stated as **43 repo-wide but 1 in Packages scope**. |
| 11 | NFR-001 states its logging context; new **Observability** subsection in §10 tabulates the generator's entire stdout/stderr output. |
| 12 | NFR-002 projection recomputed with the REQ-016 visibility applied and self-inclusion counted (see the table below). |
| 13 | §11 preamble wording (Q-10 chose the two-file split, it did not forbid a directory); §13 gains the design note explaining the deliberate `## Modules` → `## Packages` heading rename. |

### Checklist, item by item

| Item | Verdict | What the check found / fixed |
|---|---|---|
| Configurability | **PASS** | No "configurable X" claim exists; the only knobs are the six REQ-002 CLI options and the four hardcoded constants (REQ-014 20-char default rendering, REQ-017 15 fields, REQ-018 100 chars, REQ-002 `--max-depth 4`), each stated as a constant with a matching AC/EDGE. Nothing aspirational. |
| Parameter coverage | **PASS (fix 9)** | All six options have a default and a meaning (REQ-002); `-h/--help` has no default and AC-002 no longer claims it does. `--max-depth ≥ 1` bound + EDGE-014 exit 2. |
| REQ↔AC wording | **PASS (fixes 2, 3, 4, 8, 9)** | (2) REQ-004 left the exit-code choice undefined when several conditions apply at once — a precedence order is now normative (`2 → 4 → 3 → 1 → 0`) and AC-004 asserts it. (3) REQ-005 pinned the missing-`--out` line (it said only "one line naming the missing path" — not byte-testable); AC-005 now asserts the exact line. (4) REQ-014 said "source order" while its own rendering put classes before functions — now "grouped, each group in source order", and AC-014 matches. (8) AC-009 pinned the `docs/` count to `git ls-files docs`, which is the git **index**, while REQ-003 defines the file set as index **plus** untracked-not-ignored — now "the number of files under `docs/` in the file set (200 at the base commit, where it equals `git ls-files docs` because the tree is clean)". (9) AC-002's "with their stated defaults" overclaimed for `--help`. |
| Terminology drift | **PASS (fixes 5, 6, 7)** | (7) "public symbol" was defined but never used — REQ-016 now uses it as the rule's subject and the hidden-symbol count is given by that definition. (5) REQ-014 justified the nested-class rule with "12 nested classes exist … all in `tests/`"; measured, **all 12 are classes defined inside function bodies**, not inside classes, and the spec never said what happens to them — REQ-014 now excludes function-local classes explicitly, the nested-class rule is scoped to a `class` statement directly in a class body (0 exist at the base commit; the unit fixture exercises it), and the 12 are named as the reason the distinction is normative. (6) REQ-010's "pruning can never hide a module" was too broad for the 1 `.py` file outside a code dir (`.github/hooks/ruff-post-edit.py`) — now it says an in-scope module can never be hidden by pruning, and states where an out-of-code-dir `.py` appears (its top-dir count line only); INV-002 carries the same scope. |
| Test strategy coverage | **PASS** | 56 rows: all 27 AC + 6 INV + 16 EDGE + 7 NFR, each with a category, a file and a distinct test function (55 named functions, all unique; NFR-006 is a `record` row by design). All 27 REQ IDs appear in the REQ column. Files used are exactly the three fixed paths — no new test directory. |
| ID references | **PASS** | 83 IDs defined, 83 referenced, **0 dangling**, every ID referenced at least twice. `verify_spec.py` exits 0 (27 REQ→AC, 27 AC→test, 6 INV→property). |
| Scope consistency | **PASS** | Every In-scope item maps to a REQ: generator REQ-001…020, `STRUCTURE.md` REQ-008/021, pre-commit hook REQ-023, skill REQ-022, AGENTS.md four places REQ-024, `mypy scripts/` + the `verify_spec.py` type error REQ-025, specify-skill sentence REQ-026, regeneration rule REQ-027. Every Out-of-scope row is a prohibition elsewhere (no CI job, no `.gitattributes`, no `--fail-on-stale`, no `--json`, no `src/frontend/` scaffold, no hand-editing of the map). |
| Performance budget vs. observability | **PASS (fix 11)** | NFR-001 (2 s, measured floor 0.13 s) had no logging context. A new **Observability** subsection (§10) states that the generator uses no logging framework at all (REQ-001 forbids loguru) and tabulates its entire stdout/stderr output; NFR-001 now names that table as the measurement context. No per-call logging overhead exists, so the budget is not conditional on logging being disabled. |

### Re-measured numbers (fix 12): the NFR-002 projection was arithmetically wrong

The P.4 projection mixed visibility rules — it counted private classes and methods (232 class headers, 483 method
lines) while REQ-016 hides them by default, and its tree count (408) omitted the 9 root files and the 5 count lines.
Re-measured over the file set at this branch head with the REQ-016 default applied:

| Piece | Measured | P.4 claim |
|---|---|---|
| Tree | **424** = 9 root files + 332 code-dir entries + 78 code dirs + 5 count lines | 408 = 331 + 77 |
| Packages | **1 413** = 117 module headers + 116 summaries + 11 `exports:` + 32 group headers + 222 public class headers + 353 field lines (post-cap) + 399 public method lines + 163 public function lines | ≈1 506 (232 classes / 483 methods) |
| Document chrome | ≈8 | not counted |
| **Total (base tree)** | **≈1 845** | ≈1 924 |
| Self-inclusion (`scripts/make_map.py` ≈25 lines + 3 new test files) | +≈28 → **≈1 875** | not counted |
| NFR-002 ceiling | **2 000 — holds, margin ≈125 lines** | 2 000 |

Other counts corrected in the spec against the same measurement: REQ-016 hidden symbols **230** (10 classes + 105
methods of rendered classes + 115 module-level functions), not 221; REQ-012 `exports:` lines **11 of 27** package
groups (all 11 `src/` packages), 16 render none; REQ-013 docstring-less modules **43 repo-wide but 1 in Packages
scope**. Unchanged and re-confirmed: 572 tracked files / 324 `.py` at this head (570/324 at the base commit), 117
in-scope modules, 32 groups, 354 raw field lines → 353 after the cap (exactly one class over: `settings/models.py`,
17), 0 classes nested in classes, `mypy scripts/` = exactly 1 error (`verify_spec.py:74`), complexipy
`max-complexity-allowed = 15` with `paths = ["src", "tests"]`, `type-check` job exists in `quality.yml`, no
`src/frontend/`, no `tests/architecture/` reference in live guidance, `AGENTS.md:1112` is the Project Structure
section.

### Dependency Smoke-Test

**No new dependency is named by the spec** (REQ-001: stdlib only — `ast`, `ast.unparse`, `argparse`, `subprocess`,
`pathlib`, `posixpath`). The smoke-test therefore runs on the capabilities the spec *does* name, on this host
(CPython 3.14.5):

| Capability (named as what) | Host check | Result |
|---|---|---|
| `ast` + `ast.unparse` signature rendering (REQ-014, Q-27) | `ast.unparse` over a decorated `async def` with defaults | OK — the library is the mechanism, the capability ("signature text equals the `ast.unparse` rendering") is the requirement |
| `subprocess` + `git ls-files --cached --others --exclude-standard` (REQ-003) | run over this repository | OK — 572 files, 324 `.py` |
| `git ls-files` on a non-git root (REQ-003 fallback) | documented fallback + EDGE-007 stderr note | specified, no dependency |
| pre-commit `local` hook with `language: system` + `pass_filenames: false` (REQ-023) | `.pre-commit-config.yaml` already runs two such hooks (`deptry`, `mkdocs-build`) | OK — pattern exists in-repo |
| `mypy scripts/` as a CI gate (REQ-025) | `uv run mypy scripts/` on the host | OK — 1 error, fixed by REQ-025 |
| `deptry`, `hypothesis`, `pytest`, `mypy`, `pre-commit` (NFR-003/004/005, §11) | already project dev-dependencies (`pyproject.toml` lines 36–48) | OK — nothing new to install |

Nothing had to be replaced.

### Repo validators

- `uv run python scripts/verify_spec.py docs/specs/structure-map.md` → **exit 0** (all 27 REQ have ACs, all 27 ACs have tests, all 6 INVs have property tests).
- `uv run python scripts/check_traceability.py` → **PASS** (765 rows, 130 spec IDs, 714 test functions). Per finding 2 this PASS is **not** evidence of this spec's coverage: the checker treats REQ/AC IDs as one global namespace and every structure-map ID is already satisfied by another spec's row. Structure Map matrix rows remain Phase 3 (RED) / Phase 5 (GREEN) work; `docs/verification/traceability.md` was **not** touched by P.5.

### Late question raised by the pass (for the orchestrator to append under "Late questions")

**Q-7 budget vs. the content policy.** Q-7 fixed the size budget at ~900–1 000 lines; Q-8/Q-9/Q-19/Q-20 fix the
content policy (helpers and `conftest.py` in scope, code dirs in full, annotated fields listed, every decorator
listed). The re-measured projection above (≈1 845 for the base tree, ≈1 875 for the post-change tree) shows the two
are arithmetically incompatible — reaching ~1 000 requires dropping content the user asked for. The spec keeps the
more specific answers (the content policy) and raises the ceiling to **≤ 2 000** (NFR-002, deviation recorded in
finding 1). The knobs that would reach ~1 000 are listed in finding 1. **This needs a human yes/no at S1.4** — the
spec PR is the gate; it is not a blocker for P.5 and no answer of the user's was overridden silently.

### Status

P.5 gate **passed**: the specification is self-consistent and smoke-tested. `docs/specs/structure-map.md` is now
`DRAFT — P.5 self-consistency passed; awaiting human approval (S1.4)`. Next atomic step: **S1.4** (commit the spec in
the change worktree, open the approval PR). The orchestrator sets `Status: READY` in `docs/todo/structure-map.md` on
`main` after verifying this handoff.
