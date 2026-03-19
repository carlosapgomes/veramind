# Memory Embedding Write Path

## Why

The memory write pipeline now classifies memory candidates, deduplicates
materially matching records, and enforces the normative `type` and
`scope` values.

What is still missing is the explicit write-path boundary for embedding
generation and persistence.

Without a dedicated change for this, the next implementation step could:

- couple the memory write path directly to one embedding provider
- hard-code model or transport behavior into the application layer
- make embedding failure behavior implicit instead of observable
- update retrieval assumptions without defining how embeddings enter the
  durable memory store

## What Changes

- Define the embedding-generation boundary for memory capture
- Define how write-path embedding attachment integrates with the
  existing memory save flow
- Define the initial failure and fallback behavior when embeddings are
  unavailable
- Define how duplicate updates should treat existing versus newly
  generated embeddings
- Record the next implementation-oriented tasks for embedding-backed
  memory capture

## Non-Goals

- Choosing a final embedding model vendor
- Defining cross-domain embeddings for knowledge or execution
- Changing the retrieval ranking policy itself
- Introducing asynchronous background re-embedding in this change
- Designing batch backfill tooling for existing memories

## Impact

- Completes the next missing boundary in the memory write pipeline
- Keeps embedding generation adapter-neutral and observable
- Prepares the Postgres path to persist real embeddings without leaking
  provider concerns into the core or application contracts
