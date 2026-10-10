# Questions: public-api-import-boundary

One question file per change, created at **P.1 Frame** from `docs/questions/template.md` and named `public-api-import-boundary.md`. It replaces the retired central `AI_Questions.md` (archived at `docs/questions/archive-AI_Questions.md`).

- **Change:** public-api-import-boundary (REFACTOR at P.1 — challenged by P.2, see Q-01)
- **TODO file:** `docs/todo/public-api-import-boundary.md`
- **Spec:** n/a (a REFACTOR produces none; Q-02 decides whether this change gets one)
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

## Preparation questions (P.2)

26 entries, one `BLOCKED-USER` batch, most-blocking first (Q-01…Q-05 are the gate blockers — they decide the type, the rule, and the enforcement mechanism, and the orchestrator can present them as round 1).

**Measured at `2172253` (2026-10-10), the facts every entry below is grounded in:**

- **Suite baseline:** `uv run pytest tests/ -q` → **1 failed, 815 passed, 1 skipped in 252 s**. The single failure is `tests/acceptance/test_structure_map.py::test_ac_021_committed_map_matches_fresh_render`, and it has **two independent causes**: (i) content — committed `STRUCTURE.md` says `docs/ — 223 files (process record)`, a fresh render says **224** (`git ls-files docs | wc -l` = 224); (ii) line endings — `git ls-files --eol STRUCTURE.md` → `i/lf w/crlf`, `core.autocrlf = true`, no `.gitattributes` exists, so on this host the working-tree map never byte-matches the LF render. The skipped test is `tests/acceptance/filemanagement/test_filemanagement.py:364` (symlinks unavailable on this host).
- **Package surfaces:** all **11** `src/backend/*/__init__.py` define `__all__`. Sizes: authentication 44, filemanagement 37, permissions 33, search 28, settings 27, mail 25, usermanagement 26, sessionmanagement 12, logging 8, eventbus 4, shared 3.
- **Sub-module imports** (`(from|import) backend.<pkg>.<mod>`): **266 statements in 88 files** — `src/backend/` 159 in 49 files (of which **148 same-feature** and **11 cross-feature** in 9 files), `src/main.py` 7, `migrations/env.py` 4 (all `import backend.<pkg>.models as <pkg>_models  # noqa: F401`, lines 15–18), `tests/` 96 statements / 140 imported names in 37 files, `scripts/` and `.github/` **0**.
- **The 11 cross-feature `src/backend` sites (9 files):** 7 × `from backend.permissions.catalog import PermissionCatalog` (all inside `if TYPE_CHECKING:` in the seven `feature_actions.py`: authentication:17, filemanagement:15, mail:15, search:18, sessionmanagement:15, settings:15, usermanagement:15) and 4 × `backend.authentication.models` / `.repositories` from `sessionmanagement` (`service.py:31,32`, `search_source.py:24,25`). **All 11 are already satisfiable** — `PermissionCatalog`, `Session` and `SessionRepository` are in the owning package's `__all__`.
- **Names that are NOT exported today** (would need a new re-export): `src/main.py` has 7 sub-module imports — `register_actions` from `backend.authentication.feature_actions` (:32) and `backend.filemanagement.feature_actions` (:41) are **not** in those packages' `__all__`, while the other four `feature_actions` sites (mail:45, sessionmanagement:65, settings:67, usermanagement:77) are satisfiable because `register_actions` is already exported by `backend.mail`, `backend.search`, `backend.sessionmanagement`, `backend.settings` and `backend.usermanagement` (`backend.search`'s own `register_actions` already comes from the package root at `:59`); plus `:68` `from backend.settings.registry import _registry as _settings_registry_singleton` (owned by the sibling change). In `tests/` — `LEVEL_COLORS`, `_formatter_for`, `color_for_tty` (`tests/unit/logging/test_renderers.py:18-19`, same-feature), `register_actions` ×3, `value_valid_for` ×1.
- **Test-side exemption problem:** only **14 of 96** test sub-module imports sit in a directory named after the package they import; **82 do not** — tests root 20, `logging_coverage` 43, `search` 7, `permissions` 6, `sessionmanagement` 5, `settings_coverage` 1. `tests/*_test_helpers.py` at the tests root hold 17 of them (`logging_coverage_test_helpers.py` alone 12).
- **Module-object loophole already in use:** `from backend.settings import registry as _reg_mod` at 8 real sites (`tests/contract/logging/test_logging_contracts.py:40`, `tests/property/logging/test_logging_properties.py:39`, `tests/property/logging/test_pipeline_invariants.py:65`, `tests/unit/logging/test_logging_edges.py:31`, `tests/settings_test_helpers.py:116,155,176`, `tests/eventbus_test_helpers.py:73` for `backend.eventbus`) plus one inside a subprocess source string (`tests/acceptance/settings_coverage/test_wiring.py:17`).
- **ruff TID251 measured** (`ruff 0.16.10`, throwaway config): banning the module path `"backend.permissions.catalog"` flags **the owning package itself** — `src/backend/permissions/__init__.py:11` and `src/backend/permissions/service.py:39` — i.e. there is **no self-import exemption**; a wildcard key `"backend.permissions.*"` flags **nothing** ("All checks passed"); `if TYPE_CHECKING:` imports **are** flagged. `pyproject.toml` `[tool.ruff.lint] select` is at `:182`, `[tool.ruff.lint.per-file-ignores]` at `:222`.
- **Existing guard:** `tests/unit/architecture/` does **not** exist on `main`. The in-flight worktree `crosscut/settings-public-registry-setter` (11 of 12 DAG tasks `VERIFIED`, no PR open yet — `gh pr list` shows only #79) adds `tests/unit/architecture/__init__.py` + `test_singleton_slots.py` (an `ast` scan over `src` + `tests`, an `_OWNERS` table, an owner-path exemption helper, planted-violation fixtures in `tmp_path`, and a `ponytail:` note that it resolves no import bindings) plus the `[tool.ruff.lint.flake8-tidy-imports.banned-api]` block and `"TID251"` in `select`. Its **approved** spec `docs/specs/settings-public-registry-setter.md` **EDGE-009** says the public-symbol test imports of the private module path are "not migrated by this change — they belong to TODO `public-api-import-boundary`" (measured today: **7** statements in 7 test files reference `backend.settings.registry`, not 13 — the spec's count has drifted).
- **The ast-scan pattern is already repo practice on `main`:** `tests/acceptance/logging/test_pipeline_backend.py` (walks `src/` and `tests/` for forbidden backend imports), `tests/acceptance/logging_coverage/test_statements_via_feature.py`, `tests/contract/logging/test_dependency_contract.py`.
- **Spec-pinned export surfaces:** `tests/contract/logging/test_tracing_surface.py::test_ac_020_public_export_surface` asserts `set(backend.logging.__all__) == set(_PUBLIC_API)` — exactly 8 names (`setup_logger`, `logged`, `logged_class`, `get_logger`, `Settings`, `get_settings`, `register_settings`, `_read_setting`) — so **no re-export may be added to `backend.logging`** without amending structlog-logging REQ-015/AC-020. By contrast `tests/contract/authentication/test_public_api.py::test_nfr_003_public_api_stable` only does `hasattr` subset checks (additive-safe). NFR-003-style public-API contracts exist in `authentication.md`, `mail-service.md`, `session-management.md`, `user-roles-permissions.md`, and `search.md` (where Q-124 explicitly allows breaking changes with a major bump).
- **Generated map:** `scripts/make_map.py` REQ-012 renders one `exports:` line per package **from `__all__`** (`_public_imports` is only the fallback) — e.g. `STRUCTURE.md:1341` for `backend.settings`. Adding `register_actions` to two `__all__`s therefore changes map **content**, and AC-021 byte-compares the committed map. `scripts/check_traceability.py` inspects spec IDs, matrix rows and backticked test-function names only — it never reads import structure or `__all__`.
- **Cycles already exist and import cleanly:** `uv run python -c "import backend.logging / backend.settings / backend.sessionmanagement / backend.permissions, backend.usermanagement"` all succeed; `backend/settings/registry.py:12` imports `backend.logging` while `backend/logging/feature_settings.py:19` imports `backend.settings`.
- **Other repo facts:** project version `1.1.0` (`pyproject.toml:4`); `src/frontend/` is **empty** (0 entries); coverage `source = ["src/backend","src/frontend"]`, `fail_under = 92`; ruff `select` includes `RUF` (so `RUF100` flags redundant `# noqa`); CI runs the suite in the `tests` job of `spec-validation.yml` (no map job — ADR-085).
- **Overlap check** (against `docs/specs/` and every TODO in `docs/todo/`, live and archive — recorded per the P.2 rule):
  - `crosscut/settings-public-registry-setter` (**IN-WORKFLOW**, worktree exists, 11/12 tasks VERIFIED) — collides on `pyproject.toml` `[tool.ruff.lint]`, `src/main.py:68`, and owns `tests/unit/architecture/`; its approved spec (`main`, commits `1dbddb6` + `1633c5a`) **defers this change's whole subject to this TODO** — `:21` "It does **not** specify who may import the public API (deferred TODO `public-api-import-boundary`)", `:25` "No import-permission rule for `backend.settings` / `backend.eventbus`", `:382` (Impact Analysis) "Who may import `backend.settings` / `backend.eventbus` (public-API import boundary) → TODO `public-api-import-boundary`", and EDGE-009 assigns the deferred imports. Q-01, Q-02, Q-05, Q-09, Q-14, Q-21.
  - `issue/map-default-drop-shift` (**WAITING**, PR A #79 open) — edits `scripts/make_map.py` and regenerates `STRUCTURE.md`; collides on the generated map. Q-06, Q-19.
  - `refactor/composition-root-factory` (**PREPARING**) — owns `src/main.py` wiring; this change must not restructure it. Q-13, Q-23.
  - `chore/docstrings-tests` (**PREPARING**, 26 PENDING questions) — owns `[tool.ruff.lint] select` and the `tests/*` `per-file-ignores`; same table as any TID251 change. Q-05, Q-21.
  - `feature/backend-api` (**WAITING**, blocks `api-keys`) — would add **new** cross-feature import sites; ordering decides whether it starts compliant. Q-21.
  - `archive/architecture-tests-missing` (**MERGED**) — precedent: it classified three private-module→public-API import rewrites as **DOCS/CHORE** ("an import path is not a structure change") and chose **manual** Phase 6 review over a CI boundary rule. Q-01, Q-05.
  - `docs/todo/settings-public-registry-setter.md:46` — the origin of this TODO: "**Deferred to new TODOs opened at P.3 (2026-10-06):** `public-api-import-boundary` — the wider convention that a feature's package `__init__` is the only import surface, with a self-import exemption (Q-19)". The five private singleton slots (`_settings_registry`, `_event_bus`, `_search_service`, `_session_service`, `_mail_service`) are what this change's rule generalises. Q-16.
  - No collision found with `python-3.15-upgrade`, `tenacity-rich-cpython-scripts`/`tenacity-rich-cachetools`, `complexipy-scripts`, `map-*`, `notifications`, `api-keys`, `audit-log`, `error-handling-*`, `feature-flag-*`, `rate-limiting`, `websocket-*`, `metrics-endpoint`, `backup-restore`, `db-transaction-boundary`, `dependency-injection-container`, `config-hot-reload`, `structured-*`. `docs/specs/` contains **no** spec that states an import-boundary rule (searched `docs/specs/` for the rule text) — only the settings spec's REQ-013/EDGE-009 and the NFR-003-style API-freeze clauses. **No double work found; one real dependency (the sibling change) and one generated-file collision (the map).**

## Q-01 — Is this REFACTOR at all, or CROSS-CUTTING?
- **Step:** P.2 Interrogate
- **Why needed:** the type decides the whole phase set (REFACTOR skips Phase 1–3 and produces no spec; CROSS-CUTTING requires a spec, an approval PR, per-feature task grouping and per-feature traceability updates), the version bump (none vs `minor`), and — decisively — whether the boundary rule gets a **normative home**. P.1 chose REFACTOR; the measurements say the first-match criterion is 3, not 4.
- **Context:** `AGENTS.md` Change Types criterion 3 (checked **before** REFACTOR): "The change intentionally spans two or more features: new shared capability, architecture change, or shared-infrastructure change." Measured span: the rule binds **all 11** feature packages; the migration touches 9 `src/backend` files + `src/main.py` (+ 36 test files if tests are in scope); and the change **adds a new shared guard** (a second architecture test) — a new pattern element. Precedent in the same repo: `settings-public-registry-setter` was reclassified FEATURE → **CROSS-CUTTING** at P.3 (`docs/todo/settings-public-registry-setter.md:10`: "the change intentionally spans five features and introduces a new shared pattern (a public install operation on a feature's module singleton)"). Counter-precedent: `architecture-tests-missing` (MERGED) classified three identical private-module→public-API import rewrites as **DOCS/CHORE**, "an import path is not a structure change", and chose manual review over any rule.
- **Question:** keep `refactor/public-api-import-boundary`, or reclassify to `crosscut/public-api-import-boundary` (branch rename `git branch -m`, re-run Phase P for the new type per the Escalation Rules)?
- **Recommended:** reclassify to **CROSS-CUTTING** — the change's whole point is a repo-wide rule plus shared guard infrastructure spanning 11 features, and only a spec gives a rule a normative home; the REFACTOR path would leave the rule enforced by nothing but a test docstring.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-02 — Where does the boundary rule become normative?
- **Step:** P.2 Interrogate
- **Why needed:** `AGENTS.md` states the convention in prose ("Features should expose explicit public interfaces", `:1168`; "no cross-feature internal imports" as a **manual** check at `:602` (Phase 6 review check 3) and `:589` (Phase 5 REFACTOR step)) but no spec in `docs/specs/` states an enforceable import rule, and `scripts/check_traceability.py` cannot check one. A guard test with no requirement ID has no traceability row, so the rule would be un-enforceable in the spec-validation sense.
- **Context:** searched `docs/specs/` — the only import-adjacent normative text is `settings-public-registry-setter.md` REQ-013/AC-018/EDGE-008/EDGE-009 (five private singleton slots only) and the NFR-003/NFR-004 API-freeze clauses. That spec **names the gap and hands it here**: `:21` "It does **not** specify who may import the public API (deferred TODO `public-api-import-boundary`)", `:25` "No import-permission rule for `backend.settings` / `backend.eventbus`", `:382` Impact Analysis row "Who may import `backend.settings` / `backend.eventbus` (public-API import boundary) | A separate decision with its own guard design | TODO `public-api-import-boundary`". `architecture-tests-missing` deliberately removed the dangling `tests/architecture/` CI citation from `AGENTS.md` (Phase Matrix REFACTOR cell + Phase 5 step 13) and from the `verify` skill, re-pointing the architecture check at **manual** Phase 6 review — so re-adding an automated architecture gate is a reversal of that decision and should be recorded.
- **Question:** where is the rule written down — (a) a new spec `docs/specs/public-api-import-boundary.md` with REQ/AC/INV/EDGE IDs (needs Q-01 = CROSS-CUTTING); (b) a Spec Amendment to `docs/specs/settings-public-registry-setter.md` (extend REQ-013 / replace EDGE-009) since that spec already names this TODO as the owner of the deferred imports; (c) `AGENTS.md` convention text + the guard test's docstring only (REFACTOR path); (d) some combination?
- **Recommended:** (a) + a one-line cross-reference amendment under (b) — one new spec owns the repo-wide rule, and the settings spec's EDGE-009 gets a pointer so the deferral resolves in one place; (c) alone repeats the `architecture-tests-missing` mistake of a rule with no normative home.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-03 — What exactly counts as a private import?
- **Step:** P.2 Interrogate
- **Why needed:** the TODO says "Define the rule to enforce" — the rule statement is undefined, and three distinct import forms reach a submodule. Without naming them, the guard either under-reports (trivially bypassed) or over-reports (flags legal package-root imports).
- **Context:** measured forms in use today: (1) `from backend.<pkg>.<mod> import <name>` — 266 statements; (2) `import backend.<pkg>.<mod> as <alias>` — 4 statements, all `migrations/env.py:15-18`; (3) `from backend.<pkg> import <mod> [as <alias>]` — the **module-object form**, 8 real sites (`tests/contract/logging/test_logging_contracts.py:40`, `tests/property/logging/…:39`, `…:65`, `tests/unit/logging/test_logging_edges.py:31`, `tests/settings_test_helpers.py:116,155,176`, `tests/eventbus_test_helpers.py:73`) plus one inside a subprocess source string (`tests/acceptance/settings_coverage/test_wiring.py:17`). Form (3) reaches the same private module through the package root and defeats the rule entirely.
- **Question:** is the rule "no import that resolves to `backend.<pkg>.<module>` from outside `<pkg>`", covering all three forms — or only form (1)? And is `from backend import <pkg>` (package root) always legal?
- **Recommended:** all three forms banned; form (3) must be covered or the rule is bypassable at 8 existing sites, and `import backend.<pkg>` stays the required form by definition.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-04 — Which trees does the rule bind, and are `tests/` in scope?
- **Step:** P.2 Interrogate
- **Why needed:** the TODO's acceptance signal (`rg … src/ tests/` returns only same-feature imports) puts `tests/` in scope, but the measured test tree makes that rule either unenforceable or a 96-statement migration, and the REFACTOR path forbids test changes at all (Q-08).
- **Context:** measured: `src/backend` cross-feature **11** statements in 9 files (all satisfiable today), `src/main.py` **7**, `migrations/env.py` **4**, `tests/` **95 statements / 140 names in 36 files**, `scripts/` + `.github/` **0**. A "test dir == feature" exemption covers only **14 of 95** test sites; 81 are elsewhere — `acceptance/logging_coverage` 33, tests root 16, `acceptance/permissions` 6, `unit/logging_coverage` 5, `property/logging_coverage` 5, `integration/search` 3, `unit/search` 2, `integration/sessionmanagement` 2, `acceptance/search` 2, `property` 2, and 6 singletons. Tests deliberately reach internals to test them: `tests/unit/logging/test_renderers.py:18-19` imports `backend.logging._pipeline._formatter_for`, `backend.logging._renderers.LEVEL_COLORS/color_for_tty` — same-feature, but a white-box test that no public API serves.
- **Question:** scope of the ban — (a) `src/` only (11 + 7 sites); (b) `src/` + `migrations/`; (c) `src/` + `migrations/` + `tests/` (96 more sites); (d) `src/` + `migrations/` + only the `_`-prefixed-module part of `tests/` (measured: **0** additional violations, since the only private-module test imports are same-feature)? And what replaces the TODO's `rg` acceptance signal?
- **Recommended:** (b) with tests exempt from the package rule — the public-API contract exists for **feature-to-feature** coupling; a test is a white-box consumer, and (c) is a 36-file diff that buys no architectural value and breaks the REFACTOR "no test changes" invariant.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-05 — Enforcement: ast scan test, ruff TID251, import-linter, or review only?
- **Step:** P.2 Interrogate
- **Why needed:** the TODO lists "architecture test or ruff/import-linter rule" as alternatives, but the decisive fact is unmeasured in the TODO: ruff TID251 **cannot express** a package-root rule with a self-import exemption in this repo.
- **Context:** measured with `ruff 0.16.10` and a throwaway config: banning `"backend.permissions.catalog"` flags the **owning** package (`src/backend/permissions/__init__.py:11`, `src/backend/permissions/service.py:39`) — no self-import exemption exists; a wildcard key `"backend.permissions.*"` flags **nothing** ("All checks passed"); banned-api keys must be fully-qualified module/attribute paths. Per-file-ignores would be the only workaround and would switch off the sibling change's five private-slot bans for the same files. `import-linter` is **not installed** (not in any dependency group). The ast-scan pattern is already repo practice: `tests/acceptance/logging/test_pipeline_backend.py`, `tests/acceptance/logging_coverage/test_statements_via_feature.py`, `tests/contract/logging/test_dependency_contract.py`, and the sibling's `tests/unit/architecture/test_singleton_slots.py`. `architecture-tests-missing` (MERGED) chose **manual** review (Q-4 = (a) there) — this change would reverse that.
- **Question:** which enforcement — (a) an `ast` scan test in the suite (CI runs it via the `tests` job of `spec-validation.yml`, no new job); (b) ruff TID251 with per-file-ignores; (c) add `import-linter` as a dev dependency + a CI step; (d) manual Phase 6 review only (status quo)?
- **Recommended:** (a) — it is the only mechanism that can express "outside the owning package", it reuses four existing scanners and the sibling's `_OWNERS` pattern, and it needs no new dependency and no new CI job; (c) is the strongest tool but adds a dependency the existing scanners already cover.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-06 — The baseline is not GREEN: how is the gate met?
- **Step:** P.2 Interrogate
- **Why needed:** both candidate types gate on a GREEN full-suite baseline (REFACTOR: "run the full suite and confirm it is GREEN … if it is not GREEN, STOP: resolve the pre-existing failures first or reclassify"; CROSS-CUTTING: Phase 5 full gate set). `main` is not GREEN, so P.4 cannot record a baseline as it stands.
- **Context:** measured at `2172253`: `uv run pytest tests/ -q` → **1 failed, 815 passed, 1 skipped in 252 s**. The failure is `tests/acceptance/test_structure_map.py::test_ac_021_committed_map_matches_fresh_render` (REQ-021/AC-021 of `structure-map.md`, merged as PR #75, merge commit `7dfaa23`): committed `STRUCTURE.md` says `docs/ — 223 files (process record)`, a fresh render says **224** (`git ls-files docs | wc -l` = 224 — the map has not been regenerated since the planning records were added). CI cannot catch it: the map has no CI job (ADR-085) and the `tests` job's `paths:` filter omits `docs/todo/**` and `docs/questions/**`. This change adds `docs/verification/public-api-import-boundary.md` and edits `src/`, so it must regenerate the map regardless.
- **Question:** how is a GREEN baseline established — (a) regenerate `STRUCTURE.md` as this change's first commit and record the pre-existing red; (b) land a separate one-line map refresh first (fast-path: generated file, no behavior); (c) wait for `map-default-drop-shift` (PR #79) to land and regenerate then; (d) accept a "no new failures vs the recorded baseline" gate instead of GREEN?
- **Recommended:** (b) — a standalone map refresh on `main` unblocks **every** waiting change (three other TODOs are gated on the same red), costs one generated-file commit, and keeps this change's baseline honestly GREEN.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-07 — AC-021 cannot pass on this host at all (CRLF)
- **Step:** P.2 Interrogate
- **Why needed:** even with the count fixed, the witness fails locally for a second, independent reason, so "full suite GREEN" is unverifiable on the machine the agent runs on — the gate would be permanently host-dependent.
- **Context:** `git ls-files --eol STRUCTURE.md` → `i/lf w/crlf`; `git config core.autocrlf` → `true`; no `.gitattributes` exists in the repository. `make_map.py` renders LF and AC-021 byte-compares the committed map against the working-tree file, so on Windows the compare fails on `\r` before any content difference is reached. On Linux CI the same test fails only on the 223/224 count.
- **Question:** how is the host-dependent failure handled — add a `.gitattributes` (`*.md text eol=lf`) inside this change, treat the Linux CI run as the authoritative GREEN gate and record the host caveat, switch the local checkout to `core.autocrlf=input`, or open a separate TODO for the line-ending policy?
- **Recommended:** treat the CI/Linux run as authoritative and record the caveat; open a **separate** DOCS/CHORE TODO for `.gitattributes` — it changes checkout behaviour repo-wide and is unrelated to an import boundary.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-08 — "Zero test changes" vs migrating test imports
- **Step:** P.2 Interrogate
- **Why needed:** the REFACTOR contract is explicit — "Do not modify, weaken, or delete any test", "the full suite is GREEN with **zero test changes**", "suite result identical to baseline". If Q-04 puts tests in scope, the change necessarily edits 169 test files, which contradicts the type's own review gate.
- **Context:** measured 95 test import statements / 140 names in 36 files; 133 of the 140 names are already exported, so the edits are mechanical one-liners that change no assertion. The Phase 6 review gate ("no acceptance test weakened or deleted to achieve GREEN") is about assertions, not import lines — but the REFACTOR wording is absolute.
- **Question:** if tests are in scope, is the invariant re-stated as "no test **assertion or behavior** changes; import-path edits are the permitted mechanical change", recorded as an explicit amendment in `docs/verification/public-api-import-boundary.md` — or must tests stay byte-identical (forcing Q-04 = src-only)?
- **Recommended:** keep tests byte-identical (Q-04 = (b)) so the REFACTOR invariant stays literal and cheap to verify; if the user puts tests in scope, the amendment must be recorded **before** P.4, not discovered at Phase 6 review.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-09 — The imports the settings spec already assigned to this change
- **Step:** P.2 Interrogate
- **Why needed:** an **approved, merged** spec (`docs/specs/settings-public-registry-setter.md`, PR #73, merge commit `a1a15db`) defers a concrete work item to this TODO by name. Whether this change picks it up decides part of Q-04 and Q-08, and leaving it undone strands a promise in an approved spec.
- **Context:** EDGE-009 of that spec: "The 13 test sites that import **public** symbols from the private module path (`from backend.settings.registry import SettingsRegistry`) are **not** violations of this requirement … Those 13 imports are not migrated by this change — they belong to TODO `public-api-import-boundary`." Measured today: **7** statements in 7 test files reference `backend.settings.registry` (`tests/acceptance/logging_coverage/test_behavior_unchanged.py`, `test_levels.py`, `test_services_traced.py`, `test_statements_via_feature.py`, `tests/logging_coverage_test_helpers.py`, `tests/logging_test_helpers.py`, `tests/property/logging_coverage/test_invariants.py`) — the spec's "13" counts imported **names**, not statements, and has drifted. The parent change's deferral note (`docs/todo/settings-public-registry-setter.md:46`) is what opened this TODO, and the spec's Impact Analysis (`:382`) records the same hand-off.
- **Question:** does this change migrate those settings test imports (satisfiable today — `SettingsRegistry` and friends are in `backend.settings.__all__`), or re-defer them, and if re-deferred, who owns them?
- **Recommended:** migrate them — an approved spec already assigned them here, they are 7 statements, and doing it here closes EDGE-009 instead of leaving a dangling cross-change obligation; this is the one test-tree migration worth doing even if Q-04 exempts tests generally.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-10 — New public exports: `register_actions` for authentication and filemanagement
- **Step:** P.2 Interrogate
- **Why needed:** this is the one place where satisfying the rule **requires adding public API**, which is the condition under which a REFACTOR classification is wrong (new externally observable surface). It must be decided, not discovered mid-Phase 4.
- **Context:** measured: `src/main.py:32` (`from backend.authentication.feature_actions import register_actions as register_authentication_actions`) and `:41` (filemanagement) are the only two `feature_actions` imports whose symbol is **not** in the owning `__all__` — `register_actions` is already exported by `backend.mail`, `backend.search`, `backend.sessionmanagement`, `backend.settings` and `backend.usermanagement` (not by `backend.permissions`, whose actions reach `main.py` through the package root). Adding it is additive: `tests/contract/authentication/test_public_api.py::test_nfr_003_public_api_stable` checks `hasattr` per name (subset), not exact equality, so it cannot break; `docs/specs/authentication.md` NFR-003 promises the public API stays "backward compatible" (additive satisfies it). It also changes `STRUCTURE.md`'s `exports:` line for both packages (Q-19).
- **Question:** (a) add `register_actions` to `backend.authentication.__all__` and `backend.filemanagement.__all__` (accepting new public exports); (b) exempt `src/main.py` from the rule as the composition root so no export is needed; (c) leave those two lines as-is with a recorded exemption?
- **Recommended:** (a) — it makes the two packages consistent with the other six that already export the same hook, it is additive to an `hasattr`-checked contract, and (b) would carve an exemption into the exact file the rule most needs to cover.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-11 — Spec-pinned export surfaces: no widening without an amendment
- **Step:** P.2 Interrogate
- **Why needed:** the rule's natural fix ("re-export it from the package") is **forbidden** for at least one package by an existing acceptance test, so the guard and the fix strategy must respect pinned surfaces or the change reddens another feature's spec.
- **Context:** `tests/contract/logging/test_tracing_surface.py::test_ac_020_public_export_surface` asserts `set(backend.logging.__all__) == set(_PUBLIC_API)` — exactly 8 names — and separately that no logging backend is re-exported (structlog-logging REQ-015/AC-020). Measured: **no** site needs a `backend.logging` re-export, so the conflict is latent, not active. Other pinned surfaces: authentication NFR-003 (`hasattr` subset), mail-service NFR-003, session-management NFR-003 (names `SessionService`, `SessionEntry`, 4 events, `register_settings`, `get/set/reset_session_service`), user-roles-permissions NFR-003, logging-coverage NFR-004; `search.md` NFR-003 records the user-approved deviation Q-124 (breaking changes allowed with a major bump).
- **Question:** confirm the constraint — a re-export may be added only where the rule forces it and only where no spec pins the surface exactly; if a forced addition hits `backend.logging`, a Spec Amendment PR for structlog-logging REQ-015/AC-020 comes first. Should the guard test also assert the pinned surfaces (exactness) for the other 10 packages?
- **Recommended:** confirm the constraint; do **not** add exactness tests for the other 10 packages — only `backend.logging` is spec-pinned exact, and freezing 10 unpinned surfaces would block future features for no specified benefit.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-12 — `migrations/env.py`: migrate the four module imports or exempt them?
- **Step:** P.2 Interrogate
- **Why needed:** the four sites are the only `import backend.<pkg>.<mod>` form in the repo, they carry `# noqa: F401` (so a naive "unused import" reading calls them dead), and their purpose — registering SQLModel tables for alembic autogenerate — is a contract `AGENTS.md` documents by module path.
- **Context:** `migrations/env.py:15-18`: `import backend.authentication.models as auth_models  # noqa: F401` (and filemanagement, permissions, usermanagement). `AGENTS.md` "Using Migrations (alembic)" names those exact module paths and instructs "when a new module defines SQLModel tables, add its import to `env.py`". Package-root imports would work (each feature's `__init__` already imports its `models`), but they pull each whole feature package into the alembic env. CI gate: the `migrations` job in `quality.yml` runs `alembic upgrade head` against a temp database.
- **Question:** exempt `migrations/` from the rule (recorded in the guard's exemption table), or migrate the four lines to `import backend.<pkg> as <pkg>`?
- **Recommended:** exempt — the file is infrastructure, `AGENTS.md` prescribes the module paths, and the migration would trade a documented, CI-covered registration mechanism for a shorter lint report.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-13 — `src/main.py`: how much may this change touch?
- **Step:** P.2 Interrogate
- **Why needed:** `src/main.py` holds 7 of the violations, but another prepared TODO owns that file's structure, and a third (in-flight) change already rewrites line 68. Overlapping edits to the composition root are the likeliest merge conflict in this change.
- **Context:** measured `src/main.py` sub-module imports (7): `:32` authentication, `:41` filemanagement, `:45` mail, `:65` sessionmanagement, `:67` settings, `:77` usermanagement (all `feature_actions.register_actions`), and `:68` `from backend.settings.registry import _registry as _settings_registry_singleton` — the last is **owned by the in-flight sibling change**, whose branch already **deletes** it and installs the registry through `from backend.settings import get_settings_registry, set_settings_registry` (diff `main..crosscut/settings-public-registry-setter -- src/main.py`). `docs/todo/composition-root-factory.md` (PREPARING) is "Extract the composition root out of `src/main.py` into a dedicated module" and `Depends on: settings-public-registry-setter`.
- **Question:** does this change rewrite only the 6 `feature_actions` import lines in `src/main.py` (mechanical, no structure change), defer all of `src/main.py` to `composition-root-factory`, or rewrite them and additionally re-order imports?
- **Recommended:** rewrite the 6 import lines only, and sequence this change **after** `settings-public-registry-setter` merges (it owns line 68) — leaving `main.py` exempt would leave the repo's worst offender unguarded while `composition-root-factory` rewrites the file anyway.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-14 — Where the guard lives, and the `tests/unit/architecture/` collision
- **Step:** P.2 Interrogate
- **Why needed:** the natural home for the guard is the directory the in-flight sibling change is creating right now; two changes creating `tests/unit/architecture/__init__.py` and two scanners over the same tree is a guaranteed conflict and a duplication risk.
- **Context:** the sibling branch adds `tests/unit/architecture/__init__.py` and `test_singleton_slots.py` (scan over `src` + `tests`, `_OWNERS` table, `_owned_slots` owner-path exemption, planted-violation fixtures written under `tmp_path`, `ponytail:` note that no import binding is resolved) — pinned by its spec's AC-017 and EDGE-008. `tests/unit/architecture/` does not exist on `main`. Three other source-scanning tests already live elsewhere (`tests/acceptance/logging/test_pipeline_backend.py`, `tests/acceptance/logging_coverage/test_statements_via_feature.py`, `tests/contract/logging/test_dependency_contract.py`).
- **Question:** new module `tests/unit/architecture/test_package_boundaries.py` beside the sibling's file (and who owns `__init__.py`), extend `test_singleton_slots.py` itself, or put the guard somewhere else (e.g. `tests/contract/`)?
- **Recommended:** a **new** file `tests/unit/architecture/test_package_boundaries.py` that reuses the sibling's scan/exemption pattern; never edit `test_singleton_slots.py` (it is spec-pinned by AC-017/EDGE-008 and owned by another change) — whichever change merges second keeps the existing `__init__.py`.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-15 — Exemption mechanics: `# noqa` or an explicit table?
- **Step:** P.2 Interrogate
- **Why needed:** the rule needs exemptions (same-feature imports, `migrations/env.py`, possibly tests), and the mechanism decides whether they are auditable or silently scattered.
- **Context:** measured: `migrations/env.py:15-18` already carry `# noqa: F401`; ruff `select` includes `RUF`, so `RUF100` flags redundant `# noqa` comments — an exemption comment that outlives its violation becomes a lint error. The sibling's guard uses the opposite mechanism: an `_OWNERS` table in the test plus an owner-path predicate, with planted-violation fixtures proving the scan is live.
- **Question:** may a violation be silenced with `# noqa: <code>` (ruff) or an inline marker (scan test), or must every exemption be listed in one table inside the guard test? And must the guard carry planted-violation fixtures of its own, as the sibling's spec requires for its guard (EDGE-008)?
- **Recommended:** table-only exemptions (no `# noqa` escape hatch) plus planted-violation fixtures — mirrors the sibling's already-approved pattern, keeps every exemption reviewable in one place, and avoids `RUF100` churn.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-16 — Same-feature imports and the package `__init__` itself
- **Step:** P.2 Interrogate
- **Why needed:** 148 of the 159 `src/backend` sub-module imports are same-feature, and every `__init__.py` must keep importing its own submodules to re-export at all — the rule must state that these are legal or it condemns 93% of the sites it is meant to leave alone.
- **Context:** measured 148 same-feature statements, all in **absolute** form — `src/backend/settings/__init__.py:5,15,16,28,33` import `backend.settings.exceptions` / `.feature_actions` / `.models` / `.registry` / `.repository`, and `src/backend/logging/__init__.py:11-14` import `backend.logging._decorator` / `._pipeline` / `._settings` / `.feature_settings` (the private modules **are** how the public surface is built). The sibling spec's rule form is "outside the **owning module path**" — an owner-path exemption, not a ban on the module name.
- **Question:** confirm (a) a module may always import from its own package (including its own private modules), (b) a package's `__init__` may import its own private submodules (`._registry`, `._renderers`) — that is how the public surface is built, and (c) the exemption is computed from the file's path, not from a name list?
- **Recommended:** confirm all three — the owner-path exemption is the only workable form (measured: TID251 has no self-import exemption, which is exactly why it fails here), and it matches the sibling's already-approved `_owned_slots` pattern.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-17 — Circular imports: what proves the rewrites are safe?
- **Step:** P.2 Interrogate
- **Why needed:** replacing a submodule import with a package-root import executes the package's whole `__init__`, so a rewrite can create an import cycle that the submodule form avoided — the classic failure mode of exactly this refactor, and the TODO names it as a risk with no mitigation.
- **Context:** the repo **already defers package-root imports to avoid exactly this**: `src/backend/logging/feature_settings.py:19` and `:56` import `backend.settings` inside functions, with the comment at `:52-54` — "The `backend.settings` import is deferred to the call site: importing it at module level here would create a circular import (the settings registry imports `backend.logging` for its tracing decorators)" — because `src/backend/settings/registry.py:12` imports `backend.logging` at module level. Other package-level pairs: `src/backend/permissions/service.py:57` imports `backend.usermanagement` while `src/backend/usermanagement/feature_actions.py:15` imports `backend.permissions.catalog` (TYPE_CHECKING only). Measured: `uv run python -c "import backend.logging"`, `… backend.settings`, `… backend.sessionmanagement`, `… backend.permissions, backend.usermanagement` all succeed. 7 of the 11 cross-feature sites are inside `if TYPE_CHECKING:` blocks, where the import never executes at runtime, so converting them changes nothing at runtime but does make the symbol resolvable at runtime.
- **Question:** what is the safety proof — the full suite only, or an explicit Phase 5 smoke step (`uv run python -c "import backend.<pkg>"` for all 11 packages, plus `uv run alembic upgrade head` if `migrations/` is touched), and is a cycle allowed to be resolved by re-ordering imports inside the same file?
- **Recommended:** add the 11-package import smoke as an explicit Phase 5 step (one command, catches the failure mode the suite can miss if a package is never imported in a given order); do not restructure any cycle in this change — that belongs to `dependency-injection-container` / `db-transaction-boundary`.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-18 — `__all__` discipline: must every re-export be declared, and is the surface checked?
- **Step:** P.2 Interrogate
- **Why needed:** "public API = what the package re-exports" only works if the re-export set is declared; the repo already has `__all__` everywhere, but nothing states whether the guard checks it, and ruff `RUF022` (unsorted `__all__`) is in the selected rule set.
- **Context:** measured: 11/11 `__init__.py` define `__all__` (sizes 3–44). `scripts/make_map.py` REQ-012 renders the map's `exports:` line from `__all__`, falling back to `_public_imports` only when `__all__` is absent — so `__all__` is already the de-facto declared surface. `RUF022` is active (`select = ["ALL"]` minus the ignores at `pyproject.toml:182-221`), so `__all__` order is already enforced.
- **Question:** does this change add any rule about `__all__` itself (must every re-export be listed; must `__all__` be exactly the set of names consumers may use; a completeness test that every name any consumer needs is exported), or is `__all__` left as-is and only the consumer side is guarded?
- **Recommended:** guard the consumer side only — `__all__` is already universal and `RUF022`-sorted, and a completeness test would freeze 11 surfaces the specs do not pin (Q-11).
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-19 — Generated map: regeneration obligation and the `STRUCTURE.md` conflict
- **Step:** P.2 Interrogate
- **Why needed:** `AGENTS.md` requires `STRUCTURE.md` to be regenerated in the same commit as any `.py` change, AC-021 byte-compares it, and two other changes are regenerating the same generated file — a merge conflict that `AGENTS.md` has an explicit rule for, but the ordering still has to be chosen.
- **Context:** `make_map.py` renders per-module line counts **and** per-package `exports:` lines from `__all__`, so both the import rewrites (line counts) and the two new `register_actions` exports (Q-10, content) change the map. `STRUCTURE.md` is already stale (Q-06). `docs/todo/map-default-drop-shift.md` (WAITING, PR A #79 open) edits `scripts/make_map.py` and regenerates the map; `complexipy-scripts` also regenerates it. `AGENTS.md` Git Worktrees rule: on a merge conflict in the map, take either side and regenerate — never hand-merge.
- **Question:** confirm the regeneration plan — regenerate in the same commit as the `__all__`/import edits, and rebase-and-regenerate after `map-default-drop-shift`'s map refresh lands, or land this change first and make that one regenerate?
- **Recommended:** regenerate in the same commit and sequence this change **after** `map-default-drop-shift`'s map refresh — the map is a single generated file and every change that touches it should rebase on the last regeneration rather than race it.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-20 — Traceability: does the guard get matrix rows?
- **Step:** P.2 Interrogate
- **Why needed:** `AGENTS.md` forbids transitioning GREEN→VERIFIED without updating the traceability matrix, and `scripts/check_traceability.py` **fails the build** when a row cites an ID no spec defines — so a row for a rule with no spec is not optional polish, it is a CI failure.
- **Context:** measured: `check_traceability.py` checks spec IDs ↔ matrix rows ↔ backticked test-function names existing under `tests/`; it never reads imports. Current report: `Traceability: PASS (881 matrix rows, 136 spec IDs, 801 test functions)`. Migrating import lines does not rename any test function, so no existing row breaks. A REFACTOR has no REQ/AC IDs, so its guard test has nothing to cite.
- **Question:** if the type stays REFACTOR, is the guard recorded only in `docs/verification/public-api-import-boundary.md` (no matrix row), and if it becomes CROSS-CUTTING, which IDs get rows (the new spec's REQ/AC, plus updated rows for every affected feature per the CROSS-CUTTING Phase 5 rule)?
- **Recommended:** REFACTOR → no row (a row citing a non-existent ID reddens CI); CROSS-CUTTING → one row per new REQ/AC citing `tests/unit/architecture/test_package_boundaries.py`, and no refresh of untouched rows (the matrix is a historical gate record, decision Q-129).
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-21 — Sequencing against the in-flight changes and the backlog
- **Step:** P.2 Interrogate
- **Why needed:** this change edits the exact files three other changes edit (`pyproject.toml [tool.ruff.lint]`, `src/main.py`, `tests/unit/architecture/`, `STRUCTURE.md`), and it changes a **convention** that every future feature will write code against — landing it before or after the feature TODOs changes how much migration they carry.
- **Context:** in-flight: `crosscut/settings-public-registry-setter` (11/12 tasks VERIFIED, no PR yet; owns `pyproject.toml` TID251 block, `tests/unit/architecture/`, `src/main.py:68`, and its EDGE-009 defers imports **to** this change) and `issue/map-default-drop-shift` (WAITING, PR A #79; owns `scripts/make_map.py` + the map). Prepared/backlog: `refactor/composition-root-factory` (owns `src/main.py` wiring, depends on the sibling), `chore/docstrings-tests` (owns `[tool.ruff.lint] select` + `tests/*` per-file-ignores), `feature/backend-api` (WAITING; would add **new** cross-feature import sites and blocks `api-keys`), `feature/notifications`, `feature/api-keys`, `refactor/db-transaction-boundary`, `refactor/dependency-injection-container`.
- **Question:** what is the required order — (i) hard dependency: after `settings-public-registry-setter` merges? (ii) after `map-default-drop-shift`'s map refresh? (iii) before `backend-api`/`api-keys`/`notifications` so new code starts compliant, or after them? (iv) coordinate with `docstrings-tests` on the shared ruff table?
- **Recommended:** after `settings-public-registry-setter` (hard — same files, and its guard is the pattern this one extends), after `map-default-drop-shift`'s map refresh (soft, to avoid a generated-file race), and **before** `backend-api`/`api-keys`/`notifications` so their new cross-feature code is written compliant; `docstrings-tests` only needs a same-table rebase, not an ordering constraint.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-22 — Version bump and branch name
- **Step:** P.2 Interrogate
- **Why needed:** the bump level and the branch name both follow from Q-01, and the bump happens inside the PR (S6.4) — getting the type wrong means either a missing bump or a wrong one.
- **Context:** `AGENTS.md` Versioning: ISSUE → patch, FEATURE → minor, CROSS-CUTTING → minor (`major` if breaking), REFACTOR/DOCS-CHORE → **none**. Current version `1.1.0` (`pyproject.toml:4`). Nothing in the measured migration removes a public name, so no breaking change is implied; `search.md` NFR-003 (Q-124) is the only spec that allows breaking public-API changes at all, and this change does not touch it.
- **Question:** with the type as decided in Q-01: `refactor/public-api-import-boundary` with **no** bump, or `crosscut/public-api-import-boundary` with a `minor` bump (1.1.0 → 1.2.0)? Is any case (e.g. adding `register_actions` to two packages) treated as breaking enough for `major`?
- **Recommended:** follow Q-01 — CROSS-CUTTING → `minor` (1.2.0); the two added exports are additive and no name is removed, so `major` is not warranted.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-23 — Non-goals: what this change must NOT do
- **Step:** P.2 Interrogate
- **Why needed:** the TODO is one line of intent, and every near-miss below is a real, separately-tracked change that an agent could plausibly fold in. The scope boundary has to be explicit before P.4.
- **Context:** concrete near-misses measured on `main`: `docs/todo/dependency-injection-container.md` (PREPARING) owns DI; `docs/todo/composition-root-factory.md` (PREPARING) owns `src/main.py` wiring; `docs/todo/db-transaction-boundary.md` (PREPARING) owns cross-feature transaction coupling; `docs/todo/feature-flag-registry.md` and `feature/notifications` would introduce registry/plugin patterns; function-local (deferred) imports as a technique exist at `src/backend/logging/feature_settings.py:19,56`, `src/backend/eventbus/eventbus.py:60`, `src/backend/filemanagement/service.py:71,200`, `src/backend/authentication/feature_settings.py:10,16` — 20+ sites in `src/`; `import-linter` is not installed; `src/frontend/` is empty; no plugin system exists anywhere in `src/`.
- **Question:** confirm all of these are **out** of scope: introducing a dependency-injection container or any plugin/registry mechanism; converting module imports to lazy/runtime imports; fixing or restructuring circular imports; touching `src/main.py`'s wiring structure (composition-root-factory); moving/renaming modules inside a feature; adding `import-linter` or any new dependency; changing any signature, behaviour, or public name beyond the two `register_actions` re-exports (Q-10); migrating `tests/` beyond whatever Q-04/Q-09 decide.
- **Recommended:** all out — the change is exactly "one rule + one guard + the import rewrites it forces"; each near-miss already has an owner or was rejected by an earlier change.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-24 — `src/frontend/` and the "frontend equivalents" wording
- **Step:** P.2 Interrogate
- **Why needed:** the TODO's investigation note says "plus the frontend equivalents if any", which invites a search that finds nothing and could invent scope for a boundary that does not exist.
- **Context:** measured: `src/frontend/` exists but is **empty** (0 entries); coverage `source = ["src/backend", "src/frontend"]` with the comment "so the empty `frontend` placeholder is covered once implemented"; `AGENTS.md` Project Structure states "no `src/frontend/` directory exists (the coverage configuration reserves the name)" while the directory does exist and is empty — a small doc/code mismatch unrelated to this change.
- **Question:** confirm there is **no** frontend scope (drop the "frontend equivalents" wording from the TODO's intent), and whether the `AGENTS.md`/`STRUCTURE.md` mismatch about `src/frontend/` is worth a separate DOCS/CHORE TODO or is left alone?
- **Recommended:** no frontend scope — the directory is empty and holds no imports; leave the `AGENTS.md` wording mismatch alone (or note it in the verification record) rather than widen this change.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-25 — `backend.shared` and `backend.eventbus`: are they "features" under the rule?
- **Step:** P.2 Interrogate
- **Why needed:** the rule is phrased per feature, but two packages are infrastructure, and `AGENTS.md` says "`shared/` is deliberately small" — whether they are subjects (and whether their consumers must go through their `__init__`) changes the violation count and the exemption table.
- **Context:** measured: `backend/shared/__init__.py` re-exports 3 names (`PermissionChecker`, `Principal`, `requires_permission`) from `backend.shared.principal`; every consumer already imports the package root — `from backend.shared import …` at **8** sites across authentication, filemanagement, permissions, search and sessionmanagement — **0** violations; its own docstring states "no import of `backend.permissions` (no circular imports)". `backend/eventbus/__init__.py` exports 4 names; `backend/eventbus/eventbus.py` is imported by tests only (`tests/eventbus_test_helpers.py:73` uses the module-object form). `src/backend/shared/` contains 2 files, `src/backend/eventbus/` 3 files.
- **Question:** are `shared` and `eventbus` subjects of the rule like any feature (their consumers must import the package root), or infrastructure with a different exemption?
- **Recommended:** treat them exactly like features — both already have `__all__`, both have 0 violations today, and an infrastructure exemption would create a hole in the rule at the two packages that exist precisely to be depended on.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-26 — Definition of done: what is the acceptance signal?
- **Step:** P.2 Interrogate
- **Why needed:** the TODO's acceptance signal is a `rg` one-liner that counts **all** sub-module imports including same-feature ones, so as written it can never return "only same-feature imports" without also being the thing the guard enforces — the done-criterion and the guard must be the same artifact or the change has two moving definitions of done.
- **Context:** the TODO signal is `rg "from backend\.[a-z_]+\.[a-z_]+ import" src/ tests/` returning only same-feature imports; measured today it matches **261** lines in `src/` + `tests/` (grep counts 166 sub-module import statements in `src/` and 96 in `tests/`; the `ast` scan counts 95 real imports in `tests/` — one grep match sits inside a string literal), of which 148 are same-feature and legal. The sibling change's guard pattern (scan + planted violations + exemption table) is the repo's current answer for "how do we know a rule still holds", and its spec requires planted-violation fixtures (EDGE-008) because a scan that matches nothing is indistinguishable from a broken scan.
- **Question:** is the acceptance signal (a) the guard test passing with planted violations proving it is live (the `rg` line demoted to a documented smoke check), (b) the `rg` count reaching a stated number, or (c) both? And what number/shape counts as "the rule holds" in the verification record?
- **Recommended:** (a) — the guard test **is** the acceptance signal (it encodes the exemptions the `rg` line cannot express), with planted-violation fixtures as the liveness proof; record the measured before/after counts in `docs/verification/public-api-import-boundary.md` as evidence, not as the gate.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

### Category coverage

| Category | Result |
|---|---|
| Scope & boundaries / non-goals | covered (Q-04, Q-23, Q-24, Q-25) |
| Classification & governance (type, branch, bump, normative home) | covered (Q-01, Q-02, Q-22) |
| Interfaces & contracts (public API, `__all__`, spec-pinned surfaces) | covered (Q-10, Q-11, Q-18, Q-25) |
| Rule definition (what counts as a violation, which forms, which trees) | covered (Q-03, Q-04, Q-16) |
| Enforcement & tooling (scan vs ruff vs import-linter vs review, exemptions) | covered (Q-05, Q-14, Q-15) |
| Testing & witnesses (baseline, witnesses, liveness, "no test changes") | covered (Q-06, Q-07, Q-08, Q-09, Q-26) |
| Behavior preservation (import cycles, runtime vs TYPE_CHECKING, suite-as-contract) | covered (Q-17, Q-16, Q-08) |
| Sequencing & merge conflicts (in-flight worktrees, backlog, shared files) | covered (Q-13, Q-14, Q-19, Q-21) |
| Generated artifacts (`STRUCTURE.md` `exports:` + line counts, traceability matrix) | covered (Q-19, Q-20) |
| Architecture & conventions (`AGENTS.md` rules, `shared/`, infrastructure packages) | covered (Q-02, Q-25, Q-18) |
| Data & state | skipped — the change moves no data and touches no schema: measured, no SQLModel/alembic table is altered (`migrations/env.py` imports are the only migration-adjacent sites, Q-12) and no persisted format changes |
| Performance | skipped — import-form changes only alter which module object is bound; measured package-root imports of all 11 packages already succeed and no performance NFR exists for import time |
| Security & privacy | skipped — no credential, token, session or secret handling changes; the only auth-adjacent edits are `sessionmanagement` → `backend.authentication` import lines (Q-03) and they bind the same objects |

## Late questions (Phases 2–6)

_none_
