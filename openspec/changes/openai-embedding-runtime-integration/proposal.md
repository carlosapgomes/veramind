# OpenAI Embedding Runtime Integration

## Why

The local MVP now proves the core memory loop end to end, but semantic
memory behavior is still degraded in real usage because no embedding
provider is wired into the runtime path.

Today, the write path correctly records explicit fallback metadata such
as `verabrain_embedding_status=unavailable`, but the system still lacks:

- a concrete provider choice for the first runtime-backed embedding path
- explicit runtime configuration for embedding generation
- query-time embedding support for hybrid retrieval in the local MVP

Without a dedicated change, semantic recall will remain inconsistent in
practice even though the architecture and persistence layers are already
prepared for embeddings.

## What Changes

- Adopt OpenAI as the first runtime-backed embedding provider for the
  local MVP path
- Define the runtime configuration surface for OpenAI embeddings
- Define how the provider plugs into memory write-time embeddings and
  query-time memory retrieval embeddings
- Define the expected fallback behavior when OpenAI embeddings are not
  configured, unavailable, or fail at runtime
- Record the next implementation-oriented slices for the OpenAI-backed
  path

## Non-Goals

- Replacing the adapter-neutral embedding boundary
- Introducing provider-specific logic into core services
- Expanding embeddings to knowledge or execution in this change
- Adding asynchronous background backfill or re-embedding workflows
- Switching the local MVP away from MCP-first operation

## Impact

- Turns the current lexical-only local MVP into an embedding-backed MVP
  when OpenAI credentials are configured
- Preserves the current adapter-neutral contracts while choosing a
  concrete provider for real use
- Enables more reliable semantic recall over durable memory in the
  Hermes-facing workflow
