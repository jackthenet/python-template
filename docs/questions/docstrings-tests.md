# Questions: docstrings-tests

One question file per change, created at **P.1 Frame** from this template and named `docstrings-tests.md`. It replaces the retired central `AI_Questions.md` (archived at `docs/questions/archive-AI_Questions.md`).

- **Change:** docstrings-tests (DOCS/CHORE)
- **TODO file:** `docs/todo/docstrings-tests.md`
- **Spec:** n/a
- **Opened:** 2026-10-10
- **Status:** OPEN  <!-- OPEN | ALL ANSWERED — set OPEN by the orchestrator at P.1; ALL ANSWERED once every question in this file has an answer (the orchestrator records it together with the `QUESTIONS-ANSWERED` TODO advance) -->
- **Answer rounds:** 0

Every question that needs user input is recorded HERE — never in a central file. A step that needs input records **all** of its open questions in one batch and returns `BLOCKED-USER`; the orchestrator presents them (as few `ask_user_question` rounds as possible, <= 4 per round, most blocking first), records the answers here, marks each **ANSWERED** and **incorporated**, and relaunches the step **once** with the full answer set. The change is `WAITING` while its questions are unanswered — the orchestrator works on another change meanwhile, it does not idle.

### Entry format

```markdown
## Q-<n> — <short title>
- **Step:** <P.2 Interrogate, or Sx.x <step name> — Phase <n>>
- **Why needed:** <the ambiguity, missing requirement, or decision>
- **Context:** <what the step had learned at the time>
- **Question:** <the question for the user>
- **Recommended:** <the step's proposed answer + one-line reason>
- **Answer:** <the user's answer>  (or **PENDING**)
- **Date:** <YYYY-MM-DD>
- **Status:** PENDING | ANSWERED
- **Incorporated:** no | yes — <where: REQ-XXX / AC-XXX / spec section / decision>
```

### Category coverage

| Category | Result |
|---|---|
| Environment & baseline (can the DOCS/CHORE gate be met at all) | covered (Q-01, Q-02) |
| Tooling & gate configuration (which rule codes, where the gate lives, drift) | covered (Q-03, Q-05, Q-08, Q-11) |
| Scope & boundaries / non-goals (which trees, which objects, what stays out) | covered (Q-04, Q-06, Q-07, Q-15, Q-24) |
| Traceability & naming (ID in docstring vs test name vs matrix; stale IDs) | covered (Q-09, Q-10, Q-12, Q-13, Q-14) |
| Testing & witnesses (what proves no behavior delta; is the new gate witnessed) | covered (Q-16, Q-17) |
| Sequencing & merge conflicts (other in-flight/backlog changes) | covered (Q-18, Q-19) |
| Generated artifacts (`STRUCTURE.md` regeneration, NFR-002 budget, pre-commit hook) | covered (Q-02, Q-20) |
| Governance & guidance (AGENTS.md bullet, skill, version, branch prefix, matrix) | covered (Q-21, Q-22, Q-23) |
| Effort & change size (480–855 sites, one change vs split, escape hatches) | covered (Q-25, Q-26) |
| Interfaces & public API | skipped — no `src/` symbol, no runtime interface and no user-visible contract is touched; the only "interface" is the ruff config, covered under Tooling (Q-03) |
| Data & state | skipped — docstrings are inert text; no schema, database or persisted state is touched (no SQLModel/alembic import anywhere under `tests/`), and `check_traceability.py` reads only `def test_…` names and matrix rows |
| Performance | skipped — docstrings cost no runtime path, `complexipy` counts (≤ 15 gate) and coverage (`source = ["src/backend","src/frontend"]`, `fail_under = 92`) are unaffected; measured `ruff check tests` runs in ~1 s |

## Preparation questions (P.2)

26 entries, one `BLOCKED-USER` batch, most-blocking first (Q-01…Q-04 are the gate blockers; the orchestrator can present them as round 1).

**Measured at `be1eb5a` (2026-10-10), the facts every entry below is grounded in:**

- `uv run ruff check .` → **All checks passed!** and `uv run ruff format --check .` → **343 files already formatted**. The gate is green today only because `pyproject.toml:222-226` carries `[tool.ruff.lint.per-file-ignores]` = `"tests/*" = ["D"]`, `"scripts/*" = ["D"]`, `"migrations/*" = ["D"]`, `".github/*" = ["D"]` — the `tests/*` line's own comment reads `# exempt from the docstring rules (Q-3 / Q-29 → sibling change docstrings-tests)`. `[tool.ruff.lint] select` (`:183-189`) = `E, F, I, UP, TID, D`; `ignore = ["E501", "UP046"]`; `lint.pydocstyle.convention = "google"` (`:220-221`).
- Deleting only the `"tests/*"` line makes `uv run ruff check tests` report **855** `D` violations: **D103 363** (undocumented public function), **D205 201** (1 blank line between summary and description), **D209 168** (multi-line closing quotes on their own line), **D102 51** (undocumented public method), **D104 42** (undocumented public package), **D107 21** (undocumented `__init__`), **D301 6** (escape sequence → raw docstring), **D105 3** (undocumented magic method). A bare `--select D` **without** the google convention adds **D401 133** (non-imperative mood) for 988 — the convention already disables D401.
- Gate variants (measured with `--ignore` over the same selection): exempt `D2,D3,D4` → **480 sites in 100 files**; exempt `D2,D3,D4,D104` → **438**; exempt `D2,D3,D4,D104,D105,D107` → **414** (only D102+D103 enforced); full removal → **855 sites in 147 files**.
- D1xx by tree: `tests/acceptance` **191**, `tests/unit` **123**, `tests/*.py` top level (**17 `conftest.py` + 12 `*_test_helpers.py`**) **84**, `tests/property` **38**, `tests/contract` **26**, `tests/integration` **18**. D2/D3/D4 by tree: acceptance **162**, unit **137**, property **45**, contract **16**, integration **13**, top level **2**. Inside the 29 map-scoped `conftest.py`/`*_test_helpers.py` files: D102 51, D103 34, D105 3, D107 21 = **109**.
- AST counts over `tests/` (251 `.py` files): **815** `test_*` functions — **502 documented, 313 undocumented**. At the parent change's P.2 (2026-10-07) it was 414/313 of 727, so **every one of the 88 test functions added since then already carries a docstring** — the convention holds voluntarily, the undocumented 313 are all pre-existing. Module level: **209 of 251** files have a module docstring; **all 192 non-`__init__` modules are documented**; **42 of 59 `__init__.py`** are not (the D104 count).
- Traceability: `uv run python scripts/check_traceability.py` → **`Traceability: PASS (881 matrix rows, 136 spec IDs, 801 test functions)`**; `docs/verification/traceability.md` is **1134 lines**; **all 801 unique test function names are cited in the matrix — 0 orphans, 0 citations pointing at a missing test**. `scripts/check_traceability.py` parses `def test_…` names (`TEST_DEF_RE`) and matrix rows; it **never reads a docstring**.
- ID redundancy measured three ways: **624 of 815** test names already encode an ID (`test_ac_031_login_success_event`); **487 of 502** test docstrings start with an ID; **337** tests carry both a name-encoded and a docstring-encoded ID and **0 disagree**; **0** ID mentions in any test docstring are undefined in `docs/specs/` (136 IDs defined). So the convention is currently clean — and nothing enforces it.
- Suite: `uv run pytest tests/ -q -p no:randomly` → **1 failed, 815 passed, 1 skipped in 252 s**. The failure is `tests/acceptance/test_structure_map.py::test_ac_021_committed_map_matches_fresh_render` (committed `STRUCTURE.md:452` says `docs/ — 223 files (process record)`, a fresh render says **224**; on this Windows host it also differs by line ending, `i/lf w/crlf`, `core.autocrlf = true`, no `.gitattributes`).
- `STRUCTURE.md` is **1941 lines** against the NFR-002 budget of **2000** (`_NFR_002_LINE_BUDGET = 2_000`, `tests/acceptance/test_structure_map.py:1425`); `uv run python scripts/make_map.py --check` **fails on `main` today**; the check runs **only** as the pre-commit hook `structure-map-check` (`files: \.py$`) — there is no CI map job (ADR-085).
- `tests/acceptance/test_structure_map.py::test_nfr_004_mypy_and_ruff_clean` asserts `ruff check .`, `ruff format --check .`, `mypy src/`, `mypy scripts/` inside the suite, and `.github/workflows/lint.yml` runs `ruff check .` + `ruff format --check .` filtered to `src/** tests/** pyproject.toml .pre-commit-config.yaml .github/workflows/lint.yml .github/hooks/**` — so an un-backfilled `tests/` breaks **both** CI and an acceptance test.
- **Nothing asserts on the content of `per-file-ignores`.** The only tests that read `pyproject.toml` are `tests/contract/logging/test_dependency_contract.py` (project dependencies + deptry `per_rule_ignores`) and `test_structure_map.py` (which pins `pyproject.toml` as a top-level file row).
- **Overlap check** (against `docs/specs/` and every TODO in `docs/todo/`, live and archive): the parent change **`chore/ruff-d-docstrings`** is MERGED and created this TODO deliberately — `docs/questions/archive/ruff-d-docstrings.md` **Q-29** records "`src/` now, `tests/` as a follow-up change … the `tests/` backfill **and** its gate move to a new sibling change **`docstrings-tests`**", and `docs/verification/ruff-d-docstrings.md:25` records `tests/ | 827 | 743 | no — per-file-ignores (Q-3/Q-29 → sibling docstrings-tests)` with finding **F-7**: "P.2 recorded `tests/` = 762 `D` sites … **`docstrings-tests` must re-measure at its own P.4**" (this file's 855 is that re-measurement). No spec governs test docstrings; `docs/specs/logging-coverage.md` REQ-009/AC-009 is the only spec that governs docstring **content** and it covers `src/` traced classes. `docs/specs/structure-map.md` REQ-013/AC-021 + NFR-002 govern the generated map. Live TODO collisions: `settings-public-registry-setter` (IN-WORKFLOW, PR #73) edits the **same** `[tool.ruff.lint]` table and adds `tests/unit/architecture/test_singleton_slots.py`; `map-default-drop-shift` (WAITING, PR #79) and `complexipy-scripts` (PREPARING) collide on `STRUCTURE.md`/`scripts/make_map.py`; `python-3.15-upgrade` (WAITING) lists `ruff-d-docstrings` as a live collision; `complexipy-scripts`' own P.2 already cleared the pair — "`docs/todo/docstrings-tests.md` touches the `tests/*` ruff `D` ignore, not `scripts/*` … **No double work found**". **No duplicate change found.**

## Q-01 — Is this DOCS/CHORE at all, when its Phase 5 gate says "no test files touched"?
- **Step:** P.2 Interrogate
- **Why needed:** the type fixes the phase set, the Phase 5 gate and the version bump. AGENTS.md criterion 5 (DOCS/CHORE: "documentation, comments, configuration, CI, tooling") fits, but Phase 5 check 16 for DOCS/CHORE says "confirm **no test files** or behavior were touched" — and this change edits 100–147 test files by design. REFACTOR would fit the "no observable behavior change" shape but demands a GREEN full-suite baseline, which `main` does not have (Q-02).
- **Context:** the parent change `chore/ruff-d-docstrings` was DOCS/CHORE and did the structurally identical thing one tree over: it added `D` to `[tool.ruff.lint] select` (a new CI-enforced rule) and edited `pyproject.toml`, `AGENTS.md`, `.pre-commit-config.yaml`, `mkdocs.yml` — 41 `src/` files, **0** test files, and its Phase 6 review recorded the diff-surface check as **NOTE (N-1)** rather than a failure. Its no-behavior-delta proof was a docstring-stripped AST digest over `src/` (84 files, 43 587 nodes identical; docstring hosts 628 → 859).
- **Question:** keep the P.1 classification **DOCS/CHORE** and record an explicit exemption of Phase 5 check 16 in `docs/verification/docstrings-tests.md` (the change *must* touch test files; the no-delta proof is Q-22), or reclassify to REFACTOR (and then satisfy the GREEN baseline first), or split the config flip from the backfill into two changes?
- **Recommended:** keep **DOCS/CHORE** and record the exemption — the change alters no externally observable behavior and matches criterion 5 (documentation + configuration); the parent is the direct precedent, and REFACTOR would additionally require a baseline `main` cannot currently provide.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-02 — `main` is RED on AC-021 (stale `STRUCTURE.md`): does this change own the map refresh?
- **Step:** P.2 Interrogate
- **Why needed:** the change must regenerate `STRUCTURE.md` anyway (Q-19), and the pre-commit `structure-map-check` hook fires on every `.py` file it commits — so it cannot commit a single backfilled test file while the map is stale. The pre-existing red has to be attributed before P.4 states the scope.
- **Context:** measured 2026-10-10 at `be1eb5a`: `uv run python scripts/make_map.py --check` fails; the suite's `test_ac_021_committed_map_matches_fresh_render` fails with `docs/ — 223 files (process record)` vs a fresh **224** (`git ls-files docs | wc -l` = 224 — the P.1 planning-record commits added `docs/` files after the last regeneration). Separately, on this host the same test fails on line endings (`i/lf w/crlf`, `core.autocrlf = true`, no `.gitattributes`, first byte diff at index 22). `docs/questions/complexipy-scripts.md` Q-01/Q-02 ask the **same two** questions for a different change, and `docs/todo/map-default-drop-shift.md` (WAITING, PR #79) also regenerates the map.
- **Question:** does this change regenerate `STRUCTURE.md` in its first commit and record the pre-existing red (as complexipy-scripts Q-01 recommends), or must the one-line map refresh land first as its own change so this branch starts from a GREEN `main`, and is the CRLF half treated as a CI/Linux-authoritative caveat or fixed with a `.gitattributes` here?
- **Recommended:** regenerate in this change's first commit and record the pre-existing failure; treat the Linux CI run as the authoritative GREEN gate and do **not** add `.gitattributes` here (repo-wide checkout behavior change = its own DOCS/CHORE TODO) — same resolution as complexipy-scripts Q-01/Q-02, so the two changes must agree on which one lands the refresh.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-03 — Which gate variant: full removal of the ignore, or a narrower code list?
- **Step:** P.2 Interrogate
- **Why needed:** this single decision sets the diff size (414 vs 855 sites) and therefore whether the change is one PR or several; it is the direct successor to the parent's Q-29, which deferred `tests/` but never chose the shape of the eventual gate.
- **Context:** measured variants over `tests/` with `pydocstyle.convention = "google"`: delete `"tests/*" = ["D"]` → **855 sites / 147 files**; `"tests/*" = ["D2","D3","D4"]` → **480 / 100 files** (missing-docstring codes only); `"tests/*" = ["D2","D3","D4","D104"]` → **438**; `"tests/*" = ["D2","D3","D4","D104","D105","D107"]` → **414** (only D102/D103, i.e. functions and methods). The parent's own config uses the single-code `"D"` form and its record confirms ruff's per-file globs match across `/`, so `tests/*` already covers nested trees.
- **Question:** which gate lands — (a) delete the line entirely (full `D` family over `tests/`, 855 sites); (b) `"tests/*" = ["D2","D3","D4"]` — every docstring must exist, existing formatting stays free (480 sites); (c) (b) plus `D104` — packages exempt too (438); (d) only `D102`/`D103` enforced (414); (e) some other list?
- **Recommended:** **(b)** — it makes "every test carries a docstring" enforceable (the parent Q-4/Q-29 intent) at 480 sites, and it leaves the 375 cosmetic reformat sites (`D205`/`D209`/`D301`) out of an already large diff; a follow-up chore can flip the rest once the convention is settled.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-04 — Which test trees does the gate cover — all of `tests/`, or the evidence-bearing ones?
- **Step:** P.2 Interrogate
- **Why needed:** the TODO says "backfill the missing test docstrings" without naming a tree, and the AGENTS.md test hierarchy gives the five categories different jobs — the Phase 5/6 evidence rule attaches to acceptance tests, not to unit helpers.
- **Context:** D1xx sites per tree: `tests/acceptance` **191**, `tests/unit` **123**, top-level `tests/*.py` (conftest + helpers) **84**, `tests/property` **38**, `tests/contract` **26**, `tests/integration` **18**. The parent's Q-4 options included "(c) Required only for `tests/acceptance/`" and the user chose "(b) backfill all … and gate `tests/`" before Q-29 moved the whole thing here.
- **Question:** does the gate cover all of `tests/` (all five categories plus the top-level `conftest.py`/`*_test_helpers.py`), or only `tests/acceptance/` (191 sites), or acceptance + contract + property (the spec-evidence categories, 255 sites)?
- **Recommended:** **all of `tests/`** — the parent's Q-4 answer already chose "traceability enforceable, not a convention", a partial gate leaves a permanent carve-out in the same config table, and the per-tree counts show the whole set is 480 sites, not thousands.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-05 — Are the 375 format sites (`D205`/`D209`/`D301`) in scope, and is `ruff check --fix` allowed on them?
- **Step:** P.2 Interrogate
- **Why needed:** if the gate is the full `D` family (Q-03a), 375 of the 855 sites are reformatting of docstrings that already exist, in 49 files that the backfill does not otherwise touch — a second, independent kind of diff inside one change.
- **Context:** `D209` (168 sites, "multi-line open-on-same-line") is **auto-fixable**; `D205` (201 sites, "1 blank line required between summary line and description") is **not** and also hits module docstrings (e.g. `tests/acceptance/authentication/test_events.py:1:1`, `tests/acceptance/logging/test_get_logger.py:1:1`); `D301` (6 sites) requires a raw docstring. The parent change ran the same family in `src/` as separate commits, e.g. `a7894c8 docs(logging): fix docstring formatting (D205, D209)` and `df45d17 docs(sessionmanagement): fix docstring formatting (D205, D209, D403)`.
- **Question:** include the format family (and with which mechanism — `uv run ruff check --fix` for `D209` only, hand edits for `D205`, or neither), or defer it to a follow-up chore and gate `tests/` for the missing-docstring codes only?
- **Recommended:** **defer** — pair it with Q-03(b); `D205` needs a human-written summary line for 201 docstrings, which is a different task from writing 480 new ones, and mixing them makes the per-commit review unit meaningless.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-06 — Are the 42 undocumented `__init__.py` packages in scope?
- **Step:** P.2 Interrogate
- **Why needed:** `D104` fires on packages, and `tests/` is a package tree (`tests/__init__.py`, `tests/acceptance/__init__.py`, …). 42 of the 59 `__init__.py` files have no docstring, so the gate choice decides whether 42 near-empty files get prose.
- **Context:** measured: 59 `__init__.py` under `tests/`, 17 documented, **42 not** — exactly the D104 count. Those 17 that do carry one are one-liners naming the tree. `__init__.py` files are **not** in the structure map's Packages scope (`_PACKAGES_DIRS = ("src","scripts","migrations")` and only `conftest.py`/`*_test_helpers.py` render under `tests/`), so backfilling them changes no map content, only the tree's presence.
- **Question:** must every `tests/**/__init__.py` carry a docstring (and then what is acceptable prose for a test package — the category and feature it holds?), or is `D104` ignored for `tests/*` (Q-03c/d)?
- **Recommended:** **ignore `D104` for `tests/*`** — a docstring on a test package directory adds no information the directory name does not, and 42 filler lines would violate the parent's own no-filler rule (Q-15 there) before the gate even starts.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-07 — Do fixtures, `*_test_helpers.py` functions and test-class methods need docstrings?
- **Step:** P.2 Interrogate
- **Why needed:** the `D` family is not limited to `test_*` functions: enabling it over `tests/` also reaches fixtures, shared helper functions, test classes and their methods — 109 of the 480 D1xx sites are in the 29 top-level `conftest.py`/`*_test_helpers.py` files alone, and those 29 files are the only test files the structure map renders.
- **Context:** measured D1xx inside `conftest.py` + `*_test_helpers.py`: **D102 51, D103 34, D105 3, D107 21**. There are **26** `@pytest.fixture` functions in 17 `conftest.py` files, **6** documented. `tests/tooling_test_helpers.py` and its siblings are imported by other tests (AGENTS.md "Using the Test Tooling"), so their docstrings are genuinely read by users of the helper. The map renders each of these 29 modules as `#### <path> (<N> lines)` + the module docstring's first line + every signature with its docstring summary truncated at `_SUMMARY_LIMIT = 100` chars.
- **Question:** are fixtures, helper functions, test classes and their methods inside the gate (all of them / helpers yes and fixtures no / none), and does a fixture's docstring have to say anything beyond what its return type says?
- **Recommended:** **helpers yes, fixtures only where the fixture is non-obvious** — helper docstrings are consumed by other test authors and already appear in `STRUCTURE.md`; a `@pytest.fixture` returning a typed object usually restates its signature, which the no-filler rule (Q-13) would reject.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-08 — Are `D105` (magic methods) and `D107` (`__init__`) enforced for test code?
- **Step:** P.2 Interrogate
- **Why needed:** they are 24 of the 480 sites and they are the two codes where a required docstring is most likely to be pure filler; the choice must be made in the same config edit as Q-03/Q-06, not later.
- **Context:** measured: **D107 21** (undocumented `__init__`, all in test/helper classes), **D105 3** (magic methods). In `src/` the parent change **did** document `__init__` (e.g. commit `b96ad16 docs(mail): add missing docstrings (D107 x5, D102 x1)`), because those classes are published in `userdocs/api.md` via mkdocstrings. Test classes are not published anywhere.
- **Question:** enforce `D105`/`D107` over `tests/` as well, or add them to the `tests/*` ignore list alongside `D104` (Q-03d)?
- **Recommended:** **ignore them for `tests/*`** — 24 sites of near-guaranteed filler in unpublished test scaffolding; the same reasoning as Q-06, and it costs one extra code in a list that Q-03 already writes.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-09 — Must a test docstring name the REQ/AC it proves, when the matrix already maps all 801 tests?
- **Step:** P.2 Interrogate
- **Why needed:** the TODO's core idea ("each docstring names the REQ/AC the test proves") is only worth 480 new docstrings if it adds information the repository does not already carry; measured, it largely does not, so the rule needs either a justification or a narrower form.
- **Context:** measured: **all 801 unique test function names are already cited in `docs/verification/traceability.md`** (1134 lines, 881 rows) — 0 orphans and 0 dangling citations, and `scripts/check_traceability.py` enforces that referential integrity in CI (`spec-validation.yml`). **624 of 815** test names already encode the ID (`test_ac_031_login_success_event`); **487 of 502** existing docstrings start with an ID. So for a documented test the ID appears in three places; for the **313 undocumented** ones it appears in the name and the matrix but not in the file body.
- **Question:** is the docstring's job (a) to carry the ID (making it greppable in the file, and mandatory even where the name already encodes it), (b) to state **what the test proves in one line** with the ID included only when the name does not already carry it, or (c) ID mandatory **and** the matrix row must match it?
- **Recommended:** **(b)** — the matrix and the name already give CI-enforced traceability (0 orphans measured), so the docstring should add the thing neither gives: a readable statement of the behavior under test; forcing a duplicate `AC-031:` prefix on 624 tests whose name already says `test_ac_031_…` is the filler the parent's no-filler rule rejects.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-10 — If IDs are used, what is the exact prefix form?
- **Step:** P.2 Interrogate
- **Why needed:** three forms are in live use in `tests/`, and a rule that does not name one cannot be reviewed or checked; the form also decides whether a docstring can carry the REQ behind an AC.
- **Context:** measured house style is a bare ID-prefixed one-liner — `"""AC-001: publish() returns in < 10 ms and the handler runs on the worker."""`. The structure-map tests use a paired form — `"""AC-025 (REQ-025): the type-check job runs \`uv run mypy scripts/\`…"""`. 487 of 502 documented test docstrings start with an ID; **15** do not.
- **Question:** mandate one form — `AC-nnn: …`, `AC-nnn (REQ-nnn): …`, or free prose with the ID anywhere in the first line — and does the same form apply to helper/fixture docstrings (which prove nothing)?
- **Recommended:** **`AC-nnn (REQ-nnn): …` where the AC maps to exactly one REQ, otherwise `AC-nnn: …`** — it is the only form that lets a reader go from a failing acceptance test back to the requirement without opening the matrix, and it is already used by the newest test file in the repo.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-11 — Who checks that a cited ID is correct and still exists — nothing does today?
- **Step:** P.2 Interrogate
- **Why needed:** the whole risk of an ID-in-docstring rule is a wrong or stale ID that reads like evidence. Measured, the repo is clean today, and measured, **no** mechanism would catch the first wrong one.
- **Context:** measured: **0** of the 337 tests that carry both a name-encoded and a docstring-encoded ID disagree; **0** ID mentions in any test docstring are undefined in `docs/specs/` (136 IDs defined). `scripts/check_traceability.py` reads only `TEST_DEF_RE` (`def test_…`) and matrix rows — it never opens a docstring. No test or script asserts on docstring content except `tests/acceptance/logging_coverage/test_docstrings.py::test_traced_class_docstrings_mention_tracing`, which checks the wording of **`src/`** traced-class docstrings (AC-009). The parent change's Q-15 chose a **reviewer rule** over a scripted checker for the same class of problem ("No new tooling … becomes a Phase 6 review check").
- **Question:** enforce by (a) reviewer rule only (parent precedent), (b) extend `scripts/check_traceability.py` to parse docstring IDs and fail on an undefined ID or a name/docstring mismatch, (c) a new acceptance test that does the same, or (d) no check, accepting drift?
- **Recommended:** **(a) reviewer rule** for this change — it keeps the change DOCS/CHORE (option (b)/(c) is new tooling plus its own tests = new behavior, which per the Escalation Rules would reclassify it), and the measured 0/0 today means the rule starts from a clean state; open a backlog TODO for the scripted checker if the convention survives one cycle.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-12 — Should `check_traceability.py` learn to read docstrings at all?
- **Step:** P.2 Interrogate
- **Why needed:** it is the difference between "a docstring is documentation" and "a docstring is evidence", and it decides whether this change touches `scripts/` (which `complexipy-scripts` is simultaneously about to change) and whether a new spec/ADR is needed.
- **Context:** `check_traceability.py` today: 881 rows, 136 spec IDs, 801 test functions, exit 0, and it is a CI job (`spec-validation.yml`, `traceability`). `docs/todo/complexipy-scripts.md` (PREPARING, REFACTOR) plans to raise `check_traceability.py::check` (complexity **17**) and `::matrix_rows` (**19**) over the 15 ceiling — i.e. that file is about to be restructured by another change. AGENTS.md "Tests are the contract" already ranks tests above spec prose.
- **Question:** is docstring→ID parsing in scope here (yes/no); if yes, does it need a spec amendment (which spec owns it?) and does it force a reclassification to FEATURE/ISSUE?
- **Recommended:** **out of scope** — it is new enforced behavior with no spec owner, it collides with `complexipy-scripts` in the same file, and Q-09/Q-11 already show the matrix gives the enforcement; keep the docstring as human-facing intent.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-13 — What counts as filler in a test docstring, and who rejects it?
- **Step:** P.2 Interrogate
- **Why needed:** the TODO's own risk note is that a 480-docstring sweep invites docstrings that restate the test name; the parent change hit exactly this in `src/` and answered it with a reviewer rule (Q-15 there), but "restates the name" needs a test-side definition or the rule is unenforceable.
- **Context:** parent record INV-G: "No docstring that restates the signature ('Get the user.') may pass review; the unit of that check is the per-feature commit. No scripted checker is added." ruff has no filler detector that helps: `D419` (empty docstring) and `D402` (first line is the signature) report **0** today. Measured on `tests/`: the 313 undocumented functions are all pre-existing (2026-10-07: 313 of 727; today: 313 of 815), so the sweep is entirely mechanical prose.
- **Question:** state the test-side filler rule — must the docstring name the **behavior/observable outcome** (not the requirement ID alone, not the function name), is a bare `"AC-031:"` with no clause legal, and is the check a Phase 6 review item per commit (parent precedent) or something else?
- **Recommended:** **require an outcome clause and reject an ID-only docstring; enforce as a Phase 6 review check per commit group** — mirrors the parent's INV-G, and an ID-only docstring would add nothing over the test name (Q-09).
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-14 — Do the 15 documented tests whose docstring cites no ID get normalized?
- **Step:** P.2 Interrogate
- **Why needed:** a rule stated as "test docstrings name the requirement" makes those 15 (and any future ones) non-conforming, so the scope record must say whether the change edits them; they are the only existing docstrings the change would have to rewrite rather than add.
- **Context:** measured: 502 documented test functions, **487** start with an ID, **15** do not (e.g. `tests/acceptance/test_structure_map.py:243` `"""Top-level imported packages that are not standard library (REQ-001's dependency budget)."""` — ID present but not leading). Rewriting a **module** docstring would also change `STRUCTURE.md` for the 29 map-scoped files (Q-19).
- **Question:** are the 15 in scope (reword to the chosen prefix form), or explicitly left alone as "additions only, no rewrites of existing docstrings"?
- **Recommended:** **in scope for test functions, out of scope for module docstrings** — 15 one-line rewordings are cheap and make the convention uniform, while module docstrings of `conftest.py`/`*_test_helpers.py` are rendered into `STRUCTURE.md` and rewriting them mixes a map change into a docstring change.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-15 — Are existing module docstrings and the 209 documented modules frozen?
- **Step:** P.2 Interrogate
- **Why needed:** the TODO says "backfill the missing test docstrings", but `D205` (201 sites) mostly fires on docstrings that already exist, and the 29 map-scoped modules' docstring first lines are rendered verbatim into `STRUCTURE.md` — a rewrite there is a map change.
- **Context:** measured: **all 192 non-`__init__` modules under `tests/` already have a module docstring** (209 of 251 files documented counting `__init__.py`s). `make_map.py` renders `#### <path> (<N> lines)` plus the module docstring's first line (truncated at `_SUMMARY_LIMIT = 100` with `…`) for `conftest.py` and `*_test_helpers.py` only.
- **Question:** confirm the change **adds** docstrings and never rewrites an existing module docstring (including the 29 map-scoped ones), even where `D205` complains — or is prose improvement of existing module docstrings in scope?
- **Recommended:** **additions only** — it keeps `STRUCTURE.md` changes limited to line counts (Q-19), and prose rewrites of 209 documented modules is a different, unbounded task.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-16 — What is the no-behavior-delta proof for a 480-docstring diff over `tests/`?
- **Step:** P.2 Interrogate
- **Why needed:** the DOCS/CHORE gate is "confirm no behavior was touched", and with 100–147 test files edited the only honest answer is a mechanical comparison. The parent change's equivalent proof caused two logged Problem-Log entries (P-87, P-88), so the witness has to be specified before P.4, not improvised at Phase 5.
- **Context:** the parent used a **docstring-stripped AST digest** over `src/` (84 files, 43 587 nodes identical before/after; docstring hosts 628 → 859) plus a control run, and P-88 records that the control host had to be a **docstring-free** one or the digest legitimately changes. For `tests/` the natural witnesses are: `uv run pytest tests/ -q` identical counts (currently `1 failed, 815 passed, 1 skipped` — and Q-02 changes that number), `uv run pytest tests/ --collect-only -q` node-id list byte-identical (catches a test that stopped being collected), and the same AST digest over `tests/` (251 files). Note P-89 already warns that a hard-coded expected pass count goes stale when another change lands tests.
- **Question:** which proof is the gate — (a) docstring-stripped AST digest over `tests/` + a stated control run, (b) `--collect-only` node-id list byte-identical + full-suite counts identical modulo the Q-02 map fix, (c) both, or (d) full suite only?
- **Recommended:** **(c) both** — the digest proves no code node changed (the parent's precedent, with the control host named up front to avoid P-88), and the collect-only list proves no test was added, dropped or renamed, which the digest alone does not.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-17 — Does the new `tests/` gate need its own witness, or is `test_nfr_004` enough?
- **Step:** P.2 Interrogate
- **Why needed:** a gate that nothing asserts can silently disappear (a later change re-adds `"tests/*" = ["D"]` and nothing fails). The repo has a precedent for witnessing a tooling gate, and P-49/P-96 in the Problem Log are exactly this failure class.
- **Context:** `tests/acceptance/test_structure_map.py::test_nfr_004_mypy_and_ruff_clean` already runs `ruff check .` and `ruff format --check .` inside the suite, so it becomes the de-facto witness the moment the ignore line is removed. `test_nfr_005_complexipy_threshold_holds` goes further: it runs the real gate **and** a tripwire at limit 0 to prove the check is not vacuous. Nothing asserts on `per-file-ignores` content (measured: only `test_dependency_contract.py` and `test_structure_map.py` read `pyproject.toml`, for unrelated keys).
- **Question:** is a dedicated witness in scope — e.g. an acceptance test asserting `ruff check tests` reports 0 `D` violations, or one asserting `"tests/*"` is **not** in `per-file-ignores` — or does the change rely on `test_nfr_004` + `lint.yml` and add no test at all (which keeps it free of new tests, as a DOCS/CHORE normally is)?
- **Recommended:** **rely on `test_nfr_004` + `lint.yml`, add no test** — the acceptance test already fails if the gate regresses, and adding a config-shape assertion would be a new test with no requirement behind it (it would also need a traceability row and would break the "no new tests" shape of this change).
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-18 — Sequencing against `settings-public-registry-setter`: it edits the same `[tool.ruff.lint]` table and adds new tests
- **Step:** P.2 Interrogate
- **Why needed:** the two changes edit the same config block and the other one is mid-workflow, so the order decides who rebases and whether its new tests must carry docstrings.
- **Context:** `docs/todo/settings-public-registry-setter.md` is **IN-WORKFLOW** (CROSS-CUTTING, PR #73 merged 2026-10-09 per the merge log, branch still live on `origin`) and its DAG plans **T-008** = add `TID251` banned-api entries to `pyproject.toml` (the `[tool.ruff.lint]` region, lines 182–226 — the same table that holds `per-file-ignores` at 222–226) and **T-007** = a new file `tests/unit/architecture/test_singleton_slots.py`. `docs/questions/complexipy-scripts.md` records the same region: "`settings-public-registry-setter` (IN-WORKFLOW) edits `pyproject.toml` at `[tool.ruff.lint]` (192-226), not `[tool.complexipy]`".
- **Question:** does `docstrings-tests` wait for that change's branch/PR to merge (so the config edit and the new test file land on a settled base), or run in parallel and resolve the `pyproject.toml` conflict at rebase, and if parallel, must its new tests be written docstring-first?
- **Recommended:** **wait for it to merge first** — the conflict is in the exact lines this change deletes, the other change is already at Phase 3+, and this change has no dependency that would make waiting costly.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-19 — Should the gate land before the backlog changes that will add hundreds of new tests?
- **Step:** P.2 Interrogate
- **Why needed:** the value of the gate is largely prospective, and the measured fact is that the convention already holds without it (all 88 tests added since 2026-10-07 are documented). Whether it lands before `api-keys`/`backend-api`/`notifications` decides whether those changes write docstrings under a gate or by habit.
- **Context:** live backlog: `api-keys` (WAITING, FEATURE), `backend-api` (WAITING, CROSS-CUTTING), `notifications` (WAITING, FEATURE), `tenacity-rich-cachetools` (WAITING, FEATURE), `public-api-import-boundary` (PREPARING, REFACTOR — "Widen the regression guard: the `tests/unit/` boundary scan … plus ruff `TID251` banned-api entries"), `composition-root-factory` (PREPARING, REFACTOR). Measured growth: 727 → 815 test functions in three days, all documented; undocumented stayed at 313.
- **Question:** land the gate now (so every future test is gated, at the cost of a large diff that every later change rebases), or defer it until after the big test-adding features land (smaller total diff, but the convention stays unenforced through them), or gate now and backfill lazily per feature?
- **Recommended:** **gate now, backfill in the same change** — the 313-site backlog is not shrinking on its own (it has been constant for three days while the suite grew 12%), and a gate deferred past three feature PRs will be re-measured against a much larger `tests/`.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-20 — `STRUCTURE.md`: regenerate per commit or once, and does the 59-line NFR-002 headroom matter?
- **Step:** P.2 Interrogate
- **Why needed:** the change edits the only 29 test files the map renders, the pre-commit hook `structure-map-check` fires on every `.py` commit, and the map is 59 lines from its hard budget — so the commit plan is constrained by the map, not by the docstrings.
- **Context:** measured: `STRUCTURE.md` = **1941 lines**, NFR-002 budget **2000** (`_NFR_002_LINE_BUDGET = 2_000`, asserted in `tests/acceptance/test_structure_map.py`); the map renders `#### <path> (<N> lines)` for `conftest.py` and `*_test_helpers.py` under `tests/` (`_PACKAGES_DIRS = ("src","scripts","migrations")`), so **109** added docstring lines change those counts; plain `test_*.py` files appear in the tree by name only, and `__init__.py` files not at all. Module docstring first lines are rendered (truncated at 100 chars) — unchanged if Q-15's "additions only" holds. The check is a **pre-commit hook only** (`files: \.py$`), no CI job (ADR-085), and it is red on `main` today (Q-02).
- **Question:** regenerate `STRUCTURE.md` once (in the config/final commit) with the hook skipped in between, or regenerate it in **every** commit group (13-ish regenerations), and does the change also own a `docs/` file-count line refresh from Q-02 in the same regeneration?
- **Recommended:** **regenerate per commit group** — the hook cannot be skipped without `--no-verify` (which the git skill does not sanction), the regeneration is one command, and each commit then passes AC-021 on its own; fold the Q-02 `docs/` count refresh into the first regeneration.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-21 — What replaces the AGENTS.md sentence that says `tests/` is exempt?
- **Step:** P.2 Interrogate
- **Why needed:** AGENTS.md:747 states as a project convention that `tests/`, `scripts/`, `migrations/` and `.github/` are exempt from the `D` rules. After this change that sentence is false, and a false guideline is worse than none — every future step subagent reads it and writes an undocumented test.
- **Context:** the current bullet: "Docstrings are **Google style** and gated by ruff `D` over `src/` (`tests/`, `scripts/`, `migrations/`, `.github/` exempt via `per-file-ignores`); every public object in a backend package carries a docstring that states something its signature does not — filler that restates the signature ('Get the user.') is rejected in review." The parent change edited exactly this bullet (its record §4) and explicitly left the `python-best-practices` skill untouched (its Q-24).
- **Question:** what does the amended bullet say (which trees gated, which codes, the ID-prefix rule from Q-10, the filler rule from Q-13), and does the `python-best-practices` skill gain a test-docstring example or stay untouched as in the parent?
- **Recommended:** **one amended bullet, same shape**: `D` gated over `src/` and `tests/` with `scripts/`, `migrations/`, `.github/` still exempt (plus whatever codes Q-03 exempts inside `tests/`), and the test-side sentence stating the docstring form and the filler rule; leave the skill untouched for consistency with the parent's Q-24.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-22 — Does the change touch `docs/verification/traceability.md` and the verification record?
- **Step:** P.2 Interrogate
- **Why needed:** AGENTS.md says "an agent MUST NOT transition from `GREEN` to `VERIFIED` unless the traceability matrix is updated", but this change adds no test and changes no requirement, so there is nothing obvious to add — and the matrix's Status column is a dated historical record that must not be refreshed gratuitously.
- **Context:** measured: 881 rows / 136 spec IDs / 801 test functions, `check_traceability.py` PASS; decision **Q-129 (convention B)** — a row records the state as observed by the change that wrote it, a later change adds or updates rows **only** for the IDs it actually touches, and CI enforces referential integrity, never status freshness. The parent change did update the matrix (its S5.3) because it needed rows for the new gate; its Phase 6 review note N-1 records that the three record files were outside the declared scope heading.
- **Question:** does this change add matrix rows (e.g. a row for the `tests/` docstring gate) or explicitly record "no matrix change: no requirement or test added", and does the verification record list the record files as scope items the way the parent's N-1 note did?
- **Recommended:** **no matrix rows**, with the reason stated in `docs/verification/docstrings-tests.md` (no REQ/AC touched, no test added, referential integrity re-run as evidence), and declare the record files as "record files, not scope items" up front so the parent's N-1 note is not repeated.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-23 — Version bump and branch prefix
- **Step:** P.2 Interrogate
- **Why needed:** Phase 6 bumps by change type and the branch name is fixed at P.4; both are cheap to decide now and awkward to fix after the PR is open.
- **Context:** AGENTS.md bump mapping: DOCS/CHORE → **none**; the parent change's Q-27 kept the version untouched and its record lists `pyproject.toml` version as out of scope. Branch naming per AGENTS.md is `chore/<name>`; the merged log shows `chore/ruff-d-docstrings`, `chore/spec-interview-protocol`, `chore/security-changelog-license`, but the live `origin` has `issue/map-default-drop-shift` whose PR is titled `docs/map-default-drop-shift` — an inconsistency in practice.
- **Question:** confirm **no version bump**, and confirm the branch is `chore/docstrings-tests` (AGENTS.md + parent precedent) rather than `docs/docstrings-tests`?
- **Recommended:** **no bump, branch `chore/docstrings-tests`** — matches the bump table and the parent change's own branch.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-24 — Non-goals: confirm what this change must NOT do
- **Step:** P.2 Interrogate
- **Why needed:** the mandatory scope-boundary question. Every item below is a near-miss a later step could plausibly drift into, and each is cheap to exclude now and expensive to unwind after a PR.
- **Context:** measured sizes and owners: `scripts/*` has **3** `D` sites, `migrations/*` **11**, `.github/hooks/ruff-post-edit.py` **1–2** — all still `per-file-ignored`, and `scripts/` is the subject of `complexipy-scripts` (PREPARING). `src/` docstrings are done (parent, MERGED: 628 → 859 docstring hosts). `userdocs/api.md` publishes only `src/` packages, so test docstrings are never published. `mypy` settings are `disallow_untyped_defs` etc. with no docstring-related option; `mypy scripts/` and `mypy src/` are the gates. `pytest` `addopts = "-ra"` — no `--doctest-modules`, so a docstring is never executed. Coverage `source = ["src/backend","src/frontend"]`, `fail_under = 92` — test files are not measured.
- **Question:** confirm all of these are **out** of scope: any `src/` docstring change; `scripts/`, `migrations/`, `.github/hooks/` docstrings and their ignore lines; rewriting or quality-reviewing the 502 existing test docstrings beyond the 15 in Q-14; adding a scripted docstring/ID checker (Q-12); adding tests (Q-17); touching `docs/specs/`, `docs/decisions/`, the task DAG, `userdocs/`, the `python-best-practices` skill (beyond Q-21's AGENTS.md bullet), `pyproject.toml` version, ruff/pytest/mypy versions, coverage config, `--doctest-modules`, and `.gitattributes` (Q-02)?
- **Recommended:** **all out** — each is either owned by another change, would add behavior a DOCS/CHORE change may not introduce, or is the unbounded version of a bounded task.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-25 — One change or several, and what is the commit unit?
- **Step:** P.2 Interrogate
- **Why needed:** 480 sites across 100 files is the largest mechanical sweep in the repository's history (the parent's `src/` sweep was 41 files / 13 commits and produced two Problem-Log entries); the commit unit is also the unit of the no-filler review (Q-13), so it has to be chosen, not defaulted.
- **Context:** the parent grouped commits **by feature** (`docs(eventbus) …`, `docs(logging) …`, `docs(mail) …`, … 13 commits), each verified against that feature's test directory (`tests/{acceptance,unit,contract,integration,property}/<feature>`). `tests/` has no feature grouping at top level — it is grouped by **category** (acceptance/unit/property/contract/integration) and, inside each, by feature. Measured per-tree D1xx: acceptance 191, unit 123, top-level helpers/conftest 84, property 38, contract 26, integration 18.
- **Question:** one change with commits grouped by **category then feature** (≈ 10–15 commits, each verified by that subtree's tests and each with a map regeneration per Q-20), or one change with commits grouped by **feature across categories**, or split into several changes (e.g. `docstrings-tests-acceptance` first, then the rest)?
- **Recommended:** **one change, commits grouped by category then feature** — it matches the test-hierarchy vocabulary the rest of the repo uses, keeps each commit inside one test directory (so its verification command is one path), and splitting the change would need the config flip in whichever part lands first, which re-opens Q-03.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-26 — Is a `noqa` escape hatch allowed for a site where no honest docstring can be written?
- **Step:** P.2 Interrogate
- **Why needed:** with a hard gate over 480 sites, some sites will not admit a meaningful docstring; without a stated policy the step either invents filler (the TODO's named risk) or stalls on a gate it cannot pass.
- **Context:** the parent change faced the same shape in `src/` and its answer was the reviewer rule (Q-15 there) with no scripted exception mechanism; the repo does use targeted `noqa` elsewhere — the `settings-public-registry-setter` spec's EDGE-008 reasoning says "the ten inside-owner sites need no `noqa`" for `TID251`, so `noqa` is an established, deliberate mechanism. Measured candidates in `tests/`: 3 `D105` magic methods, 21 `D107` `__init__`s, 51 `D102` methods, and short generated/parametrized helpers in `tests/property/` (38 D1xx sites there).
- **Question:** are `# noqa: D103`-style inline exemptions permitted (and with what review bar — must each carry a reason comment?), is the answer instead "add the code to the `tests/*` ignore list" (Q-03/Q-06/Q-08), or is there no escape hatch at all?
- **Recommended:** **no inline `noqa`; exempt whole code families in the config instead** — a per-file ignore list is auditable in one place, whereas 20 scattered `noqa` comments re-create the inconsistency the change is removing and are invisible to the next reader of `pyproject.toml`.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Late questions (Phases 2–6)

<questions discovered after the change entered the workflow; same entry format, Step field set to the step that found it>
