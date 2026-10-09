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

## Phase 3 — S3.1 test derivation, T-001 (2026-10-07)

`git rev-parse --show-toplevel` = `C:/workspace/active-projects/python-template_kopie-worktrees/feature/structure-map`,
branch `feature/structure-map`, HEAD before this step `69801eb` (measured, not assumed — P-57). Spec approval
gate read from the cached record above (PR #69, merge commit `570bfbc`); not re-checked.

### Derived tests (T-001 only — `tests/acceptance/test_structure_map.py`, new file)

| Node ID | Witness for | Clauses asserted |
|---|---|---|
| `test_ac_025_mypy_covers_scripts` | AC-025 / REQ-025 | (1) the `type-check` job block of `.github/workflows/quality.yml` contains the literal `uv run mypy scripts/`; (2) mypy over `scripts/` exits `0`; (3) `scripts/verify_spec.py docs/specs/template.md` still exits `0` with the pre-fix report |
| `test_nfr_004_mypy_and_ruff_clean` | NFR-004 / REQ-025 | all four gates clean: `mypy scripts/`, `mypy src/`, `ruff check .`, `ruff format --check .` |

Both tests collect clause results and assert once, so the failure message names the failing clause.
No implementation code was written: `git status --porcelain` after the step shows only
`?? tests/acceptance/test_structure_map.py` (plus ` M uv.lock`, reverted — P-42); `.github/workflows/quality.yml`
and `scripts/verify_spec.py` are untouched.

### RED (the `red_command`, before implementation)

```text
$ uv run pytest tests/acceptance/test_structure_map.py::test_ac_025_mypy_covers_scripts \
      tests/acceptance/test_structure_map.py::test_nfr_004_mypy_and_ruff_clean -v
tests/acceptance/test_structure_map.py::test_nfr_004_mypy_and_ruff_clean FAILED [ 50%]
tests/acceptance/test_structure_map.py::test_ac_025_mypy_covers_scripts FAILED [100%]
E  AssertionError: mypy scripts/: exit 1: scripts\verify_spec.py:74: error: Item "TextIO" of
   "TextIO | Any" has no attribute "reconfigure"  [union-attr]
E  AssertionError: clause 1: the type-check job of quality.yml does not run 'uv run mypy scripts/'
     clause 2: mypy over scripts/ exits 1: scripts\verify_spec.py:74: … [union-attr]
     Found 1 error in 1 file (checked 3 source files)
============================== 2 failed in 1.20s ==============================
exit 1
```

**Failure mode (test contract sanity check): PASSED.** Both red tests fail with `AssertionError` on
unimplemented behavior; no collection, import, fixture or test-data error. Pre-flight and post-run
`uv run pytest --collect-only tests/acceptance/test_structure_map.py` → `2 tests collected`.

**Clause → what T-001 implements:**

- clause 1 → the added `uv run mypy scripts/` step in the `type-check` job (RED now);
- clause 2 → the behaviour-preserving `union-attr` fix at `scripts/verify_spec.py:74` (RED now);
- clause 3 → the regression guard on the fixed script: **already GREEN at this head** (the report is
  unchanged by the fix, which is exactly what the clause protects). It is not a RED witness and must
  stay GREEN through T-002…T-007;
- NFR-004 → the same fix: only the `mypy scripts/` gate is dirty, the other three pass.

### Sensitivity (the RED is not vacuous)

- `uv run mypy scripts/` → `scripts\verify_spec.py:74: error: Item "TextIO" of "TextIO | Any" has no
  attribute "reconfigure"  [union-attr]` / `Found 1 error in 1 file (checked 3 source files)`, exit 1 —
  identical to finding F-02.
- `grep -rn "mypy scripts" .github/workflows/` → **no hits**; the `type-check` job (`quality.yml:10-25`)
  runs only `uv run mypy src/` (gate) and `uv run ty check src/` (informational).
- The other three NFR-004 gates are clean at this head, so their clauses are GREEN and the NFR-004 RED
  isolates the widened gate: `uv run mypy src/` → `Success: no issues found in 84 source files`;
  `uv run ruff check .` → `All checks passed!`; `uv run ruff format --check .` → `339 files already formatted`.

### Golden baseline for AC-025 clause 3

The pre-fix report of `uv run python scripts/verify_spec.py docs/specs/template.md` (exit 0, byte-stable
over two runs) is embedded in the test as `_VERIFY_SPEC_REPORT_BEFORE_FIX` — 11 lines: the header, the
`\u2500 × 25` rule, 3 `✓ REQ-… has acceptance criteria`, 3 `✓ AC-… has executable test`, 1
`✓ INV-001 has property test`, a blank line, `Traceability: PASS`. Comparison is over
`stdout.splitlines()`, so CRLF/LF differences do not matter (NFR-007 spirit).

Why the baseline cannot be flipped by T-002…T-007: `verify_spec.py` decides the AC/INV lines by matching
the numeric part of **template.md's** IDs (`001`, `002`, `003`, `001`) against test *function names* in
`tests/`. This change's witnesses add names containing `025`, `004`, etc.; a name containing `001`/`002`/`003`
would only add a match to an already-passing line. The report is therefore insensitive to this change.

### Gates run on the new file

- `uv run ruff check tests/acceptance/test_structure_map.py` → `All checks passed!`
- `uv run ruff format --check tests/acceptance/test_structure_map.py` → `1 file already formatted`
- `uv run complexipy tests/acceptance/test_structure_map.py --max-complexity-allowed 15` (the invocation of
  the `complexity` job at `quality.yml:144`) → `All functions are within the allowed complexity`. Scores:
  `_workflow_job_block` 5, `test_ac_025_mypy_covers_scripts` 4, `test_nfr_004_mypy_and_ruff_clean` 3,
  `_opens_job_key` 1, `_run` 0, `_output` 0 — NFR-005 headroom holds (P-56).
- `uv run python scripts/check_traceability.py` → `Traceability: PASS (822 matrix rows, 136 spec IDs,
  748 test functions)`, exit 0. Its PASS is **not** evidence of this spec's rows — the matrix update is
  S3.2's.

### Deviation (recorded): `sys.executable -m <tool>` instead of a nested `uv run <tool>`

AC-025 and NFR-004 name the literal `uv run …` commands. The tests invoke `sys.executable -m mypy|ruff …`
with `cwd=_REPO_ROOT`: under `uv run pytest`, `sys.executable` **is** the uv-managed venv interpreter, so the
tool run is the same one CI runs, whereas a nested `uv run` inside a test re-syncs and rewrites `uv.lock`
(P-42) and would dirty the tree from a test. The CI command itself is still pinned literally by clause 1, and
the `type-check` job step is what CI gates. `encoding="utf-8"` is explicit in the helper because
`verify_spec.py` reconfigures stdout to UTF-8 while the Windows locale codec is cp1252 — without it the
report decodes as mojibake and clause 3 fails for the wrong reason (found and fixed inside this step).

### Hand-off note for T-002

- Reuse the module-level helpers already in the file — `_REPO_ROOT` (`parents[2]`, the worktree root),
  `_run(args)` (`sys.executable` + args, `cwd=_REPO_ROOT`, `capture_output`, `text=True`, `encoding="utf-8"`,
  `check=False`) and `_output(proc)`. `_workflow_job_block` / `_opens_job_key` / `_NFR_004_GATES` /
  `_VERIFY_SPEC_REPORT_BEFORE_FIX` belong to T-001's witnesses — leave them alone.
- `_run` always runs at the repo root. For a temp-tree run either pass absolute paths, or add a `cwd=`
  keyword to `_run` (extend the helper; do not duplicate a second `subprocess.run`).
- Append T-002's 15 node IDs to the **same** file (Q-10: no new test directory), one function per §11 row,
  docstring citing the AC/EDGE/NFR ID. Do not re-declare AC-025/NFR-004.
- Do **not** re-run mypy/ruff/complexipy inside T-002's tests — `test_nfr_004_mypy_and_ruff_clean` already
  owns those four gates. But keep the file ruff-clean **and** ruff-format-clean: NFR-004 asserts `ruff check .`
  and `ruff format --check .` repo-wide, so a formatting slip in T-002 turns NFR-004 RED again.
- Keep every new function under complexipy 15 (`uv run complexipy tests/acceptance/test_structure_map.py
  --max-complexity-allowed 15`); the CI `complexity` job scans `src tests` and no Phase 3–5 step runs it (P-56).
- AC-025 clause 3 must stay GREEN: do not change `docs/specs/template.md`, and do not change
  `scripts/verify_spec.py`'s output (its fix is T-001's Phase 4 work).
- NFR-001's witness (the 2 s budget, `skipif` on a measured calibration run) and NFR-003 (`deptry`) are in
  T-002's set; NFR-003's command rewrites `uv.lock` under `uv run` — revert it before committing (P-42).
- `git checkout -- uv.lock` before the commit; commit locally, push nothing.

### Gate (S3.1 / T-001)

Both §11 node IDs exist with the exact names and assert exactly their AC/NFR clauses ◆; RED observed for
T-001's set with the failure mode recorded (assertion, not setup error) ◆; sensitivity evidence recorded
(the one mypy error, no `mypy scripts/` step in any workflow, the other three gates clean) ◆; ruff check +
ruff format clean on the changed path ◆; complexipy clean at the CI threshold ◆;
`check_traceability.py` PASS ◆; no implementation code, no dependency/coverage/complexity/bandit/`ty`
configuration change ◆. This step does **not** declare the Phase 3 RED gate — S3.2 declares it over all
seven tasks and updates the traceability matrix.



## Phase 3 — S3.1 test derivation, T-002 (2026-10-07)

**Step:** S3.1 (Test & RED phase), DAG task **T-002 — the generator harness** only. One atomic
step; the Phase 3 RED gate is **not** declared here (S3.2 declares it over all seven tasks and
updates the traceability matrix).

**Repository root for every count below (P-57):** `git rev-parse --show-toplevel` →
`C:/workspace/active-projects/python-template_kopie-worktrees/feature/structure-map`
(branch `feature/structure-map`, tree clean before and after the step apart from the two files
this step wrote).

**Inputs read:** `docs/specs/structure-map.md` §4 Definitions, §5 REQ-001/002/003/004/006/007/008,
§7 AC-001/002/003/006/007/008, §9 EDGE-003/004/005/006/007/008/014, §10 NFR-001/003/006 + the
Observability table, §11 rows naming the T-002 nodes; `docs/decisions/ADR-086` in full; the
T-001 section of this file; `tests/acceptance/test_structure_map.py` in full.
`docs/tasks/structure-map.tasks.json` was **not** read (T-002's definition was in the step
prompt, P-66).

### Files written

| File | Lines | Content |
|---|---|---|
| `tests/acceptance/test_structure_map.py` | 124 → **468** | T-002 section appended: 8 module constants, 6 helpers, 10 tests. T-001's tests, `_workflow_job_block`, `_opens_job_key`, `_NFR_004_GATES` and `_VERIFY_SPEC_REPORT_BEFORE_FIX` are untouched. |
| `tests/unit/test_make_map.py` | **251** (new) | 5 tests + 5 helpers (`_run_generator`, `_git_tree`, `_reported_paths`, `_is_unparseable`, `_unopenable`). |

Q-10 placement respected: no new test directory, no third test file. `_run` was extended with a
`cwd: Path = _REPO_ROOT` keyword (default unchanged, so T-001's two witnesses behave exactly as
before) instead of duplicating `subprocess.run`. `_git_tree` is deliberately duplicated in the
two test files rather than imported across them — a cross-test-file import would need a third
shared module, which Q-10's placement forbids.

### The 15 derived tests → spec clauses

| Test node | File | Spec clause(s) | Asserts |
|---|---|---|---|
| `test_ac_001_stdlib_only_and_single_read` | acceptance | AC-001 (1)–(4) | the generator file exists; a generate run exits 0; every top-level import is in `sys.stdlib_module_names`; exactly one file-read call site (`read_text`/`read_bytes`/non-write `open`) in the module AST; `deptry .` exits 0 |
| `test_ac_002_cli_options_and_defaults` | acceptance | AC-002 (1)–(4) | `--help` exits 0 and lists `--root`, `--out`, `--include-private`, `--max-depth`, `--check`, `-h`, `--help`, with `STRUCTURE.md` in the `--out` option segment and `4` in the `--max-depth` segment; `--out here.md` is written against the **cwd**, never under `--root`; with no `--root` the map describes the script's repository root (`scripts/check_traceability.py` present); an unknown option exits 2 with an argparse `usage` line |
| `test_ac_003_file_set_includes_untracked_drops_deleted` | acceptance | AC-003 (1)–(3) | in a throwaway `git init` tree: exit 0; the never-`git add`ed `src/untracked.py` is in the map; the deleted-but-staged `src/gone.py` is not; `src/kept.py` is |
| `test_ac_008_document_shape` | acceptance | AC-008 (1)–(4), INV-003 | line 1 `# Repository structure`; line 2 blank; line 3 the generated-by line; the only `## ` sections are `## Directory tree` then `## Packages`; no timestamp, drive letter/UNC, backslash, absolute POSIX path or `generated in` line; no host name (`platform.node()`) or user name (`getpass.getuser()`) anywhere |
| `test_edge_006_out_parent_directory_created` | acceptance | EDGE-006 (REQ-002) | `--out deep/nested/STRUCTURE.md` exits 0 and writes a non-empty map although the parents did not exist |
| `test_edge_007_non_git_root_falls_back_to_ignore_list` | acceptance | EDGE-007 (1)–(5) | a non-git `--root` exits 0; exactly one non-empty stderr line and it names `git`; `src/mod.py` is mapped; `.venv`, `__pycache__`, `data` never appear; `src/ignored/hidden.py` **is** mapped although `.gitignore` lists `src/ignored/` (the ignore file is never parsed) |
| `test_edge_008_deleted_tracked_file_absent` | acceptance | EDGE-008 | exit 0; `src/gone.py` absent from the map; `gone.py` never mentioned on stderr; `src/kept.py` present |
| `test_edge_014_max_depth_below_one_is_usage_error` | acceptance | EDGE-014 (REQ-002) | `--max-depth 0` and `--max-depth -3` each exit 2, print an argparse `usage` line, and write no output file |
| `test_nfr_001_full_run_under_two_seconds` | acceptance | NFR-001 | a full generate run over this repository exits 0 in under 2 s (skipif-guarded, see calibration) |
| `test_nfr_003_deptry_clean` | acceptance | NFR-003 | `sys.executable -m deptry .` exits 0 — no unused/missing/misplaced dependency |
| `test_ac_006_parse_error_is_hard_failure` | unit | AC-006 (1)–(5), INV-004 | two unparseable files (`src/z_bad.py`, `src/a_bad.py`): exit 4; stderr has exactly one line per path, sorted ascending, each naming the path and `SyntaxError`, each path exactly once; stdout empty; a pre-existing `--out` file is byte-identical afterwards; no new file at `STRUCTURE.md` |
| `test_ac_007_grammar_is_the_running_interpreter` | unit | AC-007 (1)–(3) | PEP 695 sources (`type Alias = int \| None`, `def first[T](…)`) exit 0; `--feature-version 3.12` exits 2 (no grammar option, REQ-002); `--help` mentions neither `feature-version` nor `feature_version` |
| `test_edge_003_newer_syntax_is_hard_failure` | unit | EDGE-003 | a `def f(a: int \| None = None, *, b: list[str] = []) -> dict[str, int]` source exits 4 and is reported once as `SyntaxError`; no output file |
| `test_edge_004_non_utf8_is_hard_failure` | unit | EDGE-004 | `b"x = '\xe9'\n"` exits 4, reported once as `UnicodeDecodeError`, no output file |
| `test_edge_005_unopenable_file_is_hard_failure` | unit | EDGE-005 | a file made unopenable by the probe fixture exits 4, reported once as `PermissionError`/`IsADirectoryError`/`OSError`, no output file |

### RED evidence (observed, not declared)

`red_command` (run from the worktree root):

```
uv run pytest -p no:randomly -v tests/acceptance/test_structure_map.py::<10 nodes> tests/unit/test_make_map.py::<5 nodes>
→ 14 failed, 1 passed in 1.48s
```

Every failure is a `Failed:` (an explicit `pytest.fail` naming the missing generator or the
missing output file) or an `AssertionError` listing the unmet clauses — **no** collection, import
or fixture error, and no `ValidationError`/`ValueError` from invalid test data. Neither test file
imports `scripts.make_map` at module level; the generator is reached only as a subprocess
(`sys.executable <script>`), so the missing module surfaces as a behaviour failure, not an import
error. Representative evidence:

- `test_ac_001` — `Failed: …\scripts\make_map.py does not exist — T-002 Phase 4 has not implemented the generator`
- `test_ac_002` — `Failed: no map file at …\default.md (exit 2): '' "python.exe: can't open file '…scripts\\make_map.py': [Errno 2] No such file or directory"`
- `test_ac_003` / `test_ac_008` / `test_edge_007` / `test_edge_008` — same `_map_text` failure (no map written)
- `test_edge_006` — `AssertionError: clause 1: exit 2: …can't open file…`
- `test_edge_014` — `AssertionError: --max-depth 0: no argparse usage error on stderr: …`
- `test_nfr_001` — `AssertionError: generate run exits 2: …can't open file…`
- `test_ac_006` — `Failed: …make_map.py does not exist…` (its clause set is separately shown to be sensitive: against a generator that reads but never parses, it fails with `clause 1: exit 0, expected 4`, `clause 2: stderr has 0 line(s)`, `clause 4: the pre-existing output file was modified`, `clause 5: no output file may be written`)
- `test_ac_007` / `test_edge_003` / `test_edge_004` / `test_edge_005` — `Failed: …make_map.py does not exist…`

**GREEN witness (must stay GREEN through Phase 4):** `test_nfr_003_deptry_clean` passes at
derivation time — `deptry .` is already clean on the branch, and the witness exists to catch a
Phase 4 that introduces a dependency. This is the same pattern as T-001's AC-025 clause 3.

### Test sensitivity (the tests fail on a wrong implementation, not only on a missing one)

A behaviour-correct stub generator (`Temp/sens_t002/stub_make_map.py`, never committed: CLI with
`ArgumentDefaultsHelpFormatter`, `git ls-files --cached --others --exclude-standard` + the
built-in ignore fallback with one stderr note, `ast.parse` per file → exit 4 with sorted
`path: ExceptionType` lines, `--max-depth < 1` → `parser.error`, the REQ-008 chrome plus a
minimal code-dir tree) was driven through all 15 test functions directly, with `_GENERATOR`
rebound to it (`Temp/sens_t002/driver.py`):

```
15/15 pass against the stub        (same 15 nodes: 14 fail against the absent module, NFR-003 passes both times)
```

The driver also caught two defects in the derived tests themselves, both fixed before this
record: `_run`'s body still pinned `cwd=_REPO_ROOT` after the signature gained the keyword (an
`--out here.md` run leaked a file into the worktree root — removed, `git status` clean), and
`_help_segment` matched the `usage:` line instead of the option line, so the default-value
clauses could not be satisfied by any implementation.

### NFR-001 calibration (the skipif guard)

Measured at this step on this host (CPython 3.14.5, Windows): **0.0114 s** for the fixed
micro-benchmark (parse a 50-function source 40 times, best of 3). `_CALIBRATION_REFERENCE_SECONDS
= 0.011`, so `test_nfr_001_full_run_under_two_seconds` **skips** when the calibration exceeds
0.066 s (6× the reference) — the spec's "skipped on slow CI" rule. It did **not** skip in this
run (calibration 0.0114 s), and the stub's full-repository run completed well inside the 2 s
budget. NFR-001 is not a CI gate (the spec's own wording); the guard keeps it from failing a
slow runner while still asserting the budget on a normal one.

### Quality gates for this step's changed paths

- `uv run ruff check tests/acceptance/test_structure_map.py tests/unit/test_make_map.py` → **All checks passed!**
- `uv run ruff format --check` on the same two paths → **2 files already formatted** (two violations were fixed with a path-scoped `ruff format`; PLR2004 magic-value hits were fixed with named `_EXIT_USAGE` / `_EXIT_UNREADABLE` constants rather than a noqa)
- `uv run complexipy` (CI scope `src` + `tests`) → **All functions are within the allowed complexity**; the highest T-002 function is 13 (`_reported_paths`, `test_ac_008_document_shape`), all others ≤ 11 (P-56)
- Repo-wide `ruff check .` / `ruff format --check .` stay clean: T-001's `test_nfr_004_mypy_and_ruff_clean` fails **only** on the pre-existing `scripts/verify_spec.py:74` mypy error, i.e. the two T-002 files add no ruff or format violation
- `uv run python scripts/check_traceability.py` → **Traceability: PASS (822 matrix rows, 136 spec IDs, 763 test functions)** — no row updates made here (S3.2 owns the matrix)
- Full suite `uv run pytest tests/ -q` → **762 passed, 1 skipped, 16 failed in 213.51s**. Against the T-001 baseline (748 passed, 1 skipped, 2 failed) the delta is exactly the 14 new T-002 REDs; the 2 remaining failures are T-001's own RED witnesses (AC-025, NFR-004). No other test changed state.
- `uv.lock` restored with `git checkout -- uv.lock` before committing (P-42); nothing pushed.

### Decisions and deviations

- **AC-002 clause 3** witnesses "the map describes the script's repository root" with
  `scripts/check_traceability.py` rather than `scripts/make_map.py`: the witness must be
  satisfiable before Phase 4 creates the generator, and a wrong default (`--root` = cwd) still
  fails it, because the temporary cwd contains no `scripts/` directory at all.
- **AC-001 clause 3** is a static AST witness of the read *site*, not a runtime count of reads —
  marked with a `ponytail:` comment naming the ceiling and the upgrade path (an `open` audit hook
  in a wrapper process).
- **EDGE-005** fixture: the probe (`Temp/probe_edge005.py`) established that a directory passed to
  `open()` raises `IsADirectoryError` and that `os.chmod(0o000)` does **not** block reads on this
  Windows host; the fixture therefore uses `os.open(path, os.O_WRONLY)` + `os.fdopen(fd, "wb")`
  for the file's lifetime, which yields `PermissionError` (an `OSError`). The test skips when
  that fixture cannot work (root on POSIX).
- **`--max-depth -3`** is passed as a value (argparse accepts negative numbers when no option
  looks like one), so the test requires the generator's own `>= 1` validation, exactly as
  EDGE-014 states, not only argparse's type check.
- Content-bearing assertions (`src/untracked.py` in the map, the ignore-list directories absent,
  `scripts/check_traceability.py` present) cannot go GREEN before **T-003** renders the Directory
  tree body; they are still valid RED now, and T-002's own Phase 4 scope (module, CLI, file set,
  exit-code dispatcher, chrome) is what makes the *structural* clauses pass.

### Hand-off note for T-003 (Directory tree body)

- T-003's acceptance tests go in `tests/acceptance/test_structure_map.py`, its property tests in
  `tests/property/test_structure_map.py` (new file, Q-10 allows exactly this one).
- Reuse `_git_tree(root, files)` (acceptance) and `_map_text(out, proc)`; `_run(args, cwd=…)` now
  supports temporary trees. Fixture paths belong under `src/` (a code dir) so REQ-009 renders
  them entry by entry — that is what makes the T-002 content assertions work.
- The T-002 chrome assertion pins the section list to exactly `["## Directory tree", "## Packages"]`;
  T-003 must not add a section, and must keep the `# Repository structure` / blank / generated-by
  line order (lines 1–3) or `test_ac_008_document_shape` regresses.
- The stub proves the chrome + a minimal code-dir tree is enough for T-002's assertions to pass;
  T-003's Phase 4 will replace the tree body without touching T-002's tests.
- Nothing in T-002 asserts tree indentation, depth rendering, docstring first lines, count lines
  or `__init__.py` collapsing — those are T-003's nodes (REQ-009/010/011, AC-009/010/011,
  EDGE-009/010/011 and the tree invariants).

## Phase 3 — S3.1 test derivation, T-003 (2026-10-09)

**Step:** S3.1 Derive tests — DAG task **T-003** (Directory tree body, Packages scope and headers,
`--root`-relative path form). **Change:** `structure-map` (FEATURE, spec merged as PR #69).

**Inputs read:** `docs/specs/structure-map.md` §REQ-009/REQ-010/REQ-011/REQ-012/REQ-013/REQ-020,
§Acceptance Criteria (AC-009/010/011/012/013/020), §Invariants (INV-002/INV-003), §Edge Cases
(EDGE-001/002/013/015), §Non-Functional Requirements (NFR-007) — section-scoped reads only (P-66);
the T-003 entry of `.github/task-runner/tasks.json` in full (`requirements`,
`acceptance_criteria`, `invariants`, `edge_cases`, `non_functional`, `tests_to_create`,
`red_command`, `green_command`, `allowed_files`, `implementation_steps`, `design_constraints`,
`completion_gates`, `dependencies`); the T-001/T-002 sections of this file; the existing harness in
`tests/acceptance/test_structure_map.py` and `tests/unit/test_make_map.py`. `docs/tasks/structure-map.tasks.json`
was **not** read (P-66).

**Recovered work.** A previous S3.1 (T-003) execution was interrupted mid-step and left
`tests/acceptance/test_structure_map.py` modified (+288 lines: the `_TREE_FILES` fixture, helpers
and the five acceptance nodes) and `uv.lock` dirty, with no commit and no handoff. `uv.lock` was
restored first (F-9 / P-74). The uncommitted block was reviewed clause by clause against the spec,
not trusted: it was kept (fixture shape, `_tree_entries`, `_section_lines`, `_group_body`) and
corrected — the prune-marker witness was rewritten to `_prune_marker_in_branch` (a branch-scoped
scan, so a marker from another top-level branch can never be attributed to `src/backend/`), the
code-dir entry assertions were extracted to `_code_dir_entry_failures` (PLR0912, 14 branches), an
unused local was removed (F841), the missing `tests/README.md` fixture entry was added (REQ-009
clause 2 renders non-`.py` entries under a code dir), and the sorting/order clauses were added.

### Files written (exactly T-003's `allowed_files` test paths)

| File | Change | Nodes |
|---|---|---|
| `tests/acceptance/test_structure_map.py` | +324 (T-003 block appended) | 5 |
| `tests/unit/test_make_map.py` | +257 / −1 (T-003 block appended; `_run_generator` widened to `root: Path | str`) | 6 |
| `tests/property/test_structure_map.py` | new, 256 lines | 2 |

No source file was created or edited: `scripts/make_map.py` (T-003's `source_files`) is Phase 4 work.

### Derived tests → spec clauses (13 nodes, all of T-003's `tests_to_create`)

| Node | IDs | Clauses pinned |
|---|---|---|
| `acceptance::test_ac_009_tree_code_dirs_full_other_dirs_counted` | AC-009 / REQ-009 / EDGE-015 | clause 1 top-level files listed by name, sorted, **before** the code dirs; clause 2 every entry under a code dir — **of any file type** — on its own line, indented `2 × (segments − 1)`, sorted, plus a line for each code dir and for `src/backend/`, `src/backend/settings/`, `tests/unit/`; clause 3 exactly one count line per other top-level dir, carrying the file count and the role label (`docs/ — 3 files (process record)`, `.github/ — 2 files (CI and tooling)`), and nothing from a count-only dir rendered entry by entry |
| `acceptance::test_ac_010_max_depth_prunes_tree_only` | AC-010 / REQ-010 | `--max-depth 2` renders no `src/backend/*` entry but still `src/backend/`; that branch carries a `(+N dirs, M files not shown)` marker; the `scripts/` branch carries **no** marker (all its entries are at depth 2); the Packages module set is identical at `--max-depth 2` and at the default 4 and equals every `src/` fixture module |
| `acceptance::test_ac_011_packages_scope` | AC-011 / REQ-011 | Packages lists exactly the 15 in-scope fixture modules — every `.py` under `src/`, `scripts/`, `migrations/`, plus `tests/conftest.py`, `tests/settings_test_helpers.py`, `tests/unit/conftest.py` (the `tests/` rule matches the **file name at any depth**) — and not `tests/unit/test_deep_behaviour.py` / `tests/plain_helpers.py` |
| `acceptance::test_ac_012_package_header_and_exports` | AC-012 / REQ-012 | exactly one `### ` header shows `` `backend.settings` `` and `src/backend/settings/`; one `exports:` line in that group listing the `__init__.py` `__all__` names sorted (`Alpha` before `Zeta`) and **not** the merely imported `Registry`/`Model`; every header ends with a directory path, no duplicates, and the header set equals the set of containing directories of Packages-scope modules |
| `acceptance::test_edge_015_unlabelled_dir_counted_without_label` | EDGE-015 / REQ-009 clause 3 | `notes/` gets exactly one indent-0 count line, counts all 3 files, contains no `(` (no role label), and `notes/deep/` is not rendered entry by entry |
| `unit::test_ac_013_module_header_and_summary` | AC-013 / REQ-013 | header `#### src/with_doc.py (4 lines)` — the file's own `splitlines()` count, not its non-blank count — followed by the docstring's first line; `src/no_doc.py` renders `#### src/no_doc.py (2 lines)` and **no** summary line |
| `unit::test_edge_001_missing_docstring_renders_no_summary` | EDGE-001 (module half) / REQ-013 | the header still renders for `src/no_doc.py` and `src/comment_only.py`, carries no summary line, and does not end with `:` |
| `unit::test_edge_002_empty_file_renders_header_only` | EDGE-002 / REQ-013 | `src/empty.py` renders `#### src/empty.py (0 lines)` and nothing else, exit 0, nothing on stderr |
| `unit::test_edge_013_package_without_exports` | EDGE-013 / REQ-012 | `src/nopub_pkg/` (`from ._internal import _helper`, no `__all__`) renders **no** `exports:` line; `src/pub_pkg/` (public imports, no `__all__`) renders one line with those names sorted |
| `unit::test_ac_020_paths_are_relative_posix` | AC-020 / REQ-020 | no backslash, drive letter/UNC, or absolute POSIX path anywhere; none of `str(root)`, `root.as_posix()`, `str(root.parent)` appears; the module-header set equals the fixture's `--root`-relative paths with their line counts |
| `unit::test_nfr_007_output_identical_across_platforms` | NFR-007 / REQ-020 | the same tree at two different absolute locations renders byte-identical output; `--root` spelled as `str(root)` vs `root.as_posix()` renders byte-identical output; the bytes are LF-only |
| `property::test_inv_002_no_module_hidden_by_pruning` | INV-002 (hypothesis, 12 examples) | for any generated tree (3–10 module paths, 1–4 segments deep, under the four code dirs) and any `--max-depth` 1–5: every `.py` under a code dir at depth ≤ max-depth is in the tree and none deeper is; the Packages set equals the REQ-011 scope; the fixed `.github/hooks/ruff-post-edit.py` + `.github/workflows/ci.yml` appear in neither section and `.github/` has one count line for 2 files |
| `property::test_inv_003_no_absolute_path_or_timestamp` | INV-003 (hypothesis, 12 examples) | no timestamp, drive letter/UNC, backslash or absolute POSIX path; no `platform.node()` / `getpass.getuser()` value; none of `str(root)`, `root.as_posix()`, `str(base)` |

### RED evidence (observed, not declared)

Pre-flight `uv run pytest --collect-only` over the three files: **30 tests collected, no import or
collection errors** (13 T-003 nodes present).

T-003's `red_command` (the 13 nodes, verbatim from the DAG) — **13 failed, 0 passed in 2.07s**.
Every failure is the same assertion failure on unimplemented behaviour, e.g.

```text
E  Failed: C:\workspace\...\feature\structure-map\scripts\make_map.py does not exist
   — T-002 Phase 4 has not implemented the generator
```

That is a valid RED: a `pytest.fail` assertion raised inside the test body, not a collection error,
not a fixture setup error, and not a `ValidationError` from out-of-domain test data (the property
strategies emit in-domain paths only: `pkg`/`sub`/`deep` segments, `mod.py`/`conftest.py`/
`helpers_test_helpers.py`/`a.py`/`b.py` names).

No previously green test was broken: the three touched files run as a whole give **29 failed,
1 passed** = the 16 pre-existing REDs (T-001 `test_ac_025…`/`test_nfr_004…`, T-002's 14) + the 13
new T-003 REDs, with `test_nfr_003_deptry_clean` the only GREEN node in them. The full suite is a
Phase 5 gate and was not run here.

### Test sensitivity (P-68)

A behaviour-correct stand-in generator (`stub_v2.py`, written **outside** the repository, in
`%LOCALAPPDATA%/Temp/sens_t003/`, so it can never be committed) implements exactly T-003's clauses
and nothing else (no symbols, no `--check`). The driver imports the three test modules, rebinds
their `_GENERATOR` constant to the stub and calls all 13 nodes.

- **Correct stub: 13/13 nodes pass** — the tests are satisfiable, so the RED is missing behaviour,
  not a broken test.
- **Wrong-implementation matrix: 25/25 mutations caught**, each by the semantically right node:

| Mutation (one broken clause) | Caught by |
|---|---|
| tree skips non-`.py` entries under a code dir | AC-009 |
| a code dir rendered as a count line instead of in full | AC-009, AC-010, INV-002 |
| count line counts only top-level files | AC-009, EDGE-015, INV-002 |
| an unlabelled dir gets a role label | EDGE-015 |
| tree renders base names instead of paths | AC-009, AC-010, INV-002 |
| `--max-depth` ignored | AC-010, INV-002 |
| pruned one level too early | AC-009, AC-010, INV-002 |
| a prune marker emitted when nothing is hidden | AC-010 |
| hidden files counted as dirs (marker form) | AC-010 |
| Packages ignores a nested `conftest.py` | AC-011, AC-012, INV-002 |
| Packages ignores `*_test_helpers.py` | AC-011, INV-002 |
| one group header per module, not per directory | AC-012 |
| package header without its import name | AC-012 |
| an `exports:` line always rendered | EDGE-013 |
| `exports:` lists imports instead of `__all__` | AC-012 |
| module header without the line count | AC-010, AC-011, AC-013, AC-020, EDGE-001, EDGE-002, INV-002 |
| header counts non-blank lines | AC-013, AC-020 |
| module header ends with a colon | AC-013, AC-020, EDGE-001, EDGE-002 |
| a summary line rendered for an undocumented module | AC-013, EDGE-001, EDGE-002 |
| paths rendered absolute | 12 of 13 nodes |
| paths rendered with backslashes | AC-009, AC-010, AC-020, INV-002, INV-003 |
| a timestamp in the generated-by line | INV-003 |
| output written with CRLF | NFR-007 |
| top-level files not sorted first | AC-009 |
| code-dir entries not sorted | AC-009 |

The driver also exposed two defects **in the artifacts themselves** (not in the tests), both fixed
and re-run: the stub never collected public imports for the `exports:` fallback (EDGE-013 clause 3
caught it — the witness works in both directions), and the first matrix run resolved its relative
paths against the **primary** worktree, so 22 of its 25 mutations never applied and were counted as
caught; the re-run with absolute paths is the evidence above. A mutation whose replacement text was
a `SyntaxError` (`sorted(<genexpr>, reverse=True)`) was rewritten to valid syntax so it witnesses
the ordering clause rather than the parse failure.

### Quality gates (this step's changed paths only, P-6)

- `uv run ruff check tests/acceptance/test_structure_map.py tests/unit/test_make_map.py tests/property/test_structure_map.py` → **All checks passed!**
- `uv run ruff format --check` on the same three paths → **3 files already formatted**
- No whole-repo lint sweep (the Phase 5 gate), no `mypy`/`deptry`/docs build in this step.
- `uv.lock` restored before the commit (F-9 / P-74).

### Decisions and deviations

- **Depth = path segments** (`src/` = 1, `src/backend/` = 2, `src/backend/utils.py` = 3), and tree
  indent = `2 × (segments − 1)`, derived from AC-010's `--max-depth 2` example (src/backend/ renders,
  nothing under it). REQ-009's "indented two spaces per level" is read with that example.
- **Deliberate under-assertions** (not encoded rather than guessed): the prune marker's **numbers**
  — REQ-010 defines three marker forms (`(+N dirs not shown)`, `(+N files not shown)`,
  `(+N dirs, M files not shown)`) but not whether N/M count direct children or the whole hidden
  subtree, so AC-010 asserts the combined *form* and the absence of a marker where nothing is
  hidden, never the values; the relative order of the four code dirs (determinism is T-005/INV-001);
  the docstring-summary normalization (REQ-018 is T-004's gate, so AC-013 asserts only that the
  summary line follows the header); and any NFR-002 file count (those are base-commit numbers).
- **`tests/README.md` in the fixture** — REQ-009 clause 2 renders every tracked file under a code dir
  regardless of extension (this repository has 9 such files), so a `.py`-only tree implementation fails.
- **`.github/hooks/post_edit.py` + `docs/sub/c.md` + `notes/deep/three.md` in the fixture** — the
  count-only directories must not be rendered entry by entry, and INV-002's last clause (a `.py`
  outside a code dir appears only in its count line) needs a second file in that directory.
- **Property tests carry their own harness copy** (`_git_tree`, `_render`, `_GENERATOR`) rather than
  importing the acceptance file or adding a shared module: T-003's `allowed_files` lists only the
  three test files, and Q-10 forbids a third shared module (the acceptance and unit files already
  each carry their own copy for the same reason).
- **Hypothesis RED hygiene**: each node `pytest.fail`s when `scripts/make_map.py` is absent *before*
  the inner `@given` check runs, so the RED is one clean assertion failure rather than 12 shrunk
  example failures; each example builds its tree in a fresh `TemporaryDirectory` because Hypothesis
  reuses the function-scoped `tmp_path`. `@settings(max_examples=12, deadline=None,
  suppress_health_check=[HealthCheck.too_slow])` per the repo convention.
- **`_EXPECTED_PACKAGE_COUNT = 15`** is a hand-counted cross-check of the derived scope set, so a
  bug in the test's own `_in_packages_scope` cannot silently agree with itself.
- **PLR0912** (max 12 branches, only PLR0913 is ignored) forced the clause loops of AC-009 into
  `_code_dir_entry_failures(entries) -> list[str]`; **PLR2004** forced the `_SUMMARY_LINE` constant.

### What Phase 4 (T-003) must implement for these nodes

Tree: top-level files sorted first, then the four code dirs in full (one line per directory and per
entry, any extension, sorted, indent `2 × (segments − 1)`), every other top-level dir as one
`<name>/ — <N> files[ (label)]` line from the fixed role table; `--max-depth` prunes the tree only,
emitting the REQ-010 marker form that matches what is hidden. Packages: one group header per
containing directory — ``### `import.name` — dir/`` for a package (the path relative to `src/`,
`/`→`.`; outside `src/` the whole path), `### dir/` for a plain directory — then
`#### <relpath> (<N> lines)` per module (N = `splitlines()`), the docstring first line only when the
module has one, and one `exports:` line for a package `__init__.py` (`__all__` if defined, else the
public names it imports, sorted, neither → no line). Output: `--root`-relative POSIX paths only, LF
newlines, no timestamp/host/user/absolute path, and `--root` accepted in either host spelling.

### Hand-off note for T-004 (symbols, docstring summaries)

- Reuse `unit::_module_block(map_text, path)` (a module's header plus its body lines) and
  `unit::_group_block(map_text, dir_path)`; the acceptance file's `_group_body(map_text, needle)`
  slices one group.
- T-003 pins the module header form `#### <path> (<N> lines>` and that a docstring summary is the
  line immediately after it; it does **not** pin REQ-018's summary normalization — T-004 may
  normalize that line, it may not change the header form or add a line before it.
- `test_ac_020_paths_are_relative_posix` asserts the **complete** module-header set for its fixture,
  so T-004's symbol lines must appear *below* the header, never replace it.
- The T-003 fixture `_T003_FILES` (unit) and `_TREE_FILES` (acceptance) are shared by the later
  tasks' nodes in the same files: adding a fixture entry changes `_EXPECTED_PACKAGE_COUNT` and the
  `_GROUP_DIRS` cross-check — extend them deliberately, not incidentally.

## Phase 3 — S3.1 test derivation, T-004 (2026-10-09)

**Step:** S3.1 Derive tests — DAG task **T-004** (symbol inventory: signatures, decorators,
visibility, class fields, summaries), one file, 7 nodes. **Change:** `structure-map` (FEATURE, spec
merged as PR #69, merge commit `570bfbc`).

**Inputs read:** `docs/specs/structure-map.md` §REQ-014 (line 270, with its rendering block),
§REQ-015/REQ-016/REQ-017/REQ-018 (297–325), §Acceptance Criteria AC-014…AC-018 (424–428), §Edge
Cases EDGE-011/EDGE-012 (464–465) — section-scoped reads only (P-66); the T-004 entry of
`.github/task-runner/tasks.json` in full; the T-003 section of this file (its Phase-4 contract and
its hand-off note for T-004); the existing harness in `tests/unit/test_make_map.py`. No whole-file
read of the spec or of this file (P-66).

### Files written (exactly T-004's `allowed_files` test paths)

| File | Change | Nodes |
|---|---|---|
| `tests/unit/test_make_map.py` | +636 (T-004 block appended) | 7 (11 → 18 collected) |

Nothing else: `scripts/make_map.py` (T-004's `source_files`) is Phase 4 work, the shared fixtures
`_T003_FILES` / `_TREE_FILES` were **not** touched (so `_EXPECTED_PACKAGE_COUNT` and `_GROUP_DIRS`
are unchanged for T-005), and no other task's tests, `docs/todo/`, `docs/questions/` or
`tasks.json` were modified (status sync is S4.4).

New helpers in that file (all reuse the T-002/T-003 harness — `_git_tree`, `_map_text`,
`_run_generator`, which already accepts `Path | str`): `_t004_tree` (fixture-parse guard),
`_module_body` (body lines after a `#### ` header, **indent preserved** — T-003's `_module_block`
strips it, so it cannot witness REQ-014's indents), `_symbol_lines`, `_all_symbol_lines`,
`_section_headers`, `_seq_failures`, and the field-fixture generators `_field_source` /
`_field_symbol_lines`. The module header form `#### <path> (<N> lines)` is unchanged (T-003
constraint).

### Derived tests → spec clauses (7 nodes, all of T-004's `tests_to_create`)

| Node | IDs | Clauses pinned |
|---|---|---|
| `test_ac_014_symbol_inventory_and_unparsed_signatures` | AC-014 / REQ-014 | the exact 13-line symbol sequence of one module: classes first in source order (`Widget`, `Outer`), each class's annotated fields then its methods, a nested class as a `  - class \`Inner\`` member line with **its own members at 4 spaces**, module-level functions after the classes in source order (`spaced`/`fetch` render after the classes although they precede them in the source), `async ` kept inside the backticks, bases rendered ``Widget(Base, Mixin)``; the signature text is the `ast.unparse` rendering, not the source spacing (`def spaced(  a : int ,b : str = "xy" )` → ``spaced(a: int, b: str='xy')``); the ≤ 20-character default rule at its boundary (1-, 4- and 20-character defaults shown; 21-, 23-character ones omitted with their annotations kept); a function-local class, module-level assignments, imports and an `if TYPE_CHECKING` block never render; every symbol rendered exactly once |
| `test_ac_015_decorators_render_as_prefix` | AC-015 / REQ-015 | the exact 10-line sequence with `@logged_class` on a class, `@property`/`@staticmethod`/`@classmethod`/`@override` on methods, `@logged` on a function, the stacked pair `@logged @cache` in source order, the attribute chain `@pytest.fixture`, and the decorator **call** rendered as its `ast.unparse` text `@lru_cache(maxsize=8)`; plus a per-decorator presence check so a missing prefix is attributed to the decorator that went missing |
| `test_ac_016_private_symbols_and_dunders` | AC-016 / REQ-016 | `__init__` and `__repr__` rendered exactly once in **both** runs; the four `_name` symbols (`_internal`, `_Helper` and its method, `_private`) rendered only with `--include-private` (exact-line equality — a substring test would false-positive on the public name `visible_in_private_module`); the `#### ` headers of `src/_hidden.py`, `src/_pkg/__init__.py` and `src/_pkg/inner.py` present in both runs, and the whole `### `/`#### ` header list byte-identical between them |
| `test_ac_017_class_fields_capped_untyped_omitted` | AC-017 / REQ-017 | a 17-field class (one `Field(default="a")`, one `= True`) renders each annotated field as `  - \`name: annotation\`` with **no default and no `Field(` payload**, in source order; the unannotated assignment renders neither as a field nor inside the elided count; exactly 15 field lines then `  - … +2 fields` |
| `test_ac_018_summary_normalization` | AC-018 / REQ-018 | a docstring whose first logical line spans three physical lines with doubled spaces and backticks renders as one normalized summary; the module summary line (the line right after the `#### ` header) is normalized the same way; an empty docstring, no docstring, and a second paragraph render no summary and **no trailing `:`** |
| `test_edge_011_field_cap_marker` | EDGE-011 / REQ-017 | 15 fields → 15 lines and no marker; 16 → 15 lines + `  - … +1 fields`; 20 → 15 lines + `  - … +5 fields`; exactly two marker lines in the module; the at-cap class's own 16 lines contain no `…` |
| `test_edge_012_long_summary_truncated` | EDGE-012 / REQ-018 | a 135-character normalized summary renders as its first 100 characters + `…` and its tail never appears; a 100-character summary renders in full with no marker; the raw docstring carries backticks and doubled spaces **inside** the first 100 characters, so normalization must precede truncation |

### RED evidence (observed, not declared)

`uv run pytest --collect-only tests/unit/test_make_map.py -q` → **18 tests collected in 0.13s**
(11 before the block, 7 added, no collection error — the generator is driven as a subprocess, never
imported).

T-004's `red_command`, run verbatim (targeted only — the full suite is the Phase 5 gate):

```text
uv run pytest tests/unit/test_make_map.py::test_ac_014_symbol_inventory_and_unparsed_signatures \
  tests/unit/test_make_map.py::test_ac_015_decorators_render_as_prefix \
  tests/unit/test_make_map.py::test_ac_016_private_symbols_and_dunders \
  tests/unit/test_make_map.py::test_ac_017_class_fields_capped_untyped_omitted \
  tests/unit/test_make_map.py::test_ac_018_summary_normalization \
  tests/unit/test_make_map.py::test_edge_011_field_cap_marker \
  tests/unit/test_make_map.py::test_edge_012_long_summary_truncated -v

E  Failed: …\scripts\make_map.py does not exist — T-002 Phase 4 has not implemented the generator
tests\unit\test_make_map.py:56: Failed
============================== 7 failed in 1.05s ==============================
```

**Valid RED:** 7/7 fail on the missing behaviour, raised as a `pytest.fail` assertion inside the
test body; no collection, import, fixture or setup error, and no `ValidationError`/`ValueError`
from test data. Fixture data was validated before the gate: `_t004_tree` `ast.parse`s every fixture
module and fails the test if it does not parse, and the EDGE-012 fixture asserts its own lengths
(135 > 100, exactly 100 at the boundary).

### Test sensitivity (P-68)

A behaviour-correct stand-in generator (`stub_t004.py`, written **outside** the repository, in
`%LOCALAPPDATA%/Temp/sens_t004/`, so it can never be committed) extends the T-003 stub with the
symbol layer and nothing else (no `--check`). The driver imports this test module, rebinds
`_GENERATOR` to the stub, and calls all 7 nodes.

- **Correct stub: 7/7 nodes pass** — the tests are satisfiable, so the RED is missing behaviour,
  not a broken test. Building the stub corrected four expectation errors **in the tests** before
  they were trusted: the member bullet `  - ` was missing from the field/method expectations
  (REQ-014/REQ-017 render every member as a bullet), the AC-018 expectation had functions before
  classes (REQ-014 groups classes first), and the EDGE-011 expectation listed all 16/20 field lines
  instead of 15 + marker.
- **Wrong-implementation matrix: 32/32 mutations caught**, each by the semantically right node:

| Mutation (one broken clause) | Caught by |
|---|---|
| fields not capped (all rendered) | AC-017, EDGE-011 |
| field-cap elision marker missing | AC-017, EDGE-011 |
| elision count off by one | AC-017, EDGE-011 |
| unannotated class assignments rendered as fields | AC-014, AC-017 |
| field default value rendered | AC-014, AC-017 |
| positional defaults always included | AC-014 |
| keyword-only defaults always included | AC-014 |
| short positional default dropped (boundary too tight) | AC-014 |
| short keyword-only default dropped (boundary too tight) | AC-014 |
| decorators dropped | AC-015 |
| decorator call rendered without its `@` | AC-015 |
| function-local class rendered | AC-014 |
| private symbols always rendered | AC-016 |
| private symbols hidden even with `--include-private` | AC-016 |
| dunder methods treated as private | AC-014, AC-016 |
| `--include-private` also changes the module set | AC-016 |
| summary not normalized (raw first physical line) | AC-018, EDGE-012 |
| backticks kept in summaries | AC-018, EDGE-012 |
| long summary not truncated | EDGE-012 |
| summary truncated at 80 | EDGE-012 |
| truncation marker missing | EDGE-012 |
| marker also on an exactly-100-character summary | EDGE-012 |
| module summary line dropped | AC-018 |
| module-level functions rendered before classes | all 7 nodes |
| methods rendered before fields | AC-014, AC-015, AC-017, EDGE-011 |
| method line uses the `def` keyword | AC-014, AC-015, AC-016 |
| method indent lost | AC-014, AC-015, AC-017, EDGE-011 |
| nested class not rendered | AC-014 |
| nested class members not indented deeper | AC-014 |
| `async ` prefix dropped | AC-014 |
| class bases dropped | AC-014 |
| trailing `:` kept when there is no summary | all 7 nodes |

The driver itself produced two false results on the first runs and both were fixed before the
matrix above was trusted: its per-node handler caught `Exception` but `pytest.fail` raises
`_pytest.outcomes.Failed` (a `BaseException`), so one mutation crashed the driver instead of being
recorded; and two mutation search strings matched the **first** occurrence of an identical
statement in another stub function (`_exports` vs `_symbol_lines`), so one mutation applied to
nothing and was reported as “not caught by any test”. The re-run uses unique search strings and
fails loudly when a mutation does not apply or does not compile.

### Quality gates (this step's changed paths only, P-6)

- `uv run ruff format tests/unit/test_make_map.py` → **1 file reformatted / already formatted**
- `uv run ruff check tests/unit/test_make_map.py` → **All checks passed!** (one F541
  f-string-without-placeholders was fixed by promoting the decorator-call rendering to the named
  constant `_AC015_CALL_DECORATOR`, which the expectation and the clause check now share)
- No whole-repo lint sweep (the Phase 5 gate); no `mypy`/`deptry`/docs build in this step.
- `uv run python scripts/check_traceability.py` was **not** run and `docs/verification/traceability.md`
  was **not** touched — as in T-001/T-002/T-003, the matrix rows for this spec are S3.2's work.
- `uv.lock` restored before the commit (F-9 / P-74); `git status` clean afterwards.

### Decisions and deviations

- **Fixture module sources are embedded as `"""…"""` literals with single-quoted docstrings** —
  ruff `flake8-quotes multiline-quotes="double"` (Q001) forbids `'''` for the outer literal, so the
  inner docstrings use `'`; the one multi-line docstring (AC-018) uses `'''` **inside** the outer
  `"""`, which is valid Python. The first draft used a single-quoted multi-line docstring — an
  unterminated string literal — and `_t004_tree` surfaced it as invalid test data rather than as a
  RED; that guard is why the RED gate was never contaminated.
- **`_t004_tree` parses every fixture and `pytest.fail`s on a `SyntaxError`**: an unparseable fixture
  would otherwise reach the generator and exit 4 (EDGE-003), which reads like a valid RED but
  witnesses nothing.
- **Exact rendered-line sequences, not per-line regexes.** Every node compares the module's symbol
  lines as a list, so grouping order, indent, bullet form, decorator prefix order and the marker
  line are all pinned at once; the extra per-clause checks only add attribution (which decorator
  went missing, which default leaked) and the “never rendered” absence checks.
- **Exact-sequence fixtures have no module docstring** (except AC-018's, which exists precisely to
  witness module-summary normalization); the summary line is asserted separately there, so the
  bullet sequence stays unambiguous.
- **The nested class sits inside a class with no fields and no methods.** REQ-014 enumerates
  “fields first, then methods” and does not fix where a nested class renders relative to them, so
  the witness pins its **form and indent** without asserting an order the spec does not state.
- **AC-017 interleaves the unannotated assignment between the 15th and 16th annotated field.** An
  implementation that counts unannotated assignments toward the cap emits `+3 fields` instead of
  `+2 fields`, so the interleaving is a mutation witness, not noise.
- **Deliberate under-assertions** (not encoded rather than guessed): the position of a nested class
  relative to its enclosing class's fields and methods (above); keyword bases
  (`class C(metaclass=M)`) — REQ-014 writes `Name(Base, ...)` and the spec never states how a
  keyword base renders; a decorator on a nested class, and a private nested class under
  `--include-private`; and the truncation reading — the tests pin “100 characters of normalized
  text, then `…`” (the AC-018/EDGE-012 wording), so an implementation that fits the marker **inside**
  the 100-character budget fails; that reading is stated here rather than left implicit.

### What Phase 4 (T-004) must implement for these nodes

Symbol layer per module (`#### ` header, then the optional summary line, then the symbol lines):
module-level classes in source order, then module-level functions in source order; a class line
`- ` + decorators + `class ` + backticked ``Name(Base, ...)`` + `: ` + summary; a module function
line `- ` + decorators + `def ` + backticked signature (`async ` stays inside the backticks) +
`: ` + summary; a member line `  - ` + decorators + backticked signature + `: ` + summary, **no
`def` keyword**; a nested class is a member line `  - class \`Inner\`: …` whose own members are one
indent level deeper (4 spaces). Fields: `ast.AnnAssign` with a `Name` target only, rendered
`  - \`name: annotation\`` with no default and no `Field(...)` payload, in source order, capped at
**15**, then `  - … +N fields`; unannotated `Assign` statements are never rendered and never
counted. Signatures, annotations, bases, decorator calls and field annotations come from
`ast.unparse`; a parameter default is kept only when its unparsed text is ≤ **20** characters
(keyword-only defaults follow the same rule). Summary: `ast.get_docstring`, first paragraph, whitespace
runs collapsed, backticks removed, and if longer than **100** characters `text[:100] + "…"`; no or
empty docstring → no summary and no trailing `:`. Visibility: public = not `_`-prefixed, plus every
dunder; `--include-private` changes **only** which symbols render — never a module or package.
Classes/functions inside a function body, module-level assignments, imports and
`if TYPE_CHECKING` blocks are never rendered. The 20/15/100 constants stay hardcoded and
non-configurable. The `#### <path> (<N> lines)` header form and the position of the module summary
line are T-003's and must not change — six other nodes assert them.

### Hand-off note for T-005 (`--check`, `--help`, determinism)

- The T-004 block adds **no** entry to `_T003_FILES` / `_TREE_FILES` and changes no existing
  expectation, so the shared-fixture counts T-005 depends on are untouched.
- `_module_body` / `_symbol_lines` / `_all_symbol_lines` / `_section_headers` are the slicing
  helpers for any later unit node that needs an indented body; `_module_block` (T-003) strips
  indentation and must not be used for indent assertions.
- REQ-018 normalization now applies to the module summary line too: T-003's AC-013 witness asserts
  only that a summary line follows the header, so it stays GREEN under a normalized rendering —
  do not “fix” it by weakening it.


## Phase 3 — S3.1 test derivation, T-005 (2026-10-09)

Task **T-005** — `--check` semantics, the completed exit-code contract, determinism and hook-clean
output (REQ-004/005/019 · AC-004/005/019 · EDGE-009/010/016 · INV-001/004/005/006). Tests derived
from the merged spec (`docs/specs/structure-map.md` §5 REQ-004/005/019, §6 INV-001/004/005/006, §7
AC-004/005/019, §9 EDGE-009/010/016, §10 Observability, §13 newline-normalisation note) and from
ADR-085 Decision bullet 4. `scripts/make_map.py` is **not** implemented (Phase 4 owns it).

### Files written (exactly T-005's `allowed_files` test paths)

| File | Added |
|---|---|
| `tests/acceptance/test_structure_map.py` | 6 nodes + the T-005 helper block (`_generate`, `_check`, `_generate_fixed_point`, `_stale_message`, `_missing_message`, `_one_line`, `_hook_clean`, `_active_hook_ids`, `_EXIT_STALE/_EXIT_MISSING/_EXIT_UNPARSEABLE/_RUN_COMMAND/_PRE_COMMIT`) |
| `tests/property/test_structure_map.py` | 4 Hypothesis nodes + `_check_run`, `_hook_clean`, `_snapshot`, `_EXIT_MISSING` |
| `docs/verification/structure-map.md` | this section |

No other file touched: `scripts/make_map.py`, `.pre-commit-config.yaml`, `tasks.json`, `docs/todo/`,
`docs/questions/` and every other task's tests are unchanged. No `.gitattributes` was created.

### Derived tests → spec clauses (10 nodes, all of T-005's `tests_to_create`)

| Node | ID(s) | Witness |
|---|---|---|
| `test_ac_004_exit_code_contract` | AC-004 / REQ-004 | every table row (0/1/2/3/4) in its mode; `1`/`3` never in generate mode (a stale map is rewritten, a missing one is created); precedence `2→4→3→1→0` — unparseable+missing → 4, unparseable+stale → 4 not 1 |
| `test_ac_005_check_byte_exact_single_message_exit_3` | AC-005 / REQ-005 | one extra byte → exit 1 and exactly `<out> is out of date — run uv run python scripts/make_map.py` on stdout, stderr empty; a whitespace-only difference is still stale; the message names `--out` as given (`map.md`, `nested/map.md`, the default `STRUCTURE.md`); missing `--out` → exit 3 + the pinned missing line; CRLF-only → exit 0 and silent |
| `test_ac_019_double_run_byte_identical_and_hook_clean` | AC-019 / REQ-019 | two runs on an unchanged tree → identical bytes; no CR; no trailing whitespace on any line; exactly one final LF; the two hooks named in `.pre-commit-config.yaml` (asserted active) leave the bytes unchanged |
| `test_edge_009_untracked_file_listed_then_stale_on_clone` | EDGE-009 | an untracked-not-ignored `src/scratch.py` (`git status` = `??`) is listed in the map; the same tracked tree without it (the clone) exits 1 with the pinned line; regeneration drops it and then exits 0 |
| `test_edge_010_hand_edited_map_is_stale` | EDGE-010 | a hand-appended note → exit 1 + the pinned line; conflict markers appended → exit 1; regeneration restores the bytes and `--check` exits 0 |
| `test_edge_016_crlf_checkout_is_not_stale` | EDGE-016 / REQ-005 | explicit CRLF bytes of the LF render → exit 0, silent; CRLF **+ one byte** → exit 1 (the normalisation is exactly `\r\n` → `\n`); generate rewrites LF |
| `test_inv_001_render_is_deterministic` | INV-001 / REQ-019 | Hypothesis: two runs byte-identical; the same tree created in the opposite order renders identically |
| `test_inv_004_check_matches_byte_equality` | INV-004 / REQ-005 | Hypothesis: exit 0 for the render and for its CRLF form; exit 1 for added / removed / reordered / whitespace-only variants (each asserted to be a real difference first) |
| `test_inv_005_check_writes_nothing` | INV-005 | Hypothesis: the `{path: bytes}` snapshot of the whole working tree is identical before/after a fresh `--check`; a missing `--out` exits 3, is **not** created, and the snapshot is unchanged |
| `test_inv_006_output_is_hook_clean` | INV-006 / REQ-019 | Hypothesis: no CR, exactly one final LF, and the trailing-whitespace / end-of-file-fixer transforms are the identity on the render |

All four `INV-*` nodes use Hypothesis with the file's existing convention (`max_examples=12`,
`deadline=None`, `suppress_health_check=[too_slow]`, a per-example `TemporaryDirectory`); every
test's docstring cites its ID.

### RED evidence (observed, not declared)

`red_command` run verbatim (targeted, never the full suite), 2026-10-09:

```text
10 failed in 1.69s          # 0 collection errors, 0 setup errors
```

Failure mode per node — every one is `Failed`/`AssertionError` on the unimplemented behavior
(`scripts/make_map.py` does not exist yet), never an import/fixture error:

| Node | Failure (first line) |
|---|---|
| `test_ac_004_exit_code_contract` | `AssertionError: table row 0: generate success exits 2: "…can't open file '…scripts\make_map.py'"` |
| `test_ac_005_…` / `test_edge_009/010/016` | `AssertionError: generate mode must exit 0: 2/2: "…No such file or directory"` (`_generate_fixed_point`) |
| `test_ac_019_…` | `AssertionError: AC-019: generate runs exit 2/2` |
| `test_inv_001/004/005/006` | `Failed: …scripts\make_map.py does not exist — T-002 Phase 4 has not implemented the generator` |

Test-data validity: every fixture is a real `git init` + `git add -A` tree built from `_TREE_FILES`
(in-domain, valid sources); all reads are `encoding="utf-8"` explicit (P-67); no `ValidationError` /
`ValueError` / `AttributeError` appears anywhere in the RED output.

### Test sensitivity (P-68)

`stub_t005.py` (in `%LOCALAPPDATA%/Temp/sens_t005/`, outside the repository, extends the T-004 stub
with `--check`, the exit-code precedence, REQ-006 hard failures and the LF/hook-clean output, and
nothing else). `driver_t005.py` imports both test modules, rebinds `_GENERATOR`, and calls all 10
nodes; it fails loudly when a mutation's anchor is not unique, is a no-op, or does not compile.

- **Correct stub: 10/10 nodes pass** — the RED is missing behavior, not an unsatisfiable test.
  Building the stub caught **three real defects in the derived tests** before they were trusted:
  (1) the generator's own `--out` file is part of the file set once it exists (REQ-003), so a map
  generated before its own file existed is *already* stale — fixed by `_generate_fixed_point`
  (generate twice, then compare); (2) AC-019's two outputs must live **outside** the tree, or the
  second run's tree contains the first run's output; (3) the pinned messages contain an **em dash**,
  and a Windows child process writes cp1252 to a pipe, so the harness's UTF-8 decode raised
  (`proc.stdout is None`) — the stub now reconfigures stdout to UTF-8, and the requirement is part
  of the Phase-4 contract below. Without the all-pass run all three would have shipped as RED.
- **Wrong-implementation matrix: 16/16 mutations caught**, each by the semantically right node:

| Mutation (one broken clause) | Caught by |
|---|---|
| `--check` writes the `--out` file | INV-005 (+AC-004/005, EDGE-009/010/016, INV-004) |
| `--check` compares whitespace-insensitively | AC-005, INV-004 |
| missing `--out` exits 1 instead of 3 | AC-004, AC-005, INV-005 |
| stale `--check` prints a second line | AC-005, EDGE-009, EDGE-010 |
| no `\r\n` → `\n` normalisation | AC-005, EDGE-016, INV-004 |
| render carries trailing whitespace | AC-019, INV-006 |
| render ends with two newlines | AC-019, INV-006 |
| Packages order is a set (non-deterministic) | INV-001, AC-019 (+8 collateral) |
| tree order is a set (non-deterministic) | INV-001, AC-019 (+8 collateral) |
| unparseable source is not a hard failure | AC-004 |
| staleness outranks an unparseable source | AC-004 (+AC-005, EDGE-009/010) |
| generate mode exits 1 on a stale map | AC-004 (+AC-005, EDGE-009/010/016) |
| generate mode exits 3 on a missing `--out` | AC-004 (all 10) |
| `--max-depth 0` is not a usage error | AC-004 |
| a stale map is reported as fresh (exit 0) | AC-004, AC-005, EDGE-009/010/016, INV-004 |
| message names the resolved path, not `--out` as given | AC-005, EDGE-009, EDGE-010 |

### Quality gates (this step's changed paths only, P-6)

```text
uv run ruff check  tests/acceptance/test_structure_map.py tests/property/test_structure_map.py  -> All checks passed!
uv run ruff format tests/acceptance/test_structure_map.py tests/property/test_structure_map.py  -> 2 files already formatted
uv run pytest --collect-only tests/acceptance/test_structure_map.py tests/property/test_structure_map.py -> 29 collected, no errors
```

One lint finding was fixed in-step (PLR2004 on the bare `3` in INV-005 → `_EXIT_MISSING`). No
repo-wide sweep (Phase 5).

### Decisions and deviations

- **`_hook_clean` is duplicated** in the acceptance and property files instead of shared: T-005's
  `allowed_files` lists only the two test files, so no `*_test_helpers` module may be created. Both
  copies are the two hooks' byte-level transforms; `_active_hook_ids()` anchors the pair to
  `.pre-commit-config.yaml` (read-only — T-006 owns that file).
- **The hooks are not executed.** Running `pre-commit` would rewrite files and needs the hook envs;
  AC-019/INV-006 assert the transforms' effect on the generated bytes, which is what the hooks do.
- **EDGE-009's "fresh clone"** is a second `git init` tree holding the tracked files plus the
  committed map, not a `git clone` (a clone needs a commit and a committer identity; the staleness
  clause is identical either way).
- **`_snapshot` excludes `.git/`** — INV-005 protects the working tree, and a git command may
  legitimately rewrite its own index without touching a tracked file.
- **Deliberate under-assertions** (each owned elsewhere, so this task does not duplicate it): the
  REQ-006 stderr path lines and their sorted order → AC-006 (T-002); the pinned `--help` text →
  AC-002 (T-002); the absence of a trailing newline after the one-line message is *not* asserted
  (the spec pins the line, not `print`'s terminator); `--check`'s silence on a fresh map is asserted
  in AC-005/EDGE-016, not in INV-004 (INV-004 is about the exit code).
- `uv.lock` was restored before the commit (F-9 / P-74).

### What Phase 4 (T-005) must implement for these nodes

1. `--check`: read the `--out` bytes, normalise `\r\n` → `\n` **only**, compare byte-for-byte with a
   fresh render; no other normalisation, no whitespace-insensitive or section-level diffing (INV-004).
2. Exactly one stdout line, and it must be **UTF-8**: on this host a child process writes cp1252 to a
   pipe, so the em dash in the pinned message is undecodable for the UTF-8 harness (`proc.stdout`
   becomes `None`). Reconfigure stdout (`sys.stdout.reconfigure(encoding="utf-8")`) or write bytes to
   `sys.stdout.buffer`. This is a hard requirement of AC-005/EDGE-009/EDGE-010, not a test artifact.
3. Message text pinned byte-for-byte, with `<out>` **exactly as given on the command line** — never
   resolved, absolutised or normalised: `<out> is out of date — run uv run python scripts/make_map.py`
   and `<out> is missing — run uv run python scripts/make_map.py`. Nothing else on stdout, stderr empty.
4. Exit-code precedence `2 → 4 → 3 → 1 → 0`: an unparseable source outranks a missing `--out` and
   staleness (both → 4); `1` and `3` never occur in generate mode (a stale map is rewritten, a missing
   one is created, exit 0); `--max-depth < 1` and unknown options → 2.
5. `--check` writes nothing at all: it must not create a missing `--out`, must not touch any other
   path, and must leave every working-tree file byte-identical (INV-005).
6. Determinism (INV-001, REQ-019): the render is a pure function of the file set — every collection
   iterated in sorted `--root`-relative POSIX path order, never a `set` (set iteration order varies
   across processes and breaks byte identity between two runs); creation order must not matter.
7. Hook-clean output (INV-006, AC-019): LF only, no trailing whitespace on any line, exactly one
   final newline, UTF-8.
8. **Do not exclude `--out` from the file set.** The map file is itself listed once it exists
   (REQ-003 has no exclusion, and AC-021 only holds because the committed `STRUCTURE.md` appears in
   its own re-render). The tests therefore generate twice to reach that fixed point.
9. No `.gitattributes` is added (spec §13) and `.pre-commit-config.yaml` is not modified (T-006).

### Hand-off note for T-006 (skill, hook, AGENTS.md)

- AC-019/INV-006 already prove the generated output passes the two active hooks, so T-006 needs no
  hook change for the map; it only adds the `structure-map-check` local hook (AC-023).
- `_active_hook_ids()` reads `.pre-commit-config.yaml` read-only; when T-006 adds the
  `structure-map-check` hook that set grows and AC-019's subset assertion still holds — do not
  tighten it to an equality.
- The pinned message strings live once in `_stale_message`/`_missing_message` plus `_RUN_COMMAND`;
  AC-021 (T-007, the committed `STRUCTURE.md`) reuses the same `--check` path and must not restate
  them.

## Phase 3 — S3.1 test derivation, T-006 (2026-10-09)

**Task:** T-006 — the integration surface: the `code-structure-map` skill, the `structure-map-check`
local pre-commit hook (check-only, no CI job), the four `AGENTS.md` edits, the single advisory
sentence in `specify/SKILL.md` P.1, and the freshness policy documented twice.
**Requirements:** REQ-022, REQ-023, REQ-024, REQ-026, REQ-027 · **AC:** AC-022, AC-023, AC-024, AC-026, AC-027.
**File:** `tests/acceptance/test_structure_map.py` (the only test file in `allowed_files.test_files`).

### Node → ID map

| Node | AC / REQ | Witness |
|---|---|---|
| `test_ac_022_skill_exists_with_four_rules` | AC-022 / REQ-022 | `.agents/skills/code-structure-map/SKILL.md` exists, opens with `name` + `description` frontmatter, body under 60 non-blank lines, states all four rules, names the generate command, says the map is never hand-merged |
| `test_ac_023_hook_is_check_only_and_no_ci_job` | AC-023 / REQ-023 | the `structure-map-check` hook sits inside the existing `repo: local` block with the five pinned fields; its `entry` is `uv run python scripts/make_map.py --check`, carries no `--out`, is not the bare generate command; no file under `.github/workflows/` mentions `make_map` |
| `test_ac_024_agents_md_layout_matches_the_map` | AC-024 / REQ-024 | the Project Structure fenced block shows no `model/`/`services/`/`src/frontend/` (literal **and** tree-reconstructed), every directory path it shows is named by the generated map, the Tooling section names both commands, both `(ambient)` rows exist, no `tests/architecture` citation in `AGENTS.md` or `.agents/` |
| `test_ac_026_map_hook_is_advisory` | AC-026 / REQ-026 | every `AGENTS.md` line naming the map sits in one of the three REQ-024 sections and carries no machinery vocabulary (`◆`, `blockedBy`, `BLOCKED-`, `Status:`, `VERIFIED`, `prohibition`, `prerequisite`, `fast-path`, `--skip-spec`); no other phase skill mentions the map; `specify/SKILL.md` P.1 carries exactly one advisory sentence, and that sentence advises *reading*, not gating |
| `test_ac_027_freshness_policy_documented_twice` | AC-027 / REQ-027 | the skill **and** the `AGENTS.md` Tooling pointer both state the same-commit rule and the take-either-side conflict rule, and both say never hand-merge |

New helpers (all reuse the T-002…T-005 harness — `_run`, `_map_text`, `_generate`, `_tree_entries`,
`_ENTRY_PATH`, `_PRE_COMMIT`, `_active_hook_ids`, `_RUN_COMMAND`): `_text_of` (explicit
`encoding="utf-8"`, P-67), `_md_section`, `_fenced_block`, `_block_dir_paths`, `_map_dir_paths`,
`_paths_missing_from_map`, `_hook_block`; constants `_CHECK_COMMAND`, `_SKILL_BODY_MAX_LINES`,
`_MAP_MENTION`, `_COUNT_LINE`, `_SAME_COMMIT_RULE`, `_CONFLICT_RULE`, `_HAND_MERGE_RULE`,
`_FRESHNESS_RULES`, `_MACHINERY`, `_ALLOWED_MAP_SECTIONS`.

### RED gate

`red_command` run verbatim (targeted, never the full suite):

```text
5 failed in 0.71s
FAILED test_ac_023_hook_is_check_only_and_no_ci_job
FAILED test_ac_022_skill_exists_with_four_rules
FAILED test_ac_027_freshness_policy_documented_twice
FAILED test_ac_026_map_hook_is_advisory
FAILED test_ac_024_agents_md_layout_matches_the_map
```

Failure mode per node — every one is an `AssertionError` or a `pytest.fail`, no collection, import or
fixture error (`uv run pytest --collect-only tests/acceptance/test_structure_map.py` → 28 collected,
0 errors, before and after):

| Node | Observed RED failure |
|---|---|
| AC-022 | `Failed: .agents\skills\code-structure-map\SKILL.md does not exist` |
| AC-023 | `Failed: .pre-commit-config.yaml declares no hook with id 'structure-map-check'` |
| AC-024 | `AssertionError: REQ-024: the layout block still shows ['model/', 'services/']` (the tree-reconstructed clause would also flag `src/frontend/`, `src/frontend/shared/`) |
| AC-026 | `AssertionError: REQ-026: P.1 must carry exactly one advisory sentence about the map, got []` |
| AC-027 | `Failed: .agents\skills\code-structure-map\SKILL.md does not exist` |

Test-data validity: no fixture builds a model instance; every fixture is an in-domain text artifact —
the real `AGENTS.md`, `.pre-commit-config.yaml`, `.github/workflows/` (3 files), `.agents/skills/`
(9 `SKILL.md`), and a `tmp_path/STRUCTURE.md` written outside the repository, so no repo file is
written by these tests. All file reads are `encoding="utf-8"` (P-67). `_REPO_ROOT` is derived from
`Path(__file__).resolve().parents[2]`, so the witnesses resolve the worktree they live in.

### Anti-vacuity (P-68 lesson, adapted — no stub pass over markdown/config witnesses)

Checked by probing the helpers against plausible right and plausible wrong inputs
(`_block_dir_paths`, `_paths_missing_from_map`, `_hook_block`, `_md_section`, `_map_dir_paths`):

| Node | Wrong-but-plausible implementation | Assertion that catches it |
|---|---|---|
| AC-022 | a skill file that exists with frontmatter but states three of the four rules (the conflict rule missing) | `missing = [rule … ]; assert not missing` names the missing rule; `_HAND_MERGE_RULE` separately requires the never-hand-merge clause; `len(body_lines) < 60` catches a skill that dumps the whole policy in a 200-line body |
| AC-023 | a hook added with `entry: uv run python scripts/make_map.py` (generate mode — it would rewrite the map on every commit), or `stages: [pre-push]` like `mkdocs-build`, or a CI job running `--check` | the pinned `fields` dict requires `entry: … --check` and `stages: [pre-commit]` verbatim; `assert "--check" in entry` and `assert "--out" not in entry and entry != _RUN_COMMAND`; the workflow scan asserts the glob is non-empty **and** that no workflow mentions `make_map` |
| AC-024 | a rewritten block that keeps `model/`/`services/`, or lists `src/frontend/`, or names a directory the map does not show, or a Tooling section that names only the generate command | the literal `shown` clause plus the tree-reconstructed `stale` clause (`{"model", "services", "frontend"}` segments); `_paths_missing_from_map` lists every block path the map does not name; `assert _RUN_COMMAND in tooling` / `assert "--check" in tooling`; `assert rows` + `all("(ambient)" …)` per skill row |
| AC-026 | the map wired into a gate — e.g. a Phase Matrix / Atomic Steps / Handoff Output / Agent Prohibitions line mentioning `STRUCTURE.md`, a `◆` gate row, or a second map sentence in P.1 phrased as a requirement | the section whitelist (`Tooling & Execution Environment`, `Skill-to-Phase Mapping`, `Project Structure`) plus `_MACHINERY` on the same line; the per-skill `hits` assertion; `len(advisory) == 1` plus `not _MACHINERY.search(advisory[0])` |
| AC-027 | the policy documented only in the skill (the `AGENTS.md` pointer line names the commands but not the rules), or the conflict rule phrased without "either side" | the per-target loop over `(("the skill", skill), ("the AGENTS.md Tooling section", tooling))` requires `_SAME_COMMIT_RULE` and `_CONFLICT_RULE` in **both**, plus `_HAND_MERGE_RULE` in both |

Non-empty guards (added so an empty collection can never satisfy a witness): `_active_hook_ids()`
non-empty; the `.github/workflows/` glob non-empty; the Project Structure section slice, its fenced
block and the extracted path set non-empty; the Tooling and Skill-to-Phase section slices non-empty;
`_map_dir_paths` asserts both the full-entry set and the count-line set are non-empty; the skill set
under `.agents/skills/` non-empty; the P.1 section slice non-empty; the Tooling pointer-line list
non-empty; the skill body non-empty.

### Deliberate under-assertions (and who covers them)

- **REQ-009 count lines.** `.agents/skills/` and `userdocs/` can never be tree entries — REQ-009
  renders every non-code top-level directory as one count line. `_paths_missing_from_map` therefore
  accepts a path whose top-level directory the map renders as a count line, and demands a full tree
  entry everywhere else (which is what keeps `src/frontend/` a failure, since `src/` is rendered in
  full). Probed: a corrected block yields `missing: []`, adding `src/frontend/` yields
  `['src/frontend/']`.
- **"exactly four rules" (REQ-022) is not counted.** The four required rules are each asserted; a fifth
  rule is not detected. AC-026 covers the only fifth rule that would matter (a gate/prohibition).
- **AC-027 checks the Tooling section, not one line.** The two rules need not sit on the same line as
  the command; they must sit in the section that carries the pointer line (`pointer` list asserted
  non-empty). Phase 6 review reads the wording.
- **AC-026 is section- and vocabulary-based, not an exhaustive reading of the workflow.** A gate that
  depends on the map without naming it on the same line is out of reach; AC-024's `(ambient)` row
  assertion and the Phase 6 review of the four-place edit bound it.
- **AC-023 does not run pre-commit.** The hook's *effect* (a stale map blocks a commit) is AC-021
  (T-007, the committed `STRUCTURE.md`) plus the local hook itself; running pre-commit here would be a
  full-tool run, not a witness.
- **AC-024's map is generated into `tmp_path`**, never into the repository root — the committed
  `STRUCTURE.md` is T-007's artifact (AC-021).

### Phase 4 contract for T-006

Phase 4 must create/edit exactly these files; nothing else may change:

1. `.agents/skills/code-structure-map/SKILL.md` (new) — `---` frontmatter with `name:` and
   `description:`; body under 60 non-blank lines; the text must contain, somewhere in the file: a
   sentence matching `STRUCTURE.md … before … tree` (same line), the word `stale`, the phrase
   `same commit`, the phrase `either side`, a `hand-merge`/`hand merge` negation, and the literal
   command `uv run python scripts/make_map.py` (AC-022, AC-027).
2. `.pre-commit-config.yaml` — one hook inside the existing `- repo: local` block, no other `- repo:`
   between it and `- repo: local`, with the lines `entry: uv run python scripts/make_map.py --check`,
   `language: system`, `pass_filenames: false`, `stages: [pre-commit]`, `files: \.py$` exactly as
   REQ-023 pins them (AC-023). No `--out` in the entry.
3. `AGENTS.md` — four places only: (a) the Project Structure section: the fenced block must contain no
   `model/`, `services/` or `frontend` path segment, and every directory path it shows (tree-drawn
   nesting is rebuilt from the `──` marker column; `<placeholder>` segments cut the path) must be
   named by the map — code-dir paths as full tree entries, non-code top-level dirs via their count
   line; (b) the Tooling section must contain the literal `uv run python scripts/make_map.py`, the
   literal `--check`, a line naming the map/skill, `same commit`, `either side` and a hand-merge
   negation; (c) the Tooling type-check line gains `uv run mypy scripts/`; (d) the Skill-to-Phase
   Mapping table gains rows for `code-structure-map` and `python-best-practices`, each containing
   `(ambient)` (AC-024, AC-027).
4. `.agents/skills/specify/SKILL.md` — exactly one line inside `### P.1 Frame (orchestrator)` that
   mentions the map, contains the word `read`, and contains none of the `_MACHINERY` markers (AC-026).
5. No `.github/workflows/` file may ever mention `make_map` (read-only witness scope; AC-023), and no
   file under `AGENTS.md`/`.agents/` may cite `tests/architecture` (AC-024).

Interlock (gate_interlock 2): the hook fires on `\.py$` while `STRUCTURE.md` does not yet exist, so
after the hook is added this task must commit no `.py` file without regenerating the map in the same
commit — T-007 lands the committed map.

### Ruff gate

`uv run ruff check tests/acceptance/test_structure_map.py` → `All checks passed!`;
`uv run ruff format tests/acceptance/test_structure_map.py` → clean (changed path only, no repo-wide
sweep, P-6).

## Phase 3 — S3.1 test derivation, T-007 (2026-10-09)

Task: *the committed artifact — `STRUCTURE.md`* (REQ-021 · AC-021 · NFR-002 · NFR-005). Derived into
`tests/acceptance/test_structure_map.py` (appended after the T-006 section, lines 1320–1402). No
other file was written: `STRUCTURE.md` and `scripts/make_map.py` are Phase 4 artifacts.

### Node → ID map

| Node | Witnesses | What it asserts |
|---|---|---|
| `test_ac_021_committed_map_matches_fresh_render` | AC-021 / REQ-021 | `STRUCTURE.md` exists at the repo root; a render of the current tree into `tmp_path` is non-empty and **byte-identical** to the committed file; `--check` against the committed file exits `0` |
| `test_nfr_002_map_line_budget` | NFR-002 | the committed map has at least one non-blank line and `len(lines) <= 2_000` |
| `test_nfr_005_complexipy_threshold_holds` | NFR-005 | the CI gate invocation `complexipy src tests --max-complexity-allowed 15` analyses ≥ 1 function and exits `0` |

Helpers reused, none re-invented: `_REPO_ROOT` (resolved from the test file's own path, so it works
from any worktree), `_run`, `_output`, `_generate`, `_check`, `_GENERATOR`. New T-007-only helpers:
`_complexipy(max_allowed)` (the venv console script next to `sys.executable` — `sys.executable -m
complexipy` is impossible, the package ships no `__main__`; the script is the binary `uv run
complexipy` resolves in `quality.yml:144`), `_complexipy_report` (ANSI-stripped `(analysed, over)`
split), `_map_line_difference` (first differing line / line-count difference as the failure message).
All file reads are `encoding="utf-8"` and both subprocess runs pass `encoding="utf-8"` (P-67, and the
T-005 em-dash finding).

### RED gate (red_command, verbatim)

`uv run pytest tests/acceptance/test_structure_map.py::test_ac_021_committed_map_matches_fresh_render
tests/acceptance/test_structure_map.py::test_nfr_002_map_line_budget
tests/acceptance/test_structure_map.py::test_nfr_005_complexipy_threshold_holds -v`

→ `3 failed in 0.85s`, every failure an `AssertionError` (no collection error —
`uv run pytest --collect-only tests/acceptance/test_structure_map.py` → `31 tests collected`).

- `test_ac_021_…` — `AssertionError: REQ-021: no STRUCTURE.md is committed at the repository root`.
- `test_nfr_002_…` — same missing-file assertion.
- `test_nfr_005_…` — `AssertionError: NFR-005: complexipy exits 1 at max-complexity-allowed 15: 6 of
  1980 analysed functions are over the limit: test_ac_026_map_hook_is_advisory 17, _block_dir_paths
  21, test_ac_012_package_header_and_exports 26, test_ac_009_tree_code_dirs_full_other_dirs_counted
  34, test_inv_002_no_module_hidden_by_pruning 22, test_ac_016_private_symbols_and_dunders 25`.

**NFR-005 is RED, but not for the expected reason.** The prompt expected it might be GREEN (the gate
passes on `main` — re-measured here: `complexipy src tests --max-complexity-allowed 15` on the
primary worktree exits `0` with `0` FAILED lines, 2026-10-09). It is RED because **this change's own
Phase 3 derivations broke the gate**: all six over-limit functions live in `tests/acceptance/
test_structure_map.py`, `tests/property/test_structure_map.py` and `tests/unit/test_make_map.py` —
the three files T-007 lists as read-only *unless NFR-005 fails*. It fails, so DAG step 5 applies:
Phase 4 (T-007) splits those six functions inside this task; `max-complexity-allowed` and
`[tool.complexipy] paths` stay untouched (P-56). The witness is non-vacuous by construction: the
`_complexipy("0")` tripwire asserts the same invocation exits non-zero at a limit of 0, and
`analysed` (1 980 functions) is asserted non-empty before the exit code.

### Anti-vacuity (P-68, adapted)

| Node | Wrong-but-plausible implementation | Assertion that catches it |
|---|---|---|
| AC-021 | `STRUCTURE.md` hand-edited / stale by one line | `committed == fresh` byte compare, message pinpoints the line (`_map_line_difference`); verified against synthetic inputs: an edit → `line 2 differs: committed 'b' / fresh 'X'`, a truncation → `line count differs: committed 3 lines, fresh 2 lines`, and `--check` exit `0` catches it independently |
| AC-021 | generator emits an empty/stub map that matches an equally empty committed file | `assert fresh, …` before the compare (an empty render can never match a real committed map, and an empty render is refused outright) |
| NFR-002 | an empty `STRUCTURE.md` trivially satisfies `0 ≤ 2 000` | `assert any(line.strip() for line in lines)` |
| NFR-002 | a map truncated to a few lines | not NFR-002's contract (an upper bound); AC-021's byte comparison is the witness that catches truncation — recorded as a deliberate split, not a gap |
| NFR-005 | the exit code is ignored / complexipy never runs | `assert code == 0` on the real run, `assert analysed` (1 980 analysed functions) before it, and the `_complexipy("0")` tripwire `assert tripwire_code != 0` |
| NFR-005 | threshold or paths read from the wrong place | `_COMPLEXIPY_MAX = "15"` and `_COMPLEXIPY_PATHS = ("src", "tests")` are the literals of `quality.yml:144` and `[tool.complexipy]` (pyproject.toml:97-99), passed as the CI command passes them |

### Deliberate under-assertions

- NFR-002 asserts only the normative ceiling (≤ 2 000) plus non-emptiness; the spec's ≈1 875
  projection is a projection, not a requirement — the actual line count is recorded by Phase 4.
- AC-021 does not re-assert the map's document shape or section content — AC-008/AC-009…AC-016
  (T-002/T-003/T-004) own those; AC-021 witnesses *freshness of the committed artifact* only.
- NFR-005 does not assert `[tool.complexipy]` config equality, only the CI invocation's exit code —
  the config is the gate's own input, and `scripts/` staying out of scope is NFR-005's own text.

### Phase 4 contract for T-007

1. Commit every other file of the change first (clean `git status`), then run
   `uv run python scripts/make_map.py` at the repository root with defaults → `./STRUCTURE.md` for
   the post-change tree; commit it as its own commit, never hand-edited (EDGE-010).
2. AC-021 renders the tree into `tmp_path` and compares bytes against the committed file, so the
   committed bytes must be the **fixed point** render (REQ-003: the map's own `STRUCTURE.md` entry is
   in the file set) and the working tree must carry **no stray untracked file** in a mapped directory
   when the test runs (REQ-003 includes untracked files) — clean up scratch files before verifying.
3. `--check` is invoked with an **absolute** `--out` (`_check(_REPO_ROOT, str(_MAP_FILE))`); the hook
   uses the default relative path — both must exit `0`.
4. NFR-002: record the actual line count (spec projection ≈1 875, margin ≈125). Do not raise the
   ceiling and do not narrow Packages scope.
5. NFR-005: split the six over-limit functions named above (three files, all in this change) until
   `complexipy src tests --max-complexity-allowed 15` exits `0`; never touch `max-complexity-allowed`
   or `[tool.complexipy] paths` (P-56). Re-derive nothing: splitting must keep every existing node
   name and assertion intact.
6. Re-check after landing: the map is hook-clean (INV-006, proven in T-005), no `.gitattributes` was
   added, and the AC-024 cross-check (every directory path of the corrected `AGENTS.md` Project
   Structure block appears in the committed map's tree) now runs against the real artifact.

### Ruff gate

`uv run ruff check tests/acceptance/test_structure_map.py` → `All checks passed!`;
`uv run ruff format tests/acceptance/test_structure_map.py` → `1 file left unchanged` (changed path
only, no repo-wide sweep, P-6).

## Phase 3 — S3.2 gate (RED + ruff) (2026-10-09)

**Objective:** ruff clean on the three derived test paths, RED confirmed for all 7 DAG tasks, no
collection error, nothing previously GREEN broken. No implementation, no traceability update
(S5.3), no `tasks.json` status change (S4.4).

### Ruff gate (Phase 3 scope = the derived test paths)

```text
uv run ruff check tests/acceptance/test_structure_map.py tests/unit/test_make_map.py tests/property/test_structure_map.py
  -> All checks passed!                (exit 0)
uv run ruff format --check tests/acceptance/test_structure_map.py tests/unit/test_make_map.py tests/property/test_structure_map.py
  -> 3 files already formatted         (exit 0)
```

No violation to fix, so no in-step fix-and-recheck was needed. No repo-wide `ruff check .` /
`ruff format .` was run — that is the Phase 5 sweep (P-6).

### Collection check (a collection error is not a RED)

`uv run pytest --collect-only -q <the three files>` → **55 tests collected in 0.17s**, zero
collection or import errors. 55 = the union of the 7 tasks' `tests_to_create` (2 + 15 + 13 + 7 +
10 + 5 + 3), so every derived node is collected.

### Per-task RED (each `red_command` from `.github/task-runner/tasks.json` run verbatim)

| Task | Nodes | Result | RED reason (observed failure mode) |
|---|---|---|---|
| T-001 | 2 | **2 failed** / 0 passed, exit 1 | `clause 1: the type-check job of quality.yml does not run 'uv run mypy scripts/'` (AC-025); `mypy scripts/: exit 1: scripts\verify_spec.py:74: error: Item "TextIO" of "TextIO \| Any" has no attribute "reconfigure" [union-attr]` (NFR-004) |
| T-002 | 15 | **14 failed** / 1 passed, exit 1 | `scripts\make_map.py does not exist — T-002 Phase 4 has not implemented the generator`; CLI runs exit 2; `no map file at <tmp>/…` for AC-002/003/008, EDGE-007/008; `generate run exits 2`; `--max-depth 0: no argparse usage error on stderr` |
| T-003 | 13 | **13 failed** / 0 passed, exit 1 | generator missing (`scripts\make_map.py does not exist`), `no map file at <tmp>/…` for AC-009/010/011/012, EDGE-015 |
| T-004 | 7 | **7 failed** / 0 passed, exit 1 | generator missing — every node fails on the same `scripts\make_map.py does not exist` fixture guard |
| T-005 | 10 | **10 failed** / 0 passed, exit 1 | generator missing; `generate mode must exit 0: 2/2`, `AC-019: generate runs exit 2/2`, `EDGE-009 fixture: generate exits 2` |
| T-006 | 5 | **5 failed** / 0 passed, exit 1 | `.agents\skills\code-structure-map\SKILL.md does not exist` (AC-022/027); `.pre-commit-config.yaml declares no hook with id 'structure-map-check'` (AC-023/026); `REQ-024: the layout block still shows ['model/', 'services/']`; `REQ-026: P.1 must carry exactly one advisory sentence about the map, got []` |
| T-007 | 3 | **3 failed** / 0 passed, exit 1 | `REQ-021: no STRUCTURE.md is committed at the repository root` (AC-021, NFR-002); NFR-005 complexipy exit 1 — see the classification below |

Every task shows at least one node failing **on behavior** (missing generator / missing
`STRUCTURE.md` / missing skill + hook + `AGENTS.md` guidance / missing CI type-check of `scripts/` /
over-complexity), **no node failed on a collection or import error, and no test-data
`ValidationError`/`ValueError` appears** — the test-contract sanity check holds.

### Whole-set result

```text
uv run pytest tests/acceptance/test_structure_map.py tests/unit/test_make_map.py tests/property/test_structure_map.py -q
  -> 54 failed, 1 passed in 5.99s
```

Failure-mode distribution over the 54 (from `--tb=line`, deduplicated): 25 × `scripts\make_map.py
does not exist — T-002 Phase 4 has not implemented the generator`, 18 × `No such file or directory`
(the generator invoked as a subprocess), 5 × `no map file at <tmp>/…`, 2 × skill file missing, 2 ×
no committed `STRUCTURE.md`, 1 × no `structure-map-check` hook id, 1 × `mypy scripts/` exit 1,
1 × quality.yml clause 1, 1 × REQ-024 layout block, 1 × REQ-026 P.1 sentence, 1 × AC-019 exit 2,
1 × NFR-005 complexity.

### Unchanged-GREEN check

The single GREEN node in the set is **`test_nfr_003_deptry_clean`** (verified alone: `1 passed in
1.02s`). It is expected GREEN: it asserts the repo's dependency hygiene, which this change does not
touch, and it was GREEN before Phase 3. No other node in the set was GREEN before, so nothing that
was GREEN has been broken; the three new files collect cleanly, so they introduce no
collection-time side effects on the rest of the suite (full-suite regression is the Phase 5 gate).

### NFR-005 RED classification (assigned to T-007 Phase 4)

`test_nfr_005_complexipy_threshold_holds` is RED for a **different** reason than the other 54 nodes:
not a missing artifact, but a real, in-scope violation introduced by **this change's own test code**.

- Observed: `NFR-005: complexipy exits 1 at max-complexity-allowed 15: 6 of 1980 analysed functions
  are over the limit`.
- The tripwire assertion (`--max-complexity-allowed 0` must exit non-zero) passes, so the run is not
  vacuous, and 1 980 functions were analysed, so the scan is not empty.
- **Not a pre-existing repo failure — freshly measured on `main`** in the primary worktree
  (`git rev-parse --abbrev-ref HEAD` → `main`):
  `uv run complexipy src tests --max-complexity-allowed 15` → `All functions are within the allowed
  complexity.`, **exit 0**, 0 functions over the limit. The six offenders exist only in this branch's
  three new test files.
- **T-007 Phase-4 work list** (functions to restructure, with their measured branch complexity):

  | Function | File | Complexity |
  |---|---|---|
  | `test_ac_009_tree_code_dirs_full_other_dirs_counted` | `tests/acceptance/test_structure_map.py` | 34 |
  | `test_ac_012_package_header_and_exports` | `tests/acceptance/test_structure_map.py` | 26 |
  | `test_ac_016_private_symbols_and_dunders` | `tests/unit/test_make_map.py` | 25 |
  | `_block_dir_paths` | `tests/unit/test_make_map.py` | 21 |
  | `test_ac_026_map_hook_is_advisory` | `tests/acceptance/test_structure_map.py` | 17 |
  | `test_inv_002_no_module_hidden_by_pruning` | `tests/property/test_structure_map.py` | 22 |

  T-007's `allowed_files` already list the three test files as writable (the unit/property entries
  are marked `READ-ONLY unless NFR-005 fails: complexipy scans src and tests, so a function over 15
  is fixed here — listed per P-55`), so this is authorized Phase-4 work, not a Phase-3 re-derivation.
- **MUST NOT** be resolved by relaxing the gate: `max-complexity-allowed` and `[tool.complexipy]
  paths` stay exactly as the spec and CI define them (P-56). Splitting must keep every existing node
  name and assertion intact (no test weakening, no deletion).

### Phase 3 gate result

**Phase 3's gate PASSES: RED is observed for all 7 tasks (7/7), with 55 nodes collected and zero
collection errors, ruff clean on the derived paths, and the only previously-GREEN node
(`test_nfr_003_deptry_clean`) still GREEN.** The state machine is at `RED_CONFIRMED` for the whole
Phase 3 test set; **Phase 4 (IMPLEMENT) may start**, beginning with S4.1 (T-001).

`tasks.json` statuses are left `PENDING` (status sync belongs to S4.4); the traceability matrix is
not touched (S5.3).

---

## Phase 4 — S4.1 (T-001) RED re-confirmation (2026-10-09)

**Picked task: T-001** — `tooling - scripts/ joins the type gate (ADR-086)`; REQ-025 / AC-025 /
NFR-004; `dependencies: []`, `status: PENDING`. All 7 DAG tasks are ready after the Phase 3 gate
(`d945952`), so the AGENTS.md "easiest first" ordering decides. T-001 is the easiest: two edits —
one added step in `.github/workflows/quality.yml`'s `type-check` job, one mypy narrowing at
`scripts/verify_spec.py:74` — with no new module and no new pattern. It also establishes the widened
type gate (NFR-004 runs `mypy scripts/` repo-wide) that the later tasks' GREEN runs depend on: any
later task that adds code under `scripts/` is type-checked only once this gate exists. No
implementation was done in this step.

### RED evidence (red_command run verbatim, re-measured — not carried over from S3.2)

```text
uv run pytest tests/acceptance/test_structure_map.py::test_ac_025_mypy_covers_scripts tests/acceptance/test_structure_map.py::test_nfr_004_mypy_and_ruff_clean -v

tests\acceptance\test_structure_map.py::test_ac_025_mypy_covers_scripts FAILED
tests\acceptance\test_structure_map.py::test_nfr_004_mypy_and_ruff_clean FAILED
============================== 2 failed in 1.49s ==============================
```

`test_ac_025_mypy_covers_scripts` (test_structure_map.py:99, assertion at :119) — two of its three
clauses fail:

```text
AssertionError: clause 1: the type-check job of quality.yml does not run 'uv run mypy scripts/'
  clause 2: mypy over scripts/ exits 1: scripts\verify_spec.py:74: error: Item "TextIO" of "TextIO | Any" has no attribute "reconfigure"  [union-attr]
  Found 1 error in 1 file (checked 3 source files)
```

`test_nfr_004_mypy_and_ruff_clean` (test_structure_map.py:122, assertion at :131) — one of its four
gates fails:

```text
AssertionError: mypy scripts/: exit 1: scripts\verify_spec.py:74: error: Item "TextIO" of "TextIO | Any" has no attribute "reconfigure"  [union-attr]
  Found 1 error in 1 file (checked 3 source files)
```

**Both nodes fail on behavior, not on a fixture, import or collection error** — the module imports
cleanly, both test bodies run to their `assert`, and the failure text is the concrete missing
behavior. Two distinct causes, both re-measured directly rather than trusted from S3.2:

**Cause 1 — the workflow has no `mypy scripts/` step.** `type-check` job step list at this head
(`.github/workflows/quality.yml:10-26`):

```text
10:  type-check:
12:    steps:
13:      - uses: actions/checkout@v7
14:      - name: Setup uv            (15: uses: astral-sh/setup-uv@v7)
16:      - name: Setup Python        (17-19: uses: actions/setup-python@v7, python-version '3.14')
20:      - name: Sync tooling        (21: run: uv sync --only-group dev)
22:      - name: Run mypy (gate)     (23: run: uv run mypy src/)
24:      - name: Run ty (informational) (25: run: uv run ty check src/, 26: continue-on-error: true)
```

The only mypy invocation is `uv run mypy src/` at line 23 — the string `uv run mypy scripts/` does
not occur in the job block, so clause 1 is false for the right reason.

**Cause 2 — `mypy scripts/` is not clean at this head** (run directly, verbatim):

```text
uv run mypy scripts/
scripts\verify_spec.py:74: error: Item "TextIO" of "TextIO | Any" has no attribute "reconfigure"  [union-attr]
Found 1 error in 1 file (checked 3 source files)
exit code: 1
```

Exactly **1 error in 1 file** (3 source files checked), at `scripts/verify_spec.py:74` — the
`sys.stdout.reconfigure(encoding="utf-8")` call inside
`with contextlib.suppress(AttributeError, ValueError, OSError):` (line 73-74). mypy types
`sys.stdout` as `TextIO | Any`, and `TextIO` has no `reconfigure`, so the attribute access is a
`union-attr` error. This matches the ADR-086 measured baseline and the S3.2 row exactly; no second
error appeared, so `allowed_files` needs no DAG correction.

### Non-vacuity of the two witnesses

- **AC-025 is threefold and each clause is independently checked** (test_structure_map.py:105-117):
  clause 1 greps the `type-check` job block extracted by `_workflow_job_block` (job-scoped, so a
  `mypy scripts/` step in a *different* job would not satisfy it); clause 2 runs
  `sys.executable -m mypy scripts/` and requires exit 0; clause 3 runs
  `uv run python scripts/verify_spec.py docs/specs/template.md` and requires exit 0 **and** stdout
  equal to `_VERIFY_SPEC_REPORT_BEFORE_FIX` (test_structure_map.py:34-47, the 11-line report
  measured before the fix). Clause 3 **already passes at this head** — measured directly:
  `uv run python scripts/verify_spec.py docs/specs/template.md` exits **0** with exactly the
  recorded 11-line report (`Specification validation` / rule / 7 `✓` lines / blank /
  `Traceability: PASS`). A witness that passes now and would fail if the fix changed the report is
  a live constraint, not a vacuous one.
- **NFR-004 runs four gates** (`_NFR_004_GATES`, test_structure_map.py:50-55): `mypy scripts/`,
  `mypy src/`, `ruff check .`, `ruff format --check .`, each as a subprocess from the repo root with
  exit-code checked. Only `mypy scripts/` was reported dirty, which simultaneously evidences that
  the other three gates are clean at this head — so the only offender NFR-004 names is the one file
  T-001 is allowed to edit.
- Neither test asserts a weaker post-condition than the spec: the workflow clause is a text search
  for the exact command, and the type/lint clauses are exit-code checks on the real tools.

### Phase 4 (S4.2, T-001) work list — targets and constraints

1. `.github/workflows/quality.yml` — add **one** step to the `type-check` job, immediately after the
   existing `Run mypy (gate)` step (`quality.yml:22-23` at this head):
   `run: uv run mypy scripts/`. No new job; the informational `ty` step (`quality.yml:24-26`,
   `continue-on-error: true`) untouched; **no step may mention `make_map.py`** (AC-023 — no CI job
   for the map in this change, ADR-085).
2. `scripts/verify_spec.py:74` — narrow the `union-attr` error so `uv run mypy scripts/` exits 0,
   **behaviour-preservingly**: the `reconfigure` call stays on the same object, guarded/asserted
   rather than assumed, still inside the `contextlib.suppress(AttributeError, ValueError, OSError)`
   at line 73. `verify_spec.py`'s **exit codes, report text, stdout format and argument handling
   must not change** — its only witness is
   `uv run python scripts/verify_spec.py docs/specs/template.md` exiting 0 with the unchanged
   11-line report (the script has no unit tests: spec §7 AC-025, ADR-086).
3. Nothing else: no `pyproject.toml` key, no coverage/`fail_under = 92`, no complexipy/bandit/`ty`
   scope change (ADR-086); no generator, map, skill, hook or `AGENTS.md` change (out of T-001's
   `implementation_scope`).
4. GREEN command: `uv run pytest tests/acceptance/test_structure_map.py::test_ac_025_mypy_covers_scripts tests/acceptance/test_structure_map.py::test_nfr_004_mypy_and_ruff_clean -v` → 2 passed.
   Ruff gate on the changed paths: `uv run ruff check .github/workflows/quality.yml scripts/verify_spec.py`.
   `uv.lock` is rewritten by the first `uv run` in this worktree (P-42) — restore it before the commit.

**S4.1 gate: PASSED — T-001 RED re-observed (2 failed, exit 1), both causes measured directly, both
witnesses non-vacuous.** No source, test, `tasks.json`, todo/question or traceability file was
modified by this step.

## Phase 4 — S4.2 (T-001) Implement + confirm GREEN (2026-10-09)

**Objective:** minimum change for T-001 — `scripts/` joins the mypy type gate (AC-025 clauses 1–2,
NFR-004) — no refactor (S4.3), no task-status flip (S4.4).

### Exact diff (2 files, +4 / −1)

`.github/workflows/quality.yml` — one step added to the `type-check` job, immediately after the
existing `uv run mypy src/` gate step (`quality.yml:22-23` at the S4.1 head):

```diff
       - name: Run mypy (gate)
         run: uv run mypy src/
+      - name: Run mypy scripts/ (gate)
+        run: uv run mypy scripts/
       - name: Run ty (informational)
```

No new job, no other job touched, the informational `ty` step untouched, and **no step mentions
`make_map.py`** (AC-023 / ADR-085). `pyproject.toml` untouched — no mypy/coverage/complexipy/bandit/ty
key changed, `fail_under = 92` unmoved (P-56: the gate is widened by the workflow step, not by config).

`scripts/verify_spec.py` — the single `union-attr` error at `:74`, narrowed inside the existing
`contextlib.suppress(AttributeError, ValueError, OSError)`:

```diff
     with contextlib.suppress(AttributeError, ValueError, OSError):
-        sys.stdout.reconfigure(encoding="utf-8")
+        if hasattr(sys.stdout, "reconfigure"):
+            sys.stdout.reconfigure(encoding="utf-8")
```

**Why the narrowing is behaviour-preserving.** The call stays on the same object (`sys.stdout`), now
*guarded* rather than assumed. Before the change, an object without `reconfigure` raised `AttributeError`,
which the enclosing `contextlib.suppress` swallowed; after the change the same case simply skips the call.
Both paths leave stdout untouched and continue to `spec_path = ...`, so no exit code, report text,
stdout format or argument handling can differ. Forms rejected as larger or behaviour-changing:
`isinstance(sys.stdout, io.TextIOBase)` — mypy then reports `"TextIOBase" has no attribute "reconfigure"`
(measured) and it would skip the call for a non-`TextIOBase` stream that does have it; `cast(...)` —
still an assumption, not a guard (the task requires guarded/asserted).

### GREEN gate (green_command, same node ids as red_command)

`uv run pytest tests/acceptance/test_structure_map.py::test_ac_025_mypy_covers_scripts tests/acceptance/test_structure_map.py::test_nfr_004_mypy_and_ruff_clean -v`

```text
tests/acceptance/test_structure_map.py::test_nfr_004_mypy_and_ruff_clean PASSED [ 50%]
tests/acceptance/test_structure_map.py::test_ac_025_mypy_covers_scripts PASSED [100%]
============================== 2 passed in 1.15s ==============================
EXIT:0
```

Re-run with `-p no:randomly` (order-independence): `2 passed in 1.21s`, EXIT 0 (both nodes PASSED).

### NFR-004 gates + ruff gate on the changed path

| Command | Result | Exit |
|---|---|---|
| `uv run mypy scripts/` | `Success: no issues found in 3 source files` | 0 |
| `uv run mypy src/` | `Success: no issues found in 84 source files` | 0 |
| `uv run ruff check scripts/verify_spec.py` | `All checks passed!` | 0 |
| `uv run ruff format scripts/verify_spec.py` | `1 file left unchanged` | 0 |

No repo-wide `ruff check .` / `ruff format .` was run in this step (Phase 5 sweep, P-6). NFR-004's
`ruff check .` and `ruff format --check .` clauses are covered by the passing `test_nfr_004_mypy_and_ruff_clean`
node, which runs all four gates as subprocesses.

### verify_spec.py witness (AC-025 clause 3) — output unchanged

`uv run python scripts/verify_spec.py docs/specs/template.md` → **exit 0**, 11-line report identical
to `_VERIFY_SPEC_REPORT_BEFORE_FIX` (the constant the AC-025 node compares against):

```text
Specification validation
─────────────────────────
✓ REQ-001 has acceptance criteria
✓ REQ-002 has acceptance criteria
✓ REQ-003 has acceptance criteria
✓ AC-001 has executable test
✓ AC-002 has executable test
✓ AC-003 has executable test
✓ INV-001 has property test

Traceability: PASS
WITNESS_EXIT:0
```

### No regression in the touched area

`uv run pytest tests/acceptance/test_structure_map.py -q` → **28 failed, 3 passed** (5.65s). The 3
passed are the two T-001 nodes plus `test_nfr_003_deptry_clean` (already GREEN at the base, per the
S4.1 record); the other 28 nodes stay RED — expected, they belong to T-002..T-007. No previously
passing node turned failing.

`uv run python scripts/check_traceability.py` → exit 0 (still passes; its PASS is not evidence of this
spec's rows — finding 2).

### Files changed (T-001, within `allowed_files`)

- `.github/workflows/quality.yml` (+2) — the `type-check` job only.
- `scripts/verify_spec.py` (+2 / −1) — the `:74` narrowing only.
- `uv.lock` restored before the commit (`git restore uv.lock`, F-9 / P-74); no test, spec, DAG,
  `pyproject.toml` or traceability file touched by this step.

**S4.2 gate: PASSED — T-001 GREEN (2 passed, also with `-p no:randomly`), `mypy scripts/` exit 0,
`mypy src/` exit 0, ruff clean on the changed path, the `verify_spec.py` witness unchanged.**

## Phase 4 — S4.3 (T-001) Refactor (keep GREEN) (2026-10-09)

**Objective:** improve structure of the T-001 diff (duplication, complexity, naming, boundaries)
without changing behaviour. **Outcome: no-op — zero file changes** (the no-op fast-path, verified,
not assumed).

### Re-read of the changed regions

- `.github/workflows/quality.yml:10-28` — the whole `type-check` job: checkout → Setup uv → Setup
  Python → Sync tooling → `Run mypy (gate)` → **`Run mypy scripts/ (gate)`** → `Run ty (informational)`
  (`continue-on-error: true`).
- `scripts/verify_spec.py:1-100` — module header (stdlib-only imports: `contextlib`, `re`, `sys`,
  `pathlib.Path`) and the `main()` prologue holding the `:74` narrowing.

### Candidates considered

| # | Candidate | Decision | Reason (one line) |
|---|---|---|---|
| 1 | Replace the `hasattr` guard with `sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]` (0 added lines instead of +2; precedent `src/main.py:108/111` uses exactly `# type: ignore[union-attr]` with a trailing reason) | **rejected** | It is the smaller diff and it removes the one real duplication (the guard and the enclosing `suppress(AttributeError, …)` cover the same case), but T-001's purpose is to *widen* type coverage: the ignore deletes the check on the only line in `scripts/` the new gate examines, while the guard keeps mypy checking the call. Runtime duplication is harmless — the suppress still covers the `ValueError`/`OSError` that `reconfigure` itself can raise. |
| 2 | `isinstance(sys.stdout, io.TextIOBase)` | **rejected (not re-tried)** | Rejected at S4.2 by measurement: mypy then reports `"TextIOBase" has no attribute "reconfigure"`, and it would skip the call for a stream that does have `reconfigure`. |
| 3 | `cast(...)` on `sys.stdout` | **rejected (not re-tried)** | An assumption, not a guard — same reasoning recorded at S4.2. |
| 4 | Drop the now-overlapping `AttributeError` from `contextlib.suppress(AttributeError, ValueError, OSError)` | **rejected** | Touches pre-existing error handling for zero gain, and narrows the contract if `sys.stdout` is itself a proxy object whose attribute lookup raises. |
| 5 | Merge the two mypy steps into one (`uv run mypy src/ scripts/`) — 1 changed line instead of 2 added | **rejected** | AC-025 clause 1 greps the job block for the literal `uv run mypy scripts/`, which the merged command does not contain (the node would fail), and a merged step loses per-target failure attribution. |
| 6 | Extract a shared stdout-reconfiguration helper for `scripts/` | **rejected** | No second caller exists — see the grep evidence below; a helper for one call site is addition, not deletion. |
| 7 | Workflow step naming / ordering | **no change needed** | `Run mypy scripts/ (gate)` matches the neighbours' `Run <tool> (<role>)` form and sits directly after the `src/` gate, before the informational `ty` step — the ordering the spec asks for ("next to `uv run mypy src/`", REQ-025). |
| 8 | Anything else a reviewer would call noise | **none found** | The diff is 2 added lines in a workflow file and 2 added / 1 removed in the script; no new abstraction, import, comment or config key was introduced by S4.2. |

### Grep evidence: no shared `reconfigure` pattern was missed

`grep -rn "reconfigure" scripts/ src/` — the only `sys.stdout.reconfigure` in the repository is
`scripts/verify_spec.py:74-75` (the T-001 line). Every other hit is unrelated:
`src/backend/logging/_pipeline.py` (`_reconfigure` / `setup_logger` sink reconfiguration, REQ-001/INV-001
of the logging feature) and logging/settings tests. The other two scripts
(`scripts/check_traceability.py`, `scripts/validate_task_dag.py`) never touch `sys.stdout`; their
non-ASCII content is em-dashes in docstrings/comments, never printed — so there is nothing to align
with and no sibling script left un-fixed by this change.

### Gates

**No changes made → no gate re-run** (implement skill, S4.4/S4.3 done-criteria: a refactor step that
made zero file changes skips the `green_command` re-run; the GREEN recorded at S4.2 stands, and the
ruff result on the changed path is unchanged because the changed paths are unchanged). Full suite and
repo-wide ruff remain Phase 5 gates (P-6).

**S4.3 gate: no-op — the S4.2 implementation is already the smallest form that keeps mypy checking the
call; the only smaller alternative (a `type: ignore`) trades the widened gate for a shorter diff and was
rejected on purpose. Files changed by this step: none (this record only).**

---

## Phase 4 — S4.4 (T-001) Commit + update status (2026-10-09)

**Objective:** set T-001 to `"status": "VERIFIED"` in the task DAG, sync the `docs/tasks/` copy, record
the DAG state, commit. No implementation, test or spec file was touched by this step.

### Status flip

`T-001` `"status": "PENDING"` → `"status": "VERIFIED"` in both DAG copies:

- `.github/task-runner/tasks.json:152` (active build environment)
- `docs/tasks/structure-map.tasks.json:152` (planning copy)

Both files were edited at the same place (T-001's `"dependencies": []` line is the only empty-dependency
block in the DAG, so the anchor is unique) and the edit is the **only** change in either file.

### Both copies in sync (proven, not eyeballed)

```
$ diff .github/task-runner/tasks.json docs/tasks/structure-map.tasks.json
(no output; exit 0 → the two files are byte-identical)
```

Programmatic cross-check (`json.load` of both files):

```
task entries equal: True
top-level keys equal (feature/spec/branch/change_type/adr/grouping/gate_interlock/id_coverage): True
statuses: T-001 VERIFIED, T-002..T-007 PENDING
```

The DAG validator's own `check_sync` (which compares the per-task `status` field between the two
files) also ran and passed — see the gate below.

### Gates (cheap, step-scoped; the full suite stays a Phase 5 gate)

| Gate | Command | Result |
|---|---|---|
| Task DAG validator (docs copy → also runs `check_sync` against the runner copy) | `uv run python scripts/validate_task_dag.py docs/tasks/structure-map.tasks.json` | **PASSED** — `Task DAG validation PASSED: 7 tasks, acyclic, well-formed.` exit 0 |
| Traceability referential integrity | `uv run python scripts/check_traceability.py` | **PASS** — `Traceability: PASS (822 matrix rows, 136 spec IDs, 801 test functions)` exit 0 |
| T-001 `green_command` (re-run at close) | `uv run pytest tests/acceptance/test_structure_map.py::test_ac_025_mypy_covers_scripts tests/acceptance/test_structure_map.py::test_nfr_004_mypy_and_ruff_clean -v` | **2 passed in 1.55s** exit 0 (`--randomly-seed=1958164124`) |
| ruff | n/a for this step — the step's changed paths are two JSON files and this Markdown record; no Python was written or modified. The S4.2 ruff result on the changed paths (`scripts/verify_spec.py`, `tests/acceptance/test_structure_map.py`) stands. |

Not re-run here (already recorded at S4.2, unchanged inputs): `uv run mypy scripts/` (exit 0),
`uv run mypy src/` (exit 0), the `verify_spec.py` witness report (byte-identical), and the
`-p no:randomly` variant of the two nodes.

### T-001 close-out

T-001 (REQ-025 / AC-025 / NFR-004) is **VERIFIED**: RED observed at S4.1 (`6eab550`), GREEN at S4.2
(`b1c6116`), refactor no-op at S4.3 (`2e522c0`), status VERIFIED at S4.4 (this commit). All six
`completion_gates` of the task are covered by the S4.1/S4.2 records plus the two gates re-run above.

### DAG state for the orchestrator (after this commit)

| Task | Group | Dependencies | Status |
|---|---|---|---|
| T-001 | tooling — `scripts/` joins the type gate (ADR-086) | — | **VERIFIED** |
| T-002 | `scripts/make_map.py` — generator harness (module, CLI, file set, exit codes, document shape) | T-001 ✅ | PENDING ← **ready** |
| T-003 | `scripts/make_map.py` — Directory tree, Packages scope, group/module headers, path form | T-002 | PENDING |
| T-004 | `scripts/make_map.py` — symbol inventory | T-003 | PENDING |
| T-005 | `scripts/make_map.py` — `--check` semantics, determinism, hook-clean output | T-004 | PENDING |
| T-006 | integration surface — the skill, the pre-commit hook, AGENTS.md, the advisory rule, the freshness policy | T-005 | PENDING |
| T-007 | the committed artifact — `STRUCTURE.md` | T-006 | PENDING |

- **VERIFIED: 1 of 7** (T-001). **PENDING: 6** (T-002, T-003, T-004, T-005, T-006, T-007).
- The DAG is a single linear chain, so exactly **one** task is ready: **T-002** — it is therefore also
  the easiest next task by default (no ordering choice exists), and it is the natural next step: it
  creates `scripts/make_map.py` from scratch, so nothing else can be verified before it lands.
- Next atomic step: **S4.1 (T-002)** — pick T-002 and confirm RED on its `red_command` set.

**S4.4 gate: PASSED — T-001 `VERIFIED` in both DAG copies (byte-identical `diff`, exit 0; validator
`check_sync` passed), DAG validator PASSED, traceability PASS, `green_command` 2 passed. Files changed
by this step: the two DAG copies and this record.**

## Phase 4 — S4.1 (T-002) RED re-confirmation (2026-10-09)

**Picked task: T-002** — `scripts/make_map.py` generator harness (module, CLI, file set, exit codes
2/4, document shape); REQ-001/002/003/004/006/007/008 · AC-001/002/003/006/007/008 ·
EDGE-003/004/005/006/007/008/014 · NFR-001/003/006; `dependencies: ["T-001"]`, `status: PENDING`.

**Pick rationale.** The DAG is a single linear chain (T-001 → T-002 → … → T-007), and T-001 is
`VERIFIED` (`80d7c15`), so **exactly one task is ready: T-002** — T-003…T-007 are dependency-blocked.
No ordering choice exists, so the AGENTS.md "easiest first" tie-break is moot; T-002 is also the
necessary next step, since it creates `scripts/make_map.py` (absent at this head — `scripts/` holds
only `check_traceability.py`, `validate_task_dag.py`, `verify_spec.py`) and nothing later can be
verified before it lands. **No implementation was written in this step.**

### RED evidence (red_command run verbatim, re-measured — not carried over from S3.2)

```text
uv run pytest tests/acceptance/test_structure_map.py::test_ac_001_stdlib_only_and_single_read tests/acceptance/test_structure_map.py::test_ac_002_cli_options_and_defaults tests/acceptance/test_structure_map.py::test_ac_003_file_set_includes_untracked_drops_deleted tests/acceptance/test_structure_map.py::test_ac_008_document_shape tests/acceptance/test_structure_map.py::test_edge_006_out_parent_directory_created tests/acceptance/test_structure_map.py::test_edge_007_non_git_root_falls_back_to_ignore_list tests/acceptance/test_structure_map.py::test_edge_008_deleted_tracked_file_absent tests/acceptance/test_structure_map.py::test_edge_014_max_depth_below_one_is_usage_error tests/acceptance/test_structure_map.py::test_nfr_001_full_run_under_two_seconds tests/acceptance/test_structure_map.py::test_nfr_003_deptry_clean tests/unit/test_make_map.py::test_ac_006_parse_error_is_hard_failure tests/unit/test_make_map.py::test_ac_007_grammar_is_the_running_interpreter tests/unit/test_make_map.py::test_edge_003_newer_syntax_is_hard_failure tests/unit/test_make_map.py::test_edge_004_non_utf8_is_hard_failure tests/unit/test_make_map.py::test_edge_005_unopenable_file_is_hard_failure -v

=========================== short test summary info ===========================
FAILED tests/unit/test_make_map.py::test_edge_005_unopenable_file_is_hard_failure
FAILED tests/unit/test_make_map.py::test_edge_003_newer_syntax_is_hard_failure
FAILED tests/unit/test_make_map.py::test_ac_006_parse_error_is_hard_failure
FAILED tests/unit/test_make_map.py::test_ac_007_grammar_is_the_running_interpreter
FAILED tests/unit/test_make_map.py::test_edge_004_non_utf8_is_hard_failure
FAILED tests/acceptance/test_structure_map.py::test_ac_001_stdlib_only_and_single_read
FAILED tests/acceptance/test_structure_map.py::test_edge_014_max_depth_below_one_is_usage_error
FAILED tests/acceptance/test_structure_map.py::test_edge_007_non_git_root_falls_back_to_ignore_list
FAILED tests/acceptance/test_structure_map.py::test_ac_002_cli_options_and_defaults
FAILED tests/acceptance/test_structure_map.py::test_edge_008_deleted_tracked_file_absent
FAILED tests/acceptance/test_structure_map.py::test_nfr_001_full_run_under_two_seconds
FAILED tests/acceptance/test_structure_map.py::test_ac_008_document_shape
FAILED tests/acceptance/test_structure_map.py::test_edge_006_out_parent_directory_created
FAILED tests/acceptance/test_structure_map.py::test_ac_003_file_set_includes_untracked_drops_deleted
======================== 14 failed, 1 passed in 2.23s =========================
```

**15 items collected, 14 failed, 1 passed, 0 errors, 0 skipped** — identical to the Phase 3 gate
(`d945952`, 14 failed / 1 passed). There is **no collection error, no import error and no fixture
error anywhere**: every node was collected, its body ran, and it reported a `Failed:`/`AssertionError`
at its own assertion or at an explicit `pytest.fail` guard. The single pass is
`test_nfr_003_deptry_clean`.

### Per-node results and the clause each node pins

| # | Node (def line) | Clause pinned | Observed failure (site) | Result |
|---|---|---|---|---|
| 1 | `test_ac_001_stdlib_only_and_single_read` (:248) | AC-001: run exits 0 · only stdlib imports · exactly **one** file-read call site · `deptry .` exits 0 | `pytest.fail`: `scripts\make_map.py does not exist — T-002 Phase 4 has not implemented the generator` (:252) | FAILED |
| 2 | `test_ac_002_cli_options_and_defaults` (:270) | AC-002: `--help` lists all six options (`_CLI_OPTIONS`, :138) and states the `STRUCTURE.md` and `4` defaults · `--out here.md` resolves against the CWD · `--root` defaults to the script's repository root · `--nope` → usage exit 2 | `_map_text` fail: `no map file at …\test_ac_002_cli_options_and_de0\default.md (exit 2)` — the default-`--root` run wrote nothing (:238) | FAILED |
| 3 | `test_ac_003_file_set_includes_untracked_drops_deleted` (:303) | AC-003: a new **untracked** `.py` appears in the map; a tracked file **deleted** from the working tree is omitted | `no map file at …\test_ac_003_file_set_includes_0\STRUCTURE.md (exit 2)` (:238) | FAILED |
| 4 | `test_ac_008_document_shape` (:326) | AC-008 (REQ-008): `# Repository structure`, one blank line, the generated-by line, `## Directory tree`, `## Packages` — nothing else; no timestamp, absolute path, drive letter, host or user name | `no map file at …\test_ac_008_document_shape0\STRUCTURE.md (exit 2)` (:238) | FAILED |
| 5 | `test_edge_006_out_parent_directory_created` (:353) | EDGE-006: a missing `--out` parent directory is created before writing (clause 1 exit 0, clause 2 a non-empty file at the nested path) | both clauses: `clause 1: exit 2 …` + `clause 2: …\deep\nested\STRUCTURE.md was not written (its parents did not exist)` (:367) | FAILED |
| 6 | `test_edge_007_non_git_root_falls_back_to_ignore_list` (:370) | EDGE-007: a non-git `--root` uses the built-in ignore list (`.venv`, `__pycache__`, `data` absent; `src/mod.py` present), prints **exactly one** git limitation note to stderr, does **not** parse `.gitignore`, still exits 0 | `no map file at …\test_edge_007_non_git_root_fal0\STRUCTURE.md (exit 2)` (:238) | FAILED |
| 7 | `test_edge_008_deleted_tracked_file_absent` (:406) | EDGE-008: a tracked file deleted from the working tree (still in the index) is absent from the map | `no map file at …\test_edge_008_deleted_tracked_0\STRUCTURE.md (exit 2)` (:238) | FAILED |
| 8 | `test_edge_014_max_depth_below_one_is_usage_error` (:428) | EDGE-014: `--max-depth 0` and `--max-depth -3` each produce an **argparse usage error on stderr** and exit 2 | `--max-depth 0: no argparse usage error on stderr: …` and the same for `--max-depth -3` (:444) | FAILED |
| 9 | `test_nfr_001_full_run_under_two_seconds` (:451) | NFR-001: a full generate run over this repository exits 0 in under 2 s | `generate run exits 2: … can't open file '…\scripts\make_map.py'` — `assert 2 == 0` (:457) | FAILED |
| 10 | `test_nfr_003_deptry_clean` (:464) | NFR-003: `deptry .` exits 0 (no unused/missing/misplaced dependency) | — | **PASSED** |
| 11 | `test_ac_006_parse_error_is_hard_failure` (unit :136) | AC-006, five clauses: exit **4**; every offending path reported once, sorted, `--root`-relative, with `SyntaxError`; nothing on stdout in generate mode; a pre-existing output file left **byte-unchanged**; no output file written at all | `_run_generator` guard `pytest.fail` — generator module absent (test_make_map.py:56) | FAILED |
| 12 | `test_ac_007_grammar_is_the_running_interpreter` (unit :162) | AC-007, four clauses: syntax the running interpreter accepts (`type Alias = int \| None`, `def first[T](…)`) exits 0; `--feature-version 3.12` exits **2** (no grammar option, REQ-002); `--help` exits 0; `--help` advertises no `feature_version`/grammar option | same guard (:56) | FAILED |
| 13 | `test_edge_003_newer_syntax_is_hard_failure` (unit :190) | EDGE-003: source newer than the interpreter → `SyntaxError` → exit 4, `src/future.py` reported once naming the type, no output file | same guard (:56); the fixture self-check `_is_unparseable` passed, so the fixture is valid test data | FAILED |
| 14 | `test_edge_004_non_utf8_is_hard_failure` (unit :210) | EDGE-004: a file that is not valid UTF-8 → `UnicodeDecodeError` → exit 4, `src/latin.py` reported once naming the type, no output file | same guard (:56); the fixture self-check (must **not** decode as UTF-8) passed | FAILED |
| 15 | `test_edge_005_unopenable_file_is_hard_failure` (unit :234) | EDGE-005: an unopenable file (Windows sharing violation via `_unopenable`) → exit 4, `src/locked.py` reported **exactly once** naming an OSError-family type, no output file | same guard (:56) | FAILED |

### Non-vacuity

- Every failing node's message names the **concrete missing behavior** — the absent generator module,
  the map file it should have written, or the argparse usage line it should have printed — never an
  import, collection or fixture problem. The unit-file guard at `test_make_map.py:45-56` is
  deliberate (`pytest.fail` so "the unimplemented generator … must surface as a test failure, never
  as a collection/import error"), which is why the run reports 14 `FAILED` and **0 `ERROR`**.
- The `exit 2` in the acceptance messages is **CPython's** "can't open file" exit code, not the
  generator's argparse usage exit. No node passes by coincidence on it: `test_edge_014` additionally
  requires an argparse usage line on stderr (absent → fails), and `test_ac_007` clause 2 is never
  reached because the unit helper fails first.
- The fixture-side self-checks fired and passed, so the RED is not invalid test data (AGENTS.md
  Phase 3): `test_ac_007` asserts `ast.parse(modern)` succeeds before running; `test_edge_003`
  `pytest.fail`s if its source parses on the running interpreter; `test_edge_004` `pytest.fail`s if
  its bytes decode as UTF-8; `test_edge_005` skips only when `mode 000` cannot block root (not the
  case here — 0 skips in the run).
- `test_nfr_003_deptry_clean` passes **at RED** because `deptry .` is already clean over the scan set
  (`src/`, `migrations/`, `scripts/`) before the generator exists. It is a regression guard, not a
  witness of T-002's code: S4.2 must keep it green by staying stdlib-only with **no**
  `pyproject.toml`/`uv.lock` change (AC-001 clause 4 asserts the same thing from inside the
  generator's own run).
- **NFR-001 skipif calibration guard is live, not skipped**: `_CALIBRATION_REFERENCE_SECONDS = 0.011`
  and the guard skips only when the best-of-3 `ast.parse` micro-benchmark (`_calibrate`, :162-170,
  40 rounds) exceeds 6× that. On this host the node **ran** (it is in the FAILED list, not skipped),
  so the < 2 s wall-clock assertion is a real gate S4.2 must meet.

### S4.2 work list (what implementation must do — no code written here)

1. **Create `scripts/make_map.py`** (the only allowed source file) importing **only** the standard
   library — `ast` (incl. `ast.unparse`), `argparse`, `pathlib`, `subprocess`, `sys`, plus
   `collections`/`re`/`dataclasses` as needed — with the standard typing surface; no project
   dependency, **no logging framework at all** (REQ-001, ADR-086, spec §10 Observability).
2. **argparse surface with exactly the six REQ-002 options** — `--root`, `--out`,
   `--include-private`, `--max-depth` (default `4`, bound `>= 1`), `--check`, `-h/--help`; anything
   else is an argparse usage error exiting **2** (EDGE-014). `--out` resolves against the CWD;
   `--root` defaults to the repository root containing `scripts/make_map.py`, resolved with
   `pathlib` (AC-002). `--help` must state the `STRUCTURE.md` and `4` defaults and must **not**
   advertise a grammar/`feature_version` option (AC-007 clause 4).
3. **File set** = `git ls-files --cached --others --exclude-standard` filtered to `*.py` and kept only
   for paths that exist on disk (REQ-003, AC-003, EDGE-008). Non-git root or no git → the built-in
   ignore list (`.git`, `.venv`, `__pycache__`, `.mypy_cache`, `.ruff_cache`, `.pytest_cache`, `data`,
   `dist`, `build`, `.idea`), **no `.gitignore` parsing**, and the limitation note printed to stderr
   **exactly once** (EDGE-007).
4. **One read per file** — the line count and the AST must come from the *same* read; AC-001 clause 3
   counts read call sites in the module's own AST and requires exactly one (REQ-001, AC-001).
5. **Hard-failure path** (REQ-006, AC-006, EDGE-003/004/005): on `SyntaxError`, `UnicodeDecodeError`
   or `OSError` for any file in the set — print every offending path once, **sorted**, `--root`-
   relative, with the exception type; write **no** output file; leave a pre-existing output file
   **byte-unchanged**; exit **4**. No degraded mode, no `(parse error)` marker, nothing on stdout in
   generate mode.
6. **Exit-code precedence 2 → 4 → 3 → 1 → 0** (REQ-004), structured so T-005 can insert 3 (missing
   `--out` in `--check` mode) then 1 (stale) in the same order. **This task produces 2 and 4 only**;
   `--check`'s comparison is **not** implemented here — AC-004/AC-005 are T-005's gate, and 1 and 3
   never occur in generate mode.
7. **REQ-008 document shape** — `# Repository structure`, one blank line, the generated-by line,
   `## Directory tree`, `## Packages`, nothing else; no timestamp, no version banner, no absolute
   path, no drive letter, no host or user name. The **shape** is this task's gate (AC-008); the
   section **bodies** belong to T-003 (tree, group/module headers, path form) and T-004 (symbol
   inventory) — do not implement them here.
8. **Create `--out`'s parent directory** when missing, before writing (EDGE-006); write no file other
   than `--out` (INV-005's carve-out is exactly that directory).
9. **Type gate now covers the new module**: `uv run mypy scripts/` must be clean with
   `scripts/make_map.py` present under the repository's strict configuration
   (`disallow_untyped_defs`, `check_untyped_defs`, `python_version 3.14`) — the gate T-001 widened.
10. **NFR-001 stays skipif-guarded** on the measured calibration run (never a CI gate); the
    implementation must still finish a full generate run over this repository in under 2 s on a host
    that passes the calibration, so keep the per-file work linear and the subprocess count minimal.
11. **NFR-003 / NFR-006**: `uv run deptry .` must stay clean with no `pyproject.toml` change; the
    ~250-line target for `scripts/make_map.py` is a target, not a gate — Phase 5 records the actual
    line count.
12. **Gate set for S4.2 GREEN**: `green_command` = `uv run pytest tests/acceptance/test_structure_map.py tests/unit/test_make_map.py -v`; then `uv run mypy scripts/`, `uv run deptry .`, and `uv run ruff check` + `ruff format` on `scripts/make_map.py tests/acceptance/test_structure_map.py tests/unit/test_make_map.py`. No change to `pyproject.toml`, `uv.lock`, workflows, hooks, `AGENTS.md` or skills.

**S4.1 (T-002) gate: PASSED — RED re-observed per node (15 collected: 14 failed / 1 passed, 0 errors,
0 skips, matching Phase 3's `d945952`), every failing node failing on behavior, non-vacuity confirmed,
no implementation written. Files changed by this step: this record only.**

## Phase 4 — S4.2 (T-002) Implement + confirm GREEN (2026-10-09)

One file written: **`scripts/make_map.py` (new, 199 lines)** — the only file in
`allowed_files.source_files`. No test file was touched (the two test files are unchanged: ruff
reports them already formatted, and `git status` shows only the new module plus this record).

### Module structure (entry points and the T-005 insertion point)

| Unit | Role | Spec IDs |
|---|---|---|
| `_parse_args(argv)` | the six REQ-002 options and nothing else; `--max-depth < 1` → `parser.error` → argparse usage line on stderr + `SystemExit(2)` | REQ-002, EDGE-014, AC-002 |
| `_git_paths(root)` | `git ls-files --cached --others --exclude-standard -z`; `None` when git is unavailable (`OSError`) or `--root` is not a repository (non-zero return) | REQ-003, EDGE-007 |
| `_walk_paths(root)` | the non-git fallback over `rglob("*.py")`, skipping any path with a directory part in `_IGNORED_DIRS`; no `.gitignore` parsing | REQ-003, EDGE-007 |
| `_file_set(root)` | the two above joined: filtered to `*.py`, kept only where the path exists on disk, sorted; the ignore-list note printed **once** to stderr on the fallback branch | REQ-003, AC-003, EDGE-007, EDGE-008 |
| `_read_modules(paths, root)` | one read + one `ast.parse` per file; returns `(modules, report)` | REQ-001, REQ-006 |
| `_render(modules)` | the REQ-008 chrome + the interim tree listing; the two section **bodies** are T-003/T-004 | REQ-008, AC-008 |
| `main(argv)` | the exit-code dispatcher; `sys.exit(main())` under `__main__` | REQ-004 |
| `Module` (frozen dataclass) | `path` (root-relative POSIX), `source`, `tree`, `line_count` — the state T-003/T-004 render from | REQ-001 |

**Dispatcher = the REQ-004 precedence order, in place.** `main` runs: `_parse_args` (**2**, argparse
exits before anything is read) → `_file_set` + `_read_modules` → `if failures: return 4` →
`document = _render(...)` → `if args.check: return 0` → write → `return 0`. **T-005 inserts 3 then 1
at the marked line inside the `args.check` branch** — the comment in the source names it
(`# T-005 (REQ-005): compare document against the --out bytes here and return 3 then 1`), which is
exactly between the 4 and the 0, so the order `2 → 4 → 3 → 1 → 0` is preserved by construction.
`--check` is accepted by the CLI (AC-002 clause 1 lists it) but its comparison is **not** implemented
here: it renders and returns 0 without writing, so every AC-005 / AC-004 / INV-004 / INV-005 node
stays RED for T-005.

### One read per file (REQ-001 / AC-001 clause 3)

`_read_modules` is the module's **only** file-content read call site:
`source = (root / path).read_text(encoding="utf-8")`; the line count (`len(source.splitlines())`)
and the AST (`ast.parse(source, filename=path)`) are both computed from that same string. Verified
from the outside by `test_ac_001_stdlib_only_and_single_read`, whose `_read_call_sites` walk over the
module's own AST reports exactly one site (`read_text`) — the writing `out.write_text(...)` is not a
read site and the module contains no `open(` / `read_bytes`. Stdlib-only: `argparse`, `ast`,
`subprocess`, `sys`, `collections.abc`, `dataclasses`, `pathlib` — clause 2 (`_non_stdlib_imports`)
reports none, and no logging framework appears anywhere (ADR-086).

### File set and fallback (REQ-003, AC-003, EDGE-007, EDGE-008)

`git ls-files --cached --others --exclude-standard -z` run with `cwd=root` (index **plus**
untracked-but-not-ignored; `-z` keeps names byte-exact, decoded with `surrogateescape`), filtered to
`*.py`, then `(root / name).is_file()` — which is what drops a tracked file deleted from the working
tree (EDGE-008) and keeps a new untracked one (AC-003). `None` from `_git_paths` (git missing, or a
non-repository `--root`) switches to `_walk_paths` + the built-in ignore list
(`.git`, `.venv`, `__pycache__`, `.mypy_cache`, `.ruff_cache`, `.pytest_cache`, `data`, `dist`,
`build`, `.idea`), never `.gitignore`, with the note printed once from the fallback branch only.

### Hard-failure path (REQ-006, AC-006, EDGE-003/004/005) — observed directly

The whole set is read before the report is printed, so **every** offender is named, sorted,
`--root`-relative (POSIX form — the tests match `src/x.py` as a substring), one line each, naming the
exception type; nothing goes to stdout; no output file is written and a pre-existing one is never
touched (the write happens only after the 4 return). Direct run over a tree holding two syntax-error
files, a non-UTF-8 file and a good file (non-git root here, hence the leading note):

```text
note: --root is not a git repository (or git is unavailable): using the built-in ignore list; .gitignore is not parsed
src/a_bad.py: SyntaxError
src/latin.py: UnicodeDecodeError
src/z_bad.py: SyntaxError
exit=4
```

`ls` of that root afterwards: `src` only — no output file. Usage errors, same direct check:
`--max-depth 0` → the argparse usage block on stderr, `exit=2`, no file; `--feature-version 3.12` →
`exit=2` (no grammar option exists, REQ-007 / AC-007 clause 2).

### GREEN gate (`green_command`, the 15 T-002 nodes)

```text
uv run pytest tests/acceptance/test_structure_map.py::test_ac_001_stdlib_only_and_single_read … tests/unit/test_make_map.py::test_edge_005_unopenable_file_is_hard_failure -v
15 passed in 4.16s        (randomly seed 2971475432)
uv run pytest <same 15 node ids> -q -p no:randomly
15 passed in 5.58s
```

15/15 — the 14 nodes that were RED at S4.1 plus the already-green `test_nfr_003_deptry_clean`. The
five unit nodes no longer stop at the `test_make_map.py:56` module-absent guard: `_run_generator`
finds the module, runs it as a subprocess, and every clause assertion in their bodies executes —
`test_ac_006`'s five clauses (exit 4 · both paths once, sorted, naming `SyntaxError` · empty stdout ·
pre-existing bytes unchanged · no file at all), `test_ac_007`'s four (PEP 695 source exits 0 ·
`--feature-version` exits 2 · `--help` exits 0 · no grammar word in `--help`), `test_edge_003/004`
(exit 4 + the single sorted line naming `SyntaxError` / `UnicodeDecodeError`) and `test_edge_005`
(the `msvcrt` sharing violation reported once with an OSError-family type). The direct run above is
the same behavior observed outside pytest, so the pass is not a fixture artifact.

**NFR-001 ran, it was not skipped** (the calibration guard is untouched): the full generate run over
this repository — 343 files, a 351-line map — completed in **0.46 s** wall including the `uv`/interpreter
startup, against the 2 s budget. `test_nfr_003_deptry_clean` and AC-001 clause 4 both hold.

### Quality gates

| Gate | Command | Result |
|---|---|---|
| mypy (the widened REQ-025 gate) | `uv run mypy scripts/` | `Success: no issues found in 4 source files` (exit 0) |
| deptry (NFR-003) | `uv run deptry .` | `Success! No dependency issues found.` — 91 files scanned, **no `pyproject.toml` change** |
| ruff check (changed paths) | `uv run ruff check scripts/make_map.py tests/acceptance/test_structure_map.py tests/unit/test_make_map.py` | `All checks passed!` |
| ruff format (changed paths) | `uv run ruff format --diff <same paths>` | `3 files already formatted` |

No repo-wide `ruff check .` / `ruff format .` was run (Phase 5 sweep, P-6). The full suite was not run
(Phase 5 gate).

### NFR-006 line count (record, not a gate)

`scripts/make_map.py` = **199 lines** against the ≈250 target — under it, because T-002 implements
only the harness; T-003 (tree) and T-004 (symbol inventory) add the bodies that fill the target.

### Later-task nodes still RED (not implemented here)

`uv run pytest tests/acceptance/test_structure_map.py tests/unit/test_make_map.py tests/property/test_structure_map.py -q` →
**33 failed, 22 passed**. Of the 22: 15 are T-002's, 2 are T-001's already-green AC-025 / NFR-004, and
**5 pass incidentally** on the interim render — `test_ac_019_double_run_byte_identical_and_hook_clean`,
`test_nfr_007_output_identical_across_platforms`, and the property nodes `test_inv_001_render_is_deterministic`,
`test_inv_003_no_absolute_path_or_timestamp`, `test_inv_006_output_is_hook_clean` (verified: those three
property nodes pass on their own, 3 passed in 10.20s). They witness properties the harness already
satisfies (sorted-by-path determinism, relative POSIX paths, hook-clean bytes) — no test was weakened
and no T-003/T-004/T-005 behavior was implemented. Everything that needs the tree body, the Packages
body or the `--check` comparison is still RED: AC-004, AC-005, AC-009…AC-014, AC-016…AC-024, AC-026,
AC-027, EDGE-001/002/009/010/011/012/013/015/016, INV-002/INV-004/INV-005, NFR-002, NFR-005.

### Files changed (T-002, within `allowed_files`)

| File | Change |
|---|---|
| `scripts/make_map.py` | new, 199 lines — the generator harness |
| `docs/verification/structure-map.md` | this record |

No change to `pyproject.toml`, `uv.lock`, any workflow or hook, `AGENTS.md`, `.agents/`, `docs/todo/`,
`docs/questions/`, `docs/verification/traceability.md` or `tasks.json` (status flip is S4.4).

**S4.2 (T-002) gate: PASSED — 15/15 T-002 nodes GREEN (also GREEN with `-p no:randomly`), clause-level
evidence for the five unit nodes, mypy/deptry/ruff clean on the changed paths, NFR-001 run in 0.46 s,
NFR-003 clean with no dependency change, later-task nodes untouched and still RED.**

## T-002 — S4.3 refactor (keep GREEN) (2026-10-09)

Objective: improve the structure of `scripts/make_map.py` without changing specified behaviour, or
record a justified no-op. The module was read once and judged against the repo conventions (strict
typing, no needless abstraction, deletion over addition), the T-002 constraints (stdlib-only, exactly
one read call site, no logging, the REQ-004 precedence, EDGE-006, the REQ-006 hard-failure path, the
REQ-008 shape, the ~250-line NFR-006 target) and what T-003/T-004/T-005 must insert next.

### Candidates considered

| # | Candidate | Decision | Reason (one line) |
|---|---|---|---|
| 1 | `_walk_paths`: `not any(part in _IGNORED_DIRS …)` → `frozenset.isdisjoint` | **applied** | stdlib-native set test, states the intent (no directory part is ignored) in fewer tokens; identical semantics |
| 2 | `_file_set`: the `.py` filter and the on-disk check lived only in the git branch, so the two branches applied visibly different rules | **applied** | both rules now sit once, after the branch (`candidates` → `sorted(name … if (root / name).is_file())`); EDGE-008 now demonstrably covers the fallback too; the extra `is_file()` on walk results is a no-op (the walk already filtered it) |
| 3 | `main`: `for line in failures: print(line, …)` | **applied** | `print(*failures, sep="\n", file=sys.stderr)` — one line, byte-identical stderr |
| 4 | The one-read rule (REQ-001 / AC-001) was only in the docstring | **applied** | a two-line marker at the read site itself, where T-004 would be tempted to re-read for source segments; comments are invisible to the AC-001 AST witness, so the count stays 1 |
| 5 | Merge `_git_paths`/`_walk_paths` into one candidate-listing function | **rejected** | the only real duplication is the `.py` filter, and unifying it would force `rglob("*")` over the whole tree (incl. `data/`, `build/`) on the fallback branch — slower for no clarity gain; #2 already removes the asymmetry |
| 6 | Split `_render` into `_render_tree` / `_render_packages` stubs to pre-shape T-003/T-004 | **rejected** | dead abstraction until those tasks land; T-003 replaces one list comprehension, T-004 appends after `_PACKAGES_HEADING` — both insertions are already one line wide |
| 7 | Drop the unused `Module.source` field (or make `line_count` a property) | **rejected** | `source` is what makes the single read reusable — deleting it invites a re-read that breaks AC-001; `line_count` computed at the read site is the REQ-001 evidence, and a property would recompute per header |
| 8 | Typed args dataclass instead of `argparse.Namespace`; `_read_modules` renamed / report printing extracted | **rejected** | mypy already passes on `scripts/`; a second helper for three lines is addition, not deletion; parameter-order churn is noise |
| 9 | Shorten the module/function docstrings (spec-ID traces) | **rejected** | they are the spec→code traceability record the review gate reads, not prose noise |

Net effect: **8 added / 6 removed lines, `scripts/make_map.py` 199 → 201 lines** (still inside the
~250-line NFR-006 target; T-003/T-004/T-005 will push it past that and are the point where a split
into modules would be judged — recorded here as the open question for those tasks, not acted on).
No CLI surface, exit code, output byte, read-site count, ignore list, or precedence order changed.

What the refactor bought the later tasks: T-005's `--check` insertion is unchanged (the marked point
between the 4 and the 0 is untouched) and the failure-report line is one line shorter; T-003/T-004 get
a file set whose two rules are stated once (so the tree and the packages body can trust that every
`Module.path` is a `.py` file that exists, root-relative); the read-site marker tells the symbol
renderer to take text from `Module.source` instead of reading the file again.

### Gates re-run after the refactor (targeted only — no full suite, no repo-wide ruff)

```text
uv run pytest tests/acceptance/test_structure_map.py tests/unit/test_make_map.py -q
30 failed, 19 passed in 13.93s      (identical to the S4.2 baseline: 19 / 30, same node set)

uv run pytest <the 15 T-002 node ids> -q                 15 passed in 4.12s   (randomly seed active)
uv run pytest <the 15 T-002 node ids> -q -p no:randomly  15 passed in 4.91s

uv run ruff check scripts/make_map.py    All checks passed!
uv run ruff format scripts/make_map.py   1 file left unchanged
uv run mypy scripts/                     Success: no issues found in 4 source files (exit 0)
uv run deptry .                           Success! No dependency issues found. (exit 0)
```

The five hard-failure / fallback nodes (`test_ac_006`, `test_edge_003/004/005`, `test_edge_007`,
`test_edge_008`) are the witnesses for candidates 1–3 and they pass unchanged; `test_ac_001` is the
witness for candidate 4 (still exactly one read call site) and passes.

### Files changed (S4.3, T-002)

| File | Change |
|---|---|
| `scripts/make_map.py` | +8 / −6 (199 → 201 lines) — candidates 1–4 |
| `docs/verification/structure-map.md` | this record |

No test file, `pyproject.toml`, `uv.lock` (restored after `uv run` touched it), workflow, hook,
`docs/todo/`, `docs/questions/`, `docs/verification/traceability.md` or `tasks.json` was touched.

**S4.3 (T-002) gate: PASSED — behaviour-identical refactor applied, GREEN kept (19 passed / 30 failed
unchanged, 15/15 T-002 nodes GREEN with and without `-p no:randomly`), ruff + mypy + deptry clean.**

