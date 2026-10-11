# Questions: composition-root-singleton-install

One question file per change, created at **P.1 Frame** from this template and named `composition-root-singleton-install.md`. It replaces the retired central `AI_Questions.md` (archived at `docs/questions/archive-AI_Questions.md`).

- **Change:** composition-root-singleton-install (FEATURE)
- **TODO file:** `docs/todo/composition-root-singleton-install.md`
- **Spec:** `docs/specs/composition-root-singleton-install.md`  <!-- or n/a -->
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
- **Date:** 2026-10-10
- **Status:** PENDING | ANSWERED
- **Incorporated:** no | yes — <where: REQ-XXX / AC-XXX / spec section / decision>
```

## Preparation questions (P.2)

27 questions, one `BLOCKED-USER` batch, ordered most blocking first. All measurements are on `main` at `633a680` (2026-10-10) unless a worktree is named. Two TODO premises are **measured false** and are corrected in Q-02 / Q-17.

### Measured baseline (the evidence every entry below cites)

| Measurement | Command | Output |
|---|---|---|
| The install operations do **not** exist on `main` | `uv run python -c "import backend.permissions as p, backend.sessionmanagement as s; print(hasattr(p,'set_permission_service'), hasattr(s,'set_session_service'))"` | `False False` (`grep -rn "set_permission_service\|set_session_service" src/` → no match; only `get_*`/`reset_*`) |
| The two services are wired but not installed | `import main` in a scratch cwd, then `main._permission_service is get_permission_service()` | `False` |
| The lazy default is differently configured | same process: `get_permission_service()._catalog.features()`, `._session_lookup`, `._event_bus` | `[]`, `None`, `None` (main's service: 7 catalog features, `SqliteSessionRepository`, the shared bus) |
| The divergence is **behavioral**, not only identity | `get_permission_service().has_permission(None, "usermanagement.get_user")` vs `main._permission_service.has_permission(...)` | `False` (log: `permission check denied … reason=unknown_permission`) vs `True` |
| The session singleton is unreachable for the composed app | `get_session_service()` after `import main` | `ValueError: a repository is required to create the shared SessionService` |
| search + eventbus are **already** the root's instance | `get_search_service() is main._search_service`; `get_event_bus() is get_event_bus()` | `True`; `True` |
| Composition-root surface | `wc -l src/main.py` | `221` |
| Test-side slot resets (isolation surface) | `grep -rn "reset_permission_service()" tests/ \| wc -l` / `reset_session_service()` | `3` / `5` |
| The in-flight witness shape | `crosscut/settings-public-registry-setter` worktree, `tests/integration/singleton_install/test_composition_root.py` | `_MAIN = _SRC / "main.py"`, subprocess with scratch cwd, spy on `backend.settings.set_settings_registry` only (`len(installs) == 1`), plus an AST scan of `src/main.py` |
| That change's progress | `.github/task-runner/tasks.json` in its worktree | `tasks: 12`, 11 `VERIFIED`, T-010 `BLOCKED` on **Q-31** |

## Q-01 — Absorb or separate: which change owns the two install calls?

- **Step:** P.2 Interrogate — Phase P
- **Why needed:** `composition-root-factory` Q-15 ("Does the factory install the `PermissionService` / `SessionService` singletons?") is **the same question**, still `PENDING`, and that change rewrites the whole wiring this change would edit. If the two answers disagree the work is done twice or never; if they agree, one of the two changes is redundant.
- **Context:** `grep -n "^## Q-15" docs/questions/composition-root-factory.md` → `Answer: **PENDING**`. That change is `WAITING`, CROSS-CUTTING, and already carries a Spec Amendment PR over three specs (`settings-coverage` REQ-002/AC-003, `logging-coverage` REQ-011/AC-011, `settings-public-registry-setter` REQ-011/AC-016 — Q-01 = A, Q-02 = A). Its TODO's Out-of-scope row says "The singleton install semantics — owned by `settings-public-registry-setter`", but that change's §13 lists the factory as deferred **to this TODO**, and its REQ-011 covers only the settings registry site. File surface per option: **(A) separate (this TODO)** — `src/main.py` (+2 imports, +2 calls, ~4 lines), one new test file, `CHANGELOG.md`, version bump; **(B) merge into `composition-root-factory`** — the same 4 lines inside a diff that already moves 221 lines, so its review surface becomes "extraction **and** behavior change" in one PR; **(C) extend `settings-public-registry-setter` REQ-011** — reopens a change with 11/12 tasks `VERIFIED` and one blocked task: a new AC, a re-derived RED witness, a new task in an approved DAG, and a spec amendment to its own REQ-011.
- **Question:** Keep this as its own change (A), fold the installs into `composition-root-factory` (B), or extend the in-flight `settings-public-registry-setter` REQ-011 (C)?
- **Options:** **(A)** separate change, and answer `composition-root-factory` Q-15 = *preserve the non-install* so the two records agree · **(B)** drop this TODO and answer Q-15 = *install in the factory* · **(C)** extend REQ-011 and drop this TODO.
- **Recommended:** **A** — the extraction and the behavior change stay in separate review surfaces, and C would reopen a nearly-verified change for 4 lines; but A is only coherent if `composition-root-factory` Q-15 is answered "out of scope" in that change's P.3, so both answers must be recorded together.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-02 — Is `settings-public-registry-setter` a hard gate (the install operations do not exist on `main`)?

- **Step:** P.2 Interrogate — Phase P
- **Why needed:** The TODO's `Depends on:` line calls that change a dependency and its Constraints say "merge after it", but the workflow needs to know whether **P.4** may start before it merges (the sibling change's Q-02 answer set a hard gate for exactly this reason).
- **Context:** Measured above: `set_permission_service` / `set_session_service` return `hasattr → False` on `main`; they are added by `crosscut/settings-public-registry-setter` REQ-001 ("Each of the five singleton-owning features exports a public install operation — `set_settings_registry`, `set_event_bus`, `set_permission_service`, `set_search_service`, `set_session_service`"). **This corrects the TODO's "Affected features" claim that the install operations already exist** — they exist only on that unmerged branch. A spec drafted now would name an API that is not on `main`, and Phase 3's RED witness would fail with `AttributeError` (the in-flight change's own witness deliberately turns that into a `returncode` assertion).
- **Question:** Treat the merge of `settings-public-registry-setter` as a hard gate before **P.4** (as `composition-root-factory` Q-02 = A did), or allow P.4/P.5 now and gate only Phase 3?
- **Options:** **(A)** hard gate before P.4 · **(B)** draft now, gate implementation only.
- **Recommended:** **A** — the spec's API section and its test strategy both reference an API that only exists on an unmerged branch, and the sibling change already chose the same gate, so the backlog stays consistent.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-03 — ISSUE or FEATURE: does any approved spec require the composition root to install the services?

- **Step:** P.2 Interrogate — Phase P
- **Why needed:** The TODO asks P.2 to confirm the classification, and the type decides the whole route (ISSUE → triage + reproduction test, patch bump, no spec PR; FEATURE → spec + approval PR + DAG + minor bump).
- **Context:** Verbatim approved text: `session-management.md` **REQ-020** — "`get_session_service()` is the module singleton **for application use** (first call creates it and requires a repository; subsequent calls return the existing instance); `set_session_service()` installs a configured instance as the shared default (REQ-023)"; **REQ-023** — "The session-management feature **provides** a public install operation … installs the given `SessionService` as the shared default". `user-roles-permissions.md` **REQ-030** — "The permissions feature **provides** a public install operation …". `settings-public-registry-setter` **REQ-011** is the only composition-root install rule and it names **only** the registry: "The composition root `src/main.py` installs the registry it wires through `set_settings_registry()`…". `grep -rni "composition" docs/specs/session-management.md docs/specs/user-roles-permissions.md docs/specs/search.md docs/specs/event-bus.md` → **no output**: no approved spec says the root must install a service singleton. Precedent on the other side: `session-lookup-unwired` (archived TODO) was classified **ISSUE** for a composition-root wiring gap because it traced to REQ-017/AC-020, which *did* state the wiring.
- **Question:** Does the approved text support **FEATURE** (no ID requires the install; the getters are only "for application use"), or **ISSUE** tracing to `session-management` REQ-020/REQ-023 and `user-roles-permissions` REQ-030 — in which case a Spec Amendment PR adding a composition-root install ID is needed first?
- **Options:** **(A)** FEATURE with its own spec · **(B)** ISSUE + Spec Amendment of the two feature specs (new REQ in each naming the composition-root install).
- **Recommended:** **A (FEATURE)** — the cited IDs state what the *feature provides*, never what the *composition root does*; the closest rule (REQ-011) is scoped to the registry, so there is no ID a defect could trace to.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-04 — Which singletons are in scope: the two stale ones, or every singleton the root constructs?

- **Step:** P.2 Interrogate — Phase P
- **Why needed:** The TODO names two (`PermissionService`, `SessionService`); the honest generalisation is "every singleton the composition root constructs". The set decides the spec's REQ count, the witness's assertions, and whether the change is one commit or five.
- **Context:** Exactly five features have an install operation (`settings-public-registry-setter` REQ-001). Measured state of each after `import main`: **settings** — installed (private-slot write today, `set_settings_registry` after the in-flight change); **eventbus** — `get_event_bus()` lazy-creates and the root calls it, so `get_event_bus() is get_event_bus()` → `True`; **search** — the root calls `get_search_service(event_bus=…, settings_registry=…, permission_service=…)` and `get_search_service() is main._search_service` → `True`; **permissions** and **sessionmanagement** — constructed directly, **not** installed (`main._permission_service is get_permission_service()` → `False`; `get_session_service()` → `ValueError`). So today the stale set is exactly the TODO's two.
- **Question:** Scope = the two stale singletons, or the invariant "the root installs **all five** singletons it constructs" (making the eventbus and search installs explicit instead of relying on lazy create)?
- **Options:** **(A)** the two stale ones · **(B)** all five, explicit installs · **(C)** two installed, all five asserted in the witness.
- **Recommended:** **C** — installing the two is the fix; asserting all five costs one extra assertion and turns the lazy-create reliance (which `composition-root-factory` P.2 measured as silently stale) into a test instead of a hope.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-05 — Sequence before or after `composition-root-factory`?

- **Step:** P.2 Interrogate — Phase P
- **Why needed:** The TODO calls that change "recommended sequencing, not a hard dependency", but the two orders produce different code, different tests, and different coverage — the spec cannot be written without the answer.
- **Context:** `composition-root-factory` answers so far: **Q-03 = A** the module-level wiring in `src/main.py` is removed entirely (no compatibility layer); **Q-07 = B** the root moves to a new `src/backend/composition/` package and `src/main.py` keeps only a `__main__` shim; **Q-04/Q-05 = A** the callable is `build_composition_root() -> App` (frozen dataclass, keyword-only params). **Before** the factory: this change edits `src/main.py` module level, its witness must run `import main` in a subprocess (the established pattern — `tests/acceptance/settings_coverage/test_wiring.py`, `tests/acceptance/permissions/test_composition_wiring.py`, the in-flight `test_composition_root.py`), and the factory's Q-09 ordering invariant must then carry the two installs forward. **After** the factory: this change edits `src/backend/composition/`, the witness runs in-process against the returned `App`, and the install lines enter the coverage `source = ["src/backend", …]` set (see Q-23).
- **Question:** Land this change before `composition-root-factory` (subprocess witness, factory inherits the installs) or after it (in-process witness against `App`)?
- **Options:** **(A)** after · **(B)** before.
- **Recommended:** **A (after)** — writing a subprocess witness for wiring that is about to stop being module-level, then rewriting it in the next change, is duplicated work in two PRs; the factory is already the harder dependency of `backend-api`, so it will not wait for this.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-06 — What does the witness import: `main`, or "the composition root" by a single path constant?

- **Step:** P.2 Interrogate — Phase P
- **Why needed:** The witness must survive the module move that `composition-root-factory` Q-07 = B already decided, and the in-flight change shows how badly a path pin ages: its AC-016 witness hard-codes `_MAIN = _SRC / "main.py"` and AST-scans that one file.
- **Context:** `composition-root-factory` Q-02 = A already commits to amending `settings-public-registry-setter` REQ-011/AC-016 to be "position- and import-agnostic" precisely because AC-016's scan breaks when the wiring moves. If this change adds a **third** path-pinned scan of `src/main.py`, the same amendment has to cover three witnesses instead of two.
- **Question:** Write the witness against one module-path constant (so a later move is a one-line change), or pin it to `src/main.py` and let the next change rewrite it?
- **Recommended:** One module-path constant plus an import mechanism chosen by Q-05 — the identity assertion is the requirement; the path is an accident of where the wiring currently lives.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-07 — Collision: what if both changes add the same install call?

- **Step:** P.2 Interrogate — Phase P
- **Why needed:** Two in-flight/prepared changes editing the same 4 lines of the same file is a merge conflict and, worse, a duplicated acceptance witness with two names asserting one fact.
- **Context:** `composition-root-factory` rewrites all 221 lines of `src/main.py`; this change adds `set_permission_service(_permission_service)` and `set_session_service(_session_service)` plus two imports. If both add them: a textual conflict in the wiring and two witnesses (`test_composition_root.py`-style in both PRs). If only the factory adds them and this TODO still runs, this change's RED gate is unachievable — the behavior already exists, so no test can fail on it.
- **Question:** How is single ownership enforced — record this change as the sole owner (factory Q-15 = out of scope), or make this TODO a conditional that auto-closes if the factory installs first?
- **Recommended:** Sole owner here, with `composition-root-factory` Q-15 answered "preserve the non-install" in its P.3 — a conditional TODO cannot be gated by the READY rule, and the workflow has no auto-close mechanism.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-08 — The root injects the lazy **proxy**, not the real service: what is the identity target?

- **Step:** P.2 Interrogate — Phase P
- **Why needed:** The acceptance signal in the TODO ("`get_permission_service()` returns the very object `src/main.py` built") is ambiguous in exactly the place where the wiring is subtle, and a wrong target makes the witness either vacuous or permanently red.
- **Context:** `src/main.py` builds `_permission_service` (`:153`) and then wires **`_permission_service_proxy`** (a `_LazyPermissionService`, `:88-110`) into the six services, the settings registry, and the search service; the real instance is only reachable through `main._permission_service`. So after the install, `get_permission_service() is main._permission_service` → the real object, while every wired service still holds the **proxy** — two access paths, one underlying service. `composition-root-factory` Q-16 (do the proxies move unchanged?) is still `PENDING`, and its Q-28 recommendation keeps the proxies private to the container.
- **Question:** Does the witness assert identity against the real constructed instance (accepting that wired services hold the proxy), and must the spec state that the proxy is a wiring detail and **not** the installed singleton?
- **Recommended:** Assert against the real instance and say so in one spec sentence — installing the proxy would put a mutable indirection in the public singleton, and replacing the proxies is `composition-root-factory` Q-16's decision, not this change's.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-09 — What does the witness assert: identity only, or identity plus behavior?

- **Step:** P.2 Interrogate — Phase P
- **Why needed:** Identity alone is the weakest possible witness and would pass against a wrongly-configured install; the TODO's "Acceptance signal" names identity only.
- **Context:** Measured divergence is behavioral: `get_permission_service().has_permission(None, "usermanagement.get_user")` → `False` with `reason=unknown_permission` (the lazy default's catalog is empty: `_catalog.features()` → `[]`, `_session_lookup` → `None`, `_event_bus` → `None`) while `main._permission_service.has_permission(...)` → `True`; and `get_session_service()` raises `ValueError` today. An identity check would not catch an install of a service built with the wrong repositories; a behavior check would.
- **Question:** One AC (identity, `is`) or two (identity + one behavioral assertion through the singleton — a catalog action allowed, and `get_session_service()` callable with no repository)?
- **Recommended:** **Two** — identity pins "the instance the root built", the behavioral pair pins "built correctly", and both are one extra line each against evidence that is already measured.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-10 — Where do the two install calls go inside the root?

- **Step:** P.2 Interrogate — Phase P
- **Why needed:** "Install" is not one position: the permission service is built at `:153`, the session service at `:202`, and the install is **not retroactive**, so a consumer that resolves the singleton between construction and install gets the wrong instance.
- **Context:** `session-management.md` REQ-023 and `user-roles-permissions.md` REQ-030 both state "it is not retroactive". `settings-public-registry-setter` REQ-011 already pins an ordering rule for the registry ("the install therefore precedes the registrations"). `composition-root-factory` Q-09 (is the current call order normative, which precedences are load-bearing) is `PENDING` — if this change moves an install to a different position, it changes the order the factory then has to preserve.
- **Options:** **(A)** immediately after each construction (today's positions, minimal diff) · **(B)** grouped at the end of the root, before `setup_logger()`.
- **Recommended:** **A** — the shortest diff, and it minimises the window in which a consumer could resolve a stale singleton; grouping would widen that window for no benefit.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-11 — What invariant should the spec state (post-condition vs line order)?

- **Step:** P.2 Interrogate — Phase P
- **Why needed:** The spec needs an `INV-XXX` that a later refactor cannot silently break, but pinning line order duplicates `composition-root-factory` Q-09 and ages badly.
- **Context:** The in-flight change's REQ-011 pins positions (`:137-138`, `:173-178`, `:161`, `:198`, `:204`, `:214`) and its own Q-02 = A concedes those pins must be dropped when the wiring moves. The measurable, move-proof statement is a post-condition: after the composition root has run, each `get_*()` returns the instance the root constructed.
- **Question:** State the invariant as a post-condition of the composition root ("after it runs, every singleton it constructs is the one its getter returns"), or as an ordering rule over source positions?
- **Recommended:** Post-condition — it is exactly what the witness asserts, it survives the move to `src/backend/composition/`, and it does not collide with the factory's ordering decision.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-12 — WARNING on overwrite: does a second root run (or a test that installs twice) have to be specified?

- **Step:** P.2 Interrogate — Phase P
- **Why needed:** The TODO flags this as a risk ("a test that imports `main` twice will emit it, which some witnesses may assert on"), and the specs make the WARNING normative, so an unspecified double-install is either a silent log noise source or a flaky assertion.
- **Context:** `user-roles-permissions.md` **AC-042**: replacing a non-empty default logs "exactly one WARNING record … and given the shared default is unset … no WARNING record is logged"; `session-management.md` **AC-047** the same; **EDGE-027/EDGE-014**: the replaced service keeps working for every holder. Today the wiring runs at import time, so a second `import main` in one process is a no-op (module cache) — after `composition-root-factory`, `build_composition_root()` **can** be called twice, and its Q-10 ("Is the factory safe to call twice, and what must the caller reset?") is still `PENDING`.
- **Question:** Specify an EDGE for the second install (one WARNING per replaced singleton, previous holders unaffected), and must the witness assert **no** WARNING on the first install?
- **Recommended:** Yes to both — the WARNING is already normative in two approved specs, and asserting its absence on the first install is what proves the root installs into an empty slot rather than overwriting a test's instance.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-13 — Test isolation: how does the witness coexist with the suite's `reset_*` sites and the new slot-write guard?

- **Step:** P.2 Interrogate — Phase P
- **Why needed:** A witness that touches the composition root in-process collides with the tests that reset the same slots, and the in-flight change adds an architecture test that fails on cross-package slot writes.
- **Context:** Measured: `reset_permission_service()` appears at 3 test sites, `reset_session_service()` at 5 (`grep -rn … tests/ | wc -l`). `settings-public-registry-setter` §3.4 adds `tests/unit/architecture/test_singleton_slots.py` — "Scans every .py file under src/ and tests/ for an assignment to another package's singleton slot … A module may still write its OWN slot" — plus ruff `TID251` banned-api entries naming the private slots. `pytest-randomly` is in the suite (the T-010 evidence records RED runs with and without `-p no:randomly`), so in-process ordering is not stable.
- **Question:** Must the witness use only the public API (no slot writes, no `reset_*` of other features' singletons), and does it need a fresh interpreter (or explicit resets) so a randomly-ordered suite cannot leave a stale slot?
- **Recommended:** Public API only, and a fresh interpreter while the wiring is import-time (the pattern the three existing composition-root witnesses already use) — it sidesteps both the guard and the random ordering.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-14 — Where does the witness live (collision with the in-flight branch's test file)?

- **Step:** P.2 Interrogate — Phase P
- **Why needed:** The natural home is the file the in-flight branch is creating right now; two branches editing one new test file is a guaranteed conflict, and the repo's convention is one test file per change surface.
- **Context:** `crosscut/settings-public-registry-setter` (worktree, unmerged) creates `tests/integration/singleton_install/test_composition_root.py` for REQ-011/AC-016. Existing composition-root witnesses live elsewhere: `tests/acceptance/settings_coverage/test_wiring.py`, `tests/acceptance/permissions/test_composition_wiring.py`.
- **Options:** **(A)** new file of this change's own (e.g. `tests/acceptance/composition_root/test_singleton_install.py`) · **(B)** extend the in-flight `tests/integration/singleton_install/test_composition_root.py`.
- **Recommended:** **A** — zero conflict with an unmerged branch, and the witness belongs to this change's spec IDs, not to REQ-011.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-15 — Test category: acceptance or integration?

- **Step:** P.2 Interrogate — Phase P
- **Why needed:** The Test Category Hierarchy in AGENTS.md is normative and Phase 5 re-runs `tests/acceptance/` explicitly; a mis-filed witness is invisible to the acceptance gate.
- **Context:** "Acceptance — does the system satisfy the requirement?" vs "Integration — do the components work together?". The requirement is about the composed application satisfying a rule, and the closest precedent — `test_ac_020_composition_root_validates_session_token` from the `session-lookup-unwired` ISSUE — is filed under `tests/acceptance/permissions/`. The in-flight change filed its composition-root witness under `tests/integration/singleton_install/`.
- **Question:** File the witness as acceptance (matching the `session-lookup-unwired` precedent) or integration (matching the setter change's)?
- **Recommended:** **Acceptance** — the requirement is a system-level post-condition of startup, and Phase 5's acceptance run is the gate that must see it.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-16 — Spec home: a new spec file, or amendments to the two feature specs?

- **Step:** P.2 Interrogate — Phase P
- **Why needed:** FEATURE requires a spec, but the behavior spans two approved specs' vocabulary, and `check_traceability.py` enforces referential integrity for every ID it finds.
- **Context:** The TODO's own header allows either: "`docs/specs/composition-root-singleton-install.md` … may instead become a Spec Amendment of session-management/permissions if P.2 finds the requirement already stated" — Q-03 measured that it is **not** stated. The in-flight change shows the cost of touching approved specs: its §12 had to record a divergence for `settings.md` AC-042 and it amended five specs' ID lists.
- **Question:** One new spec (`composition-root-singleton-install.md`, REQ/AC/INV/EDGE/NFR of its own, the two feature specs untouched), or a new REQ in each of `session-management.md` and `user-roles-permissions.md` via the Spec Amendment Workflow?
- **Recommended:** **New spec** — the requirement is about the composition root, which no feature spec owns; amending two approved specs for a wiring rule adds ID churn and two changelog entries for one 4-line change.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-17 — Confirm zero feature-package change (the TODO's premise is measured false today)

- **Step:** P.2 Interrogate — Phase P
- **Why needed:** The TODO says `src/backend/permissions/` and `src/backend/sessionmanagement/` need "no code change — their install operations already exist"; on `main` they do not, so the spec must state the dependency rather than the false premise.
- **Context:** Measured: `hasattr(backend.permissions, 'set_permission_service')` → `False` on `main`; the operations are added by `crosscut/settings-public-registry-setter` REQ-001/REQ-030/REQ-023 (its §12 rows 3 and 5 name `src/backend/permissions/service.py` and `src/backend/sessionmanagement/service.py` as its own files). Also relevant: `user-roles-permissions.md` §13/Q-31 in that change is still `PENDING` on whether `get_permission_service()` gets `@logged` — a tracing decision this change must not re-litigate.
- **Question:** Confirm the scope is `src/main.py` (or `src/backend/composition/`) **plus tests only**, with every feature-package line owned by `settings-public-registry-setter`?
- **Recommended:** Confirm — this change adds two calls and two imports; anything else belongs to the change that owns the install API.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-18 — Is the lazy-create fallback (an empty-catalog default) a defect this change must fix?

- **Step:** P.2 Interrogate — Phase P
- **Why needed:** Installing from the root fixes the composed process only; any process that imports `backend.permissions` without running the root still gets a service that denies everything, and the interrogation found that this is not obviously "safe".
- **Context:** Measured: the lazy default's catalog is empty (`_catalog.features()` → `[]`), so `has_permission(None, "usermanagement.get_user")` → `False` with `reason=unknown_permission`; `src/backend/permissions/service.py:161` `self._catalog = catalog if catalog is not None else PermissionCatalog()`; `:394-395` returns `"unknown_permission"`. `user-roles-permissions.md` REQ-030/AC-028 make lazy create the specified behavior, and `composition-root-factory` P.2 measured the same class of staleness for search.
- **Options:** **(A)** out of scope, record a follow-up TODO · **(B)** in scope: make the lazy default fail loudly (or wire the catalog) — a Spec Amendment of REQ-030/AC-028.
- **Recommended:** **A** — the fix is a second behavior change with its own spec consequences, and this change's witness already pins the composed process; a follow-up TODO keeps the diff at four lines.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-19 — Non-goals: what must this change NOT do?

- **Step:** P.2 Interrogate — Phase P
- **Why needed:** The scope-boundary question the workflow requires, and the risk here is that a 4-line fix drifts into the composition-root redesign another change owns.
- **Context:** Candidate non-goals, each measured as someone else's work: **(a)** `build_composition_root()` / the `App` container / removing import-time wiring — `composition-root-factory` Q-03/Q-04/Q-07; **(b)** adding install operations to features that have none — `usermanagement`, `authentication`, `filemanagement`, `mail` have no module singleton at all (`grep -rn "def get_.*_service" src/backend/` finds none for them); **(c)** changing any service's constructor arguments or the two lazy proxies — `composition-root-factory` Q-16; **(d)** amending `settings-public-registry-setter` REQ-011/AC-016 — that change's Q-02 = A owns that amendment; **(e)** tracing `get_permission_service()` / `reset_permission_service()` — that change's Q-31; **(f)** registering the three missing `register_settings` calls — `composition-root-factory` Q-14 = C fixed them there, and `startup-settings-registration-gaps` (PREPARING) is the triage record for the gap.
- **Question:** Confirm (a)–(f) as non-goals, or move any of them into scope?
- **Recommended:** Confirm all six — each is either another change's owned work or a behavior change with its own spec consequence; this change is two install calls and their witness.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-20 — Do the four singleton-less services get one, and what about the `notifications` singleton to come?

- **Step:** P.2 Interrogate — Phase P
- **Why needed:** The TODO's out-of-scope line says "adding new install operations to features that do not have one", but a prepared change (`notifications`) is about to add a **new** module singleton, which will recreate this exact gap unless a rule exists.
- **Context:** `docs/todo/notifications.md` in scope: "a use-case service, SQLModel/SQLite storage, repository ABC + SQLite implementation, constructor DI, **module singleton + `reset_*()`** — the established feature shape (session-management is the closest template)" — note: no `set_*`. `settings-public-registry-setter` REQ-001 enumerates exactly five install operations; `usermanagement`/`authentication`/`filemanagement`/`mail` have no singleton.
- **Question:** Does this change's spec require only the five existing singletons to be installed by the root, or does it also state a forward-looking rule that any new feature singleton exposes an install operation and is installed by the root (which would constrain `notifications`)?
- **Recommended:** State the forward-looking rule as a **convention note in AGENTS.md** (Q-21), not as a REQ here — a REQ in this spec cannot gate a spec that does not exist yet, and `notifications` will read the convention.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-21 — Should AGENTS.md gain the "the composition root installs every singleton it constructs" note?

- **Step:** P.2 Interrogate — Phase P
- **Why needed:** Phase 6 check 9 requires documenting reusable shared capabilities so future changes use them correctly; without the note, the next feature repeats the gap.
- **Context:** AGENTS.md already carries per-feature "Using the …" sections and documents `get_settings_registry()` / `get_event_bus()` / `get_search_service()` usage, but says nothing about installing the root's instances. The gap this TODO exists for was invisible to every prior change precisely because no written rule stated it.
- **Question:** Add one bullet to the relevant AGENTS.md sections (and/or the settings/eventbus/search/session/permissions notes) stating the install rule, in this change's PR?
- **Recommended:** **Yes, one bullet** — it is the cheapest thing that stops the defect class from recurring, and it is exactly what Phase 6 check 9 asks for.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-22 — Version bump: minor or patch (contingent on Q-03)?

- **Step:** P.2 Interrogate — Phase P
- **Why needed:** Phase 6 step 11 bumps per type, and the CHANGELOG section (`Added` vs `Fixed`) follows the same decision.
- **Context:** `pyproject.toml` `version = "1.1.0"`; AGENTS.md bump mapping: ISSUE → patch, FEATURE → minor, CROSS-CUTTING → minor/major. If Q-03 lands on ISSUE-with-amendment, the bump and the changelog heading change with it.
- **Question:** `minor` (1.1.0 → 1.2.0, entry under `Added`) on the FEATURE classification, or `patch` (1.1.0 → 1.1.1, `Fixed`) if Q-03 reclassifies to ISSUE?
- **Recommended:** **minor** — the classification Q-03 recommends is FEATURE, and the observable change is a new guarantee about which instance the getters return.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-23 — Coverage: are the install lines measured, and does the answer depend on Q-05?

- **Step:** P.2 Interrogate — Phase P
- **Why needed:** `fail_under = 92` is a CI gate, and the same two lines are measured or not depending on which file they live in.
- **Context:** `pyproject.toml` `[tool.coverage.run] source = ["src/backend", "src/frontend"]` — **`src/main.py` is not in the measured source**, so installs added at module level are unmeasured; `composition-root-factory` Q-07 = B moves the wiring to `src/backend/composition/`, which **is** measured (its Q-20 notes exactly this). The witness runs the root, so the lines would be covered only if the witness runs in-process (Q-05/Q-13).
- **Question:** If the installs land in `src/backend/composition/`, must the witness run in-process so those lines count, and must Phase 5 re-measure the total before the PR opens?
- **Recommended:** Yes — an in-process witness both covers the lines and avoids a coverage regression when the code moves into the measured set; if this change lands before the factory, no coverage action is needed.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-24 — Does this need an ADR (S2.1 threshold)?

- **Step:** P.2 Interrogate — Phase P
- **Why needed:** Phase 2's S2.1 must either create ADRs or record the skip with a rationale, and the threshold is "new dependency, new pattern/architecture element, or cross-feature interface".
- **Context:** No new dependency; the install API is already specified by `settings-public-registry-setter`; the singleton pattern is ADR-065 ("Constructor DI plus module singleton `get_session_service()`") and the composition root is ADR-069/ADR-070. Highest existing ADR: `docs/decisions/ADR-086-scripts-type-checked-tree.md`.
- **Question:** Is "the composition root installs the singletons it constructs" a new architecture element deserving ADR-087, or is it the obvious use of an existing pattern (S2.1 records the skip)?
- **Recommended:** **Skip the ADR** — it is one call per singleton against an API that already exists; the AGENTS.md note (Q-21) is the lighter record and reaches future changes the same way.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-25 — Traceability: which rows are added, and are the two features' rows refreshed?

- **Step:** P.2 Interrogate — Phase P
- **Why needed:** `scripts/check_traceability.py` (the `traceability` CI job) fails on a missing row, an unknown ID, or a row citing a test function that does not exist, and decision Q-12 / convention B forbids refreshing rows a change did not touch.
- **Context:** `docs/verification/traceability.md` §"Issue: session-lookup-unwired" shows the established pattern: a **new** row for the composition-root witness (`test_ac_020_composition_root_validates_session_token`, `GREEN (session-lookup-unwired S5.3 …)`), with the service-level rows left untouched and the spec's own `PENDING` rows left `PENDING`. The in-flight change's rows for `session-management` REQ-023 / `user-roles-permissions` REQ-030 are recorded `PENDING (settings-public-registry-setter 2026-10-06)` and must not be refreshed by this change.
- **Question:** Add rows only for this spec's own REQ/AC (citing the new witness), leaving REQ-020/REQ-023/REQ-030 rows as they are?
- **Recommended:** Yes — convention B (Q-12): a row records the gate as observed by the change that wrote it; refreshing another change's rows is prohibited and would also mis-date the setter change's gate.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-26 — Startup-wiring collision with `startup-settings-registration-gaps` and `composition-root-factory` Q-14 = C

- **Step:** P.2 Interrogate — Phase P
- **Why needed:** Three changes now edit the same startup block, and one of them deliberately changes which settings are registered — which this change's witness could accidentally assert.
- **Context:** `composition-root-factory` **Q-14 = C** (answered 2026-10-10): "fix the three missing `register_settings` calls in this change, with a new acceptance test asserting the gap is closed". `docs/todo/startup-settings-registration-gaps.md` (PREPARING, ISSUE) is the triage record for the same gap and says in its out-of-scope: "The composition-root extraction itself (`composition-root-factory`) and the singleton installs (`composition-root-singleton-install`)". The in-flight AC-016 witness asserts six `_FEATURE_KEYS` are registered; a witness here that asserts the registered set would go red when Q-14 = C lands.
- **Question:** Must this change's witness assert **nothing** about which settings are registered (identity/behavior of the two services only), and is the registration gap confirmed as another change's work?
- **Recommended:** Yes and yes — asserting the registered set would couple this change to Q-14 = C's outcome and make an unrelated PR fail.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-27 — NFRs: what does this change promise (startup cost, dependencies, public API)?

- **Step:** P.2 Interrogate — Phase P
- **Why needed:** The spec template requires NFR IDs, and the self-consistency checklist rejects a performance budget that is not achievable under the mandated logging.
- **Context:** The two install calls are `@logged(slow_threshold_ms=5)` functions (the setter change's §9 convention), so each adds a traced call at startup; today `import main` completes in ~1.0 s (the `composition-root-factory` Q-23 measurement). No new dependency; no new public API (the operations are added by the other change); no new event (REQ-030/REQ-023: "it publishes no event").
- **Question:** Confirm the NFR set — no new dependency, no new public API, no new event, no numeric startup budget (the two traced installs are noise against the existing ~1.0 s) — or add a measured budget?
- **Recommended:** Confirm with **no numeric budget** — a budget that restates today's measurement constrains nothing, and the checklist rule only binds a budget that overlaps a mandated log operation.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

### Overlap check (every spec in `docs/specs/` + every TODO in `docs/todo/`, live and archived)

**Specs.** `docs/specs/` = authentication, event-bus, file-management, logging-coverage, logging, mail-service, search, session-management, settings-coverage, settings-public-registry-setter, settings, structlog-logging, structure-map, template, user-management, user-roles-permissions. The only composition-root install rule anywhere is `settings-public-registry-setter` **REQ-011** (settings registry only, with **AC-016** as its witness); `session-management.md` REQ-020/REQ-023 and `user-roles-permissions.md` REQ-023/REQ-030 state only what the **feature provides**, never what the root installs (`grep -rni "composition" docs/specs/session-management.md docs/specs/user-roles-permissions.md docs/specs/search.md docs/specs/event-bus.md` → no output). That change's §13 defers the composition-root redesign to `composition-root-factory` and never defers the service installs to anything — the gap is unowned.

**Live TODOs** (`ls docs/todo/`, 13 besides this one and the template):

| TODO | Status / type | Overlap verdict |
|---|---|---|
| `composition-root-factory` | WAITING / CROSS-CUTTING | **Direct overlap — its Q-15 is this TODO's question, still PENDING.** It removes module wiring (Q-03 = A), moves the root to `src/backend/composition/` (Q-07 = B), `build_composition_root() -> App` (Q-04/Q-05 = A). Q-15 must be answered "out of scope" if Q-01 = A here. |
| `settings-public-registry-setter` | WAITING / CROSS-CUTTING (11/12 VERIFIED, T-010 blocked on Q-31) | **Direct overlap — it adds the five `set_*` operations this change calls** (REQ-001) and pins the root's registry install (REQ-011/AC-016). Hard gate (Q-02). Extending REQ-011 is option C of Q-01. |
| `backend-api` | WAITING / CROSS-CUTTING | Downstream consumer: "Consumed unchanged: … permissions … sessionmanagement" — the first change that makes the stale singleton real. No install work of its own. |
| `api-keys` | WAITING / FEATURE | Downstream consumer of the permission check path; no singleton work. |
| `notifications` | WAITING / FEATURE | Will add a **new** module singleton + `reset_*()` with **no** `set_*` — the gap recurring; see Q-20/Q-21. |
| `startup-settings-registration-gaps` | PREPARING / ISSUE | Same startup block, different defect (three missing `register_settings`); explicitly excludes the singleton installs. See Q-26. |
| `public-api-import-boundary` | WAITING / REFACTOR | Owns who may import `backend.settings`/`backend.eventbus` (named in the setter change's §13); this change imports only public feature roots. No overlap. |
| `complexipy-scripts`, `docstrings-tests`, `gitattributes-line-endings`, `map-default-drop-shift`, `python-3.15-upgrade`, `tenacity-rich-cachetools` | WAITING/PREPARING | No overlap (tooling, docs, CI, dependency upgrades). |

**Archived TODOs** (`docs/todo/archive/`, 17): the only relevant record is **`session-lookup-unwired`** (MERGED, **ISSUE**) — the precedent for treating a composition-root wiring gap as a defect, and the source of the `import main`-in-a-fresh-interpreter witness pattern this change reuses (Q-13/Q-15). It traced to REQ-017/AC-020, which **did** state the wiring; nothing equivalent exists here (Q-03). `structlog-logging` (MERGED) and `architecture-tests-missing` (MERGED) touch startup/logging and architecture tests but not the installs. No other archived TODO mentions a singleton install.

**Verdict:** no double work **only if** Q-01 and `composition-root-factory` Q-15 are answered consistently; otherwise this change duplicates that one. The install of the two service singletons is currently owned by nobody.

### Category coverage

| Category | Coverage |
|---|---|
| Scope & Boundaries (non-goals) | covered (Q-19, Q-04, Q-17) |
| Classification & Governance (type, gates, ownership) | covered (Q-03, Q-01, Q-02, Q-07) |
| Interfaces & Public API | covered (Q-17, Q-20, Q-27) |
| State & Singletons (which slots, lazy create, staleness) | covered (Q-04, Q-18, Q-08) |
| Behavior & Edge Cases (WARNING, double install, non-retroactivity) | covered (Q-12, Q-09, Q-18) |
| Ordering & Lifecycle | covered (Q-10, Q-11, Q-12) |
| Interfaces to other changes (collision surface) | covered (Q-01, Q-05, Q-06, Q-07, Q-26) |
| Testing & Acceptance (witness shape, placement, category, isolation) | covered (Q-06, Q-09, Q-13, Q-14, Q-15) |
| Traceability & Spec Drift | covered (Q-16, Q-25) |
| Quality Gates (coverage, lint/types, complexipy) | covered (Q-23; lint/types are unchanged-file gates — no new module, so no skipped gate) |
| Architecture & Conventions (ADR, AGENTS.md note) | covered (Q-24, Q-21, Q-20) |
| Release & Changelog | covered (Q-22) |
| Security & Secrets | skipped — the install operations take object references, publish no event, and log no values (`user-roles-permissions.md` REQ-030, `session-management.md` REQ-023); no credential, token or file content is in scope. |
| Data & Persistence | skipped — no schema, no migration, no stored value changes; the repositories are constructed unchanged. |
| Performance | covered (Q-27 — no numeric budget, measured ~1.0 s startup context) |

## Late questions (Phases 2–6)

<questions discovered after the change entered the workflow; same entry format, Step field set to the step that found it>
