# Hybrid Retrieval Policy

## Why

ADR-0006 fixed the architectural boundaries for retrieval, but it did
not yet define the concrete policy VeraBrain should use for hybrid
retrieval.

The repository now has:

- accepted retrieval-policy boundaries
- memory-layer requirements that call for hybrid relevance
- Postgres and `pgvector` persistence boundaries and initial adapters

Without a dedicated retrieval-policy change, future implementation could
drift into ad hoc scoring rules, unbounded recall, or adapter-specific
heuristics that are hard to compare and evolve.

## What Changes

- Define the initial hybrid retrieval policy for memory retrieval
- Define candidate selection and reranking stages
- Define the role of lexical, semantic, salience, recency, and type
  signals
- Define bounded-result and fallback behavior
- Define how retrieval policy relates to context-bundle assembly

## Non-Goals

- Choosing a final embedding model or provider
- Defining a production observability stack
- Implementing retrieval in this change
- Defining long-term learning or consolidation behavior
- Replacing the current application contracts

## Impact

- Gives the next retrieval implementation slices a stable target
- Keeps ranking policy explicit and outside transport adapters
- Reduces the risk of hidden scoring behavior inside infrastructure code
- Preserves future tuning freedom without changing contract boundaries
