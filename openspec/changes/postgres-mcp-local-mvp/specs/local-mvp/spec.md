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

The canonical startup sequence MUST be:

1. ensure the project-local Docker Compose Postgres service is running
2. construct explicit `PostgresRuntimeSettings`
3. open a startup connection through infrastructure runtime wiring
4. apply or verify schema state according to the configured migration
   mode
5. construct the `PostgresRuntimeApplicationFactory`
6. build the `VeraBrainApplication`
7. expose the application through the host-launched MCP stdio server

The local MVP startup path MUST keep:

- Compose-managed infrastructure concerns in the local environment layer
- connection and schema bootstrap in infrastructure runtime wiring
- application assembly in the Postgres application factory
- MCP exposure in the MCP adapter/server layer

#### Scenario: Contributor starts the local MVP

- **WHEN** a contributor starts the local VeraBrain MVP
- **THEN** the system assembles the Postgres-backed application through
  explicit runtime wiring
- **AND** exposes the VeraBrain tool surface through the MCP server
  entrypoint

#### Scenario: Local MVP startup follows the canonical sequence

- **WHEN** a contributor follows the documented local startup path
- **THEN** Postgres availability is established before application
  assembly
- **AND** schema bootstrap happens before MCP server startup
- **AND** the host process starts the MCP server only after the
  Postgres-backed application is ready

### Requirement: Define the minimum local persistence environment

The project MUST define the minimum local Postgres environment required
to run the MVP, including the expectation that `pgvector` is available.

The canonical MVP path MUST provision that Postgres environment through
Docker Compose.

The MVP path MUST NOT depend on implicit machine-local database state.

The minimum Docker Compose environment MUST define:

- a dedicated Postgres service owned by the VeraBrain project
- an explicit database name, username, password, and host port for the
  host-launched VeraBrain process
- persistent storage scoped to the VeraBrain Postgres service
- a readiness check or equivalent startup signal
- an image or initialization path that makes `pgvector` available to the
  VeraBrain schema bootstrap path

The Compose environment MAY stay narrowly focused on the database for
the initial MVP and does not need to containerize the VeraBrain process
itself.

#### Scenario: Contributor provisions local persistence for the MVP

- **WHEN** a contributor prepares the local VeraBrain MVP environment
- **THEN** the contributor uses the project-local Docker Compose path to
  provision Postgres with `pgvector`
- **AND** the MVP path does not assume hidden database setup

#### Scenario: Host-launched VeraBrain connects to the Compose database

- **WHEN** a contributor starts the local MVP with host-launched MCP
- **THEN** the VeraBrain host process connects to an explicit Postgres
  host/port exposed by the project-local Compose environment
- **AND** the Compose stack remains the source of truth for the local
  durable database

### Requirement: Define the minimum Hermes-facing MCP path

The project MUST define the minimum Hermes-facing MCP configuration
needed to exercise the MVP locally.

The initial MVP path MUST focus on MCP-first integration, MUST launch
the VeraBrain MCP server from the host over `stdio`, and MUST NOT
depend on a native Hermes plugin or Hermes skill to become runnable.

#### Scenario: Contributor points Hermes at the local VeraBrain MVP

- **WHEN** a contributor configures Hermes to use the local VeraBrain
  MCP server
- **THEN** the configuration path is explicit and uses a host-launched
  `stdio` server process
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
