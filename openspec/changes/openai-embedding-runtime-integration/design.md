# Design: OpenAI Embedding Runtime Integration

## Objective

Define the first provider-backed embedding runtime path for the local
VeraBrain MVP.

This change is not about redefining the embedding boundary. It is about
choosing one concrete provider, wiring it through the existing
adapter-neutral contracts, and making the local MVP capable of real
semantic memory writes and hybrid retrieval.

## Canonical Runtime Flow

The canonical OpenAI-backed runtime flow is:

1. load explicit local MVP Postgres settings
2. load explicit OpenAI embedding settings
3. bootstrap or verify the Postgres runtime path
4. assemble a provider-backed `VeraBrainApplication`
5. expose the application through the existing MCP server over `stdio`
6. let Hermes call `save_memory`, `search_memory`, and
   `get_context_bundle`

When OpenAI settings are present and valid:

- `save_memory` should attempt write-time embedding generation
- `search_memory` and `get_context_bundle` should attempt query-time
  embedding generation
- the Postgres adapter should receive typed memory records and query
  embeddings, not OpenAI-specific payloads

When OpenAI settings are absent or provider calls fail:

- the local MVP remains usable
- writes fall back to the current explicit `unavailable` or `failed`
  metadata behavior
- retrieval falls back to lexical-only bounded behavior

## Layer Responsibilities

The responsibilities remain intentionally split:

- `runtime`: read environment configuration, construct the
  OpenAI-backed provider instance, and inject provider functions into
  the application assembly
- `application`: call the existing embedding contracts, preserve
  explicit fallback behavior, and avoid direct dependency on provider
  SDKs
- `infrastructure`: keep Postgres as the persistence boundary and keep
  OpenAI-specific client code at the edge
- `MCP adapter`: remain unchanged in contract shape and benefit from
  better retrieval without learning provider details

This preserves the current dependency direction:

- runtime/infrastructure may know the provider
- application knows only the embedding contract
- core remains provider-agnostic

## OpenAI Provider Shape

The first OpenAI integration should use one provider component at the
edge with two explicit capabilities:

- generate embeddings for memory capture text
- generate embeddings for retrieval query text

These capabilities may come from one shared client instance, but they
should still be injected into the application through the current
separate write and query boundaries.

The initial settings surface should support:

- API key
- embedding model name
- optional base URL for compatibility or future proxying
- explicit enable/disable behavior through configuration presence

The provider should be constructed only when the required settings are
present. Missing configuration should not crash the local MVP unless a
future policy explicitly changes that.

## Local MVP Assembly

The local MVP launcher should evolve from:

- Postgres settings
- Postgres runtime bootstrap
- application factory
- MCP server

to:

- Postgres settings
- OpenAI embedding settings
- Postgres runtime bootstrap
- OpenAI-backed application factory wiring
- MCP server

The application assembly should inject:

- `memory_embedding_provider` for write-time capture
- `memory_query_embedding_provider` for retrieval-time hybrid search

This keeps the local MVP path coherent:

- saved memories gain embeddings when available
- subsequent queries can use semantic recall
- the same runtime path still works without embeddings when degraded

## Failure and Fallback Paths

The first provider-backed runtime path must keep the current explicit
fallback model.

Expected cases:

- `missing API key`: provider is not constructed, the write path records
  `unavailable`, and retrieval stays lexical-only
- `provider returns no embedding`: the write path records
  `unavailable`, and retrieval stays lexical-only for that query
- `provider request fails`: the write path records `failed` plus error
  metadata, and retrieval falls back to lexical-only
- `Postgres unavailable`: startup still fails before MCP exposure,
  independent of embeddings

The key rule is that OpenAI failure must degrade the embedding behavior,
not the entire MVP when persistence and MCP remain healthy.

## Documentation Scope

The implementation slices after this design should update the local MVP
runbook to cover:

- required env vars
- how to enable OpenAI embeddings locally
- what behavior to expect when embeddings are disabled or degraded
- how to tell, from saved metadata or retrieval behavior, whether the
  runtime is operating semantically or lexically

## Out of Scope

This change does not cover:

- background backfill of old memories
- knowledge or execution embeddings
- provider benchmarking across vendors
- model selection automation
- migration away from OpenAI as the first concrete provider
