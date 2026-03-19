# Spec: Postgres and pgvector Persistence Adapter

## Status

Proposed

## Requirements

### Requirement: Keep Postgres and pgvector inside infrastructure adapters

The Postgres and `pgvector` persistence implementation MUST live in the
VeraBrain infrastructure layer and MUST fulfill the existing
application-layer repository and unit-of-work ports.

The application layer MUST NOT depend on:

- SQL statements
- database driver types
- migration tooling
- table or index names
- `pgvector` extension details

#### Scenario: Contributor wires the production persistence path

- **WHEN** a contributor implements the durable database adapter
- **THEN** the adapter lives in infrastructure
- **AND** the application-layer contracts remain unchanged

### Requirement: Persist the current domain boundaries in separate relational structures

The Postgres adapter MUST preserve the current domain split through
separate relational structures for:

- memories
- knowledge items
- explicit knowledge links
- execution items

The adapter MUST NOT collapse memory, knowledge, and execution into a
single generic table or document blob.

#### Scenario: Contributor designs the database schema

- **WHEN** the Postgres schema is defined
- **THEN** it preserves distinct structures for the current domain
  boundaries
- **AND** explicit knowledge links remain first-class persisted records

### Requirement: Store structured fields and JSON metadata

The Postgres adapter MUST store the typed fields already defined by the
application records in explicit relational columns.

The adapter MAY store free-form metadata in JSON-compatible columns, but
metadata MUST NOT replace the typed core fields required by the current
contracts.

The initial persistence shape SHOULD use timezone-aware timestamps for
temporal fields.

#### Scenario: Memory record is persisted in Postgres

- **WHEN** a memory record is saved
- **THEN** fields such as `type`, `scope`, `salience`, and timestamps are
  stored explicitly
- **AND** metadata remains inspectable without redefining the record
  shape

### Requirement: Use pgvector for memory embeddings

The initial Postgres adapter MUST support the memory-layer embedding
field through `pgvector`.

Vector storage, similarity operators, and index choices MUST stay
inside the infrastructure adapter.

The application-layer memory contracts MUST continue to expose plain
typed records and query objects instead of database-specific vector
operations.

#### Scenario: Memory retrieval uses semantic recall

- **WHEN** the Postgres adapter evaluates memory similarity or bounded
  retrieval
- **THEN** it may use `pgvector` to score or filter candidates
- **AND** the caller still interacts only through the repository ports

### Requirement: Map unit-of-work boundaries to explicit database transaction control

The Postgres persistence adapter MUST provide a unit-of-work
implementation that maps `commit` and `rollback` to explicit database
transaction behavior.

Repository operations inside the same unit of work MUST observe staged
changes consistently until the transaction is committed or rolled back.

#### Scenario: Application service writes through the persistence boundary

- **WHEN** an application service saves related records through the
  Postgres-backed unit of work
- **THEN** the writes participate in one explicit transaction boundary
- **AND** rollback prevents partially committed cross-repository changes

### Requirement: Keep retrieval and filtering bounded at the adapter edge

The Postgres adapter MUST preserve bounded query behavior for the
current repository ports.

The initial adapter MUST support:

- bounded memory similarity and search
- bounded knowledge search and link listing
- bounded execution filtering and review-queue retrieval

The exact SQL, indexing strategy, and ranking formula are
implementation-defined, but the adapter MUST return only bounded results
through the existing query objects.

#### Scenario: Runtime requests bounded context through application services

- **WHEN** the application layer issues repository queries with explicit
  limits
- **THEN** the Postgres adapter returns bounded typed results
- **AND** it does not leak database rows or unbounded result sets upward

### Requirement: Leave room for retrieval evolution

The first Postgres adapter MUST be compatible with future hybrid
retrieval improvements described by later specs, including reranking and
additional recall signals.

Those improvements MUST be introduced by evolving infrastructure and
core policy implementations, not by replacing the current repository
contracts with transport- or storage-shaped APIs.

#### Scenario: Later slice refines retrieval quality

- **WHEN** a later slice adds richer candidate selection or reranking
- **THEN** the work builds on the same repository and unit-of-work
  boundary
- **AND** existing Hermes-facing adapters do not require redesign
