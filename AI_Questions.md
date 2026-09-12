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
- **Answer:** PENDING
- **Date:** 2026-09-13
- **Status:** PENDING
- **Incorporated:** no

## Q-2 — Avatar ↔ user-management integration boundary
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** file-management, FEATURE
- **Why needed:** "User avatars" attach to user-management users (`profile_picture_url` field, http/https only). It is unclear whether file-management itself updates the user record and cleans up on user deletion, or merely returns a URL/key for the caller to wire. This decides cross-feature dependencies and whether the change is truly a single FEATURE (not CROSS-CUTTING).
- **Context:** user-management spec: `User.profile_picture_url` (URL reference only; upload/storage explicitly out of scope for user-management); `update_user` can set `profile_picture_url`; `UserDeleted`/`UserDeactivated` events are published on deletion/deactivation.
- **Question:** When an avatar is uploaded/replaced/deleted, does file-management itself call `UserManager.update_user(user_id, UserUpdate(profile_picture_url=...))` (and subscribe to `UserDeleted` to clean up avatar files)? Or does it return the avatar URL/key and the caller (application wiring) handles user-management? Should file-management depend on the usermanagement feature at all?
- **Answer:** PENDING
- **Date:** 2026-09-13
- **Status:** PENDING
- **Incorporated:** no

## Q-3 — Image processing in scope (Pillow, thumbnails)
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** file-management, FEATURE
- **Why needed:** Avatar features commonly require resizing/thumbnail generation (e.g., 64px/256px variants), which adds a Pillow dependency, image-decode validation, and multiple stored variants per upload. The idea does not mention it.
- **Context:** No Pillow in `pyproject.toml`; "user avatars" is the only image-specific bullet in the idea.
- **Question:** Is image processing in scope — e.g., generating resized avatar variants (thumbnails) with Pillow? If yes: which sizes, and are variants stored as separate files? If no: are avatars stored as raw uploads only?
- **Answer:** PENDING
- **Date:** 2026-09-13
- **Status:** PENDING
- **Incorporated:** no

## Q-4 — Out-of-scope confirmations
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** file-management, FEATURE
- **Why needed:** The idea is a bullet list; common file-management capabilities (virus scanning, content deduplication, file versioning, retention/expiration, sharing/permissions, frontend UI) are not mentioned. Explicit boundaries are needed so the spec does not accidentally cover them.
- **Context:** No antivirus/dedup/versioning/retention capability exists in the repo; the idea lists only upload/download, user avatars, file metadata, storage abstraction, size/type validation.
- **Question:** Confirm out of scope for this change: virus scanning, content deduplication, file versioning, retention/expiration (auto-cleanup), sharing/permission grants, and any frontend UI. Is anything in that list actually in scope?
- **Answer:** PENDING
- **Date:** 2026-09-13
- **Status:** PENDING
- **Incorporated:** no

## Q-5 — Storage backends
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** file-management, FEATURE
- **Why needed:** "Storage abstraction" implies a backend interface, but which backends are normative is unclear. Local disk only, or also S3-compatible (boto3)? S3 adds a major dependency and cloud semantics.
- **Context:** No boto3 in `pyproject.toml`; all existing features use local disk (SQLite files, YAML files) or in-memory storage.
- **Question:** Which storage backends must the spec cover: (a) local disk only (plus in-memory for tests), (b) local disk + S3-compatible (boto3) behind the same interface, or (c) other? Is the interface identical across backends (put/get/delete/exists/stat)?
- **Answer:** PENDING
- **Date:** 2026-09-13
- **Status:** PENDING
- **Incorporated:** no

## Q-6 — Object store (flat keys) vs. path store (directories)
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** file-management, FEATURE
- **Why needed:** Determines the core data model: flat opaque keys (object store, no directories) vs. hierarchical paths with folders. Affects the API (key vs. path), validation (path traversal), and list semantics.
- **Context:** The idea lists "storage abstraction" and "file metadata" but no folders/directories.
- **Question:** Is the store flat (opaque keys, object-store style) or hierarchical (paths with directories/folders)? Are "folders" part of the public API?
- **Answer:** PENDING
- **Date:** 2026-09-13
- **Status:** PENDING
- **Incorporated:** no

## Q-7 — Default storage root + in-memory test backend
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** file-management, FEATURE
- **Why needed:** The local backend needs a default root directory, and the backend must be swappable for tests (like `MemoryValueRepository`). The default location affects deployment and test isolation.
- **Context:** Existing features: SQLite DB paths are constructor args; settings values persist under a `settings` directory; tests use temp directories.
- **Question:** What is the default storage root directory for the local backend (e.g., `./data/files`)? Should an in-memory storage backend be part of the public API for tests/DI?
- **Answer:** PENDING
- **Date:** 2026-09-13
- **Status:** PENDING
- **Incorporated:** no

## Q-8 — Upload input shape
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** file-management, FEATURE
- **Why needed:** In-process upload could take an existing file path, raw bytes, or a file-like stream. Each has different validation (size pre-check via `stat` vs. `len` vs. streaming) and a different API surface.
- **Context:** The idea says only "upload/download"; no existing upload capability in the repo.
- **Question:** What input shape(s) should `upload` accept: existing file path, raw bytes, file-like stream (or all of them)? Should the read be streamed (chunked) or whole-file?
- **Answer:** PENDING
- **Date:** 2026-09-13
- **Status:** PENDING
- **Incorporated:** no

## Q-9 — Size limits
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** file-management, FEATURE
- **Why needed:** "Size validation" is in the idea, but the values, scope (general vs. avatar), and enforcement point (pre-write via `stat` vs. mid-stream) are unspecified. Limits should likely be configurable via the settings registry.
- **Context:** The settings registry supports NUMBER/SLIDER kinds with live reads (mail-service pattern); no existing size limits in the repo.
- **Question:** What are the max file sizes — for general uploads and for avatars (defaults, e.g., 100 MB / 5 MB)? Should limits be configurable via the settings registry (read live)? Are zero-byte files rejected (minimum size)?
- **Answer:** PENDING
- **Date:** 2026-09-13
- **Status:** PENDING
- **Incorporated:** no

## Q-10 — Concurrent uploads to the same key
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** file-management, FEATURE
- **Why needed:** Two threads uploading the same key concurrently could race (partial overwrite). The spec must state the behavior: last-write-wins, per-key locking (one fails), or undefined.
- **Context:** Existing features are thread-safe (settings registry, event bus, SQLite repositories); no precedent for same-key write races.
- **Question:** What should happen when two uploads target the same key concurrently: last-write-wins (atomic replacement), per-key locking (one fails), or undefined?
- **Answer:** PENDING
- **Date:** 2026-09-13
- **Status:** PENDING
- **Incorporated:** no

## Q-11 — Atomicity / no partial state
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** file-management, FEATURE
- **Why needed:** A failed or interrupted upload (validation failure mid-write, disk full, backend error) must not leave partial files or orphaned metadata. The spec needs a hard invariant: temp file + atomic rename, and rollback between the metadata record and the storage write.
- **Context:** Settings YAML repository uses atomic writes; user-management NFR-004: "a failed operation leaves no partial state".
- **Question:** Confirm: a failed/interrupted upload leaves no partial state (temp file + atomic rename; if the storage write fails, the metadata record is rolled back, and vice versa). Is this a hard invariant?
- **Answer:** PENDING
- **Date:** 2026-09-13
- **Status:** PENDING
- **Incorporated:** no

## Q-12 — Type detection method
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** file-management, FEATURE
- **Why needed:** "Type validation" needs a detection method: declared content-type, file extension, magic-byte sniffing (python-magic dependency), or image decode. Conflicting signals (`.png` extension but JPEG content) need a precedence rule.
- **Context:** No python-magic/Pillow in `pyproject.toml`; user-management validates `profile_picture_url` by scheme only.
- **Question:** How should file type be determined: declared MIME type, file extension, magic-byte sniffing (adds a python-magic dependency), or image decode? When signals conflict, which wins (e.g., `.png` name but JPEG content)? Should a mismatch be rejected?
- **Answer:** PENDING
- **Date:** 2026-09-13
- **Status:** PENDING
- **Incorporated:** no

## Q-13 — Allowed-type policy
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** file-management, FEATURE
- **Why needed:** "Size/type validation" implies an allowed-type policy, but the unit (MIME vs. extension) and scope (global whitelist vs. per-kind, e.g., avatars: images only) are unspecified.
- **Context:** No existing type whitelist in the repo.
- **Question:** What is the allowed-type policy: a global allowed-types list, per-kind lists (e.g., avatars restricted to image/png, image/jpeg, image/webp), or both? Is the policy unit MIME type or extension? Should it be configurable via the settings registry?
- **Answer:** PENDING
- **Date:** 2026-09-13
- **Status:** PENDING
- **Incorporated:** no

## Q-14 — Metadata fields
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** file-management, FEATURE
- **Why needed:** "File metadata" is in the idea, but the normative field set is unspecified. The fields (id, key, original filename, declared + detected MIME, size, content hash, namespace, uploader reference, created/updated timestamps, tags) and whether SHA-256 content hashing is required (integrity, future dedup) must be pinned.
- **Context:** user-management's `User` table shows the repo pattern (SQLModel, UUID id, UTC timestamps).
- **Question:** Which metadata fields are normative? Proposed: id, key, original filename, declared MIME, detected MIME, size (bytes), SHA-256 content hash, namespace, uploader reference, created/updated timestamps. Is content hashing (SHA-256) required? Any additional fields (tags, owner)?
- **Answer:** PENDING
- **Date:** 2026-09-13
- **Status:** PENDING
- **Incorporated:** no

## Q-15 — Metadata persistence
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** file-management, FEATURE
- **Why needed:** Metadata must be durable (survive restarts) and swappable (repository pattern), consistent with user-management (SQLite/SQLModel behind an ABC). In-memory (like the settings registry) is an alternative with different durability semantics.
- **Context:** user-management: `UserRepository` ABC + `SqliteUserRepository`; settings: in-memory registry with a YAML template repository.
- **Question:** Should file metadata be persisted in SQLite/SQLModel behind a repository ABC (like user-management), or in-memory (like the settings registry)?
- **Answer:** PENDING
- **Date:** 2026-09-13
- **Status:** PENDING
- **Incorporated:** no

## Q-16 — List/query API
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** file-management, FEATURE
- **Why needed:** "File metadata" implies queryability, but the API shape is unspecified: list by namespace/prefix, lookup by key, search by original filename, pagination.
- **Context:** user-management has `list_users(include_inactive)`; no pagination anywhere in the repo.
- **Question:** What list/query API is needed: list by namespace/prefix, lookup by key, search by original filename? Is pagination needed?
- **Answer:** PENDING
- **Date:** 2026-09-13
- **Status:** PENDING
- **Incorporated:** no

## Q-17 — Avatar lifecycle semantics
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** file-management, FEATURE
- **Why needed:** "User avatars" needs precise upload/replace/delete semantics: is replacing an avatar atomic (new file stored, then the user's URL swapped)? Is deleting the only avatar different from deleting a subsequent one? Any guards (like last-admin)?
- **Context:** user-management's last-admin guard shows the repo pattern for protective rules; avatars are per-user.
- **Question:** Avatar lifecycle: upload (first), replace (second and later), delete. Is replace atomic (new file stored, then the user's URL swapped)? Is deleting the only avatar different from deleting a subsequent one (e.g., revert to a default)? Any guards?
- **Answer:** PENDING
- **Date:** 2026-09-13
- **Status:** PENDING
- **Incorporated:** no

## Q-18 — Avatar URL format
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** file-management, FEATURE
- **Why needed:** Cross-feature contract conflict: user-management validates `profile_picture_url` as starting with `http://` or `https://`, but this feature has no HTTP layer (per the repo pattern). The avatar URL file-management produces must satisfy user-management's validation.
- **Context:** user-management AC-007: a `ftp://` profile picture URL is rejected; only http(s) is allowed.
- **Question:** With no HTTP layer, what URL does an avatar get? E.g., a stable pattern like `https://<base>/files/<file_id>` with a configurable base URL? Or should user-management's URL validation be extended (spec amendment)?
- **Answer:** PENDING
- **Date:** 2026-09-13
- **Status:** PENDING
- **Incorporated:** no

## Q-19 — Avatar constraints
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** file-management, FEATURE
- **Why needed:** Avatars need their own constraints (max size, allowed image types, max dimensions) and possibly per-user quotas (file count / total size).
- **Context:** No existing avatar constraints in the repo.
- **Question:** What are the avatar constraints: max size (default?), allowed image types (png/jpeg/webp?), max dimensions? Are there per-user quotas (file count / total size)?
- **Answer:** PENDING
- **Date:** 2026-09-13
- **Status:** PENDING
- **Incorporated:** no

## Q-20 — Avatar cleanup on user deletion + default avatar
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** file-management, FEATURE
- **Why needed:** When a user is deleted, their avatar files should be cleaned up (else orphaned). When a user is deactivated, is the avatar kept? Is there a "default avatar" fallback when none is set?
- **Context:** user-management publishes `UserDeleted`/`UserDeactivated` events; deletion is a hard delete of the user record.
- **Question:** When a user is deleted, are their avatar files also deleted (file-management subscribes to `UserDeleted`)? When a user is deactivated, is the avatar kept? Is there a "default avatar" fallback when no avatar is set?
- **Answer:** PENDING
- **Date:** 2026-09-13
- **Status:** PENDING
- **Incorporated:** no

## Q-21 — Download output shape
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** file-management, FEATURE
- **Why needed:** "Download" needs an output shape: return bytes, return a stream, or write to a destination path. And the error for a missing file. Range/partial download is likely out of scope.
- **Context:** No existing download capability in the repo.
- **Question:** What output shape should `download` have: return bytes, return a file-like stream, write to a destination path (or all of them)? What error for a missing file? Is range/partial download out of scope?
- **Answer:** PENDING
- **Date:** 2026-09-13
- **Status:** PENDING
- **Incorporated:** no

## Q-22 — Download access control
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** file-management, FEATURE
- **Why needed:** In-process downloads could be open to any caller (in-process trust model) or gated by owner reference/role/session (authentication integration). The idea does not specify.
- **Context:** The authentication feature provides sessions/tokens; user-management has roles; the in-process trust model is consistent with existing features (no per-call auth).
- **Question:** Are downloads open to any in-process caller (consistent with existing features), or gated (owner reference, role, session token via the authentication feature)?
- **Answer:** PENDING
- **Date:** 2026-09-13
- **Status:** PENDING
- **Incorporated:** no

## Q-23 — Events
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** file-management, FEATURE
- **Why needed:** Per the repo pattern, features publish typed lifecycle events to the shared event bus. The event set must be pinned (FileUploaded, FileDownloaded, FileDeleted, FileValidationFailed, AvatarUploaded, AvatarDeleted), and events must carry non-sensitive data only.
- **Context:** user-management publishes 7 event types; settings publishes `SettingChanged`; the event bus is the shared mechanism.
- **Question:** Which typed events should file-management publish to the shared event bus? Proposed: FileUploaded, FileDownloaded, FileDeleted, FileValidationFailed, AvatarUploaded, AvatarDeleted. Do events carry non-sensitive data only (no content, no secrets)?
- **Answer:** PENDING
- **Date:** 2026-09-13
- **Status:** PENDING
- **Incorporated:** no

## Q-24 — Error taxonomy
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** file-management, FEATURE
- **Why needed:** The spec needs a structured exception hierarchy (repo pattern: root error with documented context attributes). The classes and context must be confirmed.
- **Context:** user-management: `UserManagerError` root with context attributes; settings: `SettingsError` hierarchy; mail: `MailError` hierarchy.
- **Question:** Confirm the exception hierarchy rooted at `FileManagementError`: `FileNotFoundError`, `FileTooLargeError`, `FileTypeNotAllowedError`, `FileValidationError`, `StorageError`, `AvatarError` (plus avatar-specific). Do validation errors carry context (key, actual vs. limit/allowed)?
- **Answer:** PENDING
- **Date:** 2026-09-13
- **Status:** PENDING
- **Incorporated:** no

## Q-25 — NFR performance budgets
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** file-management, FEATURE
- **Why needed:** Testable performance budgets are needed (repo pattern: median budgets in contract tests), including the mandated logging overhead.
- **Context:** user-management NFR-001 (reads < 5 ms, create < 1 s); settings NFR-001 (per-op budgets); the logging policy mandates `@logged` tracing on all public methods.
- **Question:** What are the performance budgets? Proposed: upload of a 10 MB file < 2 s (median); download of a 10 MB file < 1 s (median); metadata read < 5 ms (median); all including `@logged` tracing overhead. Any different values?
- **Answer:** PENDING
- **Date:** 2026-09-13
- **Status:** PENDING
- **Incorporated:** no

## Q-26 — NFR security (path traversal / symlinks)
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** file-management, FEATURE
- **Why needed:** File storage has classic security risks: keys/filenames containing `../`, absolute paths, or symlinks could escape the storage root. This must be a hard invariant.
- **Context:** No existing file storage in the repo to reference; the settings YAML repository writes within its own directory.
- **Question:** Confirm the hard security invariant: no key/filename can escape the storage root (reject or normalize `../`, absolute paths, null bytes; handle symlinks — reject or resolve within root). Which symlink behavior: reject or resolve within root?
- **Answer:** PENDING
- **Date:** 2026-09-13
- **Status:** PENDING
- **Incorporated:** no

## Q-27 — Settings registry integration
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** file-management, FEATURE
- **Why needed:** Configurable limits should use the shared settings registry (repo pattern: `register_feature("file-management", [...])`, live reads like mail-service). The key set and category must be confirmed.
- **Context:** mail-service registers `mail.*` keys and reads them live on each send; the settings registry is the shared mechanism.
- **Question:** Confirm the settings keys registered via `register_feature("file-management", [...])` (e.g., `file-management.storage_root`, `file-management.max_file_size`, `file-management.avatar_max_size`, `file-management.allowed_types`, `file-management.avatar_base_url`), read live on each operation. Which keys should be settings vs. constructor args?
- **Answer:** PENDING
- **Date:** 2026-09-13
- **Status:** PENDING
- **Incorporated:** no

## Q-28 — Observability policy
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** file-management, FEATURE
- **Why needed:** The AGENTS.md tracing policy mandates public service classes traced with `@logged_class` (with `include_args=False` where secrets are involved) and module functions with `@logged`. Confirm applicability and slow thresholds.
- **Context:** AGENTS.md "Using the Logging Feature" — tracing policy (default); user-management's `UserManager` is traced with `@logged_class`.
- **Question:** Confirm: the public service class (e.g., `FileService`) is traced with `@logged_class` (with a sensible `slow_threshold_ms`), module-level functions with `@logged`, `include_args=False` where secrets are involved. Any method that needs `include_args=True` for debuggability?
- **Answer:** PENDING
- **Date:** 2026-09-13
- **Status:** PENDING
- **Incorporated:** no
