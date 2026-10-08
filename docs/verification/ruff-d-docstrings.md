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

Run it with the **relative** `src` root in each worktree (the digest includes the file paths, so an absolute root would make the two sides incomparable).

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
