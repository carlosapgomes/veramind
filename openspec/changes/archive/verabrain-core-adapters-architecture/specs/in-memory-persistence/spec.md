# Spec: Initial In-Memory Persistence Adapters

## Status

Proposed

## Requirements

### Requirement: Provide an initial infrastructure implementation

VeraBrain MUST provide an initial infrastructure adapter set that
implements the memory, knowledge, execution, and unit-of-work ports
without introducing transport or storage-engine details into the
application layer.

The initial implementation MAY be in-memory, but it MUST preserve the
same port boundaries defined by the application layer.

#### Scenario: Application services need a concrete persistence adapter

- **WHEN** a contributor wires VeraBrain services outside of repository
  fakes
- **THEN** the infrastructure layer provides concrete repository and
  unit-of-work implementations
- **AND** the application contracts remain unchanged

### Requirement: Keep committed state separate from staged unit-of-work state

The initial persistence adapter MUST distinguish committed state from
staged unit-of-work mutations so `commit` and `rollback` have observable
behavior.

#### Scenario: Write is rolled back

- **WHEN** a record is written into the in-memory unit of work and the
  unit of work is rolled back before commit
- **THEN** a fresh unit of work over the shared store does not see the
  staged record

### Requirement: Support deterministic bounded query behavior

The initial in-memory repositories MUST support deterministic bounded
query behavior for:

- memory similarity and search
- knowledge search and link listing
- execution filtering and review queue retrieval

The in-memory adapter MAY use simple text matching and ordering rules,
but those rules MUST remain inside the infrastructure adapter rather
than leaking into the application contracts.

#### Scenario: Contributor uses the in-memory adapter in tests or local wiring

- **WHEN** the in-memory repositories are queried with bounded filters
- **THEN** they return deterministic results through the existing query
  objects
- **AND** the returned records stay typed by domain
