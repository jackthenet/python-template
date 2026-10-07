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

---

## Phase 2 — S2.1 ADRs (2026-10-08)

Executed in the change worktree `C:/workspace/active-projects/python-template_kopie-worktrees/feature/structure-map`
(`git rev-parse --show-toplevel` printed alongside every measurement below), branch
`feature/structure-map`, HEAD **`aabf878`** (the branch was fast-forwarded onto `origin/main`'s tip,
so it carries the merged `structlog-logging` change — PR #74, merge `c7a9119`, version 1.0.0 — and
every other merged change). Spec approval gate **read from the cache, not re-run**: spec PR #69 merged
as `570bfbc` (2026-10-06T06:52:57Z).

### Verdict: two ADRs written, one candidate skipped

The ADR threshold (AGENTS.md "Phase 2: DECOMPOSE" / decompose skill S2.1 — new dependency, new
pattern/architecture element, or cross-feature interface) was applied per candidate decision:

| Candidate decision | Threshold verdict | Where recorded |
|---|---|---|
| `STRUCTURE.md` as a **committed, generated artifact** with a **check-only, advisory** local pre-commit hook and **no CI job** (REQ-021, REQ-023, REQ-026, REQ-027) | **Clears it — new pattern/architecture element.** No repo-owned generated committed artifact exists (finding F-03), and "advisory, never a gate" departs from the repo's gate-heavy convention on two axes at once (12 CI jobs; the two formatter hooks auto-fix) | `docs/decisions/ADR-085-committed-generated-structure-map-check-only-local-hook.md` |
| `scripts/` **joining the type gate** (REQ-025) + the generator living in `scripts/` under a stdlib-only budget (REQ-001) | **Clears it — repo-wide tooling interface.** It changes what the `mypy` gate covers, and the gate map over the repository's Python is asymmetric today (finding F-04); the placement choice (not `src/`) is what keeps coverage, complexipy and bandit scopes untouched | `docs/decisions/ADR-086-scripts-type-checked-tree.md` |
| The generator's **determinism contract** (REQ-019, REQ-020 path form, REQ-018 summary normalization) | **Skipped — the spec restated.** REQ-019/REQ-020/REQ-018 are normative requirements with AC-019/AC-020/AC-018 and property witnesses INV-001/INV-003; there is no rejected alternative and no interface beyond the artifact itself. The one decision-shaped element inside the candidate — byte-exact `--check` **plus** the `\r\n` → `\n` normalisation **instead of** a repo-wide `.gitattributes` rule (REQ-005, INV-004, EDGE-016, spec §13) — is a consequence of the freshness mechanism, so it is folded into ADR-085 (Decision bullet 4, Alternatives bullet 4) rather than getting its own ADR | ADR-085 (folded) |

No new dependency: confirmed from `docs/specs/structure-map.md` §5 REQ-001 (stdlib only — `ast`,
`argparse`, `pathlib`, `subprocess`, `sys`, plus `collections`/`re`/`dataclasses`) and NFR-003
(`deptry` stays clean). Neither ADR introduces or implies a dependency; the P.5 Dependency
Smoke-Test result stands.

### ADR numbering — reservation recorded to prevent a merge collision

| Number | State | Owner |
|---|---|---|
| ADR-081 | **absent on disk, reserved** | `api-keys` (`docs/todo/api-keys.md:64`, `docs/questions/api-keys.md:740`/`:808`; noted by ADR-082's Numbering paragraph) |
| ADR-082 | present on this branch (highest file here) | `structlog-logging` (merged) |
| ADR-083, ADR-084 | **authored on the in-flight branch `crosscut/settings-public-registry-setter`, not in this worktree** — `ADR-083-public-install-operation-feature-singletons.md`, `ADR-084-two-guards-singleton-slot-tid251-scan-test.md` | `settings-public-registry-setter` |
| **ADR-085, ADR-086** | **taken by this change** | `structure-map` |

Verified with `git ls-tree -r --name-only crosscut/settings-public-registry-setter docs/decisions |
grep -E 'ADR-08[0-9]'` → ADR-080, ADR-082, ADR-083, ADR-084. This change therefore starts at 085 so
the two PRs cannot collide on a number; if `settings-public-registry-setter` merges first, no renumber
is needed on either side.

### Re-measured facts at `aabf878` (the Phase P table above predates the `structlog-logging` merge)

All measured in this worktree (`git rev-parse --show-toplevel` =
`C:/workspace/active-projects/python-template_kopie-worktrees/feature/structure-map`), HEAD `aabf878`:

| Measurement | At `aabf878` | At the P.4/P.5 base (`249bb32` / `570bfbc`-era head) |
|---|---|---|
| Tracked files (all) | **595** | 570 (572 at the P.5 head) |
| Tracked `.py` | **339** | 324 |
| `.py` under `src/` | **84** | 83 |
| `scripts/` · `migrations/` · `docs/` · `.agents/` · `.github/` · `userdocs/` | 3 · 6 · **210** · 16 · 9 · 2 | 3 · 6 · 200 · 16 · 9 · 2 |
| Root-level tracked files | 9 | 9 |
| `__init__.py` · `tests/**/conftest.py` · `tests/**/*_test_helpers.py` | 70 · 17 · 11 | 70 · 17 · 11 |
| **Packages-scope modules (REQ-011)** | **118** = 84 + 3 + 3 + 17 + 11 | 117 |
| `.py` outside `src/` and `tests/` | **7** = 3 `scripts/` + 3 `migrations/` + 1 `.github/hooks/ruff-post-edit.py` | 7 |
| `src/backend/logging/` | 6 modules, **1 119 lines** (`_pipeline.py` 395, `_decorator.py` 253, `_renderers.py` 269, `feature_settings.py` 113, `_settings.py` 64, `__init__.py` 25) | (pre-merge file set) |
| `uv run mypy scripts/` | **1 error in 1 file (checked 3 source files)** — `scripts/verify_spec.py:74: Item "TextIO" of "TextIO \| Any" has no attribute "reconfigure" [union-attr]` | 1 error (same file/line) |
| `mypy` gate scope | `uv run mypy src/` only (quality.yml `type-check`); `ty` is `root = ["./src"]` and informational | same |
| Coverage / complexipy / bandit scope | `source = ["src/backend", "src/frontend"]`, `fail_under` floor 92 · `paths = ["src", "tests"]`, max-complexity 15 · `bandit -r src/` | same |
| CI jobs | **12** across 3 workflows (`lint.yml` 1, `quality.yml` 8, `spec-validation.yml` 3) | same |
| `repo: local` pre-commit hooks | 2 (`deptry`, `mkdocs-build`), both `language: system` + `pass_filenames: false`; the two formatter hooks (`ruff-check --fix`, `ruff-format`) rewrite files | same |
| `STRUCTURE.md` | does not exist yet (correct at S2.1) | — |
| `.gitattributes` / `git config core.autocrlf` | **absent** / **`true`** | absent / `true` |
| `make_map` references anywhere in `.github`, `AGENTS.md`, `.agents` | **none** | none |
| `pyproject.toml` version | `1.0.0` | pre-`structlog-logging` |

### Findings

- **F-01 — the NFR-002 margin is thinner than the spec states.** The spec's projection (≈1 875 lines,
  margin ≈125 under the 2 000 ceiling) was computed over 324 `.py` / 117 Packages-scope modules; at
  `aabf878` the tree is 339 `.py` / **118** Packages-scope modules and `docs/` grew to 210 files. No
  re-projection was attempted in S2.1 (that is generator work); **Phase 4 must generate and Phase 5
  must record the actual line count against NFR-002**, and the REQ-017 field cap is the named safety
  valve. Not a spec amendment — the ceiling and the content policy are unchanged.
- **F-02 — REQ-025's premise still holds after the merge:** `uv run mypy scripts/` reports exactly one
  pre-existing error, in `scripts/verify_spec.py:74`, 3 source files checked. The widened gate is
  clean-able with the one behaviour-preserving fix the spec scopes.
- **F-03 — the "new pattern" claim had to be narrowed to stay true.** `uv.lock` *is* a committed
  generated file, so "no committed generated artifact exists" would be false; what does not exist is a
  **repo-owned generator** whose output is committed **and whose freshness is checked** (`uv.lock` is
  produced by an external tool and CI runs `uv sync --only-group dev`, not `--locked`, so nothing
  checks it). ADR-085's Context is worded to that narrower, measured claim.
- **F-04 — the gate map over the repository's Python is asymmetric today** (table above): `scripts/`
  is already covered by `ruff` and `deptry` (its pre-commit `files` regex includes `scripts/`) but not
  by `mypy`, `ty`, coverage, complexipy or bandit. ADR-086 states the asymmetry so the widening is a
  decision, not an accident, and records that `migrations/` and `.github/hooks/` stay outside the type
  gate.
- **F-05 — ADR-083/ADR-084 are claimed by another in-flight branch** (verified by `git ls-tree`, not
  by this worktree's `ls`). Starting here at 085 avoids the collision; the reservation is recorded
  above so the two PRs do not fight at merge time.
- **F-06 — the "advisory, never a gate" departure is measurable:** 12 CI jobs exist today and AC-023's
  "no file under `.github/workflows/` mentions `make_map.py`" currently holds trivially (grep over
  `.github`, `AGENTS.md`, `.agents` returns nothing). ADR-085 records why no 13th job is added.
- **F-07 — finding 8 still stands at this head:** no `.gitattributes`, `core.autocrlf=true`, so the
  REQ-005 newline normalisation remains necessary (ADR-085 Decision bullet 4).
- **F-08 — spec §14's `chore/remove-spec-tdd-driver` row is stale (PR #62 is merged).** The spec
  records it as open and requires regenerating `STRUCTURE.md` after it merges. It merged as `a2000c2`
  and is reachable from this branch (`git log HEAD --grep='remove-spec-tdd'`), and `.github/` now has
  9 tracked files — so the condition is already satisfied and the map's counts already include it.
  No spec amendment needed (the requirement is met, not contradicted); ADR-085's Sequencing bullet
  states the current fact. **S2.2 must not create a task for it.**
- **F-09 — `uv.lock` is rewritten by the first `uv run` in this worktree** (`python-template`
  `0.6.1` → `1.0.0`, the version bump that `structlog-logging` landed): finding 7 / Problem Log P-42
  still bites at this head. `git checkout -- uv.lock` before every commit; this step did exactly that
  and committed only the three Markdown files.

### Gate

- **S2.1 gate: PASS.** Two ADRs in house format (Status / Context / Decision / Consequences /
  Alternatives Considered / References, per `docs/decisions/ADR-000-template.md`), each citing the
  spec IDs it justifies and the measured facts above; one candidate explicitly skipped with rationale.
- Files written by this step: `docs/decisions/ADR-085-…md`,
  `docs/decisions/ADR-086-…md`, this section of `docs/verification/structure-map.md`.
- **Nothing else was touched**: no implementation code, no test, no `STRUCTURE.md`, no `AGENTS.md`, no
  workflow, no `.pre-commit-config.yaml`, no `pyproject.toml`, no `docs/tasks/`, no
  `.github/task-runner/tasks.json` (that is S2.2), no `docs/todo/` or `docs/questions/`.
- `ruff`: **n/a** — only Markdown was written and `[tool.ruff] extend-exclude = ["**/*.md"]`.
- Next atomic step: **S2.2 — decompose the spec into `docs/tasks/structure-map.tasks.json` and copy it
  to `.github/task-runner/tasks.json`**, with ADR-085/ADR-086 as design constraints (regenerate the map
  last; no CI map job; `mypy scripts/` + the `verify_spec.py` fix in one task; no coverage/complexipy
  scope change).

### Re-entry re-verification (second S2.1 execution, 2026-10-08)

The step was re-entered (the launch brief reported HEAD as `313d058`, which does not exist as an object in
this repository — the branch had instead been fast-forwarded onto `origin/main`). The S2.1 output was
already committed as **`e54b4ec`**; this execution **verified that output against the done criteria and
corrected three loose measured claims in ADR-085** rather than rewriting it. All measurements below were
taken with `git rev-parse --show-toplevel` = `C:/workspace/active-projects/python-template_kopie-worktrees/feature/structure-map`,
HEAD `e54b4ec`.

| Claim under test | Re-verified value | Verdict |
|---|---|---|
| 12 CI jobs across 3 workflows | counted under each workflow's `jobs:` key: `lint.yml` 1 (`lint`), `quality.yml` 8 (`type-check`, `security`, `coverage`, `dependency-review`, `dependencies`, `docs`, `migrations`, `complexity`), `spec-validation.yml` 3 (`spec-validation`, `traceability`, `tests`) = **12** | correct |
| `repo: local` hooks | 2 — `deptry` (`stages: [pre-commit]`) and `mkdocs-build` (`stages: [pre-push]`); the `ruff-check --fix` / `ruff-format` hooks do rewrite | **corrected in ADR-085** (it called both "pre-commit hooks") |
| `AGENTS.md` Project Structure line | `AGENTS.md:1120` at this head | **corrected in ADR-085** (it said `:1112`, the P.5-era line) |
| parallel worktrees | `git worktree list` → primary (`main`) + **3 change worktrees** (`crosscut/settings-public-registry-setter`, `feature/structure-map`, `issue/pytest-randomly`) | **corrected in ADR-085** (it said "four") |
| ADR numbering | `git ls-tree -r --name-only crosscut/settings-public-registry-setter docs/decisions` → ADR-080, 082, **083, 084**; `git ls-tree -r --name-only HEAD docs/decisions \| grep -c ADR-081` → **0**; 84 ADR files at HEAD, highest = **ADR-086** | correct — 085/086 are free of collision |
| tracked-file counts | `git ls-files`: **597** tracked (595 at `aabf878` + the 2 ADR files this step added), **339 `.py`**, **84** under `src/`, **70** `__init__.py`, 17 `conftest.py`, 11 `*_test_helpers.py` → **118 Packages-scope modules**, 9 root-level files, `docs/` **212** (210 + 2), `.github/` 9 | correct |
| F-02 (`REQ-025` premise) | `uv run mypy scripts/` → `scripts/verify_spec.py:74: … [union-attr]`, **1 error in 1 file (checked 3 source files)** | correct |
| ADR-086 gate table | `pyproject.toml`: `python_version = "3.14"`, `check_untyped_defs`, `disallow_untyped_defs`, `explicit_package_bases`, `namespace_packages`; `[tool.ty] root = ["./src"]`; coverage `source = ["src/backend", "src/frontend"]`, `fail_under = 92`; complexipy `paths = ["src", "tests"]`, `max-complexity-allowed = 15`; `quality.yml` runs `mypy src/`, `ty check src/`, `bandit -r src/`, `complexipy src tests` | correct |
| `make_map` absent from live guidance | `grep -rn make_map .github AGENTS.md .agents` → **0 hits** (AC-023 holds trivially today) | correct |
| `.gitattributes` / `core.autocrlf` | absent / **`true`** (F-07 stands) | correct |
| `uv run python scripts/check_traceability.py` | **PASS — 822 matrix rows, 136 spec IDs, 746 test functions** (up from 765 / 130 / 714 at P.5 because other changes merged; per finding 2 the PASS is still not evidence of this spec's rows) | PASS |

ADR format check: both files follow `docs/decisions/ADR-000-template.md` (Status / Context / Decision /
Consequences / Alternatives Considered / References, `## Status` = `Accepted`), match the heading style of
ADR-082/ADR-080, cite the spec IDs they settle, and contradict no row of the spec's Out-of-scope table
(no CI job, no auto-fixing hook, no workflow gate, no `.gitattributes`, no new dependency, no coverage or
complexipy scope change). No `docs/decisions/` index file exists, so none needed updating.

## Phase 2 — S2.2 task DAG (2026-10-08)

`git rev-parse --show-toplevel` = `C:/workspace/active-projects/python-template_kopie-worktrees/feature/structure-map`,
branch `feature/structure-map`, HEAD before this step `b9a2c76`, `origin/main` = `aabf878` (an ancestor of
HEAD — re-checked with `git merge-base --is-ancestor aabf878 HEAD`, exit 0). The spec approval gate is read
from the cached record above (PR #69, merge commit `570bfbc`) and was **not** re-checked.

### Artifacts

| Artifact | State |
|---|---|
| `docs/tasks/structure-map.tasks.json` | new, 7 tasks, sha256 `520a1958a1681697c1522279b270975c65d4b8af81a658f070c752c6f0eee2dc` |
| `.github/task-runner/tasks.json` | overwritten with the new DAG (the active build environment holds one DAG at a time; the previous content was the merged `structlog-logging` DAG, 7 tasks all `VERIFIED`), sha256 `520a1958a1681697c1522279b270975c65d4b8af81a658f070c752c6f0eee2dc` — **byte-identical** to the docs copy |

Byte-identity is proven by hashing both files (`certutil -hashfile … SHA256` and a Python `hashlib.sha256`
over the raw bytes agree). `scripts/validate_task_dag.py` does **not** check byte-identity — its sync check
compares only the `task_id` sets and each task's `status` — so the hash is the evidence (PROBLEMS.md P-61).

### DAG validation output

```
$ uv run python scripts/validate_task_dag.py .github/task-runner/tasks.json
Task DAG validation PASSED: 7 tasks, acyclic, well-formed.
exit 0
```

### Task table

| Task | Title (abridged) | IDs covered | Depends on |
|---|---|---|---|
| T-001 | `uv run mypy scripts/` joins the quality.yml type-check job; fix the one pre-existing `union-attr` error in `scripts/verify_spec.py` behaviour-preservingly | REQ-025, AC-025, NFR-004 | — |
| T-002 | the stdlib-only generator harness: CLI, file set, exit-code dispatcher (2, 4), unreadable-source hard failure, document shape, `--out` parent dir | REQ-001/002/003/004/006/007/008, AC-001/002/003/006/007/008, EDGE-003/004/005/006/007/008/014, NFR-001/003/006 | T-001 |
| T-003 | Directory tree + Packages scope + group/module headers + path form | REQ-009/010/011/012/013/020, AC-009/010/011/012/013/020, INV-002/003, EDGE-001/002/013/015, NFR-007 | T-002 |
| T-004 | symbol inventory: group order, `ast.unparse` signatures, decorators, visibility, field cap, summaries | REQ-014/015/016/017/018, AC-014/015/016/017/018, EDGE-011/012 | T-003 |
| T-005 | `--check` semantics + the completed exit-code precedence + determinism + hook-clean output | REQ-004/005/019, AC-004/005/019, INV-001/004/005/006, EDGE-009/010/016 | T-004 |
| T-006 | the integration surface: skill, check-only local hook, the four `AGENTS.md` edits, the advisory sentence, the freshness policy | REQ-022/023/024/026/027, AC-022/023/024/026/027 | T-005 |
| T-007 | generate and commit `STRUCTURE.md` for the post-change tree; gate AC-021, NFR-002, NFR-005 | REQ-021, AC-021, NFR-002/005 | T-006 |

Dependency chain is linear (T-001 → … → T-007) and acyclic. T-001 runs first because it is the easiest task
(Todo Tracking Discipline, easiest-first) and because ADR-086's intent is that the generator lands in an
already-typed `scripts/` tree; T-007 is last by ADR-085.

### ID coverage — two-direction diff, 0 missing / 0 unknown

The spec defines **83** normative IDs (27 REQ, 27 AC, 6 INV, 16 EDGE, 7 NFR; series 001–027 / 001–027 /
001–006 / 001–016 / 001–007 with no gaps). Scripted diff over the spec text and the DAG's
`requirements`/`acceptance_criteria`/`invariants`/`edge_cases`/`non_functional` lists:

```text
defined in spec: 83      assigned in DAG: 83
MISSING (defined, not assigned): []
UNKNOWN  (assigned, not defined): []
id_coverage.spec_ids entries: 83   coverage-vs-task diff: []
```

Every `id_coverage.spec_ids` entry names a task that lists that ID in one of its five requirement fields,
and every ID in a task's five fields appears in `id_coverage` — checked programmatically, no mismatch.
`amended_spec_ids` is empty: this change amends no other spec.

### Witness cross-check against spec §11 — 55 node IDs, 1:1

Spec §11 names **55** witness functions (27 AC, 6 INV, 16 EDGE, 6 NFR — NFR-006 has no test and is recorded
as the line count of `scripts/make_map.py` in Phase 5). The DAG's `tests_to_create` holds exactly 55 entries,
each a single `path::test_name` node ID (never several node IDs packed into one string — the defect a sibling
change hit). Diffing the DAG's entries against §11's rows: `in spec not in dag: []`,
`in dag not in spec: []`, `path/function mismatches: []`. Layer placement matches the spec exactly:
31 acceptance / 18 unit / 6 property, in the three fixed files only (no new test directory, Q-10). No
duplicate node ID across tasks. Per-task counts: T-001 2, T-002 15, T-003 13, T-004 7, T-005 10, T-006 5,
T-007 3.

### Gate satisfiability (every test can pass with its own task plus its dependencies)

| Placement | Reason |
|---|---|
| AC-004 (the whole exit-code table, incl. exit 1 and 3) and EDGE-009 (stale on a fresh clone) → **T-005**, not T-002 | both need `--check`, which does not exist before T-005; a T-002 test asserting exit 1 or 3 could only pass vacuously. REQ-004 is nevertheless listed under T-002, which implements the 2 and 4 branches and the dispatcher shape. |
| AC-020, INV-003, NFR-007 → **T-003** | they assert on rendered paths; before any path is rendered they would pass over an empty document. |
| EDGE-001 → **T-003** (module half, per §11's EDGE-001 → REQ-013 mapping); the symbol half is REQ-018 and is exercised in **T-004** by AC-018 | narrowed-gate rule: the task that actually exercises the path owns the coverage, and T-004 is named as responsible for a regression there. |
| AC-021, NFR-002, NFR-005 → **T-007** | they can only be gated once the committed map exists, and the map must reflect the post-change tree (ADR-085). |
| NFR-005's witness (`complexipy src tests`) scans files created by T-002…T-005 | all three test files are therefore in T-007's `allowed_files` so a violation is fixed **in-task**, never deferred to Phase 5 (decompose skill: a break is fixed by the task that causes it). |
| NFR-006 → **T-002**, no test | spec §11 record row: Phase 5 records the actual line count. |

No task's test calls a component of a later task; no test was deleted to make a gate satisfiable.

### `allowed_files` derivation method (P-55)

For each task: (1) take the files its `tests_to_create` create or modify; (2) take the files its
`implementation_steps` edit; (3) take the **search/scan scope of each of its own witnesses** — every file a
test reads, greps or walks — and for each file inside that scope that the task could be required to edit, put
it in `allowed_files`; (4) where a scope is searched but must **not** change, list it annotated
read-only so the witness scope is explicit and the prohibition is stated in `design_constraints` instead.
Measured facts that make step 3 cheap here: `grep -rn make_map .github AGENTS.md .agents` → **0 hits** and
`grep -rn 'tests/architecture' AGENTS.md .agents` → **0 hits** at this head, so AC-023/AC-024/AC-026's
negative searches need no edit outside the four listed `AGENTS.md`/skill files; `uv run mypy scripts/` reports
exactly **1** offender (`scripts/verify_spec.py`), which is listed in T-001; `deptry` scans
`src/ migrations/ scripts/` (not `tests/`), and the only file in that set this change touches is
`scripts/make_map.py`. Each task records its own derivation in its `design_constraints`, and each names the
correction path (add the file to `allowed_files`, never weaken the test).

### Top-level key adaptation

The per-task key set is **identical** to the house DAG (`docs/tasks/structlog-logging.tasks.json`, 20 keys —
verified programmatically for all 7 tasks) so the task-runner tooling and the Phase 4 steps work unchanged.
Top level, `deptry_interlock` is replaced by **`gate_interlock`**: this change adds no dependency (REQ-001 is
stdlib-only), so there is nothing for deptry to interlock; what has to be interlocked instead is the widened
type gate (T-001 before T-002), the `structure-map-check` hook versus the not-yet-existing `STRUCTURE.md`
(T-006 before T-007, no `.py` commit in between), the absence of any CI map job (AC-023), the frozen
coverage/complexipy/bandit/`ty` scope with `fail_under = 92` unmoved, the three fixed test paths, and the
`complexity` CI job that no Phase 3–5 step runs (P-56). All other top-level keys
(`feature`, `spec`, `branch`, `change_type`, `adr`, `grouping`, `id_coverage`, `tasks`) are unchanged in name
and shape; `id_coverage` collapses to a single `spec_ids` map because this change has one spec and no
amendments. Initial `status` for all tasks is `PENDING`, matching the house convention at S2.2
(`b38a2cc` created `structlog-logging` with all seven tasks `PENDING`).

### Commands deliberately NOT in any task

No task runs the full suite (Phase 5 gate); no task adds a CI job for the map (AC-023); no task creates a
new test directory (Q-10); no task touches coverage/complexipy/bandit/`ty` configuration or
`fail_under = 92`; no task adds a `.gitattributes` (the CRLF handling is inside `--check`, spec §13);
no task regenerates the map for the already-merged `chore/remove-spec-tdd-driver` (F-08); no task for
`tests/architecture/` (already removed by `chore/architecture-tests-missing`).

### Gate

S2.2 done criteria: DAG committed at `docs/tasks/structure-map.tasks.json` and byte-identical at
`.github/task-runner/tasks.json` (hashes above) ◆; `validate_task_dag.py` PASSED ◆; 83/83 IDs assigned,
0 missing / 0 unknown ◆; 55 witness node IDs 1:1 with spec §11 ◆; `allowed_files` derived from each task's
own witness scope (P-55) ◆; `red_command`/`green_command` targeted, never the full suite ◆. Phase 2 writes no
implementation code and derives no acceptance tests — the three test files do not exist yet (verified:
`tests/acceptance/test_structure_map.py`, `tests/unit/test_make_map.py`,
`tests/property/test_structure_map.py` and `STRUCTURE.md` are all absent at this head).

