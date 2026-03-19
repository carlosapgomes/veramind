# Spec: Repository and Persistence Ports

## Status

Proposed

## Requirements

### Requirement: Define separate repository ports for memory, knowledge, and execution

The VeraBrain application layer MUST expose distinct repository ports
for:

- `memory` records
- `knowledge` records and links
- `execution` records

These ports MUST remain separate so that memory, knowledge, and
execution do not collapse into a single generic persistence contract.

#### Scenario: Contributor adds persistence behavior

- **WHEN** a contributor adds persistence behavior for a new use case
- **THEN** the behavior is attached to the correct repository port
- **AND** the repository boundary preserves the distinction between
  memory, knowledge, and execution

### Requirement: Keep repository ports adapter-neutral

Repository ports MUST live in the VeraBrain application layer and MUST
not expose adapter-specific storage details such as:

- SQL statements
- ORM entities
- Postgres table names
- pgvector index management
- MCP transport metadata

Repository ports MUST operate on typed VeraBrain records and query
objects rather than database rows or transport payloads.

#### Scenario: Application service persists a record

- **WHEN** an application service saves or queries a VeraBrain record
- **THEN** it does so through typed repository ports
- **AND** it does not depend on storage-engine-specific details

### Requirement: Support memory persistence and retrieval needs

The memory repository port MUST support the behavior required by the
memory-layer foundation, including:

- loading a memory record by identifier
- upserting a structured memory record
- finding similar memories for deduplication
- searching memories for bounded retrieval

#### Scenario: Memory write pipeline checks for duplicates

- **WHEN** the memory write pipeline evaluates a memory candidate
- **THEN** it can call the memory repository port to look up similar
  memories before deciding whether to create or update a record

### Requirement: Support knowledge persistence and linking

The knowledge repository port MUST support:

- saving and loading knowledge records
- searching knowledge records
- saving semantic links between knowledge items
- listing links related to a knowledge item

Knowledge persistence MUST keep linking behavior explicit rather than
burying semantic relationships in opaque metadata.

#### Scenario: Knowledge capture creates a relationship

- **WHEN** the system captures a knowledge item that references another
  item
- **THEN** the knowledge repository port can persist the record and the
  explicit link separately

### Requirement: Support execution persistence without hard-coding GTD

The execution repository port MUST support:

- saving and loading execution records
- querying execution records by filter criteria
- listing records due for review

The execution repository port MUST stay workflow-neutral and MUST NOT
hard-code GTD-specific buckets as the only valid persistence shape.

#### Scenario: Review workflow requests items due for re-evaluation

- **WHEN** a review-oriented application service needs execution items
  due for review
- **THEN** it can retrieve them through the execution repository port
- **AND** the same port remains usable by non-GTD execution workflows

### Requirement: Define a persistence coordination port

The application layer MUST define a persistence coordination port for
multi-repository write flows.

The initial coordination port MUST expose:

- access to the memory repository port
- access to the knowledge repository port
- access to the execution repository port
- explicit `commit`
- explicit `rollback`

This coordination port MAY later map to a transaction or unit-of-work
implementation, but the application layer MUST own the contract.

#### Scenario: Application service writes across repositories

- **WHEN** an application service needs to persist related changes
  across repositories
- **THEN** it performs those writes through the persistence
  coordination port
- **AND** it controls success or failure through explicit commit and
  rollback behavior

### Requirement: Keep persistence ports open to Postgres and pgvector implementation

The repository and persistence ports MUST allow a later implementation
using Postgres and pgvector without forcing those technologies into the
application signatures.

#### Scenario: Infrastructure adapter implements the ports

- **WHEN** an infrastructure adapter implements persistence with
  Postgres and pgvector
- **THEN** it fulfills the application-layer ports
- **AND** the application-layer contracts remain unchanged
