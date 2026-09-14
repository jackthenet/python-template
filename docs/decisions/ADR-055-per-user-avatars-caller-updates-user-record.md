# ADR-055: Per-user avatars with caller-updates-user-record (no user-management dependency)

## Status
Accepted

## Context
Avatars are per-user files (REQ-017, REQ-018), but the user record
(`profile_picture_url`) is owned by user-management. If file-management
imported user-management to write the URL onto the user record, the two
features would be coupled (and a user-management → file-management import
for avatars would create a dependency cycle). If file-management
subscribed to `UserDeleted` to clean up avatars, it would hard-depend on
the event bus and on user-management's event vocabulary. The feature must
stay a single, independent FEATURE.

## Decision
file-management tracks a **user → file mapping** (`UserAvatar` table,
opaque `user_id`) and exposes `upload_avatar`/`replace_avatar`/
`delete_avatar`/`get_avatar`. It does **NOT** depend on user-management and
does **NOT** subscribe to `UserDeleted`. The **caller** is responsible for
setting the avatar URL on the user record (the returned `AvatarRead.url`
always satisfies user-management's `profile_picture_url` validation, so no
spec amendment is needed) and for cleaning up the avatar on user deletion
(`delete_avatar` is idempotent, so the caller can call it at deletion time).

## Consequences
- No cross-feature dependency and no dependency cycle; file-management
  stays a single independent FEATURE.
- The caller must remember to update the user record and to delete the
  avatar on user deletion — a documented caller convention, not an
  enforced invariant.
- An orphaned avatar is possible if the caller forgets — accepted as the
  caller's responsibility (out of scope).
- The `UserAvatar` mapping uses an opaque `user_id`, so file-management
  never imports user-management types.

## Alternatives Considered
- file-management imports user-management to write the URL — rejected:
  cross-feature dependency and a potential cycle (user-management already
  conceptually references avatars via `profile_picture_url`).
- Subscribing to `UserDeleted` for avatar cleanup — rejected: hard-depends
  on the event bus and on user-management's event vocabulary; couples the
  features.
- Bidirectional sync of the user record and the avatar mapping — rejected:
  complex, two sources of truth.

## References
- `docs/specs/file-management.md` (REQ-017, REQ-018, Out of Scope; D6, D7)
- `docs/specs/user-management.md` (`profile_picture_url`)
