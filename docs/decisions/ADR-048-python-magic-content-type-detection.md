# ADR-048: Magic-byte type detection via python-magic

## Status
Accepted (amended 2026-09-14: `python-magic` replaced by `filetype` + text fallback — see Amendment)

## Context
A file's type must be validated independently of user-supplied metadata
(REQ-004, REQ-005, NFR-002). The declared MIME type and the original
filename are caller-controlled and therefore untrusted: a caller can declare
`image/jpeg` for content that is a PDF, or name an executable `report.pdf`.
The allowed-type policy (REQ-006) and the type-conflict rejection (REQ-005)
both need a trustworthy type signal that is derived from the content itself,
not from metadata.

## Decision
Use magic-byte detection on the uploaded content to determine the MIME type.
The detected type is the source of truth and is recorded in the metadata
(`detected_mime_type`). Conflicting signals are rejected, not silently
overwritten: a declared MIME type that differs from the detected type, or an
original-filename extension that implies a different MIME type than the
detected type, raises `FileValidationError` (reason `type_conflict`).

**Detection library (amended):** the pure-Python `filetype` package detects
binary types from their magic bytes (`filetype.guess_mime(data)` → MIME type,
or `None` when unidentified). For content `filetype` cannot identify, a text
fallback applies: text content (no null bytes in the leading 8 KiB) is
detected as `text/plain`; otherwise `application/octet-stream`. This preserves
the original `python-magic` behavior (binary magic-byte detection + text
detection + `application/octet-stream` fallback) with a cross-platform
dependency that has no native library to load.

## Amendment (2026-09-14)
`python-magic` was replaced by `filetype` + the text fallback described in the
Decision. **Why:** on the development/CI host (Windows), `python-magic` is
unusable — `import magic` segfaults (exit 139) and `magic.loader.load_lib()`
hangs (no bundled libmagic, and loading it deadlocks). This blocked the
T-005 implementation. `filetype` is pure Python, has no native library to
load, and was verified on the host to detect the types the spec's acceptance
criteria exercise (image/png, image/jpeg, image/webp, image/gif,
application/pdf, application/zip) plus the text fallback (text/plain).
`puremagic` was evaluated and rejected: its 2.x API returns extensions (not
MIME types) and raises for unidentified content, so it is not a clean
drop-in.

**Spec drift:** `docs/specs/file-management.md` names `python-magic`
(REQ-004, REQ-005, D3). The normative behavior — magic-byte detection on the
content as the source of truth, with conflicting signals rejected — is
preserved; only the library changes. A spec amendment to rename the library
is deferred (the behavior, not the library name, is what the spec governs).

## Consequences
- Robust type validation that cannot be spoofed by metadata; the declared
  type is recorded for transparency but never trusted.
- Rejection (rather than overwrite) is stricter: a caller that mislabels a
  file must fix the input instead of receiving a silently corrected record.
- A new runtime dependency (`filetype`, pure Python; no native library).
- Detection runs on every upload, inside the NFR-001 upload budget
  (< 2 s median for 10 MB).

## Alternatives Considered
- Trusting the declared MIME type and filename extension — rejected:
  caller-controlled metadata is spoofable; the allowed-type policy would be
  meaningless (NFR-002).
- Python's `mimetypes` module — rejected: extension-based, i.e. still
  metadata-driven, and incomplete for binary formats.
- Per-format decoders (e.g. only checking image headers) — rejected:
  incomplete coverage, custom parsing logic, no single authoritative signal.
- `python-magic` (libmagic bindings) — the original choice; rejected at
  implementation time because it segfaults/hangs on the Windows host (no
  bundled libmagic). See Amendment.
- `puremagic` (pure-Python libmagic reimplementation) — evaluated; rejected:
  its 2.x API returns extensions (not MIME types) and raises for
  unidentified content, so it is not a clean drop-in.

## References
- `docs/specs/file-management.md` (REQ-004, REQ-005, REQ-006, NFR-002; D3)
- `AGENTS.md` — Dependencies and Existing Packages
