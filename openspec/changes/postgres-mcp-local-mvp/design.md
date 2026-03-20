# Design: Postgres MCP Local MVP

## Objective

Define the first practical local run path for VeraBrain so a
contributor can start the system, connect it through MCP, and manually
exercise the archived memory-loop MVP behavior.

This change is not about expanding product scope. It is about turning
the current architecture and test baseline into a reproducible local
workflow.

## Canonical Local MVP Flow

The canonical local MVP flow is:

1. provision a local Postgres instance with `pgvector` through Docker
   Compose
2. provide explicit runtime settings to VeraBrain
3. bootstrap or verify the Postgres schema through infrastructure
   runtime wiring
4. assemble the `VeraBrainApplication` over the Postgres-backed
   unit-of-work
5. expose the application through the MCP server surface from the host
   over `stdio`
6. connect Hermes to that MCP server
7. manually exercise `save_memory`, `search_memory`, and
   `get_context_bundle`

The local MVP path must reuse the existing runtime, application, and
adapter boundaries rather than introducing a special-purpose launcher
stack.

## Runtime Assembly

The canonical runtime assembly path is:

- explicit runtime settings
- Postgres connection factory
- schema bootstrap or verification
- Postgres-backed application factory
- MCP application adapter
- MCP server startup

This preserves the existing boundary that operational wiring belongs to
infrastructure bootstrap and not to application services or MCP tool
semantics.

The canonical local startup sequence is:

1. start the project-local Docker Compose Postgres service
2. load explicit runtime settings for the local VeraBrain process
3. create a startup connection with `PostgresConnectionFactory`
4. run `bootstrap_postgres_runtime_schema(...)`
5. build the application through
   `PostgresRuntimeApplicationFactory.create_application(...)`
6. expose the application through the MCP server entrypoint on the host
7. let Hermes launch or connect to that host process over `stdio`

This ordering is intentional:

- infrastructure readiness is checked before the MCP surface is exposed
- schema handling stays out of MCP tool behavior
- the MCP server never becomes responsible for implicit Postgres setup

## Local Infrastructure Assumptions

The first local MVP should assume:

- a contributor provisions Postgres locally in a reproducible way
  through project-owned Docker Compose configuration
- the required `pgvector` extension is available
- the VeraBrain MCP server starts from the host process environment
- the MVP path should not depend on undocumented machine-local setup

This split is intentional:

- Compose isolates the durable Postgres dependency from the rest of the
  machine
- host-launched `stdio` keeps the initial Hermes MCP integration simple
  and aligned with the current server surface

## Hermes MCP Interaction Path

The local MVP remains MCP-first.

Hermes should:

- keep local session and prompt memory as defined by the archived
  boundary change
- call VeraBrain through the existing host-launched MCP tool surface
- use `save_memory` for explicit durable promotion
- use `search_memory` or `get_context_bundle` for bounded durable recall

The first local MVP must not depend on a Hermes-native plugin or skill
to function.

## Manual Smoke Workflow

The minimum manual smoke workflow should prove:

1. project-local Docker Compose Postgres is available
2. VeraBrain can start from the host over the configured Postgres path
3. the MCP server is reachable through its intended local `stdio`
   runtime path
4. a durable memory can be saved
5. the saved memory can be retrieved in bounded form
6. the observed behavior matches the archived memory-loop MVP outcomes

The smoke workflow should be documented so a contributor can follow it
without reverse engineering the codebase.

## Failure and Fallback Paths

The local MVP should make these failure states observable:

- Postgres unavailable or misconfigured at startup
- schema state missing or invalid
- MCP dependency unavailable
- memory save succeeds without embedding
- memory save fails because durable persistence failed

The change should prefer explicit startup and smoke-path failures over
silent fallback into an unintended local mode.

For the startup flow specifically:

- Postgres startup failure should stop the local MVP before MCP startup
- schema verification failure should stop the local MVP before MCP
  startup
- MCP dependency failure should stop the local MVP after application
  assembly is attempted, not silently downgrade to a non-MCP mode

## Out of Scope

This change does not cover:

- production deployment hardening
- non-local runtime environments
- native Hermes plugin integration
- advanced knowledge modeling
- execution workflows or GTD-oriented behavior
