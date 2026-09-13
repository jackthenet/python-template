# ADR-048: Magic-byte type detection via python-magic

## Status
Accepted

## Context
A file's type must be validated independently of user-supplied metadata
(REQ-004, REQ-005, NFR-002). The declared MIME type and the original
filename are caller-controlled and therefore untrusted: a caller can declare
`image/jpeg` for content that is a PDF, or name an executable `report.pdf`.
The allowed-type policy (REQ-006) and the type-conflict rejection (REQ-005)
both need a trustworthy type signal that is derived from the content itself,
not from metadata.

## Decision
Use the established `python-magic` package (libmagic bindings) to detect the
MIME type from the uploaded content's magic bytes. The detected type is the
source of truth and is recorded in the metadata (`detected_mime_type`).
Conflicting signals are rejected, not silently overwritten: a declared MIME
type that differs from the detected type, or an original-filename extension
that implies a different MIME type than the detected type, raises
`FileValidationError` (reason `type_conflict`).

## Consequences
- Robust type validation that cannot be spoofed by metadata; the declared
  type is recorded for transparency but never trusted.
- Rejection (rather than overwrite) is stricter: a caller that mislabels a
  file must fix the input instead of receiving a silently corrected record.
- A new runtime dependency (`python-magic`, native libmagic).
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

## References
- `docs/specs/file-management.md` (REQ-004, REQ-005, REQ-006, NFR-002; D3)
- `AGENTS.md` — Dependencies and Existing Packages
