# ADR-0006: Establish retrieval policy boundaries for VeraBrain

[Portuguese (Brazil)](./ADR-0006-establish-retrieval-policy-boundaries.pt-BR.md)

## Status

Accepted

## Context

VeraBrain is meant to complement Hermes memory rather than replace it.
That only works if VeraBrain retrieval stays bounded, explicit, and
architecturally separate from both transport concerns and storage
technology details.

The repository now has:

- application request contracts for bounded context retrieval
- MCP mappings that serialize grouped context back to Hermes
- an in-memory adapter that can exercise deterministic query behavior

Before implementing the Postgres adapter and richer retrieval logic, the
project needs a stable decision about what retrieval policy belongs to
the core and what remains an infrastructure concern.

## Decision

Adopt the following retrieval-policy boundaries for VeraBrain:

- retrieval is a VeraBrain core concern, not an MCP concern
- retrieval results must always be bounded by explicit limits carried by
  application requests or repository query objects
- retrieval may combine lexical, structural, salience, temporal, and
  embedding-backed signals
- the exact ranking algorithm is implementation-defined and may evolve
  without changing the application contracts
- adapters may request context, but they must not own ranking policy or
  retrieval heuristics

The initial practical direction is:

- deterministic lexical and filter-based behavior for the in-memory
  adapter
- hybrid retrieval in the future Postgres adapter, with `pgvector`
  available for semantic recall
- grouped output by memory, knowledge, and execution instead of a single
  undifferentiated retrieval pool

## Alternatives Considered

1. Keep retrieval mostly inside MCP or Hermes-facing adapters
2. Lock a single fixed scoring formula now
3. Define retrieval as a core-owned policy with adapter-neutral
   contracts and implementation-specific ranking details

## Consequences

- Positives:
  - preserves the core-plus-adapters architecture under retrieval
  - allows ranking and recall quality to improve without breaking public
    contracts
  - keeps Hermes integrations focused on requesting bounded context
    rather than reimplementing memory behavior
  - avoids collapsing memory, knowledge, and execution into one generic
    search result shape
- Negatives/Trade-offs:
  - leaves ranking details to later specs and implementations
  - requires discipline so infrastructure adapters do not leak scoring
    assumptions upward
  - may create temporary differences between in-memory retrieval and
    Postgres-backed retrieval quality

## Notes

This ADR intentionally fixes boundaries, not a final algorithm. A later
spec can define hybrid retrieval details such as embedding generation,
candidate selection, reranking, and freshness weighting.
