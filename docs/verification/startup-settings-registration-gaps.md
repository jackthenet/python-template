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
