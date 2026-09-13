# AI Questions

Persistent record of questions that arise during the workflow and need user input. This file is the **single source of truth** for unresolved decisions and user answers, so they are not lost between steps.

A step subagent records a question here when it returns `BLOCKED-USER`. The orchestrator presents the question to the user, records the answer here, marks it **incorporated**, and relaunches the same step with the answer. The workflow never proceeds past a `BLOCKED-USER` step until the user has answered.

## When questions are created

- **MAY:** any atomic step, when it meets an ambiguity, a missing requirement, or a decision that requires user input.
- **MUST:** the **Interrogate** step (**S1.1**, Phase 1) — it MUST create a question for every ambiguity, missing requirement, edge case, and scope boundary it identifies. Any step that returns `BLOCKED-USER` MUST have its questions recorded here.

## Entry format

Each question is a section with the following fields:

```markdown
## Q-<n> — <short title>
- **Step:** <step ID + phase> (e.g., S1.1 Interrogate — Phase 1)
- **Change:** <change name + type>
- **Why needed:** <why this question is needed — the ambiguity / missing requirement / decision>
- **Context:** <the available context at the time — what the step had learned>
- **Question:** <the question for the user>
- **Answer:** <the user's answer> (or **PENDING**)
- **Date:** <YYYY-MM-DD>
- **Status:** PENDING | ANSWERED
- **Incorporated:** <yes/no — whether the answer has been folded into the workflow (spec, tests, implementation)>
```

## Questions

## Q-1 — Backend-only scope (no HTTP layer)
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** file-management, FEATURE
- **Why needed:** Every existing backend feature is an in-process Python service with no HTTP/REST layer, but the idea's "upload/download" bullets could imply an HTTP API. The answer determines the entire API surface (in-process service vs. web endpoints) and whether this stays a single FEATURE.
- **Context:** `src/backend/` contains authentication, eventbus, logging, mail, settings, usermanagement — all in-process services; `src/frontend/` does not exist yet; no web framework is in `pyproject.toml` dependencies.
- **Question:** Is file-management a backend-only in-process service (no HTTP/REST layer), consistent with all existing features? If an HTTP layer is needed, is it part of this change or a separate change?
- **Answer:** Yes — backend-only in-process service API, no HTTP/REST layer, consistent with all existing features.
- **Date:** 2026-09-13
- **Status:** ANSWERED
- **Incorporated:** no

## Q-2 — Avatar ↔ user-management integration boundary
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** file-management, FEATURE
- **Why needed:** "User avatars" attach to user-management users (`profile_picture_url` field, http/https only). It is unclear whether file-management itself updates the user record and cleans up on user deletion, or merely returns a URL/key for the caller to wire. This decides cross-feature dependencies and whether the change is truly a single FEATURE (not CROSS-CUTTING).
- **Context:** user-management spec: `User.profile_picture_url` (URL reference only; upload/storage explicitly out of scope for user-management); `update_user` can set `profile_picture_url`; `UserDeleted`/`UserDeactivated` events are published on deletion/deactivation.
- **Question:** When an avatar is uploaded/replaced/deleted, does file-management itself call `UserManager.update_user(user_id, UserUpdate(profile_picture_url=...))` (and subscribe to `UserDeleted` to clean up avatar files)? Or does it return the avatar URL/key and the caller (application wiring) handles user-management? Should file-management depend on the usermanagement feature at all?
- **Answer:** B — the caller updates it. file-management stays independent (no dependency on user-management): it stores the file and returns a URL string; the application code that called it sets the URL on the user record. No automatic avatar cleanup on user deletion (caller responsibility).
- **Date:** 2026-09-13
- **Status:** ANSWERED
- **Incorporated:** no

## Q-3 — Image processing in scope (Pillow, thumbnails)
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** file-management, FEATURE
- **Why needed:** Avatar features commonly require resizing/thumbnail generation (e.g., 64px/256px variants), which adds a Pillow dependency, image-decode validation, and multiple stored variants per upload. The idea does not mention it.
- **Context:** No Pillow in `pyproject.toml`; "user avatars" is the only image-specific bullet in the idea.
- **Question:** Is image processing in scope — e.g., generating resized avatar variants (thumbnails) with Pillow? If yes: which sizes, and are variants stored as separate files? If no: are avatars stored as raw uploads only?
- **Answer:** In scope: Pillow + thumbnails (image processing is in scope; exact variant sizes to be specified in the spec).
- **Date:** 2026-09-13
- **Status:** ANSWERED
- **Incorporated:** no

## Q-4 — Out-of-scope confirmations
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** file-management, FEATURE
- **Why needed:** The idea is a bullet list; common file-management capabilities (virus scanning, content deduplication, file versioning, retention/expiration, sharing/permissions, frontend UI) are not mentioned. Explicit boundaries are needed so the spec does not accidentally cover them.
- **Context:** No antivirus/dedup/versioning/retention capability exists in the repo; the idea lists only upload/download, user avatars, file metadata, storage abstraction, size/type validation.
- **Question:** Confirm out of scope for this change: virus scanning, content deduplication, file versioning, retention/expiration (auto-cleanup), sharing/permission grants, and any frontend UI. Is anything in that list actually in scope?
- **Answer:** All out of scope: virus scanning, content deduplication, file versioning, retention/expiration, sharing/permissions, and frontend UI.
- **Date:** 2026-09-13
- **Status:** ANSWERED
- **Incorporated:** no

## Q-5 — Storage backends
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** file-management, FEATURE
- **Why needed:** "Storage abstraction" implies a backend interface, but which backends are normative is unclear. Local disk only, or also S3-compatible (boto3)? S3 adds a major dependency and cloud semantics.
- **Context:** No boto3 in `pyproject.toml`; all existing features use local disk (SQLite files, YAML files) or in-memory storage.
- **Question:** Which storage backends must the spec cover: (a) local disk only (plus in-memory for tests), (b) local disk + S3-compatible (boto3) behind the same interface, or (c) other? Is the interface identical across backends (put/get/delete/exists/stat)?
- **Answer:** (a) Local disk only, plus in-memory for tests. S3 can be added later behind the same StorageBackend interface.
- **Date:** 2026-09-13
- **Status:** ANSWERED
- **Incorporated:** no

## Q-6 — Object store (flat keys) vs. path store (directories)
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** file-management, FEATURE
- **Why needed:** Determines the core data model: flat opaque keys (object store, no directories) vs. hierarchical paths with folders. Affects the API (key vs. path), validation (path traversal), and list semantics.
- **Context:** The idea lists "storage abstraction" and "file metadata" but no folders/directories.
- **Question:** Is the store flat (opaque keys, object-store style) or hierarchical (paths with directories/folders)? Are "folders" part of the public API?
- **Answer:** Flat opaque keys (object-store style). "Folders" are NOT part of the public API; namespaces (e.g., avatars) are a logical concept, not real directories.
- **Date:** 2026-09-13
- **Status:** ANSWERED
- **Incorporated:** no

## Q-7 — Default storage root + in-memory test backend
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** file-management, FEATURE
- **Why needed:** The local backend needs a default root directory, and the backend must be swappable for tests (like `MemoryValueRepository`). The default location affects deployment and test isolation.
- **Context:** Existing features: SQLite DB paths are constructor args; settings values persist under a `settings` directory; tests use temp directories.
- **Question:** What is the default storage root directory for the local backend (e.g., `./data/files`)? Should an in-memory storage backend be part of the public API for tests/DI?
- **Answer:** Default root `./data/files` (configurable). Yes — a public in-memory storage backend for tests/DI.
- **Date:** 2026-09-13
- **Status:** ANSWERED
- **Incorporated:** no

## Q-8 — Upload input shape
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** file-management, FEATURE
- **Why needed:** In-process upload could take an existing file path, raw bytes, or a file-like stream. Each has different validation (size pre-check via `stat` vs. `len` vs. streaming) and a different API surface.
- **Context:** The idea says only "upload/download"; no existing upload capability in the repo.
- **Question:** What input shape(s) should `upload` accept: existing file path, raw bytes, file-like stream (or all of them)? Should the read be streamed (chunked) or whole-file?
- **Answer:** All three: existing file path, raw bytes, and file-like stream.
- **Date:** 2026-09-13
- **Status:** ANSWERED
- **Incorporated:** no

## Q-9 — Size limits
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** file-management, FEATURE
- **Why needed:** "Size validation" is in the idea, but the values, scope (general vs. avatar), and enforcement point (pre-write via `stat` vs. mid-stream) are unspecified. Limits should likely be configurable via the settings registry.
- **Context:** The settings registry supports NUMBER/SLIDER kinds with live reads (mail-service pattern); no existing size limits in the repo.
- **Question:** What are the max file sizes — for general uploads and for avatars (defaults, e.g., 100 MB / 5 MB)? Should limits be configurable via the settings registry (read live)? Are zero-byte files rejected (minimum size)?
- **Answer:** Defaults: 10 MB general uploads, 2 MB avatars; configurable via the settings registry (read live); zero-byte files rejected.
- **Date:** 2026-09-13
- **Status:** ANSWERED
- **Incorporated:** no

## Q-10 — Concurrent uploads to the same key
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** file-management, FEATURE
- **Why needed:** Two threads uploading the same key concurrently could race (partial overwrite). The spec must state the behavior: last-write-wins, per-key locking (one fails), or undefined.
- **Context:** Existing features are thread-safe (settings registry, event bus, SQLite repositories); no precedent for same-key write races.
- **Question:** What should happen when two uploads target the same key concurrently: last-write-wins (atomic replacement), per-key locking (one fails), or undefined?
- **Answer:** Last-write-wins (atomic replacement); exactly one winner, no error.
- **Date:** 2026-09-13
- **Status:** ANSWERED
- **Incorporated:** no

## Q-11 — Atomicity / no partial state
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** file-management, FEATURE
- **Why needed:** A failed or interrupted upload (validation failure mid-write, disk full, backend error) must not leave partial files or orphaned metadata. The spec needs a hard invariant: temp file + atomic rename, and rollback between the metadata record and the storage write.
- **Context:** Settings YAML repository uses atomic writes; user-management NFR-004: "a failed operation leaves no partial state".
- **Question:** Confirm: a failed/interrupted upload leaves no partial state (temp file + atomic rename; if the storage write fails, the metadata record is rolled back, and vice versa). Is this a hard invariant?
- **Answer:** Yes — hard invariant (MUST hold for every operation).
- **Date:** 2026-09-13
- **Status:** ANSWERED
- **Incorporated:** no

## Q-12 — Type detection method
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** file-management, FEATURE
- **Why needed:** "Type validation" needs a detection method: declared content-type, file extension, magic-byte sniffing (python-magic dependency), or image decode. Conflicting signals (`.png` extension but JPEG content) need a precedence rule.
- **Context:** No python-magic/Pillow in `pyproject.toml`; user-management validates `profile_picture_url` by scheme only.
- **Question:** How should file type be determined: declared MIME type, file extension, magic-byte sniffing (adds a python-magic dependency), or image decode? When signals conflict, which wins (e.g., `.png` name but JPEG content)? Should a mismatch be rejected?
- **Answer:** Magic-byte sniffing via python-magic (content-based detection; declared type is not trusted as the source of truth). Conflicting signals are rejected.
- **Date:** 2026-09-13
- **Status:** ANSWERED
- **Incorporated:** no

## Q-13 — Allowed-type policy
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** file-management, FEATURE
- **Why needed:** "Size/type validation" implies an allowed-type policy, but the unit (MIME vs. extension) and scope (global whitelist vs. per-kind, e.g., avatars: images only) are unspecified.
- **Context:** No existing type whitelist in the repo.
- **Question:** What is the allowed-type policy: a global allowed-types list, per-kind lists (e.g., avatars restricted to image/png, image/jpeg, image/webp), or both? Is the policy unit MIME type or extension? Should it be configurable via the settings registry?
- **Answer:** Per-namespace allowed types (avatars: images only) + a global default; unit = detected MIME type; configurable via the settings registry.
- **Date:** 2026-09-13
- **Status:** ANSWERED
- **Incorporated:** no

## Q-14 — Metadata fields
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** file-management, FEATURE
- **Why needed:** "File metadata" is in the idea, but the normative field set is unspecified. The fields (id, key, original filename, declared + detected MIME, size, content hash, namespace, uploader reference, created/updated timestamps, tags) and whether SHA-256 content hashing is required (integrity, future dedup) must be pinned.
- **Context:** user-management's `User` table shows the repo pattern (SQLModel, UUID id, UTC timestamps).
- **Question:** Which metadata fields are normative? Proposed: id, key, original filename, declared MIME, detected MIME, size (bytes), SHA-256 content hash, namespace, uploader reference, created/updated timestamps. Is content hashing (SHA-256) required? Any additional fields (tags, owner)?
- **Answer:** The proposed full set, with SHA-256 content hashing required.
- **Date:** 2026-09-13
- **Status:** ANSWERED
- **Incorporated:** no

## Q-15 — Metadata persistence
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** file-management, FEATURE
- **Why needed:** Metadata must be durable (survive restarts) and swappable (repository pattern), consistent with user-management (SQLite/SQLModel behind an ABC). In-memory (like the settings registry) is an alternative with different durability semantics.
- **Context:** user-management: `UserRepository` ABC + `SqliteUserRepository`; settings: in-memory registry with a YAML template repository.
- **Question:** Should file metadata be persisted in SQLite/SQLModel behind a repository ABC (like user-management), or in-memory (like the settings registry)?
- **Answer:** SQLite/SQLModel behind a repository ABC (like user-management).
- **Date:** 2026-09-13
- **Status:** ANSWERED
- **Incorporated:** no

## Q-16 — List/query API
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** file-management, FEATURE
- **Why needed:** "File metadata" implies queryability, but the API shape is unspecified: list by namespace/prefix, lookup by key, search by original filename, pagination.
- **Context:** user-management has `list_users(include_inactive)`; no pagination anywhere in the repo.
- **Question:** What list/query API is needed: list by namespace/prefix, lookup by key, search by original filename? Is pagination needed?
- **Answer:** Lookup by key + list by namespace (prefix), with limit/offset pagination.
- **Date:** 2026-09-13
- **Status:** ANSWERED
- **Incorporated:** no

## Q-17 — Avatar lifecycle semantics
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** file-management, FEATURE
- **Why needed:** "User avatars" needs precise upload/replace/delete semantics: is replacing an avatar atomic (new file stored, then the user's URL swapped)? Is deleting the only avatar different from deleting a subsequent one? Any guards (like last-admin)?
- **Context:** user-management's last-admin guard shows the repo pattern for protective rules; avatars are per-user.
- **Question:** Avatar lifecycle: upload (first), replace (second and later), delete. Is replace atomic (new file stored, then the user's URL swapped)? Is deleting the only avatar different from deleting a subsequent one (e.g., revert to a default)? Any guards?
- **Answer:** Upload / replace / delete. Replace: new file stored, new URL returned, old file deleted. Delete: file deleted, caller clears the URL. No special guards.
- **Date:** 2026-09-13
- **Status:** ANSWERED
- **Incorporated:** no

## Q-18 — Avatar URL format
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** file-management, FEATURE
- **Why needed:** Cross-feature contract conflict: user-management validates `profile_picture_url` as starting with `http://` or `https://`, but this feature has no HTTP layer (per the repo pattern). The avatar URL file-management produces must satisfy user-management's validation.
- **Context:** user-management AC-007: a `ftp://` profile picture URL is rejected; only http(s) is allowed.
- **Question:** With no HTTP layer, what URL does an avatar get? E.g., a stable pattern like `https://<base>/files/<file_id>` with a configurable base URL? Or should user-management's URL validation be extended (spec amendment)?
- **Answer:** Configurable base URL pattern: `https://<base>/files/<file_id>` with a configurable base URL (settings registry). No user-management spec amendment.
- **Date:** 2026-09-13
- **Status:** ANSWERED
- **Incorporated:** no

## Q-19 — Avatar constraints
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** file-management, FEATURE
- **Why needed:** Avatars need their own constraints (max size, allowed image types, max dimensions) and possibly per-user quotas (file count / total size).
- **Context:** No existing avatar constraints in the repo.
- **Question:** What are the avatar constraints: max size (default?), allowed image types (png/jpeg/webp?), max dimensions? Are there per-user quotas (file count / total size)?
- **Answer:** Allowed: image/png, image/jpeg, image/webp; max 4096x4096 dimensions (verified by Pillow decode); no per-user quota.
- **Date:** 2026-09-13
- **Status:** ANSWERED
- **Incorporated:** no

## Q-20 — Avatar cleanup on user deletion + default avatar
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** file-management, FEATURE
- **Why needed:** When a user is deleted, their avatar files should be cleaned up (else orphaned). When a user is deactivated, is the avatar kept? Is there a "default avatar" fallback when none is set?
- **Context:** user-management publishes `UserDeleted`/`UserDeactivated` events; deletion is a hard delete of the user record.
- **Question:** When a user is deleted, are their avatar files also deleted (file-management subscribes to `UserDeleted`)? When a user is deactivated, is the avatar kept? Is there a "default avatar" fallback when no avatar is set?
- **Answer:** Cleanup on user deletion stays the caller's responsibility (per Q-2; no UserDeleted subscription). There IS a built-in default avatar: the feature ships a default avatar image and returns its URL when a user has no avatar.
- **Date:** 2026-09-13
- **Status:** ANSWERED
- **Incorporated:** no

## Q-21 — Download output shape
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** file-management, FEATURE
- **Why needed:** "Download" needs an output shape: return bytes, return a stream, or write to a destination path. And the error for a missing file. Range/partial download is likely out of scope.
- **Context:** No existing download capability in the repo.
- **Question:** What output shape should `download` have: return bytes, return a file-like stream, write to a destination path (or all of them)? What error for a missing file? Is range/partial download out of scope?
- **Answer:** Return bytes or a file-like stream. Missing file → FileNotFoundError. Range/partial download out of scope.
- **Date:** 2026-09-13
- **Status:** ANSWERED
- **Incorporated:** no

## Q-22 — Download access control
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** file-management, FEATURE
- **Why needed:** In-process downloads could be open to any caller (in-process trust model) or gated by owner reference/role/session (authentication integration). The idea does not specify.
- **Context:** The authentication feature provides sessions/tokens; user-management has roles; the in-process trust model is consistent with existing features (no per-call auth).
- **Question:** Are downloads open to any in-process caller (consistent with existing features), or gated (owner reference, role, session token via the authentication feature)?
- **Answer:** Open in-process access (any in-process caller); consistent with existing features.
- **Date:** 2026-09-13
- **Status:** ANSWERED
- **Incorporated:** no

## Q-23 — Events
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** file-management, FEATURE
- **Why needed:** Per the repo pattern, features publish typed lifecycle events to the shared event bus. The event set must be pinned (FileUploaded, FileDownloaded, FileDeleted, FileValidationFailed, AvatarUploaded, AvatarDeleted), and events must carry non-sensitive data only.
- **Context:** user-management publishes 7 event types; settings publishes `SettingChanged`; the event bus is the shared mechanism.
- **Question:** Which typed events should file-management publish to the shared event bus? Proposed: FileUploaded, FileDownloaded, FileDeleted, FileValidationFailed, AvatarUploaded, AvatarDeleted. Do events carry non-sensitive data only (no content, no secrets)?
- **Answer:** The full proposed set: FileUploaded, FileDownloaded, FileDeleted, FileValidationFailed, AvatarUploaded, AvatarDeleted — non-sensitive data only.
- **Date:** 2026-09-13
- **Status:** ANSWERED
- **Incorporated:** no

## Q-24 — Error taxonomy
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** file-management, FEATURE
- **Why needed:** The spec needs a structured exception hierarchy (repo pattern: root error with documented context attributes). The classes and context must be confirmed.
- **Context:** user-management: `UserManagerError` root with context attributes; settings: `SettingsError` hierarchy; mail: `MailError` hierarchy.
- **Question:** Confirm the exception hierarchy rooted at `FileManagementError`: `FileNotFoundError`, `FileTooLargeError`, `FileTypeNotAllowedError`, `FileValidationError`, `StorageError`, `AvatarError` (plus avatar-specific). Do validation errors carry context (key, actual vs. limit/allowed)?
- **Answer:** Confirmed — the proposed hierarchy rooted at FileManagementError, with context attributes on validation errors (key, actual vs. limit/allowed).
- **Date:** 2026-09-13
- **Status:** ANSWERED
- **Incorporated:** no

## Q-25 — NFR performance budgets
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** file-management, FEATURE
- **Why needed:** Testable performance budgets are needed (repo pattern: median budgets in contract tests), including the mandated logging overhead.
- **Context:** user-management NFR-001 (reads < 5 ms, create < 1 s); settings NFR-001 (per-op budgets); the logging policy mandates `@logged` tracing on all public methods.
- **Question:** What are the performance budgets? Proposed: upload of a 10 MB file < 2 s (median); download of a 10 MB file < 1 s (median); metadata read < 5 ms (median); all including `@logged` tracing overhead. Any different values?
- **Answer:** The proposed budgets: 10 MB upload < 2 s, 10 MB download < 1 s, metadata read < 5 ms (median, incl. tracing overhead).
- **Date:** 2026-09-13
- **Status:** ANSWERED
- **Incorporated:** no

## Q-26 — NFR security (path traversal / symlinks)
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** file-management, FEATURE
- **Why needed:** File storage has classic security risks: keys/filenames containing `../`, absolute paths, or symlinks could escape the storage root. This must be a hard invariant.
- **Context:** No existing file storage in the repo to reference; the settings YAML repository writes within its own directory.
- **Question:** Confirm the hard security invariant: no key/filename can escape the storage root (reject or normalize `../`, absolute paths, null bytes; handle symlinks — reject or resolve within root). Which symlink behavior: reject or resolve within root?
- **Answer:** Hard invariant; reject symlinks. Nothing escapes the storage root; reject `../`, absolute paths, null bytes; reject symlinks.
- **Date:** 2026-09-13
- **Status:** ANSWERED
- **Incorporated:** no

## Q-27 — Settings registry integration
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** file-management, FEATURE
- **Why needed:** Configurable limits should use the shared settings registry (repo pattern: `register_feature("file-management", [...])`, live reads like mail-service). The key set and category must be confirmed.
- **Context:** mail-service registers `mail.*` keys and reads them live on each send; the settings registry is the shared mechanism.
- **Question:** Confirm the settings keys registered via `register_feature("file-management", [...])` (e.g., `file-management.storage_root`, `file-management.max_file_size`, `file-management.avatar_max_size`, `file-management.allowed_types`, `file-management.avatar_base_url`), read live on each operation. Which keys should be settings vs. constructor args?
- **Answer:** The proposed keys (storage_root, max_file_size, avatar_max_size, allowed_types, avatar_base_url), read live; repository/backend injection stays constructor args.
- **Date:** 2026-09-13
- **Status:** ANSWERED
- **Incorporated:** no

## Q-28 — Observability policy
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** file-management, FEATURE
- **Why needed:** The AGENTS.md tracing policy mandates public service classes traced with `@logged_class` (with `include_args=False` where secrets are involved) and module functions with `@logged`. Confirm applicability and slow thresholds.
- **Context:** AGENTS.md "Using the Logging Feature" — tracing policy (default); user-management's `UserManager` is traced with `@logged_class`.
- **Question:** Confirm: the public service class (e.g., `FileService`) is traced with `@logged_class` (with a sensible `slow_threshold_ms`), module-level functions with `@logged`, `include_args=False` where secrets are involved. Any method that needs `include_args=True` for debuggability?
- **Answer:** Confirmed — @logged_class on the service, @logged on module functions, include_args=False where secrets are involved.
- **Date:** 2026-09-13
- **Status:** ANSWERED
- **Incorporated:** no

## Q-29 — Scope boundary: user-file-storage vs. centralizing all persistence (user-initiated)
- **Step:** S1.1 Interrogate — Phase 1 (user-initiated clarification)
- **Change:** file-management, FEATURE
- **Why needed:** The user asked whether settings' YAML templates (and, by extension, user-management/authentication SQLite databases) should be centralized through file-management "as they are files that are stored." This is a scope/architecture decision that could reclassify the change (FEATURE → CROSS-CUTTING) and require amending multiple approved specs.
- **Context:** file-management reads its own limits live from the settings registry (file-management → settings). Routing settings' YAML (and other features' SQLite) through file-management would make every feature depend on file-management (settings → file-management), a dependency cycle. SQLite is a database engine (not file content); YAML is configuration state — different concerns from user files (upload/download/avatars). The settings, user-management, and authentication specs are already approved.
- **Question:** Should file-management centralize all file-based persistence (settings YAML, user-management/authentication SQLite), or stay the user-file-storage feature with each feature keeping its own persistence?
- **Answer:** Keep as **user file storage** (original scope). file-management = upload/download/avatars/metadata/validation for user files (StorageBackend ABC: local disk / in-memory). Each feature keeps its own persistence (SQLite via repository ABC, YAML via repository) — these are internal state, not user files. **Normative** layout convention (NOT optional): a **common persistence root** (`./data/`) where user files live under `./data/files/` and each feature's own files live in their own subdirectory — a layout convention, not a code dependency. Stays **FEATURE** (no spec amendments, no dependency cycle).
- **Date:** 2026-09-13
- **Status:** ANSWERED
- **Incorporated:** no

## Q-30 — Pre-existing import bug in the Phase 3 test helper blocks collection (S4.1/S4.2)
- **Step:** S4.1 Pick task + confirm RED / S4.2 Implement + confirm GREEN — Phase 4 (T-001)
- **Change:** file-management, FEATURE
- **Why needed:** T-001 (foundation: errors, events, models) is implemented and the module imports cleanly, but T-001's test (`test_ac_051_error_hierarchy_context`) cannot be collected: the committed Phase 3 test helper `tests/filemanagement_test_helpers.py` line 15 does `from collections.abc import BinaryIO, Sequence`, and `BinaryIO` is NOT in `collections.abc` (it lives in `typing`). This fails at import time and blocks collection of ALL file-management tests (the helper is imported at module level by every file-management conftest and test module). Fixing it requires modifying a test file, which the task rules forbid (“Do NOT weaken, modify, or delete any test”).
- **Context:** `git status` shows only `src/backend/filemanagement/` (my T-001 implementation) as new; the helper is committed and unchanged (commit `b8765db`, Phase 3). `uv run python -c "from collections.abc import BinaryIO"` fails on Python 3.14.5; `from typing import BinaryIO` works. Other helpers correctly import only `Callable`/`Iterator` from `collections.abc`. The Phase 3 verification doc records the RED state as `ModuleNotFoundError: backend.filemanagement`, but with this import bug the actual collection error is the `BinaryIO` ImportError (so the Phase 3 RED signal was not the documented one).
- **Question:** May I fix the pre-existing import bug in `tests/filemanagement_test_helpers.py` (change `from collections.abc import BinaryIO, Sequence` to `from collections.abc import Sequence` + `from typing import BinaryIO`) so the suite can be collected? This is a bug fix in test infrastructure (it does NOT weaken, modify assertions, or delete any test). Alternatively, should the Phase 3 test step be re-run to correct the helper?
- **Answer:** Yes — fix the import bug in `tests/filemanagement_test_helpers.py` line 15 (change `from collections.abc import BinaryIO, Sequence` to `from collections.abc import Sequence` + `from typing import BinaryIO`). This is a compatibility fix in test infrastructure (it does NOT weaken, modify assertions, or delete any test). The suite can then be collected and T-001 can confirm GREEN.
- **Date:** 2026-09-13
- **Status:** ANSWERED
- **Incorporated:** yes

## Q-31 — Second pre-existing import bug: the `tests.` prefix in the 5 filemanagement test files blocks collection (S4.2)
- **Step:** S4.2 Implement + confirm GREEN — Phase 4 (T-001)
- **Change:** file-management, FEATURE
- **Why needed:** After the Q-30 BinaryIO fix, the file-management test suite **still** cannot be collected — but for a different reason. All 5 filemanagement test files import the shared helper with a `tests.` prefix (`from tests.filemanagement_test_helpers import (...)`), which requires the repo root on `sys.path`. Under `uv run pytest` (and CI's `uv run pytest tests/ -v`), the repo root is **not** on `sys.path` (only `src/` is, via the editable install), so all 5 test files fail to collect with `ModuleNotFoundError: No module named 'tests'`. This blocks confirming T-001 GREEN (T-001's test `test_ac_051_error_hierarchy_context` lives in `tests/acceptance/filemanagement/test_filemanagement.py`). The task rules forbid "any OTHER changes to the test files" (only the Q-30 BinaryIO fix is authorized), so I cannot fix this without user input.
- **Context:**
  - The `tests.` prefix is an anomaly: every other suite in the repo (mail, logging, settings, usermanagement, authentication, eventbus) uses bare imports (`from mail_test_helpers import ...`), and the filemanagement `conftest.py` files themselves already use bare imports (`from filemanagement_test_helpers import ...`). Only the 5 filemanagement test files use the `tests.` prefix.
  - This import was never exercised in Phase 3 (the per-directory `conftest.py` failed first with `ModuleNotFoundError: backend.filemanagement`, before the test module was imported), so it is a latent bug that would also break CI (`uv run pytest tests/ -v`).
  - The T-001 implementation (`src/backend/filemanagement/{errors,events,models}.py`) is complete and matches the spec and T-001's test expectations (verified by reading all files: the error hierarchy, events, models, and constants all line up with `test_ac_051_error_hierarchy_context`). The **only** remaining blocker is the `tests.` prefix import.
  - Two candidate fixes: (a) change `from tests.filemanagement_test_helpers import (...)` to `from filemanagement_test_helpers import (...)` in the 5 filemanagement test files (matches the conftest in the same directory and every other suite in the repo — an import-compatibility fix, no assertion changes); or (b) add repo-root-to-`sys.path` infrastructure (a root `conftest.py`, or `pythonpath = ["."]` under `[tool.pytest.ini_options]` in `pyproject.toml`) so no existing test file is modified.
- **Question:** May I fix the `tests.` prefix import bug? **Recommended:** option (a) — change the `tests.` prefix to a bare `from filemanagement_test_helpers import (...)` in the 5 filemanagement test files (matching the conftest in the same directory and every other suite in the repo). This is an import-compatibility fix (it does NOT weaken, modify assertions, or delete any test). Alternatively, authorize option (b) (a root `conftest.py` or `pythonpath = ["."]` in `pyproject.toml`) so no existing test file is modified. Which do you authorize?
- **Answer:** Option (a) — bare imports. Change `from tests.filemanagement_test_helpers import (...)` to `from filemanagement_test_helpers import (...)` in the 5 filemanagement test files. This matches the conftest in the same directory and every other suite in the repo (mail feature). Import-compatibility only — it does NOT weaken, modify assertions, or delete any test.
- **Date:** 2026-09-13
- **Status:** ANSWERED
- **Incorporated:** yes
