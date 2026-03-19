# Spec: Memory Embedding Write Path

## Status

Proposed

## Requirements

### Requirement: Keep embedding generation outside the repository adapter

The memory write path MUST obtain embeddings through an explicit
boundary above the persistence adapter.

The memory repository and unit-of-work contracts MUST continue to accept
typed memory records rather than model clients, embedding APIs, or
provider-specific request objects.

#### Scenario: Memory capture needs semantic write support

- **WHEN** the system wants to attach an embedding to a memory record
- **THEN** embedding generation happens through an explicit write-path
  boundary
- **AND** the repository adapter still only persists the resulting
  memory record

### Requirement: Keep the embedding provider adapter-neutral

The initial embedding-generation boundary MUST stay independent from:

- a specific model vendor
- a specific inference transport
- a specific runtime shell
- Postgres or pgvector details

The exact provider implementation is adapter-defined, but the
application-layer write flow MUST consume a simple VeraBrain-facing
contract.

#### Scenario: Contributor swaps embedding backends

- **WHEN** a contributor changes the embedding backend
- **THEN** the memory write flow continues to use the same VeraBrain
  contract
- **AND** the memory repository boundary remains unchanged

### Requirement: Attach embeddings during memory capture when available

When the memory write path persists a new durable memory or updates a
materially matching memory, it MUST be able to attach an embedding when
an embedding provider is available and succeeds.

The resulting persisted memory record MUST therefore be able to carry
the generated embedding into durable storage.

#### Scenario: Provider is available during memory capture

- **WHEN** the write path processes a memory candidate
- **AND** the embedding provider returns a vector successfully
- **THEN** the persisted memory record includes that embedding

### Requirement: Define explicit fallback behavior for unavailable embeddings

The write path MUST define explicit behavior for cases where embedding
generation is unavailable, disabled, or fails.

The initial behavior MUST be observable and MUST NOT silently change the
meaning of the write flow.

The initial design MUST allow VeraBrain to continue persisting the
memory record without an embedding when that fallback policy is chosen.

#### Scenario: Embedding provider fails during memory capture

- **WHEN** the write path cannot obtain an embedding for a memory
  candidate
- **THEN** the fallback behavior is explicit
- **AND** the system can still persist the memory record without an
  embedding if the configured write policy allows it

### Requirement: Define embedding behavior for deduplicated updates

When the write path decides that a new memory candidate materially
matches an existing memory, the system MUST define what happens to the
existing embedding.

The initial policy MUST make it explicit whether the write path:

- preserves the existing embedding when no new one is available
- replaces the existing embedding when a new one is generated

The chosen behavior MUST be consistent and testable.

#### Scenario: Deduplicated memory update receives a new embedding

- **WHEN** the write path updates an existing memory after duplicate
  assessment
- **AND** a new embedding is generated successfully
- **THEN** the persisted record follows the defined replacement policy

#### Scenario: Deduplicated memory update lacks a new embedding

- **WHEN** the write path updates an existing memory after duplicate
  assessment
- **AND** no new embedding is available
- **THEN** the persisted record follows the defined preservation policy

### Requirement: Keep write-path embedding concerns separate from retrieval policy

Embedding generation during memory capture MUST remain distinct from the
hybrid retrieval policy.

The write-path change MAY provide the data needed by retrieval, but it
MUST NOT redefine retrieval scoring, bounded recall, or cross-domain
bundle assembly.

#### Scenario: Contributor extends embedding-backed capture

- **WHEN** a contributor modifies how embeddings are attached during
  writes
- **THEN** the retrieval policy remains defined by the existing
  retrieval baseline
- **AND** the write-path change does not collapse write and retrieval
  concerns into one component
