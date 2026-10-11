# Questions: composition-root-factory

One question file per change, created at **P.1 Frame** from this template and named `composition-root-factory.md`. It replaces the retired central `AI_Questions.md` (archived at `docs/questions/archive-AI_Questions.md`).

- **Change:** composition-root-factory (REFACTOR as classified at P.1 — **Q-01 asks the user to confirm or reclassify**)
- **TODO file:** `docs/todo/composition-root-factory.md`
- **Spec:** n/a (REFACTOR) — `docs/specs/settings-coverage.md` REQ-002 / AC-003 and `docs/specs/logging-coverage.md` REQ-011 / AC-011 need an amendment (Q-01); `docs/specs/settings-public-registry-setter.md` REQ-011 / AC-016 collide (Q-02)
- **Opened:** 2026-10-06
- **Status:** ALL ANSWERED  <!-- OPEN | ALL ANSWERED -->
- **Answer rounds:** 9 (rounds 1–2 on 2026-10-10 · rounds 3–9 on 2026-10-11 — 30 entries Q-01…Q-30 incl. the Q-10b/Q-16b follow-ups, 0 PENDING)

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

**Feature brief (intermediate — to be folded into the spec / scope at P.4), recorded by P.2 on 2026-10-10.**

*Goals.* Replace the 37 executable module-level statements of `src/main.py` (measured with `ast`: 66 module-level statements = 26 imports + 2 class defs + 1 docstring expr + 17 assignments + 20 calls; `wc -l src/main.py` → 221) with one callable composition root that builds the same object graph and returns it, so the graph can be built on demand and asserted in-process.

*Measured facts the interrogation rests on* (all re-measured on `main` = `6badaf5`, 2026-10-10):

- `src/main.py` has **no** `if __name__ == "__main__"` guard, no `main()` function, and `pyproject.toml` has no `[project.scripts]` entry — `README.md:39` states "There is no app or CLI entry point to run yet — `src/main.py` is startup wiring, not a command."
- Call order today: catalog + 7 `register_*_actions` (`:82-89`) → 2 lazy proxies (`:130-131`) → `SettingsRegistry(...)` (`:137`) → private-slot singleton install (`:138`) → `SqliteSessionRepository` (`:145`) → `PermissionService(...)` (`:153-162`) → `set_service` (`:163`) → `set_system_permissions` (`:170`) → 6 `register_*_settings` (`:173-178`) → user repo + `UserManager` + `set_manager` (`:181-183`) → `AuthService`/`FileService`/`MailService`/`SessionService` (`:186-206`) → `get_search_service(...)` + 3 `register_source` (`:212-219`) → `setup_logger()` (`:221`). Total `register_*` call sites: **13** (`grep -c "^register_" src/main.py` → 13), not "~10".
- `import main` side effects (measured in an empty temp dir): creates `data/authentication.db`, `data/permissions.db`, `data/usermanagement/users.db`, `data/filemanagement.db`, `logs/app.log`, `settings/values.yaml`; wall time ≈ **1.04 s** warm.
- Nothing in `src/`, `scripts/`, `migrations/` or `.github/` imports `main` (`grep -rn "import main\b" src scripts migrations .github --include=*.py` → no output). Only two **tests** import it, both in a fresh subprocess: `tests/acceptance/settings_coverage/test_wiring.py:19` and `tests/acceptance/permissions/test_composition_wiring.py:37`.
- Two approved specs pin the wiring to **module/import time**: `settings-coverage.md` REQ-002 ("The entrypoint (`src/main.py`) calls each feature's `register_settings(registry)` once at startup, before any feature code runs…") + AC-003 ("**Given** `src/main.py`, **When** it is executed, **Then** all features' settings are registered…"); `logging-coverage.md` REQ-011 ("The entrypoint (`src/main.py`) calls `setup_logger()` exactly once at startup…") + AC-011, whose test asserts the call is a **top-level module statement** (`tests/acceptance/logging_coverage/test_setup_logger.py:41-45`).
- The in-flight `settings-public-registry-setter` spec pins the wiring position harder: REQ-011 "installs the registry it wires through `set_settings_registry()` **at its current module-import-time position (`:137-138`)**… the six `register_*_settings(...)` calls (`:173-178`) and the service-construction sites (`:161`, `:198`, `:204`, `:214`)…", and AC-016 runs a **source scan of `src/main.py`**.
- Double-wiring hazard measured: re-executing the body (`importlib.reload(main)`) succeeds, but `get_search_service()` ignores its arguments after the first call, so the second wiring's `_search_service` is the **first** instance and its `_settings_registry` is the **stale** registry (measured: `search singleton identical: True`, `search service registry is the NEW one: False`). Duplicate `register_settings` on one registry raises `SettingsRegistrationError` (measured); `register_source` with the same name replaces atomically / is an idempotent no-op when identical (`src/backend/search/service.py`).
- Quality gates over `src/main.py` today: mypy checks it (`uv run mypy src/main.py` → Success), ruff + ruff-format are clean on it, complexipy scores **only its 8 proxy methods** (module-level wiring is not measured — re-confirmed: the report lists `_LazyPermissionService::*` and `_LazyUserManager::*` only, all 0), and coverage does **not** measure it (`[tool.coverage.run] source = ["src/backend", "src/frontend"]`; a `--cov` run lists no `main.py` row) with `fail_under = 92`.
- Gap found: `filemanagement`, `mail` and `sessionmanagement` each expose `feature_settings.register_settings`, and **none of the three is called anywhere in `src/`** — after `import main`, `reg.has("filemanagement.storage_root")`, `…("mail.smtp_host")`, `…("sessionmanagement.cleanup_batch_size")` are all `False` (measured). 16 keys are unregistered; the features run on REQ-005 hardcoded defaults + a warning.
- Second gap found: `src/main.py` never installs the `PermissionService` (`:153`) or the `SessionService` (`:202`) into their module singletons, so `get_permission_service()` (`src/backend/permissions/service.py:529`) would lazily build a **different** `PermissionService` with its own repositories. No `src/` caller uses those two getters today (measured).

*Out-of-scope candidates* are enumerated in Q-25. *Edge cases*: double call (Q-10), stale singletons (Q-10), unregistered-key silent fallback (Q-24), repo-root pollution by the existing subprocess test (Q-11).

## Q-01 — REFACTOR vs reclassification: does moving the wiring out of module import change specified behavior?

- **Step:** P.2 Interrogate
- **Why needed:** The TODO classifies the change REFACTOR ("restructures existing code without altering externally observable behavior") and flags that `settings-coverage.md` AC-003 may force a Spec Amendment. The answer decides the whole route: REFACTOR (baseline + scope, no spec, no approval PR) vs FEATURE/CROSS-CUTTING (spec + S1.4 approval PR + task DAG) — and it decides whether the change may proceed at all without touching two approved specs.
- **Context:** `docs/specs/settings-coverage.md` REQ-002 + AC-003 (quoted in the preamble) make **import-time execution** of `src/main.py` normative; `docs/specs/logging-coverage.md` REQ-011 + AC-011 do the same for `setup_logger()`, and its test asserts the call is a top-level module statement (`tests/acceptance/logging_coverage/test_setup_logger.py:41-45`). Measured: `import main` is itself externally observable — it creates 4 SQLite DBs, `logs/app.log` and `settings/values.yaml` in the CWD. AGENTS.md classification is first-match: #4 REFACTOR requires no observable behavior change; #2 FEATURE matches ("adds externally observable behavior or capability not covered by an approved spec"); #3 CROSS-CUTTING matches an architecture change spanning ≥ 2 features (this one rewires the wiring of 7 features + 3 shared singletons).
- **Question:** Keep the change as REFACTOR (with a Spec Amendment PR for `settings-coverage.md` REQ-002/AC-003 and `logging-coverage.md` REQ-011/AC-011), or reclassify it — FEATURE, or CROSS-CUTTING as `settings-public-registry-setter` was (its P.3 Q-2 reclassification precedent: spans ≥ 2 features + a new shared pattern)?
- **Recommended:** Reclassify to **CROSS-CUTTING** (branch `crosscut/composition-root-factory`, spec `docs/specs/composition-root-factory.md` with an Impact Analysis, plus a Spec Amendment PR amending `settings-coverage.md` REQ-002/AC-003 and `logging-coverage.md` REQ-011/AC-011) — `import main`'s side effects are measured, externally observable behavior and two approved specs' ACs assert import/module-level wiring, so a "no behavior delta" REFACTOR claim is false on the evidence.
- **Answer:** **A — reclassify to CROSS-CUTTING.** Spec `docs/specs/composition-root-factory.md` with an Impact Analysis, branch `crosscut/composition-root-factory`, plus the Spec Amendment PR for `settings-coverage.md` REQ-002/AC-003 and `logging-coverage.md` REQ-011/AC-011.
- **Date:** 2026-10-10
- **Status:** ANSWERED
- **Incorporated:** yes — `docs/todo/composition-root-factory.md` `Change type:` now CROSS-CUTTING; the branch/worktree at P.4 is `crosscut/…`; Q-29's consequences follow from this answer

## Q-02 — Collision with the in-flight `settings-public-registry-setter` REQ-011 / AC-016

- **Step:** P.2 Interrogate
- **Why needed:** That change is IN-WORKFLOW (`git worktree list` → `python-template_kopie-worktrees/crosscut/settings-public-registry-setter`, TODO `Status: IN-WORKFLOW`) and its spec is already on `main` (`git log -- docs/specs/settings-public-registry-setter.md` → `1dbddb6`, `1633c5a`). Its REQ-011 and AC-016 are written **against the exact line positions of this file**; whichever lands second breaks the other's acceptance test.
- **Context:** REQ-011: "installs the registry it wires through `set_settings_registry()` **at its current module-import-time position (`:137-138`)** … the six `register_*_settings(...)` calls (`:173-178`) and the service-construction sites (`:161`, `:198`, `:204`, `:214`) … that startup wiring still runs once, before any feature code." AC-016: "**Given** a fresh subprocess that imports `main` … **And** a source scan of `src/main.py` finds no consumer site passing the local `_settings_registry` handle". Its out-of-scope table row already names this TODO as the deferral target ("A `create_app()` / composition-root factory, moving the wiring out of module import | Explicitly deferred by Q-11").
- **Question:** Sequence this change strictly after `settings-public-registry-setter` merges, and amend its REQ-011/AC-016 in the same amendment PR (restating them position- and import-agnostic: "the composition root installs through `set_settings_registry()` before the registrations") — or hold this change until that one is merged and then treat its REQ-011/AC-016 as an approved spec this change must amend?
- **Recommended:** Both — do not start P.4 before that change merges, and amend its REQ-011/AC-016 (drop the `:137-138` / `:173-178` line pins, keep the install-before-register ordering rule) in this change's amendment PR; otherwise AC-016's source scan fails the moment the wiring moves.
- **Answer:** **A — sequence strictly after `settings-public-registry-setter` merges, and amend its REQ-011/AC-016 in this change's amendment PR**, restated position- and import-agnostic ("the composition root installs through `set_settings_registry()` before the registrations"), keeping the install-before-register ordering rule.
- **Date:** 2026-10-10
- **Status:** ANSWERED
- **Incorporated:** yes — the amendment PR now covers three specs (`settings-coverage`, `logging-coverage`, `settings-public-registry-setter`); P.4 must not start before that change merges

## Q-03 — Must `import main` become side-effect-free, or do the module-level globals stay as a compatibility layer?

- **Step:** P.2 Interrogate
- **Why needed:** The TODO's "In scope" leaves both options open ("Keep a module-level import path working so existing consumers of `main`'s globals keep resolving (or enumerate and update them — P.2 decides)"), and the acceptance signal asserts the opposite ("`import main` no longer creates `data/` databases"). The two cannot both hold.
- **Context:** Measured consumers of `main`'s globals: only `tests/acceptance/permissions/test_composition_wiring.py` (`main._user_repository`, `main._session_repository`, `main._permission_service`) and `tests/acceptance/settings_coverage/test_wiring.py` (`import main` only). No `src/`, `scripts/`, `migrations/` or `.github/` consumer exists.
- **Question:** Remove the module-level wiring entirely (import becomes side-effect-free, the two tests are rewritten), or keep the globals as a deprecated compatibility layer that still wires at import?
- **Recommended:** Remove it — there are no consumers outside the two subprocess tests, so a compatibility layer would preserve exactly the import side effect the change exists to eliminate (and would keep AC-003/AC-011 true only by keeping the old code).
- **Answer:** **A — remove the module-level wiring entirely.** `import main` becomes side-effect-free; the two subprocess wiring tests are rewritten to call the factory in-process. No compatibility layer.
- **Date:** 2026-10-10
- **Status:** ANSWERED
- **Incorporated:** yes — settles the TODO's open scope alternative and makes its acceptance signal ("`import main` no longer creates `data/` databases") normative; drives Q-12's answer

## Q-04 — Name and return shape of the callable

- **Step:** P.2 Interrogate
- **Why needed:** The TODO says "name and shape decided at P.2"; the return shape decides how the two rewritten wiring tests read, whether mypy can check them, and what the spec's API block must state.
- **Context:** The graph today is 12 module globals (`_catalog`, `_settings_registry`, `_session_repository`, `_permission_service`, `_user_repository`, `_user_manager`, `_auth_service`, `_file_repository`, `_file_service`, `_mail_service`, `_session_service`, `_search_service`) plus 2 repositories the AC-020 test reaches for. The repo's only existing factory convention is `build_*_source(repository) -> SearchSource` (`src/backend/{usermanagement,filemanagement,sessionmanagement}/search_source.py`). The TODO's goal line names `create_app()` / `build_services()`; `settings-public-registry-setter` D10 names `create_app()`.
- **Question:** Which name (`build_composition_root()` / `create_app()` / `build_services()`), and what does it return — a frozen dataclass container with named fields, a `NamedTuple`, a plain tuple, or a dict?
- **Recommended:** `build_composition_root() -> App` where `App` is a **frozen dataclass** with named, typed fields — named access keeps the rewritten wiring tests and mypy meaningful, a 12-value tuple is unmaintainable, and the name matches this TODO's own title (the `build_*` verb matches the existing `build_*_source` convention).
- **Answer:** **A — `build_composition_root() -> App`, `App` a frozen dataclass with named, typed fields.**
- **Date:** 2026-10-10
- **Status:** ANSWERED
- **Incorporated:** yes — the spec's API block at P.4; the TODO's goal line (`create_app()` / `build_services()`) is restated to this name; `backend-api` Q-07 = B builds its app on this callable, so its name is a cross-change interface (note: `create_app` stays free for the FastAPI factory)

## Q-05 — Parameters: does the callable take paths/collaborators, or nothing?

- **Step:** P.2 Interrogate
- **Why needed:** Whether an in-process test can point the graph at a temp directory decides whether the subprocess tests can be replaced at all, and every parameter needs a stated default (spec self-consistency: "parameter coverage").
- **Context:** Hardcoded locations in `src/main.py`: `:144` `sqlite:///./data/authentication.db`, `:152` `sqlite:///./data/permissions.db`, `:181` `sqlite:///./data/usermanagement/users.db`, `:194` `sqlite:///./data/filemanagement.db`, `:197` `LocalDiskStorageBackend("./data/files")`; the registry's value directory comes from the `SettingsRegistry` default `YamlValueRepository("settings")`. `src/backend/permissions/service.py:108-109` already defines `DEFAULT_DATABASE_URL = "sqlite:///./data/permissions.db"` and `DEFAULT_USER_DATABASE_URL = "sqlite:///./data/usermanagement/users.db"` — the same literals, duplicated in `main.py`.
- **Question:** Which parameters does `build_composition_root()` take — keyword-only with defaults equal to today's literals (database URLs, storage root, value repository / settings registry, event bus), or zero parameters with the test monkeypatching paths?
- **Recommended:** Keyword-only parameters defaulting to today's literals for the storage locations (`database_url`s, `storage_root`, `settings_registry`, `event_bus`), reusing `permissions.service.DEFAULT_DATABASE_URL` / `DEFAULT_USER_DATABASE_URL` instead of re-typing the literals — without them an in-process test cannot isolate a temp dir, and defaults keep the no-argument call identical to today.
- **Answer:** **A — keyword-only parameters with defaults equal to today's literals** (`database_url`s, `storage_root`, `settings_registry`, `event_bus`), reusing `permissions.service.DEFAULT_DATABASE_URL` / `DEFAULT_USER_DATABASE_URL` rather than re-typing them.
- **Date:** 2026-10-10
- **Status:** ANSWERED
- **Incorporated:** yes — the spec's API block at P.4; makes Q-11 (in-process filesystem isolation) answerable and lets the two subprocess tests become in-process ones

## Q-06 — What happens to the entrypoint itself (`python src/main.py`)?

- **Step:** P.2 Interrogate
- **Why needed:** Today running the file performs the wiring; after extraction a callable that is never called means running the file does nothing — a silent behavior change nobody asked for.
- **Context:** Measured: no `if __name__ == "__main__"` block in `src/main.py` (file ends at `:221` with `setup_logger()`), no `[project.scripts]` in `pyproject.toml`, and `README.md:39` says "There is no app or CLI entry point to run yet — `src/main.py` is startup wiring, not a command."
- **Question:** Add `if __name__ == "__main__": build_composition_root()` (so running the file keeps doing what it does today), or add nothing and let the file become import-only?
- **Recommended:** Add the two-line `__main__` guard calling the factory — it preserves the current "run the file → the app is wired" behavior at zero design cost, and inventing a CLI/`[project.scripts]` entry point is out of scope (YAGNI, README would need a rewrite).
- **Answer:** **Add the `__main__` guard** — the recommendation, accepted. `src/main.py` keeps `if __name__ == "__main__": build_composition_root()`, so `python src/main.py` keeps doing what it does today; no CLI, no `[project.scripts]` entry point (that stays a Q-25 non-goal).
- **Date:** 2026-10-11
- **Status:** ANSWERED
- **Incorporated:** yes (P.3 round 5, 2026-10-11)

## Q-07 — Where does the composition root live: `src/main.py`, `src/backend/shared/`, or a new module?

- **Step:** P.2 Interrogate
- **Why needed:** It decides coverage gating (Q-20), `STRUCTURE.md` churn (Q-21), the import-boundary exposure (Q-22), and whether the wording of REQ-002/REQ-011 ("the entrypoint (`src/main.py`)") stays literally true.
- **Context:** `src/backend/shared/` currently holds only `principal.py` + `__init__.py`; AGENTS.md says "`shared/` is deliberately small" (code belongs there only when shared by multiple features with no business logic). Coverage `source = ["src/backend", "src/frontend"]` — `src/main.py` is outside it (measured: no `main.py` row in a `--cov` report), `fail_under = 92`. `STRUCTURE.md:118` and `:1627` map `src/main.py` (221 lines).
- **Question:** Keep the factory in `src/main.py`, or move it to `src/backend/shared/composition.py` / `src/backend/composition/`?
- **Recommended:** Keep it in `src/main.py` — smallest diff, no new module, no coverage-source change, no new cross-package import surface, and the two approved specs' "the entrypoint (`src/main.py`)" wording keeps resolving; `shared/` is the wrong home for the application's own wiring (it is not feature-shared code).
- **Answer:** **B — move it to a new `src/backend/composition/` package** (against P.2's recommendation). Consequences the user accepted: `docs/specs/settings-coverage.md` REQ-002 and `docs/specs/logging-coverage.md` REQ-011 wording "the entrypoint (`src/main.py`)" must be amended to name the composition module; the code enters the coverage `source = ["src/backend", ...]` set, so it is measured against `fail_under = 92` (Q-20); `STRUCTURE.md` gains a new package (Q-21); `src/backend/api/` (the `backend-api` TODO) can import the composition root without importing a top-level module.
- **Date:** 2026-10-10
- **Status:** ANSWERED
- **Incorporated:** yes — P.4 spec: new package `src/backend/composition/` (home of `build_composition_root()` and `App`); `src/main.py` keeps only the `__main__` shim (Q-06) and the spec amendments' wording

## Q-08 — Where does `setup_logger()` go, given AC-011's test asserts a module-level call?

- **Step:** P.2 Interrogate
- **Why needed:** `tests/acceptance/logging_coverage/test_setup_logger.py` fails the moment the call moves into a function, and the spec it enforces (REQ-011/AC-011) says "at startup, before any feature code runs" — a factory call is not "startup" in the same sense.
- **Context:** The test parses `src/main.py` with `ast` and asserts (a) exactly one `setup_logger` call anywhere and (b) exactly one as a **top-level module statement** (`:41-45`); `tests/unit/logging_coverage/test_edge_cases.py:106-107` separately asserts `main_src.count("setup_logger(") == 1`. `setup_logger()` at `:221` must run **after** `register_logging_settings` (`:173`) because it reads `logging.*` live (comment at `:165-169`, REQ-011/REQ-005).
- **Question:** Move `setup_logger()` to be the first statement inside the factory (and amend REQ-011/AC-011 + rewrite both tests to assert "exactly one call, inside the composition root, before any feature object is constructed"), or keep it at module level in `src/main.py`?
- **Recommended:** Move it inside the factory as its first call and amend REQ-011/AC-011 + rewrite the two source-scan tests — keeping it at module level means `import main` still installs log sinks (an import side effect the change exists to remove) and splits the wiring in two places.
- **Answer:** **A — `setup_logger()` becomes the factory's first call** (after `register_logging_settings`, which must precede it because it reads `logging.*` live); amend `logging-coverage.md` REQ-011/AC-011 to "exactly one call, inside the composition root, before any feature object is constructed" and rewrite `tests/acceptance/logging_coverage/test_setup_logger.py` and `tests/unit/logging_coverage/test_edge_cases.py:106-107`.
- **Date:** 2026-10-10
- **Status:** ANSWERED
- **Incorporated:** yes — the amendment PR now covers `logging-coverage.md` REQ-011/AC-011 explicitly; the two source-scan tests are in this change's test scope

## Q-09 — Is the current call order normative, and which edges are load-bearing invariants?

- **Step:** P.2 Interrogate
- **Why needed:** A REFACTOR's contract is "same behavior"; with wiring, behavior **is** order. The spec/scope must state which orderings are invariants so a reviewer can check them and a test can pin them.
- **Context:** Measured order (see preamble). Ordering constraints stated in the code/specs: the registry install (`:138`) must precede the six `register_*_settings` calls (`settings-public-registry-setter` REQ-011: "the install therefore precedes the registrations, which is what makes `settings-coverage.md` REQ-002 … literally true"); the `PermissionService` is "created (and set on the proxy) **before** the settings registration, so the registry's enforced methods resolve the real service" (`:150-151`); the session repository is built before the `PermissionService` which takes it as `session_lookup` (`:140-143`, REQ-017/ADR-073); `setup_logger()` reads the logging settings live so it must follow `register_logging_settings` (`:165-169`); AGENTS.md: "`setup_logger()` exactly once … before any feature code runs", "Feature-owned registration … Call it at startup to register the feature's settings. The feature then reads its settings live"; `search.md` §12.8: "feature settings, feature actions, then the three `register_source` calls **after the repositories exist**".
- **Question:** Declare the exact current order an invariant (INV: the factory performs the same calls in the same order, with the four load-bearing precedences named), or only the four precedences, allowing the rest to be re-grouped?
- **Recommended:** Declare the full order invariant with the four precedences named as the reason — re-grouping buys nothing (the diff is a move, not a redesign) and every un-named freedom is a silent behavior change the suite cannot see.
- **Answer:** **Full order invariant, and the loop's element order is part of it** — the user chose the third option, going beyond the recommendation. INV: the factory performs the same calls in the same order, with the four load-bearing precedences named, **and** the registration loop's element order is normative. This is required by the `startup-settings-registration-gaps` **Q-14** decision (the six `register_*_settings` one-liners become an ordered collection of the nine `register_settings` callables iterated once), so the factory moves a loop, not six lines, and the list order is now part of the wiring contract. The **Q-24** guard asserts it (see that entry).
- **Date:** 2026-10-11
- **Status:** ANSWERED
- **Incorporated:** yes (P.3 round 4, 2026-10-11)

## Q-10 — Is the factory safe to call twice, and what must the caller reset?

- **Step:** P.2 Interrogate
- **Why needed:** Tests will call it repeatedly; a second call that silently returns stale objects is the worst failure mode of this change and must be specified, not discovered.
- **Context:** Measured in one process: `importlib.reload(main)` succeeds, but the second pass leaves `get_search_service()` returning the **first** instance (`search singleton identical: True`) whose `_settings_registry` is the **old** registry (`search service registry is the NEW one: False`) — because `get_search_service` "ignores its arguments" after the first call (`src/backend/search/service.py:599-617`). `register_settings` twice on one registry raises `SettingsRegistrationError` (measured; ADR-036 states it). `register_source` same-name re-registration replaces atomically / is a no-op when identical. Reset helpers that exist: `reset_settings_registry()`, `reset_event_bus()`, `reset_search_service()`, `reset_permission_service()`, `reset_session_service()`. Each call also opens 4 SQLite engines and creates files.
- **Question:** Specify the factory as **single-shot per process** (a second call requires the caller to reset the five singletons first, documented in the docstring and used by the test fixture), or make it idempotent/self-resetting?
- **Recommended:** Single-shot, documented, with the test fixture calling the five `reset_*` helpers — auto-resetting inside the factory would hide the stale-singleton hazard from every other caller and would silently discard instances other code may still hold.
- **Answer:** **Idempotent / self-resetting** — the user chose the second option, **against** the recommendation, refined by **Q-10b** below: a second `build_composition_root()` call resets the shared defaults itself, so the caller does not have to. The docstring states exactly which slots are reset and which are reused.
- **Date:** 2026-10-11
- **Status:** ANSWERED
- **Incorporated:** yes (P.3 round 5 → Q-10b, 2026-10-11)

### Q-10b — What exactly does a second factory call reset (follow-up to Q-10)

- **Step:** P.3 Answer — round 5 follow-up (raised by the orchestrator from the Q-10 answer)
- **Why needed:** `reset_event_bus()` is specified to **shut the bus down** (`src/backend/eventbus/eventbus.py:312-320`, event-bus REQ-005 / EDGE-007), so a factory that resets all five slots would drain and stop a running event bus on every second build and leave already-subscribed handlers attached to a dead bus.
- **Question:** Reset all five slots, reset the four non-bus slots and reuse the live bus, or go back to single-shot?
- **Recommended:** Reset the four non-bus slots (settings, permissions, search, session) and reuse the live event bus — self-resetting without ever draining a running bus.
- **Answer:** **Self-reset, but never the bus** — the recommendation, accepted. A second call resets `settings`, `permissions`, `search` and `session` slots and **reuses the existing event bus** (no `reset_event_bus()` call, so no drain and no shutdown); handlers subscribed to the live bus keep their bus. The test fixture no longer needs the five `reset_*` calls for the factory's own state (it still uses them for its own isolation), and the docstring names the four reset slots and the reused bus.
- **Date:** 2026-10-11
- **Status:** ANSWERED
- **Incorporated:** yes (P.3 round 5, 2026-10-11)

## Q-11 — How does an in-process wiring test isolate the filesystem?

- **Step:** P.2 Interrogate
- **Why needed:** The stated benefit ("the wiring assertions that today need a subprocess can be made in-process") is only real if the in-process call does not create `data/`, `logs/` and `settings/` in the repo root or leak between tests.
- **Context:** Measured: `import main` in an empty temp dir creates `data/{authentication,permissions,filemanagement}.db`, `data/usermanagement/users.db`, `logs/app.log`, `settings/values.yaml`. `tests/acceptance/settings_coverage/test_wiring.py` runs its subprocess with `cwd=_REPO_ROOT`, so today it writes those paths **into the repository root** (they exist there and are gitignored at `.gitignore:225` `/settings/`, `:230` `/data/`, `:231` `/logs/`); `tests/acceptance/permissions/test_composition_wiring.py` instead uses `cwd=tmp_path`. AGENTS.md (settings feature): "Test registries MUST pass an explicit isolated value repository (e.g. `YamlValueRepository(tempfile.mkdtemp())`) to avoid cross-test contamination". Note the existing AC-003 test pre-installs a temp-dir registry at `test_wiring.py:18` but `main.py:138` replaces it, so that pre-install does **not** isolate the value directory (measured: `settings/values.yaml` still created).
- **Question:** Isolate by parameters (tmp-path DB URLs + tmp storage root + `YamlValueRepository(tmp_path)` per Q-05), or by `monkeypatch.chdir(tmp_path)` around a zero-parameter call?
- **Recommended:** Parameters for the DB URLs/storage root/value repository (they are needed anyway for the container to be embeddable) plus `monkeypatch.chdir(tmp_path)` as a belt-and-braces guard for the paths that stay hardcoded (`logs/`, the `settings` default) — chdir alone leaves the singleton-collision problem of Q-10 unsolved.
- **Answer:** **Parameters + `chdir` belt-and-braces** — the recommendation, accepted. Factory parameters carry the tmp-path DB URLs, the tmp storage root and `YamlValueRepository(tmp_path)`; `monkeypatch.chdir(tmp_path)` additionally guards the paths that stay hardcoded (`logs/`, the `settings` default).
- **Date:** 2026-10-11
- **Status:** ANSWERED
- **Incorporated:** yes (P.3 round 6, 2026-10-11)

## Q-12 — Rewrite the two subprocess wiring tests, or keep them and add new ones?

- **Step:** P.2 Interrogate
- **Why needed:** Both tests execute `import main`; if import stops wiring, they fail. They are also cited by name in the traceability matrix, which CI checks for referential integrity.
- **Context:** `tests/acceptance/settings_coverage/test_wiring.py::test_main_wires_all_features` (settings-coverage AC-003) and `tests/acceptance/permissions/test_composition_wiring.py::test_ac_020_composition_root_validates_session_token` (user-roles-permissions AC-020, added by issue `session-lookup-unwired`). Matrix rows: `docs/verification/traceability.md` Settings Coverage Matrix `| REQ-002 | AC-003 | test_main_wires_all_features | GREEN … |` and the `## Issue: session-lookup-unwired` section row. `scripts/check_traceability.py` (CI `traceability` job) "fails when a row cites a test function that no longer exists under `tests/`". The AC-020 test reaches `main._user_repository`, `main._session_repository`, `main._permission_service` — private globals that disappear with the factory.
- **Question:** Rewrite both tests to call `build_composition_root()` in-process (and update the two matrix rows in the same commit), or keep them as subprocess tests that run `import main; build_composition_root()`?
- **Recommended:** Rewrite both in-process against the returned container and update the two traceability rows in the same commit — the tests assert the wiring, not the import mechanism, and keeping a subprocess per wiring assertion is the exact cost this change removes; leaving the rows stale fails the `traceability` CI job.
- **Answer:** **Rewrite both in-process** — the recommendation, accepted. Both existing subprocess wiring tests call `build_composition_root()` in-process and assert on the returned container; the two `docs/verification/traceability.md` rows are updated in the same commit. Note the interaction with `startup-settings-registration-gaps` **Q-22**: that change's strengthened witness keeps its subprocess form (it asserts `main`'s module-level wiring, which still exists until this change lands) and carries the repo-root `settings/` hygiene fixture; this change converts the wiring assertions to in-process calls.
- **Date:** 2026-10-11
- **Status:** ANSWERED
- **Incorporated:** yes (P.3 round 5, 2026-10-11)

## Q-13 — What new tests does this change require (and is a test the point of it)?

- **Step:** P.2 Interrogate
- **Why needed:** For a REFACTOR the contract is "existing tests, zero test changes" — but this change deliberately rewrites two tests and exists to make something testable. The Phase 3/5 gate set depends on which of those is agreed.
- **Context:** 815 test functions exist under `tests/` (measured `grep -rho "def test_" tests --include=*.py | wc -l`). Nothing today can assert the object graph without a subprocess. AGENTS.md REFACTOR Phase 5: "the full suite MUST be GREEN, zero test changes"; the light-tier and fast-path rules do not apply to a REFACTOR.
- **Question:** Accept that this change **must** change tests (the two wiring tests) and add exactly two new ones — (a) the factory returns a fully wired graph (the six features' settings registered, `session_lookup` wired, the three search sources registered), (b) importing `main` creates no files/directories — or a larger matrix?
- **Recommended:** Exactly those two new tests plus the two rewritten ones — (a) pins the wiring the refactor must preserve, (b) pins the acceptance signal in the TODO; anything more (per-service assertions) duplicates the features' own suites (ponytail: smallest check that fails if the logic breaks).
- **Answer:** **Two new + two rewritten** — the recommendation, accepted. (a) the factory returns a fully wired graph (every wired feature's settings registered, `session_lookup` wired, the three search sources registered), (b) importing `main` creates no files or directories. No per-service matrix. Test-side note: the Q-15 install decision adds one assertion to (a) — `get_permission_service()` / `get_session_service()` are the instances the factory returned — recorded there rather than as a third new test.
- **Date:** 2026-10-11
- **Status:** ANSWERED
- **Incorporated:** yes (P.3 round 6, 2026-10-11)

## Q-14 — Do the three never-called `register_settings` calls get added by this change?

- **Step:** P.2 Interrogate
- **Why needed:** The extraction puts all 13 `register_*` calls in one visible place, and the missing three will look like a typo in the new code. Adding them changes observable behavior, so it cannot ride along silently in a REFACTOR.
- **Context:** Measured: `src/backend/filemanagement/feature_settings.py:45`, `src/backend/mail/feature_settings.py:66`, `src/backend/sessionmanagement/feature_settings.py:29` define `register_settings`, and no call site exists anywhere in `src/` (`grep -rn "register_settings(" src/` → only definitions). After `import main`: `has("filemanagement.storage_root") = False`, `has("mail.smtp_host") = False`, `has("sessionmanagement.cleanup_batch_size") = False` (16 keys total across the three features). `settings-coverage.md` REQ-002 says "each feature's `register_settings(registry)`"; REQ-005/AC-006 make the unregistered case a silent hardcoded-default fallback with a warning. AGENTS.md documents all three features as "Registered via the feature-owned `register_settings(registry)` (call at startup)".
- **Question:** Keep them out of scope (open a separate ISSUE/FEATURE TODO for the missing registrations), or fix them here as part of the extraction?
- **Recommended:** Out of scope, open a separate TODO — registering 16 keys changes observable behavior (views, persistence, `SettingChanged` events, live reads) and would hide a real defect inside an architecture change; the factory's test should assert **today's** registered set so the gap stays visible.
- **Answer:** **C — fix the three missing `register_settings` calls in this change, with a new acceptance test asserting the gap is closed** (against P.2's recommendation). The `settings-coverage.md` REQ-002 wording is left as-is because it already requires "each feature's `register_settings(registry)`" — the change makes AC-003 true instead of amending it.
- **Date:** 2026-10-10
- **Status:** ANSWERED — **re-answered 2026-10-11 (see below)**
- **Incorporated:** yes — the change is no longer behavior-preserving in this respect: it registers 16 previously unregistered keys (`filemanagement.*`, `mail.*`, `sessionmanagement.*`). **Backlog consequence:** the separate `docs/todo/startup-settings-registration-gaps.md` TODO (score 5/5) is now absorbed by this change — its disposition (merge into this change / keep separate) is the orchestrator's next backlog decision.
- **Re-answered:** **out of scope — the separate `startup-settings-registration-gaps` ISSUE owns the three calls and lands first.** The user answered that change's **Q-18 = C** on 2026-10-11, which resolves the cross-change contradiction this entry created (`composition-root-singleton-install` Q-26 said the gap was another change's work). The original 2026-10-10 answer stands as a dated record of what was decided before that TODO was framed. **Consequences for this change:** the factory extraction is behavior-preserving again — its acceptance test asserts **today's** registered set (the six wired features, with the three unregistered ones asserted absent) so the gap stays visible until the ISSUE lands; the factory PR must not add the three calls; and if the ISSUE merges first, the factory's expected set is re-derived from `main` at that moment (nine features).

## Q-15 — Does the factory install the `PermissionService` / `SessionService` singletons?

- **Step:** P.2 Interrogate
- **Why needed:** The composition root is the natural place to install them, and not installing them is a latent divergence the new code will make obvious; whether it is fixed here decides if the change is behavior-preserving.
- **Context:** Measured: `src/main.py:153` builds `PermissionService` and `:202` builds `SessionService` **directly**; neither is installed into its module singleton (`get_permission_service()` at `src/backend/permissions/service.py:529` would lazily build a *different* instance with its own `SqliteRoleRepository`/`SqliteGrantRepository`/`UserManager`; `get_session_service()` raises `ValueError` without a repository). No `src/` code calls those two getters today (measured), so the divergence is latent. `settings-public-registry-setter` owns the install mechanism for five singletons and its REQ-011 covers only the settings registry site in `main.py`.
- **Question:** Preserve today's non-install (out of scope, record as a follow-up), or install both through the setters as part of the factory?
- **Recommended:** Preserve the non-install and record a follow-up TODO — installing them changes which instance other code resolves (observable), and the install mechanism is owned by the in-flight `settings-public-registry-setter`; a REFACTOR/CROSS-CUTTING extraction must not smuggle it in.
- **Answer:** **Install both in the factory now** — the user asked back ("why should they be installed — is it a better architecture?"), was answered with the measurements (`src/main.py:171` builds `PermissionService` and injects it at `:200,:210,:216,:217,:219,:223,:233`; **no** `src/` call site of `get_permission_service()` / `get_session_service()` exists today, so the second-instance defect is latent; three of the five singletons **are** installed today — `set_settings_registry` at `:156`, `get_event_bus()` at `:178`/`:231`, `get_search_service(...)` at `:230` — so the composition root is inconsistent 3-installed / 2-not), and chose to install both. Consequences: the factory calls `set_permission_service(...)` and `set_session_service(...)`; `get_permission_service()` / `get_session_service()` start returning the wired instances (an observable change, so this change is not a pure REFACTOR — consistent with its **Q-01** CROSS-CUTTING classification); the install is not retroactive and logs one WARNING when it replaces a non-empty slot; and `composition-root-singleton-install` is **absorbed** — see **Q-30**.
- **Date:** 2026-10-11
- **Status:** ANSWERED
- **Incorporated:** yes (P.3 round 5 → Q-30, 2026-10-11)

## Q-16 — Do the two lazy cycle proxies move unchanged, or is the cycle re-designed?

- **Step:** P.2 Interrogate
- **Why needed:** A callable root changes the two-phase wiring (proxy → `set_service`/`set_manager`); a tempting "improvement" (two-phase build, setter injection, dropping the proxies) is a redesign with its own risk.
- **Context:** `_LazyPermissionService` (`:93-114`, with `# type: ignore[union-attr]` on the two check methods) and `_LazyUserManager` (`:117-127`); instances at `:130-131`; `set_service` at `:163`, `set_manager` at `:183`. The TODO's out-of-scope already says the cycle is real (`PermissionService` ↔ `UserManager`, `SettingsRegistry` ↔ `PermissionService`) and the proxies stay. complexipy scores these 8 methods at 0 today.
- **Question:** Move the two classes and their `set_*` calls verbatim into the factory (same two-phase order), or restructure the cycle handling?
- **Recommended:** Move them verbatim — the proxies are already tested by the AC-020 composition test, the cycles are documented in the module docstring and ADR-070, and any redesign widens the diff without removing a requirement.
- **Answer:** **Re-design the cycle handling** — the user chose the second option, **against** the recommendation; the concrete shape is **Q-16b** below.
- **Date:** 2026-10-11
- **Status:** ANSWERED
- **Incorporated:** yes (P.3 round 7 → Q-16b, 2026-10-11)

### Q-16b — Which cycle redesign (follow-up to Q-16)

- **Step:** P.3 Answer — round 6 follow-up (raised by the orchestrator from the Q-16 answer)
- **Why needed:** "Re-design" has three very different shapes, and one edge must stay lazy: the settings registry is constructed before `PermissionService` and needs a checker (`src/main.py:156`), so at least one proxy remains.
- **Context:** Measured: the cycle is `PermissionService` ↔ `UserManager`, broken today by `_LazyPermissionService` (`src/main.py:112`) and `_LazyUserManager` (`:136`) plus three `type: ignore` comments (`:124`, `:127`, `:175`). ADR-070 records the no-circular-import rule; `tests/acceptance/permissions/test_composition_wiring.py` (AC-020) pins the `session_lookup` edge.
- **Question:** Drop the `UserManager` proxy by reordering; replace both proxies with typed late-binding adapters; use one generic proxy in `backend/shared/`; or reverse Q-16?
- **Recommended:** One proxy — build the `UserManager` first with the permission proxy, then `PermissionService` with the real `UserManager`; `_LazyUserManager`, its `set_manager` call and one `type: ignore` disappear.
- **Answer:** **One proxy: drop `_LazyUserManager`** — the recommendation, accepted. The factory builds `UserManager` first (injecting `_LazyPermissionService` as its checker), then `PermissionService` with the **real** `UserManager`, then `set_service(...)` on the proxy. `_LazyUserManager` and its `set_manager` call are deleted, one `type: ignore[arg-type]` goes away, and the two `type: ignore[union-attr]` in the permission proxy stay (Q-17). The **Q-09** order invariant is restated for this order, and the AC-020 composition witness is updated in the same commit.
- **Date:** 2026-10-11
- **Status:** ANSWERED
- **Incorporated:** yes (P.3 round 7, 2026-10-11)

## Q-17 — Typing obligations for the new function and container

- **Step:** P.2 Interrogate
- **Why needed:** `src/main.py` is inside the mypy gate today, and the project requires explicit parameter and return types on every signature; the container's field types decide whether the rewritten tests are type-checked.
- **Context:** Measured: `uv run mypy src/main.py` → "Success: no issues found in 1 source file"; `pyproject.toml` `[tool.mypy] disallow_untyped_defs = true`, `check_untyped_defs = true`; `src/main.py` carries `# type: ignore[arg-type]` (`:157`) and two `# type: ignore[union-attr]` (`:108`, `:111`). `ty` is the fast local tool (`uv run ty check src/`).
- **Question:** Confirm the gate: fully typed `App` fields (concrete classes, not `Any`), typed keyword parameters, and the three existing `type: ignore` comments preserved unchanged — and is `mypy src/` (not just `main.py`) the Phase 5 gate?
- **Recommended:** Yes to all — the container's value is that mypy checks the wiring, and the `type: ignore` comments encode the proxy contract, so removing them would fail the build; `mypy src/` is the CI/Phase 5 gate (`quality_check` in `pyproject.toml`).
- **Answer:** **Confirm all four** — the recommendation, accepted: `App` fields are concrete classes (not `Any`), the keyword parameters are typed, the remaining `type: ignore` comments are preserved unchanged, and `mypy src/` (not just the changed file) is the Phase 5 / CI gate. Count correction from **Q-16b**: after `_LazyUserManager` is dropped, **two** `type: ignore[union-attr]` comments remain (both in the permission proxy), not three.
- **Date:** 2026-10-11
- **Status:** ANSWERED
- **Incorporated:** yes (P.3 round 7, 2026-10-11)

## Q-18 — Docstring obligations for the new public objects (ruff `D` over `src/`)

- **Step:** P.2 Interrogate
- **Why needed:** ruff `D` is gated over `src/` (per-file-ignores exempt only `tests/`, `scripts/`, `migrations/`, `.github/`), and AGENTS.md rejects filler docstrings that restate the signature — a new public function and container need docstrings that add information.
- **Context:** `src/main.py`'s module docstring (lines 1-18) already carries the wiring rationale (ADR-069, the two cycles, REQ-005/REQ-011 references); `uv run ruff check src/main.py` and `ruff format --check` are clean today.
- **Question:** Move the module docstring's wiring rationale into the function docstring (and what stays at module level), or duplicate it?
- **Recommended:** Move it — the rationale describes the wiring, which now lives in the function; the module docstring shrinks to one line, and the function docstring must additionally state the single-shot caveat (Q-10) and the ordering invariant (Q-09), which is exactly the "something its signature does not" the review rule demands.
- **Answer:** **Move it, don't duplicate** — the recommendation, accepted. The wiring rationale moves into `build_composition_root()`'s docstring; `src/main.py`'s module docstring shrinks to one line. The function docstring states the **Q-10b** reset caveat (four slots reset, the event bus reused — never `reset_event_bus()`), the **Q-09** ordering invariant including the registration-loop element order, and the single-proxy two-phase cycle (**Q-16b**). Because **Q-28** made the proxies public container fields, the two proxy classes also need docstrings that say something their signature does not (ruff `D` over `src/`).
- **Date:** 2026-10-11
- **Status:** ANSWERED
- **Incorporated:** yes (P.3 round 7, 2026-10-11)

## Q-19 — complexipy: the wiring becomes measured once it is a function

- **Step:** P.2 Interrogate
- **Why needed:** CI runs `uv run complexipy src tests --max-complexity-allowed 15`; today the 17 executable module-level statements are **not** measured at all, so the change moves code into the gate's view.
- **Context:** Measured: `uv run complexipy src/main.py --max-complexity-allowed 15` lists only the 8 proxy methods (all 0) — module-level code is not scored. `[tool.complexipy] paths = ["src", "tests"]`, `max-complexity-allowed = 15`. A branch-free function body scores 0 on the same scale (every scored method with no control flow scores 0).
- **Question:** Accept that the factory is now complexipy-measured (and that a straight-line body passes), or split the factory into sub-builders (`_build_repositories()`, `_build_services()`, …) to keep each small?
- **Recommended:** Accept one function, no split — the body is branch-free so it scores 0, and splitting would create six new private functions and six more ordering seams to review for no gate benefit; re-run complexipy at Phase 5 as evidence.
- **Answer:** **One function, no split** — the recommendation, accepted. `build_composition_root()` stays one straight-line body in `src/backend/composition/root.py` (**Q-07** / **Q-20c**); complexipy is re-run at Phase 5 as evidence. The **Q-16b** reorder shortens the body (one proxy, one `set_*` call less), which does not change the score.
- **Date:** 2026-10-11
- **Status:** ANSWERED
- **Incorporated:** yes (P.3 round 7, 2026-10-11)

## Q-20 — Coverage: does the moved code enter the 92% gate?

- **Step:** P.2 Interrogate
- **Why needed:** If the composition root moves under `src/backend/`, it becomes coverage-measured and untested lines could fail the CI `coverage` job — a hidden cost of the Q-07 choice.
- **Context:** Measured: `[tool.coverage.run] source = ["src/backend", "src/frontend"]` and `[tool.coverage.report] fail_under = 92`; a `--cov` run's report contains **no** `src/main.py` row (module-level wiring is currently invisible to coverage). `.github/workflows/quality.yml:47-60` runs pytest with coverage and honors `fail_under`. `src/main.py` has 37 executable module-level statements plus 8 methods.
- **Question:** Confirm the Q-07 decision with this in mind (keep it in `src/main.py`, outside the coverage source), or, if it moves under `src/backend/`, require the new in-process tests to cover the factory to the project floor?
- **Recommended:** Keep it in `src/main.py` (Q-07) — it avoids a coverage-source change entirely; if the user chooses a `src/backend/` home, the two new tests must cover the factory's lines and the coverage total must be re-measured at Phase 5 before the PR opens.
- **Answer:** **Move it under `src/backend/`, and amend the pinned specs** — the user first chose the move (Q-07 = B, re-confirmed here) and then, on the measured breakage, chose **"Move + amend the pinned specs"**. Measured breakage: `tests/acceptance/logging_coverage/test_setup_logger.py:13` (`_MAIN = Path("src/main.py")`, AC-011), `tests/unit/logging_coverage/test_edge_cases.py:106-107` (counts `setup_logger(` in `src/main.py`), `tests/integration/singleton_install/test_composition_root.py:31` (`_MAIN = _SRC / "main.py"`, AC-016 private-slot scan), and the AC-003 subprocess run of `src/main.py`. Handling: `logging-coverage.md` AC-011/REQ-011 and `settings-public-registry-setter` REQ-011/AC-016 are amended in this change's amendment batch to name the composition module instead of the entrypoint; the three witnesses and their traceability rows are updated in the same commit; `src/main.py` keeps a thin entrypoint that imports and calls the factory, so the AC-003 subprocess run still works. Coverage: `[tool.coverage.run] source = ["src/backend", "src/frontend"]` (`pyproject.toml:108`) with `fail_under = 92` (`:112`), so the new package is measured and the two new tests must cover it; the total is re-measured at Phase 5 before the PR opens.
- **Date:** 2026-10-11
- **Status:** ANSWERED
- **Incorporated:** yes (P.3 round 7, 2026-10-11)

## Q-21 — STRUCTURE.md regeneration and the map tests

- **Step:** P.2 Interrogate
- **Why needed:** AGENTS.md requires the generated map to be regenerated in the same commit as the `.py` change, and a merge conflict in it is resolved by regenerating — the step must know whether a module is added (Q-07) or only edited.
- **Context:** Measured: `STRUCTURE.md:118` (tree entry) and `STRUCTURE.md:1627` (`#### src/main.py (221 lines)`); the map is checked by `uv run python scripts/make_map.py --check` and by `tests/acceptance/test_structure_map.py` / `tests/property/test_structure_map.py` / `tests/unit/test_make_map.py`; skill `code-structure-map`. `scripts/` itself needs no change (no script references `main.py` — measured `grep -rn "main.py" scripts/*.py` → no output).
- **Question:** Confirm the map is regenerated in the same commit as the `src/main.py` edit (and again if a new module is created), with `scripts/` untouched?
- **Recommended:** Yes — regenerate with `uv run python scripts/make_map.py` in the same commit; it is mandatory either way and costs one command.
- **Answer:** **Yes, same commit** — the recommendation, accepted. `STRUCTURE.md` is regenerated with `uv run python scripts/make_map.py` in the same commit as the code move (it gains the new `src/backend/composition/` package, and `src/main.py`'s line count drops), and again if a further module is created; `scripts/` is untouched. Same rule as `startup-settings-registration-gaps` **Q-19**.
- **Date:** 2026-10-11
- **Status:** ANSWERED
- **Incorporated:** yes (P.3 round 7, 2026-10-11)

## Q-22 — Interaction with the planned `public-api-import-boundary` change

- **Step:** P.2 Interrogate
- **Why needed:** That TODO will add ruff `TID251` bans on cross-package module-path imports; a composition root is the single largest consumer of such imports in the repo, so the order of the two changes decides whether one rewrites the other's imports.
- **Context:** Measured in `src/main.py`: 7 cross-package module-path imports (`:32`, `:41`, `:45`, `:65`, `:67`, `:77` — the six `feature_actions` modules plus `:68` `from backend.settings.registry import _registry`, the private slot the in-flight change removes) out of 24 `from backend…` imports. `docs/todo/public-api-import-boundary.md` (Status: PREPARING) plans "ruff `TID251` banned-api entries for cross-package module-path imports, with a self-import exemption" and depends on `settings-public-registry-setter` landing first.
- **Question:** Run this change before `public-api-import-boundary` (so the boundary change migrates the factory's imports once), or wait for it (so the factory is born boundary-clean)?
- **Recommended:** Run this change first (only `settings-public-registry-setter` is a hard dependency) — the boundary change is still PREPARING and its own risk note says import-path edits are its work; duplicating that migration here would grow this diff and collide with its guard.
- **Answer:** **This change first** — the recommendation, accepted. The hard dependency (`settings-public-registry-setter`) merged on 2026-10-10 (PR #81), so nothing blocks this change except `startup-settings-registration-gaps` (see **Q-27**); `public-api-import-boundary` stays PREPARING and owns the import-path migration.
- **Date:** 2026-10-11
- **Status:** ANSWERED
- **Incorporated:** yes (P.3 round 7, 2026-10-11)

## Q-23 — NFRs: startup cost, no new dependency, no subprocess in tests

- **Step:** P.2 Interrogate
- **Why needed:** The spec/scope needs NFR IDs the verification phase can check, and the change's claimed benefit (faster, in-process wiring tests) must be stated as a measurable budget.
- **Context:** Measured: `import main` ≈ **1.04 s** warm (timed with `time.perf_counter()` around the import in a temp dir); it opens 4 SQLite engines and creates 4 DB files + `logs/app.log` + `settings/values.yaml`. Each subprocess wiring test pays a fresh interpreter plus that full import. No new third-party dependency is needed for a dataclass + function.
- **Question:** Confirm the NFRs: NFR-001 no new runtime dependency; NFR-002 the factory performs exactly the same calls as today — 13 `register_*` calls, 8 repository constructions (`:145`, `:154-156`, `:181`, `:190-191`, `:194`), 6 service constructions (`PermissionService`, `UserManager`, `AuthService`, `FileService`, `MailService`, `SessionService`), 3 `register_source` calls and `setup_logger()` — with no added startup work and the same ≈ 1.04 s wall time; NFR-003 the rewritten wiring tests run in-process with no subprocess — or add a hard startup budget?
- **Recommended:** Confirm those three, with **no** hard startup budget — the change adds no calls, so a numeric budget would restate today's 1.04 s measurement without constraining anything (and the self-consistency rule on budgets only applies to an observability table this change does not add).
- **Answer:** **Confirm, with the inventory re-derived at P.4** — the recommendation, accepted. NFR-001 no new runtime dependency; NFR-002 the factory performs the same calls, with the call inventory **re-derived from `main` at P.4** (after `startup-settings-registration-gaps` lands: 9 settings registrations driven by the ordered loop + 7 action registrations, 8 repository constructions, 6 service constructions, 3 `register_source` calls, `setup_logger()`, **plus the two new installs from Q-15 and minus the dropped proxy from Q-16b**); NFR-003 no subprocess in the new tests. **No numeric startup budget** — the measurement quoted by P.2 (≈ 1.04 s) predates the loop, the installs and the proxy removal, so it would restate a number that is about to change.
- **Date:** 2026-10-11
- **Status:** ANSWERED
- **Incorporated:** yes (P.3 round 7, 2026-10-11)

## Q-24 — Failure mode: a dropped registration fails silently. How is it guarded?

- **Step:** P.2 Interrogate
- **Why needed:** The realistic way this refactor breaks production is a `register_*` call lost in the move, and the settings design makes that **silent** — the feature falls back to a hardcoded default and only logs a warning.
- **Context:** `settings-coverage.md` REQ-005: "Reading an unregistered key falls back to the feature's original hardcoded default and logs a warning (the feature works without wiring)"; AC-006 the same. Measured: after `import main`, the three never-registered features' keys are `False` and everything still runs — proof that a missing registration does not fail the suite. ADR-036 consequence: "Feature code run outside `main.py` … has unregistered settings — but the spec's fallback (REQ-005) makes features work without wiring."
- **Question:** Require the new acceptance test to assert the **exact registered-key set** for the six wired features (so a dropped `register_*` call fails the test), or only the four keys the current subprocess test checks (`logging.log_level`, `authentication.session_ttl`, `usermanagement.roles`, `eventbus.max_queue_size`)?
- **Recommended:** Assert the exact set of registered keys for the six wired features (one assertion, derived from the current behavior, with the three unregistered features asserted absent) — it is the only guard that turns the silent-fallback failure mode into a RED test, and it also pins Q-14's out-of-scope decision.
- **Answer:** **Full set + loop order assertion** — the user chose the third option, going beyond the recommendation. The acceptance test asserts the **exact registered-key set** the factory produces — re-derived from `main` after `startup-settings-registration-gaps` lands, i.e. **all nine features / 34 keys**, not six — **and** that the registration loop's element order matches the **Q-09** ordering invariant. The "three unregistered features asserted absent" half of the recommendation is void: after that ISSUE merges, all nine are registered.
- **Date:** 2026-10-11
- **Status:** ANSWERED
- **Incorporated:** yes (P.3 round 6, 2026-10-11)

## Q-30 — `composition-root-singleton-install` is absorbed by the Q-15 decision

- **Step:** P.3 Answer — round 6 follow-up (raised by the orchestrator from the Q-15 answer)
- **Why needed:** The user's Q-15 answer takes over the entire scope of a live TODO, and AGENTS.md's backlog-overlap rule requires the absorbed TODO's disposition to be recorded before either change proceeds.
- **Context:** `docs/todo/composition-root-singleton-install.md` (FEATURE, PREPARING, 28 open questions): Goal = "Have `src/main.py` install the `PermissionService` and `SessionService` it wires as the shared defaults"; In scope = the install calls + an acceptance witness that `get_*_service()` returns the wired instance; Out of scope = the factory extraction itself. Nothing else is in its scope.
- **Question:** Drop it as absorbed, keep it as the witness owner, or reverse Q-15 and leave the installs to it?
- **Recommended:** Drop it as absorbed — its whole scope is now this change's work; its records move to the archive folders and its 28 questions never need answering.
- **Answer:** **Drop it as absorbed** — the recommendation, accepted. `composition-root-singleton-install` gets `Status: DROPPED` with the absorb decision recorded in its `## Value triage` section, and its TODO + question records move to `docs/todo/archive/` and `docs/questions/archive/`. This change owns both halves: the two install calls and the witness assertion that `get_permission_service()` / `get_session_service()` return the factory's instances.
- **Date:** 2026-10-11
- **Status:** ANSWERED
- **Incorporated:** yes (P.3 round 6, 2026-10-11)

## Q-25 — Scope boundary: what is explicitly NOT in this change (non-goals)?

- **Step:** P.2 Interrogate
- **Why needed:** Required scope-boundary question: the extraction makes several adjacent fixes tempting (missing registrations, singleton installs, parameterizing every path, adding a CLI, splitting the factory), and each is a separate change type.
- **Context:** Candidates found by measurement: the three missing `register_settings` calls (Q-14), the two uninstalled singletons (Q-15), a `__main__` guard / CLI (Q-06), splitting into sub-builders (Q-19), migrating cross-package imports (Q-22), and any change to `scripts/` (none needed, Q-21). No feature package's public API is touched by the extraction itself; `src/main.py` imports features, never the reverse.
- **Question:** Confirm the non-goals: (a) no new registrations, (b) no singleton installs beyond what happens today, (c) no new CLI/`[project.scripts]` entry point, (d) no feature public-API change, (e) no `scripts/` change, (f) no import-boundary migration — with parameters limited to what the tests need (Q-05)?
- **Recommended:** Confirm all six as non-goals — each is either a behavior change (a, b), an unrequested capability (c), or another change's owned work (d, e, f); the change is the move plus the two tests.
- **Answer:** **Five non-goals confirmed; (b) narrowed, not kept verbatim.** The user first answered "keep (b) verbatim", which contradicts **Q-15** ("install both in the factory now"); asked to break the tie, they asked for the architectural judgment, and accepted the recommendation to **install**. Final boundary: (a) no new settings registrations (the `startup-settings-registration-gaps` ISSUE owns them), (c) no new CLI / `[project.scripts]` entry point, (d) no feature public-API change, (e) no `scripts/` change, (f) no import-boundary migration — and **(b) reads "no singleton installs beyond the two decided at Q-15"** (`set_permission_service` / `set_session_service`). In scope by the same answers: the `src/backend/composition/` package move with the coverage-source consequence (Q-20), the spec amendments it forces, and the cycle simplification (Q-16b).
- **Date:** 2026-10-11
- **Status:** ANSWERED
- **Incorporated:** yes (P.3 round 9, 2026-10-11)

## Q-26 — Overlap check against every live TODO and every spec

- **Step:** P.2 Interrogate
- **Why needed:** Required by P.2 (no double work): the change must not duplicate work another TODO owns.
- **Context:** Measured: 12 live TODOs in `docs/todo/` (`api-keys`, `backend-api`, `complexipy-scripts`, `composition-root-factory`, `docstrings-tests`, `map-default-drop-shift`, `notifications`, `public-api-import-boundary`, `python-3.15-upgrade`, `settings-public-registry-setter`, `tenacity-rich-cachetools`) plus `archive/`. None specifies a composition root. `settings-public-registry-setter` explicitly defers this to this TODO (its D10 and its out-of-scope row "A `create_app()` / composition-root factory … Explicitly deferred by Q-11 … TODO `composition-root-factory`"). No existing factory/container exists in `src/` (`grep -rn "container|bootstrap|wire|def build_|def create_" src/` → only `build_*_source` factories and unrelated `bootstrap` docstrings).
- **Question:** Confirm this proceeds as its own change (no merge into `settings-public-registry-setter` or `public-api-import-boundary`)?
- **Recommended:** Proceed as its own change — it is the deferred target of the in-flight change, not a duplicate of it, and the only overlap (import paths) is owned by a different TODO (Q-22).
- **Answer:** **Proceed as its own change** — the recommendation, accepted. Overlap state as of 2026-10-11: `settings-public-registry-setter` merged (this change is its deferred target, not a duplicate); `composition-root-singleton-install` **dropped as absorbed** by this change (**Q-30**); `public-api-import-boundary` owns the import-path migration (**Q-22**); `startup-settings-registration-gaps` owns the registrations and lands first (**Q-27**).
- **Date:** 2026-10-11
- **Status:** ANSWERED
- **Incorporated:** yes (P.3 round 9, 2026-10-11)

## Q-27 — Dependency list correction: `structlog-logging` is already merged

- **Step:** P.2 Interrogate
- **Why needed:** The TODO's `Depends on:` gates when P.4 may start; a stale dependency would idle this change for no reason (and the orchestrator's ready-selection order reads it).
- **Context:** Measured: the TODO says "`structlog-logging` (IN-WORKFLOW — it touches startup logging setup)", but `docs/todo/structlog-logging.md` is in `docs/todo/archive/`, and `git log --oneline --merges` shows `c7a9119 Merge pull request #74 from jackthenet/crosscut/structlog-logging`; `docs/specs/logging-coverage.md` already carries the v2 amendment from that change. The live worktree list shows only `crosscut/settings-public-registry-setter` and `issue/map-default-drop-shift`.
- **Question:** Record the dependency as: hard dependency = `settings-public-registry-setter` (must merge first, Q-02); `structlog-logging` = satisfied (merged 2026-10-07, PR #74)?
- **Recommended:** Yes — the TODO's `Depends on:` line is stale and should be corrected by the orchestrator when it advances the status; only the settings change blocks this one.
- **Answer:** **Record both merged dependencies as satisfied and add the ISSUE as the live blocker** — the recommendation, accepted. `Depends on:` becomes: `settings-public-registry-setter` **satisfied** (merged 2026-10-10, PR #81, merge commit `2115faa`); `structlog-logging` **satisfied** (merged 2026-10-07, PR #74); **`startup-settings-registration-gaps` is a hard sequencing dependency** — it must merge first because the factory's expected registered-key set (**Q-24**, nine features / 34 keys) and the NFR-002 call inventory (**Q-23**) are re-derived from `main` after it lands, and it replaces the six one-liners with the ordered loop whose element order this change pins (**Q-09**).
- **Date:** 2026-10-11
- **Status:** ANSWERED
- **Incorporated:** yes (P.3 round 9, 2026-10-11)

## Q-28 — What does the returned container expose?

- **Step:** P.2 Interrogate
- **Why needed:** The container is the change's public surface: too few fields and the rewritten tests cannot assert the wiring, too many and the change invents an embedding API no spec asks for (self-consistency: every field needs a reason).
- **Context:** The AC-020 test needs the user repository, the session repository and the permission service; the AC-003 test needs the settings registry; the search wiring needs the search service (and its registered sources). Today's globals are 12 objects (`_catalog`, `_settings_registry`, `_session_repository`, `_permission_service`, `_user_repository`, `_user_manager`, `_auth_service`, `_file_repository`, `_file_service`, `_mail_service`, `_session_service`, `_search_service`) plus the two proxies (internal, never read outside the module).
- **Question:** Expose all 12 objects (plus the event bus?) as `App` fields, or only the subset the tests and an embedder need (registry, permission service, user manager + repository, session repository/service, file repository/service, auth service, mail service, search service, catalog, event bus), keeping the lazy proxies private?
- **Recommended:** Expose the 12 wired objects plus the event bus, keep the two proxies and the internal ordering private — every field is either read by a test or is a service an embedder must reach, and the proxies are a wiring detail, not API.
- **Answer:** **All 14 including the proxies** — the user chose the third option, **against** the recommendation. The container exposes every wired object including the two lazy cycle proxies (`_LazyPermissionService` and the session-lookup proxy), so the two-phase cycle wiring is visible and reachable from outside. Consequences to carry into P.4: the proxies become public API (they need docstrings and types under ruff `D` / mypy, and the `type: ignore` comments of **Q-17** stay), and the Q-16 verbatim-move answer now preserves a public surface, not a private detail.
- **Date:** 2026-10-11
- **Status:** ANSWERED
- **Incorporated:** yes (P.3 round 4, 2026-10-11)

## Q-29 — If reclassified: branch, spec, and approval PR consequences

- **Step:** P.2 Interrogate
- **Why needed:** Q-01's answer changes the artifacts this change must produce and the human gates it must pass; the orchestrator must know before P.4 creates the branch.
- **Context:** AGENTS.md Escalation Rules: on reclassification keep the worktree, `git branch -m <old> <new>`, re-run the new type's Phase P from P.1, record the reclassification in `docs/verification/composition-root-factory.md`. CROSS-CUTTING adds: a spec at `docs/specs/composition-root-factory.md` with an Impact Analysis, ADRs if a new pattern is introduced, S1.4 approval PR (human merge) before Phase 2, a task DAG, spec coverage = 100% at Phase 5, and a `minor` version bump at S6.4 (REFACTOR gets none).
- **Question:** If Q-01 is CROSS-CUTTING: confirm the branch becomes `crosscut/composition-root-factory`, a spec + Impact Analysis + amendment PR for `settings-coverage.md` REQ-002/AC-003 and `logging-coverage.md` REQ-011/AC-011 are produced at P.4, and the version bump is `minor` — and does the amendment ride in the same PR as the implementation, or a separate spec PR merged first (AGENTS.md: "Merge the spec PR before resuming implementation")?
- **Recommended:** Same change branch, but the spec amendment is committed with the spec at P.4 and reaches `main` through the change's own PR only if the reviewer accepts it; safest is the repo's established pattern (as `settings-public-registry-setter` did: the spec + the six amended specs committed at P.4/P.5 on the change branch, one approval PR at S1.4, then implementation on the same branch) — one PR, spec first in the commit order.
- **Answer:** **One branch, one approval PR** — the recommendation, accepted. Branch `crosscut/composition-root-factory`; spec `docs/specs/composition-root-factory.md` with an Impact Analysis (per affected feature: what changes, which REQ/AC IDs are touched) drafted at P.4 and self-checked at P.5; the amendment batch rides the same branch — `settings-coverage.md` REQ-002/AC-003, `logging-coverage.md` REQ-011/AC-011 (the `setup_logger` scan target, Q-08/Q-20), `settings-public-registry-setter` REQ-011/AC-016 (Q-02), plus the new REQs for the composition module's public interface and the two installs absorbed from `composition-root-singleton-install` (Q-15/Q-30). One S1.4 approval PR carries spec + amendments; implementation follows on the same branch after the human merges. Version bump: **minor** (CROSS-CUTTING, non-breaking).
- **Date:** 2026-10-11
- **Status:** ANSWERED
- **Incorporated:** yes (P.3 round 9, 2026-10-11)

### Category coverage

| Category | Coverage |
|---|---|
| Classification & Normative Basis (REFACTOR vs amendment) | covered (Q-01, Q-02, Q-29) |
| Scope & Goals / non-goals | covered (Q-25, Q-03, Q-26) |
| Interfaces & Signature (name, params, return, entrypoint) | covered (Q-04, Q-05, Q-06, Q-28) |
| Behavior & Edge Cases (order, double call, stale singletons, silent fallback) | covered (Q-09, Q-10, Q-24, Q-16) |
| Data & State (import side effects, files, DBs, singleton installs, unregistered keys) | covered (Q-11, Q-14, Q-15, Q-24) |
| Testing & Acceptance (existing tests, new tests, traceability rows) | covered (Q-12, Q-13, Q-11) |
| Architecture & Conventions (module home, `shared/` rule, proxies, STRUCTURE.md, import boundary) | covered (Q-07, Q-16, Q-21, Q-22) |
| Constraints & Quality Gates (mypy, ruff `D`, complexipy, coverage, deptry) | covered (Q-17, Q-18, Q-19, Q-20; deptry unaffected — no dependency is added or removed, measured `[tool.deptry]` has no `main.py`-specific rule) |
| NFRs (startup cost, no new dependency, no subprocess) | covered (Q-23) |
| Dependencies & Sequencing (in-flight changes, stale `Depends on:`) | covered (Q-02, Q-22, Q-27) |
| Failure modes & rollback | covered (Q-24, Q-10, Q-09) |
| Security & Secrets | skipped — the change moves existing wiring only; it adds no credential, token or password handling (the only secret-adjacent rule, `include_args=False` on traced classes, lives inside the features and is untouched — measured: `src/main.py` contains no secret handling). |
| UI / Accessibility | skipped — `src/frontend/` is empty (measured: `find src/frontend -type f` → no output) and the change touches only backend wiring. |

## Late questions (Phases 2–6)

<questions discovered after the change entered the workflow; same entry format, Step field set to the step that found it>
