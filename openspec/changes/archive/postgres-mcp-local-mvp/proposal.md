# Postgres MCP Local MVP

## Why

The repository already has:

- archived architecture and boundary changes for VeraBrain core,
  adapters, and retrieval
- an archived MVP memory loop that is validated through integration
  tests
- a Postgres runtime path and an MCP server composition surface

What is still missing is the first practical path that lets a
contributor run VeraBrain locally as an MVP and test it outside the
test suite.

Without a dedicated change for the local operational MVP path, the
project would remain in an awkward state where:

- the MVP is specified and tested, but not yet easy to try manually
- Postgres-backed execution is present in code, but not yet packaged
  into a clear local run path
- Hermes-facing MCP integration exists as a surface, but not yet as a
  documented and reproducible local workflow

## What Changes

- Define the local MVP run path for VeraBrain over Postgres and MCP
- Define the minimum local infrastructure needed to run the MVP
- Define the assembly path from runtime settings to MCP server startup
- Define the minimum smoke workflow a contributor can use to test the
  system manually
- Define the first Hermes-facing local integration shape for the MVP

The canonical initial path is:

- project-local Postgres provisioned through Docker Compose
- VeraBrain MCP launched from the host over `stdio`

## Non-Goals

- Production deployment hardening
- Cloud hosting or multi-environment deployment strategy
- Native Hermes plugin or hook integration
- Broad knowledge-graph expansion
- Execution workflow or GTD-oriented product behavior

## Impact

- Converts the current baseline from architecture-plus-tests into a
  locally runnable MVP path
- Gives the project a concrete bridge from repository validation to
  hands-on testing
- Reduces ambiguity around how Postgres, MCP, and VeraBrain assembly
  should work together in practice
- Creates the right foundation for later production hardening without
  expanding scope prematurely
