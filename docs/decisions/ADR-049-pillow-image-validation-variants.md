# ADR-049: Image decode validation and variant generation via Pillow

## Status
Accepted

## Context
Avatars must be usable images: decodable, bounded in dimensions (≤ 4096×4096,
REQ-019), and served in 64px/256px variants (REQ-021). Magic-byte detection
alone is insufficient: a truncated PNG passes magic-byte sniffing as
`image/png` but fails to decode (EDGE-012), and magic bytes give no
dimensions. Avatar uploads therefore need a second, stricter validation
stage and an image processor for the variants.

## Decision
Use the established `Pillow` package. Avatar content is validated by a full
Pillow decode (undecodable content raises `FileValidationError` with reason
`image_decode_failed`; dimensions above 4096×4096 raise reason
`dimensions_exceeded`). On a successful avatar upload/replace, 64px and 256px
variants (longest side, PNG) are generated and stored as separate files with
their own metadata records and a `variant_of` reference to the main file;
variants are deleted with the main file.

## Consequences
- Decode validation is strictly stronger than magic-byte detection
  (two-stage validation); truncated images are caught (EDGE-012).
- A new runtime dependency (`Pillow`, native image libraries).
- Decode plus two resizes run per avatar upload, inside the NFR-001 budget.
- Variants are separate store files, so the store stays flat and variant
  deletion is ordinary file deletion.

## Alternatives Considered
- Magic-byte detection only — rejected: truncated/corrupt images slip
  through and dimensions are unknown (EDGE-012, REQ-019).
- A custom image parser — rejected: image decoding is a strong "use an
  established package" case per `AGENTS.md`; a hand-rolled parser is risky.
- Storing variants as database blobs — rejected: the store is flat files
  behind the `StorageBackend` ABC; blobs would bypass the storage layer.

## References
- `docs/specs/file-management.md` (REQ-019, REQ-021, EDGE-012; D8)
- `AGENTS.md` — Dependencies and Existing Packages
