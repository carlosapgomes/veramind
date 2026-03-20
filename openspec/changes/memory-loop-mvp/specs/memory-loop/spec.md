# Spec: Memory Loop MVP

## Status

Proposed

## Requirements

### Requirement: Define the MVP as an observable vertical memory loop

The initial VeraBrain MVP MUST be defined as a small vertical slice with
observable end-to-end behavior, not as a broad expansion of isolated
layers.

The MVP loop MUST at minimum cover:

- memory capture input
- memory write-path classification
- duplicate assessment
- embedding attachment when available
- durable persistence
- bounded memory retrieval
- exposure of useful memory context through the MCP-facing surface

#### Scenario: Contributor asks what the MVP must prove

- **WHEN** a contributor inspects the active MVP change
- **THEN** the expected behavior is described as an end-to-end memory
  loop
- **AND** the change does not define the MVP as a collection of
  unrelated layer-specific upgrades

### Requirement: Define the canonical happy path for durable memory capture

The MVP MUST define a canonical happy-path scenario where a durable
memory candidate travels through the existing VeraBrain write path and
becomes retrievable as useful bounded context.

That happy path MUST include:

- a durable capture candidate
- classification into the memory pipeline
- duplicate handling through the existing duplicate-assessment flow
- embedding generation when available
- durable persistence of the resulting memory record
- bounded retrieval by a later query

#### Scenario: Durable memory capture succeeds end to end

- **WHEN** the system receives a durable memory candidate
- **AND** the write path succeeds
- **THEN** the resulting memory record is stored durably
- **AND** a later bounded query can retrieve it as relevant memory
  context

### Requirement: Keep bounded retrieval as part of the MVP

The MVP MUST require bounded retrieval rather than unbounded memory
recall.

The initial behavior MUST prove that VeraBrain can return a limited,
useful set of durable memories in response to a query that Hermes can
consume through MCP.

#### Scenario: Hermes requests relevant context through MCP

- **WHEN** Hermes calls the MCP-facing VeraBrain surface for memory
  context
- **THEN** VeraBrain returns bounded memory results
- **AND** the returned context is shaped for agent consumption rather
  than raw storage inspection

### Requirement: Define explicit fallback in the MVP loop

The MVP MUST define observable fallback behavior when parts of the loop
degrade.

The initial MVP MUST at least cover:

- embedding unavailable or failed
- persistence unavailable or failed

The fallback behavior MUST remain observable to contributors and MUST
NOT silently redefine the meaning of the flow.

#### Scenario: Embedding degrades but persistence remains available

- **WHEN** the system cannot obtain an embedding during durable memory
  capture
- **THEN** the fallback behavior remains explicit
- **AND** the MVP can still persist the memory if the write policy
  allows it

#### Scenario: Persistence degrades during the MVP loop

- **WHEN** the durable write path cannot persist the memory record
- **THEN** the failure remains explicit to the caller
- **AND** the system does not pretend that the memory loop completed
  successfully

### Requirement: Keep the MVP narrow relative to later roadmap items

The MVP change MUST remain narrower than later roadmap concerns.

This change MUST NOT expand the MVP to include:

- execution workflows or GTD-specific behavior
- broad knowledge-graph ambitions
- production hardening as a substitute for proving the loop
- a final Hermes-versus-VeraBrain memory authority policy

#### Scenario: Contributor proposes adding execution workflow scope

- **WHEN** a contributor attempts to extend the MVP into workflow or
  GTD-specific behavior
- **THEN** the change is considered out of scope for the MVP memory
  loop
- **AND** that work is deferred until after the memory loop is proven
