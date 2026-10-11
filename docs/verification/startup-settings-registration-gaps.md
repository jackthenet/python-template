# startup-settings-registration-gaps — Triage Record (ISSUE)

- **Change:** startup-settings-registration-gaps · **Type:** **ISSUE** (classified at P.1, first matching criterion: "fixes a deviation from **approved spec behavior**; no new behavior is introduced"; re-confirmed by the user at **Q-01** and **Q-24**)
- **Branch / worktree:** `issue/startup-settings-registration-gaps` @ base `25b7e7b` (== `main`, `pyproject.toml:4` version `1.2.0`), worktree `../python-template_kopie-worktrees/issue/startup-settings-registration-gaps` — created at **P.4** from `main` (git skill, "Create change worktree (P.4)"), so the branch carries the TODO file and the answered question file as of P.3.
- **Normative basis:** the approved specs `docs/specs/settings-coverage.md` (primary), `docs/specs/settings-public-registry-setter.md`, `docs/specs/file-management.md`, `docs/specs/user-roles-permissions.md`, `docs/specs/session-management.md`. No new spec (AGENTS.md "ISSUE (triage — no spec, no PR)").
- **Phase Matrix for this type:** Phase P → triage record (this file) · Phase 1–2 skipped · **Phase 3** reproduction tests → RED · **Phase 4** minimal fix → GREEN · **Phase 5** **full gate set** (the light tier does **not** apply — §8) · **Phase 6** review + PR + `patch` bump (AGENTS.md Versioning: `ISSUE → patch`, `1.2.0 → 1.2.1`).
- **Date:** 2026-10-11

## Phase P record

| Step | Date | Result |
|---|---|---|
| P.1 Frame (orchestrator, `main`) | 2026-10-10 | `docs/todo/startup-settings-registration-gaps.md` + `docs/questions/startup-settings-registration-gaps.md` created on `main`; type **ISSUE**; found while the `settings-test-isolation` change was being triaged; value-triage score **4/5**, decision **implement** |
| P.2 Interrogate | 2026-10-10 | **DONE — 29 questions** (`Q-01`…`Q-29`) recorded in one `BLOCKED-USER` batch in `docs/questions/startup-settings-registration-gaps.md`, each with a `Recommended:` answer and a `### Category coverage` table; overlap checked against `docs/specs/` and every TODO in `docs/todo/` |
| P.3 Answer (orchestrator ⏸, `main`) | 2026-10-10 | **all 29 ANSWERED + incorporated**; the answers **widen** the scope (defects D-1…D-5, five in-place spec amendments, no separate Spec Amendment PR) |
| P.4 Draft triage + create branch/worktree | 2026-10-11 | **this file** — worktree + branch created, triage recorded; every defect fact re-measured in this worktree (§3), not copied from the TODO |
| P.5 Self-consistency | n/a | ISSUE — P.5 runs for FEATURE/CROSS-CUTTING only (AGENTS.md, Phase P table) |

**Why (TODO `docs/todo/startup-settings-registration-gaps.md:16-17`):** make the composition root register every feature's settings and make the settings-coverage guards actually cover all nine features, so the specified startup wiring and the specified category domain hold for every feature.

---

## 1. Type and classification rationale

**ISSUE.** Every defect below is a deviation from behaviour an **approved spec already requires**, and the fix restores that behaviour through mechanisms the specs already define — the feature-owned `register_settings(registry)` functions that already exist, the `category`/`group` rule settings-coverage REQ-018 already states, and the `backend=None` default file-management REQ-015/AC-029 already specify. No new externally observable capability is introduced. The only genuinely **new** behaviour in scope is the startup override warning (D-5), and the user decided at **Q-13(b)** to add it as a new requirement (`REQ-023` / `AC-028`) inside this change's own PR rather than as a separate FEATURE change; it is recorded as a **spec amendment + small addition**, not a reclassification, per that explicit answer (Q-24: keep ISSUE).

First matching classification criterion (ISSUE) therefore holds; FEATURE (criterion 2, "not covered by an approved spec") does not, because the wiring **is** covered.

## 2. Affected requirements and acceptance criteria

All IDs are from existing approved specs (AGENTS.md ISSUE item 11).

| Spec | ID · line | Required behaviour (as written) | Defect |
|---|---|---|---|
| `settings-coverage.md` | **REQ-002** · `:132` | the composition root registers **every** feature's settings at startup | **D-1** — only 6 of 9 features are registered |
| `settings-coverage.md` | **AC-003** · `:162` | **Given** the application starts, **When** the composition root has run, **Then** every feature's settings are registered and readable through the shared registry | **D-1/D-2** — satisfied only for the 4 keys the witness samples |
| `settings-coverage.md` | **REQ-005** · `:135` | unregistered keys fall back to the feature's hardcoded defaults | masks D-1 (features keep working on fallbacks, which is why nothing crashed) |
| `settings-coverage.md` | **REQ-001** · `:131`, **REQ-017** · `:147` | the registry holds the settings of the features **enumerated** there — logging, authentication, usermanagement, eventbus only | **D-1** — the enumeration is stale; permissions, search, filemanagement, mail, sessionmanagement are missing |
| `settings-coverage.md` | **REQ-018** · `:148`, **AC-023** · `:182` | every registered setting's `category` is its **domain** (`application` / `security`) and its `group` its feature name | **D-3** — 4 keys carry a feature name as their category |
| `settings-coverage.md` | **REQ-019** · `:149`, **AC-024** · `:183` | the inventory guard checks the inventory **of §3.5** | **D-1** — §3.5 (`:102-121`) lists 14 keys from 4 features; the guard is as stale as the wiring |
| `settings-coverage.md` | **NFR-002** · `:222`, **NFR-003** · `:223` | no secret-named key; the inventory stays backward compatible | never exercised for the 5 newer features (same stale inventory) — and widening it exposes a direct conflict with `mail.smtp_password` (**D-6**, §5.1) |
| `file-management.md` | **REQ-015** · `:376`, **AC-029** · `:423` | `backend` is a constructor argument and `None` means a `LocalDiskStorageBackend` built on the **live** `filemanagement.storage_root` (default `./data/files`) | **D-4** — the composition root injects a backend pinned to a hardcoded literal, so the specified live-read path never runs in the composed app |
| `settings-public-registry-setter.md` | **REQ-011** · `:185`, **AC-016** · `:211` | "the **six** `register_*_settings(...)` calls and the four `settings_registry=` service-construction sites" read the shared instance | **wording pinned to 6** — must become "every feature registration call site" (Q-11) |
| `user-roles-permissions.md` | **REQ-019** · `:519`; model block `:281-290` (`category="permissions"` at `:288`) | registers `permissions.system_principal` **with `category="permissions"`** | the spec **mandates** the out-of-domain value → amendment required (Q-26) |
| `session-management.md` | **REQ-019** · `:165`; model block `:129-136` (`category="sessionmanagement"` ×3) | registers the three `sessionmanagement.*` keys **with `category="sessionmanagement"`** | the spec **mandates** the out-of-domain value → amendment required (Q-26) |
| `settings.md` | **REQ-011** (persisted values override defaults) | the override is specified but silent | **D-5** — no diagnostic (Q-13) |

**Traceability state (recorded, not refreshed — decision Q-129, convention B).** The Settings Coverage Matrix (`docs/verification/traceability.md:366`) records the five rows this change re-validates as **GREEN** from the search change's S5.1 run on base `e8dd2bc`, commit `7bbc05a`: REQ-002/AC-003 → `test_main_wires_all_features` (`:374`), REQ-017/AC-022 → `test_key_prefix` (`:393`), REQ-018/AC-023 → `test_category_group` (`:394`), REQ-019/AC-024 → `test_inventory_matches` (`:395`), NFR-002 → `test_no_secret_settings` (`:417`). Those rows are a legal historical record of what that run observed; they are also the proof that the guards were GREEN while the defect was live. This change updates exactly those rows (S5.3) and adds rows for the new guards.

## 3. Defect confirmation (observed vs required) — re-measured in this worktree at `25b7e7b`

All numbers below were re-measured here (the TODO's numbers are from P.1 and are **correct for the counts**, stale for the structure-map cause — §7).

### D-1 — the composition root registers 18 of the 34 specified keys

- **Observed.** `src/main.py` imports exactly six feature registration functions (`:42` logging, `:30` authentication, `:78` usermanagement, `:34` eventbus, `:54` permissions, `:62` search — each `from backend.<feature> import register_settings as register_<feature>_settings`) and calls exactly those six (`:191-196`, under the `# --- Register every feature's settings ---` header at `:190`). `filemanagement`, `mail` and `sessionmanagement` are **not imported** for registration and **not called**.
- **Measured.** The nine `src/backend/*/feature_settings.py` modules register **34** distinct keys (no duplicates). Registered by `main`: logging 5, authentication 7, usermanagement 1, eventbus 1, permissions 1, search 3 = **18**. **Unregistered: 16** —
  - `filemanagement.*` (5): `allowed_types`, `avatar_base_url`, `avatar_max_size`, `max_file_size`, `storage_root`
  - `mail.*` (8): `from_name`, `smtp_from`, `smtp_host`, `smtp_password`, `smtp_port`, `smtp_timeout`, `smtp_tls`, `smtp_username`
  - `sessionmanagement.*` (3): `cleanup_batch_size`, `max_listed_sessions`, `max_sessions_per_user`
- **Probe (not a test).** A fresh interpreter that imports `main` and then enumerates every `feature_settings` module's keys against the live registry prints `PROBED 34 REGISTERED 18 MISSING 16`; `registry.get_definition("filemanagement.storage_root")` returns **`None`** — the key has no definition at all in the composed application. (Run with `cwd` outside the worktree: importing `main` creates `data/`, `logs/` and `settings/` in the current directory.)
- **Required.** REQ-002 / AC-003: every feature's settings are registered and readable through the shared registry after startup.
- **Deviation.** 16 keys are absent from the live registry: they are invisible in views/UI, cannot be set or reset, and every read falls through the REQ-005 hardcoded fallback (`src/backend/filemanagement/service.py:231`, `src/backend/mail/…`, `src/backend/sessionmanagement/…`). The features keep working — which is precisely why the gap stayed invisible.

### D-2 — the AC-003 witness and the contract inventory guard are themselves incomplete

- **Observed.** `tests/acceptance/settings_coverage/test_wiring.py::test_main_wires_all_features` (`:12-31`) runs `import main` in a subprocess and asserts only `result.stdout.strip().endswith("[True, True, True, True]")` (`:31`) — four keys from four features (`logging.log_level`, `authentication.session_ttl`, `usermanagement.roles`, `eventbus.max_queue_size`). It never enumerates the feature set.
- **Observed.** `tests/contract/settings_coverage/test_inventory.py` — the tier that owns the complete inventory (REQ-019/AC-024) — carries a hardcoded `INVENTORY` of **14** keys from **4** features (`:14-29`: logging 5, authentication 7, usermanagement 1, eventbus 1), and its `_registry_with_all_features` (`:42-53`) registers only those four features. So `test_key_prefix` (`:56`), `test_category_group` (`:65`), `test_inventory_matches` (`:74`) and `test_no_secret_settings` (`:84`) have never seen mail, filemanagement, sessionmanagement, permissions or search. `docs/specs/settings-coverage.md` §3.5 (`:102-121`) carries the **same 14 rows**, so the spec and the guard are stale in the same way.
- **Deviation.** AC-003 and AC-022/AC-023/AC-024 are satisfied **vacuously**: the guards cannot fail for a feature they do not know about. This is why D-1 and D-3 were GREEN at `7bbc05a`.

### D-3 — four registered settings carry a feature name as their category

- **Measured.** Across the nine `feature_settings.py` modules the `category=` values are: `application` 22, `security` 8, **`sessionmanagement` 3**, **`permissions` 1**. The four out-of-domain literals are `src/backend/sessionmanagement/feature_settings.py:41`, `:48`, `:55` and `src/backend/permissions/feature_settings.py:31`.
- **Required.** REQ-018 / AC-023: `category` is the **domain** (`application` / `security`), `group` is the feature name.
- **Measured again at S3.1 — D-3 has a `group` half too.** The three `sessionmanagement.*` definitions carry **no `group` at all** (`group=None`); `register_feature` (`src/backend/settings/registry.py:135-149`) only validates the key prefix and never sets `group`. `permissions.system_principal` does carry `group="permissions"`. So the widened AC-023 guard is RED on the category of all four keys **and** on the missing `group` of three (§5.2).
- **Deviation.** Four keys violate it, and the guard that would catch it never registers those features (D-2). **The approved specs mandate the wrong values**: `docs/specs/user-roles-permissions.md:288` and `docs/specs/session-management.md:132,134,136` show the out-of-domain categories in their normative model blocks — hence the amendments at Q-26 (§4).
- **Consequence for tests.** `tests/acceptance/sessionmanagement/test_settings.py::test_ac_039_register_settings_defaults:58` asserts `definition.category == "sessionmanagement"`. That assertion over-specifies what AC-039 (`session-management.md:215`) actually requires (defaults 100/5/1000, `min_value` 1 — no category), so it must be re-derived from the amended model block. This is a **spec-amendment-driven test update**, not a weakening: the assertion is narrowed to what the AC states, and the category itself becomes covered by the widened AC-023 guard.

### D-4 — the composed `FileService` pins the storage root to a literal

- **Observed.** `src/main.py:213-218` constructs `FileService(_file_repository, LocalDiskStorageBackend("./data/files"), settings_registry=_shared_settings_registry(), permission_service=_permission_service)`; `LocalDiskStorageBackend` is imported at `:37`. The injected backend makes `FileService._backend_for` (`src/backend/filemanagement/service.py:222-232`) return the injected instance and **never** read `filemanagement.storage_root`.
- **Measured.** The hardcoded literal `"./data/files"` is byte-identical to `DEFAULT_STORAGE_ROOT` (`src/backend/filemanagement/feature_settings.py:24`), which is also the registered default of `filemanagement.storage_root` (`:52-58`).
- **Required.** REQ-015 / AC-029: `backend=None` means a `LocalDiskStorageBackend` built from the **live** `filemanagement.storage_root` on each operation.
- **Deviation.** The composed application is the one place the specified live-read path does **not** run: changing `filemanagement.storage_root` in the registry has no effect there, and the key is not even registered (D-1). Dropping the argument **matches** the spec — no spec change is needed for this item.

### D-5 — a persisted value silently overrides a new default

- **Observed.** `SettingsRegistry.__init__` loads persisted values once (`src/backend/settings/registry.py:104`) and `register()` applies them over the definition default (`:121`) with no diagnostic; `_persist_values()` (`:127`) then rewrites the file.
- **Required.** `settings.md` REQ-011 specifies the precedence but no observability; settings-coverage has no requirement for it.
- **Deviation / gap.** A stale `settings/values.yaml` silently changes behaviour with no trace. The user decided at **Q-13(b)** to close this inside this change: one `WARNING` per key when a persisted value overrides the default, as a **new** requirement `REQ-023` / `AC-028` in `settings-coverage.md` (current max IDs there: REQ-022, AC-027, EDGE-012, INV-005, NFR-006).

### D-6 — the NFR-002 guard conflicts with a registered mail credential key

Measured: `mail.smtp_password` (`src/backend/mail/feature_settings.py:101`) is the only one of the 34 keys whose name trips the NFR-002 guard's `"password" not in key.lower()` check (`tests/contract/settings_coverage/test_inventory.py:84-95`). **Required:** NFR-002 (`:222`) forbids password/token settings; **observed:** the approved mail spec registers exactly that key. The conflict is invisible today only because the guard covers 14 keys from 4 features (D-2). Resolution and options: §5.1 (LQ-01).

## 4. Spec amendments — all in this change's own PR (Q-02, Q-11, Q-13, Q-26, Q-27)

**No separate Spec Amendment PR is opened** (explicit user answers at Q-02 and Q-27). The **six** approved specs are amended **in place, in this PR**, as wording fixes so the spec matches the fixed behaviour; each amended file gets a `## Changelog` line at its top (all six already have that section at line 3). The sixth — `structlog-logging.md` — is not one of the five the P.3 answers anticipated; it is added at **S4.3** because the D-5 fix moves a count that spec states (last row below, §6.1.1). AGENTS.md's Spec Amendment Workflow is deliberately overridden by the user for this change; the override and its reason are recorded here.

| Spec | Amendment |
|---|---|
| `settings-coverage.md` | REQ-001 (`:131`) / REQ-017 (`:147`) feature enumeration → all nine features; §3.5 inventory table (`:102-121`) → the full **34-key** inventory; REQ-019 (`:149`) → the guard checks the complete inventory; **new REQ-023 + AC-028** for the override `WARNING`; §10 test-strategy rows (`:273-275`, `:297-298`) and §11 matrix rows (`:311`, `:330-332`, `:342`) updated to the new guard functions |
| `settings-public-registry-setter.md` | REQ-011 (`:185`) and AC-016 (`:211`): "the **six** `register_*_settings(...)` calls" → "every feature `register_settings` call site in the composition root" (Q-13(b), Q-14). The same rows pinned `src/main.py` line numbers that had already drifted (`:137-138` install, `:173-178` the six calls, `:161`/`:198`/`:204`/`:214` service sites; measured in this worktree at S4.1: install `:156`, calls `:191-196`, sites `:179`/`:216`/`:222`/`:232`). **The amendment removes the count and the line references instead of refreshing them** — Q-13(b) decided "no hard-coded count and no line-number references", and the Q-14 loop moves those positions again in this very change |
| `user-roles-permissions.md` | model block `:288`: `category="permissions"` → `category="security"` (Q-26) |
| `session-management.md` | model block `:132,134,136`: `category="sessionmanagement"` → `category="security"` (Q-26) **and `group="sessionmanagement"` added** — the block states no `group`, and REQ-018 requires `group` = feature name (§5.2) |
| `settings-coverage.md` — **NFR-002** | NFR-002 (`:222`) amended to the Q-27 wording decided at **LQ-01 (a)**: no credential or token may appear in log records or events, and a setting explicitly declared as a credential **may** be persisted; `mail.smtp_password` is named as the accepted transport-credential exception (decision recorded on `main` at `093f2ff`) |
| `file-management.md` | **REQ-015 + AC-029 wording amended** (Q-24, Q-26): they now state that the composition root passes **no** `StorageBackend`, so its file storage root is the live `filemanagement.storage_root` setting and never a hard-coded path. (The P.4 row said "no wording change" — that held only for the category/group fix; Q-24/Q-26 decided the wiring wording here.) |
| `structlog-logging.md` | **AC-009 wording amended at S4.3**: the criterion no longer hardcodes "each of the 42 one-off statements" — it now states the invariant (every one-off statement the AC-009 witness counts in the four named files is written through `get_logger()`) and keeps the count as the witness's **measured** figure (43 today: 19 + 11 + 11 + 2), so a requirement of another spec that adds a statement moves the figure without amending this one. REQ-005's per-file count for `registry.py` is refreshed **18 → 19** to match the measured state. Changelog **v3**; no ID changed, the migration requirement itself is unchanged. |

## 5. Reproduction plan (Phase 3)

Two guards, both **in place** (Q-14: strengthen the existing tests rather than add a parallel suite). No new test file is needed.

**R-1 — strengthen the AC-003 witness in place.** `tests/acceptance/settings_coverage/test_wiring.py::test_main_wires_all_features` (`:12-31`). The subprocess already imports `main`; it must instead enumerate the feature set **itself** and report every key each `feature_settings` module registers, then assert that the live registry has **all** of them — i.e. `PROBED 34 / REGISTERED 34 / MISSING []` — and keep the existing four-key positive check. The feature list must be derived (import the nine `backend.<feature>.feature_settings` modules), not hardcoded, so a tenth feature cannot hide (Q-16).

**R-2 — widen the contract-tier inventory guard.** `tests/contract/settings_coverage/test_inventory.py`: `INVENTORY` (`:14-29`) → the full 34-key inventory (mirroring the amended §3.5), and `_registry_with_all_features` (`:42-53`) → register all nine features. This makes the existing `test_key_prefix` (AC-022), `test_category_group` (AC-023), `test_inventory_matches` (AC-024), `test_no_secret_settings` (NFR-002) and `test_inventory_backward_compatible` (NFR-003) cover every feature. Note that this guard builds its **own** registry (it never imports `main`), so it pins the inventory and the category rule, not the composition-root wiring — D-1 is reproduced by R-1 alone.

**Expected RED (all failures are assertion failures on behaviour, not collection/import/`ValidationError` — valid RED):**

| Test | Why it is RED on the current code |
|---|---|
| `test_main_wires_all_features` (R-1) | `MISSING` lists the 16 keys the composition root never registers (D-1) — the **only** guard that imports `main`, so the only direct D-1 reproduction |
| `test_category_group` (R-2) | 4 rows carry `sessionmanagement` / `permissions` as their category, and the 3 `sessionmanagement.*` rows carry no `group` at all (D-3, §5.2) — the direct D-3 reproduction |
| `test_ac_028_persisted_override_warns` (D-5, `tests/acceptance/settings_coverage/test_persistence.py`) | no `WARNING` record names a key whose persisted value overrode its definition default — the direct D-5 reproduction |
| `test_no_secret_settings` (R-2) | **GREEN by design, not RED** — LQ-01 (a) resolves D-6 with a **spec wording** amendment, not a code change, so the widened guard already encodes the amended NFR-002: the set of credential-named inventory keys must equal the documented exemption list (`mail.smtp_password`), which keeps the name check's full force on the other 33 keys and makes any undocumented credential-named key a failure. The conflict this row predicted is recorded as resolved in §5.1 |
| `test_key_prefix`, `test_inventory_matches`, `test_inventory_backward_compatible` (R-2) | expected to stay **GREEN** once both the inventory and the nine-feature helper are widened (each feature does register its own keys with the right kind/default) — they are widened for coverage, and they go RED if any feature ever stops registering an inventory key |
| `tests/acceptance/filemanagement/test_filemanagement.py::test_ac_029_default_local_backend` | already GREEN at the service level; it is the **contract** the D-4 fix must satisfy, so it is in the GREEN command, not the RED set |

### 5.1 Open finding LQ-01 — NFR-002 conflicts with `mail.smtp_password`

Measured: of the 34 keys, exactly one trips the NFR-002 guard's name check (`test_inventory.py:84-95` asserts `"password" not in key.lower()`): **`mail.smtp_password`** (`src/backend/mail/feature_settings.py:101`). Widening the inventory therefore makes `test_no_secret_settings` fail, and it cannot be fixed by the code — the mail spec registers that key by design (`docs/specs/mail-service.md`; AGENTS.md: `mail.smtp_password` is sensitive and never logged), while `docs/specs/settings-coverage.md` NFR-002 (`:222`) states "Settings values are not secrets; no credential storage. Settings do not contain passwords or tokens."

This is a conflict between two approved specs, surfaced only because the guard never covered mail (D-2). It is **not** resolved by any of the 29 P.3 answers, and the two resolutions differ in what the change does:

- **(a) amend NFR-002** to scope it to the settings feature's own domain (no credential storage for feature *auth* secrets) while naming `mail.smtp_password` as an explicitly accepted, transport-credential exception, and keep the guard with a documented exemption list; or
- **(b) keep NFR-002 absolute** and remove `mail.smtp_password` from the settings registry (the SMTP password moves out of settings, e.g. to an environment variable) — a materially larger change that contradicts the mail spec's registered-settings list and AGENTS.md's mail section.

**Recommended: (a)** — the mail spec and AGENTS.md both treat `mail.smtp_password` as a registered setting, so NFR-002's absolute wording is the stale side; the guard keeps its force for every other key. Recorded here as a **late question (LQ-01)** for the orchestrator to append to `docs/questions/startup-settings-registration-gaps.md` under `## Late questions (Phases 2–6)`; S3.1 must not widen the NFR-002 guard until the answer is recorded.

**ANSWERED — (a)** (recorded by the orchestrator on `main` at `093f2ff`, 2026-10-11). `settings-coverage.md` NFR-002 is amended **in this change's own PR** (no separate Spec Amendment PR) with the Q-27 wording: no credential or token may appear in log records or events, and a setting explicitly declared as a credential **may** be persisted — with `mail.smtp_password` named as the accepted transport-credential exception.

**Effect on the guard (applied at S3.1).** `test_no_secret_settings` now asserts that the set of inventory keys whose name contains `password` / `secret` / `credential` **equals** an explicit exemption list, `NFR_002_CREDENTIAL_EXEMPTIONS = {"mail.smtp_password"}`, in `tests/contract/settings_coverage/test_inventory.py`. The guard therefore keeps its full force on the other 33 keys (an undocumented credential-named key, or a stale exemption, fails the set equality with a message naming the offender), and it leaves the expected-RED set — its resolution is the §4 NFR-002 wording amendment, not a code change. `mail.smtp_password` stays registered and persisted; mail's existing secret handling (`@logged_class(include_args=False)`, secret-free events) is what the amended NFR-002 requires of it (Q-11).

**Commands (targeted — AGENTS.md "Targeted GREEN"; the full suite is a Phase 5 gate):**

- `red_command`: `uv run pytest tests/acceptance/settings_coverage/test_wiring.py tests/contract/settings_coverage/test_inventory.py -v`
- `green_command`: `uv run pytest tests/acceptance/settings_coverage/test_wiring.py tests/contract/settings_coverage/test_inventory.py tests/acceptance/filemanagement/test_filemanagement.py::test_ac_029_default_local_backend tests/integration/singleton_install/test_composition_root.py tests/acceptance/sessionmanagement/test_settings.py -v`

**Test-data validity check (AGENTS.md Phase 3 item 6):** every widened row is a real key with the real kind/default/category taken from the module that registers it, so no fixture constructs an invalid `SettingDefinition`; the RED is behaviour, not invalid data.

**In Phase 3 (S3.1):** the D-5 override `WARNING` test — it asserts behaviour no spec stated before this change, so it is derived from the **amended** REQ-023/AC-028 in the same Phase 3 pass (one new test function in `tests/contract/settings_coverage/` or `tests/acceptance/settings_coverage/`, decided by S3.1), and it is RED until the `WARNING` exists.

### 5.2 S3.1 findings (recorded with the reproduction tests)

- **D-3 also covers `group`.** Measured: `permissions.system_principal` registers `group="permissions"`, but the three `sessionmanagement.*` definitions register **`group=None`** — `register_feature` (`src/backend/settings/registry.py:135-149`) validates the key prefix only and never sets `group`. REQ-018 / AC-023 require `group` = feature name, so the widened `test_category_group` asserts `group == "sessionmanagement"` and Phase 4 MUST add `group="sessionmanagement"` to the three definitions and to the `session-management.md` model block (§4). Not a new defect class — the second half of the requirement D-3 already cites, invisible until the guard covered the feature.
- **The NFR-002 guard's value clause no longer demands a non-empty string.** The old assertion (`assert value and "://" not in value[:4]`) fails on `mail.smtp_username` and `mail.smtp_password`, whose approved defaults are the empty string (`src/backend/mail/feature_settings.py:95,101`): an empty value is the absence of a value, not a secret, and NFR-002 says nothing about non-emptiness. The guard now applies the connection-string clause only to non-empty strings; the **name** check is unchanged and is now enforced as a set equality against the documented exemption list. Recorded so the Phase 6 review can see a spec-traced correction, not a weakening.
- **D-5 witness tier.** `test_ac_028_persisted_override_warns` went into `tests/acceptance/settings_coverage/test_persistence.py` (acceptance, beside `test_persisted_precedence`) because AC-028 is a user-observable startup diagnostic, not an internal contract — and that file already owns the persisted-precedence behaviour it complements.
- **Witness hygiene (Q-22).** `tests/acceptance/settings_coverage/test_wiring.py` now runs its child with `cwd=tmp_path` and an absolute `src` entry on `sys.path` (the `tests/acceptance/permissions/test_composition_wiring.py` pattern), plus an autouse fixture that removes a repository-root `settings/` directory **only if that run created it** — a developer's own `settings/` is left alone. Within the §10 boundary: the fixture is scoped to the witness file, not to the suite.

### 5.3 S3.2 RED gate — **CONFIRMED** (2026-10-11)

Targeted commands, run in this worktree (the whole-repo ruff sweep and the full suite are **Phase 5** gates and are not run here):

```text
uv run ruff check tests/acceptance/settings_coverage/test_wiring.py tests/contract/settings_coverage/test_inventory.py tests/acceptance/settings_coverage/test_persistence.py
uv run ruff format --check tests/acceptance/settings_coverage/test_wiring.py tests/contract/settings_coverage/test_inventory.py tests/acceptance/settings_coverage/test_persistence.py
uv run pytest tests/acceptance/settings_coverage/test_wiring.py tests/contract/settings_coverage/test_inventory.py tests/acceptance/settings_coverage/test_persistence.py -q
uv run pytest tests/acceptance/settings_coverage tests/contract/settings_coverage --collect-only -q
```

**Measured.** ruff: `All checks passed!`; format: `3 files already formatted`. Targeted run: **3 failed, 6 passed in 2.34s** — identical to the orchestrator's independent re-run at S3.1 (3 failed, 6 passed in 2.62s, same three failures). Collection sanity check: **17 tests collected in 0.44s, 0 errors** (the 8 collected but not run are the untouched `test_registration.py`, `test_live_reads.py` and `test_value_repository.py` witnesses).

**Effective `red_command`** is the three-file pytest command above — the two-file `red_command` in §5 predates the D-5 witness; §12 already records the three-file form. `green_command` (§5) is unchanged.

**Per-test RED state as observed, with the failure mode** (test contract sanity check, skill `test`):

| Test | State | Observed failure mode / reason |
|---|---|---|
| `test_main_wires_all_features` | **RED** | `AssertionError` at `tests/acceptance/settings_coverage/test_wiring.py:108` — “the composition root never registers these settings: […16 keys…]” (D-1) |
| `test_category_group` | **RED** | `AssertionError` at `tests/contract/settings_coverage/test_inventory.py:166` — “permissions.system_principal: category 'permissions' != 'security'”; the three `sessionmanagement.*` rows fail the same guard on category **and** on `group=None` (D-3, §5.2) |
| `test_ac_028_persisted_override_warns` | **RED** | `AssertionError` at `tests/acceptance/settings_coverage/test_persistence.py:70` — “no WARNING named the persisted override of app.name”, with the full captured record list (D-5) |
| `test_no_secret_settings` | GREEN **by design** | LQ-01 (a): the widened guard already encodes the amended NFR-002 with the single named exemption `mail.smtp_password` (§5.1) — the absent 4th RED is not a gap |
| `test_key_prefix` / `test_inventory_matches` / `test_inventory_backward_compatible` | GREEN | widened to the nine features and the 34-key inventory; they go RED if any feature stops registering an inventory key |
| `test_set_value_persists` / `test_persisted_precedence` | GREEN | pre-existing persistence witnesses, untouched by this change |

**Test contract sanity check — PASS.** Every red test fails with an `AssertionError` raised by its own assertion on behaviour; the run contains **no** collection, import, fixture or `ValidationError` failure, and the `--collect-only` pass confirms 17 collected with 0 errors. Every widened row is a real key with the real kind/default/category of the module that registers it (§5, test-data validity), so the RED is behaviour, not invalid data; no Hypothesis strategy and no colliding fixture is involved.

**`make_map.py --check` — measured STALE, deliberately not regenerated here.** The fresh render differs from the committed `STRUCTURE.md` in exactly one line: `docs/ — 234 files (process record)` → `235`. The extra file is this change's own triage record, added at P.4 (`cce7439`) without a map regeneration; no `.py` path changed at S3.1/S3.2, so the AGENTS.md trigger (regenerate in the same commit as the `.py` change) does not fire in this step. §6 already schedules the regeneration for the Phase 4 `src/main.py` commit, which also settles the `test_ac_021` byte-compare artifact of §7 in this worktree.

**Gate: Phase 3 PASSES.** RED is observed on all three reproduction witnesses, the expected-RED table in §5 (as corrected by LQ-01 and §5.2) matches the measurement exactly, and the traceability matrix carries the issue's evidence rows for the already-defined IDs. **State machine: `TESTS_WRITTEN → RED_CONFIRMED`.** Phase 4 (S4.1, minimal fix) may start; D-4 has no RED witness by design — it is verified by the already-GREEN `test_ac_029_default_local_backend` contract in the `green_command`.

## 6. Fix scope (Phase 4)

| File | Change |
|---|---|
| `src/main.py` | **D-1:** register all nine features' settings at the composition root — keep the six existing imports and add the three missing ones, then call every registration against the shared instance (Q-09). **D-4:** drop `LocalDiskStorageBackend("./data/files")` from the `FileService(...)` call (`:213-218`) and the now-unused `LocalDiskStorageBackend` import (`:37`) so REQ-015's live-read default path runs (Q-12). **D-3:** none here |
| `src/backend/sessionmanagement/feature_settings.py` | **D-3:** `category="sessionmanagement"` → `category="security"` at `:41`, `:48`, `:55` (Q-06) **and `group="sessionmanagement"` added to the three definitions** (§5.2) |
| `src/backend/permissions/feature_settings.py` | **D-3:** `category="permissions"` → `category="security"` at `:31` (Q-06) |
| `src/backend/settings/registry.py` | **D-5:** one `WARNING` per key in `register()` where `self._persisted` overrides the definition default (`:121`) — the record names the **key only** and never the persisted value (Q-28; the amended NFR-002 forbids a credential's value in a log record, and `mail.smtp_password` is persisted), nothing else |
| `docs/specs/settings-coverage.md` | §4 amendments + new REQ-023/AC-028 + §3.5 full inventory + Changelog **+ the NFR-002 resolution per LQ-01** |
| `docs/specs/settings-public-registry-setter.md` | REQ-011/AC-016 wording (six → every call site) + Changelog |
| `docs/specs/user-roles-permissions.md` | model block category + Changelog |
| `docs/specs/session-management.md` | model block category + Changelog |
| `docs/specs/file-management.md` | REQ-015/AC-029 wiring wording + Changelog (Q-24, Q-26) |
| `docs/specs/structlog-logging.md` | **S4.3:** AC-009 wording (measured count, not a fixed 42) + REQ-005 per-file count 18 → 19 + Changelog v3 (§4, §6.1.1) |
| `STRUCTURE.md` | regenerated with the `src/main.py` edit in the **same commit** (AGENTS.md; skill `code-structure-map`) |
| `CHANGELOG.md` | one entry under `## [Unreleased]` → `Fixed` (and `Changed` for the category fix), moved to `## [1.2.1]` in the bump commit |
| `pyproject.toml` | `patch` bump `1.2.0 → 1.2.1` at S6.4 |
| `docs/verification/traceability.md` | update the five Settings Coverage rows + add rows for the new guards (S5.3) |

**Test files this change touches (Phase 3/4):** `tests/acceptance/settings_coverage/test_wiring.py` and `tests/contract/settings_coverage/test_inventory.py` (widened in place at S3.1), `tests/acceptance/settings_coverage/test_persistence.py` (the new `test_ac_028_persisted_override_warns`, S3.1), `tests/acceptance/sessionmanagement/test_settings.py:58` (the category assertion re-derived from the amended `session-management.md` model block — §3 D-3), and `tests/acceptance/logging_coverage/test_statements_via_feature.py`: its pinned `_AC_009_STATEMENTS` list for `src/backend/settings/registry.py` holds **18** entries today and must become **19**, because the D-5 `WARNING` is one more one-off statement in that module — measured at S3.1, so the D-5 fix fails `test_ac_009_settings_statements_go_through_get_logger` unless the list is updated in the same commit.

**S4.1 (2026-10-11) — the §4 spec amendments have landed in this branch.** Five specs amended in place (`settings-coverage.md` → v3, `settings-public-registry-setter.md` → v4, `user-roles-permissions.md` → v3, `session-management.md` → v3, `file-management.md` → v3) plus the REQ-023 / AC-028 rows in `docs/verification/traceability.md`; no `src/` or `tests/` file was touched. **RED is unchanged** from §5.3: `uv run pytest tests/acceptance/settings_coverage/test_wiring.py tests/contract/settings_coverage/test_inventory.py tests/acceptance/settings_coverage/test_persistence.py -q` → **3 failed, 6 passed** (`test_main_wires_all_features`, `test_category_group`, `test_ac_028_persisted_override_warns`). Docs gates: `scripts/check_traceability.py` **PASS** (891 matrix rows, 136 spec IDs, 876 test functions); `scripts/verify_spec.py` exit 0 for each of the five amended specs; `scripts/make_map.py --check` still **fails by exactly one line** (`docs/ — 234 files` → `235`, the drift the P.4 triage commit `cce7439` introduced) — not regenerated here on purpose, it lands with the `src/main.py` commit at S4.2.

### 6.1 S4.2 (2026-10-11) — **GREEN confirmed**

The minimal fix for **D-1, D-3, D-4, D-5** is implemented in four `src/` files; no behaviour beyond the affected spec IDs was introduced (the override `WARNING` is REQ-023 / AC-028, amended at `ffcd125`).

**Changed in this commit:**

| File | What changed |
|---|---|
| `src/main.py` | **D-1** — the six named `register_*_settings(...)` one-liners are replaced by `_SETTINGS_REGISTRATIONS`, an ordered tuple of the **nine** features' `register_settings` callables, plus the loop that calls each against `_shared_settings_registry()` (Q-14). Every callable is still imported from its feature's **package root** (`from backend.<feature> import register_settings as …`), so the REQ-011 witness keeps spying the call sites, and the install still precedes the registrations. **D-4** — the `LocalDiskStorageBackend("./data/files")` argument and its now-unused import are dropped from the `FileService(...)` construction, so REQ-015's live read of `filemanagement.storage_root` runs. |
| `src/backend/permissions/feature_settings.py` | **D-3** — `permissions.system_principal`: `category="permissions"` → `category="security"` (key, kind, default, `group` unchanged). |
| `src/backend/sessionmanagement/feature_settings.py` | **D-3** — the three `sessionmanagement.*` definitions: `category="sessionmanagement"` → `category="security"` **and `group="sessionmanagement"` added** (`register_feature` never sets `group`, §5.2). Keys, kinds, defaults and `min_value` unchanged. |
| `src/backend/settings/registry.py` | **D-5 / REQ-023** — `register()` emits **one `WARNING`** when the loaded persisted value differs from the definition default. The record names the **key only** (message text + `key=` field), never the persisted value and never the default (Q-28 + the amended NFR-002: `mail.smtp_password` is a persisted credential). A persisted value equal to the default emits nothing; the REQ-011/REQ-022 precedence itself is unchanged. |
| `tests/acceptance/sessionmanagement/test_settings.py` | Re-derived from the **amended** `session-management.md` model block (v3): `category == "security"` **and** `group == "sessionmanagement"` (was `category == "sessionmanagement"`). A narrowing to what AC-039 + settings-coverage REQ-018 state — not a weakening (§3 D-3, §9). |
| `tests/acceptance/logging_coverage/test_statements_via_feature.py` | Re-counted for the new `registry.py` statement: `_AC_009_STATEMENTS["src/backend/settings/registry.py"]` **18 → 19**, and with it `_AC_009_TOTAL_STATEMENTS` **42 → 43** (the table guard `sum(...) == total` fails if only the per-file count moves), plus the two per-file counts in the docstring/comment. **Finding for Phase 6:** `docs/specs/structlog-logging.md` AC-009 still states "each of the 42 one-off statements" — REQ-023 adds the 43rd statement, and `structlog-logging.md` is **not** one of the five specs this change amends (§4). The count is a spec-wording drift, not a weakened assertion: the guard mechanism is byte-for-byte unchanged and now checks 19 + 11 + 11 + 2 = 43. **RESOLVED at S4.3** — `structlog-logging.md` AC-009/REQ-005 amended (v3, §4, §6.1.1). |
| `STRUCTURE.md` | Regenerated with `uv run python scripts/make_map.py` **in the same commit** as the `src/main.py` edit (AGENTS.md; skill `code-structure-map`): the `docs/ 234 → 235` drift §5.3 recorded, plus the line counts of the four changed modules. |

**GREEN evidence** (targeted — AGENTS.md "Targeted GREEN"; the full suite and the whole-repo ruff sweep are **Phase 5** gates and were not run here):

```text
uv run pytest tests/acceptance/settings_coverage/test_wiring.py tests/contract/settings_coverage/test_inventory.py \
     tests/acceptance/settings_coverage/test_persistence.py \
     tests/acceptance/filemanagement/test_filemanagement.py::test_ac_029_default_local_backend \
     tests/integration/singleton_install/test_composition_root.py \
     tests/acceptance/sessionmanagement/test_settings.py -v
    → 14 passed in 5.84s        (the same tests were 3 failed / 6 passed at S3.2 / S4.1)

uv run pytest tests/acceptance/settings_coverage tests/contract/settings_coverage tests/acceptance/mail \
     tests/acceptance/filemanagement tests/integration/singleton_install -q
    → 95 passed, 1 skipped in 17.10s   (the skip is the inherited symlink-host skip of §7)

uv run pytest tests/acceptance/logging_coverage tests/acceptance/sessionmanagement tests/contract/singleton_install -q
    → 82 passed in 17.12s

uv run pytest tests/acceptance/test_structure_map.py tests/acceptance/settings tests/contract/settings \
     tests/unit/settings tests/acceptance/permissions -q
    → 151 passed in 48.55s      (test_ac_021 passes in this worktree now the map is regenerated, §7)

uv run ruff check src/main.py src/backend/sessionmanagement/feature_settings.py \
     src/backend/permissions/feature_settings.py src/backend/settings/registry.py \
     tests/acceptance/sessionmanagement/test_settings.py \
     tests/acceptance/logging_coverage/test_statements_via_feature.py
    → All checks passed!
uv run ruff format --check <same six paths>          → 6 files already formatted
uv run mypy src/                                    → Success: no issues found in 84 source files
uv run python scripts/check_traceability.py         → PASS (891 matrix rows, 136 spec IDs, 876 test functions)
uv run python scripts/make_map.py --check           → exit 0
```

**Per defect — the test that now proves it:**

| Defect | Proving test (GREEN) |
|---|---|
| **D-1** | `tests/acceptance/settings_coverage/test_wiring.py::test_main_wires_all_features` — the child reports `PROBED 34 / REGISTERED 34 / MISSING []` (the only witness that imports `main`) |
| **D-2** | the same witness (its expected set is derived from every `feature_settings` module, so a tenth feature cannot hide) plus `tests/contract/settings_coverage/test_inventory.py::test_key_prefix` / `::test_category_group` / `::test_inventory_matches` / `::test_no_secret_settings` / `::test_inventory_backward_compatible` — nine features registered, the 34-key inventory |
| **D-3** | `test_inventory.py::test_category_group` (category = domain **and** group = feature name for all 34 rows) and `tests/acceptance/sessionmanagement/test_settings.py::test_ac_039_register_settings_defaults` |
| **D-4** | `tests/acceptance/filemanagement/test_filemanagement.py::test_ac_029_default_local_backend` — the AC-029 contract the fix must satisfy, now reached by the composed service too (no `StorageBackend` argument); `tests/integration/singleton_install/test_composition_root.py` shows the composition root still wires |
| **D-5** | `tests/acceptance/settings_coverage/test_persistence.py::test_ac_028_persisted_override_warns` — one `WARNING` names the overridden key, the effective value is still the persisted one, and a persisted value equal to the default names nothing |
| REQ-011 / AC-016 (regression guard on the loop) | `tests/integration/singleton_install/test_composition_root.py::test_ac_016_main_installs_through_setter` and `::test_installed_registry_serves_feature_registration` — both still `[True, …, True]` with the loop: the six spied modules are still spied through their package roots, the install still precedes the registrations, and the source scan still finds no consumer site passed the local `_settings_registry` handle |

**State machine: `RED_CONFIRMED → GREEN`.** Next atomic step: S4.3 (refactor, keep GREEN).

### 6.1.1 S4.3 (2026-10-11) — refactor (GREEN kept) + the AC-009 finding resolved

**(a) Refactor — one change, everything else reviewed and left alone.**

| File | Decision |
|---|---|
| `src/backend/settings/registry.py` | **Refactored.** The REQ-023 `WARNING` call is collapsed from four lines to one (119 chars, inside the 120 limit) so it matches its sibling in the same method (`_logger.warning(f"duplicate registration: key=…", key=…)`), and its why-comment is tightened from 5 lines to 3 with the content unchanged (key-only record, the credential reason, the amended NFR-002). Net **−5 lines**; the statement count the AC-009 witness counts is unchanged (still 19 in this module). |
| `src/main.py` | **No change — already minimal.** The `_SETTINGS_REGISTRATIONS` tuple + loop is the data-driven shape Q-14 decided and the amended `settings-public-registry-setter` REQ-011 wording ("no hard-coded count") depends on; the comment states *why* (the six named one-liners left filemanagement, mail and sessionmanagement unregistered) and the two §9 constraints a later edit must not break (package-root imports, getter-not-handle, install-before-register). The loop variable is deliberately named `register_settings`: `test_composition_root.py::_consumer_sites_passing_the_handle()` classifies a call as a REQ-011 consumer site by the name pattern `register_*_settings`, so renaming it (e.g. `register`) would silently drop all nine registration call sites from that witness. The `tuple[Callable[[SettingsRegistry], None], ...]` annotation is kept — it is the single place pinning all nine callables to one signature. |
| `src/main.py` imports | **No change.** The split `from backend.<feature> import (…)` / `from backend.<feature> import (register_settings as …)` pairs are ruff isort's `combine-as-imports = false` output (the pattern the file already used for authentication, search and usermanagement), not duplication — merging them would be undone by the linter. |
| `src/backend/permissions/feature_settings.py`, `src/backend/sessionmanagement/feature_settings.py` | **No change.** The three repeated `category="security", group="sessionmanagement"` pairs are the explicit per-definition values settings-coverage REQ-018 states. Deriving `group` from the feature name inside `register_feature` would change behaviour for every feature — unspecified, and out of scope for this ISSUE (§10). |
| — | No new abstraction, helper, module or dependency (AGENTS.md "Ponytail": boring over clever, no abstraction that was not requested). |

**(b) AC-009 count drift — resolved (the sixth spec amended in this PR, §4).** `docs/specs/structlog-logging.md` **AC-009** no longer states "each of the **42** one-off statements": the criterion now names the invariant (every one-off statement the AC-009 witness counts in the four named files is written through `get_logger()`) and keeps the count as the witness's **measured** figure — 43 today, 19 + 11 + 11 + 2 — so a requirement of another spec that adds a one-off statement (settings-coverage REQ-023 did exactly that) moves the figure without amending this spec and without weakening the guard. **REQ-005**'s per-file count for `src/backend/settings/registry.py` is refreshed **18 → 19** in the same amendment, so the spec no longer contradicts its own witness. Changelog **v3 (2026-10-11)**; no ID changed, the migration requirement itself is unchanged. `tests/acceptance/logging_coverage/test_statements_via_feature.py` gets **comment-only** updates (the two comments that recorded the drift now record the amended wording); the guard mechanism — the `_AC_009_STATEMENTS` per-file table and the `sum(...) == _AC_009_TOTAL_STATEMENTS` guard — is byte-for-byte unchanged.

**Gates (targeted — the full suite and the whole-repo ruff sweep stay Phase 5 gates).**

```text
uv run pytest tests/acceptance/settings_coverage/test_wiring.py tests/contract/settings_coverage/test_inventory.py \
     tests/acceptance/settings_coverage/test_persistence.py \
     tests/acceptance/filemanagement/test_filemanagement.py::test_ac_029_default_local_backend \
     tests/integration/singleton_install/test_composition_root.py \
     tests/acceptance/sessionmanagement/test_settings.py -v
    → 14 passed in 5.12s        (identical to the S4.2 / orchestrator re-run: 14 passed)

uv run pytest tests/acceptance/logging_coverage tests/acceptance/settings_coverage tests/contract/settings_coverage -q
    → 38 passed in 4.68s

uv run ruff check src/backend/settings/registry.py tests/acceptance/logging_coverage/test_statements_via_feature.py
    → All checks passed!        uv run ruff format <same two paths> → 2 files left unchanged
uv run mypy src/                                    → Success: no issues found in 84 source files
uv run python scripts/make_map.py                   → STRUCTURE.md regenerated in the same commit as the .py edit
                                                       (src/backend/settings/registry.py 478 → 473 lines)
uv run python scripts/make_map.py --check           → exit 0
uv run python scripts/verify_spec.py docs/specs/structlog-logging.md → Traceability: PASS, exit 0
uv run python scripts/check_traceability.py         → PASS (891 matrix rows, 136 spec IDs, 876 test functions), exit 0
```

**State machine: `GREEN` unchanged** (no observable behaviour change in (a); (b) is spec wording). Next atomic step: S4.4 (commit + status).

### 6.2 S4.4 (2026-10-11) — Phase 4 complete (commit + status)

**Phase 4 commits on `issue/startup-settings-registration-gaps`** (`git log --oneline main..HEAD`, oldest first; Phase 3 commits listed for context, they are not part of Phase 4):

| Commit | Step | Content |
|---|---|---|
| `cce7439` | (Phase P) | triage record |
| `79d92cf`, `dbbe2ea` | (orchestrator) | Problem Log entries P-109…P-117 (`docs/workflow/PROBLEMS.md`) — no source or test content |
| `46d679a` | S3.1 | reproduction tests |
| `7e2508d` | S3.1 | LQ-01 answer + S3.1 findings |
| `1c0dfe5` | S3.2 | RED gate + traceability rows |
| `ffcd125` | S4.1 | five spec amendments + the REQ-023 / AC-028 traceability rows |
| `b88684d` | S4.2 | the minimal fix (D-1…D-5) — `src/main.py`, `settings/registry.py`, `permissions/feature_settings.py`, `sessionmanagement/feature_settings.py`, two test files, **`STRUCTURE.md` regenerated in the same commit** |
| `38056af` | S4.3 | refactor — `settings/registry.py` one-liner, the AC-009 witness comments, **`STRUCTURE.md` regenerated in the same commit** (478 → 473 lines) |
| `c9dfb55` | S4.3 | sixth spec amended: `structlog-logging.md` AC-009 / REQ-005 wording |

Both commits that edit a `.py` file (`b88684d`, `38056af`) carry their `STRUCTURE.md` regeneration; the two docs commits touch no source. `git status --porcelain` is **empty** — every Phase 4 artefact is committed, nothing is left in the working tree. There is **no task DAG for an ISSUE** (Phase 2 is skipped), so the "update status" half of this step is this state-machine line, not a `tasks.json` `VERIFIED` field.

**Re-run of the targeted `green_command` against the committed state** (proving the commit, not the pre-commit buffer, is GREEN):

```text
uv run pytest tests/acceptance/settings_coverage/test_wiring.py tests/contract/settings_coverage/test_inventory.py \
     tests/acceptance/settings_coverage/test_persistence.py \
     tests/acceptance/filemanagement/test_filemanagement.py::test_ac_029_default_local_backend \
     tests/integration/singleton_install/test_composition_root.py \
     tests/acceptance/sessionmanagement/test_settings.py -q
    → 14 passed in 5.59s        (identical count to S4.2, the orchestrator re-run and S4.3)
```

The full suite was **not** run here — it is the Phase 5 gate (S5.1), as is the whole-repo ruff sweep (S5.2).

**State machine: `GREEN → REFACTORED`.** Next atomic step is **S5.1** (run the full test suite), then S5.2 (lint + types), S5.3 (update traceability), S5.4 (verification report, spec coverage = 100%). This change is **not** light-tier (§8), so the full Phase 5 gate set applies.

## 7. Inherited baseline on `main` (measured verbatim in this worktree)

`uv run pytest tests/ -q` at base `25b7e7b` in this worktree:

```
3 failed, 887 passed, 1 skipped in 351.73s (0:05:51)
SKIPPED [1] tests\acceptance\filemanagement\test_filemanagement.py:364: symlinks not available on this host
FAILED tests/acceptance/test_structure_map.py::test_ac_021_committed_map_matches_fresh_render
FAILED tests/property/usermanagement/test_usermanagement_properties.py::test_inv_002_password_round_trip
FAILED tests/property/authentication/test_tokens.py::test_inv_001_token_hash_uniqueness
```

- **`test_ac_021` — deterministic, and the TODO's stated cause is stale.** The TODO records a stale map (`docs/ 225` vs `231` files). Measured here: `uv run python scripts/make_map.py --check` **exits 0** and the line counts match (committed 2004, fresh 2004). The failure is a **line-ending** artifact: `core.autocrlf=true` with **no `.gitattributes`** checks the committed LF blob out as CRLF, generate mode always writes LF (`scripts/make_map.py:576`), and `test_ac_021` compares **raw bytes** (`tests/acceptance/test_structure_map.py:1499`) while `--check` normalises CRLF→LF by design (`scripts/make_map.py:536-550`, structure-map EDGE-016). Regenerating the map in this worktree makes the byte compare pass there (the regenerated file is LF), and this change **does** regenerate it because it edits `src/main.py` — but the root cause is checkout-wide line endings and belongs to the separate `gitattributes-line-endings` TODO, which this change does not touch.
- **The two property failures are load-dependent Hypothesis flakes, not defects.** Both are `DeadlineExceeded` / `FlakyFailure` (`test_inv_002` took 257.78 ms against the 200 ms deadline on the first run and 198.47 ms on the retry). Re-run in isolation: `2 passed in 5.15s`. Phase 5 records them as the inherited flaky pair, not as regressions; they are not fixed here (out of scope).

**Baseline for this change = 3 failed / 887 passed / 1 skipped**, with the composition of that 3 as above. Phase 5 must show no failure other than these inherited ones.

### 7.1 Full regression run (S5.1) — 2026-10-11, HEAD `736a24c`, clean tree

```
uv run pytest tests/ -q
→ 891 passed, 1 skipped in 273.91s (0:04:33)
SKIPPED [1] tests\acceptance\filemanagement\test_filemanagement.py:364: symlinks not available on this host
```

No `-x`, no deselection, no marker filter; the run went to completion. `uv run pytest tests/ -q --collect-only` → **892 tests collected** against the baseline's 891 (3 failed + 887 passed + 1 skipped). The +1 is this change's own new reproduction test `tests/acceptance/settings_coverage/test_persistence.py::test_ac_028_persisted_override_warns` (the only test function the change adds — `git diff 25b7e7b HEAD -- tests/` shows one added `def test_…`, the rest of the test diff being edits to existing functions).

**Failures in the full run: 0.** Every one of the three inherited baseline failures (§7) was checked against this run:

| Inherited failure (§7) | Full run at `736a24c` | Classification |
|---|---|---|
| `tests/acceptance/test_structure_map.py::test_ac_021_committed_map_matches_fresh_render` | **did not fail** | **Measured difference, not a fix this change claims.** This change regenerates `STRUCTURE.md` (commit `b88684d`, required by the `src/main.py` edit), and the regenerated file is written with LF, so the raw-byte compare passes *in this worktree*. The root cause — `core.autocrlf=true` with no `.gitattributes` checking the LF blob out as CRLF — is untouched and still belongs to the separate `gitattributes-line-endings` TODO (§10). On `main` at base `25b7e7b` it still fails. |
| `tests/property/usermanagement/test_usermanagement_properties.py::test_inv_002_password_round_trip` | **did not fail** | Known load-dependent Hypothesis `DeadlineExceeded` flake (§7). Not fixed here; it simply did not recur in this run (the run was faster: 273.91s vs 351.73s). |
| `tests/property/authentication/test_tokens.py::test_inv_001_token_hash_uniqueness` | **did not fail** | Same inherited flake pair (§7). Not fixed here; did not recur. |

Isolation re-run of all three (the §7 check, re-run at this HEAD):

```
uv run pytest tests/acceptance/test_structure_map.py::test_ac_021_committed_map_matches_fresh_render \
    tests/property/usermanagement/test_usermanagement_properties.py::test_inv_002_password_round_trip \
    tests/property/authentication/test_tokens.py::test_inv_001_token_hash_uniqueness -q
→ 3 passed in 5.57s
```

**Reproduction tests GREEN (ISSUE obligation):**

```
uv run pytest tests/acceptance/settings_coverage/test_wiring.py tests/contract/settings_coverage/test_inventory.py \
    tests/acceptance/settings_coverage/test_persistence.py -q
→ 9 passed in 3.71s
```

The 9 are the R-1 / R-2 / D-5 witnesses that were RED at the S3.2 gate (§5.3: 3 failed, 6 passed) — all 9 now pass.

**Phase 5 regression gate: PASS.** The full suite is GREEN with **zero** failures, so there is no failure to classify as a regression: the run is strictly better than the inherited baseline (3 failed → 0 failed) and the only composition differences are the +1 collected test this change adds and the `test_ac_021` line-ending artifact passing in this worktree, both accounted for above. No test was weakened, deleted or deselected to reach this result (the single assertion change in `tests/acceptance/sessionmanagement/test_settings.py:58` is the spec-amendment narrowing recorded in §9). Next: **S5.2** (whole-repo `ruff check .` + `mypy src/`).

### 7.2 Lint + types (S5.2) — 2026-10-11, HEAD `aed5820`, clean tree

The whole-repo ruff sweep runs **once, here** (AGENTS.md "Tooling & Execution Environment"), matching CI exactly. The CI job set was enumerated from `.github/workflows/lint.yml`, `.github/workflows/quality.yml` and `.github/workflows/spec-validation.yml` (the three workflows that exist), and each job's command was re-run verbatim in this worktree.

| Command (verbatim, as CI runs it) | CI job | Exit | Result |
|---|---|---|---|
| `uv run ruff check .` | Lint → `lint` | **0** | `All checks passed!` (whole-repo sweep) |
| `uv run ruff format --check .` | Lint → `lint` ("Check formatting") | **0** | `362 files already formatted` |
| `uv run mypy src/` | Quality → `type-check` (gate) | **0** | `Success: no issues found in 84 source files` |
| `uv run mypy scripts/` | Quality → `type-check` (gate) | **0** | `Success: no issues found in 4 source files` |
| `uv run ty check src/` | Quality → `type-check` (**informational**, `continue-on-error: true`) | 1 | `Found 160 diagnostics` — see the classification below |
| `uv run bandit -r src/` | Quality → `security` | **0** | 0 issues at every severity, 0 files skipped |
| `uv run pip-audit` | Quality → `security` | **0** | `No known vulnerabilities found` (the project itself is skipped: not on PyPI) |
| `uv run deptry .` | Quality → `dependencies` (gate) | **0** | `Success! No dependency issues found.` (91 files scanned) |
| `uv run --group docs mkdocs build --strict` | Quality → `docs` (gate) | **0** | built in 3.31 s, no strict-mode warning; `site/` is gitignored, tree stays clean |
| `ALEMBIC_DATABASE_URL=sqlite:///<temp>/alembic-s52.db uv run alembic upgrade head` | Quality → `migrations` (gate) | **0** | both revisions applied; `alembic current` → `d94b7f2e6a31 (head)`. Throwaway DB under the OS temp dir — the repo's `data/migrations.db` was never touched. The change touches no SQLModel table, so this is the expected **no-delta** confirmation |
| `uv run complexipy src tests scripts --max-complexity-allowed 15` | Quality → `complexity` (gate) | **1** | 4 functions over the ceiling, **all in `scripts/`** — see the classification below |
| `uv run python scripts/check_traceability.py` | Spec Validation → `traceability` | **0** | `Traceability: PASS (891 matrix rows, 136 spec IDs, 876 test functions)` |
| `uv run python scripts/validate_task_dag.py .github/task-runner/tasks.json` | Spec Validation (CI runs it with `\|\| true`) | **0** | `Task DAG validation PASSED: 12 tasks, acyclic, well-formed.` |
| `uv run python scripts/verify_spec.py docs/specs/<spec>` — the CI loop over all 15 specs (`template.md` skipped) | Spec Validation → `spec-validation` | **0 ×15** | `Traceability: PASS` for every spec: authentication, event-bus, file-management, logging-coverage, logging, mail-service, search, session-management, settings-coverage, settings-public-registry-setter, settings, structlog-logging, structure-map, user-management, user-roles-permissions |
| `uv run python scripts/make_map.py --check` | (no CI job; the `code-structure-map` gate) | **0** | silent exit 0 = the committed `STRUCTURE.md` is current (it prints only on missing/stale, `scripts/make_map.py:536-550`) |
| `uv run pytest tests/ --cov` | Quality → `coverage` (`fail_under = 92`) | not run | Re-running the full suite is excluded from this step by its brief; the suite itself is GREEN at §7.1. The coverage threshold is a CI gate and is not re-measured here — flagged for the Phase 6 pre-merge gate |

**Nothing was fixed by this step.** ruff check and ruff format are clean over the whole repo, so there is no lint/format violation introduced by this change and no `style(...)` commit was made; the tree is unchanged apart from this record.

**`ty` (informational, not a gate).** CI runs `uv run ty check src/` with `continue-on-error: true`; **mypy is the gate** and it passes. `ty` reports **160** diagnostics here against **159** on `main` (measured read-only in the primary worktree). Normalising the worktree path prefix out of both outputs and diffing them leaves exactly **one** branch-only diagnostic: `src/main.py:207:42: invalid-type-form: Variable of type \`type\` is not allowed in a type expression`, on the `_SETTINGS_REGISTRATIONS: tuple[Callable[[SettingsRegistry], None], …]` annotation this change adds. It is the same `invalid-type-form` class `ty` already emits **seven** times on `main` for the identical `SettingsRegistry`-in-a-callable-annotation shape (`src/backend/settings/registry.py:50`, `src/backend/eventbus/eventbus.py:252`, `src/backend/permissions/service.py:528`, `src/backend/search/service.py:597`, `src/backend/sessionmanagement/service.py:363`, `src/main.py:129`, `src/main.py:148`) — a `ty` limitation around the re-exported class object, not a typing error: mypy (strict, the declared gate) accepts it. No action taken; recorded for the record.

**`complexipy` — exit 1, and the honest classification is neither "caused by this change" nor "pre-existing on `main`": the branch is stale.**

- The four failures are `scripts/check_traceability.py::check` (17), `scripts/check_traceability.py::matrix_rows` (19), `scripts/validate_task_dag.py::check_acyclic` (22), `scripts/verify_spec.py::main` (22). **None is in a file this change touches**: `git diff 25b7e7b..HEAD -- scripts/ pyproject.toml` is **empty**, and no branch commit (`main..HEAD`) touches either path.
- **`main` passes the identical command.** Read-only in the primary worktree: `uv run complexipy src tests scripts --max-complexity-allowed 15` → `All functions are within the allowed complexity.`, **exit 0**.
- The difference is that `main` moved past the branch point. `git merge-base main HEAD` = `25b7e7b`; `git log HEAD..main` contains `91b4237 Merge pull request #82 from …/chore/complexipy-scripts` (with `f2878d7`, `4dd3d78`, `7ebc19a` refactoring exactly those three script modules under the ceiling, and `54decc7` adding `scripts` to `[tool.complexipy] paths`). The branch was cut before that merge, so it still carries the pre-#82 `scripts/` — which fails the CLI command CI passes (`src tests scripts` on the command line, which overrides the config `paths`, so the branch's own `paths = ["src", "tests"]` does not shield it).
- **Merging `main` into the branch clears it, with one trivial conflict.** `git merge-tree --write-tree HEAD main` reports a conflict **only in `STRUCTURE.md`**; in the resulting tree `scripts/` and `pyproject.toml` are byte-identical to `main`'s (`git diff <merged-tree> main -- scripts/ pyproject.toml` is empty) and `src/` and `tests/` are byte-identical to the branch's (`git diff <merged-tree> HEAD -- src/ tests/` is empty). Since the branch's own `src/` and `tests/` are already under the ceiling (the only failures are in `scripts/`) and `main`'s `scripts/` pass, the merged state passes the complexity gate. The `STRUCTURE.md` conflict is resolved by taking either side and regenerating (`uv run python scripts/make_map.py`), per AGENTS.md "Git Worktrees".
- **Action this belongs to: the orchestrator, before S6.4.** The change branch must merge (or rebase onto) `main` before its PR opens, so the PR carries `main`'s `chore/complexipy-scripts` state. S5.2 does not perform that merge — it is a worktree/branch operation owned by the orchestrator (git skill), and rewriting this branch's `scripts/` here would be an out-of-scope logic change, not a lint fix. (For the record: for a same-repo `pull_request` run, `actions/checkout` checks out the PR merge ref, where `main`'s `scripts/` win, so the PR's `complexity` job is expected to pass even without the merge — the merge is what makes the branch itself and the local gate green, and it is needed anyway for `STRUCTURE.md` hygiene.)

**Phase 5 lint/types gate: PASS.** The two gates AGENTS.md names for an ISSUE — `uv run ruff check .` (whole repo, matching `.github/workflows/lint.yml` exactly) and `uv run mypy src/` — are both clean, as is `mypy scripts/`, `deptry`, `bandit`, `pip-audit`, `mkdocs build --strict`, `alembic upgrade head`, `check_traceability.py`, `validate_task_dag.py`, `verify_spec.py` ×15 and `make_map.py --check`. The only non-zero exits are `ty` (informational by CI configuration, +1 diagnostic of an already-existing class) and `complexipy` (four `scripts/` functions this change never touched, already fixed on `main` by PR #82, cleared by merging `main` — recorded above and handed to the orchestrator). Next: **S5.3** (traceability rows).

### 7.3 Branch refreshed (`main` merged) — 2026-10-11, merge commit `9b19d7d`, clean tree

**Why this step exists.** §7.2 established that the `complexipy` exit 1 is neither caused by this change nor pre-existing on `main`: the **branch is stale**, and handed the merge to the orchestrator. This step performs exactly that merge and re-confirms only the gates the merge touches.

**Fetch / `main` state (primary worktree, read-only).** `git fetch origin` → local `main` == `origin/main` == `877dcff`; `git rev-list --left-right --count main...origin/main` → `0 0`, so **no fast-forward was needed** and nothing else in the primary worktree was touched.

**The merge.** Change worktree tree clean at `fe7026a`; `git merge main --no-edit`. `git merge-base HEAD main` = `25b7e7b` (the branch point). Merge commit: **`9b19d7d` — `Merge branch 'main' into issue/startup-settings-registration-gaps`**. `main` brought in **25 commits** (`git log --oneline fe7026a..main`). The substantive ones are PR #82 (`91b4237 Merge pull request #82 from …/chore/complexipy-scripts`): `f2878d7` / `4dd3d78` / `7ebc19a` refactoring `scripts/check_traceability.py`, `scripts/validate_task_dag.py` and `scripts/verify_spec.py` under the ceiling, `54decc7` bringing `scripts/` into the gate (`pyproject.toml`, `.github/workflows/quality.yml`), **ADR-087** (`docs/decisions/ADR-087-complexipy-scope-extended-to-scripts.md`), the `complexipy-scripts` verification record, its `CHANGELOG.md` entry, and its planning-record archive moves. The remainder are other changes' P.2 / value-triage / status-advance records. Three of them touch **this** change's planning records (`72d799b` READY, `eddf94f` WAITING, `093f2ff` LQ-01 answered + IN-WORKFLOW) — they arrive **from `main`** via the merge; this step authored nothing under `docs/todo/` or `docs/questions/`.

**Conflict list: exactly one path, exactly as predicted.** `git merge-tree --write-tree HEAD main` had predicted `CONFLICT (content): Merge conflict in STRUCTURE.md` and nothing else; the real merge matched — `UU STRUCTURE.md` was the **only** unmerged path, every other path auto-merged. Resolved per AGENTS.md "Git Worktrees" and `code-structure-map` rule 4: **took `main`'s side** (`git checkout --theirs STRUCTURE.md`), then **regenerated** — `uv run python scripts/make_map.py` (exit 0) → `uv run python scripts/make_map.py --check` → **exit 0**. The generated file was never hand-merged. The regenerated map differs from `main`'s only in what this change itself moves (`src/main.py` 239→264 lines, `src/backend/settings/registry.py` 467→473, `src/backend/sessionmanagement/feature_settings.py` 58→61, `docs/` 236→237 files) — i.e. it describes the **merged tree**, not either side.

**Merged-state identity check (the §7.2 prediction, confirmed on the real merge):**

- `git diff 9b19d7d main -- scripts/ pyproject.toml .github/workflows/quality.yml` → **empty**: the branch now carries `main`'s `scripts/` and gate configuration byte-for-byte.
- `git diff 9b19d7d fe7026a -- src/ tests/` → **empty**: this change's `src/` and `tests/` are untouched by the merge, and this step modified **no** source or test file.

**Re-confirmed gates (targeted).** The merge touched only `scripts/`, gate configuration, generated and doc files, so the full suite is deliberately **not** re-run — §7.1 remains the regression record.

| Command | Exit | Result |
|---|---|---|
| `uv run complexipy src tests scripts --max-complexity-allowed 15` | **0** | `All functions are within the allowed complexity.` — the §7.2 exit-1 gate is **cleared** (was 4 functions over: `check_traceability.py::check` 17, `check_traceability.py::matrix_rows` 19, `validate_task_dag.py::check_acyclic` 22, `verify_spec.py::main` 22) |
| `uv run python scripts/make_map.py --check` | **0** | the committed map is current after the regeneration |
| `uv run python scripts/check_traceability.py` | **0** | `Traceability: PASS (891 matrix rows, 136 spec IDs, 876 test functions)` |
| `uv run python scripts/validate_task_dag.py .github/task-runner/tasks.json` | **0** | `Task DAG validation PASSED: 12 tasks, acyclic, well-formed.` |
| `uv run python scripts/verify_spec.py docs/specs/<spec>` × **15** (`template.md` skipped) | **0 ×15** | every spec PASS: authentication, event-bus, file-management, logging-coverage, logging, mail-service, search, session-management, settings-coverage, settings-public-registry-setter, settings, structlog-logging, structure-map, user-management, user-roles-permissions |
| `uv run ruff check .` | **0** | `All checks passed!` (whole-repo sweep, as CI runs it) |
| `uv run ruff format --check .` | **0** | `362 files already formatted` |
| `uv run mypy src/` | **0** | `Success: no issues found in 84 source files` — re-checked because S5.2's types gate sits on the merged tree; the merge changed no `src/` file, so the gate still holds |
| `uv run pytest tests/acceptance/settings_coverage tests/contract/settings_coverage tests/acceptance/test_structure_map.py tests/unit/test_make_map.py -q` | **0** | **68 passed in 19.89s** — the reproduction tests (§5.3 RED → §6.1 GREEN) plus the structure-map test, which is the direct witness of the artifact the conflict resolution regenerated |

**Path correction recorded.** The brief named `tests/unit/scripts`; that directory **does not exist** in this repository. The scripts' unit tests are the single module `tests/unit/test_make_map.py` — `grep -l` over `tests/` for `check_traceability|validate_task_dag|verify_spec|make_map` returns only `tests/acceptance/test_structure_map.py`, `tests/property/test_structure_map.py` and `tests/unit/test_make_map.py` — so that module was substituted and nothing was skipped.

**Still open after this step (unchanged by the merge).** The §7.2 coverage row remains **unmeasured**: `uv run pytest tests/ --cov` against `fail_under = 92` (Quality → `coverage`) has not been run on this branch and MUST be confirmed at the Phase 6 pre-merge gate (S6.4) — logged as **P-119**. The `ty` informational diagnostic (+1 instance of an already-existing class) is likewise unchanged; mypy remains the gate and passes.

**Branch state after the merge:** clean working tree, HEAD `9b19d7d`, `main` reachable from HEAD. Next: **S5.3** (traceability rows).

### 7.4 Traceability updated (S5.3) — 2026-10-11, HEAD `bc05ca5`, clean tree

**Objective.** Bring `docs/verification/traceability.md` up to date with this change's evidence: every
REQ/AC the fix touches cites a GREEN test, and the new REQ-023 / AC-028 pair is recorded GREEN. Docs only —
no `src/`, no `tests/`, no `docs/todo/`, no `docs/questions/`, no CHANGELOG entry (that is Phase 6, S6.4).

**Rows updated — 11, in place, no row added or removed** (the matrix still parses to **891 rows**):

| Matrix (spec) | Row | Cell before S5.3 | Cell after S5.3 |
|---|---|---|---|
| Settings Coverage | REQ-002 / AC-003 (`test_main_wires_all_features`) | `RED (S3.2 …)` | `GREEN` — D-1 fixed, PROBED 34 / REGISTERED 34 / MISSING [] |
| Settings Coverage | REQ-017 / AC-022 (`test_key_prefix`) | `GREEN (re-observed S3.2 …)` | `GREEN` — S5.1 full-suite observation of the widened guard |
| Settings Coverage | REQ-018 / AC-023 (`test_category_group`) | `RED (S3.2 …)` | `GREEN` — D-3 fixed on all four keys |
| Settings Coverage | REQ-019 / AC-024 (`test_inventory_matches`) | `GREEN (re-observed S3.2 …)` | `GREEN` — S5.1 observation over the 34-key inventory |
| Settings Coverage | **REQ-023 / AC-028** (`test_ac_028_persisted_override_warns`) | `RED (S3.2 …)` | `GREEN` — D-5 fixed at S4.2 |
| Settings Coverage | NFR-002 (`test_no_secret_settings`) | `GREEN (re-observed S3.2 …)` | `GREEN` — D-6 resolved by the wording amendment |
| Settings Coverage | NFR-003 (`test_inventory_backward_compatible`) | `GREEN (re-observed S3.2 …)` | `GREEN` — S5.1 observation of the nine-feature guard |
| File Management | REQ-015 / AC-029 (`test_ac_029_default_local_backend`) | bare `GREEN` | `GREEN` — D-4: the composition root passes no backend; the amended v3 wording says so |
| Session Management | REQ-019 / AC-039 (`test_ac_039_register_settings_defaults`) | bare `GREEN` | `GREEN` — witness re-derived at S4.2 from the v3 model block (category `security`, group `sessionmanagement`) |
| User Roles & Permissions | REQ-019 / AC-023 (`test_system_set_settings_alias_sync`) | bare `GREEN` | `GREEN` — the REQ-019 model-block category moved to `security`; the witness itself is unchanged |
| Structlog Logging | REQ-005 / AC-009 (`test_ac_009_statements_go_through_get_logger` + per-feature witnesses) | `GREEN (structlog-logging S5.1 …)` | `GREEN` — the amended AC-009 wording and the measured total **43** (19 + 11 + 11 + 2) recorded in the Test column |

**Convention B (decision Q-129) respected.** Each updated cell now carries **this** change's dated
observation (change name + date + evidence inside the cell); the cell each update replaced — the S3.2 RED
observations, the `search` S5.1 `727 passed` cells, the bare `GREEN` cells — is **not** kept twice in the
cell and stays recoverable from git history (`git log -p -- docs/verification/traceability.md`). No row this
change did not touch was refreshed: the other 880 rows are byte-identical.

**Why the four non-Settings-Coverage rows are in scope.** They are the rows of the four specs this change's
approved in-PR amendments touched (§4): `file-management.md` REQ-015/AC-029 (D-4), `session-management.md`
REQ-019/AC-039 (D-3, the model block the witness is derived from), `user-roles-permissions.md` REQ-019
(D-3, the `permissions.system_principal` category), `structlog-logging.md` REQ-005/AC-009 (the per-file
statement count the REQ-023 diagnostic moves to 19, and the AC-009 wording amendment of S4.3). The
`permissions` row's own witness does not assert the category — the cell says so explicitly and points at
the widened settings-coverage AC-023 guard as the witness of the fix.

**Matrix note rewritten.** The Settings Coverage section's note ("Row added with the spec amendment
(S4.1)") described a state that no longer holds — it said the REQ-023 row "stays RED until the S4.2 fix"
and that the `sessionmanagement` rows would be updated "in Phase 4". It is replaced by a "Rows updated by
`startup-settings-registration-gaps` (S5.3)" note listing the 11 rows, the Q-129 rule, and the §-pointers
to the evidence.

**Fresh measurements taken in this step** (the branch moved since §7.1 and §6.1, so the cited figures were
re-measured at `bc05ca5` before being written into the cells; the full suite is **not** re-run — §7.1 stays
the regression record):

| Command | Exit | Result |
|---|---|---|
| `uv run pytest tests/acceptance/settings_coverage/test_wiring.py tests/contract/settings_coverage/test_inventory.py tests/acceptance/settings_coverage/test_persistence.py -q` | **0** | **9 passed in 2.27s** — the three reproduction files (3 failed / 6 passed at the §5.3 RED gate) |
| the effective `green_command` of §5 (six paths) | **0** | **14 passed in 4.65s** — identical count to §6.1 / §6.2 |
| `uv run pytest tests/acceptance/logging_coverage/test_statements_via_feature.py tests/acceptance/sessionmanagement/test_settings.py::test_ac_039_register_settings_defaults tests/acceptance/permissions/test_system_principal.py::test_system_set_settings_alias_sync -q` | **0** | **5 passed in 1.03s** — the three witnesses whose rows were refreshed |
| `uv run python scripts/check_traceability.py` | **0** | `Traceability: PASS (891 matrix rows, 136 spec IDs, 876 test functions)` — the S5.3 gate |

**Gate: S5.3 PASSES.** Every REQ/AC this change touched has a row citing a GREEN test, REQ-023 / AC-028 is
GREEN, and referential integrity holds. **State machine: unchanged (`REFACTORED` → `VERIFIED` at S5.4).**
Next: **S5.4** (verification report, spec coverage = 100%).

## 8. Light ISSUE tier assessment — **NOT qualified** (full Phase 5 gate set applies)

AGENTS.md "Light ISSUE tier" requires **all** of: single feature, fix touches ≤ 3 files excluding tests, no new dependency, no new public interface, no cross-feature change, and the triage naming the covering tests.

| Criterion | Check |
|---|---|
| Single feature | **No** — the fix spans the composition root plus **four** features (settings, permissions, sessionmanagement, filemanagement) and **five** approved specs |
| ≤ 3 files excluding tests | **No** — **10**: `src/main.py`, `src/backend/sessionmanagement/feature_settings.py`, `src/backend/permissions/feature_settings.py`, `src/backend/settings/registry.py`, `docs/specs/settings-coverage.md`, `docs/specs/settings-public-registry-setter.md`, `docs/specs/user-roles-permissions.md`, `docs/specs/session-management.md`, `STRUCTURE.md`, `CHANGELOG.md` (+ `pyproject.toml` bump, + `docs/verification/traceability.md`) |
| No new dependency | Yes |
| No new public interface | Yes for D-1…D-4; **D-5 adds one observable behaviour** (a `WARNING` record) |
| No cross-feature change | **No** — this is composition-root wiring that changes what every feature's settings see |
| Existing suite covers the area | Partially — and the covering guards are themselves part of the defect (D-2), which is the opposite of a pre-covered area |

**Verdict: the light tier does not apply.** Phase 5 runs the **full ISSUE gate set**: the reproduction tests GREEN, the **full regression suite** with no new failure beyond the inherited set (§7), `uv run ruff check .`, `uv run mypy src/`, and the traceability update (AGENTS.md Phase 5, ISSUE items 9–12). The tier is not forced to fit.

**Covering tests named for the record** (the area's existing coverage, which the change widens rather than replaces): `tests/acceptance/settings_coverage/test_wiring.py::test_main_wires_all_features` (AC-003), `tests/contract/settings_coverage/test_inventory.py::test_key_prefix` / `::test_category_group` / `::test_inventory_matches` / `::test_no_secret_settings` (AC-022/023/024, NFR-002), `tests/integration/singleton_install/test_composition_root.py::test_ac_016_main_installs_through_setter` / `::test_installed_registry_serves_feature_registration` (REQ-011/AC-016 × settings-coverage REQ-002), `tests/acceptance/filemanagement/test_filemanagement.py::test_ac_029_default_local_backend` (AC-029), `tests/acceptance/sessionmanagement/test_settings.py::test_ac_039_register_settings_defaults` (session-management REQ-019/AC-039).

## 9. Constraints and risks

- **The composition-root witness must stay valid.** `tests/integration/singleton_install/test_composition_root.py` patches the six feature modules' `register_settings` **before** `import main` and asserts `len(registered) == 6` (`:126`), and `_consumer_sites_passing_the_handle()` (`:158-181`) treats any call named `register_*_settings` as a consumer site that must not receive the local `_settings_registry` handle. The fix must therefore keep importing each feature's `register_settings` from its package root and calling it (a list of the imported callables is fine; a dynamic `importlib` lookup would silently un-spy the modules and break the REQ-011 witness). The `== 6` assertion is the count of **spied** modules, not of registrations, so it stays correct once the spec wording is amended (Q-11) — but if the fix changes the call shape, this test is a first-class regression risk.
- **Install-before-register ordering is normative.** The install runs at `src/main.py:156` (comment `:151-155`) and the registrations at `:191-196`; every consumer site reads the instance back through the `_shared_settings_registry()` helper (`:84`), never a local handle. The loop must not reorder install-before-register (settings-public-registry-setter REQ-011).
- **`import main` has side effects** — it creates `data/`, `logs/` and `settings/` in the current working directory. Any guard that imports it must run with `cwd` in a temp dir (the existing witness uses `cwd=_REPO_ROOT`, `test_wiring.py:26`, which is the source of the repo-root `settings/` pollution measured at Q-22).
- **No test may be weakened or deleted to reach GREEN.** The one test assertion this change changes (`tests/acceptance/sessionmanagement/test_settings.py:58`) is a narrowing to what AC-039 actually states, driven by the spec amendment — recorded here and in the review report, not a weakening of the contract.
- **Category change is a live behaviour change for views/UI grouping** (`grouped_views()` hierarchy). `permissions.system_principal` and the three `sessionmanagement.*` keys move from their own category to `security`; the amended specs and the widened AC-023 guard are what make that intentional and checked.
- **D-4 changes when the storage root is read**, not its value: the literal and the registered default are identical (`./data/files`), so the on-disk location is unchanged unless the setting is changed — which is the point (REQ-015).
- **STRUCTURE.md** is regenerated in the same commit as the `src/main.py` edit; on a merge conflict in it, take either side and regenerate (never hand-merge).

## 10. Out of scope (TODO `docs/todo/startup-settings-registration-gaps.md:36-42`, plus the P.3 answers)

- No new settings keys, no new kinds, no new feature.
- No settings **schema/versioning** mechanism (Q-28) — D-5 is a diagnostic only.
- No repo-root `settings/` hygiene fixture beyond what the widened witness needs (Q-22) — the pollution is a consequence of the witness's `cwd`, recorded as a constraint (§9), and the isolation mechanism already exists from the merged `settings-test-isolation` change (`tests/conftest.py` `_logging_session_setup` installs an isolated registry; `tests/unit/test_settings_test_isolation.py` guards it).
- No line-ending / `.gitattributes` work (separate TODO `gitattributes-line-endings`) — §7.
- No fix for the two inherited Hypothesis deadline flakes (§7).
- No change to `docs/questions/archive-AI_Questions.md` (retired central file).
- No new dependency, no ADR (no new dependency, no new pattern; the composition-root registration list is the pattern the spec already describes).

## 11. Acceptance signal (TODO `docs/todo/startup-settings-registration-gaps.md:58-59`)

A test that starts the real composition root finds **all 34** feature settings keys registered in the shared registry (0 missing); the contract inventory guard covers all nine features and every registered setting's `category` is `application` or `security`; the composed `FileService` reads `filemanagement.storage_root` live; a persisted value overriding a default emits one `WARNING`; the full suite shows no failure beyond the inherited set (§7), and ruff and mypy are clean.

## 12. Version and changelog

ISSUE → **`patch`** (AGENTS.md Versioning): `bump-my-version bump patch` at S6.4 with a clean tree, `1.2.0 → 1.2.1`, `tag = false`; the `## [Unreleased]` entries move to `## [1.2.1] - <date>` in the same commit. `CHANGELOG.md` `## [Unreleased]` is currently empty, so this change's entries are the only ones in it.

**S3.1 done** (2026-10-11): R-1, R-2 and the D-5 witness are in place, LQ-01 is ANSWERED (§5.1), and the targeted run shows the expected RED — `uv run pytest tests/acceptance/settings_coverage/test_wiring.py tests/contract/settings_coverage/test_inventory.py tests/acceptance/settings_coverage/test_persistence.py -v` → **3 failed, 6 passed**: `test_main_wires_all_features` (16 missing keys, D-1), `test_category_group` (4 categories + 3 missing groups, D-3), `test_ac_028_persisted_override_warns` (no override `WARNING`, D-5). Every failure is an `AssertionError` on behaviour — no collection, import or `ValidationError` failure. **Next step: S3.2** (ruff on the changed paths + confirm and record RED).

---

## 13. Verification report (S5.4) — 2026-10-11, HEAD `845569f`, clean tree

**Numbering note.** The step brief asked for a section numbered 9; §9–§12 of this record are already occupied (constraints, out of scope, acceptance signal, version/changelog) and existing sections are never renumbered, so the Phase 5 report is appended as **§13**. It closes Phase 5. Docs only — this step changed no `src/`, no `tests/`, no `CHANGELOG.md`, no `pyproject.toml`, no `docs/todo/`, no `docs/questions/`.

### 13.1 Verdict

**VERIFIED.** Every gate of the ISSUE Phase 5 gate set (AGENTS.md Phase 5 → ISSUE items 9–12; §8 establishes that the light tier does **not** apply, so the full set ran) is measured and passes, and the one gate §7.2 left unmeasured — the CI `coverage` job, logged as **P-119** — is measured here and passes: **93.85%** against `fail_under = 92`.

**State machine: `REFACTORED → VERIFIED`** (§6.2 reached `REFACTORED`; the transition requires the traceability matrix updated — §7.4 — and it is).

The change satisfies its normative basis: all six defects (§3) are closed by the fix or by an approved spec amendment, the reproduction witnesses that were RED at §5.3 are GREEN, the full suite is strictly better than the inherited baseline (§7 → §7.1: 3 failed → **0 failed**), and **every REQ/AC the change touches has at least one GREEN test** (§13.4).

### 13.2 Coverage — the gate this step measured

CI command read from `.github/workflows/quality.yml:61` (`uv run pytest tests/ --cov --cov-report=xml`, Quality → `coverage`); threshold read from `pyproject.toml:112` (`[tool.coverage.report] fail_under = 92`), with `[tool.coverage.run]` `branch = true`, `source = ["src/backend", "src/frontend"]`. Run **verbatim**, no deselection, no `-x`, no marker filter, in this worktree.

| Run | Test outcome | Coverage output | Gate |
|---|---|---|---|
| 1 | `2 failed, 889 passed, 1 skipped in 291.85s` | `Required test coverage of 92.0% reached. Total coverage: 93.85%` | **PASS** |
| 2 | `891 passed, 1 skipped in 273.80s` — **0 failed** | `Required test coverage of 92.0% reached. Total coverage: 93.85%` | **PASS** |

The total is **93.85%** in both runs — identical to two decimal places, so the figure is stable, not a lucky sample. The margin over the floor is **+1.85 points**. `coverage.xml` is gitignored (`.gitignore:47`) and `git status --porcelain` is empty after both runs. The §7.2 row that said "not run" is **superseded** by this section.

**Run 1's two failures — classified (skill `verify`: pre-existing vs regression).** Neither is a regression; run 2, the same command on the same tree, has zero failures.

| Failing test | Observed | Classification |
|---|---|---|
| `tests/property/authentication/test_tokens.py::test_inv_001_token_hash_uniqueness` | `hypothesis.errors.DeadlineExceeded: Test took 312.87ms, which exceeds the deadline of 200.00ms` | **Inherited flake (§7)** — one of the two documented load-dependent deadline flakes; it did not fail in the §7.1 full-suite run and it passed in the isolation re-run. Not fixed here (§10) |
| `tests/contract/search/test_search_contracts.py::test_nfr_001_performance_budgets` | `assert 0.5423477 < 0.3` — median of 15 × `svc.search(...)` over 10k items vs the 300 ms local budget | **Not a regression.** A wall-clock budget contract, documented as load/hardware-sensitive (`docs/verification/pyproject-tooling-gaps.md:231` with the same classification, `docs/verification/search.md:456`, `docs/workflow/PROBLEMS.md:330` — a ~293 ms median against the 300 ms budget). Measured here: it **passes standalone** (`2 passed in 8.31s` with the token flake) and **passes under `--cov` in isolation** (`1 passed in 9.23s`), it **did not fail in run 2**, and this change touches **no** search code or test — `git diff main...HEAD -- tests/contract/search/` is empty and the whole `src/` diff is the four files of §6 |

### 13.3 Gate table

| Gate | Command | Measured result | Recorded |
|---|---|---|---|
| S5.1 full regression (ISSUE 9) | `uv run pytest tests/ -q` | **891 passed, 1 skipped, 0 failed** in 273.91s at `736a24c` (baseline §7: 3 failed / 887 passed / 1 skipped → strictly better; the +1 collected test is this change's own `test_ac_028_persisted_override_warns`) | §7.1 |
| Reproduction tests GREEN (ISSUE obligation) | `uv run pytest tests/acceptance/settings_coverage/test_wiring.py tests/contract/settings_coverage/test_inventory.py tests/acceptance/settings_coverage/test_persistence.py -q` | **9 passed** — the same three files were **3 failed / 6 passed** at the §5.3 RED gate | §7.1, §7.4 |
| Targeted `green_command` (§5) | six paths, `-q` | **14 passed** (identical count at S4.2, S4.3, S4.4, S5.3) | §6.1, §6.2, §7.4 |
| S5.2 lint — the one whole-repo sweep, as CI runs it | `uv run ruff check .` | **exit 0** — `All checks passed!` | §7.2, re-confirmed §7.3 |
| Formatting | `uv run ruff format --check .` | **exit 0** — `362 files already formatted` | §7.2, §7.3 |
| S5.2 types (the gate) | `uv run mypy src/` · `uv run mypy scripts/` | **exit 0 / exit 0** — 84 / 4 source files, no issues | §7.2, §7.3 |
| Types (informational, `continue-on-error: true`) | `uv run ty check src/` | exit 1 — 160 diagnostics vs 159 on `main`; exactly **+1**, an instance of a class `ty` already emits 7× on `main` | §7.2 |
| Dependencies | `uv run deptry .` | **exit 0** — no dependency issues (91 files) | §7.2 |
| Security | `uv run bandit -r src/` · `uv run pip-audit` | **exit 0 / exit 0** — 0 issues; no known vulnerabilities | §7.2 |
| Docs | `uv run --group docs mkdocs build --strict` | **exit 0** — no strict-mode warning | §7.2 |
| Migrations | `alembic upgrade head` (throwaway DB under the OS temp dir) | **exit 0** — head `d94b7f2e6a31`; the expected **no-delta** confirmation (no SQLModel table touched) | §7.2 |
| Complexity | `uv run complexipy src tests scripts --max-complexity-allowed 15` | exit 1 at §7.2 (4 `scripts/` functions this change never touched — the **branch was stale**) → **exit 0** after the branch refresh | §7.2 → §7.3 |
| **Coverage (measured at S5.4)** | `uv run pytest tests/ --cov --cov-report=xml` | **93.85% ≥ 92 → PASS**, identical in two runs | §13.2 (supersedes the §7.2 "not run" row) |
| S5.3 traceability | `uv run python scripts/check_traceability.py` | **exit 0** — `Traceability: PASS (891 matrix rows, 136 spec IDs, 876 test functions)`; **11 rows** updated to this change's dated GREEN | §7.4 |
| Spec validation (not an ISSUE gate; run anyway) | `uv run python scripts/verify_spec.py docs/specs/<spec>` × 15 | **exit 0 ×15** | §7.2, §7.3 |
| Task DAG | `uv run python scripts/validate_task_dag.py .github/task-runner/tasks.json` | **exit 0** — 12 tasks, acyclic, well-formed | §7.2, §7.3 |
| Structure map | `uv run python scripts/make_map.py --check` | **exit 0** — the committed `STRUCTURE.md` is current (regenerated in the same commit as every `.py` edit: `b88684d`, `38056af`, and after the merge conflict at §7.3) | §6.1, §6.1.1, §7.3 |
| Branch refresh | `git merge main` → `9b19d7d`; merged-tree identity checks | `scripts/`, `pyproject.toml`, `.github/workflows/quality.yml` byte-identical to `main`; `src/`, `tests/` byte-identical to the branch; one conflict (`STRUCTURE.md`), resolved by regenerate, never hand-merged | §7.3 |

### 13.4 Requirement coverage — the actual gate

AGENTS.md: *"Spec coverage = 100% is required. Code coverage is a secondary quality signal, not evidence that the specification has been implemented."* An ISSUE carries **no spec of its own** (§1, §2), so "100%" is evaluated against the **touched** IDs — every REQ/AC/NFR this change amended, re-validated or fixed. `verify_spec.py` is not an ISSUE gate; it was run over all 15 specs anyway (§7.2, §7.3).

| Spec | ID (how this change touched it) | Proving test — GREEN | Matrix row |
|---|---|---|---|
| `settings-coverage.md` | **REQ-001** (feature enumeration amended to all nine features) | `test_main_wires_all_features` (the feature set is **derived** from every `backend.<feature>.feature_settings` module, so a tenth feature cannot hide) + `test_inventory_matches` | REQ-001's own AC-001/AC-002 rows are about registration mechanics and were **not** refreshed (convention B); the enumeration is witnessed by the REQ-002 and REQ-019 rows below |
| `settings-coverage.md` | **REQ-002 / AC-003** (D-1, D-2) | `tests/acceptance/settings_coverage/test_wiring.py::test_main_wires_all_features` — `PROBED 34 / REGISTERED 34 / MISSING []` | updated at S5.3 → GREEN |
| `settings-coverage.md` | **REQ-005 / AC-006** (the fallback that masked D-1; unchanged by the fix) | `test_unregistered_key_fallback` | untouched row, still GREEN (convention B) |
| `settings-coverage.md` | **REQ-017 / AC-022** | `tests/contract/settings_coverage/test_inventory.py::test_key_prefix` (nine features / 34 keys) | updated at S5.3 → GREEN |
| `settings-coverage.md` | **REQ-018 / AC-023** (D-3: category **and** group) | `test_inventory.py::test_category_group` (all 34 rows: category = domain, group = feature name) + `tests/acceptance/sessionmanagement/test_settings.py::test_ac_039_register_settings_defaults` | updated at S5.3 → GREEN |
| `settings-coverage.md` | **REQ-019 / AC-024** (D-2: guard checks the complete inventory) | `test_inventory.py::test_inventory_matches` | updated at S5.3 → GREEN |
| `settings-coverage.md` | **NFR-002** (D-6, resolved by the wording amendment, LQ-01 (a)) | `test_inventory.py::test_no_secret_settings` — credential-named inventory keys must **equal** the documented exemption list (`mail.smtp_password` only); full force on the other 33 keys | updated at S5.3 → GREEN |
| `settings-coverage.md` | **NFR-003** | `test_inventory.py::test_inventory_backward_compatible` | updated at S5.3 → GREEN |
| `settings-coverage.md` | **REQ-023 / AC-028** — **the new requirement this change adds** (D-5) | `tests/acceptance/settings_coverage/test_persistence.py::test_ac_028_persisted_override_warns` — one `WARNING` names the overridden key, the effective value stays the persisted one, an equal value names nothing | added at S4.1, updated at S5.3 → **GREEN** |
| `settings-coverage.md` | **REQ-011 / AC-015** (the persisted precedence D-5 sits on; unchanged) | `test_persistence.py::test_persisted_precedence` | untouched row, still GREEN. (§2 cites this as `settings.md` REQ-011; the persisted-precedence requirement is `settings-coverage.md` REQ-011 — `settings.md` REQ-011 is the hierarchy/`grouped_views()` requirement. Citation slip only; no ID was left uncovered.) |
| `file-management.md` | **REQ-015 / AC-029** (D-4 + the v3 wiring wording) | `tests/acceptance/filemanagement/test_filemanagement.py::test_ac_029_default_local_backend` (the composed service now reaches this live-read path) + `tests/integration/singleton_install/test_composition_root.py` | updated at S5.3 → GREEN |
| `settings-public-registry-setter.md` | **REQ-011 / AC-016** (wording: six → every call site) | `test_composition_root.py::test_ac_016_main_installs_through_setter` + `::test_installed_registry_serves_feature_registration` — both still pass with the nine-callable loop | existing row GREEN (this change re-ran both witnesses at S4.2 and S5.3; the row itself was not refreshed) |
| `user-roles-permissions.md` | **REQ-019** (model-block category → `security`) | `tests/acceptance/permissions/test_system_principal.py::test_system_set_settings_alias_sync` (witness unchanged) — the category fix itself is witnessed by the widened `test_category_group` | updated at S5.3 → GREEN |
| `session-management.md` | **REQ-019 / AC-039** (model block: category `security`, `group` added) | `test_ac_039_register_settings_defaults` — re-derived at S4.2 from the v3 model block | updated at S5.3 → GREEN |
| `structlog-logging.md` | **REQ-005 / AC-009** (S4.3 wording amendment; measured total 43) | `test_ac_009_statements_go_through_get_logger` + the per-feature witnesses `test_ac_009_settings_statements_go_through_get_logger` / `test_ac_009_eventbus_statements_go_through_get_logger` | updated at S5.3 → GREEN |

**Statement.** Every REQ/AC/NFR this change touches has **at least one GREEN test**, and the new requirement **REQ-023 / AC-028 is covered** by `test_ac_028_persisted_override_warns` (acceptance tier, GREEN in the full suite and in the reproduction run). **Touched IDs with no GREEN test: none.** Requirement coverage is 100% over the touched set; the 93.85% branch coverage of §13.2 is the secondary signal, not the evidence.

### 13.5 Defect closure (D-1…D-6)

| Defect | What closed it | Proving test (GREEN) |
|---|---|---|
| **D-1** — the composition root registered 18 of 34 keys | `src/main.py`: the six named one-liners replaced by `_SETTINGS_REGISTRATIONS`, an ordered tuple of the **nine** features' `register_settings` callables, plus the loop calling each against `_shared_settings_registry()` (commit `b88684d`) | `test_main_wires_all_features` — `PROBED 34 / REGISTERED 34 / MISSING []` |
| **D-2** — the AC-003 witness and the contract inventory guard were themselves incomplete | The witness's expected set is now **derived** from every `feature_settings` module; the contract guard's `INVENTORY` widened to the 34-key inventory and `_registry_with_all_features` registers all nine features (S3.1, `46d679a`) | `test_main_wires_all_features` + `test_key_prefix` / `test_category_group` / `test_inventory_matches` / `test_no_secret_settings` / `test_inventory_backward_compatible` |
| **D-3** — four keys carried a feature name as their category; three carried no `group` | `permissions/feature_settings.py:31` and `sessionmanagement/feature_settings.py:41,48,55`: `category="security"`, and `group="sessionmanagement"` added to the three (the specs' model blocks amended in the same PR, Q-26) | `test_category_group` (all 34 rows) + `test_ac_039_register_settings_defaults` |
| **D-4** — the composed `FileService` pinned the storage root to a literal | `src/main.py`: the `LocalDiskStorageBackend("./data/files")` argument and its now-unused import dropped, so REQ-015's live read runs | `test_ac_029_default_local_backend` (the AC-029 contract, already GREEN at the service level, now reached by the composed service) + `test_composition_root.py` |
| **D-5** — a persisted value silently overrode a new default | `src/backend/settings/registry.py`: `register()` emits **one `WARNING`** when the loaded persisted value differs from the definition default, naming the **key only** (never the value — Q-28 + the amended NFR-002) | `test_ac_028_persisted_override_warns` (RED at §5.3 → GREEN) |
| **D-6** — NFR-002 conflicted with the registered `mail.smtp_password` | Resolved by **spec wording**, not code: LQ-01 (a) — NFR-002 amended (Q-27 wording) and the guard rewritten as a set equality against the documented exemption list | `test_no_secret_settings` — GREEN by design (§5.1), full name-check force on the other 33 keys |

### 13.6 Spec amendments carried by this PR (six)

**No separate Spec Amendment PR** — the user's explicit override of the Spec Amendment Workflow at **Q-02** and **Q-27** (recorded in §4 and in `docs/questions/startup-settings-registration-gaps.md`); the decision was also recorded on `main` at `093f2ff` for LQ-01. Each file carries its `## Changelog` line.

| Spec | Version | IDs amended |
|---|---|---|
| `settings-coverage.md` | **v3** | REQ-001, REQ-017 (nine-feature enumeration), REQ-019 (guard checks the complete inventory), §3.5 inventory → 34 keys, **new REQ-023 / AC-028**, NFR-002 (credential wording + the named `mail.smtp_password` exemption), §10 test-strategy and §11 matrix rows |
| `settings-public-registry-setter.md` | **v4** | REQ-011, AC-016 — "the six `register_*_settings(...)` calls" → "every feature `register_settings` call site"; the hard-coded count and the drifted line references removed (Q-13(b), Q-14) |
| `user-roles-permissions.md` | **v3** | REQ-019 model block: `category="permissions"` → `category="security"` (Q-26) |
| `session-management.md` | **v3** | REQ-019 model block ×3: `category="sessionmanagement"` → `category="security"` **and `group="sessionmanagement"` added** (Q-26, §5.2) |
| `file-management.md` | **v3** | REQ-015, AC-029 — the composition root passes **no** `StorageBackend`; its storage root is the live `filemanagement.storage_root`, never a hard-coded path (Q-24, Q-26) |
| `structlog-logging.md` | **v3** | AC-009 — the invariant replaces the hard-coded "42 statements", the count kept as the witness's **measured** figure (43 = 19 + 11 + 11 + 2); REQ-005's per-file count for `registry.py` refreshed 18 → 19. No ID changed (S4.3, §6.1.1) |

### 13.7 Residual / inherited items (not this change's)

- **`test_ac_021` line endings** — passes in this worktree only because the regenerated `STRUCTURE.md` is LF; the root cause (`core.autocrlf=true` with no `.gitattributes`) is untouched and belongs to the separate `gitattributes-line-endings` TODO (§7, §10).
- **The two Hypothesis deadline flakes** — `test_inv_002_password_round_trip` and `test_inv_001_token_hash_uniqueness`; load-dependent `DeadlineExceeded` (§7), one recurred in the §13.2 coverage run 1; explicitly out of scope (§10).
- **`test_nfr_001_performance_budgets` (search)** — a documented load-sensitive wall-clock contract; failed once under coverage instrumentation (§13.2), passes standalone and did not recur. Not this change's code path.
- **`ty` diagnostics** — 160 vs 159 on `main`; the +1 is an instance of an `invalid-type-form` class `ty` already emits 7× for the same annotation shape. Informational by CI configuration; **mypy is the gate** and passes (§7.2).
- **`complexipy`** — cleared by the branch refresh (§7.2 → §7.3); the four `scripts/` functions were fixed on `main` by PR #82, not here.
- **Repo-root `settings/` pollution from `import main`** — mitigated for this change's witness only (Q-22, §5.2); the general isolation mechanism already exists from `settings-test-isolation` (§10).
- **`register_feature` never sets `group`** — the three `sessionmanagement.*` definitions now pass it explicitly; deriving it inside `register_feature` would change behaviour for every feature and is out of scope (§6.1.1).

### 13.8 What Phase 6 must still do

1. **S6.1–S6.3 review** against the ISSUE normative basis (triage record + affected spec IDs): traceability (§7.4, §13.4), feature boundaries and architecture rules, **no acceptance test weakened or deleted** — the one assertion change (`tests/acceptance/sessionmanagement/test_settings.py:58`) is the spec-amendment narrowing recorded in §3/§9, and the NFR-002 guard's value-clause correction is recorded in §5.2; no behaviour beyond the affected spec IDs (§13.4).
2. **S6.4 pre-merge gate: re-confirm the full suite and coverage on the final tree.** §7.1 (891 passed / 1 skipped / 0 failed) and §13.2 (93.85% ≥ 92, twice) are the current measurements; the review report must carry the pre-merge confirmation.
3. **`CHANGELOG.md` entry under `## [Unreleased]`** — owed by every change type (skill `verify` MUST, AGENTS.md Phase 6 item 10); it does **not** exist yet, and §12 plans `Fixed` for D-1…D-5 plus `Changed` for the category move.
4. **Version bump: `bump-my-version bump patch`** — ISSUE → patch, `1.2.0 → 1.2.1`, clean tree, `tag = false`; the `## [Unreleased]` entries move to `## [1.2.1] - <date>` in the bump commit (§12).
5. **Open the PR** to `main` and present it for human merge, then STOP — the agent never merges (human governance). The branch already carries `main` (`9b19d7d`), so the `complexipy` gate is green on the branch itself.
6. **Post-merge cleanup (S7.1)** — verify the merge on `main`, remove the worktree, delete the local and remote change branches, move the two planning records to their archive folders.

## 14. Review — normative basis (S6.1) — 2026-10-11, HEAD `571b84e`, read-only

**Bounded inputs used (nothing else):** this record (§2 affected IDs, §3 D-1…D-6, §4 the six amendments, §5.1 LQ-01, §5.2 the S3.1 corrections, §6/§6.1/§6.1.1 fix scope and GREEN, §13 the verification report); the six amended specs exactly as this PR carries them (`settings-coverage.md` v3, `settings-public-registry-setter.md` v4, `user-roles-permissions.md` v3, `session-management.md` v3, `file-management.md` v3, `structlog-logging.md` v3); the **final state** of `src/main.py`, `src/backend/settings/registry.py`, `src/backend/{permissions,sessionmanagement,filemanagement,mail}/feature_settings.py`; and the five test modules this change wrote or re-derived. No `src/` or `tests/` file was modified by this step. The full suite was **not** re-run (§7.1: 891 passed / 1 skipped; §13.2: 93.85 % twice — S6.4 re-confirms on the final tree).

**Read-only checks actually run here:**

- **Spec ↔ code, measured, not asserted:** every `src/backend/*/feature_settings.py` registered into a scratch registry → **34 keys**, and the §3.5 inventory compared row-for-row against the code: **0 mismatches, 0 code-only keys, 0 spec-only keys** on key, kind, category and group. The category/group distribution is `application` × 22 / `security` × 12, and `group` equals the feature name for all 34 — REQ-018 holds over the whole live set, not only over the guard's rows.
- **Targeted witnesses (43 passed):** `tests/acceptance/settings_coverage/` + `tests/contract/settings_coverage/` + `tests/acceptance/sessionmanagement/test_settings.py` + `tests/acceptance/logging_coverage/` + `tests/integration/singleton_install/test_composition_root.py` + `tests/acceptance/filemanagement/test_filemanagement.py::test_ac_029_default_local_backend`.
- **`uv run python scripts/check_traceability.py`** → PASS (891 rows, 136 spec IDs, 876 test functions) — the new REQ-023 / AC-028 rows are referentially sound.
- **`uv run ruff check <the 11 touched paths>`** → all checks passed; `ruff format --check` on the two rewritten modules → already formatted.
- **Test-change audit:** `git diff main...HEAD -- tests/` removes **no** test function (`test_main_wires_all_features` is re-added with a strengthened body), adds no `skip`/`xfail`/weakening marker, and its 8 removed `assert` lines were each read: two are the documented re-derivations (§3/§9 the `category` assertion, §5.2 the NFR-002 value clause), the rest were replaced by strictly stronger checks (the derived 34-key wiring report, the set-equality NFR-002 name check, the `_same_default` helper).
- **Boundaries:** the new `src/main.py` imports are package-root only (`from backend.<feature> import register_settings as …`); no cross-feature internal import, no `shared/` change, no new dependency, no new ADR-worthy pattern — the loop is data over the existing REQ-011 seam.

### 14.1 Findings

| # | Finding | Severity | Resolution | Status |
|---|---|---|---|---|
| **1** | **D-4 is fixed but not guarded.** No test anywhere asserts that `src/main.py` passes no `StorageBackend`: `grep -rln "StorageBackend" tests/` finds only filemanagement fixtures/helpers, and the amended AC-029 clause "which is what the composition root uses, since `src/main.py` passes no `StorageBackend`" is therefore un-witnessed. `test_ac_029_default_local_backend` proves the *service-level* default path, not the composition root. §13.5's D-4 row cites "`+ test_composition_root.py`" — that witness is the settings-install witness and says nothing about the backend, so the citation overstates the evidence. Re-adding `LocalDiskStorageBackend("./data/files")` to `main.py` would turn the key inert again with a fully GREEN suite — the exact D-2 class this change made a requirement (REQ-019: "a guard that covers only part of it does not satisfy this requirement"). | **minor** | S6.1 may not edit tests. Two adequate fixes, S6.3's choice: (a) extend the existing AST scan in `tests/integration/singleton_install/test_composition_root.py` (it already parses `src/main.py` for `_private_slot_imports()` and consumer sites) with "the `FileService(...)` call passes no `StorageBackend`", mirroring the pattern already in that file; or (b) record a follow-up TODO and state the gap in the review report. §13.5's D-4 evidence row must be corrected either way. | **OPEN — for S6.3** |
| **2** | **The NFR-002 guard is inventory-scoped, not registry-scoped.** `test_no_secret_settings` derives the credential-named set from the test's own `INVENTORY` (`tests/contract/settings_coverage/test_inventory.py:190`), not from the registry it just built. A tenth feature registering e.g. `foo.api_secret` and no matching `INVENTORY` row would pass NFR-002 **and** `test_inventory_matches` **and** `test_main_wires_all_features` (that witness compares the derived expected set against main's registry, so both sides grow together). The exemption mechanism itself is right — set equality against `NFR_002_CREDENTIAL_EXEMPTIONS = {"mail.smtp_password"}` is stronger than the old three-name check, and the key-only WARNING invariant (D-5/REQ-023, `src/backend/settings/registry.py:123-126`) holds. | **minor** | One-line hardening: build `named` from the registry (`{v.key for v in reg.views()}`) instead of from `INVENTORY`, so the guard sees what the features actually register. S6.1 may not edit tests. | **OPEN — for S6.3** |
| **3** | **The AC-016 witness still spies six of the nine registration call sites.** `_INSTRUMENT` patches six feature modules and asserts `len(registered) == 6` over six `_FEATURE_KEYS`, while the amended REQ-011 / AC-016 now say "**every** feature `register_settings` call site". Not a contradiction — the amendment deliberately fixed no count — but the witness alone would not notice three call sites reading a second registry. | **minor** | Accepted: the two halves of the amended wording are covered **in combination** — the "no consumer site passes the local handle" half by the AST scan of the whole file (`_consumer_sites_passing_the_handle()` matches the loop's `register_settings(...)` call by name pattern, and it returns `[]`), and the "all nine register into the installed instance" half by `test_main_wires_all_features` (`PROBED 34 / REGISTERED 34 / MISSING []` against the registry `import main` installed). Widening the spy tuple to the nine is a test change out of scope for S6.1; noted as a follow-up. | resolved (accepted, rationale recorded) |
| **4** | **AC-028's "exactly one `WARNING`" is witnessed as "at least one".** `test_ac_028_persisted_override_warns` asserts some `WARNING` names the key, plus the negative case (a persisted value equal to the default names nothing). The "exactly one" clause is not counted. | **minor** | Accepted as adequate: the code emits exactly one (`src/backend/settings/registry.py:122-126` is a single `_logger.warning` on the override branch, and a second `register()` of the same key raises `SettingsRegistrationError` at `:117-118` before the override check, so a per-key duplicate record is unreachable). Counting the records is a follow-up tightening, not a gate gap. | resolved (accepted, rationale recorded) |
| **5** | **AC-009's count is still a hard-coded constant in the witness.** The amended criterion says the total is "that witness's measured total … not a normative constant", but `_AC_009_STATEMENTS` / `_AC_009_TOTAL_STATEMENTS` pin 19/11/11/2 and 43, and `_statement_violations` fails on `len(statements) != expected`. Adding a one-off statement still means editing test constants. | **note** | Accepted, and the split is the point of the amendment: the **spec** no longer carries a normative constant (that is what went stale at S4.3, §6.1.1), while the **witness** keeps the count as an explicit drift guard that also catches a statement being deleted or a backend import returning. S6.3 must judge any future count edit as a re-derivation (the pattern of §5.2), never as a weakening. | resolved (accepted, rationale recorded) |
| **6** | **`_same_default` relaxes list order for every `LIST` default**, not only the one that needs it. The justification (a `frozenset`-derived default has no stable order) is true for `permissions.system_principal`; it also stops checking order for `usermanagement.roles` and `filemanagement.allowed_types`. | **note** | Accepted: no requirement fixes list order — REQ-019 fixes key/kind/default/parameters/category/group and §3.5 states the values, not their order — and the guard still compares the full value set. Narrowing the helper to the unordered key is optional polish. | resolved (accepted, rationale recorded) |
| **7** | **Two spec-wording drifts, both wording-only.** (a) `user-roles-permissions.md` v3 says "`group="permissions"` [is] unchanged", but the §3 model block never stated a `group` — the group is normative only through `settings-coverage.md` REQ-018 and §3.5, which the code and the guard match. (b) `session-management.md` §3 still shows three `registry.register(SettingDefinition(...))` calls while the code registers through `registry.register_feature("sessionmanagement", [...])` (pre-existing drift; this amendment touched only `category`/`group`). | **note** | No behavioural impact — measured: the code's `permissions.system_principal` and the three `sessionmanagement.*` rows match §3.5 exactly on category and group. Both are wording-only and may be corrected inside this PR at S6.3's discretion (docs-only, no gate effect); (b) is inherited and already implied by §13.7's "`register_feature` never sets `group`" row. | resolved (no action required; recorded) |
| **8** | **Operator-visible consequence of the D-1 fix is not spelled out in §12's changelog plan.** With `filemanagement.*`, `mail.*` and `sessionmanagement.*` registered for the first time, a value already persisted in an operator's `settings/values.yaml` now wins over the default (REQ-011), and `filemanagement.storage_root` now actually moves the storage directory (D-1 + D-4 together). This is the specified behaviour, and REQ-023's `WARNING` is exactly the diagnostic for it. | **note** | Verified against the code; the `CHANGELOG.md` entry owed at S6.4 (§13.8 item 3) must state it — one `Fixed` line for the registration gap and one line making the live-read/override consequence visible, so the entry is not read as a no-op. | resolved (carried to S6.4 changelog) |
| **9** | **The loop leaves a module global in `main`.** `for register_settings in _SETTINGS_REGISTRATIONS:` keeps `main.register_settings` bound to the last registration function after import. | **note** | Accepted and deliberate: the name is load-bearing — `_consumer_sites_passing_the_handle()` classifies consumer sites by the name pattern `register_*_settings`, so renaming the loop variable to `_register_settings` would silently drop the loop call out of the AC-016 scan. Nothing reads the leftover binding. Already recorded at §6.1.1. | resolved (accepted, rationale recorded) |

### 14.2 Normative-basis verdict

- **Every defect is closed in the final state:** D-1 (nine-feature tuple + loop, `src/main.py:207-219`, measured 34/34), D-2 (guard and witness derived from source, §14 checks above), D-3 (measured: 0 category/group mismatches over all 34 keys), D-4 (no `StorageBackend` argument and no import in `src/main.py`, `:236-243`) — **but see finding 1: the fix is unguarded**, D-5 (one key-only `WARNING`, `registry.py:122-126`, witnessed by AC-028), D-6 (NFR-002 rewritten at LQ-01 (a) and implemented as set equality against the documented exemption).
- **No behaviour beyond the affected spec IDs.** The only new behaviour is the REQ-023 `WARNING`, and it is represented by the REQ-023 / AC-028 rows added in this same PR; the category/group move and the dropped backend argument are represented by the `session-management.md` v3, `user-roles-permissions.md` v3 and `file-management.md` v3 amendments. Nothing in the final state lacks a spec ID.
- **The six amendments match the code** row for row (§14 first bullet: 0 mismatches, 0 keys only in code, 0 keys only in spec), and the two amended count rules (`REQ-011` no count, `AC-009` measured total) are honoured.
- **No acceptance test was weakened or deleted to reach GREEN** — the two assertion changes are the re-derivations recorded at §3/§9 and §5.2, and the test-diff audit in §14 found no removed test, no marker, and no net loss of force.
- **Boundaries and architecture rules hold** (feature-owned `feature_settings` modules, package-root imports in the composition root, `shared/` untouched, no new dependency).

**Findings: 9 — 0 blockers, 4 minor (2 open for S6.3: findings 1 and 2), 5 notes.** **Blockers open: 0** — the change may proceed to S6.2/S6.3; the two open minors must be either fixed in this PR or recorded as follow-ups in the S6.3 review report, and §13.5's D-4 evidence row must be corrected either way.

---

## 15. Review — traceability + boundaries (S6.2) — 2026-10-11, HEAD `8a2939d`, read-only

**Inputs (bounded, per AGENTS.md Phase 6 / P-27):** the 11 matrix rows §7.4 lists this change updated plus the
Settings Coverage section note; this record's §2, §4, §7.4, §13.4, §14; the final code state (`src/main.py`,
`src/backend/settings/registry.py`, `src/backend/permissions/feature_settings.py`,
`src/backend/sessionmanagement/feature_settings.py`) and the five test modules this change wrote or re-derived; the
six amended specs. **No `src/` or `tests/` file was touched; the full suite was not re-run** (Phase 5 §7.1 owns it).
Targeted run of the cited witnesses (`tests/acceptance/settings_coverage`, `tests/contract/settings_coverage`,
`tests/acceptance/sessionmanagement/test_settings.py`, `tests/acceptance/logging_coverage`,
`tests/integration/singleton_install/test_composition_root.py`,
`tests/acceptance/filemanagement/test_filemanagement.py::test_ac_029_default_local_backend`,
`tests/acceptance/permissions/test_system_principal.py::test_system_set_settings_alias_sync`) →
**44 passed in 8.84s** (S6.1's 43 plus the permissions alias test added to this run).

### 15.1 Traceability — the 11 updated rows, row by row

Programmatic audit (parse `docs/verification/traceability.md`, resolve every cited function against the function
names collected from `tests/` by the same rule `scripts/check_traceability.py` uses):

| # | Matrix line | Row | Cited witness | Exists | Cell carries change name + date + measured run | ID defined in the section's spec |
|---|---|---|---|---|---|---|
| 1 | 374 | `settings-coverage.md` REQ-002 / AC-003 | `test_main_wires_all_features` | yes | yes — name + 2026-10-11 + `891 passed, 1 skipped in 273.91s at 736a24c` + S5.1 | yes |
| 2 | 393 | REQ-017 / AC-022 | `test_key_prefix` | yes | yes (same) | yes |
| 3 | 394 | REQ-018 / AC-023 | `test_category_group` | yes | yes (same) | yes |
| 4 | 395 | REQ-019 / AC-024 | `test_inventory_matches` | yes | yes (same) | yes |
| 5 | 399 | REQ-023 / AC-028 | `test_ac_028_persisted_override_warns` | yes | yes (same) | yes — new ID of this change's `settings-coverage.md` v3 |
| 6 | 418 | NFR-002 / — | `test_no_secret_settings` | yes | yes (same) | yes |
| 7 | 419 | NFR-003 / — | `test_inventory_backward_compatible` | yes | yes (same) | yes |
| 8 | 516 | `file-management.md` REQ-015 / AC-029 | `test_ac_029_default_local_backend` | yes | yes (same) | yes |
| 9 | 625 | `session-management.md` REQ-019 / AC-039 | `test_ac_039_register_settings_defaults` | yes | yes (same) | yes |
| 10 | 696 | `user-roles-permissions.md` REQ-019 / AC-023 | `test_system_set_settings_alias_sync` | yes | yes (same) | yes |
| 11 | 911 | `structlog-logging.md` REQ-005 / AC-009 | `test_ac_009_settings_statements_go_through_get_logger` | yes | yes (same) | yes |

**11 / 11 pass all three checks.** Every REQ this change touched has at least one GREEN witness, and every witness
named in an updated row is a real function under `tests/`.

**Tool gate.** `uv run python scripts/check_traceability.py` → `Traceability: PASS (891 matrix rows, 136 spec IDs,
876 test functions)`, **exit 0** — the same figures as the S4.1/S4.2 baseline in this worktree, i.e. this change
added no matrix row beyond REQ-023/AC-028 and no test function beyond `test_ac_028_persisted_override_warns`. The
script enforces four checks only — spec ID with no row, row citing an undefined ID, row citing a missing test,
undeclared Status token — and its own header says it "never asserts that a row's status is current". Orphaned tests
are therefore **not** tool-enforced; §15.2 does that check by hand.

### 15.2 Reverse mapping — every test this change touched traces to a normative ID

Diff-hunk → enclosing-function mapping over `git diff main HEAD -- tests/` (5 files, +214 / −50):

| Test function | What the change did to it | Normative ID it asserts | ID in a spec | Matrix row |
|---|---|---|---|---|
| `test_main_wires_all_features` | body re-derived: expected key set derived from every `backend.<feature>.feature_settings` module; the original four-key check kept verbatim | AC-003 / REQ-002 (`settings-coverage.md`) | yes | line 374 |
| `test_ac_028_persisted_override_warns` | **new function** | AC-028 / REQ-023 | yes | line 399 |
| `test_no_secret_settings` | body re-derived: set equality against the documented exemption; connection-string check narrowed to non-empty strings (§5.2) | NFR-002 | yes | line 418 |
| `test_inventory_matches` | body re-derived: `_same_default` for order-unstable `LIST` defaults | AC-024 / REQ-019 | yes | line 395 |
| `test_key_prefix`, `test_category_group`, `test_inventory_backward_compatible` | bodies untouched; the module-level `INVENTORY` (14 → 34 keys) and `_registry_with_all_features()` (4 → 9 features) they iterate were widened | AC-022 / REQ-017, AC-023 / REQ-018, NFR-003 | yes | lines 393, 394, 419 |
| `test_ac_039_register_settings_defaults` | re-derived from the amended `session-management.md` model block: `category == "security"`, `group == "sessionmanagement"` | AC-039 / REQ-019 | yes | line 625 |
| `test_ac_009_settings_statements_go_through_get_logger`, `test_ac_009_statements_go_through_get_logger`, `test_ac_009_eventbus_statements_go_through_get_logger` | constants and docstrings only; the guard mechanism (`_AC_009_STATEMENTS` table, `sum == _AC_009_TOTAL_STATEMENTS`) is byte-for-byte unchanged | AC-009 / REQ-005 (`structlog-logging.md`) | yes | line 911 |
| helpers `_no_repo_root_settings_dir` (autouse fixture), `_same_default`, `_registry_with_all_features` | test scaffolding, asserts nothing on its own | n/a | n/a | n/a |

**Orphans: 0.** Every test function this change added or modified names its normative ID in its docstring or first
assertion, and each maps to a spec-defined ID and a matrix row. The spec → test direction also holds: the amended
`settings-coverage.md` §10 test-strategy tables cite the same functions (`:280`, `:299-301`, `:305`, `:324-325`), and
`file-management.md` `:542` / `:582` cite theirs. No test was deleted, marked or weakened — the two assertion changes
are the recorded re-derivations §5.2 and §6.1.1, and S6.1 §14 audited the test diff for lost force.

### 15.3 Untouched rows were not refreshed (decision Q-129, convention B)

`git diff main HEAD -- docs/verification/traceability.md` = **10 removed rows, 11 added rows, 11 added note lines, 0
other changed lines**. The 11 added rows are exactly the 11 of §15.1 (REQ-023/AC-028 is the one with no removed
counterpart — it is new). Measured in the Settings Coverage section (`:366-436`, 51 rows): **38 rows still carry the
search change's dated record** (`7bbc05a`, base `e8dd2bc`) untouched and **7** carry this change's; the other four
updated rows sit in the file-management, session-management, user-roles-permissions and structlog-logging sections.
No row this change did not re-validate was refreshed.

The section note was **appended, not rewritten**: the pre-existing note at `:372` is unchanged context in the diff and
this change's dated note sits at `:424`, naming exactly these 11 rows (7 in this matrix + 4 elsewhere).

### 15.4 Feature boundaries and architecture rules (final code state, measured)

| Rule | Measurement | Verdict |
|---|---|---|
| Change lives in the correct feature package | `src/` diff = 4 files, +40 / −25: `main.py` (composition root), `settings/registry.py` (REQ-023 warning), `permissions/feature_settings.py`, `sessionmanagement/feature_settings.py`. Each edit sits in the package that owns the setting it fixes. | pass |
| No cross-feature import of a private module | `grep -rnE '^from backend\.[a-z_]+\.[a-z_.]*\.[_]\|^from backend\.[a-z_]+\._' src/` → 7 hits, **all inside `backend/logging/`** (`__init__.py`, `_pipeline.py`, `_settings.py`, `feature_settings.py`) — owner-internal and pre-existing. Cross-feature: **0**. | pass |
| Composition root imports features' public roots only | `src/main.py` import diff vs `main`: `+ from collections.abc import Callable` (stdlib) and three new package-root imports (`backend.filemanagement`, `backend.mail`, `backend.sessionmanagement`), each `… import register_settings as register_<feature>_settings`. `LocalDiskStorageBackend` no longer appears in `src/main.py` except in the explanatory comment at `:236-237`. The pre-existing `backend.<feature>.feature_actions` imports are public modules (the documented `register_actions` seam) and are unchanged. | pass |
| `shared/` deliberately small, gained nothing feature-owned | `git diff main HEAD -- src/backend/shared/` → **empty**. | pass |
| No premature layers | `find src -type d -name model -o -type d -name services -o -type d -name models` → **empty**; feature packages flat; the only nested dir under `src/` is `backend/filemanagement/assets/`. | pass |
| New log statement uses the feature's own logger at a semantic level | `src/backend/settings/registry.py:43` `_logger = get_logger("settings")`; `:122-126` one `_logger.warning("persisted value overrides setting default: key=…", key=…)` on the override branch — `WARNING` (recoverable, operator-visible), payload is the **key only**, never the persisted value or the default (amended NFR-002, Q-28). | pass |
| Registrations precede the services that read them | `src/main.py`: `set_settings_registry(…)` `:165` → `_SETTINGS_REGISTRATIONS` `:207-217` → `for register_settings in _SETTINGS_REGISTRATIONS: register_settings(_shared_settings_registry())` `:218-219` → services `_user_manager` `:223`, `_auth_service` `:227`, `_file_service` `:239`, `_mail_service` `:244`, `_session_service` `:245`, `_search_service` `:255`. The six pre-existing registrations keep their exact relative order, the three new ones are appended before the services that read their keys, and the pre-existing `PermissionService` construction at `:180` (before the registrations) is unchanged from `main`. | pass |
| No new dependency, no new pattern needing an ADR | `pyproject.toml` is not in the branch diff; the ruff `TID251` banned-api table is unchanged; `_SETTINGS_REGISTRATIONS` is data over the existing REQ-011 `register_settings` seam. | pass |
| Loop-variable name is load-bearing | `for register_settings in …` keeps `main.register_settings` bound; `tests/integration/singleton_install/test_composition_root.py::_consumer_sites_passing_the_handle()` classifies consumer sites by the `register_*_settings` name pattern, so the name must stay (S6.1 finding 9). | deliberate |

### 15.5 Findings

| # | Finding | Severity | Status |
|---|---|---|---|
| **F-1** | **D-4's fix is unguarded — restated with the exact missing evidence (S6.1 finding 1).** Spec IDs that would go un-witnessed if `LocalDiskStorageBackend("./data/files")` returned to `src/main.py`: **`file-management.md` REQ-015** (`docs/specs/file-management.md:377`, v3 clause "the composition root passes **no** backend, so the storage root it writes to is the live `filemanagement.storage_root` value and never a hard-coded path") and **AC-029** (`:424`, v3 "**which is what the composition root uses**, since `src/main.py` passes no `StorageBackend`"). Why the cited witnesses do not cover it: `test_ac_029_default_local_backend` (`tests/acceptance/filemanagement/test_filemanagement.py:331-342`) builds its **own** `FileService(…, backend=None, settings_registry=registry)` and never imports `main`; `tests/integration/singleton_install/test_composition_root.py` does AST-parse `src/main.py` but only for `_private_slot_imports()` (`:146`) and `_consumer_sites_passing_the_handle()` (`:158`), and its subprocess witness spies six `register_settings` modules against four `_FEATURE_KEYS` (`:38-45`) — nothing about `FileService`. Measured: the only five test modules that read or import `main` are `tests/acceptance/logging_coverage/test_setup_logger.py`, `tests/acceptance/permissions/test_composition_wiring.py`, `tests/acceptance/settings_coverage/test_wiring.py`, `tests/integration/singleton_install/test_composition_root.py`, `tests/unit/logging_coverage/test_edge_cases.py`; none asserts the backend argument, and `test_main_wires_all_features` checks only registered keys. Consequence: re-adding the literal leaves the whole suite GREEN (the registered default is the same `./data/files`) while REQ-015's live-read clause is inert again — the vacuous-guard class this change made a requirement (REQ-019). §13.5's D-4 evidence row cites `test_composition_root.py` and overstates the evidence; it must be corrected either way. | **minor — OPEN** | carried to S6.3: fix in this PR by extending the existing AST scan in `test_composition_root.py`, or record a follow-up TODO and state the gap in the review report |
| **F-2** | **The NFR-002 guard is inventory-scoped, not registry-scoped — restated with the exact missing evidence (S6.1 finding 2).** `tests/contract/settings_coverage/test_inventory.py:190` derives the credential-named set as `{key for key in INVENTORY if any(part in key.lower() for part in _SECRET_NAME_PARTS)}` and `:197` loops `for key in INVENTORY` — both over the test's own 34-key `INVENTORY` (`:28-96`), never over the registry it just built (`reg.views()`). Measured consequence for a tenth feature registering e.g. `foo.api_secret` with no matching `INVENTORY` row: `named` still equals `NFR_002_CREDENTIAL_EXEMPTIONS = {"mail.smtp_password"}` → NFR-002 passes; `test_key_prefix` / `test_category_group` / `test_inventory_matches` / `test_inventory_backward_compatible` iterate `INVENTORY` → pass; `test_main_wires_all_features` compares the set derived from the `feature_settings` modules against main's registry, so both sides grow together → passes. The amended NFR-002 ("no credential or token … outside the named exemption") is therefore enforced over the 34 listed keys, not over what the features actually register. The exemption mechanism itself is sound and stronger than the pre-change three-name check. | **minor — OPEN** | one-line test-only hardening (`named` built from `reg.views()`); S6.3 decides fix vs follow-up |
| **F-3** | **Orphan detection is manual in this repo.** `scripts/check_traceability.py` enforces referential integrity and the status vocabulary only; it never reports a test function with no spec reference. The orphan check in §15.2 is a review-side check — done, 0 orphans. | note | resolved (recorded, no action) |
| **F-4** | **`settings-coverage.md` §11's in-spec matrix rows still read `PENDING`** (39 `PENDING` cells in that file) while the live gate record — `docs/verification/traceability.md` — carries the dated GREEN cells. `PENDING` is a declared value so the tool passes; the spec's own §11 keeps the template default and is not the gate record. | note | resolved (no action, convention) |
| **F-5** | **The Settings Coverage section note was appended, not rewritten** (`:372` unchanged in the diff, this change's note at `:424`), and it names exactly the 11 rows §15.1 audits. The S6.2 input description ("the section note it rewrote") overstates the edit. | note | resolved (corrected here) |
| **F-6** | **`main.register_settings` stays bound as a module global after import** — deliberate: the AC-016 witness classifies consumer sites by that name pattern (S6.1 finding 9). Nothing reads the leftover binding. | note | resolved (accepted) |

### 15.6 Traceability + boundaries verdict

- **Traceability: clean.** 11/11 updated rows cite a witness that exists and carry this change's name, date and a
  measured run, and each references an ID defined in its section's spec; every REQ/AC/NFR this change touched has at
  least one GREEN witness; every test it added or re-derived maps to a normative ID (0 orphans); no untouched row was
  refreshed (38 rows in the Settings Coverage matrix still carry the search change's dated record).
- **Boundaries and architecture: clean.** All measured rules in §15.4 hold — correct package ownership, zero
  cross-feature private imports, package-root-only imports in the composition root, `shared/` untouched, no new
  layers, the new `WARNING` on the settings feature's own logger with a key-only payload, registrations before the
  services that read them, no new dependency.
- **Two minors stay open, and neither is a traceability or boundary defect:** F-1 (D-4 unguarded) and F-2 (NFR-002
  guard inventory-scoped) are both **witness-completeness** gaps — the specified behaviour is correct in the final
  state but under-guarded. S6.3 must resolve each as fix-in-PR or recorded follow-up, and §13.5's D-4 evidence row
  must be corrected either way.
- **Blockers: 0.** The change may proceed to S6.3.
