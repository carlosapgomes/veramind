# Postgres Runtime and Operational Wiring

## Why

The repository now has:

- accepted ADRs for Postgres and `pgvector`
- infrastructure repository and unit-of-work adapters for Postgres
- initial schema and migration support
- archived foundation and retrieval changes that define the core
  persistence and retrieval boundaries

What is still missing is the operational path that turns those building
blocks into a usable runtime configuration.

Without a dedicated change for runtime and operational wiring, the next
implementation work could:

- hard-code connection setup into the wrong layer
- mix migration execution into application services
- leave startup behavior ambiguous between local, test, and runtime
  environments
- make Hermes-facing integration depend on implicit database bootstrap
  assumptions

## What Changes

- Define how the Postgres persistence path is configured at runtime
- Define how connections are created and injected into VeraBrain
- Define how migrations are applied or checked operationally
- Define startup and health expectations for the Postgres-backed path
- Define the boundary between infrastructure bootstrap and application
  services

## Non-Goals

- Replacing the existing repository or retrieval contracts
- Choosing a production deployment platform
- Defining backup, replication, or disaster-recovery operations
- Implementing full CLI tooling in this change
- Designing non-Postgres persistence backends

## Impact

- Gives the next operational slices a clear target for runtime wiring
- Keeps database bootstrap concerns out of adapters and application
  services
- Clarifies how Postgres becomes the active persistence path in practice
- Reduces risk of implicit or environment-specific startup behavior
