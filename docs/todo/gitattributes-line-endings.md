# TODO: gitattributes-line-endings

Backlog item for one planned change, created at **P.1 Frame** from this template and named `gitattributes-line-endings.md`. One file per change.

This is a **planning record, not normative**: like `docs/questions/`, it is committed directly to `main` (see "Phase P: PREPARE" in `AGENTS.md`). It carries no approval gate — the spec does.

- **Status:** PREPARING  <!-- PREPARING | QUESTIONS-ANSWERED | READY | IN-WORKFLOW | WAITING | MERGED | DROPPED -->
- **Change type:** DOCS/CHORE  <!-- P.2 must confirm; if the EOL policy changes what a tool sees, it may reclassify -->
- **Created:** 2026-10-10
- **Question file:** `docs/questions/gitattributes-line-endings.md`
- **Spec:** n/a
- **Worktree:** <created at P.4> `../python-template_kopie-worktrees/chore/gitattributes-line-endings`
- **Depends on:** none
- **Related specs:** `docs/specs/structure-map.md` (AC-021 committed-map-matches-fresh-render is the witness this change unblocks on Windows)

## Goal (one line)
Add a `.gitattributes` that pins line endings in the working tree, so a checkout on Windows produces byte-identical files to the repository and the byte-comparing gates stop failing for host reasons.

## Why
Measured at `main` (2026-10-10): `core.autocrlf=true` and no `.gitattributes` exist, so Git converts on checkout — `git ls-files --eol` reports `i/lf w/crlf` for `STRUCTURE.md`, `scripts/make_map.py` and `tests/acceptance/test_structure_map.py`. The committed blob is 146 172 bytes while the checked-out file is 148 113 bytes — exactly +1 941 bytes, one CR per line of the 1 941-line map.

`uv run python scripts/make_map.py --check` compares the checked-out `STRUCTURE.md` against a freshly rendered one (written with `\n`), so on this host it exits 1 **even when the content is identical**. `tests/acceptance/test_structure_map.py::test_ac_021_committed_map_matches_fresh_render` compares bytes the same way and is therefore red on Windows for a reason CI (Linux, LF) never sees — this has already cost two changes a "pre-existing failure, host caveat" note in their verification records.

## In scope
- A `.gitattributes` at the repository root stating the EOL policy (P.2 decides `* text=auto eol=lf` vs per-extension rules).
- Re-checking the affected gates (`make_map.py --check`, the structure-map acceptance suite) on Windows afterwards.

## Out of scope
- Re-normalising file contents in the repository (no mass re-commit of existing files unless P.2 shows it is unavoidable).
- Changing `scripts/make_map.py` or any test to compare line-ending-insensitively — that would weaken the witness.
- Any `.editorconfig` / formatter change.

## Affected features
None (no `src/` or `tests/` behaviour change); the repository's checkout semantics change.

## Constraints and risks
- Adding `.gitattributes` can make Git re-normalise every text file at the next `git add`, producing a huge phantom diff in every open worktree — the change must state how it avoids that (e.g. `git add --renormalize` as an explicit, separate step, or rules that match the current index bytes exactly).
- Three worktrees/PRs may be open when it lands; each must be checked for a re-normalisation surprise.
- `core.autocrlf=true` is a per-machine setting; the `.gitattributes` must win over it (that is what `eol=lf` does) — the witness must be measured on this host, not assumed.

## Value triage (2026-10-10, pre-workflow)
- **Overlap:** none — no live or archived TODO touches line endings; `docs-path-ci-trigger` (archived) is about CI path filters, not EOL. The affected witness already exists (`test_ac_021_...`), so no new test is needed.
- **Beneficiary:** anyone running the suite on Windows, and every future verification record: it removes a recurring false failure that currently has to be explained away as a "host caveat" in each change's evidence.
- **Score: 4/5** — small, one-file change with a clear payoff (a whole class of host-dependent gate noise disappears); the risk is the re-normalisation diff, which is manageable but real.
- **Recommendation:** implement
- **Decision:** <the user's answer + date>  <!-- recorded when the user answers; a dropped TODO moves to docs/todo/archive/ with its question file -->

## Acceptance signal (plain language)
On this Windows machine, a fresh `git checkout` of `main` gives `git ls-files --eol` reporting `w/lf` for `STRUCTURE.md`, `uv run python scripts/make_map.py --check` exits 0 with no local regeneration, and `test_ac_021_committed_map_matches_fresh_render` passes locally as well as in CI.

## Prep log
| Step | Date | Result |
|---|---|---|
| P.1 Frame | 2026-10-10 | classified DOCS/CHORE; measured `i/lf w/crlf` on STRUCTURE.md/make_map.py/test_structure_map.py, blob 146 172 B vs worktree 148 113 B (+1 941 = one CR per map line), `make_map.py --check` exits 1 on identical content |
| P.2 Interrogate (22 questions) | 2026-10-10 | **DONE — 22 questions (Q-01…Q-22) recorded in one batch, all PENDING, every entry with a `Recommended:` + reason; Category coverage table complete (9 covered, 2 skipped with reasons); scope-boundary question Q-20; overlap check E-14 (15 specs, 13 live + 17 archived TODOs — no overlap).** Commit `fc5f310`. **Two premises in this TODO's "Why" are FALSE as measured — P.4 MUST draft from the corrected version:** (1) `make_map.py --check` does **not** fail on identical content — `scripts/make_map.py:533` already normalises `\r\n`→`\n` (mandated by `structure-map.md` AC-005 / EDGE-016 / NFR-007, witnessed by `test_edge_016_crlf_checkout_is_not_stale`); the real exit-1 cause is a **content** delta (`docs/ — 225 files` vs `231`). (2) "CI (Linux, LF) never sees it" is false — `main`'s Quality `coverage` job is red now for the same staleness. Conversely the TODO's headline hazard (re-normalisation diff) measures at **zero** (`git add --renormalize .` → 0 files; the index is already 100% LF), while the real hazards are the opposite: `* text=auto` **without** `eol=lf` forces CRLF even for `autocrlf=false` (E-09), and a forced `text` rule corrupts `src/backend/filemanagement/assets/default_avatar.png` (761 → 760 B, E-10). Also: `EDGE-016` ("no `.gitattributes` in this repository") and NFR-007 become factually stale (Q-10), `ADR-085` + spec §13 already rejected a repo-wide rule, and the DOCS/CHORE classification is questioned at Q-12. **The `## Value triage` `Decision:` is still the unfilled placeholder — with the premise corrected, the implement / merge / drop decision must be re-asked with the new facts (the change may be much smaller than framed, or may belong to a map-staleness fix instead).** Next: **P.3 Answer** (⏸ user — 22 PENDING answers + the value-triage decision) |
| P.3 Answer (<n> answered) | | |
| P.4 Draft spec / triage / baseline / scope | | |
| P.5 Self-consistency (FEATURE/CROSS-CUTTING) | | |
