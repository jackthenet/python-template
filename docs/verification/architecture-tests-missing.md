# architecture-tests-missing — Scope Record (DOCS/CHORE)

Phase P / **P.4 Draft** artifact for the change `architecture-tests-missing`.

- **Change:** architecture-tests-missing · **Type:** **DOCS/CHORE** (Phase 0 classification at P.1, confirmed by the P.2 classification verdict and by Q-1)
- **Classification rationale (first matching criterion, `AGENTS.md` Change Types table):** criterion 5 — "does not alter behavior: documentation, comments, configuration, CI, tooling". The change (a) removes four process citations that name an executable which does not exist in this repository and re-points the architecture check at the **manual** boundary review `AGENTS.md` Phase 6 checks 3–4 already define, and (b) rewrites 3 imports of a feature's **private** module to that feature's **public** API — the same object reached by a different import path. Not an ISSUE: no file in `docs/specs/` requires architecture tests or states a boundary rule the missing directory could violate (P.2 E-5), so there is no deviation from approved spec behavior. Not FEATURE: nothing externally observable is added. Not CROSS-CUTTING: no product feature's interface changes. Not REFACTOR: no existing code is restructured — an import path is not a structure change.
- **Branch / worktree:** `chore/architecture-tests-missing` @ base commit **`99ce0b8d652b6f4bc2f1f52ddba734b3cd717795`** (`main`, "chore(workflow-docs-nits): status WAITING (PR #64 open) + Phase 6 recorded") in `../python-template_kopie-worktrees/chore/architecture-tests-missing`
- **Phase Matrix for this type:** Phase 1 scope (this file) · Phase 2/3 skipped · Phase 4 make the scoped change · Phase 5 lint + types + the regression evidence required because `src/` is touched · Phase 6 light review + PR. No spec, no spec PR, **no version bump** (DOCS/CHORE → none, `AGENTS.md` Versioning).
- **Questions:** all 6 ANSWERED (`docs/questions/architecture-tests-missing.md`) — Q-1 = (a), Q-6 = (a2), Q-4 = (a) manual only, Q-5 = fold the import fixes in, Q-3 = land independently, Q-2 = moot.
- **Date:** 2026-10-04

## Scope summary

| # | Item | Kind | File | Shape |
|---|------|------|------|-------|
| 1 | Remove the dangling `tests/architecture/` citation from the Phase Matrix REFACTOR cell, re-pointed at the manual check | documentation | `AGENTS.md:212` | 1 table cell reworded |
| 2 | Remove the dangling citation from the Phase 5 REFACTOR step, re-pointed at the manual check | documentation | `AGENTS.md:579` | 1 line reworded |
| 3 | Remove the dangling citation from the `verify` skill FEATURE/CROSS-CUTTING gate list | documentation | `.agents/skills/verify/SKILL.md:88` | 1 bullet reworded |
| 4 | Remove the dangling citation from the `verify` skill REFACTOR gate list | documentation | `.agents/skills/verify/SKILL.md:103` | 1 bullet reworded |
| 5 | Import `logged` from the logging feature's public API instead of its private `_decorator` module | import hygiene | `src/backend/authentication/feature_settings.py:7`, `src/backend/eventbus/feature_settings.py:7`, `src/backend/usermanagement/feature_settings.py:7` | 3 one-line import rewrites |
| 6 | `src/main.py:67` private `_registry` import | **finding F-1 — NOT actionable as DOCS/CHORE** | `src/main.py:67` | see F-1 |

The 4 doc citations and the 4 import sites were re-verified against `main` @ `99ce0b8` at P.4 and sit at the line numbers the TODO gives. Two secondary numbers quoted in the P.2 evidence had drifted and are corrected here (`AGENTS.md` "prematurely" rule: `:1145`, not `:1141`; project version: `0.6.1`, not `0.6.0`).

## Item 1 — `AGENTS.md:212` (Phase Matrix, "5 Verify" row, REFACTOR column)

**Before** (verbatim, whole line):

```markdown
| **5 Verify** | Full gate set | Targeted tests + full regression + lint/types | Full gate set **+ per-feature traceability updates** | Full regression + architecture + lint/types (no spec coverage) | Light: lint/types where applicable |
```

**After** (verbatim, whole line — only the REFACTOR cell changes; the row keeps its 6 columns):

```markdown
| **5 Verify** | Full gate set | Targeted tests + full regression + lint/types | Full gate set **+ per-feature traceability updates** | Full regression + architecture rules (manual, Phase 6 checks 3–4) + lint/types (no spec coverage) | Light: lint/types where applicable |
```

## Item 2 — `AGENTS.md:579` (Phase 5: VERIFY, **REFACTOR** step 13)

**Before** (verbatim):

```markdown
13. Run the full regression suite (MUST be GREEN, zero test changes) and the architecture rules (`uv run pytest tests/architecture/ -v`).
```

**After** (verbatim — wording mirrors the existing Phase 6 review checks 3–4 at `AGENTS.md:592-593` so the re-point does not read as a new rule):

```markdown
13. Run the full regression suite (MUST be GREEN, zero test changes) and verify the architecture rules by inspection — feature boundaries (code lives in the correct feature directory, no cross-feature internal imports) and architecture rules (`model/` contains domain concepts, `services/` contains use cases, `shared/` is deliberately small) — recording the result in `docs/verification/[name].md`. These are the same checks as Phase 6 review checks 3 and 4.
```

## Item 3 — `.agents/skills/verify/SKILL.md:88` (MUST → FEATURE / CROSS-CUTTING)

**Before** (verbatim):

```markdown
- Run architecture rules (`uv run pytest tests/architecture/ -v`) and confirm they pass.
```

**After** (verbatim):

```markdown
- Verify the architecture rules by inspection — feature boundaries (code lives in the correct feature directory, no cross-feature internal imports) and architecture rules (`model/` contains domain concepts, `services/` contains use cases, `shared/` is deliberately small) — and record the result in `docs/verification/<name>.md`.
```

## Item 4 — `.agents/skills/verify/SKILL.md:103` (MUST → REFACTOR)

**Before** (verbatim — byte-identical to the Item 3 bullet):

```markdown
- Run architecture rules (`uv run pytest tests/architecture/ -v`) and confirm they pass.
```

**After** (verbatim — identical to the Item 3 after-text; the two gate lists keep the same wording):

```markdown
- Verify the architecture rules by inspection — feature boundaries (code lives in the correct feature directory, no cross-feature internal imports) and architecture rules (`model/` contains domain concepts, `services/` contains use cases, `shared/` is deliberately small) — and record the result in `docs/verification/<name>.md`.
```

**Phase 4 mechanics note:** the Items 3 and 4 bullets are byte-identical strings, so each `edit` must include a neighbouring line (e.g. the preceding bullet) to be unique in the file.

## Item 5 — the 3 private-module import rewrites (Q-5)

Verified on `main` @ `99ce0b8`: all three files import `logged` from the logging feature's **private** `_decorator` module, which `AGENTS.md:768` forbids verbatim ("Import the public API only (`from backend.logging import logged, logged_class, setup_logger, Settings, get_settings`); do not import the private `_setup` / `_decorator` modules"). `logged` **is** exported by the public API: `src/backend/logging/__init__.py` does `from backend.logging._decorator import logged, logged_class` and lists `"logged"` in `__all__`.

For each of `src/backend/authentication/feature_settings.py:7`, `src/backend/eventbus/feature_settings.py:7`, `src/backend/usermanagement/feature_settings.py:7`:

**Before** (verbatim, identical in all three files):

```python
from backend.logging._decorator import logged
```

**After** (verbatim, identical in all three files):

```python
from backend.logging import logged
```

No other line in those files changes (the `@logged(slow_threshold_ms=5)` decorator usage, the `TYPE_CHECKING` guard and the function bodies stay as they are).

## Finding F-1 — `src/main.py:67` is not a DOCS/CHORE import rewrite

Q-5 folded 4 import fixes into this change. Three are one-line rewrites; the fourth has **no public symbol to switch to**, so making it "fixed" would require new public API in the settings feature — outside this change's type.

**Current state** (verbatim, `src/main.py:67`):

```python
from backend.settings.registry import _registry as _settings_registry_singleton
```

used at `src/main.py:136-137`:

```python
_settings_registry = SettingsRegistry(permission_service=_permission_service_proxy)
_settings_registry_singleton[0] = _settings_registry
```

**Why there is no public equivalent (verified on `main`):** the settings feature's public API exposes only `get_settings_registry(required: bool = True)` (`src/backend/settings/registry.py:361`) and `reset_settings_registry()` (`:378`); `__all__` in `src/backend/settings/__init__.py` contains no setter. `get_settings_registry()` **lazily creates a default** `SettingsRegistry()` with **no** `permission_service` (`registry.py:368-373`), and `permission_service` is a constructor argument only — so replacing the private write with `get_settings_registry()` would discard the wired registry and change behavior (the composition root deliberately installs the proxy-wired instance so the other services and the feature settings registration share it). The spec confirms the surface: `docs/specs/settings.md:175` (API), `:234` REQ-014 ("`get_settings_registry()` returns a singleton … `reset_settings_registry()` resets the default for tests") — no setter is specified.

**Decision recorded here (default, no re-decision of Q-5):** the `src/main.py:67` site is **out of scope for this change** — it is not "already satisfied" (the private import is real), it is **not fixable without new public API**. Fixing it means adding a public `set_settings_registry()` (or equivalent) to the settings feature, which is a new public interface: it needs a settings-spec amendment (REQ-014) and is an ISSUE/FEATURE-or-REFACTOR change, not a DOCS/CHORE import hygiene. The same private holder is written directly by **6 test files / 9 sites** (`tests/settings_test_helpers.py`, `tests/acceptance/settings_coverage/test_setup_logger.py`, `tests/acceptance/settings_coverage/test_wiring.py`, `tests/contract/logging/test_logging_contracts.py`, `tests/property/logging/test_logging_properties.py`, `tests/unit/logging/test_logging_edges.py`), so a public setter would be the shared fix for all of them — a separate change's decision, not this one's.

**Consequence for the acceptance signal:** the change still removes the false gate and still fixes the 3 imports `AGENTS.md:768` forbids. It does **not** make the repo free of cross-feature private imports; `src/main.py:67` remains one (recorded, not hidden).

## No-behavior-delta confirmation

1. **Items 1–4 (process prose).** `AGENTS.md` and `.agents/skills/*/SKILL.md` are read by agents, not by the application: `grep -rn "AGENTS.md" src tests scripts .github` finds only prose mentions in `tests/unit/test_settings_test_isolation.py` (docstring / assertion message text — it never opens the file), and `grep -rn 'AGENTS.md"\|AGENTS.md'\|SKILL.md"\|SKILL.md'' src tests scripts .github` finds **no** code, test or CI job that reads either file as input. The change deletes a command that **errors** today (`uv run pytest tests/architecture/ -v` → `ERROR: file or directory not found: tests/architecture/`, exit 4 — P.2 E-3, reproduced on `main`) and names no new command, so no executable step is removed from any gate: the REFACTOR Phase 5 gate list keeps an architecture check, now phrased as the manual review Phase 6 checks 3–4 already perform (`AGENTS.md:592-593`; `:624` already makes respecting them a clean-review condition). No spec REQ/AC references the removed wording (P.2 E-5).
2. **Item 5 (import path only).** `from backend.logging import logged` binds the **same object** as `from backend.logging._decorator import logged`: `src/backend/logging/__init__.py` re-exports the very `logged` defined in `backend.logging._decorator` (no wrapper, no copy, no conditional export) and lists it in `__all__`. The decorator identity, its closure over `_decorator` module globals, and its behavior are unchanged.
3. **No import-cycle / initialization-order risk from the wider import.** Importing the package executes `backend/logging/__init__.py`, whose module-level imports are stdlib + `loguru` + the logging package's own submodules (`_decorator`, `_settings`, `_setup`, `feature_settings`). Every dependency on `backend.settings` / `backend.eventbus` inside those modules is **function-local** (`_settings.py:33-34`, `_setup.py:120-121`, `feature_settings.py:20,54`), so no new top-level edge is created and no cycle is possible.
4. **How Phase 5 proves it:** the full regression suite on the branch must produce the **same collected/passed count** as the same run on `main` @ `99ce0b8` (no test added, removed or weakened), `git diff --name-only main...HEAD` must contain **no** `tests/` path, and the public-API contract suites that pin the names being switched to (`tests/contract/logging/test_logging_contracts.py`, `tests/contract/settings/test_settings_contracts.py`, `tests/contract/authentication/test_public_api.py`, `tests/contract/usermanagement/test_usermanagement_contracts.py`, `tests/contract/eventbus/test_eventbus_contracts.py`) must stay GREEN. See "Phase 5 gate" below.

## Explicitly out of scope

- **No `tests/architecture/` directory** and no architecture test file (Q-1 = (a), Q-4 = (a)).
- **No CI-enforced boundary rule** — no new job, no changed workflow, no ruff `TID251` / banned-api configuration (Q-4 offered it and it was **not** taken; the 3 import fixes are therefore made but not guarded against regression).
- **No code moves** — no file is relocated, renamed or restructured; no `model/` / `services/` directory is created (`AGENTS.md:1145` forbids creating layers or directories prematurely).
- **No change to the `AGENTS.md` "Project Structure" rules or their Principles** (`AGENTS.md:1110` to end of file stays as it is), and no change to the Phase 6 review checks 3–4 themselves — they are the target of the re-point, not its subject.
- **No `src/main.py:67` fix** (finding F-1) and no new public settings-registry setter.
- **No test changes at all** (`tests/` untouched), no `pyproject.toml` / `uv.lock` / migration change, no version bump.
- **Not edited:** the frozen historical records that mention `tests/architecture/` — `docs/workflow/PROBLEMS.md` P-32, and every dated `docs/verification/*` + `docs/questions/*` record (P.2 E-1). They are records of past gates, not live guidance.

## Phase 5 gate for this type (DOCS/CHORE, but `src/` is touched → not the docs-only light gate)

Per Q-5, the change touches `src/`, so Phase 5 runs:

1. **No-behavior-delta proof — full regression suite:** `uv run pytest tests/ -v` on the branch, and the same command against `main` @ `99ce0b8`; the collected/passed counts must be **identical** and no test may be added, removed or weakened (`git diff --name-only main...HEAD` shows no `tests/` path). Record both counts in this file.
2. **Affected features' test directories** (fast targeted signal before the full run): `uv run pytest tests/acceptance/authentication tests/contract/authentication tests/integration/authentication tests/property/authentication tests/unit/authentication tests/acceptance/eventbus tests/contract/eventbus tests/integration/eventbus tests/property/eventbus tests/unit/eventbus tests/acceptance/usermanagement tests/contract/usermanagement tests/integration/usermanagement tests/property/usermanagement tests/unit/usermanagement -v` — plus the logging and settings suites, which pin the public API being imported: `uv run pytest tests/contract/logging tests/contract/settings -v`.
3. **Lint (whole repo, matches CI `.github/workflows/lint.yml`):** `uv run ruff check .` — clean.
4. **Types:** `uv run mypy src/` — clean.
5. **Traceability:** no REQ/AC is touched by this change (no spec references the removed wording, P.2 E-5), so `docs/verification/traceability.md` gets **no** new row; record that statement plus the reason in the verification report, and `uv run python scripts/check_traceability.py` must still exit 0.
6. **Verification report** in this file: pass/fail per check, with the before/after suite counts.

Phase 6 additionally: light review (scope respected, no test/source-behavior change beyond the 4 prose edits + 3 import lines), **no version bump**, PR to `main`.

## Version bump

**None.** `AGENTS.md` Versioning: DOCS/CHORE → no bump. `pyproject.toml:4` `[project] version` stays at `0.6.1`.

## Dependency / sequencing note

- **Independent of `chore/workflow-docs-nits` (PR #64, WAITING on human merge).** Different files: that change edits `.agents/skills/specify/SKILL.md` and its `AGENTS.md` restatements; this one edits `AGENTS.md:212`/`:579`, `.agents/skills/verify/SKILL.md:88`/`:103` and 3 `src/` modules. No line collision, no `Depends on:` entry.
- **`spec-interview-protocol` and `security-changelog-license` queue behind this change** (per the landing order settled at Q-3): they touch `AGENTS.md` Phase P / P.2 done-criteria and repo-level docs (`CHANGELOG`/`LICENSE`), none of them `AGENTS.md:212`/`:579` or the `verify` skill.
- **If `value-triage-gate` lands first** (it edits the Phase Matrix **"P Prepare"** row and the Phase P table — same table, different row), re-read the "5 Verify" row's REFACTOR cell wording before applying Item 1, and re-verify the line numbers.
- **`structure-map`** (WAITING, FEATURE) must **not** duplicate this work: its Q-11 asks the same "`tests/architecture/` in scope?" question and its own scope says "Do **not** reference `tests/architecture/` in the spec". This change owns the resolution (P.2 E-11).

## Premises re-verified at P.4 on `main` @ `99ce0b8`

| Premise | Check | Result |
|---|---|---|
| `tests/architecture/` does not exist | `ls -d tests/architecture` | absent (no such directory) |
| Exactly 4 live citations of the command | `grep -rn "tests/architecture" AGENTS.md .agents/` | `AGENTS.md:579`, `verify/SKILL.md:88`, `verify/SKILL.md:103` name the command; `AGENTS.md:212` names the gate as "architecture" in the Phase Matrix cell (no command) — 4 sites total, all in scope |
| No other live guidance names it | same grep, remaining hits | only frozen records (`docs/workflow/PROBLEMS.md`, `docs/verification/*`, `docs/questions/*`, incl. this change's own TODO/Q&A) — out of scope |
| `verify/SKILL.md:3` description mentions "architecture rules" | read | generic wording, no command → **no change needed** |
| `AGENTS.md:592-593` manual checks exist | read | present verbatim (check 3 = feature boundaries / no cross-feature internal imports; check 4 = `model/` / `services/` / `shared/`) and quoted in Items 2/3/4 after-text |
| line numbers from the P.2 evidence had drifted | `grep -n prematurely AGENTS.md` → `:1145` (P.2 cited `:1141`); `pyproject.toml:4` → `0.6.1` (P.2 E-12 cited `0.6.0`) | corrected in this record; the 4 citation sites and the 4 import sites are at the numbers the TODO gives |
| `AGENTS.md:768` forbids the private logging import | read | present verbatim (quoted in Item 5) |
| `logged` is public API | read `src/backend/logging/__init__.py` | re-exported from `_decorator`, in `__all__` |
| 3 `feature_settings.py` really import the private module | read each file | all three: `from backend.logging._decorator import logged` |
| `src/main.py:67` really imports a private name | read | yes — `_registry`; **no public setter exists** → F-1 |
| Settings public API has no singleton setter | read `registry.py:361-381`, `settings/__init__.py` `__all__`, `docs/specs/settings.md:175,234` | confirmed |
