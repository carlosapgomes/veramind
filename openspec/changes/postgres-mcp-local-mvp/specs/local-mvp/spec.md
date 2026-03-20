# Spec: Postgres MCP Local MVP

## Status

Proposed

## Requirements

### Requirement: Define a canonical local MVP startup path

The project MUST define a canonical local startup path that assembles
the VeraBrain application from explicit runtime settings and exposes it
through the MCP server surface.

The canonical path MUST reuse the existing infrastructure bootstrap and
MCP adapter boundaries rather than creating a parallel MVP-only runtime.

#### Scenario: Contributor starts the local MVP

- **WHEN** a contributor starts the local VeraBrain MVP
- **THEN** the system assembles the Postgres-backed application through
  explicit runtime wiring
- **AND** exposes the VeraBrain tool surface through the MCP server
  entrypoint

### Requirement: Define the minimum local persistence environment

The project MUST define the minimum local Postgres environment required
to run the MVP, including the expectation that `pgvector` is available.

This requirement MAY be satisfied through containerized local
infrastructure, documented setup steps, or both, but the MVP path MUST
not depend on implicit local machine state.

#### Scenario: Contributor provisions local persistence for the MVP

- **WHEN** a contributor prepares the local VeraBrain MVP environment
- **THEN** the required Postgres runtime prerequisites are explicit
- **AND** the MVP path does not assume hidden database setup

### Requirement: Define the minimum Hermes-facing MCP path

The project MUST define the minimum Hermes-facing MCP configuration
needed to exercise the MVP locally.

The initial MVP path MUST focus on MCP-first integration and MUST NOT
depend on a native Hermes plugin or Hermes skill to become runnable.

#### Scenario: Contributor points Hermes at the local VeraBrain MVP

- **WHEN** a contributor configures Hermes to use the local VeraBrain
  MCP server
- **THEN** the configuration path is explicit
- **AND** the MVP can be exercised without introducing a native Hermes
  extension

### Requirement: Define a manual smoke workflow for the MVP

The project MUST define the minimum manual smoke workflow that proves
the local MVP behavior outside the automated test suite.

The smoke workflow MUST at least cover:

- starting the local persistence environment
- starting the MCP-backed VeraBrain runtime
- saving durable memory
- retrieving bounded memory or a context bundle

#### Scenario: Contributor runs the MVP smoke path manually

- **WHEN** a contributor follows the documented local MVP workflow
- **THEN** the contributor can manually observe the MVP memory loop
- **AND** the observed path matches the archived memory-loop baseline

### Requirement: Keep local MVP scope intentionally narrow

The first local MVP path MUST remain narrowly focused on proving the
memory loop with durable persistence and MCP exposure.

It MUST NOT expand into production operations, advanced knowledge
modeling, or execution workflows in this change.

#### Scenario: Contributor evaluates the local MVP scope

- **WHEN** a contributor uses the first local MVP path
- **THEN** the path proves practical MVP behavior
- **AND** avoids taking on unrelated product scope
