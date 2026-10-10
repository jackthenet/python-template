# Questions: startup-settings-registration-gaps

One question file per change, created at **P.1 Frame** from this template and named `startup-settings-registration-gaps.md`. It replaces the retired central `AI_Questions.md` (archived at `docs/questions/archive-AI_Questions.md`).

- **Change:** startup-settings-registration-gaps (ISSUE)
- **TODO file:** `docs/todo/startup-settings-registration-gaps.md`
- **Spec:** `docs/specs/startup-settings-registration-gaps.md`  <!-- or n/a -->
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

All measurements below were taken at `main` (`d2d58a3`, 2026-10-10) in the primary worktree.

## Q-01 — Is this a defect at all, or a spec amendment / feature?

- **Step:** P.2 Interrogate
- **Why needed:** The whole change type hinges on it. If `settings-coverage.md` never required the three features to be registered, there is no deviation from approved spec behavior and the change is not an ISSUE.
- **Context:** `docs/specs/settings-coverage.md:15` REQ-002: "**Feature-owned registration.** Each feature owns and exposes its own `register_settings(registry)`; the entrypoint calls each feature's `register_settings(registry)` once at startup." `:20` AC-003: "`main.py` wires the shared registry and **all features' settings** at startup." Against that: REQ-001 (`:14`) enumerates only logging/authentication/usermanagement/eventbus; §3.5 (`:110-127`) inventories 14 keys for those same four features; REQ-017/REQ-019 (`:51`,`:53`) and AC-024 (`:39`) enumerate the same four. Measured: nine features define `register_settings`; `src/main.py:173-178` calls six; `filemanagement`, `mail`, `sessionmanagement` have no call site anywhere in `src/` (`grep -rn "register_settings(" src/` → definitions only). After `import main`: `has("filemanagement.storage_root")`, `has("mail.smtp_host")`, `has("sessionmanagement.cleanup_batch_size")` are all `False` (16 keys missing).
- **Question:** Read REQ-002/AC-003 as "every feature that owns settings" (→ ISSUE, defect confirmed), or as scoped to the four features §3.5/REQ-017/REQ-019 enumerate (→ the spec never required it, so this is a Spec Amendment of settings-coverage or a FEATURE)?
- **Recommended:** ISSUE on the unqualified wording — AC-003 says "all features' settings", not "the four features' settings", and `permissions`/`search` were already registered outside the §3.5 inventory, so the repo has treated REQ-002 as unqualified since those two changes landed; the inventory is a stale record, not a scope limit.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-02 — Does the fix need a Spec Amendment PR to `settings-coverage.md` before implementation?

- **Step:** P.2 Interrogate
- **Why needed:** AGENTS.md forbids introducing behavior not represented in the spec without updating the spec first, and the traceability Drift Checks list "a PR changes externally observable behavior without changing the corresponding spec" as CI-detected drift.
- **Context:** Registering the three features changes externally observable behavior: 16 keys appear in `views()`/`grouped_views()`, `settings/values.yaml` gains 16 entries (measured: `registry.py:115` `_persist_values()` runs on every `register()`), and `mail.*`/`sessionmanagement.*` live reads stop falling back to hardcoded defaults (REQ-005/AC-006). §3.5's 14-key inventory and REQ-017/REQ-019/AC-024 would then understate the registry by 20 keys (34 keys total across nine features, measured).
- **Question:** Open a Spec Amendment PR widening §3.5 + REQ-017/REQ-019 + AC-024 to all nine features before Phase 3, or implement under the existing REQ-002/AC-003 and record the inventory staleness as a finding in `docs/verification/startup-settings-registration-gaps.md`?
- **Recommended:** Implement under REQ-002/AC-003 and record the inventory staleness as a finding — REQ-002 already covers it, and a §3.5 rewrite is a 20-row docs change that would need its own approval cycle; flag it as a follow-up TODO.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-03 — Which spec IDs does the triage cite as the violated requirement?

- **Step:** P.2 Interrogate
- **Why needed:** The ISSUE triage MUST cite the affected REQ/AC from an approved spec, and the traceability matrix rows decide what S5.3 updates.
- **Context:** `settings-coverage.md` REQ-002/AC-003 (matrix row `docs/verification/traceability.md:391` cites `test_main_wires_all_features`, GREEN). The three features' own specs state their registration requirement but never name the entrypoint (`grep -n "main.py" docs/specs/{file-management,mail-service,session-management,search}.md` → no hits): file-management REQ-024/AC-052, mail-service REQ-001/AC-001, session-management REQ-019/AC-039. Only `search.md:291` prescribes an entrypoint wiring block (`register_settings(get_settings_registry())`), and search **is** registered (`src/main.py:178`).
- **Question:** Cite only `settings-coverage` REQ-002 + AC-003, or also the three feature specs' registration ACs (AC-052 / AC-001 / AC-039) as affected IDs?
- **Recommended:** Cite `settings-coverage` REQ-002 + AC-003 as the violated requirement, and list the three feature ACs as "enabled by the fix" context — their own ACs are already satisfied by the feature code, so no matrix row for them changes.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-04 — Strengthen the existing AC-003 witness, or add a new one?

- **Step:** P.2 Interrogate
- **Why needed:** The reproduction test is the ISSUE's RED artifact, and `scripts/check_traceability.py` fails CI when a matrix row cites a test function that no longer exists under `tests/`.
- **Context:** `tests/acceptance/settings_coverage/test_wiring.py::test_main_wires_all_features` is the AC-003 witness (spec §10 `:311`, matrix `:391`). It asserts 4 keys from 4 already-registered features, so it passes with the defect present — near-vacuous. `check_traceability.py:18,57` collects `def test_\w+` names and fails a row whose cited name is gone.
- **Question:** Strengthen `test_main_wires_all_features` in place (same name, stronger assertions), or add a new witness function and leave the weak one?
- **Recommended:** Strengthen it in place — the existing AC-003 row stays valid, no matrix edit is forced, and leaving a known-vacuous witness that cites the same AC is the defect's second half.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-05 — What must the strengthened witness assert?

- **Step:** P.2 Interrogate
- **Why needed:** This decides whether the fix is actually guarded; a 4-key witness passed over the defect, so the assertion set is the whole point.
- **Context:** Measured registered set after `import main`: 18 keys (logging 5, authentication 7, usermanagement 1, eventbus 1, permissions 2, search 2). The three missing features add 16 (filemanagement 5, mail 8, sessionmanagement 3) → 34 total. Measured: zero duplicate keys across the nine features, so the union is exactly 34.
- **Question:** One key per feature (9 assertions), the full 34-key set, or the full set **plus** a check that no "unregistered key" fallback WARNING is emitted at startup (REQ-005/AC-006)?
- **Recommended:** The full 34-key set (the strongest cheap assertion); skip the fallback-WARNING check — it needs stdout capture of a second code path and adds a flaky coupling for no extra coverage of AC-003.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-06 — Hardcoded key list or a source scan for the expected set?

- **Step:** P.2 Interrogate
- **Why needed:** It decides whether a tenth feature can be forgotten again — the recurrence guard.
- **Context:** Measured: no test under `tests/` scans `src/backend/*/feature_settings.py` (the only `tests/` mention of `feature_settings` is `tests/mail_test_helpers.py`). The scan pattern already exists elsewhere: `tests/acceptance/logging_coverage/test_new_classes_traced.py`, `tests/acceptance/test_structure_map.py`, `tests/contract/logging/test_dependency_contract.py` all walk `src/`. A scan version is ~6 lines: glob `src/backend/*/feature_settings.py` in the parent, import each in the child, register into a scratch `SettingsRegistry(value_repository=YamlValueRepository(tempfile.mkdtemp()))`, collect `views()` keys, then assert `reg.has(k)` for every key against **main's** registry. Measured: that scratch-registration approach yields all 16 missing keys and `has()` returns True after adding the three calls.
- **Question:** Derive the expected key set by scanning `src/backend/*/feature_settings.py` (self-updating, catches a tenth feature), or hardcode the 34 keys (explicit, but stale the next time a feature is added)?
- **Recommended:** The scan — it is shorter than a 34-key literal and it is the recurrence guard for free; a hardcoded list re-creates exactly the failure mode this change fixes.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-07 — The witness cannot enumerate main's registry with `views()`; is `has()` acceptable?

- **Step:** P.2 Interrogate
- **Why needed:** It constrains the witness implementation and could otherwise produce a false RED.
- **Context:** Measured: calling `reg.views()` on the registry `import main` installs raises `backend.permissions.errors.PermissionDeniedError: permission 'settings.views' denied for the system principal (unauthorized)`. The system principal's settings permissions are `settings.register` + `settings.register_feature` (`src/backend/permissions/models.py:99-111`) plus `settings.has` + `settings.get_value` added by `src/main.py:170` — `settings.views` is granted to neither. A scratch registry built in the test child has no permission check, so it *can* enumerate `views()`; main's registry cannot.
- **Question:** Assert membership with `reg.has(key)` (permitted) over the scan-derived key set, or add `settings.views` to the bootstrap permission set so the witness can enumerate directly?
- **Recommended:** `has()` only — widening the system principal's permissions is a permissions-behavior change with its own spec IDs and is far outside this ISSUE.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-08 — Where do the three calls go, and does anything read them at construction time?

- **Step:** P.2 Interrogate
- **Why needed:** REQ-002 requires registration "before any feature code runs"; a construction-time read would make the position load-bearing.
- **Context:** `src/main.py` (221 lines) map: `SettingsRegistry(...)` `:137`, singleton slot `_settings_registry_singleton[0]` `:138`, `SqliteSessionRepository` `:145`, `PermissionService` `:153`, `set_system_permissions` `:170`, the six `register_*_settings` calls `:173-178`, `UserManager` `:182`, `AuthService` `:186`, `SqliteFileRepository` `:194`, `FileService` `:195`, `MailService` `:201`, `SessionService` `:202`, `get_search_service` `:212`, `setup_logger()` `:221`. Measured: all three features read their settings per operation — `filemanagement/service.py:204` `_read_setting` (e.g. `storage_root` at `:231`), `sessionmanagement/service.py:121` `_read_setting` (e.g. `:331`), and mail resolves a live `MailConfig` per send (`mail/service.py:112-116` `_get_transport` builds `SmtpTransportImpl` when no transport was injected) — nothing reads them at construction, and `src/main.py:201` injects no transport.
- **Question:** Append the three calls to the existing block (after `register_search_settings(_shared_settings_registry())`), keeping them before every service construction and before `setup_logger()` — and is any earlier position required by a construction-time read?
- **Recommended:** Append after the sixth call inside the existing "Register every feature's settings" block; measured, no construction-time read exists, so no reordering is needed and the diff stays three lines.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-09 — `filemanagement.storage_root` becomes registered but stays inert in the composition root. Fix that too?

- **Step:** P.2 Interrogate
- **Why needed:** It decides whether the change delivers the beneficiary the TODO claims ("settings become configurable") or registers a key that still does nothing for the wired service.
- **Context:** `src/main.py:195` constructs `FileService(SqliteFileRepository(...), LocalDiskStorageBackend("./data/files"), ...)` — an explicit backend. `filemanagement/service.py:231` reads `filemanagement.storage_root` only inside `_backend_for`, which returns the injected backend when one exists, so the setting is never consulted for the wired service. Measured after registering filemanagement: `has("filemanagement.storage_root")` is True, `get_value` returns the default `./data/files`, and the wired service still uses the constructor backend. The other 4 filemanagement keys (`max_file_size`, `avatar_max_size`, `allowed_types`, `avatar_base_url`) **do** take effect (`:213`, `:214`, `:220`, `:590`).
- **Question:** Keep the explicit `LocalDiskStorageBackend("./data/files")` (storage_root registered-but-inert for the composition root, 15 of 16 new keys live), or drop the explicit backend so the setting actually drives the storage root?
- **Recommended:** Keep it — dropping it changes which directory the wired service writes to and is a second behavior change with its own risk; record the inert key as a finding and a follow-up TODO.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-10 — Registration writes 16 new values to `settings/values.yaml` on every startup. Acceptable?

- **Step:** P.2 Interrogate
- **Why needed:** It is the change's main side effect on disk, and it is what makes the fix observable outside the process.
- **Context:** `src/backend/settings/registry.py:115` — `register()` calls `_persist_values()`, and `:400-406` persists **all** current values including defaults (REQ-009). Measured: after registering mail + filemanagement into a registry whose `values.yaml` already existed, the file contains the newly registered keys. The repo-root `settings/` directory is gitignored (`.gitignore:225`) and does not exist in a clean checkout, so this is runtime state, not committed state.
- **Question:** Is writing the 16 new keys (defaults included) to `settings/values.yaml` at startup the intended effect, with no migration or notice?
- **Recommended:** Yes — it is REQ-009 behavior the moment the keys are registered, and the whole point of the change is that these keys become part of the persisted configuration surface.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-11 — `mail.smtp_password` becomes a registered, persisted setting; NFR-002 says settings hold no passwords.

- **Step:** P.2 Interrogate
- **Why needed:** A direct conflict between two approved specs that the fix makes real for the first time.
- **Context:** `docs/specs/settings-coverage.md:222` NFR-002: "Settings values are not secrets; no credential storage. Settings do not contain passwords or tokens." `src/backend/mail/feature_settings.py` registers `mail.smtp_password` (default `""`), and the mail spec documents it as "sensitive — never in logs/events". Measured: the NFR-002 witness `tests/contract/settings_coverage/test_inventory.py::test_no_secret_settings` (`:84-94`) iterates only its 14-key `INVENTORY`, so registering the key does **not** fail it — the conflict is latent, not caught.
- **Question:** Treat NFR-002 as a finding to record (the mail feature already owns the secret handling: `@logged_class(include_args=False)`, secret-free events), or must the change resolve it (exclude the key from persistence, or amend NFR-002 to carve out credential settings)?
- **Recommended:** Record it as a finding against `mail-service.md`/`settings-coverage.md` NFR-002 and open a follow-up; resolving it means changing mail's settings design, which is far beyond three missing calls.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-12 — A stale `settings/values.yaml` now wins over defaults (REQ-011). Is that a risk to mitigate?

- **Step:** P.2 Interrogate
- **Why needed:** REQ-011 makes registration non-idempotent with respect to existing local state, so the fix can change a developer's or deployment's behavior without any code change on their side.
- **Context:** `docs/specs/settings-coverage.md:141` REQ-011: "Persisted values take precedence over definition defaults (priority: persisted > default)." Measured: with a `settings/values.yaml` containing `mail.smtp_password: "stale-secret"`, `filemanagement.storage_root: "D:/elsewhere"`, `filemanagement.max_file_size: 999`, registering the two features yields exactly those persisted values, not the defaults. Measured: no `settings/` directory exists in a clean checkout and it is gitignored (`.gitignore:225`), so the exposure is local/deployment state and test artifacts only.
- **Question:** Accept REQ-011 as specified (a persisted value winning is the feature working), or require something extra (a startup notice for newly registered keys, a values-schema version, a docs note)?
- **Recommended:** Accept it — REQ-011 is approved behavior and inventing a migration mechanism for it would be new behavior needing its own spec.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-13 — Interlock with the in-flight `settings-public-registry-setter`: merge order and its approved "six calls" wording.

- **Step:** P.2 Interrogate
- **Why needed:** Both changes edit the same lines of `src/main.py`, and the other change's spec is already approved on `main` (PR #73), so its wording can only be corrected by a Spec Amendment.
- **Context:** Measured in `../python-template_kopie-worktrees/crosscut/settings-public-registry-setter`: `src/main.py` there is 239 lines, `set_settings_registry(...)` at `:156`, and the six calls at `:191-196` now take `_shared_settings_registry()`. Its approved spec pins the count: REQ-011 refers to "the six `register_*_settings(...)` calls (`:173-178`)" and AC-016 to "the six `register_*_settings` calls and the four service-construction sites". Measured: its witness `tests/integration/singleton_install/test_composition_root.py` would **not** mechanically fail if three more calls were added — `_consumer_sites_passing_the_handle()` matches any call named `register_*_settings`, and `len(registered) == 6` counts only the six spied modules — but its `_FEATURE_KEYS` list has six entries and the spec's "six" becomes stale.
- **Question:** (a) Does this change wait for that PR to merge and then add its three calls on top (the TODO already lists it as `Depends on:`), or go first and force them to rebase? (b) Does the "six" wording in `settings-public-registry-setter.md` REQ-011/AC-016 get amended (Spec Amendment Workflow), or is a finding recorded and the wording left stale?
- **Recommended:** (a) Wait — merge after their PR lands, so this change's three-line diff applies to the final composition-root shape once. (b) Record a finding and let their change's own authors amend the wording if they want; the witness keeps passing, so nothing is broken by the stale count.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-14 — Three explicit calls, or a data-driven feature list?

- **Step:** P.2 Interrogate
- **Why needed:** It sets the diff's size and whether the fix pre-empts the planned composition-root refactor.
- **Context:** The six existing calls are explicit one-liners (`src/main.py:173-178`). `composition-root-factory` (TODO `Status: WAITING`, REFACTOR) plans to replace the module-level wiring with a `create_app()`/`build_services()` callable, and `composition-root-singleton-install` (TODO `Status: PREPARING`, FEATURE) will add `set_permission_service(...)`/`set_session_service(...)` calls to the same area. AGENTS.md prefers the smallest boring diff and forbids abstractions that were not requested.
- **Question:** Add three explicit `register_*_settings(...)` lines matching the house style, or introduce a list/loop of feature registration functions?
- **Recommended:** Three explicit calls — a loop is an unrequested abstraction in code that a planned REFACTOR will rewrite anyway, and the scan-based witness (Q-06) already provides the recurrence guard without touching production code.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-15 — Non-goals and scope boundary (mandatory).

- **Step:** P.2 Interrogate
- **Why needed:** The mandatory scope-boundary question; without it the change drifts into every settings defect the interrogation found.
- **Context:** Findings this interrogation surfaced that are **not** the missing calls: the §3.5 inventory covers 14 of 34 keys (Q-02); `permissions` registers `category="permissions"` and `sessionmanagement` registers `category="sessionmanagement", group=None`, both outside REQ-018's `application`/`security` categories (Q-23); `filemanagement.storage_root` is inert for the wired service (Q-09); NFR-002 vs `mail.smtp_password` (Q-11); the stale `STRUCTURE.md` (Q-19); the composition root itself (`composition-root-factory`, `composition-root-singleton-install`).
- **Question:** Confirm the out-of-scope list: no default value changes, no key renames/additions, no category/group fixes, no `storage_root` rewiring, no composition-root extraction or singleton installs, no §3.5 inventory rewrite, no new settings — only the three missing `register_settings` calls plus the witness that proves them?
- **Recommended:** Confirm exactly that list; each excluded item is a separate change with its own IDs, and the TODO's value score (5/5) rests on the fix being three lines.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-16 — Overlap check against every live TODO (mandatory).

- **Step:** P.2 Interrogate
- **Why needed:** The mandatory overlap question — a duplicate of existing or in-flight work must be merged, not rebuilt.
- **Context:** Live `docs/todo/` board (measured 2026-10-10): `startup-settings-registration-gaps` PREPARING, `settings-public-registry-setter` IN-WORKFLOW (spec merged, PR #73), `composition-root-singleton-install` PREPARING, `composition-root-factory` WAITING, `gitattributes-line-endings` PREPARING, `map-default-drop-shift` WAITING (PR #79), plus `api-keys`, `backend-api`, `complexipy-scripts`, `docstrings-tests`, `notifications`, `public-api-import-boundary`, `python-3.15-upgrade`, `tenacity-rich-cachetools` WAITING. `composition-root-factory` Q-14 already measured this exact gap and recommended "out of scope, open a separate TODO" — this TODO is that record. Archived `session-lookup-unwired` contributes the reusable subprocess-witness pattern only. No live TODO adds these three calls.
- **Question:** Confirm this change proceeds as its own ISSUE (not merged into `settings-public-registry-setter`, `composition-root-factory` or `composition-root-singleton-install`), and that its `Depends on: settings-public-registry-setter` ordering is honored?
- **Recommended:** Confirm — the other three changes each have a different normative basis (singleton install semantics, factory extraction, service installs), and only settings-coverage REQ-002/AC-003 covers these three calls.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-17 — Which test category and file owns the reproduction witness?

- **Step:** P.2 Interrogate
- **Why needed:** The repo enforces a category hierarchy, and the settings-coverage spec's §10 test-strategy table already maps AC-003 to a specific file.
- **Context:** `docs/specs/settings-coverage.md:297` maps AC-003 to `tests/acceptance/settings_coverage/test_wiring.py`; the file exists and holds the current witness. `tests/contract/settings_coverage/test_inventory.py` mirrors §3.5 (14 keys, four features) and its AC-022/AC-023/AC-024 tests iterate that dict, so it cannot catch this defect either.
- **Question:** Keep the witness in `tests/acceptance/settings_coverage/test_wiring.py` (acceptance, per the spec's own mapping), or also add a contract-tier guard in `test_inventory.py` (which would mean rewriting §3.5's inventory first, Q-02)?
- **Recommended:** Acceptance only, in the mapped file — a contract-tier guard requires the §3.5 rewrite this change deliberately excludes (Q-02, Q-15).
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-18 — Absorb or separate: which change adds the three `register_settings` calls?

- **Step:** P.2 Interrogate — Phase P
- **Why needed:** `composition-root-factory` Q-14 was answered **C** on 2026-10-10 — against that step's recommendation — and it assigns **this TODO's entire scope** (the three never-called `register_settings` calls plus an acceptance test asserting the gap is closed) to that change. One of the two records must give way, or the fix is done twice, or never. This is the change's first open decision: nothing else in the batch (witness shape, placement, bump) matters if the calls are not this change's work.
- **Context:** Overlap evidence, measured 2026-10-10 at `main` (`a60d109`):
  - `docs/questions/composition-root-factory.md:206-216` — Q-14 **ANSWERED C**: "fix the three missing `register_settings` calls in this change, with a new acceptance test asserting the gap is closed", and its `Incorporated:` line already reads "the separate `docs/todo/startup-settings-registration-gaps.md` TODO (score 5/5) is now absorbed by this change — its disposition (merge into this change / keep separate) is the orchestrator's next backlog decision."
  - `composition-root-factory` state: TODO `Status: WAITING`, type CROSS-CUTTING (reclassified at its P.3 Q-01 = A), **no spec, no worktree, no PR** (`ls docs/specs/composition-root-factory.md` → no such file; `git worktree list` → primary + `crosscut/settings-public-registry-setter` + `issue/map-default-drop-shift` only), and **22 of its 30 questions still PENDING** (8 `ANSWERED`). Its Q-02 = A makes `settings-public-registry-setter` a **hard gate** (its P.4 may not start before that change merges). Its Q-01 = A also plans a **Spec Amendment PR over `settings-coverage.md` REQ-002/AC-003** — the exact IDs this ISSUE cites — and its Q-12 (PENDING) proposes rewriting `test_main_wires_all_features` in-process, i.e. the very witness Q-04/Q-05/Q-06 here would strengthen.
  - `composition-root-singleton-install` (PREPARING, 27 questions) assumes the **opposite** split: its Q-26 recommends its own witness assert *nothing* about which settings are registered "the registration gap is another change's work", and its Q-01 (absorb vs separate for the two service installs) is the same open question as `composition-root-factory` Q-15 (PENDING).
  - `settings-public-registry-setter` (IN-WORKFLOW, `Status: WAITING`): spec PR #73 **MERGED**, 11/12 tasks `VERIFIED`, 1 `PENDING`, branch pushed, **no code PR open yet** (`gh pr list --state open` → only #80). Its approved REQ-011/AC-016 pin "the six `register_*_settings(...)` calls (`:173-178`)" — stale the moment any seventh call is added, whoever adds it (Q-13).
  - Other live TODOs that edit the same startup block but add **their own** registrations, never these three: `api-keys` ("Startup wiring in `src/main.py`"), `backend-api` ("Wiring: `src/main.py`"), `notifications`.
  - The gap itself, re-measured: nine `register_settings` definitions, six calls (`src/main.py:173-178`), 16 unregistered keys (filemanagement 5, mail 8, sessionmanagement 3), 34 keys total.
  - This TODO: `Status: PREPARING`, value score **5/5**, and its `## Value triage` `Decision:` field is still the unfilled placeholder `<the user's answer + date>` — so under AGENTS.md it **may not pass P.4** (branch + worktree) until the user records an implement / merge / drop decision, which is this question.
  - Measured consequences per option: **(A) absorb** — this TODO and its question file move to `docs/todo/archive/` + `docs/questions/archive/` with `Status: DROPPED`; the fix and its witness ride a CROSS-CUTTING PR that does not exist yet, behind a hard dependency on the setter and behind 22 unanswered P.3 questions; the `settings-coverage` REQ-002/AC-003 amendment and the 16-key behavior change are reviewed inside a 221-line wiring move; no version bump of its own (the factory bumps `minor`/`major`). **(B) separate, landing after the factory** — the calls would already exist, so no deviation from REQ-002/AC-003 would remain to triage: the ISSUE would have nothing to reproduce (no RED) and would have to be reclassified or dropped at P.4. **(C) separate, landing before the factory, with factory Q-14 re-answered out-of-scope at its P.3** — a 3-line fix + strengthened witness ships as a small ISSUE PR right after the setter merges (`patch` bump); the factory then moves already-correct wiring, its amendment to REQ-002/AC-003 shrinks to the wiring *mechanism*, and `composition-root-singleton-install` Q-26 stays coherent.
- **Question:** (A) drop/merge this TODO into `composition-root-factory` (honoring its Q-14 = C), (B) keep it separate but only after that change lands, or (C) keep it separate, land it first, and re-answer `composition-root-factory` Q-14 as out-of-scope at that change's P.3?
- **Options:** **(A)** absorb — this TODO `DROPPED` + archived, witness in the factory's PR · **(B)** separate but after the factory — no defect left to reproduce at P.4 · **(C)** separate and first — factory Q-14 re-answered A (out of scope) in the same P.3 round.
- **Recommended:** **C** — the fix is three lines and a 5/5 quick win, while A parks it behind a hard dependency, a PR that does not exist and 22 unanswered questions; C only holds if `composition-root-factory` Q-14 is re-answered in that change's P.3, so both answers must be recorded in the same round.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-19 — `STRUCTURE.md` is stale on `main` and the map test is RED: does this change regenerate the map, and what is the recorded baseline?

- **Step:** P.2 Interrogate — Phase P
- **Why needed:** Phase 5's full-suite gate ◆ cannot pass over a pre-existing failure, and AGENTS.md requires `STRUCTURE.md` to be regenerated in the same commit as the `.py` change — this change edits `src/main.py`. The ISSUE's RED gate also has to distinguish its own reproduction failure from an inherited one.
- **Context:** Measured at `main` (`a60d109`): `uv run python scripts/make_map.py --check` → `STRUCTURE.md is out of date — run uv run python scripts/make_map.py`, exit 1. `uv run pytest tests/ -q` → **1 failed, 815 passed, 1 skipped in 248.31s**; the single failure is `tests/acceptance/test_structure_map.py::test_ac_021_committed_map_matches_fresh_render` (`docs/ — 225 files (process record)` committed vs `231` fresh — the planning records added since the last render). `STRUCTURE.md:1627` records `#### src/main.py (221 lines)`, so the map is stale for this change twice over: the inherited `docs/` count **and** the 3 lines this change adds. The staleness is not this change's defect, but the failing test is in the gate this change must pass.
- **Question:** Regenerate `STRUCTURE.md` inside this change (which clears the inherited `test_ac_021` RED as a side effect), or leave the map alone and record `test_ac_021` as a pre-existing failure the Phase 5 gate tolerates?
- **Recommended:** Regenerate it in the same commit as the `src/main.py` edit — AGENTS.md already mandates it for any `.py` change, it is a generated file that is never hand-merged, and it is the only way the Phase 5 full-suite gate can go GREEN; record the inherited staleness in the triage record as the baseline (1 failed / 815 passed).
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-20 — Is registering the 16 keys value-neutral today, and is a registration-time exception a risk to guard?

- **Step:** P.2 Interrogate — Phase P
- **Why needed:** The triage must state the defect's blast radius — does the fix change any effective value, and can the three new calls break `import main`? — and Phase 5 needs to know what regression to expect (and what not to guard against).
- **Context:** Measured: every fallback the three features pass to `_read_setting` is the **same** constant or literal as the registered default — `filemanagement/service.py:213,214,220,231,590,596` use the `DEFAULT_*` constants defined at `filemanagement/feature_settings.py:24-38`; `sessionmanagement/service.py:146,224,331` use `DEFAULT_MAX_SESSIONS_PER_USER` / `DEFAULT_MAX_LISTED_SESSIONS` / `DEFAULT_CLEANUP_BATCH_SIZE` (`service.py:49-51`, the same objects the registrations pass at `:39,:46,:53`); `mail/feature_settings.py:54-61` repeat the identical literals registered at `:74,:83,:94,:103,:112,:121,:130,:140`. So with nothing persisted, registering changes **no** effective value — only the ability to set one. Failure-mode probe (scratch script outside the repo, temp `YamlValueRepository`, all nine `register_settings` called into one registry): **34 keys, zero exceptions, 63.79 ms total, 0 events published** (`register()` publishes nothing; only `set_value` publishes `SettingChanged`). `register()` raises `SettingsRegistrationError` on a duplicate key (`registry.py:103-106`), and measured there are zero duplicate keys across the nine features — so the three added calls cannot raise on a fresh registry.
- **Question:** Confirm the triage states "value-neutral until a value is persisted" (no default drift, no exception path, no events, ~64 ms) as the blast radius, with **no** defensive `try`/`except` around the three calls?
- **Recommended:** Confirm, no guard — drift and duplicate-key risk are measured zero, and a `try`/`except` around registration would reintroduce exactly the silent-fallback class this change removes.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-21 — Version bump and `CHANGELOG.md` entry for an ISSUE whose behavior delta is 16 keys.

- **Step:** P.2 Interrogate — Phase P
- **Why needed:** Phase 6 requires a type-mapped bump and one changelog line in the reviewed PR; both depend on Q-18 (if the fix is absorbed, neither is this change's) and on which release the entry lands in.
- **Context:** AGENTS.md Versioning: ISSUE → `patch`; `pyproject.toml:4` `version = "1.1.0"` is the single source of truth; `CHANGELOG.md:10` `## [Unreleased]` already carries entries from un-bumped changes, and the root changelog is hand-maintained (`bump-my-version` touches only `pyproject.toml`). The in-flight `settings-public-registry-setter` (CROSS-CUTTING, `minor`) and `composition-root-factory` (`minor`/`major`) have pending bumps too, so this change's entry may be swept into either release.
- **Question:** `bump-my-version bump patch` in this change's PR with one `Fixed` line naming the 16 keys, or no bump/entry here because Q-18 = A moves the work to the factory's PR?
- **Recommended:** `patch` + one `Fixed` line ("`src/main.py` now registers the filemanagement, mail and sessionmanagement settings; their 16 keys stop falling back to hardcoded defaults") — the mapping is fixed by the type, and the entry is traceable to what the diff does; if Q-18 = A, the same line rides that PR instead.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-22 — The strengthened witness runs `main` with `cwd=_REPO_ROOT`: must it isolate the settings/data directories?

- **Step:** P.2 Interrogate — Phase P
- **Why needed:** After the fix, the witness's own subprocess persists 34 values into the **repository root**, and REQ-011 feeds them back into the next run — the witness can go false-green or flaky, and it writes state into a developer's working tree. This decides the strengthened test's shape (Q-04/Q-05/Q-06).
- **Context:** Measured: `tests/acceptance/settings_coverage/test_wiring.py` runs `python -c "…"` with `cwd=_REPO_ROOT` and pre-installs a temp-dir registry at `:18`, but `src/main.py:137-138` builds its own `SettingsRegistry(...)` and overwrites the singleton slot, so that pre-install does **not** isolate the value repository. Running the full suite on `main` just now created `settings/values.yaml` in the repository root containing **18 keys** (exactly the currently registered set); after this fix it would be 34, and a leftover value (e.g. `filemanagement.max_file_size: 999`) would win over the defaults by REQ-011 and change what the subprocess asserts. `data/` and `logs/` are likewise created in the repo root (gitignored at `.gitignore:225,230,231`). The isolation pattern already exists in the repo: `tests/acceptance/permissions/test_composition_wiring.py` runs its subprocess with `cwd=tmp_path`. Note the witness's `sys.path.insert(0, 'src')` is relative, so a `cwd=tmp_path` version must pass an absolute `src` path.
- **Question:** Does the strengthened witness isolate (run with `cwd=tmp_path` + absolute `sys.path`, like the permissions wiring test), or keep `cwd=_REPO_ROOT` and accept the persisted-values coupling?
- **Recommended:** Isolate — it is a two-line change to the same test this change already rewrites, and without it the witness's own run seeds the REQ-011 precedence that can make it pass or fail for reasons unrelated to the wiring.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-23 — Registering `sessionmanagement` makes a REQ-018/AC-023 violation visible in the views hierarchy. Confirm it stays out of scope.

- **Step:** P.2 Interrogate — Phase P
- **Why needed:** Q-15's out-of-scope list names "no category/group fixes" but the finding was never recorded as a question, and the triage must not silently absorb (or silently inherit) a second approved-spec violation.
- **Context:** `docs/specs/settings-coverage.md:148` REQ-018: "Each feature's settings use `category` = domain (`application`/`security`) and `group` = feature name for the views hierarchy"; AC-023 (`:182`) is its Given/When/Then. Measured `category=` values across the nine `feature_settings.py`: 22 `application`, 8 `security`, **1 `category="permissions"` and 3 `category="sessionmanagement"`** — four keys outside the closed domain set, three of them in a feature this change registers, so after the fix `grouped_views()` renders a `sessionmanagement` category that REQ-018 does not allow. CI cannot see it: `tests/contract/settings_coverage/test_inventory.py::test_category_group` (`:65`) iterates only its 14-key `INVENTORY` and `_registry_with_all_features()` (`:40-52`) registers only the four original features, so registering the three in `main` cannot fail it; the spec's own test-strategy row (`:331`) still lists `test_category_group` as `PENDING`.
- **Question:** Confirm the four out-of-domain `category` values stay out of scope (recorded as a finding + follow-up TODO against REQ-018/AC-023), rather than being fixed here or written into the triage as intended behavior?
- **Recommended:** Out of scope, recorded as a finding — changing four definitions' `category` is a separate behavior change with its own AC-023 evidence, and fixing it here would widen a three-line ISSUE into a second spec's remediation (Q-15's boundary).
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

<!-- PART3 -->

### Category coverage

| Category | Coverage |
|---|---|
| Classification & Normative Basis (ISSUE vs amendment/feature, cited IDs) | covered (Q-01, Q-02, Q-03) |
| Scope & Boundaries (non-goals — mandatory) | covered (Q-15, Q-14, Q-23) |
| Overlap & Sequencing against other changes (mandatory) | covered (Q-16, Q-13, Q-18) |
| Interfaces & Public API (which registry accessor the witness may use, `register_settings` shape) | covered (Q-07, Q-14) |
| Behavior & Edge Cases (live reads, inert `storage_root`, default drift, registration failure) | covered (Q-09, Q-12, Q-20) |
| Data & Persistence (`settings/values.yaml`, REQ-011 precedence, test-run side effects) | covered (Q-10, Q-12, Q-22) |
| Security & Secrets (NFR-002 vs `mail.smtp_password`) | covered (Q-11) |
| Ordering & Lifecycle (call position, construction-time reads) | covered (Q-08) |
| Testing & Acceptance (strengthen vs new witness, assertion set, recurrence guard, category/file, isolation) | covered (Q-04, Q-05, Q-06, Q-17, Q-22) |
| Traceability & Spec Drift (matrix rows, §3.5 inventory, CI referential integrity) | covered (Q-02, Q-03, Q-04) |
| Quality Gates & Baseline (full-suite state, `STRUCTURE.md`, ruff/mypy) | covered (Q-19; ruff and mypy are unchanged-file gates here — the change adds no module, so no new gate applies) |
| Release & Changelog (bump level, `CHANGELOG.md` entry) | covered (Q-21) |
| Performance & NFRs (startup cost, events, dependencies) | covered (Q-20 — measured 63.79 ms for all nine registrations, 0 events, no dependency added) |
| Architecture & Conventions (ADR, AGENTS.md capability note) | skipped — an ISSUE runs no Phase 2, so no ADR is required (AGENTS.md Phase Matrix: Decompose "— (skip; the triage is the plan)"), and the Phase 6 AGENTS.md note applies only to a reusable shared capability, which three call-site lines are not; the code-shape question the category would otherwise raise is asked as Q-14. |
| UI / Accessibility | skipped — no frontend exists (measured: `find src/frontend -type f` → no output) and the change touches backend wiring only. |

## Late questions (Phases 2–6)

<questions discovered after the change entered the workflow; same entry format, Step field set to the step that found it>
