# Spec: Pgvector Driver Registration

## Status

Proposed

## Requirements

### Requirement: The Psycopg runtime path must register pgvector types

The default Postgres runtime connector MUST register `pgvector` types on
each Psycopg 3 connection used by the VeraBrain runtime path.

#### Scenario: Runtime creates a default Postgres connection

- **WHEN** the default Psycopg connector opens a connection
- **THEN** it registers pgvector types on that connection before use

### Requirement: Semantic retrieval must not depend on unregistered vector types

The runtime path MUST NOT depend on raw fallback representations for
`vector` columns or query parameters when `pgvector` registration is
available.

#### Scenario: Runtime reads memory rows with vector embeddings

- **WHEN** the Postgres adapter reads rows containing `embedding`
  values
- **THEN** the driver registration path makes those values consumable by
  the infrastructure adapter
