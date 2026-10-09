# ruff-d-docstrings — Scope Record (DOCS/CHORE)

- **Change:** ruff-d-docstrings · **Type:** DOCS/CHORE (Phase 0 classified at P.1; re-stated here, not re-classified)
- **Branch / worktree:** `chore/ruff-d-docstrings` @ `45aa61c` (== `main` at P.4, 2026-10-08), worktree `../python-template_kopie-worktrees/chore/ruff-d-docstrings`
- **Version:** `1.0.0` (`pyproject.toml:4`) — **no bump** (Q-27; AGENTS.md Versioning: REFACTOR / DOCS-CHORE → none)
- **Phase Matrix for this type:** Phase 1 scope (this file, at P.4) · Phase 2/3 skipped · Phase 4 make the scoped non-behavior changes · Phase 5 light gate (lint/types where applicable + the Q-25 evidence set) · Phase 6 light review + PR. No spec, no spec PR.
- **Question file:** `docs/questions/ruff-d-docstrings.md` — Q-1 … Q-29, all `ANSWERED`; the binding decisions are summarized in `docs/todo/ruff-d-docstrings.md` §"P.3 decisions".
- **Date:** 2026-10-08

## Phase 0 — classification: DOCS/CHORE

First matching criterion (#5 in the Change Types table): the change **does not alter behavior** — it adds docstrings (documentation), edits `pyproject.toml` / `mkdocs.yml` / `.pre-commit-config.yaml` (configuration / tooling), and extends one `AGENTS.md` guidance line. No control flow, no public signature, no runtime path changes; §"No-behavior-delta proof plan" proves it rather than asserting it (Q-25).

Not **REFACTOR**: no existing code is restructured — the AST digest below shows the executable syntax tree is byte-identical before and after. Not **FEATURE/ISSUE**: nothing new is observable and nothing deviates from an approved spec.

**Escalation amendment (Q-26, supersedes the TODO's "stop and reclassify as ISSUE" line).** If writing a docstring reveals that a **behavior claim is wrong** (a docstring or comment asserting semantics the code does not implement), the procedure is: (1) record it as a **finding** in this file, (2) write the docstring that matches **the code as it is**, (3) open a **separate ISSUE TODO** (`docs/todo/<name>.md`, its own triage + RED/GREEN cycle). This change **stays DOCS/CHORE and finishes**; no mid-flight reclassification, no stranded per-feature commits.

## Fresh measurement (2026-10-08, this worktree, `ruff 0.16.10`, base commit `45aa61c`)

The TODO carries stale figures (see §Findings). Re-measured with `uv run ruff check --select D --statistics <tree>`, both bare and with the chosen convention:

| Tree | `--select D` (bare) | `--select D` + `convention = "google"` | Gated by this change |
|---|---|---|---|
| `src/` | 398 | **328** | **yes** |
| `tests/` | 827 | 743 | no — `per-file-ignores` (Q-3/Q-29 → sibling `docstrings-tests`) |
| `migrations/` | 11 | 7 | no — `per-file-ignores` (Q-23) |
| `scripts/` | 3 | 3 | no — `per-file-ignores` (Q-3) |
| `.github/` | 2 | 2 | no — `per-file-ignores` (Q-3) |
| repo-wide | 1 164 | 1 083 | — |

`src/` under the google convention (the set this change gates), by code:

```text
131  D102  undocumented-public-method        66  D205  missing-blank-line-after-summary
 57  D209  new-line-after-last-paragraph      51  D107  undocumented-public-init
 14  D101  undocumented-public-class           4  D403  first-word-uncapitalized
  3  D301  escape-sequence-in-docstring        2  D105  undocumented-magic-method
                                            ---  total 328   (D1xx missing-docstring family: 198)
```

Measured side effects of `convention = "google"` (ruff 0.16.10): `D401` (70 bare hits) is **not selected** — descriptive noun-phrase first lines stay (Q-10); `D400`/`D415`/`D203`/`D211`/`D212`/`D213` are not selected either, and the two "incompatible rule pair" warnings that bare `--select D` prints on stderr **disappear** with the convention set, so CI output stays clean.

`src/` files affected: **41** (nothing under `src/frontend/` and `src/main.py` — measured 0 `D` sites there):

| Feature (`src/backend/<f>/`) | Files | `D` total | `D1xx` (missing docstrings) |
|---|---|---|---|
| usermanagement | 7 | 70 | 47 |
| search | 4 | 61 | 6 |
| filemanagement | 6 | 58 | 37 |
| authentication | 7 | 51 | 50 |
| permissions | 6 | 45 | 33 |
| sessionmanagement | 3 | 16 | 2 |
| settings | 2 | 16 | 14 |
| mail | 4 | 6 | 6 |
| eventbus | 1 | 3 | 3 |
| logging | 1 | 2 | 0 |
| shared / frontend / `main.py` | 0 | 0 | 0 |
| **Total** | **41** | **328** | **198** |

Published surface (`userdocs/api.md` renders 8 packages): `permissions` (33 `D1xx`) and `search` (6) are documented but **not rendered** — `api.md` keeps its 8 packages (Q-20); that is a known gap, not an oversight.

## Exact change scope (file-level; nothing else is touched)

### 1. `pyproject.toml` (config commit, lands **last** — Q-7 a)

```toml
[tool.ruff.lint]
select = [
    # ... existing I, E, W, B, F, UP, RUF, PL, Q, SIM, C4, DTZ ...
    "D",  # pydocstyle — docstrings (google convention; src/ only, see per-file-ignores)
]

fixable = [
    # ... existing I, UP035, RUF022, Q000-Q004 ...
    "D204", "D207", "D208", "D209", "D211", "D212", "D403",  # docstring layout, always-fixable (Q-12)
]

[tool.ruff.lint.pydocstyle]
convention = "google"          # Q-1 / Q-2

[tool.ruff.lint.per-file-ignores]
"tests/*" = ["D"]              # Q-3 / Q-29 → sibling change docstrings-tests
"scripts/*" = ["D"]            # Q-3
"migrations/*" = ["D"]         # Q-23
".github/*" = ["D"]            # Q-3
```

Measured facts behind each entry:

- **`per-file-ignores` glob form.** Q-3's literal `tests/*` / `.github/*` work **as written**: `uv run ruff check --select D --per-file-ignores='.github/*:D' .github` → *All checks passed* (the 2 sites are in the nested `.github/hooks/`), and `--per-file-ignores='tests/*:D' tests` silences all 827 sites in nested test directories — ruff's per-file-ignores globs match across `/`. No `**` rewrite needed.
- **`fixable` widening (Q-12) — what it actually buys.** Measured with `--diff --fixable=D` on `src/`: `D209` (57 sites) and `D403` (4) have **safe** fixes (203 / 16 diff lines); `D301` (3) is fixable **only** with `--unsafe-fixes` (10 lines); `D205` (66) has **no fix available at all** — those 66 blank-line-after-summary sites are manual. So of the 130 format sites, 61 are mechanical, 3 need an explicit unsafe-fix run on the changed paths, 66 are hand edits. Of Q-12's seven named always-fixable codes, only `D209` and `D403` fire under the google convention today; the other five (`D204`, `D207`, `D208`, `D211`, `D212`) are listed for symmetry and report 0. `--fix` stays scoped to the step's changed paths, never repo-wide (AGENTS.md P-6).
- **No new dependency, no dependency version change.** `ruff>=0.16.10` (`pyproject.toml:62`) is untouched; only the pre-commit hook rev moves (item 3).

### 2. `mkdocs.yml` (same config commit — Q-18)

```yaml
plugins:
  - search
  - mkdocstrings:
      default_handler: python
      handlers:
        python:
          options:
            docstring_style: google
```

Measured: `mkdocstrings-python 2.0.8` (`uv.lock`) defines `PythonInputOptions.docstring_style: Literal["auto","google","numpy","sphinx"] | None = "google"` — the handler **already defaults to google**, so this is an explicit pin, not a rendering change: zero docs-output delta from this line. The delta comes from the docstrings themselves (blanks → text).

### 3. `.pre-commit-config.yaml` (same config commit — Q-28)

`rev: v0.15.12` → **`rev: v0.16.10`** on the `astral-sh/ruff-pre-commit` hook (one line, `.pre-commit-config.yaml:11`). Q-28's answer is "bump the hook rev **to match the dev pin**"; the number it quoted (`v0.16.9`) is stale — `pyproject.toml:62` is `ruff>=0.16.10` and `uv run ruff --version` → `0.16.10` (finding F-6). The hook runs `ruff-check --fix`, so with the widened `fixable` list the hook and CI must agree on the rule set and version. `pyproject.toml`'s `>=` pinning convention is unchanged (Q-28 c rejected).

### 4. `AGENTS.md` (config/guidance commit — Q-24)

Extend the single "Documentation" bullet in §"General Code & Style Conventions" (currently `AGENTS.md:743`) with the enforced convention and the no-filler rule, e.g.: docstrings are **Google style** and gated by ruff `D` over `src/` (`tests/`, `scripts/`, `migrations/`, `.github/` exempt via `per-file-ignores`); every public object in a backend package carries a docstring that states something its signature does not — filler that restates the signature ("Get the user.") is rejected in review. Prose only; no behavior, no CI change. The `python-best-practices` skill is **not** touched (Q-24).

### 5. `src/**/*.py` — docstrings and formatting (per-feature commits, item order below)

328 `D` sites in 41 files: **198 docstring additions** (`D102` 131, `D107` 51, `D101` 14, `D105` 2) and **130 format sites** (`D205` 66, `D209` 57, `D403` 4, `D301` 3) fixed in **separate commits** from the additions (Q-11). Content rules: all 51 `D107` `__init__` sites included, no `errors.py` exemption (Q-9); the two `D105` `EventBus.__enter__`/`__exit__` documented (Q-13); private helpers **in the touched files** documented too (Q-14 — review-checked, not gate-checked); `REQ-XXX`/`AC-XXX` IDs stay cited inside docstrings (Q-16); no docstring may restate the signature (Q-15).

### 6. Explicitly **not** touched

`userdocs/` (incl. `api.md` and its 8 packages — Q-20) · `tests/`, `scripts/`, `migrations/`, `.github/hooks/` docstrings and their gate (Q-29 → sibling `docstrings-tests`) · any test file, assertion or fixture · any spec, ADR or task DAG · type annotations (mypy strictness is `pyproject-tooling-gaps` follow-up work) · the `mkdocs-build` pre-push hook's `files:` filter (Q-19) · `pyproject.toml` version (Q-27) · the `python-best-practices` skill (Q-24).
## Commit plan (Q-5 a one change · Q-7 a docstrings first, config last · Q-11 format separate)

`ruff check .` is green on `main` today and stays green at **every** commit on the branch, because `select += "D"` is the last commit — before it, the new docstrings are simply un-gated additions.

| Order (easiest first) | Commits per feature | Sites |
|---|---|---|
| 1 | `eventbus` docstrings → `eventbus` format | 3 |
| 2 | `logging` format only (0 missing docstrings) | 2 |
| 3 | `mail` docstrings → format | 6 |
| 4 | `sessionmanagement` docstrings → format | 16 |
| 5 | `settings` docstrings → format | 16 |
| 6 | `permissions` docstrings → format | 45 |
| 7 | `authentication` docstrings → format | 51 |
| 8 | `filemanagement` docstrings → format | 58 |
| 9 | `search` docstrings → format | 61 |
| 10 | `usermanagement` docstrings → format | 70 |
| 11 | **config**: `pyproject.toml` + `mkdocs.yml` + `.pre-commit-config.yaml` + `AGENTS.md` | gate flips |

A feature with 0 format sites (or 0 `D1xx` sites) skips that half of the pair — the split is per feature, not a fixed 2×10.

## No-behavior-delta proof plan (Phase 5 — proven, not asserted; Q-25)

Baseline measured **now** at `45aa61c` in this worktree: `uv run ruff check .` → *All checks passed!*; `uv run ruff format --check .` → **339 files already formatted**; docstring-stripped AST digest of `src/` → **`64fc1d6ee758bf6ac572d58b100eff95d4bbd1205c993f7d9e2e126657d7bec0`** (identical in the primary worktree, so the digest is worktree-independent when run with the relative `src` root). The pytest and `mypy src/` baselines are recorded at **S4.1** before the first edit.

| Evidence | Command | Expected |
|---|---|---|
| Suite unchanged | `uv run pytest tests/ -q` (S4.1 baseline vs S5.1) | **identical counts**; no test added, changed, weakened or skipped |
| AC-009 invariant intact | `uv run pytest tests/acceptance/logging_coverage/test_docstrings.py::test_traced_class_docstrings_mention_tracing -v` | PASS (the only test in the suite that reads docstrings) |
| Lint green **with the new gate** | `uv run ruff check .` | clean — i.e. `D` selected over `src/` and 0 findings (== CI, `.github/workflows/lint.yml`) |
| Format gate green | `uv run ruff format --check .` | 0 files would be reformatted (baseline 339 already formatted) |
| Types unchanged | `uv run mypy src/` | same result as the S4.1 baseline |
| Published site still builds | `uv run --group docs mkdocs build --strict` | passes (the `mkdocs-build` pre-push hook does **not** fire on a `src/`-only change — Q-19) |
| **Executable code identical** | one-off AST digest check below, run at `45aa61c` and at the final commit | **identical digest** `64fc1d6e…` |
| Worktree clean | `git status --porcelain` | empty (S7.1 removes the worktree without `--force`) |

The AST check (throwaway script, **not** added to `scripts/` — Q-25). It removes every docstring statement and the `docstring` attribute, then hashes the dump:

```python
"""One-off no-behavior-delta check (Q-25): hash each src file's AST with every
docstring removed, so a docstring-only diff hashes identically."""
import ast, hashlib, sys
from pathlib import Path

DOC_HOSTS = (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)

def is_doc(node: ast.AST) -> bool:
    return isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str)

def strip(node: ast.AST) -> None:
    if isinstance(node, DOC_HOSTS):
        node.docstring = None
        body = getattr(node, "body", [])
        if body and is_doc(body[0]):
            body.pop(0)
            if not body:
                body.append(ast.Pass())
    for child in ast.iter_child_nodes(node):
        strip(child)

def digest(root: Path) -> str:
    h = hashlib.sha256()
    for p in sorted(root.rglob("*.py")):
        tree = ast.parse(p.read_text(encoding="utf-8"), filename=str(p))
        strip(tree)
        h.update(p.as_posix().encode())
        h.update(ast.dump(tree).encode())
    return h.hexdigest()

if __name__ == "__main__":
    print(digest(Path(sys.argv[1] if len(sys.argv) > 1 else "src")))
```

Control run (2026-10-08, this worktree — the check is sensitive to code and blind to docstrings):

```text
before (copy of src)          : 461499a8902c944e…
+ docstring on EventBus.__enter__ : 461499a8902c944e…   SAME   (digest ignores the docstring)
+ max_queue_size 1000 → 1001      : fc5635607e934ee3…   DIFFERENT (digest catches a code change)
```

Run it with the **relative** `src` root in each worktree (the digest includes the file paths, so an absolute root would make the two sides incomparable). **Control-run rule (amended at S5.4, Problem Log P-88):** the docstring mutation MUST target a host that has **no** docstring (e.g. `EventBus.__enter__`) — the script strips only the *first* docstring `Expr` of a host, so adding a second string constant to a host that already has a docstring legitimately changes the digest and looks like a false failure — and the run MUST state **both** expectations: SAME for the added docstring, DIFFERENT for the one-character code change.

## Invariants that MUST hold

- **INV-A (traced wording, logging-coverage REQ-009 / AC-009).** No `@logged_class` class docstring may lose the "traced" + "logged" wording. Measured: **41** classes in `src/` carry `@logged_class` (all 41 already have a docstring); the AC-009 test asserts the wording for the **19** classes in `INVENTORY_CLASSES` (`tests/logging_coverage_test_helpers.py:53`). Phase 5 re-runs `test_traced_class_docstrings_mention_tracing`. (The TODO's "45" is stale — finding F-3.)
- **INV-B (no test touched).** No test file is added, removed, weakened or converted; the diff touches no file under `tests/`.
- **INV-C (no escape hatches).** No `# noqa` anywhere, and `per-file-ignores` gains **exactly** the four trees decided in Q-3/Q-23/Q-29 — never a per-file exemption for a real gap in `src/`.
- **INV-D (executable code identical).** Proven by the AST digest, not by review.
- **INV-E (no version bump)** — `pyproject.toml:4` and `[tool.bumpversion] current_version` stay at `1.0.0` (Q-27).
- **INV-F (no new dependency, no dependency-range change)** — only the pre-commit hook rev moves.
- **INV-G (no-filler rule, Q-15).** No docstring that restates the signature ("Get the user.") may pass review; the unit of that check is the per-feature commit. No scripted checker is added (Q-15 b rejected) — this is a **Phase 6 review checklist item**.
- **INV-H (private helpers in touched files documented, Q-14).** Beyond what `ruff check --select D src` can prove; verified by review in Phase 6, not by the gate.
- **INV-I (spec IDs stay cited, Q-16).** `REQ-XXX`/`AC-XXX` references inside docstrings are kept.
- **INV-J (feature boundaries / architecture rules unchanged).** No file moves, no new import, no cross-feature internal import — the diff is docstrings inside existing files plus config.

## Phase 5 gate list (DOCS/CHORE light gate) and acceptance signal

Gate = the table in §"No-behavior-delta proof plan" (full suite unchanged, `ruff check .` clean **with `D` selected over `src/`**, `ruff format --check .` clean, `mypy src/` unchanged, `mkdocs build --strict` passes, AST digest identical, INV-A test re-run green) + INV-B/C/E/F verified against the final diff.

**Acceptance signal (plain language, from the TODO):** `uv run ruff check .` is green with `D` selected over `src/`; every public object in the backend packages has a docstring that says something its signature does not; `userdocs/api.md` renders real text instead of blanks; `mkdocs build --strict` still passes; the full test suite and `mypy src/` are unchanged.

## Findings (recorded at P.4 — the Problem-Log item the P.2 log owed here)

| # | Finding | Measured truth (2026-10-08, `ruff 0.16.10`, `45aa61c`) |
|---|---|---|
| F-1 | `docs/todo/ruff-d-docstrings.md` §Why still carries "`uv run ruff check --select D src` → **379 errors**" (2026-10-04) | `src/` = **398** bare, **328** under the chosen google convention. The 386 figure from P.2 (`305add3`) is also superseded — `structlog-logging` merged since then |
| F-2 | The `pyproject-tooling-gaps` claim "**156 of 515 public defs** lack a docstring" is **not reproducible** under any `D` rule | The `src/` missing-docstring family is **198** (`D102` 131, `D107` 51, `D101` 14, `D105` 2); no `D` code reports "public defs" |
| F-3 | TODO/Q-17 say "**45** `@logged_class` classes" | **41** decorated classes in `src/` (AST count), all of them already documented; the AC-009 test asserts the wording for **19** of them |
| F-4 | TODO per-feature `D1xx` split (authentication 50, usermanagement 45, filemanagement 37, permissions 32, settings 14, mail 6, search 6, eventbus 3, sessionmanagement 2) | usermanagement **47**, permissions **33**; the rest unchanged. Phase 4 uses the fresh table in §Fresh measurement |
| F-5 | TODO/Q-11 call it "the **123** `src/` format sites (`D205` 66, `D209` 57, `D301` 3, `D403` 4)" | Those four codes sum to **130**, and only 61 are auto-fixable (`D209` 57 + `D403` 4 safe; `D301` 3 unsafe-only); `D205` (66) has **no fix at all** |
| F-6 | Q-28's answer pins the pre-commit hook to "**v0.16.9**" | The dev pin is `ruff>=0.16.10` and the installed ruff is **0.16.10**; Q-28's stated intent ("match the dev pin") resolves to `rev: v0.16.10`. A scope detail, not a user block |
| F-7 | P.2 recorded `tests/` = 762 `D` sites (input for the sibling change) | **827** bare / **743** under google. Out of scope here — `docstrings-tests` must re-measure at its own P.4 |
| F-8 | Q-18 reads as if `docstring_style: google` changes rendering | `mkdocstrings-python 2.0.8` already defaults to `google` — the pin is explicit but inert; the rendering delta comes from the docstrings themselves |
| F-9 | `uv.lock` on `main` is **stale**: it records `python-template 0.6.1` while `pyproject.toml:4` says `1.0.0` (the `structlog-logging` bump never re-locked) | Any `uv run` in a fresh worktree rewrites `uv.lock` (1-line diff), so the change worktree cannot stay `git status`-clean without a decision. **Recommendation for the orchestrator:** fold the one-line `uv.lock` refresh into this change's config commit (non-behavioral, forced by the tooling), or open a separate one-line chore TODO. Not decided in P.3; reverted here so the scope record stands alone |

None of F-1 … F-9 changes what this change does: every figure is a count, and the one version number (F-6) follows its answer's own stated intent. **No item in the P.3 decision set alters externally observable behavior**, so the DOCS/CHORE classification stands and no `BLOCKED-USER` question is raised.

## Phase 4 — S4.1 baseline (2026-10-09)

Measured in this worktree at `8ec2edf` (P.4 scope record; `src/` byte-identical to `45aa61c` — **no implementation file edited yet**, by design). DOCS/CHORE has no RED gate; this section is the GREEN baseline Phase 5 (S5.1/S5.2) must reproduce. Toolchain at measurement: `ruff 0.16.10`, `mypy 2.4.0`, `Python 3.14.5`.

### Gate baselines (what Phase 5 compares against)

| Evidence | Command | S4.1 baseline (2026-10-09) |
|---|---|---|
| Suite unchanged | `uv run pytest tests/ -q` | **`1 failed, 760 passed, 1 skipped in 236.60s (0:03:56)`** — the single failure is the pre-existing timing flake in §Baseline flake; skip = `SKIPPED [1] tests\acceptance\filemanagement\test_filemanagement.py:364: symlinks not available on this host` |
| Types unchanged | `uv run mypy src/` | **`Success: no issues found in 84 source files`** |
| Lint as the gate stands today (`D` not yet selected) | `uv run ruff check .` | **`All checks passed!`** (exit 0) |
| Format gate | `uv run ruff format --check .` | **`339 files already formatted`** (exit 0) |
| Executable code identical | AST digest, §method below | **`64fc1d6ee758bf6ac572d58b100eff95d4bbd1205c993f7d9e2e126657d7bec0`** — **MATCHES** the P.4 baseline; run twice, identical output |

### AST digest reproduction (§method)

The throwaway script is the one embedded verbatim in §No-behavior-delta proof plan — copied unchanged to a path **outside** the repo (`%LOCALAPPDATA%/Temp/s41_ast_digest.py`), never added to `scripts/` (Q-25). Run in this worktree with the **relative** `src` root:

```text
uv run python "$LOCALAPPDATA/Temp/s41_ast_digest.py" src
→ 64fc1d6ee758bf6ac572d58b100eff95d4bbd1205c993f7d9e2e126657d7bec0   (run 1)
→ 64fc1d6ee758bf6ac572d58b100eff95d4bbd1205c993f7d9e2e126657d7bec0   (run 2, stability check)
```

Phase 5 re-runs the same command at the final commit and requires the same digest (INV-D).

### Baseline flake (pre-existing; recorded so Phase 5 does not misread it)

`tests/contract/search/test_search_contracts.py::test_nfr_001_performance_budgets` failed in the full-suite run:
`assert statistics.median(query_samples) < 0.3` → `0.30619730008766055 < 0.3` (NFR-001 local budget, 2% over, 10k-item SQLite source under the load of a 762-test run).

- Isolated re-run at the same commit: **`1 passed in 8.44s`** → timing/load flake, not a defect and not caused by this change (no `src/` file edited at S4.1; INV-D keeps the code identical to `main`).
- Same class as the history: `docs/workflow/PROBLEMS.md` **P-36** (the NFR-001 budget is tight against the current query path) and the flaky-failure classifications in `docs/verification/search.md` §S5.1.
- **Consequence for the Phase 5 gate:** "identical counts" is not reproducible for this one test. If S5.1 shows exactly this failure, re-run it in isolation; pass ⇒ classify as the known flake and record it, exactly as `search.md` did. Any *other* delta from `1 failed, 760 passed, 1 skipped` is a regression. → Problem Log **P-73**.

### Per-feature `D`-site work list (the gated set: `D` over `src/`, `convention = "google"`)

Measured **without** editing `pyproject.toml` — one run per group, the convention supplied inline so the numbers are what the gate will see once `select += "D"` lands (group 11):

```text
uv run ruff check src/backend/<group> --select D --output-format=concise \
  --config 'lint.pydocstyle.convention = "google"'
```

The inline `--config` also suppresses the two incompatible-rule warnings that bare `--select D` prints (as §Fresh measurement predicts), so the counts are directly comparable to the gate.

| Commit order | Group | Files | `D` total | `D1xx` additions | format (`D205`/`D209`/`D403`/`D301`) | codes |
|---|---|---|---|---|---|---|
| 1 | eventbus | 1 | 3 | 3 | 0 | `D105`:2 `D107`:1 |
| 2 | logging | 1 | 2 | 0 | 2 | `D205`:1 `D209`:1 |
| 3 | mail | 4 | 6 | 6 | 0 | `D107`:5 `D102`:1 |
| 4 | sessionmanagement | 3 | 16 | 2 | 14 | `D205`:7 `D209`:6 `D403`:1 `D102`:1 `D107`:1 |
| 5 | settings | 2 | 16 | 14 | 2 | `D102`:10 `D107`:4 `D205`:1 `D301`:1 |
| 6 | permissions | 6 | 45 | 33 | 12 | `D102`:22 `D107`:11 `D205`:5 `D209`:5 `D301`:2 |
| 7 | authentication | 7 | 51 | 50 | 1 | `D102`:36 `D101`:7 `D107`:7 `D205`:1 |
| 8 | filemanagement | 6 | 58 | 37 | 21 | `D102`:27 `D205`:11 `D107`:10 `D209`:9 `D403`:1 |
| 9 | search | 4 | 61 | 6 | 55 | `D205`:28 `D209`:26 `D107`:5 `D102`:1 `D403`:1 |
| 10 | usermanagement | 7 | 70 | 47 | 23 | `D102`:33 `D205`:12 `D209`:10 `D101`:7 `D107`:7 `D403`:1 |
| 11 | config (`pyproject.toml` + `mkdocs.yml` + `.pre-commit-config.yaml` + `AGENTS.md`) | 4 | 0 | 0 | 0 | gate flips |
| — | **Total (`src/`)** | **41** | **328** | **198** | **130** | `D102` 131 · `D205` 66 · `D209` 57 · `D107` 51 · `D101` 14 · `D403` 4 · `D301` 3 · `D105` 2 |

Cross-check: the ten group runs sum to **328 findings in 41 files**, and `uv run ruff check src --select D --statistics --config 'lint.pydocstyle.convention = "google"'` reports the same per-code totals; `src/main.py` + `src/frontend/` → **0** sites. The §Fresh measurement table (measured at `45aa61c`) **holds at `8ec2edf`** — no figure needed correcting in this step.

Mechanical vs manual split per group (derived from the code counts, per §Exact change scope item 1): `D209` + `D403` have safe fixes (61 repo-wide), `D301` (3: settings 1, permissions 2) needs an explicit `--unsafe-fixes` run on the changed paths, `D205` (66) has **no** fix and is hand-edited. Groups 1 and 3 have no format half; group 2 has no `D1xx` half — the pair collapses per feature as the commit plan says.

File-level work list (per group, `D` = total sites, `D1xx` = additions, `fmt` = format sites):

```text
eventbus
  src/backend/eventbus/eventbus.py                        D=3  D1xx=3  fmt=0   [D105x2 D107x1]
logging
  src/backend/logging/_decorator.py                       D=2  D1xx=0  fmt=2   [D205x1 D209x1]
mail
  src/backend/mail/errors.py                              D=3  D1xx=3  fmt=0   [D107x3]
  src/backend/mail/models.py                              D=1  D1xx=1  fmt=0   [D102x1]
  src/backend/mail/service.py                             D=1  D1xx=1  fmt=0   [D107x1]
  src/backend/mail/transport.py                           D=1  D1xx=1  fmt=0   [D107x1]
sessionmanagement
  src/backend/sessionmanagement/events.py                 D=1  D1xx=1  fmt=0   [D102x1]
  src/backend/sessionmanagement/search_source.py          D=12 D1xx=0  fmt=12  [D205x6 D209x5 D403x1]
  src/backend/sessionmanagement/service.py                D=3  D1xx=1  fmt=2   [D107x1 D205x1 D209x1]
settings
  src/backend/settings/registry.py                        D=2  D1xx=1  fmt=1   [D107x1 D205x1]
  src/backend/settings/repository.py                      D=14 D1xx=13 fmt=1   [D102x10 D107x3 D301x1]
permissions
  src/backend/permissions/catalog.py                      D=3  D1xx=1  fmt=2   [D301x2 D107x1]
  src/backend/permissions/errors.py                       D=6  D1xx=6  fmt=0   [D107x6]
  src/backend/permissions/events.py                       D=1  D1xx=1  fmt=0   [D102x1]
  src/backend/permissions/models.py                       D=3  D1xx=1  fmt=2   [D102x1 D205x1 D209x1]
  src/backend/permissions/repositories.py                 D=27 D1xx=23 fmt=4   [D102x20 D107x3 D205x2 D209x2]
  src/backend/permissions/service.py                      D=5  D1xx=1  fmt=4   [D205x2 D209x2 D107x1]
authentication
  src/backend/authentication/errors.py                    D=1  D1xx=1  fmt=0   [D107x1]
  src/backend/authentication/events.py                    D=7  D1xx=7  fmt=0   [D101x7]
  src/backend/authentication/repositories.py              D=1  D1xx=0  fmt=1   [D205x1]
  src/backend/authentication/repository.py                D=21 D1xx=21 fmt=0   [D102x18 D107x3]
  src/backend/authentication/service.py                   D=12 D1xx=12 fmt=0   [D102x11 D107x1]
  src/backend/authentication/tracker.py                   D=4  D1xx=4  fmt=0   [D102x3 D107x1]
  src/backend/authentication/webauthn.py                  D=5  D1xx=5  fmt=0   [D102x4 D107x1]
filemanagement
  src/backend/filemanagement/errors.py                    D=6  D1xx=6  fmt=0   [D107x6]
  src/backend/filemanagement/events.py                    D=1  D1xx=1  fmt=0   [D102x1]
  src/backend/filemanagement/repository.py                D=21 D1xx=17 fmt=4   [D102x16 D107x1 D205x2 D209x2]
  src/backend/filemanagement/search_source.py             D=12 D1xx=0  fmt=12  [D205x6 D209x5 D403x1]
  src/backend/filemanagement/service.py                   D=6  D1xx=1  fmt=5   [D107x1 D205x3 D209x2]
  src/backend/filemanagement/storage.py                   D=12 D1xx=12 fmt=0   [D102x10 D107x2]
search
  src/backend/search/errors.py                            D=5  D1xx=3  fmt=2   [D107x3 D205x1 D209x1]
  src/backend/search/events.py                            D=3  D1xx=1  fmt=2   [D102x1 D205x1 D209x1]
  src/backend/search/models.py                            D=14 D1xx=0  fmt=14  [D205x7 D209x7]
  src/backend/search/service.py                           D=39 D1xx=2  fmt=37  [D205x19 D209x17 D107x2 D403x1]
usermanagement
  src/backend/usermanagement/errors.py                    D=4  D1xx=4  fmt=0   [D107x4]
  src/backend/usermanagement/events.py                    D=8  D1xx=8  fmt=0   [D101x7 D102x1]
  src/backend/usermanagement/models.py                    D=2  D1xx=2  fmt=0   [D102x2]
  src/backend/usermanagement/repository.py                D=19 D1xx=15 fmt=4   [D102x14 D205x2 D209x2 D107x1]
  src/backend/usermanagement/role_store.py                D=3  D1xx=3  fmt=0   [D102x2 D107x1]
  src/backend/usermanagement/search_source.py             D=12 D1xx=0  fmt=12  [D205x6 D209x5 D403x1]
  src/backend/usermanagement/service.py                   D=22 D1xx=15 fmt=7   [D102x14 D205x4 D209x3 D107x1]
```

### S4.1 exit state

Nothing edited: `git status --porcelain` showed only `M uv.lock` (finding F-9 — rewritten by every `uv run`), restored before this commit and never staged. `src/`, `pyproject.toml`, `mkdocs.yml`, `.pre-commit-config.yaml`, `AGENTS.md` untouched.

**Next (S4.2, group 1):** `eventbus` docstrings — 3 sites in 1 file (`src/backend/eventbus/eventbus.py`: `D105`×2 `__enter__`/`__exit__` per Q-13, `D107`×1), no format half (0 format sites → the pair collapses to one commit).

## Phase 4 — groups 1-3 (S4.2, 2026-10-09)

Three commit-plan groups done, one commit each (groups 1 and 3 have no format half, group 2 has no `D1xx` half — the pair collapses per feature as §Commit plan says). Every `uv run` rewrote `uv.lock` (F-9); it was `git restore`d before each commit and never staged.

| Group | Commit | Sites fixed | `ruff check src/backend/<group>` | `--select D` (google) after | Feature tests (`-q`) |
|---|---|---|---|---|---|
| 1 `eventbus` | `1560bfc` `docs(eventbus): add missing docstrings (D105 x2, D107 x1)` | 3 additions | All checks passed! | **0** | `tests/{acceptance,unit,contract,integration,property}/eventbus` → **31 passed** |
| 2 `logging` | `a7894c8` `docs(logging): fix docstring formatting (D205, D209)` | 2 format | All checks passed! | **0** | `tests/acceptance/logging tests/acceptance/logging_coverage` → **33 passed**; AC-009 `test_traced_class_docstrings_mention_tracing` → **1 passed** (INV-A) |
| 3 `mail` | `b96ad16` `docs(mail): add missing docstrings (D107 x5, D102 x1)` | 6 additions | All checks passed! | **0** | `tests/{acceptance,unit,contract,integration,property}/mail` → **40 passed** |

### Sites, as edited

```text
eventbus  src/backend/eventbus/eventbus.py
  47  D107 EventBus.__init__              added (queue bound; None → live eventbus.max_queue_size
                                          setting else 1000, AC-017/AC-018; worker starts lazily)
  168 D105 EventBus.__enter__             added (returns the bus; still no worker thread)   [Q-13]
  171 D105 EventBus.__exit__              added (drains then stops; exception args ignored ⇒ never suppresses)  [Q-13]
logging   src/backend/logging/_decorator.py
  77  D205 + D209 _is_private_method      summary line split from the description; closing """ on its own line
mail      src/backend/mail/errors.py
  23  D107 MailConfigurationError.__init__   added
  37  D107 MailTransportError.__init__       added
  52  D107 MailTemplateError.__init__        added
mail      src/backend/mail/models.py
  52  D102 EventPublisher.publish          added (abstract one-liner → docstring + `...`)
mail      src/backend/mail/service.py
  42  D107 MailService.__init__           added (the three optional seams; AC-031 citation kept)
mail      src/backend/mail/transport.py
  44  D107 SmtpTransportImpl.__init__     added (no connection at construction; auth only when username non-empty)
```

Private helpers in all six touched files already carried docstrings (`_handler_name`, `_ensure_worker_unlocked`, `_worker_loop`, `_dispatch`, `_get_transport`, `_publish`) — INV-H needs no additions here. No filler docstring was written (INV-G): each states a fact the signature does not (resolution order, laziness, exception semantics, seam defaults). No `REQ-`/`AC-` citation was removed (INV-I); `AC-017/AC-018`, `AC-031`, `NFR-002` stay cited.

### No-behavior-delta (INV-D)

The throwaway script of §No-behavior-delta proof plan — byte-identical to the embedded block (verified by extracting the fenced block and comparing) — was re-used at `%LOCALAPPDATA%/Temp/s41_ast_digest.py`, never added to `scripts/` (Q-25):

```text
uv run python "$LOCALAPPDATA/Temp/s41_ast_digest.py" src
→ 64fc1d6ee758bf6ac572d58b100eff95d4bbd1205c993f7d9e2e126657d7bec0   (run 1)
→ 64fc1d6ee758bf6ac572d58b100eff95d4bbd1205c993f7d9e2e126657d7bec0   (run 2)
```

**MATCHES** the S4.1/P.4 baseline — the executable code in `src/` is unchanged. `git diff --stat 84b25bd..b96ad16` = 6 files, +41/−3, all inside docstrings (the 3 deletions are the reformatted `_is_private_method` summary line and the `EventPublisher.publish` one-liner). `ruff format src/backend/{eventbus,logging,mail}` → "files left unchanged" in all three groups.

### Q-26 check (docstring vs. code)

No docstring was written that contradicts the code, so no finding under the binding amendment. One observation for the record (not a finding, no action taken): `MailService._publish` does **not** catch a publisher exception, so a failing publisher propagates out of `send_email` — unlike user-management/authentication/file-management, whose `AGENTS.md` entries promise "a publisher failure never breaks the operation". The mail spec (REQ-012, D9) makes no such promise, and the new `EventPublisher.publish` docstring states the actual behavior ("does not catch a publisher exception, so a failing publisher surfaces to the caller"). If isolation is intended for mail, that is a separate ISSUE/FEATURE, not this change.

**Next (S4.2, groups 4-5):** `sessionmanagement` (16 sites: 2 additions + 14 format) → `settings` (16 sites: 14 additions + 2 format, incl. 1 `D301` needing `--unsafe-fixes`).

## Phase 4 — groups 4-5 (S4.2, 2026-10-09)

Groups 4 (`sessionmanagement`) and 5 (`settings`) done, **two commits each** — additions half then format half (Q-11). `uv.lock` was rewritten by every `uv run` (F-9), `git restore`d before each commit, never staged.

| Group | Commit | Sites | `ruff check src/backend/<group>` | `--select D` (google) after | Feature tests (`-q`) |
|---|---|---|---|---|---|
| 4 `sessionmanagement` additions | `e3f95c6` `docs(sessionmanagement): add missing docstrings (D102 x1, D107 x1)` | 2 additions | All checks passed! | 14 (format half pending) | — |
| 4 `sessionmanagement` format | `df45d17` `docs(sessionmanagement): fix docstring formatting (D205, D209, D403)` | 14 format | All checks passed! | **0** | `tests/{acceptance,contract,integration,property,unit}/sessionmanagement` → **69 passed** |
| 5 `settings` additions | `899c027` `docs(settings): add missing docstrings (D102 x10, D107 x4)` | 14 additions | All checks passed! | 2 (format half pending) | — |
| 5 `settings` format | `2284b71` `docs(settings): fix docstring formatting (D205, D301)` | 2 format | All checks passed! | **0** | `tests/{acceptance,contract,integration,property,unit}/settings{,_coverage}` → **103 passed** |

### Sites, as edited

```text
sessionmanagement  src/backend/sessionmanagement/events.py
  55  D102 EventPublisher.publish          added (synchronous fire-and-forget; the bus only
                                          enqueues; a publisher exception is NOT caught ⇒
                                          propagates, REQ-018). The stub body `...` is kept
                                          after the docstring — see INV-D below.
sessionmanagement  src/backend/sessionmanagement/service.py
  69  D107 SessionService.__init__        added (construction is the only wiring point: cap
                                          eviction on the *shared* bus, user-lifecycle
                                          revocation on the *injected* one and only if it has
                                          `subscribe`; None permission_service = standalone,
                                          AC-031; REQ-014/REQ-015/AC-038)
```

Format half, group 4 — 14 findings over 8 docstrings, **all hand-edited**: `--fix` and `--diff` offered **no** fix for the 6 `D209` and the 1 `D403` here. Probed on isolated single-code docstrings in `%TEMP%` (ruff 0.16.10): `D209 --fix`/`--diff` and `D403 --fix` produce **nothing** — neither code has a fixer in this version — so §"Mechanical vs manual split"'s "`D209` + `D403` have safe fixes (61 repo-wide)" does **not** hold; all 61 are hand-edits. Recorded here as finding **F-10** (the §Findings table stops at P.4); Phase 5/6 should re-measure the remaining groups' mechanical share.

```text
sessionmanagement  src/backend/sessionmanagement/search_source.py
  95  D205+D209 _free_text_matches        summary line + blank line + closing """ own line
  105 D205+D209 _eval_group               idem
  115 D205+D209 _eval_condition           idem
  143 D403      _apply_exact_operator     `boolean` → `Boolean` (first word capitalized)
  153 D205+D209 _sort_key                 idem
  163 D205+D209 _query                    idem
  189 D205      build_session_source      blank line after the summary (closing """ already ok)
sessionmanagement  src/backend/sessionmanagement/service.py
  217 D205+D209 _order_with_current       summary line split; closing """ own line
```

```text
settings  src/backend/settings/registry.py
  59  D107 SettingsRegistry.__init__      added (seam defaults incl. the lazy eventbus import that
                                          breaks the circular import; persisted values loaded once
                                          and override defaults, REQ-009/REQ-011 of
                                          settings-coverage; None permission_service = standalone,
                                          AC-031)
settings  src/backend/settings/repository.py
  131 D107 YamlValueRepository.__init__   added (single values.yaml, dir created eagerly, lock is
                                          per-instance not cross-process)
  139 D102 .save                          added (temp file + os.replace ⇒ never a partial file)
  147 D102 .load                          added (missing file is not an error; corrupted file →
                                          ValueStorageError, EDGE-003)
  202 D107 MemoryTemplateRepository.__init__ added (nothing loaded, nothing persisted)
  206 D102 .save                          added (silent replace; the frozen instance itself is kept)
  210 D102 .get                           added
  214 D102 .delete                        added (unknown name = silent no-op)
  218 D102 .list                          added (name-ordered, not insertion-ordered)
  233 D107 YamlTemplateRepository.__init__ added (one file per template, dir created eagerly)
  241 D102 .save                          added (.<name>.yaml.tmp sibling, atomic, REQ-022)
  255 D102 .get                           added (name selects the file only; fields come from the
                                          file; corrupted/incomplete → TemplateStorageError, AC-032)
  272 D102 .delete                        added (absent file = silent no-op)
  278 D102 .list                          added (one corrupted file fails the whole listing, AC-032)
```

Q-14 / INV-H additions in the touched files (not gate-detected — `D` under the google convention ignores private defs; found with a one-off `ast` walk): `registry.py` `_require_definition`, `_scope_keys`, `_publish_setting_changed`, `_persist_values`; `repository.py` `_path` ×2, `_parse` ×2. Every other private helper in the five touched files already had a docstring.

Format half, group 5:

```text
settings  src/backend/settings/registry.py
  1   D205 module docstring               summary line split from the description (hand-edited)
settings  src/backend/settings/repository.py
  49  D301 _str_representer              `r"""` prefix + `\\x85` → `\x85`, so the docstring VALUE is
                                          byte-identical (verified: ast.get_docstring of the
                                          function is equal before and after). `--unsafe-fixes`
                                          was deliberately NOT used: it only adds the `r` prefix,
                                          which would have doubled the backslash in the rendered
                                          docstring (a needless content change).
```

### Gates & no-behavior-delta (INV-D)

```text
uv run ruff check src/backend/sessionmanagement src/backend/settings --select D \
  --config 'lint.pydocstyle.convention = "google"'      → All checks passed!   (0)
uv run ruff check .                                     → All checks passed!
uv run ruff format --check src/backend/sessionmanagement src/backend/settings → 13 files already formatted
uv run python "$LOCALAPPDATA/Temp/s41_ast_digest.py" src → 64fc1d6ee758bf6ac572d58b100eff95d4bbd1205c993f7d9e2e126657d7bec0   (twice)
git diff --stat 70f68b2..HEAD                           → 5 files, +150/−26, all inside docstrings
```

**Digest near-miss, caught and fixed inside this execution.** The group-4 additions commit first replaced the protocol stub body `def publish(...) -> None: ...` with the docstring alone; the digest then printed `0736d32b…` — the strip script replaces an emptied body with `Pass`, so dropping the `Expr(Ellipsis)` **is** an AST delta. Fixed by keeping `...` after the docstring (the pattern group 3 used for `mail/models.py:52`), digest back to `64fc1d6e…`, and the one-line fix folded into `e3f95c6` with `git commit --fixup` + `--autosquash` (the branch was never pushed, so no history was rewritten for anyone else). The digest is what caught it — INV-D earned its keep.

### Q-26 check (docstring vs. code)

No docstring contradicts the code; each of the following is stated **as the code is**, with no code change and no reclassification:

- `sessionmanagement.events.EventPublisher.publish` — the feature does not catch a publisher exception, so a failing publisher propagates to the calling session method. The session-management spec (REQ-018) makes no isolation promise, so this is not a defect; it is the same observation already recorded for mail.
- `settings.repository.YamlTemplateRepository.get` — the requested name only selects the file; the returned template's fields come from the file, so a file whose `name` field disagrees with its stem is returned unchanged (no cross-check exists).
- `settings.repository.YamlTemplateRepository._path` — the repository neither validates nor escapes the name; the registry does (`is_template_name_valid`). Documented at the method.
- Citation note (no edit): the pre-existing comments in `_persist_values` cite `REQ-009`/`EDGE-009`, which are **`settings-coverage.md`** IDs (`settings.md` REQ-009 is *resets*). The new docstrings cite the `settings-coverage` IDs where the behavior comes from that spec (REQ-009, REQ-010, REQ-011, EDGE-003, EDGE-009) and `settings.md` IDs where it comes from that one (REQ-022, AC-032); no existing citation was removed (INV-I).

**Next (S4.2, group 6):** `permissions` (45 sites: 33 additions + 12 format, incl. 2 `D301`).

## Phase 4 — group 6 (S4.2, 2026-10-09)

Group 6 (`permissions`, 6 files) done, **two commits** — additions half then format half (Q-11). `uv.lock` was rewritten by every `uv run` (F-9), `git restore`d before each commit, never staged.

| Commit | Sites | `ruff check src/backend/permissions` | `--select D` (google) after | Feature tests (`-q`) |
|---|---|---|---|---|
| `9bd979a` `docs(permissions): add missing docstrings (D1xx x33)` | 33 gate sites + 2 private helpers | All checks passed! | 12 (format half pending) | — |
| `5d5a18f` `docs(permissions): fix docstring formatting (D205, D209, D301)` | 12 format | All checks passed! | **0** | `tests/{acceptance,contract,integration,property,unit}/permissions` → **68 passed in 9.68s** |

### Sites, as edited

```text
permissions  src/backend/permissions/catalog.py
  30  D107 PermissionCatalog.__init__      added (both indexes empty, nothing seeded; an unregistered
                                          catalog denies every check `unknown_permission`, REQ-004/REQ-005)
permissions  src/backend/permissions/errors.py
  27  D107 PermissionDeniedError.__init__  added (message built from the context; `user_id=None` worded
                                          as the system principal, AC-026; never a session token, NFR-002)
  41  D107 RoleNotFoundError.__init__      added (role name kept as an attribute, AC-026)
  49  D107 RoleAlreadyExistsError.__init__ added (raised by the repositories on a duplicate insert;
                                          `create_role` lets it propagate, REQ-006)
  57  D107 RoleInUseError.__init__         added (deletion guard for a still-assigned role, REQ-007)
  65  D107 RoleProtectedError.__init__     added (guard on the seeded `admin` / `user` roles, REQ-007)
  73  D107 UnknownPermissionError.__init__ added (grant/revoke and system-set paths, REQ-008, EDGE-020)
permissions  src/backend/permissions/events.py
  56  D102 EventPublisher.publish          added (the bus only enqueues; the feature adds NO isolation —
                                          a raising publisher propagates; REQ-020/AC-025 cover only the
                                          `None` case). Stub body `...` kept after the docstring (INV-D).
permissions  src/backend/permissions/models.py
  81  D102 SessionLookup.get_by_token_hash added (lookup by the SHA-256 hash, never the raw token, D9;
                                          revoked/expired still returned as a record → `invalid_session`,
                                          REQ-017). Stub body `...` kept after the docstring (INV-D).
permissions  src/backend/permissions/repositories.py   (23 gate sites + 2 private helpers)
  38  Q-14  _utcnow                       added (single UTC timestamp source; listings order by name, never time)
  70  Q-14  _SqliteRepository.__init__    added (`create_all` on every construction, idempotent; the migration
                                          is what seeds the roles + bootstrap system set, REQ-022/AC-027)
  143 D102 SqliteRoleRepository.add       added (PK violation translated to `RoleAlreadyExistsError`;
                                          `created_at` stamped here, not by the caller)
  152 D102 .get                           added (own session per call; missing role = `None`, not an error)
  156 D102 .list_all                      added (ordered by role name, not creation time)
  160 D102 .delete                        added (grant rows first; unknown role = silent no-op — the
                                          service guards it, REQ-007)
  183 D102 SqliteGrantRepository.grant    added (insert-only ⇒ a repeat grant keeps the original `granted_at`)
  189 D102 .revoke                        added (absent grant = no-op, REQ-008)
  196 D102 .get_role_permissions          added (no-grant and unknown-role are indistinguishable here;
                                          the service checks existence separately)
  201 D102 .list_all                      added (ordered by `(role, permission)`)
  209 D102 SqliteSystemPrincipalRepository.set_permissions added (one session = all-or-nothing, REQ-018;
                                          key validation happens in the service, EDGE-020)
  219 D102 .get_permissions               added (full table read every call — live, never cached, REQ-018)
  228 D107 MemoryRoleRepository.__init__  added (isolated instance, no roles)
  231 D102 .add                           added (dict membership = the in-memory PK analogue, same error)
  236 D102 .get                           added
  239 D102 .list_all                      added (sorted by name, matching the SQLite ordering)
  242 D102 .delete                        added (silent no-op via `pop` default)
  249 D107 MemoryGrantRepository.__init__ added (keyed by the `(role, permission)` pair)
  252 D102 .grant                         added (insert-only, idempotent, REQ-008)
  257 D102 .revoke                        added
  260 D102 .get_role_permissions          added (linear scan over the keys — fine at fixture sizes)
  263 D102 .list_all                      added (sorted by the key tuple)
  270 D107 MemorySystemPrincipalRepository.__init__ added (empty, NOT the bootstrap set — the migration
                                          seeds that, REQ-022)
  273 D102 .set_permissions               added (a replacement, not a merge)
  279 D102 .get_permissions               added (snapshot copy)
permissions  src/backend/permissions/service.py
  131 D107 PermissionService.__init__     added (the only wiring point, REQ-023/D19; the optional
                                          collaborators select modes: `session_lookup=None` + a token →
                                          `storage_error` (EDGE-007) while a token-less check skips
                                          validation either way (AC-021); `catalog=None` → every check
                                          denies `unknown_permission` (REQ-004); `event_bus=None` → no
                                          events and no `SettingChanged` subscription (AC-025);
                                          `settings_registry=None` → the shared registry resolved
                                          lazily (REQ-019); the subscription is taken in the constructor)
```

Gate-site count: **22 `D102` + 11 `D107` = 33**. The two private helpers (`_utcnow`, `_SqliteRepository.__init__`) are Q-14/INV-H additions found with the one-off `ast` walk, not gate-detected (the google convention ignores private defs). Every other def in the six touched files already had a docstring — the walk now reports none.

Format half — 12 findings over 7 docstrings:

```text
permissions  src/backend/permissions/catalog.py
  1   D301 module docstring              `r"""` prefix + `\\.[a-z0-9_-]` → `\.[a-z0-9_-]`, so the docstring
                                         VALUE is byte-identical (verified: all 7 docstrings of the file
                                         compare equal to `9bd979a` under `ast.get_docstring`)
  41  D301 register_feature              idem (the second backslash occurrence)
permissions  src/backend/permissions/models.py
  34  D205+D209 RolePermission           summary line split; closing `"""` on its own line (hand-edited)
permissions  src/backend/permissions/repositories.py
  57  D205+D209 _make_engine             idem
  71  D205+D209 _SqliteRepository        idem
permissions  src/backend/permissions/service.py
  280 D205+D209 get_role_permissions     idem
  339 D205+D209 _validate_grant          idem
```

**F-10 re-confirmed on this group:** `--fix` / `--diff` offered nothing for the 5 `D205` + 5 `D209` (all hand-edited); the 2 `D301` were hand-edited with the `r"""` prefix instead of `--unsafe-fixes`, for the group-5 reason. No `D403` in this group. The two protocol-stub sites (`events.py:56`, `models.py:81`) kept their `...` body after the docstring — the group-4 INV-D lesson applied pre-emptively, and the digest was checked after the additions commit, not only at the end.

### Gates & no-behavior-delta (INV-D)

```text
uv run ruff check src/backend/permissions                                  → All checks passed!
uv run ruff check src/backend/permissions --select D (google)              → All checks passed!   (0)
uv run ruff format src/backend/permissions                                 → 8 files left unchanged
uv run python "$LOCALAPPDATA/Temp/s41_ast_digest.py" src                   → 64fc1d6ee758bf6ac572d58b100eff95d4bbd1205c993f7d9e2e126657d7bec0
                                                                             (after the additions commit AND after the format commit)
uv run pytest tests/{acceptance,contract,integration,property,unit}/permissions -q → 68 passed in 9.68s
git diff --stat 9bd979a~1..5d5a18f                                         → 6 files, +128/−19, all inside docstrings
```

Remaining `D` sites in `src/` after group 6: **240** (`D102` 97, `D205` 52, `D209` 45, `D107` 29, `D101` 14, `D403` 3).

### Q-26 check (docstring vs. code)

No docstring contradicts the code; each of the following is stated **as the code is**, with no code change and no reclassification:

- `permissions.events.EventPublisher.publish` — the service calls `publish` with no `try`/`except`, so a raising publisher propagates to the calling permission operation. REQ-020 promises only that `None` means "no events, no errors", so this is not a defect — the same observation already recorded for mail and sessionmanagement.
- `repositories.SqliteGrantRepository.get_role_permissions` and `MemoryGrantRepository.get_role_permissions` — an empty result cannot distinguish "role exists with no grants" from "role unknown"; the service does the existence check separately (`_role_known`, REQ-008). Documented at the methods.
- `repositories.MemorySystemPrincipalRepository.__init__` — the in-memory store starts **empty**, it does not carry `BOOTSTRAP_SYSTEM_PERMISSIONS`; only the alembic migration seeds it (REQ-022/AC-027). Stated so a test reader does not assume the bootstrap set.
- Citation check (INV-I / Q-16): every ID cited by the new docstrings is defined in `docs/specs/user-roles-permissions.md` (REQ-004/005/006/007/008/018/019/020/022/023, AC-021/025/026/027, EDGE-007/020); no pre-existing citation was removed or re-pointed.

**Next (S4.2, group 7):** `authentication` (51 sites).

## Phase 4 — group 7 (S4.2, 2026-10-09)

`authentication` — 7 files carry `D` sites (of the feature's 14 modules); 7 files committed. Gate list measured at `049294f`: **51** sites = **50 `D1xx`** + **1 format**, exactly the §Fresh measurement row (`D102`:36 `D101`:7 `D107`:7 `D205`:1). Two commits per Q-11: `98b5dbc` additions, `cb45758` format.

### Additions half — 50 gate sites + 9 Q-14 private helpers (`98b5dbc`)

```text
authentication  src/backend/authentication/errors.py
  35  D107 InvalidResetTokenError.__init__   added (reason rendered into a secret-free message, NFR-002)
authentication  src/backend/authentication/events.py
  26  D101 LoginSucceeded                    added (published per accepted login, either method)
  31  D101 LoginFailed                       added (password path only — passkey failures publish none)
  36  D101 Logout                            added (the idempotent no-op path publishes nothing, AC-014)
  40  D101 PasswordResetRequested            added (fires for unregistered emails too, EDGE-007; no token)
  44  D101 PasswordResetCompleted            added (after the change + the session revoke, REQ-012)
  48  D101 PasskeyRegistered                 added (public key never carried)
  53  D101 PasskeyDeleted                    added (a rejected deletion publishes nothing)
authentication  src/backend/authentication/repository.py
  73  D107 SqliteSessionRepository.__init__  added (parent dir auto-created, 30 s busy timeout, StaticPool for `:memory:`)
  89  D102 .add                              added (returns the object given in, not a re-read copy)
  95  D102 .get_by_token_hash                added (hash in, tz-aware out; never sees a raw token)
  100 D102 .revoke                           added (unknown id / already revoked writes nothing)
  108 D102 .revoke_all_for_user              added (the logout-all of a completed reset, REQ-012)
  117 D102 .get                              added (state-agnostic read; validity is the service's, INV-002)
  121 D102 .list_for_user                    added (newest first, `id` tie-break, revoked+expired included)
  128 D102 .revoke_user_sessions             added (count = rows changed, not rows matched)
  140 D102 .delete_expired                   added (oldest expiry first, `limit` bounds the batch)
  152 D102 .list_all                         added (the search REQ-022 backing read, unpaginated)
  166 D107 SqlitePasswordResetRepository.__init__ added (same engine setup, normally the same database file)
  182 D102 .add                              added (hash only, REQ-011)
  188 D102 .get_by_token_hash                added (expired/used rows returned — the service maps the reason)
  193 D102 .invalidate_all_for_user          added (REQ-011/EDGE-011)
  202 D102 .mark_used                        added (single-use, INV-003)
  218 D107 SqliteWebAuthnCredentialRepository.__init__ added (args visible in tracing: only a database URL)
  234 D102 .add                              added (`transports` stored as JSON text)
  240 D102 .get_by_credential_id             added (the id the browser presents)
  245 D102 .list_for_user                    added (storage order — no `order_by`, no promised order)
  250 D102 .update_sign_count                added (the hijack basis, REQ-015/REQ-016; unknown id ignored)
  258 D102 .delete                           added (no-op; the service checks ownership first, REQ-017)
authentication  src/backend/authentication/service.py
  108 D107 AuthService.__init__              added (what each keyword selects; TTLs fixed at construction and
                                          stamped per row; `max_failed_attempts`/`lockout_duration` unused when a
                                          tracker is injected; `permission_service=None` = standalone, AC-031)
  198 D102 .login                            added (one error kind for four causes; dummy verify on the locked and
                                          unknown/inactive paths; failures counted against the identifier as typed)
  230 D102 .session_info                     added (hashed lookup; the three failure causes are indistinguishable)
  236 D102 .logout                           added (idempotent no-op publishes nothing, EDGE-006)
  244 D102 .request_password_reset           added (identical observable result either way; address lower-cased;
                                          earlier pending tokens invalidated first)
  267 D102 .complete_password_reset          added (reason order unknown → used → expired, so used+expired reports
                                          `"used"`; the password change is delegated, REQ-002)
  284 D102 .begin_passkey_registration       added (enforced action id; a second begin replaces the challenge)
  292 D102 .complete_passkey_registration    added (provider username passed empty; nothing stored on failure)
  313 D102 .begin_passkey_login              added (fails before a challenge is generated; exempt operation)
  321 D102 .complete_passkey_login           added (assertion verified before the store is read; count advanced;
                                          coexists with the password path, REQ-018)
  335 D102 .list_passkeys                    added (transports decoded; public key never exposed, REQ-021)
  347 D102 .delete_passkey                   added (unknown and foreign are the same error on purpose)
authentication  src/backend/authentication/tracker.py
  33  D107 InMemoryAttemptTracker.__init__   added (policy fixed for the tracker's lifetime; one internal lock, NFR-005)
  39  D102 .record_failure                   added (the count never decays → a failure after an elapsed lock re-locks
                                          immediately)
  49  D102 .record_success                   added (all state discarded, AC-008)
  53  D102 .is_locked                        added (an elapsed lock reports `False` without clearing anything)
authentication  src/backend/authentication/webauthn.py
  44  D107 PyWebAuthnProvider.__init__       added (the two challenge maps are the provider's only state)
  51  D102 .generate_registration_options    added (`display_name` fallback; returns `public_dict`, not the options object)
  63  D102 .verify_registration_response     added (`username` unused; the challenge is consumed before verification,
                                          so an unpaired response meets an empty expectation)
  86  D102 .generate_authentication_options  added (`"preferred"` matches `require_user_verification=False`)
  96  D102 .verify_authentication_response   added (returns the presented count; the comparison is the caller's)
  --  Q-14 private helpers (not gate-detected, found by an `ast` walk): `events._utcnow`,
      `repository._session` ×3, `service._publish` / `_user_by_identifier` / `_issue_session`,
      `tracker._AttemptState` — 9 in total. The walk now reports no undocumented def in the
      seven touched files. (`models.py` has 0 gate sites and is untouched by this change; its
      two private password validators stay undocumented — INV-H is scoped to touched files.)
```

Gate-site count: **36 `D102` + 7 `D101` + 7 `D107` = 50** — matches §Fresh measurement.

### Format half — 1 finding over 1 docstring (`cb45758`)

```text
authentication  src/backend/authentication/repositories.py
  71  D205 SessionRepository.delete_expired  summary line split onto one line + blank line before the
                                          description — hand-edited (`--fix --diff` offers nothing, F-10
                                          re-confirmed on this group)
```

No `D209` / `D301` / `D403` in this feature (the only format site in the fresh table). The `delete_expired` ABC body is the docstring alone — no `...` was involved, and the group-4 INV-D lesson was checked by digest after the additions commit anyway.

### Gates & no-behavior-delta (INV-D)

```text
uv run ruff check src/backend/authentication                                  → All checks passed!
uv run ruff check src/backend/authentication --select D (google)              → All checks passed!   (0)
uv run ruff format src/backend/authentication                                 → 13 files left unchanged
uv run python "$LOCALAPPDATA/Temp/s41_ast_digest.py" src                      → 64fc1d6ee758bf6ac572d58b100eff95d4bbd1205c993f7d9e2e126657d7bec0
                                                                                 (after the additions commit AND after the format commit)
uv run pytest tests/{acceptance,contract,integration,property,unit}/authentication -q → 69 passed in 21.08s
git diff --stat 98b5dbc~1..cb45758                                            → 7 files, +272/−2, all inside docstrings
```

Remaining `D` sites in `src/` after group 7: **189** (`D102` 61, `D205` 51, `D209` 45, `D107` 22, `D101` 7, `D403` 3).

### Q-26 check (docstring vs. code)

No docstring was written that contradicts the code; each point below is stated **as the code is**, with no code change and no reclassification:

- **F-11 (new finding, for the Problem Log / after-workflow-optimization).** `AuthService._publish` does **not** catch a publisher exception, so a raising publisher propagates out of `login` / `logout` / the reset flow / the passkey operations. `AGENTS.md` promises the opposite for this feature ("best-effort; a publisher failure never breaks the operation"), and `docs/specs/authentication.md` REQ-020 promises only that a `None` publisher means no events — so the code matches its spec and the *guidance* is what is wrong. The new `_publish` docstring states the actual behavior. Same asymmetry already recorded for mail (group 3); user-management/file-management were the ones claimed to be isolated. Fixing either the guidance or the code is a separate ISSUE, not this change.
- `SqliteWebAuthnCredentialRepository` is the only repository traced **without** `include_args=False`, so its `add` entry records carry the credential argument (public key, credential id). NFR-002 forbids passwords, raw session/reset tokens and password hashes — a WebAuthn public key is none of those, so this is not a defect; documented at the constructor.
- `InMemoryAttemptTracker` never decays a failure count: an *elapsed* lock reports `is_locked() == False` while the count stays at/above the threshold, so the next failed attempt re-locks immediately. AC-008 still holds (a *successful* login clears the state). Documented at `record_failure` / `is_locked`.
- `PyWebAuthnProvider.verify_registration_response` ignores its `username` argument, and both `verify_*` methods `pop()` the challenge *before* verifying, so a failed verification consumes the challenge and an unpaired response is checked against an empty expectation (it fails, but by way of an empty expected challenge). Documented as-is.
- Citation check (INV-I / Q-16): every ID the new docstrings cite is defined in `docs/specs/authentication.md` (REQ-001…REQ-022, AC-008/014/016/022/023/024/025/027/028/031/032, EDGE-004/005/006/007/011/013/014/016, INV-002/INV-003, NFR-002/003/005), except the deliberately qualified cross-feature ones — `session-management` REQ-017 (ADR-061), `search` REQ-022 (ADR-080), and `user-roles-permissions` REQ-024 / AC-031 for the enforcement wiring (authentication.md stops at REQ-022). The pre-existing `service.py` module-docstring citations to REQ-024 and EDGE-022 (also user-roles-permissions) were left untouched.

**Next (S4.2, group 8):** `filemanagement` (58 sites).

## Phase 4 — group 8 (S4.2, 2026-10-09)

`filemanagement` — 6 files, **58** sites: **37** `D1xx` additions (`D102` 27, `D107` 10) and **21** format sites (`D205` 11, `D209` 9, `D403` 1) — exactly the §Fresh measurement row. Two commits per Q-11: `dd8bbd5` (additions) → `c46a07e` (format). `search_source.py` has 0 `D1xx` sites, so it appears only in the format commit.

### Additions half — 37 gate sites (`dd8bbd5`)

```text
filemanagement  src/backend/filemanagement/errors.py
  19  D107 FileManagementNotFoundError.__init__   added (key echoed verbatim; the same error for
                                               "never stored" and "already deleted", REQ-023)
  31  D107 FileTooLargeError.__init__             added (both sizes in bytes; `limit` is the effective
                                               live-read limit at check time, not a default, REQ-003)
  45  D107 FileTypeNotAllowedError.__init__       added (`allowed` is a snapshot; for `avatars` it is the
                                               fixed image set, never the `allowed_types` setting, REQ-006)
  63  D107 FileValidationError.__init__           added (only the context matching `reason` is set; a
                                               filename-extension conflict arrives as `declared`)
  89  D107 StorageError.__init__                  added (`reason` is the branch point; `io` /
                                               `variant_generation` chain the OSError as __cause__, NFR-002)
 102  D107 AvatarError.__init__                   added (one class, two causes; the caller branches on
                                               `operation`, REQ-017)
filemanagement  src/backend/filemanagement/events.py
  87  D102 EventPublisher.publish                 added (no return value inspected, nothing caught → a
                                               failing publisher propagates; the `...` stub body is kept)
filemanagement  src/backend/filemanagement/repository.py
  78  D102 FileRepository.get_by_key              added (exact match; prefix matching is list_by_namespace)
  81  D102 .get_by_id                             added (ids are internal: delete + avatar mapping only)
  84  D102 .update                                added (the stored instance is returned, not the argument)
  87  D102 .delete                                added (silent no-op on an unknown id; metadata only —
                                               content is the caller's)
 101  D102 .set_user_avatar                       added (the previously referenced file is left alone, REQ-017)
 104  D102 .get_user_avatar                       added (a dangling id is returned as stored, EDGE-011)
 107  D102 .clear_user_avatar                      added (mapping row only; file + variants untouched)
 117  D107 SqliteFileRepository.__init__          added (parent dir created, EDGE-015; 30 s busy timeout for
                                               concurrent writers, NFR-004; StaticPool only for :memory:;
                                               tables created here — no migrations)
 141  D102 .add                                  added (same-key replace in one transaction, D5/ADR-054;
                                               attributes stay loaded)
 152  D102 .get_by_key                             added (tz-aware UTC reconciliation at the repository)
 156  D102 .get_by_id                              added
 160  D102 .update                                 added (merge: an unknown id is inserted, not rejected)
 166  D102 .delete                                 added (an unknown id commits nothing)
 173  D102 .list_by_namespace                      added (SQL-side LIKE prefix match, unescaped → F-12)
 188  D102 .set_user_avatar                        added (insert or update, `updated_at` stamped either way)
 199  D102 .get_user_avatar                        added (no existence check on the referenced file)
 204  D102 .clear_user_avatar                       added
filemanagement  src/backend/filemanagement/service.py
 165  D107 FileService.__init__                   added (nothing eager: `backend=None` builds a local-disk
                                               backend per operation from the live setting, REQ-024;
                                               registry resolved lazily; `permission_service=None` = no
                                               enforcement, AC-031)
filemanagement  src/backend/filemanagement/storage.py
  93  D107 LocalDiskStorageBackend.__init__       added (root resolved per operation; the directory is made
                                               by `put`, so a missing root is accepted here)
 114  D102 .put                                  added (temp file in root + os.replace; the temp file is
                                               unlinked on failure, previous content untouched)
 133  D102 .get                                  added (caller closes the stream; check-then-open race
                                               surfaces as reason 'io', not 'not_found')
 142  D102 .delete                                added (missing_ok; a non-file target raises reason 'io')
 149  D102 .exists                                added (an escaping key reports False — the rejection is
                                               swallowed here)
 156  D102 .stat                                  added (mtime as UTC; invalid key / non-file → None)
 175  D107 InMemoryStorageBackend.__init__        added (the two dicts are the whole state; `_updated_at`
                                               exists because there is no filesystem mtime)
 179  D102 .put                                  added (one assignment; a stream is consumed first, so a
                                               concurrent reader never sees a partial value, EDGE-017)
 184  D102 .get                                  added (a fresh independent BytesIO per call)
 189  D102 .delete                                added (value + timestamp; missing key is a no-op)
 193  D102 .exists                                added (dict membership — no key validation at all, unlike
                                               the local backend)
 196  D102 .stat                                  added (size from the bytes, timestamp from the last write)
```

Gate-site count: **27 `D102` + 10 `D107` = 37** — matches §Fresh measurement.

- **INV-H / Q-14 (private helpers in the touched files).** An `ast` walk over the six files reported exactly one undocumented def besides the gate sites: `repository.SqliteFileRepository._session` — documented in the same commit (the pre-existing `expire_on_commit=False` comment is kept as a comment). The walk now reports **0** undocumented def/class in all six files.
- **Group-4 INV-D lesson applied:** the only `...`-bodied site touched was `events.EventPublisher.publish` (a `Protocol` stub) — the `...` is kept after the docstring, and the digest was checked **after the additions commit**, not only at the end.

### Format half — 21 sites, all hand-edited (`c46a07e`)

Line numbers are the §Phase 4 baseline numbers (the ones the step-1 site list reports); in the format commit the `repository.py`/`service.py` sites sit later in the file because of the additions commit.

```text
filemanagement  src/backend/filemanagement/repository.py
  72  D205+D209 FileRepository.add                 summary folded to one line + blank line + description
  96  D205+D209 FileRepository.list_by_namespace    same shape (the "None → all" note moved to the body)
filemanagement  src/backend/filemanagement/search_source.py
 113  D205+D209 _free_text_matches                 summary + body; corrected to what the code does (an empty
                                               free text is a substring of any string field; the None case is
                                               short-circuited by the caller)
 123  D205+D209 _eval_group                        summary + body
 133  D205+D209 _eval_condition                    summary + body (normalization split out)
 161  D403      _apply_exact_operator              `number` → `Number` (hand edit, no fixer)
 171  D205+D209 _sort_key                          summary + body
 181  D205+D209 _query                             summary + body (the full-fetch explanation moved down)
 207  D205      build_file_source                  summary + body
filemanagement  src/backend/filemanagement/service.py
 117  D205+D209 _detect_mime_type                  summary + body; the vague "Preserves the spec's behavior"
                                               replaced by the actual fallback rule (no NUL in the first 8 KiB)
 211  D205+D209 _backend_for                       summary + body
 353  D205      FileService.upload                 one-line summary; the input shapes moved into the body
```

F-10 re-confirmed on this group: `ruff check --select D205,D209,D403 --fix --diff` over these 21 sites produced an **empty diff** — every one is a hand edit. No `D301` in this feature.

### Gates & no-behavior-delta (INV-D)

```text
uv run ruff check src/backend/filemanagement --select D (google)   → All checks passed!   (0, was 58)
uv run ruff check src/backend/filemanagement                       → All checks passed!
uv run ruff format src/backend/filemanagement                      → 10 files left unchanged
uv run python "$LOCALAPPDATA/Temp/s41_ast_digest.py" src           → 64fc1d6ee758bf6ac572d58b100eff95d4bbd1205c993f7d9e2e126657d7bec0
                                                                      (after the additions commit AND after the format commit)
uv run pytest tests/{acceptance,contract,integration,property,unit}/filemanagement -q → 91 passed, 1 skipped in 27.12s
                                                                      (the skip is the pre-existing "symlinks not available on this host")
git diff --stat dd8bbd5~1..c46a07e                                 → 6 files, +231/−41, all inside docstrings
```

Remaining `D` sites in `src/` after group 8: **131** (`D205` 40, `D209` 36, `D102` 34, `D107` 12, `D101` 7, `D403` 2) = search 61 + usermanagement 70.

### Q-26 check (docstring vs. code — no code touched, no reclassification)

- **F-12 (new finding).** `SqliteFileRepository.list_by_namespace` interpolates the namespace into a SQL `LIKE` pattern with no escape character, and `FileService.list_files` never validates its `namespace` argument. `_` is legal in a namespace (`NAMESPACE_PATTERN`, `models.py:95`), so it acts as a single-character wildcard: `list_files(namespace="a_b")` can return records stored under `axb`. REQ-014 requires a *prefix* match, so this is a defect candidate — an ISSUE for a separate change, not this one. Documented as-is at the method.
- **F-13 (same family as F-11).** `FileService._publish` catches nothing, so a raising publisher propagates out of `upload` / `download` / the avatar operations. `AGENTS.md` promises "a publisher failure never breaks the operation" for file-management; `docs/specs/file-management.md` REQ-022 promises only that a `None` publisher means no events and no error — the code matches its spec, the guidance is what is wrong. Stated in the `EventPublisher.publish` docstring.
- `InMemoryStorageBackend` performs no key-pattern/containment check (unlike the local backend). Not a defect — REQ-016 scopes the containment and symlink defenses to the local backend — documented at `exists` so the asymmetry is visible.
- Citation check (INV-I / Q-16): the new docstrings cite only IDs the citing file's own spec defines — `errors.py` / `repository.py` / `storage.py` / `service.py` → `docs/specs/file-management.md` (REQ-003/006/013/015/016/017/022/023/024, AC-031, EDGE-006/007/011/015/017, NFR-002/004). `search_source.py` cites **`docs/specs/search.md`** IDs (REQ-005/006/012/021) — verified as a different ID space (`file-management.md` REQ-021 is the avatar-variant requirement); the module docstring already names `docs/specs/search.md`, so the per-function citations resolve unambiguously and were left untouched.

**Next (S4.2, group 9):** `search` (61 sites).

## Phase 4 — group 9 (S4.2, 2026-10-09)

`search` — 4 of the 7 modules carry `D` sites (`errors.py`, `events.py`, `models.py`, `service.py`; `__init__.py`, `feature_actions.py`, `feature_settings.py` are already clean), **61** sites: **6** `D1xx` additions (`D102` 1, `D107` 5) and **55** format sites (`D205` 28, `D209` 26, `D403` 1) — exactly the §Fresh measurement row. Two commits per Q-11: `f0a2fcc` (additions) → `b02eefc` (format).

### Additions half — 6 gate sites (`f0a2fcc`)

```text
search  src/backend/search/errors.py
  19  D107 UnknownSourceError.__init__       added (the feature name is an exact dict-key lookup, not a
                                          normalized match; kept on the instance, REQ-010/EDGE-001)
  33  D107 MalformedQueryError.__init__      added (the message is composed from exactly the context that
                                          applies; a pagination problem carries no field/source, REQ-010/AC-024)
  50  D107 SourceQueryFailedError.__init__   added (`error` is the exception type name → secret-free,
                                          NFR-002; a global fan-out failure is a marker instead, REQ-011)
search  src/backend/search/events.py
  37  D102 EventPublisher.publish            added (nothing is caught: a raising publisher propagates; only a
                                          `None` publisher is promised error-free, REQ-014 — F-14; the
                                          `...` Protocol stub body is kept)
search  src/backend/search/service.py
 331  D107 SearchService.__init__            added (nothing eager: the registry is resolved per read,
                                          REQ-013; one RLock guards the source dict for registration and
                                          selection, REQ-018; pool threads start on first submit, D12/REQ-019)
 516  D107 InMemorySource.__init__           added (`fields`/`items` are copied snapshots; the declared-field
                                          map is built once for the query path, REQ-017)
```

Gate-site count: **1 `D102` + 5 `D107` = 6** — matches §Fresh measurement.

- **INV-H / Q-14 (private helpers in the touched files).** An `ast` walk over all seven modules of the package reported **0** undocumented def/class after the additions — unlike groups 7 and 8, `search` had no undocumented private helper outside the gate sites (`_normalize`, `_find_field`, `_eval_*`, `_query`, … all already documented).
- **Group-4 INV-D lesson applied:** the only `...`-bodied site touched was `events.EventPublisher.publish` (a `Protocol` stub) — the `...` is kept after the docstring, and the digest was checked **after the additions commit**, not only at the end.

### Format half — 55 sites, all hand-edited (`b02eefc`)

Line numbers are the step-1 site list (pre-additions); in the format commit the `service.py` sites sit later in the file because of the additions commit.

```text
search  src/backend/search/errors.py
  46  D205+D209 SourceQueryFailedError              one-line summary + "Carries …" body
search  src/backend/search/events.py
  34  D205+D209 EventPublisher                      summary + the `None`-publisher promise as body
search  src/backend/search/models.py
  22  D205+D209 FieldType                           summary + "a list field …" body
  41  D205+D209 SourceField                         summary + flags body
  60  D205+D209 SourcePage                          summary + page/total body
  85  D205+D209 FilterCondition                     summary + field/operator/value body
 157  D205+D209 SearchResultItem                    summary + item-shape body
 166  D205+D209 SourceFailure                       summary + marker-shape body
 176  D205+D209 SearchResult                        summary + result-shape body
search  src/backend/search/service.py
  74  D205+D209 _read_setting                       summary + the fallback-condition body
  82  D205+D209 _validate_source_declaration        summary + checks / raises body
  96  D205+D209 _is_identical_source                summary + criteria body ("compared by identity" made explicit)
 155  D205+D209 _value_matches_type                 summary + per-type list body
 169  D205+D209 _validate_pagination                summary + raise-condition body
 178  D205+D209 _validate_query_against_source      summary + filter/sort body
 200  D205+D209 _validate_filter_condition          summary + three-check body
 225  D205+D209 _free_text_matches                  imperative summary + match-rule body
 239  D205+D209 _eval_group                         folded to one line (94 < 120 chars)
 251  D205+D209 _eval_condition                     folded to one line (88 chars)
 283  D403      _apply_exact_operator               `number / boolean / datetime operators:` → `Operators of
                                                  number / boolean / datetime fields:` (hand edit; the spec's
                                                  lowercase type names kept, so D403 is satisfied without renaming)
 293  D205+D209 _apply_operator                     summary + per-type-semantics body
 306  D205+D209 _sort_key                           summary + ordering body
 320  D205      SearchService                       one-line summary; the REQ ids kept as the body's first line
 367  D205+D209 SearchService.unregister_source     folded to one line (90 chars)
 438  D205+D209 SearchService._select_sources       summary + selection-rule body
 464  D205+D209 SearchService._effective_limit      summary + default/clamp body
 474  D205      SearchService._query_source         one-line summary; `(D12, REQ-019, AC-033, EDGE-011)` moved
                                                  into the body's first sentence (the summary would not fit 120)
 494  D205+D209 SearchService._publish              summary + `None`-publisher body
 556  D205+D209 get_search_service                  summary + singleton body ("ignores its arguments" made explicit)
```

29 docstrings → 28 `D205` + 26 `D209` + 1 `D403` = **55** sites (320 and 474 are `D205`-only; the three folded docstrings clear both codes on one line).

F-10 re-confirmed on this group: `--fix --diff` over the `D205`/`D209`/`D403` sites produced an **empty diff** (probed once) — every one is a hand edit. No `D301` in this feature.

### Gates & no-behavior-delta (INV-D)

```text
uv run ruff check src/backend/search --select D (google)   → All checks passed!   (0, was 61)
uv run ruff check src/backend/search                       → All checks passed!
uv run ruff format src/backend/search                      → 7 files left unchanged / already formatted
uv run python "$LOCALAPPDATA/Temp/s41_ast_digest.py" src   → 64fc1d6ee758bf6ac572d58b100eff95d4bbd1205c993f7d9e2e126657d7bec0
                                                                      (after the additions commit AND after the format commit)
uv run pytest tests/{acceptance,contract,integration,property,unit}/search -q → 87 passed in 13.44s
git diff --stat f318713..f0a2fcc                           → 3 files, +46/−1 (additions)
git diff --stat f318713..b02eefc                           → 4 files, +175/−74, all inside docstrings
```

- **Docstring-value check.** A one-off `ast.get_docstring` comparison of every docstring in the four files against the pre-group-9 commit `f318713` reports 6 `ADDED` + 29 `CHANGED`. Every `CHANGED` pair is identical once whitespace is collapsed, except for the wording a one-line summary requires (the summary's colon moved into a body sentence) and two deliberate clarifications: `_is_identical_source` ("compared by identity" — the code compares the query function with `is`) and `get_search_service` ("ignores its arguments" — the arguments are used only on the creating call). No docstring became signature-restating filler (INV-G).
- **INV-I (citations kept).** Every `REQ`/`AC`/`EDGE`/`NFR`/`D` id present before is present after; `_query_source`'s `(D12, REQ-019, AC-033, EDGE-011)` moved from the summary to the body.

Remaining `D` sites in `src/` after group 9: **70** (`D102` 33, `D205` 12, `D209` 10, `D101` 7, `D107` 7, `D403` 1) = `usermanagement` only.

### Q-26 check (docstring vs. code — no code touched, no reclassification)

- **F-14 (same family as F-11/F-13).** `SearchService._publish` catches nothing, so a publisher that raises propagates out of `register_source` / `unregister_source` / `search`. `AGENTS.md` calls the search events "best-effort"; `docs/specs/search.md` REQ-014 promises only that a `None` publisher means no events and no error — the code matches its spec, the guidance over-promises. Stated in the new `EventPublisher.publish` docstring; `_publish`'s own docstring keeps its original (true but narrower) claim.
- **F-15 (pre-existing spec/implementation gap, untouched).** `docs/specs/search.md` v4 adds REQ-024 (`set_search_service()`, AC-038..AC-041, EDGE-022/EDGE-023) and names it in REQ-015's traced-module-function list and REQ-017's singleton surface — but no `set_search_service` exists anywhere in `src/` (only `get_search_service` / `reset_search_service`), and no test references it. Recorded as-is; no docstring claims it exists. A separate change (ISSUE or FEATURE), not this one.
- Citation check (INV-I / Q-16): every id cited by the added/edited docstrings is defined by **`docs/specs/search.md`** — verified against its tables (REQ-001/002/003/005/007/010/011/013/014/016/017/018/019, AC-024/AC-026, EDGE-001/EDGE-013/EDGE-021, NFR-002). All four touched files belong to the search feature, so there is no second ID space to disambiguate (unlike group 8's `search_source.py`).

**Next (S4.2, group 10):** `usermanagement` (70 sites) — the last feature group before the config commit.

## Phase 4 — group 10 (S4.2, 2026-10-09)

`usermanagement` — 7 of the 10 modules carry `D` sites (`errors.py`, `events.py`, `models.py`, `repository.py`, `role_store.py`, `search_source.py`, `service.py`; `__init__.py`, `feature_actions.py`, `feature_settings.py` are already clean), **70** sites: **47** `D1xx` additions (`D102` 33, `D101` 7, `D107` 7) and **23** format sites (`D205` 12, `D209` 10, `D403` 1) — exactly the §Fresh measurement row. Two commits per Q-11: `1040a76` (additions) → `39e4904` (format).

### Additions half — 47 gate sites + 15 Q-14 private helpers (`1040a76`)

```text
usermanagement  src/backend/usermanagement/errors.py
  24/32/39/48 D107 UserAlreadyExistsError / UserNotFoundError / InvalidRoleError / LastAdminError .__init__
      added (the colliding column only — the value never reaches the message, NFR-002; an explicit
      message names the identifier the site looked up; `allowed` is the store's whole role set sorted
      into the message; every guard site raises LastAdminError bare, REQ-008)
usermanagement  src/backend/usermanagement/events.py
  27/34/39/44/48/54/58 D101 UserCreated / UserUpdated / UserDeleted / UserPasswordChanged /
      UserRoleChanged / UserActivated / UserDeactivated
      added (which mutation publishes it + its AC id + what it never carries: no password, no hash;
      role events carry whole lists, user-roles-permissions REQ-026/AC-037)
  65 D102 EventPublisher.publish             added (nothing is caught: a raising publisher propagates
      after the mutation is committed, EDGE-020; the `...` Protocol stub body is kept)
  17 Q-14 _utcnow                            added (the single clock source for event timestamps)
usermanagement  src/backend/usermanagement/models.py
  39 D102 RoleListType.process_bind_param    added (a role list is written as a JSON array string;
  44 D102 RoleListType.process_result_value  added  NULL for None; a materialized list is copied,
                                              not re-decoded)
  58/68/78 Q-14 _validate_password / _validate_display_name / _validate_profile_picture_url
      added (the shared rules: 8..128 chars + one letter + one digit, NFR-001; blank/over-long
      rejected; scheme check only, the URL is never fetched)
  123/130/135/140/150 Q-14 UserCreate._check_username / _check_password / _check_display_name /
      _check_roles / _check_profile_picture_url     added (rules + the AC id; role *existence* is the
      service's role store, not the schema)
  165 Q-14 NewPassword._check_password       added  182/187 Q-14 UserUpdate._check_display_name /
      _check_profile_picture_url              added ("leave unchanged", not "clear", REQ-011)
usermanagement  src/backend/usermanagement/repository.py
  81/84/87/90/93/96 D102 UserRepository.get_by_id / get_by_username / get_by_email / update /
      delete / list_all
      added (the ABC contract a substitute repository must honour: tz-aware UTC, case-sensitive
      usernames vs. case-insensitive emails, merge semantics, unknown-id delete is a no-op,
      ordering unspecified; every `...` stub body is kept)
  112 D107 SqliteUserRepository.__init__     added (parent directory created, EDGE-007; `:memory:`
      gets a static pool so one instance sees one database, EDGE-008)
  143/152/156/161/166/175/182/189 D102 add / get_by_id / get_by_username / get_by_email / update /
      delete / list_all / count_active_by_role
      added (one session per operation; the constraint maps to the colliding field, EDGE-015; the
      inactive filter is SQL not Python; the count is what the last-admin guard counts, REQ-008)
  132/138 Q-14 _map_integrity_error / _session  added (an unrecognized violation reports field=
      "username"; `expire_on_commit=False` — the inline comment moved into the docstring)
usermanagement  src/backend/usermanagement/role_store.py
  36 D107 StaticRoleStore.__init__           added (the iterable is snapshotted to a tuple, so the
      caller cannot change the accepted set afterwards)
  39/42 D102 has_role / list_roles           added (exact, case-sensitive; the tuple itself is returned)
usermanagement  src/backend/usermanagement/service.py
  78 D107 UserManager.__init__               added (no eager work but the argon2id hasher; a None
      role store becomes StaticRoleStore(("admin", "user")); a None checker is standalone mode,
      user-roles-permissions AC-031)
  100/104/111/118/140/165/174/182/192/196/204/213/226/237 D102 get_user / get_user_by_username /
      list_users / create_user / update_user / delete_user / change_password / verify_password /
      set_role / set_roles / add_role / remove_role / activate_user / deactivate_user
      added (the idempotent no-ops that write and publish nothing; verify_password reads any argon2
      failure as a wrong password; set_roles / add_role / remove_role are not in the 11-action
      permission catalog; add_role skips the last-admin guard on purpose)
  55 Q-14 _utcnow                            added
```

Gate-site count: **33 `D102` + 7 `D101` + 7 `D107` = 47** — matches §Fresh measurement.

- **INV-H / Q-14.** An `ast` sweep over all ten modules reports **0** undocumented `def`/`class` after the additions — 15 private helpers beyond the 47 gate sites (`_utcnow` ×2, 11 model validators, `_map_integrity_error`, `_session`).
- **Group-4 INV-D lesson applied.** The `...`-bodied sites are `EventPublisher.publish` (a `Protocol` stub) and the six `UserRepository` ABC stubs — every one keeps its `...` after the docstring, and the digest was checked **after the additions commit**, not only at the end.
- **In-step fix (self-introduced).** The additions half first produced 4 new `D205`s of my own (three `errors.py` `__init__` docstrings, one `role_store.list_roles`); all were re-folded within the same execution, so `1040a76` introduces no new format site and the format half is exactly the pre-existing 23.

### Format half — 23 sites over 13 docstrings, all hand-edited (`39e4904`)

Line numbers are the pre-group (`46b3fe7`) site list — the same list §Fresh measurement counts.

```text
repository.py      76  UserRepository.add                D205+D209 → folded to one line (114 chars)
repository.py     100  UserRepository.count_active_by_role D205+D209 → one line + REQ-026 qualified
search_source.py  105  _free_text_matches                D205+D209 → one line (115 chars)
search_source.py  115  _eval_group                       D205+D209 → one line (93 chars)
search_source.py  125  _eval_condition                   D205+D209 → summary + body
search_source.py  153  _apply_exact_operator             D403 → "Operators of boolean / datetime fields:
                                                       exact comparison (search REQ-012)." — the spec's
                                                       lowercase type names kept (group-9 pattern)
search_source.py  163  _sort_key                         D205+D209 → one line (102 chars)
search_source.py  173  _query                            D205+D209 → summary + body
search_source.py  198  build_user_source                 D205      → summary line + the existing body
service.py        251  UserManager._get_user_or_raise    D205+D209 → one line (91 chars)
service.py        259  UserManager._apply_roles          D205+D209 → summary + body
service.py        285  UserManager._assert_not_last_admin D205      → summary folded to one line
service.py        309  UserManager._publish              D205+D209 → summary + body
```

13 docstrings → 12 `D205` + 10 `D209` + 1 `D403` = **23** sites. F-10 re-confirmed for this group: no `--fix` probe was attempted (groups 5-9 established these three codes offer no autofix in ruff 0.16.10). No `D301` in this feature.

- **Q-16 qualification (same commit).** `usermanagement` cites **two** ID spaces, and the numbers collide: `docs/specs/user-management.md` (REQ-001..017, AC-001..038, EDGE-001..021, NFR-001..004) and `docs/specs/user-roles-permissions.md` (REQ-012/024/026, AC-031/034/036/037, EDGE-020/022). Every cross-space citation in a touched docstring is now qualified — `user-roles-permissions REQ-012` (delegation) vs. `REQ-012` (hard delete), `AC-031` (standalone mode) vs. `AC-031` (`UserUpdated` event), `AC-034`/`AC-036` (role assignment / last-admin guard) vs. `AC-034`/`AC-036` (role / deactivate events), `REQ-024`/`REQ-026` (undefined in `user-management.md`); and in `search_source.py` the `search` REQ-005/006/012/020 vs. `user-management` REQ-005/006/012 (password / role-set / delete). The `service.py` module docstring paragraph was re-wrapped to keep the qualified line under 120 chars.

### Gates & no-behavior-delta (INV-D)

```text
uv run ruff check src/backend/usermanagement --select D (google) → All checks passed!   (0, was 70)
uv run ruff check src --select D (google)                        → All checks passed!   (0 over ALL of src/ — the config-commit pre-condition)
uv run ruff check src/backend/usermanagement                     → All checks passed!
uv run ruff format src/backend/usermanagement                    → 10 files left unchanged
uv run python "$LOCALAPPDATA/Temp/s41_ast_digest.py" src         → 64fc1d6ee758bf6ac572d58b100eff95d4bbd1205c993f7d9e2e126657d7bec0
                                                                      (after the additions commit AND after the format commit)
uv run pytest tests/{acceptance,contract,integration,property,unit}/usermanagement -q → 78 passed in 17.30s
git diff --stat 46b3fe7..1040a76                                 → 6 files, +218/−10 (additions)
git diff --stat 46b3fe7..39e4904                                 → 7 files, +267/−52, all inside docstrings
```

- **Docstring-value check.** An `ast.get_docstring` comparison of every docstring in the seven files against the pre-group commit `46b3fe7` reports **62 `ADDED` + 15 `CHANGED` + 0 `REMOVED`**. 4 `CHANGED` pairs are whitespace-only (the folded one-liners); the other 11 differ only by the summary/body split, the D403 wording, and the Q-16 qualification. No docstring became signature-restating filler (INV-G) — each states a rule, a promise or an id the signature does not carry.
- **INV-I (citations kept).** The same script reports **0** `REQ`/`AC`/`EDGE`/`NFR` ids lost between `46b3fe7` and `39e4904`.
- **Secret check (security).** No added docstring contains a password, a token or a hash value; the password-related wording names only the argon2id algorithm and the length/character rules.

Remaining `D` sites in `src/` after group 10: **0** — every feature group is done, so the config commit can flip the gate.

### Q-26 check (docstring vs. code — no code touched, no reclassification)

- **F-16 (guidance under-describes the error surface).** `UserManager.remove_role` raises a bare `ValueError` when the removal would empty the role list, and `_validate_roles` raises `ValueError` for an empty list — neither is a `UserManagerError`. `AGENTS.md` ("Exceptions are the `UserManagerError` hierarchy") presents that hierarchy as the whole surface. The code matches its spec (user-roles-permissions REQ-026 requires a non-empty role list); the guidance is incomplete. Stated as-is in the new `remove_role` and `_validate_roles` docstrings; no code touched.
- **F-17 (pre-existing spec/guidance drift, untouched).** `docs/specs/user-management.md` REQ-006 and AC-008/AC-009 still describe a single role validated against a role set whose default is `{"admin", "member"}`; the code implements the user-roles-permissions REQ-026 amendment (injected `RoleStore`, default `StaticRoleStore(("admin", "user"))`, `roles` lists). `AGENTS.md`'s user-management section is stale the same way ("an optional `roles` iterable (default `("admin", "member")`)"). Docstrings state the code as it is; the amendment is a separate change (spec-drift work, not this chore).
- **Not a finding.** `set_roles` / `add_role` / `remove_role` carry no `@requires_permission` and are absent from the 11-action `usermanagement` catalog — that matches user-roles-permissions REQ-026 (the assignment primitives) and REQ-012 (the permission service checks its own action, then delegates). Documented as such in the three docstrings so a reader does not mistake the gap for a missing check.

**Next (S4.2, group 11):** the config commit — `pyproject.toml` (`select += "D"`, `lint.pydocstyle.convention = "google"`, the four `per-file-ignores` trees, the widened `fixable`), `mkdocs.yml`, `.pre-commit-config.yaml` rev, `AGENTS.md:743`. `src/` is `--select D` clean, so the gate flips green.

## Phase 4 — group 11 config commit (S4.2, 2026-10-09)

One commit, four files, exactly the §"Exact change scope" items 1–4 — the gate flips here (Q-7 a: docstrings first, config last). Base: `ba2867a` (group 10 evidence); `src/` was already `--select D` clean, so nothing outside the config/guidance surface needed to change.

### Config diff summary

| File | Change | Scope item |
|---|---|---|
| `pyproject.toml` | `lint.select` gains `"D"  # pydocstyle — docstrings (google convention; src/ only, see per-file-ignores)` | §1 |
| `pyproject.toml` | `lint.fixable` gains `"D204", "D207", "D208", "D209", "D211", "D212", "D403"  # docstring layout, always-fixable (Q-12)` | §1 (Q-12) |
| `pyproject.toml` | new `[tool.ruff.lint.pydocstyle]` → `convention = "google"          # Q-1 / Q-2` | §1 |
| `pyproject.toml` | new `[tool.ruff.lint.per-file-ignores]` → `"tests/*" = ["D"]`, `"scripts/*" = ["D"]`, `"migrations/*" = ["D"]`, `".github/*" = ["D"]` (the record's exact glob spellings — ruff's per-file globs match across `/`, no `**` rewrite) | §1 (Q-3 / Q-23 / Q-29) |
| `mkdocs.yml` | `mkdocstrings` → `handlers.python.options.docstring_style: google` (inert pin, F-8 — the handler already defaults to `google`; zero rendering delta from this line) | §2 (Q-18) |
| `.pre-commit-config.yaml` | `astral-sh/ruff-pre-commit` `rev: v0.15.12` → **`rev: v0.16.10`** (one line, F-6 — matches the `ruff>=0.16.10` dev pin and the installed `ruff 0.16.10`) | §3 (Q-28) |
| `AGENTS.md` | the single **Documentation** bullet in §"General Code & Style Conventions" extended: Google style, gated by ruff `D` over `src/` with the four exempt trees via `per-file-ignores`, and the no-filler rule (filler that restates the signature is rejected in review). Prose only; the `python-best-practices` skill untouched (Q-24) | §4 (Q-24) |

Nothing else in `pyproject.toml` changed: `version = "1.0.0"` (line 4) and `[tool.bumpversion] current_version = "1.0.0"` (line 85) are untouched (**INV-E**, Q-27); `ruff>=0.16.10` (line 62) untouched (**INV-F**, no new/changed dependency); no `# noqa` anywhere on the branch (**INV-C** — the only `noqa` string in the branch diff is INV-C's own wording in this file); `per-file-ignores` gained **exactly** the four decided trees, no per-file exemption for a real `src/` gap.

### Verification (flipped gate + invariants)

| Evidence | Command | Result |
|---|---|---|
| **Flipped CI-parity sweep, `D` now selected** | `uv run ruff check .` | **All checks passed!** — the acceptance signal; `D` is live over `src/` and the four exempt trees are silenced by `per-file-ignores` (the 743 `tests/` and the 2 `.github/hooks/` sites do not fire) |
| Targeted `D` re-check | `uv run ruff check src --select D --config 'lint.pydocstyle.convention = "google"'` | All checks passed! (0 of the original 328 sites remain) |
| Formatting unchanged | `uv run ruff format --check .` | **339 files already formatted** — identical to the S4.1 baseline |
| Types unchanged | `uv run mypy src/` | **Success: no issues found in 84 source files** — identical to baseline |
| **INV-D** (executable code identical) | `uv run python %LOCALAPPDATA%/Temp/s41_ast_digest.py src` | `64fc1d6ee758bf6ac572d58b100eff95d4bbd1205c993f7d9e2e126657d7bec0` — byte-identical to the S4.1 baseline digest |
| **INV-A** (traced wording, AC-009) | `uv run pytest tests/acceptance/logging_coverage -q -k docstring` → `tests/acceptance/logging_coverage/test_docstrings.py::test_traced_class_docstrings_mention_tracing` | **1 passed, 19 deselected** |
| Docs site | `uv run --group docs mkdocs build --strict` | built in 3.27 s, **no `WARNING`/`ERROR` log lines** (the only "Warning" string in the output is the Material theme's upstream MkDocs-2.0 advisory banner, printed on every build, unrelated to this change) |
| Dependencies | `uv run deptry .` | **Success! No dependency issues found.** (90 files scanned) |
| **INV-B / INV-J** (diff surface) | `git diff --name-only` before commit | only `pyproject.toml`, `mkdocs.yml`, `.pre-commit-config.yaml`, `AGENTS.md` (+ this record) — no `tests/`, `scripts/`, `migrations/`, `userdocs/`, `docs/specs/`, `docs/decisions/`, `docs/tasks/` file touched |

**All 328 `D` sites measured at P.4 (398 bare / 328 under google) are now gated**: the config commit makes `ruff check .` fail if any of them regresses or if a new undocumented public object appears in `src/`, and CI's `ruff` job (`.github/workflows/lint.yml`) plus the `ruff-check --fix` pre-commit hook now run the same rule set at the same version.

### `uv.lock` decision (F-9) — deliberately NOT touched here

`uv.lock` is dirtied by every `uv run` in this worktree (the stale `python-template 0.6.1` entry vs `pyproject.toml:4` `1.0.0`). It was **reverted with `git restore uv.lock` before committing and never staged**, so the config commit contains exactly the four files. Supersedes the P-74 note that folded the refresh into this change's config commit: **structure-map's PR #75 bump commit already carries the one-line lock refresh**, so duplicating it here would only create a merge conflict on a one-line file. Until #75 merges, every step on every branch keeps reverting the incidental churn.

**Next (S5.1):** Phase 5 — full test suite (treating `tests/contract/search/test_search_contracts.py::test_nfr_001_performance_budgets` as the known flake per P-86) + the DOCS/CHORE light gate, then INV-A…INV-J against the final diff.

## Phase 5 — S5.1 full test suite (2026-10-09)

Objective: reproduce the S4.1 suite baseline at the final commit (`b603379`, all 11 commit groups landed). No source or test file was edited in this step; the only write is this section. Toolchain as at S4.1: `Python 3.14.5` (the `uv` env in this worktree).

### Commands and exact summary lines

| Command | S5.1 result (2026-10-09, `b603379`) |
|---|---|
| `uv run pytest tests/ -q` | **`761 passed, 1 skipped in 230.83s (0:03:50)`** |
| `uv run pytest tests/acceptance/ -q` | **`364 passed, 1 skipped in 47.49s`** |
| `uv run pytest tests/property/ -q` | **`71 passed in 57.30s`** |
| `uv run pytest tests/contract/ -q` | **`51 passed in 85.91s (0:01:25)`** |
| `uv run pytest tests/ -q --collect-only` | **`762 tests collected in 1.02s`** |

The single skip is unchanged from the baseline, same node and same reason:
`SKIPPED [1] tests\acceptance\filemanagement\test_filemanagement.py:364: symlinks not available on this host`.

### Baseline comparison — verdict: **DELTA-EXPLAINED** (no regression)

| | S4.1 baseline (`84b25bd`) | S5.1 (`b603379`) |
|---|---|---|
| Full suite | `1 failed, 760 passed, 1 skipped in 236.60s (0:03:56)` | `761 passed, 1 skipped in 230.83s (0:03:50)` |
| Collected | 762 | **762** |
| Skipped | 1 (symlink host limit) | 1 (same node) |
| Failed | 1 (the NFR-001 timing flake) | **0** |

The only delta is the known pre-existing flake **passing** this run: `tests/contract/search/test_search_contracts.py::test_nfr_001_performance_budgets` (`assert statistics.median(query_samples) < 0.3`) measured `0.306 s` under the S4.1 full-suite load and stayed inside the budget here. Collected count, skip set and every other test are identical, so the delta is the flake's load sensitivity (§Baseline flake, Problem Log **P-73** / **P-86**), not a behavior change — exactly the outcome §Baseline flake predicted: *"identical counts is not reproducible for this one test."*

Flake evidence (isolated re-run at this same commit, i.e. both directions observed):

```text
uv run pytest "tests/contract/search/test_search_contracts.py::test_nfr_001_performance_budgets" -q
→ 1 passed in 8.36s
```

So the test is green in isolation at both `84b25bd` (S4.1: `1 passed in 8.44s`) and `b603379`, and green in the full suite here — no run at any commit shows a failure other than the load-dependent one already recorded at S4.1. **No other delta from the baseline: no new failure, no new skip, no test disappeared.**

### INV-B (no test touched) — confirmed against the final diff

`git diff --name-only 84b25bd..HEAD` lists **47 files**: 41 under `src/` (the ten feature groups) plus `pyproject.toml`, `mkdocs.yml`, `.pre-commit-config.yaml`, `AGENTS.md` (group 11) and the two record files (`docs/verification/ruff-d-docstrings.md`, `docs/workflow/PROBLEMS.md`). **Zero paths under `tests/`** — `git diff --stat 84b25bd..HEAD -- tests/` is empty. The 762-collected / 1-skip identity above is the executable cross-check.

The AC-009 invariant test from the §No-behavior-delta proof plan (`tests/acceptance/logging_coverage/test_docstrings.py::test_traced_class_docstrings_mention_tracing`) ran green inside the acceptance run — its dedicated re-run is part of S5.2's gate set.

**S5.1 gate: PASS.** Suite reproduced (762 collected, 1 skip, the single baseline failure classified as the known pre-existing flake with isolated evidence in both directions).

**Next (S5.2):** `uv run ruff check .` (whole-repo sweep — the one full-repo run, with `D` now selected over `src/`) + `uv run ruff format --check .` + `uv run mypy src/` + `uv run --group docs mkdocs build --strict` + the docstring-stripped AST digest, each compared to its S4.1 baseline value.

## Phase 5 — S5.2 lint, types, docs build and digest (2026-10-09)

Measured in this worktree at `903339c` (all eleven groups in, `D` selected over `src/`). The full suite is **not** re-run here — S5.1 recorded it (`761 passed, 1 skipped`, no regression). Toolchain at measurement: `ruff 0.16.10`, `mypy 2.4.0 (compiled: yes)`.

| # | Gate | Command | Result line | Verdict |
|---|---|---|---|---|
| 1 | Lint **with the new gate** (CI parity, `.github/workflows/lint.yml`) | `uv run ruff check .` | `All checks passed!` (exit 0) | **PASS** |
| 2 | Format gate | `uv run ruff format --check .` | `339 files already formatted` (exit 0) | **PASS** — identical to the S4.1 baseline |
| 3 | Types | `uv run mypy src/` | `Success: no issues found in 84 source files` | **PASS** — identical to the S4.1 baseline |
| 4 | Published site still builds | `uv run --group docs mkdocs build --strict` | `INFO    -  Documentation built in 2.05 seconds` (exit 0) | **PASS** |
| 5 | INV-A / AC-009 wording intact | `uv run pytest tests/acceptance/logging_coverage/test_docstrings.py::test_traced_class_docstrings_mention_tracing -q` | `1 passed in 0.42s` | **PASS** |
| 6 | INV-D executable code identical | `uv run python "$LOCALAPPDATA/Temp/s41_ast_digest.py" src` | `64fc1d6ee758bf6ac572d58b100eff95d4bbd1205c993f7d9e2e126657d7bec0` | **PASS** — matches the P.4 / S4.1 baseline digest |
| 7 | Dependencies (the config commit edited `pyproject.toml`) | `uv run deptry .` | `Success! No dependency issues found.` (`Scanning 90 files...`) | **PASS** |

Gate 1 is the acceptance signal, and it is the gate that actually tests this change: `D` is in `select` (`pyproject.toml:195`, google convention) and `per-file-ignores` (`pyproject.toml:220-224`) exempts **exactly** the four decided trees — `tests/*`, `scripts/*`, `migrations/*`, `.github/*`. No `# noqa` anywhere, no `src/` exemption (**INV-C**).

Gate 7 is not in the S4.1 gate-baseline table; it is in the group-11 config-commit gate table, re-run here because that commit is the one that changed `pyproject.toml`.

### AST digest — change state vs. control run (INV-D, and its non-vacuity)

Change state (this worktree at `903339c`, **relative** `src` root, per §AST digest reproduction):

```text
uv run python "$LOCALAPPDATA/Temp/s41_ast_digest.py" src
→ 64fc1d6ee758bf6ac572d58b100eff95d4bbd1205c993f7d9e2e126657d7bec0
```

Control run — the **pre-change** `src/` exported from the base commit `45aa61c` (`git archive 45aa61c src | tar -x -C <tempdir>`) into a temp directory **outside** the worktree, digested with the same script and the same relative `src` root, then mutated in place:

```text
base (45aa61c)                     : 64fc1d6ee758bf6ac572d58b100eff95d4bbd1205c993f7d9e2e126657d7bec0   SAME as the change state
+ docstring on EventBus.__enter__  : 64fc1d6ee758bf6ac572d58b100eff95d4bbd1205c993f7d9e2e126657d7bec0   SAME      (blind to docstrings)
+ max_queue_size 1000 → 1001       : ce0e01e8e1fdb396b90731ecb1801fa894b5fa9bf39cc39544c5eec33e332248   DIFFERENT (catches a code change)
```

The control reproduces the P.4 control: the digest is blind to a docstring and sensitive to a one-character code change, so the gate-6 match is evidence rather than a vacuous equality. Mutator: `%LOCALAPPDATA%/Temp/s52_control_mutate.py` (throwaway, never added to `scripts/`, Q-25).

Supporting counts (throwaway helpers `%LOCALAPPDATA%/Temp/s52_ast_count.py` and `s52_doc_count.py`): `src/` = **84 files / 43 587 docstring-stripped AST nodes** and **903 docstring hosts** in **both** states — no definition was added or removed (INV-D / INV-J) — while docstrings stripped go **628 → 859 (+231)** from `45aa61c` to the final state. The step brief's "266 nodes" is not reproducible from the script (it prints only the digest); the measured figures above supersede it.

### Working tree

`git status --porcelain` after the gate runs: `M uv.lock` — the stale-lock rewrite of finding **F-9**, forced by `uv run`, not an artifact of this change. Restored with `git restore uv.lock` before this commit and not staged.

**S5.2 gate: PASS** on all seven checks — lint with `D` selected over `src/`, format, types, strict docs build, the AC-009 docstring test, the AST digest with its control run, and deptry. Every value equals its S4.1 baseline.

**Next (S5.3):** update `docs/verification/traceability.md` for the IDs this change touches.

## Phase 5 — S5.3 traceability (2026-10-09)

Objective: add/update matrix rows for the IDs this change actually touches. No source or test file was edited; the writes are this section and `docs/verification/traceability.md`.

**Normative-basis correction to the step brief.** The brief names `docs/specs/docstring-guidance.md` as this change's spec. **No such file exists** (measured: `ls docs/specs/` — authentication, event-bus, file-management, logging-coverage, logging, mail-service, search, session-management, settings-coverage, settings-public-registry-setter, settings, structlog-logging, structure-map, template, user-management, user-roles-permissions), and none is expected: `ruff-d-docstrings` is **DOCS/CHORE**, a type that produces **no spec** (AGENTS.md Phase Matrix), so it defines no `REQ`/`AC`/`INV`/`EDGE`/`NFR` IDs of its own. Its normative basis is this record (§"Exact change scope", §"Invariants that MUST hold"). The rows therefore cover only the spec IDs the S5.1/S5.2 evidence reaches, plus the change's own gate as no-spec-ID rows.

### Rows added (new section `## Chore: ruff-d-docstrings (docstring gate — Phase 5 S5.3, 2026-10-09)`, 3 rows, +10 matrix lines)

| Row | Spec / ID | Evidence cited (already recorded, not re-measured) |
|---|---|---|
| Traced-class docstring wording intact (INV-A) | `logging-coverage.md` REQ-009 / AC-009 | S5.2 gate 5 `1 passed in 0.42s` (`test_traced_class_docstrings_mention_tracing`) + green inside the S5.1 acceptance run `364 passed, 1 skipped` |
| The new docstring lint gate itself | — (chore, no spec ID) | S5.2 gate 1 `uv run ruff check .` → `All checks passed!` with `D` selected over `src/` and exactly the four exempt trees; group-11 targeted `D` re-check → 0 of the 328 sites remain; commit `16332dc` |
| No-behavior-delta of the whole change (INV-D) | — (chore, no spec ID) | S5.2 gate 6 digest `64fc1d6e…` == baseline + the control run (docstring SAME, one-character code change DIFFERENT) + the 84 files / 43 587 nodes / 903 hosts counts; S5.1 `761 passed, 1 skipped` |

**No existing row was rewritten or refreshed** (decision Q-129, convention B). The pre-existing `logging-coverage` row `REQ-009 | AC-009 | test_traced_class_docstrings_mention_tracing | GREEN` is untouched — re-run GREEN at S5.2 gate 5, but the record written by the change that observed it stands; the new row is the dated record of *this* gate.

**IDs deliberately NOT touched.** `settings-public-registry-setter.md` REQ-013 / AC-018 / NFR-004 constrain `[tool.ruff.lint] select` — the very table this change's config commit edited — so their half of the evidence (`ruff check .` clean, `mypy src/` clean, `TID251` still selected) is re-verified at S5.2 gates 1 and 3. Their rows stay `PENDING (settings-public-registry-setter P.4, 2026-10-06)` because this change has **no witness** for them: `grep -rn "def test_ac_018_ruff_bans_private_slot_import\|def test_nfr_004_ruff_and_mypy_clean" tests/` → no match (that change's Phase 3 has not run), and a matrix row may not cite a test function that does not exist (`check_traceability.py` rule 3). Same reasoning for `structure-map.md` NFR-004 — its witness does not exist and this change did not touch the map renderer.

### Referential-integrity check (`scripts/check_traceability.py`)

```text
before (this step's start, 822 rows):
Traceability: PASS (822 matrix rows, 136 spec IDs, 746 test functions)

after (3 new rows):
Traceability: PASS (825 matrix rows, 136 spec IDs, 746 test functions)
```

Exit code 0 both runs. Row count +3, spec-ID and test-function counts unchanged — no new ID reference and no new test reference.

**File sizes.** `docs/verification/traceability.md` 1028 → 1038 lines (+10: 1 section heading + 1 intro paragraph + blank lines + the 6-line table). `docs/verification/ruff-d-docstrings.md` 1254 → 1290 lines (+36, this section).

**Working tree.** `git restore uv.lock` before committing; `uv.lock` not staged (finding **F-9**).

**Next (S5.4):** the Phase 5 verification report (spec coverage for a DOCS/CHORE change = the scope items and INV-A…INV-J against the final diff).

## Phase 5 — Verification report (S5.4, 2026-10-09)

Objective: close Phase 5 with the DOCS/CHORE verification report. **No source or test file was edited in this step** — the writes are this section, one clarifying sentence in §No-behavior-delta proof plan (P-88), and two `docs/workflow/PROBLEMS.md` entries (P-87, P-88). The Phase 5 gates themselves are **not re-run here**: S5.1 (suite), S5.2 (seven quality gates) and S5.3 (traceability) recorded them; the only new measurements below are cheap `git diff` facts read off the final state, needed to prove the scope and invariant claims.

### Coverage basis: **scope coverage**, not spec coverage

`ruff-d-docstrings` is **DOCS/CHORE**, a type that produces **no specification** (AGENTS.md Phase Matrix) and therefore **defines no `REQ`/`AC`/`INV`/`EDGE`/`NFR` IDs of its own** — there is no spec file for it in `docs/specs/` and none is expected (see the §Phase 5 — S5.3 normative-basis correction). The `INV-A … INV-J` labels used below are **this record's own invariant labels**, not spec IDs, and no ID is invented to fill a coverage column.

So the S5.4 done-criterion "spec coverage = 100%" (verify skill) is **n/a for this type**. Its DOCS/CHORE equivalents are: (a) *every scoped item of §"Exact change scope" landed, and nothing outside the scope was touched*; (b) *every invariant of §"Invariants that MUST hold" holds*; (c) *no test file or behavior was touched* (AGENTS.md Phase 5, DOCS/CHORE item 16). The ID-level referential-integrity gate that does apply — `uv run python scripts/check_traceability.py` → **PASS (825 matrix rows, 136 spec IDs, 746 test functions)**, exit 0 — is recorded at S5.3.

### Diff reality check (final state vs. base `45aa61c`)

| Measurement | Result |
|---|---|
| `git diff --name-only 45aa61c..HEAD \| wc -l` | **48 files**: 41 under `src/` + 4 config/guidance files + 3 record files |
| Record files (not scope items) | `docs/verification/ruff-d-docstrings.md`, `docs/verification/traceability.md`, `docs/workflow/PROBLEMS.md` — the change's own Phase 4/5 artifacts (normative basis, the S5.3 matrix rows, the Problem Log) |
| `git diff --name-only 45aa61c..HEAD -- tests/` | **empty** — zero files under `tests/` (INV-B) |
| `git diff --shortstat 45aa61c..HEAD -- src/` | **41 files changed, 1264 insertions(+), 217 deletions(-)** |
| `git diff --name-status --find-renames 45aa61c..HEAD -- src/` | **no `A`/`D`/`R` entries** — 0 files added, deleted or moved (INV-J) |
| `git diff 45aa61c..HEAD -- src/ \| grep -E "^[+-][[:space:]]*(import \|from … import)"` | **0 added or removed import statements** (INV-J) |
| `git diff 45aa61c..HEAD -- src/ \| grep -c noqa` | **0** (INV-C) |
| **Out-of-scope files touched** | **none** |

### Scoped items — **45 / 45 DONE**

Every file of §"Exact change scope" items 1–5, with the commit that landed it (`add` = docstring additions, `fmt` = the separate formatting commit, Q-11):

| Group | Scoped item | Commit(s) | Status |
|---|---|---|---|
| 1 `eventbus` | `src/backend/eventbus/eventbus.py` | `1560bfc` (add: D105 ×2, D107 ×1) | **DONE** |
| 2 `logging` | `src/backend/logging/_decorator.py` | `a7894c8` (fmt: D205, D209) | **DONE** |
| 3 `mail` | `src/backend/mail/errors.py` | `b96ad16` (add) | **DONE** |
| 3 `mail` | `src/backend/mail/models.py` | `b96ad16` (add) | **DONE** |
| 3 `mail` | `src/backend/mail/service.py` | `b96ad16` (add) | **DONE** |
| 3 `mail` | `src/backend/mail/transport.py` | `b96ad16` (add) | **DONE** |
| 4 `sessionmanagement` | `src/backend/sessionmanagement/events.py` | `e3f95c6` (add) | **DONE** |
| 4 `sessionmanagement` | `src/backend/sessionmanagement/search_source.py` | `df45d17` (fmt) | **DONE** |
| 4 `sessionmanagement` | `src/backend/sessionmanagement/service.py` | `e3f95c6` + `df45d17` | **DONE** |
| 5 `settings` | `src/backend/settings/registry.py` | `899c027` + `2284b71` | **DONE** |
| 5 `settings` | `src/backend/settings/repository.py` | `899c027` + `2284b71` | **DONE** |
| 6 `permissions` | `src/backend/permissions/catalog.py` | `9bd979a` + `5d5a18f` | **DONE** |
| 6 `permissions` | `src/backend/permissions/errors.py` | `9bd979a` | **DONE** |
| 6 `permissions` | `src/backend/permissions/events.py` | `9bd979a` | **DONE** |
| 6 `permissions` | `src/backend/permissions/models.py` | `9bd979a` + `5d5a18f` | **DONE** |
| 6 `permissions` | `src/backend/permissions/repositories.py` | `9bd979a` + `5d5a18f` | **DONE** |
| 6 `permissions` | `src/backend/permissions/service.py` | `9bd979a` + `5d5a18f` | **DONE** |
| 7 `authentication` | `src/backend/authentication/errors.py` | `98b5dbc` | **DONE** |
| 7 `authentication` | `src/backend/authentication/events.py` | `98b5dbc` | **DONE** |
| 7 `authentication` | `src/backend/authentication/repositories.py` | `cb45758` (fmt: D205) | **DONE** |
| 7 `authentication` | `src/backend/authentication/repository.py` | `98b5dbc` | **DONE** |
| 7 `authentication` | `src/backend/authentication/service.py` | `98b5dbc` | **DONE** |
| 7 `authentication` | `src/backend/authentication/tracker.py` | `98b5dbc` | **DONE** |
| 7 `authentication` | `src/backend/authentication/webauthn.py` | `98b5dbc` | **DONE** |
| 8 `filemanagement` | `src/backend/filemanagement/errors.py` | `dd8bbd5` | **DONE** |
| 8 `filemanagement` | `src/backend/filemanagement/events.py` | `dd8bbd5` | **DONE** |
| 8 `filemanagement` | `src/backend/filemanagement/repository.py` | `dd8bbd5` + `c46a07e` | **DONE** |
| 8 `filemanagement` | `src/backend/filemanagement/search_source.py` | `c46a07e` (fmt) | **DONE** |
| 8 `filemanagement` | `src/backend/filemanagement/service.py` | `dd8bbd5` + `c46a07e` | **DONE** |
| 8 `filemanagement` | `src/backend/filemanagement/storage.py` | `dd8bbd5` | **DONE** |
| 9 `search` | `src/backend/search/errors.py` | `f0a2fcc` + `b02eefc` | **DONE** |
| 9 `search` | `src/backend/search/events.py` | `f0a2fcc` + `b02eefc` | **DONE** |
| 9 `search` | `src/backend/search/models.py` | `b02eefc` (fmt) | **DONE** |
| 9 `search` | `src/backend/search/service.py` | `f0a2fcc` + `b02eefc` | **DONE** |
| 10 `usermanagement` | `src/backend/usermanagement/errors.py` | `1040a76` | **DONE** |
| 10 `usermanagement` | `src/backend/usermanagement/events.py` | `1040a76` | **DONE** |
| 10 `usermanagement` | `src/backend/usermanagement/models.py` | `1040a76` + `39e4904` | **DONE** |
| 10 `usermanagement` | `src/backend/usermanagement/repository.py` | `1040a76` + `39e4904` | **DONE** |
| 10 `usermanagement` | `src/backend/usermanagement/role_store.py` | `1040a76` | **DONE** |
| 10 `usermanagement` | `src/backend/usermanagement/search_source.py` | `39e4904` (fmt) | **DONE** |
| 10 `usermanagement` | `src/backend/usermanagement/service.py` | `1040a76` + `39e4904` | **DONE** |
| 11 config | `pyproject.toml` — `select += "D"`, `fixable` widening, `[tool.ruff.lint.pydocstyle] convention = "google"`, `per-file-ignores` for exactly the four decided trees | `16332dc` | **DONE** |
| 11 config | `mkdocs.yml` — explicit `docstring_style: google` pin (inert, F-8) | `16332dc` | **DONE** |
| 11 config | `.pre-commit-config.yaml` — `rev: v0.15.12` → `v0.16.10` (F-6) | `16332dc` | **DONE** |
| 11 guidance | `AGENTS.md` §General Code & Style Conventions — the single "Documentation" bullet extended with the Google-style / ruff-`D` / no-filler convention (1 line replaced by 1 line, prose only, Q-24) | `16332dc` | **DONE** |

§"Explicitly **not** touched" is confirmed by the diff reality check above: no `userdocs/` path, no `tests/`/`scripts/`/`migrations/`/`.github/hooks/` path, no spec/ADR/DAG file, no `pyproject.toml` version line, no `python-best-practices` skill file appears in `git diff --name-only 45aa61c..HEAD`.

### Invariants — **10 / 10 HELD**

| INV | Statement (abridged) | Verdict | Gate / evidence |
|---|---|---|---|
| INV-A | traced-class docstrings keep the "traced"/"logged" wording | **HELD** | S5.2 gate 5 `test_traced_class_docstrings_mention_tracing` → `1 passed in 0.42s`; green inside the S5.1 acceptance run (`364 passed, 1 skipped`) |
| INV-B | no test file added/removed/weakened; diff touches no `tests/` path | **HELD** | `git diff --name-only 45aa61c..HEAD -- tests/` empty (this step); collected count identical at 762 and the skip set identical (S5.1) |
| INV-C | no `# noqa`; `per-file-ignores` gains exactly the four decided trees | **HELD** | `grep -c noqa` over the `src/` diff → 0; `pyproject.toml:220-224` lists `tests/*`, `scripts/*`, `migrations/*`, `.github/*` and nothing else (S5.2 gate 1) |
| INV-D | executable code identical | **HELD** | AST digest `64fc1d6ee758…57d7bec0` unchanged at the final commit, with the non-vacuity control run (docstring SAME / one-character code change DIFFERENT) and the 84 files / 43 587 stripped nodes / 903 hosts counts equal in both states (S5.2 gate 6) |
| INV-E | no version bump | **HELD** | `git diff 45aa61c..HEAD -- pyproject.toml` contains **no** `version` line — `[project] version` and `[tool.bumpversion] current_version` untouched (`1.0.0`) |
| INV-F | no new dependency, no dependency-range change | **HELD** | the same diff contains no dependency line; the only version move is the pre-commit hook `rev: v0.15.12` → `v0.16.10`; `deptry .` → `Success! No dependency issues found.` (S5.2 gate 7) |
| INV-G | no-filler rule (no docstring restating its signature) | **HELD** (review item) | Not gate-checkable (Q-15 b rejected). Every Phase 4 group record states the fact each new docstring adds beyond its signature; **Phase 6 review is the confirming check** |
| INV-H | private helpers in touched files documented | **HELD** (review item) | Beyond `ruff check --select D src`; recorded per group in the Phase 4 sections (e.g. groups 1–3: `_handler_name`, `_ensure_worker_unlocked`, `_worker_loop`, `_dispatch`, `_get_transport`, `_publish`); **Phase 6 review is the confirming check** |
| INV-I | spec IDs stay cited inside docstrings | **HELD** | Measured on the final diff: unique spec IDs cited in `src/` **91 at `45aa61c` → 100 at HEAD**, and `comm -23` of the two sets is **empty** — no citation was lost |
| INV-J | feature boundaries / architecture rules unchanged | **HELD** | 0 added/deleted/renamed files, 0 added or removed import statements in the `src/` diff; the digest's 84 files / 903 docstring hosts are identical in both states |

### Gate summary (Phase 5, DOCS/CHORE light gate)

| # | Gate | Command | Result | Verdict |
|---|---|---|---|---|
| 1 | Full suite reproduced | `uv run pytest tests/ -q` | `761 passed, 1 skipped in 230.83s` (762 collected; the single S4.1 failure = the known NFR-001 load flake, green in isolation at both commits) | **PASS** (S5.1) |
| 2 | Acceptance | `uv run pytest tests/acceptance/ -q` | `364 passed, 1 skipped` | **PASS** (S5.1) |
| 3 | Property | `uv run pytest tests/property/ -q` | `71 passed` | **PASS** (S5.1) |
| 4 | Contract | `uv run pytest tests/contract/ -q` | `51 passed` | **PASS** (S5.1) |
| 5 | Lint **with the new gate** (CI parity) | `uv run ruff check .` | `All checks passed!` (exit 0) — `D` selected over `src/`, 0 findings | **PASS** (S5.2) |
| 6 | Format | `uv run ruff format --check .` | `339 files already formatted` | **PASS** (S5.2) |
| 7 | Types | `uv run mypy src/` | `Success: no issues found in 84 source files` | **PASS** (S5.2) |
| 8 | Published site builds | `uv run --group docs mkdocs build --strict` | `Documentation built in 2.05 seconds` (exit 0) | **PASS** (S5.2) |
| 9 | INV-A / AC-009 wording | `uv run pytest tests/acceptance/logging_coverage/test_docstrings.py::test_traced_class_docstrings_mention_tracing -q` | `1 passed in 0.42s` | **PASS** (S5.2) |
| 10 | INV-D executable code identical | `uv run python "$LOCALAPPDATA/Temp/s41_ast_digest.py" src` | `64fc1d6ee758bf6ac572d58b100eff95d4bbd1205c993f7d9e2e126657d7bec0` == baseline, control run non-vacuous | **PASS** (S5.2) |
| 11 | Dependencies (config commit edited `pyproject.toml`) | `uv run deptry .` | `Success! No dependency issues found.` | **PASS** (S5.2) |
| 12 | Traceability referential integrity | `uv run python scripts/check_traceability.py` | `PASS (825 matrix rows, 136 spec IDs, 746 test functions)`, exit 0 | **PASS** (S5.3) |
| 13 | Worktree clean | `git status --porcelain` | empty after `git restore uv.lock` (the F-9 churn is never staged) | **PASS** |

### Findings disposition (F-1 … F-17)

| # | Disposition |
|---|---|
| F-1 | **Recorded.** The TODO's "379 errors" is superseded by the fresh measurement (398 bare / **328** under google); Phase 4 worked from the fresh table. TODO text left as the historical record. |
| F-2 | **Recorded, no action.** The "156 of 515 public defs" claim (from `pyproject-tooling-gaps`) is not reproducible under any `D` rule; the governing figure here is the 198-site missing-docstring family. Belongs to that other record, not this change. |
| F-3 | **Recorded.** 41 `@logged_class` classes (not 45), 19 asserted by AC-009; INV-A measured and gated on the true figures (gate 9). |
| F-4 | **Recorded.** The per-feature `D1xx` split is corrected (usermanagement 47, permissions 33); the Phase 4 commits match the corrected table (`1040a76` D1xx ×47, `9bd979a` ×33). |
| F-5 | **Recorded, then superseded by F-10.** The format family is 130 sites, not 123 — and none of them turned out to be auto-fixable. |
| F-6 | **Fixed.** `.pre-commit-config.yaml` `rev: v0.16.10` — Q-28's stated intent ("match the dev pin") applied to the measured pin, not its stale number. Landed in `16332dc`. |
| F-7 | **Recorded, out of scope.** `tests/` = 827 bare / 743 google; the sibling change `docstrings-tests` must re-measure at its own P.4. |
| F-8 | **Recorded; the pin landed as measured.** `mkdocs.yml` gains the explicit `docstring_style: google` (4 lines) and is inert by definition — the rendering delta comes from the docstrings, and gate 8 confirms the site still builds. |
| F-9 | **Recorded + worked around at every step; the fix is NOT in this change.** Every `uv run` rewrote `uv.lock`; each step ran `git restore uv.lock` and never staged it. Measured at the final state: `uv.lock` is **absent** from `git diff --name-only 45aa61c..HEAD`, so the one-line refresh P-74 folded into this config commit has not landed here. **Follow-up for Phase 6:** keep the stale-lock refresh as a separate one-line chore TODO (or fold it into the S6.4 bump checklist) rather than re-opening this change's scope. |
| F-10 | **Recorded; the §"Mechanical vs manual split" claim is wrong and was corrected in place.** `D209`/`D403` (and `D205`) offer **no** autofix in ruff 0.16.10 — probed with `--fix --diff` in groups 4, 5, 8, 9 (empty diffs). All 130 format sites were hand-edited; the `fixable` widening in `pyproject.toml` still lands as decided (it is a forward-looking allowance, not a used fix). |
| F-11 | **Recorded; ISSUE candidate.** `AuthService._publish` does not catch a publisher exception, so a raising publisher propagates — `AGENTS.md` promises the opposite for authentication, the spec does not. Docstring states the actual behavior; no code touched. |
| F-12 | **Recorded; ISSUE candidate.** `SqliteFileRepository.list_by_namespace` interpolates the namespace into a SQL `LIKE` pattern with no escape character and `FileService.list_files` does not validate `namespace`, so `_` acts as a wildcard against REQ-014's prefix match. Documented as-is. |
| F-13 | **Recorded; ISSUE candidate** (same family as F-11) — `FileService._publish` propagates a publisher failure; `AGENTS.md` over-promises for file-management. |
| F-14 | **Recorded; ISSUE candidate** (same family) — `SearchService._publish` likewise; `AGENTS.md` calls the search events "best-effort". **F-11/F-13/F-14 are one shared ask:** either the guidance or the four `_publish` implementations (mail included) must change — a separate ISSUE, not this chore. |
| F-15 | **Recorded; separate ISSUE/FEATURE candidate.** `docs/specs/search.md` v4 adds REQ-024 `set_search_service()` (AC-038…AC-041, EDGE-022/EDGE-023), but no such function exists in `src/` and no test references it. No docstring claims it exists; nothing was added. |
| F-16 | **Recorded; guidance follow-up.** `UserManager.remove_role` and `_validate_roles` raise bare `ValueError` outside the `UserManagerError` hierarchy that `AGENTS.md` presents as the whole surface. Code matches its spec (user-roles-permissions REQ-026); the docstrings say so. |
| F-17 | **Recorded; spec-drift follow-up.** `docs/specs/user-management.md` REQ-006 / AC-008 / AC-009 and the `AGENTS.md` user-management section are stale against the user-roles-permissions REQ-026 amendment. Docstrings describe the code as it is; the amendment is a separate change. |

**No finding is open against this change.** Every F-item is either fixed (F-6), corrected in the record (F-1…F-5, F-7, F-8, F-10), or escalated out of this change's scope (F-9, F-11…F-17). The ISSUE candidates Phase 6 must record as follow-ups: **the publisher-failure guidance mismatch (F-11/F-13/F-14 + mail), the SQL `LIKE` wildcard (F-12), and the unimplemented `set_search_service()` (F-15)**; the guidance/spec-drift candidates F-16, F-17 and the stale-lock chore F-9 are lower-priority follow-ups.

### Verdict

**PHASE 5 VERIFIED.** Scope coverage 45/45 DONE, invariants 10/10 HELD (INV-G/INV-H are review items and are confirmed at Phase 6), 13/13 gates PASS, zero files under `tests/` and zero out-of-scope files touched, `check_traceability.py` exit 0. Spec coverage is n/a (DOCS/CHORE defines no IDs) and is **not** substituted by code coverage. AGENTS.md Phase 5 DOCS/CHORE item 16 — "run lint and type checks where applicable; confirm no test files or behavior were touched" — is satisfied by gates 5–7 and the diff reality check.

**Next (S6.1):** review against the normative basis — this record (§"Exact change scope", §"Invariants that MUST hold"), the final code state, and the INV-G / INV-H review checklist items; record the F-9/F-11/F-12/F-13/F-14/F-15/F-16/F-17 follow-ups.

## Phase 6 — S6.1 review vs the normative basis (2026-10-09)

Objective (review skill, S6.1): does the change implement what its normative basis says — **no more, no less**? For DOCS/CHORE the normative basis is this record's §"Exact change scope" + §"Invariants that MUST hold", and the test is AGENTS.md Phase 6 check 6 / review-skill MUST: *no behavior, test, or source-behavior change beyond the scoped non-behavior changes*. Inputs: the **final state** (`45aa61c..HEAD`, 48 files) — not the commit-by-commit diff (P-27); the config/guidance files read hunk by hunk; 14 `src/` files sampled (of 41), chosen to cover add-only, fmt-only, protocol/ABC stubs, and the largest file. **No test was re-run** (Phase 5 owns the gate); the only new measurements are `git diff` facts and one independent re-run of the docstring-stripped AST digest. S6.2 (traceability + boundaries) is **not** done here.

### Check-by-check

| # | Check | Evidence (measured at HEAD `ee3f87f`) | Severity | Resolution / action |
|---|---|---|---|---|
| 1 | **Scope conformance** — every changed file inside the scoped set; nothing outside it; zero `tests/` files | `git diff --name-only 45aa61c..HEAD` → **48 files** = 41 `src/` + 4 config/guidance (`pyproject.toml`, `mkdocs.yml`, `.pre-commit-config.yaml`, `AGENTS.md`) + 3 record files. `-- tests/` → **0 files**; `--find-renames -- src/` → **no `A`/`D`/`R`**; no `userdocs/`, `scripts/`, `migrations/`, `.github/`, spec, ADR or DAG path in the list. All 41 `src/` files appear in the §Scoped-items table (45/45 DONE) | **NOTE (N-1)** | The three record files (`docs/verification/ruff-d-docstrings.md`, `docs/verification/traceability.md`, `docs/workflow/PROBLEMS.md`) are **not** listed in §"Exact change scope", whose heading says "nothing else is touched". They are workflow-mandated (the S5.3 matrix rows, the Problem Log, this record) and were disclosed at Phase 5 as "Record files (not scope items)". No action — the scope heading is stricter than the workflow; S6.3 accepts it as-is |
| 2 | **No behavior delta beyond docstrings/comments** — config is exactly what the scope prescribes; no other ruff rule, lint setting or dependency | `pyproject.toml` diff is **3 hunks, +11/−0**: `+    "D",  # pydocstyle — docstrings (google convention; src/ only, see per-file-ignores)` in `select`; `+    "D204", "D207", "D208", "D209", "D211", "D212", "D403",  # docstring layout, always-fixable (Q-12)` in `fixable`; and `+[tool.ruff.lint.pydocstyle] convention = "google"` + `+[tool.ruff.lint.per-file-ignores]` with exactly `"tests/*"`, `"scripts/*"`, `"migrations/*"`, `".github/*"` = `["D"]`. No `version`, no dependency line, no other rule/setting. `mkdocs.yml` = **+4/−0** (`handlers.python.options.docstring_style: google`). `.pre-commit-config.yaml` = **1 line**: `-    rev: v0.15.12` / `+    rev: v0.16.10`. `AGENTS.md` = **1 line → 1 line**. `src/`: the docstring-stripped AST digest was **re-measured independently in this step** — `uv run --no-sync python …/s41_ast_digest.py src` → `64fc1d6ee758bf6ac572d58b100eff95d4bbd1205c993f7d9e2e126657d7bec0`, **identical** to the `45aa61c` baseline → INV-D/INV-J hold on the final state (not re-asserted from S5.2). 0 real import statements added/removed (the three `^[+-]\s*from` hits are docstring prose) | **PASS** | None. INV-E (no version bump) and INV-F (no dependency change) confirmed directly off the same hunks |
| 3 | **Escape hatches** — no new `noqa`, `# type: ignore`, `--unsafe-fixes`, no inline rule disable | `git diff 45aa61c..HEAD -- src/ pyproject.toml mkdocs.yml .pre-commit-config.yaml AGENTS.md \| grep -n "noqa\|type: ignore\|unsafe-fixes\|ruff: noqa"` → **no match (exit 1)**. Every `noqa`/`unsafe-fixes` hit in the full diff is prose inside this record. `per-file-ignores` gained exactly the four decided trees — no `src/` exemption (INV-C) | **PASS** | **NOTE (N-2)**: the pre-existing `# nosec B105` comments in `src/backend/usermanagement/feature_actions.py` are Bandit suppressions, not ruff's, and that file is **not** in this diff — untouched, out of scope, no action |
| 4 | **Docstring quality (sampled 14 of 41)** — does each docstring state what the code actually does (Q-26: code as it is, not as the guidance wishes) | Sampled: `eventbus/eventbus.py`, `logging/_decorator.py`, `authentication/events.py`, `permissions/repositories.py`, `permissions/events.py`, `permissions/models.py`, `search/service.py`, `search/events.py`, `settings/repository.py`, `filemanagement/storage.py`, `filemanagement/repository.py`, `filemanagement/events.py`, `usermanagement/service.py` (largest), `usermanagement/search_source.py`. Claims checked against code: `EventBus.__init__` fallback **1000** + lazy worker (`eventbus.py:63-66`, `_ensure_worker_unlocked()` inside `publish`); `UserManager.__init__` → `StaticRoleStore(("admin", "user"))` (`service.py:101`); `remove_role` raises a **bare `ValueError`** on emptying the list (`service.py:283`) and is **not** a `UserManagerError` (F-16 stated as-is); `verify_password` catches `Argon2Error` → `False` (`service.py:224-226`); `set_role` is the `set_roles([role])` shim and `set_roles`/`add_role`/`remove_role` are **absent from the catalog** (`feature_actions.py:23-33` registers `set_role` only) — the docstring claim is true; `_SqliteRepository.__init__` "the migration seeds the built-in roles and the bootstrap system set" → `migrations/versions/d94b7f2e6a31_…py:5-6,100-127`; `LoginFailed` is always `method="password"` — the only three publish sites are `authentication/service.py:241,249,254`; `LocalDiskStorageBackend.exists` swallows the containment error → `False`, `unlink(missing_ok=True)` on a non-file → `reason='io'`; `list_by_namespace` interpolates `LIKE` **without escaping** and `NAMESPACE_PATTERN` (`models.py:95`) allows `_`, while `FileService.list_files` validates only `limit`/`offset` (`service.py:845-848`) — F-12 stated as-is; `_is_identical_source` compares the query function **by identity** (`is not`); the three `EventPublisher.publish` protocol stubs state that a raising publisher **propagates** (F-11/F-13/F-14) and keep their `...` body. **No docstring asserts behavior the code does not have** | **MINOR (M-1)** | `src/backend/logging/_decorator.py:_is_private_method` — "The second signal is a name containing ``...private``" while the code tests `"private" in name`. Read literally it describes a check the code does not perform; read as intended (the record's ellipsis shorthand, inherited from the base wording "or named ``...private``") it is correct. **Not a BLOCKER**: the verb "containing" matches `in`, and no false behavior is asserted about the feature. Fix (one word, S6.3 decision): "a name containing ``private``" |
| 5 | **`__init__.py` re-export modules** — `__all__` and imports unchanged | No `__init__.py` appears in the 48-file diff; `git diff 45aa61c..HEAD -- 'src/**/__init__.py'` → **0 lines**. All 11 feature `__init__.py` files (every one of which declares `__all__`) are byte-identical to the base — spot-checked `usermanagement`, `search`, `permissions` against the base blob (no diff) | **PASS** | None — the invariant holds trivially because the re-export modules were never in scope |
| 6 | **INV-G (no filler) / INV-H (private helpers documented)** — the two Phase 5 review items Phase 6 must confirm | INV-G: in the 14 sampled files every new docstring adds something the signature does not carry (fallback values, no-op/idempotence, error kind and propagation, ordering, atomicity, who validates what) — no "Get the user."-class filler found. INV-H: private helpers in the touched files are documented (`_utcnow`, `_publish`, `_validation_failure`, `_apply_roles`, `_assert_not_last_admin`, `_str_representer`, `_free_text_matches`, `_eval_group`, `_eval_condition`, `_sort_key`, `_query`, `_is_private_method`, `_resolve_slow_threshold` companions) | **PASS** | Both Phase 5 "HELD (review item)" verdicts are **confirmed by this review** |
| 7 | **Findings disposition F-1 … F-17** — honest, complete, none recorded-but-undisposed; ISSUE candidates actionable | All 17 have a disposition row; none is recorded without one. F-6 **fixed** (`.pre-commit-config.yaml` `rev: v0.16.10`, verified in the diff); F-1…F-5/F-7/F-8/F-10 are record corrections and each correction is visible in the record (F-10's "no autofix" is re-confirmed by the `fixable` widening landing unused); F-9/F-11…F-17 escalated. The three ISSUE candidates are stated with file + function + spec ID + observed-vs-required, i.e. a TODO can be written without re-investigation: **F-11/F-13/F-14** (`AuthService._publish` `service.py:166-173`, `FileService._publish` `service.py:234-237`, `SearchService._publish` `service.py:533-539` + mail — `AGENTS.md` promises "a publisher failure never breaks the operation", the specs promise only the `None` case, the code propagates), **F-12** (`SqliteFileRepository.list_by_namespace` `repository.py:242-255` + `FileService.list_files` `service.py:829-848` vs REQ-014 prefix match), **F-15** (`docs/specs/search.md` v4 REQ-024 / AC-038…AC-041 vs no `set_search_service` in `src/`) | **NOTE (N-3)** | F-15's disposition says "a separate change (ISSUE or FEATURE)" without naming it — the separate change **already exists and is in flight**: `docs/todo/settings-public-registry-setter.md` (`Status: IN-WORKFLOW`, CROSS-CUTTING, spec merged via PR #73) specifies `set_search_service()` among the five singleton installers. **No new TODO should be opened for F-15**; the gap closes when that change lands. Record the dependency so the orchestrator does not duplicate it |
| 8 | **AGENTS.md guidance correctness** — does the edited "Documentation" bullet describe the gate as it now is | The new line: "Docstrings are **Google style** and gated by ruff `D` over `src/` (`tests/`, `scripts/`, `migrations/`, `.github/` are exempt via `per-file-ignores`); every public object in a backend package carries a docstring that states something its signature does not — filler that restates the signature ("Get the user.") is rejected in review." Matches the config exactly: rule `D` in `select`, `convention = "google"`, `src/` gated, **four** exempt trees, and the no-filler rule is a review rule (INV-G, Q-15 b rejected a scripted checker) — the wording says "rejected in review", not "gated" | **NOTE (N-4)** | The coverage clause is scoped to "every public object in a **backend package**", while the gate covers all of `src/`, including `src/main.py` (the one non-package module, already gate-clean). The sentence understates the gate's reach by one module; no action required, and Q-24 forbids touching the `python-best-practices` skill |

### Additional notes (not checks)

| # | Note | Evidence | Action |
|---|---|---|---|
| N-5 | A `src/` docstring points at a change-local record without a path: `filemanagement/repository.py:246` "(see the Q-26 finding in the change's verification record)". The substantive statement is complete without it, and the pointer will be unresolvable to a reader who does not know which change | `sed -n '242,247p'` | Optional one-line cleanup in S6.3 (name the file or drop the pointer). Not a behavior or accuracy defect |
| N-6 | `FileService._publish` and `SearchService._publish` docstrings state only the `None`-publisher case (true but narrower); the propagation claim lives in each feature's `EventPublisher.publish` protocol docstring | `filemanagement/service.py:235`, `search/service.py:534-537` vs `filemanagement/events.py:87-92`, `search/events.py:39-45` | None — this is exactly what F-13/F-14 record ("`_publish`'s own docstring keeps its original (true but narrower) claim") |
| N-7 | The follow-ups are **recorded but not scheduled**: `docs/todo/` contains no TODO for the publisher-failure guidance mismatch (F-11/F-13/F-14), the SQL `LIKE` wildcard (F-12), the stale-lock refresh (F-9), or the guidance/spec-drift items (F-16, F-17) | `ls docs/todo/` — 15 live TODOs, none of them these | **Orchestrator action before S6.4**: create the TODO files (value triage included) or record a deliberate decision not to. This is a scheduling gap, not a defect in the change |
| N-8 | Tooling note for future steps re-running the digest: the system `python` on PATH is 3.12 and **cannot parse** `src/backend/logging/_decorator.py:46` (`except TypeError, ValueError:` — PEP 758, Python 3.14 syntax). Run it as `uv run --no-sync python <script> src` — `--no-sync` also keeps `uv.lock` untouched (F-9) | digest run under 3.12 → `SyntaxError: multiple exception types must be parenthesized`; under the project env → the baseline digest | Worth a line in the next change's record; not a code finding |

### Verdict

**Normative basis: COMPLIANT — no more, no less.** The change is exactly its scope: 41 `src/` files of docstrings/formatting, four config/guidance files matching the prescribed content line for line, and the change's own records. Zero `tests/` files, zero escape hatches, zero added/removed/renamed files or imports, and the executable code is provably identical (digest re-measured here, not quoted). Every sampled docstring states the code as it is — including the three places where that contradicts `AGENTS.md` (F-11/F-13/F-14) and the one where it contradicts the guidance's error hierarchy (F-16). INV-G and INV-H, the two items Phase 5 could only claim provisionally, are **confirmed**.

**BLOCKERS 0 / MINORS 1 / NOTES 8**

- **M-1** — `logging/_decorator.py` `_is_private_method` docstring wording (`"...private"` vs `"private" in name`): one-word fix, S6.3 decides fix-or-accept.
- **N-1** record files outside the literal scope heading (workflow-mandated, already disclosed); **N-2** pre-existing Bandit `# nosec` untouched; **N-3** F-15 already covered by the in-flight `settings-public-registry-setter` — do not open a duplicate TODO; **N-4** AGENTS.md coverage clause omits `src/main.py`; **N-5** path-less record pointer inside a `src/` docstring; **N-6** `_publish` docstrings narrower than the protocol docstring (as recorded); **N-7** follow-ups recorded but no TODO files exist yet — orchestrator action before S6.4; **N-8** digest re-run needs the project interpreter (`uv run --no-sync`).

**Next (S6.2):** traceability + boundaries — the S5.3 matrix rows (`docs/verification/traceability.md`, +10/−0), feature boundaries and the architecture rules (AGENTS.md Phase 6 checks 2–4).
