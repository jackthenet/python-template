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

<!-- PART3 -->

### Category coverage

<one row per interrogation category this change uses: `covered (Q-nn / E-nn)` or `skipped — <reason>`. Required for every change type; it sits **on top of** the ≥ 20-question floor, never instead of it.>

## Late questions (Phases 2–6)

<questions discovered after the change entered the workflow; same entry format, Step field set to the step that found it>
