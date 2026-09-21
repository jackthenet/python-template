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

## Q-32 — Third pre-existing test bug: `st.binary(alphabet=...)` in the property tests blocks collection (and T-001's GREEN gate) (S4.2)
- **Step:** S4.2 Implement + confirm GREEN — Phase 4 (T-001, re-entry after Q-30/Q-31)
- **Change:** file-management, FEATURE
- **Why needed:** After the Q-30 (BinaryIO) and Q-31 (bare imports) fixes, the file-management suite collects **84 of 85 tests** — but `tests/property/filemanagement/test_filemanagement_properties.py` still fails at collection time: line 49 calls `st.binary(min_size=1, max_size=4096, alphabet=b"abcdefghijklmnopqrstuvwxyz0123456789")`, and Hypothesis' `st.binary()` accepts **no** `alphabet` argument (in 6.155.0 or any version — `st.binary` only takes `min_size`/`max_size`). The error is raised at module level (the `@given(content=_content(), ...)` decorator evaluates `_content()` at import), so pytest reports `TypeError: binary() got an unexpected keyword argument 'alphabet'` and **interrupts the whole run before any test executes**. T-001's `green_command` runs all five file-management directories, so it cannot confirm T-001 GREEN until this is fixed. The task rules forbid "any OTHER changes to the test files" (only the Q-30 + Q-31 fixes are authorized), so I cannot fix this without user input.
- **Context:**
  - The bug is in the committed Phase 3 test (commit `b8765db`), not in my implementation. It was never exercised in Phase 3 because the per-directory conftests failed first (`ModuleNotFoundError: backend.filemanagement`), so it is a latent test-infrastructure bug that would also break CI (`uv run pytest tests/ -v`).
  - The test's documented intent (line 48 docstring): "Non-empty ASCII content of varying size (allowed by the default policy)." The `alphabet` argument was meant to restrict generated bytes to ASCII alphanumerics.
  - T-001's implementation (`src/backend/filemanagement/{errors,events,models}.py`) is complete and T-001's own test PASSES: `uv run pytest tests/acceptance/filemanagement/test_filemanagement.py::test_ac_051_error_hierarchy_context -v` → **1 passed**. The remaining 20 failed + 63 errors in the four other directories are later-task tests (T-002..T-008: service/repository/storage are `NotImplementedError` placeholders) — expected RED, not blockers for T-001.
  - **Proposed fix (validated against Hypothesis 6.155.0, preserves the documented intent, changes NO assertion):** line 49 → `return st.lists(st.sampled_from(b"abcdefghijklmnopqrstuvwxyz0123456789"), min_size=1, max_size=4096).map(bytes)`. This is the only invalid call in the file (all other `st.` calls — `st.sampled_from`, `st.lists`, `st.integers`, `st.from_regex` — are valid API).
  - Alternative (weaker): `return st.binary(min_size=1, max_size=4096)` — drops the ASCII-alphabet restriction the docstring describes.
- **Question:** May I fix the `st.binary(alphabet=...)` bug in `tests/property/filemanagement/test_filemanagement_properties.py` line 49? **Recommended:** `return st.lists(st.sampled_from(b"abcdefghijklmnopqrstuvwxyz0123456789"), min_size=1, max_size=4096).map(bytes)` (preserves the documented "non-empty ASCII content of varying size" intent; no assertion changes; no test weakened). This is a test-infrastructure bug fix (the test cannot run at all as written). Alternatively, authorize the weaker `st.binary(min_size=1, max_size=4096)`. Which do you authorize?
- **Answer:** Preserve ASCII intent — change line 49 to `return st.lists(st.sampled_from(b"abcdefghijklmnopqrstuvwxyz0123456789"), min_size=1, max_size=4096).map(bytes)`. This preserves the documented "non-empty ASCII content of varying size" intent, changes NO assertion, and weakens no test. Validated against Hypothesis 6.155.0.
- **Date:** 2026-09-13
- **Status:** ANSWERED
- **Incorporated:** yes

## Q-33 — Fourth pre-existing test bug: `function_scoped_fixture` health check trips in ALL 8 property tests, blocking T-003's RED→GREEN (S4.1)
- **Step:** S4.1 Pick task + confirm RED — Phase 4 (T-003)
- **Change:** file-management, FEATURE
- **Why needed:** After the Q-30 (BinaryIO) / Q-31 (bare imports) / Q-32 (`st.binary(alphabet=...)`) fixes, the filemanagement property test file now collects and runs — but **all 8 property tests** (`test_inv_001` .. `test_inv_008`) fail with `hypothesis.errors.FailedHealthCheck`: "uses a function-scoped fixture 'tmp_path'". This is the `function_scoped_fixture` health check, which fires **before the test body executes** — so the unimplemented-signal `NotImplementedError` from the T-003 placeholders is never reached. It is therefore **not** masking the unimplemented signal; the test body simply never runs. The check is **independent of the implementation**: it is triggered by the tests' use of `tmp_path` (a function-scoped fixture) with `@given`, and only `HealthCheck.too_slow` is suppressed (not `HealthCheck.function_scoped_fixture`). T-003's test `test_inv_007_key_containment` is one of the 8, so T-003's RED gate is "RED" (failing) but for the wrong reason, and T-003 can **never** go GREEN as written (the health check is independent of the implementation) — T-003's completion gate ("property test for INV-007 passes") cannot be met without fixing the test. The task rules forbid modifying test files, so I cannot fix this without user input.
- **Context:**
  - This is the 4th pre-existing test bug in the same Phase 3 property test file (after Q-30 BinaryIO, Q-31 bare imports, Q-32 `st.binary(alphabet=...)`). Each was discovered during S4.1/S4.2 and escalated.
  - The bug affects **all 8 property tests** in the file (`test_inv_001` .. `test_inv_008`), which span multiple tasks (T-003 owns `test_inv_007`; the other 7 belong to T-004..T-008). So it is a file-wide issue, not T-003-specific.
  - All 8 `@settings` lines (lines 52, 76, 104, 119, 141, 154, 176, 188) are identical: `@settings(max_examples=_MAX_EXAMPLES, suppress_health_check=[HealthCheck.too_slow])` — none suppress `function_scoped_fixture`.
  - The `key` strategy in `test_inv_007` is `st.from_regex(r"[A-Za-z0-9][A-Za-z0-9._-]{0,20}", fullmatch=True)` — a valid strategy (not malformed, not over-filtered). The strategy is not the problem.
  - The tests are semantically correct: each creates a unique subdirectory/DB per test invocation (function scope), and each generated input uses a unique key, so a shared `tmp_path` root is fine. The health check is a false positive for these tests.
  - **Proposed fix (mechanical, the fix Hypothesis itself recommends in the error message; preserves intent; changes NO assertion; weakens NO test):** in all 8 property tests, change `suppress_health_check=[HealthCheck.too_slow]` to `suppress_health_check=[HealthCheck.too_slow, HealthCheck.function_scoped_fixture]`.
- **Question:** May I fix the `function_scoped_fixture` health check by adding `HealthCheck.function_scoped_fixture` to `suppress_health_check` in all 8 property tests in `tests/property/filemanagement/test_filemanagement_properties.py`? **Recommended:** yes — add `HealthCheck.function_scoped_fixture` to the `suppress_health_check` list in all 8 tests (the fix Hypothesis recommends; preserves intent; changes NO assertion; weakens NO test). This unblocks T-003's RED→GREEN and the other tasks' property tests. Alternatively, authorize only the T-003 test (`test_inv_007`) and defer the other 7 to their own tasks. Which do you authorize?
- **Answer:** **Yes — fix all 8 property tests.** Add `HealthCheck.function_scoped_fixture` to `suppress_health_check` in all 8 property tests in `tests/property/filemanagement/test_filemanagement_properties.py` (change `suppress_health_check=[HealthCheck.too_slow]` to `suppress_health_check=[HealthCheck.too_slow, HealthCheck.function_scoped_fixture]`). Rationale: the `function_scoped_fixture` health check is a **false positive** for these tests — each test creates a unique `uuid4()` subdirectory/DB and each generated input uses a unique key, so the shared function-scoped `tmp_path` root is safe (no cross-example state accumulation). The fix is a **test-infrastructure compatibility fix** (the fix Hypothesis itself recommends): it preserves intent, changes **no assertion**, and weakens **no test** — the same class of authorized fix as Q-30/Q-31/Q-32. Fixing all 8 now (not just `test_inv_007`) unblocks the remaining property tests for T-004..T-008 in one go, avoiding re-hitting the same file-wide bug 7 more times. **Answered by the orchestrator under the user's delegated decision authority** (the user stepped away and instructed: "answer your questions for yourself until my next message").
- **Date:** 2026-09-14
- **Status:** ANSWERED
- **Incorporated:** yes (to be applied as an authorized test-infrastructure fix in T-003's S4.2, committed separately from the T-003 implementation)

## Q-34 — Relationship to the existing authentication feature (new feature vs. extension)
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** session-management, FEATURE
- **Why needed:** The idea (active sessions/devices, logout current/all, expiration, revocation) overlaps heavily with the already-approved authentication feature, which owns the `Session` table, `SessionRepository`, `AuthService.session_info(token)`, `logout(token)`, TTL expiration, and revocation on password change/reset. This answer determines whether the change is a new feature, an extension of authentication (spec amendment), or a CROSS-CUTTING change, and which existing REQ/AC IDs are extended.
- **Context:** `docs/specs/authentication.md`: REQ-006 (opaque tokens, SHA-256 at rest), REQ-007 (TTL expiration, `authentication.session_ttl`), REQ-008 (`session_info(token)`), REQ-009 (`logout(token)`, idempotent), REQ-012 (revocation on reset completion), INV-002 (validity iff unrevoked and unexpired), NFR-003 (public API backward-compatibility contract). Implementation `src/backend/authentication/`: `Session` table (id, user_id, token_hash, created_at, expires_at, revoked — no device fields); `SessionRepository` ABC (add, get_by_token_hash, revoke, revoke_all_for_user, delete_expired — no list_for_user); `AuthService` (login, session_info, logout, reset, passkey).
- **Question:** Which option? (a) A new feature `src/backend/sessionmanagement/` that reuses authentication's `Session` table + `SessionRepository` (constructor-injected; the repository ABC is extended with e.g. `list_for_user`), (b) extend the authentication feature itself (new `AuthService` methods + spec amendment to `authentication.md`), or (c) a new feature with its own read-only repository over the same `sessions` table (zero changes to authentication)?
- **Answer:** Option (a): a new feature `src/backend/sessionmanagement/` reusing authentication's `Session` table + `SessionRepository` (constructor-injected; the repository ABC is extended with e.g. `list_for_user`). No spec amendment to `authentication.md`.
- **Date:** 2026-09-15
- **Status:** ANSWERED
- **Incorporated:** yes

## Q-35 — Backend-only scope (no HTTP layer, no frontend)
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** session-management, FEATURE
- **Why needed:** Every existing backend feature is an in-process Python service with no HTTP/REST layer, but "active sessions/devices" could imply a user-facing UI or web API. The answer fixes the entire API surface.
- **Context:** All features in `src/backend/` (authentication, usermanagement, settings, mail, filemanagement, eventbus, logging) are in-process services; no web framework in `pyproject.toml`; the authentication spec explicitly lists frontend/HTTP as out of scope.
- **Question:** Confirm: session-management is a backend-only in-process service (no HTTP/REST layer, no frontend), consistent with all existing features? If an HTTP layer is needed, is it part of this change or a separate change?
- **Answer:** Confirmed: backend-only in-process service (no HTTP/REST layer, no frontend), consistent with all existing features.
- **Date:** 2026-09-15
- **Status:** ANSWERED
- **Incorporated:** yes

## Q-36 — Source of device identification ("devices" in "active sessions/devices")
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** session-management, FEATURE
- **Why needed:** "Active sessions/devices" implies per-session device identification, but with no HTTP layer the backend cannot observe user-agent/IP in-process, and the `Session` table has no device fields. This decides whether a schema change to authentication's login path is required and what the list entries can show.
- **Context:** `Session` table fields: id, user_id, token_hash, created_at, expires_at, revoked. No user_agent/ip/device_name. Login is owned by authentication (`AuthService.login(LoginRequest(identifier, password))`).
- **Question:** Which option? (a) capture device info at login — add optional `user_agent`/`ip`/`device_name` fields to the login schema (schema change to authentication, stored on the `Session` row), (b) no device identification — a "device" is just a session listed with timestamps (display name null), or (c) a separate device-binding API — the client calls with its token to attach a device name to an existing session?
- **Answer:** Option (a): capture device info at login — add optional `user_agent`/`ip`/`device_name` fields to the login schema, stored on the `Session` row (schema change to authentication's storage).
- **Date:** 2026-09-15
- **Status:** ANSWERED
- **Incorporated:** yes

## Q-37 — "Logout from all sessions" semantics (include the current one?)
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** session-management, FEATURE
- **Why needed:** "Logout from all sessions" is ambiguous: does "all" include the caller's current session (full logout, caller loses their token) or exclude it ("log out all other devices")? The API shape (self-service via token vs. admin via user_id) also depends on this.
- **Context:** `SessionRepository.revoke_all_for_user(user_id)` already exists (repository level, no service API); `AuthService.logout(token)` is per-token and idempotent. The repository has no "revoke all except one" operation.
- **Question:** Which option(s)? (a) `logout_all_sessions(token)` — self-service, revokes the caller's session too, (b) `logout_other_sessions(token)` — self-service, excludes the caller's current session, (c) `revoke_all_sessions(user_id)` — admin, no token required, (d) some combination (e.g., both self-service and admin variants)?
- **Answer:** Options (a), (b) and (c) — all three: `logout_all_sessions(token)` (self-service, revokes the caller's session too), `logout_other_sessions(token)` (self-service, excludes the caller's current session), and `revoke_all_sessions(user_id)` (admin, no token required).
- **Date:** 2026-09-15
- **Status:** ANSWERED
- **Incorporated:** yes

## Q-38 — Service-level revocation of a specific session
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** session-management, FEATURE
- **Why needed:** The "session revocation" bullet plus a session list implies the user can revoke a specific session (e.g., remove a device from the list). The repository has `revoke(session_id)` but no service-level API. The identifier choice (session id vs. token) is constrained by NFR-002 (raw tokens are never exposed after login).
- **Context:** `SessionRepository.revoke(session_id: UUID)` exists; `SessionInfo` (authentication) exposes only user_id, created_at, expires_at — no session id. A new list representation would need to expose the session id (a UUID, not a token).
- **Question:** Is an explicit "revoke this specific session" API in scope? If yes, what is the identifier — the session id (UUID, exposed in the list) or the raw token? Proposed: `revoke_session(session_id)` for list-driven revocation, with `logout(token)` (authentication) remaining the token-based path.
- **Answer:** In scope: `revoke_session(session_id)` — revoke a specific session by its UUID as exposed in the session list; `logout(token)` (authentication) remains the token-based path.
- **Date:** 2026-09-15
- **Status:** ANSWERED
- **Incorporated:** yes

## Q-39 — "Current session" marker in the session list
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** session-management, FEATURE
- **Why needed:** To identify the caller's own session in the list (UI "this device" label, self-lockout prevention), the list must mark the current session. This depends on whether the list API takes the caller's token.
- **Context:** Self-service listing by token would resolve user_id via `session_info(token)` (authentication REQ-008). Admin listing by user_id has no token to compare.
- **Question:** Which option? (a) the list API takes the caller's token and returns an `is_current` flag per entry, (b) no marker — the caller identifies the current session by other means, or (c) marker only for token-based (self-service) listing, absent for admin listing?
- **Answer:** Option (a): the list API takes the caller's token and returns an `is_current` flag per entry (true for the caller's own session).
- **Date:** 2026-09-15
- **Status:** ANSWERED
- **Incorporated:** yes

## Q-40 — "Session expiration" semantics (TTL reuse vs. new expiration modes)
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** session-management, FEATURE
- **Why needed:** TTL-based expiration already exists (authentication REQ-007; `authentication.session_ttl` setting, default 604800 s, read live). The "session expiration" bullet could mean: reuse the existing TTL, add sliding/active expiration (extend on activity), or add per-session/admin-set expiration. Each has very different scope.
- **Context:** `authentication.feature_settings` registers `authentication.session_ttl` (NUMBER, default 604800, min 1). `Session.expires_at` is set at creation; nothing updates it afterwards.
- **Question:** Which option? (a) no change to expiration semantics — reuse the existing TTL (this feature only manages listing/revocation/cleanup), (b) add sliding/active expiration (extend `expires_at` on activity — requires touching the token-use path), or (c) add per-session/admin-set expiration (e.g., "expire this session now" / set a custom expiry)?
- **Answer:** Option (a): no change to expiration semantics — reuse the existing TTL (`authentication.session_ttl`); this feature only manages listing/revocation/cleanup.
- **Date:** 2026-09-15
- **Status:** ANSWERED
- **Incorporated:** yes

## Q-41 — Cleanup of expired sessions (who calls `delete_expired`?)
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** session-management, FEATURE
- **Why needed:** `SessionRepository.delete_expired() -> int` exists but nothing ever calls it; expired-but-not-revoked rows accumulate in the `sessions` table indefinitely. The "session expiration" bullet may intend this cleanup.
- **Context:** `SqliteSessionRepository.delete_expired` is implemented; no scheduler, background worker, or service method references it. No other feature in the repo runs background threads.
- **Question:** Which option? (a) expose a `cleanup_expired() -> int` service method (the application calls it on its own schedule), (b) run a background worker thread inside the feature, (c) lazy cleanup (delete expired rows opportunistically on list/read operations), or (d) out of scope for this change?
- **Answer:** Option (a): expose `cleanup_expired() -> int` — the application calls it on its own schedule; no threads in the feature.
- **Date:** 2026-09-15
- **Status:** ANSWERED
- **Incorporated:** yes

## Q-42 — Listing scope: self-service vs. admin
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** session-management, FEATURE
- **Why needed:** "Active sessions/devices" could be viewed by the user themselves (token-authenticated) or by an administrator (by user id). The API surface differs (token parameter vs. user_id parameter).
- **Context:** user-management has roles (default `{"admin", "member"}`) and `UserDeactivated`/`UserDeleted` events; authentication sessions are per-user (`Session.user_id`).
- **Question:** Which option? (a) self-service only (the user lists their own sessions via their token), (b) admin only (list by user_id, no token), or (c) both (two API shapes: token-based and user_id-based)?
- **Answer:** Option (c) both: token-based self-service listing (user lists own sessions via their token) AND user_id-based admin listing.
- **Date:** 2026-09-15
- **Status:** ANSWERED
- **Incorporated:** yes

## Q-43 — Authorization model for user_id-based (admin) operations
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** session-management, FEATURE
- **Why needed:** Existing features use an in-process trust model (no per-call auth). If user_id-based operations are in scope (Q-42), it must be pinned whether they are open to any in-process caller or gated by a role check (user-management "admin" role).
- **Context:** file-management Q-22 precedent: open in-process access was chosen there. user-management exposes `get_user(user_id)` and roles; no feature currently performs a role check per call.
- **Question:** For user_id-based operations (list/revoke-all by user_id): (a) open in-process access (any caller, consistent with existing features), or (b) gated — require the caller to pass a role (e.g., "admin") or an admin user id, checked against user-management? And for token-based operations: confirm resolution via `session_info(token)` (authentication REQ-008), invalid token → `InvalidSessionError`?
- **Answer:** Option (a): open in-process access — user_id-based operations are open to any in-process caller (consistent with the in-process trust model of all existing features); token-based ops resolve via `session_info(token)` (authentication REQ-008), invalid token → `InvalidSessionError`.
- **Date:** 2026-09-15
- **Status:** ANSWERED
- **Incorporated:** yes

## Q-44 — Session list entry fields (representation)
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** session-management, FEATURE
- **Why needed:** The list entry representation must be pinned. The minimum is session_id, created_at, expires_at, is_current; device fields and login method depend on Q-36/Q-45. Raw tokens/hashes must never appear (authentication NFR-002).
- **Context:** `Session` table: id, user_id, token_hash, created_at, expires_at, revoked. `SessionInfo` (authentication): user_id, created_at, expires_at. No device fields, no login method.
- **Question:** Which field set? Proposed minimum: session_id (UUID), created_at, expires_at, is_current (bool). Optional additions: user_agent, ip, device_name (Q-36), login_method ("password"|"passkey", Q-45). Which fields are normative?
- **Answer:** Full set: session_id (UUID), created_at, expires_at, is_current (bool), user_agent, ip, device_name, login_method ("password"|"passkey"). Raw tokens/hashes never appear (authentication NFR-002).
- **Date:** 2026-09-15
- **Status:** ANSWERED
- **Incorporated:** yes

## Q-45 — Store the login method on the session row
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** session-management, FEATURE
- **Why needed:** Showing how each session was created (password vs. passkey) requires storing the method on the `Session` row — a schema change to authentication's table (NFR-003 backward-compatibility contract; existing rows would be null). The authentication `LoginSucceeded` event carries `method`, but the `Session` row does not.
- **Context:** `Session` table has no method column; `AuthService._issue_session(user, method)` receives the method but only stores user_id/token/timestamps.
- **Question:** Should the login method be stored on the `Session` row (nullable column, backward-compatible) so the list can show it? (a) yes, (b) no — the list does not show login method?
- **Answer:** Option (a) yes — add a nullable `login_method` column to the `Session` row (backward-compatible; existing rows null) so the list can show how each session was created.
- **Date:** 2026-09-15
- **Status:** ANSWERED
- **Incorporated:** yes

## Q-46 — Events published by this feature
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** session-management, FEATURE
- **Why needed:** Per the repo pattern, features publish typed lifecycle events to an injected `EventPublisher` (structural protocol). The event set must be pinned, and it must be decided whether authentication's existing `Logout` event is reused or a new event is published for logout-all.
- **Context:** authentication events: `LoginSucceeded`, `LoginFailed`, `Logout(user_id)`, `PasswordResetRequested`, `PasswordResetCompleted`, `PasskeyRegistered`, `PasskeyDeleted`. Events carry non-sensitive data only (no tokens).
- **Question:** Which events should this feature publish? Proposed: `SessionRevoked(user_id, session_id)`, `AllSessionsRevoked(user_id)`, `ExpiredSessionsDeleted(count)`. Should logout-all reuse authentication's `Logout` event, or is a distinct `AllSessionsRevoked` preferred? Is listing an event (e.g., `SessionsListed`) or not (read operation)?
- **Answer:** Proposed set plus `SessionsListed`: publish `SessionRevoked(user_id, session_id)`, `AllSessionsRevoked(user_id)` (distinct from authentication's `Logout`), `ExpiredSessionsDeleted(count)`, and `SessionsListed` (listing is also published).
- **Date:** 2026-09-15
- **Status:** ANSWERED
- **Incorporated:** yes

## Q-47 — Error taxonomy and idempotency for revocation
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** session-management, FEATURE
- **Why needed:** The spec needs a structured exception hierarchy (repo pattern: root error with documented context attributes) and idempotency semantics. Authentication's `logout(token)` is an idempotent no-op for unknown/revoked/expired tokens; `revoke_session(session_id)` with an unknown id could follow the same pattern or raise.
- **Context:** authentication errors: `AuthenticationError` root; `InvalidSessionError` (unknown/revoked/expired token). file-management precedent: `FileNotFoundError` for missing keys.
- **Question:** (a) `revoke_session` with an unknown/already-revoked session id → idempotent no-op (like `logout`), or (b) raise a `SessionNotFoundError` (rooted in a new `SessionManagementError` hierarchy)? Confirm: listing a user with zero active sessions → empty list (no error).
- **Answer:** Option (a): `revoke_session` with an unknown/already-revoked session id is an idempotent no-op (like `logout`); listing a user with zero active sessions → empty list (no error).
- **Date:** 2026-09-15
- **Status:** ANSWERED
- **Incorporated:** yes

## Q-48 — Settings registry keys for this feature
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** session-management, FEATURE
- **Why needed:** Configurable values should use the shared settings registry (repo pattern: feature-owned `register_settings(registry)`, live reads like mail-service/file-management). The key set must be pinned; session TTL already exists as `authentication.session_ttl`.
- **Context:** `authentication.feature_settings` registers `authentication.session_ttl` (604800 s default). file-management registers `filemanagement.*` keys read live per operation.
- **Question:** Which settings keys should this feature register (read live)? Proposed: `sessionmanagement.max_listed_sessions` (default limit for the list), `sessionmanagement.max_sessions_per_user` (if Q-49 caps sessions), and possibly a cleanup-related key (if Q-41 adds cleanup). Reuse `authentication.session_ttl` for expiration (no duplicate TTL key)? Which keys?
- **Answer:** Full proposed set: `sessionmanagement.max_listed_sessions` (default limit for the list), `sessionmanagement.max_sessions_per_user` (per-user cap, per Q-49), and a cleanup-related key, plus reuse of `authentication.session_ttl` for expiration (no duplicate TTL key).
- **Date:** 2026-09-15
- **Status:** ANSWERED
- **Incorporated:** yes

## Q-49 — Max concurrent sessions per user (single-device mode / eviction)
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** session-management, FEATURE
- **Why needed:** A common session-management requirement: cap the number of concurrent active sessions per user (e.g., "single device" mode), evicting the oldest session(s) when a new login exceeds the cap. This changes the login path (authentication) and is a significant behavior addition.
- **Context:** No per-user session cap exists; `AuthService.login` always creates a new session row. Eviction would require authentication's login path to call the new feature (or the repository) — a cross-feature dependency.
- **Question:** Is a per-user concurrent-session cap in scope? If yes: what is the default (e.g., unlimited, 5, 1 = single-device), what is the eviction policy (oldest first), and is the cap configurable via the settings registry? If no, confirm unlimited concurrent sessions.
- **Answer:** Configurable per-user cap — set via the settings registry (`sessionmanagement.max_sessions_per_user`), with oldest-first eviction when the cap is exceeded.
- **Date:** 2026-09-15
- **Status:** ANSWERED
- **Incorporated:** yes

## Q-50 — Pagination for the session list
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** session-management, FEATURE
- **Why needed:** The list API may need pagination (file-management precedent: limit/offset). The default limit and validation rules (file-management: `limit < 1` or `offset < 0` → `ValueError`) must be pinned if in scope.
- **Context:** file-management `list_files(namespace, limit=100, offset=0)` with `ValueError` on invalid limit/offset. No other feature paginates.
- **Question:** Should the session list support pagination (limit/offset)? If yes: default limit (e.g., 100), and the same `ValueError` validation as file-management? Or is a single bounded list (max N, no offset) sufficient?
- **Answer:** A single bounded list with a `limit` parameter (default from `sessionmanagement.max_listed_sessions`); no offset; `limit < 1` → `ValueError`.
- **Date:** 2026-09-15
- **Status:** ANSWERED
- **Incorporated:** yes

## Q-51 — Ordering of the session list
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** session-management, FEATURE
- **Why needed:** The list ordering must be pinned for deterministic output (tests + UI).
- **Context:** No precedent in the repo for session ordering; file-management orders by created_at (newest first for its list).
- **Question:** What is the ordering? Proposed: created_at descending (newest first), with the current session (is_current) optionally pinned first. Which?
- **Answer:** created_at descending (newest first), with the current session (`is_current`) pinned to the top of the list.
- **Date:** 2026-09-15
- **Status:** ANSWERED
- **Incorporated:** yes

## Q-52 — Schema change to the `Session` table (device columns)
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** session-management, FEATURE
- **Why needed:** Adding device columns (user_agent, ip, device_name) to authentication's `Session` table is a schema change to an existing approved feature (NFR-003 backward-compatibility contract). Existing rows would have NULL device data. Alternatives: a separate join table, or no device data at all (Q-36).
- **Context:** `Session` table (authentication): id, user_id, token_hash, created_at, expires_at, revoked. Bootstrap is `create_all` (no migration framework), so adding nullable columns is backward-compatible at the schema level.
- **Question:** If device data is in scope (Q-36): (a) add nullable device columns to the existing `sessions` table (simplest, backward-compatible), (b) a separate `session_devices` join table (one row per session, keeps the `sessions` table untouched), or (c) no device data (sessions only)?
- **Answer:** Option (a) — add nullable device columns to the existing `sessions` table (simplest, backward-compatible; existing rows NULL). **Implied by Q-36** (batch 1, answered 2026-09-15): the user chose "capture device info at login — add optional `user_agent`/`ip`/`device_name` fields to the login schema, stored on the `Session` row". "Stored on the `Session` row" is option (a) — the device data lives directly on the `Session` row; the separate-join-table alternative (b) and the no-device-data alternative (c) are both excluded by the same answer.
- **Date:** 2026-09-15
- **Status:** ANSWERED
- **Incorporated:** yes (implied from Q-36; to be folded into the spec as the device-data storage decision)

## Q-53 — `last_seen_at` activity tracking
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** session-management, FEATURE
- **Why needed:** "Active sessions" could imply a last-activity timestamp. Tracking `last_seen_at` requires a write on every token use (e.g., `session_info`/list), which touches the authentication read path and affects the performance budget (authentication NFR-001: login ≤ 250 ms p95).
- **Context:** `session_info(token)` is currently read-only. A `last_seen_at` update would make it a write operation (SQLite round-trip per token use).
- **Question:** Track `last_seen_at` (updated when a token is used — e.g., on `session_info` or on a token-based list)? (a) yes — acceptable to make token-use a write, (b) no — only created_at/expires_at, or (c) yes but only on token-based list calls (not on `session_info`)?
- **Answer:** Option (b) — no `last_seen_at` tracking; only `created_at`/`expires_at`. **Implied by Q-40** (batch 1, answered 2026-09-15): the user endorsed "no change to expiration semantics — reuse the existing TTL; this feature only manages listing/revocation/cleanup." Tracking `last_seen_at` requires a write on every token use (a write on the authentication read path), which is none of {listing, revocation, cleanup} — it is outside the endorsed scope.
- **Date:** 2026-09-15
- **Status:** ANSWERED
- **Incorporated:** yes (implied from Q-40's endorsed scope; to be folded into the spec as the no-activity-tracking decision)

## Q-54 — Interaction with existing revocation-on-password-change/reset
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** session-management, FEATURE
- **Why needed:** Authentication already revokes all sessions on password change/reset completion (REQ-012). The spec must confirm this path is unchanged and that this feature only adds explicit revocation paths (single/all) — no duplication or conflict.
- **Context:** authentication REQ-012: `complete_password_reset` "revokes all sessions for the user"; `UserManager.change_password` (user-management) does not currently revoke sessions (only the reset-completion path does).
- **Question:** Confirm: revocation on password change/reset (authentication REQ-012) remains unchanged and is NOT re-specified here; this feature adds only explicit revocation (single session / all sessions). Should a plain `change_password` (without reset) also revoke sessions, or does that stay out of scope?
- **Answer:** Revocation on password change/reset (authentication REQ-012) remains unchanged and is NOT re-specified here; ADDITIONALLY, a plain `change_password` (without reset) also revokes all sessions — new behavior of this feature: `session-management` subscribes to `UserPasswordChanged` (user-management) and revokes all sessions of that user.
- **Date:** 2026-09-15
- **Status:** ANSWERED
- **Incorporated:** yes

## Q-55 — Sessions on user deactivation/deletion (orphans)
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** session-management, FEATURE
- **Why needed:** `delete_user` is a hard delete and `Session` rows have no foreign key to users, so deleted users leave orphaned session rows; deactivation does not revoke sessions (a deactivated user's tokens remain valid until TTL). This is a cross-feature boundary (user-management/authentication) that must be explicitly in or out of scope.
- **Context:** user-management REQ-012: `delete_user` hard-deletes; publishes `UserDeleted`. user-management REQ-009: deactivation is a flag. No session cleanup on either event today. file-management Q-20 precedent: cleanup on user deletion was left to the caller.
- **Question:** Which option? (a) in scope — revoke all sessions on `UserDeactivated`/`UserDeleted` (this feature subscribes to user-management events), (b) in scope — only clean up orphaned rows on `UserDeleted` (deactivated users keep valid sessions), (c) out of scope — user-management/authentication behavior unchanged, orphans remain (caller responsibility)?
- **Answer:** Option (a): in scope — this feature subscribes to `UserDeactivated`/`UserDeleted` (user-management events) and revokes all sessions of that user.
- **Date:** 2026-09-15
- **Status:** ANSWERED
- **Incorporated:** yes

## Q-56 — Definition of "active" in the list (expired-but-not-cleaned rows)
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** session-management, FEATURE
- **Why needed:** Until cleanup runs (Q-41), the table contains rows with `revoked == False` but `expires_at < now`. The list must define whether such rows are "active". Including them without a flag would contradict authentication INV-002 (a session is valid iff unrevoked and unexpired).
- **Context:** authentication INV-002: `session_info` succeeds exactly when `revoked == False` and `expires_at > now`. `delete_expired` is never called, so expired rows accumulate.
- **Question:** Does "active" mean valid-only (unrevoked AND unexpired, per INV-002 — expired rows excluded from the list), or are expired-but-not-deleted rows included with an `is_expired` flag? Proposed: valid-only.
- **Answer:** Valid-only — "active" means unrevoked AND unexpired (per authentication INV-002); expired-but-not-cleaned rows are excluded from the list. **Implied by Q-44** (batch 1, answered 2026-09-15): the user pinned the normative list-entry field set as session_id, created_at, expires_at, is_current, user_agent, ip, device_name, login_method — with no `is_expired` flag. The "include expired rows with an `is_expired` flag" branch of this question requires that flag in the entry representation, which Q-44 excludes; including expired rows unflagged would contradict INV-002.
- **Date:** 2026-09-15
- **Status:** ANSWERED
- **Incorporated:** yes (implied from Q-44's pinned field set + INV-002; to be folded into the spec as the valid-only listing decision)

## Q-57 — DI and testing conventions
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** session-management, FEATURE
- **Why needed:** The spec must pin the construction/testing pattern. The repo pattern is constructor injection of repository ABCs + optional structural `EventPublisher`, in-memory fakes for tests, no module singletons (except eventbus/settings-style registries, which this feature does not need).
- **Context:** `AuthService`, `UserManager`, `FileService` all use constructor DI with repository ABCs and optional event publishers; tests use in-memory/temp-directory fakes.
- **Question:** Confirm: a `SessionService` (or similarly named) constructed with the session repository ABC + optional `event_bus` (structural `publish` protocol), an in-memory session repository for tests/DI, and no module singleton? Or should this feature expose a module-level singleton like `get_event_bus()`/`get_settings_registry()`?
- **Answer:** Constructor DI (`SessionService` with the session repository ABC + optional `event_bus`, structural `publish` protocol; in-memory session repository for tests/DI) PLUS a module-level singleton (e.g., `get_session_service()`) for application use.
- **Date:** 2026-09-15
- **Status:** ANSWERED
- **Incorporated:** yes

## Q-58 — Public API naming (package, service, methods, events)
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** session-management, FEATURE
- **Why needed:** The package name, service name, method names, and event names must be pinned for the spec (and for AGENTS.md's "Using the X Feature" note).
- **Context:** Existing packages: `backend.authentication` (`AuthService`), `backend.usermanagement` (`UserManager`), `backend.filemanagement` (`FileService`).
- **Question:** Approve the proposed naming? Package `backend.sessionmanagement`; service `SessionService` with methods `list_sessions`, `revoke_session`, `revoke_all_sessions`, `cleanup_expired` (names may shift per Q-37/Q-41 answers); events `SessionRevoked`, `AllSessionsRevoked`, `ExpiredSessionsDeleted`. Any preferred alternatives?
- **Answer:** Approved: package `backend.sessionmanagement`; service `SessionService` with methods `list_sessions`, `revoke_session`, `logout_all_sessions`, `logout_other_sessions`, `revoke_all_sessions`, `cleanup_expired`; events `SessionRevoked`, `AllSessionsRevoked`, `ExpiredSessionsDeleted`, `SessionsListed`.
- **Date:** 2026-09-15
- **Status:** ANSWERED
- **Incorporated:** yes

## Q-59 — Performance budgets (NFR)
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** session-management, FEATURE
- **Why needed:** Testable performance budgets are needed (repo pattern: budgets in contract tests, measured including the mandated logging overhead, with the logging context stated).
- **Context:** authentication NFR-001: login ≤ 250 ms p95 (local SQLite, INFO console sink). file-management NFR-001: upload/download/metadata-read budgets (median).
- **Question:** What are the performance budgets? Proposed: listing 100 sessions ≤ 50 ms p95; revoking all sessions for a user with 1000 sessions ≤ 250 ms p95; cleanup of 1000 expired rows ≤ 250 ms p95 — all measured on local hardware against a local SQLite database with the shared logging feature at default INFO level with a synchronous console sink (budgets hold including per-call logging overhead). Different values?
- **Answer:** Looser budgets (2× the proposed values): listing 100 sessions ≤ 100 ms p95; revoking all sessions for a user with 1000 sessions ≤ 500 ms p95; cleanup of 1000 expired rows ≤ 500 ms p95 — all measured on local hardware against a local SQLite database with the shared logging feature at default INFO level with a synchronous console sink (budgets hold including per-call logging overhead).
- **Date:** 2026-09-15
- **Status:** ANSWERED
- **Incorporated:** yes

## Q-60 — Observability and secrets policy
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** session-management, FEATURE
- **Why needed:** The AGENTS.md tracing policy mandates `@logged_class` on public service classes (`include_args=False` where secrets are involved) and `@logged` on module functions. Tokens/hashes must never appear in logs, events, or list entries (authentication NFR-002).
- **Context:** `AuthService` is traced with `@logged_class` (`include_args=False`); authentication NFR-002: raw tokens never appear in log records, events, or error messages.
- **Question:** Confirm: the public service class is traced with `@logged_class` (`include_args=False`, sensible `slow_threshold_ms`), module-level functions with `@logged`; raw session tokens and token hashes never appear in log records, events, error messages, or list entries (only session ids). Any method needing `include_args=True`?
- **Answer:** Confirmed: the public service class is traced with `@logged_class` (`include_args=False`, sensible `slow_threshold_ms`); module-level functions with `@logged`; raw session tokens and token hashes never appear in log records, events, error messages, or list entries (only session ids). No method needs `include_args=True`.
- **Date:** 2026-09-15
- **Status:** ANSWERED
- **Incorporated:** yes

## Q-61 — Admin self-lockout guard
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** session-management, FEATURE
- **Why needed:** If the admin (user_id-based) revoke-all API is in scope (Q-37/Q-42), an admin can revoke all sessions for themselves — including their own — and lock themselves out. The admin API has no token, so it cannot exclude the calling session by default. A guard (e.g., optional `exclude_session_id`) or an explicit acceptance is needed.
- **Context:** user-management's last-admin guard (REQ-008) shows the repo pattern for protective rules. The admin API would take `user_id` only (Q-43), so "the calling session" is not identifiable without an extra parameter.
- **Question:** Is admin self-lockout acceptable (no guard — documented behavior), or is a guard required (e.g., the admin revoke-all takes an optional `exclude_session_id: UUID | None` so the caller can keep their own session)?
- **Answer:** Guard required: the admin `revoke_all_sessions(user_id)` takes an optional `exclude_session_id: UUID | None` so the caller can keep their own session; without it, all sessions (including the caller's) are revoked.
- **Date:** 2026-09-15
- **Status:** ANSWERED
- **Incorporated:** yes

## Q-62 — Spec PR approval gate (human pre-approval)
- **Step:** S1.1 Interrogate — Phase 1 (orchestrator, user instruction)
- **Change:** session-management, FEATURE
- **Why needed:** The standard gate requires the spec to be merged through GitHub PR review before Phase 2. The user explicitly pre-approved the specification so the workflow can proceed unattended.
- **Context:** AGENTS.md "Spec Approval Gate (GitHub Review)"; user instruction 2026-09-15: "the pr approval is not necessary for this feature, it is auto approved as i want to go to bed."
- **Question:** Is the spec PR approval gate required for this change?
- **Answer:** No — the human (user) pre-approved the specification on 2026-09-15 (auto-approved). The spec PR is still opened for traceability, but the workflow does NOT stop at the spec-PR-merge gate; Phase 2 proceeds on this recorded pre-approval (deviation from the standard PR-review gate, authorized by the human). The final implementation PR is likewise pre-approved by the human; the agent still opens it and does NOT merge it itself (agent-side human-governance boundary preserved — the merge is performed by the human).
- **Date:** 2026-09-15
- **Status:** ANSWERED
- **Incorporated:** yes

## Q-63 — MkDocs site setup scope (Phase 0, dependency-updates)
- **Step:** Phase 0 — Classify (orchestrator)
- **Change:** dependency-updates, REFACTOR
- **Why needed:** The user's message lists `mkdocstrings` (an MkDocs plugin) among the new dependencies and includes a statement about MkDocs source-directory naming, but does not list the `mkdocs` core dependency or request the site setup (mkdocs.yml + source directory). Scope decision needed before worktree creation.
- **Context:** User message: "add alembic, polyfactory, respx, time-machine,mkdocstrings and deptry. pytest-random, pyyaml replace with pytest-randomly, ruamel.yaml. Update pillow to current version." + "Calling MkDocs's source directory something else (userdocs///) is actually the more honest naming, since it separates 'internal process record' from 'published documentation.'"
- **Question:** Is the MkDocs site setup itself (mkdocs dependency + mkdocs.yml + source directory) part of this dependency change, or a separate follow-up?
- **Answer:** **Deps only** — this change = the 6 additions (alembic, polyfactory, respx, time-machine, mkdocstrings, deptry), the 2 replacements (pytest-random→pytest-randomly, pyyaml→ruamel.yaml), and the pillow update. The MkDocs site setup is a separate future change; the naming decision (Q-64) is recorded and binding for it.
- **Date:** 2026-09-16
- **Status:** ANSWERED
- **Incorporated:** yes

## Q-64 — MkDocs source directory naming (binding decision, user-initiated)
- **Step:** Phase 0 — Classify (orchestrator; user statement)
- **Change:** future MkDocs site change (recorded for it; not part of dependency-updates)
- **Why needed:** The user stated a naming decision for the MkDocs site's source directory. It must be recorded so the future MkDocs site change applies it.
- **Context:** User statement: "Calling MkDocs's source directory something else (userdocs///) is actually the more honest naming, since it separates 'internal process record' from 'published documentation.'" The repo's `docs/` directory is the internal process record (specs, decisions, verification, workflow). The published documentation (MkDocs site source) must NOT live in `docs/`.
- **Question:** What should the MkDocs site's source directory be named?
- **Answer:** **`userdocs/`** (repo root) — the MkDocs site source directory is `userdocs/`, NOT the default `docs/`. Rationale (user): it separates "internal process record" (`docs/`) from "published documentation" (`userdocs/`). Binding for the future MkDocs site change.
- **Date:** 2026-09-16
- **Status:** ANSWERED
- **Incorporated:** yes (recorded; applies to the future MkDocs site change)

## Q-65 — Order-dependent test exposed by the pytest-randomly swap (Phase 4, dependency-updates)
- **Step:** S4.4 (Phase 4, REFACTOR) — dependency-updates
- **Why needed:** The `pytest-random` → `pytest-randomly` swap (user instruction) exposed a pre-existing order-dependent test: `tests/acceptance/logging_coverage/test_services_traced.py::test_service_registry_classes_traced` fails (`assert 1 == 2`) when a settings test that resets the registry singleton runs before it. The full regression (S4.4) was therefore NOT identical to the baseline.
- **Context:** Mechanism: the session-scoped autouse fixture in `tests/conftest.py` creates the settings-registry module singleton (`install_isolated_registry()`); ~6 settings test files call `reset_settings_registry()` and do NOT restore it; the failing test expects 2 `SettingsRegistry.has` log records — one from its own call, one from the `EventBus()` constructor's guarded read (AC-017/AC-018), which happens only when the singleton exists. Pre-existing state leak, exposed (not caused) by the new shuffle.
- **Question:** How should it be handled — (a) targeted order-independence fix in that one test, (b) mark broken (P-21) and proceed, or (c) fix the leak at the source (the ~6 settings test files restore the singleton after resetting it, fixture pattern)?
- **Answer:** **(c) Fix the leak at the source** — the ~6 settings test files that reset the singleton must restore it (fixture pattern). No test weakening (assertions unchanged; only the registry acquisition/teardown changes).
- **Date:** 2026-09-19
- **Status:** ANSWERED
- **Incorporated:** yes (S4.5 step)

## Q-66 — Terminology: "Admin/User" vs. the existing "admin"/"member" role names
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** user-roles-permissions, CROSS-CUTTING
- **Why needed:** The idea says "Roles such as Admin/User", but the existing user-management feature's default role set is `{"admin", "member"}` (REQ-006; roles are lowercase strings validated at construction). "User" is not an existing role name. This determines whether the new capability builds on the existing names, requires a rename (spec amendment + data migration to user-management), or introduces a third role.
- **Context:** `docs/specs/user-management.md`: REQ-006 (configurable role set, default `{"admin", "member"}`), D3 (roles are lowercase strings, `UserManager(roles=...)`), AC-009 (custom role sets work), EDGE-010 (uppercase rejected). The user-management spec lists "user groups/teams/permissions beyond roles" as out of scope — this change fills that gap on top of the existing role model.
- **Question:** Which relationship holds? (a) Keep the existing names as-is — "User" in the idea is informal for the existing `member` role; no rename, no new role; (b) Rename `member` → `user` (spec amendment to user-management, breaking change, data migration of existing role values); (c) Add `user` as a distinct third role alongside `admin`/`member`? Which?
- **Answer:** (b) Rename `member` -> `user`. The default role set becomes {"admin", "user"}. Requires a user-management spec amendment + data migration of existing role values + test updates.
- **Date:** 2026-07-10
- **Status:** ANSWERED
- **Incorporated:** yes

## Q-67 — Static vs. dynamic role→permission mapping
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** user-roles-permissions, CROSS-CUTTING
- **Why needed:** This is the largest fork in the permission model. A static mapping (fixed in code: admin → all, member → fixed subset) is simple with no storage; a dynamic mapping (DB-backed, changeable at runtime via an API — e.g., an admin grants `filemanagement.upload` to `member`) adds tables, a repository, a grant/revoke API, and validation. It determines most of the data model, API surface, and NFRs.
- **Context:** No permission/authorization code exists anywhere in `src/` (grep: no matches for permission/authorization/authorize). The repo pattern for durable state is SQLModel/SQLite behind a repository ABC (user-management, authentication, file-management, session-management).
- **Question:** Is the role→permission assignment (a) static in code (a fixed mapping defined at startup; changing it requires a code change), or (b) dynamic/configurable (persisted, changeable at runtime via an API — grant/revoke individual permissions per role)?
- **Answer:** Dynamic mapping — role->permission grants are stored (SQLite) and changeable at runtime (an admin can change which permissions a role has).
- **Date:** 2026-07-10
- **Status:** ANSWERED
- **Incorporated:** yes

## Q-68 — Unit of permission: feature-level vs. action-level granularity
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** user-roles-permissions, CROSS-CUTTING
- **Why needed:** The idea says "Permissions per feature/action" — ambiguous between per-feature (coarse: a role either has "filemanagement" or not) and per-action (fine: a role has `filemanagement.upload` but not `filemanagement.delete`). The unit determines the permission key format and whether fine-grained assignment is possible.
- **Context:** Existing features expose public service methods as their actions, e.g., `FileService.upload/download/open/delete/list_files/upload_avatar/...`, `UserManager.create_user/set_role/...`, `SessionService.list_sessions/revoke_session/revoke_all_sessions/...`, `SettingsRegistry.register/get_value/set_value/...`, `MailService.send_email/...`.
- **Question:** What is the unit of permission? (a) Per-feature only (one permission per feature), (b) per-action only (one permission per public method), or (c) hierarchical `feature.action` with feature-level wildcards (a role can hold `filemanagement.*` or individual `filemanagement.upload`)? Must a role be able to hold `filemanagement.upload` without `filemanagement.delete`?
- **Answer:** Hierarchical `feature.action` (e.g. "usermanagement.set_role"); action-level checks plus feature-level grants via wildcard ("settings.*").
- **Date:** 2026-07-10
- **Status:** ANSWERED
- **Incorporated:** yes

## Q-69 — Permission vocabulary: static vs. dynamic (custom permissions)
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** user-roles-permissions, CROSS-CUTTING
- **Why needed:** Independent of Q-67 (the mapping), the set of permissions itself could be static (a closed catalog defined in code at startup) or dynamic (DB-backed, creatable at runtime — e.g., an admin defines a new permission `reports.export` without a code change). Dynamic vocabulary adds a catalog table, creation/validation APIs, and a naming rule.
- **Context:** The idea mentions only "Permissions per feature/action" — no mention of creating custom permissions at runtime. All existing features are in-process services with no HTTP layer.
- **Question:** Is the permission vocabulary (a) static — a fixed catalog defined in code at startup (closed set; new permissions require a code change), or (b) dynamic — persisted and creatable at runtime (who may create permissions; what naming/validation rules, e.g., `^[a-z0-9_-]+\.[a-z0-9_-]+$`)?
- **Answer:** Static catalog — a fixed set of permission names derived from the features' declared actions; no runtime creation of permission names.
- **Date:** 2026-07-10
- **Status:** ANSWERED
- **Incorporated:** yes

## Q-70 — Initial permission catalog: which features and actions are covered
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** user-roles-permissions, CROSS-CUTTING
- **Why needed:** The spec must pin the initial permission catalog (which features' actions are gated). Candidate features with public actions: usermanagement (create_user, get_user, list_users, update_user, delete_user, change_password, verify_password, set_role, activate_user, deactivate_user), authentication (login, logout, session_info, password reset, passkey ops), settings (register, register_feature, get_value, set_value, reset, templates), filemanagement (upload, download, open, delete, get_file, list_files, avatar ops), mail (send_email, high-level sends), sessionmanagement (list_sessions, revoke_session, revoke_all_sessions, logout_all_sessions, logout_other_sessions, cleanup_expired). All public methods, or a curated subset (e.g., only mutating/admin operations)?
- **Context:** All six features above are implemented and merged in `src/backend/` (sessionmanagement verified implemented in this worktree's base). Each feature's public service methods are its natural action set.
- **Question:** Which features/actions are in the initial catalog? (a) All public methods of all six features, (b) a curated subset (which ones — e.g., only mutating operations, only admin-grade operations), or (c) a specific per-feature list? Are read operations (get/list) gated at all?
- **Answer:** All six features' public service methods (usermanagement, authentication, settings, filemanagement, mail, sessionmanagement); every public method is a declared action.
- **Date:** 2026-07-10
- **Status:** ANSWERED
- **Incorporated:** yes

## Q-71 — How features declare their actions to the permission feature
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** user-roles-permissions, CROSS-CUTTING
- **Why needed:** If the catalog is built from the features' actions (Q-70), the mechanism must be pinned: a module-level constant per feature, a startup registration call (like the feature-owned `register_settings(registry)` pattern), or auto-discovery (introspection of public methods). This determines whether existing feature packages are modified (cross-cutting impact) and how a new feature joins the catalog.
- **Context:** Repo pattern for feature-owned registration: each feature exposes `register_settings(registry)` in `feature_settings.py`, called at startup (logging, mail, filemanagement, settings, sessionmanagement). No feature currently declares "actions".
- **Question:** How does a feature declare its actions? (a) A module-level constant per feature (e.g., `ACTIONS: dict[str, str]` mapping permission key → description), (b) a startup registration call (feature-owned `register_actions(catalog)` in the feature, like `register_settings`), or (c) auto-discovery (introspection of the service's public methods)? Does the mechanism require modifying existing feature packages?
- **Answer:** Feature-owned registration (e.g. register_actions(...)) called at startup, mirroring the register_settings pattern.
- **Date:** 2026-07-10
- **Status:** ANSWERED
- **Incorporated:** yes

## Q-72 — Check API shape: decorator vs. explicit call; raise vs. bool
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** user-roles-permissions, CROSS-CUTTING
- **Why needed:** "Permission checks in the backend" needs a concrete API. Options: a decorator applied to service methods (`@requires_permission("feature.action")`), an explicit call (`check_permission(principal, "feature.action")`), or both. And the denial signal: raise an exception, return a bool, or both styles (`has_permission` → bool, `require_permission` → raise). This is the core public API of the new capability.
- **Context:** No existing check API in the repo. The repo pattern for cross-cutting function tracing is the `@logged`/`@logged_class` decorator (shared logging feature) — a decorator precedent exists. In-process trust model: existing features perform no per-call auth.
- **Question:** What is the check API? (a) A decorator `@requires_permission("feature.action")` for service methods, (b) an explicit call `check_permission(principal, "feature.action")` / `require_permission(...)`, or (c) both? And the denial signal: raise an exception, return a bool, or both styles (`has_permission` → bool + `require_permission` → raise)?
- **Answer:** Both — has_permission(user_id, permission) -> bool and require_permission(user_id, permission) that raises on denial.
- **Date:** 2026-07-10
- **Status:** ANSWERED
- **Incorporated:** yes

## Q-73 — Principal argument: user_id vs. session token vs. UserRead
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** user-roles-permissions, CROSS-CUTTING
- **Why needed:** A check needs a principal (who is asking). Options: `user_id: UUID` (the check looks up the user's role via user-management), `UserRead` (the caller passes the representation), or a session token (the check validates the session via authentication, then resolves the user). Note: `SessionInfo` carries only `user_id` (no role), so even token-based checks need a user lookup for the role. This determines the new feature's dependencies (user-management only, or also authentication).
- **Context:** user-management: `UserManager.get_user(user_id) -> UserRead` (carries `role`). authentication: `AuthService.session_info(token) -> SessionInfo(user_id, created_at, expires_at)` — no role; `LoginResult` carries `UserRead` (with role) at login.
- **Question:** What does the check take as the principal? (a) `user_id: UUID` (the check resolves the user via user-management), (b) `UserRead` (the caller passes it), (c) a session token (the check validates the session via authentication and resolves the user), or (d) a combination (e.g., `user_id` plus an optional token)? Which dependencies on existing features does this imply?
- **Answer:** user_id — check(user_id, permission) with a live user lookup.
- **Date:** 2026-07-10
- **Status:** ANSWERED
- **Incorporated:** yes

## Q-74 — Fail-open vs. fail-closed on undeterminable checks
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** user-roles-permissions, CROSS-CUTTING
- **Why needed:** Security posture: when a check cannot determine the outcome (user not found, lookup raises, the permission feature is not initialized, a permission is unknown), the default must be pinned. Fail-closed (deny) is the standard secure default; fail-open (allow) preserves availability. This is a hard invariant of the capability.
- **Context:** No existing check exists to reference. The repo's security posture is otherwise strict (tokens hashed at rest, no secrets in logs, argon2id).
- **Question:** When a check cannot determine the outcome (unknown user, lookup error, uninitialized feature, unknown permission), is the default (a) fail-closed — deny (raise the denial error), or (b) fail-open — allow? Is fail-closed a hard invariant for every undeterminable case?
- **Answer:** Fail-closed — undeterminable checks (unknown user, storage error, unmapped role) deny and log a warning.
- **Date:** 2026-07-10
- **Status:** ANSWERED
- **Incorporated:** yes

## Q-75 — Cross-cutting scope: does this change wire existing features to enforce checks?
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** user-roles-permissions, CROSS-CUTTING
- **Why needed:** This determines the size of the Impact Analysis and whether approved specs are amended. Option (a): the change provides only the shared permission capability (check API + role assignment + catalog) and leaves enforcement wiring to the caller (application code) — existing features are untouched except possibly declaring actions. Option (b): the change also modifies existing features (usermanagement, authentication, settings, filemanagement, mail, sessionmanagement) to enforce checks on their operations — a cross-feature change touching six implemented features and their approved specs (spec amendments required).
- **Context:** All six features are implemented and merged with approved specs and NFR-003 backward-compatibility contracts. The existing in-process trust model means none of them performs per-call auth today. session-management is a recently merged feature (admin operations like `revoke_all_sessions` are natural check targets).
- **Question:** Which option? (a) Provide only the shared permission capability (check API, role assignment, catalog); enforcement wiring stays the caller's responsibility; existing features are not modified to call checks (they may only declare actions). (b) Also modify existing features to enforce checks on their operations (cross-feature impact; the affected specs are amended via the Spec Amendment Workflow)? Which features, if (b)?
- **Answer:** Capability + enforcement — also wire existing features (usermanagement, sessionmanagement, settings, ...) to enforce checks at their entry points; requires spec amendments to those features (behavior changes).
- **Date:** 2026-07-10
- **Status:** ANSWERED
- **Incorporated:** yes

## Q-76 — Role assignment: reuse user-management's `set_role` or a new API?
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** user-roles-permissions, CROSS-CUTTING
- **Why needed:** The idea lists "Role assignment", but user-management already has `set_role(user_id, role) -> UserRead` (REQ-007) with validation (`InvalidRoleError`) and the last-admin guard. Re-specifying role assignment would be double work. The answer pins whether the new feature delegates to `set_role`, wraps it, or moves it.
- **Context:** `docs/specs/user-management.md`: REQ-007 (`set_role`), REQ-006 (role set validation), REQ-008 (last-admin guard on demote), AC-015/AC-016, EDGE-005 (set_role to same role is a no-op), `UserRoleChanged` event. The user-management spec's out-of-scope list excludes "permissions beyond roles" but NOT role assignment itself.
- **Question:** Does the new feature (a) reuse/delegate to `UserManager.set_role` (no new role-assignment API; the new feature never stores or mutates roles itself), (b) add its own role-assignment API on the permission service that calls `set_role` (a thin wrapper, possibly adding permission-related validation), or (c) replace `set_role` (role assignment moves into the permission feature)?
- **Answer:** Reuse UserManager.set_role (preserves the last-admin guard + UserRoleChanged event); no new assignment path.
- **Date:** 2026-07-10
- **Status:** ANSWERED
- **Incorporated:** yes

## Q-77 — Custom roles: is role CRUD (create/list/delete roles) in scope?
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** user-roles-permissions, CROSS-CUTTING
- **Why needed:** The existing role set is fixed at construction time (`UserManager(roles=(...))`, default `{"admin", "member"}`) — roles are not entities that can be created at runtime. "Roles such as Admin/User" might imply only those two, or it might imply custom roles (e.g., an `editor` role created at runtime with its own permission set). Custom roles add role CRUD APIs, a roles table (or extension of the role set), and guards (delete a role in use?).
- **Context:** user-management D3: roles are lowercase strings validated at construction; no role entity, no role CRUD. With a dynamic mapping (Q-67), a role's permissions live in the permission feature, but the role's existence/validation lives in user-management.
- **Question:** Are custom roles in scope — i.e., creating new roles at runtime (e.g., `editor`), listing roles, deleting roles, and updating a role's permission set? If yes: where do role CRUD APIs live (the permission feature or user-management), and what guards apply (e.g., deleting a role assigned to users)?
- **Answer:** Yes, role CRUD — role create/list/delete is in scope; roles become runtime-managed entities.
- **Date:** 2026-07-10
- **Status:** ANSWERED
- **Incorporated:** yes

## Q-78 — Multiple roles per user?
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** user-roles-permissions, CROSS-CUTTING
- **Why needed:** Currently a user has exactly one role (`User.role: str`). Multiple roles (a user is both `member` and `editor`, permissions = union) require a user-management schema change (`role: str` → `roles: list[str]`), a migration, and changes to `UserRead`, `set_role`, the last-admin guard, and events — a significant amendment to an approved spec. Single role keeps the existing schema.
- **Context:** `docs/specs/user-management.md`: `User.role: str` (single), `UserRead.role: str`, `set_role(user_id, role)`, `UserRoleChanged(old_role, new_role)`, REQ-008 last-admin guard keyed on the single role.
- **Question:** Does the new feature support multiple roles per user (permission set = union of the roles' permissions — requires a user-management schema change `role: str` → `roles: list[str]`), or does it stay single-role (one role per user, as today)?
- **Answer:** Multiple roles — a user can hold multiple roles simultaneously (union of permissions); requires a user-management schema change (role list) + migration + test updates.
- **Date:** 2026-07-10
- **Status:** ANSWERED
- **Incorporated:** yes

## Q-79 — Admin role semantics: implicit wildcard vs. explicit enumeration
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** user-roles-permissions, CROSS-CUTTING
- **Why needed:** "Admin" typically means full access. If admin is an implicit wildcard (holds every permission, including permissions added later without any update), new actions are automatically admin-accessible. If admin is explicit (enumerated like any other role), every new permission must be granted to admin explicitly — easy to forget. This is a core invariant of the model.
- **Context:** The idea says "Roles such as Admin/User" without defining admin's semantics. No existing permission model to reference.
- **Question:** Does the `admin` role implicitly hold all permissions (wildcard — including permissions added later, with no per-permission grant), or must `admin` be granted permissions explicitly like any other role? If wildcard: is the bypass rule "role == admin" or a named wildcard permission (e.g., `*`)?
- **Answer:** Implicit wildcard — the admin role implicitly grants ALL permissions, including any added later.
- **Date:** 2026-07-10
- **Status:** ANSWERED
- **Incorporated:** yes

## Q-80 — Default permissions of the non-admin role
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** user-roles-permissions, CROSS-CUTTING
- **Why needed:** The non-admin role ("user"/"member") needs a defined default permission set. Options: zero permissions (deny all — the role is inert until granted), read-only on some features (e.g., `*.get_*`/`*.list_*`), or a specific curated set. With a static mapping (Q-67) this is the fixed subset; with a dynamic mapping it is the initial grant.
- **Context:** The idea does not state what a regular user may do. Existing features are open in-process today (no gating), so any default set is new behavior.
- **Question:** What permissions does the non-admin role hold by default? (a) Zero (deny all until granted), (b) read-only on a defined set of features (which?), or (c) a specific curated set (list it)?
- **Answer:** Zero permissions — the non-admin (user) role starts with zero permissions; grants happen via the dynamic mapping.
- **Date:** 2026-07-10
- **Status:** ANSWERED
- **Incorporated:** yes

## Q-81 — Last-admin guard interaction
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** user-roles-permissions, CROSS-CUTTING
- **Why needed:** user-management REQ-008 rejects operations that would leave zero active admins (`LastAdminError` on delete/deactivate/demote). Any new role-assignment path in the permission feature must preserve this guard — either by delegating to `set_role` (which enforces it) or by re-implementing the guard. The spec must state which path enforces it and that no assignment path can bypass it.
- **Context:** `docs/specs/user-management.md`: REQ-008, AC-017/AC-018/AC-019, INV-003 (at least one active admin while `admin` is in the role set), `LastAdminError`.
- **Question:** Confirm: every role-assignment path (including any new API in the permission feature) preserves the last-admin guard — demoting/deactivating/deleting the last active admin raises `LastAdminError`. Is the guard enforced by delegation to `UserManager.set_role` (single enforcement point), or does the permission feature re-implement it?
- **Answer:** Guard always preserved — every role-assignment path preserves the last-admin guard (no bypass).
- **Date:** 2026-07-10
- **Status:** ANSWERED
- **Incorporated:** yes

## Q-82 — Interaction with authentication sessions: does a check validate the session?
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** user-roles-permissions, CROSS-CUTTING
- **Why needed:** If a check takes a session token (Q-73c), it must validate the session (unrevoked, unexpired) via authentication — making the permission feature depend on authentication's session store. If a check takes `user_id` only, session validity is the caller's concern (the caller already validated the token to get the user). This pins the dependency graph and whether a revoked session's user can still pass checks.
- **Context:** authentication: `session_info(token)` raises `InvalidSessionError` for unknown/revoked/expired tokens; `SessionInfo` has no role. The permission feature currently has no dependency on authentication.
- **Question:** Should a check validate the caller's session (token) via authentication (unrevoked + unexpired) as part of the check — implying a dependency on authentication's session repository — or are checks session-agnostic (`user_id`-based; session validity is the caller's responsibility, e.g., the HTTP/entry layer already validated the token)?
- **Answer:** Validate session too — a check also validates the session token; a revoked/expired session fails the check (coupling to authentication).
- **Date:** 2026-07-10
- **Status:** ANSWERED
- **Incorporated:** yes

## Q-83 — System / anonymous principals
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** user-roles-permissions, CROSS-CUTTING
- **Why needed:** In-process services are sometimes called without a user (startup wiring, background work, service-to-service). The check API must define what happens for a non-user principal: `user_id=None` (system), an anonymous principal, or reject. If system principals are supported, their permission set (all? none? a named `system` role?) must be pinned.
- **Context:** Existing features are called in-process with no caller identity (in-process trust model). Features like the event bus and settings are used at startup before any user context exists.
- **Question:** Are non-user principals in scope — e.g., a system/service principal (`user_id=None`) or an anonymous principal? If yes: what permissions do they hold (all — like a trusted system; none — deny; or a named `system`/`service` role with a defined set)? If no: does a check with `user_id=None` deny (fail-closed)?
- **Answer:** Configurable system principal — in scope; system/anonymous principals (e.g. background workers) have configurable permissions.
- **Date:** 2026-07-10
- **Status:** ANSWERED
- **Incorporated:** yes

## Q-84 — Caching of permission decisions
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** user-roles-permissions, CROSS-CUTTING
- **Why needed:** Checks may run on hot paths (every gated operation). Options: fresh lookup per check (always current, one user read per check) or cache the resolved permission set per `user_id` (fast, but must be invalidated on `UserRoleChanged`/role-set changes to avoid stale grants). Caching affects the latency NFR and the invalidation event subscription.
- **Context:** user-management publishes `UserRoleChanged(user_id, old_role, new_role)` on `set_role`. The shared event bus supports subscriptions. No existing feature caches lookups.
- **Question:** Should resolved permission sets be cached (per `user_id`, invalidated on `UserRoleChanged` and role-mapping changes), or is every check a fresh lookup (always current, no cache)? If cached: what is the invalidation trigger set, and is a stale-grant window acceptable?
- **Answer:** No cache — live lookup on each check (fresh data, immediate effect, no invalidation bugs).
- **Date:** 2026-07-10
- **Status:** ANSWERED
- **Incorporated:** yes

## Q-85 — Inactive users: does a check deny them?
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** user-roles-permissions, CROSS-CUTTING
- **Why needed:** A deactivated user (`is_active=False`) still has a role. Authentication's `login` rejects inactive users, but user-management reads do not check activity. If a check does not deny inactive users, a deactivated user's `user_id` could still pass permission checks in-process. The behavior must be pinned.
- **Context:** user-management: `User.is_active` flag, `deactivate_user` (REQ-009); `get_user` does not filter on activity. authentication: login raises `InvalidCredentialsError` for inactive users (REQ-003/EDGE-002).
- **Question:** Does a check deny when the user is inactive (`is_active=False`)? (a) Yes — inactive users pass no checks, (b) No — activity is the caller's concern (the check only evaluates role→permissions)?
- **Answer:** Deny — a check for an inactive (deactivated) user denies all permissions.
- **Date:** 2026-07-10
- **Status:** ANSWERED
- **Incorporated:** yes

## Q-86 — Immediate effect of role changes (live lookup vs. session-bound)
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** user-roles-permissions, CROSS-CUTTING
- **Why needed:** When a user's role is changed (e.g., demoted from admin to member), do permission checks reflect it immediately (live lookup per check — the demoted user loses access at the next check), or do the old permissions stay in effect until the next login/session refresh? Immediate effect is the secure default; session-bound effect would require storing permissions on the session.
- **Context:** Sessions (authentication) store no role/permission data — only `user_id` and timestamps. A live lookup is the natural design given the current schema.
- **Question:** When a user's role changes, do permission checks reflect it immediately (live lookup per check — no session refresh needed), or do the old permissions stay in effect until the next login? (Given sessions store no role data, immediate live lookup is the natural default.)
- **Answer:** Immediate — changes take effect on the next check (live lookup); no re-login needed.
- **Date:** 2026-07-10
- **Status:** ANSWERED
- **Incorporated:** yes

## Q-87 — Storage: tables and repository ABCs
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** user-roles-permissions, CROSS-CUTTING
- **Why needed:** If the mapping/vocabulary is dynamic (Q-67/Q-69), the spec must pin the persistence: SQLite tables (e.g., `permissions` catalog, `role_permissions` mapping) behind a repository ABC (repo pattern), sharing the same SQLite database as user-management/authentication. If static, there is no storage — confirm. Table fields, indexes, and the repository ABC methods must be specified.
- **Context:** Repo pattern: SQLModel/SQLite behind a repository ABC, constructor injection, `create_all` bootstrap (no migration framework), thread-safe SQLite (user-management, authentication, file-management, session-management). The permission feature would share the same database file.
- **Question:** If dynamic (Q-67/Q-69): which tables and fields (e.g., `permissions(key PK, description, created_at)`, `role_permissions(role, permission, PK(role,permission))`), and which repository ABC methods? If static: confirm no storage (the catalog and mapping live in code/constructor args only)?
- **Answer:** SQLite + repository ABCs — roles (CRUD), role->permission grants, system-principal config; alembic migration for the new tables.
- **Date:** 2026-07-10
- **Status:** ANSWERED
- **Incorporated:** yes

## Q-88 — Settings registry integration
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** user-roles-permissions, CROSS-CUTTING
- **Why needed:** Configurable values should use the shared settings registry (repo pattern: feature-owned `register_settings(registry)`, live reads — logging, mail, filemanagement, settings, sessionmanagement all do this). Candidates: the role→permission mapping (as a LIST setting), a fail-open/fail-closed flag, the permission catalog (dynamic), or nothing (constructor args only). This pins which values are live-configurable.
- **Context:** The settings registry supports TEXT/NUMBER/BOOLEAN/EMAIL/SLIDER/SELECT/LIST kinds with live reads and per-kind validation. Feature-owned registration is the established pattern (`feature_settings.py` + `register_settings(registry)`).
- **Question:** Which values should this feature register via the settings registry (read live)? Candidates: role→permission mapping (LIST), fail-closed flag (BOOLEAN), catalog (if dynamic), check-latency thresholds. Or: nothing — constructor args only? Which keys, and what defaults?
- **Answer:** Integrate — feature-owned register_settings(registry) called at startup; live reads (repo convention).
- **Date:** 2026-07-10
- **Status:** ANSWERED
- **Incorporated:** yes

## Q-89 — Events published by the permission feature
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** user-roles-permissions, CROSS-CUTTING
- **Why needed:** Per the repo pattern, features publish typed lifecycle events to an injected `EventPublisher` (structural protocol), non-sensitive data only. The event set must be pinned: denial events (audit signal), grant/revoke events (if dynamic mapping), and whether role assignment reuses user-management's `UserRoleChanged` or publishes a new event. Read operations (successful checks) are typically not events.
- **Context:** user-management publishes `UserRoleChanged(user_id, old_role, new_role)` on `set_role`. Other features publish 6–8 event types each. Events carry non-sensitive data only (repo invariant).
- **Question:** Which events should the permission feature publish? Candidates: `PermissionDenied(user_id, permission, occurred_at)`, `PermissionGranted(role, permission)` / `PermissionRevoked(role, permission)` (if dynamic mapping), and a role-assignment event (reuse `UserRoleChanged` or new `RoleAssigned`?). Is a successful check an event (probably not)? Non-sensitive data only?
- **Answer:** Denied + role events — PermissionDenied, RoleCreated/RoleDeleted/RolePermissionsChanged; role assignment reuses user-management's UserRoleChanged.
- **Date:** 2026-07-10
- **Status:** ANSWERED
- **Incorporated:** yes

## Q-90 — Error taxonomy and naming
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** user-roles-permissions, CROSS-CUTTING
- **Why needed:** The spec needs a structured exception hierarchy (repo pattern: root error with documented context attributes). Naming matters: Python's built-in `PermissionError` exists (OS-level), so the root should not shadow/confuse it. Candidates: root `AuthorizationError` (or `PermissionError`), `PermissionDeniedError(user_id, permission)`, `UnknownPermissionError(permission)`, `UnknownRoleError(role)`. Context attributes must be pinned.
- **Context:** Repo pattern: `UserManagerError` root (user-management), `AuthenticationError` root (authentication), `FileManagementError` root (file-management), `SessionManagementError`-style (session-management). All carry context attributes; messages are secret-free.
- **Question:** Confirm the exception hierarchy. Proposed: root `AuthorizationError` (avoiding shadowing the built-in `PermissionError`); `PermissionDeniedError(AuthorizationError)` with `user_id`, `permission`; `UnknownPermissionError(AuthorizationError)` with `permission`; `UnknownRoleError(AuthorizationError)` with `role`, `allowed`. Different root name (e.g., `PermissionError`) or different classes/context?
- **Answer:** Custom AuthorizationError hierarchy (backend.permissions.errors): PermissionDeniedError (context: user_id, permission, reason) + role errors; avoids colliding with the built-in PermissionError.
- **Date:** 2026-07-10
- **Status:** ANSWERED
- **Incorporated:** yes

## Q-91 — Audit log scope
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** user-roles-permissions, CROSS-CUTTING
- **Why needed:** user-management and authentication both list "persistent audit log" as explicitly out of scope. Permission denials are a classic audit target. The scope must be pinned: (a) no persistent audit — denials are logged (loguru WARNING) and published as events (Q-89) only; (b) a persistent audit log of checks (allow/deny rows in SQLite) — new storage + retention questions. This is a significant scope fork.
- **Context:** user-management Out of Scope: "persistent audit log". authentication Out of Scope: "persistent audit log". The logging feature (loguru) provides transient logs; no feature persists an audit trail today.
- **Question:** Is a persistent audit log of permission checks (allow/deny, user, permission, timestamp) in scope for this feature? (a) No — denials are logged transiently (loguru) and published as events only, consistent with the existing out-of-scope lists; (b) Yes — a persistent SQLite audit log (then: which events are audited — denials only, or allows too; retention/rotation; size limits)?
- **Answer:** Logs + events only — no persistent audit table.
- **Date:** 2026-07-10
- **Status:** ANSWERED
- **Incorporated:** yes

## Q-92 — Performance budgets (check latency)
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** user-roles-permissions, CROSS-CUTTING
- **Why needed:** Testable performance budgets are needed (repo pattern: budgets in contract tests, measured including the mandated logging overhead, with the logging context stated). Checks may run on hot paths, so the budget is a core NFR. Values depend on static vs. dynamic (Q-67) and caching (Q-84).
- **Context:** Repo pattern: user-management NFR-001 (reads < 5 ms median on SQLite), session-management NFR (p95 budgets, local SQLite, INFO console sink). The logging policy mandates `@logged` tracing on public methods.
- **Question:** What are the performance budgets? Proposed (static, no cache): a check completes in < 1 ms (median) in-process including `@logged` tracing overhead; with a dynamic SQLite-backed mapping: < 5 ms (median) — all measured on local hardware against a local SQLite database with the shared logging feature at default INFO level with a synchronous console sink. Different values?
- **Answer:** A check completes in < 5 ms INCLUDING user/role/grant SQLite lookups + @logged tracing overhead; measured with the synchronous console sink active.
- **Date:** 2026-07-10
- **Status:** ANSWERED
- **Incorporated:** yes

## Q-93 — Feature/package/service naming
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** user-roles-permissions, CROSS-CUTTING
- **Why needed:** The package name, service name, and check-function names must be pinned for the spec (and for the AGENTS.md "Using the X Feature" note). Options: `backend.permissions` vs. `backend.authorization`; `PermissionService` vs. `AuthorizationService`; `require_permission`/`has_permission` vs. `check_permission`.
- **Context:** Existing packages: `backend.usermanagement` (`UserManager`), `backend.authentication` (`AuthService`), `backend.filemanagement` (`FileService`), `backend.sessionmanagement` (`SessionService`), `backend.settings`, `backend.mail`, `backend.logging`, `backend.eventbus`.
- **Question:** Approve the proposed naming? Package `backend.permissions`; service `PermissionService`; check functions `require_permission(principal, permission)` (raises) and `has_permission(principal, permission) -> bool`; decorator `@requires_permission(permission)`. Or prefer `backend.authorization` / `AuthorizationService` / other names?
- **Answer:** backend.permissions / PermissionService / require_permission + has_permission.
- **Date:** 2026-07-10
- **Status:** ANSWERED
- **Incorporated:** yes

## Q-94 — Unknown permission / unmapped role behavior
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** user-roles-permissions, CROSS-CUTTING
- **Why needed:** Edge behaviors must be pinned (they become EDGE cases): (a) code checks a permission that is not in the catalog → deny + WARNING log? raise `UnknownPermissionError`? (b) a role's mapping references an unknown action → ignore? (c) a user's role has no mapping at all → zero permissions (deny all)? Each is a distinct observable behavior.
- **Context:** No existing permission model to reference. The fail-closed default (Q-74) covers undeterminable checks; these are determinable-but-inconsistent states that need explicit behavior.
- **Question:** Pin the behaviors: (a) checking a permission not in the catalog → (deny + WARNING log) or (raise `UnknownPermissionError`)? (b) a role mapping that references an unknown action → ignore that entry? (c) a user whose role has no permission mapping → zero permissions (deny all)?
- **Answer:** Deny + warn — an unknown permission or a role with no permission mapping denies and logs a warning.
- **Date:** 2026-07-10
- **Status:** ANSWERED
- **Incorporated:** yes

## Q-95 — Out-of-scope boundaries
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** user-roles-permissions, CROSS-CUTTING
- **Why needed:** The idea is a four-bullet list; common authorization capabilities are not mentioned. Explicit boundaries are needed so the spec does not accidentally cover them: frontend UI for role/permission assignment, HTTP/REST layer, multi-tenancy, MFA, JWT, groups/teams (vs. roles), per-user (non-role) permission grants (a direct user→permission grant bypassing roles), persistent audit log (see Q-91), and RBAC beyond roles (ABAC/policy engines).
- **Context:** All existing features are backend-only in-process services (no HTTP layer, no frontend). user-management lists "user groups/teams/permissions beyond roles" as out of scope. The repo has no policy-engine or ABAC capability.
- **Question:** Confirm out of scope for this change: frontend UI, HTTP/REST layer, multi-tenancy, MFA, JWT, groups/teams, per-user (non-role) permission grants (direct user→permission grants bypassing roles), and policy-engine/ABAC (only RBAC: roles→permissions). Is anything in that list actually in scope?
- **Answer:** Confirm the proposed list: frontend UI, HTTP/REST layer, multi-tenancy, MFA, JWT, groups/teams, per-user (non-role) permission grants, ABAC/policy engines.
- **Date:** 2026-07-10
- **Status:** ANSWERED
- **Incorporated:** yes

## Q-96 — DI and testing conventions
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** user-roles-permissions, CROSS-CUTTING
- **Why needed:** The spec must pin the construction/testing pattern. The repo pattern is constructor injection of repository ABCs + `UserManager` + optional structural `EventPublisher`, in-memory fakes for tests. session-management added a module-level singleton (`get_session_service()`) on top of constructor DI. Whether this feature follows the same, or also exposes a singleton (and how it is reset in tests), must be pinned.
- **Context:** `AuthService`, `UserManager`, `FileService`, `SessionService` all use constructor DI with repository ABCs and optional event publishers; tests use in-memory/temp-directory fakes. session-management: constructor DI PLUS a module singleton for application use.
- **Question:** Confirm: `PermissionService` constructed with the repository ABC(s) + `UserManager` + optional `event_bus` (structural `publish` protocol), an in-memory repository for tests/DI, and (like session-management) a module-level singleton (e.g., `get_permission_service()`) with a reset function for tests? Or no singleton (pure constructor DI)?
- **Answer:** Repo conventions — constructor DI, in-memory repositories for tests, module singleton + reset pattern.
- **Date:** 2026-07-10
- **Status:** ANSWERED
- **Incorporated:** yes

## Q-97 — Backward compatibility: additive only
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** user-roles-permissions, CROSS-CUTTING
- **Why needed:** user-management (NFR-003), authentication (NFR-003), and the other features have backward-compatibility contracts on their public APIs. The new capability must not break existing callers: no signature changes, no behavior changes in existing features (unless Q-75 option (b) is chosen), no removals. This is a hard constraint on the change.
- **Context:** user-management NFR-003: "The public API ... is backward-compatible; adding optional parameters must not break existing callers." Same for authentication NFR-003. Existing features perform no per-call auth (in-process trust model).
- **Question:** Confirm: no changes to existing public APIs of user-management/authentication/settings/filemanagement/mail/sessionmanagement (additive only; optional parameters at most); no existing behavior changes beyond what Q-75 authorizes. Is this a hard constraint?
- **Answer:** Breaking changes to existing public APIs are allowed, BUT every break must be fixed within the current scope of this change (all dependent APIs, tests, and features updated as part of this change).
- **Date:** 2026-07-10
- **Status:** ANSWERED
- **Incorporated:** yes

## Q-98 — Thread safety
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** user-roles-permissions, CROSS-CUTTING
- **Why needed:** Checks may run from multiple threads (the repo's SQLite repositories are thread-safe; the settings registry and event bus are thread-safe). The permission feature's check path, cache (Q-84), and repositories must be safe for concurrent use. This is an NFR consistent with the repo pattern.
- **Context:** Repo pattern: SQLite repositories are thread-safe (user-management NFR-004: "safe for concurrent use from multiple threads"); the settings registry and event bus are thread-safe.
- **Question:** Confirm: the check path, any cache, and the repositories are safe for concurrent use from multiple threads (repo pattern: thread-safe SQLite, no partial state on concurrent reads/writes)?
- **Answer:** Thread-safe — the check path, repositories, and internal state are thread-safe.
- **Date:** 2026-07-10
- **Status:** ANSWERED
- **Incorporated:** yes

## Q-99 — Pre-approval of the spec PR (user governance directive)
- **Step:** S1.4 Present for approval — Phase 1
- **Change:** user-roles-permissions, CROSS-CUTTING
- **Why needed:** The user is going to bed and pre-approves the spec PR without merging it. This is a governance decision that changes the normal "present and STOP" behavior: the spec is treated as HUMAN APPROVED, but the PR must NOT be merged (human governance is preserved for the merge).
- **Context:** Per the Spec Approval Gate, a spec is HUMAN APPROVED only when merged through the GitHub review process, and the Phase 2 entry gate is the merge itself (`git log main -- docs/specs/[name].md` must be non-empty). The user is pre-approving the spec in advance (going to bed) and explicitly forbids the merge. So the spec is treated as HUMAN APPROVED, but because it is not merged, the Phase 2 entry gate is NOT yet satisfied — Phase 2 (Decompose) waits until the user merges the spec PR.
- **Question:** Confirm: treat the spec PR as HUMAN APPROVED (pre-approved) but do NOT merge it (leave the PR open for the user to merge), and stop after Phase 1 because Phase 2 is gated on the merge?
- **Answer:** Yes — the user pre-approves the spec PR (going to bed) and instructs NOT to merge it. The spec is treated as HUMAN APPROVED, and the spec PR is approved (not merged) per the directive. Because the Phase 2 entry gate is the merge itself, Phase 2 (Decompose) waits until the user merges the spec PR. The workflow stops after Phase 1 (spec PR open + approved, unmerged).
- **Date:** 2026-07-10
- **Status:** ANSWERED
- **Incorporated:** yes
