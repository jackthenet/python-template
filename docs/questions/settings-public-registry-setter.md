# Questions: settings-public-registry-setter

One question file per change, created at **P.1 Frame** from this template and named `settings-public-registry-setter.md`.

- **Change:** settings-public-registry-setter (**CROSS-CUTTING** — reclassified from FEATURE at P.3 on 2026-10-06: Q-2 = all five module singletons)
- **TODO file:** `docs/todo/settings-public-registry-setter.md`
- **Spec:** `docs/specs/settings.md` + `event-bus.md` + `user-roles-permissions.md` + `search.md` + `session-management.md` (all five amended)
- **Opened:** 2026-10-04
- **Status:** OPEN  <!-- 16 of 29 answered (round 4, 2026-10-06) -->
- **Answer rounds:** 4

Every question that needs user input is recorded HERE — never in a central file. A step that needs input records **all** of its open questions in one batch and returns `BLOCKED-USER`; the orchestrator presents them (as few `ask_user_question` rounds as possible, ≤ 4 per round, most blocking first), records the answers here, marks each **ANSWERED** and **incorporated**, and relaunches the step **once** with the full answer set.

### Entry format

```markdown
## Q-<n> — <short title>
- **Step:** <P.2 Interrogate, or Sx.x <step name> — Phase <n>>
- **Why needed:** <the ambiguity, missing requirement, or decision>
- **Context:** <what the step had learned at the time>
- **Question:** <the question for the user>
- **Answer:** <the user's answer>  (or **PENDING**)
- **Date:** <YYYY-MM-DD>
- **Status:** PENDING | ANSWERED
- **Incorporated:** no | yes — <where: REQ-XXX / AC-XXX / spec section / decision>
```

## Preparation questions (P.2)

### P.2 preamble — 2026-10-05

**Batch:** **29 questions (Q-1 … Q-29)** recorded in one `BLOCKED-USER` batch (FEATURE minimum: 20). No answers are recorded here; the orchestrator presents them (≤ 4 per round, most blocking first) and records the answers below each question.

**Measured site counts** — re-measured on `main` @ `2bc94e3` (2026-10-05). The TODO's "6 test files / 9 sites" is confirmed; two of its citations are stale and are corrected here:

| What | Measured | Where |
|---|---|---|
| The private holder | 1 | `src/backend/settings/registry.py:45` — `_registry: list[SettingsRegistry | None] = [None]`. **There is no `src/backend/settings/_setup.py`** (the TODO and the task-definition name it; `_setup.py` exists only in `backend.logging`). |
| Writes to it **inside** the owning package | 3 (2 writes + 1 read) | `registry.py:368` (read), `:373` (lazy create), `:380` (reset) |
| Writes **outside** the package | **10** in **7** files | `src/main.py:138` (1) + **9** in **6** test files: `tests/settings_test_helpers.py:132,160,180`; `tests/acceptance/settings_coverage/test_setup_logger.py:31,55`; `tests/acceptance/settings_coverage/test_wiring.py:18` (inside a subprocess source string); `tests/contract/logging/test_logging_contracts.py:35`; `tests/property/logging/test_logging_properties.py:42`; `tests/unit/logging/test_logging_edges.py:32` |
| `src/main.py` line numbers | drifted by 1 | import at **`:68`** (`from backend.settings.registry import _registry as _settings_registry_singleton`), construct+install at **`:137-138`** — the TODO and `docs/verification/architecture-tests-missing.md` cite `:67` / `:136-137` |
| Imports of `backend.settings.registry` from outside the package | 16 lines in 11 files | 1 in `src/main.py:68` (imports the **private** name) + 15 in 10 test files. Of the 15: **9** import the module to reach the slot, **6** import only **public** symbols from the private module path (`tests/acceptance/logging_coverage/test_behavior_unchanged.py:19`, `test_direct_loguru_kept.py:16`, `test_levels.py:23`, `test_services_traced.py:34`, `tests/property/logging_coverage/test_invariants.py:32`, `tests/logging_coverage_test_helpers.py:40`) |
| The test helpers that wrap the slot | used by **30** test files | `isolated_registry` / `restore_singleton` / `install_isolated_registry` (`tests/settings_test_helpers.py`) — migrating the 3 helper sites covers most of the suite |
| `reset_settings_registry()` call sites | 3, all in `tests/settings_test_helpers.py:126,158,178` | — |
| The same private-list singleton pattern elsewhere | **5** holders, **no** `set_*` setter anywhere in `src/backend` (`grep '^def set_'` → 0) | `settings/registry.py:45` `_registry`; `eventbus/eventbus.py:212` `_default_bus`; `permissions/service.py:504` `_permission_service`; `search/service.py:546` `_singleton` (**the only one guarded by a `threading.Lock`**, `:547,558`); `sessionmanagement/service.py:344` `_session_service` |
| Outside-module writes to the **other** holders | 2 | `tests/eventbus_test_helpers.py:77,84` (`_default_bus[0]`; `:76,81,85` are reads) — `src/main.py` writes **only** the settings slot |
| Lazy-creation thread-safety | settings/eventbus/permissions/sessionmanagement create **without a lock**; only `search` locks | `settings/registry.py:368-373` vs `search/service.py:558-563` |

**Overlap check** (`docs/specs/` + every `docs/todo/` file, 2026-10-05):

- **`architecture-tests-missing` — MERGED** (PR #65 → `4f684f8`; TODO `Status: MERGED` at `718034d`). Its **F-1** is this change's origin and its `Depends on:` is therefore satisfied. Two of its decisions bind here: it created **no** `tests/architecture/` directory, and its **F-2** records that **no** boundary enforcement exists (its Q-4 CI guard was offered and **not** taken) — so any guard added here needs a new home and a new mechanism (Q-18).
- **`structlog-logging` — WAITING, CROSS-CUTTING, worktree live** at `../python-template_kopie-worktrees/crosscut/structlog-logging`. It amends `docs/specs/logging.md`, **`docs/specs/logging-coverage.md`** and `docs/specs/settings.md` (already v4, wording only, no ID changed), and rewrites direct-loguru statements **in `src/backend/settings/registry.py`**. Overlap with this change: the `@logged` tracing rules and the logging-coverage §3.1 inventory (Q-14/Q-15) and the same file. It does **not** touch the settings singleton — no functional collision, but a rebase is likely.
- **`ruff-d-docstrings` — PREPARING (DOCS/CHORE)**: its own Q&A (`docs/questions/ruff-d-docstrings.md:62`) already flags the same-file overlap in `src/backend/settings/` (14 `D1xx`). It will add docstrings to whatever this change adds — no conflict, but the new function must be docstring-clean from the start.
- **`structure-map` — QUESTIONS-ANSWERED (FEATURE)**: generates `STRUCTURE.md` from the tree; a new public function changes the generated map, but the map is generated, so nothing to coordinate.
- **`permissions` / `search` / `sessionmanagement` / `eventbus`**: no in-flight TODO touches their singletons; `docs/todo/notifications.md` and `docs/todo/api-keys.md` reference the settings registry only as a consumer. The "same setter for the other four holders" option (Q-2/Q-27) is therefore **not** covered by any other planned change.
- **`codecov-coverage-badge` — PREPARING**: its P.2 preamble already lists this change as "no overlap".

**Feature brief (intermediate — folded into the spec at P.4).** *Goals:* retire the cross-feature private-singleton write (`src/main.py:138` + 9 test sites) behind a public, specified install operation on the settings feature; keep the composed application byte-for-byte equivalent (the wired instance at `src/main.py:137` carries `permission_service=_permission_service_proxy`, which a lazily created default does **not** — `registry.py:373` builds `SettingsRegistry()` with no permission service, i.e. standalone mode). *Constraints:* `docs/specs/settings.md` REQ-014 (`:235`) and the §3 API block (`:176-177`) name only `get_settings_registry()` / `reset_settings_registry()`; `docs/specs/settings-coverage.md` REQ-012/AC-016/EDGE-011 pin the guarded read (`required=False`, no side effect) and must not be contradicted; NFR-002 (`:346`) requires the public API stay backward-compatible; startup wiring order must not move (`tests/acceptance/settings_coverage/test_wiring.py` executes `main.py` in a subprocess and asserts the registrations landed). *Out of scope:* value/template behavior, kinds, validation, storage, events; the three import fixes already merged; the lazy-proxy wiring in `src/main.py`. *Edge cases:* double install; install after a lazy creation; install then `reset_settings_registry()`; install while other threads read; consumers constructed before the install; the three subprocess-embedded writes.

---

## Q-1 — Public setter, dependency injection, or a test-only override
- **Step:** P.2 Interrogate
- **Why needed:** The whole change assumes "add a public setter". That is one of three shapes, and the other two change the spec, the scope and the classification. Nothing in the repo decides it.
- **Context:** `src/main.py:68,137-138` writes the private slot to install the proxy-wired registry; `get_settings_registry()` (`src/backend/settings/registry.py:361`) lazily creates a **default** instance with no `permission_service` (`:373`), so it cannot substitute. Seven feature call sites read the global today: `eventbus/eventbus.py:52`, `filemanagement/service.py:190`, `logging/_settings.py:37`, `mail/feature_settings.py:52`, `permissions/service.py:486`, `search/service.py:457`, `sessionmanagement/service.py:108`.
- **Question:** Which shape does the fix take?
- **Options:**
  - **(Recommended) A public setter on the settings feature** (`set_settings_registry(...)`) — smallest diff; one new public symbol; all 10 outside-package writes become public-API calls; the global access point stays.
  - **Pure dependency injection (no global)** — every consumer takes the registry explicitly; removes the global entirely, but rewrites 7 features and their specs (CROSS-CUTTING, several spec amendments).
  - **A test-only override helper plus a documented exception for `src/main.py`** — fixes 9 of 10 sites with no spec amendment, but leaves the composition root's cross-feature private import, which is the finding's actual subject.
- **Answer:** A public setter on each feature's public API — `set_settings_registry(...)` and its four siblings (matching Q-2 = all five). Chosen over pure DI after weighing the measured cost: the construction cycles (`PermissionService` <-> `UserManager`, `SettingsRegistry` <-> `PermissionService`, `src/main.py:100-127`) survive DI, the globals are also in-feature fallbacks (`settings/registry.py:68`, `filemanagement/service.py:190`, `sessionmanagement/service.py:90,108`, `logging/_setup.py:127`, `mail/feature_settings.py:52`), and the singleton is specified behavior (REQ-013/REQ-014/REQ-020), so removing it is a behavior amendment, not a boundary fix. DI remains possible later as its own REFACTOR TODO.
- **Date:** 2026-10-06
- **Status:** ANSWERED
- **Incorporated:** yes — spec amendment shape: new REQ per affected spec (Q-4), classification CROSS-CUTTING (Q-2)

## Q-2 — Settings only, or the same setter for all five singletons (classification)
- **Step:** P.2 Interrogate
- **Why needed:** This decides whether the change stays **FEATURE** (one spec) or becomes **CROSS-CUTTING** (five specs + an Impact Analysis) — it must be settled before P.4 drafts anything.
- **Context:** The identical private-list holder exists in five features (`settings/registry.py:45`, `eventbus/eventbus.py:212`, `permissions/service.py:504`, `search/service.py:546`, `sessionmanagement/service.py:344`) and **no** `set_*` setter exists anywhere in `src/backend`. Outside-module writes exist only for settings (10) and eventbus (`tests/eventbus_test_helpers.py:77,84`).
- **Question:** Does this change add the install operation to the settings feature only, or to every feature that has a module singleton?
- **Options:**
  - **(Recommended) Settings only (FEATURE)** — one spec amendment; the other four holders have no composition-root writer, so nothing forces them.
  - **All five now (CROSS-CUTTING)** — retires the pattern repo-wide in one change, but amends five specs (`settings`, `event-bus`, `user-roles-permissions`, `search`, `session-management`) and needs a per-feature Impact Analysis.
  - **Settings now + one backlog item per remaining feature** — keeps this change small and makes the rest explicit; the pattern stays until each item runs.
- **Answer:** All five module singletons now — `settings`, `eventbus`, `permissions`, `search`, `sessionmanagement`. **Reclassification: FEATURE -> CROSS-CUTTING** (five specs touched intentionally, new shared pattern). Consequences recorded in `docs/todo/settings-public-registry-setter.md`: Impact Analysis over the five features, an ADR for the public install operation, spec amendments in `settings.md`, `event-bus.md`, `user-roles-permissions.md`, `search.md`, `session-management.md`, and a `minor` version bump.
- **Date:** 2026-10-06
- **Status:** ANSWERED
- **Incorporated:** yes — TODO reclassified CROSS-CUTTING; P.4 drafts the spec with an Impact Analysis

## Q-3 — One spec PR or two (amendment mechanics)
- **Step:** P.2 Interrogate
- **Why needed:** The TODO states "Spec amendment first … through its own PR before implementation", but this change is a FEATURE whose own S1.4 PR already carries a spec change. Two readings give a different PR count and a different RED/GREEN sequence.
- **Context:** `AGENTS.md` Spec Amendment Workflow steps 1 and 6 (new PR, merge before resuming implementation) vs the FEATURE path where P.4 writes the spec on the change branch and S1.4 opens it for approval. `docs/specs/settings.md:3-6` shows amendments recorded as a Changelog version (`v4 (2026-10-04) … change structlog-logging`), i.e. an amendment carried by the changing feature's own PR.
- **Question:** Is the `docs/specs/settings.md` amendment a separate PR merged before the change branch is created, or is it the content of this change's own S1.4 approval PR?
- **Options:**
  - **(Recommended) One PR: the S1.4 approval PR carries the amended `settings.md`** (Changelog v5, new IDs), merged before Phase 2 — one human approval, matches how `structlog-logging` amended this same spec at v4.
  - **Two PRs: amendment-only PR merged first, then the change branch re-based** — follows the Spec Amendment Workflow literally; costs a second approval and a rebase, and the amendment PR has no tests to show.
  - **One PR with spec and code together** — cheapest, but implementation would precede spec approval (Spec Approval Gate violation).
- **Answer:** One PR: this change's own S1.4 approval PR carries the amended specs (Changelog v5 in `docs/specs/settings.md`, plus the four sibling amendments), merged before Phase 2. Precedent: `structlog-logging` amended the same spec at v4.
- **Date:** 2026-10-06
- **Status:** ANSWERED
- **Incorporated:** yes — P.4 writes the amended specs on the change branch; S1.4 opens the single approval PR

## Q-4 — Amend REQ-014 in place or add a new REQ beside it
- **Step:** P.2 Interrogate
- **Why needed:** REQ-014 is the ID the amendment touches, and its existing GREEN row (`docs/verification/traceability.md:106`, `test_ac_018_singleton`) is a historical gate record under Convention B. Rewriting the sentence changes what that row records.
- **Context:** `docs/specs/settings.md:235` REQ-014: "The settings feature provides a shared default registry: `get_settings_registry()` returns a singleton for features, `SettingsRegistry` is instantiable for tests/DI, and `reset_settings_registry()` resets the default for tests." AC-018 (`:269`) covers only "called twice → same instance". Next free IDs in this spec: REQ-026, AC-040, INV-011, EDGE-030, NFR-005. D8 (`:27`) also names only the two functions.
- **Question:** How is the new install operation written into the spec?
- **Options:**
  - **(Recommended) Add a new REQ-026 for the install operation (with its own AC/EDGE), and extend REQ-014's sentence only where it enumerates the singleton surface** — AC-018's existing row keeps describing the wording it was written against.
  - **Rewrite REQ-014 in place to name the setter** — one requirement carries the whole surface, but the dated AC-018 row then points at different wording.
  - **Add it to D8 and the §3 API block only, no new REQ** — cheapest, but fails the Self-Consistency Checklist ("every in-scope item has at least one REQ").
- **Answer:** Add a new REQ beside the existing singleton requirement (`REQ-026` in `docs/specs/settings.md`, next free IDs REQ-026 / AC-040 / INV-011 / EDGE-030 / NFR-005), with its own AC/EDGE, and extend REQ-014 only where it enumerates the singleton surface. The dated AC-018 row (`docs/verification/traceability.md:106`, `test_ac_018_singleton`) is left as a historical gate record (Convention B). Same pattern applied to the other four specs.
- **Date:** 2026-10-06
- **Status:** ANSWERED
- **Incorporated:** yes — P.4 drafts REQ-026 + AC/EDGE per spec

## Q-5 — What a second install does
- **Step:** P.2 Interrogate
- **Why needed:** The spec is silent, and the current private write is an unconditional assignment used by save/restore helpers that install repeatedly (`tests/settings_test_helpers.py:132,160,180`). The chosen semantics decide the error contract and the test migration.
- **Context:** `registry.py:373` (lazy write) and `src/main.py:138` (composition-root write) both assign unconditionally; `search/service.py:559` guards its lazy creation with `if _singleton[0] is None` under a lock.
- **Question:** When the slot already holds a registry and the setter is called again, what happens?
- **Options:**
  - **(Recommended) Replace unconditionally, no error** — matches every current call site; the save/restore pattern keeps working.
  - **Replace, and log a WARNING when the slot was non-empty** — same semantics, plus an audit trail for accidental double installs.
  - **Install only when the slot is empty and return the existing instance** — makes a second install a no-op, but breaks the test save/restore pattern.
  - **Raise if the slot is already occupied** — strongest guard, but every helper then has to reset first (3 reset sites).
- **Answer:** Replace unconditionally, and log a WARNING when the slot was non-empty. Same semantics every current call site already relies on (`registry.py:373`, `src/main.py:138`, the save/restore helpers at `tests/settings_test_helpers.py:132,160,180`), plus an audit trail for an accidental double install. The WARNING is a one-off log statement (semantic level WARNING), not a new mechanism; `include_args=False` so no wired instance is formatted into the record.
- **Date:** 2026-10-06
- **Status:** ANSWERED
- **Incorporated:** yes — new EDGE + the setter's REQ text in each of the five specs; a WARNING-level assertion in the acceptance test

## Q-6 — The setter's name
- **Step:** P.2 Interrogate
- **Why needed:** It becomes a public, spec-named symbol (`docs/specs/settings.md` §3 API block, `__all__`, and the AGENTS.md "Using the Settings Feature" section). Renaming later is a breaking change under NFR-002 (`:346`).
- **Context:** The feature's existing pair is `get_settings_registry()` / `reset_settings_registry()`; the registry already has `set_value` / `reset` (`registry.py`), so `set_` is the feature's own verb for "put a value in".
- **Question:** What is the public name?
- **Options:**
  - **(Recommended) `set_settings_registry(registry)`** — mirrors `get_`/`reset_` and the feature's `set_value`; the name the F-1 record and the TODO already use.
  - **`install_settings_registry(registry)`** — reads as a one-time wiring step, but introduces a second verb family for the singleton.
  - **`use_settings_registry(registry)`** — short, but says nothing about replace-vs-if-absent.
- **Answer:** `set_settings_registry(registry)` and its four siblings (`set_event_bus`, `set_permission_service`, `set_search_service`, `set_session_service`). Mirrors the existing `get_`/`reset_` pair and the feature's own `set_value`; the name already used in the F-1 record and this TODO. Renaming later would break NFR-002.
- **Date:** 2026-10-06
- **Status:** ANSWERED
- **Incorporated:** yes — named in each spec's §3 API block + `__all__` + the AGENTS.md usage notes

## Q-7 — Does the setter accept `None` to clear?
- **Step:** P.2 Interrogate
- **Why needed:** Two ways to clear (the setter with `None`, and `reset_settings_registry()`) can disagree, and the spec must say which is normative.
- **Context:** `reset_settings_registry()` (`registry.py:378`) sets the slot to `None` and is specified as "resets the default **for tests**" (REQ-014, `:235`); it has exactly 3 call sites, all in `tests/settings_test_helpers.py:126,158,178`.
- **Question:** Is `None` a legal argument to the setter (a clearing install)?
- **Options:**
  - **(Recommended) No — the parameter is a `SettingsRegistry`; clearing stays `reset_settings_registry()`** — one clear path, no new semantics.
  - **Yes — `set_settings_registry(None)` clears** — one entry point for install and clear, but two supported ways to clear unless reset is then deprecated.
  - **Yes, and deprecate `reset_settings_registry()`** — fewer names, but breaks NFR-002 backward compatibility and the 3 existing call sites.
- **Answer:** No — the parameter is the concrete instance; clearing stays `reset_settings_registry()`. One clear path, no new semantics, and REQ-014's existing wording (and its dated AC-018 row) is left as written.
- **Date:** 2026-10-06
- **Status:** ANSWERED
- **Incorporated:** yes — the setter's signature and the parameter type in each spec

## Q-8 — What the setter returns
- **Step:** P.2 Interrogate
- **Why needed:** It is part of the public signature in the spec's API block and decides how the test helpers read after an install.
- **Context:** `reset_settings_registry() -> None` (`registry.py:378`); `get_settings_registry()` returns the instance. The helpers currently do `saved = get_settings_registry(required=False)` … `_registry[0] = saved` (`tests/settings_test_helpers.py:176-180`).
- **Question:** What is the return type?
- **Options:**
  - **(Recommended) `None`** — mirrors `reset_settings_registry()`; the caller already holds the object.
  - **The installed `SettingsRegistry`** — chainable, and makes an install-if-absent result usable.
  - **The previously installed instance (`SettingsRegistry | None`)** — turns the helpers' save/restore into one call, but is a new concept in the API.
- **Answer:** `None` — mirrors `reset_settings_registry() -> None`; the caller already holds the object it installed. The test helpers keep their explicit save/restore shape (`settings_test_helpers.py:176-180`).
- **Date:** 2026-10-06
- **Status:** ANSWERED
- **Incorporated:** yes — the signature in each spec's API block

## Q-9 — Parameter type: the concrete class or a protocol
- **Step:** P.2 Interrogate
- **Why needed:** It decides whether tests may install a fake registry, and whether a new public interface (ABC/Protocol) enters the spec.
- **Context:** `SettingsRegistry.__init__` (`registry.py:47-53`) takes `event_bus`, `template_repository`, `value_repository`, `permission_service`; the feature already uses ABCs for repositories (`TemplateRepository`, `ValueRepository`) and structural protocols elsewhere (`EventPublisher`, `PermissionChecker`). No registry protocol exists.
- **Question:** What type does the setter accept?
- **Options:**
  - **(Recommended) `SettingsRegistry` (the concrete class)** — matches the spec's API block and every existing use; no new interface.
  - **A structural protocol/ABC for "something registry-shaped"** — lets fakes be installed, but adds a new public interface and a second spec-level concept nothing else uses.
- **Answer:** The concrete class (`SettingsRegistry`, and each feature's own concrete service class for the four siblings). Matches each spec's §3 API block and every existing use; no new public interface. A fake is still installable by constructing a real instance with the existing repository ABCs / structural protocols.
- **Date:** 2026-10-06
- **Status:** ANSWERED
- **Incorporated:** yes — the setter signature in each spec's API block

## Q-10 — Thread-safety of the setter itself
- **Step:** P.2 Interrogate
- **Why needed:** The spec says "The registry is thread-safe" (`docs/specs/settings.md:22`) but says nothing about the singleton slot; the repo is inconsistent about guarding it, so the new public function needs an explicit decision.
- **Context:** `search/service.py:547,558,571` guards its slot with `threading.Lock`; `settings/registry.py:368-373`, `eventbus/eventbus.py:216-222`, `permissions/service.py:514-524`, `sessionmanagement/service.py:359-364` do not.
- **Question:** Must the setter guard its write?
- **Options:**
  - **(Recommended) Yes — a module-level `threading.Lock`, matching `search`** — one lock, no observable change single-threaded, and it makes the REQ's thread-safety claim true for the slot too.
  - **No — a single list assignment is atomic under CPython** — smallest code, but leaves the spec's thread-safety sentence unqualified.
- **Answer:** Yes — a module-level `threading.Lock` per owning feature, matching the only existing precedent (`search/service.py:547,558,571`). No observable change single-threaded, and it makes each spec's existing thread-safety claim (`settings.md:22`) true of the slot as well as the instance. Applies to all five holders (Q-2), which also retires the settings/eventbus/permissions/sessionmanagement inconsistency.
- **Date:** 2026-10-06
- **Status:** ANSWERED
- **Incorporated:** yes — the setter's REQ text + the concurrency AC (Q-12) in each of the five specs

## Q-11 — Does this change also guard the lazy creation in `get_settings_registry()`?
- **Step:** P.2 Interrogate
- **Why needed:** If the setter takes a lock but the lazy path does not, the two can still race (two threads each create a registry; one is discarded). Fixing it is a behavior-adjacent change to an existing requirement, so it needs an explicit yes/no.
- **Context:** `registry.py:368-373` reads the slot, and if empty creates and writes it — no lock. `search/service.py:558-563` does the same under `_singleton_lock`.
- **Question:** Does this change also make the lazy creation in `get_settings_registry()` take the lock?
- **Options:**
  - **(Recommended) Yes — the same lock around the create-and-write** — closes the race the setter would otherwise leave open; a 3-line change in the owner module.
  - **No — out of scope; record it as a follow-up finding** — keeps the diff to the new function, but the race stays.
  - **Yes, and also guard `reset_settings_registry()`** — full symmetry across the three slot operations, slightly larger diff.
- **Answer:** Yes — and guard `reset_settings_registry()` too: all three slot operations (install / lazy create / reset) take the same lock, mirroring `search/service.py:558-563`. Closes the create-race the setter alone would leave open (two threads each create an instance, one silently discarded). Slightly larger diff than the recommended option; `reset` has only 3 call sites (`tests/settings_test_helpers.py:126,158,178`), so the blast radius is small. Applied per feature for the five holders.
- **Date:** 2026-10-06
- **Status:** ANSWERED
- **Incorporated:** yes — the singleton REQ in each spec now names the guarded slot; a new AC covers the create-race

## Q-12 — How thread-safety is made normative
- **Step:** P.2 Interrogate
- **Why needed:** P.4 must give every normative statement an ID and a test; an untestable "it is thread-safe" sentence fails the Self-Consistency Checklist.
- **Context:** `docs/specs/settings.md` §6 INV-001…INV-010 are all property-testable value invariants; §8 NFR categories are Performance / Contract / Resource / Observability; `AGENTS.md` requires a Hypothesis property test for every `INV-XXX`.
- **Question:** In what form does the install's concurrency behavior enter the spec?
- **Options:**
  - **(Recommended) An AC in Given/When/Then form** (install from N threads → every reader sees one of the installed instances, never a half-written slot) — executable, no property-test machinery.
  - **An `INV-XXX` + a Hypothesis property test** — matches the invariant convention, but a property test over installs is awkward and flaky.
  - **Prose in the REQ text only, no ID** — cheapest, but the checklist then flags an untestable normative claim.
- **Answer:** An AC in Given/When/Then form (e.g. 'install from N threads → every reader sees one of the installed instances, never a half-written slot'), one per affected spec. Executable as a plain acceptance test; no Hypothesis machinery, so the INV convention (`AGENTS.md`: a property test per INV-XXX) is not bent to cover concurrency.
- **Date:** 2026-10-06
- **Status:** ANSWERED
- **Incorporated:** yes — new AC IDs in the five specs, mapped to acceptance tests in the P.4 test strategy

## Q-13 — Does the package's own lazy creation call the setter?
- **Step:** P.2 Interrogate
- **Why needed:** It decides whether there is one write path or two inside the owner module, and whether the lazy path inherits the setter's tracing and lock behavior.
- **Context:** `registry.py:373` writes `_registry[0]` directly inside `get_settings_registry()`; the feature's own tests assert on the record counts produced by these functions (`tests/acceptance/logging_coverage/test_services_traced.py`).
- **Question:** After the setter exists, does `get_settings_registry()`'s lazy creation keep writing the slot directly, or call the public setter?
- **Options:**
  - **(Recommended) Keep the direct write inside the owner module** — the owner may touch its own slot; no nested logging on the lazy path.
  - **Call the setter from the lazy path** — one write path and one lock, but every lazy creation now emits a second traced call and its log records change.
- **Answer:** Keep the direct write inside the owning module — the owner may touch its own slot. No nested logging on the lazy path, so the traced-record counts asserted by `tests/acceptance/logging_coverage/test_services_traced.py` stay unchanged. The lazy path still takes the lock decided at Q-11.
- **Date:** 2026-10-06
- **Status:** ANSWERED
- **Incorporated:** yes — the singleton REQ wording; no change to the traced-function inventory

## Q-14 — Tracing of the new public function
- **Step:** P.2 Interrogate
- **Why needed:** `AGENTS.md` requires `@logged` on public module-level functions, and the two neighbours pin a concrete parameter set; the new function must match or deliberately differ.
- **Context:** `get_settings_registry` and `reset_settings_registry` are both `@logged(slow_threshold_ms=5)` with default `include_args` (`registry.py:360,377`); `docs/specs/logging-coverage.md:62-63` lists them with `include_args` = "default". `AGENTS.md` mandates `include_args=False` for handlers of secrets — a registry object is not a secret, but formatting it yields a bare `<backend.settings.registry.SettingsRegistry object at 0x…>`.
- **Question:** What tracing does the setter get?
- **Options:**
  - **(Recommended) `@logged(slow_threshold_ms=5)`, default `include_args`** — identical to its two neighbours.
  - **`@logged(slow_threshold_ms=5, include_args=False)`** — keeps the record clean (the argument repr carries nothing useful).
  - **`@logged(slow_threshold_ms=50)`** — treats an install as a heavier operation than a read.
- **Answer:** `@logged(slow_threshold_ms=5)` with default `include_args` — identical to its two neighbours `get_settings_registry()` / `reset_settings_registry()` (`registry.py:361,378`), and the same for the four siblings. The shared logging feature's tracing policy (public module-level functions traced with `@logged`) is satisfied with no new parameter choice.
- **Date:** 2026-10-06
- **Status:** ANSWERED
- **Incorporated:** yes — the new function is traced; recorded in the logging-coverage row (Q-15)

## Q-15 — Does the logging-coverage inventory get a row too?
- **Step:** P.2 Interrogate
- **Why needed:** `docs/specs/logging-coverage.md` REQ-001 calls its §3.1 table the **normative inventory of every public class and public module function**; a new public module function makes that table incomplete, so a second spec may be touched — which feeds back into the classification (Q-2).
- **Context:** `docs/specs/logging-coverage.md:32,112` (REQ-001), `:116` (REQ-005, every public module-level function traced), `:62-63` (the two settings singleton functions). `tests/acceptance/logging_coverage/test_inventory.py` only checks that listed entries are traced — it does **not** enumerate `src/`, so nothing fails automatically. `structlog-logging` (in flight) amends the same file.
- **Question:** Does this change add a `set_settings_registry()` row to `docs/specs/logging-coverage.md` §3.1?
- **Options:**
  - **(Recommended) Yes, in the same amendment** — keeps REQ-001's inventory true; touches a second spec (a row, not a requirement change).
  - **No — rely on REQ-005 ("every public module-level function is traced")** — one spec touched, but the inventory silently drifts and AC-001's "every … is listed" claim weakens.
  - **Defer to a separate chore** — keeps this change to one spec and records the gap.
- **Answer:** Yes — add a `set_settings_registry()` row (and the four sibling rows) to `docs/specs/logging-coverage.md` §3.1 in the same amendment, so REQ-001's normative inventory stays true. Consequence: this change touches **six** specs, not five (`settings`, `event-bus`, `user-roles-permissions`, `search`, `session-management`, `logging-coverage`), and `structlog-logging` amends the same file — a rebase is expected and is recorded in the TODO's `Depends on:` note.
- **Date:** 2026-10-06
- **Status:** ANSWERED
- **Incorporated:** yes — §3.1 rows added; the Impact Analysis lists logging-coverage as an affected spec

## Q-16 — Which of the 9 test sites migrate
- **Step:** P.2 Interrogate
- **Why needed:** The TODO's acceptance signal (`rg "from backend.settings._setup import" src tests` returns nothing) is only reachable if the test sites move; migrating them touches 30 files' shared helpers and risks weakening isolation behavior.
- **Context:** 9 write sites in 6 test files (listed in the preamble); the three in `tests/settings_test_helpers.py` are the ones 30 test files actually use; `isolated_registry` also depends on `reset_settings_registry()` and on `get_settings_registry(required=False)` as the save step.
- **Question:** What is the migration scope in `tests/`?
- **Options:**
  - **(Recommended) All 9 sites** — the acceptance signal holds and the helpers become the documented pattern; each helper keeps its exact save/restore semantics.
  - **Only `tests/settings_test_helpers.py` (3 sites)** — the shared helpers are fixed and the other 6 files keep their direct write; the signal then needs an exception list.
  - **None — `src/main.py` only** — smallest diff, but the leak the finding describes stays in the suite.
- **Answer:** All 9 test sites migrate to the public setter. The acceptance signal then holds with no exception list, and the three shared helpers (`isolated_registry`, `restore_singleton`, `install_isolated_registry` in `tests/settings_test_helpers.py`, used by 30 test files) become the documented pattern. Each helper keeps its exact save/restore semantics; no test is weakened.
- **Date:** 2026-10-06
- **Status:** ANSWERED
- **Incorporated:** yes — in-scope list + the acceptance signal restated with the correct module path (`backend.settings.registry`, not `_setup`)

## Q-17 — The three subprocess-embedded writes
- **Step:** P.2 Interrogate
- **Why needed:** These writes live inside a **string** executed by a subprocess, so a plain `rg` for the import is not enough and rewriting them changes what the test proves.
- **Context:** `tests/acceptance/settings_coverage/test_wiring.py:17-18` and `test_setup_logger.py:31,55` build a `python -c` program that does `from backend.settings import registry as _reg_mod` then `_reg_mod._registry[0] = …` before importing `main` / calling `setup_logger()`.
- **Question:** How are these three sites handled?
- **Options:**
  - **(Recommended) Migrate the embedded code too** (`from backend.settings import set_settings_registry; set_settings_registry(reg)`) — the `rg` signal holds and the subprocess still proves the same wiring.
  - **Exempt them and scope the acceptance signal to importable test code** — no risk to the subprocess tests, but the private write survives in the suite.
  - **Rewrite them as in-process tests** — removes the subprocess, but changes what AC-003/AC-019 prove (import-time wiring in a fresh interpreter).
- **Answer:** **PENDING**
- **Date:** 2026-10-05
- **Status:** PENDING
- **Incorporated:** no

## Q-18 — Is a regression guard added, and with which mechanism
- **Step:** P.2 Interrogate
- **Why needed:** `architecture-tests-missing` F-2 records that the 3 import fixes it made are **unguarded** and that no `tests/architecture/` directory exists; without a decision here, the same private write can return undetected.
- **Context:** `docs/verification/architecture-tests-missing.md` (F-2: "no CI-enforced boundary rule — no new job, no ruff `TID251` / banned-api configuration (Q-4 offered it and it was **not** taken)"). Existing precedent for a repo-wide static check: `scripts/check_traceability.py` wired into `.github/workflows/spec-validation.yml`; `pyproject.toml` `[tool.ruff.lint] select` currently has no `TID`.
- **Question:** Does this change add a guard that fails if a cross-package write to `_registry` returns?
- **Options:**
  - **(Recommended) A pytest guard under `tests/unit/` that scans `src/` and `tests/` for the private-slot write** — executable, no new directory, no new lint family; one file.
  - **ruff `TID251` banned-api entries in `pyproject.toml`** — CI-enforced and automatic, but adds a lint rule family the repo has deliberately kept out (the `pyproject-tooling-gaps` precedent puts lint additions in their own change).
  - **A `scripts/` check added to `quality_check`** — matches the traceability-check pattern, but touches CI.
  - **None — the manual Phase 6 checks 3–4 stay the only guard** — consistent with the ATM decision, but leaves the regression open.
- **Answer:** **PENDING**
- **Date:** 2026-10-05
- **Status:** PENDING
- **Incorporated:** no

## Q-19 — How wide is the guard's ban
- **Step:** P.2 Interrogate
- **Why needed:** 6 test lines import **public** settings symbols from the **private module path** `backend.settings.registry`; `AGENTS.md` says "Import the public API only", so a guard could ban those too — that is 6 more file edits and a different claim.
- **Context:** `tests/acceptance/logging_coverage/test_behavior_unchanged.py:19`, `test_direct_loguru_kept.py:16`, `test_levels.py:23`, `test_services_traced.py:34`, `tests/property/logging_coverage/test_invariants.py:32`, `tests/logging_coverage_test_helpers.py:40`. The logging feature's own tests legitimately import its private modules.
- **Question:** What does the guard (or the acceptance signal) cover?
- **Options:**
  - **(Recommended) Only the private-name slot (`_registry`)** — exactly the finding's subject; the 6 public-symbol imports stay as they are.
  - **Also the 6 public-symbol imports from `backend.settings.registry`** — satisfies "import the public API only" for this feature, +6 file edits in the logging-coverage suite.
  - **Every feature's private module path, repo-wide** — a general rule, much larger, and it collides with each feature's own tests and with `structlog-logging`'s work in `src/backend/logging/`.
- **Answer:** **PENDING**
- **Date:** 2026-10-05
- **Status:** PENDING
- **Incorporated:** no

## Q-20 — Does `src/main.py` keep its local reference or read the global back
- **Step:** P.2 Interrogate
- **Why needed:** It decides the shape of the composition root after the migration and whether an extra global read is introduced into startup.
- **Context:** `src/main.py:137-138` builds `_settings_registry` and installs it; the same local is then passed explicitly to `register_*_settings(...)` (`:173-178`) and to four service constructors (`:198,204,214`).
- **Question:** After installing through the public setter, does `main.py` keep using its local object?
- **Options:**
  - **(Recommended) Keep the local and pass it explicitly; install once** — object identity and wiring order are unchanged.
  - **Install, then read back with `get_settings_registry()` everywhere** — one source of truth at startup, but adds reads that would silently pick up a different instance if the install moved.
- **Answer:** **PENDING**
- **Date:** 2026-10-05
- **Status:** PENDING
- **Incorporated:** no

## Q-21 — Must the install stay at module-import time in its current position
- **Step:** P.2 Interrogate
- **Why needed:** The TODO forbids reordering startup wiring, but a public setter makes a move tempting; a test asserts the current order's effect.
- **Context:** `tests/acceptance/settings_coverage/test_wiring.py` runs `main.py` in a subprocess and asserts `logging.log_level`, `authentication.session_ttl`, `usermanagement.roles`, `eventbus.max_queue_size` are all registered (`settings-coverage.md` AC-003 / REQ-002: "the entrypoint calls each feature's `register_settings(registry)` once at startup"). `src/main.py:137-138` sits before the registrations (`:173-178`) and before the `PermissionService` construction (`:150-161`).
- **Question:** Is the install required to stay at module-import time, in its current position?
- **Options:**
  - **(Recommended) Yes — same position, module import time** — AC-003's subprocess test keeps proving the same wiring; zero ordering risk.
  - **Allow moving it into a `create_app()`/`main()` body** — cleaner composition, but changes when the singleton exists for every import of `main` and needs AC-003 re-derived.
- **Answer:** **PENDING**
- **Date:** 2026-10-05
- **Status:** PENDING
- **Incorporated:** no

## Q-22 — Consumers constructed before an install
- **Step:** P.2 Interrogate
- **Why needed:** An install does not retro-change objects that took the registry in their constructor; the spec must say so or the next reader treats the setter as a global rewire.
- **Context:** `search/service.py:551` and `sessionmanagement/service.py:348` accept `settings_registry` at construction and keep it; `filemanagement/service.py:190` and `sessionmanagement/service.py:108` read `get_settings_registry()` live on each use.
- **Question:** Does the spec state that an install only affects later `get_settings_registry()` calls?
- **Options:**
  - **(Recommended) Yes — state it in the REQ (and one AC)** — honest and cheap; documents the difference between live readers and constructor-injected ones.
  - **Make the install propagate to already-built consumers** — would need a new registry-identity mechanism and API in other features.
  - **Say nothing** — no spec cost now, a surprise later.
- **Answer:** **PENDING**
- **Date:** 2026-10-05
- **Status:** PENDING
- **Incorporated:** no

## Q-23 — Does the setter validate its argument
- **Step:** P.2 Interrogate
- **Why needed:** It is a global mutation reachable from any feature; whether it guards its input is a trust-boundary decision the spec must state.
- **Context:** The feature raises typed errors for bad input elsewhere (`SettingsRegistrationError`, `SettingsValidationError`); the test-isolation rule in `AGENTS.md` ("Test registries MUST pass an explicit isolated value repository") is currently unenforced, and the default repository is `YamlValueRepository("settings")` (`registry.py:52`).
- **Question:** Does the setter reject anything?
- **Options:**
  - **(Recommended) No runtime check — the annotation plus mypy** — matches the feature's existing style; no new exception path.
  - **Reject a non-`SettingsRegistry` argument with a typed error** — a guard on a global mutation, but a new error case to specify and test.
  - **Also reject a registry using the shared default `settings/` value repository** — enforces the AGENTS.md isolation rule, but inspects private state and is fragile.
- **Answer:** **PENDING**
- **Date:** 2026-10-05
- **Status:** PENDING
- **Incorporated:** no

## Q-24 — Is "no private-slot write remains" itself a requirement
- **Step:** P.2 Interrogate
- **Why needed:** The TODO states it as a plain-language acceptance signal (`rg` returns nothing). If it is to be checked in CI it needs an ID and a test; if it is not, P.4 must not write a REQ that nothing can satisfy.
- **Context:** `docs/specs/settings.md` NFR-002 (`:346`) already constrains the public API's shape; `scripts/check_traceability.py` requires every REQ/AC defined in a spec to have a matrix row with a real test function.
- **Question:** Does the spec carry the "install only through the public API" claim normatively?
- **Options:**
  - **(Recommended) No — keep it a plain-language signal in the verification record** — the spec specifies behavior, not import hygiene of other packages.
  - **Yes, as an NFR (Contract)** — gives a Q-18 guard a requirement to trace to, and makes the boundary durable.
  - **Yes, as an AC in Given/When/Then form** — same effect, phrased as behavior.
- **Answer:** **PENDING**
- **Date:** 2026-10-05
- **Status:** PENDING
- **Incorporated:** no

## Q-25 — Version bump
- **Step:** P.2 Interrogate
- **Why needed:** `AGENTS.md` maps FEATURE → minor, but this change's own value triage says it "changes no user-visible behavior" — the bump should be decided, not assumed.
- **Context:** `pyproject.toml:4` `version = "0.6.1"`; `[tool.bumpversion]` `tag = false`; the bump happens at S6.4 with a clean tree.
- **Question:** Which bump, if any?
- **Options:**
  - **(Recommended) `minor` → 0.7.0** — the type's mapping (a new public API symbol is externally observable to consumers of the package).
  - **`patch` → 0.6.2** — argues no user-visible behavior; contradicts the bump mapping for FEATURE.
  - **None** — only defensible after reclassifying to REFACTOR, which the new public symbol rules out.
- **Answer:** **PENDING**
- **Date:** 2026-10-05
- **Status:** PENDING
- **Incorporated:** no

## Q-26 — Does `AGENTS.md` gain a "how to use this" note
- **Step:** P.2 Interrogate
- **Why needed:** Phase 6 step 9 requires documenting reusable shared capabilities in `AGENTS.md`; the settings section currently tells readers only about `get_settings_registry()`.
- **Context:** `AGENTS.md` "Using the Settings Feature" — "Get the registry. Use `get_settings_registry()` … or instantiate `SettingsRegistry(...)` for tests/DI"; nothing about installing a configured instance.
- **Question:** Is the new section line added?
- **Options:**
  - **(Recommended) Yes — one bullet** (install the wired registry once at the composition root; tests use the helper, never the slot) — future changes copy the right pattern.
  - **No — the spec's API block is the reference** — smaller diff, and the next composition root may reach for the private slot again.
- **Answer:** **PENDING**
- **Date:** 2026-10-05
- **Status:** PENDING
- **Incorporated:** no

## Q-27 — The event-bus test helper's two writes
- **Step:** P.2 Interrogate
- **Why needed:** It is the only other outside-module slot write in the repo; leaving it makes the change's boundary explicit, taking it changes the type.
- **Context:** `tests/eventbus_test_helpers.py:77,84` write `_default_bus[0]`; `eventbus/eventbus.py:212` has no setter, and `docs/specs/event-bus.md` specifies only `get_event_bus()` / `reset_event_bus()`.
- **Question:** Are those two sites in this change's scope?
- **Options:**
  - **(Recommended) Out of scope — record a follow-up backlog item** — the event-bus spec needs its own amendment; keeps this change to one spec.
  - **In scope (this change becomes CROSS-CUTTING)** — retires both leaks at once; two spec amendments and an Impact Analysis.
  - **In scope as a test-only change that keeps the private write behind one helper** — no spec change, but the pattern survives.
- **Answer:** **PENDING**
- **Date:** 2026-10-05
- **Status:** PENDING
- **Incorporated:** no

## Q-28 — Is `reset_settings_registry()` still test-only
- **Step:** P.2 Interrogate
- **Why needed:** REQ-014 calls reset "for tests". Once a public install exists, reset becomes the natural production-side counterpart, and the install → reset → lazy-default sequence has no AC today.
- **Context:** REQ-014 (`docs/specs/settings.md:235`): "`reset_settings_registry()` resets the default for tests"; `registry.py:378` sets the slot to `None`, after which the next `get_settings_registry()` creates a **default** instance (`:373`).
- **Question:** What is reset's status after the amendment?
- **Options:**
  - **(Recommended) Stays the documented test-oriented clear; the amendment names install/reset as the pair with one AC for install → reset → lazy default** — no new semantics, and the sequence stops being unspecified.
  - **Becomes a supported production operation too** — REQ-014's "for tests" wording changes, and the existing AC-018 row's context shifts.
  - **Left as REQ-014 already words it** — smallest spec change, but the install/reset interaction stays untested.
- **Answer:** **PENDING**
- **Date:** 2026-10-05
- **Status:** PENDING
- **Incorporated:** no

## Q-29 — Does an install publish an event
- **Step:** P.2 Interrogate
- **Why needed:** The feature's event surface is closed by design (D7), and an install is a wiring change other features might want to react to; the spec must say which it is.
- **Context:** `docs/specs/settings.md:31` D7: "Value changes publish `SettingChanged` … **no other events are published**"; REQ-024 (`:245`) lists exactly the value operations that publish.
- **Question:** Does installing a registry publish an event to the bus?
- **Options:**
  - **(Recommended) No — installing is wiring, not a value change; D7 stays** — no new event ID, no consumer changes.
  - **Yes — publish a `SettingsRegistryInstalled` event** — lets features re-read wiring after an install, but contradicts D7 and adds an event ID plus consumers.
- **Answer:** **PENDING**
- **Date:** 2026-10-05
- **Status:** PENDING
- **Incorporated:** no

## Late questions (Phases 2–6)

(none yet)
