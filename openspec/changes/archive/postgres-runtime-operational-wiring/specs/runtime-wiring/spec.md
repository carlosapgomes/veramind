# Spec: Postgres Runtime and Operational Wiring

## Status

Proposed

## Requirements

### Requirement: Keep runtime wiring outside the application layer

The active Postgres persistence path MUST be wired through
infrastructure bootstrap components rather than through VeraBrain
application services or Hermes-facing adapters.

The application layer MUST continue to receive already-constructed ports
and services, not connection strings, driver handles, or migration
commands.

#### Scenario: Runtime starts the Postgres-backed VeraBrain path

- **WHEN** the runtime bootstraps VeraBrain with Postgres
- **THEN** infrastructure bootstrap constructs the required persistence
  dependencies
- **AND** application services remain unaware of runtime configuration

### Requirement: Define an explicit runtime settings surface

The Postgres-backed runtime path MUST define an explicit operational
settings surface for connection and bootstrap behavior.

The initial settings surface MUST be able to express at least:

- the Postgres DSN or equivalent connection settings
- whether startup should apply migrations, only verify them, or skip
  migration handling
- whether the runtime should fail fast when Postgres is unavailable

The exact environment-variable names or settings object shape are
implementation-defined, but the runtime configuration boundary MUST be
explicit.

#### Scenario: Contributor configures the Postgres runtime path

- **WHEN** a contributor enables Postgres-backed runtime wiring
- **THEN** the required startup inputs are provided through explicit
  runtime settings
- **AND** those settings are not spread implicitly across unrelated
  modules

### Requirement: Separate connection creation from repository usage

The runtime wiring MUST distinguish:

- connection creation
- migration/bootstrap handling
- repository and unit-of-work construction
- application assembly

These responsibilities MUST remain separate so local tests, operational
startup, and future Hermes integration can reuse the same assembly logic
without duplicating connection policy.

#### Scenario: Runtime constructs the active persistence path

- **WHEN** the system assembles the Postgres-backed unit of work
- **THEN** connection creation is handled separately from repository
  behavior
- **AND** application assembly consumes the already-constructed
  persistence boundary

### Requirement: Define explicit migration startup behavior

The Postgres runtime path MUST define explicit startup behavior for
schema state.

The initial operational modes MUST allow the runtime to:

- apply known migrations
- verify that migrations have already been applied
- skip migration handling intentionally

The chosen mode MUST be explicit in runtime configuration rather than
implied by environment or import side effects.

#### Scenario: Runtime starts with migration handling enabled

- **WHEN** the runtime starts in a mode that manages migrations
- **THEN** migration behavior follows the configured operational mode
- **AND** schema handling does not occur implicitly during unrelated
  imports or repository calls

### Requirement: Define failure behavior for unavailable persistence

The runtime wiring MUST define what happens when Postgres is
unavailable, misconfigured, or not ready.

The initial design MUST support fail-fast behavior for strict runtime
paths and MUST leave room for softer startup handling in future
environments, but the failure policy MUST be explicit.

#### Scenario: Postgres cannot be reached at startup

- **WHEN** the runtime cannot create the configured Postgres connection
- **THEN** the runtime follows the configured failure policy
- **AND** the resulting behavior is observable instead of silently
  degrading into an implicit fallback

### Requirement: Keep operational checks separate from business behavior

Health checks, startup diagnostics, and migration checks MUST remain
operational concerns.

They MUST NOT be implemented as business-service behavior or as MCP tool
semantics.

#### Scenario: Operator checks database readiness

- **WHEN** the system needs to validate Postgres readiness or schema
  state
- **THEN** that behavior runs through operational wiring components
- **AND** it does not alter the meaning of VeraBrain domain services
