# ADR-078: Stateless live query (no index, no persistence)

## Status
Accepted

## Context
Search queries content that already lives in the features' SQLite
repositories. An index would require building, maintaining, and synchronizing a
second copy of that data (change-event-driven maintenance, incremental
indexing), with consistency risk and a new storage surface. The spec's
performance budget (NFR-001: single-source query < 100 ms median,
10k–100k items per source, SQLite-backed) must hold. The spec explicitly
excludes any index, cache, or persistence for search results (spec §13, Q-101).

## Decision
No index, no cache, no persistence: every query is live. `SearchService` holds
only the in-memory registry of sources; each search fans out to the source
query functions (sync; executed in a worker thread with a per-source timeout,
D12) and combines the per-source pages (D6). The registry is the only state;
`reset()` clears it (D2). A source failure leaves no partial state — the
timed-out thread is abandoned, bounded by the worker pool (D12, NFR-005).

## Consequences
- Results are always current: no staleness, no consistency maintenance against
  the features' repositories.
- No new storage surface; the registry is trivially thread-safe (snapshot under
  the internal lock, query outside it, D18).
- The per-source timeout bounds slow sources, so one slow source cannot hang a
  global fan-out (resilient fan-out, D11/D12).
- Trade-off: every query re-reads the source's data. The budget holds for
  10k–100k items over SQLite (NFR-001); a larger corpus or a slower source
  would need an index — a future decision, not this change.

## Alternatives Considered
- A search-engine index (Elasticsearch/Meilisearch) — rejected: out of scope
  (spec §13); a new dependency + engine for a small in-process corpus.
- An in-process index maintained by change events — rejected: incremental
  indexing + event-driven maintenance is out of scope (spec §13); it duplicates
  the features' data and adds consistency work for no benefit at this scale.
- Caching query results — rejected: results would go stale against live
  repository state; the spec explicitly excludes caches (spec §13, Q-101).

## References
- `docs/specs/search.md` (D1, D2, D6, D11, D12; REQ-001, REQ-019; NFR-001,
  NFR-005; §13, Q-101)
- `docs/decisions/ADR-076-search-feature-placement.md`
