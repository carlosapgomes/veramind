# Spec: Hybrid Retrieval Policy

## Status

Proposed

## Requirements

### Requirement: Keep retrieval policy explicit and core-owned

The initial hybrid retrieval policy MUST be defined explicitly as a
VeraBrain policy rather than as an MCP, Hermes, or database-specific
behavior.

Adapters MAY request retrieval, but they MUST NOT define scoring policy,
candidate selection policy, or bounded recall rules.

#### Scenario: Hermes requests long-term context

- **WHEN** a Hermes-facing adapter requests relevant long-term context
- **THEN** the retrieval behavior follows the VeraBrain policy
- **AND** the adapter does not inject transport-specific ranking logic

### Requirement: Use a staged hybrid retrieval flow for memories

The initial memory retrieval policy MUST use staged hybrid retrieval
instead of a single undifferentiated query step.

The initial stages MUST be:

1. candidate selection
2. candidate reranking
3. bounded result selection

Candidate selection MAY combine lexical and semantic recall. Reranking
MUST remain a distinct step so ranking policy can evolve without
redefining the repository boundary.

#### Scenario: Runtime searches for relevant memories

- **WHEN** a retrieval request is issued for memory context
- **THEN** the system selects a candidate set first
- **AND** reranks that candidate set before returning the final bounded
  subset

### Requirement: Combine explicit retrieval signals

The initial hybrid retrieval policy MUST allow the following signal
families to contribute to ranking:

- lexical similarity to the query
- semantic similarity when embeddings are available
- memory salience
- recency or freshness
- memory type weighting

The exact weighting formula is implementation-defined, but the policy
MUST keep these signal families explicit so later tuning is traceable.

#### Scenario: Two candidate memories compete for the same query

- **WHEN** the system ranks memory candidates for one query
- **THEN** it may use more than one signal family
- **AND** the ranking behavior is not reduced to a raw vector score
  alone

### Requirement: Keep retrieval bounded by explicit limits

The retrieval policy MUST return only bounded results using explicit
limits provided by the requesting contract or repository query object.

The policy MUST NOT escalate into unbounded recall based on query
complexity, transport, or storage backend.

#### Scenario: Runtime asks for memory context

- **WHEN** the caller requests relevant memories with a limit
- **THEN** the retrieval policy returns at most that bounded number of
  memories
- **AND** it does not expose the full candidate pool upward

### Requirement: Provide deterministic fallback when semantic recall is unavailable

The initial policy MUST define a fallback path for environments where
embeddings, vector search, or semantic recall are unavailable.

In that case, retrieval MUST still provide bounded lexical and metadata-
aware behavior rather than failing the whole memory lookup flow.

#### Scenario: Environment lacks semantic recall

- **WHEN** embeddings or vector-backed retrieval are unavailable
- **THEN** the system falls back to lexical and structured retrieval
- **AND** callers still receive bounded results through the same
  contract boundary

### Requirement: Preserve memory-domain distinctions during ranking

The retrieval policy MUST preserve the memory-layer distinction between
durable user context and the broader knowledge corpus.

The initial hybrid retrieval policy in this change applies to the memory
layer. It MUST NOT quietly merge memory and knowledge retrieval into one
generic ranking pool.

#### Scenario: Query could match both memory and knowledge

- **WHEN** the same user query could retrieve both memories and
  knowledge items
- **THEN** the memory retrieval policy still ranks only memory records
- **AND** cross-domain assembly remains a higher-level concern

### Requirement: Support bounded context-bundle assembly without collapsing domains

Context-bundle assembly MAY request retrieval from more than one domain,
but it MUST preserve grouped output by memory, knowledge, and execution.

Hybrid retrieval policy for memory MUST therefore remain composable into
context bundles without turning the bundle into one flat ranked list.

#### Scenario: Application assembles a bounded context bundle

- **WHEN** the application prepares a context bundle for agent use
- **THEN** memory retrieval may use the hybrid policy
- **AND** the resulting bundle still groups memory, knowledge, and
  execution separately
